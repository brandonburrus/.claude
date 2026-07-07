#!/usr/bin/env python3
"""Claude Code hook: push the main loop to verify code it changes, not just write it.

Three behaviors, dispatched by event:

PostToolUse (Edit|Write|NotebookEdit): if the touched file is source code,
record it as a pending (unverified) change. If a fast linter the project has
opted into is on PATH (ruff for Python, biome for JS/TS), run it on just that
file and surface any findings as advisory context. Inform only; never blocks.

PostToolUse (Bash): if the command is a test/build/typecheck/lint runner AND it
succeeded, treat the pending changes as verified and clear them. Trivia
invocations (--version, --help, --collect-only, install/init) and commands that
mask failure with `|| true` / `; true` never count. A Bash command can also ADD
pending files: shell redirection, `sed -i`, or `tee` targeting a code-extension
path is a code write too (false-negative-leaning: unknowable targets, e.g. the
files inside a `git apply` patch, are simply not tracked).

Stop / SubagentStop: if code was changed and no verification command has run
since, block the stop with a reason naming the unverified files. This is the
forcing function: neither the main loop nor a subagent can silently end a turn
on code it never checked (a subagent's edits accrue under its own transcript
key, so SubagentStop gates exactly its own work). Honors stop_hook_active so it
blocks at most once and never wedges the session.

Scope, stated honestly: the gate enforces that verification RAN AND EXITED 0,
not that it proved the right thing. A green-but-wrong suite is the
completion-verifier agent's job and the CLAUDE.md done-gate's job, not this
hook's.

gate-done-declarations.py (PreToolUse Bash) reads this hook's state files to
deny `git commit` / `gh pr create` while changes are pending. The coupling is
the on-disk format only: JSON {"pending": [paths]} at
~/.cache/claude-verify/<session_id>-<transcript_basename> (non [A-Za-z0-9._-]
chars replaced with "_"). Change state_path() or the schema and that hook must
change in lockstep.

Convenience-grade: fails open (any internal error exits 0) so a broken hook
never wedges editing or traps a turn.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time

STATE_DIR = os.path.expanduser("~/.cache/claude-verify")
STATE_MAX_AGE_SECONDS = 7 * 24 * 3600
LINT_TIMEOUT_SECONDS = 8
MAX_PENDING_TRACKED = 200
MAX_PENDING_LISTED = 20
MAX_LINT_OUTPUT_CHARS = 1500

# Source code the project is expected to be able to test. Markdown, config
# (json/yaml/toml), shell, and SQL are deliberately excluded: they are rarely
# unit-tested, and gating on them would train the operator to route around the
# Stop hook, which is the one failure mode that destroys an enforcement hook.
CODE_EXTENSIONS = {
    ".py", ".pyi",
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".vue", ".svelte", ".astro",
    ".go", ".rs", ".java", ".kt", ".scala",
    ".rb", ".php", ".swift", ".dart",
    ".ex", ".exs",
    ".c", ".h", ".cc", ".cpp", ".hpp", ".cxx",
    ".cs",
}

# A verification command run at a statement boundary clears the pending changes.
# Breadth is deliberate: a false "verified" (a stop allowed that maybe should
# not have been) is cheap, while a false "unverified" (blocking a turn where
# checks did run) is the annoying case that erodes trust in the gate. The
# boundary anchor keeps the token out of quoted text like a commit message.
# A newline counts as a boundary too: verification commands routinely sit on
# their own line in a multi-line Bash script, and without this the gate misses
# them and falsely reports the turn as unverified.
_BOUNDARY = r"(?:^|[;&|(\n\r]|&&|\|\|)\s*"
_VERIFY_TOKENS = [
    r"pytest",
    r"tox\b",
    r"nox\b",
    # `run <script>` counts only when the script is named like a check
    # (test/lint/typecheck/check/build/e2e/ci, anywhere in the name); a bare
    # `npm run dev` or `npm run deploy` is not verification.
    r"(?:npm|pnpm|yarn|bun)\s+(?:run\s+[\w:./-]*(?:test|lint|typecheck|check|build|e2e|ci)[\w:./-]*|test|build|ci|check|typecheck|lint)",
    r"npx\s+(?:vitest|jest|tsc|playwright|eslint|biome)",
    r"vitest\b",
    r"jest\b",
    r"mocha\b",
    r"playwright\b",
    r"cypress\b",
    r"tsc\b",
    r"biome\b",
    r"eslint\b",
    r"ruff\b",
    r"mypy\b",
    r"pyright\b",
    r"pylint\b",
    r"flake8\b",
    r"cargo\s+(?:test|build|check|clippy)",
    r"go\s+(?:test|build|vet)",
    r"make\b",
    r"(?:\./)?(?:gradlew|mvnw|gradle|mvn)\s+(?:test|build|verify|check|package)",
    r"dotnet\s+(?:test|build)",
    r"rspec\b",
    r"phpunit\b",
    r"pest\b",
    r"rake\s+(?:test|spec)",
    r"bru\s+run",
    r"swift\s+(?:test|build)",
    r"python[0-9.]*\s+-m\s+(?:pytest|unittest|py_compile|mypy)",
]
_VERIFY_RE = re.compile(_BOUNDARY + r"(?:" + r"|".join(_VERIFY_TOKENS) + r")")

# Trivia invocations of a verify-shaped tool run no checks: version/help
# banners, pytest --collect-only, and install/init setup commands (`make
# install` matches the `make` token above). Conservative direction: a false
# trivia hit only delays a clear until a real check runs.
_TRIVIA_RE = re.compile(r"--(?:version|help|collect-only|init)\b|\b(?:install|init)\b")
# `cmd || true` / `cmd; true` masks the exit status, so success is unknowable;
# such a command never clears. `&& true` is harmless and not matched.
_MASKED_RE = re.compile(r"(?:\|\||;)\s*true\b")

# Bash-mediated code writes to track as pending. Deliberately false-negative-
# leaning: only targets literally visible in the command text are caught.
# Redirection targets are extracted directly; for in-place editors (sed -i,
# tee, git apply, patch) every code-extension token in the command is treated
# as a potential target (the files inside a patch body are unknowable and
# simply not tracked).
_REDIRECT_TARGET_RE = re.compile(r"(?<![<>])>{1,2}\s*([^\s;|&<>()]+)")
_INPLACE_WRITE_RE = re.compile(
    _BOUNDARY + r"(?:sed\s+[^;|&\n]*-i|tee\b|git\s+apply\b|patch\b)"
)
_TOKEN_RE = re.compile(r"[^\s;|&<>()'\"]+")


def extract_bash_write_targets(command):
    """Code-extension paths a Bash command visibly writes to."""
    candidates = set()
    for m in _REDIRECT_TARGET_RE.finditer(command):
        candidates.add(m.group(1))
    if _INPLACE_WRITE_RE.search(command):
        candidates.update(_TOKEN_RE.findall(command))
    targets = []
    for c in candidates:
        c = c.strip("'\"")
        if os.path.splitext(c)[1].lower() in CODE_EXTENSIONS:
            targets.append(c)
    return targets


def bash_succeeded(event):
    """Whether the Bash command exited 0, judged from the PostToolUse envelope.

    The harness gives PostToolUse no exit-code field for Bash: a successful
    command's tool_response is a dict ({stdout, stderr, interrupted, ...}), and
    per the hook-events digest PostToolUse fires "after tool succeeds" (failures
    route to PostToolUseFailure). Empirically a nonzero-exit command surfaces as
    a raw string tool_response starting "Error: Exit code N". So: string
    starting with "Error" = failure; dict = success unless interrupted or a
    future exit-code field says otherwise; missing/unknown shape = conservative
    failure (an unwarranted clear is the case that silently voids the gate).
    """
    resp = event.get("tool_response")
    if isinstance(resp, str):
        return not resp.lstrip().lower().startswith("error")
    if isinstance(resp, dict):
        if resp.get("interrupted"):
            return False
        for key in ("exit_code", "exitCode", "returncode", "code"):
            value = resp.get(key)
            if isinstance(value, int) and value != 0:
                return False
        return True
    return False


def state_path(event):
    # Keyed by session_id plus transcript basename, matching inject-agents-md.py:
    # subagents share the session_id but run their own transcript, so this keeps
    # a subagent's pending changes out of the main loop's Stop gate (SubagentStop
    # gates them under their own key).
    # COUPLING: gate-done-declarations.py computes this exact key and reads the
    # same {"pending": [...]} JSON; keep the two in lockstep.
    session = event.get("session_id") or "unknown"
    transcript = os.path.basename(event.get("transcript_path") or "")
    key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{session}-{transcript}")
    return os.path.join(STATE_DIR, key)


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("pending"), list):
            return data
    except (OSError, ValueError):
        pass
    return {"pending": []}


def save_state(path, state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)


def cleanup_stale_state():
    try:
        cutoff = time.time() - STATE_MAX_AGE_SECONDS
        for name in os.listdir(STATE_DIR):
            path = os.path.join(STATE_DIR, name)
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
    except OSError:
        pass


def find_up(start_dir, names):
    """Nearest ancestor file matching one of `names`, or None."""
    directory = os.path.realpath(start_dir)
    while True:
        for name in names:
            candidate = os.path.join(directory, name)
            if os.path.isfile(candidate):
                return candidate
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent


def project_opts_into(file_dir, ext):
    """Whether the project has opted into a fast linter for this file type, so
    the inform path never imposes a linter the project did not configure."""
    if ext in (".py", ".pyi"):
        if not shutil.which("ruff"):
            return None
        if find_up(file_dir, ["ruff.toml", ".ruff.toml"]):
            return ["ruff", "check"]
        pyproject = find_up(file_dir, ["pyproject.toml"])
        if pyproject:
            try:
                with open(pyproject, encoding="utf-8", errors="replace") as f:
                    if "tool.ruff" in f.read():
                        return ["ruff", "check"]
            except OSError:
                return None
        return None
    if ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
        if not find_up(file_dir, ["biome.json", "biome.jsonc"]):
            return None
        # biome is normally a local devDependency, so a PATH lookup alone
        # misses most real installs; prefer the project's node_modules/.bin
        # binary (also correct when the global version differs), fall back to
        # PATH. No `npx` fallback: `npx --no-install biome` on a project
        # without the package exits nonzero with npx's own error text, which
        # the advisory path would misreport as lint findings.
        local = find_up(file_dir, [os.path.join("node_modules", ".bin", "biome")])
        if local:
            return [local, "check"]
        if shutil.which("biome"):
            return ["biome", "check"]
        return None
    return None


def lint_file(real_path):
    ext = os.path.splitext(real_path)[1].lower()
    base_cmd = project_opts_into(os.path.dirname(real_path), ext)
    if not base_cmd:
        return None
    try:
        proc = subprocess.run(
            base_cmd + [real_path],
            capture_output=True,
            text=True,
            timeout=LINT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode == 0:
        return None
    return ((proc.stdout or "") + (proc.stderr or "")).strip() or None


def display_path(real_path, cwd):
    if cwd:
        try:
            return os.path.relpath(real_path, os.path.realpath(cwd))
        except ValueError:
            return real_path
    return real_path


def handle_edit(event):
    tool_input = event.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not file_path:
        return
    if os.path.splitext(file_path)[1].lower() not in CODE_EXTENSIONS:
        return
    real = os.path.realpath(file_path)
    # Scratch files under temp dirs are throwaway tooling, not deliverables;
    # tracking them makes unrelated repos' commits hit the done-gate.
    temp_roots = ("/tmp/", "/private/tmp/", "/var/folders/")
    tmpdir = os.environ.get("TMPDIR")
    if real.startswith(temp_roots) or (tmpdir and real.startswith(os.path.realpath(tmpdir))):
        return
    display = display_path(real, event.get("cwd"))

    spath = state_path(event)
    state = load_state(spath)
    if display not in state["pending"]:
        state["pending"].append(display)
        state["pending"] = state["pending"][-MAX_PENDING_TRACKED:]
        save_state(spath, state)

    findings = lint_file(real)
    if not findings:
        return
    if len(findings) > MAX_LINT_OUTPUT_CHARS:
        findings = findings[:MAX_LINT_OUTPUT_CHARS] + "\n...(truncated)"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"Linter findings on {display} (advisory, not blocking):\n"
                f"{findings}\n"
                "Resolve these before treating the change as done."
            ),
        }
    }))


def handle_bash(event):
    command = (event.get("tool_input") or {}).get("command") or ""

    # Bash-mediated code writes join the pending set like Edit/Write would.
    targets = extract_bash_write_targets(command)
    if targets:
        cwd = event.get("cwd") or ""
        spath = state_path(event)
        state = load_state(spath)
        for target in targets:
            real = os.path.realpath(
                target if os.path.isabs(target) else os.path.join(cwd, target)
            )
            display = display_path(real, cwd)
            if display not in state["pending"]:
                state["pending"].append(display)
        state["pending"] = state["pending"][-MAX_PENDING_TRACKED:]
        save_state(spath, state)

    # Clears require outcome, not attempt: a verify-shaped command that is
    # trivia, masks its exit status, or did not exit 0 leaves pending intact.
    if not _VERIFY_RE.search(command):
        return
    if _TRIVIA_RE.search(command) or _MASKED_RE.search(command):
        return
    if not bash_succeeded(event):
        return
    spath = state_path(event)
    state = load_state(spath)
    if state["pending"]:
        state["pending"] = []
        save_state(spath, state)


def prune_resolved(pending, cwd):
    """Keep only files that still differ from git HEAD in the working tree.

    A pending file that is clean in git was committed or reverted since it was
    edited, so there is no unverified working-tree change left to gate. Pruning
    these also stops the gate re-nagging on later no-op turns after the work was
    committed (the failure the user hit). Untracked-but-present new files show up
    in `git status --porcelain` and so correctly stay pending. Fails safe: if git
    status cannot be determined (not a repo, git missing, timeout), every file is
    kept, preserving the pre-existing behavior in non-git projects.
    """
    if not cwd:
        return pending
    realcwd = os.path.realpath(cwd)
    try:
        top = subprocess.run(
            ["git", "-C", realcwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3,
        )
        if top.returncode != 0:
            return pending
        repo_root = top.stdout.strip()
        status = subprocess.run(
            ["git", "-C", realcwd, "status", "--porcelain"],
            capture_output=True, text=True, timeout=3,
        )
        if status.returncode != 0:
            return pending
    except (OSError, subprocess.TimeoutExpired):
        return pending
    dirty = set()
    for line in status.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:  # rename: the destination is the live file
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        dirty.add(os.path.normpath(os.path.join(repo_root, path)))
    kept = []
    for f in pending:
        absf = os.path.normpath(f if os.path.isabs(f) else os.path.join(realcwd, f))
        if absf in dirty:
            kept.append(f)
    return kept


def handle_stop(event):
    # stop_hook_active is set once a Stop hook has already blocked this turn;
    # returning here caps the gate at one block so it nudges without wedging.
    if event.get("stop_hook_active"):
        return
    cleanup_stale_state()
    spath = state_path(event)
    state = load_state(spath)
    pending = state.get("pending") or []
    if not pending:
        return
    resolved = prune_resolved(pending, event.get("cwd"))
    if resolved != pending:
        state["pending"] = resolved
        save_state(spath, state)
        pending = resolved
    if not pending:
        return
    listed = pending[:MAX_PENDING_LISTED]
    more = len(pending) - len(listed)
    files = ", ".join(listed) + (f" (+{more} more)" if more > 0 else "")
    reason = (
        "You changed code this turn but ran no verification command since "
        f"(tests, build, typecheck, or lint). Unverified: {files}. Run the "
        "project's checks, or delegate to the completion-verifier agent or the "
        "verify skill, and address what they report before ending the turn. If "
        "you are intentionally leaving work unverified (work in progress, no "
        "test harness exists, or the user asked you to stop), say so explicitly "
        "and state what remains; do not present unverified changes as complete."
    )
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    event = json.load(sys.stdin)
    name = event.get("hook_event_name")
    if name == "PostToolUse":
        if event.get("tool_name") == "Bash":
            handle_bash(event)
        else:
            handle_edit(event)
    elif name in ("Stop", "SubagentStop"):
        # SubagentStop carries the subagent's own transcript_path, so
        # state_path() resolves to the subagent's pending set; stop_hook_active
        # is read with .get so its absence on either event is harmless.
        handle_stop(event)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)

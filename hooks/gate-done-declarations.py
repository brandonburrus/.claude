#!/usr/bin/env python3
"""PreToolUse(Bash) hook: gate "done" declarations behind verification.

Two guards, both scoped to the current session+transcript:

1. Deny `git commit` (including the `gc` alias) and `gh pr create` while
   enforce-verification.py's pending set is non-empty: committing or opening a
   PR is a done-declaration, and unverified code changes mean it is premature.
   The deny reason names the pending files so the fix is obvious: run the
   project's checks first.

2. Deny sweep-staging: `git add -A`, `git add --all`, `git add -a`, and bare
   `git add .`. This encodes a recorded user lesson (memory:
   stage-specific-paths-not-git-add-all): sweeping the whole tree drags the
   user's unrelated working-tree changes into the agent's commit. Always
   denied, pending or not; stage specific paths instead.

COUPLING: the pending set is read from enforce-verification.py's state files,
import-free (importing a sibling hook would create __pycache__ in this repo).
The shared contract is the on-disk format only: JSON {"pending": [paths]} at
~/.cache/claude-verify/<session_id>-<transcript_basename> with every character
outside [A-Za-z0-9._-] replaced by "_". Change that hook's state_path() or
schema and this reader must change in lockstep.

Convenience-grade, fails open: any internal error exits 0 (allow), consistent
with the sibling guards; a broken gate must never wedge the Bash tool.
"""

import json
import os
import re
import sys

STATE_DIR = os.path.expanduser("~/.cache/claude-verify")
MAX_PENDING_LISTED = 20

_BOUNDARY = r"(?:^|[;&|(\n\r]|&&|\|\|)\s*"
# `git commit` (allowing global flags like `-C dir` or `-c k=v` between git and
# the subcommand), the `gc` shell alias, and `gh pr create`.
_COMMIT_RE = re.compile(
    _BOUNDARY + r"(?:(?:command\s+)?git\s+(?:-\S+\s+)*commit\b|gc\b|gh\s+pr\s+create\b)"
)
# git add with a sweep flag anywhere in its arguments, or a bare `git add .`
# ending the statement. `git add ./src` or `git add dir/.` is fine.
_ADD_SWEEP_RE = re.compile(
    _BOUNDARY
    + r"(?:command\s+)?git\s+(?:-\S+\s+)*add\s+(?:[^\s;|&]+\s+)*(?:-A|--all|-a)\b"
    + r"|" + _BOUNDARY + r"(?:command\s+)?git\s+(?:-\S+\s+)*add\s+\.\s*(?:$|[;&|)])"
)


def pending_files(event):
    """Read enforce-verification.py's pending set for this session+transcript."""
    session = event.get("session_id") or "unknown"
    transcript = os.path.basename(event.get("transcript_path") or "")
    key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{session}-{transcript}")
    try:
        with open(os.path.join(STATE_DIR, key), encoding="utf-8") as f:
            data = json.load(f)
        pending = data.get("pending") if isinstance(data, dict) else None
        return pending if isinstance(pending, list) else []
    except (OSError, ValueError):
        return []


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main():
    event = json.load(sys.stdin)
    command = (event.get("tool_input") or {}).get("command") or ""
    if not command:
        return

    if _ADD_SWEEP_RE.search(command):
        deny(
            "BLOCKED: stage specific paths, not the whole tree. `git add -A` / "
            "`--all` / `-a` / bare `git add .` sweeps the user's unrelated "
            "working-tree changes into your commit. List the files you actually "
            "changed: `git add <path> <path>`."
        )
        return

    if _COMMIT_RE.search(command):
        pending = pending_files(event)
        if pending:
            listed = pending[:MAX_PENDING_LISTED]
            more = len(pending) - len(listed)
            files = ", ".join(listed) + (f" (+{more} more)" if more > 0 else "")
            deny(
                "BLOCKED: you are committing (or opening a PR on) code changes "
                f"that have not been verified this turn: {files}. Run the "
                "project's checks first (tests, build, typecheck, or lint); a "
                "passing run clears this gate. Do not declare work done "
                "unverified."
            )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # fail open, like the sibling guards

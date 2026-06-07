#!/usr/bin/env python3
"""Claude Code hook: auto-inject AGENTS.md files into context.

SessionStart (startup/clear): injects the project root AGENTS.md via stdout.
SessionStart (compact): clears this session's seen-state so every AGENTS.md
re-injects lazily after compaction may have summarized it away.
PostToolUse (Read|Edit|Write|NotebookEdit): walks from the touched file's
directory up to the project root and injects any AGENTS.md not yet seen this
session via hookSpecificOutput.additionalContext.

Convenience hook: fails open (exit 0) on any internal error so a broken hook
never wedges the session. Stdlib only; this runs on every file-tool call and
must not pay dependency-resolution latency.
"""

import json
import os
import re
import sys
import time

STATE_DIR = os.path.expanduser("~/.cache/claude-agents-md")
# Files over this many bytes inject as a read-this pointer instead of inline
# content, so one pathological AGENTS.md cannot flood the context window.
INLINE_CAP_BYTES = 10 * 1024
# Stale state files are deleted opportunistically at session start; a week is
# comfortably past any session's lifetime.
STATE_MAX_AGE_SECONDS = 7 * 24 * 3600


def state_path(event):
    # Key on session_id plus transcript basename: subagents share the
    # session_id but run their own transcript, and the context a hook injects
    # only reaches the agent whose tool call fired it. Without the transcript
    # component, a subagent reading a file would mark its AGENTS.md seen and
    # the main loop would never receive it.
    session = event.get("session_id") or "unknown"
    transcript = os.path.basename(event.get("transcript_path") or "")
    key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{session}-{transcript}")
    return os.path.join(STATE_DIR, key)


def load_seen(path):
    """Seen-state: one `path<TAB>mtime` line per injected AGENTS.md."""
    seen = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                agents_path, _, mtime = line.rstrip("\n").partition("\t")
                if agents_path:
                    seen[agents_path] = float(mtime or 0)
    except (OSError, ValueError):
        return {}
    return seen


def save_seen(path, seen):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for agents_path, mtime in seen.items():
            f.write(f"{agents_path}\t{mtime}\n")


def render(agents_path):
    size = os.path.getsize(agents_path)
    if size > INLINE_CAP_BYTES:
        return (
            f"AGENTS.md at {agents_path} is {size} bytes, over the inline "
            "injection cap; read it before working in this directory."
        )
    with open(agents_path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    return f"Project context from {agents_path}:\n\n{content}"


def collect_unseen(cwd, file_path, seen):
    """AGENTS.md files on the path from cwd down to file_path's directory,
    absent from `seen` or modified since last injection, root to leaf."""
    cwd = os.path.realpath(cwd)
    directory = os.path.realpath(os.path.dirname(file_path))
    if directory != cwd and not directory.startswith(cwd + os.sep):
        return []
    candidates = []
    while True:
        agents = os.path.join(directory, "AGENTS.md")
        if os.path.isfile(agents):
            candidates.append(agents)
        if directory == cwd:
            break
        directory = os.path.dirname(directory)
    candidates.reverse()  # parent context lands before child context
    # An mtime newer than the recorded one means the file changed since it
    # was injected; re-inject rather than let the session work off stale rules.
    return [p for p in candidates if os.path.getmtime(p) > seen.get(p, 0)]


def cleanup_stale_state():
    try:
        cutoff = time.time() - STATE_MAX_AGE_SECONDS
        for name in os.listdir(STATE_DIR):
            path = os.path.join(STATE_DIR, name)
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
    except OSError:
        pass


def handle_session_start(event):
    cleanup_stale_state()
    source = event.get("source")
    spath = state_path(event)
    if source == "compact":
        try:
            os.remove(spath)
        except OSError:
            pass
        return
    if source not in ("startup", "clear"):
        return  # resume keeps both its context and its seen-state
    cwd = event.get("cwd")
    if not cwd:
        return
    root_agents = os.path.realpath(os.path.join(cwd, "AGENTS.md"))
    if not os.path.isfile(root_agents):
        return
    # On SessionStart, plain stdout is added to Claude's context directly.
    print(render(root_agents))
    seen = load_seen(spath)
    seen[root_agents] = os.path.getmtime(root_agents)
    save_seen(spath, seen)


def handle_post_tool(event):
    tool_input = event.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    cwd = event.get("cwd")
    if not file_path or not cwd:
        return
    file_path = os.path.realpath(file_path)
    spath = state_path(event)
    seen = load_seen(spath)
    unseen = collect_unseen(cwd, file_path, seen)
    if not unseen:
        return
    blocks = []
    for agents in unseen:
        seen[agents] = os.path.getmtime(agents)
        # The touched file IS this AGENTS.md: Claude just read or wrote its
        # content, so injecting it back would duplicate context. Mark seen only.
        if agents == file_path:
            continue
        blocks.append(render(agents))
    save_seen(spath, seen)
    if not blocks:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "\n\n".join(blocks),
        }
    }))


def main():
    event = json.load(sys.stdin)
    name = event.get("hook_event_name")
    if name == "SessionStart":
        handle_session_start(event)
    elif name == "PostToolUse":
        handle_post_tool(event)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)

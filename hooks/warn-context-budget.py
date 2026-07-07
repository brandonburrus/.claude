#!/usr/bin/env python3
"""PostToolUse context-budget warning hook.

Auto-compact is disabled in this repo's settings.json (autoCompactEnabled: false),
so a long session can hit the context wall with no soft landing. The statusline
shows a Context: N% meter, but a passive meter is not a deterministic nudge.

Constraint that shapes the whole design: hooks do NOT receive context_window data
in their stdin (only session_id, cwd, hook_event_name, and per-event tool fields).
The statusline is the only component the harness feeds context_window to. So the
statusline publishes {remaining_percentage, timestamp} to
~/.cache/claude-context/<session_id>.json (see ../statusline.sh), and this hook
reads that bridge after each context-growing tool use. When the remaining context
crosses a threshold it injects an advisory additionalContext nudge so the agent
wraps up and offers a handoff before context runs out.

Warns once per threshold per session: with auto-compact off, context only shrinks
within a session, so each level fires at most once and never spams.

Subagent handling: subagents SHARE the main loop's session_id but run their own
transcript (main loop: <session_id>.jsonl; subagents: .../subagents/agent-*.jsonl).
Only the main loop has a statusline, so the bridge file describes the main loop's
window, not a subagent's; a subagent tool call must therefore never consume the
warning. Two guards: transcripts whose basename is not <session_id>.jsonl skip
warning entirely, and the dedup sentinel is keyed by session+transcript (like
inject-agents-md.py) so no other transcript can mute the main loop's one shot.
The bridge file itself stays keyed by session_id alone: statusline.sh writes it
and only receives session_id.

Convenience-grade: fails OPEN (exit 0 on any error) so a parser bug or a missing
bridge never wedges tool execution.

Test battery: pipe hand-built PostToolUse event JSON through it with a planted
bridge file and assert the additionalContext payload, the once-per-threshold dedup,
the stale-file skip, and exit 0.
"""
import json
import os
import re
import sys
import time

# Thresholds are in PERCENT OF THE WINDOW REMAINING (not used).
WARN_REMAINING = 25      # first, softer nudge when <= 25% remains
CRITICAL_REMAINING = 15  # stronger nudge when <= 15% remains
# Ignore a bridge file older than this. Within a session context only shrinks, so a
# stale read under-reports usage (it can only delay a warning, never raise a false
# critical); the guard exists to drop a leftover file from a long-dead session.
STALE_SECONDS = 600
# Bridge/sentinel files from dead sessions accumulate forever otherwise; a week
# is comfortably past any session's lifetime (matches the sibling hooks).
PRUNE_MAX_AGE_SECONDS = 7 * 24 * 3600

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "claude-context")


def prune_stale_files():
    try:
        cutoff = time.time() - PRUNE_MAX_AGE_SECONDS
        for name in os.listdir(CACHE_DIR):
            path = os.path.join(CACHE_DIR, name)
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
    except OSError:
        pass


def emit(message):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message,
        }
    }))


def main():
    data = json.load(sys.stdin)
    session = data.get("session_id") or ""
    # session_id builds a cache path; reject separators/traversal before using it.
    if not session or "/" in session or "\\" in session or ".." in session:
        return

    prune_stale_files()

    # The bridge measures the MAIN LOOP's window (only the main loop has a
    # statusline). A subagent shares the session_id but runs its own transcript
    # (.../subagents/agent-*.jsonl), so any transcript other than the session's
    # own <session_id>.jsonl skips warning entirely. A missing transcript_path
    # cannot be distinguished, so it is treated as the main loop (fail toward
    # warning; a wrong nudge is cheaper than a missed one).
    transcript = os.path.basename(data.get("transcript_path") or "")
    if transcript and transcript != f"{session}.jsonl":
        return

    try:
        with open(os.path.join(CACHE_DIR, f"{session}.json")) as f:
            metrics = json.load(f)
    except (FileNotFoundError, ValueError):
        # No bridge file = fresh session, or the statusline has not run yet.
        return

    ts = metrics.get("timestamp")
    if ts is not None and (time.time() - ts) > STALE_SECONDS:
        return

    remaining = metrics.get("remaining_percentage")
    if remaining is None or remaining > WARN_REMAINING:
        return

    level = "critical" if remaining <= CRITICAL_REMAINING else "warning"

    # Dedup: each level fires at most once per session. Keyed by
    # session+transcript (like the sibling hooks) so a transcript that slips
    # past the main-loop check above can never consume the main loop's shot.
    key = re.sub(r"[^A-Za-z0-9._-]", "_", f"{session}-{transcript}")
    sentinel = os.path.join(CACHE_DIR, f"{key}.warned.json")
    try:
        with open(sentinel) as f:
            fired = json.load(f).get("fired", [])
    except (FileNotFoundError, ValueError):
        fired = []
    if level in fired:
        return
    fired.append(level)
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(sentinel, "w") as f:
            json.dump({"fired": fired}, f)
    except OSError:
        pass

    pct = round(remaining)
    if level == "critical":
        emit(
            f"CONTEXT CRITICAL: about {pct}% of the context window remains and auto-compact "
            "is disabled, so this session can hard-stop without warning. Wrap up now: finish or "
            "checkpoint the current step, and offer the user a handoff document (the create-handoff "
            "skill) before continuing. Do not start new exploration or large work."
        )
    else:
        emit(
            f"CONTEXT WARNING: about {pct}% of the context window remains and auto-compact is "
            "disabled. Avoid starting new large explorations; finish the current thread. If the "
            "remaining work will not fit, tell the user and offer to capture progress with the "
            "create-handoff skill."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Convenience hook: never block tool execution on an internal error.
        pass
    sys.exit(0)

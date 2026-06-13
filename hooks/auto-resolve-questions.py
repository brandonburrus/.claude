#!/usr/bin/env python3
"""PreToolUse(AskUserQuestion) hook: auto-resolve safe, reversible questions.

When the model asks the user a question via AskUserQuestion and the question
(a) carries exactly one option flagged "(recommended)", (b) is single-select,
and (c) mentions nothing that signals an irreversible one-way-door action, this
hook answers it automatically by denying the tool call with a reason naming the
recommended option, so the model proceeds without nagging the user on a cheap,
reversible choice. Anything that fails those gates is let through to the user
untouched. This is the lightweight adaptation of gstack's question-preference
enforcement: no per-question id markers and no door-type registry, just a global
recommended-option-plus-reversibility heuristic.

Mode (env CLAUDE_QUESTION_HOOK_MODE, default "shadow"):
  shadow - never suppress; log what it WOULD have auto-resolved and let every
           question through. The safe default, so the heuristic can be observed
           before it ever changes behavior. Review ~/.cache/claude-question-hook/
           decisions.jsonl, then set the env to "active" in settings.json to arm it.
  active - auto-resolve qualifying calls (deny plus a recommended-option reason).
  off    - do nothing.

Convenience hook: FAILS OPEN. Any parse error, unexpected shape, or internal
exception exits 0 with empty stdout, so the question is shown to the user as
normal. A bug here must never suppress a question or wedge the session.

A whole AskUserQuestion call is auto-resolved only if EVERY question in it
qualifies; one ambiguous or risky question sends the entire call to the user.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

MODE = os.environ.get("CLAUDE_QUESTION_HOOK_MODE", "shadow").strip().lower()

# Decision log lives in the cache dir, never inside this repo (hooks/AGENTS.md).
LOG_DIR = Path.home() / ".cache" / "claude-question-hook"

RECOMMENDED_RE = re.compile(r"\(recommended\)\s*$", re.IGNORECASE)

# One-way-door signals. If any appears in a question's text, header, or option
# labels/descriptions, the question is treated as irreversible and always sent
# to the user. Tuned to over-match on purpose: a false "irreversible" only costs
# one normal prompt, while a false "reversible" could auto-resolve something
# consequential. Edit this list to tune what the active hook will answer.
ONE_WAY_SIGNALS = (
    "delete", "drop ", "remove", "destroy", "wipe", "purge", "truncate",
    "overwrite", "force", "deploy", "release", "publish", "production",
    "prod ", "migrate", "migration", "rollback", "revert", "rotate",
    "revoke", "terminate", "shut down", "shutdown", "uninstall", "format ",
    "charge", "payment", "refund", "bill", "send ", "email", "notify",
    "irreversible", "permanent", "merge", "rebase", "reset", "rm -", "git push",
)


def let_through():
    """Exit 0 with no stdout: the normal permission flow shows the question."""
    sys.exit(0)


def log(record):
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with (LOG_DIR / "decisions.jsonl").open("a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass  # logging must never break the hook


def recommended_label(question):
    """Return the recommended option's label (suffix stripped), or None.

    Qualifies only when exactly one option is flagged "(recommended)"; zero or
    several means no single recommendation was expressed, so defer to the user.
    """
    options = question.get("options")
    if not isinstance(options, list):
        return None
    hits = []
    for opt in options:
        label = opt.get("label", "") if isinstance(opt, dict) else ""
        if isinstance(label, str) and RECOMMENDED_RE.search(label):
            hits.append(RECOMMENDED_RE.sub("", label).strip())
    return hits[0] if len(hits) == 1 else None


def looks_one_way(question):
    """True if the question mentions any irreversible-action signal."""
    haystack = (str(question.get("question", "")) + " " + str(question.get("header", ""))).lower()
    for opt in question.get("options", []):
        if isinstance(opt, dict):
            haystack += " " + str(opt.get("label", "")).lower()
            haystack += " " + str(opt.get("description", "")).lower()
    return any(sig in haystack for sig in ONE_WAY_SIGNALS)


def resolve_one(question):
    """Return the chosen label if this question is safely auto-resolvable, else None."""
    if question.get("multiSelect"):
        return None  # multi-select has no single recommended-option semantics
    if looks_one_way(question):
        return None
    return recommended_label(question)


def main():
    raw = sys.stdin.read()
    if MODE == "off":
        let_through()
    data = json.loads(raw)
    if data.get("tool_name") != "AskUserQuestion":
        let_through()
    questions = data.get("tool_input", {}).get("questions")
    if not isinstance(questions, list) or not questions:
        let_through()

    # The call auto-resolves only if every question independently qualifies.
    choices = []
    for q in questions:
        if not isinstance(q, dict):
            choices = None
            break
        label = resolve_one(q)
        if label is None:
            choices = None
            break
        choices.append((q.get("header") or q.get("question", "question"), label))

    would_resolve = choices is not None
    log({
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "session": data.get("session_id"),
        "mode": MODE,
        "would_resolve": would_resolve,
        "headers": [q.get("header") or q.get("question") for q in questions if isinstance(q, dict)],
        "choices": choices if would_resolve else None,
    })

    if not would_resolve or MODE != "active":
        let_through()

    # Active mode and every question qualified: answer on the user's behalf.
    picks = "; ".join(f'"{header}" -> {label}' for header, label in choices)
    reason = (
        "Auto-resolved by the question-preference hook: these are reversible "
        "choices with a clear recommended option, and the configured preference "
        "is not to be asked about them. Proceed as if the user picked: "
        f"{picks}. Do not re-ask this via AskUserQuestion."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        let_through()  # fail open

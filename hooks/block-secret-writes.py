#!/usr/bin/env python3
"""Claude Code hook: block writing a recognizable secret to disk or a command.

PreToolUse (Write|Edit|NotebookEdit|Bash): scans the content about to be written
(or the shell command about to run) for high-confidence credential patterns and
denies the call when one is found. The deny reason names the credential, the
rule, and the compliant alternative (env var or secrets manager); for a key that
looks live, it says rotate, not just relocate, because a secret that reached a
remote is already published.

Only high-precision, prefixed token shapes are matched (provider key prefixes,
AWS key ids, private-key headers). Generic entropy detection is deliberately
omitted: its false-positive rate would train the operator to wave the hook away,
which defeats a guard whose whole value is being trusted when it fires.

Fail-open on unparseable input (exit 0). This is a deliberate deviation from the
fail-closed default for security hooks: the threat model is accidental leakage by
the sole operator, not an adversary crafting malformed envelopes to slip a secret
past the scanner, so wedging every write on a parser bug is the worse failure.
A successfully parsed payload containing a secret is always denied.
"""

import json
import re
import sys

# (label, compiled pattern, live): the `live` flag marks shapes that denote a real,
# usable credential (so the deny reason adds the rotate-don't-relocate note).
_SPECS = [
    ("AWS access key id", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", True),
    ("GitHub token", r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b", True),
    ("GitHub fine-grained PAT", r"\bgithub_pat_[A-Za-z0-9_]{22,}\b", True),
    ("OpenAI/Anthropic-style API key", r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}\b", True),
    ("Slack token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", True),
    ("Google API key", r"\bAIza[0-9A-Za-z_-]{35}\b", True),
    ("Stripe live key", r"\b[sr]k_live_[A-Za-z0-9]{16,}\b", True),
    ("private key block", r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----", True),
]
_PATTERNS = [(label, re.compile(rx), live) for label, rx, live in _SPECS]

# A match is treated as a placeholder (not a real secret) when it carries one of
# these tells. Covers AWS's own documented example key (AKIAIOSFODNN7EXAMPLE),
# docs, and obvious fill-ins, so .env.example templates do not trip the guard.
_PLACEHOLDER = re.compile(
    r"example|sample|placeholder|redacted|dummy|your[_-]?(?:key|token|secret)|xxxx|\.\.\.|<[^>]+>|\*\*\*",
    re.IGNORECASE,
)


def candidate_text(event):
    """The text this tool call would commit: file content, edit replacement, or
    the shell command itself."""
    name = event.get("tool_name")
    ti = event.get("tool_input") or {}
    if name == "Write":
        return ti.get("content") or ""
    if name == "Edit":
        return ti.get("new_string") or ""
    if name == "NotebookEdit":
        return ti.get("new_source") or ""
    if name == "Bash":
        return ti.get("command") or ""
    return ""


def find_secret(text):
    for label, pattern, live in _PATTERNS:
        match = pattern.search(text)
        if match and not _PLACEHOLDER.search(match.group(0)):
            return label, match.group(0), live
    return None


def main():
    event = json.load(sys.stdin)
    if event.get("hook_event_name") != "PreToolUse":
        return
    text = candidate_text(event)
    if not text:
        return
    hit = find_secret(text)
    if not hit:
        return
    label, _, live = hit
    rotate = (
        " This key looks live: rotate it now, do not just move it; a secret that "
        "reached disk or a remote must be treated as compromised." if live else ""
    )
    reason = (
        f"BLOCKED: this writes a {label}, a hard-coded credential. Secrets never go "
        f"in source or a command line. Read it from an environment variable or a "
        f"secrets manager; put real values only in a gitignored .env (templates go "
        f"in .env.example with placeholder values).{rotate}"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)

#!/usr/bin/env python3
"""PostToolUse(Edit|Write) hook: lint agent-definition frontmatter.

Claude Code silently drops an agent whose Markdown frontmatter fails to parse
as YAML: no error, no warning, the agent just never appears in the registry.
Five agents shipped broken for a month with zero feedback that way. The usual
cause is a bare `description:` value containing a colon or wrapping onto new
lines; `description: >-` (folded block scalar) is the reliable spelling.

After any Edit/Write to a file under an agents/ directory (*/agents/*.md,
which also covers */.claude/agents/*.md), this hook re-reads the file and
YAML-parses its frontmatter. On failure it emits an advisory (never blocking)
hookSpecificOutput.additionalContext warning, the same mechanism as
enforce-verification.py's lint path, telling Claude the agent will be silently
dropped and how to fix it.

Dependency note: uses pyyaml via the system python3 (present in the active
pyenv python3; verified before shipping). If the import ever fails the hook
fails open like every convenience hook here, at the cost of losing the lint.

Convenience-grade: fails open (exit 0 on any internal error).
"""

import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # fail open: no pyyaml means no lint, never a wedge
    sys.exit(0)

# Files in agents/ dirs that are not agent definitions.
NON_AGENT_BASENAMES = {"AGENTS.md", "README.md", "CLAUDE.md"}


def is_agent_definition(file_path):
    normalized = file_path.replace("\\", "/")
    if "/agents/" not in normalized or not normalized.endswith(".md"):
        return False
    return os.path.basename(normalized) not in NON_AGENT_BASENAMES


def frontmatter_problem(file_path):
    """Return a human-readable problem with the file's frontmatter, or None."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None  # unreadable file is not this hook's problem
    if not text.startswith("---\n"):
        return "no frontmatter block (file must start with `---`)"
    # The closing fence is a line that is exactly `---` (not e.g. `----`).
    closing = re.search(r"\n---[ \t]*(?:\n|$)", text[4:])
    if not closing:
        return "frontmatter block is never closed with `---`"
    block = text[4:4 + closing.start()]
    try:
        parsed = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        return f"frontmatter is not valid YAML: {str(exc).splitlines()[0]}"
    if not isinstance(parsed, dict):
        return "frontmatter parsed but is not a key/value mapping"
    description = parsed.get("description")
    if not isinstance(description, str) or not description.strip():
        return "frontmatter has no `description` (required for the agent to register)"
    return None


def main():
    event = json.load(sys.stdin)
    if event.get("hook_event_name") != "PostToolUse":
        return
    file_path = (event.get("tool_input") or {}).get("file_path") or ""
    if not file_path or not is_agent_definition(file_path):
        return
    problem = frontmatter_problem(os.path.realpath(file_path))
    if not problem:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"AGENT FRONTMATTER LINT: {file_path}: {problem}. Claude Code "
                "silently drops agents with broken frontmatter from the "
                "registry; this agent will simply not exist, with no error "
                "shown. Fix it now. For descriptions containing colons or "
                "spanning lines, use a folded block scalar: `description: >-`."
            ),
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)

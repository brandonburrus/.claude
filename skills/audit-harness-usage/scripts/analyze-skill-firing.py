# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Report which library skills fire in real sessions, which never do, and where
the heaviest usage is, by scanning the Claude config directory's transcripts.

Skill invocations appear in transcripts as a Skill tool call carrying the skill
name, which serializes as `"skill":"<name>"` in the JSONL. We count those across
projects/**/*.jsonl and history.jsonl, then diff against the skills present under
skills/ to surface never-fired skills (cut or re-route candidates) and firings of
names with no local folder (bundled/plugin skills, not orphans to cut).

The script counts only; interpretation is the audit-harness-usage skill's job.
Usage:
    uv run analyze-skill-firing.py [--claude-dir PATH] [--top N]
"""
import argparse
import os
import re
import sys
from collections import Counter

# Matches the serialized Skill-tool argument `"skill":"create-skill"` (and the
# spaced variant). Skill names are kebab-case lowercase, so the charset is tight
# enough to avoid matching unrelated "skill" keys carrying prose.
SKILL_RE = re.compile(r'"skill"\s*:\s*"([a-z0-9][a-z0-9-]*)"')


def find_skill_dirs(claude_dir):
    """Skill names present in the library (a folder under skills/ with a SKILL.md)."""
    skills_root = os.path.join(claude_dir, "skills")
    names = set()
    try:
        for entry in os.listdir(skills_root):
            if os.path.isfile(os.path.join(skills_root, entry, "SKILL.md")):
                names.add(entry)
    except OSError as e:
        sys.exit(f"Cannot read skills directory {skills_root}: {e}")
    return names


def scan_file(path, counts, per_file):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return
    hits = SKILL_RE.findall(content)
    if hits:
        per_file[path] = len(hits)
        counts.update(hits)


def scan_transcripts(claude_dir, counts, per_file):
    projects = os.path.join(claude_dir, "projects")
    for root, _dirs, files in os.walk(projects):
        for name in files:
            if name.endswith(".jsonl"):
                scan_file(os.path.join(root, name), counts, per_file)
    history = os.path.join(claude_dir, "history.jsonl")
    if os.path.isfile(history):
        scan_file(history, counts, per_file)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claude-dir",
        default=os.path.expanduser("~/.claude"),
        help="Claude config directory (default: ~/.claude)",
    )
    parser.add_argument("--top", type=int, default=15, help="How many heaviest skills to list")
    args = parser.parse_args()

    claude_dir = os.path.realpath(args.claude_dir)
    library = find_skill_dirs(claude_dir)
    counts = Counter()
    per_file = {}
    scan_transcripts(claude_dir, counts, per_file)

    fired = set(counts)
    never_fired = sorted(library - fired)
    not_in_library = sorted(fired - library)  # bundled/plugin skills, not orphans

    print(f"Library skills: {len(library)}   |   distinct skills fired: {len(fired)}   "
          f"|   total firings: {sum(counts.values())}")
    print()

    print(f"== Heaviest-used skills (top {args.top}) ==")
    for name, n in counts.most_common(args.top):
        tag = "" if name in library else "   [not in library: bundled/plugin]"
        print(f"  {n:5d}  {name}{tag}")
    print()

    print(f"== Never-fired library skills ({len(never_fired)}) ==")
    print("   (cut candidates, or re-route candidates if the description never matches real phrasing)")
    for name in never_fired:
        print(f"  {name}")
    print()

    if not_in_library:
        print(f"== Fired but not in skills/ ({len(not_in_library)}) ==")
        print("   (bundled or plugin skills; not orphans to cut)")
        for name in not_in_library:
            print(f"  {counts[name]:5d}  {name}")
        print()

    busiest = sorted(per_file.items(), key=lambda kv: kv[1], reverse=True)[:5]
    if busiest:
        print("== Busiest transcripts (read these for recurring-correction patterns) ==")
        for path, n in busiest:
            print(f"  {n:4d} skill-calls  {path}")


if __name__ == "__main__":
    main()

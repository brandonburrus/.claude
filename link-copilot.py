#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["questionary>=2.0"]
# ///
"""Interactively symlink Claude skills and agents into the Copilot CLI config dir.

  Skills: ~/.claude/skills/<name>/    ->  ~/.copilot/skills/<name>
  Agents: ~/.claude/agents/<name>.md  ->  ~/.copilot/agents/<name>.agent.md

Copilot expects agent files to end in `.agent.md`, so the symlink is renamed on
the Copilot side while sharing the original file content.

The checkbox selection is the desired end state: checked items get linked,
unchecked items that are currently linked get unlinked. Only symlinks that point
back into ~/.claude are ever removed; real files and directories are untouched.

Run it:  ./link-copilot.py   (or)   uv run link-copilot.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import questionary

CLAUDE_DIR = Path.home() / ".claude"
COPILOT_DIR = Path.home() / ".copilot"

SKILLS_SRC = CLAUDE_DIR / "skills"
AGENTS_SRC = CLAUDE_DIR / "agents"
SKILLS_DST = COPILOT_DIR / "skills"
AGENTS_DST = COPILOT_DIR / "agents"


class Item:
    """A linkable unit: its source in ~/.claude and its destination in ~/.copilot."""

    def __init__(self, name: str, src: Path, dst: Path):
        self.name = name
        self.src = src
        self.dst = dst

    @property
    def linked(self) -> bool:
        """True when dst is a symlink already resolving to src."""
        return self.dst.is_symlink() and _resolve(self.dst) == self.src.resolve()


def _resolve(link: Path) -> Path | None:
    """Resolve a symlink's target (absolute), tolerating broken links."""
    raw = Path(os.readlink(link))
    target = raw if raw.is_absolute() else (link.parent / raw)
    try:
        return target.resolve()
    except OSError:
        return None


def discover_skills() -> list[Item]:
    """Skills are directories under ~/.claude/skills that contain a SKILL.md."""
    return [
        Item(p.name, p, SKILLS_DST / p.name)
        for p in sorted(SKILLS_SRC.iterdir())
        if p.is_dir() and (p / "SKILL.md").exists()
    ]


def discover_agents() -> list[Item]:
    """Agents are *.md files under ~/.claude/agents, excluding AGENTS.md docs."""
    return [
        Item(p.stem, p, AGENTS_DST / f"{p.stem}.agent.md")
        for p in sorted(AGENTS_SRC.glob("*.md"))
        if p.name != "AGENTS.md"
    ]


def select(label: str, items: list[Item]) -> set[str] | None:
    """Show a checkbox prompt pre-checked to current link state. None = cancelled."""
    if not items:
        print(f"No {label} found.")
        return set()
    choices = [
        questionary.Choice(title=i.name, value=i.name, checked=i.linked) for i in items
    ]
    answer = questionary.checkbox(
        f"Select {label} to symlink into Copilot:", choices=choices
    ).ask()
    return None if answer is None else set(answer)


def apply(items: list[Item], desired: set[str]) -> None:
    """Make the filesystem match `desired`: link checked, unlink deselected."""
    for item in items:
        if item.name in desired:
            _link(item)
        elif item.dst.is_symlink() and _points_into_claude(item.dst):
            item.dst.unlink()
            print(f"  unlinked  {item.dst.name}")


def _link(item: Item) -> None:
    if item.linked:
        return
    item.dst.parent.mkdir(parents=True, exist_ok=True)
    if item.dst.is_symlink():
        item.dst.unlink()  # stale link, repoint it
    elif item.dst.exists():
        print(f"  SKIPPED   {item.dst.name} (a real file/dir is in the way)")
        return
    item.dst.symlink_to(item.src)
    print(f"  linked    {item.dst.name} -> {item.src}")


def _points_into_claude(link: Path) -> bool:
    """Guard so we only ever remove symlinks we manage, never foreign ones."""
    target = _resolve(link)
    claude = CLAUDE_DIR.resolve()
    return target is not None and (target == claude or claude in target.parents)


def main() -> int:
    if not COPILOT_DIR.is_dir():
        print(f"Copilot config dir not found: {COPILOT_DIR}", file=sys.stderr)
        return 1

    skills = discover_skills()
    agents = discover_agents()

    chosen_skills = select("skills", skills)
    if chosen_skills is None:
        print("Cancelled.")
        return 1
    chosen_agents = select("agents", agents)
    if chosen_agents is None:
        print("Cancelled.")
        return 1

    print("\nApplying changes:")
    apply(skills, chosen_skills)
    apply(agents, chosen_agents)
    print(
        f"\nDone. {len(chosen_skills)} skill(s) and {len(chosen_agents)} agent(s) "
        f"linked into {COPILOT_DIR}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

---
name: audit-agent-context
description: >-
  Use this skill to audit a codebase or project for proper AGENTS.md coverage
  and conformance against the CLAUDE.md contextual-documentation standard:
  whether the root and key subsystems have AGENTS.md files, whether each carries
  the required sections, whether the content still matches the code, and whether
  any decision logs follow the format and the gates. Use when the user says
  "audit the AGENTS.md files", "audit agent context", "check AGENTS.md
  coverage", "are the AGENTS.md files proper", "is this project documented for
  agents", or "review the agent context docs". The deliverable is an audit
  report with per-file findings and fixes. Do not use for writing a project's
  first AGENTS.md (use onboard-codebase), for tightening the always-on context
  to cut bloat (use tune-context), for capturing a new learning into AGENTS.md
  (use learn-from-context), or for general architecture review (use
  audit-architecture).
---

## Purpose

Audit a codebase for AGENTS.md coverage and conformance against the CLAUDE.md "Maintaining Contextual Documentation" standard, and report what is missing, malformed, drifted from the code, or mis-recorded, with a specific fix per finding. The deliverable is the audit, not the fixes; apply them on request, hand a missing root to `onboard-codebase`, or hand bloat to `tune-context`. The discipline is auditing content against reality, not just checking that files exist: a present-but-stale AGENTS.md passes a file check and fails the standard, and a doc that contradicts the code is the worst case because it misleads every agent that trusts it.

## What the standard requires

The criteria below mirror the CLAUDE.md standard; if they ever differ, CLAUDE.md governs.

**Root AGENTS.md** must carry:

- What the project is and its purpose, in one or two sentences
- Conventions: code style, documentation structure, git conventions, and other project conventions
- Critical Constraints: the must-follow rules
- A high-level project-structure overview (key directories and files and their purpose)
- Globally useful orientation for an agent working here for the first time

**Directory-proximate AGENTS.md**, for every key system, subsystem, module, component, or feature:

- Its purpose, in one or two sentences
- How it works at a high level and how it fits the larger project
- Critical information a first-time agent needs (invariants, gotchas, constraints)
- How it relates to the other components at its level

**Decision records** (a Key Decisions section, where present) must be one line each, two sentences hard cap, in the form `- YYYY-MM-DD: <what was decided>. Why: <one short clause>.`, and only for choices that pass both gates: the decision constrains future work, and it is not already evident from the code, git history, or other docs.

## Workflow

Copy this checklist and track progress:

```text
Audit agent context:
- [ ] 1. Map the structure and the expected AGENTS.md set
- [ ] 2. Check coverage (present where they should be)
- [ ] 3. Check conformance (required sections present)
- [ ] 4. Check correctness against the code (drift)
- [ ] 5. Check decision-log hygiene
- [ ] 6. Report, ordered by severity
```

### 1. Map the structure and the expected AGENTS.md set

Walk the repo (`find . -name AGENTS.md` for what exists, plus the directory tree for what should). Identify the root and every genuine system, subsystem, or feature boundary. The expected set comes from the real structure, not an idealized architecture, and "key" is the operative word: a leaf utility folder does not need its own AGENTS.md, and demanding one there is a finding against you, not the project.

### 2. Check coverage

For each expected location, does an AGENTS.md exist? A missing root is the top coverage finding; the root is mandatory. Missing files at real subsystem boundaries are gaps. Note over-coverage too: an AGENTS.md in a trivial directory is noise the standard does not ask for.

### 3. Check conformance

For each AGENTS.md, confirm the required sections from the standard above are actually present (as content, not necessarily as a literal heading). Flag the missing ones by name. A root file with no Critical Constraints, or a component file that states purpose but never how it fits, is incomplete.

### 4. Check correctness against the code

This is the highest-value check. Spot-check the claims against reality: does the structure overview match the actual directories, do the stated conventions match what the code does, do referenced files, paths, and commands still exist? A doc that contradicts the code is worse than a missing one, because the next agent trusts it and is misled; rank drift above absence.

### 5. Check decision-log hygiene

For any Key Decisions section, flag:

- **Changelog creep**: entries that log completed work ("added X", "fixed Y", verification results, file inventories, implementation summaries). The standard bans these outright; git history is the work log. This is the most common real finding.
- **Format violations**: records not in the `YYYY-MM-DD: ... Why: ...` one-line form.
- **Gate failures (prune candidates)**: decisions that are self-evident from the code or that do not constrain future work; they are noise to delete.
- **Misrouting**: a durable rule sitting in the decision log that belongs in Critical Constraints or Conventions, or a component fact that belongs in that component's AGENTS.md.

### 6. Report, ordered by severity

Lead with drift (docs that contradict the code), then missing root, then coverage gaps at real boundaries, then conformance gaps, then decision-log hygiene. Name the file and the exact fix for each. Offer to apply fixes, or to route a missing root to `onboard-codebase` and bloat to `tune-context`.

## Output shape

```markdown
## Agent-context audit: <project>

**Verdict:** <one line: healthy / gaps / drifted>

### Drift (docs contradicting the code)
- `<file>`: <claim> contradicts <reality>; <fix>

### Coverage
- Missing: `<dir>/AGENTS.md` at <subsystem>; <what it should cover>
- Over-documented: `<dir>/AGENTS.md` is a trivial location; consider removing

### Conformance
- `<file>`: missing <section(s)>

### Decision-log hygiene
- `<file>`: <changelog creep / format / prune candidate / misrouted>, <fix>
```

## Gotchas

- **Presence is not conformance.** A file that exists but is a stale changelog passes a `find` and fails the standard. Audit the content, never just the filename.
- **Drift outranks absence.** A doc that contradicts the code actively misleads; it is the priority finding, not a nitpick. A missing doc only leaves the agent to read the code, which it can do.
- **Over-documentation is also a failure.** The standard asks for AGENTS.md at key systems, not every directory; flagging a leaf util folder as a gap manufactures noise and trains the project toward documentation no one maintains.
- **Changelog creep is the usual rot.** AGENTS.md files drift into logs of what was done; the standard is explicit that they hold durable context (invariants, gotchas, constraints), not a work history. Expect this to be most of your findings.
- **The decision log is not a catch-all.** Records that fail the two gates, or durable rules misfiled there instead of in Constraints, are findings; the log is only for choices that needed a reason and are not evident from the code.

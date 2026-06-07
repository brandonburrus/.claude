---
name: audit-architecture
description: >-
  Use this skill when evaluating a codebase's architecture and surfacing
  improvement candidates, including finding refactoring opportunities,
  consolidating tightly-coupled modules, making code more testable, or when
  the user says "audit the architecture", "review the structure of this
  codebase", "why is this so hard to change", or "find tech debt". Also use
  when the fix skill escalates after repeated failed fixes in one area. Do not
  use for designing new systems (use write-tech-spec), for implementing the
  improvements it proposes (use create-code-plan then refactor-code), or for
  reviewing a single change (use review-pull-request).
---

## Purpose

Surface architectural friction and propose deepening opportunities: refactors that turn shallow modules into deep ones, judged by testability and navigability. The deliverable is an evidence-backed candidate list with a top recommendation; this skill never implements. Architecture problems hide behind symptom-level fixes, which is why the fix skill escalates here after three failed fixes in one area: at that point the defect is probably in the structure, not the lines.

## Vocabulary

Use these terms exactly; consistent language is what keeps candidates comparable:

- **Module**: anything with an interface and an implementation (function, class, package, slice)
- **Interface**: everything a caller must know to use the module: types, invariants, error modes, ordering, config. Not just the type signature
- **Depth**: leverage at the interface; a lot of behavior behind a small interface is deep, an interface nearly as complex as its implementation is shallow
- **Seam**: where an interface lives; a place behavior can be altered without editing in place
- **Leverage**: what callers get from depth. **Locality**: what maintainers get: change, bugs, and knowledge concentrated in one place
- **The deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through; if complexity reappears across N callers, it was earning its keep
- One adapter behind a seam is a hypothetical seam; two adapters make it real

## Workflow

### 1. Read the recorded decisions first

AGENTS.md, docs/adr/, CONTEXT.md or domain glossaries, and the tech spec if one exists. ADRs record decisions this audit must not re-litigate; a candidate that contradicts one is surfaced only when the friction is strong enough to justify reopening the decision, and is flagged as such explicitly. Use the project's domain vocabulary for domain things and this skill's vocabulary for structural things.

### 2. Explore for friction, not for rule violations

Walk the codebase (the Explore subagent fits this; medium thoroughness for a subsystem, very thorough for a whole repo). Hunt friction organically rather than pattern-matching a checklist:

- Understanding one concept requires bouncing between many small modules
- Shallow modules: wrappers and pass-throughs whose interface costs as much to learn as the implementation would
- Pure functions extracted "for testability" while the real bugs live in how they are called (no locality)
- Tightly-coupled modules leaking state or knowledge across their seams
- Code that is untested because its current interface makes testing miserable
- Change amplification: the one-line behavior change that touches five files every time

Apply the deletion test to every suspected pass-through. Verify each suspicion in the actual code before it becomes a candidate; an audit that mis-describes the codebase burns its credibility on the first card.

### 3. Present candidates

For each candidate:

```markdown
### <Candidate name, in domain vocabulary>

- **Files**: <modules involved>
- **Problem**: <the friction, with the evidence that shows it: call sites, change history, test gaps>
- **Solution**: <plain-English shape of the deepened module; no code>
- **Benefits**: <in terms of locality, leverage, and which tests become possible or simpler>
- **Strength**: Strong | Worth exploring | Speculative
```

Offer a before/after diagram via create-diagram when the relationship is graph-shaped. End with a **Top recommendation**: the candidate to tackle first and why (usually highest friction-to-risk ratio, not the biggest). Then stop and ask which candidates the user wants to explore; do not start designing interfaces unprompted.

### 4. Grill the chosen candidate

Walk the design tree with the user in dependency order: constraints, what sits behind the new seam, the shape of the deepened interface, what survives of the existing tests. One question at a time with a recommended answer (the clarify-ambiguity Grill mode mechanics). As decisions crystallize:

- A rejected candidate with a load-bearing reason gets an offer to record it via write-adr, framed as preventing future audits from re-suggesting it; skip the offer for ephemeral reasons ("not now")
- New domain terms coined for deepened modules go into the project's glossary or AGENTS.md

### 5. Hand off implementation

The agreed design routes to create-code-plan (and execution under refactor-code's test gate when behavior-preserving). This skill's output ends at the plan handoff.

## Guardrails

- Never propose a rewrite where a deepening exists; "replace the module" is the last resort after the deletion test says the module is genuinely a pass-through.
- Every candidate cites evidence from the actual code; no candidate from vibes or from this skill's own examples.
- Respect ADRs by default; contradicting one is an explicit, flagged act.
- Do not pad the list. Two strong candidates beat seven speculative ones; an empty result ("the architecture fits the codebase's current size") is a valid audit.

## Gotchas

- **Shallow-module sprawl usually came from good intentions.** Single-responsibility taken to powder turns one deep concept into twelve files; the fix is consolidation, which feels wrong to engineers trained to split. Lead with the deletion test evidence.
- **Testability is the sharpest lens.** "What would it take to test this through its interface" exposes shallowness faster than any dependency diagram; if the answer is "mock five collaborators", the seam is in the wrong place.
- **The audit is read-only.** The moment it starts editing, scope discipline dies and the user gets an unrequested refactor instead of a decision. Candidates, decision, plan, then code, in that order.
- **Friction clusters around the money path.** Audit where changes actually happen (git log frequency is evidence) rather than where the code looks ugliest; ugly-but-stable code earns its keep by never needing attention.

---
name: write-docs
description: >-
  Use this skill when generating or organizing a documentation set for a
  codebase, library, CLI, or API: writing a README and docs from scratch,
  filling documentation gaps, or restructuring docs that have become a
  confusing pile. Use when the user says "document this", "write the docs",
  "the docs are a mess", "add docs for this feature", or "what docs does this
  need". Do not use for the prose craft of a single explainer or tutorial (use
  teach-through-writing), for recording one architectural decision (use
  write-adr), or for API contract definition (use design-api).
---

## Purpose

Produce a complete, navigable documentation set partitioned by the Diataxis framework: every document serves exactly one of four reader needs, and the set as a whole covers the public surface. The failure this prevents is the all-too-common documentation blob that tries to teach, instruct, specify, and explain in one undifferentiated wall, serving none of those needs well. Read the code before writing a line; documentation written from the README and guesses describes a system that does not exist.

## The four Diataxis modes

Every documentation page serves one reader in one mode. Mixing modes in a single page is the central anti-pattern; a tutorial that stops to explain design rationale loses the learner, and a reference that pauses to teach loses the lookup.

| Mode | Reader's question | Orientation | The page is | Voice |
|---|---|---|---|---|
| Tutorial | "Teach me, I'm new here" | Learning | A lesson with a guaranteed working result | "We will build..." hands-on, no detours |
| How-to guide | "How do I accomplish X?" | Task | A recipe for a goal the reader already has | "To do X: step, step, step" |
| Reference | "What exactly is Y?" | Information | A complete, dry, authoritative description | "Z accepts these params, returns this" |
| Explanation | "Why is it this way?" | Understanding | A discussion of context, tradeoffs, alternatives | "This was chosen because..." |

The two axes that disambiguate them: tutorials and how-tos are *action* (the reader is doing); reference and explanation are *cognition* (the reader is studying). Tutorials and explanation serve *study/acquisition*; how-tos and reference serve *work/application*. When unsure which mode a page is, name the reader's question out loud; it lands in exactly one cell.

## Workflow

Copy this checklist and track progress:

```text
Docs Progress:
- [ ] 1. Codebase archaeology
- [ ] 2. Partition: decide which modes each subject needs
- [ ] 3. Draft each page in its single mode
- [ ] 4. Cross-link the modes
- [ ] 5. Quality gates
```

### 1. Codebase archaeology

Read the actual public surface before writing: entry points, exported functions and types, CLI commands and flags, API routes, config options, the existing README and any docs. List the complete public surface; this list is the coverage contract for the Reference pages and the menu of candidate How-to goals. Documenting from memory or the existing README guarantees describing half the feature and inventing the other half.

### 2. Partition: decide which modes each subject needs

Not every subject needs all four modes; forcing four pages per thing is how doc sets bloat. Decide per subject:

| Subject | Usually needs |
|---|---|
| A whole product or library (new user) | Tutorial (one, the getting-started path) + Reference + a How-to per common task |
| A public API surface, CLI, config schema | Reference (complete, mandatory) + How-to per real task |
| An internal module or subsystem | Reference + Explanation (the why); rarely a tutorial |
| A non-obvious design decision or model | Explanation (and link it from write-adr if a decision record exists) |

Rules: one Tutorial is usually enough for a whole product (the single path that gets a newcomer to a working result); add a How-to only for a task a real user actually performs, not every API method; Reference must cover the full surface from step 1.

### 3. Draft each page in its single mode

Hold each page to its mode's contract:

- **Tutorial**: a concrete, runnable, start-to-finish path that produces a visible result, fast (aim for the first working result within roughly three steps). Every command runs as written. No "you could also", no rationale detours, no error-handling lectures; a learner needs momentum and a win, not completeness. Teaching craft within the lesson is `teach-through-writing`'s job.
- **How-to**: title starts with "How to"; assumes the basics; solves one stated goal; ends when the goal is met. Real-world messy goals ("How to deploy behind a corporate proxy"), not feature tours.
- **Reference**: complete and austere. Every public item: signature, parameters with types and defaults, return shape, errors, one minimal example. Pull facts directly from the code, never from memory. Dry is correct here; reference is consulted, not read.
- **Explanation**: the why. Context, the alternatives considered and rejected, the tradeoffs, the boundaries of the design. This is the only mode where opinion and discussion belong.

### 4. Cross-link the modes

The set works because the modes connect: each Reference entry links to the How-to that uses it; each How-to links to the Reference for its objects; the Tutorial links onward to both for "where next"; Explanation links to the Reference it contextualizes. A reader in the wrong mode for their need should be one click from the right one. Provide an index (README or docs landing) that routes by reader intent: new here / how do I / what is / why.

### 5. Quality gates

Before declaring the set done:

- [ ] Every public item from step 1 appears in Reference (the coverage contract holds)
- [ ] Every code example and tutorial command actually runs as written, against the current code
- [ ] No page mixes modes (no rationale in the tutorial, no teaching in the reference)
- [ ] Every How-to solves a goal a real user has, and its title names that goal
- [ ] The cross-links resolve and the index routes by intent
- [ ] Names (functions, commands, types) match the code and each other across all pages

## Gotchas

- **Mode-mixing is the disease Diataxis cures; do not reintroduce it.** The instinct to "be helpful" by adding a why-paragraph to a tutorial or a worked lesson to a reference is exactly the instinct that produced the unusable blob. Put the why in Explanation and link it.
- **Reference is generated from the code, not the docs.** The single most common doc defect is a reference that drifted from the implementation. Read signatures and defaults from source every time; a confidently wrong default is worse than a missing one.
- **One tutorial, not one per feature.** Tutorials are expensive to maintain (every step must keep working) and a newcomer needs one reliable path, not twelve. Breadth lives in How-to and Reference; the Tutorial is the single front door.
- **A How-to per API method is reference cosplay.** If the "guide" is just one method with its params, it belongs in Reference. How-to earns its page only when it composes several steps toward a goal the reader brought with them.
- **Documentation that lies is worse than none.** A reader trusts docs and stops reading code; a stale example sends them down a path that no longer exists. The "examples run as written" gate is not optional polish, it is the credibility of the whole set.

---
name: vibe-code
description: >-
  Use this skill when building a throwaway prototype or quick spike to answer
  a design question before committing to it, including sanity-checking a data
  model or state machine, mocking up UI directions, or exploring options. Use
  when the user says "vibe code", "prototype this", "spike it", "quick and
  dirty", "just hack something together", "let me play with it", or "try a few
  designs". Do not use for production code of any kind (use follow-tdd), for
  fixing bugs (use fix), or for work the user has not explicitly framed as
  disposable.
---

## Purpose

Build throwaway code that answers a question, fast. A prototype is the sanctioned suspension of the library's quality gates: no TDD, no test gate, no polish, by declaration instead of by erosion. The price of that suspension is the throwaway contract: the code is marked disposable from the first file, it never graduates to production by renaming, and the only artifact worth keeping is the answer. The question decides the shape, so name the question before writing anything.

## Pick the branch by the question

| Question | Build |
|---|---|
| "Does this logic / state model / data shape feel right?" | A tiny interactive terminal app that pushes the model through the cases that are hard to reason about on paper |
| "What should this look like?" | Several radically different UI variations on one route, switchable via a URL param, so comparison is one keystroke |
| Genuinely ambiguous, user unreachable | Match the surrounding code (backend module = logic; page or component = UI) and state the assumption at the top of the prototype |

Getting the branch wrong wastes the whole prototype; a beautiful UI mock answers nothing about whether the state machine has a hole in it.

## The throwaway contract

1. **Marked disposable from day one.** Prototype-obvious naming (`proto-`, `PROTOTYPE` in the filename or route), located next to the code it is prototyping for so context is obvious, following the project's existing routing and runner conventions rather than inventing structure.
2. **One command to run.** Whatever the project's runner already supports; the user starts it without thinking, because friction at the run step kills the play loop the prototype exists for.
3. **No persistence by default.** State lives in memory; persistence is usually the thing being checked, not a dependency. When the question genuinely involves a database, use a scratch store named to be wiped.
4. **Skip the polish, deliberately.** No tests, no error handling beyond runnable, no abstractions, no design-ui pass. These are not corners cut; they are the speed the prototype buys.
5. **The security floor stays on.** harden-security's Never tier holds even here: no real credentials in code, no disabled certificate checks, no untrusted input piped to eval or the shell. A prototype with a leaked secret is an incident, not a draft.
6. **Surface the state.** After every action (logic) or on every variant switch (UI), show the full relevant state; the user is here to see what changed, and hidden state defeats the play.
7. **Time-box it.** A prototype that consumes a day is a project wearing a disguise; if the question is not converging, that is itself the answer (the design is underspecified), and the route is clarify-ambiguity, not more prototype.

## When the question is answered

- **Capture the answer durably**: what was asked, what the prototype showed, what was decided. The home follows the decision's shape: an ADR for a significant choice (write-adr), a line in the relevant AGENTS.md, the ticket (decompose-into-tasks treats decision-rich prototype snippets like state machines and schemas as the one allowed code-in-ticket exception), or learn-from-context when the lesson generalizes.
- **Delete the prototype, or explicitly absorb the decision.** Absorbing means rebuilding the validated design under follow-tdd with the prototype open as reference; it never means renaming the prototype into production. Prototype code carries every shortcut from rule 4 invisibly, and promoting it imports those shortcuts as latent bugs with no test coverage marking where they live.
- **Leave nothing rotting.** A stale prototype in the repo becomes load-bearing the moment someone imports it; that is how "it's just a prototype" becomes the production payment path.

## Gotchas

- **The contract is what makes the speed legitimate.** Skipping tests inside vibe-code is the design; skipping tests because work drifted from a prototype into a feature is gate erosion. The moment the user starts treating the output as the implementation, stop and say the quiet part: this needs the rebuild, not a cleanup pass.
- **Prototypes answer one question well and several questions badly.** "While we're in here, also check X" stacks questions until the prototype is an unplanned app; spin the second question into its own prototype or its own ticket.
- **The terminal-app branch beats print statements.** An interactive loop the user drives (enter a command, see the state) finds the awkward transitions that a hardcoded script of happy-path calls never visits.
- **UI variations must be radically different, not three paddings of the same idea.** The point of variants is to explore the space; near-duplicates spend the prototype budget confirming a bias.

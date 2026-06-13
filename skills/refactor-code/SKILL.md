---
name: refactor-code
description: Use this skill when refactoring or simplifying working code without
  changing its behavior, including reducing complexity, improving names, removing
  duplication, untangling nested logic, or cleaning up after a feature lands. Use
  when the user says "refactor this", "simplify this", "clean this up", "this code
  is a mess", or "make this readable". Do not use for fixing bugs (use fix), adding
  features, or architectural rewrites that change behavior (plan those with
  create-code-plan).
---

## Purpose

Reduce complexity while preserving behavior exactly: same outputs, same side effects and their ordering, same error behavior, same edge cases. The goal is comprehension speed, never line count; every change must pass "would a new team member understand this faster than the original?" Behavior preservation is only verifiable through a feedback loop, which is why this skill has one hard gate.

**The Test Gate: no refactoring without green tests covering the target code.** Without them, "the refactor preserved behavior" is a claim, not a fact, and the claim is wrong often enough that the gate exists. Violating the letter of this gate is violating its spirit.

## Workflow

Copy this checklist and track progress:

```text
Refactor Progress:
- [ ] 1. Scope pinned
- [ ] 2. Code understood (Chesterton's Fence)
- [ ] 3. Test Gate passed (green run recorded)
- [ ] 4. Opportunities identified
- [ ] 5. Findings recorded (tagged, one line each)
- [ ] 6. Changes applied one at a time, tests between
- [ ] 7. Whole-result verification
```

### 1. Pin the scope

Default to the code the user named or recently changed, nothing more. Drive-by refactoring of neighboring code buries the intended change in diff noise and risks regressions in code nobody asked you to touch. If adjacent code deserves work, say so and let the user decide.

### 2. Understand before touching (Chesterton's Fence)

For each piece you intend to change, answer: what is its responsibility, what calls it and what does it call, what are the edge cases and error paths, and why might it have been written this way (check `git blame`; performance, platform constraints, and historical workarounds all masquerade as needless complexity). If you cannot answer these, you are not ready to refactor; read more first.

### 3. The Test Gate

Run the tests that cover the target code and record the green run.

- **No tests, or coverage misses the target**: stop. Offer to write characterization tests first, pinning current behavior exactly as it is, including any oddities (handing the writing to the follow-tdd skill). Refactoring resumes only when they pass.
- **Tests exist but fail**: stop. A failing suite means the behavior baseline is unknown; fixing the failure is a fix-skill job, and refactoring on red would launder a behavior change as cleanup.
- Do not write the tests after refactoring instead; tests written after pin the new behavior, including any breakage the refactor introduced, which defeats the entire point of the gate.

### 4. Identify opportunities

Concrete signals, not vague smells:

| Category | Signal | Move |
|---|---|---|
| Structure | Nesting 3+ deep | Guard clauses or extracted helpers |
| Structure | Function doing several jobs (often 50+ lines) | Split along responsibility lines |
| Structure | Nested ternaries, boolean flag parameters | if/else or lookup; options object or separate functions |
| Naming | `data`, `temp`, `result`, `val` | Name the content (`validationErrors`) |
| Naming | Name lies about behavior (a `get` that mutates) | Rename to the truth |
| Comments | "What" comments restating the code | Delete; keep and protect "why" comments |
| Redundancy | Same logic in several places | Extract once |
| Redundancy | Dead code, commented-out blocks | Remove after confirming truly dead |
| Redundancy | Single-use wrapper adding nothing | Inline it |

#### First rung that holds

Once an opportunity is spotted, the table says what to change but not how far to go. Climb this ladder and stop at the first rung that works; reaching past it adds the complexity you came to remove.

1. **Does this need to exist at all?** Code with no current caller or a speculative-only one is deletable (YAGNI).
2. **Standard library does it?** Replace the hand-rolled version with the stdlib call.
3. **Native platform feature covers it?** Prefer it over custom code (a DB constraint over app-level checks, CSS over JS).
4. **An already-installed dependency solves it?** Use it before writing more code; never add a new dependency for what a few lines already handle.
5. **Can it be one clear line?** One line, as long as it still reads in a single pass.
6. **Only then**: the minimum custom code that works.

Two rungs both hold? Take the higher one and move on; this is a reflex for scoping a simplification, not a research project. The lower rungs stay subject to the same behavior-preservation gate as everything else.

### 5. Record findings (tagged, one line each)

Before applying anything, list each simplification as a single scannable line so the scope is reviewable at a glance: `<location>: <tag> <what to cut>. <what replaces it>.`

- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled logic the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same behavior, fewer lines. Show the shorter form.

The tags map onto the ladder rungs, so the finding already says which rung it stopped at. Example: `auth.ts:L12-38: stdlib: 27-line email validator. Regex check is one line; real validation is the confirmation mail.`

### 6. One change at a time

For each simplification: make the change, run the tests, then commit or continue; on red, revert and reconsider rather than patching forward. Never batch untested simplifications, because a red run after five changes tells you nothing about which one broke. Keep refactor commits separate from feature and fix commits. If the total would touch more than ~500 lines, reach for automation (codemods, AST transforms) instead of hand edits.

### 7. Verify the whole

After the pass: is the result genuinely easier to understand, does it match the project's conventions rather than your preferences, is the diff clean of unrelated changes, and did every test pass without modification? If the "simplified" version reads worse, revert it; not every attempt succeeds, and reverting is a valid outcome.

## Over-simplification traps

Simplification has its own failure mode; these moves feel like cleanup and make things worse:

- Inlining a helper whose name carried a concept; the call site now needs a comment instead
- Merging two simple functions into one complex one because they were near each other
- Removing an abstraction that exists for testability or a real second caller
- Golfing for line count; a dense one-liner that needs a mental pause lost the trade
- Stripping error handling because the happy path looks cleaner without it

## Rationalizations

| Excuse | Reality |
|---|---|
| "I had to update the tests to make them pass" | Then behavior changed; that is not a refactor. Revert and find the preserving version |
| "I'll write the tests after refactoring" | Tests written after pin the new behavior, bugs included; the gate is before, and after is worthless |
| "It obviously preserves behavior" | Obviousness is the claim; the green run is the fact. The gate exists because they diverge |
| "While I'm here, this file could use cleanup too" | Scope creep; mention it and let the user decide |
| "Fewer lines is simpler" | Comprehension speed is the metric; line count is not |
| "This abstraction is unnecessary" | Chesterton's Fence; find out why it exists before tearing it down |

## Red flags

Stop and reassess if you notice any of these in your own work:

- Any test modified to make the suite pass
- The refactored version is longer or harder to follow than the original
- You are refactoring code whose purpose you cannot state in one sentence
- Error handling got removed or weakened
- The diff mixes refactoring with feature or fix changes
- You renamed things to your own taste against the project's conventions

## Gotchas

- **Behavior includes more than outputs.** Side-effect ordering, error types and messages, logging, and performance characteristics are observable behavior; a consumer somewhere depends on each (Hyrum's Law applies to internals too).
- **Characterization tests pin bugs as well as features.** That is correct: the refactor must preserve the bug, because fixing it is a separate change with its own test (the fix skill's job). One commit doing both hides the fix inside noise.
- **Performance-critical code can be simpler and slower.** Where speed is a stated requirement, measure before and after; a clean version that misses its latency budget is a regression, not a cleanup.
- **Generated and vendored code is not yours to clean.** Refactoring it dies on the next regeneration; fix the generator or leave it.

---
name: test-driven-development
description: Use this skill when implementing any feature, fixing any bug, or changing
  any code behavior, before writing the implementation code. Also use when the user
  says "TDD", "test first", "red-green-refactor", "write the test before the code",
  or reports a bug that needs fixing. Do not use for pure configuration changes,
  documentation, static content, or for runtime-verifying an already-built change
  (use the verify skill for that).
---

## Purpose

Drive every behavior change with a failing test written first. Tests are proof; "seems right" is not done. Do not write any production code until a failing test exists for it, and do not declare work complete until the Verification Checklist passes.

## The Iron Law

```text
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before its test? Delete it. Start over.

**No exceptions:**
- Do not keep it as "reference"
- Do not "adapt" it while writing the tests
- Do not look at it
- Delete means delete

Why this severe: code written first biases the tests toward what you built instead of what is required, and tests written after pass immediately, which proves nothing. The deletion is not punishment; it is the only way the rewritten code is actually derived from the tests.

**Violating the letter of this rule is violating its spirit.** Arguments that a workaround honors the spirit are the failure mode, not an exception.

The only exceptions, each requiring user confirmation first: throwaway exploration spikes (thrown away before the real implementation starts with TDD) and generated code.

## Workflow

Copy this checklist and track each cycle:

```text
TDD Cycle:
- [ ] 1. Behaviors listed and prioritized
- [ ] 2. RED: one failing test written
- [ ] 3. Verify RED: watched it fail for the right reason
- [ ] 4. GREEN: minimal code to pass
- [ ] 5. Verify GREEN: test passes, full suite green
- [ ] 6. REFACTOR: clean up, tests stay green
- [ ] 7. Repeat for next behavior
```

### 1. List the behaviors

Before any test, list the behaviors to verify (not implementation steps), using the project's existing domain vocabulary. You cannot test everything; prioritize critical paths and complex logic over exhaustive edge-case enumeration, and confirm priorities with the user when the interface design is not already settled.

### 2. RED: write one failing test

One test, one behavior, through the public interface.

- One behavior per test; an "and" in the test name means split it
- The name reads like a specification: "rejects empty email", not "test1" or "validation works"
- Real code paths; test doubles only at system boundaries (see references/test-quality.md)
- Assert on outcomes (state), not on which methods were called internally; interaction assertions break on refactors even when behavior is unchanged

### 3. Verify RED: watch it fail

Mandatory, never skip. Run the test and confirm:

- It fails, not errors: a syntax error or broken import is not a valid RED
- It fails because the feature is missing, with the failure message you expected

If the test passes immediately, you are testing behavior that already exists; fix the test, not the code. If you cannot explain why it failed, you do not know what it tests.

### 4. GREEN: minimal code to pass

Write the simplest code that makes this test pass. Do not anticipate future tests, add options, or improve neighboring code; speculative generality is how minimal implementations become over-engineered ones (YAGNI).

### 5. Verify GREEN: watch it pass

Run the test: it passes. Run the full suite: nothing else broke. Output is pristine: no new errors or warnings. If the test fails, fix the code, not the test. Do not re-run an unchanged passing suite for reassurance; re-run only after edits.

### 6. REFACTOR: clean up on green only

Remove duplication, improve names, extract helpers. Run tests after each refactor step; behavior does not change. Never refactor while RED.

### 7. Repeat

Next behavior, next failing test. Each cycle is a complete vertical slice.

## Vertical Slices, Not Horizontal

Do not write all the tests first and then all the implementation:

```text
WRONG (horizontal):  test1, test2, test3 ... then impl1, impl2, impl3
RIGHT (vertical):    test1 -> impl1, test2 -> impl2, test3 -> impl3
```

Tests written in bulk test imagined behavior, not actual behavior; you commit to test structure before the implementation has taught you anything. Each test should respond to what the previous cycle revealed.

## The Prove-It Pattern (Bug Fixes)

When a bug arrives, do not start with the fix. Write a test that reproduces the bug and watch it fail; that failure is the proof the bug exists and the proof your fix works when it flips to green. Then run the full suite for regressions. Never fix a bug without a reproduction test: an untested fix can be a coincidence, and the regression returns silently.

For complex bugs, consider spawning a subagent to write the reproduction test from the bug report alone, without knowledge of the planned fix; tests written blind to the fix are harder to accidentally bias.

## Good Tests

| Quality | Do | Not |
|---|---|---|
| Minimal | One behavior per test | "and" in the name |
| Specified | Name describes expected behavior | "works", "handles errors" |
| Behavioral | Public interface, observable outcomes | Private methods, call sequences |
| Self-contained | DAMP: each test readable alone | Setup buried in shared helpers |
| Structured | Arrange-Act-Assert | Interleaved setup and assertions |
| Real | Real implementation > fake > stub > mock | Mocking your own modules |

When adding any mock, test double, or test utility, read `references/test-quality.md` first; it contains the gate functions and the anti-pattern catalogue (testing mock behavior, test-only production methods, incomplete mocks, over-mocking).

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. The test takes 30 seconds and documents intent. |
| "I'll write tests after" | Tests that pass immediately prove nothing; you verify what you built, not what was required. |
| "Tests-after achieve the same goals" | Tests-after answer "what does this do?"; tests-first answer "what should this do?" |
| "I already manually tested it" | Ad-hoc, no record, cannot re-run. Tomorrow's change breaks it silently. |
| "Deleting X hours of work is wasteful" | Sunk cost. Keeping unverified code is the real debt; you cannot trust it. |
| "Keep it as reference while I write tests" | You will adapt it. That is testing after. Delete means delete. |
| "I need to explore first" | Fine. Throw the exploration away and start the real implementation with TDD. |
| "The test is hard to write" | Hard to test means hard to use. Listen to the test; simplify the design. |
| "TDD will slow me down" | Debugging in production is slower. The test finds the bug before commit. |
| "It's about the spirit, not the ritual" | The ritual is the spirit. Watching the test fail is the only proof it tests anything. |
| "The behavior is already discovered; rebuilding just risks new bugs" | The understanding survives deletion and makes the rebuild fast. Where the rebuild diverges from the deleted code is exactly where the deleted code could not be trusted. |
| "Just this once" | Every exception becomes the norm under the next deadline. |
| "Production is down, no time for a test" | The reproduction test takes minutes and proves the emergency fix actually fixes the emergency. Shipping an unproven fix to a down system risks a second outage. |

## Red Flags: STOP and Start Over

- Code written before its test
- Test passes on its first run
- Cannot explain why the test failed
- "I'll add tests later" or "tests in a follow-up PR"
- "I already manually tested it"
- "Keep it as reference" or "adapt the existing code"
- "Already spent X hours, deleting is wasteful"
- "This case is different because..."
- Mock setup longer than the test logic
- Skipping or disabling tests to make the suite pass

All of these mean: delete the code, restart with TDD.

## When Stuck

| Problem | Solution |
|---|---|
| Do not know how to test it | Write the wished-for API call and the assertion first; ask the user if still stuck |
| Test too complicated | The design is too complicated; simplify the interface |
| Must mock everything | Code too coupled; inject dependencies |
| Test setup is huge | Extract helpers; if still complex, the design needs work |

## Verification Checklist

Before declaring the work complete:

- [ ] Every new behavior has a test
- [ ] Watched each test fail before implementing, for the expected reason
- [ ] Minimal code written per test, no speculative features
- [ ] Full suite passes with pristine output
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] Tests assert through public interfaces on observable outcomes
- [ ] No tests skipped or disabled

Cannot check every box? TDD was skipped somewhere; the unchecked box names where to restart.

## Example: Bug Fix

Bug report: empty email accepted by the signup form.

```typescript
// RED: reproduction test
test('rejects empty email', async () => {
  const result = await submitForm({ email: '' });
  expect(result.error).toBe('Email required');
});
```

```bash
$ npm test signup.test.ts
FAIL: expected 'Email required', received undefined   # bug confirmed
```

```typescript
// GREEN: minimal fix
function submitForm(data: FormData) {
  if (!data.email?.trim()) {
    return { error: 'Email required' };
  }
  // ...
}
```

```bash
$ npm test signup.test.ts
PASS                                                   # fix proven
$ npm test
PASS (all)                                             # no regressions
```

REFACTOR: extract field validation only if duplication actually exists, with tests staying green.

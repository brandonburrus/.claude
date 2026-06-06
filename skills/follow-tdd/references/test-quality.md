# Test Quality: Doubles, Mocking Gates, and Anti-Patterns

Read this when writing or changing tests, adding any mock or test double, or creating test utilities.

## Contents

- Test double preference order
- Mock only at system boundaries
- Gate function: before adding any mock
- Anti-pattern catalogue
- DAMP over DRY
- The test pyramid
- When mocks become too complex

## Test double preference order

```text
1. Real implementation   Highest confidence, catches real bugs
2. Fake                  In-memory version of the dependency (e.g., in-memory repo)
3. Stub                  Returns canned data, no behavior
4. Mock (interaction)    Verifies method calls; use sparingly
```

The more real code a test exercises, the more it proves. Reach down this list only when the real thing is too slow, non-deterministic, or has uncontrollable side effects.

## Mock only at system boundaries

Mock these:
- External APIs (payments, email, third-party services)
- Time and randomness
- The file system, sometimes
- Databases, preferring a test DB or in-memory fake over a mock

Never mock these:
- Your own classes or modules
- Internal collaborators
- Anything you control; if it is hard to use real, the design is too coupled (inject dependencies)

## Gate function: before adding any mock

Stop and answer, in order:

1. What side effects does the real method have?
2. Does this test depend on any of those side effects?
3. Do I fully understand what this test needs to happen?

If the test depends on a side effect, mock at a lower level (the actually slow or external operation), never the high-level method the test depends on. If unsure what the test depends on, run it against the real implementation first, observe what actually needs to happen, then add minimal mocking at the right level.

Red flags: "I'll mock this to be safe", "this might be slow, better mock it", mocking before understanding the dependency chain.

## Anti-pattern catalogue

### Testing mock behavior

```typescript
// BAD: verifies the mock exists, not that the component works
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByTestId('sidebar-mock')).toBeInTheDocument();
});

// GOOD: test the real component, or do not assert on the mock at all
test('renders sidebar', () => {
  render(<Page />);
  expect(screen.getByRole('navigation')).toBeInTheDocument();
});
```

Before asserting on any mocked element, ask: am I testing real behavior or mock existence? If the latter, delete the assertion or unmock the component. A test that fails when you remove the mock was testing the mock.

### Test-only methods in production classes

A method only called from test files does not belong on the production class; it pollutes the API and is dangerous if production code ever calls it. Move cleanup and inspection helpers to test utilities. Before adding any method, ask: is this only used by tests, and does this class even own this resource's lifecycle?

### Incomplete mocks

Mock the complete data structure as it exists in reality, not just the fields your immediate test reads. Partial mocks hide structural assumptions; downstream code that reads an omitted field fails silently, and the test passes while integration breaks. If you cannot enumerate the real response's fields, you do not understand it well enough to mock it; check the docs or a real response first.

### Interaction assertions

```typescript
// BAD: breaks on refactor even when behavior is unchanged
expect(db.query).toHaveBeenCalledWith(expect.stringContaining('ORDER BY created_at DESC'));

// GOOD: asserts the observable outcome
expect(tasks[0].createdAt.getTime()).toBeGreaterThan(tasks[1].createdAt.getTime());
```

### Other recurring failures

| Anti-pattern | Problem | Fix |
|---|---|---|
| Testing implementation details | Refactors break tests with unchanged behavior | Assert inputs and outputs only |
| Flaky tests (timing, ordering) | Erode trust until failures get ignored | Deterministic assertions, isolated state |
| No test isolation | Pass alone, fail together | Each test sets up and tears down its own state |
| Snapshot abuse | Giant snapshots nobody reviews break on any change | Small targeted snapshots, review every diff |
| Testing framework code | Verifies the library, not your code | Only test your own behavior |
| Tests as afterthought | "Implementation complete, ready for testing" | Testing is part of implementation; TDD makes this structural |

## DAMP over DRY

In production code, DRY wins. In tests, Descriptive And Meaningful Phrases win: each test should read as a complete specification without tracing through shared helpers. Duplicating an input literal across three tests is fine when it makes each test independently understandable; a shared `makeValidInput()` that hides what is being varied is not.

## The test pyramid

```text
        E2E (~5%)            full user flows, minutes, critical paths only
     Integration (~15%)      component interactions, API boundaries, seconds
   Unit tests (~80%)         pure logic, single process, no I/O, milliseconds
```

Decision guide: pure logic with no side effects gets a unit test; anything crossing a boundary (API, DB, filesystem) gets an integration test; only critical user flows earn E2E tests. The majority of the suite stays small and fast, because slow suites stop getting run, and a suite that does not run catches nothing.

## When mocks become too complex

Warning signs: mock setup longer than the test logic, mocking everything to make the test pass, mocks missing methods the real component has, tests breaking when only the mock changes. At that point an integration test against real components is usually simpler and proves more. Ask: do we need a mock here at all?

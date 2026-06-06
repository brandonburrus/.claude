Apply these practices whenever planning, writing, or reviewing Vitest tests.

## Contents

- Project Discovery
- vi.mock Hoisting and Module Mocking
- Spies and Type-Safe Mocks
- Mock Cleanup
- Fake Timers and Dates
- Test Isolation
- Async Assertions
- What to Mock vs Keep Real
- Coverage and Configuration

## Project Discovery

| Practice | Detail |
|---|---|
| Read `vitest.config.ts` (or the `test` block in `vite.config.ts`) before writing anything | It declares pool, environment, globals, `setupFiles`, and mock-cleanup defaults, so you avoid duplicating or contradicting config-level behavior. |
| Check `package.json` for the Vitest version and plugins | API surface differs across major versions (for example v8 coverage parity arrived in 3.2), and installed plugins like `@testing-library/*` change available matchers. |
| Open an existing test in the same domain before introducing a new pattern | Matching the established style keeps the suite consistent and avoids re-litigating decisions the project already made. |
| Read referenced `setupFiles` | They define global mocks and custom matchers that are active in every test, so assertions may already depend on them. |

## vi.mock Hoisting and Module Mocking

`vi.mock` calls are hoisted above all imports, so they must sit at file scope and cannot close over variables declared later in the file.

| Practice | Detail |
|---|---|
| Declare every `vi.mock` at top level, never inside a test or hook | Hoisting moves the call to the top of the module regardless of where you wrote it, so placing it elsewhere creates confusing ordering bugs. |
| Reference outer variables inside a factory only through `vi.hoisted` | The factory runs before normal module-body assignments, so a plain outer `const` is still `undefined` when the factory executes. |
| Use partial mocks via `importOriginal` when you need most real exports | Replacing a whole module forces you to stub every export, which silently drops behavior the code under test still depends on. |

```ts
const { mockFetch } = vi.hoisted(() => ({ mockFetch: vi.fn() }))
vi.mock('./api.js', () => ({ fetchUser: mockFetch }))

vi.mock(import('./utils.js'), async (importOriginal) => ({
  ...(await importOriginal()),
  formatDate: vi.fn(() => '2024-01-01'),
}))
```

## Spies and Type-Safe Mocks

| Practice | Detail |
|---|---|
| Use `vi.spyOn` when you want to observe calls but keep the real implementation | A full mock replaces behavior, so you lose the side effects you may actually be asserting against. |
| Wrap mocked references in `vi.mocked()` rather than casting with `as` | `vi.mocked()` preserves the real type, so a signature change breaks the test at compile time instead of failing silently at runtime. |
| Never use `any` or type assertions to reach mock methods | Casts hide drift between the mock and the production signature, which is exactly the bug a test should catch. |

```ts
vi.mock('./api.js')
vi.mocked(fetchUser).mockResolvedValue({ id: 1, name: 'Test' })
```

## Mock Cleanup

Stale mock state leaking between tests is the most common cause of order-dependent failures, so resetting is mandatory, not optional.

| Practice | Detail |
|---|---|
| Prefer config-level `mockReset: true` (or `restoreMocks: true`) over per-file hooks | Centralizing cleanup guarantees every test starts clean, so no single file can forget and pollute the next test. |
| Use `vi.restoreAllMocks()` in `afterEach` when relying on `vi.spyOn` | Only restore returns the original implementation; reset and clear leave the spy in place, so an unrestored spy keeps intercepting later tests. |
| Know the three cleanup verbs precisely | `mockReset` wipes implementation and history (returns `undefined`), `mockRestore` reinstates the original (spies only), and `mockClear` drops only call history, so picking the wrong one leaves residual behavior. |

## Fake Timers and Dates

| Practice | Detail |
|---|---|
| Pair `vi.useFakeTimers()` with `vi.useRealTimers()` in `afterEach` | Fake timers are global, so leaving them installed breaks every later test that relies on real `setTimeout` or `Date`. |
| Drive time explicitly with `vi.advanceTimersByTime` instead of real waits | Real `sleep` or `setTimeout` in tests makes them slow and flaky, while advancing fake time is deterministic and instant. |
| Use `vi.setSystemTime` for date-dependent assertions | Pinning the clock removes nondeterminism from anything that reads `new Date()`, which would otherwise produce values that differ on every run. |

```ts
beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())
vi.setSystemTime(new Date('2024-06-15T12:00:00Z'))
```

## Test Isolation

| Practice | Detail |
|---|---|
| Make each test independently runnable; never rely on execution order | Vitest can run tests in parallel or filter to a subset, so any hidden ordering dependency fails unpredictably. |
| Reset stateful modules with `vi.resetModules()` plus dynamic `import()` in `beforeEach` | Modules that retain state across imports (Commander commands, singletons) bleed configuration between tests unless re-imported fresh. |
| Keep `pool` isolation enabled unless you have verified clean teardown | Vitest isolates each file in its own worker by default; disabling it shares module state across files, so latent cleanup gaps become real failures. |
| Use `beforeAll` only for expensive read-only setup, `beforeEach` for mutable state | Mutable state created once in `beforeAll` is shared, so one test mutating it corrupts the others. |

```ts
beforeEach(async () => {
  vi.resetModules()
  command = (await import('../src/commands/my-command.js')).myCommand
})
```

## Async Assertions

A missing `await` is silent: the test passes while the assertion never runs, which is the highest-value async pitfall to guard against.

| Practice | Detail |
|---|---|
| Always `await` `.resolves` and `.rejects` expectations | Without `await` the returned promise is never settled or checked, so a rejection or wrong value goes undetected and the test passes falsely. |
| Use `await vi.waitFor()` for eventual conditions instead of arbitrary delays | A fixed delay is either too short (flaky) or too long (slow); `waitFor` polls until the condition holds or times out. |
| Assert errors with `await expect(fn()).rejects.toThrow(...)` rather than try/catch | If the function unexpectedly resolves, a try/catch with the assertion inside never runs the assertion, so the test silently passes. |

```ts
await expect(asyncFn()).resolves.toBe(42)
await expect(failingFn()).rejects.toThrow('message')
```

## What to Mock vs Keep Real

| Practice | Detail |
|---|---|
| Mock only external boundaries: network, file system, time, process exit | Mocking internal collaborators couples tests to implementation, so refactors break tests that should still pass. |
| Keep pure logic and in-process collaborators real | Exercising real code is what gives the test its value; over-mocking tests the mocks rather than the behavior. |
| Test observable behavior and public output, not internal state or private methods | Behavior-level assertions survive refactors, while implementation-detail assertions break on changes that preserve correct behavior. |
| Prefer specific matchers (`toHaveLength`, `toHaveProperty`, `toMatchObject`) over `toBeTruthy` on a boolean expression | Specific matchers produce diagnostic failure messages, whereas `expect(x === y).toBe(true)` reports only "expected false to be true". |
| Use snapshots only for small, stable, human-readable output | Snapshots over large or time/ID-bearing objects churn constantly and get blindly re-recorded, so they assert nothing meaningful. |

## Coverage and Configuration

| Practice | Detail |
|---|---|
| Use the `v8` coverage provider | It is the default and as accurate as Istanbul since Vitest 3.2, while being faster, so there is no reason to switch providers. |
| Aim for 80%+ statements and branches, 100% branch coverage on business logic | Branch coverage catches untested conditionals that line coverage hides, where most real bugs live. |
| Do not chase coverage numbers with assertion-free tests | A test that executes code without asserting on it inflates coverage while verifying nothing. |
| Annotate genuinely untestable branches with `/* v8 ignore next -- @preserve */` and a reason | The explanation distinguishes a deliberate gap from a forgotten one, so reviewers do not have to guess. |
| Keep test-specific mocks out of `setupFiles` | Setup files apply to every test, so a mock placed there silently alters unrelated tests that expected the real implementation. |

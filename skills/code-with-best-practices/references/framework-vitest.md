Apply these practices whenever planning, writing, or reviewing Vitest tests. Targets Vitest 4.x (version-specific items are flagged). Generic "test behavior not implementation" and clean-code rules live in CLAUDE.md; this reference is the Vitest-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Project discovery](#project-discovery)
- [vi.mock hoisting and module mocking](#vimock-hoisting-and-module-mocking)
- [Spies and type-safe mocks](#spies-and-type-safe-mocks)
- [Mock cleanup](#mock-cleanup)
- [Fake timers and dates](#fake-timers-and-dates)
- [Isolation and the pool model](#isolation-and-the-pool-model)
- [Concurrency](#concurrency)
- [Async assertions](#async-assertions)
- [Coverage](#coverage)
- [In-source and type testing](#in-source-and-type-testing)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Project discovery

| Practice | Detail |
|---|---|
| Read `vitest.config.ts` (or the `test` block in `vite.config.ts`) before writing anything | It declares pool, environment, globals, `setupFiles`, and mock-cleanup defaults, so you avoid duplicating or contradicting config-level behavior. |
| Check `package.json` for the major version | The API surface shifts across majors: v4 removed `poolOptions`, `coverage.all`, and the third-argument test-options form, and consolidated `maxThreads`/`maxForks` into `maxWorkers`. Do not copy v2/v3 patterns blindly. |
| Open an existing test in the same domain first | Matching the established style keeps the suite consistent and avoids re-litigating decisions the project already made. |
| Read referenced `setupFiles` | They define global mocks and custom matchers active in every test, so assertions may already depend on them; setup runs per worker, not once globally. |

## vi.mock hoisting and module mocking

`vi.mock` is a compiler hint: Vitest statically analyzes the file and hoists the call above all imports, even above the ESM imports themselves.

| Practice | Detail |
|---|---|
| Declare every `vi.mock` at top level, never inside a test or hook | Hoisting moves the call to module top regardless of where you wrote it, so placing it elsewhere creates confusing ordering bugs. (An eslint rule and a runtime warning flag non-top-level calls.) |
| Reference outer variables in a factory only through `vi.hoisted` | The factory runs before normal module-body assignments, so a plain outer `const` is still `undefined` when it executes. `vi.hoisted` returns values usable inside the factory. |
| Import `vi` directly from `vitest` | Hoisting relies on static analysis, so a re-exported or aliased `vi` is not recognized and the mock silently fails to hoist. |
| Use partial mocks via `importOriginal` when you need most real exports | Replacing a whole module forces you to stub every export, silently dropping behavior the code under test still depends on. |
| Reach for `vi.doMock` when you genuinely need per-test mock values | `vi.doMock` is not hoisted and runs in place, so it can close over locals, but it only affects later dynamic `import()`, never the static imports already evaluated. |

```ts
const { mockFetch } = vi.hoisted(() => ({ mockFetch: vi.fn() }))
vi.mock('./api.js', () => ({ fetchUser: mockFetch }))

vi.mock(import('./utils.js'), async (importOriginal) => ({
  ...(await importOriginal()),
  formatDate: vi.fn(() => '2024-01-01'),
}))
```

## Spies and type-safe mocks

| Practice | Detail |
|---|---|
| Use `vi.spyOn` to observe calls while keeping the real implementation | A full mock replaces behavior, so you lose the side effects you may actually be asserting against. Spy on `function`/`class` members, not arrow-function properties. |
| Wrap mocked references in `vi.mocked()` rather than casting with `as` | `vi.mocked()` is a type-only helper that preserves the real signature, so a signature change breaks the test at compile time instead of failing silently. Pass `{ partial: true }` for deep partial returns. |
| Never use `any` or assertions to reach mock methods | Casts hide drift between the mock and the production signature, which is exactly the bug a test should catch. |

```ts
vi.mock('./api.js')
vi.mocked(fetchUser).mockResolvedValue({ id: 1, name: 'Test' })
```

## Mock cleanup

Stale mock state leaking between tests is the most common cause of order-dependent failures, so resetting is mandatory, not optional.

| Practice | Detail |
|---|---|
| Set `clearMocks` (and usually `restoreMocks`) in config rather than per-file hooks | All default to `false`. Centralizing cleanup guarantees every test starts clean, so no single file can forget and pollute the next test. Add `unstubGlobals`/`unstubEnvs` too if you stub. |
| Know the three verbs precisely | `clearAllMocks` drops only call history; `resetAllMocks` also wipes the implementation (calls now return `undefined`); `restoreAllMocks` reinstates the original and only affects `vi.spyOn`-created spies, not automocks (v4). |
| Use `restoreAllMocks` whenever you rely on `vi.spyOn` | Clear and reset leave the spy intercepting, so an unrestored spy keeps shadowing the real method in later tests. |

## Fake timers and dates

| Practice | Detail |
|---|---|
| Pair `vi.useFakeTimers()` with `vi.useRealTimers()` in `afterEach` | Fake timers are global, so leaving them installed breaks every later test that relies on real `setTimeout` or `Date`. |
| Know what is faked by default | `setTimeout`, `setInterval`, their `clear*` pairs, `setImmediate`, and `Date`; `process.nextTick` and `queueMicrotask` are NOT faked unless you pass `{ toFake: [...] }`, and `nextTick` cannot be faked under `pool: 'forks'`. |
| Drive time explicitly with `vi.advanceTimersByTime` / `runAllTimersAsync` | Real `sleep` in tests is slow and flaky; advancing fake time is deterministic and instant. |
| Use `vi.setSystemTime` for date-dependent assertions | Pins the clock so anything reading `new Date()` is reproducible; it works with or without fake timers and does not fire pending timers. |

```ts
beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())
vi.setSystemTime(new Date('2024-06-15T12:00:00Z'))
```

## Isolation and the pool model

| Practice | Detail |
|---|---|
| Know the default is `pool: 'forks'`, not threads | v4 forks each test file into its own `child_process` for isolation; it is more compatible than threads (no segfaults with Prisma, bcrypt, native addons) at a small speed cost. Switch to `threads` only when you have verified compatibility. |
| Treat `isolate: false` as a sharp tool | Disabling isolation reuses the worker across files for speed but shares module-level and global state, so latent cleanup gaps become real cross-file failures. Keep isolation on unless teardown is provably clean. |
| Avoid `vmThreads`/`vmForks` for ESM-heavy code | The VM context is faster but unstable on ESM; reserve it for cases where you have measured the win. |
| Reset stateful modules with `vi.resetModules()` plus dynamic `import()` in `beforeEach` | Singletons and Commander-style command objects retain state across imports and bleed config between tests unless re-imported fresh. `resetModules` clears the module cache but not the mock registry. |
| Never share mutable state across tests | Use `beforeAll` only for expensive read-only setup; create mutable fixtures in `beforeEach` so one test mutating them cannot corrupt the others. |

```ts
beforeEach(async () => {
  vi.resetModules()
  command = (await import('../src/commands/my-command.js')).myCommand
})
```

## Concurrency

| Practice | Detail |
|---|---|
| In `test.concurrent`, use the `expect` from the test context, not the global | Concurrent tests share one worker, so the global `expect` cannot tell which test an assertion belongs to; destructure `async ({ expect }) => ...` so snapshots and assertions attribute correctly. |
| Do not let concurrent tests touch shared mutable state, modules, or fake timers | They interleave in the same context, so a global mock or system-time change set by one races the others. Keep concurrent tests fully independent and side-effect-free. |

## Async assertions

A missing `await` is silent: the test passes while the assertion never runs, which is the highest-value async pitfall to guard against.

| Practice | Detail |
|---|---|
| Always `await` `.resolves` and `.rejects` | Without `await` the promise is never settled or checked, so a rejection or wrong value goes undetected and the test passes falsely. The `valid-expect`/`no-floating-promises` lint rules catch this. |
| Use `expect.poll(fn).toBe(...)` to retry a value-producing assertion inline | It reruns the callback until it passes or times out. It cannot use snapshot matchers or `toThrow` (the value is always resolved first), so reach for `vi.waitFor` when the condition is flaky or you need the value before asserting. |
| Assert errors with `await expect(fn()).rejects.toThrow(...)`, not try/catch | If the function unexpectedly resolves, a try/catch with the assertion inside never runs the assertion, so the test silently passes. |

```ts
await expect(asyncFn()).resolves.toBe(42)
await expect.poll(() => store.getItems()).toHaveLength(3)
```

## Coverage

| Practice | Detail |
|---|---|
| Use the `v8` provider | Since 3.2 V8 uses AST-aware remapping, so it matches Istanbul accuracy while staying faster; it is the default and the experimental flag is gone. |
| Set `coverage.include` explicitly | v4 removed `coverage.all` and now requires `include` to declare which files are analyzed; without it, untested files never appear in the report and the percentage lies. |
| Aim for 100% branch coverage on business logic, 80%+ elsewhere | Branch coverage catches untested conditionals that line coverage hides, where most real bugs live; do not chase the number with assertion-free tests that execute code without verifying it. |
| Annotate genuinely untestable branches with `/* v8 ignore next -- @preserve */` and a reason | The `@preserve` keeps the comment through minification and the reason distinguishes a deliberate gap from a forgotten one. |

## In-source and type testing

| Practice | Detail |
|---|---|
| Use in-source tests (`if (import.meta.vitest)`) sparingly, for tiny pure units | They co-locate a quick check with the code but need `includeSource` config and a build-time `define` to dead-code-eliminate them from production; default to a separate test file. |
| Test types with `expectTypeOf` and the `--typecheck` flag | `expectTypeOf` does nothing at runtime; without `--typecheck` the type assertions never run. Use `toEqualTypeOf` for exact equality, `toMatchObjectType` for partial object shape. |
| Keep snapshots small, stable, and human-readable | Snapshots over large or time/ID-bearing output churn constantly and get blindly re-recorded, so they assert nothing meaningful; prefer explicit matchers (`toMatchObject`, `toHaveLength`). |

## Gotchas

- `vi.mock` in a setup file does not work: modules are already cached by the time it runs.
- A `vi.mock` factory referencing an outer `const` gets `undefined`, because the factory runs before that assignment; route through `vi.hoisted`.
- `vi.restoreAllMocks` does not touch automocked module exports (v4), so an automock you expected to revert keeps its mock.
- `vi.resetModules()` clears the module cache but not the mock registry; use `vi.unmock` to drop a mock.
- `process.nextTick` cannot be faked under `pool: 'forks'` (the v4 default), so timer tests depending on it need `pool: 'threads'`.
- `expect.poll` silently never fails with snapshot matchers and rejects `toThrow`; the condition is always resolved before the matcher sees it.
- The default pool is `forks`, not `threads`: process-level isolation, no shared globals across files unless `isolate: false`.

## Sources

- [Vitest config reference](https://vitest.dev/config/), [vi API](https://vitest.dev/api/vi.html), and [expect API](https://vitest.dev/api/expect.html) - official docs; authoritative on mock cleanup defaults, hoisting, fake-timer scope, and `expect.poll`.
- [Vitest migration guide](https://vitest.dev/guide/migration.html) - official; the v4 breaking changes (pool rewrite, `maxWorkers`, removed `coverage.all`, automock restore behavior).
- [Vitest pool config](https://vitest.dev/config/pool) and [Improving Performance](https://vitest.dev/guide/improving-performance) - official; the forks/threads/vm pool model, isolation trade-offs, and native-addon segfault guidance.
- [Vitest 3.2 blog](https://vitest.dev/blog/vitest-3-2.html) and [Coverage guide](https://vitest.dev/guide/coverage) - official; V8 AST-aware remapping reaching Istanbul-level accuracy.
- [Test API](https://vitest.dev/api/test) and [Parallelism guide](https://vitest.dev/guide/parallelism) - official; `test.concurrent` local-context `expect` requirement and concurrency caveats.
- [In-source testing](https://vitest.dev/guide/in-source) and [expectTypeOf](https://vitest.dev/api/expect-typeof) - official; in-source config requirements and type-testing matchers needing `--typecheck`.

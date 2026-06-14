Apply these practices whenever planning, writing, or reviewing Playwright Test (`@playwright/test`) end-to-end tests. Targets current Playwright (version-specific items are flagged). Generic clean-code, naming, and testing-discipline rules live in CLAUDE.md; this reference is the Playwright-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions and `playwright.config.ts` win.

## Contents

- [Project discovery](#project-discovery)
- [Locators](#locators)
- [Web-first assertions](#web-first-assertions)
- [Waiting and synchronization](#waiting-and-synchronization)
- [Test isolation](#test-isolation)
- [Fixtures](#fixtures)
- [Projects, auth, and storage state](#projects-auth-and-storage-state)
- [Network and API](#network-and-api)
- [Config, parallelism, and diagnostics](#config-parallelism-and-diagnostics)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Project discovery

| Practice | Detail |
|---|---|
| Read `playwright.config.ts` first | It defines `baseURL`, `projects`, timeouts, `retries`, `use`, and `testIdAttribute`. Match its assumptions instead of restating URLs or inventing a test-id scheme. |
| Reuse existing fixtures and POMs | A project with a custom `test` export or a Page Object layer expects new specs to extend them; bypassing that layer creates inconsistent, harder-to-maintain tests. |
| Extend an existing spec when one exists | Adding to the feature's spec keeps related tests grouped and avoids re-establishing setup the file already provides. |
| Generate a first draft with codegen | `npx playwright codegen <url>` emits resilient role/text locators you then refine, faster and less brittle than hand-writing CSS by eye. |

## Locators

| Practice | Detail |
|---|---|
| Follow the user-facing priority order | `getByRole` (with accessible name) then `getByLabel` then `getByPlaceholder` then `getByText` then `getByAltText`/`getByTitle` then `getByTestId`, and only then `page.locator()`. Each step down is more tied to implementation than to what a user perceives. |
| `getByRole` removes the most flake | Role + accessible name mirrors assistive tech and survives CSS/DOM refactors that shatter selectors; reach for it before anything else. |
| Reserve CSS/XPath for genuine last resort | Classes, `nth-child` paths, and framework-generated ids change with markup and styling and are the top source of brittle tests. |
| `getByTestId` only when role and text are ambiguous | A `data-testid` is an explicit, stable contract for elements nothing user-facing uniquely identifies, but it is not a substitute for accessible markup. Configure `testIdAttribute` if the app uses a non-default attribute. |
| Narrow with `.filter()` and chaining, not deep selectors | `.filter({ hasText })`, `.filter({ has })`, `.filter({ hasNot })`, and chaining (`row.getByRole('button')`) express intent and stay resilient where one deep selector is fragile. |
| Resolve ambiguity with filtering before `.nth()` | Locators are strict: an action on a locator matching more than one element throws. Prefer filtering to a unique match over `.first()`/`.nth()`, which silently picks a positional element. |
| Combine with `.and()` / `.or()` | `.or()` handles branching UI (a dialog that may or may not appear) deterministically; `.and()` requires both conditions. Both beat guessing with timeouts. |
| Flag missing stable locators upstream | When no role, label, or text uniquely identifies an element, propose adding a `data-testid` to the component rather than encoding a CSS path. |

```ts
await page.getByRole('button', { name: 'Submit' }).click();
await page
  .getByRole('listitem')
  .filter({ hasText: 'Product 2' })
  .getByRole('button', { name: 'Add to cart' })
  .click();
```

## Web-first assertions

| Practice | Detail |
|---|---|
| Use `await expect(locator)` matchers | They auto-retry until the condition holds or the assertion times out, eliminating the race conditions a one-shot check introduces. The single highest-leverage anti-flake habit. |
| Never wrap a sync getter in `expect` | `expect(await locator.isVisible()).toBe(true)` samples state once with no retry and flakes the instant the UI is mid-render. Use `await expect(locator).toBeVisible()`. |
| Assert specific semantic state | `toBeVisible`, `toBeEnabled`, `toBeChecked`, `toHaveText`, `toHaveValue`, `toHaveURL`, `toHaveCount` each wait for that exact condition and fail with a precise diff, not a blind timeout. |
| Prefer `toHaveCount` over reading `.count()` | `await expect(list).toHaveCount(3)` retries; `expect(await list.count()).toBe(3)` reads once before the list finishes rendering and flakes. Same logic for `toHaveText` over `textContent()`. |
| Use `expect.soft` to collect failures | Soft assertions let one test report every mismatched field at once instead of stopping at the first, speeding diagnosis of state-display bugs. |
| Group actions with `test.step` | Wrapping phases in `await test.step('...', ...)` produces a readable trace and report tree, making failures self-locating in long flows. |

## Waiting and synchronization

| Practice | Detail |
|---|---|
| Never use `page.waitForTimeout()` in committed code | A fixed sleep is both flaky (too short on a slow run) and slow (wasted time on a fast one); it never checks readiness. Wait for the actual condition. |
| Rely on built-in actionability | Playwright auto-waits for elements to be visible, stable, enabled, and receive events before `click`/`fill`, so manual pre-action waits are redundant. |
| Avoid `waitForLoadState('networkidle')` | It is discouraged and unreliable: polling, analytics, or websockets keep it from ever firing, and a slow lone request fires it too early. Wait for a visible element or a specific response instead. |
| Synchronize on the concrete event | `waitForURL` after navigation, `waitForResponse`/`waitForRequest` for network, or an `expect` on resulting UI: each is deterministic, unlike a vague lifecycle proxy. |
| Override `timeout` only for known-slow ops | `{ timeout: 30_000 }` on a specific slow assertion documents the expectation locally without inflating the global timeout and masking other flake. |

## Test isolation

| Practice | Detail |
|---|---|
| Treat every test as independent | Each test gets a fresh `BrowserContext` (clean cookies, local/session storage), so any test must pass run alone; depending on order is latent flake. |
| Use `beforeEach`, not `beforeAll`, for shared navigation | `beforeAll` runs once per worker and leaks state across tests; `beforeEach` re-establishes a clean start for each. |
| Do not write manual teardown of browser state | The context is discarded after each test, so clearing cookies/storage is noise. Reserve teardown for external state (DB rows, created records). |
| Do not test sites you do not control | Links to third-party servers are slow, flaky, and out of scope; assert the outgoing link or mock the response with `page.route()` rather than navigating off-app. |

## Fixtures

| Practice | Detail |
|---|---|
| Prefer fixtures over `beforeEach`/`afterEach` | `base.extend()` bundles setup and teardown around one `use()` call, is composable, and runs only for tests that request the fixture, unlike hooks that fire for every test in scope. |
| Put teardown after `await use(value)` | Code after `use()` always runs even when the test fails, guaranteeing cleanup an `afterEach` can miss on certain failures. |
| Scope expensive setup to the worker | `{ scope: 'worker' }` initializes a DB connection or started server once per worker instead of per test; pair with `{ auto: true }` to run without an explicit request. |
| Export `test` and `expect` from the fixtures module | Importing both from the local fixtures file ensures every spec uses the extended `test`; combine modules with `mergeTests`. |

```ts
export const test = base.extend<MyFixtures>({
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await use(todoPage);
    // teardown after use() runs even if the test failed
  },
});
```

## Projects, auth, and storage state

| Practice | Detail |
|---|---|
| Authenticate once via a setup project | A `*.setup.ts` project saves `storageState` to a file; browser projects list it under `dependencies` and reuse it via the `storageState` use-option, so no test pays a UI login. |
| Prefer API login in setup | `request.post('/api/login', ...)` then `request.storageState({ path })` is far faster and less brittle than driving the login form. |
| Use the `projects` model for browser matrix | Each project pins a device/browser via `use: { ...devices['Desktop Chrome'] }`; projects also express the setup-then-test dependency graph. |
| Separate state files per role | Distinct `admin.json`/`user.json` keep role runs isolated; apply with `test.use({ storageState })` per spec or describe block. |
| Authenticate per worker for state-mutating suites | Override the `storageState` fixture keyed on `testInfo.parallelIndex` to give each worker its own account, avoiding cross-test interference on shared server state. |
| Reset state for logged-out coverage | `test.use({ storageState: { cookies: [], origins: [] } })` exercises the unauthenticated path the shared state would otherwise hide. |
| Gitignore `playwright/.auth` and inject creds from env | State files hold live session cookies that leak credentials and expire; never commit them, and read credentials from env vars, not source. |

```ts
setup('authenticate', async ({ request }) => {
  await request.post('/api/login', { form: { user, password } });
  await request.storageState({ path: authFile });
});
```

## Network and API

| Practice | Detail |
|---|---|
| Register `page.route()` before the navigation that triggers it | A route added after `page.goto()` misses in-flight requests; intercept first. |
| Mock for speed and determinism, keep a few real-server paths | Fulfilling locally removes backend dependencies, but over-mocking hides contract drift; verify critical happy paths against the real API. |
| Test the API directly with the `request` fixture | `request.post`/`get` exercise endpoints with no browser, ideal for setup, teardown, and pure API assertions; `APIResponse` carries status and body. |
| Spy with `waitForRequest` to assert payloads | Capturing the outgoing request confirms the UI sends the method and body the API expects. |

```ts
await page.route('**/api/users', (route) =>
  route.fulfill({ json: [{ id: 1, name: 'Alice' }] }),
);
```

## Config, parallelism, and diagnostics

| Practice | Detail |
|---|---|
| Set `baseURL` and let Playwright run the app | `baseURL` enables relative `page.goto('/login')`; a `webServer` block starts and health-checks the app, removing the race of testing before it is ready. |
| Enable `fullyParallel: true` | Runs all tests across all files in parallel, viable precisely because each test is isolated; tune throughput with `workers`. |
| Use `test.describe.configure({ mode })` sparingly | `'parallel'` parallelizes within one file; `'serial'` chains dependent tests (a failure skips and retries the rest) and is a smell, not a default. |
| Shard across CI machines with `--shard=i/n` | Splits the suite for distributed runs; merge the blob reports afterward for one report. |
| Retry in CI, not locally | `retries: process.env.CI ? 2 : 0` absorbs transient CI flake while surfacing real local failures immediately. |
| Capture diagnostics only on retry | `trace: 'on-first-retry'` and `video: 'retain-on-failure'` give full failure forensics in the trace viewer without the cost of recording every passing test. |
| Set `forbidOnly: !!process.env.CI` | Fails the build on a committed `.only`, preventing one focused test from silently skipping the suite. |

## Gotchas

- `expect(await locator.count()).toBe(n)` and `.isVisible()`/`.textContent()` in an `expect` read state once with no retry; use `toHaveCount`/`toBeVisible`/`toHaveText`.
- `page.waitForTimeout()` and `waitForLoadState('networkidle')` are the two top flake sources; neither belongs in committed tests.
- Locators are strict: an action throws if more than one element matches. Filter to a unique match rather than reaching for `.first()`.
- A route registered after `page.goto()` silently misses the requests it was meant to mock.
- `beforeAll` leaks state across tests in a worker; default to `beforeEach` or a fixture.
- Committed `storageState` auth files leak live session cookies and rot as sessions expire; gitignore `playwright/.auth`.
- `getByText` matches substring and is case-insensitive by default; pass `{ exact: true }` when you need an exact, case-sensitive match.

## Sources

- [Playwright best practices](https://playwright.dev/docs/best-practices), [Locators](https://playwright.dev/docs/locators), [Auto-waiting](https://playwright.dev/docs/actionability), [Assertions](https://playwright.dev/docs/test-assertions) - official docs; authoritative on locator priority, web-first assertions, and the anti-patterns to avoid.
- [Playwright fixtures](https://playwright.dev/docs/test-fixtures) and [authentication](https://playwright.dev/docs/auth) - official; `test.extend`, scopes, teardown-after-`use`, setup projects, and `storageState` reuse.
- [Playwright parallelism](https://playwright.dev/docs/test-parallel) and [API testing](https://playwright.dev/docs/api-testing) - official; `fullyParallel`, sharding, worker isolation, and the `request` fixture.
- [17 Playwright Testing Mistakes You Should Avoid](https://elaichenkov.github.io/posts/17-playwright-testing-mistakes-you-should-avoid/) (Yevhen Laichenkov) - recognized Playwright contributor; concrete flake anti-patterns with code.
- [Playwright Waits: Auto-Waiting and Best Practices](https://www.browserstack.com/guide/playwright-wait-types) (BrowserStack) - established testing vendor; why hard waits and networkidle flake.
- [Avoiding Flaky Tests in Playwright](https://betterstack.com/community/guides/testing/avoid-flaky-playwright-tests/) (Better Stack) and [Dealing with waits and timeouts](https://www.checklyhq.com/docs/learn/playwright/waits-and-timeouts/) (Checkly) - well-regarded engineering guides; synchronization and isolation in practice.

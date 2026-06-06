Apply these practices whenever planning, writing, or reviewing Playwright tests.

## Contents

- Project Discovery
- Locators
- Assertions
- Waiting and Synchronization
- Authentication and Storage State
- Test Isolation
- Fixtures
- Network Mocking
- Page Object Model
- Configuration and Flake Prevention

## Project Discovery

| Practice | Detail |
|----------|--------|
| Read `playwright.config.ts` first | It defines baseURL, projects, timeouts, retries, and `testIdAttribute`, so your tests must match its assumptions rather than restate URLs or invent a test-id scheme. |
| Check for existing fixtures and POMs | A project with custom fixtures or a Page Object layer expects new tests to extend them; bypassing that layer creates inconsistent, harder-to-maintain tests. |
| Extend an existing spec when one exists | Adding to the feature's existing spec keeps related tests grouped and avoids duplicating setup that the file already establishes. |

## Locators

| Practice | Detail |
|----------|--------|
| Prefer `getByRole` with an accessible name | Role locators mirror how users and assistive tech find elements, so they survive CSS and DOM refactors that would break selectors. |
| Use this priority order | `getByRole` then `getByLabel` then `getByPlaceholder` then `getByText` then `getByTestId` then `getByAltText`/`getByTitle`; each step down is less tied to user-facing semantics and more to implementation. |
| Reserve `page.locator()` CSS/XPath for last resort | CSS classes, `nth-child` paths, and framework-generated IDs change with markup and styling, making these the top source of brittle tests. |
| Reach for `getByTestId` only when role and text are ambiguous | A `data-testid` is an explicit, stable contract, useful when nothing user-facing uniquely identifies the element, but it is not a substitute for accessible markup. |
| Narrow with `.filter()` and chaining instead of complex selectors | Filtering a list item by text then locating within it expresses intent clearly and stays resilient where a single deep selector would be fragile. |
| Use `.or()` for conditional UI | Branching UI (a dialog that may or may not appear) is handled deterministically by matching either locator rather than guessing with timeouts. |
| Flag missing stable locators | When no role, label, or text uniquely identifies an element, propose adding a `data-testid` to the component rather than falling back to a CSS path. |

```ts
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByLabel('Email address').fill('user@example.com');
await page
  .getByRole('listitem')
  .filter({ hasText: 'Product 2' })
  .getByRole('button', { name: 'Add to cart' })
  .click();
```

## Assertions

| Practice | Detail |
|----------|--------|
| Use web-first `await expect(locator)` assertions | They auto-wait and retry until the condition holds or times out, eliminating the race conditions that manual checks introduce. |
| Never wrap a sync getter in `expect` | `expect(await locator.isVisible()).toBe(true)` samples state once with no retry, so it flakes the moment the UI is mid-render. |
| Assert on semantic state | `toBeVisible`, `toBeEnabled`, `toBeChecked`, `toHaveText`, `toHaveValue`, `toHaveCount`, `toHaveURL` each wait for that specific condition, giving precise failures instead of timeouts on a blind wait. |
| Use `expect.soft` to collect multiple failures | Soft assertions let one test report every mismatched field at once instead of stopping at the first, which speeds diagnosis of state-display bugs. |

```ts
await expect(page.getByText('Welcome')).toBeVisible();
await expect(page.getByTestId('count')).toHaveText('42');
await expect(page).toHaveURL(/.*dashboard/);
```

## Waiting and Synchronization

| Practice | Detail |
|----------|--------|
| Never use `page.waitForTimeout()` | A hard sleep is both flaky (too short on a slow run) and slow (wasted time on a fast run); wait for the actual condition instead. |
| Rely on built-in actionability waiting | Playwright already waits for elements to be visible, enabled, and stable before clicks and fills, so manual pre-action waits are redundant. |
| Avoid `waitForLoadState('networkidle')` | Networkidle is unreliable on apps with polling, analytics, or websockets and is effectively deprecated; wait for a visible element or a specific response. |
| Use `waitForURL` after navigation and `waitForResponse` for network events | Synchronizing on the concrete event you depend on is deterministic, unlike waiting on a vague lifecycle proxy. |
| Override timeout only for genuinely slow operations | Passing `{ timeout: 30_000 }` on a known-slow assertion documents the expectation locally without inflating the global timeout and masking other flake. |

## Authentication and Storage State

| Practice | Detail |
|----------|--------|
| Authenticate once via a setup project | A `*.setup.ts` project saves `storageState` to a file that all browser projects reuse via `dependencies`, so tests do not pay a UI login cost each run. |
| Prefer API-based login for the setup | Posting to the login endpoint and calling `request.storageState()` is far faster and less brittle than driving the login form. |
| Gitignore the `.auth` directory | Stored state contains live session cookies and tokens; committing it leaks credentials and rots as sessions expire. |
| Use separate state files per role | Distinct `admin.json` and `user.json` files keep role-specific runs isolated and let one suite exercise multiple permission levels. |
| Reset state for unauthenticated tests | `test.use({ storageState: { cookies: [], origins: [] } })` gives logged-out coverage that the shared authenticated state would otherwise hide. |
| Inject credentials from the environment | Hardcoded credentials leak in source and break across environments; read them from env vars or `.env`. |

```ts
setup('authenticate', async ({ request }) => {
  await request.post('/api/login', { form: { user: 'user', password: 'pw' } });
  await request.storageState({ path: authFile });
});
```

## Test Isolation

| Practice | Detail |
|----------|--------|
| Treat each test as independent | Every test gets a fresh BrowserContext with clean cookies and storage, so any test must pass when run alone; depending on execution order is a latent flake. |
| Use `beforeEach`, not `beforeAll`, for shared navigation | `beforeAll` runs once per worker and leaks state across tests, while `beforeEach` re-establishes a clean starting point for each. |
| Do not write manual cleanup | Playwright discards the context after each test, so teardown of cookies and storage is unnecessary and only adds noise. |

## Fixtures

| Practice | Detail |
|----------|--------|
| Prefer fixtures over `beforeEach`/`afterEach` | Fixtures bundle setup and teardown around a single `use()` call, are composable, and run only for tests that request them, unlike hooks that fire for every test in scope. |
| Put teardown after `use()` | Code after `await use(value)` always runs even when the test fails, guaranteeing cleanup that an `afterEach` can miss on certain failures. |
| Scope expensive setup to `worker` | Worker-scoped fixtures (a DB connection, a started server) initialize once per worker instead of per test, cutting redundant cost for shared resources. |
| Export `test` and `expect` from a fixtures module | Importing both from your local fixtures file ensures every spec uses the extended `test` and stays consistent across the suite. |

```ts
export const test = base.extend<MyFixtures>({
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await use(todoPage);
  },
});
```

## Network Mocking

| Practice | Detail |
|----------|--------|
| Mock with `page.route()` for speed and determinism | Fulfilling responses locally removes server and data dependencies, making most tests fast and stable regardless of backend state. |
| Keep a few real-server tests for critical paths | Over-mocking hides API contract drift, so verify key happy paths against the real backend to catch schema changes mocks would mask. |
| Spy on requests with `waitForRequest` | Capturing the outgoing request lets you assert method and payload, confirming the UI sends what the API expects. |
| Set up routes before the navigation that triggers them | A route registered after `page.goto()` misses requests already in flight, so define interception first. |

```ts
await page.route('**/api/users', (route) =>
  route.fulfill({ status: 200, json: [{ id: 1, name: 'Alice' }] }),
);
```

## Page Object Model

| Practice | Detail |
|----------|--------|
| Use POMs for large suites | Playwright endorses the Page Object Model; centralizing locators and actions means a UI change updates one class instead of many specs. |
| Define locators as `readonly` in the constructor | Constructing locators once per page object keeps them consistent and self-documenting, and `readonly` prevents accidental reassignment. |
| Expose user-facing actions, not raw steps | Methods like `login(email, password)` express intent and hide implementation, so tests read as behavior rather than clicks and fills. |
| Keep `test`/`describe`/hooks out of POM classes | A POM models the page, not the test run; mixing in test control flow couples structure to specific tests and breaks reuse. |

## Configuration and Flake Prevention

| Practice | Detail |
|----------|--------|
| Set `baseURL` in config | Centralizing the base URL lets `page.goto('/login')` use relative paths and makes environment switching a one-line change. |
| Use `retries: 2` in CI, `0` locally | CI retries absorb genuinely transient flake, while zero local retries surface real failures immediately instead of hiding them. |
| Set `forbidOnly: !!process.env.CI` | This fails the build if a stray `.only()` is committed, preventing a single focused test from silently skipping the whole suite. |
| Use `trace: 'on-first-retry'` | Capturing a trace only when a test retries gives full failure diagnostics without the cost of tracing every passing test. |
| Configure `webServer` to auto-start the app | Letting Playwright start and health-check the server removes manual setup and the race of testing before the app is ready. |
| Enable `fullyParallel: true` | Running tests in parallel maximizes CPU use, which only works because each test is already isolated. |

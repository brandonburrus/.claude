---
name: validate-api
description: >-
  Use this skill to validate an API change by sending real HTTP requests against
  the running service with the Bruno CLI, asserting status, body, and headers,
  and saving every request into a reusable Bruno collection. Use after
  implementing an API change, or when the user says "validate the API",
  "smoke-test the endpoint", "hit the endpoint and check the response", "verify
  the API works", or "check the API returns the right shape". The collection is
  a byproduct for future replay, and this does not replace automated API tests.
  Do not use for browser or UI validation (use validate-web), for writing the
  vitest/supertest or Playwright suite (use follow-tdd), or for designing the
  API contract (use design-api).
---

## Purpose

Validate an API change by sending real HTTP requests against the running service with the Bruno CLI (`bru`), asserting on status, body, and headers, and saving every request into a Bruno collection so the validation effort becomes a reusable, version-controlled artifact. The collection uses the OpenCollection YAML format (`.yml` files), which the CLI runs directly. This is semi-manual validation: you drive real requests and read real responses, which catches what mocked unit tests miss (it is actually reachable, auth actually works, the real serializer produces the real shape). The collection is the byproduct that makes the next validation cheap. This complements automated testing; it does not replace a vitest/supertest or Playwright API suite.

## Iron rules

- **A running API and a stated expected response are both required.** No base URL means stop. No expected status or shape means you are poking, not validating; define the expected response first.
- **The collection is a deliverable, not scratch.** Every request you send is saved as a `.yml` request file in an OpenCollection so it replays later. Do not fire one-off `curl` commands that vanish. Reuse the project's existing Bruno collection if it has one.
- **This does not replace automated API tests.** Bruno proves the running service behaves now; it does not run in CI on every commit. The two coexist: Bruno for live validation plus a reusable collection, the test suite for automated regression. When a check is worth permanent coverage, graduate it into vitest/supertest or Playwright and say so.
- **Bruno CLI is external.** If `bru` is missing, instruct the user to install it (`npm install -g @usebruno/cli`) or run via `npx @usebruno/cli`. Do not silently global-install.

The collection layout, request YAML, assertion structure, scripting, and CLI flags are in [references/bruno.md](references/bruno.md); read it for exact syntax.

## Workflow

```text
Validate (API):
- [ ] 1. State the expected responses
- [ ] 2. Locate or create the collection and environment
- [ ] 3. Author a request per behavior, with assertions
- [ ] 4. Run with bru and capture results
- [ ] 5. Report pass/fail and where the collection lives
```

### 1. State the expected responses

Per behavior: method and path, expected status, the body fields or shape that must hold, key headers, and the error cases (401 without auth, 400 on bad input, 404 on missing). Pull them from the diff, the spec, or the API contract. An endpoint with no stated expected response cannot be validated.

### 2. Locate or create the collection and environment

Detect an existing collection first: look for an `opencollection.yml` (or a legacy `bruno.json`) in the repo and extend it if present. Otherwise create an OpenCollection (default location `<repo>/bruno/` unless the project has a convention, and say where you put it). The root `opencollection.yml`:

```yaml
version: "1"
name: <api> validation
type: collection
```

Put the base URL in an environment file as a `variables` list (the key is `variables`, not `vars`), never hardcoded per request, so the collection survives a move to staging:

```yaml
variables:
  - name: host
    value: http://localhost:8787
```

Save it as `environments/local.yml` and reference `{{host}}` in every request URL.

### 3. Author a request per behavior, with assertions

One `.yml` file per behavior, with an `info` block, an `http` block, and a `runtime` block. Use `runtime.assertions` for declarative status/body/header checks; use a `runtime.scripts` `type: tests` block for richer logic and for capturing a value (an auth token, a created id) to chain into the next request.

```yaml
info:
  name: Login
  type: http
  seq: 1
http:
  method: POST
  url: "{{host}}/login"
  body:
    type: json
    data: |-
      { "username": "sam", "password": "correct-horse" }
runtime:
  assertions:
    - expression: res.status
      operator: eq
      value: 200
  scripts:
    - type: tests
      code: |-
        bru.setVar("token", res.body.token);
```

A later request then sends `Authorization: Bearer {{token}}`. Validate the error cases too, not just the happy path; that is where real APIs diverge from their mocked tests.

### 4. Run with bru and capture results

- Whole collection: `bru run --env local` (add `-r` to recurse folders).
- Single request: `bru run get-user.yml --env local`.
- Evidence and CI: `--reporter-json results.json` and `--reporter-junit results.xml`. `bru` exits nonzero when an assertion or test fails.

Confirm the run executed every request you authored (the Requests count matches), because a request that fails to parse is excluded from the run rather than failed, which can leave a green summary that validated nothing.

### 5. Report

Per behavior: pass or fail with the assertion that decided it (quoted), and state where the collection was saved or extended (`<path>`) so the next person replays instead of re-deriving. Recommend graduating durable checks into the automated suite.

## Gotchas

- **The collection is the point, not a side effect.** A validation that leaves no replayable artifact wasted the setup; the next change re-pokes from scratch. Save every request.
- **Declarative checks go in `runtime.assertions`, logic in a `tests` script.** A status or field check is a `{ expression, operator, value }` entry under `runtime.assertions`; "the token is a non-empty string that expires in over an hour", and any value capture for chaining, goes in a `runtime.scripts` `type: tests` block with `expect()` and `bru.setVar`.
- **Validate the error cases.** The 401/400/404 paths are where a real API diverges from its mocked unit tests. An auth check that only ever exercised the 200 path has not been validated.
- **Variable, not hardcoded host.** A collection with `localhost` baked into every request does not survive moving to staging. Put the base URL in `environments/<env>.yml` as a `variables` entry and reference `{{host}}`.
- **A request count short of what you wrote means something did not run.** A `.yml` that fails to parse is silently excluded, not failed, so the summary can read green while testing less than you think. Check that Requests equals the number of requests you authored.
- **Not a CI suite.** `bru run` is local validation; it does not replace the supertest/vitest tests that run on every PR. Graduate durable checks and keep Bruno for live validation and exploration.

## Example

Validating that a new `GET /users/:id` returns the right shape and 404s correctly, against `http://localhost:8787`. An `opencollection.yml`, an `environments/local.yml` holding `host`, and two request files in `bruno/`, then:

```bash
bru run --env local --reporter-junit results.xml
# get-user.yml         -> 200, res.body.id eq 42, res.body.email isString   PASS
# get-user-missing.yml -> 404, res.body.error contains "not found"          PASS
```

Report: "Both checks pass against the running service: `GET /users/42` returns the expected shape, `GET /users/999` returns 404 with the error message. Collection saved at `bruno/` (extend it next time). The 404 path is worth a supertest case in the automated suite."

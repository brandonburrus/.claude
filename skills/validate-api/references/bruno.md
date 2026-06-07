## Bruno (OpenCollection YAML) reference

Collection layout, request YAML, assertions, scripts, and CLI for Bruno using the OpenCollection YAML format. Every structure below was verified live against `@usebruno/cli` 3.4.2; the CLI runs OpenCollection `.yml` collections directly. Bruno is a Git-friendly, offline-first API client, and OpenCollection (Bruno 3.0+) is its open, vendor-neutral YAML spec. Plain-text `.yml` files are what make the collection a durable, version-controlled validation artifact.

### Contents

- [Setup](#setup)
- [Collection structure](#collection-structure)
- [Environment files](#environment-files)
- [Request YAML](#request-yaml)
- [Assertions](#assertions)
- [Scripts and variable capture](#scripts-and-variable-capture)
- [CLI](#cli)
- [Recipes by use case](#recipes-by-use-case)

### Setup

| Step | Command |
|---|---|
| Install (global) | `npm install -g @usebruno/cli` |
| Install (no global) | `npx @usebruno/cli run ...` |
| Run a collection | `bru run --env <name>` |

### Collection structure

A collection is a directory the CLI runs against. OpenCollection uses an `opencollection.yml` root and `.yml` files (not `bruno.json` and `.bru`).

```text
bruno/
  opencollection.yml      # collection root
  environments/
    local.yml             # one environment per file
  get-user.yml            # one request per file
  users/                  # folders group requests; run recursively with -r
    create-user.yml
```

`opencollection.yml`:

```yaml
version: "1"
name: orders API validation
type: collection
```

### Environment files

Each environment is `environments/<name>.yml` holding a `variables` list (the key is `variables`, not `vars`). Reference a variable anywhere with `{{name}}`.

```yaml
variables:
  - name: host
    value: http://localhost:8787
```

Select it with `--env local`. Keep the base URL here, never hardcoded per request, so the same collection runs against staging by swapping `--env`. To override or supply a value without a file, `--env-var host=http://localhost:8787` also works.

### Request YAML

A request file has `info` and `http` blocks, plus optional `headers`, `body`, `auth` (under `http`) and a `runtime` block for assertions and scripts.

```yaml
info:
  name: Create user
  type: http
  seq: 1
http:
  method: POST
  url: "{{host}}/users"
  headers:
    - name: Content-type
      value: application/json
    - name: Authorization
      value: Bearer {{token}}
  body:
    type: json
    data: |-
      {
        "name": "Sam",
        "email": "sam@example.com"
      }
  auth: inherit
runtime:
  assertions:
    - expression: res.status
      operator: eq
      value: 201
    - expression: res.body.id
      operator: isNumber
```

A simple GET needs only `info` and `http`:

```yaml
info:
  name: Get user
  type: http
  seq: 1
http:
  method: GET
  url: "{{host}}/users/42"
```

`seq` orders requests within a recursive run; a `01-`/`02-` filename prefix works too.

### Assertions

`runtime.assertions` is a list of `{ expression, operator, value }`. The `expression` reads from the response (`res.status`, `res.body.<path>`, `res.body.items[0].price`, `res.responseTime`); the field name is `expression` (not `expr` or `name`).

```yaml
runtime:
  assertions:
    - expression: res.status
      operator: eq
      value: 200
    - expression: res.body.email
      operator: contains
      value: "@example.com"
    - expression: res.body.roles
      operator: isArray
    - expression: res.responseTime
      operator: lt
      value: 1000
```

Operators (the same abbreviated set Bruno uses; `eq`, not `equals`):

| Category | Operators |
|---|---|
| Comparison | `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `between` |
| String | `contains`, `notContains`, `startsWith`, `endsWith`, `matches`, `notMatches` |
| Presence | `isNull`, `isUndefined`, `isDefined`, `isEmpty` |
| Type | `isNumber`, `isString`, `isBoolean`, `isArray`, `isJson` |
| Truthiness | `isTruthy`, `isFalsy` |
| Membership | `in`, `notIn`, `length` |

### Scripts and variable capture

`runtime.scripts` is a list of `{ type, code }`. Use `type: tests` for richer checks with `test()` and `expect()`, and for capturing values to chain into later requests with `bru.setVar`. The `tests` script runs after the response, and a variable it sets is available as `{{name}}` in later requests of the same run. (In this CLI build the `tests` type is the script that runs; put capture logic there rather than a separate post-response type.)

```yaml
runtime:
  scripts:
    - type: tests
      code: |-
        test("token is a non-empty string", function() {
          expect(res.body.token).to.be.a('string');
          expect(res.body.token.length).to.be.above(0);
        });
        bru.setVar("token", res.body.token);
```

`res` exposes `res.status`, `res.body`, `res.headers`, `res.responseTime`. `bru.setVar` / `bru.getVar` hold run variables; `bru.setEnvVar` writes to the environment.

### CLI

`bru run` executes requests and exits nonzero on any failed assertion or test, so it gates CI directly (verified: pass exits 0, a failed assertion exits 1).

| Goal | Command |
|---|---|
| Run the whole collection | `bru run --env local` |
| Recurse into folders | `bru run -r --env local` |
| Run one request | `bru run get-user.yml --env local` |
| Run a folder | `bru run users --env local` |
| Stop on first failure | `bru run --env local --bail` |
| Only requests with tests/asserts | `bru run --env local --tests-only` |
| Override a variable | `bru run --env local --env-var token=abc123` |
| JSON report | `bru run --env local --reporter-json results.json` |
| JUnit report (CI) | `bru run --env local --reporter-junit results.xml` |
| HTML report | `bru run --env local --reporter-html results.html` |

Reporters combine; pass several in one command to emit all formats.

### Recipes by use case

**Auth, then an authenticated call.** Capture the token in a `tests` script, reuse it as `{{token}}`.

`01-login.yml`:

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

`02-get-me.yml` then sends `Authorization: Bearer {{token}}` and asserts the identity. Run both with `bru run -r --env local`; `seq` (or the `01-`/`02-` prefix) fixes the order.

**CRUD sequence.** One file per step, chaining the created id via a `tests` capture:

```text
# 01-create.yml -> tests: bru.setVar("userId", res.body.id)
# 02-get.yml    -> http.url {{host}}/users/{{userId}}  ; assertion res.status eq 200
# 03-delete.yml -> http.method DELETE, url .../{{userId}} ; assertion res.status eq 204
```

**Error-case assertions.** The paths a mocked unit test usually skips, each a `runtime.assertions` entry:

```text
# unauthorized.yml -> GET {{host}}/users/42 with no token ; res.status eq 401
# bad-input.yml    -> POST {{host}}/users with {}         ; res.status eq 400
# not-found.yml     -> GET {{host}}/users/999999          ; res.status eq 404
```

**CI / evidence run.** Emit a JUnit file and let the exit code gate:

```bash
bru run -r --env local --reporter-junit results.xml
echo "exit $?"   # nonzero if any assertion or test failed
```

---
name: design-cicd
description: >-
  Use this skill when designing or changing a CI/CD pipeline: setting up CI for a
  repo, adding a GitHub Actions (or GitLab CI, CircleCI) workflow, configuring
  quality gates, wiring a build/test/deploy pipeline, adding branch protection or
  required status checks, setting up preview/staging/production deploys, adding a
  rollback workflow, or making a slow pipeline faster. Use when the user says "set
  up CI", "add a workflow", "automate the checks", "gate merges on tests", "deploy
  pipeline", or "CI is too slow". Do not use for release-day prep and the rollback
  plan for one specific release (use prepare-for-deploy), writing the tests
  themselves (use follow-tdd), provisioning cloud resources with IaC (use
  code-with-best-practices with the CDK or Terraform reference), or opening a PR
  (use open-pull-request).
---

## Purpose

Design the pipeline that enforces every other quality practice automatically, on every change, without anyone remembering to run it. The deliverable is the pipeline configuration plus the decisions behind it: which gates run where, what blocks a merge, and how a deploy rolls back. CI is the enforcement layer: a convention that is not gated is a suggestion, and a suggestion decays. The design question is not "what can we check" but "what must pass before this reaches the next stage", because the gate is only as valuable as the merge it blocks.

## Two principles that drive every decision

- **Shift left.** Catch each class of problem at the earliest, cheapest stage. A lint error caught pre-commit costs seconds; the same logic bug caught in production costs hours. Order gates cheapest-and-most-likely-to-fail first so the pipeline fails fast and the developer waits the minimum time to learn they are wrong.
- **Faster is safer.** Small, frequent changes are easier to verify and to debug than large batches; a deploy with three changes localizes a regression that a deploy with thirty hides. A pipeline that takes 30 minutes gets bypassed; the speed of the pipeline is a correctness property, not a convenience.

## Workflow

### 1. Establish the platform and the trigger surface

Use the platform the repo already targets (GitHub Actions, GitLab CI, CircleCI, Buildkite); they differ in syntax, not in the gate model below. Decide what each trigger runs: pull request runs the full gate set (this is what protects `main`); push to `main` re-runs gates and may deploy; a tag or release triggers production. Never design a single monolithic job that runs on everything; the trigger determines the work.

### 2. Order the quality gates by cost

Every change passes through gates in ascending order of time-to-run, so the fastest signal fails first:

| Order | Gate | Typical command | Why here |
|---|---|---|---|
| 1 | Format + lint | `eslint`, `prettier --check`, `ruff` | Seconds; catches the most, costs the least |
| 2 | Type check | `tsc --noEmit`, `mypy` | Fast, catches whole classes of bugs before tests run |
| 3 | Unit tests | `vitest`, `pytest`, `go test` | The core correctness gate |
| 4 | Build | `npm run build`, compile | A green test suite that does not build ships nothing |
| 5 | Integration tests | API + real DB in a service container | Slower; needs infra, so it runs after the cheap gates pass |
| 6 | E2E (optional) | `playwright test` | Slowest and flakiest; gate the critical paths only |
| 7 | Security + supply chain | `npm audit --audit-level=high`, secret scan | Catches known-vulnerable deps and leaked secrets |

A failing gate blocks; it is never made to pass by disabling the rule, skipping the test, or lowering the audit level. That is the one rule the whole design exists to enforce.

### 3. Make the gates actually block the merge

A pipeline that runs but does not gate is theater. The enforcement lives in branch protection, not the workflow file: mark the CI jobs as required status checks, require the branch be up to date, and forbid force-push to `main`. Without this, every gate above is advisory and the first person in a hurry merges red.

### 4. Design the deploy path and its reversal

Separate deploy (ship the code) from release (turn it on), because coupling them makes every rollback a redeploy:

- **Preview deploys** per PR for manual verification before merge.
- **Staged rollout**: merge to `main` deploys to staging automatically; production is a gated promotion (manual approval or auto-after-staging-soak), followed by a monitored window.
- **Feature flags** decouple release from deploy: merge dark, enable for 1 percent, then 10, then 100; roll back by flipping the flag, not reverting code. Every flag gets a removal date or it becomes permanent debt.
- **Rollback is a first-class workflow**, not an improvised `git revert` under pressure: a one-command path back to the last known-good version, designed and tested before it is needed.

### 5. Keep secrets and environments separate

CI never holds production secrets. Use the platform's secret store (or short-lived OIDC federation over long-lived keys), separate credentials per environment, and a committed `.env.example` template while the real `.env` stays gitignored. A secret in a workflow file or a build log is a leaked secret.

### 6. Budget the pipeline to under ~10 minutes

When the pipeline crosses ten minutes it starts getting bypassed; apply in order of impact: cache dependencies, split independent gates into parallel jobs, use path filters to skip unaffected work (no E2E on a docs-only change), shard the test suite across runners, then move genuinely slow suites off the critical path onto a schedule.

## Example: a parallel GitHub Actions gate set

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm test -- --coverage
      - run: npm run build

  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }
      - run: npm ci
      - run: npm audit --audit-level=high
```

The four jobs run concurrently; each is a required status check in branch protection, so any red one blocks the merge. Caching (`cache: 'npm'`) and parallelism keep the wall-clock at the slowest single job, not the sum.

## Feed CI failures back into the loop

The value of CI under an agent is the closed loop: a failure is structured, quotable input. On red, read the specific failure, reproduce and fix locally, verify the gate passes, then push, rather than pushing speculative fixes and waiting for the remote to re-run. Lint failures often auto-fix (`--fix`); a flaky test is fixed or quarantined, never blindly re-run, because a re-run that goes green taught you nothing and the flake still hides real failures.

## Gotchas

- **A pipeline that does not gate the merge is decoration.** The workflow file running is necessary and not sufficient; without required status checks in branch protection, red merges and the gates were for nothing. Verify the protection, not just the YAML.
- **Flaky tests are treated as bugs, not weather.** "Just re-run it" normalizes ignoring failures and trains everyone to merge red; a flaky test masks a real intermittent bug. Quarantine it out of the blocking path with a ticket to fix, do not leave it failing intermittently in the gate.
- **Skipping a gate to go green defeats the gate.** Disabling a lint rule, `test.skip`, or dropping `--audit-level` to make the pipeline pass converts the enforcement layer into a rubber stamp. Fix the cause; if a check is genuinely wrong, change it deliberately with a reason, not under deadline pressure.
- **Coupling deploy and release makes rollback expensive.** If turning a feature on requires a deploy, turning it off requires another deploy at the worst possible time. Flags and a tested rollback workflow make reversal a flip, not a fire drill.
- **CI with production secrets is a breach waiting to happen.** Test pipelines get test credentials; production secrets live only in the deploy platform. A secret echoed into a log is published even after you delete the log.
- **The 10-minute budget is a correctness property.** Past it, people bypass CI, and a bypassed gate enforces nothing. Treat pipeline latency as a first-class thing to optimize, not an inconvenience to tolerate.

---
name: prepare-for-deploy
description: >-
  Use this skill when preparing a release or deployment: cutting a version,
  changelog and version bumps, pre-deploy gates, staging deploys, rollback
  plans, or when the user says "get this ready to deploy", "prep the
  release", "cut a release", "ship this", or asks to deploy anything. The
  skill prepares everything and hands the user the exact production deploy
  step; it never executes a production deploy itself. Do not use for planning
  schema or API migrations (use create-migration-plan), for fixing failures
  the gates surface (use fix), or for live production incidents (stabilize
  first, then write-post-mortem).
---

## Purpose

Take a change from "merged" to "one keystroke from production": every gate green, version and changelog cut, rollback plan written, non-production environments deployed and verified, and the exact production deploy step handed to the user. **The production deploy itself is never executed by the agent, under any phrasing.** Everything before that line is automated as far as the project allows, preferring deterministic mechanisms (scripts, CI, commit-derived changelogs) over judgment, because a release process that depends on judgment produces different releases on different days.

## Workflow

### 1. Learn the project's deploy shape; never invent one

Read the CI config, deploy scripts, infra files, and package manifests to find how this project actually releases: pipeline stages, environments, version file, changelog convention, deploy commands. The skill drives the project's existing process. If no process exists, building one is its own task; say so and offer it rather than improvising a release path on the spot.

### 2. Run the deterministic gates

These are mechanical pass/fail checks; run them, do not reason about them:

| Gate | Check |
|---|---|
| Working tree | Clean; release prep never bundles unstaged work |
| Tests, lint, types | The project's own commands, all green |
| Build | Succeeds from a clean state |
| Dependency audit | The project's audit tooling; no known-exploitable findings |
| Secrets scan | Diff since last release contains no credentials |

Any red gate stops the release and routes to fix. Never disable, skip, or rerun-until-green a failing gate to make the release happen; a gate bypassed for one release is dead from then on.

### 3. Cut version and changelog deterministically

- Derive the bump from the recorded changes, not from feel: breaking changes or removals mean major, added features mean minor, fixes only mean patch, read from conventional commits or the changelog's Unreleased section. An empty Unreleased section means there is nothing to release; stop.
- Roll Unreleased into a dated version section; write the new version to the project's version file.
- New commits only, never amend, so release commits stay separate from work commits and nothing already pushed is rewritten.

### 4. Review what rides along (judgment starts here)

- **Migrations**: if schema or data changes ship with this release, verify they are backward compatible with the currently deployed code, because app rollback takes minutes while database rollback may not exist. Staged or risky migrations route to create-migration-plan before the release proceeds.
- **Config and environment**: diff required env vars and config against what each target environment has; a release that needs an unset variable fails at startup, after the deploy.
- **Feature flags**: confirm which flags gate the new behavior and their intended launch state. Flags decouple deploying code from releasing behavior, which makes the rollback story a toggle instead of a redeploy.
- **Observability and baseline**: confirm the health endpoint covers the new surface and that errors and latency for it will actually appear on a dashboard someone watches. Then record the current production baseline now, before the deploy: error rate, p50/p95/p99 latency, availability. This is not decoration; the numbers become the concrete rollback triggers in the next step, and a baseline captured after deploying is already contaminated by the deploy.

### 5. Write the rollback plan before deploying anything

A rollback plan written during an incident is a bad plan. Before any environment receives this release, write down:

- **Triggers**: concrete thresholds, not vibes (error rate above 2x baseline, p95 latency up 50 percent, any data-integrity report).
- **Method, fastest first**: flag off (seconds), redeploy previous artifact (minutes; confirm the previous artifact still exists and is runnable), database restore (last resort; pairs with the migration compatibility check above).
- **Verification**: the health check and the metric that proves the rollback worked.

### 6. Deploy to non-production and verify

Staging, preview, and canary deploys are within the skill's authority; run them through the project's own mechanism, then verify with the project's smoke checks plus a manual pass over the critical flow: health endpoint green, no new error types, latency within baseline. A failed staging verification stops the release exactly like a red gate.

### 7. Hand off production

Present one confirmation package: version and bump reason, changelog entry, gates table, rides-along review, rollback plan, staging verification results, and the exact production deploy command or action, copy-pasteable, for the user to run. Include the post-deploy verification step they run immediately after deploying: the exact health check plus the step-4 baseline metrics to compare against, with the success condition stated plainly. The deploy is confirmed only when health is green and metrics hold within the rollback triggers; if they do not, execute the rollback plan. Offer to watch the post-deploy signals with them once they have deployed. The handoff tells the user both how to start the deploy and how to know it actually worked; the skill's job ends there, not at the deploy command alone.

## Gotchas

- **"Ship it" does not change the line.** No phrasing, urgency, or "it's just a tiny fix" moves the production deploy from the user to the agent. The handoff is the design, not friction to optimize away.
- **Staging green is necessary, not sufficient.** Production differs in data volume, traffic shape, and integrations; that is why the rollback plan and post-deploy watching exist even after a perfect staging run.
- **Deterministic before agentic, always.** If the changelog can be derived from commits, derive it; if the bump follows semver rules, compute it; reserve judgment for what cannot be scripted (is this finding a blocker, are the flags in the right launch state). Judgment applied to scriptable steps is where releases become irreproducible.
- **The previous artifact is part of this release.** A rollback plan that says "redeploy the previous version" is fiction unless the previous image or build is verified to still exist and run.
- **Release notes are not commit messages.** The changelog entry users read describes value and breakage in their terms; commit subjects are the input, not the output.

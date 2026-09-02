# Dependency upgrades: major version bumps

Read this for the execution craft of a major version bump of a library, framework, or language runtime: extracting the breaking changes, adopting incrementally behind a compatibility shim, applying codemods, and gating each step on a green test suite and a clean lockfile.

## Read the changelog before touching the lockfile

A major version exists to ship breaking changes; the changelog and migration guide are the spec for the work. Before bumping anything, extract the breaking changes that touch your usage:

- Read the upstream CHANGELOG, the release notes, and the dedicated migration guide if one exists. Major frameworks ship one (the React, Next.js, Django, Rails upgrade guides); treat its absence as a reason to read the diff between tags.
- Grep your codebase for each removed or renamed API the guide names, to size the actual blast radius. "Nobody uses that" needs the grep, not the assumption (Hyrum's Law: every observable behavior is depended on somewhere).
- Note transitive impact: a bump can force peer dependencies up. Read the peer-dependency ranges before you discover them as install failures.

## Adopt incrementally, both versions valid in the window

The upgrade is the universal method's expand-migrate-contract at repo scale; a single PR that bumps the version and rewrites every call site at once is the big-bang mistake.

- **Compat shim or adapter first (expand).** Where the old and new APIs differ, introduce a thin wrapper that presents the old surface over the new internals (or vice versa), so call sites migrate one at a time instead of all at once. For a runtime bump, this is a polyfill or a feature-detect branch.
- **Migrate call sites incrementally (migrate).** Move modules to the new API in reviewable batches, each behind its own test run. Both patterns are allowed to coexist during this window; that is the point of the shim.
- **Remove the shim and old patterns (contract).** Only after every call site is on the new API, delete the compat layer and the old-pattern lint suppressions. A lingering shim is dead weight that hides whether the migration is actually done.

## Codemods do the mechanical edits

When the change is a mechanical rename or signature shift across many files, a codemod is faster and more reliable than hand edits and leaves a reviewable diff.

- Run the upstream-provided codemod if one ships (`npx @next/codemod`, `npx jscodeshift`, `2to3` / `pyupgrade`, `gofmt -r`, `cargo fix --edition`). Major ecosystems ship them precisely because the edits are mechanical.
- A codemod handles the mechanical 90 percent, not the semantic 10 percent. Review its diff, and handle the cases it could not (behavioral changes, not just syntactic ones) by hand.
- Commit the codemod output as its own commit, separate from hand-written fixes, so the reviewable mechanical change is isolated from judgment calls.

## Lockfile and test-gate discipline

The test suite is the verification surface for an upgrade; the lockfile is the reproducibility surface.

- Bump one major dependency at a time and run the full suite before the next. Bundling several majors into one PR makes a failure impossible to attribute to its cause.
- Commit the updated lockfile (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`, `go.sum`) in the same commit as the version bump, so the resolved graph is reproducible and the bump is revertible as a unit.
- Pin the new version to an exact or tight range during the migration; loosen it only after the suite is green, so a transitive re-resolution does not move the target mid-migration.

## Pitfalls

- **The big-bang upgrade PR.** Bumping the version and rewriting every call site in one PR removes the incremental rollback. Stage it: shim, then migrate, then contract.
- **Green CI is not green production.** A suite can pass while a behavioral change (different default, changed timing, stricter validation) breaks under real load or real data. Roll the upgrade out behind the same incremental discipline as any migration, and watch a canary before full deploy.
- **Transitive peers move under you.** A major bump can force a peer dependency up a major too, which has its own breaking changes. Read the peer ranges first; a surprise transitive major is a second migration you did not plan.
- **Codemods miss semantics.** A codemod renames the call but cannot know that the new function returns a promise where the old one was synchronous. The diff review is where you catch what the codemod could not.

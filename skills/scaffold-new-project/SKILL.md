---
name: scaffold-new-project
description: 'Use this skill when scaffolding a brand-new project from scratch: starting a new TypeScript library, CLI tool (commander), or MCP server, a new Python package or Python MCP server (uv, ruff, pytest), a new React web app with Playwright e2e, or a new pnpm monorepo with workspace catalogs. Use when the user says "scaffold a new project", "start a new repo", "set up a new library/CLI/MCP server", "new TS package", "bootstrap a React app", or "create a pnpm monorepo". Triggers on choosing tsup, biome, vitest, fastmcp, or pnpm-workspace for a brand-new project. Do not use when adding files to an existing project, migrating, or copying one (use code-with-best-practices for implementation in a repo that already exists).'
---

## Purpose

Scaffold a brand-new project from Brandon's real config conventions so a repo starts consistent instead of being hand-assembled. Resolve the archetype, project name, and optional add-ons first; then copy the config templates from the matching reference verbatim; then run the verify loop. The deliverable is a runnable project that passes its own lint, typecheck, and test before you declare it done. Never scaffold into a directory that already contains a project.

## Resolve the build (always first)

Do this before writing any file. Scaffolding the wrong archetype wastes a full setup.

1. **Infer from the request.** Pull the archetype, project name, and any stated add-ons (git hooks, transport, publish target) out of what the user already said. "New commander CLI called foo" fully specifies archetype + name; do not re-ask.
2. **Ask only for missing critical decisions, in one batched message.** The critical decisions are: archetype (if ambiguous), project name (if absent), and optional add-ons (git hooks and a GitHub Actions CI gate: both default off, suggest for projects that will be published or shared). Do not interrogate when the request already answered it.
3. **Confirm the target directory does not exist or is empty.** If it contains a project, stop: this skill scaffolds new projects only. Route existing-repo work to `code-with-best-practices`.

Hard stop: do not write a single file until archetype and name are unambiguous.

## Archetype routing

Match the request to one row, then read the listed reference file(s) in full before writing. Rows that list `shared-ts-config.md` need both files: the shared base plus the archetype deltas.

| Stated intent / keywords | Archetype | Read |
|---|---|---|
| TS library, package, publishable, tsup | TS library | `references/archetype-ts-core.md` (library) + `references/shared-ts-config.md` |
| CLI, command-line tool, commander, bin | TS CLI | `references/archetype-ts-core.md` (CLI) + `references/shared-ts-config.md` |
| MCP server, TypeScript MCP, fastmcp | TS MCP | `references/archetype-ts-core.md` (MCP) + `references/shared-ts-config.md` |
| Python package, uv, ruff, pytest | Python package | `references/archetype-python.md` (package) |
| Python MCP server, fastmcp (Python) | Python MCP | `references/archetype-python.md` (MCP) |
| React app, web app, frontend, Playwright | Web/React | `references/archetype-web-react.md` + `references/shared-ts-config.md` |
| monorepo, pnpm workspace, catalog | Monorepo | `references/archetype-monorepo.md` + `references/shared-ts-config.md` |

## Scaffolding rules

- **Copy config blocks verbatim.** Do not reformat, reorder keys, bump versions, drop fields, or add fields the template does not have. These choices are deliberate, and biome reformats the rest of the project on first run anyway. Paraphrased config is the top failure mode of this skill.
- **TypeScript baseline is fixed.** Every TS project gets `type: module`, a `packageManager: pnpm@<version>` field, and `engines.node: ">=20"`. Use pnpm, never npm or yarn, for install and dependency commands.
- **Python, React, and Playwright templates are best-practice defaults, not mirrored from a real repo.** Tell the user this when you scaffold them, and invite correction. The skill is meant to iterate: capture any preference the user states back into the relevant reference.
- **Add-ons only when chosen.** Two opt-in add-ons exist: git hooks (husky + commitlint + lint-staged) and a GitHub Actions CI gate. Add either only when the user asks or accepts the suggestion, not by default.
- **Resolve versions through the package manager.** Run `pnpm add` / `uv add` so the lockfile pins versions, rather than hand-editing dependency version ranges into the manifest beyond what the template specifies.

## Verify the scaffold

Run the verify loop and fix until green before declaring done. A scaffold that does not pass its own checks is not done.

- TypeScript: `pnpm install && pnpm check && pnpm typecheck && pnpm test`
- Python: `uv sync && uv run ruff check && uv run pytest`

When green, initialize version control: `git init`, then an initial commit (`chore: scaffold <archetype> project`).

## Gotchas

- **The two fastmcp packages are different.** TypeScript MCP servers use the npm `fastmcp` (punkpeye); Python MCP servers use the PyPI `fastmcp` (jlowin). They are unrelated projects with different APIs; do not cross them.
- **biome quote style varies across Brandon's repos.** The default encoded here is the majority style (`quoteStyle: single`, `semicolons: asNeeded`). A double-quote + `always` camp exists in a couple of repos; do not "fix" the default to match those.
- **`catalog:` over hardcoded versions in monorepos.** Reference catalog entries with `catalog:` and let pnpm resolve and pin them in the lockfile, rather than hardcoding version ranges that rot.
- **Boundaries:** `code-with-best-practices` owns writing feature code inside the repo once it exists; `design-cli` owns the command-surface UX; `design-mcp` owns the tools-vs-resources contract and schemas. The optional CI add-on lays down a minimal lint+typecheck+test gate only; `design-cicd` owns real pipeline design (deploy stages, branch protection, matrix builds, caching). This skill stops at the runnable skeleton plus that starter gate; hand off the design work.

---
name: onboard-codebase
description: >-
  Use this skill when building an understanding of an unfamiliar codebase or
  orienting in a new repository. Use when the user says "onboard me", "help me
  understand this codebase", "walk me through this repo", "how does this
  project work", "zoom out", or "where does X happen in here", and when
  starting substantial work in a repo with no AGENTS.md. Do not use for
  evaluating architecture quality (use audit-architecture), for generating a
  CLAUDE.md (use the bundled init), or for locating one specific symbol (just
  search).
---

## Purpose

Build an accurate working map of an unfamiliar codebase and leave it recorded: an onboarding guide the user can scan in two minutes, plus the project's AGENTS.md created or enhanced per the global documentation rules. Orientation, not evaluation; judging the architecture is audit-architecture's job, and mixing the two turns a map into a critique nobody asked for.

## Workflow

### 1. Reconnaissance without reading everything

Gather signals with Glob and Grep, reading files only to resolve ambiguity; the Explore subagent (medium thoroughness) fits large repos. Targets:

- Manifests and lockfiles (`package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, ...) for language, dependencies, and scripts
- Framework fingerprints (config files), entry points (`main.*`, `cmd/`, `src/index.*`, app factories)
- Directory tree, top two levels, ignoring vendored and generated dirs
- Tooling: linter and formatter configs, Makefile, Dockerfile, CI workflows, `.env.example`
- Tests: location, framework, naming pattern
- Existing docs: README, AGENTS.md or CLAUDE.md, docs/, ADRs; read these first when present, the map may already exist

### 2. Map the architecture

From the signals, establish and verify against actual code (config says what was installed; code says what is used):

- Stack: languages, frameworks, datastores, build tooling
- Shape: monolith, monorepo, services; frontend/backend split; API style
- Directory purposes: every top-level directory mapped to what lives there, skipping the self-evident
- **One traced request or invocation, end to end**: entry, validation, business logic, persistence, response. The trace is what turns a directory listing into understanding, and it is the most common omission

### 3. Detect the conventions

Naming patterns (files, tests), error handling style, async patterns, state management, commit message style and branch naming from recent history (note when history is too shallow to tell). These come from observation, not inference; "could not determine the test runner" beats a guess.

### 4. Deliver the guide and record the map

**Onboarding guide** in chat, scannable in two minutes:

```markdown
## <Project> in two minutes

**What it is**: <2-3 sentences>
**Stack**: <table or one line per layer>
**Shape**: <architecture pattern, one line>
**Directory map**: <top-level dir -> purpose>
**Request lifecycle**: <the traced path>
**Conventions**: <observed patterns>
**Common tasks**: <dev / test / lint / build commands>

| I want to... | Look at... |
|---|---|
| <common change> | <where> |
```

**AGENTS.md**: per the global rules, every project gets one. If absent, offer to create it from the findings (description, conventions, constraints, structure overview); if present, verify the findings against it and propose corrections where observed reality contradicts it. Never replace existing content wholesale; enhance and call out what changed.

### 5. Zoom-out mode

When the user is lost in one area ("zoom out", "how does this fit"), skip the full workflow: go up one abstraction level and deliver a map of the relevant modules and their callers, in the project's own vocabulary, centered on where they are.

## Rules

- **Trust code over config.** A dependency in the manifest that nothing imports is not part of the stack; a framework detected from config but absent from the code is noise.
- **Flag unknowns instead of guessing.** Wrong onboarding is worse than incomplete onboarding, because the reader cannot tell which parts to distrust.
- **Stay concise.** Details belong in the code; the guide adds the structural insight the README lacks, not a paraphrase of it. Do not list every dependency, only the ones that shape how code gets written.
- **Do not editorialize.** "The auth module is a mess" belongs in audit-architecture's evidence-backed format, not here; if friction is glaring, note it as a one-line pointer and offer the audit.

## Gotchas

- **The README lies more often than it is updated.** Treat it as a hypothesis to verify, not a source; the same goes for stale AGENTS.md content, which the global rules say to correct against observed reality.
- **Monorepos onboard per-package.** A whole-monorepo guide is too thin to use; pick the package the user cares about, map the shared infrastructure once, and go deep only where they will work.
- **The two-minute constraint is load-bearing.** An onboarding guide that takes twenty minutes to read gets skimmed once and abandoned; cutting is the work.
- **Conventions are evidence-based.** Three files using a pattern is a convention; one file using it is an experiment someone left behind.

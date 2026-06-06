---
name: code-with-best-practices
description: >-
  Use this skill when planning, writing, or reviewing code in TypeScript,
  JavaScript, Python, Go, Rust, SQL, or Bash, or when working with React,
  Node.js, Vitest, Playwright, Terraform, or AWS CDK. Use for any
  implementation work in these stacks even when the user never says "best
  practices". Do not use for API contract design (use design-api), database
  schema design (use design-data-schema), or UI visual design (use design-ui).
---

## Purpose

Consolidated entry point for language and framework best practices. Detect the stack in scope, then load only the reference files the task needs; the practices live in `references/` precisely so that unrelated stacks never consume context. Loading every reference defeats the design.

## Project discovery (always do first)

1. Detect frameworks and tooling from manifests and configs: `package.json` dependencies, `vitest.config.*`, `playwright.config.*`, `cdk.json`, `*.tf` files, `go.mod`, `Cargo.toml`, `pyproject.toml`.
2. Detect the language from the extensions of the files actually being touched.
3. Load references per the routing table below.

## Routing table

| Context | Load |
|---|---|
| React component or app work | [React](references/framework-react.md) + [TypeScript](references/language-typescript.md) or [JavaScript](references/language-javascript.md) by file type |
| Node.js service, CLI, or module work | [Node](references/framework-node.md) + [TypeScript](references/language-typescript.md) or [JavaScript](references/language-javascript.md) |
| Vitest unit or integration tests | [Vitest](references/framework-vitest.md) + [TypeScript](references/language-typescript.md) or [JavaScript](references/language-javascript.md) |
| Playwright E2E tests | [Playwright](references/framework-playwright.md) + [TypeScript](references/language-typescript.md) or [JavaScript](references/language-javascript.md) |
| AWS CDK infrastructure | [CDK](references/framework-cdk.md) + [TypeScript](references/language-typescript.md) |
| Terraform infrastructure | [Terraform](references/framework-terraform.md) |
| TypeScript, no framework match | [TypeScript](references/language-typescript.md) |
| JavaScript, no framework match | [JavaScript](references/language-javascript.md) |
| Python | [Python](references/language-python.md) |
| Go | [Go](references/language-go.md) |
| Rust | [Rust](references/language-rust.md) |
| SQL queries or migrations | [SQL](references/language-sql.md) |
| Bash or shell scripts | [Bash](references/language-bash.md) |

## Loading rules

1. When a framework applies, load its framework reference first, then exactly one language reference for the files being edited.
2. For mixed-language changes, load one language reference per touched language.
3. Never load references "just in case"; an unloaded reference costs nothing, an unused loaded one crowds out the task.

## Precedence and boundaries

- On conflict, the project's own documented conventions win, then the global CLAUDE.md rules, then these references. A reference here never justifies diff noise in a codebase that does it differently.
- The SQL reference covers writing queries and migrations; designing tables, keys, and indexes belongs to design-data-schema.
- Endpoint and schema contracts belong to design-api; these references inform the implementation behind the contract.
- This skill informs how code is written, not the workflow around it: test-first discipline is follow-tdd, behavior-preserving cleanup is refactor-code, debugging is fix.

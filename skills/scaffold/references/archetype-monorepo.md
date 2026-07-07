# pnpm monorepo archetype

A pnpm workspace with a version catalog. Shared tooling (biome, tsconfig base) lives at the root; each package inside the workspace is scaffolded with one of the TS core archetypes (library / CLI / MCP) via the SKILL.md routing.

## pnpm-workspace.yaml

The `catalog:` block pins shared dependency versions in one place; packages reference them with `"typescript": "catalog:"` so every package stays on the same version. `onlyBuiltDependencies` allowlists packages permitted to run install scripts (pnpm blocks build scripts by default).

```yaml
packages:
  - "packages/*"

catalog:
  typescript: ^6.0.3
  tsup: ^8.5.1
  vitest: ^4.1.6
  "@biomejs/biome": ^2.4.15

onlyBuiltDependencies:
  - esbuild
```

## Root package.json

Private, no version. Scripts fan out across the workspace with `pnpm -r` (recursive).

```json
{
  "name": "<workspace-name>",
  "private": true,
  "type": "module",
  "packageManager": "pnpm@<version>",
  "engines": { "node": ">=20.0.0" },
  "scripts": {
    "build": "pnpm -r build",
    "test": "pnpm -r test",
    "typecheck": "pnpm -r typecheck",
    "lint": "biome lint .",
    "format": "biome format --write .",
    "check": "biome check --write ."
  },
  "devDependencies": {
    "@biomejs/biome": "catalog:"
  }
}
```

## Layout

```text
<workspace-name>/
  pnpm-workspace.yaml
  package.json
  biome.json               # from shared-ts-config.md, lints the whole tree
  tsconfig.json            # shared base; packages extend it
  packages/
    <package-a>/           # scaffolded as a TS library / CLI / MCP archetype
    <package-b>/
```

## Per-package scaffolding

For each package the user wants inside the workspace, scaffold it with the matching TS core archetype (see `archetype-ts-core.md`), with two adjustments:

- Each package's `package.json` references shared tooling via the catalog: `"typescript": "catalog:"`, `"tsup": "catalog:"`, `"vitest": "catalog:"`.
- Each package's `tsconfig.json` extends the root: `"extends": "../../tsconfig.json"`, overriding only `outDir`/`rootDir`.
- biome runs once from the root, so packages do not need their own `biome.json`.

Confirm with the user which packages to create and which archetype each one is before scaffolding them.

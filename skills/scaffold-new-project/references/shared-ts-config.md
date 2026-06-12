# Shared TypeScript config

The single source of truth for the reusable TypeScript templates every TS archetype builds on. Copy each block verbatim; the archetype reference lists only its deltas.

- [biome.json](#biomejson)
- [package.json base](#packagejson-base)
- [tsconfig: library flavor](#tsconfig-library-flavor)
- [tsconfig: bundler flavor](#tsconfig-bundler-flavor)
- [tsup.config.ts](#tsupconfigts)
- [.gitignore](#gitignore)
- [Optional add-on: git hooks](#optional-add-on-git-hooks)
- [Optional add-on: GitHub Actions CI gate](#optional-add-on-github-actions-ci-gate)

## biome.json

The verified canonical config. `quoteStyle: single` + `semicolons: asNeeded` is the default (the majority style across the repos); do not switch it to the double-quote + `always` camp.

```json
{
  "$schema": "https://biomejs.dev/schemas/2.4.15/schema.json",
  "files": {
    "ignoreUnknown": false
  },
  "vcs": {
    "enabled": true,
    "clientKind": "git",
    "useIgnoreFile": true,
    "defaultBranch": "main"
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "style": {
        "noNonNullAssertion": "off"
      },
      "suspicious": {
        "noUnknownAtRules": "off"
      },
      "nursery": {
        "useSortedClasses": "warn"
      }
    },
    "domains": {
      "test": "recommended"
    }
  },
  "assist": {
    "enabled": true,
    "actions": {
      "recommended": true,
      "source": {
        "organizeImports": "off"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "jsxQuoteStyle": "single",
      "trailingCommas": "all",
      "semicolons": "asNeeded",
      "arrowParentheses": "asNeeded"
    }
  },
  "json": {
    "formatter": {
      "enabled": true
    }
  }
}
```

## package.json base

The fields and scripts common to every TS archetype. The archetype adds `bin`, `exports`, `dependencies`, etc. on top. Set `packageManager` to the current pnpm version (`pnpm --version`).

```json
{
  "name": "<project-name>",
  "version": "0.1.0",
  "description": "",
  "author": "Brandon Burrus <brandon@burrus.io>",
  "license": "MIT",
  "type": "module",
  "packageManager": "pnpm@<version>",
  "engines": {
    "node": ">=20.0.0"
  },
  "scripts": {
    "build": "tsup",
    "dev": "tsx src/index.ts",
    "typecheck": "tsc --noEmit",
    "lint": "biome lint .",
    "format": "biome format --write .",
    "check": "biome check --write .",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  },
  "devDependencies": {
    "@biomejs/biome": "^2.4.15",
    "@types/node": "^25.9.0",
    "@vitest/coverage-v8": "^4.1.6",
    "tsup": "^8.5.1",
    "tsx": "^4.22.2",
    "typescript": "^6.0.3",
    "vitest": "^4.1.6"
  }
}
```

`vitest.config.ts` for archetypes that ship tests:

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/**/*.test.ts"],
    coverage: {
      provider: "v8",
      include: ["src/**/*"],
      exclude: ["src/index.ts"],
    },
  },
});
```

## tsconfig: library flavor

For packages that emit declarations and JS to `dist` (library, CLI, TS MCP server).

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "ignoreDeprecations": "6.0",
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["node"],
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

## tsconfig: bundler flavor

For projects where a bundler (Vite, esbuild) emits and tsc only type-checks (`noEmit`). Used by the React archetype.

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "lib": ["ESNext"],
    "module": "Preserve",
    "moduleDetection": "force",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "noEmit": true,
    "strict": true,
    "skipLibCheck": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true
  }
}
```

## tsup.config.ts

Base build. The CLI variant adds the shebang `banner` (see archetype-ts-core).

```typescript
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["cjs", "esm"],
  dts: true,
  sourcemap: true,
  clean: true,
  outDir: "dist",
});
```

## .gitignore

The standard GitHub Node `.gitignore`, trimmed to the lines that matter here. The full upstream template is also fine.

```gitignore
# Logs
logs
*.log
npm-debug.log*

# Dependencies
node_modules/

# Build output
dist
.output
coverage
*.lcov
.nyc_output

# TypeScript cache
*.tsbuildinfo

# Environment
.env
.env.*
!.env.example

# Editor / OS
.DS_Store
.idea
```

## Optional add-on: git hooks

Opt-in. Add only when the user asks or accepts the suggestion (suggest it for projects that will be published). Adds `husky`, `@commitlint/cli`, `@commitlint/config-conventional`, and `lint-staged` to `devDependencies`, plus a `"prepare": "husky"` script.

`.husky/pre-commit`:

```bash
pnpm test
```

`.husky/commit-msg`:

```bash
npx --no -- commitlint --edit "$1"
```

`commitlint.config.js`:

```javascript
/** @type {import('@commitlint/types').UserConfig} */
export default {
  extends: ["@commitlint/config-conventional"],
};
```

`lint-staged` block in `package.json`:

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx,mjs,json,md,css}": [
      "biome check --write --no-errors-on-unmatched"
    ]
  }
}
```

## Optional add-on: GitHub Actions CI gate

Opt-in. Add only when the user asks or accepts the suggestion (suggest it for projects that will be published or shared). A minimal gate that runs lint, typecheck, and tests on every push to `main` and every pull request. This is a starter gate, not a designed pipeline; richer CI (deploy stages, branch protection, matrix builds, caching strategy) is `design-cicd`'s job.

The action versions below are best-practice defaults; bump them to the current major when scaffolding. `biome ci` is biome's no-write CI command (it fails on lint/format/import issues rather than fixing them), so the gate does not depend on the `--write` scripts.

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec biome ci .
      - run: pnpm typecheck
      - run: pnpm test
```

For the monorepo archetype this same workflow works unchanged: `pnpm typecheck` and `pnpm test` fan out via the root `pnpm -r` scripts, and `biome ci .` lints the whole tree from the root. For the React archetype, replace `pnpm test` with `pnpm build` (e2e is heavier; see the React archetype for adding a Playwright job).

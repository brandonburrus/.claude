# Web/React archetype

Best-practice defaults, not mirrored from one of Brandon's repos. Tell the user the stack choice (Vite + React + TypeScript + Playwright + biome) is a default and invite correction; fold any preference back into this file.

Read `shared-ts-config.md` for the biome.json and use its **bundler** tsconfig flavor (Vite emits; tsc only type-checks). Deltas below.

## package.json

```json
{
  "name": "<project-name>",
  "version": "0.1.0",
  "type": "module",
  "packageManager": "pnpm@<version>",
  "engines": { "node": ">=20.0.0" },
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "typecheck": "tsc --noEmit",
    "lint": "biome lint .",
    "format": "biome format --write .",
    "check": "biome check --write .",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@biomejs/biome": "^2.4.15",
    "@playwright/test": "^1.49.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^6.0.3",
    "vite": "^6.0.0"
  }
}
```

For this archetype, `check` and `typecheck` cover the verify loop; `test` runs e2e via `test:e2e`.

## vite.config.ts

```typescript
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
});
```

## playwright.config.ts

The `webServer` block lets `playwright test` boot the dev server itself, so the verify loop needs no separate start step.

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "html",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
  },
});
```

## Layout

```text
<project-name>/
  index.html
  vite.config.ts
  playwright.config.ts
  tsconfig.json            # bundler flavor from shared-ts-config.md
  biome.json               # from shared-ts-config.md
  src/main.tsx
  src/App.tsx
  e2e/home.spec.ts
```

`e2e/home.spec.ts` example:

```typescript
import { expect, test } from "@playwright/test";

test("home page loads", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/.+/);
});
```

After install, run `pnpm exec playwright install` to fetch browsers before the first `test:e2e` run.

## Optional add-on: GitHub Actions CI gate

If the CI add-on is chosen (see `shared-ts-config.md`), use its workflow with `pnpm test` replaced by `pnpm build` for the base gate, since React has no unit `test` script. To also gate on e2e, add a second job that installs browsers first:

```yaml
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps
      - run: pnpm test:e2e
```

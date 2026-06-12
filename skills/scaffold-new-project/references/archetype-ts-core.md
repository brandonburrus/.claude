# TypeScript core archetypes

Three TS archetypes that share the base in `shared-ts-config.md`. Read the shared base first, then apply only the deltas below. Do not restate the shared config.

- [Library](#library)
- [CLI](#cli)
- [MCP server (TypeScript)](#mcp-server-typescript)

## Library

A publishable package that emits declarations and dual ESM/CJS output.

- tsconfig: **library flavor**.
- package.json deltas: add the publish surface.

```json
{
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    }
  },
  "files": ["dist"],
  "publishConfig": {
    "access": "public"
  }
}
```

- Layout: `src/index.ts` (the public entry), `tests/`.

## CLI

A commander-based command-line tool with a `bin`.

- tsconfig: **library flavor**.
- package.json deltas: `commander` dependency + a `bin` pointing at the built ESM entry.

```json
{
  "bin": {
    "<command-name>": "./dist/index.js"
  },
  "dependencies": {
    "commander": "^14.0.3"
  }
}
```

- tsup delta: add the ESM shebang so the built `bin` is directly executable.

```typescript
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["cjs", "esm"],
  dts: true,
  sourcemap: true,
  clean: true,
  outDir: "dist",
  banner: ctx => (ctx.format === "esm" ? { js: "#!/usr/bin/env node" } : {}),
});
```

- `src/index.ts` skeleton:

```typescript
import { Command } from "commander";
import packageJson from "../package.json" with { type: "json" };

const program = new Command(packageJson.name)
  .description(packageJson.description)
  .version(packageJson.version);

program
  .command("hello")
  .argument("<name>", "who to greet")
  .action((name: string) => {
    process.stdout.write(`Hello, ${name}\n`);
  });

program.parse(process.argv);
```

## MCP server (TypeScript)

A FastMCP server using the npm `fastmcp` package (punkpeye). This is a different project from the Python `fastmcp` (jlowin); do not confuse the two.

- tsconfig: **library flavor**.
- package.json deltas: `fastmcp` + `@modelcontextprotocol/sdk` + `zod`, plus a `bin`. Use the CLI tsup variant (shebang banner) so the server runs directly.

```json
{
  "bin": {
    "<server-name>": "./dist/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.29.0",
    "fastmcp": "^4.0.1",
    "zod": "^4.4.3"
  }
}
```

- `src/index.ts` skeleton (stdio by default; httpStream gated behind an env var, matching the real-repo pattern of warning when bound to a non-loopback host):

```typescript
#!/usr/bin/env node
import { FastMCP } from "fastmcp";
import { z } from "zod";

const server = new FastMCP({
  name: "<server-name>",
  version: "0.1.0",
});

server.addTool({
  name: "add",
  description: "Add two numbers",
  parameters: z.object({ a: z.number(), b: z.number() }),
  execute: async args => String(args.a + args.b),
});

const transport = process.env.MCP_TRANSPORT ?? "stdio";

if (transport === "httpStream") {
  const port = Number(process.env.MCP_PORT ?? 8080);
  await server.start({ transportType: "httpStream", httpStream: { port } });
} else {
  await server.start({ transportType: "stdio" });
}
```

The tool contract here is a placeholder. Designing the real tools, resources, and schemas is `design-mcp`'s job, not this skill's.

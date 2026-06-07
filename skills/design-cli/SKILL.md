---
name: design-cli
description: >-
  Use this skill when designing or building a command-line tool: a durable CLI
  that wraps an API, SDK, service, or script and exposes composable commands
  with stable output. Use when the user says "build a CLI for X", "make a
  command-line tool", "wrap this API in a CLI", "turn this script into a real
  tool", or wants reusable read/write commands with auth and JSON output. Do
  not use for designing the HTTP or GraphQL contract a service exposes (use
  design-api), for a throwaway one-off script that solves a single task in
  place, or for general code implementation (use code-with-best-practices).
---

## Purpose

Design a command-line tool that both humans and agents can run repeatably from any directory: composable commands, predictable JSON, safe writes, and auth that does not leak. The design is the deliverable that makes implementation mechanical; a CLI built without designing the command surface first becomes a pile of one-off flags that no second caller can compose. This skill is for durable tools. If a short script in the current repo solves the task once, write that script instead; not every job needs a CLI.

## First gate: tool or script?

A CLI earns its complexity only when the capability is invoked repeatedly, from outside the originating repo, by callers who did not write it. One task, one repo, one run is a script. Say which it is before proceeding; building a CLI for a one-off is over-engineering, and writing a script for a recurring cross-repo need is under-building.

## Choose the runtime deliberately

Inspect what the machine and the source material already use, then pick the least surprising durable toolchain, stating the choice and reason in one sentence:

- A compiled single binary (Rust, Go) when the tool should run anywhere with no runtime setup; this is the default for a durable, broadly-shared CLI.
- The language of the official SDK when an SDK, auth helper, or automation library is the reason the CLI can be better than raw HTTP.
- A scripting runtime (Python, Node) when the work is local file/data transforms or the surrounding tooling already lives there.

Do not pick a language that adds setup friction unless it materially improves the tool. Match the ecosystem's established CLI libraries (argument parsing, HTTP, JSON, config) rather than hand-rolling parsers.

## Design the command surface before coding

Sketch the full command list first. The shape is product nouns then verbs, kept consistent across the tool:

```text
tool <noun> <verb> [args] [--flags]      e.g.  tool projects list
tool --json messages search "phrase"     e.g.  tool channels resolve --name eng
```

Cover these command families; the taxonomy is the design:

| Family | Job | Rule |
|---|---|---|
| `doctor` | Verify config, auth presence, version, endpoint reachability | Must work and report clearly even when auth is missing, never crash |
| Discover | List top-level containers (accounts, projects, queues, repos) | The entry point when the caller knows nothing yet |
| Resolve | Turn names, URLs, slugs, permalinks into stable IDs | So later commands never re-run broad searches |
| Read | Fetch one exact object; list or search a collection | Lists take a bounded `--limit` and a documented pagination knob |
| Write | One named action each: create, update, delete, upload, retry | Narrowest stable ID; `--dry-run`/`draft`/`preview` first where the service allows |
| Raw escape hatch | `request`/`api` for the gap when a high-level verb is missing | Reads first; still uses configured auth, base URL, redaction, JSON |

Two anti-patterns to design out: a single broad command that "does the whole job" (expose composable primitives instead), and hiding writes inside vague verbs like `fix`, `sync`, or `auto` (every mutation is named and explicit). `tool --help` should answer, on its own, what can be discovered, read, resolved, written, and what the raw hatch is.

## Output contract

The output is an API other programs depend on; make it stable:

- `--json` available everywhere a caller will parse or pipe. JSON goes to stdout only; progress and diagnostics go to stderr, so a pipe is never corrupted by a log line.
- Document and hold a success shape and an error shape. Under `--json`, errors are machine-readable objects, never a bare string and never a stack trace.
- Redact tokens, cookies, secrets, and private headers from all output, including the raw hatch and error payloads.
- Exit zero on success including an empty result (empty is not an error); exit nonzero for auth failure, invalid input, network failure, parse failure, or an incomplete write.

## Auth and config

Support the boring paths, in precedence order, so the tool works before any setup ceremony:

1. Environment variable using the service's standard name (`GITHUB_TOKEN`, `STRIPE_API_KEY`).
2. A user config file at a simple documented path (`~/.config/<tool>/config.toml`).
3. A token flag only for explicit one-off tests; prefer env/config because flags leak into shell history and process listings.

Never print a full token. `doctor` reports whether a token is present and its source category (env, config, flag, missing) and what setup step is missing, never the value. If the tool has an offline or fixture mode, `doctor` says so and whether auth is even required.

## Build and verify

1. Read the source (API docs, OpenAPI spec, SDK, or the existing script) just enough to inventory resources, auth, pagination, ID shapes, and dangerous writes.
2. Implement `doctor`, discovery, resolve, and read commands first; add one narrow `--dry-run` write path and the raw read hatch.
3. Install the binary on `PATH`, then smoke-test from `/tmp` or another repo, not from the source folder: `command -v <tool>`, `<tool> --help`, `<tool> --json doctor`. Testing only inside the source directory hides the most common defect, a tool that cannot find its config or fixtures once installed elsewhere.
4. Unit-test the request and pagination builders, the no-auth `doctor` path, and at least one fixture or read-only call. A live write used for confidence is asked for first and kept reversible or draft-only.

## Companion documentation

A durable CLI ships a short usage doc ordered the way a caller should move through the tool, not as a feature tour: how to confirm it is installed, which command to run first, how auth is set, the discovery command that finds the common ID, the safe read path, the intended write path, what not to run without explicit approval, and three copy-pasteable examples. Keep exhaustive per-command detail in the tool's own `--help` and reference; the companion doc teaches the path.

## Gotchas

- **The JSON output is a contract, and contracts that drift break callers silently.** A field renamed or a shape changed under `--json` breaks every script and agent parsing it, with no error at the call site. Version or hold the shape; treat it like the API it is.
- **Smoke-testing from the source folder is the bug you will ship.** `cargo run` and `npm start` resolve paths relative to the project; the installed binary does not. Test from `/tmp` or the failure surfaces on someone else's machine.
- **A token in a flag is a token in shell history.** Default auth to env and config; the flag exists for one-off tests and leaks everywhere it is used. `doctor` reports presence and source, never the secret.
- **Writes hidden in broad commands are how an agent deletes production.** Every mutation is one named, explicit verb with a dry-run path; a `sync` or `fix` command that quietly writes is a command a cautious caller cannot reason about.
- **The raw escape hatch is a repair tool, not the interface.** If callers must reach for `request`/`api` for routine work, the high-level verbs are missing; build them. Raw writes are live writes and never hide behind a "debug" name.

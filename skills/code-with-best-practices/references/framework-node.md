Apply these practices whenever planning, writing, or reviewing Node.js code. Targets Node.js 22 LTS (and 24; version-specific items are flagged). Generic clean-code, general-JavaScript async, and dependency rules live in CLAUDE.md; this reference is the Node-runtime-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Modules and runtime](#modules-and-runtime)
- [Built-in tooling](#built-in-tooling)
- [Cancellation and timeouts](#cancellation-and-timeouts)
- [Event loop and scheduling](#event-loop-and-scheduling)
- [Buffers and binary data](#buffers-and-binary-data)
- [Filesystem](#filesystem)
- [Streams and large data](#streams-and-large-data)
- [EventEmitter](#eventemitter)
- [Process lifecycle and shutdown](#process-lifecycle-and-shutdown)
- [Networking](#networking)
- [Configuration and security](#configuration-and-security)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Modules and runtime

| Practice | Detail |
|---|---|
| Default to ESM, not CommonJS | New projects set `"type": "module"`. The `"type"` field decides whether a `.js` file is parsed as ESM or CJS, before reading its contents, so a wrong value makes Node parse the opposite format and fail. As of 22.12 `require()` can load a synchronous ESM graph, but it throws `ERR_REQUIRE_ASYNC_MODULE` if any module in that graph uses top-level await. |
| There is no `__dirname` in ESM | Use `import.meta.dirname` and `import.meta.filename` (21.2+, decoded and platform-aware), not `fileURLToPath(import.meta.url)` boilerplate. Never derive a path from `new URL(...).pathname`: it is URL-encoded (a space becomes `%20`) and breaks on Windows. |
| Treat `"exports"` as the package's real API boundary | Once a package declares `"exports"`, an undocumented subpath throws `ERR_PACKAGE_PATH_NOT_EXPORTED` even though the file exists. In conditional exports Node takes the first matching condition top to bottom, so order `"types"` first and `"default"` last, or later branches (`"require"`/`"import"`) become unreachable. |
| Use `#`-prefixed subpath imports for internal modules | Map `#utils` via the package's `"imports"` field instead of `../../../util`; the map is scope-local and monorepo-safe. ESM requires explicit file extensions (`import './x.js'`, not `'./x'`). |
| Beware the dual-package hazard | When `"import"` and `"require"` resolve to different files, each loader evaluates its own copy, duplicating singleton state and breaking `instanceof`. Collapse shared-state packages to one implementation. |
| Always prefix built-ins with `node:` | Import `node:fs`, `node:crypto`, `node:test`. The prefix cannot be shadowed by a userland package of the same name and is mandatory for newer modules like `node:test`. |
| Use native `fetch`, no `node-fetch`/`axios` | `fetch`, `Headers`, `Request`, `Response`, `FormData`, and `WebSocket` are global and stable (fetch since 18, WebSocket client on by default since 22). Also prefer in-runtime `structuredClone`, `Array.fromAsync`, `Object.groupBy`, and `fs.glob` (22) over a polyfill. |
| Check the floor version before using an API | Read `engines`/`.nvmrc`. Even lines (22, 24) are LTS; odd lines (23) never reach LTS, so do not target them in production. Do not recommend an API unavailable on the floor. |

## Built-in tooling

| Practice | Detail |
|---|---|
| Test with `node:test` + `node:assert`, no runner dep | Stable since 20. Import from `node:test` and `node:assert/strict`; run `node --test`. Covers spies, method mocks, and fake timers, auto-restored at test end. Reach for Vitest/Jest only for their richer ecosystem. |
| Always `await` subtests | A parent `test()` does not wait for `t.test(...)` unless awaited; un-awaited subtests are cancelled and reported as failures. The single most common built-in-runner mistake. |
| Native TypeScript runs, with limits | Node strips types from `.ts` since 22.6 (`--experimental-strip-types`, default in 23.6+), but enums, parameter properties (`constructor(public id)`), and value-producing namespaces throw `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX` because they emit code; only `--experimental-transform-types` handles them. Set tsconfig `erasableSyntaxOnly` + `verbatimModuleSyntax` to catch these at edit time (Node ignores tsconfig at runtime), and write `import type` for type-only imports. |
| Speed up startup with the compile cache | `NODE_COMPILE_CACHE=<dir>` (or `module.enableCompileCache()`) persists V8 bytecode across restarts; prefer the env var so it reaches preloads and CLIs. Set `NODE_DISABLE_COMPILE_CACHE=1` for coverage runs, since V8 coverage is imprecise on code deserialized from cache. |
| Use `--watch` and `node --run`, not `nodemon`/npm | `node --watch` restarts on change; `node --run <script>` runs a `package.json` script without spawning npm. `--require` preloads run before `--import`; use `--import` for ESM loader hooks. |

## Cancellation and timeouts

| Practice | Detail |
|---|---|
| Cancel async work with `AbortController` | Pass `controller.signal` to `fetch`, `fs.promises`, timers, and streams; `controller.abort()` cancels. The standard mechanism, replacing ad-hoc flags. |
| Time out with `AbortSignal.timeout(ms)` | `fetch(url, { signal: AbortSignal.timeout(5000) })`. Aborted work rejects with an `AbortError`; branch on `err.name === 'AbortError'`, not the message. |
| Combine signals with `AbortSignal.any([...])` | Merge a request signal and a timeout signal so either cancels (since 20). A `Promise.race` timeout does NOT cancel the slow operation; pair it with an `AbortController` or it leaks the loser. |
| Sleep with `node:timers/promises` | `await setTimeout(1000, undefined, { signal })` is a cancellable promise-based delay. |

## Event loop and scheduling

| Practice | Detail |
|---|---|
| Never block the event loop | One thread serves all connections, so any long synchronous operation (sync I/O, a CPU loop, a large `JSON.parse`) stalls every request until it returns. The defining runtime constraint. |
| No sync `fs` in a request path | Use `fs.promises`; `readFileSync`/`writeFileSync` hold the thread for the whole OS call. Sync is fine only in startup or CLI scripts doing nothing concurrently. |
| Offload CPU work to `worker_threads` | Hashing, image processing, large compression belong in `node:worker_threads`; inline they freeze handling for all clients. |
| Size pools with `os.availableParallelism()`, not `os.cpus().length` | `availableParallelism()` respects cgroup/container CPU quotas; `cpus().length` reports the host's inventory (e.g. 64) and causes thread thrashing in a 2-CPU container. |
| Mind the libuv thread pool (default 4) | Filesystem, `dns.lookup`, `crypto`, and `zlib` share one global 4-thread pool (network sockets do not), so a slow `fs` op can starve `crypto.pbkdf2` auth latency. Raise `UV_THREADPOOL_SIZE` before the first async I/O if measured pressure justifies it. |
| Prefer `queueMicrotask`/`setImmediate` over `process.nextTick` | The nextTick queue drains completely between every loop phase, so recursive nextTick starves timers and I/O (nextTick is now documented "legacy"). Inside an I/O callback `setImmediate()` reliably fires before the next timer; use it to yield between large batches. |
| Detect stalls with `monitorEventLoopDelay()` | Use `perf_hooks.monitorEventLoopDelay()` rather than a manual `setInterval` drift hack; note GC stop-the-world pauses show up as the same tail-latency spikes. |

## Buffers and binary data

| Practice | Detail |
|---|---|
| Prefer `Buffer.alloc`; `allocUnsafe` returns uninitialized memory | `allocUnsafe(n)` hands back un-zeroed bytes that may contain old data (keys, tokens from a prior request); only use it if you overwrite every byte before any read, otherwise `Buffer.alloc(n)`. Never use the deprecated `new Buffer()`. |
| A slice/subarray is a view, not a copy | `buf.subarray()`/`slice()` alias the parent's memory, so mutating the view mutates the original, and a retained tiny view keeps the entire parent backing buffer alive (a real leak). Copy with `Buffer.from(buf.subarray(s, e))` for anything stored in a cache, closure, or Map, or crossing an async boundary. |
| Account for off-heap Buffer memory | Buffer bytes live outside the V8 heap and appear in `process.memoryUsage().external`/`.arrayBuffers`, not `heapUsed`; `--max-old-space-size` does not bound them, so a process can exhaust RAM with a small-looking heap. Monitor `rss`, `external`, and `arrayBuffers` together (rising `arrayBuffers` with a flat heap signals retained views). |
| Decode chunked text with `StringDecoder` | A multibyte UTF-8 character split across stream chunks corrupts if each chunk is `toString()`'d independently; `node:string_decoder` buffers the partial sequence across chunks. Read binary with no encoding arg; invalid bytes decoded as UTF-8 become `�` irreversibly. |
| Size text buffers with `Buffer.byteLength` | `string.length` counts UTF-16 code units, not bytes; use `Buffer.byteLength(str, 'utf8')`. For wire protocols use explicit `readUInt16BE`/`writeUInt16BE` (TypedArray views use platform-native endianness). |

## Filesystem

| Practice | Detail |
|---|---|
| Close every `FileHandle` in `finally` (or `await using`) | A `FileHandle` from `fs/promises.open()` is not reclaimed promptly by GC; leaks accumulate to a process-wide `EMFILE`. Use `await using fh = await open(...)` (Symbol.asyncDispose, 24.2+) or a `finally { await fh.close() }`. |
| Write files atomically: temp then rename | Write to a temp file in the SAME directory, then `rename()` over the target, so readers see old-or-new, never partial (the default `'w'` truncates first, so a mid-write crash leaves an empty file). `rename()` is atomic only within one filesystem: a temp in `os.tmpdir()` fails with `EXDEV` when `/tmp` is a separate mount (common in Docker), so keep the temp adjacent to the target. |
| Fsync when durability matters | A resolved `write`/`writeFile` is not yet on disk; for ledgers and state call `fh.sync()` (or `{ flush: true }`, 20.10+), and fsync the parent directory after a rename for full crash safety. |
| Create exclusively with `'wx'`, do not preflight with `fs.access` | The `'wx'` flag (`O_EXCL`) replaces a check-then-write TOCTOU race with one atomic op. `fs.access()` as a preflight is a TOCTOU antipattern (and checks real UID while ops use effective UID); just attempt the operation and branch on `err.code` (`ENOENT`/`EACCES`/`EEXIST`). |
| Treat `fs.watch` events as hints, not facts | They are coalesced, duplicated, and platform-divergent; watch the parent directory and filter by basename (inotify follows the old inode through an atomic rename and misses the new file), and debounce, since one editor save fires several events. Atomic writes surface as `'rename'`, not `'change'`. |
| Honor `bytesRead`/`bytesWritten` and bound fs concurrency | A raw `read()` can return fewer bytes than requested near EOF; consume only `buf.subarray(0, bytesRead)`. All async fs work shares the 4-thread pool, so fanning out tens of thousands of opens causes queuing and `EMFILE`; cap with a concurrency limiter (~50-100). |

## Streams and large data

| Practice | Detail |
|---|---|
| Stream large payloads, do not buffer | Reading a whole large file or response into memory grows the heap with input size; `createReadStream` processes bounded chunks at constant memory. |
| Use `pipeline()` from `node:stream/promises` | It propagates errors from every stage, applies backpressure, and destroys all streams on failure. A raw `.pipe()` chain leaks descriptors and ignores backpressure on error. |
| `pipeline()` cleans up streams, not application state | A failed pipeline can leave a partial file or partial DB write; pair it with the temp-then-rename or commit-on-success pattern. Stream instances are single-use after end/error, so retry by building fresh instances from a factory, not by reusing them. |
| Backpressure: `write()`/`push()` returning `false` is advisory | The chunk is still buffered (peak memory is roughly 2x `highWaterMark`), so do not assume HWM caps memory. On `false`, pause the source and resume on a single `drain` (`.once`, never `.on`); never run two concurrent writers on one writable, since `drain` wakes them all. In `objectMode`, `highWaterMark` counts objects (default 16), not bytes. |
| Iterate readables with `for await`, but mind early exit | `for await (const chunk of readable)` integrates with try/catch; pass an `AbortSignal` to stop. Breaking or returning early destroys the stream, to peek without destroying use `readable.iterator({ destroyOnReturn: false })`. |
| In a custom transform, call the callback exactly once and implement `_flush` | A returned promise from `_transform`/`_read` is not awaited; a missed `callback` hangs the stream forever. If the transform buffers partial state (lines, frames), `_flush` must emit the remainder or it is silently dropped at EOF. |
| For file-to-file copies, use `copyFile`, not stream-through-buffers | `createReadStream().pipe(dest)` does ordinary `write()` syscalls (no kernel `sendfile`); `copyFile(src, dst, COPYFILE_FICLONE)` uses a reflink with silent fallback. |
| Attach an `error` handler to any standalone stream | A `Readable`/`Writable` not wrapped by `pipeline()` must handle `error`; an unhandled stream error crashes the process. |

## EventEmitter

| Practice | Detail |
|---|---|
| An unhandled `'error'` event crashes the process | Any failable emitter (server, socket, stream, child process) MUST have an `'error'` listener, or an `EADDRINUSE`-class failure takes the process down. |
| `emit()` is fully synchronous | Listeners run on the current stack in registration order, so CPU work in a listener blocks the loop and stalls the source; keep listeners light. |
| Route async-listener rejections | A rejecting async listener silently becomes an unhandled rejection unless the emitter is constructed `new EventEmitter({ captureRejections: true })`, which sends it to the `'error'` handler. |
| Treat `MaxListenersExceededWarning` as a leak alarm | The warning at the 11th listener usually means a listener is added per request without removal; fix the leak (remove via `off()`/cleanup) rather than raising `setMaxListeners`. Prefer `events.once(emitter, evt)` and `events.on(emitter, evt, { signal })`, which self-clean. |

## Process lifecycle and shutdown

| Practice | Detail |
|---|---|
| Shut down in the right order on SIGTERM | Stop accepting work (`server.close()`), drain in-flight requests, then close DB/Redis, then set `exitCode`. Closing the DB before requests finish turns a graceful shutdown into a cascade of errors. Also `child.kill()` spawned children (else they reparent to init and leak). |
| A signal handler replaces Node's default exit | Installing any SIGTERM/SIGINT listener removes the default `128+signo` exit, so the process keeps running (and ignores Ctrl+C) unless your handler explicitly exits. As container PID 1, terminating signals are not applied without a handler, so run with `--init`/tini. Bound the drain with a force-exit timer so a stuck connection cannot block a rolling deploy. |
| Set `process.exitCode`, avoid `process.exit()` | `process.exit()` truncates pending async work and unflushed stdout/logs (libuv callbacks never fire); set `exitCode` and let the loop drain. Reserve explicit `process.exit()` for fatal startup failures and the shutdown timeout. Emit honest exit codes; orchestrators restart on any non-zero. |
| Log `unhandledRejection`/`uncaughtException`, then crash | After either fires the process is in an unknown state; log, then exit so the supervisor restarts cleanly. Do not resume from the handler. |
| `.unref()` background timers and handles | A housekeeping `setInterval`, monitor socket, or open handle keeps the process alive; `.unref()` lets it exit once real work is done. `process.getActiveResourcesInfo()` enumerates what is still keeping the loop alive when a shutdown hangs. |
| Read `process.env` once at startup | Each access crosses into native code (slow in hot loops) and every value is a string, so `'false'` is truthy: parse explicitly (`=== 'true'`). Watch stdout: it is async to a pipe on POSIX, so a final line is lost if you `process.exit()` right after writing, and downstream early-exit raises `EPIPE`, which a producer CLI should treat as a clean exit. In containers use `process.constrainedMemory()`, since `os.totalmem()` reports host memory. |

## Networking

| Practice | Detail |
|---|---|
| Prefer `dns.resolve*` over `dns.lookup`, and cache | `dns.lookup` (used by `http`/`fetch` under the hood) runs `getaddrinfo` on the libuv pool, competing with fs/crypto; a burst starves them. `dns.resolve*` uses c-ares off-pool. Node does no DNS caching by default, so cache application-side and honor the record TTL; after a deploy uncached lookups return mixed answers. |
| `socket.setTimeout()` only notifies | The `'timeout'` event does not close the socket; you must `socket.destroy()`. A handler that merely logs leaks descriptors under steady traffic. App timeout, TCP keep-alive (`setKeepAlive`), and HTTP keep-alive are three independent layers. |
| Pool connections, and account for TIME-WAIT | Repeated short-lived connections pile up TIME-WAIT sockets that exhaust ephemeral ports; use a keep-alive `Agent`. Pooling also hides DNS changes (the pool serves old IPs until sockets retire), so a migration needs a lowered TTL plus active draining, `server.close()` only stops new accepts; track and `end()` existing sockets. |
| Frame your own messages; disable Nagle for small ones | TCP does not preserve `write()` boundaries, so a protocol needs explicit framing (length prefix or delimiter). For small latency-sensitive messages use `setNoDelay(true)`, but the real fix is batching writes app-side. A successful `write`/`send` means the local kernel accepted the bytes, never that the peer received them. |
| Handle errors on accepted sockets | A missing socket-level `'error'` handler crashes the process; server-level and socket-level errors are separate emitters. Do per-connection cleanup (clear timers, drop from tracking sets) in `'close'`, not `'end'`. |

## Configuration and security

| Practice | Detail |
|---|---|
| Parse `process.env` once into validated config | Validate shape, types, and required keys with a schema (zod/valibot) at startup, before the server binds, then pass a frozen config. A misconfigured deploy should crash immediately, not on the first request. |
| Use structured (JSON) logging | Emit machine-parseable JSON with a fast logger (pino), not `console.log` strings; include levels, request IDs, and fields. Never log secrets, tokens, or full PII. |
| Consider the permission model for untrusted code | Stable since 22.13/23.5: `node --permission` denies fs/child_process/worker/net, granted back via `--allow-*`. It is a seat belt, not a sandbox for hostile code, is NOT inherited by `worker_threads`, and follows symlinks. |
| Do not leak internals in errors, and audit deps | Stack traces, absolute paths, and connection strings in user-facing output expose internals; log internally, return a generic message. Run `npm audit` in CI and pin exact versions for auth/crypto packages. |

## Gotchas

- A parent `test()` does not await `t.test()` subtests; un-awaited subtests are cancelled and fail.
- `Buffer.allocUnsafe` and a retained `subarray()` view both leak: uninitialized bytes can expose old data, and a small view pins its whole parent buffer.
- `process.exit()` drops queued stdout and pending async; set `process.exitCode` instead.
- An emitter `'error'` event with no listener crashes the process; add one to every server, socket, and stream.
- A `FileHandle` not closed leaks an fd to `EMFILE`; `rename()` across mounts fails with `EXDEV`.
- ESM has no `__dirname`; use `import.meta.dirname`. ESM imports need explicit file extensions.
- `--env-file` does not validate, does not expand `$VAR`, does not coerce types, and an already-set parent variable blocks the file value.
- The permission model is not inherited by `worker_threads` and follows symlinks.
- Tuning `UV_THREADPOOL_SIZE` does nothing for network throughput; sockets do not use the pool.
- Edge runtimes (Cloudflare Workers, Vercel Edge) are not full Node; `node:fs` and parts of `node:crypto` may be absent.
- Do not implement runtime patterns from memory; stream, fs, crypto, and process APIs change across majors. Verify the signature at nodejs.org against the floor version.

## Sources

- [Node.js API docs](https://nodejs.org/api/) - official reference; authoritative on `node:test`, `permissions`, `stream/promises`, `process`, `fs`, `dns`, and CLI flags. Check the version selector against your floor.
- [Node.js releases/LTS schedule](https://nodejs.org/en/about/previous-releases) - official; what is stable vs experimental per version and which lines reach LTS.
- [The NodeBook](https://www.thenodebook.com/) - deep, architecture-first treatment of the Node runtime; the basis for the buffers (off-heap accounting, retained views), filesystem (FileHandle leaks, atomic writes, TOCTOU), stream-internals, event-loop scheduling, EventEmitter, and networking depth here.
- [Node.js Best Practices (goldbergyoni)](https://github.com/goldbergyoni/nodebestpractices) - the most-cited community best-practices list; async error handling, graceful shutdown, operational vs programmer errors.
- [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html) - OWASP; dependency auditing, not leaking internals, safe error handling.

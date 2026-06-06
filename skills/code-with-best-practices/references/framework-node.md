Apply these practices whenever planning, writing, or reviewing Node.js code.

## Contents

- Event Loop and Blocking
- Streams and Large Data
- Process Lifecycle and Graceful Shutdown
- Environment and Configuration
- Async Error Propagation
- Dependency Hygiene
- Runtime Gotchas
- Source Verification

## Event Loop and Blocking

| Practice | Detail |
|---|---|
| Never block the event loop | A single Node process serves all connections from one thread, so any long synchronous operation (sync I/O, CPU-heavy loops, large JSON.parse) stalls every other request until it finishes. This is the defining constraint of the runtime. |
| Prefer async file APIs over sync | Use `fs.promises` over `readFileSync`/`writeFileSync` in any code that serves requests, because the sync variants hold the thread for the entire OS operation while async variants yield. Sync is acceptable only in startup or CLI scripts that do nothing concurrently. |
| Offload CPU-bound work to worker threads | Hashing, image processing, compression of large payloads, and similar CPU work belong in `worker_threads` or a child process, since running them inline freezes request handling for all clients. |
| Parallelize independent async work | Use `Promise.all()` for operations with no data dependency between them, because awaiting them one at a time wastes idle I/O time and inflates latency for no benefit. |

## Streams and Large Data

| Practice | Detail |
|---|---|
| Stream large payloads instead of buffering | Reading a whole large file or response into memory grows heap usage with input size and risks OOM under load, whereas `createReadStream` processes bounded chunks at constant memory. |
| Use `stream.pipeline()` over `.pipe()` | `pipeline()` from `node:stream/promises` propagates errors from every stage, applies backpressure, and destroys all streams on failure, while a raw `.pipe()` chain leaks file descriptors and sockets when a stage errors. |
| Attach an error listener to every standalone stream | Any `Readable` or `Writable` not wrapped by `pipeline()` must handle its `error` event, because an unhandled stream error is thrown and crashes the process. |
| Iterate readables with `for await` | `for await (const chunk of readable)` integrates with normal try/catch and is harder to get wrong than manual `data`/`end`/`error` wiring. |

## Process Lifecycle and Graceful Shutdown

| Practice | Detail |
|---|---|
| Handle SIGTERM and SIGINT for clean shutdown | Orchestrators (Docker, Kubernetes, systemd) send SIGTERM and expect the process to stop accepting work, drain in-flight requests, then exit, so dropping these signals causes killed requests and corrupted state on every deploy. |
| Set `process.exitCode`, do not call `process.exit()` in library code | `process.exit()` terminates immediately and truncates pending stdout, logs, and I/O flushes, while setting `exitCode` lets the loop drain naturally. Reserve explicit `process.exit()` for top-level CLI entry points. |
| Bound the shutdown with a timeout | Wrap drain logic in a timer that force-exits if cleanup hangs, because a stuck connection or pending promise can otherwise leave the process alive indefinitely and block a rolling deploy. |
| Call `.unref()` on background timers | `setInterval`/`setTimeout` handles used for housekeeping keep the process alive after real work is done; `.unref()` lets the process exit once nothing meaningful remains. |
| Log `uncaughtException` and `unhandledRejection`, then exit | After either fires the process is in an unknown state, so the safe response is to log for diagnosis and exit to let the supervisor restart cleanly rather than continue serving from corrupted state. |

## Environment and Configuration

| Practice | Detail |
|---|---|
| Never read `process.env` inline | Every `process.env` value is `string | undefined`, so reading it at the point of use scatters string coercion and missing-value bugs through the code. Parse it once into a typed config object instead. |
| Validate and fail fast at startup | Validate all env and config (shape, types, required keys) before the server binds a port, so a misconfigured deploy crashes immediately and visibly instead of failing on the first request that touches the missing value. |
| Do not commit secrets or `.env` files | Secrets in the repo leak through git history and clones; inject them at runtime via the environment or a secrets manager and keep `.env` out of version control. |
| Treat config as immutable after load | Read config into a frozen object at startup and pass it explicitly, because mutating shared config at runtime creates ordering bugs that are hard to reproduce. |

## Async Error Propagation

| Practice | Detail |
|---|---|
| Handle every promise rejection | An unhandled rejection crashes the process on modern Node, so each `async` call must be awaited inside try/catch or have a `.catch()`. A fire-and-forget promise with no handler is a latent crash. |
| Never swallow errors in an empty catch | An empty `catch` hides failures and produces silent data loss; always log, rethrow, or translate the error into a caller-visible result. |
| Do not leak internal details to users | Stack traces, absolute paths, and connection strings in user-facing output expose internals to attackers; log them internally and return a safe generic message. |
| Promisify legacy callback APIs | Wrap older callback-style APIs with `util.promisify` so their errors flow through the same async/await path, rather than mixing callback error handling with promise handling. |

## Dependency Hygiene

| Practice | Detail |
|---|---|
| Prefer `node:` built-ins with the protocol prefix | Use `node:fs`, `node:crypto`, `node:path`, and similar over npm wrappers, importing with the explicit `node:` prefix. Built-ins add no install cost, no supply-chain risk, and the prefix removes ambiguity with user-land packages. |
| Treat each dependency as a liability | You own your entire transitive tree, including packages you never chose, so every addition widens attack surface and breakage risk. Justify necessity before adding one. |
| Commit the lockfile | Commit `package-lock.json`, `pnpm-lock.yaml`, or `yarn.lock` so installs are reproducible across machines and CI, and so a mutated upstream version cannot silently enter a build. |
| Pin security-sensitive packages | Use exact versions (no `^` or `~`) for auth, crypto, and authorization packages, because a caret range can pull a compromised patch release into those exact code paths automatically. |
| Audit on every CI build | Run `npm audit` (or the equivalent) in CI and resolve high and critical findings before merge, so known vulnerabilities are caught at the gate rather than in production. |

## Runtime Gotchas

| Gotcha | Resolution |
|---|---|
| The libuv thread pool defaults to 4 | Filesystem, `dns.lookup`, and crypto/zlib work share a 4-thread pool, so a workload with many concurrent such operations serializes behind it. Raise `UV_THREADPOOL_SIZE` before the first async I/O call if needed. |
| Network I/O does not use the thread pool | TCP and HTTP sockets use the OS non-blocking facilities (epoll/kqueue/IOCP) directly, so the thread pool is irrelevant to network scaling. Do not tune `UV_THREADPOOL_SIZE` expecting more network throughput. |
| `dns.lookup` blocks a pool thread | `dns.lookup` calls `getaddrinfo` on the thread pool, one thread per call, so high-volume resolution starves the pool. Use `dns.resolve` instead, which uses non-blocking OS DNS. |
| Edge runtimes are not full Node | V8-isolate environments (Cloudflare Workers, Vercel Edge) omit many APIs, so `node:fs` and parts of `node:crypto` may be absent. Confirm availability against the target runtime before relying on a built-in. |

## Source Verification

Do not implement Node.js runtime patterns from memory; training data carries outdated APIs from older versions.

| Practice | Detail |
|---|---|
| Verify against official docs | Check the API signature and behavior at nodejs.org for streams, crypto, worker threads, and process handling, because these surfaces change across major versions. |
| Check the target version first | Read `engines` in `package.json` or `.node-version` to find the minimum supported version, and do not recommend an API unavailable there. |
| Flag unverified patterns explicitly | If you cannot confirm a behavior in official docs, say so plainly rather than presenting a guess as fact, so the developer knows to verify before shipping. |

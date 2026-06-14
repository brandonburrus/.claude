Apply these practices whenever planning, writing, or reviewing JavaScript code. Targets ES2023+ on modern Node (20+) and evergreen browsers (version-specific items are flagged). Generic clean-code and naming rules live in CLAUDE.md; this reference is the JavaScript-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Modules](#modules)
- [Equality and coercion](#equality-and-coercion)
- [Nullish operators](#nullish-operators)
- [Modern syntax and data](#modern-syntax-and-data)
- [Async and errors](#async-and-errors)
- [Node and browser](#node-and-browser)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Modules

| Practice | Detail |
|---|---|
| ESM only, never CommonJS | Use `import`/`export`, not `require()`/`module.exports`. Mixing the two breaks resolution and produces interop surprises. A package is ESM via `"type": "module"` in package.json. (Node now supports `require()` of synchronous ESM on 22+, but authoring in ESM is the target.) |
| Named exports over default | `export const parse = ...` beats `export default`, giving uniform names across imports, safer renames, and better auto-import. |
| Explicit `.js` extensions in import paths | `import { parse } from './parser.js'`, not `'./parser'`. Both Node ESM and browsers require the extension, so omitting it fails at runtime even when a bundler tolerated it. |
| Static imports by default, dynamic `import()` only for conditional or split loading | Static imports keep the dependency graph visible to bundlers and analyzers; reserve `await import()` for runtime-chosen paths and code splitting. |
| Top-level `await` is allowed in modules | `await` works at module top level (ESM only) for init-time async (config load, dynamic import). It blocks the importing module's evaluation, so keep it to genuine startup work, not per-request paths. |

## Equality and coercion

| Practice | Detail |
|---|---|
| Always `===` / `!==` | Loose `==` coerces and yields traps: `0 == ''`, `'0' == false`, `[] == ![]`, and `null == undefined` are all true. The one sanctioned `==` is `x == null` to test null-or-undefined in a single check. |
| `typeof` for primitives, not `instanceof` | `typeof v === 'string'` catches literals; `v instanceof String` matches only boxed objects and misses every string literal. |
| `Array.isArray()` for arrays | `typeof []` is `'object'`, so only `Array.isArray()` reliably distinguishes an array. |
| `Number.isFinite` / `Number.isNaN`, never the globals | Global `isNaN('foo')` is `true` because it coerces first; the `Number.*` forms do not coerce. `NaN !== NaN`, so compare with `Number.isNaN`, never `=== NaN`. |
| Do not lean on truthiness for `0`/`''` | `if (count)` and `value || fallback` both treat `0` and `''` as absent; use explicit `!= null` or `??` when those are valid values. |

## Nullish operators

| Practice | Detail |
|---|---|
| `??` for defaults, not `||` | `??` falls back only on `null`/`undefined`; `||` falls back on any falsy value, so `count || 10` wrongly replaces a real `0`. Use `??` whenever `0`, `''`, or `false` are legitimate. (ES2020) |
| Parenthesize `??` with `&&`/`||` | `a || b ?? c` is a `SyntaxError` by design; the mix is ambiguous, so write `(a || b) ?? c` explicitly. |
| `?.` for genuinely optional access only | `user?.address?.city` short-circuits to `undefined` instead of throwing. Do not mask a property you expect to always exist, which only hides the real bug; and `obj?.a.b` still throws on `.b` if `a` is nullish. |
| `??=`, `||=`, `&&=` for conditional assignment | `config.timeout ??= 5000` sets only when nullish; `||=`/`&&=` mirror the falsy/truthy variants. Cleaner than the `x = x ?? y` rewrite. (ES2021) |

## Modern syntax and data

| Practice | Detail |
|---|---|
| `const` by default, `let` to reassign, never `var` | `var` is function-scoped and hoists, producing closure-in-loop and temporal bugs that block scoping avoids. |
| `for...of` for values, never `for...in` for arrays | `for...in` walks enumerable keys including inherited ones and gives string indices; `for...of` iterates values directly. |
| Array methods for transforms; `map`/`reduce` to build, not `forEach` | `map`, `filter`, `find`, `some`, `every`, `reduce` state intent; `forEach` returns `undefined` so producing a value with it forces external mutation. |
| Immutable copying methods (ES2023) | `toSorted`, `toReversed`, `toSpliced`, and `with(i, v)` return a new array instead of mutating in place: safe for shared state and React. `toSorted()` still sorts lexicographically by default, so pass a comparator for numbers: `nums.toSorted((a, b) => a - b)`. |
| `at()`, `findLast`, `findLastIndex` (ES2023) | `arr.at(-1)` reads from the end without `length - 1`; `findLast`/`findLastIndex` search from the tail. |
| `Object.groupBy` / `Map.groupBy` (ES2024, Node 20+) | `Object.groupBy(items, x => x.type)` returns a null-prototype object keyed by string; use `Map.groupBy` when keys are non-string. Polyfill or check support for older targets. |
| `structuredClone()` for deep copies | Correctly clones nested objects, arrays, `Map`, `Set`, `Date`, typed arrays, and cycles. It cannot clone functions, DOM nodes, or class prototypes (throws `DataCloneError`) and drops the prototype chain. Still better than `JSON.parse(JSON.stringify(x))`, which silently drops functions, `undefined`, and turns `Date` into a string. (Node 17+) |
| `Map`/`Set` for dynamic keyed collections | `Map` gives O(1) any-typed keys, preserves insertion order, and avoids the prototype-key collisions (`__proto__`, `constructor`) and string-coercion of plain objects. Use objects for fixed, known shapes. |
| `Array.from()` / spread for array-likes | `NodeList`, `arguments`, and other iterables lack array methods until converted; `Array.from(set, fn)` also maps in one pass. |

## Async and errors

| Practice | Detail |
|---|---|
| One async style per function | Pick `async/await` with `try/catch`; mixing in `.then().catch()` fragments control flow and hides error paths. |
| `Promise.all` to parallelize independent awaits | Sequential `await a; await b` serializes unrelated work; `await Promise.all([a, b])` runs them concurrently. `all` rejects on the first failure. |
| `Promise.allSettled` when partial failure is acceptable | It resolves with every `{status, value/reason}` so one rejection does not discard the successful results; pair with `Promise.any` for first-success. |
| `Promise.all` rejects fast but does not cancel the losers | The other operations keep running and consuming resources, and only the first rejection reason survives. Use `allSettled` for full visibility, `any` for first-success (read `AggregateError.errors`). A `Promise.race` timeout likewise leaves the slow operation running, so pair it with an `AbortController`. |
| Array iteration methods ignore async callbacks | `arr.forEach(async ...)`, `.map`, `.filter`, `.some`, `.sort` do not await the returned promise: `forEach` fires them unawaited, `filter` treats the promise as always truthy, `sort` compares promises instead of numbers. Use `for...of` for sequential work or `await Promise.all(arr.map(async ...))` for concurrent. |
| `return await` inside `try`/`catch`/`finally` | A bare `return promise` settles after `finally` has run and escapes the local `catch`; use `return await promise` when the error must be caught here or cleanup ordered correctly. Outside a try block the bare form is fine. |
| Keep an async API consistently async | A callback or promise API that sometimes returns synchronously and sometimes defers (the "Zalgo" hazard) produces bugs that surface only intermittently; if any path defers, defer them all (wrap the immediate path in `queueMicrotask`). |
| `for await...of` releases resources on early exit | Breaking, returning, or throwing out of a `for await` loop calls the iterator's `return()`, closing the underlying source; in a custom async generator put release in `finally` so it also runs on early exit. |
| Never swallow errors | An empty `catch` turns failures into silent corruption; log, rethrow, or handle. Subscribe to a stream/EventEmitter `'error'` event directly, as those do not reach `try/catch`. |
| Typed error classes for domain errors | Extend `Error`, set `this.name`, so callers branch on `instanceof` instead of parsing messages. |
| Check `response.ok` after `fetch` | `fetch` resolves even on 4xx/5xx, so without `if (!response.ok)` the code parses an error body as valid data. |
| `AbortController` for cancellation | Pass `{ signal }` to `fetch` and timers; catch the rejection by `err.name === 'AbortError'` so an intentional cancel is not logged as a network failure. |

## Node and browser

| Practice | Detail |
|---|---|
| Never extend native prototypes | Adding to `Array.prototype` or `Object.prototype` leaks into every object, breaks `for...in`, and collides with future spec methods (`Array.prototype.flat` broke sites that had monkey-patched it). |
| Never `eval()` or `new Function(str)` | Both execute arbitrary strings with full scope access; use a lookup object or `Map` for dynamic dispatch. |
| Validate input at boundaries | Without static types, nothing stops malformed data flowing inward; check `JSON.parse` output, HTTP bodies, and `process.env` where untrusted data enters. Wrap `JSON.parse` in `try/catch` (it throws `SyntaxError`). |
| Guard against prototype pollution | Merging untrusted objects can overwrite `__proto__`/`constructor`; reject those keys or use `Object.create(null)` dictionaries. |
| `crypto.randomUUID()` and `crypto.getRandomValues()` for IDs/tokens | `Math.random()` is not cryptographically secure and can collide; use the crypto API for anything security-bearing. |
| Subscribe to `unhandledRejection`; handle `SIGTERM`/`SIGINT` | Node exits on unhandled rejections, so log and exit deliberately; trap signals to drain connections on deploy, with a forced-exit timeout backstop. |
| `textContent` over `innerHTML` for user data | `innerHTML` parses and can execute injected markup (XSS); `textContent` inserts inertly. Use DOMPurify only when rich HTML is genuinely required. |
| `AbortController` `{ signal }` for listener cleanup | One `abort()` removes every listener registered with that signal, beating manual `removeEventListener` bookkeeping. |

## Gotchas

- `||` swallows valid `0`, `''`, and `false`; reach for `??` when those are legitimate values.
- `[].sort()` and `[].toSorted()` sort lexicographically by default: `[1, 10, 2].toSorted()` is `[1, 10, 2]`; pass `(a, b) => a - b`.
- `JSON.parse(JSON.stringify(x))` drops functions and `undefined`, stringifies `Date`, and throws on cycles; use `structuredClone`.
- `a || b ?? c` and `a && b ?? c` are syntax errors without parentheses.
- `obj?.a.b` still throws if `a` is nullish; optional chaining only guards the link it is attached to.
- `for...in` over an array yields string keys and inherited enumerable properties; use `for...of` or array methods.
- Missing the `.js` extension in an import works under some bundlers but crashes in raw Node ESM and browsers.
- `array.map(async ...)` returns an array of promises, not values; `forEach`/`filter`/`sort` ignore async callbacks entirely.
- `.then(onFulfilled, onRejected)` does not catch a throw from inside its own `onFulfilled`; a chained `.catch()` does.

## Sources

- [MDN Web Docs: JavaScript reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference) - the canonical, vendor-neutral browser reference; pages cited for [nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing), [structuredClone](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/structuredClone), [toSorted](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSorted), and [Object.groupBy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy).
- [TC39 proposals](https://github.com/tc39/proposals) and the [ECMAScript spec](https://tc39.es/ecma262/) - the standards body and authoritative source for what ES2023/ES2024 added (change-array-by-copy, array grouping).
- [Node.js best-practices](https://github.com/goldbergyoni/nodebestpractices) (goldbergyoni) - the most-starred Node practices repo; error handling, unhandledRejection, config validation, graceful shutdown.
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html) - a major maintained style guide; ESM, `const`/`let`, no prototype extension, equality conventions.
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) - widely adopted community style guide; modern syntax, array methods, and idioms.
- [You Don't Know JS Yet](https://github.com/getify/You-Dont-Know-JS) (Kyle Simpson) - deep, respected treatment of coercion, `==` vs `===`, and type gotchas.
- [V8: top-level await](https://v8.dev/features/top-level-await) - the engine team's explainer on top-level await semantics and module-blocking behavior.

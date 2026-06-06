Apply these practices whenever planning, writing, or reviewing JavaScript code.

## Module System (ESM Only)

| Practice | Detail |
|---|---|
| Use ESM exclusively | Use `import`/`export` only, never `require()`, `module.exports`, or `exports`. Mixing module systems breaks resolution and produces interop surprises across Node.js and browsers. |
| Named exports only | Prefer `export const myFunc = () => {}` over `export default`. Named exports give explicit API surfaces, better autocomplete, and safer renames across files. |
| Explicit file extensions in imports | Write `import { parse } from './parser.js'`, not `'./parser'`. Browser and Node.js ESM both require the extension, so omitting it fails at runtime. |
| No barrel files | Do not create `index.js` files that re-export from other modules. Barrels obscure an export's origin, invite circular dependencies, and defeat tree-shaking. |
| Reserve dynamic `import()` for conditional loading | Use it only for runtime-determined paths or code splitting. Static imports elsewhere let bundlers and analyzers see the dependency graph and optimize it. |

## Equality and Type Checks

| Practice | Detail |
|---|---|
| Always use `===` and `!==` | Loose equality coerces types and yields traps like `0 == ''`, `null == undefined`, and `'0' == false` all being true. Strict equality avoids these silent conversions. |
| Use `typeof` for primitive checks | Prefer `typeof value === 'string'` over `value instanceof String`, because `instanceof` misses primitive literals and matches only boxed objects. |
| Use `Array.isArray()` for arrays | `typeof []` returns `'object'`, so only `Array.isArray()` distinguishes an array from other objects reliably. |
| Use `Number.isFinite()` and `Number.isNaN()` | The global `isNaN()` and `isFinite()` coerce their argument first, producing wrong results for non-numbers. The `Number.*` forms do not coerce. |

## Coercion and Runtime Validation

| Practice | Detail |
|---|---|
| Validate input at system boundaries | Without a type system, nothing stops malformed data from flowing inward. Check types, lengths, and formats where untrusted data enters so failures surface early and locally. |
| Wrap `JSON.parse` in try/catch | Malformed JSON throws `SyntaxError`. Handling it explicitly keeps a bad payload from crashing the process. |
| Guard against prototype pollution | Merging untrusted objects via spread or `Object.assign` can overwrite `__proto__`, `constructor`, or `prototype`. Filter those keys or use `Object.create(null)` for dictionaries. |
| Avoid implicit coercion in conditionals | Relying on truthiness conflates `0`, `''`, `null`, and `undefined`. Compare explicitly (`value == null` only for the null/undefined pair) so intent and edge cases are visible. |

## Modern Syntax and Semantics

| Practice | Detail |
|---|---|
| Use `const` by default, `let` only when reassigning | Never use `var`: it has function scope and hoists, which creates surprising temporal and scoping bugs that block-scoped declarations avoid. |
| Declare variables at point of use | Declaring where a value is first assigned, rather than hoisting to the function top, keeps each name's lifetime and meaning close to its use. |
| Use `for...of`, not `for...in`, for values | `for...in` iterates keys including inherited enumerable ones, so it can pick up unexpected properties. `for...of` iterates the values directly. |
| Use array methods for transformations | `map`, `filter`, `find`, `some`, `every`, and `reduce` express intent more directly than manual index loops and reduce off-by-one risk. |
| Avoid `forEach` when producing a value | `forEach` returns `undefined`, so building a result with it forces external mutation. Use `map` or `reduce` to return the new value directly. |
| Use `Array.from()` for array-likes | `NodeList`, `arguments`, and other iterables lack array methods until converted with `Array.from()` or spread, so calling `map` on them directly fails. |
| Use `structuredClone()` for deep copies | Spread is shallow and `JSON.parse(JSON.stringify(x))` drops functions and special types. `structuredClone()` correctly copies nested objects, Maps, Sets, and cycles. |

## Async and Error Handling

| Practice | Detail |
|---|---|
| Use `async/await` with `try/catch` consistently | Mixing `.then().catch()` and `await` in one function fragments the control flow and makes error paths hard to trace. Pick one style per function. |
| Never swallow errors | An empty `catch` hides bugs and turns failures into silent corruption. Always log, rethrow, or handle the error meaningfully. |
| Use structured error classes for domain errors | Extending `Error` with a named subclass and setting `this.name` enables `instanceof` discrimination, so callers can branch on error kind instead of parsing messages. |
| Check `response.ok` after `fetch` | `fetch` resolves even on 4xx and 5xx responses, so without an `if (!response.ok)` check the code parses an error body as if it were valid data. |
| Handle `AbortError` separately | When aborting a fetch via `AbortController`, catch the error by name so an intentional cancellation is not mistaken for a network failure. |

## DOM and Browser

| Practice | Detail |
|---|---|
| Use event delegation | One listener on a parent, matched with `event.target.matches('.selector')`, handles dynamically added children and avoids per-element listener overhead. |
| Use `AbortController` for listener cleanup | Registering listeners with `{ signal }` lets a single `abort()` remove them all, which is less error-prone than tracking individual `removeEventListener` calls. |
| Use `textContent`, not `innerHTML`, for user data | `innerHTML` parses and can execute embedded markup, opening an XSS hole. `textContent` inserts text inertly; use DOMPurify when rich HTML is genuinely required. |
| Use `requestAnimationFrame` for visual updates | It syncs work with the repaint cycle, whereas `setTimeout`/`setInterval` drift out of phase and cause jank and wasted frames. |

## Node.js Runtime

| Practice | Detail |
|---|---|
| Handle process signals for graceful shutdown | Listening for `SIGTERM` and `SIGINT` to close servers and flush buffers prevents dropped connections and corrupt state on deploy or restart. Add a forced-exit timeout as a backstop. |
| Register an `unhandledRejection` handler | Recent Node.js crashes the process on unhandled rejections by default, so logging and exiting deliberately gives controlled failure instead of an opaque crash. |
| Use streams for large data | `readFileSync` loads the whole file into memory and can exhaust it. `createReadStream` with pipes handles backpressure and bounds memory use. |
| Validate environment variables at startup | Reading `process.env` through a layer that throws on missing required values fails fast at boot instead of much later inside business logic. |
| Use `crypto.randomUUID()` for IDs | `Math.random()` is not cryptographically secure and can collide. `crypto.randomUUID()` produces unguessable, well-distributed identifiers. |

## Security

| Practice | Detail |
|---|---|
| Never use `eval()` or `new Function()` | Both execute arbitrary strings with full scope access, turning any injected input into code execution. Use validated lookups into objects or maps instead. |

## Performance

| Practice | Detail |
|---|---|
| Avoid object spread inside loops | `result = { ...result, [key]: value }` copies the whole object each iteration, making the loop O(n^2). Mutate in place and freeze afterward if immutability is needed. |
| Use `WeakMap`/`WeakRef` for caches keyed by objects | Entries are garbage collected once their keys are otherwise unreferenced, preventing the slow memory leaks that strong-keyed caches cause. |
| Lazy-initialize expensive values | Computing on first access rather than at module load avoids paying for work that may never be needed and shortens startup time. |
| Use `Map` and `Set` for dynamic collections | `Map` gives O(1) keyed access with any key type and preserves insertion order, outperforming plain objects under frequent dynamic insertion and deletion. |

## Testing

| Practice | Detail |
|---|---|
| Mock ESM modules before the imports that use them | Module mocks must be hoisted above imports so the runner intercepts resolution; placing them later means the real module loads first. |
| Test error paths explicitly | Verifying that functions throw the expected error type and message ensures failure behavior is intentional and stays covered against regressions. |
| Clean up state and mocks between tests | Clearing mocks and resetting shared state each test prevents one test's leftovers from silently determining another's outcome. |

Apply these practices whenever planning, writing, or reviewing TypeScript code.

## Type Safety

| Practice | Detail |
|---|---|
| Enable `"strict": true` in tsconfig | Strict mode catches whole classes of null and type errors at compile time. Do not silence checks with `// @ts-ignore` or `// @ts-nocheck` except in rare cases documented with a reason. |
| Type external data as `unknown`, then validate | Data from `JSON.parse`, HTTP responses, `process.env`, CLI arguments, DOM reads, and file contents has no guaranteed shape, so typing it `any` lets bad data flow unchecked through the program. Validate at the boundary before use. |
| Use `readonly` where mutation is unintended | Marking properties and parameters `readonly` communicates intent and lets the compiler prevent accidental mutation bugs that are otherwise silent. |
| Model variants with discriminated unions, not `as` | A discriminated union (`{ type: 'ok'; value: T } \| { type: 'error'; message: string }`) lets the compiler narrow safely, whereas `as` assertions bypass the type checker and hide mismatches until runtime. |
| Use `const` assertions and `satisfies` | `as const` freezes literals into their narrowest type for exhaustive unions, and `satisfies` validates a value against a type without widening it, so you keep both checking and precise inference. |

## Utility Types

Prefer built-in utility types over reimplementing the same transformation, because hand-rolled equivalents drift out of sync and obscure intent. Split a type into nested sub-types only when the domain structure warrants it, since aggressive splitting hides the shape and makes code completion harder to follow.

| Type | Use case |
|---|---|
| `Partial<T>` | All properties optional, useful for patch and update payloads. |
| `Required<T>` | All properties required, the inverse of `Partial`. |
| `Readonly<T>` | All properties `readonly` to prevent mutation. |
| `Pick<T, K>` / `Omit<T, K>` | Select or exclude a subset of properties without redefining the rest. |
| `Record<K, V>` | Map type with keys `K` and values `V`. |
| `NonNullable<T>` | Remove `null` and `undefined` from `T`. |
| `ReturnType<T>` / `Parameters<T>` | Extract a function's return type or parameter tuple to stay coupled to the source signature. |
| `Awaited<T>` | Unwrap a `Promise<T>` to `T`, recursively. |

## Callbacks and Overloads

| Practice | Detail |
|---|---|
| Type ignored callback returns as `void` | An `any` return lets a caller accidentally consume a value that was meant to be discarded, while `void` signals the intent and the compiler enforces it. |
| Make callback parameters non-optional when always supplied | An optional parameter implies the callback may be invoked with fewer arguments. If the caller always provides both, make both required since an implementor can always ignore a parameter. |
| Order specific overloads before general ones | TypeScript resolves the first matching overload, so a general signature placed first shadows a more specific one and makes it unreachable. |

## Function Design

| Practice | Detail |
|---|---|
| Each function does one thing | If describing a function needs the word "and", it does two things, which makes it harder to compose, test, and reason about. Split it. |
| Avoid flag parameters | A boolean that switches code paths means the function does two things; two named functions are clearer about which behavior the caller wants. |
| Keep functions short | Aim for roughly 5 to 10 lines, because longer functions usually hide extractable operations that deserve their own name and tests. |
| Prefer pure functions | When a return value depends only on inputs with no side effects, the function is trivial to test, compose, and memoize. |
| Centralize side effects at the boundaries | Keeping file I/O, network calls, and global mutation at the edges keeps core logic predictable and avoids shared mutable state scattered through the middle. |
| Use parameter defaults | A default value (`function logNumber(num = 25)`) is clearer than checking for `undefined` inside the body and keeps the call site simpler. |

## Naming and Readability

| Practice | Detail |
|---|---|
| Name for behavior, not implementation | `isLegalDrinkingAge(age)` survives a rule change that `isOverEighteen(age)` does not, because the name states the purpose rather than the current threshold. |
| Prefix booleans with `is` or `has` | `isActive` or `hasPermission` makes a boolean recognizable at a glance without checking its type or a comment. |
| Write identifiers in English | The language keywords are English, so mixing languages in identifiers makes code harder to search and excludes part of the team. |
| Avoid deep nesting | Logic nested past two or three levels is hard to follow; early returns, guard clauses, and extracted helpers flatten it. |
| Avoid global variables and functions | Globals share a scope with every module, creating hidden coupling. Prefer module-scoped constants and explicit dependency passing. |

## Code Structure

| Practice | Detail |
|---|---|
| Prefer named exports over default exports | Named exports rename safely, produce better auto-import suggestions, and avoid letting each consumer invent its own local name. |
| Avoid circular dependencies | Cycles signal a missing abstraction or wrong responsibility boundary and can break module initialization order. Detect them with a linter or `madge` in CI. |
| One concept per file | One primary export and one concern per file keeps code findable and avoids `utils.ts` catch-alls that accumulate unrelated logic. |

## Documentation

| Practice | Detail |
|---|---|
| Use TSDoc for public APIs | Exported functions, classes, and types should carry `/** ... */` doc comments describing purpose, parameters, return value, and thrown errors, since these surface in IDE tooltips and generated docs for consumers who never read the source. |
| Never commit commented-out code | Others cannot tell whether it was left intentionally and will hesitate to remove it. Delete it and recover from version control if needed. |

## Error Handling

| Practice | Detail |
|---|---|
| Define typed error classes | Extending `Error` with domain classes (`class NotFoundError extends Error`) enables `instanceof` checks and structured metadata instead of fragile parsing of message strings. |
| Never swallow errors silently | An empty `catch` hides failures and makes incidents undiagnosable. Always log, rethrow, or propagate to the caller. |
| Prefer `async/await` and promises over callbacks | Promises compose cleanly, integrate with `Promise.all` and `Promise.race` for parallelism, and give clean error propagation without callback nesting. Wrap legacy callback APIs with `util.promisify`. |

## Input Validation

| Practice | Detail |
|---|---|
| Validate all external input | CLI arguments, environment variables, config files, request bodies, DOM values, and file contents are untrusted, so validate shape and types before use rather than relying on client-side checks. |
| Never read `process.env` directly | Its values are always `string \| undefined`. Access them through a validated config object so missing or malformed vars fail loudly at startup, not silently deep in the code. |
| Treat DOM-sourced data as untrusted | Attributes, `innerHTML`, `dataset`, and form fields can be tampered with, so validate them before use as you would any user input. |
| Use a schema library at runtime boundaries | `JSON.parse`, HTTP responses, and file reads yield `unknown`. A library like zod or valibot validates and narrows to a typed value in one step, keeping the type and the runtime check in sync. |

## Performance

| Practice | Detail |
|---|---|
| Use `for` loops only in hot paths | A `for` loop with a cached length is the fastest construct and worth it in server-side hot loops. For small arrays and client code, prefer readable `map`, `filter`, and `find`, since the difference is negligible. |
| Prefer `Map` and `Set` for dynamic collections | `Map` gives O(1) keyed access with any key type and `Set` gives O(1) membership tests, both faster than plain objects for frequent dynamic insertion and lookup. |
| Avoid object allocations in tight loops | Creating objects inside a tight loop applies GC pressure, so reuse or hoist allocations outside the loop where feasible. |
| Do not mutate `array.length` directly | Setting `.length` to truncate is a non-obvious side effect; `slice` or `splice` communicates the intent clearly. |

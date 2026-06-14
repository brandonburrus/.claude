Apply these practices whenever planning, writing, or reviewing TypeScript code. Targets TypeScript 5.x. Generic clean-code and naming rules live in CLAUDE.md; this reference is the TypeScript-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Type system](#type-system)
- [Generics and classes](#generics-and-classes)
- [tsconfig](#tsconfig)
- [Tooling and lint](#tooling-and-lint)
- [Modern idioms](#modern-idioms)
- [Validation and errors](#validation-and-errors)
- [Utility types](#utility-types)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Type system

| Practice | Detail |
|---|---|
| Prefer `unknown` over `any` | `any` disables checking and propagates silently; `unknown` is the type-safe top type that forces narrowing before use. `strict` turns on `useUnknownInCatchVariables`, so `catch (err)` is `unknown`: narrow with `err instanceof Error`. |
| Use `satisfies` to check without widening | A `:` annotation makes the type beat the value and discards literal info; `satisfies` makes the value beat the type, keeping the narrow inferred shape while still validating it. Use `as const satisfies T` for immutability + literal keys + validation together. Prefer it over `as`, which lets you lie to the compiler. (4.9+) |
| Replace `enum` with `as const` objects | Numeric enums accept arbitrary numbers, emit a reverse mapping, and are nominally typed (two identical enums are not interchangeable). Use `const Status = { Draft: "draft" } as const; type Status = typeof Status[keyof typeof Status]`. If an enum is unavoidable, use a string enum and never `const enum`. |
| Model variants with discriminated unions | A shared literal discriminant (`kind`/`type`) lets the compiler narrow each branch with no assertions, replacing bags of optional fields. |
| Enforce exhaustiveness with `never` | In an exhaustive `switch`, the value narrows to `never` in `default`; pass it to `assertNever(x: never)` so a new unhandled variant is a compile error, not a silent fallthrough. Optionally back with eslint `switch-exhaustiveness-check`. |
| `const` type params need a `readonly` constraint | `<const T>` (5.0) preserves literal/tuple inference without callers writing `as const`, but `<const T extends string[]>` silently does nothing; the constraint must be `readonly string[]`. |
| Avoid bare `{}`, `object`, `Object` | `{}` means "any non-nullish value", not "empty object". Use `Record<string, unknown>` for arbitrary objects, `Record<PropertyKey, never>` for a truly empty one. The one good use is the `<T extends {}>` constraint (excludes null/undefined). |
| `type` vs `interface` | Interfaces for extensible object shapes, public API contracts, and class `implements` (the Handbook's default, and `extends` can be faster to typecheck than `&`). `type` for unions, intersections, mapped/conditional types, and tuples, which interfaces cannot express. Beware interface declaration merging: useful for ambient augmentation, a silent footgun for app types. |
| Mark `readonly` where mutation is unintended | Communicates intent and lets the compiler block accidental mutation. |
| Use `Array<T>` for complex element types | `T[]` and `readonly T[]` read fine for simple elements, but switch to `Array<string \| number>` / `ReadonlyArray<T>` for unions and complex elements, where the bracket form gets visually ambiguous. |
| Keep nullability out of type aliases | Do not bake `\| null`/`\| undefined` into a reusable `type`/`interface`; add it at the point of use, and prefer an optional `field?: T` over `field: T \| undefined` so absence is handled close to its origin. |

## Generics and classes

| Practice | Detail |
|---|---|
| Constrain type parameters; avoid return-only generics | A type parameter used only in the return position cannot be inferred from arguments and forces the caller to guess, so make sure each appears in an argument position and `extends`-constrain it rather than leaving it open. |
| Reach for advanced type features only when needed | Mapped, conditional, and template-literal types are powerful but hard to read and slow to typecheck; use the simplest construct that expresses the shape, preferring a discriminated union or a plain generic over a clever conditional type. |
| Use parameter properties for fields | `constructor(private readonly repo: Repo) {}` declares and assigns the field in one place; initialize fields at their declaration and avoid empty constructors. |
| Prefer TS `private` over JS `#private` | The `#name` runtime-private field adds cost and bundle weight for no real gain when static checking already enforces access; use the `private` keyword. |

## tsconfig

`strict: true` is the floor, not the ceiling. It bundles `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `strictPropertyInitialization`, `noImplicitThis`, `alwaysStrict`, and `useUnknownInCatchVariables`. Add these, which `strict` does NOT include:

| Flag | Why |
|---|---|
| `noUncheckedIndexedAccess` | Adds `\| undefined` to `arr[i]` and `record[key]`, catching the most common "assumed present" bug. The single highest-value flag beyond `strict`, and the one most often omitted. |
| `exactOptionalPropertyTypes` | Makes `prop?: T` mean "T or absent", not "T \| undefined", so assigning `undefined` to an optional prop is an error. Can be noisy against some library types; recommend it but expect friction. |
| `noImplicitOverride` | Requires the `override` keyword, so renaming a base method surfaces broken overrides instead of silent new methods. |
| `noFallthroughCasesInSwitch` | Catches a missing `break`. |
| `verbatimModuleSyntax` | Forces a 1:1 source-to-emit mapping and stops import elision, so type-only imports must say `import type`; fixes ESM/CJS interop and tree-shaking. (5.0) |
| `isolatedModules` | Required for any non-`tsc` transpiler (esbuild, swc, Babel, Vite); forbids constructs that cannot compile file-by-file, preventing builds that pass `tsc` but break under the bundler. |

Pick `moduleResolution` by target: `"nodenext"` (with `module: "nodenext"`) for code or libraries that run in Node; `"bundler"` (with `module: "esnext"`/`"preserve"`) only when a bundler emits the code. `"bundler"` is infectious: it green-lights extensionless imports that crash in raw Node, so prefer `"nodenext"` for portability.

## Tooling and lint

| Practice | Detail |
|---|---|
| Layer typescript-eslint configs deliberately | `recommended` (likely bugs, no type info), `strict` (more opinionated bug-catching, NOT semver-stable), `stylistic` (consistency). The `*-type-checked` variants need `parserOptions.project` and carry the highest-value type-aware rules. |
| Enable `no-floating-promises` | In `recommended-type-checked`; catches un-awaited promises that cause out-of-order execution and unhandled rejections. |
| Enforce `import type`, one mechanism only | Use either `verbatimModuleSyntax` (build fails, manual fix) OR eslint `consistent-type-imports` (auto-fixes), never both; they conflict. |
| Format with Prettier, not ESLint | Keep formatting rules out of ESLint; let Prettier own formatting and ESLint own correctness. |

## Modern idioms

| Practice | Detail |
|---|---|
| `using` / `await using` for cleanup (5.2) | Deterministic resource cleanup via `Symbol.dispose`/`Symbol.asyncDispose`, running at scope exit (including early return and throw) in LIFO order; replaces try/finally for files, connections, locks. Use `DisposableStack` for ad-hoc cleanup. Needs `target`/`lib` es2022 + `esnext.disposable` and usually a runtime polyfill, so it does not yet work everywhere. |
| Prefer native decorators (5.0) for new code | Stage-3 ECMAScript decorators need no flag. Do not mix with legacy `experimentalDecorators` + `emitDecoratorMetadata`, which NestJS, Angular, and TypeORM still require; verify per framework before choosing the native flavor. Consume framework-provided decorators rather than authoring your own, and place a JSDoc comment before the decorator, not between it and the symbol. |
| Named exports, never default | Uniform names across imports, better refactors and auto-import. Also avoid `export let`; expose a getter instead. |
| No `namespace` | Use ES modules and files; the only modern exception is `declare global` / ambient module augmentation. |
| Promises over callbacks | `async/await` composes with `Promise.all`/`race` and propagates errors cleanly; wrap legacy callback APIs with `util.promisify`. |

## Validation and errors

| Practice | Detail |
|---|---|
| Validate external input at the boundary as `unknown` | `JSON.parse`, HTTP responses, file reads, CLI args, and DOM values are untrusted and untyped. Validate shape with a schema library (zod, valibot) that narrows `unknown` to a typed value in one step, keeping the type and the runtime check in sync. |
| Never read `process.env` directly | Values are `string \| undefined`; access through a validated config object so missing or malformed vars fail loudly at startup. |
| Define typed error classes | Extend `Error` with domain classes for `instanceof` checks and structured metadata instead of parsing message strings. Never swallow an error in an empty `catch`. |

## Utility types

Prefer built-ins over re-implementing a transformation; hand-rolled equivalents drift and obscure intent.

| Type | Use |
|---|---|
| `Partial<T>` / `Required<T>` | All properties optional / required (patch payloads and their inverse). |
| `Readonly<T>` | All properties `readonly`. |
| `Pick<T, K>` / `Omit<T, K>` | Select or exclude a property subset. |
| `Record<K, V>` | Map type with keys `K`, values `V`. |
| `NonNullable<T>` | Remove `null` and `undefined`. |
| `ReturnType<T>` / `Parameters<T>` | Stay coupled to a function's return type or parameter tuple. |
| `Awaited<T>` | Unwrap `Promise<T>` recursively. |

## Gotchas

- `{}` is "any non-nullish value", not "empty object"; reach for `Record<string, unknown>` or `Record<PropertyKey, never>`.
- `void`-ing a promise satisfies the linter but leaves the rejection unhandled at runtime.
- `<const T extends string[]>` silently does nothing; the constraint must be `readonly string[]`.
- A `:` annotation discards literal types (`as const`/`satisfies` keep them); annotating a config object too eagerly loses key autocomplete.
- `as` is an unchecked assertion that can break at runtime; reserve it for cases where you genuinely know more than the compiler (DOM, loose libs). Use `as` syntax, never angle-bracket `<T>x` (it clashes with JSX), and prefer a type annotation over `as` on an object literal so excess or missing properties are still caught.
- Spread only objects into objects and iterables into arrays; spreading a primitive, `null`, or `undefined` is a bug the type checker is configured to flag.
- `verbatimModuleSyntax` and eslint `consistent-type-imports` fight if both are on; choose one.

## Sources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html), [5.0](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html) and [5.2](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html) release notes, [TSConfig reference](https://www.typescriptlang.org/tsconfig/) - official, authoritative on language and flag semantics.
- [typescript-eslint configs](https://typescript-eslint.io/users/configs/) and rule docs ([no-floating-promises](https://typescript-eslint.io/rules/no-floating-promises/), [consistent-type-imports](https://typescript-eslint.io/rules/consistent-type-imports/)) - the canonical TS linting project.
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) (also published at [ts.dev/style](https://ts.dev/style/), the same document) - major maintained style guide; enum/namespace/any/exports conventions, `Array<T>` for complex elements, parameter properties, `private` over `#`, nullability-at-use, and the spread/assertion rules.
- [Mastering TypeScript (TypeScriptWorld)](https://typescriptworld.com/mastering-typescript-a-comprehensive-guide-to-best-practices-and-advanced-patterns) - applied best-practices and advanced-pattern guide; generics constraints and the return-only-generic caution.
- [Total TypeScript](https://www.totaltypescript.com/) (Matt Pocock) - recognized educator; `satisfies`, enum, and empty-object guidance.
- [Andrew Branch on nodenext](https://blog.andrewbran.ch/is-nodenext-right-for-libraries-that-dont-target-node-js/) - TS-team member; module-resolution trade-offs.

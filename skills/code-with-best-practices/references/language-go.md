Apply these practices whenever planning, writing, or reviewing Go code.

## Contents

- Error Handling
- Interfaces
- Goroutines and Channels
- Zero Values and Struct Design
- Slices and Maps
- Package Layout and Naming
- Doc Comments
- Testing
- Defer

## Error Handling

| Practice | Detail |
| --- | --- |
| Wrap with `%w`, not `%v`, when callers may need the cause | `%w` preserves the error chain so `errors.Is` and `errors.As` keep working, whereas `%v` flattens the cause into a string and breaks programmatic inspection. |
| Use sentinel errors (`var ErrNotFound = errors.New(...)`) for conditions callers branch on | A package-level sentinel gives callers a stable value to test with `errors.Is`, instead of forcing them to match on fragile error strings. |
| Use typed errors when callers need data from the failure | A struct implementing `error` carries fields (status code, field name) that `errors.As` can extract, which a sentinel cannot convey. |
| Never discard an error with `_` unless you can justify why | A silently dropped error hides failures that surface later as corrupted state; if ignoring is truly correct, a comment should say why. |
| Add context when wrapping, but do not repeat the callee's context | Each layer should add what only it knows (the operation, the key), since duplicated context produces noisy chains like "open file: open file: ...". |
| Do not start error strings with capital letters or punctuation | Errors are often wrapped and concatenated, so a mid-sentence capital or trailing period reads wrong in the combined message. |
| Check errors immediately, before using the other return values | Go does not guarantee the non-error returns are valid when an error is non-nil, so using them first risks acting on zero or partial data. |

## Interfaces

| Practice | Detail |
| --- | --- |
| Accept interfaces, return concrete structs | Accepting an interface lets callers pass any implementation including fakes, while returning a struct gives them the full, discoverable API without premature abstraction. |
| Define interfaces in the consuming package, not the implementing one | The consumer knows exactly which methods it needs, so a consumer-defined interface stays minimal and avoids coupling every implementer to one shared contract. |
| Keep interfaces small, ideally one to three methods | Small interfaces are easy to implement, mock, and compose, which is why `io.Reader` and `io.Writer` are reused everywhere. |
| Do not create an interface until there is a second implementation or a real test seam | A single-implementation interface adds indirection with no benefit and hides the concrete type's documentation behind an abstraction. |
| Return errors as the `error` interface, not a concrete error type | Returning a concrete pointer type makes a typed-nil compare non-nil against `error`, a classic bug; the `error` interface avoids it. |

## Goroutines and Channels

| Practice | Detail |
| --- | --- |
| Make goroutine lifetime and exit conditions explicit before launching one | A goroutine with no defined stop condition leaks for the life of the process, holding memory and resources indefinitely. |
| The party that creates a channel owns closing it | Closing is a write; only the sender side should close, since closing from a receiver or double-closing panics. |
| Propagate `context.Context` as the first parameter for cancellation | A shared context lets callers cancel in-flight work on timeout or shutdown, which is the standard mechanism for stopping goroutine trees cleanly. |
| Never store a `context.Context` in a struct field | Contexts are request-scoped and meant to flow through call arguments; stashing one in a struct outlives its scope and hides cancellation from readers. |
| Select on `ctx.Done()` in any loop or blocking send or receive | Without a `ctx.Done()` case, a goroutine blocked on a channel ignores cancellation and leaks even after its caller has given up. |
| Use buffered channels only with a concrete, justified buffer size | An arbitrary buffer hides backpressure and changes timing semantics; the size should reflect a known producer or consumer relationship. |
| Guard shared mutable state with a mutex or confine it to one goroutine | Concurrent access without synchronization is a data race that the runtime does not always catch, producing nondeterministic corruption. |

## Zero Values and Struct Design

| Practice | Detail |
| --- | --- |
| Design structs so the zero value is usable | A usable zero value (like `sync.Mutex` or `bytes.Buffer`) lets callers skip a constructor and avoids nil-pointer surprises on uninitialized fields. |
| Provide a `New` constructor only when invariants must be enforced at creation | A constructor is warranted when fields must be validated or wired together; otherwise it is ceremony that obscures the usable zero value. |
| Prefer value receivers unless you must mutate or the struct is large | Value receivers keep methods safe to call on copies and document that the method does not mutate, while pointer receivers signal the opposite. |
| Keep receiver type consistent across a type's method set | Mixing value and pointer receivers on one type confuses which value satisfies an interface and invites typed-nil and copy bugs. |

## Slices and Maps

| Practice | Detail |
| --- | --- |
| Distinguish nil slices from empty slices deliberately | A nil slice and an empty slice behave the same for `len`, `range`, and `append`, but they marshal to `null` versus `[]` in JSON, which clients may treat differently. |
| Remember that re-slicing aliases the same backing array | A sub-slice shares storage with its parent, so writing through one or appending within spare capacity can silently mutate the other. |
| Pre-size slices and maps with `make` when the count is known | Pre-sizing avoids repeated reallocation and rehashing as the collection grows, a measurable cost in hot paths. |
| Copy a slice before retaining it if the source may be reused | Holding a slice that points into a reused buffer (such as a scanner's) can expose later-overwritten data; copy to take ownership. |
| Never rely on map iteration order | Go randomizes map ranging on purpose, so any code that assumes a stable order is nondeterministically broken. |
| Reading a missing map key returns the zero value, not an error | Use the two-value form `v, ok := m[k]` to distinguish a stored zero value from an absent key, which the single-value form cannot. |
| Maps are not safe for concurrent read-write | Concurrent map writes panic the program; use a mutex or `sync.Map` for shared access. |

## Package Layout and Naming

| Practice | Detail |
| --- | --- |
| Organize by feature and domain, not by technical layer | Domain-oriented packages keep related code together and limit import surface, whereas layer packages like `models` or `utils` become dumping grounds. |
| Use short, lowercase, single-word package names with no underscores or plurals | The package name prefixes every exported identifier, so `chubby` reads better than `chubby.ChubbyFile`; concision avoids stutter at the call site. |
| Avoid stutter between package and identifier names | `http.Server` reads cleanly while `http.HTTPServer` repeats; the package qualifier already supplies the namespace. |
| Avoid a generic `util`, `common`, or `helpers` package | These names convey nothing about responsibility and attract unrelated code; name packages for what they provide. |
| Use MixedCaps for multi-word names, never underscores | Go's convention is `MixedCaps` or `mixedCaps`; underscores read as non-idiomatic and clash with tooling expectations. |
| Capitalization controls export; lowercase the first letter to keep an identifier package-private | Export is a deliberate API decision, so default to unexported and promote to exported only when a name is part of the package's contract. |

## Doc Comments

| Practice | Detail |
| --- | --- |
| Begin every exported identifier's doc comment with the identifier name | Tooling (`go doc`, pkg.go.dev) extracts these comments verbatim, so "Open opens the file..." renders correctly while "This function..." does not. |
| Write a package doc comment on exactly one file's `package` clause | A single `// Package foo ...` comment becomes the package overview; duplicating it across files is redundant and may conflict. |
| Document the why and the contract, not the mechanics | The signature already shows the what; comments earn their place by stating preconditions, side effects, and error meanings the reader cannot infer. |

## Testing

| Practice | Detail |
| --- | --- |
| Use table-driven tests with a slice of named cases | A table consolidates many inputs in one readable place and makes adding a case a one-line change rather than a copied test function. |
| Run each table case as a subtest with `t.Run(tc.name, ...)` | Subtests give each case its own name in output and allow running or skipping one with `-run`, which a single flat loop cannot. |
| Capture the loop variable per iteration before parallel subtests (pre-Go 1.22) | In older Go, the shared loop variable causes every parallel subtest to see the final value; rebind it or use Go 1.22+ where this is fixed. |
| Report failures with `t.Errorf` showing got versus want | Continuing after a failure surfaces all broken cases at once, and a got/want message makes the discrepancy diagnosable without rerunning. |
| Reserve `t.Fatal` for failures that make the rest of the test meaningless | `t.Fatal` stops the current test immediately, so use it only when later assertions cannot run, not for ordinary value mismatches. |
| Use `_test` external package suffix to test only the exported API | An external test package forces tests through the public surface, catching usability problems that white-box internal tests can mask. |

## Defer

| Practice | Detail |
| --- | --- |
| Defer cleanup immediately after a successful acquire | Pairing `Close` or `Unlock` with the acquire on the next line guarantees release on every return path, including panics and early errors. |
| Remember deferred arguments evaluate at the `defer` statement, not at call time | The argument expressions are snapshotted when `defer` runs, so a value changed afterward will not be reflected unless you defer a closure. |
| Avoid deferring inside a loop when the function is long-lived | Deferred calls run only at function return, so accumulating them in a loop holds resources (open files, locks) far longer than intended. |
| Check the error from a deferred `Close` on writable resources | A deferred `Close` on a file being written can return a flush error that signals data loss; capture it via a named return or explicit handling. |

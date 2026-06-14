Apply these practices whenever planning, writing, or reviewing Go code. Targets Go 1.22+ (version-specific items are flagged). Generic clean-code and naming rules live in CLAUDE.md; this reference is the Go-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Errors](#errors)
- [Context](#context)
- [Goroutines and channels](#goroutines-and-channels)
- [Interfaces and types](#interfaces-and-types)
- [Generics](#generics)
- [Logging](#logging)
- [Testing](#testing)
- [Defer and cleanup](#defer-and-cleanup)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Errors

| Practice | Detail |
|---|---|
| Wrap with `%w`, not `%v`, when callers may inspect the cause | `%w` preserves the chain so `errors.Is`/`errors.As` keep working; `%v` flattens the cause to a string and breaks programmatic inspection. Use `%v` deliberately at trust boundaries (RPC, storage) where you want to hide the underlying error. Put `%w` at the end of the format string. |
| Ask "must the caller match this error?" before choosing a shape | If no, a plain `fmt.Errorf` is enough. If yes and the message is static, use a sentinel (`var ErrNotFound = errors.New(...)`). If yes and it carries data, use a typed error (a struct implementing `error`) that `errors.As` can extract. |
| Test with `errors.Is`/`errors.As`, never string matching | String form is not part of the contract; `errors.Is` matches a sentinel through any wrapping, `errors.As` binds a typed error from anywhere in the chain. |
| Use `errors.Join` to carry multiple failures | `errors.Join(err1, err2)` (1.20+) returns one error that `errors.Is` matches against each; use it for accumulated loop failures or multi-step cleanup, not manual string concatenation. |
| Handle an error exactly once | Logging an error and then returning it double-reports it, because callers handle it too. Log it or return it, not both. |
| Do not capitalize error strings or end them with punctuation | Errors get wrapped and concatenated, so a mid-chain capital or trailing period reads wrong. (Logging is line-oriented and exempt.) |
| Avoid in-band error sentinels like `-1`, `""`, `nil` | Return a second value (`value string, ok bool`) or an `error` so misuse is a compile-time shape, not a runtime guess. |
| Check the error before touching other returns | Go does not guarantee the non-error returns are valid when `err != nil`. |

## Context

| Practice | Detail |
|---|---|
| Pass `ctx context.Context` as the first parameter | The standard cancellation and deadline mechanism; thread it through call arguments so cancellation is visible at every layer. |
| Never store a `Context` in a struct field | It is request-scoped; stashing it outlives its scope and hides cancellation from readers. Add a `ctx` arg to each method instead (exception: matching a stdlib/third-party interface). |
| Select on `ctx.Done()` in every loop or blocking send/receive | A goroutine blocked on a channel with no `ctx.Done()` case ignores cancellation and leaks after its caller gives up. |
| Do not pass a `nil` Context | Use `context.TODO()` when unsure which to plumb through, `context.Background()` at the top of `main`/tests/init. |

## Goroutines and channels

| Practice | Detail |
|---|---|
| Define a goroutine's stop condition before launching it | Every goroutine needs a predictable end or a signal to stop (closed `chan struct{}`, cancelled context); otherwise it leaks for the life of the process. |
| Give callers a way to block until the goroutine exits | A `sync.WaitGroup` or a channel the goroutine closes on exit lets shutdown wait for in-flight work to drain. |
| Never spawn goroutines in `init()` | Expose an object owning the goroutine's lifetime with an explicit start and a shutdown that signals and waits. |
| The party that creates a channel owns closing it | Closing is a write; only the sender closes, since closing from a receiver or double-closing panics. |
| Specify channel direction in signatures | `chan<- T` (send-only) and `<-chan T` (receive-only) document and enforce ownership and prevent accidental misuse. |
| Keep channels unbuffered or size 1; justify anything larger | A larger buffer hides backpressure and changes timing; the size should map to a known producer/consumer relationship. |
| Guard shared mutable state with a mutex or confine it to one goroutine | Unsynchronized concurrent access is a data race the runtime does not always catch; run `go test -race`. |

## Interfaces and types

| Practice | Detail |
|---|---|
| Accept interfaces, return concrete structs | An interface parameter lets callers pass fakes; a concrete return gives them the full, documented API without premature abstraction. |
| Define interfaces in the consuming package | The consumer knows exactly which methods it needs, so the interface stays small and implementers stay decoupled. Do not create one until a second implementation or a real test seam exists. |
| Pass interfaces by value, not pointer | An interface value already holds a pointer to its data; `*SomeInterface` is almost never what you want. |
| Return the `error` interface, not a concrete error type | A concrete pointer return compares non-nil against `error` even when nil (the typed-nil bug); the interface avoids it. |
| Keep receiver types consistent across a type's method set | Mixing value and pointer receivers confuses which value satisfies an interface and invites typed-nil and copy bugs. When in doubt use a pointer receiver; use value receivers only for small immutable types. |
| Design the zero value to be usable | A usable zero value (`sync.Mutex`, `bytes.Buffer`) lets callers skip a constructor. The zero `sync.Mutex` is valid, so embed it as a value field, never a pointer. Add a `New` constructor only to enforce invariants at creation. |
| Copy slices crossing a trust boundary | Storing or returning a caller's slice shares the backing array; `dst := make([]T, len(src)); copy(dst, src)` to take ownership and prevent action-at-a-distance mutation. |
| Verify interface satisfaction at compile time | `var _ Thinger = (*Concrete)(nil)` catches a broken implementation at build, not at the call site. |

## Generics

| Practice | Detail |
|---|---|
| Reach for type parameters only on repeated identical-logic-different-type code | Good fits: container helpers over slices/maps/channels, general data structures (trees, lists), one method body shared across element types. (1.18+) |
| Use an interface, not a type parameter, when you only call methods | `func ReadSome(r io.Reader)` beats `func ReadSome[T io.Reader](r T)`; if implementations differ per type, that is an interface, not a generic. |
| Write functions first, add type parameters later | Start concrete; promote to generic only when duplication across types is real, not anticipated. |

## Logging

| Practice | Detail |
|---|---|
| Use `log/slog` for structured logging (1.21+) | `slog.Info("msg", "key", val)` emits structured key/value records; swap in `slog.NewJSONHandler` for machine-readable output. |
| Run `go vet`'s slog check, or prefer typed attrs | The alternating key/value form silently breaks if a key or value is dropped; `slog.LogAttrs(ctx, level, msg, slog.String("k", v))` is type-safe and lower-allocation on hot paths. |
| Use the `*Context` variants when a context is in scope | `slog.InfoContext(ctx, ...)` lets handlers extract trace IDs and request scope; note cancelling the context does not suppress the write. |
| Attach request-scoped fields with `With` once | `logger := slog.Default().With("request_id", id)` carries the field on every later call instead of repeating it. |

## Testing

| Practice | Detail |
|---|---|
| Use table-driven tests with named cases run as subtests | A slice of named cases plus `t.Run(tc.name, ...)` consolidates inputs, names each case in output, and allows `-run` filtering. |
| Add `t.Parallel()` only when cases share no mutable state | Parallel subtests accelerate suites when the table is immutable; under Go 1.22+ no per-iteration loop-variable copy is needed. |
| Call `t.Fatal`/`t.FailNow` only from the test goroutine | These are illegal from a spawned goroutine; report from helpers with `t.Error` and return, reserving `t.Fatal` for the main goroutine when later assertions are meaningless. |
| Report failures with got-versus-want via `t.Errorf` | Continuing past a failure surfaces all broken cases at once and makes the discrepancy diagnosable. |
| Test through the exported API with a `_test` package | An external `package foo_test` forces tests through the public surface and catches usability problems white-box tests mask. |

## Defer and cleanup

| Practice | Detail |
|---|---|
| Defer cleanup immediately after a successful acquire | Pairing `Close`/`Unlock` with the acquire on the next line guarantees release on every return path, including panics. |
| Remember deferred arguments evaluate at the `defer` statement | The argument expressions are snapshotted then; defer a closure if you need the later value. |
| Do not defer inside a loop in a long-lived function | Deferred calls run only at function return, so loop-accumulated defers hold files and locks far longer than intended. |
| Check the error from a deferred `Close` on writable resources | A deferred `Close` on a file being written can return a flush error signalling data loss; capture it via a named return. |

## Gotchas

- Pre-1.22 the loop variable was shared across iterations, so closures and goroutines capturing it all saw the final value; 1.22 gives each iteration its own copy, but only for modules declaring `go 1.22`+ in `go.mod`.
- A concrete typed-nil returned as `error` is non-nil: `var e *MyErr; return e` makes `err != nil` true. Return the `error` interface and return literal `nil`.
- A nil slice and an empty slice behave alike for `len`/`range`/`append` but marshal to `null` versus `[]` in JSON.
- Re-slicing aliases the backing array, so appending within spare capacity can silently mutate the parent slice.
- Map iteration order is randomized on purpose; never depend on it. Reading a missing key returns the zero value, so use `v, ok := m[k]` to tell absent from a stored zero. Concurrent map writes panic.
- Naked returns are acceptable only in very short functions; in anything longer, be explicit, since named-return mutation across a long body is hard to track.

## Sources

- [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) - the official language guide and the canonical review checklist; naked returns, error strings, context, receivers, in-band errors.
- [Go blog: error handling](https://go.dev/blog/error-handling-and-go), [working with errors / `%w`](https://go.dev/blog/go1.13-errors), and [the `errors` package docs](https://pkg.go.dev/errors) - official; `%w`, `errors.Is`/`As`/`Join`, sentinel vs typed.
- [Go blog: loop variable scoping (1.22)](https://go.dev/blog/loopvar-preview) and [`context` docs](https://pkg.go.dev/context) - official; the 1.22 semantics change and context propagation/cancellation.
- [Go blog: structured logging with slog](https://go.dev/blog/slog) and [`log/slog` docs](https://pkg.go.dev/log/slog) - official; handlers, attrs, context variants, the key/value footgun.
- [Go blog: when to use generics](https://go.dev/blog/when-generics) - official; the type-parameter-vs-interface decision and "write functions first."
- [Google Go Style Guide](https://google.github.io/styleguide/go/) - major maintained guide; error structure, channel direction, goroutine and test-goroutine rules.
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md) - widely adopted production style guide; goroutine lifetime, zero-value mutex, channel buffer discipline, boundary slice copies, compile-time interface checks.

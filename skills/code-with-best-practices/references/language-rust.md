Apply these practices whenever planning, writing, or reviewing Rust code. Targets the 2024 edition (edition-specific items are flagged). Generic clean-code and naming rules live in CLAUDE.md; this reference is the Rust-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Error handling](#error-handling)
- [Ownership and signatures](#ownership-and-signatures)
- [Iterators and Option](#iterators-and-option)
- [Types and conversions](#types-and-conversions)
- [Traits](#traits)
- [Tooling and lint](#tooling-and-lint)
- [Unsafe and async](#unsafe-and-async)
- [Edition 2024](#edition-2024)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Error handling

| Practice | Detail |
|---|---|
| Propagate with `?`, never hand-rolled `match` | `?` keeps the happy path readable and applies a `From` conversion on the error, so it threads through layers as long as each error type implements `From` of the inner one. |
| `thiserror` for libraries, `anyhow` for applications | `thiserror` derives `Error`/`Display`/`#[from]` to give consumers a concrete, matchable enum; `anyhow::Result<T>` erases the type for app code that only logs or displays. The split is the single most common error-handling mistake: a library returning `anyhow::Error` denies callers any way to branch on the failure. |
| No `unwrap`/`expect` in library code | They panic and abort the caller's process. Return `Result`/`Option` and let the caller decide. Reserve them for tests, `main`, and cases prior logic proves infallible, and then prefer `expect("invariant: ...")` whose message states the proof. |
| Preserve the cause with `#[source]` or `#[from]` | Dropping the underlying error makes production logs useless. `#[from]` both stores the source and generates the conversion `?` needs. |
| Name variants by recovery, not by call site | `NotFound`/`Timeout` lets a caller branch on what to do; `RedisStep3Failed` leaks implementation detail and forces re-matching when internals move. |
| Add context at boundaries | `anyhow`'s `.context("reading config")?` turns an opaque downstream error into a diagnosable one; per the API guidelines (C-GOOD-ERR) error `Display` should be lowercase with no trailing punctuation. |
| Never use `()` (or `String`) as an error type | Implement `std::error::Error + Send + Sync` so the error composes with `?`, `Box<dyn Error>`, and `anyhow` (C-GOOD-ERR). |

## Ownership and signatures

| Practice | Detail |
|---|---|
| Accept `&str` not `&String`, `&[T]` not `&Vec<T>` | The slice forms accept strictly more callers (arrays, `Vec`, literals, sub-slices) via deref coercion at zero cost; `&String`/`&Vec<T>` are a double indirection that excludes them for no benefit. |
| Return owned `String`/`Vec<T>` when you create data | Returning a borrow from a value-producing function forces lifetime gymnastics and signals an unclear owner; the allocation is the honest cost of new data. |
| Do not `.clone()` to satisfy the borrow checker | A reflexive clone is a real allocation hiding a design problem; restructure ownership with references, `into_iter`, `mem::take`, or `mem::swap` so each clone is deliberate. |
| Take `T` by value when the function consumes it | An owned parameter states ownership transfer in the signature and removes a clone the caller would otherwise make. |
| Reach for `Rc`/`Arc` + `RefCell`/`Mutex` last | Shared ownership and interior mutability move guarantees from compile time to run time; reserve them for genuine sharing, not for dodging a borrow error. |
| Use `Cow<'_, str>` when a function usually borrows but sometimes owns | It avoids forcing every caller to allocate up front while still allowing the owned case (e.g. returning input unchanged vs. a modified copy). |
| Accept `impl AsRef<Path>` / `impl Into<String>` for ergonomic boundaries | Generic conversion bounds let callers pass whichever owned-or-borrowed form they have without an explicit conversion at the call site. |

## Iterators and Option

| Practice | Detail |
|---|---|
| Prefer iterator adapters over manual loops | `.iter().filter().map().collect()` states intent and optimizes well; use a `for` loop only for side effects, early exit, or control flow a chain obscures. |
| Pick `iter`/`iter_mut`/`into_iter` by ownership need | `iter()` borrows, `iter_mut()` borrows mutably, `into_iter()` consumes and avoids clones; the choice encodes how the source is used afterward. |
| Annotate the collected type | `collect()` is generic over its output, so `let v: Vec<_> =` or the `::<Vec<_>>()` turbofish tells the compiler what to build; `collect::<Result<Vec<_>, _>>()` short-circuits on the first error. |
| Combine `Option`/`Result` instead of matching | `map`, `and_then`, `unwrap_or`, `unwrap_or_else`, `ok_or`/`ok_or_else`, and `?` express the common transforms; reserve `match` for genuinely multi-armed logic. Prefer the `_else` variants when the fallback is expensive, since the eager forms always evaluate it. |
| Return `impl Iterator<Item = T>` over a `Vec` | A lazy iterator lets callers stop early or stream without you allocating the full result set; collect only when you must own or index it. |
| Avoid indexing where an iterator fits | `arr[i]` panics on out-of-bounds; `.get(i)` returns `Option`, and iterating sidesteps the bounds entirely. |

## Types and conversions

| Practice | Detail |
|---|---|
| Implement `From`, never `Into` | A blanket impl gives you `Into` (and `TryInto`) for free from `From` (and `TryFrom`); implementing `Into` directly is redundant and the API guidelines forbid it (C-CONV-TRAITS). Use `TryFrom` for fallible conversions. |
| Wrap primitives in newtypes for distinct meaning | `struct UserId(u64)` and `struct OrderId(u64)` make the compiler reject mixing values that share a representation, and give you a home for validation and trait impls. |
| Derive the standard traits eagerly | `Debug` on nearly everything; add `Clone`, `Copy`, `PartialEq`/`Eq`, `Hash`, `PartialOrd`/`Ord`, `Default` where they apply (C-COMMON-TRAITS). Missing derives surface as friction far from the type. |
| Pair `Default` with an empty `new()` | Both are expected; `#[derive(Default)]` covers the common case, and `new()` is the discoverable constructor (C-COMMON-TRAITS). |
| Prefer enums over boolean parameters | `enum Direction { Forward, Backward }` is self-documenting at the call site and extends to new cases, unlike a bare `bool` no reader can decode. |
| Model state with data-carrying enums, not optional-field bags | A struct full of `Option` fields where only some combinations are valid should be an enum whose variants carry exactly their data, making illegal states unrepresentable. |
| Use a builder for many optional fields | Method chaining keeps construction readable and a `build() -> Result<T>` centralizes invariant checks. |

## Traits

| Practice | Detail |
|---|---|
| Keep traits small and require only the bounds the body uses | Narrow traits compose and over-constraining (a bound the function never invokes) needlessly excludes valid callers. |
| Prefer `impl Trait` in argument position, generics for naming | `fn f(x: impl Read)` is the lightweight form; name the parameter `fn f<R: Read>(x: R)` only when you reference `R` elsewhere in the signature. |
| Keep a trait object-safe when you need `dyn` | Generic methods, `Self` by value in returns, and `Sized` bounds make a trait unusable as `dyn Trait`; design around them when type erasure is required. |
| Take `R: Read` / `W: Write` by value | Accepting the reader/writer by value lets the caller pass `&mut r` when they need to keep it, but not the reverse (C-RW-VALUE). |
| Document the semantic contract | Implementors cannot uphold invariants they cannot see; state laws like `Eq` reflexivity, ordering consistency, or any `unsafe` requirement. |

## Tooling and lint

| Practice | Detail |
|---|---|
| Gate CI on `clippy -- -D warnings` | Promoting warnings to errors makes Clippy a hard gate; `RUSTFLAGS="-D warnings"` does the same for `rustc`. A green build that ignores Clippy is not green. |
| Adopt `clippy::pedantic` deliberately, not wholesale | `pedantic` catches real issues but ships intentional false positives; enable it, then `#[allow(...)]` the noisy lints at the narrowest scope with a reason rather than disabling the group. |
| Format with `rustfmt`, lint with Clippy | Keep formatting out of review; `cargo fmt --check` in CI enforces it mechanically. |
| Configure project-wide lints in `Cargo.toml` `[lints]` | The `[lints.clippy]`/`[lints.rust]` tables set lint levels per crate (and workspace) in one place, replacing scattered crate-level `#![deny(...)]` attributes. |
| Follow case conventions per item kind | `UpperCamelCase` types/traits (acronyms as one word: `Uuid`, not `UUID`), `snake_case` functions/modules/vars, `SCREAMING_SNAKE_CASE` consts; getters drop `get_` (`name(&self)`, not `get_name`). |

## Unsafe and async

| Practice | Detail |
|---|---|
| Justify every `unsafe` block with a `// SAFETY:` comment | The compiler stops checking inside `unsafe`, so the comment is the only record of which invariants make it sound; wrap the smallest expression and expose a safe abstraction so callers never touch it. |
| Never use `unsafe` to bypass the borrow checker | Transmuting references to silence a borrow error hides the design flaw and is undefined behavior; fix the ownership. Prefer std's already-correct `Vec`/`Box`/`Arc` over reimplementing them. |
| Never block inside `async` | `std::fs`, `std::net`, and `std::thread::sleep` stall a runtime worker and starve other tasks; use the runtime's async equivalents or `spawn_blocking`. |
| Do not hold a `MutexGuard` across `.await` | The guard blocks every contending task while suspended (and the std guard is `!Send`); copy what you need and drop the guard before awaiting, or use the runtime's async mutex. |
| Await or store spawned `JoinHandle`s | Dropping the handle detaches the task and silently discards its result and panics; await it or keep it to join later. Use `tokio::select!` to race a future against a timeout or cancellation. |

## Edition 2024

| Change | Detail |
|---|---|
| `edition = "2024"` implies resolver v3 | The MSRV-aware resolver prefers dependency versions compatible with your `rust-version`; set `rust-version` in `Cargo.toml` so it has something to respect. |
| `if let` temporaries drop before the `else` | The temporary from the scrutinee is now dropped before entering `else`, fixing a class of deadlocks (e.g. a lock guard held into the `else` branch). Re-check `if let` chains that relied on the old scope. |
| Let-chains are stable | `if let Some(x) = a && x > 0 && let Ok(y) = b` is allowed, flattening nested `if let` pyramids. |
| RPIT captures all in-scope lifetimes | `-> impl Trait` now captures every in-scope lifetime by default; use `impl Trait + use<'a>` to capture a subset. This removes the old workaround of a `Captures` helper trait. |

## Gotchas

- A library returning `anyhow::Error` denies callers any way to match on the failure; reach for `thiserror` at any boundary others consume.
- `&String`/`&Vec<T>`/`&Box<T>` parameters compile but exclude callers a slice would accept, for no upside.
- `arr[i]` and `vec[i]` panic out of bounds; `.get(i)` returns `Option`.
- `unwrap_or(expensive())` always evaluates the fallback; use `unwrap_or_else(|| ...)` for the lazy form.
- Implementing `Into` instead of `From` is redundant and disallowed by the API guidelines; the blanket impl already gives you `Into`.
- `'static` to silence a lifetime error hides a real bug; reserve it for literals and intentionally leaked data, and prefer owning (`String` over a multi-lifetime struct of `&str`).
- A `clippy::pedantic` group enabled crate-wide without per-lint `allow`s drowns real findings in false positives.

## Sources

- [The Rust Programming Language book](https://doc.rust-lang.org/book/) - the official language book; ownership, slices, error handling, iterators, traits.
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) ([naming](https://rust-lang.github.io/api-guidelines/naming.html), [interoperability](https://rust-lang.github.io/api-guidelines/interoperability.html)) - the official library-design checklist; conversion traits (C-CONV-TRAITS), common traits, error guidance (C-GOOD-ERR).
- [Clippy documentation](https://doc.rust-lang.org/clippy/) ([usage](https://doc.rust-lang.org/clippy/usage.html), [lint levels](https://doc.rust-lang.org/clippy/lints.html)) - the official linter docs; pedantic group, `-D warnings` CI gate.
- [The Rust Edition Guide: 2024](https://doc.rust-lang.org/edition-guide/rust-2024/index.html) ([cargo resolver](https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html), [if-let scope](https://doc.rust-lang.org/edition-guide/rust-2024/temporary-if-let-scope.html), [RPIT lifetimes](https://doc.rust-lang.org/edition-guide/rust-2024/rpit-lifetime-capture.html)) - official; edition 2024 behavior changes.
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) - the official guide to unsafe Rust; invariants, undefined behavior, why to minimize `unsafe`.
- [thiserror](https://docs.rs/thiserror/) and [anyhow](https://docs.rs/anyhow/) (dtolnay) - the de facto error crates; the library-vs-application split and `#[from]`/`.context()`.
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/) - the official runnable-example companion; `Option`/`Result` combinators, `?`, conversions.

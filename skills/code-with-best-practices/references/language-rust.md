Apply these practices whenever planning, writing, or reviewing Rust code.

## Contents

- Ownership and Borrowing
- Error Handling
- Lifetimes
- Iterators
- Type System and Patterns
- Trait Design
- Async
- Unsafe Code
- Naming
- Testing
- Documentation

## Ownership and Borrowing

| Practice | Detail |
|---|---|
| Do not reach for `.clone()` to satisfy the borrow checker | A reflexive clone is a real allocation that hides a design problem; redesign ownership with references, restructured data, or `into_iter` so each clone is deliberate. |
| Prefer `&T` and `&mut T` over `Rc`/`Arc` and `RefCell`/`Mutex` | Shared ownership and interior mutability carry runtime cost and weaken compile-time guarantees, so reserve them for designs that genuinely need them rather than to dodge borrow errors. |
| Accept `T` by value when the function consumes it | Taking the owned value communicates ownership transfer in the signature and removes a clone the caller would otherwise need. |
| Return owned types from constructors and builders | Returning `&T` from a value-producing function forces lifetime gymnastics on callers and signals the value's owner is unclear. |
| Use `Cow<'_, str>` for parameters that sometimes own | A function that borrows in the common case but occasionally owns can avoid forcing every caller to allocate up front. |

## Error Handling

| Practice | Detail |
|---|---|
| Avoid `.unwrap()` and `.expect()` in library code | They panic and take down the caller's process; return `Result<T, E>` and propagate with `?` so callers decide how to recover. Reserve them for tests and cases prior logic proves infallible. |
| Propagate with `?` rather than manual matching | The `?` operator preserves the error chain and keeps the happy path readable, so the conversion and return logic stays out of the way. |
| Use `thiserror` for library error types | Deriving `Error` and `Display` plus `#[from]` gives callers a typed, matchable enum and automatic conversions without hand-written boilerplate. |
| Use `anyhow` at application boundaries | `anyhow::Result<T>` with `.context(...)` is ergonomic where the caller will not match on variants, avoiding an enum for every fallible step. |
| Group error variants by what the caller can do | Naming variants by failure mode (`NotFound`, `Timeout`) rather than by which internal call failed lets callers branch on recovery strategy instead of implementation detail. |
| Attach context when propagating | `.context("reading config file")?` turns an opaque downstream error into a diagnosable one, since bare errors are nearly useless in production logs. |

## Lifetimes

| Practice | Detail |
|---|---|
| Annotate which input a borrowed return ties to | When a function returns `&T` with multiple reference parameters, the compiler cannot infer the source, and the annotation is a contract callers rely on. |
| Treat `fn foo<'a>(x: &'a str, y: &'a str) -> &'a str` as a promise | It declares the return lives no longer than the shortest input, so understand the constraint rather than copying the syntax to silence an error. |
| Do not use `'static` to silence lifetime errors | `'static` claims the reference lives for the whole program, which hides real lifetime bugs; reserve it for literals and intentionally leaked data. |
| Prefer owning data over multi-lifetime structs | A struct needing several lifetime parameters pushes cognitive load onto every caller, so owning (`String` over `&str`) often simplifies the API more than it costs. |
| Elide lifetimes the compiler can infer | Annotating single-reference inputs and `&self` methods the elision rules already cover adds noise without adding meaning. |

## Iterators

| Practice | Detail |
|---|---|
| Prefer iterator adapters over manual loops | `.filter().map().collect()` states intent declaratively and lets the compiler optimize; use `for` only when you need side effects, early exit, or complex control flow. |
| Pick the iterator method by ownership need | `into_iter()` consumes and avoids clones, `iter()` borrows, and `iter_mut()` borrows mutably, so the choice encodes how the collection is used. |
| Annotate the target type when collecting | `collect()` is generic over the output, so a type annotation or turbofish tells the compiler which collection to build and avoids inference errors. |
| Implement `Iterator` instead of returning `Vec` | A custom iterator evaluates lazily, so consumers that stop early or stream avoid allocating the full result set. |

## Type System and Patterns

| Practice | Detail |
|---|---|
| Wrap primitives in newtypes for distinct meanings | `struct UserId(u64)` and `struct OrderId(u64)` make the compiler reject mixing semantically different values that share a representation. |
| Implement `From`/`Into` for conversions | Using the conversion traits rather than ad hoc functions enables `.into()` at call sites and lets generic bounds accept convertible inputs. |
| Use a builder for types with many optional fields | Method chaining keeps construction readable, and validating in `.build()` to return `Result` centralizes the invariant checks. |
| Prefer enums over boolean parameters | `enum Direction { Forward, Backward }` is self-documenting at the call site and extends to new cases, unlike a bare `bool`. |
| Seal traits meant to be closed | A private supertrait method prevents downstream crates from implementing a trait you need to evolve freely. |

## Trait Design

| Practice | Detail |
|---|---|
| Keep traits small and focused | Narrow traits compose and are trivial to implement, so callers depend only on the capability they actually use. |
| Require only the bounds the body uses | Over-constraining with bounds the function never invokes needlessly excludes valid callers and couples the signature to unused capabilities. |
| Keep traits object-safe when dynamic dispatch is needed | Generic methods, `Self` in return position, and `Sized` bounds make a trait unusable as `dyn Trait`, so design around them when erasure is required. |
| Provide blanket impls where they fit | `impl<T: Display> MyTrait for T` extends behavior to every qualifying type without forcing each one to opt in manually. |
| Document the semantic contract of a trait | Implementors cannot uphold guarantees they do not know about, so state invariants like `Eq` reflexivity or any `unsafe` requirements. |

## Async

| Practice | Detail |
|---|---|
| Never call blocking APIs inside async code | `std::fs`, `std::net`, and `std::thread::sleep` stall the runtime worker thread and starve other tasks; use the runtime's async equivalents. |
| Await or store spawned `JoinHandle`s | Dropping the handle detaches the task and discards its result and errors silently, so await it or keep it to join later. |
| Use `Arc` with `tokio::sync::Mutex` for shared async state | `Rc` and `RefCell` are `!Send` and cannot cross `.await`, and the std `Mutex` is not async-aware, so its guard can deadlock the runtime. |
| Drop the guard before awaiting | Holding a `MutexGuard` across `.await` blocks every other task contending for it, so copy what you need, drop, then await. |
| Use `tokio::select!` for concurrent branches with a timeout | Racing futures lets the first to finish win, and a cancellation or timeout branch prevents a hung future from blocking forever. |
| Add `+ Send` bounds to async trait methods for multithreaded runtimes | Without `Send`, the returned future cannot move between worker threads, breaking on the default multithreaded runtime. |

## Unsafe Code

| Practice | Detail |
|---|---|
| Justify every `unsafe` block with a `// SAFETY:` comment | The compiler stops checking inside `unsafe`, so the comment is the only record of which invariants make the operation sound. |
| Wrap the smallest possible expression | Minimizing scope limits how much code the safety argument must cover and lets you expose a safe abstraction so callers never touch `unsafe`. |
| Prefer std's safe abstractions | `Vec`, `Box`, `Arc`, and `Mutex` already encapsulate unsafe correctly, so reimplementing them only reintroduces bugs they have already solved. |
| Never use `unsafe` to bypass the borrow checker | Transmuting references to silence a borrow error hides the real design flaw and creates undefined behavior; fix the ownership instead. |

## Naming

| Practice | Detail |
|---|---|
| Follow Rust's case conventions per item kind | `UpperCamelCase` for types and traits, `snake_case` for functions and variables, and `SCREAMING_SNAKE_CASE` for constants match what clippy and readers expect. |
| Use `kebab-case` crate names and `snake_case` modules | A `my-crate` in Cargo.toml is imported as `my_crate`, and one module per file (`mod user_auth;` to `user_auth.rs`) keeps the mapping predictable. |
| Omit the `get_` prefix on getters | Idiomatic Rust names a getter `name(&self)`, reserving `set_` for the mutating setter, which clippy enforces. |

## Testing

| Practice | Detail |
|---|---|
| Co-locate unit tests in `#[cfg(test)] mod tests` | Keeping tests in the same file gives them access to private items, while integration tests belong in `tests/` to exercise the public API only. |
| Prefer `Result`-returning tests over `#[should_panic]` | `#[should_panic]` cannot confirm which panic fired, so asserting on a returned error variant verifies the actual failure mode. |
| Assert with `assert_eq!`/`assert_ne!` | These print both operands on failure, making the mismatch obvious where a bare `assert!` would only report false. |
| Test error paths by matching the variant | Confirming a function fails is not enough; pattern match the error so a wrong-but-still-failing path cannot pass silently. |

## Documentation

| Practice | Detail |
|---|---|
| Document every public item with `///` | Consumers see only the public surface, so each public function, type, trait, and module needs its purpose, inputs, and outputs spelled out. |
| Include `# Examples` that compile under doctest | Doc examples run as tests, so they double as regression coverage and stay correct as the API changes. |
| Add `# Errors` and `# Panics` sections | Callers cannot guard against failure conditions they cannot see, so document when a function returns an error or panics. |
| Use `//!` for module-level docs | A module header in `lib.rs` or `mod.rs` orients readers before they descend into individual items. |

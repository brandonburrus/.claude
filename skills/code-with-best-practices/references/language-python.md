Apply these practices whenever planning, writing, or reviewing Python code.

## Pythonic Idioms

| Practice | Detail |
|---|---|
| Use context managers for resource cleanup | `with open(...)` closes the file even when an exception is raised, so resources never leak. Write custom managers (`__enter__`/`__exit__` or `@contextmanager`) for any acquire/release pair such as locks, connections, or temp directories. |
| Prefer comprehensions over manual append loops | A comprehension states the transformation in one place and runs faster than building a list element by element. Keep it to a single level of nesting; extract a helper for anything deeper so it stays readable. |
| Use `enumerate` and `zip` instead of index bookkeeping | `enumerate(items)` and `zip(names, scores)` remove fragile counter variables and index math that silently go out of sync. Pass `zip(strict=True)` when mismatched lengths should be an error rather than a silent truncation. |
| Unpack sequences directly | `x, y, z = point` documents the shape of the data and fails loudly if it changes, unlike positional indexing. Bind throwaway values to `_` so intent is explicit. |
| Use `in` for membership against sets and dicts | Membership on a set or dict is O(1), while scanning a list is O(n) and degrades quietly as data grows. Choose the container based on how you query it. |
| Use f-strings for interpolation | f-strings are the most readable and fastest interpolation and evaluate inline, so avoid `%` and `.format()` in new code. |
| Compare to `None` with `is` / `is not` | `None` is a singleton, so identity is the semantically correct check, and `== None` can be subverted by a custom `__eq__`. |
| Use truthiness for empty collections | `if not items:` works uniformly across sequences, dicts, sets, and strings and reads as intent, where `len(items) == 0` is noisier and easy to get wrong on non-sized objects. |

## Function Design

| Practice | Detail |
|---|---|
| Keep `*args` and `**kwargs` rare | They erase the signature, so callers and type checkers lose all guidance. Reserve them for decorators, wrappers, and genuinely variable-arity functions; otherwise spell out parameters. |
| Prefer keyword arguments at call sites | `connect(host="localhost", port=5432)` is self-documenting where bare positionals are not. Make parameters keyword-only with `*` on public APIs so call sites cannot drift into ambiguous ordering. |
| Return early with guard clauses | Handling invalid conditions up front keeps the happy path flat and unnested, which is far easier to follow than a pyramid of conditionals. |
| Avoid mutable default arguments | `def f(items=[])` evaluates the default once at definition, so every call shares and mutates the same list. Default to `None` and create a fresh collection inside the body. |
| Prefer pure functions | Output that depends only on inputs is trivial to test and reason about with no setup. Push I/O, global mutation, and network calls to the system boundaries so the core stays deterministic. |

## Data Structures and Types

| Practice | Detail |
|---|---|
| Use `@dataclass` or `NamedTuple` for structured data | They give named fields, annotations, and generated `__init__`, `__repr__`, and `__eq__`, removing the guesswork of ad-hoc dicts and tuples. Reach for `NamedTuple` or `frozen=True` when the value should be immutable. |
| Prefer `dict.get()` over key-existence checks | `d.get("key", default)` avoids `KeyError` and collapses a check-then-access pair into one expression with no race between the two steps. |
| Reach for `collections` types when they fit | `defaultdict`, `Counter`, and `deque` are built for their jobs and signal intent, unlike reimplementing the same accumulation by hand with plain dicts and lists. |
| Prefer `Enum` over magic strings and integers | An `Enum` lists every valid value in one place, blocks typos, and enables completion, where bare literals scatter the valid set across the codebase. |
| Type-hint public signatures | Hints are documentation the type checker actually verifies, catching mismatches before runtime. Annotate parameters, returns, and attributes, and use `from __future__ import annotations` for forward references. |

## Error Handling

| Practice | Detail |
|---|---|
| Raise specific exceptions | A precise `ValueError` lets callers handle one failure mode without catching everything, while bare `Exception` forces them to swallow unrelated errors too. |
| Define domain exception classes when useful | A named class like `InsufficientFundsError` lets callers branch on the failure type instead of parsing message strings, which break the moment wording changes. |
| Never silently swallow exceptions | `except: pass` hides the bug and leaves no trace to debug. Always log, re-raise, or handle the failure in a way the caller can observe. |
| Choose EAFP vs LBYL deliberately | Prefer `try`/`except` when failure is rare and a pre-check would race with the operation; check first only when the check is cheap and failure is the common case. |
| Use `else` and `finally` on `try` blocks | `else` runs only when no exception fired, keeping the happy path out of the protected block. `finally` guarantees cleanup whether or not something failed. |

## Classes and Object-Oriented Design

| Practice | Detail |
|---|---|
| Prefer composition over inheritance | Inheritance hard-wires subclasses to a base class's internals. Composing collaborators keeps the pieces swappable when the relationship is "has-a" rather than "is-a". |
| Use `@property` for computed attributes | A property exposes a clean attribute interface while running validation or computation behind it, so callers never see getter/setter boilerplate. |
| Keep `__init__` to assignment | I/O or heavy computation in a constructor makes objects slow and awkward to build in tests. Move complex creation into a `@classmethod` such as `User.from_dict(data)`. |
| Define interfaces with abstract base classes | `ABC` plus `@abstractmethod` makes the contract explicit and fails fast on a missing method, which is clearer than relying on duck typing when several methods are required. |
| Use `__slots__` for high-volume classes | `__slots__` cuts per-instance memory and blocks accidental attribute creation, which matters when a class is instantiated many thousands of times. |

## Testing

| Practice | Detail |
|---|---|
| Name tests as specifications | `test_transfer_fails_when_balance_insufficient` states the scenario and expected outcome so a failure is self-explaining, unlike `test_transfer_3`. |
| Isolate tests from external systems | Mocking databases, APIs, and the filesystem keeps tests fast and deterministic, since real network and disk I/O make CI slow and flaky. |
| Prefer factories over shared fixtures for data | Factories build fresh, per-test objects, avoiding the hidden coupling where one test's mutation of a shared fixture breaks another. |
| Test behavior, not implementation | Asserting on outputs and observable effects survives refactors, whereas asserting on internal calls or private state breaks on every cleanup. |
| Use `pytest.mark.parametrize` for variants | Parametrizing turns each input set into an independent case with its own pass/fail, instead of one test that masks which variant failed. |

## Documentation

| Practice | Detail |
|---|---|
| Pick one docstring style project-wide | Consistent Google-style or NumPy-style docstrings let tooling parse them and readers scan them; mixing styles defeats both. Document parameters, returns, and raised exceptions. |
| Write docstrings in the imperative mood | `"""Return the user's full name."""` matches PEP 257 and reads as a command, keeping summaries uniform across the codebase. |
| Document constructor parameters in the class docstring | Describing the class and its `__init__` parameters together gives one place to learn how to build the object, rather than splitting the story across two docstrings. |

## Concurrency and Tooling

| Practice | Detail |
|---|---|
| Use `asyncio` for I/O-bound concurrency | `async`/`await` is the standard model for overlapping HTTP calls, queries, and file reads. Avoid mixing threads with asyncio in one path, since it reintroduces the locking hazards async was meant to avoid. |
| Use `concurrent.futures` for CPU-bound parallelism | `ProcessPoolExecutor` sidesteps the GIL for CPU-heavy work; `ThreadPoolExecutor` suits I/O-bound work when asyncio is not an option. |
| Synchronize all shared mutable state across threads | Use `threading.Lock`, `queue.Queue`, or immutable data, because unguarded races stay invisible in testing and surface only under production load. |
| Prefer `pathlib` over `os.path` | `Path` objects give an object-oriented, OS-agnostic API with operators like `/` for joining, replacing brittle manual string concatenation of paths. |
| Use structural pattern matching judiciously | `match`/`case` (3.10+) reads well for dispatching on the shape of structured data, but a plain `if`/`elif` chain is clearer for simple value checks, so do not force it. |
| Know inline script metadata | PEP 723 (`# /// script`) lets a single-file script declare its dependencies so tools like `uv run` execute it in an isolated environment without a separate project setup. |

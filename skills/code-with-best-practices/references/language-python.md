Apply these practices whenever planning, writing, or reviewing Python code. Targets Python 3.12+ (version-specific items are flagged). Generic clean-code rules live in CLAUDE.md; this reference is the Python-specific, version-current, and easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Typing](#typing)
- [Idioms and stdlib](#idioms-and-stdlib)
- [Tooling](#tooling)
- [Errors](#errors)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Typing

| Practice | Detail |
|---|---|
| Use built-in generics, not `typing` aliases | `list[int]`, `dict[str, int]`, `tuple[int, ...]`, `type[Foo]`, not `typing.List`/`Dict`/`Tuple`/`Type`. PEP 585 deprecated the aliases (removal targeted for 3.18). The deprecation is silent at runtime; only a checker/linter flags it. |
| Use `X \| None` and `A \| B`, not `Optional`/`Union` | PEP 604 shorthand (3.10+); put `None` last. |
| Return `Self`, not the class name | `typing.Self` (3.11+) makes a subclass's `return self` infer as the subclass. Use it for fluent methods, `classmethod` constructors, and `__enter__`. |
| Prefer `Protocol` over ABCs for "has these methods" | Structural subtyping (`typing.Protocol`) beats nominal inheritance when you only need a shape. `@runtime_checkable` enables `isinstance`, but it checks only that attributes exist, not their signatures. |
| Use PEP 695 syntax on 3.12 | `def first[T](x: list[T]) -> T:` and `class Box[T]:` instead of module-level `TypeVar`s; `type Point = tuple[float, float]` instead of `typing.TypeAlias` (deprecated). Aliases are lazily evaluated, so forward refs work. On 3.11, fall back to explicit `TypeVar`. |
| Annotate overrides and precise kwargs | `@typing.override` (PEP 698, 3.12) catches a renamed base method. Type `**kwargs` with `Unpack[SomeTypedDict]` (PEP 692) and preserve wrapped signatures with `ParamSpec` instead of `**kwargs: Any`. |
| Prefer `object` over `Any` for "accepts anything" | `Any` disables checking and propagates; `object` keeps it sound and forces narrowing. Reserve `Any` for genuinely inexpressible types. |
| Pick the data model by trust boundary | `@dataclass` for internal trusted data (no deps, no validation); Pydantic v2 when data crosses a boundary (API, config, user input: runtime validation, coercion, serialization, JSON Schema; Rust core); `attrs` for fine-grained validators/converters and slotted classes without full serialization. Use `frozen=True` / `NamedTuple` for immutable values. |
| Type-hint public signatures | Hints are documentation the checker verifies. Annotate parameters, returns, and attributes. |

## Idioms and stdlib

| Practice | Detail |
|---|---|
| `match` for destructuring, not as a switch | Pattern matching (3.10+) shines for structural decomposition of nested data; a plain `if`/`elif` is clearer for simple value checks, so do not force it. |
| `pathlib.Path` over `os.path` | Object-oriented, OS-agnostic path handling with `/` joining. Not a strict drop-in (trailing-slash/`.` normalization differs) and pure-Python, so `os.path` remains valid for byte paths and hot loops. |
| f-strings over `%` and `.format()` | Most readable and fastest. On 3.12 (PEP 701) f-strings can reuse the outer quote inside braces, nest arbitrarily, span lines, and use backslashes; those features raise `SyntaxError` on older versions. |
| Comprehensions and generators, capped | Prefer comprehensions over `map`/`filter`; keep to two control subexpressions or fewer, then extract a helper. Use generator expressions for large inputs to avoid materializing the full list. |
| `enumerate`, `zip`, extended unpacking | `enumerate(items)` and `zip(a, b)` over index bookkeeping; pass `zip(..., strict=True)` to error on length mismatch. `first, *rest = seq` and `a, b = b, a` over indexing. |
| Walrus to bind-and-test | `while (chunk := f.read(8192)):` removes the duplicated read; use `:=` where it cuts a repeated expression. |
| `contextlib` over hand-rolled managers | `@contextmanager` for generator-based managers, `suppress(Exc)` instead of `try/except/pass`, `ExitStack` for a variable number of contexts. Always bound resource lifetimes with `with`. |

## Tooling

| Practice | Detail |
|---|---|
| `uv` for environments, deps, and Python versions | Single Rust-based tool over `pyproject.toml` + `uv.lock` + `.python-version`, replacing pip/pip-tools/pipx/poetry/pyenv/virtualenv. Flow: `uv init`, `uv add`, `uv sync`, `uv run`, `uv lock`; `uvx` for ephemeral CLIs; `uv python install/pin`. |
| `ruff` for lint and format | `ruff format` is a Black-compatible drop-in (88 cols, double quotes, magic trailing comma); `ruff check` replaces Flake8 + isort + pyupgrade. |
| Know what Ruff enforces by default | Defaults are minimal: Pyflakes (`F`) plus non-stylistic pycodestyle (`E`). Modernization and import sorting are NOT on by default; explicitly select `UP` (pyupgrade, rewrites to `list[...]`/`X \| None`), `I` (isort), `B` (bugbear), `SIM`. "Ruff is on" does not mean idiom rewrites or import sorting are on. |
| Run a type checker in strict mode | `mypy --strict` (bundles `disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, `warn_unused_ignores`, `strict_equality`, ...) or pyright `typeCheckingMode: "strict"`; adopt per-module for gradual rollout. |
| Inline script metadata | PEP 723 (`# /// script`) lets a single file declare its deps so `uv run` executes it in an isolated environment with no project setup. |

## Errors

| Practice | Detail |
|---|---|
| Raise specific exceptions; define domain classes | A precise `ValueError` or `InsufficientFundsError` lets callers branch on the failure instead of catching everything or parsing messages. |
| Never silently swallow | `except: pass` hides the bug. Log, re-raise, or handle observably. |
| EAFP vs LBYL deliberately | Prefer `try`/`except` when failure is rare or a pre-check would race; check first only when the check is cheap and failure is common. Use `try`/`else`/`finally` to keep the happy path and cleanup separated. |
| `__slots__` for high-volume classes | Cuts per-instance memory and blocks accidental attribute creation when a class is instantiated many thousands of times. |

## Gotchas

- Mutable default arguments evaluate once at definition: `def f(acc=[])` shares one list across calls. Default to `None` and create inside the body.
- `@runtime_checkable` `isinstance` checks only that attributes exist, not their signatures, so it can pass for objects that fail static checking.
- PEP 585/604 deprecations are silent at runtime: `typing.List`/`Optional` keep working, so "it runs" is not evidence the typing is current; lean on the checker.
- `ruff format` does not sort imports; run `ruff check --select I --fix` (or `ruff check --fix`) for that.

## Sources

- [Python docs: What's New in 3.12](https://docs.python.org/3/whatsnew/3.12.html), [typing](https://docs.python.org/3/library/typing.html), [pathlib](https://docs.python.org/3/library/pathlib.html) - official; current language and stdlib behavior.
- [Typing best practices](https://typing.python.org/en/latest/reference/best_practices.html) and [PEP 585](https://peps.python.org/pep-0585/) - official typing project and standard; generics, `X | None`, deprecation timeline.
- [Astral: uv](https://docs.astral.sh/uv/), [Ruff rules](https://docs.astral.sh/ruff/rules/) and [formatter](https://docs.astral.sh/ruff/formatter/); [Black style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) - tool vendors; the de facto modern toolchain and its defaults.
- [mypy strict mode](https://mypy.readthedocs.io/en/stable/existing_code.html) and [pyright configuration](https://github.com/microsoft/pyright/blob/main/docs/configuration.md) - official; what strict mode enforces.
- [Effective Python, 3rd ed.](https://effectivepython.com/) (Brett Slatkin) - authoritative expert book; match, f-strings, comprehensions, dataclasses.
- [Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/style/) - well-regarded community reference; idioms and the mutable-default warning.

# Python archetypes (uv)

These templates are best-practice defaults, not mirrored from one of Brandon's repos (he has no local Python projects yet). Tell the user this when scaffolding, and fold any preference he states back into this file: the skill is meant to iterate.

Toolchain: uv for env + dependencies, ruff for lint + format, pytest for tests. `src/` layout. Python `>=3.12`.

- [Package](#package)
- [MCP server (Python)](#mcp-server-python)

## Package

- `pyproject.toml`:

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = ""
authors = [{ name = "Brandon Burrus", email = "brandon@burrus.io" }]
license = "MIT"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
# E/F: pyflakes + pycodestyle, I: isort, UP: pyupgrade, B: bugbear.
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- Layout (replace `<package_name>` with the snake_case import name):

```text
<project-name>/
  pyproject.toml
  src/<package_name>/__init__.py
  tests/test_<package_name>.py
  README.md
  .gitignore        # Python .gitignore: __pycache__/, .venv/, *.pyc, .pytest_cache/, dist/, .ruff_cache/
```

- `src/<package_name>/__init__.py` starts with `__version__ = "0.1.0"`.
- Scaffold dependencies with `uv add` / `uv add --dev` so `uv.lock` pins them, rather than hand-editing the dependency arrays.

## MCP server (Python)

Uses the PyPI `fastmcp` package (jlowin). This is a different project from the npm `fastmcp` (punkpeye) used by the TS MCP archetype.

- `pyproject.toml` deltas: add `fastmcp` to `dependencies` and a console-script entry point.

```toml
[project]
dependencies = ["fastmcp>=2"]

[project.scripts]
<server-name> = "<package_name>.server:main"
```

- `src/<package_name>/server.py`:

```python
from fastmcp import FastMCP

mcp = FastMCP("<server-name>")


@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
```

`mcp.run()` defaults to stdio transport. The tool here is a placeholder; the real tool/resource/prompt contract is `design-mcp`'s job, not this skill's.

## Optional add-on: GitHub Actions CI gate

Opt-in, the uv variant of the shared CI gate (suggest it for projects that will be published or shared). Runs ruff lint, a format check, and pytest on every push to `main` and every pull request. Starter gate only; richer CI is `design-cicd`'s job. Action versions are best-practice defaults; bump to the current major when scaffolding.

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run pytest
```

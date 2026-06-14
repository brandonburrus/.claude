Apply these practices whenever planning, writing, or reviewing Bash or shell scripts. Targets Bash 4+ (POSIX-sh differences are flagged). Generic clean-code rules live in CLAUDE.md; this reference is the Bash-specific, easy-to-get-wrong material. On conflict, the project's own conventions win.

## Contents

- [Header and safety](#header-and-safety)
- [Quoting and expansion](#quoting-and-expansion)
- [Tests and arithmetic](#tests-and-arithmetic)
- [Arrays and arguments](#arrays-and-arguments)
- [Files, temp, and cleanup](#files-temp-and-cleanup)
- [Functions and output](#functions-and-output)
- [Reading input](#reading-input)
- [Security](#security)
- [Tooling](#tooling)
- [Gotchas](#gotchas)
- [Sources](#sources)

## Header and safety

| Practice | Detail |
|---|---|
| Use `#!/usr/bin/env bash`, not `#!/bin/sh` | The `sh` shebang disables `[[`, `(())`, arrays, and process substitution; on many systems `sh` is dash, so Bashisms silently misbehave. `env bash` finds Bash on PATH (macOS ships Bash 3.2 at `/bin/bash`). If you genuinely target POSIX sh, write to that standard and lint with `shellcheck -s sh`. |
| `set -euo pipefail` is a net, not a guarantee | `-e` (errexit) is widely misunderstood: it does NOT fire inside `if`/`while` conditions, `&&`/`\|\|` chains, negated `!` commands, or (in older Bash) command substitution and function bodies called in a condition. Treat it as a backstop and still check critical commands explicitly. `-u` errors on unset vars (use `"${VAR:-default}"` for intentional optionals); `-o pipefail` makes a pipeline fail if any stage fails, not just the last. |
| Set `IFS=$'\n\t'` deliberately, not reflexively | Narrowing `IFS` stops space-splitting on unquoted expansions, but it is a footgun if later code relies on default splitting. Prefer fixing quoting at each site; scope `IFS` locally (`local IFS=,`) when you must change it. |

## Quoting and expansion

| Practice | Detail |
|---|---|
| Double-quote every expansion | `"$var"`, `"${var}"`, `"$@"`, `"${arr[@]}"`. Unquoted, the value undergoes word splitting (on `IFS`) and glob expansion: the single most common Bash bug. Quote even inside `[[ ]]` for habit, though `[[ ]]` suppresses splitting itself. |
| Quote command substitutions | `result="$(some_command)"`; unquoted `$(...)` splits on whitespace and globs, and trailing newlines are stripped regardless. |
| Use `${var}` braces when concatenating | `"${prefix}_suffix"` avoids referencing a variable named `prefix_suffix`. Some style guides brace all expansions for uniformity, positionals `${10}` aside. |
| `$()`, never backticks | `$(...)` nests without escaping and reads clearly; backticks need backslash-escaping when nested. |
| Use parameter expansion before reaching for tools | `"${var%/*}"` (dirname), `"${var##*/}"` (basename), `"${var:-default}"`, `"${var//old/new}"`, `"${#var}"` (length) avoid spawning `sed`/`expr`/`basename` for trivial string work. |

## Tests and arithmetic

| Practice | Detail |
|---|---|
| `[[ ... ]]`, not `[ ... ]` or `test` | `[[` does no word splitting or globbing on its operands and adds `==` glob matching and `=~` regex. POSIX sh has only `[`, where every operand must be quoted. With `[[`, quote the RIGHT side of `==`/`=~` to match literally; leave it unquoted to match as a pattern. |
| `(( ... ))` for arithmetic | `if (( count > 10 ))` beats `[ "$count" -gt 10 ]`: C-style operators, no `$`-prefix needed on names, no quoting of numbers. Note `(( expr ))` returns exit 1 when `expr` evaluates to 0, which trips `set -e` (e.g. `(( i++ ))` when `i` was 0). |
| Detect failure with `if`, not `&&`/`\|\|` | `set -e` is suppressed inside `&&`/`\|\|`, so `command && next` will not abort on failure. Use `if ! command; then handle; fi` when a step must be checked. |
| Save `PIPESTATUS` immediately | It is overwritten by the next command: `pipe=("${PIPESTATUS[@]}")` right after the pipeline if you need per-stage codes (a Bash array; not POSIX). |

## Arrays and arguments

| Practice | Detail |
|---|---|
| Use arrays for argument lists, never space-joined strings | `args=(--config "$file" --verbose); cmd "${args[@]}"` preserves arguments with spaces that a flat string `args="--config $file"` collapses and re-splits. Arrays are Bash-only; POSIX sh has only `"$@"`. |
| `"$@"`, never `$*` | `"$@"` expands to each argument as a separate quoted word; `"$*"` joins them into one string on the first IFS char, losing boundaries. |
| Build arrays from output with `mapfile`/`readarray` | `mapfile -t lines < <(command)` reads lines into an array without the subshell variable loss that `command | while read` causes. Use `-d ''` with NUL-delimited input. |
| Quote array expansions in loops | `for item in "${array[@]}"`; unquoted splits elements that contain spaces. `"${arr[@]}"` is per-element, `"${arr[*]}"` is one joined string. |

## Files, temp, and cleanup

| Practice | Detail |
|---|---|
| Never parse `ls` | Iterate a glob (`for f in ./*.txt`) or use `find ... -print0` piped to `while IFS= read -r -d '' f`. `ls` mangles names with spaces, newlines, and control chars, and may substitute `?` for nonprintables. Prefix globs with `./` so a file named `-rf` is not read as a flag. |
| Guard globs that may not match | A glob with no match expands to the literal pattern by default. Set `shopt -s nullglob` (empty instead) or `failglob`, or test existence before use. |
| `mktemp` for temp files and dirs | `tmp="$(mktemp)"` / `mktemp -d` yields unpredictable names, avoiding the symlink races and collisions of `/tmp/foo.$$`. |
| Always pair temp creation with a cleanup trap | `trap 'rm -rf "$tmp"' EXIT` removes the file on success and on early exit. Add specific signals (`trap ... INT TERM`) if you need to distinguish; EXIT covers normal and most error paths. |

## Functions and output

| Practice | Detail |
|---|---|
| Declare function variables `local` | Prevents clobbering globals on name collision. `local` also makes the name dynamically scoped to callees, which is usually what you want. |
| Split `local`/`export` from command substitution | `local x; x="$(cmd)"` not `local x="$(cmd)"`. Combined, the declaration's exit code (always 0) masks `cmd`'s failure, defeating `set -e` and `$?` checks (ShellCheck SC2155). |
| Return status, emit data on stdout | `return N` sets exit status (0-255); print results so callers do `out="$(my_func)"`. Bash has no real return values beyond the status byte. |
| Send diagnostics to stderr | `echo "error: ..." >&2` keeps stdout clean so the function composes in pipelines. |
| `printf` over `echo` for arbitrary data | `printf '%s\n' "$var"` is portable; `echo` handling of `-n`, `-e`, and backslashes varies by shell and the `xpg_echo` setting. Reserve `echo` for fixed, known-safe literals. |

## Reading input

| Practice | Detail |
|---|---|
| Always `read -r` | Without `-r`, `read` treats backslashes as escapes and mangles input. There is no reason to omit it. |
| `IFS= read -r line` to preserve whitespace | Clearing IFS for the read keeps leading and trailing whitespace the default IFS would strip. |
| Read with process substitution, not a pipe | `while IFS= read -r line; do ...; done < <(command)` runs the loop in the current shell; `command | while ...` runs it in a subshell, so variable assignments vanish at the pipe's end (Bash-only; POSIX sh lacks `<()`). |
| Loop NUL-delimited for unsafe names | `while IFS= read -r -d '' f; do ...; done < <(find . -print0)` is the only safe way to iterate arbitrary filenames. |

## Security

| Practice | Detail |
|---|---|
| Avoid `eval` | It executes a constructed string as code, the classic injection vector. Build dynamic commands as an array and run `"${cmd[@]}"`; use namerefs (`local -n`) or associative arrays for indirection. |
| Validate input before an arithmetic context | `$(( ))` evaluates its contents, so `$((untrusted))` can run code via array-index side effects. Validate numeric input (`case $x in *[!0-9]*) reject;; esac`) before using it arithmetically. |
| Guard destructive operations | Confirm a variable is non-empty and shaped as expected before `rm -rf "$var"` (`: "${dir:?must be set}"`); an empty value targets the wrong tree. |
| Quote heredoc delimiters for literal bodies | `cat <<'EOF'` disables expansion inside the body; use the unquoted `<<EOF` form only when expansion is intended and the content is trusted. |
| Check command existence up front | `command -v tool >/dev/null 2>&1 \|\| { echo "tool required" >&2; exit 1; }` fails fast with a clear message. Use `command -v`, not the non-portable `which`. |
| Mind redirection order | `cmd >file 2>&1` sends both streams to the file; `cmd 2>&1 >file` sends stderr to the original stdout, then stdout to the file. Order is left-to-right. |

## Tooling

| Practice | Detail |
|---|---|
| Gate every script on ShellCheck | It catches the quoting, splitting, and `set -e` traps above statically. Run it in CI; annotate intentional exceptions with a justified `# shellcheck disable=SCxxxx` rather than disabling globally. |
| Format with `shfmt` | A consistent formatter (`shfmt -i 2 -ci`) keeps diffs clean and is CI-checkable, the shell analogue of Prettier/Black. |
| Reconsider the language past ~100 lines | Google's guide advises rewriting in a real language once a script grows large or needs nontrivial data structures or control flow; Bash error handling and data modeling degrade fast at scale. |

## Gotchas

- `set -e` does NOT fire in `if`/`while` conditions, `&&`/`||` chains, `!`-negated commands, or command substitution; it is a backstop, not a guarantee.
- `local x="$(cmd)"` hides `cmd`'s exit status behind the declaration's success (SC2155); split the two lines.
- `(( i++ ))` returns exit 1 when the pre-increment value is 0, aborting under `set -e`; use `(( i++ )) || true` or `i=$((i+1))`.
- `command | while read ...; do count=...; done` loses `count` after the pipe: the loop ran in a subshell. Use `< <(command)`.
- An unmatched glob expands to the literal pattern unless `nullglob` is set; code that assumes zero matches breaks.
- `"$*"` joins all args into one word; only `"$@"` preserves argument boundaries.
- `PIPESTATUS` and most array/`mapfile`/`<()`/`[[ ]]` features are Bash, not POSIX sh; a `#!/bin/sh` shebang silently disables them.

## Sources

- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html) - the authoritative language reference for expansion, `set` options, arrays, and arithmetic semantics.
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) - major maintained style guide; shebang, `[[`, arrays, `local`, PIPESTATUS, and the rewrite-past-100-lines rule.
- [Bash Pitfalls (Greg's Wiki)](https://mywiki.wooledge.org/BashPitfalls) and [BashGuide](https://mywiki.wooledge.org/BashGuide) - the canonical community catalog of quoting, `ls`-parsing, subshell, `set -e`, and arithmetic-injection traps.
- [ShellCheck wiki](https://www.shellcheck.net/wiki/) (e.g. [SC2155](https://www.shellcheck.net/wiki/SC2155), [SC2086](https://www.shellcheck.net/wiki/SC2086)) - the de facto linter; each warning page documents one real-world bug class.
- [BashFAQ #105: set -e caveats](https://mywiki.wooledge.org/BashFAQ/105) - definitive treatment of why errexit cannot be relied on alone.
- [shfmt (mvdan/sh)](https://github.com/mvdan/sh) - the widely-used shell formatter for CI-enforceable consistency.

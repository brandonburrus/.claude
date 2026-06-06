Apply these practices whenever planning, writing, or reviewing Bash or shell scripts.

## Script Header

| Practice | Detail |
|---|---|
| Use `#!/bin/bash`, not `#!/bin/sh` | The `sh` shebang disables Bash features like `[[`, `(())`, arrays, and process substitution, so scripts silently behave differently across systems where `sh` is dash or another shell. |
| Set `set -euo pipefail` right after the shebang | This exits on error, treats unset variables as failures, and propagates failures from any stage of a pipeline, catching mistakes that would otherwise be swallowed. |
| Set a safe `IFS=$'\n\t'` | The default `IFS` splits on spaces, which corrupts iteration over filenames and command output. Restore the default only where space-splitting is intentional. |

## Quoting and Variable Expansion

| Practice | Detail |
|---|---|
| Always double-quote variable expansions | `"$var"`, `"${var}"`, and `"$@"` prevent word splitting and glob expansion, which is the single most common source of Bash bugs. |
| Quote command substitutions | Unquoted `$(...)` splits its output on whitespace and expands globs, so write `result="$(some_command)"` to keep the value intact. |
| Use `${var}` braces when concatenating | Braces remove ambiguity about where the variable name ends, so `"${prefix}_suffix"` does not accidentally reference a variable named `prefix_suffix`. |
| Use `$()`, never backticks | `$(command)` nests cleanly and reads clearly, whereas backticks require escaping when nested and are easy to get wrong. |

## Conditionals and Tests

| Practice | Detail |
|---|---|
| Use `[[ ... ]]`, not `[ ... ]` or `test` | `[[` avoids word splitting inside the test and supports `==` pattern matching and `=~` regex, while `[` is an external-style command that reintroduces quoting hazards. |
| Use `(( ... ))` for arithmetic comparisons | `if (( count > 10 ))` is clearer than `[ "$count" -gt 10 ]` and supports C-style operators without quoting numbers. |
| Prefer explicit `if` over `&&` or `||` chains for error handling | `set -e` does not trigger inside `&&` or `||` chains, so `if ! command; then handle_error; fi` is the only reliable way to detect failure there. |

## Error Handling

| Practice | Detail |
|---|---|
| Know what `set -e` ignores | It does not exit inside `if`, `while`, `&&` or `||` chains, or negated commands, so treat it as a safety net rather than a substitute for explicit checks. |
| Use `trap cleanup EXIT` for teardown | An `EXIT` trap runs cleanup on both success and failure, which prevents leaked temp files and half-finished state when the script aborts. |
| Guard critical commands explicitly | Pair `cd "$dir" || exit 1` and similar checks so a failed prerequisite does not let later commands run in the wrong context. |
| Save `PIPESTATUS` immediately | `PIPESTATUS` is overwritten by the very next command, so capture it with `status=("${PIPESTATUS[@]}")` before doing anything else if you need a pipeline's stage exit codes. |

## Arrays and Arguments

| Practice | Detail |
|---|---|
| Use arrays for command arguments | Building `args=("--config=$file")` and calling `command "${args[@]}"` preserves arguments containing spaces, which collapse and break when stored in a plain string. |
| Pass all arguments with `"$@"`, never `$*` | `"$@"` preserves each argument as a separate quoted word, while `$*` concatenates everything into one string and loses argument boundaries. |
| Capture output lines with `readarray`/`mapfile` | `readarray -t lines < <(command)` builds an array from output without the subshell variable loss that piping into a loop causes. |
| Quote array expansions in loops | `for item in "${array[@]}"` keeps elements with spaces intact, while unquoted expansion splits them apart. |

## Files and Paths

| Practice | Detail |
|---|---|
| Never parse `ls` output | Use a glob like `for file in *.txt` or `find ... -print0` with `read -r -d ''`, because `ls` output is mangled by spaces, newlines, and special characters in filenames. |
| Create temp files with `mktemp` | `mktemp` and `mktemp -d` produce unpredictable names, avoiding the race conditions and collisions of fixed paths like `/tmp/script_$$`. |
| Pair `mktemp` with a cleanup trap | `trap 'rm -f "$tmpfile"' EXIT` guarantees temporary files are removed even when the script exits early on error. |
| Use parameter expansion for path manipulation | `"${var%/*}"` for dirname and `"${var##*/}"` for basename avoid spawning external processes for trivial string work. |

## Security

| Practice | Detail |
|---|---|
| Never use `eval` | `eval` executes arbitrary constructed strings as code, so build dynamic commands with arrays and `"${cmd[@]}"` instead. |
| Quote and validate all external input | Arguments, environment variables, and file contents are untrusted, so quote them and check them before using them in commands or paths. |
| Validate before destructive operations | Confirm a variable is non-empty and matches an expected prefix before `rm -rf "$var"`, since an empty or unexpected value can delete the wrong tree. |
| Quote heredoc delimiters for literal content | `cat << 'EOF'` disables variable expansion inside the body, so use the unquoted form only when expansion is intended and the input is trusted. |
| Check command existence before use | `command -v tool &>/dev/null || { echo "tool not found" >&2; exit 1; }` fails fast with a clear message instead of erroring out midway through. |

## Functions and Output

| Practice | Detail |
|---|---|
| Declare function variables `local` | Marking variables `local` prevents functions from overwriting global state, which causes hard-to-trace bugs when names collide. |
| Return status, emit data on stdout | Use `return` for exit status and `echo` for results so callers can capture data with `result="$(my_func)"` while still checking success. |
| Send diagnostics to stderr | Writing errors with `>&2` keeps stdout clean for actual data, so the script composes correctly in pipelines. |
| Prefer `printf` over `echo` | `printf '%s\n' "$var"` avoids the implementation-dependent escape-sequence and flag handling that makes `echo` unreliable for arbitrary data. |

## Process Substitution and Reading

| Practice | Detail |
|---|---|
| Use process substitution to keep variables | `while read -r line; do ...; done < <(command)` avoids the subshell created by piping into a loop, where variable assignments are lost on exit. |
| Always pass `-r` to `read` | Without `-r`, `read` interprets backslashes and mangles input, so include it on every read. |
| Set `IFS=` on `read` to preserve whitespace | `while IFS= read -r line` keeps leading and trailing whitespace that the default `IFS` would otherwise strip. |

#!/bin/bash
# Block `git --no-verify` (and the -n short form on commit), which skip the
# pre-commit and pre-push hooks. Those hooks run lint, tests, secret scans, and
# commit-format checks; bypassing them lands unverified work, and skipping is
# exactly what a stuck agent reaches for. The fix is to make the hook pass, not
# to route around it.
#
# Also blocks any git command setting core.hooksPath (`git -c
# core.hooksPath=/dev/null commit`, `git config core.hooksPath ...`): pointing
# git at an empty hooks dir skips every hook with no --no-verify at all.
#
# Covers the alias/bypass spellings: the `gc` alias for `git commit`, and
# `command git ...` (which bypasses shell aliases but not this guard).
#
# Precise by construction: matches the long --no-verify flag anywhere in a git
# command, plus a short-flag cluster containing `n` in ANY flag cluster after
# `commit`/`gc` (-n, -nm, and `commit -a -n`). Commit-message payloads
# (`-m '...'`, `--message="..."`) are stripped before any pattern check, so a
# message that merely *mentions* --no-verify or core.hooksPath is not matched:
# a guard that blocks real commit messages just trains the operator to disable
# it. Only message payloads are stripped (not all quoted strings), so a
# quote-wrapped flag like `git commit "--no-verify"` is still caught.
#
# `git push -n` is deliberately allowed: for push, -n means --dry-run, not
# no-verify, and a dry run is harmless.
#
# Fails open: a non-matching or unparseable command exits 0 (allow).

COMMAND=$(jq -r '.tool_input.command // empty' < /dev/stdin 2>/dev/null)

deny() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

# Strip commit-message payloads so flag checks never fire on message prose.
# Newlines are folded to \r first so sed can match multi-line quoted messages
# (sed is line-oriented), then restored. \r in a real command is vanishingly
# rare and degrades to fail-open.
STRIPPED=$(echo "$COMMAND" | tr '\n' '\r' | sed -E "s/(-m|--message)(=| +)('[^']*'|\"[^\"]*\")//g" | tr '\r' '\n')

# A git invocation at a statement boundary, including `command git` and the
# `gc` (git commit) alias.
if echo "$STRIPPED" | grep -qE '(^|[;&|] *)(command +)?git( |$)|(^|[;&|] *)gc( |$)'; then
  if echo "$STRIPPED" | grep -qiE 'core\.hookspath'; then
    deny "BLOCKED: setting core.hooksPath reroutes git away from the repo's pre-commit/pre-push hooks entirely (lint, tests, secret and commit-format checks). Run git against the real hooks; if a hook is failing, fix what it reports instead of bypassing it. A genuinely broken hook is the user's call to skip, not the agent's."
  fi
  if echo "$STRIPPED" | grep -qE -- '--no-verify' || \
     echo "$STRIPPED" | grep -qE '(commit|(^|[;&|] *)gc)( +-[A-Za-z]+)* +-[A-Za-z]*n[A-Za-z]*' ; then
    deny "BLOCKED: \`--no-verify\` skips the pre-commit/pre-push hooks (lint, tests, secret and commit-format checks). Run the commit or push without it; if a hook is failing, fix what it reports instead of bypassing it. A genuinely broken hook is the user's call to skip, not the agent's."
  fi
fi

exit 0

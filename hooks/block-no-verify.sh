#!/bin/bash
# Block `git --no-verify` (and the -n short form on commit), which skip the
# pre-commit and pre-push hooks. Those hooks run lint, tests, secret scans, and
# commit-format checks; bypassing them lands unverified work, and skipping is
# exactly what a stuck agent reaches for. The fix is to make the hook pass, not
# to route around it.
#
# Precise by construction: matches the long --no-verify flag anywhere in a git
# command, plus a commit short-flag cluster containing `n` immediately after
# `commit` (-n, -nm). The bare `-n` is intentionally not matched elsewhere,
# because a commit message can legitimately contain the text "-n", and a guard
# that blocks real commit messages just trains the operator to disable it.
#
# `git push -n` is deliberately allowed: for push, -n means --dry-run, not
# no-verify, and a dry run is harmless.
#
# Fails open: a non-matching or unparseable command exits 0 (allow).

COMMAND=$(jq -r '.tool_input.command // empty' < /dev/stdin 2>/dev/null)

if echo "$COMMAND" | grep -qE '(^|[;&|] *)git( |$)' && \
   { echo "$COMMAND" | grep -qE -- '--no-verify' || \
     echo "$COMMAND" | grep -qE 'commit +-[A-Za-z]*n[A-Za-z]*'; }; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "BLOCKED: `--no-verify` skips the pre-commit/pre-push hooks (lint, tests, secret and commit-format checks). Run the commit or push without it; if a hook is failing, fix what it reports instead of bypassing it. A genuinely broken hook is the user'"'"'s call to skip, not the agent'"'"'s."
    }
  }'
  exit 0
fi

exit 0

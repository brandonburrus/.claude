#!/bin/bash
# Block `gh run watch` to protect the GitHub API rate limit.
#
# The GitHub API allows 5000 requests/hour. `gh run watch` polls every ~3s
# (1200 req/hr) and can exhaust the quota during a long CI run, blocking all
# subsequent gh calls for up to an hour. A single status check is enough.
#
# Fails open: a non-matching command exits 0 (allow).

COMMAND=$(jq -r '.tool_input.command // empty' < /dev/stdin 2>/dev/null)

# Anchor to a statement boundary so the pattern matches an actual invocation,
# not a mere mention of the string inside a quoted argument (e.g. a commit message).
if echo "$COMMAND" | grep -qE '(^|[;&|] *)gh +run +(watch|list[[:space:]].*--watch)'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "BLOCKED: `gh run watch` polls every ~3s and burns through the 5000/hr GitHub API rate limit. Use `gh run view <run-id>` for a single status check, or `sleep 600 && gh run view <run-id>` to wait then check once."
    }
  }'
  exit 0
fi

exit 0

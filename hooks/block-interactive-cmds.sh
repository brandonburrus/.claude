#!/bin/bash
# Block cp/mv/rm without -f to prevent interactive-prompt hangs.
#
# macOS shell profiles often alias cp/mv/rm to the -i (interactive) variants.
# An agent then hangs indefinitely on a y/n prompt it cannot answer. Blocking
# the bare forms forces the agent to retry with -f, which never prompts.
#
# Fails open: any command that does not match the risky pattern exits 0 (allow),
# so a parse failure can never wedge the Bash tool.

COMMAND=$(jq -r '.tool_input.command // empty' < /dev/stdin 2>/dev/null)

for cmd in cp mv rm; do
  # Deny when the command appears at a statement boundary without an -f flag,
  # unless it bypasses aliases via `command`, an absolute path, or a backslash.
  if echo "$COMMAND" | grep -qE "(^|[;&|] *)${cmd} " && \
     ! echo "$COMMAND" | grep -qE "(^|[;&|] *)${cmd} +-[a-eg-zA-Z]*f" && \
     ! echo "$COMMAND" | grep -qE "(command +${cmd}|/bin/${cmd}|/usr/bin/${cmd})" && \
     ! echo "$COMMAND" | grep -qE "(^|[;&|] *)\\\\${cmd} "; then
    jq -n --arg cmd "$cmd" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ("BLOCKED: `" + $cmd + "` without `-f` may hang on an interactive prompt (macOS often aliases `" + $cmd + "` to `" + $cmd + " -i`). Use `" + $cmd + " -f ...`, or prefix with `command " + $cmd + "` to bypass the alias.")
      }
    }'
    exit 0
  fi
done

exit 0

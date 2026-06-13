#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

# Bridge context metrics to a file the warn-context-budget PostToolUse hook reads.
# Hooks never receive context_window in their stdin; the statusline is the only
# component the harness feeds it to, so the statusline is the only place that can
# publish usage for the hook to consume.
SESSION=$(echo "$input" | jq -r '.session_id // empty')
if [ -n "$SESSION" ] && [[ "$SESSION" =~ ^[A-Za-z0-9_-]+$ ]]; then
    REMAINING=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
    [ -z "$REMAINING" ] && REMAINING=$(awk "BEGIN{print 100-${PCT:-0}}")
    BRIDGE_DIR="$HOME/.cache/claude-context"
    mkdir -p "$BRIDGE_DIR" 2>/dev/null \
        && printf '{"session_id":"%s","remaining_percentage":%s,"timestamp":%s}\n' \
            "$SESSION" "$REMAINING" "$(date +%s)" > "$BRIDGE_DIR/${SESSION}.json" 2>/dev/null
fi

BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
    echo " ${BRANCH} | ${MODEL} | Context: ${PCT}%"
else
    echo "${MODEL} | Context: ${PCT}%"
fi

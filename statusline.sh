#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
    echo " ${BRANCH} | ${MODEL} | Context: ${PCT}%"
else
    echo "${MODEL} | Context: ${PCT}%"
fi

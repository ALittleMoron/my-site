#!/usr/bin/env bash
# Runs make lint-file on any Python file after Edit/Write.
set -euo pipefail

INPUT=$(cat)
FILE=$(printf '%s' "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || true)

[[ -z "$FILE" ]] && exit 0
[[ "$FILE" != *.py ]] && exit 0
[[ ! -f "$FILE" ]] && exit 0

REPO=$(git -C "$(dirname "$FILE")" rev-parse --show-toplevel 2>/dev/null) || exit 0

make -C "$REPO" lint-file file="$FILE" 2>/dev/null || true
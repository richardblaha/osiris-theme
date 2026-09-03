#!/usr/bin/env bash
# Verify that the generated themes and DESIGN_SYSTEM.md still agree with the
# canonical palette in assets/tokens.json. Fails (exit 1) on any drift.
# Deps: jq (falls back to python3 if jq is missing).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOKENS="$ROOT/assets/tokens.json"
fail=0

read_token() {   # read_token '.themes.dark.bg.editor'
  if command -v jq >/dev/null 2>&1; then
    jq -r "$1" "$TOKENS"
  else
    TOKENS="$TOKENS" python3 - "$1" <<'PY'
import json, os, sys
d = json.load(open(os.environ["TOKENS"], encoding="utf-8"))
for k in sys.argv[1].strip(".").split("."):
    d = d[k]
print(d)
PY
  fi
}

check() {  # check <label> <expected-hex> <file...>
  local label="$1" hex="$2"; shift 2
  local lc; lc="$(printf '%s' "$hex" | tr 'A-F' 'a-f')"
  if ! grep -iqF "$hex" "$@"; then
    echo "  MISS  $label ($hex) not found in: $*"
    fail=1
  fi
}

echo "check-tokens: comparing against $TOKENS"

DARK="$ROOT/vscode/themes/osiris-dark-color-theme.json"
LIGHT="$ROOT/vscode/themes/osiris-light-color-theme.json"
DS="$ROOT/docs/DESIGN_SYSTEM.md"
PREVIEW="$ROOT/docs/preview/styles.css"

# --- dark ---
for path in \
  '.accent.primary.dark:#00f2fe' \
  '.accent.secondary.dark:#ff2a85' \
  '.themes.dark.bg.editor:#0d1117' \
  '.themes.dark.bg.sidebar:#161b22' \
  '.themes.dark.bg.statusbar:#00f2fe' \
  '.themes.dark.text.primary:#e6edf3' \
  '.themes.dark.syntax.string:#a5d6ff' \
  '.themes.dark.syntax.type:#79c0ff' \
  '.themes.dark.syntax.property:#ffa198'
do
  key="${path%%:*}"; want="${path##*:}"
  got="$(read_token "$key")"
  [ "$got" = "$want" ] || { echo "  DRIFT $key: tokens.json=$got expected=$want"; fail=1; }
  check "dark $key" "$want" "$DARK" "$DS" "$PREVIEW"
done

# --- light ---
for path in \
  '.accent.primary.light:#0969da' \
  '.accent.secondary.light:#e01a76' \
  '.themes.light.bg.editor:#ffffff' \
  '.themes.light.bg.statusbar:#0969da' \
  '.themes.light.text.primary:#1f2328'
do
  key="${path%%:*}"; want="${path##*:}"
  got="$(read_token "$key")"
  [ "$got" = "$want" ] || { echo "  DRIFT $key: tokens.json=$got expected=$want"; fail=1; }
  check "light $key" "$want" "$LIGHT" "$DS"
done

if [ "$fail" -ne 0 ]; then
  echo "check-tokens: FAILED"
  exit 1
fi
echo "check-tokens: OK"

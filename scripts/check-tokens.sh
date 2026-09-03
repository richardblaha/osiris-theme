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
VITEPRESS="$ROOT/vitepress/theme/osiris.css"
BOOTSTRAP_VARS="$ROOT/bootstrap/scss/_variables.scss"
BOOTSTRAP_DARK="$ROOT/bootstrap/scss/_dark.scss"
FF_DARK="$ROOT/browsers/firefox-dark/manifest.json"
FF_LIGHT="$ROOT/browsers/firefox-light/manifest.json"
ICON_DS="$ROOT/docs/ICONOGRAPHY.md"

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

# --- vitepress (dual-variant stylesheet: both accents live in one file) ---
for path in \
  '.accent.primary.dark:#00f2fe' \
  '.accent.secondary.dark:#ff2a85' \
  '.accent.primary.light:#0969da' \
  '.accent.secondary.light:#e01a76' \
  '.themes.dark.bg.editor:#0d1117' \
  '.themes.dark.bg.sidebar:#161b22' \
  '.themes.light.text.primary:#1f2328'
do
  key="${path%%:*}"; want="${path##*:}"
  check "vitepress $key" "$want" "$VITEPRESS"
done

# --- bootstrap (scss: light drives _variables.scss, dark drives _dark.scss) ---
for path in \
  '.accent.primary.light:#0969da' \
  '.accent.secondary.light:#e01a76' \
  '.themes.light.text.primary:#1f2328'
do
  key="${path%%:*}"; want="${path##*:}"
  check "bootstrap $key" "$want" "$BOOTSTRAP_VARS"
done
for path in \
  '.accent.primary.dark:#00f2fe' \
  '.accent.secondary.dark:#ff2a85' \
  '.themes.dark.bg.editor:#0d1117' \
  '.themes.dark.bg.sidebar:#161b22'
do
  key="${path%%:*}"; want="${path##*:}"
  check "bootstrap $key" "$want" "$BOOTSTRAP_DARK"
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

# --- browser themes (Firefox manifests carry the ramp as hex) ---
for path in \
  '.accent.primary.dark:#00f2fe' \
  '.themes.dark.bg.titlebar:#0d1117' \
  '.themes.dark.bg.sidebar:#161b22' \
  '.themes.dark.text.primary:#e6edf3'
do
  key="${path%%:*}"; want="${path##*:}"
  check "firefox-dark $key" "$want" "$FF_DARK"
done
for path in \
  '.accent.primary.light:#0969da' \
  '.themes.light.bg.editor:#ffffff' \
  '.themes.light.text.primary:#1f2328'
do
  key="${path%%:*}"; want="${path##*:}"
  check "firefox-light $key" "$want" "$FF_LIGHT"
done

# --- terminal ANSI palette mirrors terminal.ansi* in the committed VS Code themes ---
for path in \
  '.terminal.dark.palette[1] ansiRed:#ff5555' \
  '.terminal.dark.palette[2] ansiGreen:#3fb950' \
  '.terminal.dark.palette[5] ansiMagenta:#ff2a85' \
  '.terminal.dark.palette[6] ansiCyan:#00f2fe' \
  '.terminal.dark.palette[12] ansiBrightBlue:#a5d6ff'
do
  key="${path%%:*}"; want="${path##*:}"
  check "terminal $key" "$want" "$DARK"
done
for path in \
  '.terminal.light.palette[4] ansiBlue:#0969da' \
  '.terminal.light.palette[5] ansiMagenta:#e01a76' \
  '.terminal.light.palette[10] ansiBrightGreen:#0f6a2e'
do
  key="${path%%:*}"; want="${path##*:}"
  check "terminal $key" "$want" "$LIGHT"
done

# --- iconography (glyph source + maps resolve; ICONOGRAPHY.md agrees) ---
if command -v python3 >/dev/null 2>&1; then
  ROOT="$ROOT" python3 - <<'PY' || fail=1
import json, os, sys
root = os.environ["ROOT"]
def L(*p): return json.load(open(os.path.join(root, *p), encoding="utf-8"))
assert L("assets", "tokens.json")["icon"]["grid"] == 24
glyphs = set(L("iconography", "glyphs.json")["glyphs"])
bad = []
ft = L("iconography", "map", "filetypes.json")
for sec in ("fileExtensions", "fileNames"):
    bad += [f"filetypes.{sec}.{k}" for k, v in ft[sec].items() if v["glyph"] not in glyphs]
for sec in ("folderNames", "folderNamesExpanded"):
    bad += [f"filetypes.{sec}.{k}" for k, v in ft[sec].items() if v not in glyphs]
xd = L("iconography", "map", "xdg.json")
for cat, m in xd["icons"].items():
    bad += [f"xdg.icons.{cat}.{k}" for k, v in m.items() if v not in glyphs]
pi = L("iconography", "map", "producticons.json")
missing_pi = [v for k, v in pi.items() if not k.startswith("$") and v not in glyphs]
if bad:
    print("  ICON  unresolved glyph refs: " + ", ".join(bad[:8]) +
          (f" (+{len(bad)-8} more)" if len(bad) > 8 else ""))
if missing_pi:
    print(f"  ICON  producticons → {len(set(missing_pi))} unknown glyph(s): {sorted(set(missing_pi))}")
sys.exit(1 if bad or missing_pi else 0)
PY
  check "iconography grid" "24" "$ICON_DS"
  check "iconography accent" "#00f2fe" "$ICON_DS"
fi

if [ "$fail" -ne 0 ]; then
  echo "check-tokens: FAILED"
  exit 1
fi
echo "check-tokens: OK"

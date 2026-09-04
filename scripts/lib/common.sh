# shellcheck shell=bash
# Shared helpers for the OSIRIS theme build. Source, don't execute.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOKENS_JSON="$REPO_ROOT/assets/tokens.json"
BUILD_DIR="${BUILD_DIR:-$REPO_ROOT/build}"
DIST_DIR="${DIST_DIR:-$REPO_ROOT/dist}"
VERSION="$(cat "$REPO_ROOT/VERSION" 2>/dev/null || echo 0.1.0)"

log()  { printf '\033[36m[osiris]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[osiris] warn:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31m[osiris] error:\033[0m %s\n' "$*" >&2; exit 1; }

have() { command -v "$1" >/dev/null 2>&1; }

# tok '.themes.dark.bg.editor'  ->  #0d1117
tok() {
  if have jq; then
    jq -r "$1" "$TOKENS_JSON"
  else
    TOKENS_JSON="$TOKENS_JSON" python3 - "$1" <<'PY'
import json, os, sys
d = json.load(open(os.environ["TOKENS_JSON"], encoding="utf-8"))
for k in sys.argv[1].strip(".").split("."):
    d = d[k]
print(d)
PY
  fi
}

# Rasterise an SVG to PNG at WxH using whatever is available.
rasterise_svg() {
  local svg="$1" png="$2" w="$3" h="$4"
  mkdir -p "$(dirname "$png")"
  if have rsvg-convert; then
    rsvg-convert -w "$w" -h "$h" -o "$png" "$svg"
  elif have inkscape; then
    inkscape "$svg" --export-type=png "--export-filename=$png" \
      "--export-width=$w" "--export-height=$h" >/dev/null 2>&1
  elif have convert; then
    convert -background none -density 200 -resize "${w}x${h}" "$svg" "$png"
  elif python3 -c 'import cairosvg' 2>/dev/null; then
    python3 -c "import cairosvg,sys;cairosvg.svg2png(url=sys.argv[1],write_to=sys.argv[2],output_width=$w,output_height=$h)" "$svg" "$png"
  else
    die "no SVG rasteriser found (need rsvg-convert / inkscape / imagemagick / cairosvg)"
  fi
}

# Populate $BUILD_DIR/fonts/FiraCode-{Regular,Medium}.ttf for grub-mkfont.
# Tries, in order: files already there → system fonts-firacode → the pinned
# upstream release. Returns non-zero (build falls back to unicode.pf2) only when
# all three fail.
FIRA_CODE_VERSION="${FIRA_CODE_VERSION:-6.2}"
ensure_fira_ttf() {
  local d="$BUILD_DIR/fonts" style sys
  mkdir -p "$d"
  if [ ! -f "$d/FiraCode-Regular.ttf" ]; then
    for style in Regular Medium; do
      sys="$(fc-list 2>/dev/null | grep -oiE '/[^:]*FiraCode-'"$style"'\.ttf' | head -1 || true)"
      [ -f "$sys" ] || sys="$(find /usr/share/fonts /usr/local/share/fonts "$HOME/.local/share/fonts" \
              -name "FiraCode-$style.ttf" 2>/dev/null | head -1 || true)"
      [ -f "$sys" ] && cp "$sys" "$d/FiraCode-$style.ttf" || true
    done
  fi
  if [ ! -f "$d/FiraCode-Regular.ttf" ] && have curl && have unzip; then
    local tmp; tmp="$(mktemp -d)"
    if curl -fsSL -o "$tmp/f.zip" \
        "https://github.com/tonsky/FiraCode/releases/download/${FIRA_CODE_VERSION}/Fira_Code_v${FIRA_CODE_VERSION}.zip" \
        2>/dev/null && unzip -q -o "$tmp/f.zip" -d "$tmp" 2>/dev/null; then
      cp "$tmp"/ttf/FiraCode-Regular.ttf "$tmp"/ttf/FiraCode-Medium.ttf "$d/" 2>/dev/null || true
    fi
    rm -rf "$tmp"
  fi
  [ -f "$d/FiraCode-Regular.ttf" ]
}

# Expand @TOKEN@ placeholders in the GNOME Shell template for one variant.
render_gnome_shell() {
  local variant="$1" infile="$2" outfile="$3"
  local acc acc_fg sec panel surface hover border fg fg_dim fg_muted sel
  local success warning error
  acc="$(tok ".accent.primary.$variant")"
  sec="$(tok ".accent.secondary.$variant")"
  panel="$(tok ".themes.$variant.bg.activitybar")"
  surface="$(tok ".themes.$variant.bg.sidebar")"
  hover="$(tok ".themes.$variant.bg.hover")"
  border="$(tok ".themes.$variant.border.strong")"
  fg="$(tok ".themes.$variant.text.primary")"
  fg_dim="$(tok ".themes.$variant.text.secondary")"
  fg_muted="$(tok ".themes.$variant.text.muted")"
  sel="$(tok ".themes.$variant.bg.selection")"
  success="$(tok ".state.success.$variant")"
  warning="$(tok ".state.warning.$variant")"
  error="$(tok ".state.error.$variant")"
  acc_fg="$(tok ".themes.$variant.text.inverse")"

  sed -e "s|@ACCENT@|$acc|g" \
      -e "s|@ACCENT_FG@|$acc_fg|g" \
      -e "s|@ACCENT_SOFT@|${acc}26|g" \
      -e "s|@ACCENT_DIM@|${acc}14|g" \
      -e "s|@SECONDARY@|$sec|g" \
      -e "s|@SECONDARY_SOFT@|${sec}26|g" \
      -e "s|@PANEL@|$panel|g" \
      -e "s|@SURFACE@|$surface|g" \
      -e "s|@SURFACE_HOVER@|$hover|g" \
      -e "s|@SELECTION@|$sel|g" \
      -e "s|@BORDER@|$border|g" \
      -e "s|@FG@|$fg|g" \
      -e "s|@FG_DIM@|$fg_dim|g" \
      -e "s|@FG_MUTED@|$fg_muted|g" \
      -e "s|@SUCCESS@|$success|g" \
      -e "s|@SUCCESS_SOFT@|${success}26|g" \
      -e "s|@WARNING@|$warning|g" \
      -e "s|@WARNING_SOFT@|${warning}26|g" \
      -e "s|@ERROR@|$error|g" \
      -e "s|@ERROR_SOFT@|${error}26|g" \
      "$infile" > "$outfile"
}

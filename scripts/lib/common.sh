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

# Expand @TOKEN@ placeholders in the GNOME Shell template for one variant.
render_gnome_shell() {
  local variant="$1" infile="$2" outfile="$3"
  local acc acc_fg sec panel surface hover border fg fg_dim success warning error
  acc="$(tok ".accent.primary.$variant")"
  sec="$(tok ".accent.secondary.$variant")"
  panel="$(tok ".themes.$variant.bg.activitybar")"
  surface="$(tok ".themes.$variant.bg.sidebar")"
  hover="$(tok ".themes.$variant.bg.hover")"
  border="$(tok ".themes.$variant.border.strong")"
  fg="$(tok ".themes.$variant.text.primary")"
  fg_dim="$(tok ".themes.$variant.text.secondary")"
  success="$(tok ".state.success.$variant")"
  warning="$(tok ".state.warning.$variant")"
  error="$(tok ".state.error.$variant")"
  if [ "$variant" = "dark" ]; then acc_fg="#04151a"; else acc_fg="#ffffff"; fi

  sed -e "s|@ACCENT@|$acc|g" \
      -e "s|@ACCENT_FG@|$acc_fg|g" \
      -e "s|@ACCENT_SOFT@|${acc}26|g" \
      -e "s|@SECONDARY@|$sec|g" \
      -e "s|@SECONDARY_SOFT@|${sec}26|g" \
      -e "s|@PANEL@|$panel|g" \
      -e "s|@SURFACE@|$surface|g" \
      -e "s|@SURFACE_HOVER@|$hover|g" \
      -e "s|@BORDER@|$border|g" \
      -e "s|@FG@|$fg|g" \
      -e "s|@FG_DIM@|$fg_dim|g" \
      -e "s|@SUCCESS@|$success|g" \
      -e "s|@WARNING@|$warning|g" \
      -e "s|@ERROR@|$error|g" \
      "$infile" > "$outfile"
}

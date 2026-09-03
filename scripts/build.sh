#!/usr/bin/env bash
# ============================================================================
# OSIRIS themes — build orchestrator
#
#   scripts/build.sh [target ...]
#
# Targets:
#   all         everything below (default)
#   tokens      run check-tokens.sh (palette drift guard)
#   vscode      -> build/vscode/osiris-theme-<ver>.vsix   (needs: node + vsce)
#   gtk         -> build/themes/Osiris{,-Light}/gtk-{3.0,4.0}/
#   gnome       -> build/themes/Osiris{,-Light}/gnome-shell/
#   plasma      -> build/plasma/{color-schemes,Kvantum,aurorae,desktoptheme}/
#   desktop     gtk + gnome + plasma
#   grub        -> build/grub/osiris/  (theme.txt + pixmaps + icons + fonts)
#   wallpapers  -> build/wallpapers/   (PNGs + GNOME XML + KDE packages)
#   pages       -> build/pages/        (docs/ site for GitHub Pages)
#   clean       rm -rf build/ dist/
# ============================================================================
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
# shellcheck source=scripts/lib/common.sh
source scripts/lib/common.sh

TARGETS=("${@:-all}")

want() { [[ " ${TARGETS[*]} " == *" all "* || " ${TARGETS[*]} " == *" $1 "* ]]; }

# ---------------------------------------------------------------------------
build_tokens() {
  log "checking palette drift"
  bash scripts/check-tokens.sh
}

# ---------------------------------------------------------------------------
build_vscode() {
  log "packaging VS Code extension"
  local d="$BUILD_DIR/vscode"
  rm -rf "$d"; mkdir -p "$d"
  cp -r vscode/. "$d/"
  ( cd "$d"
    # sync version from repo VERSION
    node -e "const f='package.json',j=require('./'+f);j.version='$VERSION';require('fs').writeFileSync(f,JSON.stringify(j,null,2)+'\n')"
    # icon.png from icon.svg
    if [ ! -f icon.png ]; then
      rasterise_svg icon.svg icon.png 256 256 || warn "icon.png not generated; unset 'icon' in package.json if vsce fails"
    fi
    if have vsce; then VSCE=vsce
    elif have npx; then VSCE="npx --yes @vscode/vsce"
    else die "need 'vsce' or 'npx' to package the extension"; fi
    $VSCE package --no-dependencies --out "osiris-theme-$VERSION.vsix"
  )
  mkdir -p "$DIST_DIR"; cp "$d/osiris-theme-$VERSION.vsix" "$DIST_DIR/"
  log "  -> $DIST_DIR/osiris-theme-$VERSION.vsix"
}

# ---------------------------------------------------------------------------
assemble_gtk_variant() {   # <variant> <ThemeName>
  local variant="$1" name="$2"
  local t="$BUILD_DIR/themes/$name"
  mkdir -p "$t/gtk-3.0" "$t/gtk-4.0"

  cat desktop/gtk-common/colors-$variant.css desktop/gtk-common/widgets.css \
      desktop/gtk-3.0/gtk3.css > "$t/gtk-3.0/gtk.css"
  cat desktop/gtk-common/colors-$variant.css desktop/gtk-common/widgets.css \
      desktop/gtk-4.0/gtk4.css > "$t/gtk-4.0/gtk.css"
  cp "$t/gtk-3.0/gtk.css" "$t/gtk-3.0/gtk-dark.css"   # some apps look for -dark
  cp desktop/gtk-common/colors-$variant.css "$t/gtk-4.0/colors.css"

  sed -e "s|@THEME_NAME@|$name|g" -e "s|@VARIANT@|$variant|g" \
      desktop/index.theme.in > "$t/index.theme"
}

build_gtk() {
  log "assembling GTK themes"
  assemble_gtk_variant dark  Osiris
  assemble_gtk_variant light Osiris-Light
}

# ---------------------------------------------------------------------------
build_gnome() {
  log "rendering GNOME Shell themes"
  for pair in "dark:Osiris" "light:Osiris-Light"; do
    local variant="${pair%%:*}" name="${pair##*:}"
    local g="$BUILD_DIR/themes/$name/gnome-shell"
    mkdir -p "$g/assets"
    render_gnome_shell "$variant" desktop/gnome-shell/gnome-shell.css.in "$g/gnome-shell.css"
    cp -r desktop/gnome-shell/assets/. "$g/assets/"
  done
}

# ---------------------------------------------------------------------------
build_plasma() {
  log "assembling KDE Plasma / Qt themes"
  local p="$BUILD_DIR/plasma"
  rm -rf "$p"; mkdir -p "$p/color-schemes" "$p/aurorae" "$p/desktoptheme"

  cp desktop/plasma/color-schemes/*.colors "$p/color-schemes/"
  cp -r desktop/plasma/aurorae/. "$p/aurorae/"
  cp -r desktop/plasma/desktoptheme/. "$p/desktoptheme/"

  for v in Dark Light; do
    local kv="$p/Kvantum/Osiris$v"
    mkdir -p "$kv"
    cp "desktop/plasma/Kvantum/Osiris$v/Osiris$v.kvconfig" "$kv/"
    local lc; lc="$(printf '%s' "$v" | tr 'A-Z' 'a-z')"
    if have python3; then
      python3 scripts/lib/gen_kvantum_svg.py "$lc" "$kv/Osiris$v.svg" || warn "Kvantum SVG generation failed"
    else
      warn "python3 missing — Kvantum SVG not generated"
    fi
  done
}

# ---------------------------------------------------------------------------
build_grub() {
  log "building GRUB2 theme"
  local g="$BUILD_DIR/grub/osiris"
  rm -rf "$g"; mkdir -p "$g"
  cp boot/grub/theme.txt "$g/"
  rasterise_svg boot/grub/background.svg "$g/background.png" 1920 1080
  rasterise_svg assets/icons/osiris-logo.svg "$g/logo.png" 96 96

  if have python3 && python3 -c 'import PIL' 2>/dev/null; then
    python3 scripts/lib/gen_grub_assets.py "$g"
  else
    warn "Pillow missing — GRUB pixmaps/icons not generated (theme still usable, falls back to solid boxes)"
  fi

  # optional custom icon overrides
  for svg in boot/grub/icons/*.svg; do
    [ -e "$svg" ] || continue
    rasterise_svg "$svg" "$g/icons/$(basename "${svg%.svg}").png" 32 32
  done

  # fonts
  mkdir -p "$g"
  if have grub-mkfont && [ -d "$BUILD_DIR/fonts" ]; then
    for s in 13 14 16 18; do
      grub-mkfont -s "$s" -o "$g/firacode-$s.pf2" "$BUILD_DIR/fonts/FiraCode-Regular.ttf" 2>/dev/null || true
    done
    [ -f "$BUILD_DIR/fonts/FiraCode-Medium.ttf" ] && \
      grub-mkfont -s 18 -o "$g/firacode-medium-18.pf2" "$BUILD_DIR/fonts/FiraCode-Medium.ttf" 2>/dev/null || true
  else
    warn "grub-mkfont or Fira Code TTF unavailable — rewriting theme.txt to use unicode.pf2"
    sed -i 's/"Fira Code [A-Za-z]* \([0-9]*\)"/"Unifont Regular \1"/g' "$g/theme.txt" || true
    for u in /usr/share/grub/unicode.pf2 /boot/grub/fonts/unicode.pf2; do
      [ -f "$u" ] && cp "$u" "$g/unicode.pf2" && break
    done
  fi
  log "  -> $g"
}

# ---------------------------------------------------------------------------
build_wallpapers() {
  log "generating wallpapers"
  if have python3; then
    python3 scripts/generate-wallpapers.py --out "$BUILD_DIR/wallpapers"
  else
    die "python3 required for wallpaper generation"
  fi
}

# ---------------------------------------------------------------------------
build_pages() {
  log "staging GitHub Pages site"
  local s="$BUILD_DIR/pages"
  rm -rf "$s"; mkdir -p "$s"
  cp -r docs/preview/. "$s/"
  cp docs/DESIGN_SYSTEM.md "$s/DESIGN_SYSTEM.md"
  cp assets/tokens.json "$s/tokens.json"
  touch "$s/.nojekyll"
  log "  -> $s (entry: index.html)"
}

# ---------------------------------------------------------------------------
for tgt in tokens vscode gtk gnome plasma grub wallpapers pages; do
  case "$tgt" in
    gtk|gnome|plasma) want "$tgt" || want desktop || continue ;;
    *) want "$tgt" || continue ;;
  esac
  "build_$tgt"
done

if [[ " ${TARGETS[*]} " == *" clean "* ]]; then
  log "cleaning"; rm -rf "$BUILD_DIR" "$DIST_DIR"
fi

log "done: ${TARGETS[*]}"

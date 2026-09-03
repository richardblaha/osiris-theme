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
#   vitepress   -> dist/osiris-vitepress-theme-<ver>.tgz  (needs: npm)
#   bootstrap   -> dist/osiris-bootstrap-theme-<ver>.tgz  (needs: npm)
#   npm         vitepress + bootstrap
#   icons       -> build/icons/Osiris/   (XDG icon theme: index.theme + scalable/ + sizes)
#   terminal    -> build/terminal/       (GNOME Terminal / Ptyxis / Konsole schemes)
#   browsers    -> dist/osiris-{chromium,firefox}-{dark,light}-<ver>.zip
#   gtk         -> build/themes/Osiris{,-Light}/gtk-{3.0,4.0}/ + metacity-1/
#   gnome       -> build/themes/Osiris{,-Light}/gnome-shell/
#   sourceview  -> build/sourceview/Osiris{,-Light}.xml  (GtkSourceView style schemes)
#   themes      -> dist/osiris-gnome-theme-<ver>.tar.gz   (GTK+Shell+Metacity tarball)
#   plasma      -> build/plasma/{color-schemes,Kvantum,aurorae,desktoptheme}/
#   desktop     gtk + gnome + sourceview + plasma
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
  # generate the file + product icon themes from iconography/ into the build copy
  if have python3; then
    python3 scripts/lib/gen_icons.py vscode-file "$d"
    python3 scripts/lib/gen_icons.py vscode-product "$d"
  else
    warn "python3 missing — icon themes not generated; dropping them from package.json"
    node -e "const f='$d/package.json',j=require('./'+f);delete j.contributes.iconThemes;delete j.contributes.productIconThemes;require('fs').writeFileSync(f,JSON.stringify(j,null,2)+'\n')"
  fi
  ( cd "$d"
    # sync version from repo VERSION
    node -e "const f='package.json',j=require('./'+f);j.version='$VERSION';require('fs').writeFileSync(f,JSON.stringify(j,null,2)+'\n')"
    # icon.png from icon.svg
    if [ ! -f icon.png ]; then
      rasterise_svg icon.svg icon.png 256 256 || warn "icon.png not generated; unset 'icon' in package.json if vsce fails"
    fi
    if [ ! -f producticons/osiris-symbols.woff ]; then
      warn "osiris-symbols.woff missing (fantasticon unavailable) — dropping product icon theme"
      node -e "const f='package.json',j=require('./'+f);delete j.contributes.productIconThemes;require('fs').writeFileSync(f,JSON.stringify(j,null,2)+'\n')"
      rm -rf producticons
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
build_icons() {
  log "generating XDG icon theme"
  have python3 || die "python3 required for the icon theme"
  local d="$BUILD_DIR/icons"
  rm -rf "$d"; mkdir -p "$d"
  python3 scripts/lib/gen_icons.py xdg "$d"
  # a lowercase-name copy some tools expect
  [ -d "$d/Osiris" ] && ln -sfn Osiris "$d/osiris" 2>/dev/null || true
  log "  -> $d/Osiris"
}

# ---------------------------------------------------------------------------
build_terminal() {
  log "generating terminal colour schemes"
  have python3 || die "python3 required for the terminal schemes"
  local d="$BUILD_DIR/terminal"
  rm -rf "$d"; mkdir -p "$d"
  python3 scripts/lib/gen_terminal.py all "$d"
  log "  -> $d (gnome-terminal / ptyxis / konsole)"
}

# ---------------------------------------------------------------------------
build_browsers() {
  log "packaging browser themes"
  have zip || die "'zip' required to package the browser themes"
  local d="$BUILD_DIR/browsers"
  rm -rf "$d"; mkdir -p "$d" "$DIST_DIR"
  cp -r browsers/. "$d/"
  rm -f "$d/README.md"
  ( cd "$d"
    for variant in chromium-dark chromium-light firefox-dark firefox-light; do
      [ -d "$variant" ] || continue
      node -e "const f='$variant/manifest.json',j=require('./'+f);j.version='$VERSION';require('fs').writeFileSync(f,JSON.stringify(j,null,2)+'\n')"
      ( cd "$variant" && zip -qr "../osiris-$variant-$VERSION.zip" . -x '.*' )
      cp "osiris-$variant-$VERSION.zip" "$DIST_DIR/"
    done
  )
  log "  -> $DIST_DIR/osiris-{chromium,firefox}-{dark,light}-$VERSION.zip"
}

# ---------------------------------------------------------------------------
# npm_pack <dir> [install]  — copy the package to build/, sync its version from
# VERSION, optionally install deps (for a build/prepack step), `npm pack` -> dist/
npm_pack() {
  local dir="$1" install="${2:-}"
  have npm || die "npm required to build the '$dir' package"
  local d="$BUILD_DIR/$dir"
  rm -rf "$d"; mkdir -p "$d" "$DIST_DIR"
  cp -r "$dir/." "$d/"
  rm -rf "$d/node_modules"
  ( cd "$d"
    node -e "const f='package.json',j=require('./'+f);j.version='$VERSION';require('fs').writeFileSync(f,JSON.stringify(j,null,2)+'\n')"
    if [ -n "$install" ]; then
      if [ -f package-lock.json ]; then npm ci --no-audit --no-fund
      else npm install --no-audit --no-fund; fi
    fi
    npm pack --pack-destination "$DIST_DIR"
  )
}

build_vitepress() {
  log "packing osiris-vitepress-theme"
  npm_pack vitepress
  log "  -> $DIST_DIR/osiris-vitepress-theme-$VERSION.tgz"
}

build_bootstrap() {
  log "compiling + packing osiris-bootstrap-theme"
  npm_pack bootstrap install   # prepack runs `npm run build` -> dist/osiris-bootstrap.css
  log "  -> $DIST_DIR/osiris-bootstrap-theme-$VERSION.tgz"
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

  # Metacity / Marco decoration (GNOME Flashback, MATE, Xorg fallback)
  local acc_fg; acc_fg="$(tok ".themes.$variant.text.inverse")"
  mkdir -p "$t/metacity-1"
  sed -e "s|@THEME_NAME@|$name|g" -e "s|@VARIANT@|$variant|g" \
      -e "s|@TITLEBAR@|$(tok ".themes.$variant.bg.titlebar")|g" \
      -e "s|@TITLEBAR_BACKDROP@|$(tok ".themes.$variant.bg.activitybar")|g" \
      -e "s|@FG@|$(tok ".themes.$variant.text.primary")|g" \
      -e "s|@FG_DIM@|$(tok ".themes.$variant.text.secondary")|g" \
      -e "s|@ACCENT@|$(tok ".accent.primary.$variant")|g" \
      -e "s|@ACCENT_FG@|$acc_fg|g" \
      -e "s|@SECONDARY@|$(tok ".accent.secondary.$variant")|g" \
      -e "s|@BORDER@|$(tok ".themes.$variant.border.strong")|g" \
      -e "s|@HOVER@|$(tok ".themes.$variant.bg.hover")|g" \
      -e "s|@ERROR@|$(tok ".state.error.$variant")|g" \
      desktop/metacity-1/metacity-theme-3.xml.in > "$t/metacity-1/metacity-theme-3.xml"
}

build_gtk() {
  log "assembling GTK themes"
  assemble_gtk_variant dark  Osiris
  assemble_gtk_variant light Osiris-Light
}

# ---------------------------------------------------------------------------
build_sourceview() {
  log "generating GtkSourceView style schemes (GNOME Text Editor / gedit / Builder)"
  have python3 || die "python3 required for the GtkSourceView schemes"
  local d="$BUILD_DIR/sourceview"
  rm -rf "$d"; mkdir -p "$d"
  python3 scripts/lib/gen_sourceview.py "$d"
  log "  -> $d/Osiris{,-Light}.xml"
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
# Distributable tarball of the GTK + GNOME Shell + Metacity theme (both variants)
# for distros without the .deb / .rpm (Arch, openSUSE, NixOS, gnome-look.org …).
build_themes() {
  log "packaging the desktop theme tarball"
  have tar || die "'tar' required"
  [ -d "$BUILD_DIR/themes/Osiris" ] || build_gtk
  [ -d "$BUILD_DIR/themes/Osiris/gnome-shell" ] || build_gnome
  [ -d "$BUILD_DIR/sourceview" ] || build_sourceview
  local s="$BUILD_DIR/theme-pkg/osiris-gnome-theme-$VERSION"
  rm -rf "$BUILD_DIR/theme-pkg"; mkdir -p "$s" "$DIST_DIR"
  cp -r "$BUILD_DIR/themes/Osiris" "$BUILD_DIR/themes/Osiris-Light" "$s/"
  mkdir -p "$s/gtksourceview/styles"
  cp "$BUILD_DIR/sourceview/"*.xml "$s/gtksourceview/styles/"
  cat > "$s/README.md" <<EOF
# OSIRIS GNOME theme ($VERSION)

GTK 3/4 + libadwaita, GNOME Shell, Metacity — dark (\`Osiris\`) and light
(\`Osiris-Light\`). Plus the \`osiris\` / \`osiris-light\` GtkSourceView schemes
for GNOME Text Editor / gedit / Builder.

## Install (per-user)

    cp -r Osiris Osiris-Light ~/.local/share/themes/
    for v in 5 4 3.0; do
      mkdir -p ~/.local/share/gtksourceview-\$v/styles
      cp gtksourceview/styles/*.xml ~/.local/share/gtksourceview-\$v/styles/
    done

Then, with GNOME Tweaks (or \`gsettings\`):

    gsettings set org.gnome.desktop.interface gtk-theme 'Osiris'
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
    # GNOME Shell theme needs the "User Themes" extension:
    gsettings set org.gnome.shell.extensions.user-theme name 'Osiris'
EOF
  ( cd "$BUILD_DIR/theme-pkg" && tar -czf "$DIST_DIR/osiris-gnome-theme-$VERSION.tar.gz" \
      "osiris-gnome-theme-$VERSION" )
  log "  -> $DIST_DIR/osiris-gnome-theme-$VERSION.tar.gz"
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
for tgt in tokens vscode vitepress bootstrap icons terminal browsers gtk gnome plasma sourceview themes grub wallpapers pages; do
  case "$tgt" in
    gtk|gnome|plasma|sourceview) want "$tgt" || want desktop || continue ;;
    vitepress|bootstrap)         want "$tgt" || want npm || continue ;;
    *)                           want "$tgt" || continue ;;
  esac
  "build_$tgt"
done

if [[ " ${TARGETS[*]} " == *" clean "* ]]; then
  log "cleaning"; rm -rf "$BUILD_DIR" "$DIST_DIR"
fi

log "done: ${TARGETS[*]}"

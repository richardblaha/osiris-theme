#!/usr/bin/env bash
# Install built OSIRIS themes into the current user's home (no root, no package).
#
#   scripts/install-local.sh <what> [--dark|--light]
#
#   what: vscode | gtk | gnome | plasma | icons | terminal | wallpapers | grub | all
#
# Run scripts/build.sh first. GRUB still needs root (delegates to sudo).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/lib/common.sh

WHAT="${1:-all}"; shift || true
MODE="dark"
for a in "$@"; do case "$a" in --dark) MODE=dark;; --light) MODE=light;; esac; done

DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
theme_name() { [ "$MODE" = light ] && echo "Osiris-Light" || echo "Osiris"; }

do_gtk() {
  local n; n="$(theme_name)"
  mkdir -p "$DATA/themes" "$HOME/.themes"
  cp -rT "$BUILD_DIR/themes/$n" "$DATA/themes/$n"
  cp -rT "$BUILD_DIR/themes/$n" "$HOME/.themes/$n"
  # GtkSourceView schemes (GNOME Text Editor / gedit / Builder / meld)
  if [ -d "$BUILD_DIR/sourceview" ]; then
    for v in 5 4 3.0; do
      mkdir -p "$DATA/gtksourceview-$v/styles"
      cp "$BUILD_DIR/sourceview/Osiris.xml"       "$DATA/gtksourceview-$v/styles/osiris.xml"
      cp "$BUILD_DIR/sourceview/Osiris-Light.xml" "$DATA/gtksourceview-$v/styles/osiris-light.xml"
    done
    have gsettings && gsettings set org.gnome.TextEditor style-scheme \
      "$([ "$MODE" = light ] && echo osiris-light || echo osiris)" 2>/dev/null || true
  fi
  # libadwaita opt-in
  mkdir -p "$CONFIG/gtk-4.0" "$CONFIG/gtk-3.0"
  cp "$BUILD_DIR/themes/$n/gtk-4.0/gtk.css"    "$CONFIG/gtk-4.0/gtk.css"
  cp "$BUILD_DIR/themes/$n/gtk-4.0/colors.css" "$CONFIG/gtk-4.0/colors.css" 2>/dev/null || true
  cp "$BUILD_DIR/themes/$n/gtk-3.0/gtk.css"    "$CONFIG/gtk-3.0/gtk.css"
  if have gsettings; then
    gsettings set org.gnome.desktop.interface gtk-theme "$n" || true
    gsettings set org.gnome.desktop.interface color-scheme \
      "$([ "$MODE" = light ] && echo prefer-light || echo prefer-dark)" || true
  fi
  log "GTK theme '$n' installed + selected"
}

do_gnome() {
  local n; n="$(theme_name)"
  cp -rT "$BUILD_DIR/themes/$n" "$DATA/themes/$n"
  if have gsettings; then
    if gsettings writable org.gnome.shell.extensions.user-theme name >/dev/null 2>&1; then
      gsettings set org.gnome.shell.extensions.user-theme name "$n"
      log "GNOME Shell theme set to '$n' (User Themes extension)"
    else
      warn "install/enable the 'User Themes' GNOME extension to use the shell theme"
    fi
  fi
}

do_plasma() {
  mkdir -p "$DATA/color-schemes" "$DATA/aurorae/themes" \
           "$DATA/plasma/desktoptheme" "$DATA/Kvantum"
  cp "$BUILD_DIR/plasma/color-schemes/"*.colors "$DATA/color-schemes/"
  cp -rT "$BUILD_DIR/plasma/aurorae/OsirisDark"     "$DATA/aurorae/themes/OsirisDark"
  cp -rT "$BUILD_DIR/plasma/desktoptheme/Osiris"    "$DATA/plasma/desktoptheme/Osiris"
  cp -rT "$BUILD_DIR/plasma/Kvantum/OsirisDark"     "$DATA/Kvantum/OsirisDark"
  cp -rT "$BUILD_DIR/plasma/Kvantum/OsirisLight"    "$DATA/Kvantum/OsirisLight"
  if have plasma-apply-colorscheme; then
    plasma-apply-colorscheme "$([ "$MODE" = light ] && echo OsirisLight || echo Osiris)" || true
  fi
  if have plasma-apply-desktoptheme; then plasma-apply-desktoptheme Osiris || true; fi
  if have kwriteconfig6; then
    kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme "__aurorae__svg__OsirisDark"
    kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library "org.kde.kwin.aurorae"
    have qdbus && qdbus org.kde.KWin /KWin reconfigure || true
  fi
  if have kvantummanager; then kvantummanager --set "$([ "$MODE" = light ] && echo OsirisLight || echo OsirisDark)" || true; fi
  log "Plasma / Qt themes installed (Kvantum: set Qt style to 'kvantum' in systemsettings)"
}

do_wallpapers() {
  mkdir -p "$DATA/backgrounds/osiris" "$DATA/gnome-background-properties"
  cp -rT "$BUILD_DIR/wallpapers/backgrounds/osiris" "$DATA/backgrounds/osiris"
  # rewrite packaged /usr/share paths to this user's dir
  find "$DATA/backgrounds/osiris" -name '*.xml' -exec \
    sed -i "s#/usr/share/backgrounds/osiris#$DATA/backgrounds/osiris#g" {} +
  sed "s#/usr/share/backgrounds/osiris#$DATA/backgrounds/osiris#g" \
    "$BUILD_DIR/wallpapers/gnome-background-properties/osiris.xml" \
    > "$DATA/gnome-background-properties/osiris.xml"
  for pkg in "$BUILD_DIR"/wallpapers/kde/Osiris-*; do
    [ -d "$pkg" ] && cp -rT "$pkg" "$DATA/wallpapers/$(basename "$pkg")"
  done
  log "wallpapers installed to $DATA/backgrounds/osiris (pick them in Settings ▸ Background)"
}

do_vscode() {
  local vsix; vsix="$(ls -1 "$BUILD_DIR"/vscode/*.vsix 2>/dev/null | head -1 || true)"
  [ -n "$vsix" ] || die "no .vsix in $BUILD_DIR/vscode — run: scripts/build.sh vscode"
  for c in code codium code-oss osiris; do
    have "$c" && { "$c" --install-extension "$vsix"; log "installed $vsix into $c"; return; }
  done
  warn "no VS Code CLI found; install manually: <editor> --install-extension $vsix"
}

do_grub() { sudo boot/grub/install.sh; }

do_icons() {
  [ -d "$BUILD_DIR/icons/Osiris" ] || die "no icon theme in $BUILD_DIR/icons — run: scripts/build.sh icons"
  mkdir -p "$DATA/icons"
  cp -rT "$BUILD_DIR/icons/Osiris" "$DATA/icons/Osiris"
  have gtk-update-icon-cache && gtk-update-icon-cache -f -t "$DATA/icons/Osiris" 2>/dev/null || true
  if have gsettings; then
    gsettings set org.gnome.desktop.interface icon-theme "Osiris" || true
  fi
  if have kwriteconfig6; then
    kwriteconfig6 --file kdeglobals --group Icons --key Theme "Osiris" || true
  fi
  log "icon theme 'Osiris' installed to $DATA/icons/Osiris + selected"
}

do_terminal() {
  [ -d "$BUILD_DIR/terminal" ] || die "no terminal schemes in $BUILD_DIR/terminal — run: scripts/build.sh terminal"
  # Ptyxis (current GNOME default terminal)
  mkdir -p "$DATA/org.gnome.Ptyxis/palettes"
  cp "$BUILD_DIR/terminal/ptyxis/osiris.palette" "$DATA/org.gnome.Ptyxis/palettes/"
  # Konsole
  mkdir -p "$DATA/konsole"
  cp "$BUILD_DIR"/terminal/konsole/*.colorscheme "$DATA/konsole/"
  # GNOME Terminal — merge the two profiles
  if have dconf; then
    bash "$BUILD_DIR/terminal/gnome-terminal/install.sh" "$([ "$MODE" = dark ] && echo --default || echo)" || \
      warn "GNOME Terminal profile install failed"
  fi
  log "terminal schemes installed (Ptyxis palette 'Osiris', Konsole 'Osiris Dark/Light', GNOME Terminal profiles)"
}

case "$WHAT" in
  vscode) do_vscode ;;
  gtk) do_gtk ;;
  gnome) do_gtk; do_gnome ;;
  plasma) do_plasma ;;
  icons) do_icons ;;
  terminal) do_terminal ;;
  wallpapers) do_wallpapers ;;
  grub) do_grub ;;
  desktop) do_gtk; do_gnome; do_plasma; do_icons; do_terminal; do_wallpapers ;;
  all) do_vscode || true; do_gtk; do_gnome; do_plasma; do_icons; do_terminal; do_wallpapers ;;
  *) die "unknown target: $WHAT" ;;
esac

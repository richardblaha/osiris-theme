#!/usr/bin/env bash
# Install the OSIRIS GRUB2 theme system-wide. Run as root.
#   sudo boot/grub/install.sh [--theme-dir DIR] [--uninstall]
#
# Packaged form: osiris-theme-grub.deb / .rpm run the equivalent from their
# post-install scriptlets. This script is for manual / from-source installs.
set -euo pipefail

THEME_NAME="osiris"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_ROOT="/boot/grub"
[[ -d /boot/grub2 ]] && DEST_ROOT="/boot/grub2"          # Fedora/openSUSE
GRUB_DEFAULT="/etc/default/grub"
UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --theme-dir) DEST_ROOT="$2"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ $EUID -eq 0 ]] || { echo "must run as root" >&2; exit 1; }

DEST="$DEST_ROOT/themes/$THEME_NAME"

regen() {
  if command -v update-grub >/dev/null 2>&1; then
    update-grub
  elif command -v grub2-mkconfig >/dev/null 2>&1; then
    grub2-mkconfig -o "$DEST_ROOT/grub.cfg"
  elif command -v grub-mkconfig >/dev/null 2>&1; then
    grub-mkconfig -o "$DEST_ROOT/grub.cfg"
  else
    echo "!! could not find update-grub / grub2-mkconfig — regenerate grub.cfg manually" >&2
  fi
}

if [[ $UNINSTALL -eq 1 ]]; then
  rm -rf "$DEST"
  sed -i '/^GRUB_THEME=.*osiris/d' "$GRUB_DEFAULT" || true
  echo "removed $DEST and GRUB_THEME entry"
  regen
  exit 0
fi

# Expect a built theme tree (theme.txt + pixmaps). If only sources are present,
# tell the user to run the build first.
if [[ ! -f "$SRC_DIR/build/theme.txt" && ! -f "$SRC_DIR/item_c.png" ]]; then
  BUILT="$(cd "$SRC_DIR/../.." && pwd)/build/grub/osiris"
  if [[ -f "$BUILT/theme.txt" ]]; then
    SRC_DIR="$BUILT"
  else
    echo "No built theme found. Run:  scripts/build.sh grub" >&2
    exit 1
  fi
fi

install -d "$DEST"
cp -rT "$SRC_DIR" "$DEST"
rm -f "$DEST/install.sh" "$DEST/background.svg"

# Point GRUB at the theme + ensure a graphical console.
if grep -q '^GRUB_THEME=' "$GRUB_DEFAULT"; then
  sed -i "s#^GRUB_THEME=.*#GRUB_THEME=\"$DEST/theme.txt\"#" "$GRUB_DEFAULT"
else
  echo "GRUB_THEME=\"$DEST/theme.txt\"" >> "$GRUB_DEFAULT"
fi
grep -q '^GRUB_GFXMODE=' "$GRUB_DEFAULT" || echo 'GRUB_GFXMODE=1920x1080,auto' >> "$GRUB_DEFAULT"
sed -i 's/^#\?GRUB_TERMINAL=.*/#GRUB_TERMINAL=console/' "$GRUB_DEFAULT" || true

echo "installed OSIRIS GRUB theme -> $DEST"
regen

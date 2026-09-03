#!/usr/bin/env bash
# Build every OSIRIS .deb into dist/. Wraps dpkg-buildpackage with the debian/
# tree kept under packaging/debian/ (not at repo root).
#
# Deps: dpkg-dev debhelper + the Build-Depends listed in debian/control.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
REPO="$PWD"
DIST="$REPO/dist"
VERSION="$(cat VERSION 2>/dev/null || echo 0.1.0)"

command -v dpkg-buildpackage >/dev/null || { echo "install dpkg-dev + debhelper" >&2; exit 1; }

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
SRC="$STAGE/osiris-desktop-theme-$VERSION"
mkdir -p "$SRC"

# copy the working tree (sans VCS / build cruft) into the build stage
tar -c --exclude='./.git' --exclude='./build' --exclude='./dist' \
      --exclude='node_modules' --exclude='*.tgz' --exclude='./bootstrap/dist' \
      -C "$REPO" . \
  | tar -x -C "$SRC"

cp -rT "$REPO/packaging/debian/debian" "$SRC/debian"
chmod +x "$SRC/debian/rules"

( cd "$SRC" && dpkg-buildpackage -us -uc -b --no-sign )

mkdir -p "$DIST"
mv "$STAGE"/osiris-*_*.deb "$DIST"/ 2>/dev/null || mv "$STAGE"/*.deb "$DIST"/
echo "---- debs ----"
ls -la "$DIST"/*.deb

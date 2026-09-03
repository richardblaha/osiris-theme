#!/usr/bin/env bash
# Build every OSIRIS .rpm into dist/. Sets up a throwaway rpmbuild tree.
# Deps: rpm-build + the BuildRequires in the .spec.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
REPO="$PWD"
DIST="$REPO/dist"
VERSION="$(cat VERSION 2>/dev/null || echo 0.1.0)"
NAME="osiris-desktop-theme"

command -v rpmbuild >/dev/null || { echo "install rpm-build" >&2; exit 1; }

TOP="$(mktemp -d)"
trap 'rm -rf "$TOP"' EXIT
mkdir -p "$TOP"/{SOURCES,SPECS,BUILD,RPMS,SRPMS}

# tarball named <name>-<version>/ at the root (matches %autosetup)
PREFIX="$NAME-$VERSION"
tar -c --exclude='./.git' --exclude='./build' --exclude='./dist' \
      --exclude='./node_modules' --exclude='./vscode/node_modules' \
      --transform "s,^\.,$PREFIX," -C "$REPO" . \
  | gzip > "$TOP/SOURCES/$PREFIX.tar.gz"

cp "$REPO/packaging/rpm/$NAME.spec" "$TOP/SPECS/"

rpmbuild --define "_topdir $TOP" \
         --define "version $VERSION" \
         -bb "$TOP/SPECS/$NAME.spec"

mkdir -p "$DIST"
find "$TOP/RPMS" -name '*.rpm' -exec cp -v {} "$DIST/" \;
echo "---- rpms ----"
ls -la "$DIST"/*.rpm

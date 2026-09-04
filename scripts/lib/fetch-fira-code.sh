#!/usr/bin/env bash
# ============================================================================
# Re-download the pinned Fira Code release into assets/fonts/fira-code/.
# Run this to bump the bundled font; the woff2 files are committed so a normal
# build never needs the network.
#
#   scripts/lib/fetch-fira-code.sh [version]      (default: 6.2)
# ============================================================================
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

VER="${1:-6.2}"
DEST="assets/fonts/fira-code"
URL="https://github.com/tonsky/FiraCode/releases/download/${VER}/Fira_Code_v${VER}.zip"

command -v curl >/dev/null || { echo "curl required" >&2; exit 1; }
command -v unzip >/dev/null || { echo "unzip required" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "downloading Fira Code $VER"
curl -fsSL -o "$tmp/fira.zip" "$URL"
unzip -q -o "$tmp/fira.zip" -d "$tmp"

mkdir -p "$DEST"
cp "$tmp"/woff2/FiraCode-Light.woff2 \
   "$tmp"/woff2/FiraCode-Regular.woff2 \
   "$tmp"/woff2/FiraCode-Medium.woff2 \
   "$tmp"/woff2/FiraCode-SemiBold.woff2 \
   "$tmp"/woff2/FiraCode-Bold.woff2 \
   "$tmp"/woff2/FiraCode-VF.woff2 \
   "$DEST/"
curl -fsSL -o "$DEST/LICENSE" \
  "https://raw.githubusercontent.com/tonsky/FiraCode/${VER}/LICENSE"

echo "updated $DEST (v$VER):"
ls -1 "$DEST"

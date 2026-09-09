#!/usr/bin/env bash
# Build a signed APT repository from the OSIRIS .deb packages, laid out for
# static hosting on GitHub Pages:
#   https://richardblaha.github.io/osiris-theme/apt/
#
# The packages are all `Architecture: all` (pure data — themes, icons, GRUB,
# wallpapers), so a single suite serves every apt-based distro.
#
# Usage:  packaging/apt/build-apt-repo.sh <out-dir> [deb-dir]
#   <out-dir>   the repository tree is (re)created here
#   [deb-dir]   directory of *.deb files. If omitted, the *.deb assets of the
#               latest GitHub release are downloaded with `gh`
#               (needs GH_TOKEN / `gh auth`).
#
# Env:
#   APT_GPG_KEY   key id / fingerprint of an already-imported secret key used to
#                 sign Release. Unset => the repo is built UNSIGNED (fine for a
#                 local `make pages` preview; apt itself needs the signature).
#   APT_SUITE     suite name                       (default: stable)
#   APT_ARCHES    dpkg arches to advertise         (default: "amd64 arm64")
#   APT_REPO      owner/name for `gh release`      (default: richardblaha/osiris-theme)
#   APT_ORIGIN / APT_LABEL                         (default: OSIRIS / OSIRIS Theme)
#
# Deps: dpkg-dev (dpkg-scanpackages), gzip; gnupg when APT_GPG_KEY is set;
#       gh when [deb-dir] is omitted.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
VERSION="$(cat VERSION 2>/dev/null || echo 0.0.0)"

OUT="${1:?usage: build-apt-repo.sh <out-dir> [deb-dir]}"
DEB_DIR="${2:-}"
SUITE="${APT_SUITE:-stable}"
ARCHES="${APT_ARCHES:-amd64 arm64}"
COMPONENT=main
ORIGIN="${APT_ORIGIN:-OSIRIS}"
LABEL="${APT_LABEL:-OSIRIS Theme}"
GH_REPO="${APT_REPO:-richardblaha/osiris-theme}"
BASE_URL="https://richardblaha.github.io/osiris-theme/apt"
KEYRING="/usr/share/keyrings/osiris-archive-keyring.gpg"

command -v dpkg-scanpackages >/dev/null || { echo "need dpkg-dev (dpkg-scanpackages)" >&2; exit 1; }

work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT

if [ -z "$DEB_DIR" ]; then
  command -v gh >/dev/null || { echo "need gh to fetch release .deb assets (or pass a deb-dir)" >&2; exit 1; }
  echo "fetching latest $GH_REPO release .deb assets"
  mkdir -p "$work/debs"
  gh release download --repo "$GH_REPO" --pattern '*.deb' --dir "$work/debs"
  DEB_DIR="$work/debs"
fi

shopt -s nullglob
debs=("$DEB_DIR"/*.deb)
[ ${#debs[@]} -gt 0 ] || { echo "no .deb files in $DEB_DIR" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT/pool/$COMPONENT"

# ---- pool ----------------------------------------------------------------
echo "pool/$COMPONENT:"
for deb in "${debs[@]}"; do
  src="$(dpkg-deb -f "$deb" Source 2>/dev/null || true)"
  src="${src%% *}"                              # strip "(version)" if present
  src="${src:-$(dpkg-deb -f "$deb" Package)}"
  case "$src" in lib?*) prefix="${src:0:4}" ;; *) prefix="${src:0:1}" ;; esac
  dst="$OUT/pool/$COMPONENT/$prefix/$src"
  mkdir -p "$dst"
  cp "$deb" "$dst/"
  echo "  $prefix/$src/$(basename "$deb")"
done

# ---- per-arch Packages indices -----------------------------------------
gen_arch() {
  local arch="$1"
  local dir="$OUT/dists/$SUITE/$COMPONENT/binary-$arch"
  mkdir -p "$dir"
  ( cd "$OUT" && dpkg-scanpackages --arch "$arch" "pool/$COMPONENT" /dev/null ) > "$dir/Packages"
  gzip -9nkf "$dir/Packages"
  cat > "$dir/Release" <<EOF
Archive: $SUITE
Suite: $SUITE
Component: $COMPONENT
Origin: $ORIGIN
Label: $LABEL
Architecture: $arch
EOF
}
for a in $ARCHES all; do gen_arch "$a"; done

# ---- top-level Release (+ checksums) ----------------------------------
distdir="$OUT/dists/$SUITE"
cat > "$distdir/Release" <<EOF
Origin: $ORIGIN
Label: $LABEL
Suite: $SUITE
Codename: $SUITE
Version: $VERSION
Date: $(date -Ru)
Architectures: $ARCHES all
Components: $COMPONENT
Description: OSIRIS desktop theme — GTK/GNOME, KDE Plasma, icons, GRUB, wallpapers
EOF

hashes() {  # $1 = label, $2 = *sum command
  echo "$1"
  ( cd "$distdir" && find . -type f -path './main/*' \
       \( -name 'Packages' -o -name 'Packages.gz' -o -name 'Release' \) -printf '%P\n' \
     | LC_ALL=C sort | while read -r f; do
         printf ' %s %16d %s\n' "$($2 "$f" | cut -d' ' -f1)" "$(stat -c%s "$f")" "$f"
       done )
}
{
  hashes "MD5Sum:" md5sum
  hashes "SHA1:"   sha1sum
  hashes "SHA256:" sha256sum
} >> "$distdir/Release"

# ---- sign + publish the public key -----------------------------------
if [ -n "${APT_GPG_KEY:-}" ]; then
  echo "signing Release with $APT_GPG_KEY"
  gpg --batch --yes --local-user "$APT_GPG_KEY" --armor --detach-sign \
      --output "$distdir/Release.gpg" "$distdir/Release"
  gpg --batch --yes --local-user "$APT_GPG_KEY" --clearsign \
      --output "$distdir/InRelease" "$distdir/Release"
  gpg --batch --yes --export "$APT_GPG_KEY"          > "$OUT/osiris-archive-keyring.gpg"
  gpg --batch --yes --armor --export "$APT_GPG_KEY"  > "$OUT/osiris-archive-keyring.asc"
else
  echo "::warning::APT_GPG_KEY unset — repository Release is NOT signed" >&2
fi

# ---- consumer helpers ------------------------------------------------
cat > "$OUT/osiris.sources" <<EOF
Types: deb
URIs: $BASE_URL
Suites: $SUITE
Components: $COMPONENT
Architectures: $ARCHES
Signed-By: $KEYRING
EOF

cat > "$OUT/osiris.list" <<EOF
deb [signed-by=$KEYRING] $BASE_URL $SUITE $COMPONENT
EOF

cat > "$OUT/setup.sh" <<EOF
#!/bin/sh
# Add the OSIRIS APT repository. Usage:  curl -fsSL $BASE_URL/setup.sh | sudo sh
set -e
[ "\$(id -u)" = 0 ] || { echo "run as root (sudo)" >&2; exit 1; }
command -v curl >/dev/null || { echo "install curl first" >&2; exit 1; }
install -d -m 0755 /usr/share/keyrings /etc/apt/sources.list.d
curl -fsSL $BASE_URL/osiris-archive-keyring.gpg -o $KEYRING
curl -fsSL $BASE_URL/osiris.sources -o /etc/apt/sources.list.d/osiris.sources
apt-get update
echo "OSIRIS repo added — now: apt install osiris-desktop-theme"
EOF
chmod +x "$OUT/setup.sh"

cat > "$OUT/index.html" <<EOF
<!doctype html><meta charset=utf-8><title>OSIRIS APT repository</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>
 :root{color-scheme:light dark}
 body{font:15px/1.6 system-ui,sans-serif;max-width:44rem;margin:3rem auto;padding:0 1.2rem}
 h1{font-size:1.4rem} code,pre{font-family:ui-monospace,monospace}
 pre{background:#8881;padding:1rem;border-radius:4px;overflow-x:auto}
 a{color:#0aa}
</style>
<h1>OSIRIS APT repository</h1>
<p>Debian/Ubuntu packages for the <a href="../">OSIRIS desktop theme</a> —
GTK/GNOME, KDE Plasma, the Papirus-style icon theme, the GRUB theme and the
wallpapers. Packages are architecture-independent, so this works on any
apt-based distribution.</p>
<h2>Quick add</h2>
<pre>curl -fsSL $BASE_URL/setup.sh | sudo sh</pre>
<h2>Manual</h2>
<pre>curl -fsSL $BASE_URL/osiris-archive-keyring.gpg \\
  | sudo tee $KEYRING &gt; /dev/null
curl -fsSL $BASE_URL/osiris.sources \\
  | sudo tee /etc/apt/sources.list.d/osiris.sources &gt; /dev/null
sudo apt update
sudo apt install osiris-desktop-theme</pre>
<p>Suite <code>$SUITE</code>, component <code>$COMPONENT</code>. Key fingerprint
is shown in <code>osiris-archive-keyring.asc</code>. Built from OSIRIS
<code>$VERSION</code>.</p>
EOF

echo "---- apt repository ----"
find "$OUT" -maxdepth 4 -type f | LC_ALL=C sort | sed "s|^$OUT/|  |"

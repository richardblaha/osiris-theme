# APT repository — `richardblaha.github.io/osiris-theme/apt`

A self-hosted, GPG-signed APT repository served as static files from GitHub Pages.
It carries the six Debian packages
(`osiris-theme-gtk`, `osiris-theme-plasma`, `osiris-icon-theme`, `osiris-theme-grub`,
`osiris-wallpapers`, `osiris-desktop-theme`). They are all `Architecture: all` — pure
data, no compiled code — so one suite works on **any** apt-based distribution
(Debian, Ubuntu, Mint, Pop!_OS, …).

- **Suite:** `stable` · **Component:** `main` · **Base URL:**
  `https://richardblaha.github.io/osiris-theme/apt`
- Layout: `pool/main/o/osiris-desktop-theme/*.deb`,
  `dists/stable/{Release,InRelease,Release.gpg}`,
  `dists/stable/main/binary-{amd64,arm64,all}/Packages{,.gz}`

## Install (end users)

```sh
curl -fsSL https://richardblaha.github.io/osiris-theme/apt/setup.sh | sudo sh
sudo apt install osiris-desktop-theme
```

`setup.sh` drops the keyring at `/usr/share/keyrings/osiris-archive-keyring.gpg` and
a deb822 source at `/etc/apt/sources.list.d/osiris.sources`. Manual equivalent:

```sh
curl -fsSL https://richardblaha.github.io/osiris-theme/apt/osiris-archive-keyring.gpg \
  | sudo tee /usr/share/keyrings/osiris-archive-keyring.gpg > /dev/null
curl -fsSL https://richardblaha.github.io/osiris-theme/apt/osiris.sources \
  | sudo tee /etc/apt/sources.list.d/osiris.sources > /dev/null
sudo apt update
```

## How it is built and published

| Where | What |
|---|---|
| `packaging/apt/build-apt-repo.sh <out> [deb-dir]` | builds the `pool/` + `dists/` tree, signs `Release` (→ `InRelease` + `Release.gpg`) with `APT_GPG_KEY`, writes `setup.sh` / `osiris.sources` / `osiris.list` / the public key / `index.html`. With no `deb-dir` it pulls the latest GitHub release's `.deb` assets via `gh`. |
| `scripts/build.sh pages` | when `OSIRIS_APT_REPO=1`, stages the repo into `build/pages/apt/` (`OSIRIS_APT_DEB_DIR` picks the `.deb` source). |
| `.github/workflows/release.yml` → `publish-pages` | on every tag: builds the repo from that release's fresh `.deb` artifact and deploys it with the preview site. |
| `.github/workflows/build.yml` → `pages-build` | on every `main` push: rebuilds the repo from the **latest release** so a docs-only deploy never drops `/apt/`. |
| `make apt` | local: `make deb` then build the repo into `build/apt/` from `dist/*.deb`. |

Environment knobs: `APT_SUITE` (default `stable`), `APT_ARCHES` (default `amd64 arm64`),
`APT_REPO` (default `richardblaha/osiris-theme`), `APT_ORIGIN` / `APT_LABEL`.

## One-time setup — the signing key

Until the **`APT_GPG_PRIVATE_KEY`** repo secret exists, the workflows still publish the
repo but leave `Release` unsigned; users would then need `[trusted=yes]` in their
sources line. To sign it:

### 1. Create a dedicated, passphraseless repo-signing key

```sh
gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key \
    'OSIRIS Theme (APT repo signing) <richardblaha@gmail.com>' ed25519 sign 5y
KEYID=$(gpg --list-keys --with-colons richardblaha@gmail.com | awk -F: '/^fpr:/{print $10; exit}')
```

Keep this separate from any personal key — it lives in a GitHub secret.

### 2. Add it as a repo secret

```sh
gpg --armor --export-secret-keys "$KEYID" | gh secret set APT_GPG_PRIVATE_KEY
```

(or *Settings → Secrets and variables → Actions → New repository secret*,
name `APT_GPG_PRIVATE_KEY`, value = the armored block).

That is all. The workflow imports the key, derives its fingerprint, signs `Release`,
and publishes the matching public key to
`…/apt/osiris-archive-keyring.gpg` (binary, for `Signed-By:`) and `.asc` (armored).

### 3. Enable GitHub Pages (if not already)

*Settings → Pages → Source: GitHub Actions.* Until then `deploy-pages` 404s and the
`publish-pages` job is allowed to fail without failing the release.

## Rotating the key

Generate a new key, update the `APT_GPG_PRIVATE_KEY` secret, and cut a release (or
push to `main`). The new public key ships automatically; users re-run `setup.sh` to
pick it up. Announce it in `CHANGELOG.md` — an unexpected key change looks like an
attack.

## Notes

- The repo keeps only the **latest** version of each package (it is rebuilt from the
  newest release each time). Old `.deb` files stay on their GitHub Release.
- No `Valid-Until` is set, so the indices never expire between releases.
- `dpkg-scanpackages` prints "missing from override file" warnings — harmless, there
  is deliberately no override file.

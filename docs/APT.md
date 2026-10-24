# APT repository — `richardblaha.github.io/osiris-deb-repo`

A GPG-signed APT repository served as static files by GitHub Pages from the separate
[`richardblaha/osiris-deb-repo`](https://github.com/richardblaha/osiris-deb-repo) repo.
It carries every Debian package this repo builds (`osiris-theme-gtk`,
`osiris-theme-plasma`, `osiris-icon-theme`, `osiris-theme-grub`, `osiris-wallpapers`,
`osiris-desktop-theme`, `osiris-archive-keyring`). They are all `Architecture: all`,
so one suite works on any apt-based distribution.

- **Suite:** `stable` · **Component:** `main` · **Base URL:**
  `https://richardblaha.github.io/osiris-deb-repo`
- Layout: `pool/main/o/osiris-desktop-theme/*.deb`,
  `dists/stable/{Release,InRelease,Release.gpg}`,
  `dists/stable/main/binary-{amd64,arm64,all}/Packages{,.gz}`
- Every released version stays in the pool (indexed with `--multiversion`).

## Install (end users)

Either install the `osiris-archive-keyring_*.deb` from a GitHub Release:

```sh
sudo apt install ./osiris-archive-keyring_*_all.deb
sudo apt update && sudo apt install osiris-desktop-theme
```

or run the setup script, which does the same:

```sh
curl -fsSL https://richardblaha.github.io/osiris-deb-repo/setup.sh | sudo sh
sudo apt install osiris-desktop-theme
```

Both put the key at `/usr/share/keyrings/osiris-archive-keyring.gpg` and a deb822
source at `/etc/apt/sources.list.d/osiris.sources`. The keyring package is itself in
the repo, so a future key rotation reaches users through `apt upgrade`.

## How it is built and published

| Where | What |
|---|---|
| `packaging/apt/osiris-archive-keyring.gpg`, `packaging/apt/osiris.sources` | the public key and the source file; shipped by the `osiris-archive-keyring` package and copied into the repo. |
| `packaging/apt/build-apt-repo.sh <out> [deb-dir]` | builds the `pool/` + `dists/` tree from every `.deb` in `deb-dir`, signs `Release` (→ `InRelease` + `Release.gpg`) with `APT_GPG_KEY`, writes `setup.sh` / `osiris.sources` / `osiris.list` / the public key / `index.html`. With no `deb-dir` it pulls the latest GitHub release's `.deb` assets via `gh`. |
| `.github/workflows/release.yml` → `apt` | on a **stable** tag (no `-`): checks out `osiris-deb-repo`, rebuilds the repo from its existing pool plus the release's `.deb` files, and pushes. Pages on that repo serves `main`. |
| `make apt` | local: `make deb` then build the repo into `build/apt/` from `dist/*.deb`. |

Environment knobs: `APT_SUITE` (default `stable`), `APT_ARCHES` (default `amd64 arm64`),
`APT_REPO` (default `richardblaha/osiris-theme`), `APT_BASE_URL`, `APT_ORIGIN` / `APT_LABEL`.

## One-time setup — secrets in `osiris-theme`

| Secret | Value |
|---|---|
| `APT_GPG_PRIVATE_KEY` | armored secret key of the dedicated, passphraseless repo-signing key `A26BFD08F6A2AD3AFACADC3D3ED714C4D0C6E6CE`. Must match `packaging/apt/osiris-archive-keyring.gpg`. |
| `DEB_REPO_DEPLOY_KEY` | private half of an SSH key whose public half is a **write** deploy key on `osiris-deb-repo`. |

```sh
gpg --armor --export-secret-keys A26BFD08F6A2AD3AFACADC3D3ED714C4D0C6E6CE \
  | gh secret set APT_GPG_PRIVATE_KEY -R richardblaha/osiris-theme

ssh-keygen -t ed25519 -N '' -C osiris-theme-release -f deploy_key
gh repo deploy-key add deploy_key.pub -R richardblaha/osiris-deb-repo --allow-write -t "osiris-theme release"
gh secret set DEB_REPO_DEPLOY_KEY -R richardblaha/osiris-theme < deploy_key
rm deploy_key deploy_key.pub
```

## Rotating the key

Generate a new key, replace `packaging/apt/osiris-archive-keyring.gpg` with its public
part (`gpg --export <fpr>`), update `APT_GPG_PRIVATE_KEY`, and release. For a smooth
rotation, ship a keyring with **both** keys in one release before switching the
signing key. Announce it in `CHANGELOG.md` — an unexpected key change looks like an
attack.

## Notes

- No `Valid-Until` is set, so the indices never expire between releases.
- Every release adds about 18 MB to the `osiris-deb-repo` git history; GitHub Pages
  allows a 1 GB site. Prune old `.deb` files from its `pool/` when that gets close.
- `dpkg-scanpackages` prints "missing from override file" warnings — harmless, there
  is deliberately no override file.

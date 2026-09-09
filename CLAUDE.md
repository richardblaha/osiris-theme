# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

One repository that generates the entire **OSIRIS** visual identity from a single set of
design tokens: a VS Code extension (colour + file + product icon themes), an XDG/Papirus
icon theme, GTK 3/4, GNOME Shell, Metacity, KDE Plasma/Qt/Kvantum, GtkSourceView, GNOME
Terminal/Ptyxis/Konsole palettes, GRUB2, a VitePress npm theme, a Bootstrap 5 npm theme,
Forgejo/Gitea CSS, Chromium/Firefox manifests, and wallpapers. Output ships as `.vsix`,
`.tgz`, `.zip`, `.deb`, `.rpm`, and a `.tar.gz` bundle.

## The one rule: single source of truth

- **Every colour** comes from [`assets/tokens.json`](assets/tokens.json) (`accent`, `state`,
  `terminal`, `themes.{dark,light}`, plus `font`, `radius`, `shadow`, `icon`, `wallpaper`).
- **Every icon** comes from [`iconography/glyphs.json`](iconography/glyphs.json) (~145 Papirus-style
  24×24 path primitives), wired to targets through [`iconography/map/`](iconography/map/)
  (`filetypes.json`, `xdg.json`, `producticons.json`).

Never hand-tune a hex in a theme file or add a glyph straight into a target. `make tokens`
(→ [`scripts/check-tokens.sh`](scripts/check-tokens.sh)) is the CI gate and fails on drift.

### Two kinds of downstream file

- **Fully generated from tokens** — do not hand-edit: GtkSourceView schemes, Metacity
  decoration, terminal ANSI palettes, the XDG icon theme, and the GNOME Shell CSS
  (`desktop/gnome-shell/gnome-shell.css.in` uses `@TOKEN@` placeholders expanded by
  `render_gnome_shell` in [`scripts/lib/common.sh`](scripts/lib/common.sh); the token guard
  verifies every `@TOKEN@` used is one the renderer knows). Regenerate with
  `make desktop icons terminal`.
- **Hand-derived and drift-checked** — edit these by hand when tokens change, then the guard
  confirms the values match: `vscode/themes/osiris-{dark,light}-color-theme.json`,
  `docs/DESIGN_SYSTEM.md`, `docs/preview/styles.css`, `vitepress/theme/osiris.css`,
  `bootstrap/scss/_variables.scss` (light) + `bootstrap/scss/_dark.scss` (dark),
  `forgejo/theme-osiris-{dark,light}.css`, `browsers/*/manifest.json`, `docs/ICONOGRAPHY.md`.
  The terminal `terminal.ansi*` block in the committed VS Code themes is also compared to
  `assets/tokens.json → terminal`.

### Workflow for a palette change

1. Edit `assets/tokens.json`.
2. Update `docs/preview/styles.css` (`:root` / `[data-theme]`) and `docs/DESIGN_SYSTEM.md`.
3. Re-derive downstream: hand-edit the drift-checked files listed above, or for the
   templated ones run `make desktop icons terminal browsers`.
4. `make tokens` — must pass.
5. Eyeball `docs/preview/index.html` (toggle dark/light) — this is the acceptance test;
   there is no unit-test suite.

For an icon change: add the glyph to `iconography/glyphs.json`, reference it from
`iconography/map/*.json`, `make tokens`, then `make icons vscode`. See
[`docs/ICONOGRAPHY.md`](docs/ICONOGRAPHY.md).

## Build

`make` is a thin wrapper over [`scripts/build.sh`](scripts/build.sh) (`make <target>` runs
`scripts/build.sh <target>`); `packaging/{debian,rpm}/build-*.sh` do the packages.

```sh
make help          # list every target with its dependency notes
make tokens        # palette + icon drift guard — the CI gate (needs: jq; python3 fallback)
make vscode        # -> dist/osiris-theme-<ver>.vsix   (needs: node, vsce/npx, fantasticon, rsvg-convert)
make npm           # -> dist/osiris-{vitepress,bootstrap}-theme-<ver>.tgz
make icons         # -> build/icons/Osiris/            (needs: python3)
make terminal browsers forgejo sourceview
make desktop       # gtk + gnome-shell + metacity + sourceview + plasma -> build/themes/, build/plasma/
make themes        # -> dist/osiris-gnome-theme-<ver>.tar.gz
make grub wallpapers
make deb           # -> dist/*.deb   (needs: dpkg-dev, debhelper)
make rpm           # -> dist/*.rpm   (needs: rpm-build)
make dist          # everything that ships in a GitHub Release
make install-local # build + install themes into ~/.local/share and switch (no root)
make clean | distclean
```

Missing optional tools degrade gracefully (build.sh warns and drops that piece), so a
partial local toolchain still produces most artifacts.

### Icon generator

`python3 scripts/lib/gen_icons.py <target> <out-dir>` with `target` ∈
`vscode-file` | `vscode-product` (needs fantasticon for the `.woff`) | `xdg` | `all`.
Other `scripts/lib/gen_*.py` (`gen_sourceview.py`, `gen_terminal.py`, `gen_kvantum_svg.py`,
`gen_grub_assets.py`, `gen_appicons.py`) are invoked by `build.sh`.

## Versioning & releases

[`VERSION`](VERSION) is the single version source. `package.json`, `manifest.json`, the RPM
`Version:` and the Debian `changelog` are all stamped from it **at build time** — never
hand-edit a version in those files.

To cut a release: bump `VERSION`, move `CHANGELOG.md` `[Unreleased]` items under a
`## [x.y.z] - <date>` heading, commit, then `git tag vX.Y.Z && git push --tags` (must match
`VERSION` or `release.yml` fails fast; `-` in the tag ⇒ pre-release). `.github/workflows/build.yml`
runs the token guard + a full build on every push to `main` and every PR.

`release.yml` also publishes a **self-hosted APT repository** on GitHub Pages at
`https://richardblaha.github.io/osiris-theme/apt/` (`packaging/apt/build-apt-repo.sh`,
staged into `build/pages/apt/` by `scripts/build.sh pages` when `OSIRIS_APT_REPO=1`;
`make apt` builds it locally from `dist/*.deb`). The `Release` file is GPG-signed with
the `APT_GPG_PRIVATE_KEY` repo secret — until that is set the repo is unsigned and needs
`[trusted=yes]`. `build.yml` rebuilds the same repo from the latest GitHub Release on every
`main` push so a docs-only deploy never drops `/apt/`. See [`docs/APT.md`](docs/APT.md).

## Conventions

- Conventional-ish commit subjects: `feat(gtk): …`, `fix(grub): …`, `docs: …`.
- `.editorconfig`: LF, 2-space indent (4 for `*.py`/`*.sh`, tab for `Makefile`).
- The project wiki under [`wiki/`](wiki/) is written in **Czech**; `make wiki-sync`
  (`scripts/sync-wiki.sh`) pushes it to the GitHub Wiki repo. `docs/` specs are English.

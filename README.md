<div align="center">

# OSIRIS Themes

**One repository for the entire OSIRIS visual identity** — VS Code, GTK, GNOME
Shell, KDE Plasma / Qt, GRUB2 and wallpapers — all generated from a single set of
design tokens and shipped as `.vsix`, `.deb` and `.rpm`.

[Live preview & design system →](https://richardblaha.github.io/osiris-themes/)

</div>

---

## The idea

A **dual-accent** system: cyan primary + magenta/rose secondary on a
GitHub-flavoured neutral ramp (`#0d1117` / `#161b22` dark, white / `#f6f8fa`
light). The signature move is a **solid accent status bar**. Everything —
editor, window chrome, panel, boot menu — is derived from
[`assets/tokens.json`](assets/tokens.json), which was extracted verbatim from the
interactive reference in [`docs/preview/`](docs/preview/).

```
tokens.json ──┬─→ vscode/themes/*.json            → osiris-theme.vsix
              ├─→ desktop/gtk-* + gtk-common/*     → /usr/share/themes/Osiris{,-Light}
              ├─→ desktop/gnome-shell/*.css.in     → …/Osiris{,-Light}/gnome-shell
              ├─→ desktop/plasma/*                 → color-schemes / Kvantum / aurorae / desktoptheme
              ├─→ boot/grub/*                      → /boot/grub/themes/osiris
              └─→ assets/wallpapers/*              → /usr/share/backgrounds/osiris
```

## Repository layout

```text
osiris-themes/
├── assets/
│   ├── tokens.json              # ← single source of truth
│   ├── icons/                   # master OSIRIS mark
│   └── wallpapers/
│       ├── abstract/            # Bloom / Fluid — day.svg, night.svg, *.xml, kde-metadata.json
│       └── egypt/               # Ancient Egypt Sci-Fi — same set
├── docs/
│   ├── preview/                 # interactive reference → GitHub Pages
│   │   ├── index.html  styles.css  app.js
│   └── DESIGN_SYSTEM.md         # written spec (ramp, syntax, states, components)
├── vscode/                      # VS Code extension (Osiris Dark / Osiris Light)
├── desktop/
│   ├── gtk-common/              # @define-color palettes + shared widget rules
│   ├── gtk-3.0/  gtk-4.0/       # toolkit-specific extras
│   ├── gnome-shell/             # gnome-shell.css.in (+ assets/)
│   └── plasma/                  # color-schemes, Kvantum, aurorae, desktoptheme
├── boot/grub/                   # theme.txt, background.svg, icons/, fonts/, install.sh
├── packaging/
│   ├── debian/                  # source package → 5 binary debs
│   ├── rpm/                     # one spec → matching subpackages
│   └── common/                  # osiris-gtk-theme helper
├── scripts/
│   ├── build.sh                 # orchestrator (all targets)
│   ├── generate-wallpapers.py   # raster + GNOME/KDE bundle assembly
│   ├── check-tokens.sh          # palette drift guard (CI gate)
│   ├── install-local.sh         # build → $HOME, no root
│   └── lib/                     # common.sh, gen_kvantum_svg.py, gen_grub_assets.py
├── .github/workflows/           # build.yml, release.yml
├── Makefile
└── VERSION
```

## Install

### VS Code

Download `osiris-theme-<ver>.vsix` from
[Releases](https://github.com/richardblaha/osiris-themes/releases):

```sh
code --install-extension osiris-theme-<ver>.vsix
```

Then **Preferences: Color Theme → Osiris Dark / Osiris Light**.

### Debian / Ubuntu

```sh
sudo apt install ./osiris-desktop-theme_<ver>_all.deb   # metapackage — pulls all four
# …or pick components:
sudo apt install ./osiris-theme-gtk_<ver>_all.deb ./osiris-wallpapers_<ver>_all.deb
```

- `osiris-theme-gtk` — GTK 3/4 + libadwaita + GNOME Shell. Apply with
  `osiris-gtk-theme --apply` (or GNOME Tweaks → Appearance).
- `osiris-theme-plasma` — set **System Settings → Colors → Osiris**, decoration
  **Osiris Dark**, and (for full Qt coverage) the Kvantum style.
- `osiris-theme-grub` — configures `/boot/grub` and runs `update-grub` on install.
- `osiris-wallpapers` — appears in **Settings → Background** (static + *Dynamic*).

### Fedora / RHEL

```sh
sudo dnf install ./osiris-desktop-theme-<ver>.noarch.rpm
```

### From source (no packages, no root)

```sh
make install-local        # builds + installs into ~/.local/share and switches
```

## Building

See [`CONTRIBUTING.md`](CONTRIBUTING.md). TL;DR: `make help`, then `make dist`
produces every `.vsix` / `.deb` / `.rpm` into `dist/`. CI does the same on every
push; tagging `vX.Y.Z` cuts a GitHub Release and redeploys the Pages preview.

## License

MIT (see [`LICENSE`](LICENSE)). Fira Code is OFL-1.1.

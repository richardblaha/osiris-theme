<div align="center">

# OSIRIS Themes

**One repository for the entire OSIRIS visual identity** — VS Code (color, file
and product icons), a Material-Symbols icon theme, GTK, GNOME Shell, KDE Plasma /
Qt, GRUB2, VitePress, Bootstrap 5, Chromium & Firefox, and wallpapers — all
generated from a single set of design tokens and shipped as `.vsix`, npm
packages, browser `.zip`s, `.deb` and `.rpm`.

[Live preview & design system →](https://richardblaha.github.io/osiris-theme/)

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
tokens.json ──┬─→ vscode/themes/*.json            → osiris-theme.vsix (colour theme)
              ├─→ iconography/glyphs.json  ┬─→ vscode/fileicons/*     → Osiris File Icons
              │   + iconography/map/*.json ├─→ vscode/producticons/*  → Osiris Product Icons
              │                            └─→ build/icons/Osiris/    → /usr/share/icons/Osiris
              ├─→ desktop/gtk-* + gtk-common/*     → /usr/share/themes/Osiris{,-Light}/gtk-{3.0,4.0}
              ├─→ desktop/gnome-shell/*.css.in     → …/Osiris{,-Light}/gnome-shell
              ├─→ desktop/metacity-1/*.xml.in      → …/Osiris{,-Light}/metacity-1  (Flashback/Marco)
              ├─→ tokens.json → GtkSourceView      → gtksourceview-5/4/3.0/styles/osiris{,-light}.xml
              ├─→ desktop/plasma/*                 → color-schemes / Kvantum / aurorae / desktoptheme
              ├─→ tokens.json → terminal           → GNOME Terminal · Ptyxis · Konsole schemes
              ├─→ boot/grub/*                      → /boot/grub/themes/osiris
              ├─→ vitepress/theme/osiris.css       → npm: osiris-vitepress-theme
              ├─→ bootstrap/scss/*                 → npm: osiris-bootstrap-theme
              ├─→ forgejo/theme-osiris-*.css       → Forgejo / Gitea (osiris-forgejo-<ver>.zip)
              ├─→ browsers/*/manifest.json         → Chromium / Chrome / Edge / Firefox
              └─→ assets/wallpapers/*              → /usr/share/backgrounds/osiris
```

## Repository layout

```text
osiris-theme/
├── assets/
│   ├── tokens.json              # ← single source of truth
│   ├── icons/                   # master OSIRIS mark + app/ (.ico/.icns/.png/hicolor)
│   ├── fonts/fira-code/         # bundled Fira Code webfont (SIL OFL-1.1)
│   ├── watermarks/              # letterpress marks — SVG + 1x/2x PNG
│   └── wallpapers/
│       ├── abstract/            # Bloom / Fluid — day.svg, night.svg, *.xml, kde-metadata.json
│       └── egypt/               # Ancient Egypt Sci-Fi — same set
├── docs/
│   ├── preview/                 # interactive reference → GitHub Pages
│   │   ├── index.html  styles.css  app.js
│   ├── DESIGN_SYSTEM.md         # written spec (ramp, syntax, states, components)
│   └── ICONOGRAPHY.md           # icon spec (Material Symbols grid, colour, XDG layout)
├── iconography/                 # icon single-source
│   ├── glyphs.json              # ~145 Material-Symbols path primitives
│   └── map/                     # filetypes.json · xdg.json · producticons.json
├── vscode/                      # VS Code extension — colour + file + product icon themes
├── vitepress/                   # npm: osiris-vitepress-theme (default-theme override)
├── bootstrap/                   # npm: osiris-bootstrap-theme (Bootstrap 5, Sass)
├── forgejo/                     # Forgejo / Gitea CSS themes — dark / light / auto
├── browsers/                    # chromium-{dark,light} + firefox-{dark,light} manifests
├── desktop/
│   ├── gtk-common/              # @define-color palettes + shared widget rules
│   ├── gtk-3.0/  gtk-4.0/       # toolkit-specific extras
│   ├── gnome-shell/             # gnome-shell.css.in (+ assets/)
│   ├── metacity-1/              # metacity-theme-3.xml.in (Flashback / Marco / Xorg)
│   ├── plasma/                  # color-schemes, Kvantum, aurorae, desktoptheme
│   └── terminal/               # VTE schemes: GNOME Terminal / Ptyxis / Konsole
├── boot/grub/                   # theme.txt, background.svg, icons/, fonts/, install.sh
├── packaging/
│   ├── debian/                  # source package → 6 binary debs
│   ├── rpm/                     # one spec → matching subpackages
│   └── common/                  # osiris-gtk-theme helper
├── scripts/
│   ├── build.sh                 # orchestrator (all targets)
│   ├── generate-wallpapers.py   # raster + GNOME/KDE bundle assembly
│   ├── check-tokens.sh          # palette drift guard (CI gate)
│   ├── install-local.sh         # build → $HOME, no root
│   └── lib/                     # common.sh, gen_icons.py, gen_terminal.py, gen_sourceview.py, …
├── .github/workflows/           # build.yml, release.yml
├── Makefile
└── VERSION
```

## Install

### VS Code

Download `osiris-theme-<ver>.vsix` from
[Releases](https://github.com/richardblaha/osiris-theme/releases):

```sh
code --install-extension osiris-theme-<ver>.vsix
```

Then:

- **Preferences: Color Theme → Osiris Dark / Osiris Light**
- **Preferences: File Icon Theme → Osiris File Icons**
- **Preferences: Product Icon Theme → Osiris Product Icons**

### Web — npm

```sh
npm i -D osiris-vitepress-theme   # VitePress default-theme skin
npm i    osiris-bootstrap-theme   # Bootstrap 5 build (dark + light color modes)
```

See [`vitepress/`](vitepress/) and [`bootstrap/`](bootstrap/) for wiring.

### Forgejo / Gitea

Grab `osiris-forgejo-<ver>.zip` from
[Releases](https://github.com/richardblaha/osiris-theme/releases) (or the files
in [`forgejo/`](forgejo/)) and drop them into your instance:

```sh
install -Dm644 theme-osiris-*.css "$FORGEJO_CUSTOM/public/assets/css/"
```

Then list them in `app.ini` and restart:

```ini
[ui]
THEMES = forgejo-auto,forgejo-light,forgejo-dark,osiris-auto,osiris-dark,osiris-light
DEFAULT_THEME = osiris-auto
```

Users switch under **Avatar → Settings → Appearance**. See
[`forgejo/README.md`](forgejo/README.md) for Docker and details.

### Browsers

Grab `osiris-<engine>-<variant>-<ver>.zip` from
[Releases](https://github.com/richardblaha/osiris-theme/releases), or load the
folder directly:

- **Chromium / Chrome / Edge** — `chrome://extensions` → Developer mode → **Load
  unpacked** → [`browsers/chromium-dark`](browsers/chromium-dark) (or `-light`).
- **Firefox** — `about:debugging` → **Load Temporary Add-on** →
  [`browsers/firefox-dark/manifest.json`](browsers/firefox-dark) (or `-light`).

### Terminal

`make terminal` renders one 16-colour ANSI palette (dark + light) into every
VTE format — see [`desktop/terminal/`](desktop/terminal/):

- **Ptyxis** (current GNOME default) — drop `osiris.palette` in
  `~/.local/share/org.gnome.Ptyxis/palettes/`, pick **Osiris** in Preferences.
- **GNOME Terminal** — run `build/terminal/gnome-terminal/install.sh` (`--default`
  to also set it) — merges *Osiris Dark* / *Osiris Light* profiles, keeps yours.
- **Konsole** — copy `Osiris{Dark,Light}.colorscheme` into `~/.local/share/konsole/`.
- **GNOME Console** (`kgx`) can't be themed — it follows the system light/dark
  palette only.

The `.deb` / `.rpm` packages install the Ptyxis palette, the Konsole schemes and
the GNOME Terminal installer under `/usr/share`.

### Debian / Ubuntu

```sh
sudo apt install ./osiris-desktop-theme_<ver>_all.deb   # metapackage — pulls all six
# …or pick components:
sudo apt install ./osiris-icon-theme_<ver>_all.deb ./osiris-theme-gtk_<ver>_all.deb
```

- `osiris-theme-gtk` — GTK 3/4 + libadwaita + GNOME Shell + Metacity (Flashback),
  the GtkSourceView syntax schemes (**osiris** / **osiris-light** — used by GNOME
  Text Editor, gedit, GNOME Builder, meld…), the **Ptyxis** terminal palette and
  a GNOME Terminal profile installer (`/usr/share/osiris/gnome-terminal/install.sh`).
  Apply the theme with `osiris-gtk-theme --apply` (or GNOME Tweaks → Appearance);
  pick the editor scheme in the app's preferences.
- `osiris-icon-theme` — Material-Symbols icon set. Select **Osiris** in GNOME
  Tweaks → Appearance → Icons, or System Settings → Icons on KDE.
- `osiris-theme-plasma` — set **System Settings → Colors → Osiris**, decoration
  **Osiris Dark**, the Kvantum style (full Qt coverage) and the **Osiris
  Dark/Light** Konsole colour schemes.
- `osiris-theme-grub` — configures `/boot/grub` and runs `update-grub` on install.
- `osiris-wallpapers` — appears in **Settings → Background** (static + *Dynamic*).

### Fedora / RHEL

```sh
sudo dnf install ./osiris-desktop-theme-<ver>.noarch.rpm
```

### Other distros (Arch, openSUSE, NixOS, …)

Download `osiris-gnome-theme-<ver>.tar.gz` from
[Releases](https://github.com/richardblaha/osiris-theme/releases) — it bundles
the GTK 3/4 + GNOME Shell + Metacity theme (`Osiris` + `Osiris-Light`) and the
GtkSourceView schemes with an install README:

```sh
tar xf osiris-gnome-theme-<ver>.tar.gz && cd osiris-gnome-theme-<ver>
cp -r Osiris Osiris-Light ~/.local/share/themes/
# then: GNOME Tweaks → Appearance, and the "User Themes" extension for the Shell
```

### From source (no packages, no root)

```sh
make install-local        # builds + installs into ~/.local/share and switches
```

## Building

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`docs/ICONOGRAPHY.md`](docs/ICONOGRAPHY.md). TL;DR: `make help`, then `make dist`
produces every `.vsix` / `.tgz` / `.zip` / `.deb` / `.rpm` into `dist/`. CI
(`build.yml`) does the same on every push and PR; pushing a tag `vX.Y.Z` that
matches `VERSION` runs `release.yml` — it builds everything, publishes a GitHub
Release with all artifacts attached, `npm publish`es the two npm packages
(needs the `NPM_TOKEN` secret) and redeploys the Pages preview.

## License

MIT (see [`LICENSE`](LICENSE)). The bundled **Fira Code** webfont
([`assets/fonts/fira-code/`](assets/fonts/fira-code/)) is **SIL OFL-1.1** — its
`LICENSE` sits next to the font files and in
[`packaging/debian/debian/copyright`](packaging/debian/debian/copyright).

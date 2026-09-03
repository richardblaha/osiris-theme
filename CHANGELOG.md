# Changelog

All notable changes to `osiris-themes` are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/); versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **Design system**
  - `assets/tokens.json` — machine-readable single source of truth for the whole
    OSIRIS visual language (dark + light).
  - `docs/DESIGN_SYSTEM.md` — human spec (ramp, text, syntax, states, shape,
    component contract, typography).
  - `docs/preview/` — the interactive VS Code-window reference, split into
    `index.html` / `styles.css` / `app.js`; published to GitHub Pages.
- **VS Code** — `Osiris Dark` + `Osiris Light` color themes (`vscode/`), packaged
  as `osiris-theme-<ver>.vsix`.
- **GTK** — GTK 3, GTK 4 / libadwaita named-colour + widget stylesheets
  (`desktop/gtk-*`, `desktop/gtk-common/`), assembled into `Osiris` /
  `Osiris-Light` themes; `osiris-gtk-theme` helper for the libadwaita opt-in.
- **GNOME Shell** — templated theme (`desktop/gnome-shell/gnome-shell.css.in`)
  covering panel, quick settings, calendar/notifications, OSD, overview
  search/dash, app grid, switchers, modal dialogs and the lock screen.
- **KDE Plasma / Qt** — Plasma colour schemes, Kvantum `OsirisDark` /
  `OsirisLight` (`.kvconfig` + generated element SVG), `OsirisDark` Aurorae
  decoration, `Osiris` Plasma desktop theme.
- **GRUB2** — `boot/grub/theme.txt`, generated background + boot-menu icons +
  9-slice pixmaps, Fira Code `.pf2` generation, `install.sh`.
- **Wallpapers** — `Abstract Bloom` and `Ancient Egypt Sci-Fi`, each Day/Night at
  3840×2160 / 2560×1440 / 1920×1080 / 1366×768, plus GNOME time-of-day dynamic
  XML and KDE light/dark wallpaper packages (`scripts/generate-wallpapers.py`).
- **Build & packaging**
  - `Makefile` + `scripts/build.sh` orchestrator, `scripts/install-local.sh`.
  - Debian source package → `osiris-theme-gtk`, `osiris-theme-plasma`,
    `osiris-theme-grub`, `osiris-wallpapers`, `osiris-desktop-theme` (meta).
  - RPM spec with the matching subpackage split.
  - GitHub Actions: `build.yml` (token guard, vsix, deb, rpm, Pages) and
    `release.yml` (tag `v*` → GitHub Release with every artifact + Pages deploy).

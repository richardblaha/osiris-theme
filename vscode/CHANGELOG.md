# Changelog — Osiris Theme (VS Code)

All notable changes to the VS Code extension are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.1] — 2026-09-04

### Changed
- Publisher `osiris-labs` → `osiris-ide` — extension identifier is now
  `osiris-ide.osiris-theme`.
- `configurationDefaults` now sets `workbench.colorTheme` to `Osiris Dark`
  (plus `workbench.preferredDark/LightColorTheme`) as a real global default —
  *Osiris Dark* activates on install on a fresh profile, not just for scoped
  `[Osiris Dark]` settings.

### Added
- README "Font" section — VS Code cannot load a bundled font; install Fira Code
  yourself (the family falls back to `ui-monospace`). The repo bundles the
  webfont for the docs site and the npm themes.

## [0.1.0] — 2026-09-04

### Added
- Initial `Osiris Dark` and `Osiris Light` color themes derived from
  `assets/tokens.json` / `docs/preview/`.
- Workbench, editor, syntax (TextMate + semantic), terminal ANSI, git decoration,
  diff, peek, notification, settings-editor and debug colours.
- `configurationDefaults` enabling Fira Code + ligatures per theme.

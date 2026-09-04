# Osiris Theme for VS Code

Dual-accent theme suite built from the
[OSIRIS design system](https://richardblaha.github.io/osiris-theme/) — one
extension, three contributions:

| Contribution | Ids |
|---|---|
| **Color theme** | *Osiris Dark* · *Osiris Light* |
| **File Icon Theme** | *Osiris File Icons* |
| **Product Icon Theme** | *Osiris Product Icons* |

- **Osiris Dark** — cyan `#00f2fe` / rose `#ff2a85` on a `#0d1117 / #161b22` neutral ramp.
- **Osiris Light** — blue `#0969da` / rose `#e01a76` on white / `#f6f8fa`.
- **Osiris File Icons** — Material-Symbols glyphs, ~155 extensions + ~48 filenames,
  folder & language associations, dark/light folder tint.
- **Osiris Product Icons** — `osiris-symbols.woff` remapping ~400 product-icon
  ids (activity bar, status bar, SCM, debug, test, search, symbols …).

The colour themes ship `configurationDefaults` that turn on Fira Code with
ligatures while active.

The icon themes are generated from
[`iconography/`](../iconography/) by
[`scripts/lib/gen_icons.py`](../scripts/lib/gen_icons.py) at build time
(`fileicons/` + `producticons/` are git-ignored). See
[`docs/ICONOGRAPHY.md`](../docs/ICONOGRAPHY.md).

## Install

- **Marketplace / Open VSX:** search for *Osiris Theme* by `osiris-ide`
  (extension id `osiris-ide.osiris-theme`).
- **From a release:** download `osiris-theme-<version>.vsix` from
  [Releases](https://github.com/richardblaha/osiris-theme/releases) and run
  `code --install-extension osiris-theme-<version>.vsix`.

Then: **Preferences: Color Theme → Osiris Dark / Osiris Light**.

*Osiris Dark* is also declared as the extension's default `workbench.colorTheme`,
so on a fresh profile it activates on install without picking it by hand.

### Font

The colour themes set `editor.fontFamily` to **Fira Code** with ligatures. VS Code
cannot load a font from an extension, so install Fira Code yourself —
`fonts-firacode` (Debian/Ubuntu), `brew install --cask font-fira-code` (macOS),
or the [official release](https://github.com/tonsky/FiraCode/releases). The
family falls back to `ui-monospace` / the platform monospace when it is absent.
The repo bundles the webfont (`assets/fonts/fira-code/`, SIL OFL-1.1) for the
docs site and the npm themes.

## Development

The theme JSON is generated-adjacent: colours are the canonical
`assets/tokens.json` values from the repo root. After editing a theme file, run
`node scripts/check-tokens.mjs` from the repo root to confirm it still agrees
with the design tokens, then `npm run package` here to build the `.vsix`.

See the repo root [`README.md`](../README.md) and
[`docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).

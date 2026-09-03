# Osiris Theme for VS Code

Dual-accent color theme built from the [OSIRIS design system](https://richardblaha.github.io/osiris-themes/).

- **Osiris Dark** — cyan `#00f2fe` / rose `#ff2a85` on a `#0d1117 / #161b22` neutral ramp.
- **Osiris Light** — blue `#0969da` / rose `#e01a76` on white / `#f6f8fa`.

Both themes ship `configurationDefaults` that turn on Fira Code with ligatures
while the theme is active.

## Install

- **Marketplace / Open VSX:** search for *Osiris Theme* by `osiris-labs`.
- **From a release:** download `osiris-theme-<version>.vsix` from
  [Releases](https://github.com/richardblaha/osiris-themes/releases) and run
  `code --install-extension osiris-theme-<version>.vsix`.

Then: **Preferences: Color Theme → Osiris Dark / Osiris Light**.

## Development

The theme JSON is generated-adjacent: colours are the canonical
`assets/tokens.json` values from the repo root. After editing a theme file, run
`node scripts/check-tokens.mjs` from the repo root to confirm it still agrees
with the design tokens, then `npm run package` here to build the `.vsix`.

See the repo root [`README.md`](../README.md) and
[`docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).

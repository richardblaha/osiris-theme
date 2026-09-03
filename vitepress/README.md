# OSIRIS theme for VitePress

Dual-accent stylesheet that skins the [VitePress](https://vitepress.dev) default
theme with the [OSIRIS design system](https://richardblaha.github.io/osiris-themes/).

- **Dark** — cyan `#00f2fe` / rose `#ff2a85` on a `#0d1117 / #161b22` ramp.
- **Light** — blue `#0969da` / rose `#e01a76` on white / `#f6f8fa`.

Colours are the canonical `assets/tokens.json` values from the repo root, mapped
onto VitePress's `--vp-c-*` design tokens.

## Install

```sh
npm i -D osiris-vitepress-theme
```

Use it directly as your theme:

```js
// .vitepress/theme/index.js
export { default } from 'osiris-vitepress-theme'
```

…or keep your own theme entry and just pull in the stylesheet:

```js
// .vitepress/theme/index.js
import DefaultTheme from 'vitepress/theme'
import 'osiris-vitepress-theme/style.css'

export default DefaultTheme
```

Pair it with Shiki syntax themes that share the same GitHub-flavoured ramp:

```js
// .vitepress/config.js
export default {
  markdown: {
    theme: { light: 'github-light', dark: 'github-dark' },
  },
}
```

The stylesheet sets `--vp-font-family-mono` to Fira Code (with ligatures) — load
the webfont yourself if your host doesn't have it.

### Without npm

Copy [`theme/osiris.css`](theme/osiris.css) into your docs at
`.vitepress/theme/osiris.css` and `import './osiris.css'` from your theme entry.

## What it covers

- Brand / link / button colours (`--vp-c-brand-*`, `--vp-button-brand-*`)
- Surfaces, borders, text ramp (`--vp-c-bg*`, `--vp-c-border`, `--vp-c-text-*`)
- Custom-block accents — tip, note, success, warning, danger, **important**
  (rose secondary)
- Inline + block code backgrounds and line highlight
- Home-hero name gradient and glow (the signature cyan → rose sweep)
- Signature touches: cyan active-nav underline, 2px accent bar on the active
  sidebar item, accent focus ring (DESIGN_SYSTEM §6)

See the repo root [`README.md`](../README.md) and
[`docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).

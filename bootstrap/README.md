# OSIRIS theme for Bootstrap 5

Dual-accent Bootstrap 5 build with the
[OSIRIS design system](https://richardblaha.github.io/osiris-theme/) palette
baked in — both color modes.

- **Light** — blue `#0969da` / rose `#e01a76` on white / `#f6f8fa`.
- **Dark** (`data-bs-theme="dark"`) — cyan `#00f2fe` / rose `#ff2a85` on
  `#0d1117 / #161b22`.

All colours are the canonical `assets/tokens.json` values from the repo root.

## Install

```sh
npm i osiris-bootstrap-theme
```

### Drop-in CSS (replaces `bootstrap.css`)

```html
<link rel="stylesheet" href="node_modules/osiris-bootstrap-theme/dist/osiris-bootstrap.min.css">
```

```js
import 'osiris-bootstrap-theme/dist/osiris-bootstrap.min.css'
import 'bootstrap' // JS as usual
```

Toggle dark mode with `<html data-bs-theme="dark">` (or `"light"`).

### Sass

Compile Bootstrap yourself with the OSIRIS variables and dark mode layered in:

```scss
// your-styles.scss  —  needs node_modules on the Sass load path
@import "osiris-bootstrap-theme/scss/osiris";
```

…or cherry-pick just the variable overrides before your own Bootstrap import:

```scss
@import "osiris-bootstrap-theme/scss/variables";
@import "bootstrap/scss/bootstrap";
@import "osiris-bootstrap-theme/scss/dark";
@import "osiris-bootstrap-theme/scss/signature";
```

## What it covers

- `$primary` / `$secondary` / `$success` / `$info` / `$warning` / `$danger`,
  surfaces, borders, links, code, `$border-radius`, Inter + Fira Code fonts
- `[data-bs-theme="dark"]` overrides for every `--bs-*` accent, surface and
  subtle/emphasis triplet, plus `.btn-primary` / `.btn-secondary` /
  `.btn-outline-primary` (which bake their colours at compile time)
- Signature touches: 2px accent bar on active nav/tabs, accent focus ring,
  accent checkboxes and progress bars (`scss/_signature.scss`)

## Build

```sh
npm ci
npm run build   # -> dist/osiris-bootstrap.css + .min.css
```

`dist/` is generated (git-ignored); CI builds it before publishing. See the repo
root [`README.md`](../README.md) and
[`docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).

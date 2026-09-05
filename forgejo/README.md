# OSIRIS theme for Forgejo / Gitea

Dual-accent stylesheets that skin [Forgejo](https://forgejo.org) (and Gitea,
which shares the theming mechanism) with the
[OSIRIS design system](https://richardblaha.github.io/osiris-theme/) — the same
cyan/rose ramp as every other OSIRIS target.

| File | Theme id | Mode |
|---|---|---|
| [`theme-osiris-dark.css`](theme-osiris-dark.css) | `osiris-dark` | cyan `#00f2fe` / rose `#ff2a85` on `#0d1117` / `#161b22` |
| [`theme-osiris-light.css`](theme-osiris-light.css) | `osiris-light` | blue `#0969da` / rose `#e01a76` on white / `#f6f8fa` |
| [`theme-osiris-auto.css`](theme-osiris-auto.css) | `osiris-auto` | follows the OS light/dark preference |

Each file `@import`s the matching stock Forgejo theme
(`theme-forgejo-{dark,light}.css`, shipped at `/assets/css/` by every Forgejo
build) and then re-points the OSIRIS-relevant `--color-*` design tokens. That
keeps the sheet small and forward-compatible: a token Forgejo adds in a later
release simply keeps its upstream default. Colours are the canonical
[`assets/tokens.json`](../assets/tokens.json) values.

## Install

Drop the CSS **and the bundled Fira Code webfont** into your instance's custom
directory (`$FORGEJO_CUSTOM`, usually `/var/lib/forgejo/custom` or `./custom`
next to the binary — Gitea: `$GITEA_CUSTOM`). The `@font-face` in each theme
resolves `FiraCode-VF.woff2` from the same `css/` directory:

```sh
install -Dm644 forgejo/theme-osiris-*.css forgejo/FiraCode-VF.woff2 \
  "$FORGEJO_CUSTOM/public/assets/css/"
```

Register the themes in `app.ini` and (optionally) make one the default:

```ini
[ui]
THEMES = forgejo-auto,forgejo-light,forgejo-dark,osiris-auto,osiris-dark,osiris-light
DEFAULT_THEME = osiris-auto
```

Restart Forgejo. Users pick the theme under **Avatar → Settings → Appearance**.

### Docker

Mount the repo `forgejo/` files into the image's asset path:

```yaml
volumes:
  - ./theme-osiris-dark.css:/data/gitea/public/assets/css/theme-osiris-dark.css:ro
  - ./theme-osiris-light.css:/data/gitea/public/assets/css/theme-osiris-light.css:ro
  - ./theme-osiris-auto.css:/data/gitea/public/assets/css/theme-osiris-auto.css:ro
  - ./FiraCode-VF.woff2:/data/gitea/public/assets/css/FiraCode-VF.woff2:ro
```

On Kubernetes, put all four files in one ConfigMap (`--from-file`) mounted at
`/data/gitea/public/assets/css` — `kubectl` stores the `.woff2` as `binaryData`
automatically.

and set `FORGEJO__ui__THEMES` / `FORGEJO__ui__DEFAULT_THEME` (or the `GITEA__…`
equivalents) in the environment.

## Build the distributable zip

```sh
make forgejo   # -> dist/osiris-forgejo-<ver>.zip  (the three CSS files + this README)
```

## What it covers

- Typography — **Fira Code for the whole UI, prose and code** (`--fonts-*`),
  bundled as `FiraCode-VF.woff2` (SIL OFL-1.1)
- Brand / link / button colours — the full `--color-primary*` ramp (cyan dark /
  blue light) with `--color-primary-contrast` set to the OSIRIS inverse ink
- The neutral ramp — `--color-secondary*`, borders, chips, button surfaces
- Target surfaces — body, boxes, nav, footer, menus, cards, inputs, code blocks
  (`--color-body`, `--color-box-*`, `--color-nav-bg`, `--color-markup-code-*`, …)
- Status surfaces — error / success / warning / info backgrounds, borders, text
- Diff colours — GitHub-flavoured added / removed / moved rows and words
- Named label colours — `--color-red/green/yellow/blue/pink/…` from the OSIRIS
  state palette
- Secondary accent (rose) — `@mention` and code-search-hit highlight
  (`--color-highlight-*`)
- Signature touches — a 2px accent rule under the top nav, a rose underline on
  the active nav item, and the accent focus ring (DESIGN_SYSTEM §6)

Syntax highlighting (chroma / codemirror) is inherited from the stock Forgejo
theme.

See the repo root [`README.md`](../README.md) and
[`docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).

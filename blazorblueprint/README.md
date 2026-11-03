# OSIRIS theme for Blazor Blueprint UI

Dual-accent theme for [Blazor Blueprint](https://blazorblueprintui.com) — the
shadcn/ui-inspired component library for Blazor — built from the
[OSIRIS design system](https://richardblaha.github.io/osiris-theme/) palette.

- **Light** (`:root`) — blue `#0969da` / rose `#e01a76` on white / `#f6f8fa`.
- **Dark** (`.dark`) — cyan `#00f2fe` / rose `#ff2a85` on `#0d1117 / #161b22`.

All colours are the canonical `assets/tokens.json` values from the repo root,
mapped onto the Blazor Blueprint CSS variables (`--primary`, `--background`,
`--ring`, `--chart-*`, `--sidebar-*`, alert triplets, …). Hex is used instead
of OKLCH — Blazor Blueprint accepts any valid CSS color format. Shape language
follows OSIRIS: 4 px controls, 6/8 px floating surfaces, no pills
(`--radius: 0.25rem`). Fira Code is the single typeface (`--font-sans` /
`--font-mono`) and ships in `fonts/`.

## Install

```sh
npm i osiris-blazorblueprint-theme
```

Copy the stylesheet and the bundled font into your `wwwroot` (keep the
`css/` / `fonts/` structure — `osiris.css` references `../fonts/`):

```sh
mkdir -p wwwroot/css wwwroot/fonts
cp node_modules/osiris-blazorblueprint-theme/css/osiris.css wwwroot/css/
cp node_modules/osiris-blazorblueprint-theme/fonts/FiraCode-VF.woff2 wwwroot/fonts/
```

Then load the theme **before** the Blazor Blueprint stylesheet in `App.razor`
(or `index.html` for WASM):

```html
<head>
  <!-- 1. OSIRIS theme variables — must come first -->
  <link href="css/osiris.css" rel="stylesheet" />

  <!-- 2. Blazor Blueprint components -->
  <link href="_content/BlazorBlueprint.Components/blazorblueprint.css" rel="stylesheet" />
</head>
```

## Dark mode

Add the `dark` class to the `<html>` element — the `ThemeService` /
`BbDarkModeToggle` / `BbThemeSwitcher` components do this automatically and
persist the choice to `localStorage`:

```html
<html class="dark">
```

For a no-flash first paint, apply the saved theme with the library's
`_content/BlazorBlueprint.Components/js/theme-init.js` after the styles, or set
the class in a blocking inline script of your own.

## What it covers

- Core: `--background`, `--foreground`, `--card`, `--popover`, `--primary`,
  `--secondary`, `--muted`, `--accent`, `--destructive`, `--border`,
  `--input`, `--ring` (+ `-foreground` pairs) — both `:root` and `.dark`
- Alerts: `--alert-{success,info,warning,danger}{,-foreground,-bg}`
- Charts: `--chart-1 … --chart-5` (ECharts resolves them at runtime)
- Sidebar: the full `--sidebar-*` set
- `--radius` scale (4/4/6/8 px), `--font-sans` / `--font-serif` / `--font-mono`
  (Fira Code), `color-scheme` per mode

## Build

From the repo root: `make blazorblueprint` packs
`dist/osiris-blazorblueprint-theme-<ver>.tgz` (plain CSS — no build step).
`make tokens` verifies the colours against `assets/tokens.json`.

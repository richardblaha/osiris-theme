# Contributing to osiris-themes

## The golden rule: one source of truth

Every colour in every theme comes from [`assets/tokens.json`](assets/tokens.json),
and every icon from [`iconography/glyphs.json`](iconography/glyphs.json). Do
**not** hand-tune a hex in a theme file or add a glyph straight into a target —
CI (`scripts/check-tokens.sh`) fails on drift between the tokens, the VS Code
themes, `docs/DESIGN_SYSTEM.md`, the browser manifests, and on any icon map that
references a glyph that does not exist.

Workflow for a palette change:

1. Edit `assets/tokens.json`.
2. Update `docs/preview/styles.css` (`:root` / `[data-theme]`) and
   `docs/DESIGN_SYSTEM.md` to match.
3. Re-derive downstream: edit the affected theme files (including
   `vitepress/theme/osiris.css`, `bootstrap/scss/_variables.scss` +
   `bootstrap/scss/_dark.scss`, and `browsers/*/manifest.json`), or for the
   templated ones just `make desktop icons terminal browsers`. Terminal ANSI
   colours also live in `assets/tokens.json → terminal` (kept in sync with the
   VS Code `terminal.ansi*` values).
4. `make tokens` — must pass.
5. Eyeball `docs/preview/index.html` (dark + light toggle) — it is the acceptance
   test.

For an **icon** change see [`docs/ICONOGRAPHY.md`](docs/ICONOGRAPHY.md): add the
glyph to `iconography/glyphs.json`, wire it in `iconography/map/*.json`,
`make tokens`, then `make icons vscode`.

## Layout

| Path | What |
|---|---|
| `assets/` | tokens, shared icons, wallpaper SVG sources + dynamic definitions |
| `docs/preview/` | interactive reference (GitHub Pages root) |
| `docs/DESIGN_SYSTEM.md` · `docs/ICONOGRAPHY.md` | the written specs |
| `iconography/` | `glyphs.json` (Material-Symbols primitives) + `map/` |
| `vscode/` | VS Code extension — colour + file + product icon themes |
| `vitepress/` | npm `osiris-vitepress-theme` — VitePress default-theme override |
| `bootstrap/` | npm `osiris-bootstrap-theme` — Bootstrap 5 Sass build |
| `browsers/` | Chromium (MV3) + Firefox (MV2) theme manifests |
| `desktop/` | GTK / GNOME Shell / KDE Plasma / terminal sources |
| `boot/grub/` | GRUB2 theme |
| `packaging/` | `debian/`, `rpm/`, shared helper scripts |
| `scripts/` | `build.sh`, `check-tokens.sh`, `lib/` (`gen_icons.py`, …) |

## Building locally

```sh
make help          # list targets
make tokens        # palette drift guard  (needs: jq)
make vscode        # -> dist/osiris-theme-<ver>.vsix   (needs: node, vsce/npx, fantasticon, rsvg-convert)
make npm           # -> dist/osiris-{vitepress,bootstrap}-theme-<ver>.tgz  (needs: npm)
make icons         # -> build/icons/Osiris/            (XDG icon theme; needs: python3)
make terminal      # -> build/terminal/                (GNOME Terminal / Ptyxis / Konsole)
make browsers      # -> dist/osiris-{chromium,firefox}-{dark,light}-<ver>.zip  (needs: zip)
make desktop       # -> build/themes/, build/plasma/
make grub          # -> build/grub/osiris/             (needs: python3-pil, rsvg-convert)
make wallpapers    # -> build/wallpapers/              (needs: python3 + rsvg-convert/inkscape/cairosvg)
make deb           # -> dist/*.deb                     (needs: dpkg-dev, debhelper)
make rpm           # -> dist/*.rpm                     (needs: rpm-build)
make install-local # build + drop themes into ~/.local/share and switch
```

## Commits & releases

- Conventional-ish commit subjects (`feat(gtk): …`, `fix(grub): …`, `docs: …`).
- Bump `VERSION`, update `CHANGELOG.md`, tag `vX.Y.Z` → `release.yml` builds and
  attaches every `.vsix` / `.tgz` / `.zip` / `.deb` / `.rpm`, publishes the npm
  packages (needs the `NPM_TOKEN` repo secret) and deploys the Pages site.
- All npm packages take their version from `VERSION` at build time — don't
  hand-edit `version` in the `package.json` files.

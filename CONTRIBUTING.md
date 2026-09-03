# Contributing to osiris-themes

## The golden rule: one source of truth

Every colour in every theme comes from [`assets/tokens.json`](assets/tokens.json).
Do **not** hand-tune a hex in a theme file without changing the token — CI
(`scripts/check-tokens.sh`) fails on drift between the tokens, the VS Code themes
and `docs/DESIGN_SYSTEM.md`.

Workflow for a palette change:

1. Edit `assets/tokens.json`.
2. Update `docs/preview/styles.css` (`:root` / `[data-theme]`) and
   `docs/DESIGN_SYSTEM.md` to match.
3. Re-derive downstream: edit the affected theme files, or for the templated
   ones just `make desktop`.
4. `make tokens` — must pass.
5. Eyeball `docs/preview/index.html` (dark + light toggle) — it is the acceptance
   test.

## Layout

| Path | What |
|---|---|
| `assets/` | tokens, shared icons, wallpaper SVG sources + dynamic definitions |
| `docs/preview/` | interactive reference (GitHub Pages root) |
| `docs/DESIGN_SYSTEM.md` | the written spec |
| `vscode/` | VS Code extension (themes + `package.json`) |
| `desktop/` | GTK / GNOME Shell / KDE Plasma sources |
| `boot/grub/` | GRUB2 theme |
| `packaging/` | `debian/`, `rpm/`, shared helper scripts |
| `scripts/` | `build.sh`, `generate-wallpapers.py`, `check-tokens.sh`, `lib/` |

## Building locally

```sh
make help          # list targets
make tokens        # palette drift guard  (needs: jq)
make vscode        # -> dist/osiris-theme-<ver>.vsix   (needs: node, vsce/npx, rsvg-convert)
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
  attaches every `.vsix` / `.deb` / `.rpm` and deploys the Pages site.

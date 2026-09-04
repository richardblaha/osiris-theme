# Fira Code (bundled)

The OSIRIS visual language uses **[Fira Code](https://github.com/tonsky/FiraCode)**
as its monospace / code face (with ligatures on). It is bundled here so every
surface that references `Fira Code` — the docs/preview site, the VitePress and
Bootstrap npm themes, the GRUB boot menu — can ship the actual font instead of
relying on it being installed system-wide.

## Contents

| File | Use |
|---|---|
| `FiraCode-VF.woff2` | variable font, `wght 300–700` — what the web `@font-face` rules load |
| `FiraCode-{Light,Regular,Medium,SemiBold,Bold}.woff2` | static instances (older engines, GRUB `grub-mkfont` source when no TTF is available) |
| `LICENSE` | SIL Open Font License 1.1 |

Version: **6.2** (`tonsky/FiraCode`, 2021-12-06).

## License

Fira Code is licensed under the **SIL Open Font License 1.1** (`LICENSE` in this
directory) — a permissive, redistribution-friendly font licence. It is tracked
separately from the repository's MIT licence; see
[`packaging/debian/debian/copyright`](../../../packaging/debian/debian/copyright).

## Where it is referenced

- `docs/preview/styles.css` — `@font-face` → `assets/fonts/fira-code/` (staged
  into the Pages build by `scripts/build.sh pages`)
- `vitepress/theme/osiris.css` — `@font-face` → `./fonts/FiraCode-VF.woff2`
  (shipped inside the npm package)
- `bootstrap/scss/_fonts.scss` — `@font-face` → `../fonts/FiraCode-VF.woff2`
  (shipped inside the npm package)
- `boot/grub/theme.txt` — `Fira Code Regular/Medium` `.pf2`, generated at build
  time from a TTF (`scripts/build.sh grub`, see `boot/grub/fonts/README.md`)
- `vscode/themes/*` set `editor.fontFamily: 'Fira Code'` — VS Code cannot load a
  font from an extension, so users install Fira Code themselves; the family
  falls back to `ui-monospace` when it is missing.

## Refreshing

```sh
scripts/lib/fetch-fira-code.sh          # re-downloads the pinned release into this dir
```

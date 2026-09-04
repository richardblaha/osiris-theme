# OSIRIS application icons

Generated from [`vscode/icon.svg`](../../../vscode/icon.svg) (the rounded-tile
mark) by [`scripts/lib/gen_appicons.py`](../../../scripts/lib/gen_appicons.py).
Regenerate after editing the source:

```sh
make appicons        # -> scripts/build.sh appicons
```

## Layout

| Path | Format | Use |
|---|---|---|
| `osiris.ico` | Windows ICO, 16/24/32/48/64/128/256 | `electron-builder` `win.icon`, NSIS, `.exe` resource |
| `osiris.icns` | Apple ICNS, 16–512 + @2x | `electron-builder` `mac.icon`, `.app` bundle |
| `png/osiris-<n>.png` | PNG, n ∈ 16 32 48 64 128 256 512 1024 | `electron-builder` `linux.icon` dir, Snap/Flatpak, favicons, docs |
| `hicolor/<n>x<n>/apps/osiris.png` + `hicolor/scalable/apps/osiris.svg` | freedesktop icon theme tree | `install -Dm644` into `/usr/share/icons/hicolor/…` from a `.deb`/`.rpm`/AppImage |

## electron-builder

```jsonc
// electron-builder.yml — paths relative to the app root
"win":   { "icon": "assets/icons/app/osiris.ico" },
"mac":   { "icon": "assets/icons/app/osiris.icns" },
"linux": { "icon": "assets/icons/app/png" }        // directory of osiris-<n>.png
```

These files are committed so a downstream packager never has to run the
generator. Re-run `make appicons` and commit the result whenever
`vscode/icon.svg` changes.

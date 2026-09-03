# desktop/ — Linux desktop themes

Sources for the GTK, GNOME Shell, Metacity, GtkSourceView, KDE Plasma / Qt and
terminal themes. Nothing here is installed verbatim; `scripts/build.sh` assembles
it into installable trees under `build/`, and the `.deb` / `.rpm` packaging
stages those. Every artifact ships **both** an `Osiris` (dark) and an
`Osiris-Light` (light) variant.

| Source | Assembled into | Installed path |
|---|---|---|
| `gtk-common/colors-dark.css` + `widgets.css` + `gtk-3.0/gtk3.css` | `Osiris/gtk-3.0/gtk.css` (+ `gtk-dark.css`) | `/usr/share/themes/Osiris/` |
| `gtk-common/colors-light.css` + `widgets.css` + `gtk-3.0/gtk3.css` | `Osiris-Light/gtk-3.0/gtk.css` | `/usr/share/themes/Osiris-Light/` |
| `gtk-common/colors-*.css` + `widgets.css` + `gtk-4.0/gtk4.css` | `Osiris{,-Light}/gtk-4.0/gtk.css` | same |
| `gnome-shell/gnome-shell.css.in` (+ `assets/`) | `Osiris{,-Light}/gnome-shell/` | same |
| `metacity-1/metacity-theme-3.xml.in` | `Osiris{,-Light}/metacity-1/metacity-theme-3.xml` | same |
| `index.theme.in` | `Osiris{,-Light}/index.theme` | same |
| `assets/tokens.json` (via `scripts/lib/gen_sourceview.py`) | `build/sourceview/Osiris{,-Light}.xml` | `/usr/share/gtksourceview-{5,4,3.0}/styles/osiris{,-light}.xml` |
| `assets/tokens.json` (via `scripts/lib/gen_terminal.py`) | `build/terminal/{gnome-terminal,ptyxis,konsole}/` | see [`terminal/`](terminal/README.md) |
| `plasma/color-schemes/*.colors` | — (copied as-is) | `/usr/share/color-schemes/` |
| `plasma/Kvantum/Osiris{Dark,Light}/` (+ generated `.svg`) | — | `/usr/share/Kvantum/Osiris{Dark,Light}/` |
| `plasma/aurorae/OsirisDark/` | — | `/usr/share/aurorae/themes/OsirisDark/` |
| `plasma/desktoptheme/Osiris/` | — | `/usr/share/plasma/desktoptheme/Osiris/` |

## Applying a built theme locally (without a package)

```sh
scripts/build.sh desktop        # -> build/themes/, build/kvantum/, ...
scripts/install-local.sh desktop --dark      # copies into ~/.local/share + ~/.themes and switches
```

## GTK 4 / libadwaita caveat

libadwaita apps ignore `/usr/share/themes` unless `GTK_THEME` is set or the app
opts in. `osiris-gtk-theme --apply` (shipped in `osiris-theme-gtk.deb`) writes the
opt-in drop-in to `~/.config/gtk-4.0/{gtk.css,colors.css}` and sets the GNOME
`color-scheme` / legacy `gtk-theme` keys.

## Kvantum & Plasma SVGs

The Kvantum element sheet is generated from `assets/tokens.json` by
`scripts/lib/gen_kvantum_svg.py` during the build (flat, matches the preview
page). The Plasma `desktoptheme` ships a minimal hand-authored SVG set
(`panel-background`, `background`, `tasks`); Plasma falls back to Breeze drawing
for any element not overridden, tinted by the `colors` file.

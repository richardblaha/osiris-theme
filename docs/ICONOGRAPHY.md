# OSIRIS Iconography

The icon design language for every OSIRIS surface — the VS Code **file icon theme** and
the Linux **XDG icon theme**. Like the colour system it is generated from a single
pipeline:

- **Shape source:** [Papirus Icon Theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme) — fetched at build time via shallow git clone, cached in `build/papirus-src/`
- **Name wiring:** [`iconography/icon_map.json`](../iconography/icon_map.json)
- **Generator:** [`scripts/lib/gen_icons.py`](../scripts/lib/gen_icons.py)
- **Colour + geometry tokens:** [`assets/tokens.json → icon`](../assets/tokens.json)

`scripts/check-tokens.sh` fails CI if this document and `assets/tokens.json` disagree.

The VS Code **product icon theme** has been removed. VS Code falls back to its built-in
Codicon set.

---

## 1. Design language — Papirus Icon Theme

OSIRIS icons are **real Papirus Icon Theme SVGs**, recoloured with the Osiris palette at
build time. The Papirus visual language — crisp, flat geometric shapes on a 24x24 grid —
is preserved; only the colours change.

| Token | Value | Meaning |
|---|---|---|
| `icon.grid` | `24` | Every glyph is authored on a 24x24 `viewBox` |
| `icon.liveArea` | `20` | Icon content stays within a centred 20x20 box |
| `icon.padding` | `2` | 2 dp clear space on every edge |
| `icon.keyline.square` | `18` | Square shapes (e.g. `stop`) |
| `icon.keyline.circle` | `20` | Round shapes (e.g. `info`, `run`) |
| `icon.keyline.verticalRect` | `16 x 20` | Portrait shapes (e.g. `file`, `phone`) |
| `icon.keyline.horizontalRect` | `20 x 16` | Landscape shapes (e.g. `computer`) |
| `icon.strokeEquivalent` | `2` | Nominal stroke / bar weight |
| `icon.cornerRadius.outer` | `1` | Outer corner rounding |
| `icon.cornerRadius.inner` | `0` | Inner corner rounding |

The Papirus source is a shallow git clone cached in `build/papirus-src/`. The
generator reads 24x24 SVGs from `Papirus/24x24/<context>/<name>.svg`, resolves symlinks,
recolours every `fill` attribute, and writes the result to the output theme.

---

## 2. Colour remapping engine

The generator replaces every fill colour in each Papirus SVG with its Osiris equivalent.
The remapping has two layers:

### Structural colours

Papirus paper, greys, and folder-blue are mapped exactly to the Osiris neutral ramp
(GitHub-style `#0d1117` / `#161b22` / `#30363d` / ...) and the Osiris folder-cyan family.
This preserves the structural hierarchy — shadows, highlights, layering — while shifting
the palette.

### Accent colours

Every other colour is classified by hue into one of seven Osiris accent families:

| Family | Osiris hue | Reference |
|---|---|---|
| Red | 358 | `#f2585b` |
| Amber | 40 | `#d9a441` |
| Green | 120 | `#3fb950` |
| Cyan | 186 | `#22c3d6` |
| Blue | 210 | `#589bf0` |
| Violet | 258 | `#a684f5` |
| Rose | 330 | `#f0509a` |

The original **value** (brightness) is preserved so the Papirus visual hierarchy stays
intact; only the **hue** and **saturation** are shifted to the Osiris family for that
colour range. Low-saturation colours fall through to the neutral ramp by brightness.

---

## 3. `icon_map.json` structure

[`iconography/icon_map.json`](../iconography/icon_map.json) is the single wiring file. It
has these sections:

### `vscode_file` — VS Code file icon theme

| Key | Type | Maps to |
|---|---|---|
| `file` | string | Papirus mimetype icon for the default file |
| `folder` / `folderOpen` | string | Papirus place icons for folders |
| `fileExtensions` | `{ "ext": "papirus-name" }` | ~155 extensions to Papirus mimetype icons |
| `fileNames` | `{ "name": "papirus-name" }` | ~48 specific filenames to Papirus mimetype icons |
| `folderNames` | `{ "name": "papirus-name" }` | folder names to Papirus place icons |
| `folderNamesExpanded` | `{ "name": {} }` | expanded folder names (use open folder) |
| `languageIds` | `{ "lang": "ext-key" }` | VS Code language IDs to extension keys |

### `xdg` — freedesktop icon theme

One sub-object per XDG context (`actions`, `apps`, `categories`, `devices`, `emblems`,
`mimetypes`, `places`, `status`), mapping XDG icon names to Papirus icon names. Used for
explicit overrides where the XDG name differs from the Papirus name.

### `xdg_aliases` — XDG symlink aliases

Same structure as `xdg`; each entry becomes a same-directory relative symlink to its
target. Covers legacy GTK stock ids, GNOME/KDE app-id spellings, and MIME fallbacks.

---

## 4. VS Code — file icon theme

`osiris-file-icons` (label **Osiris File Icons**). Generated to `vscode/fileicons/`:

- `osiris-file-icons.json` — `iconDefinitions` + `file`, `folder`, `folderExpanded`,
  `rootFolder`, `rootFolderExpanded`, `fileExtensions`, `fileNames`, `folderNames`,
  `folderNamesExpanded`, `languageIds`.
- `icons/*.svg` — one recoloured Papirus SVG per definition.

File icons are **shared** with the XDG mimetype directory: the same recoloured Papirus
mimetype SVGs serve both the VS Code file icon theme and `build/icons/Osiris/.../mimetypes/`.
One set of SVGs, two consumers.

---

## 5. Linux — XDG icon theme

Theme id **Osiris** (`icon.xdg.themeName`), `Inherits=Papirus-Dark,Papirus,breeze,gnome,hicolor`
so anything unstyled falls through to the platform default. Generated to
`build/icons/Osiris/`.

### Structure (freedesktop Icon Theme spec)

```
Osiris/
├── index.theme                       # [Icon Theme] + one section per directory
├── scalable/<context>/*.svg          # the vector master — Type=Scalable, 8-512
└── <size>x<size>/<context>/*.svg     # 16, 24, 32, 48, 64, 128 — Type=Threshold
```

`<context>` is every mandatory category:
`actions/ apps/ categories/ devices/ emblems/ mimetypes/ places/ status/`.

The generator copies **all** Papirus 24x24 SVGs (recoloured) into `scalable/`, then adds
explicit overrides from `icon_map.json -> xdg` where the XDG name differs from the Papirus
name. Aliases from `icon_map.json -> xdg_aliases` become same-directory relative symlinks.

It is an **all-vector** theme: the fixed-size directories carry the same SVG as a
relative symlink into `scalable/`, so GNOME and KDE render crisply at any scale.

---

## 6. Adding or changing an icon

1. Find the Papirus icon name you want (browse `build/papirus-src/Papirus/24x24/`).
2. Wire it in [`iconography/icon_map.json`](../iconography/icon_map.json):
   - `vscode_file.fileExtensions` / `fileNames` / `folderNames` for VS Code
   - `xdg.<context>` for XDG (where the XDG name differs from the Papirus name)
   - `xdg_aliases.<context>` for symlink aliases
3. `make tokens` — must pass.
4. `make icons vscode` — regenerates both icon themes.
5. `make pages` — regenerates `docs/preview/icons.js`; commit it.

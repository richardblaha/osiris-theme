# OSIRIS Iconography

The icon design language for every OSIRIS surface — the VS Code **file** and
**product** icon themes and the Linux **XDG icon theme**. Like the colour system
it is generated from a single source:

- **Official upstream outlines:** [`iconography/material_symbols.json`](../iconography/material_symbols.json)
- **Upstream-name mapping:** [`iconography/material_map.json`](../iconography/material_map.json)
- **Custom fallback outlines:** [`iconography/glyphs.json`](../iconography/glyphs.json)
- **Assignment maps:** [`iconography/map/`](../iconography/map/) —
  `filetypes.json`, `xdg.json`, `producticons.json`
- **Generator:** [`scripts/lib/gen_icons.py`](../scripts/lib/gen_icons.py)
- **Colour + geometry tokens:** [`assets/tokens.json → icon`](../assets/tokens.json)

`scripts/check-tokens.sh` fails CI if a map references a glyph that does not
exist, or if this document and `assets/tokens.json` disagree.

---

## 1. Design language — Material Symbols Rounded 300

OSIRIS uses the actual outlines extracted from Google's official **Material Symbols
Rounded** variable font at weight `300`, grade `0`, optical size `24`, and fill `0`.
The committed dataset records upstream revision `10ecc14790612ca8fd164e3f4ffe9c16fc50d5b7`
and is covered by Apache-2.0 (`iconography/LICENSE.material-symbols`). Only a symbol
with no usable upstream equivalent stays in the custom fallback source; it is drawn
from Material Symbols keylines and proportions.

| Token | Value | Meaning |
|---|---|---|
| `icon.grid` | `24` | Every glyph is authored on a 24×24 `viewBox` |
| `icon.liveArea` | `20` | Icon content stays within a centred 20×20 box |
| `icon.padding` | `2` | 2 dp clear space on every edge |
| `icon.keyline.square` | `18` | Square shapes (e.g. `stop`) |
| `icon.keyline.circle` | `20` | Round shapes (e.g. `info`, `run`) |
| `icon.keyline.verticalRect` | `16 × 20` | Portrait shapes (e.g. `file`, `phone`) |
| `icon.keyline.horizontalRect` | `20 × 16` | Landscape shapes (e.g. `computer`) |
| `icon.strokeEquivalent` | `2` | Nominal stroke / bar weight |
| `icon.cornerRadius.outer` | `2` | Outer corner rounding |
| `icon.cornerRadius.inner` | `1` | Inner corner rounding |
| `icon.opticalWeight` | `300` | Material Symbols variable-font weight |
| `icon.grade` | `0` | Material Symbols grade |
| `icon.opticalSize` | `24` | Material Symbols optical size |

Glyphs are extracted as **filled geometric paths**. No stroke approximation,
font substitution, gradient, or embedded raster is used.

The current library is a **core set of 145 official Google outlines**. The maps compose and alias
those primitives to the full required icon-name lists — e.g. `text-x-python`,
`text-x-rust` and `application-javascript` all resolve to the `file-code`
primitive, tinted per language. Refresh upstream paths with
`scripts/lib/import_material_symbols.py`; add a local path only when no official
symbol can represent the concept.

---

## 2. Colour

Icons are monochrome — they inherit one colour per context.

### VS Code file icons — `icon.fileIcon`

Chosen to stay legible on both the dark (`#161b22`) and light (`#f6f8fa`)
Explorer.

| Role | Hex | Typical use |
|---|---|---|
| `cyan` | `#22c3d6` | css, jsx, go, config |
| `rose` | `#f0509a` | scss/sass, fonts, yaml |
| `blue` | `#589bf0` | ts/tsx, python, c, docs |
| `green` | `#3fb950` | shell, csv, certs, C# |
| `amber` | `#d9a441` | js, json, images, archives |
| `red` | `#f2585b` | html, java, ruby, pdf |
| `violet` | `#a684f5` | php, kotlin, haskell, wasm |
| `slate` | `#8b949e` | `icon.fileIcon.default` — unknown / plain |

Folders use the accent: `icon.fileIcon.folder` (`#00f2fe` dark / `#0969da`
light), open folders `icon.fileIcon.folderOpen` (`#79c0ff` / `#0550ae`). The
generated theme carries a `light` block that swaps the folder colours.

### XDG icon theme — `icon.xdg.categoryColor`

| Category | Colour | |
|---|---|---|
| `apps`, `categories`, `places` | `#00f2fe` | accent — the "navigation" surfaces |
| `actions`, `devices`, `mimetypes`, `status` | `#8b949e` | neutral slate |
| `emblems` | `#ff2a85` | `icon.xdg.emblemColor` — identity/rose |

---

## 3. VS Code — file icon theme

`osiris-file-icons` (label **Osiris File Icons**). Generated to
`vscode/fileicons/`:

- `osiris-file-icons.json` — `iconDefinitions` + `file`, `folder`,
  `folderExpanded`, `rootFolder`, `rootFolderExpanded`, `fileExtensions`
  (~155), `fileNames` (~48), `folderNames`, `folderNamesExpanded`, `languageIds`,
  and a `light` override block.
- `icons/*.svg` — one baked-colour SVG per definition.

Associations live in [`iconography/map/filetypes.json`](../iconography/map/filetypes.json).

## 4. VS Code — product icon theme

`osiris-product-icons` (label **Osiris Product Icons**). Generated to
`vscode/producticons/`:

- `osiris-symbols.woff` — icon font built by **fantasticon** from the
  product-icon subset of the glyph source (99 glyphs covering 660 identifiers).
- `osiris-product-icons.json` — `fonts` + `iconDefinitions` mapping 660
  product-icon identifiers (Activity Bar, status bar, editor, panel, SCM, debug,
  test, search, notifications, symbols …) to font characters. Identifiers not
  listed fall back to the built-in Codicon.

Mapping lives in [`iconography/map/producticons.json`](../iconography/map/producticons.json).

## 5. Linux — XDG icon theme

Theme id **Osiris** (`icon.xdg.themeName`), `Inherits=Adwaita,breeze,gnome,hicolor`
so anything unstyled falls through to the platform default. Generated to
`build/icons/Osiris/`.

### Structure (freedesktop Icon Theme spec)

```
Osiris/
├── index.theme                       # [Icon Theme] + one section per directory
├── scalable/<context>/*.svg          # the vector master — Type=Scalable, 8–512
└── <size>x<size>/<context>/*.svg     # 16, 24, 32, 48, 64, 128 — Type=Threshold
```

`<context>` is every mandatory category, none omitted:
`actions/ apps/ categories/ devices/ emblems/ mimetypes/ places/ status/`.

It is an **all-vector** theme: the fixed-size directories carry the same SVG as a
relative symlink into `scalable/`, so GNOME and KDE render crisply at any scale.
`OSIRIS_ICON_RASTER=1 make icons` renders real PNGs into the size directories
instead (needs `rsvg-convert`).

### GNOME ↔ KDE compatibility

Every canonical name in [`iconography/map/xdg.json`](../iconography/map/xdg.json)
`icons` is a real file; every name in `aliases` is a **same-directory relative
symlink** to its target. Aliases cover:

- legacy GTK stock ids — `gtk-add` → `list-add`, `gtk-save` → `document-save`, …
- GNOME↔KDE app-id spellings — `org.kde.dolphin` / `nautilus` →
  `system-file-manager`, `konsole` / `gnome-terminal` → `utilities-terminal`, …
- NetworkManager / battery / status spellings — `nm-signal-100` →
  `network-wireless-signal-excellent`, …
- MIME fallbacks — `text-x-python`, `text-rust`, `application-typescript` →
  `text-x-source`; `application-vnd.rar` → `application-x-7z-compressed`; …

~380 icons + ~310 aliases per build.

---

## 6. Adding an icon

1. Find an official Material Symbol and add its alias to `material_map.json`.
   Run `scripts/lib/import_material_symbols.py` against the pinned official font.
   Only if no upstream symbol exists, add a fallback to `glyphs.json`, matching
   the Rounded 300 keylines and proportions.
2. Reference it from the relevant map(s):
   `filetypes.json` (VS Code files), `producticons.json` (VS Code product),
   `xdg.json → icons`/`aliases` (Linux).
3. `make tokens` — must pass (validates every reference resolves).
4. `make icons vscode` — regenerates all three themes.

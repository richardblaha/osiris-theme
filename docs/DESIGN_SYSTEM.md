# OSIRIS Design System

The canonical description of the OSIRIS visual language. Every theme in this
repository — VS Code, GTK 3/4, libadwaita, GNOME Shell, KDE Plasma, Qt/Kvantum,
Aurorae, GRUB2, and the wallpapers — is derived from the tokens defined here.

- **Machine-readable source of truth:** [`assets/tokens.json`](../assets/tokens.json)
- **Interactive reference:** [`docs/preview/index.html`](./preview/index.html)
  (published to GitHub Pages). The preview page is a full VS Code window mock-up —
  activity bar, side bar (Explorer / Search / SCM / Run / Extensions), editor with
  IntelliSense, a Settings tab exercising every form control, command palette,
  toasts, find widget, panel and status bar. Treat its rendered pixels as the
  acceptance test for all downstream themes.

`scripts/check-tokens.sh` fails CI if this document and `assets/tokens.json`
disagree on any hex value.

---

## 1. Brand

OSIRIS is a **dual-accent** system: a **cyan** primary and a **magenta/rose**
secondary, riding on a near-black (dark) or near-white (light) GitHub-flavoured
neutral ramp. Cyan carries affordance and focus; magenta carries identity,
activity and "the current branch of attention" (active tab border, badges,
keyword syntax, progress).

| Role | Dark | Light |
|---|---|---|
| Accent · primary (cyan) | `#00f2fe` | `#0969da` |
| Accent · primary soft | `rgba(0,242,254,0.14)` | `rgba(9,105,218,0.10)` |
| Accent · secondary (rose) | `#ff2a85` | `#e01a76` |
| Accent · secondary soft | `rgba(255,42,133,0.14)` | `rgba(224,26,118,0.10)` |

> Relationship to `@osiris/branding` in the main IDE repo: that package uses the
> pure-hue legacy pair `#00FFFF` / `#FF00FF` on `#121212`. `osiris-themes`
> supersedes it with the toned pair above (softer on the eyes, AA-contrast
> verified) and the `#0d1117 / #161b22` neutral ramp. New builds should consume
> `osiris-themes`; the legacy values remain only for backwards compatibility.

---

## 2. Neutral ramp & surfaces

| Token | Dark | Light | Used for |
|---|---|---|---|
| `bg.titlebar` | `#0d1117` | `#ffffff` | Title bar, window chrome |
| `bg.activitybar` | `#0d1117` | `#f6f8fa` | Activity bar / GNOME panel / Plasma panel |
| `bg.sidebar` | `#161b22` | `#f6f8fa` | Side bar, dash, tray popups, dialogs |
| `bg.editor` | `#0d1117` | `#ffffff` | Editor / document / app content area |
| `bg.tabInactive` | `#161b22` | `#eaeef2` | Inactive tabs, header strips |
| `bg.panel` | `#161b22` | `#f6f8fa` | Bottom panel, terminal chrome |
| `bg.hover` | `#21262d` | `#eaeef2` | Hover state on rows, buttons, list items |
| `bg.selection` | `#21262d` | `#dde7f3` | Text/row selection background |
| `bg.input` | `#21262d` | `#ffffff` | Text inputs, dropdowns, textareas |
| `border.subtle` | `#21262d` | `#eaeef2` | Hairline separators between regions |
| `border.strong` | `#30363d` | `#d0d7de` | Input borders, popovers, cards |
| `scrollbar` | `#30363d` | `#d0d7de` | Scrollbar thumb |

The status bar is a **solid accent bar**: cyan `#00f2fe` on `#04151a` text
(dark), blue `#0969da` on `#ffffff` (light). This is the single most recognisable
OSIRIS signature — keep it in every shell (GNOME top bar accent, Plasma
active-task underline, GRUB progress bar).

---

## 3. Text

| Token | Dark | Light |
|---|---|---|
| `text.primary` | `#e6edf3` | `#1f2328` |
| `text.secondary` | `#8b949e` | `#57606a` |
| `text.muted` | `#565f6d` | `#8c959f` |
| `text.inverse` | `#04151a` | `#ffffff` |

Body / UI copy: `text.primary`. Section headers, captions, breadcrumbs:
`text.secondary`. Disabled, line numbers, placeholder: `text.muted`. Text on an
accent fill: `text.inverse`.

---

## 4. Syntax (editor tokens)

| Token scope | Dark | Light | TextMate scopes |
|---|---|---|---|
| comment | `#565f6d` *(italic)* | `#8c959f` *(italic)* | `comment`, `punctuation.definition.comment` |
| string | `#a5d6ff` | `#0a3069` | `string`, `constant.other.symbol` |
| keyword | `#ff2a85` | `#e01a76` | `keyword`, `storage.type`, `storage.modifier` |
| function | `#00f2fe` | `#0969da` | `entity.name.function`, `support.function` |
| type | `#79c0ff` | `#953800` | `entity.name.type`, `entity.name.class`, `support.type` |
| number | `#d29922` | `#0550ae` | `constant.numeric`, `constant.language` |
| punctuation | `#8b949e` | `#57606a` | `punctuation`, `meta.brace` |
| variable | `#e6edf3` | `#1f2328` | `variable`, `meta.definition.variable` |
| property | `#ffa198` | `#cf222e` | `variable.other.property`, `support.type.property-name`, `entity.other.attribute-name` |

---

## 5. Semantic / status colours

| Role | Dark | Light | Surfaces |
|---|---|---|---|
| info | `#00f2fe` | `#0969da` | info toast border, `editorInfo` |
| success | `#3fb950` | `#1a7f37` | test pass, `git add` (`A` flag), terminal ✓ |
| warning | `#d29922` | `#9a6700` | warn toast, `editorWarning`, `git` untracked (`U` flag) |
| error | `#ff5555` | `#cf222e` | error toast, `editorError`, problems panel |

Git decoration mapping (from the preview Explorer): **M**odified → accent
secondary, **U**ntracked → warning, **A**dded → success.

---

## 6. Shape, elevation, motion

| Token | Value | Notes |
|---|---|---|
| `radius.sm` | `3px` | inputs, buttons, list rows, tags, chips |
| `radius.md` | `6px` | cards, popovers, command palette, toasts, window corners |
| `radius.pill` | `999px` | toggles, segmented controls, debug toolbar |
| `shadow.window` | `0 30px 80px -20px rgba(0,0,0,.65), 0 8px 24px -8px rgba(0,0,0,.5)` | floating window / decorated frame |
| `shadow.popup` | `0 16px 40px rgba(0,0,0,.5)` | menus, IntelliSense, palette |
| transition | `.15s ease` | color / background / transform on hover & focus |

**Focus ring:** 3px accent-primary-soft outer glow + 1px `accent.primary` border
(`box-shadow: 0 0 0 3px var(--accent-primary-soft); border-color: var(--accent-primary)`).
Applies to every focusable control across every toolkit.

**Active-item indicator:** a 2px bar in `accent.primary` (activity bar left edge,
active tab top edge uses `accent.secondary`; panel tab bottom edge uses
`accent.primary`).

---

## 7. Component contract (from the preview page)

| Component | Rest | Hover | Focus / active | Disabled |
|---|---|---|---|---|
| Button (primary) | fill `accent.primary`, text `text.inverse`, `radius.sm` | lighten fill ~8% | focus ring | 40% opacity |
| Button (secondary) | fill `bg.input`, 1px `border.strong` | bg `bg.hover` | focus ring | 40% opacity |
| Text / number input | bg `bg.input`, 1px `border.strong`, `radius.sm` | border `border.strong` | focus ring | muted text |
| Select / dropdown | as input + chevron in `text.secondary` | — | focus ring | — |
| Checkbox / radio | `accent.primary` accent-color, 15px | — | focus ring | — |
| Toggle switch | track `border.strong`; thumb `text.primary` | — | checked: track `accent.primary`, thumb `text.inverse`, 16px travel | — |
| Range slider | track 4px, `accent.primary` accent-color | — | focus ring on thumb | — |
| Tab (editor) | bg `bg.tabInactive`, text `text.secondary` | `bg.hover` | bg `bg.tabActive`, text `text.primary`, 2px `accent.primary` top bar | — |
| List row | transparent | `bg.hover` | `accent.primary` soft bg | — |
| Badge / count | fill `accent.secondary` (activity) or `bg.hover` (panel tab), `radius.pill` | — | — | — |
| Toast | bg `bg.sidebar`, 1px `border.strong`, 3px left border in the status colour, `radius.sm`, `shadow.popup` | — | — | — |
| Command palette | box `bg.sidebar`, 1px `border.strong`, `radius.md`, `shadow.popup`; active row `accent.primary` soft | — | — | — |
| Dialog / modal backdrop | `rgba(3,6,10,0.55)` | — | — | — |

---

## 8. Typography

- **Monospace (code, terminal, GRUB):** Fira Code with ligatures on.
  `Fira Code, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`.
- **UI (shell, dialogs):** `Inter, -apple-system, "Segoe UI", Ubuntu, sans-serif`.
- Section header casing: `UPPERCASE`, `letter-spacing: 0.08em`, `font-weight: 600`,
  `font-size: 11px`, colour `text.secondary`.
- Code: `13px / 21px`. UI body: `12.5–13px`. Captions: `11–11.5px`.

---

## 9. Wallpaper palettes

See `assets/tokens.json → wallpaper`. Two families, each with a fixed **Day
(Light)** and **Night (Dark)** render plus a dynamic time-of-day transition
(GNOME `*.xml`, KDE `metadata.json` / `*.json`).

- **Abstract (Bloom / Fluid):** layered translucent curves, Fluent-style depth,
  cyan↔rose gradient wash over the neutral base.
- **Egypt (Ancient Egypt Sci-Fi):** minimalist vector Djed pillar, scarab,
  pyramid silhouette and hieroglyph strip, lit by a single accent rim light.

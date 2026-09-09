# Manuál ikonografie OSIRIS

Ikonografie OSIRIS představuje jednotný vizuální systém pro všechny ikony v ekosystému – od souborových a produktových ikon ve VS Code až po systémové ikony na Linuxovém desktopu (standard XDG / FreeDesktop).

Veškeré ikony jsou generovány z jediného centrálního repozitáře glyfů [`iconography/glyphs.json`](https://github.com/richardblaha/osiris-theme/blob/main/iconography/glyphs.json) pomocí generátoru `scripts/lib/gen_icons.py`.

---

## 1. Designový jazyk: Papirus Icon Theme

Všechny ikony vycházejí z geometrie a proporcí moderního ikonového tématu **[Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)**:
- **Mřížka:** `24×24`
- **Geometrie:** Čisté ploché geometrické tvary s minimálním zaoblením rohů (`1px` vnější / `0px` vnitřní).
- **Typ:** Vyplněné geometrické cesty (filled paths).

```text
┌───────────────────────────────┐  24×24 viewBox
│         2px padding           │
│    ┌─────────────────────┐    │
│    │                     │    │
│    │     20×20 LIVE      │    │  Aktivní kreslicí plocha
│    │        AREA         │    │
│    │                     │    │
│    └─────────────────────┘    │
│         2px padding           │
└───────────────────────────────┘
```

### Geometrické konstanty a vodicí linky (Keylines):

| Token | Hodnota | Význam a konstrukční pravidlo |
|---|---|---|
| `icon.grid` | `24` | Každý glyf je konstruován v mřížce 24×24 jednotek |
| `icon.liveArea` | `20` | Obsah ikony zůstává uvnitř vystředěného čtverce 20×20 |
| `icon.padding` | `2` | Bezpečnostní okraj 2 jednotky od každého okraje |
| `icon.keyline.square` | `18 × 18` | Vodicí čtverec pro čtvercové tvary (např. ikona `stop`) |
| `icon.keyline.circle` | `20 (ø)` | Vodicí kružnice pro kulaté tvary (např. `info`, `run`) |
| `icon.keyline.verticalRect` | `16 × 20` | Vertikální obdélník (ikony dokumentů, souborů, telefonů) |
| `icon.keyline.horizontalRect`| `20 × 16` | Horizontální obdélník (disky, okna, monitory) |
| `icon.strokeEquivalent` | `2` | Ekvivalentní tloušťka tahů a čar |
| `icon.cornerRadius.outer`| `1` | Vnější zaoblení rohů |
| `icon.cornerRadius.inner`| `0` | Vnitřní zaoblení rohů |

> [!IMPORTANT]
> **Pravidlo čistých cest:** Glyfy musí být tvořeny čistým `<path fill="currentColor">`. Žádné otevřené tahy (`stroke`), žádné přechody (`linearGradient`) ani bitmapové obrázky. Pro tvary s otvory se používá `fill-rule="evenodd"`.

---

## 2. Barevný systém pro souborové ikony (VS Code File Icons)

Souborové ikony v průzkumníku projektu jsou barevně kódovány podle typu technologie a přípony souboru. Barvy jsou pečlivě vyladěny tak, aby byly skvěle čitelné na tmavém (`#161b22`) i světlém (`#f6f8fa`) pozadí:

| Role / Barva | Hex hodnota | Typické technologie a přípony |
|---|---|---|
| **Cyan** | `#22c3d6` | CSS, JSX, Go, konfigurace (`.conf`, `.ini`, `.env`) |
| **Rose** | `#f0509a` | SCSS, SASS, fonty, YAML (`.yml`, `.yaml`) |
| **Blue** | `#589bf0` | TypeScript (`.ts`, `.tsx`), Python, C/C++, dokumentace |
| **Green** | `#3fb950` | Shell skripty (`.sh`, `.bash`), CSV, certifikáty, C# |
| **Amber** | `#d9a441` | JavaScript (`.js`, `.mjs`), JSON, obrázky, archivy (`.zip`, `.tar`) |
| **Red** | `#f2585b` | HTML, Java, Ruby, PDF dokumenty |
| **Violet**| `#a684f5` | PHP, Kotlin, Haskell, WebAssembly (`.wasm`) |
| **Slate** | `#8b949e` | Výchozí neutrální ikona pro neznámé nebo prosté textové soubory |

### Složky (Folders):
- **Zavřená složka:** `icon.fileIcon.folder` &rarr; `#00f2fe` (Dark) / `#0969da` (Light).
- **Otevřená složka:** `icon.fileIcon.folderOpen` &rarr; `#79c0ff` (Dark) / `#0550ae` (Light).

---

## 3. Systémové ikony pro Linux (XDG FreeDesktop Theme)

Systémová sada `Osiris` pro Linuxová desktopová prostředí rozděluje ikony do kategorií s přesně určenou sémantikou:

| Kategorie XDG | Barva | Význam |
|---|---|---|
| `apps`, `categories`, `places` | `#00f2fe` *(Cyan)* | Navigační a aplikační ikony (Spouštěče aplikací, Místa, Domovská složka) |
| `actions`, `devices`, `mimetypes`, `status` | `#8b949e` *(Slate)* | Nástroje, hardware, systémové stavy a obecné typy souborů |
| `emblems` | `#ff2a85` *(Rose)* | Systémové odznaky, pečetě, oblíbené položky a varovné znaky |

---

## 4. Produktové ikony (VS Code Product Icons)

Ikony pro ovládací prvky VS Code (lupa, git větev, ozubené kolo nastavení, debug tlačítka) jsou kompilovány do speciálního webového fontu:
- **Identifikátor fontu:** `osiris-symbols` (`vscode/producticons/osiris-symbols.woff`).
- **Nástroj:** Kompilováno pomocí nástroje `fantasticon`.
- **Počáteční rozsah Unicode:** `0xE000`.
- **Mapování:** Definováno v [`iconography/map/producticons.json`](https://github.com/richardblaha/osiris-theme/blob/main/iconography/map/producticons.json).


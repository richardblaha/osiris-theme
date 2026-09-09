# Barevná paleta a designové tokeny

Barevný systém OSIRIS je navržen jako **přísně hierarchický, tokenizovaný systém** s certifikovaným kontrastem podle specifikace WCAG AA. Všechny odstíny jsou definovány v jediném zdrojovém souboru [`assets/tokens.json`](https://github.com/richardblaha/osiris-theme/blob/main/assets/tokens.json) a kontrolovány automatickým CI testem (`scripts/check-tokens.sh`).

---

## 1. Koncepce Dual-Accent

OSIRIS využívá dva klíčové akcenty:
- **Primární akcent (Cyan):** Nese interaktivitu, aktivní fokus, primární akce, kurzor a stavové informace.
- **Sekundární akcent (Rose / Magenta):** Nese identitu značky, pozornost, indikátory změn (Git Modified), odznaky (badges) a klíčová slova syntaxe.

| Role | Token | Tmavý režim (Dark) | Světlý režim (Light) | Funkce v UI |
|---|---|---|---|---|
| **Accent · primary** | `accent.primary` | `#00f2fe` | `#0969da` | Hlavní tlačítka, fokus, aktivní prvek, odkazy |
| **Accent · primary soft** | `accent.primarySoft` | `rgba(0,242,254,0.14)` | `rgba(9,105,218,0.10)` | Vnější záře Focus Ringu, hover nad výběry |
| **Accent · secondary** | `accent.secondary` | `#ff2a85` | `#e01a76` | Horní linka aktivního tabu, odznaky, badge počitadla |
| **Accent · secondary soft**| `accent.secondarySoft` | `rgba(255,42,133,0.14)` | `rgba(224,26,118,0.10)` | Podkresy důležitých notifikací, alerty |

---

## 2. Podpisový prvek: Solid Accent Status Bar

Nejvýraznějším identifikačním znakem tématu OSIRIS napříč všemi platformami je **plně akcentovaný stavový řádek**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│                      HLAVNÍ PRACOVNÍ PLOCHA / EDITOR                   │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ [main*]  Ln 42, Col 12    UTF-8    JSON    OSIRIS STATUS BAR (SOLID)   │
└────────────────────────────────────────────────────────────────────────┘
  ▲ Plná akcentová výplň (Cyan #00f2fe dark / Blue #0969da light)
```

- **Tmavý režim:** Plná výplň Cyan `#00f2fe` s tmavým textem `text.inverse` (`#04151a`).
- **Světlý režim:** Plná výplň Deep Blue `#0969da` s bílým textem `text.inverse` (`#ffffff`).
- **Implementace na desktopu:** Stejný princip se promítá do horní lišty GNOME Shell, podtržení aktivní úlohy v KDE Plasma a progress baru v GRUB2.

---

## 3. Neutrální rampa a povrchy (Surfaces)

Neutrální stupnice vychází z prověřené GitHub palety s optimalizací pro hloubku a vrstvení oken:

| Token | Tmavý režim | Světlý režim | Použití v rozhraní |
|---|---|---|---|
| `bg.titlebar` | `#0d1117` | `#ffffff` | Záhlaví okna, titlebar |
| `bg.activitybar`| `#0d1117` | `#f6f8fa` | Postranní pruh ikon, systémový panel |
| `bg.sidebar` | `#161b22` | `#f6f8fa` | Průzkumník souborů, strom projektu, dialogy |
| `bg.editor` | `#0d1117` | `#ffffff` | Hlavní tělo editoru, plocha dokumentu |
| `bg.tabInactive`| `#161b22` | `#eaeef2` | Neaktivní záložky, pásy záhlaví |
| `bg.tabActive` | `#0d1117` | `#ffffff` | Aktivní otevřená záložka |
| `bg.panel` | `#161b22` | `#f6f8fa` | Spodní panel, konzole, terminál |
| `bg.hover` | `#21262d` | `#eaeef2` | Hover stav tlačítek, položek menu a řádků |
| `bg.selection` | `#21262d` | `#dde7f3` | Zvýraznění označeného textu nebo řádku |
| `bg.input` | `#21262d` | `#ffffff` | Vstupní pole, formuláře, dropdowny |
| `border.subtle`| `#21262d` | `#eaeef2` | Jemné oddělovače zón a panelů |
| `border.strong`| `#30363d` | `#d0d7de` | Okraje vstupů, karet, vyskakovacích oken |
| `scrollbar` | `#30363d` | `#d0d7de` | Táhlo posuvníku (scrollbar thumb) |

---

## 4. Typografická hierarchie barev

| Token | Tmavý režim | Světlý režim | Význam a použití |
|---|---|---|---|
| `text.primary` | `#e6edf3` | `#1f2328` | Hlavní text, kód, aktivní popisky |
| `text.secondary`| `#8b949e` | `#57606a` | Záhlaví sekcí, drobné popisky, breadcrumbs |
| `text.muted` | `#565f6d` | `#8c959f` | Čísla řádků, neaktivní prvky, placeholdery |
| `text.inverse` | `#04151a` | `#ffffff` | Text na akcentové výplni (Status Bar, primární tlačítka) |

---

## 5. Sémantické a stavové barvy

Sémantické barvy indikují stavy systému, výsledky operací a stav verzování Git:

| Role | Tmavý režim | Světlý režim | Použití v UI & Git |
|---|---|---|---|
| **Info** | `#00f2fe` | `#0969da` | Informační hlášení, modré ikony, diagnostika |
| **Success** | `#3fb950` | `#1a7f37` | Úspěch, testy OK, Git **A**dded (nový soubor) |
| **Warning** | `#d29922` | `#9a6700` | Varování, Git **U**ntracked (nesledovaný soubor) |
| **Error** | `#ff5555` | `#cf222e` | Chyba, selhání testu, chybové toast zprávy |

> **Git mapování:**  
> - **M**odified (změněno) &rarr; `accent.secondary` (`#ff2a85` / `#e01a76`)  
> - **U**ntracked (nové) &rarr; `warning` (`#d29922` / `#9a6700`)  
> - **A**dded (připraveno k commitu) &rarr; `success` (`#3fb950` / `#1a7f37`)  

---

## 6. Syntax Highlighting (Editor kódu)

Pravidla pro zvýrazňování syntaxe v editorech a na webu:

| Prvek syntaxe | Tmavý režim | Světlý režim | TextMate scopes |
|---|---|---|---|
| **Komentáře** | `#565f6d` *(kurzíva)* | `#8c959f` *(kurzíva)* | `comment`, `punctuation.definition.comment` |
| **Řetězce (Strings)** | `#a5d6ff` | `#0a3069` | `string`, `constant.other.symbol` |
| **Klíčová slova** | `#ff2a85` *(Rose)* | `#e01a76` *(Rose)* | `keyword`, `storage.type`, `storage.modifier` |
| **Funkce a metody** | `#00f2fe` *(Cyan)* | `#0969da` *(Blue)* | `entity.name.function`, `support.function` |
| **Typy a třídy** | `#79c0ff` | `#953800` | `entity.name.type`, `entity.name.class`, `support.type` |
| **Čísla a konstanty** | `#d29922` | `#0550ae` | `constant.numeric`, `constant.language` |
| **Interpunkce** | `#8b949e` | `#57606a` | `punctuation`, `meta.brace` |
| **Proměnné** | `#e6edf3` | `#1f2328` | `variable`, `meta.definition.variable` |
| **Vlastnosti (Properties)**| `#ffa198` | `#cf222e` | `variable.other.property`, `support.type.property-name` |

---

## 7. Terminálová paleta (ANSI 16 barev)

Pro systémové terminály (GNOME Terminal, Ptyxis, Konsole) generuje skript `scripts/lib/gen_terminal.py` totožné mapování:

| Index | Název ANSI | Tmavý režim | Světlý režim |
|---|---|---|---|
| 0 | Black | `#0d1117` | `#ffffff` |
| 1 | Red | `#ff5555` | `#cf222e` |
| 2 | Green | `#3fb950` | `#1a7f37` |
| 3 | Yellow | `#d29922` | `#9a6700` |
| 4 | Blue | `#58a6ff` | `#0969da` |
| 5 | Magenta | `#ff2a85` | `#e01a76` |
| 6 | Cyan | `#00f2fe` | `#0969da` |
| 7 | White | `#e6edf3` | `#1f2328` |
| 8-15 | Jasné varianty (Bright) | Lehce saturované a prosvětlené verze pro vysokou čitelnost v konzoli |


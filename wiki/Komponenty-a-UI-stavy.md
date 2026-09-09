# Komponenty, tvarosloví a UI stavy

Vizuální jazyk OSIRIS definuje přísný geometrický a stavový kontrakt pro všechny prvky uživatelského rozhraní. Ať už jde o webovou aplikaci, VS Code, GTK okno nebo dialog v KDE Plasma, komponenty se musí chovat a vypadat identicky.

---

## 1. Geometrie a rádiusy zaoblení (Radius tokens)

OSIRIS používá umírněné, technické zaoblení rohů, které působí moderně, ale zachovává pevnou mřížku:

| Token | Hodnota | Použití v rozhraní |
|---|---|---|
| `radius.sm` | `2 px` | Tlačítka, vstupní pole, řádky seznamů, štítky, chips, taby |
| `radius.md` | `2 px` | Karty, vyskakovací okna (popovers), dialogy, notifikace, rohy oken |
| `radius.pill` | `2 px` | Přepínače (toggles), segmentované přepínače, vyhledávací lišty, odznaky (badges) |

---

## 2. Elevace, hloubka a stíny (Elevation & Shadows)

Hloubka je vytvářena kombinací jemných 1px ohraničení (`border.subtle` a `border.strong`) a vícevrstvých stínů:

```css
/* Plovoucí hlavní okno aplikace */
--shadow-window: 0 30px 80px -20px rgba(0, 0, 0, 0.65), 0 8px 24px -8px rgba(0, 0, 0, 0.5);

/* Vyskakovací menu, IntelliSense, Command Palette */
--shadow-popup: 0 16px 40px rgba(0, 0, 0, 0.5);

/* Standardní přechodová animace */
--transition-default: 0.15s ease;
```

---

## 3. Podpisový prvek: Standardizovaný Focus Ring

Každý aktivní prvek ovládaný klávesnicí nebo myší používá jednotný **OSIRIS Focus Ring**. Skládá se z 1px vnitřního ohraničení v barvě primárního akcentu a 3px vnější jemné záře:

```css
:focus-visible {
  outline: none;
  border-color: var(--accent-primary) !important;
  box-shadow: 0 0 0 3px var(--accent-primary-soft) !important;
}
```

```text
┌───────────────────────────────────────┐ ◄── 3px vnější záře (accent.primarySoft)
│  ┌─────────────────────────────────┐  │ ◄── 1px linka (accent.primary)
│  │         AKTIVNÍ VSTUP           │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
```

---

## 4. Indikátory aktivního stavu (Active Indicators)

- **Postranní lišta (Activity Bar):** Svislý 2px pruh v barvě `accent.primary` na levém okraji aktivní ikony.
- **Záložky editoru (Editor Tabs):** Vodorovný 2px pruh v barvě **`accent.secondary` (Rose)** na horním okraji aktivní záložky. To je klíčový moment, kde se uplatňuje sekundární akcent jako "aktuální ohnisko pozornosti".
- **Spodní panely (Panel Tabs):** Vodorovný 2px pruh v barvě `accent.primary` na spodním okraji aktivní záložky.

---

## 5. Kontrakt jednotlivých komponent

Přehled chování a stylů komponent v jednotlivých stavech:

| Komponenta | Výchozí stav (Rest) | Najetí myší (Hover) | Aktivní / Fokus | Neaktivní (Disabled) |
|---|---|---|---|---|
| **Primární tlačítko** | Výplň `accent.primary`, text `text.inverse`, zaoblení `radius.sm` | Zesvětlení výplně o ~8 % | Focus Ring, mírné stlačení | Opacita 40 %, kurzor `not-allowed` |
| **Sekundární tlačítko**| Pozadí `bg.input`, 1px rámeček `border.strong` | Pozadí `bg.hover` | Focus Ring | Opacita 40 % |
| **Textové pole (Input)**| Pozadí `bg.input`, 1px rámeček `border.strong`, text `text.primary` | Rámeček `border.strong` | Focus Ring, pozadí `bg.input` | Text `text.muted`, rámeček `border.subtle` |
| **Výběrové pole (Select)**| Stejné jako Input + šipka chevron v barvě `text.secondary` | Zvýraznění chevronu | Focus Ring | Opacita 50 % |
| **Zaškrtávací pole (Checkbox)**| Rámeček `border.strong`, zaškrtnuto: `accent.primary` výplň | Jemný akcentový okraj | Focus Ring | Opacita 40 % |
| **Přepínač (Toggle Switch)**| Dráha `border.strong`, jezdec `text.primary`, zaoblení `radius.pill` | — | Zapnuto: dráha `accent.primary`, jezdec `text.inverse`, posun 16 px | Opacita 40 % |
| **Záložka editoru (Tab)**| Pozadí `bg.tabInactive`, text `text.secondary` | Pozadí `bg.hover` | Pozadí `bg.tabActive`, text `text.primary`, 2px horní pruh `accent.secondary` | — |
| **Řádek v seznamu** | Transparentní pozadí | Pozadí `bg.hover` | Pozadí `accent.primarySoft`, text `text.primary` | — |
| **Odznak (Badge / Count)**| Výplň `accent.secondary` (notifikace) nebo `bg.hover` (panely), zaoblení `radius.pill` | — | — | — |
| **Toast notifikace** | Pozadí `bg.sidebar`, 1px rámeček `border.strong`, 3px levý svislý pruh v sémantické barvě stavu, stín `shadow.popup` | — | — | — |
| **Command Palette** | Okno `bg.sidebar`, rámeček `border.strong`, stín `shadow.popup`, aktivní řádek `accent.primarySoft` | — | Focus na vyhledávacím poli | — |
| **Modální pozadí** | `rgba(3, 6, 10, 0.55)` (poloprůhledná tlumící vrstva) | — | — | — |


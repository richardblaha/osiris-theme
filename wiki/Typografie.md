# Typografický manuál OSIRIS

Typografie systému OSIRIS je radikální, moderní a zcela jednotná: **celé prostředí používá jediné písmo – Fira Code s aktivními ligaturami**. 

Písmo se nepoužívá pouze v editoru pro zdrojový kód, ale důsledně také pro veškeré prvky uživatelského rozhraní (UI chrome), záhlaví oken, menu, systémové lišty i bootovací nabídku GRUB2.

---

## 1. Oficiální písmo: Fira Code

Fira Code je neproporcionální písmo (monospace) navržené speciálně pro programátory Nikitou Prokopovem. Obsahuje sadu programátorských ligatur (spojování symbolů jako `=>`, `!=`, `===`, `<!--` atd.), které zvyšují rychlost čtení a vizuální eleganci.

<div align="center">

```text
  0123456789  ABCDEFGHIJKLMN  abcdefghijklmn
  !=  ==  ===  <=  >=  =>  ->  <-  </>  &&  ||
```
*Ukázka neproporcionální mřížky a programátorských ligatur Fira Code.*

</div>

### Rodiny a licenční podmínky:
- **Licence:** SIL Open Font License 1.1 (svobodné písmo).
- **Lokalizace v repozitáři:** `assets/fonts/fira-code/` (obsahuje jak variabilní font `FiraCode-VariableFont_wght.ttf`, tak statické řezy Regular, Medium, SemiBold, Bold, Retina).

---

## 2. Písomové sady (Font Stacks)

Pro web, GTK, CSS a aplikace jsou definovány tyto závazné sady fontů:

### Mono stack (Editor kódu a terminál):
```css
font-family: "Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
```

### UI stack (Uživatelské rozhraní, tlačítka, nabídky):
```css
font-family: "Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, -apple-system, "Segoe UI", Ubuntu, sans-serif;
```
> [!NOTE]
> Proporcionální fonty na konci UI stacku (`-apple-system`, `Segoe UI`, `Ubuntu`) slouží **výhradně jako bezpečnostní fallback** pro glyfy, které Fira Code neobsahuje (např. CJK znaky, specifické emoji a exotická písma).

### Zapnutí ligatur v CSS:
```css
font-variant-ligatures: normal;
font-feature-settings: "liga" 1, "calt" 1;
```

---

## 3. Typografická škála (Type Scale)

| Úroveň / Prvek | Velikost | Řádkování (Line-height) | Váha (Weight) | Barva |
|---|---|---|---|---|
| **Záhlaví okna (Titlebar)** | `12 px` | `1.2` | Regular (400) | `text.secondary` |
| **Záhlaví sekcí (Section Header)** | `11 px` | `1.4` | SemiBold (600) | `text.secondary` |
| **UI Body / Tlačítka / Položky** | `12.5 – 13 px` | `1.4` | Regular (400) / Medium (500) | `text.primary` |
| **Kód v editoru (Code Editor)** | `13 px` | `21 px` | Regular (400) / Retina (450) | Dle syntaxe |
| **Popisky, Breadcrumbs, Meta** | `11 – 11.5 px`| `1.3` | Regular (400) | `text.secondary` |
| **Čísla řádků, placeholdery** | `12 px` | `21 px` | Regular (400) | `text.muted` |
| **Odznaky (Badges)** | `10 px` | `1.0` | SemiBold (600) | `text.inverse` |

---

## 4. Pravidla pro formátování záhlaví sekcí

Záhlaví panelů a sekcí (např. *EXPLORER*, *OUTLINE*, *TIMELINE*, *SETTINGS*) mají specifický podpisový styl:

```css
.section-header {
  font-family: var(--font-ui);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
```

- **Pouze velká písmena (`UPPERCASE`).**
- **Zvýšené prostrkání písmen (`letter-spacing: 0.08em`).**
- **SemiBold řez (600).**
- **Nenápadná sekundární barva (`text.secondary`), aby netříštila pozornost od obsahu.**

---

## 5. Nastavení v systémových prostředích

### VS Code:
Nastavuje se automaticky při instalaci rozšíření `osiris-theme`:
```json
{
  "editor.fontFamily": "'Fira Code', monospace",
  "editor.fontLigatures": true,
  "editor.fontSize": 13,
  "editor.lineHeight": 21
}
```

### KDE Plasma 6:
Prostředí Qt a KDE Plasma nemá přímý háček na tématování písma ze stylů. Nastavuje se globálně příkazem:
```bash
kwriteconfig6 --file kdeglobals --group General --key font "Fira Code,10,-1,5,50,0,0,0,0,0"
kwriteconfig6 --file kdeglobals --group General --key fixed "Fira Code,10,-1,5,50,0,0,0,0,0"
```

### GTK 3 / 4 a GNOME:
Font se instaluje do uživatelského systému do `~/.local/share/fonts/` nebo `/usr/share/fonts/` a aktivuje se přes `gsettings`:
```bash
gsettings set org.gnome.desktop.interface font-name 'Fira Code 10'
gsettings set org.gnome.desktop.interface monospace-font-name 'Fira Code 10'
```


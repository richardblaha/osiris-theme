# Tapety a vizuální aktiva

Součástí kompletní identity OSIRIS jsou oficiální systémové tapety, aplikační ikony a doplňková grafická aktiva navržená tak, aby ladila s barevným schématem a podtrhovala estetiku vývojářského prostředí.

---

## 1. Tapetové rodiny (Wallpaper Families)

Projekt obsahuje dvě samostatné rodiny tapet, z nichž každá nabízí variantu **Den (Day / Light)** a **Noc (Night / Dark)** s plynulým časovým přechodem podle denní doby.

### Rodina A: Abstract (Bloom / Fluid)
- **Vizuální styl:** Plynulé vrstvené křivky z průsvitných gradientů ve stylu moderního skla (Fluent / Glassmorphism) s přechodem ze zářivého Cyanu do Rose na hlubokém neutrálním pozadí.
- **Denní varianta (Day):** Světlý perleťový podklad s čistým vzdušným gradientem.
- **Noční varianta (Night):** Hluboké uhlíkové pozadí s výrazným neonovým luminiscenčním svitem.
- **Soubory v repozitáři:**
  - `assets/wallpapers/abstract/osiris-abstract-day.svg`
  - `assets/wallpapers/abstract/osiris-abstract-night.svg`

### Rodina B: Egypt (Ancient Egypt Sci-Fi)
- **Vizuální styl:** Minimalistická vektorová kompozice spojující starověkou egyptskou symboliku (Djed pilíř – symbol stability, posvátný scarabeus a silueta pyramid) s kybernetickou sci-fi linkou osvětlenou bočním akcentovým světlem.
- **Denní varianta (Day):** Pískovcově světlý čistý technický náčrt.
- **Noční varianta (Night):** Temná silueta pyramid a posvátných symbolů s akcentovými hranami.
- **Soubory v repozitáři:**
  - `assets/wallpapers/egypt/osiris-egypt-day.svg`
  - `assets/wallpapers/egypt/osiris-egypt-night.svg`

---

## 2. Podpora dynamických tapet na Linuxu

Skript `scripts/generate-wallpapers.py` automaticky renderuje vektorové SVG do 4K rastrů (3840 × 2160 px) a sestavuje balíčky pro:

- **GNOME Shell:** Generuje XML časovací soubory (`osiris-abstract.xml`, `osiris-egypt.xml`), které v průběhu dne automaticky plynule prolínají denní a noční tapetu podle východu a západu slunce.
- **KDE Plasma:** Generuje strukturu s `metadata.json` pro nativní přepínač tapet v nastavení plochy Plasma.
- **Umístění po instalaci:** `/usr/share/backgrounds/osiris/`

---

## 3. Aplikační ikony (App Icons)

Pro spouštěče aplikací a balíčkování (Electron, VS Code, nativní binárky) je k dispozici plná sada vygenerovaných aplikačních ikon ze souboru `assets/icons/app/`:

- **Windows:** `osiris.ico` (multi-rezoluční formát obsahující velikosti 16, 24, 32, 48, 64, 128, 256 px).
- **macOS:** `osiris.icns` (retina ikony pro macOS dock a Finder).
- **Linux:** Freedesktop standardní strom `assets/icons/app/hicolor/` (škálovatelná SVG verze i pevné rastry 16x16 až 512x512 px).
- **Web:** Favicon a sociální karty (1024x1024 px PNG).

---

## 4. Letterpress vodoznaky (Letterpress Marks)

Pro podkresy dialogů, přihlašovací obrazovky (GDM/SDDM) a technické listy slouží reliéfní letterpress značky:
- `assets/watermarks/letterpress-dark.png` (a verze `@2x` pro vysoké DPI).
- `assets/watermarks/letterpress-light.png` (a verze `@2x`).


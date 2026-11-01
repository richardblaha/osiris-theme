# Tapety a vizuální aktiva

Součástí kompletní identity OSIRIS jsou oficiální systémové tapety, aplikační ikony a doplňková grafická aktiva navržená tak, aby ladila s barevným schématem a podtrhovala estetiku vývojářského prostředí.

---

## 1. Tapetová rodina (Wallpaper Family)

Projekt obsahuje jednu rodinu tapet **Neon Sci-Fi** — 10 motivů, každý ve variantě **Dark** a **Light** (celkem 20 tapet), s plynulým časovým přechodem podle denní doby.

### Neon Sci-Fi
- **Vizuální styl:** Neonové kybernetické sci-fi motivy v cyan/magenta na neutrálním GitHub rampu — portál, horizont planety, hexagonová dlažba, vlny bodů, radar, pyramida v mlze, síť uzlů, oběžná dráha, tok čar, monolit.
- **Dark varianta:** Hluboké uhlíkové pozadí (`#0d1117`) s neonovým svitem cyan `#00f2fe` / rose `#ff2a85`.
- **Light varianta:** Světlé perleťové pozadí (`#eef2f7`) s tlumenějším akcentem `#0969da` / `#e01a76`.
- **Soubory v repozitáři:** `assets/wallpapers/neon/osiris-neon-<NN>-<motiv>-<dark|light>.png` (20 master PNG, 2560×1440)

## 2. Podpora dynamických tapet na Linuxu

Skript `scripts/generate-wallpapers.py` automaticky převede master PNG na rozlišení 2560×1440 / 1920×1080 / 1366×768 a sestavuje balíčky pro:

- **GNOME Shell:** Generuje XML časovací soubory (`osiris-neon-<motiv>-<rozlišení>.xml`), které v průběhu dne automaticky plynule prolínají light a dark variantu každého motivu podle východu a západu slunce.
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


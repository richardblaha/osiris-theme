# Architektura a export ekosystému

Základním technickým pilířem projektu OSIRIS je **jediný zdroj pravdy (Single Source of Truth)**. Žádné z témat pro desítky podporovaných nástrojů a prostředí se neupravuje ručně. Všechny výstupy jsou generovány automatickými skripty z centrálních designových tokenů.

---

## 1. Tok generování aktiv (Pipeline)

Následující diagram znázorňuje, jak se data z `assets/tokens.json` a `iconography/glyphs.json` distribuují do jednotlivých cílových platforem:

```text
assets/tokens.json ─────────┬──→ vscode/themes/*.json ─────────────→ osiris-theme.vsix
                            │
iconography/glyphs.json ────┼──→ vscode/fileicons/* ───────────────→ Osiris File Icons
  + iconography/map/*.json  ├──→ vscode/producticons/* ────────────→ Osiris Product Icons (WOFF)
                            ├──→ build/icons/Osiris/ ──────────────→ /usr/share/icons/Osiris
                            │
                            ├──→ desktop/gtk-common/* ─────────────→ /usr/share/themes/Osiris{,-Light}
                            ├──→ desktop/gnome-shell/*.css.in ─────→ GNOME Shell Theme
                            ├──→ desktop/plasma/* ─────────────────→ KDE Plasma / Kvantum / Aurorae
                            ├──→ scripts/lib/gen_terminal.py ──────→ GNOME Terminal · Ptyxis · Konsole
                            ├──→ boot/grub/* ──────────────────────→ /boot/grub/themes/osiris
                            ├──→ vitepress/theme/osiris.css ───────→ npm: osiris-vitepress-theme
                            ├──→ bootstrap/scss/* ─────────────────→ npm: osiris-bootstrap-theme
                            ├──→ forgejo/theme-osiris-*.css ───────→ Forgejo / Gitea ZIP archiv
                            ├──→ browsers/*/manifest.json ─────────→ Chrome / Edge / Firefox doplňky
                            └──→ assets/wallpapers/* ──────────────→ /usr/share/backgrounds/osiris
```

---

## 2. Přehled cílů a balíčků

| Cílová platforma | Výstupní formát | Umístění / Balíček |
|---|---|---|
| **VS Code** | `.vsix` | Rozšíření obsahující barvy i obě sady ikon |
| **Linux (Debian / Ubuntu)** | `.deb` | 6 samostatných deb balíčků (`osiris-gtk-theme`, `osiris-icon-theme`, ...) |
| **Linux (Fedora / openSUSE)** | `.rpm` | RPM specifikace generující odpovídající subbalíčky |
| **VitePress (NPM)** | `.tgz` | `osiris-vitepress-theme` |
| **Bootstrap 5 (NPM)** | `.tgz` | `osiris-bootstrap-theme` |
| **Forgejo / Gitea** | `.zip` | Samostatný balíček CSS motivů |
| **Webové prohlížeče** | `.zip` | Rozšíření pro Chromium i Firefox (Dark & Light) |
| **GRUB2** | adresář / skript | Téma bootloaderu s automatickým instalátorem `install.sh` |

---

## 3. Garance konzistence: CI Token Guard

Aby se zabránilo neúmyslnému rozchodu barev mezi dokumentací a generovaným kódem, obsahuje repozitář validační skript:

```bash
bash scripts/check-tokens.sh
```

### Co tento skript ověřuje v CI:
1. Shodu každého hexadecimálního kódu v `docs/DESIGN_SYSTEM.md` s `assets/tokens.json`.
2. Validitu všech odkazů v mapovacích souborech ikon (`iconography/map/*.json`) vůči existujícím glyfům v `iconography/glyphs.json`.
3. Správnost CSS proměnných v balíčcích pro VitePress, Bootstrap a Forgejo.

Při jakémkoliv nesouladu dojde k okamžitému selhání CI pipeline na GitHubu.


# Správa a synchronizace OSIRIS Wiki

Tato složka (`wiki/`) obsahuje zdrojové soubory pro oficiální **GitHub Wiki** repozitáře `osiris-theme`. Soubory jsou uspořádány tak, aby byly plně kompatibilní s formátem GitHub Wiki (včetně postranního panelu `_Sidebar.md` a zápatí `_Footer.md`) a zároveň čitelné přímo ve stromu repozitáře.

---

## 1. Struktura souborů

- `Home.md` – Hlavní vstupní stránka Wiki.
- `_Sidebar.md` – Postranní navigační lišta.
- `_Footer.md` – Globální zápatí všech stránek.
- `Manual-grafickeho-designu.md` – Pravidla značky, konstrukce loga, ochranné zóny.
- `Barevna-paleta-a-tokeny.md` – Dual-accent paleta, neutrální rampa, status bar, syntax.
- `Typografie.md` – Specifikace Fira Code, škály velikostí a pravidla pro UI.
- `Komponenty-a-UI-stavy.md` – Rádiusy, stíny, Focus Ring a kontrakt komponent.
- `Ikonografie.md` – Papirus Icon Theme, souborové i systémové ikony.
- `Tapety-a-vizualni-aktiva.md` – Kolekce tapet, app ikony a letterpress vodoznaky.
- `Galerie-a-screenshoty.md` – Vizuální galerie a rozbor rozhraní.
- `Architektura-a-export.md` – Pipeline generování výstupních balíčků.
- `images/` – Grafická aktiva, loga a screenshoty.

---

## 2. Jak publikovat obsah do GitHub Wiki

GitHub pro každý repozitář udržuje Wiki jako samostatný Git repozitář s příponou `.wiki.git`.

### Prvotní inicializace na GitHubu:
1. Přejděte na záložku **Wiki** ve Vašem repozitáři na GitHubu (`https://github.com/richardblaha/osiris-theme/wiki`).
2. Pokud je Wiki prázdná, klikněte na **Create the first page** a uložte výchozí stránku (tím GitHub repozitář wiki fyzicky vytvoří).

### Synchronizace přes Git (ruční):
```bash
# 1. Naklonujte wiki repozitář do dočasné složky
git clone https://github.com/richardblaha/osiris-theme.wiki.git /tmp/osiris-wiki

# 2. Zkopírujte soubory z této složky wiki/ do naklonované wiki
cp -r wiki/* /tmp/osiris-wiki/

# 3. Přejděte do složky, commitněte a pushněte
cd /tmp/osiris-wiki
git add .
git commit -m "docs(wiki): aktualizace manuálu grafického designu"
git push origin master
```

Nebo můžete využít připravený příkaz v `Makefile`:
```bash
make wiki-sync
```


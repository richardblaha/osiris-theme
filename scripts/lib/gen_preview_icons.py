#!/usr/bin/env python3
"""Generate docs/preview/icons.js — the data behind the preview page's icon-theme
showcase tabs (one per icon theme this repo ships).

Single source of truth, like everything else: glyph paths from
iconography/glyphs.json, wiring from iconography/map/{filetypes,producticons,xdg}.json,
colours from assets/tokens.json (icon.fileIcon.palette / icon.xdg.categoryColor /
themes.*.text).

The three shipped icon themes:
  * file    — VS Code "Osiris File Icons"     (iconography/map/filetypes.json)
  * product — VS Code "Osiris Product Icons"  (iconography/map/producticons.json)
  * xdg     — freedesktop icon theme "Osiris" (iconography/map/xdg.json)

Run by `scripts/build.sh pages` (and `make icons`); the output is committed so
docs/preview/index.html also works opened straight from disk.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "preview" / "icons.js"


def load(*parts: str) -> dict:
    return json.loads(ROOT.joinpath(*parts).read_text(encoding="utf-8"))


APP_LABELS = {
    "text-editor": "Textový editor", "terminal-app": "Terminál",
    "file-manager": "Správce souborů", "web-browser": "Webový prohlížeč",
    "code": "Vývojové prostředí", "development": "Vývoj", "calculator": "Kalkulačka",
    "image-viewer": "Prohlížeč obrázků", "media-player": "Přehrávač videa",
    "music": "Přehrávač hudby", "mail": "Pošta", "help": "Nápověda",
    "package": "Software", "monitor": "Sledování systému", "settings": "Nastavení",
    "screenshot": "Snímek obrazovky", "color-picker": "Kapátko barev",
    "file-archive": "Správce archivů", "calendar": "Kalendář", "clock": "Hodiny",
}
CATEGORY_LABELS = {
    "development": "Vývoj", "graphics": "Grafika", "internet": "Internet",
    "multimedia": "Multimédia", "music": "Zvuk", "videos": "Video",
    "office": "Kancelář", "games": "Hry", "system": "Systém", "utilities": "Nástroje",
    "accessories": "Příslušenství", "science": "Věda", "education": "Vzdělávání",
    "package": "Ostatní", "preferences": "Předvolby", "settings": "Předvolby systému",
    "help": "Nápověda",
}
XDG_CATEGORY_CS = {
    "actions": "Akce", "apps": "Aplikace", "categories": "Kategorie nabídky",
    "devices": "Zařízení", "emblems": "Emblémy", "mimetypes": "Typy souborů",
    "places": "Místa", "status": "Stav",
}


def main() -> None:
    glyphs = load("iconography", "glyphs.json")["glyphs"]
    ft = load("iconography", "map", "filetypes.json")
    pi = load("iconography", "map", "producticons.json")
    xdg = load("iconography", "map", "xdg.json")["icons"]
    tok = load("assets", "tokens.json")["icon"]
    themes_tok = load("assets", "tokens.json")["themes"]

    palette = tok["fileIcon"]["palette"]
    file_default = tok["fileIcon"]["default"]
    folder_tok = tok["fileIcon"]["folder"]
    folder_open_tok = tok["fileIcon"]["folderOpen"]
    cat_color = tok["xdg"]["categoryColor"]
    ui_dark = themes_tok["dark"]["text"]["primary"]
    ui_light = themes_tok["light"]["text"]["primary"]

    used: dict[str, dict] = {}

    def g(key: str) -> dict:
        if key not in used:
            gl = glyphs[key]
            entry = {"d": gl["d"]}
            if gl.get("evenodd"):
                entry["e"] = 1
            used[key] = entry
        return {"glyph": key}

    def color_of(name: str) -> str:
        return file_default if name == "default" else palette.get(name, file_default)

    def dedupe(pairs, label_for) -> list:
        """pairs: iterable of (identifier, glyph). Keep first identifier per glyph."""
        out, seen = [], set()
        for ident, glyph in pairs:
            if glyph in seen or glyph not in glyphs:
                continue
            seen.add(glyph)
            out.append({**g(glyph), "label": label_for(ident, glyph)})
        return out

    # ---- 1. VS Code file icons -------------------------------------------
    folders = [
        {**g("folder"), "label": "folder", "dark": folder_tok["dark"], "light": folder_tok["light"]},
        {**g("folder-open"), "label": "folder (otevřená)",
         "dark": folder_open_tok["dark"], "light": folder_open_tok["light"]},
    ]
    seen_f = set()
    for glyph in ft["folderNames"].values():
        if glyph in seen_f or glyph not in glyphs:
            continue
        seen_f.add(glyph)
        folders.append({**g(glyph), "label": glyph,
                        "dark": folder_tok["dark"], "light": folder_tok["light"]})

    def file_entries(section: dict) -> list:
        out = []
        for name, spec in section.items():
            if spec["glyph"] not in glyphs:
                continue
            out.append({**g(spec["glyph"]), "label": name,
                        "color": color_of(spec.get("color", "default"))})
        return out

    file_theme = {
        "id": "file",
        "name": "Osiris File Icons",
        "target": "VS Code · motiv ikon souborů",
        "note": "iconography/map/filetypes.json — glyf + role z palety "
                "tokens.icon.fileIcon.palette. Barvené SVG na asociaci.",
        "groups": [
            {"title": f"Složky ({len(folders)})", "items": folders},
            {"title": f"Podle přípony ({len(ft['fileExtensions'])})",
             "items": file_entries(ft["fileExtensions"])},
            {"title": f"Podle názvu ({len(ft['fileNames'])})",
             "items": file_entries(ft["fileNames"])},
        ],
    }

    # ---- 2. VS Code product icons --------------------------------------
    prod = dedupe(
        ((ident, glyph) for ident, glyph in pi.items() if not ident.startswith("$")),
        lambda ident, glyph: glyph,
    )
    for item in prod:
        item["dark"], item["light"] = ui_dark, ui_light
    n_ids = sum(1 for k in pi if not k.startswith("$"))
    product_theme = {
        "id": "product",
        "name": "Osiris Product Icons",
        "target": "VS Code · motiv produktových ikon (osiris-symbols.woff)",
        "note": f"iconography/map/producticons.json — {n_ids} identifikátorů "
                f"Codicon přemapováno na {len(prod)} glyfů. Monochromatické, "
                f"dědí barvu UI; identifikátory mimo seznam padají zpět na Codicon.",
        "groups": [{"title": f"Sada glyfů ({len(prod)})", "items": prod}],
    }

    # ---- 3. XDG / freedesktop icon theme ------------------------------
    xdg_groups = []
    for cat, mapping in xdg.items():
        if cat.startswith("$"):
            continue
        labels = APP_LABELS if cat == "apps" else CATEGORY_LABELS if cat == "categories" else {}
        items = dedupe(mapping.items(),
                       lambda ident, glyph, lut=labels: lut.get(glyph, glyph))
        color = cat_color.get(cat, file_default)
        for item in items:
            item["color"] = color
        xdg_groups.append({"title": f"{XDG_CATEGORY_CS.get(cat, cat)} · {cat} ({len(items)})",
                           "items": items})
    xdg_theme = {
        "id": "xdg",
        "name": "Osiris",
        "target": "XDG / freedesktop · /usr/share/icons/Osiris (GNOME, KDE Plasma)",
        "note": "iconography/map/xdg.json — 8 kategorií, barva podle "
                "tokens.icon.xdg.categoryColor. Dědí Papirus-Dark, Papirus, breeze, "
                "gnome, hicolor pro cokoli nestylované.",
        "groups": xdg_groups,
    }

    data = {
        "glyphs": {k: used[k] for k in sorted(used)},
        "themes": [file_theme, product_theme, xdg_theme],
    }

    banner = ("/* GENERATED by scripts/lib/gen_preview_icons.py from iconography/ + "
              "assets/tokens.json — do not edit. */\n")
    OUT.write_text(
        banner + "window.OSIRIS_PREVIEW_ICONS = "
        + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    total = sum(len(gr["items"]) for th in data["themes"] for gr in th["groups"])
    print(f"gen_preview_icons: {len(data['themes'])} themes, {total} icon cards -> "
          f"{OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

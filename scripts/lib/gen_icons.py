#!/usr/bin/env python3
"""OSIRIS iconography generator.

Expands the compact glyph source (iconography/glyphs.json) plus the maps
(iconography/map/*.json) into every icon deliverable:

  vscode-file     VS Code file icon theme   -> <out>/fileicons/{osiris-file-icons.json, icons/*.svg}
  vscode-product  VS Code product icon theme -> <out>/producticons/{osiris-product-icons.json, osiris-symbols.woff}
  xdg             XDG / freedesktop icon theme -> <out>/Osiris/{index.theme, scalable/<cat>/*.svg, <size>x<size>/<cat>/*}
  all             all of the above

Colours come from assets/tokens.json. No network, no third-party Python deps.
The product icon font needs `fantasticon` (npx) and the XDG raster sizes need
`rsvg-convert` (or inkscape / imagemagick / cairosvg); both degrade with a
warning when the tool is missing.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICONOGRAPHY = os.path.join(ROOT, "iconography")


def load(*parts: str) -> dict:
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return json.load(fh)


TOKENS = load(ROOT, "assets", "tokens.json")
GLYPHS = load(ICONOGRAPHY, "glyphs.json")["glyphs"]
ICON_TOK = TOKENS["icon"]
GRID = ICON_TOK["grid"]


def warn(msg: str) -> None:
    print(f"\033[33m[osiris] warn:\033[0m {msg}", file=sys.stderr)


def log(msg: str) -> None:
    print(f"\033[36m[osiris]\033[0m {msg}")


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# --------------------------------------------------------------------------- SVG
def svg(glyph_name: str, color: str) -> str:
    g = GLYPHS[glyph_name]
    fr = ' fill-rule="evenodd" clip-rule="evenodd"' if g.get("evenodd") else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}" '
        f'width="{GRID}" height="{GRID}">'
        f'<path{fr} fill="{color}" d="{g["d"]}"/></svg>\n'
    )


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


# ---------------------------------------------------------------- VS Code: files
def gen_vscode_file(out: str) -> None:
    m = load(ICONOGRAPHY, "map", "filetypes.json")
    pal = ICON_TOK["fileIcon"]["palette"]
    default_c = ICON_TOK["fileIcon"]["default"]
    folder_tok = ICON_TOK["fileIcon"]["folder"]
    folder_open_tok = ICON_TOK["fileIcon"]["folderOpen"]

    icons_dir = os.path.join(out, "fileicons", "icons")
    if os.path.isdir(icons_dir):
        shutil.rmtree(icons_dir)

    defs: dict[str, dict] = {}

    def resolve_color(spec: dict) -> str:
        if "token" in spec:
            return folder_tok["dark"] if spec["token"] == "folder" else folder_open_tok["dark"]
        c = spec.get("color", "default")
        return default_c if c == "default" else pal[c]

    def define(def_id: str, glyph: str, color: str) -> str:
        if def_id not in defs:
            write(os.path.join(icons_dir, f"{def_id}.svg"), svg(glyph, color))
            defs[def_id] = {"iconPath": f"./icons/{def_id}.svg"}
        return def_id

    # base file + folders
    define("_file", m["file"]["glyph"], resolve_color(m["file"]))
    define("_folder", m["folder"]["glyph"], folder_tok["dark"])
    define("_folder_open", m["folderExpanded"]["glyph"], folder_open_tok["dark"])
    define("_folder_light", m["folder"]["glyph"], folder_tok["light"])
    define("_folder_open_light", m["folderExpanded"]["glyph"], folder_open_tok["light"])

    theme: dict = {
        "iconDefinitions": defs,
        "file": "_file",
        "folder": "_folder",
        "folderExpanded": "_folder_open",
        "rootFolder": "_folder",
        "rootFolderExpanded": "_folder_open",
        "fileExtensions": {},
        "fileNames": {},
        "folderNames": {},
        "folderNamesExpanded": {},
        "languageIds": {},
        "light": {
            "folder": "_folder_light",
            "folderExpanded": "_folder_open_light",
            "rootFolder": "_folder_light",
            "rootFolderExpanded": "_folder_open_light",
        },
        "hidesExplorerArrows": False,
        "version": TOKENS["meta"]["version"],
    }

    for ext, spec in m["fileExtensions"].items():
        did = define(f"ext_{ext.replace('.', '_')}", spec["glyph"], resolve_color(spec))
        theme["fileExtensions"][ext] = did

    for name, spec in m["fileNames"].items():
        key = name.lower().replace(".", "_").replace("/", "_")
        did = define(f"name_{key}", spec["glyph"], resolve_color(spec))
        theme["fileNames"][name] = did

    for name, glyph in m["folderNames"].items():
        did = define(f"dir_{name.strip('.').replace('/', '_') or 'dot'}", glyph, folder_tok["dark"])
        theme["folderNames"][name] = did
    for name, glyph in m["folderNamesExpanded"].items():
        theme["folderNamesExpanded"][name] = "_folder_open"

    # a few language-id fallbacks (used when a file has no extension match)
    lang_map = {
        "javascript": "ext_js", "typescript": "ext_ts", "json": "ext_json",
        "html": "ext_html", "css": "ext_css", "scss": "ext_scss",
        "python": "ext_py", "rust": "ext_rs", "go": "ext_go", "java": "ext_java",
        "c": "ext_c", "cpp": "ext_cpp", "csharp": "ext_cs", "ruby": "ext_rb",
        "php": "ext_php", "shellscript": "ext_sh", "yaml": "ext_yaml",
        "markdown": "ext_md", "sql": "ext_sql", "dockerfile": "name_dockerfile",
        "xml": "ext_xml", "plaintext": "ext_txt",
    }
    for lang, did in lang_map.items():
        if did in defs:
            theme["languageIds"][lang] = did

    write(os.path.join(out, "fileicons", "osiris-file-icons.json"),
          json.dumps(theme, indent=2) + "\n")
    log(f"  vscode file icons: {len(defs)} definitions, "
        f"{len(theme['fileExtensions'])} extensions, {len(theme['fileNames'])} names")


# -------------------------------------------------------------- VS Code: product
def gen_vscode_product(out: str) -> None:
    m = load(ICONOGRAPHY, "map", "producticons.json")
    mapping = {k: v for k, v in m.items() if not k.startswith("$")}
    used = sorted({g for g in mapping.values() if g in GLYPHS})

    font_id = ICON_TOK["productIcon"]["fontId"]
    pdir = os.path.join(out, "producticons")
    os.makedirs(pdir, exist_ok=True)

    runner = ["fantasticon"] if have("fantasticon") else \
             ["npx", "--yes", "fantasticon"] if have("npx") else None

    codepoint: dict[str, int] = {}
    if runner is None:
        warn("fantasticon/npx not found — osiris-symbols.woff not built; "
             "assigning fallback codepoints (product icon theme still needs the font at package time)")
        codepoint = {g: 0xF101 + i for i, g in enumerate(used)}
    else:
        with tempfile.TemporaryDirectory() as tmp:
            for g in used:
                write(os.path.join(tmp, f"{g}.svg"), svg(g, "#000"))
            cmd = runner + [tmp, "-o", pdir, "-n", font_id, "-t", "woff",
                            "-g", "json", "--normalize", "-h", str(GRID * 40)]
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                codepoint = {k: int(v) for k, v in
                             load(pdir, f"{font_id}.json").items()}
                os.remove(os.path.join(pdir, f"{font_id}.json"))
            except (subprocess.CalledProcessError, FileNotFoundError, KeyError) as exc:
                detail = getattr(exc, "stderr", "") or str(exc)
                warn(f"fantasticon failed — osiris-symbols.woff not built: {detail.strip()[:200]}")
                codepoint = {g: 0xF101 + i for i, g in enumerate(used)}

    icon_definitions = {
        pid: {"fontCharacter": "\\" + format(codepoint[g], "X")}
        for pid, g in mapping.items() if g in codepoint
    }
    theme = {
        "fonts": [{
            "id": font_id,
            "src": [{"path": f"./{font_id}.woff", "format": "woff"}],
            "weight": "normal",
            "style": "normal",
        }],
        "iconDefinitions": icon_definitions,
        "version": TOKENS["meta"]["version"],
    }
    write(os.path.join(pdir, "osiris-product-icons.json"),
          json.dumps(theme, indent=2) + "\n")
    built = os.path.exists(os.path.join(pdir, f"{font_id}.woff"))
    log(f"  vscode product icons: {len(icon_definitions)} ids, {len(used)}-glyph font "
        f"{'-> ' + font_id + '.woff' if built else '(font NOT built)'}")


# --------------------------------------------------------------------------- XDG
def gen_xdg(out: str) -> None:
    xdg = ICON_TOK["xdg"]
    m = load(ICONOGRAPHY, "map", "xdg.json")
    icons = m["icons"]
    aliases = {k: v for k, v in m["aliases"].items() if not k.startswith("$")}
    cat_color = xdg["categoryColor"]
    emblem_color = xdg["emblemColor"]
    sizes = xdg["sizes"]
    categories = xdg["categories"]

    theme_dir = os.path.join(out, xdg["themeName"])
    if os.path.isdir(theme_dir):
        shutil.rmtree(theme_dir)

    ctx = {
        "actions": "Actions", "apps": "Applications", "categories": "Categories",
        "devices": "Devices", "emblems": "Emblems", "mimetypes": "MimeTypes",
        "places": "Places", "status": "Status",
    }

    # ---- index.theme
    dirs = []
    for cat in categories:
        for s in sizes:
            dirs.append(f"{s}x{s}/{cat}")
        dirs.append(f"scalable/{cat}")
    lines = [
        "[Icon Theme]",
        f"Name={xdg['displayName']}",
        "Comment=OSIRIS dual-accent icon theme — Material Symbols language, cyan/rose on a GitHub-flavoured ramp",
        f"Inherits={','.join(xdg['inherits'])}",
        "Example=folder-open",
        "FollowsColorScheme=false",
        "",
        f"Directories={','.join(dirs)}",
        "",
    ]
    for cat in categories:
        for s in sizes:
            lines += [f"[{s}x{s}/{cat}]", f"Size={s}", f"Context={ctx[cat]}",
                      "Type=Threshold", "Threshold=8", "MinSize=8", "MaxSize=256", ""]
        lines += [f"[scalable/{cat}]", "Size=24", f"Context={ctx[cat]}",
                  "MinSize=8", "MaxSize=512", "Type=Scalable", ""]
    write(os.path.join(theme_dir, "index.theme"), "\n".join(lines))

    # ---- scalable SVGs
    written: dict[str, set] = {c: set() for c in categories}
    total = 0
    for cat, mapping in icons.items():
        color = emblem_color if cat == "emblems" else cat_color.get(cat, "#8b949e")
        for name, glyph in mapping.items():
            if glyph not in GLYPHS:
                warn(f"xdg {cat}/{name}: unknown glyph '{glyph}' — skipped")
                continue
            write(os.path.join(theme_dir, "scalable", cat, f"{name}.svg"), svg(glyph, color))
            written[cat].add(name)
            total += 1

    # ---- aliases as same-dir relative symlinks (resolve one hop through the map)
    alias_count = 0
    for cat, mapping in aliases.items():
        d = os.path.join(theme_dir, "scalable", cat)
        for alias, target in mapping.items():
            hop = target
            seen = set()
            while hop in mapping and hop not in written.get(cat, set()) and hop not in seen:
                seen.add(hop)
                hop = mapping[hop]
            if hop not in written.get(cat, set()):
                warn(f"xdg alias {cat}/{alias} -> {target}: target not generated — skipped")
                continue
            link = os.path.join(d, f"{alias}.svg")
            if os.path.exists(link) or os.path.islink(link):
                continue
            os.symlink(f"{hop}.svg", link)
            alias_count += 1

    # ---- populate the per-size directories.
    # Default: every size directory carries the vector as a relative symlink into
    # scalable/ (an all-vector theme — GNOME and KDE both scale SVGs per request,
    # and the Threshold dirs give apps that ask for a fixed pixel size a hit).
    # OSIRIS_ICON_RASTER=1 renders real PNGs instead (needs an SVG rasteriser).
    raster = _raster_fn() if os.environ.get("OSIRIS_ICON_RASTER") == "1" else None
    links = pngs = 0
    for cat in categories:
        sdir = os.path.join(theme_dir, "scalable", cat)
        for entry in sorted(os.listdir(sdir)):
            base = entry[:-4]
            for s in sizes:
                ddir = os.path.join(theme_dir, f"{s}x{s}", cat)
                os.makedirs(ddir, exist_ok=True)
                if raster is not None:
                    dst = os.path.join(ddir, f"{base}.png")
                    real = os.path.join(sdir, entry)
                    if os.path.islink(real):
                        tgt = os.readlink(real)[:-4] + ".png"
                        if not os.path.lexists(dst):
                            os.symlink(tgt, dst)
                    else:
                        raster(real, dst, s)
                        pngs += 1
                else:
                    dst = os.path.join(ddir, f"{base}.svg")
                    if not os.path.lexists(dst):
                        os.symlink(f"../../scalable/{cat}/{entry}", dst)
                        links += 1
    if raster is not None:
        log(f"  xdg raster: {pngs} PNGs across {len(sizes)} sizes")
    else:
        log(f"  xdg size dirs: {links} vector links across {len(sizes)} sizes")

    log(f"  xdg icon theme '{xdg['themeName']}': {total} icons, {alias_count} aliases, "
        f"{len(categories)} categories")


def _raster_fn():
    if have("rsvg-convert"):
        return lambda s, d, px: subprocess.run(
            ["rsvg-convert", "-w", str(px), "-h", str(px), "-o", d, s], check=True,
            capture_output=True)
    if have("inkscape"):
        return lambda s, d, px: subprocess.run(
            ["inkscape", s, "--export-type=png", f"--export-filename={d}",
             f"--export-width={px}", f"--export-height={px}"], check=True, capture_output=True)
    if have("convert"):
        return lambda s, d, px: subprocess.run(
            ["convert", "-background", "none", "-density", "300", "-resize",
             f"{px}x{px}", s, d], check=True, capture_output=True)
    try:
        import cairosvg  # noqa: F401
        return lambda s, d, px: __import__("cairosvg").svg2png(
            url=s, write_to=d, output_width=px, output_height=px)
    except ImportError:
        return None


# -------------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    target, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    if target in ("vscode-file", "all"):
        gen_vscode_file(out)
    if target in ("vscode-product", "all"):
        gen_vscode_product(out)
    if target in ("xdg", "all"):
        gen_xdg(out)
    if target not in ("vscode-file", "vscode-product", "xdg", "all"):
        warn(f"unknown target '{target}'")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

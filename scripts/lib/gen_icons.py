#!/usr/bin/env python3
"""OSIRIS iconography generator — Papirus-based.

Takes the Papirus Icon Theme SVGs (fetched at build time via shallow git
clone), recolours every fill with the Osiris palette, and emits:

  xdg          freedesktop icon theme  -> <out>/Osiris/{index.theme, scalable/, <size>x<size>/}
  vscode-file  VS Code file icon theme  -> <out>/fileicons/{osiris-file-icons.json, icons/*.svg}
  all          both of the above

File icons are SHARED: the same recoloured Papirus mimetype SVGs are used
for the VS Code file icon theme and the XDG mimetypes directory — one set of
SVGs, two consumers.

The product icon theme has been removed; VS Code falls back to the built-in
Codicon set.

Colours come from assets/tokens.json -> icon.recolor. No third-party Python
deps; the Papirus source is a shallow clone cached under build/papirus-src/.
"""
from __future__ import annotations

import colorsys
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ICONOGRAPHY = os.path.join(ROOT, "iconography")

PAPIRUS_REPO = "https://github.com/PapirusDevelopmentTeam/papirus-icon-theme.git"
PAPIRUS_SIZE = "24x24"  # design size — used as the scalable source


def load(*parts: str) -> dict:
    with open(os.path.join(*parts), encoding="utf-8") as fh:
        return json.load(fh)


TOKENS = load(ROOT, "assets", "tokens.json")
ICON_TOK = TOKENS["icon"]
VERSION = TOKENS["meta"]["version"]


def warn(msg: str) -> None:
    print(f"\033[33m[osiris] warn:\033[0m {msg}", file=sys.stderr)


def log(msg: str) -> None:
    print(f"\033[36m[osiris]\033[0m {msg}")


def die(msg: str) -> None:
    print(f"\033[31m[osiris] error:\033[0m {msg}", file=sys.stderr)
    raise SystemExit(1)


# ============================================================ colour remapping
# The Papirus palette is recoloured into the Osiris identity.  Structural
# colours (paper, greys, folder-blue) are mapped exactly.  Every other colour
# is classified by hue into one of the seven Osiris accent families; the
# original value (brightness) is preserved so the Papirus visual hierarchy
# (shadows, highlights, layering) is maintained.

_STRUCTURAL = {
    # Papirus paper / neutrals -> Osiris neutral ramp (GitHub-style)
    "#e4e4e4": "#e8eaed",
    "#fafafa": "#f0f3f6",
    "#f5f5f5": "#f0f3f6",
    "#ffffff": "#ffffff",
    "#4f4f4f": "#484f58",
    "#3f3f3f": "#30363d",
    "#323232": "#30363d",
    "#222c31": "#21262d",
    "#2e3436": "#21262d",
    "#1a1a1a": "#161b22",
    "#2b2b2b": "#30363d",
    "#2c2c2c": "#30363d",
    "#2d2d2d": "#30363d",
    "#303030": "#30363d",
    "#313131": "#484f58",
    "#333333": "#484f58",
    "#3d3d3d": "#484f58",
    "#3d3846": "#30363d",
    "#404040": "#484f58",
    "#424242": "#484f58",
    "#455a64": "#6e7681",
    "#607d8b": "#6e7681",
    "#676767": "#6e7681",
    "#696969": "#6e7681",
    "#727272": "#6e7681",
    "#737373": "#6e7681",
    "#808080": "#8b949e",
    "#8e8e8e": "#8b949e",
    "#908f94": "#8b949e",
    "#9a9a9a": "#8b949e",
    "#a9a9a9": "#afb8c1",
    "#b3b3b3": "#afb8c1",
    "#c2c2c2": "#afb8c1",
    "#cccccc": "#d0d7de",
    "#c8c8c8": "#d0d7de",
    "#c0c0c0": "#d0d7de",
    "#c0c8c7": "#d0d7de",
    "#d3d3d3": "#d0d7de",
    "#dcdcdc": "#d0d7de",
    "#eaeaea": "#e8eaed",
    "#f2f2f2": "#f0f3f6",
    # Papirus folder blue -> Osiris folder colour (cyan family)
    "#3a87e5": "#1f9fc7",
    "#5294e2": "#39b9d6",
    "#4877b1": "#1689a8",
    "#3b6da4": "#127a98",
    "#4a90d9": "#2aabca",
}

# Osiris accent families: (hue_min, hue_max, osiris_hue, osiris_sat)
_ACCENTS = [
    (345, 374, 358, 0.94),   # red   #f2585b
    (15,  50,  40,  0.70),   # amber #d9a441
    (50,  170, 120, 0.67),   # green #3fb950
    (170, 200, 186, 0.84),   # cyan  #22c3d6
    (200, 250, 210, 0.62),   # blue  #589bf0
    (250, 290, 258, 0.41),   # violet #a684f5
    (290, 345, 330, 0.67),   # rose  #f0509a
]

_cache: dict[str, str] = {}


def _classify_hue(h: float) -> tuple[float, float]:
    """Return (osiris_hue, osiris_saturation) for the given hue (0-360)."""
    for lo, hi, oh, osat in _ACCENTS:
        if lo <= h < hi:
            return oh, osat
    return _ACCENTS[0][2], _ACCENTS[0][3]


def _remap(hex_color: str) -> str:
    """Recolour a single hex colour into the Osiris palette."""
    lc = hex_color.lower()
    if lc in _cache:
        return _cache[lc]

    if lc in _STRUCTURAL:
        _cache[lc] = _STRUCTURAL[lc]
        return _cache[lc]

    try:
        r = int(lc[1:3], 16) / 255.0
        g = int(lc[3:5], 16) / 255.0
        b = int(lc[5:7], 16) / 255.0
    except (ValueError, IndexError):
        _cache[lc] = hex_color
        return hex_color

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Low-saturation -> neutral ramp by value
    if s < 0.08:
        if v > 0.92:
            result = "#e8eaed"
        elif v > 0.82:
            result = "#d0d7de"
        elif v > 0.68:
            result = "#afb8c1"
        elif v > 0.50:
            result = "#8b949e"
        elif v > 0.35:
            result = "#6e7681"
        elif v > 0.20:
            result = "#484f58"
        elif v > 0.10:
            result = "#30363d"
        else:
            result = "#21262d"
        _cache[lc] = result
        return result

    # Accent: shift to Osiris hue, use Osiris saturation, keep original value
    oh, osat = _classify_hue(h * 360)
    nr, ng, nb = colorsys.hsv_to_rgb(oh / 360.0, osat, v)
    result = "#{:02x}{:02x}{:02x}".format(
        round(nr * 255), round(ng * 255), round(nb * 255))
    _cache[lc] = result
    return result


_FILL_STYLE = re.compile(r'(fill:)(#[0-9a-fA-F]{6})')
_FILL_ATTR = re.compile(r'(fill=")(#[0-9a-fA-F]{6})(")')


def recolor_svg(svg_text: str) -> str:
    """Replace every fill colour in an SVG with its Osiris equivalent."""
    svg_text = _FILL_STYLE.sub(
        lambda m: m.group(1) + _remap(m.group(2)), svg_text)
    svg_text = _FILL_ATTR.sub(
        lambda m: m.group(1) + _remap(m.group(2)) + m.group(3), svg_text)
    return svg_text


# ============================================================ Papirus source
def ensure_papirus(src_dir: str) -> str:
    """Ensure the Papirus source is available; shallow-clone if missing."""
    papirus = os.path.join(src_dir, "Papirus")
    if os.path.isdir(os.path.join(papirus, PAPIRUS_SIZE)):
        return src_dir
    log("fetching Papirus icon theme (shallow clone)...")
    if os.path.isdir(src_dir):
        shutil.rmtree(src_dir)
    os.makedirs(os.path.dirname(src_dir), exist_ok=True)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", PAPIRUS_REPO, src_dir],
            check=True, capture_output=True, text=True, timeout=300)
    except (subprocess.CalledProcessError, FileNotFoundError,
            subprocess.TimeoutExpired) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        die(f"failed to fetch Papirus: {detail.strip()[:300]}")
    log("  Papirus source ready")
    return src_dir


def read_papirus_svg(papirus_root: str, category: str, name: str) -> str | None:
    """Read a Papirus 24x24 SVG, resolving symlinks."""
    path = os.path.join(papirus_root, PAPIRUS_SIZE, category, f"{name}.svg")
    real = path
    seen: set[str] = set()
    while os.path.islink(real) and real not in seen:
        seen.add(real)
        link_target = os.readlink(real)
        if os.path.isabs(link_target):
            real = link_target
        else:
            real = os.path.join(os.path.dirname(real), link_target)
    if not os.path.isfile(real):
        return None
    with open(real, encoding="utf-8") as fh:
        return fh.read()


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


# ============================================================ XDG icon theme
def gen_xdg(out: str, papirus_root: str) -> None:
    xdg = ICON_TOK["xdg"]
    m = load(ICONOGRAPHY, "icon_map.json")
    theme_name = xdg["themeName"]
    sizes = xdg["sizes"]
    categories = xdg["categories"]

    ctx = {
        "actions": "Actions", "apps": "Applications", "categories": "Categories",
        "devices": "Devices", "emblems": "Emblems", "mimetypes": "MimeTypes",
        "places": "Places", "status": "Status",
    }

    theme_dir = os.path.join(out, theme_name)
    if os.path.isdir(theme_dir):
        shutil.rmtree(theme_dir)

    # ---- index.theme
    dirs = []
    for cat in categories:
        for s in sizes:
            dirs.append(f"{s}x{s}/{cat}")
        dirs.append(f"scalable/{cat}")
    lines = [
        "[Icon Theme]",
        f"Name={xdg['displayName']}",
        "Comment=OSIRIS icon theme - Papirus shapes recoloured with the Osiris palette",
        f"Inherits={','.join(xdg['inherits'])}",
        "Example=folder",
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

    # ---- scalable SVGs: copy ALL Papirus icons (recoloured) + explicit overrides
    written: dict[str, set] = {c: set() for c in categories}
    total = 0
    xdg_map = m.get("xdg", {})

    for cat in categories:
        cat_dir = os.path.join(papirus_root, PAPIRUS_SIZE, cat)
        if not os.path.isdir(cat_dir):
            continue
        for entry in sorted(os.listdir(cat_dir)):
            if not entry.endswith(".svg"):
                continue
            name = entry[:-4]
            svg = read_papirus_svg(papirus_root, cat, name)
            if svg is None:
                continue
            write(os.path.join(theme_dir, "scalable", cat, f"{name}.svg"),
                  recolor_svg(svg))
            written[cat].add(name)
            total += 1

    # ---- explicit overrides (XDG name differs from Papirus name)
    for cat, overrides in xdg_map.items():
        if cat not in categories:
            continue
        for xdg_name, papirus_name in overrides.items():
            if xdg_name in written[cat]:
                continue
            svg = read_papirus_svg(papirus_root, cat, papirus_name)
            if svg is None:
                warn(f"xdg {cat}/{xdg_name}: Papirus '{papirus_name}' not found - skipped")
                continue
            write(os.path.join(theme_dir, "scalable", cat, f"{xdg_name}.svg"),
                  recolor_svg(svg))
            written[cat].add(xdg_name)
            total += 1

    # ---- aliases as same-dir relative symlinks
    alias_count = 0
    aliases = m.get("xdg_aliases", {})
    for cat, mapping in aliases.items():
        d = os.path.join(theme_dir, "scalable", cat)
        for alias, target in mapping.items():
            hop = target
            seen: set[str] = set()
            while hop in mapping and hop not in written.get(cat, set()) and hop not in seen:
                seen.add(hop)
                hop = mapping[hop]
            if hop not in written.get(cat, set()):
                continue
            link = os.path.join(d, f"{alias}.svg")
            if os.path.exists(link) or os.path.islink(link):
                continue
            os.symlink(f"{hop}.svg", link)
            alias_count += 1

    # ---- populate per-size dirs (symlink to scalable by default)
    links = 0
    for cat in categories:
        sdir = os.path.join(theme_dir, "scalable", cat)
        for entry in sorted(os.listdir(sdir)):
            base = entry[:-4]
            for s in sizes:
                ddir = os.path.join(theme_dir, f"{s}x{s}", cat)
                os.makedirs(ddir, exist_ok=True)
                dst = os.path.join(ddir, f"{base}.svg")
                if not os.path.lexists(dst):
                    os.symlink(f"../../scalable/{cat}/{entry}", dst)
                    links += 1

    log(f"  xdg icon theme '{theme_name}': {total} icons, {alias_count} aliases, "
        f"{links} size symlinks across {len(categories)} categories")


# ================================================ VS Code file icon theme
def gen_vscode_file(out: str, papirus_root: str) -> None:
    m = load(ICONOGRAPHY, "icon_map.json")
    ft = m["vscode_file"]

    icons_dir = os.path.join(out, "fileicons", "icons")
    if os.path.isdir(icons_dir):
        shutil.rmtree(icons_dir)

    defs: dict[str, dict] = {}

    def define(def_id: str, papirus_cat: str, papirus_name: str) -> str | None:
        if def_id in defs:
            return def_id
        svg = read_papirus_svg(papirus_root, papirus_cat, papirus_name)
        if svg is None:
            warn(f"vscode icon '{def_id}': Papirus '{papirus_cat}/{papirus_name}' not found - skipped")
            return None
        write(os.path.join(icons_dir, f"{def_id}.svg"), recolor_svg(svg))
        defs[def_id] = {"iconPath": f"./icons/{def_id}.svg"}
        return def_id

    # ---- base file + folders (shared with XDG mimetypes/places)
    define("_file", "mimetypes", ft["file"])
    define("_folder", "places", ft["folder"])
    define("_folder_open", "places", ft["folderOpen"])

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
        "hidesExplorerArrows": False,
        "version": VERSION,
    }

    # ---- file extensions -> Papirus mimetype icons (shared with XDG)
    for ext, papirus_name in ft["fileExtensions"].items():
        did = define(f"ext_{ext.replace('.', '_')}", "mimetypes", papirus_name)
        if did:
            theme["fileExtensions"][ext] = did

    # ---- specific file names
    for name, papirus_name in ft["fileNames"].items():
        key = name.lower().replace(".", "_").replace("/", "_")
        did = define(f"name_{key}", "mimetypes", papirus_name)
        if did:
            theme["fileNames"][name] = did

    # ---- folder names -> Papirus folder icons (recoloured)
    for name, papirus_name in ft["folderNames"].items():
        did = define(f"dir_{name.strip('.').replace('/', '_') or 'dot'}",
                     "places", papirus_name)
        if did:
            theme["folderNames"][name] = did
    for name in ft.get("folderNamesExpanded", {}):
        theme["folderNamesExpanded"][name] = "_folder_open"

    # ---- language-id fallbacks
    lang_map = ft.get("languageIds", {})
    for lang, ext_key in lang_map.items():
        did = f"ext_{ext_key}" if not ext_key.startswith("name_") else ext_key
        if did in defs:
            theme["languageIds"][lang] = did

    write(os.path.join(out, "fileicons", "osiris-file-icons.json"),
          json.dumps(theme, indent=2) + "\n")
    log(f"  vscode file icons: {len(defs)} definitions, "
        f"{len(theme['fileExtensions'])} extensions, {len(theme['fileNames'])} names")


# ================================================================ main
def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    target, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)

    build_dir = os.environ.get("OSIRIS_BUILD_DIR",
                               os.path.join(ROOT, "build"))
    papirus_src = os.environ.get("OSIRIS_PAPIRUS_SRC",
                                 os.path.join(build_dir, "papirus-src"))

    if target in ("xdg", "all", "vscode-file"):
        ensure_papirus(papirus_src)

    papirus_root = os.path.join(papirus_src, "Papirus")

    if target in ("xdg", "all"):
        gen_xdg(out, papirus_root)
    if target in ("vscode-file", "all"):
        gen_vscode_file(out, papirus_root)
    if target not in ("xdg", "vscode-file", "all"):
        warn(f"unknown target '{target}'")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

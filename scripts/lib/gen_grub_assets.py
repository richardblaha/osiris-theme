#!/usr/bin/env python3
"""Generate the OSIRIS GRUB2 theme pixmaps (9-slice PNG sets) + menu icons.

GRUB's gfxmenu takes "styled boxes": for a style named ``foo`` it loads
``foo_c.png foo_n.png foo_e.png foo_s.png foo_w.png foo_nw.png foo_ne.png
foo_sw.png foo_se.png`` (center / edges / corners). This script paints flat,
rounded OSIRIS boxes from assets/tokens.json — no external art needed.

Requires Pillow.  Usage:
    gen_grub_assets.py <out_dir> [tokens.json]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    sys.exit("gen_grub_assets.py needs Pillow (pip install pillow)")

CORNER = 12          # px corner radius / slice size
EDGE = 8             # edge slice thickness


def hexrgba(h: str, a: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def styled_box(out_dir: Path, name: str, fill, border=None, radius=CORNER, bw=1):
    """Render a (2*radius+2) square rounded rect and slice it 3x3."""
    S = 2 * radius + 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=fill,
                        outline=border, width=bw if border else 0)
    slices = {
        "nw": (0, 0, radius, radius),
        "n":  (radius, 0, radius + 2, radius),
        "ne": (radius + 2, 0, S, radius),
        "w":  (0, radius, radius, radius + 2),
        "c":  (radius, radius, radius + 2, radius + 2),
        "e":  (radius + 2, radius, S, radius + 2),
        "sw": (0, radius + 2, radius, S),
        "s":  (radius, radius + 2, radius + 2, S),
        "se": (radius + 2, radius + 2, S, S),
    }
    for suf, box in slices.items():
        img.crop(box).save(out_dir / f"{name}_{suf}.png")


def bar(out_dir: Path, name: str, fill, radius=3):
    S = 2 * radius + 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=fill)
    styled_box(out_dir, name, fill, radius=radius)


ICONS = {
    "osiris":   [("poly", [(16, 3), (3, 24), (16, 29)], "#00f2fe"),
                 ("poly", [(16, 3), (29, 24), (16, 29)], "#ff2a85")],
    "linux":    [("circle", (16, 16, 11), "#00f2fe"), ("dot", (16, 16, 4), "#0d1117")],
    "gnu-linux": [("circle", (16, 16, 11), "#00f2fe"), ("dot", (16, 16, 4), "#0d1117")],
    "windows":  [("rect", (4, 4, 15, 15), "#79c0ff"), ("rect", (17, 4, 28, 15), "#79c0ff"),
                 ("rect", (4, 17, 15, 28), "#79c0ff"), ("rect", (17, 17, 28, 28), "#79c0ff")],
    "recovery": [("circle", (16, 16, 11), "#d29922"), ("dot", (16, 16, 4), "#0d1117")],
    "uefi-firmware": [("rect", (5, 9, 27, 23), "#8b949e"), ("rect", (9, 13, 23, 19), "#0d1117")],
    "memtest":  [("rect", (5, 7, 27, 25), "#3fb950"), ("rect", (9, 11, 23, 21), "#0d1117")],
}


def icon(out_dir: Path, name: str, ops):
    S = 32
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for op in ops:
        kind = op[0]
        color = hexrgba(op[-1])
        if kind == "poly":
            d.polygon(op[1], fill=color)
        elif kind == "circle":
            x, y, r = op[1]
            d.ellipse([x - r, y - r, x + r, y + r], outline=color, width=3)
        elif kind == "dot":
            x, y, r = op[1]
            d.ellipse([x - r, y - r, x + r, y + r], fill=color)
        elif kind == "rect":
            d.rectangle(op[1], fill=color)
    img.save(out_dir / f"{name}.png")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    icons_dir = out_dir / "icons"
    icons_dir.mkdir(exist_ok=True)

    tok = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[2] / "assets" / "tokens.json"
    data = json.loads(tok.read_text())
    t = data["themes"]["dark"]
    accent = data["accent"]["primary"]["dark"]
    surface = hexrgba(t["bg"]["sidebar"])
    field = hexrgba(t["bg"]["editor"])
    border = hexrgba(t["border"]["strong"])
    hover = hexrgba(t["bg"]["hover"])
    accent_rgba = hexrgba(accent)
    rose = hexrgba("#ff2a85")

    styled_box(out_dir, "item", (0, 0, 0, 0), radius=6)
    styled_box(out_dir, "selected_item", hexrgba(accent, 36), border=accent_rgba, radius=6)
    styled_box(out_dir, "terminal_box", surface, border=border, radius=10)
    styled_box(out_dir, "scrollbar_frame", (0, 0, 0, 0), radius=3)
    styled_box(out_dir, "scrollbar_thumb", border, radius=3)
    bar(out_dir, "progress_bar", field)
    bar(out_dir, "progress_highlight", rose)

    for name, ops in ICONS.items():
        icon(icons_dir, name, ops)

    print(f"GRUB assets -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate the OSIRIS Xcursor theme from design tokens (no source artwork)."""
from __future__ import annotations

import json
import os
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
TOKENS = json.loads((ROOT / "assets/tokens.json").read_text(encoding="utf-8"))
CYAN = TOKENS["accent"]["primary"]["dark"]
MAGENTA = TOKENS["accent"]["secondary"]["dark"]
INK = TOKENS["themes"]["dark"]["bg"]["titlebar"]
WHITE = TOKENS["themes"]["dark"]["text"]["primary"]
SIZES = (24, 32, 48)


def canvas(size: int):
    scale = 4
    image = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image), scale


def arrow(size: int, role: str) -> tuple[Image.Image, tuple[int, int]]:
    im, d, s = canvas(size)
    pts = [(2, 1), (2, 19), (7, 15), (11, 23), (15, 21), (11, 13), (18, 13)]
    pts = [(round(x * size / 24 * s), round(y * size / 24 * s)) for x, y in pts]
    d.polygon(pts, fill=CYAN, outline=INK, width=max(2, s))
    if role == "copy":
        d.ellipse((13*s*size//24, 2*s*size//24, 22*s*size//24, 11*s*size//24), fill=MAGENTA, outline=INK, width=s)
        d.line((15*s*size//24, 6*s*size//24, 20*s*size//24, 6*s*size//24), fill=WHITE, width=s)
        d.line((17.5*s*size//24, 3.5*s*size//24, 17.5*s*size//24, 8.5*s*size//24), fill=WHITE, width=s)
    return im.resize((size, size), Image.Resampling.LANCZOS), (2 * size // 24, 1 * size // 24)


def cross(size: int, role: str) -> tuple[Image.Image, tuple[int, int]]:
    im, d, s = canvas(size)
    c, w = size*s//2, max(s, size*s//16)
    color = MAGENTA if role == "cross" else CYAN
    d.line((c, 3*s, c, size*s-3*s), fill=INK, width=w+2*s)
    d.line((3*s, c, size*s-3*s, c), fill=INK, width=w+2*s)
    d.line((c, 3*s, c, size*s-3*s), fill=color, width=w)
    d.line((3*s, c, size*s-3*s, c), fill=color, width=w)
    return im.resize((size, size), Image.Resampling.LANCZOS), (size//2, size//2)


def beam(size: int, role: str) -> tuple[Image.Image, tuple[int, int]]:
    im, d, s = canvas(size)
    c = size*s//2
    d.line((c, 2*s, c, size*s-2*s), fill=INK, width=4*s)
    d.line((c, 2*s, c, size*s-2*s), fill=CYAN, width=2*s)
    d.line((c-5*s, 2*s, c+5*s, 2*s), fill=MAGENTA, width=2*s)
    d.line((c-5*s, size*s-2*s, c+5*s, size*s-2*s), fill=MAGENTA, width=2*s)
    return im.resize((size, size), Image.Resampling.LANCZOS), (size//2, size//2)


def hand(size: int, role: str) -> tuple[Image.Image, tuple[int, int]]:
    im, d, s = canvas(size)
    points = [(8,21),(6,13),(8,12),(10,15),(10,4),(12,3),(13,12),(14,7),(16,7),(16,13),(17,9),(19,9),(19,16),(16,22)]
    points = [(x*s*size//24, y*s*size//24) for x,y in points]
    d.polygon(points, fill=CYAN, outline=INK, width=s)
    return im.resize((size, size), Image.Resampling.LANCZOS), (11*size//24, 4*size//24)


def wait_cursor(size: int, role: str) -> tuple[Image.Image, tuple[int, int]]:
    im, d, s = canvas(size)
    box = (3*s, 3*s, (size-3)*s, (size-3)*s)
    d.ellipse(box, outline=INK, width=4*s)
    d.arc(box, -90, 80, fill=CYAN, width=2*s)
    d.arc(box, 90, 250, fill=MAGENTA, width=2*s)
    return im.resize((size, size), Image.Resampling.LANCZOS), (size//2, size//2)


def resize_cursor(size: int, role: str) -> tuple[Image.Image, tuple[int, int]]:
    im, d, s = canvas(size)
    c, lo, hi = size*s//2, 4*s, (size-4)*s
    if role == "vresize":
        line, heads = (c, lo, c, hi), [((c,lo),(c-4*s,lo+4*s)),((c,lo),(c+4*s,lo+4*s)),((c,hi),(c-4*s,hi-4*s)),((c,hi),(c+4*s,hi-4*s))]
    elif role in ("d1resize", "d2resize"):
        if role == "d1resize": line, ends = (lo, lo, hi, hi), ((lo,lo),(hi,hi))
        else: line, ends = (lo, hi, hi, lo), ((lo,hi),(hi,lo))
        heads = []
        for x,y in ends:
            sx = 1 if x == lo else -1; sy = 1 if y == lo else -1
            heads += [((x,y),(x+5*s*sx,y)),((x,y),(x,y+5*s*sy))]
    else:
        line, heads = (lo, c, hi, c), [((lo,c),(lo+4*s,c-4*s)),((lo,c),(lo+4*s,c+4*s)),((hi,c),(hi-4*s,c-4*s)),((hi,c),(hi-4*s,c+4*s))]
    for coords, width, color in ((line, 5*s, INK), (line, 2*s, CYAN)):
        d.line(coords, fill=color, width=width)
    for segment in heads:
        d.line((*segment[0], *segment[1]), fill=INK, width=5*s)
        d.line((*segment[0], *segment[1]), fill=MAGENTA, width=2*s)
    return im.resize((size, size), Image.Resampling.LANCZOS), (size//2, size//2)


RENDERERS = {"default": arrow, "copy": arrow, "cross": cross, "crosshair": cross,
             "text": beam, "pointer": hand, "wait": wait_cursor,
             "hresize": resize_cursor, "vresize": resize_cursor,
             "d1resize": resize_cursor, "d2resize": resize_cursor}


ALIASES = {
    "default": ("left_ptr", "arrow", "top_left_arrow"),
    "pointer": ("hand1", "hand2", "pointing_hand", "link"),
    "text": ("xterm", "ibeam", "text"),
    "wait": ("watch", "wait", "progress", "left_ptr_watch"),
    "crosshair": ("crosshair", "tcross", "cross"),
    "cross": ("not-allowed", "forbidden", "no-drop"),
    "copy": ("copy", "dnd-copy", "alias"),
    "hresize": ("ew-resize", "e-resize", "w-resize", "left_side", "right_side", "sb_h_double_arrow", "col-resize"),
    "vresize": ("ns-resize", "n-resize", "s-resize", "top_side", "bottom_side", "sb_v_double_arrow", "row-resize"),
    "d1resize": ("nwse-resize", "nw-resize", "se-resize", "top_left_corner", "bottom_right_corner"),
    "d2resize": ("nesw-resize", "ne-resize", "sw-resize", "top_right_corner", "bottom_left_corner"),
}


def xcursor(path: Path, role: str) -> None:
    frames = []
    for size in SIZES:
        image, hot = RENDERERS[role](size, role)
        pixels = []
        pixel_data = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
        for r, g, b, a in pixel_data:
            pixels.append((a << 24) | (r << 16) | (g << 8) | b)
        frames.append((size, hot, pixels))
    ntoc = len(frames)
    positions, pos = [], 16 + ntoc * 12
    for size, _, pixels in frames:
        positions.append(pos)
        pos += 36 + len(pixels) * 4
    with path.open("wb") as out:
        out.write(struct.pack("<4I", 0x72756358, 16, 0x00010000, ntoc))
        for (size, _, _), position in zip(frames, positions):
            out.write(struct.pack("<3I", 0xfffd0002, size, position))
        for size, (hx, hy), pixels in frames:
            out.write(struct.pack("<9I", 36, 0xfffd0002, size, 1, size, size, hx, hy, 50))
            out.write(struct.pack(f"<{len(pixels)}I", *pixels))


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/cursors/Osiris-Cursors")
    if out.exists():
        shutil.rmtree(out)
    cursors = out / "cursors"
    cursors.mkdir(parents=True)
    (out / "index.theme").write_text("[Icon Theme]\nName=Osiris Cursors\nComment=OSIRIS cyan/magenta cursor theme\nInherits=Adwaita\n", encoding="utf-8")
    for role, aliases in ALIASES.items():
        target = aliases[0]
        xcursor(cursors / target, role)
        for alias in aliases[1:]:
            os.symlink(target, cursors / alias)
    print(f"generated {out} ({len(ALIASES)} cursor designs, {sum(map(len, ALIASES.values()))} names)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

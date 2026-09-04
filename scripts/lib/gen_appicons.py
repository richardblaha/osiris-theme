#!/usr/bin/env python3
"""OSIRIS application-icon generator.

Turns the master OSIRIS mark (SVG) into the full set of desktop-application icon
formats that packagers expect but that a repo of vectors does not carry:

  win32              osiris.ico   — multi-size 16/24/32/48/64/128/256
  darwin             osiris.icns  — 16…512 + @2x (up to 1024 px)
  linux / electron   png/osiris-<n>.png for n in 16 32 48 64 128 256 512 1024
  linux hicolor      hicolor/<n>x<n>/apps/osiris.png (freedesktop layout)

Usage:
  scripts/lib/gen_appicons.py <out-dir> [source.svg]

Default source: vscode/icon.svg (the rounded-tile mark — reads well at 16 px and
already has the dark plate the other surfaces expect). Pass
assets/icons/osiris-logo.svg for the transparent glyph-only variant.

Rasteriser: rsvg-convert / inkscape / imagemagick / cairosvg (first found).
.ico / .icns need Pillow.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PNG_SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
HICOLOR_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]


def log(msg: str) -> None:
    print(f"\033[36m[osiris]\033[0m {msg}")


def warn(msg: str) -> None:
    print(f"\033[33m[osiris] warn:\033[0m {msg}", file=sys.stderr)


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _rasteriser():
    if have("rsvg-convert"):
        return lambda s, d, px: subprocess.run(
            ["rsvg-convert", "-w", str(px), "-h", str(px), "-o", d, s],
            check=True, capture_output=True)
    if have("inkscape"):
        return lambda s, d, px: subprocess.run(
            ["inkscape", s, "--export-type=png", f"--export-filename={d}",
             f"--export-width={px}", f"--export-height={px}"],
            check=True, capture_output=True)
    if have("convert"):
        return lambda s, d, px: subprocess.run(
            ["convert", "-background", "none", "-density", "384", "-resize",
             f"{px}x{px}", s, d], check=True, capture_output=True)
    try:
        import cairosvg  # noqa: F401
        return lambda s, d, px: __import__("cairosvg").svg2png(
            url=s, write_to=d, output_width=px, output_height=px)
    except ImportError:
        return None


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = argv[1]
    src = argv[2] if len(argv) > 2 else os.path.join(ROOT, "vscode", "icon.svg")
    if not os.path.isfile(src):
        warn(f"source SVG not found: {src}")
        return 1

    raster = _rasteriser()
    if raster is None:
        warn("no SVG rasteriser (need rsvg-convert / inkscape / imagemagick / cairosvg)")
        return 1

    png_dir = os.path.join(out, "png")
    os.makedirs(png_dir, exist_ok=True)

    made: dict[int, str] = {}
    for px in sorted(set(PNG_SIZES + ICO_SIZES + HICOLOR_SIZES)):
        dst = os.path.join(png_dir, f"osiris-{px}.png")
        raster(src, dst, px)
        made[px] = dst
    log(f"  png: {len(made)} sizes -> {os.path.relpath(png_dir, out)}/osiris-<n>.png")

    # freedesktop hicolor tree
    for px in HICOLOR_SIZES:
        ddir = os.path.join(out, "hicolor", f"{px}x{px}", "apps")
        os.makedirs(ddir, exist_ok=True)
        shutil.copyfile(made[px], os.path.join(ddir, "osiris.png"))
    scal = os.path.join(out, "hicolor", "scalable", "apps")
    os.makedirs(scal, exist_ok=True)
    shutil.copyfile(src, os.path.join(scal, "osiris.svg"))
    log(f"  hicolor: {len(HICOLOR_SIZES)} sizes + scalable/")

    try:
        from PIL import Image
    except ImportError:
        warn("Pillow missing — osiris.ico / osiris.icns not written")
        return 0

    ico = os.path.join(out, "osiris.ico")
    Image.open(made[256]).save(
        ico, format="ICO", sizes=[(s, s) for s in ICO_SIZES])
    log(f"  ico: {ICO_SIZES} -> {os.path.basename(ico)}")

    icns = os.path.join(out, "osiris.icns")
    base = Image.open(made[1024]).convert("RGBA")
    base.save(icns, format="ICNS")
    with Image.open(icns) as chk:
        got = sorted({s[0] for s in chk.info.get("sizes", [])})
    log(f"  icns: {got} -> {os.path.basename(icns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

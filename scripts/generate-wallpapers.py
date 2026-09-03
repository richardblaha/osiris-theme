#!/usr/bin/env python3
"""Rasterise the OSIRIS wallpapers and assemble the GNOME + KDE bundles.

Inputs  (repo):  assets/wallpapers/<family>/osiris-<family>-<day|night>.svg
                 assets/wallpapers/<family>/osiris-<family>.xml        (GNOME timeline template)
                 assets/wallpapers/<family>/kde-metadata.json          (KDE package template)
Outputs (build/wallpapers/):
    backgrounds/osiris/<family>/osiris-<family>-<day|night>-<WxH>.png
    gnome/<family>/osiris-<family>-<WxH>.xml
    gnome-background-properties/osiris.xml
    kde/Osiris-<Family>/metadata.json
    kde/Osiris-<Family>/contents/images/<WxH>.png        (day)
    kde/Osiris-<Family>/contents/images_dark/<WxH>.png    (night)

Rasteriser: rsvg-convert > inkscape > cairosvg (whichever is found).

Usage:  generate-wallpapers.py [--out build/wallpapers] [--resolutions 3840x2160,1920x1080]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOKENS = json.loads((REPO / "assets" / "tokens.json").read_text(encoding="utf-8"))
FAMILIES = ["abstract", "egypt"]


def find_rasteriser() -> str:
    if shutil.which("rsvg-convert"):
        return "rsvg"
    try:
        import cairosvg  # noqa: F401
        return "cairosvg"
    except ImportError:
        pass
    if shutil.which("magick") or shutil.which("convert"):
        return "magick"
    if shutil.which("inkscape"):
        return "inkscape"
    sys.exit("need one of: rsvg-convert, python-cairosvg, ImageMagick, inkscape")


def rasterise(kind: str, svg: Path, png: Path, w: int, h: int) -> None:
    svg, png = svg.resolve(), png.resolve()
    png.parent.mkdir(parents=True, exist_ok=True)
    if kind == "rsvg":
        subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h),
                        "-o", str(png), str(svg)], check=True)
    elif kind == "cairosvg":
        import cairosvg
        cairosvg.svg2png(url=str(svg), write_to=str(png),
                         output_width=w, output_height=h)
    elif kind == "magick":
        exe = shutil.which("magick") or shutil.which("convert")
        subprocess.run([exe, "-background", "none", "-density", "200",
                        str(svg), "-resize", f"{w}x{h}!", str(png)], check=True)
    else:  # inkscape
        subprocess.run(["inkscape", str(svg), "--export-type=png",
                        f"--export-filename={png}", f"--export-width={w}",
                        f"--export-height={h}"], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "build" / "wallpapers"))
    ap.add_argument("--resolutions",
                    default=",".join(TOKENS["wallpaper"]["resolutions"]))
    args = ap.parse_args()

    out = Path(args.out)
    resolutions = [r.strip() for r in args.resolutions.split(",") if r.strip()]
    kind = find_rasteriser()
    print(f"rasteriser: {kind}   resolutions: {resolutions}")

    bg_root = out / "backgrounds" / "osiris"
    gnome_root = out / "gnome"
    kde_root = out / "kde"
    props_dir = out / "gnome-background-properties"
    for d in (bg_root, gnome_root, kde_root, props_dir):
        d.mkdir(parents=True, exist_ok=True)

    props = ['<?xml version="1.0"?>',
             '<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">', "<wallpapers>"]

    for fam in FAMILIES:
        src = REPO / "assets" / "wallpapers" / fam
        timeline_tpl = (src / f"osiris-{fam}.xml").read_text(encoding="utf-8")
        pkg = kde_root / f"Osiris-{fam.capitalize()}"
        (pkg / "contents" / "images").mkdir(parents=True, exist_ok=True)
        (pkg / "contents" / "images_dark").mkdir(parents=True, exist_ok=True)
        meta = json.loads((src / "kde-metadata.json").read_text(encoding="utf-8"))
        meta.pop("$comment", None)
        (pkg / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n",
                                           encoding="utf-8")

        for mode in ("day", "night"):
            svg = src / f"osiris-{fam}-{mode}.svg"
            for res in resolutions:
                w, h = (int(x) for x in res.split("x"))
                png = bg_root / fam / f"osiris-{fam}-{mode}-{res}.png"
                rasterise(kind, svg, png, w, h)
                kde_sub = "images" if mode == "day" else "images_dark"
                shutil.copyfile(png, pkg / "contents" / kde_sub / f"{res}.png")

        for res in resolutions:
            xml = (gnome_root / fam / f"osiris-{fam}-{res}.xml")
            xml.parent.mkdir(parents=True, exist_ok=True)
            xml.write_text(timeline_tpl.replace("@RES@", res), encoding="utf-8")

        # gnome-background-properties entries: the two statics + the dynamic
        default_res = resolutions[0]
        for mode, label in (("day", "Day"), ("night", "Night")):
            props += [
                "  <wallpaper deleted=\"false\">",
                f"    <name>Osiris {fam.capitalize()} — {label}</name>",
                f"    <filename>/usr/share/backgrounds/osiris/{fam}/osiris-{fam}-{mode}-{default_res}.png</filename>",
                "    <options>zoom</options>",
                "  </wallpaper>",
            ]
        props += [
            "  <wallpaper deleted=\"false\">",
            f"    <name>Osiris {fam.capitalize()} — Dynamic</name>",
            f"    <filename>/usr/share/backgrounds/osiris/gnome/{fam}/osiris-{fam}-{default_res}.xml</filename>",
            "    <options>zoom</options>",
            "  </wallpaper>",
        ]
        # stage the dynamic XMLs next to the PNGs too (packaging installs both trees)
        for res in resolutions:
            dst = bg_root / "gnome" / fam / f"osiris-{fam}-{res}.xml"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(timeline_tpl.replace("@RES@", res), encoding="utf-8")

    props.append("</wallpapers>")
    (props_dir / "osiris.xml").write_text("\n".join(props) + "\n", encoding="utf-8")

    print(f"wallpapers -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

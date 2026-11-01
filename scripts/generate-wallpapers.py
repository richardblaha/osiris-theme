#!/usr/bin/env python3
"""Rasterise/resize the OSIRIS wallpapers and assemble the GNOME + KDE bundles.

Inputs  (repo):  assets/wallpapers/<family>/osiris-<family>-<design>-<dark|light>.(svg|png|jpg)
                       — one master per design and variant (dark = night, light = day)
                 assets/wallpapers/<family>/osiris-<family>.xml        (GNOME timeline template, @NAME@ @RES@)
                 assets/wallpapers/<family>/kde-metadata.json          (KDE package template, @NAME@ @ID@)
Outputs (build/wallpapers/), JPEG q88 to keep the packages small:
    backgrounds/osiris/<family>/osiris-<family>-<design>-<variant>-<WxH>.jpg
    backgrounds/osiris/gnome/<family>/osiris-<family>-<design>-<WxH>.xml
    gnome/<family>/osiris-<family>-<design>-<WxH>.xml
    gnome-background-properties/osiris.xml
    kde/Osiris-<Family>-<Design>/metadata.json
    kde/Osiris-<Family>-<Design>/contents/images/<WxH>.jpg        (light)
    kde/Osiris-<Family>-<Design>/contents/images_dark/<WxH>.jpg   (dark)

Rasteriser: rsvg-convert > cairosvg > ImageMagick > inkscape for SVG sources;
Pillow (or ImageMagick) resizes PNG/JPG masters.

Usage:  generate-wallpapers.py [--out build/wallpapers] [--resolutions 1920x1080,1366x768]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOKENS = json.loads((REPO / "assets" / "tokens.json").read_text(encoding="utf-8"))
VARIANTS = ("light", "dark")          # light = day, dark = night

DESIGN_RE = re.compile(r"^osiris-(?P<fam>[a-z0-9]+)-(?P<name>.+)-(?P<variant>dark|light)\.(?:svg|png|jpe?g)$")


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
    return "none"


def have_pil() -> bool:
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def render(src: Path, out: Path, w: int, h: int, kind: str) -> None:
    """Produce a JPEG at exactly w x h from an SVG (rasterise) or PNG/JPG (resize)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    png = out if out.suffix.lower() == ".png" else out.with_suffix(".png")
    if src.suffix.lower() == ".svg":
        if kind == "rsvg":
            subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h),
                            "-o", str(png), str(src)], check=True)
        elif kind == "cairosvg":
            import cairosvg
            cairosvg.svg2png(url=str(src), write_to=str(png),
                             output_width=w, output_height=h)
        elif kind == "magick":
            exe = shutil.which("magick") or shutil.which("convert")
            subprocess.run([exe, "-background", "none", "-density", "200",
                            str(src), "-resize", f"{w}x{h}!", str(png)], check=True)
        else:
            subprocess.run(["inkscape", str(src), "--export-type=png",
                            f"--export-filename={png}", f"--export-width={w}",
                            f"--export-height={h}"], check=True)
    else:
        if have_pil():
            from PIL import Image
            with Image.open(src) as im:
                im = im.convert("RGB")
                # cover: scale to fill, center-crop to exactly w x h
                scale = max(w / im.width, h / im.height)
                im = im.resize((max(w, round(im.width * scale)),
                                max(h, round(im.height * scale))), Image.LANCZOS)
                x0 = (im.width - w) // 2
                y0 = (im.height - h) // 2
                im.crop((x0, y0, x0 + w, y0 + h)).save(png, optimize=True)
        elif kind == "magick":
            exe = shutil.which("magick") or shutil.which("convert")
            subprocess.run([exe, str(src), "-resize", f"{w}x{h}^", "-gravity", "center",
                            "-extent", f"{w}x{h}", str(png)], check=True)
        else:
            sys.exit("need Pillow or ImageMagick to resize PNG/JPG wallpaper masters")
    if out.suffix.lower() == ".jpg":
        if have_pil():
            from PIL import Image
            with Image.open(png) as im:
                im.convert("RGB").save(out, "JPEG", quality=88, optimize=True)
            png.unlink(missing_ok=True)
        elif kind == "magick":
            exe = shutil.which("magick") or shutil.which("convert")
            subprocess.run([exe, str(png), "-quality", "88", str(out)], check=True)
            png.unlink(missing_ok=True)
        else:
            sys.exit("need Pillow or ImageMagick to write JPEG wallpapers")


def discover(src_root: Path) -> dict[str, list[str]]:
    """family -> sorted design names, from the master file names."""
    fams: dict[str, set[str]] = {}
    for f in sorted(src_root.glob("*/*")):
        m = DESIGN_RE.match(f.name)
        if m and f.parent.name == m.group("fam"):
            fams.setdefault(f.parent.name, set()).add(m.group("name"))
    return {k: sorted(v) for k, v in sorted(fams.items())}


def timed_collection(fam: str, designs: list[str], variant: str, phase: int,
                     resolution: str) -> str:
    """A 24-hour GNOME slideshow using four same-variant OSIRIS designs."""
    selected = [designs[(phase + i * 2) % len(designs)] for i in range(4)]
    base = f"/usr/share/backgrounds/osiris/{fam}/osiris-{fam}"
    lines = [
        '<?xml version="1.0"?>', '<background>', '  <starttime>',
        '    <year>2026</year><month>01</month><day>01</day>',
        f'    <hour>{phase * 2:02d}</hour><minute>00</minute><second>00</second>',
        '  </starttime>',
    ]
    for i, name in enumerate(selected):
        nxt = selected[(i + 1) % len(selected)]
        current_path = f"{base}-{name}-{variant}-{resolution}.jpg"
        next_path = f"{base}-{nxt}-{variant}-{resolution}.jpg"
        lines += [
            '  <static><duration>19800.0</duration>',
            f'    <file>{current_path}</file></static>',
            '  <transition type="overlay"><duration>1800.0</duration>',
            f'    <from>{current_path}</from><to>{next_path}</to></transition>',
        ]
    lines.append('</background>')
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "build" / "wallpapers"))
    ap.add_argument("--resolutions",
                    default=",".join(TOKENS["wallpaper"]["resolutions"]))
    args = ap.parse_args()

    out = Path(args.out)
    resolutions = [r.strip() for r in args.resolutions.split(",") if r.strip()]
    kind = find_rasteriser()
    print(f"rasteriser: {kind or 'pil only'}   resolutions: {resolutions}")

    src_root = REPO / "assets" / "wallpapers"
    families = discover(src_root)
    if not families:
        sys.exit(f"no wallpaper families under {src_root}")

    bg_root = out / "backgrounds" / "osiris"
    gnome_root = out / "gnome"
    kde_root = out / "kde"
    props_dir = out / "gnome-background-properties"
    for d in (bg_root, gnome_root, kde_root, props_dir):
        d.mkdir(parents=True, exist_ok=True)

    props = ['<?xml version="1.0"?>',
             '<!DOCTYPE wallpapers SYSTEM "gnome-wp-list.dtd">', "<wallpapers>"]
    default_res = resolutions[0]

    for fam, designs in families.items():
        src = src_root / fam
        timeline_tpl = (src / f"osiris-{fam}.xml").read_text(encoding="utf-8")
        meta_tpl = json.loads((src / "kde-metadata.json").read_text(encoding="utf-8"))
        meta_tpl.pop("$comment", None)
        fam_title = fam.capitalize()

        for name in designs:
            title = name.split("-", 1)[1].capitalize() if "-" in name else name.capitalize()
            pkg_id = title
            pkg = kde_root / f"Osiris-{fam_title}-{pkg_id}"
            (pkg / "contents" / "images").mkdir(parents=True, exist_ok=True)
            (pkg / "contents" / "images_dark").mkdir(parents=True, exist_ok=True)
            meta = json.loads(json.dumps(meta_tpl).replace("@NAME@", title).replace("@ID@", pkg_id))
            (pkg / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n",
                                               encoding="utf-8")

            for variant in VARIANTS:
                masters = [src / f"osiris-{fam}-{name}-{variant}{ext}"
                           for ext in (".svg", ".png", ".jpg", ".jpeg")
                           if (src / f"osiris-{fam}-{name}-{variant}{ext}").exists()]
                if not masters:
                    sys.exit(f"missing master for {fam}/{name}/{variant}")
                master = masters[0]
                for res in resolutions:
                    w, h = (int(x) for x in res.split("x"))
                    jpg = bg_root / fam / f"osiris-{fam}-{name}-{variant}-{res}.jpg"
                    render(master, jpg, w, h, kind)
                    kde_sub = "images" if variant == "light" else "images_dark"
                    shutil.copyfile(jpg, pkg / "contents" / kde_sub / f"{res}.jpg")

            for res in resolutions:
                xml_text = (timeline_tpl
                            .replace("@NAME@", name)
                            .replace("@RES@", res))
                for root in (gnome_root, bg_root / "gnome"):
                    xml = root / fam / f"osiris-{fam}-{name}-{res}.xml"
                    xml.parent.mkdir(parents=True, exist_ok=True)
                    xml.write_text(xml_text, encoding="utf-8")

            # gnome-background-properties: static light + static dark + dynamic
            for variant, label in (("light", "Light"), ("dark", "Dark")):
                props += [
                    "  <wallpaper deleted=\"false\">",
                    f"    <name>Osiris {fam_title} {title} — {label}</name>",
                    f"    <filename>/usr/share/backgrounds/osiris/{fam}/osiris-{fam}-{name}-{variant}-{default_res}.jpg</filename>",
                    "    <options>zoom</options>",
                    "  </wallpaper>",
                ]
            props += [
                "  <wallpaper deleted=\"false\">",
                f"    <name>Osiris {fam_title} {title} — Dynamic</name>",
                f"    <filename>/usr/share/backgrounds/osiris/gnome/{fam}/osiris-{fam}-{name}-{default_res}.xml</filename>",
                "    <options>zoom</options>",
                "  </wallpaper>",
            ]

        # Three time-changing collections for each colour-scheme variant.
        # They cycle through four existing masters and never cross from dark to
        # light, so selecting a theme-specific collection remains predictable.
        for variant, label in (("dark", "Dark"), ("light", "Light")):
            for phase in range(3):
                rel = f"osiris-{fam}-{variant}-animated-{phase + 1}-{default_res}.xml"
                xml_text = timed_collection(fam, designs, variant, phase, default_res)
                for root in (gnome_root / fam, bg_root / "gnome" / fam):
                    root.mkdir(parents=True, exist_ok=True)
                    (root / rel).write_text(xml_text, encoding="utf-8")
                props += [
                    "  <wallpaper deleted=\"false\">",
                    f"    <name>Osiris {fam_title} — {label} Animated {phase + 1}</name>",
                    f"    <filename>/usr/share/backgrounds/osiris/gnome/{fam}/{rel}</filename>",
                    "    <options>zoom</options>",
                    "  </wallpaper>",
                ]

    props.append("</wallpapers>")
    (props_dir / "osiris.xml").write_text("\n".join(props) + "\n", encoding="utf-8")

    print(f"wallpapers -> {out}  ({sum(len(d) for d in families.values())} designs x {len(VARIANTS)} variants)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build lightweight wallpaper previews and docs/preview/wallpapers.js."""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets/wallpapers"
OUT = ROOT / "docs/preview/wallpapers"
DATA = ROOT / "docs/preview/wallpapers.js"
PATTERN = re.compile(r"osiris-(?P<family>[^-]+)-(?P<design>.+)-(?P<variant>dark|light)\.(?:png|jpe?g)$")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    static = []
    by_family: dict[str, dict[str, dict[str, str]]] = {}
    for source in sorted(SRC.glob("*/*")):
        match = PATTERN.fullmatch(source.name)
        if not match:
            continue
        family, design, variant = (match.group(k) for k in ("family", "design", "variant"))
        target = OUT / f"{family}-{design}-{variant}.jpg"
        with Image.open(source) as image:
            image.convert("RGB").resize((640, 360), Image.Resampling.LANCZOS).save(
                target, "JPEG", quality=78, optimize=True)
        url = f"wallpapers/{target.name}"
        static.append({"family": family, "design": design, "variant": variant, "src": url})
        by_family.setdefault(family, {}).setdefault(design, {})[variant] = url

    animated = []
    for family, designs_map in sorted(by_family.items()):
        designs = sorted(designs_map)
        for variant in ("dark", "light"):
            for phase in range(3):
                selected = [designs[(phase + i * 2) % len(designs)] for i in range(4)]
                animated.append({
                    "family": family, "variant": variant, "name": f"Animated {phase + 1}",
                    "frames": [designs_map[name][variant] for name in selected],
                })
    payload = {"static": static, "animated": animated}
    DATA.write_text("/* GENERATED — do not edit. */\nwindow.OSIRIS_WALLPAPERS = "
                    + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"gen_preview_wallpapers: {len(static)} static + {len(animated)} animated")


if __name__ == "__main__":
    main()

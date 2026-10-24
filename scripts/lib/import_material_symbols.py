#!/usr/bin/env python3
"""Extract official Material Symbols Rounded outlines into OSIRIS source JSON.

Input is Google's official variable TTF + codepoints file. The font is pinned at
wght=300, GRAD=0, opsz=24, FILL=0. Existing local glyph ids are mapped to
official ligature names; ids without an upstream equivalent remain custom.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "build/material-design-icons/variablefont"
FONT_NAME = "MaterialSymbolsRounded[FILL,GRAD,opsz,wght].ttf"
CODEPOINTS_NAME = "MaterialSymbolsRounded[FILL,GRAD,opsz,wght].codepoints"


def compact_path(path: str) -> str:
    def number(match: re.Match[str]) -> str:
        value = round(float(match.group()), 4)
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return "0" if text in ("-0", "") else text
    return re.sub(r"-?\d+\.\d+", number, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--revision", default="unknown")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "iconography/material_symbols.json")
    args = parser.parse_args()

    local = json.loads((ROOT / "iconography/glyphs.json").read_text())["glyphs"]
    aliases = json.loads((ROOT / "iconography/material_map.json").read_text())
    aliases = {k: v for k, v in aliases.items() if not k.startswith("$")}
    codepoints = dict(line.split() for line in
                      (args.source / CODEPOINTS_NAME).read_text().splitlines() if line.strip())

    font = TTFont(args.source / FONT_NAME)
    font = instantiateVariableFont(font, {
        "wght": 300, "GRAD": 0, "opsz": 24, "FILL": 0,
    }, inplace=False)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    units = font["head"].unitsPerEm
    scale = 24 / units

    extracted = {}
    missing = []
    for local_name in local:
        symbol_name = aliases.get(local_name, local_name.replace("-", "_"))
        if symbol_name not in codepoints:
            missing.append(local_name)
            continue
        glyph_name = cmap.get(int(codepoints[symbol_name], 16))
        if not glyph_name:
            missing.append(local_name)
            continue
        pen = SVGPathPen(glyph_set)
        transformed = TransformPen(pen, (scale, 0, 0, -scale, 0, 24))
        glyph_set[glyph_name].draw(transformed)
        extracted[local_name] = {
            "materialSymbol": symbol_name,
            "d": compact_path(pen.getCommands()),
        }

    result = {
        "$comment": "Extracted from Google's official Material Symbols Rounded variable font; do not hand-edit.",
        "source": "https://github.com/google/material-design-icons",
        "revision": args.revision,
        "license": "Apache-2.0",
        "axes": {"style": "Rounded", "wght": 300, "GRAD": 0, "opsz": 24, "FILL": 0},
        "glyphs": extracted,
        "customGlyphs": missing,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"material-symbols: {len(extracted)} official, {len(missing)} custom -> {args.output}")


if __name__ == "__main__":
    main()

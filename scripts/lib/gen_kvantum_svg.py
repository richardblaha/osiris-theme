#!/usr/bin/env python3
"""Generate a complete, valid Kvantum SVG for an OSIRIS variant.

Kvantum renders every widget element from an SVG whose object ids follow a fixed
naming scheme. For a *frame* element ``X`` it needs the nine slices
``X-top X-bottom X-left X-right X-topleft X-topright X-bottomleft X-bottomright``
and an interior rect ``X``. This script emits simple flat / rounded rects for
every element the OsirisDark/OsirisLight .kvconfig references, coloured from
assets/tokens.json. It is intentionally minimalist (flat design, matches the
preview page) rather than trying to reproduce a gradient-heavy stock theme.

Usage:
    gen_kvantum_svg.py <dark|light> <out.svg> [tokens.json]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

FRAME = 8          # slice thickness in px
TILE = 48          # interior tile size


def palette(variant: str, tokens: dict) -> dict:
    t = tokens["themes"][variant]
    acc = tokens["accent"]["primary"][variant]
    sec = tokens["accent"]["secondary"][variant]
    return {
        "button": t["bg"]["input"],
        "button_hover": t["bg"]["hover"],
        "button_pressed": acc,
        "button_toggled": acc,
        "button_default_border": acc,
        "lineedit": t["bg"]["input"],
        "lineedit_border": t["border"]["strong"],
        "lineedit_focus_border": acc,
        "menu": t["bg"]["sidebar"],
        "menu_border": t["border"]["strong"],
        "menuitem": "none",
        "menuitem_selected": _soft(acc),
        "tooltip": t["bg"]["sidebar"],
        "tooltip_border": t["border"]["strong"],
        "tab": "none",
        "tab_selected": t["bg"]["tabActive"],
        "tab_accent": acc,
        "progress": sec,
        "progressbar_trough": t["bg"]["input"],
        "slider_groove": t["border"]["strong"],
        "slider_handle": acc,
        "focus": _soft(acc),
        "group_border": t["border"]["subtle"],
        "window": t["bg"]["sidebar"],
        "spin": t["text"]["secondary"],
    }


def _soft(hex_: str) -> str:
    return hex_ + "26"  # ~15% alpha


def rrect(x, y, w, h, fill, rx=3, stroke="none", sw=0, oid=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke != "none" else ""
    i = f' id="{oid}"' if oid else ""
    return f'  <rect{i} x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>'


def frame_slices(name, x, y, fill, stroke="none", sw=0):
    """Emit the 9 Kvantum frame slices for element *name* around a TILE box."""
    out = []
    f, T = FRAME, TILE
    # corners
    corners = {
        "topleft": (x, y), "topright": (x + f + T, y),
        "bottomleft": (x, y + f + T), "bottomright": (x + f + T, y + f + T),
    }
    for suf, (cx, cy) in corners.items():
        out.append(rrect(cx, cy, f, f, fill, rx=2, stroke=stroke, sw=sw, oid=f"{name}-{suf}"))
    # edges
    out.append(rrect(x + f, y, T, f, fill, rx=0, stroke=stroke, sw=sw, oid=f"{name}-top"))
    out.append(rrect(x + f, y + f + T, T, f, fill, rx=0, stroke=stroke, sw=sw, oid=f"{name}-bottom"))
    out.append(rrect(x, y + f, f, T, fill, rx=0, stroke=stroke, sw=sw, oid=f"{name}-left"))
    out.append(rrect(x + f + T, y + f, f, T, fill, rx=0, stroke=stroke, sw=sw, oid=f"{name}-right"))
    return out


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    variant = sys.argv[1]
    out = Path(sys.argv[2])
    tok_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parents[2] / "assets" / "tokens.json"
    tokens = json.loads(tok_path.read_text())
    p = palette(variant, tokens)

    W, H = 2000, 1200
    body: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'  <rect width="{W}" height="{H}" fill="none"/>',
    ]

    # Lay elements out on a grid; positions are irrelevant to Kvantum (it looks
    # up by id) but must not overlap so the renderer picks them up cleanly.
    col = 0
    row = 0

    def place():
        nonlocal col, row
        x = 20 + col * (2 * FRAME + TILE + 24)
        y = 20 + row * (2 * FRAME + TILE + 24)
        col += 1
        if col > 12:
            col = 0
            row += 1
        return x, y

    frame_elems = [
        ("button", p["button"], p["lineedit_border"], 1),
        ("button-pressed", p["button_pressed"], "none", 0),
        ("button-toggled", p["button_toggled"], "none", 0),
        ("button-default", p["button"], p["button_default_border"], 2),
        ("lineedit", p["lineedit"], p["lineedit_border"], 1),
        ("lineedit-focused", p["lineedit"], p["lineedit_focus_border"], 2),
        ("menu", p["menu"], p["menu_border"], 1),
        ("menuitem", p["menuitem"], "none", 0),
        ("menuitem-selected", p["menuitem_selected"], "none", 0),
        ("tooltip", p["tooltip"], p["tooltip_border"], 1),
        ("tab", p["tab"], "none", 0),
        ("tab-selected", p["tab_selected"], p["tab_accent"], 2),
        ("group", "none", p["group_border"], 1),
        ("slider-groove", p["slider_groove"], "none", 0),
        ("progress", p["progress"], "none", 0),
        ("focus", p["focus"], "none", 0),
    ]
    for name, fill, stroke, sw in frame_elems:
        x, y = place()
        body += frame_slices(name, x, y, fill if fill != "none" else "#00000000", stroke, sw)
        body.append(rrect(x + FRAME, y + FRAME, TILE, TILE,
                          fill if fill != "none" else "#00000000", rx=3,
                          stroke=stroke, sw=sw, oid=name))

    # interior-only elements
    for name, fill in [
        ("progressbar", p["progress"]),
        ("window", p["window"]),
    ]:
        x, y = place()
        body.append(rrect(x, y, TILE + 2 * FRAME, TILE + 2 * FRAME, fill, rx=3, oid=name))

    # indicator glyphs (spin arrows, slider handle)
    x, y = place()
    body.append(f'  <circle id="slider-handle" cx="{x + 24}" cy="{y + 24}" r="12" fill="{p["slider_handle"]}"/>')
    x, y = place()
    body.append(f'  <path id="spin" d="M{x+8} {y+22} l8 -10 l8 10 z m0 12 l8 10 l8 -10 z" fill="{p["spin"]}"/>')

    body.append("</svg>")
    out.write_text("\n".join(body) + "\n")
    print(f"wrote {out} ({variant})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

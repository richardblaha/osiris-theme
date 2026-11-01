#!/usr/bin/env python3
"""Derive monochrome rounded OSIRIS SVG bodies from Papirus artwork.

Names and aliases remain separate, while identical Papirus source files share
one compact source body.  The generated data is GPL-3.0-only because it is an
adaptation of Papirus; the surrounding generator remains MIT licensed.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = ("actions", "apps", "categories", "devices", "emblems",
              "mimetypes", "places", "status")
ALLOWED = {"g", "path", "circle", "ellipse", "rect", "polygon", "polyline", "line"}
GEOMETRY = {"d", "cx", "cy", "r", "rx", "ry", "x", "y", "x1", "y1", "x2", "y2",
            "width", "height", "points", "transform", "fill-rule", "clip-rule"}
SOURCE_SUBSTITUTIONS = {
    "ai.lmstudio.lm-studio": "studio", "app.freelens.Freelens": "kontena-lens",
    "claude-desktop": "internet-chat", "io.github.totoshko88.RustConn": "rustdesk",
    "io.trezor.suite": "org.featherwallet.Feather", "net.nokyan.Resources": "gnome-system-monitor",
    "org.gnome.BrowserConnector": "chromium-browser", "org.gnome.Evolution-alarm-notify": "evolution-calendar",
    "org.gnome.Settings-mobile-network-symbolic": "network-cellular-signal-excellent-symbolic",
    "org.gnome.Settings-privacy-symbolic": "preferences-system-privacy-symbolic",
    "org.gnome.Settings-system-symbolic": "preferences-system-symbolic",
    "org.gnome.Settings-wellbeing-symbolic": "preferences-system-parental-controls-symbolic",
    "org.gnome.Tecla": "org.gnome.Settings-keyboard-symbolic",
    "org.gnome.goa-daemon-symbolic": "org.gnome.Settings-online-accounts-symbolic",
    "msedge-aghbiahbpaijignceidepookljebhfak-Default": "google-drive",
    "msedge-fmgjjmmmlfnkbppncabfkddbjimcfncm-Default": "gmail",
    "msedge-hpkkadlgbdkiimnjhfolkbcmpbmedpja-Default": "internet-chat",
    "msedge-kadndpdhfiaigidpmcgmgabmbcjnjbgn-Default": "teams",
}
NEGATIVE_WORDS = ("disabled", "inactive", "offline", "muted", "hidden", "closed",
                  "unset", "unrated", "none", "stopped", "missing", "deselect")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def style_map(element: ET.Element) -> dict[str, str]:
    result = {}
    for declaration in element.attrib.get("style", "").split(";"):
        if ":" in declaration:
            key, value = declaration.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def sanitize(element: ET.Element, scale: float) -> ET.Element | None:
    tag = local(element.tag)
    if tag not in ALLOWED:
        return None
    style = style_map(element)
    # Opacity is deliberately discarded: Papirus uses low opacity both for
    # shadows and for the actual "disabled" artwork. In the monochrome OSIRIS
    # adaptation every retained contour is drawn at full strength.
    out = ET.Element(tag)
    for key, value in element.attrib.items():
        key = local(key)
        if key in GEOMETRY:
            out.set(key, value)
    if tag == "g":
        for child in element:
            clean = sanitize(child, scale)
            if clean is not None:
                out.append(clean)
        return out if len(out) else None

    fill = style.get("fill", element.attrib.get("fill", "#000"))
    stroke = style.get("stroke", element.attrib.get("stroke", "none"))
    if fill == "none":
        out.set("fill", "none")
        out.set("stroke", "currentColor")
        width = style.get("stroke-width", element.attrib.get("stroke-width", str(1.6 / scale)))
        out.set("stroke-width", width)
    else:
        out.set("fill", "currentColor")
        # A small same-colour round stroke removes Papirus' sharp micro-corners
        # without changing the recognisable silhouette.
        out.set("stroke", "currentColor")
        out.set("stroke-width", str(round(0.45 / scale, 4)))
    if stroke != "none" and fill != "none":
        out.set("stroke", "currentColor")
    out.set("stroke-linecap", "round")
    out.set("stroke-linejoin", "round")
    return out


def source_svg(path: Path) -> tuple[str, str] | None:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return None
    view_box = root.attrib.get("viewBox")
    if not view_box:
        def number(value: str) -> str:
            return re.sub(r"[^0-9.].*$", "", value) or "64"
        view_box = f"0 0 {number(root.attrib.get('width', '64'))} {number(root.attrib.get('height', '64'))}"
    numbers = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", view_box)]
    scale = 20.0 / max(numbers[2:4]) if len(numbers) >= 4 else 20.0 / 64.0
    group = ET.Element("g")
    for child in root:
        clean = sanitize(child, scale)
        if clean is not None:
            group.append(clean)
    if not len(group):
        return None
    body = "".join(ET.tostring(child, encoding="unicode", short_empty_elements=True)
                   for child in group)
    return view_box, body


def related_names(name: str) -> list[tuple[str, bool]]:
    """Papirus names to use when an alias is intentionally represented negatively."""
    result = []
    direct = SOURCE_SUBSTITUTIONS.get(name)
    if direct:
        result.append((direct, False))
    clean = name.removesuffix("-symbolic")
    for word in NEGATIVE_WORDS:
        if word in clean:
            candidate = re.sub(rf"[-_]?{re.escape(word)}[-_]?", "-", clean).strip("-_")
            result += [(candidate, True), (candidate + "-symbolic", True)]
    result += [(clean, False), (clean + "-symbolic", False)]
    return result


def slash_overlay(view_box: str) -> str:
    nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", view_box)]
    x, y, w, h = nums[:4]
    return (f'<path d="M{x + w * .18:g} {y + h * .18:g}L{x + w * .82:g} {y + h * .82:g}" '
            f'fill="none" stroke="currentColor" stroke-width="{max(w, h) * .075:g}" '
            'stroke-linecap="round" stroke-linejoin="round"/>')


def priority(path: Path, category: str) -> tuple[int, int, str]:
    parts = path.parts
    category_penalty = 0 if category in parts else 1
    size = next((p for p in parts if re.fullmatch(r"\d+x\d+", p)), "0x0")
    px = int(size.split("x")[0])
    return category_penalty, abs(64 - px), str(path)


def main() -> int:
    papirus = Path(sys.argv[1] if len(sys.argv) > 1 else "/usr/share/icons/Papirus")
    output = Path(sys.argv[2] if len(sys.argv) > 2 else ROOT / "iconography/papirus_derived.json.gz")
    revision = sys.argv[3] if len(sys.argv) > 3 else "system-installed"
    catalog = json.loads((ROOT / "iconography/papirus_catalog.json").read_text(encoding="utf-8"))
    candidates: dict[str, list[Path]] = {}
    for path in papirus.rglob("*.svg"):
        candidates.setdefault(path.stem, []).append(path)

    sources: dict[str, dict[str, str]] = {}
    icons: dict[str, dict[str, str]] = {category: {} for category in CATEGORIES}
    missing = []
    for category in CATEGORIES:
        names = set(catalog["icons"].get(category, []))
        if category == "status":
            names.update(catalog.get("symbolic", []))
        for name in sorted(names):
            options = candidates.get(name, [])
            negative = False
            if not options:
                for related, add_slash in related_names(name):
                    if candidates.get(related):
                        options = candidates[related]
                        negative = add_slash
                        break
            if not options:
                missing.append(f"{category}/{name}")
                continue
            derived = None
            for path in sorted(options, key=lambda p: priority(p, category)):
                derived = source_svg(path.resolve())
                if derived:
                    break
            if not derived:
                missing.append(f"{category}/{name}")
                continue
            view_box, body = derived
            if negative:
                body += slash_overlay(view_box)
            digest = hashlib.sha256((view_box + body).encode()).hexdigest()[:16]
            sources.setdefault(digest, {"viewBox": view_box, "body": body})
            icons[category][name] = digest

    payload = {
        "$comment": "GPL-3.0-only derived artwork from Papirus, normalized to monochrome rounded OSIRIS geometry.",
        "sourceRevision": revision,
        "license": "GPL-3.0-only",
        "sources": sources,
        "icons": icons,
        "missing": missing,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output, "wt", encoding="utf-8", compresslevel=9) as stream:
        json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {output}: {sum(map(len, icons.values()))} names, {len(sources)} derived drawings, {len(missing)} missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

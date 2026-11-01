#!/usr/bin/env python3
"""Snapshot Papirus icon names and locally installed desktop icon IDs.

The resulting JSON contains names only; no Papirus artwork is copied.  OSIRIS
renders every name from its Material Symbols Rounded source in gen_icons.py.
"""
from __future__ import annotations

import configparser
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = {"actions", "apps", "categories", "devices", "emblems",
              "mimetypes", "places", "status"}


def icon_name(path: Path) -> str | None:
    return path.stem if path.suffix.lower() in {".svg", ".png", ".xpm"} else None


def desktop_icons() -> set[str]:
    result: set[str] = set()
    roots = (
        Path("/usr/share/applications"),
        Path.home() / ".local/share/applications",
        Path("/var/lib/flatpak/exports/share/applications"),
        Path.home() / ".local/share/flatpak/exports/share/applications",
    )
    for root in roots:
        if not root.is_dir():
            continue
        for desktop in root.glob("*.desktop"):
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                parser.read(desktop, encoding="utf-8")
                value = parser.get("Desktop Entry", "Icon", fallback="").strip()
            except (configparser.Error, OSError, UnicodeError):
                continue
            if value and not os.path.isabs(value):
                result.add(value.rsplit(".", 1)[0] if value.lower().endswith((".svg", ".png", ".xpm")) else value)
    return result


def main() -> int:
    papirus = Path(sys.argv[1] if len(sys.argv) > 1 else "/usr/share/icons/Papirus")
    output = Path(sys.argv[2] if len(sys.argv) > 2 else ROOT / "iconography/papirus_catalog.json")
    if not papirus.is_dir():
        print(f"Papirus directory not found: {papirus}", file=sys.stderr)
        return 2

    names = {category: set() for category in CATEGORIES}
    symbolic: set[str] = set()
    for path in papirus.rglob("*"):
        if not (path.is_file() or path.is_symlink()):
            continue
        name = icon_name(path)
        if not name:
            continue
        parts = set(path.parts)
        category = next((c for c in CATEGORIES if c in parts), None)
        if category:
            names[category].add(name)
        elif "symbolic" in parts:
            symbolic.add(name)

    installed = desktop_icons()
    names["apps"].update(installed)
    payload = {
        "$comment": "Papirus filename compatibility snapshot. Artwork is generated as OSIRIS Material Symbols Rounded 300; Papirus artwork is not redistributed.",
        "source": str(papirus),
        "papirusPackage": "20250501+git20260316-0ubuntu1",
        "icons": {category: sorted(values) for category, values in sorted(names.items())},
        "symbolic": sorted(symbolic),
        "installedApplications": sorted(installed),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(len(v) for v in names.values()) + len(symbolic)
    print(f"wrote {output}: {total} names, {len(installed)} installed application IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

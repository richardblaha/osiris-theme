#!/usr/bin/env python3
"""OSIRIS terminal palette generator.

Turns `assets/tokens.json → terminal` into ready-to-install colour schemes:

  gnome-terminal  dconf profiles + install.sh   -> <out>/gnome-terminal/
  ptyxis          org.gnome.Ptyxis .palette     -> <out>/ptyxis/osiris.palette
  konsole         Konsole .colorscheme (×2)     -> <out>/konsole/
  all             all of the above

GNOME Console (kgx) has no colour API — it follows the system light/dark VTE
palette and cannot be themed; use Ptyxis or GNOME Terminal.

No third-party deps, no network.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOK = json.load(open(os.path.join(ROOT, "assets", "tokens.json"), encoding="utf-8"))
TERM = TOK["terminal"]
FONT = TOK["font"]["monoFamily"]

# stable profile ids so re-running install.sh is idempotent
UUID = {"dark": "0517150d-0d11-4700-8000-0517150d1117",
        "light": "0517150c-f6f8-4a00-8000-0517150ff6f8"}


def log(msg: str) -> None:
    print(f"\033[36m[osiris]\033[0m {msg}")


def write(path: str, content: str, *, mode: int = 0o644) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    os.chmod(path, mode)


def rgb(h: str) -> str:
    h = h.lstrip("#")
    return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"


# ------------------------------------------------------------- GNOME Terminal
_GT_INSTALLER = r"""#!/usr/bin/env bash
# OSIRIS GNOME Terminal profiles — merge into your existing profile list
# (your other profiles are kept). Re-runnable. Pass --default to also make
# "Osiris Dark" the default profile.
set -euo pipefail
BASE="/org/gnome/terminal/legacy/profiles:"
DARK="__DARK__"
LIGHT="__LIGHT__"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v dconf >/dev/null || { echo "dconf not found — is GNOME Terminal installed?" >&2; exit 1; }

dconf load "$BASE/:$DARK/"  < "$HERE/profile-dark.dconf"
dconf load "$BASE/:$LIGHT/" < "$HERE/profile-light.dconf"

old="$(dconf read "$BASE/list" 2>/dev/null || true)"
case "${old:-}" in
  ""|"@as []") new="['$DARK', '$LIGHT']" ;;
  *"$DARK"*)   new="$old" ;;
  *)           new="${old%]}, '$DARK', '$LIGHT']" ;;
esac
dconf write "$BASE/list" "$new"

if [ "${1:-}" = "--default" ]; then
  dconf write "$BASE/default" "'$DARK'"
  echo "Set 'Osiris Dark' as the default profile."
fi
echo "Installed 'Osiris Dark' + 'Osiris Light'. Pick them in Terminal ▸ Preferences ▸ Profiles."
"""


def gen_gnome_terminal(out: str) -> None:
    d = os.path.join(out, "gnome-terminal")

    def keys(variant: str) -> str:
        t = TERM[variant]
        pal = ", ".join(f"'{c}'" for c in t["palette"])
        return "\n".join([
            f"visible-name='Osiris {variant.capitalize()}'",
            "use-theme-colors=false",
            "bold-color-same-as-fg=true",
            "bold-is-bright=false",
            f"foreground-color='{t['foreground']}'",
            f"background-color='{t['background']}'",
            "cursor-colors-set=true",
            f"cursor-background-color='{t['cursor']}'",
            f"cursor-foreground-color='{t['cursorForeground']}'",
            "cursor-shape='block'",
            "highlight-colors-set=true",
            f"highlight-background-color='{t['selection']}'",
            f"highlight-foreground-color='{t['selectionForeground']}'",
            f"palette=[{pal}]",
            "use-theme-transparency=false",
            "use-transparent-background=false",
            "audible-bell=false",
            "use-system-font=false",
            f"font='{FONT} 11'",
            "scrollback-lines=100000",
            "",
        ])

    # standalone per-profile keyfiles for `dconf load <path>:/<uuid>/`
    for variant in ("dark", "light"):
        write(os.path.join(d, f"profile-{variant}.dconf"), "[/]\n" + keys(variant))

    combined = "\n".join([
        "# OSIRIS — GNOME Terminal profiles.",
        "# Merge (keeps your profiles):  ./install.sh",
        "# Or replace the whole list:    dconf load /org/gnome/terminal/legacy/profiles:/ < osiris.dconf",
        "",
        "[/]",
        f"default='{UUID['dark']}'",
        f"list=['{UUID['dark']}', '{UUID['light']}']",
        "",
        f"[:{UUID['dark']}]",
        keys("dark"),
        f"[:{UUID['light']}]",
        keys("light"),
    ])
    write(os.path.join(d, "osiris.dconf"), combined)

    write(os.path.join(d, "install.sh"),
          _GT_INSTALLER.replace("__DARK__", UUID["dark"]).replace("__LIGHT__", UUID["light"]),
          mode=0o755)
    log(f"  gnome-terminal: osiris.dconf + profile-*.dconf + install.sh -> {d}")


# --------------------------------------------------------------------- Ptyxis
def gen_ptyxis(out: str) -> None:
    def group(name: str, variant: str) -> str:
        t = TERM[variant]
        lines = [f"[{name}]",
                 f"Background={t['background']}",
                 f"Foreground={t['foreground']}",
                 f"Cursor={t['cursor']}",
                 f"CursorForeground={t['cursorForeground']}",
                 f"SelectionBackground={t['selection']}",
                 f"SelectionForeground={t['selectionForeground']}"]
        lines += [f"Color{i}={c}" for i, c in enumerate(t["palette"])]
        return "\n".join(lines)

    palette = "\n\n".join([
        "[Palette]\nName=Osiris",
        group("Light", "light"),
        group("Dark", "dark"),
    ]) + "\n"
    write(os.path.join(out, "ptyxis", "osiris.palette"), palette)
    log(f"  ptyxis: osiris.palette -> {os.path.join(out, 'ptyxis')}")


# -------------------------------------------------------------------- Konsole
def gen_konsole(out: str) -> None:
    for variant, fname in (("dark", "OsirisDark"), ("light", "OsirisLight")):
        t = TERM[variant]
        blocks = []
        names = ["Color0", "Color1", "Color2", "Color3",
                 "Color4", "Color5", "Color6", "Color7"]
        for i, key in enumerate(names):
            blocks.append(f"[{key}]\nColor={rgb(t['palette'][i])}")
            blocks.append(f"[{key}Intense]\nColor={rgb(t['palette'][i + 8])}")
            blocks.append(f"[{key}Faint]\nColor={rgb(t['palette'][i])}")
        body = "\n\n".join([
            f"[Background]\nColor={rgb(t['background'])}",
            f"[BackgroundIntense]\nColor={rgb(t['background'])}",
            f"[BackgroundFaint]\nColor={rgb(t['background'])}",
            f"[Foreground]\nColor={rgb(t['foreground'])}",
            f"[ForegroundIntense]\nBold=true\nColor={rgb(t['foreground'])}",
            f"[ForegroundFaint]\nColor={rgb(t['palette'][8])}",
            *blocks,
            "\n".join([
                "[General]",
                f"Description=Osiris {variant.capitalize()}",
                "Opacity=1",
                "Wallpaper=",
                "Blur=false",
            ]),
        ]) + "\n"
        write(os.path.join(out, "konsole", f"{fname}.colorscheme"), body)
    log(f"  konsole: OsirisDark/OsirisLight.colorscheme -> {os.path.join(out, 'konsole')}")


# ----------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    target, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    ran = False
    if target in ("gnome-terminal", "all"):
        gen_gnome_terminal(out); ran = True
    if target in ("ptyxis", "all"):
        gen_ptyxis(out); ran = True
    if target in ("konsole", "all"):
        gen_konsole(out); ran = True
    if not ran:
        print(f"\033[33m[osiris] warn:\033[0m unknown target '{target}'", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

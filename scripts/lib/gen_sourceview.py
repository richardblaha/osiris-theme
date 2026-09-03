#!/usr/bin/env python3
"""OSIRIS GtkSourceView style schemes.

Turns `assets/tokens.json` into the syntax colour schemes used by the GNOME
editing stack — GNOME Text Editor, gedit, GNOME Builder, gnome-latex, meld,
Ptyxis' preview, etc.

  scripts/lib/gen_sourceview.py <outdir>

writes two schemes (both variants, always):

  <outdir>/Osiris.xml        id "osiris"        (dark)
  <outdir>/Osiris-Light.xml  id "osiris-light" (light)

Install into gtksourceview-5/4/3.0 `styles/` dirs (build.sh / packaging do this).
No deps, no network.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOK = json.load(open(os.path.join(ROOT, "assets", "tokens.json"), encoding="utf-8"))


def scheme(variant: str) -> str:
    th = TOK["themes"][variant]
    s = th["syntax"]
    bg = th["bg"]
    txt = th["text"]
    st = {k: TOK["state"][k][variant] for k in TOK["state"]}
    acc = TOK["accent"]["primary"][variant]
    sec = TOK["accent"]["secondary"][variant]
    sid = "osiris" if variant == "dark" else "osiris-light"
    name = "Osiris" if variant == "dark" else "Osiris Light"
    kind = "dark" if variant == "dark" else "light"

    # a light wash of a colour for backgrounds (8-bit alpha suffix works in GSV)
    soft = lambda c: c + "26"

    colors = {
        "osiris_bg": bg["editor"],
        "osiris_bg_alt": bg["sidebar"],
        "osiris_sel": bg["selection"],
        "osiris_line": bg["hover"],
        "osiris_border": th["border"]["strong"],
        "osiris_fg": txt["primary"],
        "osiris_fg_dim": txt["secondary"],
        "osiris_fg_muted": txt["muted"],
        "osiris_accent": acc,
        "osiris_secondary": sec,
        "osiris_string": s["string"],
        "osiris_keyword": s["keyword"],
        "osiris_function": s["function"],
        "osiris_type": s["type"],
        "osiris_number": s["number"],
        "osiris_comment": s["comment"],
        "osiris_punctuation": s["punctuation"],
        "osiris_property": s["property"],
        "osiris_success": st["success"],
        "osiris_warning": st["warning"],
        "osiris_error": st["error"],
    }

    def st_line(nm: str, **kw) -> str:
        attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
        return f'  <style name="{nm}" {attrs}/>'

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<style-scheme id="{sid}" name="{name}" version="1.0">',
        '  <author>OSIRIS</author>',
        f'  <description>OSIRIS dual-accent — cyan/rose on a GitHub-flavoured ramp ({kind})</description>',
        '',
        *[f'  <color name="{k}" value="{v}"/>' for k, v in colors.items()],
        '',
        '  <!-- global -->',
        st_line("text", foreground="osiris_fg", background="osiris_bg"),
        st_line("selection", background="osiris_sel"),
        st_line("selection-unfocused", background="osiris_bg_alt"),
        st_line("cursor", foreground="osiris_accent"),
        st_line("secondary-cursor", foreground="osiris_fg_dim"),
        st_line("current-line", background="osiris_bg_alt"),
        st_line("current-line-number", foreground="osiris_accent", background="osiris_bg_alt", bold="true"),
        st_line("line-numbers", foreground="osiris_fg_muted", background="osiris_bg"),
        st_line("line-numbers-border", background="osiris_bg"),
        st_line("right-margin", foreground="osiris_border", background="osiris_border"),
        st_line("draw-spaces", foreground="osiris_border"),
        st_line("background-pattern", background="osiris_bg_alt"),
        st_line("snippet-focus", background=soft(acc), foreground="osiris_fg"),
        st_line("bracket-match", foreground="osiris_accent", background=soft(acc), bold="true"),
        st_line("bracket-mismatch", foreground="osiris_error", background=soft(st["error"])),
        st_line("search-match", foreground="osiris_bg", background="osiris_warning"),
        st_line("map-overlay", background=soft(txt["secondary"])),
        '',
        '  <!-- def.lang core scopes -->',
        st_line("def:comment", foreground="osiris_comment", italic="true"),
        st_line("def:shebang", foreground="osiris_comment", bold="true"),
        st_line("def:doc-comment-element", foreground="osiris_comment", italic="true"),
        st_line("def:constant", foreground="osiris_number"),
        st_line("def:string", foreground="osiris_string"),
        st_line("def:special-char", foreground="osiris_type"),
        st_line("def:special-constant", foreground="osiris_number"),
        st_line("def:number", foreground="osiris_number"),
        st_line("def:floating-point", foreground="osiris_number"),
        st_line("def:base-n-integer", foreground="osiris_number"),
        st_line("def:complex", foreground="osiris_number"),
        st_line("def:boolean", foreground="osiris_number"),
        st_line("def:character", foreground="osiris_string"),
        st_line("def:identifier", foreground="osiris_fg"),
        st_line("def:function", foreground="osiris_function"),
        st_line("def:builtin", foreground="osiris_function"),
        st_line("def:keyword", foreground="osiris_keyword"),
        st_line("def:reserved", foreground="osiris_keyword"),
        st_line("def:statement", foreground="osiris_keyword"),
        st_line("def:type", foreground="osiris_type"),
        st_line("def:operator", foreground="osiris_punctuation"),
        st_line("def:preprocessor", foreground="osiris_keyword"),
        st_line("def:variable", foreground="osiris_fg"),
        st_line("def:error", foreground="osiris_error", underline="error", underline_color="osiris_error"),
        st_line("def:warning", background=soft(st["warning"])),
        st_line("def:note", foreground="osiris_accent", bold="true"),
        st_line("def:net-address", foreground="osiris_accent", underline="single"),
        st_line("def:link-destination", foreground="osiris_string", underline="single"),
        st_line("def:heading", foreground="osiris_type", bold="true"),
        st_line("def:emphasis", italic="true"),
        st_line("def:strong-emphasis", foreground="osiris_keyword", bold="true"),
        st_line("def:inline-code", foreground="osiris_string"),
        st_line("def:list-marker", foreground="osiris_secondary"),
        st_line("def:deletion", foreground="osiris_error", strikethrough="true"),
        st_line("def:insertion", foreground="osiris_success", underline="single"),
        '',
        '  <!-- markup / data languages -->',
        st_line("xml:tag", foreground="osiris_function"),
        st_line("xml:attribute-name", foreground="osiris_property"),
        st_line("xml:namespace", foreground="osiris_type"),
        st_line("xml:element-name", foreground="osiris_function"),
        st_line("xml:entity", foreground="osiris_number"),
        st_line("html:tag", foreground="osiris_function"),
        st_line("json:keyname", foreground="osiris_property"),
        st_line("yaml:tag", foreground="osiris_property"),
        st_line("css:selector", foreground="osiris_type"),
        st_line("css:selector-id", foreground="osiris_property"),
        st_line("css:selector-class", foreground="osiris_type"),
        st_line("css:property-name", foreground="osiris_property"),
        st_line("css:property-value", foreground="osiris_string"),
        st_line("css:at-rules", foreground="osiris_keyword"),
        st_line("css:color", foreground="osiris_number"),
        st_line("markdown:header", foreground="osiris_type", bold="true"),
        st_line("markdown:code", foreground="osiris_string"),
        st_line("markdown:link-text", foreground="osiris_accent"),
        st_line("markdown:url", foreground="osiris_string", underline="single"),
        st_line("markdown:emphasis", italic="true"),
        st_line("markdown:strong-emphasis", foreground="osiris_keyword", bold="true"),
        st_line("markdown:list-marker", foreground="osiris_secondary"),
        st_line("markdown:blockquote-marker", foreground="osiris_comment"),
        st_line("markdown:line-break", background=soft(acc)),
        '',
        '  <!-- diff / vcs -->',
        st_line("diff:added-line", foreground="osiris_success"),
        st_line("diff:removed-line", foreground="osiris_error"),
        st_line("diff:changed-line", foreground="osiris_warning"),
        st_line("diff:diff-file", foreground="osiris_type", bold="true"),
        st_line("diff:location", foreground="osiris_accent"),
        st_line("diff:special-case", foreground="osiris_secondary"),
        '',
        '  <!-- GtkSourceView / Builder chrome -->',
        st_line("gtksourceview:context-class:comment", italic="true"),
        st_line("gtksourceview:context-class:string", foreground="osiris_string"),
        st_line("action::hover-definition", foreground="osiris_accent", underline="single"),
        '</style-scheme>',
        '',
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = argv[1]
    os.makedirs(out, exist_ok=True)
    for variant, fname in (("dark", "Osiris.xml"), ("light", "Osiris-Light.xml")):
        path = os.path.join(out, fname)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(scheme(variant))
        print(f"\033[36m[osiris]\033[0m   sourceview: {fname}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

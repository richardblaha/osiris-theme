# OSIRIS letterpress watermarks

A debossed ("letterpress") OSIRIS mark for empty-editor / empty-workbench
backgrounds — the shape reads only through its pressed edges (dark bevel above,
faint highlight below), so it sits under UI text without competing with it.

| File | For |
|---|---|
| `letterpress-dark.svg` / `.png` / `@2x.png` | dark ramp (`#0d1117` / `#161b22`) |
| `letterpress-light.svg` / `.png` / `@2x.png` | light ramp (white / `#f6f8fa`) |

SVG is the source; the `512×512` (`@1x`) and `1024×1024` (`@2x`) PNGs are
rasterised by [`scripts/build.sh`](../../scripts/build.sh):

```sh
make watermarks
```

## Use

- **VS Code / editor-style UIs** — a workbench background image
  (`workbench.editor.empty.hint` / a `background` extension), served at the
  density the surface reports (`@2x` on HiDPI).
- **Docs / marketing** — a low-key backdrop behind hero sections.

The PNGs are committed so consumers can reference them directly. Re-run
`make watermarks` and commit the result whenever the SVGs change.

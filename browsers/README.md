# OSIRIS browser themes

Static browser themes derived from [`assets/tokens.json`](../assets/tokens.json) —
the same cyan/rose dual-accent system as every other OSIRIS target.

| Directory | Engine | Manifest |
|---|---|---|
| [`chromium-dark/`](chromium-dark/) | Chromium · Chrome · Edge · Brave · Vivaldi · Opera | MV3 `theme` |
| [`chromium-light/`](chromium-light/) | ″ | MV3 `theme` |
| [`firefox-dark/`](firefox-dark/) | Firefox · Librewolf | MV2 `theme` |
| [`firefox-light/`](firefox-light/) | ″ | MV2 `theme` |

The Chromium `theme.colors` are `[r, g, b]` triplets; the Firefox `theme.colors`
are the equivalent hex values. Both sets are the token ramp:

- **Dark** — frame `#0d1117`, toolbar `#161b22`, field `#21262d`, text `#e6edf3`,
  accent (tab line / link / highlight) cyan `#00f2fe`.
- **Light** — frame `#f6f8fa`, toolbar `#ffffff`, field `#ffffff`, text `#1f2328`,
  accent blue `#0969da`.

## Install (unpacked, for development)

**Chromium / Chrome / Edge**

1. `chrome://extensions` → enable **Developer mode**.
2. **Load unpacked** → pick `browsers/chromium-dark` (or `-light`).

**Firefox**

1. `about:debugging#/runtime/this-firefox` → **Load Temporary Add-on**.
2. Pick `browsers/firefox-dark/manifest.json` (or `-light`).
   Temporary add-ons are removed on restart; sign the zip at
   [addons.mozilla.org](https://addons.mozilla.org/developers/) for a permanent install.

## Build the distributable zips

```sh
make browsers   # -> dist/osiris-{chromium,firefox}-{dark,light}-<ver>.zip
```

`make browsers` also syncs each `manifest.json` `version` from the repo `VERSION`.
For Chrome Web Store / AMO submission add a store icon (`"icons": { "128": "icon128.png" }`)
before uploading — omitted here so the folders load unpacked with no build step.

# GRUB boot-menu icons

GRUB matches a menu entry to `icons/<class>.png` by its `--class` (set by
`os-prober` / the distro's `10_linux`, `30_os-prober`, `30_uefi-firmware`
scripts). 32×32 PNGs.

These are **generated** from `assets/tokens.json` by
`scripts/lib/gen_grub_assets.py` (invoked by `scripts/build.sh grub`) — flat
OSIRIS glyphs on transparent ground. Classes covered:

`osiris`, `gnu-linux`, `linux`, `windows`, `recovery`, `uefi-firmware`, `memtest`.

To add a custom icon, drop `icons/<class>.svg` here and the build will rasterise
it in preference to the generated one.

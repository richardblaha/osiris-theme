# GRUB fonts

GRUB needs bitmap `.pf2` fonts. They are generated at build time from the Fira
Code variable font (fetched by `scripts/build.sh`, or system
`fonts-firacode` / `/usr/share/fonts/**/FiraCode*`):

```sh
grub-mkfont -s 13 -o firacode-13.pf2 FiraCode-Regular.ttf
grub-mkfont -s 14 -o firacode-14.pf2 FiraCode-Regular.ttf
grub-mkfont -s 16 -o firacode-16.pf2 FiraCode-Regular.ttf
grub-mkfont -s 18 -o firacode-18.pf2 FiraCode-Regular.ttf
grub-mkfont -s 18 -o firacode-medium-18.pf2 FiraCode-Medium.ttf
```

`theme.txt` references these by their internal family name (`Fira Code Regular`,
`Fira Code Medium`) — `grub-mkfont` embeds it from the TTF. The built `.pf2`
files land next to `theme.txt` in the installed theme directory
(`/boot/grub/themes/osiris/`).

If `grub-mkfont` is unavailable the build falls back to copying GRUB's stock
`unicode.pf2` and rewriting the font names in `theme.txt`.

# OSIRIS terminal colour schemes

The 16-colour ANSI palette + surfaces from
[`assets/tokens.json → terminal`](../../assets/tokens.json) (it mirrors the
`terminal.ansi*` values in the VS Code themes), rendered by
[`scripts/lib/gen_terminal.py`](../../scripts/lib/gen_terminal.py) into every
VTE-based terminal format. `make terminal` → `build/terminal/`.

| Terminal | Output | Where it installs |
|---|---|---|
| **Ptyxis** (current GNOME default terminal) | `ptyxis/osiris.palette` | `~/.local/share/org.gnome.Ptyxis/palettes/` · `/usr/share/org.gnome.Ptyxis/palettes/` |
| **GNOME Terminal** | `gnome-terminal/osiris.dconf` + `install.sh` | dconf, `/org/gnome/terminal/legacy/profiles:/` |
| **Konsole** (KDE) | `konsole/Osiris{Dark,Light}.colorscheme` | `~/.local/share/konsole/` · `/usr/share/konsole/` |

**GNOME Console** (`kgx`) has no colour API — it only follows the system
light/dark VTE palette and cannot be themed. Use Ptyxis or GNOME Terminal.

Dark and light are one palette each:

- **Dark** — bg `#0d1117`, fg `#e6edf3`, cursor cyan `#00f2fe`.
- **Light** — bg `#ffffff`, fg `#1f2328`, cursor blue `#0969da`.

## Install

```sh
make terminal                       # -> build/terminal/
scripts/install-local.sh terminal   # Ptyxis + Konsole + GNOME Terminal profiles
```

or by hand:

- **Ptyxis** — `cp build/terminal/ptyxis/osiris.palette ~/.local/share/org.gnome.Ptyxis/palettes/`,
  then pick **Osiris** in Preferences ▸ Appearance.
- **GNOME Terminal** — `build/terminal/gnome-terminal/install.sh` (add `--default`
  to make *Osiris Dark* the default profile). It merges two fixed-UUID profiles
  and leaves your others alone.
- **Konsole** — `cp build/terminal/konsole/*.colorscheme ~/.local/share/konsole/`,
  then Settings ▸ Edit Profile ▸ Appearance ▸ **Osiris Dark / Light**.

The `osiris-theme-gtk` / `osiris-theme-plasma` packages ship the Ptyxis palette,
the Konsole schemes and the GNOME Terminal installer under `/usr/share`.

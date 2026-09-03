%global debug_package %{nil}
%global _build_id_links none

Name:           osiris-desktop-theme
Version:        0.1.0
Release:        1%{?dist}
Summary:        OSIRIS dual-accent desktop theme (metapackage)
License:        MIT
URL:            https://github.com/richardblaha/osiris-themes
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  make
BuildRequires:  jq
BuildRequires:  python3
BuildRequires:  python3-pillow
BuildRequires:  librsvg2-tools
BuildRequires:  grub2-tools

Requires:       osiris-theme-gtk = %{version}-%{release}
Requires:       osiris-theme-plasma = %{version}-%{release}
Requires:       osiris-icon-theme = %{version}-%{release}
Requires:       osiris-theme-grub = %{version}-%{release}
Requires:       osiris-wallpapers = %{version}-%{release}

%description
Metapackage pulling in every OSIRIS theme component: GTK/GNOME, KDE Plasma/Qt,
the icon theme, the GRUB boot theme and the wallpapers. Colours come from the
OSIRIS design system (see the bundled DESIGN_SYSTEM.md).

# --------------------------------------------------------------------------
%package -n osiris-theme-gtk
Summary:        OSIRIS GTK 3/4 + libadwaita + GNOME Shell theme
BuildArch:      noarch
%description -n osiris-theme-gtk
Cyan/rose GTK 3, GTK 4 / libadwaita and GNOME Shell theme (Osiris / Osiris-Light)
plus the osiris-gtk-theme helper for the libadwaita opt-in.

%package -n osiris-theme-plasma
Summary:        OSIRIS KDE Plasma / Qt theme
BuildArch:      noarch
Recommends:     kvantum
%description -n osiris-theme-plasma
Plasma colour schemes, Kvantum Qt themes (OsirisDark / OsirisLight), the
OsirisDark Aurorae decoration and the Osiris Plasma desktop theme.

%package -n osiris-icon-theme
Summary:        OSIRIS dual-accent icon theme (Material Symbols)
BuildArch:      noarch
Requires:       hicolor-icon-theme
Recommends:     adwaita-icon-theme
%description -n osiris-icon-theme
Freedesktop icon theme in the Material Symbols visual language — cyan/rose on a
GitHub-flavoured ramp. Covers actions, apps, categories, devices, emblems,
mimetypes, places and status with GNOME/KDE compatibility symlinks; inherits
Adwaita / Breeze / hicolor. Installed as %{_datadir}/icons/Osiris.

%package -n osiris-theme-grub
Summary:        OSIRIS graphical GRUB2 boot theme
BuildArch:      noarch
Requires:       grub2-tools
%description -n osiris-theme-grub
1920x1080 GRUB2 boot menu in the OSIRIS visual language. %post copies the theme
into /boot/grub2, sets GRUB_THEME and regenerates grub.cfg.

%package -n osiris-wallpapers
Summary:        OSIRIS wallpapers (Abstract Bloom + Ancient Egypt Sci-Fi)
BuildArch:      noarch
%description -n osiris-wallpapers
Static Day/Night renders at four resolutions plus GNOME time-of-day dynamic XML
and KDE Plasma light/dark wallpaper packages.

# --------------------------------------------------------------------------
%prep
%autosetup -n %{name}-%{version}

%build
scripts/build.sh tokens gtk gnome plasma icons terminal grub wallpapers

%check
scripts/check-tokens.sh

%install
rm -rf %{buildroot}

# GTK / GNOME Shell
install -d %{buildroot}%{_datadir}/themes
cp -rT build/themes/Osiris       %{buildroot}%{_datadir}/themes/Osiris
cp -rT build/themes/Osiris-Light %{buildroot}%{_datadir}/themes/Osiris-Light
install -Dm0755 packaging/common/osiris-gtk-theme %{buildroot}%{_bindir}/osiris-gtk-theme

# Terminal (VTE): Ptyxis palette + GNOME Terminal profile installer
install -d %{buildroot}%{_datadir}/org.gnome.Ptyxis/palettes
cp build/terminal/ptyxis/osiris.palette %{buildroot}%{_datadir}/org.gnome.Ptyxis/palettes/
install -d %{buildroot}%{_datadir}/osiris/gnome-terminal
cp -rT build/terminal/gnome-terminal %{buildroot}%{_datadir}/osiris/gnome-terminal
install -d %{buildroot}%{_datadir}/konsole
cp build/terminal/konsole/*.colorscheme %{buildroot}%{_datadir}/konsole/

# KDE Plasma / Qt
install -d %{buildroot}%{_datadir}/color-schemes
cp build/plasma/color-schemes/*.colors %{buildroot}%{_datadir}/color-schemes/
install -d %{buildroot}%{_datadir}/Kvantum
cp -rT build/plasma/Kvantum/OsirisDark  %{buildroot}%{_datadir}/Kvantum/OsirisDark
cp -rT build/plasma/Kvantum/OsirisLight %{buildroot}%{_datadir}/Kvantum/OsirisLight
install -d %{buildroot}%{_datadir}/aurorae/themes
cp -rT build/plasma/aurorae/OsirisDark %{buildroot}%{_datadir}/aurorae/themes/OsirisDark
install -d %{buildroot}%{_datadir}/plasma/desktoptheme
cp -rT build/plasma/desktoptheme/Osiris %{buildroot}%{_datadir}/plasma/desktoptheme/Osiris

# Icon theme
install -d %{buildroot}%{_datadir}/icons
cp -rT build/icons/Osiris %{buildroot}%{_datadir}/icons/Osiris

# GRUB
install -d %{buildroot}%{_datadir}/grub/themes/osiris
cp -rT build/grub/osiris %{buildroot}%{_datadir}/grub/themes/osiris

# Wallpapers
install -d %{buildroot}%{_datadir}/backgrounds/osiris
cp -rT build/wallpapers/backgrounds/osiris %{buildroot}%{_datadir}/backgrounds/osiris
install -Dm0644 build/wallpapers/gnome-background-properties/osiris.xml \
  %{buildroot}%{_datadir}/gnome-background-properties/osiris.xml
install -d %{buildroot}%{_datadir}/wallpapers
cp -r build/wallpapers/kde/Osiris-* %{buildroot}%{_datadir}/wallpapers/

# --------------------------------------------------------------------------
%post -n osiris-icon-theme
command -v gtk-update-icon-cache >/dev/null 2>&1 && \
  gtk-update-icon-cache -q -f -t %{_datadir}/icons/Osiris || :

%postun -n osiris-icon-theme
command -v gtk-update-icon-cache >/dev/null 2>&1 && \
  gtk-update-icon-cache -q -f -t %{_datadir}/icons/hicolor || :

# --------------------------------------------------------------------------
%post -n osiris-theme-grub
GRUB_DIR=/boot/grub2
[ -d /boot/grub ] && [ ! -d /boot/grub2 ] && GRUB_DIR=/boot/grub
DEST="$GRUB_DIR/themes/osiris"
mkdir -p "$DEST"
cp -rT %{_datadir}/grub/themes/osiris "$DEST"
if [ -f /etc/default/grub ]; then
  if grep -q '^GRUB_THEME=' /etc/default/grub; then
    sed -i "s#^GRUB_THEME=.*#GRUB_THEME=\"$DEST/theme.txt\"#" /etc/default/grub
  else
    echo "GRUB_THEME=\"$DEST/theme.txt\"" >> /etc/default/grub
  fi
fi
command -v grub2-mkconfig >/dev/null 2>&1 && grub2-mkconfig -o "$GRUB_DIR/grub.cfg" || :

%postun -n osiris-theme-grub
if [ "$1" -eq 0 ]; then
  GRUB_DIR=/boot/grub2
  [ -d /boot/grub ] && [ ! -d /boot/grub2 ] && GRUB_DIR=/boot/grub
  rm -rf "$GRUB_DIR/themes/osiris"
  [ -f /etc/default/grub ] && sed -i '\#^GRUB_THEME=.*themes/osiris#d' /etc/default/grub || :
  command -v grub2-mkconfig >/dev/null 2>&1 && grub2-mkconfig -o "$GRUB_DIR/grub.cfg" || :
fi

# --------------------------------------------------------------------------
%files
%doc README.md docs/DESIGN_SYSTEM.md
%license LICENSE

%files -n osiris-theme-gtk
%license LICENSE
%{_datadir}/themes/Osiris
%{_datadir}/themes/Osiris-Light
%{_bindir}/osiris-gtk-theme
%{_datadir}/org.gnome.Ptyxis/palettes/osiris.palette
%{_datadir}/osiris/gnome-terminal

%files -n osiris-theme-plasma
%license LICENSE
%{_datadir}/color-schemes/Osiris.colors
%{_datadir}/color-schemes/OsirisLight.colors
%{_datadir}/Kvantum/OsirisDark
%{_datadir}/Kvantum/OsirisLight
%{_datadir}/aurorae/themes/OsirisDark
%{_datadir}/plasma/desktoptheme/Osiris
%{_datadir}/konsole/OsirisDark.colorscheme
%{_datadir}/konsole/OsirisLight.colorscheme

%files -n osiris-icon-theme
%license LICENSE
%{_datadir}/icons/Osiris

%files -n osiris-theme-grub
%license LICENSE
%{_datadir}/grub/themes/osiris

%files -n osiris-wallpapers
%license LICENSE
%{_datadir}/backgrounds/osiris
%{_datadir}/gnome-background-properties/osiris.xml
%{_datadir}/wallpapers/Osiris-Abstract
%{_datadir}/wallpapers/Osiris-Egypt

%changelog
* Wed Sep 03 2026 OSIRIS <osiris@example.org> - 0.1.0-1
- Initial packaging (gtk, plasma, icon-theme, grub, wallpapers, metapackage).

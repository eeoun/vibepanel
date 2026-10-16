Name:           vibepanel
# x-release-please-start-version
Version:        0.12.1
# x-release-please-end
Release:        1%{?dist}
Summary:        A GTK4 panel for Wayland with notifications, OSD, and quick settings

License:        MIT
URL:            https://github.com/prankstr/vibepanel
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  gettext
BuildRequires:  gtk4-devel >= 4.22
BuildRequires:  gtk4-layer-shell-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  systemd-devel
BuildRequires:  dbus-devel

Requires:       gtk4 >= 4.22
Requires:       gtk4-layer-shell
Requires:       pulseaudio-libs
Requires:       upower
Requires:       NetworkManager
Requires:       bluez

Recommends:     power-profiles-daemon

%description
A GTK4 panel for Wayland with integrated notifications, OSD, and quick settings.
Supports Hyprland, Niri, MangoWC, Sway and other i3-IPC compatible compositors.

%prep
%autosetup

%build
# Use vendored dependencies (offline build)
cargo build --release --offline

# Compile the translation catalogs (msgfmt, hence the gettext BuildRequires).
# Only the `mo` target: `all` would re-extract the POT and msgmerge the PO
# files, rewriting them inside the source tree during a package build.
make -C crates/vibepanel/po mo

%install
install -Dm755 target/release/vibepanel %{buildroot}%{_bindir}/vibepanel

# po/Makefile writes the catalogs to crates/vibepanel/locale/, which already
# uses gettext's LOCALEDIR layout (<lang>/LC_MESSAGES/<domain>.mo), so they
# drop straight into %{_datadir}/locale where libintl looks them up.
[ -d crates/vibepanel/locale ] || {
    echo "error: crates/vibepanel/locale missing - did 'make -C crates/vibepanel/po mo' run?" >&2
    exit 1
}
install -d "%{buildroot}%{_datadir}/locale"
cp -r crates/vibepanel/po/locale-dist/. "%{buildroot}%{_datadir}/locale/"

%find_lang %{name}

%files -f %{name}.lang
%license LICENSE
%{_bindir}/vibepanel

%changelog
* Sat Jan 17 2026 prankstr
- See https://github.com/prankstr/vibepanel/releases for changelog

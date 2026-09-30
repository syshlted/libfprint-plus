## libfprint with Goodix 538d (goodixtls53xd) support
##
## Builds the pinned commit of https://github.com/syshlted/libfprint-goodix-538d
## (a fork of lbssousa/libfprint, itself a fork of freedesktop libfprint).
## The commit and its tarball checksum are pinned here and in ./sources.
##
## NOTE: this commit is based on libfprint 1.94.10. Fedora 43 and newer ship
## 1.94.100, which is a newer version, so this package will not replace it there.
## Move to a 1.94.100-based commit before publishing for those releases.

%global commit 037912c17992d2abc81c79c40e85b45ba1d3871e

Name:           libfprint
Version:        1.94.10
Release:        101.goodix538d%{?dist}
Summary:        Toolkit for fingerprint scanner (with Goodix 538d support)

# Most of the code is LGPL-2.1-or-later; libfprint/nbis is NIST-PD.
License:        LGPL-2.1-or-later AND NIST-PD
URL:            https://github.com/syshlted/libfprint-goodix-538d
Source0:        %{url}/archive/%{commit}.tar.gz#/%{name}-goodix538d-%{commit}.tar.gz
Source1:        check-meson-results.py
Source2:        known-test-failures.txt

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  pkgconfig(glib-2.0) >= 2.50
BuildRequires:  pkgconfig(gio-2.0) >= 2.44.0
BuildRequires:  pkgconfig(gusb) >= 0.3.0
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  gtk-doc
BuildRequires:  libgudev-devel
# For the udev.pc to install the rules
BuildRequires:  systemd
BuildRequires:  gobject-introspection-devel
# For the test suite; umockdev 0.13.2 has an important locking fix
BuildRequires:  python3-cairo python3-gobject cairo-devel
BuildRequires:  umockdev >= 0.13.2

%description
libfprint offers support for consumer fingerprint reader devices.

This build adds the goodixtls53xd driver for the Goodix 27c6:538d sensor.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        tests
Summary:        Tests for the %{name} package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description tests
The %{name}-tests package contains tests that can be used to verify
the functionality of the installed %{name} package.

%prep
%autosetup -n libfprint-goodix-538d-%{commit}

%build
# "all" includes the default drivers (with goodixtls53xd) plus the virtual
# drivers used by the integration tests.
%meson -Ddrivers=all --wrap-mode=nodownload
%meson_build

%install
%meson_install

%ldconfig_scriptlets

%check
# Run the whole suite; tests listed in known-test-failures.txt are tolerated,
# anything else fails the build.
%{__meson} test -C %{_vpath_builddir} --no-rebuild --print-errorlogs || :
python3 %{SOURCE1} %{_vpath_builddir} %{SOURCE2}

%files
%license COPYING
%doc NEWS THANKS AUTHORS README.md
%{_libdir}/*.so.*
%{_libdir}/girepository-1.0/*.typelib
%{_udevhwdbdir}/60-autosuspend-libfprint-2.hwdb
%{_udevrulesdir}/70-libfprint-2.rules
%{_datadir}/metainfo/org.freedesktop.libfprint.metainfo.xml

%files devel
%doc HACKING.md
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}-2.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/gtk-doc/html/libfprint-2/

%files tests
%{_libexecdir}/installed-tests/libfprint-2/
%{_datadir}/installed-tests/libfprint-2/

%changelog
* Wed Sep 30 2026 Jeremy Melanson <1080872+zish@users.noreply.github.com> - 1.94.10-101.goodix538d
- Build the pinned commit of the syshlted fork; enable the test suite in %%check
  with a documented list of tolerated failures.

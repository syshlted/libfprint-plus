#!/bin/sh
# Prepare a Fedora container for building. Usage: ci-prepare.sh RELEASE EOL(true|false)
# EOL releases lose their mirrors, so their repos are pointed at the archive.
set -eu

release=$1
eol=$2

if [ "$eol" = true ]; then
    for f in /etc/yum.repos.d/fedora.repo /etc/yum.repos.d/fedora-updates.repo; do
        [ -f "$f" ] || continue
        sed -i -e 's|^metalink=|#metalink=|' -e 's|^#baseurl=.*|baseurl=|' "$f"
    done
    sed -i "/^\[fedora\]/,/^\[/ s|^baseurl=.*|baseurl=https://dl.fedoraproject.org/pub/archive/fedora/linux/releases/${release}/Everything/\$basearch/os/|" /etc/yum.repos.d/fedora.repo
    sed -i "/^\[updates\]/,/^\[/ s|^baseurl=.*|baseurl=https://dl.fedoraproject.org/pub/archive/fedora/linux/updates/${release}/Everything/\$basearch/|" /etc/yum.repos.d/fedora-updates.repo
fi

dnf -y upgrade --refresh
dnf -y install git-core rpm-build rpmdevtools rpmlint jq meson gcc

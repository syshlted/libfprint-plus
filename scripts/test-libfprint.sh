#!/bin/sh
# Build a pinned source with all drivers and run libfprint's test suite.
# Usage: test-libfprint.sh NAME   (NAME is a key under "sources" in upstreams.json)
# Runs inside a prepared Fedora container (see scripts/ci-prepare.sh).
set -eu

cd "$(dirname "$0")/.."
name=${1:?usage: test-libfprint.sh NAME}
root=$PWD

extra=$(jq -r ".sources[\"$name\"].build_requires | join(\" \")" upstreams.json)
# shellcheck disable=SC2086
dnf -y install meson ninja-build gcc gcc-c++ openssl-devel glib2-devel libgusb-devel \
    nss-devel pixman-devel libgudev-devel gobject-introspection-devel cairo-devel \
    python3-cairo python3-gobject umockdev-devel systemd cmake $extra

work=$(mktemp -d)
scripts/fetch-upstream.sh "$name" "$work/src"
cd "$work/src"
meson setup build -Ddoc=false -Dgtk-examples=false -Ddrivers=all
ninja -C build
meson test -C build --print-errorlogs || true
python3 "$root/scripts/check-meson-results.py" build "$root/scripts/known-test-failures.txt"

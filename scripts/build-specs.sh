#!/bin/sh
# Lint, fetch sources for, and build every spec under packaging/.
# Runs inside a Fedora/Rocky container (see .github/workflows/ci.yml).
set -eu

cd "$(dirname "$0")/.."
top="$PWD/rpmbuild"
specs=$(find packaging -name '*.spec')

if [ -z "$specs" ]; then
    echo "No spec files under packaging/ yet; nothing to build."
    exit 0
fi

for spec in $specs; do
    echo "== $spec"
    rpmlint "$spec"
    dir=$(dirname "$spec")
    spectool -g -C "$dir" "$spec"
    if [ -f "$dir/sources" ]; then
        (cd "$dir" && sha256sum -c sources)
    fi
    dnf -y builddep "$spec"
    rpmbuild -ba --define "_topdir $top" --define "_sourcedir $PWD/$dir" "$spec"
done

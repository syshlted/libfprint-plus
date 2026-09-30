#!/bin/sh
# Sign RPMs with the project's RPM signing key, then verify them.
# Usage: scripts/sign-rpms.sh FILE.rpm...
# Needs: podman, localhost/rpmsign:local (tools/Containerfile.rpmsign) and the
# key unlocked in the host's gpg-agent. The container gets an empty keyring,
# the public key and the agent socket, so the private key never leaves the host.
set -eu

cd "$(dirname "$0")/.."
key=$(cat keys/SIGNING-KEY-FINGERPRINT)
[ $# -gt 0 ] || { echo "usage: $0 FILE.rpm..." >&2; exit 2; }

agent_sock=$(gpgconf --list-dirs agent-socket)
gnupg_tmp=$(mktemp -d)
trap 'rm -rf "$gnupg_tmp"' EXIT
chmod 700 "$gnupg_tmp"
mounts=""
for f in "$@"; do
    d=$(cd "$(dirname "$f")" && pwd)
    mounts="$mounts -v $d:$d:z"
done

# shellcheck disable=SC2086
podman run --rm --security-opt label=disable --userns=keep-id -u "$(id -u)" \
    -e HOME=/tmp -e GNUPGHOME=/gnupg \
    -v "$gnupg_tmp:/gnupg:z" --tmpfs "/tmp:mode=1777" \
    -v "$agent_sock:/gnupg/S.gpg-agent" \
    -v "$PWD/keys:/keys:ro,z" $mounts \
    localhost/rpmsign:local sh -eu -c '
        gpg --batch --quiet --import /keys/RPM-GPG-KEY-libfprint-goodix538d
        rpmsign --define "_gpg_name '"$key"'" --addsign "$@"
        mkdir -p /tmp/rpmdb
        rpm --dbpath /tmp/rpmdb --import /keys/RPM-GPG-KEY-libfprint-goodix538d
        rpm --dbpath /tmp/rpmdb -K "$@"
    ' sh "$@"

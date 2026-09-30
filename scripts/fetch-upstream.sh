#!/bin/sh
# Download the pinned goodixtls source and verify its checksum. Usage: fetch-upstream.sh DESTDIR
set -eu

cd "$(dirname "$0")/.."
dest=${1:?usage: fetch-upstream.sh DESTDIR}
url=$(jq -r .goodixtls.url upstreams.json)
sum=$(jq -r .goodixtls.sha256 upstreams.json)
host=$(printf '%s\n' "$url" | sed -E 's|.*://([^/]+)/.*|\1|')

grep -qxF "$host" scripts/allowed-source-hosts.txt || { echo "host $host not allowed" >&2; exit 1; }
mkdir -p "$dest"
curl -fsSL -o "$dest/source.tar.gz" "$url"
echo "$sum  $dest/source.tar.gz" | sha256sum -c -
tar -xzf "$dest/source.tar.gz" -C "$dest" --strip-components=1
rm "$dest/source.tar.gz"

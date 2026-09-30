#!/bin/sh
# Fetch one pinned source by exact commit. Usage: fetch-upstream.sh NAME DESTDIR
# NAME is a key under "sources" in upstreams.json. The commit hash is
# content-addressed, so a matching hash means the tree is exactly what was pinned.
set -eu

cd "$(dirname "$0")/.."
name=${1:?usage: fetch-upstream.sh NAME DESTDIR}
dest=${2:?usage: fetch-upstream.sh NAME DESTDIR}
repo=$(jq -er ".sources[\"$name\"].repo" upstreams.json)
commit=$(jq -er ".sources[\"$name\"].commit" upstreams.json)
host=$(printf '%s\n' "$repo" | sed -E 's|.*://([^/]+)/.*|\1|')

grep -qxF "$host" scripts/allowed-source-hosts.txt || { echo "host $host not allowed" >&2; exit 1; }
rm -rf "$dest"
git init -q "$dest"
git -C "$dest" fetch -q --depth 1 "$repo" "$commit"
git -C "$dest" checkout -q FETCH_HEAD
[ "$(git -C "$dest" rev-parse HEAD)" = "$commit" ] || { echo "commit mismatch for $name" >&2; exit 1; }

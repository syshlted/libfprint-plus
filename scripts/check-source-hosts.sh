#!/bin/sh
# Fail if any Source*/URL in a spec file points outside the upstream allowlist.
# Allowed hosts are listed in scripts/allowed-source-hosts.txt (one per line).
set -eu

cd "$(dirname "$0")/.."
allow=scripts/allowed-source-hosts.txt

find packaging -name '*.spec' | while IFS= read -r spec; do
    grep -HEi '^(Source[0-9]*|URL):[[:space:]]*(https?|git)://' "$spec" |
    while IFS= read -r line; do
        host=$(printf '%s\n' "$line" | sed -E 's|.*://([^/:]+).*|\1|')
        if ! grep -qxF "$host" "$allow"; then
            echo "ERROR: $line" >&2
            echo "       host '$host' is not in $allow" >&2
            exit 1
        fi
    done
done

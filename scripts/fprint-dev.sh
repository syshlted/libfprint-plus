#!/bin/sh
# Run one of libfprint's example programs against a pinned source and a real
# sensor, without installing anything and without fprintd or root.
#
# Usage: fprint-dev.sh NAME EXAMPLE [-t THRESHOLD_MS]
#   NAME     goodix or cs9711 (a key under "sources" in upstreams.json)
#   EXAMPLE  enroll, verify, identify or img-capture
#   -t       gap in milliseconds to flag in the timeline (default 100)
#
# The source is built once per pinned commit in ~/.cache/libfprint-plus-dev,
# inside a rootless podman container. The container gets the USB bus, so your
# user needs access to the sensor (see packaging/udev/71-libfprint-plus-dev.rules).
# Prints enrolled by the examples are kept in ~/.cache/libfprint-plus-dev/NAME/state.
# Output is libfprint's debug log, each line with the time since the previous
# one (see timeline.py). The examples print some prompts without a newline,
# which timeline.py shows after a short wait.
set -eu

cd "$(dirname "$0")/.."
name=${1:?usage: fprint-dev.sh NAME EXAMPLE [-t THRESHOLD_MS]}
example=${2:?usage: fprint-dev.sh NAME EXAMPLE [-t THRESHOLD_MS]}
shift 2
threshold=100
while getopts t: opt; do
    case $opt in
        t) threshold=$OPTARG ;;
        *) echo "usage: $0 NAME EXAMPLE [-t THRESHOLD_MS]" >&2; exit 2 ;;
    esac
done
case $example in
    enroll | verify | identify | img-capture) ;;
    *) echo "unknown example: $example" >&2; exit 2 ;;
esac

image=localhost/libfprint-plus-dev:local
commit=$(jq -er ".sources[\"$name\"].commit" upstreams.json)
cache=${XDG_CACHE_HOME:-$HOME/.cache}/libfprint-plus-dev
work=$cache/$name-$commit
state=$cache/$name/state
mkdir -p "$work" "$state"

podman image exists "$image" ||
    podman build -q -t "$image" -f tools/Containerfile.dev tools/ >/dev/null

if [ ! -x "$work/build/examples/$example" ]; then
    echo "== building $name at $commit (first run only)" >&2
    scripts/fetch-upstream.sh "$name" "$work/src"
    podman run --rm --security-opt label=disable --userns=keep-id -v "$work:/work" -w /work/src "$image" \
        sh -c 'meson setup ../build -Ddoc=false -Dgtk-examples=false -Ddrivers=all >/dev/null &&
               ninja -C ../build >/dev/null'
fi

echo "== running $example; touch the sensor when asked" >&2
podman run --rm -i --init --security-opt label=disable --userns=keep-id \
    --device /dev/bus/usb -v /run/udev:/run/udev:ro \
    -v "$work:/work:ro" -v "$state:/state" -w /state \
    -e G_MESSAGES_DEBUG=all "$image" \
    stdbuf -oL "/work/build/examples/$example" 2>&1 |
    python3 scripts/timeline.py "$threshold"

#!/bin/sh
# Time a fingerprint verify and show where the time goes.
#
# fprintd is a daemon, so libfprint's debug output ends up in the journal and
# not in the fprintd-verify client. This turns debug logging on for the
# service (a runtime drop-in, gone after a reboot and removed on exit), runs
# fprintd-verify, and prints the journal as a timeline with the gap before
# each line. Gaps over THRESHOLD_MS are flagged: those are the slow steps.
#
# Usage: fprint-timing.sh [-n RUNS] [-f FINGER] [-t THRESHOLD_MS]
#   -n  verify runs back to back (default 2: the first starts the daemon and
#       opens the device, later ones show the warm cost)
#   -f  finger to verify (default: any enrolled finger), e.g. right-index-finger
#   -t  gap in milliseconds to flag (default 100)
# Needs sudo (drop-in and service restart). Touch the sensor when prompted.
set -eu

runs=2
finger=
threshold=100
while getopts n:f:t: opt; do
    case $opt in
        n) runs=$OPTARG ;;
        f) finger=$OPTARG ;;
        t) threshold=$OPTARG ;;
        *) echo "usage: $0 [-n RUNS] [-f FINGER] [-t THRESHOLD_MS]" >&2; exit 2 ;;
    esac
done

dropin_dir=/run/systemd/system/fprintd.service.d
dropin=$dropin_dir/timing-debug.conf

cleanup() {
    sudo rm -f "$dropin"
    sudo rmdir "$dropin_dir" 2>/dev/null || true
    sudo systemctl daemon-reload
    sudo systemctl restart fprintd.service 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if ! fprintd-list "$USER" >/dev/null 2>&1; then
    echo "fprintd-list found no usable device. Is the patched libfprint booted?" >&2
    exit 1
fi

sudo mkdir -p "$dropin_dir"
printf '[Service]\nEnvironment=G_MESSAGES_DEBUG=all\n' | sudo tee "$dropin" >/dev/null
sudo systemctl daemon-reload
sudo systemctl restart fprintd.service

start=$(date +%s.%N)
i=1
while [ "$i" -le "$runs" ]; do
    echo "== run $i of $runs: touch the sensor" >&2
    t0=$(date +%s.%N)
    if [ -n "$finger" ]; then
        fprintd-verify -f "$finger" || true
    else
        fprintd-verify || true
    fi
    t1=$(date +%s.%N)
    echo "run $i wall time: $(awk -v a="$t0" -v b="$t1" 'BEGIN { printf "%.3f s", b - a }')"
    i=$((i + 1))
done

echo
echo "== timeline (gap before each line; >${threshold} ms flagged)"
sudo journalctl -u fprintd.service --since "@$start" -o short-unix --no-pager |
    awk -v thr="$threshold" '
        /^-- / { next }
        {
            ts = $1 + 0
            if (prev != "") {
                gap = (ts - prev) * 1000
                mark = gap > thr ? "  <<<" : ""
                printf "%8.1f ms%s  ", gap, mark
            } else {
                printf "%8s ms  ", "0.0"
            }
            prev = ts
            $1 = ""; $2 = ""
            print substr($0, 3)
        }'

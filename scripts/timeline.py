#!/usr/bin/env python3
"""Print stdin with the time since the previous line, flagging long gaps.

Usage: timeline.py THRESHOLD_MS

Unlike a line-by-line loop it also shows a prompt that never ends in a
newline: text left waiting for 0.3 s is printed as a line of its own.
"""
import os
import select
import sys
import time


def main():
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0
    prev = None
    buf = b""
    fd = sys.stdin.fileno()

    def emit(text):
        nonlocal prev
        now = time.monotonic()
        if prev is None:
            head = f"{'0.0':>8} ms  "
        else:
            gap = (now - prev) * 1000
            flag = "  <<<" if gap > threshold else ""
            head = f"{gap:8.1f} ms{flag}  "
        prev = now
        sys.stdout.write(head + text + "\n")
        sys.stdout.flush()

    while True:
        ready, _, _ = select.select([fd], [], [], 0.3 if buf else None)
        if not ready:
            emit(buf.decode(errors="replace") + "   [waiting for input]")
            buf = b""
            continue
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            emit(line.decode(errors="replace"))
    if buf:
        emit(buf.decode(errors="replace"))


if __name__ == "__main__":
    main()

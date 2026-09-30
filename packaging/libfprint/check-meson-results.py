#!/usr/bin/env python3
"""Fail if a meson test failed that is not listed in known-test-failures.txt.

Usage: check-meson-results.py BUILDDIR [KNOWN_FAILURES_FILE]
"""
import json
import pathlib
import sys

build = pathlib.Path(sys.argv[1])
known_file = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "scripts/known-test-failures.txt")
known = {l.strip() for l in known_file.read_text().splitlines() if l.strip() and not l.startswith("#")}

results = {}
for line in (build / "meson-logs" / "testlog.json").read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        # meson names look like "drivers - libfprint:elan"; match on the bare test name
        results[r["name"].rsplit(":", 1)[-1]] = r["result"]

bad = {n: r for n, r in results.items() if r not in ("OK", "SKIP", "EXPECTEDFAIL")}
unexpected = {n: r for n, r in bad.items() if n not in known}
tolerated = {n: r for n, r in bad.items() if n in known}
fixed = sorted(n for n in known if results.get(n) == "OK")

print(f"{len(results)} tests: {len(results) - len(bad)} passed, {len(tolerated)} known failures, {len(unexpected)} unexpected failures")
for n, r in sorted(tolerated.items()):
    print(f"  known failure: {n} ({r})")
for n in fixed:
    print(f"  listed as failing but passed: {n} (remove it from the known-failures file)")
for n, r in sorted(unexpected.items()):
    print(f"  UNEXPECTED FAILURE: {n} ({r})")
sys.exit(1 if unexpected else 0)

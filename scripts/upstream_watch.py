#!/usr/bin/env python3
"""Report drift between our pinned upstreams and what upstream/Fedora ship.

Exit status 1 when action is needed; the report goes to stdout as Markdown.
"""
import datetime
import json
import os
import re
import subprocess
import urllib.request

cfg = json.load(open("upstreams.json"))
problems, info = [], []


def get(url):
    req = urllib.request.Request(url)
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def vkey(tag):
    return [int(x) for x in re.findall(r"\d+", tag)]


# --- libfprint upstream releases
lf = cfg["libfprint"]
out = subprocess.run(["git", "ls-remote", "--tags", "--refs", lf["repo"]], capture_output=True, text=True, check=True).stdout
tags = [l.split("refs/tags/")[1] for l in out.splitlines() if re.match(lf["tag_pattern"], l.split("refs/tags/")[1])]
latest = max(tags, key=vkey)
info.append(f"- libfprint upstream latest: `{latest}`")
for name, src in cfg["sources"].items():
    if vkey(latest) > vkey(src["base"]):
        problems.append(f"New libfprint release `{latest}` is available; the {name} source is based on `{src['base']}`. Rebase our fork.")

# --- origin projects of our forks: anything new since the commit we pin?
for name, src in cfg["sources"].items():
    origin = src["origin"]
    meta = get(f"https://api.github.com/repos/{origin}")
    cmp = get(f"https://api.github.com/repos/{origin}/compare/{src['origin_base']}...{meta['default_branch']}")
    pushed = meta["pushed_at"][:10]
    info.append(f"- {name}: origin `{origin}` default branch `{meta['default_branch']}` is {cmp['ahead_by']} commit(s) ahead of the commit our fork started from (last push {pushed})")
    if cmp["ahead_by"] > 0:
        problems.append(f"`{origin}` has {cmp['ahead_by']} commit(s) newer than the commit our {name} fork started from (`{src['origin_base'][:7]}`); review and merge into our fork.")

# --- Fedora security updates for watched packages, on the releases we build for
matrix = json.loads(subprocess.run(["python3", "scripts/fedora_matrix.py"], capture_output=True, text=True, check=True).stdout)
supported = {f"F{m['release']}" for m in matrix["include"] if not m["eol"]}
now = datetime.datetime.now()
seen = set()
for pkg in cfg["watch_packages"]:
    q = f"https://bodhi.fedoraproject.org/updates/?packages={pkg}&type=security&status=stable&rows_per_page=5"
    for u in get(q)["updates"]:
        rel_name = u["release"]["name"]
        if rel_name not in supported or not u["date_stable"]:
            continue
        builds = [b["nvr"] for b in u["builds"] if b["nvr"].rsplit("-", 2)[0] in cfg["watch_packages"]]
        age = (now - datetime.datetime.fromisoformat(u["date_stable"])).days
        if age <= 2 and (u["alias"] not in seen):
            seen.add(u["alias"])
            problems.append(f"New Fedora security update for {rel_name}: {', '.join(builds)} ({u['alias']}); rebuild and retest.")
info.append(f"- Fedora releases in matrix (supported): {', '.join(sorted(supported, reverse=True))}")

print("## Upstream watch\n")
print("\n".join(info))
if problems:
    print("\n### Action needed\n")
    print("\n".join(f"- {p}" for p in problems))
raise SystemExit(1 if problems else 0)

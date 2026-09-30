#!/usr/bin/env python3
"""Report drift between our pinned upstreams and what upstream/Fedora ship.

Exit status 1 when action is needed; the report goes to stdout as Markdown.
"""
import datetime
import json
import re
import subprocess
import urllib.parse
import urllib.request

cfg = json.load(open("upstreams.json"))
problems, info = [], []


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def vkey(tag):
    return [int(x) for x in re.findall(r"\d+", tag)]


# --- libfprint upstream releases
lf = cfg["libfprint"]
out = subprocess.run(["git", "ls-remote", "--tags", "--refs", lf["repo"]], capture_output=True, text=True, check=True).stdout
tags = [l.split("refs/tags/")[1] for l in out.splitlines() if re.match(lf["tag_pattern"], l.split("refs/tags/")[1])]
latest = max(tags, key=vkey)
info.append(f"- libfprint upstream latest: `{latest}` (pinned: `{lf['pinned']}`)")
if vkey(latest) > vkey(lf["pinned"]):
    problems.append(f"New libfprint release `{latest}` is available; we pin `{lf['pinned']}`.")

# --- goodixtls upstream activity
gx = cfg["goodixtls"]
slug = urllib.parse.urlparse(gx["repo"]).path.strip("/")
meta = get(f"https://api.github.com/repos/{slug}")
pushed = datetime.datetime.fromisoformat(meta["pushed_at"].replace("Z", "+00:00"))
idle = (datetime.datetime.now(datetime.timezone.utc) - pushed).days
info.append(f"- goodixtls upstream `{slug}`: last push {pushed.date()} ({idle} days ago), archived={meta['archived']}")
if idle > gx["max_idle_days"]:
    problems.append(f"`{slug}` has had no push for {idle} days (limit {gx['max_idle_days']}); "
                    "security fixes are unlikely to arrive from it.")
rel = get(f"https://api.github.com/repos/{slug}/releases?per_page=1")
if rel and rel[0]["tag_name"] != gx["tag"]:
    problems.append(f"New goodixtls release `{rel[0]['tag_name']}` (pinned `{gx['tag']}`).")

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

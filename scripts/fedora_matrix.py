#!/usr/bin/env python3
"""Print a GitHub Actions matrix: the newest stable Fedora and N releases back."""
import json
import sys
import urllib.request

cfg = json.load(open("upstreams.json"))
back = cfg["fedora"]["releases_back"]
url = "https://bodhi.fedoraproject.org/releases/?state=current&rows_per_page=50"
with urllib.request.urlopen(url, timeout=30) as r:
    current = {int(x["version"]) for x in json.load(r)["releases"] if x["id_prefix"] == "FEDORA" and x["version"].isdigit()}

latest = max(current)
include = [
    {"release": n, "image": f"registry.fedoraproject.org/fedora:{n}", "eol": n not in current}
    for n in range(latest, latest - back - 1, -1)
]
if "--with-sources" in sys.argv:
    include = [dict(e, source=name) for e in include for name in cfg["sources"]]
print(json.dumps({"include": include}))

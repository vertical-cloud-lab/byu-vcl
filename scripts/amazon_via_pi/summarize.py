#!/usr/bin/env python3
"""Collect parsed search + product data into one JSON for the write-up.

usage: python3 -I summarize.py <rawdir> <out.json>
"""
import glob, json, os, re, subprocess, sys
raw, out = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
def run(script, files):
    r = subprocess.run([sys.executable, "-I", os.path.join(here, script), *files],
                       capture_output=True, text=True, check=True)
    return [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
searches = sorted(glob.glob(os.path.join(raw, "s_*.html.gz")))
dps = sorted(glob.glob(os.path.join(raw, "dp_*.html.gz")))
res = {"searches": {}, "products": {}}
for f in searches:
    rows = run("parse_search.py", [f])
    q = os.path.basename(f)[2:-8].replace("_", " ")
    res["searches"][q] = {"n_results": len(rows),
                          "blocked": len(rows) == 0,
                          "results": [{k: r[k] for k in ("asin", "sponsored", "title", "price", "rating", "ratings", "bought_month")} for r in rows]}
for d in run("parse_dp.py", dps):
    asin = d["file"][3:13]
    d.pop("file")
    if "customers_say" in d:
        d["customers_say"] = re.split(r"\s*<!--|\s*</", d["customers_say"])[0].strip()
    d["url"] = f"https://www.amazon.com/dp/{asin}"
    res["products"][asin] = d
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
print(len(res["searches"]), "searches,", sum(v["blocked"] for v in res["searches"].values()), "blocked;", len(res["products"]), "product pages")

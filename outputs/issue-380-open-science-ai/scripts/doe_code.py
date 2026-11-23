#!/usr/bin/env python3
"""DOE software release inventory (code.json, the agency's code.gov-format inventory) -> releases per year,
share open source, top labs, deduplicated labor-hour estimates. Writes data/doe_code_*.csv and a figure."""
import json, sys, collections, pandas as pd, numpy as np
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/doe_codejson/code.json"))
rows = []
for r in d["releases"]:
    perm = r.get("permissions") or {}
    lic = ";".join(sorted({(l.get("name") or "") for l in (perm.get("licenses") or []) if l}))
    rows.append(dict(name=r.get("name"), org=r.get("organization"), created=(r.get("date") or {}).get("created"), usage=perm.get("usageType"),
                     licenses=lic, repo=r.get("repositoryURL"), hours=r.get("laborHours"), status=r.get("status")))
t = pd.DataFrame(rows); t["year"] = pd.to_datetime(t.created, errors="coerce").dt.year
t["open"] = t.usage.eq("openSource")
by = t.groupby("year").agg(n=("name", "size"), open_share=("open", "mean")).reset_index()
by = by[(by.year >= 2000) & (by.year <= 2026)]; by.to_csv("data/doe_code_by_year.csv", index=False)
labs = t.groupby("org").agg(n=("name", "size"), open_share=("open", "mean")).sort_values("n", ascending=False).head(12); labs.to_csv("data/doe_code_by_lab.csv")
lic = collections.Counter(l for x in t[t.open].licenses for l in x.split(";") if l); pd.Series(lic).sort_values(ascending=False).head(15).to_csv("data/doe_code_licenses.csv")
dedup = t.dropna(subset=["repo"]).drop_duplicates("repo")
print("releases", len(t), "open share", round(t.open.mean(), 3), "| usage types", t.usage.value_counts().to_dict())
print(by.tail(8).to_string(index=False)); print(labs.head(8)); print("top licences", lic.most_common(6))
print("labor hours (dedup by repo, open):", f"{dedup[dedup.open].hours.sum()/1e6:.1f}M")
fig, ax = fig_ax("Government open source: DOE software releases by year", "Releases in DOE's code inventory by creation year; share released as open source",
                 rect=(0.08, 0.13, 0.80, 0.68))
source_note(fig, "Source: DOE code.json inventory (code.gov format), 5,879 releases; data/doe_code_by_year.csv. Creation dates of inventory records, not first public release; 2026 partial.")
b = by[by.year >= 2010]
ax.bar(b.year, b.n, color=BLUE, width=0.8, label="Releases created that year")
for x, n, s in zip(b.year, b.n, b.open_share):
    ax.text(x, n + 8, f"{s:.0%}", ha="center", fontsize=12, color=TEXT2)
ax.set_ylabel("releases"); ax.legend(loc="upper left"); ax.text(2010, b.n.max() * 0.85, "labels: share open source", fontsize=15, color=TEXT2)
fig.savefig("figures/doe_code_by_year.png", dpi=DPI); print("saved")

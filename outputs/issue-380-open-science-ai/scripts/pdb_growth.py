#!/usr/bin/env python3
"""Protein Data Bank entries released per year (RCSB Search API, count-only range queries) -> data/pdb_released_per_year.csv"""
import json, urllib.request, time, csv
def count(y):
    q = {"query": {"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_accession_info.initial_release_date", "operator": "range",
         "value": {"from": f"{y}-01-01", "to": f"{y + 1}-01-01", "include_lower": True, "include_upper": False}}},
         "request_options": {"return_counts": True}, "return_type": "entry"}
    req = urllib.request.Request("https://search.rcsb.org/rcsbsearch/v2/query", data=json.dumps(q).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r).get("total_count", 0)
rows = []; cum = 0
for y in range(1972, 2027):
    try: n = count(y)
    except Exception as e: n = 0
    cum += n; rows.append((y, n, cum)); time.sleep(0.2)
with open("data/pdb_released_per_year.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "released", "cumulative"]); w.writerows(rows)
print(rows[:3], rows[-5:])

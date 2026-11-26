#!/usr/bin/env python3
"""U4: open-source startups from two third-party lists, minus those already in U1-U3.

- Runa Capital's ROSS Index, 2024-2026 periods (data/u4/ross_index.csv; older periods use a layout the scraper
  doesn't read).
- Y Combinator companies tagged or described as open source in YC's directory (data/yc_open_source.csv).

Matching against U1-U3 uses normalised names and GitHub owners. Appends U4 to data/ventures_input.csv and writes
deal-pass inputs data/deal_passes/input_d01.csv ... Run from funders/ after build_inputs.py. Added after the first
deal passes had started, because there was time left; U4 is reported separately.
"""
import csv, os, re

GEN = r"\b(inc|labs?|ai|technologies|technology|software|hq|io|dev|co|corp|ltd|llc|gmbh|the|app|platform)\b"


def norm(s):
    s = re.sub(r"\([^)]*\)", " ", (s or "").lower())
    s = re.sub(GEN, " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def main():
    vin = list(csv.DictReader(open("data/ventures_input.csv")))
    vin = [v for v in vin if v["universe"] != "U4"]
    have = {norm(v["venture"]) for v in vin}
    owners = {o.lower() for v in vin for o in (v["owners"] or "").split(";") if o}
    for v in vin:  # alternative names inside parentheses
        for a in re.findall(r"\(([^)]*)\)", v["venture"]):
            have.add(norm(a))
    cand = {}
    for r in csv.DictReader(open("data/u4/ross_index.csv")):
        k = norm(r["startup"])
        own = r["repo"].split("/")[0].lower()
        if not k or k in have or own in owners:
            continue
        c = cand.setdefault(k, {"venture": r["startup"], "lists": set(), "hint": ""})
        c["lists"].add("ross")
        c["hint"] = (f"ROSS Index {r['period']}: repo github.com/{r['repo']}; {r['country']} {r['city']}; founded "
                     f"{r['founded']}; Runa's funding figure {r['funding_musd'] or 'none'} (USD M)")
    for r in csv.DictReader(open("data/yc_open_source.csv")):
        k = norm(r["name"])
        if not k or k in have:
            continue
        c = cand.setdefault(k, {"venture": r["name"], "lists": set(), "hint": ""})
        c["lists"].add("yc")
        c["hint"] = (c["hint"] + "; " if c["hint"] else "") + (f"YC {r['batch']} ({r['status']}); site {r['website']}; "
                                                              f"YC page {r['yc_url']}; {r['one_liner']}")
    rows = []
    for k, c in sorted(cand.items(), key=lambda x: x[1]["venture"].lower()):
        key = "u4-" + re.sub(r"[^a-z0-9]+", "-", c["venture"].lower()).strip("-")
        rows.append({"key": key, "venture": c["venture"], "universe": "U4", "category": "open-source startup",
                     "source_list": "+".join(sorted(c["lists"])), "hint": c["hint"][:600], "owners": "", "stars": ""})
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "duplicate U4 keys"
    cols = list(vin[0].keys())
    with open("data/ventures_input.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(vin + rows)
    n = 25
    for i in range(0, len(rows), n):
        pid = f"d{i // n + 1:02d}"
        with open(f"data/deal_passes/input_{pid}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows[i:i + n])
    print(len(rows), "U4 ventures:", sum("ross" in r["source_list"] for r in rows), "from ROSS,",
          sum("yc" in r["source_list"] for r in rows), "from YC;", (len(rows) + n - 1) // n, "passes")


if __name__ == "__main__":
    main()

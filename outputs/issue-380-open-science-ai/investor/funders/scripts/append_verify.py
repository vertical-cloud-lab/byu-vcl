#!/usr/bin/env python3
"""Record a verification verdict for an investor name that the source check could not find on its cited page.

    python3 scripts/append_verify.py <<'JSON'
    {"key": "...", "name": "Seedcamp", "source": "https://...", "verdict": "confirmed", "new_source": "", "note": ""}
    JSON

verdict: `confirmed` (the cited page does name it, e.g. spelled differently), `confirmed_other_source` (another page
names it; give new_source), `not_supported` (no page found that names it as an investor in this venture; the name
is then left out of the counts), or `unclear`. Writes data/verify/verdicts.csv. Run from funders/.
"""
import csv, json, os, sys

COLS = ["key", "name", "source", "verdict", "new_source", "note"]
OK = {"confirmed", "confirmed_other_source", "not_supported", "unclear"}
rows, errs = [], []
for n, line in enumerate(sys.stdin, 1):
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
        if d.get("verdict") not in OK:
            raise ValueError(f"verdict must be one of {sorted(OK)}")
        if d["verdict"] == "confirmed_other_source" and not str(d.get("new_source", "")).startswith("http"):
            raise ValueError("confirmed_other_source needs new_source URL")
        rows.append({c: str(d.get(c) or "") for c in COLS})
    except Exception as e:  # noqa: BLE001
        errs.append(f"line {n}: {e}")
if errs:
    sys.exit("NOTHING WRITTEN:\n" + "\n".join(errs))
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "verify", "verdicts.csv")
new = not os.path.exists(p)
with open(p, "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    if new:
        w.writeheader()
    w.writerows(rows)
print(f"appended {len(rows)}")

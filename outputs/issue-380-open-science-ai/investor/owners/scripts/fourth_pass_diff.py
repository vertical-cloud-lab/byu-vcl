#!/usr/bin/env python3
"""List what the fourth finance pass changed: one row per company and field, old value, new value and source.

    python scripts/fourth_pass_diff.py <core_financials before the fourth pass> data/core_financials.csv

The "before" table is part 2's data/core_financials.csv as committed (e.g. `git show 54834ab:<path>`). Writes
data/fourth_pass_changes.csv and prints counts by field and kind of change. Run from owners/.
"""
import sys
import numpy as np, pandas as pd

FIELDS = {"status": None, "acquirer": None, "status_date": None, "exit_value_usd": "exit_source",
          "total_funding_usd": "funding_source", "last_valuation_usd": "valuation_source",
          "peak_value_usd": "peak_source", "ever_1b": None}
a = pd.read_csv(sys.argv[1], dtype=str).set_index("owner")
b = pd.read_csv(sys.argv[2], dtype=str).set_index("owner")
rows = []
for o in b.index:
    for f, src in FIELDS.items():
        old, new = a.at[o, f] if o in a.index else np.nan, b.at[o, f]
        if f.endswith("_usd"):
            old = float(old) if isinstance(old, str) and old else np.nan
            new = float(new) if isinstance(new, str) and new else np.nan
            same = (np.isnan(old) and np.isnan(new)) or (not np.isnan(old) and not np.isnan(new)
                                                         and abs(old - new) <= 0.005 * max(old, new))
        else:
            old = old if isinstance(old, str) else ""
            new = new if isinstance(new, str) else ""
            same = old.strip().lower() == new.strip().lower()
        if same:
            continue
        kind = ("filled" if (old == "" or (isinstance(old, float) and np.isnan(old))) else
                "cleared" if (new == "" or (isinstance(new, float) and np.isnan(new))) else "changed")
        if f == "ever_1b" and old == "unknown":
            kind = "filled"
        rows.append({"owner": o, "entity": b.at[o, "entity"], "field": f, "kind": kind, "old": old, "new": new,
                     "source": b.at[o, src] if src else "", "pass_file": b.at[o, "pass_file"]})
d = pd.DataFrame(rows)
d.to_csv("data/fourth_pass_changes.csv", index=False)
if len(d):
    print(d.groupby(["field", "kind"]).size().unstack(fill_value=0).to_string())
    print("companies changed:", d.entity.nunique(), "orgs:", d.owner.nunique())

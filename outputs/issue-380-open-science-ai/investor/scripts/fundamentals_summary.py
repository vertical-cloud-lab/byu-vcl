#!/usr/bin/env python3
"""Survivors only: Yahoo Finance fundamentals (snapshot 2026-11-24) of the cohort companies still listed.
Domo is excluded because it sold its operating business in 2026 and is now a cash shell (HUCK).
Writes data/fundamentals_summary.csv. Run from investor/."""
import pandas as pd
f = pd.read_csv("data/fundamentals_snapshot.csv")
f = f[f.ticker != "DOMO"].copy()
f["fcf_margin"] = f.freeCashflow / f.totalRevenue
cols = {"revenueGrowth": "revenue growth (latest quarter, y/y)", "grossMargins": "gross margin", "operatingMargins": "operating margin",
        "fcf_margin": "free-cash-flow margin", "enterpriseToRevenue": "EV / revenue"}
rows = []
for k, lab in cols.items():
    rows.append({"metric": lab, **{f"median_{c}": f[f.cohort == c][k].median() for c in ["oss", "closed"]},
                 "n_oss": int(f[f.cohort == "oss"][k].notna().sum()), "n_closed": int(f[f.cohort == "closed"][k].notna().sum())})
s = pd.DataFrame(rows); s.to_csv("data/fundamentals_summary.csv", index=False); print(s.round(3).to_string())
print("OSS:", ", ".join(f[f.cohort == "oss"].ticker)); print("closed:", ", ".join(f[f.cohort == "closed"].ticker))

#!/usr/bin/env python3
"""Survivors only: Yahoo Finance fundamentals (snapshot 2026-11-24) of the cohort companies still listed, with
cohorts defined as in H1. Domo is excluded because it sold its operating business in 2026 (now a cash shell, HUCK).
Two variants: JFrog excluded (H1's pre-registered definition) and JFrog counted as open source.
Writes data/fundamentals_summary.csv. Run from investor/."""
import pandas as pd
f = pd.read_csv("data/fundamentals_snapshot.csv")
f = f[f.ticker != "DOMO"].copy()
f["fcf_margin"] = f.freeCashflow / f.totalRevenue
cols = {"revenueGrowth": "revenue growth (latest quarter, y/y)", "grossMargins": "gross margin", "operatingMargins": "operating margin",
        "fcf_margin": "free-cash-flow margin", "enterpriseToRevenue": "EV / revenue"}
rows = []
for variant, oss in [("JFrog excluded (H1 definition)", f[(f.cohort == "oss") & (f.ticker != "FROG")]),
                     ("JFrog counted as open source", f[f.cohort == "oss"])]:
    cl = f[f.cohort == "closed"]
    for k, lab in cols.items():
        rows.append({"variant": variant, "metric": lab, "median_open_source": oss[k].median(), "median_closed": cl[k].median(),
                     "n_open_source": int(oss[k].notna().sum()), "n_closed": int(cl[k].notna().sum()),
                     "open_source_tickers": " ".join(oss.ticker), "closed_tickers": " ".join(cl.ticker)})
s = pd.DataFrame(rows); s.to_csv("data/fundamentals_summary.csv", index=False)
print(s[["variant", "metric", "median_open_source", "median_closed", "n_open_source", "n_closed"]].round(3).to_string())

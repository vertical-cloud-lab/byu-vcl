#!/usr/bin/env python3
"""Assemble data/core_financials.csv from the six sourced research passes, Yahoo and SEC Form D.

latest_value_usd: market cap on the snapshot date for listed companies (Yahoo); the disclosed acquisition price for
acquired ones; the last disclosed post-money valuation for private ones; blank for shutdowns and undisclosed values.
Run from owners/ after the research passes are copied to data/finance_passes/ and after listed_financials.py and
sec_form_d.py have run. Also writes data/form_d_targets.csv (US core companies) if it doesn't exist, so that
sec_form_d.py can run between the two invocations of this script.
"""
import glob, os
import numpy as np, pandas as pd

parts = sorted(glob.glob("data/finance_passes/output_*.csv"))
F = pd.concat([pd.read_csv(p, dtype=str).assign(pass_file=os.path.basename(p)) for p in parts], ignore_index=True)
F["owner"] = F.owner.str.strip()
inp = pd.read_csv("data/finance_passes/input_all.csv", dtype=str)
missing = set(inp.owner) - set(F.owner)
print(f"rows {len(F)}, input {len(inp)}, missing {len(missing)}", sorted(missing)[:20])
F = F.drop_duplicates("owner", keep="last")
F = inp[["owner", "frames", "stars", "h9_addition", "country"]].merge(F, on="owner", how="left")
num = ["exit_value_usd", "total_funding_usd", "last_valuation_usd", "peak_value_usd"]
for c in num:
    F[c] = pd.to_numeric(F[c].astype(str).str.replace(r"[,$\s]", "", regex=True), errors="coerce")
F["status"] = F.status.fillna("unknown").str.strip().str.lower().replace({"shut down": "shut_down", "shutdown":
                                                                         "shut_down"})
F["ever_1b"] = F.ever_1b.fillna("unknown").str.strip().str.lower()
F["in_frame_a"] = F.frames.str.contains("A").astype(int)
F["h9_addition"] = F.h9_addition.fillna("0").astype(int)

# US companies for the Form D cross-check
if not os.path.exists("data/form_d_targets.csv"):
    us = F[F.country.fillna("").eq("US") | F.legal_name.fillna("").str.contains(r"\bInc\b|LLC|Corp", regex=True)]
    t = us[["owner", "legal_name", "entity"]].copy()
    t["legal_name"] = t.legal_name.fillna(t.entity)
    t[["owner", "legal_name"]].to_csv("data/form_d_targets.csv", index=False)
    print("form D targets", len(t))

if os.path.exists("data/listed_financials.csv"):
    L = pd.read_csv("data/listed_financials.csv")
    F = F.merge(L[["ticker", "market_cap_usd", "revenue_usd", "grossMargins", "operatingMargins", "snapshot_utc"]],
                on="ticker", how="left")
if os.path.exists("data/form_d_by_owner.csv"):
    D = pd.read_csv("data/form_d_by_owner.csv")
    F = F.merge(D, on="owner", how="left")

F["latest_value_usd"] = np.where(F.status.eq("listed"), F.get("market_cap_usd"),
                         np.where(F.status.eq("acquired"), F.exit_value_usd,
                         np.where(F.status.eq("private"), F.last_valuation_usd, np.nan)))
F["latest_value_basis"] = np.where(F.status.eq("listed"), "market cap (Yahoo)", np.where(F.status.eq("acquired"),
                                   "disclosed acquisition price", np.where(F.status.eq("private"),
                                   "last disclosed valuation", "")))
F.loc[F.latest_value_usd.isna(), "latest_value_basis"] = ""
F.to_csv("data/core_financials.csv", index=False)
print(F.status.value_counts().to_string())
print("with latest value:", int(F.latest_value_usd.notna().sum()), "with funding:", int(F.total_funding_usd.notna().sum()))

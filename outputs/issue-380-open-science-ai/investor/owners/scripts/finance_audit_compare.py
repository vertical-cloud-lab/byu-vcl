#!/usr/bin/env python3
"""Compare Edison's blind re-research of 40 randomly drawn companies with this study's rows.

The sample (../edison/uploads_owners/finance_audit_sample.csv) has 20 companies whose row had at least one sourced
figure and 20 whose row had none (data/finance_audit_strata.csv); Edison saw neither the strata nor any figure.
Agreement is reported for status, for ever_1b, and for total funding and peak value: two figures agree if within
25% of each other (rounds and sums differ legitimately), and a figure only one side found is counted separately.

Writes data/finance_audit_comparison.csv and data/finance_audit_summary.json. Run from owners/.
"""
import glob, json, re
import numpy as np, pandas as pd

exec(open("scripts/owners_analysis.py").read().split("if __name__")[0])

path = sorted(glob.glob("../edison/inv_finance_audit_files/**/finance_audit.csv", recursive=True))[0]
E = pd.read_csv(path, dtype=str)
E.columns = [c.strip() for c in E.columns]
Co = company_table()
strata = pd.read_csv("data/finance_audit_strata.csv")
mine = Co.set_index("owner")


def num(v):
    v = re.sub(r"[,$\s]", "", str(v or ""))
    try:
        return float(v) if v and v.lower() != "nan" else np.nan
    except ValueError:
        return np.nan


def compare(a, b):
    if np.isnan(a) and np.isnan(b):
        return "both blank"
    if np.isnan(a):
        return "only Edison"
    if np.isnan(b):
        return "only mine"
    return "agree (within 25%)" if abs(a - b) <= 0.25 * max(a, b) else "differ"


rows = []
for r in E.itertuples(index=False):
    key = str(r.github_orgs).strip()
    if key not in mine.index:
        continue
    m = mine.loc[key]
    st = strata.set_index("owner").stratum.get(key, "")
    rows.append({"github_orgs": key, "entity": m.entity, "stratum": st,
                 "status_mine": m.status, "status_edison": str(r.status).strip().lower(),
                 "ever_1b_mine": m.ever_1b, "ever_1b_edison": str(r.ever_1b).strip().lower(),
                 "funding_mine": m.raised_usd, "funding_edison": num(r.total_funding_usd),
                 "peak_mine": m.peak_value_usd, "peak_edison": num(r.peak_value_usd),
                 "notes_edison": r.notes})
d = pd.DataFrame(rows)
d["status_agree"] = d.status_mine == d.status_edison
d["ever_1b_agree"] = d.ever_1b_mine == d.ever_1b_edison
dec = d.ever_1b_mine.isin(["yes", "no"]) & d.ever_1b_edison.isin(["yes", "no"])
d["funding_cmp"] = [compare(a, b) for a, b in zip(d.funding_mine, d.funding_edison)]
d["peak_cmp"] = [compare(a, b) for a, b in zip(d.peak_mine, d.peak_edison)]
d.to_csv("data/finance_audit_comparison.csv", index=False)
summ = {"n": int(len(d)), "edison_file": path,
        "status_agreement": round(float(d.status_agree.mean()), 3),
        "status_disagreements": d[~d.status_agree][["entity", "status_mine", "status_edison"]].to_dict("records"),
        "ever_1b_agreement": round(float(d.ever_1b_agree.mean()), 3),
        "ever_1b_both_decisive": int(dec.sum()),
        "ever_1b_agreement_when_both_decisive": round(float(d[dec].ever_1b_agree.mean()), 3) if dec.any() else None,
        "ever_1b_crosstab": pd.crosstab(d.ever_1b_mine, d.ever_1b_edison).to_dict(),
        "funding": d.funding_cmp.value_counts().to_dict(), "peak_value": d.peak_cmp.value_counts().to_dict(),
        "by_stratum": {k: {"n": int(len(g)), "status_agreement": round(float(g.status_agree.mean()), 3),
                           "funding": g.funding_cmp.value_counts().to_dict()} for k, g in d.groupby("stratum")}}
json.dump(summ, open("data/finance_audit_summary.json", "w"), indent=1, default=str)
print(json.dumps(summ, indent=1, default=str))

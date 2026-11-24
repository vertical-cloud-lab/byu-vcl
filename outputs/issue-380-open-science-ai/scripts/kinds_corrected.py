#!/usr/bin/env python3
"""Corrected 'who closes' analysis (after the independent review): classify public/nonprofit/foundation/
government infrastructure FIRST, then companies founded before 2000, then VC-era companies; and adjust
the VC-era vs incumbent difference for starting openness (bounded 0-4 score). Writes data/kinds_corrected.csv."""
import pandas as pd, numpy as np
m = pd.read_csv("companies/companies_master.csv"); m = m[m.group.isin(list("ABCDEFG"))].copy()
c = pd.read_csv("companies/calibration_scores.csv")
m = m.merge(c[["group", "slug", "rescored_initial", "rescored_current"]], on=["group", "slug"], how="left")
def kind(r):
    if str(r.ownership_status) in ("government", "nonprofit", "foundation") or str(r.origin) in ("government",): return "public/nonprofit infrastructure"
    if r.founded_year == r.founded_year and r.founded_year < 2000: return "company founded before 2000"
    if str(r.ownership_status) == "private_bootstrapped": return "bootstrapped company"
    return "company founded 2000+ (VC era)"
m["kind"] = m.apply(kind, axis=1)
rows = []
for lab, a, b in [("original", "openness_initial", "openness_current"), ("rescored", "rescored_initial", "rescored_current")]:
    d = m.dropna(subset=[a, b]).copy(); d["delta"] = d[b] - d[a]
    for k, g in d.groupby("kind"):
        rows.append(dict(scores=lab, kind=k, n=len(g), start=round(g[a].mean(), 2), now=round(g[b].mean(), 2), change=round(g.delta.mean(), 2),
                         closing_share=round((g.n_closing > 0).mean(), 2)))
    va = d[d.kind == "company founded 2000+ (VC era)"]; vb = d[d.kind == "company founded before 2000"]
    rng = np.random.default_rng(380)
    diffs = [rng.choice(va.delta.values, len(va)).mean() - rng.choice(vb.delta.values, len(vb)).mean() for _ in range(5000)]
    # adjust for starting openness: OLS delta ~ vc + start
    sub = pd.concat([va.assign(vc=1), vb.assign(vc=0)])
    X = np.column_stack([np.ones(len(sub)), sub.vc.values, sub[a].values]); y = sub.delta.values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    boots = []
    for _ in range(3000):
        idx = rng.integers(0, len(sub), len(sub)); bb, *_ = np.linalg.lstsq(X[idx], y[idx], rcond=None); boots.append(bb[1])
    print(f"[{lab}] raw diff {va.delta.mean() - vb.delta.mean():.2f} CI {np.round(np.percentile(diffs, [2.5, 97.5]), 2)} | adjusted for start {beta[1]:.2f} CI {np.round(np.percentile(boots, [2.5, 97.5]), 2)} (n VC {len(va)}, pre-2000 {len(vb)})")
t = pd.DataFrame(rows); t.to_csv("data/kinds_corrected.csv", index=False); print(t.to_string(index=False))
print("pre-2000 companies:", sorted(m[m.kind == "company founded before 2000"].name.str[:22].tolist()))

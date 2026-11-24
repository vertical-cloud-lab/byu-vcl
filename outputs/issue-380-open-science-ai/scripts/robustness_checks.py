#!/usr/bin/env python3
"""Robustness checks on the case files: US-only versions of the kind table; Spearman correlations between
openness and log value overall and within sectors; bootstrap CI for the VC-era vs incumbent difference."""
import pandas as pd, numpy as np
from scipy.stats import spearmanr
m = pd.read_csv("companies/companies_master.csv")
m = m[m.group.isin(list("ABCDEFG"))]  # organizations only; group I = AI-for-science models
m["delta"] = m.openness_current - m.openness_initial
us = m.hq_country.astype(str).str.contains("US|United States", regex=True)
def kind(r):
    if r.founded_year == r.founded_year and r.founded_year < 2000: return "long-standing (<2000)"
    if str(r.ownership_status) in ("government", "nonprofit", "foundation"): return "public/nonprofit infra"
    if str(r.ownership_status) == "private_bootstrapped": return "bootstrapped"
    if (r.funding_total_usd == r.funding_total_usd and r.funding_total_usd > 0) or str(r.ownership_status) in ("private_vc", "public", "acquired", "private_pe"): return "VC-era (2000+)"
    return "other"
m["kind"] = m.apply(kind, axis=1)
out = []
for scope, df in [("all A-G", m), ("US only", m[us]), ("A-F", m[m.group.isin(list("ABCDEF"))])]:
    g = df.groupby("kind")
    t = pd.DataFrame({"n": g.size(), "mean_change": g.delta.mean(), "closing_share": g.n_closing.apply(lambda s: (s > 0).mean()),
                      "opening_share": g.n_opening.apply(lambda s: (s > 0).mean())}).round(2)
    t["scope"] = scope; out.append(t.reset_index())
res = pd.concat(out); res.to_csv("data/robustness_kinds_by_scope.csv", index=False)
print(res[res.kind.isin(["VC-era (2000+)", "long-standing (<2000)", "public/nonprofit infra"])].to_string(index=False))
# bootstrap difference in mean change VC-era minus long-standing (A-G)
rng = np.random.default_rng(0)
a = m[m.kind == "VC-era (2000+)"].delta.dropna().values; b = m[m.kind == "long-standing (<2000)"].delta.dropna().values
diffs = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(5000)]
print("VC-era minus long-standing mean change:", round(a.mean() - b.mean(), 2), "95% CI", np.round(np.percentile(diffs, [2.5, 97.5]), 2))
# Spearman openness vs log value
v = m[m.latest_value_usd > 0].copy(); v["logv"] = np.log10(v.latest_value_usd)
rows = []
for name, df in [("all", v)] + [(s, v[v.group.isin(list(gs))]) for s, gs in [("commercial OSS (A,B)", "AB"), ("Big Tech & AI (C)", "C"), ("hardware (D)", "D"), ("physical science (E,F)", "EF"), ("AM & instruments (G)", "G")]]:
    df = df.dropna(subset=["openness_current"])
    if len(df) >= 6:
        r, p = spearmanr(df.openness_current, df.logv); rows.append(dict(scope=name, n=len(df), spearman_rho=round(r, 2), p=round(p, 3)))
c = pd.DataFrame(rows); c.to_csv("data/robustness_openness_vs_value.csv", index=False); print(c.to_string(index=False))

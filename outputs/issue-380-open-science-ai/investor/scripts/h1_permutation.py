#!/usr/bin/env python3
"""Permutation tests (difference in medians, open minus closed, two-sided) for the H1 measures, pre-registered
cohorts (JFrog excluded) and JFrog-as-open. Also re-values SolarWinds' N-able shares two other ways (sold at the
first regular-way close, $12.50, or held to SolarWinds' exit) to show the headline medians don't depend on it.
Writes data/h1_permutation.csv. Run from investor/."""
import numpy as np, pandas as pd
rng = np.random.default_rng(11)
R = pd.read_csv("data/h1_returns.csv")
R["pme"] = R.multiple_from_offer / R.qqq_multiple
def perm(x, y, n=50000):
    x, y = np.asarray(x), np.asarray(y); obs = np.median(x) - np.median(y); z = np.concatenate([x, y]); k = 0
    for _ in range(n):
        rng.shuffle(z); k += abs(np.median(z[:len(x)]) - np.median(z[len(x):])) >= abs(obs) - 1e-12
    return obs, k / n
rows = []
for label, jf in [("pre-registered (JFrog excluded)", None), ("JFrog counted as open source", "open_source")]:
    d = R[R.cohort.isin(["open_source", "closed"])].copy()
    d = d[d.company != "JFrog"] if jf is None else d.assign(cohort=np.where(d.company == "JFrog", jf, d.cohort))
    for m in ["excess_vs_qqq_offer", "excess_vs_qqq_first", "excess_vs_igv_offer", "pme"]:
        o = d[d.cohort == "open_source"][m].dropna(); c = d[d.cohort == "closed"][m].dropna()
        obs, p = perm(o, c)
        rows.append({"set": label, "measure": m, "n_open": len(o), "n_closed": len(c), "median_diff": obs, "perm_p_two_sided": p})
P = pd.DataFrame(rows); P.to_csv("data/h1_permutation.csv", index=False); print(P.round(4).to_string())
# SolarWinds valuation alternatives (per original IPO share): buyout 9.25 + dividends 1.25 + N-able
for lab, nable in [("N-able at tax-basis average $14.05 (used)", 0.5 * 14.05), ("N-able sold at first close $12.50", 0.5 * 12.50)]:
    print(lab, "-> exit value", round(9.25 + 1.25 + nable, 3), "multiple", round((9.25 + 1.25 + nable) / 15, 3))
print("Edison's held-to-exit alternative: 13.72 -> multiple", round(13.72 / 15, 3), "(closed median unchanged at 1.575 because SolarWinds sits below it either way)")

#!/usr/bin/env python3
"""H1 robustness: is the open-source gap just listing vintage (the 2021 bubble)? Compares cohorts within
listing-year buckets and fits excess return on an open-source dummy with listing-year fixed effects
(pre-registered cohorts, JFrog excluded). Writes data/h1_vintage.csv. Run from investor/."""
import numpy as np, pandas as pd
R = pd.read_csv("data/h1_returns.csv", parse_dates=["listing_date"])
R = R[R.cohort.isin(["open_source", "closed"]) & (R.company != "JFrog")].copy()
R["year"] = R.listing_date.dt.year
R["vintage"] = pd.cut(R.year, [2013, 2018, 2020, 2022], labels=["2014-18", "2019-20", "2021-22"])
t = R.groupby(["vintage", "cohort"], observed=True).agg(n=("company", "size"), median_excess_qqq=("excess_vs_qqq_offer", "median"),
                                                         median_multiple=("multiple_from_offer", "median"),
                                                         companies=("company", lambda s: ", ".join(s))).reset_index()
t.to_csv("data/h1_vintage.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
print(t.round(3).to_string())
# OLS with listing-year fixed effects, bootstrap CI on the open-source coefficient
def fit(df):
    X = pd.get_dummies(df.year.astype(str), drop_first=True).astype(float)
    X.insert(0, "open", (df.cohort == "open_source").astype(float)); X.insert(0, "const", 1.0)
    b, *_ = np.linalg.lstsq(X.values, df.excess_vs_qqq_offer.values, rcond=None)
    return b[1]
rng = np.random.default_rng(7); est = fit(R)
bs = []
for _ in range(5000):
    s = R.sample(len(R), replace=True, random_state=int(rng.integers(1e9)))
    if s.cohort.nunique() == 2:
        try: bs.append(fit(s))
        except Exception: pass
print("open-source coefficient with listing-year fixed effects:", round(est, 3), "95% CI", np.round(np.percentile(bs, [2.5, 97.5]), 3))
# rank-based check: Mann-Whitney on excess return
from scipy.stats import mannwhitneyu
o = R[R.cohort == "open_source"].excess_vs_qqq_offer; c = R[R.cohort == "closed"].excess_vs_qqq_offer
print("Mann-Whitney U p =", round(mannwhitneyu(o, c).pvalue, 3))

# Robustness not in the pre-registration: public-market equivalent (Kaplan-Schoar PME with one cash flow),
# PME = (value / offer) / (QQQ multiple over the same window). Unlike an annualized excess, it doesn't inflate
# short holds (MuleSoft 1.1 years, Apigee 1.6, Pivotal 1.7, Datto 1.7, MariaDB 1.6).
R["pme_qqq"] = R.multiple_from_offer / R.qqq_multiple
R["log_pme"] = np.log(R.pme_qqq)
def fit_pme(df):
    X = pd.get_dummies(df.year.astype(str), drop_first=True).astype(float)
    X.insert(0, "open", (df.cohort == "open_source").astype(float)); X.insert(0, "const", 1.0)
    b, *_ = np.linalg.lstsq(X.values, df.log_pme.values, rcond=None)
    return b[1]
e2 = fit_pme(R); bs2 = []
for _ in range(5000):
    s = R.sample(len(R), replace=True, random_state=int(rng.integers(1e9)))
    if s.cohort.nunique() == 2:
        bs2.append(fit_pme(s))
lo, hi = np.percentile(bs2, [2.5, 97.5])
med = R.groupby("cohort").pme_qqq.median()
def bdiff(n=10000):
    o = R[R.cohort == "open_source"].pme_qqq.values; c = R[R.cohort == "closed"].pme_qqq.values
    d = [np.median(rng.choice(o, len(o))) - np.median(rng.choice(c, len(c))) for _ in range(n)]
    return np.percentile(d, [2.5, 97.5])
dl, dh = bdiff()
print("median PME vs QQQ:", med.round(3).to_dict(), "difference CI", np.round([dl, dh], 3))
print("log-PME open-source coefficient, listing-year FE:", round(e2, 3), "=> ratio", round(np.exp(e2), 2),
      "95% CI ratio", np.round(np.exp([lo, hi]), 2))
print("Mann-Whitney on PME p =", round(mannwhitneyu(R[R.cohort == "open_source"].pme_qqq, R[R.cohort == "closed"].pme_qqq).pvalue, 3))
print(R.groupby(["vintage", "cohort"], observed=True).pme_qqq.median().round(3))
pd.DataFrame({"metric": ["median_pme_open", "median_pme_closed", "median_diff_ci_lo", "median_diff_ci_hi", "logpme_open_coef_yearFE", "ratio", "ratio_ci_lo", "ratio_ci_hi"],
              "value": [med.get("open_source"), med.get("closed"), dl, dh, e2, np.exp(e2), np.exp(lo), np.exp(hi)]}).to_csv("data/h1_pme.csv", index=False)
R[["cohort", "company", "year", "multiple_from_offer", "qqq_multiple", "pme_qqq"]].sort_values("pme_qqq").to_csv("data/h1_pme_by_company.csv", index=False)

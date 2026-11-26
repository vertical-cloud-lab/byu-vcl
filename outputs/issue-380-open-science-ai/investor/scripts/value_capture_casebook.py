#!/usr/bin/env python3
"""H2: value captured per dollar raised, by openness, in the first round's case files (db24bf3).

Uses only for-profit organizations with both total funding and a latest value (private valuation, market cap
or acquisition price). Big Tech and the AI-for-science model releases (group I) are excluded: their funding
totals are not venture capital. Writes data/h2_value_to_funding.csv and data/h2_summary.csv. Run from investor/."""
import numpy as np, pandas as pd
rng = np.random.default_rng(0)
d = pd.read_csv("edison/uploads/companies_master.csv")
d = d[~d.group.isin(["I"]) & (d.category != "big_tech")]
d = d[~d.ownership_status.isin(["nonprofit", "government", "foundation"])]
d = d[(d.funding_total_usd > 0) & d.latest_value_type.isin(["private_valuation", "market_cap", "acquisition_price"])]
d = d[d.latest_value_usd > 0].copy()
d["multiple"] = d.latest_value_usd / d.funding_total_usd
d["log_mult"] = np.log10(d.multiple)
d["open_now"] = pd.cut(d.openness_current, [-0.1, 0.5, 1.5, 2.5, 4.1], labels=["0 closed", "1 restricted", "2 mixed", "3-4 open"])
d["open_start"] = pd.cut(d.openness_initial, [-0.1, 0.5, 1.5, 2.5, 4.1], labels=["0 closed", "1 restricted", "2 mixed", "3-4 open"])
d["sector"] = np.where(d.category.isin(["hardware", "physical_science"]), "hardware/physical", np.where(d.category.isin(["ai_lab"]), "AI lab", "software"))
d[["group", "slug", "sector", "openness_initial", "openness_current", "funding_total_usd", "latest_value_usd",
   "latest_value_type", "latest_value_date", "multiple", "confidence"]].sort_values("multiple").to_csv("data/h2_value_to_funding.csv", index=False)
def boot_median(x, n=4000):
    x = np.asarray(x); b = [np.median(rng.choice(x, len(x))) for _ in range(n)]
    return np.percentile(b, [2.5, 97.5])
rows = []
for col in ["open_now", "open_start"]:
    for k, g in d.groupby(col, observed=True):
        lo, hi = boot_median(g.multiple) if len(g) > 2 else (np.nan, np.nan)
        rows.append({"by": col, "level": k, "n": len(g), "median_multiple": g.multiple.median(), "ci_lo": lo, "ci_hi": hi,
                     "share_below_1x": (g.multiple < 1).mean(), "share_10x_plus": (g.multiple >= 10).mean(),
                     "n_hardware": (g.sector == "hardware/physical").sum()})
s = pd.DataFrame(rows); s.to_csv("data/h2_summary.csv", index=False)
print(len(d), "organizations with funding and value"); print(s.round(2).to_string())
from scipy.stats import spearmanr
for col in ["openness_current", "openness_initial"]:
    r, p = spearmanr(d[col], d.log_mult, nan_policy="omit")
    bs = []
    for _ in range(4000):
        i = rng.integers(0, len(d), len(d)); bs.append(spearmanr(d[col].values[i], d.log_mult.values[i], nan_policy="omit")[0])
    print(col, "Spearman rho", round(r, 2), "95% CI", np.round(np.nanpercentile(bs, [2.5, 97.5]), 2), "p", round(p, 2))
print(d.groupby("sector").agg(n=("slug", "size"), median_mult=("multiple", "median")).round(2))
print(d.sort_values("multiple")[["slug", "sector", "openness_current", "multiple"]].round(2).to_string())

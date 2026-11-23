#!/usr/bin/env python3
"""Cross-tabulate the 121 case files: openness vs longevity, value, risk events, origin, sector, US.
Writes data/openness_outcomes_*.csv and prints markdown tables."""
import pandas as pd, numpy as np
m = pd.read_csv("companies/companies_master.csv")
m["sector"] = m.group.map({"A": "Software (commercial OSS)", "B": "Software (commercial OSS)", "C": "Big Tech & AI labs", "D": "Hardware",
                           "E": "Physical science: labs & AI-for-science", "F": "Physical science: software & infrastructure"})
m["open0"] = pd.cut(m.openness_initial, [-0.5, 0.5, 2.5, 4.5], labels=["closed (0)", "mixed (1-2)", "open (3-4)"])
m["open_now"] = pd.cut(m.openness_current, [-0.5, 0.5, 2.5, 4.5], labels=["closed (0)", "mixed (1-2)", "open (3-4)"])
alive = m.still_operating.astype(str).str.lower().eq("true")
m["age"] = np.where(alive, 2026, m.end_year) - m.founded_year
m["acquired"] = m.ownership_status.astype(str).isin(["acquired", "private_pe"]) | (m.n_exits > 0) & m.ownership_status.astype(str).eq("acquired")
m["us"] = m.hq_country.astype(str).str.contains("US|United States", regex=True)
def tab(by):
    g = m.groupby(by, observed=True)
    t = pd.DataFrame({"n": g.size(), "median_founded": g.founded_year.median(), "median_age_yrs": g.age.median(),
                      "share_operating": g.still_operating.apply(lambda s: s.astype(str).str.lower().eq("true").mean()),
                      "share_with_closing_move": g.n_closing.apply(lambda s: (s > 0).mean()),
                      "share_with_opening_move": g.n_opening.apply(lambda s: (s > 0).mean()),
                      "share_acquired_or_PE": g.ownership_status.apply(lambda s: s.astype(str).isin(["acquired", "private_pe"]).mean()),
                      "n_with_value": g.latest_value_usd.count(), "median_value_usd_B": g.latest_value_usd.median() / 1e9})
    return t.round(2)
out = {}
for by in ["open0", "open_now", "sector", "origin", "us"]:
    t = tab(by); out[by] = t; t.to_csv(f"data/openness_outcomes_by_{by}.csv")
    print(f"\n### by {by}\n"); print(t.to_markdown())
# openness change by sector
m["delta"] = m.openness_current - m.openness_initial
d = m.groupby("sector").delta.agg(["mean", lambda s: (s < 0).mean(), lambda s: (s > 0).mean()]).round(2)
d.columns = ["mean_change", "share_closed_down", "share_opened_up"]; d.to_csv("data/openness_change_by_sector.csv")
print("\n### openness change (current - initial) by sector\n"); print(d.to_markdown())

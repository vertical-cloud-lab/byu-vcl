#!/usr/bin/env python3
"""Turn data/openalex_us_oa_by_sector.json into tidy CSV: OA share and sector share by year."""
import json, pandas as pd
d = json.load(open("data/openalex_us_oa_by_sector.json"))
rows = []
for key, v in d.items():
    scope, t = key.split("|")
    for y, n in v["total"].items():
        rows.append(dict(scope=scope, inst_type=t, year=int(y), total=n, oa=v["oa"].get(y, 0)))
df = pd.DataFrame(rows); df["oa_share"] = df.oa / df.total
anyus = df[df.inst_type == "any_us"][["scope", "year", "total"]].rename(columns={"total": "us_total"})
df = df.merge(anyus, on=["scope", "year"]); df["share_of_us_articles"] = df.total / df.us_total
df.sort_values(["scope", "inst_type", "year"]).to_csv("data/openalex_us_oa_by_sector.csv", index=False)
lab = {"education": "Academia", "government": "Government", "facility": "Facility (incl. national labs)", "company": "Industry",
       "nonprofit": "Nonprofit", "healthcare": "Healthcare", "any_us": "All US"}
for scope in ["all", "physical_sciences", "materials", "ai"]:
    p = df[(df.scope == scope) & (df.year.isin([2000, 2005, 2010, 2015, 2020, 2022, 2024, 2025]))].pivot_table(index="year", columns="inst_type", values="oa_share").round(2)
    print("OA share", scope); print(p.rename(columns=lab))
p = df[(df.scope == "ai") & (df.inst_type == "company")][["year", "total", "share_of_us_articles"]]
print("Industry share of US AI articles\n", p[p.year >= 2000].iloc[::3].round(3).to_string(index=False))
p = df[(df.scope == "physical_sciences") & (df.inst_type == "company")][["year", "total", "share_of_us_articles"]]
print("Industry share of US physical-science articles\n", p[p.year >= 1995].iloc[::5].round(3).to_string(index=False))

#!/usr/bin/env python3
"""Openness of AI models by year, sector, country and domain, from Epoch AI's public database (CC-BY).
Source: https://epoch.ai/data (all_ai_models.csv, downloaded 2026-11-23)."""
import pandas as pd, numpy as np, json
import os, urllib.request
SRC = "/tmp/dl/epoch/all_ai_models.csv"   # raw file not committed (7 MB); re-download if missing
if not os.path.exists(SRC):
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    urllib.request.urlretrieve("https://epoch.ai/data/all_ai_models.csv", SRC)
d = pd.read_csv(SRC, low_memory=False)
d["year"] = pd.to_datetime(d["Publication date"], errors="coerce").dt.year
def acc(x):
    x = str(x)
    if x.startswith("Open weights (unrestricted)"): return "open_unrestricted"
    if x.startswith("Open weights"): return "open_restricted"
    if x in ("API access", "Hosted access (no API)", "Limited access"): return "api_or_hosted"
    if x == "Unreleased": return "unreleased"
    return None
d["acc"] = d["Model accessibility"].map(acc)
def sector(x):
    s = {t.strip() for t in str(x).split(",")}
    if "Industry" in s and "Academia" in s: return "Industry+Academia"
    for k in ["Industry", "Academia", "Government", "Research collective"]:
        if k in s: return k
    return None
d["sector"] = d["Organization categorization"].map(sector)
d["us"] = d["Country (of organization)"].fillna("").astype(str).str.contains("United States")
d["china"] = d["Country (of organization)"].fillna("").astype(str).str.contains("China")
SCI = {"Biology", "Materials science", "Earth science", "Medicine", "Mathematics", "Astronomy"}
d["science"] = d["Domain"].fillna("").astype(str).apply(lambda s: any(t.strip() in SCI for t in s.split(",")))
d["open_any"] = d["acc"].isin(["open_unrestricted", "open_restricted"])
k = d[d["acc"].notna() & d["year"].between(2012, 2026)].copy()

def share(df, by):
    g = df.groupby(by)
    out = g.agg(n=("acc", "size"), open_any=("open_any", "mean"),
                open_unrestricted=("acc", lambda s: (s == "open_unrestricted").mean()),
                api_or_hosted=("acc", lambda s: (s == "api_or_hosted").mean()),
                unreleased=("acc", lambda s: (s == "unreleased").mean())).reset_index()
    return out
rows = []
for scope, df in [("all", k), ("US", k[k.us]), ("China", k[k.china])]:
    s = share(df, ["year", "sector"]); s["scope"] = scope; rows.append(s)
    t = share(df, ["year"]); t["sector"] = "All sectors"; t["scope"] = scope; rows.append(t)
bysec = pd.concat(rows); bysec.to_csv("data/epoch_openness_by_year_sector.csv", index=False)
sci = share(k[k.us], ["year", "science"]); sci.to_csv("data/epoch_openness_science_us.csv", index=False)
# compute frontier: max training compute of open vs closed models by year
k["flop"] = pd.to_numeric(k["Training compute (FLOP)"], errors="coerce")
kf = k[k.flop > 0].copy(); kf["cls"] = np.where(kf.open_any, "open weights", "closed (API/unreleased)")
comp = kf.groupby(["year", "cls"])["flop"].max().unstack()
comp.to_csv("data/epoch_max_compute_open_vs_closed.csv")
# top-10 most compute-intensive models each year: share open
top = (k[k.flop > 0].sort_values("flop", ascending=False).groupby("year").head(10)
         .groupby("year")["open_any"].mean())
top.to_csv("data/epoch_top10_compute_open_share.csv")
print(bysec[(bysec.scope == "US") & (bysec.year >= 2016)].pivot_table(index="year", columns="sector", values="open_any").round(2))
print(bysec[(bysec.scope == "US") & (bysec.year >= 2016)].pivot_table(index="year", columns="sector", values="n"))
print("science vs not, US\n", sci[sci.year >= 2018].pivot_table(index="year", columns="science", values="open_any").round(2))
print("max compute log10\n", np.log10(comp[comp.index >= 2016]).round(1))
print("top10 open share\n", top[top.index >= 2016].round(2).to_dict())

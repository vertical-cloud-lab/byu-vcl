#!/usr/bin/env python3
"""Daily prices (Yahoo Finance via yfinance) for the H1 listing cohorts and benchmarks, plus a fundamentals
snapshot for the companies still listed. Delisted tickers are tried too; Yahoo usually no longer has them, and
their exits are valued from deal terms instead (data/cohort_listings.csv).

Writes data/prices_daily_adjclose.csv, data/prices_daily_close.csv, data/prices_coverage.json and
data/fundamentals_snapshot.csv. Run from investor/."""
import json, yfinance as yf, pandas as pd

LISTED = {"oss": ["MDB", "ESTC", "GTLB", "KLTR", "FROG"],
          "closed": ["TEAM", "NTNX", "APPN", "DOMO", "PD", "FSLY", "DT", "NET", "DDOG", "SNOW", "U", "PLTR",
                     "DOCN", "AVPT", "BLZE"]}
DELISTED = ["HDP", "TLND", "MULE", "CLDR", "PVTL", "CFLT", "BASE", "HCP", "MRDB", "INST", "FORG", "NEWR", "MOBL",
            "APIC", "APTI", "AYX", "SWI", "SUMO", "MSP", "JAMF", "INFA", "NABL"]
BENCH = ["QQQ", "IGV", "SPY"]
tick = sorted(set(sum(LISTED.values(), [])) | set(DELISTED) | set(BENCH))
adj = yf.download(tick, start="2014-01-01", interval="1d", progress=False, auto_adjust=True, threads=True)["Close"]
raw = yf.download(tick, start="2014-01-01", interval="1d", progress=False, auto_adjust=False, threads=True)["Close"]
adj.to_csv("data/prices_daily_adjclose.csv"); raw.to_csv("data/prices_daily_close.csv")
cov = {}
for t in tick:
    s = adj[t].dropna() if t in adj else pd.Series(dtype=float)
    cov[t] = None if s.empty else [str(s.index[0].date()), str(s.index[-1].date()), int(len(s))]
json.dump(cov, open("data/prices_coverage.json", "w"), indent=1)
print(json.dumps(cov, indent=0))
F = ["shortName", "marketCap", "enterpriseValue", "totalRevenue", "revenueGrowth", "grossMargins", "operatingMargins",
     "ebitdaMargins", "profitMargins", "freeCashflow", "operatingCashflow", "enterpriseToRevenue", "fullTimeEmployees"]
rows = []
for g, ts in LISTED.items():
    for t in ts:
        try:
            i = yf.Ticker(t).info
        except Exception as e:
            i = {"error": str(e)}
        rows.append({"cohort": g, "ticker": t, **{k: i.get(k) for k in F}})
pd.DataFrame(rows).to_csv("data/fundamentals_snapshot.csv", index=False)
print(pd.DataFrame(rows)[["cohort", "ticker", "grossMargins", "operatingMargins", "revenueGrowth", "enterpriseToRevenue"]])

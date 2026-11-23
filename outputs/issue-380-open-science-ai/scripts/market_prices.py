#!/usr/bin/env python3
"""Weekly adjusted closes (Yahoo Finance via yfinance) for open-source-origin public companies,
closed-source software peers of the same IPO vintage, hardware and AI-for-science names, and QQQ.
Delisted tickers (Red Hat, Hortonworks, Cloudera, Talend, Pivotal; HashiCorp after Feb 2025,
Confluent after Mar 2026, Couchbase after 2025) are often missing from Yahoo; whatever returns is kept."""
import yfinance as yf, pandas as pd, json
GROUPS = {
 "oss_origin": ["MDB", "ESTC", "GTLB", "CFLT", "HCP", "BASE"],
 "closed_saas_peers": ["SNOW", "DDOG", "CRWD", "OKTA", "TWLO", "ZS", "DOCU", "TEAM"],
 "big_tech": ["META", "GOOGL", "MSFT", "AMZN", "IBM", "ORCL", "NVDA", "AAPL", "QCOM"],
 "hardware": ["RPI.L", "SSYS", "DDD"],
 "science": ["SDGR", "RXRX"],
 "index": ["QQQ", "IGV"],
}
tick = sorted({t for v in GROUPS.values() for t in v})
d = yf.download(tick, start="2012-01-01", interval="1wk", progress=False, auto_adjust=True, threads=True)
close = d["Close"]
close.to_csv("data/prices_weekly_close.csv")
got = {t: (str(close[t].first_valid_index())[:10] if t in close and close[t].notna().any() else None,
           str(close[t].last_valid_index())[:10] if t in close and close[t].notna().any() else None) for t in tick}
json.dump({"groups": GROUPS, "coverage": got}, open("data/prices_meta.json", "w"), indent=1)
for t, (a, b) in got.items(): print(t, a, b)

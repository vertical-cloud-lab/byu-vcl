#!/usr/bin/env python3
"""Tiny event study: cumulative return vs QQQ in the 5 and 20 trading days after public relicensing
announcements by listed companies with Yahoo data (HashiCorp is delisted). Writes data/relicense_event_study.csv"""
import yfinance as yf, pandas as pd
events = [("MongoDB → SSPL", "MDB", "2018-10-16"), ("Elastic → SSPL/ELv2", "ESTC", "2021-01-14"), ("Elastic adds AGPL", "ESTC", "2024-08-29"),
          ("GitLab (no relicense; control: Q3 FY25 results)", None, None)]
px = yf.download(["MDB", "ESTC", "QQQ"], start="2018-09-01", progress=False, auto_adjust=True)["Close"]
rows = []
for lab, t, d in events:
    if not t: continue
    s = px[[t, "QQQ"]].dropna(); i = s.index.searchsorted(pd.Timestamp(d)); base = s.iloc[i - 1]
    for h in (5, 20):
        end = s.iloc[min(i - 1 + h, len(s) - 1)]
        r_s = end[t] / base[t] - 1; r_m = end["QQQ"] / base["QQQ"] - 1
        rows.append(dict(event=lab, ticker=t, date=d, horizon_days=h, stock_return=round(r_s, 3), qqq_return=round(r_m, 3), excess=round(r_s - r_m, 3)))
out = pd.DataFrame(rows); out.to_csv("data/relicense_event_study.csv", index=False); print(out.to_string(index=False))

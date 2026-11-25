#!/usr/bin/env python3
"""Market cap and reported fundamentals of the listed companies that own (or whose subsidiaries own) repositories.

Input: data/listed_targets.csv (columns entity, ticker). Yahoo Finance via yfinance, converted to US dollars at the
same day's Yahoo exchange rates. Writes data/listed_financials.csv. Run from owners/.
Yahoo figures change daily: this is a snapshot, dated in the output.
"""
import datetime as dt, time
import pandas as pd, yfinance as yf

FIELDS = ["longName", "exchange", "currency", "financialCurrency", "marketCap", "totalRevenue", "grossMargins",
          "operatingMargins", "profitMargins", "freeCashflow", "revenueGrowth", "fullTimeEmployees"]
_fx = {"USD": 1.0}


def fx(cur):
    if not cur:
        return None
    sub = {"GBp": ("GBP", 0.01), "ILA": ("ILS", 0.01), "ZAc": ("ZAR", 0.01)}  # quotes in minor units
    if cur in sub:
        major, k = sub[cur]
        v = fx(major)
        return v * k if v else None
    cur = cur.upper()
    if cur not in _fx:
        h = yf.Ticker(f"{cur}USD=X").history(period="5d")
        _fx[cur] = float(h["Close"].iloc[-1]) if len(h) else None
    return _fx[cur]


def main():
    tg = pd.read_csv("data/listed_targets.csv").drop_duplicates("ticker")
    rows = []
    for _, t in tg.iterrows():
        try:
            info = yf.Ticker(t.ticker).info
        except Exception as e:  # noqa: BLE001
            rows.append({"entity": t.entity, "ticker": t.ticker, "error": str(e)[:100]}); continue
        r = {"entity": t.entity, "ticker": t.ticker, **{k: info.get(k) for k in FIELDS}}
        q, f = fx(info.get("currency")), fx(info.get("financialCurrency") or info.get("currency"))
        r["market_cap_usd"] = r["marketCap"] * q if r.get("marketCap") and q else None
        r["revenue_usd"] = r["totalRevenue"] * f if r.get("totalRevenue") and f else None
        r["fcf_usd"] = r["freeCashflow"] * f if r.get("freeCashflow") and f else None
        rows.append(r)
        time.sleep(0.3)
        print(t.ticker, r.get("longName"), r.get("market_cap_usd"), flush=True)
    d = pd.DataFrame(rows)
    d["snapshot_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    d.to_csv("data/listed_financials.csv", index=False)


if __name__ == "__main__":
    main()

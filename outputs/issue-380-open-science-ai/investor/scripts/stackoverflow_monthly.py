#!/usr/bin/env python3
"""Monthly new Stack Overflow questions (Stack Exchange API, filter=total; deleted questions excluded) from 2018-01
to 2026-10. Writes data/stackoverflow_monthly_questions.csv. Run from investor/."""
import time, datetime as dt, requests, pandas as pd
rows = []
d = dt.date(2018, 1, 1)
while d <= dt.date(2026, 10, 1):
    nxt = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    a = int(dt.datetime(d.year, d.month, 1, tzinfo=dt.timezone.utc).timestamp())
    b = int(dt.datetime(nxt.year, nxt.month, 1, tzinfo=dt.timezone.utc).timestamp()) - 1
    r = requests.get("https://api.stackexchange.com/2.3/questions",
                     params={"site": "stackoverflow", "filter": "total", "fromdate": a, "todate": b}, timeout=60)
    j = r.json()
    if "total" not in j:
        print("stop:", j); break
    rows.append({"month": d.isoformat()[:7], "questions": j["total"]}); time.sleep(0.25)
    if j.get("backoff"): time.sleep(int(j["backoff"]) + 1)
    d = nxt
pd.DataFrame(rows).to_csv("data/stackoverflow_monthly_questions.csv", index=False)
print(len(rows), rows[:2], rows[-2:])

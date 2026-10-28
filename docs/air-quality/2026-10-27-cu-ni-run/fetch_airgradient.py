"""Download the CB 154 AirGradient's readings from the AirGradient public API.

    AIRGRADIENT_API_KEY=... python fetch_airgradient.py raw 2026-10-26T06:00Z 2026-10-28T03:00Z out.csv.gz
    AIRGRADIENT_API_KEY=... python fetch_airgradient.py past 2026-09-25T06:00Z 2026-10-28T03:00Z out.csv.gz

`raw` is every upload, about one a minute; the API keeps it for about a week
(on 2026-10-28 it went back to Oct 20) and serves at most 200 records a call,
so it is fetched 3 h at a time. `past` is 5-minute averages, kept for 150
days, at most 10 days a call. The token goes in the query string, so errors
report the path only. The monitor's serial number is its MAC address, so it
and the coordinates are dropped before saving.
"""
import datetime as dt
import os
import sys

import pandas as pd
import requests

API = "https://api.airgradient.com/public/api/v1"
LOCATION_ID = 184200  # "CB 154", the only monitor; inside the atomizer enclosure since Sep 29
STEP = {"raw": dt.timedelta(hours=3), "past": dt.timedelta(days=10)}
DROP = ["serialno", "latitude", "longitude", "locationType"]


def get(path, **params):
    r = requests.get(f"{API}{path}", params={"token": os.environ["AIRGRADIENT_API_KEY"], **params}, timeout=180)
    if r.status_code == 404:  # a window with no uploads
        return []
    if not r.ok:
        raise RuntimeError(f"AirGradient {path} returned HTTP {r.status_code}")
    return r.json()


def main(kind, start, end, out):
    t, end = dt.datetime.fromisoformat(start.replace("Z", "+00:00")), dt.datetime.fromisoformat(end.replace("Z", "+00:00"))
    rows = []
    while t < end:
        to = min(t + STEP[kind], end)
        rows += get(f"/locations/{LOCATION_ID}/measures/{kind}",
                    **{"from": t.strftime("%Y%m%dT%H%M%SZ"), "to": to.strftime("%Y%m%dT%H%M%SZ")})
        t = to
    df = pd.DataFrame(rows).drop(columns=DROP, errors="ignore")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.drop_duplicates("timestamp").sort_values("timestamp")
    df.to_csv(out, index=False)
    print(f"{len(df)} rows, {df.timestamp.min()} to {df.timestamp.max()} -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:5])

"""The comparison table in README.md: peak particle counts and time at the top
of the TVOC scale, per day, 06:00-21:00 MDT.

    python compare_days.py airgradient_1min_20261020_20261028.csv.gz airgradient_5min_20260929_20261028.csv.gz
"""
import sys

import pandas as pd

TZ = "America/Denver"
DAYS = {  # from digital-alloy-lab#159 and #219, and Gage's video titles
    "2026-10-02": "Al run (first unsupervised)",
    "2026-10-06": "Al 6067 run, 840 °C",
    "2026-10-08": "Al run, CF plate",
    "2026-10-20": "set-up only, no melt",
    "2026-10-21": "Al 4047 run, 810 °C",
    "2026-10-22": "Al 4047 run, 810 °C",
    "2026-10-26": "BN coat sprayed, in another lab's hood",
    "2026-10-27": "Cu70/Ni30 run, 1,300 °C",
}


def load(path):
    d = pd.read_csv(path, parse_dates=["timestamp"])
    return d.set_index(d.timestamp.dt.tz_convert(TZ)).sort_index()


one, five = load(sys.argv[1]), load(sys.argv[2])
rows = []
for day, what in DAYS.items():
    a, b = five.loc[f"{day} 06:00":f"{day} 21:00"], one.loc[f"{day} 06:00":f"{day} 21:00"]
    row = {"date": day, "what": what,
           "0.3um count, max 5-min": a.pm003Count.max(),
           "TVOC index >= 400, min": 5 * int((a.tvocIndex >= 400).sum())}
    if len(b):
        row.update({"0.3um count, max 1-min": b.pm003Count.max(),
                    "corrected PM2.5, max 1-min": b.pm02_corrected.max(),
                    "raw PM2.5, max 1-min": b.pm02.max(),
                    "min >= 5 ug/m3": int((b.pm02_corrected >= 5).sum())})
    rows.append(row)
print(pd.DataFrame(rows).to_markdown(index=False))

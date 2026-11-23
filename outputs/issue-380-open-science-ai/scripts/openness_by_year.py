#!/usr/bin/env python3
"""Openness as a function of calendar time, by sector: mean openness (0-4) of organizations operating in each
year, reconstructed from each case file's founding year, initial/current openness and dated relicensing
events (same segment logic as the lane charts). Writes data/openness_by_year_sector.csv and
figures/openness_by_year_sector.png, plus an animated MP4 (video/extras/openness_by_year_sector.mp4)."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import scenes_companies as sc
M = sc.M; E = sc.E
SECT = {"A": "Commercial OSS software", "B": "Commercial OSS software", "C": "Big Tech & AI labs", "D": "Hardware",
        "E": "Physical science (companies & infrastructure)", "F": "Physical science (companies & infrastructure)", "G": "AM & lab instruments, open-science infra"}
rows = []
for g, sect in SECT.items():
    L = sc.lanes(M[M.group == g], E)
    for l in L:
        for y in range(1990, 2027):
            lvl = None
            for a, b, o in l["segs"]:
                if a <= y + 0.5 < b: lvl = o
            if lvl is not None: rows.append(dict(sector=sect, year=y, org=l["lab"], open=lvl))
d = pd.DataFrame(rows)
t = d.groupby(["sector", "year"]).agg(mean_open=("open", "mean"), n=("org", "nunique")).reset_index()
t.to_csv("data/openness_by_year_sector.csv", index=False)
print(t[t.year.isin([2000, 2010, 2015, 2020, 2023, 2026])].pivot_table(index="year", columns="sector", values="mean_open").round(2).to_string())
series = [("Commercial OSS software", BLUE), ("Hardware", ORANGE), ("Physical science (companies & infrastructure)", AQUA), ("Big Tech & AI labs", YELLOW)]
fig, ax = fig_ax("Openness as a function of time, by sector", "Mean openness (0 closed – 4 open + open governance) of case-study organizations operating each year (n ≥ 5)",
                 rect=(0.07, 0.13, 0.70, 0.68))
source_note(fig, "Source: data/openness_by_year_sector.csv, rebuilt from the case files (founding year, openness, dated licence changes). Survivor sample, not a census.")
ax.set_xlim(1995, 2026.5); ax.set_ylim(0, 4); ax.set_ylabel("mean openness score")
lines = {}; labs = {}
for s, c in series:
    lines[s], = ax.plot([], [], color=c, label=s); labs[s] = ax.text(0, 0, "", fontsize=16, color=TEXT, va="center")
ax.legend(loc="upper left", fontsize=15, ncol=2)
def update(p):
    xmax = 1995 + p * 31.5
    for s, c in series:
        x = t[(t.sector == s) & (t.n >= 5) & (t.year <= xmax)]
        lines[s].set_data(x.year, x.mean_open)
        if len(x): labs[s].set_position((x.year.iloc[-1] + 0.3, x.mean_open.iloc[-1])); labs[s].set_text(f"{x.mean_open.iloc[-1]:.2f} (n={int(x.n.iloc[-1])})" if p >= 1 else "")
    if p >= 1:
        order = sorted(series, key=lambda sc_: labs[sc_[0]].get_position()[1]); last = -9
        for s_, c_ in order:
            xx, yy = labs[s_].get_position(); yy = max(yy, last + 0.12); labs[s_].set_position((xx, yy)); last = yy
os.makedirs("video/extras", exist_ok=True)
render(fig, update, 14, "video/extras/openness_by_year_sector.mp4", "figures/openness_by_year_sector.png")
print("saved")

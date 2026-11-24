#!/usr/bin/env python3
"""Openness over calendar time in six sectors, as small multiples (one sector per panel, the others in gray).

Follows up the independent review (REVIEW_FINDINGS.md, row 1): the four-sector chart averaged closed
AI-for-science companies (group E) with open science infrastructure (group F) and left out group G. Six
series can't share one colour scale safely (no six-colour subset of the palette clears the all-pairs CVD
check), so each sector gets its own panel. Same reconstruction as scripts/openness_by_year.py.
Writes data/openness_by_year_six_sectors.csv, figures/openness_by_year_six_sectors.png and
video/extras/openness_by_year_six_sectors.mp4."""
import sys, os, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import scenes_companies as sc
M = sc.M; E = sc.E
SECT = {"A": "Commercial OSS software", "B": "Commercial OSS software", "C": "Big Tech & AI labs", "D": "Hardware",
        "E": "Lab automation & AI-for-science firms", "F": "Science software & infrastructure",
        "G": "AM, lab instruments & publishing"}
ORDER = ["Commercial OSS software", "Big Tech & AI labs", "Hardware",
         "Lab automation & AI-for-science firms", "Science software & infrastructure", "AM, lab instruments & publishing"]
rows = []
for g, sect in SECT.items():
    for l in sc.lanes(M[M.group == g], E):
        for y in range(1990, 2027):
            lvl = None
            for a, b, o in l["segs"]:
                if a <= y + 0.5 < b: lvl = o
            if lvl is not None: rows.append(dict(sector=sect, group=g, year=y, org=l["lab"], open=lvl))
d = pd.DataFrame(rows)
t = d.groupby(["sector", "year"]).agg(mean_open=("open", "mean"), n=("org", "nunique"),
                                      share_0=("open", lambda s: (s == 0).mean()), share_3_4=("open", lambda s: (s >= 3).mean())).reset_index()
t.to_csv("data/openness_by_year_six_sectors.csv", index=False)
print(t[t.year.isin([2000, 2010, 2020, 2026])].pivot_table(index="year", columns="sector", values="mean_open").round(2).T.to_string())

fig = plt.figure(figsize=(W, H), dpi=DPI)
fig.text(0.05, 0.935, "Science splits into closed firms and open infrastructure", fontsize=32, fontweight="bold", color=TEXT, va="center")
fig.text(0.05, 0.885, "Mean openness (0 closed – 4 open + open governance) of case-study organizations operating each year (n ≥ 5). Gray: the other five sectors.",
         fontsize=18, color=TEXT2, va="center")
fig.text(0.05, 0.03, "Source: data/openness_by_year_six_sectors.csv, rebuilt from case files A–G. Survivor sample, not a census; "
         "yearly means also move as firms enter.", fontsize=13, color=MUTED, va="center")
axes = []
for i, s in enumerate(ORDER):
    r, c = divmod(i, 3)
    ax = fig.add_axes((0.05 + c * 0.315, 0.50 - r * 0.40, 0.27, 0.30))
    ax.set_xlim(1995, 2026.5); ax.set_ylim(0, 4); ax.set_yticks([0, 1, 2, 3, 4]); ax.set_xticks([2000, 2010, 2020])
    ax.tick_params(labelsize=15)
    if c: ax.set_yticklabels([])
    if r == 0: ax.set_xticklabels([])
    axes.append(ax)
ctx, main, lab, ttl, dot = {}, {}, {}, {}, {}
for ax, s in zip(axes, ORDER):
    ctx[s] = [ax.plot([], [], color=MUTED, lw=1.5, alpha=0.55)[0] for _ in ORDER if _ != s]
    main[s], = ax.plot([], [], color=BLUE, lw=LW)
    lab[s] = ax.text(2026.3, 3.85, "", fontsize=16, color=TEXT, va="top", ha="right")
    dot[s], = ax.plot([], [], "o", ms=9, color=BLUE, mec=SURFACE, mew=2, zorder=5)
    ttl[s] = ax.set_title(s, fontsize=19, color=TEXT, loc="left", pad=8)

def series(s, xmax):
    return t[(t.sector == s) & (t.n >= 5) & (t.year <= xmax)]

def update(p):
    xmax = 1995 + p * 31.5
    for s in ORDER:
        others = [o for o in ORDER if o != s]
        for ln, o in zip(ctx[s], others):
            x = series(o, xmax); ln.set_data(x.year, x.mean_open)
        x = series(s, xmax); main[s].set_data(x.year, x.mean_open)
        if p >= 1 and len(x):
            last = x.iloc[-1]
            lab[s].set_text(f"2026: {last.mean_open:.2f} (n={int(last.n)})"); dot[s].set_data([last.year], [last.mean_open])
        else:
            lab[s].set_text(""); dot[s].set_data([], [])

os.makedirs("video/extras", exist_ok=True)
render(fig, update, 12, "video/extras/openness_by_year_six_sectors.mp4", "figures/openness_by_year_six_sectors.png")
print("saved")

#!/usr/bin/env python3
"""US open-access share (OpenAlex, all US articles and industry) with US federal open-science / open-AI policy milestones."""
import sys, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
df = pd.read_csv("data/openalex_us_oa_by_sector.csv")
fig, ax = fig_ax("US open-access share and the federal policies around it", "Share of US-affiliated articles free to read (OpenAlex); US federal open-science and open-AI milestones",
                 rect=(0.07, 0.13, 0.86, 0.66))
source_note(fig, "Sources: data/openalex_us_oa_by_sector.csv; policy dates from the Edison open-science-return and sector-trends answers and from primary pages fetched through the Pi.")
for key, lab, c in [("any_us", "All US articles", BLUE), ("company", "Industry", ORANGE), ("government", "Government", AQUA)]:
    t = df[(df.scope == "all") & (df.inst_type == key) & df.year.between(2000, 2025)].sort_values("year")
    ax.plot(t.year, t.oa_share, color=c, label=lab)
ax.set_xlim(2000, 2026.5); ax.set_ylim(0, 1.05); ax.yaxis.set_major_formatter(mt.PercentFormatter(1.0)); ax.legend(loc="upper left", fontsize=16)
events = [(2008, "NIH Public Access\nPolicy mandatory"), (2013, "OSTP Holdren memo\n(12-month embargo)"), (2022.6, "OSTP Nelson memo\n(no embargo by 2025)"),
          (2023, "NIH data-sharing\npolicy"), (2024.5, "NTIA: no case yet to\nrestrict open weights"), (2025.5, "AI Action Plan;\nGenesis Mission")]
for i, (x, lab) in enumerate(events):
    ax.axvline(x, color=TEXT2, lw=1, ls=(0, (3, 4)))
    ax.text(x - 0.15, 0.14 + (i % 3) * 0.13, lab, fontsize=13, color=TEXT, ha="right", va="bottom")
fig.savefig("figures/policy_timeline.png", dpi=DPI); print("saved")

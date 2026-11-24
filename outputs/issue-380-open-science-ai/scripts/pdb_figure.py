#!/usr/bin/env python3
"""Figure: 50 years of open structural data (PDB releases per year and cumulative), with AlphaFold milestones."""
import sys, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
d = pd.read_csv("data/pdb_released_per_year.csv"); d = d[d.year >= 1976]
fig, ax = fig_ax("Fifty years of open data trained the AI: the PDB",
                 "Protein Data Bank structures released per year, all free to reuse; CC0 since 2021",
                 rect=(0.08, 0.13, 0.82, 0.66))
source_note(fig, "Source: RCSB PDB Search API, count of entries by initial release date (queried 2026-11-23; 2026 is year to date).\nAlphaFold 2 milestones: CASP14 (2020), Nature paper and open code (2021), Nobel Prize in Chemistry (2024).")
ax.bar(d.year, d.released, color=BLUE, width=0.8, label="Released that year")
ax.set_ylim(0, 21000); ax.yaxis.set_major_locator(mt.MultipleLocator(5000))
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1000:g}k")); ax.set_ylabel("structures released per year"); ax.set_xlim(1975, 2027)
c2020 = int(d[d.year == 2020].cumulative.iloc[0]); last = d.iloc[-1]
for y, lab in [(2020, f"2020: AlphaFold 2 at CASP14 ({c2020/1000:.0f}k open structures by then)"), (2024, "2024: Nobel Prize in Chemistry")]:
    ax.axvline(y, color=TEXT2, lw=1.2, ls=(0, (4, 4)))
ax.text(2019.6, 20600, f"2020: AlphaFold 2 at CASP14\n{c2020/1000:.0f}k open structures by then", ha="right", va="top", fontsize=17, color=TEXT)
ax.text(2024.4, 20600, "2024: Nobel Prize", ha="left", va="top", fontsize=17, color=TEXT)
ax.text(1977, 17500, f"{int(last.cumulative):,} structures in total by {int(last.year)}", fontsize=22, color=TEXT, fontweight="bold")
# single series: the subtitle names it, so no legend
fig.savefig("figures/pdb_growth.png", dpi=DPI); print("saved", c2020, int(last.cumulative))

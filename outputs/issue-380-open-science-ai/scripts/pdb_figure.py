#!/usr/bin/env python3
"""Figure: 50 years of open structural data (PDB releases per year and cumulative), with AlphaFold milestones."""
import sys, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
d = pd.read_csv("data/pdb_released_per_year.csv"); d = d[d.year >= 1976]
fig, ax = fig_ax("Fifty years of open data trained the AI: the Protein Data Bank",
                 "Structures released per year (bars) and cumulative (line), all free to reuse; CC0 since 2021",
                 rect=(0.08, 0.13, 0.82, 0.66))
source_note(fig, "Source: RCSB PDB Search API, count of entries by initial release date (queried 2026-11-23; 2026 is year to date). AlphaFold 2 milestones: CASP14 (2020), Nature paper and open code (2021), Nobel Prize (2024).")
ax.bar(d.year, d.released, color=BLUE, width=0.8, label="Released that year")
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v/1000:.0f}k")); ax.set_ylabel("structures released per year"); ax.set_xlim(1975, 2027)
c2020 = int(d[d.year == 2020].cumulative.iloc[0]); last = d.iloc[-1]
for y, lab in [(2020, f"2020: AlphaFold 2 at CASP14 ({c2020/1000:.0f}k open structures by then)"), (2024, "2024: Nobel Prize in Chemistry")]:
    ax.axvline(y, color=TEXT2, lw=1.2, ls=(0, (4, 4)))
ax.text(2019.6, d.released.max() * 1.02, f"2020: AlphaFold 2 at CASP14\n{c2020/1000:.0f}k open structures by then", ha="right", va="top", fontsize=17, color=TEXT)
ax.text(2023.6, d.released.max() * 0.80, "2024:\nNobel Prize", ha="right", va="top", fontsize=17, color=TEXT)
ax.text(1977, d.released.max() * 0.9, f"{int(last.cumulative):,} structures in total by {int(last.year)}", fontsize=22, color=TEXT, fontweight="bold")
ax.legend(loc="upper left", bbox_to_anchor=(0, 0.85))
fig.savefig("figures/pdb_growth.png", dpi=DPI); print("saved", c2020, int(last.cumulative))

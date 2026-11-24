#!/usr/bin/env python3
"""Figure: licence-change rates by starting openness (groups A-F, 2000-26), all organizations vs US-headquartered.
Reads data/licence_events_by_start_openness.csv and data/licence_events_by_start_openness_us.csv
(scripts/licence_rate_per_org_year.py). Writes figures/convergence_by_start_openness.png."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from viz_style import *
a = pd.read_csv("data/licence_events_by_start_openness.csv")
u = pd.read_csv("data/licence_events_by_start_openness_us.csv")
fig = plt.figure(figsize=(W, H), dpi=DPI)
fig.text(0.06, 0.92, "Organizations converge toward the middle", fontsize=36, fontweight="bold", color=TEXT, va="center")
fig.text(0.06, 0.865, "Closing and opening moves per 100 organization-years, by openness at founding (groups A–F, 2000–26)",
         fontsize=20, color=TEXT2, va="center")
fig.text(0.06, 0.035, "Source: data/licence_events_by_start_openness*.csv (scripts/licence_rate_per_org_year.py). Partly mechanical: a firm at 0 "
         "has little left to close, one at 4 nothing left to open.", fontsize=13, color=MUTED, va="center")
labels = ["Closed at founding (0)", "Mixed (1–2)", "Open at founding (3–4)"]
x = np.arange(3); w = 0.36
for j, (d, title) in enumerate([(a, "All organizations"), (u, "US-headquartered only")]):
    ax = fig.add_axes((0.06 + j * 0.48, 0.14, 0.42, 0.62))
    ax.set_title(f"{title} (n = {int(d.n_orgs.sum())})", loc="left", fontsize=22, color=TEXT)
    bc = ax.bar(x - w / 2 - 0.01, d.closing_per_100_org_years, width=w, color=ORANGE, label="Closing moves")
    bo = ax.bar(x + w / 2 + 0.01, d.opening_per_100_org_years, width=w, color=BLUE, label="Opening moves")
    for bars in (bc, bo):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.06, f"{b.get_height():.1f}", ha="center", va="bottom", fontsize=16, color=TEXT)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=16, color=TEXT); ax.set_ylim(0, 4.8); ax.grid(axis="x", visible=False)
    if j == 0:
        ax.set_ylabel("moves per 100 organization-years"); ax.legend(loc="upper center", fontsize=16)
    else:
        ax.set_yticklabels([])
fig.savefig("figures/convergence_by_start_openness.png", dpi=DPI); print("saved")

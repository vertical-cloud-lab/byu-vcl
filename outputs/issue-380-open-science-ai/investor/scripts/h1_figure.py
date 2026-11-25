#!/usr/bin/env python3
"""H1 figure: what $1 at each listing's offer price became, relative to $1 put in QQQ over the same window
(public-market equivalent, log scale). Pre-registered cohorts; JFrog excluded (ambiguous, reported both ways)."""
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from viz import style, OPEN, CLOSED, INK, INK2, MUTED, SURFACE
style()
R = pd.read_csv("data/h1_returns.csv")
R = R[R.cohort.isin(["open_source", "closed"]) & (R.company != "JFrog")].copy()
R["pme"] = R.multiple_from_offer / R.qqq_multiple
fig, ax = plt.subplots(figsize=(11, 6.4))
ys = {"open_source": 1.0, "closed": 0.0}; cols = {"open_source": OPEN, "closed": CLOSED}
label = set(R[R.cohort == "open_source"].company) | {"Palantir", "Cloudflare", "Datadog", "Domo", "Sumo Logic",
                                                     "Atlassian", "Jamf", "Informatica", "New Relic"}
for coh, g in R.groupby("cohort"):
    g = g.sort_values("pme"); n = len(g)
    off = np.tile([0.3, 0.15, 0.0, -0.15, -0.3], n // 5 + 1)[:n]   # deterministic 4-row stagger so labels don't collide
    y = ys[coh] + off
    listed = (g.status == "listed").values
    med = g.pme.median()
    ax.scatter(g.pme[listed], y[listed], s=70, color=cols[coh], edgecolor=SURFACE, linewidth=1.5, zorder=6)
    ax.scatter(g.pme[~listed], y[~listed], s=70, facecolor=SURFACE, edgecolor=cols[coh], linewidth=2, zorder=6)
    ax.plot([med, med], [ys[coh] - 0.36, ys[coh] + 0.36], color=INK, lw=2.2, zorder=2)
    ax.text(med, ys[coh] + 0.39, f"median {med:.2f}", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=INK)
    for (_, r), yy in zip(g.iterrows(), y):
        if r.company in label:
            left = r.pme < med                                   # labels point away from the crowded middle
            ax.annotate(r.company, (r.pme, yy), xytext=(-7 if left else 7, 0), textcoords="offset points",
                        ha="right" if left else "left", va="center", fontsize=7.8, color=INK2, zorder=5,
                        bbox=dict(boxstyle="square,pad=0.05", fc=SURFACE, ec="none", alpha=0.8))
ax.set_xscale("log"); ax.axvline(1, color=MUTED, lw=1.2, zorder=1)
ax.text(1.04, -0.55, "= same as QQQ", fontsize=8.5, color=INK2)
ax.set_xlim(0.025, 14); ax.set_xticks([0.05, 0.1, 0.25, 0.5, 1, 2, 4, 8]); ax.set_xticklabels(["0.05", "0.1", "0.25", "0.5", "1", "2", "4", "8"])
ax.set_yticks([0, 1]); ax.set_ylim(-0.6, 1.62); ax.grid(axis="y", visible=False)
ax.set_yticklabels([f"Closed source\n(n = {(R.cohort == 'closed').sum()})", f"Open-source origin\n(n = {(R.cohort == 'open_source').sum()})"])
ax.set_xlabel("Value of \\$1 invested at the offer price, relative to \\$1 in QQQ over the same window (log scale)")
ax.set_title("Software listings 2014–22: open-source origin earned no premium")
leg = [Line2D([0], [0], marker="o", color="none", markerfacecolor=INK2, markeredgecolor=INK2, markersize=8, label="still listed (to 2026-11-24)"),
       Line2D([0], [0], marker="o", color="none", markerfacecolor=SURFACE, markeredgecolor=INK2, markeredgewidth=2, markersize=8, label="bought out or merged (deal value)")]
ax.legend(handles=leg, loc="upper left", fontsize=9)
fig.text(0.01, -0.03, "Open-source cohort pre-registered; closed cohort = infrastructure software chosen by category rule. Medians differ (0.52 vs 0.84), but with listing-year "
         "controls the gap is not significant (ratio 1.17, 95% CI 0.54–2.4).\nSeven of the 14 open-source listings came in 2021–22. "
         "Sources: deal terms and offer prices in data/cohort_listings_verified.csv; prices from Yahoo Finance.", fontsize=8, color=INK2)
fig.savefig("figures/h1_listing_returns.png"); print("saved")

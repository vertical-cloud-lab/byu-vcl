#!/usr/bin/env python3
"""Figure for H1: each listing's annualized return from the offer price, minus QQQ's over the same window."""
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from viz import style, OPEN, CLOSED, INK, INK2, MUTED
style()
R = pd.read_csv("data/h1_returns.csv")
R = R[R.cohort.isin(["open_source", "closed"])].copy()
R.loc[R.company == "JFrog", "cohort"] = "closed"          # pre-registered main analysis
R = R.sort_values("excess_vs_qqq_offer")
fig, ax = plt.subplots(figsize=(10.5, 6.2))
ys = {"open_source": 1.0, "closed": 0.0}
rng = np.random.default_rng(3)
label_these = {"MongoDB", "MariaDB", "HashiCorp", "Confluent", "Elastic", "GitLab", "Talend", "MuleSoft",
               "Palantir", "Snowflake", "Datadog", "Sumo Logic", "New Relic", "Unity Software", "Couchbase", "SUSE"}
for coh, g in R.groupby("cohort"):
    col = OPEN if coh == "open_source" else CLOSED
    y = ys[coh] + rng.uniform(-0.16, 0.16, len(g))
    listed = g.status == "listed"
    ax.scatter(g.excess_vs_qqq_offer[listed] * 100, y[listed.values], s=64, color=col, edgecolor="#fcfcfb", linewidth=1.5, zorder=3)
    ax.scatter(g.excess_vs_qqq_offer[~listed] * 100, y[~listed.values], s=64, facecolor="#fcfcfb", edgecolor=col, linewidth=2, zorder=3)
    med = g.excess_vs_qqq_offer.median() * 100
    ax.plot([med, med], [ys[coh] - 0.3, ys[coh] + 0.3], color=INK, lw=2, zorder=4)
    ax.text(med, ys[coh] + 0.34, f"median {med:+.0f} pts/yr", ha="center", va="bottom", color=INK, fontsize=9.5, fontweight="bold")
    for (_, r), yy in zip(g.iterrows(), y):
        if r.company in label_these:
            ax.annotate(r.company, (r.excess_vs_qqq_offer * 100, yy), xytext=(0, -13), textcoords="offset points",
                        ha="center", fontsize=8, color=INK2)
ax.axvline(0, color=MUTED, lw=1)
ax.set_yticks([0, 1]); ax.set_yticklabels([f"Closed source\n(n = {(R.cohort=='closed').sum()})", f"Open-source origin\n(n = {(R.cohort=='open_source').sum()})"])
ax.set_ylim(-0.6, 1.65); ax.grid(axis="y", visible=False)
ax.set_xlabel("Annualized return from the offer price, minus QQQ over the same window (percentage points)")
ax.set_title("What public investors earned: every 2014–22 listing in infrastructure software")
ax.text(0, -0.2, "Filled: still listed (to 2026-11-24). Hollow: bought out, valued at the deal price. "
        "Open-source cohort pre-registered; closed cohort chosen by category rule.", transform=ax.transAxes, fontsize=8.5, color=INK2)
fig.savefig("figures/h1_listing_returns.png"); print("saved")

#!/usr/bin/env python3
"""Figures for the owners analysis. Run from owners/ after owners_analysis.py.

figures/who_owns_the_stars.png: share of stars by owner class, for the top 2,000 repos and the science topics.
figures/popularity_vs_value.png: org stars against latest disclosed value for core companies, and what became of
the core companies in the top 2,000.
Palette: the dataviz skill's reference categorical slots, validated with its validate_palette.js (adjacent pairs
for the stacked bars, all pairs for the three scatter colours). Segments carry direct labels for contrast relief.
"""
import json
import matplotlib as mpl, matplotlib.pyplot as plt, numpy as np, pandas as pd
from matplotlib.ticker import FuncFormatter

SURFACE, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8985", "#e6e5e1"
SLOTS = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17"]
mpl.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 10.5, "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False, "figure.dpi": 110, "savefig.dpi": 160, "savefig.bbox": "tight"})

exec(open("scripts/owners_analysis.py").read().split("if __name__")[0])
GROUPS = [("Company that sells it", ["core"]), ("Company that gives it away\n(complement)", ["complement"]),
          ("Nonprofit or foundation", ["nonprofit"]), ("University or government", ["academic", "government"]),
          ("Community project", ["community", "unknown"]), ("Personal account", ["individual"])]
LAB_TOPICS = {"lab-automation", "laboratory-automation", "self-driving-lab", "autonomous-experimentation",
              "materials-science", "materials-informatics", "chemistry", "computational-chemistry", "cheminformatics",
              "quantum-chemistry", "molecular-dynamics", "drug-discovery"}


def shares(d):
    s = d.groupby("cls").stars.sum()
    tot = s.sum()
    return [sum(s.get(c, 0) for c in cs) / tot for _, cs in GROUPS]


def fig_ownership():
    a, b = frame(A), frame(B)
    lab = b[b.topic_queries.str.split(";").apply(lambda t: bool(set(t) & LAB_TOPICS))]
    rows = [(f"Top 2,000 repos on GitHub\n{len(a):,} software repos, {a.stars.sum() / 1e6:.0f}M stars", shares(a)),
            (f"22 science topics\n{len(b):,} repos, {b.stars.sum() / 1e6:.2f}M stars", shares(b)),
            (f"Chemistry, materials, lab automation\n{len(lab):,} repos, {lab.stars.sum() / 1e3:.0f}k stars",
             shares(lab))]
    fig, ax = plt.subplots(figsize=(10.5, 3.9))
    y = np.arange(len(rows))[::-1]
    for (label, sh), yy in zip(rows, y):
        left = 0
        for k, v in enumerate(sh):
            ax.barh(yy, v, left=left, height=0.58, color=SLOTS[k], edgecolor=SURFACE, linewidth=2)
            if v >= 0.05:
                ax.text(left + v / 2, yy, f"{v:.0%}", ha="center", va="center", fontsize=9.5, color=INK)
            left += v
    ax.set_yticks(y, [r[0] for r in rows], fontsize=9.5)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(axis="y", visible=False); ax.tick_params(axis="y", length=0)
    ax.set_axisbelow(True)
    ax.set_title("Who owns the stars: share of GitHub stars on software repositories, by owner", pad=50)
    handles = [mpl.patches.Patch(color=SLOTS[k], label=g[0].replace("\n", " ")) for k, g in enumerate(GROUPS)]
    ax.legend(handles=handles, ncol=3, loc="lower left", bbox_to_anchor=(0, 1.01), fontsize=9, handlelength=1.2,
              columnspacing=1.2, borderaxespad=0.2)
    fig.text(0, -0.04, "GitHub search, 2026-11-25. Owners classified before any financial data was pulled. "
             "Lists, books and courses excluded by the pre-registered rule.", fontsize=8.5, color=INK2)
    fig.savefig("figures/who_owns_the_stars.png")


def money(v, _=None):
    for k, s in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
        if v >= k:
            return f"${v / k:.0f}{s}" if v / k >= 10 else f"${v / k:.1f}{s}".replace(".0", "")
    return f"${v:.0f}"


def fig_value():
    try:
        F = pd.read_csv("data/core_financials.csv")
    except FileNotFoundError:
        return
    stars = pd.concat([A, B]).drop_duplicates("full_name").groupby("owner").stars.sum()
    F["org_stars"] = F.owner.map(stars)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.45, 1]})
    v = F.dropna(subset=["latest_value_usd"])
    v = v[v.latest_value_usd > 0]
    groups = [("Listed", "listed", SLOTS[0]), ("Acquired (price)", "acquired", SLOTS[1]),
              ("Private (last valuation)", "private", SLOTS[2])]
    for lab, st, col in groups:
        s = v[v.status == st]
        ax.scatter(s.org_stars, s.latest_value_usd, s=34, color=col, edgecolor=SURFACE, linewidth=1.2, label=lab,
                   zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(money))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1000:.0f}k" if x >= 1000 else f"{x:.0f}"))
    ax.set_xlabel("Stars on the company's repos in the two frames"); ax.set_ylabel("Latest disclosed value")
    res = json.load(open("data/results_summary.json")).get("H8", [])
    r = next((x for x in res if x["measure"] == "latest value (disclosed)"), None)
    sub = f"Spearman ρ = {r['spearman_rho']:.2f} (95% CI {r['ci_low']:.2f} to {r['ci_high']:.2f}), n = {r['n']}" if r else ""
    ax.set_title("Popularity and value, companies that sell the project", pad=8)
    ax.text(0, 1.0, sub, transform=ax.transAxes, fontsize=9, color=INK2, va="bottom")
    for name in v.sort_values("latest_value_usd", ascending=False).head(6).itertuples():
        ax.annotate(name.entity.split(" (")[0], (name.org_stars, name.latest_value_usd), fontsize=8, color=INK2,
                    xytext=(4, 3), textcoords="offset points")
    ax.legend(loc="lower right", fontsize=8.5)
    fa = F[F.in_frame_a == 1]
    order = [("Private", "private"), ("Acquired", "acquired"), ("Listed", "listed"), ("Shut down", "shut_down"),
             ("Unknown", "unknown")]
    cnt = [int((fa.status == k).sum()) for _, k in order]
    yy = np.arange(len(order))[::-1]
    bx.barh(yy, cnt, color=SLOTS[0], height=0.6)
    for y0, c in zip(yy, cnt):
        bx.text(c + max(cnt) * 0.01, y0, str(c), va="center", fontsize=9.5)
    bx.set_yticks(yy, [o[0] for o in order]); bx.grid(axis="y", visible=False); bx.tick_params(axis="y", length=0)
    e1 = int((fa.ever_1b == "yes").sum())
    bx.set_title(f"What became of them ({len(fa)} in the top 2,000)", pad=8)
    bx.text(0, 1.0, f"{e1} ever reached a disclosed value of $1B or more", transform=bx.transAxes, fontsize=9,
            color=INK2, va="bottom")
    bx.set_xlabel("Companies")
    fig.text(0, -0.03, "Values are market caps (Yahoo, 2026-11-25), disclosed acquisition prices or last disclosed "
             "private valuations, each with a source in data/core_financials.csv. Undisclosed values are omitted.",
             fontsize=8.5, color=INK2)
    fig.tight_layout()
    fig.savefig("figures/popularity_vs_value.png")


if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)
    fig_ownership()
    fig_value()

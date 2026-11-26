#!/usr/bin/env python3
"""Figures for FUNDERS.md: the funders that backed the most open-source-minded ventures, and the mix of funder types
by kind of venture. Palette: the dataviz skill's reference categorical slots (validated, light mode); types get a
fixed slot whatever their rank. Run from funders/ after build_funders.py."""
import collections, csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts"))
from viz import style, INK, INK2, MUTED, SURFACE  # noqa: E402

style()
GROUPS = [  # (label, types, colour) in fixed slot order
    ("Venture firm", {"venture_firm"}, "#257de0"),
    ("Corporate or strategic", {"corporate_venture", "company"}, "#f47230"),
    ("Accelerator or studio", {"accelerator"}, "#00b894"),
    ("Growth, crossover, PE or state", {"growth_pe_hedge", "public_investor", "bank_or_debt"}, "#f2a600"),
    ("Person (angel)", {"angel"}, "#ee7fac"),
    ("Grant, crowd or crypto", {"philanthropy", "government_grant", "crowdfunding", "crypto_fund_or_dao"}, "#008a17"),
    ("Unclassified", {"unclassified", "other"}, "#8a8985"),
]
UNI = [("U1", "U1: companies behind\nthe most-starred projects"), ("U2", "U2: open hardware,\nscience and lab"),
       ("U3", "U3: notable COSS and\nopen-weight AI"), ("U4", "U4: young open-source\nstartups (YC, ROSS)")]


def group_of(t):
    for lab, ts, col in GROUPS:
        if t in ts:
            return lab, col
    return GROUPS[-1][0], GROUPS[-1][2]


def main():
    inv = {r["investor"]: r for r in csv.DictReader(open("data/investors.csv"))}
    links = list(csv.DictReader(open("data/investor_links.csv")))
    os.makedirs("figures", exist_ok=True)
    # 1. top funders across U1-U3
    cnt, led = collections.Counter(), collections.Counter()
    for l in links:
        if l["universe"] in ("U1", "U2", "U3"):
            cnt[l["investor"]] += 1
            led[l["investor"]] += int(l["led"]) > 0
    top = cnt.most_common(30)[::-1]
    fig, ax = plt.subplots(figsize=(9.2, 9.6))
    ax.set_axisbelow(True)
    used = []
    for i, (name, c) in enumerate(top):
        lab, col = group_of(inv.get(name, {}).get("type", "unclassified"))
        used.append(lab)
        ax.barh(i, c, height=0.72, color=col, edgecolor=SURFACE, linewidth=2)
        ax.text(c + 0.3, i, f"{c}" + (f"  (led {led[name]})" if led[name] else ""), va="center", fontsize=9, color=INK2)
    ax.set_yticks(range(len(top)), [n for n, _ in top], fontsize=9.5)
    ax.set_xlabel("Open-source-minded ventures backed (U1–U3, one count per venture)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(c for _, c in top) * 1.22)
    ax.set_title("Who has backed the most open-source-minded ventures", pad=26)
    ax.text(0, 1.01, "Funders named in public announcements, filings and company pages; 640 hand-researched ventures",
            transform=ax.transAxes, fontsize=9, color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=col) for lab, _, col in GROUPS if lab in used]
    ax.legend(handles, [lab for lab, _, _ in GROUPS if lab in used], loc="lower right", fontsize=9)
    fig.savefig("figures/top_funders.png")
    plt.close(fig)
    # 2. funder-type mix by universe (share of investor-venture links)
    mix = collections.defaultdict(collections.Counter)
    for l in links:
        lab, _ = group_of(inv.get(l["investor"], {}).get("type", "unclassified"))
        mix[l["universe"]][lab] += 1
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    ax.set_axisbelow(True)
    for i, (u, ulab) in enumerate(UNI[::-1]):
        tot = sum(mix[u].values()) or 1
        left = 0
        for lab, _, col in GROUPS:
            w = 100 * mix[u][lab] / tot
            if w <= 0:
                continue
            ax.barh(i, w, left=left, height=0.62, color=col, edgecolor=SURFACE, linewidth=2)
            if w >= 7:
                ax.text(left + w / 2, i, f"{w:.0f}%", ha="center", va="center", fontsize=8.5, color=INK)
            left += w
        ax.text(101, i, f"n = {tot}", va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(UNI)), [u for _, u in UNI[::-1]], fontsize=9)
    ax.set_xlim(0, 112)
    ax.set_xlabel("Share of funder–venture links (%)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Who funds which kind of open venture", pad=34)
    handles = [plt.Rectangle((0, 0), 1, 1, color=col) for _, _, col in GROUPS]
    ax.legend(handles, [lab for lab, _, _ in GROUPS], loc="lower left", bbox_to_anchor=(0, 1.0), ncol=4, fontsize=8.5,
              handlelength=1.2, columnspacing=1.0)
    fig.savefig("figures/funder_mix.png")
    plt.close(fig)
    print("figures/top_funders.png, figures/funder_mix.png")


if __name__ == "__main__":
    main()

"""Figures for the twin's benchmarks and checks -> out/twin/*.png

    python3 -m twin.figures            # all of them (needs out/twin/runs/*.jsonl from twin.bench)

Colours: the validated reference palette's first three categorical slots (blue, orange, aqua), one per policy, in a
fixed order; every line is also labelled directly, since two of the three are under 3:1 on the light surface.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "out" / "twin"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
POL = {"cost_aware": ("#2a78d6", "cost-aware network surrogate"), "tiered": ("#eb6834", "tiered CALPHAD screening"),
       "random": ("#1baf7a", "random, full chain")}
CAMP = {"flaime_al": "FLAIME: Al alloys for LPBF", "onr_cu": "ONR YIP: Cu alloys for blown-powder DED"}


def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                         "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                         "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
                         "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
                         "axes.titlesize": 11, "axes.titleweight": "bold", "legend.frameon": False})
    return plt


def _curves(rows, camp, xs, col):
    from twin.bench import step_at
    return np.array([step_at(r["campaigns"][camp]["curve"], xs, col) for r in rows])


def best_vs(rows_by_policy, col, xlabel, xs, fname, title):
    plt = _style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    for ax, camp in zip(axes, CAMP):
        xx = xs[camp]
        for pol, rows in rows_by_policy.items():
            if not rows:
                continue
            Y = _curves(rows, camp, xx, col)
            m, se = Y.mean(0), Y.std(0, ddof=1) / math.sqrt(len(Y)) if len(Y) > 1 else 0 * Y.mean(0)
            colr, lab = POL[pol]
            xp = xx / 1000.0 if col == 1 else xx
            ax.fill_between(xp, m - se, m + se, color=colr, alpha=0.15, linewidth=0)
            ax.plot(xp, m, color=colr, linewidth=2, label=f"{lab} (n={len(Y)})")
            ax.annotate(f"{m[-1]:.2f}", (xp[-1], m[-1]), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=9, color=INK2)
        ax.set_title(CAMP[camp], loc="left")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("best alloy demonstrated (true utility)")
        ax.set_ylim(0, 0.85)
        ax.set_xlim(xp[0], xp[-1] * 1.08)
    axes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle(title, x=0.01, ha="left", fontsize=11, color=INK2)
    fig.savefig(OUT / fname, dpi=150)
    plt.close(fig)


def dots(groups, labels, fname, title, value="best_mean", err="best_se", xlabel="best alloy demonstrated"):
    """groups: {row label: {policy: summary-group}}; one panel per campaign, rows = scenarios."""
    plt = _style()
    fig, axes = plt.subplots(1, 2, figsize=(12, 0.55 * len(labels) + 1.9), constrained_layout=True)
    for ax, camp in zip(axes, CAMP):
        for i, lab in enumerate(labels):
            pols = groups[lab]
            for j, (pol, g) in enumerate(pols.items()):
                colr, _ = POL[pol]
                y = i + (j - (len(pols) - 1) / 2) * 0.22
                v, e = g[camp][value], g[camp].get(err, 0) or 0
                ax.errorbar(v, y, xerr=e, fmt="o", color=colr, markersize=8, capsize=0, elinewidth=2,
                            markeredgecolor=SURF, markeredgewidth=1.5)
                ax.annotate(f"{v:.2f}", (v + e, y), xytext=(5, 0), textcoords="offset points", va="center",
                            fontsize=8.5, color=INK2)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_title(CAMP[camp], loc="left")
        ax.set_xlabel(xlabel)
        ax.grid(axis="y", visible=False)
    handles = [plt.Line2D([], [], marker="o", linestyle="", color=POL[p][0], markersize=8, label=POL[p][1])
               for p in next(iter(groups.values()))]
    for ax in axes:
        lo, hi = ax.get_xlim()
        ax.set_xlim(lo, hi + 0.12 * (hi - lo))
    fig.legend(handles=handles, loc="upper right", ncol=len(handles), fontsize=9, bbox_to_anchor=(1.0, 1.0))
    fig.suptitle(title, x=0.01, ha="left", fontsize=11, color=INK2)
    fig.savefig(OUT / fname, dpi=150)
    plt.close(fig)


def market(fname="twin_market.png", seed=3):
    from twin import supply
    plt = _style()
    names = ["calm", "historical", "tariffs", "export_controls", "inflation"]
    cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
    coms = [("Al", "aluminium"), ("Cu", "copper"), ("Ni", "nickel"), ("Sc", "scandium")]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), constrained_layout=True, sharey=True)
    days = np.arange(0, 366)
    for ax, (c, nm) in zip(axes, coms):
        # the scenarios share one random draw (common random numbers), so they coincide except where they differ;
        # 'historical' is drawn last, dashed, so it shows where the others sit on it
        order = [1, 0, 2, 3, 4]
        for i in order[1:] + order[:1]:
            sc, col = names[i], cols[i]
            m = supply.Market(sc, seed, 400)
            y = [m.index(c, d) for d in days]
            ax.plot(days, y, color=col, linewidth=1.6 if sc == "historical" else 2.2,
                    linestyle="--" if sc == "historical" else "-", label=sc.replace("_", " "), zorder=3 if sc == "historical" else 2)
        ax.set_title(nm, loc="left")
        ax.set_xlabel("day")
        ax.set_xlim(0, 365)
    axes[0].set_ylabel("price index (day 0 = 1)")
    h, l = axes[0].get_legend_handles_labels()
    k = {lab: hh for hh, lab in zip(h, l)}
    axes[3].legend([k[n.replace("_", " ")] for n in names], [n.replace("_", " ") for n in names], fontsize=8.5,
                   loc="upper right")
    fig.suptitle(f"One draw of each market scenario (seed {seed}); volatility from USGS MCS 2026, 2021-2025",
                 x=0.01, ha="left", fontsize=11, color=INK2)
    fig.savefig(OUT / fname, dpi=150)
    plt.close(fig)


def validation(fname="twin_validation.png"):
    from twin import thermo
    plt = _style()
    ref = json.loads((HERE / "data" / "al_scheil_ref.json").read_text())
    tr, op = thermo.AlSolidification("truth"), thermo.AlSolidification("open")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    ax = axes[0]
    for name, r in ref.items():
        if not np.isfinite(r.get("kou_index_K", np.nan)):
            continue
        wt = {k.capitalize(): v for k, v in r["wt"].items()}
        a, b = tr.run(wt), op.run(wt)
        ax.plot([r["kou_index_K"]], [1.3 * a["kou_index_K"]], "o", color="#2a78d6", markersize=8,
                markeredgecolor=SURF, markeredgewidth=1.5)
        ax.annotate(name.split(" (")[0], (r["kou_index_K"], 1.3 * a["kou_index_K"]), xytext=(5, -3),
                    textcoords="offset points", fontsize=8, color=INK2)
    lim = [0, 1000]
    ax.plot(lim, lim, color=INK2, linewidth=1, linestyle="--")
    ax.set_xlabel("Kou index, pycalphad Scheil on mc_al (K)")
    ax.set_ylabel("Kou index, the twin's fast model x 1.3 (K)")
    ax.set_title("Al crack index: fast model vs pycalphad", loc="left", fontsize=10)
    ax = axes[1]
    X, Y = thermo._cu_rows()
    from scipy.interpolate import RBFInterpolator
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(X))
    n = int(0.15 * len(X))
    te, trn = idx[:n], idx[n:]
    f = RBFInterpolator(X[trn] / thermo.CU_SCALE, Y[trn], kernel="thin_plate_spline", smoothing=1e-3, degree=1)
    P = f(X[te] / thermo.CU_SCALE)
    ax.plot(Y[te, 0], P[:, 0], "o", color="#eb6834", markersize=6, markeredgecolor=SURF, markeredgewidth=1)
    lo, hi = Y[te, 0].min() - 20, Y[te, 0].max() + 20
    ax.plot([lo, hi], [lo, hi], color=INK2, linewidth=1, linestyle="--")
    rm = float(np.sqrt(np.mean((P[:, 0] - Y[te, 0]) ** 2)))
    ax.set_xlabel("liquidus, pycalphad on mc_ni (degC)")
    ax.set_ylabel("liquidus, emulator (degC)")
    ax.set_title(f"Cu liquidus: emulator, {n} held out (RMSE {rm:.0f} degC)", loc="left", fontsize=10)
    ax = axes[2]
    els = ["Si", "Mg", "Cu", "Fe", "Mn", "Ni", "Cr", "Ti", "Zr", "Sc", "Zn", "Ce", "Li", "Sn", "Er"]
    t_ = [thermo.AL_TRUTH[e][0] for e in els]
    o_ = [thermo._open_params().get(e, (np.nan,))[0] for e in els]
    xi = np.arange(len(els))
    floor = 1e-3
    ax.bar(xi - 0.2, np.maximum(t_, floor), 0.38, color="#2a78d6", label="assessed diagrams (truth)")
    ax.bar(xi + 0.2, np.maximum(np.nan_to_num(o_, nan=floor), floor), 0.38, color="#eb6834",
           label="pycalphad, open databases")
    for i, v in enumerate(o_):
        if not np.isfinite(v):
            ax.annotate("none", (xi[i] + 0.2, floor), xytext=(0, 3), textcoords="offset points", ha="center",
                        fontsize=7, color=INK2, rotation=90)
    ax.set_yscale("log")
    ax.set_ylim(floor, 30)
    ax.axhline(1.0, color=INK2, linewidth=1, linestyle="--")
    ax.set_xticks(xi)
    ax.set_xticklabels(els, fontsize=8.5)
    ax.set_ylabel("partition coefficient k at the Al corner")
    ax.set_title("k at the Al corner: off for Zr, Sc, Ni", loc="left", fontsize=10)
    ax.legend(fontsize=8.5, loc="upper left")
    fig.savefig(OUT / fname, dpi=150)
    plt.close(fig)


NETWORKS = {
    "flaime_al": [
        ("sim_open", "CALPHAD, open\n(pycalphad)", "$1, minutes", 0, 0, "sim"),
        ("sim_tc", "TC-Python TCAL\nScheil", "$10, 30 min", 0, 1, "sim"),
        ("sim_am", "Thermo-Calc\nAM Module", "$25, 2 h", 0, 2, "sim"),
        ("powder", "charge + atomize\n+ sieve + QC", "~$200-400 a run\n+ feedstock", 1, 1, "lab"),
        ("print", "LPBF build\n9 cubes + bars", "$800 (Utah) or\n$150 (PR 318)", 2, 1, "out"),
        ("test", "EDM, heat treat,\ntensile (250 degC)", "$270, 1-2 weeks", 3, 1, "lab"),
        ("promote", "E8 plate\n(440 g)", "~$1.5k, gate G3", 4, 1, "out"),
    ],
    "onr_cu": [
        ("sim_open", "CALPHAD, open\n(mc_ni)", "$1, minutes", 0, 0, "sim"),
        ("sim_tc", "TC-Python\nTCCU", "$10, 30 min", 0, 1, "sim"),
        ("sim_heat", "heat flow +\nCALPHAD on history", "$5, 30 min", 0, 2, "sim"),
        ("powder", "charge + atomize\n(0.8 kg a run)", "~$550 a run in\nplates, nozzles", 1, 1, "lab"),
        ("small_ded", "Utah MX-Lab\ntracks, blocks", "$300, half a day\n+ 0.5 kg", 2, 2, "out"),
        ("nsl", "NSL O, C,\ncomposition", "$150, 2 weeks", 2, 0, "out"),
        ("large_ded", "Mines X2\n2 kg, coupons", "$600, weeks\n(1 per 5 weeks)", 3, 1, "out"),
        ("tensile", "tensile", "$120", 4, 2, "lab"),
        ("screen", "CubXL screen", "$35, 1 h", 4, 1, "lab"),
        ("immersion", "immersion", "$170, 30 days", 4, 0, "lab"),
    ],
}
EDGES = {"flaime_al": [("sim_open", "powder"), ("sim_tc", "powder"), ("sim_am", "print"), ("powder", "print"),
                       ("print", "test"), ("powder", "promote")],
         "onr_cu": [("sim_open", "powder"), ("sim_tc", "powder"), ("sim_heat", "small_ded"), ("powder", "small_ded"),
                    ("powder", "nsl"), ("small_ded", "large_ded"), ("nsl", "large_ded"), ("large_ded", "tensile"),
                    ("large_ded", "screen"), ("large_ded", "immersion")]}


def networks(fname="twin_networks.png"):
    plt = _style()
    from matplotlib.patches import FancyBboxPatch
    kinds = {"sim": ("#eef4fc", "#2a78d6", "simulator (BYU HPC)"), "lab": ("#f6f6f4", "#52514e", "in the lab"),
             "out": ("#fdf0ea", "#eb6834", "outside facility (in house in PR 318's lab)")}
    fig, axes = plt.subplots(2, 1, figsize=(13, 7.4), constrained_layout=True)
    for ax, camp in zip(axes, ("flaime_al", "onr_cu")):
        ax.set_axis_off()
        pos = {}
        for key, lab, cost, col, row, kind in NETWORKS[camp]:
            x, y = col * 2.6, row * 1.25
            pos[key] = (x, y)
            fc, ec, _ = kinds[kind]
            ax.add_patch(FancyBboxPatch((x - 1.0, y - 0.45), 2.0, 0.9, boxstyle="round,pad=0.02,rounding_size=0.08",
                                        fc=fc, ec=ec, lw=1.5))
            ax.text(x, y + 0.12, lab, ha="center", va="center", fontsize=8.5, color=INK, linespacing=1.1)
            ax.text(x, y - 0.3, cost, ha="center", va="center", fontsize=7.2, color=INK2, linespacing=1.0)
        for a, b in EDGES[camp]:
            (x1, y1), (x2, y2) = pos[a], pos[b]
            kw = dict(arrowstyle="-|>", color=INK2, lw=1.0, shrinkA=2, shrinkB=2)
            if abs(x2 - x1) > 2.7 and abs(y2 - y1) < 0.1 and camp == "flaime_al" and a == "powder":
                # past the print and test boxes on the same row: an arc over them
                ax.annotate("", xy=(x2, y2 + 0.45), xytext=(x1, y1 + 0.45),
                            arrowprops=dict(kw, connectionstyle="arc3,rad=-0.18"))
            elif abs(x2 - x1) > 2.7 and y1 > y2:
                # from the top row down past the powder box: aim at the target's upper-left corner
                ax.annotate("", xy=(x2 - 1.0, y2 + 0.35), xytext=(x1 + 1.0, y1), arrowprops=kw)
            else:
                ax.annotate("", xy=(x2 - 1.0, y2), xytext=(x1 + 1.0, y1), arrowprops=kw)
        ax.set_xlim(-1.2, 4 * 2.6 + 1.2)
        ax.set_ylim(-0.8, 3.2)
        ax.set_title(CAMP[camp], loc="left")
    hs = [plt.Rectangle((0, 0), 1, 1, fc=v[0], ec=v[1], lw=1.5, label=v[2]) for v in kinds.values()]
    axes[1].legend(handles=hs, loc="upper right", fontsize=8.5, ncol=3, bbox_to_anchor=(1.0, 1.12))
    fig.suptitle("The two function networks as actions a policy can buy one at a time (partial evaluation)",
                 x=0.01, ha="left", fontsize=11, color=INK2)
    fig.savefig(OUT / fname, dpi=150)
    plt.close(fig)


def main():
    from twin.bench import load, summary, HORIZON_DAYS, BUDGET
    OUT.mkdir(parents=True, exist_ok=True)
    S = summary()
    main_rows = load("main")
    by = {p: [r for r in main_rows if r["cfg"]["policy"] == p] for p in ("cost_aware", "tiered", "random")}
    days = {k: np.linspace(0, HORIZON_DAYS, 200) for k in CAMP}
    spend = {k: np.linspace(0, BUDGET[k], 200) for k in CAMP}
    best_vs(by, 0, "days since both campaigns started", days, "twin_best_vs_days.png",
            "Both campaigns at once on the proposals' lab and partners, historical market; mean and SE over seeds")
    best_vs(by, 1, "money spent ($k, materials, consumables and services)", spend, "twin_best_vs_spend.png",
            "Both campaigns at once on the proposals' lab and partners, historical market; mean and SE over seeds")
    if "supply" in S:
        labels = ["calm", "historical", "tariffs", "export_controls", "inflation"]
        groups = {}
        for lab in labels:
            groups[lab.replace("_", " ")] = {p: S["supply"][f"facility=proposed|scenario={lab}|policy={p}|kappa=1.0|isolated=False"]
                                             for p in ("cost_aware", "random")}
        dots(groups, list(groups), "twin_supply.png", "Best alloy after a year, by market scenario (mean and SE, 10 seeds)")
        dots(groups, list(groups), "twin_supply_orders.png", "Money spent on orders in the year, by market scenario",
             value="order_cost_mean", err=None, xlabel="orders ($)")
    if "facility" in S:
        groups = {}
        for f, lab in (("proposed", "the proposals' lab and partners"), ("vertical_lab", "PR 318's lab")):
            groups[lab] = {p: S["facility"][f"facility={f}|scenario=historical|policy={p}|kappa=1.0|isolated=False"]
                           for p in ("cost_aware", "random")}
        dots(groups, list(groups), "twin_facility.png", "Best alloy after a year, by facility (mean and SE, 10 seeds)")
    if "kappa" in S:
        groups = {}
        for k in (0.0, 0.5, 1.0):
            groups[f"nucleant effect kappa={k}"] = {p: S["kappa"][f"facility=proposed|scenario=historical|policy={p}|kappa={k}|isolated=False"]
                                                    for p in ("cost_aware", "tiered")}
        dots(groups, list(groups), "twin_kappa.png",
             "FLAIME: how much the CALPHAD screen misses (kappa) and which policy it hurts (mean and SE, 10 seeds)")
    if "wip" in S:
        groups = {}
        for w, lab in (("1/1", "one at a time"), ("6/3", "6 and 3 in flight"), ("24/8", "24 and 8 in flight")):
            k = f"facility=proposed|scenario=historical|policy=cost_aware|kappa=1.0|isolated=False|wip={w}"
            if k in S["wip"]:
                groups[lab] = {"cost_aware": S["wip"][k]}
        if groups:
            dots(groups, list(groups), "twin_wip.png",
                 "The ONR proposal's H4: working around pending results (FLAIME/ONR actions in flight; 10 seeds)")
    market()
    validation()
    networks()
    return S


if __name__ == "__main__":
    main()

"""Round-2 figures from out/twin2/bench2_summary.json and the run files.

    python3 -m twin.figures2          # -> out/twin2/fig/*.png and out/twin2/fig/tables.md

Colours: one per policy, assigned in the reference palette's fixed slot order (validated: adjacent CVD and
normal-vision separation pass); the vertical lab is a solid line, the conventional lab dashed. Every line is
labelled at its end as well as in the legend. Curves are the best true utility of a NEW alloy demonstrated so far
(a re-tested reference alloy is not a discovery), mean over seeds with a band of one standard error.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from twin import bench2

FIG = bench2.OUT / "fig"
POL = [  # (key, label, colour): the reference palette's slots in order
    ("bofn", "BOFN", "#257de0"),
    ("heuristic", "heuristic (from the references)", "#f47230"),
    ("bofn_blend", "BOFN + blend screen", "#00b894"),
    ("sobol", "Sobol DoE", "#f2a600"),
    ("tiered", "tiered (CALPHAD funnel)", "#ee7fac"),
    ("cost_aware", "round-1 cost-aware GP", "#008a17"),
    ("gpbo", "GP-BO", "#6a4ce2"),
    ("random", "random", "#ec4647"),
]
COL = {k: c for k, _, c in POL}
LAB = {k: l for k, l, _ in POL}
COL.update(saasbo="#6a4ce2", saasmap="#6a4ce2", bofn_saas="#257de0")
LAB.update(saasbo="SAASBO (NUTS)", saasmap="SAAS-MAP BO", bofn_saas="BOFN, SAAS nodes")
CAMP = {"flaime_al": "FLAIME (Al, LPBF)", "onr_cu": "ONR (Cu, DED)"}
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"


def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                         "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
                         "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                         "figure.dpi": 110, "savefig.dpi": 150, "font.family": "DejaVu Sans"})
    return plt


def step_at(curves, xs, col):
    """Best-so-far of each seed's curve at each x (0 before its first point). curves: [[days, usd, best], ...]."""
    out = np.zeros((len(curves), len(xs)))
    for i, c in enumerate(curves):
        if not c:
            continue
        a = np.array(c, float)
        idx = np.searchsorted(a[:, col], xs, side="right") - 1
        ok = idx >= 0
        out[i, ok] = a[idx[ok], 2]
    return out


def band(ax, xs, Y, color, label, ls="-", lw=2.0, end_label=True):
    m = np.nanmean(Y, 0)
    se = np.nanstd(Y, 0, ddof=1) / math.sqrt(len(Y)) if len(Y) > 1 else np.zeros(Y.shape[1])
    ax.fill_between(xs, m - se, m + se, color=color, alpha=0.12, lw=0)
    ax.plot(xs, m, color=color, lw=lw, ls=ls, label=label)
    if end_label:
        ax.__dict__.setdefault("_ends", []).append((float(m[-1]), float(xs[-1]), color))
    return m


def end_labels(ax, gap=0.03):
    """Value labels at the lines' ends, nudged apart so none overlap; a short leader in the line's colour."""
    ends = sorted(ax.__dict__.get("_ends", []), key=lambda e: e[0])
    placed = []
    for y, x, c in ends:
        yy = max(y, placed[-1] + gap) if placed else y
        placed.append(yy)
        ax.annotate(f" {y:.2f}", (x, y), xytext=(6, (yy - y) * 0), textcoords="offset points", va="center",
                    fontsize=8, color=INK, annotation_clip=False) if yy == y else ax.annotate(
            f" {y:.2f}", xy=(x, y), xytext=(x, yy), textcoords="data", va="center", fontsize=8, color=INK,
            annotation_clip=False, arrowprops=dict(arrowstyle="-", color=c, lw=0.6))
        ax.plot([x], [y], marker="o", ms=3, color=c, clip_on=False)
    xmin, xmax = ax.get_xlim()


def _groups(S, exp):
    return S["experiments"].get(exp, {})


def _find(E, policy, facility="vertical_lab"):
    """The group of an experiment with this policy and facility (group keys carry the run's options, e.g.
    proposed_bofn_stock-lean)."""
    for g in E.values():
        if g["policy"] == policy and g["facility"] == facility:
            return g
    return None


def best_vs(S, col, fname, xlabel, xmax_by_camp, exp="main", pols=None, log=False, title=None,
            facility="vertical_lab"):
    plt = _style()
    E = _groups(S, exp)
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6))
    for ax, camp in zip(axs, ("flaime_al", "onr_cu")):
        xmax = xmax_by_camp[camp]
        xs = np.geomspace(1, xmax, 300) if log else np.linspace(0, xmax, 300)
        for key, _, colr in POL:
            if pols and key not in pols:
                continue
            g = _find(E, key, facility)
            if not g:
                continue
            Y = step_at(g["campaigns"][camp]["curves"], xs, col)
            band(ax, xs, Y, colr, f"{LAB[key]} (n={g['n']})")
        T = S["targets"]
        ax.axhline(T["T1"][camp], color=INK2, lw=1, ls=":")
        ax.text(0.99, T["T1"][camp], "state of the art (best reference alloy) ", va="bottom", ha="right", fontsize=8,
                color=INK2, transform=ax.get_yaxis_transform(), bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
        end_labels(ax)
        ax.set_title(CAMP[camp], loc="left", color=INK)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("best new alloy so far (true utility)")
        ax.set_ylim(0, 0.9)
        if log:
            ax.set_xscale("log")
        if col == 1:
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v / 1000:.0f}k"))
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=8.5)
    fig.suptitle(title or "The vertical lab, one year, both campaigns at once: each policy's best new alloy "
                 "(mean ± SE over seeds)", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / fname)
    plt.close(fig)


def vertical_vs_conventional(S, fname="twin2_vertical_vs_conventional.png"):
    plt = _style()
    main, conv = _groups(S, "main"), _groups(S, "conventional")
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6))
    xs = np.geomspace(1, 1095, 400)
    for ax, camp in zip(axs, ("flaime_al", "onr_cu")):
        for key in ("bofn", "heuristic", "sobol", "tiered"):
            for fac, E, ls in (("vertical_lab", main, "-"), ("proposed", conv, "--")):
                g = _find(E, key, fac)
                if not g:
                    continue
                Y = step_at(g["campaigns"][camp]["curves"], xs, 0)
                if fac == "vertical_lab":
                    Y[:, xs > 365] = np.nan
                    Yp = Y[:, xs <= 365]
                    band(ax, xs[xs <= 365], Yp, COL[key], f"{LAB[key]}, vertical lab", ls=ls)
                else:
                    band(ax, xs, Y, COL[key], f"{LAB[key]}, conventional lab", ls=ls)
        ax.axhline(S["targets"]["T1"][camp], color=INK2, lw=1, ls=":")
        end_labels(ax)
        ax.set_xscale("log")
        ax.set_xlabel("days from the start (log)")
        ax.set_ylabel("best new alloy so far (true utility)")
        ax.set_title(CAMP[camp], loc="left")
        ax.set_ylim(0, 0.9)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=8)
    fig.suptitle("Vertical lab (solid, one year) against a conventional lab (dashed, three years at three years' "
                 "money)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.savefig(FIG / fname)
    plt.close(fig)


def time_to_target(S, fname="twin2_time_to_target.png", tname="T1"):
    plt = _style()
    rows = []
    for exp, fac_lab in (("main", "vertical lab"), ("conventional", "conventional lab")):
        for key, g in _groups(S, exp).items():
            rows.append((fac_lab, g["policy"], g))
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.2), sharey=True)
    order = [r for r in rows]
    order.sort(key=lambda r: (r[0] != "vertical lab", [k for k, _, _ in POL].index(r[1])
                              if r[1] in COL and r[1] in [k for k, _, _ in POL] else 99))
    labels = [f"{LAB.get(p, p)} · {f}" for f, p, _ in order]
    for ax, camp in zip(axs, ("flaime_al", "onr_cu")):
        for i, (f, p, g) in enumerate(order):
            t = g["campaigns"][camp]["targets"][tname]
            horizon = g["cfg"].get("days", 365)
            d = [x for x in t["days"] if x is not None]
            nmiss = sum(1 for x in t["days"] if x is None)
            col = COL.get(p, INK2)
            ax.scatter(d, [i] * len(d), s=26, color=col, edgecolor="white", linewidth=0.8, zorder=3,
                       marker="o" if f == "vertical lab" else "D")
            if nmiss:
                ax.scatter([horizon * 1.08], [i], s=30, facecolor="none", edgecolor=col, zorder=3)
                ax.text(horizon * 1.15, i, f"{nmiss} not by day {horizon}", va="center", fontsize=7, color=INK2)
            if d:
                ax.plot([np.median(d)] * 2, [i - 0.3, i + 0.3], color=INK, lw=1.5)
        ax.set_xscale("log")
        ax.set_xlim(0.8, 3000)
        ax.set_title(f"{CAMP[camp]}: days to a new alloy at or above "
                     f"{S['targets'][tname][camp]:.2f}", loc="left", fontsize=10)
        ax.set_xlabel("days (log); black tick: median of the seeds that got there")
    axs[0].set_yticks(range(len(order)))
    axs[0].set_yticklabels(labels, fontsize=8)
    axs[0].invert_yaxis()
    fig.suptitle("Time to a state-of-the-art alloy, each seed a dot (circles: vertical lab; diamonds: conventional lab)",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / fname)
    plt.close(fig)


def dots(S, items, fname, title):
    """items: [(label, experiment, group key)] -> mean ± SE of the best new alloy, per campaign."""
    plt = _style()
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 0.45 * len(items) + 1.6), sharey=True)
    for ax, camp in zip(axs, ("flaime_al", "onr_cu")):
        for i, (lab, exp, key) in enumerate(items):
            g = _groups(S, exp).get(key)
            if not g:
                continue
            c = g["campaigns"][camp]
            col = COL.get(g["policy"], INK2)
            ax.errorbar(c["best_mean"], i, xerr=c["best_se"], fmt="o", color=col, ms=7, capsize=3, lw=1.5)
            ax.text(c["best_mean"] + c["best_se"] + 0.01, i, f"{c['best_mean']:.2f}  (n={g['n']})", va="center",
                    fontsize=7.5, color=INK)
        ax.axvline(S["targets"]["T1"][camp], color=INK2, lw=1, ls=":")
        ax.set_xlim(0, 1.0)
        ax.set_title(CAMP[camp], loc="left")
        ax.set_xlabel("best new alloy in the year (true utility), mean ± SE")
    axs[0].set_yticks(range(len(items)))
    axs[0].set_yticklabels([lab for lab, _, _ in items], fontsize=8)
    axs[0].invert_yaxis()
    fig.suptitle(title, x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / fname)
    plt.close(fig)


def seeded(S, fname="twin2_seeded_best_vs_days.png"):
    """Best new alloy so far against simulated days for BOFN, standard BO (GP-BO) and random, every policy from DAL
    #275's common seed set: the vertical lab (top) and DAL's own lab on DAL #256's schedule (bottom)."""
    plt = _style()
    rows = [("seeded", "vertical_lab", "the vertical lab (PR 318), stocked"),
            ("seeded_dal256", "dal256", "DAL's lab on DAL #256's schedule, ordering as it goes")]
    rows = [r for r in rows if r[0] in S["experiments"]]
    if not rows:
        return
    fig, axs = plt.subplots(len(rows), 2, figsize=(12.5, 4.3 * len(rows)), squeeze=False)
    xs = np.linspace(0, 365, 366)
    for i, (exp, fac, lab) in enumerate(rows):
        E = _groups(S, exp)
        for j, camp in enumerate(("flaime_al", "onr_cu")):
            ax = axs[i][j]
            for key in ("bofn", "gpbo", "random"):
                g = _find(E, key, fac)
                if not g:
                    continue
                Y = step_at(g["campaigns"][camp]["curves"], xs, 0)
                band(ax, xs, Y, COL[key], f"{LAB[key]} (n={g['n']})")
            ax.axhline(S["targets"]["T1"][camp], color=INK2, lw=1, ls=":")
            ax.text(0.99, S["targets"]["T1"][camp], "state of the art ", va="bottom", ha="right", fontsize=8,
                    color=INK2, transform=ax.get_yaxis_transform(), bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))
            end_labels(ax)
            ax.set_title(f"{CAMP[camp]}: {lab}", loc="left", fontsize=9.5)
            ax.set_xlabel("simulated days from the start")
            ax.set_ylabel("best new alloy so far (true utility)")
            ax.set_ylim(0, 0.9)
            ax.set_xlim(0, 380)
    h, l = axs[0][0].get_legend_handles_labels()
    fig.legend(h, [x.split(" (n=")[0] for x in l], loc="lower center", ncol=3, fontsize=9)
    fig.suptitle("Every policy from DAL #275's common seed set: best new alloy so far against simulated days "
                 "(mean ± SE over seeds)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(FIG / fname)
    plt.close(fig)


def cu_hidden(S, fname="twin2_cu_hidden.png"):
    """Copper with and without the effect the CALPHAD screen cannot see: each policy's best new alloy, mean ± SE."""
    plt = _style()
    if "cu_hidden" not in S["experiments"]:
        return
    main, hid = _groups(S, "main"), _groups(S, "cu_hidden")
    pols = [k for k, _, _ in POL if _find(hid, k)]
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 0.5 * len(pols) + 1.8), sharey=True)
    for ax, camp in zip(axs, ("onr_cu", "flaime_al")):
        for i, k in enumerate(pols):
            for E, mk, dy, lab in ((main, "o", -0.15, "as run"), (hid, "s", 0.15, "hidden gamma-2")):
                g = _find(E, k)
                if not g:
                    continue
                c = g["campaigns"][camp]
                ax.errorbar(c["best_mean"], i + dy, xerr=c["best_se"], fmt=mk, color=COL[k], ms=6, capsize=3,
                            lw=1.4, mfc=COL[k] if mk == "s" else "white")
                ax.text(c["best_mean"] + c["best_se"] + 0.01, i + dy, f"{c['best_mean']:.2f}", va="center",
                        fontsize=7.5, color=INK)
        ax.axvline(S["targets"]["T1"][camp], color=INK2, lw=1, ls=":")
        ax.set_xlim(0, 1.0)
        ax.set_title(CAMP[camp] + (": the test" if camp == "onr_cu" else ": unchanged truth, shares the lab"),
                     loc="left")
        ax.set_xlabel("best new alloy in the year (true utility), mean ± SE")
    axs[0].set_yticks(range(len(pols)))
    axs[0].set_yticklabels([LAB[k] for k in pols], fontsize=8.5)
    axs[0].invert_yaxis()
    fig.suptitle("Copper with an effect the CALPHAD screen cannot see (gamma-2 above Al = 8.2 + Ni/2): open circles "
                 "as run, filled squares with the effect", x=0.01, ha="left", fontsize=10.5)
    fig.tight_layout()
    fig.savefig(FIG / fname)
    plt.close(fig)


def table(S) -> str:
    out = []
    for exp, E in S["experiments"].items():
        if exp == "dev":
            continue
        out.append(f"\n**{exp}**\n")
        out.append("| setting | n | FLAIME best new (± SE) | hit T1 | median days to T1 | median $ to T1 | ONR best new (± SE) "
                   "| hit T1 | median days to T1 | median $ to T1 | s/run |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for key, g in E.items():
            cells = [f"{key}", str(g["n"])]
            for camp in ("flaime_al", "onr_cu"):
                c = g["campaigns"][camp]
                t = c["targets"]["T1"]
                d = [x for x in t["days"] if x is not None]
                u = [x for x in t["usd"] if x is not None]
                cells += [f"{c['best_mean']:.3f} ± {c['best_se']:.3f}", f"{t['hit_frac']:.0%}",
                          f"{np.median(d):.0f}" if d else "-", f"${np.median(u) / 1000:.0f}k" if u else "-"]
            cells.append(f"{g['seconds']:.0f}")
            out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    S = json.loads((bench2.OUT / "bench2_summary.json").read_text())
    FIG.mkdir(parents=True, exist_ok=True)
    exp = "main" if "main" in S["experiments"] else "dev"
    best_vs(S, 0, "twin2_best_vs_days.png", "days from the start", {"flaime_al": 365, "onr_cu": 365}, exp=exp)
    spend = {"flaime_al": 120_000, "onr_cu": 60_000}
    best_vs(S, 1, "twin2_best_vs_spend.png", "money spent", spend, exp=exp)
    if "conventional" in S["experiments"]:
        vertical_vs_conventional(S)
        time_to_target(S)
    cu_hidden(S)
    seeded(S)
    items = []
    for k in ("bofn", "bofn_blend", "heuristic", "gpbo"):
        items.append((f"{LAB[k]}: as run", "main", f"vertical_lab_{k}"))
        for exp2, suff, lab in (("crucible", "_crucible-400", "400 cm3 crucible"), ("reuse", "_reuse-False",
                                                                                    "no powder reuse"),
                                ("stock", "_stock-lean", "ordering as it goes"),
                                ("cu", "_cu_budget-180000.0", "copper money x3")):
            if f"vertical_lab_{k}{suff}" in _groups(S, exp2):
                items.append((f"{LAB[k]}: {lab}", exp2, f"vertical_lab_{k}{suff}"))
    if len(items) > 4:
        dots(S, items, "twin2_options.png", "What the crucible, powder reuse, stocking and money change")
    sitems = [(LAB[k], exp2, f"vertical_lab_{k}") for k, exp2 in (("gpbo", "main"), ("saasmap", "saas"),
                                                                    ("saasbo", "saas"), ("bofn", "main"),
                                                                    ("bofn_saas", "saas"))]
    if "saas" in S["experiments"]:
        dots(S, sitems, "twin2_saas.png", "Default GP surrogates against SAAS priors (high-dimensional spaces)")
    (FIG / "tables.md").write_text(table(S))
    print("figures in", FIG)


if __name__ == "__main__":
    main()

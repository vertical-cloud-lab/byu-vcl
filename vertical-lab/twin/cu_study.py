"""The copper investigation (round 1 had the tiered funnel and the cost-aware GP tied on copper).

    python3 -m twin.cu_study        # -> out/twin2/fig/twin2_cu.png, out/twin2/cu_study.json

Three panels: where the copper campaign's money goes, per policy (main runs); how many alloys a year each policy
gets through the whole chain; and the best new alloy per policy at the proposal's money, at three times that, and
with the blend screen. Reads out/twin2/runs/{main,cu,crucible}.jsonl and out/twin2/oracle.json.
"""
from __future__ import annotations

import json

import numpy as np

from twin import bench2
from twin.figures2 import COL, INK, INK2, LAB, _style

KINDS = [("order", "feedstock and atomizer consumables"), ("blown", "DED deposits"),
         ("tests", "tensile, immersion, screen, PIP, sections"), ("other", "everything else")]


def _kind(k):
    if k.startswith("order"):
        return "order"
    if k.startswith("blown") or k.startswith("blend") or k == "preplaced":
        return "blown"
    if k in ("tensile", "immersion", "corrosion", "pip", "section", "screen") or k.startswith("immersion") \
            or k.startswith("tensile") or k.startswith("corrosion") or k.startswith("section") or k.startswith("pip"):
        return "tests"
    return "other"


def main():
    plt = _style()
    main_runs = bench2.load("main")
    cu_runs = bench2.load("cu")
    cr_runs = bench2.load("crucible")
    oracle = json.loads((bench2.OUT / "oracle.json").read_text())["onr_cu"]
    pols = [p for p in ("random", "sobol", "heuristic", "tiered", "cost_aware", "gpbo", "bofn", "bofn_blend")
            if any(r["cfg"]["policy"] == p for r in main_runs)]
    out = {"oracle": {k: oracle[k] for k in ("sota", "sota_utility", "best_found", "random_default_process", "screen")},
           "policies": {}}
    fig, axs = plt.subplots(1, 3, figsize=(15.5, 4.8), gridspec_kw=dict(width_ratios=[1.25, 0.9, 1.25]))
    # (a) money by kind
    ax = axs[0]
    cols = ["#257de0", "#f47230", "#00b894", "#9c9c9c"]
    for i, p in enumerate(pols):
        rs = [r for r in main_runs if r["cfg"]["policy"] == p]
        tot = {k: 0.0 for k, _ in KINDS}
        for r in rs:
            for k, v in r["campaigns"]["onr_cu"]["spend_by"].items():
                tot[_kind(k)] += v / len(rs)
        left = 0.0
        for (k, lab), c in zip(KINDS, cols):
            ax.barh(i, tot[k] / 1000, left=left, color=c, height=0.62, label=lab if i == 0 else None,
                    edgecolor="white", linewidth=1.5)
            left += tot[k] / 1000
        out["policies"].setdefault(p, {})["spend_by_kind"] = {k: round(v) for k, v in tot.items()}
    ax.set_yticks(range(len(pols)))
    ax.set_yticklabels([LAB.get(p, p) for p in pols], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("copper campaign's money in the year ($k, mean over seeds)")
    ax.set_title("Where the money goes", loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.16), ncol=2, fontsize=7.5)
    # (b) alloys through the whole chain a year
    ax = axs[1]
    mx = 1.0
    for i, p in enumerate(pols):
        rs = [r for r in main_runs if r["cfg"]["policy"] == p]
        dem = [r["campaigns"]["onr_cu"]["n_demonstrated"] for r in rs]
        lots = [r["campaigns"]["onr_cu"]["n_lots"] for r in rs]
        ax.barh(i, np.mean(dem), color=COL.get(p, INK2), height=0.62)
        ax.text(np.mean(dem) + 0.3, i, f"{np.mean(dem):.1f} alloys from {np.mean(lots):.0f} lots", va="center",
                fontsize=7.5, color=INK)
        out["policies"][p].update(n_demonstrated=float(np.mean(dem)), n_lots=float(np.mean(lots)))
        mx = max(mx, float(np.mean(dem)))
    ax.set_xlim(0, mx * 2.1)
    ax.set_yticks(range(len(pols)))
    ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_xlabel("alloys through the whole chain in a year (mean)")
    ax.set_title("Throughput", loc="left")
    # (c) best new alloy: $60k, $180k, 400 cm3
    ax = axs[2]
    groups = [("$60k (as proposed)", main_runs, "o"), ("$180k", cu_runs, "s"), ("400 cm3 crucible", cr_runs, "^")]
    for j, (lab, runs, mk) in enumerate(groups):
        for i, p in enumerate(pols):
            rs = [r for r in runs if r["cfg"]["policy"] == p]
            if not rs:
                continue
            b = np.array([r["campaigns"]["onr_cu"]["best_new"] for r in rs])
            y = i + (j - 1) * 0.22
            ax.errorbar(b.mean(), y, xerr=b.std() / np.sqrt(len(b)), fmt=mk, color=COL.get(p, INK2), ms=6,
                        capsize=2, lw=1.2, label=lab if i == 0 or (p == "bofn_blend" and j > 0) else None)
            out["policies"][p][f"best_new_{lab}"] = [round(float(b.mean()), 4), round(float(b.std() / np.sqrt(len(b))), 4),
                                                    len(b)]
    ax.axvline(oracle["sota_utility"], color=INK2, ls=":", lw=1)
    ax.text(oracle["sota_utility"], -0.6, " NAB", fontsize=7.5, color=INK2)
    ax.axvline(oracle["best_found"]["utility"], color=INK2, ls="--", lw=1)
    ax.text(oracle["best_found"]["utility"], -0.6, " oracle's best", fontsize=7.5, color=INK2)
    ax.set_yticks(range(len(pols)))
    ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_xlim(0, 0.85)
    ax.set_xlabel("best new copper alloy in the year (true utility), mean ± SE")
    ax.set_title("What separates the policies", loc="left")
    h, l = ax.get_legend_handles_labels()
    seen, hh, ll = set(), [], []
    for a, b in zip(h, l):
        if b not in seen:
            seen.add(b)
            hh.append(a)
            ll.append(b)
    ax.legend(hh, ll, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3, fontsize=7.5)
    fig.suptitle("Copper (ONR): consumables bound the campaign, the CALPHAD screen can't rank it, and a cheap blend "
                 "screen is what lets a model learn", x=0.01, ha="left", fontsize=11)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    (bench2.OUT / "fig").mkdir(parents=True, exist_ok=True)
    fig.savefig(bench2.OUT / "fig" / "twin2_cu.png")
    (bench2.OUT / "cu_study.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out["policies"], indent=0)[:1500])


if __name__ == "__main__":
    main()

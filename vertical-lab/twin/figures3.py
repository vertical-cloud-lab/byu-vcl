"""Round 3's figures and tables, from out/twin3/runs (twin/bench3.py) and round 2's runs for the comparisons.

    python3 -m twin.figures3        # -> out/twin3/fig/*.png, out/twin3/fig/tables.md, out/twin3/fig/numbers.json

Policies keep one colour each across every figure (the reference palette's fixed order); the denominator is the line
style: solid for time-aware (bottleneck-hours), dashed for per-dollar.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from twin import bench2 as B2
from twin import bench3 as B3

OUT = B3.OUT / "fig"
CAMPS = ("flaime_al", "onr_cu")
CNAME = {"flaime_al": "Aluminium (FLAIME, LPBF)", "onr_cu": "Copper (ONR, DED)"}
COLOR = {"bofn": "#257de0", "pkgfn": "#f47230", "tiered": "#00b894", "heuristic": "#f2a600", "gpbo": "#ee7fac",
         "sobol": "#008a17", "random": "#6a4ce2"}
LABEL = {"bofn3": "BOFN, time-aware", "bofn3_usd": "BOFN, per dollar", "pkgfn3": "pKGFN, time-aware",
         "pkgfn3_usd": "pKGFN, per dollar", "tiered": "Tiered screening", "heuristic": "Heuristic", "gpbo": "GP-BO",
         "sobol": "Sobol", "random": "Random", "tiered_mis": "Tiered, mis-specified proxy",
         "tiered_screen": "Tiered, screen only (random order)", "tiered_proxy": "Tiered, proxy only (no screen)",
         "bofn_blend": "BOFN + blend screen (round 2)", "bofn": "BOFN (round 2)", "cost_aware": "Round-1 cost-aware"}
ORDER = ("bofn3", "pkgfn3", "bofn3_usd", "pkgfn3_usd", "tiered", "heuristic", "gpbo", "sobol", "random")
TEXT, MUTED, GRID = "#191919", "#666666", "#e6e6e6"


def fam(p):
    return "bofn" if p.startswith("bofn") else ("pkgfn" if p.startswith("pkgfn") else p.split("_")[0])


def style(p):
    return dict(color=COLOR.get(fam(p), MUTED), ls="--" if p.endswith("_usd") else "-", lw=2)


def _ax(ax):
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)


def mse(x):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) == 0:
        return float("nan"), float("nan")
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 1 else 0.0


def by_policy(rows, camp=None):
    out = {}
    for r in rows:
        out.setdefault(r["cfg"]["policy"], {})[r["cfg"]["seed"]] = r
    return out


def step_mean(curves, grid):
    """Mean and SE over seeds of best-so-far step curves [[day, $, u], ...] on a day grid."""
    M = np.zeros((len(curves), len(grid)))
    for i, c in enumerate(curves):
        j, best = 0, 0.0
        for k, d in enumerate(grid):
            while j < len(c) and c[j][0] <= d:
                best = max(best, c[j][2])
                j += 1
            M[i, k] = best
    m = M.mean(0)
    se = M.std(0, ddof=1) / math.sqrt(len(curves)) if len(curves) > 1 else np.zeros(len(grid))
    return m, se


def hit_days(c, target):
    h = B2.hit(c, target, 2)
    return h[0] if h else None


def paired(a: dict, b: dict, f):
    """Mean and SE of f(run a) - f(run b) over the seeds both have, and how many seeds a was ahead."""
    seeds = sorted(set(a) & set(b))
    d = [f(a[s]) - f(b[s]) for s in seeds]
    m, se = mse(d)
    return m, se, sum(1 for x in d if x > 1e-9), sum(1 for x in d if x < -1e-9), len(seeds)


def fig_best_vs_days(rows, T, path, title):
    import matplotlib.pyplot as plt
    P = by_policy(rows)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), dpi=140)
    for ax, camp in zip(axes, CAMPS):
        days = max(r["cfg"].get("days", 365) for r in rows)
        grid = np.linspace(0, days, 200)
        for p in ORDER:
            if p not in P:
                continue
            cur = [P[p][s]["campaigns"][camp]["curve_new"] for s in sorted(P[p])]
            m, se = step_mean(cur, grid)
            st = style(p)
            ax.plot(grid, m, label=f"{LABEL.get(p, p)} (n={len(cur)})", **st)
            ax.fill_between(grid, m - se, m + se, color=st["color"], alpha=0.10, lw=0)
        for tn, ls in (("T1", ":"), ("T2", "-.")):
            ax.axhline(T[tn][camp], color=MUTED, lw=1, ls=ls)
            ax.text(days, T[tn][camp], f" {tn}", color=MUTED, va="center", fontsize=8)
        ax.set_title(CNAME[camp], color=TEXT, fontsize=11)
        ax.set_xlabel("simulated days", color=TEXT)
        ax.set_ylabel("best new alloy so far (true utility)", color=TEXT)
        ax.set_ylim(0, 0.85)
        _ax(ax)
    axes[1].legend(fontsize=8, frameon=False, loc="lower right")
    fig.suptitle(title, color=TEXT, fontsize=11)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def fig_time_to_target(rows, T, path, title, horizon=365):
    import matplotlib.pyplot as plt
    P = by_policy(rows)
    pols = [p for p in ORDER if p in P]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4), dpi=140)
    for ax, camp in zip(axes, CAMPS):
        for i, p in enumerate(pols):
            for k, (tn, mk) in enumerate((("T1", "o"), ("T2", "s"))):
                ds = [hit_days(P[p][s]["campaigns"][camp]["curve_new"], T[tn][camp]) for s in sorted(P[p])]
                xs = [d if d is not None else horizon * 1.04 for d in ds]
                y = i + (k - 0.5) * 0.3 + np.linspace(-0.08, 0.08, len(xs))
                ax.scatter(xs, y, s=22, marker=mk, color=COLOR.get(fam(p), MUTED),
                           facecolors="none" if tn == "T2" else COLOR.get(fam(p), MUTED), linewidths=1.2)
                med = B3.km_median(ds, horizon)
                if med is not None:
                    ax.plot([med, med], [y.min() - 0.08, y.max() + 0.08], color=TEXT, lw=1.5)
        ax.axvline(horizon, color=MUTED, lw=1, ls=":")
        ax.set_yticks(range(len(pols)))
        ax.set_yticklabels([LABEL.get(p, p) for p in pols], fontsize=8)
        ax.set_xlabel("days to the target (each seed a mark; past the dotted line: not reached; bar: median)",
                      color=TEXT, fontsize=8)
        ax.set_title(f"{CNAME[camp]}: filled T1 (state of the art), open T2 (halfway)", color=TEXT, fontsize=10)
        ax.invert_yaxis()
        _ax(ax)
    fig.suptitle(title, color=TEXT, fontsize=11)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def fig_counts(r2, r3, path):
    """Evaluations completed a year, round 2 (cap) against round 3 (physical capacity), seed means."""
    import matplotlib.pyplot as plt
    kinds = {"flaime_al": [("powder", "lots"), ("print", "prints"), ("pip", "PIP"), ("test", "bar tests")],
             "onr_cu": [("powder", "lots"), ("blend", "blend screens"), ("blown_large", "1 kg deposits"),
                        ("tensile", "tensile"), ("immersion", "30-day immersions")]}
    pols = [p for p in ("bofn3", "pkgfn3", "tiered", "heuristic", "gpbo", "random") if p in r3]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), dpi=140)
    for ax, camp in zip(axes, CAMPS):
        ks = kinds[camp]
        w = 0.8 / max(len(pols), 1)
        for i, p in enumerate(pols):
            vals = [np.mean([(r["campaigns"][camp].get("done") or {}).get(k, 0) for r in r3[p].values()]) for k, _ in ks]
            ax.bar(np.arange(len(ks)) + i * w, vals, width=w * 0.92, color=COLOR.get(fam(p), MUTED),
                   label=LABEL.get(p, p))
        ax.set_xticks(np.arange(len(ks)) + 0.4 - w / 2)
        ax.set_xticklabels([n for _, n in ks], fontsize=9)
        ax.set_yscale("symlog", linthresh=10)
        ax.set_ylabel("completed in a year (mean over seeds)", color=TEXT)
        ax.set_title(CNAME[camp] + ", round 3", color=TEXT, fontsize=10)
        _ax(ax)
    axes[0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def fig_spend(rows, path, title):
    import matplotlib.pyplot as plt
    P = by_policy(rows)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2), dpi=140)
    for ax, camp in zip(axes, CAMPS):
        for p in ORDER:
            if p not in P:
                continue
            cs = [P[p][s]["campaigns"][camp].get("spend_curve") for s in sorted(P[p])]
            cs = [c for c in cs if c]
            if not cs:
                continue
            n = min(len(c) for c in cs)
            d = np.array([x[0] for x in cs[0][:n]])
            m = np.mean([[x[1] for x in c[:n]] for c in cs], axis=0) / 1e3
            ax.plot(d, m, label=LABEL.get(p, p), **style(p))
        b = rows[0]["campaigns"][camp]["budget"]
        days = rows[0]["cfg"].get("days", 365)
        tt = np.linspace(0, days, 100)
        ax.plot(tt, b / 1e3 * np.minimum(1.0, 0.15 + 0.85 * tt / (0.75 * days)), color=MUTED, ls=":", lw=1,
                label="spending plan")
        ax.set_xlabel("simulated days", color=TEXT)
        ax.set_ylabel("spent ($k, mean over seeds)", color=TEXT)
        ax.set_title(CNAME[camp], color=TEXT, fontsize=10)
        _ax(ax)
    axes[1].legend(fontsize=8, frameon=False)
    fig.suptitle(title, color=TEXT, fontsize=11)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def table_main(rows, T, ref="tiered", horizon=365, r2rows=None):
    P = by_policy(rows)
    L = []
    for camp in CAMPS:
        L.append(f"\n**{CNAME[camp]}** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the "
                 f"seeds got there; paired against {LABEL.get(ref, ref)} on the same seeds)\n")
        L.append("| Policy | n | best new alloy | paired vs " + LABEL.get(ref, ref) + " (ahead/behind) | T1 reached | "
                 "T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for p in ORDER:
            if p not in P:
                continue
            rs = P[p]
            best = [rs[s]["campaigns"][camp]["best_new"] for s in rs]
            m, se = mse(best)
            pr = ""
            if ref in P and p != ref:
                dm, dse, a, b, n = paired(rs, P[ref], lambda r: r["campaigns"][camp]["best_new"])
                pr = f"{dm:+.2f} ± {dse:.2f} ({a}/{b})"
            cells = []
            for tn in ("T1", "T2"):
                ds = [hit_days(rs[s]["campaigns"][camp]["curve_new"], T[tn][camp]) for s in rs]
                frac = sum(1 for d in ds if d is not None)
                med = B3.km_median(ds, horizon)
                cells += [f"{frac}/{len(ds)}", f"{med:.0f}" if med is not None else f">{horizon}"]
            spent = np.mean([rs[s]["campaigns"][camp]["spent"] for s in rs]) / 1e3
            nal = np.mean([rs[s]["campaigns"][camp].get("n_new_alloys", 0) for s in rs]) * 365 / horizon
            stp = np.mean([len(rs[s]["campaigns"][camp].get("stops") or []) for s in rs]) * 365 / horizon
            L.append(f"| {LABEL.get(p, p)} | {len(rs)} | {m:.2f} ± {se:.2f} | {pr} | {cells[0]} | {cells[1]} | "
                     f"{cells[2]} | {cells[3]} | {spent:.1f} | {nal:.1f} | {stp:.1f} |")
    return "\n".join(L)


def numbers(rows, T, horizon=365):
    """Per policy and campaign: best (mean, SE, per seed), T1/T2 days per seed and KM medians, spend, counts."""
    P = by_policy(rows)
    out = {}
    for p, rs in P.items():
        out[p] = {}
        for camp in CAMPS:
            cc = {s: rs[s]["campaigns"][camp] for s in rs}
            best = {s: c["best_new"] for s, c in cc.items()}
            m, se = mse(list(best.values()))
            d = dict(n=len(cc), best_mean=round(m, 4), best_se=round(se, 4), best=best,
                     spent_mean=round(float(np.mean([c["spent"] for c in cc.values()])), 1),
                     done=_mean_counts([c.get("done") or {} for c in cc.values()], horizon),
                     n_new_alloys=round(float(np.mean([c.get("n_new_alloys", 0) for c in cc.values()])) * 365 / horizon, 2),
                     stops=round(float(np.mean([len(c.get("stops") or []) for c in cc.values()])) * 365 / horizon, 2))
            for tn in ("T1", "T2"):
                ds = {s: hit_days(c["curve_new"], T[tn][camp]) for s, c in cc.items()}
                usd = {s: (B2.hit(c["curve_new"], T[tn][camp], 2) or (None, None))[1] for s, c in cc.items()}
                d[tn] = dict(days=ds, usd=usd, hit=sum(1 for x in ds.values() if x is not None),
                             km_median=B3.km_median(list(ds.values()), horizon))
            out[p][camp] = d
    return out


def _mean_counts(dicts, horizon):
    keys = sorted({k for d in dicts for k in d})
    return {k: round(float(np.mean([d.get(k, 0) for d in dicts])) * 365 / horizon, 2) for k in keys}


def main():
    import matplotlib
    matplotlib.use("Agg")
    OUT.mkdir(parents=True, exist_ok=True)
    T = B2.targets()
    N = {"targets": T}
    md = ["# Round 3 tables (simulated)", "",
          f"Targets: T1 = the state of the art (aluminium {T['T1']['flaime_al']}, copper {T['T1']['onr_cu']}); "
          f"T2 = halfway from it to the oracle's best (aluminium {T['T2']['flaime_al']}, copper {T['T2']['onr_cu']}). "
          "New alloys only. Standard errors: sample SD (n - 1) / sqrt(n)."]
    main_rows = B3.load("main")
    if main_rows:
        fig_best_vs_days(main_rows, T, OUT / "twin3_best_vs_days.png",
                         "Round 3, simulated: best new alloy so far, mean ± SE over seeds (vertical lab, one year)")
        fig_time_to_target(main_rows, T, OUT / "twin3_time_to_target.png", "Round 3, simulated: days to the targets")
        fig_spend(main_rows, OUT / "twin3_spend.png", "Round 3, simulated: money spent against the spending plan")
        md += ["", "## Main benchmark (vertical lab, one year)", table_main(main_rows, T, "tiered")]
        N["main"] = numbers(main_rows, T)
    more = B3.load("main_more")
    if more:
        allr = main_rows + more
        md += ["", "## Main benchmark, all seeds (main + main_more)", table_main(allr, T, "tiered")]
        N["main_all"] = numbers(allr, T)
    for name, ref in (("cu_hidden", "tiered"), ("cu_money", "tiered"), ("cu_proxy", None), ("cu_ablation", None)):
        rows = B3.load(name)
        if rows:
            md += ["", f"## {name}", table_main(rows, T, ref or "tiered")]
            N[name] = numbers(rows, T)
    conv = B3.load("conventional")
    if conv:
        md += ["", "## Conventional lab, three years at three years' money (async)", table_main(conv, T, "tiered", 1095)]
        N["conventional"] = numbers(conv, T, 1095)
        fig_best_vs_days(conv, T, OUT / "twin3_conventional_best_vs_days.png",
                         "Round 3, simulated: the conventional lab with the same freedom, three years")
    if main_rows:
        r3 = by_policy(main_rows)
        fig_counts(None, r3, OUT / "twin3_counts.png")
    (OUT / "tables.md").write_text("\n".join(md) + "\n")
    (OUT / "numbers.json").write_text(json.dumps(B2._jsonable(N), indent=1))
    print("\n".join(md))


if __name__ == "__main__":
    main()

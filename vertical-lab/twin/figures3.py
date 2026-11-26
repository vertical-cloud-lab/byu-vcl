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


def table_counts(r2rows, r3rows):
    """Alloys and evaluations of each kind a year, round 2 (cap on work in flight) against round 3 (physical
    capacity), seed means. Round 2's logs count results by type only (its 'cu_test' lumps tensile, screen and
    immersion), so the copper columns there are lots, deposits and demonstrated alloys (tensile and immersion both
    back)."""
    R2 = by_policy(r2rows)
    R3 = by_policy(r3rows)
    pairs = [("random", "random"), ("sobol", "sobol"), ("heuristic", "heuristic"), ("tiered", "tiered"),
             ("gpbo", "gpbo"), ("bofn", "bofn3"), ("bofn_blend", "bofn3"), ("bofn", "pkgfn3")]
    L = ["| Policy (round 2 -> round 3) | Al lots | Al prints | Al PIP | Al bar tests | Al alloys demonstrated | "
         "Cu lots | Cu blend screens | Cu 1 kg deposits | Cu 30-day immersions finished | Cu coupons stopped early | "
         "Cu alloys demonstrated |", "|---|" + "---|" * 11]

    def m(rs, f):
        return float(np.mean([f(r) for r in rs.values()])) if rs else float("nan")
    for a, b in pairs:
        if a not in R2 or b not in R3:
            continue
        r2, r3 = R2[a], R3[b]
        A2, C2 = (lambda r: r["campaigns"]["flaime_al"]), (lambda r: r["campaigns"]["onr_cu"])
        nr = lambda c, k: (c.get("n_results") or {}).get(k, 0)
        d3 = lambda c, k: (c.get("done") or {}).get(k, 0)
        row2 = [m(r2, lambda r: A2(r)["n_lots"]), m(r2, lambda r: nr(A2(r), "build")), m(r2, lambda r: nr(A2(r), "pip")),
                m(r2, lambda r: nr(A2(r), "test")), m(r2, lambda r: A2(r)["n_demonstrated"]),
                m(r2, lambda r: C2(r)["n_lots"]), None, None, None, None, m(r2, lambda r: C2(r)["n_demonstrated"])]
        row3 = [m(r3, lambda r: d3(A2(r), "powder")), m(r3, lambda r: d3(A2(r), "print")),
                m(r3, lambda r: d3(A2(r), "pip")), m(r3, lambda r: d3(A2(r), "test")),
                m(r3, lambda r: A2(r)["n_demonstrated"]), m(r3, lambda r: d3(C2(r), "powder")),
                m(r3, lambda r: d3(C2(r), "blend")), m(r3, lambda r: d3(C2(r), "blown_large")),
                m(r3, lambda r: d3(C2(r), "immersion")), m(r3, lambda r: d3(C2(r), "immersion_stopped")),
                m(r3, lambda r: C2(r)["n_demonstrated"])]
        fmt = lambda x: "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.0f}"
        L.append(f"| {LABEL.get(a, a)} -> {LABEL.get(b, b)} | " +
                 " | ".join(f"{fmt(x)} -> {fmt(y)}" for x, y in zip(row2, row3)) + " |")
    return "\n".join(L)


def _first(c, target, horizon):
    d = hit_days(c, target)
    return d if d is not None else math.inf


def table_pairs(rows_a, rows_b, pairs, T, horizon=365, title=""):
    """Paired comparisons on the seeds both arms have: best new alloy (a - b, mean ± SE, seeds ahead/behind), and per
    target which arm got there first (a seed that never got there counts as later), with each arm's median days."""
    A, Bb = by_policy(rows_a), by_policy(rows_b)
    L = [title, "", "| Campaign | A | B | seeds | best: A − B (A ahead/behind) | T1: A first / B first / tie | "
         "T1 median days A; B | T2: A first / B first / tie | T2 median days A; B | spent A − B ($k) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for camp in CAMPS:
        for a, b in pairs:
            if a not in A or b not in Bb:
                continue
            seeds = sorted(set(A[a]) & set(Bb[b]))
            if not seeds:
                continue
            ra, rb = {s: A[a][s] for s in seeds}, {s: Bb[b][s] for s in seeds}
            dm, dse, up, dn, n = paired(ra, rb, lambda r: r["campaigns"][camp]["best_new"])
            cells = []
            for tn in ("T1", "T2"):
                fa = [_first(ra[s]["campaigns"][camp]["curve_new"], T[tn][camp], horizon) for s in seeds]
                fb = [_first(rb[s]["campaigns"][camp]["curve_new"], T[tn][camp], horizon) for s in seeds]
                wa = sum(1 for x, y in zip(fa, fb) if x < y)
                wb = sum(1 for x, y in zip(fa, fb) if y < x)
                ma = B3.km_median([x if math.isfinite(x) else None for x in fa], horizon)
                mb = B3.km_median([y if math.isfinite(y) else None for y in fb], horizon)
                fm = lambda m: f"{m:.0f}" if m is not None else f">{horizon}"
                cells += [f"{wa} / {wb} / {n - wa - wb}", f"{fm(ma)}; {fm(mb)}"]
            ds = np.mean([ra[s]["campaigns"][camp]["spent"] - rb[s]["campaigns"][camp]["spent"] for s in seeds]) / 1e3
            L.append(f"| {CNAME[camp].split(' (')[0]} | {LABEL.get(a, a)} | {LABEL.get(b, b)} | {n} | {dm:+.2f} ± {dse:.2f} "
                     f"({up}/{dn}) | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {ds:+.1f} |")
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
    if main_rows:
        md += ["", table_pairs(main_rows, main_rows,
                               [("bofn3", "bofn3_usd"), ("pkgfn3", "bofn3_usd"), ("pkgfn3", "bofn3"),
                                ("bofn3", "tiered"), ("pkgfn3", "tiered"), ("bofn3", "heuristic"),
                                ("pkgfn3", "heuristic"), ("bofn3", "gpbo"), ("pkgfn3", "gpbo")], T,
                               title="## Paired comparisons within the main benchmark (same seeds)")]
    for name, ref in (("cu_hidden", "tiered"), ("cu_money", "tiered"), ("cu_proxy", None), ("cu_ablation", None)):
        rows = B3.load(name)
        if rows:
            md += ["", f"## {name}", table_main(rows, T, ref or "tiered")]
            N[name] = numbers(rows, T)
            if main_rows:
                pp = [(p, p) for p in by_policy(rows)] + [(p, "tiered") for p in by_policy(rows) if p != "tiered"]
                md += ["", table_pairs(rows, main_rows, pp, T, title=f"### {name} against the main benchmark "
                                                                      f"(B = main, same seeds)")]
    conv = B3.load("conventional")
    if conv:
        md += ["", "## Conventional lab, three years at three years' money (async)", table_main(conv, T, "tiered", 1095)]
        N["conventional"] = numbers(conv, T, 1095)
        fig_best_vs_days(conv, T, OUT / "twin3_conventional_best_vs_days.png",
                         "Round 3, simulated: the conventional lab with the same freedom, three years")
    if main_rows:
        r3 = by_policy(main_rows)
        fig_counts(None, r3, OUT / "twin3_counts.png")
        r2 = B2.load("main")
        if r2:
            md += ["", "## Alloys and evaluations a year, round 2 -> round 3 (main benchmark, seed means)",
                   table_counts(r2, main_rows)]
            N["round2_main"] = numbers(r2, T)
    (OUT / "tables.md").write_text("\n".join(md) + "\n")
    (OUT / "numbers.json").write_text(json.dumps(B2._jsonable(N), indent=1))
    print("\n".join(md))


if __name__ == "__main__":
    main()

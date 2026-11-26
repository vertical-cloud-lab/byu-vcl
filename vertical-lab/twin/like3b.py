"""Round 3b: the lab comparison like with like.

    python3 -m twin.like3b           # -> out/twin3b/like3b.json and out/twin3b/tables.md

Round 3's lab factors set a stocked vertical lab against a conventional lab ordering metal as it goes, so the stock's
share was not measured. Here each lab runs both ways, and every speed-up is given four ways:

* **lean / lean**: both labs ordering metal as each charge needs it;
* **stocked / stocked**: both with the standing inventory bought on day 0;
* **stocked / lean**: round 3's pairing (the vertical lab stocked, the conventional lab lean);
* **lean / stocked**: the other mixed pair.

The vertical lab runs one year at one year's money, the conventional lab three years at three years' money (round 3's
set-up). Each vertical-lab policy is set against the same policy in the conventional lab and against the conventional
lab run by rule of thumb (the heuristic).

**Days to a target** are per seed, from the run's best-so-far curve of new demonstrated alloys; a seed that never
reaches the target is censored at its horizon. **Medians** are Kaplan-Meier medians over seeds for every arm (the
smallest day by which half the seeds have got there; with all seeds there, the lower middle one), one rule
throughout, unlike round 3's ``econ_summary.json``. **The factor** is the conventional arm's median over the vertical
arm's. When fewer than half the conventional lab's seeds get there in three years its median is unbounded and the
factor is a lower bound (at least 1,095 days over the vertical median, written ``>= x``); when fewer than half the
vertical lab's get there in a year, an upper bound (``<= x``). **Intervals** are 95 % percentile intervals from a
paired bootstrap over seeds (seeds resampled together in both arms, 2,000 draws), on the seeds both arms have.
**Paired differences** are per seed: the days the vertical lab saves (conventional minus vertical) where both got
there, mean ± SE; and in how many seeds the vertical lab got there first (a seed that never gets there counts as
last).

**Cost**, on one basis throughout: *campaign spend to the target*, the money the campaign has spent (metal and
consumables, the stock where there is one, outside services) on the day it first reaches the target; no staff,
equipment or building. Its factor is the conventional arm's median spend over the vertical arm's, with the same
censoring rule (an arm that doesn't get there is censored at everything it spent).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from twin import accel as AC
from twin import bench2 as B2

HERE = Path(__file__).resolve().parent
R3 = HERE.parent / "out" / "twin3" / "runs"
R3B = HERE.parent / "out" / "twin3b" / "runs"
OUT = HERE.parent / "out" / "twin3b"

POLICIES = ("heuristic", "tiered", "bofn3", "pkgfn3")
NAMES = {"heuristic": "Heuristic", "tiered": "Tiered screening (the funnel)", "bofn3": "BOFN, time-aware",
         "pkgfn3": "pKGFN, time-aware"}
CAMPS = {"flaime_al": "Aluminium (FLAIME)", "onr_cu": "Copper (ONR)"}
TNAMES = {"T1": "the best existing alloy on this synthetic benchmark (T1)", "T2": "halfway to the best alloy (T2)"}
PAIRS = (("lean", "lean"), ("stocked", "stocked"), ("stocked", "lean"), ("lean", "stocked"))
PAIR_NAMES = {("lean", "lean"): "both lean", ("stocked", "stocked"): "both stocked",
              ("stocked", "lean"): "vertical stocked, conventional lean (round 3)",
              ("lean", "stocked"): "vertical lean, conventional stocked"}
HORIZON = {"vertical_lab": 365.0, "proposed": 1095.0}


def _rows(path):
    if not Path(path).exists():
        return []
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def arms() -> dict:
    """{(facility, stock, policy): {seed: row}} from round 3's committed runs and round 3b's."""
    A = {}

    def add(rows, src):
        for r in rows:
            c = r["cfg"]
            if c.get("cu_hidden") or c.get("cu_budget") or c.get("crucible", 225) != 225:
                continue
            if c["policy"] not in POLICIES:
                continue
            k = (c["facility"], c.get("stock", "stocked"), c["policy"])
            A.setdefault(k, {}).setdefault(c["seed"], dict(r, _src=src))
    add(_rows(R3 / "main.jsonl"), "out/twin3/runs/main.jsonl")
    add(_rows(R3 / "conventional.jsonl"), "out/twin3/runs/conventional.jsonl")
    for nm in ("v_lean", "c_stocked", "c_lean_net"):
        add(_rows(R3B / f"{nm}.jsonl"), f"out/twin3b/runs/{nm}.jsonl")
    return A


def to_target(row, camp, target, x="days"):
    """(days or dollars to first reach target, reached?) for one run; censored at its horizon or its total spend."""
    c = row["campaigns"][camp]
    h = B2.hit(c["curve_new"], target, 2)
    if h:
        return (float(h[0]) if x == "days" else float(h[1])), True
    if x == "days":
        return float(row["cfg"].get("days", 365)), False
    return float(c["spent"]), False


def km(vals, ok):
    return AC.km_median(list(vals), list(ok)) if len(vals) else float("nan")


def _ratio(a, b):
    if not math.isfinite(a) and not math.isfinite(b):
        return float("nan")
    if not math.isfinite(b):
        return 0.0
    if not math.isfinite(a):
        return float("inf")
    return a / b if b > 0 else float("inf")


def factor(conv, vert, seeds, camp, target, x="days", n_boot=2000, seed=0):
    """Conventional arm against vertical arm on the given seeds: the factor, its bound, a paired bootstrap interval,
    counts and paired differences."""
    tc = [to_target(conv[s], camp, target, x) for s in seeds]
    tv = [to_target(vert[s], camp, target, x) for s in seeds]
    xc, ec = np.array([t[0] for t in tc]), np.array([t[1] for t in tc])
    xv, ev = np.array([t[0] for t in tv]), np.array([t[1] for t in tv])
    mc, mv = km(xc, ec), km(xv, ev)
    f = _ratio(mc, mv)
    bound = None
    if not math.isfinite(mc) and math.isfinite(mv):
        bound = ("lower", float(np.max(xc)) / mv)
    elif math.isfinite(mc) and not math.isfinite(mv):
        bound = ("upper", mc / float(np.max(xv)))
    rng = np.random.default_rng(seed)
    boots = []
    n = len(seeds)
    for _ in range(n_boot):
        i = rng.integers(n, size=n)
        boots.append(_ratio(km(xc[i], ec[i]), km(xv[i], ev[i])))
    b = np.array([v for v in boots if not math.isnan(v)])
    lo, hi = AC._q(b, [0.025, 0.975]) if len(b) else (float("nan"), float("nan"))
    both = ec & ev
    d = (xc - xv)[both]
    inf_c = np.where(ec, xc, np.inf)
    inf_v = np.where(ev, xv, np.inf)
    v_first = int(np.sum(inf_v < inf_c))
    c_first = int(np.sum(inf_c < inf_v))
    return dict(n=n, seeds=list(seeds), median_conv=mc, median_vert=mv, factor=f, bound=bound, lo=lo, hi=hi,
                hit_conv=int(ec.sum()), hit_vert=int(ev.sum()), v_first=v_first, c_first=c_first,
                diff_mean=float(d.mean()) if len(d) else None,
                diff_se=float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else None, n_both=int(both.sum()),
                per_seed=[dict(seed=s, conv=(float(a) if e1 else None), vert=(float(c) if e2 else None))
                          for s, a, e1, c, e2 in zip(seeds, xc, ec, xv, ev)])


def arm_stats(arm, seeds, camp, target, x="days"):
    t = [to_target(arm[s], camp, target, x) for s in seeds]
    xs, ok = [a for a, _ in t], [b for _, b in t]
    return dict(n=len(seeds), hit=int(sum(ok)), median=km(xs, ok),
                best_mean=float(np.mean([arm[s]["campaigns"][camp]["best_new"] for s in seeds])),
                best_se=float(np.std([arm[s]["campaigns"][camp]["best_new"] for s in seeds], ddof=1)
                              / math.sqrt(len(seeds))) if len(seeds) > 1 else 0.0,
                spent_mean=float(np.mean([arm[s]["campaigns"][camp]["spent"] for s in seeds])))


def median_seeds(A=None, T=None) -> dict:
    """For a replay: each arm's seed at its Kaplan-Meier median day to each target (the seed whose day is the median;
    ties broken by the final best alloy nearest the arm's median final best, then by the lower seed), with the event
    log that seed has. {arm: {campaign: {target: dict(seed, day, hit, of, events)}}}."""
    A = A or arms()
    T = T or B2.targets()
    ev3b = HERE.parent / "out" / "twin3b" / "events"
    out = {}
    for (fac, stock, pol), rows in sorted(A.items()):
        key = f"{fac}|{stock}|{pol}"
        out[key] = {}
        for camp in CAMPS:
            out[key][camp] = {}
            bests = {s: r["campaigns"][camp]["best_new"] for s, r in rows.items()}
            mb = float(np.median(list(bests.values())))
            for tn, tv in T.items():
                tt = {s: to_target(r, camp, tv[camp]) for s, r in rows.items()}
                m = km([v[0] for v in tt.values()], [v[1] for v in tt.values()])
                if math.isfinite(m):
                    cand = [s for s, v in tt.items() if v[1] and v[0] == m]
                else:
                    cand = [s for s, v in tt.items() if not v[1]]
                cand.sort(key=lambda s: (abs(bests[s] - mb), s))
                s = cand[0] if cand else None
                rid = None
                if s is not None:
                    from twin import bench3 as B3
                    rid = B3.run_id(rows[s]["cfg"])
                    f = ev3b / f"{rid}.json.xz"
                    f3 = HERE.parent / "out" / "twin3" / "events" / f"{rid}.json"
                    rid = (str(f.relative_to(HERE.parent)) if f.exists() else
                           str(f3.relative_to(HERE.parent)) if f3.exists() else None)
                out[key][camp][tn] = dict(seed=s, day=(m if math.isfinite(m) else None), hit=sum(v[1] for v in tt.values()),
                                          of=len(tt), events=rid)
    return out


def run(n_boot=2000) -> dict:
    A = arms()
    T = B2.targets()
    S = dict(targets=T, arms={}, comparisons=[], stock_effect=[])
    for (fac, stock, pol), rows in sorted(A.items()):
        S["arms"][f"{fac}|{stock}|{pol}"] = dict(seeds=sorted(rows), sources=sorted({r["_src"] for r in rows.values()}),
                                                 campaigns={camp: {tn: arm_stats(rows, sorted(rows), camp, tv[camp])
                                                                   for tn, tv in T.items()} for camp in CAMPS})
    for pol in POLICIES:
        for vs, cs in PAIRS:
            V = A.get(("vertical_lab", vs, pol))
            for ref in dict.fromkeys((pol, "heuristic")):
                C = A.get(("proposed", cs, ref))
                if not V or not C:
                    continue
                seeds = sorted(set(V) & set(C))
                if len(seeds) < 2:
                    continue
                for camp in CAMPS:
                    for tn, tv in T.items():
                        rec = dict(policy=pol, ref=ref, vert_stock=vs, conv_stock=cs, campaign=camp, target=tn)
                        rec["days"] = factor(C, V, seeds, camp, tv[camp], "days", n_boot)
                        rec["usd"] = factor(C, V, seeds, camp, tv[camp], "usd", n_boot)
                        S["comparisons"].append(rec)
    # the stock's own effect, in each lab and for each policy: lean against stocked on the same seeds
    for fac in ("vertical_lab", "proposed"):
        for pol in POLICIES:
            L, St = A.get((fac, "lean", pol)), A.get((fac, "stocked", pol))
            if not L or not St:
                continue
            seeds = sorted(set(L) & set(St))
            if len(seeds) < 2:
                continue
            for camp in CAMPS:
                for tn, tv in T.items():
                    rec = dict(facility=fac, policy=pol, campaign=camp, target=tn)
                    rec["days"] = factor(L, St, seeds, camp, tv[camp], "days", n_boot)
                    rec["usd"] = factor(L, St, seeds, camp, tv[camp], "usd", n_boot)
                    bl = np.array([L[s]["campaigns"][camp]["best_new"] for s in seeds])
                    bs = np.array([St[s]["campaigns"][camp]["best_new"] for s in seeds])
                    dd = bs - bl
                    rec["best_diff"] = dict(mean=float(dd.mean()), se=float(dd.std(ddof=1) / math.sqrt(len(dd))),
                                            n=len(dd))
                    S["stock_effect"].append(rec)
    S["median_seeds"] = median_seeds(A, T)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "like3b.json").write_text(json.dumps(B2._jsonable(S), indent=1, default=str))
    (OUT / "tables.md").write_text(tables(S))
    return S


# ------------------------------------------------------------------------------------------------------- tables
def _d(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    if not math.isfinite(v):
        return "never"
    return f"{v:.0f}"


def fmt_factor(r, money=False):
    f, b = r["factor"], r["bound"]
    if b is not None:
        s = (">= " if b[0] == "lower" else "<= ") + f"{b[1]:.1f}x"
    elif math.isnan(f):
        s = "neither"
    else:
        s = f"{f:.1f}x"
    if b is None and not math.isnan(f):
        hi = "∞" if not math.isfinite(r["hi"]) else f"{r['hi']:.1f}"
        lo = ("∞" if not math.isfinite(r["lo"]) else "0" if r["lo"] == 0 else f"{r['lo']:.1f}")
        s += f" ({lo}-{hi})"
    return s


def _diff_cell(r):
    x = r["days"]
    if not x["n_both"]:
        return f"none both ({x['hit_vert']}/{x['n']} vs {x['hit_conv']}/{x['n']})"
    se = f" ± {x['diff_se']:.0f}" if x["diff_se"] is not None else ""
    return f"{x['diff_mean']:+.0f}{se} d (n={x['n_both']}); first {x['v_first']}-{x['c_first']}"


def _cell(r, money=False):
    x = r["usd" if money else "days"]
    s = fmt_factor(x, money)
    s += f"; {x['hit_vert']}/{x['n']} vs {x['hit_conv']}/{x['n']}"
    if not money:
        s += f"; first in {x['v_first']}/{x['n']}"
    return s


def tables(S) -> str:
    T = S["targets"]
    L = ["# Round 3b: the lab comparison, like with like (simulated)", "",
         "Generated by `python -m twin.like3b` from round 3's committed runs (`out/twin3/runs/`) and round 3b's "
         "(`out/twin3b/runs/`). Everything is simulated: synthetic truths, simulated instruments, assumed capacities, "
         "prices and schedules. The vertical lab runs one year at one year's money; the conventional lab three years "
         "at three years' money.", "",
         "Each cell: **the factor** (conventional lab's Kaplan-Meier median over the vertical lab's; `>=` a lower "
         "bound where fewer than half the conventional seeds got there, `<=` an upper bound where fewer than half the "
         "vertical seeds did), its 95 % paired-bootstrap interval, then the seeds that got there (vertical vs "
         "conventional) and the seeds in which the vertical lab got there first.", "",
         "Targets: " + "; ".join(f"{TNAMES[t]}: aluminium {T[t]['flaime_al']:.3f}, copper {T[t]['onr_cu']:.3f}"
                                  for t in ("T1", "T2")) + ".", ""]
    comps = S["comparisons"]

    def get(pol, ref, vs, cs, camp, tn):
        for r in comps:
            if (r["policy"], r["ref"], r["vert_stock"], r["conv_stock"], r["campaign"], r["target"]) == \
                    (pol, ref, vs, cs, camp, tn):
                return r
        return None

    for money in (False, True):
        L.append("## " + ("Speed-up to the target (days)" if not money else
                          "Cost to the target: campaign spend (one basis for every table in this section)"))
        L.append("")
        if money:
            L += ["Basis: the money the campaign had spent on the day it first reached the target (metal, consumables, "
                  "the day-0 stock where there is one, outside services); no staff, equipment or building. The factor "
                  "is the conventional lab's median spend over the vertical lab's (above 1: the vertical lab spends "
                  "less to get there).", ""]
        for camp, cname in CAMPS.items():
            for tn in ("T1", "T2"):
                L.append(f"### {cname}: {TNAMES[tn]}")
                L.append("")
                L.append("| Vertical lab's policy | Against | " + " | ".join(PAIR_NAMES[p] for p in PAIRS) + " |")
                L.append("|---|---|" + "---|" * len(PAIRS))
                for pol in POLICIES:
                    for ref in dict.fromkeys((pol, "heuristic")):
                        cells = []
                        for vs, cs in PAIRS:
                            r = get(pol, ref, vs, cs, camp, tn)
                            cells.append(_cell(r, money) if r else "not run")
                        if all(c == "not run" for c in cells):
                            continue
                        against = "the same policy" if ref == pol else "the rule of thumb (heuristic)"
                        L.append(f"| {NAMES[pol]} | {against} | " + " | ".join(cells) + " |")
                L.append("")
    L += ["## Paired differences in days", "",
          "Per seed, the days the vertical lab saved (the conventional lab's day minus the vertical lab's), mean ± SE "
          "over the seeds where both got there (n); then the seeds in which the vertical lab got there first and those "
          "in which the conventional lab did (a seed that never gets there counts as last; seeds where neither did "
          "are in neither count).", ""]
    for camp, cname in CAMPS.items():
        for tn in ("T1", "T2"):
            L.append(f"### {cname}: {TNAMES[tn]}")
            L.append("")
            L.append("| Vertical lab's policy | Against | " + " | ".join(PAIR_NAMES[p] for p in PAIRS) + " |")
            L.append("|---|---|" + "---|" * len(PAIRS))
            for pol in POLICIES:
                for ref in dict.fromkeys((pol, "heuristic")):
                    cells = []
                    for vs, cs in PAIRS:
                        r = get(pol, ref, vs, cs, camp, tn)
                        cells.append(_diff_cell(r) if r else "not run")
                    if all(c == "not run" for c in cells):
                        continue
                    against = "the same policy" if ref == pol else "the rule of thumb (heuristic)"
                    L.append(f"| {NAMES[pol]} | {against} | " + " | ".join(cells) + " |")
            L.append("")
    # medians of each arm
    L += ["## Each arm on its own", "",
          "Kaplan-Meier median days to each target, the seeds that got there, and the final best alloy (mean ± SE). "
          "Seeds: the vertical lab's arms and the conventional lab's heuristic and funnel have 12 (0-11); the "
          "conventional lab's BOFN and pKGFN have fewer (three simulated years each).", "",
          "| Lab | Stock | Policy | Al best | Al T1 | Al T2 | Cu best | Cu T1 | Cu T2 | Mean campaign spend Al / Cu |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for key, a in S["arms"].items():
        fac, stock, pol = key.split("|")
        c = a["campaigns"]
        al, cu = c["flaime_al"], c["onr_cu"]

        def tt(x):
            return f"{x['hit']}/{x['n']}; {_d(x['median']) if math.isfinite(x['median']) else '>' + str(int(HORIZON[fac]))}"
        L.append(f"| {'vertical' if fac == 'vertical_lab' else 'conventional'} | {stock} | {NAMES[pol]} | "
                 f"{al['T1']['best_mean']:.2f} ± {al['T1']['best_se']:.2f} | {tt(al['T1'])} | {tt(al['T2'])} | "
                 f"{cu['T1']['best_mean']:.2f} ± {cu['T1']['best_se']:.2f} | {tt(cu['T1'])} | {tt(cu['T2'])} | "
                 f"${al['T1']['spent_mean'] / 1e3:.0f}k / ${cu['T1']['spent_mean'] / 1e3:.0f}k |")
    L.append("")
    # the stock's own effect
    L += ["## What the stock does within each lab", "",
          "Each lab lean against itself stocked, same policy, same seeds: the factor is the lean arm's median days over "
          "the stocked arm's (above 1: the stock makes the lab faster), the seeds that got there (stocked vs lean), and "
          "the paired difference in the final best alloy (stocked minus lean, mean ± SE).", "",
          "| Lab | Policy | Campaign | T1: factor | T2: factor | Final best, stocked − lean |", "|---|---|---|---|---|---|"]
    se = S["stock_effect"]
    for fac in ("vertical_lab", "proposed"):
        for pol in POLICIES:
            for camp in CAMPS:
                rs = {r["target"]: r for r in se if (r["facility"], r["policy"], r["campaign"]) == (fac, pol, camp)}
                if not rs:
                    continue

                def c2(r):
                    x = r["days"]
                    return f"{fmt_factor(x)}; {x['hit_vert']}/{x['n']} vs {x['hit_conv']}/{x['n']}"
                bd = rs["T1"]["best_diff"]
                L.append(f"| {'vertical' if fac == 'vertical_lab' else 'conventional'} | {NAMES[pol]} | "
                         f"{'Al' if camp == 'flaime_al' else 'Cu'} | {c2(rs['T1'])} | {c2(rs['T2'])} | "
                         f"{bd['mean']:+.2f} ± {bd['se']:.2f} (n={bd['n']}) |")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    S = run()
    print((OUT / "tables.md").read_text()[:4000])

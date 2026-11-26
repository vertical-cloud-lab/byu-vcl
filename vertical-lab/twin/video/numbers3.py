"""Every number round 3's cards and narration show, read from the committed summaries, with where each came from.

    TWIN_VIDEO_ROUND=3 python -m twin.video.numbers3      # -> out/twin3/video/numbers.json, and prints its checks

Sources:
  out/twin3/fig/numbers.json        twin.figures3: the tables' numbers (best new alloy, runs that reached each target,
                                    Kaplan-Meier median days), for the main benchmark, the conventional lab and the
                                    three-times-money test
  out/twin3/econ/econ_summary.json  twin.econ3: the lab-against-lab factors with their intervals (to the best existing
                                    alloy's score in `acceleration`, to the halfway target in `acceleration_T2`), the
                                    cost ratios, the cost per alloy and the utilization
  out/twin3/runs/*.jsonl            the runs themselves: the replayed seed among its twelve, the paired differences of
                                    the three-times-money test (as tables.md prints them), the runs that reached a
                                    target inside their first 365 days, where the money went, atomizer runs a week
  out/twin2/oracle.json             the targets and the share of random designs that beat the first
  the replayed run's event log      atomizer runs a week in the replayed year

Nothing here is fitted or re-simulated. A number that isn't in a committed file is not made up: `missing` lists what
round 3 did not run, and the cards say so.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

from . import data as D

N = 12                                                  # runs per arm in every comparison the cards show
HEUR, FUNNEL, PKGFN, BOFN = "heuristic", "tiered", "pkgfn3", "bofn3"
POLICY_WORDS = {"bofn3": "BOFN, time-aware", "pkgfn3": "pKGFN, time-aware", "bofn3_usd": "BOFN, per dollar",
                "tiered": "tiered CALPHAD screening", "heuristic": "the heuristic", "gpbo": "GP-BO",
                "sobol": "Sobol", "random": "random"}
# the lab's own atomizer record, from DAL's log (digital-alloy-lab atomizer-runs/runs.csv at 8320f13, on PR 286): ten
# runs from 2026-10-02 to 2026-11-13, two of them good (Oct 27, about 91 % of the charge; Nov 10, about 75 %, estimated)
LAB_ATOMIZER = dict(runs=10, weeks=6, good=2, first="2026-10-02", last="2026-11-13", best_yield=0.91,
                    source="digital-alloy-lab atomizer-runs/runs.csv @ 8320f13 (PR 286); DAL audit PR 293 section 2")
# the twin's atomizer, as coded: twin/physics.py atomize() (p_fail = 0.06 + ..., usable = 0.91 * ...) and
# twin/facility.py (starts 08:00, 10:30, 13:00 Mon-Fri and one on Saturday)
TWIN_ATOMIZER = dict(p_fail_base=0.06, usable_good=0.91, slots_week=16,
                     source="twin/physics.py atomize(); twin/facility.py the atomizer's start slots")
_N: dict = {}


def _num(v):
    if v in ("inf", "Infinity"):
        return float("inf")
    return None if v is None else float(v)


def _arm(g: dict) -> dict:
    """One policy's campaign entry of fig/numbers.json, as the cards read it."""
    return dict(n=g["n"], best=g["best_mean"], se=g["best_se"],
                T1=dict(hit=g["T1"]["hit"], day=g["T1"]["km_median"]),
                T2=dict(hit=g["T2"]["hit"], day=g["T2"]["km_median"]),
                spent=g.get("spent_mean"), new_alloys=g.get("n_new_alloys"), stops=g.get("stops"))


def _cell(d: dict, n: int = N) -> dict:
    """One lab-against-lab factor as it is shown. `kind`: 'factor' (an estimate with its interval), 'at_least' (the
    conventional lab reached the target in half its runs or fewer, so its median is its last run to get there, or
    later: a lower bound), or 'none' (the automated lab reached it in half its runs or fewer: no median, no factor)."""
    hn, hr = round(_num(d["hit_new"]) * n), round(_num(d["hit_ref"]) * n)
    af, lo, hi = _num(d.get("af")), _num(d.get("lo")), _num(d.get("hi"))
    out = dict(hit_new=hn, hit_ref=hr, n=n, day_new=_num(d.get("median_new")), day_ref=_num(d.get("median_ref")),
               lo=lo, hi=hi)
    if 2 * hn <= n:
        out.update(kind="none", af=None)
    elif 2 * hr < n:                                    # no median in the conventional lab: horizon / automated's
        out.update(kind="at_least", af=_num(d.get("af_bound")))
    elif 2 * hr == n:
        out.update(kind="at_least", af=af)
    else:
        out.update(kind="factor", af=af)
    return out


def numbers() -> dict:
    if _N:
        return _N
    F = json.loads((D.OUT3 / "fig" / "numbers.json").read_text())
    E = json.loads((D.OUT3 / "econ" / "econ_summary.json").read_text())
    O = json.loads((D.OUT2 / "oracle.json").read_text())
    out: dict = {}
    # ---------------------------------------------------------------------------------------------- the targets
    out["targets"] = dict(
        T1=F["targets"]["T1"], T2=F["targets"]["T2"], ref={c: O[c]["sota"] for c in D.CAMPAIGNS},
        frac_random={c: O[c]["random_default_process"]["frac_above_sota"] for c in D.CAMPAIGNS},
        src="out/twin3/fig/numbers.json targets; out/twin2/oracle.json sota, random_default_process.frac_above_sota")
    out["targets"]["one_in"] = round(1.0 / min(out["targets"]["frac_random"].values()))
    # -------------------------------------------------------------------------------------- the main benchmark
    out["main"] = {p: {c: _arm(F["main"][p][c]) for c in D.CAMPAIGNS} for p in F["main"]}
    out["conventional"] = {p: {c: _arm(F["conventional"][p][c]) for c in D.CAMPAIGNS} for p in F["conventional"]}
    out["main_all_funnel_cu"] = _arm(F["main_all"][FUNNEL]["onr_cu"])        # the funnel on copper over 24 seeds
    # aluminium's halfway target: the most runs any policy without a network model got there in
    out["al_T2_others_max"] = max(out["main"][p]["flaime_al"]["T2"]["hit"] for p in out["main"]
                                  if p not in (BOFN, PKGFN, "bofn3_usd"))
    # --------------------------------------------------------------- three times the copper money (as tables.md)
    main = {(r["cfg"]["policy"], r["cfg"]["seed"]): r for r in D.rows3("main")}
    money = {(r["cfg"]["policy"], r["cfg"]["seed"]): r for r in D.rows3("cu_money")}
    cm = {}
    for p in (FUNNEL, BOFN, PKGFN, HEUR, "gpbo"):
        seeds = sorted(s for (q, s) in money if q == p)
        a = np.array([money[(p, s)]["campaigns"]["onr_cu"]["best_new"] for s in seeds])
        b = np.array([main[(p, s)]["campaigns"]["onr_cu"]["best_new"] for s in seeds])
        f = np.array([money[(FUNNEL, s)]["campaigns"]["onr_cu"]["best_new"] for s in seeds])

        def pair(x):
            return dict(mean=float(x.mean()), se=float(x.std(ddof=1) / math.sqrt(len(x))),
                        ahead=int((x > 1e-9).sum()), behind=int((x < -1e-9).sum()))
        g = _arm(F["cu_money"][p]["onr_cu"])
        assert g["n"] == len(seeds) and abs(g["best"] - float(a.mean())) < 1e-3, (p, g, a.mean())
        cm[p] = dict(g, seeds=seeds, own=pair(a - b), funnel=None if p == FUNNEL else pair(a - f),
                     base=float(b.mean()))
    out["cu_money"] = dict(cm, budget=180_000, base_budget=60_000,
                           src="out/twin3/runs/cu_money.jsonl against main.jsonl, same seeds (tables.md, cu_money)")
    # ----------------------------------------------------------------------------- the lab against a conventional lab
    acc, acc2 = E["acceleration"], E["acceleration_T2"]

    def cmp_(new, ref, camp):
        name = f"vertical lab + {new} vs conventional + {ref}"
        d1 = acc[name][camp]["compare"]["days"]
        c1, c2 = _cell(d1), _cell(acc2[name][camp])
        a3 = D.arm3("conventional", "proposed", ref, camp)
        b3 = D.arm3("main", "vertical_lab", new, camp)
        for tn, c in (("T1", c1), ("T2", c2)):                      # the conventional lab inside its first 365 days
            c["hit_ref_365"] = a3[tn]["hits_365"]
            assert a3[tn]["hits"] == c["hit_ref"] and b3[tn]["hits"] == c["hit_new"], (name, camp, tn)
            # the tables' day counts are Kaplan-Meier medians for every arm; econ_summary.json takes the ordinary
            # median for an arm whose 12 runs all got there (twin/accel.py), so its days differ there by a few (and
            # its factor with them). The cards show the days only where the two agree to the day.
            km_new, km_ref = b3[tn]["median"], a3[tn]["median"]
            c["km_new"], c["km_ref"] = km_new, km_ref
            c["days_ok"] = bool(c["kind"] != "none" and km_new is not None and km_ref is not None
                                and abs(km_new - c["day_new"]) < 0.5 and abs(km_ref - c["day_ref"]) < 0.5)
        return dict(name=name, new=new, ref=ref, T1=c1, T2=c2)
    out["labs"] = {
        "flaime_al": dict(same=cmp_(HEUR, HEUR, "flaime_al"), thumb=cmp_(PKGFN, HEUR, "flaime_al")),
        "onr_cu": dict(same=cmp_(FUNNEL, FUNNEL, "onr_cu"), thumb=cmp_(PKGFN, HEUR, "onr_cu")),
        "src": "out/twin3/econ/econ_summary.json acceleration (to the best existing alloy's score) and "
               "acceleration_T2 (to the halfway target): af, lo, hi, hit_new, hit_ref, median_new, median_ref",
        "stock": "every factor: the vertical lab stocked on day 0 (one-year runs) against the conventional lab "
                 "ordering metal as each charge needs it (three-year runs at three years' money)"}
    out["missing"] = [
        "both labs ordering metal as they go, or both stocked: round 3 has no run of the vertical lab ordering as it "
        "goes, nor of the conventional lab stocked (twin/bench3.py EXPERIMENTS), so the stock's share of a factor "
        "is not known here",
        "BOFN and pKGFN in the conventional lab (bench3's conventional_net): not run, so there is no same-policy "
        "comparison for them",
        "the tiered screen in the vertical lab against the heuristic in the conventional lab: not among "
        "econ_summary.json's comparisons"]
    # ------------------------------------------------------------------------------------------------- the cost
    name = f"vertical lab + {PKGFN} vs conventional + {HEUR}"
    K = E["key_numbers"]
    cost = {}
    for c in D.CAMPAIGNS:
        cc = acc[name][c]["compare"]["cost"]
        cost[c] = {D.canon_basis(k): dict(ratio=_num(v["ratio"]), lo=_num(v["lo"]), hi=_num(v["hi"]),
                                          new=_num(v["median_new"]), ref=_num(v["median_ref"]))
                   for k, v in cc.items()}
    out["cost"] = dict(
        to_T1=cost, comparison=name,
        per_alloy={k.split("|", 1)[1]: v for k, v in K.items() if k.startswith("cost_per_alloy|")},
        capex=dict(vertical=K["capex_vertical"], conventional=K["capex_conventional"]),
        fixed_year=dict(vertical=K["fixed_per_year_vertical"], conventional=K["fixed_per_year_conventional"]),
        src="out/twin3/econ/econ_summary.json acceleration.<comparison>.<campaign>.compare.cost and key_numbers")
    out["util"] = dict(capex_weighted=K["capex_weighted_utilization_campaigns"],
                       atomizer_slots=K["atomizer_utilization_campaigns"], outside_cap=K["outside_cap"],
                       src="econ_summary.json key_numbers")
    # ------------------------------------------------------------------------------------- where the money went
    share = {}
    for c in D.CAMPAIGNS:
        v = []
        for (p, s), r in main.items():
            sb = r["campaigns"][c]["spend_by"]
            v.append(sb.get("order", 0.0) / max(1e-9, sum(sb.values())))
        share[c] = float(np.mean(v))
    out["orders_share"] = dict(share, src="out/twin3/runs/main.jsonl spend_by.order over the total, all 96 runs")
    lots = [F["main"][p]["onr_cu"]["done"].get("powder") or 0.0 for p in F["main"]]
    imm = [F["main"][p]["onr_cu"]["done"].get("immersion") or 0.0 for p in F["main"]]
    out["cu_year"] = dict(lots=[min(lots), max(lots)], immersions=[min(imm), max(imm)],
                          src="out/twin3/fig/numbers.json main.<policy>.onr_cu.done powder and immersion: the least "
                              "and the most over the 8 policies (each a mean of 12 runs)")
    # ---------------------------------------------------------------------------------------- the replayed run
    try:
        R = D.Replay()
        pol, seed = R.policy, R.seed
        rep = dict(policy=pol, seed=seed, file=R.path.name, n=N)
        for c in D.CAMPAIGNS:
            a = D.arm3("main", "vertical_lab", pol, c)
            i = a["seeds"].index(seed)
            rep[c] = {}
            for tn in ("T1", "T2"):
                days = a[tn]["days"]
                mine = days[i]
                order = sorted(x for x in days if x is not None)
                rep[c][tn] = dict(day=mine, median=a[tn]["median"], hits=a[tn]["hits"],
                                  rank=None if mine is None else order.index(mine) + 1, all=days)
            rep[c]["best"] = a["best"][i]
            rep[c]["best_rank"] = sorted(a["best"], reverse=True).index(a["best"][i]) + 1
        runs = int(np.sum(R.station == "atomizer"))
        rep["atomizer_runs"] = runs
        rep["atomizer_runs_week"] = runs / (R.horizon_days / 7.0)
        rep["helpers_busy"] = {h: v / R.horizon_h / (2 if h == "robot" else 1)
                               for h, v in getattr(R, "helper_h", {}).items()}
        out["replay"] = rep
    except Exception as e:                              # noqa: BLE001  (no event log yet)
        out["replay"] = dict(error=str(e))
    # atomizer runs a week across the main benchmark: the atomizer's booked hours over 2.5 h a run (round 3's notes)
    per = {}
    for (p, s), r in main.items():
        per.setdefault(p, []).append(r["busy_h"].get("atomizer", 0.0))
    out["atomizer"] = dict(twin=TWIN_ATOMIZER, lab=dict(LAB_ATOMIZER, runs_week=LAB_ATOMIZER["runs"] /
                                                        LAB_ATOMIZER["weeks"]))
    _N.update(out)
    return _N


def claims() -> list:
    """What the cards and the narration say in words, each checked against the numbers: (claim, holds)."""
    n = numbers()
    M, al, cu = n["main"], "flaime_al", "onr_cu"
    cm = n["cu_money"]
    best = lambda c: sorted(M, key=lambda p: -M[p][c]["best"])
    t1 = {p: M[p][al]["T1"]["day"] for p in M if M[p][al]["T1"]["day"] is not None}
    cst = n["cost"]["to_T1"]
    rep = n["replay"]
    out = [
        ("aluminium: time-aware BOFN and pKGFN finished highest", set(best(al)[:2]) == {BOFN, PKGFN}),
        ("copper: tiered screening finished ahead of every other policy", best(cu)[0] == FUNNEL),
        ("aluminium's halfway target: BOFN per dollar in 7 runs, no other policy in more than 2",
         M["bofn3_usd"][al]["T2"]["hit"] == 7 and n["al_T2_others_max"] == 2),
        ("the heuristic reaches aluminium's first target soonest", min(t1, key=t1.get) == HEUR),
        ("the heuristic then stalls: the halfway target in 1 of 12 runs", M[HEUR][al]["T2"]["hit"] == 1),
        ("BOFN and pKGFN reach aluminium's halfway target in about three months",
         all(75 <= M[p][al]["T2"]["day"] <= 105 for p in (BOFN, PKGFN))),
        ("more than four fifths of each campaign's spending is orders",
         all(0.8 < n["orders_share"][c] < 0.9 for c in (al, cu))),
        ("three times the money: BOFN and pKGFN draw level with tiered screening (within 0.05, and within 2 SE)",
         all(abs(cm[p]["funnel"]["mean"]) < 0.05 and abs(cm[p]["funnel"]["mean"]) < 2 * cm[p]["funnel"]["se"]
             for p in (BOFN, PKGFN))),
        ("three times the money: tiered screening is still first to both targets",
         all(cm[FUNNEL][t]["day"] < cm[p][t]["day"] for p in (BOFN, PKGFN) for t in ("T1", "T2"))),
        ("the cost intervals, equipment included, both include 1.0",
         all(cst[c]["full_alone"]["lo"] < 1.0 < cst[c]["full_alone"]["hi"] for c in (al, cu))),
        ("the replay is the median seed for aluminium's halfway target",
         abs(rep[al]["T2"]["day"] - rep[al]["T2"]["median"]) < 0.5),
        ("the replay's copper never reaches the first target, as in 4 of the 12 seeds",
         rep[cu]["T1"]["day"] is None and rep["n"] - rep[cu]["T1"]["hits"] == 4),
        ("the only committed event log of time-aware BOFN in the vertical lab is seed 0",
         sorted(q.name for q in (D.OUT3 / "events").glob("r3_vertical_lab_bofn3_s*.json")) ==
         ["r3_vertical_lab_bofn3_s0.json"]),
        ("copper, same policy in both labs, halfway target: a factor with both medians",
         n["labs"][cu]["same"]["T2"]["kind"] == "factor"),
        ("aluminium against rule of thumb, halfway target: a lower bound (6 of 12)",
         n["labs"][al]["thumb"]["T2"]["kind"] == "at_least" and n["labs"][al]["thumb"]["T2"]["hit_ref"] == 6),
        ("aluminium, the heuristic in both labs, halfway target: no speed-up (1 of 12 against 6 of 12)",
         n["labs"][al]["same"]["T2"]["kind"] == "none" and n["labs"][al]["same"]["T2"]["hit_new"] == 1
         and n["labs"][al]["same"]["T2"]["hit_ref"] == 6),
        ("copper against rule of thumb, halfway target: no factor (4 of 12 against 1 of 12)",
         n["labs"][cu]["thumb"]["T2"]["kind"] == "none" and n["labs"][cu]["thumb"]["T2"]["hit_new"] == 4
         and n["labs"][cu]["thumb"]["T2"]["hit_ref"] == 1),
    ]
    return out


def write() -> dict:
    n = numbers()
    D.VID.mkdir(parents=True, exist_ok=True)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, float):
            return "inf" if math.isinf(o) else round(o, 4)
        if isinstance(o, (np.floating, np.integer)):
            return clean(o.item())
        return o
    (D.VID / "numbers.json").write_text(json.dumps(clean(n), indent=1) + "\n")
    return n


# ------------------------------------------------------------------------------------------------- words
def x1(v) -> str:
    return "n/a" if v is None or not math.isfinite(v) else f"{v:.1f}x"


def rng(lo, hi) -> str:
    def f(v):
        return "unbounded" if v is None or not math.isfinite(v) else f"{v:.1f}"
    return f"{f(lo)} to {f(hi)}"


def cell_words(c: dict) -> tuple:
    """(the big text, the line under it) for one lab-against-lab cell."""
    counts = f"{c['hit_new']} of {c['n']} one-year runs against {c['hit_ref']} of {c['n']} three-year runs"
    if c["kind"] == "none":
        return "no factor", f"the automated lab got there in {counts}"
    if c["kind"] == "at_least":
        return f"at least {x1(c['af'])}", counts
    return x1(c["af"]), f"95 % interval {rng(c['lo'], c['hi'])}; {counts}"


if __name__ == "__main__":
    n = write()
    M = n["main"]
    print("targets", n["targets"])
    for c in D.CAMPAIGNS:
        for p in ("bofn3", "pkgfn3", "bofn3_usd", "tiered", "heuristic", "gpbo", "sobol", "random"):
            a = M[p][c]
            print(f"  {c:9s} {p:10s} {a['best']:.2f} ± {a['se']:.2f}  T1 {a['T1']['hit']}/12 {a['T1']['day']}  "
                  f"T2 {a['T2']['hit']}/12 {a['T2']['day']}")
    for c in D.CAMPAIGNS:
        for k in ("same", "thumb"):
            x = n["labs"][c][k]
            for tn in ("T1", "T2"):
                print(f"  {c:9s} {k:5s} {x['new']:9s} vs {x['ref']:9s} {tn}: {cell_words(x[tn])}  "
                      f"days {x[tn]['day_new']} vs {x[tn]['day_ref']}; conventional inside 365 d: "
                      f"{x[tn]['hit_ref_365']}")
    print("cu_money", {p: (round(v["best"], 3), round(v["se"], 3), v["n"], v["own"], v["funnel"]) for p, v in
                       n["cu_money"].items() if isinstance(v, dict)})
    print("cost", json.dumps(n["cost"]["to_T1"], default=str)[:900])
    print("per alloy", n["cost"]["per_alloy"])
    print("util", n["util"], "orders", n["orders_share"])
    print("replay", json.dumps(n["replay"], default=str)[:1500])
    print("atomizer", n["atomizer"])
    bad = 0
    for c, ok in claims():
        print("ok " if ok else "BAD", c)
        bad += not ok
    sys.exit(1 if bad else 0)

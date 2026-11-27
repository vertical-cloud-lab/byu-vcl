"""Every number round 3b's re-cut shows or speaks, read from the committed files, with where each came from.

    TWIN_VIDEO_ROUND=3b python -m twin.video.numbers3b     # -> out/twin3b/video/numbers.json, and prints its checks

It is round 3's numbers (numbers3.numbers(): the policies' results in the automated lab, the three-times-money test,
the atomizer, the targets) with round 3b's on top:

  out/twin3b/like3b.json   twin.like3b: what out/twin3b/tables.md prints. `comparisons`: the conventional lab's
                           Kaplan-Meier median over the vertical lab's, in days and in campaign spend, for every
                           policy against the same policy and against the rule of thumb, to both targets, in the
                           four pairings of stocked and ordering-as-it-goes; `stock_effect`: each lab against itself;
                           `median_seeds`: each arm's median seed, for a replay
  out/twin3b/runs/re_*.jsonl   round 3's committed rows rerun under the pin (each row's `committed_match`)
  out/twin3/...            as numbers3 reads them (round 3's own summaries)

Nothing is fitted, re-simulated or typed in. The words used on screen for the four pairings:
  like      both labs ordering metal as they go            (like3b: vertical lean, conventional lean)
  stocked   both labs stocked on day 0                     (stocked, stocked)
  round3    the automated lab stocked, the conventional lab ordering as it goes: round 3's pairing (stocked, lean)
  rev       the automated lab ordering as it goes, the conventional lab stocked (lean, stocked)
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

from . import data as D
from . import numbers3 as N3

HEUR, FUNNEL, PKGFN, BOFN = N3.HEUR, N3.FUNNEL, N3.PKGFN, N3.BOFN
PAIRS = {"like": ("lean", "lean"), "stocked": ("stocked", "stocked"), "round3": ("stocked", "lean"),
         "rev": ("lean", "stocked")}
PAIR_WORDS = {"like": "both labs ordering metal as they go", "stocked": "both labs stocked on day 0",
              "round3": "the automated lab stocked, the conventional lab ordering as it goes (round 3's pairing)",
              "rev": "the automated lab ordering as it goes, the conventional lab stocked"}
AL, CU = "flaime_al", "onr_cu"
_N: dict = {}
_L: dict = {}


def like3b() -> dict:
    if not _L:
        _L.update(json.loads((D.OUT3B / "like3b.json").read_text()))
    return _L


def _f(v):
    """like3b.json's numbers: null, 'inf' and NaN as they come out of json."""
    if v is None:
        return None
    if isinstance(v, str):
        return float("inf") if "inf" in v.lower() else float("nan")
    return float(v)


def cell(x: dict) -> dict:
    """One factor of like3b.json (a `days` or `usd` record) as the cards show it.

    kind: 'factor' (an estimate with its 95 % interval); 'at_least' (the conventional arm reached the target in half
    its seeds or fewer, so its median is its last seed to get there, or later: a lower bound, as round 3's cut rules
    and as tables.md's '>='); 'at_most' (the same for the automated arm: an upper bound, tables.md's '<='); 'none'
    (neither arm has a median). new = the automated lab's arm, ref = the conventional lab's."""
    n, hn, hr = int(x["n"]), int(x["hit_vert"]), int(x["hit_conv"])
    f, lo, hi = _f(x["factor"]), _f(x["lo"]), _f(x["hi"])
    b = x.get("bound")
    out = dict(n=n, hit_new=hn, hit_ref=hr, lo=lo, hi=hi, m_new=_f(x["median_vert"]), m_ref=_f(x["median_conv"]),
               first_new=int(x["v_first"]), first_ref=int(x["c_first"]), diff_mean=_f(x.get("diff_mean")),
               diff_se=_f(x.get("diff_se")), n_both=int(x.get("n_both") or 0),
               per_seed=[dict(seed=q["seed"], new=q["vert"], ref=q["conv"]) for q in x.get("per_seed") or []])
    if b is not None:                                   # one arm has no median: tables.md's >= or <=
        out.update(kind="at_least" if b[0] == "lower" else "at_most", af=float(b[1]))
    elif f is None or math.isnan(f):
        out.update(kind="none", af=None)
    elif 2 * hr <= n:                                   # exactly half: the median is the last seed to get there
        out.update(kind="at_least", af=f)
    elif 2 * hn <= n:
        out.update(kind="at_most", af=f)
    else:
        out.update(kind="factor", af=f)
    return out


def _cmp(policy: str, ref: str, pair: str, camp: str, tn: str) -> dict:
    vs, cs = PAIRS[pair]
    for r in like3b()["comparisons"]:
        if (r["policy"], r["ref"], r["vert_stock"], r["conv_stock"], r["campaign"], r["target"]) == \
                (policy, ref, vs, cs, camp, tn):
            return dict(days=cell(r["days"]), usd=cell(r["usd"]), policy=policy, ref=ref, pair=pair,
                        campaign=camp, target=tn)
    raise KeyError((policy, ref, pair, camp, tn))


def _stock(fac: str, policy: str, camp: str, tn: str) -> dict:
    """Each lab against itself: here `new` is the stocked arm and `ref` the arm ordering as it goes (like3b's
    stock_effect: the lean arm's median over the stocked arm's; above 1, the stock makes that lab sooner)."""
    for r in like3b()["stock_effect"]:
        if (r["facility"], r["policy"], r["campaign"], r["target"]) == (fac, policy, camp, tn):
            return dict(days=cell(r["days"]), usd=cell(r["usd"]), best_diff=r["best_diff"], facility=fac,
                        policy=policy, campaign=camp, target=tn)
    raise KeyError((fac, policy, camp, tn))


def _arm(fac: str, stock: str, policy: str) -> dict:
    a = like3b()["arms"][f"{fac}|{stock}|{policy}"]
    return dict(seeds=a["seeds"], n=len(a["seeds"]), sources=a["sources"],
                **{c: {tn: dict(hit=int(v["hit"]), n=int(v["n"]), day=_f(v["median"]), best=_f(v["best_mean"]),
                                se=_f(v["best_se"]), spent=_f(v["spent_mean"]))
                       for tn, v in a["campaigns"][c].items()} for c in D.CAMPAIGNS})


def _reruns() -> dict:
    """Round 3's committed rows rerun under round 3b's pin, each compared with its committed row field by field
    (twin.bench3b.rerun_report: 'exact', 'last bit' of a float with everything else identical, or different)."""
    sys.path.insert(0, str(D.HERE))
    from twin import bench3b as B3
    kinds: dict = {}
    by_exp = {}
    for name, K in B3.rerun_report().items():
        by_exp[name] = {k: len(v) for k, v in K.items()}
        for k, v in K.items():
            kinds[k] = kinds.get(k, 0) + len(v)
    tot = sum(kinds.values())
    exact, last = kinds.get("exact", 0), kinds.get("last bit", 0)
    return dict(rerun=tot, identical=exact, last_bit=last, different=tot - exact - last, by_experiment=by_exp,
                src="twin.bench3b.rerun_report(): out/twin3b/runs/re_*.jsonl against round 3's committed rows "
                    "(notes/twin_round3b.md 1.4)")


def _replay() -> dict:
    """The two parts of the replay (data.replay3b_parts: like3b.json median_seeds for the replay arm), each run's own
    days to the targets (round 3's committed rows), and where the cut changes from one to the other."""
    parts = D.replay3b_parts()
    fac, stock, pol = D.REPLAY_ARM3B.split("|")
    T = dict(T1=D.target(), T2=D.targets2())
    out = dict(arm=D.REPLAY_ARM3B, policy=pol, facility=fac, stock=stock, n=parts[0]["of"], parts=[],
               src="out/twin3b/like3b.json median_seeds (notes/twin_round3b.md section 3); each run's days from "
                   "out/twin3/runs/main.jsonl; the logs in out/twin3b/events")
    runs = []
    for q in parts:
        R = D.Replay(q["events"])
        runs.append(R)
        row = D.run_row(R.facility, R.policy, R.seed)
        days = {c: {tn: D.hit_day(row["campaigns"][c]["curve_new"], T[tn][c]) for tn in ("T1", "T2")}
                for c in D.CAMPAIGNS}
        at = int(np.sum(R.station == "atomizer"))
        arm = _arm(fac, stock, pol)
        out["parts"].append(dict(
            seed=q["seed"], campaign=q["campaign"], target=q["target"], day=float(q["day"]), hit=q["hit"],
            of=q["of"], file=str(q["events"].relative_to(D.HERE)), run=R.path.name, days=days,
            best={c: float(row["campaigns"][c]["best_new"]) for c in D.CAMPAIGNS},
            arm_hits={c: {tn: arm[c][tn]["hit"] for tn in ("T1", "T2")} for c in D.CAMPAIGNS},
            arm_median={c: {tn: arm[c][tn]["day"] for tn in ("T1", "T2")} for c in D.CAMPAIGNS},
            bookings=len(R.ev), atomizer_runs=at, atomizer_runs_week=at / (R.horizon_days / 7.0)))
    out["a"], out["b"] = out["parts"]                  # by name too (the script's paths: replay.a.day)
    out["atomizer_runs_week"] = float(np.mean([q["atomizer_runs_week"] for q in out["parts"]]))
    # where the cut changes run (the timeline's own switch: compose.Timeline.switch_h), as the clock shows it
    try:
        from . import compose as C
        sh = float(C.S("tl").switch_h)
        out["switch_h"] = sh
        out["switch_day"] = int(sh // 24) + 1
        a, b = runs
        at_sw = {k: {c: R.best_at(c, sh) for c in D.CAMPAIGNS} for k, R in (("a", a), ("b", b))}
        out["best_at_switch"] = at_sw
        b_al2 = out["parts"][1]["days"][AL]["T2"]
        words = (f"aluminium past both targets since day {b_al2:.0f}" if (b_al2 is not None and b_al2 * 24 < sh)
                 else f"aluminium's best new alloy at {at_sw['b'][AL]:.2f}")
        words += ("; no new copper alloy scored yet" if at_sw["b"][CU] <= 0 else
                  f"; copper's best new alloy at {at_sw['b'][CU]:.2f}")
        out["b_so_far"] = words
    except Exception as e:                              # noqa: BLE001  (no timeline: the numbers without the cut)
        out["switch_error"] = str(e)
    return out


def numbers() -> dict:
    if _N:
        return _N
    out = dict(N3.numbers())                            # round 3's, as its cut reads them
    L = like3b()
    out["like_src"] = "out/twin3b/like3b.json (twin.like3b; printed as out/twin3b/tables.md)"
    # ------------------------------------------------------------------------------ the lab against a conventional lab
    lab: dict = {}
    for pair in PAIRS:
        lab[pair] = {
            AL: dict(T1=dict(same_heur=_cmp(HEUR, HEUR, pair, AL, "T1"), bofn_thumb=_cmp(BOFN, HEUR, pair, AL, "T1"),
                             pkgfn_thumb=_cmp(PKGFN, HEUR, pair, AL, "T1"), bofn_same=_cmp(BOFN, BOFN, pair, AL, "T1"),
                             pkgfn_same=_cmp(PKGFN, PKGFN, pair, AL, "T1")),
                     T2=dict(same_heur=_cmp(HEUR, HEUR, pair, AL, "T2"), bofn_thumb=_cmp(BOFN, HEUR, pair, AL, "T2"),
                             pkgfn_thumb=_cmp(PKGFN, HEUR, pair, AL, "T2"), bofn_same=_cmp(BOFN, BOFN, pair, AL, "T2"),
                             pkgfn_same=_cmp(PKGFN, PKGFN, pair, AL, "T2"))),
            CU: dict(T1=dict(same_funnel=_cmp(FUNNEL, FUNNEL, pair, CU, "T1"),
                             bofn_same=_cmp(BOFN, BOFN, pair, CU, "T1"), pkgfn_same=_cmp(PKGFN, PKGFN, pair, CU, "T1"),
                             bofn_thumb=_cmp(BOFN, HEUR, pair, CU, "T1"), pkgfn_thumb=_cmp(PKGFN, HEUR, pair, CU, "T1")),
                     T2=dict(same_funnel=_cmp(FUNNEL, FUNNEL, pair, CU, "T2"),
                             bofn_same=_cmp(BOFN, BOFN, pair, CU, "T2"), pkgfn_same=_cmp(PKGFN, PKGFN, pair, CU, "T2"),
                             bofn_thumb=_cmp(BOFN, HEUR, pair, CU, "T2"), pkgfn_thumb=_cmp(PKGFN, HEUR, pair, CU, "T2"))),
        }
    out["lab"] = lab
    # ------------------------------------------------------------------------------------------ what the stock buys
    out["stock"] = {fac: {p: {c: {tn: _stock(fac, p, c, tn) for tn in ("T1", "T2")} for c in D.CAMPAIGNS}
                          for p in (HEUR, FUNNEL, BOFN, PKGFN)} for fac in ("vertical_lab", "proposed")}
    # ------------------------------------------------------------------------------------------- each arm on its own
    out["arms"] = {f"{fac}|{st}|{p}": _arm(fac, st, p) for fac in ("vertical_lab", "proposed")
                   for st in ("stocked", "lean") for p in (HEUR, FUNNEL, BOFN, PKGFN)}
    out["reruns"] = _reruns()
    out["replay"] = dict(_replay(), helpers_busy=out["replay"].get("helpers_busy"))
    out["targets3b"] = L["targets"]
    out["missing3b"] = [
        "round 3's economics (fixed costs, cost per alloy with the equipment) were not redone for round 3b's arms: "
        "the cost shown is campaign spend to the target, which leaves fixed costs out",
        "BOFN and pKGFN in the conventional lab have 4 seeds (three simulated years each)",
        "BOFN and pKGFN in round 3's copper tests (cu_money, cu_hidden_net) were not rerun under the pin"]
    _N.update(out)
    return _N


def claims() -> list:
    """What round 3b's cards and narration say in words, each checked against the numbers: (claim, holds)."""
    n = numbers()
    M, cm = n["main"], n["cu_money"]
    like, r3, st = n["lab"]["like"], n["lab"]["round3"], n["stock"]["vertical_lab"]
    rep = n["replay"]
    a, b = rep["parts"]
    best = lambda c: sorted(M, key=lambda p: -M[p][c]["best"])
    bt, pt = like[AL]["T2"]["bofn_thumb"]["days"], like[AL]["T2"]["pkgfn_thumb"]["days"]
    cf = like[CU]["T2"]["same_funnel"]["days"]
    bs, ps = like[AL]["T2"]["bofn_same"]["days"], like[AL]["T2"]["pkgfn_same"]["days"]
    sb, sp = st[BOFN][AL]["T2"]["days"], st[PKGFN][AL]["T2"]["days"]
    r3p = r3[AL]["T2"]["pkgfn_thumb"]["days"]
    ub, up, uf = (like[AL]["T2"]["bofn_thumb"]["usd"], like[AL]["T2"]["pkgfn_thumb"]["usd"],
                  like[CU]["T2"]["same_funnel"]["usd"])
    rr = n["reruns"]
    out = [
        # ---- round 3's policy results, which this cut keeps
        ("aluminium: time-aware BOFN and pKGFN finished highest", set(best(AL)[:2]) == {BOFN, PKGFN}),
        ("copper: tiered screening finished ahead of every other policy", best(CU)[0] == FUNNEL),
        ("aluminium's halfway target: BOFN per dollar in 7 runs, no other policy in more than 2",
         M["bofn3_usd"][AL]["T2"]["hit"] == 7 and n["al_T2_others_max"] == 2),
        ("the heuristic reaches aluminium's first target soonest, then stalls (1 of 12 at the halfway target)",
         min((p for p in M if M[p][AL]["T1"]["day"] is not None), key=lambda p: M[p][AL]["T1"]["day"]) == HEUR
         and M[HEUR][AL]["T2"]["hit"] == 1),
        ("more than four fifths of each campaign's spending is orders",
         all(0.8 < n["orders_share"][c] < 0.9 for c in (AL, CU))),
        ("three times the money: BOFN and pKGFN draw level with tiered screening, which is still first to both "
         "targets", all(abs(cm[p]["funnel"]["mean"]) < 0.05 for p in (BOFN, PKGFN))
         and all(cm[FUNNEL][t]["day"] < cm[p][t]["day"] for p in (BOFN, PKGFN) for t in ("T1", "T2"))),
        # ---- like for like
        ("like for like, aluminium's halfway target: BOFN and pKGFN both 1.8x against the rule of thumb, 11 of 12 "
         "seeds against 6 of 12, a lower bound",
         all(round(x["af"], 1) == 1.8 and x["hit_new"] == 11 and x["hit_ref"] == 6 and x["n"] == 12
             and x["kind"] == "at_least" for x in (bt, pt))),
        ("like for like, aluminium's halfway target: day 183 against day 337 for both",
         all(round(x["m_new"]) == 183 and round(x["m_ref"]) == 337 for x in (bt, pt))),
        ("like for like, copper's halfway target, the funnel in both labs: 3.2x (1.9 to 4.8), a factor with both "
         "medians", cf["kind"] == "factor" and round(cf["af"], 1) == 3.2 and round(cf["lo"], 1) == 1.9
         and round(cf["hi"], 1) == 4.8),
        ("the first targets like for like are factors with both medians (heuristic 2.4x, funnel 2.5x)",
         round(like[AL]["T1"]["same_heur"]["days"]["af"], 1) == 2.4
         and round(like[CU]["T1"]["same_funnel"]["days"]["af"], 1) == 2.5
         and like[AL]["T1"]["same_heur"]["days"]["kind"] == like[CU]["T1"]["same_funnel"]["days"]["kind"] == "factor"),
        # ---- the stock
        ("the stock buys BOFN and pKGFN 1.9x and 2.2x in the automated lab (aluminium's halfway target)",
         round(sb["af"], 1) == 1.9 and round(sp["af"], 1) == 2.2 and sb["kind"] == sp["kind"] == "factor"),
        ("stocked, pKGFN reaches aluminium's halfway target on day 83 and BOFN on day 96 (ordering as they go: 183)",
         round(sp["m_new"]) == 83 and round(sb["m_new"]) == 96 and round(sp["m_ref"]) == round(sb["m_ref"]) == 183),
        ("round 3's 4.0x (pKGFN, stocked against ordering as it goes) is the lab's 1.8x times the stock's 2.2x",
         round(r3p["af"], 1) == 4.0 and abs(r3p["af"] - pt["af"] * sp["af"]) < 1e-6),
        ("round 3's pairing gives 3.8x for copper's halfway target (the funnel) and 3.5x for BOFN on aluminium's",
         round(r3[CU]["T2"]["same_funnel"]["days"]["af"], 1) == 3.8
         and round(r3[AL]["T2"]["bofn_thumb"]["days"]["af"], 1) == 3.5),
        ("the stock does little for copper's funnel (1.2x to either target in the automated lab)",
         all(round(st[FUNNEL][CU][t]["days"]["af"], 1) == 1.2 for t in ("T1", "T2"))),
        # ---- where it doesn't win
        ("the same optimizer in both labs, both ordering as they go: about a tie on aluminium's halfway target "
         "(0.9x and 1.0x, 4 seeds)", round(bs["af"], 1) == 0.9 and round(ps["af"], 1) == 1.0
         and bs["n"] == ps["n"] == 4 and bs["kind"] == ps["kind"] == "factor"),
        ("those ties' intervals include 1.0", all(x["lo"] < 1.0 < x["hi"] for x in (bs, ps))),
        ("the same optimizer, copper's best existing alloy: the conventional lab got there in more of the 4 seeds",
         all(like[CU]["T1"][k]["days"]["hit_ref"] > like[CU]["T1"][k]["days"]["hit_new"]
             for k in ("bofn_same", "pkgfn_same"))),
        ("the stocked conventional heuristic reaches aluminium's first target (day 46) sooner than the automated "
         "lab ordering as it goes with any policy",
         all(n["arms"]["proposed|stocked|heuristic"][AL]["T1"]["day"] < n["arms"][f"vertical_lab|lean|{p}"][AL]["T1"]["day"]
             for p in (HEUR, FUNNEL, BOFN, PKGFN))),
        # ---- cost, campaign spend
        ("campaign spend like for like: at least 2.2x (BOFN) and 2.3x (pKGFN) less to aluminium's halfway target, "
         "3.2x less to copper's with the funnel",
         round(ub["af"], 1) == 2.2 and round(up["af"], 1) == 2.3 and ub["kind"] == up["kind"] == "at_least"
         and round(uf["af"], 1) == 3.2 and uf["kind"] == "factor"),
        ("campaign spend, the same optimizer, both ordering as they go: intervals include 1.0 on aluminium's halfway "
         "target, and no saving on copper's first target",
         all(like[AL]["T2"][k]["usd"]["lo"] < 1.0 < like[AL]["T2"][k]["usd"]["hi"] for k in ("bofn_same", "pkgfn_same"))
         and all(like[CU]["T1"][k]["usd"]["af"] <= 1.0 for k in ("bofn_same", "pkgfn_same"))),
        ("round 3 put the automated lab's fixed costs above the conventional lab's ($1.18M against $0.12M a year)",
         round(n["cost"]["fixed_year"]["vertical"] / 1e6, 2) == 1.18
         and round(n["cost"]["fixed_year"]["conventional"] / 1e6, 2) == 0.12),
        # ---- the replay
        ("the replay's two runs are the replay arm's median seeds as like3b.json names them: seed 0 for aluminium's "
         "halfway target (day 96), seed 5 for copper's best existing alloy (day 221)",
         (a["seed"], a["campaign"], a["target"], round(a["day"])) == (0, AL, "T2", 96)
         and (b["seed"], b["campaign"], b["target"], round(b["day"])) == (5, CU, "T1", 221)),
        ("each is its arm's Kaplan-Meier median day, and its own run's day",
         abs(a["day"] - a["arm_median"][AL]["T2"]) < 0.01 and abs(b["day"] - b["arm_median"][CU]["T1"]) < 0.01
         and abs(a["day"] - a["days"][AL]["T2"]) < 0.01 and abs(b["day"] - b["days"][CU]["T1"]) < 0.01),
        ("both logs are committed in out/twin3b/events",
         all((D.HERE / q["file"]).exists() and q["file"].startswith("out/twin3b/events/") for q in (a, b))),
        ("the cut changes run after the first seed's aluminium passed both targets and before the second seed's "
         "copper reaches its first", "switch_h" in rep and a["days"][AL]["T2"] * 24 < rep["switch_h"] <
         b["days"][CU]["T1"] * 24),
        ("at the switch the second seed's aluminium is also past both targets, and neither seed has a new copper "
         "alloy at its first target", "switch_h" in rep and b["days"][AL]["T2"] * 24 < rep["switch_h"]
         and all(rep["best_at_switch"][k][CU] < n["targets"]["T1"][CU] for k in ("a", "b"))),
        ("the atomizer is used about 10 times a week in both replayed runs",
         all(round(q["atomizer_runs_week"]) == 10 for q in (a, b))),
        # ---- the reruns
        ("round 3's committed rows rerun under the pin: 348, of which 338 identical, 10 to the last bit, 0 different",
         (rr["rerun"], rr["identical"], rr["last_bit"], rr["different"]) == (348, 338, 10, 0)),
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
            return "inf" if math.isinf(o) else (None if math.isnan(o) else round(o, 4))
        if isinstance(o, (np.floating, np.integer)):
            return clean(o.item())
        return o
    (D.VID / "numbers.json").write_text(json.dumps(clean(n), indent=1) + "\n")
    return n


# ------------------------------------------------------------------------------------------------- words
x1 = N3.x1


def rng(lo, hi) -> str:
    """'1.9 to 4.8', '0 to 2.5', '1.3 to unbounded': an interval as tables.md prints it (0 for 0.0, unbounded for ∞)."""
    def f(v):
        if v is None or not math.isfinite(v):
            return "unbounded"
        return "0" if v == 0 else f"{v:.1f}"
    return f"{f(lo)} to {f(hi)}"


def big(c: dict, less: bool = False) -> str:
    """'at least 1.8x', '3.2x', 'at most 1.3x', 'no factor' for a cell."""
    if c["kind"] == "none":
        return "no factor"
    return {"at_least": "at least ", "at_most": "at most "}.get(c["kind"], "") + x1(c["af"])


def counts(c: dict) -> str:
    return f"{c['hit_new']} of {c['n']} against {c['hit_ref']} of {c['n']}"


if __name__ == "__main__":
    n = write()
    for pair in PAIRS:
        print(pair, "-", PAIR_WORDS[pair])
        for c in (AL, CU):
            for tn in ("T1", "T2"):
                for k, v in n["lab"][pair][c][tn].items():
                    d, u = v["days"], v["usd"]
                    print(f"   {c:9s} {tn} {k:12s} days {big(d):14s} ({rng(d['lo'], d['hi'])}) {counts(d):22s} "
                          f"medians {d['m_new']} vs {d['m_ref']}; first {d['first_new']}-{d['first_ref']} | "
                          f"usd {big(u):14s} ({rng(u['lo'], u['hi'])}) {u['m_new']} vs {u['m_ref']}")
    print("stock (vertical lab)")
    for p in (HEUR, FUNNEL, BOFN, PKGFN):
        for c in (AL, CU):
            for tn in ("T1", "T2"):
                v = n["stock"]["vertical_lab"][p][c][tn]
                d = v["days"]
                print(f"   {p:10s} {c:9s} {tn} {big(d):14s} ({rng(d['lo'], d['hi'])}) stocked {d['hit_new']}/{d['n']} "
                      f"day {d['m_new']} vs lean {d['hit_ref']}/{d['n']} day {d['m_ref']}; best diff {v['best_diff']}")
    print("reruns", n["reruns"])
    print("replay", json.dumps(n["replay"], default=str)[:2400])
    bad = 0
    for c, ok in claims():
        print("ok " if ok else "BAD", c)
        bad += not ok
    sys.exit(1 if bad else 0)

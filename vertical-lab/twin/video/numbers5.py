"""Every number the lab-comparison chapter and the takeaway of the two-year cut show or speak (twin/video/figs5_labs.py),
read from the round's committed files, with where each came from.

    TWIN_VIDEO_ROUND=5 python -m twin.video.numbers5     # -> out/twin5/video/numbers.json, and prints its claims

The round is the one switch (twin/video/data.py: ROUND, RES = out/twin<ROUND>). What is read:

  out/twin<R>/like<R>.json   twin.like<R>: what out/twin<R>/tables.md prints. `four_way`: the conventional lab's
                             Kaplan-Meier median over the automated lab's, in days and in campaign spend, for the same
                             policy in both labs, to both targets, in the four pairings of stocked and ordering as it
                             goes; `arms`: each arm's days, final alloys, median seed and when 90 % of its money was
                             spent; `policy_effect`; `economics`; `used` (when the in-house stations came online)
  out/twin<R>/runs/          the rows themselves (twin.like<R>.load_all), for each run's own spending over time
                             (`campaigns.<c>.spend_curve`), which like<R>.json doesn't keep

Nothing is fitted, re-simulated or typed in. The words used on screen for the four pairings:
  lean      both labs ordering metal as they go            (like5: vertical lean, conventional lean)
  stocked   both labs stocked by the reorder rule          (reorder, reorder)
  round3    the automated lab stocked, the conventional lab ordering as it goes: round 3's pairing (reorder, lean)
  rev       the automated lab ordering as it goes, the conventional lab stocked (lean, reorder)

Top-level keys (the intro cards' numbers are another module's, under `intro`): labs, nowin, win, money, econ, take,
replay, src. `claims()` checks every worded statement the cards and the lines make against these numbers, so a later
round that changes an outcome fails loudly instead of saying something false.
"""
from __future__ import annotations

import importlib
import json
import math
import sys

import numpy as np

from . import data as D

AL, CU = "flaime_al", "onr_cu"
CAMPS = (AL, CU)
POLS = ("fast", "bofn3", "pkgfn3")                  # the cheap policy (heuristic on aluminium, funnel on copper), then
OPTS = ("bofn3", "pkgfn3")                          # the two optimizers
PAIRS = {"lean": ("lean", "lean"), "stocked": ("reorder", "reorder"), "round3": ("reorder", "lean"),
         "rev": ("lean", "reorder")}                # (automated lab, conventional lab)
PAIR_WORDS = {"lean": "both labs ordering metal as they go", "stocked": "both labs stocked",
              "round3": "the automated lab stocked, the conventional lab ordering as it goes (round 3's pairing)",
              "rev": "the automated lab ordering as it goes, the conventional lab stocked"}
LABS = {"vertical": "parallel", "conventional": "external"}     # each lab's plan in the like-for-like arms
REPLAY = ("bofn3", "reorder")                       # the replayed arm: time-aware BOFN, stocked (cut5's replay)
SPENT_SHARE = 0.9                                   # like<R>.money_out: the day 90 % of a campaign's money was spent
_N: dict = {}
_L: dict = {}


def LK():
    """The round's analysis module (twin/like5.py for round 5)."""
    sys.path.insert(0, str(D.HERE))
    return importlib.import_module(f"twin.like{D.ROUND}")


def like() -> dict:
    if not _L:
        _L.update(json.loads((D.RES / f"like{D.ROUND}.json").read_text()))
    return _L


def _f(v):
    """like<R>.json's numbers: null, Infinity and NaN as they come out of json."""
    if v is None:
        return None
    if isinstance(v, str):
        return float("inf") if "inf" in v.lower() else float("nan")
    return float(v)


def cell(x: dict | None, money: bool = False) -> dict | None:
    """One factor of like<R>.json as the cards show it, in the tables' own terms.

    kind: 'factor' (an estimate with its 95 % paired interval); 'at_least' (fewer than half the conventional lab's
    seeds got there, so it has no median: tables.md's '>=', a lower bound); 'at_most' (the same for the automated lab:
    tables.md's '<='); 'none'. new = the automated lab's arm, ref = the conventional lab's. `printed` is the cell as
    tables.md prints it (twin.like<R>._f), `half` whether the conventional lab got there in half its seeds or fewer
    (its median is then its last seed to get there, or missing)."""
    if x is None:
        return None
    n, hn, hr = int(x["n"]), int(x["hit_vert"]), int(x["hit_conv"])
    f, lo, hi = _f(x["factor"]), _f(x["lo"]), _f(x["hi"])
    b = x.get("bound")
    out = dict(n=n, hit_new=hn, hit_ref=hr, lo=lo, hi=hi, m_new=_f(x["median_vert"]), m_ref=_f(x["median_conv"]),
               first_new=int(x["v_first"]), first_ref=int(x["c_first"]), half=bool(2 * hr <= n),
               printed=LK()._f(dict(x, factor=f, lo=lo, hi=hi), money))
    if b is not None:
        out.update(kind="at_least" if b[0] == "lower" else "at_most", af=float(b[1]))
    elif f is None or math.isnan(f):
        out.update(kind="none", af=None)
    else:
        out.update(kind="factor", af=f)
    return out


def _four(camp: str, tn: str, pol: str) -> dict:
    for r in like()["four_way"]:
        if (r["camp"], r["target"], r["vert"], r["conv"]) == (camp, tn, pol, pol):
            return r
    raise KeyError((camp, tn, pol))


def _arm(lab: str, pol: str, st: str) -> dict:
    """One like-for-like arm: seeds there, the Kaplan-Meier median day and the final alloy per campaign; when 90 % of
    each campaign's money was spent (median day over seeds; 730 where fewer than half ever did)."""
    key = LK().gk(lab, LABS[lab], pol, st)
    a = like()["arms"][key]
    out = dict(key=key, n=int(a["n"]))
    for c in CAMPS:
        s1, s2 = a["stats"][f"{c}|T1"], a["stats"][f"{c}|T2"]
        mo = a["money"][c]
        out[c] = dict(T1=dict(hit=int(s1["hit"]), n=int(s1["n"]), day=_f(s1["median"])),
                      T2=dict(hit=int(s2["hit"]), n=int(s2["n"]), day=_f(s2["median"])),
                      best=float(s1["best_mean"]), best_se=float(s1["best_se"]), spent_mean=float(s1["spent_mean"]),
                      d90=_f(mo["median_d90"]), n_spent90=int(mo["n_spent90"]))
    return out


def _span(vals, nd: int = 1) -> dict:
    v = [round(float(x), nd) for x in vals if x is not None and math.isfinite(x)]
    return dict(lo=min(v), hi=max(v), n=len(v)) if v else dict(lo=None, hi=None, n=0)


def _ispan(vals) -> dict:
    v = [int(x) for x in vals]
    return dict(lo=min(v), hi=max(v))


def _traces(rows: dict, key: str, seed) -> dict:
    """Each campaign's cumulative spend against the day in one arm: the median over its seeds, the quartiles and the
    whole range, and the replayed seed's own trace (each run's `spend_curve`, its ledger at 7-day steps)."""
    arm = rows.get(key, {})
    out = {}
    for c in CAMPS:
        cur = {s: np.array(r["campaigns"][c].get("spend_curve") or [[0.0, 0.0]], float) for s, r in arm.items()}
        if not cur:
            continue
        days = sorted({float(d) for v in cur.values() for d in v[:, 0]})
        M = np.array([np.interp(days, v[:, 0], v[:, 1]) for _, v in sorted(cur.items())])
        bud = [arm[s]["campaigns"][c].get("budget") for s in arm]
        bud = [float(b) for b in bud if b is not None and math.isfinite(float(b)) and float(b) < 1e9]
        out[c] = dict(days=days, median=np.median(M, 0).tolist(), q25=np.percentile(M, 25, 0).tolist(),
                      q75=np.percentile(M, 75, 0).tolist(), lo=M.min(0).tolist(), hi=M.max(0).tolist(),
                      seed=(np.interp(days, cur[seed][:, 0], cur[seed][:, 1]).tolist() if seed in cur else None),
                      n=len(cur), end_median=float(np.median(M[:, -1])), end_lo=float(M[:, -1].min()),
                      end_hi=float(M[:, -1].max()), budget=(float(np.median(bud)) if bud else None))
    return out


def _first_routes(rows: dict, key: str, T: dict) -> dict:
    """Where each seed's first new alloy past a target was printed or deposited: in house (a station of the automated
    lab, `...@vcl` in the rows) or at a partner (`campaigns.<c>.demonstrated[].route_fab`)."""
    arm = rows.get(key, {})
    out = {}
    for c in CAMPS:
        out[c] = {}
        for tn in ("T1", "T2"):
            cnt = dict(inhouse=0, partner=0, none=0, of=len(arm), routes={})
            for r in arm.values():
                hit = next((x for x in sorted(r["campaigns"][c].get("demonstrated") or [], key=lambda x: x["t_h"])
                            if not x.get("ref") and x["u"] >= T[tn][c]), None)
                if hit is None:
                    cnt["none"] += 1
                    continue
                rt = str(hit.get("route_fab"))
                cnt["routes"][rt] = cnt["routes"].get(rt, 0) + 1
                cnt["inhouse" if rt.endswith("@vcl") else "partner"] += 1
            out[c][tn] = cnt
    return out


def numbers() -> dict:
    if _N:
        return _N
    L = like()
    T = L["targets"]
    out: dict = dict(src=dict(
        like=f"out/twin{D.ROUND}/like{D.ROUND}.json (twin.like{D.ROUND}; printed as out/twin{D.ROUND}/tables.md)",
        rows=f"out/twin{D.ROUND}/runs (twin.like{D.ROUND}.load_all): each run's spend_curve"))
    # ---------------------------------------------------------------------------------------------- like for like
    days = {c: {tn: {p: {pair: cell(_four(c, tn, p)["cells"].get(f"{sv}|{sc}")) for pair, (sv, sc) in PAIRS.items()}
                     for p in POLS} for tn in ("T1", "T2")} for c in CAMPS}
    usd = {c: {tn: {p: {pair: cell(_four(c, tn, p)["money"].get(f"{sv}|{sc}"), True)
                        for pair, (sv, sc) in PAIRS.items() if f"{sv}|{sc}" in _four(c, tn, p)["money"]}
                    for p in POLS} for tn in ("T1", "T2")} for c in CAMPS}
    names = {p: {c: _four(c, "T1", p)["vert_name"] for c in CAMPS} for p in POLS}
    arms = {f"{lab}|{p}|{st}": _arm(lab, p, st) for lab in LABS for p in POLS for st in ("reorder", "lean")}
    n_seeds = sorted({a["n"] for a in arms.values()})
    both = ("lean", "stocked")
    al1h = [days[AL]["T1"]["fast"][q] for q in both]
    al1o = [days[AL]["T1"][p][q] for p in OPTS for q in both]
    al2h = [days[AL]["T2"]["fast"][q] for q in both]
    al2o = [days[AL]["T2"][p][q] for p in OPTS for q in both]
    cuf = [days[CU][tn]["fast"][q] for tn in ("T1", "T2") for q in both]
    cuo = [days[CU][tn][p][q] for tn in ("T1", "T2") for p in OPTS for q in both]
    out["labs"] = dict(
        n_seeds=n_seeds[0] if len(n_seeds) == 1 else n_seeds, targets=T, names=names, days=days, usd=usd, arms=arms,
        sum=dict(
            al_T1_heur=dict(af=_span(c["af"] for c in al1h), ci_lo=min(c["lo"] for c in al1h),
                            ci_hi=max(c["hi"] for c in al1h)),
            al_T1_opt=dict(af=_span(c["af"] for c in al1o), ci_lo=_span((c["lo"] for c in al1o), 2),
                           ci_hi=_span((c["hi"] for c in al1o), 2), cells=len(al1o),
                           first_new=_ispan(c["first_new"] for c in al1o)),
            al_T2_heur=dict(hit_new=_ispan(c["hit_new"] for c in al2h), hit_ref=_ispan(c["hit_ref"] for c in al2h),
                            hits=_ispan([c["hit_new"] for c in al2h] + [c["hit_ref"] for c in al2h]),
                            lean=al2h[0], stocked=al2h[1]),
            al_T2_opt=dict(af=_span(c["af"] for c in al2o), hit_new=_ispan(c["hit_new"] for c in al2o),
                           hit_ref=_ispan(c["hit_ref"] for c in al2o),
                           first_new=_ispan(c["first_new"] for c in al2o),
                           ci_lo_lean=_span((days[AL]["T2"][p]["lean"]["lo"] for p in OPTS), 2),
                           ci_lo_stocked=_span((days[AL]["T2"][p]["stocked"]["lo"] for p in OPTS), 2)),
            cu_funnel=dict(af=_span(c["af"] for c in cuf), first_new=_ispan(c["first_new"] for c in cuf),
                           hit_new=_ispan(c["hit_new"] for c in cuf), hit_ref=_ispan(c["hit_ref"] for c in cuf),
                           ci_lo=_span((c["lo"] for c in cuf), 2)),
            cu_opt=dict(af=_span(c["af"] for c in cuo),
                        T1=dict(hit_new=_ispan(days[CU]["T1"][p][q]["hit_new"] for p in OPTS for q in both),
                                hit_ref=_ispan(days[CU]["T1"][p][q]["hit_ref"] for p in OPTS for q in both)),
                        T2=dict(hit_new=_ispan(days[CU]["T2"][p][q]["hit_new"] for p in OPTS for q in both),
                                hit_ref=_ispan(days[CU]["T2"][p][q]["hit_ref"] for p in OPTS for q in both)),
                        first_new=_ispan(c["first_new"] for c in cuo))))
    # ------------------------------------------------------------------------------ where the automated lab doesn't win
    pe = {(x["lab"], x["stock"], x["policy"], x["camp"], x["target"]): cell(x["r"]) for x in L.get("policy_effect", [])}
    day1 = lambda lab, pols: _span(arms[f"{lab}|{p}|{st}"][AL]["T1"]["day"] for p in pols for st in ("reorder", "lean"))
    hit2 = lambda pols: _ispan(arms[f"{lab}|{p}|{st}"][AL]["T2"]["hit"] for lab in LABS for p in pols
                               for st in ("reorder", "lean"))
    rev1 = [days[AL]["T1"][p]["rev"] for p in POLS]
    rev_all = [days[AL][tn][p]["rev"] for tn in ("T1", "T2") for p in OPTS]
    usd_st = [usd[AL][tn][p]["stocked"] for tn, p in (("T1", "fast"), ("T1", "bofn3"), ("T1", "pkgfn3"),
                                                     ("T2", "bofn3"), ("T2", "pkgfn3"))]
    usd_lean_opt = [usd[AL][tn][p]["lean"] for tn in ("T1", "T2") for p in OPTS]
    usd_cu = [usd[CU][tn]["fast"][q] for tn in ("T1", "T2") for q in both]
    online = L.get("used", {}).get("online_median_d", {})
    out["nowin"] = dict(
        policy=dict(auto_opt=day1("vertical", OPTS), auto_heur=day1("vertical", ("fast",)),
                    conv_opt=day1("conventional", OPTS), conv_heur=day1("conventional", ("fast",)),
                    factor={f"{lab}|{st}|{p}": pe.get((lab, st, p, AL, "T1")) for lab in LABS
                            for st in ("reorder", "lean") for p in OPTS},
                    al_T2_hits_opt=hit2(OPTS), al_T2_hits_heur=hit2(("fast",))),
        rev=dict(al_T1=_span(c["af"] for c in rev1), cells={p: days[AL]["T1"][p]["rev"] for p in POLS},
                 round3=_span(days[AL]["T1"][p]["round3"]["af"] for p in POLS),
                 opt=_span(c["af"] for c in rev_all), opt_first_ref=_ispan(c["first_ref"] for c in rev_all)),
        usd=dict(al_stocked=_span(c["af"] for c in usd_st), al_lean_opt=_span(c["af"] for c in usd_lean_opt),
                 al_lean_opt_more=_span(1.0 / c["af"] for c in usd_lean_opt),
                 cu_funnel=_span(c["af"] for c in usd_cu), cu_funnel_more_pct=_span(
                     (100.0 * (1.0 / c["af"] - 1.0) for c in usd_cu if c["kind"] == "factor"), 0)),
        online=dict(midi=_f(online.get("utah_midi@vcl")), mxlab=_f(online.get("utah_mxlab@vcl")),
                    cell=float(np.median(L["used"]["cell_d"])) if L.get("used", {}).get("cell_d") else None))
    out["win"] = dict(cu_best=dict(auto=_span((arms[f"vertical|{p}|{st}"][CU]["best"] for p in POLS
                                               for st in ("reorder", "lean")), 2),
                                   conv=_span((arms[f"conventional|{p}|{st}"][CU]["best"] for p in POLS
                                               for st in ("reorder", "lean")), 2)))
    # ------------------------------------------------------------------------------------------------- economics
    E = L["economics"]
    ea = {}
    for k, v in E["arms"].items():
        ea[k] = {c: dict(total_2y=float(v[c]["total_2y_mean"]), alloys=float(v[c]["new_alloys_mean"]),
                         per_alloy=_f(v[c]["per_alloy_median"]), per_alloy_campaign=_f(
                             v[c]["per_alloy_campaign_only_median"]),
                         T1=dict(usd=_f(v[c]["T1"]["median"]), n=int(v[c]["T1"]["n"]), of=int(v[c]["T1"]["of"])),
                         T2=dict(usd=_f(v[c]["T2"]["median"]), n=int(v[c]["T2"]["n"]), of=int(v[c]["T2"]["of"])))
                 for c in CAMPS}
    pa = lambda lab, pols, c, f="per_alloy": _span((ea[f"{lab}|{p}|reorder"][c][f] / 1e3 for p in pols), 1)
    tt = lambda lab, c: _span((ea[f"{lab}|{p}|reorder"][c][tn]["usd"] / 1e6 for p in POLS for tn in ("T1", "T2")), 2)
    out["econ"] = dict(
        fixed_year={lab: dict(total=float(E["fixed_per_year"][lab]["total"]),
                              capex=float(E["fixed_per_year"][lab]["capex"])) for lab in LABS},
        arms=ea,
        sum=dict(al_opt=dict(auto=pa("vertical", OPTS, AL), conv=pa("conventional", OPTS, AL)),
                 cu_opt=dict(auto=pa("vertical", OPTS, CU), conv=pa("conventional", OPTS, CU)),
                 al_opt_campaign=dict(auto=pa("vertical", OPTS, AL, "per_alloy_campaign"),
                                      conv=pa("conventional", OPTS, AL, "per_alloy_campaign")),
                 to_target=dict(auto=_span((ea[f"vertical|{p}|reorder"][c][tn]["usd"] / 1e6 for p in POLS
                                            for c in CAMPS for tn in ("T1", "T2")), 1),
                                conv=_span((ea[f"conventional|{p}|reorder"][c][tn]["usd"] / 1e3 for p in POLS
                                            for c in CAMPS for tn in ("T1", "T2")), 0)),
                 ratio_al={p: ea[f"vertical|{p}|reorder"][AL]["per_alloy"] / ea[f"conventional|{p}|reorder"][AL]
                           ["per_alloy"] for p in POLS}))
    # ----------------------------------------------------------------------------------------------- the replay
    pol, st = REPLAY
    va, ca = arms[f"vertical|{pol}|{st}"], arms[f"conventional|{pol}|{st}"]
    ms = L["arms"][va["key"]].get("median_seed") or {}
    seed = ms.get("seed")
    out["replay"] = dict(policy=pol, stock=st, seed=seed, arm=va["key"], conv_arm=ca["key"], events=ms.get("events"),
                         days=ms.get("days"), medians=ms.get("medians"),
                         src=f"like{D.ROUND}.json arms.{va['key']}.median_seed (twin.like{D.ROUND}.median_seed)")
    # ------------------------------------------------------------------------------- money: spending against the day
    rows = LK().load_all()
    horizon = float(getattr(LK(), "HORIZON", 730.0))
    fr = {k: _first_routes(rows, a["key"], T) for k, a in arms.items()}
    out["win"]["first"] = fr
    out["win"]["cu_inhouse"] = _ispan(fr[f"vertical|{p}|{s_}"][CU]["T1"]["inhouse"] for p in POLS
                                      for s_ in ("reorder", "lean"))
    out["win"]["cu_got_there"] = _ispan(fr[f"vertical|{p}|{s_}"][CU]["T1"]["of"] - fr[f"vertical|{p}|{s_}"][CU]["T1"]
                                        ["none"] for p in POLS for s_ in ("reorder", "lean"))
    out["nowin"]["partner_al_T1"] = dict(
        auto=_ispan(fr[f"vertical|fast|{s_}"][AL]["T1"]["partner"] for s_ in ("reorder", "lean")),
        auto_stocked=fr["vertical|fast|reorder"][AL]["T1"], conv_stocked=fr["conventional|fast|reorder"][AL]["T1"])
    tr = {"auto": _traces(rows, va["key"], seed), "conv": _traces(rows, ca["key"], seed)}
    cheap = {"auto": arms[f"vertical|fast|{st}"], "conv": arms[f"conventional|fast|{st}"]}
    out["money"] = dict(
        horizon=horizon, share=SPENT_SHARE, share_pct=100.0 * SPENT_SHARE, traces=tr,
        d90={"auto": {c: dict(day=va[c]["d90"], n=va[c]["n_spent90"], of=va["n"]) for c in CAMPS},
             "conv": {c: dict(day=ca[c]["d90"], n=ca[c]["n_spent90"], of=ca["n"]) for c in CAMPS}},
        d90_cheap={k: {c: dict(day=a[c]["d90"], n=a[c]["n_spent90"], of=a["n"]) for c in CAMPS}
                   for k, a in cheap.items()},
        d90_opt=dict(auto={c: _span((arms[f"vertical|{p}|{s_}"][c]["d90"] for p in OPTS for s_ in ("reorder", "lean")),
                                    0) for c in CAMPS},
                     auto_all=_span((arms[f"vertical|{p}|{s_}"][c]["d90"] for p in OPTS for s_ in ("reorder", "lean")
                                     for c in CAMPS), 0),
                     auto_cheap=_span((arms[f"vertical|fast|{s_}"][c]["d90"] for s_ in ("reorder", "lean")
                                       for c in CAMPS), 0)),
        budget={c: tr["auto"].get(c, {}).get("budget") for c in CAMPS},
        end={k: {c: dict(median=v[c]["end_median"], lo=v[c]["end_lo"], hi=v[c]["end_hi"],
                         share=(v[c]["end_median"] / v[c]["budget"] if v[c].get("budget") else None))
                 for c in CAMPS if c in v} for k, v in tr.items()})
    # ------------------------------------------------------------------------------------------------- the takeaway
    out["take"] = dict(months=_span((va[c]["d90"] / (365.25 / 12.0) for c in CAMPS if va[c]["d90"]), 0),
                       src="the replayed arm's median day at which 90 % of each campaign's money was spent, in months")
    _N.update(out)
    return _N


# ------------------------------------------------------------------------------------------------------- claims
def claims_by_key() -> dict:
    """What the cards and the lines say in words, each checked against the numbers: {key: (claim, holds)}."""
    n = numbers()
    S, D_, A = n["labs"]["sum"], n["labs"]["days"], n["labs"]["arms"]
    N, M, E = n["nowin"], n["money"], n["econ"]
    ns = n["labs"]["n_seeds"]
    both = ("lean", "stocked")
    al1h = [D_[AL]["T1"]["fast"][q] for q in both]
    al1o = [D_[AL]["T1"][p][q] for p in OPTS for q in both]
    al2o = [D_[AL]["T2"][p][q] for p in OPTS for q in both]
    cuf = [D_[CU][tn]["fast"][q] for tn in ("T1", "T2") for q in both]
    cuo = [D_[CU][tn][p][q] for tn in ("T1", "T2") for p in OPTS for q in both]
    half = ns / 2.0 if isinstance(ns, (int, float)) else 8.0
    fin = lambda v: v is not None and math.isfinite(v)
    d90a, d90c = M["d90"]["auto"], M["d90"]["conv"]
    out = {
        "one_n": ("every like-for-like arm has the same number of seeds", isinstance(ns, int)),
        "al_T1_heur_tie": ("aluminium's best existing alloy with the heuristic is a tie: each factor an estimate "
                           "between 0.9x and 1.2x whose interval includes 1",
                           all(c["kind"] == "factor" and 0.9 <= round(c["af"], 1) <= 1.2 and c["lo"] < 1.0 < c["hi"]
                               for c in al1h)),
        "al_T1_opt_not_clear": ("with BOFN or pKGFN in both labs aluminium's best existing alloy comes sooner in the "
                                "automated lab by one factor (the four cells round to the same), and every interval "
                                "includes 1",
                                all(c["kind"] == "factor" and c["af"] > 1.0 and c["lo"] < 1.0 < c["hi"] for c in al1o)
                                and S["al_T1_opt"]["af"]["lo"] == S["al_T1_opt"]["af"]["hi"]),
        "al_T2_heur_half": ("with the heuristic, aluminium's halfway target is reached in about half the seeds in "
                            "either lab (within 2 of half, both pairings)",
                            all(abs(v - half) <= 2 for v in (S["al_T2_heur"]["hits"]["lo"],
                                                             S["al_T2_heur"]["hits"]["hi"]))),
        "al_T2_heur_no_lead": ("with the heuristic and both labs stocked, the automated lab reaches aluminium's "
                               "halfway target in no more seeds than the conventional lab",
                               S["al_T2_heur"]["stocked"]["hit_new"] <= S["al_T2_heur"]["stocked"]["hit_ref"]),
        "al_T2_opt_sooner": ("with BOFN or pKGFN in both labs aluminium's halfway target comes sooner in the automated "
                             "lab: four estimates above 1, the automated lab there in every seed and first in most",
                             all(c["kind"] == "factor" and c["af"] > 1.0 and c["hit_new"] == c["n"]
                                 and c["first_new"] > c["n"] / 2 for c in al2o)),
        "al_T2_opt_intervals": ("those intervals clear 1 with both labs ordering as they go, and include it with both "
                                "stocked",
                                all(D_[AL]["T2"][p]["lean"]["lo"] > 1.0 for p in OPTS)
                                and all(D_[AL]["T2"][p]["stocked"]["lo"] < 1.0 for p in OPTS)),
        "cu_funnel_sooner": ("copper with the funnel comes sooner in the automated lab in every pairing and to both "
                             "targets: estimates above 1 whose intervals stay above 1, first in most seeds",
                             all(c["kind"] == "factor" and c["af"] > 1.0 and c["lo"] > 1.0
                                 and c["first_new"] > c["n"] / 2 for c in cuf)),
        "cu_opt_at_least": ("copper with BOFN or pKGFN: every factor is a lower bound, or the conventional lab got "
                            "there in half its seeds or fewer, and each is at least 2.0x",
                            all((c["kind"] == "at_least" or (c["kind"] == "factor" and c["half"]))
                                and round(c["af"], 1) >= 2.0 for c in cuo)),
        "cu_opt_fewer_seeds": ("with BOFN or pKGFN the conventional lab reaches copper's first target in half its seeds "
                               "or fewer, the automated lab in nearly all",
                               S["cu_opt"]["T1"]["hit_ref"]["hi"] <= half and S["cu_opt"]["T1"]["hit_new"]["lo"] >= ns - 1),
        "cu_wins": ("copper: the automated lab is sooner with every policy, in both pairings, to both targets",
                    all(c["af"] is not None and c["af"] > 1.0 and c["kind"] in ("factor", "at_least")
                        for c in cuf + cuo)),
        "cu_best_higher": ("the automated lab's final copper alloys are at least as good in every arm",
                           n["win"]["cu_best"]["auto"]["lo"] >= n["win"]["cu_best"]["conv"]["hi"]),
        "opt_later_T1": ("in either lab BOFN and pKGFN reach aluminium's best existing alloy later than the heuristic",
                         N["policy"]["auto_opt"]["lo"] > N["policy"]["auto_heur"]["hi"]
                         and N["policy"]["conv_opt"]["lo"] > N["policy"]["conv_heur"]["hi"]),
        "policy_over_lab": ("for aluminium's halfway target the policy does more than the lab: BOFN and pKGFN reach "
                            "it in nearly every seed in either lab, the heuristic in about half",
                            N["policy"]["al_T2_hits_opt"]["lo"] >= ns - 1
                            and N["policy"]["al_T2_hits_heur"]["hi"] <= half + 2),
        "rev_keeps_up": ("a stocked conventional lab keeps up with an automated lab ordering as it goes on "
                         "aluminium's best existing alloy: every factor below 1",
                         all(c["kind"] == "factor" and c["af"] < 1.0 for c in N["rev"]["cells"].values())),
        "stock_decides_al_T1": ("on aluminium's best existing alloy the stock decides which lab is sooner: the "
                                "automated lab when it alone is stocked (every factor above 1), the conventional lab "
                                "when it alone is (every factor below 1)",
                                all(D_[AL]["T1"][p]["round3"]["kind"] == "factor" and D_[AL]["T1"][p]["round3"]["af"] > 1
                                    and D_[AL]["T1"][p]["rev"]["af"] < 1 for p in POLS)),
        "usd_no_lower": ("campaign money to aluminium's targets is no lower in the automated lab: with both stocked "
                         "every interval includes 1; with both ordering as they go and an optimizer it spends more",
                         all(c["kind"] == "factor" and c["lo"] < 1.0 < c["hi"]
                             for c in [n["labs"]["usd"][AL][tn][p]["stocked"] for tn, p in
                                       (("T1", "fast"), ("T1", "bofn3"), ("T1", "pkgfn3"), ("T2", "bofn3"),
                                        ("T2", "pkgfn3"))])
                         and N["usd"]["al_lean_opt"]["hi"] < 1.0),
        "usd_cu_more": ("to copper's targets with the funnel the automated lab spends more campaign money (every "
                        "estimate below 1)", N["usd"]["cu_funnel"]["hi"] < 1.0),
        "per_alloy_dearer": ("per aluminium alloy with fixed costs the automated lab is dearer with every policy, and "
                             "about twice as dear with an optimizer",
                             all(v > 1.0 for v in E["sum"]["ratio_al"].values())
                             and all(1.7 <= E["sum"]["ratio_al"][p] <= 2.6 for p in OPTS)),
        "per_alloy_campaign_cheaper": ("on campaign money alone an aluminium alloy costs less in the automated lab "
                                       "with an optimizer",
                                       E["sum"]["al_opt_campaign"]["auto"]["hi"] < E["sum"]["al_opt_campaign"]["conv"]["lo"]),
        "fixed_higher": ("the automated lab's fixed costs a year are several times the conventional lab's",
                         E["fixed_year"]["vertical"]["total"] > 5 * E["fixed_year"]["conventional"]["total"]),
        "to_target_dearer": ("to each target with its equipment the automated lab has committed more than the "
                             "conventional lab", E["sum"]["to_target"]["auto"]["lo"] * 1e6
                             > E["sum"]["to_target"]["conv"]["hi"] * 1e3),
        "money_limit": ("each campaign has a fixed amount of money for the two years (the rows carry a budget)",
                        all(fin(M["budget"][c]) for c in CAMPS)),
        "money_runs_out": ("the automated lab spends 90 % of both campaigns' two-year money in every seed of the "
                           "replayed arm, well before the end (median day under three quarters of the horizon)",
                           all(fin(M["budget"][c]) and d90a[c]["n"] == d90a[c]["of"]
                               and fin(d90a[c]["day"]) and d90a[c]["day"] < 0.75 * M["horizon"] for c in CAMPS)),
        "conv_spreads": ("the conventional lab, same policy and stock rule, doesn't spend 90 % of either campaign's "
                         "money in two years in half its seeds",
                         all(2 * d90c[c]["n"] <= d90c[c]["of"] for c in CAMPS)),
        "al_T1_partner_most": ("with the heuristic, most of the automated lab's first aluminium alloys past the best "
                               "existing alloy were printed at a partner, as all of the conventional lab's were",
                               2 * N["partner_al_T1"]["auto"]["lo"] > ns
                               and N["partner_al_T1"]["conv_stocked"]["inhouse"] == 0),
        "cu_inhouse_most": ("in every automated arm, most seeds' first copper alloy past the best existing alloy was "
                            "deposited on the in-house DED machine, and every one of the conventional lab's came "
                            "from a partner", 2 * n["win"]["cu_inhouse"]["lo"] > ns
                            and all(n["win"]["first"][f"conventional|{p}|{s_}"][CU]["T1"]["inhouse"] == 0
                                    for p in POLS for s_ in ("reorder", "lean"))),
        "replay_median_seed": ("the replayed run is its arm's median seed for both campaigns together, as "
                               f"like{D.ROUND}.json names it, and its event log is committed",
                               n["replay"]["seed"] is not None and n["replay"]["events"] is not None
                               and (D.HERE / n["replay"]["events"]).exists()),
    }
    return out


def claims() -> list:
    return list(claims_by_key().values())


def write() -> dict:
    n = numbers()
    D.VID.mkdir(parents=True, exist_ok=True)

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            o = o.item()
        if isinstance(o, float):
            return "inf" if math.isinf(o) else (None if math.isnan(o) else round(o, 4))
        return o
    p = D.VID / "numbers.json"
    have = json.loads(p.read_text()) if p.exists() else {}       # another module's keys (the intro cards') stay
    have.update(clean(n))
    p.write_text(json.dumps(have, indent=1) + "\n")
    return n


# ------------------------------------------------------------------------------------------------- words
def x1(v) -> str:
    return f"{v:.1f}×"


def end(v) -> str:
    """One end of an interval: one decimal, two where it would round to 1.0 without being 1 (so that 'includes 1'
    can be read off), 0 for 0, ∞ when unbounded."""
    if v is None or not math.isfinite(v):
        return "∞"
    if v == 0:
        return "0"
    if round(v, 1) == 1.0 and abs(v - 1.0) >= 0.005:
        return f"{v:.2f}"
    return f"{v:.1f}"


def rng(c: dict) -> str:
    return f"{end(c['lo'])} to {end(c['hi'])}"


def big(c: dict) -> str:
    """'at least 2.1×', '1.2×', 'at most 0.8×', 'no factor' for a cell."""
    if c is None or c["kind"] == "none":
        return "no factor"
    return {"at_least": "at least ", "at_most": "at most "}.get(c["kind"], "") + x1(c["af"])


def day(v) -> str:
    h = numbers()["money"]["horizon"]
    return f"after day {h:.0f}" if v is None or not math.isfinite(v) else f"day {v:.0f}"


def span(s: dict, fmt: str = ".1f", unit: str = "") -> str:
    """'1.3 to 1.4' or '1.2' for a {lo, hi} span."""
    a, b = format(s["lo"], fmt), format(s["hi"], fmt)
    return f"{a}{unit}" if a == b else f"{a} to {b}{unit}"


if __name__ == "__main__":
    n = write()
    D_ = n["labs"]["days"]
    for c in CAMPS:
        for tn in ("T1", "T2"):
            for p in POLS:
                print(f"{c:9s} {tn} {n['labs']['names'][p][c]:9s} " + " | ".join(
                    f"{q}: {D_[c][tn][p][q]['printed']}; {D_[c][tn][p][q]['hit_new']}/{D_[c][tn][p][q]['n']} vs "
                    f"{D_[c][tn][p][q]['hit_ref']}/{D_[c][tn][p][q]['n']}" for q in PAIRS))
    print("sum", json.dumps(n["labs"]["sum"], default=str)[:1500])
    print("nowin", json.dumps({k: v for k, v in n["nowin"].items() if k != "policy"}, default=str)[:1500])
    print("econ.sum", json.dumps(n["econ"]["sum"], default=str))
    print("money.d90", n["money"]["d90"], n["money"]["d90_cheap"], n["money"]["end"])
    print("replay", n["replay"])
    bad = 0
    for k, (c, ok) in claims_by_key().items():
        print("ok " if ok else "BAD", f"[{k}]", c)
        bad += not ok
    sys.exit(1 if bad else 0)

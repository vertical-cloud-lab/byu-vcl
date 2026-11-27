"""Round 5's comparisons, from the rows in out/twin5/runs (twin/bench5.py).

    python3 -m twin.like5            # -> out/twin5/like5.json and out/twin5/tables.md

Comparison 1 (like with like, four ways), comparison 2 (round 4's three plans), comparison 3 (round 3's economics),
the sensitivities (decision time, the automated atomizer's cycle, used equipment), the stock and the purchasing
look-back, shared stations, idle stretches, and each arm's median seed for both campaigns together. An arm is
reported only when it has at least ``MIN_SEEDS`` seeds; the paired statistics use the seeds two arms share.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np

from twin import bench2 as B2
from twin import bench5 as B5
from twin import like3b as L3

HERE = Path(__file__).resolve().parent
OUT = B5.OUT
MIN_SEEDS = int(os.environ.get("TWIN5_MIN_SEEDS", "12"))
HORIZON = 730.0
CAMPS = {"flaime_al": "Aluminium", "onr_cu": "Copper"}
TN = {"T1": "the best existing alloy on this synthetic benchmark (T1)", "T2": "halfway to the best alloy (T2)"}
PAIRS = (("lean", "lean"), ("reorder", "reorder"), ("reorder", "lean"), ("lean", "reorder"))   # (vertical, conv)
PAIR_NAMES = {("lean", "lean"): "both ordering as they go", ("reorder", "reorder"): "both stocked",
              ("reorder", "lean"): "vertical stocked, conventional lean (round 3's pairing)",
              ("lean", "reorder"): "vertical lean, conventional stocked"}
POL = {"fast": {"flaime_al": "heuristic", "onr_cu": "funnel"}, "bofn3": {"flaime_al": "BOFN", "onr_cu": "BOFN"},
       "pkgfn3": {"flaime_al": "pKGFN", "onr_cu": "pKGFN"}}


def load_all() -> dict:
    """{group key: {seed: row}} over every experiment's rows (a configuration run in two experiments counts once)."""
    A = {}
    for name in B5.EXPERIMENTS:
        for r in B5.load(name):
            A.setdefault(B5.group_key(r["cfg"]), {}).setdefault(r["cfg"]["seed"], r)
    return A


def gk(lab, plan, policy, stock, **o):
    return B5.group_key(B5._cfg(lab, plan, policy, stock, 0, **o))


def to_target(row, camp, tv):
    return L3.to_target(row, camp, tv)


def arm_stats(arm, camp, tv, seeds=None):
    seeds = sorted(arm) if seeds is None else seeds
    t = [to_target(arm[s], camp, tv) for s in seeds]
    xs, ok = [a for a, _ in t], [b for _, b in t]
    best = [arm[s]["campaigns"][camp]["best_new"] for s in seeds]
    spent = [arm[s]["campaigns"][camp]["spent"] for s in seeds]
    return dict(n=len(seeds), hit=int(sum(ok)), median=L3.km(xs, ok), best_mean=float(np.mean(best)),
                best_se=float(np.std(best, ddof=1) / math.sqrt(len(best))) if len(best) > 1 else 0.0,
                spent_mean=float(np.mean(spent)), days=[(float(a) if b else None) for a, b in zip(xs, ok)])


def factor(conv, vert, camp, tv, x="days", n_boot=2000):
    seeds = sorted(set(conv) & set(vert))
    if len(seeds) < MIN_SEEDS:
        return None
    return L3.factor(conv, vert, seeds, camp, tv, x=x, n_boot=n_boot)


def _f(r, money=False):
    """A factor cell as round 3b's tables print it."""
    if r is None:
        return "not enough seeds"
    return L3.fmt_factor(r, money=money)


def _cnt(r):
    return f"{r['hit_vert']}/{r['n']} vs {r['hit_conv']}/{r['n']}" if r else ""


def _d(v):
    return ">730" if v is None or not math.isfinite(v) else f"{v:.0f}"


# ------------------------------------------------------------------------------------------- comparison 1
def four_way(A, T, n_boot=2000) -> list:
    """Each campaign, target and policy pairing: the four stockings, both labs' arms nominal (decision windows,
    the derived atomizer cycle, used equipment allowed)."""
    rows = []
    combos = [("fast", "fast"), ("bofn3", "bofn3"), ("pkgfn3", "pkgfn3"), ("bofn3", "fast"), ("pkgfn3", "fast")]
    for camp in CAMPS:
        for tn in ("T1", "T2"):
            tv = T[tn][camp]
            for pv, pc in combos:
                if camp == "onr_cu" and (pv, pc) in (("bofn3", "fast"), ("pkgfn3", "fast")):
                    continue
                cells = {}
                for sv, sc in PAIRS:
                    V = A.get(gk("vertical", "parallel", pv, sv), {})
                    Cv = A.get(gk("conventional", "external", pc, sc), {})
                    cells[f"{sv}|{sc}"] = factor(Cv, V, camp, tv, n_boot=n_boot)
                money = {}
                for sv, sc in (("lean", "lean"), ("reorder", "reorder")):
                    V = A.get(gk("vertical", "parallel", pv, sv), {})
                    Cv = A.get(gk("conventional", "external", pc, sc), {})
                    money[f"{sv}|{sc}"] = factor(Cv, V, camp, tv, x="usd", n_boot=n_boot)
                if all(v is None for v in cells.values()):
                    continue
                rows.append(dict(camp=camp, target=tn, vert=pv, conv=pc, vert_name=POL[pv][camp],
                                 conv_name=POL[pc][camp], cells=cells, money=money))
    return rows


def stock_effect(A, T, n_boot=2000) -> list:
    """What the stock buys within one lab: lean against stocked, the same policy."""
    out = []
    for lab, plan in (("vertical", "parallel"), ("conventional", "external")):
        for pol in ("fast", "bofn3", "pkgfn3"):
            S = A.get(gk(lab, plan, pol, "reorder"), {})
            Lr = A.get(gk(lab, plan, pol, "lean"), {})
            for camp in CAMPS:
                for tn in ("T1", "T2"):
                    r = factor(Lr, S, camp, T[tn][camp], n_boot=n_boot)
                    if r:
                        out.append(dict(lab=lab, policy=pol, camp=camp, target=tn, r=r))
    return out


# ------------------------------------------------------------------------------------------- sensitivities
def decision_sensitivity(A, T, n_boot=1000) -> dict:
    """The four-way factors (cheap policies) with no decision delay, the nominal windows and slow windows."""
    out = {}
    for lev in ("none", "nominal", "slow"):
        o = {} if lev == "nominal" else dict(decisions=lev)
        rows = {}
        for camp in CAMPS:
            for tn in ("T1", "T2"):
                tv = T[tn][camp]
                for sv, sc in PAIRS:
                    V = A.get(gk("vertical", "parallel", "fast", sv, **o), {})
                    Cv = A.get(gk("conventional", "external", "fast", sc, **o), {})
                    rows[f"{camp}|{tn}|{sv}|{sc}"] = factor(Cv, V, camp, tv, n_boot=n_boot)
                for lab, plan in (("vertical", "parallel"), ("conventional", "external")):
                    for st in ("reorder", "lean"):
                        arm = A.get(gk(lab, plan, "fast", st, **o), {})
                        if len(arm) >= MIN_SEEDS:
                            rows[f"{camp}|{tn}|{lab}|{st}|arm"] = arm_stats(arm, camp, tv)
        out[lev] = rows
    return out


def atom_sensitivity(A, T) -> dict:
    out = {}
    for a in ("derived", "3h", "slow"):
        o = {} if a == "derived" else dict(atom=a)
        for st in ("reorder", "lean"):
            arm = A.get(gk("vertical", "parallel", "fast", st, **o), {})
            if len(arm) < MIN_SEEDS:
                continue
            d = {}
            for camp in CAMPS:
                for tn in ("T1", "T2"):
                    d[f"{camp}|{tn}"] = arm_stats(arm, camp, T[tn][camp])
            runs = []
            for r in arm.values():
                at = r["r5"]["atom"]
                sw = at.get("switch_h")
                weeks_auto = max(0.0, (HORIZON * 24 - (sw or HORIZON * 24)) / 168.0)
                runs.append(dict(total=at["runs"], by=at["runs_by"], weeks_auto=weeks_auto))
            d["atom_runs_mean"] = float(np.mean([x["total"] for x in runs]))
            d["atom_runs_by_mean"] = {c: float(np.mean([x["by"].get(c, 0) for x in runs])) for c in CAMPS}
            out[f"{a}|{st}"] = d
    return out


def used_effect(A, T, n_boot=1000) -> dict:
    W = A.get(gk("vertical", "parallel", "fast", "reorder"), {})
    N = A.get(gk("vertical", "parallel", "fast", "reorder", used=False), {})
    out = dict(stations={}, targets={})
    per = {}
    for r in W.values():
        for k, u in (r["r5"].get("used") or {}).items():
            per.setdefault(k, []).append(u)
    for k, us in per.items():
        out["stations"][k] = dict(name=us[0]["name"], n=len(us), faulty=sum(1 for u in us if u["fault"]),
                                  days_bought_median=float(np.median([u["days_bought"] for u in us])),
                                  days_bought_mean=float(np.mean([u["days_bought"] for u in us])),
                                  days_bought_min=float(np.min([u["days_bought"] for u in us])),
                                  expected_days_saved=us[0]["expected_days_saved"],
                                  usd_saved_mean=float(np.mean([u["usd_saved"] for u in us])),
                                  market=us[0]["market"])
    for camp in CAMPS:
        for tn in ("T1", "T2"):
            out["targets"][f"{camp}|{tn}"] = factor(N, W, camp, T[tn][camp], n_boot=n_boot)
    # which in-house stations come online when, with used and with new (the counterfactual in each row)
    on = {}
    for r in W.values():
        for st, h in (r["r4"].get("station_online") or {}).items():
            on.setdefault(st, []).append(h / 24.0)
    out["online_median_d"] = {k: float(np.median(v)) for k, v in on.items()}
    out["room_d"] = [r["r5"]["room_h"] / 24.0 for r in W.values() if r["r5"].get("room_h")]
    out["cell_d"] = [(r["r4"].get("cell_h") or 0) / 24.0 for r in W.values()]
    return out


# ------------------------------------------------------------------------------------------- comparison 2
def plans(A, T, n_boot=1000) -> dict:
    P = {p: A.get(gk("vertical", p, "fast", "reorder"), {}) for p in ("wait", "parallel", "external")}
    out = dict(arms={}, paired={})
    for p, arm in P.items():
        if len(arm) < MIN_SEEDS:
            continue
        out["arms"][p] = {f"{camp}|{tn}": arm_stats(arm, camp, T[tn][camp]) for camp in CAMPS for tn in ("T1", "T2")}
        out["arms"][p]["start_d"] = float(np.median([r["r4"]["start_h"] / 24.0 for r in arm.values()]))
        out["arms"][p]["cell_d"] = float(np.median([(r["r4"]["cell_h"] or 0) / 24.0 for r in arm.values()]))
        out["arms"][p]["full_d"] = float(np.median([(r["r4"].get("full_h") or 0) / 24.0 for r in arm.values()]))
    for other in ("wait", "external"):
        for camp in CAMPS:
            for tn in ("T1", "T2"):
                out["paired"][f"{other}|{camp}|{tn}"] = factor(P[other], P["parallel"], camp, T[tn][camp],
                                                               n_boot=n_boot)
    # with BOFN on both campaigns, where there are enough seeds
    PN = {"wait": A.get(gk("vertical", "wait", "bofn3", "reorder"), {}),
          "parallel": A.get(gk("vertical", "parallel", "bofn3", "reorder"), {}),
          "external": A.get(gk("vertical", "external", "bofn3", "reorder"), {})}
    out["net"] = {p: {f"{camp}|{tn}": arm_stats(arm, camp, T[tn][camp]) for camp in CAMPS for tn in ("T1", "T2")}
                  for p, arm in PN.items() if len(arm) >= MIN_SEEDS}
    return out


# ------------------------------------------------------------------------------------------- comparison 3
def economics(A, T) -> dict:
    """Round 3's economics on one stated basis each (round 2's cost model, twin/econ.py):

    * fixed costs: each lab's annual fixed cost (depreciation, service, utilities and space, fixed staff), from day 0
      for two years, the automated lab's in full from day 0 although its stations arrive over months (conservative
      for the automated lab); split between the campaigns by their money (aluminium 2/3, copper 1/3);
    * cost per demonstrated alloy: the campaign's spend over two years plus its share of the fixed costs, over the
      new alloys it tested through the whole chain;
    * cost to each target with equipment: the campaign's spend by the target plus its share of the capital paid by
      then (the automated lab's payments; none for the conventional lab, whose equipment exists) and of the fixed
      costs other than depreciation accrued by then. Seeds that never got there are left out (counts shown)."""
    from twin import econ as E
    fx = {lab: E.annual_cost(f) for lab, f in (("vertical", "vertical_lab"), ("conventional", "proposed"))}
    share = {"flaime_al": 2.0 / 3.0, "onr_cu": 1.0 / 3.0}
    out = dict(fixed_per_year={k: {kk: round(vv) for kk, vv in v.items()} for k, v in fx.items()}, arms={})
    for lab, plan in (("vertical", "parallel"), ("conventional", "external")):
        for pol in ("fast", "bofn3", "pkgfn3"):
            for st in ("reorder", "lean"):
                arm = A.get(gk(lab, plan, pol, st), {})
                if len(arm) < MIN_SEEDS:
                    continue
                F = fx[lab]
                nocap = (F["total"] - F["capex"]) / 365.0
                d = {}
                for camp in CAMPS:
                    tot, n_al, per_alloy = [], [], []
                    for r in arm.values():
                        c = r["campaigns"][camp]
                        fixed = F["total"] * 2.0 * share[camp]
                        n = c.get("n_new_alloys", 0)
                        tot.append(c["spent"] + fixed)
                        n_al.append(n)
                        if n:
                            per_alloy.append((c["spent"] + fixed) / n)
                    d[camp] = dict(total_2y_mean=float(np.mean(tot)), new_alloys_mean=float(np.mean(n_al)),
                                   per_alloy_median=float(np.median(per_alloy)) if per_alloy else None,
                                   per_alloy_campaign_only_median=float(np.median(
                                       [r["campaigns"][camp]["spent"] / r["campaigns"][camp]["n_new_alloys"]
                                        for r in arm.values() if r["campaigns"][camp].get("n_new_alloys")]))
                                   if any(r["campaigns"][camp].get("n_new_alloys") for r in arm.values()) else None)
                    for tn in ("T1", "T2"):
                        vals = []
                        for r in arm.values():
                            c = r["campaigns"][camp]
                            h = B2.hit(c["curve_new"], T[tn][camp], 2)
                            if not h:
                                continue
                            day, usd = float(h[0]), float(h[1])
                            cap = sum(u for t, u, _ in r["r4"].get("payments", []) if t / 24.0 <= day) \
                                if lab == "vertical" else 0.0
                            vals.append(usd + share[camp] * (cap + nocap * day))
                        d[camp][tn] = dict(n=len(vals), of=len(arm), median=float(np.median(vals)) if vals else None)
                out["arms"][f"{lab}|{pol}|{st}"] = d
    return out


# ------------------------------------------------------------------------------------------- stock, look-back
def stock_summary(A) -> dict:
    out = {}
    for key, arm in A.items():
        if len(arm) < MIN_SEEDS or "dec-" in key or "atom-" in key or "noused" in key:
            continue
        d = {}
        for camp in CAMPS:
            S = [r["r5"]["stock"][camp] for r in arm.values()]
            d[camp] = dict(mode=S[0]["mode"], charges=float(np.mean([s["n_charges"] for s in S])),
                           short_frac=float(np.mean([s.get("charges_short_frac", 0) for s in S])),
                           short_after90=float(np.mean([s.get("n_stockouts_after90", 0) for s in S])),
                           wait_mean_d=float(np.mean([s.get("wait_mean_d", 0) for s in S])),
                           wait_p90_d=float(np.mean([s.get("wait_p90_d", 0) for s in S])),
                           stock_usd=float(np.mean([s["stock_usd"] for s in S])),
                           bought_usd=float(np.mean([s["bought_usd"] for s in S])),
                           left_usd=float(np.mean([s["left_usd"] for s in S])),
                           items_short={k: sum(1 for s in S if k in s["items_short"]) for k in
                                        sorted({k for s in S for k in s["items_short"]})})
        out[key] = d
    return out


def lookback(A, key, qs=(0.5, 0.75, 0.9), period_w=8) -> dict:
    """The purchasing look-back for one arm. From the materials the campaigns actually used (weekly, every seed), a
    buying schedule for each quantile q: an order every ``period_w`` weeks, timed to arrive (a median lead after it
    is placed, never before day 0, since nothing can be bought before the money arrives) at the start of its period,
    for the use until the next order arrives, at the q quantile over seeds, net of what is left. Each schedule, and
    the heuristic's own orders as they were placed in the runs (event logs; with the stock on hand at day 0), are set
    against each seed's own use: item-weeks short (a week that ends with more used than has arrived: a charge was
    waiting), money bought, and stock left at the end."""
    from twin import campaign as C
    from twin import supply
    arm = A.get(key, {})
    if len(arm) < MIN_SEEDS:
        return {}
    nw = int(math.ceil(HORIZON / 7.0))
    out = {}
    logs = {}
    if key.endswith("_reorder") or "_reorder_" in key:
        for s_, r in arm.items():
            p = HERE.parent / r.get("events_file", "")
            if p.exists():
                try:
                    logs[s_] = B5.read_events(p).get("round5", {}).get("stock", {})
                except Exception:
                    pass
    for camp in CAMPS:
        U = {}
        for s_, r in arm.items():
            for it, w in r["r5"]["stock"][camp]["use_weekly"].items():
                U.setdefault(it, {})[s_] = np.array(w[:nw] + [0.0] * max(0, nw - len(w)), dtype=float)
        seeds = sorted(arm)
        pre = C.PRESTOCK[camp]
        res = {q: dict(usd=0.0, left=0.0, short=0.0, schedule={}) for q in qs}
        heur = dict(usd=0.0, left=0.0, short=0.0, n=0)
        for it, per in U.items():
            if it not in supply.ITEMS:
                continue
            I = supply.ITEMS[it]
            price = I.price
            M = np.array([per.get(s_, np.zeros(nw)) for s_ in seeds])
            cum = np.cumsum(M, axis=1)
            lead_w = int(math.ceil((I.lead_days + 3.0) / 7.0))
            p0 = pre.get(it, 0.0)
            for q in qs:
                arr = np.zeros(nw + lead_w + 2)
                arr[0] += p0
                orders = []
                for w_arr in range(0, nw, period_w):
                    w_ord = max(0, w_arr - lead_w)
                    w_got = w_ord + lead_w
                    w_next = min(nw, w_arr + period_w + lead_w)
                    need_to = np.quantile(cum[:, min(w_next, nw) - 1], q)
                    have = float(arr[:nw].sum())
                    qty = max(0.0, need_to - have)
                    if qty > 1e-9:
                        qty = max(qty, I.moq)
                        arr[min(w_got, nw + lead_w)] += qty
                        orders.append((w_ord, qty))
                ca = np.cumsum(arr[:nw])
                short = float(np.mean([(cum[i] > ca + 1e-9).sum() for i in range(len(seeds))]))
                left = float(np.mean([max(0.0, arr.sum() - cum[i, -1]) for i in range(len(seeds))])) * price
                usd = sum(qq for _, qq in orders) * price
                R = res[q]
                R["usd"] += usd
                R["left"] += left
                R["short"] += short
                merged = {}
                for w, qq in orders:
                    merged[int(w * 7)] = merged.get(int(w * 7), 0.0) + qq
                R["schedule"][it] = dict(orders=[(d_, round(qq, 4)) for d_, qq in sorted(merged.items())],
                                         lead_d=I.lead_days,
                                         total_qty=round(sum(qq for _, qq in orders), 4), usd=round(usd, 2),
                                         weeks_short=round(short, 2), left_usd=round(left, 2),
                                         use_median=round(float(np.median(cum[:, -1])), 4))
            if logs:
                sh, lf, us = [], [], []
                for i, s_ in enumerate(seeds):
                    L = logs.get(s_, {}).get(camp)
                    if not L:
                        continue
                    arr = np.zeros(nw + 400)
                    arr[0] += p0
                    tot = p0
                    usd = 0.0
                    for o in L.get("orders", []):
                        d0, item, qty, cost, why, arr_d = o
                        if item != it:
                            continue
                        arr[min(int(arr_d // 7), nw + 399)] += qty
                        tot += qty
                        usd += cost
                    ca = np.cumsum(arr[:nw])
                    sh.append(int((cum[i] > ca + 1e-9).sum()))
                    lf.append(max(0.0, tot - cum[i, -1]) * price)
                    us.append(usd)
                if sh:
                    heur["short"] += float(np.mean(sh))
                    heur["left"] += float(np.mean(lf))
                    heur["usd"] += float(np.mean(us))
                    heur["n"] = len(sh)
        H = [r["r5"]["stock"][camp] for r in arm.values()]
        out[camp] = dict(schedules={str(q): dict(usd=round(R["usd"], 2), left_usd=round(R["left"], 2),
                                                 item_weeks_short=round(R["short"], 2), schedule=R["schedule"])
                                    for q, R in res.items()},
                         heuristic=dict(usd=round(heur["usd"], 2), left_usd=round(heur["left"], 2),
                                        item_weeks_short=round(heur["short"], 2), n=heur["n"]) if logs else None,
                         heuristic_run=dict(usd=float(np.mean([h["stock_usd"] for h in H])),
                                            left_usd=float(np.mean([h["left_usd"] for h in H])),
                                            charges_short=float(np.mean([h.get("charges_short_frac", 0) for h in H]))))
    return out


# ------------------------------------------------------------------------------------------- shared, idle
def shared(A, key) -> dict:
    """Each station kind's use by campaign (unit-hours) against the unit-hours it offered, by quarter, mean over
    seeds: in-house and outside routes of a kind together; which bind (over 70 % in some quarter)."""
    arm = A.get(key, {})
    if not arm:
        return {}
    agg = {}
    for r in arm.values():
        for st, d in r["r5"]["shared"].items():
            role = d["role"]
            g = agg.setdefault(role, dict(busy={}, avail=None, n=0, stations=set()))
            g["stations"].add(st)
            for camp, arr in d["busy"].items():
                b = g["busy"].setdefault(camp, np.zeros(len(arr)))
                b[:len(arr)] += np.array(arr) / len(arm)
            av = np.array(d["avail"]) / len(arm)
            g["avail"] = av if g["avail"] is None else g["avail"] + av
    out = {}
    for role, g in agg.items():
        tot = sum(g["busy"].values()) if g["busy"] else np.zeros_like(g["avail"])
        util = [float(b / a) if a > 0 else None for b, a in zip(tot, g["avail"])]
        out[role] = dict(stations=sorted(g["stations"]), util=util,
                         busy={c: [round(float(x), 1) for x in v] for c, v in g["busy"].items()},
                         avail=[round(float(x), 1) for x in g["avail"]],
                         share={c: round(float(np.sum(v) / max(np.sum(tot), 1e-9)), 3) for c, v in g["busy"].items()},
                         binds=bool(any(u is not None and u > 0.7 for u in util)))
    return out


CAUSE_NAMES = {"spending plan": "money kept for the partners' standing slots",
               "WIP limit": "WIP limit (lots already waiting for the first fabrication step)",
               "capacity": "capacity (station busy)"}


def idle(A, key) -> dict:
    """Round 5 has no spending plan: a 'plan' refusal there is round 4's reserve for the coming week's standing
    slots, so it is named that here."""
    arm = A.get(key, {})
    out = {}
    for camp in CAMPS:
        for grp in ("atomizer", "fab"):
            days, n, flagged = {}, 0, []
            for s, r in arm.items():
                for x in r["r5"]["idle"]["stretches"][camp][grp]:
                    cz = CAUSE_NAMES.get(x["cause"], x["cause"])
                    days[cz] = days.get(cz, 0) + x["days"]
                    n += 1
                    if x["flag"]:
                        flagged.append(dict(seed=s, start_d=x["start_d"], days=x["days"], causes=x["causes"]))
            tot = sum(days.values())
            out[f"{camp}|{grp}"] = dict(stretches_per_seed=n / max(len(arm), 1),
                                        idle_days_per_seed=tot / max(len(arm), 1),
                                        by_cause={k: round(v / max(len(arm), 1), 1) for k, v in
                                                  sorted(days.items(), key=lambda kv: -kv[1])},
                                        flagged=flagged)
    return out


def counters(A, key) -> dict:
    arm = A.get(key, {})
    out = {}
    for camp in CAMPS:
        C = [r["r5"]["counters"][camp] for r in arm.values()]
        out[camp] = {k: float(np.mean([c[k] for c in C])) for k in C[0]} if C else {}
    return out


def money_out(A, key) -> dict:
    """When each campaign had spent 90 % of its money (median day; seeds that never did count as 730)."""
    arm = A.get(key, {})
    out = {}
    for camp in CAMPS:
        days = []
        for r in arm.values():
            c = r["campaigns"][camp]
            sc = c.get("spend_curve") or []
            d90 = None
            for p in sc:
                if p[1] >= 0.9 * c["budget"]:
                    d90 = p[0]
                    break
            days.append(d90 if d90 is not None else HORIZON)
        out[camp] = dict(median_d90=float(np.median(days)) if days else None,
                         n_spent90=sum(1 for d in days if d < HORIZON), n=len(days))
    return out


def hpc_summary(A, T, n_boot=1000) -> dict:
    """Note 4: the HPC stream's candidates (evaluated at the allocation's throughput, and seen by the policies),
    the policies' own simulation hours, and four times the candidates seen against the nominal pool."""
    out = dict(arms={}, more={})
    for key, arm in A.items():
        if len(arm) < MIN_SEEDS or "dec-" in key or "atom-" in key or "noused" in key:
            continue
        hp = [r["r5"].get("hpc") for r in arm.values() if r["r5"].get("hpc")]
        if not hp:
            continue
        out["arms"][key] = dict(cores=hp[0]["cores"], per_day=hp[0]["per_day"], keep=hp[0]["keep"],
                                add_per_day=hp[0]["add_per_day"],
                                **{f"{camp}_{f}": float(np.mean([h["campaigns"][camp][f] for h in hp]))
                                   for camp in CAMPS for f in ("evaluated", "materialized", "own_sims",
                                                               "hpc_station_h")})
    for lab, plan in (("vertical", "parallel"), ("conventional", "external")):
        base = A.get(gk(lab, plan, "fast", "reorder"), {})
        more = A.get(gk(lab, plan, "fast", "reorder", hpc=dict(keep=512, add_per_day=256)), {})
        for camp in CAMPS:
            for tn in ("T1", "T2"):
                out["more"][f"{lab}|{camp}|{tn}"] = factor(base, more, camp, T[tn][camp], n_boot=n_boot)
    return out


# ------------------------------------------------------------------------------------------- median seeds
def median_seed(arm, T) -> dict | None:
    """The one seed whose aluminium and copper days to their targets are both closest to the arm's medians: the
    largest of its four distances (each campaign, each target; days censored at 730), in units of that target's
    interquartile range over seeds, is the smallest."""
    if len(arm) < MIN_SEEDS:
        return None
    seeds = sorted(arm)
    D, med, iqr = {}, {}, {}
    for camp in CAMPS:
        for tn in ("T1", "T2"):
            v = np.array([to_target(arm[s], camp, T[tn][camp])[0] for s in seeds])
            D[(camp, tn)] = v
            med[(camp, tn)] = float(np.median(v))
            q1, q3 = np.percentile(v, [25, 75])
            iqr[(camp, tn)] = max(float(q3 - q1), 7.0)
    score = {s: max(abs(D[k][i] - med[k]) / iqr[k] for k in D) for i, s in enumerate(seeds)}
    best = min(seeds, key=lambda s: (score[s], s))
    i = seeds.index(best)
    rid = B5.run_id(arm[best]["cfg"])
    return dict(seed=best, score=round(score[best], 3), events=f"out/twin5/events/{rid}.json.xz",
                days={f"{c}|{t}": float(D[(c, t)][i]) for c, t in D}, medians={f"{c}|{t}": med[(c, t)] for c, t in D})


# ------------------------------------------------------------------------------------------- run
def run(n_boot=2000) -> dict:
    A = load_all()
    T = B2.targets()
    S = dict(targets=T, min_seeds=MIN_SEEDS, n_seeds={k: len(v) for k, v in A.items()},
             four_way=four_way(A, T, n_boot), stock_effect=stock_effect(A, T, n_boot),
             decisions=decision_sensitivity(A, T), atom=atom_sensitivity(A, T), used=used_effect(A, T),
             plans=plans(A, T), economics=economics(A, T), stock=stock_summary(A))
    S["arms"] = {}
    for key, arm in A.items():
        if len(arm) < MIN_SEEDS:
            continue
        S["arms"][key] = dict(n=len(arm), stats={f"{c}|{t}": arm_stats(arm, c, T[t][c]) for c in CAMPS
                                                 for t in ("T1", "T2")},
                              counters=counters(A, key), money=money_out(A, key), median_seed=median_seed(arm, T),
                              idle=idle(A, key))
    S["hpc"] = hpc_summary(A, T)
    for key in (gk("vertical", "parallel", "fast", "reorder"), gk("conventional", "external", "fast", "reorder"),
                gk("vertical", "parallel", "fast", "lean"), gk("conventional", "external", "fast", "lean")):
        S.setdefault("lookback", {})[key] = lookback(A, key)
        S.setdefault("shared", {})[key] = shared(A, key)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "like5.json").write_text(json.dumps(B2._jsonable(S), default=lambda o: sorted(o) if isinstance(o, set)
                                               else str(o)))
    (OUT / "tables.md").write_text(tables(S))
    return S


# ------------------------------------------------------------------------------------------- tables
def _arm_line(st):
    return f"{st['hit']}/{st['n']}; {_d(st['median'])}"


def tables(S) -> str:
    T = S["targets"]
    L = ["# Round 5: tables", "",
         "Made by `python -m twin.like5` from `out/twin5/runs/`. All simulated. Days from the day the money arrives; "
         "medians are Kaplan-Meier over seeds (a seed that never gets there counts as censored at day 730; '>730': "
         "fewer than half got there). Factors: the conventional lab's median over the automated lab's, with a 95 % "
         "paired-bootstrap interval; '>=' a lower bound where fewer than half the conventional seeds got there. "
         f"Arms with fewer than {S['min_seeds']} seeds are not reported. Targets: "
         + "; ".join(f"{CAMPS[c]} T1 {T['T1'][c]:.2f}, T2 {T['T2'][c]:.2f}" for c in CAMPS) + ".", ""]
    L += ["## 1. Like with like, four ways (nominal decision windows, the derived atomizer cycle)", "",
          "| Target | Automated lab | Conventional lab | " + " | ".join(PAIR_NAMES[p] for p in PAIRS) + " |",
          "|---|---|---|" + "---|" * len(PAIRS)]
    for r in S["four_way"]:
        cells = []
        for sv, sc in PAIRS:
            x = r["cells"].get(f"{sv}|{sc}")
            cells.append(f"{_f(x)}; {_cnt(x)}" if x else "not enough seeds")
        L.append(f"| {CAMPS[r['camp']]} {r['target']} | {r['vert_name']} | {r['conv_name']} | " + " | ".join(cells) + " |")
    L += ["", "Cost on one basis (campaign spend to the target; fixed costs and equipment left out; section 3 adds them):",
          "", "| Target | Automated | Conventional | both lean | both stocked |", "|---|---|---|---|---|"]
    for r in S["four_way"]:
        m = r["money"]
        L.append(f"| {CAMPS[r['camp']]} {r['target']} | {r['vert_name']} | {r['conv_name']} | "
                 f"{_f(m.get('lean|lean'), True)} | {_f(m.get('reorder|reorder'), True)} |")
    L += ["", "### The arms", "", "| Arm | seeds | Al T1 | Al T2 | Cu T1 | Cu T2 | Al best | Cu best | money 90 % spent "
          "(median day: Al, Cu) |", "|---|---|---|---|---|---|---|---|---|"]
    for key, a in sorted(S["arms"].items()):
        st = a["stats"]
        mo = a["money"]
        L.append(f"| `{key}` | {a['n']} | {_arm_line(st['flaime_al|T1'])} | {_arm_line(st['flaime_al|T2'])} | "
                 f"{_arm_line(st['onr_cu|T1'])} | {_arm_line(st['onr_cu|T2'])} | "
                 f"{st['flaime_al|T1']['best_mean']:.2f} ± {st['flaime_al|T1']['best_se']:.2f} | "
                 f"{st['onr_cu|T1']['best_mean']:.2f} ± {st['onr_cu|T1']['best_se']:.2f} | "
                 f"{_d(mo['flaime_al']['median_d90'])}, {_d(mo['onr_cu']['median_d90'])} |")
    L += ["", "### What the stock buys within a lab (lean over stocked, same policy)", "",
          "| Lab | Policy | Target | factor; seeds there (stocked vs lean) |", "|---|---|---|---|"]
    for x in S["stock_effect"]:
        L.append(f"| {x['lab']} | {POL[x['policy']][x['camp']]} | {CAMPS[x['camp']]} {x['target']} | "
                 f"{_f(x['r'])}; {_cnt(x['r'])} |")
    # decisions
    L += ["", "## Decision time: the four-way factors with no delay, the nominal windows and slow windows (cheap "
          "policies)", "", "| Target | Pairing | no delay | nominal | slow |", "|---|---|---|---|---|"]
    D = S["decisions"]
    for camp in CAMPS:
        for tn in ("T1", "T2"):
            for sv, sc in PAIRS:
                k = f"{camp}|{tn}|{sv}|{sc}"
                L.append(f"| {CAMPS[camp]} {tn} | {PAIR_NAMES[(sv, sc)]} | " +
                         " | ".join(f"{_f(D[lev].get(k))}" for lev in ("none", "nominal", "slow")) + " |")
    L += ["", "| Arm | Target | no delay | nominal | slow |", "|---|---|---|---|---|"]
    for camp in CAMPS:
        for tn in ("T1", "T2"):
            for lab in ("vertical", "conventional"):
                for st in ("reorder", "lean"):
                    k = f"{camp}|{tn}|{lab}|{st}|arm"
                    L.append(f"| {lab}, {'stocked' if st == 'reorder' else 'lean'} | {CAMPS[camp]} {tn} | " +
                             " | ".join(_arm_line(D[lev][k]) if D[lev].get(k) else "-" for lev in
                                        ("none", "nominal", "slow")) + " |")
    # atom
    L += ["", "## The automated atomizer's cycle (note 2; the automated lab, cheap policies)", "",
          "| Cycle | Stock | Al T1 | Al T2 | Cu T1 | Cu T2 | atomizer runs in 2 years (Al, Cu) |",
          "|---|---|---|---|---|---|---|"]
    for k, d in S["atom"].items():
        a, st = k.split("|")
        L.append(f"| {a} | {'stocked' if st == 'reorder' else 'lean'} | {_arm_line(d['flaime_al|T1'])} | "
                 f"{_arm_line(d['flaime_al|T2'])} | {_arm_line(d['onr_cu|T1'])} | {_arm_line(d['onr_cu|T2'])} | "
                 f"{d['atom_runs_by_mean'].get('flaime_al', 0):.0f}, {d['atom_runs_by_mean'].get('onr_cu', 0):.0f} |")
    # used
    U = S["used"]
    L += ["", "## Used equipment (the automated lab, stocked, cheap policies)", "",
          "| Item | bought used in | arrived faulty | days bought (median; min) | expected by the rule | $ saved (mean) |",
          "|---|---|---|---|---|---|"]
    for k, d in U["stations"].items():
        L.append(f"| {d['name']} | {d['n']} seeds | {d['faulty']} | {d['days_bought_median']:.0f}; "
                 f"{d['days_bought_min']:.0f} | {d['expected_days_saved']:.0f} | {d['usd_saved_mean']:,.0f} |")
    L += ["", "| Target | all new over with used: factor; seeds there (used vs new) |", "|---|---|"]
    for k, r in U["targets"].items():
        c, t = k.split("|")
        L.append(f"| {CAMPS[c]} {t} | {_f(r)}; {_cnt(r)} |")
    # plans
    P = S["plans"]
    L += ["", "## 2. Round 4's three plans (cheap policies, stocked)", "",
          "| Plan | starts (median day) | Al T1 | Al T2 | Cu T1 | Cu T2 | Al best | Cu best |", "|---|---|---|---|---|---|---|---|"]
    for p, d in P["arms"].items():
        L.append(f"| {p} | {d['start_d']:.0f} | {_arm_line(d['flaime_al|T1'])} | {_arm_line(d['flaime_al|T2'])} | "
                 f"{_arm_line(d['onr_cu|T1'])} | {_arm_line(d['onr_cu|T2'])} | "
                 f"{d['flaime_al|T1']['best_mean']:.2f} ± {d['flaime_al|T1']['best_se']:.2f} | "
                 f"{d['onr_cu|T1']['best_mean']:.2f} ± {d['onr_cu|T1']['best_se']:.2f} |")
    L += ["", "| Parallel against | Target | factor (other plan's median over parallel's); parallel first / other first |",
          "|---|---|---|"]
    for k, r in P["paired"].items():
        o, c, t = k.split("|")
        if r:
            L.append(f"| {o} | {CAMPS[c]} {t} | {_f(r)}; {r['v_first']} / {r['c_first']} |")
    if P.get("net"):
        L += ["", "With BOFN on both campaigns:", "", "| Plan | Al T1 | Al T2 | Cu T1 | Cu T2 |", "|---|---|---|---|---|"]
        for p, d in P["net"].items():
            L.append(f"| {p} | " + " | ".join(_arm_line(d[f'{c}|{t}']) for c in CAMPS for t in ("T1", "T2")) + " |")
    # economics
    E = S["economics"]
    L += ["", "## 3. Economics (round 3's model; the bases are in `twin/like5.py` `economics`)", "",
          "Fixed costs a year: " + "; ".join(f"{lab} ${v['total']:,.0f} (depreciation ${v['capex']:,.0f})"
                                              for lab, v in E["fixed_per_year"].items()) + ".", "",
          "| Arm | Campaign | spend + fixed, 2 years | new alloys tested | per alloy (with fixed) | per alloy (campaign "
          "only) | to T1 with equipment (seeds) | to T2 with equipment (seeds) |", "|---|---|---|---|---|---|---|---|"]
    for k, d in E["arms"].items():
        for camp in CAMPS:
            x = d[camp]
            f = lambda v: "-" if v is None else f"${v:,.0f}"
            L.append(f"| `{k}` | {CAMPS[camp]} | {f(x['total_2y_mean'])} | {x['new_alloys_mean']:.1f} | "
                     f"{f(x['per_alloy_median'])} | {f(x['per_alloy_campaign_only_median'])} | "
                     f"{f(x['T1']['median'])} ({x['T1']['n']}/{x['T1']['of']}) | "
                     f"{f(x['T2']['median'])} ({x['T2']['n']}/{x['T2']['of']}) |")
    # stock
    L += ["", "## Stock (mean over seeds)", "", "| Arm | Campaign | charges | charges that waited for stock | "
          "waits after day 90 | mean wait (days) | stock bought | left at the end |", "|---|---|---|---|---|---|---|---|"]
    for k, d in S["stock"].items():
        for camp in CAMPS:
            x = d[camp]
            L.append(f"| `{k}` | {CAMPS[camp]} | {x['charges']:.0f} | {x['short_frac']:.0%} | {x['short_after90']:.0f} | "
                     f"{x['wait_mean_d']:.1f} | ${x['bought_usd']:,.0f} | ${x['left_usd']:,.0f} |")
    for key, lb in (S.get("lookback") or {}).items():
        if not lb:
            continue
        L += ["", f"### Purchasing look-back: `{key}`", "",
              "Each set against each seed's own weekly use, mean over seeds. An item-week short is a week that ends with "
              "more of an item used than has arrived (a charge was waiting for it). The look-back schedules order every "
              "8 weeks, timed to arrive as each period starts (never before day 0), for the use until the next order "
              "arrives at the given quantile over seeds.", "",
              "| Campaign | rule | bought | left at the end | item-weeks short |", "|---|---|---|---|---|"]
        for camp in CAMPS:
            x = lb[camp]
            if x.get("heuristic"):
                h = x["heuristic"]
                L.append(f"| {CAMPS[camp]} | the heuristic, as it ran | ${h['usd']:,.0f} | ${h['left_usd']:,.0f} | "
                         f"{h['item_weeks_short']:.1f} |")
            for q, d in x["schedules"].items():
                L.append(f"| {CAMPS[camp]} | look-back schedule, q = {q} | ${d['usd']:,.0f} | ${d['left_usd']:,.0f} | "
                         f"{d['item_weeks_short']:.1f} |")
        for camp in CAMPS:
            sch = lb[camp]["schedules"].get("0.75", {}).get("schedule", {})
            top = sorted(sch.items(), key=lambda kv: -kv[1]["usd"])[:8]
            if not top:
                continue
            L += ["", f"Recommended buying schedule (q = 0.75), {CAMPS[camp]}: the 8 items with the most money "
                  "(day the order is placed: quantity)", "", "| Item | median lead (days) | orders | total | $ |",
                  "|---|---|---|---|---|"]
            for it, d in top:
                od = ", ".join(f"d{dd}: {qq:.3g}" for dd, qq in d["orders"][:7]) + (" ..." if len(d["orders"]) > 7
                                                                                   else "")
                L.append(f"| {it} | {d['lead_d']:.0f} | {od} | {d['total_qty']:.3g} | ${d['usd']:,.0f} |")
    # shared and idle
    for key, sh in (S.get("shared") or {}).items():
        if not sh:
            continue
        L += ["", f"### Shared stations: `{key}` (use over offered unit-hours by quarter; share by campaign)", "",
              "| Station kind | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Al share | binds |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for role, d in sorted(sh.items(), key=lambda kv: -max([u or 0 for u in kv[1]["util"]] or [0])):
            if not d["busy"]:
                continue
            u = [("-" if x is None else f"{x:.0%}") for x in d["util"][:8]]
            u += ["-"] * (8 - len(u))
            L.append(f"| {role} | " + " | ".join(u) + f" | {d['share'].get('flaime_al', 0):.0%} | "
                     f"{'yes' if d['binds'] else ''} |")
    L += ["", "## Idle stretches (note 3): at least 7 days with no start at a campaign's pacing station", "",
          "| Arm | Campaign, station | stretches per seed | idle days per seed | by cause (days per seed) | flagged |",
          "|---|---|---|---|---|---|"]
    for key, a in sorted(S["arms"].items()):
        if "dec-" in key or "atom-" in key or "noused" in key:
            continue
        for k, x in a["idle"].items():
            c, g = k.split("|")
            L.append(f"| `{key}` | {CAMPS[c]}, {'atomizer' if g == 'atomizer' else 'first fabrication step'} | "
                     f"{x['stretches_per_seed']:.1f} | {x['idle_days_per_seed']:.0f} | "
                     + ", ".join(f"{kk} {vv:.0f}" for kk, vv in list(x["by_cause"].items())[:5]) +
                     f" | {len(x['flagged'])} |")
    L += ["", "## Counters (mean per run)", "", "| Arm | Campaign | designed | lots made | alloys made | alloys printed or "
          "deposited | alloys tested | tests |", "|---|---|---|---|---|---|---|---|"]
    for key, a in sorted(S["arms"].items()):
        if "dec-" in key or "atom-" in key or "noused" in key:
            continue
        for camp in CAMPS:
            c = a["counters"].get(camp) or {}
            if c:
                L.append(f"| `{key}` | {CAMPS[camp]} | {c['designed']:.0f} | {c['lots_made']:.0f} | {c['alloys_made']:.0f} | "
                         f"{c['alloys_printed']:.0f} | {c['alloys_tested']:.0f} | {c['tests']:.0f} |")
    Hh = S.get("hpc") or {}
    if Hh.get("arms"):
        L += ["", "## The HPC stream (note 4)", "", "| Arm | cores | candidates a day (allocation) | evaluated, Al | "
              "seen by the policy, Al | evaluated, Cu | seen, Cu | policies' own simulation hours (Al, Cu) |",
              "|---|---|---|---|---|---|---|---|"]
        for key, d in sorted(Hh["arms"].items()):
            L.append(f"| `{key}` | {d['cores']} | {d['per_day']:,.0f} | {d['flaime_al_evaluated']:,.0f} | "
                     f"{d['flaime_al_materialized']:,.0f} | {d['onr_cu_evaluated']:,.0f} | {d['onr_cu_materialized']:,.0f} | "
                     f"{d['flaime_al_hpc_station_h']:.0f}, {d['onr_cu_hpc_station_h']:.0f} |")
        L += ["", "Four times the candidates the policies see (512 kept, 256 new a day) against the nominal pool "
              "(128, 64 a day): factor (nominal's median over the bigger pool's); seeds there (bigger vs nominal)", "",
              "| Lab | Target | factor |", "|---|---|---|"]
        for k, r in Hh["more"].items():
            lab, c, t = k.split("|")
            L.append(f"| {lab} | {CAMPS[c]} {t} | {_f(r)}; {_cnt(r)} |")
    L += ["", "## Median seed for both campaigns together (for a continuous replay)", "",
          "| Arm | seed | Al T1, T2 (median) | Cu T1, T2 (median) | event log |", "|---|---|---|---|---|"]
    for key, a in sorted(S["arms"].items()):
        m = a.get("median_seed")
        if not m:
            continue
        dd, md = m["days"], m["medians"]
        L.append(f"| `{key}` | {m['seed']} | {dd['flaime_al|T1']:.0f}, {dd['flaime_al|T2']:.0f} "
                 f"({md['flaime_al|T1']:.0f}, {md['flaime_al|T2']:.0f}) | {dd['onr_cu|T1']:.0f}, {dd['onr_cu|T2']:.0f} "
                 f"({md['onr_cu|T1']:.0f}, {md['onr_cu|T2']:.0f}) | `{m['events']}` |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    S = run()
    print((OUT / "tables.md").read_text()[:6000])

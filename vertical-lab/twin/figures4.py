"""Round 4's tables and figures, from out/twin4/runs/*.jsonl.

    python3 -m twin.figures4      # -> out/twin4/fig/{tables.md, numbers.json, *.png}

Every number in notes/twin_round4.md comes from tables.md or numbers.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from twin import bench2 as B2
from twin import bench3 as B3
from twin import bench4 as B4
from twin import round4 as R4

FIG = B4.OUT / "fig"
CAMPS = ("flaime_al", "onr_cu")
CNAME = {"flaime_al": "Aluminium", "onr_cu": "Copper"}
PNAME = {"wait": "Wait for the cell", "parallel": "Ramp up in parallel", "external": "External routes only"}
# categorical slots 1-3 of the reference palette (validated: twin/figures4.py's docstring; dataviz validate_palette)
PCOL = {"wait": "#257de0", "parallel": "#f47230", "external": "#00b894"}
INK, INK2, GRID, AXIS = "#191919", "#666666", "#e7e7e7", "#c2c2c2"
MONTH_H = 30.4 * 24.0


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def _rows(name):
    return B4.load(name)


def _by_plan(rows):
    out = {}
    for r in rows:
        out.setdefault(r["cfg"]["plan"], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: r["cfg"]["seed"])
    return out


def _hit_day(curve, target):
    h = B2.hit(curve, target, 2)
    return h[0] if h else None


def _t3_day(r, camp, T):
    """Days to the first alloy through every stage (gas lot, validation network, full part) whose discovery utility
    (true) is at or above T2."""
    st = (r["r4"].get("stages") or {}).get(camp) or {}
    days = [d["t_end"] for d in st.get("done", []) if d.get("result") == "validated" and
            (d.get("u_true") or 0) >= T["T2"][camp] - 1e-9]
    return min(days) if days else None


def _fmt_day(d):
    return "—" if d is None else f"{d:.0f}"


def _km(days, horizon=B4.DAYS):
    m = B3.km_median(days, horizon)
    return f">{horizon}" if m is None else f"{m:.0f}"


def _mse(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return f"{x.mean():.2f}"
    return f"{x.mean():.2f} ± {x.std(ddof=1) / math.sqrt(len(x)):.2f}"


def plan_table(name, T, N):
    rows = _rows(name)
    if not rows:
        return []
    P = _by_plan(rows)
    lines = [f"**`{name}`** ({rows[0]['cfg']['policy']} = {B4.ALIAS.get(rows[0]['cfg']['policy'], '')}; "
             f"money ×{rows[0]['cfg'].get('money', 1.0):g}; days from funding; Kaplan-Meier medians over seeds; "
             f"'>730' means fewer than half the seeds got there in two years)", "",
             "| Plan | n | Al best | Al T1: seeds; day | Al T2: seeds; day | Cu best | Cu T1: seeds; day | "
             "Cu T2: seeds; day | validated T2 alloy (Al; Cu): seeds; day | cell complete (day) | "
             "discovery spend (Al + Cu) | capital |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    N[name] = {}
    for plan in B4.PLANS:
        rs = P.get(plan)
        if not rs:
            continue
        n = len(rs)
        rec = dict(n=n, seeds=[r["cfg"]["seed"] for r in rs])
        cells = [PNAME[plan], str(n)]
        for camp in CAMPS:
            best = [r["campaigns"][camp]["best_new"] for r in rs]
            rec[camp] = dict(best=best)
            cells.append(_mse(best))
            for tn in ("T1", "T2"):
                dl = [_hit_day(r["campaigns"][camp]["curve_new"], T[tn][camp]) for r in rs]
                rec[camp][tn] = dl
                cells.append(f"{sum(d is not None for d in dl)}/{n}; {_km(dl)}")
        t3 = {camp: [_t3_day(r, camp, T) for r in rs] for camp in CAMPS}
        for camp in CAMPS:
            rec[camp]["T3"] = t3[camp]
        cells.append("; ".join(f"{sum(d is not None for d in t3[c])}/{n}, {_km(t3[c])}" for c in CAMPS))
        cell = [r["r4"]["cell_h"] / 24.0 for r in rs if r["r4"].get("cell_h")]
        rec["cell_days"] = cell
        rec["start_days"] = [r["r4"]["start_h"] / 24.0 for r in rs]
        cells.append(f"{np.median(cell):.0f}" if cell else "never")
        sp = [sum(r["campaigns"][c]["spent"] for c in CAMPS) for r in rs]
        rec["spent"] = sp
        cells.append(f"${np.mean(sp) / 1e3:.0f}k")
        cap = [sum(u for _, u, _ in r["r4"]["payments"]) for r in rs]
        rec["capex"] = cap
        cells.append(f"${np.mean(cap) / 1e6:.2f}M" if np.mean(cap) > 0 else "$0")
        lines.append("| " + " | ".join(cells) + " |")
        N[name][plan] = rec
    lines.append("")
    return lines


def paired_table(name, T, N):
    """Parallel against wait and against external, seed by seed: who reached each target first (a seed where one plan
    got there and the other didn't counts for the one that did), and the median of the paired differences."""
    rec = N.get(name)
    if not rec or "parallel" not in rec:
        return []
    lines = [f"**`{name}`, paired by seed** (days the parallel plan saves: the other plan's day minus the parallel "
             "plan's; seeds where only one plan reached the target count for that plan; the median is over seeds where "
             "both did)", "",
             "| Target | parallel vs wait: parallel first / other first / neither; median days saved | "
             "parallel vs external: same |", "|---|---|---|"]
    out = {}
    for camp in CAMPS:
        for tn in ("T1", "T2", "T3"):
            cells = [f"{CNAME[camp]} {tn if tn != 'T3' else 'validated T2'}"]
            for other in ("wait", "external"):
                if other not in rec:
                    cells.append("—")
                    continue
                a = dict(zip(rec["parallel"]["seeds"], rec["parallel"][camp][tn]))
                b = dict(zip(rec[other]["seeds"], rec[other][camp][tn]))
                seeds = sorted(set(a) & set(b))
                pf = sum(1 for s in seeds if a[s] is not None and (b[s] is None or a[s] < b[s]))
                of = sum(1 for s in seeds if b[s] is not None and (a[s] is None or b[s] < a[s]))
                ne = sum(1 for s in seeds if a[s] is None and b[s] is None)
                diffs = [b[s] - a[s] for s in seeds if a[s] is not None and b[s] is not None]
                med = f"{np.median(diffs):+.0f}" if diffs else "—"
                cells.append(f"{pf} / {of} / {ne}; {med} (n={len(diffs)})")
                out[f"{camp}_{tn}_vs_{other}"] = dict(parallel_first=pf, other_first=of, neither=ne,
                                                      diffs=diffs, median=(float(np.median(diffs)) if diffs else None))
            lines.append("| " + " | ".join(cells) + " |")
    N.setdefault("paired", {})[name] = out
    lines.append("")
    return lines


def money_table(name, T, N):
    """What a plan has spent by the day it reaches each target: the campaign's own discovery money (the twin's
    ledger) and the capital paid by that day (medians over the seeds that got there)."""
    P = _by_plan(_rows(name))
    if not P:
        return []
    lines = [f"**Money by the target** (`{name}`; medians over the seeds that got there: the campaign's discovery money "
             "by that day, and the capital paid by that day)", "",
             "| Plan | Al T1: discovery; capital | Al T2: same | Cu T1: same | Cu T2: same |", "|---|---|---|---|---|"]
    out = {}
    for plan in B4.PLANS:
        rs = P.get(plan)
        if not rs:
            continue
        cells = [PNAME[plan]]
        for camp in CAMPS:
            for tn in ("T1", "T2"):
                dd, uu, cc = [], [], []
                for r in rs:
                    h = B2.hit(r["campaigns"][camp]["curve_new"], T[tn][camp], 2)
                    if not h:
                        continue
                    dd.append(h[0])
                    uu.append(h[1])
                    cc.append(sum(u for t, u, _ in r["r4"]["payments"] if t <= h[0] * 24.0))
                if dd:
                    cells.append(f"${np.median(uu) / 1e3:.0f}k; ${np.median(cc) / 1e6:.2f}M (n={len(dd)})")
                else:
                    cells.append("—")
                out[f"{plan}/{camp}/{tn}"] = dict(days=dd, usd=uu, capex=cc)
        lines.append("| " + " | ".join(cells) + " |")
    N.setdefault("money_by_target", {})[name] = out
    lines.append("")
    return lines


def warm_table(name, T, N):
    """Where the parallel plan stands on the day the wait plan starts (the same seed): the data the ramp-up has
    gathered by then, which warm-starts the in-house work."""
    rec = _by_plan(_rows(name))
    if "parallel" not in rec or "wait" not in rec:
        return []
    W = {r["cfg"]["seed"]: r for r in rec["wait"]}
    lines = [f"**Warm start** (`{name}`: the parallel plan on the day the wait plan starts, same seed; means over seeds)",
             "", "| Campaign | wait plan's start (day) | parallel: alloys demonstrated by then | parallel: best by then | "
                 "parallel: seeds at or above T1 by then; T2 |", "|---|---|---|---|---|"]
    out = {}
    for camp in CAMPS:
        st, nd, bb, t1, t2 = [], [], [], 0, 0
        for r in rec["parallel"]:
            w = W.get(r["cfg"]["seed"])
            if w is None:
                continue
            S = w["r4"]["start_h"] / 24.0
            cv = [c for c in r["campaigns"][camp]["curve_new"] if c[0] <= S]
            st.append(S)
            nd.append(sum(1 for d in r["campaigns"][camp]["demonstrated"] if not d.get("ref") and d["t_h"] / 24 <= S))
            b = cv[-1][2] if cv else 0.0
            bb.append(b)
            t1 += b >= T["T1"][camp]
            t2 += b >= T["T2"][camp]
        lines.append(f"| {CNAME[camp]} | {np.mean(st):.0f} | {np.mean(nd):.1f} | {_mse(bb)} | {t1}/{len(bb)}; "
                     f"{t2}/{len(bb)} |")
        out[camp] = dict(start=st, n_demo=nd, best=bb, t1=t1, t2=t2, n=len(bb))
    N.setdefault("warm", {})[name] = out
    lines.append("")
    return lines


def build_table(N):
    rows = _rows("plans")
    rs = [r for r in rows if r["cfg"]["plan"] == "parallel"]
    if not rs:
        return []
    st = {}
    for r in rs:
        for k, v in r["r4"]["station_online"].items():
            st.setdefault(k, []).append(v / 24.0)
    lines = ["**Build-out** (days from funding to online, i.e. arrived, installed in the fitted-out room and "
             "commissioned; median and range over seeds; every lead time is a stand-in, `twin/round4.py` BUILD)", "",
             "| In-house station | online: median day (range) |", "|---|---|"]
    for k, v in sorted(st.items(), key=lambda kv: np.median(kv[1])):
        lines.append(f"| `{k}` | {np.median(v):.0f} ({min(v):.0f}-{max(v):.0f}) |")
    cell = [r["r4"]["cell_h"] / 24.0 for r in rs]
    full = [r["r4"]["full_h"] / 24.0 for r in rs]
    lines.append(f"| the cell (robots and Kardex integrated: stations run round the clock) | {np.median(cell):.0f} "
                 f"({min(cell):.0f}-{max(cell):.0f}) |")
    lines.append(f"| everything (the wait plan starts) | {np.median(full):.0f} ({min(full):.0f}-{max(full):.0f}) |")
    lines.append("")
    N["build"] = {k: dict(median=float(np.median(v)), lo=float(min(v)), hi=float(max(v))) for k, v in st.items()}
    N["build"]["cell"] = dict(median=float(np.median(cell)), lo=float(min(cell)), hi=float(max(cell)))
    N["build"]["full"] = dict(median=float(np.median(full)), lo=float(min(full)), hi=float(max(full)))
    # capital over time (the same in both building plans)
    days = (0, 30, 91, 182, 273, 365, 547, 730)
    cum = []
    for d in days:
        cum.append(float(np.mean([sum(u for t, u, _ in r["r4"]["payments"] if t <= d * 24.0) for r in rs])))
    lines += ["**Capital spend over time** (wait and parallel; external spends none; 30 % deposit on order for items of "
              "$100k or more, the rest on delivery)", "",
              "| day | " + " | ".join(str(d) for d in days) + " |", "|---" * (len(days) + 1) + "|",
              "| cumulative capital ($M) | " + " | ".join(f"{c / 1e6:.2f}" for c in cum) + " |", ""]
    N["capex_curve"] = dict(days=list(days), usd=cum)
    return lines


def _slot_cap_month(k):
    """Jobs a slot-based route can take in a month: (cap, unit), or None for a station measured in hours."""
    if k in R4.STANDING:
        n, d = R4.STANDING[k]["per_period"]
        return n / d * 30.4
    for s in R4.EXTRA:
        if s.key == k and s.per_period:
            n, d = s.per_period
            return n / d * 30.4
    if k == "atomizer":
        return 16 * 30.4 / 7.0
    if k == "ames":
        return 30.4 / 300.0
    return None


SITE_ROWS = [("atomizer", "BYU atomizer (runs / starts)"), ("utah_midi", "Utah MIDI (builds / slots)"),
             ("lpbf_3dpt", "3D Powder Tech (builds / slots)"), ("utah_midi@vcl", "In-house MIDI"),
             ("utah_mxlab", "Utah MX-Lab (sessions / slots)"), ("mines_x2", "Mines X2 (sessions / slots)"),
             ("utah_mxlab@vcl", "In-house MX-Lab"), ("valimet", "Valimet (runs / slots)"),
             ("edm", "Provo EDM service"), ("edm@vcl", "In-house EDM"), ("tensile", "BYU Instron frames"),
             ("tensile_ext", "Outside tensile lab"), ("tensile@vcl", "In-house tensile"),
             ("byu_sem", "BYU Microscopy Center"), ("byu_sem@vcl", "In-house SEM"), ("pip", "PIP service"),
             ("pip@vcl", "In-house PIP"), ("operator", "People (3, day shifts)"), ("robot", "Robots (2)")]


def utilization(name, plan, N):
    rows = [r for r in _rows(name) if r["cfg"]["plan"] == plan]
    if not rows:
        return None, []
    n_m = len(next(iter(rows[0]["r4"]["monthly"].values()))["busy"])
    U = {}
    for k, _ in SITE_ROWS:
        mats = []
        for r in rows:
            m = r["r4"]["monthly"].get(k)
            if m is None:
                continue
            cap = _slot_cap_month(k)
            u = []
            for i in range(n_m):
                if m["avail"][i] <= 0:
                    u.append(np.nan)
                elif cap is not None:
                    u.append(min(m["jobs"][i] / cap, 1.5))
                else:
                    u.append(m["busy"][i] / max(m["avail"][i], 1e-9))
            mats.append(u)
        if mats:
            U[k] = np.nanmean(np.array(mats, float), axis=0)
    N.setdefault("utilization", {})[f"{name}/{plan}"] = {k: [None if np.isnan(x) else round(float(x), 4)
                                                            for x in v] for k, v in U.items()}
    lines = [f"**Utilization by route over time** (`{name}`, {PNAME[plan]}, mean over seeds; slot routes: jobs over "
             "the slots the partner offers; stations: busy unit-hours over the calendar's unit-hours while online)", "",
             "| Route | months 1-3 | 4-6 | 7-9 | 10-12 | 13-18 | 19-24 |", "|---|---|---|---|---|---|---|"]
    for k, lab in SITE_ROWS:
        if k not in U:
            continue
        v = U[k]
        segs = [(0, 3), (3, 6), (6, 9), (9, 12), (12, 18), (18, 24)]
        cells = []
        for a, b in segs:
            x = v[a:b]
            x = x[~np.isnan(x)]
            cells.append(f"{100 * x.mean():.0f} %" if len(x) else "—")
        lines.append(f"| {lab} | " + " | ".join(cells) + " |")
    lines.append("")
    return U, lines


def route_shares(name, plan, N):
    rows = [r for r in _rows(name) if r["cfg"]["plan"] == plan]
    if not rows:
        return []
    roles = {}
    for r in rows:
        for camp, d in r["r4"]["routes"].items():
            for role, cnt in d.items():
                for st, n in cnt.items():
                    roles.setdefault((camp, role), {}).setdefault(st, 0)
                    roles[(camp, role)][st] += n
    lines = [f"**Each route's share of the jobs** (`{name}`, {PNAME[plan]}, all seeds together)", "",
             "| Campaign | Step | Routes (share of its jobs) |", "|---|---|---|"]
    keep = ("utah_midi", "utah_mxlab", "edm", "tensile", "byu_sem", "pip", "prep", "shop", "furnace", "mines_x2")
    rec = {}
    for (camp, role), cnt in sorted(roles.items()):
        if role not in keep:
            continue
        tot = sum(cnt.values())
        parts = ", ".join(f"`{k}` {100 * v / tot:.0f} %" for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]))
        lines.append(f"| {CNAME[camp]} | {role} | {parts} (n = {tot}) |")
        rec[f"{camp}/{role}"] = {k: v / tot for k, v in cnt.items()}
    # the routes that made each campaign's demonstrated alloys, and the ones at or above T1
    T = B2.targets()
    lines += ["", "| Campaign | alloys demonstrated: fabrication route (share) | at or above T1 |", "|---|---|---|"]
    for camp in CAMPS:
        allr, t1r = {}, {}
        for r in rows:
            for d in r["campaigns"][camp]["demonstrated"]:
                if d.get("ref"):
                    continue
                k = d.get("route_fab") or "?"
                allr[k] = allr.get(k, 0) + 1
                if d["u"] >= T["T1"][camp]:
                    t1r[k] = t1r.get(k, 0) + 1
        fa = lambda c: ", ".join(f"`{k}` {100 * v / max(sum(c.values()), 1):.0f} %" for k, v in
                                 sorted(c.items(), key=lambda kv: -kv[1])) + f" (n = {sum(c.values())})"
        lines.append(f"| {CNAME[camp]} | {fa(allr)} | {fa(t1r)} |")
        rec[f"{camp}/demonstrated"] = allr
        rec[f"{camp}/at_T1"] = t1r
    N.setdefault("routes", {})[f"{name}/{plan}"] = rec
    lines.append("")
    return lines


def first_route_table(name, T, N):
    """The route that made (fabricated and tested) the first alloy at each target, seed by seed: each route's share of
    the discoveries themselves rather than of the jobs."""
    P = _by_plan(_rows(name))
    if not P:
        return []
    lines = [f"**Which route made the first alloy at each target** (`{name}`; seeds that got there; fabrication route, "
             "then testing route)", "", "| Plan | Al T1 | Al T2 | Cu T1 | Cu T2 |", "|---|---|---|---|---|"]
    out = {}
    for plan in B4.PLANS:
        rs = P.get(plan)
        if not rs:
            continue
        cells = [PNAME[plan]]
        for camp in CAMPS:
            for tn in ("T1", "T2"):
                cnt = {}
                for r in rs:
                    for d in r["campaigns"][camp]["demonstrated"]:
                        if d.get("ref") or d["u"] < T[tn][camp] - 1e-12:
                            continue
                        k = f"{d.get('route_fab') or '?'} / {d.get('route_test') or '?'}"
                        cnt[k] = cnt.get(k, 0) + 1
                        break
                cells.append(", ".join(f"{k} ×{v}" for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])) or "—")
                out[f"{plan}/{camp}/{tn}"] = cnt
        lines.append("| " + " | ".join(cells) + " |")
    N.setdefault("first_route", {})[name] = out
    lines.append("")
    return lines


def stages_table(name, N):
    rows = _rows(name)
    if not rows:
        return []
    P = _by_plan(rows)
    lines = [f"**The stages after discovery** (`{name}`; per run: alloys that entered, failed the validation network, "
             "were validated through the full-part test; scale-up money)", "",
             "| Plan | Al entered; failed network; validated | Cu entered; failed network; validated | "
             "scale-up spend (both) |", "|---|---|---|---|"]
    rec = {}
    for plan in B4.PLANS:
        rs = P.get(plan)
        if not rs:
            continue
        cells = [PNAME[plan]]
        for camp in CAMPS:
            ent = fail = val = 0
            for r in rs:
                st = r["r4"]["stages"][camp]
                ent += len(st["done"]) + (1 if st["open"] else 0)
                fail += sum(1 for d in st["done"] if d["result"] == "failed network")
                val += sum(1 for d in st["done"] if d["result"] == "validated")
            cells.append(f"{ent / len(rs):.1f}; {fail / len(rs):.1f}; {val / len(rs):.1f}")
            rec[f"{plan}/{camp}"] = dict(entered=ent / len(rs), failed=fail / len(rs), validated=val / len(rs))
        usd = np.mean([sum(r["r4"]["stages"][c]["usd"] for c in CAMPS) for r in rs])
        cells.append(f"${usd / 1e3:.0f}k")
        lines.append("| " + " | ".join(cells) + " |")
    N.setdefault("stages", {})[name] = rec
    lines.append("")
    return lines


def variant_table(name, T, N, label):
    """Second-priority experiments: each variant against the same plan in `plans` on the same seeds (paired): the
    variant's Kaplan-Meier median day and the base's on those seeds, and the seeds where the variant got there first
    or later."""
    rows = _rows(name)
    if not rows:
        return []
    bases = {}
    for r in _rows("plans"):
        bases.setdefault(r["cfg"]["plan"], {})[r["cfg"]["seed"]] = r
    groups = {}
    for r in rows:
        groups.setdefault(B4.group_key(r["cfg"]), []).append(r)
    lines = [f"**{label}** (`{name}`; each against the same plan in `plans` on the same seeds: the variant's median "
             "day → the base's on those seeds (variant first / later); final alloy paired, variant − base)", "",
             "| Variant | n | Al T1 | Al T2 | Cu T1 | Cu T2 | Al best | Cu best |", "|---|---|---|---|---|---|---|---|"]
    rec = {}
    for key, rs in sorted(groups.items()):
        rs.sort(key=lambda r: r["cfg"]["seed"])
        n = len(rs)
        base = bases.get(rs[0]["cfg"]["plan"], {})
        rb = [base[r["cfg"]["seed"]] for r in rs if r["cfg"]["seed"] in base]
        cells = [f"`{key.replace('r4_', '')}`", str(n)]
        rr = {}
        for camp, tn in (("flaime_al", "T1"), ("flaime_al", "T2"), ("onr_cu", "T1"), ("onr_cu", "T2")):
            dv = [_hit_day(r["campaigns"][camp]["curve_new"], T[tn][camp]) for r in rs]
            db = [_hit_day(r["campaigns"][camp]["curve_new"], T[tn][camp]) for r in rb]
            first = sum(1 for x, y in zip(dv, db) if x is not None and (y is None or x < y - 1e-9))
            later = sum(1 for x, y in zip(dv, db) if y is not None and (x is None or y < x - 1e-9))
            cells.append(f"{_km(dv)} → {_km(db)} ({first} / {later})")
            rr[f"{camp}_{tn}"] = dict(variant=dv, base=db, first=first, later=later)
        for camp in CAMPS:
            pd = [r["campaigns"][camp]["best_new"] - b["campaigns"][camp]["best_new"] for r, b in zip(rs, rb)]
            cells.append(_mse(pd) if pd else "—")
            rr[f"{camp}_paired"] = pd
        lines.append("| " + " | ".join(cells) + " |")
        rec[key] = rr
    N.setdefault("variants", {})[name] = rec
    lines.append("")
    return lines


def provenance_table(T, N):
    """Provenance on and off at each offset level, paired by seed: days saved to each target, the change in the final
    alloy, and the visits' cost; the visit pays when the days it saves are worth more than it costs."""
    rows = _rows("provenance")
    if not rows:
        return []
    by = {}
    for r in rows:
        o = r["cfg"]["opts"]
        by.setdefault(float(o.get("offset_mult", 1.0)), {}).setdefault("on" if o.get("provenance") else "off", {})[
            r["cfg"]["seed"]] = r
    lines = ["**Provenance: when it pays** (`provenance`, the parallel plan with the cheap policies; someone on site "
             "at each partner's first job; paired by seed at each offset level; 'days saved' are the seeds' paired "
             "differences where both reached the target, and the count of seeds that got there first)", "",
             "| Offset level (× the stand-in σ) | n | Al T2 days saved: median (first / later) | Cu T1 | Cu T2 | "
             "Al best (on − off) | Cu best (on − off) | visits' cost |", "|---|---|---|---|---|---|---|---|"]
    out = {}
    for m in sorted(by):
        on, off = by[m].get("on", {}), by[m].get("off", {})
        seeds = sorted(set(on) & set(off))
        if not seeds:
            continue
        cells = [f"{m:g}", str(len(seeds))]
        rec = {}
        for camp, tn in (("flaime_al", "T2"), ("onr_cu", "T1"), ("onr_cu", "T2")):
            a = [_hit_day(on[s_]["campaigns"][camp]["curve_new"], T[tn][camp]) for s_ in seeds]
            b = [_hit_day(off[s_]["campaigns"][camp]["curve_new"], T[tn][camp]) for s_ in seeds]
            diffs = [y - x for x, y in zip(a, b) if x is not None and y is not None]
            first = sum(1 for x, y in zip(a, b) if x is not None and (y is None or x < y))
            later = sum(1 for x, y in zip(a, b) if y is not None and (x is None or y < x))
            cells.append(f"{np.median(diffs):+.0f} ({first} / {later})" if diffs else f"— ({first} / {later})")
            rec[f"{camp}_{tn}"] = dict(diffs=diffs, first=first, later=later)
        for camp in CAMPS:
            d = [on[s_]["campaigns"][camp]["best_new"] - off[s_]["campaigns"][camp]["best_new"] for s_ in seeds]
            cells.append(_mse(d))
            rec[f"{camp}_best"] = d
        cost = np.mean([sum(on[s_]["campaigns"][c].get("prov_usd", 0.0) for c in CAMPS) for s_ in seeds])
        cells.append(f"${cost / 1e3:.1f}k")
        rec["cost"] = float(cost)
        lines.append("| " + " | ".join(cells) + " |")
        out[str(m)] = rec
    N["provenance"] = out
    lines.append("")
    return lines


# ------------------------------------------------------------------------------------------------- figures
def fig_best(names, T):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = [n for n in names if _rows(n)]
    if not names:
        return
    fig, axes = plt.subplots(len(names), 2, figsize=(11, 3.6 * len(names)), squeeze=False)
    grid = np.arange(0, B4.DAYS + 1, 5)
    for i, name in enumerate(names):
        P = _by_plan(_rows(name))
        for j, camp in enumerate(CAMPS):
            ax = axes[i, j]
            _style(ax)
            for plan in B4.PLANS:
                rs = P.get(plan)
                if not rs:
                    continue
                M = []
                for r in rs:
                    cv = r["campaigns"][camp]["curve_new"]
                    y = np.zeros_like(grid, float)
                    for d, _, u in cv:
                        y[grid >= d] = np.maximum(y[grid >= d], u)
                    M.append(y)
                M = np.array(M)
                med = np.median(M, axis=0)
                ax.fill_between(grid, np.percentile(M, 25, axis=0), np.percentile(M, 75, axis=0),
                                color=PCOL[plan], alpha=0.15, lw=0)
                ax.plot(grid, med, color=PCOL[plan], lw=2, label=f"{PNAME[plan]} (n={len(rs)})")
                if plan == "wait":
                    st = np.median([r["r4"]["start_h"] / 24.0 for r in rs])
                    ax.axvline(st, color=PCOL[plan], lw=1, ls=":")
                    ax.text(st + 5, 0.03, f"cell complete,\nwait starts (day {st:.0f})", color=INK2, fontsize=7)
            for tn, ls in (("T1", "--"), ("T2", "-.")):
                ax.axhline(T[tn][camp], color=INK2, lw=0.8, ls=ls)
                ax.text(B4.DAYS - 5, T[tn][camp] + 0.01, tn, color=INK2, fontsize=7, ha="right")
            ax.set_xlim(0, B4.DAYS)
            ax.set_ylim(0, 0.85)
            ax.set_xlabel("days from the funding", color=INK2, fontsize=8)
            ax.set_ylabel("best new alloy (true utility)", color=INK2, fontsize=8)
            pol = B4.ALIAS.get(_rows(name)[0]["cfg"]["policy"], "").split("+")[0 if camp == "flaime_al" else 1]
            money = _rows(name)[0]["cfg"].get("money", 1.0)
            ax.set_title(f"{CNAME[camp]}: {pol}, money ×{money:g} ({name})", color=INK, fontsize=9, loc="left")
            if i == 0 and j == 0:
                ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.suptitle("Round 4: best new alloy against days from the funding (median over seeds; band: 25th-75th "
                 "percentile)", fontsize=10, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "twin4_best_vs_days.png", dpi=130)
    plt.close(fig)


def fig_targets(N):
    import matplotlib.pyplot as plt
    names = [n for n in ("plans_best", "plans", "plans_3x") if n in N and N[n]]
    if not names:
        return
    nrow = sum(len([p for p in B4.PLANS if N[n].get(p)]) * 2 for n in names)
    fig, axes = plt.subplots(1, 2, figsize=(12, 0.28 * nrow + 1.6), squeeze=False, sharey=True)
    for j, camp in enumerate(CAMPS):
        ax = axes[0, j]
        _style(ax)
        ticks, labels, y = [], [], 0.0
        for name in names:
            pol = B4.ALIAS.get(B4.load(name)[0]["cfg"]["policy"], "")
            money = B4.load(name)[0]["cfg"].get("money", 1.0)
            for tn in ("T1", "T2"):
                for plan in B4.PLANS:
                    rec = N[name].get(plan)
                    if not rec:
                        continue
                    dl = rec[camp][tn]
                    hit = [d for d in dl if d is not None]
                    miss = sum(d is None for d in dl)
                    rng = np.random.default_rng(int(y * 10) + 7)
                    ax.scatter(hit, y + rng.uniform(-0.2, 0.2, len(hit)), s=14, color=PCOL[plan], alpha=0.9,
                               edgecolor="white", lw=0.5, zorder=3)
                    if miss:
                        ax.scatter([B4.DAYS + 20] * miss, y + rng.uniform(-0.2, 0.2, miss), s=14, facecolor="none",
                                   edgecolor=PCOL[plan], lw=1, zorder=3)
                    km = B3.km_median(dl, B4.DAYS)
                    if km is not None:
                        ax.plot([km, km], [y - 0.32, y + 0.32], color=INK, lw=1.6, zorder=4)
                    ticks.append(y)
                    labels.append(f"{name} (money ×{money:g}) · {tn} · {PNAME[plan]}")
                    ax.text(B4.DAYS + 38, y, f"{len(hit)}/{len(dl)}", fontsize=6.5, color=INK2, va="center")
                    y += 1
                y += 0.4
            y += 0.6
        ax.set_yticks(ticks)
        ax.set_yticklabels(labels, fontsize=6.5)
        ax.set_xlim(0, B4.DAYS + 70)
        ax.set_ylim(y, -0.8)
        ax.set_xlabel("days from the funding", color=INK2, fontsize=7.5)
        ax.set_title(CNAME[camp], color=INK, fontsize=9, loc="left")
    fig.suptitle("Round 4: days from the funding to each target, each seed a mark (blue: wait for the cell; orange: "
                 "ramp up in parallel; green: external routes only). Open marks at the right: not reached in two "
                 "years; black bar: Kaplan-Meier median; at the right: seeds that got there", fontsize=8.5, color=INK,
                 x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "twin4_time_to_target.png", dpi=130)
    plt.close(fig)


def fig_money(N):
    import matplotlib.pyplot as plt
    rows = _rows("plans")
    if not rows:
        return
    P = _by_plan(rows)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
    days = np.arange(0, B4.DAYS + 1, 7)
    ax = axes[0]
    _style(ax)
    for plan in B4.PLANS:
        rs = P.get(plan)
        if not rs:
            continue
        cum = np.array([[sum(u for t, u, _ in r["r4"]["payments"] if t <= d * 24.0) for d in days] for r in rs])
        ax.plot(days, cum.mean(axis=0) / 1e6, color=PCOL[plan], lw=2, label=PNAME[plan],
                ls="-" if plan != "parallel" else "--")
    ax.set_title("Capital spent (the cell; mean over seeds)", color=INK, fontsize=9, loc="left")
    ax.set_ylabel("$M, cumulative", color=INK2, fontsize=8)
    ax.set_xlabel("days from the funding", color=INK2, fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    _style(ax)
    for plan in B4.PLANS:
        rs = P.get(plan)
        if not rs:
            continue
        cur = []
        for r in rs:
            tot = np.zeros(len(days))
            for camp in CAMPS:
                sc = dict((d, u) for d, u in r["campaigns"][camp]["spend_curve"])
                tot += np.array([sc.get(int(d), np.nan) for d in days])
            cur.append(tot)
        ax.plot(days, np.nanmean(np.array(cur), axis=0) / 1e3, color=PCOL[plan], lw=2, label=PNAME[plan])
    ax.set_title("Discovery money spent (both campaigns; the same budget in every plan)", color=INK, fontsize=9,
                 loc="left")
    ax.set_ylabel("$k, cumulative", color=INK2, fontsize=8)
    ax.set_xlabel("days from the funding", color=INK2, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "twin4_money.png", dpi=130)
    plt.close(fig)


def fig_utilization(U, title, fn):
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    if not U:
        return
    keys = [k for k, _ in SITE_ROWS if k in U]
    labs = [l for k, l in SITE_ROWS if k in U]
    M = np.array([U[k] for k in keys], float)[:, :int(B4.DAYS // 30.4)]          # whole months only
    cmap = LinearSegmentedColormap.from_list("blue", ["#cce3fd", "#84b9f3", "#338ced", "#1b64be", "#0e3d7e"])
    cmap.set_bad("#f2f2f2")
    fig, ax = plt.subplots(figsize=(11, 0.32 * len(keys) + 1.4))
    im = ax.imshow(np.clip(M, 0, 1), aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels(labs, fontsize=7, color=INK2)
    ax.set_xticks(range(M.shape[1]))
    ax.set_xticklabels([str(i + 1) for i in range(M.shape[1])], fontsize=7, color=INK2)
    ax.set_xlabel("month from the funding (grey: not online; a slot route can pass 100 % in a month when a session "
                  "falls in it that the yearly average spreads thinner)", color=INK2, fontsize=8)
    for s in ax.spines.values():
        s.set_visible(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            if not np.isnan(M[i, j]) and M[i, j] >= 0.005:
                ax.text(j, i, f"{100 * M[i, j]:.0f}", ha="center", va="center", fontsize=5.5,
                        color="#ffffff" if M[i, j] > 0.45 else INK)
    cb = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.01)
    cb.ax.tick_params(labelsize=7, colors=INK2)
    cb.set_label("utilization", fontsize=7, color=INK2)
    ax.set_title(title, color=INK, fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / fn, dpi=130)
    plt.close(fig)


def fig_timeline(T):
    """Seed 0 of the parallel plan: the build-out (lead, installation, commissioning) of every in-house station, the
    jobs each route took per month, and when each campaign reached its targets."""
    import matplotlib.pyplot as plt
    rows = [r for r in _rows("plans") if r["cfg"]["plan"] == "parallel" and r["cfg"]["seed"] == 0]
    if not rows:
        return
    r = rows[0]
    b = r["r4"]["build"]
    st_items = R4.STATION_ITEMS
    fig, axes = plt.subplots(2, 1, figsize=(11, 8.5), gridspec_kw=dict(height_ratios=[1.15, 1]), sharex=True)
    ax = axes[0]
    _style(ax)
    order = sorted(st_items, key=lambda k: r["r4"]["station_online"][k])
    rows_b = [("room (fit-out)", ["services"])] + [(k.replace("@vcl", ""), list(st_items[k])) for k in order] + \
        [("the cell (robots, Kardex, integration)", list(R4.CELL))]
    for i, (lab, its) in enumerate(rows_b):
        its = [x for x in its if x in b]
        if not its:
            continue
        arr = max(b[x]["arrive_h"] for x in its) / 24.0
        ins = max(b[x]["install_h"] for x in its) / 24.0
        com = max(b[x]["commission_h"] for x in its) / 24.0
        onl = max(b[x]["online_h"] for x in its) / 24.0
        if lab.startswith("the cell"):
            onl = r["r4"]["cell_h"] / 24.0
        ax.barh(i, arr, color="#e7e7e7", height=0.6)
        if ins > arr:
            ax.barh(i, ins - arr, left=arr, color="#f2a600", height=0.6, alpha=0.5)
        ax.barh(i, com - ins, left=ins, color="#f2a600", height=0.6)
        ax.barh(i, onl - com, left=com, color="#6a4ce2", height=0.6)
        ax.barh(i, B4.DAYS - onl, left=onl, color="#257de0", height=0.25, alpha=0.35)
    ax.set_yticks(range(len(rows_b)))
    ax.set_yticklabels([l for l, _ in rows_b], fontsize=7, color=INK2)
    ax.invert_yaxis()
    ax.set_title("Build-out (seed 0): grey, on order; light yellow, waiting for the room; yellow, installing; violet, "
                 "commissioning; blue, online", color=INK, fontsize=8.5, loc="left")
    ax2 = axes[1]
    _style(ax2)
    mon = r["r4"]["monthly"]
    keys = [k for k, _ in SITE_ROWS if k in mon and k not in ("operator", "robot")]
    labs = {k: l for k, l in SITE_ROWS}
    for i, k in enumerate(keys):
        jobs = mon[k]["jobs"]
        mx = max(max(jobs), 1)
        for m, n in enumerate(jobs):
            if n:
                ax2.add_patch(plt.Rectangle((m * 30.4, i - 0.4 * n / mx), 30.4 - 1, 0.8 * n / mx,
                                            color="#257de0" if "@vcl" in k else "#f47230" if k != "atomizer"
                                            else "#00b894"))
        ax2.text(B4.DAYS + 4, i, f"max {mx}/month", fontsize=6, color=INK2, va="center")
    for camp, mk in (("flaime_al", "o"), ("onr_cu", "s")):
        for tn in ("T1", "T2"):
            d = _hit_day(r["campaigns"][camp]["curve_new"], T[tn][camp])
            if d is not None:
                ax2.axvline(d, color=INK, lw=0.8, ls="--" if tn == "T1" else "-.")
                ax2.text(d + 2, -0.9 if camp == "flaime_al" else len(keys) - 0.2,
                         f"{'Al' if camp == 'flaime_al' else 'Cu'} {tn}, day {d:.0f}", fontsize=6.5, color=INK)
    ax2.set_yticks(range(len(keys)))
    ax2.set_yticklabels([labs[k] for k in keys], fontsize=7, color=INK2)
    ax2.set_ylim(len(keys) - 0.3, -1.3)
    ax2.set_xlim(0, B4.DAYS + 60)
    ax2.set_xlabel("days from the funding", color=INK2, fontsize=8)
    ax2.set_title("Jobs per month on each route (bar height relative to the route's busiest month; orange: partner "
                  "or BYU, green: the atomizer, blue: in house)", color=INK, fontsize=8.5, loc="left")
    fig.tight_layout()
    fig.savefig(FIG / "twin4_timeline.png", dpi=130)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    T = B2.targets()
    N = dict(targets=T)
    L = ["# Round 4: tables", "", "Generated by `python -m twin.figures4` from `out/twin4/runs/*.jsonl`. Everything is "
         "simulated. Targets: T1 = state of the art (Al " + f"{T['T1']['flaime_al']:.3f}, Cu {T['T1']['onr_cu']:.3f}), "
         f"T2 = halfway to the oracle's best (Al {T['T2']['flaime_al']:.3f}, Cu {T['T2']['onr_cu']:.3f}); a "
         "validated T2 alloy is one at or above T2 that has been through the gas lot, the validation network and its "
         "full-part test.", ""]
    L += ["## 1. The three plans", ""]
    for name in ("plans", "plans24", "plans_3x", "plans_best"):
        L += plan_table(name, T, N)
        L += paired_table(name, T, N)
        L += money_table(name, T, N)
        L += warm_table(name, T, N)
    L += ["## 2. Build-out and capital", ""]
    L += build_table(N)
    L += ["## 3. Utilization and routes", ""]
    U, lu = utilization("plans", "parallel", N)
    L += lu
    U3, lu3 = utilization("plans_3x", "parallel", N)
    L += lu3
    Ue, lue = utilization("plans", "external", N)
    L += lue
    L += first_route_table("plans", T, N)
    L += first_route_table("plans_best", T, N)
    L += route_shares("plans", "parallel", N)
    L += route_shares("plans_3x", "parallel", N)
    L += route_shares("plans_best", "parallel", N)
    L += ["## 4. The stages after discovery", ""]
    for name in ("plans", "plans_3x", "plans_best"):
        L += stages_table(name, N)
    L += ["## 5. Second priority", ""]
    L += variant_table("routes", T, N, "One partner route taken away at a time")
    L += provenance_table(T, N)
    L += variant_table("nolearn", T, N, "No learning curve (every station at full rate once commissioned)")
    (FIG / "tables.md").write_text("\n".join(L) + "\n")
    (FIG / "numbers.json").write_text(json.dumps(B2._jsonable(N), indent=1))
    try:
        fig_best(["plans", "plans_3x", "plans_best"], T)
        fig_targets(N)
        fig_money(N)
        fig_utilization(U, "Utilization by route and month: ramp up in parallel (plans, money ×1, mean over seeds; "
                           "slot routes: jobs over slots)", "twin4_utilization.png")
        fig_utilization(U3, "Utilization by route and month: ramp up in parallel (plans_3x, money ×3)",
                        "twin4_utilization_3x.png")
        fig_timeline(T)
    except Exception:
        import traceback
        traceback.print_exc()
    print("\n".join(L[:60]))


if __name__ == "__main__":
    main()

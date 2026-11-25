"""The campaign trace: one JSON file with every event of a twin run, the samples they served, what came of each, and
the optimizer's state at every iteration. Schema: out/twin2/trace/README.md.

    python -m twin.trace run [policy] [facility] [seed]   # one traced run -> out/twin2/trace/<run_id>.json
    python -m twin.trace check <trace.json>              # schema and consistency checks, printed

A traced run is an ordinary run (``Twin(..., trace=True)`` only records; tests/test_trace.py checks a traced and an
untraced run give the same results). ``twin.bench2`` writes a trace for every run whose config has ``trace=True``.

What it adds to the event log (``Twin.event_log``):
* each booking's **outcome**, in the node-level ledger DAL #274 proposes (Ax's trial statuses, per node);
* each booking's **step in the workflow network of DAL #211**;
* the **samples** (lots, builds, deposits, E8 plates), their parents, and how each ended;
* the **iterations**: what the policy proposed, the acquisition value it gave each proposal and why, its incumbent
  (the best utility it has measured) and the hidden best so far;
* the **literature searches** the campaign would run, each pointing at an Edison result already posted in DAL (no
  new queries are sent);
* the **seed set** (DAL #275) and the **weekly atomizer runs** against DAL #256's three a week.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("TWIN_OUT", HERE.parent / "out" / "twin2")) / "trace"
SCHEMA = "vertical-lab campaign trace v1"
H = 24.0

# --------------------------------------------------------------------------------------------- the workflow network
# Each booking is (campaign, twin node, station). STEPS gives its step name here and its node in DAL #211's network
# (ONR YIP Fig. 1, "the full workflow network": the TikZ in near-term-submissions/onr-yip/onr-yip-technical-proposal-
# cu-ded.tex L206-L275 at DAL b4d5a89, the head of DAL PR 215). The figure draws the copper/DED workflow only, so an
# aluminium booking gets the same node where the step is the same one (charge, atomize, microscopy, tensile) and None
# where the figure has no such step (LPBF builds, Archimedes density, PIP, heat treatment, hot tensile, XRD, XRF,
# ICP-MS, the blend doser). Where the figure folds a step into a node's time (sieving into "Atomize", EDM and
# machining into "Tensile") the booking gets that node.
DAL211_SOURCE = ("https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/b4d5a89/near-term-submissions/onr-yip/"
                 "onr-yip-technical-proposal-cu-ded.tex#L206-L275")
DAL211: dict = {
    "comp": ("composition: Ni, Al, Fe, Mn; Cr, Si, Nb, Ti in Cu-Ni", "input"),
    "atom": ("atomizer settings", "input"),
    "dep": ("deposition settings: laser power, travel speed, feed rate", "input"),
    "p1": ("CALPHAD and heat flow", "model"),
    "p2": ("Charge", "process"),
    "p3": ("Atomize", "process"),
    "p4": ("Small DED, Utah", "process"),
    "p5": ("Large DED, Mines", "process"),
    "p6": ("Microscopy", "characterization"),
    "t1": ("Tensile", "test"),
    "t2": ("Seawater screen", "test"),
    "t3": ("Immersion", "test"),
    "t4": ("Repair coupon", "test"),
    "feedback": ("each result updates the models, which choose the next step by expected gain per cost", "decision"),
}
DAL211_EDGES = [("p1", "p2"), ("p2", "p3"), ("p3", "p4"), ("p4", "p5"), ("p5", "p6"), ("p6", "t1"), ("p6", "t2"),
                ("p6", "t4"), ("t2", "t3"), ("comp", "p1"), ("comp", "p2"), ("atom", "p3"), ("dep", "p4"),
                ("dep", "p5"), ("t4", "feedback"), ("feedback", "p1")]
STEPS: dict = {
    (None, "sim", "hpc"): ("CALPHAD or heat-flow simulation", "p1"),
    (None, "powder", "shop"): ("machine the charge cups and plugs", "p2"),
    (None, "powder", "doser"): ("dose the charge and press the plug", "p2"),
    (None, "powder", "atomizer"): ("atomize (rePOWDER, ultrasonic)", "p3"),
    (None, "powder", "sieve"): ("sieve the lot", "p3"),
    (None, "powder", "psd"): ("powder size and flow", "p3"),
    (None, "powder", "byu_sem"): ("powder SEM and EDS", "p3"),
    (None, "powder", "xrd"): ("powder XRD", None),
    (None, "powder", "xrf"): ("powder XRF", None),
    (None, "powder", "byu_icpms"): ("powder ICP-MS", None),
    (None, "nsl", "nsl"): ("outside O, C and composition (NSL Analytical)", "p3"),
    (None, "print", "utah_midi"): ("LPBF build (Aconity MIDI)", None),
    (None, "print", "density"): ("Archimedes density of the build's cubes", None),
    (None, "print", "byu_sem"): ("SEM of a polished cube section", "p6"),
    (None, "section", "prep"): ("section, mount and polish", "p6"),
    (None, "section", "byu_sem"): ("SEM, EDS and EBSD of the section", "p6"),
    (None, "section", "hardness"): ("micro-Vickers row", None),
    (None, "section", "xrd"): ("XRD of the section (beta-prime)", "p6"),
    (None, "pip", "furnace"): ("heat treatment before PIP", None),
    (None, "pip", "prep"): ("PIP surface prep", None),
    (None, "pip", "pip"): ("PIP (profilometry-based indentation plastometry)", None),
    (None, "test", "utah_midi"): ("E8 plate build (LPBF)", None),
    (None, "test", "edm"): ("wire EDM the bars off the plate", "t1"),
    (None, "test", "furnace"): ("heat treat the bars", "t1"),
    (None, "test", "shop"): ("machine the tensile bars", "t1"),
    (None, "test", "tensile"): ("room-temperature tensile", "t1"),
    (None, "test", "tensile_hot"): ("elevated-temperature tensile", None),
    (None, "ded_small", "doser"): ("blend elemental powders for a DED screen", None),
    (None, "ded_small", "utah_mxlab"): ("small DED deposit (MX-Lab)", "p4"),
    (None, "ded_small", "byu_sem"): ("SEM of the deposit", "p6"),
    (None, "ded_large", "utah_mxlab"): ("1 kg DED deposit (MX-Lab)", "p5"),
    (None, "ded_large", "mines_x2"): ("2 kg DED deposit (FormAlloy X2, Mines)", "p5"),
    (None, "ded_large", "byu_sem"): ("SEM of the large deposit", "p6"),
    (None, "tensile", "shop"): ("machine bars from the deposit", "t1"),
    (None, "tensile", "tensile"): ("tensile of the deposit's bars", "t1"),
    (None, "screen", "cubxl"): ("seawater corrosion screen (CubXL: OCP, LPR, EIS, CP)", "t2"),
    (None, "screen", "byu_icpms"): ("ICP-MS of the screen's electrolyte", "t2"),
    (None, "immersion", "immersion"): ("30-day immersion", "t3"),
    (None, "immersion", "byu_sem"): ("SEM of the immersion coupon", "t3"),
    (None, "immersion", "byu_icpms"): ("ICP-MS of the immersion solution", "t3"),
}


def step_of(campaign, node, station, what):
    """(step label, DAL #211 node id or None) for one booking."""
    for key in ((campaign, node, station), (None, node, station), (campaign, node, None), (None, node, None)):
        if key in STEPS:
            return STEPS[key]
    return (f"{node or what} at {station}", None)


# ------------------------------------------------------------------------------------------------- literature steps
# Where a campaign would run a literature search, and the Edison result already posted in DAL that answers it (no new
# query is sent, so the step takes no lab time). Each is keyed by the decision it informs and fires at its trigger:
# "start" (day 0, before the first proposal), "first_new_element" (the first accepted design with one of ``elements``),
# "first_result" (the first ``result``: build, test, screen or immersion) or "first_promotion" (the first part sent on
# to the dear step). From DAL's committed Edison answers (paths at their commits).
_D = "https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/"
LITERATURE: dict = {
    "flaime_al": {
        "the design box: each element's cap": dict(
            when="start", question="Conservative and non-conservative wt% bounds for Al plus 15 solutes in an LPBF "
                                   "BOFN space", dal211="p1",
            edison=_D + "115a99ab2c6dbca50ff94b63738014847e7b5d9d/edison-trajectories/element-bounds/"
                        "01_simultaneous_all_bounds.md"),
        "the seed set: how many seeds, which kinds": dict(
            when="start", question="Critically review a seeding plan (baselines, agent picks, space-filling) for a "
                                   "BOFN LPBF aluminium campaign (DAL #275 q1)",
            edison=_D + "ce394072f58aaedbbd72c688cbf597ac09cb6303/bofn-seeding/edison/q1-seeding-strategy/answer.md"),
        "the seed alloys: crack-free Sc-free baselines and data for each node": dict(
            when="start", question="Which crack-free Sc-free or Sc-lean LPBF Al alloys should be seeds, and which "
                                   "datasets can seed each BOFN stage (DAL #275 q2)",
            edison=_D + "ce394072f58aaedbbd72c688cbf597ac09cb6303/bofn-seeding/edison/q2-seed-alloys-and-data/"
                        "answer.md"),
        "the charge: powder in 6063 cups for the rePOWDER": dict(
            when="start", question="Critically check a powder-in-6063-cup charge design for the AMAZEMET rePOWDER "
                                   "(crucible, Si dissolution, vent, BN, oxygen pickup) (DAL #222)", dal211="p2",
            edison=_D + "14d236c258fa11284420a054c2192d83feb57149/outputs/issue-222-edison-doublecheck/"
                        "literature_answer.md"),
        "the mineral-lean target": dict(
            when="start", question="Is FLAIME's mineral-lean discovery-yield KPI realistic and well defined?",
            edison=_D + "535d3dda4cd244e770ffdfe4d505a30437fb277e/edison-trajectories/"
                        "edison-kpi1-discovery_yield-review.md"),
        "a nucleant against hot cracking (Zr, Sc, Er, Ti)": dict(
            when="first_new_element", elements=["Zr", "Sc", "Er", "Ti"],
            question="Quantitative LPBF solidification-cracking data for Al alloys, the widest crack-free windows and "
                     "the most effective grain refiners (TiB2, TiC, ZrH2, Sc/Zr)", dal211="p1",
            edison=_D + "535d3dda4cd244e770ffdfe4d505a30437fb277e/edison-trajectories/pareto-am-al-alloys/"
                        "batch3_process_property.md"),
        "the print's process window": dict(
            when="first_result", result="build",
            question="LPBF parameter windows (power, speed, hatch, layer, VED) giving > 99.5 % density for AlSi10Mg, "
                     "Scalmalloy, Al-Cu and Al-Zn-Mg-Cu",
            edison=_D + "535d3dda4cd244e770ffdfe4d505a30437fb277e/edison-trajectories/pareto-am-al-alloys/"
                        "batch3_process_property.md"),
        "powder reuse: how many builds a lot can serve": dict(
            when="first_result", result="build",
            question="Required LPBF aluminium powder characteristics and the quantitative effects of powder reuse",
            edison=_D + "535d3dda4cd244e770ffdfe4d505a30437fb277e/edison-trajectories/pareto-am-al-alloys/"
                        "batch3_process_property.md"),
        "the strength-ductility bar for bars": dict(
            when="first_promotion",
            question="Ranking of AM aluminium alloy systems by simultaneous strength and ductility", dal211="t1",
            edison=_D + "535d3dda4cd244e770ffdfe4d505a30437fb277e/edison-trajectories/pareto-am-al-alloys/"
                        "batch1_core_mechanical.md"),
    },
    "onr_cu": {
        "the design box: the Cu-Ni and NAB palette and its bounds": dict(
            when="start", question="Which elements and wt% bounds should the copper DED palette (Cu-Ni and NAB "
                                   "families) use, with multi-element constraints?", dal211="p1",
            edison=_D + "d1ca727fb37fa044cbcf78c420e17aa1ac827bc5/edison-trajectories/cu-ded-elements-2026-10/"
                        "phase1/joint-shortlist.md"),
        "the atomizer's temperature limit for copper": dict(
            when="start", question="What is the AMAZEMET rePOWDER induction module's real maximum temperature, and "
                                   "which alloys can it atomize?", dal211="p3",
            edison=_D + "535d3dda4cd244e770ffdfe4d505a30437fb277e/edison-trajectories/"
                        "ultrasonic-atomization-temperature-assessment.md"),
    },
}


# ------------------------------------------------------------------------------------------------------ outcomes
OUTCOMES = {
    "COMPLETED": "ran and measured (whatever the value)",
    "FAILED": "did not produce its output for a reason outside the inputs (equipment, chance); may be retried; "
              "the node gets no data point",
    "ABANDONED": "did not produce a usable output because of its inputs (a cold melt that drips, a cracked or porous "
                 "part); a viability label 0 at that node's inputs",
    "EARLY_STOPPED": "a usable part the policy chose not to take further (partial evaluation); upstream data kept",
    "STALE": "proposed but never run (refused for budget, or still queued at the horizon)",
    "NOT_AS_PLANNED": "ran, but what was made differs from the design (e.g. Mg boiled off); fit on the executed values",
    "DOWN": "a station breakdown; bookings wait for the repair, none fail",
}
P_FAIL_BASE = 0.06          # twin/physics.py: the atomizer's drip rate at good settings (chance, not the inputs)


def _r(x, n=4):
    if x is None:
        return None
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    try:
        return round(float(x), n)
    except (TypeError, ValueError):
        return x


def _summ(m: dict, keys) -> dict:
    return {k: _r(m.get(k)) for k in keys if m.get(k) is not None}


def _ref_flags(campaign_obj):
    from twin import spaces as SP
    k = campaign_obj.key
    refs = [{e: w.get(e, 0.0) for e in SP.SPACES[k].elements} for w in SP.REFERENCE[k].values()]
    flags = {}
    for i, d in campaign_obj.designs.items():
        comp = d["composition"]
        flags[i] = any(all(abs(comp.get(e, 0.0) - r[e]) < 0.06 for e in r) for r in refs)
    return flags


# --------------------------------------------------------------------------------------------------- the builder
def build(tw, cfg: dict, run_id: str, seeds: dict | None = None) -> dict:
    """The trace of a finished traced run (``tw = Twin(..., trace=True); tw.run()``)."""
    from twin import spaces as SP
    log = tw.event_log(meta=dict(cfg=cfg, run_id=run_id))
    camps = tw.campaigns
    horizon_h = tw.h
    samples, results, events = {}, [], []

    # ---------------------------------------------------------------- samples and what came of each
    for k, c in camps.items():
        refs = _ref_flags(c)
        for lid, lt in c._lot_truth.items():
            L = c.lots.get(lid)
            runs = lt.get("runs", [])
            nf = sum(1 for r in runs if r.get("failed"))
            st, det = "COMPLETED", None
            if L is None:
                # a top-up lot is blended into an earlier lot of the same design when it comes back
                into = next((x for x in c.lots.values() if x.get("topped_up") and x["design"] ==
                             _design_of_lot(c, lid)), None)
                st, det = ("COMPLETED", f"top-up, blended into L{into['id']}") if into else \
                    ("STALE", "still in flight at the horizon")
            elif runs and nf == len(runs):
                st, det = "ABANDONED", f"all {len(runs)} atomizer runs dripped: no powder"
            samples[f"L{lid}"] = dict(type="lot", campaign=k, design=_design_of_lot(c, lid),
                                      created_h=_r(L["t"] if L else None, 3), status=st, detail=det,
                                      runs=len(runs), failed_runs=nf, crucible_cm3=lt.get("crucible_cm3"),
                                      cut_g=_r(L["measured"].get("cut_g") if L else None, 1))
            if L is not None:
                m = L["measured"]
                results.append(dict(t_h=_r(L["t"], 3), campaign=k, type="lot", sample=f"L{lid}", design=L["design"],
                                    measured=dict(_summ(m, ("runs", "failed_runs", "cut_g", "d50_um", "cut_frac",
                                                            "oxygen_ppm")),
                                                  eds_wt_pct={e: _r(v, 3) for e, v in (m.get("eds") or {}).items()})))
                # run, but not as planned: the powder's composition (hidden) is off the design by > 15 % relative
                # (and > 0.2 wt%) in some element; the lab sees it in the EDS / XRF / ICP-MS numbers it attaches
                want = c.designs[L["design"]]["composition"]
                got = lt.get("composition", {})
                off = {e: (_r(want.get(e, 0.0), 3), _r(got.get(e, 0.0), 3)) for e in set(want) | set(got)
                       if e != c.space.balance and abs(got.get(e, 0.0) - want.get(e, 0.0)) >
                       max(0.2, 0.15 * want.get(e, 0.0))}
                if off and samples[f"L{lid}"]["status"] == "COMPLETED":
                    samples[f"L{lid}"].update(status="NOT_AS_PLANNED",
                                              detail="composition off the design (designed, made): " +
                                                     ", ".join(f"{e} {a}->{b}" for e, (a, b) in sorted(off.items())),
                                              executed_wt_pct={e: _r(v, 3) for e, v in (m.get("eds") or {}).items()})
        for bid, B in c.builds.items():
            m = B["measured"][B["bars_at"]]
            sound = m["rel_density"] >= 0.98 and m["crack_density"] < 0.3
            if not sound:
                st, det = "ABANDONED", (f"bars cube {m['rel_density']:.3f} dense, crack density "
                                        f"{m['crack_density']:.2f}/mm2 (needs >= 0.98 and < 0.3)")
            elif B.get("tested") or any(t["build"] == bid for t in c.tests):
                st, det = "COMPLETED", "machined into bars and pulled"
            elif B.get("_await_pip") or B.get("pip") is not None:
                st, det = "EARLY_STOPPED", "sound; PIP and section measured; the policy did not buy bars"
            else:
                st, det = "STALE", "sound; not tested by the horizon"
            samples[f"B{bid}"] = dict(type="build", campaign=k, design=B["design"], parent=f"L{B['lot']}",
                                      created_h=_r(B["t"], 3), status=st, detail=det,
                                      cubes=len(B["measured"]), bars_cube=B["bars_at"],
                                      sound_cubes=sum(1 for x in B["measured"]
                                                      if x["rel_density"] >= 0.98 and x["crack_density"] < 0.3))
            results.append(dict(t_h=_r(B["t"], 3), campaign=k, type="build", sample=f"B{bid}", design=B["design"],
                                measured=dict(bars_cube=_summ(m, ("rel_density", "rel_density_archimedes",
                                                                  "rel_density_sem", "crack_density")),
                                              params=_summ(m.get("params", {}), list(m.get("params", {}))))))
        for did, D in c.deposits.items():
            ms = D["measured"]
            ok = [x for x in ms if x["rel_density"] >= (0.96 if D["mode"] == "blend" else 0.98)
                  and x["crack_density"] < 0.3]
            mode = D["mode"]
            if not ok and mode != "blown_large":
                st, det = "ABANDONED", f"no block of {len(ms)} dense and crack-free"
            elif mode == "blown_large":
                x = ms[0]
                if x["rel_density"] < 0.97 or x["crack_density"] >= 0.5:
                    st, det = "ABANDONED", f"1 kg deposit {x['rel_density']:.3f} dense"
                elif isinstance(D.get("tensile"), dict) and isinstance(D.get("immersion"), dict):
                    st, det = "COMPLETED", "bars pulled and 30-day immersion done"
                else:
                    st, det = "STALE", "tests not back by the horizon"
            else:
                promoted = _promoted(c, D)
                if promoted:
                    st, det = "COMPLETED", "screened; promoted to an atomized lot and a 1 kg deposit"
                elif isinstance(D.get("pip"), dict) or isinstance(D.get("screen"), dict):
                    st, det = "EARLY_STOPPED", "sound; PIP and corrosion screen measured; not promoted"
                else:
                    st, det = "STALE", "sound; not screened by the horizon"
            samples[f"D{did}"] = dict(type="deposit", campaign=k, design=D["design"], mode=mode,
                                      parent=f"L{D['lot']}" if D.get("lot") else None, created_h=_r(D["t"], 3),
                                      status=st, detail=det, blocks=len(ms))
            results.append(dict(t_h=_r(D["t"], 3), campaign=k, type="deposit", sample=f"D{did}", design=D["design"],
                                measured=dict(mode=mode, blocks=[_summ(x, ("rel_density", "crack_density",
                                                                            "beta_prime", "dilution")) for x in ms])))
        # parts made but not back by the horizon (their bookings are in the log; their results are not)
        for pid, pt in c._part_truth.items():
            if pid in c.builds or pid in c.deposits:
                continue
            dep = "mode" in pt
            samples[("D" if dep else "B") + str(pid)] = dict(
                type="deposit" if dep else "build", campaign=k, design=None, mode=pt.get("mode"),
                parent=f"L{pt['lot']}" if pt.get("lot") else None, created_h=None, status="STALE",
                detail="made, but its result was not back by the horizon")
        for t in c.tests:
            sid = f"B{t['build']}" if t.get("build") else f"E8-L{_lot_of_e8(c, t)}"
            results.append(dict(t_h=_r(t["t"], 3), campaign=k, type="tensile", sample=sid, design=t["design"],
                                measured=_summ(t["measured"], ("ys_MPa", "uts_MPa", "el_pct", "hot_ys_MPa",
                                                               "n_bars"))))
        for x in c.corr:
            results.append(dict(t_h=_r(x["t"], 3), campaign=k, type=x["what"], sample=f"D{x['deposit']}",
                                design=x["design"],
                                measured=_summ(x["measured"], ("ys_MPa", "uts_MPa", "el_pct", "early_rate_um_yr",
                                                               "Rp_ohm_cm2", "Eb_mV", "rate30_um_yr", "Ni_release",
                                                               "Cu_release"))))
        for s in c.sims:
            results.append(dict(t_h=_r(s["t"], 3), campaign=k, type=s["kind"], sample=None, design=s["design"],
                                measured={kk: _r(vv) for kk, vv in (s["out"] or {}).items()
                                          if isinstance(vv, (int, float, np.floating, np.integer))}))
        for d in c.demonstrated:
            results.append(dict(t_h=_r(d["t_h"], 3), campaign=k, type="scored (hidden)", sample=None,
                                design=d["design"], reference=bool(refs.get(d["design"])),
                                hidden=dict(u_true=_r(d["u"]), discovery=bool(d.get("discovery")),
                                            feasible=bool(d.get("feasible", d.get("h5_pass", False))))))
    results.sort(key=lambda r: (r["t_h"] is None, r["t_h"] or 0.0))

    # ---------------------------------------------------------------- bookings, with outcome and step
    for i, e in enumerate(log["events"]):
        k = e["campaign"]
        c = camps.get(k)
        sid = e.get("sample")
        outcome, detail = "COMPLETED", None
        if e["station"] == "atomizer" and e["what"] == "atomize" and sid and c is not None:
            lt = c._lot_truth.get(int(sid[1:]))
            run = (lt or {}).get("runs", [])
            j = e.get("run")
            if j is not None and j < len(run):
                r = run[j]
                if r.get("failed"):
                    p = float(r.get("p_fail", P_FAIL_BASE))
                    if p - P_FAIL_BASE > P_FAIL_BASE:
                        outcome = "ABANDONED"
                        detail = f"dripped; P(fail) {p:.2f} at these settings, mostly from the inputs (cold melt or flood)"
                    else:
                        outcome = "FAILED"
                        detail = f"dripped; P(fail) {p:.2f}, the base rate (chance): retry"
                else:
                    detail = f"{r['charge_g']:.0f} g charge, {100 * r['usable_frac']:.0f} % usable, " \
                             f"d50 {r['d50_um']:.0f} um"
        elif e["what"] == "print" and e["station"] == "utah_midi" and sid in samples:
            S = samples[sid]
            outcome = "ABANDONED" if S["status"] == "ABANDONED" else "COMPLETED"
            if "sound_cubes" in S:
                detail = f"{S['sound_cubes']} of {S['cubes']} cubes sound" + (
                    f"; {S['detail']}" if outcome == "ABANDONED" else "")
            else:                                # printed, but its cubes were not measured by the horizon
                detail = S.get("detail")
        elif e["what"] in ("blend_ded", "blown_small", "blown_large") and e["station"] == "utah_mxlab" and sid in samples:
            S = samples[sid]
            outcome = "ABANDONED" if S["status"] == "ABANDONED" else "COMPLETED"
            detail = S["detail"] if outcome == "ABANDONED" else None
        step, n211 = step_of(k, e.get("node"), e["station"], e["what"])
        events.append(dict(id=i, t_start_h=e["t0_h"], t_end_h=e["t1_h"], duration_h=_r(e["t1_h"] - e["t0_h"], 3),
                           day=_r(e["t0_h"] / H, 3), station=e["station"], campaign=k, sample=sid,
                           design=e.get("design"), step=step, dal211=n211, twin_node=e.get("node"), what=e["what"],
                           run=e.get("run"), outcome=outcome, detail=detail))
    # breakdowns
    f = next(iter(tw.facilities.values()))
    for key, r in f.res.items():
        for a, b in r.down:
            if a < horizon_h:
                events.append(dict(id=None, t_start_h=_r(a, 3), t_end_h=_r(b, 3), duration_h=_r(b - a, 3),
                                   day=_r(a / H, 3), station=key, campaign=None, sample=None, design=None,
                                   step="breakdown and repair", dal211=None, twin_node=None, what="down",
                                   run=None, outcome="DOWN", detail=f"{r.st.name}: down {b - a:.0f} h"))
    # artifact-level decisions at the horizon: sound parts not taken further, proposals never run
    for sid, S in samples.items():
        if S["status"] in ("EARLY_STOPPED", "STALE"):
            events.append(dict(id=None, t_start_h=_r(horizon_h, 3), t_end_h=_r(horizon_h, 3), duration_h=0.0,
                               day=_r(horizon_h / H, 3), station=None, campaign=S["campaign"], sample=sid,
                               design=S["design"], step="decision at the horizon", dal211=None, twin_node=None,
                               what="decision", run=None, outcome=S["status"], detail=S["detail"]))

    # ---------------------------------------------------------------- iterations (the optimizer's state)
    its = []
    best_new, best_all = {}, {}
    dem = {k: sorted(c.demonstrated, key=lambda d: d["t_h"]) for k, c in camps.items()}
    refs = {k: _ref_flags(c) for k, c in camps.items()}
    for rec in (tw.trace or []):
        k = rec["campaign"]
        t = rec["t_h"]
        bn = max([d["u"] for d in dem[k] if d["t_h"] <= t and not refs[k].get(d["design"])] or [0.0])
        ba = max([d["u"] for d in dem[k] if d["t_h"] <= t] or [0.0])
        props = []
        for p in rec["proposals"]:
            p = dict(p)
            if p.get("acq_kind") is None:
                p["acq_kind"] = _default_kind(cfg["policy"], p["kind"])
            if p["kind"] in ("powder", "blend_ded") and p.get("design") is not None and not p.get("accepted"):
                p["outcome"] = "STALE"
            props.append(p)
            if not p.get("accepted"):
                events.append(dict(id=None, t_start_h=t, t_end_h=t, duration_h=0.0, day=_r(t / H, 3), station=None,
                                   campaign=k, sample=None, design=p.get("design"), step="proposal refused",
                                   dal211=None, twin_node=None, what=p["kind"], run=None, outcome="STALE",
                                   detail="refused: over the campaign's money left, or nothing to act on"))
        its.append(dict(campaign=k, it=rec["it"], t_h=t, day=_r(t / H, 3), n_free=rec["n_free"],
                        spent_usd=rec["spent"], best_obs=rec.get("best_obs"), best_true_new=_r(bn),
                        best_true_all=_r(ba), proposals=props))

    # ---------------------------------------------------------------- literature steps (reused Edison results)
    lit = literature_events(camps, its)
    for L in lit:
        events.append(dict(id=None, t_start_h=L["t_h"], t_end_h=L["t_h"] + L.get("duration_h", 0.0),
                           duration_h=L.get("duration_h", 0.0), day=_r(L["t_h"] / H, 3), station="literature",
                           campaign=L["campaign"], sample=None, design=None, step="literature search (Edison, reused)",
                           dal211=L.get("dal211"), twin_node="literature", what=L["decision"], run=None,
                           outcome="COMPLETED", detail=L["question"]))
    events.sort(key=lambda e: (e["t_start_h"], e["station"] or ""))
    for n, e in enumerate(events):
        e["id"] = n

    # ---------------------------------------------------------------- weekly atomizer runs, curves, meta
    weeks = int(math.ceil(horizon_h / 168.0))
    atom = {k: [0] * weeks for k in camps}
    for e in events:
        if e["station"] == "atomizer" and e["what"] == "atomize" and e["campaign"] in atom:
            w = int(e["t_start_h"] // 168)
            if w < weeks:
                atom[e["campaign"]][w] += 1
    tot = [sum(atom[k][w] for k in camps) for w in range(weeks)]
    weekly = dict(atomizer_runs=atom, atomizer_runs_total=tot,
                  weeks_below_3=[w for w, n in enumerate(tot) if n < 3],
                  rule="DAL #256: at least 3 atomizer runs a week")
    curves = {}
    for k in camps:
        best, cur = 0.0, []
        for d in dem[k]:
            if refs[k].get(d["design"]):
                continue
            best = max(best, d["u"])
            cur.append([_r(d["t_h"] / H, 3), _r(d["spent"], 2), _r(best)])
        curves[k] = cur
    meta = dict(schema=SCHEMA, run_id=run_id, generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                cfg=cfg, time="hours from the start (t = 0 is a Monday, 00:00); day = t / 24",
                horizon_h=horizon_h, outcomes=OUTCOMES,
                campaigns={k: dict(budget_usd=c.spec.budget_usd, wip=c.spec.wip, spent_usd=_r(c.spent, 2),
                                   elements=c.space.elements, process=[v.name for v in c.space.process],
                                   base=c.space.balance)
                           for k, c in camps.items()})
    return dict(meta=meta, stations=log["stations"], seeds=seeds or {}, samples=samples, events=events,
                iterations=its, results=results, weekly=weekly, curves=curves,
                literature=lit)


def _design_of_lot(c, lid):
    L = c.lots.get(lid)
    if L is not None:
        return L["design"]
    for r in c.results_log:
        pass
    # a top-up lot's design: find the booking that made it
    f = c.fac
    for j in f.res["atomizer"].jobs:
        tag = (j[4] if len(j) > 4 else None) or {}
        if tag.get("sample") == f"L{lid}":
            return tag.get("design")
    return None


def _promoted(c, D):
    """Copper blend screen: did a later atomized lot of the same design exist?"""
    return any(L["design"] == D["design"] and L["t"] > D["t"] for L in c.lots.values())


def _lot_of_e8(c, t):
    for L in c.lots.values():
        if L["design"] == t["design"]:
            return L["id"]
    return "?"


def _default_kind(policy, kind):
    if kind in ("powder", "blend_ded"):
        return {"random": "random design", "sobol": "next Sobol design", "heuristic": "mutation of the best alloy",
                "tiered": "next on the CALPHAD-screened shortlist"}.get(policy, "new design")
    if kind.startswith("sim"):
        return "simulation request"
    return "next step of a part already made (no acquisition)"


def literature_events(camps, its) -> list:
    """The campaign's literature steps, each answered by an Edison result already posted in DAL (LITERATURE)."""
    out = []
    for k, c in camps.items():
        for dec, L in LITERATURE.get(k, {}).items():
            t = None
            if L["when"] == "start":
                t = 0.0
            elif L["when"] == "first_new_element":
                seen = set()
                for it in its:
                    if it["campaign"] != k:
                        continue
                    for p in it["proposals"]:
                        x = p.get("x") or {}
                        for e in L.get("elements", []):
                            if x.get(e, 0.0) > 0 and e not in seen and p.get("accepted"):
                                seen.add(e)
                                t = it["t_h"] if t is None else t
            elif L["when"] == "first_result":
                ts = [x["t"] for x in (c.corr if L.get("result") in ("screen", "immersion") else [])
                      if x["what"] == L.get("result")]
                if L.get("result") == "test":
                    ts = [x["t"] for x in c.tests]
                if L.get("result") == "build":
                    ts = [B["t"] for B in c.builds.values()]
                t = min(ts) if ts else None
            elif L["when"] == "first_promotion":          # the first part sent on to bars or a 1 kg deposit
                ts = [it["t_h"] for it in its if it["campaign"] == k and
                      any(p.get("kind") in ("test", "large_ded", "promote") or
                          any(w in (p.get("acq_kind") or "") for w in ("promote", "bars", "1 kg"))
                          for p in it["proposals"] if p.get("accepted"))]
                t = min(ts) if ts else None
            if t is None:
                continue
            out.append(dict(t_h=_r(t, 3), campaign=k, decision=dec, question=L["question"],
                            duration_h=L.get("duration_h", 0.0), dal211=L.get("dal211"),
                            edison=L["edison"], reused=True))
    return sorted(out, key=lambda x: x["t_h"])


# ------------------------------------------------------------------------------------------------- one traced run
def run(policy="bofn", facility="vertical_lab", seed=0, seeding="dal275", days=365, out=None):
    import torch
    torch.set_num_threads(1)
    from twin import bench2
    cfg = bench2._cfg(policy, seed, facility=facility, days=days, seeding=seeding, trace=True)
    res = bench2.run_one(cfg)
    return res


def check(path) -> list:
    """Consistency checks on a trace file; returns the problems found (empty: none)."""
    T = json.loads(Path(path).read_text())
    bad = []
    for key in ("meta", "stations", "seeds", "samples", "events", "iterations", "results", "weekly", "curves"):
        if key not in T:
            bad.append(f"missing {key}")
    ok_out = set(OUTCOMES)
    for e in T.get("events", []):
        if e["outcome"] not in ok_out:
            bad.append(f"event {e['id']}: outcome {e['outcome']}")
        if e["t_end_h"] < e["t_start_h"] - 1e-9:
            bad.append(f"event {e['id']}: ends before it starts")
        if e.get("sample") and e["sample"] not in T["samples"] and not str(e["sample"]).startswith("E8"):
            bad.append(f"event {e['id']}: sample {e['sample']} not in samples")
    last = {}
    for it in T.get("iterations", []):
        k = it["campaign"]
        if it["best_true_new"] < last.get(k, 0.0) - 1e-9:
            bad.append(f"iteration {k} {it['it']}: best so far went down")
        last[k] = it["best_true_new"]
    return bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "check":
        probs = check(a[1])
        print("\n".join(probs) if probs else "ok")
    elif a and a[0] == "run":
        r = run(*(a[1:2] or ["bofn"]), *(a[2:3] or []), *[int(x) for x in a[3:4]])
        print(r.get("trace_file"))
    else:
        raise SystemExit(__doc__)

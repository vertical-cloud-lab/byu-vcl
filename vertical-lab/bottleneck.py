"""Bottlenecks: from about one fully tested alloy a day to ten (#303, PR #318).

    python3 bottleneck.py              # the analysis -> out/bottleneck.json, out/bottleneck_ladder.png,
                                       #   out/bottleneck_capacity.png, out/bottleneck_utilization.png
    python3 bottleneck.py ladder       # print the ladder only (about 1 min)

Sterling, on PR #318 (2026-11-08): "Approx. one full alloy tested per day was the estimation. How can we get that up
to 10/day? What would be required? For example, each atomizer run could probably be completed within 2-4 hours, which
lends itself to 6-12 unique compositions per day, assuming only one unit is available. Similarly for the other
machines (e.g., LPBF, DED)."

The "one a day" is the finale's schedule (timelapse.py): 324 alloys fully tested in a year with no upkeep, 304 with it
(notes/timelapse.md, notes/upkeep.md). This file asks the same model what ten a day would take, two ways:

1. ``capacity()``, per machine. The hours each station spends per fully tested alloy (timelapse.STEPS, with the runs
   that drip, the builds that fail and the promoted alloys' extra runs), against the hours it has in a day. That gives
   each machine's ceiling in alloys a day, one unit running round the clock, and the units ten a day needs.
2. ``simulate()``, the whole lab. timelapse.simulate's greedy schedule, generalised: several units of a station, the
   crucible's person on shifts (or a robot), the arms' whole handling time (in, attended, out) rather than 6 min at a
   step's start, the Shuttles' openings held while a tray is presented, a wash for the sieves, and a DED front end.
   ``LADDER`` runs it rung by rung: each rung removes the bottleneck the one before it found.

With the finale's settings and handling, ``simulate()`` reproduces timelapse.simulate's alloys exactly (``check()``),
so the rungs above it start from the same model. Everything this file adds is an assumption unless it cites a source:
``ASSUMED`` lists them, and out/bottleneck.json carries each with its value.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

import timelapse as T

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "bottleneck"
WEEK = 168.0
WEEKS = 20                     # each scenario runs 20 weeks
W0 = 6                         # and is measured over weeks 7-20, after the finale's 4-week ramp and a fill-up week
TARGET = 10.0                  # fully tested alloys a day

STEP = {s: dict(station=st, h=h, needs=n, tray=tr) for s, st, h, n, tr, _, _ in T.STEPS}
FULL = [(s, st, h) for s, st, h, _, _ in T.FULL]
POWDER_CHECKS = ["ld", "xrd", "xrf", "psem"]
TESTS = ["tensile_rt", "tensile_hot", "sem", "vhx", "hv", "nano", "pip", "corrosion"]
TR = T.PARAMS["transfer_h"]["value"]

# ------------------------------------------------------------------------------------------------ what this adds
# The arm's time at a station beyond carrying the sample in and out, as a share of the step (assumed, from what the
# arm does in each chapter: it doses and presses the cups in chapter 1, builds and tips the sieve stack in chapter 3,
# sifts the XRD holder in chapter 4, runs the lance and loads each bar in chapter 5, changes the PX500's discs in
# chapter 6, turns the bar over under the VHX in chapter 7). The atomizer's is absolute: the lid and the cups (ch. 2).
ATTEND = dict(charge=0.8, sieve=0.7, ld=0.3, xrd=0.5, xrf=0.2, psem=0.2, print=0.1, depowder=0.8, edm=0.3, heat=0.05,
              tensile_rt=0.5, tensile_hot=0.3, section=0.2, face=0.3, mount=0.3, polish=0.3, sem=0.15, vhx=0.2,
              hv=0.1, nano=0.1, pip=0.2, corrosion=0.05, print_full=0.05, depowder_full=0.8, edm_full=0.3,
              heat_full=0.05, e8_rt=0.5, e8_hot=0.3, ded=0.05, wash=0.3)
ATTEND_H = dict(atomize=0.3, print=0.2, heat=0.05, tensile_hot=0.15, corrosion=0.05, print_full=0.2,
                heat_full=0.05)

# The cells of the "cells" handling: machines on the floor, side by side, served by a fixed arm of their own; the
# MiR250 + UR10e units only carry between cells and the Shuttles. (Our proposal for ten a day; not in the chapters.)
CELLS = {
    "charge": ["charge"],
    "powder": ["atomize", "sieve", "wash"],
    "print": ["print", "depowder", "print_full", "depowder_full", "ded"],
    "prep": ["edm", "section", "face", "mount", "polish", "edm_full"],
    "tensile": ["heat", "tensile_rt", "tensile_hot", "heat_full", "e8_rt", "e8_hot"],
}
PRED = {s: (n[0] if n else None) for s, _, _, n, *_ in T.STEPS}
PRED.update(wash="sieve", edm="depowder", print_full="sieve", depowder_full="print_full", edm_full="depowder_full",
            heat_full="edm_full", e8_rt="heat_full", e8_hot="heat_full")

ASSUMED = {
    "attended": dict(value=dict(ATTEND, **{k + "_h": v for k, v in ATTEND_H.items()}),
                     source="assumed: the share of each step the arm spends at the station, from the chapters"),
    "present_h": dict(value=0.05, unit="h", source="assumed: a tray presented for a load or an unload holds its "
                      "Shuttle's opening 3 min beyond the arm's attended time (Kardex's tray change plus the arm's "
                      "pick or place); Kardex's own access time is a question for Kardex"),
    "wash_h": dict(value=1.4, unit="h", source="notes/alloy_print.md: 12-15 min a sieve, about 75-90 min for the six"),
    "u_max": dict(value=0.85, source="assumed: the share of its available hours a station can be booked before queues "
                  "grow without bound in a schedule with this much variety"),
    "availability": dict(value="out/upkeep_model.json availability (seed 303, at about one alloy a day)",
                         source="upkeep.py; at ten a day the usage-driven faults come ten times as often, so these are "
                                "optimistic"),
    "shifts": dict(value={"1x5": "08-16 Mon-Fri", "2x5": "06-22 Mon-Fri", "2x7": "06-22 daily",
                          "3x7": "round the clock"}, source="assumed shift patterns for the crucible's person"),
    "ded": dict(value=dict(per_plate=8, plate_h=8.0, fail_every=10),
                source="assumed: an MX-Lab plate of 8 small blocks, one composition each, blended in the melt pool "
                       "from its six feeders; 8 h a plate with set-up, deposition, cooling and unloading"),
}

SHIFTS = {"1x5": (5, 8.0, 16.0), "2x5": (5, 6.0, 22.0), "2x7": (7, 6.0, 22.0), "3x7": (7, 0.0, 24.0)}

DEFAULT = dict(
    key="", label="", note="",
    atomizers=1,
    atom=dict(person=1.0, run=1.0, cool=0.5),      # timelapse PARAMS atomize_h: 2.5 h
    crucible="slots",          # "slots": the finale's 3 staffed starts a weekday; "shifts": a person on shift; "robot"
    shifts="3x7", people=1,    # for "shifts": the pattern, and crucible-trained people on each shift
    run_fail_every=10, build_fail_every=7,
    promote_every=10, promote_charge_g=300.0, promote_source="atomizer",   # or "vendor" (bought powder), or "none"
    promote_chain=True,        # the finale's promoted runs one after another; False: each as soon as it can
    pools={}, dur={}, trays={},  # station -> units; step -> hours; step -> tray (None: on the floor)
    handling="finale",         # "finale": a unit 6 min at each step's start (timelapse); "full": see the module doc
    units=2, openings=1,       # MiR250 + UR10e units; access openings per Shuttle
    sieve_wash=False,          # a wash module run after each sieving, 1.4 h (notes/alloy_print.md)
    front="powder",            # "powder": charge, atomize, sieve, LPBF; "ded": an MX-Lab plate, blended in situ
    ded=dict(units=1, per_plate=8, plate_h=8.0, fail_every=10),
)


def scenario(**kw) -> dict:
    s = json.loads(json.dumps(DEFAULT))
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(s.get(k), dict):
            s[k] = {**s[k], **v}
        else:
            s[k] = v
    return s


# ------------------------------------------------------------------------------------------------ the schedule
def first(lines, t, d):
    """(start, index): the line of `lines` that can take d hours soonest at or after t."""
    best = (math.inf, -1)
    for i, ln in enumerate(lines):
        s = ln.earliest(t, d)
        if s < best[0]:
            best = (s, i)
    return best


def next_staffed(t: float, d: float, pattern: str) -> float:
    """The first t' >= t with [t', t' + d] inside a staffed shift (t = 0 is Monday 06:00 of week 1)."""
    days, h0, h1 = SHIFTS[pattern]
    if days == 7 and h0 == 0.0 and h1 == 24.0:
        return t
    for _ in range(60):
        day = math.floor((t + 6.0) / 24.0)
        hod, dow = t + 6.0 - 24.0 * day, day % 7
        if dow < days and hod >= h0 - 1e-9 and hod + d <= h1 + 1e-9:
            return t
        if dow < days and hod < h0:
            t = 24.0 * day + h0 - 6.0
        else:
            t = 24.0 * (day + 1) + h0 - 6.0
    return t


def busy_h(ln, a: float, b: float) -> float:
    return sum(max(0.0, min(e, b) - max(s, a)) for s, e in zip(ln.s, ln.e))


def simulate(scn: dict, weeks: int = WEEKS, hours: float | None = None) -> dict:
    """The greedy schedule of timelapse.simulate, generalised (module doc). -> events, alloys and resources."""
    S = scenario(**scn) if "atomizers" not in scn else scn
    hand = S["handling"]                                    # "finale", "full" or "cells"
    full = hand != "finale"
    pr = ASSUMED["present_h"]["value"] if full else 0.0
    shut_of = T._shuttles()
    cell_of = {st: c for c, sts in CELLS.items() for st in sts} if hand == "cells" else {}
    pools: dict[str, list] = {}

    def pool(st, n=None):
        if st not in pools:
            pools[st] = [T.Line() for _ in range(n or S["pools"].get(st, 1))]
        return pools[st]

    pool("repowder", S["atomizers"])
    units = pool("units", S["units"])
    opening = {1: [T.Line() for _ in range(S["openings"])], 2: [T.Line() for _ in range(S["openings"])]}
    people = [T.Line() for _ in range(S["people"])]
    robots = [T.Line() for _ in range(S["atomizers"])]
    atom_h = sum(S["atom"].values())
    person_h = S["atom"]["person"]
    ev: list[dict] = []
    hands_h: dict[str, float] = {}                          # "units" or "arm:<cell>" -> hours

    def dur(step, default):
        return S["dur"].get(step, default)

    def tray(step, default):
        if step in cell_of:                                 # a cell's machines stand on the floor
            return None
        return S["trays"].get(step, default)

    def finale_hands(t, ready, atom, TRs):
        """timelapse.simulate's: a unit for TRs just before the step; an atomizer's charge may wait by it."""
        best = None
        for u, ul in enumerate(units):
            tu = ul.earliest(t - TRs, TRs) + TRs
            tx = tu - TRs
            if atom and tu > t + 1e-9:
                x = ul.earliest(max(ready, t - T.ATOM_WAIT_H), TRs)
                if x + TRs <= t + 1e-9:
                    tu, tx = t, x
            if best is None or tu < best[1]:
                best = (u, tu, tx)
        return best

    def book(step, station, ready, d, alloy, tr=None, atom=False, share=1.0, line=None):
        """Book `step` on a free line of `station` as soon as everything it needs is free together. share: the part
        of a carry this booking pays for (a DED plate's blocks share one load and one unload)."""
        allp = pool(station)
        lines = allp if line is None else [allp[line]]
        cell = cell_of.get(step)
        arm = pool("arm:" + cell, S["pools"].get("arm:" + cell, 1)) if cell else None
        att = ((ATTEND_H[step] if step in ATTEND_H else ATTEND.get(step, 0.2) * d) * share) if full else 0.0
        TRs = TR * share
        occ = d + (TRs if full else 0.0)
        sh = shut_of.get(tr) if (tr and full) else None
        prev = PRED.get(step)
        att_by = arm if cell else units                     # who stays with it
        load_by = arm if (cell and cell_of.get(prev) == cell) else units
        window = full and (atom or load_by is not att_by)   # carried in early, to wait in a buffer
        t = max(ready, 0.0)
        for _ in range(5000):
            if atom and S["crucible"] == "slots":
                t = T.next_run_slot(t)
            if atom and S["crucible"] == "shifts":
                ts = next_staffed(t, person_h, S["shifts"])
                if ts > t + 1e-9:
                    t = ts
                    continue
            s, li = first(lines, t, occ)
            if s > t + 1e-9:
                t = s
                continue
            if atom and S["crucible"] in ("shifts", "robot"):
                pl = people if S["crucible"] == "shifts" else robots
                ps, pi = first(pl, t, person_h)
                if ps > t + 1e-9:
                    t = ps
                    continue
            if sh:
                os_, oi = first(opening[sh], t - pr, pr + att)
                if os_ > t - pr + 1e-9:
                    t = os_ + pr
                    continue
            if not full:
                best = finale_hands(t, ready, atom, TRs)
                if best[1] > t + 1e-9:
                    t = best[1]
                    continue
                break
            if window:
                if att > 0:
                    sa, ia = first(att_by, t, att)
                    if sa > t + 1e-9:
                        t = sa
                        continue
                x, ix = first(load_by, max(ready, t - T.ATOM_WAIT_H), TRs)
                if x + TRs > t + 1e-9:
                    t = x + TRs
                    continue
            else:
                sa, ia = first(att_by, t - TRs, TRs + att)
                if sa > t - TRs + 1e-9:
                    t = sa + TRs
                    continue
            break
        lines[li].add(t, t + occ)
        li = allp.index(lines[li])
        if not full:
            u, _, tx = best
            units[u].add(tx, tx + TRs)
            hands_h["units"] = hands_h.get("units", 0.0) + TRs
        elif window:
            if att > 0:
                sa, ia = first(att_by, t, att)               # found again: the carry may share its line
                att_by[ia].add(t, t + att)
            x, ix = first(load_by, max(ready, t - T.ATOM_WAIT_H), TRs)
            load_by[ix].add(x, x + TRs)
            k_att, k_load = ("arm:" + cell if cell else "units"), ("units" if load_by is units else "arm:" + cell)
            hands_h[k_att] = hands_h.get(k_att, 0.0) + att
            hands_h[k_load] = hands_h.get(k_load, 0.0) + TRs
        else:
            att_by[ia].add(t - TRs, t + att)
            k = "arm:" + cell if cell else "units"
            hands_h[k] = hands_h.get(k, 0.0) + TRs + att
        if atom and S["crucible"] in ("shifts", "robot"):
            pl[pi].add(t, t + person_h)
        if sh:
            opening[sh][oi].add(t - pr, t + att)
        out_t = t + d
        if full:                                            # taken out: by the cell's arm, or a unit at the tray
            by = arm if cell else units
            s2, u2 = first(by, t + d, TRs)
            if sh:
                for _ in range(200):
                    s3, o3 = first(opening[sh], s2, pr)
                    if s3 <= s2 + 1e-9:
                        break
                    s2, u2 = first(by, s3, TRs)
                opening[sh][o3].add(s2, s2 + pr)
            by[u2].add(s2, s2 + TRs)
            k = "arm:" + cell if cell else "units"
            hands_h[k] = hands_h.get(k, 0.0) + TRs
            out_t = s2 + TRs
        ev.append(dict(t0=t, t1=t + d, station=station, step=step, alloy=alloy, line=li, ready=ready))
        return out_t

    count = dict(runs=0, builds=0, tested=0, ded=0)
    fr = S["run_fail_every"] or 10 ** 9
    fb = S["build_fail_every"] or 10 ** 9
    t_front: list[float] = []

    def run(alloy, ready, charge_g=None):
        """Charge and atomize, again if the run drips. -> (the good run's end, its start)."""
        while True:
            e_c = book("charge", "carousel", ready, dur("charge", STEP["charge"]["h"]), alloy,
                       tray("charge", STEP["charge"]["tray"]))
            count["runs"] += 1
            e_a = book("atomize", "repowder", e_c, atom_h, alloy, atom=True)
            t0 = ev[-1]["t0"]
            if count["runs"] % fr == fr - 3:
                ev[-1]["failed"] = True
                ready = e_a
                continue
            return e_a, t0

    def sieve(alloy, t):
        e = book("sieve", "sieve_cell", t, dur("sieve", STEP["sieve"]["h"]), alloy, tray("sieve", None))
        if S["sieve_wash"]:
            book("wash", "sieve_wash", e, ASSUMED["wash_h"]["value"], alloy)
        return e

    def downstream(alloy, done, first_step="depowder"):
        names = [s for s, *_ in T.STEPS]
        for step in names[names.index(first_step):]:
            st = STEP[step]
            needs = [n if n in done else "depowder" for n in st["needs"]]
            line = done.get("print_line") if step == "depowder" else None    # on the MIDI it was printed on
            done[step] = book(step, st["station"], max(done[n] for n in needs), dur(step, st["h"]), alloy,
                              tray(step, st["tray"]), line=line)
        return max(done[k] for k in TESTS)

    def promote(alloy, t):
        if S["promote_source"] == "none":
            return None
        if S["promote_source"] == "atomizer":         # more runs of the same composition, run as soon as each can
            per = S["promote_charge_g"] * T.PARAMS["fines_frac"]["value"]
            extra = max(0, math.ceil(T.PARAMS["full_build_g"]["value"] / per) - 1)
            ends = [t]
            for _ in range(extra):
                if S["promote_chain"]:                     # the finale's: each run after the last one's sieving
                    e, _ = run(alloy, ends[-1])
                else:
                    e, _ = run(alloy, t)
                ends.append(sieve(alloy, e))
            t = max(ends)
        line = None
        for step, st, h in FULL:
            t = book(step, st, t, dur(step, h), alloy, line=line if step == "depowder_full" else None)
            line = ev[-1]["line"]
        return t

    def powder_route(alloy, ready):
        e_atom, t0 = run(alloy, ready)
        done = {"atomize": e_atom}
        rec = dict(alloy=alloy, atomized=e_atom, t_front=t0)
        done["sieve"] = sieve(alloy, e_atom)
        for step in POWDER_CHECKS:
            st = STEP[step]
            done[step] = book(step, st["station"], done["sieve"], dur(step, st["h"]), alloy, tray(step, st["tray"]))
        count["builds"] += 1
        done["print"] = book("print", "aconity", done["sieve"], dur("print", STEP["print"]["h"]), alloy)
        done["print_line"] = ev[-1]["line"]
        if count["builds"] % fb == 0:
            ev[-1]["failed"] = True
            return rec
        rec["printed"] = done["print"]
        rec["tested"] = downstream(alloy, done)
        return rec

    alloys = []
    hours = hours if hours is not None else weeks * WEEK
    if S["front"] == "powder":
        k = 2 * S["atomizers"]
        for a in range(20000):
            ready = t_front[a - k] if a >= k else 0.0
            rec = powder_route(a, ready)
            if rec["atomized"] > hours:
                break
            t_front.append(rec["t_front"])
            if "tested" in rec:
                count["tested"] += 1
                if count["tested"] % (S["promote_every"] or 10 ** 9) == 0:
                    p = promote(a, rec["tested"])
                    if p is not None:
                        rec["promoted"] = p
            alloys.append(rec)
    else:                                                   # DED front: an MX-Lab plate of small blocks
        D = S["ded"]
        pools["ded"] = [T.Line() for _ in range(D["units"] * D["per_plate"])]
        k = 2 * D["units"] * D["per_plate"]
        lp = 0
        for a in range(20000):
            ready = t_front[a - k] if a >= k else 0.0
            e = book("ded", "ded", ready, D["plate_h"], a, share=1.0 / D["per_plate"])
            t_front.append(ev[-1]["t0"])
            if e > hours:
                break
            rec = dict(alloy=a, deposited=e, t_front=ev[-1]["t0"])
            count["ded"] += 1
            if count["ded"] % (D["fail_every"] or 10 ** 9) == 0:
                alloys.append(rec)
                continue
            done = {"depowder": e}
            done["xrf"] = book("xrf", "xrf", e, dur("xrf", STEP["xrf"]["h"]), a, tray("xrf", "M"))
            rec["tested"] = max(downstream(a, done, "edm"), done["xrf"])
            count["tested"] += 1
            if count["tested"] % (S["promote_every"] or 10 ** 9) == 0:   # the best go through the powder route
                lp += 1
                r2 = powder_route(10 ** 6 + lp, rec["tested"])
                if "tested" in r2:
                    rec["promoted"] = r2["tested"]
            alloys.append(rec)

    ev.sort(key=lambda e: e["t0"])
    res = dict(alloys=alloys, events=ev, runs=count["runs"], pools=pools, units=units, opening=opening,
               people=people, robots=robots, hands_h=hands_h, S=S, hours=hours)
    return res


def measure(res: dict, w0: int = W0) -> dict:
    """Steady-state rates over weeks w0+1 .. the end, and each resource's busy share then."""
    S = res["S"]
    a, b = w0 * WEEK, res["hours"]
    days = (b - a) / 24.0
    tested = sum(1 for r in res["alloys"] if a < r.get("tested", -1) <= b and r["alloy"] < 10 ** 6)
    promoted = sum(1 for r in res["alloys"] if a < r.get("promoted", -1) <= b)
    runs = sum(1 for e in res["events"] if e["step"] == "atomize" and a < e["t1"] <= b)
    util = {}
    for st, lines in res["pools"].items():
        util[st] = sum(busy_h(ln, a, b) for ln in lines) / (len(lines) * (b - a))
    for k in (1, 2):
        util[f"opening{k}"] = sum(busy_h(ln, a, b) for ln in res["opening"][k]) / (len(res["opening"][k]) * (b - a))
    if S["crucible"] == "shifts":
        days_, h0, h1 = SHIFTS[S["shifts"]]
        staffed = (b - a) / WEEK * days_ * (h1 - h0) * len(res["people"])
        util["crucible_people"] = sum(busy_h(ln, a, b) for ln in res["people"]) / staffed
    if S["crucible"] == "slots":
        slots, t = 0, a
        while True:
            t = T.next_run_slot(t)
            if t > b:
                break
            slots += 1
            t += 0.01
        util["atomizer_slots"] = runs / max(slots, 1)
    util = dict(sorted(((k, round(v, 3)) for k, v in util.items()), key=lambda kv: -kv[1]))
    lat = [r["tested"] - r["t_front"] for r in res["alloys"] if a < r.get("tested", -1) <= b and r["alloy"] < 10 ** 6]
    waits: dict[str, list] = {}
    for e in res["events"]:
        if a < e["t0"] <= b:
            waits.setdefault(e["step"], []).append(e["t0"] - e["ready"])
    wait = dict(sorted(((k, round(float(np.mean(v)), 2)) for k, v in waits.items()), key=lambda kv: -kv[1]))
    return dict(tested_per_day=round(tested / days, 2), promoted_per_day=round(promoted / days, 2),
                runs_per_day=round(runs / days, 2), utilization=util, bottleneck=next(iter(util)),
                lead_time_h=dict(median=round(float(np.median(lat)), 1) if lat else None,
                                 p90=round(float(np.percentile(lat, 90)), 1) if lat else None),
                wait_h=wait,
                hands_h_per_alloy={k: round(v / max(1, len(res["alloys"])), 2) for k, v in res["hands_h"].items()})


def check() -> dict:
    """The finale's settings reproduce timelapse.simulate (no upkeep): the same alloys, atomized and tested."""
    base = T.simulate()
    mine = simulate(scenario(), hours=T.YEAR_H)
    y = T.YEAR_H
    a = [sum(1 for r in x["alloys"] if r["atomized"] <= y) for x in (base, mine)]
    t = [sum(1 for r in x["alloys"] if r.get("tested", 1e18) <= y) for x in (base, mine)]
    return dict(timelapse=dict(atomized=a[0], tested=t[0]), bottleneck_py=dict(atomized=a[1], tested=t[1]),
                same=a[0] == a[1] and t[0] == t[1])

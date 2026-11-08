"""Bottlenecks: from about one fully tested alloy a day to ten (#303, PR #318).

    python3 bottleneck.py              # the analysis -> out/bottleneck.json, out/bottleneck_ladder.png,
                                       #   out/bottleneck_capacity.png, out/bottleneck_utilization.png
    python3 bottleneck.py ladder       # print the ladder only (a few seconds)

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
   step's start, the Shuttles' openings held while a tray is presented, floor cells with fixed arms of their own, a
   wash for the sieves, a cap on the alloys in process (CONWIP), and a DED front end.
   ``LADDER`` runs it rung by rung: each rung removes the bottleneck the one before it found.

With the finale's settings and handling, ``simulate()`` reproduces timelapse.simulate's alloys exactly (``check()``),
so the rungs above it start from the same model. Everything this file adds is an assumption unless it cites a source:
``ASSUMED`` lists them, and out/bottleneck.json carries each with its value.
"""
from __future__ import annotations

import bisect
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

SLOT_FLEX_H = 0.5                # assumed: the crucible's person waits up to 30 min for the arm before a slot is lost
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
    wip=None,                  # at most this many alloys started and not yet finished (CONWIP); None: the finale's
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
            if atom and S["crucible"] == "slots":          # beyond the finale, a run may start up to 30 min late
                t = T.next_run_slot(t) if not full else max(T.next_run_slot(t - SLOT_FLEX_H), t)
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
    exits: list[float] = []                                 # when each alloy so far left the line, sorted

    def released(a, ready):
        """CONWIP: a new alloy starts only once all but `wip` of those before it have finished."""
        w = S["wip"]
        if w and a >= w:
            return max(ready, exits[a - w])
        return ready

    def leave(rec):
        t = rec.get("tested") or max((e["t1"] for e in ev[-3:]), default=0.0)
        bisect.insort(exits, t)

    if S["front"] == "powder":
        k = 2 * S["atomizers"]
        for a in range(20000):
            ready = t_front[a - k] if a >= k else 0.0
            ready = released(a, ready)
            rec = powder_route(a, ready)
            leave(rec)
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
            ready = released(a, ready)
            e = book("ded", "ded", ready, D["plate_h"], a, share=1.0 / D["per_plate"])
            t_front.append(ev[-1]["t0"])
            if e > hours:
                break
            rec = dict(alloy=a, deposited=e, t_front=ev[-1]["t0"])
            count["ded"] += 1
            if count["ded"] % (D["fail_every"] or 10 ** 9) == 0:
                bisect.insort(exits, e)
                alloys.append(rec)
                continue
            done = {"depowder": e}
            done["xrf"] = book("xrf", "xrf", e, dur("xrf", STEP["xrf"]["h"]), a, tray("xrf", "M"))
            rec["tested"] = max(downstream(a, done, "edm"), done["xrf"])
            bisect.insort(exits, rec["tested"])
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


# ------------------------------------------------------------------------------------------------ per machine
AVAIL = {}


def avail(station: str) -> float:
    """The share of the year a station is up (out/upkeep_model.json, at about one alloy a day)."""
    if not AVAIL:
        try:
            m = json.loads((OUT / "upkeep_model.json").read_text())
            AVAIL.update({k: v["availability"] for k, v in m["availability"].items()})
        except Exception:                                  # noqa: BLE001
            pass
    if station == "units":
        return min(AVAIL.get("unit0", 0.95), AVAIL.get("unit1", 0.95))
    if station.startswith("opening"):
        return AVAIL.get("open" + station[-1], 0.96)
    return AVAIL.get(station, 0.97 if station in ("ded", "sieve_wash") or station.startswith("arm:") else 0.98)


def step_table(S: dict) -> list[tuple]:
    """(step, station, hours, tray) of every step a scenario can book, with its own durations."""
    rows = [(s, st["station"], S["dur"].get(s, st["h"]), S["trays"].get(s, st["tray"])) for s, st in STEP.items()]
    rows = [r if r[0] != "atomize" else ("atomize", "repowder", sum(S["atom"].values()), None) for r in rows]
    rows += [(s, st, S["dur"].get(s, h), None) for s, st, h in FULL]
    rows += [("wash", "sieve_wash", ASSUMED["wash_h"]["value"], None),
             ("ded", "ded", S["ded"]["plate_h"] / S["ded"]["per_plate"], None)]
    return rows


def multiplicity(S: dict) -> dict:
    """How many times each step runs per fully tested alloy: the runs that drip, the builds that fail, promotions."""
    fr = 1 - 1 / (S["run_fail_every"] or 1e12)
    fb = 1 - 1 / (S["build_fail_every"] or 1e12)
    prom = 1 / S["promote_every"] if (S["promote_every"] and S["promote_source"] != "none") else 0.0
    extra = 0
    if S["promote_source"] == "atomizer":
        per = S["promote_charge_g"] * T.PARAMS["fines_frac"]["value"]
        extra = max(0, math.ceil(T.PARAMS["full_build_g"]["value"] / per) - 1)
    down = [s for s, *_ in T.STEPS[8:]]
    m: dict[str, float] = {}
    if S["front"] == "powder":
        good = 1 / fb + prom * extra
        m.update(charge=good / fr, atomize=good / fr, sieve=good, wash=good if S["sieve_wash"] else 0.0)
        m.update({s: 1 / fb for s in POWDER_CHECKS + ["print"]})
        m.update({s: 1.0 for s in down})
        m.update({s: prom for s, *_ in FULL})
    else:                                                  # DED; the promoted go through the powder route's kit build
        fd = 1 - 1 / (S["ded"]["fail_every"] or 1e12)
        m.update(ded=1 / fd, xrf=1.0)
        m.update({s: 1.0 for s in down if s != "depowder"})
        m.update(charge=prom / fr, atomize=prom / fr, sieve=prom, wash=prom if S["sieve_wash"] else 0.0)
        for s in POWDER_CHECKS + ["print"]:
            m[s] = m.get(s, 0.0) + prom
        for s in down:
            m[s] = m.get(s, 0.0) + prom * fb
    return m


def capacity(S: dict, target: float = TARGET) -> dict:
    """Each machine's hours per fully tested alloy, its ceiling in alloys a day per unit (round the clock, at its
    availability), and the units `target` a day needs at u_max. Also the people, the arms and the openings."""
    S = scenario(**S) if "atomizers" not in S else S
    m = multiplicity(S)
    u_max = ASSUMED["u_max"]["value"]
    hours: dict[str, float] = {}
    for step, st, h, _ in step_table(S):
        if m.get(step):
            hours[st] = hours.get(st, 0.0) + m[step] * h
    units_of = dict(S["pools"], repowder=S["atomizers"], ded=S["ded"]["units"])
    rows = {}
    for st, h in sorted(hours.items(), key=lambda kv: -kv[1]):
        a = avail(st)
        per_unit = 24 * a / h
        have = units_of.get(st, 1)
        rows[st] = dict(h_per_alloy=round(h, 3), availability=a, ceiling_per_unit=round(per_unit, 2),
                        practical_per_unit=round(per_unit * u_max, 2), units=have,
                        practical_with_units=round(per_unit * u_max * have, 2),
                        units_for_target=math.ceil(target * h / (24 * a * u_max) - 1e-9))
    # the crucible's hands
    ph = m.get("atomize", 0.0) * S["atom"]["person"]
    if S["crucible"] == "slots":
        slots_day = 14 / 7.0                               # three a weekday, none on Friday afternoon
        rows["crucible (staffed slots)"] = dict(h_per_alloy=round(ph, 3),
                                                practical_with_units=round(slots_day / max(m["atomize"], 1e-9), 2),
                                                note="3 run slots a weekday, 2 on Fridays: 14 runs a week")
    elif S["crucible"] == "shifts":
        days, h0, h1 = SHIFTS[S["shifts"]]
        staffed = days / 7 * (h1 - h0) * S["people"]
        rows["crucible (people on shift)"] = dict(h_per_alloy=round(ph, 3),
                                                  practical_with_units=round(staffed * u_max / max(ph, 1e-9), 2),
                                                  note=f"{S['people']} a shift, {S['shifts']}")
    # the hands and the openings
    shut_of = T._shuttles()
    cell_of = {st: c for c, sts in CELLS.items() for st in sts} if S["handling"] == "cells" else {}
    hands: dict[str, float] = {}
    open_h = {1: 0.0, 2: 0.0}
    pr = ASSUMED["present_h"]["value"]
    for step, st, h, tray in step_table(S):
        k = m.get(step, 0.0)
        if not k:
            continue
        share = 1 / S["ded"]["per_plate"] if step == "ded" else 1.0
        att = (ATTEND_H[step] if step in ATTEND_H else ATTEND.get(step, 0.2) * h) * share
        if S["handling"] == "finale":
            hands["units"] = hands.get("units", 0.0) + k * TR
            continue
        cell = cell_of.get(step)
        if cell:
            key = "arm:" + cell
            same = cell_of.get(PRED.get(step)) == cell
            hands[key] = hands.get(key, 0.0) + k * (att + TR * share + (TR * share if same else 0.0))
            if not same:
                hands["units"] = hands.get("units", 0.0) + k * TR * share
        else:
            hands["units"] = hands.get("units", 0.0) + k * (att + 2 * TR * share)
            sh = shut_of.get(tray) if tray else None
            if sh:
                open_h[sh] += k * (att + 2 * pr)
    for key, h in hands.items():
        n = S["units"] if key == "units" else S["pools"].get(key, 1)
        a = avail(key)
        rows[key] = dict(h_per_alloy=round(h, 3), availability=a, units=n,
                         practical_with_units=round(24 * a * u_max * n / h, 2),
                         units_for_target=math.ceil(target * h / (24 * a * u_max) - 1e-9))
    if S["handling"] != "finale":
        for sh, h in open_h.items():
            if h:
                a = avail(f"opening{sh}")
                rows[f"opening{sh}"] = dict(h_per_alloy=round(h, 3), availability=a, units=S["openings"],
                                            practical_with_units=round(24 * a * u_max * S["openings"] / h, 2),
                                            units_for_target=math.ceil(target * h / (24 * a * u_max) - 1e-9))
    limit = min(rows.items(), key=lambda kv: kv[1]["practical_with_units"])
    return dict(rows=rows, multiplicity={k: round(v, 3) for k, v in m.items() if v}, limit=limit[0],
                limit_per_day=limit[1]["practical_with_units"])


# ------------------------------------------------------------------------------------------------ the ladder
WIP = 16                       # assumed: about a day and a half of alloys in process at ten a day (CONWIP)
POWDER_FLOOR = dict(handling="cells", sieve_wash=True, promote_chain=False, wip=WIP)


def _ladder() -> list[dict]:
    """Rungs, each the one before plus one change: what the change is, why (the bottleneck the rung before found),
    and what it takes. Cumulative."""
    rungs = []

    def add(key, label, change, needs, **kw):
        base = dict(rungs[-1]["scenario"]) if rungs else {}
        for k, v in kw.items():
            base[k] = {**base.get(k, {}), **v} if isinstance(v, dict) and k in ("pools", "dur", "trays") else v
        rungs.append(dict(key=key, label=label, change=change, needs=needs, scenario=base))

    add("R0", "The finale's lab", "as the finale models it (timelapse.py, no upkeep)",
        "nothing: 1 rePowder, 1 MIDI, 2 MiR250 + UR10e units, the crucible on a day shift")
    add("R1", "The same lab, handling counted in full",
        "the arm's whole time at each station and both carries; a tray held at its Shuttle's opening while the arm "
        "works it; the sieves washed after each run; promoted runs side by side",
        "nothing new: a more honest baseline", handling="full", sieve_wash=True, promote_chain=False, wip=WIP)
    add("R2", "The crucible round the clock",
        "a crucible-trained person on every shift, 7 days (or a crucible robot: the same result)",
        "about 4.2 FTE of crucible cover (168 h a week), or the crucible automated (notes/crucible_automation.md)",
        crucible="shifts", shifts="3x7", people=1)
    add("R3", "Promoted alloys from the 400 cm³ crucible",
        "a promoted alloy's 440 g of fines from 684 g charges: 3 more runs, not 8",
        "AMAZEMET's 400 cm³ crucible (DAL #219; 'coming soon' on AMAZEMET's configurator)", promote_charge_g=684.0)
    add("R4", "Three Aconity MIDIs", "two more MIDIs, each with the 55 mm kit", "2 more LPBF machines",
        pools={"aconity": 3})
    add("R5", "Floor cells with arms of their own",
        "the charge station, the atomizers and sieving, the printers, sample prep and the tensile line each on the "
        "floor with a fixed arm; the Shuttles keep the measuring instruments; the MiR250s only carry between them",
        "5 fixed cobots (charge, powder, print, prep, tensile); the doser, press, furnace, mount press, polisher, "
        "Carvera and zwickiLine moved off their trays", handling="cells")
    add("R6", "A second rePowder", "a second atomizer; the same one crucible person a shift serves both",
        "1 more rePowder", atomizers=2)
    add("R7", "The test line doubled",
        "two heat treatments at once (a second furnace, or one loaded with two alloys' bars at a time), a second "
        "CubXL, a second sieve-wash module",
        "furnace capacity x2, 1 more CubXL + potentiostat, 1 more wash module",
        pools={"furnace": 2, "cubxl_corrosion": 2, "sieve_wash": 2})
    add("R8", "Second arms in the powder and prep cells", "a second fixed arm in each of the two busiest cells",
        "2 more fixed cobots", pools={"arm:powder": 2, "arm:prep": 2})
    add("R9", "A fourth MIDI", "one more LPBF machine", "1 more MIDI", pools={"aconity": 4})
    add("R10", "A third rePowder", "a third atomizer; still one crucible person a shift (about 70 % busy)",
        "1 more rePowder", atomizers=3)
    add("R11", "Margin: a hot frame and a unit more",
        "a second frame with a hot chamber, and a third MiR250 + UR10e for the carries between cells and Shuttles",
        "1 more frame + chamber, 1 more MiR250 + UR10e", pools={"instron_floor": 2}, units=3)
    return rungs


def _ded() -> list[dict]:
    """The other front end: DED blocks, blended in the melt pool, screen the compositions; the best one in ten goes
    through the powder route as the lab has it now (one rePowder on day-shift slots, one MIDI)."""
    rungs = []

    def add(key, label, change, needs, **kw):
        base = dict(rungs[-1]["scenario"]) if rungs else dict(POWDER_FLOOR, front="ded")
        for k, v in kw.items():
            base[k] = {**base.get(k, {}), **v} if isinstance(v, dict) and k in ("pools", "dur", "trays") else v
        rungs.append(dict(key=key, label=label, change=change, needs=needs, scenario=base))

    add("D1", "An MX-Lab screens, the cells test",
        "one InssTek MX-Lab printing 8 small blocks a plate, one composition each, blended from its feeders; the "
        "floor cells of R5; the powder route only for the best one in ten",
        "1 MX-Lab (DED); 5 fixed cobots; the rePowder and MIDI as now, on a day shift")
    add("D2", "The test line doubled", "two furnace loads at once and a second CubXL",
        "furnace capacity x2, 1 more CubXL + potentiostat", pools={"furnace": 2, "cubxl_corrosion": 2})
    add("D3", "A second arm in the prep cell", "a second fixed arm in sample prep", "1 more fixed cobot",
        pools={"arm:prep": 2})
    return rungs


LADDER = _ladder()
DED_LADDER = _ded()


def sensitivity() -> dict:
    """Units of each front-end machine ten a day needs, against its cycle time and the promotion policy
    (capacity(): round the clock, at its availability, booked to u_max)."""
    out = {"atomizer": [], "lpbf": [], "ded": []}
    for cyc, parts in [(2.0, dict(person=0.75, run=0.85, cool=0.4)), (2.5, dict(person=1.0, run=1.0, cool=0.5)),
                       (3.0, dict(person=1.0, run=1.5, cool=0.5)), (4.0, dict(person=1.0, run=2.0, cool=1.0))]:
        for pol, kw in [("promoted from 300 g runs (the finale)", dict()),
                        ("promoted from 684 g runs (400 cm³)", dict(promote_charge_g=684.0)),
                        ("promoted powder bought", dict(promote_source="vendor"))]:
            S = scenario(atom=parts, handling="cells", sieve_wash=True, **kw)
            r = capacity(S)["rows"]["repowder"]
            runs = multiplicity(S)["atomize"]
            out["atomizer"].append(dict(cycle_h=cyc, promotion=pol, runs_per_tested=round(runs, 3),
                                        runs_per_day_per_unit=round(24 * r["availability"] *
                                                                    ASSUMED["u_max"]["value"] / cyc, 2),
                                        tested_per_day_per_unit=r["practical_per_unit"],
                                        units_for_10=r["units_for_target"]))
    for label, h in [("MIDI as modelled: 5.0 h a build (inert 0.5, build 3, cool 0.5, unload and powder change 1)",
                      5.0),
                     ("MIDI with a second process chamber: 3.75 h on the machine (assumed)", 3.75),
                     ("MIDI, shorter screening build (2 mm specimens, 1.5 h of scanning) and a second chamber", 2.25)]:
        S = scenario(handling="cells", sieve_wash=True, promote_charge_g=684.0, dur={"print": h})
        r = capacity(S)["rows"]["aconity"]
        out["lpbf"].append(dict(option=label, print_h=h, h_per_tested=r["h_per_alloy"],
                                tested_per_day_per_unit=r["practical_per_unit"], units_for_10=r["units_for_target"]))
    for label, per, ph in [("8 blocks of about 1 cm³ a plate, 8 h (1.5 cm³/h, datasheet)", 8, 8.0),
                           ("16 blocks a plate, 14 h", 16, 14.0),
                           ("25 blocks of 1 cm³ in 5 h, as Islam, Nelaturu & Thoma 2021 did on a LENS", 25, 6.0)]:
        S = scenario(front="ded", handling="cells", ded=dict(units=1, per_plate=per, plate_h=ph))
        r = capacity(S)["rows"]["ded"]
        out["ded"].append(dict(option=label, per_plate=per, plate_h=ph, h_per_tested=r["h_per_alloy"],
                               tested_per_day_per_unit=r["practical_per_unit"], units_for_10=r["units_for_target"]))
    return out


def run_ladder(rungs: list[dict]) -> list[dict]:
    out = []
    for r in rungs:
        S = scenario(**r["scenario"])
        res = simulate(S)
        m = measure(res)
        c = capacity(S)
        out.append(dict(key=r["key"], label=r["label"], change=r["change"], needs=r["needs"],
                        scenario={k: v for k, v in S.items() if v != DEFAULT.get(k)},
                        simulated=m, capacity=dict(limit=c["limit"], limit_per_day=c["limit_per_day"],
                                                   rows=c["rows"])))
        print(f"{r['key']:4s} {r['label']:44s} {m['tested_per_day']:6.2f} a day (capacity {c['limit_per_day']:.2f}, "
              f"{c['limit']}); busiest: {m['bottleneck']} {m['utilization'][m['bottleneck']]:.2f}", flush=True)
    return out


def machines(S: dict) -> int:
    """Pieces of equipment that get planned maintenance: every station's units, the mobile units and fixed arms."""
    S = scenario(**S) if "atomizers" not in S else S
    n = sum(1 for st in {r[1] for r in step_table(S)} if st not in ("ded", "sieve_wash"))
    n += S["atomizers"] - 1 + sum(v - 1 for k, v in S["pools"].items() if not k.startswith("arm:"))
    n += S["units"] + (sum(S["pools"].get("arm:" + c, 1) for c in CELLS) if S["handling"] == "cells" else 0)
    n += sum(S["pools"].get(k, 1) for k in ("sieve_wash",) if S["sieve_wash"])
    n += S["ded"]["units"] if S["front"] == "ded" else 0
    return n


def staffing(rung: dict, base_rung: dict) -> dict:
    """People's hours a week at a rung, scaled from upkeep.py's year at about one alloy a day (out/upkeep_model.json):
    the crucible by runs, consumables and repairs by alloys, planned maintenance, IT, charts, vendors and safety by
    pieces of equipment. A rough scaling, not upkeep.py re-run at ten a day."""
    up = json.loads((OUT / "upkeep_model.json").read_text())["people_hours_per_week"]["by_kind_mean_after_ramp"]
    S, B0 = scenario(**rung["scenario"]), scenario(**base_rung["scenario"])
    m, m0 = rung["simulated"], base_rung["simulated"]
    use = m["tested_per_day"] / m0["tested_per_day"]
    kit = machines(S) / machines(B0)
    crucible = 0.0 if S["crucible"] == "robot" else m["runs_per_day"] * 7 * S["atom"]["person"]
    h = dict(crucible=round(crucible, 1), pm=round(up["pm"] * kit, 1), consumables=round(up["consumables"] * use, 1),
             repair=round(up["repair"] * use, 1), it=round(up["it"] * kit, 1), review=round(up["review"] * kit, 1),
             vendor=round(up["vendor"] * kit, 1), compliance=round(up["compliance"] * kit, 1))
    total = sum(h.values())
    cover = 0.0
    if S["crucible"] == "shifts":
        days, h0, h1 = SHIFTS[S["shifts"]]
        cover = days * (h1 - h0) * S["people"]
    return dict(hours_per_week=h, total=round(total, 1), fte_40h=round(total / 40, 1),
                crucible_cover_h_per_week=cover, fte_for_cover=round(cover / 40, 1),
                scale=dict(alloys=round(use, 2), equipment=round(kit, 2), equipment_count=machines(S),
                           equipment_count_base=machines(B0)))


def consumables(rung: dict) -> dict:
    """What ten a day goes through, per day (from the rung's simulated rates)."""
    m = rung["simulated"]
    S = scenario(**rung["scenario"])
    good = m["runs_per_day"] * (1 - 1 / S["run_fail_every"])
    fb = 1 - 1 / S["build_fail_every"]
    builds = (m["tested_per_day"] if S["front"] == "powder" else m["promoted_per_day"]) / fb
    return dict(runs=round(m["runs_per_day"], 1), charge_cups=round(4 * m["runs_per_day"], 1),
                sieved_jars=round(5 * good, 1), store_full_in_days=round(581 / max(5 * good, 1e-9), 1),
                screening_plates=round(builds, 1),
                full_plates=round(m["promoted_per_day"], 2) if S["front"] == "powder" else 0.0,
                mounts=round(2 * m["tested_per_day"], 1), tensile_specimens=round(4 * m["tested_per_day"], 1),
                instrument_data_gb=round(6.5 * m["tested_per_day"], 1),
                note="4 cups a run (chapter 1), 5 sieved cuts a good run (chapter 3), the 581-jar store (trays N, O), "
                     "2 mounts and 4 specimens an alloy (STEPS), about 6.5 GB an alloy (the finale's year: 1,974 GB "
                     "for 304 alloys)")


# ------------------------------------------------------------------------------------------------ figures
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf",
       "#1c5cab", "#184f95", "#104281", "#0d366b"]
NAMES = {"aconity": "Aconity MIDI (LPBF)", "repowder": "rePowder (atomizer)", "furnace": "furnace (heat treat)",
         "cubxl_corrosion": "CubXL (corrosion)", "carousel": "multi-doser + press (charge)",
         "instron_floor": "68FM-100 + chamber (hot tensile)", "sieve_cell": "sieve shaker",
         "sieve_wash": "sieve wash module", "wire_edm": "wire EDM", "sem": "SEM", "polisher": "PX500 polisher",
         "nanoindenter": "iMicro nanoindenter", "xrd": "MiniFlex XRD", "tensile_h": "zwickiLine (RT tensile)",
         "mount_press": "MX400 mount press", "xrf": "S2 PUMA XRF", "vhx": "VHX", "cnc": "Carvera CNC",
         "hardness": "HM-220 micro-Vickers", "mastersizer": "Mastersizer", "pip": "PIP", "ded": "MX-Lab (DED)",
         "units": "MiR250 + UR10e units", "opening1": "Shuttle 1's opening", "opening2": "Shuttle 2's opening",
         "atomizer_slots": "the crucible's day-shift slots", "crucible_people": "crucible people on shift",
         "arm:charge": "charge cell's arm", "arm:powder": "powder cell's arm", "arm:print": "print cell's arm",
         "arm:prep": "prep cell's arm", "arm:tensile": "tensile cell's arm",
         "crucible (staffed slots)": "the crucible's day-shift slots",
         "crucible (people on shift)": "crucible people on shift"}


def _style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def fig_ladder(lad: list[dict], ded: list[dict], path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    rows = [("powder", r) for r in lad] + [("ded", r) for r in ded]
    fig, ax = plt.subplots(figsize=(13.5, 0.46 * len(rows) + 2.2), dpi=150)
    fig.patch.set_facecolor(SURF)
    _style(ax)
    ax.grid(False)
    ys, y = [], 0.0
    for i, (grp, r) in enumerate(rows):
        if i and grp != rows[i - 1][0]:
            y += 0.9
        ys.append(y)
        y += 1.0
    bar_max, col = 13.0, 13.6
    for gx in range(2, 14, 2):
        ax.plot([gx, gx], [ys[0] - 0.6, ys[-1] + 0.6], color=GRID, lw=0.8, zorder=1)
    for (grp, r), yy in zip(rows, ys):
        v = r["simulated"]["tested_per_day"]
        ax.barh(yy, v, height=0.62, color=BLUE if grp == "powder" else ORANGE, zorder=2)
        b = r["simulated"]["bottleneck"]
        ax.text(v + 0.12, yy, f"{v:.1f}", va="center", ha="left", fontsize=9.5, color=INK, fontweight="bold",
                zorder=4, bbox=dict(facecolor=SURF, edgecolor="none", pad=0.6))
        ax.text(col, yy, f"{NAMES.get(b, b)} ({r['simulated']['utilization'][b]:.0%} busy)", va="center",
                ha="left", fontsize=8.6, color=INK2)
    ax.text(col, ys[0] - 0.95, "next limit (the busiest resource)", fontsize=8.6, color=INK2, va="bottom",
            fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['key']}  {r['label']}" for _, r in rows], fontsize=9, color=INK)
    ax.set_ylim(ys[-1] + 0.7, ys[0] - 1.3)
    ax.plot([TARGET, TARGET], [ys[0] - 0.6, ys[-1] + 0.6], color=INK, lw=1.2, ls=(0, (4, 3)), zorder=3)
    ax.text(TARGET, ys[0] - 0.75, "10 a day", ha="center", va="bottom", fontsize=9, color=INK)
    ax.set_xlim(0, col + 7.6)
    ax.set_xticks(range(0, 14, 2))
    ax.spines["bottom"].set_bounds(0, bar_max)
    ax.set_xlabel("fully tested alloys a day (simulated; steady state, weeks 7-20)", color=INK2, fontsize=9.5,
                  loc="left")
    fig.legend(handles=[Patch(color=BLUE, label="powder route: atomize, sieve, LPBF, then test (each rung adds "
                                              "one change to the rung above)"),
                        Patch(color=ORANGE, label="DED front end: blocks blended in the melt pool, then the same "
                                                "tests; the best 1 in 10 through the powder route")],
               loc="upper left", bbox_to_anchor=(0.008, 0.955), frameon=False, fontsize=8.6, labelcolor=INK2,
               ncol=1)
    fig.suptitle("From about one fully tested alloy a day to ten: the bottleneck, rung by rung", x=0.01, ha="left",
                 fontsize=13, color=INK, y=0.995)
    fig.text(0.01, 0.005, "A model (bottleneck.py on timelapse.py's schedule), not a measurement. Everything runs "
             "round the clock except where a rung says otherwise; upkeep and faults are not booked.",
             fontsize=7.8, color=MUTED, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.02, 1, 0.885))
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)


def fig_capacity(cap: dict, ded_cap: dict, path: Path):
    """Each machine's ceiling, one unit round the clock, at the R5 lab's settings; the units ten a day needs."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [(k, v) for k, v in cap["rows"].items() if "practical_per_unit" in v]
    if "ded" in ded_cap["rows"]:
        rows.append(("ded", ded_cap["rows"]["ded"]))
    rows.sort(key=lambda kv: kv[1]["practical_per_unit"])
    rows = rows[:14][::-1]                                 # the most limiting at the top
    fig, ax = plt.subplots(figsize=(11.5, 0.42 * len(rows) + 1.8), dpi=150)
    fig.patch.set_facecolor(SURF)
    _style(ax)
    xmax = 30
    for i, (k, v) in enumerate(rows):
        p = v["practical_per_unit"]
        ax.barh(i, min(p, xmax), height=0.62, color=ORANGE if k == "ded" else BLUE, zorder=2)
        ax.text(min(p, xmax) + 0.3, i, f"{p:.1f}", va="center", fontsize=9, color=INK, fontweight="bold",
                zorder=4, bbox=dict(facecolor=SURF, edgecolor="none", pad=0.6))
        n = v["units_for_target"]
        ax.text(xmax + 4.6, i, f"{n}", va="center", ha="right", fontsize=9.5, color=INK,
                fontweight="bold" if n > 1 else "normal")
        ax.text(xmax + 5.2, i, f"{v['h_per_alloy']:.2f} h", va="center", ha="left", fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([NAMES.get(k, k) for k, _ in rows], fontsize=9, color=INK)
    ax.axvline(TARGET, color=INK, lw=1.2, ls=(0, (4, 3)), zorder=3)
    ax.text(TARGET, len(rows) - 0.35, "10 a day", ha="center", va="bottom", fontsize=9, color=INK)
    ax.text(xmax + 4.6, len(rows) - 0.35, "units for 10", ha="right", va="bottom", fontsize=8.5, color=INK2)
    ax.text(xmax + 5.2, len(rows) - 0.35, "h per alloy", ha="left", va="bottom", fontsize=8.5, color=INK2)
    ax.set_xlim(0, xmax + 9)
    ax.set_xticks(range(0, xmax + 1, 5))
    ax.set_ylim(-0.6, len(rows) + 0.4)
    ax.set_xlabel("fully tested alloys a day that one unit can carry (round the clock, at its availability, "
                  "booked to 85 %)", color=INK2, fontsize=9.5)
    fig.suptitle("What one of each machine can do, and how many ten a day needs", x=0.01, ha="left", fontsize=13,
                 color=INK, y=0.995)
    fig.text(0.01, 0.005, "Hours per alloy include runs that drip (1 in 10), builds that fail (1 in 7) and the "
             "promoted 1 in 10 (400 cm³ runs, a full-plate build, E8 bars). Orange: the DED front end instead of "
             "atomizing and printing.", fontsize=7.8, color=MUTED, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)


def fig_utilization(lad: list[dict], path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    keys = ["atomizer_slots", "crucible_people", "repowder", "aconity", "carousel", "sieve_wash", "furnace",
            "cubxl_corrosion", "instron_floor", "wire_edm", "units", "opening1", "opening2", "arm:charge",
            "arm:powder", "arm:print", "arm:prep", "arm:tensile"]
    keys = [k for k in keys if any(k in r["simulated"]["utilization"] for r in lad)]
    M = np.full((len(keys), len(lad)), np.nan)
    for j, r in enumerate(lad):
        for i, k in enumerate(keys):
            if k in r["simulated"]["utilization"]:
                M[i, j] = r["simulated"]["utilization"][k]
    cmap = LinearSegmentedColormap.from_list("seq", SEQ)
    cmap.set_bad(SURF)
    fig, ax = plt.subplots(figsize=(12.5, 0.36 * len(keys) + 2.2), dpi=150)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    ax.imshow(np.ma.masked_invalid(M), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i in range(len(keys)):
        for j in range(len(lad)):
            if not np.isnan(M[i, j]):
                v = M[i, j]
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=7.6,
                        color="#ffffff" if v > 0.55 else INK)
            else:
                ax.text(j, i, "–", ha="center", va="center", fontsize=7.6, color=MUTED)
    for j, r in enumerate(lad):
        b = r["simulated"]["bottleneck"]
        if b in keys:
            i = keys.index(b)
            ax.add_patch(plt.Rectangle((j - 0.48, i - 0.46), 0.96, 0.92, fill=False, ec=ORANGE, lw=2.0))
    ax.set_xticks(range(len(lad)))
    ax.set_xticklabels([f"{r['key']}\n{r['simulated']['tested_per_day']:.1f}/d" for r in lad], fontsize=8.5,
                       color=INK)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([NAMES.get(k, k) for k in keys], fontsize=8.5, color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.suptitle("How busy each resource is, rung by rung (orange box: the busiest, the next bottleneck)", x=0.01,
                 ha="left", fontsize=12, color=INK, y=0.995)
    fig.text(0.01, 0.005, "Share of its hours booked, weeks 7-20; for the day-shift slots, the share of slots used. "
             "'–': not in that rung. Rungs as in bottleneck_ladder.png.", fontsize=7.8, color=MUTED, ha="left",
             va="bottom")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)


def main(argv):
    lad = run_ladder(LADDER)
    ded = run_ladder(DED_LADDER)
    if argv[1:2] == ["ladder"]:
        return
    sens = sensitivity()
    ref = scenario(**LADDER[5]["scenario"])                 # R5: cells, washed sieves, 400 cm³ promotions
    cap = capacity(ref)
    ded_cap = capacity(scenario(**DED_LADDER[0]["scenario"]))
    out = dict(
        what="Bottlenecks from about one fully tested alloy a day to ten (bottleneck.py): each machine's capacity "
             "per unit, and a ladder of scenarios on timelapse.py's schedule, generalised. A model, not a "
             "measurement.",
        question="Sterling, PR #318, 2026-11-08: 'Approx. one full alloy tested per day was the estimation. How can "
                 "we get that up to 10/day? What would be required?'",
        check=check(), target_per_day=TARGET, weeks=WEEKS, measured_from_week=W0 + 1,
        assumed=ASSUMED, cells=CELLS, attended=ATTEND, attended_h=ATTEND_H, wip=WIP,
        timelapse_params={k: v for k, v in T.PARAMS.items()},
        ladder=lad, ded_ladder=ded, sensitivity=sens,
        capacity_R5=cap, capacity_ded=ded_cap,
        capacity_R1_full_handling=capacity(scenario(**LADDER[1]["scenario"])),
        capacity_R11=capacity(scenario(**LADDER[-1]["scenario"])),
        staffing=dict(R0=staffing(lad[0], lad[0]), R11=staffing(lad[-1], lad[0]),
                      R11_crucible_robots=staffing(dict(lad[-1], scenario=dict(lad[-1]["scenario"], crucible="robot")),
                                                   lad[0]),
                      D3=staffing(ded[-1], lad[0])),
        consumables=dict(R0=consumables(lad[0]), R11=consumables(lad[-1]), D3=consumables(ded[-1])),
    )
    OUT.mkdir(exist_ok=True)
    (OUT / f"{NAME}.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    fig_ladder(lad, ded, OUT / f"{NAME}_ladder.png")
    fig_capacity(cap, ded_cap, OUT / f"{NAME}_capacity.png")
    fig_utilization(lad, OUT / f"{NAME}_utilization.png")
    print("wrote", OUT / f"{NAME}.json", "and three figures")


if __name__ == "__main__":
    main(sys.argv)

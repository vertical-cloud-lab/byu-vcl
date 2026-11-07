"""The finale (#303, round 8): the whole lab at speed, hour by hour, then day by day, week by week and month by month,
with what it has made and measured so far.

    python3 timelapse.py model                                  # the throughput model only -> out/timelapse_model.json
    VIZ3D_FPS=6 xvfb-run -a python3 timelapse.py                # the movie -> out/mp4/timelapse.mp4, out/timelapse.gif
    PREVIEW=1 xvfb-run -a python3 timelapse.py                  # nine frames -> /tmp/preview_timelapse.png

Sterling, on PR #318: "At the very end, I want you to show the entire laboratory operating in high-speed, starting by
the hour, then day-by-day, then by weeks and months showing the total dataset sizes, including number of unique alloys
fully tested and printed."

**The counters are a model, not a measurement.** ``simulate()`` schedules every alloy through the route the chapters
show, station by station, with each step's time taken from this branch's notes or from DAL, or marked as an assumption
(``STEPS``, ``PARAMS``; notes/timelapse.md lists every one with its source). It is a greedy schedule: each alloy in
turn, each step as soon as its inputs are ready, its station is free and a MiR250 + UR10e unit is free to carry it.
The one constraint from people: the atomizer's crucible is changed and coated by hand (notes/crucible_automation.md,
and Sterling: "Things related to the crucible in terms of automation are going to be very difficult"), so a run only
starts on a weekday shift. Everything after it runs round the clock, lights out.

**The animation** is the set-up movie's lab (setup_lab.build: two Shuttles, every tray loaded, the floor machines, the
two units), driven by the schedule: the tray a step needs comes to its Shuttle's opening while a unit loads or unloads
it, the units dock where the schedule says they are, and a status beacon on each floor machine shows its state. The
beacons are drawn for this clip; they are not a design. Frames are rendered one by one (no Scene.step), so the counters
and the clock change every frame while the 3-D scene only moves groups.

**Round 10: upkeep is in the schedule and on screen.** Sterling, on PR #318 (2026-11-07): "Something that's been on my
mind is maintenance over long-term and how that gets handled in workflows." ``sims()`` books upkeep.py's tasks and
seeded failures into the same schedule (calendar PM, consumables by use, the arms' reference checks, repairs), and the
film shows them: the one person on shift drawn where their task is (the atomizer's crucible, a tray held at a
Shuttle's opening with the units kept away, a floor machine, a unit on its charger), a vendor likewise, the beacons
amber while a station is out for upkeep and red while a fault waits for someone, and a card of counters at the right
edge, beside the throughput ones: people's hours this week, upkeep hours and tasks so far, availability so far. The
chart and the totals card set the year against the same schedule with no upkeep at all (round 8's).
"""
from __future__ import annotations

import bisect
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FPS = int(os.environ.get("VIZ3D_FPS", "15"))
PREVIEW = bool(os.environ.get("PREVIEW"))
NAME = "timelapse"
TITLE = "Vertical cloud lab: the whole lab at speed"
YEAR_H = 52 * 7 * 24.0 - 6.1                 # 52 calendar weeks: to Sunday 23:54 of week 52

# ================================================================================================ the model
# Every number the schedule uses, with where it comes from. "assumed" marks a layout or planning choice of ours.
PARAMS = {
    "shift": dict(value=(8.0, 16.0), unit="h of day, Mon-Fri",
                  source="assumed: one person on a day shift, for the atomizer's crucible (notes/crucible_automation.md)"),
    "run_starts": dict(value=(8.0, 10.5, 13.0), unit="h of day",
                       source="assumed: a run needs its person for the first 1.0 h (crucible out, cleaned, BN-coated or "
                              "swapped, loaded), so three runs fit an 8 h shift"),
    "runs_per_day_ramp": dict(value=[(0, 1), (14, 2), (28, 3)], unit="(day, runs a weekday)",
                              source="assumed: two weeks of one run a day while the lab is commissioned, two of two"),
    "friday_pm": dict(value="no run starts after 12:00 on Fridays", source="assumed: weekly maintenance"),
    "atomize_h": dict(value=dict(person=1.0, run=1.0, cool=0.5), unit="h",
                      source="a run about 1 h with prep (AMAZEMET training T5, 21:50) and a full cool-down about 30 min "
                             "(T3, 49:52), both in notes/crucible_automation.md; the person's hour is assumed"),
    "charge_per_run": dict(value=300.0, unit="g",
                           source="four cups as long as the Oct 27 rod pieces, about 300 g (notes/alloy_atomize.md, "
                                  "'Four cups a run'); chapter 1's 2.5 in cups hold 157 g"),
    "usable_frac": dict(value=0.91, source="the Oct 27 bronze run: 91 % under 250 um (DAL #219, notes/alloy_atomize.md)"),
    "fines_frac": dict(value=0.17, source="the same run: 17 % of the charge under 63 um, the MIDI's cut (DAL #219); an "
                                          "upper estimate for Al, which atomizes coarser"),
    "run_fail_every": dict(value=10, source="assumed: one run in ten drips instead of atomizing, as the Oct 8 Al 6063 "
                                            "run did (notes/alloy_atomize.md)"),
    "screen_build_g": dict(value=30.0, unit="g",
                           source="the MIDI's 55 mm reduction kit takes about 30 g (DAL #138, notes/alloy_print.md)"),
    "full_build_g": dict(value=440.0, unit="g",
                         source="the full 170 mm cylinder, the lab's planning figure (powder-doser design/"
                                "brainstorming.md section 3, notes/alloy_atomize.md)"),
    "build_fail_every": dict(value=7, source="assumed: one screening build in seven cracks or delaminates, and that "
                                             "alloy stops at its powder data"),
    "promote_every": dict(value=10, source="assumed: one fully tested alloy in ten is promoted to a full-plate build of "
                                           "chapter 5's E8 subsize bars"),
    "transfer_h": dict(value=0.1, unit="h",
                       source="assumed: a unit's drive plus pick and place, about 6 min (the MiR250 at 0.3 m/s^2, "
                              "props.ramp_secs; the arm's moves in chapters 1-7)"),
    "units": dict(value=2, source="two MiR250 + UR10e units (setup_lab.py)"),
    "stream_mbps": dict(value=1.0, unit="Mbit/s per camera",
                        source="assumed: each stream camera archived at 1 Mbit/s, 24 h a day"),
}

# (step, station, hours, needs, tray, what it makes, source). Station keys are the scene's (setup_lab ITEMS and
# FLOOR_PLAN keys). A tray step brings its tray to the opening while a unit loads it, and again to unload it; the
# instrument runs in storage, powered through its dock (services.py).
STEPS = [
    ("charge", "carousel", 1.0, [], "B", "4 cups dosed, weighed and pressed",
     "chapter 1: the HR-202i weighing, two layers a cup, the vacuum press's 2 min hold and 1 min program "
     "(notes/vacuum_press.md); about 15 min a cup, assumed"),
    ("atomize", "repowder", 2.5, ["charge"], None, "one atomizer run", "PARAMS atomize_h"),
    ("sieve", "sieve_cell", 0.75, ["atomize"], None, "5 sieved cuts in labelled jars",
     "assumed: four passes of minutes each (notes/alloy_print.md) plus stacking and tipping"),
    ("ld", "mastersizer", 0.25, ["sieve"], "E", "1 size distribution", "assumed: 3 repeats on the Aero S, and cleaning"),
    ("xrd", "xrd", 0.6, ["sieve"], "D", "1 XRD pattern",
     "assumed: back-loading prep (notes/edison_r8.md) and a 20-90 deg scan"),
    ("xrf", "xrf", 0.35, ["sieve"], "M", "1 XRF analysis", "assumed: a He-mode run on loose powder"),
    ("psem", "sem", 0.35, ["sieve"], "D", "6 SEM images of the powder", "assumed"),
    ("print", "aconity", 5.0, ["sieve"], None, "1 screening build",
     "assumed: inerting 0.5 h, a 3 h build of 5 mm-tall miniature specimens in the 55 mm kit, cooling 0.5 h, "
     "unloading and powder change 1 h"),
    ("depowder", "aconity", 0.5, ["print"], None, "", "chapter 5's lance and box; assumed 30 min"),
    ("edm", "wire_edm", 0.75, ["depowder"], None, "specimens off the plate",
     "at least 11 min of cutting (notes/alloy_workflow.md) plus the tank's fill and drain"),
    ("heat", "furnace", 3.0, ["edm"], "F", "1 heat treatment",
     "assumed: about 2 h at temperature plus heating and cooling"),
    ("tensile_rt", "tensile_h", 0.6, ["heat"], "L", "3 tensile tests at room temperature",
     "assumed: 3 miniature specimens on the zwickiLine Z5.0 TN, 10 min each with loading"),
    ("tensile_hot", "instron_floor", 1.5, ["heat"], None, "1 tensile test at temperature",
     "assumed: a soak in the 3119-608 chamber (r8_test.py) and the pull"),
    ("section", "wire_edm", 0.4, ["edm"], None, "2 sections", "chapter 6; assumed"),
    ("face", "cnc", 0.3, ["section"], "M", "2 faced slices", "chapter 6's Carvera; assumed"),
    ("mount", "mount_press", 0.6, ["face"], "F", "2 mounts",
     "the MX400's cycle (notes/alloy_prep.md: curing 0-30 min); assumed 18 min a mount"),
    ("polish", "polisher", 0.8, ["mount"], "F", "2 polished mounts",
     "the SOP's 9 min a mount on the clock (notes/alloy_characterize.md) plus disc changes"),
    ("sem", "sem", 0.5, ["polish"], "D", "12 SEM images, 2 EDS maps",
     "chapter 7's clock: about 20 min (notes/alloy_characterize.md), plus pump-down"),
    ("vhx", "vhx", 0.4, ["polish"], "K", "1 VHX 3-D reconstruction", "assumed"),
    ("hv", "hardness", 0.3, ["polish"], "L", "1 micro-Vickers map", "assumed: 10 indents"),
    ("nano", "nanoindenter", 0.75, ["polish"], "E", "1 nanoindentation grid",
     "chapter 7's clock: 45 min (notes/alloy_characterize.md)"),
    ("pip", "pip", 0.25, ["polish"], "E", "3 PIP tests", "assumed"),
    ("corrosion", "cubxl_corrosion", 2.2, ["polish"], "A", "2 corrosion spots",
     "67 min a spot with EIS (DAL copper_numbers.json, notes/cubxl_corrosion.md)"),
]
FULL = [  # a promoted alloy: more powder of the same composition, a full plate, chapter 5's E8 bars
    ("print_full", "aconity", 8.0, "1 full-plate build",
     "assumed: a 5 mm build on the 170 mm plate (chapter 5), inerting, cooling, unloading"),
    ("depowder_full", "aconity", 0.75, "", "assumed"),
    ("edm_full", "wire_edm", 1.0, "4 E8 subsize bars", "notes/alloy_workflow.md; assumed"),
    ("heat_full", "furnace", 3.0, "", "assumed"),
    ("e8_rt", "instron_floor", 0.6, "2 E8 tensile tests at room temperature", "assumed"),
    ("e8_hot", "instron_floor", 2.5, "2 E8 tensile tests at temperature", "assumed"),
]
# data per item, GB (all assumed; notes/timelapse.md): what a step adds to the lab's records
DATA_GB = {"atomize": 1.5, "print": 0.35, "print_full": 0.6, "psem": 0.04, "sem": 0.7, "xrd": 0.001, "xrf": 0.001,
           "ld": 0.002, "vhx": 1.5, "hv": 0.01, "nano": 0.05, "pip": 0.02, "corrosion": 0.01, "tensile_rt": 0.3,
           "tensile_hot": 0.1, "e8_rt": 0.2, "e8_hot": 0.2, "heat": 0.001, "heat_full": 0.001}
SHUTTLE_OF = {}          # tray -> Shuttle (1 or 2), from setup_lab.TRAYS's slots (filled by _shuttles())


def _shuttles() -> dict:
    if SHUTTLE_OF:
        return SHUTTLE_OF
    try:
        import setup_lab as SL
        import vlm as V
        SL.merge_r8()
        for k, (slot, _) in SL.TRAYS.items():
            SHUTTLE_OF[k] = V.SLOT_SHUTTLE.get(slot, 1)
    except Exception:                                  # noqa: BLE001  (the model runs without the scene's modules)
        SHUTTLE_OF.update({k: 1 for k in "ABCDEFJ"})
        SHUTTLE_OF.update({k: 2 for k in "GHIKLMNO"})
    return SHUTTLE_OF


def cameras() -> int:
    """The stream cameras the set-up movie puts in: every tray's (services.TRAY_CAMS, setup_lab.CAMS) and the two
    over the bays."""
    try:
        import services
        import setup_lab as SL
        SL.merge_r8()
        n = 0
        for k in SL.TRAYS:
            if services.TRAY_CAMS.get(k):
                n += len(services.TRAY_CAMS[k])
            elif k in SL.CAMS:
                n += len(SL.CAMS[k][0])
        return n + 2
    except Exception:                                  # noqa: BLE001
        return 32


def runs_today(day: int) -> int:
    n = 0
    for d0, k in PARAMS["runs_per_day_ramp"]["value"]:
        if day >= d0:
            n = k
    return n


def next_run_slot(t: float) -> float:
    """The first allowed atomizer start at or after t (hours from Monday 06:00 of week 1)."""
    starts = PARAMS["run_starts"]["value"]
    day = int((t + 6.0) // 24)
    while True:
        dow = day % 7                                       # 0 Monday
        if dow < 5:
            allowed = starts[:runs_today(day)]
            if dow == 4:
                allowed = [s for s in allowed if s < 12.0]
            for s in allowed:
                ts = day * 24.0 + s - 6.0
                if ts >= t - 1e-9:
                    return ts
        day += 1


# Round 10: the atomizer's charge may be carried over up to this long before its run slot and wait there, so a run
# isn't lost because both units are busy in the 6 min before the slot (round 8's schedule never hit that case).
ATOM_WAIT_H = 2.0


class Line:
    """A station's (or a unit's) bookings: non-overlapping intervals, sorted, so a later booking can use an earlier
    gap (the schedule books alloy by alloy, not in time order)."""

    def __init__(self):
        self.s: list[float] = []
        self.e: list[float] = []

    def earliest(self, t: float, d: float) -> float:
        i = bisect.bisect_right(self.e, t)
        while i < len(self.s):
            if self.s[i] >= t + d - 1e-9:
                return t
            t = max(t, self.e[i])
            i += 1
        return t

    def add(self, a: float, b: float):
        i = bisect.bisect_left(self.s, a)
        self.s.insert(i, a)
        self.e.insert(i, b)


def simulate(hours=YEAR_H, upkeep=None) -> dict:
    """The greedy schedule: events [{t0, t1, station, alloy, step, tray, shuttle, unit}] through `hours`. Each step
    starts once its inputs are done, its station has a free spell as long as the step, and a unit has the transfer
    time free just before it; an atomizer run also waits for a run slot on a staffed shift (next_run_slot).

    upkeep (round 10, an upkeep.Upkeep): maintenance booked into the same schedule. Its calendar tasks and robot-run
    checks are booked first (a check like a step: a unit, the tray at the opening); each alloy step may fail part-way
    and is run again after its repair; each finished step counts towards the usage-driven tasks; a step on a tray
    waits while a person has that Shuttle's opening. The record is in the result's "maint". With upkeep=None the
    schedule is round 8's, unchanged."""
    shuttles = _shuttles()
    lines: dict[str, Line] = {}
    ulines = [Line() for _ in range(PARAMS["units"]["value"])]
    unit_log: list[tuple[float, float, int, str]] = []     # (t0, t1, unit, station): a unit carrying to a station
    ev: list[dict] = []
    tr = PARAMS["transfer_h"]["value"]
    fail_run, fail_build = PARAMS["run_fail_every"]["value"], PARAMS["build_fail_every"]["value"]
    promote = PARAMS["promote_every"]["value"]
    alloys = []
    count = dict(runs=0, builds=0, tested=0)
    t_atom: list[float] = []                               # each alloy's atomizer start: a WIP limit on the charges

    last = [None]                                          # the last alloy step booked (maintenance books too)

    def book(station, ready, dur, step, alloy, tray=None, atom=False, maint=None):
        line = lines.setdefault(station, Line())
        t, bu = max(ready, 0.0), 0
        for _ in range(400):
            if atom:
                t = next_run_slot(t)
            t1 = line.earliest(t, dur)
            if t1 > t + 1e-9:
                t = t1
                continue
            if upkeep is not None:
                t2 = upkeep.presentable(tray, t, dur)
                if t2 > t + 1e-9:
                    t = t2
                    continue
            best = None
            for u, ul in enumerate(ulines):
                tu = ul.earliest(t - tr, tr) + tr
                tx = tu - tr
                if atom and tu > t + 1e-9:                 # the charge may go over earlier and wait at the atomizer
                    x = ul.earliest(max(ready, t - ATOM_WAIT_H), tr)
                    if x + tr <= t + 1e-9:
                        tu, tx = t, x
                if best is None or tu < best[1]:
                    best = (u, tu, tx)
            bu, tx = best[0], best[2]
            if best[1] > t + 1e-9:
                t = best[1]
                continue
            break
        if upkeep is not None and maint is None:
            t_f = upkeep.breaks(station, t, dur)
            if t_f is not None:                             # it fails part-way: repaired, then run again
                line.add(t, t_f)
                ulines[bu].add(tx, tx + tr)
                unit_log.append((tx, tx + tr, bu, station))
                ev.append(dict(t0=t, t1=t_f, station=station, alloy=alloy, step=step, tray=tray,
                               shuttle=shuttles.get(tray) if tray else None, unit=bu, interrupted=True))
                t_r = upkeep.repair(station, t_f)
                return book(station, t_r, dur, step, alloy, tray, atom)
        line.add(t, t + dur)
        ulines[bu].add(tx, tx + tr)
        unit_log.append((tx, tx + tr, bu, station))
        e = dict(t0=t, t1=t + dur, station=station, alloy=alloy, step=step, tray=tray,
                 shuttle=shuttles.get(tray) if tray else None, unit=bu)
        if maint is not None:
            e["maint"] = maint
        ev.append(e)
        if maint is None:
            last[0] = e
            if upkeep is not None:
                upkeep.used(e)
        return t + dur

    if upkeep is not None:
        upkeep.start(lines, ulines, book, ev, hours, shuttles)

    def run(alloy, ready, repeat=False):
        """Charge and atomize, again if the run drips. -> the good run's end."""
        while True:
            e_c = book("carousel", ready, STEPS[0][2], "charge", alloy, "B")
            count["runs"] += 1
            e_a = book("repowder", e_c, STEPS[1][2], "atomize", alloy, atom=True)
            last[0]["run"] = count["runs"]
            if repeat:
                last[0]["repeat"] = True
            if count["runs"] % fail_run == fail_run - 3:        # this run dripped
                last[0]["failed"] = True
                ready = e_a
                continue
            return e_a, last[0]["t0"]

    a = 0
    while a < 5000:
        ready = t_atom[a - 2] if a >= 2 else 0.0
        e_atom, t0_atom = run(a, ready)
        if e_atom > hours:
            break
        t_atom.append(t0_atom)
        done = {"atomize": e_atom}
        rec = dict(alloy=a, atomized=e_atom)
        for step, station, h, needs, tray, _, _ in STEPS[2:7]:          # the sieve, then the powder's checks
            done[step] = book(station, max(done[n] for n in needs), h, step, a, tray)
        rec["powder_done"] = max(done[k] for k in ("ld", "xrd", "xrf", "psem"))
        count["builds"] += 1
        printable = count["builds"] % fail_build != 0
        done["print"] = book("aconity", done["sieve"], STEPS[7][2], "print", a)
        last[0]["failed"] = not printable
        if printable:
            rec["printed"] = done["print"]
            for step, station, h, needs, tray, _, _ in STEPS[8:]:
                done[step] = book(station, max(done[n] for n in needs), h, step, a, tray)
            rec["tested"] = max(done[k] for k in ("tensile_rt", "tensile_hot", "sem", "vhx", "hv", "nano", "pip",
                                                  "corrosion"))
            count["tested"] += 1
            if count["tested"] % promote == 0:                     # promoted: powder for a full plate
                per = PARAMS["charge_per_run"]["value"] * PARAMS["fines_frac"]["value"]
                extra = max(0, math.ceil(PARAMS["full_build_g"]["value"] / per) - 1)
                t = rec["tested"]
                for _ in range(extra):
                    t, _t0 = run(a, t, repeat=True)
                    t = book("sieve_cell", t, STEPS[2][2], "sieve", a)
                for step, station, h, _, _ in FULL:
                    t = book(station, t, h, step, a)
                rec["promoted"] = t
        alloys.append(rec)
        a += 1
    ev.sort(key=lambda e: e["t0"])
    unit_log.sort()
    out = dict(events=ev, alloys=alloys, unit_log=unit_log, runs=count["runs"])
    if upkeep is not None:
        out["maint"] = upkeep.finish()
    return out


# per step, what it adds to each counter
YIELD = {
    "tensile": {"tensile_rt": 3, "tensile_hot": 1, "e8_rt": 2, "e8_hot": 2},
    "sem_images": {"psem": 6, "sem": 14},
    "xrd": {"xrd": 1}, "xrf": {"xrf": 1}, "psd": {"ld": 1},
    "indents": {"hv": 1, "nano": 1, "pip": 1},
    "corrosion": {"corrosion": 2},
}


def counters(sim: dict, t: float, ncam: int) -> dict:
    """Everything made and measured by lab time t (hours)."""
    ev = sim["events"]
    out = dict(atomized=0, printed=0, tested=0, promoted=0, runs=0, powder_kg=0.0, data_gb=0.0, video_tb=0.0)
    for k in YIELD:
        out[k] = 0
    g_run = PARAMS["charge_per_run"]["value"] * PARAMS["usable_frac"]["value"] / 1000.0
    for e in ev:
        if e["t1"] > t or e.get("interrupted"):
            continue
        s = e["step"]
        if s == "atomize":
            out["runs"] += 1
            if not e.get("failed"):
                out["powder_kg"] += g_run
        for k, d in YIELD.items():
            out[k] += d.get(s, 0)
        out["data_gb"] += DATA_GB.get(s, 0.0)
    for r in sim["alloys"]:
        out["atomized"] += r["atomized"] <= t
        out["printed"] += r.get("printed", 1e18) <= t
        out["tested"] += r.get("tested", 1e18) <= t
        out["promoted"] += r.get("promoted", 1e18) <= t
    out["video_tb"] = ncam * PARAMS["stream_mbps"]["value"] / 8 * 3600 * max(t, 0.0) / 1e6
    return out


def busy(sim: dict, t: float) -> dict:
    """station -> the event running there at t (or absent)."""
    out = {}
    for e in sim["events"]:
        if e["t0"] <= t < e["t1"]:
            out[e["station"]] = e
        elif e["t0"] > t + 24 * 30:
            break
    return out


def utilization(sim: dict, t0: float, t1: float) -> dict:
    tot: dict[str, float] = {}
    for e in sim["events"]:
        a, b = max(e["t0"], t0), min(e["t1"], t1)
        if b > a:
            tot[e["station"]] = tot.get(e["station"], 0.0) + (b - a)
    return {k: v / (t1 - t0) for k, v in sorted(tot.items(), key=lambda kv: -kv[1])}


_SIMS: dict = {}


def sims() -> tuple[dict, dict]:
    """(the year with upkeep.py's maintenance and failures booked into it, as the finale shows it since round 10; the
    same schedule with none, as round 8 had it). Cached."""
    if not _SIMS:
        import upkeep as UK
        _SIMS["up"] = simulate(upkeep=UK.Upkeep())
        _SIMS["base"] = simulate()
    return _SIMS["up"], _SIMS["base"]


def upkeep_summary(sim: dict, base: dict) -> dict:
    """What the year's upkeep costs, from upkeep.py's own measures of the same schedule (out/upkeep_model.json has
    every task with its interval, who does it and its source)."""
    import upkeep as UK
    log = sim["maint"]
    av = UK.availability(sim)
    ppl = UK.weekly_people(sim)
    steady = range(8, 52)
    wk = [sum(ppl[k][i] for k in UK.KINDS) for i in range(52)]
    mean = {k: float(np.mean([ppl[k][i] for i in steady])) for k in UK.KINDS}
    people_h = sum(r["person_h"] for r in log if r["who"] in UK.PEOPLE or r["who"] == "vendor")   # hosting a vendor too
    arm_h = sum(r["t1"] - r["t0"] for r in log if r["who"] == "arm")
    tested = [sum(1 for r in x["alloys"] if r.get("tested", 1e18) <= YEAR_H) for x in (sim, base)]
    atom = [sum(1 for r in x["alloys"] if r["atomized"] <= YEAR_H) for x in (sim, base)]
    route = [k for k in UK.ROUTE if k in av]
    return dict(
        what="upkeep.py's tasks and seeded failures booked into this schedule: calendar PM, consumables by use, the "
             "arms' reference checks (control charts), repairs by a person on the next shift or a vendor after a wait "
             "for parts. A model; out/upkeep_model.json has every task with its source.",
        people_hours_per_week=dict(mean_after_ramp=round(float(np.mean([wk[i] for i in steady])), 1),
                                   max=round(max(wk), 1), crucible=round(mean["crucible"], 1),
                                   upkeep=round(sum(v for k, v in mean.items() if k != "crucible"), 1),
                                   of_a_shift_week=40.0),
        tasks=dict(arm_checks=sum(1 for r in log if r["who"] == "arm"),
                   people=sum(1 for r in log if r["who"] in UK.PEOPLE and r["planned"]),
                   vendor_visits=sum(1 for r in log if r["who"] == "vendor" and r["planned"]),
                   machine_itself=sum(1 for r in log if r["who"] == "auto"),
                   repairs=sum(1 for r in log if not r["planned"])),
        hours=dict(people=round(people_h), arms=round(arm_h)),
        availability={k: v["availability"] for k, v in av.items()},
        availability_route_mean=round(float(np.mean([av[k]["availability"] for k in route])), 4),
        alloys_a_year=dict(atomized_with_upkeep=atom[0], atomized_without=atom[1], tested_with_upkeep=tested[0],
                           tested_without=tested[1]),
    )


def model(write=True) -> dict:
    sim, base = sims()
    ncam = cameras()
    marks = {"1 day": 24, "1 week": 168, "4 weeks": 672, "13 weeks": 2184, "26 weeks": 4368, "1 year": YEAR_H}
    at = {k: {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in counters(sim, h, ncam).items()}
          for k, h in marks.items()}
    at_base = {k: {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in counters(base, h, ncam).items()}
               for k, h in marks.items()}
    lat = [r["tested"] - r["atomized"] for r in sim["alloys"] if "tested" in r]
    first = min((r["tested"] for r in sim["alloys"] if "tested" in r), default=None)
    util = utilization(sim, 24 * 28, YEAR_H)
    slots, t = 0, 0.0                                      # the atomizer's staffed run slots in the year
    while True:
        t = next_run_slot(t)
        if t + STEPS[1][2] > YEAR_H:
            break
        slots += 1
        t += 0.01
    used = sum(1 for e in sim["events"] if e["step"] == "atomize" and e["t1"] <= YEAR_H and not e.get("interrupted"))
    out = dict(
        what="The lab at speed (timelapse.py): a greedy schedule of every alloy through the route of chapters 1-7, "
             "each step on its station, carried by two MiR250 + UR10e units; the atomizer's crucible changed by a "
             "person on weekday shifts, everything else round the clock; since round 10 with upkeep.py's maintenance "
             "and seeded failures booked into it. A model, not a measurement.",
        fully_tested="atomized powder measured (laser diffraction, XRD, XRF, SEM); printed in the 55 mm kit; heat "
                     "treated; tensile tested at room temperature and at temperature; sectioned, faced, mounted and "
                     "polished; SEM/EDS, VHX, micro-Vickers, nanoindentation and PIP; a corrosion screen on the CubXL",
        params=PARAMS,
        steps=[dict(step=s, station=st, hours=h, needs=n, tray=tr, makes=mk, source=src)
               for s, st, h, n, tr, mk, src in STEPS],
        promoted_steps=[dict(step=s, station=st, hours=h, makes=mk, source=src) for s, st, h, mk, src in FULL],
        data_gb_per_step=DATA_GB, stream_cameras=ncam,
        totals=at,
        totals_without_upkeep=at_base,
        upkeep=upkeep_summary(sim, base),
        first_alloy_fully_tested_h=round(first, 1) if first is not None else None,
        latency_atomized_to_tested_h=dict(median=round(float(np.median(lat)), 1), max=round(float(max(lat)), 1))
        if lat else None,
        utilization_after_ramp=dict((k, round(v, 3)) for k, v in util.items()),
        atomizer_slots=dict(used=used, available=slots,
                            note="a run starts only in a staffed slot (PARAMS run_starts, runs_per_day_ramp)"),
        bottleneck="repowder" if used >= 0.9 * slots else (next(iter(util)) if util else None),
    )
    if write:
        OUT.mkdir(exist_ok=True)
        (OUT / f"{NAME}_model.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


# ================================================================================================ the movie's clock
# (video seconds, lab hours from, lab hours to, label, caption). Lab time 0 is Monday 06:00 of the lab's first week.
PHASES = [
    (2.5, 0.0, 0.0, "Day 1",
     "The lab as set up: two Shuttles with every tray loaded and powered, the floor machines, two MiR250 + UR10e "
     "units on charge. The clock starts on a Monday at 06:00."),
    (30.0, 0.0, 24.0, "1/4  Hour by hour",
     "Hour by hour, the first day. One person comes in 08:00-16:00: the atomizer's crucible first, then the day's "
     "upkeep where it is done (a tray held at a Shuttle's opening with the units kept away, a floor machine, a unit "
     "on its charger). The arms run their reference checks between jobs, and keep going with the lights off."),
    (16.0, 24.0, 14 * 24.0, "2/4  Day by day",
     "Day by day. The atomizer runs only while someone is on site: one run a day while the lab is commissioned, then "
     "three a weekday. A beacon is amber while its machine is out for upkeep, red while a fault waits for the next "
     "shift or for parts; the rest runs round the clock."),
    (14.0, 14 * 24.0, 13 * 7 * 24.0, "3/4  Week by week",
     "Week by week. Upkeep takes {upkeep:.0f} of the person's 40 hours a week on average, the crucible {crucible:.0f} "
     "more. An alloy is fully tested about half a day after it is atomized; one in ten is promoted to a full plate of "
     "E8 bars."),
    (16.0, 13 * 7 * 24.0, YEAR_H, "4/4  Month by month",
     "Month by month, to the end of the first year. Upkeep and failures cost {lost} of the {without} alloys the same "
     "schedule would test with none (the faint line). A model built from each chapter's step times and the "
     "assumptions in notes/timelapse.md and notes/upkeep.md, not measurements."),
    (9.0, YEAR_H, YEAR_H, "The first year", ""),
]


def caption(i: int, m: dict | None) -> str:
    """Phase i's caption, its numbers from the model."""
    cap = " ".join(PHASES[i][4].split())
    if m is None or "{" not in cap:
        return cap
    ph, al = m["upkeep"]["people_hours_per_week"], m["upkeep"]["alloys_a_year"]
    return cap.format(upkeep=ph["upkeep"], crucible=ph["crucible"], without=al["tested_without"],
                      lost=al["tested_without"] - al["tested_with_upkeep"])


def phase_frames() -> list[tuple[int, int]]:
    out, n = [], 0
    for sec, *_ in PHASES:
        k = max(1, int(round(sec * FPS)))
        out.append((n, n + k))
        n += k
    return out


def lab_time(f: int) -> tuple[float, int, float]:
    """(lab hours, phase index, u within the phase) at frame f."""
    for i, ((a, b), (sec, h0, h1, *_)) in enumerate(zip(phase_frames(), PHASES)):
        if a <= f < b:
            u = (f - a) / max(1, b - a - 1)
            return h0 + (h1 - h0) * u, i, u
    sec, h0, h1, *_ = PHASES[-1]
    return h1, len(PHASES) - 1, 1.0


def clock_text(t: float) -> tuple[str, str]:
    t = max(t, 0.0) + 6.0
    day = int(t // 24)
    hh = t - day * 24
    dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][day % 7]
    week = day // 7 + 1
    return f"Day {day + 1}  ·  week {week}", f"{dow} {int(hh):02d}:{int((hh % 1) * 60):02d}"


def people_on(t: float) -> bool:
    t = t + 6.0
    day = int(t // 24)
    h = t - day * 24
    s0, s1 = PARAMS["shift"]["value"]
    return day % 7 < 5 and s0 <= h < s1


def speed_text(i: int) -> str:
    sec, h0, h1, *_ = PHASES[i]
    if h1 <= h0:
        return ""
    k = (h1 - h0) * 3600 / sec
    per = (h1 - h0) / sec
    if per < 1.0:
        what = f"{per * 60:.0f} min"
    elif per < 48:
        what = f"{per:.1f} h".replace(".0 h", " h")
    else:
        what = f"{per / 24:.1f} days".replace(".0 days", " days")
    return f"x{k:,.0f}: 1 s of video = {what}"


# ================================================================================================ the scene
STATION_NAMES = {
    "carousel": "multi-doser and vacuum press (tray B)", "repowder": "rePowder atomizer", "sieve_cell": "sieving cell",
    "mastersizer": "Mastersizer (tray E)", "xrd": "MiniFlex XRD (tray D)", "xrf": "S2 PUMA XRF (tray M)",
    "sem": "TM4000 SEM (tray D)", "aconity": "Aconity MIDI", "wire_edm": "wire EDM", "furnace": "furnace (tray F)",
    "tensile_h": "zwickiLine (tray L)", "instron_floor": "Instron 68FM-100", "cnc": "Carvera CNC (tray M)",
    "mount_press": "MX400 mounting press (tray F)", "polisher": "PX500 polisher (tray F)", "vhx": "VHX (tray K)",
    "hardness": "HM-220 hardness (tray L)", "nanoindenter": "iMicro (tray E)", "pip": "PLX-Benchtop PIP (tray E)",
    "cubxl_corrosion": "CubXL corrosion (tray A)",
}
STEP_WORDS = {
    "charge": "dosing and pressing cups", "atomize": "atomizing", "sieve": "sieving", "ld": "size distribution",
    "xrd": "XRD", "xrf": "XRF", "psem": "SEM of the powder", "print": "printing", "depowder": "depowdering",
    "edm": "cutting the specimens off", "heat": "heat treating", "tensile_rt": "tensile, room temperature",
    "tensile_hot": "tensile, at temperature", "section": "sectioning", "face": "facing the slice",
    "mount": "hot mounting", "polish": "grinding and polishing", "sem": "SEM and EDS", "vhx": "3-D imaging",
    "hv": "micro-Vickers", "nano": "nanoindentation", "pip": "PIP", "corrosion": "corrosion screen",
    "print_full": "printing a full plate", "depowder_full": "depowdering", "edm_full": "cutting E8 bars",
    "heat_full": "heat treating", "e8_rt": "E8 tensile, room temperature", "e8_hot": "E8 tensile, at temperature",
}
FLOOR_BEACONS = ["repowder", "sieve_cell", "aconity", "wire_edm", "instron_floor", "instron_small", "fumehood",
                 "packaging", "glovebox", "ded"]
C_RUN, C_UNIT, C_PERSON, C_IDLE, C_FAIL = (0.15, 0.78, 0.30), (0.20, 0.45, 0.95), (1.0, 0.68, 0.10), \
    (0.62, 0.64, 0.67), (0.92, 0.18, 0.16)
FOCUS = (700.0, -4300.0, 300.0)
CAM_W = [(-4300, -27500, 17800), FOCUS, (0, 0, 1)]
CAM_E = [(5700, -27500, 17800), FOCUS, (0, 0, 1)]
CAM_END = [(700, -24000, 23500), (700, -4000, 0), (0, 0, 1)]
# Every tray is built and the Shuttles are drawn see-through, as in the set-up movie that comes before this clip: a
# clad Shuttle, or one built with only the eight trays the schedule presents (setup_lab's VLAB_ONLY_TRAYS, about half
# the memory), would look like a different machine (PR #318: "9:09: suddenly the VLM only has a few things on board").


def cam_at(f: int, n: int) -> list:
    """A slow pan from the south-west to the south-east over the film, rising at the end, eased."""
    u = f / max(1, n - 1)
    a, b, w = (CAM_W, CAM_E, u / 0.8) if u < 0.8 else (CAM_E, CAM_END, (u - 0.8) / 0.2)
    w = min(1.0, max(0.0, w))
    w = w * w * (3 - 2 * w)
    return [tuple(float(x) + (float(y) - float(x)) * w for x, y in zip(p, q)) for p, q in zip(a, b)]


# ================================================================================================ upkeep on screen
class Spans:
    """Merged intervals with a running sum: is t covered, and how many hours of [a, b] are."""

    def __init__(self, iv):
        m: list[list[float]] = []
        for a, b in sorted(iv):
            if b <= a:
                continue
            if m and a <= m[-1][1]:
                m[-1][1] = max(m[-1][1], b)
            else:
                m.append([a, b])
        self.s = np.array([x[0] for x in m], float)
        self.e = np.array([x[1] for x in m], float)
        self.cum = np.concatenate([[0.0], np.cumsum(self.e - self.s)])

    def upto(self, t: float) -> float:
        i = int(np.searchsorted(self.s, t, side="right"))
        if i == 0:
            return 0.0
        return float(self.cum[i - 1] + min(t, self.e[i - 1]) - self.s[i - 1])

    def hours(self, a: float, b: float) -> float:
        return self.upto(b) - self.upto(a)

    def at(self, t: float) -> bool:
        i = int(np.searchsorted(self.s, t, side="right"))
        return i > 0 and t < self.e[i - 1]


class UpkeepView:
    """The year's maintenance record (sim["maint"], upkeep.py) as the film draws it: who is where at lab time t,
    which stations are out and why, and the running totals for the counters."""

    def __init__(self, sim: dict):
        import upkeep as UK
        self.UK = UK
        self.log = log = sim["maint"]
        self.lo = np.array([min(r["t0"], r["down"][0]) for r in log], float)
        self.hi = np.array([max(r["t1"], r["down"][1]) for r in log], float)
        wait, upk = {}, {}
        for r in log:
            if not r["planned"] and r["t0"] > r["down"][0]:
                wait.setdefault(r["own"], []).append((r["down"][0], r["t0"]))
            if r["who"] != "arm" and r["t1"] > r["t0"]:
                for k in set(r["stations"]) | {r["own"]}:
                    upk.setdefault(k, []).append((r["t0"], r["t1"]))
        self.wait = {k: Spans(v) for k, v in wait.items()}
        self.upk = {k: Spans(v) for k, v in upk.items()}
        self.none = Spans([])
        # out of use, every kind (upkeep.down_hours' rule), for availability so far
        down = {k: [] for k in UK.AVAIL_ROWS}
        for r in log:
            for st in down:
                if st == r.get("own") or (st == r["asset"] and not r["stations"]):
                    down[st].append(tuple(r["down"]))
                elif st in r["stations"]:
                    down[st].append((r["t0"], r["t1"]))
        self.down = {k: Spans(v) for k, v in down.items()}
        self.route = [k for k in UK.ROUTE]
        # the person's time: the crucible's hours, their upkeep (each task's segments) and hosting a vendor
        p_cru = PARAMS["atomize_h"]["value"]["person"]
        self.crucible = Spans([(e["t0"], e["t0"] + p_cru) for e in sim["events"] if e["step"] == "atomize"])
        pt = []
        for r in log:
            if r["who"] in UK.PEOPLE and r["person_h"] > 0:
                pt += [tuple(x) for x in (r.get("segments") or [[r["t0"], r["t1"]]])]
            elif r["who"] == "vendor" and r["person_h"] > 0:
                pt.append((r["t0"], r["t0"] + r["person_h"]))
        self.people = Spans(pt)
        self.arms = Spans([(r["t0"], r["t1"]) for r in log if r["who"] == "arm"])
        ends = lambda f: np.sort(np.array([r["t1"] for r in log if f(r)], float))          # noqa: E731
        self.done = dict(checks=ends(lambda r: r["who"] == "arm"),
                         tasks=ends(lambda r: r["planned"] and r["who"] not in ("arm", "auto")),
                         repairs=ends(lambda r: not r["planned"]))

    def state(self, key: str, t: float) -> str | None:
        """'wait' (a fault waiting for a person or parts), 'upkeep' (out for upkeep or a repair), or None."""
        if self.wait.get(key, self.none).at(t):
            return "wait"
        if self.upk.get(key, self.none).at(t):
            return "upkeep"
        return None

    def opening_of(self, r) -> tuple:
        """(Shuttle, tray or None) when record r holds a Shuttle's opening, else (None, None)."""
        for k in r["stations"]:
            if k in ("open1", "open2"):
                a = r["asset"]
                return int(k[-1]), (a[5:] if a.startswith("tray:") else self.UK.TRAY_OF.get(a))
        return None, None

    def now(self, t: float, on_site: bool):
        """(the person's task now or None, the vendor's or None, {Shuttle: tray} openings held, records for the
        'Running now' panel: (kind, record))."""
        person = vendor = None
        held, rows = {}, []
        for i in np.nonzero((self.lo <= t) & (t < self.hi))[0]:
            r = self.log[i]
            if not r["planned"] and r["down"][0] <= t < r["t0"]:
                rows.append(("wait", r))
                continue
            if not (r["t0"] <= t < r["t1"]) or r["who"] == "arm":
                continue
            sh, tray = self.opening_of(r)
            if sh:
                held[sh] = tray
            if r["who"] in ("opening", "extracted", "floor", "desk"):
                segs = r.get("segments") or [[r["t0"], r["t1"]]]
                if on_site and any(a <= t < b for a, b in segs) and (person is None or not r["planned"]):
                    person = r
                    continue
            elif r["who"] == "vendor" and on_site:
                vendor = r
                continue
            rows.append(("out", r))
        if person is not None:
            rows.insert(0, ("person", person))
        if vendor is not None:
            rows.insert(0, ("vendor", vendor))
        return person, vendor, held, rows

    def what_of(self, key: str) -> str:
        k = key.split(":")[0]
        for t_ in self.UK.TASKS:
            if t_["key"] == k:
                return t_["what"]
        return k

    def unit_out(self, i: int, t: float) -> bool:
        return self.state(f"unit{i}", t) is not None

    def counters(self, t: float) -> dict:
        w0 = (t // 168.0) * 168.0
        t = max(t, 0.0)
        av = lambda keys: 1.0 - sum(self.down[k].upto(t) for k in keys) / (len(keys) * t) if t > 1.0 else None  # noqa
        return dict(week_crucible=self.crucible.hours(w0, t), week_upkeep=self.people.hours(w0, t),
                    people=self.people.upto(t), arms=self.arms.upto(t),
                    checks=int(np.searchsorted(self.done["checks"], t, side="right")),
                    tasks=int(np.searchsorted(self.done["tasks"], t, side="right")),
                    repairs=int(np.searchsorted(self.done["repairs"], t, side="right")),
                    avail_route=av(self.route), avail_atom=av(["repowder"]), avail_units=av(["unit0", "unit1"]))


VENDOR_COAT = (0.20, 0.27, 0.42)          # a vendor's navy jacket, so the two figures read apart
UP_NAMES = dict(open1="Shuttle 1's opening", open2="Shuttle 2's opening", unit0="unit 1", unit1="unit 2",
                vlm1="Shuttle 1", vlm2="Shuttle 2", n2="the N2 generator", chiller="the chiller",
                glovebox="the gloveboxes", fumehood="the fume hood", depowder="the depowdering box",
                packaging="the packaging station", ded="the DED cell", staff="the lab", it="IT", site="the site")


def up_name(key: str) -> str:
    if key.startswith("tray:"):
        return f"tray {key[5:]}"
    return UP_NAMES.get(key) or STATION_NAMES.get(key, key)
LIP = -1612.0                             # the front of the blue cover under a Shuttle's opening (vlm.opening)


class Movie:
    def __init__(self, sim: dict, ncam: int):
        import animate as A
        import lab
        import pyvista as pv
        import setup_lab as SL
        import vlm as V
        import warehouse as W
        self.sim, self.ncam, self.A, self.V, self.W = sim, ncam, A, V, W
        data = lab.meshes()
        idata = SL.load_all()
        il = getattr(SL, "item_label", None)            # setup_lab's tray-item label, mid-edit in another stream:
        if il is not None:                                # the clip uses no item labels, so never let it stop the build
            def safe_label(inst, il=il):
                try:
                    return il(inst)
                except Exception:                       # noqa: BLE001
                    return getattr(inst, "model", "")
            SL.item_label = safe_label
        (self.sc, self.L, self.F, self.items, self.rigs, self.units, self.util, _, self.vp) = SL.build(
            data, idata, mp4=not PREVIEW, name=NAME, title=TITLE)
        sc, L = self.sc, self.L
        SL.add_bay_cams(sc)
        L.show_gauges = False
        L.skin(1.0)(1.0)                 # see-through, as in the set-up and every other clip: every tray shows
        # a beacon over every floor machine and each Shuttle: a pole and a lens, coloured by the schedule each frame
        self.beacons = {}

        def beacon(key, x, y, z):
            sc.add(f"beacon {key} pole", pv.Cylinder(center=(x, y, z + 250), direction=(0, 0, 1), radius=22,
                                                     height=500, resolution=16), (0.25, 0.26, 0.28), "beacons")
            lens = f"beacon {key} lens"
            sc.add(lens, pv.Cylinder(center=(x, y, z + 630), direction=(0, 0, 1), radius=150, height=260,
                                     resolution=32), C_IDLE, "beacons", ambient=0.9, diffuse=0.25, specular=0.0)
            self.beacons[key] = lens
        for key in FLOOR_BEACONS:
            names = self.F.groups.get(key)
            if not names:
                continue
            b = np.array(SL._bounds_of(sc, names), float)
            if not np.isfinite(b).all():
                continue
            beacon(key, b[0] + 0.78 * (b[1] - b[0]), (b[2] + b[3]) / 2, b[5])
        for i, x in enumerate((0.0, SL.X2)):
            beacon(f"vlm{i + 1}", x + 900, -200, V.UNIT_H)
        lights = sc.pl.renderer.GetLights()
        lights.InitTraversal()
        self.lights = []
        for _ in range(lights.GetNumberOfItems()):
            lt = lights.GetNextItem()
            self.lights.append((lt, lt.GetIntensity()))
        self.docks = {}
        for key in list(W.STATIONS):
            try:
                self.docks[key] = W.dock_pose(key)
            except Exception:                         # noqa: BLE001  (not a docking station)
                pass
        self.chargers = [W.charger_pose(i) for i in range(len(W.CHARGERS))]
        self.q_park = np.radians(A.PARK_DEG)
        self.q_ready = np.radians((-90.0, -100.0, 110.0, -100.0, -90.0, 0.0))
        self.home = {k: [*V.SLOTS[A.HOME[k]]] for k in L.tray}
        self.work_q: dict = {}
        # round 10: the person on shift and a vendor, drawn where their task is (upkeep_clip's figure)
        import upkeep_clip as UC
        self.up = UpkeepView(sim)
        self.person = UC.Person(sc, "staff")
        self.vendor = UC.Person(sc, "vendor")
        for n in self.vendor.names():
            if any(w in n for w in ("coat", "sleeve", "forearm")):
                sc.color[n] = VENDOR_COAT
        self.person.show(0.0)
        self.vendor.show(0.0)
        self.spots = {}                     # floor machine -> (x, y, heading, hands' target): at its front, its dock
        for key, (cx, row, _, dx) in W.STATIONS.items():
            names = self.F.groups.get(key)
            if key in ("vlm", "vlm2") or not names:
                continue
            b = np.array(SL._bounds_of(sc, names), float)
            if not np.isfinite(b).all():
                continue
            x = float(np.clip(dx, b[0] + 250.0, b[1] - 250.0))
            if row == "N":
                self.spots[key] = (x, b[2] - 330.0, 0.0, (x, b[2] + 30.0, 1050.0))
            else:
                self.spots[key] = (x, b[3] + 330.0, 180.0, (x, b[3] - 30.0, 1050.0))
        self.urows, self.at_person = [], None

    def work(self, i: int, key: str, f: int):
        """Joint angles for unit i working at dock `key`: the gripper down over the presented tray's front (a VLM) or
        500 mm in front of the machine; three targets, one per few frames. Cached; the parked pose if IK fails."""
        from scene import T, R
        uu = self.units[i]
        k3 = (f // 3) % 3
        ck = (i, key, k3)
        if ck in self.work_q:
            return self.work_q[ck]
        x, y, hd = uu.pose
        M = T((x, y, 0)) @ R((0, 0, 1), hd)
        dx = (-260.0, 0.0, 260.0)[k3]
        if key in ("vlm", "vlm2"):
            yo, zo = self.V.SLOTS["open"]
            arm = M @ np.array([*self.A.ARM_LOCAL, 0.0, 1.0])
            p = (arm[0] + dx, yo - self.V.TRAY_D / 2 + 230.0, zo + self.V.T_FLOOR + 260.0)
        else:
            q = M @ np.array([self.A.ARM_LOCAL[0] + dx, self.A.ARM_LOCAL[1] + 520.0, 0.0, 1.0])
            p = (q[0], q[1], 980.0)
        try:
            qq = uu.robot.solve(self.A.down(p), seed=self.q_ready)
            ok = qq is not None and np.all(np.isfinite(qq))
        except Exception:                             # noqa: BLE001
            ok = False
        self.work_q[ck] = np.asarray(qq, float) if ok else self.q_park
        return self.work_q[ck]

    # ------------------------------------------------------------------------------------- state at lab time t
    def spot_of(self, r):
        """(x, y, heading, the hands' target) where the person works on record r; None at a desk or a service room."""
        if r is None or r["who"] == "desk":
            return None
        sh, _ = self.up.opening_of(r)
        if sh:                              # at a Shuttle's opening, a little right of centre, turned to the tray
            x0 = self.V.SHUTTLE_X[sh]
            return (x0 + 420.0, LIP - 330.0, 12.0, (x0 + 260.0, -1450.0, self.V.Z_OPEN + 130.0))
        a = r["asset"]
        if a.startswith("unit"):            # beside the unit on its charger
            cx, cy, _ = self.chargers[int(a[4:])]
            return (cx, cy + 400.0 + 330.0, 180.0, (cx, cy + 360.0, 840.0))
        return self.spots.get(a)

    def pose(self, fig, spot, f: int):
        if spot is None:
            fig.show(0.0)
            return
        x, y, hd, (hx, hy, hz) = spot
        k = (f // 3) % 2                    # two working poses, a few frames each
        c_, s_ = math.cos(math.radians(hd)), math.sin(math.radians(hd))
        across = np.array([c_, s_, 0.0])
        hl = np.array([hx, hy, hz + (0.0, 70.0)[k]]) - 150.0 * across
        hr = np.array([hx, hy, hz + (70.0, 0.0)[k]]) + 150.0 * across
        fig.set(x=x, y=y, hd=hd, lean=12.0, amp=0.0, phase=0.0, hands={"l": tuple(hl), "r": tuple(hr)})
        fig.show(1.0)

    def set_state(self, t: float, phase: int, f: int):
        V, A, sc, L, sim = self.V, self.A, self.sc, self.L, self.sim
        now = busy(sim, t) if phase < len(PHASES) - 1 else {}
        live = 0 < phase < len(PHASES) - 1
        person, vendor, held, self.urows = self.up.now(t, people_on(t)) if live else (None, None, {}, [])
        if live and person is None and self.crucible_now(t):
            person = "crucible"
        # trays: the one a unit loads or unloads comes to its Shuttle's opening
        shown = {1: None, 2: None}
        win = 0.15 if phase <= 1 else 1.5
        best = {1: 1e9, 2: 1e9}
        for e in sim["events"]:
            if e["t0"] > t + win:
                break
            if not e.get("tray") or e["t1"] < t - win:
                continue
            for edge in (e["t0"], e["t1"]):
                d = abs(t - edge)
                if d < win and d < best[e["shuttle"]]:
                    best[e["shuttle"]] = d
                    shown[e["shuttle"]] = e["tray"]
        for sh, tray in held.items():               # a person's or a vendor's task holds the opening, its tray there
            shown[sh] = tray if tray in L.tray else None
        if phase == 0 or phase == len(PHASES) - 1:
            shown = {1: None, 2: None}
        for k in L.tray:
            L.tray[k] = list(self.home[k])
            L.where[k] = A.HOME[k]
        for sh in (1, 2):
            L.use(sh)
            k = shown[sh]
            if k is not None and k in L.tray:
                L.tray[k] = [*V.SLOTS["open"]]
                L.where[k] = "open"
                L.lift_z = V.SLOTS["open"][1]
            else:
                L.lift_z = A.LIFT_HOME
        L.use(1)
        L.apply_state()
        self.shown = shown
        # the units: docked at the station of their nearest transfer, else on charge
        at = [None, None]
        if 0 < phase < len(PHASES) - 1:
            linger = 1.5                                  # a unit waits where it last delivered, up to 1.5 h
            last = [None, None]
            for (t0, t1, u, st) in sim["unit_log"]:
                if t0 > t + win:
                    break
                if u < 2 and t0 <= t + win and t1 >= t - linger:
                    last[u] = st
            at = last
        keep_off = {("vlm" if sh == 1 else "vlm2") for sh in held}       # the MiR drives off while a person has it
        for r in (person, vendor):
            if isinstance(r, dict) and r["asset"] in self.docks:
                keep_off.add(r["asset"])
        if person == "crucible":
            keep_off.add("repowder")
        poses = []
        for i in range(2):
            st = at[i]
            key = None
            if st is not None:
                key = st if st in self.docks else ("vlm" if SHUTTLE_OF.get(self._tray_of(st), 1) == 1 else "vlm2")
            if key in keep_off or (live and self.up.unit_out(i, t)):
                key = None                             # kept off a station a person has, or on its charger for upkeep
            pose = self.docks.get(key) if key else None
            if pose is not None and any(abs(pose[0] - q[0]) < 1000 and abs(pose[1] - q[1]) < 1000 for q, _ in poses):
                pose, key = None, None                     # the other unit is there: this one waits on charge
            poses.append((pose if pose is not None else self.chargers[i], key))
        for i, (pose, key) in enumerate(poses):
            uu = self.units[i]
            uu.set(pose)
            uu.robot.set(self.work(i, key, f) if key else self.q_park)
        self.at_keys = [k for _, k in poses]
        # the figures: the person at their task (or the crucible), a vendor at theirs
        if person == "crucible":
            sp = self.spots.get("repowder")
        else:
            sp = self.spot_of(person)
        self.pose(self.person, sp if live else None, f)
        self.pose(self.vendor, self.spot_of(vendor) if live else None, f)
        self.at_person = person
        # beacons
        util = utilization(sim, max(0.0, t - 24), max(t, 24)) if phase >= 3 else {}
        docked = {k for k in self.at_keys if k}
        for key, lens in self.beacons.items():
            c = C_IDLE
            if key.startswith("vlm"):
                c = C_UNIT if shown[int(key[-1])] else C_IDLE
            elif phase >= 3:                                   # weeks and months: busy over the last day
                c = C_RUN if util.get(key, 0.0) > 0.15 else C_IDLE
            elif key in now:                                 # a person, then a failed run, then a unit, then running
                e = now[key]
                c = C_UNIT if key in docked else C_RUN
                if e.get("failed") and e["step"] == "atomize":
                    c = C_FAIL
                if key == "repowder" and e["t0"] <= t < e["t0"] + PARAMS["atomize_h"]["value"]["person"]:
                    c = C_PERSON
            elif key in docked:
                c = C_UNIT
            k2 = {"vlm1": "open1", "vlm2": "open2"}.get(key, key)        # upkeep over the schedule's state
            if 0 < phase < 3:
                us = self.up.state(k2, t)
                c = C_FAIL if us == "wait" else (C_PERSON if us == "upkeep" else c)
                if key == "repowder" and person == "crucible":
                    c = C_PERSON
            elif phase < len(PHASES) - 1:                  # weeks and months: over the last day, as busy above
                if self.up.wait.get(k2, self.up.none).hours(t - 24.0, t) > 2.0:
                    c = C_FAIL
                elif self.up.upk.get(k2, self.up.none).hours(t - 24.0, t) > 2.0:
                    c = C_PERSON
            sc.color[lens] = c
        # lights: out when nobody is on site, at the hour and day scales (at the week scale they would strobe)
        dark = phase in (1, 2) and not people_on(t)
        k = 0.62 if dark else 1.0
        for lt, i0 in self.lights:
            lt.SetIntensity(i0 * k)
        sc.pl.set_background((0.80, 0.82, 0.87) if dark else (1.0, 1.0, 1.0))
        self.now = now
        self.dark = dark

    def crucible_now(self, t: float) -> bool:
        return self.up.crucible.at(t)

    def _tray_of(self, station):
        for s_, st, h, needs, tray, *_ in STEPS:
            if st == station:
                return tray
        return None


# ================================================================================================ the overlay
def draw_panels(img, mv: Movie, t: float, phase: int, s: float):
    """The ribbon under the title (the clock, then the counters), what is running now with the beacons' key (hours
    and days, bottom left), the chart (weeks and months, bottom right), the totals card at the end."""
    from PIL import ImageDraw
    from scene import font
    W, H = img.size
    d = ImageDraw.Draw(img, "RGBA")
    c = counters(mv.sim, t, mv.ncam)
    ink, grey, blue = (15, 15, 20), (95, 99, 106), (30, 60, 140)
    if phase == len(PHASES) - 1:
        totals_card(d, W, H, c, mv, s)
        return img
    # ---- the ribbon
    y0, y1 = 42 * s, 134 * s
    d.rounded_rectangle((8 * s, y0, W - 8 * s, y1), 8 * s, fill=(255, 255, 255, 232), outline=(190, 196, 204, 255))
    day, hm = clock_text(t)
    d.text((20 * s, y0 + 5 * s), day, font=font(14 * s, bold=True), fill=ink)
    d.text((20 * s, y0 + 23 * s), hm, font=font(26 * s, bold=True), fill=blue)
    d.text((20 * s, y0 + 58 * s), speed_text(phase) or "the clock starts", font=font(11.5 * s), fill=grey)
    if phase in (1, 2):
        on = people_on(t)
        tag = "people on site" if on else "nobody on site: lights out"
        tw = d.textlength(tag, font=font(11.5 * s))
        d.rounded_rectangle((18 * s, y0 + 73 * s, 30 * s + tw, y0 + 89 * s), 5 * s,
                            fill=(255, 232, 190, 255) if on else (205, 214, 236, 255))
        d.text((24 * s, y0 + 74 * s), tag, font=font(11.5 * s), fill=ink)
    xd = 292 * s
    d.line([(xd, y0 + 8 * s), (xd, y1 - 8 * s)], fill=(205, 209, 215, 255), width=1)
    d.text((xd + 12 * s, y0 + 4 * s), "made and measured so far (model)", font=font(11 * s), fill=grey)
    for i, (name, v) in enumerate((("alloys atomized", c["atomized"]), ("alloys printed", c["printed"]),
                                   ("alloys fully tested", c["tested"]))):
        x = xd + 12 * s + i * 128 * s
        d.text((x, y0 + 20 * s), f"{v:,}", font=font(30 * s, bold=True), fill=blue)
        d.text((x, y0 + 60 * s), name, font=font(12 * s), fill=ink)
    d.text((xd + 12 * s, y0 + 76 * s), f"of them promoted to a full plate: {c['promoted']:,}", font=font(11 * s),
           fill=grey)
    xg = xd + 400 * s
    d.line([(xg, y0 + 8 * s), (xg, y1 - 8 * s)], fill=(205, 209, 215, 255), width=1)
    cells = [("atomizer runs", f"{c['runs']:,}"), ("powder made", f"{c['powder_kg']:,.1f} kg"),
             ("tensile tests", f"{c['tensile']:,}"),
             ("SEM/EDS images", f"{c['sem_images']:,}"), ("XRD, XRF, PSD", f"{c['xrd']:,} each"),
             ("hardness, nano, PIP", f"{c['indents']:,}"),
             ("corrosion spots", f"{c['corrosion']:,}"), ("instrument data", gb(c["data_gb"])),
             ("stream video kept", gb(c["video_tb"] * 1000))]
    cw = (W - 8 * s - 10 * s - xg) / 3
    for i, (name, val) in enumerate(cells):
        col, row = i % 3, i // 3
        x = xg + 12 * s + col * cw
        y = y0 + 12 * s + row * 27 * s
        d.text((x, y + 1 * s), name, font=font(11.5 * s), fill=grey)
        f = font(13 * s, bold=True)
        vw = d.textlength(val, font=f)
        d.text((x + cw - 20 * s - vw, y), val, font=f, fill=ink)
        if row < 2:
            d.line([(x, y + 21 * s), (x + cw - 20 * s, y + 21 * s)], fill=(232, 234, 238, 255), width=1)
    # ---- upkeep (round 10): a card at the right edge, over the racking and above the chart, so the north row's
    # beacons and the Shuttles' tops under the ribbon stay in view
    cap_top = H - caption_h(d, mv.sc.caption, W, s) - 8 * s
    u = mv.up.counters(t)
    pct = lambda v: "-" if v is None else f"{100 * v:.1f} %"                          # noqa: E731
    week_h = u["week_crucible"] + u["week_upkeep"]
    ucells = [("the person's hours this week", f"{week_h:.0f} of 40 h",
               f"crucible {u['week_crucible']:.0f}, upkeep {u['week_upkeep']:.0f}"),
              ("upkeep so far", f"{u['people']:,.0f} h", "the person's"),
              ("", f"{u['arms']:,.0f} h", "the arms' checks"),
              ("tasks done", f"{u['tasks'] + u['checks']:,}", f"{u['checks']:,} by the arms"),
              ("repairs", f"{u['repairs']}", ""),
              ("available so far", pct(u["avail_route"]), "the stations, on average"),
              ("", pct(u["avail_atom"]), "the atomizer"),
              ("", pct(u["avail_units"]), "the two units")]
    cw = 236 * s
    x0c, y0c = W - 8 * s - cw, y1 + 8 * s
    y1c = (cap_top - 196 * s - 12 * s) if phase >= 3 else (y0c + 280 * s)
    n_lab = sum(1 for c_ in ucells if c_[0])
    step_v = min(20 * s, (y1c - y0c - 32 * s - n_lab * 16 * s) / len(ucells))
    hc = 26 * s + n_lab * 16 * s + len(ucells) * step_v + 6 * s
    d.rounded_rectangle((x0c, y0c, x0c + cw, y0c + hc), 8 * s, fill=(255, 255, 255, 232),
                        outline=(190, 196, 204, 255))
    d.text((x0c + 12 * s, y0c + 6 * s), "Upkeep (model)", font=font(12.5 * s, bold=True), fill=grey)
    yy = y0c + 26 * s
    for name, val, sub in ucells:
        if name:
            yy += 3 * s
            d.text((x0c + 12 * s, yy), name, font=font(10.5 * s), fill=grey)
            yy += 13 * s
        fv = font(14 * s, bold=True)
        d.text((x0c + 12 * s, yy), val, font=fv, fill=ink)
        d.text((x0c + 18 * s + d.textlength(val, font=fv), yy + 3 * s), sub, font=font(10.5 * s), fill=grey)
        yy += step_v
    # ---- running now, and the beacons' key (hours and days)
    if phase in (1, 2):
        rows, urows = [], []
        for kind, r in mv.urows[:3]:                     # upkeep first: the person, a vendor, a fault waiting
            where = up_name(r["own"])
            sh, tray = mv.up.opening_of(r)
            if sh:
                where = f"Shuttle {sh}'s opening" + (f", tray {tray}" if tray and not r["what"].startswith("tray")
                                                     else "")
            elif r["own"].startswith("unit"):
                where = f"unit {int(r['own'][4:]) + 1} on its charger"
            if kind == "wait":
                urows.append(("stopped: " + up_name(r["own"]) + f": {r['mode']}; waits for "
                              + ("a vendor" if r["who"] == "vendor" else "the next shift"), C_FAIL))
            elif kind == "person":
                urows.append((f"the person, {where}: {r['what']}" if r["who"] != "desk" else
                              f"the person, at a desk: {r['what']}", C_PERSON))
            elif kind == "vendor":
                urows.append((f"a vendor, {where}: {r['what']}", C_PERSON))
            elif r["who"] != "auto" or r["t1"] - r["t0"] >= 0.25:
                urows.append((f"out for upkeep, {where}: {r['what']}", C_PERSON))
        if mv.at_person == "crucible":
            urows.insert(0, ("the person, at the atomizer: its crucible changed and the run started", C_PERSON))
        for st, e in sorted(mv.now.items(), key=lambda kv: kv[1]["t0"]):
            if e.get("maint"):
                what = mv.up.what_of(e["maint"])
                urows.append((f"the arm's check, {STATION_NAMES.get(st, st)}: {what}", C_UNIT))
                continue
            word = STEP_WORDS.get(e["step"], e["step"])
            if e["step"] == "atomize" and e.get("failed"):
                word = "atomizing; the melt dripped"
            elif e["step"] == "print" and e.get("failed"):
                word = "printing; this build cracks"
            where = STATION_NAMES.get(st, st)
            rows.append(f"alloy {e['alloy'] + 1}: {word}, {where}")
        urows = urows[:3]
        rows = [(r, None) for r in rows[:7 - len(urows)]]
        rows = urows + rows or [("waiting for the next atomizer run", None)]
        bw = 470 * s
        bh = (30 + 17 * len(rows) + 24) * s
        x, y = 8 * s, cap_top - bh - 6 * s
        d.rounded_rectangle((x, y, x + bw, y + bh), 8 * s, fill=(255, 255, 255, 222), outline=(190, 196, 204, 255))
        d.text((x + 12 * s, y + 6 * s), "Running now", font=font(12.5 * s, bold=True), fill=grey)
        for i, (r, col) in enumerate(rows):
            xr = x + 12 * s
            if col is not None:                          # an upkeep row: a dot in the beacons' colour
                d.ellipse((xr, y + (29 + 17 * i) * s, xr + 8 * s, y + (37 + 17 * i) * s),
                          fill=tuple(int(255 * v) for v in col) + (255,))
                xr += 13 * s
            while d.textlength(r, font=font(12 * s)) > bw - 12 * s - (xr - x) and len(r) > 10:
                r = r[:-2].rstrip(" ,;:") + "…"
            d.text((xr, y + (25 + 17 * i) * s), r, font=font(12 * s), fill=ink)
        ly = y + bh - 22 * s
        lx = x + 12 * s
        for name, col in (("running", C_RUN), ("a unit at it", C_UNIT), ("a person at it, upkeep", C_PERSON),
                          ("idle", C_IDLE), ("stopped: a fault", C_FAIL)):
            d.ellipse((lx, ly + 3 * s, lx + 11 * s, ly + 14 * s), fill=tuple(int(255 * v) for v in col) + (255,))
            d.text((lx + 15 * s, ly + 1 * s), name, font=font(11 * s), fill=ink)
            lx += 26 * s + d.textlength(name, font=font(11 * s))
    # ---- the chart (weeks and months)
    if phase >= 3:
        w, h = 450 * s, 196 * s
        chart(d, mv, t, W - w - 8 * s, cap_top - h - 6 * s, w, h, s, phase)
    return img


def caption_h(d, caption: str, W, s) -> float:
    """The height of Scene.overlay's caption box for this caption (its own wrapping)."""
    from scene import font
    if not caption:
        return 0.0
    fc = font(18 * s)
    maxw = W - 60 * s
    n = 0
    for para in [q.strip() for q in caption.split("|")]:
        cur = ""
        for w_ in para.split():
            tt = (cur + " " + w_).strip()
            if d.textlength(tt, font=fc) > maxw and cur:
                n += 1
                cur = w_
            else:
                cur = tt
        n += 1
    return n * 24 * s + 20 * s


def gb(x: float) -> str:
    if x >= 1000:
        return f"{x / 1000:,.1f} TB"
    return f"{x:,.0f} GB" if x >= 10 else f"{x:,.1f} GB"


_CURVE = {}


def curve(mv: Movie, upto_h: float, n=160):
    """(lab hours, [atomized, printed, fully tested, fully tested with no upkeep]) at n points to upto_h."""
    key = (round(upto_h, 1), n)
    if key not in _CURVE:
        ts = np.linspace(0, upto_h, n)
        rows = [counters(mv.sim, tt, mv.ncam) for tt in ts]
        base = [sum(1 for r in mv.base["alloys"] if r.get("tested", 1e18) <= tt) for tt in ts]
        _CURVE[key] = (ts, np.array([[r["atomized"], r["printed"], r["tested"], b] for r, b in zip(rows, base)],
                                    float))
    return _CURVE[key]


def chart(d, mv: Movie, t: float, x0, y0, w, h, s, phase):
    from scene import font
    span = 13 * 7 * 24.0 if phase == 3 else YEAR_H
    ts, ys = curve(mv, span)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8 * s, fill=(255, 255, 255, 232), outline=(190, 196, 204, 255))
    d.text((x0 + 12 * s, y0 + 6 * s), "Alloys, cumulative, by " + ("week" if phase == 3 else "month"),
           font=font(13 * s, bold=True), fill=(90, 94, 100))
    gx0, gx1, gy0, gy1 = x0 + 40 * s, x0 + w - 14 * s, y0 + 30 * s, y0 + h - 26 * s
    ymax = max(10.0, float(ys[-1].max()) * 1.12)
    d.line([(gx0, gy1), (gx1, gy1)], fill=(150, 154, 160, 255), width=1)
    d.line([(gx0, gy0), (gx0, gy1)], fill=(150, 154, 160, 255), width=1)
    step = 10 ** math.floor(math.log10(ymax / 2))
    for m in (1, 2, 5):
        if ymax / (step * m) <= 5:
            step *= m
            break
    v = 0.0
    while v <= ymax:
        yy = gy1 - (gy1 - gy0) * v / ymax
        d.line([(gx0, yy), (gx1, yy)], fill=(225, 228, 232, 255), width=1)
        d.text((x0 + 8 * s, yy - 7 * s), f"{v:,.0f}", font=font(10.5 * s), fill=(110, 114, 120))
        v += step
    nt = 13 if phase == 3 else 12
    for i in range(0, nt + 1, 1 if phase == 3 else 3):
        hx = span * i / nt
        xx = gx0 + (gx1 - gx0) * hx / span
        d.text((xx - 4 * s, gy1 + 4 * s), str(i), font=font(10.5 * s), fill=(110, 114, 120))
    cols = [(120, 120, 128), (40, 110, 200), (20, 150, 70), (150, 205, 165)]
    k = int(np.searchsorted(ts, min(t, span), side="right"))
    for j in (3, 0, 1, 2):                         # the no-upkeep line first, faint and thin, under the others
        col = cols[j]
        pts = [(gx0 + (gx1 - gx0) * ts[i] / span, gy1 - (gy1 - gy0) * ys[i, j] / ymax) for i in range(max(k, 1))]
        if len(pts) > 1:
            d.line(pts, fill=col + (255,), width=max(1, int((1.4 if j == 3 else 2.4) * s)))
    lx = gx0 + 8 * s
    for name, col in zip(("atomized", "printed", "fully tested", "tested, no upkeep"), cols):
        d.line([(lx, gy0 + 6 * s), (lx + 14 * s, gy0 + 6 * s)], fill=col + (255,), width=max(2, int(2.4 * s)))
        d.text((lx + 18 * s, gy0 - 1 * s), name, font=font(11 * s), fill=(40, 40, 46))
        lx += (28 + d.textlength(name, font=font(11 * s)) / s) * s


def totals_card(d, W, H, c, mv: Movie, s):
    from scene import font
    m = mv.model
    uk = m["upkeep"]
    ph, av, al = uk["people_hours_per_week"], uk["availability"], uk["alloys_a_year"]
    x0, y0, x1, y1 = 120 * s, 70 * s, W - 120 * s, H - 40 * s
    d.rounded_rectangle((x0, y0, x1, y1), 12 * s, fill=(255, 255, 255, 240), outline=(30, 60, 140, 255),
                        width=max(1, int(2 * s)))
    d.text((x0 + 30 * s, y0 + 20 * s), "The first year, by the model", font=font(26 * s, bold=True), fill=(15, 15, 20))
    big = [("unique alloys atomized", c["atomized"]), ("printed", c["printed"]), ("fully tested", c["tested"])]
    x = x0 + 30 * s
    for name, v in big:
        d.text((x, y0 + 64 * s), f"{v:,}", font=font(46 * s, bold=True), fill=(30, 60, 140))
        d.text((x, y0 + 120 * s), name, font=font(15 * s), fill=(60, 64, 70))
        x += 300 * s
    rows = [f"{c['runs']:,} atomizer runs (repeats for promoted alloys and failed runs included), "
            f"{c['powder_kg']:,.0f} kg of usable powder",
            f"{c['promoted']:,} alloys promoted to a full plate of E8 bars; {c['tensile']:,} tensile tests, room "
            f"temperature and hot; {c['sem_images']:,} SEM images and EDS maps",
            f"{c['xrd']:,} XRD patterns, {c['xrf']:,} XRF analyses, {c['psd']:,} size distributions; "
            f"{c['indents']:,} hardness, nanoindentation and PIP sets; {c['corrosion']:,} corrosion spots",
            f"{gb(c['data_gb'])} of instrument data; {gb(c['video_tb'] * 1000)} of stream video from {mv.ncam} "
            f"cameras, if every stream is kept",
            f"Fully tested: {m['fully_tested']}.",
            f"The bottleneck is the {STATION_NAMES.get(m['bottleneck'], m['bottleneck'])}: it runs only while a "
            "person is on site to change its crucible. A model, not a measurement: every step time and assumption is "
            "in notes/timelapse.md.",
            f"Upkeep, booked like any job: {uk['tasks']['arm_checks']:,} reference checks by the arms, "
            f"{uk['tasks']['people']:,} tasks by the person, {uk['tasks']['vendor_visits']} vendor visits, "
            f"{uk['tasks']['repairs']} repairs. The person's week averaged {ph['mean_after_ramp']:.0f} of 40 h "
            f"({ph['crucible']:.0f} at the crucible). Available: the stations {100 * uk['availability_route_mean']:.1f} "
            f"% on average, the atomizer {100 * av['repowder']:.1f} %, the units {100 * av['unit0']:.1f} %. With no "
            f"upkeep at all the same schedule gives {al['tested_without']} alloys fully tested, not {al['tested_with_upkeep']}."]
    from scene import font as F_
    fr = F_(15 * s)
    y = y0 + 160 * s
    for r in rows:
        words, cur = r.split(), ""
        for w_ in words:
            tt = (cur + " " + w_).strip()
            if d.textlength(tt, font=fr) > (x1 - x0 - 60 * s) and cur:
                d.text((x0 + 30 * s, y), cur, font=fr, fill=(30, 30, 36))
                y += 21 * s
                cur = w_
            else:
                cur = tt
        d.text((x0 + 30 * s, y), cur, font=fr, fill=(30, 30, 36))
        y += 29 * s
    if y1 - y > 120 * s:
        chart(d, mv, YEAR_H, x0 + 30 * s, y, x1 - x0 - 60 * s, y1 - y - 16 * s, s, 4)


# ================================================================================================ the frames
def movie():
    from PIL import Image
    sim, base = sims()
    m = model(write=True)
    mv = Movie(sim, m["stream_cameras"])
    mv.model, mv.base = m, base
    sc = mv.sc
    pf = phase_frames()
    n = pf[-1][1]
    picks = None
    if PREVIEW:
        # day 1 (hour 0 is 06:00): 09:30 the MIDI's chamber cleaned, 11:30 tray N held at Shuttle 2's opening,
        # 10:50 a unit on its charger, 14:50 a repair on the MIDI; then a day, a week, a month and the totals
        want = [(1, 0.146), (1, 0.229), (1, 0.205), (1, 0.37), (1, 0.75), (2, 0.6), (3, 0.6), (4, 0.95), (5, 0.5)]
        picks = {pf[i][0] + int((pf[i][1] - pf[i][0] - 1) * u) for i, u in want}
    orig = sc.overlay
    still_at = pf[4][0] + int((pf[4][1] - pf[4][0]) * 0.85)
    shots = []
    import time
    t_start = time.time()
    for f in range(n):
        if picks is not None and f not in picks:
            sc.n += 1
            continue
        t, ph, u = lab_time(f)
        mv.set_state(t, ph, f)
        sc.cam = cam_at(f, n)
        sc.label = PHASES[ph][3]
        sc.caption = caption(ph, m)
        sc.labels = []
        t_f = time.time()
        base = sc.render_base()
        if mv.dark:                                   # lights out: the floor is unlit (ambient), so dim the frame
            base = (base.astype(np.float32) * np.array([0.62, 0.66, 0.80], np.float32)).astype(np.uint8)
        img = orig(Image.fromarray(base), 1.0, [])
        img = draw_panels(img, mv, t, ph, 1.0)
        if sc.mp4 is not None:
            sc.mp4.stdin.write(np.asarray(img.convert("RGB")).tobytes())
        if f == still_at:
            sc.still = (f, np.asarray(img.convert("RGB")).copy())
        if picks is not None:
            shots.append(img.convert("RGB"))
            img.convert("RGB").save(f"/tmp/timelapse_preview_{f:04d}.png")
            print(f"preview frame {f} (lab {t:.1f} h, phase {ph}): {time.time() - t_f:.1f} s", flush=True)
        sc.n += 1
        if f % 30 == 0:
            el = time.time() - t_start
            print(f"frame {f}/{n}  lab {t:8.1f} h  phase {ph}  {el / max(1, f + 1):.2f} s/frame", flush=True)
    for i, ((a, b), (sec, h0, h1, lbl, cap)) in enumerate(zip(pf, PHASES)):
        sc.substeps.append(dict(label=lbl, caption=caption(i, m), start_frame=a, end_frame=b - 1,
                                lab_hours=[h0, h1]))
    if PREVIEW:
        sc.pl.close()
        tw, th = 640, 360
        cols = 3
        rows = (len(shots) + cols - 1) // cols
        sheet = Image.new("RGB", (tw * cols, th * rows), "white")
        for i, im in enumerate(shots):
            sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
        sheet.save(f"/tmp/preview_{NAME}.png")
        print("preview", NAME, len(shots), flush=True)
        return None
    info = sc.save()
    print(info, flush=True)
    return info


def gif():
    import line
    mp4, out = OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"
    for fps, width, lossy in ((5, 640, 90), (4, 560, 100), (4, 480, 120), (3, 480, 140), (3, 400, 160),
                              (2, 400, 160)):
        msg = line.mp4_to_gif(mp4, out, fps=fps, width=width, lossy=lossy)
        print(msg, flush=True)
        if out.stat().st_size < 4.9e6:
            break
    return out


if __name__ == "__main__":
    sys.modules.setdefault("timelapse", sys.modules[__name__])      # upkeep.py imports timelapse: the same module
    args = sys.argv[1:]
    if args and args[0] == "model":
        m = model()
        print(json.dumps(dict(totals=m["totals"], first_alloy_fully_tested_h=m["first_alloy_fully_tested_h"],
                              latency=m["latency_atomized_to_tested_h"], bottleneck=m["bottleneck"],
                              utilization=dict(list(m["utilization_after_ramp"].items())[:8]),
                              atomizer_slots=m["atomizer_slots"],
                              cameras=m["stream_cameras"],
                              upkeep={k: v for k, v in m["upkeep"].items() if k not in ("what", "availability")}),
                         indent=1))
    elif args and args[0] == "gif":
        gif()
    else:
        movie()
        if not PREVIEW:
            gif()

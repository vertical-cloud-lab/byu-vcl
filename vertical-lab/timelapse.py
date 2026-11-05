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


def simulate(hours=YEAR_H) -> dict:
    """The greedy schedule: events [{t0, t1, station, alloy, step, tray, shuttle, unit}] through `hours`. Each step
    starts once its inputs are done, its station has a free spell as long as the step, and a unit has the transfer
    time free just before it; an atomizer run also waits for a run slot on a staffed shift (next_run_slot)."""
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

    def book(station, ready, dur, step, alloy, tray=None, atom=False):
        line = lines.setdefault(station, Line())
        t, bu = max(ready, 0.0), 0
        for _ in range(400):
            if atom:
                t = next_run_slot(t)
            t1 = line.earliest(t, dur)
            if t1 > t + 1e-9:
                t = t1
                continue
            best = None
            for u, ul in enumerate(ulines):
                tu = ul.earliest(t - tr, tr) + tr
                if best is None or tu < best[1]:
                    best = (u, tu)
            bu = best[0]
            if best[1] > t + 1e-9:
                t = best[1]
                continue
            break
        line.add(t, t + dur)
        ulines[bu].add(t - tr, t)
        unit_log.append((t - tr, t, bu, station))
        ev.append(dict(t0=t, t1=t + dur, station=station, alloy=alloy, step=step, tray=tray,
                       shuttle=shuttles.get(tray) if tray else None, unit=bu))
        return t + dur

    def run(alloy, ready, repeat=False):
        """Charge and atomize, again if the run drips. -> the good run's end."""
        while True:
            e_c = book("carousel", ready, STEPS[0][2], "charge", alloy, "B")
            count["runs"] += 1
            e_a = book("repowder", e_c, STEPS[1][2], "atomize", alloy, atom=True)
            ev[-1]["run"] = count["runs"]
            if repeat:
                ev[-1]["repeat"] = True
            if count["runs"] % fail_run == fail_run - 3:        # this run dripped
                ev[-1]["failed"] = True
                ready = e_a
                continue
            return e_a, ev[-1]["t0"]

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
        ev[-1]["failed"] = not printable
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
    return dict(events=ev, alloys=alloys, unit_log=unit_log, runs=count["runs"])


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
        if e["t1"] > t:
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


def model(write=True) -> dict:
    sim = simulate()
    ncam = cameras()
    marks = {"1 day": 24, "1 week": 168, "4 weeks": 672, "13 weeks": 2184, "26 weeks": 4368, "1 year": YEAR_H}
    at = {k: {kk: (round(v, 2) if isinstance(v, float) else v) for kk, v in counters(sim, h, ncam).items()}
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
    used = sum(1 for e in sim["events"] if e["step"] == "atomize" and e["t1"] <= YEAR_H)
    out = dict(
        what="The lab at speed (timelapse.py): a greedy schedule of every alloy through the route of chapters 1-7, "
             "each step on its station, carried by two MiR250 + UR10e units; the atomizer's crucible changed by a "
             "person on weekday shifts, everything else round the clock. A model, not a measurement.",
        fully_tested="atomized powder measured (laser diffraction, XRD, XRF, SEM); printed in the 55 mm kit; heat "
                     "treated; tensile tested at room temperature and at temperature; sectioned, faced, mounted and "
                     "polished; SEM/EDS, VHX, micro-Vickers, nanoindentation and PIP; a corrosion screen on the CubXL",
        params=PARAMS,
        steps=[dict(step=s, station=st, hours=h, needs=n, tray=tr, makes=mk, source=src)
               for s, st, h, n, tr, mk, src in STEPS],
        promoted_steps=[dict(step=s, station=st, hours=h, makes=mk, source=src) for s, st, h, mk, src in FULL],
        data_gb_per_step=DATA_GB, stream_cameras=ncam,
        totals=at,
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
     "Hour by hour, the first day. A person comes in 08:00-16:00 to change the atomizer's crucible; the arms, the "
     "MiR250s and the Shuttles do the rest, and keep going with the lights off."),
    (16.0, 24.0, 14 * 24.0, "2/4  Day by day",
     "Day by day. The atomizer runs only while someone is on site: one run a day while the lab is commissioned, then "
     "three a weekday. The rest runs round the clock and over the weekends."),
    (14.0, 14 * 24.0, 13 * 7 * 24.0, "3/4  Week by week",
     "Week by week. An alloy is fully tested about half a day after it is atomized. One in ten is promoted to a full "
     "plate of E8 bars, which takes eight more atomizer runs."),
    (16.0, 13 * 7 * 24.0, YEAR_H, "4/4  Month by month",
     "Month by month, to the end of the first year. The counters are a model built from each chapter's step times "
     "and the assumptions in notes/timelapse.md, not measurements."),
    (9.0, YEAR_H, YEAR_H, "The first year", ""),
]


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
    def set_state(self, t: float, phase: int, f: int):
        V, A, sc, L, sim = self.V, self.A, self.sc, self.L, self.sim
        now = busy(sim, t) if phase < len(PHASES) - 1 else {}
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
        poses = []
        for i in range(2):
            st = at[i]
            key = None
            if st is not None:
                key = st if st in self.docks else ("vlm" if SHUTTLE_OF.get(self._tray_of(st), 1) == 1 else "vlm2")
            pose = self.docks.get(key) if key else None
            if pose is not None and any(abs(pose[0] - q[0]) < 1000 and abs(pose[1] - q[1]) < 1000 for q, _ in poses):
                pose, key = None, None                     # the other unit is there: this one waits on charge
            poses.append((pose if pose is not None else self.chargers[i], key))
        for i, (pose, key) in enumerate(poses):
            uu = self.units[i]
            uu.set(pose)
            uu.robot.set(self.work(i, key, f) if key else self.q_park)
        self.at_keys = [k for _, k in poses]
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
            sc.color[lens] = c
        # lights: out when nobody is on site, at the hour and day scales (at the week scale they would strobe)
        dark = phase in (1, 2) and not people_on(t)
        k = 0.62 if dark else 1.0
        for lt, i0 in self.lights:
            lt.SetIntensity(i0 * k)
        sc.pl.set_background((0.80, 0.82, 0.87) if dark else (1.0, 1.0, 1.0))
        self.now = now
        self.dark = dark

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
    # ---- running now, and the beacons' key (hours and days)
    cap_top = H - caption_h(d, mv.sc.caption, W, s) - 8 * s
    if phase in (1, 2):
        rows = []
        for st, e in sorted(mv.now.items(), key=lambda kv: kv[1]["t0"]):
            word = STEP_WORDS.get(e["step"], e["step"])
            if e["step"] == "atomize" and e.get("failed"):
                word = "atomizing; the melt dripped"
            elif e["step"] == "print" and e.get("failed"):
                word = "printing; this build cracks"
            where = STATION_NAMES.get(st, st)
            rows.append(f"alloy {e['alloy'] + 1}: {word}, {where}")
        rows = rows[:6] or ["waiting for the next atomizer run"]
        bw = 430 * s
        bh = (30 + 17 * len(rows) + 24) * s
        x, y = 8 * s, cap_top - bh - 6 * s
        d.rounded_rectangle((x, y, x + bw, y + bh), 8 * s, fill=(255, 255, 255, 222), outline=(190, 196, 204, 255))
        d.text((x + 12 * s, y + 6 * s), "Running now", font=font(12.5 * s, bold=True), fill=grey)
        for i, r in enumerate(rows):
            while d.textlength(r, font=font(12 * s)) > bw - 24 * s and len(r) > 10:
                r = r[:-2].rstrip(" ,") + "…"
            d.text((x + 12 * s, y + (25 + 17 * i) * s), r, font=font(12 * s), fill=ink)
        ly = y + bh - 22 * s
        lx = x + 12 * s
        for name, col in (("running", C_RUN), ("a unit at it", C_UNIT), ("a person at it", C_PERSON),
                          ("idle", C_IDLE), ("failed run", C_FAIL)):
            d.ellipse((lx, ly + 3 * s, lx + 11 * s, ly + 14 * s), fill=tuple(int(255 * v) for v in col) + (255,))
            d.text((lx + 15 * s, ly + 1 * s), name, font=font(11 * s), fill=ink)
            lx += 26 * s + d.textlength(name, font=font(11 * s))
    # ---- the chart (weeks and months)
    if phase >= 3:
        w, h = 400 * s, 196 * s
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
    key = (round(upto_h, 1), n)
    if key not in _CURVE:
        ts = np.linspace(0, upto_h, n)
        rows = [counters(mv.sim, tt, mv.ncam) for tt in ts]
        _CURVE[key] = (ts, np.array([[r["atomized"], r["printed"], r["tested"]] for r in rows], float))
    return _CURVE[key]


def chart(d, mv: Movie, t: float, x0, y0, w, h, s, phase):
    from scene import font
    span = 13 * 7 * 24.0 if phase == 3 else YEAR_H
    ts, ys = curve(mv, span)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8 * s, fill=(255, 255, 255, 232), outline=(190, 196, 204, 255))
    d.text((x0 + 12 * s, y0 + 6 * s), "Alloys, cumulative, by " + ("week" if phase == 3 else "month"),
           font=font(13 * s, bold=True), fill=(90, 94, 100))
    gx0, gx1, gy0, gy1 = x0 + 40 * s, x0 + w - 14 * s, y0 + 30 * s, y0 + h - 26 * s
    ymax = max(10.0, float(ys[-1].max()) * 1.08)
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
    cols = [(120, 120, 128), (40, 110, 200), (20, 150, 70)]
    k = int(np.searchsorted(ts, min(t, span), side="right"))
    for j, col in enumerate(cols):
        pts = [(gx0 + (gx1 - gx0) * ts[i] / span, gy1 - (gy1 - gy0) * ys[i, j] / ymax) for i in range(max(k, 1))]
        if len(pts) > 1:
            d.line(pts, fill=col + (255,), width=max(2, int(2.4 * s)))
    lx = gx0 + 8 * s
    for name, col in zip(("atomized", "printed", "fully tested"), cols):
        d.line([(lx, gy0 + 6 * s), (lx + 14 * s, gy0 + 6 * s)], fill=col + (255,), width=max(2, int(2.4 * s)))
        d.text((lx + 18 * s, gy0 - 1 * s), name, font=font(11 * s), fill=(40, 40, 46))
        lx += (34 + d.textlength(name, font=font(11 * s)) / s) * s


def totals_card(d, W, H, c, mv: Movie, s):
    from scene import font
    m = mv.model
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
            "in notes/timelapse.md."]
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
    sim = simulate()
    m = model(write=True)
    mv = Movie(sim, m["stream_cameras"])
    mv.model = m
    sc = mv.sc
    pf = phase_frames()
    n = pf[-1][1]
    picks = None
    if PREVIEW:
        want = [(0, 0.5), (1, 0.12), (1, 0.3), (1, 0.55), (1, 0.75), (2, 0.6), (3, 0.6), (4, 0.95), (5, 0.5)]
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
        sc.caption = " ".join(PHASES[ph][4].split())
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
    for (a, b), (sec, h0, h1, lbl, cap) in zip(pf, PHASES):
        sc.substeps.append(dict(label=lbl, caption=" ".join(cap.split()), start_frame=a, end_frame=b - 1,
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
    args = sys.argv[1:]
    if args and args[0] == "model":
        m = model()
        print(json.dumps(dict(totals=m["totals"], first_alloy_fully_tested_h=m["first_alloy_fully_tested_h"],
                              latency=m["latency_atomized_to_tested_h"], bottleneck=m["bottleneck"],
                              utilization=dict(list(m["utilization_after_ramp"].items())[:8]),
                              atomizer_slots=m["atomizer_slots"],
                              cameras=m["stream_cameras"]), indent=1))
    elif args and args[0] == "gif":
        gif()
    else:
        movie()
        if not PREVIEW:
            gif()

"""Is the vertical lab worth it? A queue model of sample transport, replayed on the twin's event logs (issue #407).

    python -m twin.worth_it run            # 2 timings x 4 layouts x 3 external loads x 24 logs -> out/worth_it/
    python -m twin.worth_it sens           # sensitivities on 4 logs at 30 % and 60 % outside load
    python -m twin.worth_it run5 <dir>     # the same on round 5's 16 automated-lab logs (PR 405), from <dir>
    python -m twin.worth_it tables         # out/worth_it/tables.md from the saved results
    python -m twin.worth_it one <log> <layout> <n_mm> <ext> ['{"attend": "cells"}']

What it adds to the twin. Round 3 books one 6 min robot transfer with every in-house step and has no tray, extractor
or opening (twin/facility.py ROBOT_H), so it cannot say whether a Shuttle opening or a robot would bind. This model
keeps the twin's decisions and instrument hours (one committed event log) and replaces the 6 minutes with a transport
layer that has the resources the issue names:

* **vlm**: PR 318's lab. Instruments on trays in two Kardex Shuttles (tray plan below), one extractor and one opening
  per Shuttle, floor machines at docks. A mobile manipulator works at a presented tray. A tray is fetched, worked at,
  and stored. By default a tray does not move while an instrument on it is running (``lock="running"``: notes/ups.md,
  "the schedule never moves a tray while an unbacked load is working", extended here to every measurement), so
  instruments that share a tray wait for each other.
* **flat**: the same instruments on benches, at the docks of PR 406's "automated, same floor plan" layout. A mobile
  manipulator drives to a bench, docks, localizes and loads. One unit in an aisle at a time (PR 406: a docked MiR250
  leaves 0.94 m of a 5 ft aisle).

Each with one or two mobile manipulators. Every visit to an instrument is two robot tasks: IN (the sample from a rack
into the instrument) and OUT (back to a rack beside the dock). Internal steps are the log's bookings, released at
their original start or when their predecessor's sample is out, whichever is later. The twin books a 6 min transfer
inside each step (``credit_h``), so a step runs for its booking less that, and the replay's own handling takes its
place: with handling as quick as the twin assumed, the replay keeps the twin's pace.

Rules a lab would use, all in both layouts: time-critical stations first (the atomizer's start slots, the furnace's
cycles, and the steps that feed them), then internal loads and every unload, then outside loads; outside work takes
only the gaps the twin's plan leaves before the next internal step at its station, or anywhere on its tray in the VLM
(``protect``); one unit charges at a time while the others have charge in reserve. External jobs arrive at random
(Poisson) at the instruments in twin/cloud.py's catalogue, at a rate that would keep each instrument busy for `ext`
of the clock (0, 0.3, 0.6). Two timings: the twin's (a load and an unload a step) and PR 332's attended time
(``attend="cells"``: the arm stays for its share of each step, at the presented tray in the VLM; the powder line in a
cell of its own).

Everything here is a model. The handling times are stand-ins (Params, each marked); nobody has timed a MiR250 + UR12e
at one of these instruments or a Shuttle carrying one. The replay keeps the twin's decisions fixed: a policy that saw
later results would choose differently. Pure standard library, so it runs without the twin's numerical stack; only
``reference_filter`` imports twin.spaces (numpy).
"""
from __future__ import annotations

import bisect
import heapq
import json
import lzma
import math
import random
import sys
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "out" / "twin3b" / "events"
OUT = ROOT / "out" / "worth_it"


# ----------------------------------------------------------------------------------------------------- parameters
@dataclass
class Params:
    """Handling times. 'vendor' and 'repo' figures have a source; every 'stand-in' is a guess to be measured."""
    v_mm: float = 0.8          # m/s driving. Stand-in, between Liverpool's 0.3 m/s cap (Burger 2020, SI) and an Aethon
    #                            T3's 0.76 m/s hospital maximum, under the 1.0 m/s people walk beside a robot (Neggers
    #                            2022); MiR250's rated top speed is 2.0 m/s (MiR250 spec, 2023)
    a_mm: float = 0.3          # m/s2. Vendor: MiR250 at full payload (MiR250 spec, 2023)
    t_dock: float = 60.0       # s to dock at a marker and localize the arm. Stand-in: MiR250 docks to a VL-marker in up
    #                            to 14 s (spec); the arm's calibration time is not published (ER-VISION "to 1 mm");
    #                            machining_sim.py assumes 150 s to drive in, dock and re-localize
    t_arm: float = 60.0        # s to load or unload one instrument (door, fixture, grip). Stand-in
    t_rack: float = 20.0       # s to pick from or place on an open rack. Stand-in
    t_fetch: float = 26.0      # s, slot to opening: Kardex's 20 s average to fetch (configured Shuttle 500, 6.75 m, at
    #                            100 % speed; units ship at 70 % extractor speed) + 2 x 3 s for the tray's coupling to
    #                            undock and dock (notes/services.md)
    t_store: float = 26.0      # s, opening to slot, the same way; store + fetch = 52 s against Kardex's 38 s + 12 s
    t_tray_loc: float = 10.0   # s, a camera look at a newly presented tray. Stand-in (the extractor's repeatability
    #                            against the arm's needs is unknown: notes/services.md)
    tray_slow: float = 1.0     # multiplier on t_fetch and t_store (a gentle profile for sensitive trays)
    lock: str = "running"      # "running": a tray stays put while an instrument on it runs; "never": it may move
    charge_every_h: float = 4.5    # Vendor: MiR's MC250 (MiR250 + UR arm) runs 4.5 h from 100 % to 10 %; an idle unit
    #                                tops up at its charger (a bare MiR250: 13 h at full payload)
    charge_h: float = 1.0          # 40 min for 20-80 % (MC250), so about an hour for the 90 % a full run uses
    opp_min_h: float = 5.0 / 60.0  # an idle gap tops the battery up only beyond the round trip to the charger and
    #                                this long on it (stand-in)
    aisle_exclusive: bool = True   # flat: one unit in an aisle at a time (PR 406's layout note)
    max_queue: int = 20        # external jobs waiting at a station before a new request is turned away
    slot_grace_h: float = 0.5  # a slotted station (atomizer starts, furnace cycles) starts up to this late. Stand-in
    bonus_tray: float = 600.0  # s of seniority given to a task on the tray already presented
    bonus_dock: float = 300.0  # s of seniority given to a task at the dock the unit is already at
    attend: str = "none"       # "none": the twin's own timing, a load and an unload a step. "cells": the arm also
    #                            attends each step for PR 332's share of it (ATTEND), at the presented tray in the
    #                            VLM, with the powder line in cells of its own; "pr332": PR 332's shares everywhere
    prefetch: bool = True      # the Shuttle starts fetching a tray when a unit is assigned to it, not when it arrives
    credit_h: float = 0.1      # the twin books a 6 min robot transfer inside each step (twin/facility.py ROBOT_H), so
    #                            an internal step's run is its booking less this (at most half the step); the replay's
    #                            own handling takes its place. 0 adds the handling on top of the twin's bookings
    protect: bool = True       # outside work takes only the gaps: an outside job starts only if it would end before
    #                            the next internal step due at its station (or, in the VLM, anywhere on its tray), as
    #                            the twin's plan has it. False: first come, first served (internal first in the queue)
    protect_margin_h: float = 0.25  # handling allowance when fitting an outside job into a gap
    ext_start_h: float = 0.0   # outside jobs start arriving at this hour (round 5: when the lab's own stations open)
    ext_intake: bool = False   # True: every outside sample is carried from the packaging station to its instrument;
    #                            False: outside samples wait in a rack at the instrument's dock (delivered in batches)


# ----------------------------------------------------------------------------------------------------- geometry
# Dock positions in metres from PR 406's layouts (vertical-lab/out/floorspace/layouts.json at e0171d97, 'docks').
FLAT_DOCKS = {
    "glovebox": (-10.78, -5.54), "repowder": (-7.62, -5.70), "sieve_cell": (-4.32, -3.87), "B1": (-10.23, -7.79),
    "K0": (-6.26, -7.63), "eos_m400": (0.46, -4.98), "meltio_cell": (5.42, -6.67), "aconity": (2.20, -6.71),
    "ded": (5.86, -7.17), "wire_edm": (10.39, -5.78), "M2": (10.56, -7.79), "F1": (14.11, -3.55),
    "instron_floor": (-11.10, -12.96), "instron_small": (-9.47, -13.38), "L0": (-7.75, -13.85),
    "E0": (-8.93, -12.92), "D0": (-4.76, -13.85), "D1": (-2.03, -13.85), "F0": (-0.38, -13.07),
    "fumehood": (2.48, -13.06), "A0": (4.17, -13.85), "C0": (7.13, -13.85), "H0": (8.45, -13.07),
    "packaging": (12.34, -13.26),
}
FLAT_CORRIDOR_Y = -10.35            # the corridor's centre line (its rectangle runs y = -11.27 to -9.44)
FLAT_CHARGER = (15.62, -13.24)
_FLAT_N = (-2.40, 8.36, 12.42)      # x where the north rooms change: powder | metal AM | machine shop | furnace
_FLAT_S = (-6.12, -2.61, 1.20, 6.21, 10.60)   # south rooms: mech | SEM | analytical | wet | fabrication | shipping
VERT_DOCKS = {
    "sieve_cell": (-2.56, -1.93), "repowder": (-5.16, -1.93), "glovebox": (-8.36, -1.93), "aconity": (6.88, -1.93),
    "instron_floor": (-8.73, -5.87), "instron_small": (-7.10, -5.87), "fumehood": (-1.98, -5.87),
    "ded": (-0.11, -5.87), "wire_edm": (2.21, -5.87), "packaging": (4.91, -5.87),
    "vlm1": (0.0, -1.93), "vlm2": (3.63, -1.93),
}
VERT_CHARGER = (-4.73, -6.48)


def flat_aisle(dock: str) -> str:
    x, y = FLAT_DOCKS[dock]
    if y > FLAT_CORRIDOR_Y:
        return "N%d" % sum(x > b for b in _FLAT_N)
    return "S%d" % sum(x > b for b in _FLAT_S)


def flat_dist(a: tuple, b: tuple, same_aisle: bool) -> float:
    if same_aisle:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    return abs(a[1] - FLAT_CORRIDOR_Y) + abs(a[0] - b[0]) + abs(b[1] - FLAT_CORRIDOR_Y)


def vert_dist(a: tuple, b: tuple) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def drive_s(d: float, p: Params) -> float:
    """Seconds to drive d metres from rest to rest: a trapezoid, or a triangle when d is short."""
    if d <= 0:
        return 0.0
    if d >= p.v_mm ** 2 / p.a_mm:
        return d / p.v_mm + p.v_mm / p.a_mm
    return 2.0 * math.sqrt(d / p.a_mm)


# ----------------------------------------------------------------------------------------------------- stations
# Where each of the twin's in-house stations is: its dock on the flat plan, and in PR 318's lab either a tray
# (Shuttle, tray letter: notes/tray_plan.md and vlm.py's slot plan) or a floor dock. `lock`: a run holds its tray.
def _T(shuttle, tray):
    return ("tray", shuttle, tray)


def _F(dock):
    return ("floor", dock)


STATIONS = {
    "atomizer": dict(flat="repowder", vert=[_F("repowder")]),
    "shop": dict(flat="M2", vert=[_F("wire_edm")], note="stand-in: the machining cell is not on PR 318's floor plan"),
    "doser": dict(flat="B1", vert=[_T(1, "B")]),
    "sieve": dict(flat="sieve_cell", vert=[_F("sieve_cell")]),
    "psd": dict(flat="D1", vert=[_T(1, "E")]),
    "byu_sem": dict(flat="D0", vert=[_T(1, "D")]),
    "byu_icpms": dict(flat="fumehood", vert=[_F("fumehood")], note="stand-in: the ICP-MS station is not placed"),
    "density": dict(flat="D0", vert=[_T(2, "K")], note="stand-in: the crack check on the VHX-7000, tray K"),
    "edm": dict(flat="wire_edm", vert=[_F("wire_edm")]),
    "furnace": dict(flat="F1", vert=[_T(1, "F")]),
    "tensile": dict(flat="L0", vert=[_T(2, "L"), _F("instron_small")]),
    "tensile_hot": dict(flat="instron_floor", vert=[_F("instron_floor")]),
    "utah_midi": dict(flat="aconity", vert=[_F("aconity")]),
    "utah_mxlab": dict(flat="ded", vert=[_F("ded")]),
    "immersion": dict(flat="A0", vert=[_T(1, "A")], lock=False,
                      note="30-day vials on the CubXL's deck: they must ride the tray, or tray A never moves"),
    "cubxl": dict(flat="A0", vert=[_T(1, "A")]),
    "xrd": dict(flat="D1", vert=[_T(1, "D")]),
    "xrf": dict(flat="D1", vert=[_T(2, "M")]),
    "prep": dict(flat="F0", vert=[_T(1, "F")]),
    "hardness": dict(flat="L0", vert=[_T(2, "L")]),
    "nanoindent": dict(flat="E0", vert=[_T(1, "E")]),
    "pip": dict(flat="E0", vert=[_T(1, "E")]),
}
DEFAULT_UNITS = {"furnace": 8, "tensile": 2, "immersion": 24, "shop": 2}
# External jobs: (hours, coefficient of variation) per station, copied from twin/cloud.py CATALOGUE (a test compares
# them). Left out: the atomizer (the campaigns' own bottleneck, and its crucible needs a person) and the ICP-MS
# (samples go in racks). `EXT_UNITS`: how many units of a station take outside work.
EXT_JOBS = {
    "byu_sem": [(1.0, 0.5), (2.0, 0.5)], "xrd": [(0.75, 0.3)], "psd": [(0.5, 0.3)], "xrf": [(0.5, 0.3)],
    "pip": [(0.5, 0.3)], "tensile": [(0.6, 0.3)], "tensile_hot": [(1.5, 0.3)], "hardness": [(0.5, 0.3)],
    "nanoindent": [(1.0, 0.4)], "cubxl": [(1.2, 0.2)], "utah_midi": [(8.0, 0.5)], "utah_mxlab": [(4.0, 0.3)],
    "furnace": [(4.0, 0.3)], "edm": [(1.0, 0.5)],
}
EXT_UNITS = {"furnace": 2, "tensile": 2}      # two furnaces (the twin counts their eight coupon positions)
# The arm's attended time at a station: PR 332's bottleneck.py ATTEND (a share of the step) and ATTEND_H (hours a
# step), "assumed: the share of each step the arm spends at the station, from the chapters" (not timed), mapped to the
# twin's stations. In the VLM the tray stays at the opening while the arm attends, so attended work holds the
# Shuttle's opening as well as the unit (notes/bottleneck.md, "The hands"). Left at 0: the machining cell ("shop",
# PR 373 has its own arm), the immersion (vials only loaded) and the ICP-MS (autosampler racks).
ATTEND = {
    "atomizer": ("h", 0.3), "sieve": ("share", 0.7), "doser": ("share", 0.8), "psd": ("share", 0.3),
    "byu_sem": ("share", 0.2), "density": ("share", 0.2), "edm": ("share", 0.3), "furnace": ("h", 0.05),
    "tensile": ("share", 0.5), "tensile_hot": ("h", 0.15), "utah_midi": ("h", 0.2), "utah_mxlab": ("share", 0.05),
    "cubxl": ("h", 0.05), "xrd": ("share", 0.5), "xrf": ("share", 0.2), "prep": ("share", 0.3),
    "hardness": ("share", 0.1), "nanoindent": ("share", 0.1), "pip": ("share", 0.2),
}


# PR 332's R5 ("floor cells with fixed arms"): the powder line's attended work (the atomizer, the sieve, the crucible's
# charge) goes to cells with arms of their own, so the mobile units only carry to and from them.
CELL_TENDED = {"atomizer", "sieve", "doser"}
ATTEND_MODES = ("none", "cells", "pr332")


def attend_h(station: str, dur: float, mode: str = "cells") -> float:
    """Hours of a step of `dur` hours that a mobile unit's arm spends attending it (never more than the step).
    mode "none": the twin's timing (a load and an unload); "pr332": PR 332's shares everywhere; "cells": PR 332's
    shares, with the powder line tended by its own cell (CELL_TENDED)."""
    if mode not in ATTEND_MODES:
        raise ValueError(mode)
    if mode == "none" or station not in ATTEND or (mode == "cells" and station in CELL_TENDED):
        return 0.0
    kind, x = ATTEND[station]
    return min(dur, x * dur if kind == "share" else x)
HELPERS = {"robot", "operator", "hpc"}
LAYOUTS = (("vlm", 1), ("flat", 2), ("vlm", 2), ("flat", 1))     # the issue's three, and flat with one for symmetry
LOADS = (0.0, 0.3, 0.6)


# ----------------------------------------------------------------------------------------------------- the log
def load_log(path) -> dict:
    path = Path(path)
    with (lzma.open(path, "rt") if path.suffix == ".xz" else open(path)) as fh:
        return json.load(fh)


def internal_jobs(log: dict) -> list:
    """The log's in-house bookings as jobs, each with one predecessor: the latest-finished earlier booking of the same
    design, or failing that of the same campaign (the result a decision could have waited for)."""
    jobs = []
    for e in log["events"]:
        k = e["station"]
        if k in HELPERS or k not in STATIONS or log["stations"].get(k, {}).get("external"):
            continue
        jobs.append(dict(id=len(jobs), station=k, campaign=e["campaign"], design=e.get("design"), t0=e["t0_h"],
                         t1=e["t1_h"], dur=e["t1_h"] - e["t0_h"], ext=False, pred=None, pred_kind=None, succ=[]))
    by_design, by_camp = defaultdict(list), defaultdict(list)
    for j in sorted(jobs, key=lambda j: j["t1"]):
        by_design[(j["campaign"], j["design"])].append(j)
        by_camp[j["campaign"]].append(j)

    def latest(lst, t, me):
        lo, hi = 0, len(lst)
        while lo < hi:                       # the last entry with t1 <= t
            mid = (lo + hi) // 2
            if lst[mid]["t1"] <= t + 1e-9:
                lo = mid + 1
            else:
                hi = mid
        i = lo - 1
        while i >= 0 and lst[i] is me:
            i -= 1
        return lst[i] if i >= 0 else None

    for j in jobs:
        p = latest(by_design[(j["campaign"], j["design"])], j["t0"], j)
        kind = "chain"
        if p is None:
            p, kind = latest(by_camp[j["campaign"]], j["t0"], j), "decision"
        if p is not None and p["t1"] <= j["t0"] + 1e-9:
            j["pred"], j["pred_kind"] = p["id"], kind
            p["succ"].append(j["id"])
    return jobs


def slots_of(log: dict, jobs: list) -> dict:
    """Stations whose bookings start on the clock (the atomizer's start slots, the furnace's 3 h cycles):
    {(station, campaign): {weekday or None: [times of day]}}, read off the log itself. A station counts as slotted
    when its starts fall on a few half-hours; a station that merely follows a slotted one (the sieve after the
    atomizer) starts at odd minutes and is left alone."""
    tods = defaultdict(set)
    n = defaultdict(int)
    for j in jobs:
        tods[j["station"]].add(round(j["t0"] % 24.0, 2))
        n[j["station"]] += 1
    out = {}
    for st, s in tods.items():
        if n[st] < 20 or len(s) > 8 or any(abs(x * 2 - round(x * 2)) > 1e-6 for x in s):
            continue
        round_clock = log["stations"][st].get("hours") == "24/7"
        for j in jobs:
            if j["station"] != st:
                continue
            d = out.setdefault((st, None if round_clock else j["campaign"]), defaultdict(set))
            d[None if round_clock else int(j["t0"] // 24) % 7].add(round(j["t0"] % 24.0, 2))
    return {k: {dow: sorted(v) for dow, v in d.items()} for k, d in out.items()}


def _slot_table(slots, st, camp):
    return slots.get((st, camp)) or slots.get((st, None))


def next_slot(tab: dict, t: float, grace: float) -> float:
    """The start a slotted station gives a job that is ready at t: now, if a slot opened within `grace`; otherwise
    the next slot."""
    day = int((t - grace) // 24)
    best = None
    for d in range(day, day + 22):
        for tod in tab.get(None, tab.get(d % 7, ())):
            ts = d * 24.0 + tod
            if ts <= t + 1e-9 and t - ts <= grace + 1e-9:
                return t
            if ts > t and (best is None or ts < best):
                best = ts
        if best is not None:
            return best
    return t


# ----------------------------------------------------------------------------------------------------- simulation
class Sim:
    def __init__(self, log: dict, layout: str, n_mm: int, ext: float, p: Params | None = None, seed: int = 0,
                 horizon_h: float | None = None, jobs: list | None = None):
        self.p = p or Params()
        self.layout, self.n_mm, self.ext = layout, n_mm, ext
        self.H = float(horizon_h or 24.0 * log["meta"]["horizon_days"])
        self.rng = random.Random(1000003 * seed + 17)
        self.now, self.seq, self.heap = 0.0, 0, []
        self.docks = VERT_DOCKS if layout == "vlm" else FLAT_DOCKS
        self.jobs = jobs if jobs is not None else internal_jobs(log)
        self.jobs = [dict(j, succ=list(j["succ"]), credit=min(self.p.credit_h, j["dur"] / 2.0)) for j in self.jobs]
        self.slots = slots_of(log, self.jobs)
        self.int_at = defaultdict(list)             # station -> internal jobs in order of their planned start
        for j in sorted(self.jobs, key=lambda j: j["t0"]):
            self.int_at[j["station"]].append(j)
        self.int_t0 = {k: [j["t0"] for j in v] for k, v in self.int_at.items()}
        # Time-critical stations go first: a slotted station (the atomizer's starts, the furnace's cycles) loses its
        # slot after `slot_grace_h`, and so does a slotted job whose predecessor (the crucible's charge) is late.
        slotted = {st for st, _ in self.slots}
        self.slotted = slotted
        self.urgent = set(slotted)
        for j in self.jobs:
            if j["station"] in slotted and j["pred"] is not None and j["pred_kind"] == "chain":
                self.urgent.add(self.jobs[j["pred"]]["station"])
        # stations and their units
        self.units, self.q_int, self.q_ext = {}, defaultdict(deque), defaultdict(deque)
        # "cells": the powder line is tended and unloaded by its own cell's arm (PR 332, R5), so the mobile units
        # neither carry for it nor attend it, and the charge station is in the cell rather than on tray B
        self.cell = set(CELL_TENDED) if self.p.attend == "cells" else set()
        for k, s in STATIONS.items():
            n = int(log["stations"].get(k, {}).get("units", DEFAULT_UNITS.get(k, 1)))
            locs = s["vert"] if layout == "vlm" else [_F(s["flat"])]
            if k in self.cell:
                locs = [_F("repowder")]
            self.units[k] = [dict(station=k, i=i, loc=locs[min(i, len(locs) - 1)], state="idle", job=None,
                                  lock=s.get("lock", True), run_h=0.0, blocked_h=0.0, t_state=0.0)
                             for i in range(n)]
        self.waiting, self.done_units = set(), []
        self.mates = defaultdict(set)               # (shuttle, tray) -> stations with a locking unit on it
        for k, us in self.units.items():
            for u in us:
                if u["loc"][0] == "tray" and u["lock"]:
                    self.mates[u["loc"][1:]].add(k)
        # shuttles
        self.sh = {s: dict(id=s, holder=None, presented=None, busy_until=0.0, running=defaultdict(int), pending=[],
                           pres_start=None, open_h=0.0, lock_h=defaultdict(float), lock_t0={}, n_pres=0)
                   for s in (1, 2)} if layout == "vlm" else {}
        home = VERT_CHARGER if layout == "vlm" else FLAT_CHARGER
        self.mm = [dict(id=i, busy=False, dock=None, pos=home, used_h=0.0, free_since=0.0, busy_h=0.0, charge_h=0.0, drive_h=0.0,
                        aisles=set(), n_tasks=0, charging=False) for i in range(n_mm)]
        self.stats = dict(task=defaultdict(list), resp=defaultdict(list), turned_away=0, ext_offered=0, ext_done=0,
                          ext_turnaround=[], ext_start_wait=[], int_start_delay=[], int_delay=[], int_done=0,
                          tray_wait=[], attended_h=0.0)
        self.t_end = {}                     # internal job id -> replayed end of its run
        self.wake = {}
        for j in self.jobs:
            if j["pred"] is None and j["t0"] < self.H:
                self._push(j["t0"], "release", j)
        self._external()

    # ---- events
    def _push(self, t, kind, x):
        self.seq += 1
        heapq.heappush(self.heap, (t, self.seq, kind, x))

    def _external(self):
        if self.ext <= 0:
            return
        for st, cat in EXT_JOBS.items():
            units = EXT_UNITS.get(st, len(self.units[st]))
            mean_h = sum(h for h, _ in cat) / len(cat)
            rate = self.ext * units / mean_h          # jobs an hour that keep `ext` of the units' clock hours busy
            t = self.p.ext_start_h + self.rng.expovariate(rate)
            while t < self.H:
                h, cv = cat[self.rng.randrange(len(cat))]
                s2 = math.log(1.0 + cv * cv)
                dur = self.rng.lognormvariate(math.log(h) - s2 / 2.0, math.sqrt(s2))
                job = dict(id=-1, station=st, campaign="external", design=None, t0=t, t1=t + dur, dur=dur, ext=True,
                           pred=None, succ=[])
                if self.p.ext_intake:
                    job["src"] = "packaging"
                self._push(t, "release", job)
                t += self.rng.expovariate(rate)

    def run(self, drain_h: float = 30 * 24.0) -> dict:
        end = self.H + drain_h
        while self.heap:
            t, _, kind, x = heapq.heappop(self.heap)
            if t > end:
                break
            self.now = t
            getattr(self, "_on_" + kind)(x)
            self._dispatch()
        return self.summary()

    def _on_release(self, j):
        j["t_req"] = self.now
        st = j["station"]
        if j["ext"]:
            self.stats["ext_offered"] += 1
            if len(self.q_ext[st]) >= self.p.max_queue:
                self.stats["turned_away"] += 1
                return
            self.q_ext[st].append(j)
        else:
            self.q_int[st].append(j)
        self.waiting.add(st)

    def _on_start(self, u):
        j = u["job"]
        t = self.now
        self._state(u, "running")
        j["t_start"] = t
        if u["loc"][0] == "tray" and u["lock"] and not u.pop("held", False):
            sh = self.sh[u["loc"][1]]
            tray = u["loc"][2]
            if sh["running"][tray] == 0:
                sh["lock_t0"][tray] = t
            sh["running"][tray] += 1
        (self.stats["ext_start_wait"] if j["ext"] else self.stats["int_start_delay"]).append(t - j["t_req"])
        self._push(t + j["dur"] - j.get("credit", 0.0) - j.get("att", 0.0), "run_done", u)

    def _on_run_done(self, u):
        j = u["job"]
        u["run_h"] += min(self.now, self.H) - min(j["t_start"], self.H)
        self._state(u, "done")
        j["t_end"] = j["t_req_out"] = self.now
        if u["loc"][0] == "tray" and u["lock"]:
            sh = self.sh[u["loc"][1]]
            tray = u["loc"][2]
            sh["running"][tray] -= 1
            if sh["running"][tray] == 0:
                t0 = sh["lock_t0"].pop(tray)
                sh["lock_h"][tray] += min(self.now, self.H) - min(t0, self.H)
        self.done_units.append(u)
        if u["station"] in self.cell:
            self._unloaded(u, j)
            self._run_done_internal(j)
            return
        self._run_done_internal(j)

    def _run_done_internal(self, j):
        if not j["ext"]:
            self.t_end[j["id"]] = self.now
            self.stats["int_delay"].append(self.now - j["t1"])
            self.stats["int_done"] += 1
            for s in j["succ"]:                     # a decision waits for the result, not for the sample
                sj = self.jobs[s]
                if sj["pred_kind"] == "decision" and sj["t0"] < self.H:
                    self._push(max(sj["t0"], self.now), "release", sj)

    def _on_arm_done(self, x):
        m, kind, u = x
        j = u["job"]
        m["busy"], m["aisles"], m["free_since"] = False, set(), self.now
        m["n_tasks"] += 1
        self.stats["task"][(kind, "ext" if j["ext"] else "int")].append(self.now - (j["t_req"] if kind == "IN"
                                                                                  else j["t_req_out"]))
        if kind == "IN":
            att = j.get("att", 0.0)
            if att > 0:
                u["run_h"] += min(self.now, self.H) - min(self.now - att, self.H)
            self._state(u, "loaded")
            if u["loc"][0] == "tray" and u["lock"] and self.p.lock == "running":
                self.sh[u["loc"][1]]["pending"].append(u)      # it starts once its tray is back in its slot
            else:
                self._on_start(u)
        else:
            self._unloaded(u, j)
        if m["used_h"] >= self.p.charge_every_h:        # worked a battery's worth without an idle spell
            reserve = m["used_h"] < self.p.charge_every_h / 0.9      # 100-10 % used; the last 10 % is the reserve
            if reserve and (any(o["charging"] for o in self.mm) or self._urgent_waiting()):
                return                                  # one unit charges at a time; slot-critical work first
            self._release_opening(m, None)
            home = VERT_CHARGER if self.layout == "vlm" else FLAT_CHARGER
            dt = (drive_s(self._dist(m["pos"], None, home, None), self.p) / 3600.0
                  + self.p.charge_h * min(1.0, m["used_h"] / self.p.charge_every_h))
            m.update(busy=True, dock=None, pos=home, charging=True)
            m["charge_h"] += dt
            self._push(self.now + dt, "charged", m)

    def _urgent_waiting(self) -> bool:
        if any(u["state"] == "done" and u["station"] in self.urgent for u in self.done_units):
            return True
        return any(self.q_int[st] for st in self.urgent if st not in self.cell)

    def _unloaded(self, u, j):
        self._state(u, "idle")
        u["job"] = None
        self.done_units.remove(u)
        if j["ext"]:
            self.stats["ext_done"] += 1
            self.stats["ext_turnaround"].append(self.now - j["t0"])
        else:
            for s in j["succ"]:                 # the next step of the same design needs the sample
                sj = self.jobs[s]
                if sj["pred_kind"] == "chain" and sj["t0"] < self.H:
                    sj["src"] = self._dock_of(u)
                    self._push(max(sj["t0"], self.now), "release", sj)
        if self.q_int[u["station"]] or self.q_ext[u["station"]]:
            self.waiting.add(u["station"])

    def _on_charged(self, m):
        m["busy"], m["used_h"], m["free_since"], m["charging"] = False, 0.0, self.now, False

    def _on_noop(self, x):
        pass

    # ---- helpers
    def _state(self, u, s):
        if u["state"] in ("done", "loaded", "unloading"):
            u["blocked_h"] += min(self.now, self.H) - min(u["t_state"], self.H)
        u["state"], u["t_state"] = s, self.now

    def _dock_of(self, u) -> str:
        return ("vlm%d" % u["loc"][1]) if u["loc"][0] == "tray" else u["loc"][1]

    def _dist(self, a, a_dock, b, b_dock) -> float:
        if self.layout == "vlm":
            return vert_dist(a, b)
        same = a_dock is not None and b_dock is not None and flat_aisle(a_dock) == flat_aisle(b_dock)
        return flat_dist(a, b, same)

    def _store(self, sh):
        """Send the presented tray back to its slot; the instruments loaded on it start when it is docked there."""
        if sh["presented"] is None:
            return
        t = max(self.now, sh["busy_until"]) + self.p.t_store * self.p.tray_slow / 3600.0
        sh["busy_until"] = t
        sh["open_h"] += min(t, self.H) - min(sh["pres_start"], self.H)
        sh["presented"], sh["pres_start"] = None, None
        for u in sh["pending"]:
            tray = u["loc"][2]                  # the tray is theirs from now: nobody may fetch it while it docks
            if sh["running"][tray] == 0:
                sh["lock_t0"][tray] = self.now
            sh["running"][tray] += 1
            u["held"] = True
            self._push(t, "start", u)
        sh["pending"] = []
        self._push(t, "noop", None)             # wake the dispatcher when the extractor is free

    def _release_opening(self, m, keep):
        """The unit stops holding any opening other than `keep`; a tray left out there goes back."""
        for sh in self.sh.values():
            if sh["holder"] == m["id"] and sh["id"] != keep:
                self._store(sh)
                sh["holder"] = None

    # ---- dispatch
    def _candidates(self):
        for u in self.done_units:
            if u["state"] == "done":            # not one a unit is already on its way to unload
                yield "OUT", u, u["job"]
        for st in sorted(self.waiting):             # sorted: a set's order follows the hash seed
            if st in self.cell:
                continue
            q = self.q_int[st] or self.q_ext[st]
            if not q:
                self.waiting.discard(st)
                continue
            seen = set()
            for u in self.units[st]:
                if u["state"] == "idle" and u["loc"] not in seen:
                    seen.add(u["loc"])
                    yield "IN", u, self._head(u, q)

    def _head(self, u, q):
        """The job a free unit of a station takes next: the first in the queue, or at a slotted station the first
        whose start window is open (the two campaigns' atomizer jobs share a queue but not their days)."""
        if u["station"] not in self.slotted or len(q) == 1:
            return q[0]
        for j in q:
            if self._slot_open(u, j):
                return j
        return q[0]

    def _slot_open(self, u, j) -> bool:
        """A slotted station (the atomizer's starts, the furnace's cycles) is loaded only while a start window is
        open, so that a sample that is early or late waits on a rack, not in the machine."""
        tab = _slot_table(self.slots, u["station"], j["campaign"] if not j["ext"] else None)
        if not tab:
            return True
        ts = next_slot(tab, self.now, self.p.slot_grace_h)
        if ts <= self.now + 1e-9:
            return True
        key = (u["station"], j["campaign"])
        if self.wake.get(key, -1.0) < ts - 1e-9:        # look again when the next window opens
            self.wake[key] = ts
            self._push(ts, "noop", None)
        return False

    def _due(self, st, t_from, t_to):
        """Internal jobs planned to start at `st` before t_to that have not started (including late ones)."""
        t0s = self.int_t0.get(st)
        if not t0s:
            return 0
        n = 0
        for i in range(bisect.bisect_left(t0s, t_from - 48.0), bisect.bisect_left(t0s, t_to)):
            j = self.int_at[st][i]
            if "t_start" not in j and j["t0"] < self.H:
                n += 1
        return n

    def _protect_ok(self, u, j) -> bool:
        """An outside job may start on unit u only in a gap that internal work does not need."""
        end = self.now + j["dur"] + self.p.protect_margin_h
        st = u["station"]
        idle_others = sum(1 for v in self.units[st] if v is not u and v["state"] == "idle")
        if self.q_int[st] and idle_others == 0:
            return False
        if self._due(st, self.now, end) > idle_others:
            return False
        if self.layout == "vlm" and u["loc"][0] == "tray" and u["lock"] and self.p.lock == "running":
            for st2 in self.mates[u["loc"][1:]]:        # a run here holds the tray for its tray-mates too
                if self.q_int[st2] or self._due(st2, self.now, end):
                    return False
        return True

    def _feasible(self, m, kind, u, j) -> bool:
        if kind == "IN" and not self._slot_open(u, j):
            return False
        if kind == "IN" and j["ext"] and self.p.protect and not self._protect_ok(u, j):
            return False
        if self.layout == "vlm":
            src = j.get("src") if kind == "IN" else None
            if src in ("vlm1", "vlm2") and src != self._dock_of(u):
                if self.sh[int(src[-1])]["holder"] not in (None, m["id"]):
                    return False
            if u["loc"][0] != "tray":
                return True
            sh = self.sh[u["loc"][1]]
            if sh["holder"] not in (None, m["id"]):
                return False
            if sh["presented"] == u["loc"][2]:
                return True
            return not (self.p.lock == "running" and sh["running"][u["loc"][2]] > 0)
        if self.p.aisle_exclusive and self.n_mm > 1:
            need = {flat_aisle(self._dock_of(u))}
            if kind == "IN" and j.get("src"):
                need.add(flat_aisle(j["src"]))
            for o in self.mm:
                if o is not m and o["busy"] and o["aisles"] & need:
                    return False
        return True

    def _serve_cells(self):
        for st in sorted(self.cell):
            q = self.q_int[st] or self.q_ext[st]
            while q:
                u = next((u for u in self.units[st] if u["state"] == "idle"), None)
                if u is None:
                    break
                j = self._head(u, q)
                if not self._slot_open(u, j):
                    break
                q.remove(j)
                j["att"] = 0.0
                u["job"] = j
                self._state(u, "reserved")
                self._on_start(u)

    def _dispatch(self):
        self._serve_cells()
        for m in self.mm:
            if m["busy"]:
                continue
            best = None
            for kind, u, j in self._candidates():
                if not self._feasible(m, kind, u, j):
                    continue
                t_req = j["t_req"] if kind == "IN" else j["t_req_out"]
                dock = self._dock_of(u)
                bonus = 0.0
                if u["loc"][0] == "tray" and self.sh[u["loc"][1]]["presented"] == u["loc"][2] \
                        and self.sh[u["loc"][1]]["holder"] == m["id"]:
                    bonus = self.p.bonus_tray
                elif m["dock"] == dock:
                    bonus = self.p.bonus_dock
                # time-critical stations first, then internal loads and every unload (a finished outside job
                # must not hold an instrument that internal work is waiting for), then outside loads
                cls = 2 if (j["ext"] and kind == "IN") else (0 if u["station"] in self.urgent else 1)
                key = (cls, t_req - bonus / 3600.0)
                if best is None or key < best[0]:
                    best = (key, kind, u, j)
            if best is None:
                self._release_opening(m, None)      # nothing to do: put the tray away so its instruments start
                continue
            self._assign(m, *best[1:])

    def _go(self, m, dock, t) -> float:
        """Drive to a dock and localize there, unless already docked at it. Returns the new time (hours)."""
        if m["dock"] == dock:
            return t
        for o in self.mm:                       # an idle unit parked at that dock moves off
            if o is not m and not o["busy"] and o["dock"] == dock:
                o["dock"] = None
        dt = (drive_s(self._dist(m["pos"], m["dock"], self.docks[dock], dock), self.p) + self.p.t_dock) / 3600.0
        m["drive_h"] += dt
        m["pos"], m["dock"] = self.docks[dock], dock
        return t + dt

    def _assign(self, m, kind, u, j):
        p, t = self.p, self.now
        dock = self._dock_of(u)
        tray = u["loc"][0] == "tray"
        sh = self.sh[u["loc"][1]] if tray else None
        self._release_opening(m, sh["id"] if tray else None)
        if kind == "IN":
            q = self.q_int[u["station"]] if not j["ext"] else self.q_ext[u["station"]]
            if q and q[0] is j:
                q.popleft()
            else:
                q.remove(j)
            u["job"] = j
            self._state(u, "reserved")
        else:
            self._state(u, "unloading")
        m["busy"] = True
        # an idle unit recharges at its charger, but only in a gap long enough to drive there and back: the rest of
        # the gap gives back charge_every_h of work per charge_h
        home = VERT_CHARGER if self.layout == "vlm" else FLAT_CHARGER
        trip = 2.0 * drive_s(self._dist(m["pos"], m["dock"], home, None), p) / 3600.0 + p.opp_min_h
        gap = self.now - m["free_since"]
        if gap > trip:
            m["used_h"] = max(0.0, m["used_h"] - (gap - trip) * p.charge_every_h / p.charge_h)
        if self.layout == "flat":
            m["aisles"] = {flat_aisle(dock)}
        arm = p.t_arm + p.t_rack
        att = attend_h(u["station"], j["dur"] - j.get("credit", 0.0), p.attend) if kind == "IN" else 0.0
        if kind == "IN":
            j["att"] = att
            self.stats["attended_h"] += att
        src = j.get("src") if kind == "IN" else None
        fresh, ready = False, t
        if tray:
            sh["holder"] = m["id"]
            if sh["presented"] != u["loc"][2]:          # put the presented tray away, then fetch this one
                self._store(sh)
                fresh = True
                if p.prefetch:                          # the Shuttle fetches while the unit drives over
                    sh["pres_start"] = max(self.now, sh["busy_until"])
                    ready = sh["pres_start"] + p.t_fetch * p.tray_slow / 3600.0
                    sh.update(presented=u["loc"][2], busy_until=ready)
                    sh["n_pres"] += 1
        if src and src != dock:                     # fetch the sample from the rack where the last step left it
            if self.layout == "flat":
                m["aisles"].add(flat_aisle(src))
            t = self._go(m, src, t) + p.t_rack / 3600.0
            arm = p.t_arm
        t = self._go(m, dock, t)
        if tray and fresh:
            if not p.prefetch:                      # the fetch starts only when the unit is there
                t = max(t, sh["busy_until"])
                sh["pres_start"] = t
                sh["n_pres"] += 1
                ready = t + p.t_fetch * p.tray_slow / 3600.0
                sh.update(presented=u["loc"][2], busy_until=ready)
            self.stats["tray_wait"].append(max(0.0, ready - t))
            t = max(t, ready) + p.t_tray_loc / 3600.0
        self.stats["resp"][(kind, "ext" if j["ext"] else "int")].append(t - (j["t_req"] if kind == "IN"
                                                                             else j["t_req_out"]))
        t += (arm + att * 3600.0) / 3600.0
        m["busy_h"] += min(t, self.H) - min(self.now, self.H)
        m["used_h"] += t - self.now
        self._push(t, "arm_done", (m, kind, u))

    # ---- results
    def summary(self) -> dict:
        H = self.H
        S = self.stats

        def q(v, f):
            v = sorted(v)
            return v[min(len(v) - 1, int(f * len(v)))] if v else None

        def mean(v):
            return sum(v) / len(v) if v else None

        tasks = {"%s_%s" % k: dict(n=len(v), mean_min=mean(v) * 60, p95_min=q(v, 0.95) * 60)
                 for k, v in S["task"].items() if v}
        resp = {"%s_%s" % k: dict(n=len(v), mean_min=mean(v) * 60, p50_min=q(v, 0.5) * 60, p95_min=q(v, 0.95) * 60)
                for k, v in S["resp"].items() if v}
        units = {k: dict(util=sum(u["run_h"] for u in us) / (H * len(us)),
                         blocked=sum(u["blocked_h"] for u in us) / (H * len(us))) for k, us in self.units.items()}
        out = dict(
            layout=self.layout, n_mm=self.n_mm, ext_load=self.ext, horizon_days=H / 24.0, tasks=tasks, resp=resp,
            stations=units, attended_h_per_day=S["attended_h"] / (H / 24.0),
            tray_wait_s=dict(n=len(S["tray_wait"]), mean=(mean(S["tray_wait"]) or 0.0) * 3600,
                             p95=(q(S["tray_wait"], 0.95) or 0.0) * 3600),
            mm=[dict(busy=m["busy_h"] / H, charging=m["charge_h"] / H, drive_share=m["drive_h"] / max(m["busy_h"], 1e-9),
                     drive_s_per_task=3600.0 * m["drive_h"] / max(m["n_tasks"], 1),
                     tasks_per_day=m["n_tasks"] / (H / 24.0)) for m in self.mm],
            mm_busy=sum(m["busy_h"] for m in self.mm) / (H * self.n_mm),
            external=dict(load=self.ext, offered=S["ext_offered"], done=S["ext_done"], turned_away=S["turned_away"],
                     done_per_day=S["ext_done"] / (H / 24.0),
                     served=S["ext_done"] / S["ext_offered"] if S["ext_offered"] else None,
                     turnaround_h=mean(S["ext_turnaround"]), turnaround_p95_h=q(S["ext_turnaround"], 0.95),
                     start_wait_h=mean(S["ext_start_wait"]), start_wait_p95_h=q(S["ext_start_wait"], 0.95)),
            atomizer_runs=sum(1 for j in self.jobs if j["station"] == "atomizer" and j["t0"] < H),
            atomizer_late=sum(1 for j in self.jobs if j["station"] == "atomizer" and j["t0"] < H
                              and j.get("t_start", 1e18) > j["t0"] + self.p.slot_grace_h + 1e-6),
            internal=dict(done=S["int_done"], start_delay_min=(mean(S["int_start_delay"]) or 0) * 60,
                          end_delay_p50_h=q(S["int_delay"], 0.5),
                          start_delay_p95_min=(q(S["int_start_delay"], 0.95) or 0) * 60,
                          end_delay_h=mean(S["int_delay"]), end_delay_p95_h=q(S["int_delay"], 0.95)))
        if self.sh:
            for sh in self.sh.values():
                for tray, t0 in sh["lock_t0"].items():
                    sh["lock_h"][tray] += max(0.0, H - min(t0, H))
            out["openings"] = {s: dict(busy=sh["open_h"] / H, presentations_per_day=sh["n_pres"] / (H / 24.0))
                               for s, sh in self.sh.items()}
            out["tray_locked"] = {"%d%s" % (s, tray): h / H for s, sh in self.sh.items()
                                  for tray, h in sorted(sh["lock_h"].items())}
        return out


# ----------------------------------------------------------------------------------------------------- targets
def targets() -> dict:
    """The twin's two targets per campaign (twin/bench2.py targets(), from out/twin2/oracle.json)."""
    o = json.loads((ROOT / "out" / "twin2" / "oracle.json").read_text())
    t1 = {k: o[k]["sota_utility"] for k in ("flaime_al", "onr_cu")}
    t2 = {k: round(o[k]["sota_utility"] + 0.5 * (o[k]["best_found"]["utility"] - o[k]["sota_utility"]), 4)
          for k in t1}
    return {"T1": t1, "T2": t2}


def reference_filter(log: dict) -> dict:
    """{campaign: set of design ids that are re-tests of a reference alloy} (twin/bench3.py's rule)."""
    from twin import spaces as SP
    out = {}
    for camp, designs in log["designs"].items():
        refs = [{e: w.get(e, 0.0) for e in SP.SPACES[camp].elements} for w in SP.REFERENCE[camp].values()]
        out[camp] = {str(k) for k, comp in designs.items()
                     if any(all(abs(comp.get(e, 0.0) - r[e]) < 0.06 for e in r) for r in refs)}
    return out


def days_to_targets(log: dict, jobs: list, t_end: dict | None, refs: dict, T: dict | None = None) -> dict:
    """Day each campaign first reaches each target, from the log's demonstrated new alloys. With `t_end` (a replay's
    run ends by job id) each result moves by the delay of the last booking of its design that ended before it."""
    T = T or targets()
    last = defaultdict(list)
    for j in jobs:
        last[(j["campaign"], j["design"])].append(j)
    out = {}
    for camp in ("flaime_al", "onr_cu"):
        pts = []
        for r in log["results"]:
            if r.get("type") != "demonstrated" or r["campaign"] != camp or str(r["design"]) in refs.get(camp, ()):
                continue
            t = r["t_h"]
            if t_end is not None:
                prev = [j for j in last[(camp, r["design"])] if j["t1"] <= t + 1e-6 and j["id"] in t_end]
                if prev:
                    j = max(prev, key=lambda j: j["t1"])
                    t += t_end[j["id"]] - j["t1"]
            pts.append((t, r["u_true"]))
        pts.sort()
        for name in ("T1", "T2"):
            day = next((t / 24.0 for t, u in pts if u >= T[name][camp] - 1e-12), None)
            out["%s_%s" % (camp, name)] = day
    return out


# ----------------------------------------------------------------------------------------------------- runs
OWN_PLAIN = {"atomizer", "immersion", "cubxl"}     # round 5: the lab's own stations that carry no "@vcl"


def round5_log(log: dict) -> tuple[dict, float]:
    """A round-5 event log (PR 405, twin/round5.py) in round 3b's terms: the lab's own instruments ("<station>@vcl")
    under their round-3 names, with the atomizer, the immersion and the CubXL; BYU's existing equipment, core
    facilities and partners (stations without "@vcl") are left out, since people, not the lab's robots, serve them.
    Returns the log and the hour of its first in-house step (when outside work could start)."""
    st = dict(log["stations"])
    stations = {}
    for k, v in st.items():
        if k.endswith("@vcl") and k[:-4] in STATIONS:
            stations[k[:-4]] = dict(v, external=False)
        elif k in OWN_PLAIN or k in HELPERS:
            stations[k] = dict(v)
    events, first = [], None
    for e in log["events"]:
        k = e["station"]
        if k.endswith("@vcl") and k[:-4] in STATIONS:
            events.append(dict(e, station=k[:-4]))
            first = e["t0_h"] if first is None else min(first, e["t0_h"])
        elif k in OWN_PLAIN or k in HELPERS:
            events.append(e)
    return dict(log, stations=stations, events=events), (first or 0.0)


def run_one(log_path, layout: str, n_mm: int, ext: float, seed: int = 0, params: dict | None = None,
            with_targets: bool = True, round5: bool = False) -> dict:
    log = load_log(log_path)
    params = dict(params or {})
    if round5:
        log, first = round5_log(log)
        params.setdefault("ext_start_h", first)
        with_targets = False          # round 5's targets are its own (twin/like5.py), not round 2's oracle
    jobs = internal_jobs(log)
    sim = Sim(log, layout, n_mm, ext, Params(**params), seed=seed, jobs=jobs)
    out = sim.run()
    out.update(log=Path(log_path).name.replace(".json.xz", ""), seed=seed, params=params or {})
    if with_targets:
        refs = reference_filter(log)
        out["days_twin"] = days_to_targets(log, jobs, None, refs)
        out["days"] = days_to_targets(log, jobs, sim.t_end, refs)
    return out


def decision_holds(paths) -> dict:
    """Round 5's decision time, read off its logs: the results held for a person's decision point
    (``round5.held``: (kind, from h, to h) per campaign). {"holds": per-log counts, "median_h": per-log medians}."""
    out = dict(holds=[], median_h=[], total_h=[])
    for path in paths:
        held = load_log(path).get("round5", {}).get("held", {})
        durs = sorted(b - a for c in held for (_, a, b) in held[c])
        out["holds"].append(len(durs))
        out["median_h"].append(durs[len(durs) // 2] if durs else 0.0)
        out["total_h"].append(sum(durs))
    return out


def _worker(a):
    return run_one(*a)


def _worker5(a):
    return run_one(*a, with_targets=False, round5=True)


MAIN_LOGS = [f"r3_vertical_lab_{pol}_s{s}.json.xz" for pol in ("bofn3", "tiered") for s in range(12)]
MODES = ("none", "cells")              # the twin's timing; PR 332's attended time with the powder line in a cell
SENS_LOGS = [f"r3_vertical_lab_{pol}_s{s}.json.xz" for pol in ("bofn3", "tiered") for s in range(2)]
SENS = {
    "base (the twin's timing)": {},
    "attended time (PR 332, powder line in a cell)": dict(attend="cells"),
    "attended time everywhere (PR 332; the replay loses atomizer slots)": dict(attend="pr332"),
    "trays may move while instruments run": dict(lock="never"),
    "attended, trays may move while instruments run": dict(attend="cells", lock="never"),
    "gentle trays (2.5x slower)": dict(tray_slow=2.5),
    "attended, gentle trays (2.5x slower)": dict(attend="cells", tray_slow=2.5),
    "no pre-fetch (the Shuttle waits for the unit)": dict(prefetch=False),
    "slow handling (dock 150 s, load 120 s)": dict(t_dock=150.0, t_arm=120.0),
    "fast handling (dock 30 s, load 30 s)": dict(t_dock=30.0, t_arm=30.0),
    "driving at 0.3 m/s (Liverpool's cap)": dict(v_mm=0.3),
    "driving at 1.5 m/s": dict(v_mm=1.5),
    "a bare MiR250's battery (13 h a charge, 52 min to charge)": dict(charge_every_h=13.0, charge_h=52.0 / 60.0),
    "attended, a bare MiR250's battery": dict(attend="cells", charge_every_h=13.0, charge_h=52.0 / 60.0),
    "aisles shared (flat)": dict(aisle_exclusive=False),
    "outside samples carried from packaging": dict(ext_intake=True),
    "outside work first come, first served (no gaps kept for internal work)": dict(protect=False),
    "attended, outside work first come, first served": dict(attend="cells", protect=False),
}


def grid(logs=None, layouts=LAYOUTS, loads=LOADS, params=None, workers: int = 4, events=None,
         round5: bool = False) -> list:
    from multiprocessing import Pool
    logs = logs or MAIN_LOGS
    events = Path(events) if events else EVENTS
    args = [(str(events / lg), lay, n, ext, i, params) for i, lg in enumerate(logs) for lay, n in layouts
            for ext in loads]
    with Pool(workers) as pool:
        return pool.map(_worker5 if round5 else _worker, args, chunksize=1)


# Round 5 (PR 405): the automated lab, built from the day the money arrives and run for two years, with every route at
# once and decisions that wait for people (nominal), the cheap policies. Its logs are on PR 405's branch, not this one:
#   git show origin/claude/twin-round5-20261127:vertical-lab/out/twin5/events/<log> > <dir>/<log>
R5_LOGS = [f"r5_vertical_parallel_fast_reorder_s{s}.json.xz" for s in range(16)]


def _save(path: Path, obj) -> None:
    with lzma.open(path, "wt") as fh:
        json.dump(obj, fh, separators=(",", ":"))


def _load(path: Path):
    with lzma.open(path, "rt") as fh:
        return json.load(fh)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    OUT.mkdir(parents=True, exist_ok=True)
    from twin import worth_it_report as R
    if cmd == "one":
        prm = json.loads(argv[6]) if len(argv) > 6 else None
        print(json.dumps(run_one(EVENTS / argv[2], argv[3], int(argv[4]), float(argv[5]), params=prm), indent=1))
    elif cmd == "run":
        rows = [r for mode in MODES for r in grid(params=dict(attend=mode))]
        _save(OUT / "results.json.xz", dict(params=asdict(Params()), logs=MAIN_LOGS, rows=rows))
        R.write(rows)
    elif cmd == "sens":
        out = {name: grid(SENS_LOGS, loads=(0.3, 0.6), params=prm) for name, prm in SENS.items()}
        _save(OUT / "sensitivity.json.xz", out)
        R.write_sens(out)
    elif cmd == "run5":                       # python -m twin.worth_it run5 <dir with round 5's logs>
        rows = [r for mode in MODES for r in grid(R5_LOGS, params=dict(attend=mode), events=argv[2], round5=True)]
        _save(OUT / "results_r5.json.xz", dict(params=asdict(Params()), logs=R5_LOGS, rows=rows))
        R.write(rows, name="tables_r5.md", round5=True)
    elif cmd == "holds":                      # python -m twin.worth_it holds <dir>: round 5's decision time
        import statistics
        d = Path(argv[2])
        for tag, names in (("nominal", R5_LOGS), ("slow", [n.replace(".json.xz", "_dec-slow.json.xz") for n in R5_LOGS]),
                           ("none", [n.replace(".json.xz", "_dec-none.json.xz") for n in R5_LOGS])):
            paths = [d / n for n in names if (d / n).exists()]
            if paths:
                h = decision_holds(paths)
                print(tag, len(paths), "logs: holds a log", statistics.median(h["holds"]), "; median hold (h)",
                      round(statistics.median(h["median_h"]), 1))
    elif cmd == "tables":
        R.write(_load(OUT / "results.json.xz")["rows"])
        if (OUT / "sensitivity.json.xz").exists():
            R.write_sens(_load(OUT / "sensitivity.json.xz"))
        if (OUT / "results_r5.json.xz").exists():
            R.write(_load(OUT / "results_r5.json.xz")["rows"], name="tables_r5.md", round5=True)


if __name__ == "__main__":
    main(sys.argv)

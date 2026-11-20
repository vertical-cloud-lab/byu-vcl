"""Automatic floor cleaning for spilled powder (#366, #303): how much of the lab's floor each kind of cleaner reaches,
how long its passes take, and how it fits the lab's year (upkeep.py's schedule).

    python3 floor_cleaning.py            # everything -> out/floor_cleaning.json, out/floor_cleaning_reach.png,
                                         #               out/floor_cleaning_year.png
    python3 floor_cleaning.py reach      # the floor maps and the coverage table only
    python3 floor_cleaning.py year       # the schedules only (needs the reach for the pass times; it is quick)

Sterling, on PR #318 (2026-11-20): powder (Al, Cu, Ni, NAB, alloy fines) will end up on the floor around the
atomizer, sieving, depowdering and the trays; explore automatic floor cleaning: a Roomba-like device adapted to an
explosion-proof vacuum, or a third MiR250 carrying a combustible-dust-rated vacuum that works with one of the mobile
manipulators when needed, and maybe a UR arm on it as well. Notes: notes/floor_cleaning.md.

**The floor** is setup_lab.py fit's floor plan (out/tray_plan.json "floor": every machine's plan rectangle, the docks,
the target posts, the chargers, the aisle) on a 25 mm grid, between the side racking (warehouse.RACKS) and from the
north racking to 400 mm past the Meltio cell. Two things are ours and are added: the atomizer's vacuum station (PR
#353's two 118EXPs and their post, which the lab's floor plan doesn't have yet) and the cleaner's own bay.

**The cleaners** are footprints with a clearance: a robot centre is reachable if its footprint (grown by the
clearance) touches no obstacle at a heading of 0 or 90 deg and it is connected to the aisle, turning only where its
corners' circle is clear. What it cleans is where its nozzle passes (a disc robot: its own disc; a MiR250 with a nozzle
across its back: the nozzle's strip; an arm with the wand: the floor within the wand's reach of the robot). Narrow-gap
travel at cleaning speed assumes the MiR's reduced safety fields (as when docking); at travel speed MiR asks for a
1450 mm corridor (warehouse.MIR250).

**The year** is upkeep.py's (timelapse.simulate with upkeep booked). A pass is due after every atomizer run, sieving
and depowdering, at that station's zone, and the whole of the powder zones and the aisle is swept every night. Each
option books those passes on a different resource: the one person (on shift only), the two existing units (their
transfers wait), or a cleaner of its own (a separate line; it yields to a unit's transfer at the same dock and to the
person's crucible hour at the atomizer).

Everything here is a model. Every figure without a source says "assumed".
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "floor_cleaning"

# ================================================================================================ the floor
CELL = 25.0                                    # mm, grid
X_LIM = (-11833.0, 11833.0)                    # the side racking's inner faces (warehouse.RACKS: x0 -12900 + 1067)
Y_LIM = (-12800.0, 2800.0)                     # 400 mm past the Meltio cell's far side; the north racking's face
PLAN = OUT / "tray_plan.json"                  # setup_lab.py fit's output (round 13)
NAMES = {"glovebox": "glovebox", "repowder": "rePowder", "aconity": "Aconity MIDI", "packaging": "packaging",
         "instron_floor": "Instron 68FM-100", "instron_small": "68SC-2", "fumehood": "fume hood", "ded": "DED",
         "wire_edm": "wire EDM", "eos_m400": "EOS M 400-4", "meltio_cell": "Meltio cell", "sieve_cell": "sieving",
         "vlm": "Shuttle 1", "vlm2": "Shuttle 2", "charger0": "charger", "charger1": "charger"}
POST_FOOT = 150.0                              # half-size of a target post's foot plate (warehouse.Floor._tape)
# ours: PR #353's vacuum station on the lab floor. Its clip (atom_vacuum.py) stands the two 118EXPs at the rePowder's
# west end with the pail, the extinguisher and the sign at y -2460 to -3260, which is the lab's aisle (y -2400 to
# -5400). Here (floor_clean_still.py draws it) they stand west of the machine, behind the dock line: the two 508 x 610
# mm vacuums side by side (Al family west, Cu family east), our post with the holster, rack and fixture behind them
# with a pail each side, the Class D extinguisher and the sign at the front corner, clear of the rePowder dock's pivot
# circle. 1.19 x 1.64 m in all (x, y ranges in mm)
VAC_STATION = (-5900.0, -4710.0, -1980.0, -340.0)
# ours: the cleaner's bay, for the options with a cleaner of its own: a third MiR Charge 48V in the south row, 1.6 m
# west of units 1-2's (warehouse.CHARGERS x -1500 and -300), outside every powder zone (charging belongs outside any
# classified area: OSHA 1910.178(g)(1), Karcher's Zone 22 practice) and clear of the small Instron's target post. Full
# liners go to the grounded pails at the vacuum stations, so the bay has none.
BAY = dict(charger=(-3411.0, -2789.0, -6725.0, -6238.0), park=(-3100.0, -5818.0, -90.0))

# The powder zones (ours): DAL tapes a containment area round the atomizer (atom_base.py draws it 600 mm round the
# machine), so each source here is its footprint grown by 600 mm; the Shuttles' openings are their 996 mm opening
# grown by 600 mm a side, from the lip 950 mm out (the docked MiR and 300 mm); the aisle is where the units carry
# jars. (x0, x1, y0, y1) mm, and what puts powder there.
ZONE_PAD = 600.0
ZONES_SPEC = {
    "atomizer": ("repowder", "the rePowder: container off, chamber vacuumed, liners, the crucible hour"),
    "sieving": ("sieve_cell", "the sieving cell: jars, sieves and the tipper on its downdraft bench"),
    "midi": ("aconity", "the Aconity MIDI: the 55 mm kit's powder change, unloading, the depowdering lance and box"),
    "opening 1": (None, "Shuttle 1's opening: powder trays B (the multi-doser), D (XRD and SEM prep), E (the "
                        "Mastersizer) presented"),
    "opening 2": (None, "Shuttle 2's opening: tray M (the XRF's powder) presented"),
    "glovebox": ("glovebox", "the glovebox's antechamber end, where powder goes in and out"),
    "DED": ("ded", "the powder-fed DED (InssTek MX-Lab class)"),
    "EOS": ("eos_m400", "the EOS M 400-4: powder by the 100 kg, handled by people (no MiR dock)"),
    "aisle": (None, "the aisle the units carry jars, cups and plates along"),
}
OPENING_W = 996.0                              # round 7's opening (README: "a 996 mm opening")
LIP_Y = -1612.0                                # timelapse.LIP: the front of the cover under an opening
SHUTTLE_X = {"opening 1": 0.0, "opening 2": 3630.0}   # tray_plan.json shuttle_x
DOCK_OF_ZONE = {"atomizer": "repowder", "sieving": "sieve_cell", "midi": "aconity", "opening 1": "vlm",
                "opening 2": "vlm2", "glovebox": "glovebox", "DED": "ded"}
STATION_OF_ZONE = {"atomizer": "repowder", "sieving": "sieve_cell", "midi": "aconity", "DED": "ded"}


class Floor:
    """The occupancy grid and the zones. occ[i, j] is True where a machine, a post, a charger, a station or the room's
    edge is; row i is y, column j is x."""

    def __init__(self, plan=PLAN, bay=False):
        d = json.loads(Path(plan).read_text())["floor"]
        self.plan = d
        self.nx = int(round((X_LIM[1] - X_LIM[0]) / CELL))
        self.ny = int(round((Y_LIM[1] - Y_LIM[0]) / CELL))
        self.xc = X_LIM[0] + (np.arange(self.nx) + 0.5) * CELL
        self.yc = Y_LIM[0] + (np.arange(self.ny) + 0.5) * CELL
        self.X, self.Y = np.meshgrid(self.xc, self.yc)
        occ = np.zeros((self.ny, self.nx), bool)
        self.rects = {}
        for k, (x0, x1, y0, y1) in d["machines"].items():
            self.rects[k] = (x0, x1, y0, y1)
            occ |= self.rect(x0, x1, y0, y1)
        self.posts = []
        for k, dk in d["docks"].items():
            px, py = dk["target_post"]
            self.posts.append((px, py))
            occ |= self.rect(px - POST_FOOT, px + POST_FOOT, py - POST_FOOT, py + POST_FOOT)
        self.rects["vacuum station"] = VAC_STATION
        occ |= self.rect(*VAC_STATION)
        if bay:
            self.rects["bay charger"] = BAY["charger"]
            occ |= self.rect(*BAY["charger"])
        occ[0, :] = occ[-1, :] = occ[:, 0] = occ[:, -1] = True      # the room's edge
        self.occ = occ
        self.free = ~occ
        self.aisle = tuple(d["aisle_mm"])                           # x0, x1, y0, y1
        self.zones = self._zones()

    def rect(self, x0, x1, y0, y1) -> np.ndarray:
        return (self.X >= x0) & (self.X <= x1) & (self.Y >= y0) & (self.Y <= y1)

    def ij(self, x, y) -> tuple[int, int]:
        return int((y - Y_LIM[0]) // CELL), int((x - X_LIM[0]) // CELL)

    def _zones(self) -> dict:
        out = {}
        for z, (src, _) in ZONES_SPEC.items():
            if z == "aisle":
                x0, x1, y0, y1 = self.aisle
                r = (x0, x1, min(y0, y1), max(y0, y1))
            elif src is None:
                cx = SHUTTLE_X[z]
                r = (cx - OPENING_W / 2 - ZONE_PAD, cx + OPENING_W / 2 + ZONE_PAD, LIP_Y - 950.0, LIP_Y)
            elif z == "glovebox":                                    # its antechamber end, towards the aisle
                x0, x1, y0, y1 = self.rects[src]
                r = (x0 - ZONE_PAD, x1 + ZONE_PAD, y0 - ZONE_PAD, y0 + ZONE_PAD)
            else:
                x0, x1, y0, y1 = self.rects[src]
                r = (x0 - ZONE_PAD, x1 + ZONE_PAD, y0 - ZONE_PAD, y1 + ZONE_PAD)
            out[z] = dict(rect=tuple(float(v) for v in r), mask=self.rect(*r) & self.free)
        return out

    def area_m2(self, mask) -> float:
        return float(mask.sum()) * CELL * CELL / 1e6


# ================================================================================================ the cleaners
# Each: the footprint (a disc of diameter d, or L x W), the clearance it keeps (assumed), what it cleans, and its pass
# rate (an effective width, a speed and a factor for turns and edges, all assumed unless cited), with the fixed time a
# job takes (the vacuum SOP's continuity check, run-on and settle, or the robot's own start and stop).
ROBOTS = {
    "disc": dict(
        label="Roomba-class disc", shape="disc", d=350.0, clear=10.0, cleans=("disc", 175.0),
        w_eff=0.20, v=0.25, k=1.6, fixed_min=1.0,
        source="iRobot Roomba 900-class: about 350 mm across and 92 mm tall (assumed from its class; no model is "
               "picked). Bumps along edges; side brush to the edge. None is rated for combustible dust"),
    "pad": dict(
        label="commercial vacuum robot (Gausium Vacuum 40 class)", shape="rect", L=800.0, W=690.0, clear=30.0,
        cleans=("front", 690.0, 1.0), w_eff=0.65, v=0.35, k=1.3, fixed_min=1.0,
        source="Gausium Vacuum 40: 800 x 690 x 890 mm, 91 kg, a 720 mm path with its side brushes, 3 h (gausium.com "
               "specs; $42,000 at RobotLAB, 2026-11-20). The KIRA CV 60/1 is bigger: 50 x 30 x 52 in, 850 lb, a 24 in "
               "path (kaercher.com). 0.35 m/s is ours, slow for fine powder. None is rated for combustible dust"),
    "mir": dict(
        label="MiR250 + floor nozzle", shape="rect", L=880.0, W=580.0, clear=50.0, cleans=("rear", 560.0, 80.0),
        w_eff=0.50, v=0.20, k=1.3, fixed_min=3.0,
        source="MiR250 800 x 580 mm (warehouse.MIR250) with a 560 mm nozzle across its back (ours, 80 mm deep: a "
               "full-width squeegee nozzle, as the 118EXP's floor squeegee 01768800 does by hand); 0.2 m/s is slow "
               "for fine powder (assumed); 3 min a job for the continuity check, run-on and settle (vacuum SOP 1, "
               "4.1-4.3)"),
    "mir_arm": dict(
        label="MiR250 + UR10e + wand", shape="rect", L=800.0, W=580.0, clear=50.0, cleans=("arm", 1300.0),
        w_eff=0.30, v=0.15, k=1.25, fixed_min=4.0,
        source="MiR250 + UR10e; the 14 in (356 mm) floor tool on the wand, 0.30 m a stroke with overlap; the "
               "floor 1.3 m from the robot's centre at most (the UR10e's 1300 mm reach from a base about 600 mm up, "
               "plus the wand: assumed); 0.15 m/s strokes; 4 min a job (continuity on the fixture, as atom_vacuum)"),
    "units_pou": dict(
        label="units 1-2 + vacuums at the stations", shape="rect", L=800.0, W=580.0, clear=50.0,
        cleans=("arm_hose", 1300.0, 7000.0), w_eff=0.30, v=0.15, k=1.25, fixed_min=4.0,
        source="the two existing MiR250 + UR10e units, taking the wand of a 118EXP that stands at each powder "
               "zone, as arm 2 does at the atomizer (atom_vacuum); a 25 ft (7.6 m) conductive hose, 7.0 m of reach "
               "(Ruwac's EXP151525CB kit has one); arm reach as above"),
    "person": dict(
        label="a person with the 118EXP", shape="disc", d=450.0, clear=0.0, cleans=("arm", 1000.0),
        w_eff=0.30, v=0.30, k=1.3, fixed_min=10.0,
        source="the lab's practice: the 118EXP by hand (vacuum SOP); a person stands where a 450 mm circle fits and "
               "the wand reaches 1.0 m; 10 min a job for the SOP's continuity check, area checks and liner check"),
}
# point-of-use vacuum stations for units_pou (ours): the atomizer's (PR #353), one at the sieving cell, one at the MIDI
# (atom_vacuum.md's third vacuum serves the printer line), one by each opening, one at the DED
POU = {"atomizer": (-5230.0, -1640.0), "sieving": (-2800.0, -900.0), "midi": (5500.0, -1300.0),
       "opening 1": (-1700.0, -1600.0), "opening 2": (1815.0, -1600.0), "DED": (3000.0, -6300.0),
       "glovebox": (-6500.0, -1400.0)}


def _shift(a, oy: int, ox: int) -> np.ndarray:
    """a moved oy rows and ox columns (towards higher indices when positive), zero-filled."""
    out = np.zeros_like(a)
    ny, nx = a.shape
    out[max(oy, 0):ny + min(oy, 0), max(ox, 0):nx + min(ox, 0)] = \
        a[max(-oy, 0):ny + min(-oy, 0), max(-ox, 0):nx + min(-ox, 0)]
    return out


def _dilate_rect(mask, hx: int, hy: int, ox: int = 0, oy: int = 0) -> np.ndarray:
    """mask grown by a rectangle of half-sizes hx, hy cells, centred ox, oy cells from each true cell."""
    from scipy import ndimage
    g = ndimage.maximum_filter(mask.astype(np.uint8), size=(2 * hy + 1, 2 * hx + 1), mode="constant") > 0
    return _shift(g, oy, ox) if (ox or oy) else g


def reach(F: Floor, key: str) -> dict:
    """{centres: where the robot's centre can be (any heading), covered: the floor it cleans, ...} for one cleaner."""
    from scipy import ndimage
    r = ROBOTS[key]
    edt = ndimage.distance_transform_edt(F.free) * CELL               # mm from each free cell to the nearest obstacle
    seed = F.ij(0.0, (F.aisle[2] + F.aisle[3]) / 2)
    if r["shape"] == "disc":
        ok = edt >= r["d"] / 2 + r["clear"]
        lab, _ = ndimage.label(ok)
        cen = lab == lab[seed]
        layers = [cen]
    else:
        hx = int(math.ceil((r["L"] / 2 + r["clear"]) / CELL))
        hy = int(math.ceil((r["W"] / 2 + r["clear"]) / CELL))
        free0 = ~_dilate_rect(F.occ, hx, hy)                          # heading 0/180: long side along x
        free90 = ~_dilate_rect(F.occ, hy, hx)
        turn = edt >= math.hypot(r["L"] / 2, r["W"] / 2) + r["clear"]  # it can turn on the spot here
        l0, n0 = ndimage.label(free0)
        l90, n90 = ndimage.label(free90)
        parent = list(range(n0 + n90 + 2))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        both = turn & free0 & free90
        for a, b in set(zip(l0[both].tolist(), (l90[both] + n0).tolist())):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
        s0 = l0[seed]
        root = find(s0) if s0 else None
        if root is None:
            raise RuntimeError(f"{key}: the aisle's centre isn't free")
        ok0 = np.isin(l0, [i for i in range(1, n0 + 1) if find(i) == root])
        ok90 = np.isin(l90, [i for i in range(1, n90 + 1) if find(i + n0) == root])
        cen = ok0 | ok90
        layers = [ok0, ok90]
    how = r["cleans"]
    if how[0] == "disc":
        cov = (ndimage.distance_transform_edt(~cen) * CELL <= how[1]) & F.free
    elif how[0] in ("rear", "front"):
        w, dep = how[1], how[2]
        L = r["L"]
        off = (L / 2 - dep / 2) if how[0] == "rear" else (L / 2 - dep / 2)
        cov = np.zeros_like(cen)
        for li, lay in enumerate(layers):
            if not lay.any():
                continue
            o = int(round(off / CELL))
            if li == 0:          # long side along x: the nozzle at either end (it drives its lanes both ways)
                hx, hy = max(0, int(round(dep / 2 / CELL))), int(round(w / 2 / CELL))
                cov |= _dilate_rect(lay, hx, hy, o, 0) | _dilate_rect(lay, hx, hy, -o, 0)
            else:
                hx, hy = int(round(w / 2 / CELL)), max(0, int(round(dep / 2 / CELL)))
                cov |= _dilate_rect(lay, hx, hy, 0, o) | _dilate_rect(lay, hx, hy, 0, -o)
        cov &= F.free
    elif how[0] == "arm":
        cov = (ndimage.distance_transform_edt(~cen) * CELL <= how[1]) & F.free
    elif how[0] == "arm_hose":
        near = np.zeros_like(cen)
        for x, y in POU.values():
            near |= np.hypot(F.X - x, F.Y - y) <= how[2]
        cen_h = cen & near
        cov = (ndimage.distance_transform_edt(~cen_h) * CELL <= how[1]) & F.free & near
    else:
        raise ValueError(how)
    return dict(centres=cen, covered=cov)


def coverage(F: Floor, R: dict) -> dict:
    """The table: each zone's free floor and the share of it each cleaner reaches, and the whole floor's."""
    zones = {}
    for z, zd in F.zones.items():
        a = F.area_m2(zd["mask"])
        zones[z] = dict(area_m2=round(a, 2), rect_mm=zd["rect"], why=ZONES_SPEC[z][1],
                        reached={k: round(F.area_m2(zd["mask"] & R[k]["covered"]) / a, 3) if a else None for k in R})
    allz = np.zeros_like(F.free)
    for z, zd in F.zones.items():
        allz |= zd["mask"]
    tot = dict(floor_m2=round(F.area_m2(F.free), 1), zones_m2=round(F.area_m2(allz), 1),
               reached_floor={k: round(F.area_m2(R[k]["covered"]) / F.area_m2(F.free), 3) for k in R},
               reached_zones={k: round(F.area_m2(R[k]["covered"] & allz) / F.area_m2(allz), 3) for k in R})
    # the floor within 300 mm of a machine's or a post's edge: where powder that is kicked or drifts ends up
    from scipy import ndimage
    edge = (ndimage.distance_transform_edt(F.free) * CELL <= 300.0) & F.free & allz
    tot["edge_band_m2"] = round(F.area_m2(edge), 1)
    tot["reached_edge_band"] = {k: round(F.area_m2(R[k]["covered"] & edge) / F.area_m2(edge), 3) for k in R}
    return dict(zones=zones, total=tot)


def pass_minutes(r: dict, area_m2: float) -> float:
    """One pass over area_m2 of reached floor: the fixed time plus lanes at the effective width and speed, times the
    turns-and-edges factor."""
    return r["fixed_min"] + area_m2 / (r["w_eff"] * r["v"]) / 60.0 * r["k"]


def job_table(F: Floor, R: dict) -> dict:
    """Minutes for a pass over each zone (its reached part), and for the nightly sweep (every zone and the aisle, with
    the drive between them at 0.5 m/s), per cleaner."""
    out = {}
    allz = np.zeros_like(F.free)
    for zd in F.zones.values():
        allz |= zd["mask"]
    for k, rr in R.items():
        r = ROBOTS[k]
        zt = {z: round(pass_minutes(r, F.area_m2(zd["mask"] & rr["covered"])), 1) for z, zd in F.zones.items()}
        a = F.area_m2(allz & rr["covered"])
        drive = 2 * (X_LIM[1] - X_LIM[0]) / 1000.0 / 0.5 / 60.0                 # twice the room's length
        night = r["fixed_min"] + a / (r["w_eff"] * r["v"]) / 60.0 * r["k"] + drive
        out[k] = dict(zone_min=zt, night_min=round(night, 1), night_area_m2=round(a, 1))
    return out


# ================================================================================================ the year
TRIGGERS = {"atomize": "atomizer", "sieve": "sieving", "depowder": "midi", "depowder_full": "midi"}
NIGHT_H = 1.0                                  # the nightly sweep starts at 01:00 (assumed: lights out, no person)
SIM = dict(seed=303)


def _year_events(seed: int, fails: bool = True):
    import upkeep as U
    import timelapse as TL
    up = U.Upkeep(seed=seed, fails=fails)
    sim = TL.simulate(upkeep=up)
    return sim, up


def _tested(sim) -> int:
    import timelapse as TL
    return sum(1 for r in sim["alloys"] if r.get("tested", 1e18) <= TL.YEAR_H)


def _people(sim) -> dict:
    """The one person's week, crucible hours included, as notes/upkeep.md counts it (upkeep.weekly_people): the mean
    and the busiest of weeks 9-52 (after the ramp), the floor passes' share, and the hours of work that slid past the
    year's end (weekly_people puts those in week 52; here they are counted apart)."""
    import timelapse as TL
    tot, floor, over = [0.0] * 52, [0.0] * 52, 0.0
    for e in sim["events"]:
        if e["step"] == "atomize" and e["t0"] < TL.YEAR_H:
            tot[min(51, int(e["t0"] // 168))] += TL.PARAMS["atomize_h"]["value"]["person"]
    for r in sim["maint"]:
        if r["person_h"] <= 0:
            continue
        if r["t0"] >= TL.YEAR_H:
            over += r["person_h"]
            continue
        w = min(51, int(r["t0"] // 168))
        tot[w] += r["person_h"]
        if r["task"].startswith("floor"):
            floor[w] += r["person_h"]
    after = range(8, 52)
    return dict(mean_h=round(float(np.mean([tot[w] for w in after])), 1),
                max_h=round(float(max(tot[w] for w in after)), 1),
                floor_mean_h=round(float(np.mean([floor[w] for w in after])), 1),
                weeks_over_40=int(sum(tot[w] > 40.0 + 1e-6 for w in after)),
                slid_past_year_end_h=round(over, 1))


def make_floor_upkeep(mode: str, jobs: dict, night_h: float):
    """An upkeep.Upkeep that also books the floor passes. mode "person": each pass is a person's task on shift, and the
    nightly sweep becomes a morning one at 08:00 on weekdays; mode "units": each pass goes on whichever of the two units
    is free first, the nightly sweep on unit 1 at 01:00. jobs: {zone: hours a pass}."""
    import upkeep as U

    class FloorUpkeep(U.Upkeep):
        def __init__(self, **kw):
            extra = []
            if mode == "person":
                extra.append(U.T("floor_sweep", "floor:all", "floor swept (vacuumed) in every powder zone and the "
                                 "aisle", ("days", 1), "floor", night_h, kind="pm", route=False, source="assumed"))
            else:
                extra.append(U.T("floor_sweep", "unit0", "nightly floor sweep by unit 1", ("days", 1), "arm",
                                 night_h, kind="pm", source="assumed"))
            super().__init__(tasks=U.TASKS + extra, **kw)
            self.floor_log = []

        def _ready(self, t, d):
            if t["key"].startswith("floor_sweep"):
                if mode == "person":
                    day = d
                    while day % 7 >= 5:
                        day += 1
                    return U.at(day, 8.0)
                return U.at(d, NIGHT_H)
            return super()._ready(t, d)

        def used(self, e):
            super().used(e)
            z = TRIGGERS.get(e["step"])
            if z is None or e.get("interrupted"):
                return
            h = jobs[z]
            if mode == "person":
                t = U.T(f"floor_{z}", f"floor:{z}", f"floor pass at the {z}", ("n", 1), "floor", h, kind="pm",
                        source="assumed")
                n = len(self.log)
                self.do(t, e["t1"])
                if len(self.log) > n:
                    r = self.log[-1]
                    self.floor_log.append(dict(zone=z, ready=e["t1"], t0=r["t0"], t1=r["t1"]))
            else:
                best = None
                for u, ul in enumerate(self.ulines):
                    t0 = ul.earliest(e["t1"], h)
                    if best is None or t0 < best[1]:
                        best = (u, t0)
                u, t0 = best
                self.ulines[u].add(t0, t0 + h)
                self.floor_log.append(dict(zone=z, ready=e["t1"], t0=t0, t1=t0 + h, unit=u))

    return FloorUpkeep


def own_cleaner(sim, jobs: dict, night_h: float) -> dict:
    """A cleaner of its own on the year's schedule: every trigger's pass in time order on its own line, waiting for
    a unit's transfer at the same dock to finish and, at the atomizer, for the person's crucible hour; the nightly
    sweep at 01:00 first. -> its log and its figures."""
    import timelapse as TL
    import upkeep as U
    line = TL.Line()
    log = []
    days = int(TL.YEAR_H // 24) + 1
    for d in range(days):
        a = U.at(d, NIGHT_H)
        if a + night_h > TL.YEAR_H:
            break
        line.add(a, a + night_h)
        log.append(dict(zone="night", ready=a, t0=a, t1=a + night_h))
    docks: dict[str, list] = {}
    for t0, t1, u, st in sim["unit_log"]:
        docks.setdefault(st, []).append((t0, t1))
    trig = sorted((e["t1"], TRIGGERS[e["step"]], e["station"]) for e in sim["events"]
                  if e["step"] in TRIGGERS and not e.get("interrupted") and not e.get("maint"))
    waits_dock = waits_person = 0
    for ready, z, st in trig:
        h = jobs[z]
        t = ready
        why = set()
        for _ in range(200):
            t = line.earliest(t, h)
            push = t
            for a, b in docks.get(st, ()):
                if a < t + h and b > t and b > push:
                    push = b
                    why.add("dock")
            if z == "atomizer":
                d = U.day_of(t)
                for a, b in U.crucible_hours(d):
                    a, b = U.at(d, a), U.at(d, b)
                    if a < t + h and b > t and b > push:
                        push = b
                        why.add("person")
            if push > t + 1e-9:
                t = push
                continue
            break
        waits_dock += "dock" in why
        waits_person += "person" in why
        line.add(t, t + h)
        log.append(dict(zone=z, ready=ready, t0=t, t1=t + h))
    return dict(log=log, waited_for_dock=waits_dock, waited_for_person=waits_person)


def _lat(log) -> dict:
    w = np.array([r["t0"] - r["ready"] for r in log if r["zone"] != "night"]) if log else np.array([0.0])
    return dict(median_h=round(float(np.median(w)), 2), p95_h=round(float(np.percentile(w, 95)), 2),
                max_h=round(float(w.max()), 1), n=int(len(w)))


def year(jobs_by: dict) -> dict:
    """The schedules. jobs_by: {cleaner: (zone hours, night hours)} from the reach."""
    import timelapse as TL
    import upkeep as U
    out = {}
    weeks = TL.YEAR_H / (7 * 24)
    base_sim, base_up = _year_events(SIM["seed"])
    base_nf, _ = _year_events(SIM["seed"], fails=False)
    out["baseline"] = dict(tested=_tested(base_sim), tested_planned_only=_tested(base_nf),
                           person=_people(base_sim),
                           unit_transfer_h=[round(sum(b - a for a, b, u, s in base_sim["unit_log"] if u == i), 1)
                                        for i in (0, 1)],
                           what="upkeep.py's year (seed 303, upkeep and failures): no floor cleaning booked")
    trig_n = {z: 0 for z in set(TRIGGERS.values())}
    for e in base_sim["events"]:
        if e["step"] in TRIGGERS and not e.get("interrupted"):
            trig_n[TRIGGERS[e["step"]]] += 1
    out["triggers_per_year"] = trig_n
    for mode, key in (("person", "person"), ("units", "units_pou")):
        jobs, night = jobs_by[key]
        cls = make_floor_upkeep(mode, jobs, night)
        res = {}
        for fails in (True, False):
            up = cls(seed=SIM["seed"], fails=fails)
            sim = TL.simulate(upkeep=up)
            res[fails] = (sim, up)
        sim, up = res[True]
        flog = up.floor_log
        rec = dict(tested=_tested(sim), tested_planned_only=_tested(res[False][0]),
                   latency=_lat(flog), passes=len(flog))
        if mode == "person":
            rec["person"] = _people(sim)
            rec["unbooked"] = len([1 for e in sim["events"] if e["step"] in TRIGGERS]) - len(flog)
        else:
            rec["unit_transfer_h"] = [round(sum(b - a for a, b, u, s in sim["unit_log"] if u == i), 1) for i in (0, 1)]
            rec["floor_unit_h_week"] = round((sum(r["t1"] - r["t0"] for r in flog) +
                                              night * (TL.YEAR_H / 24)) / weeks, 1)
        # seeds 1-8: the spread the failures' draws give
        spread = []
        for s in range(1, 9):
            up_s = cls(seed=s, fails=True)
            spread.append(_tested(TL.simulate(upkeep=up_s)) - _tested(TL.simulate(upkeep=U.Upkeep(seed=s))))
        rec["tested_change_seeds_1_8"] = spread
        out[key] = rec
    for key in ("disc", "pad", "mir", "mir_arm"):
        jobs, night = jobs_by[key]
        oc = own_cleaner(base_sim, jobs, night)
        busy = sum(r["t1"] - r["t0"] for r in oc["log"])
        out[key] = dict(latency=_lat(oc["log"]), busy_h_day=round(busy / (TL.YEAR_H / 24), 2),
                        passes=sum(1 for r in oc["log"] if r["zone"] != "night"),
                        waited_for_dock=oc["waited_for_dock"], waited_for_person=oc["waited_for_person"],
                        tested=out["baseline"]["tested"])
    # energy for the MiR-based cleaners if the vacuum rode on the robot: the 118EXP's 1200 W (its CSA certificate,
    # Nilfisk's "ATEX and safety" brochure) through an inverter at 90 %, and the base's driving (upkeep.UNIT_W: 400 W off
    # the charger, assumed for the whole unit), against the 1.63 kWh pack. The MiR250's top-module supply is 48 V, 10 A
    # (480 W, its spec sheet), so a 1.2 kW vacuum would need its own pack and inverter, which nothing lists for Group E
    for key in ("mir", "mir_arm"):
        busy = out[key]["busy_h_day"]
        kwh = busy * (1.2 / 0.9 + 0.4)
        out[key]["energy_kwh_day"] = round(kwh, 2)
        out[key]["battery_kwh"] = round(U.MIR_KWH["value"], 2)
        out[key]["charge_min_day"] = round(kwh / (0.8 * U.MIR_KWH["value"]) * 52.0, 0)
        out[key]["top_module_w"] = 480.0
    return out


# ================================================================================================ figures
def plot_reach(F: Floor, R: dict, cov: dict, path=None):
    """Six panels, one per cleaner, of the north row (where the atomizer, the sieving cell, the openings, the MIDI and
    the glovebox are): the floor it cleans in its colour, the floor it doesn't in pale grey, the powder zones
    outlined. The DED's and the EOS's zones are on the south side; the table has them."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    import upkeep as U
    path = path or OUT / f"{NAME}_reach.png"
    keys = ["disc", "pad", "mir", "mir_arm", "units_pou", "person"]
    xl, yl = (-9.0, 9.4), (-2.95, 0.75)
    fig, axs = plt.subplots(len(keys), 1, figsize=(15.0, 3.05 * len(keys) + 0.7), dpi=110)
    fig.patch.set_facecolor(U.SURF)
    ext = (X_LIM[0] / 1000, X_LIM[1] / 1000, Y_LIM[0] / 1000, Y_LIM[1] / 1000)
    for ax, k, col in zip(axs.flat, keys, U.SLOTS):
        img = np.ones((F.ny, F.nx, 3))
        img[F.free] = (0.90, 0.90, 0.88)                       # floor it doesn't reach
        c = np.array(matplotlib.colors.to_rgb(col))
        img[R[k]["covered"]] = 0.35 + 0.65 * c                  # reached: the option's colour, lightened
        img[F.occ] = (0.42, 0.44, 0.47)                         # machines, posts, stations
        ax.imshow(img, origin="lower", extent=ext, interpolation="nearest")
        for z, zd in F.zones.items():
            x0, x1, y0, y1 = zd["rect"]
            ax.add_patch(Rectangle((x0 / 1000, y0 / 1000), (x1 - x0) / 1000, (y1 - y0) / 1000, fill=False,
                                   lw=1.1, ec=U.INK, ls=(0, (3, 2)) if z == "aisle" else "-"))
        t = cov["total"]
        z = cov["zones"]
        ax.set_title(f"{ROBOTS[k]['label']}: {t['reached_zones'][k]:.0%} of the powder zones' floor, "
                     f"{t['reached_edge_band'][k]:.0%} of the 300 mm along their machines' edges "
                     f"(atomizer {z['atomizer']['reached'][k]:.0%}, sieving {z['sieving']['reached'][k]:.0%}, "
                     f"MIDI {z['midi']['reached'][k]:.0%})", fontsize=10.5, color=U.INK, loc="left")
        ax.set_xlim(*xl)
        ax.set_ylim(*yl)
        ax.set_aspect("equal")
        ax.tick_params(colors=U.INK2, labelsize=8.5)
        for sp in ax.spines.values():
            sp.set_color("#9b9a94")
        for key, lbl in (("repowder", "rePowder"), ("sieve_cell", "sieving"), ("vlm", "Shuttle 1"),
                         ("vlm2", "Shuttle 2"), ("aconity", "MIDI"), ("glovebox", "glove-\nbox"),
                         ("vacuum station", "vac")):
            x0, x1, y0, y1 = F.rects[key]
            ax.text((x0 + x1) / 2000, max(y0, yl[0] * 1000) / 2000 + min(y1, yl[1] * 1000) / 2000, lbl,
                    ha="center", va="center", fontsize=7.5, color="white")
    axs[-1].set_xlabel("x, m (along the aisle; the aisle is the dashed box, its north half shown)", color=U.INK2)
    for ax in axs:
        ax.set_ylabel("y, m", color=U.INK2)
    fig.suptitle("The north row: floor each cleaner can clean (coloured), floor it can't (pale grey), the powder "
                 "zones (outlined), machines and posts (dark grey)", fontsize=11.5, color=U.INK, x=0.01, ha="left",
                 y=0.997)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    fig.savefig(path, facecolor=U.SURF)
    plt.close(fig)
    return path


def plot_year(y: dict, cov: dict, path=None):
    """Three panels, one row per option in the same order and colour: cleaning hours a week and whose; the wait from
    a trigger to its pass; the share of the zones' edge band it reaches. (Alloys fully tested are the same, 309, for
    every option in this model, so they are a sentence in the notes rather than a panel.)"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import upkeep as U
    path = path or OUT / f"{NAME}_year.png"
    keys = ["person", "units_pou", "disc", "pad", "mir", "mir_arm"]
    labels = [ROBOTS[k]["label"] for k in keys]
    cols = [U.SLOTS[["disc", "pad", "mir", "mir_arm", "units_pou", "person"].index(k)] for k in keys]
    fig, axs = plt.subplots(1, 3, figsize=(16.5, 4.8), dpi=110, sharey=True,
                            gridspec_kw=dict(width_ratios=[1.0, 1.15, 0.9]))
    fig.patch.set_facecolor(U.SURF)
    ypos = np.arange(len(keys))[::-1]
    hw = []
    for k in keys:
        r = y[k]
        if k == "person":
            hw.append(r["person"]["floor_mean_h"])
        elif k == "units_pou":
            hw.append(r["floor_unit_h_week"])
        else:
            hw.append(r["busy_h_day"] * 7)
    ax = axs[0]
    ax.barh(ypos, hw, color=cols, height=0.62)
    for yy, v, k in zip(ypos, hw, keys):
        who = {"person": "the person's", "units_pou": "units 1-2's"}.get(k, "its own")
        ax.text(v + 0.25, yy, f"{v:.1f} h, {who}", va="center", fontsize=9, color=U.INK2)
    ax.set_yticks(ypos, labels)
    ax.set_title("Cleaning time a week, and whose", loc="left", fontsize=11, color=U.INK)
    ax.set_xlim(0, max(hw) * 1.6)
    ax.set_xlabel("hours a week", color=U.INK2)
    ax = axs[1]
    med = [y[k]["latency"]["median_h"] for k in keys]
    p95 = [y[k]["latency"]["p95_h"] for k in keys]
    ax.barh(ypos, p95, color=cols, height=0.62, alpha=0.35)
    ax.barh(ypos, med, color=cols, height=0.62)
    for yy, m, p_ in zip(ypos, med, p95):
        ax.text(p_ + 1.5, yy, f"median {m:.1f} h, 95th pct {p_:.1f} h", va="center", fontsize=9, color=U.INK2)
    ax.set_title("Wait from a spill to its pass", loc="left", fontsize=11, color=U.INK)
    ax.set_xlim(0, max(p95) * 1.75 + 1)
    ax.set_xlabel("hours (solid: median; pale: 95th percentile)", color=U.INK2)
    ax = axs[2]
    e = [cov["total"]["reached_edge_band"][k] * 100 for k in keys]
    ax.barh(ypos, e, color=cols, height=0.62)
    for yy, v in zip(ypos, e):
        ax.text(v + 1.5, yy, f"{v:.0f} %", va="center", fontsize=9, color=U.INK2)
    ax.set_xlim(0, 118)
    ax.set_title("Edge floor reached", loc="left", fontsize=11, color=U.INK)
    ax.set_xlabel("% of the zones' floor within 300 mm of a machine", color=U.INK2)
    for ax in axs:
        U._style(ax)
    fig.tight_layout()
    fig.savefig(path, facecolor=U.SURF)
    plt.close(fig)
    return path


# ================================================================================================ main
def model(write=True, do_year=True) -> dict:
    F = Floor(bay=True)
    R = {k: reach(F, k) for k in ROBOTS}
    cov = coverage(F, R)
    jt = job_table(F, R)
    out = dict(what="Automatic floor cleaning: what each cleaner reaches on setup_lab's floor plan, its pass times, and "
                    "its year on upkeep.py's schedule (floor_cleaning.py; notes/floor_cleaning.md). A model.",
               grid_mm=CELL, floor_mm=dict(x=X_LIM, y=Y_LIM), zone_pad_mm=ZONE_PAD, vacuum_station_mm=VAC_STATION,
               bay=BAY, point_of_use_mm=POU,
               robots={k: {kk: v for kk, v in r.items()} for k, r in ROBOTS.items()},
               coverage=cov, jobs=jt)
    plot_reach(F, R, cov)
    if do_year:
        jobs_by = {k: ({z: v / 60.0 for z, v in jt[k]["zone_min"].items()}, jt[k]["night_min"] / 60.0) for k in jt}
        y = year(jobs_by)
        out["year"] = y
        plot_year(y, cov)
    if write:
        (OUT / f"{NAME}.json").write_text(json.dumps(out, indent=1, default=float))
    return out


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    m = model(do_year=arg != "reach")
    c = m["coverage"]["total"]
    print(json.dumps(dict(floor_m2=c["floor_m2"], zones_m2=c["zones_m2"], reached_zones=c["reached_zones"],
                          reached_edge=c["reached_edge_band"], reached_floor=c["reached_floor"]), indent=1))
    for z, zd in m["coverage"]["zones"].items():
        print(f"{z:10s} {zd['area_m2']:7.1f} m2  " + "  ".join(f"{k} {v:.0%}" for k, v in zd["reached"].items()))
    for k, j in m["jobs"].items():
        print(k, j)
    if "year" in m:
        print(json.dumps(m["year"], indent=1))

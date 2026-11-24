"""The vertical lab scaled to a $200M facility: a render of under two minutes, made to be refined in Higgsfield later.

    xvfb-run -a python3 facility/bake.py                                   # once: the pilot cell's assets (bake.py)
    python3 facility/facility.py plan                                      # shots, counts and budget -> out/*.json
    PREVIEW=1 xvfb-run -a python3 facility/facility.py stills              # one frame per shot -> out/stills/
    VIZ3D_HD=1 VIZ3D_SIZE=1920x1080 VIZ3D_FPS=30 xvfb-run -a python3 facility/facility.py render a   # shots 1-4
    VIZ3D_HD=1 VIZ3D_SIZE=1920x1080 VIZ3D_FPS=30 xvfb-run -a python3 facility/facility.py render b   # shots 5-9
    python3 facility/facility.py join                                      # the cuts, per-shot clips, keyframes

Sterling, PR #318 (2026-11-24): "create a render that shows the above vertical lab, then scaled to a $200M facility,
with many vertical lift modules (each the same height (35' or so?)), many ultrasonic atomizers, several gas atomizers,
all operating and conducting experiments independently and asynchronously. This video would probably get passed to
Higgsfield later for refinement, so look into that and keep it in mind. Probably max 2 minutes for the video."

The film opens on the pilot cell (PR #318's lab, as ``setup_lab.build`` lays it out, its two Shuttles drawn 35 ft
tall like every other one here), pulls back to the whole facility, then goes hall by hall and ends on the whole site at
eight times speed. Every station runs on its own clock: each MiR250 + UR12e unit keeps to its own stretch of a dock
line, docks, works and moves on; a Shuttle presents a tray when its unit comes, and now and then for its bay cameras;
every machine's stack light shows its own state; the gas atomizers glow at their view-ports while they melt and
spray. Nothing here is a schedule of real experiments: the clocks are seeded random draws (``SEED``).

For Higgsfield (README.md, "Higgsfield"): the 3-D is drawn opaque (no see-through parts, no cutaways inside machines),
the clean cut carries no text, every shot is a single continuous camera move, and ``join`` cuts each shot into clips
of at most 10 s with their first and last frames and a prompt for each.
"""
from __future__ import annotations

import json
import math
import os
import pickle
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(HERE))
os.chdir(LAB)
os.environ.setdefault("VIZ3D_PEEL", "off")          # nothing see-through: no depth peeling (scene.render_base)
os.environ.setdefault("VIZ3D_FPS", "24")            # Higgsfield's edit models work at 24 fps (README.md)
os.environ.setdefault("VIZ3D_QUICK_EXIT", "1")

OUT = HERE / "out"
SEED = 20261124
NAME = "facility"
TITLE = "The vertical lab, scaled to a $200M facility"

import layout as LY  # noqa: E402

# ================================================================================================= the shots
# (key, part, seconds, lab speed, label, caption, camera keys [(u, eye, focus)], view angle)
# Positions in mm in the pilot cell's frame (layout.py). Each shot is one continuous move (no cuts inside a shot).
SHOTS = [
    dict(key="s1_pilot", part="a", secs=12.0, speed=1.0, label="1 · the pilot cell",
         caption="Where it starts: PR #318's vertical lab, its rePowder, sieving cell and two Kardex Shuttles (here "
                 "35 ft tall) along one aisle, a MiR250 + UR12e at a Shuttle's opening.",
         cam=[(0.0, (-6600, -5100, 2600), (-3300, -1500, 1200)), (1.0, (2000, -5000, 2500), (2300, -1400, 1500))],
         va=56.0),
    dict(key="s2_reveal", part="a", secs=16.0, speed=1.0, label="2 · scaled up",
         caption="The same way of working, repeated: 34 Shuttles, 33 ultrasonic atomizers, 4 gas atomizers, 41 "
                 "Aconity MIDIs and 28 mobile manipulators, each station on its own clock.",
         cam=[(0.0, (2000, -5000, 2500), (2300, -1400, 1500)), (0.22, (800, -7500, 9500), (7000, 1500, 1500)),
              (0.55, (-8000, -26000, 20000), (20000, 6000, 1000)), (1.0, (-22000, -54000, 45000), (44000, 13000, 0))],
         va=44.0),
    dict(key="s3_vlm_hall", part="a", secs=12.0, speed=1.0, label="3 · the VLM hall",
         caption="32 more Shuttles along the pilot cell's aisle, 16 a side. A tray comes to a Shuttle's opening when "
                 "its MiR250 docks there, and on its own for the bay cameras' inventory pass.",
         cam=[(0.0, (13500, -3900, 2700), (33500, -3500, 2600)), (1.0, (49000, -3900, 2300), (69000, -3500, 2900))],
         va=50.0),
    dict(key="s4_height", part="a", secs=10.0, speed=1.0, label="4 · 35 ft",
         caption="Each Shuttle is 10.7 m (35 ft) tall: Kardex builds the Shuttle 500 from 2.55 m to 30 m on a 100 mm "
                 "grid. The trays above the opening are storage and slow-moving instruments.",
         cam=[(0.0, (46500, -5000, 1000), (41500, -300, 5600)), (1.0, (39500, -4800, 1200), (34500, -300, 6000))],
         va=64.0),
    dict(key="s5_atomize", part="b", secs=12.0, speed=1.0, label="5 · ultrasonic atomization",
         caption="32 AMAZEMET rePowders in two aisles, each with its sieving cell: a run every 2-4 h on each, started "
                 "and unloaded by the units, the crucible still a person's job.",
         cam=[(0.0, (16500, 2400, 9000), (29000, 14000, 500)), (1.0, (40500, 2500, 7600), (52000, 14500, 500))],
         va=50.0),
    dict(key="s6_gas", part="b", secs=12.0, speed=1.0, label="6 · gas atomization",
         caption="Four gas atomizers for the kilogram lots of the alloys worth scaling, sized after PSI's HERMIGA "
                 "100/10 VI (10-25 kg a run): induction melt on the deck, argon atomization in the tower, cyclone beside.",
         cam="orbit_gas", va=50.0),
    dict(key="s7_print", part="b", secs=12.0, speed=1.0, label="7 · the print hall",
         caption="40 Aconity MIDIs print the screening builds; four EOS M 400-4s print the larger parts. Each "
                 "machine's stack light shows its own state: green printing, blue a unit at it, grey waiting.",
         cam=[(0.0, (56500, 2600, 6200), (70000, 13500, 900)), (1.0, (85000, 3200, 5200), (99000, 14500, 900))],
         va=50.0),
    dict(key="s8_test", part="b", secs=10.0, speed=1.0, label="8 · testing",
         caption="Ten wire EDMs cut the bars off the build plates; ten Instron 68FM-100 frames with furnaces pull them "
                 "at room and elevated temperature. Past them, DED machines, Meltio cells, fume hoods and gloveboxes.",
         cam=[(0.0, (18500, 33000, 2700), (34000, 34000, 1600)), (1.0, (56000, 33000, 3000), (72000, 34000, 1600))],
         va=52.0),
    dict(key="s9_site", part="b", secs=16.0, speed=8.0, label="9 · all at once, 8× speed",
         caption="Every station on its own clock, none waiting on another: the facility at eight times speed.",
         cam="orbit_site", va=44.0),
]
PARTS = {"a": [s["key"] for s in SHOTS if s["part"] == "a"], "b": [s["key"] for s in SHOTS if s["part"] == "b"]}
CARD_SECS = 8.0
HANDLE = 12                  # frames rendered before and after every shot (the camera held, the clocks running on),
                             # so an editor or a restyle has room to trim; the cuts themselves leave them out


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def _interp(keys, u):
    """Eye and focus along the keys [(u, eye, focus)]: Catmull-Rom through the points, eased in and out."""
    e = ease(u)
    us = [k[0] for k in keys]
    if len(keys) == 2:
        a, b = keys
        w = e
        return (tuple(np.array(a[1], float) + (np.array(b[1], float) - np.array(a[1], float)) * w),
                tuple(np.array(a[2], float) + (np.array(b[2], float) - np.array(a[2], float)) * w))
    i = max(0, min(len(keys) - 2, int(np.searchsorted(us, e, side="right")) - 1))
    t = (e - us[i]) / max(us[i + 1] - us[i], 1e-9)
    out = []
    for j in (1, 2):
        P = [np.array(k[j], float) for k in keys]
        p0 = P[max(i - 1, 0)]
        p1, p2 = P[i], P[i + 1]
        p3 = P[min(i + 2, len(P) - 1)]
        t2, t3 = t * t, t * t * t
        v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
        out.append(tuple(v))
    return out[0], out[1]


def camera(shot, u):
    """[(eye), (focus), (up)] at u in 0..1 of the shot."""
    cam = shot["cam"]
    if cam == "orbit_gas":
        cx, cy = LY.GAS_AT[1]
        a = math.radians(-128.0 + 72.0 * ease(u))
        r = 13000.0 - 2200.0 * ease(u)
        eye = (cx + r * math.cos(a), cy + r * math.sin(a), 6800.0 - 1900.0 * ease(u))
        foc = (cx + 300.0, cy, 2500.0)
        return [eye, foc, (0, 0, 1)]
    if cam == "orbit_site":
        cx, cy = 42000.0, 13500.0
        a = math.radians(-118.0 + 64.0 * ease(u))
        r = 92000.0 - 8000.0 * ease(u)
        eye = (cx + r * math.cos(a), cy + r * math.sin(a), 60000.0 - 6000.0 * ease(u))
        foc = (cx, cy + 2000.0, 0.0)
        return [eye, foc, (0, 0, 1)]
    eye, foc = _interp(cam, u)
    return [eye, foc, (0, 0, 1)]


def shot_u(f: int, n: int) -> float:
    """The camera's progress at frame f of an n-frame shot; held at 0 and 1 over the handles."""
    return min(max(f / max(n - 1, 1), 0.0), 1.0)


def shot_frames(fps) -> list[tuple[dict, int, float]]:
    """[(shot, frames, film start s)]."""
    out, t = [], 0.0
    for s in SHOTS:
        n = int(round(s["secs"] * fps))
        out.append((s, n, t))
        t += s["secs"]
    return out


def lab_time(shot_start: float, f: int, fps: int, speed: float) -> float:
    """Lab time at frame f of a shot that starts at film second shot_start: the clocks run on through the cuts, the
    last shot faster."""
    return 40.0 + shot_start + speed * f / fps


# ================================================================================================= the clocks
class Clocks:
    """Seeded schedules for every unit, Shuttle and machine; state(t) for any lab time t."""

    def __init__(self, stations, fleets, seed=SEED):
        rng = np.random.default_rng(seed)
        self.rng = rng
        self.stations = stations
        self.by_id = {s["id"]: s for s in stations}
        self.visits: dict[int, list[tuple[float, float, int]]] = {}   # station id -> [(dock start, dock end, unit)]
        self.units = []
        for k, fl in enumerate(fleets):
            sts = [s for s in stations if s["kind"] in fl["kinds"] and s["side"] == fl["side"] and s["yc"] == fl["yc"]
                   and fl["x0"] - 1 <= s["dock_x"] <= fl["x1"] + 1]
            sts.sort(key=lambda s: s["dock_x"])
            if not sts:
                continue
            self.units.append(self._route(k, fl, sts, rng))
        # pilot cell units are added by the film (their own docks)
        self.machine_phase = {s["id"]: float(rng.uniform(0, 1)) for s in stations}
        self.inventory = {}                                          # Shuttle id -> [(t0, t1)] bay-camera passes
        for s in stations:
            if s["kind"] == "shuttle":
                ts, t = [], float(rng.uniform(0, 60))
                while t < 400:
                    d = float(rng.uniform(7, 12))
                    ts.append((t, t + d))
                    t += d + float(rng.uniform(25, 90))
                self.inventory[s["id"]] = ts

    def _route(self, k, fl, sts, rng):
        """A unit's day on its line: dock at a station (work 14-26 s), drive to another (never the same one twice
        running), dock, ..., for 400 s of lab time. -> dict(segments=[(t0, t1, kind, x0, x1, station id)])"""
        t = -float(rng.uniform(0, 30))
        i = int(rng.integers(len(sts)))
        segs = []
        vmax, acc = 1000.0, 300.0
        while t < 420:
            s = sts[i]
            dwell = float(rng.uniform(14, 26))
            segs.append((t, t + dwell, "dock", s["dock_x"], s["dock_x"], s["id"]))
            self.visits.setdefault(s["id"], []).append((t, t + dwell, k))
            t += dwell
            j = i
            while j == i and len(sts) > 1:
                j = int(rng.integers(len(sts)))
            d = abs(sts[j]["dock_x"] - s["dock_x"])
            dur = _ramp_secs(d, vmax, acc) + 0.8
            segs.append((t, t + dur, "drive", s["dock_x"], sts[j]["dock_x"], None))
            t += dur
            i = j
        y = LY.dock_y(fl["yc"], fl["side"])
        return dict(id=k, y=y, heading=LY.heading(fl["side"]), segs=segs, hall=fl["hall"], kinds=fl["kinds"],
                    seed=int(rng.integers(1 << 30)))

    def unit_state(self, u, t):
        """(x, y, heading, phase, kind of the station or None, seconds into the phase, phase length)"""
        for t0, t1, what, x0, x1, sid in u["segs"]:
            if t0 <= t < t1:
                if what == "dock":
                    return x0, u["y"], u["heading"], "dock", sid, t - t0, t1 - t0
                d = t1 - t0 - 0.8
                tt = min(max(t - t0 - 0.4, 0.0), d)
                f = _ramp_frac(tt, abs(x1 - x0), 1000.0, 300.0) if d > 0 else 1.0
                return x0 + (x1 - x0) * f, u["y"], u["heading"], "drive", None, t - t0, t1 - t0
        x = u["segs"][-1][4]
        return x, u["y"], u["heading"], "dock", None, 0.0, 1.0

    def served(self, sid, t, lead=0.0, lag=0.0):
        for a, b, _k in self.visits.get(sid, []):
            if a - lead <= t < b + lag:
                return (a, b)
        return None


def _ramp_secs(d, vmax, acc):
    if d <= 0:
        return 0.0
    da = vmax * vmax / acc
    if d < da:
        return 2 * math.sqrt(d / acc)
    return 2 * vmax / acc + (d - da) / vmax


def _ramp_frac(t, d, vmax, acc):
    """Fraction of distance d covered t s into a trapezoidal move (accel acc, top speed vmax)."""
    if d <= 0:
        return 1.0
    T = _ramp_secs(d, vmax, acc)
    t = min(max(t, 0.0), T)
    da = vmax * vmax / acc
    if d < da:
        vp = math.sqrt(d * acc)
        th = T / 2
        s = 0.5 * acc * t * t if t < th else d - 0.5 * acc * (T - t) ** 2
        return s / d
    ta = vmax / acc
    if t < ta:
        s = 0.5 * acc * t * t
    elif t < T - ta:
        s = 0.5 * acc * ta * ta + vmax * (t - ta)
    else:
        s = d - 0.5 * acc * (T - t) ** 2
    return s / d


# ================================================================================================= the scene
GREEN, BLUE, GREY, AMBER = (0.20, 0.86, 0.36), (0.22, 0.50, 1.00), (0.66, 0.68, 0.70), (1.00, 0.68, 0.10)
MELT, SPRAY, DARK_GLASS = (1.00, 0.45, 0.08), (1.00, 0.86, 0.45), (0.20, 0.22, 0.25)
TRAY_LOADS = ["tray_C", "tray_D", "tray_E", "tray_F", "tray_K", "tray_L", "tray_M", "tray_A"]
FLOOR_C, GROUND_C, WALL_C, CAP_C, LINE_C = (0.80, 0.80, 0.78), (0.47, 0.48, 0.47), (0.86, 0.87, 0.88), \
    (0.36, 0.38, 0.41), (0.95, 0.78, 0.12)
NEAR_M = {"unit": 16000.0, "shuttle35": 30000.0, "pilot": 42000.0, "tray": 14000.0, "gas_atomizer": 40000.0}
NEAR_DEFAULT = 22000.0
# the pilot cell's two units: unit 0 between the two Shuttles' openings (its target posts stand outside that stretch),
# unit 1 docked at the rePowder (setup_lab.DOCK_Y: 298 mm further out than the row, the machine standing proud of it).
# A unit there drives in along the aisle and turns into a dock; a straight run along a dock line would go through the
# AprilTag posts standing beyond each docked MiR (warehouse.target_xy), so unit 1 stays where it is.
PILOT_UNITS = [dict(y=-1932.0, heading=0.0, docks=[(0.0, "shuttle", "p_s1"), (3630.0, "shuttle", "p_s2")]),
               dict(y=-2230.0, heading=0.0, docks=[(-3487.0, "floor", None)])]


def _box(x0, y0, z0, x1, y1, z1):
    import pyvista as pv
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def trim_high(asset, zmax):
    """The asset without the connected pieces of any part that reach above zmax (in place)."""
    import pyvista as pv
    for p in asset.parts:
        if p.mesh.bounds[5] <= zmax:
            continue
        m = p.mesh.connectivity("all")
        keep = []
        for i in np.unique(m["RegionId"]):
            sub = m.threshold([i, i], scalars="RegionId").extract_surface(algorithm="dataset_surface")
            if sub.bounds[5] <= zmax:
                keep.append(sub)
        p.mesh = pv.merge(keep).triangulate() if keep else pv.PolyData()
    asset.parts = [p for p in asset.parts if p.mesh.n_points]
    return asset


ROOF_Z = 15000.0            # the roof's underside (ours): 10.7 m Shuttles plus room for sprinklers, lights and ducts
LIGHT_PITCH = (8000.0, 8000.0)


def building_assets(closed: bool = False):
    """The building (ours): the hall floor, the ground round it, the aisles' edge lines and the bulk gas tanks outside
    the gas hall's west wall, and either walls cut away at 4.5 m with a dark cap and no roof (``closed=False``: an
    architect's cutaway, for the shots from above) or walls up to a roof of steel deck on girders every 12 m, with LED
    high-bay lights (``closed=True``: the shots inside, so no shot looks out into empty sky; README.md, Higgsfield)."""
    import pyvista as pv
    from assets import Asset, Part
    B = LY.BUILDING
    a = Asset("building_closed" if closed else "building")
    a.parts.append(Part(_box(B["x0"], B["y0"], -30, B["x1"], B["y1"], -2), FLOOR_C, 0.05, 0.30))
    g = 260000.0
    cx, cy = (B["x0"] + B["x1"]) / 2, (B["y0"] + B["y1"]) / 2
    ground = pv.Plane(center=(cx, cy, -40), direction=(0, 0, 1), i_size=g, j_size=g, i_resolution=4, j_resolution=4)
    a.parts.append(Part(ground.triangulate(), GROUND_C, 0.0, 0.30))
    t, h = B["wall_t"], (ROOF_Z + 600.0 if closed else B["wall_h"])
    for x0, y0, x1, y1 in ((B["x0"] - t, B["y0"] - t, B["x1"] + t, B["y0"]), (B["x0"] - t, B["y1"], B["x1"] + t, B["y1"] + t),
                           (B["x0"] - t, B["y0"], B["x0"], B["y1"]), (B["x1"], B["y0"], B["x1"] + t, B["y1"])):
        a.parts.append(Part(_box(x0, y0, 0, x1, y1, h - 120), WALL_C, 0.1, 0.30))
        a.parts.append(Part(_box(x0 - 20, y0 - 20, h - 120, x1 + 20, y1 + 20, h), CAP_C, 0.1, 0.25))
        if closed:        # the wall's girts every 2.5 m, as an insulated metal panel wall shows them
            for zz in np.arange(2500.0, h - 500.0, 2500.0):
                ex = 0 if x1 - x0 > y1 - y0 else (60 if x0 < B["x0"] else -60)
                ey = 0 if x1 - x0 <= y1 - y0 else (60 if y0 < B["y0"] else -60)
                a.parts.append(Part(_box(x0 + (ex if ex > 0 else 0), y0 + (ey if ey > 0 else 0), zz - 25,
                                         x1 + (ex if ex < 0 else 0), y1 + (ey if ey < 0 else 0), zz + 25),
                                    (0.78, 0.79, 0.80), 0.1, 0.3))
    if closed:
        a.parts.append(Part(_box(B["x0"] - t, B["y0"] - t, ROOF_Z + 900, B["x1"] + t, B["y1"] + t, ROOF_Z + 1100),
                            (0.80, 0.81, 0.82), 0.05, 0.30))                   # the deck
        for x in np.arange(B["x0"] + 6000.0, B["x1"], 12000.0):              # girders, 900 mm deep, north-south
            a.parts.append(Part(_box(x - 150, B["y0"], ROOF_Z, x + 150, B["y1"], ROOF_Z + 40), (0.42, 0.45, 0.50), 0.3))
            a.parts.append(Part(_box(x - 12, B["y0"], ROOF_Z + 40, x + 12, B["y1"], ROOF_Z + 860), (0.42, 0.45, 0.50), 0.3))
            a.parts.append(Part(_box(x - 150, B["y0"], ROOF_Z + 860, x + 150, B["y1"], ROOF_Z + 900), (0.42, 0.45, 0.50), 0.3))
        lights = []
        for x in np.arange(B["x0"] + 4000.0, B["x1"], LIGHT_PITCH[0]):
            for y in np.arange(B["y0"] + 4000.0, B["y1"], LIGHT_PITCH[1]):
                lights.append(pv.Cylinder(center=(x, y, ROOF_Z - 500), direction=(0, 0, 1), radius=280, height=90,
                                          resolution=24).triangulate())
        a.parts.append(Part(pv.merge(lights), (0.97, 0.97, 0.93), 0.0, 0.95))
        stems = [_box(x - 15, y - 15, ROOF_Z - 460, x + 15, y + 15, ROOF_Z)
                 for x in np.arange(B["x0"] + 4000.0, B["x1"], LIGHT_PITCH[0])
                 for y in np.arange(B["y0"] + 4000.0, B["y1"], LIGHT_PITCH[1])]
        a.parts.append(Part(pv.merge(stems), (0.30, 0.31, 0.33), 0.2))
    # aisle edge lines (yellow floor tape, 100 mm) along each aisle the units work in
    lines = []
    for yc, x0, x1 in ((LY.YC_VLM, 14500.0, LY.VLM_X[-1] + 1600.0),
                       (LY.YC_AT[0], LY.RP_X[0] - 1700.0, LY.EOS_X[-1] + 2300.0),
                       (LY.YC_AT[1], LY.RP_X[0] - 1700.0, LY.EOS_X[-1] + 2300.0),
                       (LY.YC_TEST, LY.TEST_X[0] - 1500.0, LY.TEST_X[-1] + 1500.0)):
        for y in (yc - 1500.0, yc + 1500.0):
            lines.append(_box(x0, y - 50, 0, x1, y + 50, 1.5))
    a.parts.append(Part(pv.merge(lines), LINE_C, 0.0, 0.35))
    # bulk liquid argon and nitrogen: vertical vacuum-insulated tanks on legs, with their finned vaporizers (ours)
    for x, y, gas in LY.TANKS:
        a.parts.append(Part(pv.Cylinder(center=(x, y, 6800), direction=(0, 0, 1), radius=1450, height=11000,
                                        resolution=48).triangulate(), (0.93, 0.94, 0.95), 0.4, 0.25))
        dome = pv.Sphere(radius=1450, center=(x, y, 12300), theta_resolution=48, phi_resolution=16, end_phi=90)
        a.parts.append(Part(dome.scale((1, 1, 0.35), inplace=False).translate((0, 0, 12300 * 0.65), inplace=False)
                            .triangulate(), (0.93, 0.94, 0.95), 0.4, 0.25))
        for dx in (-900, 900):
            for dy in (-900, 900):
                a.parts.append(Part(_box(x + dx - 80, y + dy - 80, 0, x + dx + 80, y + dy + 80, 1400),
                                    (0.55, 0.57, 0.60), 0.3))
        for k in range(6):
            a.parts.append(Part(_box(x + 1900 + k * 220, y - 700, 200, x + 1960 + k * 220, y + 700, 4200),
                                (0.80, 0.82, 0.84), 0.5))
        a.parts.append(Part(_box(x - 2000, y - 2000, -10, x + 3500, y + 2000, 150), (0.66, 0.66, 0.64), 0.05))
    return a


def beacon_asset():
    """A stack light on a short stub, standing on a machine's top (ours, as the finale draws a beacon over each floor
    machine): a 60 mm stub 140 mm tall and a 150 mm lens."""
    import pyvista as pv
    from assets import Asset, Part
    a = Asset("beacon")
    a.parts.append(Part(_box(-60, -60, 0, 60, 60, 15), (0.22, 0.23, 0.25), 0.3))
    a.parts.append(Part(pv.Cylinder(center=(0, 0, 80), direction=(0, 0, 1), radius=30, height=130,
                                    resolution=16).triangulate(), (0.22, 0.23, 0.25), 0.3))
    a.parts.append(Part(pv.Cylinder(center=(0, 0, 220), direction=(0, 0, 1), radius=75, height=150,
                                    resolution=24).triangulate(), GREY, 0.0, 0.9, "beacon"))
    return a


def top_spot(asset) -> tuple[float, float, float]:
    """Where a stack light can stand on a machine: the highest surface near its front-right corner (in the asset's
    frame, front towards -y), searched inwards until some of the machine is under it."""
    pts = np.vstack([p.mesh.points for p in asset.parts if p.mesh.n_points])
    lo, hi = pts.min(0), pts.max(0)
    for f in (0.12, 0.25, 0.4, 0.5):
        x0, x1 = hi[0] - (hi[0] - lo[0]) * (f + 0.15), hi[0] - (hi[0] - lo[0]) * f
        y0, y1 = lo[1] + (hi[1] - lo[1]) * f, lo[1] + (hi[1] - lo[1]) * (f + 0.25)
        m = (pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1)
        if m.sum() > 20:
            sel = pts[m]
            k = int(np.argmax(sel[:, 2]))
            return float(sel[k, 0]), float(sel[k, 1]), float(sel[k, 2])
    return float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2), float(hi[2])


class Film:
    """Everything placed, and set to lab time t every frame."""

    def __init__(self, sc):
        from assets import CACHE, Library, shuttle35, unit_asset, shuttle_dims
        import gas_atomizer as GA
        from scene import T, R
        self.sc = sc
        t0 = time.time()
        ren = sc.pl.renderer
        ren.SetUseDepthPeeling(False)
        self.lib = lib = Library(ren)
        baked = pickle.loads((CACHE / "baked.pkl").read_bytes())
        self.meta = baked["meta"]
        lib.add(trim_high(baked["pilot"], 6000.0), keep={"near": 1.0, "far": 0.22})
        kinds = {s["kind"] for s in LY.stations()} - {"shuttle"}
        for key in kinds:
            lib.add(baked["machines"][key], keep={"near": 1.0, "far": 0.25})
        for tr in TRAY_LOADS:
            if tr in baked["trays"]:
                lib.add(baked["trays"][tr], keep={"near": 0.7, "far": 0.12})
        self.trays = [tr for tr in TRAY_LOADS if tr in baked["trays"]]
        lib.add(shuttle35(), keep={"near": 1.0, "far": 1.0})
        lib.add(unit_asset(keep_arm=float(os.environ.get("FAC_ARM_KEEP", "0.3"))), keep={"near": 1.0, "far": 0.2})
        lib.add(GA.gas_atomizer(), keep={"near": 1.0, "far": 0.5})
        lib.add(building_assets(), lods=("near",))
        lib.add(building_assets(closed=True), lods=("near",))
        lib.add(beacon_asset(), lods=("near",))
        self.spots = {k: top_spot(lib.assets[k]) for k in kinds}
        del baked
        self.D = shuttle_dims()
        # --- placed
        self.open_bldg = lib.place("building")             # walls cut at 4.5 m, no roof: the aerial shots
        self.closed_bldg = lib.place("building_closed")    # full walls, the roof and its lights: the shots inside
        self.closed_bldg.show(False)
        self.pilot = lib.place("pilot")
        self.stations = LY.stations()
        self.clocks = Clocks(self.stations, LY.fleets())
        self.placed = {}            # station id -> Placed
        self.beacons = {}           # station id -> Placed beacon
        self.tray_of = {}           # shuttle station id -> Placed tray load
        rng = np.random.default_rng(SEED + 1)
        # the pilot cell's two Shuttles, as stations of their own (ids "p_s1", "p_s2")
        pil = [dict(kind="shuttle", x=0.0, y=0.0, turn=0.0, id="p_s1"), dict(kind="shuttle", x=3630.0, y=0.0, turn=0.0,
                                                                              id="p_s2")]
        for s in self.stations + pil:
            M = T((s["x"], s["y"], 0.0)) @ R((0, 0, 1), s["turn"])
            asset = "shuttle35" if s["kind"] == "shuttle" else s["kind"]
            self.placed[s["id"]] = lib.place(asset, M, "far")
            if s["kind"] == "shuttle":
                tr = self.trays[int(rng.integers(len(self.trays)))]
                self.tray_of[s["id"]] = lib.place(tr, M @ T((0.0, self.D["y_open"], self.D["z_open"])), "far")
                self.tray_of[s["id"]].show(False)
            else:
                self.beacons[s["id"]] = lib.place("beacon", M @ T(self.spots[s["kind"]]), "near")
        self.pilot_beacons = []         # the pilot cell is drawn as PR #318 has it: no stack lights
        # gas atomizers
        self.gas = [lib.place("gas_atomizer", T((x, y, 0)), "far") for x, y in LY.GAS_AT]
        self.gas_phase = [float(rng.uniform(0, 1)) for _ in self.gas]
        # units: the fleets' and the pilot cell's two
        self.units = [lib.place("unit", np.eye(4), "far") for _ in self.clocks.units]
        self.pilot_units = []
        for k, pu in enumerate(PILOT_UNITS):
            self.pilot_units.append((pu, lib.place("unit", np.eye(4), "far"), float(rng.uniform(0, 30))))
        self.work = WorkPoses()
        print(f"film: built in {time.time() - t0:.0f} s; "
              f"{sum(len(v) for p in [self.pilot] for v in p.actors.values())} pilot actors", flush=True)

    # ----------------------------------------------------------------------------------------- per frame
    def lod(self, p, eye, kind):
        if getattr(self, "locked", False):
            return
        d = float(np.linalg.norm(p.centre() - np.asarray(eye, float)))
        p.set_lod("near" if d < NEAR_M.get(kind, NEAR_DEFAULT) else "far")

    def lock_lod(self, shot):
        """One level of detail for each thing for the whole shot, from the nearest the camera comes to it, so nothing
        changes its mesh mid-shot (Higgsfield's guidance: no pop-ins). Also the building: closed (walls to the roof)
        for the shots inside, cut away for the two from above."""
        closed = shot["key"] not in ("s2_reveal", "s9_site")
        self.closed_bldg.show(closed)
        self.open_bldg.show(not closed)
        self.locked = False
        eyes = np.array([camera(shot, u)[0] for u in np.linspace(0, 1, 33)], float)

        def nearest(pts):
            pts = np.atleast_2d(np.asarray(pts, float))
            return float(np.min(np.linalg.norm(eyes[:, None, :] - pts[None, :, :], axis=2)))

        def setp(p, kind, pts=None):
            d = nearest(p.centre() if pts is None else pts)
            p.set_lod("near" if d < NEAR_M.get(kind, NEAR_DEFAULT) else "far")
        setp(self.pilot, "pilot")
        for s in self.stations + [dict(kind="shuttle", id="p_s1"), dict(kind="shuttle", id="p_s2")]:
            p = self.placed[s["id"]]
            setp(p, "shuttle35" if s["kind"] == "shuttle" else s["kind"])
            if s["kind"] == "shuttle":
                tr = self.tray_of[s["id"]]
                setp(tr, "tray", p.centre())
        for g in self.gas:
            setp(g, "gas_atomizer")
        for u, pl in zip(self.clocks.units, self.units):
            xs = np.linspace(min(sg[3] for sg in u["segs"]), max(sg[3] for sg in u["segs"]), 12)
            setp(pl, "unit", [(x, u["y"], 1000.0) for x in xs])
        for pu, pl, _off in self.pilot_units:
            xs = np.linspace(min(d[0] for d in pu["docks"]), max(d[0] for d in pu["docks"]), 8)
            setp(pl, "unit", [(x, pu["y"], 1000.0) for x in xs])
        self.locked = True

    def set(self, t, eye):
        from scene import T, R
        C = self.clocks
        self.lod(self.pilot, eye, "pilot")
        # Shuttles: a tray out while a unit is docked there (from 5 s before to 2 s after), or for an inventory pass
        for s in self.stations + [dict(kind="shuttle", id="p_s1"), dict(kind="shuttle", id="p_s2")]:
            sid = s["id"]
            p = self.placed[sid]
            self.lod(p, eye, "shuttle35" if s["kind"] == "shuttle" else s["kind"])
            if s["kind"] == "shuttle":
                iv = C.served(sid, t, lead=5.0, lag=2.0) if sid in C.visits else None
                if iv is None:
                    for a, b in C.inventory.get(sid, []):
                        if a <= t < b:
                            iv = (a, b)
                            break
                if iv is None and isinstance(sid, str):
                    iv = self.pilot_present(sid, t)
                self.shuttle_state(sid, p, t, iv, eye)
            else:
                b = self.beacons.get(sid)
                if b is not None:
                    b.colour("beacon", self.machine_colour(sid, t))
            p.update()
        for key, b, ph in self.pilot_beacons:
            u = (t / 150.0 + ph) % 1.0
            b.colour("beacon", GREEN if u < 0.7 else (BLUE if u < 0.82 else GREY))
        for g, ph in zip(self.gas, self.gas_phase):
            self.lod(g, eye, "gas_atomizer")
            self.gas_state(g, (t / 180.0 + ph) % 1.0, t)
            g.update()
        for u, pl in zip(C.units, self.units):
            x, y, hd, phase, sid, tin, tlen = C.unit_state(u, t)
            kind = self.clocks.by_id[sid]["kind"] if sid is not None else None
            self.unit_pose(pl, x, y, hd, phase, kind, tin, tlen, eye, u["seed"])
        for pu, pl, off in self.pilot_units:
            x, phase, kind, tin, tlen = self.pilot_unit_state(pu, t + off)
            self.unit_pose(pl, x, pu["y"], pu["heading"], phase, kind, tin, tlen, eye, 7)

    def pilot_unit_state(self, pu, t):
        """The pilot cell's units: 22 s at each dock in turn, 6-8 s between."""
        docks = pu["docks"]
        cyc = []
        tt = 0.0
        for i, (x, kind, _sid) in enumerate(docks):
            nx = docks[(i + 1) % len(docks)][0]
            dur = _ramp_secs(abs(nx - x), 1000.0, 300.0) + 0.8
            cyc.append((tt, tt + 22.0, "dock", x, x, kind))
            tt += 22.0
            cyc.append((tt, tt + dur, "drive", x, nx, None))
            tt += dur
        tm = t % tt
        for a, b, what, x0, x1, kind in cyc:
            if a <= tm < b:
                if what == "dock":
                    return x0, "dock", kind, tm - a, b - a
                d = b - a - 0.8
                f = _ramp_frac(min(max(tm - a - 0.4, 0.0), d), abs(x1 - x0), 1000.0, 300.0)
                return x0 + (x1 - x0) * f, "drive", None, tm - a, b - a
        return docks[0][0], "dock", docks[0][1], 0.0, 22.0

    def pilot_present(self, sid, t):
        pu = PILOT_UNITS[0]
        off = self.pilot_units[0][2]
        x, phase, kind, tin, tlen = self.pilot_unit_state(pu, t + off)
        xs = 0.0 if sid == "p_s1" else 3630.0
        if phase == "dock" and abs(x - xs) < 1.0:
            return (t - tin, t - tin + tlen)
        # a little before the unit arrives, and after it leaves
        for dt in (2.0, 4.0):
            x2, ph2, _k, tin2, _l = self.pilot_unit_state(pu, t + off + dt)
            if ph2 == "dock" and abs(x2 - xs) < 1.0:
                return (t + dt - tin2, t + dt + 22.0)
        return None

    def shuttle_state(self, sid, p, t, iv, eye):
        from scene import T
        tray = self.tray_of[sid]
        D = self.D
        if iv is None:
            p.pose({"shutter": np.eye(4)})
            p.colour("beacon", GREY)
            tray.show(False)
            return
        a, b = iv
        # 0.5 s shutter up, 1.8 s the tray out, 0.5 s shutter down behind it; the reverse to store it
        def phase(tt):
            sh = ease(tt / 0.5) if tt < 0.5 else (1.0 if tt < 2.3 else 1.0 - ease((tt - 2.3) / 0.5))
            tr = 0.0 if tt < 0.5 else ease((tt - 0.5) / 1.8)
            return sh, tr
        if t - a < (b - a) / 2:
            up, f = phase(t - a)
        else:
            up, f = phase(b - t)
        p.pose({"shutter": T((0, 0, 1000.0 * up))})
        y = D["y_open"] + (1.0 - f) * 1250.0
        Ms = p.M
        tray.M = Ms @ T((0.0, y, D["z_open"]))
        tray.show(f > 0.05)
        self.lod(tray, eye, "tray")
        tray.update()
        p.colour("beacon", GREEN)

    def machine_colour(self, sid, t):
        C = self.clocks
        if C.served(sid, t) is not None:
            return BLUE
        vs = C.visits.get(sid)
        if not vs:
            u = (t / 170.0 + C.machine_phase[sid]) % 1.0
            return GREEN if u < 0.78 else GREY
        # running from the end of the last visit for 70 % of the gap to the next
        prev = [v for v in vs if v[1] <= t]
        nxt = [v for v in vs if v[0] > t]
        if not prev:
            return GREEN if C.machine_phase[sid] < 0.75 else GREY
        e = prev[-1][1]
        n = nxt[0][0] if nxt else e + 120.0
        return GREEN if t < e + 0.7 * (n - e) else GREY

    def gas_state(self, g, u, t):
        flick = 0.85 + 0.15 * math.sin(t * 9.0) * math.sin(t * 4.3)
        if u < 0.15:
            g.colour("beacon", BLUE)
            g.colour("glow_melt", DARK_GLASS, 0.9)
            g.colour("glow_spray", DARK_GLASS, 0.9)
        elif u < 0.55:
            k = (u - 0.15) / 0.40
            g.colour("beacon", GREEN)
            g.colour("glow_melt", tuple(DARK_GLASS[i] + (MELT[i] - DARK_GLASS[i]) * min(1.0, k * 1.6) * flick
                                        for i in range(3)), 1.0)
            g.colour("glow_spray", DARK_GLASS, 0.9)
        elif u < 0.70:
            g.colour("beacon", GREEN)
            g.colour("glow_melt", tuple(c * flick for c in MELT), 1.0)
            g.colour("glow_spray", tuple(c * flick for c in SPRAY), 1.0)
        else:
            g.colour("beacon", GREEN if u < 0.9 else GREY)
            g.colour("glow_melt", DARK_GLASS, 0.9)
            g.colour("glow_spray", DARK_GLASS, 0.9)

    def unit_pose(self, pl, x, y, hd, phase, kind, tin, tlen, eye, seed):
        from scene import T, R
        from assets import unit_local
        pl.M = T((x, y, 0.0)) @ R((0, 0, 1), hd)
        q = self.work.q(kind if phase == "dock" else None, tin, tlen, seed)
        pl.pose(unit_local(q))
        self.lod(pl, eye, "unit")
        pl.colour("band", (0.35, 0.90, 0.45) if phase == "dock" else (0.40, 0.80, 1.00))
        pl.update()


class WorkPoses:
    """The arm's moves at a dock, in the unit's own frame: park -> ready -> three targets over the presented tray (a
    Shuttle) or at the machine's front, a few seconds each -> ready -> park. The targets are solved once (ur_arm.ik)."""

    def __init__(self):
        import animate as A
        import props as P
        import ur_arm
        from scene import T
        self.A, self.ur = A, ur_arm
        self.park = np.radians(A.PARK_DEG)
        self.ready = np.radians((-90.0, -100.0, 110.0, -100.0, -90.0, 0.0))
        base = T((*A.ARM_LOCAL, P.AMR_TOP))
        Bi = np.linalg.inv(base)
        import vlm as V
        y_front = LY.AISLE_HALF - LY.DOCK_OFF                          # 370: a station's front from the dock line
        self.targets = {}
        tray_y = y_front + LY.SHUTTLE_FRONT + V.Y_OPEN - V.TRAY_D / 2 + 230.0
        z_tray = V.Z_OPEN + V.T_FLOOR + 260.0
        sets = {"shuttle": [(dx, tray_y, z_tray) for dx in (-260.0, 0.0, 260.0)],
                "floor": [(dx, y_front - 130.0, 1120.0 + dz) for dx, dz in ((-240.0, 0.0), (0.0, 60.0), (240.0, 0.0))]}
        for kind, pts in sets.items():
            qs = []
            for p in pts:
                try:
                    # over the tray, the gripper points down; at a machine's front, level towards it
                    Tt = A.down(p) if kind == "shuttle" else A.level(p, toward=(0, 1, 0))
                    q = ur_arm.ik(A.ROBOT, Bi @ Tt, self.ready)
                    if q is not None and np.all(np.isfinite(q)):
                        qs.append(np.asarray(q, float))
                except Exception as e:                 # noqa: BLE001
                    print(f"WorkPoses: no IK for {kind} {p}: {e}", flush=True)
            self.targets[kind] = qs or [self.ready]
        print("WorkPoses:", {k: len(v) for k, v in self.targets.items()}, flush=True)

    def q(self, kind, tin, tlen, seed):
        if kind is None:
            return self.park
        tg = self.targets["shuttle" if kind == "shuttle" else "floor"]
        seq = [self.park, self.ready] + [tg[(seed + i) % len(tg)] for i in range(3)] + [self.ready, self.park]
        # park->ready 1.4 s, then the targets share what is left before ready->park (1.4 s)
        n = len(seq) - 1
        mid = max(tlen - 2.8, 0.5)
        times = [0.0, 1.4] + [1.4 + mid * (i + 1) / 4.0 for i in range(3)] + [1.4 + mid, tlen]
        for i in range(n):
            if tin <= times[i + 1]:
                w = (tin - times[i]) / max(times[i + 1] - times[i], 1e-6)
                w = ease(min(1.0, w / 0.75))                  # move in the first 3/4, hold for the rest
                return seq[i] + (seq[i + 1] - seq[i]) * w
        return self.park


# ================================================================================================= commands
def _scene(name, mp4=True):
    import scene
    scene.OUT = OUT                      # this film's files go to facility/out, not the lab's out/
    from scene import Scene
    sc = Scene(name, TITLE, gif=False, mp4=mp4)
    sc.pl.set_background((0.93, 0.94, 0.95))
    return sc


def stills(which=None):
    """One frame at the start, middle and end of each shot (text drawn) -> out/stills/<shot>_<u>.png."""
    import scene
    from PIL import Image
    sc = _scene("facility_stills", mp4=False)
    F = Film(sc)
    fps = scene.FPS
    d = OUT / "stills"
    d.mkdir(parents=True, exist_ok=True)
    for shot, n, t0 in shot_frames(fps):
        if which and shot["key"] not in which and shot["part"] not in which:
            continue
        F.lock_lod(shot)
        for u in (0.0, 0.5, 1.0):
            f = int(round(u * (n - 1)))
            cam = camera(shot, u)
            sc.cam, sc.view_angle = cam, shot["va"]
            sc.label, sc.caption = shot["label"], shot["caption"]
            t1 = time.time()
            F.set(lab_time(t0, f, fps, shot["speed"]), cam[0])
            base = sc.render_base()
            img = sc.overlay(Image.fromarray(base), scene.size_scale(sc.size), [])
            img.convert("RGB").save(d / f"{shot['key']}_{int(u * 100):03d}.png")
            print(f"{shot['key']} u={u}: {time.time() - t1:.2f} s", flush=True)
    sc.pl.close()


def render(part):
    """The shots of one part (``PARTS``), every frame: out/clean/facility_<part>.mp4 (no text) and
    out/hd/facility_<part>.mp4 (with the titles and captions) under VIZ3D_HD=1; their JSON gives each shot's frames."""
    import scene
    sc = _scene(f"{NAME}_{part}")
    F = Film(sc)
    fps = scene.FPS
    t_start = time.time()
    only = os.environ.get("FAC_SHOTS")                     # a comma list of shot keys, to re-render some only
    for shot, n, t0 in shot_frames(fps):
        if shot["part"] != part or (only and shot["key"] not in only.split(",")):
            continue
        F.lock_lod(shot)
        start = sc.n
        sc.label, sc.caption = shot["label"], shot["caption"]
        for f in range(-HANDLE, n + HANDLE):
            cam = camera(shot, shot_u(f, n))
            sc.cam, sc.view_angle = cam, shot["va"]
            F.set(lab_time(t0, f, fps, shot["speed"]), cam[0])
            sc.snap()
            if f % 48 == 0:
                print(f"{shot['key']}: frame {f}/{n} at {time.strftime('%H:%M:%S', time.gmtime())} "
                      f"({(time.time() - t_start) / max(sc.n, 1):.2f} s a frame)", flush=True)
        sc.substeps.append(dict(label=shot["key"], caption=shot["caption"], start_frame=start, end_frame=sc.n - 1,
                                core=[start + HANDLE, sc.n - 1 - HANDLE], handle=HANDLE, secs=shot["secs"]))
    sc.save()


def planview():
    """A top view of the facility (parallel projection, the roof off), the halls named -> out/facility_plan.png."""
    import scene
    from PIL import Image, ImageDraw
    sc = _scene("facility_plan", mp4=False)
    F = Film(sc)
    shot = next(s for s in SHOTS if s["key"] == "s9_site")
    F.lock_lod(shot)
    for p in [F.pilot] + list(F.placed.values()) + list(F.tray_of.values()) + F.gas + F.units:
        p.set_lod("near")
    B = LY.BUILDING
    cx, cy = (B["x0"] + B["x1"]) / 2 - 7000, (B["y0"] + B["y1"]) / 2
    sc.cam = [(cx, cy, 200000.0), (cx, cy, 0.0), (0, 1, 0)]
    F.set(60.0, sc.cam[0])
    sc.pl.camera.SetParallelProjection(True)
    W, H = sc.size
    sc.pl.camera.SetParallelScale(0.5 * max((B["y1"] - B["y0"] + 8000), (B["x1"] - B["x0"] + 26000) * H / W))
    sc._clip_n = 0
    img = Image.fromarray(sc.render_base()).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    s_ = H / 1080

    def to_px(x, y):
        ps = sc.pl.camera.GetParallelScale()
        return (W / 2 + (x - cx) / (2 * ps) * H, H / 2 - (y - cy) / (2 * ps) * H)
    halls = [("pilot cell (PR #318's lab)", 0, -12500), ("VLM hall: 32 Shuttles, 35 ft", 46000, -11800),
             ("atomization: 32 rePowders", 37000, 24600), ("print: 40 MIDIs, 4 EOS M 400-4", 78000, 24600),
             ("gas atomization: 4 plants", 1000, 39500), ("test: Instrons, wire EDMs", 38000, 39700),
             ("DED, Meltio, hoods, gloveboxes", 78000, 39700), ("argon, nitrogen", -21500, 28500)]
    for text, x, y in halls:
        px, py = to_px(x, y)
        f = scene.font(24 * s_, bold=True)
        tw = d.textlength(text, font=f)
        d.rounded_rectangle((px - tw / 2 - 10 * s_, py - 18 * s_, px + tw / 2 + 10 * s_, py + 18 * s_), 8 * s_,
                            fill=(255, 255, 255, 215))
        d.text((px - tw / 2, py - 15 * s_), text, font=f, fill=(25, 30, 38))
    x0, y0 = to_px(B["x0"], B["y0"])
    x1, _ = to_px(B["x0"] + 20000, B["y0"])
    yb = y0 + 40 * s_
    d.line((x0, yb, x1, yb), fill=(25, 30, 38), width=max(2, int(4 * s_)))
    d.text((x0, yb + 8 * s_), "20 m", font=scene.font(22 * s_, bold=True), fill=(25, 30, 38))
    d.text((24 * s_, 20 * s_), f"The facility from above: {LY.BUILDING['x1'] / 1000 - LY.BUILDING['x0'] / 1000:.0f} x "
           f"{(LY.BUILDING['y1'] - LY.BUILDING['y0']) / 1000:.0f} m, roof off", font=scene.font(30 * s_, bold=True),
           fill=(25, 30, 38))
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / "facility_plan.png", optimize=True)
    sc.pl.close()
    print("plan view written", flush=True)


# ================================================================================================= the cuts
CLIP_MAX = 9.0               # s of a shot per Higgsfield clip, so a clip with its two handles stays within 10 s
THREADS = os.environ.get("FFMPEG_THREADS", "4")


def _ff(args, threads=2):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *args]
    if threads:
        cmd[1:1] = []
    subprocess.run(cmd, check=True)


def _parts_meta() -> dict:
    """{shot key: (part MP4 clean, part MP4 captioned, substep)} from the renders' JSON."""
    out = {}
    for part in PARTS:
        j = OUT / "clean" / f"{NAME}_{part}.json"
        if not j.exists():
            continue
        meta = json.loads(j.read_text())
        for st in meta["substeps"]:
            out[st["label"]] = (OUT / "clean" / f"{NAME}_{part}.mp4", OUT / "hd" / f"{NAME}_{part}.mp4", st,
                                meta["fps"], tuple(meta["size"]))
    return out


def _segment_filter(inputs, ranges, size, fps):
    """ffmpeg filter graph concatenating frame ranges [(input index, first, last)]."""
    parts, labels = [], []
    for k, (i, a, b) in enumerate(ranges):
        parts.append(f"[{i}:v]trim=start_frame={a}:end_frame={b + 1},setpts=PTS-STARTPTS,"
                     f"scale={size[0]}:{size[1]},fps={fps},format=yuv420p[v{k}]")
        labels.append(f"[v{k}]")
    return ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(ranges)}:v=1:a=0[out]"


def join():
    """The captioned cut (with the budget card) and the clean cut, both without the handles; the Higgsfield clips
    (each shot in pieces of at most CLIP_MAX s, with their handles), their first and last frames, the shot list with
    a prompt for each, and a contact sheet."""
    from PIL import Image
    pm = _parts_meta()
    keys = [s["key"] for s in SHOTS if s["key"] in pm]
    if not keys:
        raise SystemExit("no renders found under out/clean/")
    fps, size = pm[keys[0]][3], pm[keys[0]][4]
    files_clean = sorted({pm[k][0] for k in keys})
    files_text = sorted({pm[k][1] for k in keys})
    card = OUT / "card.png"
    budget_card(card, size)
    # --- the cuts
    for files, out_name, with_card in ((files_text, f"{NAME}.mp4", True), (files_clean, f"{NAME}_clean.mp4", False)):
        idx = {f: i for i, f in enumerate(files)}
        ranges = []
        for k in keys:
            src = pm[k][0] if files is files_clean else pm[k][1]
            c0, c1 = pm[k][2]["core"]
            ranges.append((idx[src], c0, c1))
        args = []
        for f in files:
            args += ["-i", str(f)]
        if with_card:
            args += ["-loop", "1", "-framerate", str(fps), "-t", str(CARD_SECS), "-i", str(card)]
            ranges.append((len(files), 0, int(CARD_SECS * fps) - 1))
        graph = _segment_filter(range(len(ranges)), ranges, size, fps)
        _ff([*args, "-filter_complex", graph, "-map", "[out]", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
             "-pix_fmt", "yuv420p", "-r", str(fps), "-threads", THREADS, "-movflags", "+faststart",
             str(OUT / out_name)])
        print(f"{out_name}: {(OUT / out_name).stat().st_size / 1e6:.1f} MB", flush=True)
    # --- the Higgsfield clips
    hdir = OUT / "higgsfield"
    hdir.mkdir(parents=True, exist_ok=True)
    clips = []
    for n_shot, k in enumerate(keys, 1):
        src, _t, st, _f, _s = pm[k]
        shot = next(s for s in SHOTS if s["key"] == k)
        c0, c1 = st["core"]
        lo, hi = st["start_frame"], st["end_frame"]
        n_core = c1 - c0 + 1
        pieces = max(1, math.ceil(n_core / (CLIP_MAX * fps)))
        edges = [c0 + round(i * n_core / pieces) for i in range(pieces + 1)]
        for j in range(pieces):
            a, b = edges[j], edges[j + 1] - 1
            fa, fb = max(lo, a - HANDLE), min(hi, b + HANDLE)
            name = f"{n_shot:02d}_{k}" + (f"_{j + 1}" if pieces > 1 else "")
            mp4 = hdir / f"{name}.mp4"
            _ff(["-i", str(src), "-vf", f"trim=start_frame={fa}:end_frame={fb + 1},setpts=PTS-STARTPTS",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), "-an",
                 "-threads", THREADS, "-movflags", "+faststart", str(mp4)])
            for which, fr in (("first", 0), ("last", fb - fa)):
                png = hdir / f"{name}_{which}.png"
                _ff(["-i", str(mp4), "-vf", f"select=eq(n\\,{fr})", "-vframes", "1", str(png)])
            u0 = (a - c0) / max(n_core - 1, 1)
            u1 = (b - c0) / max(n_core - 1, 1)
            clips.append(dict(file=f"higgsfield/{name}.mp4", first=f"higgsfield/{name}_first.png",
                              last=f"higgsfield/{name}_last.png", shot=k, label=shot["label"],
                              seconds=round((fb - fa + 1) / fps, 2), frames=fb - fa + 1, fps=fps,
                              size=list(size), handles=[a - fa, fb - b], camera=camera_words(shot, u0, u1),
                              mb=round(mp4.stat().st_size / 1e6, 1), prompt=prompt(shot)))
            print(f"  {name}: {clips[-1]['seconds']} s, {clips[-1]['mb']} MB", flush=True)
    (hdir / "shotlist.json").write_text(json.dumps(dict(fps=fps, size=list(size), handle_frames=HANDLE, clips=clips,
                                                        negative=NEGATIVE), indent=1) + "\n")
    lines = ["# Higgsfield shot list", "", f"{len(clips)} clips, {size[0]} x {size[1]} at a constant {fps} fps, "
             f"H.264, no audio, no text. Each has {HANDLE} frames of handle at either end (the camera held, the "
             "machines still moving); `_first.png` and `_last.png` are its first and last frames.", "",
             f"**Negative / constraints, for every clip:** {NEGATIVE}", ""]
    for c in clips:
        lines += [f"## {Path(c['file']).stem} ({c['seconds']} s)", "", f"- **Camera:** {c['camera']}",
                  f"- **Prompt:** {c['prompt']}", ""]
    (hdir / "shotlist.md").write_text("\n".join(lines) + "\n")
    # --- a contact sheet: the middle of every shot
    thumbs = []
    for k in keys:
        src, _t, st, _f, _s = pm[k]
        mid = (st["core"][0] + st["core"][1]) // 2
        png = Path("/tmp") / f"fac_mid_{k}.png"
        _ff(["-i", str(src), "-vf", f"select=eq(n\\,{mid})", "-vframes", "1", str(png)])
        thumbs.append(Image.open(png).convert("RGB").resize((640, 360), Image.LANCZOS))
    cols = 3
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (640 * cols, 360 * rows), "white")
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
    sheet.save(OUT / "facility_sheet.png", optimize=True)
    # --- a GIF of the pull-back (shot 2), from the clean cut, for the README
    if "s2_reveal" in pm:
        src, _t, st, _f, _s = pm["s2_reveal"]
        a, b = st["core"]
        pal = Path("/tmp/fac_pal.png")
        vf = f"trim=start_frame={a}:end_frame={b + 1},setpts=PTS-STARTPTS,fps=6,scale=560:-1:flags=lanczos"
        _ff(["-i", str(src), "-vf", f"{vf},palettegen=max_colors=96", str(pal)])
        _ff(["-i", str(src), "-i", str(pal), "-lavfi", f"{vf}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
             str(OUT / "facility_reveal.gif")])
    print("join: done", flush=True)


LEAD = ("Restyle this 3D render as photoreal footage of an automated metal-powder materials lab in a new high-bay "
        "steel-frame industrial hall.")
LOCK = ("Keep every object's position, size, count and motion, and the camera path, framing and timing, exactly as in "
        "the source.")
LIGHT_IN = "Cool-white LED high-bay light, polished light-grey concrete floor with yellow aisle lines."
LIGHT_UP = "Seen from above with the roof cut away like an architect's section; soft overcast daylight."
TAIL = "No people, no text, no new objects."

# what each object in the shot becomes, in generic words (brand names invite fake logos: higgsfield.md)
SUBJECT = {
    "s1_pilot": "The tall light-grey towers are 10.7 m automated vertical-lift storage modules with a lit access opening "
                "at waist height; the small wheeled cart with a six-axis arm is an autonomous mobile robot working at an "
                "opening; the blue cabinet with a small glass chamber is a benchtop ultrasonic powder atomizer and the grey "
                "enclosure beside it a sieving station; the steel platform with stairs behind is a gas atomizer.",
    "s2_reveal": "The camera rises and pulls back from one aisle to show the whole hall: two long rows of tall grey "
                 "vertical-lift storage modules, rows of benchtop powder atomizers with sieving stations, rows of black "
                 "enclosed metal 3D printers, four steel platforms carrying white process vessels (gas atomizers), and "
                 "bulk gas tanks outside the west wall.",
    "s3_vlm_hall": "A long aisle between two rows of tall light-grey vertical-lift storage modules; small autonomous "
                   "mobile robots with six-axis arms dock at their lit openings while trays slide out.",
    "s4_height": "Looking up from the aisle floor at a row of 10.7 m light-grey vertical-lift storage modules under a "
                 "steel roof with LED high-bay lights.",
    "s5_atomize": "From above: rows of blue benchtop ultrasonic powder atomizers, each with a grey sieving station "
                  "beside it, small mobile robots with arms docked at some of them, small stack lights on the machines.",
    "s6_gas": "A pilot-scale gas atomizer: a steel deck with yellow handrails and stairs, a horizontal white vacuum "
              "melting chamber on it with two orange-glowing view-ports, a white atomization tower and a cyclone under "
              "the deck, a rack of green gas cylinders; three more of the same plant behind it.",
    "s7_print": "From above: rows of black enclosed metal powder-bed 3D printers along two aisles, four larger white "
                "industrial metal printers at the end, mobile robots with arms docked at some of them.",
    "s8_test": "An aisle with a row of black universal tensile-testing machines on one side and white wire-EDM machines "
               "on the other, then compact laser deposition machines, robot repair cells and fume hoods; mobile robots "
               "with arms at some of them.",
    "s9_site": "An aerial orbit over the whole factory, every machine running, mobile robots moving quickly along the "
               "aisles (time-lapse).",
}
NEGATIVE = ("people, text, captions, logos, new or extra machines or robots, machines changing size, shape or count, "
            "fire, smoke or sparks (only the orange glow in the gas atomizers' view-ports), camera shake")


def prompt(shot) -> str:
    up = shot["key"] in ("s2_reveal", "s9_site")
    return " ".join([LEAD, SUBJECT.get(shot["key"], ""), LOCK, LIGHT_UP if up else LIGHT_IN, TAIL])


def camera_words(shot, u0, u1) -> str:
    """The camera move over [u0, u1] of a shot, in words."""
    a, b = camera(shot, u0), camera(shot, u1)
    e0, e1 = np.array(a[0]), np.array(b[0])
    d = e1 - e0
    h = np.linalg.norm(d[:2])
    words = []
    if shot["cam"] in ("orbit_gas", "orbit_site"):
        words.append("slow orbit round the subject, keeping it centred")
    else:
        if h > 500:
            words.append(f"dolly {h / 1000:.0f} m")
        if abs(d[2]) > 500:
            words.append(f"{'rising' if d[2] > 0 else 'descending'} {abs(d[2]) / 1000:.0f} m")
    z0, z1 = f"{e0[2] / 1000:.1f}", f"{e1[2] / 1000:.1f}"
    eye = f"eye at {z0} m" if z0 == z1 else f"eye {z0} m to {z1} m"
    words.append(f"{eye} above the floor, {shot['va']:.0f} deg field of view, eased in and out, no cuts")
    if shot["speed"] != 1:
        words.append(f"the machines at {shot['speed']:.0f}x speed")
    return "; ".join(words)


def budget_card(path, size):
    """The closing card: what the $200M buys (plan.py's budget), drawn with PIL."""
    from PIL import Image, ImageDraw
    import scene
    import plan
    b = plan.budget()
    W, H = size
    s = H / 1080
    img = Image.new("RGB", (W, H), (246, 247, 248))
    d = ImageDraw.Draw(img)
    d.text((90 * s, 70 * s), "The vertical lab, scaled: a $200M facility (a plan, not a quote)",
           font=scene.font(46 * s, bold=True), fill=(20, 24, 30))
    y = 170 * s
    for row in b["rows"]:
        d.text((110 * s, y), row["what"], font=scene.font(27 * s), fill=(35, 40, 48))
        d.text((1390 * s, y), f"${row['usd_m']:.1f}M", font=scene.font(27 * s, bold=True), fill=(35, 40, 48))
        y += 44 * s
    d.line((110 * s, y + 8 * s, 1560 * s, y + 8 * s), fill=(120, 125, 130), width=max(1, int(2 * s)))
    d.text((110 * s, y + 22 * s), "Total", font=scene.font(30 * s, bold=True), fill=(20, 24, 30))
    d.text((1390 * s, y + 22 * s), f"${b['total_m']:.0f}M", font=scene.font(30 * s, bold=True), fill=(20, 24, 30))
    d.text((110 * s, H - 120 * s), b["note"], font=scene.font(22 * s), fill=(80, 86, 94))
    img.save(path)


def upload(commit: str):
    """The captioned cut to the lab's channel: unlisted (a draft for Higgsfield), subscribers not notified; recorded in
    out/youtube.json with the file's sha256."""
    import datetime as dt
    import hashlib
    sys.path.insert(0, str(LAB.parent))
    from googleapiclient.http import MediaFileUpload
    from youtube.yt_service import get_youtube_service, with_triggering_link
    import plan
    path = OUT / f"{NAME}.mp4"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rec_path = OUT / "youtube.json"
    rec = json.loads(rec_path.read_text()) if rec_path.exists() else {"videos": []}
    for v in rec["videos"]:
        if v["sha256"] == digest:
            print(f"already up: https://www.youtube.com/watch?v={v['id']}")
            return v["id"]
    c = LY.counts()
    b = plan.budget()
    base = f"https://github.com/vertical-cloud-lab/byu-vcl/blob/{commit}/vertical-lab/facility"
    lines = [
        "PR #318's vertical lab (a Kardex vertical lift module lab with mobile manipulators), then the same way of "
        f"working scaled to a $200M facility: {c['shuttle']} Kardex Shuttles 35 ft tall, {c['repowder']} ultrasonic "
        f"atomizers, {c['gas_atomizer']} gas atomizers, {c['aconity']} Aconity MIDI printers, {c['eos_m400']} EOS M "
        f"400-4s and {c['units']} MiR250 + UR12e mobile manipulators, every station on its own clock.",
        "",
        "A 3-D render (VTK), a draft to be refined in Higgsfield. The layout, the clocks and most unit costs are a plan, "
        f"not a quote: ${b['total_m']:.0f}M with {b['remainder_pct']:.0f} % left for design, permits and contingency.",
        "",
    ]
    t = 0.0
    for sh in SHOTS:
        lines.append(f"{int(t // 60)}:{int(t % 60):02d} {sh['label'].split(' · ', 1)[-1].capitalize()}")
        t += sh["secs"]
    lines.append(f"{int(t // 60)}:{int(t % 60):02d} The budget")
    lines += ["", f"Notes, sources and the budget: {base}/README.md",
              f"Clean per-shot clips for Higgsfield: {base}/out/higgsfield/shotlist.md"]
    desc = with_triggering_link("\n".join(lines))
    title = "The vertical lab, scaled to a $200M facility (3-D render, draft for Higgsfield)"
    yt = get_youtube_service("upload")
    body = {"snippet": {"title": title, "description": desc, "categoryId": "28", "defaultLanguage": "en",
                        "tags": ["vertical cloud lab", "Kardex", "vertical lift module", "lab automation",
                                 "self-driving lab", "metal additive manufacturing", "atomization", "BYU"]},
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False, "embeddable": True}}
    media = MediaFileUpload(str(path), mimetype="video/mp4", chunksize=16 << 20, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=False)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {status.progress():.0%}", flush=True)
    vid = resp["id"]
    rec["videos"].append(dict(id=vid, sha256=digest, bytes=path.stat().st_size, commit=commit, title=title,
                              privacy="unlisted", notified_subscribers=False,
                              uploaded=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    rec_path.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"https://www.youtube.com/watch?v={vid}")
    return vid


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        stills(sys.argv[2:] or None)
    elif cmd == "render":
        render(sys.argv[2])
    elif cmd == "join":
        join()
    elif cmd == "planview":
        planview()
    elif cmd == "upload":
        upload(sys.argv[2])
    else:
        raise SystemExit(f"unknown command {cmd}")

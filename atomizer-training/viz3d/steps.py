"""One 3-D animation per core step of the rePowder SOP (../sop.md), from the CadQuery model.

    xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py              # all of them
    xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py 06_pour      # one (or several)

Each writes out/<name>.gif (800 x 450, 10 fps), out/mp4/<name>.mp4 (1280 x 720, 15 fps, no audio),
out/<name>_still.png (1280 x 720) and out/<name>.json (frame range of every sub-step in the MP4).
Numbers in captions and readouts are the ones used in training (see ../sop.md); illustrative,
not a recipe. Motion is along real assembly paths; heat is shown as colour, not physics.
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pyvista as pv

import model as M
from scene import FPS, MELT, R, S, Scene, T, ease, lighter, load_machine, mix, set_cut, temp_color, window

FURNACE_CUT = ("crucible", "holder", "nozzle", "furnace", "side_ins", "top_ins", "bottom_ins", "coil", "hood", "tc")
FURNACE_FIXED = tuple(g for g in FURNACE_CUT if g not in ("crucible", "holder", "nozzle"))
CHAMBER_CUT = ("chamber", "door", "bowl", "splash", "container", "flange_clamp", "flange_clamp_b")
STACK = ("plate", "sonotrode", "booster", "transducer", "cover")
UTILITY_NAMES = ("argon_cylinder", "argon_regulator", "argon_gauges", "vacuum_pump", "pump_sight_glass",
                 "heat_exchanger", "hx_grille", "hx_display", "air_frl")

CAM = {
    "machine": [(-2350, -3500, 2150), (180, 320, 820), (0, 0, 1)],
    "machine_near": [(-1650, -2500, 1750), (60, 100, 900), (0, 0, 1)],
    "furnace_top": [(-360, -900, 1800), (0, 0, 1335), (0, 0, 1)],
    "furnace_sec": [(-330, -820, 1430), (5, 0, 1262), (0, 0, 1)],
    "column": [(-820, -2750, 1120), (70, 0, 860), (0, 0, 1)],
    "pour": [(-620, -1720, 1200), (10, 0, 1030), (0, 0, 1)],
    "chamber": [(-900, -2200, 1000), (110, 0, 760), (0, 0, 1)],
    "stream": [(-380, -1050, 1080), (5, 0, 1030), (0, 0, 1)],
    "wash": [(-640, -2050, 1280), (70, 0, 1000), (0, 0, 1)],
    "container": [(-750, -2050, 950), (220, -120, 340), (0, 0, 1)],
    "door_out": [(-1750, -700, 1200), (-160, -40, 930), (0, 0, 1)],
    "nut": [(330, -880, 930), (-20, 0, 1105), (0, 0, 1)],          # from the front right: the open door is to the left
    "left_high": [(-1450, -320, 1700), (110, 0, 720), (0, 0, 1)],   # from the left, past the open door's free edge
    "bench": [(-560, -1250, 1650), (0, -170, 1330), (0, 0, 1)],
    "outside": [(-1500, -2600, 1650), (60, 100, 950), (0, 0, 1)],
    "section_fr": [(300, -980, 1330), (-15, 0, 1225), (0, 0, 1)],  # the cut furnace and the nut under the deck at once
}

STREAM_TOP = M.NOZZLE_EXIT_Z
BENCH = np.array([0.0, -330.0, 140.0])         # crucible + holder assembled in front of the furnace, as if in the hands
OVER = 270.0                                    # height above its seat at which the crucible is carried over the furnace
NOZZLE_OUT = np.array([-70.0, -60.0, 30.0])    # nozzle held up beside the holder for the light check (from its seat)


# --------------------------------------------------------------------------------- helpers
# Per-frame effects were written for 15 fps. These keep them the same per second at any VIZ3D_FPS (identical at 15).
PER_FRAME = 15 / FPS      # exactly 1.0 at 15 fps


def per_frame(n):
    """A count emitted every frame at 15 fps, scaled to the frame rate."""
    return int(round(n * PER_FRAME))


def tick(sc):
    """The frame number at 15 fps: the plate's exaggerated vibration alternates on it, so it flickers at the same rate."""
    return sc.n * 15 // FPS


def hood(sc, deg):
    sc.gmat["hood"] = R((0, 1, 0), -deg, M.HINGE)


def door_mat(deg):
    """The door turns about its front-edge hinge; positive opens it outwards, towards the operator."""
    return R((0, 0, 1), deg, (M.DOOR_HINGE[0], M.DOOR_HINGE[1], 0))


def door(sc, deg):
    sc.gmat["door"] = door_mat(deg)


def on_door(p, deg=100):
    """World position of a point that rides on the door, with the door open `deg`."""
    return (door_mat(deg) @ np.append(np.asarray(p, float), 1.0))[:3]


def clamp(sc, k, f):
    """f = 1 closed, 0 open (the swing bolt and its star knob swung clear of the door)."""
    sc.gmat[f"clamp{k}"] = R(M.CLAMP_AXES[k], M.CLAMP_SWING[k] * (1 - f), M.CLAMP_PTS[k])


def lever(sc, f):
    """The sealing-rod lever: f = 0 down on the rod adapter, 1 swung up clear of the furnace opening."""
    sc.gmat["arm"] = R(M.LEVER_AXIS, M.ARM_RAISED * f, M.PIVOT)


def rod_lift(sc, mm):
    """The post's piston lifts the lever and the rod together (sealing rod UP is +12 mm)."""
    sc.gmat["arm_base"] = T((0, 0, mm))


def flange_clamp(sc, f):
    """f = 1 closed round the joint, 0 open: the two halves 40 mm apart, front and back."""
    sc.gmat["flange_clamp"] = T((0, -40 * (1 - f), 0))
    sc.gmat["flange_clamp_b"] = T((0, 40 * (1 - f), 0))


def path(u, pts):
    """Piecewise-linear path through pts, eased per leg; u from 0 to 1 spread evenly over the legs."""
    pts = [np.asarray(p, float) for p in pts]
    n = len(pts) - 1
    k = min(int(u * n), n - 1)
    return pts[k] + (pts[k + 1] - pts[k]) * ease(u * n - k)


def linear(e, t0, t1):
    """Like window(), but linear in time: undoes the step's easing, for steady motions such as screwing."""
    u = 0.5 - math.sin(math.asin(max(-1.0, min(1.0, 1 - 2 * e))) / 3)
    return min(1.0, max(0.0, (u - t0) / (t1 - t0)))


def cut_in(sc, u, groups=None):
    """Open the deferred cutaway over the first part of a sub-step (u from 0 to 1)."""
    set_cut(sc, window(u, 0.0, 0.35), groups)


def slug_xy(k):
    a = math.radians(M.SLUG_ANGLES[k])
    return M.SLUG_R * math.cos(a), M.SLUG_R * math.sin(a)


def heat(sc, temp, coil_on):
    """Colour the charge by temperature, and light the coil while the generator runs."""
    c = temp_color(temp)
    for k in range(4):
        for n in (f"slug{k}",):
            if n in sc.actors:
                sc.color[n] = c
                sc.ambient[n] = 0.18 + 0.55 * max(0.0, min(1.0, (temp - 450) / 400))
    for n in ("coil", "coil#cut", "w:coil"):
        if n in sc.actors:
            sc.color[n] = mix(M.COPPER, (1.0, 0.62, 0.30), coil_on)
            sc.ambient[n] = 0.18 + 0.45 * coil_on


def gauges(sc, **kv):
    fmt = {"furnace": ("Furnace", "{:+.0f} mbar"), "chamber": ("Chamber", "{:+.0f} mbar"),
           "o2": ("O₂", "{:.0f} ppm"), "t": ("T", "{:.0f} °C"), "set": ("Setpoint", "{:.0f} °C"),
           "us": ("US", "{}"), "amp": ("Amplitude", "{:.0f} %"), "status": ("", "{}"), "torque": ("Torque", "{}"),
           "scan": ("Scan", "{}"), "hold": ("Hold", "{}"), "flow": ("Flow", "{}"), "rod": ("Rod", "{}")}
    sc.gauges = [(fmt[k][0], fmt[k][1].format(v)) for k, v in kv.items() if v is not None]


class Pool:
    """Melt pool in the crucible, from pre-built meshes at a series of levels."""

    def __init__(self, sc, half=True, level=-30):
        self.sc, self.half = sc, half
        v = M.variant_meshes()
        self.levels = v["pool_levels"]
        self.meshes = v["pool_half"] if half else [(m, None) for m in v["pool"]]
        body, cut = self.meshes[0]
        sc.add("pool", body, MELT, "crucible", ambient=0.75, diffuse=0.45, specular=0.5)
        if half:
            sc.add("pool#cut", cut, lighter(MELT, 0.3), "crucible", ambient=0.85, diffuse=0.3, specular=0.0,
                   smooth_shading=False)
        self.set(level)

    def set(self, level, color=MELT):
        on = level > self.levels[0] - 0.5
        i = int(np.argmin(np.abs(self.levels - level)))
        body, cut = self.meshes[i]
        self.sc.set_mesh("pool", body)
        self.sc.alpha["pool"] = 1.0 if on else 0.0
        self.sc.color["pool"] = color
        if self.half:
            self.sc.set_mesh("pool#cut", cut)
            self.sc.alpha["pool#cut"] = 1.0 if on else 0.0
            self.sc.color["pool#cut"] = lighter(color, 0.3)


class Powder:
    def __init__(self, sc, half=True, level=0):
        self.sc, self.half = sc, half
        v = M.variant_meshes()
        self.levels = v["powder_levels"]
        self.meshes = v["powder_half"] if half else [(m, None) for m in v["powder"]]
        col = (0.62, 0.63, 0.66)
        sc.add("powder", self.meshes[0][0], col, "container", specular=0.05, ambient=0.3)
        if half:
            sc.add("powder#cut", self.meshes[0][1], lighter(col, 0.25), "container", smooth_shading=False,
                   ambient=0.6, specular=0.0)
        self.set(level)

    def set(self, level):
        on = level >= self.levels[0]
        i = int(np.argmin(np.abs(self.levels - level)))
        body, cut = self.meshes[i]
        self.sc.set_mesh("powder", body)
        self.sc.alpha["powder"] = 1.0 if on else 0.0
        if self.half:
            self.sc.set_mesh("powder#cut", cut)
            self.sc.alpha["powder#cut"] = 1.0 if on else 0.0


def add_stream(sc, radius=1.4):
    h = STREAM_TOP - M.IMPACT[2]
    cyl = pv.Cylinder(center=(0, 0, M.IMPACT[2] + h / 2), direction=(0, 0, 1), radius=radius, height=h,
                      resolution=16)
    sc.add("stream", cyl, MELT, "stream", ambient=0.85, diffuse=0.4, shown=False)


def stream(sc, on, thick=1.0, frac=1.0):
    """frac < 1: only the leading part of the stream exists yet (it is still falling)."""
    sc.alpha["stream"] = 1.0 if on > 0.02 else 0.0
    top = STREAM_TOP
    sc.gmat["stream"] = S((thick, thick, max(frac, 0.01)), (0, 0, top))


class Particles:
    """Droplets / powder as points rendered as spheres; a tiny ballistic model in slow motion."""

    def __init__(self, sc, name, color, size=6.0, slowmo=0.22, seed=1, free=False):
        self.sc, self.name, self.slowmo, self.free = sc, name, slowmo, free
        self.rng = np.random.default_rng(seed)
        self.p = np.zeros((0, 3))
        self.v = np.zeros((0, 3))
        self.landed = 0
        self.poly = pv.PolyData(np.array([[0.0, 0.0, -500.0]]))
        sc.add(name, self.poly, color, "static", render_points_as_spheres=True, point_size=size, ambient=0.4,
               smooth_shading=False)

    def emit_spray(self, n, spread=1.0):
        if n <= 0:
            return
        r = self.rng
        sp = r.uniform(600, 1900, n) * spread
        d = (M.STACK_DIR[None, :] * r.uniform(0.35, 1.0, n)[:, None]
             + M.PLATE_UP[None, :] * r.uniform(-0.55, 0.9, n)[:, None]
             + np.array([0, 1.0, 0])[None, :] * r.uniform(0.05, 1.0, n)[:, None])   # back half only
        d /= np.linalg.norm(d, axis=1)[:, None]
        p = M.IMPACT[None, :] + r.normal(0, 2.5, (n, 3))
        p[:, 1] = np.abs(p[:, 1]) + 1.0
        self.p = np.vstack([self.p, p])
        self.v = np.vstack([self.v, d * sp[:, None]])

    def emit_drops(self, n, pos, vel):
        if n <= 0:
            return
        self.p = np.vstack([self.p, np.repeat(np.asarray(pos, float)[None, :], n, 0)])
        self.v = np.vstack([self.v, np.asarray(vel, float)[None, :] + self.rng.normal(0, 60, (n, 3))])

    def emit_settle(self, n):
        """Powder lying in the chamber being brushed down: start on the chamber floor, slide to the chute."""
        if n <= 0:
            return
        r = self.rng
        x = r.uniform(-60, 300, n)
        p = np.column_stack([x, r.uniform(2, M.CH_Y[1] - 20, n), np.maximum(M.CH_BOTTOM + 8, M.SLOPE_C + 10 - x)])
        self.p = np.vstack([self.p, p])
        self.v = np.vstack([self.v, np.zeros((n, 3))])

    def step(self, dt=None):
        if len(self.p):
            h = (dt or 1 / FPS) * self.slowmo
            self.v[:, 2] -= 9810 * h
            self.v *= (1 - 1.8 * h)
            self.p += self.v * h
            if self.free:                 # outside the chamber: just fall, and go once well below
                keep = self.p[:, 2] > 300
                self.p, self.v = self.p[keep], self.v[keep]
                pts = self.p if len(self.p) else np.array([[0.0, 0.0, -500.0]])
                self.sc.set_mesh(self.name, pv.PolyData(pts.copy()))
                self.sc.alpha[self.name] = 1.0 if len(self.p) else 0.0
                return
            x0, x1 = M.CH_X[0] + 6, M.CH_RIGHT - 6
            y0, y1 = 1.0, M.CH_Y[1] - 6
            fl = np.maximum(M.CH_BOTTOM + 8, M.SLOPE_C + 8 - self.p[:, 0])     # the sloped underside
            inside = self.p[:, 2] > fl - 2
            for ax, lo, hi in ((0, x0, x1), (1, y0, y1)):
                hit = inside & ((self.p[:, ax] < lo) | (self.p[:, ax] > hi))
                self.p[hit, ax] = np.clip(self.p[hit, ax], lo, hi)
                self.v[hit, ax] *= -0.15
            low = self.p[:, 2] <= fl
            if low.any():   # on the sloped underside: slide down to the outlet and drop
                tgt = np.array([M.CHUTE_X, 0.0, M.CONT_Z[1] - 45])
                dvec = tgt[None, :] - self.p[low]
                dist = np.linalg.norm(dvec, axis=1)[:, None] + 1e-6
                self.v[low] = dvec / dist * 900
            gone = self.p[:, 2] < M.CONT_Z[1] - 20
            self.landed += int(gone.sum())
            self.p, self.v = self.p[~gone], self.v[~gone]
        pts = self.p if len(self.p) else np.array([[0.0, 0.0, -500.0]])
        self.sc.set_mesh(self.name, pv.PolyData(pts.copy()))
        self.sc.alpha[self.name] = 1.0 if len(self.p) else 0.0


def gas_meshes(half):
    fur = pv.Cylinder(center=(0, 0, 1251), direction=(0, 0, 1), radius=128, height=186, resolution=72).merge(
        pv.Cylinder(center=(0, 0, 1412), direction=(0, 0, 1), radius=112, height=130, resolution=6))
    ch = M.tess(M.chamber_solid(M.CH_WALL + 1.0), 1.0).triangulate()
    ch = ch.merge(pv.Cylinder(center=(M.CHUTE_X, 0, (M.CONT_Z[0] + M.CH_BOTTOM) / 2), direction=(0, 0, 1),
                              radius=M.CONT_R - 6, height=M.CH_BOTTOM - M.CONT_Z[0] - 8, resolution=48).triangulate())
    if half:
        fur = fur.clip(normal=(0, -1, 0), origin=(0, 0.5, 0))
        ch = ch.clip(normal=(0, -1, 0), origin=(0, 0.5, 0))
    return fur, ch


ARGON = (0.45, 0.72, 1.0)


def add_gas(sc, half=True, furnace=1.0, chamber=1.0):
    f, c = gas_meshes(half)
    sc.add("gas_furnace", f, ARGON, "static", opacity=0.30, smooth_shading=False, specular=0.0, ambient=0.6)
    sc.add("gas_chamber", c, ARGON, "static", opacity=0.22, smooth_shading=False, specular=0.0, ambient=0.6)
    sc.alpha["gas_furnace"], sc.alpha["gas_chamber"] = furnace, chamber


def set_gas(sc, furnace=None, chamber=None):
    if furnace is not None:
        sc.alpha["gas_furnace"] = furnace
    if chamber is not None:
        sc.alpha["gas_chamber"] = chamber


class Flow:
    """Dots moving along a utility line, to show what is flowing where."""

    def __init__(self, sc, route, color, n=14, speed=0.010, size=9):
        self.sc, self.name = sc, "flow_" + route
        pts = np.array(M.pipe_routes()[route]["pts"], float)
        self.line = pv.Spline(pts, 400).points
        self.n, self.speed, self.phase, self.on = n, speed, 0.0, 0.0
        sc.add(self.name, pv.PolyData(self.line[:1].copy()), color, "pipes", render_points_as_spheres=True,
               point_size=size, ambient=0.7, shown=False)

    def step(self):
        self.phase = (self.phase + self.speed * PER_FRAME) % (1.0 / self.n)
        s = (np.arange(self.n) / self.n + self.phase) % 1.0
        idx = (s * (len(self.line) - 1)).astype(int)
        self.sc.set_mesh(self.name, pv.PolyData(self.line[idx].copy()))
        self.sc.alpha[self.name] = self.on


def seq(*fs):
    def f(u):
        for g in fs:
            g(u)
    return f


def at(f, t0, t1=1.0):
    return lambda u: f(window(u, t0, t1))


def lab(text, xyz, fx, fy):
    return (text, tuple(float(v) for v in xyz), (fx, fy))


# ---------------------------------------------------------------------------- 03 furnace load
def anim_03_furnace_load():
    sc = Scene("03_furnace_load", "2a · Furnace prep and loading")
    # the cutaway waits until something goes inside; the chamber is cut too, to show the nut under its top plate.
    # The ultrasonic stack is not in the door yet: the furnace is loaded first, through the open chamber (T1 46:33).
    load_machine(sc, cut=FURNACE_CUT + ("chamber",), hide=UTILITY_NAMES, pipes=False, defer=True)
    for g in STACK:
        sc.show(sc.members(g), 0.0)
    hood(sc, 0)
    lift = {"side_ins": 300, "top_ins": 330, "bottom_ins": 360, "tc": 140, "rod": 260, "seal": -94}
    for g, dz in lift.items():
        sc.show(sc.members(g), 0.0)
        sc.gmat[g] = T((0, 0, dz))
    sc.show(sc.members("crucible") + sc.members("holder") + sc.members("nozzle"), 0.0)
    sc.gmat["crucible"] = T(BENCH)
    sc.gmat["holder"] = T((0, 0, -70))
    sc.gmat["nut"] = T((0, 0, -94))      # below its seat; the last 10 mm are 5 turns of a 2 mm thread
    sc.show(sc.members("nut"), 0.0)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    rod_lift(sc, 12)                      # the piston is up: the strip-down started with "sealing rod up" (T1 36:24)
    sc.gmat["rod"] = T((0, 0, lift["rod"] - 12))
    sc.cam = CAM["machine_near"]
    gauges(sc, t=24, status="furnace cold, power on")

    def open_lid(u):
        hood(sc, 110 * window(u, 0.0, 0.55))
        lever(sc, window(u, 0.5, 1.0))
    sc.step("2a.1", "Start cold. Open the furnace lid (it hinges up to the left) and swing the sealing-rod lever up, clear "
            "of the opening. For a rebuild everything comes out: thermocouple, sealing rod, insulation, crucible.", 4.5,
            open_lid, hold=1.2, cam_to=CAM["furnace_top"],
            labels=[lab("furnace lid (bell)", M.HINGE + np.array([-90, 0, 200]), 0.06, 0.20),
                    lab("sealing-rod lever,\nswung up", M.PIVOT + np.array([12, 0, 70]), 0.72, 0.22)])

    turns = 4.0                           # the holder threads into the crucible over its last 8 mm

    def nozzle_in(u):
        sc.show(sc.members("crucible") + sc.members("holder") + sc.members("nozzle"), 1.0 if u > 0.05 else 0.0)
        rise = window(u, 0.1, 0.3)
        screw = linear(u, 0.3, 0.97)         # about 1.5 turns a second, 2 mm a turn
        sc.gmat["holder"] = T((0, 0, -70 + 62 * rise + 8 * screw)) @ R((0, 0, 1), 360 * turns * screw)
    sc.step("2a.2", "On the bench: nozzle into its holder, white side up (Ø0.5 mm standard, Ø0.7 for Al alloys), then "
            "screw the holder into the crucible by hand: several turns, and only just tight.", 5.5, nozzle_in,
            hold=1.4, cam_to=CAM["bench"],
            labels=[lab("graphite crucible", BENCH + np.array([-30, -20, M.Z_CR + 50]), 0.06, 0.25),
                    lab("nozzle holder, nozzle\nwhite side up", BENCH + np.array([0, -8, M.CRUCIBLE_BASE - 20]),
                        0.06, 0.60)])

    def crucible_in(u):
        set_cut(sc, window(u, 0.0, 0.15), FURNACE_FIXED)
        sc.show(sc.members("bottom_ins"), 1.0 if u > 0.02 else 0.0)
        sc.gmat["bottom_ins"] = T((0, 0, 360 * (1 - window(u, 0.05, 0.35))))
        w = window(u, 0.4, 1.0)
        sc.gmat["crucible"] = T(path(w, [BENCH, (BENCH[0], BENCH[1], OVER), (0, 0, OVER), (0, 0, 0)]))
        set_cut(sc, window(u, 0.75, 0.9), ("crucible", "holder", "nozzle"))     # straight down: nothing turns
    sc.step("2a.3", "Graphite seal and bottom insulation in first. Then lift the crucible over and lower it straight down "
            "into the coil, its shank through the floor. Handle it gently: graphite is brittle.", 6.5, crucible_in,
            hold=1.2, cam_to=CAM["furnace_top"],
            labels=[lab("bottom insulation", (40, 0, M.CRUCIBLE_BASE - 12), 0.70, 0.62),
                    lab("holder shank, through\nthe floor into the chamber", (8, 0, M.SHANK_Z0 + 6), 0.70, 0.80)])

    def nut_on(u):
        for c in range(3):
            clamp(sc, c, 1 - window(u, 0.02 * c, 0.02 * c + 0.08))
        door(sc, 100 * window(u, 0.1, 0.28))
        set_cut(sc, window(u, 0.18, 0.3), ("chamber",))
        sc.show(sc.members("nut") + sc.members("seal"), 1.0 if u > 0.2 else 0.0)
        rise = window(u, 0.22, 0.36)
        screw = linear(u, 0.36, 0.97)        # 5 turns at under a turn a second
        sc.gmat["seal"] = T((0, 0, -94 * (1 - window(u, 0.2, 0.32))))
        sc.gmat["nut"] = T((0, 0, -94 + 84 * rise + 10 * screw)) @ R((0, 0, 1), -360 * 5 * screw)
        gauges(sc, t=24, status="nut snug, not tight" if u > 0.95 else "threading the nut on (5 turns)")
    sc.step("2a.4", "Swing the three bolts back and open the chamber's left door. Through it, the lower seal, then thread the thin graphite nut onto the "
            "shank from below while the crucible is held still at the top, its thermocouple hole turned to the back "
            "right. A second person at the top helps; alone, keep a hand on the crucible. Snug, not tight: graphite "
            "cracks if forced, and a loose nut leaks.", 9.0, nut_on, hold=1.6, cam_to=CAM["nut"],
            labels=[lab("graphite nut: thin,\na few threads", (0, -28, 1116), 0.70, 0.62),
                    lab("hold the crucible\nhere, at the top", (0, -40, M.RIM - 10), 0.06, 0.22),
                    lab("left door open:\nthe access opening", on_door((M.CH_X[0] - M.DOOR_T, 40, 1000)), 0.06, 0.62)])

    def insulation_in(u):
        gauges(sc, t=24, status="furnace cold, power on; chamber door stays open")
        a, b = window(u, 0.0, 0.55), window(u, 0.45, 1.0)
        sc.show(sc.members("side_ins"), 1.0 if u > 0.01 else 0.0)
        sc.gmat["side_ins"] = T((0, 0, 300 * (1 - a)))
        sc.show(sc.members("top_ins"), 1.0 if u > 0.45 else 0.0)
        sc.gmat["top_ins"] = T((0, 0, 330 * (1 - b)))
    sc.step("2a.5", "Side insulation round the crucible, its hole lined up with the thermocouple port at the back right, "
            "then the top insulation (filling cone). Silica-alumina: dusty and fragile.", 4.0, insulation_in, hold=1.2,
            cam_to=CAM["furnace_top"],
            labels=[lab("side insulation", (50, 0, M.Z_CR + 40), 0.70, 0.45),
                    lab("top insulation", (75, 0, M.BODY_TOP - 18), 0.70, 0.30)])

    a = math.radians(M.TC_ANGLE)
    tc_pt = np.array([33.1 * math.cos(a), 33.1 * math.sin(a), M.BODY_TOP + 6])

    def tc_in(u):
        sc.show(sc.members("tc"), 1.0 if u > 0.01 else 0.0)
        sc.gmat["tc"] = T((0, 0, 140 * (1 - u)))
    sc.step("2a.6", "Thermocouple (Type N) in at the back right, down into the hole in the crucible wall, bent to sit "
            "close; its plug is behind the lever post. Leave it in even for maintenance, or the HMI raises 'master "
            "temperature sensor'.", 3.5, tc_in,
            hold=1.2, labels=[lab("wall thermocouple,\nback right", tc_pt + np.array([40, 0, 0]), 0.70, 0.22)])

    def rod_in(u):
        sc.show(sc.members("rod"), 1.0 if u > 0.01 else 0.0)
        sc.gmat["rod"] = T((0, 0, 260 * (1 - u) - 12))      # onto the nozzle (the piston it rides on is still up)
    sc.step("2a.7", "Sealing rod in BEFORE any metal, its tip clean and smooth or it will not seal. Screwed into its "
            "adapter, it goes straight down onto the nozzle.", 3.5, rod_in, hold=1.2,
            labels=[lab("sealing rod", (0, -6, M.Z_CR + 60), 0.70, 0.40),
                    lab("rod adapter", (0, -10, M.Z_ARM - 30), 0.70, 0.22)])

    def lever_down(u):
        lever(sc, 1 - window(u, 0.0, 0.6))
        v = window(u, 0.7, 1.0)
        rod_lift(sc, 12 * (1 - v))
        sc.gmat["rod"] = T((0, 0, -12 * (1 - v)))            # the rod stays on the nozzle; the eye slides down to it
        gauges(sc, t=24, rod="DOWN" if u > 0.95 else "lever on, pin in")
    sc.step("2a.8", "Swing the lever down onto the adapter, push the safety pin in, and press SEALING ROD to bring it "
            "down. The rod now rides on the lever, which the pneumatics lift to pour.", 3.5, lever_down, hold=1.2,
            labels=[lab("lever on the adapter,\nsafety pin in", (30, 0, M.Z_ARM + 10), 0.70, 0.20)])

    def charge_in(u):
        for k in range(4):
            w = window(u, 0.18 * k, 0.18 * k + 0.45)
            sc.show(sc.members(f"slug{k}"), 1.0 if u > 0.18 * k else 0.0)
            sc.gmat[f"slug{k}"] = T((0, 0, 260 * (1 - w)))
    sc.step("2a.9", "Charge: clean rods no thicker than 20 mm, 250–300 g; here 4 × Ø17 × 100 mm 6063 (≈245 g), "
            "dropped in round the rod, beside the lever. They stand proud and sink as they melt.", 5.0,
            charge_in, hold=1.4, still=True,
            labels=[lab("charge: 4 rods, ≈245 g", (slug_xy(1)[0], slug_xy(1)[1], M.Z_CR + 85), 0.06, 0.62)])

    def close_lid(u):
        set_cut(sc, 1 - window(u, 0.6, 1.0))
        hood(sc, 110 * (1 - window(u, 0.0, 0.6)))
    sc.step("2a.10", "Close the lid and set the latch just tight enough to seal: if it hisses under pressure, loosen "
            "it, adjust the latch and retighten. The chamber door stays open for the next step.", 3.5, close_lid,
            hold=1.6, cam_to=CAM["machine_near"])
    return sc.save()


# ------------------------------------------------------------------------------ 00 machine tour
def anim_00_machine():
    sc = Scene("00_machine", "rePowder induction atomizer: a tour of the machine")
    ms = load_machine(sc)
    # cutaway halves, hidden until the end
    for name, m in ms.items():
        if m["group"] in FURNACE_CUT + CHAMBER_CUT and m["half"] is not None:
            sc.add("h:" + name, m["half"], m["color"], m["group"], shown=False)
            if m["half_cut"] is not None:
                sc.add("h:" + name + "#cut", m["half_cut"], lighter(m["color"]), m["group"], shown=False,
                       smooth_shading=False, ambient=0.55, diffuse=0.5, specular=0.0)
    whole_cut = [n for n in ms if ms[n]["group"] in FURNACE_CUT + CHAMBER_CUT and n in sc.actors]
    halves = [n for n in sc.actors if n.startswith("h:")]
    focus = np.array([120.0, 300.0, 850.0])

    def orbit_cam(az, el, dist, f=focus):
        a, e = math.radians(az), math.radians(el)
        pos = f + dist * np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
        return [tuple(pos), tuple(f), (0, 0, 1)]

    sc.cam = orbit_cam(-115, 24, 4700)
    sc.step("0.1", "BYU's AMAZEMET rePowder: an induction furnace on top of an argon-filled atomization chamber, "
            "with the controls and electronics built into its blue frame, and the utilities round it.", 2.0, None,
            hold=1.0,
            cam_to=orbit_cam(-118, 24, 4300))
    sc.step("0.2", "On top, the Blue Power furnace: a stainless body holding the coil, crucible and insulation, "
            "under a faceted lid with a window, hinged on the left.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-112, 22, 2600, np.array([20, 120, 1250])),
            labels=[lab("furnace lid (bell)", (-30, -110, 1440), 0.06, 0.22),
                    lab("furnace body", (-90, -100, 1250), 0.06, 0.40)])
    sc.step("0.3", "Controls: the melting control panel (furnace) and the main switch on the blue frame, and the "
            "15.6 in HMI on its swing arm, which runs pressures, gas and ultrasonics.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-82, 18, 2700, np.array([330, 150, 1350])),
            labels=[lab("melting control panel", M.PANEL_C, 0.06, 0.22),
                    lab("main switch", M.SWITCH_C, 0.06, 0.55),
                    lab("HMI", M.HMI_C + np.array([0, -20, 60]), 0.74, 0.20)])
    sc.step("0.4", "Below the furnace, the 57 L atomization chamber: a view port at the front, a door on the left "
            "held by three star-knob bolts, and an underside that slopes down to the outlet.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-118, 16, 2700, np.array([60, 0, 820])),
            labels=[lab("atomization chamber", (180, M.CH_Y[0], 850), 0.74, 0.40),
                    lab("view port", M.VIEWPORT + M.VIEWPORT_N * 40, 0.74, 0.22),
                    lab("door, 3 star knobs", (M.CH_X[0] - 20, -60, 1000), 0.06, 0.30)])
    sc.step("0.5", "The ultrasonic unit rides in the door: transducer under its cover outside, sonotrode and plate "
            "inside, under the furnace nozzle.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-150, 14, 2300, np.array([-150, 0, 850])),
            labels=[lab("ultrasonic unit:\ntransducer under its cover", M.PLATE_C - M.STACK_DIR * 330, 0.06, 0.55)])
    sc.step("0.6", "The sloped underside and a short cone take the powder down through a valve to the airlock "
            "container, clamped on by its flange.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-120, 12, 2300, np.array([200, 0, 420])),
            labels=[lab("cone + valve", (M.CHUTE_X, -60, 360), 0.74, 0.40),
                    lab("powder container", (M.CHUTE_X, -66, 160), 0.74, 0.62)])
    sc.step("0.7", "Behind and beside it: argon 5N with its regulator, the vacuum pump, compressed air for the "
            "transducer, and the heat exchanger on the chilled water.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-98, 42, 5200, np.array([150, 450, 450])),
            labels=[lab("argon 5N", (-560, 650, 1000), 0.06, 0.30),
                    lab("vacuum pump", (-700, 140, 220), 0.06, 0.70),
                    lab("heat exchanger", (920, 140, 800), 0.74, 0.40),
                    lab("compressed air", (-275, 960, 1430), 0.06, 0.15)])

    def to_cut(u):
        for n in whole_cut:
            sc.alpha[n] = 1 - u
        for n in halves:
            sc.alpha[n] = u
    sc.step("0.8", "Cut in half at the furnace axis: crucible, sealing rod and nozzle over the plate, and the cone "
            "down to the container.", 3.0, to_cut, hold=2.0, still=True,
            cam_to=CAM["column"],
            labels=[lab("crucible + sealing rod", (0, 0, M.Z_CR + 40), 0.06, 0.18),
                    lab("plate on the sonotrode", M.PLATE_C, 0.06, 0.42),
                    lab("powder container", (M.CHUTE_X + M.CONT_R - 2, 0, 160), 0.74, 0.75)])
    return sc.save()


# ------------------------------------------------------------------------------------ 06 pour
def anim_06_pour():
    sc = Scene("06_pour", "5 · Pour and atomize")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, ghost={"stack_cover": 0.35}, hide=UTILITY_NAMES, pipes=False,
                 defer=True)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    pool = Pool(sc, half=True, level=36)
    powder = Powder(sc, half=True, level=0)
    add_stream(sc)
    spray = Particles(sc, "spray", (0.40, 0.41, 0.46), size=5.5)       # dark enough to read on the chamber wall
    drops = Particles(sc, "drops", MELT, size=7.0, slowmo=0.35)
    heat(sc, 795, 1.0)
    add_gas(sc, half=True, furnace=0.7, chamber=0.7)
    st = dict(pf=130.0, pc=150.0, us="off", amp=None, level=36.0, made=0.0)
    sc.cam = CAM["column"]

    def show_g():
        gauges(sc, furnace=st["pf"], chamber=st["pc"], o2=45, t=795, us=st["us"], amp=st["amp"])
    show_g()

    def vibrate(on):
        k = tick(sc) % 2
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if (on and k) else 0.0))

    sc.step("5.1", "Melt held at ~800 °C, O₂ at 45 ppm. The pour goes in this order, quickly: vibration "
            "ON, draining pressure, sealing rod UP, turbo as needed.", 3.0, lambda u: (cut_in(sc, u), show_g()),
            hold=1.2,
            cam_to=CAM["pour"], labels=[lab("melt, ~800 °C", (-14, 0, M.Z_CR + 20), 0.06, 0.30),
                                        lab("plate", M.PLATE_C, 0.06, 0.72)])

    def us_on(u):
        st["us"], st["amp"] = "40.08 kHz", 90 * u
        vibrate(True)
        show_g()
    sc.step("5.2", "Vibration ON. Amplitude is a percentage of generator current: start about 90 % and adjust; "
            "lower gives finer powder but may stop atomizing.", 2.5, us_on, hold=1.0, live=True)

    def drain(u):
        st["pf"] = 130 + 90 * u
        vibrate(True)
        show_g()
    sc.step("5.3", "Draining pressure: furnace above chamber pushes the melt out. Only the difference matters.",
            2.0, drain, hold=1.0, live=True)

    def rod_up(u):
        rod_lift(sc, 12 * window(u, 0.0, 0.3))
        stream(sc, 1.0 if u > 0.3 else 0.0, 1.0, window(u, 0.3, 0.6))
        if 0.6 < u < 0.95 and sc.n % max(1, 3 * FPS // 15) == 0:
            drops.emit_drops(2, M.IMPACT + np.array([0, 0, 3]), M.PLATE_UP * 250 + M.STACK_DIR * 500)
        drops.step()
        vibrate(True)
        show_g()
    sc.step("5.4", "Sealing rod UP: the melt stream falls onto the plate. The first drops usually bounce off: a "
            "cold, dry plate does not wet.", 3.0, rod_up, hold=1.0, live=True, cam_to=CAM["stream"],
            labels=[lab("sealing rod up", (0, -6, M.Z_CR + 70), 0.70, 0.22),
                    lab("melt stream", (0, 0, 1000), 0.70, 0.45)])

    def turbo(u):
        st["pf"] = 220 + (1500 - 220) * (math.sin(math.pi * u))
        stream(sc, 1.0, 1.0 + 0.8 * math.sin(math.pi * u))
        spray.emit_spray(per_frame(int(18 * window(u, 0.3, 1.0))))
        spray.step()
        drops.step()
        st["level"] -= 0.12 * PER_FRAME
        pool.set(st["level"])
        vibrate(True)
        show_g()
    sc.step("5.5", "A short TURBO push (1.5 bar) heats the plate and clears debris; pouring more at the start is "
            "what makes the plate wet.", 2.5, turbo, hold=1.0, live=True)

    def atomize(u, rate=28, cam=None):
        st["pf"] = 220
        stream(sc, 1.0, 1.0)
        spray.emit_spray(per_frame(rate))
        spray.step()
        drops.step()
        st["level"] = max(-12.0, st["level"] - 0.085 * PER_FRAME)
        pool.set(st["level"])
        st["made"] += rate
        powder.set(3 + 55 * min(1.0, spray.landed / 5200))
        vibrate(True)
        show_g()
    sc.step("5.6", "Once the plate is hot every drop atomizes: droplets fly off the plate, freeze in the argon and "
            "fall to the cone. Steer with the plate position: land high on it, not over the top.", 6.0, atomize,
            hold=1.0, live=True, labels=[lab("droplets freeze into powder", M.IMPACT + np.array([90, 0, -40]), 0.70, 0.62)])
    sc.step("5.7", "The powder runs down the cone into the container. Too thin a stream gathers and drips; melt "
            "shooting past the plate means the pressure is too high (the Oct 2 lesson).", 6.0, atomize, hold=1.0, live=True,
            cam_to=CAM["chamber"], still=True,
            labels=[lab("powder container", (M.CHUTE_X + M.CONT_R - 2, 0, 300), 0.70, 0.75)])
    sc.step("5.8", "Two to three minutes of attention: amplitude slider, turbo pulses, plate position, with the "
            "operator at the window the whole time.", 6.0, atomize, hold=1.0, live=True)

    def tail(u):
        st["level"] = max(-12.0, st["level"] - 0.2 * PER_FRAME)
        pool.set(st["level"])
        stream(sc, 1.0 if u < 0.6 else 0.0, 1.0 - 0.6 * u)
        if u < 0.6:
            spray.emit_spray(per_frame(int(20 * (1 - u))))
        spray.step()
        powder.set(3 + 55 * min(1.0, spray.landed / 5200))
        vibrate(True)
        show_g()
    sc.step("5.9", "The crucible runs empty: next, the end-of-pour sequence (step 6).", 3.0, tail, hold=1.5, live=True)
    return sc.save()


# ------------------------------------------------------------------------------- 02 stack
def anim_02_stack():
    sc = Scene("02_stack", "2c \u00b7 Ultrasonic stack: build, mount, scan, close the door")
    # the door is locked open for this, so the stack and plate are in plain view: no cutaway. The furnace is loaded and
    # the container, splash disc and catch bowl are in (2a and 2b): the stack goes in last, then the door shuts.
    load_machine(sc, hide=UTILITY_NAMES, pipes=False)
    DOOR = 100.0
    door(sc, DOOR)
    for c in range(3):
        clamp(sc, c, 0.0)
    dm = door_mat(DOOR)[:3, :3]
    w = lambda p: on_door(p, DOOR)                           # door-frame point -> world
    bench = 330.0             # the stack is put together this far out along its axis, then slid in
    for g in ("transducer", "booster", "sonotrode", "plate", "cover"):
        sc.show(sc.members(g), 0.0)
    for g in ("transducer", "booster", "sonotrode"):
        sc.gmat[g] = T(-M.STACK_DIR * bench)
    sc.gmat["plate"] = T(M.STACK_DIR * 140)
    sc.gmat["cover"] = T(-M.STACK_DIR * 300)
    pw = w(M.PLATE_C)
    # the open door's stack points its transducer end at the operator: look at the assembly side-on, from the left, and
    # at the plate from behind the door, where it now sits
    mid = w(M.PLATE_C - M.STACK_DIR * (bench + 180))
    axis = dm @ -M.STACK_DIR
    side_dir = np.cross(axis, (0, 0, 1.0))
    side_dir = side_dir / np.linalg.norm(side_dir)
    if side_dir[0] > 0:
        side_dir = -side_dir
    cam_side = [tuple(mid + side_dir * 1550 + np.array([0, 0, 470])), tuple(mid + np.array([0, 0, 110])), (0, 0, 1)]
    cam_in = [tuple(pw + np.array([-430, 620, 260])), tuple(pw + np.array([0, 0, -30])), (0, 0, 1)]
    sc.cam = CAM["machine_near"]
    gauges(sc, status="chamber ready, door locked open")

    def transducer_in(u):
        sc.show(sc.members("transducer"), min(1.0, u * 4))
        sc.gmat["transducer"] = T(-M.STACK_DIR * (bench + 160 * (1 - u)))
    sc.step("2c.1", "The stack goes transducer \u2192 booster \u2192 sonotrode \u2192 plate, and it goes in last, "
            "after the furnace and the chamber. First the transducer: piezo stack, ~1000 V cable, air-cooled. Never "
            "drop it or get it wet.", 3.5, transducer_in, hold=1.2, cam_to=cam_side,
            labels=[lab("transducer", w(M.PLATE_C - M.STACK_DIR * (bench + 320)), 0.06, 0.62)])

    def booster_on(u):
        sc.show(sc.members("booster"), min(1.0, u * 4))
        sc.gmat["booster"] = T(-M.STACK_DIR * (bench - 120 * (1 - u))) @ R(M.STACK_DIR, 300 * (1 - u), M.PLATE_C)
        gauges(sc, torque="65 N\u00b7m" if u > 0.9 else "\u2026")
    sc.step("2c.2", "Booster onto the transducer, 65 N\u00b7m (M10 fine thread). The 1.5:1 booster mounted in "
            "reverse lowers the amplitude, for finer powder.", 3.0, booster_on, hold=1.2,
            labels=[lab("booster 1.5:1", w(M.PLATE_C - M.STACK_DIR * (bench + 210)), 0.06, 0.40)])

    def sono_on(u):
        sc.show(sc.members("sonotrode"), min(1.0, u * 4))
        sc.gmat["sonotrode"] = T(-M.STACK_DIR * (bench - 120 * (1 - u))) @ R(M.STACK_DIR, 300 * (1 - u), M.PLATE_C)
        gauges(sc, torque="60 N\u00b7m" if u > 0.9 else "\u2026")
    sc.step("2c.3", "Sonotrode on, 60 N\u00b7m, isopropanol on the threads. Its KF50 flange is always at the top.",
            3.0, sono_on, hold=1.2,
            labels=[lab("sonotrode, KF50 flange", w(M.PLATE_C - M.STACK_DIR * (bench + 110)), 0.06, 0.25)])

    def stack_in(u):
        for g in ("transducer", "booster", "sonotrode"):
            sc.gmat[g] = T(-M.STACK_DIR * bench * (1 - u))
        gauges(sc, status="stack in the door housing")
    sc.step("2c.4", "With the splash disc already in and the door locked open, slide the stack into the door's housing "
            "and fit both clamps without touching the safety cover.", 3.5, stack_in,
            hold=1.0, labels=[lab("door housing", w(M.PLATE_C - M.STACK_DIR * (M.DOOR_S + 30)), 0.06, 0.30)])

    def plate_on(u):
        sc.show(sc.members("plate"), min(1.0, u * 4))
        sc.gmat["plate"] = T(M.STACK_DIR * 140 * (1 - u)) @ R(M.STACK_DIR, 360 * 2 * (1 - u), M.PLATE_C)
        gauges(sc, torque="50 N\u00b7m" if u > 0.9 else "\u2026")
    sc.step("2c.5", "Plate onto its M8 stud with the stack in the housing: 50 N\u00b7m, counter-holding the "
            "sonotrode with a 17 mm wrench.", 3.0, plate_on, hold=1.2, cam_to=cam_in,
            labels=[lab("plate, Ti 20 \u00d7 100", w(M.PLATE_C + M.PLATE_UP * 30), 0.70, 0.25)])

    def scan(u):
        f = 39.6 + 0.9 * u
        gauges(sc, scan=f"{f:.2f} kHz \u2026" if u < 0.95 else "one wide peak at 40.12 kHz")
    sc.step("2c.6", "Advanced ultrasonics \u2192 scan: one wide peak a little over 40 kHz. A double peak? Run a "
            "short burst and rescan.", 3.0, scan, hold=1.4)
    mist = Particles(sc, "mist", (0.35, 0.65, 1.0), size=4.0, slowmo=0.15, seed=5, free=True)
    sd, pu = dm @ M.STACK_DIR, dm @ M.PLATE_UP
    ny = np.cross(sd, pu)

    def wet(u):
        if u < 0.7:
            n = per_frame(6)
            r = mist.rng
            p = pw[None, :] + pu[None, :] * r.uniform(-45, 45, n)[:, None] + ny[None, :] * r.uniform(-9, 9, n)[:, None]
            v = sd[None, :] * r.uniform(150, 700, n)[:, None] + r.normal(0, 150, (n, 3))
            mist.p = np.vstack([mist.p, p])
            mist.v = np.vstack([mist.v, v])
        mist.step()
        gauges(sc, us="40.12 kHz", amp=90)
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if tick(sc) % 2 else 0.0))
    sc.step("2c.7", "Wet test: a drop of water should atomize over the whole plate. If only half of it atomizes, "
            "the plate is cracked.", 3.5, wet, hold=1.0, live=True)

    def cover_on(u):
        mist.p = mist.p[:0]
        mist.v = mist.v[:0]
        mist.step()
        sc.gmat["plate"] = np.eye(4)
        sc.show(sc.members("cover"), min(1.0, u * 4))
        sc.gmat["cover"] = T(-M.STACK_DIR * 300 * (1 - u))
        gauges(sc, status="cover on, air + cable locked")
    sc.step("2c.8", "Bolt the protective cover over the transducer, then push in and lock the cable and connect "
            "the cooling air: two or three minutes that protect a part worth thousands.", 3.0, cover_on, hold=1.4,
            cam_to=cam_side, labels=[lab("protective cover", w(M.PLATE_C - M.STACK_DIR * 330), 0.06, 0.62)])

    def shut(u):
        door(sc, DOOR * (1 - u))
        gauges(sc, status="frequency checked; door closing")
    sc.step("2c.9", "Run the frequency check now, before closing. Then swing the door shut: the stack rides in it, and "
            "the plate swings in under the nozzle.", 3.5, shut, hold=1.0, cam_to=CAM["door_out"])

    def clamps(u):
        for c in range(3):
            clamp(sc, c, window(u, 0.25 * c, 0.25 * c + 0.4))
        gauges(sc, status="door closed, 3 bolts tight" if u > 0.95 else "swinging the bolts over")
    sc.step("2c.10", "Swing the three bolts over the door's back edge and tighten the star knobs. Opening one under "
            "pressure just leaks.", 3.0, clamps, hold=2.0, still=True,
            labels=[lab("3 star-knob bolts", M.CLAMP_PTS[1] + np.array([-20, 0, 0]), 0.74, 0.40)])
    return sc.save()


# ------------------------------------------------------------------------------- 03b chamber
def anim_03b_chamber():
    sc = Scene("03b_chamber", "2b · Chamber: splash disc, container, catch bowl")
    ghost = {"chamber": 0.28, "chamber_slots": 0.28, "chute": 0.35, "viewport_glass": 0.4}
    load_machine(sc, ghost=ghost, hide=UTILITY_NAMES, pipes=False, defer=True)    # see-through only inside
    for g in STACK:                       # the stack goes in after this (2c)
        sc.show(sc.members(g), 0.0)
    door(sc, 100)                         # still open from the furnace step
    for c in range(3):
        clamp(sc, c, 0.0)
    floor = np.array((0.0, -330.0, -M.CONT_Z[0]))     # container standing on the floor in front
    held = np.array((0.0, -330.0, -20.0))
    under = np.array((0.0, 0.0, -20.0))               # under the outlet, 20 mm low
    sc.gmat["container"] = T(floor)
    sc.show(sc.members("container"), 0.0)
    sc.gmat["splash"] = T((0, 0, 120))
    sc.show(sc.members("splash"), 0.0)
    flange_clamp(sc, 0.0)
    bowl_out = np.array((-738.0, 0.0, 476.0))         # outside the open door, at the opening's height
    sc.show(sc.members("bowl"), 0.0)
    sc.gmat["bowl"] = T(bowl_out)
    sc.cam = CAM["container"]
    gauges(sc, status="chamber open, at atmosphere")

    def disc(u):
        sc.show(sc.members("container"), 1.0 if u > 0.01 else 0.0)
        sc.show(sc.members("splash"), 1.0 if u > 0.15 else 0.0)
        sc.gmat["splash"] = T((0, 0, 120 * (1 - window(u, 0.2, 0.9))))
    sc.step("2b.1", "Splash-protection disc first: it drops into the container's top flange. One is enough for "
            "aluminium.", 3.5, disc, hold=1.2,
            labels=[lab("splash disc", floor + np.array([M.CHUTE_X + 40, 0, M.CVALVE_Z[1]]), 0.06, 0.35),
                    lab("powder container", floor + np.array([M.CHUTE_X, -66, 160]), 0.06, 0.62)])

    def cont(u):
        w = window(u, 0.0, 0.8)
        sc.gmat["container"] = T(path(w, [floor, held, under, (0, 0, 0)]))
        flange_clamp(sc, window(u, 0.82, 1.0))
    sc.step("2b.2", "Lift the container under the outlet and close the flange clamp, finger-tight. A second person "
            "makes this easier (one holds the weight, one closes the clamp); alone, keep it supported until the clamp "
            "is shut.", 5.5, cont, hold=1.4,
            labels=[lab("flange clamp", (M.CHUTE_X + 62, -30, M.CLAMP_Z[0] + 6), 0.74, 0.50)])

    def bowl(u):
        cut_in(sc, u)
        sc.show(sc.members("bowl"), 1.0 if u > 0.05 else 0.0)
        w = window(u, 0.1, 1.0)
        sc.gmat["bowl"] = T(path(w, [bowl_out, bowl_out * np.array([0.336, 0, 1]), (0, 0, bowl_out[2]), (0, 0, 0)]))
    sc.step("2b.3", "Through the open door: the catch bowl goes on the chamber floor, round the outlet. It catches "
            "un-atomized melt and protects the chamber if a plate breaks. Wipe the chamber and hang the covers.", 5.0,
            bowl, hold=1.6, cam_to=CAM["left_high"], still=True,
            labels=[lab("catch bowl", (M.CHUTE_X + 50, 0, M.CH_BOTTOM + 20), 0.74, 0.70)])
    return sc.save()


# ---------------------------------------------------------------------------------- 05 melt
def anim_05_melt():
    sc = Scene("05_melt", "4 · Melt: overshoot to drop the rods, hold at ~800 °C, wait 2 min")
    load_machine(sc, cut=FURNACE_CUT, hide=tuple(n for n in UTILITY_NAMES if n != "air_frl"), pipes=("air",),
                 defer=True)
    pool = Pool(sc, half=True, level=-30)
    add_gas(sc, half=True, furnace=0.7, chamber=0.0)
    st = dict(t=500.0, set=1000.0)
    sc.cam = CAM["furnace_sec"]

    def show_g(extra=None):
        gauges(sc, furnace=130, chamber=150, o2=45, set=st["set"], t=st["t"], **(extra or {}))
    heat(sc, 500, 1.0)
    show_g()

    def heat_up(u):
        cut_in(sc, u)
        st["t"] = 500 + 350 * u
        heat(sc, st["t"], 1.0)
        show_g()
    sc.step("4.1", "Setpoint 850–1000 °C: long rods heat at the bottom and stay cooler at the top, so "
            "overshoot first. The generator heats the graphite; the graphite heats the charge.", 4.0, heat_up,
            hold=1.0, labels=[lab("coil on (10 kW, 7 kHz)", (-47, 0, M.Z_CR - 28 + 12.5 * 2.5), 0.06, 0.62),
                              lab("charge heating", (slug_xy(1)[0], 0, M.Z_CR + 70), 0.06, 0.28)])

    def cues(u):
        st["t"] = 850 + 30 * u - 12 * math.sin(math.pi * window(u, 0.5, 1.0))
        heat(sc, st["t"], 1.0)
        rod_lift(sc, -1.5 * u)              # the rod and its lever sink a little as the charge gives way
        show_g()
    sc.step("4.2", "Melt cues: a small temperature dip as melt reaches the thermocouple, faster induction beeping, "
            "the sealing rod sinking a little, the Al 'jumping' in the middle.", 3.5, cues, hold=1.0)

    def slump(u):
        st["t"] = 870 - 70 * window(u, 0.4, 1.0)
        st["set"] = 1000 - 200 * window(u, 0.3, 0.5)
        for k in range(4):
            x, y = slug_xy(k)
            f = 1 - 0.95 * window(u, 0.05 * k, 0.75 + 0.05 * k)
            sc.gmat[f"slug{k}"] = S((1 + 0.1 * (1 - f), 1 + 0.1 * (1 - f), f), (x, y, M.Z_CR))
            sc.alpha[f"slug{k}"] = 1.0 if f > 0.07 else 0.0
        pool.set(-14 + 50 * window(u, 0.05, 0.95))
        heat(sc, max(st["t"], 760), 1.0)
        show_g()
    sc.step("4.3", "The rods slump into a pool. As soon as they do, bring the setpoint down to 780–800 "
            "°C: the plate will not stand much more.", 5.0, slump, hold=1.2, still=True,
            labels=[lab("melt pool", (-14, 0, M.Z_CR + 20), 0.70, 0.55)])

    def hold2(u):
        st["t"] = 800 - 5 * u
        secs = int(round(120 * (1 - u)))
        show_g({"hold": f"{secs // 60}:{secs % 60:02d}"})
    sc.step("4.4", "Wait 2 minutes once everything is liquid: the crucible-wall thermocouple lags the melt. Any "
            "longer only oxidizes it.", 4.0, hold2, hold=1.0)
    air = Flow(sc, "air", M.AIR_LINE)

    def meanwhile(u):
        air.on = 1.0
        air.step()
        show_g({"status": "transducer air ON, rescan"})
    sc.step("4.5", "Meanwhile: transducer cooling air on, rescan the ultrasonics (scans expire), hearing "
            "protection on, an operator at the window.", 4.0, meanwhile, hold=1.5, live=True, cam_to=CAM["column"],
            labels=[lab("cooling air to the transducer", M.PLATE_C - M.STACK_DIR * 380, 0.06, 0.62)])
    return sc.save()


# ------------------------------------------------------------------------------ 04 gas wash
def anim_04_gas_wash():
    sc = Scene("04_gas_wash", "3 · Gas wash: vacuum and argon, furnace then chamber")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, hide=UTILITY_NAMES, pipes=False, defer=True)
    add_gas(sc, half=True, furnace=1.0, chamber=1.0)
    st = dict(pf=150.0, pc=150.0, o2=1000.0, t=24.0, pump="off")
    sc.cam = CAM["wash"]

    class _Off:
        on = 0.0

        def step(self):
            pass
    vac, ar = _Off(), _Off()

    def show_g():
        gauges(sc, furnace=st["pf"], chamber=st["pc"], o2=st["o2"], t=st["t"], status=st["pump"])
    show_g()
    sc.step("3.1", "Pressure control OFF before any pumping (it holds 150 mbar). Wash one vessel while the other "
            "keeps its overpressure: graphite seals leak, and a leak should pull argon, not air.", 3.0,
            lambda u: (cut_in(sc, u), show_g()), hold=1.0,
            labels=[lab("furnace (argon)", (60, 60, 1250), 0.70, 0.18),
                    lab("chamber (argon, +150 mbar)", (150, 60, 860), 0.70, 0.40)])

    def cycle(vessel, o2_to, t_from=None, t_to=None):
        key = "pf" if vessel == "furnace" else "pc"
        gas = "gas_furnace" if vessel == "furnace" else "gas_chamber"
        o2_from = st["o2"]

        def f(u):
            if u < 0.5:
                w = window(u, 0.0, 0.45)
                st[key] = 150 - 1000 * w
                sc.alpha[gas] = 1 - w
                st["pump"] = f"pumping {vessel}"
                vac.on, ar.on = 1.0, 0.0
            else:
                w = window(u, 0.55, 1.0)
                st[key] = -850 + 1000 * w
                sc.alpha[gas] = w
                st["pump"] = f"argon into the {vessel}"
                vac.on, ar.on = 0.0, 1.0
                st["o2"] = o2_from + (o2_to - o2_from) * w
            st[key] = max(st[key], -850)
            if t_to is not None:
                st["t"] = t_from + (t_to - t_from) * u
                heat(sc, st["t"], 1.0)
            vac.step()
            ar.step()
            show_g()
        return f
    sc.step("3.2", "Furnace wash 1: pump to the gauge floor, about −850 mbar at Provo's altitude (−1000 at "
            "sea level): normal, not a leak. Then argon back in to +150.", 4.0, cycle("furnace", 650), hold=1.0)
    sc.step("3.3", "Furnace washes 2 and 3, same again. O₂ reads nonsense under vacuum: backfill, then read.",
            4.0, cycle("furnace", 380), hold=1.0)
    sc.step("3.3", "Furnace washes 2 and 3, same again. O₂ reads nonsense under vacuum: backfill, then read.",
            3.0, cycle("furnace", 260), hold=1.0)
    sc.step("3.4", "Then the chamber, while the furnace holds its overpressure: pump to the floor, fill with "
            "argon, repeat.", 4.0, cycle("chamber", 120), hold=1.0)
    sc.step("3.5", "Generator on, 250 °C, wash again: the target is moisture in new insulation and crucible, "
            "not the metal.", 4.5, cycle("furnace", 70, 24, 250), hold=1.0,
            labels=[lab("coil on: 250 °C", (-47, 0, M.Z_CR - 28 + 12.5 * 2.5), 0.06, 0.35)])
    sc.step("3.6", "500 °C, wash again. Stop washing once O₂ is low and stable: ≤100 ppm, best "
            "40–50 (the team has seen the low 20s).", 4.5, cycle("furnace", 45, 250, 500), hold=1.0,
            still=True)

    def ready(u):
        st["pf"] = 150 - 20 * u
        st["pump"] = "pressure control ON"
        vac.on = ar.on = 0.0
        vac.step()
        ar.step()
        show_g()
    sc.step("3.7", "Pressure control back ON at melting pressure, the furnace slightly below the chamber "
            "(130 / 150 mbar). Ready to melt.", 2.5, ready, hold=2.0)
    return sc.save()


# --------------------------------------------------------------------------- 07 end, cooldown
def anim_07_end_cooldown():
    sc = Scene("07_end_cooldown", "6–8 · End of pour, cool down, open, collect")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, ghost={"stack_cover": 0.35}, hide=UTILITY_NAMES, pipes=False,
                 defer=True)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    pool = Pool(sc, half=True, level=-11)
    powder = Powder(sc, half=True, level=55)
    add_stream(sc)
    add_gas(sc, half=True, furnace=0.7, chamber=0.7)
    spray = Particles(sc, "spray", (0.80, 0.80, 0.84), size=5.0)
    heat(sc, 795, 1.0)
    rod_lift(sc, 12)
    stream(sc, 1.0, 0.7)
    st = dict(pf=220.0, pc=150.0, t=795.0)
    sc.cam = CAM["pour"]

    def show_g(extra=None):
        gauges(sc, furnace=st["pf"], chamber=st["pc"], t=st["t"], **(extra or {}))
    show_g({"us": "40.08 kHz"})

    def turbo(u):
        cut_in(sc, u)
        st["pf"] = 220 + 1280 * math.sin(math.pi * u)
        pool.set(-11 - 3 * u)
        stream(sc, 1.0 if u < 0.85 else 0.0, 1.2 * (1 - u) + 0.3)
        if u < 0.8:
            spray.emit_spray(per_frame(10))
        spray.step()
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if tick(sc) % 2 else 0.0))
        show_g({"us": "40.08 kHz"})
    sc.step("6.1", "Crucible empty: one TURBO push clears the last drops and the nozzle.", 2.5, turbo, hold=1.0, live=True)

    def stop(u):
        rod_lift(sc, 12 * (1 - window(u, 0.0, 0.3)))
        st["pf"] = 220 - 90 * window(u, 0.2, 0.5)
        heat(sc, 795, 1 - window(u, 0.4, 0.6))
        spray.step()
        on = u < 0.75
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if (on and tick(sc) % 2) else 0.0))
        show_g({"us": "40.08 kHz" if on else "STOP"})
    sc.step("6.2", "Within seconds: sealing rod DOWN, melting pressure, generator STOP, ultrasonics STOP. "
            "Vibrating against solidified metal cracks the plate.", 3.0, stop, hold=1.0,
            labels=[lab("sealing rod down", (0, -6, M.Z_CR + 60), 0.70, 0.22)])

    def cool(u):
        st["t"] = 795 - 395 * u
        pool.set(-11, temp_color(st["t"], cold=(0.62, 0.63, 0.66)))
        spray.step()
        show_g({"status": "cooling, open at ≤400 °C"})
    sc.step("7.1", "Set 250 °C for next time and let it cool. Open at or below 400 °C: above 500 "
            "°C graphite burns in air. Cooling water stays on until about 100 °C.", 4.0, cool, hold=1.0)

    def show_whole(f):
        set_cut(sc, 1 - f, CHAMBER_CUT + ("*",))

    def vent(u):
        show_whole(window(u, 0.5, 1.0))
        st["pc"] = 150 * (1 - u)
        st["pf"] = 130 * (1 - u)
        set_gas(sc, furnace=0.7 * (1 - u), chamber=0.7 * (1 - u))
        show_g({"status": "pressure control OFF, VENT"})
    sc.step("7.2", "Pressure control OFF, press VENT. The door stays locked while the pressure is off "
            "atmospheric. Masks and lab coat on.", 3.0, vent, hold=1.0, cam_to=CAM["door_out"])

    def open_door(u):
        for c in range(3):
            clamp(sc, c, 1 - window(u, 0.12 * c, 0.12 * c + 0.3))
        door(sc, 100 * window(u, 0.45, 1.0))
    sc.step("7.3", "Swing the three bolts back and open the door: the plate comes out with it. The chamber and cone "
            "are water-cooled and wet; the furnace parts are still hot.", 4.0, open_door, hold=1.0)
    brush = Particles(sc, "brushed", (0.70, 0.71, 0.74), size=5.0, slowmo=0.5, seed=7)

    def brush_down(u):
        show_whole(1 - window(u, 0.0, 0.3))
        if u < 0.7:
            brush.emit_settle(per_frame(14))
        brush.step()
        powder.set(55 + 8 * u)
    sc.step("7.4", "Brush the plate, bowl, walls and view port down into the container, in a circle, before it "
            "comes off. Let the dust settle before reaching in.", 4.5, brush_down, hold=1.0, live=True, cam_to=CAM["chamber"],
            still=True)

    def take_off(u):
        brush.step()
        flange_clamp(sc, 1 - window(u, 0.25, 0.45))          # the clamp opens: its two halves part
        sc.gmat["container"] = T((0, -280 * window(u, 0.7, 1.0), -40 * window(u, 0.5, 0.68)))
    sc.step("8.1", "Close the container valve first (pull down and across: it is heavier than it looks), brush the "
            "top, release the clamp and lift it off. Argon stays inside, a semi-protective atmosphere.", 4.0,
            take_off, hold=1.0, cam_to=CAM["container"])

    def shutdown(u):
        st["t"] = 400 - 300 * u
        show_g({"status": "~100 °C: utilities off"})
    sc.step("8.2", "Pour onto paper, pick out chunks, sieve, bag, 6-character ID label, photo on GitHub. At about "
            "100 °C: heat exchanger, water, air, argon, power off, in any order.", 3.5, shutdown, hold=2.0)
    return sc.save()


# ----------------------------------------------------------------------------------- 08 clean
def anim_08_clean():
    sc = Scene("08_clean", "9 · Clean and reset")
    load_machine(sc, cut=tuple(g for g in FURNACE_CUT if g != "nozzle") + CHAMBER_CUT, ghost={"stack_cover": 0.35},
                 hide=UTILITY_NAMES, pipes=False, defer=True)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    pool = Pool(sc, half=True, level=-13)
    pool.set(-13, (0.55, 0.56, 0.58))
    door(sc, 100)
    for c in range(3):
        clamp(sc, c, 0.0)
    for g in ("container", "splash", "flange_clamp", "flange_clamp_b"):     # off since 8.1
        sc.show(sc.members(g), 0.0)
    dust = Particles(sc, "dust", (0.66, 0.67, 0.70), size=5.0, slowmo=0.5, seed=3)
    dust.emit_settle(160)
    sc.cam = CAM["chamber"]
    gauges(sc, t=60, status="cold, utilities off")

    def brush(u):
        cut_in(sc, u)
        if u > 0.1:
            dust.step()
    sc.step("9.1", "Same alloy next: open, brush, vacuum. A material change takes about an hour: vacuum, then wipe "
            "everything. Brushes, paper towels and isopropanol only.", 4.0, brush, hold=1.0, live=True)

    def plate_off(u):
        dust.step()
        sc.gmat["plate"] = T(M.STACK_DIR * 160 * window(u, 0.2, 1.0)) @ R(M.STACK_DIR, -400 * window(u, 0, 0.5),
                                                                        M.PLATE_C)
        sc.alpha.update({n: 1 - window(u, 0.8, 1.0) for n in sc.members("plate")})
    pw = on_door(M.PLATE_C, 100)
    sc.step("9.2", "Plate off its stud. Never grind or clean it: one plate per alloy, logged (1–3 runs "
            "each). A stainless scraper for stuck particles, never plastic.", 3.5, plate_off, hold=1.0,
            cam_to=[tuple(pw + np.array([-650, -650, 350])), tuple(pw), (0, 0, 1)],
            labels=[lab("plate", pw, 0.06, 0.30)])

    def rod_out(u):
        hood(sc, 110 * window(u, 0.0, 0.3))
        rod_lift(sc, 12 * window(u, 0.3, 0.4))             # SEALING ROD up: lever and rod together
        lever(sc, window(u, 0.42, 0.62))                  # pin out: the lever swings up, the rod is held
        sc.gmat["rod"] = T((0, 0, 260 * window(u, 0.64, 0.95)))
        sc.alpha.update({n: 1 - window(u, 0.9, 1.0) for n in sc.members("rod")})
    sc.step("9.3", "Once the furnace can be touched (150 °C is too hot): lid open, SEALING ROD up, safety pin out, "
            "lever up, rod out. Scrape Al off its shaft and keep the tip smooth.", 5.0, rod_out, hold=1.0,
            cam_to=CAM["furnace_top"], labels=[lab("slag on the crucible floor", (-12, 0, M.Z_CR - 8), 0.70, 0.55)])

    def up_and_away(g, dz, u, t0, t1):
        sc.gmat[g] = T((0, 0, dz * window(u, t0, t1)))
        sc.alpha.update({n: 1 - window(u, t1 - 0.04, t1) for n in sc.members(g)})

    def strip(u):
        up_and_away("tc", 140, u, 0.0, 0.14)
        up_and_away("top_ins", 330, u, 0.12, 0.28)
        up_and_away("side_ins", 300, u, 0.26, 0.42)
        unscrew = linear(u, 0.42, 0.6)
        drop = window(u, 0.6, 0.68)
        sc.gmat["nut"] = T((0, 0, -10 * unscrew - 84 * drop)) @ R((0, 0, 1), 360 * 5 * unscrew)
        sc.gmat["seal"] = T((0, 0, -94 * window(u, 0.62, 0.7)))
        sc.alpha.update({n: 1 - window(u, 0.68, 0.72) for n in sc.members("nut") + sc.members("seal")})
        w = window(u, 0.72, 0.95)
        sc.gmat["crucible"] = T(path(w, [(0, 0, 0), (0, 0, OVER), (BENCH[0], BENCH[1], OVER), BENCH]))
        set_cut(sc, 1 - window(u, 0.74, 0.8), ("crucible", "holder"))
        sc.alpha["pool"] = sc.alpha["pool#cut"] = 0.0 if u > 0.74 else 1.0      # slag peeled off
        up_and_away("bottom_ins", 360, u, 0.84, 1.0)
    sc.step("9.4", "Strip it in order: thermocouple, top and side insulation; through the door, hold the graphite nut "
            "and unscrew it from below with the seal, so nothing falls; then the crucible comes up and out, and the "
            "bottom insulation.", 9.0, strip, hold=1.2, cam_to=CAM["furnace_sec"])

    def nozzle_check(u):
        screw = linear(u, 0.0, 0.45)
        sc.gmat["holder"] = T((0, 0, -8 * screw - 62 * window(u, 0.45, 0.6))) @ R((0, 0, 1), -360 * 4 * screw)
        sc.gmat["nozzle"] = T(path(window(u, 0.6, 1.0), [(0, 0, 0), (0, 0, 12), NOZZLE_OUT]))
    sc.step("9.5", "On the bench, unscrew the holder and lift the nozzle out. Look through it for light; unclog it "
            "with a needle or drill it to Ø0.7; swap it if a new charge would not push through.", 5.0,
            nozzle_check, hold=1.2, cam_to=CAM["bench"],
            labels=[lab("nozzle: light through it?", BENCH + NOZZLE_OUT + np.array([0, 0, M.CRUCIBLE_BASE - 70]),
                        0.06, 0.55)])

    def rebuild(u):
        sc.gmat["nozzle"] = T(path(window(u, 0.0, 0.1), [NOZZLE_OUT, (0, 0, 12), (0, 0, 0)]))
        back = window(u, 0.1, 0.14)
        screw = linear(u, 0.14, 0.2)
        sc.gmat["holder"] = T((0, 0, -70 + 62 * back + 8 * screw)) @ R((0, 0, 1), 360 * 4 * screw)
        sc.show(sc.members("bottom_ins"), 1.0 if u > 0.2 else 0.0)
        sc.gmat["bottom_ins"] = T((0, 0, 360 * (1 - window(u, 0.2, 0.3))))
        w = window(u, 0.3, 0.5)
        sc.gmat["crucible"] = T(path(w, [BENCH, (BENCH[0], BENCH[1], OVER), (0, 0, OVER), (0, 0, 0)]))
        set_cut(sc, window(u, 0.44, 0.5), ("crucible", "holder"))
        sc.show(sc.members("nut") + sc.members("seal"), 1.0 if u > 0.5 else 0.0)
        sc.gmat["seal"] = T((0, 0, -94 * (1 - window(u, 0.5, 0.56))))
        nut_screw = linear(u, 0.56, 0.62)
        sc.gmat["nut"] = T((0, 0, -10 - 84 * (1 - window(u, 0.5, 0.56)) + 10 * nut_screw)) @ \
            R((0, 0, 1), -360 * 5 * nut_screw)
        for g, dz, t0 in (("side_ins", 300, 0.62), ("top_ins", 330, 0.7), ("tc", 140, 0.78)):
            sc.show(sc.members(g), 1.0 if u > t0 else 0.0)
            sc.gmat[g] = T((0, 0, dz * (1 - window(u, t0, t0 + 0.08))))
        sc.show(sc.members("rod"), 1.0 if u > 0.82 else 0.0)
        v = window(u, 0.93, 0.96)                 # SEALING ROD down: the eye slides down the stub, the rod stays put
        sc.gmat["rod"] = T((0, 0, 260 * (1 - window(u, 0.82, 0.88)) - 12 * (1 - v)))
        lever(sc, 1 - window(u, 0.88, 0.92))
        rod_lift(sc, 12 * (1 - v))
        hood(sc, 110 * (1 - window(u, 0.96, 1.0)))
    sc.step("9.6", "Reassemble in the same order as before a run: nozzle, holder, bottom insulation, crucible, nut, "
            "insulation, thermocouple, rod, lever. Wipe the O-rings; HEPA filter about every two months (sand tray).",
            9.0, rebuild, hold=2.0, still=True, cam_to=CAM["furnace_sec"])
    return sc.save()


# ------------------------------------------------------------------------------- 01 utilities
def anim_01_utilities():
    sc = Scene("01_utilities", "1 · Utilities on (before heating)")
    load_machine(sc)
    flows = {k: Flow(sc, k, c) for k, c in (("water_supply", (0.55, 0.75, 1.0)), ("water_return", (1.0, 0.6, 0.5)),
                                             ("air", (0.85, 0.95, 1.0)), ("argon", (0.6, 1.0, 0.75)))}
    sc.cam = CAM["machine"]
    gauges(sc, status="all off")

    def run(*keys):
        def f(u):
            for k in keys:
                flows[k].on = 1.0
            for fl in flows.values():
                fl.step()
        return f

    def switch(u):
        sc.gmat["switch"] = R((0, 1, 0), 90 * window(u, 0.4, 0.8), (M.SWITCH_C[0], M.FR_Y[0] - 10, M.SWITCH_C[2]))
        gauges(sc, status="main switch ON" if u > 0.8 else "all off")
    sc.step("1.1", "Breakers and main switch on. Everything else is still off.", 2.5, switch, hold=1.0,
            cam_to=[(-1200, -2600, 1900), (300, 200, 1250), (0, 0, 1)],
            labels=[lab("main switch", M.SWITCH_C, 0.74, 0.50)])
    sc.step("1.2", "Facility chilled water: open the valve only a little (at least 2 L/min, but 'water too cold' "
            "trips below 7–10 °C).", 3.5, run("water_supply", "water_return"), hold=1.0, live=True,
            cam_to=[(2300, -2400, 1900), (500, 400, 600), (0, 0, 1)],
            labels=[lab("chilled water to the coil", (M.FR_X[1] + 2, 420, 800), 0.06, 0.40)])
    sc.step("1.3", "Heat exchanger on only when you are about to heat; wait for 'cooling water flow low' to "
            "clear.", 3.0, run("water_supply", "water_return"), hold=1.0, live=True,
            labels=[lab("heat exchanger", (920, 140, 700), 0.74, 0.30)])
    sc.step("1.4", "Compressed air: 8 bar supply, about 4 bar regulated. It only cools the transducer, but no air "
            "means no ultrasonics.", 3.5, run("water_supply", "water_return", "air"), hold=1.0, live=True,
            cam_to=[(-2700, -1900, 1700), (-300, 300, 900), (0, 0, 1)],
            labels=[lab("air to the transducer", M.PLATE_C - M.STACK_DIR * 405, 0.74, 0.62),
                    lab("air filter-regulator", (-275, 960, 1430), 0.06, 0.20)])
    sc.step("1.5", "Argon 5N at 8 bar on the regulator (0–10 bar, not a welding regulator): one T into the "
            "furnace line and the chamber line; it also drives the pneumatics.", 3.5,
            run("water_supply", "water_return", "air", "argon"), hold=1.0, live=True,
            labels=[lab("argon 5N, regulator", (-560, 700, 1480), 0.06, 0.35)])
    sc.step("1.6", "Checklist: vacuum-pump oil in the sight glass, exchanger water level, HEPA filter (every ~2 "
            "months), hoses dry.", 3.5, run("water_supply", "water_return", "air", "argon"), hold=2.0, live=True,
            cam_to=CAM["machine"], still=True,
            labels=[lab("pump oil sight glass", (-590, 127, 110), 0.06, 0.75)])
    return sc.save()


# ------------------------------------------------------------------------- summary, for slides
def anim_summary():
    """About 30 s for a slide, in one take: the furnace loaded (2a), the ultrasonic stack mounted (2c), then the melt (4)
    and the pour (5). Same parts on the same paths, in the same order, as 03_furnace_load, 02_stack, 05_melt and 06_pour.
    The fasteners (holder, nut, booster, sonotrode, plate, cover, bolts) are sped up. The checks, gas washes and holds
    are left out. Captions and narration come from ../ppt/, so render it with VIZ3D_CLEAN=1."""
    sc = Scene("summary", "The rePowder atomizer: a run in 30 s")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, ghost={"stack_cover": 0.35}, hide=UTILITY_NAMES, pipes=False,
                 defer=True)
    sc.intro = 0.6
    # the furnace as 03_furnace_load starts it: cold, stripped, the crucible not yet built, the piston up
    hood(sc, 0)
    lift = {"side_ins": 300, "top_ins": 330, "bottom_ins": 360, "tc": 140, "rod": 260, "seal": -94}
    for g, dz in lift.items():
        sc.show(sc.members(g), 0.0)
        sc.gmat[g] = T((0, 0, dz))
    cru = sc.members("crucible") + sc.members("holder") + sc.members("nozzle")
    sc.show(cru, 0.0)
    sc.gmat["crucible"] = T(BENCH)
    sc.gmat["holder"] = T((0, 0, -70))
    sc.gmat["nut"] = T((0, 0, -94))
    sc.show(sc.members("nut"), 0.0)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    rod_lift(sc, 12)
    sc.gmat["rod"] = T((0, 0, lift["rod"] - 12))
    # the stack as 02_stack starts it: not built yet, so hidden, each part where it comes from (it rides on the door)
    bench = 330.0
    for g in STACK:
        sc.show(sc.members(g), 0.0)
    for g in ("transducer", "booster", "sonotrode"):
        sc.gmat[g] = T(-M.STACK_DIR * bench)
    sc.gmat["plate"] = T(M.STACK_DIR * 140)
    sc.gmat["cover"] = T(-M.STACK_DIR * 300)
    # the run, as 05_melt and 06_pour: no melt, no argon, no powder yet
    pool = Pool(sc, half=True, level=-30)
    powder = Powder(sc, half=True, level=0)
    add_stream(sc)
    spray = Particles(sc, "spray", (0.40, 0.41, 0.46), size=5.5)
    add_gas(sc, half=True, furnace=0.0, chamber=0.0)
    heat(sc, 24, 0.0)
    sc.cam = CAM["machine_near"]

    # ---- furnace (2a), each move as in 03_furnace_load, in the same order and with the same relative timing
    def open_lid(u):
        hood(sc, 110 * window(u, 0.0, 0.55))
        lever(sc, window(u, 0.5, 1.0))
    sc.step("F.1", "Lid open, lever up", 1.2, open_lid, hold=0, cam_to=CAM["bench"])

    def nozzle_in(u):                       # 4 turns in about a second: sped up
        sc.show(cru, 1.0 if u > 0.05 else 0.0)
        rise = window(u, 0.1, 0.3)
        screw = linear(u, 0.3, 0.97)
        sc.gmat["holder"] = T((0, 0, -70 + 62 * rise + 8 * screw)) @ R((0, 0, 1), 360 * 4 * screw)
    sc.step("F.2", "Holder screwed into the crucible (sped up)", 1.1, nozzle_in, hold=0)

    def crucible_in(u):
        set_cut(sc, window(u, 0.0, 0.15), FURNACE_FIXED)
        sc.show(sc.members("bottom_ins"), 1.0 if u > 0.02 else 0.0)
        sc.gmat["bottom_ins"] = T((0, 0, 360 * (1 - window(u, 0.05, 0.35))))
        sc.gmat["crucible"] = T(path(window(u, 0.4, 1.0), [BENCH, (BENCH[0], BENCH[1], OVER), (0, 0, OVER), (0, 0, 0)]))
        set_cut(sc, window(u, 0.75, 0.9), ("crucible", "holder", "nozzle"))
    sc.step("F.3", "Bottom insulation, then the crucible down into the coil", 2.6, crucible_in, hold=0.1,
            cam_to=CAM["furnace_top"])

    def nut_on(u):                          # 5 turns in about a second: sped up
        for c in range(3):
            clamp(sc, c, 1 - window(u, 0.02 * c, 0.02 * c + 0.08))
        door(sc, 100 * window(u, 0.1, 0.28))
        set_cut(sc, window(u, 0.18, 0.3), ("chamber",))
        sc.show(sc.members("nut") + sc.members("seal"), 1.0 if u > 0.2 else 0.0)
        rise = window(u, 0.22, 0.36)
        screw = linear(u, 0.36, 0.97)
        sc.gmat["seal"] = T((0, 0, -94 * (1 - window(u, 0.2, 0.32))))
        sc.gmat["nut"] = T((0, 0, -94 + 84 * rise + 10 * screw)) @ R((0, 0, 1), -360 * 5 * screw)
    sc.step("F.4", "Door open, the graphite nut on from below (sped up)", 2.3, nut_on, hold=0, cam_to=CAM["section_fr"])

    def insulation_in(u):
        a, b = window(u, 0.0, 0.55), window(u, 0.45, 1.0)
        sc.show(sc.members("side_ins"), 1.0 if u > 0.01 else 0.0)
        sc.gmat["side_ins"] = T((0, 0, 300 * (1 - a)))
        sc.show(sc.members("top_ins"), 1.0 if u > 0.45 else 0.0)
        sc.gmat["top_ins"] = T((0, 0, 330 * (1 - b)))
    sc.step("F.5", "Side and top insulation", 1.1, insulation_in, hold=0)

    def tc_in(u):
        sc.show(sc.members("tc"), 1.0 if u > 0.01 else 0.0)
        sc.gmat["tc"] = T((0, 0, 140 * (1 - u)))
    sc.step("F.6", "Thermocouple in (sped up)", 0.7, tc_in, hold=0)

    def rod_in(u):
        sc.show(sc.members("rod"), 1.0 if u > 0.01 else 0.0)
        sc.gmat["rod"] = T((0, 0, 260 * (1 - u) - 12))
    sc.step("F.7", "Sealing rod in", 1.0, rod_in, hold=0)

    def lever_down(u):
        lever(sc, 1 - window(u, 0.0, 0.6))
        v = window(u, 0.7, 1.0)
        rod_lift(sc, 12 * (1 - v))
        sc.gmat["rod"] = T((0, 0, -12 * (1 - v)))
    sc.step("F.8", "Lever down, pin in, rod down (sped up)", 0.7, lever_down, hold=0)

    def charge_in(u):
        for k in range(4):
            w = window(u, 0.18 * k, 0.18 * k + 0.45)
            sc.show(sc.members(f"slug{k}"), 1.0 if u > 0.18 * k else 0.0)
            sc.gmat[f"slug{k}"] = T((0, 0, 260 * (1 - w)))
    sc.step("F.9", "The charge", 1.4, charge_in, hold=0)

    def close_lid(u):
        set_cut(sc, 1 - window(u, 0.6, 1.0))
        hood(sc, 110 * (1 - window(u, 0.0, 0.6)))
    sc.step("F.10", "Lid closed", 1.2, close_lid, hold=0, cam_to=CAM["machine_near"])

    # ---- ultrasonic stack (2c), as in 02_stack: the door is still open from the nut
    DOOR = 100.0
    dm = door_mat(DOOR)[:3, :3]
    w = lambda p: on_door(p, DOOR)
    mid = w(M.PLATE_C - M.STACK_DIR * (bench + 180))
    axis = dm @ -M.STACK_DIR
    side_dir = np.cross(axis, (0, 0, 1.0))
    side_dir = side_dir / np.linalg.norm(side_dir)
    if side_dir[0] > 0:
        side_dir = -side_dir
    cam_side = [tuple(mid + side_dir * 1550 + np.array([0, 0, 470])), tuple(mid + np.array([0, 0, 110])), (0, 0, 1)]

    def transducer_in(u):
        v = window(u, 0.35, 1.0)
        sc.show(sc.members("transducer"), min(1.0, v * 4))
        sc.gmat["transducer"] = T(-M.STACK_DIR * (bench + 160 * (1 - v)))
    sc.step("S.1", "Transducer", 1.4, transducer_in, hold=0, cam_to=cam_side)

    def booster_sono(u):                    # 65 and 60 N·m: sped up
        for g, (t0, t1) in (("booster", (0.0, 0.5)), ("sonotrode", (0.5, 1.0))):
            v = window(u, t0, t1)
            sc.show(sc.members(g), min(1.0, v * 4))
            sc.gmat[g] = T(-M.STACK_DIR * (bench - 120 * (1 - v))) @ R(M.STACK_DIR, 300 * (1 - v), M.PLATE_C)
    sc.step("S.2", "Booster and sonotrode on (sped up)", 1.1, booster_sono, hold=0)

    def into_door(u):                       # then the plate, 50 N·m: sped up
        v = window(u, 0.0, 0.6)
        for g in ("transducer", "booster", "sonotrode"):
            sc.gmat[g] = T(-M.STACK_DIR * bench * (1 - v))
        p = window(u, 0.6, 1.0)
        sc.show(sc.members("plate"), min(1.0, p * 4))
        sc.gmat["plate"] = T(M.STACK_DIR * 140 * (1 - p)) @ R(M.STACK_DIR, 360 * 2 * (1 - p), M.PLATE_C)
    sc.step("S.3", "Into the door, plate on (sped up)", 1.2, into_door, hold=0)

    def cover_shut(u):                      # cover on (sped up), then the door swings shut
        c = window(u, 0.0, 0.3)
        sc.show(sc.members("cover"), min(1.0, c * 4))
        sc.gmat["cover"] = T(-M.STACK_DIR * 300 * (1 - c))
        door(sc, DOOR * (1 - window(u, 0.35, 1.0)))
    sc.step("S.4", "Cover on, door shut", 1.5, cover_shut, hold=0, cam_to=CAM["door_out"])

    def bolts(u):                           # the three star-knob bolts: sped up
        for c in range(3):
            clamp(sc, c, window(u, 0.25 * c, 0.25 * c + 0.4))
    sc.step("S.5", "Three bolts (sped up)", 0.7, bolts, hold=0)

    # ---- the run (4 melt, 5 pour), as in 05_melt and 06_pour; the gas washes are left out
    st = dict(level=-30.0)

    def vibrate(on):
        k = tick(sc) % 2
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if (on and k) else 0.0))

    def melt(u):
        cut_in(sc, u)
        set_gas(sc, furnace=0.7 * window(u, 0.05, 0.35), chamber=0.7 * window(u, 0.05, 0.35))
        coil = window(u, 0.2, 0.3)
        t = 24 + 846 * window(u, 0.25, 0.6) - 70 * window(u, 0.8, 1.0)
        heat(sc, t, coil)
        for k in range(4):
            x, y = slug_xy(k)
            f = 1 - 0.95 * window(u, 0.5 + 0.03 * k, 0.88 + 0.03 * k)
            sc.gmat[f"slug{k}"] = S((1 + 0.1 * (1 - f), 1 + 0.1 * (1 - f), f), (x, y, M.Z_CR))
            sc.alpha[f"slug{k}"] = 1.0 if f > 0.07 else 0.0
        st["level"] = -30 if u < 0.52 else -14 + 50 * window(u, 0.52, 0.97)
        pool.set(st["level"])
    sc.step("R.1", "Argon in; the coil melts the charge", 4.0, melt, hold=0, cam_to=CAM["furnace_sec"])

    def pour(u):
        vibrate(True)
        rod_lift(sc, 12 * window(u, 0.0, 0.2))
        stream(sc, 1.0 if u > 0.2 else 0.0, 1.0, window(u, 0.2, 0.4))
        if u > 0.4:
            spray.emit_spray(per_frame(int(28 * window(u, 0.4, 0.8))))
        spray.step()
        st["level"] = max(-12.0, st["level"] - (0.085 * PER_FRAME if u > 0.4 else 0.0))
        pool.set(st["level"])
        powder.set(3 + 55 * min(1.0, spray.landed / 1800))
    sc.step("R.2", "Vibration on, rod up: the melt onto the plate", 4.1, pour, hold=0, cam_to=CAM["stream"],
            live=True)

    def atomize(u):
        vibrate(True)
        stream(sc, 1.0, 1.0)
        spray.emit_spray(per_frame(28))
        spray.step()
        st["level"] = max(-12.0, st["level"] - 0.085 * PER_FRAME)
        pool.set(st["level"])
        powder.set(3 + 55 * min(1.0, spray.landed / 1800))
    sc.step("R.3", "Droplets freeze into powder, down into the container", 3.8, atomize, hold=0.5, live=True,
            cam_to=CAM["chamber"], still=True)
    return sc.save()


ANIMS = {
    "03_furnace_load": anim_03_furnace_load,
    "00_machine": anim_00_machine,
    "06_pour": anim_06_pour,
    "02_stack": anim_02_stack,
    "03b_chamber": anim_03b_chamber,
    "05_melt": anim_05_melt,
    "04_gas_wash": anim_04_gas_wash,
    "07_end_cooldown": anim_07_end_cooldown,
    "08_clean": anim_08_clean,
    "01_utilities": anim_01_utilities,
    "summary": anim_summary,
}

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(ANIMS)):
        ANIMS[name]()

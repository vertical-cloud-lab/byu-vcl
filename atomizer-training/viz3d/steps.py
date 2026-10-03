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
from scene import MELT, R, S, Scene, T, ease, lighter, load_machine, mix, temp_color, window

FURNACE_CUT = ("crucible", "nozzle", "furnace", "side_ins", "top_ins", "bottom_ins", "coil", "hood", "tc")
CHAMBER_CUT = ("chamber", "door", "bowl", "splash", "container", "flange_clamp")
UTILITY_NAMES = ("argon_cylinder", "argon_regulator", "argon_gauges", "vacuum_pump", "pump_sight_glass",
                 "heat_exchanger", "hx_grille", "hx_display", "air_frl")

CAM = {
    "machine": [(-2350, -3500, 2150), (180, 320, 820), (0, 0, 1)],
    "machine_near": [(-1650, -2500, 1750), (60, 100, 900), (0, 0, 1)],
    "furnace_top": [(-360, -900, 1800), (0, 0, 1335), (0, 0, 1)],
    "furnace_sec": [(-330, -820, 1430), (5, 0, 1262), (0, 0, 1)],
    "column": [(-760, -2650, 1020), (40, 0, 830), (0, 0, 1)],
    "pour": [(-620, -1720, 1220), (10, 0, 1070), (0, 0, 1)],
    "chamber": [(-1000, -2150, 930), (40, 0, 590), (0, 0, 1)],
    "stream": [(-380, -1050, 1100), (5, 0, 1000), (0, 0, 1)],
    "wash": [(-640, -2050, 1280), (40, 0, 1060), (0, 0, 1)],
    "container": [(-650, -1500, 700), (40, 0, 420), (0, 0, 1)],
    "door_out": [(-1500, -1250, 1050), (-150, 0, 780), (0, 0, 1)],
}

STREAM_TOP = M.NOZZLE_EXIT_Z
NOZZLE_OUT = np.array([-80.0, -70.0, -45.0])    # where the nozzle is held out of the crucible for the light check


# --------------------------------------------------------------------------------- helpers
def hood(sc, deg):
    sc.gmat["hood"] = R((0, 1, 0), -deg, M.HINGE)


def door(sc, deg):
    sc.gmat["door"] = R((0, 0, 1), -deg, (M.DOOR_HINGE[0], M.DOOR_HINGE[1], 0))


def clamp(sc, k, f):
    """f = 1 closed, 0 open (lever flipped up)."""
    z = (M.CH_Z[0] + 75, (M.CH_Z[0] + M.CH_Z[1]) / 2, M.CH_Z[1] - 75)[k]
    sc.gmat[f"clamp{k}"] = R((0, 1, 0), 80 * (1 - f), (M.CH_X[0] - 4, M.CH_Y[0] - 19, z))


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
    for n in ("coil", "coil#cut"):
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

    def __init__(self, sc, name, color, size=6.0, slowmo=0.22, seed=1):
        self.sc, self.name, self.slowmo = sc, name, slowmo
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
        p = np.column_stack([r.uniform(-100, 220, n), r.uniform(2, 160, n), np.full(n, M.CH_Z[0] + 8)])
        self.p = np.vstack([self.p, p])
        self.v = np.vstack([self.v, np.zeros((n, 3))])

    def step(self, dt=1 / 15):
        if len(self.p):
            h = dt * self.slowmo
            self.v[:, 2] -= 9810 * h
            self.v *= (1 - 1.8 * h)
            self.p += self.v * h
            x0, x1 = M.CH_X[0] + 6, M.CH_X[1] - 6
            y0, y1 = 1.0, M.CH_Y[1] - 6
            inside = self.p[:, 2] > M.CH_Z[0] + 6
            for ax, lo, hi in ((0, x0, x1), (1, y0, y1)):
                hit = inside & ((self.p[:, ax] < lo) | (self.p[:, ax] > hi))
                self.p[hit, ax] = np.clip(self.p[hit, ax], lo, hi)
                self.v[hit, ax] *= -0.15
            low = self.p[:, 2] <= M.CH_Z[0] + 8
            if low.any():   # on the chamber floor / chute: slide to the outlet and drop
                tgt = np.array([M.CHUTE_X, 0.0, M.CONT_Z[1] - 10])
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
    ch = pv.Box(bounds=(M.CH_X[0] + 5, M.CH_X[1] - 5, M.CH_Y[0] + 5, M.CH_Y[1] - 5, M.CH_Z[0] + 5, M.CH_Z[1] - 5))
    ch = ch.triangulate().merge(pv.Cylinder(center=(M.CHUTE_X, 0, 280), direction=(0, 0, 1), radius=M.CONT_R - 6,
                                            height=240, resolution=48).triangulate())
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
        self.phase = (self.phase + self.speed) % (1.0 / self.n)
        s = (np.arange(self.n) / self.n + self.phase) % 1.0
        idx = (s * (len(self.line) - 1)).astype(int)
        self.sc.set_mesh(self.name, pv.PolyData(self.line[idx].copy()))
        self.sc.alpha[self.name] = self.on


def add_whole(sc, groups):
    """Hidden whole copies (named w:<part>) of parts that are shown halved, for crossfading out of a cutaway."""
    ms = M.meshes()
    names = []
    for name, m in ms.items():
        if m["group"] in groups and m["half"] is not None or (m["group"] in groups and m.get("gone")):
            sc.add("w:" + name, m["whole"], m["color"], m["group"], shown=False)
            names.append("w:" + name)
    return names


def cut_names(sc):
    ms = M.meshes()
    return {n for n in sc.actors if n.split("#")[0] in ms and ms[n.split("#")[0]]["half"] is not None}


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
    sc = Scene("03_furnace_load", "3 · Furnace prep and loading")
    load_machine(sc, cut=FURNACE_CUT, hide=UTILITY_NAMES, pipes=False)
    # start: lid closed, everything that gets rebuilt is out
    hood(sc, 0)
    lift = {"crucible": 240, "side_ins": 300, "top_ins": 330, "bottom_ins": 360, "tc": 140, "rod": 260}
    for g in ("crucible", "side_ins", "top_ins", "bottom_ins", "tc", "rod"):
        sc.show(sc.members(g), 0.0)
        sc.gmat[g] = T((0, 0, lift[g]))
    sc.gmat["nozzle"] = T((0, 0, -70))
    sc.show(sc.members("nozzle"), 0.0)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    sc.cam = CAM["machine_near"]
    gauges(sc, t=24, status="furnace cold, power on")

    def open_lid(u):
        hood(sc, 110 * u)

    sc.step("3.1", "Start cold, with the furnace lid open: it hinges up to the left. For a rebuild, everything "
            "comes out: thermocouple, sealing rod, insulation, crucible.", 3.5, open_lid, hold=1.4,
            cam_to=CAM["furnace_top"],
            labels=[lab("furnace lid (bell)", M.HINGE + np.array([-90, 0, 200]), 0.06, 0.20),
                    lab("induction coil, in the\nhalf-cut furnace body", (-47, 0, M.Z_CR + 20), 0.06, 0.45)])

    def nozzle_in(u):
        sc.show(sc.members("crucible"), min(1.0, u * 4))
        sc.show(sc.members("nozzle"), min(1.0, u * 4))
        sc.gmat["nozzle"] = T((0, 0, -70 * (1 - window(u, 0.25, 1.0))))
    sc.step("3.2", "Nozzle into its holder, white side up: Ø0.5 mm is standard, Ø0.7 for Al alloys. "
            "Screw nozzle and holder onto the crucible as a pair, just tight: the thread barely engages.",
            3.5, nozzle_in, hold=1.6,
            labels=[lab("graphite crucible", (-30, -20, M.Z_CR + 240 + 50), 0.06, 0.25),
                    lab("nozzle, white side up", (0, -8, M.CRUCIBLE_BASE + 240 - 3), 0.06, 0.55)])

    def crucible_in(u):
        sc.show(sc.members("bottom_ins"), min(1.0, u * 5))
        sc.gmat["bottom_ins"] = T((0, 0, 360 * (1 - window(u, 0.0, 0.4))))
        w = window(u, 0.35, 1.0)
        sc.gmat["crucible"] = T((0, 0, 240 * (1 - w))) @ R((0, 0, 1), 200 * (1 - w))
    sc.step("3.3", "Graphite seal and bottom insulation in, then the crucible down into the coil. The graphite nut "
            "goes on from below; before it is tight, turn its hole to where you can reach it.", 4.0, crucible_in,
            hold=1.4, labels=[lab("bottom insulation", (60, 0, M.CRUCIBLE_BASE - 12), 0.70, 0.62)])

    def insulation_in(u):
        a, b = window(u, 0.0, 0.55), window(u, 0.45, 1.0)
        sc.show(sc.members("side_ins"), min(1.0, u * 6))
        sc.gmat["side_ins"] = T((0, 0, 300 * (1 - a)))
        sc.show(sc.members("top_ins"), min(1.0, max(0.0, (u - 0.4) * 6)))
        sc.gmat["top_ins"] = T((0, 0, 330 * (1 - b)))
    sc.step("3.4", "Side insulation round the crucible, its hole lined up with the thermocouple port, then the "
            "top insulation (filling cone). Silica-alumina: dusty and fragile, vacuum up afterwards.", 4.0,
            insulation_in, hold=1.4,
            labels=[lab("side insulation", (40.5, 0, M.Z_CR + 40), 0.70, 0.45),
                    lab("top insulation", (75, 0, M.BODY_TOP - 18), 0.70, 0.30)])

    a = math.radians(M.TC_ANGLE)
    tc_pt = np.array([33.1 * math.cos(a), 33.1 * math.sin(a), M.BODY_TOP + 6])

    def tc_in(u):
        sc.show(sc.members("tc"), min(1.0, u * 5))
        sc.gmat["tc"] = T((0, 0, 140 * (1 - u)))
    sc.step("3.5", "Thermocouple (Type N) into the hole in the crucible wall, bent to sit close. Leave it in even "
            "for maintenance, or the HMI raises 'master temperature sensor' and bleeds argon.", 3.0, tc_in,
            hold=1.4, labels=[lab("wall thermocouple", tc_pt + np.array([-30, 20, 0]), 0.06, 0.30)])

    def rod_in(u):
        sc.show(sc.members("rod"), min(1.0, u * 5))
        sc.gmat["rod"] = T((0, 0, 260 * (1 - u)))
    sc.step("3.6", "Sealing rod in BEFORE any metal, its tip clean and smooth or it will not seal. Screw it into "
            "its adapter, pin the adapter to the arm, lower it onto the nozzle.", 3.5, rod_in, hold=1.6,
            labels=[lab("sealing rod", (0, -6, M.Z_CR + 60), 0.70, 0.40),
                    lab("adapter on the holder arm", (40, 18, M.RIM + M.ARM_ABOVE_RIM + 8), 0.70, 0.20)])

    def charge_in(u):
        for k in range(4):
            w = window(u, 0.18 * k, 0.18 * k + 0.45)
            sc.show(sc.members(f"slug{k}"), 1.0 if u > 0.18 * k else 0.0)
            sc.gmat[f"slug{k}"] = T((0, 0, 260 * (1 - w)))
    sc.step("3.7", "Charge: clean rods no thicker than 20 mm, 250–300 g; here 4 × Ø17 × 100 mm "
            "6063 (≈245 g) dropped in round the seated rod. They stand proud and sink as they melt.", 5.0,
            charge_in, hold=1.6, still=True,
            labels=[lab("charge: 4 rods, ≈245 g", (slug_xy(0)[0], slug_xy(0)[1], M.Z_CR + 85), 0.70, 0.62)])

    def close_lid(u):
        hood(sc, 110 * (1 - u))
    sc.step("3.8", "Close the lid and set the latch just tight enough to seal: if it hisses under pressure, loosen "
            "it, adjust the latch and retighten.", 3.5, close_lid, hold=2.0, cam_to=CAM["furnace_sec"])
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
            "with the controls on a blue cabinet and the utilities behind it.", 2.0, None, hold=1.0,
            cam_to=orbit_cam(-118, 24, 4300))
    sc.step("0.2", "On top, the Blue Power furnace: a stainless body holding the coil, crucible and insulation, "
            "under a faceted lid with a window, hinged on the left.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-112, 22, 2600, np.array([20, 120, 1250])),
            labels=[lab("furnace lid (bell)", (-30, -110, 1440), 0.06, 0.22),
                    lab("furnace body", (-90, -100, 1250), 0.06, 0.40)])
    sc.step("0.3", "Controls: the melting control panel (furnace) and the main switch on the cabinet, and the "
            "15.6 in HMI on its swing arm, which runs pressures, gas and ultrasonics.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-82, 18, 2700, np.array([330, 150, 1350])),
            labels=[lab("melting control panel", (337, 200, 1470), 0.06, 0.22),
                    lab("main switch", (345, 190, 1200), 0.06, 0.55),
                    lab("HMI", (600, 60, 1520), 0.74, 0.20)])
    sc.step("0.4", "Below the furnace, the 57 L atomization chamber: a view port at the front, and on the left a "
            "door closed by three clamps.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-118, 16, 2700, np.array([40, 0, 850])),
            labels=[lab("atomization chamber", (200, -120, 800), 0.74, 0.40),
                    lab("view port", M.VIEWPORT + np.array([50, -40, 40]), 0.74, 0.22),
                    lab("door, 3 clamps", (-140, -150, 935), 0.06, 0.30)])
    sc.step("0.5", "The ultrasonic unit rides in the door: transducer under its cover outside, sonotrode and plate "
            "inside, under the furnace nozzle.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-150, 14, 2300, np.array([-120, 0, 760])),
            labels=[lab("ultrasonic unit:\ntransducer under its cover", M.PLATE_C - M.STACK_DIR * 330, 0.06, 0.55)])
    sc.step("0.6", "A cone takes the powder down through a valve to the airlock container, clamped on by its "
            "flange.", 2.4, None, hold=1.2,
            cam_to=orbit_cam(-120, 12, 2300, np.array([40, 0, 520])),
            labels=[lab("chute cone + valve", (M.CHUTE_X - 70, -110, 520), 0.74, 0.40),
                    lab("powder container", (M.CHUTE_X - 40, -88, 280), 0.74, 0.62)])
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
            cam_to=[(-760, -2650, 1020), (40, 0, 830), (0, 0, 1)],
            labels=[lab("crucible + sealing rod", (0, 0, M.Z_CR + 40), 0.06, 0.18),
                    lab("plate on the sonotrode", M.PLATE_C, 0.06, 0.42),
                    lab("powder container", (M.CHUTE_X + M.CONT_R - 2, 0, 280), 0.74, 0.75)])
    return sc.save()


# ------------------------------------------------------------------------------------ 06 pour
def anim_06_pour():
    sc = Scene("06_pour", "6 · Pour and atomize")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, ghost={"stack_cover": 0.35}, hide=UTILITY_NAMES, pipes=False)
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
        k = sc.n % 2
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if (on and k) else 0.0))

    sc.step("6.1", "Melt held at ~800 °C, O₂ at 45 ppm. The pour goes in this order, quickly: vibration "
            "ON, draining pressure, sealing rod UP, turbo as needed.", 3.0, lambda u: show_g(), hold=1.2,
            cam_to=CAM["pour"], labels=[lab("melt, ~800 °C", (-14, 0, M.Z_CR + 20), 0.06, 0.30),
                                        lab("plate", M.PLATE_C, 0.06, 0.72)])

    def us_on(u):
        st["us"], st["amp"] = "40.08 kHz", 90 * u
        vibrate(True)
        show_g()
    sc.step("6.2", "Vibration ON. Amplitude is a percentage of generator current: start about 90 % and adjust; "
            "lower gives finer powder but may stop atomizing.", 2.5, us_on, hold=1.0, live=True)

    def drain(u):
        st["pf"] = 130 + 90 * u
        vibrate(True)
        show_g()
    sc.step("6.3", "Draining pressure: furnace above chamber pushes the melt out. Only the difference matters.",
            2.0, drain, hold=1.0, live=True)

    def rod_up(u):
        sc.gmat["arm"] = T((0, 0, 12 * window(u, 0.0, 0.3)))
        stream(sc, 1.0 if u > 0.3 else 0.0, 1.0, window(u, 0.3, 0.6))
        if 0.6 < u < 0.95 and sc.n % 3 == 0:
            drops.emit_drops(2, M.IMPACT + np.array([0, 0, 3]), M.PLATE_UP * 250 + M.STACK_DIR * 500)
        drops.step()
        vibrate(True)
        show_g()
    sc.step("6.4", "Sealing rod UP: the melt stream falls onto the plate. The first drops usually bounce off: a "
            "cold, dry plate does not wet.", 3.0, rod_up, hold=1.0, live=True, cam_to=CAM["stream"],
            labels=[lab("sealing rod up", (0, -6, M.Z_CR + 70), 0.70, 0.22),
                    lab("melt stream", (0, 0, 1000), 0.70, 0.45)])

    def turbo(u):
        st["pf"] = 220 + (1500 - 220) * (math.sin(math.pi * u))
        stream(sc, 1.0, 1.0 + 0.8 * math.sin(math.pi * u))
        spray.emit_spray(int(18 * window(u, 0.3, 1.0)))
        spray.step()
        drops.step()
        st["level"] -= 0.12
        pool.set(st["level"])
        vibrate(True)
        show_g()
    sc.step("6.5", "A short TURBO push (1.5 bar) heats the plate and clears debris; pouring more at the start is "
            "what makes the plate wet.", 2.5, turbo, hold=1.0, live=True)

    def atomize(u, rate=28, cam=None):
        st["pf"] = 220
        stream(sc, 1.0, 1.0)
        spray.emit_spray(rate)
        spray.step()
        drops.step()
        st["level"] = max(-12.0, st["level"] - 0.085)
        pool.set(st["level"])
        st["made"] += rate
        powder.set(3 + 55 * min(1.0, spray.landed / 5200))
        vibrate(True)
        show_g()
    sc.step("6.6", "Once the plate is hot every drop atomizes: droplets fly off the plate, freeze in the argon and "
            "fall to the cone. Steer with the plate position: land high on it, not over the top.", 6.0, atomize,
            hold=1.0, live=True, labels=[lab("droplets freeze into powder", M.IMPACT + np.array([90, 0, -40]), 0.70, 0.62)])
    sc.step("6.7", "The powder runs down the cone into the container. Too thin a stream gathers and drips; melt "
            "shooting past the plate means the pressure is too high (the Oct 2 lesson).", 6.0, atomize, hold=1.0, live=True,
            cam_to=CAM["chamber"], still=True,
            labels=[lab("powder container", (M.CHUTE_X + M.CONT_R - 2, 0, 300), 0.70, 0.75)])
    sc.step("6.8", "Two to three minutes of attention: amplitude slider, turbo pulses, plate position, with the "
            "operator at the window the whole time.", 6.0, atomize, hold=1.0, live=True)

    def tail(u):
        st["level"] = max(-12.0, st["level"] - 0.2)
        pool.set(st["level"])
        stream(sc, 1.0 if u < 0.6 else 0.0, 1.0 - 0.6 * u)
        if u < 0.6:
            spray.emit_spray(int(20 * (1 - u)))
        spray.step()
        powder.set(3 + 55 * min(1.0, spray.landed / 5200))
        vibrate(True)
        show_g()
    sc.step("6.9", "The crucible runs empty: next, the end-of-pour sequence (step 7).", 3.0, tail, hold=1.5, live=True)
    return sc.save()


# ------------------------------------------------------------------------------- 02 stack
def anim_02_stack():
    sc = Scene("02_stack", "2 \u00b7 Ultrasonic stack: build, torque, scan")
    load_machine(sc, cut=CHAMBER_CUT, hide=UTILITY_NAMES, pipes=False)
    bench = 330.0             # the stack is put together this far out along its axis, then slid in
    for g in ("transducer", "booster", "sonotrode", "plate", "cover"):
        sc.show(sc.members(g), 0.0)
    for g in ("transducer", "booster", "sonotrode"):
        sc.gmat[g] = T(-M.STACK_DIR * bench)
    sc.gmat["plate"] = T(M.STACK_DIR * 140)
    sc.gmat["cover"] = T(-M.STACK_DIR * 520)
    mid = M.PLATE_C - M.STACK_DIR * 330
    cam_side = [tuple(mid + np.array([-120, -1500, 260])), tuple(mid + np.array([0, 0, 40])), (0, 0, 1)]
    cam_in = [tuple(M.PLATE_C + np.array([-260, -900, 160])), tuple(M.PLATE_C - M.STACK_DIR * 120), (0, 0, 1)]
    sc.cam = CAM["machine_near"]
    gauges(sc, status="chamber at atmosphere")

    def transducer_in(u):
        sc.show(sc.members("transducer"), min(1.0, u * 4))
        sc.gmat["transducer"] = T(-M.STACK_DIR * (bench + 160 * (1 - u)))
    sc.step("2.1", "The stack goes transducer \u2192 booster \u2192 sonotrode \u2192 plate. First the transducer: "
            "piezo stack, ~1000 V cable, air-cooled. Never drop it or get it wet.", 3.5, transducer_in, hold=1.2,
            cam_to=cam_side,
            labels=[lab("transducer", M.PLATE_C - M.STACK_DIR * (bench + 320), 0.06, 0.62)])

    def booster_on(u):
        sc.show(sc.members("booster"), min(1.0, u * 4))
        sc.gmat["booster"] = T(-M.STACK_DIR * (bench - 120 * (1 - u))) @ R(M.STACK_DIR, 300 * (1 - u), M.PLATE_C)
        gauges(sc, torque="65 N\u00b7m" if u > 0.9 else "\u2026")
    sc.step("2.2", "Booster onto the transducer, 65 N\u00b7m (M10 fine thread). The 1.5:1 booster mounted in "
            "reverse lowers the amplitude, for finer powder.", 3.0, booster_on, hold=1.2,
            labels=[lab("booster 1.5:1", M.PLATE_C - M.STACK_DIR * (bench + 210), 0.06, 0.40)])

    def sono_on(u):
        sc.show(sc.members("sonotrode"), min(1.0, u * 4))
        sc.gmat["sonotrode"] = T(-M.STACK_DIR * (bench - 120 * (1 - u)))
        gauges(sc, torque="60 N\u00b7m" if u > 0.9 else "\u2026")
    sc.step("2.3", "Sonotrode on, 60 N\u00b7m, isopropanol on the threads. Its KF50 flange is always at the top.",
            3.0, sono_on, hold=1.2,
            labels=[lab("sonotrode, KF50 flange", M.PLATE_C - M.STACK_DIR * (bench + 110), 0.06, 0.25)])

    def stack_in(u):
        for g in ("transducer", "booster", "sonotrode"):
            sc.gmat[g] = T(-M.STACK_DIR * bench * (1 - u))
        gauges(sc, status="stack in the door housing")
    sc.step("2.4", "Splash plate in first (hard to fit later), O-ring checked, door locked open; then slide the "
            "stack into the door's housing and fit both clamps without touching the safety cover.", 3.5, stack_in,
            hold=1.0, labels=[lab("door housing", M.PLATE_C - M.STACK_DIR * 194 + np.array([0, -45, 0]), 0.06,
                                  0.30)])

    def plate_on(u):
        sc.show(sc.members("plate"), min(1.0, u * 4))
        sc.gmat["plate"] = T(M.STACK_DIR * 140 * (1 - u)) @ R(M.STACK_DIR, 360 * (1 - u), M.PLATE_C)
        gauges(sc, torque="50 N\u00b7m" if u > 0.9 else "\u2026")
    sc.step("2.5", "Plate onto its M8 stud with the stack in the housing: 50 N\u00b7m, counter-holding the "
            "sonotrode with a 17 mm wrench.", 3.0, plate_on, hold=1.2, cam_to=cam_in,
            labels=[lab("plate, Ti 20 \u00d7 100", M.PLATE_C + M.PLATE_UP * 30, 0.70, 0.25)])

    def scan(u):
        f = 39.6 + 0.9 * u
        gauges(sc, scan=f"{f:.2f} kHz \u2026" if u < 0.95 else "one wide peak at 40.12 kHz")
    sc.step("2.6", "Advanced ultrasonics \u2192 scan: one wide peak a little over 40 kHz. A double peak? Run a "
            "short burst and rescan.", 3.0, scan, hold=1.4)
    mist = Particles(sc, "mist", (0.35, 0.65, 1.0), size=4.0, slowmo=0.15, seed=5)

    def wet(u):
        if u < 0.7:
            n = 6
            r = mist.rng
            p = M.PLATE_C[None, :] + M.PLATE_UP[None, :] * r.uniform(-45, 45, n)[:, None] \
                + np.array([0, 1.0, 0])[None, :] * r.uniform(1, 9, n)[:, None]
            v = M.STACK_DIR[None, :] * r.uniform(150, 700, n)[:, None] + r.normal(0, 150, (n, 3))
            v[:, 1] = np.abs(v[:, 1])
            mist.p = np.vstack([mist.p, p])
            mist.v = np.vstack([mist.v, v])
        mist.step()
        gauges(sc, us="40.12 kHz", amp=90)
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if sc.n % 2 else 0.0))
    sc.step("2.7", "Wet test: a drop of water should atomize over the whole plate. If only half of it atomizes, "
            "the plate is cracked.", 3.5, wet, hold=1.0, live=True)

    def cover_on(u):
        mist.p = mist.p[:0]
        mist.v = mist.v[:0]
        mist.step()
        sc.gmat["plate"] = np.eye(4)
        sc.show(sc.members("cover"), min(1.0, u * 4))
        sc.gmat["cover"] = T(-M.STACK_DIR * 520 * (1 - u))
        gauges(sc, status="cover on, air + cable locked")
    sc.step("2.8", "Bolt the protective cover over the transducer, then push in and lock the cable and connect "
            "the cooling air: two or three minutes that protect a part worth thousands.", 3.0, cover_on, hold=2.0,
            cam_to=cam_side, still=True,
            labels=[lab("protective cover", M.PLATE_C - M.STACK_DIR * 330 + np.array([0, -50, 0]), 0.06, 0.62)])
    return sc.save()


# ------------------------------------------------------------------------------- 03b chamber
def anim_03b_chamber():
    sc = Scene("03b_chamber", "3b · Chamber: container, splash plate, door")
    ghost = {"chamber": 0.28, "chamber_slots": 0.28, "chute": 0.35, "viewport_glass": 0.4}
    load_machine(sc, ghost=ghost, hide=UTILITY_NAMES, pipes=False)
    door(sc, 100)
    for c in range(3):
        clamp(sc, c, 0.0)
    sc.gmat["container"] = T((0, 0, -260))
    sc.show(sc.members("container"), 0.0)
    sc.gmat["flange_clamp"] = T((0, 0, -30))
    sc.show(sc.members("flange_clamp"), 0.0)
    for g in ("bowl", "splash"):
        sc.show(sc.members(g), 0.0)
        sc.gmat[g] = T((-420, 0, 120))
    sc.cam = CAM["container"]
    gauges(sc, status="chamber open, at atmosphere")

    def cont(u):
        sc.show(sc.members("container"), min(1.0, u * 4))
        sc.gmat["container"] = T((0, 0, -260 * (1 - window(u, 0.1, 0.75))))
        sc.show(sc.members("flange_clamp"), window(u, 0.65, 0.85))
        sc.gmat["flange_clamp"] = T((0, 0, -30 * (1 - window(u, 0.7, 1.0))))
    sc.step("3b.1", "Container on with two people: one lifts it into place under the cone while the other closes "
            "the flange clamp. Finger-tight only.", 4.0, cont, hold=1.4,
            labels=[lab("powder container", (M.CHUTE_X - 60, -70, 260), 0.06, 0.60),
                    lab("flange clamp", (M.CHUTE_X + 84, 0, 431), 0.74, 0.50)])

    def inside(u):
        a, b = window(u, 0.0, 0.55), window(u, 0.45, 1.0)
        sc.show(sc.members("bowl"), 1.0 if u > 0 else 0)
        sc.gmat["bowl"] = T(np.array((-420, 0, 120)) * (1 - a))
        sc.show(sc.members("splash"), 1.0 if u > 0.45 else 0)
        sc.gmat["splash"] = T(np.array((-420, 0, 120)) * (1 - b))
    sc.step("3b.2", "Through the door: catch bowl on the chamber floor and the splash plate above the container "
            "(one is enough for aluminium). Wipe the plate; hang the covers over the openings.", 4.0, inside,
            hold=1.4, cam_to=CAM["chamber"],
            labels=[lab("catch bowl", (M.CHUTE_X + 100, 0, M.CH_Z[0] + 20), 0.74, 0.70),
                    lab("splash plate", (M.CHUTE_X + 70, 0, M.CH_Z[0] + 95), 0.74, 0.52)])

    def shut(u):
        door(sc, 100 * (1 - u))
    sc.step("3b.3", "Run the frequency check now, before closing. Then swing the door shut: the ultrasonic unit "
            "rides in it.", 3.0, shut, hold=1.0, cam_to=CAM["door_out"])

    def clamps(u):
        for c in range(3):
            clamp(sc, c, window(u, 0.25 * c, 0.25 * c + 0.4))
    sc.step("3b.4", "Close all three clamps. Opening one under pressure just leaks.", 3.0, clamps, hold=2.0,
            still=True, labels=[lab("3 door clamps", (M.CH_X[0] - 30, M.CH_Y[0] - 20, 835), 0.74, 0.40)])
    return sc.save()


# ---------------------------------------------------------------------------------- 05 melt
def anim_05_melt():
    sc = Scene("05_melt", "5 · Melt: overshoot to drop the rods, hold at ~800 °C, wait 2 min")
    load_machine(sc, cut=FURNACE_CUT, hide=tuple(n for n in UTILITY_NAMES if n != "air_frl"), pipes=("air",))
    pool = Pool(sc, half=True, level=-30)
    add_gas(sc, half=True, furnace=0.7, chamber=0.0)
    st = dict(t=500.0, set=1000.0)
    sc.cam = CAM["furnace_sec"]

    def show_g(extra=None):
        gauges(sc, furnace=130, chamber=150, o2=45, set=st["set"], t=st["t"], **(extra or {}))
    heat(sc, 500, 1.0)
    show_g()

    def heat_up(u):
        st["t"] = 500 + 350 * u
        heat(sc, st["t"], 1.0)
        show_g()
    sc.step("5.1", "Setpoint 850–1000 °C: long rods heat at the bottom and stay cooler at the top, so "
            "overshoot first. The generator heats the graphite; the graphite heats the charge.", 4.0, heat_up,
            hold=1.0, labels=[lab("coil on (10 kW, 7 kHz)", (-47, 0, M.Z_CR - 28 + 12.5 * 2.5), 0.06, 0.62),
                              lab("charge heating", (slug_xy(1)[0], 0, M.Z_CR + 70), 0.06, 0.28)])

    def cues(u):
        st["t"] = 850 + 30 * u - 12 * math.sin(math.pi * window(u, 0.5, 1.0))
        heat(sc, st["t"], 1.0)
        sc.gmat["rod"] = T((0, 0, -1.5 * u))
        show_g()
    sc.step("5.2", "Melt cues: a small temperature dip as melt reaches the thermocouple, faster induction beeping, "
            "the sealing rod sinking a little, the Al 'jumping' in the middle.", 3.5, cues, hold=1.0)

    def slump(u):
        st["t"] = 870 - 70 * window(u, 0.4, 1.0)
        st["set"] = 1000 - 200 * window(u, 0.3, 0.5)
        for k in range(4):
            x, y = slug_xy(k)
            f = 1 - 0.95 * window(u, 0.05 * k, 0.75 + 0.05 * k)
            sc.gmat[f"slug{k}"] = S((1 + 0.2 * (1 - f), 1 + 0.2 * (1 - f), f), (x, y, M.Z_CR))
            sc.alpha[f"slug{k}"] = 1.0 if f > 0.07 else 0.0
        pool.set(-14 + 50 * window(u, 0.05, 0.95))
        heat(sc, max(st["t"], 760), 1.0)
        show_g()
    sc.step("5.3", "The rods slump into a pool. As soon as they do, bring the setpoint down to 780–800 "
            "°C: the plate will not stand much more.", 5.0, slump, hold=1.2, still=True,
            labels=[lab("melt pool", (-14, 0, M.Z_CR + 20), 0.70, 0.55)])

    def hold2(u):
        st["t"] = 800 - 5 * u
        secs = int(round(120 * (1 - u)))
        show_g({"hold": f"{secs // 60}:{secs % 60:02d}"})
    sc.step("5.4", "Wait 2 minutes once everything is liquid: the crucible-wall thermocouple lags the melt. Any "
            "longer only oxidizes it.", 4.0, hold2, hold=1.0)
    air = Flow(sc, "air", M.AIR_LINE)

    def meanwhile(u):
        air.on = 1.0
        air.step()
        show_g({"status": "transducer air ON, rescan"})
    sc.step("5.5", "Meanwhile: transducer cooling air on, rescan the ultrasonics (scans expire), hearing "
            "protection on, an operator at the window.", 4.0, meanwhile, hold=1.5, live=True, cam_to=CAM["column"],
            labels=[lab("cooling air to the transducer", M.PLATE_C - M.STACK_DIR * 380, 0.06, 0.62)])
    return sc.save()


# ------------------------------------------------------------------------------ 04 gas wash
def anim_04_gas_wash():
    sc = Scene("04_gas_wash", "4 · Gas wash: vacuum and argon, furnace then chamber")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, hide=UTILITY_NAMES, pipes=False)
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
    sc.step("4.1", "Pressure control OFF before any pumping (it holds 150 mbar). Wash one vessel while the other "
            "keeps its overpressure: graphite seals leak, and a leak should pull argon, not air.", 3.0,
            lambda u: show_g(), hold=1.0,
            labels=[lab("furnace (argon)", (60, 60, 1250), 0.70, 0.18),
                    lab("chamber (argon, +150 mbar)", (150, 60, 900), 0.70, 0.40)])

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
    sc.step("4.2", "Furnace wash 1: pump to the gauge floor, about −850 mbar at Provo's altitude (−1000 at "
            "sea level): normal, not a leak. Then argon back in to +150.", 4.0, cycle("furnace", 650), hold=1.0)
    sc.step("4.3", "Furnace washes 2 and 3, same again. O₂ reads nonsense under vacuum: backfill, then read.",
            4.0, cycle("furnace", 380), hold=1.0)
    sc.step("4.3", "Furnace washes 2 and 3, same again. O₂ reads nonsense under vacuum: backfill, then read.",
            3.0, cycle("furnace", 260), hold=1.0)
    sc.step("4.4", "Then the chamber, while the furnace holds its overpressure: pump to the floor, fill with "
            "argon, repeat.", 4.0, cycle("chamber", 120), hold=1.0)
    sc.step("4.5", "Generator on, 250 °C, wash again: the target is moisture in new insulation and crucible, "
            "not the metal.", 4.5, cycle("furnace", 70, 24, 250), hold=1.0,
            labels=[lab("coil on: 250 °C", (-47, 0, M.Z_CR - 28 + 12.5 * 2.5), 0.06, 0.35)])
    sc.step("4.6", "500 °C, wash again. Stop washing once O₂ is low and stable: ≤100 ppm, best "
            "40–50 (the team has seen the low 20s).", 4.5, cycle("furnace", 45, 250, 500), hold=1.0,
            still=True)

    def ready(u):
        st["pf"] = 150 - 20 * u
        st["pump"] = "pressure control ON"
        vac.on = ar.on = 0.0
        vac.step()
        ar.step()
        show_g()
    sc.step("4.7", "Pressure control back ON at melting pressure, the furnace slightly below the chamber "
            "(130 / 150 mbar). Ready to melt.", 2.5, ready, hold=2.0)
    return sc.save()


# --------------------------------------------------------------------------- 07 end, cooldown
def anim_07_end_cooldown():
    sc = Scene("07_end_cooldown", "7 · End of pour, cooldown, open, collect")
    load_machine(sc, cut=FURNACE_CUT + CHAMBER_CUT, ghost={"stack_cover": 0.35}, hide=UTILITY_NAMES, pipes=False)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    pool = Pool(sc, half=True, level=-11)
    powder = Powder(sc, half=True, level=55)
    add_stream(sc)
    add_gas(sc, half=True, furnace=0.7, chamber=0.7)
    spray = Particles(sc, "spray", (0.80, 0.80, 0.84), size=5.0)
    heat(sc, 795, 1.0)
    sc.gmat["arm"] = T((0, 0, 12))
    stream(sc, 1.0, 0.7)
    st = dict(pf=220.0, pc=150.0, t=795.0)
    sc.cam = CAM["pour"]

    def show_g(extra=None):
        gauges(sc, furnace=st["pf"], chamber=st["pc"], t=st["t"], **(extra or {}))
    show_g({"us": "40.08 kHz"})

    def turbo(u):
        st["pf"] = 220 + 1280 * math.sin(math.pi * u)
        pool.set(-11 - 3 * u)
        stream(sc, 1.0 if u < 0.85 else 0.0, 1.2 * (1 - u) + 0.3)
        if u < 0.8:
            spray.emit_spray(10)
        spray.step()
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if sc.n % 2 else 0.0))
        show_g({"us": "40.08 kHz"})
    sc.step("7.1", "Crucible empty: one TURBO push clears the last drops and the nozzle.", 2.5, turbo, hold=1.0, live=True)

    def stop(u):
        sc.gmat["arm"] = T((0, 0, 12 * (1 - window(u, 0.0, 0.3))))
        st["pf"] = 220 - 90 * window(u, 0.2, 0.5)
        heat(sc, 795, 1 - window(u, 0.4, 0.6))
        spray.step()
        on = u < 0.75
        sc.gmat["plate"] = T(M.STACK_DIR * (1.2 if (on and sc.n % 2) else 0.0))
        show_g({"us": "40.08 kHz" if on else "STOP"})
    sc.step("7.2", "Within seconds: sealing rod DOWN, melting pressure, generator STOP, ultrasonics STOP. "
            "Vibrating against solidified metal cracks the plate.", 3.0, stop, hold=1.0,
            labels=[lab("sealing rod down", (0, -6, M.Z_CR + 60), 0.70, 0.22)])

    def cool(u):
        st["t"] = 795 - 395 * u
        pool.set(-11, temp_color(st["t"], cold=(0.62, 0.63, 0.66)))
        spray.step()
        show_g({"status": "cooling, open at ≤400 °C"})
    sc.step("7.3", "Set 250 °C for next time and let it cool. Open at or below 400 °C: above 500 "
            "°C graphite burns in air. Cooling water stays on until about 100 °C.", 4.0, cool, hold=1.0)

    whole = add_whole(sc, CHAMBER_CUT + ("clamp0", "clamp1", "clamp2"))
    halves = [n for n in sc.actors if sc.group_of[n] in CHAMBER_CUT and not n.startswith("w:")
              and n in cut_names(sc)]

    def show_whole(f):
        for n in whole:
            sc.alpha[n] = f
        for n in halves:
            sc.alpha[n] = 1 - f

    def vent(u):
        show_whole(window(u, 0.5, 1.0))
        st["pc"] = 150 * (1 - u)
        st["pf"] = 130 * (1 - u)
        set_gas(sc, furnace=0.7 * (1 - u), chamber=0.7 * (1 - u))
        show_g({"status": "pressure control OFF, VENT"})
    sc.step("7.4", "Pressure control OFF, press VENT. The door stays locked while the pressure is off "
            "atmospheric. Masks and lab coat on.", 3.0, vent, hold=1.0, cam_to=CAM["door_out"])

    def open_door(u):
        for c in range(3):
            clamp(sc, c, 1 - window(u, 0.12 * c, 0.12 * c + 0.3))
        door(sc, 100 * window(u, 0.45, 1.0))
    sc.step("7.5", "Three clamps off, door open. The chamber and cone are water-cooled and wet; the furnace parts "
            "are still hot.", 4.0, open_door, hold=1.0)
    brush = Particles(sc, "brushed", (0.70, 0.71, 0.74), size=5.0, slowmo=0.5, seed=7)

    def brush_down(u):
        show_whole(1 - window(u, 0.0, 0.3))
        if u < 0.7:
            brush.emit_settle(14)
        brush.step()
        powder.set(55 + 8 * u)
    sc.step("7.6", "Brush the plate, bowl, walls and view port down into the container, in a circle, before it "
            "comes off. Let the dust settle before reaching in.", 4.5, brush_down, hold=1.0, live=True, cam_to=CAM["chamber"],
            still=True)

    def take_off(u):
        brush.step()
        sc.gmat["container_valve"] = np.eye(4)
        sc.gmat["flange_clamp"] = T((0, 0, -30 * window(u, 0.3, 0.5)))
        sc.alpha.update({n: 1 - window(u, 0.45, 0.6) for n in sc.members("flange_clamp")
                         if not n.startswith("w:")})
        sc.gmat["container"] = T((0, -420 * window(u, 0.7, 1.0), -70 * window(u, 0.55, 0.7)))
    sc.step("7.7", "Close the container valve first (pull down and across: it is heavier than it looks), brush the "
            "top, release the clamp and lift it off. Argon stays inside, a semi-protective atmosphere.", 4.0,
            take_off, hold=1.0, cam_to=CAM["container"])

    def shutdown(u):
        st["t"] = 400 - 300 * u
        show_g({"status": "~100 °C: utilities off"})
    sc.step("7.8", "Pour onto paper, pick out chunks, sieve, bag, 6-character ID label, photo on GitHub. At about "
            "100 °C: heat exchanger, water, air, argon, power off, in any order.", 3.5, shutdown, hold=2.0)
    return sc.save()


# ----------------------------------------------------------------------------------- 08 clean
def anim_08_clean():
    sc = Scene("08_clean", "8 · Clean and reset")
    load_machine(sc, cut=tuple(g for g in FURNACE_CUT if g != "nozzle") + CHAMBER_CUT, ghost={"stack_cover": 0.35},
                 hide=UTILITY_NAMES, pipes=False)
    for k in range(4):
        sc.show(sc.members(f"slug{k}"), 0.0)
    pool = Pool(sc, half=True, level=-13)
    pool.set(-13, (0.55, 0.56, 0.58))
    door(sc, 100)
    for c in range(3):
        clamp(sc, c, 0.0)
    sc.show(sc.members("container"), 0.0)
    sc.show(sc.members("flange_clamp"), 0.0)
    dust = Particles(sc, "dust", (0.66, 0.67, 0.70), size=5.0, slowmo=0.5, seed=3)
    dust.emit_settle(160)
    dust.p[:, 2] = M.CH_Z[0] + 9
    sc.cam = CAM["chamber"]
    gauges(sc, t=60, status="cold, utilities off")

    def brush(u):
        if u > 0.1:
            dust.step()
    sc.step("8.1", "Same alloy next: open, brush, vacuum. A material change takes about an hour: vacuum, then wipe "
            "everything. Brushes, paper towels and isopropanol only.", 4.0, brush, hold=1.0, live=True)

    def plate_off(u):
        dust.step()
        sc.gmat["plate"] = T(M.STACK_DIR * 160 * window(u, 0.2, 1.0)) @ R(M.STACK_DIR, -400 * window(u, 0, 0.5),
                                                                        M.PLATE_C)
        sc.alpha.update({n: 1 - window(u, 0.8, 1.0) for n in sc.members("plate")})
    dm = R((0, 0, 1), -100, (M.DOOR_HINGE[0], M.DOOR_HINGE[1], 0))
    pw = (dm @ np.append(M.PLATE_C, 1))[:3]
    sc.step("8.2", "Plate off its stud. Never grind or clean it: one plate per alloy, logged (1–3 runs "
            "each). A stainless scraper for stuck particles, never plastic.", 3.5, plate_off, hold=1.0,
            cam_to=[tuple(pw + np.array([-500, -700, 350])), tuple(pw), (0, 0, 1)],
            labels=[lab("plate", pw, 0.06, 0.30)])

    def rod_out(u):
        hood(sc, 110 * window(u, 0.0, 0.4))
        sc.gmat["rod"] = T((0, 0, 260 * window(u, 0.45, 1.0)))
    sc.step("8.3", "Once the furnace can be touched (150 °C is too hot): lid open, sealing rod out. Peel the "
            "slag from the crucible floor, scrape Al off the shaft, keep the tip smooth.", 4.0, rod_out, hold=1.0,
            cam_to=CAM["furnace_top"], labels=[lab("slag on the crucible floor", (-12, 0, M.Z_CR - 8), 0.70, 0.55)])

    def nozzle_check(u):
        w = window(u, 0.0, 0.5)
        for g in ("tc", "top_ins", "side_ins"):
            sc.alpha.update({n: 1 - w for n in sc.members(g)})
        sc.gmat["crucible"] = T((0, 0, 240 * window(u, 0.3, 0.7)))
        sc.alpha["pool"] = sc.alpha["pool#cut"] = 0.0 if u > 0.3 else 1.0
        sc.gmat["nozzle"] = T(NOZZLE_OUT * window(u, 0.7, 1.0))
    sc.step("8.4", "Strip it: thermocouple, insulation, crucible. Nozzle: look through it for light; unclog with "
            "a needle or drill it to Ø0.7; swap it if a new charge would not push through.", 4.0,
            nozzle_check, hold=1.2,
            labels=[lab("nozzle: light through it?", NOZZLE_OUT + np.array([0, 0, M.CRUCIBLE_BASE - 3 + 240]),
                        0.06, 0.55)])

    def rebuild(u):
        w = window(u, 0.0, 0.6)
        sc.gmat["nozzle"] = T(NOZZLE_OUT * (1 - window(u, 0.0, 0.3)))
        sc.gmat["crucible"] = T((0, 0, 240 * (1 - window(u, 0.25, 0.6))))
        for g in ("tc", "top_ins", "side_ins"):
            sc.alpha.update({n: window(u, 0.55, 0.75) for n in sc.members(g)})
        sc.gmat["rod"] = T((0, 0, 260 * (1 - window(u, 0.6, 0.85))))
        hood(sc, 110 * (1 - window(u, 0.8, 1.0)))
    sc.step("8.5", "Reassemble: nozzle, crucible, insulation, thermocouple, rod. Wipe the O-rings; HEPA filter "
            "about every two months (sand tray).", 5.0, rebuild, hold=2.0, still=True,
            cam_to=CAM["furnace_sec"])
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
        sc.gmat["switch"] = R((0, 1, 0), 90 * window(u, 0.4, 0.8), (345, 200, 1195))
        gauges(sc, status="main switch ON" if u > 0.8 else "all off")
    sc.step("1.1", "Breakers and main switch on. Everything else is still off.", 2.5, switch, hold=1.0,
            cam_to=[(-1200, -2600, 1900), (300, 200, 1250), (0, 0, 1)],
            labels=[lab("main switch", (345, 190, 1200), 0.74, 0.50)])
    sc.step("1.2", "Facility chilled water: open the valve only a little (at least 2 L/min, but 'water too cold' "
            "trips below 7–10 °C).", 3.5, run("water_supply", "water_return"), hold=1.0, live=True,
            cam_to=[(2300, -2400, 1900), (500, 400, 600), (0, 0, 1)],
            labels=[lab("chilled water to the coil", (443, 420, 800), 0.06, 0.40)])
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
}

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(ANIMS)):
        ANIMS[name]()

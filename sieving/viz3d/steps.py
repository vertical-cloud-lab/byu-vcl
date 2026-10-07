"""The sieving procedure of docs/sieve-order.md as one 3-D animation, from the CadQuery model in model.py.

    xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py              # out/sieving.gif, out/mp4/sieving.mp4
    PREVIEW=1 xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py    # last frame of each sub-step, /tmp/preview_sieving.png

Same pipeline as #255's ``atomizer-training/viz3d`` (``scene.py`` is a copy of its Scene framework): parts move
along the paths an operator's hands would take them, there is no operator figure, and the stack is cut open only
while the powder is moving through it. The masses in the readouts are an example split of a 50 g batch, not a
measurement: the real yield is whatever the balance says.
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pyvista as pv

import model as M
from scene import FPS, R, Scene, T, ease, lighter, window

STACK_GROUPS = ("pan", "s635", "s230", "s60", "cover")
SX, SY = M.STACK_XY
PX, PY = M.PAPER_C
DENSITY = 1.6            # g/cm3, tapped Al powder (#232)
MESH_AREA = math.pi * (M.MESH_R - 1.0) ** 2 / 100.0     # cm2
JAR_AREA = math.pi * (M.JAR_R - 2.0) ** 2 / 100.0
BATCH = 50.0             # g, example
SPLIT = {"s60": 3.0, "s230": 8.0, "s635": 33.0, "pan": 6.0}      # example, g


def depth(mass_g, area_cm2=MESH_AREA):
    """Layer depth in mm of a mass of powder on an area."""
    return mass_g / DENSITY / area_cm2 * 10.0


CAM = {
    "bench": [(-120.0, -980.0, 560.0), (10.0, 30.0, 50.0), (0, 0, 1)],
    "pour": [(-420.0, -640.0, 330.0), (-170.0, 50.0, 70.0), (0, 0, 1)],
    "paper": [(-230.0, -520.0, 330.0), (-110.0, 30.0, 15.0), (0, 0, 1)],
    "fill": [(-60.0, -520.0, 330.0), (0.0, 10.0, 80.0), (0, 0, 1)],
    "stack": [(40.0, -400.0, 190.0), (70.0, 0.0, 72.0), (0, 0, 1)],
    "stack_cut": [(70.0, -330.0, 120.0), (70.0, 0.0, 66.0), (0, 0, 1)],
    "unstack": [(0.0, -560.0, 330.0), (90.0, 40.0, 70.0), (0, 0, 1)],
    "jars": [(90.0, -640.0, 400.0), (210.0, 50.0, 60.0), (0, 0, 1)],
    "balance": [(160.0, -520.0, 330.0), (280.0, 40.0, 70.0), (0, 0, 1)],
    "final": [(-60.0, -900.0, 520.0), (40.0, 30.0, 50.0), (0, 0, 1)],
}


# --------------------------------------------------------------------------------- helpers
def lab(text, xyz, fx, fy):
    return (text, tuple(float(v) for v in xyz), (fx, fy))


def path(u, pts):
    """Piecewise-linear path through pts, eased per leg; u from 0 to 1 spread evenly over the legs."""
    pts = [np.asarray(p, float) for p in pts]
    n = len(pts) - 1
    k = min(int(u * n), n - 1)
    return pts[k] + (pts[k + 1] - pts[k]) * ease(u * n - k)


def gauges(sc, **kv):
    fmt = {"batch": ("Batch", "{}"), "s60": ("No. 60", "{}"), "s230": ("No. 230", "{}"), "s635": ("No. 635", "{}"),
           "pan": ("Pan", "{}"), "balance": ("Balance", "{}"), "status": ("", "{}")}
    sc.gauges = [(fmt[k][0], fmt[k][1].format(v)) for k, v in kv.items() if v is not None]


def load_parts(sc: Scene, ghost: dict | None = None, hidden=()):
    """Add every model part. Cuttable parts are added twice (whole and halved at y = 0); set_cut() blends them."""
    ms = M.meshes()
    ghost = ghost or {}
    sc.cut_f["*"] = 0.0
    for name, m in ms.items():
        op = ghost.get(name, m["opacity"])
        shown = name not in hidden
        if name == "bench":
            sc.add(name, m["whole"], m["color"], m["group"], ambient=0.95, diffuse=0.05, specular=0.0,
                   smooth_shading=False, shown=shown)
        elif name in ("paper", "trough", "label"):
            sc.add(name, m["whole"], m["color"], m["group"], ambient=0.80, diffuse=0.30, specular=0.0,
                   smooth_shading=False, shown=shown)
        elif m["cut"] and m["half"] is not None:
            sc.add(name, m["half"], m["color"], m["group"], opacity=op, shown=shown)
            if m["half_cut"] is not None:
                sc.add(name + "#cut", m["half_cut"], lighter(m["color"]), m["group"], opacity=op,
                       smooth_shading=False, ambient=0.55, diffuse=0.5, specular=0.0, shown=shown)
            sc.add("w:" + name, m["whole"], m["color"], m["group"], opacity=op, shown=shown)
            sc.cutrole.update({name: "half", name + "#cut": "half", "w:" + name: "whole"})
            sc.cut_f[m["group"]] = 0.0
        else:
            sc.add(name, m["whole"], m["color"], m["group"], opacity=op, shown=shown)
    for g in STACK_GROUPS:
        sc.parent[g] = "stack"
    sc.parent["grit"] = "s60"
    return ms


def set_cut(sc: Scene, f: float, groups=STACK_GROUPS):
    for g in groups:
        sc.cut_f[g] = f


def show_group(sc: Scene, group: str, a: float):
    for n in sc.members(group):
        sc.alpha[n] = a


class Heap:
    """A powder heap from the prebuilt meshes, placed at `pos` in its group's assembled coordinates. With half=True
    it has a halved copy too, blended by the group's cut factor like the sieves."""

    def __init__(self, sc: Scene, name: str, kind: str, group: str, pos, half=False, color=M.POWDER):
        v = M.heap_meshes()
        self.sc, self.name, self.half = sc, name, half
        self.levels, self.meshes = v["levels"][kind], v[kind]
        self.pos = np.asarray(pos, float)
        self.level = None
        style = dict(ambient=0.30, diffuse=0.80, specular=0.15, specular_power=12)
        sc.add(name, self.meshes[0][0].copy(), color, group, **style)
        if half:
            sc.add("h:" + name, self.meshes[0][1].copy(), color, group, **style)
            sc.add("h:" + name + "#cut", self.meshes[0][2].copy(), lighter(color), group, smooth_shading=False,
                   ambient=0.55, diffuse=0.5, specular=0.0)
            sc.cutrole.update({name: "whole", "h:" + name: "half", "h:" + name + "#cut": "half"})
        self.set(0.0, shown=False)

    def set(self, level: float, shown=True):
        i = int(np.argmin(np.abs(self.levels - level)))
        if i != self.level:
            body, hb, hc = self.meshes[i]
            self.sc.set_mesh(self.name, body.translate(self.pos, inplace=False))
            if self.half:
                self.sc.set_mesh("h:" + self.name, hb.translate(self.pos, inplace=False))
                self.sc.set_mesh("h:" + self.name + "#cut", hc.translate(self.pos, inplace=False))
            self.level = i
        a = 1.0 if shown and level > 0.05 else 0.0
        self.sc.alpha[self.name] = a
        if self.half:
            self.sc.alpha["h:" + self.name] = a
            self.sc.alpha["h:" + self.name + "#cut"] = a


class Drops:
    """Powder in motion: points rendered as spheres, falling in slow motion until they reach their floor."""

    def __init__(self, sc: Scene, name: str, color=M.POWDER, size=4.0, slowmo=0.30, seed=1):
        self.sc, self.name, self.slowmo = sc, name, slowmo
        self.rng = np.random.default_rng(seed)
        self.p = np.zeros((0, 3))
        self.v = np.zeros((0, 3))
        self.floor = np.zeros(0)
        self.axis = None          # (x, y, r): keep particles inside a vertical cylinder (a sieve frame, a jar)
        self.landed = 0
        sc.add(name, pv.PolyData(np.array([[0.0, 0.0, -500.0]])), color, "static", render_points_as_spheres=True,
               point_size=size, ambient=0.45, smooth_shading=False)

    def emit(self, n, pos, vel, floor, spread=(2.0, 2.0, 1.0), vspread=25.0, y_min=None):
        if n <= 0:
            return
        p = np.asarray(pos, float)[None, :] + self.rng.normal(0, 1, (n, 3)) * np.asarray(spread, float)
        if y_min is not None:
            p[:, 1] = np.maximum(p[:, 1], y_min)
        v = np.asarray(vel, float)[None, :] + self.rng.normal(0, vspread, (n, 3))
        self.p, self.v = np.vstack([self.p, p]), np.vstack([self.v, v])
        self.floor = np.concatenate([self.floor, np.full(n, float(floor))])

    def step(self):
        if len(self.p):
            h = self.slowmo / FPS
            self.v[:, 2] -= 9810 * h
            self.v *= (1 - 1.2 * h)
            self.p += self.v * h
            if self.axis is not None:
                x, y, r = self.axis
                off = self.p[:, :2] - np.array([x, y])
                d = np.linalg.norm(off, axis=1) + 1e-9
                k = np.minimum(1.0, r / d)
                self.p[:, :2] = np.array([x, y]) + off * k[:, None]
            gone = self.p[:, 2] <= self.floor
            self.landed += int(gone.sum())
            self.p, self.v, self.floor = self.p[~gone], self.v[~gone], self.floor[~gone]
        pts = self.p if len(self.p) else np.array([[0.0, 0.0, -500.0]])
        self.sc.set_mesh(self.name, pv.PolyData(pts.copy()))
        self.sc.alpha[self.name] = 1.0 if len(self.p) else 0.0


def rim_point(side=-1.0, z=None):
    """A point on a sieve's rim (assembled coordinates), on the -x side by default."""
    return np.array([SX + side * (M.SIEVE_OD / 2 - 1.0), SY, z])


def tip_matrix(group_rim: np.ndarray, target: np.ndarray, ang: float):
    """Carry a sieve so that `group_rim` (a point on its rim) sits at `target`, then tip it `ang` degrees about the
    bench-parallel y axis through that point (the far side goes up and over, the rim point stays put)."""
    return T(target - group_rim) @ R((0, 1, 0), ang, group_rim)


# ------------------------------------------------------------------------------- the animation
def anim_sieving():
    sc = Scene("sieving", "Sieving atomized powder: 3 in stack, No. 60 / 230 / 635 (#222)")
    sc.cam = CAM["bench"]
    load_parts(sc, hidden=("trough", "label", "doser_tube", "doser_band", "doser_cap", "funnel", "lid_coarse",
                           "lid_print", "lid_fines")
               + tuple(f"chunk{k}" for k in range(7)) + tuple(f"grit{k}" for k in range(9)))
    chunk_groups = [f"chunk{k}" for k in range(7)]
    M.parts()                     # fills M.CHUNK_POS (the meshes come from the cache)
    rng = np.random.default_rng(2)
    chunk_targets = []
    for c in M.CHUNK_POS:
        a, rr = rng.uniform(0, 2 * math.pi), rng.uniform(0, 19)
        tgt = np.array([M.DISH_XY[0] + rr * math.cos(a), M.DISH_XY[1] + rr * math.sin(a), 1.2 + 2.2])
        chunk_targets.append(tgt - (np.array([PX, PY, 0.3]) + c))
    # powder: a cone on the paper, a layer on each mesh and in the pan, and a layer in each jar
    cone = Heap(sc, "heap_paper", "cone", "paper", (PX, PY, 0.3))
    heaps = {"s60": Heap(sc, "heap_s60", "disc", "s60", (SX, SY, M.MESH_Z["s60"] + 0.3), half=True),
             "s230": Heap(sc, "heap_s230", "disc", "s230", (SX, SY, M.MESH_Z["s230"] + 0.3), half=True),
             "s635": Heap(sc, "heap_s635", "disc", "s635", (SX, SY, M.MESH_Z["s635"] + 0.3), half=True),
             "pan": Heap(sc, "heap_pan", "disc", "pan", (SX, SY, M.MESH_Z["pan"] + 0.1), half=True)}
    jars = {"coarse": Heap(sc, "heap_jar_coarse", "jar", "jar_coarse", (*M.JAR_COARSE_XY, 2.0)),
            "print": Heap(sc, "heap_jar_print", "jar", "jar_print", (*M.JAR_PRINT_XY, M.BAL_PAN_Z + 4.0)),
            "fines": Heap(sc, "heap_jar_fines", "jar", "jar_fines", (*M.JAR_FINES_XY, 2.0))}
    drops = Drops(sc, "drops", size=4.0, seed=3)
    bits = Drops(sc, "bits", color=M.CHUNK, size=7.0, slowmo=0.30, seed=5)
    # the container stands beside the paper; its mouth (the top tube's centre) and the direction to the paper
    cx, cy = M.CONT_XY
    mouth = np.array([cx, cy, M.CONT_H + 26.0])
    to_paper = np.array([PX - cx, PY - cy, 0.0])
    to_paper /= np.linalg.norm(to_paper)
    tilt_axis = np.array([-to_paper[1], to_paper[0], 0.0])     # horizontal, perpendicular: the top tips towards the paper
    mouth_target = np.array([PX, PY, 0.0]) - to_paper * 58.0 + np.array([0.0, 0.0, 92.0])
    gauges(sc, batch=f"{BATCH:.0f} g (example)", status="after a run: the container, opened cold")

    # 1 · pour out -------------------------------------------------------------------------------------------
    def pour(u):
        w = window(u, 0.0, 0.42)
        lift = path(w, [mouth, mouth + (0, 0, 70), mouth_target + (0, 0, 40), mouth_target])
        ang = 118.0 * window(u, 0.30, 0.62)
        sc.gmat["container"] = T(lift - mouth) @ R(tilt_axis, ang, mouth)
        if 0.52 < u < 0.97:
            lip = mouth_target + to_paper * 48.0 - (0, 0, 6.0)
            drops.emit(int(round(14 * (15 / FPS))), lip, to_paper * 160.0 + (0, 0, -120.0), 0.6,
                       spread=(4.0, 4.0, 2.0))
        cone.set(window(u, 0.55, 0.98))
        drops.step()
        if u > 0.93:
            for g in chunk_groups:
                show_group(sc, g, (u - 0.93) / 0.07)
    sc.step("1 · pour out", "After a run, with the dust settled: tip the powder container out onto a sheet of paper. "
            "Bartosz's practice (T2 50:51). The heap is mostly spheres with unatomized pieces in it.", 4.5, pour,
            hold=1.2, cam_to=CAM["pour"], live=True,
            labels=[lab("powder container (size assumed, #255)", mouth + (0, 0, -60), 0.06, 0.30),
                    lab("letter sheet", (PX + 60, PY - 80, 0), 0.60, 0.80)])

    # 2 · pick out the pieces ---------------------------------------------------------------------------------
    def pick(u):
        w = window(u, 0.0, 0.5)
        back = path(w, [mouth_target, mouth_target + (0, 0, 50), mouth + (0, 0, 70), mouth])
        sc.gmat["container"] = T(back - mouth) @ R(tilt_axis, 118.0 * (1 - window(u, 0.0, 0.35)), mouth)
        for k, (g, d) in enumerate(zip(chunk_groups, chunk_targets)):
            v = window(u, 0.20 + 0.07 * k, 0.55 + 0.07 * k)
            sc.gmat[g] = T(path(v, [(0, 0, 0), (d[0] * 0.5, d[1] * 0.5, 70.0), d]))
        drops.step()
    sc.step("2 · pieces out", "Pick the pieces out by hand: splats, beads and anything over a few millimetres go to "
            "the dish. They are feedstock again (TA 04:50), not waste.", 3.5, pick, hold=1.2, cam_to=CAM["paper"],
            labels=[lab("pieces: back into the next charge", (*M.DISH_XY, 14), 0.55, 0.22)])

    # 3 · fold the paper and fill the top sieve --------------------------------------------------------------
    # the cover's parking place on the bench, as a translation from where it sits on the stack
    cover_delta = np.array([95.0, -60.0, -(M.TOP_RIM_Z - M.COVER_SKIRT) + 0.5])
    trough_end = np.array([PX + M.PAPER_W / 2, PY, 0.0])        # the +x end of the fold, which goes over the sieve
    trough_target = np.array([SX - 6.0, SY, M.TOP_RIM_Z + 16.0])
    full_s60 = depth(BATCH)

    def fill(u):
        a = window(u, 0.0, 0.22)
        sc.alpha["paper"] = 1.0 - a
        show_group(sc, "trough", a)
        cone.set(1.0 - window(u, 0.42, 0.90))
        w = window(u, 0.18, 0.48)
        sc.gmat["cover"] = T(path(w, [(0, 0, 0), (0, 0, 55), cover_delta + (0, 0, 50), cover_delta]))
        v = window(u, 0.22, 0.52)
        carry = path(v, [trough_end, trough_end + (0, 0, 120), trough_target + (-30, 0, 30), trough_target])
        tilt = 24.0 * window(u, 0.40, 0.60)
        sc.gmat["trough"] = T(carry - trough_end) @ R((0, 1, 0), tilt, trough_end)
        if 0.44 < u < 0.90:
            drops.axis = (SX, SY, M.MESH_R - 1.5)
            drops.emit(int(round(16 * (15 / FPS))), trough_target + (14.0, 0, 8.0), (90.0, 0, -60.0),
                       M.MESH_Z["s60"] + 0.5, spread=(3.0, 6.0, 2.0))
        heaps["s60"].set(full_s60 * window(u, 0.50, 0.95))
        drops.step()
    sc.step("3 · into the No. 60", "Fold the sheet and slide the powder into the top sieve, the No. 60 (250 µm): it "
            "scalps what the hand missed and keeps the fine meshes safe. 50 g is a 7.7 mm bed on a 3 in mesh.", 5.5,
            fill, hold=1.2, cam_to=CAM["fill"], live=True,
            labels=[lab("No. 60 (250 µm)", (SX + 38, SY, M.MESH_Z["s60"] + 14), 0.70, 0.30),
                    lab("No. 230 (63 µm)", (SX + 38, SY, M.MESH_Z["s230"] + 14), 0.70, 0.46),
                    lab("No. 635 (20 µm)", (SX + 38, SY, M.MESH_Z["s635"] + 14), 0.70, 0.62),
                    lab("pan", (SX + 38, SY, 20), 0.70, 0.78)])

    def lid_on(u):
        show_group(sc, "trough", 1.0 - window(u, 0.0, 0.3))
        sc.alpha["paper"] = window(u, 0.2, 0.5)
        w = window(u, 0.0, 0.8)
        sc.gmat["cover"] = T(path(w, [cover_delta, cover_delta + (0, 0, 60), (0, 0, 60),
                                      (0, 0, 0)]))
        drops.axis = None
        drops.step()
    sc.step("3 · cover on", "Cover on before anything is shaken. Fine aluminium is a combustible dust and the "
            "cover is the containment.", 2.0, lid_on, hold=1.0, cam_to=CAM["stack"],
            labels=[lab("cover", (SX, SY, M.TOP_RIM_Z + 8), 0.68, 0.22)])

    # 4 · sieve -------------------------------------------------------------------------------------------------
    sieve_s = 7.0
    final = {k: depth(SPLIT[k]) for k in ("s60", "s230", "s635", "pan")}

    def sieve(u):
        t = u * sieve_s
        amp = 5.0
        wob = (amp * math.cos(2 * math.pi * 2.2 * t), amp * math.sin(2 * math.pi * 2.2 * t), 0.0)
        tap = 1.6 if (int(t * FPS) % int(round(0.6 * FPS))) == 0 else 0.0
        sc.gmat["stack"] = T((wob[0], wob[1], tap))
        set_cut(sc, window(u, 0.0, 0.18))
        k = window(u, 0.12, 0.96)
        heaps["s60"].set(full_s60 + (final["s60"] - full_s60) * k)
        heaps["s230"].set(final["s230"] * min(1.0, k * 1.25))
        heaps["s635"].set(final["s635"] * k)
        heaps["pan"].set(final["pan"] * max(0.0, (k - 0.15) / 0.85))
        show_group(sc, "grit", window(u, 0.70, 0.95))
        if 0.12 < u < 0.95:
            rate = int(round(9 * (15 / FPS)))
            drops.axis = (SX, SY, M.MESH_R - 2.0)
            for src, dst in (("s60", "s230"), ("s230", "s635"), ("s635", "pan")):
                for _ in range(rate):
                    a, rr = drops.rng.uniform(0, math.pi), drops.rng.uniform(0, M.MESH_R - 4)
                    pos = (SX + rr * math.cos(a), SY + abs(rr * math.sin(a)) + 2.0, M.MESH_Z[src] - 0.8)
                    drops.emit(1, pos, (0, 0, -30.0), M.MESH_Z[dst] + 0.4 + heaps[dst].levels[heaps[dst].level or 0],
                               spread=(0.5, 0.5, 0.3), vspread=8.0, y_min=SY + 1.5)
        drops.step()
        gauges(sc, batch=f"{BATCH:.0f} g (example)", s60=f"{BATCH + (SPLIT['s60'] - BATCH) * k:.0f} g",
               s230=f"{SPLIT['s230'] * k:.0f} g", s635=f"{SPLIT['s635'] * k:.0f} g", pan=f"{SPLIT['pan'] * k:.0f} g",
               status="sieving by hand, 3 min")
    sc.step("4 · sieve", "Rotate the stack in a flat circle and tap the frame with the other hand, about 3 minutes. "
            "Cut open here: pieces stay on the No. 60, 63-250 µm on the No. 230, the 20-63 µm print fraction on "
            "the No. 635, dust in the pan. The fine meshes blind: tap, and do 10-20 g at a time.", sieve_s, sieve,
            hold=1.6, cam_to=CAM["stack_cut"], live=True, still=True,
            labels=[lab("20-63 µm: the print fraction", (SX + 20, SY + 10, M.MESH_Z["s635"] + 6), 0.66, 0.60),
                    lab("< 20 µm: dust, flows badly", (SX + 20, SY + 10, 8), 0.66, 0.80)])

    # 5 · unstack and weigh --------------------------------------------------------------------------------------
    rest60 = np.array([SX + 100.0, SY - 60.0, M.SIEVE_H])
    dish_target = np.array([M.DISH_XY[0] - 20.0, M.DISH_XY[1], 46.0])
    rim60 = rim_point(-1.0, M.MESH_Z["s60"] + M.STACKED_H)

    def unstack1(u):
        sc.gmat["stack"] = T((0, 0, 0))
        set_cut(sc, 1.0 - window(u, 0.0, 0.25))
        w = window(u, 0.15, 0.45)
        sc.gmat["cover"] = T(path(w, [(0, 0, 0), (0, 0, 60), cover_delta + (0, 0, 60), cover_delta]))
        v = window(u, 0.35, 0.75)
        carry = path(v, [rim60, rim60 + (0, 0, 90), dish_target + (40, 0, 40), dish_target])
        ang = -150.0 * window(u, 0.70, 0.90)
        sc.gmat["s60"] = tip_matrix(rim60, carry, ang)
        if 0.76 < u < 0.92:
            show_group(sc, "grit", 0.0)
            heaps["s60"].set(0.0)
            bits.emit(int(round(3 * (15 / FPS))), dish_target + (-6, 0, -4), (-40.0, 0, -40.0), 3.0,
                      spread=(4.0, 6.0, 2.0), vspread=15.0)
        bits.step()
        drops.step()
        gauges(sc, batch=f"{BATCH:.0f} g (example)", s60=f"{SPLIT['s60']:.0f} g", s230=f"{SPLIT['s230']:.0f} g",
               s635=f"{SPLIT['s635']:.0f} g", pan=f"{SPLIT['pan']:.0f} g", status="unstacking")
    sc.step("5 · unstack", "Cover off, then the No. 60: what it held joins the pieces in the dish.", 5.0, unstack1,
            hold=1.0, cam_to=CAM["unstack"], live=True)

    funnel_home = np.array([M.JAR_COARSE_XY[0], M.JAR_COARSE_XY[1], 0.0])
    rim230 = rim_point(-1.0, M.MESH_Z["s230"] + M.STACKED_H)
    over_coarse = np.array([M.JAR_COARSE_XY[0] - 12.0, M.JAR_COARSE_XY[1], M.JAR_H + 60.0])

    def unstack2(u):
        sc.gmat["s60"] = tip_matrix(rim60, path(window(u, 0.0, 0.3), [dish_target, dish_target + (60, -80, 40),
                                                                        rest60 + (0, 0, 60), rest60]), 0.0)
        show_group(sc, "funnel", window(u, 0.0, 0.15))
        v = window(u, 0.25, 0.62)
        carry = path(v, [rim230, rim230 + (0, 0, 70), over_coarse + (40, 0, 40), over_coarse])
        ang = -150.0 * window(u, 0.60, 0.80)
        sc.gmat["s230"] = tip_matrix(rim230, carry, ang)
        if 0.66 < u < 0.92:
            heaps["s230"].set(final["s230"] * (1 - window(u, 0.66, 0.90)))
            drops.axis = (M.JAR_COARSE_XY[0], M.JAR_COARSE_XY[1], M.JAR_R - 3.0)
            drops.emit(int(round(10 * (15 / FPS))), over_coarse + (6, 0, -6), (10.0, 0, -80.0), 3.0,
                       spread=(3.0, 3.0, 2.0), vspread=12.0)
        jars["coarse"].set(depth(SPLIT["s230"], JAR_AREA) * window(u, 0.72, 0.96))
        drops.step()
        bits.step()
    sc.step("5 · No. 230", "The No. 230 next, through the funnel into its own jar: 63-250 µm, too coarse for the "
            "bed. Keep it; it can be re-atomized (E6 in #222).", 5.0, unstack2, hold=1.0, cam_to=CAM["jars"],
            live=True, labels=[lab("63-250 µm", (*M.JAR_COARSE_XY, 40), 0.30, 0.30)])

    rest230 = np.array([SX + 100.0, SY + 70.0, M.SIEVE_H])
    rim635 = rim_point(-1.0, M.MESH_Z["s635"] + M.STACKED_H)
    over_print = np.array([M.JAR_PRINT_XY[0] - 12.0, M.JAR_PRINT_XY[1], M.BAL_PAN_Z + 2.0 + M.JAR_H + 60.0])
    funnel_print = np.array([M.JAR_PRINT_XY[0], M.JAR_PRINT_XY[1], M.BAL_PAN_Z + 2.0])

    def unstack3(u):
        sc.gmat["s230"] = tip_matrix(rim230, path(window(u, 0.0, 0.28), [over_coarse, over_coarse + (0, 0, 40),
                                                                          rest230 + (0, 0, 60), rest230]), 0.0)
        f = window(u, 0.05, 0.32)
        sc.gmat["funnel"] = T(path(f, [(0, 0, 0), (0, 0, 60), funnel_print - funnel_home + (0, 0, 60),
                                       funnel_print - funnel_home]))
        v = window(u, 0.25, 0.62)
        carry = path(v, [rim635, rim635 + (0, 0, 70), over_print + (40, 0, 40), over_print])
        ang = -150.0 * window(u, 0.60, 0.80)
        sc.gmat["s635"] = tip_matrix(rim635, carry, ang)
        if 0.66 < u < 0.94:
            heaps["s635"].set(final["s635"] * (1 - window(u, 0.66, 0.92)))
            drops.axis = (M.JAR_PRINT_XY[0], M.JAR_PRINT_XY[1], M.JAR_R - 3.0)
            drops.emit(int(round(12 * (15 / FPS))), over_print + (6, 0, -6), (10.0, 0, -80.0), M.BAL_PAN_Z + 5.0,
                       spread=(3.0, 3.0, 2.0), vspread=12.0)
        k = window(u, 0.72, 0.97)
        jars["print"].set(depth(SPLIT["s635"], JAR_AREA) * k)
        drops.step()
        bits.step()
        gauges(sc, batch=f"{BATCH:.0f} g (example)", balance=f"{SPLIT['s635'] * k:5.1f} g",
               status="tared with the empty jar")
    sc.step("5 · No. 635", "The No. 635 holds the print fraction, 20-63 µm. It goes through the funnel into a jar "
            "already tared on the balance. Weigh every fraction: the yield says how many runs a print needs.", 5.5,
            unstack3, hold=1.4, cam_to=CAM["balance"], live=True,
            labels=[lab("20-63 µm: print fraction", (M.JAR_PRINT_XY[0], M.JAR_PRINT_XY[1] - 30, M.BAL_PAN_Z + 50),
                        0.26, 0.26)])

    rest635 = np.array([SX + 170.0, SY + 130.0, M.SIEVE_H])
    rim_pan = rim_point(-1.0, M.PAN_H)
    over_fines = np.array([M.JAR_FINES_XY[0] - 12.0, M.JAR_FINES_XY[1], M.JAR_H + 60.0])
    funnel_fines = np.array([M.JAR_FINES_XY[0], M.JAR_FINES_XY[1], 0.0])

    def unstack4(u):
        sc.gmat["s635"] = tip_matrix(rim635, path(window(u, 0.0, 0.28), [over_print, over_print + (0, 0, 40),
                                                                          rest635 + (0, 0, 60), rest635]), 0.0)
        f = window(u, 0.05, 0.32)
        sc.gmat["funnel"] = T(path(f, [funnel_print - funnel_home, funnel_print - funnel_home + (0, 0, 60),
                                       funnel_fines - funnel_home + (0, 0, 60), funnel_fines - funnel_home]))
        v = window(u, 0.25, 0.62)
        carry = path(v, [rim_pan, rim_pan + (0, 0, 70), over_fines + (40, 0, 40), over_fines])
        ang = -150.0 * window(u, 0.60, 0.80)
        sc.gmat["pan"] = tip_matrix(rim_pan, carry, ang)
        if 0.66 < u < 0.92:
            heaps["pan"].set(final["pan"] * (1 - window(u, 0.66, 0.90)))
            drops.axis = (M.JAR_FINES_XY[0], M.JAR_FINES_XY[1], M.JAR_R - 3.0)
            drops.emit(int(round(8 * (15 / FPS))), over_fines + (6, 0, -6), (10.0, 0, -80.0), 3.0,
                       spread=(3.0, 3.0, 2.0), vspread=12.0)
        jars["fines"].set(depth(SPLIT["pan"], JAR_AREA) * window(u, 0.72, 0.96))
        drops.step()
        bits.step()
    sc.step("5 · pan", "The pan last: under 20 um is dust. It flows badly on a bed and it is the fraction most "
            "likely to go airborne, so it gets its own closed jar, not the bin.", 4.5, unstack4, hold=1.0,
            cam_to=CAM["jars"], live=True, labels=[lab("< 20 µm", (*M.JAR_FINES_XY, 40), 0.60, 0.72)])

    # 6 · lids, label, and on to the doser ----------------------------------------------------------------------
    rest_pan = np.array([SX + 170.0, SY - 110.0, M.PAN_H])

    def finish(u):
        sc.gmat["pan"] = tip_matrix(rim_pan, path(window(u, 0.0, 0.25), [over_fines, over_fines + (0, 0, 40),
                                                                         rest_pan + (0, 0, 60), rest_pan]), 0.0)
        f = window(u, 0.0, 0.25)
        sc.gmat["funnel"] = T(path(f, [funnel_fines - funnel_home, funnel_fines - funnel_home + (0, 0, 80),
                                       (0, 0, 80), (0, 0, 0)]))
        show_group(sc, "funnel", 1.0 - window(u, 0.2, 0.3))
        for j in ("coarse", "print", "fines"):
            w = window(u, 0.25, 0.55)
            sc.gmat[f"lid_{j}"] = T((0, 0, 70.0 * (1 - w)))
            show_group(sc, f"lid_{j}", 1.0 if u > 0.25 else 0.0)
        show_group(sc, "label", window(u, 0.55, 0.70))
        show_group(sc, "doser", window(u, 0.70, 0.90))
        drops.step()
        bits.step()
    sc.step("6 · label, store, dose", "Lids on, a 6-character ID on the print jar (#249), and the jar lives in the "
            "desiccant box. The 20-63 µm jar is what feeds the doser's 25 mm cartridge: the Sep 30 clog was "
            "unsieved powder.", 4.5, finish, hold=2.0, cam_to=CAM["final"],
            labels=[lab("doser cartridge, Ø25 mm tube", (M.DOSER_XY[0], M.DOSER_XY[1] - 14, 60), 0.72, 0.62),
                    lab("6-character ID (#249)", (M.JAR_PRINT_XY[0], M.JAR_PRINT_XY[1] - 26, M.BAL_PAN_Z + 36), 0.72,
                        0.30)])
    for j in ("coarse", "print", "fines"):
        show_group(sc, f"lid_{j}", 1.0)
    return sc.save()


ANIMS = {"sieving": anim_sieving}

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(ANIMS)):
        ANIMS[name]()

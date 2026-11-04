"""The whole lab set up from scratch (#303, round 4), on the warehouse floor of ``warehouse.py``: an empty bay; the
layout taped on the floor; the utilities; the VLM assembled; the floor machines moved in; the UR10e arms installed on
their MiR250s; every tray loaded, A to I; the cameras; a closing orbit.

    xvfb-run -a python3 setup_lab.py            # -> out/setup_lab.gif, out/mp4/setup_lab.mp4, out/setup_lab_still.png
    PREVIEW=1 xvfb-run -a python3 setup_lab.py  # the last frame of each sub-step -> /tmp/preview_setup_lab.png
    python3 setup_lab.py fit                    # what loads where, and whether each item fits its tray

What gets loaded is data: ``TRAY_ITEMS`` (tray -> [(key, x, y)]), ``warehouse.STATIONS`` for the floor, and
``ROUND4_TRAY`` for the instruments that other modules add. A key that ``tour.load()`` doesn't return is skipped, so the
same script renders today's lab and, once those modules are merged, the full one. The cameras come from ``services.py``
when it provides ``CAMERA_HOOK``'s function; until then stand-ins are drawn and the caption says so.

Everything here that isn't a maker's figure is a layout choice: the cable trays, drops and the argon line, the cameras
and where they sit. Kardex's 208 V three-phase supply is #53's. Installing the arm follows UR's manual (four M8 bolts at
20 Nm, two 8 mm pins for re-mounting; UR10e user manual SW5.26, 6.1).

Trays G-I (``fab_trays.py``: resin printing, PCB assembly, desktop LPBF) need room the 3950 mm Shuttle of #53 doesn't
have: its six 800 mm slots hold A-F. So in this scene, and only here, the Shuttle is assumed 500 mm taller, 4450 mm
(``UNIT_H``). Kardex builds the XP 250/500 from 2550 to 30 050 mm in 100 mm steps and can change a unit's height after it
is built (Shuttle XP brochure, "Technical data" and "Flexible and modular design"); #53's 13 ft is that room's ceiling,
and this warehouse's racking alone is 16 ft. That adds a top slot to each column, for G and I. H, the shortest, goes in
the front column under the opening, which the 3950 mm unit already has. Every other scene keeps the 3950 mm unit.
"""
from __future__ import annotations

import math
import pickle
import sys

import numpy as np
import pyvista as pv

import animate as A
import lab
import line
import props as P
import tour
import vlm as V
import warehouse as W
from scene import FPS, OUT, PREVIEW, Scene, T, R, window

TITLE = "Vertical cloud lab, set up from scratch"

# ================================================================================================ what goes where
# Trays: {tray: [(instrument key, x, y)]} in the tray's frame (centre of its floor, y to the back), as animate.LOADS.
# A-C are round 2's (animate.LOADS, built by animate.Lab), D-F round 3's (line.TRAY_LOADS).
TRAY_ITEMS = {**{k: list(v) for k, v in A.LOADS.items()}, **{k: list(v) for k, v in line.TRAY_LOADS.items()}}
# Round 4's tray instruments, from the modules other agents are writing (tour.MODULES). These spots were picked before
# the models existed: run `python3 setup_lab.py fit` after merging and move anything that overlaps or is too tall. A
# key tour.load() doesn't return is skipped. To use a new tray, add it here and give it a slot in NEW_TRAYS.
# An item is (key, x, y) or (key, x, y, turn): (x, y) is the centre of its box, y None puts its front 30 mm behind the
# tray's front lip (as fab_trays.LOADS), and turn is degrees about z.
ROUND4_TRAY: dict[str, list[tuple]] = {
    # placed after merging, from `setup_lab.py fit`: no overlaps, every item inside its tray's rim
    "A": [("cubxl_corrosion", -300.0, -114.5)],                          # tray A's CubXL, set up for corrosion
    "C": [("vhx", 860.0, 0.0)],                                          # beside the A1 mini
    # no "D": the OpenFlexure array is in line.TRAY_LOADS["D"] itself now, at (792, -148), so it comes in with D-F
    "F": [("sieve", -990.0, 0.0), ("xrf", 876.0, 0.0)],
    # trays G-I as fab_trays.LOADS lays them out (fab_tour.load()'s models, FAB_KEYS); `fit` passes them as they are
    "G": [("form4", -920.0, None), ("form4", -470.0, None), ("form_wash", -40.0, None), ("form_cure", 360.0, None)],
    "H": [("stencil", -640.0, 0.0, 90.0), ("lumenpnp", 400.0, 0.0)],     # the stencil printer is 903 deep: turned
    "I": [("snowpod", -500.0, None), ("snowpod", 300.0, None)],
}
FAB_KEYS = {it[0] for k in "GHI" for it in ROUND4_TRAY[k]}               # loaded with fab_tour.load(), not tour.load()
# Round 4 replaces a round-2 item: the CubXL on tray A is the corrosion set-up (instruments_lab.cubxl_corrosion). (Tray
# D's two freestanding OpenFlexures were replaced here by the array too, until line.TRAY_LOADS made the same swap.)
REPLACED = {"A": ["cubxl"]}
for _k, _keys in REPLACED.items():
    TRAY_ITEMS[_k] = [it for it in TRAY_ITEMS[_k] if it[0] not in _keys]
# Trays beyond A-F: tray -> (slot, role). A-F fill vlm.SLOTS, so G-I get storage positions of their own (NEW_SLOTS),
# which need the taller unit (UNIT_H, see the docstring). Tray bottoms on Kardex's 25 mm pitch:
# - F0, the front column under the opening, at 300 mm, the lowest the extractor goes (R1 is there too). The presented
#   tray's supports are at Z_OPEN - 30 = 824 mm, so with Kardex's 20 mm clear it takes 501 mm of goods: H's 406.
# - F3 and R5, the top of each column, at 3475 mm: the first step clear of E and F at 2700 (2700 + 3 + 727.5 + 20 =
#   3450.5). Under the drive bay at UNIT_H - 260 = 4190 mm they take 692 mm of goods: G's 554 and I's 660. I sets the
#   height: 3478 + 660 + 20 = 4158 mm under the drive bay needs a 4418 mm unit, so 4450 on the 100 mm steps.
UNIT_H = 4450.0
NEW_SLOTS = {"F0": (V.Y_FRONT, 300.0), "F3": (V.Y_FRONT, 3475.0), "R5": (V.Y_REAR, 3475.0)}
SLOT_NOTE = {"F0": "the front column, under the opening", "F3": "the top of the front column",
             "R5": "the top of the rear column"}
NEW_TRAYS: dict[str, tuple[str, str]] = {"G": ("F3", "resin printing"), "H": ("F0", "PCB assembly"),
                                         "I": ("R5", "desktop LPBF")}


def slot_goods_h(slot: str) -> float:
    """The tallest goods a new slot takes, with Kardex's 20 mm clear above them (UNIT_H's unit)."""
    z = NEW_SLOTS[slot][1] + V.T_FLOOR
    top = V.Z_OPEN - 30.0 if slot == "F0" else UNIT_H - 260.0      # the opening's supports; the drive bay
    return top - V.GOODS_CLEAR - z
# Floor machines: warehouse.STATIONS (the DED machine and the packaging station have reserved spots; HIP has one too).
# Services: CAMERA_HOOK names the function in services.py that adds the stream cameras and the bay camera; it is called
# as hook(sc, L) and should return [(label, xyz)] for the captions. Until it exists, stand-ins are drawn.
CAMERA_HOOK = "add_cameras"
INSTALL_AT = 0                                 # the first unit is put together at charger 0

CAM_ROOM = [(9000, -21000, 14500), (-300, -2700, 0), (0, 0, 1)]
CAM_TOP = [(1500, -14500, 21000), (-300, -2600, 0), (0, 0, 1)]
CAM_UTIL = [(7600, -16500, 9500), (-600, -2600, 2400), (0, 0, 1)]
# the VLM's view: 1.18 times as far back as for the 3950 mm unit, looking 300 mm higher, to take the 4450 mm one
CAM_VLM = [(7434, -10784, 6566), (0, -400, 2200), (0, 0, 1)]
CAM_FLOOR = W.CAM_ALL
CAM_UNIT = [(1900, -2900, 2300), (-1300, -5600, 800), (0, 0, 1)]
CAM_OPEN = [(4300, -7700, 3100), (0, -1000, 1300), (0, 0, 1)]
ORBIT = [[(-9000, -16500, 9000), (-300, -2300, 600), (0, 0, 1)],
         [(-15500, -2000, 9500), (-300, -2300, 600), (0, 0, 1)],
         [(-5500, 9500, 10500), (-300, -2300, 600), (0, 0, 1)],
         [(9500, -18000, 12500), (-300, -2600, 300), (0, 0, 1)]]


def load() -> dict:
    """tour.load()'s instruments with fab_tour.load()'s models for trays G-I (which also registers their materials)."""
    import fab_tour
    idata = tour.load()
    idata.update(fab_tour.load(FAB_KEYS))
    return idata


def tall_vlm() -> dict:
    """lab.meshes()'s VLM entries for a unit UNIT_H tall, with NEW_SLOTS added to vlm.SLOTS. vlm.py builds every height
    from UNIT_H and Z_TOP_IN (and animate the belts from Z_BELT_TOP), so they are set here, for this process, after
    lab.meshes() has cached the 3950 mm unit, and these meshes are cached apart from it."""
    V.SLOTS.update(NEW_SLOTS)
    if V.UNIT_H != UNIT_H:
        lab.meshes()                     # lab's own cache holds the 3950 mm unit before anything here changes
        V.UNIT_H, V.Z_TOP_IN = UNIT_H, UNIT_H - 260.0
        A.Z_BELT_TOP = V.Z_TOP_IN + 140.0
    srcs = (lab.HERE / "vlm.py", lab.HERE / "lab.py", lab.HERE / "lab_models" / "common.py")
    path = lab.CACHE / f"vlm_h{UNIT_H:.0f}_{lab._hash_sources(*srcs)}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    print(f"tessellating the {UNIT_H:.0f} mm VLM (cached afterwards in {path.name})", flush=True)
    ents = lab._vlm_entries()
    path.write_bytes(pickle.dumps(ents))
    return ents


def _item(it) -> tuple:
    """(key, x, y[, turn]) -> (key, x, y, turn)."""
    return (*it, 0.0) if len(it) == 3 else tuple(it)


def _box(inst, x, y, turn) -> tuple:
    """Where an item stands on its tray: its box centre (y None: front 30 mm behind the lip) and footprint (w, d),
    turned."""
    x0, x1, y0, y1, _, _ = inst.bbox()
    t = math.radians(turn)
    c, s = abs(math.cos(t)), abs(math.sin(t))
    w, d = c * (x1 - x0) + s * (y1 - y0), s * (x1 - x0) + c * (y1 - y0)
    if y is None:
        y = -(V.TRAY_D - 24.0) / 2 + 30.0 + d / 2
    return x, y, w, d


def _placed(inst, x, y, turn) -> np.ndarray:
    """An item's own frame -> its tray's: the box centred on (x, y), turned about z, standing on the tray floor."""
    x0, x1, y0, y1, z0, _ = inst.bbox()
    x, y, _, _ = _box(inst, x, y, turn)
    return T((x, y, V.T_FLOOR)) @ R((0, 0, 1), turn) @ T((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


# ================================================================================================ the lab
class Unit:
    """A MiR250 + UR10e built so it can be put together: the MiR250, its cabinet (a child group), the UR control box
    (UR10e data sheet: 460 x 449 x 254 mm) inside it, the arm on the cabinet's top plate and the gripper on the arm."""

    def __init__(self, sc: Scene, name: str, pose):
        import robot as RB
        self.sc, self.name, self.pose = sc, name, list(pose)
        cab = f"{name}_cab"
        for nm, (mesh, col) in P.mir250().items():
            grp = cab if ("cabinet" in nm or "e-stop" in nm) else name
            sc.add(f"{name}/{nm}", mesh, col, grp, **(dict(ambient=0.8) if "light" in nm else {}))
        holder, seat = P.buffer_holder()
        sc.add(f"{name}/holder", holder.translate((*A.BUFFER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, cab)
        sc.parent[cab] = name
        sc.gmat[cab] = np.eye(4)
        cb = f"{name}_cb"                         # the control box, standing on the MiR's top, inside the cabinet
        H0 = P.MIR["H"]
        box = pv.Box(bounds=(-230, 230, -127, 127, H0 + 5, H0 + 5 + 449)).triangulate()
        sc.add(f"{name}/control box", box, (0.60, 0.62, 0.64), cb)
        sc.add(f"{name}/control box front", pv.Box(bounds=(-200, 200, -129, -127, H0 + 60, H0 + 400)).triangulate(),
               (0.25, 0.27, 0.30), cb)
        sc.parent[cb] = name
        sc.gmat[cb] = np.eye(4)
        self.robot = RB.Robot(sc, A.ROBOT, cab, T((*A.ARM_LOCAL, P.AMR_TOP)), q0=A.PARK_DEG, prefix=f"{name}ur")
        self.set()

    def set(self, pose=None):
        if pose is not None:
            self.pose = list(pose)
        x, y, hd = self.pose
        self.sc.gmat[self.name] = T((x, y, 0)) @ R((0, 0, 1), hd)

    def part_names(self, part):
        sc, nm = self.sc, self.name
        if part == "base":
            return [n for n, g in sc.group_of.items() if g == nm]
        if part == "cabinet":
            return [n for n, g in sc.group_of.items() if g == f"{nm}_cab"]
        if part == "control box":
            return [n for n, g in sc.group_of.items() if g == f"{nm}_cb"]
        if part == "arm":
            return [n for n, g in sc.group_of.items() if g.startswith(f"{nm}ur_") and "_gr_" not in g]
        if part == "gripper":
            return [n for n, g in sc.group_of.items() if g.startswith(f"{nm}ur_gr_")]
        raise KeyError(part)

    def all_names(self):
        return [n for p in ("base", "cabinet", "control box", "arm", "gripper") for n in self.part_names(p)]

    def gripper_offset(self, d):
        """Slide the gripper d mm off the flange, along the tool axis (the arm's own set() puts it back)."""
        import ur_arm
        rb = self.robot
        fk = ur_arm.fk(rb.model, rb.q)
        gfk = ur_arm.gripper_fk(rb.close)
        for part in rb.gparts:
            self.sc.gmat[f"{rb.prefix}_gr_{part}"] = fk["tool0"] @ T((0, 0, d)) @ gfk[part]


def footprints(sc: Scene, L: A.Lab, F: W.Floor) -> pv.PolyData:
    """Tape round every floor machine's footprint, from where it will stand."""
    rects = []
    for key, rig in F.rigs.items():
        x0, x1, y0, y1, _, _ = rig.inst.bbox()
        rects.append(_rect_of(sc.world(rig.prefix + "body"), (x0, x1, y0, y1)))
    if "aconity" in F.groups:
        ents = line.aconity_entries()
        pts = np.vstack([e["mesh"].points for e in ents.values() if e["mesh"].n_points])
        lo, hi = pts.min(0), pts.max(0)
        rects.append(_rect_of(sc.world("aconity"), (lo[0], hi[0], lo[1], hi[1])))
    pts = np.vstack([e["mesh"].points for e in sc_data(L)["repowder"].values() if e["mesh"].n_points])
    lo, hi = pts.min(0), pts.max(0)
    rects.append(_rect_of(T(A.REPOWDER_AT), (lo[0], hi[0], lo[1], hi[1])))
    xo, yo = V.UNIT_W / 2 + V.SKIN, V.UNIT_D / 2 + V.SKIN
    rects.append((-xo, xo, -yo - 50, yo))
    out = []
    for x0, x1, y0, y1 in rects:
        out.append(W.tape_rect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0 + 160, y1 - y0 + 160, t=50.0))
    return W._merge(out)


def _rect_of(M, bb):
    x0, x1, y0, y1 = bb
    c = np.array([[x, y, 0, 1] for x in (x0, x1) for y in (y0, y1)]) @ M.T
    return (c[:, 0].min(), c[:, 0].max(), c[:, 1].min(), c[:, 1].max())


_DATA = {}


def sc_data(L):
    return _DATA


def z_north() -> float:
    """The north cable tray's height: 325 mm over the VLM's roof (4300 mm over the 3950 mm unit)."""
    return V.UNIT_H + V.SKIN + 325.0


def utilities() -> dict:
    """Cable trays over both rows with drops to each station, a network cable in each, and an argon line from a
    cylinder manifold to the gas users. Layout choices, drawn to read, not a design."""
    zn, yn = z_north(), W.Y_FACE_N + 700.0       # over the north row, 325 mm above the VLM's roof
    zs, ys = 3200.0, W.Y_FACE_S - 600.0
    xs = (-9200.0, 9800.0)

    def tray(x0, x1, y, z):
        return W._merge([W._box(x0, y - 150, z, x1, y + 150, z + 12), W._box(x0, y - 150, z, x1, y - 138, z + 100),
                         W._box(x0, y + 138, z, x1, y + 150, z + 100)])
    trays = W._merge([tray(*xs, yn, zn), tray(xs[0] + 1200, xs[1], ys, zs)])
    hangers = W._merge([W._box(x - 15, y - 15, z + 100, x + 15, y + 15, 6000) for x in np.arange(xs[0], xs[1], 3000)
                        for y, z in ((yn, zn), (ys, zs))])
    net = W._merge([pv.Cylinder(center=((xs[0] + xs[1]) / 2, y + 60, z + 35), direction=(1, 0, 0), radius=18,
                                height=xs[1] - xs[0], resolution=16).triangulate() for y, z in ((yn, zn), (ys, zs))])
    drops, boxes = [], []
    north = {"glovebox": -7300.0, "repowder": -3640.0, "vlm": 900.0, "aconity": 3700.0, "wire_edm": 7400.0}
    south = {"instron_floor": -6400.0, "instron_small": -4300.0, "chargers": -900.0, "ded": 3500.0, "packaging": 7300.0}
    for x in north.values():
        z_end = V.UNIT_H + V.SKIN if x == 900.0 else 2500.0
        drops.append(pv.Cylinder(center=(x, yn - 60, (zn + z_end) / 2), direction=(0, 0, 1), radius=22,
                                 height=zn - z_end, resolution=16).triangulate())
        boxes.append(W._box(x - 110, yn - 160, z_end - 160, x + 110, yn + 40, z_end))
    for x in south.values():
        drops.append(pv.Cylinder(center=(x, ys + 60, (zs + 1900) / 2), direction=(0, 0, 1), radius=22,
                                 height=zs - 1900, resolution=16).triangulate())
        boxes.append(W._box(x - 110, ys - 40, 1740, x + 110, ys + 160, 1900))
    gas_users = [-7300.0, -3640.0, 3700.0]
    gx0 = xs[0] - 400
    ar = [pv.Cylinder(center=((gx0 + 3700) / 2, yn + 230, zn - 150), direction=(1, 0, 0), radius=14,
                      height=3700 - gx0, resolution=14).triangulate(),
          pv.Cylinder(center=(gx0, yn + 230, zn / 2), direction=(0, 0, 1), radius=14, height=zn,
                      resolution=14).triangulate()]
    for x in gas_users:
        ar.append(pv.Cylinder(center=(x + 200, yn + 230, (zn - 150 + 1800) / 2), direction=(0, 0, 1), radius=12,
                              height=zn - 150 - 1800, resolution=14).triangulate())
    # the DED's argon: down the south tray
    ar.append(pv.Cylinder(center=(gx0, (yn + 230 + ys - 200) / 2, zs - 150), direction=(0, 1, 0), radius=14,
                          height=yn + 230 - (ys - 200), resolution=14).triangulate())
    ar.append(pv.Cylinder(center=((gx0 + 3500) / 2, ys - 200, zs - 150), direction=(1, 0, 0), radius=14,
                          height=3500 - gx0, resolution=14).triangulate())
    cyl = [pv.Cylinder(center=(gx0 - 300 + 260 * i, yn + 700, 750), direction=(0, 0, 1), radius=115, height=1500,
                       resolution=24).triangulate() for i in range(4)]
    return {"cable trays": (trays, (0.70, 0.72, 0.74)), "tray hangers": (hangers, (0.55, 0.57, 0.60)),
            "network cable": (net, (0.15, 0.40, 0.85)), "power drops": (W._merge(drops), (0.30, 0.31, 0.33)),
            "drop boxes": (W._merge(boxes), (0.95, 0.75, 0.15)), "argon line": (W._merge(ar), (0.25, 0.60, 0.35)),
            "argon cylinders": (W._merge(cyl), (0.30, 0.55, 0.36))}


def stand_in_cameras(sc: Scene, trays) -> list:
    """Stand-ins for services.py's cameras: a small camera on a post at the back corner of each tray, looking along it,
    and two bay cameras under the north cable tray. Schematic."""
    labels = []
    for k in trays:
        g = f"tray_{k}"
        post = pv.Cylinder(center=(-V.TRAY_W / 2 + 70, V.TRAY_D / 2 - 70, 330), direction=(0, 0, 1), radius=8,
                           height=600, resolution=12).triangulate()
        head = W._box(-V.TRAY_W / 2 + 40, V.TRAY_D / 2 - 100, 620, -V.TRAY_W / 2 + 110, V.TRAY_D / 2 - 40, 670)
        lens = pv.Cylinder(center=(-V.TRAY_W / 2 + 120, V.TRAY_D / 2 - 70, 645), direction=(1, -0.3, -0.4), radius=14,
                           height=20, resolution=16).triangulate()
        sc.add(f"cam {k}/post", post, (0.25, 0.26, 0.28), g)
        sc.add(f"cam {k}/head", head, (0.10, 0.45, 0.30), g)
        sc.add(f"cam {k}/lens", lens, (0.05, 0.05, 0.06), g)
    for i, (x, aim) in enumerate(((0.0, (0, -1, -0.9)), (-4000.0, (0.4, -1, -0.8)))):
        y, z = W.Y_FACE_N + 700.0 - 160, z_north() - 60
        dome = pv.Sphere(radius=70, center=(x, y - 120, z - 90)).triangulate()
        arm = W._box(x - 20, y - 140, z - 40, x + 20, y, z)
        sc.add(f"baycam{i}/dome", dome, (0.15, 0.15, 0.17), "cams")
        sc.add(f"baycam{i}/arm", arm, (0.85, 0.86, 0.87), "cams")
        labels.append((f"bay camera {i + 1}", (x, y - 120, z - 90)))
    return labels


def rig_in(sc: Scene, g, names, out=False, travel=1700.0):
    """A tray instrument (a tour.Rig) comes in through the opening onto its place, as animate.item_in does."""
    base = sc.gmat[g].copy()

    def up(u):
        v = u if out else 1.0 - u
        sc.gmat[g] = T((0, -travel * v, min(1.0, v * 6) * 20.0)) @ base
        for n in names:
            sc.alpha[n] = 1.0 if v < 0.7 else max(0.0, 1 - (v - 0.7) / 0.3)
    return up


def spread(sc: Scene, cam, items, fy=0.15) -> list:
    """Leader labels spread evenly across the frame (right of the gauge table) in the order their anchors are seen from
    `cam`, in two staggered rows: W.auto puts each over its own anchor, which hides one of four items side by side."""
    out = W.auto(sc, cam, items)                 # sorted left to right as seen
    n = len(out)
    return [(t, xyz, (0.30 + 0.60 * i / max(n - 1, 1), fy + 0.06 * (i % 2))) for i, (t, xyz, _) in enumerate(out)]


def stagger(fs, overlap=0.45):
    """Run updates one after another within one step, each over `overlap` of it."""
    n = len(fs)

    def up(u):
        for i, f in enumerate(fs):
            t0 = 0.0 if n == 1 else i * (1.0 - overlap) / (n - 1)
            f(window(u, t0, t0 + overlap if n > 1 else 1.0))
    return up


def build(data, idata):
    data = {**data, "vlm": tall_vlm()}               # the UNIT_H unit, with room for trays G-I (see the docstring)
    _DATA.update(data)
    sc = Scene("setup_lab", TITLE, gif=False)
    sc.cam = list(CAM_ROOM)
    L = A.Lab(sc, data, robot=False)
    if "cubxl_corrosion" in idata:                   # round 2's CubXL stays hidden: the corrosion set-up replaces it
        for g in L.eq_groups.get("A", []):
            if L.eq_key[g] in REPLACED["A"]:
                for nm in L.eq_names(g):
                    sc.alpha[nm] = 0.0
    else:
        TRAY_ITEMS["A"] = list(A.LOADS["A"])
    F = W.Floor(sc, L, idata)
    rigs, items = {}, {k: [] for k in "ABCDEF"}
    for k, (slot, role) in NEW_TRAYS.items():
        line.EXTRA[k] = (slot, role)
    for k in ["D", "E", "F", *NEW_TRAYS]:
        line.add_tray(sc, L, k)
    loads = {k: list(v) for k, v in TRAY_ITEMS.items()}
    for k, extra in ROUND4_TRAY.items():
        loads.setdefault(k, [])
        loads[k] += [it for it in extra if it[0] in idata]
    for k, lst in loads.items():
        items.setdefault(k, [])
        for it in lst:
            key, x, y, turn = _item(it)
            if k in A.LOADS and (key, x, y) in A.LOADS[k]:
                g = next(gg for gg in L.eq_groups[k] if L.eq_key[gg] == key)
                names = L.eq_names(g) + (L.groups("vial", "vial_powder", "vial_liquid") if key == "rack" else [])
                items[k].append((key, g, names, "lab"))
                continue
            if key not in idata:
                continue
            inst, ents = idata[key]
            tag = f"{k}_{key}"
            n = sum(1 for kk, _, _, _ in items[k] if kk == key)       # a second of the same (tray G's two Form 4s)
            tag = tag if n == 0 else f"{tag}{n + 1}"
            rig = tour.Rig(sc, inst, ents, f"{tag}:", at=_placed(inst, x, y, turn), parent=f"tray_{k}")
            for piece in [pc for pc in rig.names if pc in inst.props]:
                for nm in rig.names.pop(piece):
                    sc.alpha[nm] = 0.0
            rigs[tag] = rig
            items[k].append((key, f"{tag}:body", rig.all_names(), "rig"))
    for r in fit(idata):                       # say so if a round-4 item doesn't fit where ROUND4_TRAY puts it
        if r.get("overlaps") or False in (r.get("fits_height"), r.get("inside_tray"), r.get("fits_slot")):
            print(f"setup_lab: check {r['key']} on tray {r['tray']}: {r}", flush=True)
    units = [Unit(sc, f"unit{i}", W.charger_pose(i)) for i in range(len(W.CHARGERS))]
    util = {}
    for nm, (mesh, col) in utilities().items():
        sc.add(f"util/{nm}", mesh, col, "util", specular=0.2)
        util[nm] = f"util/{nm}"
    sc.add("footprints", footprints(sc, L, F), W.TAPE_W, "tape", specular=0.0, ambient=0.5)
    return sc, L, F, items, rigs, units, util


# ================================================================================================ the movie
def movie(data, idata):
    sc, L, F, items, rigs, units, util = build(data, idata)
    vlm_groups = ["base", "posts", "col_front", "col_rear", "lift_rails", "drive", "lift", "belts", "bay", "console",
                  "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top"]
    trays = [k for k in L.tray]
    tray_groups = [f"tray_{k}" for k in trays]
    eq = [n for k in items for _, _, names, _ in items[k] for n in names]
    machines = [n for key, ns in F.groups.items() if key in W.STATIONS and key != "vlm" for n in ns]
    layout = F.groups["tape"] + F.groups["docks"] + ["footprints"] + \
        [n for n, g in sc.group_of.items() if g.startswith("reserved_")] + \
        [n for n, g in sc.group_of.items() if g.startswith("charger") and g.endswith("_tape")]
    chargers = [n for n, g in sc.group_of.items() if g.startswith("charger") and not g.endswith("_tape")]
    unit_names = [n for u in units for n in u.all_names()]
    A.hide(L, L.groups(*vlm_groups, *tray_groups) + eq + machines + layout + chargers + unit_names +
           list(util.values()))
    L.skin(0.0)(1.0)
    L.show_gauges = False
    L.apply_state()
    n = 9
    have = set(idata)
    # ------------------------------------------------------------------ 1. the empty bay
    sc.step(f"1/{n}", "An empty bay in a warehouse, about 24 m between the racks on its side walls. Everything that "
            "follows goes into it.", 2.4, None, hold=1.2)
    # ------------------------------------------------------------------ 2. the layout on the floor
    fl = {nm: 1.0 for nm in layout}

    def tape_on(u):
        for nm in fl:
            sc.alpha[nm] = u
    sc.step(f"2/{n}", "The layout goes down in tape first: the 3.0 m aisle, each machine's footprint, a dock for the "
            "MiR250 at every front with a camera target on a post, two charger bays, and space kept for the DED "
            "machine and the packaging station.", 2.6, tape_on, hold=1.6, cam_to=CAM_TOP,
            labels=W.auto(sc, CAM_TOP, [("main aisle, 3.0 m", (-7000, (W.AISLE[0] + W.AISLE[1]) / 2, 0)),
                                         ("footprint: Kardex VLM", (0, -1000, 0)),
                                         ("dock and camera target", (*W.target_xy("aconity"), W.TARGET_Z)),
                                         ("charger bays", (W.CHARGERS[0], W.Y_FACE_S + 400, 0)),
                                         (W.RESERVED["ded"][0] if "ded" not in have else "DED machine",
                                          tuple(F.where["ded"]))]))
    # ------------------------------------------------------------------ 3. utilities
    names_u = list(util.values())

    def util_on(u):
        for i, nm in enumerate(names_u):
            sc.alpha[nm] = window(u, i / (len(names_u) + 1), (i + 2) / (len(names_u) + 1))
    sc.step(f"3/{n}", "Utilities: cable trays over both rows with a drop to every station (power and network), "
            "208 V three-phase to the VLM (#53), and an argon line from a cylinder manifold to the glovebox, the "
            "rePowder, the Aconity and the DED. Layout choices, not a design.", 3.2, util_on, hold=1.6, cam_to=CAM_UTIL,
            labels=W.auto(sc, CAM_UTIL, [("cable tray: power and network", (5200, W.Y_FACE_N + 700, z_north() + 100)),
                                          ("argon cylinders", (-9500, W.Y_FACE_N + 1400, 1500)),
                                          ("power drop", (-4300, W.Y_FACE_S - 600, 2500)),
                                          ("VLM supply, 208 V 3-phase", (900, W.Y_FACE_N + 640, z_north()))]))
    # ------------------------------------------------------------------ 4. the VLM
    s = A.slide_in
    sc.step(f"4/{n}", f"The Kardex Shuttle XP 500 goes together where its footprint is taped: base frame, posts, "
            f"storage columns. Assumed here: {UNIT_H:.0f} mm tall, 500 mm more than #53's 13 ft unit (Kardex builds it "
            f"in 100 mm steps), so that it holds trays G-I too.", 3.4,
            A.both(s(L, ["base"], (0, 0, 900)), s(L, ["posts"], (0, 0, 1800)),
                   s(L, ["col_front", "col_rear"], (2600, 0, 0))),
            hold=0.6, cam_to=CAM_VLM)
    sc.step(f"4/{n}", f"The extractor and its drive, then {len(trays)} empty electrified trays, A to {trays[-1]}. G and "
            "I take a new slot at the top of each column; H goes in the front column, under the opening.", 2.8,
            A.both(s(L, ["lift_rails"], (0, 0, 2500)), s(L, ["drive"], (0, 0, 1400)),
                   s(L, ["lift", "belts"], (0, 0, 2400)), s(L, tray_groups, (3200, 0, 0))), hold=0.5)
    sc.step(f"4/{n}", "The cladding, the opening, the console and the shutter.", 2.2,
            A.both(s(L, ["skin_L"], (-900, 0, 0)), s(L, ["skin_R"], (900, 0, 0)), s(L, ["skin_back"], (0, 900, 0)),
                   s(L, ["skin_top"], (0, 0, 900)), s(L, ["skin_front", "bay", "console", "shutter"], (0, -900, 0))),
            hold=0.6)
    # ------------------------------------------------------------------ 5. the floor machines
    order = [k for k in ("glovebox", "repowder", "aconity", "wire_edm", "instron_floor", "instron_small", "ded",
                         "packaging", "hip") if k in F.groups and (k not in W.RESERVED or k in have)]
    fs = []
    for k in order:
        root = {"repowder": "repowder", "aconity": "aconity"}.get(k, f"wh_{k}:body")
        row = W.STATIONS[k][1]
        fs.append(s(L, [root], (0, -2600 if row == "N" else 2600, 0), names=F.groups[k]))
    sc.step(f"5/{n}", "The floor machines come in on their footprints, fronts to the aisle: the glovebox (its "
            "antechamber to the aisle), the rePowder, the Aconity MIDI, the wire EDM and the two Instrons.", 5.0,
            stagger(fs, overlap=0.40), hold=1.0, cam_to=CAM_FLOOR,
            labels=W.auto(sc, CAM_FLOOR, W.floor_labels(F, order, have)))
    # ------------------------------------------------------------------ 6. the arms
    u0 = units[INSTALL_AT]
    x, y, hd = u0.pose
    start = (x, y + 2200.0, hd)
    u0.set(start)
    ch = chargers

    def chargers_on(u):
        for nm in ch:
            sc.alpha[nm] = u
    sc.step(f"6/{n}", "Two MiR Charge 48V chargers go in, then the first MiR250 rolls onto its charging plate.", 1.4,
            chargers_on, hold=0.1, cam_to=CAM_UNIT)
    base_names = u0.part_names("base")

    def roll(u):
        for nm in base_names:
            sc.alpha[nm] = min(1.0, u * 4)
        u0.set((x, start[1] + (y - start[1]) * u, hd))
    sc.step(f"6/{n}", "Two MiR Charge 48V chargers go in, then the first MiR250 rolls onto its charging plate.", 2.0,
            roll, hold=0.2, labels=[("MiR250, 800 x 580 x 300 mm", (x, y, 300), (0.20, 0.60))])
    cab_names = u0.part_names("cabinet")

    def cabinet(u):
        sc.gmat[f"{u0.name}_cab"] = T((0, 0, 700 * (1 - u)))
        for nm in cab_names:
            sc.alpha[nm] = min(1.0, u * 3)
    sc.step(f"6/{n}", "Its cabinet goes on top: it carries the arm at 800 mm and holds the UR control box.", 1.6,
            cabinet, hold=0.2)
    cb_names = u0.part_names("control box")
    cab_body = [nm for nm in cab_names if "holder" not in nm]

    def control_box(u):
        sc.gmat[f"{u0.name}_cb"] = T((0, -700 * (1 - u), 0))
        for nm in cb_names:
            sc.alpha[nm] = min(1.0, u * 4)
        for nm in cab_body:
            sc.alpha[nm] = 1.0 - 0.7 * math.sin(math.pi * u)
    sc.step(f"6/{n}", "The UR control box (460 x 449 x 254 mm, 12 kg) goes into the cabinet.", 1.8, control_box,
            hold=0.2, labels=[("UR control box", (x, y, 600), (0.20, 0.42))])
    rb = u0.robot
    arm_names = u0.part_names("arm")
    root0 = sc.gmat[rb.root].copy()

    def arm_on(u):
        sc.gmat[rb.root] = T((0, 0, 900 * (1 - u))) @ root0
        for nm in arm_names:
            sc.alpha[nm] = min(1.0, u * 3)
    sc.step(f"6/{n}", "The UR10e is lowered onto the cabinet's top plate and bolted down: four M8 bolts at 20 Nm, two "
            "8 mm pins so it goes back in the same place (UR's manual).", 2.2, arm_on, hold=0.4,
            labels=[("UR10e, 33.3 kg", (x, y, 1300), (0.20, 0.30))])
    g_names = u0.part_names("gripper")

    def gripper_on(u):
        u0.gripper_offset(160 * (1 - u))
        for nm in g_names:
            sc.alpha[nm] = min(1.0, u * 3)
    sc.step(f"6/{n}", "The Robotiq 2F-85 goes on the flange.", 1.4, gripper_on, hold=0.2)
    rb.set()
    others = [nm for uu in units if uu is not u0 for nm in uu.all_names()]
    q_ready = np.radians((-90.0, -100.0, 110.0, -100.0, -90.0, 0.0))

    def wake(u):
        for nm in others:
            sc.alpha[nm] = u
    sc.step(f"6/{n}", "It wakes up and stretches. The second unit is built the same way at the other charger.", 1.8,
            A.both(rb.joint_to(q_ready), wake), hold=0.2)
    sc.step(f"6/{n}", "It wakes up and stretches. The second unit is built the same way at the other charger.", 1.4,
            rb.joint_to(A.PARK_RAD), hold=0.4)
    # ------------------------------------------------------------------ 7. the trays
    sc.step(f"7/{n}", "Loading, drawn see-through: each tray comes to the opening, people put its instruments on "
            "through it (most weigh more than the arm's 12.5 kg), and it goes back to its slot and its power.", 1.8,
            L.skin(1.0), hold=0.2, cam_to=CAM_OPEN)
    L.show_gauges = True
    for k in trays:
        lst = items.get(k, [])
        role = A.ROLE.get(k, "")
        L.fetch(k, f"7/{n}", f"Tray {k} ({role}) comes to the opening.", fast=0.3, hold=0.05)
        if lst:
            fs = []
            lbls = []
            for key, g, names, kind in lst:
                fs.append(A.item_in(L, g) if kind == "lab" else rig_in(sc, g, names))
                nm = A.NAMES.get(key) if kind == "lab" else idata[key][0].model
                lbls.append((nm, tuple(np.array(sc.world(g)[:3, 3]) + (0, 0, 400))))
            texts = [lb[0] for lb in lbls]               # two of the same once: "2 x Formlabs Form 4"
            cap = f"Tray {k}: " + ", ".join(f"{texts.count(t)} x {t}" if texts.count(t) > 1 else t
                                            for t in dict.fromkeys(texts)) + "."
            for key, _, _, turn in map(_item, ROUND4_TRAY.get(k, [])):
                if turn and key in idata:                 # tray H's stencil printer
                    inst = idata[key][0]
                    _, _, y0, y1, _, _ = inst.bbox()
                    cap += (f" The {inst.model} is turned {turn:.0f} degrees: it is {y1 - y0:.0f} mm deep, the "
                            f"tray's inside {V.TRAY_D - 24:.0f}.")
            sc.step(f"7/{n}", cap, 0.9 + 0.5 * len(lst), stagger(fs, overlap=0.55), hold=0.5,
                    labels=spread(sc, CAM_OPEN, lbls) if k in NEW_TRAYS else W.auto(sc, CAM_OPEN, lbls, dy=0.16))
        slot = A.HOME[k]
        where = f"{slot}, {SLOT_NOTE[slot]}" if slot in SLOT_NOTE else slot
        L.store(k, f"7/{n}", f"Tray {k} goes back to its slot ({where}), where it has power.", fast=0.3, hold=0.05)
    # ------------------------------------------------------------------ 8. the cameras
    hook = None
    try:
        import services  # noqa: F401  (subagent C's module, once merged)
        hook = getattr(services, CAMERA_HOOK, None)
    except ImportError:
        pass
    if hook is not None:
        cam_lbls = hook(sc, L) or []
        cap = "The cameras go on: stream cameras on trays A-F and the bay camera (services.py, which has none for " \
              "trays G-I yet)."
    else:
        cam_lbls = stand_in_cameras(sc, trays)
        cap = "The cameras go on: a stream camera on each tray and two bay cameras under the cable tray. Stand-ins: " \
              "services.py's cameras replace them once merged."
    L.show_gauges = False
    L.apply_state()
    cam_names = [nm for nm in sc.actors if nm.startswith(("cam ", "cam_", "camhead_", "baycam"))]
    for nm in cam_names:
        sc.alpha[nm] = 0.0

    def cams_on(u):
        for nm in cam_names:
            sc.alpha[nm] = u
    sc.step(f"8/{n}", cap, 1.6, cams_on, hold=1.4, cam_to=CAM_VLM,
            labels=W.auto(sc, CAM_VLM, cam_lbls[:2] + [("tray camera", (-V.TRAY_W / 2 + 80, V.Y_REAR + 360,
                                                                       V.SLOTS["R4"][1] + 640))]))
    # ------------------------------------------------------------------ 9. orbit
    L.show_gauges = False
    L.apply_state()
    done = f"Set up: the VLM ({UNIT_H:.0f} mm tall) with trays A-{trays[-1]}, the floor machines, two MiR250 + UR10e " \
           "units on charge."
    sc.step(f"9/{n}", done, 1.2, L.skin(0.0), hold=0.0)
    for i, cam in enumerate(ORBIT):
        last = i == len(ORBIT) - 1
        sc.step(f"9/{n}", done, 2.4, None, hold=2.4 if last else 0.0, cam_to=cam, still=last)
    return sc.save()


def fit(idata) -> list:
    """Every tray item: its height against Kardex's 727.5 mm (and, on trays G-I, against its slot: slot_goods_h), its
    footprint against the tray's rim, and any overlap with its neighbours on the tray."""
    rows = []
    for k, lst in {**TRAY_ITEMS, **{kk: TRAY_ITEMS.get(kk, []) + v for kk, v in ROUND4_TRAY.items()}}.items():
        boxes = []
        for it in lst:
            key, x, y, turn = _item(it)
            if key in idata:
                inst = idata[key][0]
                x0, x1, y0, y1, z0, z1 = inst.bbox()
                x, y, w, d = _box(inst, x, y, turn)
                h = z1 - z0
            elif key in A.NAMES:
                rows.append(dict(tray=k, key=key, note="round 2 equipment (animate.LOADS)"))
                continue
            else:
                rows.append(dict(tray=k, key=key, note="not loaded by tour.load() or fab_tour.load(): skipped"))
                continue
            b = (x - w / 2, x + w / 2, y - d / 2, y + d / 2)
            over = [kk for kk, bb in boxes if b[0] < bb[1] and bb[0] < b[1] and b[2] < bb[3] and bb[2] < b[3]]
            boxes.append((key, b))
            row = dict(tray=k, key=key, at_mm=[round(float(x), 1), round(float(y), 1)],
                       size_mm=[round(w), round(d), round(h)],
                       fits_height=bool(h <= V.MAX_GOODS_H),
                       inside_tray=bool(abs(b[0]) <= V.TRAY_W / 2 - 12 and b[1] <= V.TRAY_W / 2 - 12
                                        and abs(b[2]) <= V.TRAY_D / 2 - 12 and b[3] <= V.TRAY_D / 2 - 12),
                       overlaps=over)
            if turn:
                row["turn_deg"] = turn
            if k in NEW_TRAYS:
                slot = NEW_TRAYS[k][0]
                row.update(slot=slot, slot_goods_mm=round(slot_goods_h(slot), 1),
                           fits_slot=bool(h <= slot_goods_h(slot)))
            rows.append(row)
    return rows


if __name__ == "__main__":
    args = sys.argv[1:]
    idata = load()
    if args and args[0] == "fit":
        for r in fit(idata):
            print(r)
    else:
        data = lab.meshes()
        print(movie(data, idata), flush=True)
        if not PREVIEW:
            print(line.mp4_to_gif(OUT / "mp4" / "setup_lab.mp4", OUT / "setup_lab.gif", **W.GIF), flush=True)

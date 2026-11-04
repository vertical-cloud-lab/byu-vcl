"""The whole lab set up from scratch (#303), on the warehouse floor of ``warehouse.py``: an empty bay; the layout taped
on the floor, with a MiR250 dock and an AprilTag target at every station; the utilities; two Kardex Shuttles
assembled; the floor machines moved in; the UR10e arms installed on their MiR250s; every tray loaded, A to M, each
with its UPS and its stream cameras; the bay cameras; a closing orbit. Mobile bases only: no rail anywhere.

    xvfb-run --server-num=60 python3 setup_lab.py            # -> out/setup_lab.gif, out/mp4/setup_lab.mp4, still
    PREVIEW=1 xvfb-run --server-num=60 python3 setup_lab.py  # the last frame of each sub-step -> /tmp/preview_setup_lab.png
    xvfb-run --server-num=60 python3 setup_lab.py fit        # every tray and the floor, measured as drawn ->
                                                             #   out/tray_plan.json, out/tray_plan.png, out/tray_plan_floor.png

What goes where is data: ``TRAYS`` (tray -> slot and role), ``ITEMS`` (tray -> [(key, x, y, turn)]), ``CAMS`` (the
stream cameras of the trays services.TRAY_CAMS doesn't cover yet) and ``FLOOR_PLAN`` (the floor, in
warehouse.STATIONS's form). Slots and their heights are ``vlm.COLUMNS``; notes/tray_plan.md explains the plan.
``fit`` builds the scene, then measures every tray item, the tray's UPS, its dock plate and its camera rigs from their
meshes, in the tray's frame: overlaps, the rim, the opening's product height and the slot's span. On the floor it
checks every MiR250 dock, its approach and the pivot spot it turns on, against every machine and every target post.

Everything here that isn't a maker's figure is a layout choice: the cable trays, drops, junction boxes and the argon
line, the cameras and where they sit, the second Shuttle and the floor plan. Kardex's 208 V three-phase supply is
#53's. Installing the arm follows UR's manual (four M8 bolts at 20 Nm, two 8 mm pins for re-mounting; UR10e user manual
SW5.26, 6.1).
"""
from __future__ import annotations

import hashlib
import importlib
import json
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
from scene import FPS, OUT, PREVIEW, Scene, T, R, S, window

TITLE = "Vertical cloud lab, set up from scratch"
X2 = V.SHUTTLE_X[2]                            # the second Shuttle's centre

# ================================================================================================ what goes where
# tray: (slot in vlm.SLOTS, role). Shuttle 1 holds the alloy route and characterization, Shuttle 2 fabrication, the
# inert glovebox and the round-7 testing trays (notes/tray_plan.md).
TRAYS = {
    "A": ("R2", "liquid handling, corrosion"), "B": ("R3", "powder dosing, vacuum press"),
    "C": ("F1", "3D printing"), "D": ("R1", "microscopy and diffraction"),
    "E": ("R4", "mechanical testing, particle size"), "F": ("F2", "polishing and heat treatment"),
    "J": ("F0", "sample storage"),
    "K": ("2R1", "inert glovebox, digital microscope"), "L": ("2R2", "tensile and hardness"), "M": ("2R3", "machining and XRF, under a hood"),
    "H": ("2R4", "PCB assembly"), "G": ("2F1", "resin printing"), "I": ("2F2", "desktop LPBF"),
}
ORDER = ["D", "A", "B", "E", "J", "C", "F", "K", "L", "M", "H", "G", "I"]      # loading order: Shuttle 1, then 2
# tray: [(key, x, y, turn)] in the tray's frame (centre of its floor, y to the back); y None puts the item's front 30 mm
# behind the tray's front lip, as fab_trays does. A-C's round-2 items are animate.LOADS's (built by animate.Lab), D-F
# line.TRAY_LOADS's, G-I fab_trays.LOADS's. Each tray also carries its UPS and dock plate at the back right
# (services.UPS_AT, services.PLATE_*) and its camera posts (services.TRAY_CAMS or CAMS below); `fit` checks them all.


def _items() -> dict:
    import alloy_press as AP
    import fab_trays as FT
    out = {k: [(key, x, y, 0.0) for key, x, y in v] for k, v in A.LOADS.items()}
    out["A"] = [it for it in out["A"] if it[0] != "cubxl"] + [("cubxl_corrosion", -300.0, -114.5, 0.0)]
    out["B"] += [("vacuum_press", *AP.PRESS_AT, 0.0)]           # alloy_press.PRESS_AT, as in the alloy route
    for k, v in line.TRAY_LOADS.items():
        out[k] = [(key, x, y, 0.0) for key, x, y in v]
    for k, v in FT.LOADS.items():
        out[k] = [tuple(it) for it in v]
    out["J"] = [("storage", -320.0, 0.0, 0.0)]                  # its right 630 mm left for the UPS and the dock
    # the Keyence VHX with its controller beside it is 948 mm wide: too wide for tray C beside the UPS, so it went to K
    # (its box centre at x; the controller makes the unit reach 318 mm left and 630 mm right of it)
    out["K"] = [("glovebox_tray", -460.0, None, 0.0), ("vhx", 573.0, -15.0, 0.0)]
    out["L"] = [("tensile_h", -565.0, None, 0.0), ("hardness", 343.0, None, 0.0)]     # left of the UPS
    out["M"] = [("xrf", -873.0, None, 0.0), ("fumehood_tray", -53.0, None, 0.0), ("cnc", 722.0, None, 0.0)]
    return out


ITEMS = _items()
# the stream cameras of the trays services.TRAY_CAMS has no entry for: tray: ([(mast x, mast y, aim x, aim y, aim z
# [, post yaw])], block height on the post, post height). The short trays (H, J) have short posts, so their slots stay
# low: the head's top is about block + 148 mm over the tray's underside (services.TILT_AXIS, head_reach).
CAMS = {
    "G": ([(-1150.0, 361.0, -920.0, -150.0, 300.0, 90.0), (160.0, 361.0, 200.0, -150.0, 250.0, 90.0)], None, None),
    "H": ([(-1150.0, 361.0, -640.0, -100.0, 250.0, 90.0), (-130.0, 361.0, 400.0, -100.0, 200.0, 90.0)], 270.0, 320.0),
    "I": ([(-1150.0, 361.0, -500.0, -150.0, 400.0, 90.0), (-100.0, 361.0, 300.0, -150.0, 400.0, 90.0)], None, None),
    "J": ([(680.0, -360.0, -320.0, -100.0, 150.0), (1160.0, 100.0, -700.0, -100.0, 150.0)], 270.0, 320.0),
    "K": ([(470.0, 361.0, -460.0, -300.0, 450.0, 90.0)], None, None),
    "L": ([(-1150.0, 361.0, -540.0, -150.0, 300.0, 90.0), (180.0, 361.0, 560.0, -150.0, 400.0, 90.0)], None, None),
    "M": ([(-480.0, 361.0, -873.0, -150.0, 400.0, 90.0), (470.0, 361.0, 722.0, -150.0, 400.0, 90.0)], None, None),
}

# ------------------------------------------------------------------------------------------------ the floor
# warehouse.STATIONS's form: key: (x of its centre, row, turn about z, dock x). The second Shuttle stands 800 mm right
# of the first: a MiR250 turns on the spot between them (its corners sweep 0.49 m), then backs into the first one's
# dock or drives forwards into the second's. The wire EDM and the DED went to the south row and the packaging station
# to the north, so every dock has a pivot spot at its open end (``fit`` checks it).
FLOOR_PLAN = {
    "glovebox": (-7300.0, "N", -90.0, -7300.0),
    "repowder": (None, "N", 0.0, A.REPOWDER_AT[0] + 288.0),
    "sieve_cell": (-1982.5, "N", 0.0, -1700.0),
    "vlm": (0.0, "N", 0.0, 0.0),
    "vlm2": (X2, "N", 0.0, X2),
    "aconity": (6950.0, "N", 0.0, 6650.0),
    "packaging": (10050.0, "N", 0.0, 10050.0),
    "instron_floor": (-6400.0, "S", 0.0, -6600.0),
    "instron_small": (-4300.0, "S", 0.0, -4300.0),
    "fumehood": (1500.0, "S", 0.0, 1500.0),
    "ded": (3900.0, "S", 0.0, 3900.0),
    "wire_edm": (6600.0, "S", 0.0, 6600.0),
}
BACK_IN = {"instron_small", "vlm", "aconity", "sieve_cell"}   # backed into from the open end beyond the MiR's back
# the rePowder sticks out 337 mm past the row's fronts, so a MiR docks there 298 mm further out, as the alloy route's
# chapters 2-3 park it (alloy_atomize.END_POSE); so does the sieving cell's (alloy_print: 300 mm off its bench)
DOCK_Y = {"repowder": -2230.0, "sieve_cell": W.DOCK_N - 300.0}
# targets that can't stand where warehouse.target_xy puts them: the VLMs' stand outside the opening's width, so a tray
# pulled out to the front for maintenance passes them; the rePowder's in front of its own front
TARGET_AT = {"vlm": (-1330.0, -1742.0), "vlm2": (X2 + 1330.0, -1742.0),
             "repowder": (A.REPOWDER_AT[0] + 288.0 + 650.0, -1899.0 - 180.0)}
SIEVE_BENCH = dict(x=-1982.5, w=1065.0, d=600.0, h=700.0, encl_h=1150.0)    # alloy_print.BENCH, ENCL_H
INSTALL_AT = 0                                 # the first unit is put together at charger 0

CAM_ROOM = [(11000, -22000, 15500), (500, -2700, 0), (0, 0, 1)]
CAM_TOP = [(2000, -15000, 22500), (300, -2800, 0), (0, 0, 1)]
CAM_UTIL = [(9600, -17500, 9800), (300, -2600, 2400), (0, 0, 1)]
CAM_VLM = [(9800, -10400, 6600), (1800, -400, 1900), (0, 0, 1)]
CAM_FLOOR = [(6200, -21500, 17500), (700, -2900, 0), (0, 0, 1)]
CAM_UNIT = [(1900, -2900, 2300), (-1300, -5600, 800), (0, 0, 1)]
CAM_OPEN = [(4300, -7700, 3100), (0, -1000, 1300), (0, 0, 1)]
CAM_OPEN2 = [(X2 + 4300, -7700, 3100), (X2, -1000, 1300), (0, 0, 1)]
ORBIT = [[(-9000, -16500, 9000), (700, -2300, 600), (0, 0, 1)],
         [(-15500, -2000, 9500), (700, -2300, 600), (0, 0, 1)],
         [(-4500, 10500, 10500), (700, -2300, 600), (0, 0, 1)],
         [(11500, -18500, 12500), (700, -2600, 300), (0, 0, 1)]]


def use_floor_plan():
    """Point warehouse.py's floor plan at FLOOR_PLAN for this process: its stations, docks and targets."""
    W.STATIONS.clear()
    W.STATIONS.update(FLOOR_PLAN)
    W.BACK_IN.clear()
    W.BACK_IN.update(BACK_IN)
    W.RESERVED.clear()
    W.NAMES.update(fumehood="ducted fume hood", sieve_cell="sieving cell", vlm2="second Kardex Shuttle")
    if getattr(W, "_setup_lab_patched", False):
        return
    dock0, target0 = W.dock_pose, W.target_xy

    def dock_pose(key):
        x, y, hd = dock0(key)
        return (x, DOCK_Y.get(key, y), hd)

    def target_xy(key):
        return np.array(TARGET_AT[key]) if key in TARGET_AT else target0(key)
    W.dock_pose, W.target_xy, W._setup_lab_patched = dock_pose, target_xy, True


# ================================================================================================ the models
def load_r7() -> dict:
    """instruments_r7's models (round 7: the tray glovebox, the sideways tensile tester, the hardness tester, the CNC,
    the fume hoods, the storage load), cached on their sources, unless tour.MODULES loads them already."""
    try:
        mod = importlib.import_module("instruments_r7")
    except ModuleNotFoundError:
        return {}
    if "instruments_r7" in tour.MODULES or not getattr(mod, "REGISTRY", None):
        return {}
    tour.MATS.update(getattr(mod, "MATERIALS", {}))
    h = hashlib.sha256()
    for f in [*tour._sources("instruments"), lab.HERE / "instruments_r7.py"]:
        if f.exists():
            h.update(f.read_bytes())
    path = tour.CACHE / f"instruments_r7_{h.hexdigest()[:12]}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    out = {}
    for key, build in mod.REGISTRY.items():
        print(f"  building {key}", flush=True)
        try:
            inst = build()
        except FileNotFoundError as e:
            print(f"  skipping {key}: {e}", flush=True)
            continue
        out[key] = (inst, tour.piece_entries(inst))
    path.write_bytes(pickle.dumps(out))
    return out


def r7_stand_ins(have) -> dict:
    """A plain box at its FOOTPRINTS size for each instruments_r7 model not built yet, so the layout and the checks
    run before the models land. Each one says so in its model name."""
    try:
        import instruments_r7 as R7
    except ModuleNotFoundError:
        return {}
    import instruments as I
    sys.path.insert(0, str(lab.HERE / "lab_models"))
    from common import box
    out = {}
    for key, (w, d, h, _kg, product, url, where) in getattr(R7, "FOOTPRINTS", {}).items():
        if key in have:
            continue
        inst = I.Instrument(key, key, product.split(",")[0].split(" (")[0] + " (stand-in box)", (w, d, h), url,
                            floor=where == "floor")
        I._piece(inst, "body").add("stand-in", box(-w / 2, -d / 2, 0, w / 2, d / 2, h), "inst_light")
        out[key] = (inst, tour.piece_entries(inst))
    return out


def load_all() -> dict:
    """{key: (Instrument, entries)}: tour.load()'s, fab_tour's for trays G-I, and instruments_r7's (stand-in boxes
    for the ones not built yet)."""
    import fab_tour
    idata = tour.load()
    fab = {key for k in "GHI" for key, *_ in ITEMS[k]}
    idata.update(fab_tour.load(fab))
    idata.update(load_r7())
    idata.update(r7_stand_ins(idata))
    return idata


def placed(inst, x, y, turn) -> np.ndarray:
    """An instrument's own frame -> (x, y) on the tray floor, turned about z; y None: its front 30 mm behind the lip."""
    x0, x1, y0, y1, z0, _ = inst.bbox()
    if y is None:
        d = (y1 - y0) if abs(turn) % 180 < 1 else (x1 - x0)
        y = -(V.TRAY_D - 24.0) / 2 + 30.0 + d / 2
    return T((x, y, V.T_FLOOR)) @ R((0, 0, 1), turn) @ T((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


# ================================================================================================ two Shuttles
class TwoLab(A.Lab):
    """animate.Lab with a second Shuttle at x = X2: a copy of the VLM's meshes (groups 'u2_*'), its own extractor and
    shutter, and the trays whose slot is in it (vlm.SLOT_SHUTTLE). fetch/store work on the tray's own Shuttle."""

    def __init__(self, sc, data):
        self.unit = {}
        self.other = dict(lift_z=A.LIFT_HOME, shutter=0.0)
        self.active = 1
        self.focus = None
        super().__init__(sc, data, robot=False)
        for name, e in data["vlm"].items():
            kw = {}
            if e["material"] in ("vlm_skin", "vlm_bay"):
                kw = dict(specular=0.05, ambient=0.35)
            if e["material"] == "vlm_led":
                kw = dict(ambient=0.9, diffuse=0.2)
            g = f"u2_{e['group']}"
            sc.add(f"u2/{name}", e["mesh"], e["color"], g, opacity=e["opacity"], **kw)
            sc.gmat[g] = T((X2, 0, 0))
            if e["material"] in A.GHOST:
                self.ghost[f"u2/{name}"] = A.GHOST[e["material"]]
        self.skin(getattr(self, "_skin_f", 0.0))(1.0)
        self.apply_state()

    def use(self, unit):
        if unit != self.active:
            cur = dict(lift_z=self.lift_z, shutter=self.shutter)
            self.lift_z, self.shutter = self.other["lift_z"], self.other["shutter"]
            self.other, self.active = cur, unit

    def apply_state(self):
        sc = self.sc
        for k, (y, z) in self.tray.items():
            sc.gmat[f"tray_{k}"] = T((X2 if self.unit.get(k, 1) == 2 else 0.0, y, z))
            on = self.where[k] is not None
            sc.color[f"tray {k} lamp"] = A.GREEN if on else A.OFF
            sc.ambient[f"tray {k} lamp"] = 0.9 if on else 0.2
        mine, other = (self.lift_z, self.shutter), (self.other["lift_z"], self.other["shutter"])
        states = {1: mine if self.active == 1 else other, 2: other if self.active == 1 else mine}
        for unit, pre, x in ((1, "", 0.0), (2, "u2_", X2)):
            z, s = states[unit]
            sc.gmat[f"{pre}lift"] = T((x, 0, z))
            sc.gmat[f"{pre}belts"] = T((x, 0, z + 40)) @ S((1, 1, max(1.0, A.Z_BELT_TOP - (z + 40))))
            sc.gmat[f"{pre}shutter"] = T((x, 0, s * (V.Z_OPEN_TOP - V.Z_SILL + 10)))
        self.gauges()

    def gauges(self):
        if not self.show_gauges or self.focus is None:
            self.sc.gauges = []
            return
        k = self.focus
        w = self.where[k]
        state = "moving, unpowered" if w is None else ("at the opening, powered" if w == "open" else
                                                      f"stored ({w}), powered")
        self.sc.gauges = [(f"Tray {k}", state), ("Shuttle", str(self.unit.get(k, 1)))]

    def fetch(self, k, label, caption, fast=1.0, cam=None, hold=0.4, mint=0.6):
        """animate.Lab.fetch on tray k's own Shuttle, to its opening; mint: the shortest lift move (s)."""
        self.use(self.unit.get(k, 1))
        self.focus = k
        sc = self.sc
        ys, zs = V.SLOTS[self.where[k]]
        yt, zt = V.SLOTS["open"]
        if abs(self.lift_z - zs) > 1:
            sc.step(label, caption, max(mint, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs), hold=0.1,
                    cam_to=cam)
            cam = None
        self.where[k] = None
        self.apply_state()
        sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.1, cam_to=cam)
        sc.step(label, caption, max(mint, abs(zs - zt) / 1333 * fast), self.lift_to(zt, carry=k), hold=0.1)
        sc.step(label, caption, 0.7 * fast, self.shut(1.0), hold=0.0)
        sc.step(label, caption, 2.2 * fast, self.slide(k, yt), hold=0.0)
        sc.step(label, caption, 0.7 * fast, self.shut(0.0), hold=0.0)
        self.where[k] = "open"
        self.apply_state()
        sc.snap(max(1, int(round(hold * FPS))))

    def store(self, k, label, caption, fast=1.0, cam=None, hold=0.3, mint=0.6):
        """animate.Lab.store on tray k's own Shuttle."""
        self.use(self.unit.get(k, 1))
        self.focus = k
        self.where[k] = None
        self.apply_state()
        ys, zs = V.SLOTS[A.HOME[k]]
        sc = self.sc
        sc.step(label, caption, 0.7 * fast, self.shut(1.0), hold=0.0, cam_to=cam)
        sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.0)
        sc.step(label, caption, 0.7 * fast, self.shut(0.0), hold=0.1)
        sc.step(label, caption, max(mint, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs, carry=k), hold=0.1)
        sc.step(label, caption, 2.2 * fast, self.slide(k, ys), hold=0.0)
        self.where[k] = A.HOME[k]
        self.apply_state()
        sc.snap(max(1, int(round(hold * FPS))))


def add_tray(sc: Scene, L: TwoLab, k: str):
    """Tray k in its slot (TRAYS), with its dock plate and its tray lines (services.py) riding on it."""
    import services
    slot, role = TRAYS[k]
    V.TRAYS.setdefault(k, dict(kind="extra", role=role))
    A.HOME[k], A.ROLE[k] = slot, role
    L.unit[k] = V.SLOT_SHUTTLE[slot]
    if f"tray_{k}" not in {g for g in sc.group_of.values()}:
        for name, (shape, mat, group) in {**V.tray(k), **V.lamp(k)}.items():
            if hasattr(shape, "vals"):
                shape = shape.val() if len(shape.vals()) == 1 else line.I.cq.Compound.makeCompound(shape.vals())
            e = lab._entry(lab.to_mesh(shape, 2.0), mat, group)
            sc.add(name, e["mesh"], e["color"], group, opacity=e["opacity"])
    L.tray[k] = [*V.SLOTS[slot]]
    L.where[k] = slot
    L.eq_groups.setdefault(k, [])
    services.add_tray_services(sc, k, ups=False)


def add_ups(sc: Scene, k: str) -> list:
    """The tray's UPS (services.ups_parts) as its own group, so it can be carried in."""
    import services
    g = f"ups_{k}"
    names = services.add_meshes(sc, g, services.meshes_of("ups", services.ups_parts, 1.0), g)
    sc.parent[g] = f"tray_{k}"
    return names


def add_cams(sc: Scene, k: str) -> list[str]:
    """The tray's stream camera rigs: services.TRAY_CAMS, or CAMS for the trays it doesn't cover. -> post groups."""
    import services
    if services.TRAY_CAMS.get(k):
        return services.add_tray_cameras(sc, k)
    if k not in CAMS:
        return []
    layout, h, post_h = CAMS[k]
    h = services.CAM_H if h is None else h
    groups = []
    for i, (x, y, ax, ay, az, *fixed) in enumerate(layout):
        post, pan, tilt = services.rig_pose(x, y, (ax, ay, az), h, post=fixed[0] if fixed else None)
        g = f"cam_{k}{i}"
        services._add_rig(sc, g, f"tray_{k}", T((x, y, V.T_FLOOR)), post, h, pan, tilt,
                          post_h=post_h or services.POST_H)
        groups.append(g)
    return groups


def group_names(sc: Scene, prefix: str) -> list[str]:
    return [n for n, g in sc.group_of.items() if g == prefix or g.startswith(prefix)]


# ================================================================================================ the floor
class Floor(W.Floor):
    """warehouse.Floor on FLOOR_PLAN, plus the second Shuttle's dock and the sieving cell's bench."""

    def _stations(self):
        super()._stations()
        sc = self.sc
        self.groups["vlm2"] = []
        self.where["vlm2"] = np.array([X2, W.Y_FACE_N, V.UNIT_H])
        b = SIEVE_BENCH
        x0, x1, y0, y1 = b["x"] - b["w"] / 2, b["x"] + b["w"] / 2, W.Y_FACE_N, W.Y_FACE_N + b["d"]
        sc.add("sieve_cell/top", W._box(x0, y0, b["h"] - 30, x1, y1, b["h"]), (0.28, 0.29, 0.31), "sieve_cell",
               specular=0.2)
        sc.add("sieve_cell/legs", W._merge([W._box(x - 20, y - 20, 0, x + 20, y + 20, b["h"] - 30)
                                            for x in (x0 + 30, x1 - 30) for y in (y0 + 30, y1 - 30)]),
               (0.66, 0.67, 0.70), "sieve_cell", specular=0.4)
        try:
            import sieve_station as SS
            for name, (mesh, col, spec, op) in SS.enclosure_parts(b["w"], b["d"], b["encl_h"]).items():
                sc.add(f"sieve_cell/encl {name}", mesh.translate((b["x"], (y0 + y1) / 2, b["h"]), inplace=False),
                       col, "sieve_cell", opacity=op, specular=spec)
        except Exception as e:                       # noqa: BLE001  (the enclosure is a nicety)
            print("setup_lab: no sieving-cell enclosure:", e, flush=True)
        names = sc.members("sieve_cell")
        if "sieve" in self.idata:
            inst, ents = self.idata["sieve"]
            bb = inst.bbox()
            at = T((b["x"] + 11.5, W.Y_FACE_N + 60.0 - bb[2], b["h"] - bb[4]))
            rig = tour.Rig(self.sc, inst, ents, "wh_sieve:", at=at)
            for piece in [pc for pc in rig.names if pc in inst.props]:
                for nm in rig.names.pop(piece):
                    sc.alpha[nm] = 0.0
            self.rigs["sieve_cell"] = rig
            names += rig.all_names()
        self.groups["sieve_cell"] = names
        self.where["sieve_cell"] = np.array([b["x"], W.Y_FACE_N + 300, b["h"] + b["encl_h"]])


def footprints(sc: Scene, F: Floor) -> pv.PolyData:
    """Tape round every floor machine's footprint, from where it will stand."""
    out = []
    for key, (x0, x1, y0, y1) in machine_rects(sc, F).items():
        if key.startswith("charger"):
            continue
        out.append(W.tape_rect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0 + 160, y1 - y0 + 160, t=50.0))
    return W._merge(out)


def _bounds_of(sc: Scene, names, M_inv=None):
    """(x0, x1, y0, y1, z0, z1) of the actors `names` as placed now, in the frame M_inv maps to (world if None)."""
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for n in names:
        a = sc.actors.get(n)
        if a is None or sc.alpha.get(n, 1.0) <= 0.0 or sc.base_alpha.get(n, 1.0) <= 0.0:
            continue
        b = a.GetMapper().GetInput().GetBounds()
        if b[0] > b[1]:
            continue
        c = np.array([[x, y, z, 1.0] for x in b[:2] for y in b[2:4] for z in b[4:]])
        M = sc.world(sc.group_of[n])
        if M_inv is not None:
            M = M_inv @ M
        p = (c @ M.T)[:, :3]
        lo, hi = np.minimum(lo, p.min(0)), np.maximum(hi, p.max(0))
    return (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]) if np.isfinite(lo).all() else None


def machine_rects(sc: Scene, F: Floor) -> dict:
    """Plan rectangles (x0, x1, y0, y1) of everything that stands on the floor: the machines, the two Shuttles, the
    sieving cell, the chargers."""
    out = {}
    for key, names in F.groups.items():
        if key in ("tape", "docks", "racking", "chargers", "vlm", "vlm2") or not names:
            continue
        bb = _bounds_of(sc, [n for n in names if sc.base_alpha.get(n, 1.0) > 0.0])
        if bb is not None:
            out[key] = bb[:4]
    if "repowder" not in out:
        bb = _bounds_of(sc, sc.members("repowder"))
        if bb is not None:
            out["repowder"] = bb[:4]
    xo, yo = V.UNIT_W / 2 + V.SKIN, V.UNIT_D / 2 + V.SKIN
    out["vlm"] = (-xo, xo, -yo, yo)
    out["vlm2"] = (X2 - xo, X2 + xo, -yo, yo)
    for i, x in enumerate(W.CHARGERS):
        out[f"charger{i}"] = (x - W.CHARGER["W"] / 2, x + W.CHARGER["W"] / 2, W.Y_FACE_S - W.CHARGER["D_plate"],
                              W.Y_FACE_S)
    return out


# ================================================================================================ utilities
def junction_box(x, y, z, face):
    """A grey electrical junction box at the end of a power and network drop: two sockets and a network port on its
    face. face = -1: the face looks to -y (the north row), +1 to +y. -> {name: (mesh, colour)}."""
    w, d, h = 240.0, 120.0, 180.0
    body = W._box(x - w / 2, y - d / 2, z - h, x + w / 2, y + d / 2, z)
    yf = y + face * d / 2
    sockets, holes, port = [], [], []
    for sx in (-60.0, 30.0):
        sockets.append(W._box(x + sx - 32, yf, z - h + 60, x + sx + 32, yf + face * 6, z - h + 130))
        for dx in (-9.0, 9.0):
            holes.append(W._box(x + sx + dx - 3, yf + face * 6, z - h + 98, x + sx + dx + 3, yf + face * 7.5,
                                z - h + 110))
        holes.append(W._box(x + sx - 4, yf + face * 6, z - h + 74, x + sx + 4, yf + face * 7.5, z - h + 84))
    port.append(W._box(x + 80, yf, z - h + 80, x + 106, yf + face * 6, z - h + 104))
    return {"junction boxes": (body, (0.62, 0.64, 0.66)), "box sockets": (W._merge(sockets), (0.93, 0.93, 0.92)),
            "socket holes": (W._merge(holes), (0.10, 0.10, 0.11)), "network ports": (W._merge(port), (0.15, 0.40, 0.85))}


def utilities(hood=None) -> tuple[dict, tuple]:
    """Cable trays over both rows with a drop to each station ending in a grey junction box (sockets and a network
    port), a network cable in each tray, an argon line from a cylinder manifold to the gas users, and the fume hood's
    duct. Layout choices, drawn to read, not a design. -> ({name: (mesh, colour)}, a junction box's label point)."""
    zn, yn = 4300.0, W.Y_FACE_N + 700.0          # over the north row, above the VLM's 3950 mm roof
    zs, ys = 3200.0, W.Y_FACE_S - 600.0
    xs = (-9200.0, 11000.0)

    def tray(x0, x1, y, z):
        return W._merge([W._box(x0, y - 150, z, x1, y + 150, z + 12), W._box(x0, y - 150, z, x1, y - 138, z + 100),
                         W._box(x0, y + 138, z, x1, y + 150, z + 100)])
    trays = W._merge([tray(*xs, yn, zn), tray(xs[0] + 1200, xs[1], ys, zs)])
    hangers = W._merge([W._box(x - 15, y - 15, z + 100, x + 15, y + 15, 6000) for x in np.arange(xs[0], xs[1], 3000)
                        for y, z in ((yn, zn), (ys, zs))])
    net = W._merge([pv.Cylinder(center=((xs[0] + xs[1]) / 2, y + 60, z + 35), direction=(1, 0, 0), radius=18,
                                height=xs[1] - xs[0], resolution=16).triangulate() for y, z in ((yn, zn), (ys, zs))])
    drops, parts = [], {}
    north = {"glovebox": -7300.0, "repowder": -3640.0, "sieve_cell": -1700.0, "vlm": 900.0, "vlm2": X2 + 900.0,
             "aconity": 7300.0, "packaging": 10050.0}
    south = {"instron_floor": -6400.0, "instron_small": -4300.0, "chargers": -900.0, "fumehood": 900.0,
             "ded": 3900.0, "wire_edm": 6600.0}

    def add(d):
        for k, (m, c) in d.items():
            parts.setdefault(k, ([], c))[0].append(m)
    label = None
    for key, x in north.items():
        z_end = 3975.0 if key.startswith("vlm") else 2500.0
        drops.append(pv.Cylinder(center=(x, yn - 60, (zn + z_end) / 2), direction=(0, 0, 1), radius=22,
                                 height=zn - z_end, resolution=16).triangulate())
        if not key.startswith("vlm"):
            add(junction_box(x, yn - 60, z_end, -1))
        else:
            add({"junction boxes": (W._box(x - 120, yn - 120, z_end - 5, x + 120, yn, z_end + 150), (0.62, 0.64, 0.66))})
    for key, x in south.items():
        drops.append(pv.Cylinder(center=(x, ys + 60, (zs + 1900) / 2), direction=(0, 0, 1), radius=22,
                                 height=zs - 1900, resolution=16).triangulate())
        add(junction_box(x, ys + 60, 1900.0, +1))
        if key == "instron_small":
            label = (x, ys + 60, 1800.0)
    gas_users = [-7300.0, -3640.0, 7300.0]
    gx0 = xs[0] - 400
    ar = [pv.Cylinder(center=((gx0 + gas_users[-1]) / 2, yn + 230, zn - 150), direction=(1, 0, 0), radius=14,
                      height=gas_users[-1] - gx0, resolution=14).triangulate(),
          pv.Cylinder(center=(gx0, yn + 230, zn / 2), direction=(0, 0, 1), radius=14, height=zn,
                      resolution=14).triangulate()]
    for x in gas_users:
        ar.append(pv.Cylinder(center=(x + 200, yn + 230, (zn - 150 + 1800) / 2), direction=(0, 0, 1), radius=12,
                              height=zn - 150 - 1800, resolution=14).triangulate())
    xd = FLOOR_PLAN["ded"][0]                    # the DED's argon: down the south tray
    ar.append(pv.Cylinder(center=(gx0, (yn + 230 + ys - 200) / 2, zs - 150), direction=(0, 1, 0), radius=14,
                          height=yn + 230 - (ys - 200), resolution=14).triangulate())
    ar.append(pv.Cylinder(center=((gx0 + xd) / 2, ys - 200, zs - 150), direction=(1, 0, 0), radius=14,
                          height=xd - gx0, resolution=14).triangulate())
    ar.append(pv.Cylinder(center=(xd + 200, ys - 200, (zs - 150 + 1800) / 2), direction=(0, 0, 1), radius=12,
                          height=zs - 150 - 1800, resolution=14).triangulate())
    cyl = [pv.Cylinder(center=(gx0 - 300 + 260 * i, yn + 700, 750), direction=(0, 0, 1), radius=115, height=1500,
                       resolution=24).triangulate() for i in range(4)]
    # the ducted hood's exhaust: up from its top, behind the south cable tray, to the roof (a 180 mm duct; a layout
    # choice). hood: the hood's world bounds
    duct = None
    if hood is not None:
        z0 = hood[5]
        duct = pv.Cylinder(center=((hood[0] + hood[1]) / 2, hood[2] + 110.0, (z0 + 6200.0) / 2), direction=(0, 0, 1),
                           radius=90, height=6200.0 - z0, resolution=28).triangulate()
    out = {"cable trays": (trays, (0.70, 0.72, 0.74)), "tray hangers": (hangers, (0.55, 0.57, 0.60)),
           "network cable": (net, (0.15, 0.40, 0.85)), "power drops": (W._merge(drops), (0.30, 0.31, 0.33)),
           "argon line": (W._merge(ar), (0.25, 0.60, 0.35)), "argon cylinders": (W._merge(cyl), (0.30, 0.55, 0.36)),
           "hood duct": (duct, (0.78, 0.79, 0.81))}
    for k, (ms, c) in parts.items():
        out[k] = (W._merge(ms), c)
    return {k: v for k, v in out.items() if v[0] is not None}, label


def rig_in(sc: Scene, g, names, out=False, travel=1700.0):
    """A tray item (a group riding on its tray) comes in through the opening onto its place, as animate.item_in."""
    base = sc.gmat[g].copy()

    def up(u):
        v = u if out else 1.0 - u
        sc.gmat[g] = T((0, -travel * v, min(1.0, v * 6) * 20.0)) @ base
        for n in names:
            sc.alpha[n] = 1.0 if v < 0.7 else max(0.0, 1 - (v - 0.7) / 0.3)
    return up


def stagger(fs, overlap=0.45):
    """Run updates one after another within one step, each over `overlap` of it."""
    n = len(fs)

    def up(u):
        for i, f in enumerate(fs):
            t0 = 0.0 if n == 1 else i * (1.0 - overlap) / (n - 1)
            f(window(u, t0, t0 + overlap if n > 1 else 1.0))
    return up


# ================================================================================================ build
def build(data, idata, mp4=True):
    use_floor_plan()
    sc = Scene("setup_lab", TITLE, gif=False, mp4=mp4)       # fit: no encoder, so it leaves the MP4 alone
    sc.cam = list(CAM_ROOM)
    L = TwoLab(sc, data)
    for k in ("A", "B", "C"):
        add_tray(sc, L, k)
    for g in L.eq_groups.get("A", []):                  # round 2's CubXL stays hidden: the corrosion set-up replaces it
        if L.eq_key[g] == "cubxl" and "cubxl_corrosion" in idata:
            for nm in L.eq_names(g):
                sc.alpha[nm] = 0.0
    F = Floor(sc, L, idata)
    for k in ORDER:
        if k not in "ABC":
            add_tray(sc, L, k)
    items, rigs = {k: [] for k in ORDER}, {}
    vp = None
    for k in ORDER:
        for i, (key, x, y, turn) in enumerate(ITEMS.get(k, [])):
            if k in A.LOADS and any(it[0] == key for it in A.LOADS[k]) and key != "cubxl":
                g = next(gg for gg in L.eq_groups[k] if L.eq_key[gg] == key)
                names = L.eq_names(g) + (L.groups("vial", "vial_powder", "vial_liquid") if key == "rack" else [])
                items[k].append((key, g, names, A.NAMES.get(key, key)))
                continue
            if key == "vacuum_press":
                import alloy_press as AP
                import vacuum_press as VPm
                vp = AP.VacPress(sc, f"tray_{k}", (x, y), V.T_FLOOR)
                vp.st["guard"] = 0.0                     # stored with its guard down
                vp.apply()
                names = group_names(sc, "vpress") + group_names(sc, "vp_")
                items[k].append((key, "vpress", names, VPm.AT["model"].split(" (")[0] + ", vacuum press"))
                continue
            if key not in idata:
                print(f"setup_lab: {key} (tray {k}) not loaded: skipped", flush=True)
                continue
            inst, ents = idata[key]
            pre = f"{k}{i}_{key}:"
            rig = tour.Rig(sc, inst, ents, pre, at=placed(inst, x, y, turn), parent=f"tray_{k}")
            for piece in [pc for pc in rig.names if pc in inst.props]:
                for nm in rig.names.pop(piece):
                    sc.alpha[nm] = 0.0
            rigs[pre[:-1]] = rig
            items[k].append((key, f"{pre}body", rig.all_names(), inst.model))
        ups = add_ups(sc, k)
        items[k].append(("ups", f"ups_{k}", ups, "UPS"))
        for g in add_cams(sc, k):
            items[k].append(("cam", g, group_names(sc, g), "camera"))
    units = [W_unit(sc, i) for i in range(len(W.CHARGERS))]
    util = {}
    hood = _bounds_of(sc, F.groups["fumehood"]) if F.groups.get("fumehood") else None
    umesh, ulabel = utilities(hood)
    for nm, (mesh, col) in umesh.items():
        sc.add(f"util/{nm}", mesh, col, "util", specular=0.2)
        util[nm] = f"util/{nm}"
    L.apply_state()
    sc.apply()
    sc.add("footprints", footprints(sc, F), W.TAPE_W, "tape", specular=0.0, ambient=0.5)
    return sc, L, F, items, rigs, units, util, ulabel, vp


def W_unit(sc, i):
    return Unit(sc, f"unit{i}", W.charger_pose(i))


# ================================================================================================ the lab's units
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


# ================================================================================================ the movie
def movie(data, idata):
    sc, L, F, items, rigs, units, util, ulabel, vp = build(data, idata)
    import services
    vlm_groups = ["base", "posts", "col_front", "col_rear", "lift_rails", "drive", "lift", "belts", "bay", "console",
                  "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top"]
    u2 = [f"u2_{g}" for g in vlm_groups]
    trays = list(ORDER)
    tray_groups = [f"tray_{k}" for k in trays]
    eq = [n for k in items for _, _, names, _ in items[k] for n in names]
    floor_keys = [k for k in FLOOR_PLAN if k not in ("vlm", "vlm2") and k in F.groups]
    machines = [n for key in floor_keys for n in F.groups[key]]
    layout = F.groups["tape"] + F.groups["docks"] + ["footprints"] + \
        [n for n, g in sc.group_of.items() if g.startswith("charger") and g.endswith("_tape")]
    chargers = [n for n, g in sc.group_of.items() if g.startswith("charger") and not g.endswith("_tape")]
    unit_names = [n for u in units for n in u.all_names()]
    A.hide(L, L.groups(*vlm_groups, *u2, *tray_groups) + eq + machines + layout + chargers + unit_names +
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
    sc.step(f"2/{n}", "The layout goes down in tape first: the 3.0 m aisle, each machine's footprint, and a MiR250 dock "
            "at every front with an AprilTag target on a post. Every dock has room at its open end for a MiR to turn "
            "on the spot; nothing stands in a dock or on the way into one.", 3.0, tape_on, hold=1.8, cam_to=CAM_TOP,
            labels=W.auto(sc, CAM_TOP, [("main aisle, 3.0 m", (-7000, (W.AISLE[0] + W.AISLE[1]) / 2, 0)),
                                         ("two Kardex Shuttles", (X2 / 2, -1000, 0)),
                                         ("dock and AprilTag target", (*W.target_xy("aconity"), W.TARGET_Z)),
                                         ("charger bays", (W.CHARGERS[0], W.Y_FACE_S + 400, 0))]))
    # ------------------------------------------------------------------ 3. utilities
    names_u = list(util.values())

    def util_on(u):
        for i, nm in enumerate(names_u):
            sc.alpha[nm] = window(u, i / (len(names_u) + 1), (i + 2) / (len(names_u) + 1))
    ulbls = [("cable tray: power and network", (5200, W.Y_FACE_N + 700, 4400)),
             ("argon cylinders", (-9500, W.Y_FACE_N + 1400, 1500)),
             ("VLM supply, 208 V 3-phase", (900, W.Y_FACE_N + 640, 4300))]
    if ulabel is not None:
        ulbls.append(("power and network drop", ulabel))
    sc.step(f"3/{n}", "Utilities: cable trays over both rows. A drop comes down to every station and ends in a grey "
            "junction box with sockets and a network port. 208 V three-phase goes to each VLM (#53), argon from a "
            "cylinder manifold to the glovebox, the rePowder, the Aconity and the DED, and a duct up from the fume "
            "hood. Layout choices, not a design.", 3.6, util_on, hold=1.8, cam_to=CAM_UTIL,
            labels=W.auto(sc, CAM_UTIL, ulbls))
    # ------------------------------------------------------------------ 4. the VLMs
    s = A.slide_in
    sc.step(f"4/{n}", "Two Kardex Shuttle XP 500s go together where their footprints are taped, 800 mm apart: base "
            "frames, posts, storage columns.", 2.6,
            A.both(s(L, ["base", "u2_base"], (0, 0, 900)), s(L, ["posts", "u2_posts"], (0, 0, 1800)),
                   s(L, ["col_front", "col_rear", "u2_col_front", "u2_col_rear"], (2600, 0, 0))),
            hold=0.3, cam_to=CAM_VLM)
    sc.step(f"4/{n}", f"The extractors and their drives, then {len(trays)} empty electrified trays, A to M, each with "
            "its dock plate at the back right.", 2.6,
            A.both(s(L, ["lift_rails", "u2_lift_rails"], (0, 0, 2500)), s(L, ["drive", "u2_drive"], (0, 0, 1400)),
                   s(L, ["lift", "belts", "u2_lift", "u2_belts"], (0, 0, 2400)), s(L, tray_groups, (3200, 0, 0))),
            hold=0.3)
    sc.step(f"4/{n}", "The cladding, the openings (996 mm tall), the consoles and the shutters.", 2.2,
            A.both(s(L, ["skin_L", "u2_skin_L"], (-900, 0, 0)), s(L, ["skin_R", "u2_skin_R"], (900, 0, 0)),
                   s(L, ["skin_back", "u2_skin_back"], (0, 900, 0)), s(L, ["skin_top", "u2_skin_top"], (0, 0, 900)),
                   s(L, ["skin_front", "bay", "console", "shutter", "u2_skin_front", "u2_bay", "u2_console",
                         "u2_shutter"], (0, -900, 0))),
            hold=0.6)
    L.apply_state()
    # ------------------------------------------------------------------ 5. the floor machines
    order = [k for k in ("glovebox", "repowder", "sieve_cell", "aconity", "packaging", "instron_floor", "instron_small",
                         "fumehood", "ded", "wire_edm") if k in F.groups and F.groups[k]]
    fs = []
    for k in order:
        root = {"repowder": "repowder", "aconity": "aconity", "sieve_cell": "sieve_cell"}.get(k, f"wh_{k}:body")
        row = FLOOR_PLAN[k][1]
        names = F.groups[k]
        roots = [root] + (["wh_sieve:body"] if k == "sieve_cell" and "sieve_cell" in F.rigs else []) + \
            ([f"bench_{k}"] if k in W.BENCH else [])
        fs.append(s(L, roots, (0, -2600 if row == "N" else 2600, 0), names=names))
    sc.step(f"5/{n}", "The floor machines come in on their footprints, fronts to the aisle: the glovebox (its "
            "antechamber to the aisle), the rePowder, the sieving cell, the Aconity MIDI, the packaging station; "
            "across the aisle the two Instrons, the ducted fume hood, the DED and the wire EDM.", 5.4,
            stagger(fs, overlap=0.36), hold=1.2, cam_to=CAM_FLOOR,
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
    sc.step(f"6/{n}", "Its cabinet goes on top: it carries the arm and holds the UR control box.", 1.6, cabinet, hold=0.2)
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
    sc.step(f"7/{n}", "Loading, drawn see-through: each tray comes to its Shuttle's opening, people put its instruments, "
            "its UPS and its camera posts on through it (most weigh more than the arm's 12.5 kg), and it goes back to "
            "its slot and its power.", 2.2, L.skin(1.0), hold=0.3, cam_to=CAM_OPEN)
    L.show_gauges = True
    cam_now = CAM_OPEN
    first = set()
    for k in trays:
        lst = items.get(k, [])
        role = A.ROLE.get(k, "")
        unit = L.unit.get(k, 1)
        want = CAM_OPEN if unit == 1 else CAM_OPEN2
        cam = None if want is cam_now else want
        cam_now = want
        full = unit not in first                 # the first tray of each Shuttle at full pace, the rest quicker
        first.add(unit)
        fast, mint = (0.28, 0.6) if full else (0.17, 0.35)
        L.fetch(k, f"7/{n}", f"Tray {k} ({role}) comes to the opening of Shuttle {unit}.", fast=fast,
                hold=0.05, cam=cam, mint=mint)
        if lst:
            fs, lbls = [], []
            for key, g, names, nm in lst:
                fs.append(rig_in(sc, g, names) if key != "rack" and not g.startswith("eq_") else A.item_in(L, g))
                if key not in ("ups", "cam"):
                    lbls.append((nm, tuple(np.array(sc.world(g)[:3, 3]) + (0, 0, 420))))
            ncam = sum(1 for it in lst if it[0] == "cam")
            extra = ", its UPS" + (f" and {ncam} camera post{'s' if ncam > 1 else ''}" if ncam else "")
            cap = f"Tray {k}: " + ", ".join(lb[0] for lb in lbls) + extra + "."
            sc.step(f"7/{n}", cap, (1.0 + 0.32 * len(lst)) if full else (0.8 + 0.24 * len(lst)),
                    stagger(fs, overlap=0.5), hold=0.6 if full else 0.45, labels=W.auto(sc, cam_now, lbls, dy=0.16))
        L.store(k, f"7/{n}", f"Tray {k} goes back to its slot ({A.HOME[k]}), {V.SPAN[A.HOME[k]]:.0f} mm tall, "
                "where it has power.", fast=fast, hold=0.05, mint=mint)
    L.focus = None
    # ------------------------------------------------------------------ 8. the bay cameras
    services.add_bay_camera(sc)
    services.add_meshes(sc, "baycam2", services.meshes_of("baybar", services.bay_parts, 0.5), "baycam2")
    sc.gmat["baycam2"] = T((X2, 0, 0))
    b = services.BAY_CAM
    services._add_rig(sc, "baycamrig2", None, T((X2, b["y"], b["bar_z"] + 10.0)), 0.0, b["h"], 0.0, b["tilt"],
                      post_h=b["post_h"], foot=False)
    L.show_gauges = False
    L.apply_state()
    cam_names = [nm for nm in sc.actors if sc.group_of[nm].startswith(("baycam", "baycamrig"))]
    for nm in cam_names:
        sc.alpha[nm] = 0.0

    def cams_on(u):
        for nm in cam_names:
            sc.alpha[nm] = u
    sc.step(f"8/{n}", "The bay cameras go on, one over each opening, looking down at the presented tray (services.py). "
            "Every tray already carries its own stream cameras.", 1.8, cams_on, hold=1.4, cam_to=CAM_VLM,
            labels=W.auto(sc, CAM_VLM, [("overhead camera at the bay", services.bay_cam_point()),
                                        ("overhead camera at the bay", (X2, *services.bay_cam_point()[1:]))]))
    # ------------------------------------------------------------------ 9. orbit
    L.apply_state()
    cap = (f"Set up: two Shuttles with trays A-M, the floor machines, two MiR250 + UR10e units on charge.")
    sc.step(f"9/{n}", cap, 1.2, L.skin(0.0), hold=0.0)
    for i, cam in enumerate(ORBIT):
        last = i == len(ORBIT) - 1
        sc.step(f"9/{n}", cap, 2.4, None, hold=2.4 if last else 0.0, cam_to=cam, still=last)
    return sc.save()


# ================================================================================================ the checks
def _fcl_of(sc: Scene, names, Mi):
    """One FCL mesh of the visible actors `names`, in the frame Mi maps to (the tray's)."""
    import fcl
    vs, fs, off = [], [], 0
    for n in names:
        a = sc.actors.get(n)
        if a is None or sc.alpha.get(n, 1.0) <= 0.0 or sc.base_alpha.get(n, 1.0) <= 0.0:
            continue
        poly = pv.wrap(a.GetMapper().GetInput())
        if not poly.n_points or not poly.n_cells:
            continue
        tri = poly.triangulate()
        if not tri.faces.size:
            continue
        f = tri.faces.reshape(-1, 4)
        f = f[f[:, 0] == 3][:, 1:]
        if not len(f):
            continue
        M = Mi @ sc.world(sc.group_of[n])
        p = (np.c_[tri.points, np.ones(len(tri.points))] @ M.T)[:, :3]
        vs.append(p)
        fs.append(f + off)
        off += len(p)
    if not vs:
        return None
    bvh = fcl.BVHModel()
    v, f = np.vstack(vs), np.vstack(fs)
    bvh.beginModel(len(v), len(f))
    bvh.addSubModel(v, f)
    bvh.endModel()
    return fcl.CollisionObject(bvh, fcl.Transform())


def tray_parts(sc: Scene, items: dict, k: str) -> list:
    """[(label, kind, (x0, x1, y0, y1, z0, z1))] on tray k, in the tray's frame: its items, its UPS, its dock plate and
    tray lines, and each camera rig in two parts (the post on its foot, and the head with its yoke)."""
    Mi = np.linalg.inv(sc.world(f"tray_{k}"))
    out = []
    for key, g, names, nm in items.get(k, []):
        if key == "cam":
            post = [n for n in names if sc.group_of[n] == g]
            head = [n for n in names if sc.group_of[n] != g]
            out.append((f"{g} post", "cam", _bounds_of(sc, post, Mi), post))
            out.append((f"{g} head", "cam", _bounds_of(sc, head, Mi), head))
            continue
        out.append((nm if key != "ups" else "UPS", "ups" if key == "ups" else "item", _bounds_of(sc, names, Mi), names))
    plate = [n for n in sc.actors if n.startswith((f"plate_{k}/", f"lines_{k}/"))]
    out.append(("dock plate and tray lines", "plate", _bounds_of(sc, plate, Mi), plate))
    return [o for o in out if o[2] is not None]


def check_trays(sc: Scene, items: dict) -> dict:
    """Each tray's parts against each other: their boxes first, then, where two boxes overlap, the meshes themselves
    (FCL), so a camera head over an instrument's low corner isn't a clash."""
    import fcl
    inside = (V.TRAY_W / 2 - 12.0, V.TRAY_D / 2 - 12.0)
    edge = (V.TRAY_W / 2, V.TRAY_D / 2)
    rep = {}
    for k in ORDER:
        parts = tray_parts(sc, items, k)
        Mi = np.linalg.inv(sc.world(f"tray_{k}"))
        objs = {}

        def obj(i):
            if i not in objs:
                objs[i] = _fcl_of(sc, parts[i][3], Mi)
            return objs[i]

        def hit(i, j):
            a, b = obj(i), obj(j)
            if a is None or b is None:
                return True
            res = fcl.CollisionResult()
            return fcl.collide(a, b, fcl.CollisionRequest(), res) > 0 or res.is_collision
        rows, top = [], 0.0
        for i, (lbl, kind, b, _) in enumerate(parts):
            over = []
            for j, (lbl2, kind2, b2, _) in enumerate(parts):
                if j == i or (kind == kind2 == "cam" and lbl.split()[0] == lbl2.split()[0]):
                    continue
                if {kind, kind2} <= {"ups", "plate", "cam"} and kind != kind2:
                    continue                             # services.py's own parts against each other: its call
                if all(b[2 * a] < b2[2 * a + 1] - 1.0 and b2[2 * a] < b[2 * a + 1] - 1.0 for a in range(3)) and \
                        hit(min(i, j), max(i, j)):
                    over.append(lbl2)
            lim = edge if kind == "cam" else inside           # a camera head may lean over the rim, not the edge
            rim = kind == "plate" or (b[0] >= -lim[0] - 0.5 and b[1] <= lim[0] + 0.5 and b[2] >= -lim[1] - 0.5
                                      and b[3] <= lim[1] + 0.5)
            h = b[5] - V.T_FLOOR
            top = max(top, b[5])
            rows.append(dict(item=lbl, kind=kind, box_mm=[round(float(v)) for v in b], height_mm=round(float(h), 1),
                             under_goods_height=bool(h <= V.MAX_GOODS_H + 0.5), inside_rim=bool(rim),
                             overlaps=over))
        slot = TRAYS[k][0]
        need = V.PITCH * math.ceil((top + V.GOODS_CLEAR - 1e-6) / V.PITCH)
        rep[k] = dict(role=TRAYS[k][1], slot=slot, shuttle=V.SLOT_SHUTTLE[slot], slot_z_mm=V.SLOTS[slot][1],
                      span_mm=V.SPAN[slot], tallest_mm=round(float(top - V.T_FLOOR), 1), span_needed_mm=need,
                      span_ok=bool(need <= V.SPAN[slot]), items=rows,
                      ok=bool(need <= V.SPAN[slot] and all(not r["overlaps"] and r["inside_rim"] and
                                                           r["under_goods_height"] for r in rows)))
    return rep


def _rect_circle(rect, c, r):
    x0, x1, y0, y1 = rect
    dx = max(x0 - c[0], 0.0, c[0] - x1)
    dy = max(y0 - c[1], 0.0, c[1] - y1)
    return dx * dx + dy * dy < r * r


def _rects_hit(a, b, m=0.0):
    return a[0] < b[1] + m and b[0] < a[1] + m and a[2] < b[3] + m and b[2] < a[3] + m


def check_floor(sc: Scene, F: Floor) -> dict:
    """Every dock: the docked MiR250, its approach along the dock line from the pivot spot at its open end, and the
    pivot itself (a circle of the MiR's half-diagonal), against every machine's plan rectangle and every target post's
    foot; and the aisle against the machines. Margin 30 mm."""
    m = 30.0
    rects = machine_rects(sc, F)
    Lm, Wm = P.MIR["L"], P.MIR["W"]
    r_piv = math.hypot(Lm / 2, Wm / 2)
    posts = {k: tuple(W.target_xy(k)) for k in FLOOR_PLAN if k in F.groups or k in ("vlm", "repowder")}
    feet = {k: (x - 150, x + 150, y - 150, y + 150) for k, (x, y) in posts.items()}
    docks = {}
    for key in posts:
        x, y, hd = W.dock_pose(key)
        fwd = 1.0 if abs(hd) < 1 else -1.0                    # along +x (north row) or -x (south)
        back = key in W.BACK_IN
        open_dir = fwd if back else -fwd                      # the end it comes in from
        docked = (x - Lm / 2, x + Lm / 2, y - Wm / 2, y + Wm / 2)
        piv, hits = None, []
        for d in np.arange(Lm / 2 + 50.0, 4000.0, 25.0):        # the nearest clear pivot spot on the dock line
            c = (x + open_dir * d, y)
            if not any(_rect_circle(rr, c, r_piv + m) for kk, rr in rects.items()) and \
                    not any(_rect_circle(ff, c, r_piv + m) for kk, ff in feet.items()):
                piv = c
                break
        if piv is None:
            hits.append("no pivot spot within 4 m")
        else:
            lane = (min(x, piv[0]) - Lm / 2, max(x, piv[0]) + Lm / 2, y - Wm / 2, y + Wm / 2)
            hits += [kk for kk, rr in rects.items() if _rects_hit(lane, rr, m)]
            hits += [f"post {kk}" for kk, ff in feet.items() if kk != key and _rects_hit(lane, ff, 0.0)]
            ff = feet[key]
            if _rects_hit(docked, ff, 0.0):
                hits.append("its own post under the docked MiR")
        docks[key] = dict(dock=[round(x), round(y), round(hd)], backs_in=back,
                          pivot=None if piv is None else [round(piv[0]), round(piv[1])],
                          approach_mm=None if piv is None else round(abs(piv[0] - x)),
                          target_post=[round(v) for v in posts[key]], hits=sorted(set(hits)), ok=not hits)
    aisle = (W.X_END[0], W.X_END[1], W.AISLE[1], W.AISLE[0])
    in_aisle = [k for k, rr in rects.items() if _rects_hit(aisle, rr, 0.0)]
    return dict(docks=docks, machines={k: [round(v) for v in r] for k, r in rects.items()},
                aisle_mm=[round(v) for v in aisle], machines_in_aisle=in_aisle,
                ok=bool(all(d["ok"] for d in docks.values()) and not in_aisle),
                method=" ".join(check_floor.__doc__.split()))


def draw_plan(rep: dict, path):
    """Every tray from above, its items, UPS, dock plate and camera posts, with its slot; and both Shuttles' columns."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    cols = {"item": "#4a7bd0", "ups": "#e0a020", "plate": "#c8553d", "cam": "#2e9c6a"}
    trays = [k for k in ORDER]
    nrow = math.ceil(len(trays) / 2)
    fig = plt.figure(figsize=(18, 2.35 * nrow), dpi=110)
    gs = fig.add_gridspec(nrow, 3, width_ratios=[1, 1, 0.55], wspace=0.06, hspace=0.55, top=0.95)
    for i, k in enumerate(trays):
        ax = fig.add_subplot(gs[i % nrow, i // nrow])
        r = rep[k]
        ax.add_patch(Rectangle((-V.TRAY_W / 2, -V.TRAY_D / 2), V.TRAY_W, V.TRAY_D, fc="#eceef0", ec="#555", lw=1.0))
        ax.add_patch(Rectangle((-V.TRAY_W / 2 + 12, -V.TRAY_D / 2 + 12), V.TRAY_W - 24, V.TRAY_D - 24, fc="none",
                               ec="#999", lw=0.6, ls=":"))
        for it in r["items"]:
            x0, x1, y0, y1 = it["box_mm"][:4]
            bad = it["overlaps"] or not it["inside_rim"] or not it["under_goods_height"]
            kind = it["kind"]
            alpha = 0.35 if it["item"].endswith("head") else 0.75
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=cols[kind], alpha=alpha,
                                   ec="red" if bad else "#222", lw=1.4 if bad else 0.5))
            if kind == "item":
                ax.text((x0 + x1) / 2, (y0 + y1) / 2, f"{it['item'][:26]}\n{it['height_mm']:.0f} mm", ha="center",
                        va="center", fontsize=6.0, color="white")
        ax.set_xlim(-V.TRAY_W / 2 - 30, V.TRAY_W / 2 + 30)
        ax.set_ylim(-V.TRAY_D / 2 - 30, V.TRAY_D / 2 + 30)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ok = "fits" if r["ok"] else "CHECK"
        ax.set_title(f"Tray {k}: {r['role']}\nShuttle {r['shuttle']}, slot {r['slot']}: {r['span_mm']:.0f} mm "
                     f"(needs {r['span_needed_mm']:.0f}; tallest {r['tallest_mm']:.0f}): {ok}", fontsize=8,
                     loc="left")
        ax.text(0, -V.TRAY_D / 2 - 22, "front: the opening, where the arm works", ha="center", va="top", fontsize=5.5,
                color="#555")
    ax = fig.add_subplot(gs[:, 2])
    for u, x in V.SHUTTLE_X.items():
        for slot, (y, z) in V.SLOTS.items():
            if slot == "open" or V.SLOT_SHUTTLE[slot] != u:
                continue
            xc = (0.0 if y > 0 else -1.05) + (u - 1) * 2.4
            tray = next((k for k, (s, _) in TRAYS.items() if s == slot), None)
            span = V.SPAN[slot]
            ax.add_patch(Rectangle((xc, z), 0.95, span, fc="#dfe8f5" if tray else "#f4f4f4", ec="#456", lw=0.7))
            if tray:
                need = rep[tray]["span_needed_mm"]
                ax.add_patch(Rectangle((xc, z), 0.95, rep[tray]["tallest_mm"] + V.T_FLOOR, fc="#4a7bd0", alpha=0.45,
                                       ec="none"))
                ax.text(xc + 0.475, z + span / 2, f"{slot}: tray {tray}\n{span:.0f} (needs {need:.0f})",
                        ha="center", va="center", fontsize=6.4)
            else:
                ax.text(xc + 0.475, z + span / 2, f"{slot}: free\n{span:.0f}", ha="center", va="center", fontsize=6.4,
                        color="#777")
        x0 = (u - 1) * 2.4 - 1.05
        ax.add_patch(Rectangle((x0, V.Z_SILL), 0.95, V.OPEN_H, fc="#fff7e0", ec="#c90", lw=0.8))
        ax.text(x0 + 0.475, V.Z_SILL + V.OPEN_H / 2, f"opening\n{V.OPEN_H:.0f} mm\ngoods\n{V.MAX_GOODS_H:.1f}",
                ha="center", va="center", fontsize=6.0, color="#963")
        ax.text(x0 + 1.0, V.UNIT_H + 90, f"Shuttle {u}" + (" (x = 0)" if u == 1 else f" (x = {x:.0f} mm)"),
                ha="center", fontsize=8)
        ax.text(x0 + 0.475, 120, "front", ha="center", fontsize=6.5, color="#555")
        ax.text(x0 + 1.525, 120, "rear", ha="center", fontsize=6.5, color="#555")
    ax.axhline(V.Z_TOP_IN, color="#999", lw=0.6, ls="--")
    ax.text(3.6, V.Z_TOP_IN + 30, "drive bay", fontsize=6, ha="right", color="#777")
    ax.set_xlim(-1.2, 3.8)
    ax.set_ylim(0, V.UNIT_H + 250)
    ax.set_xticks([])
    ax.set_ylabel("height over the floor, mm (tray bottoms; 25 mm pitch)", fontsize=7)
    ax.tick_params(labelsize=6.5)
    fig.suptitle("The tray plan: every tray from above, front (the opening) at the bottom. Items blue, UPS amber, "
                 "dock plate and tray lines red, camera posts and heads green; a red outline is a clash.\nRight: the "
                 "two Shuttles' columns, each slot as tall as its tray needs (setup_lab.py fit)", fontsize=10.5,
                 x=0.12, y=0.995, ha="left")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def draw_floor(frep: dict, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    fig, ax = plt.subplots(figsize=(16, 7.2), dpi=110)
    a = frep["aisle_mm"]
    ax.add_patch(Rectangle((a[0], a[2]), a[1] - a[0], a[3] - a[2], fc="#fff6cf", ec="#d8b400", lw=0.8))
    ax.text(a[0] + 200, (a[2] + a[3]) / 2, "aisle, 3.0 m", fontsize=8, va="center", color="#8a7300")
    for k, (x0, x1, y0, y1) in frep["machines"].items():
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#9aa6b5", ec="#334", lw=0.7, alpha=0.8))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, W.NAMES.get(k, k).split(":")[0], ha="center", va="center", fontsize=6.5)
    Lm, Wm = P.MIR["L"], P.MIR["W"]
    for k, d in frep["docks"].items():
        x, y, _ = d["dock"]
        c = "#2e9c6a" if d["ok"] else "#d03030"
        ax.add_patch(Rectangle((x - Lm / 2, y - Wm / 2), Lm, Wm, fc=c, alpha=0.35, ec=c, lw=0.8))
        if d["pivot"]:
            px, py = d["pivot"]
            ax.add_patch(Circle((px, py), math.hypot(Lm / 2, Wm / 2), fc="none", ec=c, lw=0.7, ls="--"))
            ax.annotate("", xy=(x, y), xytext=(px, py), arrowprops=dict(arrowstyle="->", color=c, lw=0.8))
        tx, ty = d["target_post"]
        ax.add_patch(Rectangle((tx - 150, ty - 150), 300, 300, fc="#222", ec="none"))
    ax.set_aspect("equal")
    ax.set_xlim(-10800, 11800)
    ax.set_ylim(-9300, 1900)
    ax.set_xlabel("x, mm", fontsize=7)
    ax.set_ylabel("y, mm", fontsize=7)
    ax.tick_params(labelsize=6.5)
    ok = "every dock clear" if frep["ok"] else "CHECK: " + ", ".join(k for k, d in frep["docks"].items() if not d["ok"])
    ax.set_title("The floor plan for MiR250 docking: docked MiR (green), the pivot spot it turns on (dashed) and its "
                 f"way in, target posts (black). {ok}", fontsize=9, loc="left")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fit(data, idata) -> dict:
    sc, L, F, items, rigs, units, util, ulabel, vp = build(data, idata, mp4=False)
    L.apply_state()
    rep = check_trays(sc, items)
    frep = check_floor(sc, F)
    out = dict(trays=rep, floor=frep, slots={k: dict(y=v[0], z=v[1], span=V.SPAN.get(k), shuttle=V.SLOT_SHUTTLE[k])
                                             for k, v in V.SLOTS.items()},
               shuttle_x=V.SHUTTLE_X, max_goods_h_mm=V.MAX_GOODS_H, goods_clear_mm=V.GOODS_CLEAR,
               method="setup_lab.py fit: each item, UPS, dock plate (with its tray lines) and camera rig measured from "
                      "its meshes as drawn, an axis-aligned box in the tray's frame; overlaps are 3-D box overlaps "
                      "of more than 1 mm; a slot needs the tallest top + 20 mm, on the 25 mm pitch")
    (OUT / "tray_plan.json").write_text(json.dumps(out, indent=1) + "\n")
    draw_plan(rep, OUT / "tray_plan.png")
    draw_floor(frep, OUT / "tray_plan_floor.png")
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    data = lab.meshes()
    idata = load_all()
    if args and args[0] == "fit":
        out = fit(data, idata)
        for k, r in out["trays"].items():
            bad = [(it["item"], it["overlaps"], it["inside_rim"], it["under_goods_height"]) for it in r["items"]
                   if it["overlaps"] or not it["inside_rim"] or not it["under_goods_height"]]
            print(f"tray {k} {r['slot']}: span {r['span_mm']:.0f}, needs {r['span_needed_mm']:.0f} "
                  f"(tallest {r['tallest_mm']:.0f}) {'ok' if r['ok'] else 'CHECK'} {bad if bad else ''}")
        if "-v" in args:
            for k, r in out["trays"].items():
                print("tray", k)
                for it in r["items"]:
                    print("   ", it["item"][:40].ljust(40), it["box_mm"], it["overlaps"], it["inside_rim"])
        for k, d in out["floor"]["docks"].items():
            print(f"dock {k}: {'ok' if d['ok'] else 'CHECK'} pivot {d['pivot']} {d['hits']}")
        print("machines in the aisle:", out["floor"]["machines_in_aisle"])
    else:
        print(movie(data, idata), flush=True)
        if not PREVIEW:
            print(line.mp4_to_gif(OUT / "mp4" / "setup_lab.mp4", OUT / "setup_lab.gif", **W.GIF), flush=True)

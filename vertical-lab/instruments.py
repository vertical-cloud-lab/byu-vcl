"""Characterization, sample-prep and test instruments for the vertical cloud lab, each its own model (#303).

Every instrument is an ``Instrument``: named pieces (``body`` stays put; doors, drawers, stages, crossheads and
samples move), a ``Joint`` per moving piece, and a short ``actions`` script that ``tour.py`` plays: the XRD's chamber
door opening and closing, a sample going onto the PIP's anvil, the SEM's stage drawer, and so on. The pieces are
``lab_models`` Models (CadQuery solids with materials), the same as #199's equipment, except where real CAD exists:
the OpenFlexure microscopes are OpenFlexure's own OpenSCAD, exported here (``openflexure.py``).

Frame, as in ``lab_models/equipment.py``: x to the right and y away from you when you face the front, z up from the
bench or floor it stands on, origin at the centre of the footprint, millimetres.

Each model gets its envelope from the maker's published W x D x H (``SPECS``, with the source of every figure) and
its layout from the maker's product photos; the proportions in between are read off those photos and are
approximate. Where a figure is an estimate, ``SPECS`` says so. None of the makers below publishes CAD.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import Model, box, cyl, rbox, tube  # noqa: E402

# name: (r, g, b, opacity, specular), merged into lab.MATS by tour.py
MATERIALS = {
    "inst_white": (0.94, 0.94, 0.93, 1.0, 0.25),
    "inst_offwhite": (0.86, 0.87, 0.86, 1.0, 0.25),
    "inst_light": (0.76, 0.77, 0.79, 1.0, 0.30),
    "inst_grey": (0.52, 0.54, 0.56, 1.0, 0.30),
    "inst_dark": (0.22, 0.23, 0.25, 1.0, 0.30),
    "inst_black": (0.09, 0.09, 0.10, 1.0, 0.30),
    "inst_blue": (0.10, 0.36, 0.66, 1.0, 0.30),
    "inst_navy": (0.10, 0.18, 0.36, 1.0, 0.30),
    "inst_red": (0.78, 0.12, 0.12, 1.0, 0.30),
    "inst_green": (0.20, 0.62, 0.32, 1.0, 0.30),
    "inst_orange": (0.95, 0.50, 0.10, 1.0, 0.30),
    "inst_purple": (0.52, 0.27, 0.72, 1.0, 0.30),
    "vention_blue": (0.12, 0.22, 0.45, 1.0, 0.45),      # Vention's dark blue anodizing
    "inst_yellow": (0.98, 0.80, 0.15, 1.0, 0.25),
    "stainless": (0.72, 0.73, 0.75, 1.0, 0.75),
    "chrome": (0.85, 0.86, 0.88, 1.0, 0.95),
    "window": (0.66, 0.80, 0.88, 0.30, 0.9),
    "lead_glass": (0.55, 0.50, 0.32, 0.42, 0.9),        # X-ray shielding window, faintly amber
    "polycarb": (0.78, 0.86, 0.90, 0.28, 0.9),
    "screen_on": (0.18, 0.40, 0.62, 1.0, 0.8),
    "sample": (0.80, 0.81, 0.83, 1.0, 0.85),            # a polished metal coupon
    "mount": (0.12, 0.12, 0.14, 1.0, 0.4),              # a phenolic metallographic mount
    "cloth": (0.86, 0.82, 0.72, 1.0, 0.05),             # polishing cloth
    "glow": (1.00, 0.42, 0.08, 1.0, 0.1),               # a hot furnace chamber
    "refractory": (0.93, 0.90, 0.82, 1.0, 0.05),
    "laser": (0.95, 0.08, 0.08, 0.85, 0.0),
    "glove": (0.08, 0.08, 0.09, 1.0, 0.2),              # butyl gloves
    "brass_wire": (0.86, 0.68, 0.28, 1.0, 0.7),
    "water": (0.35, 0.60, 0.80, 0.45, 0.8),
    "powder": (0.45, 0.46, 0.48, 1.0, 0.05),
}


# ===================================================================================================== joints
def _T(v) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = v
    return m


def _R(axis, deg, pivot=(0, 0, 0)) -> np.ndarray:
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    rot = np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                    [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                    [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])
    m = np.eye(4)
    m[:3, :3] = rot
    p = np.asarray(pivot, float)
    return _T(p) @ m @ _T(-p)


@dataclass
class Joint:
    """How a piece moves with a value v (0 = as modelled, 1 = the far end of its travel).

    slide: translate by v * vec.  hinge/spin: rotate v * deg about axis through pivot.  path: translate along the
    waypoints (offsets from the modelled position), evenly by arc length.  fade: only its opacity follows v.
    follow: a linkage driven by another piece's displacement d, which is v * vec or, given a path, the path's offset
    at v (as slide and path move that piece): the matrix is I + sum_k d[k] * jac[k], jac being three 3x4 matrices,
    the motion per mm of d along x, y and z. For small motions, such as flexure legs and levers (openflexure.py).
    A piece with a parent rides on that piece."""
    kind: str
    vec: tuple = (0.0, 0.0, 0.0)
    axis: tuple = (0.0, 0.0, 1.0)
    pivot: tuple = (0.0, 0.0, 0.0)
    deg: float = 0.0
    path: tuple = ()
    parent: str | None = None
    v0: float = 0.0                  # the value it starts at in the tour
    jac: tuple = ()                  # follow: three 3x4 matrices

    def matrix(self, v: float) -> np.ndarray:
        if self.kind == "follow":
            d = Joint("path", path=self.path).matrix(v)[:3, 3] if self.path else np.asarray(self.vec, float) * v
            m = np.eye(4)
            m[:3] += np.tensordot(d, np.asarray(self.jac, float), axes=1)
            return m
        if self.kind == "slide":
            return _T(np.asarray(self.vec, float) * v)
        if self.kind in ("hinge", "spin"):
            return _R(self.axis, self.deg * v, self.pivot)
        if self.kind == "path":
            pts = np.asarray(self.path, float)
            seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
            s = np.concatenate([[0], np.cumsum(seg)])
            if s[-1] <= 0:
                return _T(pts[0])
            t = min(max(v, 0.0), 1.0) * s[-1]
            i = min(int(np.searchsorted(s, t, side="right")) - 1, len(seg) - 1)
            f = (t - s[i]) / max(seg[i], 1e-9)
            return _T(pts[i] + (pts[i + 1] - pts[i]) * f)
        return np.eye(4)


@dataclass
class Instrument:
    key: str
    title: str                       # what it is, e.g. "Benchtop X-ray diffractometer"
    model: str                       # the maker's product, e.g. "Rigaku MiniFlex"
    size: tuple                      # published W x D x H, mm, closed
    source: str                      # where the envelope and look come from
    pieces: dict = field(default_factory=dict)     # name -> Model; "body" does not move
    joints: dict = field(default_factory=dict)     # name -> Joint
    actions: list = field(default_factory=list)    # [(caption, seconds, {piece: (v0, v1)})]
    labels: list = field(default_factory=list)     # [(text, (x, y, z), (fx, fy))] leader labels for the tour
    notes: list = field(default_factory=list)      # what to know, for the README
    floor: bool = False              # stands on the floor (beside the VLM) rather than a tray
    cam: tuple = (1.0, -1.6, 0.9)    # camera direction for the tour, scaled by the instrument's size
    framing: tuple = ()              # (pad, look_z) for the tour's camera, when the default doesn't suit
    meshes: dict = field(default_factory=dict)     # name -> [(PolyData, rgb, opacity)]: pieces that are meshes, not CAD
    zoom: dict = field(default_factory=dict)       # action index -> ((x, y, z), distance mm): the camera moves in;
                                                   # -> "out": back to the whole instrument (tour.py)
    props: tuple = ("load", "sample", "specimen", "holder", "stub", "slide", "beam", "glow", "powder")  # not the machine

    def bbox(self, all_pieces=False) -> tuple:
        """(xmin, xmax, ymin, ymax, zmin, zmax) of the machine (every piece but the props) in its modelled position."""
        lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
        for name, m in self.pieces.items():
            if not m.parts or (name in self.props and not all_pieces):
                continue
            bb = m.bbox()
            lo = np.minimum(lo, (bb.xmin, bb.ymin, bb.zmin))
            hi = np.maximum(hi, (bb.xmax, bb.ymax, bb.zmax))
        for name, parts in self.meshes.items():
            if name in self.props and not all_pieces:
                continue
            for mesh, _, _ in parts:
                b = mesh.bounds
                lo = np.minimum(lo, (b[0], b[2], b[4]))
                hi = np.maximum(hi, (b[1], b[3], b[5]))
        return (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])


def _piece(inst: Instrument, name: str) -> Model:
    if name not in inst.pieces:
        inst.pieces[name] = Model(f"{inst.key}_{name}", f"{inst.model}: {name}")
    return inst.pieces[name]


def _wedge(w, d0, d1, h, x=0.0, y0=0.0, z=0.0) -> cq.Workplane:
    """A box w wide whose depth goes from d0 at the bottom to d1 at the top (a sloped front), back face at y0 + d0
    ... drawn as a prism in the YZ plane, extruded along x and centred on x."""
    pts = [(y0, 0), (y0 + d0, 0), (y0 + d0, h), (y0 + d0 - d1, h)]
    return cq.Workplane("YZ").polyline(pts).close().extrude(w).translate((x - w / 2, 0, z))


def _xcyl(d, L, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    """Cylinder along +x from x."""
    return cq.Workplane("YZ").circle(d / 2).extrude(L).translate((x, y, z))


def _ycyl(d, L, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    """Cylinder along +y from y."""
    return cq.Workplane("XZ").circle(d / 2).extrude(-L).translate((x, y, z))


# ===================================================================================================== furnace
# Nabertherm NAT 15/65, a forced-convection chamber furnace: 470 W x 790 D x 460 H mm, 60 kg, 15 L, up to 650 C with
# +-5 C uniformity, sold for solution annealing and ageing (Nabertherm's forced-convection tabletop range). One furnace
# covers both steps for the Al alloys (~530 C, then ~160-200 C). A muffle furnace like the L 9/11 is only specified to
# +-5 K above 800 C, and its lift-door LT version stands 755 mm tall with the door up. Look from Nabertherm's photos
# of the NAT series: textured stainless housing; the door fills the upper two thirds of the front, hinged on the
# right, with a black lever latch on the left; the controller strip below it; the circulation fan in the back wall.
FURNACE = dict(W=470.0, D=790.0, H=460.0, feet=20.0, ctrl_h=120.0, ch_w=300.0, ch_d=340.0, ch_h=150.0, door_t=80.0)


def furnace() -> Instrument:
    p = FURNACE
    inst = Instrument("furnace", "Heat treatment and ageing furnace", "Nabertherm NAT 15/65", (p["W"], p["D"], p["H"]),
                      "Nabertherm forced-convection chamber furnaces, tabletop (NAT 15/65: 470 x 790 x 460 mm, 60 kg, "
                      "650 C); look from Nabertherm's photos")
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    cw, cd, chh = p["ch_w"], p["ch_d"], p["ch_h"]
    cz = p["feet"] + p["ctrl_h"] + 45          # chamber floor
    dz0, dz1 = p["feet"] + p["ctrl_h"] + 5, H - 10
    body = _piece(inst, "body")
    body.add("feet", box(-W / 2 + 15, yf + 15, 0, -W / 2 + 55, D / 2 - 15, p["feet"]).union(
        box(W / 2 - 55, yf + 15, 0, W / 2 - 15, D / 2 - 15, p["feet"])), "inst_black")
    shell = box(-W / 2, yf + p["door_t"], p["feet"], W / 2, D / 2, H).edges("|Y").fillet(10)
    shell = shell.cut(box(-cw / 2, yf + p["door_t"] - 1, cz, cw / 2, yf + p["door_t"] + cd, cz + chh))
    body.add("housing", shell, "stainless")
    body.add("front frame", box(-W / 2, yf + p["door_t"] - 6, p["feet"], W / 2, yf + p["door_t"], dz0)
             .union(box(-W / 2, yf + 20, p["feet"], W / 2, yf + p["door_t"], dz0)), "stainless")
    body.add("controller strip", box(-W / 2 + 20, yf + 16, p["feet"] + 15, W / 2 - 20, yf + 20, dz0 - 15), "inst_black")
    body.add("controller screen", box(W / 2 - 190, yf + 14, p["feet"] + 30, W / 2 - 50, yf + 16, dz0 - 30), "screen_on")
    body.add("power switch", box(-W / 2 + 40, yf + 12, p["feet"] + 45, -W / 2 + 70, yf + 16, p["feet"] + 75), "inst_green")
    body.add("chamber", box(-cw / 2, yf + p["door_t"] + cd - 4, cz, cw / 2, yf + p["door_t"] + cd, cz + chh).union(
        box(-cw / 2, yf + p["door_t"], cz - 4, cw / 2, yf + p["door_t"] + cd, cz)), "stainless")
    body.add("fan guard", _ycyl(130, 6, y=yf + p["door_t"] + cd - 10, z=cz + chh / 2).cut(
        _ycyl(110, 8, y=yf + p["door_t"] + cd - 11, z=cz + chh / 2)), "steel")
    body.add("exhaust", cyl(40, 50, y=D / 2 - 90, z=H), "stainless")
    fan = _piece(inst, "fan")
    fz, fy = cz + chh / 2, yf + p["door_t"] + cd - 12
    for i in range(4):
        blade = box(-50, -2, -8, 50, 2, 8).rotate((0, 0, 0), (0, 1, 0), i * 45.0)
        fan.add(f"blade {i}", blade.translate((0, fy, fz)), "steel")
    door = _piece(inst, "door")
    door.add("door", box(-W / 2 + 4, yf, dz0, W / 2 - 4, yf + p["door_t"] - 8, dz1).edges("|Y").fillet(8), "stainless")
    door.add("door logo", box(W / 2 - 150, yf - 1, dz1 - 60, W / 2 - 40, yf, dz1 - 35), "inst_yellow")
    door.add("door latch", box(-W / 2 + 25, yf - 30, (dz0 + dz1) / 2 - 50, -W / 2 + 45, yf, (dz0 + dz1) / 2 + 50),
             "inst_black")
    load = _piece(inst, "load")
    load.add("tray", box(-110, -80, 0, 110, 80, 8).cut(box(-104, -74, 3, 104, 74, 9)), "stainless")
    for i, x in enumerate((-60, 0, 60)):
        load.add(f"coupon {i + 1}", box(x - 8, -60, 3, x + 8, 60, 7), "sample")
    chamber_c = (0.0, yf + p["door_t"] + cd / 2, cz)
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(W / 2 - 4, yf, 0), deg=100.0),   # free edge out to the front
        # the tray waits to the left, outside the door's swing (a 462 mm radius about the hinge)
        "load": Joint("path", path=((-330, yf - 330, cz + 80), (0, yf - 60, cz + 10), chamber_c)),
        "fan": Joint("spin", axis=(0, 1, 0), pivot=(0, fy, fz), deg=1440.0),
    }
    inst.actions = [
        ("The door swings open on its right-hand hinge.", 1.6, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("A tray of printed tensile coupons goes in.", 1.8, {"load": (0.0, 1.0)}),
        ("Door shut. Solution treatment at about 530 C, quench, then ageing at 160-200 C: the circulation fan holds "
         "+-5 C, so one furnace does both.", 3.0, {"door": (1.0, 0.0), "fan": (0.0, 1.0), "~door": (0.0, 0.7)}),
        ("", 0.8, {"~door": (0.7, 0.0)}),
    ]
    inst.labels = [("swing door", (W / 2 - 40, yf - 2, dz1 - 40), (0.80, 0.18)),     # near the hinge: stays on it
                   ("controller", (W / 2 - 120, yf + 14, p["feet"] + 70), (0.84, 0.72))]
    inst.cam = (0.9, -1.7, 0.8)
    inst.framing = (0.95, 0.40)              # room on the left for the tray waiting outside the door's swing
    return inst


# ===================================================================================================== Instron
def _dogbone(L=100.0, w=10.0, grip_w=20.0, t=3.0, gauge=40.0) -> cq.Workplane:
    """A flat tensile specimen standing along z, centred on the origin, thickness along y."""
    half = L / 2
    shape = (cq.Workplane("XZ").polyline([
        (-grip_w / 2, -half), (grip_w / 2, -half), (grip_w / 2, -gauge / 2 - 12), (w / 2, -gauge / 2),
        (w / 2, gauge / 2), (grip_w / 2, gauge / 2 + 12), (grip_w / 2, half), (-grip_w / 2, half),
        (-grip_w / 2, gauge / 2 + 12), (-w / 2, gauge / 2), (-w / 2, -gauge / 2), (-grip_w / 2, -gauge / 2 - 12)])
        .close().extrude(t / 2, both=True))
    return shape


def _wedge_grip(z, up=True, w=90.0, h=110.0) -> cq.Workplane:
    """A wedge-action grip body: a block with a tapered nose and a slot for the specimen."""
    g = rbox(w, 70, h, 6, z=z if up else z - h)
    slot = box(-14, -3, (z - 1) if up else (z - h - 1), 14, 3, (z + h + 1) if up else (z + 1))
    return g.cut(slot)


# Instron 6800 Series floor model 68FM-100 (100 kN): 2287 H x 1140 W x 786 D mm, 799 kg; 1494 mm of vertical test
# space, 575 mm between the columns; short base about 500 mm (Instron's 6800 Series floor-model sheet). The look from
# Instron's photos: matte black frame, ribbed columns, satin-silver worktop edge, red Instron logo on the crosshead and
# base, a red-and-silver load cell, and the dashboard, handset and e-stop on the right column.
INSTRON_FM = dict(W=1140.0, D=786.0, H=2287.0, base_h=500.0, col_dx=575.0, col_w=200.0, col_d=260.0, xh_h=200.0,
                  top_h=150.0, xh_z=1250.0, travel=160.0)


def _ribbed_column(w, d, h, x, y, z) -> cq.Workplane:
    c = rbox(w, d, h, 10, x=x, y=y, z=z)
    for i in range(5):                        # vertical ribs on the front cover
        xx = x - w / 2 + w * (i + 1) / 6
        c = c.cut(box(xx - 3, y - d / 2 - 1, z + 30, xx + 3, y - d / 2 + 4, z + h - 30))
    return c


def instron_floor() -> Instrument:
    p = INSTRON_FM
    inst = Instrument("instron_floor", "Universal testing machine, floor model", "Instron 68FM-100",
                      (p["W"], p["D"], p["H"]), "Instron 6800 Series floor-model sheet (2287 x 1140 x 786 mm, 799 kg, "
                      "1494 mm test space, 575 mm between columns); look from Instron's photos", floor=True)
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    body = _piece(inst, "body")
    base = box(-W / 2, yf, 0, W / 2, D / 2, p["base_h"] - 30).edges("|Z").fillet(40)
    body.add("base", base, "inst_dark")
    body.add("worktop", rbox(W + 10, D + 10, 30, 40, z=p["base_h"] - 30), "aluminium")
    body.add("base logo", box(-W / 2 + 70, yf - 2, p["base_h"] - 120, -W / 2 + 250, yf, p["base_h"] - 80), "inst_red")
    body.add("base recess", box(-W / 2 + 60, yf - 1, 60, W / 2 - 60, yf + 4, p["base_h"] - 160), "inst_black")
    cx = p["col_dx"] / 2 + p["col_w"] / 2
    for sx in (-1, 1):
        body.add(f"column {'LR'[sx > 0]}", _ribbed_column(p["col_w"], p["col_d"], H - p["base_h"] - p["top_h"],
                                                         sx * cx, 0, p["base_h"]), "inst_black")
    body.add("top plate", rbox(p["col_dx"] + 2 * p["col_w"] + 40, p["col_d"] + 40, p["top_h"], 16, z=H - p["top_h"]),
             "inst_dark")
    body.add("lower grip", _wedge_grip(p["base_h"] + 90, up=True), "steel")
    body.add("lower adapter", cyl(70, 90, z=p["base_h"]), "steel")
    xr = cx + p["col_w"] / 2
    body.add("handset", rbox(90, 50, 150, 8, x=xr + 30, y=-p["col_d"] / 2 + 40, z=1100), "inst_dark")
    body.add("e-stop", _ycyl(40, 20, x=xr + 30, y=-p["col_d"] / 2 - 5, z=1320), "inst_red")
    body.add("e-stop label", box(xr + 5, -p["col_d"] / 2 + 13, 1295, xr + 55, -p["col_d"] / 2 + 15, 1345), "inst_yellow")
    body.add("dashboard arm", box(xr, -20, 1480, xr + 260, 20, 1510), "inst_dark")
    body.add("dashboard", box(xr + 220, -150, 1390, xr + 520, -120, 1610).rotate((xr + 370, -135, 1500),
                                                                                  (xr + 370, -135, 1501), 25),
             "inst_black")
    body.add("dashboard screen", box(xr + 235, -152, 1405, xr + 505, -150, 1595).rotate((xr + 370, -135, 1500),
                                                                                        (xr + 370, -135, 1501), 25),
             "screen_on")
    xh = _piece(inst, "crosshead")
    z = p["xh_z"]
    # its ends run in the columns, on the screws at their centrelines (it poked out of their outer sides)
    xh.add("crosshead", rbox(p["col_dx"] + p["col_w"], p["col_d"] - 30, p["xh_h"], 12, z=z), "inst_black")
    xh.add("crosshead logo", box(-90, -(p["col_d"] - 30) / 2 - 2, z + 80, 90, -(p["col_d"] - 30) / 2,
                                 z + 120), "inst_red")
    xh.add("load cell", cyl(110, 70, z=z - 70), "chrome")
    xh.add("load cell band", cyl(112, 14, z=z - 42), "inst_red")
    xh.add("upper grip", _wedge_grip(z - 70, up=False), "steel")
    spec = _piece(inst, "specimen")
    g0, g1 = p["base_h"] + 90 + 110, z - 70 - 110
    spec.add("specimen", _dogbone(L=g1 - g0 + 120, w=12.5, grip_w=20, t=4, gauge=g1 - g0 - 60)
             .translate((0, 0, (g0 + g1) / 2)), "sample")
    inst.joints = {"crosshead": Joint("slide", vec=(0, 0, p["travel"]))}
    inst.actions = [
        ("A printed tensile bar in the wedge grips. The crosshead pulls at a constant rate; the load cell above "
         "the upper grip reads the force.", 3.0, {"crosshead": (0.0, 0.15)}),
        ("Ductile fracture: the crosshead returns. 100 kN capacity, 2.3 m tall and 800 kg, so it stands beside the "
         "VLM.", 2.2, {"crosshead": (0.15, 0.0)}),
    ]
    inst.labels = [("moving crosshead", (-200, -(p["col_d"] - 30) / 2, z + p["xh_h"] / 2), (0.15, 0.25)),
                   ("load cell", (0, -55, z - 35), (0.82, 0.32)),
                   ("wedge grips", (0, -35, p["base_h"] + 150), (0.82, 0.62))]
    inst.cam = (1.0, -2.4, 0.9)
    return inst


# Instron 6800 Series single column 68SC-2 (2 kN; the 68SC-1 is the same frame): 1410 H x 460 W x 615 D mm, 62 kg;
# 1118 mm of vertical test space, 100 mm throat from the column to the load axis (Instron 6800 Series brochure). The
# shortest single column, the 68SC-05, is still 1020 mm tall: no Instron frame fits under Kardex's 727.5 mm. Look from
# Instron's renders: black ribbed column at the back, black arm with a silver load cell with a red band, a low black
# base with a silver strip, the red badge and the red e-stop, and the touchscreen on a swing arm.
INSTRON_SC = dict(W=460.0, D=615.0, H=1410.0, base_h=130.0, col_w=170.0, col_d=200.0, throat=100.0, arm_h=110.0,
                  xh_z=760.0, travel=60.0)


def instron_small() -> Instrument:
    p = INSTRON_SC
    inst = Instrument("instron_small", "Universal testing machine, tabletop", "Instron 68SC-2",
                      (p["W"], p["D"], p["H"]), "Instron 6800 Series brochure (68SC-1/-2: 1410 x 460 x 615 mm, 62 kg, "
                      "100 mm throat); look from Instron's renders", floor=True)
    W, D, H = p["W"], p["D"], p["H"]
    body = _piece(inst, "body")
    col_y = D / 2 - p["col_d"] / 2 - 15
    gy = col_y - p["col_d"] / 2 - p["throat"]          # the load axis, 100 mm in front of the column
    body.add("base", rbox(W, D, p["base_h"] - 20, 16, z=20), "inst_dark")
    body.add("base strip", rbox(W - 10, D - 10, 20, 14), "aluminium")
    body.add("badge", box(-W / 2 + 30, -D / 2 - 2, p["base_h"] - 60, -W / 2 + 120, -D / 2, p["base_h"] - 35),
             "inst_red")
    body.add("e-stop label", box(W / 2 - 90, -D / 2 - 2, 45, W / 2 - 30, -D / 2, 105), "inst_yellow")
    body.add("e-stop", _ycyl(36, 18, x=W / 2 - 60, y=-D / 2 - 20, z=75), "inst_red")
    body.add("column", _ribbed_column(p["col_w"], p["col_d"], H - p["base_h"] - 20, 0, col_y, p["base_h"]),
             "inst_black")
    body.add("lifting eye", cyl(40, 20, y=col_y, z=H - 20), "steel")
    body.add("lower grip", _wedge_grip(p["base_h"] + 60, up=True, w=60, h=70).translate((0, gy, 0)), "steel")
    body.add("lower adapter", cyl(50, 60, y=gy, z=p["base_h"]), "steel")
    body.add("screen arm", box(p["col_w"] / 2, col_y - 15, 1050, p["col_w"] / 2 + 160, col_y + 15, 1075), "inst_dark")
    body.add("touchscreen", box(p["col_w"] / 2 + 140, col_y - 120, 930, p["col_w"] / 2 + 165, col_y + 40, 1180),
             "inst_black")
    xh = _piece(inst, "crosshead")
    z = p["xh_z"]
    arm_y0 = gy - 70
    # narrower than the column and out of its front face (it was wider, and wrapped round the column to its middle)
    xh.add("arm", box(-p["col_w"] / 2 + 15, arm_y0, z, p["col_w"] / 2 - 15, col_y - p["col_d"] / 2 + 30, z + p["arm_h"])
           .edges("|X").fillet(10), "inst_black")
    xh.add("load cell", cyl(70, 50, y=gy, z=z - 50), "chrome")
    xh.add("load cell band", cyl(72, 10, y=gy, z=z - 32), "inst_red")
    xh.add("upper grip", _wedge_grip(z - 50, up=False, w=60, h=70).translate((0, gy, 0)), "steel")
    spec = _piece(inst, "specimen")
    g0, g1 = p["base_h"] + 60 + 70, z - 50 - 70
    spec.add("specimen", _dogbone(L=g1 - g0 + 70, w=4, grip_w=8, t=1.5, gauge=g1 - g0 - 30)
             .translate((0, gy, (g0 + g1) / 2)), "sample")
    inst.joints = {"crosshead": Joint("slide", vec=(0, 0, p["travel"]))}
    inst.actions = [
        ("A sub-size printed bar in its grips. The arm rides up the single column and pulls it.", 2.6,
         {"crosshead": (0.0, 0.25)}),
        ("Back to the start. A tabletop frame, but 1410 mm tall: even the shortest single column (1020 mm) is "
         "taller than a tray takes, so it stands beside the VLM.", 2.4, {"crosshead": (0.25, 0.0)}),
    ]
    inst.labels = [("single column", (0, col_y - p["col_d"] / 2, 1100), (0.80, 0.25)),
                   ("load cell and grips", (0, gy - 30, z - 60), (0.16, 0.45))]
    inst.cam = (1.4, -2.2, 0.9)
    return inst


# ===================================================================================================== XRD
# Rigaku MiniFlex (6th generation, "MiniFlex 6G"): 620 W x 722 H x 460 D mm, ~80 kg, vertical goniometer of 150 mm
# radius, theta-2theta (Rigaku MiniFlex 6G sheet; Rigaku brochure). The layout is Rigaku's own outline drawing in the
# brochure: a base with the control panel, the upper housing with a full-height front door between two side posts
# (vertical handle at its left, so it hinges on the right), a raised cover on top, and a bulge on each side.
XRD = dict(W=620.0, D=456.0, H=722.0, body_w=566.0, body_d=395.0, feet=23.0, base_top=297.0, door_top=611.0,
           upper_top=692.0, door_x=199.0, door_t=59.0, gonio_r=150.0, gonio_z=440.0)


def xrd() -> Instrument:
    p = XRD
    inst = Instrument("xrd", "Benchtop X-ray diffractometer", "Rigaku MiniFlex 600", (p["W"], p["D"], p["H"]),
                      "Rigaku MiniFlex brochure (outline drawings: 620 W x 456 D x 722 H mm with the feet and the top "
                      "hump, 80 kg; 150 mm vertical goniometer, theta-2theta) and the MiniFlex 6G sheet")
    bw, bd = p["body_w"], p["body_d"]
    yf, yb = -bd / 2, bd / 2
    gy = yf + p["door_t"] + 150.0                 # goniometer centre, behind the door
    gz = p["gonio_z"]
    body = _piece(inst, "body")
    feet = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            f = cyl(40, p["feet"], x=sx * (bw / 2 - 45), y=sy * (bd / 2 - 45))
            feet = f if feet is None else feet.union(f)
    body.add("feet", feet, "inst_dark")
    body.add("base", box(-bw / 2, yf, p["feet"], bw / 2, yb, p["base_top"]), "inst_white")
    body.add("control panel", box(-p["door_x"], yf - 3, 199, p["door_x"], yf, 290), "inst_light")
    for i, x in enumerate((-160, -110, -60, 0, 50)):
        body.add(f"button {i + 1}", _ycyl(16 if i != 1 else 10, 6, x=x, y=yf - 9, z=245), "inst_grey")
    body.add("door lock", _ycyl(24, 8, x=110, y=yf - 11, z=245), "inst_yellow")
    body.add("HV key", _ycyl(14, 10, x=-110, y=yf - 13, z=245), "chrome")
    body.add("emergency stop", _ycyl(34, 10, x=160, y=yf - 13, z=245), "inst_red")
    body.add("rear fittings", box(-120, yb, 80, 120, yb + 30, 200), "inst_grey")
    # the upper housing: posts either side of the door, the logo band over it, the chamber behind it
    hood = _piece(inst, "hood")
    upper = box(-bw / 2, yf, p["base_top"], bw / 2, yb, p["upper_top"])
    upper = upper.cut(box(-p["door_x"], yf - 1, p["base_top"], p["door_x"], yf + p["door_t"], p["door_top"]))
    cx0, cz1 = bw / 2 - 20, p["upper_top"] - 15      # the chamber behind the door frame: wider and taller than the door
    upper = upper.cut(box(-cx0, yf + p["door_t"] - 1, p["base_top"] + 6, cx0, yb - 30, cz1))
    hood.add("upper housing", upper, "inst_white")
    hood.add("logo band", box(-p["door_x"], yf - 2, p["door_top"] + 12, p["door_x"], yf, p["upper_top"] - 12),
             "inst_offwhite")
    hood.add("logo", box(-80, yf - 3, 655, 80, yf - 2, 672), "inst_grey")
    top = cq.Workplane("YZ").polyline([(yf + 95, 0), (yf + 215, 0), (yf + 205, 30), (yf + 105, 30)]).close() \
        .extrude(2 * 188).translate((-188, 0, p["upper_top"]))
    hood.add("top cover", top, "inst_light")
    hood.add("X-ray lamp", cyl(22, 14, x=230, y=yf + 160, z=p["upper_top"]), "inst_orange")
    for sx in (-1, 1):
        w = box(min(sx * bw / 2, sx * (bw / 2 + 27)), yf + 92, 309, max(sx * bw / 2, sx * (bw / 2 + 27)), yf + 216, 543)
        hood.add(f"side bulge {'LR'[sx > 0]}", w.edges("|Y").chamfer(12), "inst_light")
    # inside: the goniometer's back plate, the fixed X-ray tube on the left, the stage and the detector arm
    inner = _piece(inst, "chamber")
    inner.add("chamber lining", box(-cx0, yb - 34, p["base_top"] + 6, cx0, yb - 30, cz1).union(
        box(-cx0, yf + p["door_t"], p["base_top"] + 6, cx0, yb - 30, p["base_top"] + 10)), "inst_dark")
    inner.add("goniometer", _ycyl(250, 12, y=yb - 46, z=gz), "inst_grey")
    # the hub is behind the sample (it used to ring the stage, in the beam's way); the stage turns on a theta shaft
    inner.add("goniometer hub", _ycyl(70, yb - 46 - (gy + 60), y=gy + 60, z=gz), "aluminium")
    tube_x0 = -p["gonio_r"]
    inner.add("X-ray tube", _xcyl(64, 170, x=tube_x0 - 140, y=gy, z=gz), "inst_black")
    inner.add("tube window", _xcyl(30, 30, x=tube_x0 + 30, y=gy, z=gz), "steel")
    inner.add("divergence slit", box(tube_x0 + 60, gy - 18, gz - 18, tube_x0 + 66, gy + 18, gz + 18), "brass")
    stage = _piece(inst, "stage")
    stage.add("sample stage", box(-35, gy - 30, gz - 16, 35, gy + 30, gz - 3), "aluminium")
    stage.add("theta shaft", _ycyl(24, 30, y=gy + 30, z=gz), "steel")
    holder = _piece(inst, "holder")
    holder.add("sample holder", box(-22, -26, 0, 22, 26, 2.5), "window")
    holder.add("powder", box(-10, -10, 2.5, 10, 10, 3.0), "powder")
    det = _piece(inst, "detector")
    r = p["gonio_r"]
    # the D/teX head at the 150 mm circle on its 2theta arm, which turns about the axis behind the beam plane
    d_shape = box(r - 10, gy - 30, -28, r + 60, gy + 31, 28).union(_xcyl(36, 30, x=r - 40, y=gy, z=0)).union(
        box(14, gy + 31, -12, r + 20, gy + 45, 12))
    d_shape = d_shape.rotate((0, gy, 0), (0, gy + 1, 0), -10.0).translate((0, 0, gz))    # 2theta = 10 deg
    det.add("D/teX detector", d_shape, "inst_dark")
    door = _piece(inst, "door")
    door.add("door", box(-p["door_x"] + 1, yf, p["base_top"] + 1, p["door_x"] - 1, yf + p["door_t"] - 2,
                         p["door_top"] - 1), "inst_navy")
    door.add("door logo", box(-40, yf - 1, 340, 70, yf, 352), "inst_light")
    door.add("door handle", box(-178, yf - 28, 353, -166, yf - 16, 461).union(
        box(-178, yf - 28, 353, -166, yf, 365)).union(box(-178, yf - 28, 449, -166, yf, 461)), "chrome")
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(p["door_x"], yf, 0), deg=100.0),
        "stage": Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-40.0),
        # it waits clear of the door's swing and comes in through the doorway, at the goniometer's height
        "holder": Joint("path", parent="stage", path=((-200, -520, gz + 60), (0, yf - 40, gz + 40),
                                                      (0, gy - 60, gz - 3 + 40), (0, gy, gz - 3))),
        "detector": Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-80.0),
    }
    inst.actions = [
        ("The door unlocks and swings open on its right-hand hinge, showing the 150 mm vertical goniometer.", 1.6,
         {"door": (0.0, 1.0), "holder": (0.0, 0.0)}),
        ("A powder sample on its holder goes onto the stage at the goniometer's centre.", 2.0, {"holder": (0.0, 1.0)}),
        ("Door closed and locked: the X-ray interlock lets the 600 W tube switch on.", 1.4, {"door": (1.0, 0.0)}),
        ("Scan, drawn see-through: the tube stays put, the sample tilts by theta and the detector sweeps 2theta "
         "from 10 to 90 degrees.", 3.2, {"~hood": (0.0, 1.0), "~door": (0.0, 1.0), "stage": (0.0, 1.0),
                                         "detector": (0.0, 1.0)}),
        ("The detector parks and the door opens again.", 1.8,
         {"stage": (1.0, 0.0), "detector": (1.0, 0.0), "~hood": (1.0, 0.0), "~door": (1.0, 0.0),
          "door": (0.0, 1.0)}),
        ("The sample comes out.", 1.4, {"holder": (1.0, 0.0)}),
        ("Door shut. At 722 mm tall the MiniFlex just fits a tray: Kardex allows 727.5 mm.", 1.4,
         {"door": (1.0, 0.0)}),
    ]
    inst.labels = [("X-ray tube", (-200, gy, gz + 30), (0.12, 0.30)), ("detector", (150, gy, gz + 60), (0.84, 0.30)),
                   ("front door", (-170, yf - 30, 520), (0.14, 0.62))]
    inst.cam = (0.75, -1.8, 0.7)
    return inst


# ===================================================================================================== SEM
# Hitachi TM4000PlusII tabletop SEM: main unit 330 W x 614 D x 547 H mm (Hitachi High-Tech); the look from Hitachi's
# product photo: white body and top hood, a dark blue front with the EVAC/AIR button, and the sample chamber's drawer
# below it with a black handle. The stage rides on the drawer and comes out with it. EDS and EBSD detectors mount on
# the chamber's sides; their electronics stand beside it, the diaphragm pump behind.
SEM = dict(W=330.0, D=614.0, H=547.0, feet=25.0, front_z0=30.0, drawer_top=250.0, blue_top=430.0, draw=170.0)


def sem() -> Instrument:
    p = SEM
    inst = Instrument("sem", "Tabletop SEM with EDS and EBSD", "Hitachi TM4000PlusII", (p["W"], p["D"], p["H"]),
                      "Hitachi High-Tech TM4000PlusII specifications (main unit 330 W x 614 D x 547 H mm, 54 kg; "
                      "pump 144 x 270 x 216 mm); Hitachi's EDS brochure (AZtecOne analyser 290 x 260 x 330 mm); look "
                      "from Hitachi's photo; envelope and the 17 cm drawer travel cross-checked against ac-dev-lab "
                      "#132's TM4000II model")
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"foot {sx}{sy}", cyl(40, p["feet"], x=sx * (W / 2 - 40), y=sy * (D / 2 - 50)), "chrome")
    shell = rbox(W, D - 10, H - p["feet"] - 70, 18, y=5, z=p["feet"])
    shell = shell.cut(box(-W / 2 + 32, yf - 1, p["front_z0"], W / 2 - 32, yf + 40, p["blue_top"]))
    # the sample chamber behind the drawer, so the stage comes out of an opening rather than out of solid shell
    chamber = box(-115, yf + 39, 45, 115, yf + 240, 235)
    shell = shell.cut(chamber)
    body.add("body", shell, "inst_white")
    body.add("chamber", chamber.cut(box(-111, yf + 38, 49, 111, yf + 236, 231)), "inst_dark")
    hood = rbox(W - 6, D - 60, 70, 30, y=20, z=H - 70).edges(">Z").fillet(20)
    body.add("top hood", hood, "inst_offwhite")
    body.add("hood ridge", rbox(175, D - 120, 14, 10, y=40, z=H - 14), "inst_white")
    body.add("front panel", box(-W / 2 + 36, yf + 8, p["drawer_top"], W / 2 - 36, yf + 40, p["blue_top"]), "inst_blue")
    body.add("status lights", box(-60, yf + 6, p["blue_top"] - 22, 60, yf + 8, p["blue_top"] - 14), "screen_on")
    body.add("model plate", box(-70, yf + 6, p["blue_top"] - 80, 70, yf + 8, p["blue_top"] - 50), "inst_light")
    body.add("EVAC/AIR button", _ycyl(30, 6, x=W / 2 - 55, y=yf + 2, z=p["blue_top"] - 110), "chrome")
    body.add("drawer frame", box(-W / 2 + 32, yf + 8, p["front_z0"], W / 2 - 32, yf + 40, p["front_z0"] + 4), "inst_navy")
    # EDS: the detector is built in (Hitachi); only Oxford's AZtecOne analyser box stands beside. EBSD: Hitachi lists
    # no EBSD option for the TM4000 series; drawn here is Bruker's e-Flash XS (sold for tabletop SEMs, 48 x 84 mm
    # outside the chamber) on a side port, with a 70 degree pre-tilted stub holder. A proposal, not a documented mount.
    cz = 150.0
    body.add("EDS analyser", rbox(260, 290, 330, 12, x=W / 2 + 190, y=-90, z=0), "inst_white")
    body.add("EDS analyser front", box(W / 2 + 70, -236, 40, W / 2 + 310, -235, 300), "inst_navy")
    body.add("EDS analyser light", _ycyl(14, 3, x=W / 2 + 190, y=-237, z=250), "inst_orange")
    body.add("EBSD port", _xcyl(70, 20, x=-W / 2 - 20, y=-40, z=cz), "inst_light")
    body.add("EBSD detector", _xcyl(48, 84, x=-W / 2 - 104, y=-40, z=cz), "inst_dark")
    body.add("EBSD camera", _xcyl(56, 40, x=-W / 2 - 144, y=-40, z=cz), "inst_black")
    body.add("pump", rbox(144, 270, 216, 10, x=-W / 2 - 110, y=D / 2 - 160, z=0), "inst_white")
    body.add("pump hose", cyl(22, 30, x=-W / 2 - 110, y=D / 2 - 160, z=216), "inst_black")
    # the drawer: the chamber's front door, with the stage on its inside face
    drawer = _piece(inst, "drawer")
    drawer.add("drawer front", rbox(W - 72, 30, p["drawer_top"] - p["front_z0"] - 12, 6, y=yf + 15,
                                    z=p["front_z0"] + 6), "inst_blue")
    drawer.add("handle", rbox(160, 16, 22, 8, y=yf - 6, z=p["drawer_top"] - 70), "inst_black")
    # rails long enough to stay in the chamber with the drawer out, and a carrier plate under the stage's column
    drawer.add("stage rails", box(-80, yf + 30, 60, -60, yf + 230, 75).union(box(60, yf + 30, 60, 80, yf + 230, 75)),
               "steel")
    drawer.add("stage carrier", box(-80, yf + 30, 52, 80, yf + 200, 60), "steel")
    drawer.add("stage", cyl(70, 30, y=yf + 120, z=95), "aluminium")
    drawer.add("stage column", cyl(30, 35, y=yf + 120, z=60), "steel")
    stub = _piece(inst, "stub")
    stub.add("mount", cyl(25, 10, z=0), "mount")
    stub.add("polished face", cyl(15, 0.6, z=10), "sample")
    drawer.add("pre-tilted holder", box(-14, -8, 0, 14, 8, 26).rotate((0, 0, 0), (1, 0, 0), 20)
               .translate((32, yf + 120, 110)), "aluminium")
    inst.joints = {
        "drawer": Joint("slide", vec=(0, -p["draw"], 0)),
        "stub": Joint("path", parent="drawer", path=((0, yf - 250, 330), (0, yf + 120, 270), (0, yf + 120, 125))),
    }
    inst.actions = [
        ("AIR vents the chamber; the drawer slides out with the stage on its inside face.", 1.6,
         {"drawer": (0.0, 1.0), "stub": (0.0, 0.0)}),
        ("A polished, mounted sample (25 mm) goes onto the stage.", 2.0, {"stub": (0.0, 1.0)}),
        ("Drawer in, EVAC: about three minutes to vacuum. The EDS detector is built in, its analyser beside. "
         "EBSD (left) is a proposal: no TM4000 option exists, and it needs a 70 degree pre-tilted holder.", 2.6,
         {"drawer": (1.0, 0.0)}),
    ]
    inst.labels = [("EDS analyser (AZtecOne)", (W / 2 + 190, -90, 330), (0.84, 0.22)),
                   ("EBSD (proposed)", (-W / 2 - 110, -40, cz + 30), (0.14, 0.28)),
                   ("sample drawer", (0, yf, 180), (0.18, 0.70))]
    inst.cam = (-0.9, -2.0, 0.85)
    return inst


# ===================================================================================================== PIP
# Plastometrex PLX-Benchtop (profilometry-based indentation plastometry): a matte charcoal portal, two side columns
# under a rounded housing with a U-shaped blue LED band, an open test bay with no door or guard: a crosshead with the
# indenter over a round stainless platen on a load cell (Plastometrex's product render and brochure). The sample is
# set on the platen by hand, unclamped; up to 160 mm across, under 8 mm thick on a fixture (Illinois MRL and a
# published SOP). PLX-AutoStage is Plastometrex's add-on that automates the loading and places indents within 150 um.
# Plastometrex publishes no dimensions: the envelope is scaled from photos (about 0.5 m wide and 0.65-0.7 m tall,
# +-20 %), so whether it fits a tray is not settled.
# The profile is measured with a stylus profilometer on the Benchtop (an interferometer on the PLX-Portable,
# Plastometrex's "What is PIP?" page). Where the stylus sits and how it reaches the indent is not published: here it is
# a traverse unit on the left-hand column, its arm level with the sample. It stays parked well clear of the indenter
# while the indent is made; then, with the indenter lifted, the arm reaches in under it, sets the stylus down in the
# indent and traces across it. Without the AutoStage the sample can't move, so the stylus has to come to the indent.
PIP = dict(W=500.0, D=500.0, H=680.0, pillar=100.0, base_h=60.0, top_z0=390.0, stage_d=150.0, stage_t=16.0,
           cell_d=80.0, cell_h=24.0, head_z=185.0, reach=40.0, drop=8.0, scan=3.0, lift=0.4)


def pip() -> Instrument:
    p = PIP
    inst = Instrument("pip", "Indentation plastometer (PIP)", "Plastometrex PLX-Benchtop", (p["W"], p["D"], p["H"]),
                      "Plastometrex's product render, brochure and FAQ; Illinois MRL's instrument page and a published "
                      "SOP for loading; no published dimensions, so the envelope is scaled from photos")
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    yc = -20.0                                   # the indenter's axis, and so the indent, is at (0, yc)
    body = _piece(inst, "body")
    body.add("base", rbox(W, D, p["base_h"], 20), "inst_dark")
    plate_z = p["base_h"] + 8
    body.add("base plate", box(-W / 2 + p["pillar"], yf + 20, p["base_h"] - 2, W / 2 - p["pillar"], D / 2 - 40,
                               plate_z), "aluminium")
    for sx in (-1, 1):
        x0, x1 = sorted((sx * W / 2, sx * (W / 2 - p["pillar"])))
        pil = box(x0, yf, p["base_h"], x1, D / 2, p["top_z0"] + 20).edges("|Z").fillet(18)
        body.add(f"pillar {'LR'[sx > 0]}", pil, "inst_dark")
    body.add("back wall", box(-W / 2 + p["pillar"], D / 2 - 60, p["base_h"], W / 2 - p["pillar"], D / 2 - 20,
                              p["top_z0"]), "inst_black")
    for i in range(8):
        z = p["base_h"] + 30 + i * 30
        body.add(f"louvre {i}", box(-W / 2 + p["pillar"] + 20, D / 2 - 62, z, W / 2 - p["pillar"] - 20, D / 2 - 60,
                                    z + 8), "inst_grey")
    top = box(-W / 2, yf, p["top_z0"], W / 2, D / 2, H).edges("|Y").fillet(60)
    body.add("top housing", top, "inst_dark")
    body.add("trim", box(-W / 2 - 2, yf - 2, p["top_z0"] - 6, W / 2 + 2, D / 2 + 2, p["top_z0"]), "aluminium")
    body.add("front panel", box(-W / 2 + 70, yf - 3, p["top_z0"] + 60, W / 2 - 70, yf, H - 35), "inst_black")
    led = box(-W / 2 + 64, yf - 5, p["top_z0"] + 54, W / 2 - 64, yf - 3, p["top_z0"] + 62).union(
        box(-W / 2 + 64, yf - 5, p["top_z0"] + 54, -W / 2 + 72, yf - 3, H - 80)).union(
        box(W / 2 - 72, yf - 5, p["top_z0"] + 54, W / 2 - 64, yf - 3, H - 80))
    body.add("LED band", led, "screen_on")
    body.add("e-stop", _xcyl(36, 22, x=W / 2, y=yf + 60, z=p["top_z0"] - 30), "inst_red")
    body.add("e-stop collar", _xcyl(48, 8, x=W / 2, y=yf + 60, z=p["top_z0"] - 30), "inst_yellow")
    body.add("guide columns", cyl(26, p["top_z0"] - p["base_h"], x=-W / 2 + p["pillar"] + 28, y=60, z=p["base_h"])
             .union(cyl(26, p["top_z0"] - p["base_h"], x=W / 2 - p["pillar"] - 28, y=60, z=p["base_h"])), "chrome")
    # the load string under the sample: a load cell, then a plain stainless disc for the platen
    body.add("load cell", cyl(p["cell_d"], p["cell_h"], y=yc, z=plate_z), "steel")
    platen_z = plate_z + p["cell_h"]
    body.add("platen", cyl(p["stage_d"], p["stage_t"], y=yc, z=platen_z).faces(">Z").edges().chamfer(1.5),
             "stainless")
    stz = platen_z + p["stage_t"]                 # the platen's top face
    s_top = stz + 6                               # the sample's top face, where the indent is
    # the profilometer's traverse unit, on the left-hand column's inner face (in view from the front right), level
    # with the sample
    xl = -(W / 2 - p["pillar"])                   # the column's inner face
    arm_z = s_top + 16                            # underside of the stylus arm when it travels
    ux1 = -62.0                                   # the unit's inner end
    body.add("profilometer traverse unit", rbox(ux1 - xl, 44, 46, 6, x=(xl + ux1) / 2, y=yc, z=arm_z - 14),
             "inst_light")
    body.add("profilometer unit window", box(xl + 12, yc - 23, arm_z + 10, ux1 - 12, yc - 22, arm_z + 26),
             "inst_dark")
    body.add("profilometer bracket", box(xl, yc - 30, arm_z - 22, xl + 12, yc + 30, arm_z + 40), "inst_dark")
    head = _piece(inst, "head")
    hz = p["head_z"] + p["base_h"]
    head.add("crosshead", box(-W / 2 + p["pillar"] + 10, -60, hz + 40, W / 2 - p["pillar"] - 10, 120, hz + 110)
             .edges("|Y").fillet(12), "inst_dark")
    head.add("crosshead nose", box(-100, -95, hz + 10, 100, 40, hz + 70).edges("|Y").chamfer(25), "inst_dark")
    for sx in (-1, 1):
        head.add(f"warning {sx}", box(sx * 80 - 13, -97, hz + 42, sx * 80 + 13, -95, hz + 62), "inst_yellow")
    head.add("indenter holder", cyl(32, 55, y=yc, z=hz - 45), "chrome")
    head.add("indenter", cyl(12, 10, y=yc, z=hz - 55).union(
        cq.Workplane("XY").sphere(3.0).translate((0, yc, hz - 55))), "inst_black")   # a WC ball in its seat
    # the stylus arm, parked: it slides out of the traverse unit along +x; its stylus hangs under the tip
    sty = _piece(inst, "stylus")
    park = p["reach"]                              # the tip parks this far to the left of the indenter's axis
    sty.add("profilometer arm", box(xl + 20, yc - 3, arm_z, -park, yc + 3, arm_z + 6), "steel")
    sty.add("stylus", cyl(2.5, 10, x=-park - 2, y=yc, z=arm_z - 10 + 1).union(
        cq.Workplane("XY").sphere(1.0).translate((-park - 2, yc, arm_z - 9))), "inst_black")
    sample = _piece(inst, "sample")
    sample.add("sample", box(-20, -20, 0, 20, 20, 6), "sample")
    dent = _piece(inst, "indent")                  # shows once the ball lifts off; rides on the sample
    dent.add("indent", cyl(2.5, 0.3, z=6.0), "inst_dark")        # in the sample's own frame
    gap = hz - 58 - s_top                          # the ball's lowest point to the sample's top face
    tip = arm_z - 10                               # the stylus tip, parked
    dx, dz, sc = park + 2, tip - s_top, p["scan"]
    # the stylus's route: in under the indenter, down into the indent, across it and back, up, and parked again
    route = ((0, 0, 0), (dx, 0, 0), (dx, 0, -dz), (dx - sc, 0, -dz), (dx + sc, 0, -dz), (dx, 0, -dz), (dx, 0, 0),
             (0, 0, 0))
    seg = np.linalg.norm(np.diff(np.asarray(route, float), axis=0), axis=1)
    at = np.concatenate([[0], np.cumsum(seg)]) / seg.sum()      # v at each waypoint
    inst.joints = {
        "sample": Joint("path", path=((0, -420, 260), (0, -220, 120), (0, yc, stz + 40), (0, yc, stz))),
        "head": Joint("slide", vec=(0, 0, -gap)),
        "stylus": Joint("path", path=route),
        "indent": Joint("fade", parent="sample"),
    }
    inst.actions = [
        ("No door or guard: a flat sample (here a 40 mm square cut from a print; 3 x 3 x 1.5 mm at the least) goes "
         "on the platen by hand, unclamped.", 2.4, {"sample": (0.0, 1.0)}),
        ("Hands clear: the crosshead drives the spherical indenter in, an indent 0.25-1 mm wide. The profilometer's "
         "stylus stays parked at the side.", 1.8, {"head": (0.0, 1.0)}),
        ("The indenter lifts; the stylus arm reaches in under it and sets the stylus down in the indent.", 2.2,
         {"head": (1.0, p["lift"]), "stylus": (0.0, float(at[2])), "indent": (0.0, 1.0)}),
        ("The stylus traces across the indent, line by line, to map its 3D shape.", 1.8,
         {"stylus": (float(at[2]), float(at[5]))}),
        ("It lifts and parks, and the crosshead goes back up.", 1.6,
         {"stylus": (float(at[5]), 1.0), "head": (p["lift"], 0.0)}),
        ("CORSICA fits a stress-strain curve to that profile in minutes. The sample comes off.", 2.0,
         {"sample": (1.0, 0.0), "indent": (1.0, 1.0)}),
    ]
    inst.labels = [("indenter", (0, yc, hz - 40), (0.84, 0.34)),
                   ("profilometer stylus", (-park - 10, yc - 3, arm_z + 3), (0.12, 0.46)),
                   ("platen on a load cell", (0, yc - p["stage_d"] / 2, platen_z + 8), (0.84, 0.72))]
    inst.zoom = {2: ((0.0, yc, s_top + 30), 520.0), 4: "out"}      # in on the bay for the profile, then back out
    inst.notes = ["The stylus profilometer's mounting is not published; the traverse unit on the left-hand column "
                  "is this model's choice."]
    inst.cam = (0.75, -1.9, 0.6)
    inst.framing = (0.66, 0.30)
    return inst


# ===================================================================================================== rail
# Vention's robot seventh axis, rack and pinion (Vention design 337010, "Robot 7th axis rack and pinion robot transfer
# unit 3330 mm": 3488 x 628 x 1017 mm, 220 kg): a 247.5 x 247.5 mm extrusion beam in 3330 mm segments on legs of the
# same extrusion on 405 mm floor plates; two 20 mm profile guides and a steel rack; a 426.5 x 358 x 86 mm carriage
# plate driven by a NEMA 34 servo through a right-angle gearbox; a 73 mm drag chain; dark blue anodizing; up to 4 m/s
# (Vention's design, part pages and actuator docs). The legs are cut so the arm's base sits at 800 mm, where it sits on
# the MiR250, and the axis runs along the fronts of the line. Vention's STEP needs a MachineBuilder account.
RAIL = dict(beam_w=247.5, beam_h=247.5, top=800.0, leg_pitch=3330.0, car_l=426.5, car_w=358.0, car_t=86.0)


def rail(length: float = 4000.0, travel: float = 1600.0) -> Instrument:
    p = RAIL
    inst = Instrument("rail", "Backup: a floor rail for the arm", "Vention robot 7th axis", (length, 628.0, p["top"]),
                      "Vention design 337010 and its part pages (beam, guides, carriage plate) and actuator docs",
                      floor=True)
    L = length
    bw, bh, top = p["beam_w"], p["beam_h"], p["top"]
    z1 = top - p["car_t"] - 30.0            # top of the beam, under the guides and the carriage
    z0 = z1 - bh
    body = _piece(inst, "body")
    beam = box(-L / 2, -bw / 2, z0, L / 2, bw / 2, z1)
    for y in (-bw / 2 + 22.5, bw / 2 - 22.5):            # the extrusions' T-slots, as grooves
        beam = beam.cut(box(-L / 2 - 1, y - 4, z1 - 8, L / 2 + 1, y + 4, z1 + 1))
    body.add("beam", beam, "vention_blue")
    for y in (-bw / 2 + 30, bw / 2 - 30):
        body.add(f"guide {y:+.0f}", box(-L / 2 + 20, y - 10, z1, L / 2 - 20, y + 10, z1 + 15), "steel")
    body.add("rack", box(-L / 2 + 20, -bw / 2 - 12, z1 - 40, L / 2 - 20, -bw / 2, z1), "steel")
    body.add("chain tray", box(-L / 2, bw / 2, z0 + 20, L / 2, bw / 2 + 90, z0 + 30).union(
        box(-L / 2, bw / 2 + 85, z0 + 20, L / 2, bw / 2 + 90, z0 + 70)), "vention_blue")
    body.add("cable chain", box(-L / 2 + 100, bw / 2 + 10, z0 + 30, 0, bw / 2 + 80, z0 + 75), "inst_black")
    n_legs = max(2, int(round(L / p["leg_pitch"])) + 1)
    legs = None
    for i in range(n_legs):
        x = -L / 2 + 150 + i * (L - 300) / (n_legs - 1)
        leg = box(x - 123.75, -123.75, 20, x + 123.75, 123.75, z0).union(box(x - 202.5, -202.5, 0, x + 202.5, 202.5, 20))
        for sx in (-1, 1):                     # gussets
            g = cq.Workplane("XZ").polyline([(x + sx * 123, 20), (x + sx * 200, 20), (x + sx * 123, 200)]).close() \
                .extrude(20, both=True)
            leg = leg.union(g)
        legs = leg if legs is None else legs.union(leg)
    body.add("legs", legs, "vention_blue")
    body.add("control cabinet", box(-L / 2 + 500, -150, z0 - 420, -L / 2 + 900, 150, z0 - 20), "inst_navy")
    body.add("cabinet screen", box(-L / 2 + 560, -152, z0 - 200, -L / 2 + 760, -150, z0 - 80), "screen_on")
    car = _piece(inst, "carriage")
    cl, cw = p["car_l"], p["car_w"]
    car.add("carriage plate", box(-cl / 2, -cw / 2, top - p["car_t"], cl / 2, cw / 2, top).cut(
        cyl(120, p["car_t"] + 2, z=top - p["car_t"] - 1)), "vention_blue")
    car.add("bearing blocks", box(-cl / 2 + 30, -cw / 2 + 40, z1 + 15, cl / 2 - 30, cw / 2 - 40, top - p["car_t"]), "steel")
    # the servo and its right-angle gearbox hang off the plate's front edge on a bracket, the pinion behind the bracket
    # meshing with the rack (they floated in front of the plate, with no pinion)
    car.add("motor bracket", box(-75, -cw / 2 - 15, z1 - 60, 75, -cw / 2, top), "aluminium")
    car.add("gearmotor", box(-60, -cw / 2 - 115, z1 - 60, 60, -cw / 2 - 15, z1 + 20).union(
        cyl(100, 160, x=0, y=-cw / 2 - 65, z=z1 - 220)), "inst_black")
    car.add("pinion", cyl(44, 40, x=0, y=-bw / 2 - 12 - 22, z=z1 - 42), "steel")
    car.add("robot adapter", cyl(210, 12, z=top - 12), "aluminium")
    inst.joints = {"carriage": Joint("slide", vec=(travel, 0, 0))}
    inst.actions = [
        ("The backup to the mobile base: a Vention seventh axis. The carriage carries the arm along the line on a "
         "rack and pinion.", 2.6, {"carriage": (0.0, 1.0)}),
        ("Up to 4 m/s. Its legs are cut so the arm's base is at 800 mm, where it sits on the MiR250.", 2.2,
         {"carriage": (1.0, 0.0)}),
    ]
    inst.labels = [("carriage and gearmotor", (0, -cw / 2 - 70, z1 - 60), (0.16, 0.30)),
                   ("rack and guides", (L / 2 - 400, -bw / 2, z1), (0.82, 0.40)),
                   ("control cabinet", (-L / 2 + 700, -150, z0 - 220), (0.16, 0.72))]
    inst.cam = (0.55, -1.5, 0.6)
    return inst


# ===================================================================================================== polisher
# Buehler EcoMet 30 semi-automatic grinder-polisher, single 12 in (305 mm) platen, with its built-in power head:
# 488 W x 638 D x 650 H mm (drawing; 500 x 650 x 650 in the table), 75 kg; 50-500 rpm, 25-200 N head force; it needs
# water, compressed air (> 0.4 MPa) and a drain (EcoMet 30 manual). Layout from the manual's drawing and Buehler's
# photos: a cream base with its deck at 254.5 mm and a blue side panel, the bowl front-centre with a blue rim, a tower
# at the back right (444.5 mm) with the 7 in touchscreen, and the power head (blue body, white cap) on a column at the
# back left, reaching over the platen with a six-hole specimen holder.
POLISHER = dict(W=488.0, D=638.0, H=650.0, deck=254.5, platen_d=305.0, bowl_d=400.0, tower_h=444.5, head_drop=40.0)


def polisher() -> Instrument:
    p = POLISHER
    inst = Instrument("polisher", "Metallographic grinder-polisher", "Buehler EcoMet 30 semi-automatic",
                      (p["W"], p["D"], p["H"]), "Buehler EcoMet 30 instruction manual (drawing 488 x 638 x 650 mm, "
                      "75 kg, platens, services); look from Buehler's photos")
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    pc = (0.0, yf + 230.0)                      # platen centre, front-centre
    body = _piece(inst, "body")
    base = box(-W / 2, yf, 0, W / 2, yb, p["deck"]).edges("|Z").fillet(30)
    body.add("base", base, "inst_offwhite")
    body.add("side panel", box(-W / 2 - 2, yf + 60, 30, -W / 2, yb - 60, p["deck"] - 30), "inst_blue")
    body.add("e-stop", _ycyl(34, 16, x=W / 2 - 50, y=yf - 14, z=p["deck"] - 50), "inst_red")
    body.add("e-stop collar", _ycyl(46, 4, x=W / 2 - 50, y=yf - 2, z=p["deck"] - 50), "inst_yellow")
    bowl = cyl(p["bowl_d"], 90, x=pc[0], y=pc[1], z=p["deck"]).cut(
        cyl(p["bowl_d"] - 24, 91, x=pc[0], y=pc[1], z=p["deck"] + 8))
    body.add("splash bowl", bowl, "inst_light")
    body.add("bowl rim", cyl(p["bowl_d"] + 6, 10, x=pc[0], y=pc[1], z=p["deck"] + 85).cut(
        cyl(p["bowl_d"] - 24, 12, x=pc[0], y=pc[1], z=p["deck"] + 84)), "inst_blue")
    tx, ty = W / 2 - 75, yb - 95
    body.add("tower", rbox(130, 150, p["tower_h"] - p["deck"], 14, x=tx, y=ty, z=p["deck"]), "inst_offwhite")
    tscr = box(-80, -4, 0, 80, 0, 100).rotate((0, 0, 0), (1, 0, 0), -20).translate((tx - 30, ty - 77, p["tower_h"] - 115))
    body.add("touchscreen", tscr.rotate((tx, ty, 0), (tx, ty, 1), 0), "screen_on")
    cx, cy = -W / 2 + 80, yb - 90
    # the column ends inside the head even with the head down (it came up through the cap)
    body.add("column", rbox(90, 90, H - p["deck"] - 90, 10, x=cx, y=cy, z=p["deck"]), "inst_offwhite")
    pz = p["deck"] + 70                         # the platen's underside; the cloth's top is 18 mm above it
    # the spout comes out of the tower over the bowl's rim, its nozzle 10 mm above the cloth (it went into the platen)
    sz0 = pz + 28
    body.add("water spout", box(pc[0] + 120, pc[1] + 60, p["deck"] + 110, pc[0] + 132, yb - 160, p["deck"] + 122)
             .union(box(pc[0] + 120, pc[1] + 60, sz0, pc[0] + 132, pc[1] + 72, p["deck"] + 122)), "steel")
    head = _piece(inst, "head")
    hz = H - 150
    hz0 = pz + 18.6 + p["head_drop"]            # the mounts' faces: on the cloth with the head down
    hcx, hcy = pc[0] - 30, pc[1] + 20             # the holder's axis, off the platen's centre
    head.add("head arm", box(cx - 50, hcy - 60, hz, cx + 50, cy + 40, hz + 110).edges("|Z").fillet(20).union(
        box(cx - 50, hcy - 60, hz, hcx + 70, hcy + 60, hz + 110).edges("|Z").fillet(20)), "inst_blue")
    head.add("head cap", box(cx - 45, hcy - 55, hz + 110, hcx + 65, hcy + 55, hz + 125).edges("|Z").fillet(18)
             .union(box(cx - 45, hcy - 55, hz + 110, cx + 45, cy + 35, hz + 125)), "inst_white")
    head.add("chevron", box(hcx - 20, hcy - 61, hz + 40, hcx + 40, hcy - 60, hz + 70), "inst_white")
    head.add("spindle", cyl(36, hz - (hz0 + 40), x=hcx, y=hcy, z=hz0 + 40), "chrome")
    holder = _piece(inst, "holder")
    holder.add("specimen holder", cyl(160, 18, x=hcx, y=hcy, z=hz0 + 22).cut(cyl(30, 20, x=hcx, y=hcy, z=hz0 + 21)),
               "steel")
    for i in range(6):
        a_ = math.radians(90 + 60 * i)
        holder.add(f"mount {i + 1}", cyl(30, 25, x=hcx + 52 * math.cos(a_), y=hcy + 52 * math.sin(a_), z=hz0),
                   "mount")
    holder.add("mark", box(hcx + 60, hcy - 4, hz0 + 40, hcx + 78, hcy + 4, hz0 + 41), "inst_red")
    platen = _piece(inst, "platen")
    platen.add("platen", cyl(p["platen_d"], 15, x=pc[0], y=pc[1], z=pz), "aluminium")
    platen.add("platen hub", cyl(80, pz - p["deck"] - 8, x=pc[0], y=pc[1], z=p["deck"] + 8), "steel")
    platen.add("cloth", cyl(p["platen_d"] - 6, 3, x=pc[0], y=pc[1], z=pz + 15), "cloth")
    for i in range(4):
        bar = box(-p["platen_d"] / 2 + 10, -3, pz + 18, p["platen_d"] / 2 - 10, 3, pz + 18.6)
        platen.add(f"groove {i}", bar.rotate((0, 0, 0), (0, 0, 1), i * 45.0).translate((pc[0], pc[1], 0)), "inst_grey")
    water = _piece(inst, "glow")
    water.add("water", cyl(6, sz0 - (pz + 18), x=pc[0] + 126, y=pc[1] + 66, z=pz + 18), "water")     # nozzle to cloth
    inst.joints = {
        "head": Joint("slide", vec=(0, 0, -p["head_drop"])),
        "holder": Joint("spin", parent="head", axis=(0, 0, 1), pivot=(hcx, hcy, 0), deg=-720.0),
        "platen": Joint("spin", axis=(0, 0, 1), pivot=(pc[0], pc[1], 0), deg=1800.0),
        "glow": Joint("fade"),
    }
    inst.actions = [
        ("Six mounted samples (30 mm) in the power head's holder, over a 12 in platen with a polishing cloth.",
         1.4, {"glow": (0.0, 0.0)}),
        ("The head presses the holder onto the cloth (25-200 N); water on; platen and holder turn, 50-500 rpm.", 3.6,
         {"head": (0.0, 1.0), "platen": (0.0, 1.0), "holder": (0.0, 1.0), "glow": (0.0, 1.0)}),
        ("Done: the head lifts. It needs water, air and a drain, so on a tray it needs a recirculating unit.", 1.8,
         {"head": (1.0, 0.0), "glow": (1.0, 0.0)}),
    ]
    inst.labels = [("power head", (cx, hcy, hz + 125), (0.16, 0.22)),
                   ("touchscreen", (tx - 30, ty - 77, p["tower_h"] - 70), (0.84, 0.25)),
                   ("platen", (pc[0] + 140, pc[1] - 60, pz + 15), (0.84, 0.62))]
    inst.cam = (0.8, -1.7, 1.1)
    return inst


# ===================================================================================================== nanoindenter
# KLA iMicro nanoindenter (the iNano's cabinet, with a 1 N actuator for metals): a white cabinet, roughly a cube, with
# vibration isolation and the controller built in; an L-shaped hood (top and front) hinged along the top rear edge
# lifts 70-80 degrees on gas struts; purple patterned side panels, a green status bar; inside, the indenter head and
# a microscope over a motorized XY stage for 32 mm mounts (KLA product photos). KLA publishes no dimensions: the
# envelope is scaled from photos (0.5-0.55 m wide).
NANO = dict(W=540.0, D=520.0, H=520.0, feet=25.0, lid_t=40.0, lid_deg=75.0, stage_z=150.0, head_x=-40.0,
            scope_x=60.0)


def nanoindenter() -> Instrument:
    p = NANO
    inst = Instrument("nanoindenter", "Nanoindenter", "KLA iMicro", (p["W"], p["D"], p["H"]),
                      "KLA Instruments iMicro / iNano product photos and data sheet; envelope in SPECS")
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"foot {sx}{sy}", box(sx * (W / 2 - 60) - 30, sy * (D / 2 - 50) - 25, 0, sx * (W / 2 - 60) + 30,
                                           sy * (D / 2 - 50) + 25, p["feet"]), "inst_black")
    hz = H - p["lid_t"]
    shell = box(-W / 2, yf, p["feet"], W / 2, yb, hz).edges("|Y").fillet(16)
    shell = shell.cut(box(-W / 2 + 40, yf - 1, p["feet"] + 70, W / 2 - 30, yb - 30, hz + 1))
    shell = shell.cut(box(-W / 2 + 40, yf + 30, p["feet"] + 70, W / 2 - 30, yb - 30, hz + 1))
    body.add("cabinet", shell, "inst_white")
    body.add("inner walls", box(-W / 2 + 40, yb - 34, p["feet"] + 70, W / 2 - 30, yb - 30, hz).union(
        box(-W / 2 + 40, yf, p["feet"] + 66, W / 2 - 30, yb - 30, p["feet"] + 70)), "inst_dark")
    body.add("side panel", box(-W / 2 - 3, yf + 10, p["feet"] + 10, -W / 2, yb - 10, hz - 10), "inst_purple")
    body.add("status light", box(-50, yf - 2, p["feet"] + 28, 50, yf, p["feet"] + 42), "inst_green")
    sz = p["feet"] + 70 + p["stage_z"] - 60
    body.add("frame", box(-120, yb - 160, p["feet"] + 70, 120, yb - 34, hz - 40), "inst_black")
    body.add("indenter head", cyl(70, 150, x=p["head_x"], y=0, z=sz + 90).union(
        box(p["head_x"] - 50, -40, sz + 200, p["head_x"] + 50, yb - 150, sz + 280)), "inst_black")
    body.add("indenter tip", cyl(10, 30, x=p["head_x"], y=0, z=sz + 60), "chrome")
    body.add("objective", cyl(36, 110, x=p["scope_x"], y=0, z=sz + 100), "chrome")
    body.add("camera", cyl(46, 80, x=p["scope_x"], y=0, z=sz + 210), "inst_dark")     # under the lid
    body.add("stage base", box(-150, -110, p["feet"] + 70, 150, 110, sz - 20), "inst_dark")
    stage = _piece(inst, "stage")
    stage.add("xy stage", box(-90, -80, sz - 20, 90, 80, sz), "aluminium")
    stage.add("sample puck", cyl(40, 15, x=0, y=0, z=sz), "steel")
    sample = _piece(inst, "sample")
    sample.add("sample", cyl(25, 10, z=0), "mount")
    sample.add("polished face", cyl(15, 0.5, z=10), "sample")
    lid = _piece(inst, "lid")
    lid.add("lid", box(-W / 2, yf, hz, W / 2, yb, H).edges("|Y").fillet(14), "inst_white")
    lid.add("lid window", box(-W / 2 + 120, yf + 80, H, W / 2 - 80, yb - 120, H + 1), "inst_black")
    # the hood's front, down to the status light: it lifts with the lid
    lid.add("hood front", box(-W / 2 + 40, yf, p["feet"] + 70, W / 2 - 30, yf + 12, hz).cut(
        box(-W / 2 + 90, yf - 1, p["feet"] + 120, W / 2 - 80, yf + 13, hz - 50)), "inst_white")
    lid.add("hood glass", box(-W / 2 + 90, yf + 4, p["feet"] + 120, W / 2 - 80, yf + 8, hz - 50), "window")
    inst.joints = {
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, yb, hz), deg=-p["lid_deg"]),     # front up, about the back edge
        "stage": Joint("slide", vec=(p["head_x"] - p["scope_x"], 0, 0)),
        "sample": Joint("path", parent="stage", path=((p["scope_x"], -380, 420), (p["scope_x"], -150, sz + 120),
                                                      (p["scope_x"], 0, sz + 15 + 30), (p["scope_x"], 0, sz + 15))),
    }
    inst.actions = [
        ("The lid lifts on its gas struts, hinged at the back.", 1.6, {"lid": (0.0, 1.0), "sample": (0.0, 0.0)}),
        ("A mounted sample goes onto the stage's puck, under the microscope.", 2.0, {"sample": (0.0, 1.0)}),
        ("Lid down: the cabinet shuts out air currents and noise. The stage carries the chosen spot under the "
         "indenter for a grid of indents (hardness and modulus).", 2.6, {"lid": (1.0, 0.0), "stage": (0.0, 1.0),
                                                                          "~lid": (0.0, 1.0)}),
        ("Back under the microscope to image the indents.", 1.6, {"stage": (1.0, 0.0), "~lid": (1.0, 0.0)}),
    ]
    inst.labels = [("indenter head", (p["head_x"], 0, sz + 160), (0.14, 0.30)),
                   ("microscope", (p["scope_x"], 0, sz + 200), (0.84, 0.30))]
    inst.cam = (-0.7, -1.8, 1.0)
    inst.framing = (1.2, 0.85)                  # room above for the lid, which lifts to about 1 m
    return inst


# ===================================================================================================== laser diffraction
# Malvern Panalytical Mastersizer 3000 with the Aero S dry powder disperser, as for metal powders (Malvern's Mastersizer
# 3000 and 3000+ brochures): the optical bench is 690 L x 300 W x 450 H mm, 30 kg, a satin warm-grey box with a black
# top deck and left end and a vertical cell bay a third of the way along, under a dark dome lid; the Aero S (260 x 180
# x 380 mm, 10.5 kg) stands in front of the bay, its feed tray and hopper under a clear hinged dome, and blows the
# powder through a venturi in the bay across the laser; a vacuum extractor takes it away.
MS3000 = dict(L=690.0, W=300.0, H=450.0, bay_x=-115.0, bay_w=130.0, aero_l=260.0, aero_w=180.0, aero_h=380.0,
              vac_w=330.0, vac_d=330.0, vac_h=480.0)


def mastersizer() -> Instrument:
    p = MS3000
    L, W, H = p["L"], p["W"], p["H"]
    tot_l = L + 60 + p["vac_w"]
    inst = Instrument("mastersizer", "Laser diffraction particle sizer", "Malvern Mastersizer 3000 + Aero S",
                      (L, W, H),
                      "Malvern Panalytical Mastersizer 3000 and 3000+ brochures (bench 690 x 300 x 450 mm, 30 kg; "
                      "Aero S 260 x 180 x 380 mm, 10.5 kg); look from Malvern's product photos")
    x0 = -tot_l / 2
    xb = x0 + L / 2                              # the bench's centre
    yf, yb = -W / 2 + p["aero_w"] / 2, W / 2 + p["aero_w"] / 2          # bench front and back
    body = _piece(inst, "body")
    bench = box(xb - L / 2, yf, 0, xb + L / 2, yb, H - 20).edges("|Y").fillet(30)
    bx = xb + p["bay_x"]
    bench = bench.cut(box(bx - p["bay_w"] / 2, yf - 1, 60, bx + p["bay_w"] / 2, yb - 60, H))
    body.add("bench", bench, "inst_light")
    body.add("top deck", box(xb - L / 2 + 10, yf + 10, H - 20, xb + L / 2 - 10, yb - 10, H - 6), "inst_black")
    body.add("left end", box(xb - L / 2 - 4, yf + 5, 20, xb - L / 2, yb - 5, H - 40), "inst_black")
    body.add("cell bay", box(bx - p["bay_w"] / 2, yf + 20, 60, bx + p["bay_w"] / 2, yb - 60, H - 20), "inst_dark")
    body.add("bay dome", cyl(p["bay_w"] + 20, 40, x=bx, y=(yf + yb) / 2 - 20, z=H - 20).edges(">Z").fillet(18),
             "inst_dark")
    body.add("dome handle", box(bx - 40, (yf + yb) / 2 - 30, H + 20, bx + 40, (yf + yb) / 2 - 10, H + 32), "inst_black")
    body.add("status light", box(xb - L / 2 + 30, yf - 1, H - 70, xb - L / 2 + 80, yf, H - 60), "screen_on")
    body.add("lettering", box(bx + p["bay_w"] / 2 + 20, yf - 1, 90, bx + p["bay_w"] / 2 + 32, yf, H - 80), "inst_grey")
    # the Aero S in front of the bay: a grey body on a black base, the blue LED strip, the hopper under a clear dome
    ax, ay = bx, yf - p["aero_w"] / 2
    body.add("Aero S base", rbox(p["aero_l"], p["aero_w"], 40, 20, x=ax, y=ay), "inst_black")
    body.add("Aero S", rbox(p["aero_l"] - 20, p["aero_w"] - 20, p["aero_h"] - 100, 60, x=ax, y=ay, z=40)
             .edges(">Z").fillet(20), "inst_light")
    body.add("Aero S LED", box(ax - 80, ay - p["aero_w"] / 2 + 8, 52, ax + 80, ay - p["aero_w"] / 2 + 10, 60), "screen_on")
    # the hopper is a funnel set into the deck and the tray stays under the dome, clear of its back wall as it lifts;
    # the venturi takes the powder on from the back of the Aero S into the cell bay
    hy = ay - 15                                 # the hopper's centre
    body.add("feed tray", box(ax - 20, hy - 40, p["aero_h"] - 60, ax + 20, ay + 35, p["aero_h"] - 50), "steel")
    body.add("hopper", cyl(90, 45, x=ax, y=hy, z=p["aero_h"] - 90).cut(cyl(76, 45, x=ax, y=hy, z=p["aero_h"] - 80)),
             "steel")
    body.add("venturi", box(ax - 25, ay + 70, 230, ax + 25, yf + 25, 270), "inst_dark")
    # the vacuum extractor on the right
    vx = x0 + L + 60 + p["vac_w"] / 2
    vy = (yf + yb) / 2
    body.add("vacuum extractor", rbox(p["vac_w"], p["vac_d"], p["vac_h"] - 60, 60, x=vx, y=vy, z=60), "inst_grey")
    body.add("extractor head", rbox(p["vac_w"] - 20, p["vac_d"] - 20, 60, 50, x=vx, y=vy, z=p["vac_h"] - 60), "inst_dark")
    body.add("extractor wheels", box(vx - p["vac_w"] / 2 + 30, vy - 120, 0, vx - p["vac_w"] / 2 + 70, vy + 120, 60).union(
        box(vx + p["vac_w"] / 2 - 70, vy - 120, 0, vx + p["vac_w"] / 2 - 30, vy + 120, 60)), "inst_black")
    from common import hose as _hose
    body.add("extract hose", _hose([(bx, yb - 30, 150), (bx, yb + 50, 150), (vx - 80, yb + 50, 220),
                                     (vx - 80, vy + 40, p["vac_h"] - 30)], 38), "inst_black")
    dome = _piece(inst, "lid")
    dome.add("clear dome", rbox(p["aero_l"] - 40, p["aero_w"] - 30, 70, 40, x=ax, y=ay, z=p["aero_h"] - 60)
             .edges(">Z").fillet(25).cut(rbox(p["aero_l"] - 50, p["aero_w"] - 40, 66, 36, x=ax, y=ay,
                                               z=p["aero_h"] - 60)), "polycarb")
    vial = _piece(inst, "sample")
    vial.add("vial", cyl(28, 61, z=0).cut(cyl(25, 60, z=2)), "window")
    vial.add("powder", cyl(25, 30, z=2), "powder")
    beam = _piece(inst, "beam")
    beam.add("laser", _xcyl(3, L - 80, x=xb - L / 2 + 40, y=(yf + yb) / 2, z=220), "laser")
    for i in range(16):
        t = i / 15.0
        beam.add(f"grain {i}", cq.Workplane("XY").sphere(2.4).translate((
            ax + 5 * math.sin(i * 1.9), ay + (yf + 60 - ay) * t, p["aero_h"] - 60 - 160 * t)), "powder")
    hinge_y = ay + (p["aero_w"] - 30) / 2        # the dome's back edge, on top: hinged at the bottom it would swing
    inst.joints = {                              # back into the bench; hinged at the top its front rises (angle < 0)
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, hinge_y, p["aero_h"] + 10), deg=-70.0),
        "sample": Joint("path", path=((ax - 250, ay - 400, p["aero_h"] + 140), (ax, ay - 250, p["aero_h"] + 50),
                                      (ax, hy, p["aero_h"] + 20))),     # in from the front, under the raised dome
        "beam": Joint("fade"),
    }
    inst.actions = [
        ("The Aero S's clear dome lifts; a vial of atomized powder (a few grams) is emptied into its hopper.", 2.2,
         {"lid": (0.0, 1.0), "sample": (0.0, 1.0), "beam": (0.0, 0.0)}),
        ("Dome down. A vibrating tray feeds the powder to a venturi in the cell bay; compressed air disperses it "
         "across the laser (drawn see-through).", 2.6, {"sample": (1.0, 0.0), "lid": (1.0, 0.0), "beam": (0.0, 1.0),
                                                        "~body": (0.0, 1.0)}),
        ("The scattering pattern gives the size distribution, 0.1 um to 3.5 mm, in under a minute; the vacuum "
         "extractor takes the powder away.", 2.0, {"beam": (1.0, 0.0), "~body": (1.0, 0.0)}),
    ]
    inst.labels = [("Aero S dry disperser", (ax, ay, p["aero_h"] - 40), (0.20, 0.22)),
                   ("optical bench", (xb + L / 2 - 120, yf, 300), (0.50, 0.70)),
                   ("vacuum extractor", (vx, vy - p["vac_d"] / 2, 300), (0.86, 0.55))]
    inst.cam = (0.5, -1.7, 0.8)
    return inst


# ===================================================================================================== wire EDM
# FANUC ROBOCUT alpha-C400iC wire EDM: 2120 W x 2540 D x 1970 H mm (2120 mm with the safety cover up), about 2200 kg;
# workpieces up to 730 x 630 x 250 mm and 500 kg; X/Y travel 400 x 300 mm, Z 255 mm (FANUC America data sheet and
# floor plan). The machine is 1210 mm wide on the left, its control cabinet 900 mm on the right. The look from FANUC's
# photo: off-white sheet metal, the upper head with a triangular window onto the wire spool and the yellow FANUC
# ROBOCUT badge, a yellow work-tank door with a wide window, the CNC panel on the cabinet. It cuts printed parts off
# their build plate; at 1970 mm and 2.2 t it stands beside the VLM.
EDM = dict(W=2120.0, D=2540.0, H=1970.0, mach_w=1210.0, base_h=700.0, tank_top=1220.0, table_z=780.0,
           head_z0=1230.0, travel_x=360.0)


def wire_edm() -> Instrument:
    p = EDM
    inst = Instrument("wire_edm", "Wire EDM", "FANUC ROBOCUT alpha-C400iC", (p["W"], p["D"], p["H"]),
                      "FANUC America ROBOCUT alpha-C400iC data sheet and floor plan; look from FANUC's photo",
                      floor=True)
    W, D, H = p["W"], p["D"], p["H"]
    xl, xr = -W / 2, W / 2
    xm = xl + p["mach_w"]                   # machine | cabinet
    yf, yb = -D / 2, D / 2
    bz, tz = p["base_h"], p["tank_top"]
    body = _piece(inst, "body")
    body.add("base", box(xl, yf, 40, xm, yb, bz), "inst_white")
    body.add("plinth", box(xl + 20, yf + 20, 0, xm - 20, yb - 20, 40), "inst_grey")
    body.add("base panel", box(xl + 120, yf - 2, 90, xm - 120, yf, bz - 220), "inst_offwhite")
    body.add("base badge", box(xl + 450, yf - 4, bz - 160, xl + 800, yf - 2, bz - 120), "inst_light")
    tx0, tx1 = xl + 200, xm - 150           # the work tank
    ty0, ty1 = yf + 60, yf + 760
    body.add("tank", box(tx0, ty0 + 30, bz, tx1, ty1, tz).cut(box(tx0 + 20, ty0 + 20, bz + 20, tx1 - 20, ty1 - 20,
                                                                    tz + 1)), "stainless")
    # a U-shaped table, open at the back for the lower arm. A vertical wire can only cut parts off their build plate
    # along its face, so the plate stands on its edge against an angle plate on a bridge, its parts facing the door
    # (lying flat, the wire would have sliced down through the bars and the plate, and the lower arm drove through it)
    tzt = p["table_z"]
    body.add("table", box(tx0 + 120, ty0 + 150, bz + 20, tx1 - 120, ty1 - 150, tzt).cut(
        box(tx0 + 200, ty0 + 230, bz + 19, tx1 - 200, ty1 - 149, tzt + 1)), "steel")
    px, py, pz = (tx0 + tx1) / 2, ty0 + 390, tzt + 115         # the build plate's back face and centre, on edge
    wy = py - 28                                               # the wire, 3 mm in front of the plate's face
    body.add("fixture", box(tx0 + 160, py, tzt, tx1 - 160, py + 40, tzt + 50).union(
        box(px - 100, py, tzt + 50, px + 100, py + 25, pz + 50)), "steel")
    body.add("column", box(xl + 250, ty1, bz, xm - 200, yb - 300, p["head_z0"] + 120), "inst_offwhite")
    hx0, hx1 = xl + 160, xm - 120
    head = box(hx0, yf + 200, p["head_z0"], hx1, yb - 600, H)
    body.add("upper housing", head, "inst_white")
    tri = cq.Workplane("XZ").polyline([(hx0 + 40, p["head_z0"] + 60), (hx0 + 600, p["head_z0"] + 60),
                                       (hx0 + 40, H - 120)]).close().extrude(2).translate((0, yf + 199, 0))
    body.add("spool window", tri, "inst_dark")
    body.add("wire spool", _ycyl(260, 120, x=hx0 + 220, y=yf + 230, z=p["head_z0"] + 330), "brass_wire")
    body.add("badge", box(hx1 - 330, yf + 196, H - 230, hx1 - 40, yf + 200, H - 60), "inst_yellow")
    # the control cabinet with the CNC panel and its pendant
    body.add("cabinet", box(xm + 10, yf + 300, 0, xr, yb - 500, 1250), "inst_white")
    panel = box(xm + 120, yf + 300, 0, xr - 120, yf + 380, 520).rotate((0, yf + 380, 0), (1, yf + 380, 0), -12)
    body.add("CNC panel", panel.translate((0, 0, 1250)), "inst_dark")
    scr = box(xm + 170, yf + 296, 270, xr - 170, yf + 300, 500).rotate((0, yf + 380, 0), (1, yf + 380, 0), -12)
    body.add("CNC screen", scr.translate((0, 0, 1250)), "screen_on")
    body.add("CNC e-stop", _ycyl(40, 20, x=xr - 170, y=yf + 270, z=1300), "inst_red")
    body.add("pendant", box(xm + 40, yf + 280, 1380, xm + 110, yf + 320, 1560), "inst_dark")
    # the yellow tank door drops into the base to load; the wire head traverses X
    door = _piece(inst, "door")
    door.add("tank door", box(tx0 - 10, ty0, bz + 10, tx1 + 10, ty0 + 30, tz).cut(       # the window shows the tank
        box(tx0 + 80, ty0 - 1, tz - 230, tx1 - 80, ty0 + 31, tz - 50)), "inst_yellow")
    door.add("door window", box(tx0 + 80, ty0 + 10, tz - 230, tx1 - 80, ty0 + 20, tz - 50), "window")
    door.add("door warning", box(tx1 - 140, ty0 - 2, bz + 60, tx1 - 60, ty0, bz + 140), "inst_black")
    hd = _piece(inst, "wirehead")
    gx = px - p["travel_x"] / 2
    hd.add("upper guide", box(gx - 60, wy - 60, tzt + 260, gx + 60, wy + 60, p["head_z0"] + 20), "inst_offwhite")
    hd.add("upper nozzle", cyl(40, 40, x=gx, y=wy, z=tzt + 220), "steel")
    hd.add("lower arm", box(gx - 40, wy - 40, tzt - 40, gx + 40, ty1 - 20, tzt - 2), "steel")     # under the work
    hd.add("lower nozzle", cyl(40, 22, x=gx, y=wy, z=tzt - 2), "steel")
    hd.add("wire", cyl(2.0, 200, x=gx, y=wy, z=tzt + 20), "brass_wire")
    plate = _piece(inst, "load")                 # built flat, parts up, then stood on its edge: parts toward -y
    on_edge = dict(axisStartPoint=(0, 0, 0), axisEndPoint=(1, 0, 0), angleDegrees=90)
    plate.add("build plate", cyl(170, 25, z=0).rotate(**on_edge), "steel")
    for i, (xx, yy) in enumerate([(-45, -30), (0, -30), (45, -30), (-45, 30), (0, 30), (45, 30)]):
        plate.add(f"printed bar {i + 1}", box(xx - 6, yy - 20, 25, xx + 6, yy + 20, 105).rotate(**on_edge), "sample")
    water = _piece(inst, "glow")
    water.add("dielectric", box(tx0 + 22, ty0 + 52, bz + 22, tx1 - 22, ty1 - 22, tz - 40), "water")
    inst.joints = {
        "door": Joint("slide", vec=(0, 0, -(tz - bz) + 30)),
        "load": Joint("path", path=((px, yf - 700, 1250), (px, yf - 200, 1200), (px, py - 200, pz + 40), (px, py, pz))),
        "wirehead": Joint("slide", vec=(p["travel_x"], 0, 0)),
        "glow": Joint("fade"),
    }
    inst.actions = [
        ("The yellow tank door drops. A build plate with printed bars is clamped on its edge, parts facing out.", 2.6,
         {"door": (0.0, 1.0), "load": (0.0, 1.0), "glow": (0.0, 0.0)}),
        ("Door up; the tank fills with deionized water, the dielectric.", 1.8, {"door": (1.0, 0.0), "glow": (0.0, 1.0)}),
        ("The brass wire, held between the upper and lower guides, runs along the plate's face and cuts the parts "
         "off at their base.", 3.2, {"wirehead": (0.0, 1.0)}),
        ("Drained and opened. At 1970 mm and 2.2 t it stands beside the VLM; no benchtop wire EDM is sold.", 2.2,
         {"glow": (1.0, 0.0), "door": (0.0, 1.0), "wirehead": (1.0, 0.0)}),
    ]
    inst.labels = [("wire spool", (hx0 + 220, yf + 200, p["head_z0"] + 330), (0.14, 0.25)),
                   ("work tank", (tx0, ty0, bz + 300), (0.12, 0.62)),
                   ("CNC panel", (xm + 400, yf + 330, 1600), (0.86, 0.25))]
    inst.cam = (0.9, -2.0, 0.85)
    return inst


# ===================================================================================================== glovebox
# An inert-gas glovebox for the oxidation-sensitive powders, set up for automation: the arm stays outside and works
# through an automatic antechamber, which a PLC evacuates and refills on its own (the recommendation in DAL PR #185's
# decision matrix and DAL #130; LC Technology quoted its AC-601 automatic antechamber control, VAC's NexGen and
# Inert's PureLab have the same). Envelope from Inert's PureLab HE 2GB drawing (NIST's copy of its manual): 2005 W x
# 834 D x 1794 H mm, a 1219 mm box, 928 mm tall, on an 867 mm stand, glove ports 457 mm apart, a 381 mm (15 in)
# antechamber over the purifier.
GLOVEBOX = dict(W=2005.0, D=834.0, H=1794.0, box_w=1219.0, box_h=928.0, stand_h=867.0, port_dx=457.0, port_d=220.0,
                ante_d=381.0, ante_l=600.0)


def glovebox() -> Instrument:
    p = GLOVEBOX
    inst = Instrument("glovebox", "Inert glovebox with automatic antechamber", "Inert PureLab HE 2GB",
                      (p["W"], p["D"], p["H"]), "Inert PureLab HE 2GB drawing (NIST's copy of Inert's manual); the "
                      "automatic antechamber after DAL #130 and DAL PR #185", floor=True)
    W, D, H = p["W"], p["D"], p["H"]
    xb0 = -W / 2                                # the box on the left, the antechamber bay on the right
    xb1 = xb0 + p["box_w"]
    yf, yb = -D / 2, D / 2
    sz, tz = p["stand_h"], p["stand_h"] + p["box_h"]
    body = _piece(inst, "body")
    stand = None
    for x in (xb0 + 30, xb1 - 30, W / 2 - 30):
        for y in (yf + 40, yb - 40):
            q = box(x - 25, y - 25, 0, x + 25, y + 25, sz)
            stand = q if stand is None else stand.union(q)
    stand = stand.union(box(xb0, yf + 15, sz - 60, W / 2, yb - 15, sz)).union(box(xb0, yf + 15, 120, W / 2, yb - 15, 160))
    body.add("stand", stand, "inst_grey")
    shell = _wedge(p["box_w"], D - 40, D - 240, p["box_h"], x=(xb0 + xb1) / 2, y0=yf + 20, z=sz)
    shell = shell.cut(_wedge(p["box_w"] - 60, D - 100, D - 300, p["box_h"] - 60, x=(xb0 + xb1) / 2, y0=yf + 50, z=sz + 30))
    # the sloped window with its two glove ports, and the gloves
    import math as _m
    slope = _m.atan2(200, p["box_h"])           # the front leans back 200 mm over the box's height
    opening = box(xb0 + 50, -60, 50, xb1 - 50, 60, p["box_h"] - 50).rotate((0, 0, 0), (1, 0, 0), -_m.degrees(slope))
    shell = shell.cut(opening.translate((0, yf + 20, sz)))
    body.add("box", shell, "stainless")
    win = box(xb0 + 40, 4, 40, xb1 - 40, 10, p["box_h"] - 40).rotate((0, 0, 0), (1, 0, 0), -_m.degrees(slope))
    body.add("window", win.translate((0, yf + 20, sz)), "polycarb")
    port_y = yf + 20 + 7 / _m.cos(slope) + 300 * _m.tan(slope)      # the window's mid-plane, 300 mm up
    for sx in (-1, 1):
        px = (xb0 + xb1) / 2 + sx * p["port_dx"] / 2
        ring = _ycyl(p["port_d"] + 40, 30, x=px, y=-15, z=0).cut(_ycyl(p["port_d"], 32, x=px, y=-16, z=0))
        ring = ring.rotate((0, 0, 0), (1, 0, 0), -_m.degrees(slope)).translate((0, port_y, sz + 300))
        body.add(f"port {sx}", ring, "inst_dark")
        glove = _ycyl(p["port_d"] - 10, 420, x=px, y=-15, z=0).rotate((0, 0, 0), (1, 0, 0), -_m.degrees(slope))
        body.add(f"glove {sx}", glove.translate((0, port_y, sz + 300)), "glove")
    # purifier, controls and the automatic antechamber over it, on the right
    body.add("purifier", box(xb1 + 20, yf + 30, 160, W / 2 - 20, yb - 30, sz - 60), "inst_blue")
    body.add("touch panel", box(xb1 + 60, yf + 60, tz - 250, xb1 + 380, yf + 90, tz - 30), "inst_dark")
    body.add("touch screen", box(xb1 + 80, yf + 58, tz - 230, xb1 + 360, yf + 60, tz - 50), "screen_on")
    body.add("panel arm", box(xb1 - 5, yf + 70, tz - 160, xb1 + 60, yf + 110, tz - 120), "inst_grey")
    ay = (yf + yb) / 2
    az = sz + p["ante_d"] / 2 + 80
    ante = _xcyl(p["ante_d"], p["ante_l"], x=xb1, y=ay, z=az).cut(_xcyl(p["ante_d"] - 20, p["ante_l"] - 9,
                                                                         x=xb1 + 10, y=ay, z=az))
    body.add("antechamber", ante, "stainless")
    body.add("antechamber cradle", box(xb1 + 60, ay - 160, sz - 60, xb1 + p["ante_l"] - 60, ay + 160, az - 120)
             .cut(_xcyl(p["ante_d"], p["ante_l"], x=xb1, y=ay, z=az)), "inst_grey")
    body.add("mini antechamber", _xcyl(150, 300, x=xb0 - 300, y=ay - 150, z=sz + 450), "stainless")
    body.add("vacuum pump", box(xb0 + 200, yf + 120, 160, xb0 + 560, yb - 160, 420), "inst_dark")
    door = _piece(inst, "door")
    door.add("outer door", _xcyl(p["ante_d"] + 30, 30, x=xb1 + p["ante_l"], y=ay, z=az), "stainless")
    door.add("door handle", box(xb1 + p["ante_l"] + 30, ay - 15, az - 80, xb1 + p["ante_l"] + 55, ay + 15, az + 80),
             "inst_dark")
    tray = _piece(inst, "load")
    tray.add("transfer tray", box(-150, -100, 0, 150, 100, 6), "aluminium")
    tray.add("powder jar", cyl(60, 80, x=-60, z=6), "inst_white")
    tray.add("powder jar lid", cyl(64, 15, x=-60, z=86), "inst_blue")
    tray.add("vial", cyl(28, 61, x=60, z=6), "window")
    hinge = (xb1 + p["ante_l"] + 15, ay + p["ante_d"] / 2 + 15, 0)
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=hinge, deg=105.0),          # out, about its back edge
        "load": Joint("path", path=((xb1 + p["ante_l"] + 700, ay - 400, az + 200), (xb1 + p["ante_l"] + 250, ay, az - 60),
                                    (xb1 + p["ante_l"] / 2, ay, az - p["ante_d"] / 2 + 41))),
    }
    inst.actions = [
        ("The automatic antechamber's outer door swings open on the side facing the line, where an arm outside "
         "can reach it.", 1.8, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("A tray with a powder jar and a vial goes in.", 2.0, {"load": (0.0, 1.0)}),
        ("Door shut. The PLC evacuates and refills it three times on its own, then someone at the gloves (or an arm "
         "inside) takes it in. Under 1 ppm O2 and H2O.", 2.4, {"door": (1.0, 0.0), "~body": (0.0, 0.6)}),
        ("", 1.0, {"~body": (0.6, 0.0)}),
    ]
    inst.labels = [("automatic antechamber", (xb1 + p["ante_l"] / 2, ay, az + p["ante_d"] / 2), (0.78, 0.22)),
                   ("glove ports", ((xb0 + xb1) / 2, yf + 80, sz + 300), (0.14, 0.32)),
                   ("gas purifier", (xb1 + 300, yf + 30, 500), (0.84, 0.70))]
    inst.cam = (1.2, -1.8, 0.8)
    return inst


# ===================================================================================================== registry
def _registry() -> dict:
    def ofm(which):
        def build():
            import openflexure
            return getattr(openflexure, which)()
        return build
    g = dict(globals(), openflexure_v7=ofm("v7"), openflexure_delta=ofm("delta"))
    names = ["xrd", "sem", "pip", "openflexure_v7", "openflexure_delta", "nanoindenter", "polisher", "furnace",
             "mastersizer", "instron_small", "instron_floor", "wire_edm", "glovebox", "rail"]
    return {k: g[k] for k in names if k in g}


REGISTRY = _registry()

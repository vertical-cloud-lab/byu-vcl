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
    A piece with a parent rides on that piece."""
    kind: str
    vec: tuple = (0.0, 0.0, 0.0)
    axis: tuple = (0.0, 0.0, 1.0)
    pivot: tuple = (0.0, 0.0, 0.0)
    deg: float = 0.0
    path: tuple = ()
    parent: str | None = None
    v0: float = 0.0                  # the value it starts at in the tour

    def matrix(self, v: float) -> np.ndarray:
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
    meshes: dict = field(default_factory=dict)     # name -> [(PolyData, rgb, opacity)]: pieces that are meshes, not CAD
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
# Nabertherm LT 9/11 (lift door): 1100 C chamber furnace, 9 L, 230 x 240 x 170 mm chamber. Solution treatment of
# the Al alloys (~530-550 C) and ageing (~160-200 C) both fit its range; the lift door keeps the hot face away from
# the operator, and from an arm. Envelope from Nabertherm's L/LT data table (see SPECS).
FURNACE = dict(W=415.0, D=455.0, H=515.0, door_lift=200.0, ch_w=230.0, ch_d=240.0, ch_h=170.0, ch_z=200.0)


def furnace() -> Instrument:
    p = FURNACE
    inst = Instrument("furnace", "Heat treatment and ageing furnace", "Nabertherm LT 9/11", (p["W"], p["D"], p["H"]),
                      "Nabertherm L/LT 3-40 data sheet (outer and chamber dimensions); look from Nabertherm's photos")
    W, D, H = p["W"], p["D"], p["H"]
    body = _piece(inst, "body")
    y0 = -D / 2
    shell = rbox(W, D, H - 20, 6, y=0, z=20)
    cw, chh, cz = p["ch_w"], p["ch_h"], p["ch_z"]
    shell = shell.cut(box(-cw / 2 - 20, y0 - 1, cz - 20, cw / 2 + 20, y0 + 60, cz + chh + 20))
    body.add("housing", shell, "stainless")
    body.add("chamber", box(-cw / 2 - 20, y0 + 60, cz - 20, cw / 2 + 20, y0 + 70, cz + chh + 20).union(
        box(-cw / 2 - 20, y0 + 5, cz - 20, -cw / 2, y0 + 70 + p["ch_d"], cz + chh + 20)).union(
        box(cw / 2, y0 + 5, cz - 20, cw / 2 + 20, y0 + 70 + p["ch_d"], cz + chh + 20)).union(
        box(-cw / 2 - 20, y0 + 5, cz - 20, cw / 2 + 20, y0 + 70 + p["ch_d"], cz)).union(
        box(-cw / 2 - 20, y0 + 5, cz + chh, cw / 2 + 20, y0 + 70 + p["ch_d"], cz + chh + 20)), "refractory")
    body.add("controller panel", box(-W / 2 + 25, y0 - 4, 40, W / 2 - 25, y0, cz - 45), "inst_black")
    body.add("controller screen", box(W / 2 - 170, y0 - 6, 70, W / 2 - 50, y0 - 4, 150), "screen_on")
    body.add("power switch", box(-W / 2 + 50, y0 - 8, 95, -W / 2 + 80, y0 - 4, 125), "inst_green")
    body.add("feet", box(-W / 2 + 15, -D / 2 + 15, 0, -W / 2 + 55, D / 2 - 15, 20).union(
        box(W / 2 - 55, -D / 2 + 15, 0, W / 2 - 15, D / 2 - 15, 20)), "inst_black")
    body.add("exhaust", cyl(40, 60, y=D / 2 - 90, z=H), "stainless")
    body.add("door guides", box(-cw / 2 - 45, y0 - 30, cz - 30, -cw / 2 - 30, y0, H + 10).union(
        box(cw / 2 + 30, y0 - 30, cz - 30, cw / 2 + 45, y0, H + 10)), "inst_dark")
    # the glowing chamber, faded in while it heats
    glow = _piece(inst, "glow")
    glow.add("hot chamber", box(-cw / 2 + 2, y0 + 72, cz + 2, cw / 2 - 2, y0 + 68 + p["ch_d"], cz + chh - 2)
             .cut(box(-cw / 2 + 4, y0 + 70, cz + 4, cw / 2 - 4, y0 + 66 + p["ch_d"], cz + chh - 4)), "glow")
    # lift door: a refractory plug in a steel frame; out 30 mm, then straight up
    door = _piece(inst, "door")
    door.add("door", box(-cw / 2 - 28, y0 - 28, cz - 28, cw / 2 + 28, y0, cz + chh + 28), "stainless")
    door.add("door plug", box(-cw / 2 - 18, y0, cz - 18, cw / 2 + 18, y0 + 58, cz + chh + 18), "refractory")
    door.add("door handle", box(-60, y0 - 45, cz + chh + 8, 60, y0 - 28, cz + chh + 20), "inst_black")
    # the load: a ceramic tray with three tensile coupons
    load = _piece(inst, "load")
    load.add("tray", box(-90, -60, 0, 90, 60, 12).cut(box(-84, -54, 4, 84, 54, 13)), "refractory")
    for i, x in enumerate((-50, 0, 50)):
        load.add(f"coupon {i + 1}", box(x - 8, -45, 4, x + 8, 45, 8), "sample")
    chamber_c = (0.0, y0 + 70 + p["ch_d"] / 2, cz + 2)
    inst.joints = {
        "door": Joint("path", path=((0, 0, 0), (0, -30, 0), (0, -30, p["door_lift"]))),
        "load": Joint("path", path=((0, y0 - 260, cz + 60), (0, y0 - 120, cz + 2), chamber_c), v0=0.0),
        "glow": Joint("fade"),
    }
    inst.actions = [
        ("The lift door rises: out 30 mm, then straight up, so the hot face never swings towards the arm.", 1.6,
         {"door": (0.0, 1.0), "load": (0.0, 0.0), "glow": (0.0, 0.0)}),
        ("A tray of printed tensile coupons goes in on the chamber floor.", 1.8, {"load": (0.0, 1.0)}),
        ("Door down. Solution treatment at 530 C, then ageing at 160-200 C: the same furnace, two programs.", 2.4,
         {"door": (1.0, 0.0), "glow": (0.0, 1.0)}),
    ]
    inst.labels = [("lift door", (0, y0 - 30, cz + chh + 30), (0.15, 0.30)),
                   ("controller", (W / 2 - 110, y0 - 6, 110), (0.80, 0.70))]
    inst.cam = (0.9, -1.7, 0.8)
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


# Instron 6800 Series floor model, 68FM-100 (100 kN): envelope from Instron's 6800 Series floor-model data (SPECS).
INSTRON_FM = dict(W=1257.0, D=762.0, H=2459.0, base_h=660.0, col_dx=575.0, col_w=150.0, xh_h=190.0, top_h=170.0,
                  xh_z=1450.0, travel=180.0)


def instron_floor() -> Instrument:
    p = INSTRON_FM
    inst = Instrument("instron_floor", "Universal testing machine, floor model", "Instron 68FM-100",
                      (p["W"], p["D"], p["H"]), "Instron 6800 Series floor-model specifications; look from Instron's "
                      "photos (grey frame, black base, blue crosshead trim)", floor=True)
    W, D, H = p["W"], p["D"], p["H"]
    body = _piece(inst, "body")
    body.add("base", rbox(W, D, p["base_h"], 20), "inst_dark")
    body.add("base front", box(-W / 2 + 60, -D / 2 - 3, 120, W / 2 - 60, -D / 2, p["base_h"] - 60), "inst_black")
    body.add("logo plate", box(-150, -D / 2 - 5, p["base_h"] - 140, 150, -D / 2 - 3, p["base_h"] - 90), "inst_blue")
    cx = p["col_dx"] / 2 + p["col_w"] / 2
    cols = None
    for sx in (-1, 1):
        c = rbox(p["col_w"], p["col_w"] + 40, H - p["base_h"] - p["top_h"], 10, x=sx * cx, z=p["base_h"])
        cols = c if cols is None else cols.union(c)
    body.add("columns", cols, "inst_light")
    body.add("top plate", rbox(p["col_dx"] + 2 * p["col_w"] + 80, D - 220, p["top_h"], 14, z=H - p["top_h"]),
             "inst_dark")
    body.add("lower grip", _wedge_grip(p["base_h"] + 90, up=True), "steel")
    body.add("lower adapter", cyl(70, 90, z=p["base_h"]), "steel")
    body.add("handset", rbox(110, 60, 160, 8, x=cx + p["col_w"] / 2 + 70, y=-120, z=1150), "inst_dark")
    body.add("handset screen", box(cx + p["col_w"] / 2 + 30, -151, 1220, cx + p["col_w"] / 2 + 110, -150, 1290),
             "screen_on")
    body.add("handset arm", box(cx + p["col_w"] / 2, -110, 1200, cx + p["col_w"] / 2 + 20, -80, 1240), "inst_dark")
    # the moving crosshead with the load cell and the upper grip
    xh = _piece(inst, "crosshead")
    z = p["xh_z"]
    xh.add("crosshead", rbox(p["col_dx"] + 2 * p["col_w"] + 60, D - 260, p["xh_h"], 12, z=z), "inst_dark")
    xh.add("crosshead trim", box(-p["col_dx"] / 2, -(D - 260) / 2 - 3, z + 60, p["col_dx"] / 2, -(D - 260) / 2,
                                 z + p["xh_h"] - 60), "inst_blue")
    xh.add("load cell", cyl(110, 70, z=z - 70), "chrome")
    xh.add("upper grip", _wedge_grip(z - 70, up=False), "steel")
    spec = _piece(inst, "specimen")
    g0, g1 = p["base_h"] + 90 + 110, z - 70 - 110
    spec.add("specimen", _dogbone(L=g1 - g0 + 120, w=12.5, grip_w=20, t=4, gauge=g1 - g0 - 60)
             .translate((0, 0, (g0 + g1) / 2)), "sample")
    inst.joints = {"crosshead": Joint("slide", vec=(0, 0, p["travel"]))}
    inst.actions = [
        ("A printed tensile bar in the wedge grips. The crosshead pulls at a constant rate; the load cell above "
         "the upper grip reads the force.", 3.0, {"crosshead": (0.0, 0.15)}),
        ("Ductile fracture: the crosshead returns. 100 kN capacity, about 2.5 m tall, so it stands beside the VLM.",
         2.2, {"crosshead": (0.15, 0.0)}),
    ]
    inst.labels = [("moving crosshead", (0, -(D - 260) / 2, z + p["xh_h"] / 2), (0.15, 0.25)),
                   ("load cell", (0, -55, z - 35), (0.82, 0.32)),
                   ("wedge grips", (0, -35, p["base_h"] + 150), (0.82, 0.62))]
    inst.cam = (1.0, -2.4, 0.9)
    return inst


# Instron 6800 Series single column, 68SC-2 (2 kN) tabletop: envelope from Instron's single-column data (SPECS).
INSTRON_SC = dict(W=420.0, D=600.0, H=1100.0, base_h=170.0, col_w=150.0, col_d=150.0, arm_l=270.0, arm_h=110.0,
                  xh_z=640.0, travel=60.0)


def instron_small() -> Instrument:
    p = INSTRON_SC
    inst = Instrument("instron_small", "Universal testing machine, tabletop", "Instron 68SC-2",
                      (p["W"], p["D"], p["H"]), "Instron 6800 Series single-column specifications; look from "
                      "Instron's photos")
    W, D, H = p["W"], p["D"], p["H"]
    body = _piece(inst, "body")
    col_y = D / 2 - p["col_d"] / 2 - 20
    body.add("base", rbox(W, D, p["base_h"], 16), "inst_dark")
    body.add("base front", box(-W / 2 + 40, -D / 2 - 3, 40, W / 2 - 40, -D / 2, p["base_h"] - 40), "inst_black")
    body.add("column", rbox(p["col_w"], p["col_d"], H - p["base_h"], 12, y=col_y, z=p["base_h"]), "inst_light")
    body.add("column cap", rbox(p["col_w"] + 10, p["col_d"] + 10, 30, 12, y=col_y, z=H - 30), "inst_dark")
    gy = col_y - p["col_d"] / 2 - p["arm_l"] + 70        # grips' axis, in front of the column
    body.add("lower grip", _wedge_grip(p["base_h"] + 60, up=True, w=60, h=70).translate((0, gy, 0)), "steel")
    body.add("lower adapter", cyl(50, 60, y=gy, z=p["base_h"]), "steel")
    body.add("logo plate", box(-90, -D / 2 - 5, p["base_h"] - 70, 90, -D / 2 - 3, p["base_h"] - 45), "inst_blue")
    xh = _piece(inst, "crosshead")
    z = p["xh_z"]
    xh.add("arm", rbox(p["col_w"] + 30, p["arm_l"], p["arm_h"], 10, y=col_y - p["arm_l"] / 2 + p["col_d"] / 2 - 10,
                       z=z), "inst_dark")
    xh.add("arm trim", box(-60, col_y - p["arm_l"] + p["col_d"] / 2 - 13, z + 30, 60,
                           col_y - p["arm_l"] + p["col_d"] / 2 - 10, z + p["arm_h"] - 30), "inst_blue")
    xh.add("load cell", cyl(70, 50, y=gy, z=z - 50), "chrome")
    xh.add("upper grip", _wedge_grip(z - 50, up=False, w=60, h=70).translate((0, gy, 0)), "steel")
    spec = _piece(inst, "specimen")
    g0, g1 = p["base_h"] + 60 + 70, z - 50 - 70
    spec.add("specimen", _dogbone(L=g1 - g0 + 70, w=4, grip_w=8, t=1.5, gauge=g1 - g0 - 30)
             .translate((0, gy, (g0 + g1) / 2)), "sample")
    inst.joints = {"crosshead": Joint("slide", vec=(0, 0, p["travel"]))}
    inst.actions = [
        ("A sub-size printed bar in its grips. The arm rides up the single column and pulls it.", 2.6,
         {"crosshead": (0.0, 0.25)}),
        ("Back to the start. A tabletop frame, but its column is still taller than a tray takes.", 2.0,
         {"crosshead": (0.25, 0.0)}),
    ]
    inst.labels = [("single column", (0, col_y, 900), (0.80, 0.25)), ("grips", (0, gy - 30, 300), (0.16, 0.60))]
    inst.cam = (1.4, -2.2, 0.9)
    return inst


# ===================================================================================================== XRD
# Rigaku MiniFlex (6th generation, "MiniFlex 6G"): 620 W x 722 H x 460 D mm, ~80 kg, vertical goniometer of 150 mm
# radius, theta-2theta (Rigaku MiniFlex 6G sheet; Rigaku brochure). The layout is Rigaku's own outline drawing in the
# brochure: a base with the control panel, the upper housing with a full-height front door between two side posts
# (vertical handle at its left, so it hinges on the right), a raised cover on top, and a bulge on each side.
XRD = dict(W=620.0, D=460.0, H=722.0, body_w=558.0, body_d=395.0, feet=23.0, base_top=294.0, door_top=611.0,
           upper_top=692.0, door_x=199.0, door_t=59.0, gonio_r=150.0, gonio_z=440.0)


def xrd() -> Instrument:
    p = XRD
    inst = Instrument("xrd", "Benchtop X-ray diffractometer", "Rigaku MiniFlex", (p["W"], p["D"], p["H"]),
                      "Rigaku MiniFlex 6G specification sheet (620 W x 722 H x 460 D mm, 80 kg, 150 mm vertical "
                      "goniometer, theta-2theta) and the outline drawing in Rigaku's MiniFlex brochure")
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
    body.add("emergency stop", _ycyl(34, 10, x=160, y=yf - 13, z=245), "inst_red")
    body.add("rear fittings", box(-120, yb, 80, 120, yb + 30, 200), "inst_grey")
    # the upper housing: posts either side of the door, the logo band over it, the chamber behind it
    hood = _piece(inst, "hood")
    upper = box(-bw / 2, yf, p["base_top"], bw / 2, yb, p["upper_top"])
    upper = upper.cut(box(-p["door_x"], yf - 1, p["base_top"], p["door_x"], yf + p["door_t"], p["door_top"]))
    upper = upper.cut(box(-p["door_x"] + 8, yf + p["door_t"] - 1, p["base_top"] + 6, p["door_x"] - 8, yb - 30,
                          p["door_top"] - 6))
    hood.add("upper housing", upper, "inst_white")
    hood.add("logo band", box(-p["door_x"], yf - 2, p["door_top"] + 12, p["door_x"], yf, p["upper_top"] - 12),
             "inst_offwhite")
    hood.add("logo", box(-80, yf - 3, 655, 80, yf - 2, 672), "inst_grey")
    top = cq.Workplane("YZ").polyline([(yf + 95, 0), (yf + 215, 0), (yf + 205, 30), (yf + 105, 30)]).close() \
        .extrude(2 * 188).translate((-188, 0, p["upper_top"]))
    hood.add("top cover", top, "inst_light")
    for sx in (-1, 1):
        w = box(min(sx * bw / 2, sx * (bw / 2 + 31)), yf + 92, 309, max(sx * bw / 2, sx * (bw / 2 + 31)), yf + 216, 543)
        hood.add(f"side bulge {'LR'[sx > 0]}", w.edges("|Y").chamfer(12), "inst_light")
    # inside: the goniometer's back plate, the fixed X-ray tube on the left, the stage and the detector arm
    inner = _piece(inst, "chamber")
    inner.add("chamber lining", box(-p["door_x"] + 8, yb - 34, p["base_top"] + 6, p["door_x"] - 8, yb - 30,
                                    p["door_top"] - 6).union(
        box(-p["door_x"] + 8, yf + p["door_t"], p["base_top"] + 6, p["door_x"] - 8, yb - 30, p["base_top"] + 10)),
        "inst_dark")
    inner.add("goniometer", _ycyl(250, 12, y=yb - 46, z=gz), "inst_grey")
    inner.add("goniometer hub", _ycyl(70, 120, y=gy - 20, z=gz).cut(_ycyl(40, 200, y=gy - 100, z=gz)), "aluminium")
    tube_x0 = -p["gonio_r"]
    inner.add("X-ray tube", _xcyl(64, 170, x=tube_x0 - 140, y=gy, z=gz), "inst_black")
    inner.add("tube window", _xcyl(30, 30, x=tube_x0 + 30, y=gy, z=gz), "steel")
    inner.add("divergence slit", box(tube_x0 + 60, gy - 18, gz - 18, tube_x0 + 66, gy + 18, gz + 18), "brass")
    stage = _piece(inst, "stage")
    stage.add("sample stage", box(-35, gy - 30, gz - 16, 35, gy + 30, gz - 3), "aluminium")
    holder = _piece(inst, "holder")
    holder.add("sample holder", box(-22, -26, 0, 22, 26, 2.5), "window")
    holder.add("powder", box(-10, -10, 2.5, 10, 10, 3.0), "powder")
    det = _piece(inst, "detector")
    r = p["gonio_r"]
    d_shape = box(r - 10, gy - 30, -28, r + 120, gy + 30, 28).union(_xcyl(36, 30, x=r - 40, y=gy, z=0))
    d_shape = d_shape.rotate((0, gy, 0), (0, gy + 1, 0), -10.0).translate((0, 0, gz))    # 2theta = 10 deg
    det.add("D/teX detector", d_shape, "inst_dark")
    door = _piece(inst, "door")
    door.add("door", box(-p["door_x"] + 1, yf, p["base_top"] + 1, p["door_x"] - 1, yf + p["door_t"] - 2,
                         p["door_top"] - 1), "inst_white")
    door.add("door logo", box(-40, yf - 1, 340, 70, yf, 352), "inst_grey")
    door.add("door handle", box(-178, yf - 33, 353, -166, yf - 20, 461).union(
        box(-178, yf - 33, 353, -166, yf, 365)).union(box(-178, yf - 33, 449, -166, yf, 461)), "inst_grey")
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(p["door_x"], yf, 0), deg=100.0),
        "stage": Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-40.0),
        "holder": Joint("path", parent="stage", path=((0, -420, 120), (0, -260, 60), (0, gy - 60, gz - 3 + 40),
                                                      (0, gy, gz - 3))),
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
        ("The detector parks, the door opens again and the sample comes out.", 2.2,
         {"stage": (1.0, 0.0), "detector": (1.0, 0.0), "~hood": (1.0, 0.0), "~door": (1.0, 0.0),
          "door": (0.0, 1.0)}),
        ("Door shut. At 722 mm tall the MiniFlex just fits a tray: Kardex allows 727.5 mm.", 1.4,
         {"holder": (1.0, 0.0), "door": (1.0, 0.0)}),
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
SEM = dict(W=330.0, D=614.0, H=547.0, feet=25.0, front_z0=30.0, drawer_top=250.0, blue_top=420.0, draw=160.0)


def sem() -> Instrument:
    p = SEM
    inst = Instrument("sem", "Tabletop SEM with EDS and EBSD", "Hitachi TM4000PlusII", (p["W"], p["D"], p["H"]),
                      "Hitachi High-Tech TM4000PlusII specifications (main unit 330 W x 614 D x 547 H mm); look from "
                      "Hitachi's product photo; envelope cross-checked against ac-dev-lab's TM4000II model")
    W, D, H = p["W"], p["D"], p["H"]
    yf, yb = -D / 2, D / 2
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"foot {sx}{sy}", cyl(40, p["feet"], x=sx * (W / 2 - 40), y=sy * (D / 2 - 50)), "chrome")
    shell = rbox(W, D - 10, H - p["feet"] - 70, 18, y=5, z=p["feet"])
    shell = shell.cut(box(-W / 2 + 32, yf - 1, p["front_z0"], W / 2 - 32, yf + 40, p["blue_top"]))
    body.add("body", shell, "inst_white")
    hood = rbox(W - 6, D - 60, 70, 30, y=20, z=H - 70).edges(">Z").fillet(20)
    body.add("top hood", hood, "inst_offwhite")
    body.add("hood ridge", rbox(170, D - 200, 14, 10, y=40, z=H - 2), "inst_offwhite")
    body.add("front panel", box(-W / 2 + 32, yf + 8, p["drawer_top"], W / 2 - 32, yf + 40, p["blue_top"]), "inst_navy")
    body.add("status lights", box(-60, yf + 6, p["blue_top"] - 22, 60, yf + 8, p["blue_top"] - 14), "screen_on")
    body.add("model plate", box(-70, yf + 6, p["blue_top"] - 80, 70, yf + 8, p["blue_top"] - 50), "inst_light")
    body.add("EVAC/AIR button", _ycyl(30, 6, x=W / 2 - 55, y=yf + 2, z=p["blue_top"] - 110), "chrome")
    body.add("drawer frame", box(-W / 2 + 32, yf + 8, p["front_z0"], W / 2 - 32, yf + 40, p["front_z0"] + 4), "inst_navy")
    # detectors: EDS on the right, EBSD on the left, at the chamber's height
    cz = 150.0
    body.add("EDS detector", _xcyl(46, 200, x=W / 2 - 10, y=-60, z=cz).union(
        box(W / 2 + 110, -110, cz - 60, W / 2 + 230, -10, cz + 60)), "inst_light")
    body.add("EDS cold finger cap", _xcyl(50, 20, x=W / 2 + 230, y=-60, z=cz), "inst_dark")
    body.add("EBSD detector", _xcyl(70, 160, x=-W / 2 - 150, y=-40, z=cz).union(
        box(-W / 2 - 260, -95, cz - 55, -W / 2 - 140, 15, cz + 55)), "inst_dark")
    body.add("EBSD camera", _xcyl(40, 60, x=-W / 2 - 320, y=-40, z=cz), "inst_black")
    # the drawer: the chamber's front door, with the stage on its inside face
    drawer = _piece(inst, "drawer")
    drawer.add("drawer front", rbox(W - 70, 30, p["drawer_top"] - p["front_z0"] - 12, 6, y=yf + 15,
                                    z=p["front_z0"] + 6), "inst_navy")
    drawer.add("handle", rbox(160, 16, 22, 8, y=yf - 6, z=p["drawer_top"] - 70), "inst_black")
    drawer.add("stage rails", box(-80, yf + 30, 60, -60, yf + 200, 75).union(box(60, yf + 30, 60, 80, yf + 200, 75)),
               "steel")
    drawer.add("stage", cyl(70, 30, y=yf + 120, z=95), "aluminium")
    drawer.add("stage column", cyl(30, 35, y=yf + 120, z=60), "steel")
    stub = _piece(inst, "stub")
    stub.add("mount", cyl(25, 10, z=0), "mount")
    stub.add("polished face", cyl(15, 0.6, z=10), "sample")
    inst.joints = {
        "drawer": Joint("slide", vec=(0, -p["draw"], 0)),
        "stub": Joint("path", parent="drawer", path=((0, yf - 250, 330), (0, yf + 120, 190), (0, yf + 120, 125))),
    }
    inst.actions = [
        ("AIR vents the chamber; the drawer slides out with the stage on its inside face.", 1.6,
         {"drawer": (0.0, 1.0), "stub": (0.0, 0.0)}),
        ("A polished, mounted sample (25 mm) goes onto the stage.", 2.0, {"stub": (0.0, 1.0)}),
        ("Drawer in, EVAC: about three minutes to vacuum. EDS (right) and EBSD (left) look at the sample in the "
         "chamber; EBSD needs a 70 degree pre-tilted holder.", 2.4, {"drawer": (1.0, 0.0)}),
    ]
    inst.labels = [("EDS detector", (W / 2 + 170, -60, cz + 60), (0.84, 0.28)),
                   ("EBSD detector", (-W / 2 - 200, -40, cz + 55), (0.14, 0.28)),
                   ("sample drawer", (0, yf, 180), (0.18, 0.70))]
    inst.cam = (0.9, -2.0, 0.85)
    return inst


# ===================================================================================================== PIP
# Plastometrex PLX-Benchtop (profilometry-based indentation plastometry): an arch of two rounded pillars under a top
# housing with a blue LED band, an open test space with the indenter head on a crosshead, and a round sample stage
# on an aluminium base (Plastometrex's product render). A spherical indenter pushes into a flat sample, the
# profilometer maps the residual indent, and CORSICA fits the stress-strain curve to the profile. PLX-AutoStage is
# Plastometrex's add-on that automates the loading. Envelope: see SPECS (the proportions are the render's).
PIP = dict(W=560.0, D=520.0, H=750.0, pillar=110.0, base_h=70.0, top_z0=430.0, stage_d=150.0, stage_h=45.0,
           head_z=200.0, stroke=95.0)


def pip() -> Instrument:
    p = PIP
    inst = Instrument("pip", "Indentation plastometer (PIP)", "Plastometrex PLX-Benchtop", (p["W"], p["D"], p["H"]),
                      "Plastometrex's PLX-Benchtop product render and brochure; overall size estimated from the "
                      "render (see SPECS)")
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    body = _piece(inst, "body")
    body.add("base", rbox(W, D, p["base_h"], 20), "inst_dark")
    body.add("base plate", box(-W / 2 + p["pillar"], yf + 20, p["base_h"] - 2, W / 2 - p["pillar"], D / 2 - 40,
                               p["base_h"] + 8), "aluminium")
    for sx in (-1, 1):
        x0, x1 = sorted((sx * W / 2, sx * (W / 2 - p["pillar"])))
        pil = box(x0, yf, p["base_h"], x1, D / 2, p["top_z0"] + 20).edges("|Z").fillet(18)
        body.add(f"pillar {'LR'[sx > 0]}", pil, "inst_dark")
    body.add("back wall", box(-W / 2 + p["pillar"], D / 2 - 60, p["base_h"], W / 2 - p["pillar"], D / 2 - 20,
                              p["top_z0"]), "inst_black")
    body.add("louvres", box(-W / 2 + p["pillar"], yf + 80, p["base_h"] + 40, -W / 2 + p["pillar"] + 4, D / 2 - 80,
                            p["top_z0"] - 120), "inst_grey")
    top = box(-W / 2, yf, p["top_z0"], W / 2, D / 2, H).edges("|Y").fillet(70)
    body.add("top housing", top, "inst_dark")
    body.add("trim", box(-W / 2 - 2, yf - 2, p["top_z0"] - 6, W / 2 + 2, D / 2 + 2, p["top_z0"]), "aluminium")
    body.add("front panel", box(-W / 2 + 80, yf - 3, p["top_z0"] + 70, W / 2 - 80, yf, H - 40), "inst_black")
    led = box(-W / 2 + 74, yf - 5, p["top_z0"] + 64, W / 2 - 74, yf - 3, p["top_z0"] + 72).union(
        box(-W / 2 + 74, yf - 5, p["top_z0"] + 64, -W / 2 + 82, yf - 3, H - 90)).union(
        box(W / 2 - 82, yf - 5, p["top_z0"] + 64, W / 2 - 74, yf - 3, H - 90))
    body.add("LED band", led, "screen_on")
    body.add("e-stop", _xcyl(40, 25, x=W / 2, y=yf + 60, z=p["top_z0"] + 20), "inst_red")
    body.add("e-stop collar", _xcyl(50, 8, x=W / 2, y=yf + 60, z=p["top_z0"] + 20), "inst_yellow")
    body.add("guide columns", cyl(28, p["top_z0"] - p["base_h"], x=-W / 2 + p["pillar"] + 30, y=60, z=p["base_h"])
             .union(cyl(28, p["top_z0"] - p["base_h"], x=W / 2 - p["pillar"] - 30, y=60, z=p["base_h"])), "chrome")
    # the sample stage, which shifts the sample from under the indenter to under the profilometer
    stage = _piece(inst, "stage")
    stage.add("sample stage", cyl(p["stage_d"], p["stage_h"], y=-20, z=p["base_h"] + 8), "aluminium")
    stage.add("anvil", cyl(p["stage_d"] - 30, 8, y=-20, z=p["base_h"] + 8 + p["stage_h"]), "steel")
    # the crosshead with the indenter and the profilometer probe beside it
    head = _piece(inst, "head")
    hz = p["head_z"] + p["base_h"]
    head.add("crosshead", box(-W / 2 + p["pillar"] + 10, -60, hz + 40, W / 2 - p["pillar"] - 10, 120, hz + 120)
             .edges("|Y").fillet(12), "inst_dark")
    head.add("crosshead nose", box(-110, -95, hz + 10, 110, 40, hz + 70).edges("|Y").chamfer(25), "inst_dark")
    for sx in (-1, 1):
        head.add(f"warning {sx}", box(sx * 90 - 14, -97, hz + 45, sx * 90 + 14, -95, hz + 65), "inst_yellow")
    head.add("indenter holder", cyl(36, 60, y=-20, z=hz - 50), "chrome")
    head.add("indenter", cyl(14, 12, y=-20, z=hz - 62), "inst_black")
    head.add("profilometer probe", cyl(16, 70, x=70, y=-20, z=hz - 60), "inst_grey")
    sample = _piece(inst, "sample")
    sample.add("sample", box(-20, -20, 0, 20, 20, 6), "sample")
    stz = p["base_h"] + 8 + p["stage_h"] + 8
    inst.joints = {
        "sample": Joint("path", parent="stage", path=((0, -420, 260), (0, -220, 120), (0, -20, stz + 40),
                                                      (0, -20, stz))),
        "head": Joint("slide", vec=(0, 0, -p["stroke"])),
        "stage": Joint("slide", vec=(-70, 0, 0)),
    }
    gap = p["head_z"] + p["base_h"] - 62 - (stz + 6)
    inst.joints["head"] = Joint("slide", vec=(0, 0, -gap))
    inst.actions = [
        ("A flat sample (3 x 3 x 1.5 mm at the least; here a 40 mm square cut from a print) goes onto the anvil.",
         2.2, {"sample": (0.0, 1.0)}),
        ("The crosshead drives the spherical indenter in: a few hundred newtons, an indent 0.25-1 mm wide.", 1.8,
         {"head": (0.0, 1.0)}),
        ("It lifts off, and the stage carries the indent under the profilometer, which maps its shape.", 2.2,
         {"head": (1.0, 0.0), "stage": (0.0, 1.0)}),
        ("CORSICA fits a stress-strain curve to that profile. The stage returns and the sample comes off.", 2.2,
         {"stage": (1.0, 0.0), "sample": (1.0, 0.0)}),
    ]
    inst.labels = [("indenter", (0, -20, hz - 40), (0.14, 0.40)), ("profilometer", (70, -20, hz - 40), (0.84, 0.40)),
                   ("sample stage", (0, -20 - p["stage_d"] / 2, p["base_h"] + 30), (0.16, 0.72))]
    inst.cam = (0.75, -1.9, 0.75)
    return inst


# ===================================================================================================== rail
# Vention's robot seventh axis, elevated version (Vention's "7th axis" application page and MachineBuilder render): a
# beam of aluminium extrusions on braced legs, two linear guides and a rack on top, a carriage plate with the
# gearmotor and pinion, the robot's adapter plate, a cable chain along the beam and the control cabinet hung under
# it. Vention renders its extrusions blue. The beam height is set so the arm's base sits where it does on the MiR250
# (800 mm), and the axis runs along the fronts of the line. Section and leg sizes are read off the render.
RAIL = dict(beam_w=180.0, beam_h=135.0, top=780.0, leg_pitch=3000.0, car_l=450.0, car_w=400.0, car_t=20.0)


def rail(length: float = 4000.0, travel: float = 1600.0) -> Instrument:
    p = RAIL
    inst = Instrument("rail", "Backup: a floor rail for the arm", "Vention robot 7th axis", (length, 600.0, p["top"]),
                      "Vention's seventh-axis application page and MachineBuilder render; section sizes read off "
                      "the render", floor=True)
    L = length
    bw, bh, top = p["beam_w"], p["beam_h"], p["top"]
    z1 = top - 25.0                         # top of the beam, under the guides
    z0 = z1 - bh
    body = _piece(inst, "body")
    beam = box(-L / 2, -bw / 2, z0, L / 2, bw / 2, z1)
    for y in (-bw / 2 + 22.5, bw / 2 - 22.5):            # the extrusions' T-slots, as grooves
        beam = beam.cut(box(-L / 2 - 1, y - 4, z1 - 8, L / 2 + 1, y + 4, z1 + 1))
    body.add("beam", beam, "inst_blue")
    for y in (-bw / 2 + 30, bw / 2 - 30):
        body.add(f"guide {y:+.0f}", box(-L / 2 + 20, y - 10, z1, L / 2 - 20, y + 10, z1 + 15), "steel")
    body.add("rack", box(-L / 2 + 20, -bw / 2 - 12, z1 - 40, L / 2 - 20, -bw / 2, z1), "steel")
    body.add("chain tray", box(-L / 2, bw / 2, z0 + 20, L / 2, bw / 2 + 90, z0 + 30).union(
        box(-L / 2, bw / 2 + 85, z0 + 20, L / 2, bw / 2 + 90, z0 + 70)), "inst_blue")
    body.add("cable chain", box(-L / 2 + 100, bw / 2 + 10, z0 + 30, 0, bw / 2 + 80, z0 + 75), "inst_black")
    n_legs = max(2, int(round(L / p["leg_pitch"])) + 1)
    legs = None
    for i in range(n_legs):
        x = -L / 2 + 150 + i * (L - 300) / (n_legs - 1)
        leg = box(x - 45, -45, 20, x + 45, 45, z0).union(box(x - 160, -160, 0, x + 160, 160, 20))
        for sx in (-1, 1):                     # gussets
            g = cq.Workplane("XZ").polyline([(x + sx * 45, 20), (x + sx * 150, 20), (x + sx * 45, 260)]).close() \
                .extrude(20, both=True)
            leg = leg.union(g)
        legs = leg if legs is None else legs.union(leg)
    body.add("legs", legs, "inst_blue")
    body.add("control cabinet", box(-L / 2 + 500, -150, z0 - 420, -L / 2 + 900, 150, z0 - 20), "inst_navy")
    body.add("cabinet screen", box(-L / 2 + 560, -152, z0 - 200, -L / 2 + 760, -150, z0 - 80), "screen_on")
    car = _piece(inst, "carriage")
    cl, cw = p["car_l"], p["car_w"]
    car.add("carriage plate", box(-cl / 2, -cw / 2, z1 + 15, cl / 2, cw / 2, top - p["car_t"] + 20), "inst_blue")
    car.add("bearing blocks", box(-cl / 2 + 30, -cw / 2 + 50, z1 + 5, cl / 2 - 30, cw / 2 - 50, z1 + 15), "steel")
    car.add("gearmotor", cyl(110, 170, x=0, y=-cw / 2 - 70, z=z1 - 140).union(
        box(-70, -cw / 2 - 130, z1 - 10, 70, -cw / 2, z1 + 20)), "inst_black")
    car.add("robot adapter", cyl(210, 20, z=top), "aluminium")
    inst.joints = {"carriage": Joint("slide", vec=(travel, 0, 0))}
    inst.actions = [
        ("The backup to the mobile base: a Vention seventh axis. The carriage carries the arm along the line on a "
         "rack and pinion.", 2.6, {"carriage": (0.0, 1.0)}),
        ("Its beam is set so the arm's base is at 800 mm, where it sits on the MiR250.", 2.2,
         {"carriage": (1.0, 0.0)}),
    ]
    inst.labels = [("carriage and gearmotor", (0, -cw / 2 - 70, z1 - 60), (0.16, 0.30)),
                   ("rack and guides", (L / 2 - 400, -bw / 2, z1), (0.82, 0.40)),
                   ("control cabinet", (-L / 2 + 700, -150, z0 - 220), (0.16, 0.72))]
    inst.cam = (0.55, -1.5, 0.6)
    return inst


# ===================================================================================================== polisher
# Buehler EcoMet 30 semi-automatic grinder-polisher, single 12 in (305 mm) platen: 500 L x 650 D x 650 H mm, 75 kg;
# 50-500 rpm; holds 25-40 mm mounts. It needs water, compressed air and a drain (EcoMet 30 manual), which a VLM tray
# does not supply: see the notes.
POLISHER = dict(W=500.0, D=650.0, H=650.0, base_h=300.0, platen_d=305.0, bowl_d=400.0, col_x=150.0, col_y=230.0,
                head_drop=40.0)


def polisher() -> Instrument:
    p = POLISHER
    inst = Instrument("polisher", "Metallographic grinder-polisher", "Buehler EcoMet 30 semi-automatic",
                      (p["W"], p["D"], p["H"]), "Buehler EcoMet 30 instruction manual (machine size, platen sizes, "
                      "weights); look from Buehler's photos")
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    pc = (0.0, -50.0)                         # platen centre
    body = _piece(inst, "body")
    base = box(-W / 2, yf, 0, W / 2, D / 2, p["base_h"]).edges("|Z").fillet(30)
    body.add("base", base, "inst_light")
    body.add("front panel", _wedge(W - 80, 40, 10, 120, x=0, y0=yf - 30, z=p["base_h"] - 160), "inst_dark")
    body.add("touchscreen", box(60, yf - 8, p["base_h"] - 130, 200, yf - 4, p["base_h"] - 60), "screen_on")
    bowl = cyl(p["bowl_d"], 90, x=pc[0], y=pc[1], z=p["base_h"]).cut(
        cyl(p["bowl_d"] - 24, 91, x=pc[0], y=pc[1], z=p["base_h"] + 8))
    body.add("splash bowl", bowl, "inst_black")
    body.add("drain", cyl(30, 40, x=-W / 2 + 60, y=yf + 60, z=p["base_h"] - 40), "inst_grey")
    # the power head: a column at the back right and an arm over the platen
    cx, cy = p["col_x"], p["col_y"]
    body.add("column", rbox(90, 90, H - p["base_h"] - 60, 10, x=cx, y=cy, z=p["base_h"]), "inst_dark")
    body.add("water arm", box(-W / 2 + 60, cy - 10, p["base_h"] + 150, -W / 2 + 75, cy + 10, p["base_h"] + 165).union(
        box(-W / 2 + 60, pc[1] - 20, p["base_h"] + 150, -W / 2 + 75, cy + 10, p["base_h"] + 165)).union(
        box(-W / 2 + 60, pc[1] - 25, p["base_h"] + 95, -W / 2 + 75, pc[1] - 10, p["base_h"] + 165)), "steel")
    head = _piece(inst, "head")
    hz = H - 140
    head.add("head", rbox(150, 330, 120, 20, x=cx - 10, y=cy - 130, z=hz), "inst_dark")
    head.add("head cap", rbox(130, 300, 20, 18, x=cx - 10, y=cy - 130, z=hz + 120), "inst_grey")
    head.add("spindle", cyl(36, 70, x=pc[0] + 70, y=pc[1] + 10, z=hz - 70), "chrome")
    holder = _piece(inst, "holder")
    hcx, hcy = pc[0] + 70, pc[1] + 10
    hz0 = p["base_h"] + 95 + p["head_drop"]
    holder.add("specimen holder", cyl(150, 18, x=hcx, y=hcy, z=hz0 + 22).cut(cyl(30, 20, x=hcx, y=hcy, z=hz0 + 21)),
               "steel")
    for i in range(3):
        a = math.radians(90 + 120 * i)
        holder.add(f"mount {i + 1}", cyl(30, 25, x=hcx + 45 * math.cos(a), y=hcy + 45 * math.sin(a), z=hz0), "mount")
    holder.add("mark", box(hcx + 55, hcy - 4, hz0 + 40, hcx + 74, hcy + 4, hz0 + 41), "inst_red")
    platen = _piece(inst, "platen")
    pz = p["base_h"] + 70
    platen.add("platen", cyl(p["platen_d"], 15, x=pc[0], y=pc[1], z=pz), "aluminium")
    platen.add("cloth", cyl(p["platen_d"] - 6, 3, x=pc[0], y=pc[1], z=pz + 15), "cloth")
    for i in range(4):
        a = i * 45.0
        bar = box(-p["platen_d"] / 2 + 10, -3, pz + 18, p["platen_d"] / 2 - 10, 3, pz + 18.6)
        platen.add(f"groove {i}", bar.rotate((0, 0, 0), (0, 0, 1), a).translate((pc[0], pc[1], 0)), "inst_grey")
    water = _piece(inst, "glow")
    water.add("water", cyl(6, 75, x=-W / 2 + 67, y=pc[1] - 17, z=pz + 20), "water")
    inst.joints = {
        "head": Joint("slide", vec=(0, 0, -p["head_drop"])),
        "holder": Joint("spin", parent="head", axis=(0, 0, 1), pivot=(hcx, hcy, 0), deg=-720.0),
        "platen": Joint("spin", axis=(0, 0, 1), pivot=(pc[0], pc[1], 0), deg=1800.0),
        "glow": Joint("fade"),
    }
    inst.actions = [
        ("Three mounted samples (30 mm) in the power head's holder, over a 12 in platen with a polishing cloth.",
         1.4, {"glow": (0.0, 0.0)}),
        ("The head lowers the holder onto the cloth; water on; platen and holder turn, 50-500 rpm.", 3.6,
         {"head": (0.0, 1.0), "platen": (0.0, 1.0), "holder": (0.0, 1.0), "glow": (0.0, 1.0)}),
        ("Done: the head lifts. It needs water, air and a drain, so on a tray it needs a recirculating unit.", 1.8,
         {"head": (1.0, 0.0), "glow": (1.0, 0.0)}),
    ]
    inst.labels = [("power head", (cx, cy - 130, hz + 120), (0.82, 0.25)), ("platen", (pc[0] - 140, pc[1], pz + 15),
                                                                            (0.14, 0.62))]
    inst.cam = (0.8, -1.7, 1.1)
    return inst


# ===================================================================================================== nanoindenter
# KLA iMicro nanoindenter (the iNano's enclosure, with a 1 N actuator for metals): a white cabinet with a lid hinged at
# the back on gas struts, a window in the lid, a patterned side panel and a status light along the front; inside, the
# indenter head and a microscope above a motorized XY stage (KLA product photos). Envelope: see SPECS.
NANO = dict(W=560.0, D=520.0, H=500.0, feet=25.0, lid_t=40.0, lid_deg=58.0, stage_z=150.0, head_x=-40.0,
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
    body.add("camera", cyl(46, 90, x=p["scope_x"], y=0, z=sz + 210), "inst_dark")
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
        "lid": Joint("hinge", axis=(1, 0, 0), pivot=(0, yb, hz), deg=p["lid_deg"]),
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
    return inst


# ===================================================================================================== laser diffraction
# Malvern Panalytical Mastersizer 3000 with the Aero S dry powder disperser, as for metal powders: the optical bench is
# 690 L x 300 W x 450 H mm, 30 kg; the Aero S docks into the bench's accessory slot, its hopper on top, and feeds the
# powder through a venturi across the laser; a vacuum extractor takes it away (Malvern's Mastersizer 3000 brochure,
# specifications; the look from Malvern's product photo: a silver bench with a curved top and an arch under it).
MS3000 = dict(L=690.0, W=300.0, H=450.0, slot_x0=-60.0, slot_x1=70.0, vac_w=330.0, vac_d=330.0, vac_h=480.0)


def mastersizer() -> Instrument:
    p = MS3000
    inst = Instrument("mastersizer", "Laser diffraction particle sizer", "Malvern Mastersizer 3000 + Aero S",
                      (p["L"] + 60 + p["vac_w"], p["W"] + 40, p["H"] + 90),
                      "Malvern Panalytical Mastersizer 3000 brochure (bench 690 x 300 x 450 mm, 30 kg; Aero S "
                      "dry disperser); look from Malvern's product photo")
    L, W, H = p["L"], p["W"], p["H"]
    x0b = -(L + 60 + p["vac_w"]) / 2            # the bench on the left, the vacuum extractor on the right
    xb = x0b + L / 2
    yf = -W / 2
    body = _piece(inst, "body")

    def bench_block(xa, xc, mat, name):
        prof = cq.Workplane("XZ").polyline([(xa, 0), (xc, 0), (xc, H - 60 + 60 * (xb + L / 2 - xc) / L),
                                            (xa, H - 60 + 60 * (xb + L / 2 - xa) / L)]).close().extrude(-W)
        prof = prof.translate((0, yf, 0))
        arch = _ycyl(560, 40, x=xb + 60, y=yf - 1, z=-215)
        body.add(name, prof.cut(arch), mat)

    bench_block(xb - L / 2, xb + p["slot_x0"], "inst_light", "bench left")
    bench_block(xb + p["slot_x1"], xb + L / 2, "inst_light", "bench right")
    body.add("bench feet", box(xb - L / 2 + 20, yf + 20, -0.1, xb - L / 2 + 70, -yf - 20, 1).union(
        box(xb + L / 2 - 70, yf + 20, -0.1, xb + L / 2 - 20, -yf - 20, 1)), "inst_black")
    body.add("logo", box(xb - L / 2 + 50, yf - 1, H - 120, xb - L / 2 + 110, yf, H - 70), "inst_navy")
    # the Aero S in the slot: its front with the status light and the knob, the hopper on top
    sx0, sx1 = xb + p["slot_x0"], xb + p["slot_x1"]
    body.add("Aero S", box(sx0 + 2, yf - 6, 40, sx1 - 2, -yf, H + 10), "inst_offwhite")
    body.add("Aero S light", _ycyl(10, 3, x=(sx0 + sx1) / 2 - 25, y=yf - 9, z=H - 40), "inst_green")
    body.add("Aero S knob", _ycyl(22, 18, x=(sx0 + sx1) / 2 + 10, y=yf - 24, z=H - 180), "inst_black")
    hx, hy = (sx0 + sx1) / 2, 10.0
    body.add("hopper", cyl(120, 70, x=hx, y=hy, z=H + 10).cut(cyl(100, 70, x=hx, y=hy, z=H + 20)), "steel")
    # the vacuum extractor and its hose
    vx = x0b + L + 60 + p["vac_w"] / 2
    body.add("vacuum extractor", rbox(p["vac_w"], p["vac_d"], p["vac_h"] - 60, 60, x=vx, z=60), "inst_grey")
    body.add("extractor head", rbox(p["vac_w"] - 20, p["vac_d"] - 20, 60, 50, x=vx, z=p["vac_h"] - 60), "inst_dark")
    body.add("extractor wheels", box(vx - p["vac_w"] / 2 + 30, -120, 0, vx - p["vac_w"] / 2 + 70, 120, 60).union(
        box(vx + p["vac_w"] / 2 - 70, -120, 0, vx + p["vac_w"] / 2 - 30, 120, 60)), "inst_black")
    from common import hose as _hose
    body.add("extract hose", _hose([(hx + 20, -yf - 10, 120), (hx + 20, -yf + 60, 120), (vx - 60, -yf + 60, 200),
                                     (vx - 60, 40, p["vac_h"] - 30)], 38), "inst_black")
    lid = _piece(inst, "lid")
    lid.add("hopper lid", cyl(124, 8, x=hx, y=hy, z=H + 80), "inst_dark")
    lid.add("lid knob", cyl(20, 14, x=hx, y=hy, z=H + 88), "inst_dark")
    vial = _piece(inst, "sample")
    vial.add("vial", cyl(28, 61, z=0).cut(cyl(25, 60, z=2)), "window")
    vial.add("powder", cyl(25, 30, z=2), "powder")
    beam = _piece(inst, "beam")
    beam.add("laser", _xcyl(3, L - 80, x=xb - L / 2 + 40, y=0, z=200), "laser")
    for i in range(14):
        beam.add(f"grain {i}", cq.Workplane("XY").sphere(2.2).translate((hx + 6 * math.sin(i * 1.7), hy - 4,
                                                                         H + 20 - i * 18)), "powder")
    inst.joints = {
        "lid": Joint("slide", vec=(0, 0, 90)),
        "sample": Joint("path", path=((hx - 260, -260, H - 40), (hx - 120, -120, H + 140), (hx, hy, H + 130),
                                      (hx, hy, H + 100))),
        "beam": Joint("fade"),
    }
    inst.actions = [
        ("The hopper's lid lifts; a vial of atomized powder (a few grams) is emptied into the Aero S.", 2.2,
         {"lid": (0.0, 1.0), "sample": (0.0, 1.0), "beam": (0.0, 0.0)}),
        ("Lid down. A vibrating tray feeds the powder through a venturi; compressed air disperses it across the "
         "laser (drawn see-through).", 2.6, {"sample": (1.0, 0.0), "lid": (1.0, 0.0), "beam": (0.0, 1.0),
                                             "~body": (0.0, 1.0)}),
        ("The scattering pattern gives the size distribution, 0.1 um to 3.5 mm, in under a minute; the vacuum "
         "extractor takes the powder away.", 2.0, {"beam": (1.0, 0.0), "~body": (1.0, 0.0)}),
    ]
    inst.labels = [("Aero S dry disperser", (hx, yf, H - 60), (0.40, 0.18)),
                   ("optical bench", (xb - L / 2 + 100, yf, 250), (0.12, 0.55)),
                   ("vacuum extractor", (vx, -p["vac_d"] / 2, 300), (0.86, 0.55))]
    inst.cam = (0.5, -1.7, 0.75)
    return inst


# ===================================================================================================== registry
def _registry() -> dict:
    names = ["xrd", "sem", "pip", "openflexure_v7", "openflexure_delta", "nanoindenter", "polisher", "furnace",
             "instron_small", "instron_floor", "mastersizer", "wire_edm", "glovebox", "rail"]
    g = globals()
    return {k: g[k] for k in names if k in g}


REGISTRY = _registry()

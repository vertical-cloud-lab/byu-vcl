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


# ===================================================================================================== registry
def _registry() -> dict:
    names = ["xrd", "sem", "pip", "openflexure_v7", "openflexure_delta", "nanoindenter", "polisher", "furnace",
             "instron_small", "instron_floor", "mastersizer", "wire_edm", "glovebox", "rail"]
    g = globals()
    return {k: g[k] for k in names if k in g}


REGISTRY = _registry()

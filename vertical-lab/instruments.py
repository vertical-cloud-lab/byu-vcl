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
from common import Model, box, cyl, hose, rbox, tube  # noqa: E402

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
    "rigaku_navy": (0.13, 0.12, 0.25, 1.0, 0.35),       # the MiniFlex's dark navy front
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
    "px_grey": (0.83, 0.84, 0.83, 1.0, 0.20),          # LECO's light grey (PX500), from the lab's SOP frames
    "sic_paper": (0.17, 0.19, 0.27, 1.0, 0.05),        # the dark SiC papers in the SOP
    "cloth_white": (0.96, 0.96, 0.95, 1.0, 0.05),      # the white final-polish cloth
    "mount_red": (0.46, 0.09, 0.11, 1.0, 0.35),        # the lab's maroon Bakelite mounts
    "led_blue": (0.40, 0.62, 1.00, 1.0, 0.10),         # the PX500's lit ring under the head
    "px_screen": (0.07, 0.13, 0.22, 1.0, 0.6),          # the PX500's dark navy screen
    "px_ui": (0.62, 0.86, 0.92, 1.0, 0.1),              # its light-cyan dial and setting rows
    "nat_screen": (0.86, 0.93, 0.97, 1.0, 0.3),        # the NAT controller's light touchscreen
    "alumina": (0.93, 0.93, 0.90, 0.85, 0.30),         # alumina suspension
}


# register.py's view of a model (see its docstring): key -> (the parameter dict the model is built from, a function of
# (params, pose) giving named points, circles and lines); FREE[key], the parameters it may fit to the reference frames
# in refs/<key>/; CHECKS[key](params), numbers that must stay >= 0 for the fitted model to make sense. Each
# instrument registers itself after its build function.
ANCHORS: dict = {}
FREE: dict = {}
CHECKS: dict = {}

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


def chain_params(s, x_fixed, x_end0, travel, straight, radius, z_low) -> tuple:
    """A link `s` mm along a horizontal energy chain from its fixed end at x_fixed: the chain lies in its lower run
    from there towards -x, bends up round radius `radius` and comes back along the upper run to its moving end, at
    x_end0 + travel * v. straight is the chain's length less its bend; z_low the lower run's centre line."""
    return (float(s), float(x_fixed), float(x_end0), float(travel), float(straight), float(radius), float(z_low))


def chain_pose(params, v: float) -> np.ndarray:
    """The 4x4 pose (link frame: x along the chain, z out of the bend) of a link at v. The bend sits where the two runs
    meet, (x_fixed + x_end - straight) / 2, so it moves at half the carriage's speed."""
    s, xf, xe0, travel, straight, r, z_low = params
    xe = xe0 + travel * v
    xl = (xf + xe - straight) / 2.0
    a = xf - xl                                          # the lower run
    if s <= a:
        x, z, ang = xf - s, z_low, 0.0
    elif s <= a + math.pi * r:
        phi = (s - a) / r
        x, z, ang = xl - r * math.sin(phi), z_low + r - r * math.cos(phi), phi
    else:
        x, z, ang = xl + (s - a - math.pi * r), z_low + 2 * r, math.pi
    return _T((x, 0.0, z)) @ _R((0, 1, 0), math.degrees(ang))


@dataclass
class Joint:
    """How a piece moves with a value v (0 = as modelled, 1 = the far end of its travel).

    slide: translate by v * vec.  hinge/spin: rotate v * deg about axis through pivot.  path: translate along the
    waypoints (offsets from the modelled position), evenly by arc length.  fade: only its opacity follows v.
    follow: a linkage driven by another piece's displacement d, which is v * vec or, given a path, the path's offset
    at v (as slide and path move that piece): the matrix is I + sum_k d[k] * jac[k], jac being three 3x4 matrices,
    the motion per mm of d along x, y and z. For small motions, such as flexure legs and levers (openflexure.py).
    chain: one link of an energy chain whose moving end rides a carriage (v as the carriage's slide), path =
    chain_params(...): the link lies in the lower run, rolls round the bend or rides the upper run (rail()).
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
        if self.kind == "chain":
            return chain_pose(self.path, v) @ np.linalg.inv(chain_pose(self.path, 0.0))
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
    anchors: dict = field(default_factory=dict)    # name -> point, ("circle", c, r) or ("line", p0, p1): register.py
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
# +-5 K above 800 C, and its lift-door LT version stands 755 mm tall with the door up. The look follows Nabertherm's
# own video of the NAT series ("Discover the NAT Series", youtu.be/WE6O8EccLyc, 0:16-0:22, the NAT 15/65 itself),
# measured with register.py (refs/furnace/): a stainless chamber unit on a separate controller unit with a wide
# touchscreen in the middle of its front; a slotted vent strip along the top front; the door a stainless panel with a
# thick insulating plug behind it, hinged on two brackets at the right, a vertical bar handle near its left edge and a
# latch knob on the left side; a small round fan guard in the back wall of the chamber.
FURNACE = dict(W=470.0, D=790.0, H=460.0, feet=12.0, lower_h=149.0, mouth_w=329.0, mouth_h=170.0, mouth_z0=226.0,
               mouth_x=-1.0, ch_w=300.0, ch_d=340.0, ch_h=150.0, panel_t=30.0, plug_t=60.0, fan_d=72.0,
               scr_w=228.0, scr_h=75.0, scr_z=74.0, vent_h=16.0)


def furnace_anchors(p, pose=None) -> dict:
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    y1 = yf + p["panel_t"]                                          # the chamber unit's front face, behind the door
    mx, mz0, mw, mh = p["mouth_x"], p["mouth_z0"], p["mouth_w"], p["mouth_h"]
    cz = mz0 + (mh - p["ch_h"]) / 2
    a = {"mouth tl": (mx - mw / 2, y1, mz0 + mh), "mouth tr": (mx + mw / 2, y1, mz0 + mh),
         "mouth bl": (mx - mw / 2, y1, mz0), "mouth br": (mx + mw / 2, y1, mz0),
         "top front left": (-W / 2, y1, H), "top front right": (W / 2, y1, H),
         "split left": (-W / 2, y1, p["lower_h"]),
         "fan": (mx, y1 + p["ch_d"], cz + p["ch_h"] / 2),
         "screen tl": (-p["scr_w"] / 2, yf + 8, p["scr_z"] + p["scr_h"] / 2),
         "screen tr": (p["scr_w"] / 2, yf + 8, p["scr_z"] + p["scr_h"] / 2),
         "screen bl": (-p["scr_w"] / 2, yf + 8, p["scr_z"] - p["scr_h"] / 2),
         "screen br": (p["scr_w"] / 2, yf + 8, p["scr_z"] - p["scr_h"] / 2),
         "foot left front": (-W / 2, yf + 6, 0.0)}
    return a


def furnace() -> Instrument:
    p = FURNACE
    inst = Instrument("furnace", "Heat treatment and ageing furnace", "Nabertherm NAT 15/65", (p["W"], p["D"], p["H"]),
                      "Nabertherm forced-convection chamber furnaces, tabletop (NAT 15/65: 470 x 790 x 460 mm, 60 kg, "
                      "650 C); the look from Nabertherm's NAT video, measured with register.py")
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    y1 = yf + p["panel_t"]
    lh, ft = p["lower_h"], p["feet"]
    mx, mz0, mw, mh = p["mouth_x"], p["mouth_z0"], p["mouth_w"], p["mouth_h"]
    cw, cd, chh = p["ch_w"], p["ch_d"], p["ch_h"]
    cz = mz0 + (mh - chh) / 2                                       # chamber floor
    body = _piece(inst, "body")
    body.add("feet", box(-W / 2 + 15, yf + 25, 0, -W / 2 + 55, D / 2 - 15, ft).union(
        box(W / 2 - 55, yf + 25, 0, W / 2 - 15, D / 2 - 15, ft)), "inst_black")
    # the controller unit: its own box, the wide touchscreen in the middle of its front, the switch at the right
    lower = box(-W / 2, yf + 4, ft, W / 2, D / 2, lh - 3).edges("|Y").fillet(6)
    body.add("controller unit", lower, "stainless")
    sw, sh, sz = p["scr_w"], p["scr_h"], p["scr_z"]                # the display's black glass; its light page on the right
    body.add("screen bezel", box(-sw / 2 - 8, yf + 1, sz - sh / 2 - 8, sw / 2 + 8, yf + 4, sz + sh / 2 + 8), "inst_grey")
    body.add("screen glass", box(-sw / 2, yf + 0.6, sz - sh / 2, sw / 2, yf + 1.2, sz + sh / 2), "inst_black")
    body.add("controller screen", box(-sw / 2 + 0.22 * sw, yf + 0.2, sz - sh / 2 + 4, sw / 2 - 4, yf + 0.7,
                                      sz + sh / 2 - 4), "nat_screen")
    body.add("power switch", box(W / 2 - 62, yf + 1, p["scr_z"] - 12, W / 2 - 38, yf + 4, p["scr_z"] + 12), "inst_black")
    body.add("warning label", box(W / 2 - 92, yf + 3.4, ft + 14, W / 2 - 40, yf + 4.2, ft + 30), "inst_yellow")
    # the chamber unit, with its mouth and the chamber behind it
    shell = box(-W / 2, y1, lh, W / 2, D / 2, H).edges("|Y").fillet(6)
    shell = shell.cut(box(mx - mw / 2, y1 - 1, mz0, mx + mw / 2, y1 + 25, mz0 + mh))
    shell = shell.cut(box(mx - cw / 2, y1 + 20, cz, mx + cw / 2, y1 + cd, cz + chh))
    body.add("chamber unit", shell, "stainless")
    body.add("split", box(-W / 2 + 2, y1 - 0.5, lh - 3, W / 2 - 2, D / 2 - 2, lh), "inst_dark")
    slots = None
    for i in range(5):                                              # the vent strip along the top front
        x0 = -W / 2 + 38 + i * (W - 76) / 5
        s = box(x0 + 6, y1 - 1.0, H - 12 - p["vent_h"] / 2, x0 + (W - 76) / 5 - 6, y1 + 0.5, H - 12 + p["vent_h"] / 2 - 8)
        slots = s if slots is None else slots.union(s)
    body.add("vent slots", slots, "inst_black")
    body.add("latch knob", _xcyl(16, 24, x=-W / 2 - 24, y=y1 + 40, z=mz0 + mh * 0.62).union(
        _xcyl(26, 8, x=-W / 2 - 30, y=y1 + 40, z=mz0 + mh * 0.62)), "chrome")
    for zh in (mz0 + 18, mz0 + mh - 18):                           # the door's two hinge brackets, on the right
        body.add(f"hinge {zh:.0f}", box(W / 2 - 6, yf - 6, zh - 22, W / 2 + 10, y1 + 30, zh + 22), "stainless")
    body.add("chamber floor", box(mx - cw / 2, y1 + 20, cz - 3, mx + cw / 2, y1 + cd, cz), "steel")
    fy = y1 + cd - 2
    guard = _ycyl(p["fan_d"], 3, x=mx, y=fy - 3, z=cz + chh / 2).cut(_ycyl(p["fan_d"] - 8, 5, x=mx, y=fy - 4,
                                                                              z=cz + chh / 2))
    for r in (0.62, 0.30):
        d = p["fan_d"] * r
        guard = guard.union(_ycyl(d, 3, x=mx, y=fy - 3, z=cz + chh / 2).cut(_ycyl(d - 6, 5, x=mx, y=fy - 4,
                                                                                   z=cz + chh / 2)))
    for ang in (0, 45, 90, 135):
        bar = box(-p["fan_d"] / 2 + 3, fy - 3, -1.5, p["fan_d"] / 2 - 3, fy, 1.5).rotate((0, 0, 0), (0, 1, 0), ang)
        guard = guard.union(bar.translate((mx, 0, cz + chh / 2)))
    body.add("fan guard", guard, "inst_dark")
    body.add("exhaust", cyl(40, 50, y=D / 2 - 90, z=H), "stainless")
    fan = _piece(inst, "fan")
    fz = cz + chh / 2
    for i in range(4):
        blade = box(-p["fan_d"] / 2 + 8, -2, -6, p["fan_d"] / 2 - 8, 2, 6).rotate((0, 0, 0), (0, 1, 0), i * 45.0)
        fan.add(f"blade {i}", blade.translate((mx, fy + 4, fz)), "steel")
    door = _piece(inst, "door")
    dz0, dz1 = lh + 6, H - 34                                       # under the vent strip
    door.add("door", box(-W / 2 + 6, yf, dz0, W / 2 - 6, y1, dz1).edges("|Y").fillet(6), "stainless")
    # the insulating plug: a step that fills the mouth, then one that goes into the chamber (white fibre in the video)
    door.add("door plug", box(mx - mw / 2 + 6, y1, mz0 + 6, mx + mw / 2 - 6, y1 + 22, mz0 + mh - 6).union(
        box(mx - cw / 2 + 6, y1 + 22, cz + 5, mx + cw / 2 - 6, y1 + p["plug_t"], cz + chh - 5)), "refractory")
    hx = -W / 2 + 52
    door.add("door handle", _ycyl(14, 26, x=hx, y=yf - 26, z=fz - 60).union(_ycyl(14, 26, x=hx, y=yf - 26, z=fz + 60))
             .union(cyl(16, 150, x=hx, y=yf - 26, z=fz - 75)), "chrome")
    door.add("door badge", box(W / 2 - 150, yf - 1, dz1 - 50, W / 2 - 50, yf, dz1 - 30), "inst_yellow")
    load = _piece(inst, "load")
    load.add("tray", box(-110, -80, 0, 110, 80, 8).cut(box(-104, -74, 3, 104, 74, 9)), "stainless")
    for i, x in enumerate((-60, 0, 60)):
        load.add(f"coupon {i + 1}", box(x - 8, -60, 3, x + 8, 60, 7), "sample")
    chamber_c = (mx, y1 + 20 + (cd - 20) / 2, cz)
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(W / 2 + 2, yf, 0), deg=100.0),   # free edge out to the front
        # the tray waits to the left, outside the door's swing (a 466 mm radius about the hinge)
        "load": Joint("path", path=((-330, yf - 330, cz + 80), (mx, yf - 60, cz + 10), chamber_c)),
        "fan": Joint("spin", axis=(0, 1, 0), pivot=(mx, fy, fz), deg=1440.0),
    }
    inst.actions = [
        ("The door swings open on its two right-hand hinges; its insulating plug comes out of the chamber's mouth.",
         1.6, {"door": (0.0, 1.0), "load": (0.0, 0.0)}),
        ("A tray of printed tensile coupons goes in.", 1.8, {"load": (0.0, 1.0)}),
        ("Door shut. Solution treatment at about 530 C, quench, then ageing at 160-200 C: the circulation fan holds "
         "+-5 C, so one furnace does both.", 3.0, {"door": (1.0, 0.0), "fan": (0.0, 1.0), "~door": (0.0, 0.7)}),
        ("", 0.8, {"~door": (0.7, 0.0)}),
    ]
    inst.labels = [("swing door", (W / 2 - 40, yf - 2, dz1 - 40), (0.80, 0.18)),     # near the hinge: stays on it
                   ("controller", (p["scr_w"] / 2, yf, p["scr_z"]), (0.84, 0.72))]
    inst.anchors = furnace_anchors(p)
    inst.cam = (0.9, -1.7, 0.8)
    inst.framing = (0.95, 0.40)              # room on the left for the tray waiting outside the door's swing
    return inst


ANCHORS["furnace"] = (FURNACE, furnace_anchors)
FREE["furnace"] = ["lower_h", "mouth_w", "mouth_h", "mouth_z0", "mouth_x", "scr_w", "scr_h", "scr_z"]
CHECKS["furnace"] = lambda p: [p["mouth_z0"] - p["lower_h"] - 30, p["H"] - p["mouth_z0"] - p["mouth_h"] - 50,
                               p["mouth_w"] - p["ch_w"], p["mouth_h"] - p["ch_h"], p["lower_h"] - p["scr_z"] -
                               p["scr_h"] / 2 - 20]


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
# Rigaku MiniFlex, 6th generation ("MiniFlex 6G", sold since 2023 and so what a lab buying one now gets; the MiniFlex
# 600 it replaced was the 5th): 620 W x 722 H x 460 D mm, ~80 kg; a vertical goniometer of 150 mm radius, theta-2theta;
# a 600 W tube (Rigaku's MiniFlex 6G sheet; its brochure's outline drawing gives 456 mm deep, used here). The front's
# proportions are fitted with register.py (refs/xrd/) to frames of Rigaku's own 6G launch video (8tI9uFKevr0): a
# light-grey body split at the button strip into a base and an upper housing, with rounded vertical edges; a dark navy
# front of three parts, the "Rigaku" band at the top, the door (a vertical handle at its left, hinged on its right,
# "MiniFlex" low on it) and the button strip under it (radiation label, DOOR LOCK, a lamp, the HV key, power off and
# on, the e-stop); a bulge on each side of the upper housing; the orange X-ray lamp at the top of the front, over the
# Rigaku band; vents low on the sides. The top is flat: neither 6G view shows the raised cover this model used to
# have, and without one the published 722 mm and 620 mm agree with the frames. Inside (that video, and the MiniFlex
# 600's, which the 6G kept): the tube's white housing with a green lamp on the left, the goniometer in the middle, the
# navy D/teX detector on the 2theta arm on the right; the door's inside is light grey.
XRD = dict(W=620.0, D=456.0, H=722.0, body_w=560.2, body_d=395.0, feet=23.0, seam_z=305.3, strip_z0=210.4,
           door_top=628.2, panel_top=707.6, panel_x=199.6, bulge_z0=353.5, bulge_z1=554.7, bulge_y0=92.0,
           bulge_y1=216.0, estop_x=153.0, estop_z=254.8, handle_x=-179.4, handle_z0=368.4, handle_z1=467.4,
           door_t=30.0, door_deg=100.0, gonio_r=150.0, gonio_z=450.0)
FOOT_IN = 60.0                  # the feet's centres, in from the body's sides and front (the product shot)
STRIP_BUTTONS = ((-0.75, 34, "inst_yellow", "DOOR LOCK"), (-0.48, 20, "inst_white", "lamp"),
                 (-0.21, 24, "chrome", "HV key"), (0.08, 32, "inst_offwhite", "power off"),
                 (0.35, 32, "inst_green", "power on"))   # (x / panel_x, diameter, material, name), left to right


def _miniflex(p) -> dict:
    """The positions the model and its anchors share."""
    bw, bd = p["body_w"], p["body_d"]
    yf, yb = -bd / 2, bd / 2
    return dict(bw=bw, bd=bd, yf=yf, yb=yb, gy=yf + p["door_t"] + 150.0, gz=p["gonio_z"],
                hinge=(p["panel_x"], yf - 3.0))           # the door's right front edge


def _door_pt(p, pt, v) -> tuple:
    """A point on the door, swung open by v (0 shut, 1 open) about its right-hand hinge."""
    hx, hy = _miniflex(p)["hinge"]
    t = math.radians(p["door_deg"] * v)
    x, y = pt[0] - hx, pt[1] - hy
    return (hx + x * math.cos(t) - y * math.sin(t), hy + x * math.sin(t) + y * math.cos(t), pt[2])


def xrd_anchors(p, pose=None) -> dict:
    """Named points of the model, for register.py; the handle follows pose["door"] (0 shut, 1 open)."""
    g = _miniflex(p)
    bw, yf, H, px, W = g["bw"], g["yf"], p["H"], p["panel_x"], p["W"]
    xb = (bw + W) / 4                                          # the bulges' mid-thickness
    v = float((pose or {}).get("door", 0.0))
    a = {"front top left": (-bw / 2, yf, H), "front top right": (bw / 2, yf, H),
         "front bottom left": (-bw / 2, yf, p["feet"]), "front bottom right": (bw / 2, yf, p["feet"]),
         "seam left": (-bw / 2, yf, p["seam_z"]), "seam right": (bw / 2, yf, p["seam_z"]),
         "panel tl": (-px, yf, p["panel_top"]), "panel tr": (px, yf, p["panel_top"]),
         "band bl": (-px, yf, p["door_top"]), "band br": (px, yf, p["door_top"]),
         "strip tl": (-px, yf, p["seam_z"]), "strip tr": (px, yf, p["seam_z"]),
         "strip bl": (-px, yf, p["strip_z0"]), "strip br": (px, yf, p["strip_z0"]),
         "estop": (p["estop_x"], yf - 28.0, p["estop_z"]), "lamp": (0.0, yf, H - 7.0),
         "foot left": (-(bw / 2 - FOOT_IN), yf + FOOT_IN, 0.0), "foot right": (bw / 2 - FOOT_IN, yf + FOOT_IN, 0.0),
         "bulge left top": (-xb, yf + p["bulge_y0"], p["bulge_z1"]),
         "bulge left bottom": (-xb, yf + p["bulge_y0"], p["bulge_z0"]),
         "bulge right top": (xb, yf + p["bulge_y0"], p["bulge_z1"]),
         "bulge right bottom": (xb, yf + p["bulge_y0"], p["bulge_z0"]),
         "handle top": _door_pt(p, (p["handle_x"], yf - 26.0, p["handle_z1"]), v),
         "handle bottom": _door_pt(p, (p["handle_x"], yf - 26.0, p["handle_z0"]), v)}
    return a


def xrd() -> Instrument:
    p = XRD
    g = _miniflex(p)
    inst = Instrument("xrd", "Benchtop X-ray diffractometer", "Rigaku MiniFlex (6th generation)",
                      (p["W"], p["D"], p["H"]),
                      "Rigaku MiniFlex 6G sheet and brochure (620 W x 456 D x 722 H mm, 80 kg; 150 mm vertical "
                      "goniometer, theta-2theta, 600 W); the front fitted with register.py to Rigaku's 6G launch video")
    bw, bd, yf, yb, gy, gz = g["bw"], g["bd"], g["yf"], g["yb"], g["gy"], g["gz"]
    H, px, seam, W = p["H"], p["panel_x"], p["seam_z"], p["W"]
    body = _piece(inst, "body")
    feet = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            f = cyl(40, p["feet"], x=sx * (bw / 2 - FOOT_IN), y=-sy * (bd / 2 - FOOT_IN))
            feet = f if feet is None else feet.union(f)
    body.add("feet", feet, "inst_black")
    body.add("base", box(-bw / 2, yf, p["feet"], bw / 2, yb, seam).edges("|Z").fillet(12), "inst_white")
    # the button strip: the bottom of the navy front, on the base, its lower corners rounded
    body.add("button strip", box(-px, yf - 3, p["strip_z0"], px, yf + 1, seam - 1).edges("|Y").edges("<Z")
             .fillet(14), "rigaku_navy")
    sz = p["estop_z"]
    for k, (fx, d, mat, nm) in enumerate(STRIP_BUTTONS):
        body.add(nm, _ycyl(d, 8, x=fx * px, y=yf - 11, z=sz), mat)
    body.add("HV key bow", box(-0.21 * px - 4, yf - 14, sz - 46, -0.21 * px + 4, yf - 10, sz - 12), "chrome")
    body.add("radiation label", box(-0.93 * px - 14, yf - 4, sz - 25, -0.93 * px + 14, yf - 3, sz + 25),
             "inst_yellow")
    ex = p["estop_x"]
    body.add("e-stop collar", _ycyl(62, 10, x=ex, y=yf - 11, z=sz), "inst_yellow")
    body.add("emergency stop", _ycyl(50, 30, x=ex, y=yf - 28, z=sz), "inst_red")      # a mushroom, well proud
    # vents low on both sides of the base, near the front
    for sx in (-1, 1):
        for i in range(9):
            y = yf + 50 + 12 * i
            body.add(f"vent {'LR'[sx > 0]}{i + 1}", box(sx * bw / 2 - 1.5, y, 60, sx * bw / 2 + 1.5, y + 5, 230),
                     "inst_grey")
    body.add("rear fittings", box(-120, yb, 80, 120, yb + 30, 200), "inst_grey")
    # the upper housing: the door's recess and the opening behind it, the chamber; the Rigaku band over the door
    hood = _piece(inst, "hood")
    dt = p["door_t"]
    upper = box(-bw / 2, yf, seam, bw / 2, yb, H).edges("|Z").fillet(12)
    upper = upper.cut(box(-px, yf - 1, seam, px, yf + dt, p["door_top"]))
    upper = upper.cut(box(-px + 25, yf + dt - 1, seam + 40, px - 30, yf + dt + 16, p["door_top"] - 20))
    cx0, cz1 = bw / 2 - 25, H - 20                               # the chamber: wider and taller than the opening
    upper = upper.cut(box(-cx0, yf + dt + 15, seam + 6, cx0, yb - 30, cz1))
    hood.add("upper housing", upper, "inst_white")
    hood.add("Rigaku band", box(-px, yf - 3, p["door_top"], px, yf + 1, p["panel_top"]), "rigaku_navy")
    lz = p["door_top"] + 0.54 * (p["panel_top"] - p["door_top"])
    hood.add("Rigaku logo", box(-96, yf - 4, lz - 16, 96, yf - 3, lz + 16), "inst_light")
    hood.add("X-ray lamp", box(-28, yf - 2, H - 12, 28, yf + 14, H - 1), "inst_orange")
    lit = _piece(inst, "glow")                                   # the lamp lit while the X-rays are on
    lit.add("X-ray lamp lit", box(-29, yf - 3, H - 13, 29, yf + 15, H), "glow")
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (bw / 2 - 5), sx * W / 2))
        w = box(x0, yf + p["bulge_y0"], p["bulge_z0"], x1, yf + p["bulge_y1"], p["bulge_z1"])
        hood.add(f"side bulge {'LR'[sx > 0]}", w.edges("|Y").fillet(9), "inst_white")
    # inside: the goniometer's back plate, the tube's housing on the left, the stage and the detector arm
    inner = _piece(inst, "chamber")
    inner.add("chamber lining", box(-cx0, yb - 34, seam + 6, cx0, yb - 30, cz1).union(
        box(-cx0, yf + dt + 15, seam + 6, cx0, yb - 30, seam + 10)), "inst_dark")
    inner.add("goniometer", _ycyl(250, 12, y=yb - 46, z=gz), "inst_grey")
    # the hub is behind the sample (it used to ring the stage, in the beam's way); the stage turns on a theta shaft
    inner.add("goniometer hub", _ycyl(70, yb - 46 - (gy + 60), y=gy + 60, z=gz), "aluminium")
    tube_x0 = -p["gonio_r"]
    inner.add("X-ray tube housing", box(tube_x0 - 105, gy - 45, gz - 55, tube_x0 + 10, gy + 45, gz + 50), "inst_white")
    inner.add("shutter lamp", box(tube_x0 - 60, gy - 47, gz - 30, tube_x0 - 30, gy - 45, gz - 20), "inst_green")
    inner.add("tube label", box(tube_x0 - 20, gy - 47, gz + 5, tube_x0 + 2, gy - 45, gz + 30), "inst_yellow")
    inner.add("tube window", _xcyl(30, 30, x=tube_x0 + 10, y=gy, z=gz), "steel")
    inner.add("divergence slit", box(tube_x0 + 40, gy - 18, gz - 18, tube_x0 + 46, gy + 18, gz + 18), "brass")
    stage = _piece(inst, "stage")
    stage.add("sample stage", box(-35, gy - 30, gz - 16, 35, gy + 30, gz - 3), "aluminium")
    stage.add("theta shaft", _ycyl(24, 30, y=gy + 30, z=gz), "steel")
    holder = _piece(inst, "holder")
    holder.add("sample holder", box(-22, -26, 0, 22, 26, 2.5), "window")
    holder.add("powder", box(-10, -10, 2.5, 10, 10, 3.0), "powder")
    det = _piece(inst, "detector")
    r = p["gonio_r"]
    # the D/teX head (navy, as Rigaku's) at the 150 mm circle on its 2theta arm, which turns about the axis behind the
    # beam plane
    d_shape = box(r - 10, gy - 30, -28, r + 60, gy + 31, 28).union(_xcyl(36, 30, x=r - 40, y=gy, z=0)).union(
        box(14, gy + 31, -12, r + 20, gy + 45, 12))
    d_shape = d_shape.rotate((0, gy, 0), (0, gy + 1, 0), -10.0).translate((0, 0, gz))    # 2theta = 10 deg
    det.add("D/teX detector", d_shape, "rigaku_navy")
    # the door: light grey, its outside navy; the handle at its left, "MiniFlex" low on it
    door = _piece(inst, "door")
    dz0, dz1 = seam + 1, p["door_top"] - 1
    door.add("door", box(-px + 1, yf - 1, dz0, px - 1, yf + dt - 2, dz1), "inst_light")
    door.add("door front", box(-px + 1, yf - 3, dz0, px - 1, yf - 1, dz1), "rigaku_navy")
    door.add("MiniFlex label", box(-58, yf - 4, seam + 14, 58, yf - 3, seam + 34), "inst_light")   # centred, low
    hx, hz0, hz1 = p["handle_x"], p["handle_z0"], p["handle_z1"]
    door.add("door handle", box(hx - 5, yf - 29, hz0, hx + 5, yf - 23, hz1).union(
        box(hx - 5, yf - 29, hz0, hx + 5, yf - 3, hz0 + 10)).union(box(hx - 5, yf - 29, hz1 - 10, hx + 5, yf - 3, hz1)),
        "chrome")
    inst.joints = {
        "door": Joint("hinge", axis=(0, 0, 1), pivot=(g["hinge"][0], g["hinge"][1], 0), deg=p["door_deg"]),
        "stage": Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-40.0),
        # it waits clear of the door's swing and comes in through the doorway by hand, at the goniometer's height
        "holder": Joint("path", parent="stage", path=((-200, -520, gz + 60), (0, yf - 40, gz + 40),
                                                      (0, gy - 60, gz - 3 + 40), (0, gy, gz - 3))),
        "detector": Joint("hinge", axis=(0, 1, 0), pivot=(0, gy, gz), deg=-80.0),
        "glow": Joint("fade"),
    }
    inst.actions = [
        ("DOOR LOCK pressed, the door swings open on its right-hand hinge, past square, showing the 150 mm vertical "
         "goniometer.", 1.6, {"door": (0.0, 1.0), "holder": (0.0, 0.0)}),
        ("A powder sample on its holder goes in by hand onto the stage at the goniometer's centre.", 2.0,
         {"holder": (0.0, 1.0)}),
        ("Door closed and locked: the X-ray interlock lets the 600 W tube switch on; the lamp on top lights.", 1.4,
         {"door": (1.0, 0.0), "glow": (0.0, 1.0)}),
        ("Scan, drawn see-through: the tube stays put, the sample tilts by theta and the detector sweeps 2theta "
         "from 10 to 90 degrees.", 3.2, {"~hood": (0.0, 1.0), "~door": (0.0, 1.0), "stage": (0.0, 1.0),
                                         "detector": (0.0, 1.0)}),
        ("X-rays off, the detector parks and the door opens again.", 1.8,
         {"stage": (1.0, 0.0), "detector": (1.0, 0.0), "~hood": (1.0, 0.0), "~door": (1.0, 0.0),
          "door": (0.0, 1.0), "glow": (1.0, 0.0)}),
        ("The sample comes out.", 1.4, {"holder": (1.0, 0.0)}),
        ("Door shut. At 722 mm tall the MiniFlex just fits a tray: Kardex allows 727.5 mm.", 1.4,
         {"door": (1.0, 0.0)}),
    ]
    inst.labels = [("X-ray tube", (tube_x0 - 50, gy, gz + 50), (0.12, 0.30)),
                   ("detector", (150, gy, gz + 60), (0.84, 0.30)),
                   ("front door", (hx, yf - 30, hz1), (0.14, 0.62))]
    inst.anchors = xrd_anchors(p)
    inst.cam = (0.75, -1.8, 0.7)
    return inst


# register.py: the MiniFlex's anchors, the front's proportions fitted to the 6G frames (refs/xrd/), and what keeps a
# fitted model buildable: the panel inside the body, the band, door and strip in order from the top, the e-stop on the
# strip, the handle on the door.
ANCHORS["xrd"] = (XRD, xrd_anchors)
FREE["xrd"] = ["body_w", "panel_x", "panel_top", "door_top", "seam_z", "strip_z0", "bulge_z0", "bulge_z1", "estop_x",
               "estop_z", "handle_x", "handle_z0", "handle_z1"]
CHECKS["xrd"] = lambda p: [p["body_w"] / 2 - p["panel_x"] - 15, p["H"] - p["panel_top"] - 8,
                           p["panel_top"] - p["door_top"] - 40, p["door_top"] - p["seam_z"] - 200,
                           p["seam_z"] - p["strip_z0"] - 50, p["strip_z0"] - p["feet"] - 80,
                           p["bulge_z1"] - p["bulge_z0"] - 80, p["estop_z"] - p["strip_z0"] - 25,
                           p["seam_z"] - p["estop_z"] - 25, p["panel_x"] - p["estop_x"] - 25,
                           p["handle_z1"] - p["handle_z0"] - 50, p["handle_x"] + p["panel_x"] - 10,
                           p["handle_z0"] - p["seam_z"] - 20, p["door_top"] - p["handle_z1"] - 20,
                           p["door_top"] - 60 - p["gonio_z"], p["gonio_z"] - p["seam_z"] - 80]


# ===================================================================================================== SEM
# Hitachi TM4000PlusII tabletop SEM: main unit 330 W x 614 D x 547 H mm, 54 kg (Hitachi High-Tech). The proportions
# are fitted with register.py (refs/sem/) to Hitachi's product shot of the TM4000II / TM4000PlusII (the opening of
# its own launch video) and to the Canadian Centre for Electron Microscopy's TM4000Plus videos, whose body is the same.
# Look, from those: a white body whose top front edge rolls over in a large radius, with a raised strip along the
# middle of the top that ramps down at its front end; the top cover's seam sweeps down each side from the back of the
# top to the front; two vent grilles on the left side. The front is a dark navy panel set into a white frame: a lit
# strip between "EVAC" and "AIR" along its top, "TM4000Plus", the II badge, an icon and HITACHI, and the round
# EVAC/AIR button at the right. Below it the sample chamber's door, a navy block standing a little proud of the frame
# with a black bar handle on two posts near its top. The door is a drawer: pulled straight out by the handle once
# AIR has vented the chamber, it brings the motorized X-Y stage out on its inside face, and the sample, on a
# cylindrical holder whose height is set on a gauge at the bench, drops into the socket in the middle of the stage
# (CCEM, "Loading the specimen"; Microscopy Australia's workflow video). EDS and EBSD detectors mount on the chamber's
# sides; their electronics stand beside it, the diaphragm pump behind.
SEM = dict(W=330.0, D=614.0, H=547.0, feet=12.0, front_z0=30.0, drawer_top=236.0, blue_top=417.0, draw=170.0,
           frame_w=35.0, recess=20.0, proud=6.0, nose_r=80.0, cap_z=400.0, hump_w=151.0, hump_h=31.0, hump_y0=59.0,
           hump_run=15.0, hump_len=200.0, door_w=201.0, btn_x=107.0, btn_z=277.0, badge_z=320.0, handle_z=212.0,
           handle_w=149.0)


def _tm4000(p) -> dict:
    """The positions the model and its anchors share."""
    W, D, H = p["W"], p["D"], p["H"]
    yf = -D / 2
    xb = W / 2 - p["frame_w"]                      # the navy recess's sides
    Ht, r, y0 = H - p["hump_h"], p["nose_r"], p["hump_y0"]
    return dict(W=W, D=D, H=H, yf=yf, yb=D / 2, Ht=Ht, xb=xb, xd=p["door_w"] / 2, yp=yf + p["recess"],
                ydf=yf - p["proud"], ys=yf + 130.0,                                        # ys: the stage's socket
                zh=Ht - r + math.sqrt(max(r * r - (r - y0) ** 2, 0.0)))   # the rolled edge's top where the wedge stands


def sem_anchors(p, pose=None) -> dict:
    """Named points and lines of the model, for register.py; the door follows pose["drawer"] (0 in, 1 out)."""
    g = _tm4000(p)
    W, H, yf, yb, Ht, xb, xd = g["W"], g["H"], g["yf"], g["yb"], g["Ht"], g["xb"], g["xd"]
    yd = g["ydf"] - p["draw"] * float((pose or {}).get("drawer", 0.0))
    z0, hx, hy, hw = p["feet"], p["handle_w"] / 2, yf + p["hump_y0"], p["hump_w"] / 2
    a = {"blue tl": (-xb, yf, p["blue_top"]), "blue tr": (xb, yf, p["blue_top"]),
         "button": (p["btn_x"], g["yp"] - 4, p["btn_z"]), "badge": (0.0, g["yp"], p["badge_z"]),
         "drawer tl": (-xd, yd, p["drawer_top"]), "drawer tr": (xd, yd, p["drawer_top"]),
         "drawer bl": (-xd, yd, p["front_z0"]), "drawer br": (xd, yd, p["front_z0"]),
         "handle l": (-hx, yd - 26, p["handle_z"]), "handle r": (hx, yd - 26, p["handle_z"]),
         "wedge tl": (-hw, hy + p["hump_run"], H), "wedge tr": (hw, hy + p["hump_run"], H),
         "wedge bl": (-hw, hy, g["zh"]), "wedge br": (hw, hy, g["zh"])}
    for s, nm in ((-1, "left"), (1, "right")):
        x = s * W / 2
        a.update({f"front {nm} bottom": (x, yf, z0), f"back {nm} bottom": (x, yb, z0), f"back {nm} top": (x, yb, Ht),
                  f"front {nm} edge": ("line", (x, yf, z0 + 30), (x, yf, Ht - p["nose_r"])),
                  f"back {nm} edge": ("line", (x, yb, z0 + 30), (x, yb, Ht - 15)),
                  f"{nm} bottom": ("line", (x, yf + 30, z0), (x, yb - 30, z0))})
    return a


def sem() -> Instrument:
    p = SEM
    g = _tm4000(p)
    W, D, H, yf, yb, Ht, xb, xd, yp, ydf, ys = (g[k] for k in ("W", "D", "H", "yf", "yb", "Ht", "xb", "xd", "yp",
                                                                "ydf", "ys"))
    inst = Instrument("sem", "Tabletop SEM with EDS and EBSD", "Hitachi TM4000PlusII", (W, D, H),
                      "Hitachi High-Tech TM4000PlusII specifications (main unit 330 W x 614 D x 547 H mm, 54 kg; "
                      "pump 144 x 270 x 216 mm); Hitachi's EDS brochure (AZtecOne analyser 290 x 260 x 330 mm); "
                      "proportions fitted with register.py to Hitachi's TM4000II/PlusII product shot and CCEM's "
                      "TM4000Plus videos; the 17 cm drawer travel from ac-dev-lab #132's TM4000II model")
    z0, fz, dt, bt = p["feet"], p["front_z0"], p["drawer_top"], p["blue_top"]
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"foot {sx}{sy}", cyl(36, z0, x=sx * (W / 2 - 35), y=sy * (D / 2 - 45)), "inst_light")
    # the shell: its top front edge rolls over in a large radius; the navy recess, and the chamber behind the door
    shell = box(-W / 2, yf, z0, W / 2, yb, Ht).edges("<Y and >Z").fillet(p["nose_r"])
    try:
        shell = shell.edges("|Z").fillet(10)
    except Exception:                              # noqa: BLE001 - square side edges if the kernel refuses
        pass
    recess = box(-xb, yf - 1, fz, xb, yp, bt).edges("|Y").fillet(8)
    chamber = box(-xd + 4, yp - 1, fz + 6, xd - 4, yf + 270, dt - 6)
    shell = shell.cut(recess).cut(chamber)
    # the top cover: its seam sweeps down each side from the back of the top to the front, below the recess's top
    seam = [(yf + 0.30 * D, p["cap_z"] + 30), (yf + 0.62 * D, Ht - 45), (yb + 2, Ht - 22)]
    above = (cq.Workplane("YZ").moveTo(yf - 2, p["cap_z"]).spline(seam, includeCurrent=True)
             .lineTo(yb + 2, H + 5).lineTo(yf - 2, H + 5).close().extrude(W + 4).translate((-W / 2 - 2, 0, 0)))
    body.add("body", shell.cut(above), "inst_offwhite")
    body.add("top cover", shell.intersect(above), "inst_white")
    # a wedge on the top's front: its face stands on the rolled edge, and it tapers back into the top
    hy0, hy1 = yf + p["hump_y0"], yf + p["hump_y0"] + p["hump_run"]
    body.add("top wedge", cq.Workplane("YZ").polyline([(hy0, g["zh"] - 30), (hy0, g["zh"]), (hy1, H),
                                                      (hy1 + p["hump_len"], Ht), (hy1 + p["hump_len"], Ht - 30)])
             .close().extrude(p["hump_w"]).translate((-p["hump_w"] / 2, 0, 0)), "inst_white")
    for i, vy in enumerate((-30.0, 60.0)):         # the vent grilles on the left side
        for k in range(6):
            body.add(f"vent {i} {k}", box(-W / 2 - 1.5, vy - 22, 330 + 12 * k, -W / 2 + 1, vy + 22, 335 + 12 * k),
                     "inst_dark")
    # the front: a navy panel set into the white frame, lined in navy, its lit strip, lettering, badges and button
    navy = "inst_navy"
    body.add("recess lining", box(-xb, yf + 0.5, fz, xb, yp, bt).edges("|Y").fillet(8)
             .cut(box(-xb + 2.5, yf, fz + 2.5, xb - 2.5, yp + 1, bt - 2.5)), navy)
    body.add("front panel", box(-xb + 1, yp - 0.5, dt - 4, xb - 1, yp + 6, bt - 1), navy)
    body.add("door surround", box(-xb + 1, yp - 0.5, fz, xb - 1, yp + 2, dt - 4).cut(
        box(-xd + 4, yp - 1, fz + 6, xd - 4, yp + 3, dt - 6)), "inst_black")
    body.add("EVAC-AIR strip", box(-75, yp - 1.5, bt - 30, 75, yp - 0.4, bt - 24), "led_blue")
    body.add("model name", box(-58, yp - 1.2, bt - 62, 58, yp - 0.4, bt - 48), "inst_light")
    body.add("II badge", box(-9, yp - 1.6, p["badge_z"] - 9, 9, yp - 0.4, p["badge_z"] + 9), "inst_light")
    body.add("icon badge", box(-16, yp - 1.6, p["badge_z"] - 44, 16, yp - 0.4, p["badge_z"] - 20), "inst_light")
    body.add("HITACHI", box(-45, yp - 1.2, dt + 14, 45, yp - 0.4, dt + 24), "inst_light")
    body.add("EVAC/AIR ring", _ycyl(30, 3, x=p["btn_x"], y=yp - 3, z=p["btn_z"]), "inst_light")
    body.add("EVAC/AIR button", _ycyl(22, 3, x=p["btn_x"], y=yp - 5, z=p["btn_z"]), "chrome")
    body.add("chamber", chamber.cut(box(-xd + 6, yp - 2, fz + 9, xd - 6, yf + 266, dt - 9)), "inst_dark")
    # EDS: the detector is built in (Hitachi); only Oxford's AZtecOne analyser box stands beside. EBSD: Hitachi lists
    # no EBSD option for the TM4000 series; drawn here is Bruker's e-Flash XS (sold for tabletop SEMs, 48 x 84 mm
    # outside the chamber) on a side port level with the stage, with a 70 degree pre-tilted stub holder. A proposal,
    # not a documented mount.
    cz = 150.0
    body.add("EDS analyser", rbox(260, 290, 330, 12, x=W / 2 + 190, y=-90, z=0), "inst_white")
    body.add("EDS analyser front", box(W / 2 + 70, -236, 40, W / 2 + 310, -235, 300), navy)
    body.add("EDS analyser light", _ycyl(14, 3, x=W / 2 + 190, y=-237, z=250), "inst_orange")
    body.add("EBSD port", _xcyl(70, 20, x=-W / 2 - 20, y=ys, z=cz), "inst_light")
    body.add("EBSD detector", _xcyl(48, 84, x=-W / 2 - 104, y=ys, z=cz), "inst_dark")
    body.add("EBSD camera", _xcyl(56, 40, x=-W / 2 - 144, y=ys, z=cz), "inst_black")
    body.add("pump", rbox(144, 270, 216, 10, x=-W / 2 - 110, y=D / 2 - 160, z=0), "inst_white")
    body.add("pump hose", cyl(22, 30, x=-W / 2 - 110, y=D / 2 - 160, z=216), "inst_black")
    # the door: a navy block a little proud of the frame, its bar handle near the top, the stage on its inside face
    drawer = _piece(inst, "drawer")
    drawer.add("door", box(-xd, ydf, fz + 3, xd, yp + 16, dt - 2).edges("<Y").fillet(5), navy)
    hx = p["handle_w"] / 2
    drawer.add("handle", box(-hx, ydf - 30, p["handle_z"] - 8, hx, ydf - 18, p["handle_z"] + 8).edges("|Y")
               .fillet(5), "inst_black")
    for s in (-1, 1):
        drawer.add(f"handle post {s}", _ycyl(14, 19, x=s * (hx - 10), y=ydf - 19, z=p["handle_z"]), "inst_black")
    # the motorized X-Y stage: a carrier on rails long enough to stay in the chamber, two slides, lead screws, and
    # the holder's socket in the middle
    st = fz + 62.0                                 # the socket's top, where the holder stands
    drawer.add("stage carrier", box(-xd + 12, yp + 16, fz + 10, xd - 12, yf + 255, fz + 20), "steel")
    drawer.add("stage y slide", box(-85, ys - 70, fz + 20, 85, ys + 70, fz + 38), "aluminium")
    drawer.add("stage x slide", box(-65, ys - 55, fz + 38, 65, ys + 55, fz + 54), "aluminium")
    drawer.add("socket", cyl(34, st - fz - 54, y=ys, z=fz + 54), "steel")
    drawer.add("y lead screw", _ycyl(8, 150, x=78, y=ys - 75, z=fz + 30), "steel")
    drawer.add("x lead screw", _xcyl(8, 130, x=-65, y=ys + 62, z=fz + 46), "steel")
    # its left face, where the sample goes, stands 70 degrees from horizontal and faces the EBSD detector on the left
    drawer.add("pre-tilted holder", box(-14, -8, 0, 14, 8, 26).rotate((0, 0, 0), (0, 1, 0), 20)
               .translate((45, ys, fz + 54)), "aluminium")
    # the sample: the polisher's 1.25 in Bakelite mount on a cylindrical holder, its height set at the bench
    stub = _piece(inst, "stub")
    stub.add("holder pin", cyl(12, 10, z=0), "steel")
    stub.add("holder post", cyl(20, 28, z=8), "aluminium")
    stub.add("holder collar", cyl(30, 8, z=22), "steel")
    stub.add("mount", cyl(MOUNT_D, 14, z=36), "mount_red")
    stub.add("polished face", cyl(MOUNT_D - 8, 0.6, z=50), "sample")
    inst.joints = {
        "drawer": Joint("slide", vec=(0, -p["draw"], 0)),
        "stub": Joint("path", parent="drawer", path=((W / 2 + 70, ys - 230, st + 200), (0, ys, st + 150),
                                                      (0, ys, st))),
    }
    inst.actions = [
        ("EVAC/AIR vents the chamber; the door is pulled straight out by its handle, the stage on its inside face.",
         1.6, {"drawer": (0.0, 1.0), "stub": (0.0, 0.0)}),
        ("The polished mount, on a holder set to height at the bench, drops into the socket in the stage.", 2.0,
         {"stub": (0.0, 1.0)}),
        ("Door in, EVAC/AIR again: about three minutes to vacuum. The EDS detector is built in, its analyser beside. "
         "EBSD (left) is a proposal: no TM4000 option exists, and it needs a 70 degree pre-tilted holder.", 2.6,
         {"drawer": (1.0, 0.0)}),
    ]
    inst.labels = [("EDS analyser (AZtecOne)", (W / 2 + 190, -90, 330), (0.84, 0.22)),
                   ("EBSD (proposed)", (-W / 2 - 110, ys, cz + 30), (0.14, 0.28)),
                   ("sample drawer", (0, ydf, 150), (0.18, 0.70)),
                   ("EVAC/AIR", (p["btn_x"], yp, p["btn_z"]), (0.62, 0.42))]
    inst.notes = ["The door is a drawer: AIR vents the chamber, the door comes straight out with the X-Y stage on "
                  "its inside face, and the sample holder drops into the stage's socket (CCEM's and Microscopy "
                  "Australia's TM4000Plus videos)."]
    # from the front left, steep enough, and far enough round, to see past the open door into the stage's socket
    inst.cam = (-1.5, -1.2, 1.2)
    inst.zoom = {1: ((0, yf - 40, st + 60), 800.0), 2: "out"}
    return inst


# register.py: the SEM's anchors, the parameters fitted to the frames in refs/sem/, and what keeps a fitted model
# buildable: the door under the panel with room for the handle, the button and badges on the panel, the top strip
# behind the rolled front edge.
ANCHORS["sem"] = (SEM, sem_anchors)
FREE["sem"] = ["front_z0", "drawer_top", "blue_top", "frame_w", "recess", "proud", "door_w", "btn_x", "btn_z", "badge_z",
               "handle_z", "handle_w", "hump_w", "hump_h", "hump_y0", "hump_run", "feet"]
CHECKS["sem"] = lambda p: [p["blue_top"] - p["drawer_top"] - 120, p["drawer_top"] - p["front_z0"] - 150,
                           p["btn_z"] - p["drawer_top"] - 20, p["blue_top"] - p["btn_z"] - 40,
                           p["drawer_top"] - p["handle_z"] - 14, p["W"] / 2 - p["frame_w"] - p["btn_x"] - 15,
                           p["door_w"] - p["handle_w"] - 20, p["W"] - 2 * p["frame_w"] - p["door_w"] - 6,
                           p["hump_y0"] - 20, p["nose_r"] - p["hump_y0"] - 5, p["feet"] - 5]


# ===================================================================================================== PIP
# Plastometrex PLX-Benchtop (profilometry-based indentation plastometry), from Plastometrex's own videos: "Introducing
# the PLX-Benchtop" (w7OZsrru9AI), "Benchtop Indentation Plastometer Demonstration" (1qGM3JY2tFM, which labels the load
# cell, indenter and profilometer) and the "How a PIP test works!" animation (wL5z5wjLI1U); the proportions are fitted
# to the first one's frames with register.py (refs/pip/). Matte black: a housing with rounded top edges over a
# portal of two columns, a silver trim at the waist and a silver plinth; on the housing's front a recessed panel with
# "PX" and a U of blue LEDs; a red e-stop on its right side. In the bay, open at the front with no door or guard: a dark
# crosshead between the columns with two yellow hazard labels and silver blocks at its ends, louvres on the columns'
# inner faces; under it the indenter in a stainless cylinder, and a stainless platen on eight posts on a pancake load
# cell set into the floor. The sample goes on the platen by hand, unclamped; up to 160 mm across, under 8 mm thick on
# a fixture (Illinois MRL and a published SOP). PLX-AutoStage is Plastometrex's add-on that automates the loading.
# The stylus profilometer is beside the indenter, not on a column: a slotted aluminium arm hangs from a carriage under
# the right of the crosshead, leaning outwards, with a short shaft at its foot pointing to the front and the stylus
# pick-up on that. The carriage runs along x: parked, the stylus is about 110 mm right of the indenter's axis, outside
# the platen, at the sample's height (demonstration video, 0:36); it runs in towards the indenter (0:55), and with the
# indenter lifted the pick-up goes in under it, over the indent (animation, 0:09). Plastometrex publishes no
# dimensions: the width, 500 mm, is the scale (from photos, +-20 %); the other proportions are fitted to the frames.
PIP = dict(W=500.0, D=560.0, H=689.0, feet=8.0, base_h=43.0, col_w=104.0, top_z0=387.0, trim_h=12.0, led_x=172.0,
           led_z0=52.0, led_z1=196.0, xh_y=18.0, xh_z0=184.0, xh_z1=369.0, lab_x=126.0, stack=56.0, stage_d=154.0,
           yc=-30.0, estop_y=45.0, estop_z=79.0, park=112.0, arm_deg=27.0, drop=3.0, scan=3.0, lift=-2.0)


def _plx(p) -> dict:
    """The positions the PIP model and its anchors share."""
    W, D = p["W"], p["D"]
    yf = -D / 2
    zb = p["feet"] + p["base_h"]                  # the plinth's top: the bay floor, the columns' feet
    bx = W / 2 - p["col_w"]                       # the columns' inner faces, at +-bx
    stz = zb + p["stack"]                         # the platen's top face
    return dict(W=W, D=D, yf=yf, zb=zb, bx=bx, stz=stz, s_top=stz + 6.0, yc=p["yc"],
                lab_z=p["xh_z0"] + 0.62 * (p["xh_z1"] - p["xh_z0"]))


def pip_anchors(p, pose=None) -> dict:
    """Named points, circles and lines of the PIP model for register.py (the machine doesn't move in the frames)."""
    g = _plx(p)
    W, yf, zb, bx, z0 = g["W"], g["yf"], g["zb"], g["bx"], p["top_z0"]
    a = {"base fl": (-W / 2, yf, p["feet"]), "base fr": (W / 2, yf, p["feet"]),
         "col fl foot": (-W / 2, yf, zb), "col fr foot": (W / 2, yf, zb),
         "bay bl": (-bx, yf, zb), "bay br": (bx, yf, zb), "bay tl": (-bx, yf, z0), "bay tr": (bx, yf, z0),
         "trim fl": (-W / 2, yf, z0), "trim fr": (W / 2, yf, z0),
         "led bl": (-p["led_x"], yf - 2, z0 + p["led_z0"]), "led br": (p["led_x"], yf - 2, z0 + p["led_z0"]),
         "led tl": (-p["led_x"], yf - 2, z0 + p["led_z1"]), "led tr": (p["led_x"], yf - 2, z0 + p["led_z1"]),
         "estop": (W / 2 + 22, yf + p["estop_y"], z0 + p["estop_z"]),
         "label L": (-p["lab_x"], yf + p["xh_y"] - 1, g["lab_z"]), "label R": (p["lab_x"], yf + p["xh_y"] - 1, g["lab_z"]),
         "xh bottom": ("line", (-bx + 30, yf + p["xh_y"] + 30, p["xh_z0"]), (bx - 30, yf + p["xh_y"] + 30, p["xh_z0"])),
         "platen edge": ("circle", (0.0, g["yc"], g["stz"]), p["stage_d"] / 2),
         "top": ("line", (-W / 2 + 60, yf + 32, p["H"]), (W / 2 - 60, yf + 32, p["H"])),
         "left edge": ("line", (-W / 2, yf, zb + 40), (-W / 2, yf, p["H"] - 60)),
         "right edge": ("line", (W / 2, yf, zb + 40), (W / 2, yf, p["H"] - 60))}
    return a


def pip() -> Instrument:
    p = PIP
    g = _plx(p)
    W, D, H, yf, zb, bx, stz, s_top, yc = g["W"], g["D"], p["H"], g["yf"], g["zb"], g["bx"], g["stz"], g["s_top"], g["yc"]
    z0, z1 = p["top_z0"], p["top_z0"] + p["trim_h"]
    inst = Instrument("pip", "Indentation plastometer (PIP)", "Plastometrex PLX-Benchtop", (W, D, H),
                      "Plastometrex's videos (PLX-Benchtop introduction, benchtop demonstration, 'How a PIP test "
                      "works!'), fitted with register.py; Illinois MRL and a published SOP for loading; no published "
                      "dimensions, so the 500 mm width is the scale")
    body = _piece(inst, "body")
    for sx in (-1, 1):
        for sy in (-1, 1):
            body.add(f"foot {sx} {sy}", box(sx * (W / 2 - 15) - 15, sy * (D / 2 - 25) - 15, 0,
                                            sx * (W / 2 - 15) + 15, sy * (D / 2 - 25) + 15, p["feet"]), "inst_black")
    body.add("plinth", box(-W / 2, yf, p["feet"], W / 2, D / 2, zb).edges("|Z").fillet(10)
             .faces(">Z").edges("<Y").chamfer(4), "aluminium")
    for sx in (-1, 1):
        x0, x1 = sorted((sx * W / 2, sx * bx))
        col = box(x0, yf, zb, x1, D / 2, z0).edges("|Z").fillet(10)
        body.add(f"column {'LR'[sx > 0]}", col, "inst_dark")
        # louvres on the column's inner face, from the floor up to the crosshead
        xi = sx * bx
        for i in range(int((p["xh_z0"] - zb - 20) // 9)):
            z = zb + 12 + 9 * i
            body.add(f"louvre {'LR'[sx > 0]} {i}", box(min(xi, xi - sx * 3), yf + 40, z, max(xi, xi - sx * 3),
                                                       D / 2 - 40, z + 4), "inst_black")
    body.add("back panel", box(-bx, D / 2 - 30, zb, bx, D / 2 - 18, z0), "inst_light")
    body.add("trim", box(-W / 2 - 1.5, yf - 1.5, z0, W / 2 + 1.5, D / 2 + 1.5, z1).edges("|Z").fillet(10), "aluminium")
    for sx in (-1, 1):                           # the silver lozenge on each side at the waist
        tab = cq.Workplane("YZ").polyline([(-60, 0), (-45, 12), (45, 12), (60, 0), (45, -8), (-45, -8)]).close() \
            .extrude(2).translate((sx * (W / 2 + 1.5) - (2 if sx < 0 else 0), 0, z0 + 6))
        body.add(f"waist tab {sx}", tab, "aluminium")
    housing = box(-W / 2, yf, z1, W / 2, D / 2, H).edges("|Z").fillet(10).faces(">Z").edges().fillet(32)
    body.add("housing", housing, "inst_dark")
    # the recessed front panel ("PX"), framed by a U of blue LEDs
    lx, lz0, lz1 = p["led_x"], z0 + p["led_z0"], z0 + p["led_z1"]
    body.add("front panel", box(-lx + 5, yf - 1, lz0 + 5, lx - 5, yf, H - 40), "inst_black")
    led = box(-lx - 3, yf - 2, lz0 - 3, lx + 3, yf, lz0 + 3).union(box(-lx - 3, yf - 2, lz0 - 3, -lx + 3, yf, lz1)) \
        .union(box(lx - 3, yf - 2, lz0 - 3, lx + 3, yf, lz1))
    body.add("LED band", led, "led_blue")
    body.add("PX logo", box(-38, yf - 1.6, lz0 + 70, 38, yf - 1, lz0 + 110), "inst_dark")
    ey, ez = yf + p["estop_y"], z0 + p["estop_z"]
    body.add("e-stop base", _xcyl(30, 10, x=W / 2, y=ey, z=ez), "inst_black")
    body.add("e-stop", _xcyl(34, 12, x=W / 2 + 10, y=ey, z=ez).edges(">X").fillet(4), "inst_red")
    # the crosshead between the columns: a dark cowl, its lower front edge bevelled, a raised panel in the middle
    xy0 = yf + p["xh_y"]
    xz0, xz1 = p["xh_z0"], p["xh_z1"]
    cowl = box(-bx, xy0, xz0, bx, D / 2 - 40, xz1).faces("<Z").edges("<Y").chamfer(28)
    body.add("crosshead", cowl, "inst_dark")
    body.add("crosshead panel", box(-60, xy0 - 4, xz0 + 34, 60, xy0, xz1 - 14).edges("|Y").fillet(6), "inst_dark")
    for sx in (-1, 1):
        tri = cq.Workplane("XZ").polyline([(-13, -11), (13, -11), (0, 12)]).close().extrude(1) \
            .translate((sx * p["lab_x"], xy0 - 0.5, g["lab_z"]))
        body.add(f"hazard label {sx}", tri, "inst_yellow")
        body.add(f"guide block {sx}", box(sx * bx - (16 if sx > 0 else 0), xy0 + 6, xz0 - 34, sx * bx + (0 if sx > 0 else 16),
                                          xy0 + 36, xz0 + 8), "aluminium")
    # the load string: a pancake load cell set into the floor, eight posts, a plain stainless disc for the platen
    cell_top = stz - 12 - 9
    body.add("load cell", cyl(0.9 * p["stage_d"], cell_top - zb + 6, y=yc, z=zb - 6).edges(">Z").chamfer(2), "steel")
    body.add("load cell connector", _xcyl(14, 34, x=0.45 * p["stage_d"] - 4, y=yc, z=zb + 8), "steel")
    for i in range(8):
        t = math.radians(22.5 + 45 * i)
        body.add(f"post {i}", cyl(14, 9, x=0.36 * p["stage_d"] * math.cos(t), y=yc + 0.36 * p["stage_d"] * math.sin(t),
                                  z=cell_top), "stainless")
    body.add("platen", cyl(p["stage_d"], 12, y=yc, z=stz - 12).faces(">Z").edges().chamfer(1.5), "stainless")
    # the profilometer's rail under the crosshead, behind the indenter
    ya = yc + 30.0                                # the arm's plane; its shaft reaches 30 mm forward to the indent's y
    body.add("profilometer rail", box(-20, ya - 6, xz0 - 10, bx - 10, ya + 6, xz0), "aluminium")
    # the indenter: a stainless cylinder down from the crosshead, a dark tip holder, the ball (the "head" piece)
    head = _piece(inst, "head")
    hold_z = s_top + 7.0 + 12.0                   # the holder's underside with the ram up: the ball 7 mm above the sample
    head.add("indenter cylinder", cyl(40, xz0 - hold_z + 10, y=yc, z=hold_z), "stainless")
    head.add("indenter collar", cyl(32, 4, y=yc, z=hold_z - 4), "inst_black")
    head.add("indenter tip", cq.Workplane("XY").circle(8).workplane(offset=8).circle(3).loft()
             .rotate((0, 0, 0), (1, 0, 0), 180).translate((0, yc, hold_z - 4)), "inst_dark")
    head.add("indenter", cq.Workplane("XY").sphere(1.0).translate((0, yc, hold_z - 12)), "inst_black")  # a 1 mm-radius WC ball
    # the profilometer: carriage, inclined arm, a shaft forward at its foot, the pick-up with its stylus
    sty = _piece(inst, "stylus")
    tip_z = s_top + p["drop"]                      # the stylus tip, parked: just above the sample's top face
    foot = np.array([p["park"], ya, tip_z + 14.0])  # the arm's foot, where the shaft comes out
    rise = xz0 - 10 - foot[2]
    t = math.radians(p["arm_deg"])
    top = foot + np.array([-rise * math.tan(t), 0, rise])   # it leans outwards going down
    sty.add("profilometer carriage", box(top[0] - 18, ya - 7, xz0 - 22, top[0] + 18, ya + 7, xz0 - 10), "inst_dark")
    L = float(np.linalg.norm(foot - top))
    arm = (cq.Workplane("XZ").rect(18, L + 10).extrude(-6).edges("|Y").fillet(8.5)
           .faces("<Y").workplane().rect(9, L - 20).cutBlind(-2)
           .rotate((0, 0, 0), (0, 1, 0), -p["arm_deg"]).translate(tuple((foot + top) / 2 + np.array([0, -3, 0]))))
    sty.add("profilometer arm", arm, "aluminium")
    sty.add("profilometer shaft", _ycyl(6, 30, x=foot[0], y=ya - 30, z=foot[2]), "steel")
    sty.add("stylus pick-up", box(foot[0] - 5, ya - 36, foot[2] - 11, foot[0] + 5, ya - 26, foot[2] + 3), "inst_black")
    sty.add("stylus", cyl(1.6, 3.5, x=foot[0], y=yc, z=tip_z).union(
        cq.Workplane("XY").sphere(0.5).translate((foot[0], yc, tip_z))), "steel")
    sample = _piece(inst, "sample")
    sample.add("sample", box(-20, -20, 0, 20, 20, 6), "sample")
    dent = _piece(inst, "indent")                  # shows once the ball lifts off; rides on the sample
    dent.add("indent", cyl(2.0, 0.3, z=6.0), "inst_dark")        # in the sample's own frame
    gap = 7.0                                      # the ball's lowest point to the sample's top face, ram up
    dx, sc, dz = p["park"], p["scan"], p["drop"]
    # the stylus's route: in along x until it is just past the indent, down onto the surface, across the indent and
    # back, up, and out to its parking place again
    route = ((0, 0, 0), (-dx + sc, 0, 0), (-dx + sc, 0, -dz), (-dx - sc, 0, -dz), (-dx + sc, 0, -dz),
             (-dx + sc, 0, 0), (0, 0, 0))
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
        ("Hands clear: the indenter comes down out of its cylinder and presses the 1 mm-radius ball in, an indent "
         "0.25-1 mm wide. The profilometer waits at the right, clear of the platen.", 1.8, {"head": (0.0, 1.0)}),
        ("The indenter lifts well clear; the profilometer's carriage runs in along the crosshead and its pick-up "
         "passes under the indenter to the indent.", 2.2,
         {"head": (1.0, p["lift"]), "stylus": (0.0, float(at[2])), "indent": (0.0, 1.0)}),
        ("The stylus traces across the indent, line by line, to map its 3D shape.", 1.8,
         {"stylus": (float(at[2]), float(at[4]))}),
        ("It lifts and runs back out to the right, and the indenter goes back to its start.", 1.6,
         {"stylus": (float(at[4]), 1.0), "head": (p["lift"], 0.0)}),
        ("CORSICA fits a stress-strain curve to that profile in minutes. The sample comes off.", 2.0,
         {"sample": (1.0, 0.0), "indent": (1.0, 1.0)}),
    ]
    inst.labels = [("indenter", (-20, yc, hold_z + 30), (0.16, 0.30)),
                   ("profilometer", (float(foot[0]) + 8, ya, float(foot[2]) + 30), (0.86, 0.34)),
                   ("platen on a load cell", (0, yc - p["stage_d"] / 2, stz - 6), (0.84, 0.72))]
    inst.anchors = pip_anchors(p)
    inst.zoom = {2: ((30.0, yc, s_top + 30), 520.0), 4: "out"}      # in on the bay for the profile, then back out
    inst.notes = ["The profilometer's place is from Plastometrex's own footage; how its pick-up is lowered onto the "
                  "surface (the animation shows a rotation at the arm's foot) is simplified to a small drop here."]
    inst.cam = (0.32, -1.9, 0.28)                   # low and nearly frontal, as the videos show the bay
    inst.framing = (0.86, 0.44)                     # the whole machine in view, the bay still large
    return inst


# register.py: the PIP's anchors, the proportions fitted to Plastometrex's frames (refs/pip/), with the 500 mm width
# as the scale, and what keeps a fitted model buildable: the LED U inside the panel, the crosshead under the waist and
# above the platen, the labels on the crosshead, the platen between the columns.
ANCHORS["pip"] = (PIP, pip_anchors)
FREE["pip"] = ["H", "base_h", "col_w", "top_z0", "led_x", "led_z0", "led_z1", "xh_y", "xh_z0", "xh_z1", "lab_x",
               "stack", "stage_d", "yc", "estop_y", "estop_z"]
CHECKS["pip"] = lambda p: [p["W"] / 2 - p["led_x"] - 30, p["led_z1"] - p["led_z0"] - 60,
                           p["H"] - p["top_z0"] - p["led_z1"] - 30, p["top_z0"] - p["xh_z1"] - 10,
                           p["xh_z1"] - p["xh_z0"] - 60, p["xh_z0"] - p["feet"] - p["base_h"] - p["stack"] - 35,
                           p["W"] / 2 - p["col_w"] - p["lab_x"] - 20, p["W"] / 2 - p["col_w"] - p["stage_d"] / 2 - 10]


# ===================================================================================================== rail
# Vention's robot seventh axis, rack and pinion (Vention design 337010, "Robot 7th axis rack and pinion robot transfer
# unit 3330 mm": 3488 x 628 x 1017 mm, 220 kg): a 247.5 x 247.5 mm extrusion beam in 3330 mm segments on legs of the
# same extrusion on 405 mm floor plates; two 20 mm profile guides and a steel rack; a 426.5 x 358 x 86 mm carriage
# plate driven by a NEMA 34 servo through a right-angle gearbox; a 73 mm drag chain; dark blue anodizing; up to 4 m/s
# (Vention's design, part pages and actuator docs). The legs are cut so the arm's base sits at 800 mm, where it sits on
# the MiR250, and the axis runs along the fronts of the line. Vention's STEP needs a MachineBuilder account.
RAIL = dict(beam_w=247.5, beam_h=247.5, top=800.0, leg_pitch=3330.0, car_l=426.5, car_w=358.0, car_t=86.0)


def rail(length: float = 4000.0, travel: float = 1600.0, chain: bool | None = None) -> Instrument:
    """Vention's seventh axis with the carriage at x = 0 (v = 0) to `travel` (v = 1). chain: its energy chain as
    links that follow the carriage (the default for a travel in mm; line.py drives the carriage with travel = 1 and
    a 17 m beam, so its chain is the fixed one it had)."""
    p = RAIL
    chain = travel >= 200.0 if chain is None else chain
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
    # the energy chain, in its tray behind the beam: its fixed end halfway along the moving end's travel, its lower
    # run on the tray's floor, the bend rising to the upper run, which ends on a bracket under the carriage's back
    # edge; the bend travels at half the carriage's speed. Link 70 x 44 mm, bend radius 98 mm: ours, to suit the
    # 73 mm chain and the 230 mm between the tray's floor and the carriage plate.
    cy0, cy1 = bw / 2 + 10, bw / 2 + 80
    ch = dict(h=44.0, r=98.0, z_low=z0 + 30 + 22.0, end_dx=-p["car_l"] / 2 + 20.0)
    x_end0 = ch["end_dx"]
    x_fix = x_end0 + travel / 2.0
    straight = travel / 2.0 + 100.0
    if not chain:
        body.add("cable chain", box(-L / 2 + 100, cy0, z0 + 30, 0, cy1, z0 + 75), "inst_black")
    else:
        body.add("chain fixed end", box(x_fix, cy0 - 4, z0 + 30, x_fix + 30, cy1 + 4, z0 + 30 + ch["h"] + 8),
                 "aluminium")
        body.add("chain cable", hose([(x_fix + 15, (cy0 + cy1) / 2, z0 + 20), (x_fix + 15, (cy0 + cy1) / 2, 300.0),
                                      (-L / 2 + 900, (cy0 + cy1) / 2, 300.0), (-L / 2 + 900, 120.0, 300.0)], 24.0),
                 "inst_black")
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
    links = []
    if chain:
        zu = ch["z_low"] + 2 * ch["r"]
        car.add("chain bracket", box(x_end0 - 22, cy0 - 4, zu - ch["h"] / 2 - 6, x_end0 + 8, p["car_w"] / 2,
                                     top - p["car_t"]), "aluminium")
        total = straight + math.pi * ch["r"]
        n = int(round(total / 36.0))
        pitch = total / n
        for i in range(n):
            prm = chain_params((i + 0.5) * pitch, x_fix, x_end0, travel, straight, ch["r"], ch["z_low"])
            pose = chain_pose(prm, 0.0)
            link = box(-pitch / 2 + 1.2, cy0, -ch["h"] / 2, pitch / 2 - 1.2, cy1, ch["h"] / 2)
            link = link.union(box(-pitch / 2 + 4, cy0 + 8, -ch["h"] / 2 - 1, pitch / 2 - 4, cy1 - 8, ch["h"] / 2 + 1))
            ang = math.degrees(math.atan2(pose[0, 2], pose[0, 0]))
            link = link.rotate((0, 0, 0), (0, 1, 0), ang).translate((float(pose[0, 3]), 0.0, float(pose[2, 3])))
            key = f"chain {i:02d}"
            _piece(inst, key).add("link", link, "inst_black")
            inst.joints[key] = Joint("chain", path=prm)
            links.append(key)

    def drive(a, b):
        return {"carriage": (a, b), **{k: (a, b) for k in links}}
    inst.actions = [
        ("The backup to the mobile base: a Vention seventh axis. The carriage carries the arm along the line on a "
         "rack and pinion; its energy chain's bend travels at half the carriage's speed.", 2.6, drive(0.0, 1.0)),
        ("Up to 4 m/s. Its legs are cut so the arm's base is at 800 mm, where it sits on the MiR250.", 2.2,
         drive(1.0, 0.0)),
    ]
    inst.labels = [("carriage and gearmotor", (0, -cw / 2 - 70, z1 - 60), (0.16, 0.30)),
                   ("rack and guides", (L / 2 - 400, -bw / 2, z1), (0.82, 0.40)),
                   ("control cabinet", (-L / 2 + 700, -150, z0 - 220), (0.16, 0.72))]
    inst.cam = (0.55, -1.5, 0.6)
    if chain:                   # seen from behind, where the chain runs; the gearmotor and rack are on the far side
        inst.labels = [("carriage (gearmotor, pinion and rack on the far side)", (0, cw / 2, top), (0.16, 0.24)),
                       ("guides", (L / 2 - 400, bw / 2 - 30, z1 + 15), (0.84, 0.30)),
                       ("energy chain: fixed end halfway along the travel", (x_fix + 15, cy1 + 4, z0 + 70),
                        (0.84, 0.62)),
                       ("control cabinet", (-L / 2 + 700, 150, z0 - 220), (0.16, 0.74))]
        inst.cam = (0.5, 1.6, 0.75)
    return inst


# ===================================================================================================== polisher
# LECO PX500 semi-automatic grinder-polisher: the machine in the lab's own SOP videos (BYU Vertical Cloud Lab channel,
# "Alumina polish" parts 1-3 and "320-1200 Polishing + Alumina on pad"). Until the SOP footage was checked this was a
# Buehler EcoMet 30. LECO's brochure (form 209-254, 2020): wheels up to 12 in (300 mm); a motorized head for fixed
# and individual specimen holders; up to five metered dispensers; a 7 in multi-touch screen with the emergency stop
# under it; a spiral bowl with automatic bowl wash; a detachable water spigot; LED work light. LECO publishes no
# dimensions (533 W x 711 D x 635 H mm, 21 x 28 x 25 in, is a reseller's figure for the PX400/PX500 series), so the
# proportions are fitted to the lab's frames with register.py (refs/polisher/), the 7 in screen (155 x 87 mm active)
# setting the scale. Look, from those frames and LECO's photos: light grey; the round front-left of the base holds the
# bowl, its lip a raised grey ring; the right of the front is a block with the screen on a steep slope, "PX500" above
# it and the red e-stop in a yellow collar below; the head is a tall, rounded grey housing over the back of the bowl,
# with a blue-lit ring around the spindle under it and the 6-position holder below that; a stainless gooseneck spigot
# comes out of the head's right side; five dispenser bottles stand in a rack on the left side.
POLISHER = dict(W=558.0, D=711.0, deck=312.0, drum_r=226.0, rim_gap=8.0, lip_w=24.0, rim_h=16.0, block_k=0.90,
                platen_d=305.0, platen_z=-33.0, slope_z0=191.0, slope_d=82.0, scr_x=191.0, scr_s=0.30,
                estop_x=247.0, estop_z=94.0, head_w=281.0, head_d=360.0, head_h=253.0, head_back=100.0,
                head_up=112.0, head_drop=95.0, hold_dx=-29.0, hold_dy=35.0, hold_d=150.0)
SCREEN = (155.0, 87.0)          # a 7 in 16:9 display's active area, mm
MOUNT_D = 31.75                 # 1.25 in Bakelite mounts, as in the lab's "Making Bakelite Polishing Puck"


def _px500(p) -> dict:
    """The positions the model and its anchors share."""
    W, D = p["W"], p["D"]
    yf = -D / 2
    bx, by = -W / 2 + p["drum_r"], yf + p["drum_r"]
    hx, hy = bx + p["hold_dx"], by + p["hold_dy"]                  # the holder's axis, under the head
    sy, sz = p["slope_d"], p["deck"] - p["slope_z0"]
    L = math.hypot(sy, sz)
    up = np.array([0.0, sy / L, sz / L])                           # up the screen's slope
    sc = np.array([p["scr_x"], yf, p["slope_z0"]]) + up * (p["scr_s"] * L)
    rim_r = p["drum_r"] - p["rim_gap"]                             # the bowl's lip, a little inside the drum
    return dict(W=W, D=D, yf=yf, bx=bx, by=by, hx=hx, hy=hy, up=up, L=L, sc=sc, rim_r=rim_r, bowl_r=rim_r - p["lip_w"],
                xb=bx + p["block_k"] * p["drum_r"],                # the screen block's left side
                hcy=hy + p["head_back"] - p["head_d"] / 2)        # the housing's centre: it reaches back to the column


def polisher_anchors(p, pose=None) -> dict:
    """Named points, circles and lines of the model, for register.py; the head's follow pose["head"] (0 up, 1 down)."""
    g = _px500(p)
    dk, yf, W = p["deck"], g["yf"], g["W"]
    a = {"platen edge": ("circle", (g["bx"], g["by"], dk + p["platen_z"]), p["platen_d"] / 2),
         "rim outer": ("circle", (g["bx"], g["by"], dk + p["rim_h"]), g["rim_r"]),
         "rim inner": ("circle", (g["bx"], g["by"], dk + p["rim_h"]), g["bowl_r"]),
         "drum foot": ("circle", (g["bx"], g["by"], 0.0), p["drum_r"]),
         "drum top": ("circle", (g["bx"], g["by"], dk), p["drum_r"]),
         "block foot right": (W / 2, yf, 0.0),
         "block top right": (W / 2, yf, p["slope_z0"]),
         "deck front right": (W / 2, yf + p["slope_d"], dk),
         "block top left": (g["xb"], yf, p["slope_z0"]),
         "estop": (p["estop_x"], yf - 14.0, p["estop_z"])}
    w, h = SCREEN
    for nm, (fx, fz) in {"screen tl": (-1, 1), "screen tr": (1, 1), "screen bl": (-1, -1), "screen br": (1, -1)}.items():
        a[nm] = tuple(g["sc"] + np.array([fx * w / 2, 0, 0]) + g["up"] * (fz * h / 2))
    dz = -p["head_drop"] * float((pose or {}).get("head", 0.0))
    z0, z1 = dk + p["head_up"] + dz, dk + p["head_up"] + p["head_h"] + dz
    hcy = g["hcy"]
    hy0 = hcy - p["head_d"] / 2                                     # the housing's front
    a.update({"head front bottom": (g["hx"], hy0, z0), "head front top": (g["hx"], hy0, z1),
              "head left": ("line", (g["hx"] - p["head_w"] / 2, hcy, z0 + 40), (g["hx"] - p["head_w"] / 2, hcy, z1 - 40)),
              "head right": ("line", (g["hx"] + p["head_w"] / 2, hcy, z0 + 40), (g["hx"] + p["head_w"] / 2, hcy, z1 - 40)),
              "head top": ("line", (g["hx"] - p["head_w"] / 2 + 60, hcy, z1), (g["hx"] + p["head_w"] / 2 - 60, hcy, z1)),
              "holder": ("circle", (g["hx"], g["hy"], dk + p["head_up"] - 120 + dz), p["hold_d"] / 2)})
    return a


def polisher() -> Instrument:
    p = POLISHER
    g = _px500(p)
    W, D, yf, bx, by, hx, hy, dk = g["W"], g["D"], g["yf"], g["bx"], g["by"], g["hx"], g["hy"], p["deck"]
    H = dk + p["head_up"] + p["head_h"]
    inst = Instrument("polisher", "Metallographic grinder-polisher", "LECO PX500 semi-automatic", (W, D, round(H)),
                      "the lab's SOP videos (BYU Vertical Cloud Lab channel), fitted with register.py; LECO's PX400/PX500 "
                      "brochure (form 209-254) for the features; 533 x 711 x 635 mm is a reseller's series figure")
    body = _piece(inst, "body")
    R = p["drum_r"]
    # the base: the round drum around the bowl, the full-width back, and the screen block at the front right
    base = (cyl(2 * R, dk, x=bx, y=by)
            .union(box(-W / 2, by, 0, W / 2, D / 2, dk).edges("|Z and >Y").fillet(25))
            .union(box(g["xb"], yf, 0, W / 2, by + 1, dk).edges("|Z and <Y and >X").fillet(14)))
    # the screen's slope across the block's front: from slope_z0 at the front edge up to the deck
    pts = [(yf - 1, p["slope_z0"]), (yf + p["slope_d"], dk + 1), (yf - 1, dk + 1)]
    cut = cq.Workplane("YZ").polyline(pts).close().extrude(W / 2 - g["xb"] + 2).translate((g["xb"] - 1, 0, 0))
    base = base.cut(cut)
    bowl_floor = dk - 120.0
    rim_r, bowl_r = g["rim_r"], g["bowl_r"]
    base = base.cut(cyl(2 * bowl_r, dk - bowl_floor + 1, x=bx, y=by, z=bowl_floor))
    body.add("base", base, "px_grey")
    body.add("bowl", cyl(2 * bowl_r + 2, 4, x=bx, y=by, z=bowl_floor).union(
        tube(2 * bowl_r + 2, 2 * bowl_r - 6, dk - bowl_floor, x=bx, y=by, z=bowl_floor)), "inst_grey")
    body.add("bowl lip", tube(2 * rim_r, 2 * bowl_r, p["rim_h"], x=bx, y=by, z=dk).edges(">Z").fillet(5), "inst_light")
    # the screen in its bezel on the slope, PX500 above it, the e-stop under it
    up = g["up"]
    tilt = -math.degrees(math.atan2(up[1], up[2]))               # the slope's angle from vertical, about x
    sc = g["sc"]
    bez = box(-SCREEN[0] / 2 - 12, -3, -SCREEN[1] / 2 - 6, SCREEN[0] / 2 + 12, 0, SCREEN[1] / 2 + 8)
    scr = box(-SCREEN[0] / 2, -4, -SCREEN[1] / 2, SCREEN[0] / 2, -3, SCREEN[1] / 2)
    lab = box(SCREEN[0] / 2 - 50, -1.2, SCREEN[1] / 2 + 20, SCREEN[0] / 2, -0.5, SCREEN[1] / 2 + 30)
    # the SOP's screen: three setting rows on the left, the timer dial on the right, light on dark navy
    ui = box(-SCREEN[0] / 2 + 8, -4.6, -SCREEN[1] / 2 + 12, -SCREEN[0] / 2 + 70, -4.0, -SCREEN[1] / 2 + 14)
    for k in (1, 2):
        ui = ui.union(box(-SCREEN[0] / 2 + 8, -4.6, -SCREEN[1] / 2 + 12 + 22 * k, -SCREEN[0] / 2 + 70, -4.0,
                          -SCREEN[1] / 2 + 14 + 22 * k))
    dial = cq.Workplane("XZ").circle(24).circle(21).extrude(0.6).translate((SCREEN[0] / 2 - 42, -4.0, 2))
    for nm, solid, mat in (("bezel", bez, "inst_black"), ("touchscreen", scr, "px_screen"), ("screen rows", ui, "px_ui"),
                           ("screen dial", dial, "px_ui"), ("PX500 label", lab, "inst_dark")):
        body.add(nm, solid.rotate((0, 0, 0), (1, 0, 0), tilt).translate(tuple(sc)), mat)
    ex, ez = p["estop_x"], p["estop_z"]
    body.add("e-stop collar", _ycyl(54, 6, x=ex, y=yf - 6, z=ez), "inst_yellow")
    body.add("e-stop", _ycyl(38, 14, x=ex, y=yf - 18, z=ez).union(_ycyl(26, 8, x=ex, y=yf - 6, z=ez)), "inst_red")
    # the dark mat over the deck behind the bowl, as in the SOP frames
    body.add("deck mat", box(-W / 2 + 15, by + p["drum_r"] * 0.55, dk, W / 2 - 15, D / 2 - 15, dk + 3)
             .cut(cyl(2 * rim_r + 4, 10, x=bx, y=by, z=dk - 1)), "inst_dark")
    # the head's column, at the back under the housing (it stays inside the housing with the head down)
    cy = hy + p["head_back"] - 40
    body.add("column", rbox(110, 80, p["head_up"] + 60, 12, x=hx, y=cy, z=dk), "inst_grey")
    # five dispenser bottles in a rack on the left side
    rx = -W / 2 - 38                                               # the 5-position bottle holder, low on the left side
    body.add("bottle rack", box(rx - 34, by - 150, 12, rx + 34, by + 150, 18).union(
        box(-W / 2 - 2, by - 150, 12, -W / 2, by + 150, 90)), "steel")
    for i in range(5):
        y = by - 120 + 60 * i
        body.add(f"bottle {i + 1}", cyl(52, 150, x=rx, y=y, z=18).edges(">Z").fillet(10)
                 .union(cyl(20, 14, x=rx, y=y, z=168)), "inst_white")
    # the head: housing, the lit ring and spindle under it, the water spigot and the dispenser nozzles
    head = _piece(inst, "head")
    hz = dk + p["head_up"]
    hcy = g["hcy"]
    housing = rbox(p["head_w"], p["head_d"], p["head_h"], 0.42 * p["head_w"], x=hx, y=hcy, z=hz).edges(">Z").fillet(30)
    head.add("housing", housing.edges("<Z").fillet(8), "px_grey")
    head.add("housing skirt", rbox(p["head_w"] - 70, p["head_d"] - 70, 18, 0.35 * p["head_w"], x=hx, y=hcy, z=hz - 18),
             "inst_dark")
    head.add("lit ring", cyl(118, 34, x=hx, y=hy, z=hz - 52), "led_blue")
    head.add("hub", cyl(70, 26, x=hx, y=hy, z=hz - 78), "inst_dark")
    head.add("spindle", cyl(34, 30, x=hx, y=hy, z=hz - 108), "chrome")
    sx = hx + p["head_w"] / 2
    spout_end = (bx + 105, by + 20, dk + 62)
    hh = p["head_h"]
    head.add("spigot fitting", _xcyl(26, 34, x=sx - 20, y=hy, z=hz + 0.78 * hh), "inst_white")
    head.add("spigot", hose([(sx + 10, hy, hz + 0.78 * hh), (sx + 34, hy - 4, hz + 0.70 * hh),
                             (sx + 44, hy - 8, hz + 0.40 * hh), (sx + 38, hy - 12, hz + 0.05 * hh),
                             (spout_end[0] + 18, spout_end[1], dk + 110), spout_end], 10), "chrome")
    for i in range(2):
        head.add(f"dispenser nozzle {i + 1}", cyl(7, 40, x=hx + 70 + 14 * i, y=hy - 70, z=hz - 40), "steel")
    holder = _piece(inst, "holder")
    hz_h = hz - 120.0                                              # the holder's underside, head up
    flower = cyl(p["hold_d"], 12, x=hx, y=hy, z=hz_h)
    for i in range(6):
        a_ = math.radians(30 + 60 * i)
        flower = flower.cut(cyl(MOUNT_D + 1, 14, x=hx + 52 * math.cos(a_), y=hy + 52 * math.sin(a_), z=hz_h - 1))
        flower = flower.cut(cyl(40, 14, x=hx + 84 * math.cos(a_ + math.pi / 6), y=hy + 84 * math.sin(a_ + math.pi / 6),
                                z=hz_h - 1))
    holder.add("6-position holder", flower, "stainless")
    for i in range(6):
        a_ = math.radians(30 + 60 * i)
        holder.add(f"mount {i + 1}", cyl(MOUNT_D, 25, x=hx + 52 * math.cos(a_), y=hy + 52 * math.sin(a_),
                                         z=hz_h - 13), "mount_red")
    pz = dk + p["platen_z"]                                        # the abrasive's top
    platen = _piece(inst, "platen")
    platen.add("platen", cyl(p["platen_d"], 16, x=bx, y=by, z=pz - 17), "aluminium")
    platen.add("platen hub", cyl(90, pz - 17 - bowl_floor, x=bx, y=by, z=bowl_floor), "steel")
    platen.add("magnetic disc", cyl(p["platen_d"] - 4, 0.8, x=bx, y=by, z=pz - 1.2), "inst_dark")
    paper = _piece(inst, "paper")
    paper.add("SiC paper", cyl(p["platen_d"] - 2, 0.6, x=bx, y=by, z=pz - 0.6).union(
        box(bx - 2, by - p["platen_d"] / 2 + 6, pz, bx + 2, by - p["platen_d"] / 2 + 60, pz + 0.3)), "sic_paper")
    cloth = _piece(inst, "cloth")
    cloth.add("polishing cloth", cyl(p["platen_d"] - 2, 1.4, x=bx, y=by, z=pz - 0.6), "cloth_white")
    drop = hz_h - 13 - pz                                          # the head comes down until the mounts touch
    # the water and the suspension are drawn as they fall with the head down (they ride on the head)
    water = _piece(inst, "glow")
    ls = spout_end[2] - drop - pz
    water.add("water", cyl(5, ls, x=spout_end[0], y=spout_end[1], z=spout_end[2] - ls), "water")
    stream = _piece(inst, "powder")
    ls = hz - 40 - drop - pz - 1.4
    stream.add("alumina stream", cyl(4, ls, x=hx + 70, y=hy - 70, z=hz - 40 - ls), "alumina")
    film = _piece(inst, "alumina")
    film.add("alumina on the cloth", tube(250, 90, 0.5, x=bx, y=by, z=pz + 0.8), "alumina")
    inst.joints = {
        "head": Joint("slide", vec=(0, 0, -drop)),
        "holder": Joint("spin", parent="head", axis=(0, 0, 1), pivot=(hx, hy, 0), deg=-150.0),
        "platen": Joint("spin", axis=(0, 0, 1), pivot=(bx, by, 0), deg=-720.0),
        "paper": Joint("fade", parent="platen"),
        "cloth": Joint("fade", parent="platen"),
        "glow": Joint("fade", parent="head"),
        "powder": Joint("fade", parent="head"),
        "alumina": Joint("fade", parent="platen"),
    }
    inst.actions = [
        ("The lab's LECO PX500, as in its SOP videos: six Bakelite mounts in the 6-position holder; a 12 in platen.",
         1.4, {}),
        ("A 320-grit SiC paper on the platen (by hand in the SOP; by the arm on a tray).", 1.2, {"paper": (0.0, 1.0)}),
        ("Head down, water on. The SOP's grinding step: head 35 rpm, force 30, platen 150 rpm, 30 s.", 3.4,
         {"head": (0.0, 1.0), "platen": (0.0, 1.0), "holder": (0.0, 1.0), "glow": (0.0, 1.0)}),
        ("Head up and rinse; then 400, 600, 800 and 1200 grit, a fresh paper each time.", 1.6,
         {"head": (1.0, 0.0), "glow": (1.0, 0.0), "paper": (1.0, 0.0)}),
        ("The final polish: a white cloth on the platen, for 1 um alumina suspension.", 1.4, {"cloth": (0.0, 1.0)}),
        ("Head down, suspension from a dispenser (squeezed from a bottle in the SOP): force 3-5, 150 rpm, 3 min.", 3.4,
         {"head": (0.0, 1.0), "platen": (1.0, 2.0), "holder": (1.0, 2.0), "powder": (0.0, 1.0),
          "alumina": (0.0, 1.0)}),
        ("Done: the head lifts; the mounts are rinsed at the sink and dried. On a tray it needs water, a drain and air.",
         1.8, {"head": (1.0, 0.0), "powder": (1.0, 0.0)}),
    ]
    inst.labels = [("power head", (hx - p["head_w"] / 2, hcy, hz + p["head_h"] * 0.7), (0.14, 0.22)),
                   ("7 in touchscreen", tuple(sc + np.array([SCREEN[0] / 2, 0, 0])), (0.86, 0.36)),
                   ("6-position holder", (hx - p["hold_d"] / 2, hy, hz_h), (0.12, 0.52)),
                   ("dispenser bottles", (rx, by - 120, 170), (0.12, 0.80))]
    inst.anchors = polisher_anchors(p)
    inst.cam = (0.7, -1.7, 0.8)
    inst.framing = (1.0, 0.40)
    near = ((hx + 40, hy - 40, dk - 10), 1350.0)                   # in on the holder, on the abrasive
    inst.zoom = {2: near, 3: "out", 5: near, 6: "out"}
    return inst


# register.py: the polisher's anchors, the parameters fitted to the SOP frames (refs/polisher/), and what keeps a
# fitted model buildable: the bowl inside the drum and the platen inside the bowl, below the lip; the screen on its
# slope with the e-stop under it; the housing reaching back over its column; the e-stop on the block.
ANCHORS["polisher"] = (POLISHER, polisher_anchors)
FREE["polisher"] = ["W", "deck", "drum_r", "platen_z", "block_k", "slope_z0", "slope_d", "scr_x", "scr_s", "estop_x",
                     "estop_z", "head_w", "head_h", "head_up", "hold_dx", "head_back"]
CHECKS["polisher"] = lambda p: [p["drum_r"] - p["rim_gap"] - p["lip_w"] - p["platen_d"] / 2 - 8, -p["platen_z"] - 15,
                                p["deck"] - p["slope_z0"] - 60, p["slope_z0"] - p["estop_z"] - 35, p["head_back"] - 60,
                                p["W"] / 2 - p["estop_x"] - 30]


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
# Malvern Panalytical Mastersizer 3000 with the Aero S dry powder disperser, as for metal powders. Published (Malvern's
# Mastersizer 3000 brochure): the optical bench 690 W x 300 D x 450 H mm, 30 kg; the Aero S 260 x 180 x 380 mm, 10.5 kg.
# The proportions in between are fitted with register.py (refs/mastersizer/) to frames of Malvern's own videos, "Mastersizer
# 3000 Aero Demo" (iaHJ8QEwJ-I) and "Measuring metal powders with the Mastersizer 3000" (6ZuKAAHb_20), the bench's
# 690 x 450 setting the scale. The look, from those frames: a satin silver-grey bench under a charcoal deck; a narrow
# bay a third of the way along holds the measurement cell's cassette, its front plate lettered AERO with a green LED
# and the fitting for the Aero S's hose, a lower block under it; MASTERSIZER runs up the left panel. The lower edges of
# both panels sweep down from the bay to the ends over a dark recessed plinth, so the plinth peaks under the bay. A
# round light-grey lid with a dark handle closes the cell from above; a raised teardrop runs right from it along the
# deck, a blue-lit oval sits left of it; a darker grey cap closes the right end; small adjustable feet. The Aero S
# stands in front of the left panel: a dark base and core, a silver shell sweeping down over its front, a blue LED at
# the front right of the base, a clear cover over the top that lifts off by hand ("Adjust Hopper", 0:52 of the Aero
# demo); under it a U-shaped carrier holds the vibrating tray, the black hopper standing over one end of it, the
# venturi at the other, and from the venturi a black hose runs to the cassette's fitting. The powder leaves the cell
# downwards, by a tube from under the bay, to a vacuum extractor (not in the frames; drawn as a generic unit).
MS3000 = dict(L=690.0, W=300.0, H=450.0, feet=15.0, deck=381.0, bay_x0=186.0, bay_w=102.0, cass_z0=189.0,
              z_cut=69.0, cap_w=24.0, dome_x=238.0, dome_y=141.0, dome_r=110.0, sw_x1=541.0, sw_y=130.0,
              fit_z=264.0, aero_l=260.0, aero_w=180.0, aero_h=380.0, aero_x=152.0, aero_y=138.0, cover_z=250.0,
              hop_x=79.0, hop_z=331.0, vac_w=330.0, vac_d=330.0, vac_h=480.0)


def _ms3000(p) -> dict:
    """The positions the model and its anchors share: the bench's ends, front and back, its bay, and the Aero S."""
    xl = -(p["L"] + 60 + p["vac_w"]) / 2             # the bench's left end; the extractor stands to its right
    yf = -p["W"] / 2 + p["aero_w"] / 2               # the bench's front; the Aero S stands in front of it
    bx0 = xl + p["bay_x0"]
    ax, ay = xl + p["aero_x"], yf - p["aero_y"]      # the Aero S's centre, aero_y in front of the bench
    return dict(xl=xl, xr=xl + p["L"], yf=yf, yb=yf + p["W"], bx0=bx0, bx1=bx0 + p["bay_w"],
                xp=xl + p["L"] - p["cap_w"],         # the right panel's right edge, where the end cap begins
                fx=bx0 + p["bay_w"] / 2,             # the cassette's hose fitting, on its front plate
                dx=xl + p["dome_x"], dy=yf + p["dome_y"], ax=ax, ay=ay,
                hx=ax - p["aero_l"] / 2 + p["hop_x"], hy=ay + 15.0)     # the hopper, over the tray


def mastersizer_anchors(p, pose=None) -> dict:
    """Named points and lines of the model, for register.py (the Aero S's only in views where it stands as here)."""
    g = _ms3000(p)
    xl, yf, yb, bx0, bx1, xp = g["xl"], g["yf"], g["yb"], g["bx0"], g["bx1"], g["xp"]
    dk, ft, zc = p["deck"], p["feet"], p["z_cut"]
    l, w = p["aero_l"], p["aero_w"]
    return {"top front left": (xl, yf, dk), "top back left": (xl, yb, dk), "top front right": (xp, yf, dk),
            "bay left top": (bx0, yf, dk), "bay right top": (bx1, yf, dk),
            "cassette bottom left": (bx0, yf, p["cass_z0"]), "cassette bottom right": (bx1, yf, p["cass_z0"]),
            "hose fitting": (g["fx"], yf - 10, p["fit_z"]),
            "cut at bay left": (bx0, yf, zc), "cut at bay right": (bx1, yf, zc), "bottom front left": (xl, yf, ft),
            "dome top": (g["dx"], g["dy"], p["H"]), "swoosh tip": (xl + p["sw_x1"], yf + p["sw_y"], dk + 8),
            "front top edge": ("line", (xl, yf, dk), (xp, yf, dk)), "back top edge": ("line", (xl, yb, dk), (xp, yb, dk)),
            "left cut": ("line", (xl, yf, ft), (bx0, yf, zc)), "right cut": ("line", (bx1, yf, zc), (xp, yf, ft)),
            "left edge": ("line", (xl, yf, ft), (xl, yf, dk)), "panel right edge": ("line", (xp, yf, ft), (xp, yf, dk)),
            "aero LED": (g["ax"] + l / 2 - 9.5, g["ay"] - w / 2 + 9.5, 48.0), "hopper top": (g["hx"], g["hy"], p["hop_z"])}


def _teardrop(c, r, tip_x, z, h) -> cq.Workplane:
    """A flat drop on z, h thick: round (radius r) behind c (x, y), and half an ellipse in front, out to tip_x."""
    a = tip_x - c[0]
    pts = [(c[0] + a * math.cos(t), c[1] + r * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, 30)]
    pts += [(c[0] - r * math.cos(t), c[1] + r * math.sin(t)) for t in np.linspace(math.pi / 2, -math.pi / 2, 30)[1:-1]]
    return cq.Workplane("XY").polyline(pts).close().extrude(h).translate((0, 0, z))


def mastersizer() -> Instrument:
    p = MS3000
    g = _ms3000(p)
    xl, xr, yf, yb, bx0, bx1, xp, fx = (g[k] for k in ("xl", "xr", "yf", "yb", "bx0", "bx1", "xp", "fx"))
    L, W, H, dk, ft, zc = p["L"], p["W"], p["H"], p["deck"], p["feet"], p["z_cut"]
    inst = Instrument("mastersizer", "Laser diffraction particle sizer", "Malvern Mastersizer 3000 + Aero S",
                      (L, W, H),
                      "Malvern Panalytical Mastersizer 3000 brochure (bench 690 x 300 x 450 mm, 30 kg; Aero S 260 x 180 "
                      "x 380 mm, 10.5 kg); proportions fitted with register.py to frames of Malvern's videos")
    body = _piece(inst, "body")
    # the bench: one silver shell to the deck, its front cut away below the panels' sweep down from the bay to the ends,
    # where a dark plinth shows, set back
    rec = 30.0
    shell = box(xl, yf, ft, xp, yb, dk).edges("|Z and <X").fillet(8)
    sweep = (cq.Workplane("XZ").polyline([(xl - 1, ft - 1), (xl - 1, ft), (bx0, zc), (bx1, zc), (xp + 1, ft),
                                          (xp + 1, ft - 1)]).close().extrude(-(rec + 1)).translate((0, yf - 1, 0)))
    body.add("bench", shell.cut(sweep), "inst_light")
    body.add("plinth", box(xl + 2, yf + rec - 1.5, ft, xp - 2, yf + rec, zc + 2), "inst_black")
    body.add("end cap", box(xp, yf - 3, ft, xr, yb, dk + 12).edges("|Z and >X").fillet(12), "inst_grey")
    body.add("deck", box(xl + 8, yf + 12, dk - 1, xp, yb - 8, dk + 2), "inst_dark")
    for sx in (xl + 30, xp - 30):
        for sy in (yf + 35, yb - 35):
            body.add(f"foot {sx:.0f} {sy:.0f}", cyl(30, ft, x=sx, y=sy), "chrome")
    # the cell's bay: the cassette's front plate (AERO, a green LED, the hose fitting), a lower block, dark joints
    body.add("bay joints", box(bx0 - 1.5, yf - 0.6, zc, bx0 + 1.5, yf + 1, dk).union(
        box(bx1 - 1.5, yf - 0.6, zc, bx1 + 1.5, yf + 1, dk)).union(
        box(bx0, yf - 0.6, p["cass_z0"] - 1.5, bx1, yf + 1, p["cass_z0"] + 1.5)), "inst_black")
    body.add("cassette plate", box(bx0 + 2, yf - 2, p["cass_z0"] + 2, bx1 - 2, yf, dk - 2), "inst_light")
    body.add("AERO lettering", box(bx0 + 14, yf - 2.4, p["fit_z"] + 30, bx0 + 22, yf - 2, dk - 40), "inst_grey")
    body.add("green LED", _ycyl(9, 2, x=bx0 + 18, y=yf - 2.5, z=dk - 25), "inst_green")
    body.add("cassette fitting", _ycyl(20, 10, x=fx, y=yf - 10, z=p["fit_z"]), "chrome")
    body.add("bay LED", box(bx0 + 4, yf - 1, zc + 6, bx0 + 45, yf, zc + 12), "led_blue")
    body.add("MASTERSIZER lettering", box(bx0 - 32, yf - 0.6, 110, bx0 - 22, yf, 330), "inst_grey")
    # on the deck: the round lid over the cell, with its handle; the raised teardrop running right; the blue oval
    dx, dy, R = g["dx"], g["dy"], p["dome_r"]
    top = H - 12 - (dk + 2 + 10)                                   # the lid's rise above its base ring
    prof = [(0, 0), (R, 0)] + [(R * math.cos(t), top * math.sin(t)) for t in np.linspace(0.15, math.pi / 2, 14)]
    lid = cq.Workplane("XZ").polyline(prof).close().revolve(360, (0, 0, 0), (0, 1, 0)).translate((dx, dy, dk + 12))
    body.add("lid ring", cyl(2 * R + 10, 10, x=dx, y=dy, z=dk + 2), "inst_light")
    body.add("cell lid", lid, "inst_light")
    body.add("lid handle", rbox(36, 1.5 * R, 26, 12, x=dx, y=dy - 0.15 * R, z=H - 26).edges(">Z").fillet(8),
             "inst_dark")
    body.add("swoosh", _teardrop((dx, yf + p["sw_y"]), 0.85 * R, xl + p["sw_x1"], dk + 2, 6),
             "inst_light")
    body.add("status light", cq.Workplane("XY").ellipse(32, 15).extrude(3).translate((dx - R - 32, dy - 15, dk + 2)),
             "led_blue")
    # the Aero S: dark base and core, the silver shell over the front and right; its blue LED at the front right
    ax, ay, hx, hy = g["ax"], g["ay"], g["hx"], g["hy"]
    l, w, h, cz = p["aero_l"], p["aero_w"], p["aero_h"], p["cover_z"]
    body.add("Aero S base", rbox(l, w, 45, 34, x=ax, y=ay), "inst_black")
    body.add("Aero S core", rbox(l - 10, w - 10, cz - 45, 38, x=ax, y=ay, z=45), "inst_dark")
    sweep_a = (cq.Workplane("XZ").polyline([(ax - l, cz - 25), (ax - l / 2, cz - 25), (ax + l / 2, 60), (ax + l, 60),
                                            (ax + l, 0), (ax - l, 0)]).close().extrude(-(w + 20))
               .translate((0, ay - w / 2 - 10, 0)))
    silver = rbox(l - 4, w - 4, cz - 45, 40, x=ax, y=ay, z=45).cut(sweep_a).cut(
        box(ax - l, ay + w / 2 - 45, 0, ax + l, ay + w, h))
    body.add("Aero S shell", silver, "inst_light")
    lc = (ax + l / 2 - 34, ay - w / 2 + 34)                         # the base's front corner, where the LED wraps
    body.add("Aero S LED", cq.Workplane("XY").circle(35.5).circle(33).extrude(6).translate((*lc, 45)).intersect(
        box(lc[0] + 4, lc[1] - 40, 40, lc[0] + 40, lc[1] - 4, 55)), "led_blue")
    body.add("Aero S deck", rbox(l - 14, w - 12, 6, 36, x=ax, y=ay, z=cz), "inst_light")
    # under the cover: the U-shaped carrier on its pillar, the hopper over the tray, the venturi and its hose
    ux = ax + 10
    body.add("tray carrier", rbox(190, 72, 18, 34, x=ux, y=hy, z=cz + 42).cut(rbox(160, 42, 20, 20, x=ux, y=hy,
                                                                                    z=cz + 41)).union(
        box(ux - 30, hy - 14, cz + 6, ux + 30, hy + 14, cz + 42)), "inst_light")
    body.add("hopper", cyl(46, p["hop_z"] - 14 - (cz + 62), x=hx, y=hy, z=cz + 62).union(
        cyl(30, 10, x=hx, y=hy, z=cz + 52)), "inst_black")
    body.add("hopper ring", cyl(54, 14, x=hx, y=hy, z=p["hop_z"] - 14), "inst_dark")
    vx_ = ax + 95                                                    # the venturi, at the tray's other end
    body.add("venturi", box(vx_ - 12, hy - 20, cz + 6, vx_ + 22, hy + 20, cz + 56), "steel")
    out = (ax + l / 2 + 4, hy, cz + 30)
    body.add("venturi outlet", _xcyl(22, ax + l / 2 + 6 - (vx_ + 22), x=vx_ + 22, y=hy, z=cz + 30), "chrome")
    body.add("sample hose", hose([out, (out[0] + 45, hy - 10, cz + 20), (fx - 10, yf - 60, p["fit_z"]),
                                  (fx, yf - 15, p["fit_z"])], 15), "inst_black")
    # inside the bay: the cell's body and its two windows across the beam (seen when the bench goes see-through)
    cy, bz = yf + 120, p["fit_z"] - 15
    body.add("cell", box(bx0 + 18, yf + 40, p["cass_z0"] - 40, bx1 - 18, yf + 200, dk - 30).cut(
        box(bx0 + 30, cy - 25, bz - 25, bx1 - 30, cy + 25, bz + 25)), "inst_dark")
    for x_ in (bx0 + 26, bx1 - 30):
        body.add(f"cell window {x_:.0f}", _xcyl(44, 4, x=x_, y=cy, z=bz), "window")
    # the extractor, and its hose from the cell's outlet under the bay
    vac_x = xr + 60 + p["vac_w"] / 2
    vac_y = (yf + yb) / 2
    body.add("vacuum extractor", rbox(p["vac_w"], p["vac_d"], p["vac_h"] - 120, 60, x=vac_x, y=vac_y, z=60),
             "inst_grey")
    body.add("extractor head", rbox(p["vac_w"] - 20, p["vac_d"] - 20, 60, 50, x=vac_x, y=vac_y, z=p["vac_h"] - 60),
             "inst_dark")
    body.add("extractor wheels", box(vac_x - p["vac_w"] / 2 + 30, vac_y - 120, 0, vac_x - p["vac_w"] / 2 + 70,
                                     vac_y + 120, 60).union(box(vac_x + p["vac_w"] / 2 - 70, vac_y - 120, 0,
                                                                vac_x + p["vac_w"] / 2 - 30, vac_y + 120, 60)),
             "inst_black")
    body.add("extract hose", hose([(fx, yf + rec + 8, zc - 25), (fx, yb + 45, 30), (vac_x - 90, yb + 45, 30),
                                   (vac_x - 90, yb + 45, p["vac_h"] - 40), (vac_x - 90, vac_y + 60, p["vac_h"] + 10)],
                                  34), "inst_black")
    # the clear cover, level-topped at the published height (its edges slope in the frames only with perspective)
    cover = _piece(inst, "lid")
    cv = rbox(l - 14, w - 8, h - cz, 44, x=ax, y=ay, z=cz).edges(">Z").fillet(30)
    cover.add("clear cover", cv.cut(rbox(l - 20, w - 14, h - cz - 3, 41, x=ax, y=ay, z=cz - 1)), "polycarb")
    tray = _piece(inst, "tray")
    tray.add("vibrating tray", box(hx - 22, hy - 13, cz + 50, vx_ - 10, hy + 13, cz + 53).union(
        box(hx - 22, hy - 13, cz + 53, vx_ - 10, hy - 11, cz + 60)).union(
        box(hx - 22, hy + 11, cz + 53, vx_ - 10, hy + 13, cz + 60)), "stainless")
    vial = _piece(inst, "vial")                                     # not a prop: it stands on the bench at rest
    vial.add("vial", cyl(28, 61, z=0).cut(cyl(25, 60, z=2)), "window")
    vial.add("powder in vial", cyl(25, 30, z=2), "powder")
    charge = _piece(inst, "powder")
    charge.add("powder in the hopper", cyl(38, 30, x=hx, y=hy, z=p["hop_z"] - 48), "powder")
    beam = _piece(inst, "beam")
    beam.add("laser", _xcyl(3, xp - 40 - (bx0 - 60), x=bx0 - 60, y=cy, z=bz), "laser")
    path = [(hx, hy, cz + 56), (vx_, hy, cz + 56), out, (out[0] + 45, hy - 10, cz + 20), (fx - 10, yf - 60, p["fit_z"]),
            (fx, yf - 15, p["fit_z"]), (fx, cy, p["fit_z"]), (fx, cy, p["cass_z0"] - 30)]
    seg = np.linalg.norm(np.diff(np.asarray(path), axis=0), axis=1)
    s = np.r_[0, np.cumsum(seg)]
    for i, t in enumerate(np.linspace(0.02, 0.98, 30) * s[-1]):
        k = min(int(np.searchsorted(s, t, side="right")) - 1, len(seg) - 1)
        q = np.asarray(path[k]) + (np.asarray(path[k + 1]) - path[k]) * (t - s[k]) / seg[k]
        beam.add(f"grain {i}", cq.Workplane("XY").sphere(4.0).translate(tuple(q + (0, 0, 3.0 * math.sin(i * 2.3)))),
                 "powder")
    buzz = tuple((2.5 * (-1) ** i, 0.0, 0.0) if 0 < i < 24 else (0.0, 0.0, 0.0) for i in range(25))
    inst.joints = {
        "lid": Joint("path", path=((0, 0, 0), (0, 0, 130), (-170, -60, 170))),           # lifted off by hand
        "vial": Joint("path", path=((fx + 170, yf - 150, 0), (fx + 170, yf - 150, h + 90), (hx, hy, h + 90),
                                    (hx, hy, p["hop_z"] + 25))),                         # from the bench to the hopper
        "powder": Joint("fade"),
        "tray": Joint("path", path=buzz),                                                 # the feeder's vibration
        "beam": Joint("fade"),
    }
    inst.actions = [
        ("The Aero S's clear cover lifts off; a few grams of atomized powder go into its hopper, over the vibrating "
         "tray.", 2.4, {"lid": (0.0, 1.0), "vial": (0.0, 1.0), "powder": (0.0, 0.0), "beam": (0.0, 0.0)}),
        ("The hopper's gap sets the feed; the cover goes back on.", 1.6, {"vial": (1.0, 0.0), "powder": (0.0, 1.0),
                                                                         "lid": (1.0, 0.0)}),
        ("Air on and the background measured, then the tray vibrates the powder into the venturi, and the air carries "
         "it down the hose to the cell in the bay, across the laser (drawn see-through).", 3.2,
         {"tray": (0.0, 1.0), "beam": (0.0, 1.0), "~body": (0.0, 1.0), "powder": (1.0, 0.0)}),
        ("The scattering gives the size distribution, 0.1 um to 3.5 mm, in under a minute; the extractor draws the "
         "powder away from under the cell.", 2.0, {"beam": (1.0, 0.0), "~body": (1.0, 0.0)}),
    ]
    inst.labels = [("Aero S dry disperser", (ax - l / 2, ay, h - 80), (0.12, 0.30)),
                   ("cell cassette", (fx, yf, dk - 60), (0.42, 0.10)),
                   ("optical bench", (xp - 150, yf, 300), (0.62, 0.80)),
                   ("vacuum extractor", (vac_x, vac_y - p["vac_d"] / 2, 300), (0.88, 0.55))]
    inst.anchors = mastersizer_anchors(p)
    inst.cam = (0.5, -1.7, 0.8)
    inst.zoom = {0: ((hx + 60, hy, cz + 40), 1700.0), 2: "out"}
    return inst


# register.py: the Mastersizer's anchors, the proportions fitted to Malvern's frames (refs/mastersizer/), and what keeps
# a fitted model buildable: the bay between two real panels, the cassette over its lower block, the lid's rise, the
# fitting on the cassette's plate, the hopper between the Aero S's deck and its cover.
ANCHORS["mastersizer"] = (MS3000, mastersizer_anchors)
FREE["mastersizer"] = ["deck", "bay_x0", "bay_w", "cass_z0", "z_cut", "cap_w", "dome_x", "dome_y", "sw_x1", "sw_y",
                       "fit_z", "aero_x", "aero_y", "hop_x", "hop_z"]
CHECKS["mastersizer"] = lambda p: [p["bay_x0"] - 120, p["L"] - p["cap_w"] - p["bay_x0"] - p["bay_w"] - 250,
                                   p["cass_z0"] - p["z_cut"] - 50, p["deck"] - p["cass_z0"] - 120, p["H"] - p["deck"] - 35,
                                   p["fit_z"] - p["cass_z0"] - 20, p["deck"] - p["fit_z"] - 40, p["cap_w"] - 8,
                                   p["aero_h"] - p["hop_z"] - 12,
                                   p["hop_z"] - p["cover_z"] - 75,
                                   p["aero_y"] - p["aero_w"] / 2 - 5]


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


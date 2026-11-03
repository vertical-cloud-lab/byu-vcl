"""Vertical lift module animations: a Kardex Shuttle XP 500 holding the lab's equipment on three electrified trays, a
UR arm on a mobile base working at its access opening.

    xvfb-run -a python3 animate.py assembly      # the machine goes together            -> out/vlm_assembly.gif, out/mp4/...
    xvfb-run -a python3 animate.py loading       # opaque, then see-through; the trays are loaded one piece at a time
    xvfb-run -a python3 animate.py workflow      # the arm doses a powder with the multi-doser and takes it to the CubXL
    xvfb-run -a python3 animate.py disassembly   # unloaded and taken apart
    python3 animate.py full                      # -> out/mp4/vertical_lab_full.mp4, the four joined
    PREVIEW=1 xvfb-run -a python3 animate.py workflow   # last frame of each sub-step -> /tmp/preview_*.png

``lab.py`` tessellates the models once and caches them in ``.cache/``. Every move is a real one: trays only move on
their supports, on the extractor or through the opening; equipment goes in and out through the opening; the arm's
moves are straight lines of its gripper solved with inverse kinematics every frame (``robot.py``); the multi-doser
indexes, docks, tilts and doses with its own kinematics (``carousel.py``).
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pyvista as pv

import lab
import props as P
import vlm as V
from scene import FPS, Scene, T, R, S

TITLE = "Vertical cloud lab: Kardex Shuttle XP 500 vertical lift module"
ROBOT = "ur10e"                 # chosen in reach.py: the one arm of the three that reaches every seat the workflow uses
ROBOT_NAME = {"ur3e": "UR3e", "ur7e": "UR7e", "ur10e": "UR10e"}[ROBOT]
LIFT_HOME = V.SLOTS["open"][1]
Z_BELT_TOP = V.Z_TOP_IN + 140
GREEN, OFF = (0.20, 0.85, 0.35), (0.30, 0.32, 0.30)
FLOOR_C = (0.965, 0.965, 0.96)
GHOST = {"vlm_skin": 0.16, "vlm_seam": 0.16, "vlm_bay": 0.22, "vlm_shutter": 0.35}   # see-through opacities
# the cell (#303, round 3): the rePowder atomizer just off the VLM's left side and the Aconity MIDI just off its right,
# both turned to face inward, across the space in front of the opening where the arm works. Each is placed by its own
# frame (front at -y): turned 90 deg, its front face 1450 mm from the centre line, its working end (the atomizer's
# chamber, the Aconity's process chamber) in front of the VLM's lip and its utilities (heat exchanger, filter) beside
# the VLM's front corner
REPOWDER_ROT, REPOWDER_AT = 90.0, (-1649.0, -2339.0, 0.0)      # front turned to +x
ACONITY_ROT, ACONITY_AT = -90.0, (2220.0, -2291.0, 0.0)        # front turned to -x
REPOWDER_LBL = ("AMAZEMET rePowder ultrasonic atomizer", (-1900.0, -2100.0, 1650.0), (0.10, 0.30))
ACONITY_LBL = ("Aconity MIDI metal LPBF (candidate)", (2070.0, -2000.0, 2350.0), (0.80, 0.30))

# what goes on each tray, in the tray's frame (centre of its floor, y to the back): (key, x, y), every item placed by
# the centre of its footprint. Printers and liquid handlers stand at the front edge, where they are reached; the vial
# rack and the multi-doser's station are within the arm's reach from its parking spot (reach.py)
LOADS = {
    "A": [("ot2", -700.0, -131.0), ("ot2", 0.0, -131.0), ("ot2", 700.0, -131.0)],
    "B": [("rack", 600.0, -372.0), ("carousel", 250.0, -316.0)],
    "C": [("cubxl", -760.0, -12.25), ("cubxl", 0.0, -12.25), ("cubxl", 760.0, -12.25)],
    "D": [("h2d", -560.0, -158.0), ("h2d", 0.0, -158.0), ("h2d", 560.0, -158.0)],
    "E": [("a2l", -620.0, -155.5), ("a2l", 0.0, -155.5), ("a2l", 620.0, -155.5)],
    "F": [("a1mini", -480.0, -267.5), ("a1mini", 0.0, -267.5), ("a1mini", 480.0, -267.5)],
}
ROLE = {"A": "liquid handling, OT-2s", "B": "powder dosing", "C": "liquid handling, CubXLs", "D": "3D printing, H2Ds",
        "E": "3D printing, A2Ls", "F": "3D printing, A1 minis"}
NAMES = {"ot2": "Opentrons OT-2", "cubxl": "CubXL liquid-handling gantry", "rack": "vial rack",
         "carousel": "multi-doser: chain carousel v2, 13 powders", "h2d": "Bambu Lab H2D", "a1mini": "Bambu Lab A1 mini",
         "a2l": "Bambu Lab A2L"}
SOURCE = {"ot2": "Opentrons' own reference STEP", "cubxl": "the lab's model from #199",
          "rack": "a printed rack for the doser's 20 mL vials",
          "carousel": "powder-doser PR #185's CAD, driven by its own kinematics",
          "h2d": "the lab's model from Bambu's spec", "a1mini": "the lab's model from Bambu's outline drawing",
          "a2l": "modelled from Bambu's published envelope"}
HOME = {"A": "R1", "B": "R2", "C": "F1", "D": "R3", "E": "R4", "F": "F0"}       # storage slot of each tray
CUB_WORK = 2                    # the CubXL the workflow uses: the right-hand one of tray C

# the mobile manipulator: a MiR250 parked square to the opening, 30 mm off the tray cover's 50 mm lip, the arm over
# its front half
AMR_XY = (0.0, -V.UNIT_D / 2 - V.SKIN - 50.0 - 30.0 - P.MIR["W"] / 2)
ARM_LOCAL = (0.0, 130.0)
RACK_N, RACK_PITCH = 5, 70.0                   # one row at 70 mm: room for the fingers of a side grasp between vials
RACK_SEAT = 0                                  # the rack's seat with the vial the workflow uses (the left-hand one)
# the rack stands right of the doser and the workflow uses the right-hand CubXL: with the gripper level and pointing
# into the tray, every grasp, transfer and approach then keeps the UR's wrist at least 245 mm off its base axis
# the vial stays upright all the way: the station takes it only from the side (its cup is under the funnel), so the
# arm grasps it from the side at the rack too, holds it while the VLM swaps trays, and stands it on a one-vial seat at
# the front of the CubXL's deck (a layout choice: the CubXL's own rack is too tight for fingers between its vials)
SIDE_Z = 46.0         # grasp height up the vial, the same everywhere: the 22 mm pads clear the rack's 32 mm holes and
#                       the cup's 18 mm, and stay under the vial's 61 mm mouth, where the funnel's spout goes in
CUB_SEAT = (130.0, -200.0, 86.0)               # the one-vial seat on the CubXL's deck (base of the vial), CubXL frame
MODULE = 5                                     # the powder module the workflow doses from (0-based; "module 6")
DOSE_G = 0.512

CAM_WIDE = [(3400, -10600, 6000), (0, -1100, 1550), (0, 0, 1)]
CAM_FRONT = [(1500, -9800, 2900), (0, -1200, 1750), (0, 0, 1)]
CAM_OPEN = [(1700, -7400, 3300), (100, -1000, 1400), (0, 0, 1)]
CAM_CELL = [(-300, -11800, 8200), (150, -1300, 1500), (0, 0, 1)]    # over the cell: the atomizer, the VLM, the Aconity
CAM_WORK = [(-1250, -4300, 2550), (60, -1450, 1060), (0, 0, 1)]
CAM_MID = [(1100, -3300, 2100), (245, -1320, 1170), (0, 0, 1)]      # on the way to CAM_DOSE, clear of the arm
CAM_DOSE = [(640, -1770, 1300), (245, -1330, 1180), (0, 0, 1)]      # at the station: the upright vial in its cup
CAM_CUB = [(1150, -3500, 2150), (820, -1380, 1000), (0, 0, 1)]


class Lab:
    """The scene plus the state of the machine: where each tray is, the extractor's height, the shutter."""

    def __init__(self, sc: Scene, data: dict, robot: bool = True, highlight: int | None = None):
        self.sc = sc
        self.highlight = highlight
        self.tray = {k: [*V.SLOTS[HOME[k]]] for k in V.TRAYS}      # [y, z] of each tray
        self.where = dict(HOME)                                     # slot name, or None in transit
        self.lift_z = LIFT_HOME
        self.shutter = 0.0
        self.eq_groups: dict[str, list[str]] = {k: [] for k in V.TRAYS}
        self.eq_key: dict[str, str] = {}
        self.show_gauges = True
        self.extra_gauges: list[tuple[str, str]] = []
        self.robot = None
        self._build(data, robot)

    # ---------------------------------------------------------------------------------- scene
    def _build(self, data, robot):
        sc = self.sc
        floor = pv.Plane(center=(0, -600, -1), direction=(0, 0, 1), i_size=16000, j_size=14000)
        sc.add("floor", floor, FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
        shadow = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=V.UNIT_W + 900, j_size=V.UNIT_D + 900)
        sc.add("floor shadow", shadow, (0.90, 0.90, 0.895), "floor", ambient=1.0, diffuse=0.0, specular=0.0,
               smooth_shading=False)
        self.ghost = {}
        for name, e in data["vlm"].items():
            kw = {}
            if e["material"] in GHOST:
                self.ghost[name] = GHOST[e["material"]]
            if e["material"] in ("vlm_skin", "vlm_bay"):
                kw = dict(specular=0.05, ambient=0.35)
            if e["material"] == "vlm_led":
                kw = dict(ambient=0.9, diffuse=0.2)
            sc.add(name, e["mesh"], e["color"], e["group"], opacity=e["opacity"], **kw)
        eq = data["equipment"]
        for k, loads in LOADS.items():
            for i, (key, x, y) in enumerate(loads):
                g = f"eq_{k}{i}"
                self.eq_key[g] = key
                if key == "carousel":
                    import carousel
                    self.carousel = carousel.Carousel(sc, g, prefix=g, highlight=self.highlight)
                    sc.gmat[g] = T((x, y, V.T_FLOOR)) @ R((0, 0, 1), 90)
                elif key == "rack":
                    self._rack(g)
                    sc.gmat[g] = T((x, y, V.T_FLOOR))
                elif key == "cubxl":
                    self._cubxl(g, eq, work=(i == CUB_WORK))
                    sc.gmat[g] = T((x, y, V.T_FLOOR)) @ self.cub_center
                else:
                    entries, bb = eq[key]
                    cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
                    for name, e in entries.items():
                        sc.add(f"{g}/{name}", e["mesh"].transform(T((-cx, -cy, -bb[4])), inplace=False), e["color"], g,
                               opacity=e["opacity"])
                    sc.gmat[g] = T((x, y, V.T_FLOOR))
                sc.parent[g] = f"tray_{k}"
                self.eq_groups[k].append(g)
        # the rePowder atomizer and its utilities just off the left side, the Aconity MIDI just off the right, both
        # facing inward
        for name, e in data["repowder"].items():
            sc.add(name, e["mesh"], e["color"], "repowder", opacity=e["opacity"])
        sc.gmat["repowder"] = T(REPOWDER_AT) @ R((0, 0, 1), REPOWDER_ROT)
        for name, e in eq["aconity"][0].items():
            sc.add(f"aconity/{name}", e["mesh"], e["color"], "aconity", opacity=e["opacity"])
        sc.gmat["aconity"] = T(ACONITY_AT) @ R((0, 0, 1), ACONITY_ROT)
        # the vial the workflow follows: in the rack's last seat at the start
        self._vial()
        if robot:
            self._amr()
        self.skin(1.0)(1.0)
        self.apply_state()

    def _rack(self, g):
        sc = self.sc
        block, seats = P.vial_rack(RACK_N, RACK_PITCH)
        sc.add(f"{g}/rack", block, P.RACK_C, g)
        self.rack_seats = seats
        glass = None
        for i, s in enumerate(seats):
            if i == RACK_SEAT:
                continue
            v = P.vial_glass().translate(s, inplace=False)
            glass = v if glass is None else glass.merge(v)
        sc.add(f"{g}/vials", glass, P.GLASS, g, opacity=0.45, specular=0.6)

    def _cubxl(self, g, eq, work=False):
        """The CubXL frame plus its gantry (y), carriage (x) and tools (z) as child groups, all in the frame's frame.
        The one the workflow uses (`work`) also gets the one-vial seat at the front of its deck."""
        sc = self.sc
        _, bb = eq["cubxl_frame"]
        cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
        self.cub_center = T((-cx, -cy, -bb[4]))
        for piece, parent in (("frame", None), ("gantry", g), ("carriage", f"{g}_gantry"), ("tools", f"{g}_carriage")):
            entries, _ = eq[f"cubxl_{piece}"]
            grp = g if piece == "frame" else f"{g}_{piece}"
            for name, e in entries.items():
                sc.add(f"{g}/{piece}/{name}", e["mesh"], e["color"], grp, opacity=e["opacity"])
            if parent:
                sc.parent[grp] = parent
                sc.gmat[grp] = np.eye(4)
        if work:
            # a printed block on the deck with a 14 mm hole the vial stands in (the vial hides the hole)
            seat = pv.Box(bounds=(CUB_SEAT[0] - 25, CUB_SEAT[0] + 25, CUB_SEAT[1] - 25, CUB_SEAT[1] + 25, 80.0,
                                  CUB_SEAT[2] + 14)).triangulate()
            sc.add(f"{g}/seat", seat, P.RACK_C, g)
            self.cub = g
            self.cub_xyz = [0.5, 0.5, 0.5]

    def _vial(self):
        sc = self.sc
        sc.add("vial/glass", P.vial_glass(), P.GLASS, "vial", opacity=0.55, specular=0.7)
        sc.add("vial/powder", P.fill(1.0), P.POWDER, "vial_powder")
        sc.add("vial/liquid", P.fill(1.0), P.LIQUID, "vial_liquid", opacity=0.85)
        sc.parent["vial_powder"] = "vial"
        sc.parent["vial_liquid"] = "vial"
        rack = self.eq_groups["B"][0]
        sc.parent["vial"] = rack
        sc.gmat["vial"] = T(self.rack_seats[RACK_SEAT])
        self.powder_h = 0.0
        self.liquid_h = 0.0
        self.set_fill()
        # the dose stream (points) and the pipette's stream (a thin tube), hidden until used
        sc.add("stream", pv.PolyData(np.zeros((40, 3))), (0.30, 0.30, 0.33), "stream", shown=False, style="points",
               point_size=4.5, render_points_as_spheres=True)
        sc.add("pipette stream", pv.Cylinder(center=(0, 0, 0.5), direction=(0, 0, 1), radius=1.2, height=1.0),
               P.LIQUID, "pstream", shown=False)

    def set_fill(self):
        sc = self.sc
        hp, hl = max(self.powder_h, 0.01), max(self.liquid_h, 0.01)
        sc.gmat["vial_powder"] = T((0, 0, P.VIAL_FLOOR)) @ S((1, 1, hp))
        sc.gmat["vial_liquid"] = T((0, 0, P.VIAL_FLOOR + self.powder_h)) @ S((1, 1, hl))
        sc.alpha["vial/powder"] = 1.0 if self.powder_h > 0.05 else 0.0
        sc.alpha["vial/liquid"] = 1.0 if self.liquid_h > 0.05 else 0.0

    def _amr(self):
        import robot as RB
        sc = self.sc
        for name, (mesh, col) in P.mir250().items():
            kw = dict(ambient=0.8) if "light" in name else {}
            sc.add(f"amr/{name}", mesh, col, "amr", **kw)
        sc.gmat["amr"] = T((*AMR_XY, 0))
        # parked: folded over its own base, the gripper pointing down
        self.robot = RB.Robot(sc, ROBOT, "amr", T((*ARM_LOCAL, P.AMR_TOP)), q0=PARK_DEG)

    # ---------------------------------------------------------------------------------- state
    def apply_state(self):
        sc = self.sc
        for k, (y, z) in self.tray.items():
            sc.gmat[f"tray_{k}"] = T((0, y, z))
            on = self.where[k] is not None
            sc.color[f"tray {k} lamp"] = GREEN if on else OFF
            sc.ambient[f"tray {k} lamp"] = 0.9 if on else 0.2
        sc.gmat["lift"] = T((0, 0, self.lift_z))
        L = max(1.0, Z_BELT_TOP - (self.lift_z + 40))
        sc.gmat["belts"] = T((0, 0, self.lift_z + 40)) @ S((1, 1, L))
        sc.gmat["shutter"] = T((0, 0, self.shutter * (V.Z_OPEN_TOP - V.Z_SILL + 10)))
        if self.robot is not None and self.robot.held is not None:
            self.robot.set()
        self.gauges()

    def gauges(self):
        g = []
        if not self.show_gauges:
            self.sc.gauges = []
            return
        for k in V.TRAYS:
            w = self.where[k]
            if w is None:
                state = "moving, unpowered"
            elif w == "open":
                state = "at the opening, powered"
            else:
                state = f"stored ({w}), powered"
            g.append((f"Tray {k}", f"{state}"))
        self.sc.gauges = g + self.extra_gauges

    def note(self, i, key, text):
        """Set line i of the workflow's status lines and redraw the table now (not at the next tray move)."""
        self.extra_gauges[i] = (key, text)
        self.gauges()

    def skin(self, f1):
        """Cladding from opaque (0) to see-through (1)."""
        sc = self.sc
        f0 = getattr(self, "_skin_f", 0.0)

        def up(u):
            self._skin_f = f0 + (f1 - f0) * u
            for n, ghost in self.ghost.items():
                sc.base_alpha[n] = 1.0 + (ghost - 1.0) * self._skin_f
        return up

    # ---------------------------------------------------------------------------------- moves
    def lift_to(self, z, carry=None):
        z0 = self.lift_z

        def up(u):
            self.lift_z = z0 + (z - z0) * u
            if carry:
                self.tray[carry][1] = self.lift_z
            self.apply_state()
        return up

    def slide(self, k, y1):
        y0 = self.tray[k][0]

        def up(u):
            self.tray[k][0] = y0 + (y1 - y0) * u
            self.apply_state()
        return up

    def shut(self, f1):
        f0 = self.shutter

        def up(u):
            self.shutter = f0 + (f1 - f0) * u
            self.apply_state()
        return up

    def fetch(self, k, label, caption, to="open", fast=1.0, cam=None, hold=0.4):
        """Extractor goes to tray k's slot, pulls it on, carries it to `to` and pushes it in."""
        sc = self.sc
        ys, zs = V.SLOTS[self.where[k]]
        yt, zt = V.SLOTS[to]
        if abs(self.lift_z - zs) > 1:
            sc.step(label, caption, max(0.6, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs), hold=0.1,
                    cam_to=cam)
            cam = None
        self.where[k] = None
        self.apply_state()
        sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.1, cam_to=cam)
        sc.step(label, caption, max(0.6, abs(zs - zt) / 1333 * fast), self.lift_to(zt, carry=k), hold=0.1)
        if to == "open":            # the shutter at the back of the bay opens to let the tray through, then shuts
            sc.step(label, caption, 0.7 * fast, self.shut(1.0), hold=0.0)
        sc.step(label, caption, 2.2 * fast, self.slide(k, yt), hold=0.0)
        if to == "open":
            sc.step(label, caption, 0.7 * fast, self.shut(0.0), hold=0.0)
        self.where[k] = to
        self.apply_state()
        sc.snap(max(1, int(round(hold * FPS))))

    def store(self, k, label, caption, fast=1.0, cam=None, hold=0.3):
        """Tray k from the opening back to its home slot."""
        self.where[k] = None
        self.apply_state()
        ys, zs = V.SLOTS[HOME[k]]
        self.sc.step(label, caption, 0.7 * fast, self.shut(1.0), hold=0.0, cam_to=cam)
        self.sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.0)
        self.sc.step(label, caption, 0.7 * fast, self.shut(0.0), hold=0.1)
        self.sc.step(label, caption, max(0.6, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs, carry=k), hold=0.1)
        self.sc.step(label, caption, 2.2 * fast, self.slide(k, ys), hold=0.0)
        self.where[k] = HOME[k]
        self.apply_state()
        self.sc.snap(max(1, int(round(hold * FPS))))

    # ---------------------------------------------------------------------------------- CubXL
    def cub_to(self, x=None, y=None, z=None):
        """CubXL carriage to (x, y, z), fractions of its 400 x 300 x 110 mm travel (lab_models.equipment.CUBXL)."""
        import equipment
        tr = equipment.CUBXL["travel"]
        x0, y0, z0 = self.cub_xyz
        x1, y1, z1 = (x0 if x is None else x), (y0 if y is None else y), (z0 if z is None else z)

        def up(u):
            xx, yy, zz = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, z0 + (z1 - z0) * u
            self.cub_xyz = [xx, yy, zz]
            self.sc.gmat[f"{self.cub}_gantry"] = T((0, (yy - 0.5) * tr[1], 0))
            self.sc.gmat[f"{self.cub}_carriage"] = T(((xx - 0.5) * tr[0], 0, 0))
            self.sc.gmat[f"{self.cub}_tools"] = T((0, 0, (zz - 0.5) * tr[2]))
        return up

    # ---------------------------------------------------------------------------------- visibility
    def groups(self, *pats):
        out = []
        for n, g in self.sc.group_of.items():
            if any(g == p or (p.endswith("*") and g.startswith(p[:-1])) for p in pats):
                out.append(n)
        return out

    def eq_names(self, g):
        """Every actor of equipment group g, its child groups (the CubXL's gantry, ...) included."""
        kids = [x for x in self.sc.gmat if x.startswith(g + "_")] + [g]
        return self.groups(*kids)


PARK_DEG = (-90.0, -150.0, 135.0, -75.0, -90.0, 0.0)    # folded over its base, facing the opening (q0 = -90: +y)


def both(*fs):
    def up(u):
        for f in fs:
            if f is not None:
                f(u)
    return up


def slide_in(L: Lab, groups, offset, names=None, out=False):
    """Groups slide along `offset` into place (or out of it) while fading in (or out)."""
    sc = L.sc
    base = {g: sc.gmat.get(g, np.eye(4)).copy() for g in groups}
    names = names if names is not None else L.groups(*groups)
    off = np.asarray(offset, float)

    def up(u):
        v = u if out else 1.0 - u
        for g in groups:
            sc.gmat[g] = T(off * v) @ base[g]
        for n in names:
            sc.alpha[n] = 1.0 - min(1.0, v * 1.6) if not out else max(0.0, 1.0 - v * 1.6)
    return up


def item_in(L: Lab, g, out=False, travel=1700.0):
    """One piece of equipment comes in through the opening onto its place (or goes out), 20 mm over the tray floor."""
    sc = L.sc
    base = sc.gmat[g].copy()
    names = L.eq_names(g) + (L.groups("vial", "vial_powder", "vial_liquid") if g == L.eq_groups["B"][0] else [])

    def up(u):
        v = u if out else 1.0 - u
        lift = min(1.0, v * 6) * 20.0
        sc.gmat[g] = T((0, -travel * v, lift)) @ base
        for n in names:
            if n.startswith("vial/") and n != "vial/glass":
                continue
            sc.alpha[n] = 1.0 if v < 0.7 else max(0.0, 1 - (v - 0.7) / 0.3)
    return up


def tray_world(k, xyz) -> np.ndarray:
    """A point in tray k's frame when the tray is at the opening, in world coordinates."""
    return np.array([xyz[0], V.Y_OPEN + xyz[1], V.Z_OPEN + xyz[2]])


# ======================================================================================= the arm's targets
def down(p, spin=90.0):
    """Gripper pointing straight down at p, its fingers closing along world y (across a rack's row)."""
    return P.tcp_frame(p, (0, 0, -1), spin)


def level(p, toward=(0, 1, 0), spin=0.0):
    """Gripper level, pointing along `toward`, its fingers closing sideways (world x)."""
    return P.tcp_frame(p, toward, spin)


def pick(L: Lab, rb, step, cap, M_grasp, M_pre, group, seconds=(1.6, 0.9, 0.5, 0.8), cam=None, labels=()):
    """Approach M_pre (joint move), line to M_grasp, close, take `group` with it, line back to M_pre."""
    sc = L.sc
    sc.step(step, cap, seconds[0], both(rb.joint_to(Tw=M_pre), rb.grip_to(0.0)), hold=0.05, cam_to=cam, labels=labels)
    sc.step(step, cap, seconds[1], rb.line_to(M_grasp), hold=0.05)
    sc.step(step, cap, seconds[2], rb.grip_to(GRIP_VIAL), hold=0.05)
    rb.grasp(group)
    sc.step(step, cap, seconds[3], rb.line_to(M_pre), hold=0.05)


def place(L: Lab, rb, step, cap, M_place, M_pre, new_parent, seconds=(1.6, 0.9, 0.5, 0.8), cam=None, labels=(),
          via=None):
    sc = L.sc
    if via is not None:
        sc.step(step, cap, seconds[0] * 0.6, rb.joint_to(Tw=via), hold=0.0, cam_to=cam, labels=labels)
        cam = None
    sc.step(step, cap, seconds[0], rb.joint_to(Tw=M_pre), hold=0.05, cam_to=cam, labels=labels if via is None else ())
    sc.step(step, cap, seconds[1], rb.line_to(M_place), hold=0.05)
    sc.step(step, cap, seconds[2], rb.grip_to(0.0), hold=0.05)
    rb.release(new_parent)
    sc.step(step, cap, seconds[3], rb.line_to(M_pre), hold=0.05)


GRIP_VIAL = 0.70               # 2F-85 closure with its pads 28 mm apart: the vial (ur_arm.gripper_fk)
GRIP_SIDE_OPEN = 0.36          # part open (about 55 mm) for a side grasp: the fingers fit between the rack's vials


# ======================================================================================= chapters
def new_scene(name, data, robot=True, highlight=None) -> tuple[Scene, Lab]:
    sc = Scene(name, TITLE)
    sc.cam = list(CAM_WIDE)
    L = Lab(sc, data, robot=robot, highlight=highlight)
    return sc, L


def hide(L: Lab, names):
    for n in names:
        L.sc.alpha[n] = 0.0


def assembly(data):
    sc, L = new_scene("vlm_assembly", data, robot=False)
    eq = [n for k in V.TRAYS for g in L.eq_groups[k] for n in L.eq_names(g)] + L.groups("vial", "vial_powder",
                                                                                          "vial_liquid")
    vlm_groups = ["base", "posts", "col_front", "col_rear", "lift_rails", "drive", "lift", "belts", "bay", "console",
                  "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top", *(f"tray_{k}" for k in V.TRAYS)]
    hide(L, L.groups(*vlm_groups) + eq)
    L.skin(0.0)(1.0)                 # the cladding goes on as it is: opaque
    L.show_gauges = False
    L.apply_state()
    n = 7
    sc.step(f"1/{n}", "The Kardex Shuttle XP 500 quoted in #53, between the lab's rePowder atomizer and an Aconity MIDI: "
            "2450 × 864 mm trays in a 2780 × 3074 mm module, 3950 mm tall to stay under 13 ft. The base frame goes down "
            "first, on levelling feet.",
            2.0, slide_in(L, ["base"], (0, 0, 900)), hold=1.2,
            labels=[("base frame, 2780 × 3074 mm", (V.UNIT_W / 2, -V.UNIT_D / 2, 100), (0.62, 0.82)), REPOWDER_LBL,
                    ACONITY_LBL])
    sc.step(f"2/{n}", "Posts and roof rails. The posts at the middle of each side mark off the three bays: front "
            "storage, the extractor's shaft and rear storage.",
            2.0, slide_in(L, ["posts"], (0, 0, 1800)), hold=1.0,
            labels=[("front storage", (V.UNIT_W / 2, V.Y_FRONT, V.UNIT_H), (0.83, 0.20)),
                    ("extractor shaft", (V.UNIT_W / 2, 0, V.UNIT_H), (0.86, 0.28)),
                    ("rear storage", (V.UNIT_W / 2, V.Y_REAR, V.UNIT_H), (0.88, 0.36))])
    sc.step(f"3/{n}", "Storage columns. Trays rest on supports on a 25 mm pitch (drawn every 100 mm here), so a tray "
            "takes only the height its equipment needs. The front column leaves a gap for the access opening.",
            2.4, slide_in(L, ["col_front", "col_rear"], (2600, 0, 0)), hold=1.4,
            labels=[("rear column: tray supports", (V.TRAY_W / 2, V.Y_REAR, 2600), (0.86, 0.30)),
                    ("front column", (V.TRAY_W / 2, V.Y_FRONT, 2600), (0.84, 0.48)),
                    ("gap for the opening", (V.TRAY_W / 2, V.Y_FRONT, 1300), (0.84, 0.66))])
    sc.step(f"4/{n}", "The extractor: guide rails in the shaft, the drive on the roof frame (motor, cross shaft, two "
            "belt pulleys), then the platform on its belts. It carries one tray at a time.",
            2.6, both(slide_in(L, ["lift_rails"], (0, 0, 2500)), slide_in(L, ["drive"], (0, 0, 1400)),
                      slide_in(L, ["lift", "belts"], (0, 0, 2400))), hold=1.4,
            labels=[("drive on the roof frame", (V.UNIT_W / 2 - 700, 0, V.Z_TOP_IN + 150), (0.80, 0.16)),
                    ("extractor platform", (V.TRAY_W / 2, 0, LIFT_HOME - 60), (0.86, 0.62))])
    trays_lbl = [(f"tray {k}: {V.TRAYS[k]['kind']}, {V.TRAYS[k]['capacity_lb']} lb", (V.TRAY_W / 2, *V.SLOTS[HOME[k]]),
                  (0.88, 0.14 + 0.115 * i)) for i, k in enumerate(V.TRAYS)]
    sc.step(f"5/{n}", "Six electrified trays: #53's strong (1080 lb), medium (794 lb) and light (502 lb) ones, and three "
            "more light ones for the equipment here. Each has a power strip and a socket; it has power in its slot and at "
            "the opening, not while it moves.",
            2.6, slide_in(L, [f"tray_{k}" for k in V.TRAYS], (3200, 0, 0)), hold=1.8, labels=trays_lbl)
    sc.step(f"6/{n}", f"Cladding in RAL 7035 and the access opening, {V.OPEN_W:.0f} mm wide at a {V.Z_SILL:.0f} mm table: "
            "header with the LED light, side posts, the OPTIC panel on the right post, and the powered safety shutter "
            "at the back of the bay, which closes whenever the extractor moves.",
            2.6, both(slide_in(L, ["skin_L"], (-900, 0, 0)), slide_in(L, ["skin_R"], (900, 0, 0)),
                      slide_in(L, ["skin_back"], (0, 900, 0)), slide_in(L, ["skin_top"], (0, 0, 900)),
                      slide_in(L, ["skin_front", "bay", "console", "shutter"], (0, -900, 0))), hold=1.4,
            labels=[("large access opening", (0, -V.UNIT_D / 2, V.Z_SILL + 500), (0.20, 0.62)),
                    ("operator console", (V.CONSOLE_X, -V.UNIT_D / 2 - 120, V.CONSOLE_Z), (0.84, 0.70)),
                    ("blue cover under the tray", (-900, -V.UNIT_D / 2 - 60, V.Z_SILL - 60), (0.18, 0.80))])
    sc.step(f"7/{n}", "Assembled: from outside, a closed cabinet with one opening. Next: what goes inside.",
            2.0, None, hold=2.5, cam_to=CAM_FRONT, still=True)
    return sc.save()


def tray_items(L: Lab, k):
    """[(group, key, x, y)] of tray k, in loading order."""
    return [(g, key, x, y) for g, (key, x, y) in zip(L.eq_groups[k], LOADS[k])]


def load_tray(L: Lab, k, step, out=False):
    """Every piece of equipment of tray k goes in through the opening one at a time (or out, in reverse). The first of
    a kind takes its time and gets a label; the copies after it are quicker."""
    sc = L.sc
    items = tray_items(L, k)
    if out:
        items = items[::-1]
    seen = set()
    for g, key, x, y in items:
        count = sum(1 for kk, _, _ in LOADS[k] if kk == key)
        first = key not in seen
        seen.add(key)
        if out:
            cap = f"Unloading tray {k} ({ROLE[k]}): the equipment goes out through the opening, one piece at a time."
            sc.step(step, cap, 1.3 if first else 1.0, item_in(L, g, out=True), hold=0.15)
            continue
        what = f"{count} × {NAMES[key]}" if count > 1 else f"the {NAMES[key]}"
        cap = f"Tray {k}: {what} goes in through the opening, one at a time ({SOURCE[key]})."
        lbl = [(f"{count} × {NAMES[key]}" if count > 1 else NAMES[key], tray_world(k, (x, y, 560)),
                (0.72 if x > 0 else 0.22, 0.22))] if first else []
        sc.step(step, cap, 1.9 if first else 1.2, item_in(L, g), hold=0.5 if first else 0.2, labels=lbl)


def loading(data):
    sc, L = new_scene("vlm_loading", data)
    rb = L.robot
    eq = [n for k in V.TRAYS for g in L.eq_groups[k] for n in L.eq_names(g)] + L.groups("vial", "vial_powder",
                                                                                          "vial_liquid")
    hide(L, eq + L.groups("amr", *rb.groups()))
    L.skin(0.0)(1.0)
    L.apply_state()
    sc.cam = list(CAM_FRONT)
    order = ("A", "B", "C", "D", "E", "F")
    n = len(order) + 3
    sc.step(f"1/{n}", "The Kardex Shuttle XP 500 as it would stand in the lab: a closed cabinet, 2780 mm wide, 3074 mm "
            "deep and 3950 mm tall, with one large access opening at counter height. The rePowder ultrasonic atomizer "
            "stands just off its left side and the Aconity MIDI metal printer just off its right, both facing inward.",
            3.4, None, hold=1.2, cam_to=CAM_CELL,
            labels=[("large access opening", (0, -V.UNIT_D / 2 - V.SKIN, V.Z_SILL + 400), (0.50, 0.70)),
                    REPOWDER_LBL, ACONITY_LBL])
    sc.step(f"2/{n}", "Inside, drawn see-through from here on: the front storage column, the extractor's shaft and the "
            "rear storage column, with six empty trays in their slots.",
            2.4, L.skin(1.0), hold=1.2, cam_to=CAM_WIDE,
            labels=[("front storage", (V.TRAY_W / 2, V.Y_FRONT, 2900), (0.84, 0.30)),
                    ("extractor", (V.TRAY_W / 2, 0, LIFT_HOME - 40), (0.88, 0.52)),
                    ("rear storage", (V.TRAY_W / 2, V.Y_REAR, 3300), (0.88, 0.20))])
    for i, k in enumerate(order):
        step = f"{3 + i}/{n}"
        cap0 = f"Loading tray {k} ({ROLE[k]}): the extractor brings it to the opening; the shutter behind the " \
               "opening lets it through and closes behind it."
        L.fetch(k, step, cap0, fast=0.6, cam=CAM_OPEN if i == 0 else None, hold=0.2)
        load_tray(L, k, step)
        L.store(k, step, f"Tray {k} goes back to its slot ({HOME[k]}), where it has power again.", fast=0.6,
                cam=CAM_WIDE if i == len(order) - 1 else None, hold=0.2)
    cap = f"The operator rolls up: a Universal Robots {ROBOT_NAME} with a Robotiq 2F-85 gripper on a MiR250 mobile " \
          f"base, parked square to the opening. Its {ur_reach():.0f} mm reach covers every seat it works on from here."
    sc.step(f"{n - 1}/{n}", cap, 2.6, slide_in(L, ["amr"], (0, -2200, 0), names=L.groups("amr", *rb.groups())),
            hold=1.0, cam_to=CAM_OPEN,
            labels=[(f"{ROBOT_NAME} on a MiR250", (AMR_XY[0], AMR_XY[1], 1300), (0.16, 0.42))])
    sc.step(f"{n}/{n}", "Loaded, 16 pieces on six powered trays: three OT-2s, the multi-doser, three CubXLs, three H2Ds, "
            "three A2Ls and three A1 minis, each tray powered in its slot so its equipment keeps running while stored.",
            1.6, None, hold=2.6, cam_to=CAM_WIDE, still=True,
            labels=[(f"tray {k}: {ROLE[k]}", (V.TRAY_W / 2 - 300, *V.SLOTS[HOME[k]]), (0.88, 0.14 + 0.115 * i))
                    for i, k in enumerate(V.TRAYS)])
    return sc.save()


def stream_points(L: Lab, t: float, on: float) -> np.ndarray:
    """The dose stream from the auger's outlet to the vial, in the rig's frame: grains falling under gravity."""
    import carousel as C
    car = L.carousel
    top = car.exit_point()
    bottom_z = C.VIAL_Z + P.VIAL_FLOOR + L.powder_h + 2.0
    n = 40
    s = (np.arange(n) / n + t * 1.7) % 1.0
    s = s[s < on]
    if not len(s):
        return np.zeros((0, 3))
    seat = C.vial_seat()
    x = top[0] + (seat[0] - top[0]) * s ** 0.5
    y = np.full_like(s, top[1]) + np.sin(np.arange(len(s)) * 2.3) * 1.2
    z = top[2] - (top[2] - bottom_z) * s ** 2
    return np.c_[x, y, z]


def workflow(data):
    import carousel as C
    sc, L = new_scene("vlm_workflow", data, highlight=MODULE)
    rb, car = L.robot, L.carousel
    sc.cam = list(CAM_WIDE)
    L.extra_gauges = [("Arm", f"{ROBOT_NAME}, parked"), ("Doser", "module 1 at the station"),
                      ("Load cell", "0.000 g")]
    L.apply_state()
    n = 6
    # ------------------------------------------------------------------ 1. tray B down
    cap = "An example run: dose 0.5 g of a powder from the multi-doser, then add liquid to it in a CubXL. The arm " \
          "asks for tray B: the extractor pulls it off its supports, carries it down and pushes it into the opening."
    sc.step(f"1/{n}", cap, 1.0, None, hold=0.5,
            labels=[("tray B: powder dosing", (V.TRAY_W / 2 - 300, *V.SLOTS[HOME["B"]]), (0.86, 0.34))])
    L.fetch("B", f"1/{n}", cap, cam=CAM_WORK)
    # ------------------------------------------------------------------ 2. an empty vial into the doser, upright
    rack_xy = LOADS["B"][0][1:]
    seat = np.array(L.rack_seats[RACK_SEAT]) + (*rack_xy, V.T_FLOOR)
    p_rack = tray_world("B", seat + (0, 0, SIDE_Z))
    car_xy = LOADS["B"][1][1:]
    vs = C.vial_seat()                                       # rig frame; the rig is turned 90 deg on the tray
    cup = np.array([car_xy[0] - vs[1], car_xy[1] + vs[0], V.T_FLOOR + vs[2]])
    p_cup = tray_world("B", cup + (0, 0, SIDE_Z))
    lift = (0, 0, 45.0)                                      # clears the rack's 32 mm holes
    cap = f"The {ROBOT_NAME} takes an empty 20 mL vial from the rack at the front of the tray, from the side, so it " \
          "stays upright: the station's cup is under its funnel, and the vial only goes in from the front, mouth up."
    L.note(0, "Arm", "vial: rack to doser, upright")
    sc.step(f"2/{n}", cap, 1.6, both(rb.joint_to(Tw=level(p_rack + (0, -170, 0))), rb.grip_to(GRIP_SIDE_OPEN)),
            hold=0.05, cam_to=CAM_WORK,
            labels=[("vial rack", p_rack + (150, 0, 60), (0.80, 0.30)),
                    ("multi-doser (powder-doser #185)", p_cup + (0, 150, 420), (0.70, 0.18))])
    sc.step(f"2/{n}", cap, 0.9, rb.line_to(level(p_rack)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.5, rb.grip_to(GRIP_VIAL), hold=0.05)
    rb.grasp("vial")
    sc.step(f"2/{n}", cap, 0.6, rb.line_to(level(p_rack + lift)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.7, rb.line_to(level(p_rack + lift + (0, -170, 0))), hold=0.05)
    cap = "It carries the vial level, upright all the way, to the front of the station and slides it into the cup " \
          "on the 100 g load cell, its mouth under the funnel's spout."
    sc.step(f"2/{n}", cap, 1.4, rb.line_to(level(p_cup + (0, -190, 6))), hold=0.05)
    sc.step(f"2/{n}", cap, 1.0, rb.line_to(level(p_cup + (0, 0, 6))), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.line_to(level(p_cup)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.5, rb.grip_to(GRIP_SIDE_OPEN), hold=0.05)
    rb.release(L.eq_groups["B"][1])
    sc.step(f"2/{n}", cap, 0.9, rb.line_to(level(p_cup + (0, -190, 0))), hold=0.05, cam_to=CAM_MID)
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(PARK_RAD), hold=0.1)
    L.note(0, "Arm", "parked, clear of the doser")
    # ------------------------------------------------------------------ 3. dose
    cap = f"The carousel indexes powder module {MODULE + 1} (green) to the station, 8 chain links per module, and the " \
          "Actuonix P16 lifts the electronics carriage and docks it under the module's plate, magnet on."
    L.note(1, "Doser", f"indexing to module {MODULE + 1}")
    sc.step(f"3/{n}", cap, 2.6, car.to(shift=car.index_to(MODULE)), hold=0.2, cam_to=CAM_DOSE,
            labels=[(f"module {MODULE + 1}", p_cup + (0, 80, 90), (0.74, 0.20))])
    L.note(1, "Doser", f"module {MODULE + 1} docking")
    cap = cap + " The other modules are drawn see-through: the docked one rides inside the loop."
    sc.step(f"3/{n}", cap, 1.4, both(car.to(ext=C.DOCK_EXT, magnet_on=True), car.ghost(0.18)), hold=0.2)
    cap = f"Module {MODULE + 1} tilts {C.CP.TILT_DOSE_WORLD:.0f}°, cap end up into the loop, and the auger turns through " \
          "the steel pinion: the powder drops through the D-cut funnel into the upright vial while the load cell counts " \
          "it. Then hold, tilt back, reverse one turn at rest, undock (powder-doser's leakage study)."
    L.note(1, "Doser", f"module {MODULE + 1} tilted, dosing")
    sc.step(f"3/{n}", cap, 1.6, car.to(tilt=C.TILT), hold=0.1)
    spin0 = car.state["spin"]
    st = car.to(spin=spin0 + 2 * math.pi * 2.0)

    def dose(u):
        st(u)
        on = 1.0 if 0.05 < u < 0.95 else 0.0
        pts = stream_points(L, u * 6.0, on)
        sc.alpha["stream"] = 1.0 if len(pts) else 0.0
        if len(pts):
            sc.set_mesh("stream", pv.PolyData(pts))
        L.powder_h = 14.0 * min(1.0, max(0.0, (u - 0.12) / 0.83))
        L.set_fill()
        L.note(2, "Load cell", f"{DOSE_G * min(1.0, max(0.0, (u - 0.12) / 0.83)):.3f} g")
    sc.parent["stream"] = L.eq_groups["B"][1]
    sc.step(f"3/{n}", cap, 3.6, dose, hold=0.4, live=False, still=True)
    sc.alpha["stream"] = 0.0
    L.note(1, "Doser", f"module {MODULE + 1} back, undocking")
    sc.step(f"3/{n}", cap, 1.2, car.to(tilt=0.0), hold=0.1)
    sc.step(f"3/{n}", cap, 0.8, car.to(spin=spin0 + 2 * math.pi), hold=0.1)
    sc.step(f"3/{n}", cap, 1.0, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0)), hold=0.2)
    L.note(1, "Doser", f"module {MODULE + 1} undocked")
    # ------------------------------------------------------------------ 4. the arm holds the vial; tray B up, tray C down
    wait = level(p_cup + (0, -380, 60))                      # out of the bay, so the tray can go
    cap = f"The arm takes the vial out of the cup ({DOSE_G:.3f} g in it), still upright, and holds it clear of the " \
          "opening while the VLM swaps trays: tray B goes back to its slot and its power."
    L.note(0, "Arm", "holding the vial")
    sc.step(f"4/{n}", cap, 1.2, both(rb.joint_to(Tw=level(p_cup + (0, -190, 0))), rb.grip_to(GRIP_SIDE_OPEN)),
            hold=0.05, cam_to=CAM_WORK)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(level(p_cup)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.5, rb.grip_to(GRIP_VIAL), hold=0.05)
    rb.grasp("vial")
    sc.step(f"4/{n}", cap, 0.4, rb.line_to(level(p_cup + (0, 0, 6))), hold=0.0)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(level(p_cup + (0, -190, 6))), hold=0.05)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(wait), hold=0.1)
    L.store("B", f"4/{n}", cap, cam=CAM_OPEN)
    # ------------------------------------------------------------------ 5. tray C down, vial onto the CubXL's deck
    cap = "Tray C (liquid handling: three CubXLs) comes down. The right-hand CubXL's gantry parks at the back, so the " \
          "arm can stand the vial on the one-vial seat at the front of its deck."
    L.fetch("C", f"5/{n}", cap, cam=CAM_CUB)
    sc.step(f"5/{n}", cap, 1.0, L.cub_to(x=0.2, y=1.0, z=1.0), hold=0.2)
    base = (sc.world(L.cub) @ np.r_[CUB_SEAT, 1.0])[:3]          # tray C is at the opening now
    p_seat = base + (0, 0, SIDE_Z)
    L.note(0, "Arm", "vial: to the CubXL")
    sc.step(f"5/{n}", cap, 1.4, rb.line_to(level(p_seat + (0, -190, 20))), hold=0.05,
            labels=[("CubXL: one-vial seat", p_seat + (0, 0, 60), (0.74, 0.24))])
    sc.step(f"5/{n}", cap, 1.0, rb.line_to(level(p_seat + (0, 0, 20))), hold=0.05)
    sc.step(f"5/{n}", cap, 0.6, rb.line_to(level(p_seat)), hold=0.05)
    sc.step(f"5/{n}", cap, 0.5, rb.grip_to(GRIP_SIDE_OPEN), hold=0.05)
    rb.release(L.cub)
    sc.step(f"5/{n}", cap, 0.9, rb.line_to(level(p_seat + (0, -190, 0))), hold=0.05)
    sc.step(f"5/{n}", cap, 1.4, both(rb.joint_to(PARK_RAD), rb.grip_to(0.0)), hold=0.1)
    L.note(0, "Arm", "parked")
    # ------------------------------------------------------------------ 6. CubXL adds liquid; tray C up
    cap = "The CubXL's gantry brings its pipette over the vial and adds the liquid; the vial stays there for the " \
          "measurement. Tray C goes back to its slot, where it has power, so the CubXL keeps working while it is stored."
    import equipment
    tr = equipment.CUBXL["travel"]
    px = (CUB_SEAT[0] + 50.0 + tr[0] / 2) / tr[0]                       # pipette at cx - 50 (equipment.cubxl)
    py = (CUB_SEAT[1] + 80.0 + equipment.CUBXL["D"] / 2 - 150.0) / tr[1]   # pipette at gy - 80
    sc.step(f"6/{n}", cap, 2.0, L.cub_to(x=px, y=py), hold=0.1, cam_to=CAM_CUB,
            labels=[("CubXL pipette", p_seat + (0, 0, 260), (0.74, 0.24))])
    sc.step(f"6/{n}", cap, 1.0, L.cub_to(z=0.55), hold=0.1)
    tip = lambda: (sc.world(f"{L.cub}_tools") @ np.r_[CUB_SEAT[0], CUB_SEAT[1], 100.0 + 0.5 * tr[2] - 40.0, 1.0])[:3]  # noqa: E731

    def pour(u):
        L.liquid_h = 22.0 * u
        L.set_fill()
        on = 0.08 < u < 0.95
        sc.alpha["pipette stream"] = 1.0 if on else 0.0
        if on:
            top = tip()
            bot = (sc.world("vial") @ np.r_[0, 0, P.VIAL_FLOOR + L.powder_h + L.liquid_h, 1.0])[:3]
            sc.gmat["pstream"] = T(bot) @ S((1, 1, max(1.0, top[2] - bot[2])))
    sc.step(f"6/{n}", cap, 2.2, pour, hold=0.3)
    sc.alpha["pipette stream"] = 0.0
    sc.step(f"6/{n}", cap, 1.0, L.cub_to(z=1.0), hold=0.1)
    L.store("C", f"6/{n}", cap, cam=CAM_WIDE)
    L.note(0, "Arm", "parked; next request")
    sc.step(f"6/{n}", "Done: the dosed vial is in the CubXL on tray C, in storage and powered. The arm and the opening "
            "are free for the next request.", 1.0, None, hold=2.5)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; opening top {V.Z_OPEN_TOP:.0f} mm", flush=True)
    return sc.save()


def disassembly(data):
    sc, L = new_scene("vlm_disassembly", data)
    rb = L.robot
    L.skin(1.0)(1.0)
    L.apply_state()
    n = 6
    sc.step(f"1/{n}", "Taking it down is the assembly in reverse. The mobile manipulator drives away first.", 1.8,
            slide_in(L, ["amr"], (0, -2200, 0), out=True, names=L.groups("amr", *rb.groups())), hold=0.6)
    for i, k in enumerate(("F", "E", "D", "C", "B", "A")):
        step = f"2/{n}"
        cap = f"Unloading tray {k} ({ROLE[k]}): it comes to the opening and the equipment goes out through it, one " \
              "piece at a time."
        L.fetch(k, step, cap, fast=0.55, cam=CAM_OPEN if i == 0 else None, hold=0.15)
        load_tray(L, k, step, out=True)
        L.store(k, step, cap, fast=0.55, hold=0.15)
    L.show_gauges = False
    L.apply_state()
    sc.step(f"3/{n}", "The cladding, the opening's posts, header and cover, the console and the shutter come off.",
            2.4, both(slide_in(L, ["skin_L"], (-900, 0, 0), out=True), slide_in(L, ["skin_R"], (900, 0, 0), out=True),
                      slide_in(L, ["skin_back"], (0, 900, 0), out=True), slide_in(L, ["skin_top"], (0, 0, 900), out=True),
                      slide_in(L, ["skin_front", "bay", "console", "shutter"], (0, -900, 0), out=True)),
            hold=0.8, cam_to=CAM_WIDE)
    sc.step(f"4/{n}", "The trays slide out of their slots.", 2.0,
            slide_in(L, [f"tray_{k}" for k in V.TRAYS], (3200, 0, 0), out=True), hold=0.6)
    sc.step(f"5/{n}", "The extractor platform, its drive and its guide rails come out.", 2.4,
            both(slide_in(L, ["lift_rails"], (0, 0, 2500), out=True), slide_in(L, ["drive"], (0, 0, 1400), out=True),
                 slide_in(L, ["lift", "belts"], (0, 0, 2400), out=True)), hold=0.6)
    sc.step(f"6/{n}", "The storage columns, the posts and roof rails, and last the base frame.", 2.0,
            slide_in(L, ["col_front", "col_rear"], (2600, 0, 0), out=True), hold=0.3)
    sc.step(f"6/{n}", "The storage columns, the posts and roof rails, and last the base frame.", 2.4,
            both(slide_in(L, ["posts"], (0, 0, 1800), out=True), slide_in(L, ["base"], (0, 0, 900), out=True)),
            hold=1.5)
    return sc.save()


def scale(data):
    """Scaling up (scale.py): eight Shuttle XP 500s 15.15 m tall in two rows, served by a UR10e on a floor rail."""
    import robot as RB
    import scale as SC
    sc = Scene("vlm_scale", "Scaling up: Kardex Shuttle XP 500s at 15.15 m, served by a UR10e on a rail")
    sc.add("floor", pv.Plane(center=(0, 0, -1), direction=(0, 0, 1), i_size=60000, j_size=60000), FLOOR_C, "floor",
           ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    tmpl = SC.tray_templates(data, LOADS)
    shell = SC.unit_shell()
    tall = SC.slots()
    units = [(1, 1), (1, 0), (1, 2), (1, 3), (0, 0), (0, 1), (0, 2), (0, 3)]     # the first is the one that grows
    # the tray each unit brings down: one high up, one low, and so on, so the extractors run different distances
    pick = {u: k for u, k in zip(units, (len(tall) // 2 - 2, 12, 3, len(tall) // 2 - 6, len(tall) // 2 - 10, 7,
                                         len(tall) // 2 - 4, 20))}
    grow_parts, ghosts, bands = [], {}, []
    for r, i in units:
        g = f"u{r}{i}"
        sc.gmat[g] = SC.unit_xform(r, i)
        for name, (mesh, col, ghost, grow) in shell.items():
            grp = g if grow is None else f"{g}_g_{name}"
            if grow is not None:
                sc.parent[grp] = g
                grow_parts.append((grp, grow))
            kw = dict(specular=0.05, ambient=0.35) if name.startswith("skin") else {}
            if name == "LED light":
                kw = dict(ambient=0.9, diffuse=0.2)
            sc.add(f"{g}/{name}", mesh, col, grp, opacity=ghost if name == "shutter" else 1.0, smooth_shading=False,
                   **kw)
            if ghost is not None and name != "shutter":
                ghosts[f"{g}/{name}"] = ghost
        by: dict = {}
        grower = (r, i) == units[0]
        for k, (y, z, kind) in enumerate(tall):
            if k == pick[(r, i)]:
                continue
            band = int((z + SC.KIND_H[kind]) // 1500) if grower else 0    # the growing unit's trays, in height bands
            for key, m in tmpl[kind].items():
                by.setdefault((band, *key), []).append(m.translate((0, y, z), inplace=False))
        for j, ((band, col, op), ms) in enumerate(sorted(by.items())):
            sc.add(f"{g}/trays/{j}", pv.merge(ms, merge_points=False), col, f"{g}_trays", opacity=op,
                   smooth_shading=col != tuple(V.MATERIALS["vlm_tray"][:3]))
            if grower:
                bands.append((f"{g}/trays/{j}", (band + 1) * 1500.0))
        sc.parent[f"{g}_trays"] = g
        y, z, kind = tall[pick[(r, i)]]
        for j, ((col, op), m) in enumerate(sorted(tmpl[kind].items())):
            sc.add(f"{g}/tray/{j}", m, col, f"{g}_tray", opacity=op, smooth_shading=col != tuple(V.MATERIALS["vlm_tray"][:3]))
        sc.parent[f"{g}_tray"] = g
        sc.gmat[f"{g}_tray"] = T((0, y, z))
        sc.add(f"{g}/lift", SC.extractor_mesh(), V.MATERIALS["vlm_lift"][:3], f"{g}_lift", smooth_shading=False)
        sc.parent[f"{g}_lift"] = g
        sc.gmat[f"{g}_lift"] = T((0, 0, z))
    n_trays, n_inst = len(tall) * len(units), 3 * len(tall) * len(units)
    # the rail and the arm on its carriage
    span = SC.N_ROW * SC.PITCH_X + 1200
    for part, items in SC.rail_meshes(span).items():
        for name, (mesh, col) in items.items():
            sc.add(f"{part}/{name}", mesh, col, part, smooth_shading=False,
                   **(dict(ambient=0.8) if "light" in name else {}))
    car_x = [SC.unit_xform(1, SC.N_ROW - 1)[0, 3] + 1200.0]
    sc.gmat["carriage"] = T((car_x[0], 0, 0))
    rb = RB.Robot(sc, ROBOT, "carriage", T((0, 0, SC.RAIL_Z)), q0=PARK_DEG, prefix="rail_ur")
    rb.set(np.radians((0.0, -150.0, 135.0, -75.0, -90.0, 0.0)))
    everything_else = [n for n in sc.actors if not n.startswith(f"u{units[0][0]}{units[0][1]}/") and n != "floor"]

    cars = {u: dict(y=tall[pick[u]][0], z=tall[pick[u]][1]) for u in units}

    def grow(f):
        """The first unit from the lab's 3950 mm to H_TALL; its trays above the roof are hidden as it grows."""
        h = V.UNIT_H + (SC.H_TALL - V.UNIT_H) * f
        for grp, pivot in grow_parts:
            if not grp.startswith(f"u{units[0][0]}{units[0][1]}_"):
                continue
            if pivot == "roof":
                sc.gmat[grp] = T((0, 0, h - SC.H_TALL))
            else:
                sc.gmat[grp] = T((0, 0, pivot)) @ S((1, 1, (h - pivot) / (SC.H_TALL - pivot))) @ T((0, 0, -pivot))
        for name, top in bands:                 # nothing pokes out of the roof (the cladding is opaque meanwhile)
            sc.alpha[name] = 1.0 if top <= h - 260.0 else 0.0
        g0 = f"u{units[0][0]}{units[0][1]}"
        for name in [x for x in sc.actors if x.startswith(f"{g0}/tray/") or x == f"{g0}/lift"]:
            sc.alpha[name] = 1.0 if cars[units[0]]["z"] + 800.0 <= h - 260.0 else 0.0
        return h

    def skin(f):
        for n, gh in ghosts.items():
            sc.base_alpha[n] = 1.0 + (gh - 1.0) * f

    def trays_move(down=True, stagger=0.35):
        """Every unit's extractor brings its tray from its slot to the opening (or back): pull it on, ride, push it
        out; units start a little apart."""
        def up(e):
            for j, u in enumerate(units):
                g = f"u{u[0]}{u[1]}"
                c = cars[u]
                t0 = (j % 4) * stagger / 4 * (1 if down else 0.5)
                v = min(1.0, max(0.0, (e - t0) / (1.0 - stagger + 1e-9)))
                if not down:
                    v = 1.0 - v
                a, b2 = min(1.0, v / 0.2), min(1.0, max(0.0, (v - 0.2) / 0.6))
                c3 = min(1.0, max(0.0, (v - 0.8) / 0.2))
                y = c["y"] + (0.0 - c["y"]) * a + (V.Y_OPEN - 0.0) * c3
                z = c["z"] + (V.Z_OPEN - c["z"]) * b2
                sc.gmat[f"{g}_tray"] = T((0, y, z))
                sc.gmat[f"{g}_lift"] = T((0, 0, z))
        return up

    def roll_to(x1):
        x0 = car_x[0]

        def up(e):
            car_x[0] = x0 + (x1 - x0) * e
            sc.gmat["carriage"] = T((car_x[0], 0, 0))
            rb.set()
        return up

    def reach(r, i):
        """IK pose with the gripper down 250 mm into unit (r, i)'s presented tray, 150 mm over its floor."""
        x = SC.unit_xform(r, i)[0, 3]
        side = 1.0 if r == 1 else -1.0
        p = np.array([x, side * (SC.AISLE / 2 + 150.0 + 250.0), V.Z_OPEN + V.T_FLOOR + 150.0])
        return P.tcp_frame(p, (0, 0, -1), 90.0)

    sc.gauges = [("Shuttles", f"{len(units)} × Shuttle XP 500, {SC.H_TALL / 1000:.2f} m"),
                 ("Trays", f"{len(units)} × {len(tall)} = {n_trays}, powered"),
                 ("Instruments", f"{n_inst}: OT-2, CubXL, H2D, A2L, A1 mini"),
                 ("Arm", f"one {ROBOT_NAME} on a floor rail")]
    gauges = sc.gauges
    sc.gauges = []
    for n in everything_else:
        sc.alpha[n] = 0.0
    grow(0.0)
    x11 = SC.unit_xform(1, 1)[0, 3]
    C1 = [(x11 + 4200, -8200, 3300), (x11, SC.Y_UNIT, 2200), (0, 0, 1)]
    C2 = [(x11 + 15000, -36000, 11000), (x11, SC.Y_UNIT, 7600), (0, 0, 1)]
    C3 = [(31000, -25000, 23000), (0, 0, 7000), (0, 0, 1)]
    C4 = [(14500, 0, 3200), (0, 0, 2300), (0, 0, 1)]                  # down the aisle from its east end
    C5 = [(29000, 21000, 24000), (0, 0, 6800), (0, 0, 1)]
    C6 = [(11500, 0, 4600), (-2000, 0, 1500), (0, 0, 1)]               # in the aisle: openings, rail and arm
    sc.cam = list(C1)
    n = 6
    sc.step(f"1/{n}", "Scaling up. The Shuttle XP 500 in the lab is 3.95 m tall. Kardex builds the Shuttle up to 30 m, "
            "in 100 mm steps, on the same 2780 × 3074 mm footprint: here it is 15.15 m, just under 50 ft.",
            4.2, lambda e: grow(e), hold=1.0, cam_to=C2,
            labels=[(f"{SC.H_TALL / 1000:.2f} m (49 ft 8 in)", (x11 + V.UNIT_W / 2, SC.Y_UNIT, SC.H_TALL), (0.70, 0.20)),
                    ("the lab's unit: 3.95 m", (x11 + V.UNIT_W / 2, SC.Y_UNIT - V.UNIT_D / 2, V.UNIT_H), (0.72, 0.62))])
    others = [n2 for n2 in everything_else if n2.startswith("u")]

    def appear(e):
        for n2 in others:
            sc.alpha[n2] = min(1.0, e * 1.4)
        for u in units[1:]:
            g = f"u{u[0]}{u[1]}"
            sc.gmat[g] = T((0, 0, -SC.H_TALL * (1.0 - e) ** 2)) @ SC.unit_xform(*u)
    sc.step(f"2/{n}", f"An array: eight of them in two rows of four, facing each other across an {SC.AISLE:.0f} mm aisle. "
            f"Each holds {len(tall)} powered trays in its two columns, one load of three instruments each.",
            4.0, appear, hold=1.0, cam_to=C3)
    rail = [n2 for n2 in everything_else if not n2.startswith("u")]

    def rail_in(e):
        for n2 in rail:
            sc.alpha[n2] = min(1.0, e * 1.5)
        sc.gmat["rail"] = T((0, 0, -400 * (1 - e)))
    sc.step(f"3/{n}", f"One {ROBOT_NAME} serves all eight openings: it rides a floor rail down the aisle on an 800 mm "
            "riser, the height it has on the MiR250, and turns to either row.", 2.6, rail_in, hold=0.8, cam_to=C4,
            labels=[(f"{ROBOT_NAME} on its rail carriage", (car_x[0], 0, 1600), (0.80, 0.30))])
    sc.gauges = gauges
    sc.step(f"4/{n}", f"See-through: {n_trays} trays and {n_inst} instruments, every tray powered in its slot (#53). "
            "The extractors run in parallel, one per unit.", 2.6, skin, hold=1.0, cam_to=C5)
    first, second = (1, 2), (0, 0)
    sc.step(f"5/{n}", "Every unit brings a tray down to its opening at once, at Kardex's 2 m/s vertical speed, while the "
            "arm rolls to the first one.", 6.0, both(trays_move(True), roll_to(SC.unit_xform(*first)[0, 3])),
            hold=0.3, cam_to=C6)
    q_park = rb.q.copy()
    cap = "The arm reaches into the opening and back, then rolls on to the next unit, across the aisle."
    sc.step(f"5/{n}", cap, 1.6, rb.joint_to(Tw=reach(*first)), hold=0.4)
    sc.step(f"5/{n}", cap, 1.2, rb.joint_to(q_park), hold=0.1)
    q_south = q_park.copy()
    q_south[0] += math.pi
    sc.step(f"5/{n}", cap, 2.8, both(roll_to(SC.unit_xform(*second)[0, 3]), rb.joint_to(q_south)), hold=0.1)
    sc.step(f"5/{n}", cap, 1.6, rb.joint_to(Tw=reach(*second)), hold=0.4)
    sc.step(f"5/{n}", cap, 1.2, rb.joint_to(q_south), hold=0.1)
    sc.step(f"6/{n}", "The trays go back to their slots, where they have power again. The same arm, the same trays and "
            f"the same equipment as the lab's one unit, on about {len(units) * 9.4:.0f} m² of floor plus the aisle.",
            6.0, trays_move(False), hold=0.3, cam_to=C3)
    sc.step(f"6/{n}", "The same arm, the same trays and the same equipment as the lab's one unit, "
            f"{SC.H_TALL / V.UNIT_H:.1f} times as tall and eight times over.", 1.0, None, hold=3.0, still=True)
    return sc.save()


def full():
    """Join the four MP4s without re-encoding."""
    import subprocess
    from scene import OUT
    parts = [OUT / "mp4" / f"vlm_{c}.mp4" for c in ("assembly", "loading", "workflow", "scale", "disassembly")]
    lst = OUT / "mp4" / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    out = OUT / "mp4" / "vertical_lab_full.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(out)], check=True)
    lst.unlink()
    return f"vertical_lab_full: {out.stat().st_size / 1e6:.1f} MB"


def ur_reach() -> float:
    import ur_arm
    return ur_arm.MODELS[ROBOT]["reach_mm"]


PARK_RAD = np.radians(PARK_DEG)
CHAPTERS = {"assembly": assembly, "loading": loading, "workflow": workflow, "disassembly": disassembly,
            "scale": scale}

if __name__ == "__main__":
    names = sys.argv[1:] or [*CHAPTERS, "full"]
    data = lab.meshes() if any(n in CHAPTERS for n in names) else None
    for name in names:
        print(full() if name == "full" else CHAPTERS[name](data), flush=True)

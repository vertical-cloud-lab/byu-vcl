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
REPOWDER_AT = (-3775.0, -1700.0, 0.0)          # its heat exchanger 1.2 m from the VLM's side, a little forward
REPOWDER_LBL = ("AMAZEMET rePowder atomizer", (REPOWDER_AT[0] + 250, REPOWDER_AT[1] + 400, 1600), (0.10, 0.30))

# what goes on each tray, in the tray's frame (centre of its floor, y to the back): (key, x, y). Items the arm works
# with are at the front edge, and the vial seats are within the arm's reach from its parking spot (reach.py)
LOADS = {
    "A": [("cubxl", -112.0, -114.5), ("ot2", 760.0, -40.0)],
    "B": [("rack", -250.0, -372.0), ("carousel", 250.0, -316.0)],
    "C": [("h2d", -560.0, 0.0), ("a1mini", 360.0, 0.0)],
}
ROLE = {"A": "liquid handling", "B": "powder dosing", "C": "3D printing"}
NAMES = {"ot2": "Opentrons OT-2", "cubxl": "CubXL liquid-handling gantry", "rack": "vial rack",
         "carousel": "multi-doser: chain carousel v2, 13 powders", "h2d": "Bambu Lab H2D", "a1mini": "Bambu Lab A1 mini"}
SOURCE = {"ot2": "Opentrons' own reference STEP", "cubxl": "the lab's model from #199",
          "rack": "a printed rack for the doser's 20 mL vials",
          "carousel": "powder-doser PR #185's CAD, driven by its own kinematics",
          "h2d": "the lab's model from Bambu's spec", "a1mini": "the lab's model from Bambu's outline drawing"}
HOME = {"A": "R2", "B": "R3", "C": "F1"}       # storage slot of each tray

# the mobile manipulator: a MiR250 parked square to the opening, 30 mm off the tray cover's 50 mm lip, the arm over
# its front half
AMR_XY = (0.0, -V.UNIT_D / 2 - V.SKIN - 50.0 - 30.0 - P.MIR["W"] / 2)
ARM_LOCAL = (0.0, 130.0)
BUFFER_LOCAL = (-300.0, -150.0)                # the one-vial holder on the cabinet top
RACK_SEAT = 5                                  # the rack's seat with the vial the workflow uses
CUB_SLOT = (100.0, -60.0, 80.0)                # the CubXL rack's sixth seat (base of the vial), CubXL frame
MODULE = 5                                     # the powder module the workflow doses from (0-based; "module 6")
DOSE_G = 0.512

CAM_WIDE = [(7570, -6720, 4790), (0, -250, 1800), (0, 0, 1)]
CAM_FRONT = [(4300, -9200, 2600), (-300, -600, 1700), (0, 0, 1)]
CAM_OPEN = [(5200, -7600, 3100), (100, -900, 1450), (0, 0, 1)]
CAM_WORK = [(-1300, -4300, 2550), (60, -1450, 1060), (0, 0, 1)]
CAM_MID = [(1700, -3300, 2100), (245, -1320, 1170), (0, 0, 1)]      # on the way to CAM_DOSE, clear of the arm
CAM_DOSE = [(1000, -1600, 1330), (245, -1320, 1170), (0, 0, 1)]     # along the rig's loop, at the station
CAM_CUB = [(1500, -3300, 2000), (60, -1420, 1010), (0, 0, 1)]


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
                    self._cubxl(g, eq)
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
        # the rePowder atomizer and its utilities stand to the left, fronts in line with the VLM's
        for name, e in data["repowder"].items():
            sc.add(name, e["mesh"], e["color"], "repowder", opacity=e["opacity"])
        sc.gmat["repowder"] = T(REPOWDER_AT)
        # the vial the workflow follows: in the rack's last seat at the start
        self._vial()
        if robot:
            self._amr()
        self.skin(1.0)(1.0)
        self.apply_state()

    def _rack(self, g):
        sc = self.sc
        block, seats = P.vial_rack()
        sc.add(f"{g}/rack", block, P.RACK_C, g)
        self.rack_seats = seats
        glass = None
        for i, s in enumerate(seats):
            if i == RACK_SEAT:
                continue
            v = P.vial_glass().translate(s, inplace=False)
            glass = v if glass is None else glass.merge(v)
        sc.add(f"{g}/vials", glass, P.GLASS, g, opacity=0.45, specular=0.6)

    def _cubxl(self, g, eq):
        """The CubXL frame plus its gantry (y), carriage (x) and tools (z) as child groups, all in the frame's frame."""
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
        holder, seat = P.buffer_holder()
        sc.add("amr/holder", holder.translate((*BUFFER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, "amr")
        self.buffer_seat = (BUFFER_LOCAL[0], BUFFER_LOCAL[1], P.AMR_TOP - 20 + seat[2])
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
                  "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top", "tray_A", "tray_B", "tray_C"]
    hide(L, L.groups(*vlm_groups) + eq)
    L.skin(0.0)(1.0)                 # the cladding goes on as it is: opaque
    L.show_gauges = False
    L.apply_state()
    n = 7
    sc.step(f"1/{n}", "The Kardex Shuttle XP 500 quoted in #53, beside the lab's rePowder atomizer: 2450 × 864 mm trays "
            "in a 2780 × 3074 mm module, 3950 mm tall to stay under 13 ft. The base frame goes down first, on levelling feet.",
            2.0, slide_in(L, ["base"], (0, 0, 900)), hold=1.2,
            labels=[("base frame, 2780 × 3074 mm", (V.UNIT_W / 2, -V.UNIT_D / 2, 100), (0.80, 0.80)), REPOWDER_LBL])
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
                  (0.86, 0.30 + 0.12 * i)) for i, k in enumerate(V.TRAYS)]
    sc.step(f"5/{n}", "Three electrified trays (#53): strong (1080 lb), medium (794 lb) and light (502 lb). Each has a "
            "power strip and a socket; it has power in its slot and at the opening, not while it moves.",
            2.4, slide_in(L, ["tray_A", "tray_B", "tray_C"], (3200, 0, 0)), hold=1.6, labels=trays_lbl)
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


def loading(data):
    sc, L = new_scene("vlm_loading", data)
    rb = L.robot
    eq = [n for k in V.TRAYS for g in L.eq_groups[k] for n in L.eq_names(g)] + L.groups("vial", "vial_powder",
                                                                                          "vial_liquid")
    hide(L, eq + L.groups("amr", *rb.groups()))
    L.skin(0.0)(1.0)
    L.apply_state()
    sc.cam = list(CAM_FRONT)
    n = 6
    sc.step(f"1/{n}", "The Kardex Shuttle XP 500 as it would stand in the lab: a closed cabinet, 2780 mm wide, 3074 mm "
            "deep and 3950 mm tall, with one large access opening at counter height and the operator console beside it.",
            3.0, None, hold=1.0, cam_to=CAM_WIDE,
            labels=[("large access opening", (0, -V.UNIT_D / 2 - V.SKIN, V.Z_SILL + 400), (0.18, 0.66)),
                    ("operator console", (V.CONSOLE_X, -V.UNIT_D / 2 - 120, V.CONSOLE_Z), (0.84, 0.72)),
                    REPOWDER_LBL])
    sc.step(f"2/{n}", "Inside, drawn see-through from here on: the front storage column, the extractor's shaft and the "
            "rear storage column, with the three empty trays in their slots.",
            2.4, L.skin(1.0), hold=1.2,
            labels=[("front storage", (V.TRAY_W / 2, V.Y_FRONT, 2900), (0.84, 0.30)),
                    ("extractor", (V.TRAY_W / 2, 0, LIFT_HOME - 40), (0.88, 0.52)),
                    ("rear storage", (V.TRAY_W / 2, V.Y_REAR, 3300), (0.88, 0.20))])
    for i, k in enumerate(("A", "B", "C")):
        step = f"{3 + i}/{n}"
        cap0 = f"Loading tray {k} ({ROLE[k]}): the extractor brings it to the opening; the shutter behind the " \
               "opening lets it through and closes behind it."
        L.fetch(k, step, cap0, fast=0.8, cam=CAM_OPEN if i == 0 else None)
        for g in L.eq_groups[k]:
            key = L.eq_key[g]
            x, y = next((xx, yy) for kk, xx, yy in LOADS[k] if kk == key)
            cap = f"Tray {k}: the {NAMES[key]} goes in through the opening ({SOURCE[key]})."
            lbl = [(NAMES[key], tray_world(k, (x, y, 500)), (0.72 if x > 0 else 0.20, 0.22))]
            sc.step(step, cap, 2.2, item_in(L, g), hold=0.7, labels=lbl)
        L.store(k, step, f"Tray {k} goes back to its slot ({HOME[k]}), where it has power again.", fast=0.8,
                cam=CAM_WIDE if i == 2 else None)
    cap = f"The operator rolls up: a Universal Robots {ROBOT_NAME} with a Robotiq 2F-85 gripper on a MiR250 mobile " \
          f"base, parked square to the opening. Its {ur_reach():.0f} mm reach covers every seat it works on from here."
    sc.step(f"{n}/{n}", cap, 2.6, slide_in(L, ["amr"], (0, -2200, 0), names=L.groups("amr", *rb.groups())),
            hold=1.0, cam_to=CAM_OPEN,
            labels=[(f"{ROBOT_NAME} on a MiR250", (AMR_XY[0], AMR_XY[1], 1300), (0.16, 0.42))])
    sc.step(f"{n}/{n}", "Loaded: liquid handling on tray A, powder dosing on tray B, 3D printing on tray C, each powered "
            "in its slot so its equipment can keep running while it is stored.",
            1.6, None, hold=2.4, cam_to=CAM_WIDE, still=True,
            labels=[(f"tray {k}: {ROLE[k]}", (V.TRAY_W / 2 - 300, *V.SLOTS[HOME[k]]), (0.86, 0.30 + 0.12 * i))
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
    cap = "An example run: dose 0.5 g of a powder from the multi-doser, then add liquid to it in the CubXL. The arm " \
          "asks for tray B: the extractor pulls it off its supports, carries it down and pushes it into the opening."
    sc.step(f"1/{n}", cap, 1.0, None, hold=0.5,
            labels=[("tray B: powder dosing", (V.TRAY_W / 2 - 300, *V.SLOTS["R3"]), (0.86, 0.34))])
    L.fetch("B", f"1/{n}", cap, cam=CAM_WORK)
    # ------------------------------------------------------------------ 2. an empty vial into the doser
    rack_xy = LOADS["B"][0][1:]
    seat = np.array(L.rack_seats[RACK_SEAT]) + (*rack_xy, V.T_FLOOR)
    grasp_z = 50.0                                           # grip 50 mm up the vial: above the rack's 40 mm block
    p_rack = tray_world("B", seat + (0, 0, grasp_z))
    car_xy = LOADS["B"][1][1:]
    vs = C.vial_seat()                                       # rig frame; the rig is turned 90 deg on the tray
    cup = np.array([car_xy[0] - vs[1], car_xy[1] + vs[0], V.T_FLOOR + vs[2]])
    p_cup = tray_world("B", cup + (0, 0, 32.0))
    cap = f"The {ROBOT_NAME} takes an empty 20 mL vial from the rack at the front of the tray and sets it in the " \
          "multi-doser's cup, on its 100 g load cell under the station."
    L.note(0, "Arm", "vial: rack to doser")
    pick(L, rb, f"2/{n}", cap, down(p_rack), down(p_rack + (0, 0, 110)), "vial", cam=CAM_WORK,
         labels=[("vial rack", p_rack + (-120, 0, 60), (0.20, 0.30)),
                 ("multi-doser (powder-doser #185)", p_cup + (0, 150, 420), (0.70, 0.18))])
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(Tw=level(p_cup + (0, -190, 6))), hold=0.05)
    sc.step(f"2/{n}", cap, 1.0, rb.line_to(level(p_cup + (0, 0, 6))), hold=0.05)
    sc.step(f"2/{n}", cap, 0.4, rb.line_to(level(p_cup)), hold=0.05)
    sc.step(f"2/{n}", cap, 0.5, rb.grip_to(0.0), hold=0.05)
    rb.release(L.eq_groups["B"][1])
    sc.step(f"2/{n}", cap, 0.9, rb.line_to(level(p_cup + (0, -190, 0))), hold=0.05)
    sc.step(f"2/{n}", cap, 1.2, rb.joint_to(PARK_RAD), hold=0.1, cam_to=CAM_MID)
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
          "the steel pinion: the powder drops through the D-cut funnel into the vial while the load cell counts it. Then " \
          "hold, tilt back, reverse one turn at rest, undock (powder-doser's leakage study)."
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
    sc.step(f"3/{n}", cap, 3.6, dose, hold=0.4, live=False)
    sc.alpha["stream"] = 0.0
    L.note(1, "Doser", f"module {MODULE + 1} back, undocking")
    sc.step(f"3/{n}", cap, 1.2, car.to(tilt=0.0), hold=0.1)
    sc.step(f"3/{n}", cap, 0.8, car.to(spin=spin0 + 2 * math.pi), hold=0.1)
    sc.step(f"3/{n}", cap, 1.0, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0)), hold=0.2)
    L.note(1, "Doser", f"module {MODULE + 1} undocked")
    # ------------------------------------------------------------------ 4. vial to the arm's base, tray B up
    buf = np.array(L.buffer_seat)
    p_buf = (sc.world("amr") @ np.r_[buf + (0, 0, grasp_z), 1.0])[:3]
    cap = f"The arm takes the vial out ({DOSE_G:.3f} g in it) and stands it in the holder on its own base, so the " \
          "VLM can swap trays. Tray B goes back to its slot and its power."
    L.note(0, "Arm", "vial: doser to its base")
    sc.step(f"4/{n}", cap, 1.2, rb.joint_to(Tw=level(p_cup + (0, -190, 0))), hold=0.05, cam_to=CAM_WORK)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(level(p_cup)), hold=0.05)
    sc.step(f"4/{n}", cap, 0.5, rb.grip_to(GRIP_VIAL), hold=0.05)
    rb.grasp("vial")
    sc.step(f"4/{n}", cap, 0.4, rb.line_to(level(p_cup + (0, 0, 6))), hold=0.0)
    sc.step(f"4/{n}", cap, 1.0, rb.line_to(level(p_cup + (0, -190, 6))), hold=0.05)
    place(L, rb, f"4/{n}", cap, down(p_buf), down(p_buf + (0, 0, 120)), "amr")
    sc.step(f"4/{n}", cap, 1.2, rb.joint_to(PARK_RAD), hold=0.1)
    L.note(0, "Arm", "parked, vial on its base")
    L.store("B", f"4/{n}", cap, cam=CAM_OPEN)
    # ------------------------------------------------------------------ 5. tray A down, vial into the CubXL
    cap = "Tray A (liquid handling) comes down. The CubXL's gantry is parked at the back, so the arm can put the vial " \
          "in the free seat of its rack."
    L.fetch("A", f"5/{n}", cap, cam=CAM_CUB)
    sc.step(f"5/{n}", cap, 1.0, L.cub_to(x=0.2, y=1.0, z=1.0), hold=0.2)
    slot = (sc.world(L.cub) @ np.r_[CUB_SLOT, 1.0])[:3]          # tray A is at the opening now
    p_slot = slot + (0, 0, grasp_z - 8.0)
    L.note(0, "Arm", "vial: base to CubXL")
    pick(L, rb, f"5/{n}", cap, down(p_buf), down(p_buf + (0, 0, 120)), "vial")
    place(L, rb, f"5/{n}", cap, down(p_slot), down(p_slot + (0, 0, 130)), L.cub,
          labels=[("CubXL: free seat in its rack", p_slot + (0, 0, 40), (0.74, 0.24))])
    sc.step(f"5/{n}", cap, 1.4, rb.joint_to(PARK_RAD), hold=0.1)
    L.note(0, "Arm", "parked")
    # ------------------------------------------------------------------ 6. CubXL adds liquid; tray A up
    cap = "The CubXL's gantry brings its pipette over the vial and adds the liquid; the vial stays there for the " \
          "measurement. Tray A goes back to its slot, where it has power, so the CubXL keeps working while it is stored."
    import equipment
    tr = equipment.CUBXL["travel"]
    px = (CUB_SLOT[0] + 50.0 + tr[0] / 2) / tr[0]                       # pipette at cx - 50 (equipment.cubxl)
    py = (CUB_SLOT[1] + 80.0 + equipment.CUBXL["D"] / 2 - 150.0) / tr[1]   # pipette at gy - 80
    sc.step(f"6/{n}", cap, 2.0, L.cub_to(x=px, y=py), hold=0.1, cam_to=CAM_CUB,
            labels=[("CubXL pipette", p_slot + (0, 0, 260), (0.74, 0.24))])
    sc.step(f"6/{n}", cap, 1.0, L.cub_to(z=0.55), hold=0.1)
    tip = lambda: (sc.world(f"{L.cub}_tools") @ np.r_[CUB_SLOT[0], CUB_SLOT[1], 100.0 + 0.5 * tr[2] - 40.0 + 0.0, 1.0])[:3]  # noqa: E731

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
    L.store("A", f"6/{n}", cap, cam=CAM_WIDE)
    L.note(0, "Arm", "parked; next request")
    sc.step(f"6/{n}", "Done: the dosed vial is in the CubXL on tray A, in storage and powered. The arm and the opening "
            "are free for the next request.", 1.0, None, hold=2.5, still=True)
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; opening top {V.Z_OPEN_TOP:.0f} mm", flush=True)
    return sc.save()


def disassembly(data):
    sc, L = new_scene("vlm_disassembly", data)
    rb = L.robot
    L.skin(1.0)(1.0)
    L.apply_state()
    n = 8
    sc.step(f"1/{n}", "Taking it down is the assembly in reverse. The mobile manipulator drives away first.", 1.8,
            slide_in(L, ["amr"], (0, -2200, 0), out=True, names=L.groups("amr", *rb.groups())), hold=0.6)
    for i, k in enumerate(("C", "B", "A")):
        step = f"{2 + i}/{n}"
        cap = f"Unloading tray {k} ({ROLE[k]}): it comes to the opening and the equipment goes out through it, one " \
              "piece at a time."
        L.fetch(k, step, cap, fast=0.7, cam=CAM_OPEN if i == 0 else None)
        for g in reversed(L.eq_groups[k]):
            sc.step(step, cap, 1.5, item_in(L, g, out=True), hold=0.2)
        L.store(k, step, cap, fast=0.7)
    L.show_gauges = False
    L.apply_state()
    sc.step(f"5/{n}", "The cladding, the opening's posts, header and cover, the console and the shutter come off.",
            2.4, both(slide_in(L, ["skin_L"], (-900, 0, 0), out=True), slide_in(L, ["skin_R"], (900, 0, 0), out=True),
                      slide_in(L, ["skin_back"], (0, 900, 0), out=True), slide_in(L, ["skin_top"], (0, 0, 900), out=True),
                      slide_in(L, ["skin_front", "bay", "console", "shutter"], (0, -900, 0), out=True)),
            hold=0.8, cam_to=CAM_WIDE)
    sc.step(f"6/{n}", "The trays slide out of their slots.", 2.0,
            slide_in(L, ["tray_A", "tray_B", "tray_C"], (3200, 0, 0), out=True), hold=0.6)
    sc.step(f"7/{n}", "The extractor platform, its drive and its guide rails come out.", 2.4,
            both(slide_in(L, ["lift_rails"], (0, 0, 2500), out=True), slide_in(L, ["drive"], (0, 0, 1400), out=True),
                 slide_in(L, ["lift", "belts"], (0, 0, 2400), out=True)), hold=0.6)
    sc.step(f"8/{n}", "The storage columns, the posts and roof rails, and last the base frame.", 2.0,
            slide_in(L, ["col_front", "col_rear"], (2600, 0, 0), out=True), hold=0.3)
    sc.step(f"8/{n}", "The storage columns, the posts and roof rails, and last the base frame.", 2.4,
            both(slide_in(L, ["posts"], (0, 0, 1800), out=True), slide_in(L, ["base"], (0, 0, 900), out=True)),
            hold=1.5)
    return sc.save()


def full():
    """Join the four MP4s without re-encoding."""
    import subprocess
    from scene import OUT
    parts = [OUT / "mp4" / f"vlm_{c}.mp4" for c in ("assembly", "loading", "workflow", "disassembly")]
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
CHAPTERS = {"assembly": assembly, "loading": loading, "workflow": workflow, "disassembly": disassembly}

if __name__ == "__main__":
    names = sys.argv[1:] or [*CHAPTERS, "full"]
    data = lab.meshes() if any(n in CHAPTERS for n in names) else None
    for name in names:
        print(full() if name == "full" else CHAPTERS[name](data), flush=True)

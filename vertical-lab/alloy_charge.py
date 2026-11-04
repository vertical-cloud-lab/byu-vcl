"""The alloy workflow, start to finish (#303), chapter 1: the atomizer charge, made up on tray B of the VLM.

    xvfb-run -a python3 alloy_charge.py            # -> out/alloy_charge.gif, out/mp4/alloy_charge.mp4, .json, stills
    PREVIEW=1 xvfb-run -a python3 alloy_charge.py  # the last frame of each sub-step -> /tmp/preview_alloy_charge.png

The rePowder melts **charge cups**, the lab's own (#222, ``charge.py``): turned from high-purity bar, filled with
powder by the multi-doser and closed with a vented plug pressed into the bore. The lab loads four charges a crucible
(byu-vcl PR #318), so the rack on tray B holds eight cups: four 5N Al cups for this run's Al-10Si and four oxygen-free
Cu cups for a 90/10 Cu-Ni run (DAL #162, #219), each with a plug of its own metal.

Answering PR #318's review of round 4:
* **No load cell.** The doser's weighing is an A&D analytical balance, as on the lab's doser (HR-100A). Here it is
  the HR-202i (220 g x 0.1 mg), the larger one powder-doser's design notes name, because a Cu cup with its plug and
  Ni is about 130 g. The chain carousel's docking actuator stands 6 mm behind the auger's outlet, so no balance fits
  under the outlet as the rig is built (``charge.STATION``): the cup is dosed in a plain cradle and weighed on the
  HR-202i beside it.
* **One funnel per powder.** The doser has no shared catch funnel. Each powder has its own labelled funnel; the arm
  sets the Si funnel in the station's fork for the four Al cups and swaps it for the Ni funnel before the Cu cups.

Every arm move is a straight line of the grasp point or a joint move between two solved poses (``robot.py``), as in
``animate.workflow``. The cups are always held level (fingers closing sideways), so a cup never tilts in the gripper;
the plugs are taken from above. Close-ups cut the cup, powder, funnel, plug and sleeve in half (``charge.lathe``).
"""
from __future__ import annotations

import math
import sys

import numpy as np
import pyvista as pv

import scene
scene.GIF_FPS = 5                      # a 2.5-minute GIF under 4.9 MB (the MP4 keeps every frame, 15 fps)
scene.GIF_SIZE = (640, 360)
from scene import Scene, T, R, S  # noqa: E402

import animate as A                    # noqa: E402
import carousel as CR                  # noqa: E402
import charge as C                     # noqa: E402
import lab                             # noqa: E402
import props as P                      # noqa: E402
import vlm as V                        # noqa: E402
from robot import both                 # noqa: E402

sys.path.insert(0, str(lab.HERE / "lab_models"))
import labware as LW                   # noqa: E402

NAME = "alloy_charge"
TITLE = "Vertical cloud lab, the alloy route 1/4: the atomizer charge"
# tray B, left of the doser: the balance, the eight-cup rack and the press behind it; the funnel stand right of the doser
RACK_AT = (-512.0, -372.0)
PRESS_AT = (-500.0, -150.0)
BAL_AT = (-102.0, -110.0)              # the HR-202i's body centre, turned so its left side door faces the arm
FSTAND_AT = (470.0, -372.0)
SLOTS = [("Al", "Si")] * 4 + [("Cu", "Ni")] * 4     # rack seat -> (cup metal, powder)
FUNNELS = ("Si", "Ni")                 # stand seat -> powder
MODULE = {"Si": 5, "Ni": 2}            # carousel modules (0-based) holding the two powders
CUP_GRASP = 45.0                       # grasp point above a cup's base (its top 18.5 mm higher)
PLUG_GRASP = 21.5                      # above a plug's base: the pads' lower ends 2 mm over the cup's rim
GRIP_CUP = 0.80                        # 2F-85 closure on the 19.05 mm cup: gap = 28 - 90 (c - 0.70) (ur_arm.gripper_fk)
GRIP_PLUG = 0.87                       # on the 12.7 mm plug
OPEN_CUP = 0.66                        # 31.6 mm between the pads: clear of a neighbouring cup in a pocket row
OPEN_PLUG = 0.60
GRIP_FUNNEL = 0.70 + (28.0 - C.FUNNEL["band_d"]) / 90.0      # on the funnel's 42 mm band
OPEN_FUNNEL = 0.70 + (28.0 - C.FUNNEL["band_d"] - 12.0) / 90.0
CARRIER_LOCAL = A.BUFFER_LOCAL         # the MiR's cup carrier stands where round 2's one-vial holder stood
METAL_C = {"Al": C.AL_5N, "Cu": C.CU}
CUP_NAME = {"Al": "5N Al", "Cu": "OFE Cu"}
BAL_HOLDER = 2.0                       # the cup holder's floor on the pan
DOOR_OPEN = 140.0                      # the side door's travel (it slides back along the chamber)
TOL = 0.01                             # dose tolerance, fraction of the dose (assumed)
STATION_GONE = {"load_cell", "vial_cup", "vial_funnel", "ext_vial_post", "level_wedge"}

CAM_WORK = [(-1250, -4450, 2550), (-160, -1430, 1010), (0, 0, 1)]
CAM_RACK = [(-1200, -2700, 1750), (-470, -1360, 950), (0, 0, 1)]
CAM_AMR = [(1300, -4100, 1900), (-250, -1900, 1000), (0, 0, 1)]


def cam_near(p, off, look=(0.0, 0.0, 0.0)):
    """A camera at p + off looking at p + look (world)."""
    p = np.asarray(p, float)
    return [tuple(p + off), tuple(p + np.asarray(look, float)), (0, 0, 1)]


def lvl(p, toward=(0.0, 1.0, 0.0)):
    """Gripper level, pointing along `toward`, fingers closing sideways (props.tcp_frame)."""
    return P.tcp_frame(np.asarray(p, float), toward, 0.0)


def dwn(p):
    """Gripper pointing straight down, fingers closing along world x (along a rack's row)."""
    return P.tcp_frame(np.asarray(p, float), (0, 0, -1), 0.0)


def masses(metal: str, pw: str, wt: float = 10.0) -> dict:
    """Cup, plug and dose of one cup, g, unrounded (charge.recipe() rounds)."""
    v = C.volumes()
    frac = C.fill_fraction(metal, pw, wt)
    return dict(cup=v["cup"] * C.RHO[metal], plug=v["plug"] * C.RHO[metal],
                dose=v["cavity"] * C.POWDERS[pw][1] * frac, fill=(C.FILL_TOP - C.FLOOR_Z) * frac)


def _model_meshes(parts) -> list[tuple[str, pv.PolyData, tuple, float, float]]:
    """[(material, mesh, colour, opacity, specular)] of a list of (name, cq shape, material), merged by material."""
    by = {}
    for _, shape, mat in parts:
        sh = shape.val() if len(shape.vals()) == 1 else LW.cq.Compound.makeCompound(shape.vals())
        by.setdefault(mat, []).append(lab.to_mesh(sh, 0.4))
    out = []
    for mat, ms in by.items():
        r, g, b, a, spec = lab.MATS[mat]
        out.append((mat, lab._merge(ms), (r, g, b), a, spec))
    return out


class Charge:
    """The charge rack, the press, the cups and plugs, the funnels and their stand, the rebuilt doser station, the
    HR-202i and the MiR's carrier, added to round 2's scene (``A.Lab``); the vial, its rack and the one-vial holder
    are hidden."""

    def __init__(self, sc: Scene, L: A.Lab):
        self.sc, self.L = sc, L
        rig = L.eq_groups["B"][1]
        self.rig = rig
        for n in ("vial/glass", f"{L.eq_groups['B'][0]}/rack", f"{L.eq_groups['B'][0]}/vials", "amr/holder"):
            sc.alpha[n] = 0.0
            sc.base_alpha[n] = 0.0
        # the rack, on tray B
        body, rims, self.seats = C.rack()
        sc.add("crack/body", body, P.RACK_C, "crack")
        sc.add("crack/rims", rims, C.PRINT, "crack")
        sc.parent["crack"] = "tray_B"
        sc.gmat["crack"] = T((*RACK_AT, V.T_FLOOR))
        # the press: frame fixed; nest (with F1 and the ejector) on its rail; the ram
        pp = C.press_parts()
        for k, (m, col) in pp["fixed"].items():
            sc.add(f"press/{k}", m, col, "press", specular=0.3)
        sc.parent["press"] = "tray_B"
        sc.gmat["press"] = T((*PRESS_AT, V.T_FLOOR))
        sc.add("press/nest", pp["nest"]["nest"][0], pp["nest"]["nest"][1], "press_nest")
        sc.add("press/sleeve", pp["nest"]["sleeve"][0], C.STEEL, "press_nest", specular=0.5)
        sc.add("press/sleeve_cut", C.sleeve(cut=True).translate((0, 0, C.PR["nest_top"]), inplace=False), C.STEEL,
               "press_nest", specular=0.5, shown=False)
        sc.parent["press_nest"] = "press"
        self.nest_y = C.PR["out_y"]
        sc.add("press/ram", pp["ram"][0], pp["ram"][1], "press_ram", specular=0.6)
        sc.parent["press_ram"] = "press"
        self.ram_z = C.PR["ram_up"]
        sc.add("press/ejector", pp["ejector"][0], pp["ejector"][1], "press_ej")
        sc.parent["press_ej"] = "press_nest"
        self.eject = 0.0
        # the vent's puff of air while the plug goes in (points), hidden until used
        sc.add("puff", pv.PolyData(np.zeros((12, 3))), (0.95, 0.97, 1.0), "puff", shown=False, style="points",
               point_size=6.0, render_points_as_spheres=True)
        # the doser's cup station, rebuilt: post, cradle, funnel fork (rig frame)
        fit, self.st_seat = C.station_fittings()
        for k, (m, col) in fit.items():
            sc.add(f"station/{k}", m, col, rig, specular=0.3)
        # the HR-202i, its left side door (facing the arm) on its own group
        bal = LW.hr202i_parts(0.0)
        for j, (mat, m, col, a, spec) in enumerate(_model_meshes(bal["body"] + bal["door_right"] + bal["top_door"])):
            sc.add(f"bal/{mat}{j}", m, col, "bal", opacity=a, specular=spec)
        for j, (mat, m, col, a, spec) in enumerate(_model_meshes(bal["door_left"])):
            sc.add(f"bal_door/{mat}{j}", m, col, "bal_door", opacity=a, specular=spec)
        sc.parent["bal"] = "tray_B"
        sc.gmat["bal"] = T((*BAL_AT, V.T_FLOOR)) @ R((0, 0, 1), 90)
        sc.parent["bal_door"] = "bal"
        self.door = 0.0
        hp = LW.HR202I
        self.pan_xyz = np.array([0.0, -hp["D"] / 2 + hp["pan_y"], hp["pan_top"]])
        holder = C.lathe([(0, 0), (20, 0), (20, BAL_HOLDER), (0, BAL_HOLDER)], res=48)
        cwall = C.lathe([(C.STOCK_D / 2 + 0.6, BAL_HOLDER), (C.STOCK_D / 2 + 3.6, BAL_HOLDER),
                         (C.STOCK_D / 2 + 3.6, BAL_HOLDER + 6.0), (C.STOCK_D / 2 + 0.6, BAL_HOLDER + 6.0)], cut=True)
        # the C opens to the door (balance -x): lathe(cut) keeps +y; turned, its wall is on +x
        cwall = cwall.rotate_z(-90.0, inplace=False)
        sc.add("bal/holder", holder.merge(cwall).translate(self.pan_xyz, inplace=False), C.PRINT, "bal")
        # the funnels on their stand
        stand, self.fseats = C.funnel_stand(len(FUNNELS))
        sc.add("fstand/body", stand, P.RACK_C, "fstand")
        sc.parent["fstand"] = "tray_B"
        sc.gmat["fstand"] = T((*FSTAND_AT, V.T_FLOOR))
        fm, fcut = C.funnel(), C.funnel(cut=True)
        for j, pw in enumerate(FUNNELS):
            g = f"funnel_{pw}"
            sc.add(f"{g}/body", fm["body"], (0.95, 0.95, 0.93), g, specular=0.2)
            sc.add(f"{g}/cut", fcut["body"], (0.95, 0.95, 0.93), g, specular=0.2, shown=False)
            sc.add(f"{g}/label", fm["label"], C.FUNNEL_LABEL[pw], g, specular=0.2)
            sc.parent[g] = "fstand"
            sc.gmat[g] = T(self.fseats[j])
        # the MiR's carrier
        mesh, self.carrier_seats = C.carrier()
        sc.add("amr/carrier", mesh.translate((*CARRIER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, "amr")
        self.carrier_base = np.array([*CARRIER_LOCAL, P.AMR_TOP - 20])
        # cups and plugs, in the rack
        unit, point = C.unit_powder(cut=True), C.drill_point_fill(cut=True)
        self.powder_h = [0.0] * len(SLOTS)
        self._point = [False] * len(SLOTS)
        for i, (metal, pw) in enumerate(SLOTS):
            g = f"cup{i}"
            sc.add(f"{g}/whole", C.cup(), METAL_C[metal], g, specular=0.7)
            sc.add(f"{g}/cut", C.cup(cut=True), METAL_C[metal], g, specular=0.7, shown=False)
            sc.add(f"{g}/point", point, C.POWDERS[pw][0], g, shown=False, specular=0.05)
            sc.add(f"{g}/powder", unit, C.POWDERS[pw][0], f"{g}_pw", shown=False, specular=0.05)
            sc.parent[f"{g}_pw"] = g
            sc.gmat[f"{g}_pw"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, 0.01))
            sc.parent[g] = "crack"
            sc.gmat[g] = T(self.seats["cup"][i])
            p = f"plug{i}"
            sc.add(f"{p}/whole", C.plug(), METAL_C[metal], p, specular=0.7)
            sc.add(f"{p}/cut", C.plug(cut=True), METAL_C[metal], p, specular=0.7, shown=False)
            sc.parent[p] = "crack"
            sc.gmat[p] = T(self.seats["plug"][i])
        self.apply()

    # ------------------------------------------------------------------------------------------ state
    def apply(self):
        sc = self.sc
        sc.gmat["press_nest"] = T((0, self.nest_y, 0))
        sc.gmat["press_ram"] = T((0, C.PR["ram_y"], self.ram_z))
        sc.gmat["press_ej"] = T((0, 0, C.PR["nest_top"] + self.eject))
        sc.gmat["bal_door"] = T((0, self.door, 0))
        for i in range(len(SLOTS)):
            h = self.powder_h[i]
            sc.gmat[f"cup{i}_pw"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, max(h, 0.01)))

    def cut(self, i, on: bool, sleeve=False, funnel=None):
        """Swap cup i (and its plug, F1 and a funnel) for the half-section versions."""
        sc = self.sc
        sc.alpha[f"cup{i}/whole"] = 0.0 if on else 1.0
        sc.alpha[f"cup{i}/cut"] = 1.0 if on else 0.0
        sc.alpha[f"plug{i}/whole"] = 0.0 if on else 1.0
        sc.alpha[f"plug{i}/cut"] = 1.0 if on else 0.0
        shown = on and self.powder_h[i] > 0.05
        sc.alpha[f"cup{i}/point"] = 1.0 if on and self._point[i] else 0.0
        sc.alpha[f"cup{i}/powder"] = 1.0 if shown else 0.0
        if sleeve is not None:
            sc.alpha["press/sleeve"] = 0.0 if (on and sleeve) else 1.0
            sc.alpha["press/sleeve_cut"] = 1.0 if (on and sleeve) else 0.0
        if funnel is not None:
            sc.alpha[f"funnel_{funnel}/body"] = 0.0 if on else 1.0
            sc.alpha[f"funnel_{funnel}/cut"] = 1.0 if on else 0.0

    def to(self, **kw):
        """An update(u) easing nest_y / ram_z / eject / door to the given values."""
        start = {k: getattr(self, k) for k in kw}

        def up(u):
            for k, v in kw.items():
                setattr(self, k, start[k] + (v - start[k]) * u)
            self.apply()
        return up

    # ------------------------------------------------------------------------------------------ places (world)
    def _w(self, group, xyz):
        return (self.sc.world(group) @ np.r_[np.asarray(xyz, float), 1.0])[:3]

    def rack_cup(self, i):
        return self._w("crack", self.seats["cup"][i])

    def rack_plug(self, i):
        return self._w("crack", self.seats["plug"][i])

    def station_cup(self):
        return self._w(self.rig, self.st_seat["cup"])

    def station_funnel(self):
        return self._w(self.rig, self.st_seat["funnel"])

    def stand_funnel(self, j):
        return self._w("fstand", self.fseats[j])

    def bal_cup(self):
        return self._w("bal", self.pan_xyz + (0, 0, BAL_HOLDER))

    def nest_seat(self, eject):
        """Base centre of a cup on the ejector, world, with the nest out."""
        return self._w("press", (0.0, C.PR["out_y"], C.PR["nest_top"] + eject))

    def carrier_seat(self, k):
        return self._w("amr", self.carrier_base + self.carrier_seats[k])


def stream_points(L: A.Lab, K: Charge, i: int, t: float, on: float) -> np.ndarray:
    """The dose, rig frame: grains falling from the auger's outlet onto the funnel's cone, and from its stem into cup
    i's bore."""
    top = L.carousel.exit_point()
    ax, ay, tip = K.st_seat["funnel"]
    r_hit = math.hypot(top[0] - ax, top[1] - ay)
    f = C.FUNNEL
    cone_z = tip + f["stem_l"] + f["flange_t"] + (r_hit - f["stem_od"] / 2) / (f["cone_r"] - f["stem_od"] / 2) \
        * (f["cone_h"] - f["band_h"])
    n = 30
    s = (np.arange(n) / n + t * 1.7) % 1.0
    s = s[s < on]
    if not len(s):
        return np.zeros((0, 3))
    a = np.c_[top[0] + 0 * s, top[1] + np.sin(np.arange(len(s)) * 2.3) * 0.6, top[2] - (top[2] - cone_z) * s ** 2]
    bottom = K.st_seat["cup"][2] + C.FLOOR_Z + K.powder_h[i] + 1.0
    m = 14
    s2 = (np.arange(m) / m + t * 2.3) % 1.0
    s2 = s2[s2 < on]
    b = np.c_[ax + 0 * s2, ay + np.sin(np.arange(len(s2)) * 1.7) * 0.8, tip - (tip - bottom) * s2 ** 2]
    return np.r_[a, b]


def movie():
    data = lab.meshes()
    CR.SKIP = CR.SKIP | STATION_GONE           # the rig's load cell, vial cup, vial post and catch funnel come out
    sc = Scene(NAME, TITLE)
    sc.cam = list(A.CAM_WIDE)
    L = A.Lab(sc, data, robot=True, highlight=MODULE["Si"])
    K = Charge(sc, L)
    rb, car = L.robot, L.carousel
    sc.parent["stream"] = K.rig
    run = RECIPE["runs"]
    al, cu = run["Al-10Si"], run["Cu-10Ni"]
    ms = {"Al": masses("Al", "Si"), "Cu": masses("Cu", "Ni")}
    L.extra_gauges = [("Arm", f"{A.ROBOT_NAME}, parked"), ("Doser", "module 1 at the station"),
                      ("HR-202i", "0.0000 g  (220 g x 0.1 mg)"), ("Press", "nest out, ram up"),
                      ("Charge", "0 of 8 cups made up")]
    L.apply_state()
    n = 8
    made = {"Al": 0, "Cu": 0}

    def charge_line():
        L.note(4, "Charge", f"{made['Al']} of 4 Al-10Si, {made['Cu']} of 4 Cu-10Ni cups made up")

    # ------------------------------------------------------------------ 1. tray B down
    cap = ("The alloy route, start to finish. First the charge: the atomizer melts cups, the lab's own (#222), turned "
           "from high-purity bar, filled with powder and closed with a vented plug. Four go into the crucible a run. "
           "Tray B holds four 5N Al cups for this run's Al-10Si and four oxygen-free Cu cups for a 90/10 Cu-Ni run.")
    sc.step(f"1/{n}", cap, 1.0, None, hold=0.6,
            labels=[("tray B: powder dosing and the charge", (V.TRAY_W / 2 - 300, *V.SLOTS["R3"]), (0.84, 0.34))])
    L.fetch("B", f"1/{n}", cap, cam=CAM_WORK)
    sc.step(f"1/{n}", cap, 1.6, None, hold=1.6, cam_to=CAM_WORK,
            labels=[("charge rack: 4 x 5N Al and 4 x OFE Cu cups, a plug for each", K.rack_cup(1) + (0, 0, 70),
                     (0.10, 0.20)),
                    ("plug press with #222's steel sleeve (F1)", K.nest_seat(0) + (0, 0, 330), (0.12, 0.40)),
                    ("A&D HR-202i balance, 220 g x 0.1 mg", K.bal_cup() + (0, 0, 260), (0.36, 0.16)),
                    ("multi-doser (powder-doser #185), its station rebuilt for cups", tray_xyz(L, (250, -250, 560)),
                     (0.62, 0.12)),
                    ("one funnel per powder: Si (yellow), Ni (green)", K.stand_funnel(0) + (30, 0, 50), (0.80, 0.30))])
    cap = ("No load cell: the doser's weighing is an A&D analytical balance, as on the lab's own doser (HR-100A). The "
           "HR-202i reads 220 g to 0.1 mg, so a Cu cup, about 130 g with its plug and Ni, is fine. The doser has no "
           "shared funnel: each powder has its own, and the arm sets it in the station's fork.")
    sc.step(f"1/{n}", cap, 1.2, None, hold=2.8, cam_to=cam_near(K.bal_cup(), (650.0, -1500.0, 700.0),
                                                                 (250.0, 40.0, 140.0)))

    # ------------------------------------------------------------------ the funnel moves
    def funnel_to_station(pw, st, fast=1.0, cam=None):
        j = FUNNELS.index(pw)
        g = f"funnel_{pw}"
        gr = C.FUNNEL["grasp"]
        f = fast
        p0 = K.stand_funnel(j) + (0, 0, gr)
        p1 = K.station_funnel() + (0, 0, gr)
        L.note(0, "Arm", f"{pw} funnel: stand to the doser's fork")
        sc.step(st, None, 1.4 * f, both(rb.joint_to(Tw=lvl(p0 + (0, -170, 30))), rb.grip_to(OPEN_FUNNEL)), hold=0.05,
                cam_to=cam)
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p0 + (0, 0, 4))), hold=0.05)
        sc.step(st, None, 0.3 * f, rb.line_to(lvl(p0)), hold=0.0)
        sc.step(st, None, 0.4 * f, rb.grip_to(GRIP_FUNNEL), hold=0.05)
        rb.grasp(g)
        sc.step(st, None, 0.4 * f, rb.line_to(lvl(p0 + (0, 0, 6))), hold=0.0)
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p0 + (0, -170, 6))), hold=0.05)
        sc.step(st, None, 1.3 * f, rb.joint_to(Tw=lvl(p1 + (0, -200, 6))), hold=0.05)
        sc.step(st, None, 1.0 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=0.05)
        sc.step(st, None, 0.4 * f, rb.line_to(lvl(p1)), hold=0.05)
        sc.step(st, None, 0.4 * f, rb.grip_to(OPEN_FUNNEL), hold=0.05)
        rb.release(K.rig)
        sc.step(st, None, 0.8 * f, rb.line_to(lvl(p1 + (0, -200, 0))), hold=0.05)
        sc.step(st, None, 1.0 * f, rb.joint_to(A.PARK_RAD), hold=0.05)
        L.note(0, "Arm", "parked")

    def funnel_to_stand(pw, st, fast=1.0, cam=None):
        j = FUNNELS.index(pw)
        g = f"funnel_{pw}"
        gr = C.FUNNEL["grasp"]
        f = fast
        p0 = K.station_funnel() + (0, 0, gr)
        p1 = K.stand_funnel(j) + (0, 0, gr)
        L.note(0, "Arm", f"{pw} funnel: back to its place on the stand")
        sc.step(st, None, 1.3 * f, both(rb.joint_to(Tw=lvl(p0 + (0, -200, 0))), rb.grip_to(OPEN_FUNNEL)), hold=0.05,
                cam_to=cam)
        sc.step(st, None, 0.8 * f, rb.line_to(lvl(p0)), hold=0.05)
        sc.step(st, None, 0.4 * f, rb.grip_to(GRIP_FUNNEL), hold=0.05)
        rb.grasp(g)
        sc.step(st, None, 0.4 * f, rb.line_to(lvl(p0 + (0, 0, 6))), hold=0.0)
        sc.step(st, None, 0.9 * f, rb.line_to(lvl(p0 + (0, -200, 6))), hold=0.05)
        sc.step(st, None, 1.3 * f, rb.joint_to(Tw=lvl(p1 + (0, -170, 6))), hold=0.05)
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=0.05)
        sc.step(st, None, 0.3 * f, rb.line_to(lvl(p1)), hold=0.05)
        sc.step(st, None, 0.4 * f, rb.grip_to(OPEN_FUNNEL), hold=0.05)
        rb.release("fstand")
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p1 + (0, -170, 0))), hold=0.05)
        sc.step(st, None, 1.0 * f, rb.joint_to(A.PARK_RAD), hold=0.05)
        L.note(0, "Arm", "parked")

    # ------------------------------------------------------------------ one cup, rack to carrier (or back to the rack)
    def cycle(i, fast):
        metal, pw = SLOTS[i]
        m = ms[metal]
        f = 0.075 if fast else 0.85
        H = (lambda x: x) if not fast else (lambda x: 0.0)     # no holds in the time-lapse
        k_al = sum(1 for s in SLOTS[:i] if s[0] == "Al")
        detail = not fast
        st = f"{3 if detail else (5 if metal == 'Al' else 7)}/{n}"
        # -------------------------------------------------- cup to the doser's cradle
        if detail:
            cap = (f"The {A.ROBOT_NAME} takes an empty {CUP_NAME[metal]} cup from the rack, level from the front, and "
                   f"slides it into the doser's cradle, under the {pw} funnel's stem: the stem stops 4 mm over the "
                   f"rim, so the funnel never touches a cup.")
            L.note(0, "Arm", f"{CUP_NAME[metal]} cup {i + 1}: rack to the doser")
        else:
            cap = None
        p0 = K.rack_cup(i) + (0, 0, CUP_GRASP)
        p1 = K.station_cup() + (0, 0, CUP_GRASP)
        sc.step(st, cap, 1.6 * f, both(rb.joint_to(Tw=lvl(p0 + (0, -150, 30))), rb.grip_to(OPEN_CUP)), hold=H(0.05),
                cam_to=CAM_WORK if detail else None)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(p0 + (0, 0, 30))), hold=H(0.0))
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0 + (0, -150, 30))), hold=H(0.05))
        sc.step(st, cap, 1.4 * f, rb.joint_to(Tw=lvl(p1 + (0, -200, 2))), hold=H(0.05))
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(p1 + (0, 0, 2))), hold=H(0.05),
                cam_to=cam_near(K.station_cup(), (230.0, -430.0, 170.0), (0.0, 0.0, 70.0)) if detail else None)
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(p1)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
        rb.release(K.rig)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p1 + (0, -200, 0))), hold=H(0.05))
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=H(0.05), cam_to=A.CAM_MID if detail else None)
        L.note(0, "Arm", "parked, clear of the doser")
        # -------------------------------------------------- dose
        mod = MODULE[pw]
        if detail or car.state["shift"] != car.index_to(mod):
            if detail:
                cap = (f"The carousel brings module {mod + 1} ({pw} powder) to the station and docks it. It tilts and "
                       f"its auger turns: the {pw} falls onto its own funnel and through the stem into the cup's 1/2 "
                       f"in bore. Cut open here: the bore fills from the 118° drill point.")
            L.note(1, "Doser", f"indexing to module {mod + 1} ({pw})")
            sc.step(st, cap, 2.2 * f, car.to(shift=car.index_to(mod)), hold=H(0.1), cam_to=A.CAM_DOSE if detail else None)
        L.note(1, "Doser", f"module {mod + 1} ({pw}) docking")
        ghost = mod == MODULE["Si"]
        seat = K.station_cup()
        cam_dose = cam_near(seat, (120.0, -250.0, 95.0), (0.0, 0.0, 62.0))
        sc.step(st, cap, 1.2 * f, both(car.to(ext=CR.DOCK_EXT, magnet_on=True), car.ghost(0.18) if ghost else None),
                hold=H(0.1), cam_to=cam_dose if detail else None)
        L.note(1, "Doser", f"module {mod + 1} tilted, dosing {pw} by auger turns")
        sc.step(st, cap, 1.3 * f, car.to(tilt=CR.TILT), hold=H(0.05))
        if detail:
            K.cut(i, True, sleeve=None, funnel=pw)
        spin0 = car.state["spin"]
        stt = car.to(spin=spin0 + 2 * math.pi * 2.0)
        target = m["fill"]

        def dose(u, i=i, target=target, stt=stt, pw=pw):
            stt(u)
            on = 1.0 if 0.05 < u < 0.95 else 0.0
            pts = stream_points(L, K, i, u * 6.0, on)
            sc.alpha["stream"] = 1.0 if len(pts) else 0.0
            if len(pts):
                sc.set_mesh("stream", pv.PolyData(pts))
            k = min(1.0, max(0.0, (u - 0.12) / 0.83))
            K._point[i] = k > 0.02
            K.powder_h[i] = target * max(0.0, (k - 0.08) / 0.92)
            K.apply()
            if detail:
                K.cut(i, True, sleeve=None, funnel=pw)
        sc.step(st, cap, 3.4 * f, dose, hold=0.3 if detail else 0.0, live=False)
        sc.alpha["stream"] = 0.0
        K.powder_h[i] = target
        K._point[i] = True
        K.apply()
        L.note(1, "Doser", f"module {mod + 1} back, undocking")
        sc.step(st, cap, 1.0 * f, car.to(tilt=0.0), hold=H(0.05))
        sc.step(st, cap, 0.7 * f, car.to(spin=spin0 + 2 * math.pi), hold=H(0.05))
        sc.step(st, cap, 0.9 * f, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0) if ghost else None), hold=H(0.1))
        K.cut(i, False, sleeve=None, funnel=pw)
        L.note(1, "Doser", f"module {mod + 1} undocked")
        # -------------------------------------------------- weigh
        q = K.bal_cup() + (0, 0, CUP_GRASP)
        read = m["cup"] + m["dose"] * (0.9987 if i % 3 else 1.0006)        # a dose within the tolerance
        if detail:
            cap = (f"Weighed on the HR-202i: the doser doses by auger turns, so the balance checks every cup. The "
                   f"door opens (driven: assumed; the HR-i's doors are manual) and the cup goes onto the pan.")
            L.note(0, "Arm", f"cup {i + 1}: doser to the balance")
        sc.step(st, cap, 1.1 * f, rb.joint_to(Tw=lvl(p1 + (0, -200, 0))), hold=H(0.05), cam_to=CAM_WORK if detail else None)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(p1 + (0, 0, 2))), hold=H(0.0))
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1 + (0, -200, 2))), hold=H(0.05))
        cam_bal = cam_near(K.bal_cup(), (360.0, -660.0, 330.0), (0.0, 0.0, 55.0))
        sc.step(st, cap, 1.4 * f, both(rb.joint_to(Tw=lvl(q + (0, -150, 2))), K.to(door=DOOR_OPEN)), hold=H(0.05),
                cam_to=cam_bal if detail else None)
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(q + (0, 0, 2))), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(q)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
        rb.release("bal")
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q + (0, -150, 0))), hold=H(0.05))
        if detail:
            cap = (f"Door shut, reading: {read:.4f} g, the cup's {m['cup']:.4f} g (weighed once, when it was turned) "
                   f"plus {read - m['cup']:.4f} g of {pw} against {m['dose']:.4f} g. Inside ±{TOL * 100:.0f} % "
                   f"(assumed), it goes on; a short cup would go back to the doser for a top-up, as the trickler "
                   f"does on the HR-100A.")
        sc.step(st, cap, 0.6 * f, K.to(door=0.0), hold=H(0.05))

        def settle(u, read=read):
            v = m["cup"] + (read - m["cup"]) * min(1.0, u * 1.25) + (0.0007 * math.sin(u * 19) * (1 - u))
            L.note(2, "HR-202i", f"{v:.4f} g{'  stable' if u > 0.85 else ''}")
        sc.step(st, cap, 1.4 * f, settle, hold=1.6 if detail else 0.0)
        sc.step(st, cap, 0.6 * f, K.to(door=DOOR_OPEN), hold=H(0.05))
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        L.note(2, "HR-202i", "0.0000 g")
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(q + (0, 0, 2))), hold=H(0.0))
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q + (0, -150, 2))), hold=H(0.05))
        sc.step(st, cap, 0.5 * f, K.to(door=0.0), hold=H(0.0))
        # -------------------------------------------------- to the press, plug on
        if detail:
            st = f"4/{n}"
            cap = (f"Dosed: {m['dose']:.2f} g of {pw}, {m['fill']:.1f} mm up the bore. The arm lowers the cup onto "
                   f"the press nest's ejector, which draws it down into #222's steel sleeve: F1 is bored to the cup's "
                   f"OD + .0005 in, so the wall can't bulge. Then the cup's own plug, from above.")
            L.note(0, "Arm", f"cup {i + 1}: balance to the press")
        sc.step(st, cap, 0.5 * f, K.to(eject=C.PR["eject"]), hold=H(0.0))
        q_up = K.nest_seat(C.PR["eject"]) + (0, 0, CUP_GRASP)
        cam_press = cam_near(K.nest_seat(0.0), (-520.0, -760.0, 470.0), (60.0, 0.0, 60.0))
        # the nest is reached from above, level: a straight approach from the front would carry the wrist across the
        # line through the arm's base (a wrist flip), since the press stands beside the arm, not in front of it
        sc.step(st, cap, 1.5 * f, rb.joint_to(Tw=lvl(q_up + (0, 0, 150))), hold=H(0.05),
                cam_to=cam_press if detail else None)
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(q_up + (0, 0, 1))), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
        rb.release("press_ej")
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(q_up + (0, 0, 150))), hold=H(0.05))
        sc.step(st, cap, 0.8 * f, K.to(eject=0.0), hold=H(0.05))
        L.note(3, "Press", "cup in F1, ejector down")
        if detail:
            L.note(0, "Arm", f"plug {i + 1}: rack to cup")
        g0 = K.rack_plug(i) + (0, 0, PLUG_GRASP)
        sc.step(st, cap, 1.4 * f, both(rb.joint_to(Tw=dwn(g0 + (0, 0, 120))), rb.grip_to(OPEN_PLUG)), hold=H(0.05),
                cam_to=CAM_RACK if detail else None)
        sc.step(st, cap, 0.7 * f, rb.line_to(dwn(g0)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_PLUG), hold=H(0.05))
        rb.grasp(f"plug{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g0 + (0, 0, 120))), hold=H(0.05))
        lead = C.PLUG_LEADIN_L * 0.98                       # the lead-in lets the plug stand 1.5 mm in the mouth
        top = K.nest_seat(0.0) + (0, 0, C.SLUG_L)
        g1 = top + (0, 0, PLUG_GRASP - lead)
        sc.step(st, cap, 1.3 * f, rb.joint_to(Tw=dwn(g1 + (0, 0, 110))), hold=H(0.05),
                cam_to=cam_near(K.nest_seat(0.0), (-330.0, -480.0, 300.0), (30.0, 0.0, 60.0)) if detail else None)
        sc.step(st, cap, 0.8 * f, rb.line_to(dwn(g1 + (0, 0, 3))), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.line_to(dwn(g1)), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.grip_to(OPEN_PLUG), hold=H(0.05))
        rb.release(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g1 + (0, 0, 140))), hold=H(0.05))
        sc.step(st, cap, 1.0 * f, rb.joint_to(A.PARK_RAD), hold=H(0.05))
        L.note(0, "Arm", "parked")
        # -------------------------------------------------- press
        if detail:
            cap = ("The nest slides in under the ram. The ram comes down and presses the plug flush: F1 is as long as "
                   "the cup, so the ram bottoms out on it. Cut open: the plug closes the bore over the powder; the air "
                   "it pushes out leaves through its 1/16 in vent, the same way the chamber's air will on pump-down.")
            L.note(3, "Press", "nest in")
        nest_in = K._w("press", (0.0, C.PR["ram_y"], C.PR["nest_top"]))
        sc.step(st, cap, 1.0 * f, K.to(nest_y=C.PR["ram_y"]), hold=H(0.05),
                cam_to=cam_near(nest_in, (55.0, -205.0, 52.0), (0.0, 0.0, 44.0)) if detail else None)
        if detail:
            K.cut(i, True, sleeve=True)
        plug_top0 = C.PR["sleeve_top"] - lead + C.PLUG_L
        sc.step(st, cap, 1.0 * f, K.to(ram_z=plug_top0), hold=H(0.05))
        L.note(3, "Press", "pressing the plug")
        pl_local = sc.gmat[f"plug{i}"].copy()

        def press(u, i=i):
            K.ram_z = plug_top0 + (C.PR["sleeve_top"] - plug_top0) * u
            K.apply()
            sc.gmat[f"plug{i}"] = T((0, 0, -(C.PLUG_L - lead) * u)) @ pl_local     # 8 mm, to flush
            on = 0.1 < u < 0.97 and detail
            sc.alpha["puff"] = 1.0 if on else 0.0
            if on:
                vent = K._w(f"plug{i}", (0, 0, C.PLUG_L))
                kk = np.arange(12)
                s = (kk / 12 + u * 3.0) % 1.0
                ang = kk * 2.4
                r = 3.0 + 14.0 * s
                sc.set_mesh("puff", pv.PolyData(np.c_[vent[0] + r * np.cos(ang) * 0.5 - 4.0 * s,
                                                      vent[1] + r * np.sin(ang) * 0.5 - 4.0 * s,
                                                      vent[2] + 1.0 + 1.5 * s]))
        sc.step(st, cap, 2.2 * f, press, hold=0.6 if detail else 0.0)
        sc.alpha["puff"] = 0.0
        L.note(3, "Press", "plug home, flush; ram up")
        sc.step(st, cap, 0.8 * f, K.to(ram_z=C.PR["ram_up"]), hold=0.2 if detail else 0.0)
        K.cut(i, False, sleeve=True)
        sc.step(st, cap, 0.9 * f, K.to(nest_y=C.PR["out_y"]), hold=H(0.05))
        sc.step(st, cap, 0.6 * f, K.to(eject=C.PR["eject"] * 0.9), hold=H(0.05))
        L.note(3, "Press", "nest out, cup ejected")
        made[metal] += 1
        charge_line()
        # -------------------------------------------------- away
        q = K.nest_seat(C.PR["eject"] * 0.9) + (0, 0, CUP_GRASP)
        if detail:
            cap = (f"The charged cup, {m['cup'] + m['dose'] + m['plug']:.1f} g, goes onto the carrier on the MiR250's "
                   f"cabinet, beside the arm, for the atomizer.")
            L.note(0, "Arm", f"cup {i + 1}: press to the MiR's carrier")
        sc.step(st, cap, 1.2 * f, both(rb.joint_to(Tw=lvl(q + (0, 0, 150))), rb.grip_to(OPEN_CUP)), hold=H(0.05),
                cam_to=cam_press if detail else None)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q + (0, 0, 150))), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, K.to(eject=0.0), hold=H(0.0))
        if metal == "Al":
            c = K.carrier_seat(k_al) + (0, 0, CUP_GRASP)
            d = np.array([0.0, -1.0, 0.0])
            sc.step(st, cap, 1.6 * f, rb.joint_to(Tw=lvl(c - d * 170 + (0, 0, 40), d)), hold=H(0.05),
                    cam_to=CAM_AMR if detail else None)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 40), d)), hold=H(0.05))
            sc.step(st, cap, 0.6 * f, rb.line_to(lvl(c + (0, 0, 1), d)), hold=H(0.05))
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
            rb.release("amr")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c - d * 170, d)), hold=H(0.05))
        else:
            c = K.rack_cup(i) + (0, 0, CUP_GRASP)
            sc.step(st, cap, 1.4 * f, rb.joint_to(Tw=lvl(c + (0, -150, 30))), hold=H(0.05))
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 30))), hold=H(0.05))
            sc.step(st, cap, 0.5 * f, rb.line_to(lvl(c + (0, 0, 1))), hold=H(0.05))
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
            rb.release("crack")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, -150, 0))), hold=H(0.05))
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=H(0.1))
        L.note(0, "Arm", "parked")

    # ------------------------------------------------------------------ 2. the Si funnel into the fork
    cap = ("The Si funnel goes into the doser's fork. It is only ever used for Si, and its stem points into the cup's "
           "bore without touching it, so nothing passes from one powder or one cup to the next.")
    with_caption(sc, cap, lambda: funnel_to_station("Si", f"2/{n}", 0.8,
                                                    cam=cam_near(K.station_funnel(), (330.0, -650.0, 230.0),
                                                                 (-60.0, 0.0, 10.0))))
    # ------------------------------------------------------------------ 3-4. the first Al cup in full
    cycle(0, fast=False)
    # ------------------------------------------------------------------ 5. the other three Al cups, faster
    cap = (f"The same for the other three Al cups, shown faster: {ms['Al']['dose']:.2f} g of Si each, every one "
           f"weighed. Four cups make the run's {al['charge_g']:.1f} g of Al-10Si.")
    sc.step(f"5/{n}", cap, 0.6, None, hold=1.4, cam_to=CAM_WORK)
    for i in (1, 2, 3):
        with_caption(sc, cap, lambda i=i: cycle(i, fast=True))
    # ------------------------------------------------------------------ 6. the funnel swap
    cap = ("Before the Ni goes in, the Si funnel comes out and goes back to its place on the stand, and the Ni "
           "funnel takes the fork. One funnel per powder: a funnel that has carried Si never carries Ni.")
    with_caption(sc, cap, lambda: funnel_to_stand("Si", f"6/{n}", 0.4, cam=cam_near(
        K.station_funnel(), (520.0, -900.0, 330.0), (90.0, -60.0, 0.0))))
    with_caption(sc, cap, lambda: funnel_to_station("Ni", f"6/{n}", 0.4))
    # ------------------------------------------------------------------ 7. the four Cu cups
    cap = (f"Then the four Cu cups with {ms['Cu']['dose']:.2f} g of Ni each. A Cu cup with its plug and Ni is "
           f"{ms['Cu']['cup'] + ms['Cu']['plug'] + ms['Cu']['dose']:.0f} g, well inside the HR-202i's 220 g. The Cu "
           f"cups go back on the rack for their own run.")
    sc.step(f"7/{n}", cap, 0.6, None, hold=1.4, cam_to=CAM_WORK)
    for i in (4, 5, 6, 7):
        with_caption(sc, cap, lambda i=i: cycle(i, fast=True))
    with_caption(sc, cap, lambda: funnel_to_stand("Ni", f"7/{n}", 0.25))
    # ------------------------------------------------------------------ 8. tray B up; ready for the atomizer
    cap = (f"Made up: four Al-10Si cups, {al['charge_g']:.1f} g together, on the MiR250 for the rePowder, and four "
           f"90/10 Cu-Ni cups on the rack, {cu['charge_g']:.1f} g, for their own run (designed compositions, if every "
           f"gram dissolves; out/alloy_recipe.json). Tray B goes back into storage.")
    L.store("B", f"8/{n}", cap, cam=CAM_AMR)
    L.note(0, "Arm", "parked; next: the atomizer")
    sc.step(f"8/{n}", cap, 1.6, None, hold=2.0, still=True,
            cam_to=cam_near(K.carrier_seat(1) + (17, 0, 0), (-600.0, -640.0, 340.0), (0.0, 0.0, 25.0)),
            labels=[("four charged 5N Al cups, for the rePowder", K.carrier_seat(1) + (17, 0, 90), (0.30, 0.25))])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; opening top {V.Z_OPEN_TOP:.0f} mm", flush=True)
    print(f"{sc.n} frames, {sc.n / scene.FPS:.1f} s", flush=True)
    return sc.save()


def with_caption(sc, cap, fn):
    """Run fn() with every sub-step that has no caption of its own given `cap`."""
    orig = sc.step

    def step(label, caption, *a, **kw):
        return orig(label, caption if caption is not None else cap, *a, **kw)
    sc.step = step
    try:
        fn()
    finally:
        sc.step = orig


def tray_xyz(L: A.Lab, xyz) -> np.ndarray:
    return (L.sc.world("tray_B") @ np.r_[np.asarray(xyz, float), 1.0])[:3]


RECIPE = C.recipe()

if __name__ == "__main__":
    movie()

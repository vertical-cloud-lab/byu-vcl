"""The alloy workflow, start to finish (#303), chapter 1: the atomizer charge, made up on tray B of the VLM.

    xvfb-run -a python3 alloy_charge.py            # -> out/alloy_charge.gif, out/mp4/alloy_charge.mp4, .json, stills
    PREVIEW=1 xvfb-run -a python3 alloy_charge.py  # the last frame of each sub-step -> /tmp/preview_alloy_charge.png

This replaces round 2's vial (``animate.workflow``: a 20 mL vial dosed, then liquid added in the CubXL). The rePowder
melts what it is given as **charge cups**: the lab's own (#222, ``charge.py``), turned from high-purity bar, each
filled with powder by the multi-doser and closed with a vented plug pressed into its bore. The rack on tray B holds
two 5N Al cups, for this run's Al-10Si, and two oxygen-free Cu cups, for a 90/10 Cu-Ni run (DAL #162, #219), with a
plug of the same metal for each. The arm takes each cup to the doser, then to a press, sets its plug and the press
pushes it home inside #222's steel sleeve (F1). The Al cups go onto the MiR250's carrier for the atomizer (chapter 2,
``alloy_atomize.py``); the Cu cups go back on the rack, and tray B back into storage.

Every arm move is a straight line of the grasp point or a joint move between two solved poses (``robot.py``), as in
``animate.workflow``. The cups are always held level (fingers closing sideways), so a cup never tilts in the gripper;
the plugs are taken from above. Close-ups cut the cup, powder, plug and sleeve in half (``charge.lathe``).
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import scene
scene.GIF_FPS = 6                      # a ~2.5-minute GIF under 4.9 MB (the MP4 keeps every frame, 15 fps)
scene.GIF_SIZE = (640, 360)
from scene import Scene, T, S  # noqa: E402

import animate as A                    # noqa: E402
import carousel as CR                  # noqa: E402
import charge as C                     # noqa: E402
import lab                             # noqa: E402
import props as P                      # noqa: E402
import vlm as V                        # noqa: E402
from robot import both                 # noqa: E402

NAME = "alloy_charge"
TITLE = "Vertical cloud lab, the alloy route 1/4: the atomizer charge"
RACK_AT = (-250.0, -372.0)             # tray B frame: where round 2's vial rack stood (animate.LOADS)
PRESS_AT = (-610.0, -250.0)
SLOTS = [("Al", "Si"), ("Al", "Si"), ("Cu", "Ni"), ("Cu", "Ni")]     # rack seat -> (cup metal, powder)
MODULE = {"Si": 5, "Ni": 2}            # carousel modules (0-based) holding the two powders
CUP_GRASP = 45.0                       # grasp point above a cup's base (its top 18.5 mm higher)
PLUG_GRASP = 21.5                      # above a plug's base: the pads' lower ends 2 mm over the cup's rim
GRIP_CUP = 0.80                        # 2F-85 closure on the 19.05 mm cup: gap = 28 - 90 (c - 0.70) (ur_arm.gripper_fk)
GRIP_PLUG = 0.87                       # on the 12.7 mm plug
OPEN_CUP = 0.66                        # 31.6 mm between the pads: clear of a neighbouring cup in a pocket row
OPEN_PLUG = 0.60
CARRIER_LOCAL = A.BUFFER_LOCAL         # the MiR's cup carrier stands where round 2's one-vial holder stood
METAL_C = {"Al": C.AL_5N, "Cu": C.CU}
CUP_NAME = {"Al": "5N Al", "Cu": "OFE Cu"}

CAM_WORK = [(-1500, -4300, 2500), (-260, -1450, 1020), (0, 0, 1)]
CAM_RACK = [(-1150, -2650, 1800), (-330, -1360, 960), (0, 0, 1)]


def cam_near(p, off, look=(0.0, 0.0, 0.0)):
    """A camera at p + off looking at p + look (world)."""
    p = np.asarray(p, float)
    return [tuple(p + off), tuple(p + np.asarray(look, float)), (0, 0, 1)]
CAM_AMR = [(1300, -4100, 1900), (-250, -1900, 1000), (0, 0, 1)]

RECIPE = C.recipe()


def lvl(p, toward=(0.0, 1.0, 0.0)):
    """Gripper level, pointing along `toward`, fingers closing sideways (props.tcp_frame)."""
    return P.tcp_frame(np.asarray(p, float), toward, 0.0)


def dwn(p):
    """Gripper pointing straight down, fingers closing along world x (along a rack's row)."""
    return P.tcp_frame(np.asarray(p, float), (0, 0, -1), 0.0)


class Charge:
    """The charge rack, the press, the cups and plugs, and the MiR's carrier, added to round 2's scene (``A.Lab``);
    the vial, its rack and the one-vial holder are hidden."""

    def __init__(self, sc: Scene, L: A.Lab):
        self.sc, self.L = sc, L
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
        # the MiR's carrier
        mesh, self.carrier_seats = C.carrier()
        sc.add("amr/carrier", mesh.translate((*CARRIER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, "amr")
        self.carrier_base = np.array([*CARRIER_LOCAL, P.AMR_TOP - 20])
        # cups and plugs, in the rack
        unit, point = C.unit_powder(cut=True), C.drill_point_fill(cut=True)
        self.powder_h = [0.0] * len(SLOTS)
        self.plugged = [False] * len(SLOTS)
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
        for i in range(len(SLOTS)):
            h = self.powder_h[i]
            sc.gmat[f"cup{i}_pw"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, max(h, 0.01)))

    def cut(self, i, on: bool, sleeve=False):
        """Swap cup i (and its plug, and F1) for the half-section versions."""
        sc = self.sc
        sc.alpha[f"cup{i}/whole"] = 0.0 if on else 1.0
        sc.alpha[f"cup{i}/cut"] = 1.0 if on else 0.0
        sc.alpha[f"plug{i}/whole"] = 0.0 if on else 1.0
        sc.alpha[f"plug{i}/cut"] = 1.0 if on else 0.0
        shown = on and self.powder_h[i] > 0.05
        sc.alpha[f"cup{i}/point"] = 1.0 if on and self.powder_h[i] > -1 and self._point[i] else 0.0
        sc.alpha[f"cup{i}/powder"] = 1.0 if shown else 0.0
        if sleeve is not None:
            sc.alpha["press/sleeve"] = 0.0 if (on and sleeve) else 1.0
            sc.alpha["press/sleeve_cut"] = 1.0 if (on and sleeve) else 0.0

    _point = [False] * len(SLOTS)

    def to(self, **kw):
        """An update(u) easing nest_y / ram_z / eject to the given values."""
        start = {k: getattr(self, k) for k in kw}

        def up(u):
            for k, v in kw.items():
                setattr(self, k, start[k] + (v - start[k]) * u)
            self.apply()
        return up

    # ------------------------------------------------------------------------------------------ places (world)
    def rack_cup(self, i):
        return (self.sc.world("crack") @ np.r_[self.seats["cup"][i], 1.0])[:3]

    def rack_plug(self, i):
        return (self.sc.world("crack") @ np.r_[self.seats["plug"][i], 1.0])[:3]

    def nest_seat(self, eject):
        """Base centre of a cup on the ejector, world, with the nest out."""
        return (self.sc.world("press") @ np.r_[0.0, C.PR["out_y"], C.PR["nest_top"] + eject, 1.0])[:3]

    def carrier_seat(self, k):
        return (self.sc.world("amr") @ np.r_[self.carrier_base + self.carrier_seats[k], 1.0])[:3]


def doser_seat_rig() -> np.ndarray:
    """Base centre of a cup in the doser (rig frame): its rim at the catch funnel's spout, as the vial's mouth was
    (assumed: a deeper printed holder in place of the vial cup)."""
    import layout as CL
    return np.array([CR.VIAL_XY[0], CR.VIAL_XY[1], float(CL.FUNNEL_SPOUT_Z) - C.SLUG_L])


def stream_points(L: A.Lab, K: Charge, i: int, t: float, on: float) -> np.ndarray:
    """The dose stream from the auger's outlet into cup i's bore, rig frame: grains falling under gravity."""
    top = L.carousel.exit_point()
    seat = doser_seat_rig()
    bottom_z = seat[2] + C.FLOOR_Z + K.powder_h[i] + 1.0
    n = 40
    s = (np.arange(n) / n + t * 1.7) % 1.0
    s = s[s < on]
    if not len(s):
        return np.zeros((0, 3))
    x = top[0] + (seat[0] - top[0]) * s ** 0.5
    y = np.full_like(s, top[1]) + np.sin(np.arange(len(s)) * 2.3) * 0.8
    z = top[2] - (top[2] - bottom_z) * s ** 2
    return np.c_[x, y, z]


def movie():
    data = lab.meshes()
    sc = Scene(NAME, TITLE)
    sc.cam = list(A.CAM_WIDE)
    L = A.Lab(sc, data, robot=True, highlight=MODULE["Si"])
    K = Charge(sc, L)
    rb, car = L.robot, L.carousel
    sc.parent["stream"] = L.eq_groups["B"][1]
    run = RECIPE["runs"]
    al, cu = run["Al-10Si"], run["Cu-10Ni"]
    dose_g = {"Si": al["cups"][0]["powder_g"], "Ni": cu["cups"][0]["powder_g"]}
    cup_g = {"Al": al["cups"][0]["cup_g"], "Cu": cu["cups"][0]["cup_g"]}
    fill = {"Si": al["cups"][0]["fill_mm"], "Ni": cu["cups"][0]["fill_mm"]}
    plug_g = {"Al": al["cups"][0]["plug_g"], "Cu": cu["cups"][0]["plug_g"]}
    L.extra_gauges = [("Arm", f"{A.ROBOT_NAME}, parked"), ("Doser", "module 1 at the station"),
                      ("Load cell", "0.000 g"), ("Press", "nest out, ram up"), ("Charge", "0 of 4 cups made up")]
    L.apply_state()
    n = 7
    made = []

    def charge_line():
        L.note(4, "Charge", ", ".join(made) if made else "0 of 4 cups made up")

    # ------------------------------------------------------------------ 1. tray B down
    cap = ("The alloy route, start to finish. First the charge: the atomizer melts cups, the lab's own (#222), turned "
           "from high-purity bar, filled with powder and closed with a vented plug. Tray B holds two 5N Al cups for "
           "this run's Al-10Si and two oxygen-free Cu cups for a 90/10 Cu-Ni run, a plug for each. The arm asks for it.")
    sc.step(f"1/{n}", cap, 1.0, None, hold=0.6,
            labels=[("tray B: powder dosing and the charge", (V.TRAY_W / 2 - 300, *V.SLOTS["R3"]), (0.84, 0.34))])
    L.fetch("B", f"1/{n}", cap, cam=CAM_WORK)
    p_r = K.rack_cup(0)
    sc.step(f"1/{n}", cap, 1.6, None, hold=1.6, cam_to=CAM_RACK,
            labels=[("charge rack: 5N Al and OFE Cu cups (#222's cup, 3/4 x 2.5 in)", p_r + (40, 0, 60), (0.30, 0.20)),
                    ("their vented plugs, 1/2 x 3/8 in", K.rack_plug(2) + (0, 0, 20), (0.62, 0.30)),
                    ("plug press with #222's steel sleeve (F1)", K.nest_seat(0) + (0, 0, 200), (0.14, 0.42)),
                    ("multi-doser (powder-doser #185)", tray_xyz(L, (250, -250, 520)), (0.80, 0.16))])

    def cycle(i, fast):
        metal, pw = SLOTS[i]
        f = 0.38 if fast else 1.0
        st = f"{2 if i == 0 else 6}/{n}"
        # -------------------------------------------------- cup to the doser
        if not fast:
            cap = (f"The {A.ROBOT_NAME} takes an empty {CUP_NAME[metal]} cup from the rack, level from the front, and "
                   f"stands it under the multi-doser's funnel on its load cell, its rim at the spout.")
            L.note(0, "Arm", f"{CUP_NAME[metal]} cup {i + 1}: rack to doser")
        else:
            cap = None
        p0 = K.rack_cup(i) + (0, 0, CUP_GRASP)
        seat = (sc.world(L.eq_groups["B"][1]) @ np.r_[doser_seat_rig(), 1.0])[:3]
        p1 = seat + (0, 0, CUP_GRASP)
        sc.step(st, cap, 1.6 * f, both(rb.joint_to(Tw=lvl(p0 + (0, -150, 30))), rb.grip_to(OPEN_CUP)), hold=0.05,
                cam_to=None if fast else CAM_WORK)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(p0 + (0, 0, 30))), hold=0.0)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0 + (0, -150, 30))), hold=0.05)
        sc.step(st, cap, 1.4 * f, rb.joint_to(Tw=lvl(p1 + (0, -190, 6))), hold=0.05)
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.line_to(lvl(p1)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
        rb.release(L.eq_groups["B"][1])
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p1 + (0, -190, 0))), hold=0.05)
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=0.05, cam_to=None if fast else A.CAM_MID)
        L.note(0, "Arm", "parked, clear of the doser")
        # -------------------------------------------------- dose
        m = MODULE[pw]
        if not fast or car.state["shift"] != car.index_to(m):
            if not fast:
                cap = (f"The carousel brings module {m + 1} ({pw} powder) to the station and docks it. It tilts and its "
                       f"auger turns: the powder falls through the funnel into the cup's 1/2 in bore while the load "
                       f"cell counts it. Cut open here: the bore fills from the 118° drill point.")
            L.note(1, "Doser", f"indexing to module {m + 1} ({pw})")
            sc.step(st, cap, 2.2 * f, car.to(shift=car.index_to(m)), hold=0.1, cam_to=None if fast else A.CAM_DOSE)
        L.note(1, "Doser", f"module {m + 1} ({pw}) docking")
        ghost = MODULE[pw] == MODULE["Si"]
        cam_dose = cam_near(seat, (95.0, -205.0, 62.0), (0.0, 0.0, 40.0))
        sc.step(st, cap, 1.2 * f, both(car.to(ext=CR.DOCK_EXT, magnet_on=True), car.ghost(0.18) if ghost else None),
                hold=0.1, cam_to=None if fast else cam_dose)
        L.note(1, "Doser", f"module {m + 1} tilted, dosing {pw}")
        sc.step(st, cap, 1.3 * f, car.to(tilt=CR.TILT), hold=0.05)
        if not fast:
            K.cut(i, True, sleeve=None)
        spin0 = car.state["spin"]
        stt = car.to(spin=spin0 + 2 * math.pi * 2.0)
        target = fill[pw]
        over = cup_g[metal] + dose_g[pw] > 100.0

        def dose(u, i=i, pw=pw, target=target, stt=stt, metal=metal):
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
            if not fast:
                K.cut(i, True, sleeve=None)
            L.note(2, "Load cell", f"{cup_g[metal] + dose_g[pw] * k:.2f} g: cup {cup_g[metal]:.2f} + {pw} "
                                   f"{dose_g[pw] * k:.3f}" + ("  (over its 100 g)" if over else ""))
        sc.step(st, cap, 3.4 * f, dose, hold=0.3 if not fast else 0.05, live=False)
        sc.alpha["stream"] = 0.0
        K.powder_h[i] = target
        K._point[i] = True
        K.apply()
        L.note(1, "Doser", f"module {m + 1} back, undocking")
        sc.step(st, cap, 1.0 * f, car.to(tilt=0.0), hold=0.05)
        sc.step(st, cap, 0.7 * f, car.to(spin=spin0 + 2 * math.pi), hold=0.05)
        sc.step(st, cap, 0.9 * f, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0) if ghost else None), hold=0.1)
        K.cut(i, False, sleeve=None)
        L.note(1, "Doser", f"module {m + 1} undocked")
        # -------------------------------------------------- to the press, plug on
        st = f"{3 if i == 0 else 6}/{n}"
        if not fast:
            cap = (f"Dosed: {dose_g[pw]:.2f} g of {pw}, {fill[pw]:.1f} mm up the bore. The arm takes the cup to the "
                   f"press and lowers it onto the nest's ejector, which draws it down into #222's steel sleeve: F1 is "
                   f"bored to the cup's OD + .0005 in, so the wall can't bulge. Then the cup's own plug, from above.")
            L.note(0, "Arm", f"cup {i + 1}: doser to press")
        sc.step(st, cap, 1.1 * f, rb.joint_to(Tw=lvl(p1 + (0, -190, 0))), hold=0.05, cam_to=None if fast else CAM_WORK)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.4 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=0.0)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1 + (0, -190, 6))), hold=0.05)
        sc.step(st, cap, 0.5 * f, K.to(eject=C.PR["eject"]), hold=0.0)
        q_up = K.nest_seat(C.PR["eject"]) + (0, 0, CUP_GRASP)
        cam_press = cam_near(K.nest_seat(0.0), (-520.0, -760.0, 470.0), (60.0, 0.0, 60.0))
        sc.step(st, cap, 1.5 * f, rb.joint_to(Tw=lvl(q_up + (0, -170, 50))), hold=0.05,
                cam_to=None if fast else cam_press)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(q_up + (0, 0, 50))), hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q_up + (0, 0, 1))), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
        rb.release("press_ej")
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q_up + (0, -170, 0))), hold=0.05)
        sc.step(st, cap, 0.8 * f, K.to(eject=0.0), hold=0.05)
        L.note(3, "Press", "cup in F1, ejector down")
        # the plug, from above
        if not fast:
            L.note(0, "Arm", f"plug {i + 1}: rack to cup")
        g0 = K.rack_plug(i) + (0, 0, PLUG_GRASP)
        sc.step(st, cap, 1.4 * f, both(rb.joint_to(Tw=dwn(g0 + (0, 0, 120))), rb.grip_to(OPEN_PLUG)), hold=0.05,
                cam_to=None if fast else CAM_RACK)
        sc.step(st, cap, 0.7 * f, rb.line_to(dwn(g0)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_PLUG), hold=0.05)
        rb.grasp(f"plug{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g0 + (0, 0, 120))), hold=0.05)
        lead = C.PLUG_LEADIN_L * 0.98                       # the lead-in lets the plug stand 1.5 mm in the mouth
        top = K.nest_seat(0.0) + (0, 0, C.SLUG_L)
        g1 = top + (0, 0, PLUG_GRASP - lead)
        sc.step(st, cap, 1.3 * f, rb.joint_to(Tw=dwn(g1 + (0, 0, 110))), hold=0.05,
                cam_to=None if fast else cam_near(K.nest_seat(0.0), (-330.0, -480.0, 300.0), (30.0, 0.0, 60.0)))
        sc.step(st, cap, 0.8 * f, rb.line_to(dwn(g1 + (0, 0, 3))), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.line_to(dwn(g1)), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.grip_to(OPEN_PLUG), hold=0.05)
        rb.release(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g1 + (0, 0, 140))), hold=0.05)
        sc.step(st, cap, 1.0 * f, rb.joint_to(A.PARK_RAD), hold=0.05)
        L.note(0, "Arm", "parked")
        # -------------------------------------------------- press
        if not fast:
            cap = ("The nest slides in under the ram. The ram comes down and presses the plug flush: F1 is as long as "
                   "the cup, so the ram bottoms out on it. Cut open: the plug closes the bore over the powder; the air "
                   "it pushes out leaves through its 1/16 in vent, the same way the chamber's air will on pump-down.")
            L.note(3, "Press", "nest in")
        nest_in = (sc.world("press") @ np.r_[0.0, C.PR["ram_y"], C.PR["nest_top"], 1.0])[:3]
        sc.step(st, cap, 1.0 * f, K.to(nest_y=C.PR["ram_y"]), hold=0.05,
                cam_to=None if fast else cam_near(nest_in, (70.0, -260.0, 70.0), (0.0, 0.0, 42.0)))
        if not fast:
            K.cut(i, True, sleeve=True)
        plug_top0 = C.PR["sleeve_top"] - lead + C.PLUG_L
        sc.step(st, cap, 1.0 * f, K.to(ram_z=plug_top0), hold=0.05)
        L.note(3, "Press", "pressing the plug")
        pl_local = sc.gmat[f"plug{i}"].copy()

        def press(u, i=i):
            K.ram_z = plug_top0 + (C.PR["sleeve_top"] - plug_top0) * u
            K.apply()
            sc.gmat[f"plug{i}"] = T((0, 0, -(C.PLUG_L - lead) * u)) @ pl_local     # 8 mm, to flush
            on = 0.1 < u < 0.97 and not fast
            sc.alpha["puff"] = 1.0 if on else 0.0
            if on:
                vent = (sc.world(f"plug{i}") @ np.r_[0, 0, C.PLUG_L, 1.0])[:3]
                k = np.arange(12)
                s = (k / 12 + u * 3.0) % 1.0
                ang = k * 2.4
                r = 3.0 + 14.0 * s
                sc.set_mesh("puff", pv.PolyData(np.c_[vent[0] + r * np.cos(ang) * 0.5 - 4.0 * s,
                                                      vent[1] + r * np.sin(ang) * 0.5 - 4.0 * s,
                                                      vent[2] + 1.0 + 1.5 * s]))
        sc.step(st, cap, 2.2 * f, press, hold=0.6 if not fast else 0.05)
        sc.alpha["puff"] = 0.0
        L.note(3, "Press", "plug home, flush; ram up")
        sc.step(st, cap, 0.8 * f, K.to(ram_z=C.PR["ram_up"]), hold=0.2 if not fast else 0.0)
        K.cut(i, False, sleeve=True)
        sc.step(st, cap, 0.9 * f, K.to(nest_y=C.PR["out_y"]), hold=0.05)
        sc.step(st, cap, 0.6 * f, K.to(eject=C.PR["eject"] * 0.9), hold=0.05)
        L.note(3, "Press", "nest out, cup ejected")
        made.append(f"{CUP_NAME[metal]} + {pw}")
        charge_line()
        # -------------------------------------------------- away
        st = f"{4 if i == 0 else 6}/{n}"
        q = K.nest_seat(C.PR["eject"] * 0.9) + (0, 0, CUP_GRASP)
        dest_al = metal == "Al"
        if not fast:
            cap = (f"The charged cup, {cup_g[metal] + dose_g[pw] + plug_g[metal]:.1f} g, "
                   f"goes onto the carrier on the MiR250's cabinet, beside the arm, for the atomizer.")
            L.note(0, "Arm", f"cup {i + 1}: press to the MiR's carrier")
        sc.step(st, cap, 1.2 * f, both(rb.joint_to(Tw=lvl(q + (0, -170, 0))), rb.grip_to(OPEN_CUP)), hold=0.05,
                cam_to=None if fast else cam_near(K.nest_seat(0.0), (-520.0, -760.0, 470.0), (60.0, 0.0, 60.0)))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(q + (0, 0, 40))), hold=0.0)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q + (0, -170, 40))), hold=0.05)
        sc.step(st, cap, 0.4 * f, K.to(eject=0.0), hold=0.0)
        if dest_al:
            k = [0, 1][i]
            c = K.carrier_seat(k) + (0, 0, CUP_GRASP)
            d = np.array([0.0, -1.0, 0.0])
            sc.step(st, cap, 1.6 * f, rb.joint_to(Tw=lvl(c - d * 170 + (0, 0, 40), d)), hold=0.05,
                    cam_to=None if fast else CAM_AMR)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 40), d)), hold=0.05)
            sc.step(st, cap, 0.6 * f, rb.line_to(lvl(c + (0, 0, 1), d)), hold=0.05)
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
            rb.release("amr")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c - d * 170, d)), hold=0.05)
        else:
            c = K.rack_cup(i) + (0, 0, CUP_GRASP)
            sc.step(st, cap, 1.4 * f, rb.joint_to(Tw=lvl(c + (0, -150, 30))), hold=0.05)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 30))), hold=0.05)
            sc.step(st, cap, 0.5 * f, rb.line_to(lvl(c + (0, 0, 1))), hold=0.05)
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
            rb.release("crack")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, -150, 0))), hold=0.05)
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=0.1)
        L.note(0, "Arm", "parked")

    cycle(0, fast=False)
    # ------------------------------------------------------------------ 5-6. the other three, faster
    cap = (f"The same for the second Al cup ({dose_g['Si']:.2f} g Si), then the two Cu cups with Ni "
           f"({dose_g['Ni']:.2f} g each), shown faster. A Cu cup alone is {cup_g['Cu']:.0f} g: over the doser's 100 g "
           f"load cell (TAL221), so Cu cups need a bigger cell. The Cu cups go back on the rack for their own run.")
    sc.step(f"5/{n}", cap, 0.6, None, hold=1.6, cam_to=CAM_WORK)
    globals()["_CAP6"] = cap
    for i in (1, 2, 3):
        _cycle_fast(cycle, sc, i, cap)
    # ------------------------------------------------------------------ 7. tray B up; ready for the atomizer
    cap = (f"Made up: two Al-10Si cups, {al['charge_g']:.1f} g together, on the MiR250 for the rePowder, and two "
           f"90/10 Cu-Ni cups on the rack, {cu['charge_g']:.1f} g, for their own run (designed compositions, if every "
           f"gram dissolves; out/alloy_charge.json). Tray B goes back into storage.")
    L.store("B", f"7/{n}", cap, cam=CAM_AMR)
    L.note(0, "Arm", "parked; next: the atomizer")
    sc.step(f"7/{n}", cap, 1.6, None, hold=2.4, still=True,
            cam_to=cam_near(K.carrier_seat(0) + (17, 0, 0), (520.0, -700.0, 380.0), (0.0, 0.0, 30.0)),
            labels=[("two charged 5N Al cups, for the rePowder", K.carrier_seat(0) + (17, 0, 90), (0.30, 0.25))])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; opening top {V.Z_OPEN_TOP:.0f} mm", flush=True)
    return sc.save()


def _cycle_fast(cycle, sc, i, cap):
    """A faster cycle with the shared caption (cycle() leaves the caption to its caller when fast)."""
    orig = sc.step

    def step(label, caption, *a, **kw):
        return orig(label, caption if caption is not None else cap, *a, **kw)
    sc.step = step
    try:
        cycle(i, fast=True)
    finally:
        sc.step = orig


def tray_xyz(L: A.Lab, xyz) -> np.ndarray:
    return (L.sc.world("tray_B") @ np.r_[np.asarray(xyz, float), 1.0])[:3]


if __name__ == "__main__":
    movie()

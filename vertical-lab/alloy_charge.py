"""The alloy workflow, start to finish (#303), chapter 1: the atomizer charge, made up on tray B of the VLM.

    xvfb-run -a python3 alloy_charge.py            # -> out/alloy_charge.gif, out/mp4/alloy_charge.mp4, .json, stills
    PREVIEW=1 xvfb-run -a python3 alloy_charge.py  # the last frame of each sub-step -> /tmp/preview_alloy_charge.png

This replaces round 2's vial (``animate.workflow``: a 20 mL vial dosed, then liquid added in the CubXL). The rePowder
melts what it is given as **charge cups**: the lab's own (#222, ``charge.py``), turned from high-purity bar, each
filled with powder by the multi-doser and closed with a vented plug pressed into its bore. The rack on tray B holds
two 5N Al cups, for this run's Al-10Si, and two oxygen-free Cu cups, for a 90/10 Cu-Ni run (DAL #162, #219), with a
plug of the same metal for each. The arm takes each cup to the doser, which fills its bore to where the plug will
stand (the alloying powder, then a top-up of the cup's own metal), then to a vacuum press (``alloy_press.py``: a Specac
Atlas Autotouch 15T and the lab's evacuable die round #222's F1 sleeve), which pumps the die down and drives the plug
home to flush on a set load, compacting the powder under vacuum (DAL #140). The Al cups go onto the MiR250's carrier for the atomizer (chapter 2,
``alloy_atomize.py``); the Cu cups go back on the rack, and tray B back into storage.

Every arm move is a straight line of the grasp point or a joint move between two solved poses (``robot.py``), as in
``animate.workflow``; joint moves are collision-checked and planned round obstacles (``collide.py``). The cups are always held level (fingers closing sideways), so a cup never tilts in the gripper;
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
import alloy_press as AP               # noqa: E402
import charge as C                     # noqa: E402
import vacuum_press as VPm             # noqa: E402
import lab                             # noqa: E402
import props as P                      # noqa: E402
import vlm as V                        # noqa: E402
from robot import both                 # noqa: E402

NAME = "alloy_charge"
TITLE = "Vertical cloud lab, the alloy route 1/4: the atomizer charge"
RACK_AT = (-250.0, -372.0)             # tray B frame: where round 2's vial rack stood (animate.LOADS)
PRESS_AT = (-610.0, -250.0)
SLOTS = [("Al", "Si"), ("Al", "Si"), ("Cu", "Ni"), ("Cu", "Ni")]     # rack seat -> (cup metal, powder)
MODULE = {"Si": 5, "Ni": 2, "AlSi10Mg": AP.TOPUP_MODULE["Al"], "Cu": AP.TOPUP_MODULE["Cu"]}   # carousel
#                                        modules (0-based): the two alloying powders and the two top-ups
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
    """The charge rack, the vacuum press (``alloy_press.VacPress``), the cups and plugs, and the MiR's carrier, added
    to round 2's scene (``A.Lab``); the vial, its rack and the one-vial holder are hidden. Each cup's bore holds two
    powder layers (the alloying powder, then the top-up of the cup's own metal), squeezed together when pressed."""

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
        # the vacuum press, its die and the punch's rest
        self.vp = AP.VacPress(sc, "tray_B", AP.PRESS_AT, V.T_FLOOR)
        # the MiR's carrier
        mesh, self.carrier_seats = C.carrier()
        sc.add("amr/carrier", mesh.translate((*CARRIER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, "amr")
        self.carrier_base = np.array([*CARRIER_LOCAL, P.AMR_TOP - 20])
        # cups and plugs, in the rack
        unit, point = C.unit_powder(cut=True), C.drill_point_fill(cut=True)
        self.powder_h = [0.0] * len(SLOTS)        # top of the alloying layer, above the bore floor (mm)
        self.powder_h2 = [0.0] * len(SLOTS)       # top of the top-up layer
        self.squeeze = [1.0] * len(SLOTS)         # pressing scales both layers by this
        self.plugged = [False] * len(SLOTS)
        for i, (metal, pw) in enumerate(SLOTS):
            g = f"cup{i}"
            top = AP.TOPUP[metal][0]
            sc.add(f"{g}/whole", C.cup(), METAL_C[metal], g, specular=0.7)
            sc.add(f"{g}/cut", C.cup(cut=True), METAL_C[metal], g, specular=0.7, shown=False)
            sc.add(f"{g}/point", point, C.POWDERS[pw][0], g, shown=False, specular=0.05)
            sc.add(f"{g}/powder", unit, C.POWDERS[pw][0], f"{g}_pw", shown=False, specular=0.05)
            sc.add(f"{g}/powder2", unit, AP.TOPUP_COL[top], f"{g}_pw2", shown=False, specular=0.05)
            for k in ("pw", "pw2"):
                sc.parent[f"{g}_{k}"] = g
                sc.gmat[f"{g}_{k}"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, 0.01))
            sc.parent[g] = "crack"
            sc.gmat[g] = T(self.seats["cup"][i])
            p = f"plug{i}"
            sc.add(f"{p}/whole", C.plug(), METAL_C[metal], p, specular=0.7)
            sc.add(f"{p}/cut", C.plug(cut=True), METAL_C[metal], p, specular=0.7, shown=False)
            sc.add(f"{p}/chan", VPm.channel_strip(), VPm.DARK, p)
            sc.add(f"{p}/chan_cut", VPm.channel_strip(cut=True), VPm.DARK, p, shown=False)
            sc.parent[p] = "crack"
            sc.gmat[p] = T(self.seats["plug"][i])
        self.apply()

    # ------------------------------------------------------------------------------------------ state
    def apply(self):
        sc = self.sc
        for i in range(len(SLOTS)):
            k = self.squeeze[i]
            h1, h2 = self.powder_h[i] * k, self.powder_h2[i] * k
            sc.gmat[f"cup{i}_pw"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, max(h1, 0.01)))
            sc.gmat[f"cup{i}_pw2"] = T((0, 0, C.FLOOR_Z + 0.05 + h1)) @ S((1, 1, max(h2 - h1, 0.01)))
        self.vp.apply()

    def cut(self, i, on: bool, sleeve=False):
        """Swap cup i (and its plug, and the die) for the half-section versions."""
        sc = self.sc
        sc.alpha[f"cup{i}/whole"] = 0.0 if on else 1.0
        sc.alpha[f"cup{i}/cut"] = 1.0 if on else 0.0
        sc.alpha[f"plug{i}/whole"] = 0.0 if on else 1.0
        sc.alpha[f"plug{i}/cut"] = 1.0 if on else 0.0
        sc.alpha[f"plug{i}/chan"] = 0.0 if on else 1.0
        sc.alpha[f"plug{i}/chan_cut"] = 1.0 if on else 0.0
        sc.alpha[f"cup{i}/point"] = 1.0 if on and self._point[i] else 0.0
        sc.alpha[f"cup{i}/powder"] = 1.0 if on and self.powder_h[i] > 0.05 else 0.0
        sc.alpha[f"cup{i}/powder2"] = 1.0 if on and self.powder_h2[i] > self.powder_h[i] + 0.05 else 0.0
        if sleeve is not None:
            self.vp.cutaway = bool(on and sleeve)
            self.vp.apply()

    _point = [False] * len(SLOTS)

    # ------------------------------------------------------------------------------------------ places (world)
    def rack_cup(self, i):
        return (self.sc.world("crack") @ np.r_[self.seats["cup"][i], 1.0])[:3]

    def rack_plug(self, i):
        return (self.sc.world("crack") @ np.r_[self.seats["plug"][i], 1.0])[:3]

    def nest_seat(self, eject=None):
        """Base centre of a cup on the press's raised ejector pin, shuttle out (world)."""
        return self.vp.cup_seat_at(VPm.VP["eject"] if eject is None else eject)

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
    bottom_z = seat[2] + C.FLOOR_Z + max(K.powder_h[i], K.powder_h2[i]) + 1.0
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
    PRES = AP.write_recipe()
    PRUN = {"Al": PRES["runs"]["Al-10Si"], "Cu": PRES["runs"]["Cu-10Ni"]}
    cup_g = {"Al": al["cups"][0]["cup_g"], "Cu": cu["cups"][0]["cup_g"]}
    L.extra_gauges = [("Arm", f"{A.ROBOT_NAME}, parked"), ("Doser", "module 1 at the station"),
                      ("Load cell", "0.000 g"), ("Press", "shuttle out, guard up"), ("Charge", "0 of 4 cups made up")]
    L.apply_state()
    n = 7
    made = []

    base_xy = sc.world(rb.root)[:2, 3].copy()           # the arm's base; the MiR stays parked for the chapter

    def aim(p, offs, prefer, step=15):
        """The horizontal direction to aim a level gripper at p: the clear one nearest `prefer`. offs lists the poses
        the moves use, as (distance back along the direction, height up) from p; each must have an IK solution clear of
        everything (collide.py), and the arm's own links, with what it holds. Square to the tray, a target near the
        arm's base or off to one side folds the arm into itself; the cups and the punch are round, so any horizontal
        approach grips them."""
        import collide
        chk = rb.checker()
        W = chk.snapshot()
        a0 = math.atan2(prefer[0], prefer[1])
        angs = sorted(range(-180, 180, step),
                      key=lambda g: abs((math.radians(g) - a0 + math.pi) % (2 * math.pi) - math.pi))
        inv = np.linalg.inv(sc.world(rb.root))
        for g in angs:
            a = math.radians(g)
            d = np.array([math.sin(a), math.cos(a), 0.0])
            ok = True
            for back, up in offs:
                Tb = inv @ lvl(np.asarray(p, float) - d * back + (0, 0, up), d)
                contact = back < 1 and up < 3
                good = False
                for q in collide.ik_all(rb.model, Tb, rb.q):
                    allow = chk.touching(q, rb.close, W) if contact else set()
                    if not chk.collisions(q, rb.close, W, allow, first=True):
                        good = True
                        break
                if not good:
                    ok = False
                    break
            if ok:
                return d
        print(f"warning: no clear level approach at {np.round(p).tolist()}", flush=True)
        return np.array([prefer[0], prefer[1], 0.0], float)

    def radial(p, ref=(0.0, 1.0), lim=35.0):
        """A level gripper aimed along the line from the arm's base to p, within `lim` degrees of `ref`. Square to
        the tray, a target near the base or off to one side folds the arm into itself; aimed from the base it
        reaches out instead (the cups and the punch are round, so any horizontal approach grips them)."""
        v = np.asarray(p[:2], float) - base_xy
        a, a0 = math.atan2(v[0], v[1]), math.atan2(ref[0], ref[1])
        da = (a - a0 + math.pi) % (2 * math.pi) - math.pi
        da = max(-math.radians(lim), min(math.radians(lim), da))
        return np.array([math.sin(a0 + da), math.cos(a0 + da), 0.0])

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
        f = 0.30 if fast else 1.0
        st = f"{2 if i == 0 else 6}/{n}"
        # -------------------------------------------------- cup to the doser
        if not fast:
            cap = (f"The {A.ROBOT_NAME} takes an empty {CUP_NAME[metal]} cup from the rack, level from the front, and "
                   f"stands it under the multi-doser's funnel on its load cell, its rim at the spout.")
            L.note(0, "Arm", f"{CUP_NAME[metal]} cup {i + 1}: rack to doser")
        else:
            cap = None
        p0 = K.rack_cup(i) + (0, 0, CUP_GRASP)
        d0 = d1 = aim(p0, [(150, 30), (0, 0), (0, 30)], radial(p0))
        seat = (sc.world(L.eq_groups["B"][1]) @ np.r_[doser_seat_rig(), 1.0])[:3]
        p1 = seat + (0, 0, CUP_GRASP)
        sc.step(st, cap, 1.6 * f, both(rb.joint_to(Tw=lvl(p0 - d0 * 150 + (0, 0, 30), d0)), rb.grip_to(OPEN_CUP)), hold=0.05,
                cam_to=None if fast else CAM_WORK)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0, d0)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(p0 + (0, 0, 30), d0)), hold=0.0)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0 - d0 * 150 + (0, 0, 30), d0)), hold=0.05)
        sc.step(st, cap, 1.4 * f, rb.joint_to(Tw=lvl(p1 + (0, -190, 6))), hold=0.05)
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.line_to(lvl(p1)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
        rb.release(L.eq_groups["B"][1])
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p1 + (0, -190, 0))), hold=0.05)
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=0.05, cam_to=None if fast else A.CAM_MID)
        L.note(0, "Arm", "parked, clear of the doser")
        # -------------------------------------------------- dose: the alloying powder, then the top-up to the plug
        top_name = AP.TOPUP[metal][0]
        pr = PRUN[metal]
        layers = [(pw, pr["alloying_g"], 0.0, pr["column_mm_alloying"]),
                  (top_name, pr["top_up_g"], pr["column_mm_alloying"], pr["column_mm_set"])]
        dosed = 0.0
        for kd, (pname, grams, h_from, h_to) in enumerate(layers):
            m = MODULE[pname]
            if not fast:
                if kd == 0:
                    cap = (f"The carousel brings module {m + 1} ({pname} powder) to the station and docks it. It tilts "
                           f"and its auger turns: {grams:.2f} g of {pname} falls through the funnel into the cup's 1/2 in "
                           f"bore while the load cell counts it. Cut open here: the bore fills from the 118° drill point.")
                else:
                    cap = (f"Then module {m + 1}, {pname}: {grams:.2f} g tops the bore up to where the plug will stand, "
                           f"{h_to:.0f} mm up, so the plug has powder to press. "
                           + ("AlSi10Mg is itself 10 % Si, so the cup stays Al-10Si." if metal == "Al" else
                              f"The Ni is {pr['alloying_g']:.1f} g so the cup stays Cu-10Ni with the Cu on top."))
            if not fast or car.state["shift"] != car.index_to(m):
                L.note(1, "Doser", f"indexing to module {m + 1} ({pname})")
                sc.step(st, cap, 2.2 * f, car.to(shift=car.index_to(m)), hold=0.1,
                        cam_to=None if fast or kd == 1 else A.CAM_DOSE)
            L.note(1, "Doser", f"module {m + 1} ({pname}) docking")
            ghost = kd == 0 and MODULE[pname] == MODULE["Si"]
            cam_dose = cam_near(seat, (95.0, -205.0, 62.0), (0.0, 0.0, 40.0))
            sc.step(st, cap, 1.2 * f, both(car.to(ext=CR.DOCK_EXT, magnet_on=True), car.ghost(0.18) if ghost else None),
                    hold=0.1, cam_to=None if fast else cam_dose)
            L.note(1, "Doser", f"module {m + 1} tilted, dosing {pname}")
            sc.step(st, cap, 1.3 * f, car.to(tilt=CR.TILT), hold=0.05)
            if not fast:
                K.cut(i, True, sleeve=None)
            spin0 = car.state["spin"]
            stt = car.to(spin=spin0 + 2 * math.pi * 2.0)
            over = cup_g[metal] + pr["alloying_g"] + pr["top_up_g"] > 100.0

            def dose(u, i=i, kd=kd, h_from=h_from, h_to=h_to, stt=stt, metal=metal, grams=grams, base=dosed,
                     pname=pname, over=over):
                stt(u)
                on = 1.0 if 0.05 < u < 0.95 else 0.0
                pts = stream_points(L, K, i, u * 6.0, on)
                sc.alpha["stream"] = 1.0 if len(pts) else 0.0
                if len(pts):
                    sc.set_mesh("stream", pv.PolyData(pts))
                k = min(1.0, max(0.0, (u - 0.12) / 0.83))
                if kd == 0:
                    K._point[i] = k > 0.02
                    K.powder_h[i] = h_to * max(0.0, (k - 0.08) / 0.92)
                    K.powder_h2[i] = K.powder_h[i]
                else:
                    K.powder_h2[i] = h_from + (h_to - h_from) * k
                K.apply()
                if not fast:
                    K.cut(i, True, sleeve=None)
                L.note(2, "Load cell", f"{cup_g[metal] + base + grams * k:.2f} g: cup {cup_g[metal]:.2f} + {pname} "
                                       f"{grams * k:.3f}" + ("  (over its 100 g)" if over else ""))
            sc.step(st, cap, 3.4 * f * (0.8 if kd == 1 else 1.0), dose, hold=0.3 if not fast else 0.05, live=False)
            sc.alpha["stream"] = 0.0
            dosed += grams
            if kd == 0:
                K.powder_h[i] = h_to
                K._point[i] = True
            K.powder_h2[i] = h_to
            K.apply()
            L.note(1, "Doser", f"module {m + 1} back, undocking")
            sc.step(st, cap, 1.0 * f, car.to(tilt=0.0), hold=0.05)
            sc.step(st, cap, 0.7 * f, car.to(spin=spin0 + 2 * math.pi), hold=0.05)
            sc.step(st, cap, 0.9 * f, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0) if ghost else None),
                    hold=0.1)
        K.cut(i, False, sleeve=None)
        L.note(1, "Doser", f"module {m + 1} undocked")
        # -------------------------------------------------- the plug, at the rack; then the cup onto the press's pin
        st = f"{3 if i == 0 else 6}/{n}"
        vp = K.vp
        if not fast:
            cap = (f"Dosed: {pr['alloying_g']:.2f} g of {pw} and {pr['top_up_g']:.2f} g of {top_name}, tapped "
                   f"{pr['column_mm_set']:.0f} mm up the bore. The cup goes back to the rack and its plug goes into the "
                   f"mouth there, on its 15° lead-in, 8.0 mm proud: low down, where the gripper can come at it from "
                   f"above. (The press works too high for that: the wrist would hit the VLM's opening.)")
            L.note(0, "Arm", f"cup {i + 1}: doser to rack")
        sc.step(st, cap, 1.1 * f, rb.joint_to(Tw=lvl(p1 + (0, -190, 0))), hold=0.05, cam_to=None if fast else CAM_WORK)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.4 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=0.0)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1 + (0, -190, 6))), hold=0.05)
        c_r = K.rack_cup(i) + (0, 0, CUP_GRASP)
        sc.step(st, cap, 1.3 * f, rb.joint_to(Tw=lvl(c_r - d1 * 150 + (0, 0, 30), d1)), hold=0.05, cam_to=None if fast else CAM_RACK)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r + (0, 0, 30), d1)), hold=0.05)
        sc.step(st, cap, 0.5 * f, rb.line_to(lvl(c_r + (0, 0, 1), d1)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
        rb.release("crack")
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r - d1 * 150, d1)), hold=0.05)
        if not fast:
            L.note(0, "Arm", f"plug {i + 1}: into its cup")
        g0 = K.rack_plug(i) + (0, 0, PLUG_GRASP)
        sc.step(st, cap, 1.2 * f, both(rb.joint_to(Tw=dwn(g0 + (0, 0, 120))), rb.grip_to(OPEN_PLUG)), hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(dwn(g0)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_PLUG), hold=0.05)
        rb.grasp(f"plug{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g0 + (0, 0, 120))), hold=0.05)
        lead = C.PLUG_LEADIN_L * 0.98                       # the lead-in lets the plug stand 1.5 mm in the mouth
        top = K.rack_cup(i) + (0, 0, C.SLUG_L)
        g1 = top + (0, 0, PLUG_GRASP - lead)
        sc.step(st, cap, 1.1 * f, rb.joint_to(Tw=dwn(g1 + (0, 0, 110))), hold=0.05)
        sc.step(st, cap, 0.8 * f, rb.line_to(dwn(g1 + (0, 0, 3))), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.line_to(dwn(g1)), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.grip_to(OPEN_PLUG), hold=0.05)
        rb.release(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g1 + (0, 0, 140))), hold=0.05)
        # the cup, its plug riding in the mouth, onto the raised pin of the die, out on its shuttle
        if not fast:
            cap = ("Then the cup, its plug riding in the mouth, goes to the vacuum press, a Specac Atlas Autotouch 15T. "
                   "The arm stands it on the ejector pin of the lab's evacuable die, out on its shuttle, and the pin "
                   "lowers it into F1, #222's steel sleeve.")
            L.note(0, "Arm", f"cup {i + 1}: rack to press")
        sc.step(st, cap, 1.2 * f, both(rb.joint_to(Tw=lvl(c_r - d1 * 150 + (0, 0, 30), d1)), rb.grip_to(OPEN_CUP)), hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r, d1)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(c_r + (0, 0, 30), d1)), hold=0.0)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r - d1 * 150 + (0, 0, 30), d1)), hold=0.05)
        q_up = vp.cup_seat() + (0, 0, CUP_GRASP)
        dq = aim(q_up, [(170, 50), (0, 50), (0, 1), (170, 0)], radial(q_up))
        cam_press = cam_near(vp.die_top(), (-430.0, -760.0, 420.0), (60.0, 0.0, 40.0))
        sc.step(st, cap, 1.5 * f, rb.joint_to(Tw=lvl(q_up - dq * 170 + (0, 0, 50), dq)), hold=0.05,
                cam_to=None if fast else cam_press,
                labels=[] if fast else [("vacuum press: Specac Atlas Autotouch 15T", vp.die_top() + (120, 150, 260),
                                         (0.62, 0.20)),
                                        ("our evacuable die round F1, on its shuttle", vp.die_top() + (0, 0, 10),
                                         (0.16, 0.56)),
                                        ("vacuum pump, valves, gauge", vp.world("vpress", (-420, -20, 240)),
                                         (0.12, 0.34))])
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(q_up + (0, 0, 50), dq)), hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q_up + (0, 0, 1), dq)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
        rb.release("vp_pin")
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q_up - dq * 170, dq)), hold=0.05, labels=[])
        sc.step(st, cap, 0.9 * f, vp.to(e=0.0), hold=0.05)
        L.note(3, "Press", "cup in F1, plug 8.0 mm proud")
        # the punch, from its rest, into the die on the plug, held level by its flange: its O-ring seals the bore
        if not fast:
            cap = ("Then the die's punch, from its rest beside the press, held level by its flange. It goes down into "
                   "the die's bore and stands on the plug; its O-ring seals the bore, and the channel across the plug's "
                   "top (DAL #156) keeps the vent open under it.")
            L.note(0, "Arm", "punch: rest to die")
        gp = vp.punch_grasp_rest()
        gd = vp.punch_grasp_die()
        dp = aim(gp, [(150, 0), (0, 0), (0, AP.REST_POCKET + 20)], radial(gp))
        dd = aim(gd, [(0, 32), (0, 2), (0, 0), (160, 0)], radial(gd))
        sc.step(st, cap, 1.3 * f, both(rb.joint_to(Tw=lvl(gp - dp * 150, dp)), rb.grip_to(AP.OPEN_FLANGE)), hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gp, dp)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(AP.GRIP_FLANGE), hold=0.05)
        rb.grasp("vp_punch")
        vp.punch_at = "held"
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(gp + (0, 0, AP.REST_POCKET + 20), dp)), hold=0.05)
        sc.step(st, cap, 1.1 * f, rb.joint_to(Tw=lvl(gd + (0, 0, 32), dd)), hold=0.05)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(gd + (0, 0, 2), dd)), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(gd, dd)), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.grip_to(AP.OPEN_FLANGE), hold=0.05)
        rb.release("vp_shuttle")
        vp.punch_into_die()
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gd - dd * 160, dd)), hold=0.05)
        sc.step(st, cap, 1.0 * f, rb.joint_to(A.PARK_RAD), hold=0.05)
        L.note(0, "Arm", "parked")
        # -------------------------------------------------- the press cycle, under vacuum
        if not fast:
            cap = ("The shuttle carries the die in under the leadscrew and the guard comes down: the press won't start "
                   "with it up. V1 opens to the pump, slowly at first through the needle valve so the powder stays put. "
                   "Air leaves the cup through the plug's vent and out of the die's port: under 1 mbar in about 2 min.")
            L.note(3, "Press", "shuttle in, guard down")
        in_c = vp.world("vpress", (VPm.AXX, VPm.AXY, VPm.Z_PISTON + VPm.CUP_BASE + 52.0))
        cam_cut = cam_near(in_c, (110.0, -300.0, 70.0), (0.0, 0.0, 0.0))
        sc.step(st, cap, 1.2 * f, vp.to(y=VPm.AXY), hold=0.05, cam_to=None if fast else cam_near(
            in_c, (420.0, -880.0, 380.0), (0.0, 40.0, 40.0)))
        sc.step(st, cap, 1.0 * f, vp.to(guard=0.0), hold=0.05)
        if not fast:
            K.cut(i, True, sleeve=True)
        plug_local = sc.gmat[f"plug{i}"].copy()
        plug_z0 = float(plug_local[2, 3])

        def pump(u, i=i):
            vp.st["mbar"] = 1013.0 * (0.8 / 1013.0) ** u
            vp.apply()
            on = 0.02 < u < 0.9 and not fast
            sc.alpha["vpress/air"] = 1.0 if on else 0.0
            if on:
                vp.air(f"cup{i}", u * 3.0, plug_z0)
            L.note(3, "Press", vp.gauge())
        sc.step(st, cap, 3.0 * f, pump, hold=0.2 if not fast else 0.05, cam_to=None if fast else cam_cut, live=False)
        sc.alpha["vpress/air"] = 0.0
        if not fast:
            cap = (f"Start: program 1 pumps up to {AP.SET_T:.1f} t ({AP.SET_T * 9.80665:.1f} kN). The ram lifts the die "
                   f"2 mm to the leadscrew, then drives the plug {VPm.TRAVEL:.1f} mm to flush: the powder goes from "
                   f"{100 * pr['rel_density_set']:.0f} to {100 * pr['rel_density_flush']:.0f} % dense, with no air in it "
                   f"(DAL #140). It holds a minute, topping the load up as the powder settles; F1 takes what's left "
                   f"once the plug is flush.")
        h_set = pr["column_mm_set"]

        def press(u, i=i):
            r = (VPm.GAP + VPm.TRAVEL) * u
            x = max(0.0, r - VPm.GAP)
            vp.st["ram"], vp.st["x"] = r, x
            vp.st["load"] = AP.SET_T * (0.0 if r <= VPm.GAP else min(1.0, 0.25 * (x / VPm.TRAVEL) + 0.75 *
                                                                     (x / VPm.TRAVEL) ** 3))
            sc.gmat[f"plug{i}"] = T((0, 0, -x)) @ plug_local
            K.squeeze[i] = (h_set - x) / h_set
            K.apply()
            L.note(3, "Press", vp.gauge())
        sc.step(st, cap, 3.0 * f, press, hold=0.05)
        L.note(3, "Press", vp.gauge() + ", holding")
        sc.step(st, cap, 0.8 * f, None, hold=0.6 if not fast else 0.05)
        if not fast:
            cap = ("Slow release; V2 lets dry argon into the die, so the cup sees no air until it is out; the guard goes "
                   "up and the shuttle brings the die out. The plug is flush with the rim.")
        sc.step(st, cap, 1.0 * f, vp.to(load=0.0, ram=0.0), hold=0.05)
        sc.step(st, cap, 1.2 * f, vp.to(mbar=1013.0), hold=0.05)
        L.note(3, "Press", vp.gauge() + ", vented with Ar")
        K.cut(i, False, sleeve=True)
        sc.step(st, cap, 1.0 * f, vp.to(guard=1.0), hold=0.05, cam_to=None if fast else cam_press)
        sc.step(st, cap, 1.2 * f, vp.to(y=VPm.Y_OUT), hold=0.05)
        L.note(3, "Press", "shuttle out, plug flush")
        # the punch back to its rest; the pin pushes the cup up out of F1
        if not fast:
            cap = ("The arm lifts the punch off, now the die is vented (under vacuum it would be held down with about "
                   "80 N), and puts it back on its rest. The pin pushes the cup up out of F1.")
            L.note(0, "Arm", "punch: die to rest")
        gd2 = vp.punch_grasp_die() - (0, 0, VPm.TRAVEL)
        sc.step(st, cap, 1.2 * f, both(rb.joint_to(Tw=lvl(gd2 - dd * 160, dd)), rb.grip_to(AP.OPEN_FLANGE)),
                hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gd2, dd)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(AP.GRIP_FLANGE), hold=0.05)
        rb.grasp("vp_punch")
        vp.punch_at = "held"
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gd2 + (0, 0, 40), dd)), hold=0.05)
        sc.step(st, cap, 1.1 * f, rb.joint_to(Tw=lvl(gp + (0, 0, AP.REST_POCKET + 20), dp)), hold=0.05)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gp + (0, 0, 1), dp)), hold=0.05)
        sc.step(st, cap, 0.3 * f, rb.grip_to(AP.OPEN_FLANGE), hold=0.05)
        rb.release("vpress")
        vp.punch_rest()
        vp.st["x"] = 0.0
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(gp - dp * 150, dp)), hold=0.05)
        sc.step(st, cap, 0.8 * f, vp.to(e=VPm.VP["eject"]), hold=0.05)
        L.note(3, "Press", "cup ejected, shuttle out")
        made.append(f"{CUP_NAME[metal]} + {pw} + {top_name}")
        charge_line()

        # -------------------------------------------------- away
        st = f"{4 if i == 0 else 6}/{n}"
        q = K.nest_seat() + (0, 0, CUP_GRASP)
        dest_al = metal == "Al"
        if not fast:
            cap = (f"The charged cup, {pr['charged_cup_g']:.1f} g, its plug flush on {pr['alloying_g'] + pr['top_up_g']:.1f} "
                   f"g of powder pressed to {100 * pr['rel_density_flush']:.0f} % under vacuum, goes onto the carrier on "
                   f"the MiR250's cabinet, beside the arm, for the atomizer.")
            L.note(0, "Arm", f"cup {i + 1}: press to the MiR's carrier")
        sc.step(st, cap, 1.2 * f, both(rb.joint_to(Tw=lvl(q - dq * 170, dq)), rb.grip_to(OPEN_CUP)), hold=0.05,
                cam_to=None if fast else cam_near(K.nest_seat(0.0), (-520.0, -760.0, 470.0), (60.0, 0.0, 60.0)))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q, dq)), hold=0.05)
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=0.05)
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(q + (0, 0, 40), dq)), hold=0.0)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q - dq * 170 + (0, 0, 40), dq)), hold=0.05)
        if dest_al:
            k = [0, 1][i]
            c = K.carrier_seat(k) + (0, 0, CUP_GRASP)
            d = aim(c, [(170, 40), (0, 40), (0, 1), (170, 0)], (0.0, -1.0))
            sc.step(st, cap, 1.6 * f, rb.joint_to(Tw=lvl(c - d * 170 + (0, 0, 40), d)), hold=0.05,
                    cam_to=None if fast else CAM_AMR)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 40), d)), hold=0.05)
            sc.step(st, cap, 0.6 * f, rb.line_to(lvl(c + (0, 0, 1), d)), hold=0.05)
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
            rb.release("amr")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c - d * 170, d)), hold=0.05)
        else:
            c = K.rack_cup(i) + (0, 0, CUP_GRASP)
            sc.step(st, cap, 1.4 * f, rb.joint_to(Tw=lvl(c - d1 * 150 + (0, 0, 30), d1)), hold=0.05)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 30), d1)), hold=0.05)
            sc.step(st, cap, 0.5 * f, rb.line_to(lvl(c + (0, 0, 1), d1)), hold=0.05)
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=0.05)
            rb.release("crack")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c - d1 * 150, d1)), hold=0.05)
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=0.1)
        L.note(0, "Arm", "parked")

    cycle(0, fast=False)
    # ------------------------------------------------------------------ 5-6. the other three, faster
    pa, pc = PRUN["Al"], PRUN["Cu"]
    cap = (f"The same for the second Al cup ({pa['alloying_g']:.2f} g Si + {pa['top_up_g']:.2f} g AlSi10Mg), then the two "
           f"Cu cups ({pc['alloying_g']:.2f} g Ni + {pc['top_up_g']:.2f} g Cu each), shown faster, each pressed at "
           f"{AP.SET_T:.1f} t under vacuum. A charged Cu cup is {pc['charged_cup_g']:.0f} g: over the doser's 100 g load "
           f"cell (TAL221), so Cu cups need a bigger one. The Cu cups go back on the rack for their own run.")
    sc.step(f"5/{n}", cap, 0.6, None, hold=1.6, cam_to=CAM_WORK)
    globals()["_CAP6"] = cap
    for i in (1, 2, 3):
        _cycle_fast(cycle, sc, i, cap)
    # ------------------------------------------------------------------ 7. tray B up; ready for the atomizer
    cap = (f"Made up: two Al-10Si cups, {2 * pa['charged_cup_g']:.1f} g together, on the MiR250 for the rePowder, and "
           f"two 90/10 Cu-Ni cups on the rack, {2 * pc['charged_cup_g']:.1f} g, for their own run (designed "
           f"compositions, if every gram dissolves; out/alloy_recipe_pressed.json). Tray B goes back into storage.")
    L.store("B", f"7/{n}", cap, cam=CAM_AMR)
    L.note(0, "Arm", "parked; next: the atomizer")
    sc.step(f"7/{n}", cap, 1.6, None, hold=2.4, still=True,
            cam_to=cam_near(K.carrier_seat(0) + (17, 0, 0), (-560.0, -620.0, 330.0), (0.0, 0.0, 25.0)),
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

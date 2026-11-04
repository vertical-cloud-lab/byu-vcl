"""The alloy workflow, start to finish (#303), chapter 1: the atomizer charge, made up on tray B of the VLM.

    xvfb-run -a python3 alloy_charge.py            # -> out/alloy_charge.gif, out/mp4/alloy_charge.mp4, .json, stills
    PREVIEW=1 xvfb-run -a python3 alloy_charge.py  # the last frame of each sub-step -> /tmp/preview_alloy_charge.png
    ARM_AUDIT=1 xvfb-run -a python3 alloy_charge.py   # no render: every frame collision-checked -> out/collisions/

This replaces round 2's vial (``animate.workflow``: a 20 mL vial dosed, then liquid added in the CubXL). The rePowder
melts what it is given as **charge cups**: the lab's own (#222, ``charge.py``), turned from high-purity bar, each
filled with powder by the multi-doser and closed with a vented plug pressed home into its bore. Four go into the
crucible a run (byu-vcl PR #318), so the rack on tray B holds eight: four 5N Al cups for this run's Al-10Si and four
oxygen-free Cu cups for a 90/10 Cu-Ni run (DAL #162, #219), each with a plug of its own metal.

The two versions of this chapter written for PR #318's review are merged here:

* **Dosing and weighing** (was ``alloy_charge_doser.py``). The doser's 100 g load cell and its shared catch funnel come
  out. The cup is dosed in a plain cradle at the doser's station, through a funnel that only ever carries one powder
  (four on a stand: Si, AlSi10Mg, Ni, Cu), and weighed on an A&D HR-202i (220 g x 0.1 mg) beside the doser. The
  balance stands on a granite block, so the arm reaches its side door over the cup rack.
* **The plug pressed home under vacuum** (was this file's vacuum-press rewrite; ``alloy_press.py``). The bore is filled
  to where the plug is set: the alloying powder (Si, Ni), then a top-up of the cup's own metal (AlSi10Mg, Cu). The plug
  goes into the cup's mouth at the rack, and a Specac Atlas Autotouch 15T with the lab's evacuable die round #222's F1
  sleeve pumps the die down and drives the plug to flush on a set load (DAL #140).

So each cup is dosed twice, one powder at a time, so that a funnel is swapped only when the powder changes: all four
cups of a run get their alloying powder and are weighed, then the top-up funnel takes the fork and each cup is topped
up to the plug line, weighed again, plugged, pressed, and put on the MiR250's carrier (Al, for the atomizer, chapter 2,
``alloy_atomize.py``) or back in the rack (Cu, for its own run). Tray B goes back into storage.

Every arm move is a straight line of the grasp point or a joint move between two solved poses (``robot.py``), as in
``animate.workflow``; joint moves are collision-checked and planned round obstacles (``collide.py``). The cups and
funnels are always held level (fingers closing sideways), so a cup never tilts in the gripper; the plugs are taken
from above. Close-ups cut the cup, powder, funnel, plug and die in half (``charge.lathe``).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import numpy as np
import pyvista as pv

import scene
scene.GIF_FPS = 4                      # a ~4-minute GIF under 4.9 MB (the MP4 keeps every frame, 15 fps); at
scene.GIF_SIZE = (512, 288)            # 560 x 315 the last render's came out at 5.3 MB
from scene import Scene, T, R, S, OUT  # noqa: E402

import animate as A                    # noqa: E402
import carousel as CR                  # noqa: E402
import alloy_press as AP               # noqa: E402
import charge as C                     # noqa: E402
import vacuum_press as VPm             # noqa: E402
import lab                             # noqa: E402
import props as P                      # noqa: E402
import vlm as V                        # noqa: E402
from robot import both                 # noqa: E402

sys.path.insert(0, str(lab.HERE / "lab_models"))
import labware as LW                   # noqa: E402

NAME = "alloy_charge"
TITLE = "Vertical cloud lab, the alloy route 1/4: the atomizer charge"
# the punch's rest, 40 mm further left than alloy_press puts it (still in front of the control tower): with eight cups
# the rack's first plug stands beside the rest, and taking it from above put the gripper's knuckles in the rest's post
AP.REST_LOCAL = (110.0, AP.REST_LOCAL[1])
# tray B frame. Left to right: the vacuum press (alloy_press.PRESS_AT), the cup rack in front, the HR-202i on its block
# behind the rack, the multi-doser, and the funnel stand right of the doser
RACK_AT = (-250.0, -372.0)             # where round 2's vial rack stood (animate.LOADS)
BAL_AT = (-102.0, -110.0)              # the HR-202i's body centre, turned so its left side door faces the arm
BLOCK_H = 120.0                        # the granite block under it: the door's sill clears the rack's cups
FSTAND_AT = (960.0, -372.0)
SLOTS = [("Al", "Si")] * 4 + [("Cu", "Ni")] * 4     # rack seat -> (cup metal, alloying powder)
FUNNELS = ("Si", "AlSi10Mg", "Ni", "Cu")            # stand seat -> powder: one funnel per powder
FUNNEL_COL = {"Si": C.FUNNEL_LABEL["Si"], "AlSi10Mg": C.FUNNEL_LABEL["Al"], "Ni": C.FUNNEL_LABEL["Ni"],
              "Cu": C.FUNNEL_LABEL["Cu"]}
FUNNEL_WORD = {"Si": "yellow", "AlSi10Mg": "blue", "Ni": "green", "Cu": "orange"}
MODULE = {"Si": 5, "Ni": 2, "AlSi10Mg": AP.TOPUP_MODULE["Al"], "Cu": AP.TOPUP_MODULE["Cu"]}   # carousel modules
#                                        (0-based): the two alloying powders and the two top-ups
CUP_GRASP = 45.0                       # grasp point above a cup's base (its top 18.5 mm higher)
PLUG_GRASP = 21.5                      # above a plug's base: the pads' lower ends 2 mm over the cup's rim
GRIP_CUP = 0.80                        # 2F-85 closure on the 19.05 mm cup: gap = 28 - 90 (c - 0.70) (ur_arm.gripper_fk)
GRIP_PLUG = 0.87                       # on the 12.7 mm plug
OPEN_CUP = 0.66                        # 31.6 mm between the pads: clear of a neighbouring cup in a pocket row
OPEN_RACK = 0.75                       # 23.5 mm, 2.2 mm a side, at the rack: its cups stand 40 mm apart, and the cups
#                                        nearest the arm's base are reached at an angle, past their neighbours
OPEN_PLUG = 0.60
GRIP_FUNNEL = 0.70 + (28.0 - C.FUNNEL["band_d"]) / 90.0      # on the funnel's 42 mm band
OPEN_FUNNEL = 0.70 + (28.0 - C.FUNNEL["band_d"] - 12.0) / 90.0
CARRIER_LOCAL = A.BUFFER_LOCAL         # the MiR's cup carrier stands where round 2's one-vial holder stood
METAL_C = {"Al": C.AL_5N, "Cu": C.CU}
CUP_NAME = {"Al": "5N Al", "Cu": "OFE Cu"}
BAL_HOLDER = 2.0                       # the cup holder's floor on the pan
DOOR_OPEN = 150.0                      # the side door's travel: it slides back along the chamber, clear of its opening
TOL = 0.01                             # dose tolerance, fraction of the dose (assumed)
STATION_GONE = {"load_cell", "vial_cup", "vial_funnel", "ext_vial_post", "level_wedge"}
ERR = [0.0006, -0.0013, 0.0009, -0.0004, 0.0011, -0.0008, 0.0003, -0.0010]   # each cup's dose off its target (made
#                                        up, inside TOL: the readings shown)
F_DETAIL = {"Al": 0.55, "Cu": 0.36}    # the first cup of each run, shown in full
F_FAST = 0.10                          # the other three of each run: a time-lapse, no holds, its short moves cut
FAST_CUT = 0.10                        # (s): in the time-lapse, a sub-step shorter than this is done between frames

CAM_WORK = [(-1500, -4300, 2500), (-60, -1450, 1020), (0, 0, 1)]
CAM_RACK = [(-1150, -2650, 1800), (-330, -1360, 960), (0, 0, 1)]
CAM_AMR = [(1300, -4100, 1900), (-250, -1900, 1000), (0, 0, 1)]
CAM_RIGHT = [(1900, -3900, 2200), (520, -1420, 1000), (0, 0, 1)]

RECIPE = C.recipe()
STILLS = {}                            # name -> frame, cut from the MP4 after the render (out/alloy_charge_<name>.png)


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
    """The charge rack, the vacuum press (``alloy_press.VacPress``), the cups and plugs, the funnels and their stand,
    the doser's rebuilt station, the HR-202i on its block and the MiR's carrier, added to round 2's scene (``A.Lab``);
    the vial, its rack and the one-vial holder are hidden. Each cup's bore holds two powder layers (the alloying
    powder, then the top-up of the cup's own metal), squeezed together when pressed."""

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
        # the vacuum press, its die and the punch's rest
        self.vp = AP.VacPress(sc, "tray_B", AP.PRESS_AT, V.T_FLOOR)
        # the doser's cup station, rebuilt: post, cradle, funnel fork (rig frame)
        fit, self.st_seat = C.station_fittings()
        for k, (m, col) in fit.items():
            sc.add(f"station/{k}", m, col, rig, specular=0.3)
        # the HR-202i on its granite block, its left side door (facing the arm) on its own group
        hp = LW.HR202I
        blk = C._box(-hp["D_all"] / 2 - 10, hp["D_all"] / 2 + 10, -hp["W_doors"] / 2 - 10, hp["W_doors"] / 2 + 10, 0.0,
                     BLOCK_H)
        sc.add("balblock/body", blk, (0.30, 0.31, 0.33), "balblock", specular=0.35)
        sc.parent["balblock"] = "tray_B"
        sc.gmat["balblock"] = T((*BAL_AT, V.T_FLOOR))
        bal = LW.hr202i_parts(0.0)
        for j, (mat, m, col, a, spec) in enumerate(_model_meshes(bal["body"] + bal["door_right"] + bal["top_door"])):
            sc.add(f"bal/{mat}{j}", m, col, "bal", opacity=a, specular=spec)
        for j, (mat, m, col, a, spec) in enumerate(_model_meshes(bal["door_left"])):
            sc.add(f"bal_door/{mat}{j}", m, col, "bal_door", opacity=a, specular=spec)
        sc.parent["bal"] = "tray_B"
        sc.gmat["bal"] = T((*BAL_AT, V.T_FLOOR + BLOCK_H)) @ R((0, 0, 1), 90)
        sc.parent["bal_door"] = "bal"
        self.door = 0.0
        self.pan_xyz = np.array([0.0, -hp["D"] / 2 + hp["pan_y"], hp["pan_top"]])
        holder = C.lathe([(0, 0), (20, 0), (20, BAL_HOLDER), (0, BAL_HOLDER)], res=48)
        cwall = C.lathe([(C.STOCK_D / 2 + 0.6, BAL_HOLDER), (C.STOCK_D / 2 + 3.6, BAL_HOLDER),
                         (C.STOCK_D / 2 + 3.6, BAL_HOLDER + 6.0), (C.STOCK_D / 2 + 0.6, BAL_HOLDER + 6.0)], cut=True)
        cwall = cwall.rotate_z(-90.0, inplace=False)        # the C opens to the door (balance -x)
        sc.add("bal/holder", holder.merge(cwall).translate(self.pan_xyz, inplace=False), C.PRINT, "bal")
        # the funnels on their stand, one per powder
        stand, self.fseats = C.funnel_stand(len(FUNNELS))
        sc.add("fstand/body", stand, P.RACK_C, "fstand")
        sc.parent["fstand"] = "tray_B"
        sc.gmat["fstand"] = T((*FSTAND_AT, V.T_FLOOR))
        fm, fcut = C.funnel(), C.funnel(cut=True)
        for j, pw in enumerate(FUNNELS):
            g = f"funnel_{pw}"
            sc.add(f"{g}/body", fm["body"], (0.95, 0.95, 0.93), g, specular=0.2)
            sc.add(f"{g}/cut", fcut["body"], (0.95, 0.95, 0.93), g, specular=0.2, shown=False)
            sc.add(f"{g}/label", fm["label"], FUNNEL_COL[pw], g, specular=0.2)
            sc.parent[g] = "fstand"
            sc.gmat[g] = T(self.fseats[j])
        # the MiR's carrier
        mesh, self.carrier_seats = C.carrier()
        sc.add("amr/carrier", mesh.translate((*CARRIER_LOCAL, P.AMR_TOP - 20), inplace=False), P.RACK_C, "amr")
        self.carrier_base = np.array([*CARRIER_LOCAL, P.AMR_TOP - 20])
        # cups and plugs, in the rack
        unit, point = C.unit_powder(cut=True), C.drill_point_fill(cut=True)
        self.powder_h = [0.0] * len(SLOTS)        # top of the alloying layer, above the bore floor (mm)
        self.powder_h2 = [0.0] * len(SLOTS)       # top of the top-up layer
        self.squeeze = [1.0] * len(SLOTS)         # pressing scales both layers by this
        self._point = [False] * len(SLOTS)
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
        sc.gmat["bal_door"] = T((0, self.door, 0))
        for i in range(len(SLOTS)):
            k = self.squeeze[i]
            h1, h2 = self.powder_h[i] * k, self.powder_h2[i] * k
            sc.gmat[f"cup{i}_pw"] = T((0, 0, C.FLOOR_Z + 0.05)) @ S((1, 1, max(h1, 0.01)))
            sc.gmat[f"cup{i}_pw2"] = T((0, 0, C.FLOOR_Z + 0.05 + h1)) @ S((1, 1, max(h2 - h1, 0.01)))
        self.vp.apply()

    def cut(self, i, on: bool, sleeve=False, funnel=None):
        """Swap cup i (and its plug, the die and a funnel) for the half-section versions."""
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
        if funnel is not None:
            sc.alpha[f"funnel_{funnel}/body"] = 0.0 if on else 1.0
            sc.alpha[f"funnel_{funnel}/cut"] = 1.0 if on else 0.0

    def to(self, **kw):
        """An update(u) easing the balance's door to the given value."""
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

    def nest_seat(self, eject=None):
        """Base centre of a cup on the press's raised ejector pin, shuttle out (world)."""
        return self.vp.cup_seat_at(VPm.VP["eject"] if eject is None else eject)

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
    bottom = K.st_seat["cup"][2] + C.FLOOR_Z + max(K.powder_h[i], K.powder_h2[i]) + 1.0
    m = 14
    s2 = (np.arange(m) / m + t * 2.3) % 1.0
    s2 = s2[s2 < on]
    b = np.c_[ax + 0 * s2, ay + np.sin(np.arange(len(s2)) * 1.7) * 0.8, tip - (tip - bottom) * s2 ** 2]
    return np.r_[a, b]


def movie():
    data = lab.meshes()
    CR.SKIP = CR.SKIP | STATION_GONE           # the rig's load cell, vial cup, vial post and catch funnel come out
    sc = Scene(NAME, TITLE)
    if os.environ.get("CHARGE_FXAA"):          # FXAA in place of SSAA: about a quarter of the pixel work, for a render
        sc.pl.disable_anti_aliasing()           # on a loaded machine (scene.py's default is SSAA)
        sc.pl.enable_anti_aliasing("fxaa")
    sc.cam = list(A.CAM_WIDE)
    L = A.Lab(sc, data, robot=True, highlight=MODULE["Si"])
    K = Charge(sc, L)
    rb, car = L.robot, L.carousel
    sc.parent["stream"] = K.rig
    auditor = None
    if os.environ.get("ARM_AUDIT_PARTIAL") and sc.auditor is not None:     # the audit so far, every 300 frames
        mark = [0]

        def partial(sc):
            if sc.n >= mark[0] + 300:
                mark[0] = sc.n
                rep = sc.auditor.report()
                rep["label"] = sc.label
                with open(os.environ["ARM_AUDIT_PARTIAL"], "w") as fh:
                    json.dump(rep, fh, indent=1)
                print(f"audit so far: {rep['frames_with_collisions']} of {rep['frames_checked']} frames, "
                      f"at {sc.label}", flush=True)
        sc.frame_hooks.append(partial)
    if not os.environ.get("ARM_AUDIT"):
        import time
        t_start = time.time()
        if os.environ.get("ARM_AUDIT_RENDER"):          # render and check every frame in the same pass
            import collide
            auditor = collide.Auditor(sc)
            sc.frame_hooks.append(auditor)

        last = [0]

        def progress(sc):
            if sc.n >= last[0] + 300:
                last[0] = sc.n
                print(f"frame {sc.n}, {time.time() - t_start:.0f} s", flush=True)
        sc.frame_hooks.append(progress)
    PRES = AP.write_recipe()
    PRUN = {"Al": PRES["runs"]["Al-10Si"], "Cu": PRES["runs"]["Cu-10Ni"]}
    run = RECIPE["runs"]
    cup_g = {"Al": run["Al-10Si"]["cups"][0]["cup_g"], "Cu": run["Cu-10Ni"]["cups"][0]["cup_g"]}
    L.extra_gauges = [("Arm", f"{A.ROBOT_NAME}, parked"), ("Doser", "module 1 at the station, no funnel"),
                      ("HR-202i", "0.0000 g  (220 g x 0.1 mg)"), ("Press", "shuttle out, guard up"),
                      ("Charge", "0 of 4 Al-10Si, 0 of 4 Cu-10Ni cups made up")]
    L.apply_state()
    n = 10
    made = {"Al": 0, "Cu": 0}
    read = {}                                  # cup -> (after the alloying powder, after the top-up), g
    base_xy = sc.world(rb.root)[:2, 3].copy()           # the arm's base; the MiR stays parked for the chapter

    def charge_line():
        L.note(4, "Charge", f"{made['Al']} of 4 Al-10Si, {made['Cu']} of 4 Cu-10Ni cups made up")

    def aim(p, offs, prefer, step=15, close=None, only=None, fallback=True):
        """The horizontal direction to aim a level gripper at p: the clear one nearest `prefer`. offs lists the poses
        the moves use, as (distance back along the direction, height up) from p; each must have an IK solution clear of
        everything (collide.py), and the arm's own links, with what it holds. Square to the tray, a target near the
        arm's base or off to one side folds the arm into itself; the cups and the punch are round, so any horizontal
        approach grips them. An entry of offs may carry a third number, the gripper's closure there; `close` is the
        default (the closure as it is now if None). `only`: the groups the gripper may touch at the contact pose
        (default: whatever it touches there), so that an open fingertip brushing the next cup in a rack rules a
        direction out; if no direction passes with it, any contact there is allowed, as before."""
        import collide
        chk = rb.checker()
        W = chk.snapshot()
        c = rb.close if close is None else close
        a0 = math.atan2(prefer[0], prefer[1])
        angs = sorted(range(-180, 180, step),
                      key=lambda g: abs((math.radians(g) - a0 + math.pi) % (2 * math.pi) - math.pi))
        inv = np.linalg.inv(sc.world(rb.root))
        for g in angs:
            a = math.radians(g)
            d = np.array([math.sin(a), math.cos(a), 0.0])
            ok = True
            for o in offs:
                back, up = o[:2]
                cc = o[2] if len(o) > 2 else c
                Tb = inv @ lvl(np.asarray(p, float) - d * back + (0, 0, up), d)
                contact = back < 1 and up < 3
                good = False
                for q in collide.ik_all(rb.model, Tb, rb.q):
                    allow = chk.touching(q, cc, W) if contact else set()
                    if only is not None:
                        allow &= set(only)
                    if not chk.collisions(q, cc, W, allow, first=True):
                        good = True
                        break
                if not good:
                    ok = False
                    break
            if ok:
                return d
        if not fallback:
            return None
        if only is not None:
            print(f"note: {sc.label}: no level approach at {np.round(p).tolist()} touching only {sorted(only)}; "
                  f"any contact allowed", flush=True)
            return aim(p, offs, prefer, step, close, None)
        print(f"warning: no clear level approach at {np.round(p).tolist()}", flush=True)
        return np.array([prefer[0], prefer[1], 0.0], float)

    def radial(p, ref=(0.0, 1.0), lim=35.0):
        """A level gripper aimed along the line from the arm's base to p, within `lim` degrees of `ref`."""
        v = np.asarray(p[:2], float) - base_xy
        a, a0 = math.atan2(v[0], v[1]), math.atan2(ref[0], ref[1])
        da = (a - a0 + math.pi) % (2 * math.pi) - math.pi
        da = max(-math.radians(lim), min(math.radians(lim), da))
        return np.array([math.sin(a0 + da), math.cos(a0 + da), 0.0])

    def pre(T_pre, T_at, close=None):
        """A joint move to T_pre in an IK branch from which the straight line on to T_at is clear and doesn't flip
        (collide.py), the nearest such; else the planner's own choice of branch. The planner picks a clear branch for
        the pose itself, but the line that follows may cross a wrist flip in it, or sweep the forearm into the rack."""
        import collide
        import ur_arm
        from scipy.spatial.transform import Rotation, Slerp
        c = rb.close if close is None else close
        chk = rb.checker()
        W = chk.snapshot()
        inv = np.linalg.inv(sc.world(rb.root))
        sl = Slerp([0.0, 1.0], Rotation.from_matrix(np.stack([T_pre[:3, :3], T_at[:3, :3]])))
        for q0 in collide.ik_all(rb.model, inv @ T_pre, rb.q):
            if chk.collisions(q0, c, W, set(), first=True):
                continue
            q, path, ok = q0, [q0], True
            for s_ in np.linspace(0.0, 1.0, 21)[1:]:
                M = np.eye(4)
                M[:3, :3] = sl([s_]).as_matrix()[0]
                M[:3, 3] = T_pre[:3, 3] + (T_at[:3, 3] - T_pre[:3, 3]) * s_
                qn = ur_arm.ik(rb.model, inv @ M, q)
                if np.abs(qn - q).max() > np.radians(25):
                    ok = False
                    break
                q = qn
                path.append(q)
            if not ok:
                continue
            allow = chk.touching(path[-1], c, W)
            if any(chk.collisions(x, c, W, allow, first=True) for x in path[1:]):
                continue
            return rb.joint_to(q1=q0)
        print(f"note: {sc.label}: no IK branch with a clear line on from {np.round(T_pre[:3, 3]).tolist()}",
              flush=True)
        return rb.joint_to(Tw=T_pre)

    rack_dir, rack_bk = {}, {}

    def rack_aim(i):
        """The level direction to rack cup i, and how far back the approach starts (rack_bk[i]): the open fingertips
        (OPEN_RACK) may touch cup i and its rack, not the cups beside it. The cups nearest the arm's base can't be
        reached square from 150 mm back, so a shorter approach is tried before an angled one is ruled out."""
        if i not in rack_dir:
            p0 = K.rack_cup(i) + (0, 0, CUP_GRASP)
            only = {f"cup{i}", f"plug{i}", "crack"}
            for bk in (150, 110, 80):
                d = aim(p0, [(bk, 30, OPEN_RACK), (0, 0, OPEN_RACK), (0, 30, GRIP_CUP), (bk, 0, OPEN_RACK)],
                        radial(p0), step=5, only=only, fallback=False)
                if d is not None:
                    break
            else:
                bk = 150
                d = aim(p0, [(bk, 30, OPEN_RACK), (0, 0, OPEN_RACK), (0, 30, GRIP_CUP)], radial(p0), step=5)
            rack_dir[i], rack_bk[i] = d, bk
        return rack_dir[i]

    # ------------------------------------------------------------------ 1. tray B down
    cap = ("The alloy route, start to finish. First the charge: the atomizer melts cups, the lab's own (#222), turned "
           "from high-purity bar, filled with powder and closed with a vented plug pressed home. Four go into the "
           "crucible a run: tray B holds four 5N Al cups for this run's Al-10Si and four oxygen-free Cu cups for a "
           "90/10 Cu-Ni run.")
    sc.step(f"1/{n}", cap, 1.0, None, hold=0.6,
            labels=[("tray B: powder dosing and the charge", (V.TRAY_W / 2 - 300, *V.SLOTS["R3"]), (0.84, 0.34))])
    L.fetch("B", f"1/{n}", cap, cam=CAM_WORK)
    sc.step(f"1/{n}", cap, 1.6, None, hold=2.2, cam_to=CAM_WORK,
            labels=[("charge rack: 4 x 5N Al and 4 x OFE Cu cups, a plug for each", K.rack_cup(1) + (0, 0, 70),
                     (0.16, 0.18)),
                    ("vacuum press, on tray B since set-up: Specac Atlas Autotouch 15T, our die round F1",
                     K.vp.die_top() + (0, 0, 300), (0.10, 0.36)),
                    ("A&D HR-202i balance, 220 g x 0.1 mg", K.bal_cup() + (0, 0, 250), (0.40, 0.12)),
                    ("multi-doser (powder-doser #185), its station rebuilt for cups", tray_xyz(L, (250, -250, 560)),
                     (0.66, 0.12)),
                    ("one funnel per powder", K.stand_funnel(1) + (30, 0, 50), (0.86, 0.30))])
    cap = ("No load cell and no shared funnel. The doser doses into a plain cradle, through a funnel that only ever "
           "carries one powder: Si (yellow), AlSi10Mg (blue), Ni (green), Cu (orange). An A&D HR-202i, 220 g to 0.1 mg, "
           "weighs every cup, on a granite block so the arm reaches its door over the rack.")
    sc.step(f"1/{n}", cap, 1.4, None, hold=3.0, cam_to=cam_near(K.station_cup(), (420.0, -1500.0, 620.0),
                                                                 (180.0, 60.0, 80.0)))

    # ------------------------------------------------------------------ the funnel moves
    def funnel_to_station(pw, st, f=1.0, cam=None):
        j = FUNNELS.index(pw)
        g = f"funnel_{pw}"
        gr = C.FUNNEL["grasp"]
        H = (lambda x: x) if f > 0.3 else (lambda x: 0.0)
        p0 = K.stand_funnel(j) + (0, 0, gr)
        p1 = K.station_funnel() + (0, 0, gr)
        L.note(0, "Arm", f"{pw} funnel: stand to the doser's fork")
        sc.step(st, None, 1.4 * f, both(pre(lvl(p0 + (0, -170, 30)), lvl(p0 + (0, 0, 4)), OPEN_FUNNEL),
                                        rb.grip_to(OPEN_FUNNEL)), hold=H(0.05), cam_to=cam)
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p0 + (0, 0, 4))), hold=H(0.05))
        sc.step(st, None, 0.3 * f, rb.line_to(lvl(p0)), hold=0.0)
        sc.step(st, None, 0.4 * f, rb.grip_to(GRIP_FUNNEL), hold=H(0.05))
        rb.grasp(g)
        sc.step(st, None, 0.4 * f, rb.line_to(lvl(p0 + (0, 0, 6))), hold=0.0)
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p0 + (0, -170, 6))), hold=H(0.05))
        sc.step(st, None, 1.4 * f, pre(lvl(p1 + (0, -200, 6)), lvl(p1 + (0, 0, 6))), hold=H(0.05))
        sc.step(st, None, 1.0 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=H(0.05))
        sc.step(st, None, 0.4 * f, rb.line_to(lvl(p1)), hold=H(0.05))
        sc.step(st, None, 0.4 * f, rb.grip_to(OPEN_FUNNEL), hold=H(0.05))
        rb.release(K.rig)
        sc.step(st, None, 0.8 * f, rb.line_to(lvl(p1 + (0, -200, 0))), hold=H(0.05))
        L.note(1, "Doser", f"{pw} funnel in the fork")

    def funnel_to_stand(pw, st, f=1.0, cam=None):
        j = FUNNELS.index(pw)
        g = f"funnel_{pw}"
        gr = C.FUNNEL["grasp"]
        H = (lambda x: x) if f > 0.3 else (lambda x: 0.0)
        p0 = K.station_funnel() + (0, 0, gr)
        p1 = K.stand_funnel(j) + (0, 0, gr)
        L.note(0, "Arm", f"{pw} funnel: back to its place on the stand")
        sc.step(st, None, 1.3 * f, both(pre(lvl(p0 + (0, -200, 0)), lvl(p0), OPEN_FUNNEL), rb.grip_to(OPEN_FUNNEL)),
                hold=H(0.05), cam_to=cam)
        sc.step(st, None, 0.8 * f, rb.line_to(lvl(p0)), hold=H(0.05))
        sc.step(st, None, 0.4 * f, rb.grip_to(GRIP_FUNNEL), hold=H(0.05))
        rb.grasp(g)
        sc.step(st, None, 0.4 * f, rb.line_to(lvl(p0 + (0, 0, 6))), hold=0.0)
        sc.step(st, None, 0.9 * f, rb.line_to(lvl(p0 + (0, -200, 6))), hold=H(0.05))
        sc.step(st, None, 1.4 * f, pre(lvl(p1 + (0, -170, 6)), lvl(p1 + (0, 0, 6))), hold=H(0.05))
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p1 + (0, 0, 6))), hold=H(0.05))
        sc.step(st, None, 0.3 * f, rb.line_to(lvl(p1)), hold=H(0.05))
        sc.step(st, None, 0.4 * f, rb.grip_to(OPEN_FUNNEL), hold=H(0.05))
        rb.release("fstand")
        sc.step(st, None, 0.7 * f, rb.line_to(lvl(p1 + (0, -170, 0))), hold=H(0.05))
        L.note(1, "Doser", "no funnel in the fork")

    def park(st, f, H, cam=None, cap=None):
        sc.step(st, cap, 1.1 * f, rb.joint_to(A.PARK_RAD), hold=H(0.05), cam_to=cam)
        L.note(0, "Arm", "parked")

    # ------------------------------------------------------------------ the cup's moves
    def rack_to_cradle(i, st, cap, f, H, detail):
        p0 = K.rack_cup(i) + (0, 0, CUP_GRASP)
        d0 = rack_aim(i)
        bk = rack_bk[i]
        p1 = K.station_cup() + (0, 0, CUP_GRASP)
        sc.step(st, cap, 1.6 * f, both(pre(lvl(p0 - d0 * bk + (0, 0, 30), d0), lvl(p0, d0), OPEN_RACK),
                                       rb.grip_to(OPEN_RACK)), hold=H(0.05), cam_to=CAM_WORK if detail else None)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0, d0)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(p0 + (0, 0, 30), d0)), hold=0.0)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p0 - d0 * bk + (0, 0, 30), d0)), hold=H(0.05))
        sc.step(st, cap, 1.4 * f, pre(lvl(p1 + (0, -200, 2)), lvl(p1 + (0, 0, 2))), hold=H(0.05))
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(p1 + (0, 0, 2))), hold=H(0.05),
                cam_to=cam_near(K.station_cup(), (230.0, -430.0, 170.0), (0.0, 0.0, 70.0)) if detail else None)
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(p1)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
        rb.release(K.rig)
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(p1 + (0, -200, 0))), hold=H(0.05))

    def cradle_to_balance(i, st, cap, f, H, detail):
        p1 = K.station_cup() + (0, 0, CUP_GRASP)
        q = K.bal_cup() + (0, 0, CUP_GRASP)
        sc.step(st, cap, 1.0 * f, pre(lvl(p1 + (0, -200, 0)), lvl(p1)), hold=H(0.05))
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(p1 + (0, 0, 2))), hold=0.0)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(p1 + (0, -200, 2))), hold=H(0.05))
        cam_bal = cam_near(K.bal_cup(), (360.0, -660.0, 330.0), (0.0, 0.0, 55.0))
        door0 = K.door
        K.door = DOOR_OPEN                     # the move is planned with the door open, as it is when the line starts
        K.apply()
        mv = pre(lvl(q + (0, -150, 2)), lvl(q + (0, 0, 2)))
        K.door = door0
        K.apply()
        sc.step(st, cap, 1.4 * f, both(mv, K.to(door=DOOR_OPEN)), hold=H(0.05), cam_to=cam_bal if detail else None)
        sc.step(st, cap, 1.0 * f, rb.line_to(lvl(q + (0, 0, 2))), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(q)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
        rb.release("bal")
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q + (0, -150, 0))), hold=H(0.05))

    def weigh(i, value, what, st, cap, f, H, detail, still=None):
        metal = SLOTS[i][0]
        sc.step(st, cap, 0.6 * f, K.to(door=0.0), hold=H(0.05))

        def settle(u, value=value):
            v = cup_g[metal] + (value - cup_g[metal]) * min(1.0, u * 1.25) + (0.0007 * math.sin(u * 19) * (1 - u))
            L.note(2, "HR-202i", f"{v:.4f} g{'  stable: ' + what if u > 0.85 else ''}")
        if still:
            STILLS[still] = sc.n + int(round(1.4 * f * scene.FPS)) + int(round(0.6 * scene.FPS))
        sc.step(st, cap, 1.4 * f, settle, hold=1.2 if detail else 0.0)
        sc.step(st, cap, 0.6 * f, K.to(door=DOOR_OPEN), hold=H(0.05))

    def balance_to_rack(i, st, cap, f, H, detail):
        q = K.bal_cup() + (0, 0, CUP_GRASP)
        d1 = rack_aim(i)
        bk = rack_bk[i]
        c_r = K.rack_cup(i) + (0, 0, CUP_GRASP)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        L.note(2, "HR-202i", "0.0000 g")
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(q + (0, 0, 2))), hold=0.0)
        sc.step(st, cap, 0.9 * f, rb.line_to(lvl(q + (0, -150, 2))), hold=H(0.05))
        sc.step(st, cap, 0.5 * f, K.to(door=0.0), hold=0.0)
        sc.step(st, cap, 1.3 * f, pre(lvl(c_r - d1 * bk + (0, 0, 30), d1), lvl(c_r + (0, 0, 30), d1)), hold=H(0.05),
                cam_to=CAM_RACK if detail else None)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r + (0, 0, 30), d1)), hold=H(0.05))
        sc.step(st, cap, 0.5 * f, rb.line_to(lvl(c_r + (0, 0, 1), d1)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_RACK), hold=H(0.05))
        rb.release("crack")
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r - d1 * bk, d1)), hold=H(0.05))

    def dose(i, layer, st, cap, f, H, detail, still=None):
        """Index, dock, tilt and dose one layer into cup i in the cradle (layer 0: the alloying powder, to its column;
        layer 1: the top-up, to the set plug's line)."""
        metal, pw = SLOTS[i]
        pr = PRUN[metal]
        pname = pw if layer == 0 else AP.TOPUP[metal][0]
        grams = pr["alloying_g"] * (1 + ERR[i]) if layer == 0 else topup_g(i)
        h_from = 0.0 if layer == 0 else pr["column_mm_alloying"]
        h_to = pr["column_mm_alloying"] if layer == 0 else pr["column_mm_set"]
        m = MODULE[pname]
        if detail or car.state["shift"] != car.index_to(m):
            L.note(1, "Doser", f"indexing to module {m + 1} ({pname})")
            sc.step(st, cap, 2.2 * f, car.to(shift=car.index_to(m)), hold=H(0.1), cam_to=A.CAM_DOSE if detail else None)
        L.note(1, "Doser", f"module {m + 1} ({pname}) docking")
        ghost = m == MODULE["Si"]
        seat = K.station_cup()
        cam_dose = cam_near(seat, (120.0, -250.0, 95.0), (0.0, 0.0, 62.0))
        sc.step(st, cap, 1.2 * f, both(car.to(ext=CR.DOCK_EXT, magnet_on=True), car.ghost(0.18) if ghost else None),
                hold=H(0.1), cam_to=cam_dose if detail else None)
        L.note(1, "Doser", f"module {m + 1} tilted, dosing {pname} by auger turns")
        sc.step(st, cap, 1.3 * f, car.to(tilt=CR.TILT), hold=H(0.05))
        if detail:
            K.cut(i, True, sleeve=None, funnel=pname)
        spin0 = car.state["spin"]
        stt = car.to(spin=spin0 + 2 * math.pi * 2.0)

        def run(u, stt=stt):
            stt(u)
            on = 1.0 if 0.05 < u < 0.95 else 0.0
            pts = stream_points(L, K, i, u * 6.0, on)
            sc.alpha["stream"] = 1.0 if len(pts) else 0.0
            if len(pts):
                sc.set_mesh("stream", pv.PolyData(pts))
            k = min(1.0, max(0.0, (u - 0.12) / 0.83))
            if layer == 0:
                K._point[i] = k > 0.02
                K.powder_h[i] = h_to * max(0.0, (k - 0.08) / 0.92)
                K.powder_h2[i] = K.powder_h[i]
            else:
                K.powder_h2[i] = h_from + (h_to - h_from) * k
            K.apply()
            if detail:
                K.cut(i, True, sleeve=None, funnel=pname)
            L.note(1, "Doser", f"module {m + 1}: {grams * k:.2f} of {grams:.2f} g {pname} by auger turns")
        if still:
            STILLS[still] = sc.n + int(round(3.4 * f * 0.8 * scene.FPS))
        sc.step(st, cap, 3.4 * f, run, hold=0.3 if detail else 0.0, live=False)
        sc.alpha["stream"] = 0.0
        if layer == 0:
            K.powder_h[i] = h_to
            K._point[i] = True
        K.powder_h2[i] = h_to
        K.apply()
        L.note(1, "Doser", f"module {m + 1} back, undocking")
        sc.step(st, cap, 1.0 * f, car.to(tilt=0.0), hold=H(0.05))
        sc.step(st, cap, 0.7 * f, car.to(spin=spin0 + 2 * math.pi), hold=H(0.05))
        sc.step(st, cap, 0.9 * f, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0) if ghost else None),
                hold=H(0.1))
        K.cut(i, False, sleeve=None, funnel=pname)
        L.note(1, "Doser", f"module {m + 1} undocked")

    def topup_g(i):
        """The top-up, from the weighed alloying dose: for Cu-10Ni the Cu that keeps the cup at 10 wt % Ni; for
        Al-10Si the AlSi10Mg is itself 10 % Si, so the run's AlSi10Mg dose."""
        metal = SLOTS[i][0]
        pr = PRUN[metal]
        m_pw = read[i][0] - cup_g[metal]
        if metal == "Cu":
            return 9.0 * m_pw - pr["cup_plus_plug_g"]
        return pr["top_up_g"]

    # ------------------------------------------------------------------ layer 1: the alloying powder, weighed
    def layer1(i, fast):
        metal, pw = SLOTS[i]
        detail = not fast
        f = F_FAST if fast else F_DETAIL[metal]
        H = (lambda x: x) if detail else (lambda x: 0.0)
        pr = PRUN[metal]
        st = f"{3 if metal == 'Al' else 7}/{n}"
        first = detail and metal == "Al"
        cap = None
        if detail:
            cap = (f"The {A.ROBOT_NAME} takes an empty {CUP_NAME[metal]} cup from the rack, level, and slides it into "
                   f"the doser's cradle, under the {pw} funnel's stem: the stem stops 4 mm over the rim, so the funnel "
                   f"never touches a cup." if first else
                   f"The first Cu cup in full: it goes into the cradle under the Ni funnel.")
            L.note(0, "Arm", f"{CUP_NAME[metal]} cup {i + 1}: rack to the doser")
        rack_to_cradle(i, st, cap, f, H, detail)
        park(st, f, H, cam=A.CAM_MID if detail else None, cap=cap)
        if detail:
            cap = (f"The carousel brings module {MODULE[pw] + 1} ({pw}) to the station and docks it. It tilts and its "
                   f"auger turns: {pr['alloying_g']:.2f} g of {pw} falls onto its own funnel and through the stem into "
                   f"the cup's 1/2 in bore, up to {pr['column_mm_alloying']:.0f} mm. Cut open here: the bore fills "
                   f"from the 118° drill point." if first else
                   f"Module {MODULE[pw] + 1} doses {pr['alloying_g']:.2f} g of Ni, {pr['column_mm_alloying']:.0f} mm up "
                   f"the bore.")
        read[i] = [cup_g[metal] + pr["alloying_g"] * (1 + ERR[i]), None]
        dose(i, 0, st, cap, f, H, detail, still="dose" if first else None)
        if detail:
            cap = (f"Weighed on the HR-202i: the doser doses by auger turns, so the balance checks every cup. The door "
                   f"opens (driven: assumed; the HR-i's doors are manual) and the cup goes onto the pan." if first else
                   "Onto the HR-202i.")
            L.note(0, "Arm", f"cup {i + 1}: doser to the balance")
        cradle_to_balance(i, st, cap, f, H, detail)
        if detail:
            r = read[i][0]
            cap = (f"Door shut: {r:.4f} g, the cup's {cup_g[metal]:.2f} g (weighed once, when it was turned) plus "
                   f"{r - cup_g[metal]:.4f} g of {pw} against {pr['alloying_g']:.2f} g. Inside ±{TOL * 100:.0f} % "
                   f"(assumed), it goes on; a short cup would go back to the doser for more, as the trickler does on "
                   f"the HR-100A." if first else
                   f"{r:.4f} g: {r - cup_g[metal]:.4f} g of Ni against {pr['alloying_g']:.2f} g. A Cu cup is "
                   f"{r:.0f} g here, well inside the HR-202i's 220 g.")
        weigh(i, read[i][0], f"{read[i][0] - cup_g[metal]:.4f} g {pw}", st, cap, f, H, detail,
              still="weigh" if first else None)
        if detail:
            cap = "Back to the rack, to wait for its top-up."
        balance_to_rack(i, st, cap, f, H, detail)

    # ------------------------------------------------------------------ layer 2: the top-up, weighed, plug, press, away
    def layer2(i, fast):
        metal, pw = SLOTS[i]
        detail = not fast
        f = F_FAST if fast else F_DETAIL[metal]
        H = (lambda x: x) if detail else (lambda x: 0.0)
        pr = PRUN[metal]
        top_name = AP.TOPUP[metal][0]
        first = detail and metal == "Al"
        st = f"{5 if metal == 'Al' else 9}/{n}"
        cap = None
        if detail:
            cap = (f"Then the top-up. The cup goes back into the cradle, now under the {top_name} funnel."
                   if first else f"The first Cu cup again, now under the Cu funnel.")
            L.note(0, "Arm", f"cup {i + 1}: rack to the doser")
        rack_to_cradle(i, st, cap, f, H, detail)
        park(st, f, H, cam=A.CAM_MID if detail else None, cap=cap)
        g_top = topup_g(i)
        if detail:
            cap = (f"Module {MODULE[top_name] + 1}, {top_name}: {g_top:.2f} g tops the bore up to where the plug will "
                   f"stand, {pr['column_mm_set']:.0f} mm up, so the plug has powder to press. AlSi10Mg is itself 10 % "
                   f"Si, so the cup stays Al-10Si." if first else
                   f"Module {MODULE[top_name] + 1}: {g_top:.2f} g of Cu, worked out from the Ni the balance read so "
                   f"the cup stays 10 wt % Ni, tops the bore up to the plug line.")
        dose(i, 1, st, cap, f, H, detail)
        read[i][1] = read[i][0] + g_top * (1 + 0.5 * ERR[(i + 3) % len(ERR)])
        if detail:
            cap = "Weighed again: the top-up too." if first else "Weighed again."
        cradle_to_balance(i, st, cap, f, H, detail)
        r1, r2 = read[i]
        if detail:
            cap = (f"{r2:.4f} g: {r1 - cup_g[metal]:.4f} g of {pw} and {r2 - r1:.4f} g of {top_name}, tapped "
                   f"{pr['column_mm_set']:.0f} mm up the bore. Back to the rack for its plug.")
        weigh(i, r2, f"{r2 - r1:.4f} g {top_name}", st, cap, f, H, detail)
        balance_to_rack(i, st, cap, f, H, detail)
        # -------------------------------------------------- the plug, at the rack; then the cup onto the press's pin
        vp = K.vp
        d1 = rack_aim(i)
        c_r = K.rack_cup(i) + (0, 0, CUP_GRASP)
        if detail:
            cap = (f"Its plug goes into the mouth at the rack, on its 15° lead-in, 8.0 mm proud: low down, where the "
                   f"gripper can come at it from above. (The press works too high for that: the wrist would hit the "
                   f"VLM's opening.)" if first else "The plug, into the mouth at the rack.")
            L.note(0, "Arm", f"plug {i + 1}: into its cup")
        g0 = K.rack_plug(i) + (0, 0, PLUG_GRASP)
        sc.step(st, cap, 1.2 * f, both(pre(dwn(g0 + (0, 0, 120)), dwn(g0), OPEN_PLUG), rb.grip_to(OPEN_PLUG)),
                hold=H(0.05))
        sc.step(st, cap, 0.7 * f, rb.line_to(dwn(g0)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_PLUG), hold=H(0.05))
        rb.grasp(f"plug{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g0 + (0, 0, 120))), hold=H(0.05))
        lead = C.PLUG_LEADIN_L * 0.98                       # the lead-in lets the plug stand 1.5 mm in the mouth
        top = K.rack_cup(i) + (0, 0, C.SLUG_L)
        g1 = top + (0, 0, PLUG_GRASP - lead)
        sc.step(st, cap, 1.1 * f, pre(dwn(g1 + (0, 0, 110)), dwn(g1 + (0, 0, 3))), hold=H(0.05))
        sc.step(st, cap, 0.8 * f, rb.line_to(dwn(g1 + (0, 0, 3))), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.line_to(dwn(g1)), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.grip_to(OPEN_PLUG), hold=H(0.05))
        rb.release(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(dwn(g1 + (0, 0, 140))), hold=H(0.05))
        if detail:
            cap = (f"Then the cup, its plug riding in the mouth, goes to the vacuum press (a Specac Atlas Autotouch 15T, on "
                   f"tray B since set-up). The arm stands it on the raised ejector pin of the lab's evacuable die, its "
                   f"bottom {VPm.CATCH:.0f} mm down in the catch ring on F1, so it can't tip; the pin lowers it into F1, "
                   f"#222's steel sleeve." if first else
                   "Into the die's catch ring, on the pin, which lowers it into F1.")
            L.note(0, "Arm", f"cup {i + 1}: rack to press")
        bk = rack_bk[i]
        sc.step(st, cap, 1.2 * f, both(pre(lvl(c_r - d1 * bk + (0, 0, 30), d1), lvl(c_r, d1), OPEN_RACK),
                                       rb.grip_to(OPEN_RACK)), hold=H(0.05))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r, d1)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(c_r + (0, 0, 30), d1)), hold=0.0)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r - d1 * bk + (0, 0, 30), d1)), hold=H(0.05))
        q_up = vp.cup_seat() + (0, 0, CUP_GRASP)
        dq = aim(q_up, [(170, 50), (0, 50), (0, 1), (170, 0)], radial(q_up))
        cam_press = cam_near(vp.die_top(), (-430.0, -760.0, 420.0), (60.0, 0.0, 40.0))
        sc.step(st, cap, 1.5 * f, pre(lvl(q_up - dq * 170 + (0, 0, 50), dq), lvl(q_up + (0, 0, 50), dq)), hold=H(0.05),
                cam_to=cam_press if detail else None,
                labels=[] if not first else [
                    ("vacuum press, on tray B since set-up: Specac Atlas Autotouch 15T", vp.die_top() + (120, 150, 260),
                     (0.56, 0.20)),
                    ("our evacuable die round F1, on its shuttle", vp.die_top() + (30, 0, -30), (0.16, 0.62)),
                    (f"catch ring: holds the cup's bottom {VPm.CATCH:.0f} mm", vp.die_top() + (-12, -6, 0), (0.62, 0.70)),
                    ("vacuum pump, valves, gauge", vp.world("vpress", (-420, -20, 240)), (0.12, 0.34))])
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(q_up + (0, 0, 50), dq)), hold=H(0.05))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q_up + (0, 0, 1), dq)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
        rb.release("vp_pin")
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q_up - dq * 170, dq)), hold=H(0.05), labels=[])
        sc.step(st, cap, 0.9 * f, vp.to(e=0.0), hold=H(0.05))
        L.note(3, "Press", "cup in F1, plug 8.0 mm proud")
        # the punch, from its rest, into the die on the plug, held level by its flange: its O-ring seals the bore
        if detail:
            cap = ("Then the die's punch, from its rest beside the press, held level by its flange. It goes down into "
                   "the die's bore and stands on the plug; its O-ring seals the bore, and the channel across the plug's "
                   "top (DAL #156) keeps the vent open under it." if first else "The punch, from its rest into the die.")
            L.note(0, "Arm", "punch: rest to die")
        gp = vp.punch_grasp_rest()
        gd = vp.punch_grasp_die()
        dp = aim(gp, [(150, 0), (0, 0), (0, AP.REST_POCKET + 20)], radial(gp))
        dd = aim(gd, [(0, 32), (0, 2), (0, 0), (160, 0)], radial(gd))
        sc.step(st, cap, 1.3 * f, both(pre(lvl(gp - dp * 150, dp), lvl(gp, dp), AP.OPEN_FLANGE),
                                       rb.grip_to(AP.OPEN_FLANGE)), hold=H(0.05))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gp, dp)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(AP.GRIP_FLANGE), hold=H(0.05))
        rb.grasp("vp_punch")
        vp.punch_at = "held"
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(gp + (0, 0, AP.REST_POCKET + 20), dp)), hold=H(0.05))
        sc.step(st, cap, 1.1 * f, pre(lvl(gd + (0, 0, 32), dd), lvl(gd + (0, 0, 2), dd)), hold=H(0.05))
        sc.step(st, cap, 0.8 * f, rb.line_to(lvl(gd + (0, 0, 2), dd)), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.line_to(lvl(gd, dd)), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.grip_to(AP.OPEN_FLANGE), hold=H(0.05))
        rb.release("vp_shuttle")
        vp.punch_into_die()
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gd - dd * 160, dd)), hold=H(0.05))
        park(st, f, H, cap=cap)
        # -------------------------------------------------- the press cycle, under vacuum
        if detail:
            cap = ("The shuttle carries the die in under the leadscrew and the guard comes down: the press won't start "
                   "with it up. V1 opens to the pump, slowly at first through the needle valve so the powder stays put. "
                   "Air leaves the cup through the plug's vent and out of the die's port: under 1 mbar in about 2 min."
                   if first else "Shuttle in, guard down, pumped below 1 mbar.")
            L.note(3, "Press", "shuttle in, guard down")
        in_c = vp.world("vpress", (VPm.AXX, VPm.AXY, VPm.Z_PISTON + VPm.CUP_BASE + 52.0))
        cam_cut = cam_near(in_c, (110.0, -300.0, 70.0), (0.0, 0.0, 0.0))
        sc.step(st, cap, 1.2 * f, vp.to(y=VPm.AXY), hold=H(0.05), cam_to=cam_near(
            in_c, (420.0, -880.0, 380.0), (0.0, 40.0, 40.0)) if detail else None)
        sc.step(st, cap, 1.0 * f, vp.to(guard=0.0), hold=H(0.05))
        if detail:
            K.cut(i, True, sleeve=True)
        plug_local = sc.gmat[f"plug{i}"].copy()
        plug_z0 = float(plug_local[2, 3])

        def pump(u):
            vp.st["mbar"] = 1013.0 * (0.8 / 1013.0) ** u
            vp.apply()
            on = 0.02 < u < 0.9 and detail
            sc.alpha["vpress/air"] = 1.0 if on else 0.0
            if on:
                vp.air(f"cup{i}", u * 3.0, plug_z0)
            L.note(3, "Press", vp.gauge())
        sc.step(st, cap, 3.0 * f, pump, hold=H(0.2), cam_to=cam_cut if detail else None, live=False)
        sc.alpha["vpress/air"] = 0.0
        if detail:
            cap = (f"Start: program 1 pumps up to {AP.SET_T:.1f} t ({AP.SET_T * 9.80665:.1f} kN). The ram lifts the die "
                   f"2 mm to the leadscrew, then drives the plug {VPm.TRAVEL:.1f} mm to flush: the powder goes from "
                   f"{100 * pr['rel_density_set']:.0f} to {100 * pr['rel_density_flush']:.0f} % dense, with no air in it "
                   f"(DAL #140). It holds a minute, topping the load up as the powder settles; at flush the punch's "
                   f"collar lands on the catch ring, and F1 under it takes what's left." if first else
                   f"{AP.SET_T:.1f} t: the plug goes {VPm.TRAVEL:.1f} mm to flush, the powder from "
                   f"{100 * pr['rel_density_set']:.0f} to {100 * pr['rel_density_flush']:.0f} % dense.")
        h_set = pr["column_mm_set"]

        def press(u):
            r = (VPm.GAP + VPm.TRAVEL) * u
            x = max(0.0, r - VPm.GAP)
            vp.st["ram"], vp.st["x"] = r, x
            vp.st["load"] = AP.SET_T * (0.0 if r <= VPm.GAP else min(1.0, 0.25 * (x / VPm.TRAVEL) + 0.75 *
                                                                     (x / VPm.TRAVEL) ** 3))
            sc.gmat[f"plug{i}"] = T((0, 0, -x)) @ plug_local
            K.squeeze[i] = (h_set - x) / h_set
            K.apply()
            L.note(3, "Press", vp.gauge())
        if first:
            STILLS["press"] = sc.n + int(round(3.0 * f * scene.FPS * 0.92))
        sc.step(st, cap, 3.0 * f, press, hold=H(0.05))
        L.note(3, "Press", vp.gauge() + ", holding")
        sc.step(st, cap, 0.8 * f, None, hold=0.6 if detail else 0.0)
        if detail:
            cap = ("Slow release; V2 lets dry argon into the die, so the cup sees no air until it is out; the guard goes "
                   "up and the shuttle brings the die out. The plug is flush with the rim." if first else
                   "Released, vented with dry Ar, out.")
        sc.step(st, cap, 1.0 * f, vp.to(load=0.0, ram=0.0), hold=H(0.05))
        sc.step(st, cap, 1.2 * f, vp.to(mbar=1013.0), hold=H(0.05))
        L.note(3, "Press", vp.gauge() + ", vented with Ar")
        K.cut(i, False, sleeve=True)
        sc.step(st, cap, 1.0 * f, vp.to(guard=1.0), hold=H(0.05), cam_to=cam_press if detail else None)
        sc.step(st, cap, 1.2 * f, vp.to(y=VPm.Y_OUT), hold=H(0.05))
        L.note(3, "Press", "shuttle out, plug flush")
        # the punch back to its rest; the pin pushes the cup up out of F1
        if detail:
            cap = (f"The arm lifts the punch off, now the die is vented (under vacuum it would be held down with about "
                   f"30 N), and puts it back on its rest. The pin pushes the cup up out of F1 and stops with its bottom "
                   f"{VPm.CATCH:.0f} mm in the catch ring: it stands there, steady, until the arm takes it." if first else
                   "The punch back on its rest; the pin pushes the cup up into the catch ring.")
            L.note(0, "Arm", "punch: die to rest")
        gd2 = vp.punch_grasp_die() - (0, 0, VPm.TRAVEL)
        sc.step(st, cap, 1.2 * f, both(pre(lvl(gd2 - dd * 160, dd), lvl(gd2, dd), AP.OPEN_FLANGE),
                                       rb.grip_to(AP.OPEN_FLANGE)), hold=H(0.05))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gd2, dd)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(AP.GRIP_FLANGE), hold=H(0.05))
        rb.grasp("vp_punch")
        vp.punch_at = "held"
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gd2 + (0, 0, 40), dd)), hold=H(0.05))
        sc.step(st, cap, 1.1 * f, pre(lvl(gp + (0, 0, AP.REST_POCKET + 20), dp), lvl(gp + (0, 0, 1), dp)),
                hold=H(0.05))
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(gp + (0, 0, 1), dp)), hold=H(0.05))
        sc.step(st, cap, 0.3 * f, rb.grip_to(AP.OPEN_FLANGE), hold=H(0.05))
        rb.release("vpress")
        vp.punch_rest()
        vp.st["x"] = 0.0
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(gp - dp * 150, dp)), hold=H(0.05))
        sc.step(st, cap, 0.8 * f, vp.to(e=VPm.VP["eject"]), hold=H(0.05))
        L.note(3, "Press", "cup ejected, shuttle out")
        made[metal] += 1
        charge_line()
        # -------------------------------------------------- away: Al cups to the MiR's carrier, Cu cups to the rack
        q = K.nest_seat() + (0, 0, CUP_GRASP)
        if detail:
            charged = r2 - cup_g[metal] + pr["cup_plus_plug_g"]
            cap = (f"The charged cup, {charged:.1f} g, its plug flush on {r2 - cup_g[metal]:.1f} g of powder pressed to "
                   f"{100 * pr['rel_density_flush']:.0f} % under vacuum, goes onto the carrier on the MiR250's cabinet, "
                   f"beside the arm, for the atomizer." if metal == "Al" else
                   f"The charged Cu cup, {charged:.1f} g, goes back on the rack for its own run.")
            L.note(0, "Arm", f"cup {i + 1}: press to the {'MiR' if metal == 'Al' else 'rack'}")
        sc.step(st, cap, 1.2 * f, both(pre(lvl(q - dq * 170, dq), lvl(q, dq), OPEN_CUP), rb.grip_to(OPEN_CUP)),
                hold=H(0.05),
                cam_to=cam_near(K.nest_seat(0.0), (-520.0, -760.0, 470.0), (60.0, 0.0, 60.0)) if detail else None)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q, dq)), hold=H(0.05))
        sc.step(st, cap, 0.4 * f, rb.grip_to(GRIP_CUP), hold=H(0.05))
        rb.grasp(f"cup{i}")
        sc.step(st, cap, 0.6 * f, rb.line_to(lvl(q + (0, 0, 40), dq)), hold=0.0)
        sc.step(st, cap, 0.7 * f, rb.line_to(lvl(q - dq * 170 + (0, 0, 40), dq)), hold=H(0.05))
        if metal == "Al":
            k = sum(1 for s in SLOTS[:i] if s[0] == "Al")
            c = K.carrier_seat(k) + (0, 0, CUP_GRASP)
            d = aim(c, [(170, 40, GRIP_CUP), (0, 40, GRIP_CUP), (0, 1, GRIP_CUP), (0, 1, OPEN_CUP), (170, 0, OPEN_CUP)],
                    (0.0, -1.0), only={f"cup{i}", f"plug{i}", "amr"})
            sc.step(st, cap, 1.6 * f, pre(lvl(c - d * 170 + (0, 0, 40), d), lvl(c + (0, 0, 40), d)), hold=H(0.05),
                    cam_to=CAM_AMR if detail else None)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c + (0, 0, 40), d)), hold=H(0.05))
            sc.step(st, cap, 0.6 * f, rb.line_to(lvl(c + (0, 0, 1), d)), hold=H(0.05))
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_CUP), hold=H(0.05))
            rb.release("amr")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c - d * 170, d)), hold=H(0.05))
        else:
            sc.step(st, cap, 1.4 * f, pre(lvl(c_r - d1 * bk + (0, 0, 30), d1), lvl(c_r + (0, 0, 30), d1)),
                    hold=H(0.05), cam_to=CAM_RACK if detail else None)
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r + (0, 0, 30), d1)), hold=H(0.05))
            sc.step(st, cap, 0.5 * f, rb.line_to(lvl(c_r + (0, 0, 1), d1)), hold=H(0.05))
            sc.step(st, cap, 0.4 * f, rb.grip_to(OPEN_RACK), hold=H(0.05))
            rb.release("crack")
            sc.step(st, cap, 0.7 * f, rb.line_to(lvl(c_r - d1 * bk, d1)), hold=H(0.05))
        park(st, f, H, cap=cap)

    pa, pc = PRUN["Al"], PRUN["Cu"]
    cam_fork = cam_near(K.station_funnel(), (330.0, -650.0, 230.0), (-60.0, 0.0, 10.0))
    # ------------------------------------------------------------------ 2. the Si funnel into the fork
    cap = ("The Si funnel goes into the doser's fork. It is only ever used for Si, and its stem points into the cup's "
           "bore without touching it, so nothing passes from one powder or one cup to the next.")
    with_caption(sc, cap, lambda: funnel_to_station("Si", f"2/{n}", 0.6, cam=CAM_RIGHT))
    with_caption(sc, cap, lambda: sc.step(f"2/{n}", None, 0.8, None, hold=0.6, cam_to=cam_fork))
    STILLS["funnels"] = sc.n - 2
    # ------------------------------------------------------------------ 3. the four Al cups' Si, the first in full
    layer1(0, fast=False)
    cap = (f"The same for the other three Al cups, shown faster: {pa['alloying_g']:.2f} g of Si each, every one "
           f"weighed.")
    sc.step(f"3/{n}", cap, 0.6, None, hold=1.2, cam_to=CAM_WORK)
    for i in (1, 2, 3):
        with_caption(sc, cap, lambda i=i: layer1(i, fast=True), cut=True)
    # ------------------------------------------------------------------ 4. the Si funnel out, the AlSi10Mg funnel in
    cap = ("Now the top-up, the cup's own metal: the Si funnel goes back to its place on the stand and the AlSi10Mg "
           "funnel takes the fork. One funnel per powder: a funnel that has carried Si never carries anything else.")
    with_caption(sc, cap, lambda: funnel_to_stand("Si", f"4/{n}", 0.4, cam=CAM_RIGHT))
    with_caption(sc, cap, lambda: funnel_to_station("AlSi10Mg", f"4/{n}", 0.4))
    # ------------------------------------------------------------------ 5. top-up, plug, press: the first in full
    layer2(0, fast=False)
    cap = (f"The other three Al cups the same way, faster: {pa['top_up_g']:.2f} g of AlSi10Mg each, weighed, plugged, "
           f"pressed at {AP.SET_T:.1f} t under vacuum and onto the MiR250. Four cups make the run's "
           f"{4 * pa['charged_cup_g']:.1f} g of Al-10Si.")
    sc.step(f"5/{n}", cap, 0.6, None, hold=1.4, cam_to=CAM_WORK)
    for i in (1, 2, 3):
        with_caption(sc, cap, lambda i=i: layer2(i, fast=True), cut=True)
    # ------------------------------------------------------------------ 6. the AlSi10Mg funnel out, the Ni funnel in
    cap = ("Then the Cu-10Ni run. The AlSi10Mg funnel goes back to the stand and the Ni funnel takes the fork, so no "
           "Al run powder reaches a Cu cup.")
    with_caption(sc, cap, lambda: funnel_to_stand("AlSi10Mg", f"6/{n}", 0.32, cam=CAM_RIGHT))
    with_caption(sc, cap, lambda: funnel_to_station("Ni", f"6/{n}", 0.32))
    # ------------------------------------------------------------------ 7. the four Cu cups' Ni
    layer1(4, fast=False)
    cap = (f"The other three Cu cups' Ni, faster: {pc['alloying_g']:.2f} g each, weighed.")
    sc.step(f"7/{n}", cap, 0.5, None, hold=0.9, cam_to=CAM_WORK)
    for i in (5, 6, 7):
        with_caption(sc, cap, lambda i=i: layer1(i, fast=True), cut=True)
    # ------------------------------------------------------------------ 8. the Ni funnel out, the Cu funnel in
    cap = "The Ni funnel back to the stand; the Cu funnel takes the fork for the Cu cups' top-up."
    with_caption(sc, cap, lambda: funnel_to_stand("Ni", f"8/{n}", 0.3, cam=CAM_RIGHT))
    with_caption(sc, cap, lambda: funnel_to_station("Cu", f"8/{n}", 0.3))
    # ------------------------------------------------------------------ 9. the Cu cups' top-up, plug, press
    layer2(4, fast=False)
    cap = (f"The other three Cu cups, faster: Cu to the plug line, weighed, plugged and pressed. A charged Cu cup is "
           f"{pc['charged_cup_g']:.0f} g. They go back on the rack for their own run.")
    sc.step(f"9/{n}", cap, 0.5, None, hold=0.9, cam_to=CAM_WORK)
    for i in (5, 6, 7):
        with_caption(sc, cap, lambda i=i: layer2(i, fast=True), cut=True)
    with_caption(sc, cap, lambda: funnel_to_stand("Cu", f"9/{n}", 0.3))
    with_caption(sc, cap, lambda: park(f"9/{n}", 0.4, lambda x: 0.0))
    # ------------------------------------------------------------------ 10. tray B up; ready for the atomizer
    al_g = sum(read[i][1] - cup_g["Al"] + pa["cup_plus_plug_g"] for i in range(4))
    cu_g = sum(read[i][1] - cup_g["Cu"] + pc["cup_plus_plug_g"] for i in range(4, 8))
    cap = (f"Made up: four Al-10Si cups, {al_g:.1f} g together, on the MiR250 for the rePowder, and four 90/10 Cu-Ni "
           f"cups on the rack, {cu_g:.1f} g, for their own run (designed compositions, if every gram dissolves; "
           f"out/alloy_recipe_pressed.json). Tray B goes back into storage.")
    L.store("B", f"10/{n}", cap, cam=CAM_AMR)
    L.note(0, "Arm", "parked; next: the atomizer")
    sc.step(f"10/{n}", cap, 1.6, None, hold=2.4, still=True,
            cam_to=cam_near((K.carrier_seat(1) + K.carrier_seat(2)) / 2, (-600.0, -640.0, 340.0), (0.0, 0.0, 25.0)),
            labels=[("four charged 5N Al cups, for the rePowder", (K.carrier_seat(1) + K.carrier_seat(2)) / 2 + (0, 0, 90),
                     (0.30, 0.25))])
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm; opening top {V.Z_OPEN_TOP:.0f} mm", flush=True)
    print(f"{sc.n} frames, {sc.n / scene.FPS:.1f} s", flush=True)
    out = sc.save()
    if not (scene.PREVIEW or os.environ.get("ARM_AUDIT")):
        cut_stills()
    if auditor is not None:
        auditor.save()
    return out


def cut_stills():
    """out/alloy_charge_<name>.png: the frames STILLS names, cut from the MP4 (alloy_route.SHEET uses _press)."""
    mp4 = OUT / "mp4" / f"{NAME}.mp4"
    for name, k in STILLS.items():
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"select=eq(n\\,{int(k)})",
                        "-vframes", "1", str(OUT / f"{NAME}_{name}.png")], check=False)
    (OUT / f"{NAME}.json").write_text(json.dumps(dict(json.loads((OUT / f"{NAME}.json").read_text()),
                                                      stills=STILLS), indent=1, ensure_ascii=False) + "\n")


def with_caption(sc, cap, fn, cut=False):
    """Run fn() with every sub-step that has no caption of its own given `cap`. cut=True (the time-lapse): a sub-step
    shorter than FAST_CUT with no hold happens between two frames (its update run to the end at once), so a cup's
    approach, grip and retreat cost no frames and the joint moves, the dose and the press stroke carry the cut."""
    orig = sc.step

    def step(label, caption, seconds, update=None, hold=1.2, cam_to=None, labels=(), **kw):
        if cut and seconds < FAST_CUT and hold <= 0 and not labels:
            if update is not None:
                update(1.0)
            if cam_to is not None:
                sc.cam = list(cam_to)
            return None
        return orig(label, caption if caption is not None else cap, seconds, update, hold=hold, cam_to=cam_to,
                    labels=labels, **kw)
    sc.step = step
    try:
        fn()
    finally:
        sc.step = orig


def tray_xyz(L: A.Lab, xyz) -> np.ndarray:
    return (L.sc.world("tray_B") @ np.r_[np.asarray(xyz, float), 1.0])[:3]


if __name__ == "__main__":
    movie()

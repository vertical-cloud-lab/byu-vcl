"""The anti-static brush the container clip uses (atom_container.py), as a tool a robot can hold, and its head station
on MiR250 1 (#303, round 14). No scene is built here: meshes and the numbers the clip needs.

Sterling on PR #318 (2026-11-20), at the moment the arm puts the brush back on its rest: "There's also not much of an
automation-friendly grip for the gripper. Seems like it would slip out." And: "Cross-contamination for the
anti-static brush is going to be a concern.. how to handle that? Thorough cleaning? (e.g., ultrasonic cleaning).
Disposable heads? (e.g., kind of like disposable wand attachments in other contexts)."

**The grip (ours).** Round 12/13's brush was a plain 18 mm round handle: the 2F-85's flat pads held it by friction
alone, so it could turn about its own axis and, with 0.3 kg of brush 0.3 m out, pivot about the fingers' closing line
(the usual way a parallel gripper drops a long tool). Now the 2F-85 holds an 18 x 18 mm square grip block, so flat pads
on flat faces can't turn about the shaft, between two collars that stand 1 mm clear of the fingertips' sides
(``ur_arm``'s fingertips span y -14.3..13.5 mm in the TCP frame, closed on 18.8 mm): the brush can't slide along the
fingers, and it can't pivot about their closing line more than a few degrees before a fingertip bears on a collar.
The pads close on the same 18.8 mm gap as before, so the grasp and every brushing pose are unchanged.

**The rest (ours).** Two V-blocks under the shaft centre it; the first has a slot that takes a fin hanging under the
shaft by the grip, so the brush lies one way only (fin down, bristles out) and can't roll or slide off. The slot is
long enough for the 25 mm push that puts a fresh head on.

**One head per run (ours).** The head (bristles, block and an orange ferrule) is pushed onto a 12 mm spigot at the shaft's
end and held by a spring detent, like a pipette tip: push on, strip off. The brush waits on its rest with a fresh head
sitting in the rest's pocket. After brushing, the arm drops the shaft into a slotted stripper bar across a grounded
waste can and pulls back: the bar holds the ferrule, the head comes off and falls into the can, with the powder it
carries. The headless shaft goes back onto the rest 25 mm short and pushes onto the next head, which a spring-fed
magazine has slid into the pocket. So no bristle that touched one alloy touches the next, and nothing is washed.

**Why not clean the brush between alloys.** Ultrasonic cleaning in IPA was the alternative. It was rejected because:
- it puts reactive fine Al (and Mg, Li alloy) powder into a solvent bath: a fire load, and a new solvent waste stream
  to collect, store and ship;
- a brush has to dry completely before it touches dry powder again (wet bristles cake fines), which adds time between
  runs;
- the powder lodges at the bristles' roots, where nothing on the arm can see or test whether the brush is clean, so a
  cleaned brush can't be shown to be free of the last alloy.

A head goes to the same combustible-metal waste as the vacuum's liners. Its bristles are conductive (carbon or stainless
fibre, as anti-static brushes are); the head's size and cost are ours, not a product's.

Frames: the brush's meshes are in its TCP frame (the grasp point: tool x the fingers' closing line, y along the shaft
towards the head, z the approach, the gripper on the -z side), so a brush group's matrix *is* its TCP pose. The head is
its own group in the same frame, riding on the brush when it is on the spigot. The rest, the pocket and magazine, and
the can are in MiR250 1's local frame (z = 0 on the floor), built for the brush resting at REST (x, y) and the cabinet
top at height ``top``.
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

# ------------------------------------------------------------------------------------------------ colours
OURS = (0.20, 0.42, 0.75)               # our machined parts, blue (as atom_nilfisk.py)
OURS_DK = (0.14, 0.24, 0.42)
SS = (0.72, 0.73, 0.75)                 # the shaft: stainless, so it bonds to the arm's flange
SS_DK = (0.52, 0.53, 0.56)
HEAD_BODY = (0.17, 0.17, 0.19)
FERRULE = (0.93, 0.48, 0.12)            # the disposable part reads orange
BRISTLE_NEW = (0.20, 0.19, 0.18)
BRISTLE_USED = (0.47, 0.46, 0.43)       # dusted with the run's powder (the clip's dust is (0.36, 0.35, 0.33))
STAND = (0.30, 0.32, 0.36)              # the MiR's fixtures, as chapter 2's
CAN = (0.42, 0.44, 0.47)
SPRING = (0.62, 0.64, 0.66)
GN_YE = (0.30, 0.65, 0.20)              # the can's ground strap

# ------------------------------------------------------------------------------------------------ the brush (TCP frame)
GRIP_GAP = 18.0                         # the grip block's flats, across x
GRIP_CLOSE_GAP = GRIP_GAP + 0.8         # the pads close 0.4 mm off each flat (LT.close_for_gap(18.8), as before)
COLLAR_R = 18.5                         # the collars' radius: wide enough to stop a fingertip (|x| >= 9.4), short of
                                        # the inner knuckles (z <= -19.4 in the TCP frame)
COLLAR_IN = (-15.3, 14.5)               # the collars' inner faces, y: 1 mm off the fingertips' sides (-14.3, 13.5)
COLLAR_T = 6.0
SHAFT_R = 9.0
SHAFT_Y = (-40.0, 598.0)                # the shaft runs past the grip to an end cap, and on to the spigot's shoulder
SPIGOT_R, SPIGOT_Y = 6.0, (598.0, 618.0)
FIN = dict(x=2.0, y=(55.0, 85.0), z=(SHAFT_R, SHAFT_R + 25.0))   # hangs under the shaft at rest (tool +z is down there)
# the head: an orange ferrule over the spigot, the block and bristles where round 12's were (BRUSH_TIP unchanged)
FERRULE_R, FERRULE_BORE, FERRULE_Y = 11.0, 6.3, (598.0, 626.0)
BLOCK = dict(x=(-10.0, 8.0), y=(620.0, 660.0), z=(-32.0, 32.0))
BRISTLES = dict(x=(-40.0, -10.0), y=(622.0, 658.0), z=(-30.0, 30.0))
BRUSH_TIP = np.array([-40.0, 640.0, 0.0])
PUSH = 25.0                             # mm the shaft moves to go fully onto a head (the spigot is 20 mm long)
PUSH_SHORT = 0.3                        # it stops this short of the ferrule's back face (the detent has clicked)
DETENT_N = 30.0                         # the spring detent's hold, N (ours, assumed)


def _box(x0, x1, y0, y1, z0, z1) -> pv.PolyData:
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _cyl_y(r, y0, y1, x=0.0, z=0.0, res=32) -> pv.PolyData:
    return pv.Cylinder(center=(x, (y0 + y1) / 2, z), direction=(0, 1, 0), radius=r, height=y1 - y0,
                       resolution=res).triangulate()


def _tube_y(ro, ri, y0, y1, res=32) -> pv.PolyData:
    """A tube along y, its bore open at both ends (as a closed solid: outer wall, inner wall, two rings)."""
    th = np.linspace(0, 2 * math.pi, res, endpoint=False)
    pts, faces = [], []
    for y in (y0, y1):
        for r in (ro, ri):
            pts += [(r * math.cos(t), y, r * math.sin(t)) for t in th]
    pts = np.array(pts)
    n = res

    def q(a, b, c, d):
        faces.extend([4, a, b, c, d])
    for k in range(n):
        k1 = (k + 1) % n
        q(k, k1, 2 * n + k1, 2 * n + k)                       # outer wall
        q(n + k, 3 * n + k, 3 * n + k1, n + k1)               # inner wall
        q(k, n + k, n + k1, k1)                               # the y0 ring
        q(2 * n + k, 2 * n + k1, 3 * n + k1, 3 * n + k)       # the y1 ring
    return pv.PolyData(pts, faces=np.array(faces)).triangulate().clean()


def brush_meshes() -> dict:
    """{name: (mesh, colour)}: the brush's handle, TCP frame. The grip block and collars are ours (blue); the shaft
    and spigot stainless."""
    g = GRIP_GAP / 2
    grip = _box(-g, g, COLLAR_IN[0], COLLAR_IN[1], -g, g)
    collars = _cyl_y(COLLAR_R, COLLAR_IN[0] - COLLAR_T, COLLAR_IN[0], res=40).merge(
        _cyl_y(COLLAR_R, COLLAR_IN[1], COLLAR_IN[1] + COLLAR_T, res=40))
    shaft = _cyl_y(SHAFT_R, SHAFT_Y[0], COLLAR_IN[0] - COLLAR_T).merge(
        _cyl_y(SHAFT_R, COLLAR_IN[1] + COLLAR_T, SHAFT_Y[1]))
    spigot = _cyl_y(SPIGOT_R, *SPIGOT_Y, res=24)
    fin = _box(-FIN["x"], FIN["x"], FIN["y"][0], FIN["y"][1], FIN["z"][0] - 1.0, FIN["z"][1])
    return {"atc brush grip": (grip, OURS), "atc brush collars": (collars.merge(fin), OURS_DK),
            "atc brush shaft": (shaft, SS), "atc brush spigot": (spigot, SS_DK)}


def head_meshes(tag: str) -> dict:
    """{name: (mesh, colour)}: one disposable head, in the brush's TCP frame (where it sits on the spigot)."""
    ferrule = _tube_y(FERRULE_R, FERRULE_BORE, *FERRULE_Y, res=36)
    block = _box(*BLOCK["x"], *BLOCK["y"], *BLOCK["z"])
    bris = _box(*BRISTLES["x"], *BRISTLES["y"], *BRISTLES["z"])
    return {f"atc head{tag} ferrule": (ferrule, FERRULE), f"atc head{tag} block": (block, HEAD_BODY),
            f"atc head{tag} bristles": (bris, BRISTLE_NEW)}


def head_extent_tool() -> tuple[np.ndarray, np.ndarray]:
    """The head's bounding box in the TCP frame (lo, hi)."""
    lo = np.array([min(BRISTLES["x"][0], -FERRULE_R), FERRULE_Y[0], min(BLOCK["z"][0], -FERRULE_R)])
    hi = np.array([max(BLOCK["x"][1], FERRULE_R), BLOCK["y"][1], max(BLOCK["z"][1], FERRULE_R)])
    return lo, hi


# ------------------------------------------------------------------------------------------------ on MiR250 1
# The brush rests along MiR-local +x (tool y), bristles to local -y (tool -x), tool z down: a tool-frame point (tx, ty,
# tz) is at local (x_r + ty, y_r + tx, z_r - tz), with (x_r, y_r, z_r) the grip's centre.
REST = (-270.0, -190.0)                 # the grip's centre on the rest, MiR-local x, y (round 12's place)
REST_DZ = 71.0                          # the shaft's axis this far over the cabinet top (62 mm blocks + its radius)
REST_A_X = (-245.0, -170.0)             # the first V-block, with the fin's slot (the fin at rest and 25 mm short)
REST_B_X = (138.0, 162.0)               # the second, plain
V_HALF = 22.0                           # the V-blocks are 44 wide
FIN_SLOT = (-242.0, -183.0)             # x; the fin is at x -215..-185 at rest and -240..-210 before the push
POCKET_PITCH = 52.0                     # the magazine's heads, along local -y
STRIP = (-260.0, -100.0, 150.0)         # the grip's centre when the head goes into the stripper: local x, y, and the
                                        # shaft's height over the cabinet top
STRIP_PULL = 30.0                       # the pull back along -x: the head stops at the bar after 3 mm
CAN_C, CAN_R, CAN_H = (366.0, -114.5), 44.0, 110.0   # round the falling head with 2-3 mm all round, clear of
                                        # the pocket's wall (y -172) and the container cradle (y -70)
BAR_X = (329.0, 335.0)                  # the stripper bar: across the can's mouth, standing on its rim
SLOT_W = 20.0                           # the bar's slot: the 18 mm shaft passes, the 22 mm ferrule doesn't


def _v_block(x0, x1, yc, top, z_axis, slot=None) -> pv.PolyData:
    """A V-block: base on the cabinet top, a 90 deg V whose faces are tangent to the shaft (radius SHAFT_R) with its
    axis z_axis over the floor; `slot` (half-width, z bottom) cuts a slot down the middle for the fin."""
    z_ap = z_axis - SHAFT_R * math.sqrt(2.0)            # the V's apex
    zt = z_axis - 1.0                                    # the block's top: the V is 2 x (zt - z_ap) wide there
    h = V_HALF

    def prism(poly_yz):
        pts = np.array([[x0, yc + y, z] for y, z in poly_yz] + [[x1, yc + y, z] for y, z in poly_yz])
        n = len(poly_yz)
        faces = [n] + list(range(n)) + [n] + list(range(2 * n - 1, n - 1, -1))
        for k in range(n):
            k1 = (k + 1) % n
            faces += [4, k, n + k, n + k1, k1]
        return pv.PolyData(pts, faces=faces).triangulate()
    if slot is None:
        return prism([(-h, top), (h, top), (h, zt), (zt - z_ap, zt), (0.0, z_ap), (-(zt - z_ap), zt), (-h, zt)])
    sw, zb = slot
    z_s = z_ap + sw                                       # the V's face where it meets the slot
    left = prism([(-h, zb), (-sw, zb), (-sw, z_s), (-(zt - z_ap), zt), (-h, zt)])
    right = prism([(sw, zb), (h, zb), (h, zt), (zt - z_ap, zt), (sw, z_s)])
    base = _box(x0, x1, yc - h, yc + h, top, zb)
    return left.merge(right).merge(base)


def rest_meshes(top: float) -> dict:
    """{name: (mesh, colour)}: the brush's two V-blocks, MiR-local."""
    z_axis = top + REST_DZ
    yc = REST[1]
    fin_bottom = z_axis - FIN["z"][1] - 2.0                # 2 mm under the fin
    a = _v_block(*REST_A_X, yc, top, z_axis, slot=(FIN["x"] + 1.0, fin_bottom))
    # the slot's ends: close it at FIN_SLOT so the fin locates the brush along the shaft
    ends = [_box(REST_A_X[0], FIN_SLOT[0], yc - FIN["x"] - 1.0, yc + FIN["x"] + 1.0, fin_bottom, z_axis - SHAFT_R - 4.0),
            _box(FIN_SLOT[1], REST_A_X[1], yc - FIN["x"] - 1.0, yc + FIN["x"] + 1.0, fin_bottom, z_axis - SHAFT_R - 4.0)]
    for e in ends:
        a = a.merge(e)
    b = _v_block(*REST_B_X, yc, top, z_axis)
    return {"atc brush rest A (V + fin slot)": (a, STAND), "atc brush rest B (V)": (b, STAND)}


def head_slot_local(k: int, top: float) -> np.ndarray:
    """The pose (4x4, MiR-local) of a head in pocket k: 0 the pocket in line with the rest, 1, 2 up the magazine."""
    Mx = rest_pose_local(top)
    return np.array([[1, 0, 0, 0], [0, 1, 0, -POCKET_PITCH * k], [0, 0, 1, 0], [0, 0, 0, 1]], float) @ Mx


def rest_pose_local(top: float, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> np.ndarray:
    """The brush's TCP frame on its rest (MiR-local), moved dx, dy, dz."""
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = (0, 1, 0), (1, 0, 0), (0, 0, -1)
    Mx[:3, 3] = (REST[0] + dx, REST[1] + dy, top + REST_DZ + dz)
    return Mx


def strip_pose_local(top: float, dx: float = 0.0, dz: float = 0.0) -> np.ndarray:
    """The brush's TCP frame over the stripper (MiR-local), moved dx along the shaft and dz up."""
    Mx = rest_pose_local(top)
    Mx[:3, 3] = (STRIP[0] + dx, STRIP[1], top + STRIP[2] + dz)
    return Mx


def station_meshes(top: float) -> dict:
    """{name: (mesh, colour)}: the pocket and the spring-fed magazine (at the brush's head end), and the grounded waste
    can with its stripper bar, MiR-local. The pocket holds the head as it sits on the resting brush."""
    lo, hi = head_extent_tool()
    x_r, y_r = REST
    # the head at rest in local coordinates: x = x_r + ty, y = y_r + tx, z = z_r - tz
    hx = (x_r + lo[1], x_r + hi[1])                       # 328 .. 390
    hy = (y_r + lo[0], y_r + hi[0])                       # -230 .. -179
    floor_z = top + REST_DZ - BLOCK["z"][1]               # the heads stand on it: their block's lower end
    y_far = y_r - 2 * POCKET_PITCH + lo[0] - 26.0          # the magazine's back end, behind the spring
    out = {}
    floor = _box(hx[0] - 4.0, hx[1] + 7.0, y_far, hy[1] + 7.0, top, floor_z)
    wall_y = _box(hx[0] - 4.0, hx[1] + 7.0, hy[1] + 1.0, hy[1] + 7.0, floor_z, floor_z + 41.0)   # the pocket's stop
    wall_x = _box(hx[1] + 1.0, hx[1] + 7.0, y_far, hy[1] + 7.0, floor_z, floor_z + 41.0)
    # the magazine's -x wall stops short of the pocket, which is open towards the spigot
    wall_mx = _box(hx[0] - 8.0, hx[0] - 2.0, y_far, hy[0] - 4.0, floor_z, floor_z + 31.0)
    out["atc head magazine (ours)"] = (floor.merge(wall_y).merge(wall_x).merge(wall_mx), STAND)
    # the grounded waste can, hung over the cabinet's +x end, with the stripper bar across its mouth
    cx, cy = CAN_C
    out["atc head waste can (ours)"] = (_can_wall(cx, cy, top), CAN)
    z0, z1 = top + CAN_H, top + STRIP[2] + 25.0
    zs = top + STRIP[2] - SHAFT_R - 1.0                    # the slot's bottom: 1 mm under the shaft
    sy = STRIP[1]
    bar = _box(*BAR_X, cy - CAN_R, sy - SLOT_W / 2, z0, z1).merge(
        _box(*BAR_X, sy + SLOT_W / 2, cy + CAN_R, z0, z1)).merge(
        _box(*BAR_X, sy - SLOT_W / 2, sy + SLOT_W / 2, z0, zs))
    out["atc head stripper bar (ours)"] = (bar, OURS)
    strap = pv.Cylinder(center=(cx - CAN_R - 2.0, cy + 30.0, top + 30.0), direction=(0, 0, 1), radius=2.5, height=60.0,
                        resolution=12).triangulate()
    out["atc head can ground strap"] = (strap, GN_YE)
    return out


def _can_wall(cx, cy, top) -> pv.PolyData:
    wall = pv.Cylinder(center=(cx, cy, top + CAN_H / 2), direction=(0, 0, 1), radius=CAN_R, height=CAN_H,
                       resolution=48, capping=False).triangulate()
    wall_in = pv.Cylinder(center=(cx, cy, top + CAN_H / 2 + 1.5), direction=(0, 0, 1), radius=CAN_R - 1.5,
                          height=CAN_H - 3.0, resolution=48, capping=False).triangulate()
    bottom = pv.Disc(center=(cx, cy, top + 1.5), inner=0.0, outer=CAN_R, normal=(0, 0, 1), c_res=48).triangulate()
    return wall.merge(wall_in).merge(bottom)


def spring_meshes(top: float) -> tuple[dict, dict]:
    """The magazine's pusher: ({name: (mesh, colour)} that move, a plate on a gas spring's rod, 1 mm behind the last
    head's bristles; {name: (mesh, colour)} that stay, the spring's body, an open tube on a bracket), MiR-local. The
    pusher moves one POCKET_PITCH towards the pocket for each head taken. Rigid parts only."""
    lo, hi = head_extent_tool()
    x_r, y_r = REST
    hx = (x_r + lo[1], x_r + hi[1])
    floor_z = top + REST_DZ - BLOCK["z"][1]
    y_plate = y_r - 2 * POCKET_PITCH + lo[0] - 1.0        # its face: 1 mm behind the last head's bristle tips
    xc, zc = (hx[0] + hx[1]) / 2, floor_z + 31.0
    plate = _box(hx[0] + 2.0, hx[1] - 2.0, y_plate - 6.0, y_plate, floor_z + 6.0, floor_z + 56.0)
    rod = _cyl_y(4.0, y_plate - 66.0, y_plate - 6.0, x=xc, z=zc, res=16)
    body = pv.Cylinder(center=(xc, y_plate - 40.0, zc), direction=(0, 1, 0), radius=8.0, height=60.0,
                       resolution=20, capping=False).triangulate()        # y_plate - 70 .. - 10, open at both ends:
    #                                                                       the rod's end stays 4 mm in after 52 mm
    return ({"atc head pusher": (plate.merge(rod), OURS)}, {"atc head spring body": (body, SPRING)})


def bom() -> list[dict]:
    """The brush's parts as a list for the clip's notes (all ours, sizes as drawn)."""
    return [dict(part="grip block", size="18 x 18 x 30 mm, between two 37 mm collars", note="ours: form-fit for the 2F-85"),
            dict(part="shaft", size="18 mm stainless, 640 mm grip to spigot", note="ours: conductive, bonded via the arm"),
            dict(part="spigot and detent", size="12 x 20 mm, spring ball detent", note=f"ours: ~{DETENT_N:.0f} N hold, assumed"),
            dict(part="head (disposable)", size="22 mm ferrule, 64 x 40 mm block, 30 mm conductive bristles",
                 note="ours: one per run; not a catalogue part"),
            dict(part="rest", size="two V-blocks, one with a fin slot", note="ours"),
            dict(part="magazine and pocket", size="three heads, spring-fed", note="ours"),
            dict(part="waste can and stripper bar", size="90 x 110 mm can, bonded to the MiR", note="ours")]

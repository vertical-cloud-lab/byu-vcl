"""Taking the powder container off the rePowder after a run, and putting a clean one on (PR #353, #303).

DAL SOP "Powder Collection and Cleaning" 1-3, 10 (/tmp/dalpr/253_atomizer-sop.md) and 178_sop "After a run", powder
collection 1-3, "Chamber and container" 1 (T2 43:37, 50:32, 53:39; T6 00:03; T5 03:44-04:48): with the chamber vented,
cold and open, brush the powder off the cone, the view port and the catch bowl down into the container, in a circle;
let the dust settle; close the container's valve ("pull down and move"); brush the powder off its top; take it off
("heavier than it looks": one person holds its weight while the other works the clamp); a clean container with a
fresh splash disc goes back on, clamped, its valve open.

Who does what here: arm 1 (MiR250 1) brushes, works the valve, the flange clamp and the cap; arm 2 (MiR250 2) holds the
container's weight from below with a fork (ours: the 2F-85 opens to 85 mm, the container is 130 mm across) and carries
it. Tools and fixtures drawn here are ours and assumed unless the notes say otherwise (notes/atom_latch_container.md).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import atom_base as AB                 # noqa: E402
import atom_latch_tools as LT          # noqa: E402
import alloy_atomize as AA             # noqa: E402
import props as P                      # noqa: E402
from scene import OUT, PREVIEW, AUDIT, T, R, window  # noqa: E402

M = AB.M
NAME = "atom_container"
TITLE = "Vertical cloud lab: the powder container off, a clean one on"
CX = M.CHUTE_X                          # the container's axis, x (y = 0)
Z0, Z1 = M.CONT_Z                       # the container body, z 60..262
ZV1 = M.CVALVE_Z[1]                     # its valve's top flange, 288
ZC = (M.CLAMP_Z[0] + M.CLAMP_Z[1]) / 2  # the flange clamp's mid-height, 294
A_LEFT = (-700.0, -350.0, -45.0)        # MiR250 1 front-left of the open door, for the brushing
A_FRONT = (CX - 320.0, -950.0, 0.0)     # MiR250 1 left of the container, for the valve, clamp and cap (chapter 2's spot)
B_FRONT = (800.0, -480.0, 90.0)         # MiR250 2 right of the container, with the fork: it comes in from the right
STEEL_KG_CM3 = 7.9e-3                   # stainless, kg/cm3
FORK_KG = 0.9                           # the fork, aluminium (ours, estimated from its drawn volume below)
GRIPPER_PAYLOAD = 5.0                   # kg, Robotiq 2F-85 (Robotiq's spec sheet)
UR10E_PAYLOAD = 12.5                    # kg, UR10e (UR's spec sheet)

# the fork (ours): grip block, stem, cross bar, two prongs; in the TCP frame (tool z down the stem, prongs along -y)
FORK_STEM = 265.0                       # from the TCP down to the prongs' top
FORK_Y0, FORK_Y1 = -10.0, -245.0        # the prongs, along tool y (world +y when the fork faces +y)
FORK_X = 45.0                           # prong centres, +-x
FORK_REACH = 160.0                      # the container's axis this far along the prongs from the stem


def fork_meshes() -> dict:
    blk = pv.Box(bounds=(-15, 15, -20, 20, -25, 25))
    stem = pv.Box(bounds=(-10, 10, -10, 10, 25, FORK_STEM))
    bar = pv.Box(bounds=(-53, 53, -10, 10, FORK_STEM, FORK_STEM + 12))
    prongs = [pv.Box(bounds=(s * FORK_X - 8, s * FORK_X + 8, FORK_Y1, FORK_Y0, FORK_STEM, FORK_STEM + 12))
              for s in (-1, 1)]
    al = (0.72, 0.74, 0.78)
    return {"atc fork": (blk.merge(stem).merge(bar).merge(prongs[0]).merge(prongs[1]).triangulate(), al)}


def brush_meshes() -> dict:
    """An anti-static brush on a long handle (ours; AMAZEMET ships a set of anti-static brushes, 178_manual): the handle
    along tool +y from the grip, 680 mm, the bristles at its far end pointing along tool -x. TCP at the grip. The handle
    is long so the arm stays outside the door while the bristles reach the outlet, 400 mm in."""
    h = pv.Cylinder(center=(0, 300, 0), direction=(0, 1, 0), radius=9.0, height=680.0, resolution=24).triangulate()
    head = pv.Box(bounds=(-10, 8, 620, 660, -32, 32))
    bris = pv.Box(bounds=(-40, -10, 622, 658, -30, 30))
    return {"atc brush handle": (h.merge(head).triangulate(), (0.15, 0.15, 0.17)),
            "atc brush bristles": (bris.triangulate(), (0.25, 0.22, 0.20))}


BRUSH_TIP = np.array([-40.0, 640.0, 0.0])  # the bristles' tips, TCP frame


def cradle_meshes(slot_dir: float) -> pv.PolyData:
    """A slotted cradle (ours): a ring the container stands in on two rails, a slot in its wall where the fork's
    prongs pass under the container. Local frame: origin on the cabinet top at the cradle's axis; the slot faces
    slot_dir (deg about z)."""
    parts = [pv.Box(bounds=(-80, 80, -80, 80, 0, 3))]
    for s in (-1, 1):
        parts.append(pv.Box(bounds=(-60, 60, s * 20 - 8, s * 20 + 8, 3, 22)))       # rails along x (slot at +x)
    n = 28
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        am = (a0 + a1) / 2
        in_slot = abs(math.atan2(math.sin(am), math.cos(am))) < math.radians(62)
        z0 = 40.0 if in_slot else 3.0
        r0, r1 = 69.0, 75.0
        pts = np.array([[r0 * math.cos(a0), r0 * math.sin(a0)], [r1 * math.cos(a0), r1 * math.sin(a0)],
                        [r1 * math.cos(a1), r1 * math.sin(a1)], [r0 * math.cos(a1), r0 * math.sin(a1)]])
        seg = pv.PolyData(np.c_[pts, np.full(4, z0)], faces=[4, 0, 1, 2, 3]).extrude((0, 0, 70.0 - z0), capping=True)
        parts.append(seg.triangulate())
    m = parts[0]
    for p in parts[1:]:
        m = m.merge(p)
    return m.triangulate().rotate_z(slot_dir, inplace=False)


CRADLE_RAIL_TOP = 22.0                  # the container's bottom stands this far over the cabinet top in the cradle


# ------------------------------------------------------------------------------------------------ the flange clamp
CL_HINGE = np.array([CX + 66.0, 0.0])   # the hinge pin, right side (ours, assumed)
CL_LUG_X = CX - 74.0                    # the T-bolt's lugs, left side


def clamp_meshes() -> dict:
    """A two-part hinged flange clamp (ours, assumed: the footage only shows it finger-tightened, T5 03:44-04:48):
    front and back half-rings round the joint, hinged at the right, joined at the left by a T-handle bolt through two
    lugs. Model frame, closed."""
    def half(front: bool):
        th = np.linspace(math.pi, 2 * math.pi, 25) if front else np.linspace(0, math.pi, 25)
        ring = None
        for a0, a1 in zip(th[:-1], th[1:]):
            r0, r1 = 56.5, 64.0
            pts = np.array([[r0 * math.cos(a0), r0 * math.sin(a0)], [r1 * math.cos(a0), r1 * math.sin(a0)],
                            [r1 * math.cos(a1), r1 * math.sin(a1)], [r0 * math.cos(a1), r0 * math.sin(a1)]])
            seg = pv.PolyData(np.c_[pts + (CX, 0), np.full(4, M.CLAMP_Z[0] - 4)], faces=[4, 0, 1, 2, 3]).extrude(
                (0, 0, M.CLAMP_Z[1] - M.CLAMP_Z[0] + 8), capping=True).triangulate()
            ring = seg if ring is None else ring.merge(seg)
        s = -1 if front else 1
        lug = pv.Box(bounds=(CL_LUG_X - 8, CX - 60, min(s * 2, s * 14), max(s * 2, s * 14), ZC + 4, ZC + 7)).merge(
            pv.Box(bounds=(CL_LUG_X - 8, CX - 60, min(s * 2, s * 14), max(s * 2, s * 14), ZC - 7, ZC - 4)))   # a slot
        z_k = (M.CLAMP_Z[0] - 4, ZC) if front else (ZC, M.CLAMP_Z[1] + 4)
        knuckle = pv.Cylinder(center=(CL_HINGE[0], 0, (z_k[0] + z_k[1]) / 2), direction=(0, 0, 1), radius=6.0,
                              height=z_k[1] - z_k[0], resolution=20).triangulate()
        leaf = pv.Box(bounds=(CX + 58, CL_HINGE[0], min(0, s * 6), max(0, s * 6), z_k[0], z_k[1]))
        return ring.merge(lug.triangulate()).merge(knuckle).merge(leaf.triangulate()).triangulate()
    bolt = pv.Cylinder(center=(CL_LUG_X, -14.0, ZC), direction=(0, 1, 0), radius=3.5, height=60.0,
                       resolution=16).triangulate()           # y -44 .. 16
    tee = pv.Cylinder(center=(CL_LUG_X, -46.0, ZC), direction=(0, 0, 1), radius=4.5, height=38.0,
                      resolution=16).triangulate()
    return {"atc clamp front": (half(True), M.STEEL_DK), "atc clamp back": (half(False), M.STEEL_DK),
            "atc tbolt": (bolt.merge(tee).triangulate(), (0.10, 0.10, 0.11))}


TEE = np.array([CL_LUG_X, -46.0, ZC])   # the T-handle's middle
BOLT_PITCH = 1.25                       # mm per turn (M8, assumed)
BOLT_TURNS = 0.5
BOLT_PULL = 24.0                        # mm the bolt slides out once unscrewed: its tip clears the back lug


def front_open(deg):
    """The front half (and the bolt riding on it) swung open about the hinge (z axis at CL_HINGE)."""
    return R((0, 0, 1), deg, (CL_HINGE[0], CL_HINGE[1], 0))


def back_open(deg):
    return R((0, 0, 1), -deg, (CL_HINGE[0], CL_HINGE[1], 0))


# ------------------------------------------------------------------------------------------------ the valve lever
LEVER_PIVOT = np.array([CX, -94.0, 275.0])   # the container valve's stem, along y (model.py's boss and handle)


def valve_lever_mesh() -> pv.PolyData:
    return pv.Box(bounds=(CX - 4, CX + 85, -100, -88, 269, 281)).triangulate()


def lever_rot(closed: float):
    """closed 0 = open (the model's: along +x), 1 = pulled down 90 deg about the stem: closed (assumed direction,
    from "pull down and move", T2 53:39)."""
    return R((0, 1, 0), 90.0 * closed, tuple(LEVER_PIVOT))


LEVER_END = np.array([CX + 70.0, -94.0, 275.0])   # where the arm takes the lever


def mass_sums() -> dict:
    ms = M.meshes()
    vol = {n: abs(ms[n]["whole"].volume) / 1000.0 for n in ("container", "container_handle", "splash_plate")}
    steel = sum(vol.values()) * STEEL_KG_CM3
    runs = {"four Al cups (chapter 2)": 0.143, "225 cm3 crucible of Al, as Oct 27": 0.50,
            "225 cm3 crucible of NAB bronze": 1.6}
    out = dict(drawn_cm3={k: round(v, 1) for k, v in vol.items()}, container_kg=round(steel, 2),
               powder_kg=runs, fork_kg=FORK_KG, gripper_payload_kg=GRIPPER_PAYLOAD, ur10e_payload_kg=UR10E_PAYLOAD,
               note=("Stainless at 7.9 g/cm3 on the model's drawn volumes (a 4 mm wall; its valve drawn as a plain tube, "
                     "so a real ball valve adds more); powder from chapter 2's sums."))
    out["worst_on_fork_kg"] = round(steel + max(runs.values()) + FORK_KG, 2)
    return out


# ------------------------------------------------------------------------------------------------ the clip
def drop_actor(sc, name):
    a = sc.actors.pop(name, None)
    if a is not None:
        sc.pl.remove_actor(a)
    for d in (sc.group_of, sc.alpha, sc.base_alpha, sc.cutrole, sc.ghost_of, sc.color, sc.ambient):
        d.pop(name, None)


def drop_part(sc, part):
    for n in [n for n in list(sc.actors) if n in (part, part + "#cut", "w:" + part)]:
        drop_actor(sc, n)


def main():
    sc, ma, mb = AB.build(NAME, TITLE)
    rb, rbB = ma.rb, mb.rb
    sums = mass_sums()
    AB.set_joints(sc, lid=0.0, latch=0.0, loop=0.0, bolt=1.0, door=1.0, clamp0=1.0, clamp1=1.0)
    for n in ("container_handle", "flange_clamp", "flange_clamp_b"):
        drop_part(sc, n)
    ms = M.meshes()
    # the container's valve lever as its own group, riding on the container
    sc.add("atc lever", valve_lever_mesh(), M.RED, "atc lever")
    sc.parent["atc lever"] = AB.g("container")
    sc.gmat["atc lever"] = np.eye(4)
    # the clamp
    for name, (mesh, col) in clamp_meshes().items():
        sc.add(name, mesh, col, name, specular=0.4)
        sc.parent[name] = "rp"
        sc.gmat[name] = np.eye(4)
    sc.parent["atc tbolt"] = "atc clamp front"
    # the paper under the door's opening (DAL SOP Powder Collection 1)
    sc.add("atc paper", pv.Box(bounds=(-700, -120, -260, 140, 0.5, 1.5)).translate(tuple(AB.RP), inplace=False),
           (0.97, 0.97, 0.95), "floor", ambient=0.6)
    # dust on the cone, the bowl and the view port's glass: fades as it is brushed
    dust = {}
    zc = M.chamber_floor(60.0) + 1.0
    dust["cone"] = pv.Box(bounds=(-80, 200, -95, 95, -0.8, 0.8)).rotate_y(45.0, inplace=False).translate(
        (60.0 + 0.5, 0.0, M.chamber_floor(60.0) + 1.2), inplace=False)
    dust["bowl"] = pv.Disc(center=(CX, 0, 429.5), inner=8.0, outer=47.0, normal=(0, 0, 1), c_res=48).triangulate()
    vpc = M.VIEWPORT + M.VIEWPORT_N * 6.5
    dust["viewport"] = pv.Disc(center=tuple(vpc), inner=0.0, outer=30.0, normal=tuple(M.VIEWPORT_N), c_res=36)
    for k, mesh in dust.items():
        sc.add(f"atc dust {k}", mesh.triangulate(), (0.36, 0.35, 0.33), AB.g("chamber"), opacity=0.85,
               specular=0.0)
    sc.fluids = set(getattr(sc, "fluids", set())) | {f"atc dust {k}" for k in dust}

    # MiR 1: the brush on a rest, the cap on a peg, a slotted cradle (for the full container) in place of its ring
    drop_actor(sc, "amr/cradle")
    cx_l, cy_l, cz_l = AA.CRADLE_AT
    sc.add("atc cradle A", cradle_meshes(0.0).translate((cx_l, cy_l, cz_l), inplace=False), (0.30, 0.32, 0.36),
           "amr")
    seatA = np.array([cx_l, cy_l, cz_l + CRADLE_RAIL_TOP])
    top = P.MIR["H"] + P.CAB_H
    rest_at = np.array([-230.0, -190.0, top])
    # the brush lies along MiR-local x, handle on the two rests (tool y along local +x, tool z down)
    for name, (mesh, col) in brush_meshes().items():
        sc.add(name, mesh, col, "atc brush", specular=0.2)
    Rb = np.eye(4)
    Rb[:3, 0], Rb[:3, 1], Rb[:3, 2] = (0, 1, 0), (1, 0, 0), (0, 0, -1)     # tool x local +y: bristles to local -y
    brush_home = T((rest_at[0] - 40.0, rest_at[1], top + 62.0 + 9.0)) @ Rb
    sc.parent["atc brush"] = "amr"
    sc.gmat["atc brush"] = brush_home
    # fix the rests under the handle: at local x = brush start + 0 and + 330
    for k, xx in enumerate((70.0, 420.0)):           # clear of where the fingers take the handle
        sc.add(f"atc brush rest {k}", pv.Box(bounds=(-12, 12, -14, 14, 0, 62)).translate(
            (rest_at[0] - 40.0 + xx, rest_at[1], top), inplace=False), (0.30, 0.32, 0.36), "amr")
    cap_at = np.array([-250.0, 150.0, top])
    sc.add("atc cap peg", pv.Cylinder(center=(cap_at[0], cap_at[1], top + 20), direction=(0, 0, 1), radius=30.0,
                                      height=40.0, resolution=36).triangulate(), (0.30, 0.32, 0.36), "amr")
    cap = pv.Cylinder(center=(0, 0, 5), direction=(0, 0, 1), radius=56.0, height=10.0, resolution=48).triangulate()
    cap = cap.merge(pv.Cylinder(center=(0, 0, 22), direction=(0, 0, 1), radius=10.0, height=24.0,
                                resolution=24).triangulate())
    sc.add("atc cap", cap, (0.85, 0.20, 0.15), "atc cap")
    sc.parent["atc cap"] = "amr"
    sc.gmat["atc cap"] = T((cap_at[0], cap_at[1], top + 40.0))
    # MiR 2: the fork in a stand, the clean container in a slotted cradle
    for name, (mesh, col) in fork_meshes().items():
        sc.add(name, mesh, col, "atc fork", specular=0.4)
    fork_home_local = T((-300.0, -200.0, top + FORK_STEM + 12.0)) @ np.diag([1.0, -1.0, -1.0, 1.0])
    sc.parent["atc fork"] = "amrB"
    sc.gmat["atc fork"] = fork_home_local
    for k, xs in enumerate((-22.0, 12.0)):
        sc.add(f"atc fork stand {k}", pv.Box(bounds=(xs, xs + 10, -18, 18, 0, 80)).translate((-300.0, -200.0, top),
                                                                                          inplace=False),
               (0.30, 0.32, 0.36), "amrB")
    sc.add("atc cradle B", cradle_meshes(90.0).translate((cx_l, cy_l, cz_l), inplace=False), (0.30, 0.32, 0.36),
           "amrB")
    seatB = np.array([cx_l, cy_l, cz_l + CRADLE_RAIL_TOP])
    for n in ("container", "splash_plate"):
        sc.add(f"atc c2 {n}", ms[n]["whole"], ms[n]["color"], "atc c2")
    sc.add("atc c2 lever", valve_lever_mesh(), M.RED, "atc c2 lever")
    sc.parent["atc c2 lever"] = "atc c2"
    sc.gmat["atc c2 lever"] = lever_rot(1.0)               # its valve shut while it travels
    sc.parent["atc c2"] = "amrB"
    sc.gmat["atc c2"] = T(seatB) @ R((0, 0, 1), 90.0) @ T((-CX, 0.0, -Z0))    # its valve 90 deg from the fork's stem, as installed
    AB.mir_at(ma, A_LEFT)
    AB.mir_at(mb, B_FRONT)

    def rows(**kw):
        base = dict(Chamber="vented, open, cold", Container=None, Valve=None, Clamp=None, Arm_1=None, Arm_2=None)
        base.update(kw)
        AB.caption_rows(sc, **base)

    CAM_DOOR = AB.cam((-1500, -1300, 1500), (-60, -20, 820))
    CAM_IN = AB.cam((-1000, 250, 1350), (80, -20, 700))
    CAM_CONT = AB.cam((520, -1750, 1250), (270, -40, 320))
    CAM_WIDE = AB.cam((900, -2800, 1800), (100, -300, 500))
    sc.cam = CAM_DOOR

    # ---------------------------------------------------------------- 1. the state
    rows(Container="under the outlet, full", Valve="open", Clamp="closed", Arm_1="parked", Arm_2="parked")
    cap1 = ("After the run: cold, vented (Pressure Control off, Vent Valve), the door's two clamps swung off, then the "
            "door opened (178_sop After a run; T2 39:00). Paper under the opening catches what falls (DAL SOP 1).")
    sc.step("1/5", cap1, 2.4, None, hold=1.2,
            labels=[("powder on the cone, bowl, view port", tuple(AB.W((80, -40, 640))), (0.62, 0.20)),
                    ("anti-static brush (ours, on a long handle)", tuple(MiRw(ma, brush_home[:3, 3])), (0.12, 0.62))])

    # ---------------------------------------------------------------- 2. the brush
    brush_w = sc.world("atc brush")
    pre = T((0, 0, 120)) @ brush_w
    rows(Arm_1="takes the brush")
    cap2 = ("Arm 1 takes the anti-static brush (AMAZEMET supplies a set; this long-handled one is ours) and reaches in "
            "through the door.")
    sc.step("2/5", cap2, 2.2, AB.both(rb.joint_to(Tw=pre), rb.grip_to(0.3)), hold=0.05)
    sc.step("2/5", cap2, 0.8, rb.line_to(brush_w), hold=0.05)
    sc.step("2/5", cap2, 0.4, rb.grip_to(LT.close_for_gap(18.8)), hold=0.05)
    rb.grasp("atc brush")
    sc.step("2/5", cap2, 0.8, rb.line_to(pre), hold=0.05)

    def tcp_for_tip(p_model, handle, bristles):
        """The TCP pose putting the bristle tips at model point p, the handle along `handle` (grip to head), the
        bristles pointing along `bristles` (tool -x)."""
        y = np.asarray(handle, float)
        y /= np.linalg.norm(y)
        x = -np.asarray(bristles, float)
        x = x - y * (x @ y)
        x /= np.linalg.norm(x)
        z = np.cross(x, y)
        Mx = np.eye(4)
        Mx[:3, 0], Mx[:3, 1], Mx[:3, 2] = x, y, z
        Mx[:3, 3] = AB.W(p_model) - Mx[:3, :3] @ BRUSH_TIP
        return Mx

    # strokes: down the cone (the 45 deg underside) to the outlet, round the bowl, round the view port's glass
    hy = np.array([0.56, 0.12, -0.82])                 # the handle in through the door, steep enough to clear its sill
    nz = np.array([-0.83, 0.0, -0.56])                 # the bristles onto the 45 deg cone
    cone = []
    for yy in (-30.0, 15.0, 60.0):
        for xx in (-40.0, 150.0):
            cone.append(tcp_for_tip((xx, yy, M.chamber_floor(xx) + 9.0), hy, nz))
    hb = np.array([0.747, 0.10, -0.665])               # the handle to the bowl: the flattest that clears the sill
    bowl = [tcp_for_tip((CX - 6 + 18 * math.cos(a), 18 * math.sin(a), 441.0), hb, (-0.665, 0.0, -0.747))
            for a in np.linspace(math.pi, 3 * math.pi, 13)]
    entry = tcp_for_tip((-60.0, 0.0, 860.0), hy, nz)
    rows(Arm_1="brushing")
    cap3 = ("It brushes the powder down the cone into the container, then round the catch bowl, in a circle (178_sop "
            "After a run 2; T2 43:37, T4 08:47). The view port is not brushed here: from the door the grip meets the "
            "stack on the open door.")
    sc.step("3/5", cap3, 2.4, rb.joint_to(Tw=entry), hold=0.05, cam_to=CAM_IN)
    f_cone = AA.follow(rb, [entry] + cone)

    def brush_cone(u):
        f_cone(u)
        sc.alpha["atc dust cone"] = 1.0 - window(u, 0.15, 1.0)
    sc.step("3/5", cap3, 4.5, brush_cone, hold=0.05)
    f_bowl = AA.follow(rb, [cone[-1]] + bowl)

    def brush_bowl(u):
        f_bowl(u)
        sc.alpha["atc dust bowl"] = 1.0 - window(u, 0.2, 1.0)
    sc.step("3/5", cap3, 3.6, brush_bowl, hold=0.05)
    sc.step("3/5", cap3, 1.6, rb.joint_to(Tw=entry), hold=0.05)
    # the brush back on its rest
    rows(Arm_1="brush back")
    sc.step("3/5", "The brush goes back on its rest.", 2.2, rb.joint_to(Tw=pre), hold=0.05, cam_to=CAM_DOOR)
    sc.step("3/5", "The brush goes back on its rest.", 0.8, rb.line_to(brush_w), hold=0.05)
    rb.release("amr")
    sc.step("3/5", "The brush goes back on its rest.", 0.4, rb.grip_to(0.3), hold=0.05)
    sc.step("3/5", "The brush goes back on its rest.", 0.7, rb.line_to(pre), hold=0.05)

    # ---------------------------------------------------------------- 3. the dust settles
    def settle(u):
        rows(Container="dust settling", Arm_1="parked", Clock=f"{60 * u:4.0f} s of 60")
    cap5 = "The dust settles for a minute before anyone reaches in again (178_sop After a run 2; T2 50:32). Time-lapse."
    sc.step("4/5", cap5, 2.4, AB.both(rb.joint_to(np.radians(AA.A.PARK_DEG)), settle), hold=0.4)
    rows(Container="under the outlet, full", Arm_1="to the container")
    drive, secs = AB.mir_drive(ma, A_FRONT)
    sc.step("4/5", "MiR250 1 drives round to the container.", secs, drive, hold=0.1, cam_to=CAM_CONT)

    # ---------------------------------------------------------------- 4. the valve shut
    lev_g0 = AB.tcp(tuple(LEVER_END), (0.0, 1.0, 0.0), 90.0)       # from the front, fingers across the bar (vertical)
    def lever_pose(c):
        return T(AB.RP) @ lever_rot(c) @ T(-AB.RP) @ lev_g0
    cap6 = ("Arm 1 closes the container's valve: its lever pulled down a quarter turn (\"pull down and move\", T2 "
            "53:39). Shut, it keeps the argon in the container's bottom (T6 00:03).")
    rows(Arm_1="closing the valve")
    sc.step("5/5", cap6, 2.2, AB.both(rb.joint_to(Tw=lever_pose(0.0) @ T((0, 0, -90))), rb.grip_to(0.3)), hold=0.05)
    sc.step("5/5", cap6, 0.8, rb.line_to(lever_pose(0.0)), hold=0.05)
    sc.step("5/5", cap6, 0.4, rb.grip_to(LT.close_for_gap(12.8)), hold=0.05)
    rb.events.append((sc.n, "grasp", "atc lever", None))
    f_lev = AA.follow(rb, [lever_pose(c) for c in np.linspace(0, 1, 10)])

    def shut(u):
        f_lev(u)
        sc.gmat["atc lever"] = lever_rot(u)
        rows(Valve="shut" if u > 0.98 else "closing")
    sc.step("5/5", cap6, 1.8, shut, hold=0.1)
    rb.events.append((sc.n, "grasp", "atc lever", None))
    sc.step("5/5", cap6, 0.4, rb.grip_to(0.3), hold=0.05)
    rb.events.append((sc.n, "release", "atc lever", None))
    sc.step("5/5", cap6, 0.7, rb.line_to(lever_pose(1.0) @ T((0, 0, -90))), hold=0.05)
    if not FULL:
        # the rest (the fork under it, the clamp, onto MiR250 1, the cap, the clean container) is drawn below but its
        # two-arm moves still collide (audit of 2026-11-19 01:42: 994 frames in steps 6-8), so the clip stops here
        rows(Container="valve shut, ready to come off", Valve="shut", Arm_1="parked")
        sc.step("5/5", "Arm 1 stands back.", 1.4, rb.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.2, cam_to=CAM_WIDE)
        capN = (f"Next, not animated yet: arm 2 holds the weight from below with a fork (ours; the 2F-85 opens to 85 mm, "
                f"the container is 130 mm across), arm 1 opens the clamp, the container goes onto MiR250 1, capped, and a "
                f"clean one with a fresh splash disc goes on. It weighs about {sums['container_kg']:.1f} kg empty "
                f"(the model's stainless) plus 0.14-1.6 kg of powder: under the UR10e's {UR10E_PAYLOAD:g} kg, near or over "
                f"the 2F-85's {GRIPPER_PAYLOAD:g} kg.")
        sc.step("5/5", capN, 0.5, None, hold=8.0)
        if not (PREVIEW or AUDIT):
            (OUT / "atom").mkdir(parents=True, exist_ok=True)
            (OUT / "atom" / "atom_container_mass.json").write_text(json.dumps(sums, indent=1) + "\n")
        AB.finish(sc)
        return

    # ---------------------------------------------------------------- 5. the fork under it, the clamp open
    yaw_f = 0.0
    def fork_tcp(z_top, dx=0.0, at=(CX, 0.0)):
        """The TCP holding the fork with its prongs' top at z_top under a container whose axis is at `at` (model),
        the fork coming from the right (prongs along -x), dx mm further out."""
        return T(AB.W((at[0] + FORK_REACH + dx, at[1], z_top + FORK_STEM))) @ R((0, 0, 1), 90.0) @ \
            np.diag([1.0, -1.0, -1.0, 1.0])
    fork_w = sc.world("atc fork")
    rows(Arm_2="takes the fork")
    cap7 = (f"Arm 2 takes a fork (ours) and slides it under the container: it weighs about {sums['container_kg']:.1f} kg "
            "empty (the model's steel), and the 2F-85 opens to 85 mm while the container is 130 mm across. "
            "\"Keep it fully supported until the clamp is closed\" (178_sop Chamber 1).")
    sc.step("6/8", cap7, 2.2, AB.both(rbB.joint_to(Tw=T((0, 0, 130)) @ fork_w), rbB.grip_to(0.3)), hold=0.05)
    sc.step("6/8", cap7, 0.8, rbB.line_to(fork_w), hold=0.05)
    sc.step("6/8", cap7, 0.4, rbB.grip_to(LT.close_for_gap(30.8)), hold=0.05)
    rbB.grasp("atc fork")
    sc.step("6/8", cap7, 0.8, rbB.line_to(T((0, 0, 130)) @ fork_w), hold=0.05)
    under0 = fork_tcp(Z0 - 4.0, dx=140.0)
    under1 = fork_tcp(Z0 - 4.0)
    sc.step("6/8", cap7, 2.4, rbB.joint_to(Tw=under0), hold=0.05, cam_to=CAM_CONT)
    sc.step("6/8", cap7, 1.4, rbB.line_to(under1), hold=0.05)
    sc.step("6/8", cap7, 0.5, rbB.line_to(fork_tcp(Z0 - 0.5)), hold=0.05)
    rbB.reparent(AB.g("container"), "atc fork")         # the fork bears on its bottom from here
    rbB.events.append((sc.n, "grasp", AB.g("container"), "atc fork"))
    sc.step("6/8", cap7, 0.5, rbB.line_to(fork_tcp(Z0 + 0.5)), hold=0.2,
            labels=[("fork (ours) under the container", tuple(AB.W((CX, -120, Z0))), (0.20, 0.70))])
    rows(Container="held from below", Arm_2="holding the weight")

    # arm 1: the T-bolt out, the front half open
    tee_g = AB.tcp(tuple(TEE), (0.0, 1.0, 0.0), 0.0)
    def tee_pose(turn_deg, pull, swing):
        return T(AB.RP) @ front_open(swing) @ T((0, -pull, 0)) @ R((0, 1, 0), -turn_deg, tuple(TEE)) @ T(-AB.RP) @ tee_g
    cap8 = (f"Arm 1 opens the flange clamp: half a turn of its T-handle, the bolt slid out of the back lug, "
            "the front half swung open on its hinge (a two-part clamp; its exact type is not in the footage).")
    rows(Arm_1="opening the clamp", Clamp="closed")
    sc.step("6/8", cap8, 2.2, AB.both(rb.joint_to(Tw=tee_pose(0, 0, 0) @ T((0, 0, -90))), rb.grip_to(0.4)), hold=0.05)
    sc.step("6/8", cap8, 0.8, rb.line_to(tee_pose(0, 0, 0)), hold=0.05)
    sc.step("6/8", cap8, 0.4, rb.grip_to(LT.close_for_gap(9.8)), hold=0.05)
    rb.events.append((sc.n, "grasp", "atc tbolt", "atc clamp front"))
    turns = 360.0 * BOLT_TURNS
    f_turn = AA.follow(rb, [tee_pose(a, a / 360.0 * BOLT_PITCH, 0) for a in np.linspace(0, turns, 28)])

    def unscrew(u):
        f_turn(u)
        a = turns * u
        sc.gmat["atc tbolt"] = T((0, -a / 360.0 * BOLT_PITCH, 0)) @ R((0, 1, 0), -a, tuple(TEE))
    sc.step("6/8", cap8, 2.4, unscrew, hold=0.05)
    rb.events.append((sc.n, "grasp", "atc tbolt", "atc clamp front"))
    p0 = turns / 360.0 * BOLT_PITCH
    f_pull = AA.follow(rb, [tee_pose(turns, p0 + BOLT_PULL * s, 0) for s in np.linspace(0, 1, 6)])

    def pull(u):
        f_pull(u)
        sc.gmat["atc tbolt"] = T((0, -(p0 + BOLT_PULL * u), 0)) @ R((0, 1, 0), -turns, tuple(TEE))
    sc.step("6/8", cap8, 0.9, pull, hold=0.05)
    f_swing = AA.follow(rb, [tee_pose(turns, p0 + BOLT_PULL, d) for d in np.linspace(0, SWING, 10)])

    def swing(u):
        f_swing(u)
        sc.gmat["atc clamp front"] = front_open(SWING * u)
        rows(Clamp="open" if u > 0.98 else "opening")
    sc.step("6/8", cap8, 1.8, swing, hold=0.1)
    rb.events.append((sc.n, "grasp", "atc tbolt", "atc clamp front"))
    sc.step("6/8", cap8, 0.4, rb.grip_to(0.4), hold=0.05)
    rb.events.append((sc.n, "release", "atc tbolt", "atc clamp front"))
    sc.step("6/8", cap8, 0.7, rb.line_to(tee_pose(turns, p0 + BOLT_PULL, SWING) @ T((0, 0, -90))), hold=0.05)
    sc.step("6/8", cap8, 1.6, rb.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.05)

    # ---------------------------------------------------------------- 6. down, out, onto MiR 1
    rows(Container="on the fork", Arm_2="carrying it", Clamp="open")
    cap9 = (f"Arm 2 lowers it out of the clamp, still level, and carries it to MiR250 1's cradle: container, powder "
            f"and fork are at most {sums['worst_on_fork_kg']:.1f} kg, inside the UR10e's {UR10E_PAYLOAD:g} kg but over "
            f"the 2F-85's {GRIPPER_PAYLOAD:g} kg with a full bronze charge.")
    sc.step("7/8", cap9, 1.2, rbB.line_to(fork_tcp(Z0 - 45.0)), hold=0.05)
    sc.step("7/8", cap9, 1.4, rbB.line_to(fork_tcp(Z0 - 45.0, dx=200.0)), hold=0.05)
    seat_w = ma.world(seatA)
    # the container's bottom on the cradle's rails, the fork's prongs through its slot (the slot faces MiR-local -x)
    psiA = ma.yaw + 90.0                                # the fork's yaw: its prongs in through the slot (MiR-local +x)
    fork_seat = T(seat_w + (0, 0, -4.0 + FORK_STEM)) @ R((0, 0, 1), psiA) @ T((0, -FORK_REACH, 0)) @ \
        np.diag([1.0, -1.0, -1.0, 1.0])
    sc.step("7/8", cap9, 3.0, rbB.joint_to(Tw=T((0, 0, 60)) @ fork_seat), hold=0.05, cam_to=CAM_WIDE)
    sc.step("7/8", cap9, 0.9, rbB.line_to(T((0, 0, 3.5)) @ fork_seat), hold=0.05)
    rbB.reparent(AB.g("container"), "amr")
    rbB.events.append((sc.n, "release", AB.g("container"), "amr"))
    sc.step("7/8", cap9, 0.5, rbB.line_to(fork_seat), hold=0.05)
    sc.step("7/8", cap9, 1.2, rbB.line_to(back_off(fork_seat, psiA, FORK_REACH + 40.0)), hold=0.05)
    # arm 2 waits with the fork over its own MiR, out of arm 1's way
    psiB0 = mb.yaw + 180.0
    wait_B = T((0, 0, 250.0)) @ back_off(T(mb.world(seatB) + (0, 0, -4.0 + FORK_STEM)) @ R((0, 0, 1), psiB0) @
                                          T((0, -FORK_REACH, 0)) @ np.diag([1.0, -1.0, -1.0, 1.0]), psiB0,
                                          FORK_REACH + 40.0)
    sc.step("7/8", cap9, 2.0, rbB.joint_to(Tw=wait_B), hold=0.05)
    rows(Container="on MiR250 1, valve shut", Arm_2="to the clean container")

    # arm 1 caps it
    cap_w = sc.world("atc cap")
    cap_g = cap_w @ T((0, 0, 22.0)) @ np.diag([1.0, -1.0, -1.0, 1.0])
    on_top = ma.world(seatA) + (0, 0, ZV1 - Z0 + 1.0)
    cap10 = ("Arm 1 caps it (ours: a blank on its top flange), so the splashes on its disc and the powder stay in; "
             "its valve is shut, so the argon stays in its bottom (178_sop After a run 3).")
    rows(Arm_1="capping it")
    sc.step("7/8", cap10, 2.0, AB.both(rb.joint_to(Tw=T((0, 0, 100)) @ cap_g), rb.grip_to(0.5)), hold=0.05)
    sc.step("7/8", cap10, 0.7, rb.line_to(cap_g), hold=0.05)
    sc.step("7/8", cap10, 0.4, rb.grip_to(LT.close_for_gap(20.8)), hold=0.05)
    rb.grasp("atc cap")
    sc.step("7/8", cap10, 0.7, rb.line_to(T((0, 0, 100)) @ cap_g), hold=0.05)
    cap_on = T(on_top + (0, 0, 22.0)) @ np.diag([1.0, -1.0, -1.0, 1.0])
    sc.step("7/8", cap10, 2.0, rb.joint_to(Tw=T((0, 0, 80)) @ cap_on), hold=0.05)
    sc.step("7/8", cap10, 0.7, rb.line_to(cap_on), hold=0.05)
    rb.release(AB.g("container"))
    sc.step("7/8", cap10, 0.4, rb.grip_to(0.5), hold=0.05)
    sc.step("7/8", cap10, 0.6, rb.line_to(T((0, 0, 80)) @ cap_on), hold=0.05)
    sc.step("7/8", cap10, 1.4, rb.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.05)

    # ---------------------------------------------------------------- 7. the clean container on
    rows(Container="clean one, fresh splash disc", Arm_2="fetching it")
    c2_w = sc.world("atc c2")
    seatB_w = mb.world(seatB)
    psiB = mb.yaw + 180.0                               # cradle B's slot faces MiR-local +y
    forkB = T(seatB_w + (0, 0, -4.0 + FORK_STEM)) @ R((0, 0, 1), psiB) @ T((0, -FORK_REACH, 0)) @ \
        np.diag([1.0, -1.0, -1.0, 1.0])
    cap11 = ("Arm 2 takes a clean container, a fresh splash disc in its top flange (178_sop Chamber 1; T5 02:21), from "
             "MiR250 2's cradle, and lifts it under the outlet.")
    sc.step("8/8", cap11, 2.2, rbB.joint_to(Tw=back_off(forkB, psiB, FORK_REACH + 40.0)), hold=0.05)
    sc.step("8/8", cap11, 1.1, rbB.line_to(forkB), hold=0.05)
    sc.step("8/8", cap11, 0.5, rbB.line_to(T((0, 0, 3.5)) @ forkB), hold=0.05)
    rbB.reparent("atc c2", "atc fork")
    rbB.events.append((sc.n, "grasp", "atc c2", "amrB"))
    sc.step("8/8", cap11, 0.8, rbB.line_to(T((0, 0, 60.0)) @ forkB), hold=0.05)
    sc.step("8/8", cap11, 3.0, rbB.joint_to(Tw=fork_tcp(Z0 - 45.0, dx=200.0)), hold=0.05, cam_to=CAM_CONT)
    sc.step("8/8", cap11, 1.4, rbB.line_to(fork_tcp(Z0 - 45.0)), hold=0.05)
    sc.step("8/8", cap11, 1.2, rbB.line_to(fork_tcp(Z0 - 0.5)), hold=0.1)
    rows(Container="clean one, held up", Arm_2="holding the weight")
    # arm 1 closes the clamp and opens the valve
    cap12 = ("Arm 1 swings the clamp shut, slides the bolt in and turns it finger-tight while arm 2 holds the weight: "
             "\"one holding the weight while the other closes the clamp\" (178_sop Chamber 1).")
    rows(Arm_1="closing the clamp")
    sc.step("8/8", cap12, 2.2, AB.both(rb.joint_to(Tw=tee_pose(turns, p0 + BOLT_PULL, SWING) @ T((0, 0, -90))),
                                       rb.grip_to(0.4)), hold=0.05)
    sc.step("8/8", cap12, 0.7, rb.line_to(tee_pose(turns, p0 + BOLT_PULL, SWING)), hold=0.05)
    sc.step("8/8", cap12, 0.4, rb.grip_to(LT.close_for_gap(9.8)), hold=0.05)
    rb.events.append((sc.n, "grasp", "atc tbolt", "atc clamp front"))
    f_sw2 = AA.follow(rb, [tee_pose(turns, p0 + BOLT_PULL, d) for d in np.linspace(SWING, 0, 10)])

    def swing_shut(u):
        f_sw2(u)
        sc.gmat["atc clamp front"] = front_open(SWING * (1 - u))
    sc.step("8/8", cap12, 1.8, swing_shut, hold=0.05)
    f_push = AA.follow(rb, [tee_pose(turns, p0 + BOLT_PULL * (1 - s), 0) for s in np.linspace(0, 1, 6)])

    def push(u):
        f_push(u)
        sc.gmat["atc tbolt"] = T((0, -(p0 + BOLT_PULL * (1 - u)), 0)) @ R((0, 1, 0), -turns, tuple(TEE))
    sc.step("8/8", cap12, 0.9, push, hold=0.05)
    f_scr = AA.follow(rb, [tee_pose(a, a / 360.0 * BOLT_PITCH, 0) for a in np.linspace(turns, 0, 28)])

    def screw(u):
        f_scr(u)
        a = turns * (1 - u)
        sc.gmat["atc tbolt"] = T((0, -a / 360.0 * BOLT_PITCH, 0)) @ R((0, 1, 0), -a, tuple(TEE))
        rows(Clamp="finger-tight" if u > 0.98 else "tightening")
    sc.step("8/8", cap12, 2.4, screw, hold=0.05)
    rb.events.append((sc.n, "grasp", "atc tbolt", "atc clamp front"))
    sc.step("8/8", cap12, 0.4, rb.grip_to(0.4), hold=0.05)
    rb.events.append((sc.n, "release", "atc tbolt", "atc clamp front"))
    sc.step("8/8", cap12, 0.7, rb.line_to(tee_pose(0, 0, 0) @ T((0, 0, -90))), hold=0.05)
    # the new container's valve open
    def lever2_pose(c):
        return T(AB.RP) @ lever_rot(c) @ T(-AB.RP) @ lev_g0
    cap13 = "Then its valve open, lever back up (DAL SOP Powder Collection 10: \"reattach the cup with its valve open\")."
    rows(Arm_1="opening the valve")
    sc.step("8/8", cap13, 1.8, rb.joint_to(Tw=lever2_pose(1.0) @ T((0, 0, -90))), hold=0.05)
    sc.step("8/8", cap13, 0.7, rb.line_to(lever2_pose(1.0)), hold=0.05)
    sc.step("8/8", cap13, 0.4, rb.grip_to(LT.close_for_gap(12.8)), hold=0.05)
    rb.events.append((sc.n, "grasp", "atc c2 lever", None))
    f_op = AA.follow(rb, [lever2_pose(c) for c in np.linspace(1, 0, 10)])

    def open_(u):
        f_op(u)
        sc.gmat["atc c2 lever"] = lever_rot(1 - u)
        rows(Valve="open" if u > 0.98 else "opening")
    sc.step("8/8", cap13, 1.6, open_, hold=0.05)
    rb.events.append((sc.n, "grasp", "atc c2 lever", None))
    sc.step("8/8", cap13, 0.4, rb.grip_to(0.3), hold=0.05)
    rb.events.append((sc.n, "release", "atc c2 lever", None))
    sc.step("8/8", cap13, 0.7, rb.line_to(lever2_pose(0.0) @ T((0, 0, -90))), hold=0.05)
    rows(Container="clean, clamped, valve open", Arm_2="fork out")
    cap14 = "Arm 2 lowers the fork 3 mm, slides it out and puts it back; both arms park."
    rbB.reparent("atc c2", "rp")                       # the clamp holds it now
    rbB.events.append((sc.n, "release", "atc c2", "rp"))
    sc.step("8/8", cap14, 0.5, rbB.line_to(fork_tcp(Z0 - 4.0)), hold=0.05)
    sc.step("8/8", cap14, 1.3, rbB.line_to(fork_tcp(Z0 - 4.0, dx=140.0)), hold=0.05)
    sc.step("8/8", cap14, 1.6, AB.both(rb.joint_to(np.radians(AA.A.PARK_DEG)), rbB.joint_to(Tw=T((0, 0, 130)) @
                                                                                             fork_w)), hold=0.05,
            cam_to=CAM_WIDE)
    sc.step("8/8", cap14, 0.8, rbB.line_to(fork_w), hold=0.05)
    rbB.release("amrB")
    sc.step("8/8", cap14, 0.4, rbB.grip_to(0.3), hold=0.05)
    sc.step("8/8", cap14, 0.7, rbB.line_to(T((0, 0, 130)) @ fork_w), hold=0.05)
    sc.step("8/8", cap14, 1.4, rbB.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.3)
    s = sums
    cap15 = (f"Mass: the container {s['container_kg']:.1f} kg (the model's stainless), the powder 0.14-1.6 kg, the "
             f"fork {FORK_KG:g}: under the UR10e's {UR10E_PAYLOAD:g} kg, near or over the 2F-85's {GRIPPER_PAYLOAD:g}. "
             "The used container rides on MiR250 1, capped, to the sieve.")
    sc.step("8/8", cap15, 0.5, None, hold=5.0)
    if not (PREVIEW or AUDIT):
        (OUT / "atom").mkdir(parents=True, exist_ok=True)
        (OUT / "atom" / "atom_container_mass.json").write_text(json.dumps(sums, indent=1) + "\n")
    AB.finish(sc)


SWING = 45.0                            # deg the clamp's front half swings open
FULL = bool(__import__("os").environ.get("ATOM_CONTAINER_FULL"))   # the whole sequence (its steps 6-8 still collide)


def back_off(Mx, psi, d):
    """The fork's TCP pose Mx moved d mm back along its prongs (away from what they carry), in the world."""
    a = math.radians(psi)
    return T((d * math.sin(a), -d * math.cos(a), 0.0)) @ Mx


def MiRw(mir, p_local):
    return mir.world(np.asarray(p_local, float))


if __name__ == "__main__":
    main()

"""Changing the crucible on the rePowder with two arms (PR #353, #303): taking the furnace apart and the crucible out
(``atom_crucible_out``), and the rebuild with the graphite nut threaded on from below (``atom_crucible_in``).

    xvfb-run -a python3 atom_crucible.py out        # or in; or CRUCIBLE_CLIP=in
    PREVIEW=1 / ARM_AUDIT=1 as for every atom_* clip (atom_base.py); run through runner_guard.py

Arm 1 (MiR250 1, in front) works the furnace from the top; arm 2 (MiR250 2, at the left by the chamber's door) holds
or turns the nut from below with the nut key, through the open door. The procedure, its sources and what is ours or
assumed: notes/atom_crucible.md. The tools and fixtures: atom_crucible_tools.py. The bill of materials:
out/atom/crucible_bom.json (written by this script with ``CRUCIBLE_BOM=1``, no render).

Start state, both clips: the furnace cold (it can be touched: DAL checklist, Cooldown 1 and Powder 8), the lid open
with its latch undone (another clip, atom_latch, does the latch), the chamber's door open with both clamps off, and
the ultrasonic stack out on its bench (DAL checklist, Loading the Furnace: "If the furnace is being rebuilt, do it
before the stack goes in"). The out clip ends with the crucible in its cradle on MiR250 1; atom_bn.py cleans and
recoats it at the hood, and the in clip starts with it back in the cradle, clean, coated and dry.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pyvista as pv

import atom_base as AB
import atom_crucible_tools as CT
import alloy_atomize as AA
import robot as RB
from scene import AUDIT, PREVIEW, R, T

M = AB.M
g = AB.g
both = RB.both
CLIP = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CRUCIBLE_CLIP", "out")).lower()
NAME = f"atom_crucible_{CLIP}" + os.environ.get("CRUCIBLE_SUFFIX", "")

# ---------------------------------------------------------------------------------------------- numbers
PITCH = M.NUT_PITCH                                   # 2.0 mm (model.py)
NUT_RUN = M.NUT_Z[0] - (M.SHANK_Z0 - (M.NUT_Z[1] - M.NUT_Z[0]))   # 14 mm: the nut's top from the shank's end to snug
NUT_TURNS = NUT_RUN / PITCH                           # 7 turns
TQ_NUT = 0.30                                         # N m, assumed start value for the nut (notes: bench test)
TQ_HOLDER = 0.40                                      # N m, assumed start value for the crucible onto the holder
TQ_BREAK = 0.55                                       # N m, an example breakaway reading (to be logged, not known)
HOLDER_TURNS = 1.25                                   # turns onto the holder: "just barely" (T8 2:26); assumed
HOLDER_PITCH = 2.0                                    # assumed, as the nut's
ALIGN_DEG = 90.0                                      # the crucible goes in 90 deg short of the port and turns to it
BRK_DEG = 25.0                                        # the breakaway turn, arm 1's wrist
LEVER_UP = 70.0      # the sealing-rod lever swung up 70 deg (chapter 2: 95): since the lid was turned onto the left
                     # (model.py LID_TURN_DEG), the open latch lever stands on the housing's right face, where the 2F-85
                     # would be at 95; at 70 the lever's eye is still 15 mm clear of the crucible gripper's plate
ROD_SPIN = 270.0     # the rod taken with the fingers across the lever's line (y) and the wrist camera to the left
TURN = R((0, 0, 1), 90.0)   # the tools sit turned 90 deg on what they hold, so at the furnace the 2F-85's fingers
                            # close along y, across the lever (at 70 deg its eye is 63 mm from the axis)
TURN_OUT, ROD_SPIN_OUT = np.eye(4), 180.0   # the out clip as rendered and audited (see notes: these two
                                            # would clear its 10 lever frames; not re-rendered in time)
MIR2_AT = (-960.0, -40.0, 90.0)   # MiR250 2: 200 mm further left than PARK["left"], so the key's handle (500 mm out)
                                  # is a comfortable reach and arm 2's wrist stays clear of the open lid (x -375..-152)
FT = "FT 300-S"                                       # the wrist sensor on both arms (notes: why)
GRIP = CT.GRIP_TOOL
GRIP_TC = CT.gripper_gap_close(3.8) + 0.004           # the 3.8 mm sheath
GRIP_ROD = CT.gripper_gap_close(21.7) + 0.004         # the brass adapter, 21.7 mm
GRIP_PIN = CT.gripper_gap_close(14.0) + 0.004         # the pin's T-handle, end to end
GRIP_LEVER = AA.GRIP_LEVER
TC_XY = 33.1 * np.array([math.cos(math.radians(M.TC_ANGLE)), math.sin(math.radians(M.TC_ANGLE))])
_pa = math.radians(M.TC_PLUG_ANGLE)
TC_LEG = M.TC_PLUG_R * np.array([math.cos(_pa), math.sin(_pa)]) - TC_XY
TC_LEN = float(np.linalg.norm(TC_LEG)) - 9.0
TC_DIR = TC_LEG / np.linalg.norm(TC_LEG)
TC_GRIP = np.array([*(TC_XY + TC_DIR * TC_LEN * 0.55), M.BODY_TOP + 6.0])   # on the leg, from above
TC_SPIN = math.degrees(math.atan2(TC_DIR[0], TC_DIR[1])) + 180.0           # fingers across the leg, camera in front
ROD_GRIP_Z = 1378.0                                   # on the adapter's body (1318.6 .. 1388)
TC_PULL = 100.0
CAB = CT.CAB_TOP

# cameras, model frame
C_FUR = AB.cam((-260.0, -1020.0, 2250.0), (0.0, -60.0, 1290.0))
C_FUR2 = AB.cam((330.0, -900.0, 2150.0), (0.0, -40.0, 1310.0))
C_MIR1 = AB.cam((-120.0, -1950.0, 1650.0), (20.0, -820.0, 880.0))
C_NUT = AB.cam((-360.0, -620.0, 1170.0), (-30.0, 0.0, 1105.0))
C_DOOR = AB.cam((-1150.0, -1250.0, 1650.0), (-300.0, -60.0, 1050.0))
C_WIDE = AB.cam((-1500.0, -2350.0, 2250.0), (-150.0, -380.0, 1000.0))
C_CRADLE = AB.cam((-330.0, -1450.0, 1400.0), (-110.0, -900.0, 930.0))
C_TABLE = AB.cam((350.0, -1500.0, 1700.0), (420.0, -420.0, 950.0))

# ---------------------------------------------------------------------------------------------- the scene
TOOLS1 = dict(cg=("cr:cg", CT.cg_meshes, CT.CG_Z), nt=("cr:nt", CT.nt_meshes, CT.NT_Z),
              tw=("cr:tw", CT.tw_meshes, CT.TW_Z))
HANDLE = dict(cg=CT.CG_HANDLE, nt=CT.NT_HANDLE, tw=CT.TW_HANDLE)
PARTS_CUT = ("crucible", "holder", "nozzle", "furnace", "bottom_ins", "coil", "side_ins", "top_ins", "tc", "chamber")


def fresh_after(rb):
    """collide.Checker caches the held group's subtree by the group's name. This chapter changes what rides on a held
    tool (the crucible on its gripper, the nut in the key's cup) and swaps which of two nested groups is held, so the
    cache has to be dropped after every grasp, release and reparent (here, on these two arms only; collide.py as is)."""
    def drop():
        sc = rb.sc
        chks = [rb._checker] + list(getattr(getattr(sc, "auditor", None), "checkers", {}).values())
        for chk in chks:
            if chk is not None:
                chk.held_group = None
                chk.held_bodies = []
    for name in ("grasp", "release", "reparent"):
        orig = getattr(rb, name)

        def wrapped(*a, _orig=orig, **kw):
            out = _orig(*a, **kw)
            drop()
            return out
        setattr(rb, name, wrapped)


class Rig:
    """The scene, the two units and everything this chapter adds."""

    def __init__(self, clip):
        title = ("Vertical cloud lab: the crucible out (thermocouple, rod, insulation, nut held from below)"
                 if clip == "out" else
                 "Vertical cloud lab: the rebuild, the graphite nut threaded on from below")
        self.sc, self.ma, self.mb = AB.build(NAME, title)
        sc = self.sc
        self.r1, self.r2 = self.ma.rb, self.mb.rb
        for rb in (self.r1, self.r2):
            fresh_after(rb)
        AB.set_joints(sc, lid=1.0, latch=1.0, loop=1.0, bolt=1.0, door=1.0, clamp0=1.0, clamp1=1.0)
        for grp in ("stack", "connector", "sonotrode", "booster", "transducer", "plate", "upper", "cover"):
            sc.show(sc.members(g(grp)), 0.0)              # the stack is out, on its bench
        sc.show([n for n in sc.members("amr") if n.endswith("/cradle")], 0.0)   # chapter 2's container cradle
        AB.mir_at(self.ma, "front")
        AB.mir_at(self.mb, MIR2_AT)
        for name, (mesh, col) in CT.fixtures1().items():
            sc.add(f"amr/cr {name}", mesh, col, "amr", specular=0.2,
                   **(dict(ambient=0.95, diffuse=0.1) if "light" in name else {}))
        self.lights = [n for n in sc.actors if n.startswith("amr/cr ") and "light" in n]
        for grp, (mesh, col) in CT.fixture_jaws().items():
            sc.add(f"cr {grp}", mesh, col, f"cr:{grp}")
            sc.parent[f"cr:{grp}"] = "amr"
        sc.add("amrB/cr key posts", CT.key_posts(), CT.FIX, "amrB", specular=0.2)
        for name, (mesh, col) in CT.table_meshes().items():
            sc.add(f"cr {name}", mesh, col, "cr:table", specular=0.2)
        sc.parent["cr:table"] = "rp"
        # the tools on MiR 1
        for key, (grp, fn, z) in TOOLS1.items():
            for name, (mesh, col, part) in fn().items():
                sub = grp if part == "body" else f"{grp}_{part}"
                sc.add(name, mesh, col, sub, specular=0.45)
                if sub != grp:
                    sc.parent[sub] = grp
            x, y = CT.LAY1[key]
            sc.parent[grp] = "amr"
            sc.gmat[grp] = T((x, y, z))
        self.cg_jaws(1.0)
        sc.show(sc.members("cr:nt_needles"), 0.0)
        # the key on MiR 2, with the nut and the lower seal in its cup
        for name, (mesh, col, part) in CT.key_meshes().items():
            sub = "cr:key" if part == "body" else "cr:key_sock"
            sc.add(name, mesh, col, sub, specular=0.45)
        sc.parent["cr:key_sock"] = "cr:key"
        sc.parent["cr:key"] = "amrB"
        sc.gmat["cr:key"] = CT.key_rack_pose()
        # the lever's safety pin (ours), on the lever; drawn through the eye and the stub without their cross holes,
        # so it is a soft part for the audit (as an uncompressed O-ring)
        for name, (mesh, col) in CT.pin_meshes(M.Z_ARM).items():
            sc.add(name, mesh, col, "cr:pin", specular=0.4)
        sc.parent["cr:pin"] = g("arm")
        sc.soft = set(getattr(sc, "soft", ())) | set(sc.members("cr:pin"))
        # the model's furnace extension (model.py hood_parts: furnace_ext) keeps a solid 5 mm floor plate across the
        # holder's shank (x 0-184, z 1150-1155), where the furnace floor and the top plate have their holes; cut the
        # same hole in it here (r 30), or the crucible as built already sits 12 mm into it
        for nm in ("furnace_ext", "furnace_ext#cut", "w:furnace_ext"):
            if nm in sc.actors:
                pd = pv.wrap(sc.actors[nm].GetMapper().GetInput())
                sc.set_mesh(nm, pd.clip_box((-30.0, 30.0, -30.0, 30.0, 1146.0, 1159.0), invert=True)
                            .extract_surface(algorithm="dataset_surface").triangulate())
        self.fur_cut = [g(x) for x in PARTS_CUT]
        self.sock_deg = 0.0
        self.cr_deg = 0.0
        AB.caption_rows(sc)

    # ------------------------------------------------------------------------------------------ small parts
    def cg_jaws(self, f_open):
        for k, d in enumerate(CT.cg_jaw_dirs()):
            self.sc.gmat[f"cr:cg_jaw{k}"] = T(d * CT.CG_JAW_OPEN * f_open)

    def fix_jaws(self, f_open):
        for s, grp in ((-1, "cr:fix_a"), (1, "cr:fix_b")):
            self.sc.gmat[grp] = T((s * CT.FIX_JAW_OPEN * f_open, 0.0, 0.0))

    def tw_jaws(self, f_open):
        """f_open 1: the tweezers' tips 20 mm apart (rest); 0: on the 16 mm nozzle."""
        self.tw_set(16.0 + 4.0 * f_open)

    def tw_set(self, gap):
        """The tweezers' tips `gap` mm apart (20 at rest). A lever in the handle: 4 mm of tip travel for each mm the
        2F-85's pads close on the handle's halves (ours)."""
        self.tw_gap = gap
        for s, grp in ((-1, "cr:tw_jaw_a"), (1, "cr:tw_jaw_b")):
            self.sc.gmat[grp] = T((s * (gap / 2.0 - 8.0), 0.0, 0.0))

    def tw_close_to(self, rb, gap):
        """update(u): the 2F-85 squeezes the tweezers' handle until the tips are `gap` mm apart."""
        g0 = getattr(self, "tw_gap", 20.0)
        c0, c1 = rb.close, CT.gripper_gap_close(28.0 - (20.0 - gap) / 4.0)

        def upd(u):
            rb.set(close=c0 + (c1 - c0) * u)
            self.tw_set(g0 + (gap - g0) * u)
        return upd

    def sock(self, deg):
        self.sock_deg = deg
        self.sc.gmat["cr:key_sock"] = R((0, 0, 1), deg)

    def seat_local(self, name):
        """An insulation piece on its seat on the parts table: its matrix in the model frame (parent "rp")."""
        key = dict(top_ins="top_ring", side_ins="side_tube", bottom_ins="bottom_ring")[name]
        z0 = dict(top_ins=M.RIM, side_ins=M.CRUCIBLE_BASE, bottom_ins=1157.0)[name]
        x, y = CT.SEATS_T[key]
        return T((x, y, CT.SEAT_Z - z0))

    def fix_turn(self, deg, f_open=0.0):
        """The holder fixture turns its jaws (and the holder they clamp) `deg` about its axis."""
        x, y = CT.LAY1["fixture"]
        Rz = T((x, y, 0.0)) @ R((0, 0, 1), deg) @ T((-x, -y, 0.0))
        for s_, grp in ((-1, "cr:fix_a"), (1, "cr:fix_b")):
            self.sc.gmat[grp] = Rz @ T((s_ * CT.FIX_JAW_OPEN * f_open, 0.0, 0.0))
        self.sc.gmat[g("holder")] = T((x, y, CT.FIX_TOP - 1160.0)) @ R((0, 0, 1), deg)

    def mir_local(self, mir, Mx):
        return self.sc.world(mir.g) @ Mx

    def at1(self, key, z, extra=None):
        """A MiR-1-local pose over a fixture."""
        x, y = CT.LAY1[key]
        Mx = T((x, y, z))
        return Mx if extra is None else Mx @ extra

    # ------------------------------------------------------------------------------------------ poses
    def tool_tcp(self, grp, h, spin=0.0, world=None):
        W = self.sc.world(grp) if world is None else world
        return W @ T((0.0, 0.0, h)) @ R((1, 0, 0), 180.0) @ R((0, 0, 1), spin)

    def key_tcp(self, world=None):
        W = self.sc.world("cr:key") if world is None else world
        return W @ T(tuple(CT.KEY_GRASP)) @ R((0, 0, 1), 90.0) @ R((1, 0, 0), 180.0)

    def key_model(self, z0, x0=0.0):
        """The key's frame in the model at the furnace axis (x0 = 0), its cup floor's top at z0, handle out the door."""
        return AB.WT(T((x0, 0.0, z0)) @ R((0, 0, 1), 180.0))


def tw_on_tc(W_tc):
    """The tweezers' frame holding the thermocouple by its leg (TC_GRIP), tips across the leg, 2 mm under its axis;
    W_tc: the thermocouple group's world matrix."""
    x = np.array([TC_DIR[1], -TC_DIR[0], 0.0])
    z = np.array([0.0, 0.0, 1.0])
    F = np.eye(4)
    F[:3, 0], F[:3, 1], F[:3, 2] = x, np.cross(z, x), z
    F[:3, 3] = TC_GRIP - np.array([0.0, 0.0, 2.0])
    return W_tc @ F


def tcp_down(p_model, spin=180.0):
    return AB.tcp(p_model, (0.0, 0.0, -1.0), spin)


def up(Tw, dz):
    return T((0.0, 0.0, dz)) @ Tw


def back(Tw, d):
    return Tw @ T((0.0, 0.0, -d))


def swap(rb, new):
    """The arm holds `old` with `new` riding on it: hold `new` instead, `old` riding on it (same poses). A new held
    episode starts, so the audit allows what the parts touch here, at this end of it."""
    rb.reparent(new, None)
    rb.release(new)
    rb.grasp(new)


def joint_w3(rb, Tw, lo_deg=-330.0, hi_deg=330.0, then=None):
    """rb.joint_to(Tw) but with wrist 3 wrapped into [lo, hi] deg (the UR10e's wrist 3 turns +-360 deg), so a turn
    that follows stays in range; among the IK branches, the nearest one clear of everything."""
    import collide
    sc = rb.sc
    Tb = np.linalg.inv(sc.world(rb.root)) @ Tw
    cands = collide.ik_all(rb.model, Tb, rb.q) or [rb.solve(Tw)]
    lo, hi = math.radians(lo_deg), math.radians(hi_deg)
    ok = []
    for q in cands:
        q = np.array(q, float)
        while q[5] > hi:
            q[5] -= 2 * math.pi
        while q[5] < lo:
            q[5] += 2 * math.pi
        if lo <= q[5] <= hi:
            ok.append(q)
    chk = rb.checker()
    world = chk.snapshot()

    def clear(q):
        if chk.collisions(q, rb.close, world, chk.touching(q, rb.close, world)):
            return False
        if then is None:
            return True
        try:                                  # the straight line that follows, in this branch: clear at its end too
            q2 = rb.solve(then, q)            # (the lid now stands on the left, at the wrist's height)
        except ValueError:
            return False
        if np.abs(q2 - q).max() > math.radians(25):
            return False
        return not chk.collisions(q2, rb.close, world, chk.touching(q2, rb.close, world))
    free = [q for q in ok if clear(q)]
    if not free:
        print(f"warning: {rb.sc.name} {rb.sc.label}: no IK branch clear at both ends", file=sys.stderr, flush=True)
        return rb.joint_to(Tw=Tw)              # as robot.py does: the nearest branch clear at the pre-pose
    pick = min(free, key=lambda q: float(np.sum((np.asarray(q) - rb.q) ** 2)))
    return rb.joint_to(q1=pick)


def turn_path(rb, pivot_w, deg, axis=(0.0, 0.0, 1.0), extra_dz=0.0):
    """update(u): the held tool turned `deg` about the vertical axis through the grasp point (the crucible's and the
    gripper's axis: the handle is on it), as a pure wrist-3 rotation (the TCP lies on tool0's z axis), so the turn
    can't flip the arm. The sign is checked against forward kinematics; the UR10e's wrist 3 range (+-360 deg) is
    checked too."""
    q0 = rb.q.copy()
    T0 = rb.tcp_world()
    want = R(axis, deg, tuple(T0[:3, 3])) @ T0
    best = None
    for sgn in (1.0, -1.0):
        q1 = q0.copy()
        q1[5] += math.radians(deg) * sgn
        err = np.linalg.norm(rb.tcp_world(q1)[:3, :3] - want[:3, :3]) + np.linalg.norm(rb.tcp_world(q1)[:3, 3]
                                                                                       - want[:3, 3]) / 100.0
        if best is None or err < best[0]:
            best = (err, q1)
    err, q1 = best
    if err > 1e-3:
        print(f"warning: turn_path: the grasp point is off the wrist's axis (err {err:.4f})", file=sys.stderr)
    if abs(q1[5]) > 2 * math.pi + 1e-6:
        print(f"warning: turn_path: wrist 3 at {math.degrees(q1[5]):.0f} deg, past +-360", file=sys.stderr)
    print(f"{NAME} turn {deg:+.0f} deg: wrist 3 {math.degrees(q0[5]):.0f} -> {math.degrees(q1[5]):.0f} deg", flush=True)

    def upd(u):
        q = q0 + (q1 - q0) * u
        rb.set(q)
    return upd


# ---------------------------------------------------------------------------------------------- clip helpers
class Clip:
    def __init__(self, rig: Rig):
        self.rig, self.sc = rig, rig.sc
        self.k = 0
        self.N = 1
        self.rows = {}

    def gauges(self, **kv):
        self.rows.update({k: v for k, v in kv.items()})
        AB.caption_rows(self.sc, **self.rows)

    def step(self, cap, secs, update=None, hold=0.05, **kw):
        self.sc.step(f"{self.k}/{self.N}", cap, secs, update, hold=hold, **kw)

    # tools ---------------------------------------------------------------------------------------------
    def fetch(self, rb, key, cap, cam=None, labels=(), also=None):
        rig, sc = self.rig, self.sc
        grp = TOOLS1[key][0]
        G = rig.tool_tcp(grp, HANDLE[key])
        self.step(cap, 1.5, both(rb.joint_to(Tw=back(G, 110.0)), rb.grip_to(0.0), also), cam_to=cam, labels=labels)
        self.step(cap, 0.6, rb.line_to(G))
        self.step(cap, 0.35, rb.grip_to(GRIP))
        rb.grasp(grp)
        self.step(cap, 0.7, rb.line_to(up(rb.tcp_world(), 150.0 if key != "nt" else 230.0)))

    def stow(self, rb, key, cap, cam=None):
        rig, sc = self.rig, self.sc
        grp, _, z = TOOLS1[key]
        dest = rig.mir_local(rig.ma, rig.at1(key, z))
        G = rig.tool_tcp(grp, HANDLE[key], world=dest)
        lift = 150.0 if key != "nt" else 230.0
        self.step(cap, 1.5, rb.joint_to(Tw=up(G, lift)), cam_to=cam)
        self.step(cap, 0.7, rb.line_to(G))
        rb.release("amr")
        sc.gmat[grp] = rig.at1(key, z)                 # exactly on its stand
        self.step(cap, 0.3, rb.grip_to(0.0))
        self.step(cap, 0.5, rb.line_to(back(rb.tcp_world(), 90.0)))

    def take(self, rb, part):
        """The tool the arm holds has closed on `part`: the arm now holds the part, the tool riding on it (so the
        audit's held episodes start and end where the part is picked up and put down)."""
        tool = rb.held[0]
        rb.release(part)
        rb.grasp(part)
        return tool

    def give(self, rb, tool, dest):
        rb.release(dest)
        rb.grasp(tool)


# ---------------------------------------------------------------------------------------------- the out clip
def clip_out():
    rig = Rig("out")
    sc, r1, r2 = rig.sc, rig.r1, rig.r2
    c = Clip(rig)
    c.N = 8
    c.gauges(Furnace="cold (< 50 C): can be touched", Lid="open (latch: atom_latch)",
             Door="open, clamps off", Stack="out, on its bench")
    sc.cam = list(C_WIDE)
    # 1 ------------------------------------------------------------------------ the thermocouple
    c.k = 1
    cap = ("The furnace is cold, the lid open and the chamber's door open with its clamps off; the ultrasonic stack "
           "is out, so the nut can be reached through the door. First out: the Type N thermocouple, its thin "
           "ceramic sheath taken by its leg on tweezers and drawn straight up (SOP 1).")
    # arm 2 goes to stand by over its key, out of arm 1's way, while arm 1 takes the tweezers
    c.fetch(r1, "tw", cap, cam=C_MIR1, also=both(r2.joint_to(Tw=back(rig.key_tcp(), 110.0)), r2.grip_to(0.0)),
            labels=[("tweezers", tuple(rig.mir_local(rig.ma, rig.at1("tw", CT.TW_Z + 200.0))[:3, 3]), (0.40, 0.30))])
    Wtw = tw_on_tc(AB.WT(np.eye(4)))
    Gtc = rig.tool_tcp("cr:tw", CT.TW_HANDLE, world=Wtw)
    c.step(cap, 2.0, joint_w3(r1, up(Gtc, 90.0), then=Gtc), hold=0.5, cam_to=C_FUR,
           labels=[("thermocouple, Type N (back right)", tuple(AB.W(TC_GRIP + (0, 0, 10))), (0.70, 0.26)),
                   ("sealing-rod lever and pin", tuple(AB.W((40.0, -20.0, M.Z_ARM + 10))), (0.68, 0.52))])
    c.step(cap, 0.8, r1.line_to(Gtc))
    c.step(cap, 0.35, rig.tw_close_to(r1, 3.8))
    tw_tool = c.take(r1, g("tc"))
    c.gauges(**{"F/T 1": "pull 0.8 N (assumed: friction in the hole)"})
    c.step(cap, 1.3, r1.line_to(up(r1.tcp_world(), TC_PULL)), hold=0.2)
    # into its stand on MiR 1: the vertical part down the stand's bore
    psi = 180.0 - math.degrees(math.atan2(TC_DIR[1], TC_DIR[0]))
    tc_dest_local = rig.at1("tc", CT.TC_Z, R((0, 0, 1), psi) @ T((-TC_XY[0], -TC_XY[1], -(M.RIM - 40.0))))
    tc_dest = rig.mir_local(rig.ma, tc_dest_local)
    Gtc_dest = tc_dest @ np.linalg.inv(sc.world(g("tc"))) @ r1.tcp_world()
    c.step(cap, 1.6, r1.joint_to(Tw=up(Gtc_dest, 100.0)), cam_to=C_MIR1)
    c.step(cap, 1.0, r1.line_to(Gtc_dest))
    c.step(cap, 0.3, rig.tw_close_to(r1, 20.0))
    c.give(r1, tw_tool, "amr")
    sc.gmat[g("tc")] = tc_dest_local
    c.gauges(**{"F/T 1": ""})
    c.step(cap, 0.5, r1.line_to(up(r1.tcp_world(), 90.0)))
    c.stow(r1, "tw", cap, cam=C_MIR1)
    c.rows = {"Furnace": "cold, lid open, door open"}
    c.gauges()
    # 2 ------------------------------------------------------------------------ the pin and the lever
    c.k = 2
    cap = ("The lever's safety pin out by its T-handle, the rod still seated on the nozzle (pulled with the rod "
           "lifted, the rod would drop 12 mm onto the nozzle), then the lever swung up 70 deg on its post.")
    pin_g = np.array([0.0, CT.PIN_GRIP_Y, M.Z_ARM])
    Gp = tcp_down(pin_g, 180.0)
    c.step(cap, 1.6, both(r1.joint_to(Tw=back(Gp, 110.0)), r1.grip_to(0.0)), cam_to=C_FUR2,
           labels=[("safety pin", tuple(AB.W(pin_g + (0, -10, 12))), (0.30, 0.30))])
    c.step(cap, 0.7, r1.line_to(Gp))
    c.step(cap, 0.3, r1.grip_to(GRIP_PIN))
    r1.grasp("cr:pin")
    c.step(cap, 0.9, r1.line_to(T((0.0, -48.0, 0.0)) @ r1.tcp_world()))
    pin_dest_local = rig.at1("pin", CT.PIN_Z - M.Z_ARM, T((0.0, 1.0, 0.0)))
    pin_dest = rig.mir_local(rig.ma, pin_dest_local)
    Gp_dest = pin_dest @ np.linalg.inv(AB.WT(np.eye(4))) @ Gp
    c.step(cap, 1.6, r1.joint_to(Tw=up(Gp_dest, 90.0)), cam_to=C_MIR1)
    c.step(cap, 0.7, r1.line_to(Gp_dest))
    r1.release("amr")
    sc.gmat["cr:pin"] = pin_dest_local
    c.step(cap, 0.3, r1.grip_to(0.0))
    c.step(cap, 0.5, r1.line_to(back(r1.tcp_world(), 80.0)))
    # the lever up (chapter 2's grasp and arc)
    lev_g = tcp_down((AA.LEVER_AT, 0.0, M.Z_ARM), 90.0)
    piv_w = tuple(AB.W(M.PIVOT))

    def lev_pose(u):
        return R(tuple(M.LEVER_AXIS), LEVER_UP * u, piv_w) @ lev_g
    q_lev = AA.arc_branch(r1, sc, lev_g, lev_pose, lambda u: AA.lever(sc, LEVER_UP * u), GRIP_LEVER,
                          ("holder_arm",), back=100.0)
    c.step(cap, 1.5, both(r1.joint_to(q1=r1.solve(back(lev_g, 100.0), q_lev)), r1.grip_to(0.0)), cam_to=C_FUR2)
    c.step(cap, 0.6, r1.line_to(lev_g))
    c.step(cap, 0.3, r1.grip_to(GRIP_LEVER))
    r1.events.append((sc.n, "grasp", g("arm"), None))
    arc = AA.follow(r1, [lev_pose(u) for u in np.linspace(0.0, 1.0, 12)])
    c.step(cap, 1.6, both(arc, lambda u: AA.lever(sc, LEVER_UP * u)))
    c.step(cap, 0.3, r1.grip_to(0.0))
    r1.events.append((sc.n, "release", g("arm"), None))
    c.step(cap, 0.6, r1.line_to(up(r1.tcp_world(), 110.0)))
    # 3 ------------------------------------------------------------------------ the rod
    c.k = 3
    cap = ("The sealing rod out by its brass adapter, never by the graphite, lifted straight up so the ball tip "
           "doesn't drag on the crucible's floor, and stood in its holder on MiR250 1 (SOP 1, 6).")
    Gr = tcp_down((0.0, 0.0, ROD_GRIP_Z), ROD_SPIN_OUT)
    c.step(cap, 1.5, both(joint_w3(r1, back(Gr, 110.0), then=Gr), r1.grip_to(0.0)), cam_to=C_FUR,
           labels=[("sealing rod: brass adapter", tuple(AB.W((0, 0, ROD_GRIP_Z + 20))), (0.30, 0.28))])
    c.step(cap, 0.7, r1.line_to(Gr))
    c.step(cap, 0.3, r1.grip_to(GRIP_ROD))
    r1.grasp(g("rod"))
    c.step(cap, 1.6, r1.line_to(up(Gr, 175.0)))
    rod_dest_local = rig.at1("rod", CT.ROD_Z - 1200.2)
    rod_dest = rig.mir_local(rig.ma, rod_dest_local)
    Gr_dest = rod_dest @ np.linalg.inv(AB.WT(np.eye(4))) @ Gr
    c.step(cap, 1.8, r1.joint_to(Tw=up(Gr_dest, 140.0)), cam_to=C_MIR1)
    c.step(cap, 1.2, r1.line_to(Gr_dest))
    r1.release("amr")
    sc.gmat[g("rod")] = rod_dest_local
    c.step(cap, 0.3, r1.grip_to(0.0))
    c.step(cap, 0.5, r1.line_to(back(r1.tcp_world(), 80.0)))
    # 4 ------------------------------------------------------------------------ top ring and side tube; the key in
    c.k = 4
    cap = ("Insulation out: the top ring, then the side tube. The side tube has 0.6 mm to the crucible and 1 mm to "
           "the coil, so only its top face can be taken: a needle tool (four Schmalz SNG-M heads) on that face. "
           "Arm 2 takes the nut key meanwhile.")
    c.fetch(r1, "nt", cap, cam=C_MIR1, labels=[("needle tool (insulation)", tuple(rig.mir_local(
        rig.ma, rig.at1("nt", CT.NT_Z + 120))[:3, 3]), (0.62, 0.30))])
    # arm 2 takes the key while arm 1 works
    Gk = rig.key_tcp()
    k_pre = back(Gk, 110.0)
    for name, (part, Mx) in (("top_ins", ("top_ring", 1341.0)), ("side_ins", ("side_tube", M.RIM))):
        face = Mx
        lift = 60.0 if name == "top_ins" else 175.0
        Gn = rig.tool_tcp("cr:nt", CT.NT_HANDLE, spin=0.0, world=AB.WT(T((0.0, 0.0, face))) @ TURN_OUT)
        upd2 = None
        if name == "top_ins":
            upd2 = both(r2.joint_to(Tw=k_pre), r2.grip_to(0.0))
        c.step(cap, 1.7, both(joint_w3(r1, up(Gn, 120.0), then=Gn), upd2), cam_to=C_FUR)
        if name == "top_ins":
            c.step(cap, 0.6, both(r1.line_to(Gn), r2.line_to(Gk)))
            c.step(cap, 0.3, r2.grip_to(GRIP))
            r2.grasp("cr:key")
        else:
            c.step(cap, 0.7, r1.line_to(Gn))
        c.take(r1, g(name))
        c.step(cap, 0.35, lambda u: sc.show(sc.members("cr:nt_needles"), u), hold=0.1)
        c.gauges(**{"F/T 1": f"lift {'2.6' if name == 'top_ins' else '1.4'} N (the part's weight, est.)"})
        c.step(cap, 1.0 if name == "top_ins" else 1.6, r1.line_to(up(r1.tcp_world(), lift)))
        seat = rig.seat_local(name)
        dest = AB.WT(seat)
        Gd = rig.tool_tcp("cr:nt", CT.NT_HANDLE, world=dest @ T((0.0, 0.0, face)) @ TURN_OUT)
        c.step(cap, 1.8, r1.joint_to(Tw=up(Gd, 90.0)), cam_to=C_TABLE)
        c.step(cap, 0.8, r1.line_to(Gd))
        c.step(cap, 0.3, lambda u: sc.show(sc.members("cr:nt_needles"), 1.0 - u))
        c.give(r1, "cr:nt", "rp")
        sc.gmat[g(name)] = seat
        c.gauges(**{"F/T 1": ""})
        c.step(cap, 0.6, r1.line_to(up(r1.tcp_world(), 90.0)))
    # arm 2: the key up and over to the door, while arm 1 puts the needle tool back
    k_door = AB.WT(T((-185.0, 0.0, 1080.0)) @ R((0, 0, 1), 180.0))
    Gk_door = rig.key_tcp(world=k_door)
    c.step(cap, 0.7, r2.line_to(up(r2.tcp_world(), 110.0)))
    c.step(cap, 2.0, both(r2.joint_to(Tw=Gk_door), c_stow_first(c, r1)), cam_to=C_DOOR)
    c_stow_rest(c, r1)
    # 5 ------------------------------------------------------------------------ the crucible, the nut held below
    c.k = 5
    cap = ("Arm 2 brings the key in through the door, under the nut: six pins go into the nut's six notches and its "
           "cup sits under the nut and the seal. Arm 1 sets the crucible gripper's three soft jaws on the crucible.")
    k_in = AB.WT(T((0.0, 0.0, 1080.0)) @ R((0, 0, 1), 180.0))
    k_hold = AB.WT(T((0.0, 0.0, M.NUT_Z[0])) @ R((0, 0, 1), 180.0))
    c.fetch(r1, "cg", cap, cam=C_MIR1)
    cut_on = (lambda u: AA.set_cut(sc, u, rig.fur_cut))
    c.step(cap, 1.6, both(r2.line_to(rig.key_tcp(world=k_in)), cut_on), cam_to=C_NUT,
           labels=[("graphite nut and seal (cut away)", tuple(AB.W((0, -30, 1116))), (0.62, 0.30)),
                   ("nut key, arm 2", tuple(AB.W((-120, 0, 1090))), (0.20, 0.62))])
    c.step(cap, 1.0, r2.line_to(rig.key_tcp(world=k_hold)))
    rig.sock(0.0)
    rb = r2
    for grp in ("nut", "seal"):                      # the key takes them: 0.3 mm off the roof as it holds
        rb.reparent(g(grp), "cr:key_sock")
        sc.gmat[g(grp)] = T((0.0, 0.0, -0.3)) @ sc.gmat[g(grp)]
    c.gauges(**{"F/T 2": "up 3 N on the nut (assumed)"})
    Gc = rig.tool_tcp("cr:cg", CT.CG_HANDLE, world=AB.WT(T((0.0, 0.0, M.RIM))) @ TURN_OUT)
    c.step(cap, 1.8, joint_w3(r1, up(Gc, 120.0), -170.0, 170.0, then=Gc), cam_to=C_FUR)
    c.step(cap, 1.0, r1.line_to(Gc))
    c.step(cap, 0.5, lambda u: rig.cg_jaws(1.0 - u))
    c.take(r1, g("crucible"))
    cap = (f"Breakaway: arm 1 turns the crucible {BRK_DEG:.0f} deg anticlockwise while the key holds the nut. The "
           f"wrist's {FT} reads the torque that breaks the joint, and the number is logged every time.")

    def brk(u):
        tq = TQ_BREAK * min(1.0, u / 0.25) if u < 0.4 else TQ_BREAK * max(0.15, 1.0 - (u - 0.4) * 2.5)
        c.gauges(**{"F/T 1": f"Mz {tq:.2f} N m (breakaway, logged)"})
    rot = turn_path(r1, AB.W((0.0, 0.0, M.RIM)), BRK_DEG)
    c.step(cap, 1.8, both(rot, brk), hold=0.5, cam_to=C_FUR2)
    cap = ("Then the key's motor spins the nut off: 6.9 more turns of 2.0 mm pitch, the cup following it down, while "
           "arm 1 holds the crucible still. The nut and the seal stay in the cup, so nothing falls.")
    turns = NUT_TURNS - BRK_DEG / 360.0
    z_off = M.NUT_Z[0] - 0.3 - turns * PITCH          # the nut's top at the shank's end: off the thread

    def spin(u):
        rig.sock(-360.0 * turns * u)
        c.gauges(**{"Nut": f"{turns * u:.1f} of {turns:.1f} turns off",
                    "F/T 1": "Mz 0.04 N m (thread drag)"})
    c.step(cap, 4.5, both(r2.line_to(rig.key_tcp(world=rig.key_model(z_off))), spin), cam_to=C_NUT, still=True)
    c.gauges(**{"F/T 1": "Mz 0.00 N m: off"})
    c.step(cap, 0.6, r2.line_to(rig.key_tcp(world=rig.key_model(z_off - 6.0))), hold=0.4)
    # 6 ------------------------------------------------------------------------ out: the key, the crucible
    c.k = 6
    cap = ("The key goes out through the door with the nut and the seal in its cup, and back onto its posts on "
           "MiR250 2. Arm 1 lifts the crucible straight up out of the coil, the holder's shank clear of the floor.")
    k_out = AB.WT(T((0.0, 0.0, 1080.0)) @ R((0, 0, 1), 180.0))
    c.step(cap, 0.8, r2.line_to(rig.key_tcp(world=k_out)))
    c.step(cap, 1.5, both(r2.line_to(Gk_door), lambda u: AA.set_cut(sc, 1.0 - u, rig.fur_cut)), cam_to=C_DOOR)
    c.step(cap, 2.0, both(r2.joint_to(Tw=up(Gk, 110.0)), r1.line_to(up(r1.tcp_world(), 260.0))), cam_to=C_WIDE)
    c.step(cap, 0.8, r2.line_to(Gk))
    r2.release("amrB")
    sc.gmat["cr:key"] = CT.key_rack_pose()
    c.step(cap, 0.3, r2.grip_to(0.0))
    c.step(cap, 0.6, r2.line_to(back(r2.tcp_world(), 100.0)))
    cr_dest_local = rig.at1("cradle", CT.CRADLE_Z - M.CRUCIBLE_BASE, R((0, 0, 1), BRK_DEG))
    cr_dest = rig.mir_local(rig.ma, cr_dest_local)
    Gc_dest = cr_dest @ np.linalg.inv(sc.world(g("crucible"))) @ r1.tcp_world()
    c.step(cap, 2.2, both(r1.joint_to(Tw=up(Gc_dest, 120.0)), r2.joint_to(q1=r2.solve(back(Gk, 220.0)))),
           cam_to=C_CRADLE)
    c.step(cap, 1.2, r1.line_to(Gc_dest))
    c.step(cap, 0.4, lambda u: rig.cg_jaws(u))
    c.give(r1, "cr:cg", "amr")
    sc.gmat[g("crucible")] = cr_dest_local
    c.gauges(**{"F/T 1": "", "F/T 2": "", "Nut": "in the key's cup, with the seal"})
    # 7 ------------------------------------------------------------------------ the nozzle checked
    c.k = 7
    cap = ("On the way: the cradle's backlight under the nozzle and the wrist camera looking down the bore. Light "
           "through the 0.5 mm bore means it is open; a closed one waits for a person to drill it by hand (SOP 2).")
    c.step(cap, 0.8, r1.line_to(up(r1.tcp_world(), 150.0)))
    cam_tcp = up(Gc_dest, 150.0) @ T((0.0, 67.0, 0.0))
    for n in rig.lights:
        sc.ambient[n] = 1.0
    c.step(cap, 1.0, r1.line_to(cam_tcp), hold=0.9,
           labels=[("backlight under the nozzle: light through the bore", tuple(rig.mir_local(rig.ma, rig.at1(
               "cradle", CT.CRADLE_Z + 120))[:3, 3]), (0.62, 0.30))])
    c.gauges(Nozzle="light through the bore: open (D405)")
    # 8 ------------------------------------------------------------------------ bottom ring, tool back
    c.k = 8
    cap = ("Last, the bottom ring, which sits under the crucible's base in the model and so comes out after it "
           "(the SOP lists it first). The furnace is empty for the explosion-proof vacuum (atom_vac).")
    c.stow(r1, "cg", cap, cam=C_MIR1)
    c.fetch(r1, "nt", cap, cam=C_MIR1)
    Gn = rig.tool_tcp("cr:nt", CT.NT_HANDLE, world=AB.WT(T((0.0, 0.0, M.CRUCIBLE_BASE))) @ TURN_OUT)
    c.step(cap, 1.8, joint_w3(r1, up(Gn, 120.0), then=Gn), cam_to=C_FUR)
    c.step(cap, 1.2, r1.line_to(Gn))
    c.take(r1, g("bottom_ins"))
    c.step(cap, 0.35, lambda u: sc.show(sc.members("cr:nt_needles"), u))
    c.step(cap, 1.6, r1.line_to(up(r1.tcp_world(), 205.0)))
    seat = rig.seat_local("bottom_ins")
    Gd = rig.tool_tcp("cr:nt", CT.NT_HANDLE, world=AB.WT(seat) @ T((0.0, 0.0, M.CRUCIBLE_BASE)) @ TURN_OUT)
    c.step(cap, 1.8, r1.joint_to(Tw=up(Gd, 90.0)), cam_to=C_TABLE)
    c.step(cap, 0.8, r1.line_to(Gd))
    c.step(cap, 0.3, lambda u: sc.show(sc.members("cr:nt_needles"), 1.0 - u))
    c.give(r1, "cr:nt", "rp")
    sc.gmat[g("bottom_ins")] = seat
    c.step(cap, 0.6, r1.line_to(up(r1.tcp_world(), 120.0)))
    c.stow(r1, "nt", cap, cam=C_WIDE)
    c.gauges(Furnace="empty: ready for the vacuum")
    c.step(cap, 1.0, r1.line_to(up(r1.tcp_world(), 120.0)), hold=1.4, cam_to=C_WIDE)
    return AB.finish(sc)


def clip_in():
    rig = Rig("in")
    sc, r1, r2 = rig.sc, rig.r1, rig.r2
    c = Clip(rig)
    c.N = 9
    # the start: the furnace empty and vacuumed; the parts on MiR 1; the nut and the lower seal in the key's cup
    th0 = 15.0
    cr_cradle = rig.at1("cradle", CT.CRADLE_Z - M.CRUCIBLE_BASE, R((0, 0, 1), th0))
    for grp in ("crucible", "holder", "nozzle", "rod", "tc"):
        sc.parent[g(grp)] = "amr"
    sc.gmat[g("crucible")] = cr_cradle
    sc.gmat[g("holder")] = rig.at1("fixture", CT.FIX_TOP - 1160.0)
    sc.gmat[g("nozzle")] = rig.at1("nozzle", CT.NOZ_Z - (M.CRUCIBLE_BASE - 5.0))
    for grp in ("top_ins", "side_ins", "bottom_ins"):
        sc.gmat[g(grp)] = rig.seat_local(grp)
    sc.gmat[g("rod")] = rig.at1("rod", CT.ROD_Z - 1200.2)
    psi = 180.0 - math.degrees(math.atan2(TC_DIR[1], TC_DIR[0]))
    sc.gmat[g("tc")] = rig.at1("tc", CT.TC_Z, R((0, 0, 1), psi) @ T((-TC_XY[0], -TC_XY[1], -(M.RIM - 40.0))))
    sc.parent["cr:pin"] = "amr"
    sc.gmat["cr:pin"] = rig.at1("pin", CT.PIN_Z - M.Z_ARM, T((0.0, 1.0, 0.0)))
    AA.lever(sc, LEVER_UP)
    for grp in ("nut", "seal"):
        sc.parent[g(grp)] = "cr:key_sock"
        sc.gmat[g(grp)] = R((0, 0, 1), -180.0) @ T((0.0, 0.0, -M.NUT_Z[0]))
    rig.fix_jaws(1.0)
    rig.tw_jaws(1.0)
    c.gauges(Furnace="cold, empty, vacuumed", Crucible="BN coated, dry (atom_bn)", Lid="open (latch: atom_latch)",
             Door="open, clamps off; stack out")
    sc.cam = list(C_WIDE)
    # 1 ------------------------------------------------------------------------ the bottom ring
    c.k = 1
    cap = ("The rebuild (SOP 3): the furnace is empty and vacuumed, the crucible back in its cradle, BN coated and "
           "dry. First the bottom ring, lowered into the coil on the needle tool. Arm 2 takes the nut key, the nut "
           "and the lower seal in its cup.")
    c.fetch(r1, "nt", cap, cam=C_MIR1)
    Gn_seat = rig.tool_tcp("cr:nt", CT.NT_HANDLE,
                           world=sc.world(g("bottom_ins")) @ T((0.0, 0.0, M.CRUCIBLE_BASE)) @ TURN)
    Gk = rig.key_tcp()
    c.step(cap, 1.6, both(r1.joint_to(Tw=up(Gn_seat, 90.0)), r2.joint_to(Tw=back(Gk, 110.0)), r2.grip_to(0.0)),
           cam_to=C_TABLE)
    c.step(cap, 0.8, both(r1.line_to(Gn_seat), r2.line_to(Gk)))
    c.take(r1, g("bottom_ins"))
    c.step(cap, 0.35, both(lambda u: sc.show(sc.members("cr:nt_needles"), u), r2.grip_to(GRIP)))
    r2.grasp("cr:key")
    c.step(cap, 0.8, both(r1.line_to(up(r1.tcp_world(), 220.0)), r2.line_to(up(r2.tcp_world(), 110.0))))
    Gn = rig.tool_tcp("cr:nt", CT.NT_HANDLE, world=AB.WT(T((0.0, 0.0, M.CRUCIBLE_BASE))) @ TURN)
    k_door = rig.key_model(1080.0, -185.0)
    c.step(cap, 2.0, both(joint_w3(r1, up(Gn, 200.0), then=Gn), r2.joint_to(Tw=rig.key_tcp(world=k_door))),
           cam_to=C_FUR)
    c.step(cap, 1.5, r1.line_to(Gn))
    c.step(cap, 0.3, lambda u: sc.show(sc.members("cr:nt_needles"), 1.0 - u))
    c.give(r1, "cr:nt", "rp")
    sc.gmat[g("bottom_ins")] = np.eye(4)
    c.step(cap, 1.3, r1.line_to(up(r1.tcp_world(), 220.0)))
    c.rows = {"Furnace": "cold, empty; lid, door open"}
    c.gauges()
    c.stow(r1, "nt", cap, cam=C_MIR1)
    # 2 ------------------------------------------------------------------------ the nozzle into the holder
    c.k = 2
    cap = ("The nozzle on tweezers: over its tray's backlight the wrist camera checks for light through the bore, "
           "then it goes into the holder's recess white side up (SOP 2-3). A closed one waits for a person to drill.")
    c.fetch(r1, "tw", cap, cam=C_CRADLE)
    Gtw = rig.tool_tcp("cr:tw", CT.TW_HANDLE, world=sc.world(g("nozzle")) @ T((0.0, 0.0, M.CRUCIBLE_BASE - 2.0)))
    c.step(cap, 1.4, r1.joint_to(Tw=up(Gtw, 60.0)))
    for n in rig.lights:
        sc.ambient[n] = 1.0
    c.step(cap, 0.7, r1.line_to(Gtw))
    c.step(cap, 0.35, rig.tw_close_to(r1, 16.0))
    tool = c.take(r1, g("nozzle"))
    c.gauges(Nozzle="light through the bore: open (D405)")
    c.step(cap, 0.7, r1.line_to(up(r1.tcp_world(), 60.0)), hold=0.4,
           labels=[("nozzle, white side up", tuple(rig.mir_local(rig.ma, rig.at1("nozzle", CT.NOZ_Z + 70))[:3, 3]),
                    (0.62, 0.30))])
    hol = sc.world(g("holder"))
    # into the recess: the tips stop 0.6 mm over the holder's face; it slides the last 2.6 mm down the recess
    noz_in = hol @ T((0.0, 0.0, 2.6))
    Gtw_in = noz_in @ np.linalg.inv(sc.world(g("nozzle"))) @ r1.tcp_world()
    c.step(cap, 1.2, r1.joint_to(Tw=up(Gtw_in, 50.0)))
    c.step(cap, 0.8, r1.line_to(Gtw_in))
    c.step(cap, 0.3, rig.tw_close_to(r1, 20.0))
    c.give(r1, tool, "amr")
    sc.gmat[g("nozzle")] = np.linalg.inv(sc.world("amr")) @ noz_in
    noz0 = sc.gmat[g("nozzle")].copy()
    c.step(cap, 0.3, lambda u: sc.gmat.__setitem__(g("nozzle"), T((0.0, 0.0, -2.6 * u)) @ noz0))
    r1.reparent(g("nozzle"), g("holder"))
    c.step(cap, 0.6, r1.line_to(up(r1.tcp_world(), 60.0)))
    c.stow(r1, "tw", cap, cam=C_MIR1)
    # 3 ------------------------------------------------------------------------ the crucible onto the holder
    c.k = 3
    cap = ("The holder fixture's soft jaws close on the shank. Arm 1 takes the crucible on its gripper's three soft "
           "jaws and sets it on the holder: a light push, turned back until the thread drops in, then forward.")
    c.step(cap, 0.5, lambda u: rig.fix_jaws(1.0 - u))
    c.fetch(r1, "cg", cap, cam=C_CRADLE)
    Gc = rig.tool_tcp("cr:cg", CT.CG_HANDLE, world=sc.world(g("crucible")) @ T((0.0, 0.0, M.RIM)))
    c.step(cap, 1.5, r1.joint_to(Tw=up(Gc, 100.0)))
    c.step(cap, 0.9, r1.line_to(Gc))
    c.step(cap, 0.4, lambda u: rig.cg_jaws(1.0 - u))
    c.take(r1, g("crucible"))
    c.step(cap, 1.0, r1.line_to(up(r1.tcp_world(), 140.0)))
    base_on = sc.world(g("holder"))                    # the holder's frame: its top face at model z 1185
    # where the crucible goes: its base 2.8 mm over the holder's top, turned so the screwing ends where we want it
    cr_now = sc.world(g("crucible"))
    rot_now = math.degrees(math.atan2(cr_now[1, 0], cr_now[0, 0]))
    start_deg = rot_now
    over = base_on @ T((0.0, 0.0, HOLDER_TURNS * HOLDER_PITCH + 0.3)) @ R((0, 0, 1), start_deg)
    Gc_over = over @ np.linalg.inv(cr_now) @ r1.tcp_world()
    c.step(cap, 1.6, r1.joint_to(Tw=up(Gc_over, 60.0)), cam_to=C_CRADLE)
    c.step(cap, 1.0, r1.line_to(Gc_over))
    c.gauges(**{"F/T 1": "Fz -2 N (a light push, assumed)"})
    c.step(cap, 1.0, lambda u: rig.fix_turn(-45.0 * u))
    c.step(cap, 0.25, r1.line_to(up(r1.tcp_world(), -0.3)), hold=0.2)
    cap = (f"The fixture turns the holder {HOLDER_TURNS:g} turns while arm 1 holds the crucible still: the thread's "
           "engagement is tiny, \"you just barely have to get it on\" (T8 2:26). It stops at the torque limit, "
           f"{TQ_HOLDER:.2f} N m (assumed): overtightening cracks the holder's thread (T9 33:45).")

    def tq_h(u):
        tq = 0.03 if u < 0.85 else 0.03 + (TQ_HOLDER - 0.03) * (u - 0.85) / 0.15
        c.gauges(**{"F/T 1": f"Mz {tq:.2f} N m" + (" (limit: stop)" if u > 0.99 else ""),
                    "Holder": f"{HOLDER_TURNS * u:.2f} of {HOLDER_TURNS:g} turns"})
    fwd = r1.line_to(up(r1.tcp_world(), -HOLDER_TURNS * HOLDER_PITCH))
    c.step(cap, 3.2, both(fwd, tq_h, lambda u: rig.fix_turn(-45.0 + 360.0 * HOLDER_TURNS * u)), hold=0.4)
    for grp in ("holder", "nozzle"):
        r1.reparent(g(grp), g("crucible"))
    # a new held episode: the arm holds the gripper with the crucible (now with its holder) riding on it
    swap(r1, "cr:cg")
    fdeg = -45.0 + 360.0 * HOLDER_TURNS
    x_, y_ = CT.LAY1["fixture"]
    Rz = T((x_, y_, 0.0)) @ R((0, 0, 1), fdeg) @ T((-x_, -y_, 0.0))
    c.step(cap, 0.4, lambda u: [sc.gmat.__setitem__(gr, Rz @ T((s_ * CT.FIX_JAW_OPEN * u, 0.0, 0.0)))
                                for s_, gr in ((-1, "cr:fix_a"), (1, "cr:fix_b"))])
    c.gauges(**{"F/T 1": "", "Holder": f"on, {TQ_HOLDER:.2f} N m"})
    c.step(cap, 1.0, r1.line_to(up(r1.tcp_world(), 120.0)))
    # 4 ------------------------------------------------------------------------ into the furnace
    c.k = 4
    cap = ("Straight down into the coil, the holder's shank through the bottom ring, the furnace floor and the "
           "chamber's top plate, with a light force limit. If it hangs, a small spiral search finds the bore.")
    cr_now = sc.world(g("crucible"))
    seated = AB.WT(R((0, 0, 1), ALIGN_DEG))
    Gseat = seated @ np.linalg.inv(cr_now) @ r1.tcp_world()
    c.step(cap, 2.2, joint_w3(r1, up(Gseat, 300.0), -220.0, 180.0, then=Gseat), cam_to=C_FUR)
    c.step(cap, 1.6, r1.line_to(up(Gseat, 30.0)))
    spiral = []
    for s in np.linspace(0.0, 1.0, 25):
        rr = 0.7 * (1.0 - s)
        a = 4.0 * math.pi * s
        spiral.append(T((rr * math.cos(a), rr * math.sin(a), 30.0 * (1.0 - s))) @ Gseat)

    def fz(u):
        c.gauges(**{"F/T 1": f"Fz {-2.0 - 4.0 * math.sin(math.pi * min(1.0, u * 1.3)):.1f} N (limit 8 N, "
                                   "assumed)" if u < 0.97 else "Fz -1.0 N: seated"})
    c.step(cap, 2.4, both(AA.follow(r1, spiral), fz), hold=0.3,
           labels=[("crucible, holder's shank through the floor", tuple(AB.W((0.0, -40.0, 1250.0))), (0.66, 0.28))])
    # 5 ------------------------------------------------------------------------ the nut from below
    c.k = 5
    cap = ("Arm 1 holds the crucible still. Arm 2's key comes in through the door with the nut and the lower seal in "
           "its cup and lifts them under the shank; the seal slides on first (SOP 3, T1 47:02).")
    c.step(cap, 1.0, lambda u: AA.set_cut(sc, u, rig.fur_cut), cam_to=C_NUT,
           labels=[("nut key, arm 2", tuple(AB.W((-200.0, 0.0, 1090.0))), (0.18, 0.60)),
                   ("graphite nut and lower seal", tuple(AB.W((0.0, -30.0, 1090.0))), (0.60, 0.70))])
    c.step(cap, 1.6, r2.line_to(rig.key_tcp(world=rig.key_model(1080.0))))
    c.gauges(**{"F/T 2": "Fz +3 N up (assumed)"})
    c.step(cap, 1.2, r2.line_to(rig.key_tcp(world=rig.key_model(1095.5))))
    cap = ("Thread finding, as a person does it: a light push up, the nut turned backwards until it drops onto the "
           "thread's start, then forward. Torque that rises in the first turn would mean a crossed thread: back off.")
    c.step(cap, 1.0, lambda u: rig.sock(-120.0 * u))
    c.step(cap, 0.2, r2.line_to(rig.key_tcp(world=rig.key_model(1096.0))), hold=0.3)
    run = 6.5
    cap = (f"The key's motor runs the nut up {run:g} turns, 2.0 mm a turn ({run * PITCH:.0f} mm), the arm rising "
           "with it. Arm 1 holds the crucible still and reads the thread's drag.")

    def run_up(u):
        rig.sock(-120.0 + 360.0 * run * u)
        c.gauges(Nut=f"{run * u:.1f} turns on", **{"F/T 1": "Mz 0.03 N m (drag)"})
    c.step(cap, 5.0, both(r2.line_to(rig.key_tcp(world=rig.key_model(1096.0 + run * PITCH))), run_up), hold=0.3)
    # 6 ------------------------------------------------------------------------ TC hole to the port, snug
    c.k = 6
    cap = (f"Before the nut is tight, arm 1 turns the crucible {ALIGN_DEG:.0f} deg clockwise so its thermocouple "
           "hole comes to the port at the back right; the key holds the nut, so the joint draws up 0.5 mm (SOP 3).")
    c.step(cap, 1.0, lambda u: AA.set_cut(sc, 1.0 - u, [g("crucible"), g("tc"), g("furnace")]), cam_to=C_FUR2,
           labels=[("thermocouple hole", tuple(AB.W((*(33.1 * np.array([math.cos(math.radians(M.TC_ANGLE
                                                                                         + ALIGN_DEG)),
                                                                          math.sin(math.radians(M.TC_ANGLE
                                                                                                + ALIGN_DEG))])),
                                                     M.RIM + 20.0))), (0.30, 0.25)),
                   ("port, back right", tuple(AB.W((*(80.0 * np.array([math.cos(math.radians(M.TC_ANGLE)),
                                                                        math.sin(math.radians(M.TC_ANGLE))])),
                                                    M.BODY_TOP + 10.0))), (0.70, 0.22))])

    def align(u):
        c.gauges(**{"TC hole": f"{M.TC_ANGLE + ALIGN_DEG * (1 - u):.0f} deg (port at {M.TC_ANGLE:.0f} deg)",
                    "F/T 1": f"Mz {0.04 + 0.08 * u:.2f} N m"})
    rot = turn_path(r1, AB.W((0.0, 0.0, M.RIM)), -ALIGN_DEG)
    c.step(cap, 2.0, both(rot, align, r2.line_to(rig.key_tcp(world=rig.key_model(1096.0 + run * PITCH + 0.5)))),
           hold=0.4)
    cap = (f"Snug: the key turns the nut the last {0.15 * 360:.0f} deg to the torque limit, {TQ_NUT:.2f} N m "
           f"(assumed: our bench-test start value), read by arm 1's {FT} through the crucible. Then it stops.")

    def snug(u):
        rig.sock(-120.0 + 360.0 * (run + 0.15 * u))
        tq = 0.04 + (TQ_NUT - 0.04) * u ** 2
        c.gauges(Nut=f"{run + 0.25 + 0.15 * u:.2f} turns: snug" if u > 0.98 else f"{run + 0.25 + 0.15 * u:.2f} turns",
                 **{"F/T 1": f"Mz {tq:.2f} N m" + (" (limit: stop)" if u > 0.98 else "")})
    c.step(cap, 1.0, lambda u: AA.set_cut(sc, u, rig.fur_cut), cam_to=C_NUT)
    c.step(cap, 1.6, both(r2.line_to(rig.key_tcp(world=rig.key_model(1109.8))), snug), hold=0.6, still=True)
    # 7 ------------------------------------------------------------------------ the key out, the gripper off
    c.k = 7
    cap = ("The key lets go: it drops 16 mm so the pins and the cup clear the nut, and goes out through the door. "
           "Arm 1 opens its jaws and lifts the gripper off; the crucible stays on its thread.")
    for grp in ("nut", "seal"):
        r2.reparent(g(grp), "rp")
    c.step(cap, 0.8, r2.line_to(rig.key_tcp(world=rig.key_model(1092.0))))
    swap(r1, g("crucible"))
    c.step(cap, 0.6, lambda u: rig.cg_jaws(u))
    c.give(r1, "cr:cg", "rp")
    c.gauges(**{"F/T 1": "", "F/T 2": "", "Nut": f"snug, {TQ_NUT:.2f} N m"})
    c.step(cap, 1.4, both(r2.line_to(rig.key_tcp(world=rig.key_model(1080.0))), r1.line_to(up(r1.tcp_world(), 90.0))))
    c.step(cap, 1.4, both(r2.line_to(rig.key_tcp(world=k_door)), lambda u: AA.set_cut(sc, 1.0 - u, rig.fur_cut)),
           cam_to=C_WIDE)
    c.stow(r1, "cg", cap)
    c.step(cap, 2.0, r2.joint_to(Tw=up(Gk, 110.0)))
    c.step(cap, 0.8, r2.line_to(Gk))
    r2.release("amrB")
    sc.gmat["cr:key"] = CT.key_rack_pose()
    c.step(cap, 0.3, r2.grip_to(0.0))
    c.step(cap, 0.8, both(r2.line_to(back(r2.tcp_world(), 100.0))))
    # 8 ------------------------------------------------------------------------ insulation, thermocouple
    c.k = 8
    cap = ("The side tube down over the crucible on the needle tool (0.6 mm inside, 1 mm to the coil), then the top "
           "ring. In the model the thermocouple runs through the top ring, so it goes in last (SOP: side, TC, top).")
    c.fetch(r1, "nt", cap, cam=C_MIR1)
    for name, face in (("side_ins", M.RIM), ("top_ins", 1341.0)):
        src = sc.world(g(name))
        Gs = rig.tool_tcp("cr:nt", CT.NT_HANDLE, world=src @ T((0.0, 0.0, face)) @ TURN)
        c.step(cap, 1.6, r1.joint_to(Tw=up(Gs, 90.0)), cam_to=C_MIR1)
        c.step(cap, 0.8, r1.line_to(Gs))
        c.take(r1, g(name))
        c.step(cap, 0.3, lambda u: sc.show(sc.members("cr:nt_needles"), u))
        c.step(cap, 1.0, r1.line_to(up(r1.tcp_world(), 150.0)))
        Gd = rig.tool_tcp("cr:nt", CT.NT_HANDLE, world=AB.WT(T((0.0, 0.0, face))) @ TURN)
        lift = 175.0 if name == "side_ins" else 70.0
        c.step(cap, 2.0, joint_w3(r1, up(Gd, lift), then=Gd), cam_to=C_FUR)
        c.step(cap, 1.6 if name == "side_ins" else 1.0, r1.line_to(Gd))
        c.step(cap, 0.3, lambda u: sc.show(sc.members("cr:nt_needles"), 1.0 - u))
        c.give(r1, "cr:nt", "rp")
        sc.gmat[g(name)] = np.eye(4)
        c.step(cap, 0.8, r1.line_to(up(r1.tcp_world(), 120.0)))
    c.stow(r1, "nt", cap, cam=C_MIR1)
    cap = ("The thermocouple back in: down through the top ring's hole into the crucible's wall hole, now at the "
           "back right. Without it the HMI raises \"master temperature sensor\" (T1 38:06).")
    c.fetch(r1, "tw", cap, cam=C_MIR1)
    Gt_src = rig.tool_tcp("cr:tw", CT.TW_HANDLE, world=tw_on_tc(sc.world(g("tc"))))
    c.step(cap, 1.6, r1.joint_to(Tw=up(Gt_src, 90.0)), cam_to=C_MIR1)
    c.step(cap, 0.7, r1.line_to(Gt_src))
    c.step(cap, 0.3, rig.tw_close_to(r1, 3.8))
    tw_tool = c.take(r1, g("tc"))
    c.step(cap, 1.0, r1.line_to(up(r1.tcp_world(), 100.0)))
    Gt = AB.WT(np.eye(4)) @ np.linalg.inv(sc.world(g("tc"))) @ r1.tcp_world()
    c.step(cap, 1.8, joint_w3(r1, up(Gt, TC_PULL), then=Gt), cam_to=C_FUR)
    c.gauges(**{"F/T 1": "push 0.5 N (stop at 2 N: the sheath cracks; assumed)"})
    c.step(cap, 1.4, r1.line_to(Gt))
    c.step(cap, 0.3, rig.tw_close_to(r1, 20.0))
    c.give(r1, tw_tool, "rp")
    sc.gmat[g("tc")] = np.eye(4)
    c.gauges(**{"F/T 1": ""})
    c.step(cap, 0.5, r1.line_to(up(r1.tcp_world(), 90.0)))
    c.stow(r1, "tw", cap, cam=C_MIR1)
    # 9 ------------------------------------------------------------------------ the rod, the lever, the pin
    c.k = 9
    cap = ("The sealing rod by its adapter, lowered until the force rises a little and the ball centres on the "
           "nozzle; the lever down onto it, the pin in, and SEALING ROD down (a PLC input: AMAZEMET would have to "
           "allow it).")
    src = sc.world(g("rod"))
    Gr = tcp_down((0.0, 0.0, ROD_GRIP_Z), ROD_SPIN)
    Gr_src = src @ np.linalg.inv(AB.WT(np.eye(4))) @ Gr
    c.step(cap, 1.6, both(r1.joint_to(Tw=back(Gr_src, 100.0)), r1.grip_to(0.0)), cam_to=C_MIR1)
    c.step(cap, 0.7, r1.line_to(Gr_src))
    c.step(cap, 0.3, r1.grip_to(GRIP_ROD))
    r1.grasp(g("rod"))
    c.step(cap, 1.2, r1.line_to(up(r1.tcp_world(), 140.0)))
    c.step(cap, 2.0, joint_w3(r1, up(Gr, 180.0), then=Gr), cam_to=C_FUR)
    c.gauges(**{"F/T 1": "Fz -1.5 N on the seat (assumed)"})
    c.step(cap, 1.8, r1.line_to(Gr))
    r1.release(g("arm_base"))
    sc.gmat[g("rod")] = np.eye(4)
    c.step(cap, 0.3, r1.grip_to(0.0))
    c.gauges(**{"F/T 1": ""})
    c.step(cap, 0.5, r1.line_to(back(r1.tcp_world(), 100.0)))
    lev_g = tcp_down((AA.LEVER_AT, 0.0, M.Z_ARM), 90.0)
    piv_w = tuple(AB.W(M.PIVOT))

    def lev_pose(u):
        return R(tuple(M.LEVER_AXIS), LEVER_UP * (1.0 - u), piv_w) @ lev_g
    g_up = lev_pose(0.0)
    q_lev = AA.arc_branch(r1, sc, g_up, lev_pose, lambda u: AA.lever(sc, LEVER_UP * (1.0 - u)), GRIP_LEVER,
                          ("holder_arm",), back=100.0)
    c.step(cap, 1.5, r1.joint_to(q1=r1.solve(up(g_up, 110.0), q_lev)), cam_to=C_FUR2)
    c.step(cap, 0.6, r1.line_to(g_up))
    c.step(cap, 0.3, r1.grip_to(GRIP_LEVER))
    r1.events.append((sc.n, "grasp", g("arm"), None))
    arc = AA.follow(r1, [lev_pose(u) for u in np.linspace(0.0, 1.0, 12)])
    c.step(cap, 1.6, both(arc, lambda u: AA.lever(sc, LEVER_UP * (1.0 - u))))
    c.step(cap, 0.3, r1.grip_to(0.0))
    r1.events.append((sc.n, "release", g("arm"), None))
    c.step(cap, 0.5, r1.line_to(back(r1.tcp_world(), 100.0)))
    # the pin from its rest into the eye
    src = sc.world("cr:pin")
    pin_g = np.array([0.0, CT.PIN_GRIP_Y, M.Z_ARM])
    Gp = tcp_down(pin_g, 180.0)
    Gp_src = src @ np.linalg.inv(sc.world(g("arm"))) @ Gp
    c.step(cap, 1.6, both(r1.joint_to(Tw=back(Gp_src, 90.0)), r1.grip_to(0.0)), cam_to=C_MIR1)
    c.step(cap, 0.7, r1.line_to(Gp_src))
    c.step(cap, 0.3, r1.grip_to(GRIP_PIN))
    r1.grasp("cr:pin")
    c.step(cap, 0.8, r1.line_to(up(r1.tcp_world(), 90.0)))
    Gp_out = T((0.0, -48.0, 0.0)) @ Gp
    c.step(cap, 1.8, r1.joint_to(Tw=Gp_out), cam_to=C_FUR2)
    c.step(cap, 0.9, r1.line_to(Gp))
    r1.release(g("arm"))
    sc.gmat["cr:pin"] = np.eye(4)
    c.step(cap, 0.3, r1.grip_to(0.0))
    c.step(cap, 0.5, r1.line_to(back(r1.tcp_world(), 90.0)))
    c.gauges(**{"SEALING ROD": "down (PLC input; or the arm on the HMI key)"})
    c.step(cap, 0.8, lambda u: AA.rod_lift(sc, -1.5 * u), hold=0.4)
    c.gauges(Furnace="rebuilt: next, the stack, the charge, the lid (leak check)")
    c.step(cap, 1.0, r1.line_to(up(r1.tcp_world(), 120.0)), hold=1.4, cam_to=C_FUR2)
    return AB.finish(sc)


def c_stow_first(c, rb):
    """The first sub-step of stowing the needle tool, as an update to run beside arm 2's move."""
    rig = c.rig
    grp, _, z = TOOLS1["nt"]
    dest = rig.mir_local(rig.ma, rig.at1("nt", z))
    G = rig.tool_tcp(grp, HANDLE["nt"], world=dest)
    c._stow_G = G
    return rb.joint_to(Tw=up(G, 230.0))


def c_stow_rest(c, rb):
    rig, sc = c.rig, c.sc
    grp, _, z = TOOLS1["nt"]
    cap = sc.caption
    c.step(cap, 0.8, rb.line_to(c._stow_G))
    rb.release("amr")
    sc.gmat[grp] = rig.at1("nt", z)
    c.step(cap, 0.3, rb.grip_to(0.0))
    c.step(cap, 0.5, rb.line_to(back(rb.tcp_world(), 90.0)))


# ---------------------------------------------------------------------------------------------- bill of materials
ROBOTIQ_FT = ("https://blog.robotiq.com/hubfs/Product-sheets/FT%20300/ur/Product_sheet-FT300S_FC_EN.pdf")
ATI_AXIA = "https://www.ati-ia.com/Library/documents/Axia80_Flyer.pdf"
SCHMALZ_SNG = ("https://media.schmalz.com/MAM_Library/Dokumente/Datenblatt_Artikel/1/100/10012900001/"
               "eea1348ed8b8_Datasheet_Article_10.01.29.00001_en-EN.pdf")
BOM = [
    dict(item="Force/torque sensor between flange and 2F-85, one per arm", maker="Robotiq", part_no="FT 300-S",
         qty=2, unit_usd=None, source=ROBOTIQ_FT,
         for_="reading 'snug' on graphite: Mz noise 0.003 N m against the UR10e's own +-0.5 N m torque accuracy "
              "(notes/crucible_automation.md); not drawn on the arms (it adds about 37 mm)", status="to buy"),
    dict(item="Force/torque sensor (alternative), 8 N m calibration", maker="ATI Industrial Automation",
         part_no="Axia80-M20", qty=0, unit_usd=None, source=ATI_AXIA,
         for_="alternative to the FT 300-S: Tz resolution 0.005 N m, 20 or 8 N m ranges (ATI flyer)", status="to buy"),
    dict(item="Needle gripper head, 4 needles 0.8 mm, 3 mm stroke, 30 deg, 4-6 bar", maker="Schmalz",
         part_no="SNG-M 4 0.8 (10.01.29.00001)", qty=4, unit_usd=None, source=SCHMALZ_SNG,
         for_="the needle tool: lifts the top ring, side tube and bottom ring by their top faces", status="to buy"),
    dict(item="Needle tool body: hub r 58, stem, 28 mm handle", maker="ours", part_no=None, qty=1, unit_usd=None,
         source="atom_crucible_tools.nt_meshes", for_="carries the four needle heads; 1-2 mm off the coil",
         status="ours: to make"),
    dict(item="Solenoid valve, air line and 4-6 bar supply for the needle heads", maker=None, part_no=None, qty=1,
         unit_usd=None, source="Schmalz datasheet (operating pressure)", for_="the needle tool on MiR250 1",
         status="to buy"),
    dict(item="Crucible gripper: top plate, three jaws with 2 mm silicone pads, wedge driven by the 2F-85's squeeze",
         maker="ours", part_no=None, qty=1, unit_usd=None, source="atom_crucible_tools.cg_meshes",
         for_="holds the crucible's outside, top 38 mm, 1.5 mm jaw stroke; inside r 46 (coil at r 60)",
         status="ours: to make"),
    dict(item="Tweezers tool: two 1.5 mm jaws with PEEK tips on a flexure handle", maker="ours", part_no=None, qty=1,
         unit_usd=None, source="atom_crucible_tools.tw_meshes", for_="the 16 mm nozzle into the holder",
         status="ours: to make"),
    dict(item="Nut key: 300 mm bar, gear head, turning socket with six pins and a captive cup", maker="ours",
         part_no=None, qty=1, unit_usd=None, source="atom_crucible_tools.key_meshes",
         for_="holds and turns the 60 x 12 mm graphite nut through the chamber's door; keeps the nut and seal",
         status="ours: to make"),
    dict(item="Small DC gearmotor with encoder, about 1 N m", maker=None, part_no=None, qty=2, unit_usd=None,
         source="to choose", for_="one turns the key's socket (7 turns out, 6.9 in), one the holder fixture "
         "(1.25 turns); the encoders count turns", status="to buy"),
    dict(item="Bevel gear pair 1:1, module 0.5", maker=None, part_no=None, qty=1, unit_usd=None, source="to choose",
         for_="the key's gear head under the socket", status="to buy"),
    dict(item="Crucible cradle with a white LED under the nozzle", maker="ours", part_no=None, qty=1, unit_usd=None,
         source="atom_crucible_tools.fixtures1", for_="carries the crucible on MiR250 1; backlight for the nozzle check",
         status="ours: to make"),
    dict(item="Holder fixture: block with a shank bore, two soft jaws, turned by a gearmotor underneath",
         maker="ours", part_no=None, qty=1, unit_usd=None, source="atom_crucible_tools.fixtures1",
         for_="clamps the nozzle holder's shank and turns the holder onto the crucible, which arm 1 holds still",
         status="ours: to make"),
    dict(item="Small pneumatic parallel gripper for the holder fixture's jaws", maker="SMC", part_no="MHZ2-20D (e.g.)",
         qty=1, unit_usd=None, source="to confirm", for_="closes the fixture's soft jaws on the shank",
         status="to buy"),
    dict(item="Seats for the three insulation pieces, rod holder, thermocouple stand, pin rest, nozzle tray",
         maker="ours", part_no=None, qty=1, unit_usd=None, source="atom_crucible_tools.fixtures1",
         for_="MiR250 1's cabinet top", status="ours: to make"),
    dict(item="Spare graphite set: crucible, nozzle holder, nozzles, nuts, seals", maker="AMAZEMET", part_no=None,
         qty=1, unit_usd=None, source="ask AMAZEMET (notes/crucible_automation.md: no price found)",
         for_="the bench tests (snug and breaking torque) and a swap when one cracks", status="to buy"),
    dict(item="Peak-hold torque gauge with adapters for the nut and the crucible", maker=None, part_no=None, qty=1,
         unit_usd=None, source="to choose", for_="measuring what hands do: snug and breakaway torques",
         status="to buy"),
    dict(item="Bench rig plate with the furnace floor's and top plate's holes", maker="ours", part_no=None, qty=1,
         unit_usd=None, source="notes/atom_crucible.md", for_="50+ thread-finding trials before the machine",
         status="ours: to make"),
]


def write_bom():
    out = AB.OUT / "atom"
    out.mkdir(parents=True, exist_ok=True)
    rows = [{("for" if k == "for_" else k): v for k, v in r.items()} for r in BOM]
    (out / "crucible_bom.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    print("wrote", out / "crucible_bom.json", len(rows))


if __name__ == "__main__":
    if os.environ.get("CRUCIBLE_BOM"):
        write_bom()
    elif CLIP == "out":
        clip_out()
    else:
        clip_in()

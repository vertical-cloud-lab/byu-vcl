"""The furnace lid's draw latch, unclamped after a run and clamped again before the next (PR #353, #303).

Sterling (PR #318, 2026-11-19): "it doesn't seem like you actually used the heat chamber latch correctly (i.e., actually
clamping it down and then unclamping it)". The latch here is the third pass's (notes/repowder_refine.md, T4 5:29.5-5:41):
a lever pivoting at its top that hangs flat over a base, a wire loop on its own pivot on the lever, hooked on a keeper on
the lid, and the machine's pneumatic bolt through the base. Its parts are redrawn on the model's own joints
(atom_latch_tools.py says why: as drawn in model.py they pass through each other when the lever opens).

Unclamping (vented, the bolt back): arm 2 holds the lid down with its closed fingertips; arm 1 takes the lever's free
end and pulls it out and up about the top pivot, through dead centre to 150 deg; the loop goes slack and its bar rides
up the keeper; arm 2 takes the loop by its legs, lifts the bar off and lays the loop over the lever; arm 1 folds the
lever down; arm 1 swings the lid up and back by its knob, 105 deg about the back hinge. Clamping is the reverse, with
the over-centre curve and the seal's squeeze in an inset, then the bolt in at the pump-down and the leak check the
machine allows. ``ARM_AUDIT=1`` checks every frame; ``PREVIEW=1`` the last frame of each step.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import atom_base as AB                 # noqa: E402
import atom_latch_tools as LT          # noqa: E402
import alloy_atomize as AA             # noqa: E402
import robot as RB                     # noqa: E402
from scene import OUT, PREVIEW, AUDIT, T, R, window  # noqa: E402

M = AB.M
NAME = "atom_latch"
TITLE = "Vertical cloud lab: the furnace latch, unclamped and clamped"
A_AT = (460.0, -620.0, 0.0)            # MiR250 1 (arm 1), model frame: right of the furnace, so the arm reaches the
                                       # knob all the way to 105 deg and the lever all the way to 150 (IK search)
B_AT = (-560.0, -620.0, 0.0)           # MiR250 2 (arm 2): AB.PARK["front_left"]
LID_UP = 4.0 / M.LID_OPEN_DEG           # how far the lid opens here: in the model the lid's hinge leaf meets the blue
                                       # cabinet's front (y = 165) at 5 deg and the lid itself at 28.5 (FCL); the footage
                                       # shows it open ~105 deg, standing behind the furnace (T4 1:53, 2:28, 5:08)
LID_SPOTS = [(460.0, -620.0, 0.0), (450.0, -600.0, 20.0), (450.0, -600.0, 40.0), (500.0, -600.0, 40.0),
             (420.0, -650.0, 30.0), (550.0, -560.0, 45.0), (500.0, -625.0, -20.0), (380.0, -640.0, 45.0)]
LEVER_ALPHA = 35.0                     # arm 1's approach to the lever: in, and up 35 deg from level
GAP_LEVER = 52.0 + 0.8                 # the lever's flanges are 52 mm across: pads 0.4 mm off each
GAP_LEGS = 2 * (LT.LEG_X + LT.LEG_R) + 0.8
GAP_KNOB = 28.0 + 0.8                  # the lid's 28 mm ball knob
LID_KNOB_N = AA.LID_KNOB_N
F_PEAK = AA.LATCH_F["expected"]        # N at the lever's free end: chapter 2's estimate (Kipp K0080 cover latches)
F_STIFF = AA.LATCH_F["design"]
PRESS_F = AA.PRESS_F
STAB = {}


# ------------------------------------------------------------------------------------------------ the scene
def drop_actor(sc, name):
    a = sc.actors.pop(name, None)
    if a is not None:
        sc.pl.remove_actor(a)
    for d in (sc.group_of, sc.alpha, sc.base_alpha, sc.cutrole, sc.ghost_of, sc.color, sc.ambient):
        d.pop(name, None)


def swap_latch(sc):
    """The model's lever, loop, keeper and pin out; atom_latch_tools' in, on the same groups (and so the same joints)."""
    for part in ("latch_lever", "latch_loop", "latch_keeper", "latch_pin"):
        for n in [n for n in list(sc.actors) if n in (part, part + "#cut", "w:" + part)]:
            drop_actor(sc, n)
    for name, (mesh, col, grp) in LT.latch_meshes().items():
        sc.add("atl " + name, mesh, col, AB.g(grp), specular=0.4)


def joints_now(sc):
    return dict(getattr(sc, "joint_vals", {}))


def set_latch(sc, lever_deg, loop_val):
    AB.set_joints(sc, latch=lever_deg / M.LATCH_OPEN_DEG, loop=loop_val)


def ride_val(v):
    lv, dr = LT.ride(v)
    return (lv - 2.0 if lv > 1.0 else lv), dr


def model_pose(name, vals, G):
    """World pose of a grasp G (model frame, the part as built) on the part moved by joint `name` at vals."""
    return AB.WT(M.joint_world(name, vals) @ G)


def lever_pose(deg, G):
    return model_pose("latch", {"latch": deg / M.LATCH_OPEN_DEG}, G)


def loop_pose(deg, loop_val, G):
    return model_pose("loop", {"latch": deg / M.LATCH_OPEN_DEG, "loop": loop_val}, G)


def lid_pose(v, G):
    return model_pose("lid", {"lid": v}, G)


def knob_grasp_model():
    """The 2F-85 on the lid's ball knob (model frame, lid shut): pads either side of the ball across x, approaching
    down along the stalk (model.py hood_knob: kd), so the hand stands up and out of the lid's front."""
    kd = np.array([0.62, -0.15, 0.77])
    kd /= np.linalg.norm(kd)
    c = M.knob_centre() + kd * 5.0                  # 5 mm out along the stalk: the pads still span the 28 mm ball
    _, n_f = M.facet_plane(M.LID, "front", 0.12)    # the lid's front facet, where the stalk stands
    z = -kd
    x = np.cross(z, n_f)                            # fingers close level with the facet, so neither dips into it
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = x, y, z, c
    return Mx


def pick_branch(rb, sc, poses, move, close, skip, back=100.0, n_chk=14, score=False):
    """The IK solution at poses[0] from which the arm follows every pose (dense, as AA.follow does: 6 mm steps, no
    joint over 20 deg in a step), with the fewest collisions along the way (move(u) puts the part where it is at u;
    hits on actors named in `skip` are the grasp itself), clear to back off `back` mm: its joints, or the nearest."""
    import collide
    from scipy.spatial.transform import Rotation, Slerp
    dense = []
    for A0, A1 in zip(poses[:-1], poses[1:]):
        sl = Slerp([0.0, 1.0], Rotation.from_matrix(np.stack([A0[:3, :3], A1[:3, :3]])))
        k = max(4, int(np.linalg.norm(A1[:3, 3] - A0[:3, 3]) / 6.0))
        for s in np.linspace(0, 1, k, endpoint=False):
            Mx = np.eye(4)
            Mx[:3, :3] = sl([s]).as_matrix()[0]
            Mx[:3, 3] = A0[:3, 3] + (A1[:3, 3] - A0[:3, 3]) * s
            dense.append(Mx)
    dense.append(poses[-1])
    chk = rb.checker()
    Tb = AA.inv(sc.world(rb.root)) @ poses[0]
    cands = collide.ik_all(rb.model, Tb, rb.q) or [rb.solve(poses[0])]
    best, best_score = None, None
    for q in cands:
        qq, path, ok = q.copy(), [q.copy()], True
        for Mx in dense[1:]:
            try:
                qn = rb.solve(Mx, qq)
            except ValueError:
                ok = False
                break
            if np.abs(qn - qq).max() > math.radians(20):
                ok = False
                break
            qq = qn
            path.append(qq)
        if not ok:
            continue
        hits = 0
        for i in np.linspace(0, len(path) - 1, n_chk).astype(int):
            move(i / max(len(path) - 1, 1))
            hits += sum(1 for h in chk.collisions(path[i], close, chk.snapshot()) if not any(k in h[2] for k in skip))
        move(0.0)
        try:
            qb = rb.solve(poses[0] @ T((0, 0, -back)), q)
            hits += 3 * len(chk.collisions(qb, 0.0, chk.snapshot()))
        except ValueError:
            hits += 50
        if best_score is None or hits < best_score:
            best, best_score = q, hits
        if hits == 0:
            break
    if best is None:
        print(f"warning: {sc.label}: no IK branch follows the arc", flush=True)
        return (cands[0], 999) if score else cands[0]
    if best_score and not score:
        print(f"warning: {sc.label}: best IK branch has {best_score} hit(s) on the arc", flush=True)
    return (best, best_score) if score else best


def press_pose(rb, gap=0.8):
    """Arm 2's shut fingertips on the lid's top at AA.PRESS_AT, the tool leaning AA.PRESS_TILT away from its base."""
    base = rb.sc.world(rb.root)[:3, 3]
    p = AB.W((AA.PRESS_AT[0], AA.PRESS_AT[1], AA.HOOD_TOP + 40.0))
    h = p[:2] - base[:2]
    h /= np.linalg.norm(h)
    a = math.radians(AA.PRESS_TILT)
    import props as P
    Tw = P.tcp_frame(p, (h[0] * math.sin(a), h[1] * math.sin(a), -math.cos(a)), 90.0)
    Tw[2, 3] += AB.RP[2] + AA.HOOD_TOP + gap - AA.gripper_low(Tw, 1.0)
    return Tw


def force_curve():
    """Pull at the lever's free end vs lever angle (deg): the loop's tension, taken proportional to the squeeze past
    its set length, times its line's moment arm about the pivot, over the 133 mm to the toe; scaled so its peak is
    chapter 2's 100 N estimate. Positive: the lever resists opening (pulls it shut)."""
    P0 = LT.PIV
    out = []
    for d in np.linspace(0.0, M.LATCH_OPEN_DEG, 301):
        v = d / M.LATCH_OPEN_DEG
        Q = LT.loop_pivot(v)
        _, sq = LT.ride(v)
        u = (LT.HOOK - Q) / np.linalg.norm(LT.HOOK - Q)
        arm = float(np.cross(Q - P0, u)[0])       # about +x: + turns the free end inward (shut)
        out.append((float(d), sq * arm))
    k = F_PEAK / max(abs(t) for _, t in out)
    return [(d, t * k / 1.0) for d, t in out]


FCURVE = force_curve()


def pull_at(deg):
    return float(np.interp(deg, [d for d, _ in FCURVE], [f for _, f in FCURVE]))


# ------------------------------------------------------------------------------------------------ the clip
def main():
    sc, ma, mb = AB.build(NAME, TITLE)
    swap_latch(sc)
    AB.mir_at(ma, A_AT)
    AB.mir_at(mb, B_AT)
    rb, rbB = ma.rb, mb.rb
    AB.set_joints(sc, lid=0.0, latch=0.0, loop=0.0, bolt=0.0, door=0.0, clamp0=0.0, clamp1=0.0)
    state = dict(inset=False, deg=0.0, sq=0.0, taut=True)
    orig_overlay = sc.overlay

    def overlay(img, scale, anchors):
        img = orig_overlay(img, scale, anchors)
        if state["inset"]:
            LT.inset(img, state["deg"], LT.draw_mm(state["deg"] / M.LATCH_OPEN_DEG), state["sq"], state["taut"],
                     scale=scale)
        return img
    sc.overlay = overlay

    def latch_state(deg, loop_val, sq=None):
        set_latch(sc, deg, loop_val)
        state["deg"] = deg
        if sq is None:
            _, sq = ride_val(deg / M.LATCH_OPEN_DEG)
        state["sq"] = sq
        state["taut"] = deg <= LT.theta_taut() + 1e-6 and abs(loop_val - ride_val(deg / M.LATCH_OPEN_DEG)[0]) < 1e-6

    def rows(**kw):
        base = dict(Furnace=None, Lever=None, Loop=None, Seal=None, Pull=None, Bolt=None, Arm_1=None, Arm_2=None)
        base.update(kw)
        AB.caption_rows(sc, **base)

    # cameras (model frame)
    CAM_WIDE = AB.cam((1250, -2350, 2050), (-60, -330, 1150))
    CAM_LATCH = AB.cam((190, -730, 1170), (72, -165, 1320))
    CAM_LATCH2 = AB.cam((-70, -640, 1220), (72, -168, 1340))
    CAM_LID = AB.cam((-950, -1750, 2150), (60, 40, 1400))
    sc.cam = CAM_WIDE

    th_taut = LT.theta_taut()
    dc = max(LT.toggle_curve(), key=lambda t: t[1])
    peak_f = max(FCURVE, key=lambda t: t[1])

    # ---------------------------------------------------------------- 1. vent, bolt back
    rows(Furnace="cooling, 150 mbar Ar", Lever="shut", Loop="on the keeper", Seal="squeezed", Bolt="in (locked)",
         Arm_1="parked", Arm_2="parked")
    lab_pts = dict(lever=AB.W((LT.LX + 30, -160, 1240)), loop=AB.W((LT.LX - 34, -147, 1345)),
                   keeper=AB.W((LT.LX - 20, -146, 1395)), bolt=AB.W((150, LT.BOLT_Y, LT.BOLT_Z)))
    cap = ("After a run: below 400 C the operator turns off Melting Pressure and Pressure Control and presses Vent "
           "Valve (DAL SOP, Cooldown 2-3). The furnace's lid is held by a draw latch and a pneumatic bolt.")
    sc.step("1/9", cap, 2.4, None, hold=0.8, cam_to=CAM_LATCH,
            labels=[("lever: pivots at its top", tuple(lab_pts["lever"]), (0.80, 0.62)),
                    ("loop on the keeper", tuple(lab_pts["loop"]), (0.10, 0.42)),
                    ("keeper (on the lid)", tuple(lab_pts["keeper"]), (0.12, 0.22)),
                    ("pneumatic bolt", tuple(lab_pts["bolt"]), (0.82, 0.38))])

    def vent(u):
        p = 150.0 * (1.0 - window(u, 0.0, 0.6))
        rows(Furnace=f"venting, {p:.0f} mbar" if p > 1 else "at atmosphere", Bolt="in (locked)" if u < 0.65 else
             "back (released)")
        AB.set_joints(sc, bolt=window(u, 0.65, 1.0))
    cap = ("At atmosphere the bolt goes back: it locks the lever whenever the furnace is pumped or pressurised "
           "(Kalicki, AMAZEMET, install call 22:04). Its release on venting is our reading of that, not seen in a video.")
    sc.step("1/9", cap, 3.0, vent, hold=0.6,
            labels=[("bolt back: lever free", tuple(AB.W((150, LT.BOLT_Y, LT.BOLT_Z))), (0.82, 0.38))])

    # ---------------------------------------------------------------- 2. arm 2 presses, arm 1 takes the lever
    press = press_pose(rbB)
    pre_press = T((0, 0, 60)) @ press
    rows(Arm_2="to the lid's top")
    cap = (f"Arm 2 holds the lid down with its closed fingertips, about {PRESS_F:.0f} N, as the operator's palm does "
           "(T4 5:17-5:24): the lid can't jump when the latch lets go.")
    sc.step("2/9", cap, 2.6, AB.both(rbB.joint_to(Tw=pre_press), rbB.grip_to(1.0)), hold=0.1, cam_to=CAM_WIDE)
    sc.step("2/9", cap, 1.0, rbB.line_to(press), hold=0.3,
            labels=[(f"arm 2 presses, ~{PRESS_F:.0f} N", tuple(press[:3, 3] + (0, 0, 40)), (0.20, 0.20))])
    q_press = rbB.q.copy()
    rows(Arm_2=f"pressing, ~{PRESS_F:.0f} N")

    G_lever = LT.lever_grasp(LEVER_ALPHA)
    g0 = lever_pose(0.0, G_lever)
    c_lever = LT.close_for_gap(GAP_LEVER)
    arc_open = [lever_pose(d, G_lever) for d in np.linspace(0.0, 150.0, 31)]

    def lever_move(u):
        d = 150.0 * u
        v = d / M.LATCH_OPEN_DEG
        set_latch(sc, d, ride_val(v)[0])
    q_lev = pick_branch(rb, sc, arc_open, lever_move, c_lever, ("atl latch_lever", "atl latch_loop"), back=100.0)
    lever_move(0.0)
    pre_lev = g0 @ T((0, 0, -100))
    rows(Arm_1="to the lever's free end")
    cap = (f"Arm 1 takes the lever near its free end, the 2F-85's pads on its two side flanges, {LT.TOE_ARM:.0f} mm "
           "below the pivot. The lever pivots at its top and hangs flat over its base (T4 5:35.5).")
    sc.step("3/9", cap, 2.6, AB.both(rb.joint_to(q1=rb.solve(pre_lev, q_lev)), rb.grip_to(0.15)), hold=0.1,
            cam_to=CAM_LATCH)
    sc.step("3/9", cap, 1.0, rb.line_to(g0), hold=0.1)
    sc.step("3/9", cap, 0.5, rb.grip_to(c_lever), hold=0.3)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    q_grab = rb.q.copy()

    # ---------------------------------------------------------------- 3. over centre, open
    path_a = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(0.0, 45.0, 10)])
    state["inset"] = True

    def open_a(u):
        path_a(u)
        d = 45.0 * u
        lv, sq = ride_val(d / M.LATCH_OPEN_DEG)
        latch_state(d, lv, sq)
        rows(Lever=f"{d:5.1f} deg", Loop="taut on the keeper" if d <= th_taut else "slack",
             Seal=f"squeeze {sq:+.2f} mm" if d <= th_taut else "free", Pull=f"{max(pull_at(d), 0):5.0f} N")
    cap = (f"Out and up about the top pivot. The loop's pivot first draws away from the hook: the seal is squeezed "
           f"{dc[1]:.2f} mm more at dead centre, {dc[0]:.0f} deg out; the pull peaks just before it, about "
           f"{F_PEAK:.0f} N (estimate; {F_STIFF:.0f} N if stiff), and is zero there.")
    sc.step("4/9", cap, 4.5, open_a, hold=0.4, cam_to=CAM_LATCH2)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    path_b = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(45.0, 150.0, 22)])

    def open_b(u):
        path_b(u)
        d = 45.0 + 105.0 * u
        lv, sq = ride_val(d / M.LATCH_OPEN_DEG)
        latch_state(d, lv, sq)
        rows(Lever=f"{d:5.1f} deg", Loop="slack: the bar rides up the keeper", Seal="free", Pull="lever's weight")
    cap = (f"Past {th_taut:.0f} deg the loop is slack. Its pivot comes back towards the hook, so the rigid loop pushes "
           "its bar up the keeper's plate. The lever stands up and out, about 150 deg (T4 5:32-5:34).")
    sc.step("4/9", cap, 3.2, open_b, hold=0.4)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))

    # ---------------------------------------------------------------- 4. arm 2 lifts the loop off onto the lever
    G_legs = LT.legs_grasp()
    ride150 = ride_val(1.0)[0]
    # the legs' grasp is defined on the loop as built; at the lever's 150 deg the loop is at ride150
    c_legs = LT.close_for_gap(GAP_LEGS)

    def loop_move(u):
        set_latch(sc, 150.0, ride150 + (LT.on_web() - ride150) * u)
    g_legs = loop_pose(150.0, ride150, G_legs)
    q_legs = pick_branch(rbB, sc, [loop_pose(150.0, ride150 + (LT.on_web() - ride150) * s, G_legs)
                                   for s in np.linspace(0, 1, 12)], loop_move, c_legs, ("atl latch_loop",), back=90.0)
    loop_move(0.0)
    rows(Arm_2="to the loop", Pull="holding the lever up")
    cap = ("Arm 2 lets go of the lid, which now sits free, and takes the loop by its two legs from outside, so the "
           "fingers stay clear of the lever and the keeper.")
    sc.step("5/9", cap, 0.8, rbB.line_to(T((0, 0, 60)) @ press), hold=0.05)
    sc.step("5/9", cap, 2.4, AB.both(rbB.joint_to(q1=rbB.solve(g_legs @ T((0, 0, -90)), q_legs)),
                                     rbB.grip_to(0.10)), hold=0.1)
    sc.step("5/9", cap, 0.9, rbB.line_to(g_legs), hold=0.05)
    sc.step("5/9", cap, 0.4, rbB.grip_to(c_legs), hold=0.2)
    rbB.events.append((sc.n, "grasp", AB.g("latch_loop"), None))
    path_l = AA.follow(rbB, [loop_pose(150.0, ride150 + (LT.on_web() - ride150) * s, G_legs)
                             for s in np.linspace(0, 1, 12)])

    def lift_off(u):
        path_l(u)
        loop_move(u)
    cap = ("It lifts the bar off the keeper and lays the loop over the lever, as the hand does (T4 5:29.5-5:35, "
           "read backwards). The 2F-85 has one hand, so arm 1 holds the lever meanwhile.")
    sc.step("5/9", cap, 2.2, lift_off, hold=0.2,
            labels=[("loop lifted off the keeper", tuple(AB.W((LT.LX - 36, -175, 1395))), (0.12, 0.30))])
    rbB.events.append((sc.n, "grasp", AB.g("latch_loop"), None))
    sc.step("5/9", cap, 0.4, rbB.grip_to(0.10), hold=0.05)
    rbB.events.append((sc.n, "release", AB.g("latch_loop"), None))
    sc.step("5/9", cap, 0.8, rbB.line_to(rbB.tcp_world() @ T((0, 0, -90))), hold=0.05)
    rows(Loop="over the lever", Arm_2="parked")
    sc.step("5/9", cap, 1.8, rbB.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.1)

    # ---------------------------------------------------------------- 5. arm 1 folds the lever down
    path_c = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(150.0, 0.0, 31)])
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    state["inset"] = False

    def fold(u):
        path_c(u)
        d = 150.0 * (1.0 - u)
        latch_state(d, LT.on_web())
        rows(Lever=f"{d:5.1f} deg", Pull=None, Seal=None)
    cap = "Arm 1 folds the lever back down, flat, with the loop hanging over it (T4 5:08: the lid open, the loop dangling)."
    sc.step("6/9", cap, 3.0, fold, hold=0.2, cam_to=CAM_LATCH)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    sc.step("6/9", cap, 0.4, rb.grip_to(0.15), hold=0.05)
    rb.events.append((sc.n, "release", AB.g("latch_lever"), AB.g("latch_loop")))
    sc.step("6/9", cap, 0.8, rb.line_to(g0 @ T((0, 0, -100))), hold=0.1)
    rows(Lever="folded", Loop="hanging over the lever", Arm_1="to the knob")

    # ---------------------------------------------------------------- 6. the lid up and back
    G_knob = knob_grasp_model()
    c_knob = LT.close_for_gap(GAP_KNOB)

    def lid_move(u):
        AB.set_joints(sc, lid=u)
    # MiR 1 moves to where its arm follows the knob all the way to 105 deg clear of the furnace (searched here: the
    # spot whose best IK branch has the fewest collisions along the arc)
    sc.step("7/9", "Arm 1 lets go and parks; MiR250 1 moves round for the lid.", 1.6,
            rb.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.05)
    home, q_home = (ma.x - AB.RP[0], ma.y - AB.RP[1], ma.yaw), rb.q.copy()
    best = None
    for spot in [home] + LID_SPOTS:
        AB.mir_at(ma, spot)
        rb.set(q_home)
        q, sco = pick_branch(rb, sc, [lid_pose(s, G_knob) for s in np.linspace(0, LID_UP, 12)],
                             lambda u: lid_move(LID_UP * u), c_knob, ("knob", "hood"), back=45.0, score=True)
        print("lid spot", spot, "hits", sco, flush=True)
        if best is None or sco < best[2]:
            best = (spot, q, sco)
        if sco == 0:
            break
    AB.mir_at(ma, home)
    rb.set(q_home)
    lid_spot, q_knob, _ = best
    lid_move(0.0)
    if lid_spot != home:
        drive, secs = AB.mir_drive(ma, lid_spot)
        sc.step("7/9", "MiR250 1 moves round for the lid.", secs, drive, hold=0.1)
    gk0 = lid_pose(0.0, G_knob)
    cap = (f"Arm 1 lifts the lid by its knob about its back hinge (T4 5:14.5-5:16.5, reversed), about {LID_KNOB_N:.0f} N "
           f"(chapter 2's estimate): it comes free. The footage has it open ~105 deg; in this model its hinge leaf "
           f"meets the blue cabinet after 5 deg, so here it lifts 4 deg (a model fault, reported).")
    sc.step("7/9", cap, 2.4, AB.both(rb.joint_to(q1=rb.solve(gk0 @ T((0, 0, -45)), q_knob)), rb.grip_to(0.2)),
            hold=0.1, cam_to=CAM_LID)
    sc.step("7/9", cap, 0.9, rb.line_to(gk0), hold=0.05)
    sc.step("7/9", cap, 0.4, rb.grip_to(c_knob), hold=0.1)
    rb.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    q_knob_g = rb.q.copy()
    path_lid = AA.follow(rb, [lid_pose(s, G_knob) for s in np.linspace(0, LID_UP, 12)])

    def lid_up(u):
        path_lid(u)
        lid_move(LID_UP * u)
        rows(Furnace=f"lid {105 * LID_UP * u:3.0f} deg")
    sc.step("7/9", cap, 2.4, lid_up, hold=1.2)
    q_top = rb.q.copy()
    rb.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    rows(Furnace="lid up, held: rebuild, charge (other clips)")
    sc.step("7/9", "Opened, the furnace is rebuilt and charged (the other clips in this series). Then the same steps, "
            "backwards, close it.", 0.6, None, hold=2.4)
    rb.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))

    # ---------------------------------------------------------------- 7. clamping: the lid down
    rows(Furnace="lid up, charged", Arm_1="lid down")
    cap = ("Clamping, after IPA on the seal and its face (DAL SOP, Loading the Furnace 8). Arm 1 brings the lid down by "
           "its knob onto the O-ring.")
    path_lid2 = AA.follow(rb, [lid_pose(s, G_knob) for s in np.linspace(LID_UP, 0, 12)])

    def lid_down(u):
        path_lid2(u)
        lid_move(LID_UP * (1.0 - u))
        rows(Furnace=f"lid {105 * LID_UP * (1 - u):3.0f} deg" if u < 1 else "lid down, not clamped")
    sc.step("8/9", cap, 2.4, lid_down, hold=0.2)
    rb.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    sc.step("8/9", cap, 0.4, rb.grip_to(0.2), hold=0.05)
    rb.events.append((sc.n, "release", AB.g("knob"), AB.g("hood")))
    sc.step("8/9", cap, 0.8, rb.line_to(gk0 @ T((0, 0, -45))), hold=0.05)
    sc.step("8/9", cap, 1.6, rb.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.05)
    drive, secs = AB.mir_drive(ma, A_AT)
    sc.step("8/9", "MiR250 1 goes back in front of the latch.", secs, drive, hold=0.1, cam_to=CAM_LATCH2)

    # arm 1 back to the lever: raises it to 150 deg with the loop lying on it
    rows(Arm_1="to the lever")
    cap = "Arm 1 takes the lever again and raises it to 150 deg; the loop rides up on it."
    sc.step("8/9", cap, 2.4, AB.both(rb.joint_to(q1=rb.solve(pre_lev, q_lev)), rb.grip_to(0.15)), hold=0.05,
            cam_to=CAM_LATCH2)
    sc.step("8/9", cap, 0.9, rb.line_to(g0), hold=0.05)
    sc.step("8/9", cap, 0.4, rb.grip_to(c_lever), hold=0.05)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    path_d = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(0.0, 150.0, 31)])

    def raise_(u):
        path_d(u)
        d = 150.0 * u
        latch_state(d, LT.on_web())
        rows(Lever=f"{d:5.1f} deg", Loop="over the lever")
    sc.step("8/9", cap, 3.0, raise_, hold=0.1)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))

    # arm 2 hooks the loop: over onto the keeper
    rows(Arm_2="to the loop")
    g_legs_w = loop_pose(150.0, LT.on_web(), G_legs)
    cap = ("Arm 2 takes the loop by its legs and lays its bar on the keeper's plate, above the ledge: hooking it on "
           "(T4 5:30-5:35).")
    sc.step("8/9", cap, 2.4, AB.both(rbB.joint_to(q1=rbB.solve(g_legs_w @ T((0, 0, -90)), q_legs)),
                                     rbB.grip_to(0.10)), hold=0.05)
    sc.step("8/9", cap, 0.9, rbB.line_to(g_legs_w), hold=0.05)
    sc.step("8/9", cap, 0.4, rbB.grip_to(c_legs), hold=0.05)
    rbB.events.append((sc.n, "grasp", AB.g("latch_loop"), None))
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    path_h = AA.follow(rbB, [loop_pose(150.0, LT.on_web() + (ride150 - LT.on_web()) * s, G_legs)
                             for s in np.linspace(0, 1, 12)])

    def hook_on(u):
        path_h(u)
        set_latch(sc, 150.0, LT.on_web() + (ride150 - LT.on_web()) * u)
    sc.step("8/9", cap, 2.2, hook_on, hold=0.1)
    rbB.events.append((sc.n, "grasp", AB.g("latch_loop"), None))
    sc.step("8/9", cap, 0.4, rbB.grip_to(0.10), hold=0.05)
    rbB.events.append((sc.n, "release", AB.g("latch_loop"), None))
    sc.step("8/9", cap, 0.8, rbB.line_to(rbB.tcp_world() @ T((0, 0, -90))), hold=0.05)
    rows(Loop="on the keeper's plate", Arm_2="to the lid's top")
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    cap = "Arm 2 presses the lid's top again, so the seal is squeezed evenly while the loop draws the lid down."
    sc.step("8/9", cap, 2.2, rbB.joint_to(q1=rbB.solve(pre_press, q_press)), hold=0.05, cam_to=CAM_WIDE)
    sc.step("8/9", cap, 0.9, rbB.line_to(press), hold=0.1)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    rows(Arm_2=f"pressing, ~{PRESS_F:.0f} N")

    # ---------------------------------------------------------------- 8. over centre, shut
    state["inset"] = True
    path_e = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(150.0, 45.0, 22)])

    def close_a(u):
        path_e(u)
        d = 150.0 - 105.0 * u
        lv, sq = ride_val(d / M.LATCH_OPEN_DEG)
        latch_state(d, lv, sq)
        rows(Lever=f"{d:5.1f} deg", Loop="slack: the bar slides down the keeper", Seal="free", Pull="lever's weight")
    cap = "Arm 1 swings the lever down. The loop's bar slides down the keeper's plate onto its ledge."
    sc.step("9/9", cap, 3.0, close_a, hold=0.2, cam_to=CAM_LATCH2)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    path_f = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(45.0, 0.0, 12)])

    def close_b(u):
        path_f(u)
        d = 45.0 * (1.0 - u)
        lv, sq = ride_val(d / M.LATCH_OPEN_DEG)
        latch_state(d, lv, sq)
        rows(Lever=f"{d:5.1f} deg", Loop="taut on the keeper" if d <= th_taut else "slack",
             Seal=f"squeeze {sq:+.2f} mm" if d <= th_taut else "free", Pull=f"{max(pull_at(d), 0):5.0f} N")
    cap = (f"At {th_taut:.0f} deg the loop goes taut. Down through dead centre ({dc[0]:.0f} deg) the seal takes "
           f"{dc[1]:.2f} mm more squeeze, the pull peaks at about {F_PEAK:.0f} N, then the loop pulls the lever shut "
           f"onto its base: over centre, it stays shut.")
    sc.step("9/9", cap, 4.5, close_b, hold=0.6, still=True)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    sc.step("9/9", cap, 0.4, rb.grip_to(0.15), hold=0.05)
    rb.events.append((sc.n, "release", AB.g("latch_lever"), AB.g("latch_loop")))
    state["inset"] = False
    rows(Lever="shut, over centre", Loop="taut on the keeper", Seal=f"squeeze {LT.PRELOAD:+.2f} mm (set)", Pull=None,
         Arm_1="parked", Arm_2="parked")
    cap = "Both arms let go and stand back."
    sc.step("9/9", cap, 0.8, AB.both(rb.line_to(g0 @ T((0, 0, -100))), rbB.line_to(T((0, 0, 60)) @ press)), hold=0.05)
    sc.step("9/9", cap, 1.8, AB.both(rb.joint_to(np.radians(AA.A.PARK_DEG)),
                                     rbB.joint_to(np.radians(AA.A.PARK_DEG))), hold=0.1, cam_to=CAM_LATCH)

    # ---------------------------------------------------------------- 9. pump-down, the bolt, the leak check
    def pump(u):
        p = -850.0 * window(u, 0.0, 0.7)
        AB.set_joints(sc, bolt=1.0 - window(u, 0.05, 0.3))
        rows(Furnace=f"pumping, {p:4.0f} mbar" if u < 0.72 else "-850 mbar, holding", Bolt="in (locked)" if u > 0.3
             else "coming in")
    cap = ("Vacuum Pump and Vacuum Valve (Cold purge 7): as the pressure changes the bolt comes in and locks the "
           "lever. The check the machine allows: the furnace reaches about -850 mbar and holds, with no hiss.")
    sc.step("9/9", cap, 4.0, pump, hold=0.8,
            labels=[("bolt in: lever locked", tuple(AB.W((150, LT.BOLT_Y, LT.BOLT_Z))), (0.82, 0.38))])
    cap = ("If it can't reach -0.85 bar or the lid hisses (DAL SOP troubleshooting): vent, open the latch, shorten "
           "the loop half a turn at its lock nuts (an adjuster we assume: the model and the footage show none), close "
           "it and pump again.")
    sc.step("9/9", cap, 0.5, None, hold=4.0,
            labels=[("adjuster: lock nuts on the loop (ours)", tuple(AB.W((LT.LX + LT.LEG_X, -147, 1357))),
                     (0.80, 0.24))])

    # ---------------------------------------------------------------- the MiRs' margins at the two loads
    try:
        stab = {}
        F_open = -(lever_pose(dc[0] + 1.0, G_lever)[:3, 3] - lever_pose(dc[0] - 1.0, G_lever)[:3, 3])
        F_open /= np.linalg.norm(F_open)
        for key, ball in (("with_ballast", True), ("without_ballast", False)):
            stab[key] = dict(
                arm1_lever_open=AA.stability(ma, q_grab, g0[:3, 3], F_open, ball),
                arm1_lever_shut=AA.stability(ma, q_grab, g0[:3, 3], -F_open, ball),
                arm2_press=AA.stability(mb, q_press, press[:3, 3], -press[:3, 2], ball),
                arm1_lid=AA.stability(ma, q_knob_g, gk0[:3, 3], (0.0, 0.0, -1.0), ball))
        stab["loads_N"] = dict(lever=F_PEAK, lever_stiff=F_STIFF, press=PRESS_F, lid_knob=LID_KNOB_N)
        stab["note"] = ("tips_at_N / slides_at_N: alloy_atomize.stability(): the force at the tool, in that direction, "
                        "that would tip the MiR250 about its weakest edge / slide it on its drive wheels. Lever: arm 1 "
                        "at its grasp on the lever, the force along the free end's path at dead centre.")
        STAB.update(stab)
        if not (PREVIEW or AUDIT):
            (OUT / "atom" / "atom_latch_stability.json").parent.mkdir(parents=True, exist_ok=True)
            (OUT / "atom" / "atom_latch_stability.json").write_text(json.dumps(stab, indent=1) + "\n")
        s = stab["with_ballast"]
        print("stability:", {k: (v["tips_at_N"], v["slides_at_N"]) for k, v in s.items()}, flush=True)
    except Exception as e:                  # never lose a render to the sums
        print("stability failed:", e, flush=True)
    s = STAB.get("with_ballast")
    if s:
        cap = (f"Margins (chapter 2's stability(), 131 kg plates): MiR 1 would tip at {s['arm1_lever_open']['tips_at_N']:.0f} N "
               f"and slide at {s['arm1_lever_open']['slides_at_N']:.0f} N on the lever (needs {F_PEAK:.0f}-{F_STIFF:.0f}); "
               f"MiR 2 at {s['arm2_press']['tips_at_N']:.0f} / {s['arm2_press']['slides_at_N']:.0f} N "
               f"pressing ({PRESS_F:.0f}).")
        sc.step("9/9", cap, 0.5, None, hold=5.0)
    AB.finish(sc)


if __name__ == "__main__":
    main()

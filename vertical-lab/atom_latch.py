"""The furnace lid's draw latch, unclamped after a run and clamped again before the next (PR #353, #303).

Sterling (PR #318, 2026-11-19): "it doesn't seem like you actually used the heat chamber latch correctly (i.e., actually
clamping it down and then unclamping it)". The latch here is the third pass's (notes/repowder_refine.md, T4 5:29.5-5:41):
a lever pivoting at its top that hangs flat over a base, a wire loop on its own pivot on the lever, hooked on a keeper on
the lid, and the machine's pneumatic bolt through the base. Its parts are redrawn on the model's own joints
(atom_latch_tools.py says why: as drawn in model.py they pass through each other when the lever opens).

Since commit e3b1428 the lid assembly is turned 90 deg on the machine: hinged on the left (DAL PR 189), the knob and
the latch on the housing's right face, the bolt running back into the blue cabinet. The latch is worked out in the
lid's own frame (atom_latch_tools) and carried over with M.LID_TURN_T.

Unclamping (vented, the bolt back): arm 2 holds the lid down with its closed fingertips; arm 1 (MiR250 1, right of the
furnace) takes the lever's free end and pulls it out and up about the top pivot, through dead centre to 150 deg; the
loop goes slack and its bar rides up the keeper; arm 2 takes the loop by its legs, lifts the bar off and lays the loop
over the lever; arm 1 folds the lever down; arm 2 swings the lid up and over to the left by its knob, 105 deg about
the left hinge. Clamping is the reverse, with the over-centre curve and the seal's squeeze in an inset, then the bolt
in at the pump-down and the leak check the machine allows. ``ARM_AUDIT=1`` checks every frame; ``PREVIEW=1`` the last frame of each step.
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
A_AT = (650.0, -560.0, 0.0)            # MiR250 1 (arm 1), model frame: right of the furnace, facing the latch on the
                                       # housing's right face (the lid assembly turned, commit e3b1428)
B_AT = (-500.0, -600.0, 0.0)           # MiR250 2 (arm 2), front left: the press and the lid (IK search)
# (02:13's render searched six spots and moved MiR250 1 onto (700, -420, 50) without a drive: its corner stood in the
# rePowder's base frame. It now stays at A_AT, whose footprint is clear: x 250..1050, y -850..-270.)
TURN = LT.TURN                         # the lid assembly's own frame -> the machine
LEVER_ALPHA = -35.0                    # arm 1's approach to the lever: in, and down 35 deg: the hand stands out and
                                       # above the latch (under it, on the turned lid, is the chamber's top plate)
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
    c = M.knob_centre(turned=False) + kd * 5.0      # 5 mm out along the stalk: the pads still span the 28 mm ball
    _, n_f = M.facet_plane(M.LID, "front", 0.12, turned=False)   # the facet the stalk stands on (lid frame)
    z = -kd
    x = np.cross(z, n_f)                            # fingers close level with the facet, so neither dips into it
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    Mx = np.eye(4)
    Mx[:3, 0], Mx[:3, 1], Mx[:3, 2], Mx[:3, 3] = x, y, z, c
    return TURN @ Mx                                # onto the machine: the knob on the lid's right facet


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
    if os.environ.get("ATOM_COMBINED_AUDIT") and not (PREVIEW or AUDIT):
        import collide                      # the ARM_AUDIT=1 checks run alongside the render: one pass for both
        sc.auditor = collide.Auditor(sc)
        sc.frame_hooks.append(sc.auditor)
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
    CAM_WIDE = AB.cam((1300, -2300, 2050), (0, -250, 1150))
    CAM_LATCH = AB.cam((520, 60, 1950), (165, 72, 1330))     # from above the right, over arm 1's reach
    CAM_LATCH2 = AB.cam((430, 150, 1720), (170, 72, 1340))   # closer, in front of the cabinet's top edge
    CAM_LID = AB.cam((300, -1900, 2150), (-90, 0, 1430))
    sc.cam = CAM_WIDE

    th_taut = LT.theta_taut()
    dc = max(LT.toggle_curve(), key=lambda t: t[1])
    peak_f = max(FCURVE, key=lambda t: t[1])

    # ---------------------------------------------------------------- 1. vent, bolt back
    rows(Furnace="cooling, 150 mbar Ar", Lever="shut", Loop="on the keeper", Seal="squeezed", Bolt="in (locked)",
         Arm_1="parked", Arm_2="parked")
    lab_pts = dict(lever=AB.W(LT.turn((LT.LX + 30, -160, 1240))), loop=AB.W(LT.turn((LT.LX - 34, -147, 1345))),
                   keeper=AB.W(LT.turn((LT.LX - 20, -146, 1395))), bolt=AB.W(LT.turn((150, LT.BOLT_Y, LT.BOLT_Z))))
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
            labels=[("bolt back: lever free", tuple(lab_pts['bolt']), (0.82, 0.38))])

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

    G_lever = TURN @ LT.lever_grasp(LEVER_ALPHA, z_c=1222.0)
    G_legs = TURN @ LT.legs_grasp()
    c_lever = LT.close_for_gap(GAP_LEVER)
    c_legs = LT.close_for_gap(GAP_LEGS)
    TH_REST = th_taut + 0.5                 # the lever rests here on the slack loop, its bar back on the hook
    TH_UP = 85.0                            # lifted by the loop to here, the bar rides up the plate clear of the lip

    def lever_move(u):
        d = 60.0 * u
        set_latch(sc, d, ride_val(d / M.LATCH_OPEN_DEG)[0])

    def ride_d(d):
        return ride_val(d / M.LATCH_OPEN_DEG)[0]

    def legs_state(s_):
        """The loop held by its legs: s_ 0..0.4 lifts the lever from TH_REST to TH_UP by the loop (its bar riding up
        the plate), 0.4..1 swings the loop out over the lever's top while the lever folds down, ending on its web."""
        if s_ <= 0.4:
            d = TH_REST + (TH_UP - TH_REST) * (s_ / 0.4)
            return d, ride_d(d)
        w = (s_ - 0.4) / 0.6
        d = TH_UP * (1.0 - w)
        t = ride_d(TH_UP) + (LT.on_web() - ride_d(TH_UP)) * min(1.0, w / 0.55)
        return d, t

    def legs_move(u):
        d, t = legs_state(u)
        set_latch(sc, d, t)
    arc_open = [lever_pose(d, G_lever) for d in np.linspace(0.0, 60.0, 13)]
    # MiR 1 stays where it starts (A_AT: its corner clear of the rePowder's base frame; the 02:13 render's search moved
    # it, without a drive, onto a spot whose corner stood in the frame). The loop's grasp: of a few approach angles,
    # with the tool as is or turned 180 deg about its axis, the one whose arm follows the loop's swing with the fewest
    # hits (the default, in and down 40 deg, is kept unless another does better and follows the whole swing)
    q_lev, s1 = pick_branch(rb, sc, arc_open, lever_move, c_lever, ("atl latch_lever", "atl latch_loop"), back=100.0,
                            score=True)
    best = None
    for alpha in (-40.0, -10.0, -65.0, 15.0):
        for spin in (0.0, 180.0):
            Gc = TURN @ LT.legs_grasp(alpha_deg=alpha) @ R((0, 0, 1), spin)
            path_c = [loop_pose(*legs_state(s_), Gc) for s_ in np.linspace(0, 1, 26)]
            rb.set(np.radians(AA.A.PARK_DEG))
            q2, s2 = pick_branch(rb, sc, path_c, legs_move, c_legs, ("atl latch_loop", "atl latch_lever"), back=90.0,
                                 score=True)
            print("loop grasp", alpha, spin, "hits", s2, flush=True)
            if s2 < 999 and (best is None or s2 < best[0]):
                best = (s2, Gc, q2)
    lever_move(0.0)
    rb.set(np.radians(AA.A.PARK_DEG))
    if best is not None:
        _, G_legs, q_legs = best
    else:
        q_legs = pick_branch(rb, sc, [loop_pose(*legs_state(s_), G_legs) for s_ in np.linspace(0, 1, 26)],
                             legs_move, c_legs, ("atl latch_loop", "atl latch_lever"), back=90.0)
    lever_move(0.0)
    g0 = lever_pose(0.0, G_lever)
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
    path_a = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(0.0, 60.0, 13)])
    state["inset"] = True

    def open_a(u):
        path_a(u)
        d = 60.0 * u
        lv, sq = ride_val(d / M.LATCH_OPEN_DEG)
        latch_state(d, lv, sq)
        rows(Lever=f"{d:5.1f} deg", Loop="taut on the keeper" if d <= th_taut else "slack",
             Seal=f"squeeze {sq:+.2f} mm" if d <= th_taut else "free", Pull=f"{max(pull_at(d), 0):5.0f} N")
    cap = (f"Out and up about the top pivot. The loop's pivot first draws away from the hook: the seal is squeezed "
           f"{dc[1]:.2f} mm more at dead centre, {dc[0]:.0f} deg out; the pull peaks just before it, about "
           f"{F_PEAK:.0f} N (estimate; {F_STIFF:.0f} N if stiff), and is zero there. Past {th_taut:.0f} deg the loop is "
           f"slack.")
    sc.step("4/9", cap, 4.5, open_a, hold=0.3, cam_to=CAM_LATCH2)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    path_b = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(60.0, TH_REST, 6)])

    def back_b(u):
        path_b(u)
        d = 60.0 + (TH_REST - 60.0) * u
        latch_state(d, ride_d(d), 0.0)
        rows(Lever=f"{d:5.1f} deg", Loop="slack, its bar on the hook", Seal="free", Pull="lever's weight")
    cap = (f"Arm 1 lets the lever back to {TH_REST:.0f} deg, where it rests on the slack loop, whose bar sits on the "
           "keeper's hook again; then it lets go.")
    sc.step("4/9", cap, 1.4, back_b, hold=0.2)
    q_rest = rb.q.copy()
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))
    sc.step("4/9", cap, 0.4, rb.grip_to(0.15), hold=0.05)
    rb.events.append((sc.n, "release", AB.g("latch_lever"), AB.g("latch_loop")))
    g_rest = lever_pose(TH_REST, G_lever)
    sc.step("4/9", cap, 0.8, rb.line_to(g_rest @ T((0, 0, -90))), hold=0.05)
    state["inset"] = False
    q_press_end = rbB.q.copy()
    rows(Arm_2="parked", Pull=None)
    sc.step("4/9", "Arm 2 lets go of the lid, which now sits free.", 0.8, rbB.line_to(T((0, 0, 60)) @ press),
            hold=0.05)
    sc.step("4/9", "Arm 2 lets go of the lid, which now sits free.", 1.6, rbB.joint_to(np.radians(AA.A.PARK_DEG)),
            hold=0.05)

    # ---------------------------------------------------------------- 4. arm 1 lifts the loop off, folds the lever
    g_legs = loop_pose(*legs_state(0.0), G_legs)
    rows(Arm_1="to the loop", Loop="slack, on the hook")
    cap = ("Arm 1 takes the loop by its two legs, from outside, clear of the lever and the keeper. Lifting it raises "
           "the lever on the loop's pin, and the bar rides up the keeper's plate, over the hook's lip.")
    sc.step("5/9", cap, 2.2, AB.both(rb.joint_to(q1=rb.solve(g_legs @ T((0, 0, -90)), q_legs)), rb.grip_to(0.10)),
            hold=0.05)
    sc.step("5/9", cap, 0.9, rb.line_to(g_legs), hold=0.05)
    sc.step("5/9", cap, 0.4, rb.grip_to(c_legs), hold=0.1)
    rb.events.append((sc.n, "grasp", AB.g("latch_loop"), AB.g("latch_lever")))
    f_legs = AA.follow(rb, [loop_pose(*legs_state(s_), G_legs) for s_ in np.linspace(0, 0.4, 8)])

    def lift_up(u):
        f_legs(u)
        d, t = legs_state(0.4 * u)
        latch_state(d, t, 0.0)
        rows(Lever=f"{d:5.1f} deg", Loop="lifted: the bar rides up the plate")
    sc.step("5/9", cap, 1.8, lift_up, hold=0.1,
            labels=[("loop lifted off the hook", tuple(AB.W(LT.turn((LT.LX - 36, -175, 1395)))), (0.12, 0.30))])
    rb.events.append((sc.n, "grasp", AB.g("latch_loop"), AB.g("latch_lever")))
    f_fold = AA.follow(rb, [loop_pose(*legs_state(s_), G_legs) for s_ in np.linspace(0.4, 1.0, 16)])

    def fold(u):
        f_fold(u)
        d, t = legs_state(0.4 + 0.6 * u)
        latch_state(d, t, 0.0)
        rows(Lever=f"{d:5.1f} deg", Loop="swung over the lever")
    cap = ("It swings the loop out over the lever's top and lets the lever down with it: folded, the lever has the "
           "loop hanging over it (T4 5:08, 5:29.5; the hand's moves read backwards from 5:29.5-5:41).")
    sc.step("5/9", cap, 3.2, fold, hold=0.2)
    q_web = rb.q.copy()
    rb.events.append((sc.n, "grasp", AB.g("latch_loop"), AB.g("latch_lever")))
    sc.step("5/9", cap, 0.4, rb.grip_to(0.10), hold=0.05)
    rb.events.append((sc.n, "release", AB.g("latch_loop"), AB.g("latch_lever")))
    g_web = loop_pose(*legs_state(1.0), G_legs)
    sc.step("5/9", cap, 0.8, rb.line_to(g_web @ T((0, 0, -90))), hold=0.05)
    rows(Lever="folded", Loop="hanging over the lever", Seal=None, Arm_1="parked")
    sc.step("5/9", cap, 1.6, rb.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.05)

    # ---------------------------------------------------------------- 6. the lid up and over to the left
    G_knob = knob_grasp_model()
    c_knob = LT.close_for_gap(GAP_KNOB)
    gk0 = lid_pose(0.0, G_knob)

    def lid_move(u):
        AB.set_joints(sc, lid=u)
    q_knob = pick_branch(rbB, sc, [lid_pose(s, G_knob) for s in np.linspace(0, 1, 22)], lid_move, c_knob,
                         ("knob", "hood"), back=45.0)
    lid_move(0.0)
    rows(Lever="folded", Loop="hanging over the lever", Arm_1="parked", Arm_2="to the knob")
    cap = (f"Arm 2 takes the lid's knob, on its right facet, and swings the lid up and over to the left about its "
           f"hinge, 105 deg (the hinge is on the left: DAL PR 189; T4 5:14.5-5:16.5 shows one rotation, no lift or "
           f"slide). The lid's weight on the knob is about {LID_KNOB_N:.0f} N at the start (chapter 2's estimate).")
    sc.step("7/9", cap, 2.6, AB.both(rbB.joint_to(q1=rbB.solve(gk0 @ T((0, 0, -60)), q_knob)), rbB.grip_to(0.2)),
            hold=0.1, cam_to=CAM_LID)
    sc.step("7/9", cap, 0.9, rbB.line_to(gk0), hold=0.05)
    sc.step("7/9", cap, 0.4, rbB.grip_to(c_knob), hold=0.1)
    rbB.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    q_knob_g = rbB.q.copy()
    path_lid = AA.follow(rbB, [lid_pose(s, G_knob) for s in np.linspace(0, 1, 22)])

    def lid_up(u):
        path_lid(u)
        lid_move(u)
        rows(Furnace=f"lid {105 * u:3.0f} deg")
    sc.step("7/9", cap, 4.0, lid_up, hold=0.3)
    rbB.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    q_top = rbB.q.copy()
    gk1 = lid_pose(1.0, G_knob)
    sc.step("7/9", cap, 0.4, rbB.grip_to(0.2), hold=0.05)
    rbB.events.append((sc.n, "release", AB.g("knob"), AB.g("hood")))
    sc.step("7/9", cap, 0.8, rbB.line_to(gk1 @ T((0, 0, -60))), hold=0.05)
    rows(Furnace="lid open: rebuild, charge (other clips)", Arm_2="parked")
    sc.step("7/9", "Open, the furnace is rebuilt and charged (the other clips in this series). Then the same steps, "
            "backwards, close it.", 1.8, rbB.joint_to(np.radians(AA.A.PARK_DEG)), hold=1.4)

    # ---------------------------------------------------------------- 7. clamping: the lid down
    rows(Furnace="lid open, charged", Arm_2="to the knob")
    cap = ("Clamping, after IPA on the seal and the face it meets (DAL SOP, Loading the Furnace 8). Arm 2 brings the "
           "lid back down by its knob onto the O-ring.")
    sc.step("8/9", cap, 2.4, AB.both(rbB.joint_to(q1=rbB.solve(gk1 @ T((0, 0, -60)), q_top)), rbB.grip_to(0.2)),
            hold=0.05)
    sc.step("8/9", cap, 0.8, rbB.line_to(gk1), hold=0.05)
    sc.step("8/9", cap, 0.4, rbB.grip_to(c_knob), hold=0.05)
    rbB.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    path_lid2 = AA.follow(rbB, [lid_pose(s, G_knob) for s in np.linspace(1, 0, 22)])

    def lid_down(u):
        path_lid2(u)
        lid_move(1.0 - u)
        rows(Furnace=f"lid {105 * (1 - u):3.0f} deg" if u < 1 else "lid down, not clamped")
    sc.step("8/9", cap, 3.6, lid_down, hold=0.2)
    rbB.events.append((sc.n, "grasp", AB.g("knob"), AB.g("hood")))
    sc.step("8/9", cap, 0.4, rbB.grip_to(0.2), hold=0.05)
    rbB.events.append((sc.n, "release", AB.g("knob"), AB.g("hood")))
    sc.step("8/9", cap, 0.8, rbB.line_to(gk0 @ T((0, 0, -60))), hold=0.05)
    sc.step("8/9", cap, 1.6, rbB.joint_to(np.radians(AA.A.PARK_DEG)), hold=0.05, cam_to=CAM_LATCH2)

    # ---------------------------------------------------------------- 8. hook the loop on, shut over centre
    rows(Arm_1="to the loop")
    cap = ("Arm 1 takes the loop's legs again and swings it back over the lever's top, raising the lever with it, "
           "and lays the bar on the keeper's plate (\"hook the loop on\", T4 5:30-5:35).")
    sc.step("8/9", cap, 2.2, AB.both(rb.joint_to(q1=rb.solve(g_web @ T((0, 0, -90)), q_web)), rb.grip_to(0.10)),
            hold=0.05, cam_to=CAM_LATCH2)
    sc.step("8/9", cap, 0.9, rb.line_to(g_web), hold=0.05)
    sc.step("8/9", cap, 0.4, rb.grip_to(c_legs), hold=0.05)
    rb.events.append((sc.n, "grasp", AB.g("latch_loop"), AB.g("latch_lever")))
    f_unfold = AA.follow(rb, [loop_pose(*legs_state(s_), G_legs) for s_ in np.linspace(1.0, 0.4, 16)])

    def unfold(u):
        f_unfold(u)
        d, t = legs_state(1.0 - 0.6 * u)
        latch_state(d, t, 0.0)
        rows(Lever=f"{d:5.1f} deg", Loop="over onto the keeper")
    sc.step("8/9", cap, 3.2, unfold, hold=0.1)
    rb.events.append((sc.n, "grasp", AB.g("latch_loop"), AB.g("latch_lever")))
    f_down = AA.follow(rb, [loop_pose(*legs_state(s_), G_legs) for s_ in np.linspace(0.4, 0.0, 8)])

    def seat(u):
        f_down(u)
        d, t = legs_state(0.4 * (1.0 - u))
        latch_state(d, t, 0.0)
        rows(Lever=f"{d:5.1f} deg", Loop="on the hook" if u > 0.98 else "sliding down the plate")
    cap = f"Lowered, the bar slides down the plate onto the hook; the lever rests at {TH_REST:.0f} deg on the slack loop."
    sc.step("8/9", cap, 1.8, seat, hold=0.1)
    rb.events.append((sc.n, "grasp", AB.g("latch_loop"), AB.g("latch_lever")))
    sc.step("8/9", cap, 0.4, rb.grip_to(0.10), hold=0.05)
    rb.events.append((sc.n, "release", AB.g("latch_loop"), AB.g("latch_lever")))
    sc.step("8/9", cap, 0.8, rb.line_to(g_legs @ T((0, 0, -90))), hold=0.05)
    rows(Arm_2="to the lid's top")
    cap = "Arm 2 presses the lid's top again, so the seal is squeezed evenly while the loop draws the lid down."
    sc.step("8/9", cap, 2.2, rbB.joint_to(q1=rbB.solve(pre_press, q_press)), hold=0.05, cam_to=CAM_WIDE)
    sc.step("8/9", cap, 0.9, rbB.line_to(press), hold=0.1)
    rows(Arm_2=f"pressing, ~{PRESS_F:.0f} N", Arm_1="to the lever")
    cap = f"Arm 1 takes the lever's free end again, at {TH_REST:.0f} deg."
    sc.step("8/9", cap, 2.0, AB.both(rb.joint_to(q1=rb.solve(g_rest @ T((0, 0, -90)), q_rest)), rb.grip_to(0.15)),
            hold=0.05, cam_to=CAM_LATCH2)
    sc.step("8/9", cap, 0.8, rb.line_to(g_rest), hold=0.05)
    sc.step("8/9", cap, 0.4, rb.grip_to(c_lever), hold=0.05)
    rb.events.append((sc.n, "grasp", AB.g("latch_lever"), AB.g("latch_loop")))

    # ---------------------------------------------------------------- 9. over centre, shut
    state["inset"] = True
    path_f = AA.follow(rb, [lever_pose(d, G_lever) for d in np.linspace(TH_REST, 0.0, 12)])

    def close_b(u):
        path_f(u)
        d = TH_REST * (1.0 - u)
        lv, sq = ride_val(d / M.LATCH_OPEN_DEG)
        latch_state(d, lv, sq)
        rows(Lever=f"{d:5.1f} deg", Loop="taut on the keeper" if d <= th_taut else "slack",
             Seal=f"squeeze {sq:+.2f} mm" if d <= th_taut else "free", Pull=f"{max(pull_at(d), 0):5.0f} N")
    cap = (f"Down through dead centre ({dc[0]:.0f} deg): the loop goes taut, the seal takes {dc[1]:.2f} mm more "
           f"squeeze, the pull peaks at about {F_PEAK:.0f} N; past it the loop pulls the lever shut onto its base. "
           f"Over centre, it stays shut.")
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
            labels=[("bolt in: lever locked", tuple(lab_pts['bolt']), (0.82, 0.38))])
    cap = ("If it can't reach -0.85 bar or the lid hisses (DAL SOP troubleshooting): vent, open the latch, shorten "
           "the loop half a turn at its lock nuts (an adjuster we assume: the model and the footage show none), close "
           "it and pump again.")
    sc.step("9/9", cap, 0.5, None, hold=4.0,
            labels=[("adjuster: lock nuts on the loop (ours)", tuple(AB.W(LT.turn((LT.LX + LT.LEG_X, -147, 1357)))),
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
                arm2_lid=AA.stability(mb, q_knob_g, gk0[:3, 3], (0.0, 0.0, -1.0), ball))
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
    if getattr(sc, "auditor", None) is not None and not AUDIT:
        sc.auditor.save()


if __name__ == "__main__":
    main()

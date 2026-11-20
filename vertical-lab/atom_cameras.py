"""Clip: the rePowder's melt-chamber and melt-stream cameras and their displays (DAL PR 189), on this repo's model,
with the live feeds (PR #353, #303).

The three Pi 5 units of digital-alloy-lab PR 189 (atom_cams.py: DAL's own Onshape parts, placed as DAL's units.py
placed them): what each camera looks at; the top unit's arm swung to its parked dimple and back by MiR250 1's UR10e
(it grips the 2020 extrusion and swings it about the post, the tool solved on the exact arc each frame; the ball
plunger clicks into each dimple); the displays beside the operator's positions, which Pi drives which, and the
atomizer's own HMI; then a melt and a pour (chapter 2's stream, plate and spray), seen by the cameras: each feed is
rendered from the camera's own pose and lens (HQ + 16 mm: 22.2 x 16.8 deg; Camera Module 3 Wide: 102 x 67 deg), put
on its display as a texture and shown in panels. notes/atom_cameras.md has the sources and the findings.

    python3 runner_guard.py slot --label cams --mem 3000 -- xvfb-run -a python3 atom_cameras.py
    ARM_AUDIT=1 ... python3 atom_cameras.py      # FCL every frame -> out/collisions/atom_cameras.json
    PREVIEW=1 ...   python3 atom_cameras.py      # the last frame of each sub-step -> /tmp/preview_atom_cameras.png
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import atom_base as AB                # noqa: E402
import atom_cams as CAMS              # noqa: E402
import alloy_atomize as AA            # noqa: E402
import charge as CH                   # noqa: E402
import ur_arm as UA                   # noqa: E402
from scene import AUDIT, FPS, OUT, PREVIEW, S, T, mix, window   # noqa: E402

M = AB.M
W = AB.W
NAME = "atom_cameras"
MELT_C = (1.0, 0.52, 0.16)            # the melt as the top camera shows it through the hot mirror and ND (not white)
LOS = dict(top_hq=(0.85, 0.15, 0.15), front_hq=(0.95, 0.55, 0.10), front_wide=(0.15, 0.55, 0.95),
           left_wide=(0.20, 0.70, 0.30))
GRIP_S = 300.0                        # mm out along the extrusion from the post's axis where the 2F-85 holds it
BAR = 20.0                            # 2020 extrusion: 20 x 20 mm
STREAM_F = 0.98                       # the stream drawn to 4 mm short of where it lands, so it does not cut the plate
LEVEL_END = 29.0                      # mm over the crucible datum when the charge has melted (four 17 x 100 slugs, ours)

sc, ma, mb = AB.build(NAME, "Vertical cloud lab: the melt-chamber and melt-stream cameras and their displays (DAL PR 189)")
names = CAMS.add_units(sc)
rb = ma.rb
AB.mir_at(mb, (1150.0, -950.0, 90.0))   # MiR250 2 has no part here: parked at the right, out of the views
POSES0 = CAMS.unit_poses(0.0, 0.0)


# --------------------------------------------------------------------------------- extras: lines of sight
def frustum(p: dict, length: float, r: float = 1.1) -> pv.PolyData:
    """The camera's field of view as a wire pyramid `length` mm long (model frame, as built)."""
    e, d, up = p["eye"], p["dir"], p["up"]
    x = np.cross(d, up)
    hw = length * math.tan(math.radians(p["hfov"] / 2))
    hh = length * math.tan(math.radians(p["vfov"] / 2))
    c = e + d * length
    corners = [c + x * sx * hw + up * sy * hh for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    segs = [(e, k) for k in corners] + [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    out = None
    for a, b in segs:
        t = pv.Line(a, b).tube(radius=r, n_sides=8)
        out = t if out is None else out.merge(t)
    return out


LOS_LEN = dict(top_hq=None, front_hq=200.0, front_wide=120.0, left_wide=160.0)
los_names = []
for key, p in POSES0.items():
    ln = LOS_LEN[key] or float(np.linalg.norm(CAMS.AIM - p["eye"]))
    unit = CAMS.CAMERAS[key]["unit"]
    nm = f"cams los {key}"
    sc.add(nm, frustum(p, ln, 1.4 if key == "top_hq" else 1.1), LOS[key], CAMS.GROUPS[unit], ambient=0.8,
           specular=0.0)
    los_names.append(nm)
# the top camera's line to the melt (DAL's red line in its renders)
p = POSES0["top_hq"]
sc.add("cams los top line", pv.Line(p["eye"], CAMS.AIM).tube(radius=2.0, n_sides=10), (0.90, 0.10, 0.10),
       CAMS.GROUPS["arm"], ambient=0.8, specular=0.0)
los_names.append("cams los top line")
sc.show(los_names, 0.0)

# --------------------------------------------------------------------------------- the charge and its melt
SLUGS = [f"slug{k}" for k in range(4)]
slug_actors = [n for k in range(4) for n in sc.members(AB.g(f"slug{k}"))]
sc.show(slug_actors, 1.0)                      # four 17 x 100 mm slugs standing in the crucible (the model's)
SLUG_C = [np.array([M.SLUG_R * math.cos(math.radians(a)), M.SLUG_R * math.sin(math.radians(a))])
          for a in M.SLUG_ANGLES]


def melt_mesh(level: float) -> pv.PolyData:
    """The melt filling the crucible's floor cone and bore up to `level` mm over the datum (full, not cut)."""
    z0 = M.Z_CR - M.FLOOR_CONE_H
    r = M.CRUCIBLE_ID / 2 - 0.3
    if level <= -M.FLOOR_CONE_H + 0.5:
        level = -M.FLOOR_CONE_H + 0.5
    if level < 0:
        rr = r * (level + M.FLOOR_CONE_H) / M.FLOOR_CONE_H
        prof = [(0.0, z0), (rr, M.Z_CR + level), (0.0, M.Z_CR + level)]
    else:
        prof = [(0.0, z0), (r, M.Z_CR), (r, M.Z_CR + level), (0.0, M.Z_CR + level)]
    return CH.lathe(prof, res=48)


sc.add("cams melt", melt_mesh(-15.0), MELT_C, AB.g("crucible"), ambient=0.9, diffuse=0.35, specular=0.3)
sc.show(["cams melt"], 0.0)


def set_melt(level: float, on: bool = True):
    sc.set_mesh("cams melt", melt_mesh(level))
    sc.alpha["cams melt"] = 1.0 if on else 0.0


AA.add_stream(sc, radius=1.4)
spray = AA.Particles(sc, "spray", (1.0, 0.62, 0.28), size=4.0, slowmo=0.22, seed=3)
drops = AA.Particles(sc, "drops", (1.0, 0.55, 0.20), size=5.0, slowmo=0.22, seed=4)

# --------------------------------------------------------------------------------- the lid's swing, as a still ghost
# two copies of the lid (model, e3b1428: hinged on the left) at half and full opening; they never move while shown
GHOSTS = {}
for tag, v_g in (("a", 0.5), ("b", 1.0)):
    grp = f"cams:lid_ghost_{tag}"
    for g_ in (AB.g("hood"), AB.g("knob")):
        for n in sc.members(g_):
            if sc.cutrole.get(n) not in (None, "whole") or sc.base_alpha.get(n, 1.0) <= 0.02 or n.endswith("#cut"):
                continue
            gn = f"cams lid ghost {tag} {n}"
            sc.add(gn, pv.wrap(sc.actors[n].GetMapper().GetInput()).copy(), (0.55, 0.66, 0.90), grp, opacity=0.25,
                   specular=0.0, ambient=0.5)
            GHOSTS.setdefault(tag, []).append(gn)
    sc.parent[grp] = "rp"
    sc.gmat[grp] = M.joint_matrix("lid", v_g)
    sc.show(GHOSTS[tag], 0.0)


def ghosts(a: float):
    for tag in GHOSTS:
        sc.show(GHOSTS[tag], a)


# --------------------------------------------------------------------------------- the live feeds
feeds = CAMS.Feeds(sc, every=2)
feeds.add_display_textures()
feeds.sync()

# --------------------------------------------------------------------------------- the swing: poses
C0, D0 = CAMS.extrusion_axis()


def grip_pose(v: float, back: float = 0.0) -> np.ndarray:
    """World TCP pose holding the extrusion GRIP_S out, the arm at v: the tool level and square to the bar, on its
    trailing side, pointing the way the arm turns to park (so the palm pushes it round); the fingers close top and
    bottom on the bar (TCP x vertical). back: mm backed off along the tool axis."""
    p = CAMS.extrusion_point(GRIP_S, v)
    d = CAMS.top_arm_matrix(v)[:3, :3] @ D0
    z = np.array([-d[1], d[0], 0.0])
    x = np.array([0.0, 0.0, 1.0])
    y = np.cross(z, x)
    Tm = np.eye(4)
    Tm[:3, 0], Tm[:3, 1], Tm[:3, 2], Tm[:3, 3] = x, y, z, W(p - z * back)
    return Tm


def arc(v0: float, v1: float, n: int = 19) -> list:
    return [grip_pose(v) for v in np.linspace(v0, v1, n)]


def reachable(poses) -> bool:
    q = rb.q.copy()
    for Tw in poses:
        try:
            q = rb.solve(Tw, q)
        except ValueError:
            return False
        Tg = rb.tcp_world(q)
        if np.linalg.norm(Tg[:3, 3] - Tw[:3, 3]) > 0.5:
            return False
    return True


# the spot MiR 1 drives to for the swing (ours): the first, over every IK branch, from which the whole sequence is
# reachable and clean, checked as it will run: the approach line with the fingers open, the swing with the arm held
# (held part and gripper against everything, the arm against itself and the held part), the back-off. The paths are
# recorded and played back, and the return is the same path reversed.
BACK = 60.0                            # mm the tool backs off along its axis before and after holding the bar
CLOSE_BAR = UA.close_for(BAR + 0.6)
SPOTS = [(x, y, yaw) for y in (-620.0, -680.0, -580.0, -740.0) for x in (100.0, 200.0, 0.0, 300.0, -100.0)
         for yaw in (0.0, 30.0, -30.0, 60.0, -60.0)]
start_xy = (ma.x, ma.y, ma.yaw)
q_home = rb.q.copy()
chk = rb.checker()
ARM_G, POST_G = CAMS.GROUPS["arm"], CAMS.GROUPS["post"]


def _inv(Mx):
    Mi = np.eye(4)
    Mi[:3, :3] = Mx[:3, :3].T
    Mi[:3, 3] = -Mx[:3, :3].T @ Mx[:3, 3]
    return Mi


def _solve_path(poses, q):
    out = []
    for Tw in poses:
        q = rb.solve(Tw, q)
        if np.linalg.norm(rb.tcp_world(q)[:3, 3] - Tw[:3, 3]) > 0.5:
            raise ValueError("off the path")
        out.append(q.copy())
    return out


def _bad(hits):
    """Hits that count: anything but the fingers on the extrusion they hold."""
    return [h for h in hits if not (h[0] == "gripper" and h[3] == ARM_G)]


def plan(spot):
    import collide
    AB.mir_at(ma, spot)
    rb.q = q_home.copy()
    try:
        branches = collide.ik_all(rb.model, _inv(sc.world(rb.root)) @ grip_pose(0.0, BACK), q_home)
    except ValueError:
        return None
    line0 = [grip_pose(0.0, BACK * (1 - t)) for t in np.linspace(0, 1, 21)]
    line1 = [grip_pose(1.0, BACK * t) for t in np.linspace(0, 1, 21)]
    vs = np.linspace(0.0, 1.0, 121)
    ev = list(rb.events)
    for q0 in branches:
        CAMS.set_top_arm(sc, 0.0)
        try:
            p_in0 = _solve_path(line0, np.asarray(q0, float))
            p_sw = _solve_path([grip_pose(v) for v in vs], p_in0[-1])
            p_out1 = _solve_path(line1, p_sw[-1])
        except ValueError:
            continue
        world0 = chk.snapshot()
        if any(_bad(chk.collisions(q, 0.0, world0, allow={ARM_G})) for q in p_in0[:-1]):
            continue
        rb.set(p_in0[-1], CLOSE_BAR)
        rb.grasp(ARM_G)
        world_h = chk.snapshot()
        ok = True
        for v, q in zip(vs, p_sw):
            rb.set(q)
            if _bad(chk.collisions(q, CLOSE_BAR, world_h, allow={ARM_G})):
                if os.environ.get("CAMS_SPOT_DEBUG"):
                    print("spot", spot, "swing v", round(float(v), 2),
                          _bad(chk.collisions(q, CLOSE_BAR, world_h, allow={ARM_G}))[:3], flush=True)
                ok = False
                break
        rb.release("rp")
        CAMS.set_top_arm(sc, 1.0)
        if ok:
            world1 = chk.snapshot()
            ok = not any(_bad(chk.collisions(q, 0.0, world1, allow={ARM_G})) for q in p_out1[1:])
        CAMS.set_top_arm(sc, 0.0)
        rb.events[:] = ev
        if ok:
            return dict(q_pre=np.asarray(q0, float), in0=p_in0, sw=(vs, p_sw), out1=p_out1)
    return None


SPOT, PLAN = None, None
for s_ in SPOTS:
    PLAN = plan(s_)
    if PLAN is not None:
        SPOT = s_
        break
CAMS.set_top_arm(sc, 0.0)
if SPOT is None:
    raise SystemExit("no MiR spot reaches the swing clear of the machine")
ma.set(*start_xy)
rb.q = q_home.copy()
rb.set(close=0.0)
Q_PRE = PLAN["q_pre"]
print("MiR 1 swing spot (model frame x, y, yaw):", SPOT, "branch", np.degrees(Q_PRE).round(1).tolist(), flush=True)


def play(path):
    """update(u): the arm through a recorded joint path (linear between its samples)."""
    path = [np.asarray(q, float) for q in path]

    def up(u):
        x = u * (len(path) - 1)
        i = min(int(x), len(path) - 2)
        rb.set(path[i] + (path[i + 1] - path[i]) * (x - i))
    return up


def swing(v0: float, v1: float):
    """The arm held and turned about the post from v0 to v1, through the recorded path (solved on the exact arc,
    121 samples over the 90 deg), so the hub turns about the post's axis."""
    vs, qs = PLAN["sw"]

    def up(u):
        v = v0 + (v1 - v0) * u
        x = v * (len(vs) - 1)
        i = min(int(x), len(vs) - 2)
        rb.set(qs[i] + (qs[i + 1] - qs[i]) * (x - i))
        sc.cams_top = v
    return up


# the lid's swing (model, commit e3b1428: hinged on the left) against the top arm in its working dimple (FCL)
def lid_clearance():
    import fcl

    def body(n):
        m = pv.wrap(sc.actors[n].GetMapper().GetInput()).triangulate()
        Wm = sc.world(sc.group_of[n])
        v = (Wm[:3, :3] @ np.asarray(m.points).T).T + Wm[:3, 3]
        b = fcl.BVHModel()
        b.beginModel(len(v), m.n_cells)
        b.addSubModel(v, m.faces.reshape(-1, 4)[:, 1:])
        b.endModel()
        return fcl.CollisionObject(b, fcl.Transform())
    lid_parts = [n for g_ in (AB.g("hood"), AB.g("knob")) for n in sc.members(g_)
                 if sc.cutrole.get(n) in (None, "whole") and not n.endswith("#cut")]
    arm = [body(n) for n in names["arm"]]
    best = (1e9, None, None)
    for v in np.linspace(0.0, 1.0, 22):
        AB.set_joints(sc, lid=float(v))
        for n in lid_parts:
            o = body(n)
            for k, a in enumerate(arm):
                d = fcl.distance(o, a, fcl.DistanceRequest(), fcl.DistanceResult())
                if d < best[0]:
                    best = (float(d), float(v), names["arm"][k] + " / " + n)
    AB.set_joints(sc, lid=0.0)
    return best


LID_CLEAR = lid_clearance()
print("lid swing vs the top arm (working): %.1f mm at lid %.2f, %s" % LID_CLEAR, flush=True)


# --------------------------------------------------------------------------------- views (model frame)
V_ALL = AB.cam((-1500, -2300, 2150), (120, 0, 1250))
V_TOP = AB.cam((-650, -1150, 2050), (0, -60, 1600))
V_TOP_LINE = AB.cam((-900, -420, 1750), (0, -110, 1500))
V_FRONT = AB.cam((-420, -880, 1250), (-15, -180, 1060))
V_LEFT = AB.cam((-850, -520, 1200), (-180, -30, 1030))
V_SWING = AB.cam((-1300, -1900, 2500), (60, -150, 1550))
V_LIDG = AB.cam((-1500, -900, 2000), (0, 50, 1550))
V_DISP_FRONT = AB.cam((-300, -620, 1180), (-20, -230, 1090))
V_DISP_LEFT = AB.cam((-560, -260, 1120), (-210, -30, 1030))
V_DISP_TOP = AB.cam((-150, -720, 1900), (20, -300, 1790))
V_HMI = AB.cam((350, -1250, 1650), (550, 0, 1400))
V_MELT = AB.cam((-700, -1000, 1950), (0, -150, 1600))
V_POUR = AB.cam((-1100, -1250, 1450), (-60, -60, 1050))

UNITS_LAB = [("front unit: HQ Camera (M12) + Camera Module 3 Wide,\n5 in HDMI display, on AMAZEMET's LED cover",
              tuple(W((-15, -235, 1060))), (0.06, 0.62)),
             ("left unit, on the door: Camera Module 3 Wide,\n5 in Touch Display 2, on the sight-glass ring",
              tuple(W((-190, 20, 1015))), (0.06, 0.42)),
             ("top unit: HQ Camera + 16 mm C lens, hot mirror, ND,\n2.8 in DSI, on a 2020 arm from a post on the frame",
              tuple(W((10, -300, 1800))), (0.06, 0.22))]


def gauges(**kw):
    AB.caption_rows(sc, **kw)


# one pass for the clip and its audit (the coordinator, 19 Nov): the collision auditor rides the render's frames
if not (AUDIT or PREVIEW):
    import collide
    sc.auditor = collide.Auditor(sc)
    sc.frame_hooks.append(sc.auditor)

# ======================================================================================== 1. the three units
gauges(Units="front, left, top (DAL PR 189)", Top_arm="working dimple", Furnace="cold, lid shut")
cap = ("Three Pi 5 camera units from DAL PR 189, on the lab's rePowder model: one on the chamber's front view port, "
       "one on the door's sight glass, one looking down through the furnace lid's window. Each shows its picture on its "
       "own display beside the operator.")
sc.step("1/6", cap, 4.0, None, hold=2.4, cam_to=V_ALL, labels=UNITS_LAB)

# ======================================================================================== 2. lines of sight
cap = ("Top: the HQ Camera sits on the line through the lid's 60 x 64 mm window to the crucible, 66 deg below "
       "level, 250 mm from the glass. With the 16 mm lens it sees 22 x 17 deg: about 190 mm across at the melt (DAL).")


def los_in(keys):
    def up(u):
        for k in keys:
            sc.alpha[f"cams los {k}"] = min(1.0, u * 2)
        if "top_hq" in keys:
            sc.alpha["cams los top line"] = min(1.0, u * 2)
    return up


sc.step("2/6", cap, 3.0, los_in(["top_hq"]), hold=2.0, cam_to=V_TOP_LINE,
        labels=[("lid window, front facet: DAL's 60 x 64 mm\nglass-ceramic pane in its 8-screw plate",
                 tuple(W(CAMS.window_pose()["centre"])), (0.06, 0.70)),
                ("HQ + 16 mm C lens, hot mirror, variable ND", tuple(W(POSES0["top_hq"]["eye"])), (0.06, 0.25)),
                ("aim: crucible datum + 20 mm of melt", tuple(W(CAMS.AIM + np.array([0, -20, 60]))), (0.70, 0.80))])
cap = ("Front: both cameras look in along the port's axis, 20 deg up from the plate. The HQ (16 mm M12 lens) sees "
       "about 65 x 49 mm at 165 mm, the impact zone; the Camera Module 3 Wide (102 x 67 deg) the nozzle, plate and chamber.")
sc.step("2/6", cap, 3.0, los_in(["front_hq", "front_wide"]), hold=2.2, cam_to=V_FRONT,
        labels=[("HQ (M12), 15 mm left of the axis", tuple(W(POSES0["front_hq"]["eye"])), (0.08, 0.30)),
                ("Camera Module 3 Wide, 18.5 mm right", tuple(W(POSES0["front_wide"]["eye"])), (0.70, 0.28)),
                ("AMAZEMET's LED cover: the socket\nslides 15 mm over it, keyed by its cable pod",
                 tuple(W((-60, -200, 960))), (0.08, 0.72))])
cap = ("Left: a Camera Module 3 Wide on the door's sight-glass axis, side on. DAL put it here to see where the stream "
       "lands (on 6 Oct it hit the upper sonotrode). Here the landing point is 49 deg below its axis: outside its 67 deg "
       "and the 44 mm bore through the door.")
sc.step("2/6", cap, 3.0, los_in(["left_wide"]), hold=2.2, cam_to=V_LEFT,
        labels=[("split collar on the sight-glass ring (one M4)", tuple(W((-170, -45, 1095))), (0.08, 0.25)),
                ("5 in Touch Display 2, facing the operator", tuple(W((-208, -50, 1030))), (0.08, 0.75))])


def los_out(u):
    for n in los_names:
        sc.alpha[n] = max(0.0, 1.0 - u * 2) if sc.alpha[n] > 0 else 0.0


# ======================================================================================== 3. parked for loading
gauges(Units="front, left, top", Top_arm="working dimple", Furnace="cold, lid shut", MiR_1="driving")
cap = ("To load the crucible the top arm swings 90 deg about its post to a second dimple, clear of the furnace (DAL). "
       "MiR250 1 comes up to the front of the machine.")
up_d, secs = AB.mir_drive(ma, SPOT)
sc.step("3/6", cap, secs, AB.both(up_d, los_out), hold=0.3, cam_to=V_SWING)
gauges(Units="front, left, top", Top_arm="working dimple", Furnace="cold, lid shut", MiR_1="at the machine")
cap = ("The UR10e reaches up to the 2020 extrusion, 300 mm out from the post, and closes the 2F-85 on its top and "
       "bottom faces, on the side away from the way it will turn.")
sc.step("3/6", cap, 1.0, rb.grip_to(0.0), hold=0.1)
sc.step("3/6", cap, 2.6, rb.joint_to(q1=Q_PRE), hold=0.1)
sc.step("3/6", cap, 1.2, play(PLAN["in0"]), hold=0.1)
sc.step("3/6", cap, 0.7, rb.grip_to(CLOSE_BAR), hold=0.2,
        labels=[("2F-85 on the extrusion, 300 mm from the post", tuple(W(CAMS.extrusion_point(GRIP_S, 0.0))),
                 (0.70, 0.22))])
rb.grasp(CAMS.GROUPS["arm"])
cap = ("It swings the arm 90 deg about the post, over the blue frame's top, until the ball plunger in the hub clicks "
       "into the 'parked' dimple of the detent collar (M6 plunger; DAL's design).")
gauges(Units="front, left, top", Top_arm="swinging", Furnace="cold, lid shut", MiR_1="at the machine")
sc.step("3/6", cap, 4.0, swing(0.0, 1.0), hold=0.4,
        labels=[("detent collar: 'working' and 'parked'\ndimples, 90 deg apart", tuple(W((-90, 200, 1778))),
                 (0.70, 0.30))])
gauges(Units="front, left, top", Top_arm="parked dimple", Furnace="cold, lid shut", MiR_1="at the machine")
sc.step("3/6", "Click: parked. The 2F-85 lets go and backs off.", 0.6, rb.grip_to(0.0), hold=0.1)
rb.release("rp")
CAMS.set_top_arm(sc, 1.0)
sc.step("3/6", "Click: parked. The 2F-85 lets go and backs off.", 1.0, play(PLAN["out1"]), hold=0.2)
if LID_CLEAR[0] < 25.0:
    cap = (f"Why it parks. The lid opens up and over to the left (ghost) and passes only {LID_CLEAR[0]:.0f} mm from the "
           f"arm in its working dimple (DAL: 118 mm); the loading arm's wrist and tong also come in over the furnace.")
else:
    cap = (f"Why it parks. The lid opens up and over to the left (ghost), {LID_CLEAR[0]:.0f} mm clear of the arm in its "
           f"working dimple (DAL: 118 mm). The loading arm's wrist and tong come in over the furnace, where the arm, "
           f"pod and display box hang, 1.68-1.84 m up.")
sc.step("3/6", cap, 2.0, lambda u: ghosts(u), hold=2.8, cam_to=V_LIDG,
        labels=[("the lid's swing, hinged on the left (ghost, 52 and 105 deg)", tuple(W((-300, 0, 1560))), (0.06, 0.30)),
                ("top arm, parked over the frame", tuple(W(CAMS.extrusion_point(300, 1.0))), (0.70, 0.30))])
sc.step("3/6", cap, 0.8, lambda u: ghosts(1.0 - u), hold=0.1)
gauges(Units="front, left, top", Top_arm="parked dimple", Furnace="loaded, lid shut", MiR_1="at the machine")
cap = ("Loaded and the lid shut again (the charge and the lid are other clips). The arm grips the extrusion again "
       "and swings it back until it clicks into the 'working' dimple: the camera's aim comes back to the same place.")
sc.step("3/6", cap, 1.4, play(PLAN["out1"][::-1]), hold=0.1, cam_to=V_SWING)
sc.step("3/6", cap, 0.7, rb.grip_to(CLOSE_BAR), hold=0.1)
rb.grasp(CAMS.GROUPS["arm"])
gauges(Units="front, left, top", Top_arm="swinging", Furnace="loaded, lid shut", MiR_1="at the machine")
sc.step("3/6", cap, 4.0, swing(1.0, 0.0), hold=0.4)
gauges(Units="front, left, top", Top_arm="working dimple", Furnace="loaded, lid shut", MiR_1="at the machine")
sc.step("3/6", "Click: working. The 2F-85 lets go and the arm folds back.", 0.6, rb.grip_to(0.0), hold=0.1)
rb.release("rp")
CAMS.set_top_arm(sc, 0.0)
sc.step("3/6", "Click: working. The 2F-85 lets go and the arm folds back.", 1.0, play(PLAN["in0"][::-1]),
        hold=0.1)
sc.step("3/6", "Click: working. The 2F-85 lets go and the arm folds back.", 2.4, rb.joint_to(q1=q_home), hold=0.2)
up_d, secs = AB.mir_drive(ma, (250.0, -1250.0, 0.0))
gauges(Units="front, left, top", Top_arm="working dimple", Furnace="loaded, lid shut", MiR_1="driving away")
sc.step("3/6", "MiR250 1 drives back to its waiting spot, clear of the operator's places at the displays.", secs,
        up_d, hold=0.2, cam_to=V_ALL)

# ======================================================================================== 4. the displays
gauges(Units="front, left, top", Top_arm="working dimple", Furnace="loaded, lid shut", MiR_1="waiting")
cap = ("Front: the 5 in HDMI display (Elecrow, 800 x 480) shows both feeds side by side, facing out along the port, "
       "20 deg up to a standing operator. It is HDMI because the two cameras take both of the Pi 5's camera ports.")
sc.step("4/6", cap, 3.0, None, hold=2.4, cam_to=V_DISP_FRONT,
        labels=[("front Pi 5: HQ on CSI0, Camera Module 3 Wide on CSI1,\ndisplay on micro-HDMI",
                 tuple(W((-20, -235, 1095))), (0.06, 0.25))])
cap = ("Left: the 5 in Touch Display 2 (DSI), the largest picture, beside the operator's hands at the stack. The "
       "unit rides on the door. Touch stays off on all three; nothing is controlled from them (DAL).")
sc.step("4/6", cap, 3.0, None, hold=2.4, cam_to=V_DISP_LEFT,
        labels=[("left Pi 5: Camera Module 3 Wide on CSI0,\nTouch Display 2 on DSI", tuple(W((-205, 20, 1015))),
                 (0.06, 0.25))])
cap = ("Top: a 2.8 in DSI display (Waveshare, 480 x 640) at the arm's tip, tilted 30 deg down to the operator: a "
       "glance at whether the charge has melted. Its Pi 5 is in the box behind it.")
sc.step("4/6", cap, 3.0, None, hold=2.4, cam_to=V_DISP_TOP,
        labels=[("top Pi 5: HQ on CSI0, 2.8 in DSI display", tuple(W((20, -300, 1830))), (0.06, 0.25))])
cap = ("The atomizer's own HMI (Weintek, 15.6 in) is separate. The 5 in HDMI panel was bench-tested on 13 Nov on "
       "the lab's atomizer HMI Pi: 800 x 480 set by hand (no EDID), two feeds side by side at 30 fps, none dropped.")
sc.step("4/6", cap, 3.0, None, hold=2.4, cam_to=V_HMI,
        labels=[("atomizer HMI (Weintek cMT2166X)", tuple(W(M.HMI_C)), (0.70, 0.25))])

# ======================================================================================== 5. the melt
feeds.pip(["top_hq"])
st = dict(level=-M.FLOOR_CONE_H)
SLUG_GROUPS = [AB.g(f"slug{k}") for k in range(4)]


def heat(u):
    t = 25 + (640 - 25) * u
    AA.coil_glow(sc, min(1.0, u * 3))
    col = AA.temp_color(t, cold=(0.80, 0.81, 0.84))
    for n in slug_actors:
        sc.color[n] = col
        sc.ambient[n] = 0.2 + 0.6 * max(0.0, (t - 450) / 300)
    gauges(Furnace=f"{t:.0f} C, coil on", Top_arm="working dimple", Feed="top HQ on the 2.8 in display")


cap = ("The coil heats the charge under argon. The top camera watches through the lid window: the hot mirror and "
       "the ND keep the glowing charge from saturating the sensor.")
sc.step("5/6", cap, 3.0, heat, hold=0.4, cam_to=V_MELT,
        labels=[("top feed on its own display", tuple(W((20, -330, 1790))), (0.06, 0.70))])


def slump(u):
    t = 640 + 110 * u
    for k, (grp, c) in enumerate(zip(SLUG_GROUPS, SLUG_C)):
        f = 1.0 - 0.97 * window(u, 0.05 + 0.08 * k, 0.65 + 0.07 * k)
        sc.gmat[grp] = S((1.0 + 0.1 * (1 - f), 1.0 + 0.1 * (1 - f), f), (c[0], c[1], M.Z_CR))
        for n in sc.members(grp):
            sc.alpha[n] = 1.0 if f > 0.06 else 0.0
    st["level"] = -M.FLOOR_CONE_H + (LEVEL_END + M.FLOOR_CONE_H) * window(u, 0.08, 0.95)
    set_melt(st["level"])
    AA.coil_glow(sc, 1.0)
    gauges(Furnace=f"{t:.0f} C, coil on", Top_arm="working dimple", Feed="top HQ on the 2.8 in display")


cap = ("The slugs slump and run together into a pool round the sealing rod. The pool's surface is about 20-30 mm over "
       "the crucible's datum, where DAL aimed the camera.")
sc.step("5/6", cap, 5.0, slump, hold=1.2,
        labels=[("melt, seen at 66 deg through the window", tuple(W((0, -10, M.Z_CR + LEVEL_END))), (0.06, 0.70))])

# ======================================================================================== 6. the pour
feeds.pip(["front_hq", "front_wide", "left_wide"])
drain = (LEVEL_END + 6.0) / (9.0 * FPS)


def rod_up(u):
    AA.rod_lift(sc, 13.5 * window(u, 0.15, 0.45))
    AA.stream(sc, 1.0 if u > 0.45 else 0.0, 1.0, STREAM_F * window(u, 0.45, 0.75))
    AA.film(sc, u > 0.75)
    if u > 0.75 and sc.n % 2 == 0:
        drops.emit_drops(2, M.IMPACT + np.array([0, 0, 3]), M.PLATE_UP * 250 + M.STACK_DIR * 500)
    drops.step()
    gauges(Furnace="750 C", Plate="40 kHz", Argon="+200 mbar on the furnace", Feed="front and left on their displays")


cap = ("Vibration on, argon over-pressure on the furnace, the sealing rod up: the stream falls through the nozzle "
       "onto the vibrating plate. The front and left feeds show it on their displays and here.")
sc.step("6/6", cap, 3.0, rod_up, hold=0.4, live=True, cam_to=V_POUR,
        labels=[("left unit's display: the side view", tuple(W((-208, -50, 1030))), (0.06, 0.30)),
                ("front unit's display: HQ | wide", tuple(W((-15, -240, 1090))), (0.06, 0.70))])


def atomize(u, rate=24):
    AA.stream(sc, 1.0, 1.0, STREAM_F)
    spray.emit_spray(int(round(rate * 15 / FPS)))
    spray.step()
    drops.step()
    st["level"] = max(-12.0, st["level"] - drain)
    set_melt(st["level"])


cap = ("Front HQ, on the port's axis: the stream in mid-air and the sonotrode's end; the landing point is 24 deg "
       "below its axis, as DAL found on 5 Nov. The front wide sees the landing. The left sees the nozzle and the "
       "stream's top only.")
sc.step("6/6", cap, 6.0, atomize, hold=0.8, live=True, still=True,
        labels=[("left unit (on the door)", tuple(W((-190, 20, 1015))), (0.06, 0.30)),
                ("front unit", tuple(W((-15, -240, 1060))), (0.06, 0.70))])


def tail(u):
    st["level"] = max(-18.0, st["level"] - 2 * drain)
    set_melt(st["level"], on=u < 0.85)
    AA.stream(sc, 1.0 if u < 0.6 else 0.0, 1.0 - 0.6 * u, STREAM_F)
    AA.film(sc, u < 0.7)
    if u < 0.6:
        spray.emit_spray(int(round(18 * (1 - u) * 15 / FPS)))
    spray.step()
    drops.step()
    AA.coil_glow(sc, 1.0 - u)
    gauges(Furnace=f"{750 - 200 * u:.0f} C", Plate="off" if u > 0.7 else "40 kHz", Argon="+200 mbar",
           Feed="front and left on their displays")


cap = ("The crucible runs empty and the coil and the plate stop. Each unit also streams to YouTube in the same "
       "picamera2 process (DAL); nothing here has been printed or bench-tested with cameras yet.")
sc.step("6/6", cap, 3.0, tail, hold=1.2, live=True)
feeds.pip(None)
AB.finish(sc)
if not (AUDIT or PREVIEW):
    print(sc.auditor.save(), flush=True)
if not (AUDIT or PREVIEW):
    info = dict(spot_model_xy_yaw=SPOT, grip_s_mm=GRIP_S, close=CLOSE_BAR,
                cameras={k: dict(eye=[round(float(x), 1) for x in p["eye"]], dir=[round(float(x), 3) for x in p["dir"]],
                                 hfov=p["hfov"], vfov=p["vfov"], pi=p["pi"], display=p["display"])
                         for k, p in POSES0.items()})
    (OUT / "atom" / "cameras_poses.json").write_text(json.dumps(info, indent=1) + "\n")

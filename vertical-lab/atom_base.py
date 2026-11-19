"""The shared scene for the atomizer-automation clips (PR #353, stacked on #318 for #303).

Every clip in this series (``atom_*.py``) works on the AMAZEMET rePowder as ``repowder/model.py`` draws it after PR
#327 (the lid hinged at the back, the chamber door hinged at its back edge, two swing-bolt clamps, the viewport on the
front face) and after this PR's third-pass latch (the lever pivoting at its top, the loop with its own joint, the bolt
through the base: notes/repowder_refine.md, "Third pass"). The model's own frame is used throughout: x right (the
chamber's door is on its left wall, x = -115), y back (the front face is at y = -120; the blue cabinet behind, y > 165),
z up from the floor; the furnace axis is x = y = 0. ``W()``/``WT()``/``cam()`` take model-frame points and poses to
the world, where the rePowder stands at ``alloy_atomize.RP``.

    import atom_base as AB
    sc, ma, mb = AB.build("atom_latch", "Vertical cloud lab: the furnace latch, unclamped and clamped")
    AB.set_joints(sc, bolt=1.0)                         # model joints, 0..1 of their travel (AB.JOINTS)
    rb = ma.rb                                          # the UR10e + 2F-85 (+ D405) on MiR250 1
    sc.step("1/4", "caption", 1.6, rb.joint_to(Tw=AB.tcp((72, -260, 1250), (0, 1, 0))), cam_to=AB.cam(eye, at))
    sc.step("1/4", "caption", 1.0, AB.joint_anim(sc, "latch", 0.0, 0.2))
    AB.finish(sc)

Rendering: ``xvfb-run -a python3 atom_<clip>.py`` writes out/<name>.gif, out/mp4/<name>.mp4, out/<name>.json and
out/<name>_still.png (scene.py). ``ARM_AUDIT=1`` renders nothing and checks every frame (collide.py) into
out/collisions/<name>.json; ``PREVIEW=1`` renders the last frame of each sub-step to /tmp/preview_<name>.png. Run
anything that builds a scene through ``python3 runner_guard.py slot --label <name> -- ...`` (at most 3 at once).
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("ATOMIZE_LITE", "1")

import alloy_atomize as AA          # noqa: E402  the rePowder loader, the MiR250 + UR10e units, the camera helpers
import props as P                   # noqa: E402
import robot as RB                  # noqa: E402
from scene import OUT, R, T, Scene  # noqa: E402

M = AA.M                             # repowder/model.py
RP = np.asarray(AA.RP, float)        # the rePowder's origin in the world
g = AA.g                             # a rePowder part group -> its scene group ("rp:<group>")
status = AA.status                   # the gauge rows in the frame's corner: status(sc, Furnace="250 C", ...)

# the scene group each model joint moves (load_rp puts a part in group "rp:<part.group>"; the knob rides the hood)
JOINT_GROUP = {"lid": "hood", "latch": "latch_lever", "loop": "latch_loop", "bolt": "latch_bolt", "door": "door",
               "clamp0": "clamp0", "clamp1": "clamp1"}
JOINTS = tuple(JOINT_GROUP)
FLOOR_C = (0.93, 0.93, 0.92)
TAPE_C = (0.95, 0.78, 0.10)          # the yellow floor tape round the atomizer's containment area (DAL daily SOP)
# where the two MiR250s park, model frame (x, y, yaw deg). FRONT: in front of the chamber for the furnace, the lid
# and the container; LEFT: beside the door, facing it, for the chamber, the stack and the nut under the crucible.
PARK = dict(front=(150.0, -760.0, 0.0), front_left=(-560.0, -620.0, 0.0), left=(-760.0, -40.0, 90.0),
            right=(760.0, -560.0, 0.0))


def W(p) -> np.ndarray:
    """A model-frame point -> the world."""
    return np.asarray(p, float)[:3] + RP


def WT(Mx) -> np.ndarray:
    """A model-frame 4x4 pose -> the world."""
    return T(RP) @ np.asarray(Mx, float)


def cam(eye, at, up=(0, 0, 1)) -> list:
    """A camera given in the model frame."""
    return [tuple(W(eye)), tuple(W(at)), tuple(up)]


def tcp(p, approach, spin=0.0) -> np.ndarray:
    """The gripper's grasp point (TCP) at model point p, pointing along `approach` (the tool's z), turned `spin` deg
    about it; world pose. The 2F-85's fingers close along the TCP frame's x axis (ur_arm.py)."""
    return P.tcp_frame(tuple(W(p)), tuple(np.asarray(approach, float)), spin)


def mir_at(m, where: str | tuple):
    """Park a MiR250 at PARK[where] (or an (x, y, yaw) in the model frame)."""
    x, y, yaw = PARK[where] if isinstance(where, str) else where
    m.set(x + RP[0], y + RP[1], yaw)


def mir_drive(m, where: str | tuple):
    """(update(u), seconds): a MiR250 driven to PARK[where] (or a model-frame (x, y, yaw)) along an S-curve at its
    published 0.3 m/s^2 (alloy_atomize.Mir.drive: it heads along the curve), then turned on the spot to the yaw."""
    x, y, yaw = PARK[where] if isinstance(where, str) else where
    x, y = x + RP[0], y + RP[1]
    f, secs = m.drive(x, y), m.secs(x, y)
    state = {}

    def up(u):
        f(min(1.0, u / 0.85))
        if u > 0.85:
            y0 = state.setdefault("yaw0", m.yaw)
            d = (yaw - y0 + 180.0) % 360.0 - 180.0
            m.set(m.x, m.y, y0 + d * (u - 0.85) / 0.15)
    return up, secs + 1.5


def mir_turn(m, yaw: float):
    """update(u): turn a MiR250 on the spot to `yaw` (deg)."""
    y0 = m.yaw
    d = (yaw - y0 + 180.0) % 360.0 - 180.0
    return lambda u: m.set(m.x, m.y, y0 + d * u)


# ---------------------------------------------------------------------------------------------- joints
def set_joints(sc, **vals):
    """Set model joints (0..1 of their travel; M.joints()), keeping the others where they were. A child joint (the
    loop on the latch's lever) is set in its parent's frame, so it rides along."""
    cur = getattr(sc, "joint_vals", None)
    if cur is None:
        cur = sc.joint_vals = {k: 0.0 for k in JOINTS}
    cur.update({k: float(v) for k, v in vals.items()})
    js = M.joints()
    for name, grp in JOINT_GROUP.items():
        j = js[name]
        if j.get("parent"):
            sc.parent[g(grp)] = g(JOINT_GROUP[j["parent"]])
        sc.gmat[g(grp)] = M.joint_matrix(name, cur[name])
    return cur


def joint_anim(sc, name: str, v0: float, v1: float, also=None):
    """update(u): joint `name` from v0 to v1 (0..1 of its travel); `also(u)` called too, if given."""
    def up(u):
        set_joints(sc, **{name: v0 + (v1 - v0) * u})
        if also is not None:
            also(u)
    return up


def latch_hooked(sc, v_latch: float):
    """The lever at v_latch with the loop still hooked on the keeper (its cross bar kept on the lip)."""
    set_joints(sc, latch=v_latch, loop=M.loop_aim_deg(v_latch) / M.LOOP_OPEN_DEG)


def part_world(name: str, Mx=None) -> np.ndarray:
    """World pose of a rePowder group's frame (the model frame moved by its joint or by Mx), for grasps."""
    return WT(np.eye(4) if Mx is None else Mx)


# ---------------------------------------------------------------------------------------------- the scene
def build(name: str, title: str, *, mirs: int = 2, ghost: dict | None = None, tape: bool = True):
    """The rePowder on its floor with the two MiR250 + UR10e units (ballasted, round 9): (sc, mir_a, mir_b).
    mir_a carries chapter 1's cup carrier and the container's cradle (alloy_atomize.Mir); mir_b carries nothing.
    The units start at PARK["front"] and PARK["front_left"]."""
    sc = Scene(name, title)
    sc.add("atom floor", pv.Plane(center=(RP[0], RP[1] - 600, -1.5), direction=(0, 0, 1), i_size=9000, j_size=7000),
           FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    if tape:                                      # the containment area's tape, 600 mm round the machine (ours)
        x0, x1, y0, y1 = -1300.0, 1500.0, -1600.0, 1000.0
        for k, (a, b) in enumerate((((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0)))):
            c = (np.array(a) + np.array(b)) / 2
            ln = float(np.linalg.norm(np.array(b) - np.array(a)))
            horiz = abs(a[1] - b[1]) < 1
            sc.add(f"atom tape {k}", pv.Box(bounds=(c[0] - (ln / 2 if horiz else 25), c[0] + (ln / 2 if horiz else 25),
                                                     c[1] - (25 if horiz else ln / 2), c[1] + (25 if horiz else ln / 2),
                                                     -1.0, 0.5)).translate((RP[0], RP[1], 0), inplace=False),
                   TAPE_C, "floor", ambient=0.9, diffuse=0.2, specular=0.0)
    for k in range(4):
        sc.parent.setdefault(g(f"slug{k}"), "rp")
    AA.load_rp(sc, ghost=ghost if ghost is not None else {"stack_cover": 0.35})
    for k in range(4):
        sc.show(sc.members(g(f"slug{k}")), 0.0)
    set_joints(sc)
    AA.flange_clamp(sc, 1.0)
    ma = mb = None
    if mirs >= 1:
        ma = AA.Mir(sc)
        sc.show([n for n in sc.members("amr") if "cup carrier" in n], 0.0)
        mir_at(ma, "front")
    if mirs >= 2:
        mb = AA.Mir(sc, g="amrB", prefix="urB", cargo=False)
        mir_at(mb, "front_left")
    sc.intro = 0.8
    return sc, ma, mb


def finish(sc):
    """Write the clip (or the audit, or the preview sheet)."""
    return sc.save()


def caption_rows(sc, **rows):
    """Replace the gauge rows wholesale (alloy_atomize.status merges; this starts clean)."""
    sc._rows = {}
    status(sc, **{k: v for k, v in rows.items() if v})


both = RB.both

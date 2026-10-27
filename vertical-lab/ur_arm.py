"""Universal Robots e-Series arms (UR3e, UR7e, UR10e) with a Robotiq 2F-85 gripper, for the vertical-lab animations.

Everything is the vendors' own ROS 2 description, fetched at run time at a pinned commit, SHA-256 checked and
cached under ``.cache/ur_arm/`` (never committed):

* Arm: github.com/UniversalRobots/Universal_Robots_ROS2_Description (BSD-3-Clause). Visual meshes are
  ``meshes/<model>/visual/*.dae``. The joint origins (``config/<model>/default_kinematics.yaml``), the
  visual-mesh origins (``config/<model>/visual_parameters.yaml``) and the link chain
  (``urdf/ur_macro.xacro``) are transcribed below. The UR7e has no meshes of its own: its
  ``visual_parameters.yaml`` points at the UR5e's, and its kinematics are the UR5e's (same arm, re-rated).
* Gripper: github.com/PickNikRobotics/ros2_robotiq_gripper (BSD-3-Clause), ``robotiq_description``: the
  2F-85 visual meshes, joint origins and mimic relations of ``urdf/robotiq_2f_85_macro.urdf.xacro``, and
  the UR coupling of ``urdf/ur_to_robotiq_adapter.urdf.xacro``.

Frames are in millimetres, z up. The arm's base frame is the UR controller's ``base`` frame: DH frame 0, the
URDF's ``base_link_inertia`` (ROS's ``base_link`` is this turned 180 deg about z). Joint angles are the
controller's, so at q = 0 the arm lies horizontal along -x with tool0 at (a2 + a3, -(d4 + d6), d1 - d5)
pointing along -y, as the teach pendant shows. ``fk`` uses the URDF joint chain, which reproduces UR's DH
table to within 1e-6 mm; ``tool0`` is the flange (the URDF's tool0, which coincides with wrist_3_link).

The gripper's fingers close along tool0's x axis. ``close`` 0 is fully open (85 mm between the pads) and 1
is the driver's closed position (knuckle 0.7929 rad, pads touching). The fingertips swing on an arc, so the
grasp point moves 13.5 mm along z over the stroke: ``TCP_MM`` is the closed value (within 1 mm of the truth
for any part under 30 mm wide); ``tcp_mm(close)`` gives the rest, and ``ik(..., tcp_mm=...)`` takes it.

Colours are the .dae materials', sRGB-encoded (Blender exports linear values; VTK shows numbers as given).

    import ur_arm
    links = ur_arm.arm_meshes("ur10e")          # {"base": [(mesh, rgb, specular), ...], ...}
    T = ur_arm.fk("ur10e", q)                   # {"base": 4x4, ..., "tool0": 4x4}
    G = ur_arm.gripper_fk(0.5)                  # {"base": 4x4 relative to tool0, ...}
    q = ur_arm.ik("ur10e", T_tcp, q_seed)       # TCP = tool0 moved TCP_MM along its z
"""
from __future__ import annotations

import functools
import hashlib
import math
import pickle
import urllib.request
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache" / "ur_arm"

UR_SHA = "81f7c9fe003c2f0e02eec5a7253f1b262ad38b61"      # Universal_Robots_ROS2_Description, rolling, 2026-10-27
RQ_SHA = "a74d007d8f2f06dc6a503ad21038ba869d4999a6"      # ros2_robotiq_gripper, main, 2026-10-27
UR_URL = ("https://raw.githubusercontent.com/UniversalRobots/Universal_Robots_ROS2_Description/"
          f"{UR_SHA}/meshes/{{mesh}}/visual/{{part}}.dae")
RQ_URL = ("https://raw.githubusercontent.com/PickNikRobotics/ros2_robotiq_gripper/"
          f"{RQ_SHA}/robotiq_description/meshes/visual/2f_85/{{part}}.dae")

SHA256 = {
    "ur3e/base": "2392d48fd62ec9ab579702ef7548c303bcf2dd41fc895cb7f410d9d2bde5ab9e",
    "ur3e/shoulder": "d047f6b253e3c5f295717818923bf337a7d2f2583395cb99a1e60b696b226191",
    "ur3e/upperarm": "c1b7280deb24b227903c1f5943b6d50221ef1aa30b92a0709abeb9d93852a879",
    "ur3e/forearm": "410cd4771845c9434139e1fe41a4171296f7115b7a82211ebfaefc90732811c1",
    "ur3e/wrist1": "de8c42623011c04ab09626f8dfd7e2d07fe05ac04b0e92b765d9b7c924faaa7e",
    "ur3e/wrist2": "e010c1d8c1802b150110782cc3ab993e51aeacaa096b871bd72ba8d46ea7b109",
    "ur3e/wrist3": "2eec93dd08aa9380763bcb314851558602f015759afb43af9bb249eea0661ed5",
    "ur5e/base": "c30e4d7228ef633dca2a02c26df2316741f6642cb6333e8289dba6e6d0b22819",
    "ur5e/shoulder": "c581bfa55b86061d9b99d315ed53817b6b693e6a500643bbf9bbb783322d585d",
    "ur5e/upperarm": "c040a05bb224f14cfab6aa6704d70cbb773ada940eca9a3e34e6ce486c4c4c29",
    "ur5e/forearm": "04694bf57dac46e9b8bc7c30f2eec75a1bc762e1f1a879ea30c944f24cacbad8",
    "ur5e/wrist1": "a07a3d96d2540f9be12e4a07bcb8577d9f1e36005920c396a407804343a3b588",
    "ur5e/wrist2": "982fa42933c6f81629882ad7975e9ba5dac5d474a6b56694e233708376cf840e",
    "ur5e/wrist3": "7a7664ac4adcd53b0870fe6a2b8b975693d846dd4d07a5f44194c7d16f4890ba",
    "ur10e/base": "28226d95af8c1579a49fe69b62a00d9133a2a05258dad550bb9b583c80dc938f",
    "ur10e/shoulder": "1c38a6afedfb8f064117da87b60c2dcb9ccd107f957e4c5e0a198f4c2bb63d36",
    "ur10e/upperarm": "f9d2380d14127440f4a50ed79ab4e7562f86289cd6131016c3d49a3e7483e6ed",
    "ur10e/forearm": "24d909834c380cceb0490181dae40bcdfcfa4a7fb0c6807d6e58794cdfadcf6e",
    "ur10e/wrist1": "643717d042920313dd9daa81511bd9afa66a877625967e6dd8d359ec851b4237",
    "ur10e/wrist2": "b820e8c8a4488563c7a21fe73bf2fa4038ec9f882dcf9db12e2d1df928253793",
    "ur10e/wrist3": "52ace7588f131dc43b49ba88d1c83c1f871e6d00659ea84b1f437e2a7f1ab7fe",
    "2f_85/ur_to_robotiq_adapter": "ed326c745df2942d2efb8dd902ecfafa84c692d360a7c03ce9276ad491614ac4",
    "2f_85/robotiq_base": "761a79d586a48d367d60f146ca77ef7d2821ad790f7b1b1c93b061ac59799267",
    "2f_85/left_knuckle": "1b82214363d9548f3562be70e25cd23217a304c72ccd37bc1551cf1a3a64029d",
    "2f_85/right_knuckle": "532b6f6f8794883ff34995701036ca392461f26127757f92003db127693bc57c",
    "2f_85/left_finger": "5fb9e5659c735e48eb55269da431cf61b3b7a6745922c1932a7adefb1db86dc3",
    "2f_85/right_finger": "3b2245b5537eb596d7f8a4c64b12e3aedea46e365fc589019184d3b4200e664f",
    "2f_85/left_inner_knuckle": "2df009ef28868c90a4904370f5f4995c74ec84e0b8ca1371044e0ea669edcd71",
    "2f_85/right_inner_knuckle": "4cc6de99e177773ba755805b58b67537c3af24b2fd8f3a1bf4bbced87d6240a5",
    "2f_85/left_finger_tip": "785ec7a83b4fc6357c211a39bb117833b1cfd4e9bccbef2efc7f35aeb2fdb92e",
    "2f_85/right_finger_tip": "568371d25ddbcee8e432c0610bdcc7afcd1393d48d973eed92168e353eb4edf5",
}

_SRC_UR = f"UniversalRobots/Universal_Robots_ROS2_Description@{UR_SHA[:7]}"
# Datasheet figures (universal-robots.com); dh is UR's published DH table in mm, a2 and a3 negative as UR gives them.
MODELS = {
    "ur3e": dict(reach_mm=500, payload_kg=3.0, base_diameter_mm=128, mass_kg=11.2,
                 dh=dict(d1=151.85, a2=-243.55, a3=-213.2, d4=131.05, d5=85.35, d6=92.1),
                 source=f"{_SRC_UR}: meshes/ur3e, config/ur3e"),
    "ur7e": dict(reach_mm=850, payload_kg=7.5, base_diameter_mm=151, mass_kg=20.6,
                 dh=dict(d1=162.5, a2=-425.0, a3=-392.2, d4=133.3, d5=99.7, d6=99.6),
                 source=f"{_SRC_UR}: meshes/ur5e (the UR7e reuses them), config/ur7e"),
    "ur10e": dict(reach_mm=1300, payload_kg=12.5, base_diameter_mm=190, mass_kg=33.5,
                  dh=dict(d1=180.7, a2=-612.7, a3=-571.55, d4=174.15, d5=119.85, d6=116.55),
                  source=f"{_SRC_UR}: meshes/ur10e, config/ur10e"),
}
_MESH_SET = {"ur3e": "ur3e", "ur7e": "ur5e", "ur10e": "ur10e"}

LINKS = ("base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3")
_DAE = dict(base="base", shoulder="shoulder", upper_arm="upperarm", forearm="forearm", wrist1="wrist1",
            wrist2="wrist2", wrist3="wrist3")
_H = math.pi / 2
# visual_parameters.yaml mesh_offset per mesh set: x, y, z (mm), roll, pitch, yaw (rad)
_VISUAL = {
    "ur3e": dict(base=(0, 0, 0, 0, 0, math.pi), shoulder=(0, 0, 0, 0, 0, math.pi),
                 upper_arm=(0, 0, 120, _H, 0, -_H), forearm=(0, 0, 27, _H, 0, -_H),
                 wrist1=(0, 0, -104, _H, 0, 0), wrist2=(0, 0, -85.35, 0, 0, 0), wrist3=(0, 0, -92.1, _H, 0, 0)),
    "ur5e": dict(base=(0, 0, 0, 0, 0, math.pi), shoulder=(0, 0, 0, 0, 0, math.pi),
                 upper_arm=(0, 0, 138, _H, 0, -_H), forearm=(0, 0, 7, _H, 0, -_H),
                 wrist1=(0, 0, -127, _H, 0, 0), wrist2=(0, 0, -99.7, 0, 0, 0), wrist3=(0, -0.5, -98.9, _H, 0, 0)),
    "ur10e": dict(base=(0, 0, 0, 0, 0, math.pi), shoulder=(0, 0, 0, 0, 0, math.pi),
                  upper_arm=(0, 0, 176.2, _H, 0, -_H), forearm=(0, 0, 39.3, _H, 0, -_H),
                  wrist1=(0, 0, -135, _H, 0, 0), wrist2=(0, 0, -120, 0, 0, 0), wrist3=(0, -0.5, -116.8, _H, 0, 0)),
}
_LIMIT = np.array([2, 2, 1, 2, 2, 2]) * math.pi     # joint limits, +-: the ROS description halves the elbow's

MAX_TRIS = 60000            # links above this are decimated (none of the current meshes are); settable at run time


# --------------------------------------------------------------------------------------------- transforms
def _rpy(roll, pitch, yaw) -> np.ndarray:
    """URDF rpy: fixed-axis x, then y, then z."""
    cr, sr, cp, sp, cy, sy = (math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch), math.cos(yaw),
                              math.sin(yaw))
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def _origin(x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = _rpy(roll, pitch, yaw)
    m[:3, 3] = (x, y, z)
    return m


def _rot(axis, t) -> np.ndarray:
    """4x4 rotation by t (rad) about a unit axis through the origin."""
    x, y, z = axis
    c, s = math.cos(t), math.sin(t)
    m = np.eye(4)
    m[:3, :3] = [[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                 [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                 [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]]
    return m


def _rz(t) -> np.ndarray:
    return _rot((0.0, 0.0, 1.0), t)


# --------------------------------------------------------------------------------------------- kinematics
@functools.lru_cache(maxsize=None)
def _joint_origins(model: str) -> tuple:
    """default_kinematics.yaml's six joint origins (mm), written with the DH numbers they were derived from
    (the yaml's ~1e-8 mm residuals in z are dropped)."""
    p = MODELS[model]["dh"]
    return (_origin(z=p["d1"]),
            _origin(roll=_H),
            _origin(x=p["a2"]),
            _origin(x=p["a3"], z=p["d4"]),
            _origin(y=-p["d5"], roll=_H),
            _origin(y=p["d6"], roll=_H, pitch=math.pi, yaw=math.pi))


def fk(model: str, q) -> dict[str, np.ndarray]:
    """4x4 transforms (mm) of base, shoulder, upper_arm, forearm, wrist1, wrist2, wrist3 and tool0 (the flange)
    in the arm's base frame, for joint angles q (6, rad)."""
    q = np.asarray(q, float).reshape(6)
    out = {"base": np.eye(4)}
    T = out["base"]
    for name, o, qi in zip(LINKS[1:], _joint_origins(model), q):
        T = T @ o @ _rz(qi)
        out[name] = T
    out["tool0"] = T.copy()           # flange -> tool0 undoes wrist_3 -> flange: tool0 is wrist_3_link
    return out


def _dh(model: str):
    p = MODELS[model]["dh"]
    return p["d1"], p["a2"], p["a3"], p["d4"], p["d5"], p["d6"]


def _ik_analytic(model: str, T06: np.ndarray, q6_free: float = 0.0) -> list[np.ndarray]:
    """All (up to 8) closed-form solutions for the flange pose T06 (mm), UR DH convention
    (alpha = 90, 0, 0, 90, -90, 0 deg). Joints 2-4 are parallel, so the wrist-centre plane fixes q1,
    the tool axis against joint 2's axis fixes q5 and q6, and q2-q4 are a planar 3R problem."""
    d1, a2, a3, d4, d5, d6 = _dh(model)
    R, p = T06[:3, :3], T06[:3, 3]
    p5 = p - d6 * R[:, 2]
    r = math.hypot(p5[0], p5[1])
    if r < abs(d4) - 1e-9:
        return []
    psi = math.atan2(p5[1], p5[0])
    phi = math.asin(max(-1.0, min(1.0, d4 / r)))
    sols = []
    for q1 in (psi + phi, psi + math.pi - phi):
        z1 = np.array([math.sin(q1), -math.cos(q1), 0.0])        # joint 2's axis
        c5 = float(np.clip(R[:, 2] @ z1, -1.0, 1.0))
        for q5 in (math.acos(c5), -math.acos(c5)):
            s5 = math.sin(q5)
            if abs(s5) < 1e-9:            # wrist singularity: only q4 + q6 matters; q6 is taken from the seed
                q6 = q6_free
            else:
                q6 = math.atan2(-(R[:, 1] @ z1) / s5, (R[:, 0] @ z1) / s5)
            # frame 4 in frame 1
            A1 = _dh_A(q1, d1, 0.0, _H)
            A5 = _dh_A(q5, d5, 0.0, -_H)
            A6 = _dh_A(q6, d6, 0.0, 0.0)
            T14 = np.linalg.inv(A1) @ T06 @ np.linalg.inv(A5 @ A6)
            px, py = T14[0, 3], T14[1, 3]
            c3 = (px * px + py * py - a2 * a2 - a3 * a3) / (2 * a2 * a3)
            if abs(c3) > 1 + 1e-9:
                continue
            c3 = max(-1.0, min(1.0, c3))
            for q3 in (math.acos(c3), -math.acos(c3)):
                q2 = math.atan2(py, px) - math.atan2(a3 * math.sin(q3), a2 + a3 * math.cos(q3))
                q234 = math.atan2(T14[1, 0], T14[0, 0])
                q4 = q234 - q2 - q3
                sols.append(np.array([q1, q2, q3, q4, q5, q6]))
    return sols


def _dh_A(theta, d, a, alpha) -> np.ndarray:
    ct, st, ca, sa = math.cos(theta), math.sin(theta), math.cos(alpha), math.sin(alpha)
    return np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d],
                     [0, 0, 0, 1.0]])


def _pose_err(T, T_goal) -> np.ndarray:
    """6-vector: position error (mm) and rotation-vector error (rad) of T relative to T_goal, in the base frame."""
    dp = T_goal[:3, 3] - T[:3, 3]
    Rerr = T_goal[:3, :3] @ T[:3, :3].T
    c = max(-1.0, min(1.0, (np.trace(Rerr) - 1) / 2))
    ang = math.acos(c)
    w = np.array([Rerr[2, 1] - Rerr[1, 2], Rerr[0, 2] - Rerr[2, 0], Rerr[1, 0] - Rerr[0, 1]])
    if ang < 1e-9:
        dw = w / 2
    elif ang > math.pi - 1e-6:          # near 180 deg: axis from the symmetric part
        k = np.sqrt(np.maximum((np.diag(Rerr) + 1) / 2, 0.0))
        k *= np.sign(w) + (w == 0)
        dw = ang * k / max(np.linalg.norm(k), 1e-12)
    else:
        dw = w * ang / (2 * math.sin(ang))
    return np.concatenate([dp, dw])


def _polish(model: str, q, T_goal, iters=8) -> np.ndarray:
    """Newton steps on the URDF chain with the geometric Jacobian (the analytic answer is already ~exact)."""
    q = np.array(q, float)
    for _ in range(iters):
        F = fk(model, q)
        e = _pose_err(F["tool0"], T_goal)
        if np.linalg.norm(e[:3]) < 1e-9 and np.linalg.norm(e[3:]) < 1e-12:
            break
        p_end = F["tool0"][:3, 3]
        J = np.zeros((6, 6))
        for i, name in enumerate(LINKS[1:]):
            z = F[name][:3, 2]
            J[:3, i] = np.cross(z, p_end - F[name][:3, 3])
            J[3:, i] = z
        lam = 1e-6
        q = q + J.T @ np.linalg.solve(J @ J.T + lam * np.eye(6), e)
    return q


def _wrap_near(q, seed) -> np.ndarray:
    """Each joint shifted by whole turns to the value nearest the seed that is inside the joint limits."""
    q = np.array(q, float)
    for i in range(6):
        k = np.round((seed[i] - q[i]) / (2 * math.pi))
        best = None
        for kk in (k - 1, k, k + 1):
            v = q[i] + 2 * math.pi * kk
            if abs(v) <= _LIMIT[i] + 1e-9 and (best is None or abs(v - seed[i]) < abs(best - seed[i])):
                best = v
        q[i] = best if best is not None else math.remainder(q[i], 2 * math.pi)
    return q


def ik(model: str, T_tcp: np.ndarray, q_seed, tcp_mm: float | None = None) -> np.ndarray:
    """Joint angles (rad) putting the TCP (the gripper's grasp point, TCP_MM along tool0's z) at the 4x4 pose
    T_tcp (mm) in the base frame: UR's closed-form solutions, each joint moved by whole turns towards q_seed,
    the one nearest q_seed, then a Newton polish. ValueError if the pose is out of reach. ``tcp_mm`` overrides
    TCP_MM (e.g. ``tcp_mm(close)`` for a partly closed grasp, or 0 for the bare flange)."""
    T_tcp = np.asarray(T_tcp, float)
    seed = np.asarray(q_seed, float).reshape(6)
    off = np.eye(4)
    off[2, 3] = -(TCP_MM if tcp_mm is None else tcp_mm)
    T06 = T_tcp @ off
    sols = [_wrap_near(s, seed) for s in _ik_analytic(model, T06, q6_free=float(seed[5]))]
    if not sols:
        raise ValueError(f"{model}: TCP pose out of reach (flange at {np.round(T06[:3, 3], 1).tolist()} mm)")
    sols.sort(key=lambda s: float(np.sum((s - seed) ** 2)))
    for s in sols:
        q = _polish(model, s, T06)
        e = _pose_err(fk(model, q)["tool0"], T06)
        if np.linalg.norm(e[:3]) < 1e-3 and np.linalg.norm(e[3:]) < 1e-6:
            return _wrap_near(q, seed)
    raise ValueError(f"{model}: IK did not converge for flange at {np.round(T06[:3, 3], 1).tolist()} mm")


# ------------------------------------------------------------------------------------------------ gripper
_KNUCKLE_CLOSED = 0.7929       # rad: the driver's gripper_closed_position (2f_85 macro default)
_Y = (0.0, -1.0, 0.0)          # every 2F-85 joint turns about the base's -y
GRIPPER_PARTS = ("adapter", "base", "left_knuckle", "right_knuckle", "left_finger", "right_finger",
                 "left_inner_knuckle", "right_inner_knuckle", "left_finger_tip", "right_finger_tip")
_GRIPPER_DAE = dict(adapter="ur_to_robotiq_adapter", base="robotiq_base", left_knuckle="left_knuckle",
                    right_knuckle="right_knuckle", left_finger="left_finger", right_finger="right_finger",
                    left_inner_knuckle="left_inner_knuckle", right_inner_knuckle="right_inner_knuckle",
                    left_finger_tip="left_finger_tip", right_finger_tip="right_finger_tip")


def gripper_fk(close: float) -> dict[str, np.ndarray]:
    """4x4 (mm) of every gripper part relative to tool0, close 0 (open) .. 1 (closed). The URDF's one actuated
    joint is the left knuckle; the rest follow it through their mimic multipliers (+1 or -1)."""
    t = float(np.clip(close, 0.0, 1.0)) * _KNUCKLE_CLOSED
    mm = 1000.0
    out = {"adapter": np.eye(4)}                                  # tool0 -> ur_to_robotiq_link, rotation 0
    base = out["adapter"] @ _origin(z=0.011 * mm)                 # gripper_side_joint; the gripper sits on it at 0
    out["base"] = base
    out["left_knuckle"] = base @ _origin(0.03060114 * mm, 0, 0.05490452 * mm) @ _rot(_Y, t)
    out["right_knuckle"] = base @ _origin(-0.03060114 * mm, 0, 0.05490452 * mm) @ _rot(_Y, -t)
    out["left_finger"] = out["left_knuckle"] @ _origin(0.03152616 * mm, 0, -0.00376347 * mm)
    out["right_finger"] = out["right_knuckle"] @ _origin(-0.03152616 * mm, 0, -0.00376347 * mm)
    out["left_inner_knuckle"] = base @ _origin(0.0127 * mm, 0, 0.06142 * mm) @ _rot(_Y, t)
    out["right_inner_knuckle"] = base @ _origin(-0.0127 * mm, 0, 0.06142 * mm) @ _rot(_Y, -t)
    out["left_finger_tip"] = out["left_finger"] @ _origin(0.00563134 * mm, 0, 0.04718515 * mm) @ _rot(_Y, -t)
    out["right_finger_tip"] = out["right_finger"] @ _origin(-0.00563134 * mm, 0, 0.04718515 * mm) @ _rot(_Y, t)
    return out


# The pads: in the fingertip frame each pad's flat inner face sits at x = -25.26 (left) / +25.26 (right) mm and
# spans z ~13 .. 51 mm, area-weighted centre z = 31.9 mm. The grasp point is midway between the two pad centres.
_PAD = (25.26, 31.9)           # |x| of the pad face, z of the pad centre, in the fingertip frame (mm)


def tcp_mm(close: float = 1.0) -> float:
    """Distance (mm) along tool0's z from the flange to the grasp point for a given closure. The 2F-85's
    fingertips travel on an arc, so this grows by ~13 mm from open to closed."""
    G = gripper_fk(close)
    zl = (G["left_finger_tip"] @ np.array([-_PAD[0], 0, _PAD[1], 1.0]))[2]
    zr = (G["right_finger_tip"] @ np.array([_PAD[0], 0, _PAD[1], 1.0]))[2]
    return float((zl + zr) / 2)


TCP_MM = round(tcp_mm(1.0), 1)       # pads closed: a small part (a vial, a cap) is gripped close to this


# ---------------------------------------------------------------------------------------------- meshes
def _fetch(key: str, url: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / (key.replace("/", "_") + ".dae")
    if not path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        tmp = path.with_suffix(".part")
        tmp.write_bytes(urllib.request.urlopen(req, timeout=300).read())
        tmp.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != SHA256[key]:
        print(f"warning: {path.name} has sha256 {digest}, built against {SHA256[key]}")
    return path


def _srgb(c: float) -> float:
    """Blender writes linear material colours to COLLADA; VTK shows the numbers as they are, so encode them."""
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _specular(rgb) -> float:
    lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    if max(rgb) - min(rgb) > 0.08:      # UR's blue caps: painted
        return 0.3
    return 0.5 if lum > 0.5 else (0.35 if lum > 0.3 else 0.2)     # aluminium, grey castings, black plastic


def _load_dae(path: Path, T_visual: np.ndarray, max_tris: int) -> list[tuple[pv.PolyData, tuple, float]]:
    """One .dae -> one mesh per material colour, in mm, moved by the URDF visual origin (mm)."""
    import trimesh
    sc = trimesh.load(str(path), force="scene")
    by_col: dict[tuple, list] = {}
    for node in sc.graph.nodes_geometry:
        tf, gname = sc.graph[node]
        g = sc.geometry[gname]
        col = (0.75, 0.75, 0.75, 1.0)
        mat = getattr(g.visual, "material", None)
        c = getattr(mat, "diffuse", None)
        if c is None:
            c = getattr(mat, "baseColorFactor", None)
        if c is not None:
            c = np.asarray(c, float)
            col = tuple(c / 255.0 if c.max() > 1.0 else c)
        rgb = tuple(round(_srgb(float(x)), 3) for x in col[:3])
        v = np.asarray(g.vertices, float) @ tf[:3, :3].T + tf[:3, 3]
        v = (v * 1000.0) @ T_visual[:3, :3].T + T_visual[:3, 3]
        faces = np.hstack([np.full((len(g.faces), 1), 3), np.asarray(g.faces)]).ravel()
        by_col.setdefault(rgb, []).append(pv.PolyData(v, faces))
    out = []
    for rgb, ms in sorted(by_col.items()):
        m = ms[0].merge(ms[1:]) if len(ms) > 1 else ms[0]
        m = m.clean(tolerance=1e-6).triangulate()
        out.append((m, rgb, _specular(rgb)))
    n = sum(m.n_cells for m, _, _ in out)
    if n > max_tris:
        out = [(m.decimate_pro(1 - max_tris / n, preserve_topology=True), c, s) for m, c, s in out]
    # split the vertices along sharp edges so smooth shading keeps the CAD edges crisp
    return [(m.compute_normals(split_vertices=True, feature_angle=35.0, auto_orient_normals=False), c, s)
            for m, c, s in out]


def _cached(key: str, build):
    h = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:12]
    path = CACHE / f"{key}_{h}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    data = build()
    CACHE.mkdir(parents=True, exist_ok=True)
    for stale in CACHE.glob(f"{key}_*.pkl"):
        stale.unlink()
    path.write_bytes(pickle.dumps(data))
    return data


@functools.lru_cache(maxsize=None)
def _arm_meshes(model: str, max_tris: int):
    mset = _MESH_SET[model]

    def build():
        out = {}
        for link in LINKS:
            key = f"{mset}/{_DAE[link]}"
            path = _fetch(key, UR_URL.format(mesh=mset, part=_DAE[link]))
            x, y, z, r, p, yw = _VISUAL[mset][link]
            out[link] = _load_dae(path, _origin(x, y, z, r, p, yw), max_tris)
        return out
    return _cached(f"meshes_{mset}_{max_tris}", build)


def arm_meshes(model: str) -> dict[str, list[tuple[pv.PolyData, tuple, float]]]:
    """{link: [(mesh in the link's own frame, mm), rgb 0..1, specular), ...]} for base, shoulder, upper_arm,
    forearm, wrist1, wrist2 and wrist3; place each with fk(model, q)[link]. Copies, so callers may modify them."""
    if model not in MODELS:
        raise KeyError(f"{model}: one of {', '.join(MODELS)}")
    return {k: [(m.copy(), c, s) for m, c, s in v] for k, v in _arm_meshes(model, MAX_TRIS).items()}


@functools.lru_cache(maxsize=None)
def _gripper_meshes(max_tris: int):
    def build():
        return {part: _load_dae(_fetch(f"2f_85/{dae}", RQ_URL.format(part=dae)), np.eye(4), max_tris)
                for part, dae in _GRIPPER_DAE.items()}
    return _cached(f"meshes_2f_85_{max_tris}", build)


def gripper_meshes() -> dict[str, list[tuple[pv.PolyData, tuple, float]]]:
    """{part: [(mesh in the part's own frame, mm), rgb, specular), ...]}; place each with
    fk(model, q)["tool0"] @ gripper_fk(close)[part]."""
    return {k: [(m.copy(), c, s) for m, c, s in v] for k, v in _gripper_meshes(MAX_TRIS).items()}


if __name__ == "__main__":
    for name, spec in MODELS.items():
        tris = sum(m.n_cells for v in arm_meshes(name).values() for m, _, _ in v)
        print(f"{name}: {tris} triangles; tool0 at q = 0: {np.round(fk(name, np.zeros(6))['tool0'][:3, 3], 2)} mm")
    print(f"2F-85: {sum(m.n_cells for v in gripper_meshes().values() for m, _, _ in v)} triangles, "
          f"TCP_MM = {TCP_MM} (open {tcp_mm(0):.1f})")

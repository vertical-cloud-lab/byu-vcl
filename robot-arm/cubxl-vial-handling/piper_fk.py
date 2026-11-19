"""Forward kinematics for the AgileX PiPER straight from its official URDF.

The URDF and meshes come from agilexrobotics/piper_ros (MIT), pinned below and
fetched on demand, so nothing vendored lives in this repo.
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

PIPER_ROS_URL = "https://github.com/agilexrobotics/piper_ros.git"
PIPER_ROS_COMMIT = "ac41fcb"  # 2026-03-04
CACHE = Path("/tmp/piper_ros")
DESC = CACHE / "src/piper_description"


def fetch_description():
    if not (DESC / "urdf/piper_description.urdf").exists():
        subprocess.run(["git", "clone", "--filter=blob:none", "--sparse", PIPER_ROS_URL, str(CACHE)], check=True)
        subprocess.run(["git", "-C", str(CACHE), "sparse-checkout", "set", "src/piper_description"], check=True)
    subprocess.run(["git", "-C", str(CACHE), "checkout", "-q", PIPER_ROS_COMMIT], check=False)
    return DESC


def _rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return rz @ ry @ rx


def _axis_angle(axis, q):
    a = np.asarray(axis, float) / np.linalg.norm(axis)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(q) * k + (1 - np.cos(q)) * k @ k


def _tf(R=np.eye(3), t=(0, 0, 0)):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


class Piper:
    """Serial chain arm_base -> link6 -> fingers, parsed from the URDF.

    Joint limits are the URDF's (the SDK's software defaults), slightly narrower than the
    manual's hardware ranges; reach and height come out the same either way.
    """

    def __init__(self, urdf="urdf/piper_description_v100.urdf"):
        root = ET.parse(fetch_description() / urdf).getroot()
        self.meshes, self.visual_origin = {}, {}
        for link in root.findall("link"):
            m = link.find("visual/geometry/mesh")
            if m is not None:
                self.meshes[link.get("name")] = DESC / m.get("filename").split("piper_description/")[1]
                o = link.find("visual/origin")
                self.visual_origin[link.get("name")] = _tf(
                    _rpy(*map(float, o.get("rpy").split())), list(map(float, o.get("xyz").split()))
                ) if o is not None else np.eye(4)
        self.joints = []
        for j in root.findall("joint"):
            o, a, lim = j.find("origin"), j.find("axis"), j.find("limit")
            self.joints.append(dict(
                name=j.get("name"), type=j.get("type"),
                parent=j.find("parent").get("link"), child=j.find("child").get("link"),
                T=_tf(_rpy(*map(float, o.get("rpy").split())), list(map(float, o.get("xyz").split()))),
                axis=list(map(float, a.get("xyz").split())) if a is not None else None,
                lim=(float(lim.get("lower")), float(lim.get("upper"))) if lim is not None else None,
            ))
        self.limits = {j["name"]: j["lim"] for j in self.joints if j["lim"]}

    def fk(self, q, grip=0.0):
        """Link poses for joint angles q[0..5] (rad) and finger opening per side (m)."""
        vals = {f"joint{i + 1}": v for i, v in enumerate(q)}
        vals["joint7"], vals["joint8"] = grip, -grip
        poses = {self.joints[0]["parent"]: np.eye(4)}
        for j in self.joints:
            T = poses[j["parent"]] @ j["T"]
            v = vals.get(j["name"], 0.0)
            if j["type"] == "revolute":
                T = T @ _tf(_axis_angle(j["axis"], v))
            elif j["type"] == "prismatic":
                T = T @ _tf(t=np.asarray(j["axis"]) * v)
            poses[j["child"]] = T
        return poses

    # Fingertip = 140 mm past the flange on the tool axis (extent of the finger mesh, link7).
    TIP = 0.140

    def tip(self, q):
        T = self.fk(q)["link6"]
        return T[:3, 3] + T[:3, 2] * self.TIP

    def flange(self, q):
        return self.fk(q)["link6"][:3, 3]


def _axis_angle_batch(axis, q):
    a = np.asarray(axis, float) / np.linalg.norm(axis)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    s, c = np.sin(q)[:, None, None], np.cos(q)[:, None, None]
    return np.eye(3) + s * k + (1 - c) * (k @ k)


def fk_points(piper, Q):
    """Vectorised FK: shoulder, elbow, wrist, flange and fingertip for every row of Q (N x 6)."""
    n = len(Q)
    vals = {f"joint{i + 1}": Q[:, i] for i in range(6)}
    poses = {piper.joints[0]["parent"]: np.broadcast_to(np.eye(4), (n, 4, 4)).copy()}
    for j in piper.joints:
        T = poses[j["parent"]] @ j["T"]
        if j["type"] == "revolute" and j["name"] in vals:
            R = np.broadcast_to(np.eye(4), (n, 4, 4)).copy()
            R[:, :3, :3] = _axis_angle_batch(j["axis"], vals[j["name"]])
            T = T @ R
        poses[j["child"]] = T
    pick = {"shoulder": "link2", "elbow": "link3", "wrist": "link4", "flange": "link6"}
    out = {k: poses[v][:, :3, 3] for k, v in pick.items()}
    out["tip"] = out["flange"] + poses["link6"][:, :3, 2] * piper.TIP
    return out


def sample_joints(piper, n, seed=0):
    """Uniform random joint angles over the URDF limits, N x 6."""
    rng = np.random.default_rng(seed)
    lims = [piper.limits[f"joint{i}"] for i in range(1, 7)]
    return np.column_stack([rng.uniform(lo, hi, n) for lo, hi in lims])

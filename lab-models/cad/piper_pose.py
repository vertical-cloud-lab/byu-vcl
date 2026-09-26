"""A posable PiPER for renders: AgileX's URDF and meshes (agilexrobotics/piper_ros, MIT), with
forward kinematics adapted from robot-arm/enclosure/piper_fk.py (#229) and a small IK that puts
the fingertip over a point with the gripper pointing straight down.

The meshes are only used for pictures. The PiPER in the STEP exports and in Onshape is AgileX's
own STEP (vendor.py), in the pose it is delivered in.
"""
from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET

import numpy as np
import pyvista as pv
from scipy.optimize import least_squares

from common import CACHE

PIPER_ROS = "https://github.com/agilexrobotics/piper_ros.git"
BRANCH = "humble"                 # the default branch, noetic, is ROS 1
DESC = CACHE / "piper_ros" / "src" / "piper_description"
TIP = 0.140                       # fingertip past the flange on the tool axis, m (#229)


def fetch() -> None:
    if not (DESC / "urdf" / "piper_description.urdf").exists():
        dst = CACHE / "piper_ros"
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", BRANCH, "--filter=blob:none", "--sparse",
                        PIPER_ROS, str(dst)], check=True)
        subprocess.run(["git", "-C", str(dst), "sparse-checkout", "set", "src/piper_description"], check=True)


def _rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    return (np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]]) @ np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
            @ np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]]))


def _rot(axis, q):
    a = np.asarray(axis, float) / np.linalg.norm(axis)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(q) * k + (1 - np.cos(q)) * k @ k


def _tf(R=np.eye(3), t=(0, 0, 0)):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, t
    return T


def _origin(el):
    o = el.find("origin")
    if o is None:
        return np.eye(4)
    return _tf(_rpy(*map(float, o.get("rpy", "0 0 0").split())), list(map(float, o.get("xyz", "0 0 0").split())))


class Piper:
    def __init__(self):
        fetch()
        root = ET.parse(DESC / "urdf" / "piper_description.urdf").getroot()
        self.visuals = {}
        for link in root.findall("link"):
            mesh = link.find("visual/geometry/mesh")
            if mesh is not None:
                self.visuals[link.get("name")] = (DESC / "meshes" / mesh.get("filename").split("/")[-1],
                                                  _origin(link.find("visual")))
        self.joints = []
        for j in root.findall("joint"):
            a, lim = j.find("axis"), j.find("limit")
            self.joints.append(dict(name=j.get("name"), type=j.get("type"), parent=j.find("parent").get("link"),
                                    child=j.find("child").get("link"), T=_origin(j),
                                    axis=list(map(float, a.get("xyz").split())) if a is not None else None,
                                    lim=(float(lim.get("lower")), float(lim.get("upper"))) if lim is not None else None))
        self.limits = [next(j["lim"] for j in self.joints if j["name"] == f"joint{i}") for i in range(1, 7)]

    def fk(self, q, grip: float = 0.0) -> dict[str, np.ndarray]:
        vals = {f"joint{i + 1}": v for i, v in enumerate(q)}
        vals["joint7"], vals["joint8"] = grip, -grip
        poses = {self.joints[0]["parent"]: np.eye(4)}
        for j in self.joints:
            T = poses[j["parent"]] @ j["T"]
            v = vals.get(j["name"], 0.0)
            if j["type"] == "revolute":
                T = T @ _tf(_rot(j["axis"], v))
            elif j["type"] == "prismatic":
                T = T @ _tf(t=np.asarray(j["axis"]) * v)
            poses[j["child"]] = T
        return poses

    def ik_down(self, target_mm, yaw: float = 0.0, q0=None):
        """Joint angles that put the fingertip at target (mm, base frame) pointing straight down."""
        target = np.asarray(target_mm, float) / 1000.0
        down = np.array([0.0, 0.0, -1.0])
        side = np.array([np.cos(yaw), np.sin(yaw), 0.0])

        def err(q):
            T = self.fk(q)["link6"]
            tip = T[:3, 3] + T[:3, 2] * TIP
            return np.concatenate([(tip - target) * 10, (T[:3, 2] - down), 0.3 * (T[:3, 0] - side)])
        lo, hi = np.array(self.limits).T
        best = None
        for guess in ([0, 1.2, -1.3, 0, 0.6, 0] if q0 is None else q0, [0, 0.8, -0.8, 0, 0.9, 0], [0.5, 1.5, -1.6, 0, 0.3, 0]):
            g = np.clip(np.asarray(guess, float), lo + 1e-3, hi - 1e-3)
            g[0] = np.clip(np.arctan2(target[1], target[0]), lo[0] + 1e-3, hi[0] - 1e-3)
            r = least_squares(err, g, bounds=(lo, hi))
            if best is None or r.cost < best.cost:
                best = r
        return best.x, float(np.linalg.norm(err(best.x)[:3]) / 10 * 1000)   # q, position error in mm

    def meshes(self, q, grip: float = 0.02, base=np.eye(4)) -> list[tuple[pv.PolyData, str]]:
        """(mesh in mm, material) per link, placed by `base` (4x4, mm)."""
        out = []
        poses = self.fk(q, grip)
        for name, (path, vis) in self.visuals.items():
            T = poses[name] @ vis
            T = T.copy()
            T[:3, 3] *= 1000.0
            S = np.diag([1000.0, 1000.0, 1000.0, 1.0])
            mesh = pv.read(str(path)).transform(base @ T @ S, inplace=False)
            material = "printer_black" if name in ("link7", "link8", "gripper_base") else "printer_white"
            out.append((mesh, material))
        return out

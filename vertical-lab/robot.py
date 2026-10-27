"""The UR arm and its Robotiq 2F-85 in the scene: actors per link, forward kinematics every frame, and the moves the
workflow is written in (joint moves, straight-line tool moves solved with IK every frame, gripper, pick and place).

The arm's meshes and kinematics come from ``ur_arm.py`` (Universal Robots' own ROS 2 description and Robotiq's
2F-85 description, fetched at pinned commits). Nothing here is scripted in joint space by hand except the via poses:
every approach, grasp and retreat is a straight line of the gripper's grasp point, so what the arm does is what it
would have to do.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation, Slerp

import ur_arm
from scene import T

LINKS = ("base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3")


def _inv(M):
    Mi = np.eye(4)
    Mi[:3, :3] = M[:3, :3].T
    Mi[:3, 3] = -M[:3, :3].T @ M[:3, 3]
    return Mi


class Robot:
    def __init__(self, sc, model: str, parent: str, base_T: np.ndarray, q0, prefix="ur"):
        self.sc, self.model, self.prefix = sc, model, prefix
        self.root = f"{prefix}_root"
        sc.parent[self.root] = parent
        sc.gmat[self.root] = base_T
        for link, lst in ur_arm.arm_meshes(model).items():
            g = f"{prefix}_{link}"
            for i, (mesh, col, spec) in enumerate(lst):
                sc.add(f"{prefix}/{link}/{i}", mesh, col, g, specular=spec)
            sc.parent[g] = self.root
        self.gparts = []
        for part, lst in ur_arm.gripper_meshes().items():
            g = f"{prefix}_gr_{part}"
            for i, (mesh, col, spec) in enumerate(lst):
                sc.add(f"{prefix}/gr/{part}/{i}", mesh, col, g, specular=spec)
            sc.parent[g] = self.root
            self.gparts.append(part)
        self.q = np.radians(np.asarray(q0, float))
        self.close = 0.0
        self.held: tuple[str, np.ndarray] | None = None
        self.max_z_world = -1e9                    # highest point of the elbow/wrists seen so far (clearance report)
        self.set()

    # ------------------------------------------------------------------------------------ state
    def groups(self) -> list[str]:
        return [self.root] + [f"{self.prefix}_{l}" for l in LINKS] + [f"{self.prefix}_gr_{p}" for p in self.gparts]

    def set(self, q=None, close=None):
        if q is not None:
            self.q = np.asarray(q, float)
        if close is not None:
            self.close = float(close)
        fk = ur_arm.fk(self.model, self.q)
        for link in LINKS:
            self.sc.gmat[f"{self.prefix}_{link}"] = fk[link]
        gfk = ur_arm.gripper_fk(self.close)
        for part in self.gparts:
            self.sc.gmat[f"{self.prefix}_gr_{part}"] = fk["tool0"] @ gfk[part]
        if self.held is not None:
            g, off = self.held
            self.sc.gmat[g] = self.tcp_world() @ off
        W = self.sc.world(self.root)
        for link in ("forearm", "wrist1", "wrist2"):
            self.max_z_world = max(self.max_z_world, float((W @ fk[link])[2, 3]))

    def tcp_world(self, q=None) -> np.ndarray:
        fk = ur_arm.fk(self.model, self.q if q is None else q)
        return self.sc.world(self.root) @ fk["tool0"] @ T((0, 0, ur_arm.TCP_MM))

    def solve(self, Tw: np.ndarray, seed=None) -> np.ndarray:
        Tb = _inv(self.sc.world(self.root)) @ Tw
        return ur_arm.ik(self.model, Tb, self.q if seed is None else seed)

    # ------------------------------------------------------------------------------------ moves
    def joint_to(self, q1=None, Tw=None):
        """Joint-space move to q1 (radians) or to the IK solution of the tool pose Tw nearest the current joints."""
        q0 = self.q.copy()
        q1 = self.solve(Tw, q0) if Tw is not None else np.asarray(q1, float)

        def up(u):
            self.set(q0 + (q1 - q0) * u)
        return up

    def line_to(self, Tw1: np.ndarray, n: int = 40):
        """Straight-line move of the grasp point to Tw1 (orientation slerped), IK solved along the path now so an
        unreachable move fails before anything renders."""
        T0 = self.tcp_world()
        rots = Rotation.from_matrix(np.stack([T0[:3, :3], Tw1[:3, :3]]))
        sl = Slerp([0.0, 1.0], rots)
        path, q = [], self.q.copy()
        for s in np.linspace(0, 1, n + 1):
            M = np.eye(4)
            M[:3, :3] = sl([s]).as_matrix()[0]
            M[:3, 3] = T0[:3, 3] + (Tw1[:3, 3] - T0[:3, 3]) * s
            q = self.solve(M, q)
            path.append(q)
        path = np.array(path)
        jump = np.abs(np.diff(path, axis=0)).max()
        if jump > np.radians(25):
            raise ValueError(f"line move would flip the arm ({np.degrees(jump):.0f} deg in one step)")

        def up(u):
            f = u * n
            i = min(int(f), n - 1)
            self.set(path[i] + (path[i + 1] - path[i]) * (f - i))
        return up

    def grip_to(self, c1: float):
        c0 = self.close

        def up(u):
            self.set(close=c0 + (c1 - c0) * u)
        return up

    # -------------------------------------------------------------------------------- holding
    def reparent(self, group: str, new_parent: str | None):
        W = self.sc.world(group)
        if new_parent is None:
            self.sc.parent.pop(group, None)
            self.sc.gmat[group] = W
        else:
            self.sc.parent[group] = new_parent
            self.sc.gmat[group] = _inv(self.sc.world(new_parent)) @ W

    def grasp(self, group: str):
        self.reparent(group, None)
        self.held = (group, _inv(self.tcp_world()) @ self.sc.gmat[group])

    def release(self, new_parent: str | None):
        g, _ = self.held
        self.held = None
        self.reparent(g, new_parent)


def both(*fs):
    def up(u):
        for f in fs:
            if f is not None:
                f(u)
    return up

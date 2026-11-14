"""The UR arm and its Robotiq 2F-85 in the scene: actors per link, forward kinematics every frame, and the moves the
workflow is written in (joint moves, straight-line tool moves solved with IK every frame, gripper, pick and place).

The arm's meshes and kinematics come from ``ur_arm.py`` (Universal Robots' own ROS 2 description and Robotiq's
2F-85 description, fetched at pinned commits). The wrist camera (an Intel RealSense D405 on a bracket round the
2F-85's coupling, round 7) is one of the gripper's parts there, so every arm drawn here carries it. Nothing here is scripted in joint space by hand except the via poses:
every approach, grasp and retreat is a straight line of the gripper's grasp point, so what the arm does is what it
would have to do.

Joint moves are collision-checked (``collide.py``, FCL on the drawn meshes): the arm against itself, and the arm, the
gripper and what it holds against everything else in the scene, the MiR it rides on included. If the straight joint
line between the two poses hits anything, the move is planned round it (RRT-Connect in joint space, shortcut), so the
arm no longer swings through its own base, its cabinet or a holder on the way. ``ARM_AUDIT=1`` checks every frame of a
clip, line moves too, and writes ``out/collisions/<clip>.json``.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from scipy.spatial.transform import Rotation, Slerp

import ur_arm

try:
    import collide                                 # needs python-fcl (pip install python-fcl)
except ImportError as _e:                          # without it the arm moves as before, unchecked
    collide = None
    print(f"warning: robot.py: no collision checks ({_e}); pip install python-fcl", file=sys.stderr)
from scene import T

LINKS = ("base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3")
NO_PLAN = bool(os.environ.get("ARM_NO_PLAN")) or collide is None   # the old straight joint lines (before/after)


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
        self.events: list[tuple[int, str, str]] = []      # (frame, "grasp" / "release", group), for the audit
        self.plans: list[dict] = []                # one entry per joint move: planned round something or not
        self._checker = None
        if not hasattr(sc, "robots"):
            sc.robots = []
        sc.robots.append(self)
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
    def checker(self) -> collide.Checker:
        if self._checker is None:
            self._checker = collide.Checker(self)
        return self._checker

    def joint_to(self, q1=None, Tw=None, check: bool = True):
        """Joint-space move to q1 (radians) or to the IK solution of the tool pose Tw nearest the current joints. The
        straight joint line is checked against the scene as it is now; if it hits anything, the move goes round it
        (collide.plan_joint_move). Where the arm ends is the same either way."""
        q0 = self.q.copy()
        if Tw is not None and check and not NO_PLAN:
            # every IK branch for the pose, nearest first: the nearest may put the elbow through the MiR's cabinet or
            # the VLM's front panel, when another branch reaches the same pose clear of both
            Tb = _inv(self.sc.world(self.root)) @ Tw
            cands = collide.ik_all(self.model, Tb, q0) or [self.solve(Tw, q0)]
        else:
            cands = [self.solve(Tw, q0) if Tw is not None else np.asarray(q1, float)]
        path = [q0, cands[0]]
        if check and not NO_PLAN:
            chk = self.checker()
            world = chk.snapshot()
            free = [q for q in cands if not chk.collisions(q, self.close, world, chk.touching(q, self.close, world))]
            info = None
            for k, q in enumerate(free or cands[:1]):
                got, info = collide.plan_joint_move(chk, q0, q, self.close, seed=len(self.plans))
                if got is not None:
                    path = got
                    info = dict(info, branch=k if free and q is not cands[0] else 0,
                                other_branch=bool(free) and q is not cands[0])
                    break
            info = dict(info or {}, frame=self.sc.n, label=self.sc.label)
            self.plans.append(info)
            if info.get("reason"):
                print(f"warning: {self.sc.name} {self.sc.label}: joint move not planned ({info.get('reason')}); "
                      f"{info.get('start') or ''} {info.get('goal') or ''}", file=sys.stderr, flush=True)
            elif info.get("planned") or info.get("other_branch"):
                print(f"{self.sc.name} after {self.sc.label}: joint move "
                      f"{'to another IK branch, ' if info.get('other_branch') else ''}"
                      f"{len(path) - 2} via pose(s)", flush=True)

        def up(u):
            self.set(collide.along(path, u))
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
            if not NO_PLAN:
                # an earlier joint move went to another IK branch to stay clear of something, and in this branch the
                # line crosses a wrist or elbow flip: go there by a planned joint move instead (the gripper then
                # doesn't run exactly straight, but nothing passes through anything)
                print(f"{self.sc.name} {self.sc.label}: line move would flip the arm in this IK branch "
                      f"({np.degrees(jump):.0f} deg in one step); a planned joint move instead", flush=True)
                return self.joint_to(Tw=Tw1)
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
        src = self.sc.parent.get(group)
        self.reparent(group, None)
        self.held = (group, _inv(self.tcp_world()) @ self.sc.gmat[group])
        self.events.append((self.sc.n, "grasp", group, src))

    def release(self, new_parent: str | None):
        g, _ = self.held
        self.held = None
        self.reparent(g, new_parent)
        self.events.append((self.sc.n, "release", g, new_parent))


def both(*fs):
    def up(u):
        for f in fs:
            if f is not None:
                f(u)
    return up


class FingerSet:
    """Round 11: a pair of parts that ride on the 2F-85's fingertips (ur_arm.spec_finger_meshes: chapter 5's specimen
    fingers), as scene groups `parts` = {"left_finger_tip": group, "right_finger_tip": group} under one container
    group. While `on`, every Robot.set places each part on its fingertip as the gripper opens and closes, whatever
    the container hangs from: the arm holds the container (rb.grasp) or a part the fingers hold, so collide.py checks
    the fingers as held geometry against everything. Off, they stay where they were put (their stand). Wraps the
    one Robot instance's set(); the class and every other arm are untouched."""

    def __init__(self, rb: Robot, container: str, parts: dict):
        self.rb, self.container, self.parts, self.on = rb, container, dict(parts), False
        orig = rb.set

        def set_(q=None, close=None, _orig=orig):
            _orig(q, close)
            if self.on:
                self.follow()
        rb.set = set_

    def follow(self):
        sc, rb = self.rb.sc, self.rb
        Wt = sc.world(rb.root) @ ur_arm.fk(rb.model, rb.q)["tool0"]
        G = ur_arm.gripper_fk(rb.close)
        Wc_inv = _inv(sc.world(self.container))
        for tip, g in self.parts.items():
            sc.gmat[g] = Wc_inv @ Wt @ G[tip]

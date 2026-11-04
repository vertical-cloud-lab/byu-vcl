"""Collision checks and collision-free joint moves for the UR arms in the vertical-lab scenes (#303).

Until now ``robot.py`` moved the arm in two ways, a straight line of the grasp point (IK every frame) or a straight
line in joint space between two solved poses, and nothing checked either one against anything. A joint move from a
pose over the tray to one over the MiR's own cabinet swung the elbow and the wrists through whatever lay between, the
MiR and the vial holder included, and through the arm's own links. Sterling caught it on PR #318.

This module checks, with FCL (the Flexible Collision Library, the checker MoveIt uses by default), on the meshes that
are drawn:

* **the arm against itself**: every pair of links that isn't adjacent in the chain, with the gripper (all its parts)
  as one body on the flange. Pairs that touch in every pose (the joints' own housings) are found by sampling and left
  out, the way MoveIt's setup assistant writes UR's SRDF;
* **the arm, gripper and whatever it holds against everything else that is visible**: the MiR it rides on, holders,
  racks, trays, machines, the VLM, the other arm. The arm's base may touch its own mounting (the MiR's cabinet); the
  gripper may touch what it is picking up or putting down; a part it holds may touch where it came from and where it
  is going. Nothing else may touch.

``plan_joint_move`` replaces the straight joint line when that line hits something: RRT-Connect in joint space
(Kuffner & LaValle 2000) from the start pose to the goal, every edge checked at 1.5 deg steps, then shortcut, so the
move goes round what is in the way rather than through it. ``Auditor`` runs a whole clip without rendering
(``ARM_AUDIT=1 xvfb-run -a python3 <clip>.py``) and writes ``out/collisions/<clip>.json``: every frame where an arm
touches something it should not, grouped into runs, with the sub-step it happens in.

Units mm, the scene's world frame. FCL works on triangle meshes (BVH, OBB-RSS), so concave things (a holder on a post,
a cabinet with a plate on it, an open machine) are checked as drawn, not as convex hulls.
"""
from __future__ import annotations

import functools
import json
import math
import os
from pathlib import Path

import fcl
import numpy as np
import pyvista as pv

import ur_arm

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "collisions"
AUDIT = bool(os.environ.get("ARM_AUDIT"))

ARM_LINKS = ("base", "shoulder", "upper_arm", "forearm", "wrist1", "wrist2", "wrist3")
ADJACENT = {("base", "shoulder"), ("shoulder", "upper_arm"), ("upper_arm", "forearm"), ("forearm", "wrist1"),
            ("wrist1", "wrist2"), ("wrist2", "wrist3"), ("wrist3", "gripper"), ("wrist2", "gripper")}
MAX_TRIS = 8000            # links above this are decimated for the checks (the drawn meshes are not touched)
STEP_RAD = math.radians(1.5)


# ------------------------------------------------------------------------------------------------- meshes
def _tris(poly: pv.PolyData) -> tuple[np.ndarray, np.ndarray] | None:
    if poly is None:
        return None
    poly = pv.wrap(poly)
    if poly.n_points == 0:
        return None
    if not isinstance(poly, pv.PolyData) or poly.n_cells == 0:
        return None
    m = poly.triangulate()
    f = np.asarray(m.faces).reshape(-1, 4)
    if not len(f) or (f[:, 0] != 3).any():
        return None
    return np.asarray(m.points, float), f[:, 1:].astype(np.int32)


def _bvh(v: np.ndarray, f: np.ndarray) -> fcl.BVHModel:
    m = fcl.BVHModel()
    m.beginModel(len(v), len(f))
    m.addSubModel(v, f)
    m.endModel()
    return m


class Body:
    """One mesh in its own (group) frame: its FCL object and its local box corners for a quick overlap test."""

    __slots__ = ("name", "group", "obj", "corners", "tf")

    def __init__(self, name: str, group: str, v: np.ndarray, f: np.ndarray):
        self.name, self.group = name, group
        self.obj = fcl.CollisionObject(_bvh(v, f), fcl.Transform())
        lo, hi = v.min(0), v.max(0)
        self.corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        self.tf = None

    def place(self, M: np.ndarray):
        if self.tf is not None and np.array_equal(self.tf, M):
            return
        self.tf = M.copy()
        self.obj.setTransform(fcl.Transform(M[:3, :3], M[:3, 3]))

    def box(self, M: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        w = self.corners @ M[:3, :3].T + M[:3, 3]
        return w.min(0), w.max(0)


def _hit(a: fcl.CollisionObject, b: fcl.CollisionObject) -> bool:
    return fcl.collide(a, b, fcl.CollisionRequest(), fcl.CollisionResult()) > 0


def _decimated(mesh: pv.PolyData) -> pv.PolyData:
    mesh = mesh.triangulate().clean()
    if mesh.n_cells > MAX_TRIS:
        mesh = mesh.decimate(1.0 - MAX_TRIS / mesh.n_cells)
    return mesh


@functools.lru_cache(maxsize=None)
def _arm_geometry(model: str):
    """{link: (v, f)} for the arm's links and {"gripper": {part: (v, f)}}, decimated, in each link's own frame."""
    out = {}
    for link, lst in ur_arm.arm_meshes(model).items():
        m = lst[0][0].merge([x for x, _, _ in lst[1:]]) if len(lst) > 1 else lst[0][0]
        out[link] = _tris(_decimated(m))
    grip = {}
    for part, lst in ur_arm.gripper_meshes().items():
        m = lst[0][0].merge([x for x, _, _ in lst[1:]]) if len(lst) > 1 else lst[0][0]
        grip[part] = _tris(_decimated(m))
    return out, grip


# ------------------------------------------------------------------------------------------------ the arm
class ArmBodies:
    """FCL bodies for one arm: its seven links and its gripper's parts, placed for a joint vector q."""

    def __init__(self, model: str):
        self.model = model
        links, grip = _arm_geometry(model)
        self.links = {k: Body(k, k, *links[k]) for k in ARM_LINKS}
        self.grip = {k: Body(k, "gripper", *grip[k]) for k in grip}
        self.close = None
        self._G = None

    def place(self, W_root: np.ndarray, q, close: float) -> dict[str, np.ndarray]:
        F = ur_arm.fk(self.model, q)
        for k, b in self.links.items():
            b.place(W_root @ F[k])
        if self._G is None or close != self.close:
            self._G, self.close = ur_arm.gripper_fk(close), close
        Wt = W_root @ F["tool0"]
        for k, b in self.grip.items():
            b.place(Wt @ self._G[k])
        return F

    def bodies(self):
        yield from self.links.values()
        yield from self.grip.values()


@functools.lru_cache(maxsize=None)
def _always_touching(model: str, n: int = 400) -> frozenset:
    """Pairs of arm bodies that touch in nearly every pose: the joints' own housings. Sampled, as MoveIt's setup
    assistant does it ("Default" and "Always" pairs), and cached."""
    cache = HERE / ".cache" / f"collide_acm_{model}.json"
    if cache.exists():
        return frozenset(tuple(p) for p in json.loads(cache.read_text()))
    arm = ArmBodies(model)
    rng = np.random.default_rng(7)
    names = list(ARM_LINKS) + ["gripper"]
    counts = {}
    for _ in range(n):
        q = rng.uniform(-math.pi, math.pi, 6)
        arm.place(np.eye(4), q, float(rng.uniform(0, 1)))
        groups = {k: [arm.links[k]] for k in ARM_LINKS}
        groups["gripper"] = list(arm.grip.values())
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if any(_hit(x.obj, y.obj) for x in groups[a] for y in groups[b]):
                    counts[(a, b)] = counts.get((a, b), 0) + 1
    pairs = sorted(p for p, c in counts.items() if c > 0.9 * n)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(pairs))
    return frozenset(pairs)


def self_pairs(model: str) -> list[tuple[str, str]]:
    """The pairs of arm bodies (links and "gripper") checked for self-collision."""
    names = list(ARM_LINKS) + ["gripper"]
    skip = ADJACENT | set(_always_touching(model))
    return [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if (a, b) not in skip and (b, a) not in skip]


# ---------------------------------------------------------------------------------------------- the scene
def _visible(sc, name: str) -> bool:
    """Whether an actor is drawn at all (as Scene.apply decides). Cutaway halves and wholes both count: the machine
    is whole whatever the camera is shown, so an arm can't reach through the half that is cut away for the view."""
    if sc.cutrole.get(name):
        return True
    return sc.alpha.get(name, 1.0) * sc.base_alpha.get(name, 1.0) > 0.02 or name in sc.ghost_of


class World:
    """FCL bodies for every mesh actor in a Scene, built once per actor and moved with its group every check."""

    def __init__(self, sc):
        self.sc = sc
        self.bodies: dict[str, Body] = {}
        self._seen: dict[str, int] = {}
        self.refresh()

    def refresh(self):
        for name, actor in self.sc.actors.items():
            inp = actor.GetMapper().GetInput()
            key = (inp.__this__, inp.GetMTime()) if inp is not None else None     # the VTK object, not its wrapper
            if self._seen.get(name) == key:
                continue
            self._seen[name] = key
            t = _tris(inp)
            if t is None:
                self.bodies.pop(name, None)
                continue
            self.bodies[name] = Body(name, self.sc.group_of[name], *t)

    def current(self, exclude_groups: set[str]) -> list[tuple[Body, np.ndarray, np.ndarray]]:
        """(body, box min, box max) for every visible body not in exclude_groups, placed where its group is now."""
        sc = self.sc
        cache, out = {}, []
        for name, b in self.bodies.items():
            if b.group in exclude_groups or not _visible(sc, name):
                continue
            if b.group not in cache:
                cache[b.group] = sc.world(b.group)
            M = cache[b.group]
            b.place(M)
            lo, hi = b.box(M)
            out.append((b, lo, hi))
        return out


def _subtree(sc, group: str) -> set[str]:
    """group and every group parented (directly or not) to it."""
    out, todo = {group}, [group]
    kids: dict[str, list[str]] = {}
    for c, p in sc.parent.items():
        kids.setdefault(p, []).append(c)
    while todo:
        g = todo.pop()
        for c in kids.get(g, ()):
            if c not in out:
                out.add(c)
                todo.append(c)
    return out


def _ancestors(sc, group: str) -> set[str]:
    out, g = set(), group
    while g in sc.parent:
        g = sc.parent[g]
        out.add(g)
    return out


# ---------------------------------------------------------------------------------------------- checking
class Checker:
    """Everything one arm (``robot.Robot``) can hit, with the rules of what may touch what."""

    def __init__(self, rb):
        self.rb, self.sc = rb, rb.sc
        if not hasattr(self.sc, "_collide_world"):
            self.sc._collide_world = World(self.sc)
        self.world: World = self.sc._collide_world
        self.arm = ArmBodies(rb.model)
        self.pairs = self_pairs(rb.model)
        self.mount = _ancestors(self.sc, rb.root)            # the arm's base stands on these (the MiR's group)
        self.held_bodies: list[Body] = []
        self.held_group = None

    # ----------------------------------------------------------------------- what the arm holds
    def _held(self):
        h = self.rb.held
        if h is None:
            self.held_bodies, self.held_group = [], None
            return None
        g = h[0]
        if g != self.held_group:
            sub = _subtree(self.sc, g)
            self.held_bodies = [b for b in self.world.bodies.values() if b.group in sub]
            self.held_group = g
        return h

    def robot_groups(self) -> set[str]:
        out = set(self.rb.groups())
        if self.rb.held is not None:
            out |= _subtree(self.sc, self.rb.held[0])
        return out

    # ----------------------------------------------------------------------- one pose
    def snapshot(self):
        """The world as it is now, for checks of many arm poses against it (the plan of one move)."""
        self.world.refresh()
        self._held()
        return self.world.current(self.robot_groups())

    def collisions(self, q=None, close=None, world=None, allow: set | None = None, first=False) -> list[tuple]:
        """[(kind, robot body, other, other's group)] for the arm at q (default: where it is) against the world as it
        is (or the snapshot `world`). kind is "self", "arm", "gripper" or "held". `allow` is a set of world groups the
        gripper and held part may touch (the part being handled and its fixtures)."""
        rb, sc = self.rb, self.sc
        q = rb.q if q is None else np.asarray(q, float)
        close = rb.close if close is None else close
        if world is None:
            world = self.snapshot()
        W_root = sc.world(rb.root)
        F = self.arm.place(W_root, q, close)
        held = self._held()
        hb = []
        if held is not None:
            g, off = held
            Wh = W_root @ F["tool0"] @ _tcp() @ off           # the held group's world matrix at q
            Mg = {}
            for b in self.held_bodies:
                if b.group not in Mg:
                    Mg[b.group] = Wh @ _rel(sc, b.group, g)
                b.place(Mg[b.group])
                hb.append(b)
        out = []
        # self: links against links, and the held part against the links it isn't gripped by
        groups = {k: [self.arm.links[k]] for k in ARM_LINKS}
        groups["gripper"] = list(self.arm.grip.values())
        for a, b in self.pairs:
            for x in groups[a]:
                hitp = next((y for y in groups[b] if _hit(x.obj, y.obj)), None)
                if hitp is not None:
                    out.append(("self", a, b, ""))
                    if first:
                        return out
                    break
        for x in hb:
            for k in ("base", "shoulder", "upper_arm", "forearm", "wrist1"):
                if _hit(x.obj, self.arm.links[k].obj):
                    out.append(("self", f"held:{x.group}", k, ""))
                    if first:
                        return out
        # the world
        mine = [(b, *b.box(b.tf)) for b in self.arm.bodies()] + [(b, *b.box(b.tf)) for b in hb]
        allow = allow or set()
        for b, lo, hi in mine:
            kind = "held" if b in hb else ("gripper" if b.group == "gripper" else "arm")
            for w, wlo, whi in world:
                if (lo > whi).any() or (hi < wlo).any():
                    continue
                if kind == "arm" and b.name == "base" and w.group in self.mount:
                    continue
                if kind in ("gripper", "held") and w.group in allow:
                    continue
                if _hit(b.obj, w.obj):
                    out.append((kind, b.name if kind != "held" else f"held:{b.group}", w.name, w.group))
                    if first:
                        return out
        return out

    def touching(self, q=None, close=None, world=None) -> set[str]:
        """World groups the gripper or the held part touches at q: the part being handled and its fixtures."""
        hits = self.collisions(q, close, world)
        return {g for k, _, _, g in hits if k in ("gripper", "held")}


def _tcp() -> np.ndarray:
    M = np.eye(4)
    M[2, 3] = ur_arm.TCP_MM
    return M


def _rel(sc, group: str, top: str) -> np.ndarray:
    """group's matrix relative to its ancestor `top` (identity for top itself)."""
    M, g = np.eye(4), group
    while g != top:
        M = sc.gmat.get(g, np.eye(4)) @ M
        g = sc.parent[g]
    return M


# ---------------------------------------------------------------------------------------------- planning
def ik_all(model: str, T_tcp: np.ndarray, q_seed, tcp: float | None = None) -> list[np.ndarray]:
    """Every converged IK solution (up to 8: shoulder left/right, elbow up/down, wrist flipped or not) for the TCP pose
    T_tcp in the arm's base frame, each joint moved by whole turns towards q_seed, nearest q_seed first."""
    seed = np.asarray(q_seed, float).reshape(6)
    off = np.eye(4)
    off[2, 3] = -(ur_arm.TCP_MM if tcp is None else tcp)
    T06 = np.asarray(T_tcp, float) @ off
    out = []
    for s in ur_arm._ik_analytic(model, T06, q6_free=float(seed[5])):
        q = ur_arm._polish(model, ur_arm._wrap_near(s, seed), T06)
        e = ur_arm._pose_err(ur_arm.fk(model, q)["tool0"], T06)
        if np.linalg.norm(e[:3]) < 1e-3 and np.linalg.norm(e[3:]) < 1e-6:
            q = ur_arm._wrap_near(q, seed)
            if all(np.abs(q - o).max() > 1e-4 for o in out):
                out.append(q)
    out.sort(key=lambda q: float(np.sum((q - seed) ** 2)))
    return out


def _segment_free(chk: Checker, world, allow, qa, qb, close) -> bool:
    n = max(1, int(math.ceil(np.abs(qb - qa).max() / STEP_RAD)))
    for i in range(1, n + 1):
        q = qa + (qb - qa) * (i / n)
        if chk.collisions(q, close, world, allow, first=True):
            return False
    return True


def path_hits(chk: Checker, path, close, world=None, allow=None) -> list[tuple[int, list]]:
    """[(index, hits)] for the poses along a joint path (list of q), sampled at 1.5 deg."""
    world = chk.snapshot() if world is None else world
    out = []
    for a, b in zip(path[:-1], path[1:]):
        n = max(1, int(math.ceil(np.abs(b - a).max() / STEP_RAD)))
        for i in range(n + 1):
            h = chk.collisions(a + (b - a) * (i / n), close, world, allow)
            if h:
                out.append((len(out), h))
    return out


def plan_joint_move(chk: Checker, q0, q1, close, seed: int = 0, iters: int = 6000, step: float = 0.35):
    """A collision-free joint path [q0, ..., q1] (list of arrays), or None. The straight line if it is clear,
    otherwise RRT-Connect, shortcut. What the gripper or the held part touches at either end is allowed throughout."""
    q0, q1 = np.asarray(q0, float), np.asarray(q1, float)
    world = chk.snapshot()
    allow = chk.touching(q0, close, world) | chk.touching(q1, close, world)
    bad0 = chk.collisions(q0, close, world, allow)
    bad1 = chk.collisions(q1, close, world, allow)
    if bad0 or bad1:
        return None, dict(reason="end pose in collision", start=bad0[:4], goal=bad1[:4])
    if _segment_free(chk, world, allow, q0, q1, close):
        return [q0, q1], dict(planned=False)
    rng = np.random.default_rng(seed)
    lim = ur_arm._LIMIT
    lo = np.maximum(np.minimum(q0, q1) - math.pi, -lim)
    hi = np.minimum(np.maximum(q0, q1) + math.pi, lim)

    def free(q):
        return not chk.collisions(q, close, world, allow, first=True)

    def extend(tree, parent, q_to):
        """Step from the nearest node of `tree` towards q_to; returns the new index or None."""
        d = np.linalg.norm(np.asarray(tree) - q_to, axis=1)
        i = int(np.argmin(d))
        qn = tree[i]
        v = q_to - qn
        L = float(np.linalg.norm(v))
        q_new = q_to if L <= step else qn + v * (step / L)
        if not free(q_new) or not _segment_free(chk, world, allow, qn, q_new, close):
            return None
        tree.append(q_new)
        parent.append(i)
        return len(tree) - 1

    def connect(tree, parent, q_to):
        last = None
        while True:
            k = extend(tree, parent, q_to)
            if k is None:
                return last, False
            last = k
            if np.linalg.norm(tree[k] - q_to) < 1e-9:
                return k, True

    A, pa, B, pb = [q0], [-1], [q1], [-1]
    swapped = False
    for it in range(iters):
        q_rand = q1 if rng.random() < 0.1 else rng.uniform(lo, hi)
        k = extend(A, pa, q_rand)
        if k is not None:
            j, ok = connect(B, pb, A[k])
            if ok:
                def trace(tree, parent, idx):
                    out = []
                    while idx >= 0:
                        out.append(tree[idx])
                        idx = parent[idx]
                    return out
                pA, pB = trace(A, pa, k), trace(B, pb, j)
                path = pA[::-1] + pB[1:]
                if swapped:
                    path = path[::-1]
                path = _shortcut(chk, world, allow, path, close, rng)
                return path, dict(planned=True, iterations=it + 1, nodes=len(A) + len(B), waypoints=len(path))
        A, pa, B, pb = B, pb, A, pa
        swapped = not swapped
    return None, dict(reason=f"no path in {iters} iterations")


def _shortcut(chk, world, allow, path, close, rng, rounds: int = 120):
    path = [np.asarray(p, float) for p in path]
    for _ in range(rounds):
        if len(path) <= 2:
            break
        i, j = sorted(rng.choice(len(path), 2, replace=False))
        if j - i < 2:
            continue
        if _segment_free(chk, world, allow, path[i], path[j], close):
            path = path[:i + 1] + path[j:]
    # then try to drop each remaining via point in turn
    k = 1
    while k < len(path) - 1:
        if _segment_free(chk, world, allow, path[k - 1], path[k + 1], close):
            path.pop(k)
        else:
            k += 1
    return path


def along(path, u: float) -> np.ndarray:
    """The pose a fraction u of the way along a joint path, by joint-space length."""
    if len(path) == 2:
        return path[0] + (path[1] - path[0]) * u
    seg = [float(np.linalg.norm(b - a)) for a, b in zip(path[:-1], path[1:])]
    tot = sum(seg)
    if tot < 1e-12:
        return np.asarray(path[-1], float)
    s = u * tot
    for (a, b), L in zip(zip(path[:-1], path[1:]), seg):
        if s <= L + 1e-12:
            return a + (b - a) * (0.0 if L < 1e-12 else s / L)
        s -= L
    return np.asarray(path[-1], float)


# ------------------------------------------------------------------------------------------------ audit
class Auditor:
    """Checks every arm in a Scene after every frame's update and writes out/collisions/<clip>.json at save.

    What may touch: the gripper and whatever group it is picking up, holding or putting down, within 4 s of the
    grasp or release; a held part and the groups it touches when it is taken and when it is let go (where it came
    from and where it goes)."""

    def __init__(self, sc):
        self.sc = sc
        self.frames: list[dict] = []
        self.checkers: dict[str, Checker] = {}

    def __call__(self, sc):
        world_by = {}
        rec = []
        for rb in getattr(sc, "robots", []):
            chk = self.checkers.get(rb.prefix)
            if chk is None:
                chk = self.checkers[rb.prefix] = Checker(rb)
            for kind, a, b, g in chk.collisions():
                rec.append((rb.prefix, kind, a, b, g))
        self.frames.append(dict(n=sc.n, label=sc.label, hits=rec,
                                held={rb.prefix: (rb.held[0] if rb.held else None) for rb in getattr(sc, "robots", [])}))

    def report(self) -> dict:
        sc = self.sc
        fps = 15.0
        events = []           # (frame, prefix, group)
        for rb in getattr(sc, "robots", []):
            for ev in getattr(rb, "events", []):
                n, what, g = ev[:3]
                events.append((n, rb.prefix, g, what))
                for extra in ev[3:]:
                    if extra:
                        events.append((n, rb.prefix, extra, what))
        win = int(4 * fps)
        # held episodes: allowed groups = what the part touches at its first and last frame held
        ep_allow: dict[tuple, set] = {}
        episodes = []         # (prefix, group, i0, i1)
        open_ep: dict[str, list] = {}
        for i, fr in enumerate(self.frames):
            for p, g in fr["held"].items():
                if g is not None and (p not in open_ep or open_ep[p][1] != g):
                    if p in open_ep:
                        episodes.append(tuple(open_ep[p][:2]) + (open_ep[p][2], i - 1))
                    open_ep[p] = [p, g, i]
                elif g is None and p in open_ep:
                    episodes.append(tuple(open_ep[p][:2]) + (open_ep[p][2], i - 1))
                    open_ep.pop(p)
        for p, (pp, g, i0) in open_ep.items():
            episodes.append((pp, g, i0, len(self.frames) - 1))
        for p, g, i0, i1 in episodes:
            ends = set()
            for i in (i0, i1):
                for pre, kind, a, b, grp in self.frames[i]["hits"]:
                    if pre == p and kind == "held":
                        ends.add(grp)
            ep_allow[(p, g, i0, i1)] = ends
        runs = []
        clean_frames = 0
        last = None
        for i, fr in enumerate(self.frames):
            bad = []
            for p, kind, a, b, grp in fr["hits"]:
                if kind == "gripper":
                    near = {e[2] for e in events if e[1] == p and abs(e[0] - fr["n"]) <= win}
                    sub = set()
                    for g in near:
                        sub |= _subtree(sc, g)
                    if grp in sub:
                        continue
                if kind == "held":
                    ok = False
                    for (pp, g, i0, i1), al in ep_allow.items():
                        if pp == p and i0 <= i <= i1 and grp in al:
                            ok = True
                    if ok:
                        continue
                bad.append(dict(arm=p, kind=kind, part=a, other=b, other_group=grp))
            if not bad:
                clean_frames += 1
                last = None
                continue
            key = tuple(sorted({(d["arm"], d["kind"], d["part"], d["other_group"] or d["other"]) for d in bad}))
            if last is not None and runs and runs[-1]["label"] == fr["label"] and runs[-1]["_key"] == key:
                runs[-1]["last_frame"] = fr["n"]
                runs[-1]["frames"] += 1
            else:
                runs.append(dict(label=fr["label"], first_frame=fr["n"], last_frame=fr["n"], frames=1, _key=key,
                                 pairs=[dict(arm=a, kind=k, part=pt, other=o) for a, k, pt, o in key]))
            last = key
        for r in runs:
            r.pop("_key")
        n_bad = sum(r["frames"] for r in runs)
        return dict(clip=sc.name, frames_checked=len(self.frames), frames_with_collisions=n_bad,
                    runs=runs, rules=self.__doc__.split("\n\n", 1)[1].strip(),
                    method="FCL 0.7 (python-fcl) mesh-mesh collision on the drawn meshes, arm links decimated to "
                           f"{MAX_TRIS} triangles; every frame of the clip, after its update")

    def save(self):
        OUT.mkdir(parents=True, exist_ok=True)
        rep = self.report()
        path = OUT / f"{self.sc.name}.json"
        path.write_text(json.dumps(rep, indent=1) + "\n")
        print(f"{self.sc.name}: {rep['frames_with_collisions']} of {rep['frames_checked']} frames with collisions, "
              f"{len(rep['runs'])} runs -> {path.relative_to(HERE)}", flush=True)
        return rep

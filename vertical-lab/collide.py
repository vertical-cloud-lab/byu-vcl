"""Collision checks and collision-free joint moves for the UR arms in the vertical-lab scenes (#303).

Until now ``robot.py`` moved the arm in two ways, a straight line of the grasp point (IK every frame) or a straight
line in joint space between two solved poses, and nothing checked either one against anything. A joint move from a
pose over the tray to one over the MiR's own cabinet swung the elbow and the wrists through whatever lay between, the
MiR and the vial holder included, and through the arm's own links. Sterling caught it on PR #318.

This module checks, with FCL (the Flexible Collision Library, the checker MoveIt uses by default), on the meshes that
are drawn:

* **the arm against itself**: every pair of links that isn't adjacent in the chain, with the gripper (all its parts,
  the wrist camera on its coupling included: ``ur_arm.camera_meshes``) as one body on the flange. Pairs that touch in every pose (the joints' own housings) are found by sampling and left
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

Round 11 (Sterling, 2026-11-13: the arm through a camera post, the tensile bars, the maintenance clip, "there are
probably other collisions and interferences that I didn't catch") made the audit stricter, and that is the default
for ``ARM_AUDIT=1`` (``ARM_AUDIT_RULES=old`` gives round 10's rules, for before/after numbers):

* **Depth limits on what is allowed.** The gripper may touch what it picks up or puts down, and a held part its
  source and destination, only up to ``ARM_AUDIT_DEPTH_MM`` (1.5 mm) of penetration. Until now any depth was allowed,
  so fingers sunk into a grip's jaws counted as "allowed". The depth is ``depth()``: the translational penetration
  depth (the shortest move that frees one body from the other), sampled over 26 directions. FCL's own contact
  ``penetration_depth`` was tested first and is not a depth for mesh-mesh contacts: it is per triangle pair, so on
  finely meshed parts it is capped by the triangle size (a 20 mm finger sunk 10 mm into a block meshed at 5 mm
  reads 1.1 mm, a sphere sunk 8 mm reads 0.5 mm; see notes/arm_collisions.md).
* **The movers check** (``Movers``). Every group whose world matrix changed since the last frame and isn't part of an
  arm or held by one (MiRs, trays, doors, tables, people, parts riding on them) is checked against every other
  visible body except its own subtree and ancestors, boxes first, then FCL. Contacts a group already had when it
  started moving (at its last pose before the move: the floor under a MiR, a tray on its lift) are left out; a new
  contact deeper than 1.5 mm is reported, in the JSON's "movers" section.
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
# round 11: the stricter audit (depth limits on what may touch, and the movers check) is the default
STRICT = os.environ.get("ARM_AUDIT_RULES", "strict").lower() != "old"
MOVERS = STRICT and os.environ.get("ARM_AUDIT_MOVERS", "1") != "0"
DEPTH_MM = float(os.environ.get("ARM_AUDIT_DEPTH_MM", "1.5"))
LADDER = (DEPTH_MM, 3.0, 6.0, 12.0, 25.0, 50.0)     # depth() answers with the first of these that frees the pair
DEEP = 999.0                                        # depth() past the last step of LADDER
FLOOR_MM = 6.0      # the movers check: a body whose top is at most this far above z = 0 is the floor (the slab, tape,
                    # painted marks), which a MiR's skirt drawn down to z = 0 and anything set on the floor may touch
_DIRS = np.array([d for d in __import__("itertools").product((-1, 0, 1), repeat=3) if any(d)], float)
_DIRS /= np.linalg.norm(_DIRS, axis=1)[:, None]     # the 26 directions to a cube's faces, edges and corners


# ------------------------------------------------------------------------------------------------- meshes
def _tris(poly: pv.PolyData) -> tuple[np.ndarray, np.ndarray] | None:
    if poly is None:
        return None
    poly = pv.wrap(poly)
    if poly.n_points == 0:
        return None
    if not isinstance(poly, pv.PolyData) or poly.n_cells == 0:
        return None
    import warnings
    with warnings.catch_warnings():             # actors whose cell normals outlived a re-mesh: only the points count here
        warnings.simplefilter("ignore")
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

    __slots__ = ("name", "group", "obj", "corners", "tf", "pending", "wkey", "wbox")

    def __init__(self, name: str, group: str, v: np.ndarray, f: np.ndarray):
        self.name, self.group = name, group
        self.obj = fcl.CollisionObject(_bvh(v, f), fcl.Transform())
        self.corners = _corners(v.min(0), v.max(0))
        self.tf = None
        self.pending = None            # a re-meshed VTK input whose BVH isn't built yet (built when something is near)
        self.wkey = self.wbox = None   # World.current's cache: the group matrix (bytes) its world box was made for

    def ensure(self):
        """Build the BVH of a re-meshed actor now (it was only marked when its mesh changed)."""
        if self.pending is None:
            return
        t = _tris(self.pending)
        self.pending = None
        if t is None:
            return
        self.obj = fcl.CollisionObject(_bvh(*t), fcl.Transform())
        self.tf = None
        self.wkey = None

    def place(self, M: np.ndarray):
        if self.tf is not None and np.array_equal(self.tf, M):
            return
        self.tf = M.copy()
        self.wkey = None
        self.obj.setTransform(fcl.Transform(M[:3, :3], M[:3, 3]))

    def box(self, M: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        w = self.corners @ M[:3, :3].T + M[:3, 3]
        return w.min(0), w.max(0)


def _corners(lo, hi) -> np.ndarray:
    return np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])


def _hit(a: fcl.CollisionObject, b: fcl.CollisionObject) -> bool:
    return fcl.collide(a, b, fcl.CollisionRequest(), fcl.CollisionResult()) > 0


def depth(x: "Body", y: "Body", upto: float | None = None) -> float:
    """How far x is into y (mm): the first step of LADDER (1.5, 3, 6, 12, 25, 50 mm) by which moving x along one of 26
    directions (to a cube's faces, edges and corners) frees it from y; 0 if they don't touch, DEEP (999) if nothing up
    to 50 mm does. That is the translational penetration depth (the shortest move that separates two bodies),
    sampled, rounded up to the ladder, so "1.5" means "1.5 mm or less" and "6" means "more than 3, at most 6".
    Directions nearest the line between the two boxes' centres are tried first. `upto`: stop once a step >= upto has
    failed and return the next step (enough to tell "deeper than upto").

    Validated on known cases (notes/arm_collisions.md): a 20 mm finger sunk 0.3, 1.0, 1.5, 3, 10 and 25 mm into a
    block, coarse and finely meshed, reads 1.5, 1.5, 1.5, 3, 12 and 25 or 50; a sphere sunk 8 mm reads 12; a rod
    straight through a block reads 12. Both bodies must be placed (Body.place) where they are."""
    if not _hit(x.obj, y.obj):
        return 0.0
    M = x.tf if x.tf is not None else np.eye(4)
    lo_x, hi_x = x.box(M)
    lo_y, hi_y = y.box(y.tf if y.tf is not None else np.eye(4))
    c = (lo_x + hi_x - lo_y - hi_y) * 0.5
    n = float(np.linalg.norm(c))
    order = np.argsort(-(_DIRS @ (c / n))) if n > 1e-9 else np.arange(len(_DIRS))
    Rm, p = M[:3, :3].copy(), M[:3, 3].copy()
    try:
        for k, t in enumerate(LADDER):
            for i in order:
                x.obj.setTranslation(p + t * _DIRS[i])
                if not _hit(x.obj, y.obj):
                    return float(t)
            if upto is not None and t >= upto:
                return float(LADDER[k + 1]) if k + 1 < len(LADDER) else DEEP
        return DEEP
    finally:
        x.obj.setTransform(fcl.Transform(Rm, p))


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
        self._builds: dict[str, int] = {}
        self._last: dict[str, int] = {}
        self._tick = 0
        self.refresh()

    def refresh(self):
        """Pick up actors added or re-meshed since the last call. A re-meshed actor (the multi-doser's carousel
        rewrites its merged meshes every frame it moves) only gets its new bounds now; its BVH is rebuilt when an arm
        part comes near it (Body.ensure), since a BVH per frame would cost more than the rest of the check."""
        self._tick += 1
        for name, actor in self.sc.actors.items():
            inp = actor.GetMapper().GetInput()
            key = (inp.__this__, inp.GetMTime()) if inp is not None else None     # the VTK object, not its wrapper
            if self._seen.get(name) == key:
                continue
            self._seen[name] = key
            b = self.bodies.get(name)
            if b is not None and inp is not None and inp.GetNumberOfPolys() > 0:
                lo = np.array(inp.GetBounds()[0::2])
                hi = np.array(inp.GetBounds()[1::2])
                b.corners = _corners(lo, hi)
                b.pending = inp
                b.wkey = None
                continue
            t = _tris(inp)
            if t is None:
                self.bodies.pop(name, None)
                continue
            self.bodies[name] = Body(name, self.sc.group_of[name], *t)

    def current(self, exclude_groups: set[str]) -> "Snap":
        """Every visible body not in exclude_groups, placed where its group is now, with its world box."""
        sc = self.sc
        cache, out = {}, []
        fluids = set(getattr(sc, "fluids", ()))     # actors that are liquids: a part may be dipped in them
        for name, b in self.bodies.items():
            if b.group in exclude_groups or not _visible(sc, name) or name in fluids:
                continue
            got = cache.get(b.group)
            if got is None:
                M = sc.world(b.group)
                got = cache[b.group] = (M, M.tobytes())
            M, key = got
            if b.wkey is not None and b.wkey == key and b.tf is not None:      # round 11: nothing moved, as placed
                lo, hi = b.wbox
            else:
                b.place(M)
                lo, hi = b.box(M)
                b.wkey, b.wbox = key, (lo, hi)
            out.append((b, lo, hi, M))
        return Snap(out)


class Snap:
    """The world at one instant: its bodies and their world boxes as arrays, for a vectorised overlap test."""

    def __init__(self, items):
        self.items = items
        self.bodies = [b for b, _, _, _ in items]
        self.M = [m for _, _, _, m in items]
        self.lo = np.array([lo for _, lo, _, _ in items]).reshape(-1, 3)
        self.hi = np.array([hi for _, _, hi, _ in items]).reshape(-1, 3)


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

    def collisions(self, q=None, close=None, world=None, allow: set | None = None, first=False,
                   depths: bool = False) -> list[tuple]:
        """[(kind, robot body, other, other's group)] for the arm at q (default: where it is) against the world as it
        is (or the snapshot `world`). kind is "self", "arm", "gripper" or "held". `allow` is a set of world groups the
        gripper and held part may touch (the part being handled and its fixtures). depths=True (round 11, the
        audit): each hit gets a fifth item, how far the gripper part or held part is into the other (depth(), mm),
        None for "self" and "arm" hits, which are collisions at any depth."""
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
        mine = list(self.arm.bodies()) + hb
        boxes = [b.box(b.tf) for b in mine]
        R_lo = np.array([lo for lo, _ in boxes])
        R_hi = np.array([hi for _, hi in boxes])
        idx = {id(b): i for i, b in enumerate(mine)}

        def near(x, y):
            i, j = idx[id(x)], idx[id(y)]
            return not ((R_lo[i] > R_hi[j]).any() or (R_hi[i] < R_lo[j]).any())

        # self: links against links, and the held part against the links it isn't gripped by
        groups = {k: [self.arm.links[k]] for k in ARM_LINKS}
        groups["gripper"] = list(self.arm.grip.values())
        for a, b in self.pairs:
            found = False
            for x in groups[a]:
                for y in groups[b]:
                    if near(x, y) and _hit(x.obj, y.obj):
                        found = True
                        break
                if found:
                    break
            if found:
                out.append(("self", a, b, "") + ((None,) if depths else ()))
                if first:
                    return out
        for x in hb:
            for k in ("base", "shoulder", "upper_arm", "forearm", "wrist1"):
                y = self.arm.links[k]
                if near(x, y) and _hit(x.obj, y.obj):
                    out.append(("self", f"held:{x.group}", k, "") + ((None,) if depths else ()))
                    if first:
                        return out
        # the world: boxes first, all pairs at once, then the meshes of the pairs whose boxes overlap
        allow = allow or set()
        if len(world.bodies):
            ov = ~((R_lo[:, None, :] > world.hi[None]) | (R_hi[:, None, :] < world.lo[None])).any(-1)
            nh = len(self.arm.links) + len(self.arm.grip)
            for i, j in zip(*np.nonzero(ov)):
                b, w = mine[i], world.bodies[j]
                kind = "held" if i >= nh else ("gripper" if b.group == "gripper" else "arm")
                if kind == "arm" and b.name == "base" and w.group in self.mount:
                    continue
                if kind in ("gripper", "held") and w.group in allow:
                    continue
                if w.pending is not None:
                    w.ensure()
                    w.place(world.M[j])
                if _hit(b.obj, w.obj):
                    hit = (kind, b.name if kind != "held" else f"held:{b.group}", w.name, w.group)
                    if depths:
                        hit += (depth(b, w) if kind in ("gripper", "held") else None,)
                    out.append(hit)
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


def _top(chk: Checker, q) -> float:
    """The highest of the elbow and the wrists (world z, mm) at q."""
    W = chk.sc.world(chk.rb.root)
    F = ur_arm.fk(chk.rb.model, q)
    return max(float((W @ F[k])[2, 3]) for k in ("forearm", "wrist1", "wrist2", "wrist3"))


def _segment_free(chk: Checker, world, allow, qa, qb, close, zmax=None) -> bool:
    n = max(1, int(math.ceil(np.abs(qb - qa).max() / STEP_RAD)))
    for i in range(1, n + 1):
        q = qa + (qb - qa) * (i / n)
        if zmax is not None and _top(chk, q) > zmax:
            return False
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


def plan_joint_move(chk: Checker, q0, q1, close, seed: int = 0, iters: int = 2500, step: float = 0.35):
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
    # a detour may not lift the elbow or the wrists more than 150 mm over the higher end of the move (or 1.8 m): a
    # random sample can otherwise send the arm straight up, which is clear but nothing a person would program
    zmax = max(_top(chk, q0), _top(chk, q1), 1650.0) + 150.0
    rng = np.random.default_rng(seed)
    lim = ur_arm._LIMIT
    lo = np.maximum(np.minimum(q0, q1) - math.pi, -lim)
    hi = np.minimum(np.maximum(q0, q1) + math.pi, lim)

    def free(q):
        return _top(chk, q) <= zmax and not chk.collisions(q, close, world, allow, first=True)

    def extend(tree, parent, q_to):
        """Step from the nearest node of `tree` towards q_to; returns the new index or None."""
        d = np.linalg.norm(np.asarray(tree) - q_to, axis=1)
        i = int(np.argmin(d))
        qn = tree[i]
        v = q_to - qn
        L = float(np.linalg.norm(v))
        q_new = q_to if L <= step else qn + v * (step / L)
        if not free(q_new) or not _segment_free(chk, world, allow, qn, q_new, close, zmax):
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
                path = _shortcut(chk, world, allow, path, close, rng, zmax=zmax)
                return path, dict(planned=True, iterations=it + 1, nodes=len(A) + len(B), waypoints=len(path))
        A, pa, B, pb = B, pb, A, pa
        swapped = not swapped
    return None, dict(reason=f"no path in {iters} iterations")


def _shortcut(chk, world, allow, path, close, rng, rounds: int = 120, zmax=None):
    path = [np.asarray(p, float) for p in path]
    for _ in range(rounds):
        if len(path) <= 2:
            break
        i, j = sorted(rng.choice(len(path), 2, replace=False))
        if j - i < 2:
            continue
        if _segment_free(chk, world, allow, path[i], path[j], close, zmax):
            path = path[:i + 1] + path[j:]
    # then try to drop each remaining via point in turn
    k = 1
    while k < len(path) - 1:
        if _segment_free(chk, world, allow, path[k - 1], path[k + 1], close, zmax):
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


# ---------------------------------------------------------------------------------------- movers (round 11)
_I4 = np.eye(4)


def _ikey(inp):
    return (inp.__this__, inp.GetMTime()) if inp is not None else None


def _arm_excluded(sc) -> set[str]:
    """Groups the movers check leaves to the arm checks: every arm's links and gripper, and what each arm holds."""
    out = set()
    for rb in getattr(sc, "robots", []):
        out |= set(rb.groups())
        if rb.held is not None:
            out |= _subtree(sc, rb.held[0])
    return out


class Movers:
    """Round 11: everything that moves and isn't an arm, checked every audited frame.

    A group "moves" in a frame when its world matrix changed since the last audited frame (by more than 1e-6). Groups
    that moved by the same rigid motion (a MiR with its cabinet, its holders and the parts on them) form one cluster
    and are not checked against each other: their relative poses didn't change, so no new contact can appear between
    them. Every visible body of a moving group is checked against every other visible body except its own group's
    subtree and ancestors, the arms and what they hold (the arm checks do those), liquids, and the floor with its
    markings (anything whose top is within FLOOR_MM, 6 mm, of z = 0: tape is paint, and a MiR's skirt is drawn down to
    the floor): world boxes first, all at once, then FCL on the meshes of the pairs whose boxes overlap (BVHs built
    only for those). The contacts a group
    had at its last pose before it started moving are its baseline and are left out while it keeps moving, until
    that pair comes apart; a new contact counts if depth() puts it deeper than DEPTH_MM (1.5 mm), so a tray set down
    on a table or a MiR rolling onto a floor plate isn't reported."""

    def __init__(self, sc):
        self.sc = sc
        self.groups: list[str] = []            # append-only; index into the stacked matrices
        self.gpos: dict[str, int] = {}
        self.names: list[str] = []
        self.gidx = np.zeros(0, int)
        self.C = np.zeros((0, 8, 3))
        self.ckey: dict[str, object] = {}      # actor -> key of the VTK input its local box came from
        self.body: dict[str, Body] = {}
        self.bkey: dict[str, object] = {}
        self.baked: dict[str, tuple] = {}      # actor -> (matrix bytes, Body in world coordinates) for scaled groups
        self.Wprev = None
        self.moving: set[str] = set()
        self.base: dict[str, set] = {}
        self.frames: list[dict] = []
        self.checked = 0
        self.seconds = 0.0
        self._n_actors = -1

    # ------------------------------------------------------------------------------ bookkeeping
    def _corners(self, name):
        inp = self.sc.actors[name].GetMapper().GetInput()
        self.ckey[name] = _ikey(inp)
        if inp is None or inp.GetNumberOfPoints() == 0:
            return np.full((8, 3), np.nan)
        b = inp.GetBounds()
        return _corners(np.array(b[0::2]), np.array(b[1::2]))

    def _index(self):
        sc = self.sc
        if len(sc.actors) == self._n_actors:
            return
        self._n_actors = len(sc.actors)
        self.names = list(sc.actors)
        for n in self.names:
            g = sc.group_of[n]
            if g not in self.gpos:
                self.gpos[g] = len(self.groups)
                self.groups.append(g)
        self.gidx = np.array([self.gpos[sc.group_of[n]] for n in self.names], int)
        self.C = np.stack([self._corners(n) for n in self.names]) if self.names else np.zeros((0, 8, 3))

    def _worlds(self) -> np.ndarray:
        sc, memo = self.sc, {}

        def w(g):
            m = memo.get(g)
            if m is None:
                par = sc.parent.get(g)
                m = sc.gmat.get(g, _I4) if par is None else w(par) @ sc.gmat.get(g, _I4)
                memo[g] = m
            return m
        return np.stack([w(g) for g in self.groups]) if self.groups else np.zeros((0, 4, 4))

    @staticmethod
    def _boxes(C, W, gidx):
        Wg = W[gidx]
        w = np.einsum("nij,nkj->nki", Wg[:, :3, :3], C) + Wg[:, None, :3, 3]
        return w.min(1), w.max(1)

    def _body(self, name) -> Body | None:
        """The FCL body of an actor, built when first needed (or taken from the arm checks' World if it has it)."""
        inp = self.sc.actors[name].GetMapper().GetInput()
        key = _ikey(inp)
        b = self.body.get(name)
        if b is not None and self.bkey.get(name) == key:
            return b
        wd = getattr(self.sc, "_collide_world", None)
        if wd is not None and name in wd.bodies and wd._seen.get(name) == key and wd.bodies[name].pending is None:
            b = wd.bodies[name]
        else:
            t = _tris(inp)
            b = Body(name, self.sc.group_of[name], *t) if t is not None else None
        self.body[name], self.bkey[name] = b, key
        return b

    def _placed(self, name, M) -> Body | None:
        """The actor's body placed at M. FCL takes only rigid transforms (a scaled matrix is read as a rotation and
        the scale dropped: a box stretched to +-6 doesn't touch a probe at 4), so a group drawn with a scale (the VLM's
        belts, a level) gets a body built from its vertices moved into the world, cached per matrix."""
        R = M[:3, :3]
        if np.abs(R.T @ R - np.eye(3)).max() < 1e-6:
            b = self._body(name)
            if b is not None:
                b.place(M)
            return b
        key = M.tobytes()
        got = self.baked.get(name)
        if got is not None and got[0] == key:
            return got[1]
        t = _tris(self.sc.actors[name].GetMapper().GetInput())
        if t is None:
            return None
        b = Body(name, self.sc.group_of[name], t[0] @ R.T + M[:3, 3], t[1])
        b.place(np.eye(4))
        self.baked[name] = (key, b)
        return b

    # ------------------------------------------------------------------------------ one frame
    def __call__(self, sc):
        import time
        t0 = time.time()
        self._index()
        W = self._worlds()
        if self.Wprev is None:
            self.Wprev = W.copy()
        elif len(self.Wprev) < len(W):              # groups added since: they haven't moved
            self.Wprev = np.concatenate([self.Wprev, W[len(self.Wprev):]])
        excl = _arm_excluded(sc)
        moved = np.abs(W - self.Wprev).max(axis=(1, 2)) > 1e-6
        for g in excl:
            if g in self.gpos:
                moved[self.gpos[g]] = False
        hits = []
        now_moving = {self.groups[i] for i in np.nonzero(moved)[0]}
        if now_moving:
            hits = self._check(sc, W, moved, excl, now_moving)
        self.moving = now_moving
        self.Wprev = W
        self.frames.append(dict(n=sc.n, label=sc.label, hits=hits, moving=len(now_moving)))
        self.seconds += time.time() - t0

    def _check(self, sc, W, moved, excl, now_moving):
        fluids = set(getattr(sc, "fluids", ()))
        mov_a = np.nonzero(moved[self.gidx])[0]
        mov_a = [i for i in mov_a if self.names[i] not in fluids and _visible(sc, self.names[i])]
        if not mov_a:
            return []
        for i in mov_a:                                       # a moving actor may have been re-meshed too
            n = self.names[i]
            if self.ckey.get(n) != _ikey(sc.actors[n].GetMapper().GetInput()):
                self.C[i] = self._corners(n)
        lo, hi = self._boxes(self.C, W, self.gidx)
        # rigid clusters: groups that moved by the same displacement this frame
        mg = np.nonzero(moved)[0]
        D = W[mg] @ np.linalg.inv(self.Wprev[mg])
        cl_of_g = {}
        keys = {}
        for k, gi in enumerate(mg):
            key = np.round(D[k, :3, :], 3).tobytes()
            cl_of_g[gi] = keys.setdefault(key, len(keys))
        kids: dict[str, list[str]] = {}
        for c, par in sc.parent.items():
            kids.setdefault(par, []).append(c)
        fam_memo = {}

        def family(g):
            f = fam_memo.get(g)
            if f is None:
                out, todo = {g}, [g]
                while todo:
                    x = todo.pop()
                    for c in kids.get(x, ()):
                        if c not in out:
                            out.add(c)
                            todo.append(c)
                f = fam_memo[g] = out | _ancestors(sc, g)
            return f
        # episode starts: the contacts at the last pose before the move are the baseline
        starting = now_moving - self.moving
        if starting:
            plo, phi = self._boxes(self.C, self.Wprev, self.gidx)
            for g in starting:
                self.base[g] = self._contacts(sc, [i for i in mov_a if self.groups[self.gidx[i]] == g],
                                              plo, phi, self.Wprev, excl, fluids, family, cl=None).get(g, set())
        for g in list(self.base):
            if g not in now_moving:
                self.base.pop(g)
        cur = self._contacts(sc, mov_a, lo, hi, W, excl, fluids, family, cl=(moved, cl_of_g))
        hits = []
        touching = set()                                      # every pair in contact now, both ways round (a pair of
        for prs in cur.values():                              # two moving clusters is checked under one of them)
            for a, b in prs:
                touching.add((a, b))
                touching.add((b, a))
        for g in now_moving:                                  # a baseline pair that came apart is a new one next time
            if g in self.base:
                self.base[g] &= touching
        for g, pairs in cur.items():
            for a, b in pairs:
                gb = sc.group_of[b]
                if (a, b) in self.base.get(g, ()) or (b, a) in self.base.get(gb, ()):
                    continue
                x = self._placed(a, W[self.gpos[g]])
                y = self._placed(b, W[self.gpos[gb]])
                d = depth(x, y)
                if d > DEPTH_MM:
                    hits.append((g, a, b, gb, d))
        return hits

    def _contacts(self, sc, act, lo, hi, W, excl, fluids, family, cl) -> dict[str, set]:
        """{moving group: {(its actor, other actor)}} of the pairs that touch, for the actors `act` with world boxes
        lo/hi and group matrices W. cl=(moved, cluster of group): pairs in one cluster are skipped, and a pair of two
        moving clusters is checked once."""
        out: dict[str, set] = {}
        if not act:
            return out
        by_cl: dict[int, list] = {}                       # one union box per rigid cluster (a MiR and a tray far apart)
        for i in act:
            by_cl.setdefault(cl[1][self.gidx[i]] if cl is not None else 0, []).append(i)
        pairs = []
        for members in by_cl.values():
            A = np.asarray(members)
            ulo, uhi = lo[A].min(0), hi[A].max(0)
            cand = np.nonzero(~((ulo > hi) | (uhi < lo)).any(1))[0]      # every box that meets the cluster's box
            if not len(cand):
                continue
            ov = ~((lo[A][:, None, :] > hi[cand][None]) | (hi[A][:, None, :] < lo[cand][None])).any(-1)
            pairs += [(A[r], cand[c]) for r, c in zip(*np.nonzero(ov))]
        vis = {}
        for i, j in pairs:
            if i == j:
                continue
            gi, gj = self.gidx[i], self.gidx[j]
            ga, gb = self.groups[gi], self.groups[gj]
            if gb in excl or hi[j][2] <= FLOOR_MM:          # the arms' own; the floor and its markings
                continue
            if cl is not None:
                moved, cl_of = cl
                if moved[gj]:
                    if cl_of[gi] == cl_of[gj] or cl_of[gi] > cl_of[gj]:
                        continue
            elif gi == gj:
                continue
            if gb in family(ga):
                continue
            nb = self.names[j]
            if nb in fluids:
                continue
            if nb not in vis:
                vis[nb] = _visible(sc, nb)
            if not vis[nb]:
                continue
            na = self.names[i]
            x = self._placed(na, W[gi])
            y = self._placed(nb, W[gj])
            if x is None or y is None:
                continue
            self.checked += 1
            if _hit(x.obj, y.obj):
                out.setdefault(ga, set()).add((na, nb))
        return out

    # ------------------------------------------------------------------------------ the report
    def report(self) -> dict:
        runs, last = [], None
        n_bad = 0
        for fr in self.frames:
            if not fr["hits"]:
                last = None
                continue
            n_bad += 1
            key = tuple(sorted({(g, gb) for g, _, _, gb, _ in fr["hits"]}))
            if last is not None and runs and runs[-1]["label"] == fr["label"] and runs[-1]["_key"] == key:
                r = runs[-1]
                r["last_frame"] = fr["n"]
                r["frames"] += 1
            else:
                r = dict(label=fr["label"], first_frame=fr["n"], last_frame=fr["n"], frames=1, _key=key, _pairs={})
                runs.append(r)
            for g, a, b, gb, d in fr["hits"]:
                pk = (g, a, b, gb)
                r["_pairs"][pk] = max(r["_pairs"].get(pk, 0.0), d)
            last = key
        for r in runs:
            r.pop("_key")
            pairs = r.pop("_pairs")
            r["depth_mm"] = max(pairs.values())
            r["pairs"] = [dict(mover=g, body=a, other=b, other_group=gb, depth_mm=d)
                          for (g, a, b, gb), d in sorted(pairs.items(), key=lambda kv: -kv[1])[:12]]
        return dict(frames_checked=len(self.frames), frames_moving=sum(1 for f in self.frames if f["moving"]),
                    frames_with_collisions=n_bad, runs=runs, fcl_pairs_checked=self.checked,
                    seconds=round(self.seconds, 1), rules=" ".join(self.__doc__.split("\n\n", 1)[1].split()))


# ------------------------------------------------------------------------------------------------ audit
class Auditor:
    """Checks every arm in a Scene after every frame's update and writes out/collisions/<clip>.json at save.

    What may touch (round 11, the default): the gripper and whatever group it is picking up, holding or putting down,
    within 4 s of the grasp or release, and a held part and the groups it touches when it is taken and when it is let
    go (where it came from and where it goes), each only up to 1.5 mm deep (collide.depth: the shortest of 26 moves
    that frees the pair). Anything else an arm, its gripper or what it holds touches is a collision at any depth. The
    movers check (collide.Movers, its own "movers" section) covers everything else that moves. ARM_AUDIT_RULES=old:
    round 10's rules (no depth limit, no movers)."""

    def __init__(self, sc):
        self.sc = sc
        self.frames: list[dict] = []
        self.checkers: dict[str, Checker] = {}
        # ARM_AUDIT_SNAP="540,930": also draw those frames, the parts in collision in red -> out/collisions/*.png.
        # Round 11: ARM_AUDIT_SNAP=auto (or auto:N) draws the first frame of each new run of collisions (up to N, 24),
        # the camera aimed at the contact, -> ARM_AUDIT_SNAP_DIR (/tmp/r11_snaps)/<clip>_<frame>.jpg and an index
        # <clip>_snaps.json, for audit_all.py's sheet
        snap = os.environ.get("ARM_AUDIT_SNAP", "").strip()
        self.auto_snap = snap.startswith("auto")
        self.auto_max = int(snap.split(":", 1)[1]) if self.auto_snap and ":" in snap else 24
        self.snap_frames = set() if self.auto_snap else {int(x) for x in snap.split(",") if x.strip()}
        self.snap_dir = Path(os.environ.get("ARM_AUDIT_SNAP_DIR", "/tmp/r11_snaps"))
        self.snaps: list[dict] = []
        self._last_bad = None
        self.movers = Movers(sc) if MOVERS else None
        self.seconds = 0.0

    def _bad_now(self) -> frozenset:
        """This frame's hits as far as they can be judged now (a shallow touch of the gripper or a held part is
        taken as allowed: the event windows are only known at the end), for ARM_AUDIT_SNAP=auto."""
        out = set()
        for h in (self.frames[-1]["hits"] if self.frames else []):
            p, kind, a, b, g, d = h
            if kind in ("self", "arm") or (STRICT and d is not None and d > DEPTH_MM):
                out.add((p, kind, a, g or b))
        if self.movers is not None and self.movers.frames:
            out |= {("mover", g, a, gb) for g, a, _, gb, _ in self.movers.frames[-1]["hits"]}
        return frozenset(out)

    def _aim(self, sc) -> bool:
        """Point the camera at this frame's first contact (ARM_AUDIT_SNAP=auto); False if there is none to aim at."""
        def bounds(names):
            bs = [np.array(sc.actors[n].GetBounds()).reshape(3, 2) for n in names if n in sc.actors]
            bs = [b for b in bs if np.isfinite(b).all() and (b[:, 1] >= b[:, 0]).all()]
            if not bs:
                return None
            return np.min([b[:, 0] for b in bs], 0), np.max([b[:, 1] for b in bs], 0)
        pairs = []
        if self.movers is not None and self.movers.frames:
            pairs += [([a], [b]) for _, a, b, _, _ in self.movers.frames[-1]["hits"]]
        for h in (self.frames[-1]["hits"] if self.frames else []):
            p, kind, a, b, g, d = h
            if not (kind in ("self", "arm") or (STRICT and d is not None and d > DEPTH_MM)):
                continue
            if a.startswith("held:"):
                mine = [n for n, gg in sc.group_of.items() if gg == a[5:]]
            elif a in ARM_LINKS:
                mine = [n for n in sc.actors if n.startswith(f"{p}/{a}/")]
            else:
                mine = [n for n in sc.actors if n.startswith(f"{p}/gr/")]
            other = [n for n in sc.actors if n.startswith(f"{p}/{b}/")] if kind == "self" else [b]
            pairs.insert(0, (mine, other))
        sc.apply()
        for mine, other in pairs:
            A, B = bounds(mine), bounds(other)
            if A is None or B is None:
                continue
            lo, hi = np.maximum(A[0], B[0]), np.minimum(A[1], B[1])
            if (hi < lo).any():
                lo, hi = (A[0] + A[1]) / 2, (B[0] + B[1]) / 2
                lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)
            f = (lo + hi) / 2
            pos, foc = np.array(sc.cam[0], float), np.array(sc.cam[1], float)
            v = pos - foc
            v = v / (np.linalg.norm(v) or 1.0)
            dist = float(np.clip(2.6 * max(float((hi - lo).max()), 260.0), 800.0, 3500.0))
            sc.cam = [tuple(f + v * dist), tuple(f), (0, 0, 1)]
            sc.view_angle = 30.0
            return True
        return False

    def picture(self, sc):
        """Draw the current frame with every arm part that touches something it shouldn't in red (and, round 11,
        both bodies of every mover's new contact)."""
        from PIL import ImageDraw
        from scene import font
        hits = self.frames[-1]["hits"] if self.frames else []
        mhits = self.movers.frames[-1]["hits"] if self.movers is not None and self.movers.frames else []
        red = {}

        def paint(n):
            if n in sc.actors and n not in red:
                red[n] = (sc.color.get(n), tuple(sc.actors[n].GetProperty().GetColor()))
        for rb in getattr(sc, "robots", []):
            mine = [h for h in hits if h[0] == rb.prefix]
            for h in mine:
                _, kind, a, b, g = h[:5]
                parts = [a] + ([b] if kind == "self" and not b.startswith("held") else [])
                for part in parts:
                    if part.startswith("held:"):
                        grp = part[5:]
                        names = [n for n, gg in sc.group_of.items() if gg == grp]
                    elif part == "gripper":
                        names = [n for n in sc.actors if n.startswith(f"{rb.prefix}/gr/")]
                    elif part in ARM_LINKS:
                        names = [n for n in sc.actors if n.startswith(f"{rb.prefix}/{part}/")]
                    else:
                        names = [n for n in sc.actors if n.startswith(f"{rb.prefix}/gr/{part}/")]
                    for n in names:
                        paint(n)
                if kind != "self":
                    paint(b)
        for g, a, b, gb, d in mhits:
            paint(a)
            paint(b)
        for n in red:
            sc.color[n] = (0.92, 0.10, 0.10)
        from PIL import Image
        cam0, va0 = list(sc.cam), sc.view_angle
        aimed = self.auto_snap and self._aim(sc)
        img = Image.fromarray(sc.render_base())
        sc.cam, sc.view_angle = cam0, va0
        for n, (c, drawn) in red.items():
            if c is None:
                sc.color.pop(n, None)
                sc.actors[n].GetProperty().SetColor(*drawn)
            else:
                sc.color[n] = c
        d = ImageDraw.Draw(img)
        tag = os.environ.get("ARM_AUDIT_TAG", "") or "planned"
        what = sorted({f"{h[2]} in {h[4] or h[3]}" + (f" {h[5]:g} mm" if len(h) > 5 and h[5] else "") for h in hits})
        what += sorted({f"{g} into {gb} {dd:g} mm" for g, _, _, gb, dd in mhits})
        txt = (f"{sc.name}, frame {sc.n} ({sc.label}), {'old straight joint moves' if tag == 'before' else 'planned'}: "
               + ("; ".join(what) if what else "no collisions"))
        d.rectangle((0, 0, img.width, 34), fill=(255, 255, 255))
        d.text((14, 8), txt[:150], fill=(180, 20, 20) if what else (20, 110, 40), font=font(17, bold=True))
        if self.auto_snap:
            self.snap_dir.mkdir(parents=True, exist_ok=True)
            path = self.snap_dir / f"{sc.name}_{sc.n:05d}.jpg"
            img.convert("RGB").save(path, quality=86)
            self.snaps.append(dict(frame=sc.n, label=sc.label, file=str(path), aimed=bool(aimed), hits=what))
            (self.snap_dir / f"{sc.name}_snaps.json").write_text(json.dumps(self.snaps, indent=1) + "\n")
            return
        OUT.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(OUT / f"{sc.name}_{tag}_{sc.n:05d}.png", optimize=True)

    def __call__(self, sc):
        import time
        t0 = time.time()
        rec = []
        for rb in getattr(sc, "robots", []):
            chk = self.checkers.get(rb.prefix)
            if chk is None:
                chk = self.checkers[rb.prefix] = Checker(rb)
            for kind, a, b, g, d in chk.collisions(depths=True):
                rec.append((rb.prefix, kind, a, b, g, d))
        self.frames.append(dict(n=sc.n, label=sc.label, hits=rec,
                                held={rb.prefix: (rb.held[0] if rb.held else None) for rb in getattr(sc, "robots", [])}))
        self.seconds += time.time() - t0
        if self.movers is not None:
            self.movers(sc)
        if self.auto_snap:
            bad = self._bad_now()
            if bad and bad != self._last_bad and len(self.snaps) + len(self.snap_frames - {x["frame"] for x in self.snaps}) < self.auto_max:
                self.snap_frames.add(sc.n)
            self._last_bad = bad or None

    def report(self) -> dict:
        sc = self.sc
        try:
            from scene import FPS as fps
        except ImportError:
            fps = 15
        events = []           # (frame, prefix, group)
        for rb in getattr(sc, "robots", []):
            for ev in getattr(rb, "events", []):
                n, what, g = ev[:3]
                events.append((n, rb.prefix, g, what))
                for extra in ev[3:]:
                    if extra:
                        events.append((n, rb.prefix, extra, what))
        win = int(round(4 * fps))
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
                for h in self.frames[i]["hits"]:
                    if h[0] == p and h[1] == "held":
                        ends.add(h[4])
            ep_allow[(p, g, i0, i1)] = ends
        runs = []
        clean_frames = 0
        bad_ns = set()
        too_deep = 0           # hits that round 10's rules allowed and the depth limit doesn't
        last = None
        for i, fr in enumerate(self.frames):
            bad = []
            for h in fr["hits"]:
                p, kind, a, b, grp = h[:5]
                d = h[5] if len(h) > 5 else None
                shallow = not STRICT or d is None or d <= DEPTH_MM
                if kind == "gripper":
                    near = {e[2] for e in events if e[1] == p and abs(e[0] - fr["n"]) <= win}
                    sub = set()
                    for g in near:
                        sub |= _subtree(sc, g)
                    if grp in sub:
                        if shallow:
                            continue
                        too_deep += 1
                if kind == "held":
                    ok = False
                    for (pp, g, i0, i1), al in ep_allow.items():
                        if pp == p and i0 <= i <= i1 and grp in al:
                            ok = True
                    if ok:
                        if shallow:
                            continue
                        too_deep += 1
                bad.append(dict(arm=p, kind=kind, part=a, other=b, other_group=grp, depth_mm=d))
            if not bad:
                clean_frames += 1
                last = None
                continue
            bad_ns.add(fr["n"])
            key = tuple(sorted({(d_["arm"], d_["kind"], d_["part"], d_["other_group"] or d_["other"]) for d_ in bad}))
            if last is not None and runs and runs[-1]["label"] == fr["label"] and runs[-1]["_key"] == key:
                runs[-1]["last_frame"] = fr["n"]
                runs[-1]["frames"] += 1
            else:
                runs.append(dict(label=fr["label"], first_frame=fr["n"], last_frame=fr["n"], frames=1, _key=key,
                                 _depth={}))
            for d_ in bad:
                pk = (d_["arm"], d_["kind"], d_["part"], d_["other_group"] or d_["other"])
                if d_["depth_mm"] is not None:
                    runs[-1]["_depth"][pk] = max(runs[-1]["_depth"].get(pk, 0.0), d_["depth_mm"])
            last = key
        for r in runs:
            key, dep = r.pop("_key"), r.pop("_depth")
            r["pairs"] = [dict(arm=a, kind=k, part=pt, other=o, **({"depth_mm": dep[(a, k, pt, o)]}
                                                                  if (a, k, pt, o) in dep else {}))
                          for a, k, pt, o in key]
        n_bad = sum(r["frames"] for r in runs)
        rep = dict(clip=sc.name, frames_checked=len(self.frames), frames_with_collisions=n_bad,
                   runs=runs, rules=" ".join(self.__doc__.split("\n\n", 1)[1].split()),
                   rules_version="round 11 (strict)" if STRICT else "round 10 (old)",
                   depth_limit_mm=DEPTH_MM if STRICT else None, hits_allowed_before_but_too_deep=too_deep,
                   fps=fps, arm_seconds=round(self.seconds, 1),
                   method="FCL 0.7 (python-fcl) mesh-mesh collision on the drawn meshes, arm links decimated to "
                          f"{MAX_TRIS} triangles; every frame of the clip, after its update; depths by collide.depth "
                          "(26-direction translational depth, rounded up to 1.5/3/6/12/25/50 mm, 999 past 50)")
        if self.movers is not None:
            mv = self.movers.report()
            rep["movers"] = mv
            mv_frames = {f["n"] for f in self.movers.frames if f["hits"]}
            rep["frames_with_collisions_all"] = len(bad_ns | mv_frames)
        return rep

    def save(self):
        OUT.mkdir(parents=True, exist_ok=True)
        rep = self.report()
        tag = os.environ.get("ARM_AUDIT_TAG", "")
        path = OUT / f"{self.sc.name}{'_' + tag if tag else ''}.json"
        path.write_text(json.dumps(rep, indent=1) + "\n")
        print(f"{self.sc.name}: {rep['frames_with_collisions']} of {rep['frames_checked']} frames with collisions, "
              f"{len(rep['runs'])} runs ({rep['rules_version']}) -> {path.relative_to(HERE)}", flush=True)
        for r in rep["runs"][:15]:
            prs = "; ".join(f"{q['part']} in {q['other']}" + (f" {q['depth_mm']:g} mm" if "depth_mm" in q else "")
                            for q in r["pairs"][:4])
            print(f"  arm   {r['label'][:40]:40s} frames {r['first_frame']}-{r['last_frame']} ({r['frames']}): {prs}",
                  flush=True)
        mv = rep.get("movers")
        if mv is not None:
            print(f"{self.sc.name}: movers: {mv['frames_with_collisions']} of {mv['frames_checked']} frames with a new "
                  f"contact deeper than {DEPTH_MM:g} mm, {len(mv['runs'])} runs ({mv['frames_moving']} frames with "
                  f"something moving, {mv['fcl_pairs_checked']} FCL pair checks, {mv['seconds']} s); all: "
                  f"{rep['frames_with_collisions_all']} frames", flush=True)
            for r in mv["runs"][:15]:
                prs = "; ".join(f"{q['body']} into {q['other']} {q['depth_mm']:g} mm" for q in r["pairs"][:3])
                print(f"  mover {r['label'][:40]:40s} frames {r['first_frame']}-{r['last_frame']} ({r['frames']}): "
                      f"{prs}", flush=True)
        return rep

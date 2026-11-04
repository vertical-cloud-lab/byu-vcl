"""Interference check for the animated models, in MuJoCo (#303, PR #318): every moving piece swept through its tour,
every frame, and every hit confirmed on the exact meshes.

Asked on PR #318: "For all those collisions and interferences, couldn't you use something like MuJoCo to simulate
this?" Yes, with one catch. MuJoCo collides convex shapes only: a mesh geom is replaced by its convex hull, so a
cabinet, a chamber or a door frame would look solid and touch everything near it. So:

1. **Geometry.** Each part (a CadQuery solid, as tour.py tessellates it) is tested for convexity. A non-convex part is
   split into convex pieces with CoACD (Wei et al., SIGGRAPH 2022). Each piece is a MuJoCo mesh geom.
2. **MuJoCo model.** One body per moving piece, nested as the pieces ride on each other (``Joint.parent``). Joints
   are MuJoCo joints: ``slide`` a slide joint, ``hinge``/``spin``/``turn`` a hinge through the pivot,
   ``path``/``track`` three slides. ``fade`` pieces are welded to their parent. The model is built with ``MjSpec``
   and can be written out as MJCF (``python3 interference.py mjcf <key>``).
3. **Sweep.** Every action of the tour is played at the tour's 15 fps, with the tour's easing, exactly as
   ``tour.Rig`` drives the pieces. At each frame the joint values become ``qpos``, MuJoCo runs its kinematics and
   collision pipeline, and every penetrating contact between two different pieces is a candidate.
4. **Exact check.** A candidate counts only if the two parts' own triangle meshes overlap at that frame: FCL
   (``python-fcl``) tests the surfaces for a crossing, a point-in-mesh test catches one part inside another, and
   manifold3d computes the overlap's volume and thickness. Hulls are bigger than the parts they cover, so this
   rejects the decomposition's false positives; it can't miss a real overlap, since the hulls cover the parts.

    python3 interference.py                     # every model -> out/interference.json
    python3 interference.py furnace wire_edm    # just these, merged into out/interference.json
    xvfb-run -a python3 interference.py sheet   # out/interference_sheet.png: the worst hits, drawn
    python3 interference.py mjcf furnace        # .cache/interference/mjcf/furnace.xml, for python3 -m mujoco.viewer

Liquids, powders, glows, beams and overlays are not solids and are left out (``VISUAL``). Contacts a model is meant
to have (a specimen in its grips, a plug in its bore) are listed in ``INTENDED`` with the reason, and reported as
such rather than dropped. Overlaps under ``TOUCH_MM`` thick are within the tessellation's chord error and count as
touching.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import math
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "lab_models"))
CACHE = HERE / ".cache" / "interference"
OUT = HERE / "out"
FPS = 15
INTRO, HOLD = 0.6, 0.5                  # tour.py and fab_tour.py: sc.intro, and the hold after every action
TESS = (0.4, 0.2)                       # chord (mm) and angle (rad) tolerances: a little finer than the tour's
TOUCH_MM = 0.6                          # thinner overlaps are tessellation error: touching, not interfering
FAULT_MM = 2.0                          # at least this thick: a fault; between the two: minor
LOOSE_MM = 10.0                         # a moving machine piece this far from the rest of the machine has come loose
CODE = "interference-v1"                     # bump to rebuild the geometry caches
MODULES = ["instruments", "instruments_char", "instruments_lab", "services", "fab_metal", "fab_resin", "fab_pcb",
           "instruments_r7"]

# not solids: fluids, powders, glows, beams, overlays (by material), and the mesh pieces that are powder heaps,
# falling powder or a readout panel's carrier (by piece name)
VISUAL = {"glow", "laser", "plasma", "plasma_halo", "xray", "uv_glow", "water", "lab_nacl", "ipa", "fl_resin", "melt",
          "powder", "powder_coarse", "powder_fine", "powder_mid", "paste", "lab_over", "staging"}
VISUAL_PIECES = ("frac_", "fall_", "stream", "readout",
                 "env",                   # the HIP clip's ghost of the opening
                 "scan")                  # the LPBF laser's 2 mm carrier speck

# Contacts the models are meant to have: (instrument, piece a, piece b, reason). Either order; "*" matches any piece.
INTENDED = [
    ("instron_small", "specimen", "crosshead", "the upper grip's jaws close on the specimen"),
    ("instron_small", "specimen", "body", "the lower grip's jaws close on the specimen"),
    ("instron_floor", "specimen", "crosshead", "the upper grip's jaws close on the specimen"),
    ("instron_floor", "specimen", "body", "the lower grip's jaws close on the specimen"),
    ("press", "plug", "cup", "the plug is a press fit in the cup's bore"),
    ("press", "cup", "nest", "the cup slides in F1, bored to its OD + .0005 in"),
    ("press", "cup", "ejector", "the cup stands on the ejector"),
    ("wire_edm", "wirehead/wire", "load/printed bar", "the wire cutting the bars off at their base: the cut itself"),
    ("ded", "bead*", "bead*", "weld beads fuse with the beads beside and under them"),
    ("ded", "bead*", "load", "the first layer fuses with the substrate"),
    ("vhx", "head/arm", "body/tilt guide", "the free-angle head's arm rides its tilt guide"),
    ("packaging", "arm/H-190 upper jaw", "neck", "the sealer's jaws close on the bag's neck"),
    ("packaging", "body/H-190 jaw", "arm/H-190 upper jaw", "the sealer's jaws close on each other"),
    ("cubxl_corrosion", "cap/pogo", "body/lids", "the cap's pogo pins compress on the lid's pads"),
    ("tray_dock", "head", "tray", "the dock's CombiTac half mates with the tray's: pins in bushings, contacts in "
                                  "contacts"),
    ("form4", "holder/carrier", "load/build platform", "the build platform's spine slots into the carrier"),
    ("form_wash", "holder/carriage", "load/build platform", "the build platform's spine slots into the elevator"),
]


# ================================================================================================= models
def _module(name):
    import instruments as I
    return I if name == "instruments" else importlib.import_module(name)


def registry() -> dict:
    """{key: (module name, build)} over every module, then the charge press."""
    out = {}
    for name in MODULES:
        if (HERE / f"{name}.py").exists():
            for key, build in _module(name).REGISTRY.items():
                out[key] = (name, build)
    out["press"] = ("charge", press_instrument)
    return out


def press_instrument():
    """charge.py's plug press as an Instrument, driven the way alloy_charge.py drives it: the nest out and the cup
    up on the ejector, down into F1, the plug set in the mouth, the nest in, the ram down until the plug is flush,
    then back. The pieces are charge.press_parts()'s meshes."""
    import charge as C
    import instruments as I
    from instruments_lab import Track
    pp = C.press_parts()
    inst = I.Instrument("press", "Plug press", "the alloy route's plug press (assumed), with #222's F1",
                        (2 * C.PR["base_x"], C.PR["base_y"][1] - C.PR["base_y"][0], C.PR["z_top"] + C.PR["motor_h"]),
                        "charge.press_parts()")
    inst.meshes = {"body": [(m, col, 1.0) for m, col in pp["fixed"].values()],
                   "nest": [(m, col, 1.0) for m, col in pp["nest"].values()],
                   "ram": [(pp["ram"][0], pp["ram"][1], 1.0)],
                   "ejector": [(pp["ejector"][0], pp["ejector"][1], 1.0)],
                   "cup": [(C.cup(), C.AL_5N, 1.0)],
                   "plug": [(C.plug(), C.AL_5N, 1.0)]}
    lead = C.PLUG_LEADIN_L * 0.98
    plug_top0 = C.PR["sleeve_top"] - lead + C.PLUG_L
    ry = C.PR["ram_y"]
    inst.joints = {
        "nest": Track("track", knots=((0.0, (0.0, C.PR["out_y"], 0.0)), (1.0, (0.0, ry, 0.0)))),
        "ejector": Track("track", parent="nest", knots=((0.0, (0.0, 0.0, C.PR["nest_top"])),
                                                         (1.0, (0.0, 0.0, C.PR["nest_top"] + C.PR["eject"])))),
        "ram": Track("track", knots=((0.0, (0.0, ry, C.PR["ram_up"])), (0.5, (0.0, ry, plug_top0)),
                                     (1.0, (0.0, ry, C.PR["sleeve_top"])))),
        "cup": I.Joint("fade", parent="ejector", v0=1.0),
        "plug": Track("track", parent="cup", v0=1.0,
                      knots=((0.0, (0.0, 0.0, C.SLUG_L - lead)), (1.0, (0.0, 0.0, C.SLUG_L - C.PLUG_L)))),
    }
    inst.joints["ejector"].v0 = 1.0
    inst.joints["ram"].v0 = 0.0
    inst.joints["plug"].v0 = 0.0
    inst.actions = [
        ("The ejector draws the cup down into F1.", 0.8, {"ejector": (1.0, 0.0)}),
        ("The nest slides in under the ram.", 1.0, {"nest": (0.0, 1.0)}),
        ("The ram comes down onto the plug.", 1.0, {"ram": (0.0, 0.5)}),
        ("The ram presses the plug flush.", 2.2, {"ram": (0.5, 1.0), "plug": (0.0, 1.0)}),
        ("The ram goes back up.", 0.8, {"ram": (1.0, 0.0)}),
        ("The nest slides out.", 0.9, {"nest": (1.0, 0.0)}),
        ("The ejector lifts the cup.", 0.6, {"ejector": (0.0, 0.9)}),
    ]
    inst.props = ("cup", "plug")
    inst.cam = (-0.9, -1.4, 0.8)
    return inst


def _sources(module: str) -> list[Path]:
    files = [HERE / "lab_models" / "common.py", HERE / "instruments.py", HERE / "lab.py"]     # and CODE
    if module == "charge":
        files += [HERE / "charge.py", HERE / "instruments_lab.py"]
    elif module != "instruments":
        files.append(HERE / f"{module}.py")
    return files


# ================================================================================================= geometry
def _tri(points, faces):
    import trimesh
    tm = trimesh.Trimesh(np.asarray(points, float), np.asarray(faces, np.int64), process=True)
    tm.merge_vertices()
    tm.remove_unreferenced_vertices()
    return tm


def _hulls(tm) -> tuple[list, float]:
    """Convex pieces covering the mesh: itself if it is (nearly) convex, else CoACD's decomposition."""
    import coacd
    try:
        hull = tm.convex_hull
        ratio = abs(float(tm.volume)) / max(float(hull.volume), 1e-9) if tm.is_watertight else 0.0
    except Exception:
        return [np.asarray(tm.vertices)], 0.0
    if ratio > 0.97 or len(tm.faces) < 16:
        return [np.asarray(hull.vertices)], ratio
    coacd.set_log_level("error")
    parts = coacd.run_coacd(coacd.Mesh(np.asarray(tm.vertices), np.asarray(tm.faces)), threshold=0.04,
                            max_convex_hull=40, preprocess_resolution=40, resolution=1500, mcts_nodes=16,
                            mcts_iterations=80, mcts_max_depth=2, seed=1)
    out = [np.asarray(v) for v, _ in parts if len(v) >= 4]
    return (out or [np.asarray(hull.vertices)]), ratio


def geo_path(key: str, module: str) -> Path:
    """The geometry cache, keyed on CODE, TESS and the model's sources (not on this file, so editing the check
    doesn't redo the decompositions)."""
    h = hashlib.sha256(f"{CODE} {TESS}".encode())
    for f in _sources(module):
        if f.exists():
            h.update(f.read_bytes())
    return CACHE / f"geo_{key}_{h.hexdigest()[:12]}.pkl"


def geometry(key: str, module: str, build) -> dict:
    """{"inst": Instrument, "parts": [dict(piece, part, material, verts, faces, hulls, ratio)]}, cached."""
    import lab
    CACHE.mkdir(parents=True, exist_ok=True)
    path = geo_path(key, module)
    if path.exists():
        return _solid(pickle.loads(path.read_bytes()))
    inst = build()
    parts = []
    for piece, model in inst.pieces.items():
        for p in model.parts:
            pd = lab.to_mesh(p.shape, *TESS)
            if not pd.n_points:
                continue
            parts.append(dict(piece=piece, part=p.name, material=p.material, pd=pd))
    for piece, ms in inst.meshes.items():
        for i, (pd, col, op) in enumerate(ms):
            if pd is None or not pd.n_points or not pd.n_cells:
                continue
            pd = pd.triangulate()
            parts.append(dict(piece=piece, part=f"mesh {i}", material="mesh", pd=pd))
    out = []
    known = _hull_cache()
    n0 = len(known)
    for p in parts:
        pd = p.pop("pd")
        f = pd.faces.reshape(-1, 4)[:, 1:] if pd.faces.size else np.zeros((0, 3), int)
        if not len(f):
            continue
        tm = _tri(pd.points, f)
        if len(tm.faces) < 4:
            continue
        v, fc = np.asarray(tm.vertices), np.asarray(tm.faces)
        hk = _mesh_key(v, fc)
        if hk not in known:                       # only a part that changed is decomposed again
            known[hk] = _hulls(tm)
        hulls, ratio = known[hk]
        out.append(dict(p, verts=v, faces=fc, hulls=hulls, ratio=ratio, watertight=bool(tm.is_watertight)))
    data = dict(inst=inst, parts=out)
    path.write_bytes(pickle.dumps(data))
    if len(known) > n0:
        (CACHE / "hulls.pkl").write_bytes(pickle.dumps(known))
    return _solid(data)


def _mesh_key(v, f) -> str:
    return hashlib.sha1(np.ascontiguousarray(v, np.float64).tobytes() + np.ascontiguousarray(f, np.int64).tobytes()
                        + CODE.encode()).hexdigest()


_HULLS = None


def _hull_cache() -> dict:
    """{mesh key: (hulls, ratio)}: every part ever decomposed, so editing one part of a model redoes only that part.
    Seeded from the per-model caches the first time."""
    global _HULLS
    if _HULLS is None:
        p = CACHE / "hulls.pkl"
        _HULLS = pickle.loads(p.read_bytes()) if p.exists() else {}
        if not _HULLS:
            for g in CACHE.glob("geo_*.pkl"):
                try:
                    for q in pickle.loads(g.read_bytes())["parts"]:
                        _HULLS.setdefault(_mesh_key(q["verts"], q["faces"]), (q["hulls"], q["ratio"]))
                except Exception:
                    continue
    return _HULLS


def _solid(data: dict) -> dict:
    """Drop what isn't a solid: VISUAL materials and pieces, and invisible meshes (a joint's carrier speck)."""
    inst = data["inst"]

    def keep(p):
        if p["material"] in VISUAL or p["piece"].startswith(VISUAL_PIECES):
            return False
        if p["material"] == "mesh":
            i = int(p["part"].split()[-1])
            ms = inst.meshes.get(p["piece"], [])
            if i < len(ms) and ms[i][2] is not None and ms[i][2] < 0.05:
                return False
        return True
    return dict(inst=inst, parts=[p for p in data["parts"] if keep(p)])


# ================================================================================================= kinematics
def _order(inst) -> list[str]:
    """Moving pieces, each after its parent."""
    out, seen = [], set()

    def visit(k):
        if k in seen or k not in inst.joints:
            return
        j = inst.joints[k]
        if j.parent:
            visit(j.parent)
        seen.add(k)
        out.append(k)
    for k in inst.joints:
        visit(k)
    return out


def world(inst, v: dict) -> dict:
    """{piece: 4x4} as tour.Rig and Scene.world compose them: a piece rides on its parent."""
    cache = {}

    def w(k):
        if k in cache:
            return cache[k]
        j = inst.joints.get(k)
        if j is None:
            m = np.eye(4)
        else:
            m = j.matrix(v.get(k, j.v0))
            if j.parent:
                m = w(j.parent) @ m
        cache[k] = m
        return m
    return {k: w(k) for k in set(inst.pieces) | set(inst.meshes) | set(inst.joints)}


def present(inst, v: dict, piece: str) -> bool:
    """A fade piece is there once it is at least half shown; the rest are always there."""
    j = inst.joints.get(piece)
    while j is not None:
        if j.kind == "fade" and v.get(piece, j.v0) < 0.5:
            return False
        if not j.parent:
            break
        piece, j = j.parent, inst.joints.get(j.parent)
    return True


def frames(inst):
    """Every frame of the tour, as Scene.step plays it: [(action index, frame number, eased u, {piece: v})].
    Frame numbers count from the tour MP4's first frame (the intro, then each action and its hold)."""
    from scene import ease
    v = {k: j.v0 for k, j in inst.joints.items()}
    out = [(-1, 0, 0.0, dict(v))]
    n = int(round(INTRO * FPS))
    for a, (cap, secs, targets) in enumerate(inst.actions):
        tg = {k: t for k, t in targets.items() if not k.startswith("~") and k in inst.joints}
        start = {k: v[k] for k in tg}
        nf = max(1, int(round(secs * FPS)))
        for i in range(1, nf + 1):
            e = ease(i / nf)
            for k, (a0, b0) in tg.items():
                a0 = start[k] if a0 is None else a0
                v[k] = a0 + (b0 - a0) * e
            out.append((a, n + i - 1, i / nf, dict(v)))
        n += nf + max(1, int(round(HOLD * FPS)))
    return out


# ================================================================================================= MuJoCo
def _angle(m: np.ndarray, axis) -> float:
    """The signed angle of m's rotation about `axis` (radians)."""
    r = m[:3, :3]
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    s = 0.5 * np.dot(a, [r[2, 1] - r[1, 2], r[0, 2] - r[2, 0], r[1, 0] - r[0, 1]])
    c = 0.5 * (np.trace(r) - 1.0)
    return math.atan2(s, c)


def _dofs(j) -> str:
    if j.kind == "fade":
        return "weld"
    if j.kind == "slide":
        return "slide" if np.linalg.norm(j.vec) > 0 else "weld"
    if j.kind in ("hinge", "spin", "turn"):
        return "hinge"
    if j.kind in ("path", "track"):
        return "xyz"
    return "free"                         # follow (OpenFlexure's flexures): three slides and a ball


class Sim:
    """An instrument as a MuJoCo model: bodies, joints and convex mesh geoms, and the map back to pieces and parts."""

    def __init__(self, geo: dict):
        import mujoco
        self.mj = mujoco
        self.inst = inst = geo["inst"]
        self.parts = geo["parts"]
        spec = mujoco.MjSpec()
        spec.modelname = inst.key
        spec.option.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_FILTERPARENT)   # check parent-child pairs too
        spec.option.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_GRAVITY)
        spec.memory = 256 * 1024 * 1024
        spec.compiler.inertiafromgeom = mujoco.mjtInertiaFromGeom.mjINERTIAFROMGEOM_FALSE
        self.order = _order(inst)
        bodies = {}
        self.jadr = {}                       # piece -> (kind of dofs, [joint names])
        for k in self.order:
            j = inst.joints[k]
            parent = bodies.get(j.parent, spec.worldbody) if j.parent else spec.worldbody
            b = parent.add_body()
            b.name = f"piece:{k}"
            b.explicitinertial = True
            b.mass = 1.0
            b.inertia = [1.0, 1.0, 1.0]
            kind = _dofs(j)
            names = []
            if kind == "slide":
                jt = b.add_joint()
                jt.name, jt.type = f"{k}:slide", mujoco.mjtJoint.mjJNT_SLIDE
                jt.axis = list(np.asarray(j.vec, float) / np.linalg.norm(j.vec))
                names.append(jt.name)
            elif kind == "hinge":
                jt = b.add_joint()
                jt.name, jt.type = f"{k}:hinge", mujoco.mjtJoint.mjJNT_HINGE
                jt.axis = list(np.asarray(j.axis, float) / np.linalg.norm(j.axis))
                jt.pos = list(np.asarray(j.pivot, float))
                names.append(jt.name)
            elif kind in ("xyz", "free"):
                for ax, e in zip("xyz", np.eye(3)):
                    jt = b.add_joint()
                    jt.name, jt.type, jt.axis = f"{k}:{ax}", mujoco.mjtJoint.mjJNT_SLIDE, list(e)
                    names.append(jt.name)
                if kind == "free":
                    jt = b.add_joint()
                    jt.name, jt.type = f"{k}:ball", mujoco.mjtJoint.mjJNT_BALL
                    names.append(jt.name)
            bodies[k] = b
            self.jadr[k] = (kind, names)
        for pi, p in enumerate(self.parts):
            host = bodies.get(p["piece"], spec.worldbody)
            for hi, hv in enumerate(p["hulls"]):
                ext = hv.max(0) - hv.min(0)
                if np.sort(ext)[0] < 0.02:   # a flat hull has no volume: MuJoCo can't use it
                    hv = np.vstack([hv, hv.mean(0) + np.array([0.01, 0.013, 0.017])])
                me = spec.add_mesh()
                me.name = f"m{pi}_{hi}"
                me.uservert = hv.astype(float).ravel().tolist()
                g = host.add_geom()
                g.name = f"g{pi}_{hi}"
                g.type = mujoco.mjtGeom.mjGEOM_MESH
                g.meshname = me.name
                g.contype, g.conaffinity = 1, 1
                g.margin = 0.0
        self.spec = spec
        self.m = spec.compile()
        self.d = mujoco.MjData(self.m)
        # the compiler groups geoms by body, so map them back by name, not by the order they were added
        self.geom_part = np.array([int(self.m.geom(g).name[1:].split("_")[0]) for g in range(self.m.ngeom)])
        self.qadr = {}
        for k, (kind, names) in self.jadr.items():
            self.qadr[k] = [int(self.m.jnt_qposadr[self.m.joint(n).id]) for n in names]

    def set(self, v: dict):
        """Joint values -> qpos, from each joint's own matrix (so every joint kind moves exactly as in the tour)."""
        inst = self.inst
        q = self.d.qpos
        for k, (kind, names) in self.jadr.items():
            j = inst.joints[k]
            m = j.matrix(v.get(k, j.v0))
            adr = self.qadr[k]
            if kind == "slide":
                u = np.asarray(j.vec, float) / np.linalg.norm(j.vec)
                q[adr[0]] = float(np.dot(m[:3, 3], u))
            elif kind == "hinge":
                q[adr[0]] = _angle(m, j.axis)
            elif kind in ("xyz", "free"):
                q[adr[0]:adr[0] + 3] = m[:3, 3]
                if kind == "free":
                    u_, _, vt = np.linalg.svd(m[:3, :3])   # the nearest rotation to a flexure's small affine motion
                    r = u_ @ vt
                    quat = np.zeros(4)
                    self.mj.mju_mat2Quat(quat, r.ravel())
                    q[adr[3]:adr[3] + 4] = quat
        self.mj.mj_kinematics(self.m, self.d)
        self.mj.mj_collision(self.m, self.d)

    def check_pose(self, v: dict) -> float:
        """Largest difference (mm) between MuJoCo's body poses and the tour's, at the corners of each piece."""
        self.set(v)
        w = world(self.inst, v)
        worst = 0.0
        for k in self.jadr:
            b = self.m.body(f"piece:{k}").id
            mm = np.eye(4)
            mm[:3, :3] = self.d.xmat[b].reshape(3, 3)
            mm[:3, 3] = self.d.xpos[b]
            for p in self.parts:
                if p["piece"] == k:
                    c = np.c_[p["verts"][[0, -1]], np.ones(2)]
                    worst = max(worst, float(np.abs((mm @ c.T - w[k] @ c.T)[:3]).max()))
        return worst

    def contacts(self):
        """[(part i, part j, depth mm)] for every penetrating contact between different pieces."""
        d = self.d
        n = d.ncon
        if not n:
            return []
        g = np.asarray(d.contact.geom[:n])
        dist = np.asarray(d.contact.dist[:n])
        pa, pb = self.geom_part[g[:, 0]], self.geom_part[g[:, 1]]
        out = []
        for a, b, dd in zip(pa, pb, dist):
            if dd < -0.05 and self.parts[a]["piece"] != self.parts[b]["piece"]:
                out.append((int(min(a, b)), int(max(a, b)), float(-dd)))
        return out

    def mjcf(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.spec.to_xml())
        return path


# ================================================================================================= exact check
class Exact:
    """The parts' own triangle meshes: FCL for a crossing, a point-in-mesh test for containment, manifold3d for the
    overlap's volume and thickness."""

    def __init__(self, parts):
        import fcl
        self.fcl = fcl
        self.parts = parts
        self.obj = {}
        self.tm = {}
        self.man = {}

    def _o(self, i):
        if i not in self.obj:
            fcl = self.fcl
            p = self.parts[i]
            b = fcl.BVHModel()
            b.beginModel(len(p["verts"]), len(p["faces"]))
            b.addSubModel(np.asarray(p["verts"], float), np.asarray(p["faces"], np.int32))
            b.endModel()
            self.obj[i] = fcl.CollisionObject(b, fcl.Transform())
        return self.obj[i]

    def _t(self, i):
        if i not in self.tm:
            import trimesh
            p = self.parts[i]
            self.tm[i] = trimesh.Trimesh(p["verts"], p["faces"], process=False)
        return self.tm[i]

    def _m(self, i):
        if i not in self.man:
            import manifold3d as M
            p = self.parts[i]
            try:
                m = M.Manifold(M.Mesh(vert_properties=np.asarray(p["verts"], np.float32),
                                      tri_verts=np.asarray(p["faces"], np.uint32)))
                self.man[i] = m if m.status() == M.Error.NoError and not m.is_empty() else None
            except Exception:
                self.man[i] = None
        return self.man[i]

    def overlap(self, i, j, mi, mj) -> bool:
        """Do parts i and j (at world matrices mi, mj) overlap: surfaces crossing, or one inside the other?"""
        fcl = self.fcl
        oi, oj = self._o(i), self._o(j)
        oi.setTransform(fcl.Transform(mi[:3, :3], mi[:3, 3]))
        oj.setTransform(fcl.Transform(mj[:3, :3], mj[:3, 3]))
        res = fcl.CollisionResult()
        if fcl.collide(oi, oj, fcl.CollisionRequest(num_max_contacts=1, enable_contact=False), res):
            return True
        for a, ma, b, mb in ((i, mi, j, mj), (j, mj, i, mi)):      # containment: a vertex of one inside the other
            if not self.parts[b]["watertight"]:
                continue
            pt = (np.linalg.inv(mb) @ ma @ np.r_[self.parts[a]["verts"][0], 1.0])[:3]
            try:
                if self._t(b).contains([pt])[0]:
                    return True
            except Exception:
                pass
        return False

    def distance(self, i, j, mi, mj) -> float:
        """Least distance (mm) between parts i and j at world matrices mi, mj; 0 if they touch or overlap."""
        fcl = self.fcl
        oi, oj = self._o(i), self._o(j)
        oi.setTransform(fcl.Transform(mi[:3, :3], mi[:3, 3]))
        oj.setTransform(fcl.Transform(mj[:3, :3], mj[:3, 3]))
        return max(0.0, float(fcl.distance(oi, oj, fcl.DistanceRequest(), fcl.DistanceResult())))

    def measure(self, i, j, mi, mj):
        """(volume mm3, thickness mm, centroid world, overlap mesh (verts, faces) in world) or None."""
        a, b = self._m(i), self._m(j)
        if a is None or b is None:
            return None
        x = a.transform(np.asarray(mi[:3], np.float64)) ^ b.transform(np.asarray(mj[:3], np.float64))
        vol = float(x.volume())
        if vol <= 1e-6:
            return (0.0, 0.0, None, None)
        # the thickness is the deepest single overlap: each connected piece's thinnest extent along its own principal
        # axes, so a bag's two thin walls through a foam block read as their own depth, not as the gap between them
        thick, cen = 0.0, None
        for comp in x.decompose():
            cm = comp.to_mesh()
            cv = np.asarray(cm.vert_properties, float)[:, :3]
            if len(cv) < 4 or comp.volume() <= 1e-6:
                continue
            c0 = cv.mean(0)
            _, _, vt = np.linalg.svd(cv - c0, full_matrices=False)
            # its thinnest principal extent, but no more than 4 V / A: a U-shaped overlap (a bag's floor and two
            # walls in a foam pocket) is one piece whose extents are all large, while 4 V / A stays near twice its
            # walls' thickness (a slab of thickness t gives 2t, a cube of side a gives 2a/3)
            t = min(float(np.ptp((cv - c0) @ vt.T, axis=0).min()), 4.0 * comp.volume() / max(comp.surface_area(), 1e-9))
            if t > thick:
                thick, cen = t, c0
        mesh = x.to_mesh()
        v = np.asarray(mesh.vert_properties, float)[:, :3]
        f = np.asarray(mesh.tri_verts, np.int64)
        return (vol, thick, v.mean(0) if cen is None else cen, (v, f))


# ================================================================================================= coming loose
def _aabb(p, m):
    c = np.array([[x, y, z] for x in p["lo_hi"][:, 0] for y in p["lo_hi"][:, 1] for z in p["lo_hi"][:, 2]])
    w = (m[:3, :3] @ c.T).T + m[:3, 3]
    return w.min(0), w.max(0)


def gaps(geo, fr, ex) -> list:
    """Moving machine pieces (not props, not fades) that come loose: at rest and at the end of every action, the
    least distance from the piece to the rest of the machine. A ram that leaves its guide, a frame that floats
    above its columns. Hinge pins and bearings aren't modelled, so gaps under LOOSE_MM don't count."""
    inst, parts = geo["inst"], geo["parts"]
    for p in parts:
        p.setdefault("lo_hi", np.array([p["verts"].min(0), p["verts"].max(0)]))
    props = set(inst.props)
    machine = [i for i, p in enumerate(parts) if p["piece"] not in props]
    moving = [k for k, j in inst.joints.items()
              if j.kind != "fade" and k not in props and any(parts[i]["piece"] == k for i in machine)]
    ends = [fr[0]] + [f for f, nxt in zip(fr, fr[1:] + [None]) if nxt is None or nxt[0] != f[0]]
    out = []
    for k in moving:
        mine = [i for i in machine if parts[i]["piece"] == k]
        others = [i for i in machine if parts[i]["piece"] != k]
        rows = []
        for a, fno, u, v in ends:
            if not present(inst, v, k):
                continue
            w = world(inst, v)
            best = math.inf
            boxes = {i: _aabb(parts[i], w[parts[i]["piece"]]) for i in mine + others
                     if present(inst, v, parts[i]["piece"])}
            for i in mine:
                if i not in boxes:
                    continue
                lo_i, hi_i = boxes[i]
                for j in others:
                    if j not in boxes:
                        continue
                    lo_j, hi_j = boxes[j]
                    lb = float(np.linalg.norm(np.maximum(0.0, np.maximum(lo_i - hi_j, lo_j - hi_i))))
                    if lb >= best:
                        continue
                    best = min(best, ex.distance(i, j, w[parts[i]["piece"]], w[parts[j]["piece"]]))
                    if best == 0.0:
                        break
                if best == 0.0:
                    break
            rows.append((a, fno, best))
        if not rows:
            continue
        rest = rows[0][2]
        worst = max(rows, key=lambda r: r[2])
        if worst[2] > LOOSE_MM:
            out.append(dict(piece=k, gap_at_rest_mm=round(rest, 1), worst_gap_mm=round(worst[2], 1),
                            worst_frame=int(worst[1]),
                            when=inst.actions[worst[0]][0][:90] if worst[0] >= 0 else "as modelled"))
    return out


# ================================================================================================= the check
def _match(pat: str, piece: str, part: str) -> bool:
    """"piece", "piece*" (a prefix), "piece/part name prefix" or "*"."""
    if pat == "*":
        return True
    pc, _, pt = pat.partition("/")
    ok = piece.startswith(pc[:-1]) if pc.endswith("*") else pc == piece
    return ok and part.startswith(pt)


def _intended(key, a, b):
    """The reason a contact between parts a and b (dicts with piece and part) is meant to be, or None."""
    for k, pa, pb, why in INTENDED:
        if k != key:
            continue
        for x, y in ((a, b), (b, a)):
            if _match(pa, x["piece"], x["part"]) and _match(pb, y["piece"], y["part"]):
                return why
    return None


def _not_rigid(inst, fr) -> list[str]:
    """Pieces whose joint (or a parent's) scales or shears as it moves, such as a cable chain whose runs stretch with
    the carriage (a `follow` joint): no rigid body can do that, so MuJoCo can't check them."""
    bad = set()
    for k, j in inst.joints.items():
        for v in sorted({f[3].get(k, j.v0) for f in fr})[::7] + [fr[-1][3].get(k, j.v0)]:
            m = j.matrix(v)[:3, :3]
            if np.abs(m.T @ m - np.eye(3)).max() > 1e-6:
                bad.add(k)
                break
    out = set()
    for k in set(inst.pieces) | set(inst.meshes):
        p = k
        while p is not None:
            if p in bad:
                out.add(k)
                break
            j = inst.joints.get(p)
            p = j.parent if j is not None else None
    return sorted(out)


def check(key: str, module: str, build, verbose=True) -> dict:
    t0 = time.time()
    geo = geometry(key, module, build)
    t_geo = time.time() - t0
    inst = geo["inst"]
    fr = frames(inst)
    stretch = _not_rigid(inst, fr)
    if stretch:
        geo = dict(geo, parts=[p for p in geo["parts"] if p["piece"] not in stretch])
    parts = geo["parts"]
    sim = Sim(geo)
    pose_err = max(sim.check_pose(fr[k][3]) for k in sorted({0, len(fr) // 2, len(fr) - 1}))
    ex = Exact(parts)
    hits = {}                                     # (i, j) -> dict
    meant = {}                                    # (i, j) -> listed in INTENDED
    n_cand = n_conf = n_skip = 0
    t1 = time.time()
    for a, fno, u, v in fr:
        sim.set(v)
        cands = {}
        for i, j, depth in sim.contacts():
            cands[(i, j)] = max(cands.get((i, j), 0.0), depth)
        if not cands:
            continue
        w = world(inst, v)
        for (i, j), depth in cands.items():
            pi, pj = parts[i]["piece"], parts[j]["piece"]
            if not (present(inst, v, pi) and present(inst, v, pj)):
                continue
            n_cand += 1
            if (i, j) not in meant:
                meant[(i, j)] = _intended(key, parts[i], parts[j]) is not None
            if meant[(i, j)] and (i, j) in hits and fno % 10:      # intended (DED's fused beads): every 10th frame
                n_skip += 1
                continue
            if not ex.overlap(i, j, w[pi], w[pj]):
                continue
            n_conf += 1
            h = hits.setdefault((i, j), dict(frames=[], mj_depth=0.0))
            h["frames"].append((a, fno, u))
            h["mj_depth"] = max(h["mj_depth"], depth)
            h.setdefault("_poses", []).append((w[pi], w[pj], fno))
    t_sweep = time.time() - t1
    # measure each confirmed pair at up to 12 of its frames, keep the deepest
    findings = []
    for (i, j), h in hits.items():
        poses = h.pop("_poses")
        pick = np.unique(np.linspace(0, len(poses) - 1, min(12, len(poses))).round().astype(int))
        best = None
        for k in pick:
            mi, mj, fno = poses[k]
            r = ex.measure(i, j, mi, mj)
            if r is None:
                continue
            if best is None or r[1] > best[0][1] or (r[1] == best[0][1] and r[0] > best[0][0]):
                best = (r, fno)
        pa, pb = parts[i], parts[j]
        acts = sorted({f[0] for f in h["frames"]})
        rest = h["frames"][0][0] == -1                   # overlapping as modelled, before anything moves
        if best is None:
            vol = thick = None
            cen = None
            fmax = h["frames"][0][1]
        else:
            (vol, thick, cen, _), fmax = best
        if thick is not None and thick < TOUCH_MM:
            level = "touching"
        elif thick is None:
            level = "unmeasured"
        else:
            level = "fault" if thick >= FAULT_MM else "minor"
        why = _intended(key, pa, pb)
        vols = [r for r in (ex.measure(i, j, *poses[k][:2]) for k in pick[:4]) if r is not None] if rest else []
        steady = bool(vols) and max(r[0] for r in vols) <= 1.5 * max(1e-9, min(r[0] for r in vols))
        kind = ("guide" if rest and steady and len(h["frames"]) >= 0.9 * len(fr) else
                "built in" if rest else "motion")
        findings.append(dict(
            a=f"{pa['piece']} / {pa['part']}", b=f"{pb['piece']} / {pb['part']}",
            pieces=[pa["piece"], pb["piece"]], level=level, kind=kind, intended=why,
            at_rest=bool(rest), all_frames=len(h["frames"]) == len(fr),
            thickness_mm=None if thick is None else round(thick, 2),
            volume_mm3=None if vol is None else round(vol, 1),
            mujoco_depth_mm=round(h["mj_depth"], 2),
            frames=len(h["frames"]), first_frame=int(h["frames"][0][1]), last_frame=int(h["frames"][-1][1]),
            worst_frame=int(fmax), at_mm=None if cen is None else [round(float(c), 1) for c in cen],
            actions=[a for a in acts],
            captions=[inst.actions[a][0][:90] if a >= 0 else "as modelled" for a in acts]))
    order = {"fault": 0, "minor": 1, "unmeasured": 2, "touching": 3}
    korder = {"motion": 0, "built in": 1, "guide": 2}
    findings.sort(key=lambda f: (f["intended"] is not None, order[f["level"]], korder[f["kind"]],
                                 -(f["thickness_mm"] or 0)))
    t2 = time.time()
    loose = gaps(geo, fr, ex)
    t_gap = time.time() - t2
    n_hull = sum(len(p["hulls"]) for p in parts)
    res = dict(key=key, title=inst.title, model=inst.model, module=module, frames=len(fr),
               parts=len(parts), nonconvex_parts=sum(1 for p in parts if len(p["hulls"]) > 1 or p["ratio"] < 0.97),
               mujoco_geoms=n_hull, moving_pieces=len(sim.jadr),
               pose_error_mm=round(pose_err, 6), candidates=n_cand, confirmed=n_conf,
               intended_not_rechecked=n_skip, rejected_by_exact=n_cand - n_conf - n_skip,
               seconds=dict(geometry=round(t_geo, 1), sweep=round(t_sweep, 1), loose=round(t_gap, 1),
                            total=round(time.time() - t0, 1)),
               findings=findings, loose=loose, not_rigid_left_out=stretch)
    if verbose:
        nf = sum(1 for f in findings if f["level"] == "fault" and not f["intended"])
        nm = sum(1 for f in findings if f["level"] == "minor" and not f["intended"])
        print(f"{key:18s} {len(fr):5d} frames {n_hull:4d} geoms  candidates {n_cand:6d}, exact {n_conf:6d}  "
              f"faults {nf}, minor {nm}  ({res['seconds']['total']} s, pose err {pose_err:.1e} mm)", flush=True)
        for f in findings:
            if f["level"] in ("fault", "minor") and not f["intended"]:
                print(f"    {f['level']:6s} {f['kind']:8s} {f['thickness_mm']} mm {f['volume_mm3']} mm3  {f['a']}  x  "
                      f"{f['b']}  frames {f['first_frame']}-{f['last_frame']}  {f['captions'][:2]}"[:300], flush=True)
        for g in loose:
            print(f"    loose  {g['piece']}: {g['worst_gap_mm']} mm from the machine at frame {g['worst_frame']} "
                  f"(at rest {g['gap_at_rest_mm']}): {g['when']}", flush=True)
    return res


# ================================================================================================= the sheet
def sheet(n=12, cols=4):
    """out/interference_sheet.png: the worst unintended hits, each the instrument at its worst frame, the two pieces in
    colour, the rest faint, the overlap in red."""
    import pyvista as pv
    from PIL import Image, ImageDraw
    from scene import font
    rep = json.loads((OUT / "interference.json").read_text())
    rows = []
    for key, r in rep["models"].items():
        best = {}
        for f in r.get("findings", []):
            if f["level"] == "fault" and f["kind"] == "motion" and not f["intended"] and f["at_mm"] is not None:
                pair = tuple(sorted(f["pieces"]))           # one tile per pair of pieces: the deepest
                if pair not in best or f["thickness_mm"] > best[pair]["thickness_mm"]:
                    best[pair] = f
        rows += [(key, f) for f in best.values()]
    rows.sort(key=lambda kf: -(kf[1]["thickness_mm"] or 0))
    rows = rows[:n]
    reg = registry()
    tw, th, cap = 480, 330, 62
    sh = Image.new("RGB", (tw * cols, (th + cap) * max(1, (len(rows) + cols - 1) // cols)), "white")
    dr = ImageDraw.Draw(sh)
    pl = pv.Plotter(off_screen=True, window_size=(tw * 2, th * 2))
    pl.set_background("white")
    for idx, (key, f) in enumerate(rows):
        module, build = reg[key]
        geo = geometry(key, module, build)
        inst, parts = geo["inst"], geo["parts"]
        v = next(vv for a, fno, u, vv in frames(inst) if fno >= f["worst_frame"])
        w = world(inst, v)
        pl.clear_actors()
        ia = ib = None
        for i, p in enumerate(parts):
            if not present(inst, v, p["piece"]):
                continue
            nm = f"{p['piece']} / {p['part']}"
            mesh = pv.PolyData(p["verts"], np.c_[np.full(len(p["faces"]), 3), p["faces"]].ravel())
            mesh = mesh.transform(w[p["piece"]], inplace=False)
            if nm == f["a"]:
                pl.add_mesh(mesh, color=(0.95, 0.55, 0.15), opacity=0.55, smooth_shading=False)
                ia = i
            elif nm == f["b"]:
                pl.add_mesh(mesh, color=(0.20, 0.45, 0.80), opacity=0.55, smooth_shading=False)
                ib = i
            else:
                pl.add_mesh(mesh, color=(0.72, 0.73, 0.75), opacity=0.12, smooth_shading=False)
        if ia is not None and ib is not None:
            ex = Exact(parts)
            r = ex.measure(ia, ib, w[parts[ia]["piece"]], w[parts[ib]["piece"]])
            if r and r[3] is not None:
                vv, ff = r[3]
                pl.add_mesh(pv.PolyData(vv, np.c_[np.full(len(ff), 3), ff].ravel()), color=(0.9, 0.05, 0.05))
        c = np.asarray(f["at_mm"], float)
        x0, x1, y0, y1, z0, z1 = inst.bbox()
        size = np.linalg.norm([x1 - x0, y1 - y0, z1 - z0])
        dist = max(250.0, 0.45 * size)
        dd = np.asarray(inst.cam, float)
        dd /= np.linalg.norm(dd)
        pl.camera_position = [tuple(c + dd * dist), tuple(c), (0, 0, 1)]
        pl.camera.view_angle = 30.0
        pl.render()
        img = pl.screenshot(return_img=True)
        x, y = (idx % cols) * tw, (idx // cols) * (th + cap)
        sh.paste(Image.fromarray(img).resize((tw, th), Image.LANCZOS), (x, y))
        dr.text((x + 8, y + th + 3), f"{inst.model[:46]}", font=font(14, bold=True), fill=(20, 20, 24))
        dr.text((x + 8, y + th + 21), f"{f['a'][:30]}  x  {f['b'][:30]}", font=font(12), fill=(70, 72, 78))
        dr.text((x + 8, y + th + 38), f"{f['thickness_mm']:.1f} mm deep, tour frames {f['first_frame']}-"
                f"{f['last_frame']} (worst {f['worst_frame']})", font=font(12), fill=(170, 30, 30))
    pl.close()
    path = OUT / "interference_sheet.png"
    sh.save(path, optimize=True)
    return path


# ================================================================================================= main
def run(keys=None) -> dict:
    path = OUT / "interference.json"
    rep = json.loads(path.read_text()) if path.exists() and keys else dict(models={})
    reg = registry()
    for key, (module, build) in reg.items():
        if keys and key not in keys:
            continue
        try:
            rep["models"][key] = check(key, module, build)
        except FileNotFoundError as e:           # the OpenFlexure meshes need OpenSCAD (openflexure/README.md)
            rep["models"][key] = dict(key=key, skipped=f"{type(e).__name__}: {e}"[:200])
            print(f"{key:18s} skipped: {e}"[:160], flush=True)
    models = rep["models"]
    done = [r for r in models.values() if "findings" in r]
    rep["summary"] = dict(
        models_checked=len(done), models_skipped=sorted(k for k, r in models.items() if "skipped" in r),
        frames=sum(r["frames"] for r in done), mujoco_geoms=sum(r["mujoco_geoms"] for r in done),
        candidates=sum(r["candidates"] for r in done), confirmed=sum(r["confirmed"] for r in done),
        rejected_by_exact=sum(r.get("rejected_by_exact", 0) for r in done),
        faults=sum(1 for r in done for f in r["findings"] if f["level"] == "fault" and not f["intended"]),
        minor=sum(1 for r in done for f in r["findings"] if f["level"] == "minor" and not f["intended"]),
        moving_faults=sum(1 for r in done for f in r["findings"]
                          if f["level"] == "fault" and f["kind"] == "motion" and not f["intended"]),
        intended=sum(1 for r in done for f in r["findings"] if f["intended"]),
        loose=sum(len(r.get("loose", [])) for r in done),
        seconds=round(sum(r["seconds"]["total"] for r in done), 1))
    rep["method"] = dict(tessellation_mm_rad=TESS, touching_below_mm=TOUCH_MM, fault_from_mm=FAULT_MM, fps=FPS,
                         visual_materials_left_out=sorted(VISUAL), mujoco=__import__("mujoco").__version__)
    path.write_text(json.dumps(rep, indent=1) + "\n")
    return rep


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "sheet":
        print(sheet())
    elif args and args[0] == "mjcf":
        reg = registry()
        for key in args[1:]:
            module, build = reg[key]
            print(Sim(geometry(key, module, build)).mjcf(CACHE / "mjcf" / f"{key}.xml"))
    else:
        r = run(args or None)
        print(json.dumps(r["summary"], indent=1))

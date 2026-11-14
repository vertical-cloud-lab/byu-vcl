"""People for the vertical-lab clips (#303, PR #318, round 11): a skinned human, dressed for the lab.

Sterling on round 10's figure (capsule limbs on a box of a coat, an egg of a head): "Yikes.. That's kind of a cringy
looking human, although I don't totally dislike the idea of showing an actual person with movement." This one is
MakeHuman's base mesh (hm08, one smooth body of 13,380 vertices with a face, ears and fingers) on MakeHuman's default
skeleton and its skin weights, posed every frame by linear-blend skinning in numpy: a walk cycle, a lean from the hips,
both arms solved to hand targets (two-bone IK, elbows out and down), the head turned to what the person looks at, the
fingers curled. It is dressed by region: a lab coat over the torso and arms to the wrists (the body's own surface
pushed out 12 mm), with its skirt to mid-thigh (MakeHuman's skirt helper) and a collar; dark trousers; shoes; blue
nitrile gloves; skin on the face and neck; short hair; wrap-around safety glasses. 1.75 m with shoes.

Sources, fetched at run time into ``.cache/makehuman/`` and never committed, pinned to one commit of
https://github.com/makehumancommunity/makehuman (CC0 1.0: section C of its LICENSE.md, "The license for the bundled
assets", which covers the base mesh and the rigs):

* ``makehuman/data/3dobjs/base.obj``: the base mesh. Its ``body``, ``helper-skirt`` and the two eye groups are used;
  the other helpers (tights, hair, teeth, tongue, eyelashes, genitals) and the ``joint-*`` marker groups are dropped.
* ``makehuman/data/rigs/default.mhskel``: the default skeleton (163 bones; each joint is the mean of a joint group's
  vertices). The face's 60-odd bones are folded into ``head`` and the toes into ``foot``: 74 bones are posed.
* ``makehuman/data/rigs/default_weights.mhw``: its skin weights.

API as round 10's ``upkeep_clip.Person``: ``set(x, y, hd, lean, phase, amp, hands, look=None, grip=None)``,
``hold``, ``let_go``, ``held``, ``rest_hand``, ``names``, ``show``.

    xvfb-run -a python3 people.py        # close-up stills of the poses -> /tmp/people_*.png
"""
from __future__ import annotations

import functools
import hashlib
import json
import math
import pickle
import urllib.request
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache" / "makehuman"
MH_SHA = "a8bc2d54ff0ac92e78ff71431b1023eda42bf482"      # makehumancommunity/makehuman, master, 2024-06-26
MH_URL = f"https://raw.githubusercontent.com/makehumancommunity/makehuman/{MH_SHA}/makehuman/data/{{path}}"
FILES = {
    "base.obj": ("3dobjs/base.obj", "8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c"),
    "default.mhskel": ("rigs/default.mhskel", "99f179bce0aa850b45d4191a1d0d234c5851f881c057439470ded3bddf729a24"),
    "default_weights.mhw": ("rigs/default_weights.mhw",
                            "0f3641d651ae3d00ad6b4ccee43142edb109d3bd909d27d9e4139ef1beed8625"),
}
MODEL_V = 11                         # bump when the derived model changes (the cached pickle's name)

HEIGHT = 1735.0                     # the body, sole to crown, mm; the shoes add ~10 mm and the hair ~5: 1.75 m
SOLE = 10.0                         # the shoes' sole under the foot
SKIN = (0.80, 0.64, 0.53)
COAT = (0.93, 0.94, 0.95)
SHIRT = (0.62, 0.71, 0.82)          # a light blue shirt in the coat's V
TROUSERS = (0.21, 0.24, 0.31)
SHOES = (0.11, 0.11, 0.12)
GLOVE = (0.27, 0.48, 0.85)          # nitrile
HAIR = (0.24, 0.17, 0.12)
BROW = (0.22, 0.16, 0.12)
IRIS = (0.20, 0.14, 0.10)
SCLERA = (0.93, 0.92, 0.90)
LENS = (0.80, 0.88, 0.93)
FRAME = (0.16, 0.18, 0.22)

# offsets along the posed normals, mm: the coat and its skirt stand off the body; the trousers are loose
OFFSET = dict(coat=12.0, skirt=15.0, collar=12.0, trousers=7.0, shoes=9.0, glove=1.2, hair=6.0, shirt=1.5, brow=0.8)

FACE_BONES = ("levator", "oris", "risorius", "oculi", "orbicularis", "temporalis", "tongue", "special", "jaw", "eye")


# ================================================================================================ the assets
def _fetch(key: str) -> Path:
    path, sha = FILES[key]
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / key
    if not out.exists():
        req = urllib.request.Request(MH_URL.format(path=path), headers={"User-Agent": "Mozilla/5.0"})
        tmp = out.with_suffix(out.suffix + ".part")
        tmp.write_bytes(urllib.request.urlopen(req, timeout=300).read())
        tmp.replace(out)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    if digest != sha:
        raise RuntimeError(f"{out}: sha256 {digest}, expected {sha} (MakeHuman {MH_SHA[:7]})")
    return out


def _merged(bone: str) -> str:
    """The posed bone a MakeHuman bone's weights go to: the face's bones to the head, toes to the foot, the breasts
    to the chest."""
    if bone.startswith(FACE_BONES):
        return "head"
    if bone.startswith("toe"):
        return "foot" + bone[-2:]
    if bone.startswith("breast"):
        return "spine02"
    return bone


def _to_ours(p: np.ndarray, k: float, y0: float) -> np.ndarray:
    """MakeHuman (x to the figure's left, y up, z forward, decimetres) to ours (x to its right, y forward, z up, mm,
    the soles at z = SOLE). A rotation, no mirror."""
    p = np.asarray(p, float)
    return np.stack([-p[..., 0] * k, p[..., 2] * k, (p[..., 1] - y0) * k + SOLE], axis=-1)


def _build_model() -> dict:
    obj, skel, wts = (_fetch(k) for k in FILES)
    verts, groups, cur = [], {}, None
    for line in obj.read_text().splitlines():
        if line.startswith("v "):
            verts.append([float(t) for t in line.split()[1:4]])
        elif line.startswith("g "):
            cur = line.split()[1]
        elif line.startswith("f "):
            groups.setdefault(cur, []).append([int(t.split("/")[0]) - 1 for t in line.split()[1:]])
    Vmh = np.array(verts)
    keep = ("body", "helper-skirt", "helper-l-eye", "helper-r-eye")
    quads = {g: np.array(groups[g], int) for g in keep}
    body_v = np.unique(quads["body"])
    y0, y1 = Vmh[body_v, 1].min(), Vmh[body_v, 1].max()
    k = HEIGHT / (y1 - y0)
    sk = json.loads(skel.read_text())
    J = {name: _to_ours(Vmh[idx].mean(0), k, y0) for name, idx in sk["joints"].items()}
    # the posed bones, parents before children
    bones = {}
    for b, d in sk["bones"].items():
        if _merged(b) != b:
            continue
        bones[b] = dict(parent=d["parent"], head=J[d["head"]], tail=J[d["tail"]])
    order, done = [], set()
    while len(order) < len(bones):
        for b, d in bones.items():
            if b not in done and (d["parent"] is None or d["parent"] in done):
                order.append(b)
                done.add(b)
    # the used vertices, re-indexed
    used = np.unique(np.concatenate([q.ravel() for q in quads.values()]))
    remap = -np.ones(len(Vmh), int)
    remap[used] = np.arange(len(used))
    V = _to_ours(Vmh[used], k, y0)
    tris = {}
    for g, q in quads.items():
        q = remap[q]
        tris[g] = np.r_[q[:, [0, 1, 2]], q[:, [0, 2, 3]]]
    # skin weights onto the posed bones, normalised per vertex
    bidx = {b: i for i, b in enumerate(order)}
    acc = {}
    for b, lst in json.loads(wts.read_text())["weights"].items():
        j = bidx[_merged(b)]
        for vi, w in lst:
            r = remap[vi]
            if r >= 0:
                acc[(r, j)] = acc.get((r, j), 0.0) + w
    rows = np.array([r for r, _ in acc], int)
    cols = np.array([c for _, c in acc], int)
    vals = np.array(list(acc.values()), float)
    tot = np.bincount(rows, weights=vals, minlength=len(V))
    vals = vals / tot[rows]
    dom = np.zeros(len(V), int)                      # each vertex's heaviest bone
    best = np.zeros(len(V))
    for r, c, w in zip(rows, cols, vals):
        if w > best[r]:
            best[r], dom[r] = w, c
    eyes = {s: V[np.unique(remap[quads[f"helper-{s}-eye"]])].mean(0) for s in ("l", "r")}
    return dict(V=V, tris=tris, order=order, parent=[bidx.get(bones[b]["parent"], -1) for b in order],
                head=np.array([bones[b]["head"] for b in order]), tail=np.array([bones[b]["tail"] for b in order]),
                rows=rows, cols=cols, vals=vals, dom=dom, eyes=eyes, scale=k, y0=y0)


@functools.lru_cache(maxsize=None)
def model() -> dict:
    src = Path(__file__).read_text()
    key = hashlib.sha256((src + MH_SHA).encode()).hexdigest()[:12]
    path = CACHE / f"model_v{MODEL_V}_{key}.pkl"
    if path.exists():
        try:
            return pickle.loads(path.read_bytes())
        except Exception:                               # noqa: BLE001
            pass
    m = _build_model()
    m.update(_dress(m))
    CACHE.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    tmp.write_bytes(pickle.dumps(m))
    tmp.replace(path)
    return m


# ================================================================================================ the clothes
TROUSER_BONES = ("root", "pelvis", "upperleg", "lowerleg", "foot")
TRUNK_BONES = ("spine", "clavicle")


def _poly(P, F, W=None) -> pv.PolyData:
    m = pv.PolyData(np.asarray(P, float), np.c_[np.full(len(F), 3), np.asarray(F, int)].ravel())
    if W is not None:
        m.point_data["W"] = np.asarray(W, np.float32)
    return m


def _faces(m: pv.PolyData) -> np.ndarray:
    m = m.triangulate()
    f = np.asarray(m.faces).reshape(-1, 4)
    return f[:, 1:].astype(int)


def _split(m: pv.PolyData, field: np.ndarray) -> tuple[pv.PolyData, pv.PolyData]:
    """(where field > 0, the rest), cut along field = 0 (the weights are interpolated onto the cut)."""
    m = m.copy()
    m.point_data["_f"] = np.asarray(field, float)
    m.set_active_scalars("_f")
    pos = m.clip_scalar(scalars="_f", value=0.0, invert=False)
    neg = m.clip_scalar(scalars="_f", value=0.0, invert=True)
    out = []
    for x in (pos, neg):
        x = pv.PolyData(x.extract_surface(algorithm=None)) if not isinstance(x, pv.PolyData) else x
        x = x.triangulate().clean(tolerance=1e-6)
        for k in list(x.point_data.keys()):
            if k != "W":
                del x.point_data[k]
        out.append(x)
    return out[0], out[1]


def _drape(P: np.ndarray, mask: np.ndarray, axis, z_top: float, nbins: int = 60) -> np.ndarray:
    """A coat hangs: below z_top its radius about the body's vertical axis never comes back in (it can't tuck into
    the waist), at the front and back; at the sides, where the arms hang, it follows the body."""
    idx = np.where(mask & (P[:, 2] <= z_top))[0]
    if not len(idx):
        return P
    d = P[idx, :2] - axis
    r = np.hypot(d[:, 0], d[:, 1])
    phi = np.arctan2(d[:, 1], d[:, 0])
    b = ((phi + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins
    newr = r.copy()
    for k in range(nbins):
        s = np.where((b == k) | (b == (k - 1) % nbins) | (b == (k + 1) % nbins))[0]
        own = b[s] == k
        if not own.any():
            continue
        o = s[np.argsort(-P[idx[s], 2])]
        run = np.maximum.accumulate(r[o])
        sel = b[o] == k
        newr[o[sel]] = run[sel]
    w = np.clip((np.abs(np.sin(phi)) - 0.40) / 0.35, 0.0, 1.0)
    newr = r + w * (newr - r)
    out = P.copy()
    out[idx, :2] = axis + d * (newr / np.maximum(r, 1e-9))[:, None]
    return out


def _offset(m: pv.PolyData, mm: float, smooth: int = 0) -> pv.PolyData:
    m = m.copy()
    if smooth:
        W = m.point_data["W"].copy()
        m = m.smooth_taubin(n_iter=smooth, pass_band=0.08, boundary_smoothing=False, feature_smoothing=False)
        m.point_data["W"] = W
    if mm:
        F = _faces(m)
        N = _normals(np.asarray(m.points, float), F, m.n_points)
        m.points = np.asarray(m.points, float) + mm * N
    return m


def _bridge(P: np.ndarray, mask: np.ndarray, sign: float, dz: float = 14.0) -> np.ndarray:
    """Cloth stretched across a hollow: in each height slice, the masked points' profile y(x) (sign +1: the front,
    -1: the back) is raised to its convex hull, so a coat spans the chest and the back instead of following them."""
    out = P.copy()
    idx = np.where(mask)[0]
    if len(idx) < 3:
        return out
    z = P[idx, 2]
    for z0 in np.arange(z.min(), z.max() + dz, dz):
        win = idx[(z >= z0 - 1.5 * dz) & (z < z0 + 1.5 * dz)]
        mine = idx[(z >= z0 - dz / 2) & (z < z0 + dz / 2)]
        if len(win) < 3 or not len(mine):
            continue
        o = np.argsort(P[win, 0])
        pts = np.c_[P[win, 0][o], sign * P[win, 1][o]]
        hull = []
        for q in pts:
            while len(hull) >= 2 and ((hull[-1][0] - hull[-2][0]) * (q[1] - hull[-2][1]) -
                                      (hull[-1][1] - hull[-2][1]) * (q[0] - hull[-2][0])) >= 0:
                hull.pop()
            hull.append(q)
        hx, hy = np.array(hull).T
        if len(hx) < 2:
            continue
        yh = np.interp(P[mine, 0], hx, hy)
        out[mine, 1] = sign * np.maximum(sign * P[mine, 1], yh)
    return out


def _vbridge(P: np.ndarray, mask: np.ndarray, axis, nbins: int = 48) -> np.ndarray:
    """Cloth hangs over hollows top to bottom too: at the front and the back, each angular sector's profile r(z) about
    the body's vertical axis is raised to its convex hull, so the coat runs straight from the shoulder blades to the
    seat (and from the chest down) instead of following the small of the back."""
    idx = np.where(mask)[0]
    if len(idx) < 3:
        return P
    d = P[idx, :2] - axis
    r = np.hypot(d[:, 0], d[:, 1])
    phi = np.arctan2(d[:, 1], d[:, 0])
    b = ((phi + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins
    z = P[idx, 2]
    newr = r.copy()
    for k in range(nbins):
        s = np.where((b == k) | (b == (k - 1) % nbins) | (b == (k + 1) % nbins))[0]
        mine = np.where(b == k)[0]
        if len(s) < 3 or not len(mine):
            continue
        o = s[np.argsort(z[s])]
        hull = []
        for q in zip(z[o], r[o]):
            while len(hull) >= 2 and ((hull[-1][0] - hull[-2][0]) * (q[1] - hull[-2][1]) -
                                      (hull[-1][1] - hull[-2][1]) * (q[0] - hull[-2][0])) >= 0:
                hull.pop()
            hull.append(q)
        hz, hr = np.array(hull).T
        if len(hz) < 2:
            continue
        newr[mine] = np.maximum(r[mine], np.interp(z[mine], hz, hr))
    w = np.clip((np.abs(np.sin(phi)) - 0.40) / 0.35, 0.0, 1.0)
    newr = r + w * (newr - r)
    out = P.copy()
    out[idx, :2] = axis + d * (newr / np.maximum(r, 1e-9))[:, None]
    return out


def _leg_drape(P: np.ndarray, mask: np.ndarray, knee: np.ndarray, ankle: np.ndarray, nbins: int = 40) -> np.ndarray:
    """A trouser leg hangs straight from the knee: about the shin's axis, its radius never comes back in going
    down."""
    e3 = _unit(knee - ankle)
    e1 = _unit(np.cross(e3, (0.0, 1.0, 0.0)))
    e2 = np.cross(e3, e1)
    idx = np.where(mask)[0]
    if not len(idx):
        return P
    d = P[idx] - ankle
    h = d @ e3
    q = np.c_[d @ e1, d @ e2]
    r = np.hypot(q[:, 0], q[:, 1])
    phi = np.arctan2(q[:, 1], q[:, 0])
    b = ((phi + np.pi) / (2 * np.pi) * nbins).astype(int) % nbins
    top = float((knee - ankle) @ e3)
    newr = r.copy()
    for k in range(nbins):
        s = np.where(((b == k) | (b == (k - 1) % nbins) | (b == (k + 1) % nbins)) & (h <= top))[0]
        if not len(s):
            continue
        o = s[np.argsort(-h[s])]
        run = np.maximum.accumulate(r[o])
        sel = b[o] == k
        newr[o[sel]] = run[sel]
    out = P.copy()
    scale = newr / np.maximum(r, 1e-9)
    out[idx] = ankle + np.outer(h, e3) + (q[:, :1] * scale[:, None]) * e1 + (q[:, 1:] * scale[:, None]) * e2
    return out


def _dress(m: dict) -> dict:
    """The parts drawn in one colour each, in the rest pose: {part: dict(P, F, rows, cols, vals)}; region edges are
    cut along smooth lines (the weights interpolated onto them), the garments smoothed, draped and pushed out."""
    V, order = m["V"], m["order"]
    nb = len(order)
    Wd = np.zeros((len(V), nb), np.float32)
    Wd[m["rows"], m["cols"]] = m["vals"]
    H = lambda b: m["head"][order.index(b)]          # noqa: E731
    bones = np.array(order)

    def dom(W):
        return bones[np.asarray(W).argmax(1)]

    tb = m["tris"]["body"]
    bv, inv = np.unique(tb, return_inverse=True)
    body = _poly(V[bv], inv.reshape(-1, 3), Wd[bv])
    P = V[bv]
    db = dom(Wd[bv])
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    n0 = H("neck01")
    # 1. the head and neck above the collar line (lower at the front, rising over the shoulders)
    zc = n0[2] - 34.0 + 0.50 * (n0[1] - y) + 1.7 * np.maximum(np.abs(x) - 50.0, 0.0)
    # the shirt (a scrub top) has its own V-neck: the skin shows in a narrow V under the neck, down to z_vs
    z_vs = n0[2] - 105.0
    f_vs = np.minimum(0.62 * (z - z_vs) - np.abs(x), y - (n0[1] + 15.0))
    headneck = np.isin(db, ["head", "neck01", "neck02", "neck03", "spine01", "spine02", "clavicle.L", "clavicle.R"])
    upper, lower = _split(body, np.where(headneck, np.maximum(z - zc, f_vs), -200.0))
    # hair: the scalp above a line from the forehead's hairline down to the nape, not over the ears
    eye = (m["eyes"]["l"] + m["eyes"]["r"]) / 2
    Pu = np.asarray(upper.points)
    zr, yr, ax_ = Pu[:, 2] - eye[2], Pu[:, 1] - eye[1], np.abs(Pu[:, 0])
    f_hair = zr - (48.0 - 0.55 * np.clip(-yr - 25.0, -40.0, 220.0) + 0.20 * np.maximum(yr, 0.0))
    f_ear = np.maximum.reduce([58.0 - ax_, zr - 40.0, -100.0 - yr, (-yr - 150.0)])
    hair, skin = _split(upper, np.minimum(f_hair, np.maximum(f_ear, (zr - 40.0) * 3.0)))
    # the hair: thicker over the crown, thinning to nothing at its line (not a cap's hard edge)
    hair = _offset(hair, 0.0, smooth=12)
    Ph = np.asarray(hair.points, float)
    zr_h, yr_h = Ph[:, 2] - eye[2], Ph[:, 1] - eye[1]
    fh = zr_h - (48.0 - 0.55 * np.clip(-yr_h - 25.0, -40.0, 220.0) + 0.20 * np.maximum(yr_h, 0.0))
    Nh = _normals(Ph, _faces(hair), len(Ph))
    hair.points = Ph + (1.5 + 9.0 * np.clip(fh / 45.0, 0.0, 1.0))[:, None] * Nh
    # the brows: two short arcs over the eyes
    Ps = np.asarray(skin.points)
    f_brow = np.full(len(Ps), -50.0)
    for sd in ("l", "r"):
        e = m["eyes"][sd]
        u = (Ps[:, 0] - e[0]) / 25.0
        v = (Ps[:, 2] - (e[2] + 17.0 - 6.0 * u * u)) / 3.6
        f_brow = np.maximum(f_brow, np.where(Ps[:, 1] > e[1] - 12.0, 1.0 - u * u - v * v, -50.0))
    brow, skin = _split(skin, f_brow)
    # 2. the shirt in the coat's V
    Pl = np.asarray(lower.points)
    zv0 = H("spine01")[2] - 60.0
    f_v = np.minimum(0.45 * (Pl[:, 2] - zv0) - np.abs(Pl[:, 0]), Pl[:, 1] - (n0[1] + 25.0))
    shirt, lower = _split(lower, f_v)
    # 3. the gloves, 55 mm up the forearm from the wrist
    Pl = np.asarray(lower.points)
    dl = dom(lower.point_data["W"])
    f_g = np.full(len(Pl), -500.0)
    for sd in ("L", "R"):
        w_, e_ = H(f"wrist.{sd}"), H(f"lowerarm01.{sd}")
        a_ = _unit(w_ - e_)
        arm = np.array([b.endswith(sd) and b.startswith(("upperarm", "lowerarm", "wrist", "metacarpal", "finger"))
                        for b in dl])
        f_g = np.where(arm, (Pl - w_) @ a_ + 55.0, f_g)
    glove, lower = _split(lower, f_g)
    # 4. the shoes, up to the ankle
    Pl = np.asarray(lower.points)
    dl = dom(lower.point_data["W"])
    leg = np.array([b.startswith(("upperleg", "lowerleg", "foot")) for b in dl])
    shoes, lower = _split(lower, np.where(leg, H("foot.L")[2] + 30.0 - Pl[:, 2], -500.0))
    # 5. the coat (trunk and arms) and the trousers (hips and legs): the cut is under the coat's skirt
    dl = dom(lower.point_data["W"])
    coat, trousers = _split(lower, np.where(np.array([b.startswith(TROUSER_BONES) for b in dl]), -1.0, 1.0))
    # the skirt: MakeHuman's skirt helper, cut level at mid-thigh
    ts = m["tris"]["helper-skirt"]
    sv, sinv = np.unique(ts, return_inverse=True)
    skirt = _poly(V[sv], sinv.reshape(-1, 3), Wd[sv])
    hip, knee = H("upperleg01.L")[2], H("lowerleg01.L")[2]
    cut = knee + 0.45 * (hip - knee)
    skirt, _ = _split(skirt, np.asarray(skirt.points)[:, 2] - cut)
    # drape the coat's trunk and the skirt together, then smooth and push out
    # the skirt hangs more from the pelvis than it follows each thigh
    Ws = np.asarray(skirt.point_data["W"], float)
    Ws = 0.55 * Ws
    Ws[:, order.index("root")] += 0.45
    skirt.point_data["W"] = Ws.astype(np.float32)
    # the coat's torso ends 10 mm under the skirt's top edge, so the skirt is the outside surface below it (round 11's
    # first try had the torso's lower edge show through the skirt at the small of the back)
    Pk0 = np.asarray(skirt.points, float)
    ek = np.sort(np.r_[_faces(skirt)[:, [0, 1]], _faces(skirt)[:, [1, 2]], _faces(skirt)[:, [2, 0]]], axis=1)
    uk, ck = np.unique(ek, axis=0, return_counts=True)
    bk = np.unique(uk[ck == 1])
    top_edge = Pk0[bk][Pk0[bk][:, 2] > cut + 50.0]
    skirt_top = float(top_edge[:, 2].min()) if len(top_edge) else float(Pk0[:, 2].max())
    dcoat = dom(coat.point_data["W"])
    is_trunk = np.array([b.startswith(TRUNK_BONES) for b in dcoat])
    coat, _ = _split(coat, np.where(is_trunk, np.asarray(coat.points)[:, 2] - (skirt_top - 10.0), 1.0))
    coat = _offset(coat, 0.0, smooth=40)
    Pc, Pk = np.asarray(coat.points, float), np.asarray(skirt.points, float)
    trunk = np.array([b.startswith(TRUNK_BONES) for b in dom(coat.point_data["W"])])
    waist = np.abs(Pc[:, 2] - H("spine03")[2]) < 40.0
    axis = np.array([0.0, float(Pc[trunk & waist, 1].mean()) if (trunk & waist).any() else 0.0])
    chest = trunk & (Pc[:, 2] < H("neck01")[2] - 20.0) & (np.abs(Pc[:, 0]) < 175.0)
    Pc = _bridge(Pc, chest & (Pc[:, 1] > axis[1] + 15.0), 1.0)
    Pc = _bridge(Pc, chest & (Pc[:, 1] < axis[1] - 15.0), -1.0)
    both = np.r_[Pc, Pk]
    hang = np.r_[trunk, np.ones(len(Pk), bool)]
    both = _vbridge(both, hang & (both[:, 2] < H("neck01")[2] - 45.0), axis)
    zt = H("spine01")[2] - 10.0
    dr = _drape(both, hang, axis, zt)
    coat.points, skirt.points = dr[:len(Pc)], dr[len(Pc):]
    Pt = np.asarray(trousers.points, float)
    dt = dom(trousers.point_data["W"])
    for sd in ("L", "R"):
        Pt = _leg_drape(Pt, np.array([x_.startswith("lowerleg") and x_.endswith(sd) for x_ in dt]),
                        H(f"lowerleg01.{sd}") + (0, 0, 40.0), H(f"foot.{sd}"))
    trousers.points = Pt
    parts = dict(
        skin=skin, hair=hair, brow=_offset(brow, OFFSET["brow"]),
        shirt=_offset(shirt, OFFSET["shirt"]), glove=_offset(glove, OFFSET["glove"]),
        shoes=_offset(shoes, OFFSET["shoes"], smooth=25), trousers=_offset(trousers, OFFSET["trousers"], smooth=24),
        coat=_offset(coat, OFFSET["coat"], smooth=30), skirt=_offset(skirt, OFFSET["skirt"], smooth=20))
    # eyes: the iris where the eyeball faces forward
    for sd in ("l", "r"):
        te = m["tris"][f"helper-{sd}-eye"]
        ev, einv = np.unique(te, return_inverse=True)
        eyem = _poly(V[ev], einv.reshape(-1, 3), Wd[ev])
        c = V[ev].mean(0)
        dv = np.asarray(eyem.points) - c
        fwd = dv[:, 1] / np.maximum(np.linalg.norm(dv, axis=1), 1e-9)
        iris, sclera = _split(eyem, fwd - 0.80)
        for k_, part in (("iris", iris), ("sclera", sclera)):
            parts[k_] = part if k_ not in parts else parts[k_].merge(part)
    out = {}
    for k_, part in parts.items():
        F = _faces(part)
        W = np.asarray(part.point_data["W"], float)
        r_, c_ = np.nonzero(W > 1e-4)
        v_ = W[r_, c_]
        v_ = v_ / np.bincount(r_, weights=v_, minlength=len(W))[r_]
        out[k_] = dict(P=np.asarray(part.points, float), F=F, rows=r_, cols=c_, vals=v_)
    out["collar"] = _collar(out["coat"], H)
    return dict(parts=out, glasses=_glasses(m), skirt_cut=cut)


def _collar(coat: dict, H) -> dict | None:
    """The coat's collar along its neck opening: standing 30 mm at the back, lying out as lapels along the V."""
    P, F = coat["P"], coat["F"]
    e = np.sort(np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]], axis=1)
    u, c = np.unique(e, axis=0, return_counts=True)
    b = u[c == 1]
    n0 = H("neck01")
    keep = (P[b[:, 0], 2] > H("spine01")[2] - 20.0) & (np.abs(P[b[:, 0], 0]) < 140.0) & \
        (P[b[:, 1], 2] > H("spine01")[2] - 20.0)
    b = b[keep]
    if len(b) < 8:
        return None
    adj = {}
    for i, j in b:
        adj.setdefault(i, []).append(j)
        adj.setdefault(j, []).append(i)
    start = max(adj, key=lambda v: -P[v, 1])                # at the back
    loop, prev, cur = [start], None, start
    while True:
        nxt = [w for w in adj[cur] if w != prev and w not in loop[1:]]
        if not nxt:
            break
        prev, cur = cur, nxt[0]
        if cur == start:
            break
        loop.append(cur)
    if len(loop) < 8:
        return None
    loop = np.array(loop)
    P0 = P[loop]
    for _ in range(3):                                   # smooth the edge along the loop (a moving average)
        P0 = (np.roll(P0, 2, 0) + np.roll(P0, 1, 0) + P0 + np.roll(P0, -1, 0) + np.roll(P0, -2, 0)) / 5.0
    front = np.clip((P0[:, 1] - (n0[1] - 5.0)) / 45.0, 0.0, 1.0)
    out = P0[:, :2] - np.array([0.0, n0[1]])
    out = np.c_[out / np.maximum(np.linalg.norm(out, axis=1), 1e-9)[:, None], np.zeros(len(P0))]
    side = np.c_[np.sign(P0[:, 0]), np.zeros(len(P0)), np.zeros(len(P0))]
    up = np.array([0.0, 0.0, 1.0])
    stand = (1.0 - front)[:, None]
    lap = front[:, None]
    r1 = P0 + stand * (up * 16.0 + out * 4.0) + lap * (side * 12.0 + np.array([0, 4.0, 2.0]))
    r2 = P0 + stand * (up * 30.0 + out * 14.0) + lap * (side * 30.0 + np.array([0, 7.0, -6.0]))
    rings = [P0, r1, r2]
    n = len(loop)
    pts = np.concatenate(rings)
    faces = []
    for r in range(len(rings) - 1):
        for i in range(n):
            a, b2 = r * n + i, r * n + (i + 1) % n
            faces += [(a, b2, b2 + n), (a, b2 + n, a + n)]
    rows, cols, vals = coat["rows"], coat["cols"], coat["vals"]
    o = np.argsort(rows, kind="stable")
    rs, cs, vs = rows[o], cols[o], vals[o]
    s0, s1 = np.searchsorted(rs, loop), np.searchsorted(rs, loop, side="right")
    R_, C_, W_ = [], [], []
    for r in range(len(rings)):
        for i, (a0, a1) in enumerate(zip(s0, s1)):
            R_ += [r * n + i] * (a1 - a0)
            C_ += list(cs[a0:a1])
            W_ += list(vs[a0:a1])
    return dict(P=pts, F=np.array(faces), rows=np.array(R_), cols=np.array(C_), vals=np.array(W_))


def _glasses(m: dict) -> dict:
    """Wrap-around safety glasses on the rest head: {piece: (points, faces)}; they ride on the head bone."""
    el, er = m["eyes"]["l"], m["eyes"]["r"]
    c = (el + er) / 2
    half = abs(el[0] - er[0]) / 2
    cx, cy, cz = c[0], c[1] - 70.0, c[2]                 # the arc's axis, behind the eyes
    rad = (c[1] + 24.0) - cy                             # the lens 24 mm in front of the eyes' centres
    phis = np.radians(np.linspace(-66, 66, 41))
    zs = np.array([-21.0, -14.0, 0.0, 12.0, 17.0])
    pts, faces = [], []
    for z in zs:
        for ph in phis:
            sag = 1.0 - 0.10 * (z / 20.0) ** 2
            pts.append((cx + rad * math.sin(ph), cy + rad * math.cos(ph) * sag, cz + z - 3.0 * math.cos(2 * ph)))
    n = len(phis)
    for i in range(len(zs) - 1):
        for j in range(n - 1):
            a = i * n + j
            faces += [(a, a + 1, a + n + 1), (a, a + n + 1, a + n)]
    lens = (np.array(pts), np.array(faces))
    fr = []
    top = np.array(pts[(len(zs) - 1) * n:(len(zs)) * n])
    for j in range(n - 1):
        a, b = top[j], top[j + 1]
        d = b - a
        fr.append(pv.Cylinder(center=(a + b) / 2, direction=d, radius=3.0, height=float(np.linalg.norm(d)) + 1.5,
                              resolution=10).triangulate())
    for sgn in (-1, 1):
        p0 = np.array([cx + sgn * rad * math.sin(math.radians(66)), cy + rad * math.cos(math.radians(66)), cz + 8.0])
        p1 = np.array([cx + sgn * (half + 46.0), c[1] - 108.0, cz - 2.0])
        d = p1 - p0
        fr.append(pv.Cylinder(center=(p0 + p1) / 2, direction=d, radius=2.6, height=float(np.linalg.norm(d)),
                              resolution=10).triangulate())
    frame = fr[0].merge(fr[1:]).clean()
    ff = np.asarray(frame.faces).reshape(-1, 4)[:, 1:]
    return dict(lens=lens, frame=(np.asarray(frame.points, float), ff))


# ================================================================================================ maths
def _rot(axis, ang: float) -> np.ndarray:
    a = np.asarray(axis, float)
    a = a / max(np.linalg.norm(a), 1e-12)
    x, y, z = a
    c, s = math.cos(ang), math.sin(ang)
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def _unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    return v / max(np.linalg.norm(v), 1e-12)


def _M(Rm=None, t=None) -> np.ndarray:
    M = np.eye(4)
    if Rm is not None:
        M[:3, :3] = Rm
    if t is not None:
        M[:3, 3] = t
    return M


def _normals(P: np.ndarray, F: np.ndarray, n: int) -> np.ndarray:
    a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    fn = np.cross(b - a, c - a)
    out = np.zeros((n, 3))
    for k in range(3):
        for j in range(3):
            out[:, j] += np.bincount(F[:, k], weights=fn[:, j], minlength=n)
    return out / np.maximum(np.linalg.norm(out, axis=1), 1e-12)[:, None]


# ================================================================================================ the person
class Person:
    """A person, 1.75 m, in a lab coat: one skinned body posed every frame (see the module's docstring). Its local
    frame: x to its right, y the way it faces, z up, the origin on the floor between its feet; ``set(x, y, hd)``
    puts that frame in the world (hd in degrees about z, 0 = facing +y)."""

    LEAN_HIPS = 0.6                     # of a lean, the share taken at the hips (the rest along the lower spine)
    STRIDE = 1016.0                     # mm per gait cycle

    def __init__(self, sc, name="person", coat=COAT, skin=SKIN, hair=HAIR, trousers=TROUSERS):
        self.sc, self.n = sc, name
        m = self.m = model()
        self.order = m["order"]
        self.bi = {b: i for i, b in enumerate(self.order)}
        self.group = f"{name}_body"
        colours = dict(skin=skin, coat=coat, skirt=coat, collar=coat, shirt=SHIRT, glove=GLOVE, shoes=SHOES,
                       trousers=trousers, hair=hair, brow=BROW, iris=IRIS, sclera=SCLERA)
        spec = dict(coat=0.08, skirt=0.08, collar=0.08, glove=0.35, shoes=0.3, hair=0.05, skin=0.12, iris=0.6,
                    sclera=0.4)
        self.parts = {}                                  # part -> (its data, PolyData)
        for part, d in m["parts"].items():
            if d is None or not len(d["F"]):
                continue
            poly = _poly(d["P"], d["F"])
            poly.point_data["Normals"] = np.zeros((len(d["P"]), 3))
            poly.point_data.active_normals_name = "Normals"
            nm = f"{name}/{'coat ' if part in ('skirt', 'collar') else ''}{part}"
            sc.add(nm, poly, colours[part], self.group, specular=spec.get(part, 0.1), split_sharp_edges=False)
            sc.set_mesh(nm, poly)
            self.parts[part] = (d, poly)
        self.rigid = {}                                  # pieces that ride on the head: the glasses
        for piece, (P, F) in m["glasses"].items():
            poly = _poly(P, F)
            nm = f"{name}/glasses {piece}"
            if piece == "lens":
                sc.add(nm, poly, LENS, self.group, opacity=0.38, specular=0.9, split_sharp_edges=False)
            else:
                sc.add(nm, poly, FRAME, self.group, specular=0.5)
            sc.set_mesh(nm, poly)
            self.rigid[piece] = (P, poly)
        self.hand_groups = {s: f"{name}_hand_{s}" for s in ("l", "r")}
        self.groups = [self.group, *self.hand_groups.values()]
        self.held = {}                                   # side -> (group, offset from the hand's frame)
        self.st = dict(x=0.0, y=0.0, hd=0.0, lean=0.0, phase=0.0, amp=0.0, hands={"l": None, "r": None}, look=None,
                       grip={"l": 0.3, "r": 0.3})
        self._rest_arm()
        self.set()

    # ------------------------------------------------------------------------------------------- set-up
    def H(self, b) -> np.ndarray:
        return self.m["head"][self.bi[b]]

    def T(self, b) -> np.ndarray:
        return self.m["tail"][self.bi[b]]

    def _rest_arm(self):
        """The rest arm's geometry for the IK (the upper arm, the elbow to the palm's centre, the flexion axis) and
        the fingers' rest directions."""
        self.arm = {}
        for s, side in (("l", "L"), ("r", "R")):
            Sh, El, Wr = self.H(f"upperarm01.{side}"), self.H(f"lowerarm01.{side}"), self.H(f"wrist.{side}")
            k1, k2 = self.H(f"finger2-1.{side}"), self.H(f"finger5-1.{side}")
            palm_n = -_unit(np.cross(k1 - Wr, k2 - Wr))
            base, tip = self.H(f"finger3-1.{side}"), self.T(f"finger3-3.{side}")
            dm = _unit(base - self.H(f"metacarpal2.{side}"))
            if (tip - (base + dm * np.linalg.norm(tip - base))) @ palm_n < 0:
                palm_n = -palm_n
            palm = Wr + 0.55 * ((k1 + k2) / 2 - Wr) + 12.0 * palm_n
            a0 = _unit(El - Sh)
            f0 = _unit(palm - El)
            k0 = _unit(np.cross(a0, f0))
            mid = _unit(self.T(f"finger3-1.{side}") - self.H(f"finger3-1.{side}"))
            close = {}
            for fi in (2, 4, 5):
                d = _unit(self.T(f"finger{fi}-1.{side}") - self.H(f"finger{fi}-1.{side}"))
                ang = math.acos(float(np.clip(d @ mid, -1, 1)))
                close[fi] = _rot(np.cross(d, mid), 0.8 * ang) if ang > 1e-3 else np.eye(3)
            self.arm[s] = dict(side=side, L1=float(np.linalg.norm(El - Sh)), L2=float(np.linalg.norm(palm - El)),
                               a0=a0, f0=f0, k0=k0, e0=math.acos(float(np.clip(a0 @ f0, -1, 1))), palm=palm,
                               palm_n=palm_n, close=close, fw=_unit(Wr - self.H(f"lowerarm02.{side}")))

    # ------------------------------------------------------------------------------------------- the API
    def names(self):
        return [n for n, g in self.sc.group_of.items() if g in self.groups]

    def show(self, a):
        for n in self.names():
            self.sc.alpha[n] = a

    def frame(self) -> np.ndarray:
        s = self.st
        c, si = math.cos(math.radians(s["hd"])), math.sin(math.radians(s["hd"]))
        return _M(np.array([[c, -si, 0], [si, c, 0], [0, 0, 1.0]]), (s["x"], s["y"], 0.0))

    def rest_hand(self, side) -> np.ndarray:
        """Where a hand hangs (world): at the side, a little forward, swinging against the legs when walking."""
        s = self.st
        sx = -1.0 if side == "l" else 1.0
        swing = sx * 115.0 * s["amp"] * math.sin(s["phase"])
        a = self.arm[side]
        sh = self.H(f"upperarm01.{a['side']}")
        local = np.r_[sx * (abs(sh[0]) + 40.0), 45.0 + swing,
                      sh[2] - a["L1"] - a["L2"] + 18.0 + 0.25 * abs(swing), 1.0]
        return (self.frame() @ local)[:3]

    def set(self, **kw):
        s = self.st
        for k, v in kw.items():
            if k in ("hands", "grip"):
                s[k] = dict(s[k], **v)
            else:
                s[k] = v
        self._pose()

    def hold(self, side, group):
        """Carry Scene group `group` in a hand from now on (as it is now, relative to the hand)."""
        sc = self.sc
        Mw = sc.world(group)
        Mh = sc.gmat[self.hand_groups[side]]
        self.held[side] = (group, np.linalg.inv(Mh) @ Mw)

    def let_go(self, side, parent=None):
        sc = self.sc
        grp, _ = self.held.pop(side)
        Mw = sc.world(grp)
        if parent is None:
            sc.parent.pop(grp, None)
            sc.gmat[grp] = Mw
        else:
            sc.parent[grp] = parent
            sc.gmat[grp] = np.linalg.inv(sc.world(parent)) @ Mw

    def hand_point(self, side) -> np.ndarray:
        """The palm's centre now (world)."""
        return (self.sc.gmat[self.hand_groups[side]] @ np.r_[self.arm[side]["palm"], 1.0])[:3]

    # ------------------------------------------------------------------------------------------- posing
    def _chain(self, Q: dict, root: np.ndarray) -> np.ndarray:
        """Skinning transforms (nb, 4, 4): each bone's rotation Q (in the rest frame, about its rest head)
        composed down the chain from the root's transform."""
        S = np.empty((len(self.order), 4, 4))
        heads = self.m["head"]
        for i, b in enumerate(self.order):
            p = self.m["parent"][i]
            base = root if p < 0 else S[p]
            q = Q.get(b)
            if q is None:
                S[i] = base
            else:
                h = heads[i]
                L = np.eye(4)
                L[:3, :3] = q
                L[:3, 3] = h - q @ h
                S[i] = base @ L
        return S

    def _pose(self):
        s = self.st
        Q = {}
        ph, amp = s["phase"], s["amp"]
        lean = math.radians(s["lean"])
        # the legs: stood naturally (MakeHuman's rest stance is wide), then the gait
        thetas = {}
        for side, sx, off in (("L", -1.0, 0.0), ("R", 1.0, math.pi)):
            p = ph + off
            th = amp * math.radians(21.0) * math.sin(p)
            kn = amp * (math.radians(58.0) * max(0.0, math.cos(p - 0.35)) ** 1.6 + math.radians(6.0))
            thetas[side] = (th, kn)
            Q[f"upperleg01.{side}"] = _rot((1, 0, 0), th + self.LEAN_HIPS * lean) @ _rot((0, 1, 0), sx * math.radians(7.0))
            Q[f"lowerleg01.{side}"] = _rot((1, 0, 0), -kn) @ _rot((0, 1, 0), sx * math.radians(2.0))
            Q[f"foot.{side}"] = _rot((1, 0, 0), -0.75 * (th - kn))
        # the pelvis: the lean's share at the hips, about the hip joints; the walk's bob
        hips = (self.H("upperleg01.L") + self.H("upperleg01.R")) / 2
        leg = float(hips[2] - SOLE)
        drop = 0.0
        if amp > 0:
            spread = max(abs(thetas["L"][0]), abs(thetas["R"][0]))
            drop = 0.75 * leg * (1.0 - math.cos(spread)) + 8.0 * amp
        Rr = _rot((1, 0, 0), -self.LEAN_HIPS * lean) @ _rot((0, 0, 1), 0.06 * amp * math.sin(ph))
        root = _M(Rr, hips - Rr @ hips + np.array([0.0, 0.0, -drop]))
        rest = (1.0 - self.LEAN_HIPS) * lean
        for b in ("spine05", "spine04", "spine03", "spine02"):
            Q[b] = _rot((1, 0, 0), -rest / 4)
        Q["spine01"] = _rot((0, 0, 1), -0.08 * amp * math.sin(ph))
        # the head: towards what it looks at, or ahead
        S = self._chain(Q, root)
        look = s["look"]
        yaw = pitch = 0.0
        F = self.frame()
        Finv = np.linalg.inv(F)
        if look is not None:
            loc = Finv @ np.r_[np.asarray(look, float), 1.0]
            hpos = (S[self.bi["head"]] @ np.r_[self.H("head") + (0, 60.0, 40.0), 1.0])[:3]
            d = loc[:3] - hpos
            yaw = float(np.clip(math.atan2(-d[0], max(d[1], 1e-6)), -1.2, 1.2))
            down = math.atan2(-d[2], math.hypot(d[0], d[1]))
            pitch = float(np.clip(down - lean, math.radians(-25), math.radians(45)))
        elif lean > 0:
            pitch = -0.35 * lean
        for b, k in (("neck01", 0.3), ("neck03", 0.25), ("head", 0.45)):
            Q[b] = _rot((0, 0, 1), k * yaw) @ _rot((1, 0, 0), -k * pitch)
        S = self._chain(Q, root)
        # the arms: two-bone IK from the posed shoulder to each palm target
        for side in ("l", "r"):
            a = self.arm[side]
            sd = a["side"]
            tgt = s["hands"][side]
            Hw = self.rest_hand(side) if tgt is None else np.asarray(tgt, float)
            Hl = (Finv @ np.r_[Hw, 1.0])[:3]
            Sh = (S[self.bi[f"shoulder01.{sd}"]] @ np.r_[self.H(f"upperarm01.{sd}"), 1.0])[:3]
            d = Hl - Sh
            L = float(np.linalg.norm(d))
            L1, L2 = a["L1"], a["L2"]
            L = min(max(L, abs(L1 - L2) + 5.0), L1 + L2 - 2.0)
            du = _unit(d)
            sx = -1.0 if side == "l" else 1.0
            pole = np.array([sx * 0.75, -0.30, -1.0])
            v = pole - (pole @ du) * du
            if np.linalg.norm(v) < 1e-6:
                v = np.array([sx, 0.0, 0.0]) - du[0] * sx * du
            v = _unit(v)
            p = (L1 * L1 - L2 * L2 + L * L) / (2 * L)
            q = math.sqrt(max(L1 * L1 - p * p, 0.0))
            E = Sh + p * du + q * v
            Ht = Sh + du * L
            au = _unit(E - Sh)
            fu = _unit(Ht - E)
            k = _unit(np.cross(v, du))
            eps = math.acos(float(np.clip(au @ fu, -1, 1)))
            Rw = np.c_[au, k, np.cross(au, k)] @ np.c_[a["a0"], a["k0"], np.cross(a["a0"], a["k0"])].T
            P = S[self.bi[f"shoulder01.{sd}"]][:3, :3]
            Q[f"upperarm01.{sd}"] = P.T @ Rw
            Q[f"lowerarm01.{sd}"] = _rot(a["k0"], eps - a["e0"])
            # the forearm's turn: palms down to a bar in front, towards the thighs when hanging
            reach = 0.0 if tgt is None else float(np.clip((Hl[2] - (Sh[2] - L1 - L2 + 120.0)) / 380.0, 0.0, 1.0))
            Q[f"lowerarm02.{sd}"] = _rot(a["fw"], -sx * math.radians(-15.0 + 70.0 * reach))
            # the fingers: together, curled a little, more when holding
            g = s["grip"][side] if side not in self.held else 0.8
            for fi in range(2, 6):
                for j, w in ((1, 0.8), (2, 1.0), (3, 0.75)):
                    b = f"finger{fi}-{j}.{sd}"
                    ax = _unit(np.cross(_unit(self.T(b) - self.H(b)), a["palm_n"]))
                    R_ = _rot(ax, math.radians(70.0) * g * w)
                    Q[b] = R_ @ a["close"][fi] if (j == 1 and fi in a["close"]) else R_
            for j in (2, 3):
                b = f"finger1-{j}.{sd}"
                ax = _unit(np.cross(_unit(self.T(b) - self.H(b)), a["palm_n"]))
                Q[b] = _rot(ax, math.radians(35.0) * g)
        S = self._chain(Q, root)
        self.S = S
        # the hands' frames (world), for what they hold
        for side in ("l", "r"):
            Mh = F @ S[self.bi[f"wrist.{self.arm[side]['side']}"]]
            self.sc.gmat[self.hand_groups[side]] = Mh
            if side in self.held:
                grp, off = self.held[side]
                self.sc.gmat[grp] = Mh @ off
                self.sc.parent.pop(grp, None)
        self._skin(S)
        self.sc.gmat[self.group] = F

    def _skin(self, S):
        for part, (d, poly) in self.parts.items():
            P0, rows, cols, vals = d["P"], d["rows"], d["cols"], d["vals"]
            Pk = np.einsum("kij,kj->ki", S[cols, :3, :3], P0[rows]) + S[cols, :3, 3]
            n = len(P0)
            P = np.empty((n, 3))
            for j in range(3):
                P[:, j] = np.bincount(rows, weights=vals * Pk[:, j], minlength=n)
            poly.points = P
            poly.point_data["Normals"] = _normals(P, d["F"], n)
            poly.point_data.active_normals_name = "Normals"
        Mh = S[self.bi["head"]]
        for piece, (P0, poly) in self.rigid.items():
            poly.points = P0 @ Mh[:3, :3].T + Mh[:3, 3]

    def posed(self) -> dict:
        """{actor name: (points (n, 3) in the world, faces (m, 3))} as posed now: for collision checks."""
        F = self.sc.gmat[self.group]
        out = {}
        for part, (d, poly) in self.parts.items():
            P = np.asarray(poly.points, float)
            out[part] = (P @ F[:3, :3].T + F[:3, 3], d["F"])
        return out


# ================================================================================================ a look at it
def _preview():
    """Close-up stills: standing, mid-stride, pushing a table, leaning in to reach, from the front and the side."""
    from scene import Scene
    import scene as S_
    out = Path("/tmp")
    poses = {
        "stand": dict(lean=0.0, amp=0.0, phase=0.0, hands={"l": None, "r": None}, look=None),
        "walk": dict(lean=0.0, amp=1.0, phase=0.6 * math.pi, hands={"l": None, "r": None}, look=None),
        "push": dict(lean=20.0, amp=0.8, phase=1.1, hands={"l": (-215.0, 236.0, 849.0), "r": (215.0, 236.0, 849.0)},
                     look=None),
        "reach": dict(lean=30.0, amp=0.0, phase=0.0, hands={"l": (-120.0, 560.0, 1090.0), "r": (40.0, 620.0, 1010.0)},
                      look=(40.0, 700.0, 1000.0)),
    }
    cams = {"front": [(1500, 2600, 1500), (0, 0, 950), (0, 0, 1)], "side": [(2900, 300, 1400), (0, 150, 950), (0, 0, 1)],
            "back": [(-1300, -2600, 1700), (0, 0, 950), (0, 0, 1)], "face": [(250, 900, 1620), (0, 0, 1560), (0, 0, 1)]}
    S_.PREVIEW = True
    sc = Scene("people_preview", "", size=(900, 900), gif=False, mp4=False)
    sc.add("floor", pv.Plane(center=(0, 0, -1), i_size=4000, j_size=4000), (0.85, 0.86, 0.86), specular=0.0)
    p = Person(sc, "p")
    imgs = []
    for nm, kw in poses.items():
        p.set(**kw)
        row = []
        for cn, cam in cams.items():
            sc.cam = cam
            sc.view_angle = 30.0 if cn != "face" else 26.0
            row.append(sc.render_base())
        strip = np.concatenate(row, axis=1)
        pv.wrap(strip)
        from PIL import Image
        Image.fromarray(strip).save(out / f"people_{nm}.png")
        imgs.append(out / f"people_{nm}.png")
    print("\n".join(str(i) for i in imgs))


if __name__ == "__main__":
    _preview()

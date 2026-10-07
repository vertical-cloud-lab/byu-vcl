"""Interference check for the step animations: do parts pass through each other?

Replays every animation in steps.py without rendering. Each frame records where every part is and whether it is
shown; any two shown parts that have moved relative to each other since the assembled machine are then tested for
penetration: dense samples on each part's surface are checked against the other part's signed distance. A pair that
overlaps by more than TOL mm is reported, by sub-step and frame range, with its depth. The assembled machine itself is
checked first, for parts that overlap where they stand.

    xvfb-run -a python collide.py                    # every animation; writes out/collisions.md and .json
    xvfb-run -a python collide.py 03_furnace_load    # one (or several)

Only solid parts are checked: particles, the melt, powder, gas and flow dots are not. Pairs that are meant to touch
or nest (a part sliding in a bore with clearance, a nut on its thread) pass as long as they do not overlap by more than
TOL. Hidden parts are ignored: a part is present while its alpha is above 0.02, as in the renderer.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pyvista as pv
import vtk
from vtk.util import numpy_support as ns

import model as M
import scene as SC

HERE = Path(__file__).resolve().parent
TOL = 1.5                     # mm of overlap tolerated (tessellation error is up to ~0.5 mm a side)
DENSITY = 0.6                 # surface samples per mm^2
MAX_SAMPLES = 250_000
SKIP = {"floor"}              # the floor is checked separately: nothing may go below z = 0


# --------------------------------------------------------------------------- recording (no rendering)
_orig_init = SC.Scene.__init__


def _init(self, name, title, size=SC.SIZE, gif=True, mp4=True):
    _orig_init(self, name, title, size, gif=False, mp4=False)
    self.rec = []


def _snap(self, n=1):
    parts = {}
    for a, g in self.group_of.items():
        p = a.split("#")[0]
        if p.startswith(("w:", "h:")):
            p = p[2:]
        if p not in MESHES:
            continue
        al = self.alpha.get(a, 0.0)
        if p in parts:
            parts[p] = (parts[p][0], max(parts[p][1], al))
        else:
            parts[p] = (g, al)
    cache = {}
    state = {}
    for p, (g, al) in parts.items():
        if al <= 0.02:
            continue
        if g not in cache:
            cache[g] = self.world(g)
        state[p] = cache[g]
    self.rec.append(dict(frame=self.n, n=n, label=self.label, state=state))
    self.n += n


def _save(self):
    self.pl.close()
    RECORDS[self.name] = dict(rec=self.rec, substeps=self.substeps)
    return self.name


SC.Scene.__init__ = _init
SC.Scene.snap = _snap
SC.Scene.save = _save
RECORDS: dict = {}
MESHES = M.meshes()


# ------------------------------------------------------------------------------ geometry per part
class Body:
    def __init__(self, name, shape, tol):
        # tessellate the whole solid at once, so faces share their edge points and the mesh closes up after merging:
        # the per-face render meshes leave slits along cut edges, which flip the sign of the distance near them
        verts, tris = shape.tessellate(min(tol, 0.5), 0.2)
        pts = np.array([(v.x, v.y, v.z) for v in verts], float)
        faces = np.hstack([[3, *t] for t in tris]).astype(np.int64)
        m = pv.PolyData(pts, faces).clean(tolerance=1e-4).triangulate()
        self.name = name
        self.pts = np.asarray(m.points, float)
        tri = m.faces.reshape(-1, 4)[:, 1:]
        self.lo, self.hi = self.pts.min(0), self.pts.max(0)
        self.mesh = m
        self.f = vtk.vtkImplicitPolyDataDistance()
        self.f.SetInput(m)
        # area-weighted random samples on the surface, plus every vertex
        a, b, c = self.pts[tri[:, 0]], self.pts[tri[:, 1]], self.pts[tri[:, 2]]
        area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
        n = int(min(MAX_SAMPLES, max(200, area.sum() * DENSITY)))
        rng = np.random.default_rng(abs(hash(name)) % 2**32)
        idx = rng.choice(len(tri), n, p=area / area.sum())
        u, v = rng.random(n), rng.random(n)
        flip = u + v > 1
        u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
        s = a[idx] + (b[idx] - a[idx]) * u[:, None] + (c[idx] - a[idx]) * v[:, None]
        self.samples = np.vstack([s, self.pts])

    def sdf(self, p):
        inp = ns.numpy_to_vtk(np.ascontiguousarray(p, dtype=np.float64), deep=True)
        out = vtk.vtkDoubleArray()
        out.SetNumberOfTuples(len(p))
        self.f.FunctionValue(inp, out)
        return ns.vtk_to_numpy(out).copy()


BODIES: dict[str, Body] = {}


SHAPES = {p.name: p for p in M.parts()}


def body(name) -> Body:
    if name not in BODIES:
        BODIES[name] = Body(name, SHAPES[name].shape, SHAPES[name].tol)
    return BODIES[name]


def corners(lo, hi):
    return np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])], float)


def xform(m, p):
    return p @ m[:3, :3].T + m[:3, 3]


def world_box(b: Body, m):
    c = xform(m, corners(b.lo, b.hi))
    return c.min(0), c.max(0)


def depth_into(a: Body, ma, b: Body, mb):
    """Deepest sample of a's surface inside b (mm, positive = overlap), with a at pose ma and b at mb."""
    rel = np.linalg.inv(mb) @ ma                    # a's local frame -> b's local frame
    # only a's samples that can reach b: b's box, in a's frame
    inv = np.linalg.inv(rel)
    c = xform(inv, corners(b.lo - TOL, b.hi + TOL))
    lo, hi = c.min(0), c.max(0)
    s = a.samples
    k = np.all((s >= lo) & (s <= hi), axis=1)
    if not k.any():
        return 0.0, None
    p = xform(rel, s[k])
    d = b.sdf(p)
    # the distance's sign comes from the nearest triangle's normal, which can point the wrong way at a sharp edge: confirm
    # every point that reads as inside by casting rays (vtkSelectEnclosedPoints), and flip the ones that are not
    cand = np.flatnonzero(d < -TOL)
    if len(cand):
        sel = pv.PolyData(p[cand]).select_enclosed_points(b.mesh, check_surface=False)
        inside = np.asarray(sel.point_data["SelectedPoints"]).astype(bool)
        d[cand[~inside]] = np.abs(d[cand[~inside]])
    i = int(np.argmin(d))
    return float(-d[i]), xform(mb, p[i:i + 1])[0]


def pair_depth(na, ma, nb, mb):
    a, b = body(na), body(nb)
    d1, p1 = depth_into(a, ma, b, mb)
    d2, p2 = depth_into(b, mb, a, ma)
    return (d1, p1) if d1 >= d2 else (d2, p2)


def same(m1, m2):
    return np.allclose(m1, m2, atol=1e-6)


# ------------------------------------------------------------------------------------- checking
def check_rest():
    """Parts that overlap in the assembled machine (every part at home)."""
    names = [n for n in MESHES if n not in SKIP]
    boxes = {n: (body(n).lo, body(n).hi) for n in names}
    out = []
    eye = np.eye(4)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            (la, ha), (lb, hb) = boxes[a], boxes[b]
            if np.any(la > hb + TOL) or np.any(lb > ha + TOL):
                continue
            d, p = pair_depth(a, eye, b, eye)
            if d > TOL:
                out.append(dict(a=a, b=b, depth=round(d, 1), at=[round(float(x)) for x in p]))
    return out


def check_anim(name):
    import steps
    t = time.time()
    steps.ANIMS[name]()
    rec = RECORDS[name]["rec"]
    events = {}               # (a, b) -> list of (frame, n, label, depth, point)
    below = {}
    prev = None
    for r in rec:
        st = r["state"]
        if prev is not None and st.keys() == prev.keys() and all(same(st[k], prev[k]) for k in st):
            continue           # nothing moved or appeared since the last checked frame
        prev = st
        names = [n for n in st if n not in SKIP]
        boxes = {n: world_box(body(n), st[n]) for n in names}
        for n in names:
            if boxes[n][0][2] < -TOL:
                below.setdefault(n, []).append((r["frame"], r["label"], round(float(boxes[n][0][2]), 1)))
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                ma, mb = st[a], st[b]
                if same(np.linalg.inv(ma) @ mb, np.eye(4)):
                    continue   # as assembled relative to each other: checked by check_rest()
                (la, ha), (lb, hb) = boxes[a], boxes[b]
                if np.any(la > hb + TOL) or np.any(lb > ha + TOL):
                    continue
                d, p = pair_depth(a, ma, b, mb)
                if d > TOL:
                    events.setdefault((a, b), []).append((r["frame"], r["n"], r["label"], d, p))
    # group each pair's frames into runs per sub-step
    out = []
    for (a, b), ev in events.items():
        run = None
        for f, n, lab, d, p in ev:
            if run and run["label"] == lab and f <= run["f1"] + 3:
                run["f1"] = f + n - 1
                if d > run["depth"]:
                    run.update(depth=d, at=p)
            else:
                if run:
                    out.append(run)
                run = dict(a=a, b=b, label=lab, f0=f, f1=f + n - 1, depth=d, at=p)
        out.append(run)
    for r in out:
        r["depth"] = round(float(r["depth"]), 1)
        r["at"] = [round(float(x)) for x in r["at"]]
    out.sort(key=lambda r: (r["f0"], r["a"], r["b"]))
    floor = [dict(part=n, label=v[0][1], frame=v[0][0], z=min(x[2] for x in v)) for n, v in below.items()]
    print(f"{name}: {len(rec)} frames recorded, {len(out)} interference runs, {len(floor)} below the floor "
          f"({time.time() - t:.0f} s)", flush=True)
    return dict(events=out, below_floor=floor, substeps=RECORDS[name]["substeps"])


def report(rest, results):
    lines = ["# Interference check", "",
             f"Generated by `collide.py`: every animation replayed frame by frame; pairs of shown parts that overlap by "
             f"more than {TOL} mm while moving relative to each other. Depth is the deepest overlap in the run, "
             f"`at` the world point (mm) where it occurs. Frames are MP4 frames at {SC.FPS} fps.", ""]
    lines += ["## Assembled machine", "",
              "Parts that overlap where they stand: these are mounted on or into each other (a flange set into its wall, "
              "a plug in the deck, a knob on the lid, a pin in its clevis), not motion. Pairs listed here are not "
              "re-checked while they stay put relative to each other.", ""]
    if rest:
        lines += ["| Part | Part | Overlap (mm) | At |", "| --- | --- | ---: | --- |"]
        lines += [f"| {r['a']} | {r['b']} | {r['depth']} | {r['at']} |" for r in rest]
    else:
        lines += ["No overlaps."]
    for name, res in results.items():
        lines += ["", f"## {name}", ""]
        if not res["events"] and not res["below_floor"]:
            lines += ["No interference."]
            continue
        if res["events"]:
            lines += ["| Sub-step | Frames | Moving part | Other part | Overlap (mm) | At |",
                      "| --- | --- | --- | --- | ---: | --- |"]
            lines += [f"| {r['label']} | {r['f0']}–{r['f1']} | {r['a']} | {r['b']} | {r['depth']} | {r['at']} |"
                      for r in res["events"]]
        for r in res["below_floor"]:
            lines += [f"- `{r['part']}` goes below the floor in {r['label']} (lowest point z = {r['z']} mm)."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import steps
    names = sys.argv[1:] or steps.DEFAULT
    out = HERE / "out"
    rest = check_rest()
    print(f"assembled machine: {len(rest)} overlaps", flush=True)
    results = {n: check_anim(n) for n in names}
    suffix = "" if not sys.argv[1:] else "_" + "_".join(names)
    (out / f"collisions{suffix}.json").write_text(json.dumps(dict(rest=rest, anims=results), indent=1) + "\n")
    (out / f"collisions{suffix}.md").write_text(report(rest, results))
    print("wrote", out / f"collisions{suffix}.md")

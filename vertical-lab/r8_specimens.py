"""The two specimens that pass from sample prep (chapter 6, ``alloy_prep.py``) to characterization (chapter 7) (#303).

Owned by the prep stream. Others import it; please don't edit it (ask the prep stream). The names below are stable.

**1.5 in, not 1.25 in.** The lab's own LECO MX400 reads "Mold Size 1.50\"" on its screen in "Making Bakelite
Polishing Puck" (https://www.youtube.com/watch?v=9m_hdgmu2Jw, 6:20), so both mounts are 38.1 mm across
(``MOUNT_D``), not the 31.75 mm that ``instruments.MOUNT_D`` and round8_plan.md assumed. Read ``MOUNT_D`` from here
rather than writing the number in.

* **The conductive hot mount** (``hot_mount``): a 1.5 in (38.1 mm) round mount, 20 mm tall, pressed from
  carbon-filled conductive phenolic in the LECO hot mounting press, with the AlSi10Mg coupon (14 x 10 x 6 mm, cut on
  the wire EDM) set in it, its polished face flush with the top. The filler is the SEM's path to ground: coupon ->
  compound -> the mount's sides and base -> the SEM holder's cup and set screw. For the micrographs, the SEM/EDS and
  the micro-Vickers hardness.
* **The steel mount for the mechanical tests** (``steel_mount``): a 38.1 mm steel puck (416 stainless: magnetic,
  free-machining, doesn't rust in the polishing water), 20 mm tall, with a 10.1 x 10.1 mm pocket. The wire-EDM slice
  (10 x 10 mm, 6 mm as cut, 5.6 mm once the CNC has faced both sides flat and parallel) sits on the pocket's steel
  floor, metal on metal, held by a ball plunger in the pocket wall (an M3 spring plunger, drawn as the "screw"
  part), faced flush with the puck's top on the CNC and polished. For nanoindentation and PIP: nothing soft under the
  sample to add compliance.

Frame for both: millimetres, the mount's axis on z, its base at z = 0, centred on x = y = 0; the specimen's face is at
``FACE_Z`` (the top). The coupon's and the slice's long edges run along x. The set screw enters from +x.

API
---
``hot_mount(state="polished", contact=False)`` and ``steel_mount(state="polished")`` return
``{part: (pyvista.PolyData, (r, g, b), specular)}``, the same triple ``alloy_characterize.mount_parts()`` returns, so
``for name, (mesh, col, spec) in hot_mount().items(): sc.add(f"grp/{name}", mesh, col, "grp", specular=spec)``
works as it is. Opacity is always 1.

* parts of ``hot_mount``: ``"phenolic"`` (the compound), ``"coupon"`` (the AlSi10Mg section), and with
  ``contact=True`` also ``"contact"`` (a brass M3 screw in a hole drilled from the base to the coupon's back: not
  used by default, see notes/alloy_prep.md).
* parts of ``steel_mount``: ``"puck"`` (the steel), ``"slice"`` (the AlSi10Mg slice), ``"screw"`` (the M3 set screw).
* ``state``: ``"polished"`` (the default: what chapter 7 gets), ``"ground"`` (after the SiC papers, a matte face),
  ``"pressed"`` (hot mount only: as ejected from the press, the coupon's wire-EDM face under a skin of compound,
  the mount 0.6 mm taller) or ``"seated"`` (steel mount only: the slice as cut, 6.0 mm, just pressed into the 5.6 mm
  pocket, 0.4 mm proud, before the CNC faces it flush). Only the colours and those offsets change; the part names are the same in every state.

``hot_mount_solids(...)`` and ``steel_mount_solids(...)`` take the same arguments and return the CadQuery solids,
``{part: (cadquery.Workplane, material key)}``, for an ``instruments.Instrument`` piece:
``_piece(inst, "sample").add(name, solid.translate(...), mat)``; ``MATERIALS`` (``instruments.MATERIALS``'s
``(r, g, b, opacity, specular)`` convention) holds every material key used, for ``tour.py`` to merge. Or put the
meshes on an instrument directly: ``inst.meshes["sample"] = inst_meshes(hot_mount(), M)``.

``moved(parts, M)`` returns the parts moved by a 4 x 4 matrix; ``merged(parts)`` one mesh of them all (for a collision
checker or a bounding box). ``FACE_Z``, ``MOUNT_D``, ``HOT`` and ``STEEL`` hold the sizes; ``COUPON_XY`` and
``SLICE_XY`` the specimens' (x, y) half-extents on the face, for placing indents or an SEM field.
"""
from __future__ import annotations

from functools import lru_cache

import cadquery as cq
import numpy as np
import pyvista as pv

MOUNT_D = 38.1                    # 1.5 in: the lab's MX400 mold ("Mold Size 1.50\"" on its screen, 9m_hdgmu2Jw 6:20)
FACE_Z = 20.0                     # both mounts: the polished face 20 mm over the base

# the conductive hot mount. The coupon is 14 x 10 x 6 mm (x, y, z), as alloy_characterize's was. Pressed, the mount
# is 0.6 mm taller (the skin of compound over the coupon's face that the first SiC paper grinds off) and the face is
# the as-cut wire-EDM surface
HOT = dict(d=MOUNT_D, h=FACE_Z, chamfer=0.5, coupon=(14.0, 10.0, 6.0), skin=0.6, contact_d=3.0)
# the steel mount. pocket 10.1 x 10.1 mm (0.05 mm a side over the slice) with 2 mm corner reliefs (an end mill
# leaves round corners: the reliefs let the square slice seat on the floor), 5.6 mm deep; the slice goes in as cut
# (6.0 mm, 0.4 mm proud: "seated") and the CNC faces it flush (5.6 mm); the ball plunger M3, 3 mm under the face, from
# +x (the part is still called "screw")
STEEL = dict(d=MOUNT_D, h=FACE_Z, chamfer=0.5, slice=(10.0, 10.0, 5.6), as_cut=6.0, pocket=10.1, relief_d=2.0,
             proud=0.4, screw_d=3.0, screw_z=FACE_Z - 3.0)
COUPON_XY = (HOT["coupon"][0] / 2, HOT["coupon"][1] / 2)
SLICE_XY = (STEEL["slice"][0] / 2, STEEL["slice"][1] / 2)

# key -> (r, g, b, opacity, specular), as instruments.MATERIALS
MATERIALS = {
    "r8s_phenolic": (0.10, 0.10, 0.11, 1.0, 0.35),     # carbon-filled conductive phenolic: black, a dull sheen
    "r8s_skin": (0.14, 0.14, 0.15, 1.0, 0.15),         # the same, as pressed (the ram's face)
    "r8s_polished": (0.82, 0.83, 0.85, 1.0, 0.90),     # AlSi10Mg, polished to 1 um alumina
    "r8s_ground": (0.66, 0.67, 0.69, 1.0, 0.35),       # AlSi10Mg off the SiC papers: matte
    "r8s_edm": (0.47, 0.48, 0.50, 1.0, 0.10),          # AlSi10Mg as cut on the wire EDM: grey, dull
    "r8s_steel": (0.64, 0.65, 0.68, 1.0, 0.70),        # 416 stainless, machined
    "r8s_steel_pol": (0.76, 0.77, 0.79, 1.0, 0.90),    # its top face, polished with the slice
    "r8s_screw": (0.13, 0.13, 0.14, 1.0, 0.40),        # black-oxide set screw
    "r8s_brass": (0.80, 0.65, 0.30, 1.0, 0.60),
}


def _rgb(mat):
    r, g, b, _, spec = MATERIALS[mat]
    return (r, g, b), spec


def _disc(d, h, chamfer, z=0.0) -> cq.Workplane:
    w = cq.Workplane("XY").circle(d / 2).extrude(h)
    if chamfer > 0:
        w = w.edges().chamfer(chamfer)
    return w.translate((0, 0, z))


def _box(x0, y0, z0, x1, y1, z1) -> cq.Workplane:
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2,
                                                                        (z0 + z1) / 2))


@lru_cache(maxsize=None)
def hot_mount_solids(state: str = "polished", contact: bool = False) -> dict:
    """The conductive hot mount as CadQuery solids: {part: (Workplane, material key)}. See the module docstring."""
    if state not in ("polished", "ground", "pressed"):
        raise ValueError(f"hot_mount state {state!r}: polished, ground or pressed")
    p = HOT
    cx, cy, cz = p["coupon"]
    h = p["h"] + (p["skin"] if state == "pressed" else 0.0)
    body = _disc(p["d"], h, p["chamfer"])
    hole = _box(-cx / 2, -cy / 2, p["h"] - cz, cx / 2, cy / 2, p["h"] + 0.01)
    if state == "pressed":
        hole = _box(-cx / 2, -cy / 2, p["h"] - cz, cx / 2, cy / 2, p["h"])
    body = body.cut(hole)
    out = {}
    if contact:
        bore = cq.Workplane("XY").circle(p["contact_d"] / 2).extrude(p["h"] - cz)
        body = body.cut(bore)
        out["contact"] = (cq.Workplane("XY").circle(p["contact_d"] / 2 - 0.05).extrude(p["h"] - cz - 0.5)
                          .translate((0, 0, 0.5)), "r8s_brass")
    face = {"polished": "r8s_polished", "ground": "r8s_ground", "pressed": "r8s_edm"}[state]
    coupon = _box(-cx / 2, -cy / 2, p["h"] - cz, cx / 2, cy / 2, p["h"])
    out = {"phenolic": (body, "r8s_skin" if state == "pressed" else "r8s_phenolic"), "coupon": (coupon, face), **out}
    return out


@lru_cache(maxsize=None)
def steel_mount_solids(state: str = "polished") -> dict:
    """The steel mount as CadQuery solids: {part: (Workplane, material key)}. See the module docstring."""
    if state not in ("polished", "ground", "seated"):
        raise ValueError(f"steel_mount state {state!r}: polished, ground or seated")
    p = STEEL
    h, a = p["h"], p["pocket"]
    sx, sy, sz = p["slice"]
    puck = _disc(p["d"], h, p["chamfer"])
    pocket = _box(-a / 2, -a / 2, h - sz, a / 2, a / 2, h + 1)
    for kx in (-1, 1):
        for ky in (-1, 1):
            pocket = pocket.union(cq.Workplane("XY").circle(p["relief_d"] / 2).extrude(sz + 1)
                                  .translate((kx * a / 2, ky * a / 2, h - sz)))
    puck = puck.cut(pocket)
    tap = cq.Workplane("YZ").circle(p["screw_d"] / 2).extrude(p["d"] / 2 + 1).translate((a / 2 - 0.5, 0, p["screw_z"]))
    puck = puck.cut(tap)
    up = p["proud"] if state == "seated" else 0.0
    slab = _box(-sx / 2, -sy / 2, h - sz, sx / 2, sy / 2, h + up)
    # the set screw: its point on the slice's +x side, its socket 0.5 mm inside the puck's surface
    L = p["d"] / 2 - 0.5 - sx / 2
    screw = cq.Workplane("YZ").circle(p["screw_d"] / 2 - 0.1).extrude(L).translate((sx / 2, 0, p["screw_z"]))
    screw = screw.cut(cq.Workplane("YZ").polygon(6, 1.7).extrude(1.6).translate((sx / 2 + L - 1.5, 0, p["screw_z"])))
    face = {"polished": "r8s_polished", "ground": "r8s_ground", "seated": "r8s_edm"}[state]
    return {"puck": (puck, "r8s_steel"), "slice": (slab, face), "screw": (screw, "r8s_screw")}


def _tess(w: cq.Workplane, tol=0.05, ang=0.2) -> pv.PolyData:
    shape = w.val() if len(w.vals()) == 1 else cq.Compound.makeCompound(w.vals())
    verts, tris = shape.tessellate(tol, ang)
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces).compute_normals(split_vertices=True, auto_orient_normals=False)


def _meshes(solids: dict) -> dict:
    out = {}
    for name, (w, mat) in solids.items():
        rgb, spec = _rgb(mat)
        out[name] = (_tess(w), rgb, spec)
    return out


@lru_cache(maxsize=None)
def _hot(state, contact):
    return _meshes(hot_mount_solids(state, contact))


@lru_cache(maxsize=None)
def _steel(state):
    return _meshes(steel_mount_solids(state))


def hot_mount(state: str = "polished", contact: bool = False) -> dict:
    """The conductive hot mount: {part: (PolyData, (r, g, b), specular)}, parts "phenolic", "coupon" (and "contact").
    Fresh copies each call, so they can be moved in place."""
    return {k: (m.copy(), c, s) for k, (m, c, s) in _hot(state, contact).items()}


def steel_mount(state: str = "polished") -> dict:
    """The steel mount: {part: (PolyData, (r, g, b), specular)}, parts "puck", "slice", "screw"."""
    return {k: (m.copy(), c, s) for k, (m, c, s) in _steel(state).items()}


def moved(parts: dict, M) -> dict:
    """The parts moved by the 4 x 4 matrix M (copies)."""
    M = np.asarray(M, float)
    return {k: (m.transform(M, inplace=False), c, s) for k, (m, c, s) in parts.items()}


def merged(parts: dict) -> pv.PolyData:
    """Every part in one mesh (for a collision checker or a bounding box)."""
    ms = [m for m, _, _ in parts.values()]
    return ms[0].merge(ms[1:]) if len(ms) > 1 else ms[0].copy()


def inst_meshes(parts: dict, M=None) -> list:
    """The parts as ``instruments.Instrument.meshes`` wants them: [(PolyData, (r, g, b), opacity)], moved by M."""
    if M is not None:
        parts = moved(parts, M)
    return [(m, c, 1.0) for m, c, _ in parts.values()]


if __name__ == "__main__":
    import sys
    for nm, fn, states in (("hot_mount", hot_mount, ("polished", "ground", "pressed")),
                           ("steel_mount", steel_mount, ("polished", "ground", "seated"))):
        for st in states:
            parts = fn(st)
            b = merged(parts).bounds
            print(f"{nm}({st!r}): " + ", ".join(f"{k} {m.n_cells} tris" for k, (m, _, _) in parts.items()),
                  f"| x {b[0]:.2f}..{b[1]:.2f} y {b[2]:.2f}..{b[3]:.2f} z {b[4]:.2f}..{b[5]:.2f}")
    if sys.argv[1:] == ["still"]:
        pl = pv.Plotter(off_screen=True, window_size=(900, 500))
        for dx, parts in ((-22.0, hot_mount()), (22.0, steel_mount())):
            for k, (m, c, s) in moved(parts, np.array([[1, 0, 0, dx], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                                                      float)).items():
                pl.add_mesh(m, color=c, specular=s, smooth_shading=False)
        pl.camera_position = [(40, -110, 90), (0, 0, 8), (0, 0, 1)]
        pl.screenshot("/tmp/r8_specimens.png")
        print("/tmp/r8_specimens.png")

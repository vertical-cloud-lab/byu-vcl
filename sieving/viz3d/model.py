"""CadQuery model of the bench for sieving atomized powder (docs/sieve-order.md), for the 3-D animation.

Everything is in millimetres, z up from the bench top, the operator stands at -y. Sizes:

* The three Gilson 3 in all-stainless full-height sieves, pan and cover of the order (V3SF #60 / #230 / #635,
  V3SFXPN, V3SFXCV): frame OD 3 in (76.2 mm), overall height 1.75 in (44.5 mm), stacked height 1-1/8 in
  (28.6 mm), so the skirt that nests into the sieve below is 5/8 in (15.9 mm). From globalgilson.com, read
  2026-10-07. The mesh is drawn as a thin disc, since 20-250 um wires are far below the drawing's resolution.
* The rePowder powder container as drawn in #255's ``atomizer-training/viz3d/model.py`` (O130 x 202 mm with a
  O108 top tube and a handle): its position was observed on video, its size was assumed there and is still not
  measured. Nobody has put a rule on it.
* A letter sheet of paper (279 x 216 mm), the stainless dish for pieces that go back as feedstock, 100 mL glass
  jars (O50 x 80 mm, a smaller jar than Chem Stores' per #222), a O75 mm powder funnel, a top-loading balance, and
  the powder doser's cartridge: the O25.0 mm auger tube from vertical-cloud-lab/powder-doser (PR #170).

``parts()`` returns the named solids; ``meshes()`` tessellates them (whole, and halved at y = 0 for the cutaway)
and caches them in ``.cache/``; ``heap_meshes()`` prebuilds the powder heaps at a series of levels.

    python model.py      # builds and caches the meshes, prints the part list
"""
from __future__ import annotations

import hashlib
import math
import pickle
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"

# ------------------------------------------------------------------------------------------ colours
STEEL = (0.80, 0.81, 0.83)
STEEL_DK = (0.60, 0.62, 0.65)
MESH_C = (0.50, 0.52, 0.56)
MESH_F = (0.44, 0.46, 0.50)
BENCH = (0.92, 0.91, 0.88)
PAPER = (0.985, 0.985, 0.97)
POWDER = (0.70, 0.72, 0.76)
CHUNK = (0.58, 0.60, 0.64)
GLASS = (0.72, 0.86, 0.94)
LID = (0.12, 0.12, 0.13)
BLACK = (0.07, 0.07, 0.08)
PANEL = (0.95, 0.95, 0.96)
LCD = (0.25, 0.55, 0.95)
BLUE = (0.16, 0.36, 0.78)
WHITE = (0.96, 0.96, 0.96)
RED = (0.80, 0.10, 0.08)
LABEL = (1.0, 1.0, 1.0)

# ------------------------------------------------------------------------------------- the sieves
SIEVE_OD = 76.2            # 3 in
SIEVE_H = 44.5             # overall, 1.75 in
STACKED_H = 28.6           # 1-1/8 in: what each nested sieve adds
SKIRT_H = SIEVE_H - STACKED_H     # 15.9 mm, nests inside the frame below
WALL = 0.8
SKIRT_OD = SIEVE_OD - 2 * WALL - 0.6
MESH_R = SIEVE_OD / 2 - WALL - 0.3
PAN_H = SIEVE_H            # the full-height pan matches the sieves
COVER_H = 12.0
COVER_SKIRT = 9.0

STACK_XY = (70.0, 0.0)     # the stack's axis on the bench
ORDER = ("pan", "s635", "s230", "s60")       # bottom to top
MESH_Z = {"pan": 1.2, "s635": PAN_H, "s230": PAN_H + STACKED_H, "s60": PAN_H + 2 * STACKED_H}
TOP_RIM_Z = PAN_H + 3 * STACKED_H              # 130.3: rim of the top sieve, where the cover sits
SIEVE_LABEL = {"s60": "No. 60 (250 um)", "s230": "No. 230 (63 um)", "s635": "No. 635 (20 um)", "pan": "pan"}

# ------------------------------------------------------------------------------- other things
PAPER_C = (-120.0, 15.0)   # letter sheet, landscape
PAPER_W, PAPER_D = 279.0, 216.0
CONT_R, CONT_H = 65.0, 202.0     # #255's assumed powder container (not measured)
CONT_XY = (-275.0, 110.0)
DISH_XY = (-70.0, 160.0)
JAR_R, JAR_H = 25.0, 80.0        # 100 mL jar
JAR_COARSE_XY = (195.0, 150.0)
JAR_FINES_XY = (195.0, -70.0)
BAL_XY = (305.0, 65.0)           # balance body centre; the print jar sits on its pan
BAL_W, BAL_D, BAL_H = 190.0, 210.0, 42.0
BAL_PAN_R, BAL_PAN_Z = 60.0, BAL_H + 10.0
JAR_PRINT_XY = BAL_XY
FUNNEL_TOP_R, FUNNEL_H = 37.5, 50.0
DOSER_XY = (290.0, -95.0)
DOSER_R, DOSER_L = 12.5, 100.0   # O25.0 auger tube (powder-doser PR #170)

# ------------------------------------------------------------------------------------- primitives
V = cq.Vector


def box(x0, x1, y0, y1, z0, z1) -> cq.Shape:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, pnt=V(x0, y0, z0))


def cyl(r, h, base=(0, 0, 0), d=(0, 0, 1)) -> cq.Shape:
    return cq.Solid.makeCylinder(r, h, V(*base), V(*d))


def tube(ro, ri, h, base=(0, 0, 0), d=(0, 0, 1)) -> cq.Shape:
    return cyl(ro, h, base, d).cut(cyl(ri, h + 2, np.array(base, float) - np.array(d, float) * 1.0, d))


def sphere(r, c=(0, 0, 0)) -> cq.Shape:
    return cq.Workplane("XY").sphere(r).val().translate(V(*c))


def lathe(pts, z0=0.0, x=0.0, y=0.0) -> cq.Shape:
    """Revolve a closed half-profile of (r, z) points about the z axis, then move it."""
    wp = cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))
    return wp.val().translate(V(x, y, z0))


def fuse(*shapes) -> cq.Shape:
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def torus(R, r, c=(0, 0, 0)) -> cq.Shape:
    return cq.Solid.makeTorus(R, r, V(*c), V(0, 0, 1))


# ------------------------------------------------------------------------------------------- parts
@dataclass
class Part:
    name: str
    shape: cq.Shape
    color: tuple
    group: str = "static"
    opacity: float = 1.0
    cut: bool = True               # halve it in cutaway views
    tol: float = 0.3
    tags: tuple = field(default_factory=tuple)


def sieve_frame(z_skirt: float, x: float, y: float) -> cq.Shape:
    """A full-height sieve with its skirt bottom at z_skirt: skirt, the step that rests on the sieve below, frame,
    rolled rim. The mesh is a separate part (so it can be coloured by fineness)."""
    zs, zm, zt = z_skirt, z_skirt + SKIRT_H, z_skirt + SIEVE_H
    ro, ri = SIEVE_OD / 2, SIEVE_OD / 2 - WALL
    rs = SKIRT_OD / 2
    prof = [(rs - WALL, zs), (rs, zs), (rs, zm - 1.0), (ro, zm - 1.0), (ro, zt - 1.5), (ro + 1.2, zt - 1.5),
            (ro + 1.2, zt), (ri, zt), (ri, zm + 0.6), (rs - WALL, zm + 0.6)]
    return lathe(prof, 0.0, x, y)


def sieve_mesh(z_skirt: float, x: float, y: float) -> cq.Shape:
    zm = z_skirt + SKIRT_H
    return cyl(MESH_R, 0.45, (x, y, zm - 0.2))


def pan(x: float, y: float) -> cq.Shape:
    ro, ri = SIEVE_OD / 2, SIEVE_OD / 2 - WALL
    prof = [(0, 0), (ro, 0), (ro, PAN_H - 1.5), (ro + 1.2, PAN_H - 1.5), (ro + 1.2, PAN_H), (ri, PAN_H),
            (ri, 1.2), (0, 1.2)]
    return lathe(prof, 0.0, x, y)


def cover(z_rim: float, x: float, y: float) -> cq.Shape:
    """A shallow lid: a skirt inside the top sieve's rim and a flat top with a rolled edge and a centre knob."""
    ri = SIEVE_OD / 2 - WALL - 0.4
    ro = SIEVE_OD / 2 + 1.2
    z0, z1 = z_rim - COVER_SKIRT, z_rim + 1.0
    prof = [(ri - WALL, z0), (ri, z0), (ri, z_rim), (ro, z_rim), (ro, z1 + 1.5), (ro - 1.5, z1 + 1.5), (ro - 1.5, z1),
            (0, z1), (0, z1 - 1.0), (ri - WALL, z1 - 1.0)]
    lid = lathe(prof, 0.0, x, y)
    knob = fuse(cyl(6, 3, (x, y, z1)), cyl(9, 2.5, (x, y, z1 + 3)))
    return fuse(lid, knob)


def container(x: float, y: float) -> cq.Shape:
    """#255's powder container: a stainless cylinder with a top tube (the valve seat) and a handle. Assumed size."""
    h = CONT_H
    body = lathe([(0, 0), (CONT_R - 12, 0), (CONT_R, 12), (CONT_R, h - 12), (52, h - 4), (52, h), (0, h)], 0.0, x, y)
    body = body.cut(lathe([(0, 4), (CONT_R - 15, 4), (CONT_R - 4, 15), (CONT_R - 4, h - 14), (40, h - 6),
                           (40, h + 40), (0, h + 40)], 0.0, x, y))
    body = body.fuse(tube(54, 40, 26, (x, y, h)))
    handle = fuse(box(x - 8, x + 8, y - 88, y - 54, h + 5, h + 21),
                  box(x - 4, x + 85, y - 100, y - 88, h + 7, h + 19))
    return fuse(body, handle)


def jar(x: float, y: float, z0: float = 0.0) -> cq.Shape:
    r = JAR_R
    prof = [(0, 0), (r - 3, 0), (r, 3), (r, JAR_H - 8), (r - 2, JAR_H - 5), (r - 2, JAR_H), (r - 3.5, JAR_H),
            (r - 3.5, JAR_H - 5), (r - 1.8, JAR_H - 9), (r - 1.8, 4), (r - 4, 1.8), (0, 1.8)]
    return lathe(prof, z0, x, y)


def jar_lid(x: float, y: float, z0: float = 0.0) -> cq.Shape:
    r = JAR_R - 1.4
    return lathe([(0, JAR_H - 6), (r, JAR_H - 6), (r, JAR_H + 2), (r - 1.2, JAR_H + 2.6), (0, JAR_H + 2.6)], z0, x, y)


def funnel(x: float, y: float, z0: float) -> cq.Shape:
    R, h = FUNNEL_TOP_R, FUNNEL_H
    prof = [(5.0, 0), (6.2, 0), (6.2, 14), (R, h + 14), (R + 1.5, h + 14), (R + 1.5, h + 12.5), (R - 0.3, h + 12.5),
            (5.0, 14)]
    return lathe(prof, z0, x, y)


def dish(x: float, y: float) -> cq.Shape:
    return lathe([(0, 0), (28, 0), (32, 11), (33.5, 11), (33.5, 12), (31, 12), (27, 1.2), (0, 1.2)], 0.0, x, y)


def balance(x: float, y: float) -> list[Part]:
    P = []
    body = cq.Workplane("XY").box(BAL_W, BAL_D, BAL_H).edges("|Z").fillet(8).val().translate(V(x, y, BAL_H / 2))
    P.append(Part("balance_body", body, PANEL, "balance", cut=False, tol=0.6))
    P.append(Part("balance_display", box(x - 60, x + 60, y - BAL_D / 2 - 0.6, y - BAL_D / 2 + 1.0, 12, 30), LCD,
                  "balance", cut=False, tol=0.5))
    P.append(Part("balance_pedestal", cyl(16, BAL_PAN_Z - BAL_H, (x, y, BAL_H)), STEEL_DK, "balance", cut=False))
    P.append(Part("balance_pan", cyl(BAL_PAN_R, 2.0, (x, y, BAL_PAN_Z)), STEEL, "balance", cut=False, tol=0.4))
    return P


def doser_tube(x: float, y: float) -> list[Part]:
    """The doser's cartridge: the O25.0 auger tube with its screw-on cap, standing on end for scale."""
    r = DOSER_R
    P = [Part("doser_tube", fuse(cyl(r, DOSER_L - 14, (x, y, 0)), cyl(r - 0.5, 14, (x, y, DOSER_L - 14))), WHITE,
              "doser", cut=False, tol=0.2),
         Part("doser_band", tube(r + 0.6, r - 1, 22, (x, y, 30)), BLUE, "doser", cut=False, tol=0.2),
         Part("doser_cap", fuse(cyl(13.2, 9, (x, y, DOSER_L - 2)), cyl(10, 3, (x, y, DOSER_L + 7))), BLUE, "doser",
              cut=False, tol=0.2)]
    return P


CHUNK_POS: list[np.ndarray] = []      # each piece's centre on the paper heap (filled by chunk_shapes)


def chunk_shapes(rng: np.random.Generator, n: int) -> list[cq.Shape]:
    """Irregular unatomized pieces, 2-6 mm: two or three fused spheres each, half-buried in the surface of the
    full heap on the paper (heap_cone(1.0): 50 mm radius, 19 mm high)."""
    out = []
    CHUNK_POS.clear()
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        rr = rng.uniform(8, 30)
        r0 = rng.uniform(1.2, 3.0)
        zc = 19.0 * (1 - rr / 50.0) * 0.9 - r0 * 0.3
        c = np.array([rr * math.cos(a), rr * math.sin(a), zc])
        CHUNK_POS.append(c.copy())
        parts = []
        for k in range(rng.integers(2, 4)):
            r = r0 if k == 0 else rng.uniform(1.0, 2.6)
            off = rng.normal(0, 1.5, 3) if k else np.zeros(3)
            parts.append(sphere(r, c + off))
        out.append(fuse(*parts))
    return out


def heap_cone(v: float, R0=50.0, H0=19.0) -> cq.Shape:
    """A heap poured onto the paper: volume fraction v (0-1) of the full heap, keeping the angle of repose."""
    s = max(v, 0.02) ** (1 / 3)
    R, h = R0 * s, H0 * s
    return lathe([(0, 0), (R, 0), (R * 0.88, h * 0.12), (R * 0.45, h * 0.62), (0, h)])


def heap_disc(d: float, R=MESH_R - 1.0) -> cq.Shape:
    """A layer d mm deep on a mesh or in the pan, slightly domed."""
    d = max(d, 0.5)
    return lathe([(0, 0), (R, 0), (R, d * 0.75), (R * 0.6, d * 1.05), (0, d * 1.25)])


def heap_jar(d: float, R=JAR_R - 2.0) -> cq.Shape:
    d = max(d, 0.6)
    return lathe([(0, 0), (R, 0), (R, d * 0.85), (R * 0.5, d * 1.08), (0, d * 1.15)])


def parts() -> list[Part]:
    P = []
    # bench top (the drawing's floor), matte
    P.append(Part("bench", box(-420, 440, -210, 260, -18, 0), BENCH, "static", cut=False, tol=2.0))
    # paper, flat, and its folded form (a V trough along x) at the same place
    px, py = PAPER_C
    P.append(Part("paper", box(px - PAPER_W / 2, px + PAPER_W / 2, py - PAPER_D / 2, py + PAPER_D / 2, 0, 0.3), PAPER,
                  "paper", cut=False, tol=1.0))
    half_w = PAPER_D / 2
    leaf = box(-PAPER_W / 2, PAPER_W / 2, 0, half_w, 0, 0.3)
    left = leaf.rotate(V(0, 0, 0), V(1, 0, 0), 32).translate(V(px, py, 0))
    right = leaf.rotate(V(0, 0, 0), V(1, 0, 0), 180 - 32).translate(V(px, py, 0))
    P.append(Part("trough", fuse(left, right), PAPER, "trough", cut=False, tol=1.0))
    # the sieve stack, assembled, pan on the bench
    sx, sy = STACK_XY
    P.append(Part("pan", pan(sx, sy), STEEL, "pan", tol=0.25))
    for name, meshc in (("s635", MESH_F), ("s230", MESH_F), ("s60", MESH_C)):
        zs = MESH_Z[name] - SKIRT_H
        P.append(Part(name, sieve_frame(zs, sx, sy), STEEL, name, tol=0.25))
        P.append(Part(name + "_mesh", sieve_mesh(zs, sx, sy), meshc, name, tol=0.6))
    P.append(Part("cover", cover(TOP_RIM_Z, sx, sy), STEEL, "cover", tol=0.25))
    # the powder container, standing beside the paper
    P.append(Part("container", container(*CONT_XY), STEEL, "container", cut=False, tol=0.5))
    # dish for the pieces, jars with lids, funnel, balance, doser cartridge
    P.append(Part("dish", dish(*DISH_XY), STEEL, "dish", cut=False, tol=0.3))
    for name, (x, y), z0 in (("coarse", JAR_COARSE_XY, 0.0), ("fines", JAR_FINES_XY, 0.0),
                             ("print", JAR_PRINT_XY, BAL_PAN_Z + 2.0)):
        P.append(Part(f"jar_{name}", jar(x, y, z0), GLASS, f"jar_{name}", opacity=0.40, cut=False, tol=0.3))
        P.append(Part(f"lid_{name}", jar_lid(x, y, z0), LID, f"lid_{name}", cut=False, tol=0.3))
    P.append(Part("funnel", funnel(JAR_COARSE_XY[0], JAR_COARSE_XY[1], JAR_H - 10), STEEL, "funnel", cut=False,
                  tol=0.3))
    P += balance(*BAL_XY)
    P += doser_tube(*DOSER_XY)
    P.append(Part("label", box(JAR_PRINT_XY[0] - 14, JAR_PRINT_XY[0] + 14,
                               JAR_PRINT_XY[1] - JAR_R - 0.4, JAR_PRINT_XY[1] - JAR_R + 0.3,
                               BAL_PAN_Z + 2.0 + 22, BAL_PAN_Z + 2.0 + 44), LABEL, "label", cut=False, tol=0.3))
    # unatomized pieces on the paper heap (group "chunks") and the grit that stays on the No. 60 (group "grit")
    rng = np.random.default_rng(7)
    for k, s in enumerate(chunk_shapes(rng, 7)):
        P.append(Part(f"chunk{k}", s.translate(V(px, py, 0.3)), CHUNK, f"chunk{k}", cut=False, tol=0.15))
    rng = np.random.default_rng(11)
    for k in range(9):
        a, rr, r = rng.uniform(0, 2 * math.pi), rng.uniform(4, 30), rng.uniform(0.6, 1.4)
        P.append(Part(f"grit{k}", sphere(r, (sx + rr * math.cos(a), sy + rr * math.sin(a), MESH_Z["s60"] + 0.3 + r)),
                      CHUNK, "grit", cut=False, tol=0.1))
    return P


# ----------------------------------------------------------------------------------------- meshing
def _poly(shape: cq.Shape, tol: float):
    import pyvista as pv
    verts, tris = shape.tessellate(tol, 0.3)
    if not tris:
        return None
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([[3, *t] for t in tris]).astype(np.int64)
    return pv.PolyData(pts, faces)


def tess(shape: cq.Shape, tol: float = 0.3, split_cut: bool = False):
    """PyVista mesh of a CadQuery shape. With split_cut, returns (body, cut faces lying on y = 0)."""
    import pyvista as pv
    body, cut = [], []
    for f in shape.Faces():
        p = _poly(f, tol)
        if p is None:
            continue
        if split_cut and f.geomType() == "PLANE":
            bb = f.BoundingBox()
            if abs(bb.ymin) < 1e-4 and abs(bb.ymax) < 1e-4:
                cut.append(p)
                continue
        body.append(p)

    def merge(ps):
        if not ps:
            return None
        m = pv.merge(ps, merge_points=False) if len(ps) > 1 else ps[0]
        return m.compute_normals(split_vertices=True, feature_angle=40, auto_orient_normals=False)

    return (merge(body), merge(cut)) if split_cut else merge(body)


def halve(shape: cq.Shape) -> cq.Shape:
    """Keep y >= 0 (the camera looks from -y, so the cut faces point at it)."""
    return shape.cut(box(-3000, 3000, -3000, 0, -3000, 3000))


def _source_hash() -> str:
    return hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]


def meshes(force: bool = False) -> dict:
    """{name: dict(whole, half, half_cut, color, group, opacity, cut, gone)} (cached)."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"meshes_{_source_hash()}.pkl"
    if path.exists() and not force:
        return pickle.loads(path.read_bytes())
    out = {}
    for p in parts():
        whole = tess(p.shape, p.tol)
        half = half_cut = None
        gone = False
        if p.cut:
            try:
                h = halve(p.shape)
                if h.isValid() and h.Volume() > 1e-3:
                    half, half_cut = tess(h, p.tol, split_cut=True)
                else:
                    gone = p.shape.BoundingBox().ymax <= 1e-6
            except Exception as exc:  # noqa: BLE001
                print("halve failed:", p.name, exc)
        out[p.name] = dict(whole=whole, half=half, half_cut=half_cut, color=p.color, group=p.group,
                           opacity=p.opacity, cut=p.cut, gone=gone)
    path.write_bytes(pickle.dumps(out))
    return out


HEAP_LEVELS = {"cone": np.linspace(0.0, 1.0, 26), "disc": np.linspace(0.5, 10.0, 24),
               "jar": np.linspace(0.6, 36.0, 24)}


def heap_meshes(force: bool = False) -> dict:
    """Powder heaps at a series of levels, as (whole, half, half_cut) meshes, built about the origin: the animation
    moves them into place. Cached."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"heaps_{_source_hash()}.pkl"
    if path.exists() and not force:
        return pickle.loads(path.read_bytes())
    out = {"levels": HEAP_LEVELS, "cone": [], "disc": [], "jar": []}
    for v in HEAP_LEVELS["cone"]:
        out["cone"].append((tess(heap_cone(v), 0.3), None, None))
    for d in HEAP_LEVELS["disc"]:
        s = heap_disc(d)
        hb, hc = tess(halve(s), 0.3, split_cut=True)
        out["disc"].append((tess(s, 0.3), hb, hc))
    for d in HEAP_LEVELS["jar"]:
        out["jar"].append((tess(heap_jar(d), 0.3), None, None))
    path.write_bytes(pickle.dumps(out))
    return out


if __name__ == "__main__":
    import time
    t = time.time()
    m = meshes(force=True)
    print(f"{len(m)} parts in {time.time() - t:.0f} s")
    for k, v in m.items():
        print(f"  {k:18s} {v['group']:10s} {v['whole'].n_cells if v['whole'] is not None else 0:7d} tris"
              f"{'  (cutaway)' if v['half'] is not None else ''}")
    t = time.time()
    heap_meshes(force=True)
    print(f"heaps in {time.time() - t:.0f} s")

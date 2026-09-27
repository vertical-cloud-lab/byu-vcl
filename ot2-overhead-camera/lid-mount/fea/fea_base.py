#!/usr/bin/env python3
"""FEA check of the OT-2 lid-mount base (plate + four posts): CadQuery STEP -> gmsh -> CalculiX.

One command, end to end (about a minute on a 4-core runner):

    python fea/fea_base.py                           # default mesh, about 5 min on 4 cores
    python fea/fea_base.py --root 0.35 --tag fine    # finer post roots

Needs gmsh + numpy + matplotlib (pip), the GL/X runtime libs the gmsh wheel links against
(apt: libglu1-mesa libxcursor1 libxft2 libxinerama1) and ccx on PATH (apt: calculix-ccx).

Units: mm, N, MPa, tonne (density in t/mm^3), s  ->  eigenfrequencies come out in Hz.

Model
-----
* The base is fixed on its whole bottom face (z = 0): taped or bolted to the lid (in the
  modal case: stuck to the build plate).
* Two material models on one mesh:
    solid    - every element as-printed solid PLA (upper bound on stiffness and mass).
    printed  - each post split into its 3 perimeters (1.32 mm, solid PLA) and a core of 25 %
               grid infill homogenised as E_core = 0.25 E, rho_core = 0.25 rho, from the post
               root (z = 6) to z = 86 (below the M3 hole). The plate stays solid (optimistic).
* Loads go onto the four post-top faces (the deck sits on them) as consistent nodal forces
  for 6-node triangles (corner nodes 0, mid-side nodes A/3 each).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

LID = Path(__file__).resolve().parents[1]
STEP_FILE = LID / "exports" / "base.step"
P = json.loads((LID / "exports" / "params.json").read_text())

# --- geometry, with the same formulas as cad/lid_mount.py Params ---------------------------
Z_LENS_FRONT = P["base_t"] + P["lens_front_gap"]
Z_LENS_FLANGE = Z_LENS_FRONT + P["lens_length"] - P["lens_thread_len"]
Z_DECK = Z_LENS_FLANGE + P["c_cs_adapter"] + P["cs_seat_from_pcb_back"] + P["cam_standoff"]
Z_POST_TOP = Z_DECK + P["socket_depth"]                               # 102.16
Z_M3_SLOT = Z_POST_TOP - P["m3_nut_roof"] - P["m3_nut_slot_h"]        # 94.66
Z_M3_HOLE_BOTTOM = Z_DECK + P["deck_t"] - P["m3_screw_len"] - 1.0    # 87.66
Z_ROOT = P["base_t"]                                                  # 6.0
POST_L = Z_POST_TOP - Z_ROOT                                          # 96.16
PC, PW, POST_R = P["post_c"], P["post_w"], 1.5                        # 1.5: rounded_box() in make_base
POSTS = [(sx * PC, sy * PC) for sx in (-1, 1) for sy in (-1, 1)]

# --- print settings, read from slice/lid_mount_A1mini_PLA.3mf -----------------------------
WALL_T = 0.42 + 2 * 0.45      # outer_wall_line_width + 2 x inner_wall_line_width (wall_loops = 3)
INFILL = 0.25                 # sparse_infill_density, pattern = grid
Z_CORE_TOP = 86.0             # stop the core below the M3 hole (87.66): the top is walls/skins

# --- materials ----------------------------------------------------------------------------
# E in MPa, rho in t/mm^3. nu = 0.35 is an assumption (neither datasheet gives it).
#  bulk    : NatureWorks Ingeo 4043D, tensile modulus 3.6 GPa, SG 1.24, solid everywhere.
#            The stiff/heavy end of the bracket.
#  printed : Bambu Lab PLA Basic TDS v3.0, Z (across layers) modulus 2060 MPa, density 1.24.
#            Walls are solid; the post cores are 25 % grid, whose lines stack into vertical
#            walls, so E_core,Z ~ 0.25 E (stretch-dominated; an upper estimate for the core).
MATERIALS = {
    "bulk": dict(E_wall=3600.0, E_core=3600.0, nu=0.35, rho_wall=1.24e-9, rho_core=1.24e-9),
    "printed": dict(E_wall=2060.0, E_core=INFILL * 2060.0, nu=0.35, rho_wall=1.24e-9,
                    rho_core=INFILL * 1.24e-9),
}
STRENGTH = {                  # MPa, short-term tensile
    "XY": 35.0,               # Bambu PLA Basic TDS, X-Y (annealed, 100 % infill coupons)
    "Z_TDS": 31.0,            # Bambu PLA Basic TDS, Z: across layers (same annealed coupons)
    "Z_design": 15.0,         # assumption: ~0.5 x TDS for as-printed, unannealed thin walls
}

# --- loads ----------------------------------------------------------------------------------
G = 9.81
MASSES_KG = {
    "deck (slicer: plate 2 of the 3mf, 43.5 g)": 0.0435,
    "HQ camera + C-CS adapter + 8-50 mm zoom lens (upper bound)": 0.40,
    "Pi 5 + Active Cooler (upper bound)": 0.10,
    "screws, nuts, Pi spacers, ribbon cable (estimate)": 0.03,
}
DYN = 3.0                     # dynamic factor on the static weight
F_LAT = 10.0                  # N, lateral bump, shared by the four post tops
N_MODES = 10


# ============================================================================================
# mesh
# ============================================================================================
def build_mesh(args, work: Path) -> dict:
    import gmsh

    t0 = time.time()
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    # One thread: multithreaded HXT gave a different mesh on every run. Serial is still ~10 s.
    gmsh.option.setNumber("General.NumThreads", 1)
    gmsh.model.add("base")
    # OCC converts STEP lengths to mm by default (Geometry.OCCTargetUnit empty); CadQuery writes mm.
    gmsh.model.occ.importShapes(str(STEP_FILE))
    gmsh.model.occ.synchronize()
    (vol,) = gmsh.model.getEntities(3)
    step_volume = gmsh.model.occ.getMass(*vol)

    # Post cores: boxes inside the 3 perimeters, fragmented into the solid so both share nodes.
    hc = PW / 2 - WALL_T
    boxes = [(3, gmsh.model.occ.addBox(x - hc, y - hc, Z_ROOT, 2 * hc, 2 * hc, Z_CORE_TOP - Z_ROOT))
             for x, y in POSTS]
    gmsh.model.occ.fragment([vol], boxes)
    gmsh.model.occ.synchronize()

    # Entity tags change after a boolean: classify everything again by bounding box.
    core_vols, wall_vols = [], []
    for d, t in gmsh.model.getEntities(3):
        b = gmsh.model.getBoundingBox(d, t)
        (core_vols if (b[3] - b[0]) < PW - 1 and (b[4] - b[1]) < PW - 1 else wall_vols).append(t)
    assert len(core_vols) == 4 and len(wall_vols) == 1, (core_vols, wall_vols)

    def in_post(b, pad=0.05):
        return next((i for i, (x, y) in enumerate(POSTS)
                     if b[0] > x - PW / 2 - pad and b[3] < x + PW / 2 + pad
                     and b[1] > y - PW / 2 - pad and b[4] < y + PW / 2 + pad), None)

    bottom, tops = [], {}
    for d, t in gmsh.model.getEntities(2):
        b = gmsh.model.getBoundingBox(d, t)
        if abs(b[2]) < 1e-6 and abs(b[5]) < 1e-6:
            bottom.append(t)
        if abs(b[2] - Z_POST_TOP) < 1e-6 and abs(b[5] - Z_POST_TOP) < 1e-6:
            i = in_post(b)
            assert i is not None
            tops[i] = t
    assert bottom and len(tops) == 4, (bottom, tops)

    root_curves, slot_curves = [], []
    for d, t in gmsh.model.getEntities(1):
        b = gmsh.model.getBoundingBox(d, t)
        if in_post(b) is None:
            continue
        if abs(b[2] - Z_ROOT) < 1e-4 and abs(b[5] - Z_ROOT) < 1e-4:
            root_curves.append(t)          # post/plate junction (and the core's bottom edges)
        elif b[2] > Z_M3_SLOT - 0.05 and b[5] < Z_M3_SLOT + P["m3_nut_slot_h"] + 0.05:
            slot_curves.append(t)          # M3 nut slot

    # Size fields: fine at the roots and the nut slots, medium in the posts, coarse elsewhere.
    f = gmsh.model.mesh.field
    fields = []
    for curves, h, dmax in ((root_curves, args.root, 10.0), (slot_curves, args.slot, 4.0)):
        fd = f.add("Distance")
        f.setNumbers(fd, "CurvesList", curves)
        f.setNumber(fd, "Sampling", 60)
        ft = f.add("Threshold")
        f.setNumber(ft, "InField", fd)
        f.setNumber(ft, "SizeMin", h)
        f.setNumber(ft, "SizeMax", args.size)
        f.setNumber(ft, "DistMin", 0.3)
        f.setNumber(ft, "DistMax", dmax)
        fields.append(ft)
    for x, y in POSTS:
        fb = f.add("Box")
        f.setNumber(fb, "VIn", args.post)
        f.setNumber(fb, "VOut", args.size)
        for k, v in (("XMin", x - PW / 2 - 0.5), ("XMax", x + PW / 2 + 0.5), ("YMin", y - PW / 2 - 0.5),
                     ("YMax", y + PW / 2 + 0.5), ("ZMin", Z_ROOT - 1.0), ("ZMax", Z_POST_TOP + 1.0)):
            f.setNumber(fb, k, v)
        f.setNumber(fb, "Thickness", 4.0)
        fields.append(fb)
    fm = f.add("Min")
    f.setNumbers(fm, "FieldsList", fields)
    f.setAsBackgroundMesh(fm)
    for k, v in (("Mesh.MeshSizeExtendFromBoundary", 0), ("Mesh.MeshSizeFromPoints", 0),
                 ("Mesh.MeshSizeFromCurvature", 12), ("Mesh.MeshSizeMax", args.size),
                 ("Mesh.MeshSizeMin", 0.2), ("Mesh.Algorithm", 6), ("Mesh.Algorithm3D", 10),
                 ("Mesh.Optimize", 1)):
        gmsh.option.setNumber(k, v)
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.setOrder(2)            # 10-node tets, mid-side nodes snapped to the CAD
    # Snapping mid-side nodes onto curved faces can nearly invert a tet (one had minSICN 0.003;
    # a Delaunay mesh even went negative). The high-order optimiser fixes those in ~1 s.
    et = np.concatenate(gmsh.model.mesh.getElements(3)[1])
    q_curved = float(gmsh.model.mesh.getElementQualities(et, "minSICN").min())
    gmsh.option.setNumber("Mesh.HighOrderThresholdMin", 0.3)
    gmsh.model.mesh.optimize("HighOrder")

    # --- pull the mesh out ----------------------------------------------------------------
    ntags, xyz, _ = gmsh.model.mesh.getNodes()
    X = np.zeros((int(ntags.max()) + 1, 3))
    X[ntags.astype(np.int64)] = xyz.reshape(-1, 3)
    elsets = {}
    for name, vols in (("WALLS", wall_vols), ("CORES", core_vols)):
        conns = []
        for t in vols:
            types, _, enodes = gmsh.model.mesh.getElements(3, t)
            assert list(types) == [11], types                     # 11 = 10-node tetrahedron
            conns.append(enodes[0].reshape(-1, 10).astype(np.int64))
        # gmsh tet10 edges: 4:(0,1) 5:(1,2) 6:(2,0) 7:(3,0) 8:(3,2) 9:(3,1)
        # ccx C3D10 edges:  5:(1,2) 6:(2,3) 7:(3,1) 8:(1,4) 9:(2,4) 10:(3,4)  -> swap the last two
        elsets[name] = np.vstack(conns)[:, [0, 1, 2, 3, 4, 5, 6, 7, 9, 8]]

    # Check the ordering geometrically: each mid-side node sits near its edge midpoint.
    allc = np.vstack(list(elsets.values()))
    edges = [(0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)]
    err = max(float(np.max(np.linalg.norm(X[allc[:, 4 + k]] - 0.5 * (X[allc[:, a]] + X[allc[:, b]]), axis=1)
                           / np.linalg.norm(X[allc[:, a]] - X[allc[:, b]], axis=1)))
              for k, (a, b) in enumerate(edges))
    assert err < 0.25, f"C3D10 node ordering looks wrong (mid-side offset {err:.2f} x edge)"

    # Sign of the corner-node Jacobian (ccx needs positive volumes).
    c = allc[:, :4]
    vol6 = np.einsum("ij,ij->i", np.cross(X[c[:, 1]] - X[c[:, 0]], X[c[:, 2]] - X[c[:, 0]]), X[c[:, 3]] - X[c[:, 0]])
    assert (vol6 > 0).all(), f"{(vol6 <= 0).sum()} inverted tets"
    qual = []
    for t in wall_vols + core_vols:
        _, etags, _ = gmsh.model.mesh.getElements(3, t)
        qual.append(gmsh.model.mesh.getElementQualities(etags[0], "minSICN"))
    qual = np.concatenate(qual)

    fix = set()
    for t in bottom:
        fix.update(gmsh.model.mesh.getNodes(2, t, includeBoundary=True)[0].astype(np.int64).tolist())
    tops_tri = {}
    for i, t in tops.items():
        types, _, enodes = gmsh.model.mesh.getElements(2, t)
        assert list(types) == [9], types                            # 9 = 6-node triangle
        tops_tri[i] = enodes[0].reshape(-1, 6).astype(np.int64)
    # Boundary triangles for the picture: only faces with exactly one adjacent volume are on the
    # outside (the cores add internal faces).
    ext = [t for d, t in gmsh.model.getEntities(2) if len(gmsh.model.getAdjacencies(2, t)[0]) == 1]
    skin = [enodes[0].reshape(-1, 6)[:, :3].astype(np.int64)
            for t in ext for types, _, enodes in [gmsh.model.mesh.getElements(2, t)] if len(types)]
    gmsh.write(str(work / "base_mesh.msh"))
    gmsh.finalize()

    used = np.unique(allc)
    stats = dict(
        nodes=int(used.size), C3D10=int(allc.shape[0]), dofs=int(3 * used.size),
        walls_elements=int(elsets["WALLS"].shape[0]), core_elements=int(elsets["CORES"].shape[0]),
        size_global_mm=args.size, size_posts_mm=args.post, size_roots_mm=args.root, size_slots_mm=args.slot,
        min_quality_minSICN=float(qual.min()), p01_quality_minSICN=float(np.percentile(qual, 1)),
        min_quality_before_high_order_opt=q_curved,
        midside_offset_max=round(err, 4), step_volume_mm3=round(step_volume, 1),
        mesh_volume_mm3=round(float(vol6.sum() / 6), 1),
        walls_volume_mm3=round(float(vol6[:elsets["WALLS"].shape[0]].sum() / 6), 1),
        core_volume_mm3=round(float(vol6[elsets["WALLS"].shape[0]:].sum() / 6), 1),
        root_curves=len(root_curves), slot_curves=len(slot_curves), mesh_time_s=round(time.time() - t0, 1))
    return dict(X=X, elsets=elsets, fix=np.array(sorted(fix)), tops=tops_tri, skin=np.vstack(skin),
                used=used, stats=stats)


def write_mesh_inp(mesh: dict, path: Path) -> None:
    X, used = mesh["X"], mesh["used"]
    out = ["*NODE, NSET=NALL"]
    out += [f"{n}, {X[n, 0]:.9g}, {X[n, 1]:.9g}, {X[n, 2]:.9g}" for n in used]
    eid = 1
    for name, conn in mesh["elsets"].items():
        out.append(f"*ELEMENT, TYPE=C3D10, ELSET={name}")
        for row in conn:
            out.append(f"{eid}, " + ", ".join(str(int(n)) for n in row))
            eid += 1

    def nset(name, nodes):
        out.append(f"*NSET, NSET={name}")
        nodes = [int(n) for n in nodes]
        out.extend(", ".join(map(str, nodes[i:i + 16])) for i in range(0, len(nodes), 16))

    nset("FIX", mesh["fix"])
    for i, tri in mesh["tops"].items():
        nset(f"TOP{i + 1}", np.unique(tri))
    path.write_text("\n".join(out) + "\n")


# ============================================================================================
# loads and CalculiX
# ============================================================================================
def face_loads(mesh: dict, traction_per_post: np.ndarray) -> dict[int, np.ndarray]:
    """Consistent nodal forces for a uniform traction on each post-top face.

    For a flat 6-node triangle under uniform traction t, the consistent loads are 0 at the
    corners and t*A/3 at each mid-side node. traction_per_post[i] is the total force (N) on post i.
    """
    X, loads = mesh["X"], {}
    for i, tri in mesh["tops"].items():
        a = 0.5 * np.linalg.norm(np.cross(X[tri[:, 1]] - X[tri[:, 0]], X[tri[:, 2]] - X[tri[:, 0]]), axis=1)
        t = traction_per_post[i] / a.sum()                        # N/mm^2 on this face
        for k in range(len(tri)):
            for m in tri[k, 3:]:
                loads[int(m)] = loads.get(int(m), np.zeros(3)) + t * a[k] / 3.0
    return loads


def write_job(work: Path, name: str, mat: dict, loads: dict | None) -> Path:
    L = ["*HEADING", f"OT-2 lid mount base: {name}", "*INCLUDE, INPUT=mesh.inp"]
    for tag, E, rho in (("WALL", mat["E_wall"], mat["rho_wall"]), ("CORE", mat["E_core"], mat["rho_core"])):
        L += [f"*MATERIAL, NAME={tag}", "*ELASTIC", f"{E:.6g}, {mat['nu']}", "*DENSITY", f"{rho:.6e}"]
    L += ["*SOLID SECTION, ELSET=WALLS, MATERIAL=WALL", "*SOLID SECTION, ELSET=CORES, MATERIAL=CORE",
          "*BOUNDARY", "FIX, 1, 3, 0.0", "*STEP"]
    if loads is None:
        L += ["*FREQUENCY", f"{N_MODES}", "*NODE FILE", "U"]
    else:
        L += ["*STATIC", "*CLOAD"]
        for n, fvec in sorted(loads.items()):
            L += [f"{n}, {d + 1}, {fvec[d]:.10e}" for d in range(3) if abs(fvec[d]) > 0]
        L += ["*NODE FILE", "U", "*EL FILE", "S", "*NODE PRINT, NSET=FIX, TOTALS=ONLY", "RF"]
    L += ["*END STEP"]
    inp = work / f"{name}.inp"
    inp.write_text("\n".join(L) + "\n")
    return inp


def run_ccx(work: Path, name: str, threads: int) -> float:
    # SPOOLES stays on ONE thread: with 4 solver threads, ccx 2.21 (Ubuntu apt) returned corrupt
    # nodal results on this model (99 MPa spikes; one case out of equilibrium by 0.4 %), while
    # 1 thread and the iterative solver agreed. Parallelism comes from running jobs side by side.
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), CCX_NPROC_EQUATION_SOLVER="1",
               CCX_NPROC_STIFFNESS=str(threads), CCX_NPROC_RESULTS=str(threads))
    t0 = time.time()
    r = subprocess.run(["ccx", "-i", name], cwd=work, env=env, capture_output=True, text=True)
    (work / f"{name}.log").write_text(r.stdout + r.stderr)
    # ccx can exit 0 after an *ERROR, so check the log and the result file too.
    if r.returncode != 0 or "*ERROR" in r.stdout or not (work / f"{name}.frd").exists():
        tail = "\n".join((r.stdout + r.stderr).splitlines()[-25:])
        raise RuntimeError(f"ccx failed on {name}:\n{tail}")
    return time.time() - t0


def read_frd(path: Path) -> list[dict]:
    """Minimal ASCII .frd reader: nodal result blocks (DISP, STRESS, ...).

    Values are fixed-width (I10 node id after ' -1', then E12.5 fields); negative numbers run
    together with no space, so never split on whitespace.
    """
    blocks, cur = [], None
    with open(path) as fh:
        for line in fh:
            if line.startswith("  100C"):
                cur = dict(value=float(line[12:24]), name=None, comps=[], data={})
                blocks.append(cur)
            elif cur is not None and line.startswith(" -4"):
                cur["name"] = line[5:13].strip()
            elif cur is not None and line.startswith(" -5"):
                cur["comps"].append(line[5:13].strip())
            elif cur is not None and line.startswith(" -1"):
                s = line.rstrip("\n")
                n = int(s[3:13])
                cur["data"][n] = [float(s[13 + 12 * k:25 + 12 * k]) for k in range((len(s) - 13) // 12)]
            elif cur is not None and line.startswith(" -3"):
                cur = None
    return blocks


def as_array(block: dict, nmax: int) -> np.ndarray:
    ncol = len(next(iter(block["data"].values())))
    A = np.full((nmax + 1, ncol), np.nan)
    for n, v in block["data"].items():
        A[n] = v
    return A


def dat_total_force(path: Path) -> list[float]:
    lines = path.read_text().splitlines()
    for i, s in enumerate(lines):
        if "total force" in s:
            for t in lines[i + 1:i + 4]:
                if t.strip():
                    return [float(v) for v in t.split()]
    raise RuntimeError("no total force in .dat")


def dat_frequencies(path: Path) -> list[float]:
    txt = path.read_text()
    part = txt.split("E I G E N V A L U E   O U T P U T")[1]
    part = part.split("P A R T I C I P A T I O N")[0]
    freqs = []
    for s in part.splitlines():
        m = re.match(r"^\s*(\d+)\s+([-+0-9.E]+)\s+([-+0-9.E]+)\s+([-+0-9.E]+)\s+([-+0-9.E]+)\s*$", s)
        if m:
            freqs.append(float(m.group(4)))
    return freqs


# ============================================================================================
# post-processing
# ============================================================================================
def von_mises(S):
    sxx, syy, szz, sxy, syz, szx = S.T
    return np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + syz ** 2 + szx ** 2))


def principal(S):
    T = np.zeros((len(S), 3, 3))
    T[:, 0, 0], T[:, 1, 1], T[:, 2, 2] = S[:, 0], S[:, 1], S[:, 2]
    T[:, 0, 1] = T[:, 1, 0] = S[:, 3]
    T[:, 1, 2] = T[:, 2, 1] = S[:, 4]
    T[:, 0, 2] = T[:, 2, 0] = S[:, 5]
    return np.linalg.eigvalsh(T)          # ascending


def where(X, n):
    x, y, z = X[n]
    post = next((i + 1 for i, (px, py) in enumerate(POSTS) if abs(x - px) <= PW / 2 + 0.01 and abs(y - py) <= PW / 2 + 0.01), None)
    region = ("plate" if z < Z_ROOT - 0.01 else "post root (z = 6)" if z < Z_ROOT + 0.01
              else "nut slot" if Z_M3_SLOT - 0.1 <= z <= Z_M3_SLOT + P["m3_nut_slot_h"] + 0.1
              else "post" if post else "collar/plate")
    return dict(node=int(n), xyz=[round(float(v), 2) for v in (x, y, z)], post=post, region=region)


def section_props(core: bool) -> dict:
    """Area and second moments of the rounded 10 mm post, walls and core, by rasterising."""
    h = 0.005
    u = np.arange(-PW / 2 + h / 2, PW / 2, h)
    x, y = np.meshgrid(u, u, indexing="ij")
    a, r = PW / 2, POST_R
    cx, cy = np.clip(np.abs(x), a - r, None), np.clip(np.abs(y), a - r, None)
    inside = (cx - (a - r)) ** 2 + (cy - (a - r)) ** 2 <= r ** 2
    hc = PW / 2 - WALL_T
    in_core = (np.abs(x) < hc) & (np.abs(y) < hc)
    dA = h * h
    out = {}
    for name, m in (("all", inside), ("core", inside & in_core), ("walls", inside & ~in_core)):
        out[name] = dict(A=float(m.sum() * dA), I=float((x[m] ** 2).sum() * dA),
                         Idiag=float((((x[m] + y[m]) / math.sqrt(2)) ** 2).sum() * dA))
    rho_diag = float(np.max(np.abs(x[inside] + y[inside]) / math.sqrt(2)))
    out["c"] = PW / 2
    out["c_diag"] = rho_diag
    return out


def analytic(mat: dict, sec: dict) -> dict:
    """Beam theory for one post: a cantilever from the plate (z = 6) to the top face (z = 102.16)."""
    Ew, Ec = mat["E_wall"], mat["E_core"]
    Iw, Ic = sec["walls"]["I"], sec["core"]["I"]
    EI = Ew * Iw + Ec * Ic
    Aw, Ac = sec["walls"]["A"], sec["core"]["A"]
    EA = Ew * Aw + Ec * Ac
    mprime = mat["rho_wall"] * Aw + mat["rho_core"] * Ac          # t/mm
    L = POST_L
    F_v = sum(MASSES_KG.values()) * G * DYN / 4
    F_h = F_LAT / 4
    M_root = F_h * L
    sig_root = M_root * sec["c"] * Ew / EI                        # outer wall fibre
    sig_root_diag = M_root * sec["c_diag"] * Ew / (Ew * sec["walls"]["Idiag"] + Ec * sec["core"]["Idiag"])
    lam = 1.8751040687
    f1 = lam ** 2 / (2 * math.pi) * math.sqrt(EI / (mprime * L ** 4))
    # The same cantilever with the real mass distribution: the printed core stops at z = 86, so
    # the top 16 mm is solid (heavier, stiffer). 1-D Euler-Bernoulli FE, 200 Hermite elements.
    segs = [(Z_ROOT, Z_CORE_TOP, EI, mprime),
            (Z_CORE_TOP, Z_POST_TOP, Ew * sec["all"]["I"], mat["rho_wall"] * sec["all"]["A"])]
    f1_seg = beam_f1(segs)
    # Axial stress through the post, and through the net section at the nut slot:
    # the 5.8 mm channel from the axis out through the face, plus the half hexagon inboard.
    a_slot = sec["all"]["A"] - (P["m3_nut_slot_w"] * PW / 2 + 0.5 * (math.sqrt(3) / 2) * P["m3_nut_slot_w"] ** 2)
    return dict(
        F_vertical_per_post_N=F_v, F_lateral_per_post_N=F_h, L_mm=L,
        A_mm2=sec["all"]["A"], I_solid_mm4=sec["all"]["I"], I_walls_mm4=Iw, I_core_mm4=Ic, EI_Nmm2=EI,
        axial_stress_post_MPa=-F_v * Ew / EA, axial_stress_nut_slot_net_MPa=-F_v / a_slot, A_net_slot_mm2=a_slot,
        euler_buckling_per_post_N=math.pi ** 2 * EI / (4 * L ** 2),
        euler_buckling_factor=math.pi ** 2 * EI / (4 * L ** 2) / F_v,
        top_deflection_vertical_mm=F_v * L / EA,
        M_root_Nmm=M_root, sigma_root_bending_MPa=sig_root, sigma_root_bending_diagonal_MPa=sig_root_diag,
        top_deflection_lateral_mm=F_h * L ** 3 / (3 * EI),
        f1_cantilever_Hz=f1, f1_cantilever_solid_top_Hz=f1_seg, mass_per_length_g_per_mm=mprime * 1e6,
    )


def beam_f1(segs, n=200) -> float:
    """First bending frequency (Hz) of a clamped-free Euler-Bernoulli beam with piecewise EI, m'."""
    from scipy.linalg import eigh
    z0, z1 = segs[0][0], segs[-1][1]
    zs = np.linspace(z0, z1, n + 1)
    K, M = np.zeros((2 * n + 2,) * 2), np.zeros((2 * n + 2,) * 2)
    for e in range(n):
        h, zm = zs[e + 1] - zs[e], 0.5 * (zs[e] + zs[e + 1])
        EI, m = next((s[2], s[3]) for s in segs if s[0] <= zm <= s[1])
        k = EI / h ** 3 * np.array([[12, 6 * h, -12, 6 * h], [6 * h, 4 * h * h, -6 * h, 2 * h * h],
                                    [-12, -6 * h, 12, -6 * h], [6 * h, 2 * h * h, -6 * h, 4 * h * h]])
        mm = m * h / 420 * np.array([[156, 22 * h, 54, -13 * h], [22 * h, 4 * h * h, 13 * h, -3 * h * h],
                                     [54, 13 * h, 156, -22 * h], [-13 * h, -3 * h * h, -22 * h, 4 * h * h]])
        i = slice(2 * e, 2 * e + 4)
        K[i, i] += k
        M[i, i] += mm
    w2 = eigh(K[2:, 2:], M[2:, 2:], eigvals_only=True, subset_by_index=[0, 0])[0]
    return math.sqrt(w2) / (2 * math.pi)


def static_summary(job, X, frd, dat, mesh, loads) -> dict:
    blocks = read_frd(frd)
    U = as_array(next(b for b in blocks if b["name"] == "DISP"), X.shape[0] - 1)[:, :3]
    S = as_array(next(b for b in blocks if b["name"] == "STRESS"), X.shape[0] - 1)[:, :6]
    used = mesh["used"]
    um = np.linalg.norm(U[used], axis=1)
    vm = von_mises(S[used])
    pr = principal(S[used])
    szz = S[used, 2]
    z = X[used, 2]
    applied = np.sum(list(loads.values()), axis=0)
    rf = np.array(dat_total_force(dat))

    # sigma_zz on the tension face of the posts, 10 mm above the root (clear of the corner), vs beam theory.
    def band(z0):
        vals = []
        for (px, py) in POSTS:
            m = (np.abs(X[used, 2] - z0) < 0.6) & (np.abs(X[used, 1] - py) < 2.5) & (np.abs(X[used, 0] - (px - PW / 2)) < 0.02)
            if m.any():
                vals.append(float(np.mean(szz[m])))
        return vals

    posts_mask = z > Z_ROOT + 0.01
    i_vm, i_p1, i_u = int(np.argmax(vm)), int(np.argmax(pr[:, 2])), int(np.argmax(um))
    i_zz = int(np.argmax(np.where(posts_mask, szz, -np.inf)))
    i_zz_all = int(np.argmax(szz))
    away = z > Z_ROOT + 2.0          # 2 mm clear of the root corner
    i_vm_away = int(np.argmax(np.where(away, vm, -np.inf)))
    # Guards against a bad solve: global equilibrium, and no isolated nodal spikes (the corrupt
    # multithreaded-SPOOLES results balanced exactly but had 99 MPa nodes next to 2 MPa ones).
    eq_err = float(np.abs(applied + rf).max())
    spike = float(vm[i_vm] / np.percentile(vm, 99.9))
    if eq_err > 1e-4 * max(1.0, float(np.abs(applied).max())) or spike > 10:
        raise RuntimeError(f"{job}: suspicious solution (equilibrium error {eq_err:.3g} N, "
                           f"max/p99.9 von Mises {spike:.1f})")
    return dict(
        applied_force_N=applied.round(6).tolist(), reaction_force_N=rf.round(6).tolist(),
        equilibrium_error_N=eq_err, vm_max_over_p999=round(spike, 2),
        max_displacement_mm=float(um[i_u]), max_displacement_at=where(X, used[i_u]),
        max_von_mises_MPa=float(vm[i_vm]), max_von_mises_at=where(X, used[i_vm]),
        max_von_mises_2mm_above_root_MPa=float(vm[i_vm_away]), max_von_mises_2mm_above_root_at=where(X, used[i_vm_away]),
        max_principal_MPa=float(pr[i_p1, 2]), max_principal_at=where(X, used[i_p1]),
        min_principal_MPa=float(pr[:, 0].min()),
        max_szz_tension_in_posts_MPa=float(szz[i_zz]), max_szz_tension_in_posts_at=where(X, used[i_zz]),
        max_szz_tension_anywhere_MPa=float(szz[i_zz_all]), max_szz_tension_anywhere_at=where(X, used[i_zz_all]),
        szz_tension_face_z16_per_post_MPa=[round(v, 4) for v in band(Z_ROOT + 10.0)],
        szz_tension_face_z56_per_post_MPa=[round(v, 4) for v in band(Z_ROOT + 50.0)],
        mean_top_displacement_mm=np.mean([U[np.unique(t)].mean(axis=0) for t in mesh["tops"].values()], axis=0).round(5).tolist(),
        _vm_nodes=(used, vm, U),
    )


def plot(mesh, used, vm, U, png: Path, title: str, scale: float) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    from matplotlib.colors import LinearSegmentedColormap

    X = mesh["X"]
    V = np.zeros(X.shape[0])
    V[used] = vm
    tri = mesh["skin"]
    Xd = X + scale * np.nan_to_num(U)
    val = V[tri].mean(axis=1)
    vmax = float(np.percentile(V[used], 99.9))
    # One-hue sequential ramp (light = low stress), on a light chart surface with neutral ink.
    cmap = LinearSegmentedColormap.from_list("blue_seq", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                                                          "#256abf", "#184f95", "#0d366b"])
    plt.rcParams.update({"text.color": "#0b0b0b", "axes.labelcolor": "#52514e",
                         "xtick.color": "#52514e", "ytick.color": "#52514e"})
    fig = plt.figure(figsize=(8.4, 4.2), dpi=110, facecolor="#fcfcfb")
    # Zoom: one post root, cropped above the plate top so the plate's side faces don't clutter it.
    views = ((None, "whole base"), ((PC - 10, PC + 10, -PC - 10, -PC + 10, Z_ROOT - 0.05, 30), "post root at (+47, -47)"))
    for k, (box, sub) in enumerate(views):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d", facecolor="#fcfcfb")
        t = tri
        if box:
            c = X[tri].mean(axis=1)
            m = ((c[:, 0] > box[0]) & (c[:, 0] < box[1]) & (c[:, 1] > box[2]) & (c[:, 1] < box[3])
                 & (c[:, 2] > box[4]) & (c[:, 2] < box[5]))
            t, vv = tri[m], val[m]
        else:
            vv = val
        pc = Poly3DCollection(Xd[t], facecolors=cmap(np.clip(vv / vmax, 0, 1)), edgecolors="none", linewidths=0)
        ax.add_collection3d(pc)
        P3 = Xd[t].reshape(-1, 3)
        lo, hi = P3.min(axis=0), P3.max(axis=0)
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
        ax.set_box_aspect(hi - lo)
        ax.view_init(elev=22, azim=-58)
        ax.set_axis_off()
        ax.set_title(sub, fontsize=9)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, vmax))
    cb = fig.colorbar(sm, ax=fig.axes, shrink=0.7, pad=0.02)
    cb.set_label("von Mises (MPa), clipped at the 99.9th percentile", fontsize=8, color="#52514e")
    cb.ax.tick_params(labelsize=7, colors="#52514e")
    fig.suptitle(title, fontsize=9)
    fig.savefig(png, dpi=110, facecolor="#fcfcfb", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


# ============================================================================================
PLOT_SCALE = 20.0


def plot_title(s: dict) -> str:
    return (f"Walls + 25 % infill core model, 10 N lateral (+X) shared by the post tops, displacements x{PLOT_SCALE:.0f};\n"
            f"peak {s['max_von_mises_MPa']:.2f} MPa at a post-root corner (mesh-dependent: sharp re-entrant edge)")


def replot(work: Path, job: str = "printed_b_lateral_x") -> None:
    """Redraw the PNG from base_mesh.msh + the job's .frd, without meshing or solving again."""
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.open(str(work / "base_mesh.msh"))
    ntags, xyz, _ = gmsh.model.mesh.getNodes()
    X = np.zeros((int(ntags.max()) + 1, 3))
    X[ntags.astype(np.int64)] = xyz.reshape(-1, 3)
    skin = [enodes[0].reshape(-1, 6)[:, :3].astype(np.int64)
            for d, t in gmsh.model.getEntities(2) if len(gmsh.model.getAdjacencies(2, t)[0]) == 1
            for types, _, enodes in [gmsh.model.mesh.getElements(2, t)] if len(types)]
    gmsh.finalize()
    blocks = read_frd(work / f"{job}.frd")
    U = as_array(next(b for b in blocks if b["name"] == "DISP"), X.shape[0] - 1)[:, :3]
    S = as_array(next(b for b in blocks if b["name"] == "STRESS"), X.shape[0] - 1)[:, :6]
    used = np.where(~np.isnan(S[:, 0]))[0]
    vm = von_mises(S[used])
    res = json.loads((work / "results.json").read_text())["runs"][job]
    plot(dict(X=X, skin=np.vstack(skin)), used, vm, U, work / "von_mises_lateral_x.png", plot_title(res), PLOT_SCALE)
    print("wrote", work / "von_mises_lateral_x.png")


def main() -> None:
    import threading
    from concurrent.futures import ThreadPoolExecutor

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--size", type=float, default=4.0, help="global element size (mm)")
    ap.add_argument("--post", type=float, default=1.6, help="element size in the posts (mm)")
    ap.add_argument("--root", type=float, default=0.6, help="element size at the post roots (mm)")
    ap.add_argument("--slot", type=float, default=0.6, help="element size at the nut slots (mm)")
    ap.add_argument("--jobs", type=int, default=3, help="ccx jobs side by side (~3 GB each; modal ~5 GB, one at a time)")
    ap.add_argument("--materials", default=",".join(MATERIALS), help="comma list of: " + ", ".join(MATERIALS))
    ap.add_argument("--cases", default="a_vertical,b_lateral_x,b_lateral_diag,c_modal")
    ap.add_argument("--tag", default="default")
    ap.add_argument("--out", type=Path, default=Path("/tmp/fea/out"))  # .frd files run to 130 MB each
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--replot", action="store_true", help="only redraw the PNG from an earlier run's files")
    args = ap.parse_args()
    if args.replot:
        return replot(args.out / args.tag)
    if not shutil.which("ccx"):
        raise SystemExit("ccx not on PATH: sudo apt-get install -y calculix-ccx")

    t_all = time.time()
    work = args.out / args.tag
    work.mkdir(parents=True, exist_ok=True)
    mesh = build_mesh(args, work)
    write_mesh_inp(mesh, work / "mesh.inp")
    X = mesh["X"]
    print("mesh:", json.dumps(mesh["stats"]), flush=True)

    sec = section_props(core=True)
    m_total = sum(MASSES_KG.values())
    F_v = m_total * G * DYN
    d = 1 / math.sqrt(2)
    loads_all = {
        "a_vertical": np.array([[0, 0, -F_v / 4]] * 4),
        "b_lateral_x": np.array([[F_LAT / 4, 0, 0]] * 4),
        "b_lateral_diag": np.array([[F_LAT / 4 * d, F_LAT / 4 * d, 0]] * 4),
        "c_modal": None,
    }
    mats = [m for m in args.materials.split(",") if m]
    cases = [c for c in args.cases.split(",") if c]
    results = dict(
        inputs=dict(step=str(STEP_FILE), post_length_mm=POST_L, z_post_top=Z_POST_TOP, z_nut_slot=Z_M3_SLOT,
                    wall_thickness_mm=WALL_T, infill=INFILL, core_z=[Z_ROOT, Z_CORE_TOP], masses_kg=MASSES_KG,
                    total_mass_kg=m_total, dynamic_factor=DYN, F_vertical_total_N=F_v, F_lateral_total_N=F_LAT,
                    materials=MATERIALS, strength_MPa=STRENGTH, ccx=subprocess.run(
                        ["ccx", "-v"], capture_output=True, text=True).stdout.strip()),
        mesh=mesh["stats"], section=sec, model_mass_g={}, runs={}, analytic={}, timing_s={})
    st = mesh["stats"]
    for m in mats:
        mat = MATERIALS[m]
        results["analytic"][m] = analytic(mat, sec)
        results["model_mass_g"][m] = round(1e6 * (mat["rho_wall"] * st["walls_volume_mm3"]
                                                  + mat["rho_core"] * st["core_volume_mm3"]), 1)

    jobs = []
    for m in mats:
        for c in cases:
            name = f"{m}_{c}"
            loads = face_loads(mesh, loads_all[c]) if loads_all[c] is not None else None
            write_job(work, name, MATERIALS[m], loads)
            jobs.append((name, m, c, loads))
    jobs.sort(key=lambda j: j[2] != "c_modal")          # start the long modal jobs first
    modal_lock = threading.Semaphore(1)
    threads = max(1, (os.cpu_count() or 1) // max(1, args.jobs))

    def run(job):
        name, m, c, loads = job
        if c == "c_modal":
            with modal_lock:
                dt = run_ccx(work, name, threads)
        else:
            dt = run_ccx(work, name, threads)
        print(f"{name}: {dt:.1f} s", flush=True)
        return name, dt

    t_ccx = time.time()
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for name, dt in ex.map(run, jobs):
            results["timing_s"][name] = round(dt, 1)
    results["timing_s"]["ccx_wall_total"] = round(time.time() - t_ccx, 1)

    for name, m, c, loads in sorted(jobs):
        if c == "c_modal":
            freqs = dat_frequencies(work / f"{name}.dat")
            blocks = [b for b in read_frd(work / f"{name}.frd") if b["name"] == "DISP"]
            modes = []
            for b, fr in zip(blocks, freqs):
                U = np.nan_to_num(as_array(b, X.shape[0] - 1)[:, :3])
                n = int(np.argmax(np.linalg.norm(U, axis=1)))
                top = [float(np.linalg.norm(U[np.unique(t)].mean(axis=0))) for i, t in sorted(mesh["tops"].items())]
                ux, uy = np.abs(U[mesh["used"], 0]).mean(), np.abs(U[mesh["used"], 1]).mean()
                modes.append(dict(f_Hz=round(fr, 2), max_at=where(X, n), dominant="X" if ux > uy else "Y",
                                  post_top_motion=[round(v / max(top), 3) for v in top]))
            results["runs"][name] = dict(frequencies_Hz=[round(v, 2) for v in freqs], modes=modes)
            continue
        s = static_summary(name, X, work / f"{name}.frd", work / f"{name}.dat", mesh, loads)
        used, vm, U = s.pop("_vm_nodes")
        zz = s["max_szz_tension_in_posts_MPa"]
        s["safety_factors"] = {
            "interlayer_Z_TDS_31MPa_on_max_szz": STRENGTH["Z_TDS"] / zz if zz > 0 else None,
            "interlayer_Z_design_15MPa_on_max_szz": STRENGTH["Z_design"] / zz if zz > 0 else None,
            "XY_35MPa_on_max_von_mises": STRENGTH["XY"] / s["max_von_mises_MPa"],
        }
        results["runs"][name] = s
        if m == "printed" and c == "b_lateral_x" and not args.no_plot:
            plot(mesh, used, vm, U, work / "von_mises_lateral_x.png", plot_title(s), PLOT_SCALE)
    results["timing_s"]["total"] = round(time.time() - t_all, 1)
    (work / "results.json").write_text(json.dumps(results, indent=2, default=float) + "\n")
    print("wrote", work / "results.json", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pod-to-bracket joint: how far the HQ Camera moves under its own inertia, old joint vs new.

OLD is the pod on an ~11 x 40 mm strip with 2 x M3 (commit 66763fc, its exports read with
git show); NEW is the 45 deg seat with 4 x M3 (../exports). For each, bracket + pod are
fragmented together in gmsh, so the tet mesh shares nodes across their contact face: a bonded
joint, i.e. a preloaded bolted joint that neither slips nor opens (the screws themselves are
not modelled). Linear elastic, quadratic (P2) tets in scikit-fem, PLA taken solid and isotropic
(E = 2.4 GPa, nu = 0.35). Infill and layer lines make a print softer, so the absolute numbers
are a lower bound; the old/new ratio is the point.

Fixed: the half-collar bore, and the pad face within 7 mm of each tab screw. Load: the HQ Camera
+ 6 mm lens (83 g) at 1 g along world X, Y and Z in turn, as a uniform traction on the end faces
of the HQ's four bosses. Out, per case: the mean displacement of those faces, the tilt of the HQ
optical axis from a best-fit rigid motion of them, and that tilt as image shift at the 6 mm lens.
Also a Rayleigh-Ritz estimate of the first natural frequency (printed parts' mass, plus the
camera's spread over the boss faces), from the three static deflections.

    pip install gmsh scikit-fem pyamg pyvista     # gmsh needs libGLU: apt install libglu1-mesa
    python piper-camera-mount/sim/joint_fea.py    # -> sim/joint_fea.json, renders/joint_fea.png
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
import time
from collections import Counter
from dataclasses import fields
from pathlib import Path

import gmsh
import numpy as np
import pyamg
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import cg
from skfem import (Basis, BilinearForm, ElementTetP2, ElementVector, FacetBasis, Functional, LinearForm, MeshTet,
                   asm)
from skfem.models.elasticity import lame_parameters, linear_elasticity

HERE = Path(__file__).resolve().parent
MOUNT = HERE.parent
sys.path.insert(0, str(MOUNT / "cad"))
from piper_mount import Params, optical_axes, station_vec  # noqa: E402

OLD_REV = "66763fc"
E, NU = 2400.0, 0.35            # MPa: PLA, solid
RHO = 1.24e-9                   # t/mm^3 (1.24 g/cm^3)
M_CAM = 0.083                   # kg: HQ Camera + 6 mm lens
G = 9.80665
PIXEL = 1.55e-3                 # mm, IMX477
H_MAX, H_MIN = 3.0, 0.8         # mm, tet size
PAD_R, BOSS_R = 7.0, 4.0        # mm: pad patch round each tab screw; boss face round each boss centre
DIRS = "XYZ"


def load_params(text: str) -> Params:
    names = {f.name for f in fields(Params)}
    return Params(**{k: v for k, v in json.loads(text).items() if k in names})


def sources(tmp: Path) -> dict:
    """{design: (bracket STEP, pod STEP, Params it was built with)}"""
    for name in ("bracket.step", "pod.step", "params.json"):
        out = subprocess.run(["git", "show", f"{OLD_REV}:piper-camera-mount/exports/{name}"], cwd=MOUNT,
                             check=True, capture_output=True).stdout
        (tmp / f"old_{name}").write_bytes(out)
    ex = MOUNT / "exports"
    return {"old": (tmp / "old_bracket.step", tmp / "old_pod.step", load_params((tmp / "old_params.json").read_text())),
            "new": (ex / "bracket.step", ex / "pod.step", load_params((ex / "params.json").read_text()))}


def mesh_design(steps) -> tuple[MeshTet, float]:
    """One conforming tet mesh of bracket + pod; also the area of the face they share."""
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        vols = []
        for f in steps:
            vols += [e for e in gmsh.model.occ.importShapes(str(f)) if e[0] == 3]
        gmsh.model.occ.fragment(vols[:1], vols[1:])
        gmsh.model.occ.synchronize()
        faces = Counter(abs(t) for _, v in gmsh.model.getEntities(3)
                        for _, t in gmsh.model.getBoundary([(3, v)], oriented=False))
        joint = sum(gmsh.model.occ.getMass(2, s) for s, n in faces.items() if n > 1)
        gmsh.option.setNumber("Mesh.MeshSizeMax", H_MAX)
        gmsh.option.setNumber("Mesh.MeshSizeMin", H_MIN)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
        gmsh.model.mesh.generate(3)
        tags, xyz, _ = gmsh.model.mesh.getNodes()
        _, conn = gmsh.model.mesh.getElementsByType(4)
    finally:
        gmsh.finalize()
    idx = np.zeros(int(tags.max()) + 1, dtype=np.int64)
    idx[tags.astype(np.int64)] = np.arange(len(tags))
    used, t = np.unique(idx[conn.astype(np.int64)], return_inverse=True)
    p, t = xyz.reshape(-1, 3)[used].T, t.reshape(-1, 4).T
    n = p.shape[1]
    adj = sum(coo_matrix((np.ones(t.shape[1]), (t[0], t[k])), shape=(n, n)) for k in (1, 2, 3))
    assert connected_components(adj, directed=False)[0] == 1, "bracket and pod did not bond"
    return MeshTet(np.ascontiguousarray(p), np.ascontiguousarray(t)), joint


def station(p: Params):
    """(origin, rows = station x, y, z axes) in world coordinates."""
    o = np.array(station_vec(p, 0.0, 0.0, 0.0).toTuple())
    return o, np.array([np.array(station_vec(p, *e).toTuple()) - o for e in np.eye(3)])


def boundary_groups(mesh: MeshTet, p: Params):
    """Boundary facets: collar bore, pad patches round the tab screws, HQ boss end faces."""
    bf = mesh.boundary_facets()
    v = mesh.p[:, mesh.facets[:, bf]]
    c = v.mean(axis=1)
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0], axis=0)
    n /= np.linalg.norm(n, axis=0)
    r = np.hypot(c[0] - p.ax_x, c[2] - p.ax_z)
    bore = (abs(r - p.bore_r) < 0.3) & (abs(n[1]) < 0.1) & (c[1] > p.collar_y0) & (c[1] < p.collar_y1)
    d_tab = np.min([np.hypot(c[0] - x, c[2] - z) for x, z in p.tab_holes], axis=0)
    pad = (abs(c[1] - p.collar_y0) < 1e-3) & (abs(n[1]) > 0.999) & (d_tab < PAD_R)
    o, R = station(p)
    s, ns = R @ (c - o[:, None]), R @ n
    h = p.hq_hole_pitch / 2
    d_boss = np.min([np.hypot(s[0] - x, s[2] - z) for x in (-h, h) for z in (-h, h)], axis=0)
    boss = (abs(s[1]) < 1e-3) & (abs(ns[1]) > 0.999) & (d_boss < BOSS_R)
    return bf[bore], bf[pad], bf[boss]


def rigid_fit(x: np.ndarray, u: np.ndarray):
    """Least-squares small rigid motion u ~ a + th x (x - centroid): returns (a, th)."""
    r = x - x.mean(axis=1, keepdims=True)
    A = np.zeros((3 * r.shape[1], 6))
    for i, (rx, ry, rz) in enumerate(r.T):
        A[3 * i:3 * i + 3, :3] = np.eye(3)
        A[3 * i:3 * i + 3, 3:] = [[0, rz, -ry], [-rz, 0, rx], [ry, -rx, 0]]    # -skew(r): th x r
    sol = np.linalg.lstsq(A, u.T.ravel(), rcond=None)[0]
    return sol[:3], sol[3:]


def rigid_modes(ib: Basis) -> np.ndarray:
    """Six rigid-body modes on the vector P2 dofs: AMG's near-nullspace."""
    x, comp = ib.doflocs, np.empty(ib.N, dtype=int)
    for c in range(3):
        comp[ib.nodal_dofs[c]] = c
        comp[ib.edge_dofs[c]] = c
    B = np.zeros((ib.N, 6))
    B[np.arange(ib.N), comp] = 1.0
    for k, (a, b) in enumerate(((1, 2), (2, 0), (0, 1))):        # rotations about x, y, z
        B[comp == a, 3 + k] = -x[b, comp == a]
        B[comp == b, 3 + k] = x[a, comp == b]
    return B


def solve_design(mesh: MeshTet, p: Params) -> dict:
    t0 = time.time()
    e = ElementVector(ElementTetP2())
    ib = Basis(mesh, e, intorder=2)
    K = asm(linear_elasticity(*lame_parameters(E, NU)), ib).tocsr()
    bore, pad, boss = boundary_groups(mesh, p)
    fixed = ib.get_dofs(facets=np.concatenate([bore, pad])).all()
    free = np.setdiff1d(np.arange(ib.N), fixed)
    fb = FacetBasis(mesh, e, facets=boss, intorder=4)
    area = {k: asm(Functional(lambda w: 1.0 + 0.0 * w.x[0]), FacetBasis(mesh, e, facets=f))
            for k, f in (("bore", bore), ("pad", pad), ("boss", boss))}
    F = np.column_stack([asm(LinearForm(lambda v, w, k=k: v.value[k]), fb) for k in range(3)])
    F *= M_CAM * G / area["boss"]                     # N/mm^2, uniform over the boss faces
    Kf = K[free][:, free].tocsr()
    ml = pyamg.smoothed_aggregation_solver(Kf, B=rigid_modes(ib)[free], max_coarse=2000)
    U, iters = np.zeros((ib.N, 3)), []
    for k in range(3):
        res = []
        U[free, k], info = cg(Kf, F[free, k], M=ml.aspreconditioner(), rtol=1e-10, maxiter=2000,
                              callback=lambda xk: res.append(1))
        assert info == 0, f"CG did not converge ({DIRS[k]})"
        iters.append(len(res))
    t_solve = time.time() - t0

    # Boss faces: P2 nodes (vertices + edge midpoints) for the rigid fit, area mean for the displacement.
    fv, fe = np.unique(mesh.facets[:, boss]), np.unique(mesh.f2e[:, boss])
    pts = np.hstack([mesh.p[:, fv], mesh.p[:, mesh.edges[:, fe]].mean(axis=1)])
    dofs = np.hstack([ib.nodal_dofs[:, fv], ib.edge_dofs[:, fe]])
    d = np.array(optical_axes(p)["hq"][1].toTuple())
    cases = {}
    for k in range(3):
        uf = fb.interpolate(U[:, k])
        ubar = np.array([asm(Functional(lambda w, i=i: w.u.value[i]), fb, u=uf) for i in range(3)]) / area["boss"]
        _, th = rigid_fit(pts, U[dofs, k])
        tilt = np.linalg.norm(th - th.dot(d) * d)
        cases[DIRS[k]] = {
            "mean displacement (um)": round(float(np.linalg.norm(ubar)) * 1e3, 3),
            "mean displacement vector (um)": [round(float(c) * 1e3, 3) for c in ubar],
            "optical axis tilt (arcmin)": round(math.degrees(tilt) * 60, 4),
            "roll about the optical axis (arcmin)": round(math.degrees(abs(th.dot(d))) * 60, 4),
            "image shift (px)": round(p.lens_f * math.tan(tilt) / PIXEL, 4),
            "max displacement anywhere (um)": round(float(np.linalg.norm(U[ib.nodal_dofs, k], axis=0).max()) * 1e3, 3),
            "CG iterations": iters[k],
        }

    # Rayleigh-Ritz on the three static deflections: an upper bound on the first natural frequency.
    sb = Basis(mesh, ElementTetP2(), intorder=4)
    mass = BilinearForm(lambda u, v, w: u * v)
    Ms = RHO * asm(mass, sb) + (M_CAM * 1e-3 / area["boss"]) * asm(mass, FacetBasis(mesh, ElementTetP2(),
                                                                                     facets=boss, intorder=4))
    vec_of = np.zeros((3, sb.N), dtype=int)
    vec_of[:, sb.nodal_dofs[0]], vec_of[:, sb.edge_dofs[0]] = ib.nodal_dofs, ib.edge_dofs
    KU = K @ U
    Kr = U.T @ KU
    Mr = sum(U[vec_of[c]].T @ (Ms @ U[vec_of[c]]) for c in range(3))
    lam = np.linalg.eigvals(np.linalg.solve(Mr, Kr)).real.min()
    f1 = math.sqrt(lam) / (2 * math.pi)
    mass_parts = RHO * asm(Functional(lambda w: 1.0 + 0.0 * w.x[0]), sb) * 1e6     # g
    return {
        "mesh": {"nodes (P1)": int(mesh.p.shape[1]), "tets": int(mesh.t.shape[1]), "dofs (P2)": int(ib.N),
                 "free dofs": int(len(free))},
        "areas (mm2)": {k: round(v, 1) for k, v in area.items()},
        "printed mass (g)": round(mass_parts, 1),
        "cases": cases,
        "first natural frequency, Rayleigh-Ritz (Hz)": round(f1, 1),
        "solve time (s)": round(t_solve, 1),
        "_U": U, "_ib": ib,
    }


def render(mesh_u: dict, k: int, out: Path, labels: dict) -> float:
    """Side by side |u| for load case k, same colour scale and exaggeration; returns the factor."""
    import pyvista as pv
    umax = max(np.linalg.norm(u, axis=0).max() for _, u in mesh_u.values())
    scale = 4.0 / umax
    mag = 10 ** math.floor(math.log10(scale))
    scale = max(m * mag for m in (1, 2, 5) if m * mag <= scale)
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(2400, 1150), border=False)
    pl.set_background("white")
    for i, (name, (mesh, u)) in enumerate(mesh_u.items()):
        pl.subplot(0, i)
        g = pv.UnstructuredGrid({pv.CellType.TETRA: mesh.t.T}, mesh.p.T)
        g["u"] = u.T
        g["|u| (um)"] = np.linalg.norm(u, axis=0) * 1e3
        surf = g.extract_surface()
        pl.add_mesh(surf, color="lightgrey", opacity=0.18)
        pl.add_mesh(surf.warp_by_vector("u", factor=scale), scalars="|u| (um)", cmap="viridis",
                    clim=(0, umax * 1e3), show_edges=False, smooth_shading=False,
                    scalar_bar_args={"title": f"displacement (um), 83 g at 1 g along {DIRS[k]}, same scale both sides",
                                     "color": "black",
                                     "vertical": False, "width": 0.6, "position_x": 0.2, "position_y": 0.04,
                                     "fmt": "%.0f"})
        pl.add_text(f"{labels[name]}\ndeformation x {scale:g}, undeformed in grey", position="upper_left",
                    font_size=13, color="black")
        c = np.array(surf.center)
        pl.camera_position = [tuple(c + 260 * np.array([-0.75, -0.45, 0.48])), tuple(c), (0, 0, 1)]
    pl.link_views()
    pl.screenshot(str(out))
    pl.close()
    return scale


def main() -> None:
    t0 = time.time()
    results, fields_u = {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, (bracket, pod, p) in sources(Path(tmp)).items():
            tm = time.time()
            mesh, joint = mesh_design((bracket, pod))
            t_mesh = time.time() - tm
            r = solve_design(mesh, p)
            r["bonded contact area, pod to bracket (mm2)"] = round(joint, 1)
            r["mesh time (s)"] = round(t_mesh, 1)
            fields_u[name] = (mesh, r.pop("_U"), r.pop("_ib"))
            results[name] = r
            print(name, json.dumps(r, indent=1))

    old, new = results["old"]["cases"], results["new"]["cases"]
    ratio = {d: {"displacement old/new": round(old[d]["mean displacement (um)"] / new[d]["mean displacement (um)"], 2),
                 "tilt old/new": round(old[d]["optical axis tilt (arcmin)"] / new[d]["optical axis tilt (arcmin)"], 2)}
             for d in DIRS}
    worst = max(range(3), key=lambda k: old[DIRS[k]]["optical axis tilt (arcmin)"])
    labels = {"old": f"OLD ({OLD_REV}): strip, 2 x M3, "
                     f"{results['old']['bonded contact area, pod to bracket (mm2)']:.0f} mm2 bonded",
              "new": f"NEW: 45 deg seat, 4 x M3, "
                     f"{results['new']['bonded contact area, pod to bracket (mm2)']:.0f} mm2 bonded"}
    mesh_u = {n: (m, U[ib.nodal_dofs, worst]) for n, (m, U, ib) in fields_u.items()}
    scale = render(mesh_u, worst, MOUNT / "renders" / "joint_fea.png", labels)
    out = {
        "what": "HQ Camera motion under its own inertia (83 g at 1 g), pod bonded to bracket; old strip joint "
                f"({OLD_REV}) vs new 45 deg seat",
        "settings": {
            "material": {"E (MPa)": E, "nu": NU, "density (g/cm3)": RHO * 1e9, "note": "solid, isotropic PLA; "
                         "infill and layer lines make a print softer: compare, don't trust the absolute values"},
            "elements": "quadratic tets (P2) on a straight-sided gmsh mesh",
            "mesh size (mm)": {"max": H_MAX, "min": H_MIN, "per 2 pi of curvature": 12},
            "joint": "bracket and pod fragmented to one conforming mesh: bonded, i.e. a preloaded bolted joint "
                     "that neither slips nor opens; screws not modelled",
            "fixed": f"half-collar bore (r = bore_r, y = collar_y0..collar_y1) and pad face y = collar_y0 within "
                     f"{PAD_R} mm of each tab screw",
            "load": f"{M_CAM * 1e3:.0f} g x {G} m/s2 = {M_CAM * G:.3f} N along world X, Y, Z in turn, uniform "
                    f"traction on the HQ boss end faces (station y = 0, within {BOSS_R} mm of each boss centre)",
            "tilt": "best-fit small rigid rotation of the boss-face P2 nodes, component normal to the optical axis",
            "image shift": f"lens_f * tan(tilt) / {PIXEL * 1e3} um",
            "solver": "pyamg smoothed aggregation (rigid-body near-nullspace) + CG, rtol 1e-10",
            "frequency": "Rayleigh-Ritz on the X, Y, Z static deflections (an upper bound); printed-part density + "
                         "camera mass spread over the boss faces",
        },
        "old": results["old"], "new": results["new"], "old/new": ratio,
        "render": {"file": "renders/joint_fea.png", "load case": DIRS[worst], "deformation scale": scale},
        "run time (s)": round(time.time() - t0, 1),
    }
    (HERE / "joint_fea.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(ratio, indent=1), "\nrun time", out["run time (s)"], "s")


if __name__ == "__main__":
    main()

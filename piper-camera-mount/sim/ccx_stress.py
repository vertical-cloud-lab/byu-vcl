#!/usr/bin/env python3
"""Stresses in the printed parts, solved in CalculiX (ccx), plus a check of ccx against joint_fea.py.

Same meshes and supports as joint_fea.py: gmsh tets, fragmented so bracket + pod share nodes
(bonded), made quadratic by adding a node at each edge midpoint. ccx's C3D10 on that mesh is the
same element space as scikit-fem's P2, so on the three joint_fea.py load cases the two solvers
should agree to solver precision. That is the check. Then the stress cases:

  pod bump  bracket + pod, collar bore and pad fixed as in joint_fea.py; 10 N spread over the pod's
            outer edge face along world +X (toward the gripper), +Y (toward the arm) and +Z. The
            pod is the widest thing on the wrist, 96 mm out, so it is what hits a rack upright.
  yank      the carrier alone, its half-collar bore fixed; 10 N at the Pi 5's USB-C plug (10 mm out
            from the socket) along +X (off the board), +Y (straight out of the socket) and +Z,
            carried to the four standoff seats as through a rigid board.

The clamp is in ccx_split.py, which puts both half-collars in one model so that the split can close.

Linear elastic PLA as in joint_fea.py (E = 2.4 GPa, nu = 0.35). The stress for a given load hardly
depends on E, so the numbers stand for any of the materials; compare them with each material's
strength, across the layers where the stress crosses them. Out: sim/ccx_stress.json and
renders/ccx_stress.png.

    sudo apt install calculix-ccx          # CalculiX 2.21
    pip install gmsh scikit-fem pyamg pyvista
    xvfb-run -a python piper-camera-mount/sim/ccx_stress.py [--keep DIR] [--skfem]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

import gmsh
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from skfem import MeshTet

HERE = Path(__file__).resolve().parent
MOUNT = HERE.parent
sys.path.insert(0, str(MOUNT / "cad"))
sys.path.insert(0, str(HERE))
from joint_fea import (DIRS, E, G, H_MAX, H_MIN, M_CAM, NU, PIXEL, boundary_groups, load_params,  # noqa: E402
                       rigid_fit, station)
from piper_mount import Params, optical_axes, pi_holes  # noqa: E402

EX = MOUNT / "exports"
BUMP_N = 10.0          # N, each bump and yank case; everything here is linear, so scale freely
YANK_LEVER = 10.0      # mm, socket mouth to where the plug is gripped
PU0 = -42.5            # piper_mount.PI_U0
# Print orientation (build direction) per part, from the README's Printing table.
BUILD = {"bracket": "world Y (pad face down)", "pod": "station Y (plate face down)", "carrier": "world X (Pi plate face down)"}


# --- mesh -------------------------------------------------------------------------------------

def mesh_parts(steps: dict[str, Path]) -> tuple[MeshTet, np.ndarray, float]:
    """One conforming P1 tet mesh of the named STEPs (fragmented, so shared faces share nodes),
    the part index of every tet, and the area of the faces the parts share."""
    names = list(steps)
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        per = [[e for e in gmsh.model.occ.importShapes(str(steps[n])) if e[0] == 3] for n in names]
        flat = [v for vs in per for v in vs]
        owner = [i for i, vs in enumerate(per) for _ in vs]
        if len(flat) > 1:
            _, out_map = gmsh.model.occ.fragment(flat[:1], flat[1:])
        else:
            out_map = [flat]
        gmsh.model.occ.synchronize()
        vol_part = {}
        for i, ents in enumerate(out_map):
            for d, t in ents:
                if d == 3:
                    vol_part.setdefault(t, owner[i])
        faces = Counter(abs(t) for _, v in gmsh.model.getEntities(3)
                        for _, t in gmsh.model.getBoundary([(3, v)], oriented=False))
        joint = sum(gmsh.model.occ.getMass(2, s) for s, n in faces.items() if n > 1)
        gmsh.option.setNumber("Mesh.MeshSizeMax", H_MAX)
        gmsh.option.setNumber("Mesh.MeshSizeMin", H_MIN)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
        gmsh.model.mesh.generate(3)
        tags, xyz, _ = gmsh.model.mesh.getNodes()
        conn, lab = [], []
        for _, v in gmsh.model.getEntities(3):
            types, _, nodes = gmsh.model.mesh.getElements(3, v)
            for ty, nd in zip(types, nodes):
                if ty == 4:
                    conn.append(nd)
                    lab.append(np.full(len(nd) // 4, vol_part[v]))
    finally:
        gmsh.finalize()
    conn, lab = np.concatenate(conn), np.concatenate(lab)
    idx = np.zeros(int(tags.max()) + 1, dtype=np.int64)
    idx[tags.astype(np.int64)] = np.arange(len(tags))
    used, t = np.unique(idx[conn.astype(np.int64)], return_inverse=True)
    p, t = xyz.reshape(-1, 3)[used].T, t.reshape(-1, 4).T
    n = p.shape[1]
    adj = sum(coo_matrix((np.ones(t.shape[1]), (t[0], t[k])), shape=(n, n)) for k in (1, 2, 3))
    assert connected_components(adj, directed=False)[0] == 1, "the parts did not bond into one mesh"
    return MeshTet(np.ascontiguousarray(p), np.ascontiguousarray(t)), lab, joint


class Quadratic:
    """C3D10 on a P1 MeshTet: node i < N is vertex i, node N + e the midpoint of edge e. scikit-fem's
    t2e lists a tet's edges as (0,1) (1,2) (0,2) (0,3) (1,3) (2,3), which is ccx's C3D10 order."""

    def __init__(self, mesh: MeshTet):
        self.mesh = mesh
        self.N = mesh.p.shape[1]
        mid = mesh.p[:, mesh.edges].mean(axis=1)
        self.x = np.hstack([mesh.p, mid]).T                         # (N + E, 3)
        self.el = np.vstack([mesh.t, self.N + mesh.t2e]).T          # (M, 10), 0-based

    def facet_nodes(self, facets: np.ndarray) -> np.ndarray:
        return np.unique(np.concatenate([self.mesh.facets[:, facets].ravel(),
                                         self.N + self.mesh.f2e[:, facets].ravel()]))

    def traction(self, facets: np.ndarray, force: np.ndarray) -> dict[int, np.ndarray]:
        """Consistent nodal forces for `force` (N, total) spread uniformly over `facets`. On a
        straight 6-node triangle a uniform traction goes 1/3 to each midside node, 0 to corners."""
        v = self.mesh.p[:, self.mesh.facets[:, facets]]
        a = 0.5 * np.linalg.norm(np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0], axis=0), axis=0)
        out: dict[int, np.ndarray] = {}
        for k in range(3):
            for e, ai in zip(self.mesh.f2e[k, facets], a):
                n = self.N + int(e)
                out[n] = out.get(n, 0.0) + force * ai / a.sum() / 3.0
        return out


def facet_geometry(mesh: MeshTet, facets: np.ndarray):
    """Centroids, unit normals and areas. Normals point out of the tet on the facet's first side,
    i.e. outward on a boundary facet (scikit-fem stores facet vertices sorted, so their order
    says nothing about which side the solid is on)."""
    v = mesh.p[:, mesh.facets[:, facets]]
    c = v.mean(axis=1)
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0], axis=0)
    a = 0.5 * np.linalg.norm(n, axis=0)
    n = n / (2 * a)
    tet = mesh.t[:, mesh.f2t[0, facets]]
    inside = mesh.p[:, tet].mean(axis=1)                  # the tet's centroid is on the solid side
    n *= np.where(np.einsum("ij,ij->j", n, c - inside) < 0, -1.0, 1.0)
    return c, n, a


# --- ccx --------------------------------------------------------------------------------------

def write_deck(path: Path, q: Quadratic, fixed: dict[int, tuple[int, ...]], steps: list[dict],
               transforms: dict[str, np.ndarray] | None = None, prescribed: dict[int, float] | None = None,
               print_nset: str | None = None, nsets: dict[str, np.ndarray] | None = None):
    """fixed: node -> dofs held at 0. steps: [{'name', 'loads': {node: force}}]. transforms: nset
    name -> node list put in a cylindrical frame about the J6 axis (dof 1 radial, 2 tangential).
    prescribed: node -> radial displacement (needs the node in a transform)."""
    with path.open("w") as f:
        f.write("*HEADING\nPiPER camera mount, ccx_stress.py\n*NODE, NSET=NALL\n")
        np.savetxt(f, np.column_stack([np.arange(1, len(q.x) + 1), q.x]), fmt="%d, %.6f, %.6f, %.6f")
        f.write("*ELEMENT, TYPE=C3D10, ELSET=EALL\n")
        np.savetxt(f, np.column_stack([np.arange(1, len(q.el) + 1), q.el + 1]), fmt="%d" + ", %d" * 10)
        for name, nodes in (nsets or {}).items():
            f.write(f"*NSET, NSET={name}\n")
            np.savetxt(f, np.asarray(nodes) + 1, fmt="%d")
        for name, nodes in (transforms or {}).items():
            f.write(f"*NSET, NSET={name}\n")
            np.savetxt(f, np.asarray(nodes) + 1, fmt="%d")
            p = Params()
            # ccx cylindrical frame: points a, b on the axis; dof 1 radial, 2 tangential, 3 axial
            f.write(f"*TRANSFORM, NSET={name}, TYPE=C\n{p.ax_x}, 0, {p.ax_z}, {p.ax_x}, 1, {p.ax_z}\n")
        f.write(f"*MATERIAL, NAME=PLA\n*ELASTIC\n{E}, {NU}\n*SOLID SECTION, ELSET=EALL, MATERIAL=PLA\n")
        f.write("*BOUNDARY\n")
        for n, dofs in fixed.items():
            for d in dofs:
                f.write(f"{n + 1}, {d}, {d}, 0.\n")
        for n, u in (prescribed or {}).items():
            f.write(f"{n + 1}, 1, 1, {u:.6e}\n")
        for s in steps:
            f.write(f"*STEP\n*STATIC, SOLVER={os.environ.get('CCX_SOLVER', 'SPOOLES')}\n*CLOAD, OP=NEW\n")
            for n, F in s["loads"].items():
                for d in range(3):
                    if F[d] != 0.0:
                        f.write(f"{n + 1}, {d + 1}, {F[d]:.8e}\n")
            f.write("*NODE FILE\nU, S\n")
            if print_nset:
                f.write(f"*NODE PRINT, NSET={print_nset}, GLOBAL=YES\nRF\n")
            f.write("*END STEP\n")


def run_ccx(deck: Path) -> float:
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS=str(os.cpu_count()), CCX_NPROC_EQUATION_SOLVER=str(os.cpu_count()))
    r = subprocess.run(["ccx", "-i", deck.stem], cwd=deck.parent, capture_output=True, text=True, env=env)
    if r.returncode != 0 or "*ERROR" in r.stdout:
        raise RuntimeError(f"ccx failed:\n{r.stdout[-3000:]}\n{r.stderr[-2000:]}")
    return time.time() - t0


def read_frd(path: Path, n_nodes: int) -> list[dict[str, np.ndarray]]:
    """The DISP and STRESS blocks of an ASCII .frd, one dict per step, rows in node order."""
    steps: list[dict[str, np.ndarray]] = []
    block, rows = None, None
    with path.open() as f:
        for line in f:
            if line.startswith(" -4"):
                name = line[5:13].strip()
                ncomp = {"DISP": 3, "STRESS": 6}.get(name)
                block = name if ncomp else None
                if block:
                    rows = np.zeros((n_nodes, ncomp))
            elif line.startswith(" -1") and block:
                i = int(line[3:13]) - 1
                vals = line[13:].rstrip("\n")
                rows[i] = [float(vals[12 * k:12 * k + 12]) for k in range(rows.shape[1])]
            elif line.startswith(" -3") and block:
                if block == "DISP":
                    steps.append({})
                steps[-1][block] = rows
                block = None
    return steps


def read_rf(path: Path) -> list[dict[int, np.ndarray]]:
    """Reaction forces from the .dat file (only nodes that carry one are listed)."""
    out, cur = [], None
    for line in path.read_text().splitlines():
        if line.strip().startswith("forces (fx,fy,fz)"):
            cur = {}
            out.append(cur)
        elif cur is not None and line.strip():
            parts = line.split()
            if len(parts) == 4:
                try:
                    cur[int(parts[0]) - 1] = np.array([float(v) for v in parts[1:]])
                except ValueError:
                    cur = None
    return out


# --- stress measures ---------------------------------------------------------------------------

def tensor(s: np.ndarray) -> np.ndarray:
    """ccx order SXX SYY SZZ SXY SYZ SZX -> (n, 3, 3)."""
    xx, yy, zz, xy, yz, zx = s.T
    return np.stack([np.stack([xx, xy, zx], -1), np.stack([xy, yy, yz], -1), np.stack([zx, yz, zz], -1)], -2)


def measures(s: np.ndarray, build: np.ndarray) -> dict[str, np.ndarray]:
    """von Mises, max and min principal, and the normal stress across the layers (build: (n, 3))."""
    T = tensor(s)
    ev = np.linalg.eigvalsh(T)
    xx, yy, zz, xy, yz, zx = s.T
    vm = np.sqrt(0.5 * ((xx - yy) ** 2 + (yy - zz) ** 2 + (zz - xx) ** 2) + 3 * (xy ** 2 + yz ** 2 + zx ** 2))
    layer = np.einsum("ni,nij,nj->n", build, T, build)
    return {"vm": vm, "p1": ev[:, 2], "p3": ev[:, 0], "layer": layer}


def summarise(m: dict[str, np.ndarray], keep: np.ndarray, x: np.ndarray, part: np.ndarray, names: list[str],
              sign: float = 1.0) -> dict:
    """Peaks over the nodes in `keep` (away from the supports), for the load or its reverse (sign -1:
    the tensor flips, so the largest tension becomes -min principal)."""
    out = {}
    vm = m["vm"]
    t1 = m["p1"] if sign > 0 else -m["p3"]
    lay = sign * m["layer"]
    for key, arr in (("von Mises (MPa)", vm), ("max principal (MPa)", t1), ("tension across layers (MPa)", lay)):
        best = {}
        for k, name in enumerate(names):
            sel = keep & (part == k)
            if sel.any():
                i = np.flatnonzero(sel)[np.argmax(arr[sel])]
                best[name] = {"value": round(float(arr[i]), 3), "at (mm)": [round(float(c), 1) for c in x[i]]}
        out[key] = best
    return out


def node_parts(q: Quadratic, lab: np.ndarray) -> np.ndarray:
    part = np.full(len(q.x), -1)
    for k in np.unique(lab):
        part[np.unique(q.el[lab == k])] = k
    return part


def away_from(x: np.ndarray, fixed_nodes: np.ndarray, r: float) -> np.ndarray:
    from scipy.spatial import cKDTree
    d, _ = cKDTree(x[fixed_nodes]).query(x, k=1)
    return d > r


# --- cases ------------------------------------------------------------------------------------

def facet_part(mesh: MeshTet, lab: np.ndarray, facets: np.ndarray) -> np.ndarray:
    return lab[mesh.f2t[0, facets]]


def seat_forces(p: Params, force: np.ndarray, point: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """A force at `point`, carried by a rigid board to the four standoff seats (equal, isotropic
    supports): f_i = F / 4 + (J^-1 M) x r_i. Returns (seat centres, forces), both (4, 3)."""
    x = p.carrier_x0 + p.carrier_t
    c = np.array([[x, y, z] for y, z in pi_holes(p)])
    cbar = c.mean(axis=0)
    r = c - cbar
    J = sum(np.dot(ri, ri) * np.eye(3) - np.outer(ri, ri) for ri in r)
    th = np.linalg.solve(J, np.cross(point - cbar, force))
    f = force / 4 + np.cross(th, r)
    assert np.allclose(f.sum(axis=0), force) and np.allclose(np.cross(r, f).sum(axis=0), np.cross(point - cbar, force))
    return c, f


def radial(x: np.ndarray, p: Params) -> np.ndarray:
    d = np.column_stack([x[:, 0] - p.ax_x, np.zeros(len(x)), x[:, 2] - p.ax_z])
    return d / np.linalg.norm(d, axis=1)[:, None]


def solve_steps(work: Path, name: str, q: Quadratic, fixed, steps, **kw):
    """Write and run one deck. With --keep, a deck identical to the one already there (and its
    results) is not run again, so a re-run only solves what changed."""
    work.mkdir(parents=True, exist_ok=True)
    deck, new = work / f"{name}.inp", work / f"{name}.inp.new"
    write_deck(new, q, fixed, steps, **kw)
    frd = work / f"{name}.frd"
    if deck.exists() and frd.exists() and frd.stat().st_size and deck.read_bytes() == new.read_bytes():
        new.unlink()
        return read_frd(frd, len(q.x)), 0.0
    new.replace(deck)
    dt = run_ccx(deck)
    return read_frd(frd, len(q.x)), dt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skfem", action="store_true", help="re-solve joint_fea.py's cases in scikit-fem on this mesh "
                                                           "(about 5 min) instead of comparing with joint_fea.json")
    ap.add_argument("--keep", help="keep the ccx decks and results in this directory")
    args = ap.parse_args()
    t_all = time.time()
    p = load_params((EX / "params.json").read_text())
    work = Path(args.keep) if args.keep else Path(tempfile.mkdtemp(prefix="ccx_"))
    out: dict = {"what": "CalculiX (ccx 2.21) stress analysis of the printed parts, and a check of ccx against "
                         "joint_fea.py (scikit-fem) on the same mesh",
                 "settings": {"material": {"E (MPa)": E, "nu": NU, "note": "solid, isotropic PLA as in joint_fea.py; "
                                           "stress for a given load hardly depends on E, so compare the stresses "
                                           "with any material's strength"},
                              "elements": "C3D10 (quadratic tets) on joint_fea.py's gmsh mesh, midside nodes at the "
                                          "edge midpoints",
                              "solver": "ccx SPOOLES", "print orientation (layers normal to)": BUILD}}

    # 1. bracket + pod: joint_fea.py's three cases (the check) and the three bumps, one deck.
    mesh, lab, joint = mesh_parts({"bracket": EX / "bracket.step", "pod": EX / "pod.step"})
    q = Quadratic(mesh)
    bore, pad, boss = boundary_groups(mesh, p)
    fixed_nodes = q.facet_nodes(np.concatenate([bore, pad]))
    fixed = {int(k): (1, 2, 3) for k in fixed_nodes}
    o, R = station(p)
    bf = mesh.boundary_facets()
    c, n, a = facet_geometry(mesh, bf)
    s, ns = R @ (c - o[:, None]), R @ n
    edge = bf[(abs(s[0] - p.pod_x_out) < 0.05) & (ns[0] < -0.99) & (facet_part(mesh, lab, bf) == 1)]
    edge_area = float(facet_geometry(mesh, edge)[2].sum())
    steps = [{"name": f"HQ 1 g {d}", "loads": q.traction(boss, M_CAM * G * np.eye(3)[k])} for k, d in enumerate(DIRS)]
    steps += [{"name": f"bump {d}", "loads": q.traction(edge, BUMP_N * np.eye(3)[k])} for k, d in enumerate(DIRS)]
    res, dt = solve_steps(work, "bracket_pod", q, fixed, steps)
    d_opt = np.array(optical_axes(p)["hq"][1].toTuple())
    cb, _, ab = facet_geometry(mesh, boss)
    mids = q.N + mesh.f2e[:, boss]
    fv, fe = np.unique(mesh.facets[:, boss]), np.unique(mesh.f2e[:, boss])
    pts = np.hstack([mesh.p[:, fv], mesh.p[:, mesh.edges[:, fe]].mean(axis=1)])
    check = {}
    for k, dname in enumerate(DIRS):
        U = res[k]["DISP"]
        ubar = (U[mids].mean(axis=0) * ab[:, None]).sum(axis=0) / ab.sum()
        _, th = rigid_fit(pts, np.vstack([U[fv], U[q.N + fe]]).T)
        tilt = np.linalg.norm(th - th.dot(d_opt) * d_opt)
        check[dname] = {"mean displacement (um)": float(np.linalg.norm(ubar)) * 1e3,
                        "optical axis tilt (arcmin)": math.degrees(tilt) * 60,
                        "image shift (px)": p.lens_f * math.tan(tilt) / PIXEL,
                        "max displacement anywhere (um)": float(np.linalg.norm(U, axis=1).max()) * 1e3}
    ref = json.loads((HERE / "joint_fea.json").read_text())["new"]
    same_mesh = ref["mesh"]["nodes (P1)"] == mesh.p.shape[1] and ref["mesh"]["tets"] == mesh.t.shape[1]
    if args.skfem or same_mesh:
        if args.skfem:
            from joint_fea import solve_design
            sk = solve_design(mesh, p)["cases"]
        else:
            sk = ref["cases"]                       # rounded as joint_fea.json prints them
        for dname in DIRS:
            for key in ("mean displacement (um)", "optical axis tilt (arcmin)", "max displacement anywhere (um)"):
                v_ccx = check[dname][key]
                check[dname][key] = {"ccx": round(v_ccx, 5), "scikit-fem": sk[dname][key],
                                     "scikit-fem from": "re-solved on this mesh" if args.skfem else
                                     "joint_fea.json (the same mesh: same node and tet counts)",
                                     "difference (%)": round(100 * (v_ccx - sk[dname][key]) / sk[dname][key], 3)}
    part = node_parts(q, lab)
    names = ["bracket", "pod"]
    build = np.zeros((len(q.x), 3))
    build[part == 0] = [0, 1, 0]
    build[part == 1] = R[1]
    keep = away_from(q.x, fixed_nodes, 2.0)
    bump = {}
    viz = {}
    for k, dname in enumerate(DIRS):
        m = measures(res[3 + k]["STRESS"], build)
        for sign, tag in ((1, "+"), (-1, "-")):
            bump[f"{tag}{dname}"] = summarise(m, keep, q.x, part, names, sign)
        viz[dname] = (res[3 + k]["DISP"], m)
    hq1g = {}
    for k, dname in enumerate(DIRS):
        m = measures(res[k]["STRESS"], build)
        hq1g[dname] = {"max von Mises (MPa)": round(float(m["vm"][keep].max()), 4)}
    out["bracket + pod"] = {
        "mesh": {"nodes (C3D10)": len(q.x), "elements": len(q.el), "bonded contact area (mm2)": round(joint, 1)},
        "fixed": "half-collar bore and the pad round the tab screws, as joint_fea.py",
        "check against joint_fea.py (83 g at 1 g on the HQ bosses)": check,
        "HQ Camera at 1 g, stress": hq1g,
        "bump": {"load": f"{BUMP_N} N spread over the pod's outer edge face ({edge_area:.0f} mm2), along world +X "
                         "(toward the gripper), +Y (toward the arm), +Z; the reverse directions are the same "
                         "solutions with the sign flipped",
                 "peaks (at least 2 mm from the supports)": bump},
        "ccx time (s)": round(dt, 1),
    }
    viz_bp = (q, viz, lab)
    print(json.dumps(out["bracket + pod"]["check against joint_fea.py (83 g at 1 g on the HQ bosses)"], indent=1))

    # 2. carrier alone: the yank at the Pi 5's USB-C.
    mesh_c, lab_c, _ = mesh_parts({"carrier": EX / "carrier.step"})
    qc = Quadratic(mesh_c)
    bore_c, _, _ = boundary_groups(mesh_c, p)
    fix_c = qc.facet_nodes(bore_c)
    bfc = mesh_c.boundary_facets()
    cc, nc, ac = facet_geometry(mesh_c, bfc)
    plug = np.array([p.pi_x + 1.6 + 3.3 / 2, p.y_max + 1.0 + YANK_LEVER, p.ax_z + PU0 + (6.7 + 15.7) / 2])
    seats = []
    x_seat = p.carrier_x0 + p.carrier_t
    for y, z in pi_holes(p):
        r = np.hypot(cc[1] - y, cc[2] - z)
        sel = (abs(cc[0] - x_seat) < 0.05) & (nc[0] > 0.99) & (r < 3.0 + 0.05)
        assert sel.any(), f"no standoff seat at y={y}, z={z:.1f}"
        seats.append(bfc[sel])
    ysteps, seat_f = [], {}
    for k, dname in enumerate(DIRS):
        F = BUMP_N * np.eye(3)[k]
        _, f = seat_forces(p, F, plug)
        seat_f[dname] = [[round(float(v), 2) for v in fi] for fi in f]
        loads: dict[int, np.ndarray] = {}
        for fac, fi in zip(seats, f):
            for kk, v in qc.traction(fac, fi).items():
                loads[kk] = loads.get(kk, 0.0) + v
        ysteps.append({"name": f"yank {dname}", "loads": loads})
    res_c, dt_c = solve_steps(work, "carrier", qc, {int(k): (1, 2, 3) for k in fix_c}, ysteps)
    part_c = np.zeros(len(qc.x), dtype=int)
    build_c = np.tile([1.0, 0.0, 0.0], (len(qc.x), 1))
    keep_c = away_from(qc.x, fix_c, 2.0)
    yank, viz_y = {}, {}
    for k, dname in enumerate(DIRS):
        m = measures(res_c[k]["STRESS"], build_c)
        for sign, tag in ((1, "+"), (-1, "-")):
            yank[f"{tag}{dname}"] = summarise(m, keep_c, qc.x, part_c, ["carrier"], sign)
        viz_y[dname] = (res_c[k]["DISP"], m)
    out["carrier: cable yank"] = {
        "mesh": {"nodes (C3D10)": len(qc.x), "elements": len(qc.el)},
        "fixed": "the carrier's half-collar bore (clamped to the body)",
        "load": f"{BUMP_N} N at the USB-C plug, {YANK_LEVER} mm out from the socket, at "
                f"{[round(float(v), 1) for v in plug]} mm; through a rigid board to the four standoff seats "
                "(O6 mm) on the carrier's outer face",
        "forces on the four seats (N)": seat_f,
        "peaks (at least 2 mm from the bore)": yank,
        "ccx time (s)": round(dt_c, 1),
    }

    out["clamp"] = "see ccx_split.py and ccx_split.json: both halves in one model, so the split can close"
    out["run time (s)"] = round(time.time() - t_all, 1)
    (HERE / "ccx_stress.json").write_text(json.dumps(out, indent=2) + "\n")
    render(viz_bp, (qc, viz_y))
    print(json.dumps({k: v for k, v in out.items() if k not in ("settings",)}, indent=1)[:6000])
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)


def render(bp, yank) -> None:
    import pyvista as pv

    def surface(q: Quadratic, val: np.ndarray, label: str):
        g = pv.UnstructuredGrid({pv.CellType.QUADRATIC_TETRA: q.el}, q.x)
        g.point_data[label] = val
        return g.extract_surface(nonlinear_subdivision=2, algorithm="dataset_surface")

    q, viz, lab = bp
    qc, viz_y = yank
    worst_b = max(DIRS, key=lambda d: viz[d][1]["vm"].max())
    worst_y = max(DIRS, key=lambda d: viz_y[d][1]["vm"].max())
    panels = [
        (q, viz[worst_b][1]["vm"], f"Pod bumped: {BUMP_N:g} N on its outer edge along {worst_b}\nbracket + pod",
         "pod bump", (-0.55, 0.45, 0.70), 1.3),
        (qc, viz_y[worst_y][1]["vm"], f"Cable yank: {BUMP_N:g} N at the USB-C plug along {worst_y}\n"
         "carrier, seen from the gripper side", "cable yank", (-0.55, 0.62, 0.55), 1.0),
    ]
    pl = pv.Plotter(off_screen=True, shape=(1, 2), window_size=(1600, 1050), border=False)
    pl.set_background("white")
    for i, (qq, val, title, tag, view, zoom) in enumerate(panels):
        pl.subplot(0, i)
        label = f"von Mises (MPa), {tag}"
        surf = surface(qq, val, label)
        top = float(np.percentile(val, 99.8))
        pl.add_mesh(surf, scalars=label, cmap="viridis", clim=(0, top), show_edges=False,
                    scalar_bar_args={"title": f"{label}\n(colours stop at the 99.8th percentile)",
                                     "color": "black", "vertical": False, "width": 0.8, "position_x": 0.1,
                                     "position_y": 0.04, "fmt": "%.3g", "title_font_size": 18,
                                     "label_font_size": 16, "n_labels": 4})
        pl.add_text(title, position="upper_left", font_size=13, color="black")
        c = np.array(surf.center)
        pl.camera_position = [tuple(c + 300 * np.array(view)), tuple(c), (0, 0, 1)]
        pl.reset_camera()
        pl.camera.zoom(zoom)
    pl.screenshot(str(MOUNT / "renders" / "ccx_stress.png"))
    pl.close()


if __name__ == "__main__":
    main()

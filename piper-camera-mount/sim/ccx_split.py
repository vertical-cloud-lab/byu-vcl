#!/usr/bin/env python3
"""The clamp's split as a stop: both half-collars in one CalculiX model, the screws tightened past snug.

ccx_stress.py solves each half-collar on its own round a rigid body. That is right while the split is
open, but once it closes the halves push on each other, so here both halves go into one deck. It is
run for the 1.0 mm split the collar had and the 0.6 mm it has now. Both use one mesh, the 0.6 mm
parts' (from piper_mount.py), with the split faces moved 0.2 mm apart for the 1.0 mm: the peaks sit
at the sharp ear roots, where the value depends on the mesh, so those are meshed identically.

  body    rigid O57, frictionless, 0.15 mm clear all round: an active set of radial constraints on
          both bores, as in ccx_stress.py.
  split   frictionless too: an active set of stiff springs (SPRING2, along X) from each node of the
          bracket's split face to the point of the carrier's split face opposite it, which is tied to
          that facet's six nodes by an *EQUATION. Each half is first moved half the split toward the
          other, so the two faces start together and the width of the split goes into the radial
          constraints instead (a rigid shift strains nothing). Nodes on the bore's edge are left out:
          they carry the cylindrical frame, and that edge is the last place to close.
  screws  F in each of the four M3s, on the carrier's counterbore floors and the bracket's
          nut-pocket floors, as in ccx_stress.py.

F steps up to 1000 N per screw, each step starting from the last one's contact sets. Linear elastic,
solid, isotropic PLA as in joint_fea.py, so past PLA's strength the numbers say where it would
break, not what it would do next. Out: sim/ccx_split.json, renders/split_closeup.png,
renders/split_overtighten.png and renders/split_overtighten.gif.

    sudo apt install calculix-ccx          # CalculiX 2.21
    pip install cadquery gmsh scikit-fem pyvista matplotlib pillow
    xvfb-run -a python piper-camera-mount/sim/ccx_split.py [--keep DIR] [--plot-only]
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
MOUNT = HERE.parent
sys.path.insert(0, str(MOUNT / "cad"))
sys.path.insert(0, str(HERE))
from ccx_stress import (Quadratic, away_from, facet_geometry, measures, mesh_parts, radial,  # noqa: E402
                        read_frd, read_rf, summarise)
from joint_fea import E, NU, boundary_groups, load_params  # noqa: E402

EX = MOUNT / "exports"
RENDERS = MOUNT / "renders"
GAPS = (1.0, 0.6)                   # mm: the split as it was, and as it is now
MESH_GAP = 0.6                      # every design is meshed as this one, its split faces then moved
MORPH_BAND = 3.0                    # mm: nodes this close to a split face move with it, tapering off
FORCES = (50, 100, 150, 200, 250, 300, 400, 500, 650, 800, 1000)     # N per M3
K_SPLIT = 1e5                       # N/mm per split-face spring: the faces overlap by under 1 um
MAX_ITER = 40
TOUCH = 1e-3                        # mm: a split-face node this close to the other face is touching
BUILD = {0: [0.0, 1.0, 0.0], 1: [1.0, 0.0, 0.0]}     # print direction: bracket world Y, carrier world X
NAMES = ["bracket", "carrier"]


# --- geometry and mesh ----------------------------------------------------------------------------

def run_ccx(deck: Path) -> float:
    """As ccx_stress.run_ccx, but CCX_THREADS sets the threads, so both designs can solve at once."""
    t0 = time.time()
    n = os.environ.get("CCX_THREADS", str(os.cpu_count()))
    env = dict(os.environ, OMP_NUM_THREADS=n, CCX_NPROC_EQUATION_SOLVER=n)
    r = subprocess.run(["ccx", "-i", deck.stem], cwd=deck.parent, capture_output=True, text=True, env=env)
    if r.returncode != 0 or "*ERROR" in r.stdout:
        raise RuntimeError(f"ccx failed:\n{r.stdout[-3000:]}\n{r.stderr[-2000:]}")
    return time.time() - t0


def build_halves(p, work: Path) -> dict[str, Path]:
    """bracket.step and carrier.step for this split_gap, from piper_mount.py (world frame)."""
    import cadquery as cq
    from piper_mount import make_bracket, make_carrier
    out = {}
    for name, make in (("bracket", make_bracket), ("carrier", make_carrier)):
        f = work / f"{name}_split{p.split_gap:.2f}.step"
        if not f.exists():
            cq.exporters.export(make(p), str(f))
        out[name] = f
    return out


def morph(mesh, p, side: int, gap0: float):
    """Move a half's split face from where gap0 puts it to where p.split_gap does. Nodes within
    MORPH_BAND of the face move along X, all the way at the face and not at all at MORPH_BAND, so
    the rest of the mesh (the ear roots, where the peaks sit, and the screw seats) is untouched."""
    from skfem import MeshTet
    x = mesh.p.copy()
    face = p.ax_x + side * gap0 / 2
    x[0] += side * (p.split_gap - gap0) / 2 * np.clip(1 - abs(x[0] - face) / MORPH_BAND, 0, None)
    return MeshTet(x, mesh.t)


def screw_loads(q: Quadratic, p, side: int) -> dict[int, np.ndarray]:
    """Nodal loads for 1 N in each M3: carrier, on the counterbore floors under the heads (pushed -X);
    bracket, on the nut-pocket floors (pulled +X). Both toward the other half, as ccx_stress.py."""
    mesh = q.mesh
    bf = mesh.boundary_facets()
    c, n, _ = facet_geometry(mesh, bf)
    x_face = p.ax_x + p.clamp_head_seat if side > 0 else p.ax_x - p.ear_w + p.m3_nut_depth
    loads: dict[int, np.ndarray] = {}
    for y in p.clamp_y:
        for sz in (1, -1):
            z = p.ax_z + sz * p.clamp_r
            r = np.hypot(c[1] - y, c[2] - z)
            sel = (abs(c[0] - x_face) < 0.05) & (n[0] * side > 0.99) & (r > p.m3_clear_d / 2 - 0.05) & (r < 3.4)
            assert sel.any(), f"no bearing face for the M3 at y={y}, z={z:.1f}"
            for k, v in q.traction(bf[sel], np.array([-side * 1.0, 0.0, 0.0])).items():
                loads[k] = loads.get(k, 0.0) + v
    return loads


def split_faces(q: Quadratic, p, side: int) -> np.ndarray:
    bf = q.mesh.boundary_facets()
    c, n, _ = facet_geometry(q.mesh, bf)
    xs = p.ax_x + side * p.split_gap / 2
    return bf[(abs(c[0] - xs) < 0.05) & (n[0] * side < -0.99)]


def split_pairs(qb: Quadratic, sb: np.ndarray, bore_b: np.ndarray, qc: Quadratic, sc: np.ndarray,
                bore_c: np.ndarray):
    """For each node of the bracket's split face, the carrier split-face facet opposite it (in y, z)
    and the six quadratic shape functions there. Returns (slave nodes, (n, 6) master nodes, (n, 6)
    weights), carrier-local master numbering."""
    mc = qc.mesh
    slaves = np.setdiff1d(qb.facet_nodes(sb), bore_b)
    on_bore = np.zeros(len(qc.x), bool)
    on_bore[bore_c] = True
    six = np.vstack([mc.facets[:, sc], qc.N + mc.f2e[:, sc]])          # (6, F)
    keep = sc[~on_bore[six].any(axis=0)]
    corners = mc.facets[:, keep]
    yz = qc.x[:, 1:]
    tree = cKDTree(yz[corners].mean(axis=0))
    S, M, W = [], [], []
    for s in slaves:
        pt = qb.x[s, 1:]
        _, cand = tree.query(pt, k=min(12, len(keep)))
        for j in np.atleast_1d(cand):
            a, b, c = yz[corners[:, j]]
            l2, l3 = np.linalg.solve(np.column_stack([b - a, c - a]), pt - a)
            L = np.array([1 - l2 - l3, l2, l3])
            if L.min() < -1e-6:
                continue
            f = keep[j]
            vs = list(mc.facets[:, f])
            nodes = vs + [qc.N + int(e) for e in mc.f2e[:, f]]
            w = [L[i] * (2 * L[i] - 1) for i in range(3)]
            for e in mc.f2e[:, f]:
                i, k = (vs.index(v) for v in mc.edges[:, e])
                w.append(4 * L[i] * L[k])
            S.append(s)
            M.append(nodes)
            W.append(w)
            break
    return np.array(S), np.array(M), np.array(W)


class Model:
    """Both halves in one node numbering: bracket first, then carrier. `x` is the shifted frame
    (each half moved split_gap / 2 toward the other); x + U is where the material really ends up."""

    def __init__(self, p, work: Path):
        self.p = p
        steps = build_halves(replace(p, split_gap=MESH_GAP), work)
        halves = []
        for name, side in (("bracket", -1), ("carrier", 1)):
            mesh, _, _ = mesh_parts({name: steps[name]})
            mesh = morph(mesh, p, side, MESH_GAP)
            q = Quadratic(mesh)
            bore, _, _ = boundary_groups(mesh, p)
            halves.append((q, side, q.facet_nodes(bore), split_faces(q, p, side), screw_loads(q, p, side)))
        (qb, _, bb, sb, lb), (qc, _, bc, sc, lc) = halves
        self.halves = halves
        self.Nb = Nb = len(qb.x)
        g = p.split_gap / 2
        self.x_real = np.vstack([qb.x, qc.x])
        self.x = np.vstack([qb.x + [g, 0, 0], qc.x - [g, 0, 0]])
        self.el = np.vstack([qb.el, qc.el + Nb])
        self.part = np.r_[np.zeros(len(qb.x), int), np.ones(len(qc.x), int)]
        self.unit = {**{k: v for k, v in lb.items()}, **{k + Nb: v for k, v in lc.items()}}
        self.bore = np.r_[bb, bc + Nb]
        self.rhat = radial(self.x[self.bore], p)
        self.r0 = np.hypot(self.x[self.bore, 0] - p.ax_x, self.x[self.bore, 2] - p.ax_z)
        # One crown node per half held tangentially and axially (a frictionless body leaves those
        # free), and the first guess at contact: 30 degrees either side of each crown.
        self.crowns, self.start = [], set()
        for (q, side, bn, _, _), off in zip(halves, (0, Nb)):
            xr = q.x[bn]
            crown = bn[np.argmin(np.linalg.norm(xr - [p.ax_x + side * p.bore_r, (p.collar_y0 + p.collar_y1) / 2,
                                                      p.ax_z], axis=1))]
            self.crowns.append(int(crown + off))
            ang = np.degrees(np.arctan2(xr[:, 2] - p.ax_z, side * (xr[:, 0] - p.ax_x)))
            self.start |= set((bn[abs(ang) < 30] + off).tolist())
        S, M, W = split_pairs(qb, sb, bb, qc, sc, bc)
        self.S, self.M, self.W = S, M + Nb, W
        self.split_b = sb
        self.load_nodes = np.array(list(self.unit))
        self.build = np.array([BUILD[k] for k in self.part])

    def write_deck(self, path: Path, F: float, bore_on: set, pairs_on: np.ndarray) -> int:
        p = self.p
        n = len(self.x)
        virt = n + np.arange(len(pairs_on))                     # one node per active spring
        with path.open("w") as f:
            f.write("*HEADING\nPiPER camera mount, ccx_split.py\n*NODE, NSET=NALL\n")
            np.savetxt(f, np.column_stack([np.arange(1, n + 1), self.x]), fmt="%d, %.6f, %.6f, %.6f")
            if len(virt):
                np.savetxt(f, np.column_stack([virt + 1, self.x[self.S[pairs_on]]]), fmt="%d, %.6f, %.6f, %.6f")
            f.write("*ELEMENT, TYPE=C3D10, ELSET=EALL\n")
            np.savetxt(f, np.column_stack([np.arange(1, len(self.el) + 1), self.el + 1]), fmt="%d" + ", %d" * 10)
            if len(virt):
                f.write("*ELEMENT, TYPE=SPRING2, ELSET=ESPLIT\n")
                ids = len(self.el) + 1 + np.arange(len(virt))
                np.savetxt(f, np.column_stack([ids, self.S[pairs_on] + 1, virt + 1]), fmt="%d, %d, %d")
            f.write("*NSET, NSET=NBORE\n")
            np.savetxt(f, self.bore + 1, fmt="%d")
            f.write(f"*TRANSFORM, NSET=NBORE, TYPE=C\n{p.ax_x}, 0, {p.ax_z}, {p.ax_x}, 1, {p.ax_z}\n")
            if len(virt):
                f.write("*EQUATION\n")
                for v, i in zip(virt, pairs_on):
                    terms = [(v, 1.0)] + [(m, -w) for m, w in zip(self.M[i], self.W[i]) if abs(w) > 1e-12]
                    f.write(f"{len(terms)}\n")
                    for k in range(0, len(terms), 4):
                        f.write(", ".join(f"{a + 1}, 1, {c:.10e}" for a, c in terms[k:k + 4]) + "\n")
            f.write(f"*MATERIAL, NAME=PLA\n*ELASTIC\n{E}, {NU}\n*SOLID SECTION, ELSET=EALL, MATERIAL=PLA\n")
            if len(virt):
                f.write(f"*SPRING, ELSET=ESPLIT\n1, 1\n{K_SPLIT:.6e}\n")
            f.write("*BOUNDARY\n")
            for c in self.crowns:
                f.write(f"{c + 1}, 2, 3, 0.\n")
            for v in virt:
                f.write(f"{v + 1}, 2, 3, 0.\n")
            for i, k in enumerate(self.bore):
                if int(k) in bore_on:
                    f.write(f"{k + 1}, 1, 1, {p.body_r - self.r0[i]:.8e}\n")
            f.write(f"*STEP\n*STATIC, SOLVER={os.environ.get('CCX_SOLVER', 'SPOOLES')}\n*CLOAD\n")
            for k, v in self.unit.items():
                f.write(f"{k + 1}, 1, {F * v[0]:.8e}\n")
            f.write("*NODE FILE\nU, S\n*NODE PRINT, NSET=NBORE, GLOBAL=YES\nRF\n*END STEP\n")
        return n + len(virt)

    def solve(self, work: Path, F: float, bore_on: set, pairs_on: set, tag: str):
        """Active-set loop at one screw force, from the given contact sets."""
        hist = []
        for it in range(MAX_ITER):
            on = np.array(sorted(pairs_on), dtype=int)
            deck = work / f"{tag}_{it}.inp"
            ntot = self.write_deck(deck, F, bore_on, on)
            dt = run_ccx(deck)
            res = read_frd(deck.with_suffix(".frd"), ntot)[0]
            U, S = res["DISP"][:len(self.x)], res["STRESS"][:len(self.x)]
            rf = read_rf(deck.with_suffix(".dat"))[0]
            for ext in (".inp", ".frd", ".dat", ".sta", ".cvg", ".12d"):
                if not os.environ.get("CCX_SPLIT_KEEP"):
                    deck.with_suffix(ext).unlink(missing_ok=True)
            # the body: drop nodes it pulls on, add nodes pushed into it
            ur = np.einsum("ij,ij->i", U[self.bore], self.rhat)
            R = np.array([rf.get(int(k), np.zeros(3)) @ self.rhat[i] for i, k in enumerate(self.bore)])
            tol_r = 1e-3 * max(1.0, float(abs(R).max()))
            act = np.array([int(k) in bore_on for k in self.bore])
            drop_b = set(self.bore[act & (R < -tol_r)].tolist())
            add_b = set(self.bore[~act & (self.r0 + ur < self.p.body_r - 1e-4)].tolist())
            # the split: gap from the bracket's face to the carrier's, at each pair
            gap = (self.W * U[self.M, 0]).sum(axis=1) - U[self.S, 0]
            act_s = np.zeros(len(self.S), bool)
            act_s[on] = True
            fs = -K_SPLIT * gap * act_s                              # compression > 0
            tol_s = 1e-3 * max(1.0, float(fs.max()))
            drop_s = set(np.flatnonzero(act_s & (fs < -tol_s)).tolist())
            add_s = set(np.flatnonzero(~act_s & (gap < -1e-4)).tolist())
            hist.append({"iteration": it, "body nodes": len(bore_on), "split nodes": len(pairs_on),
                         "changes": len(drop_b) + len(add_b) + len(drop_s) + len(add_s), "ccx (s)": round(dt, 1)})
            print(f"  {tag} it {it}: body {len(bore_on)} -{len(drop_b)} +{len(add_b)}, split {len(pairs_on)} "
                  f"-{len(drop_s)} +{len(add_s)}, gap {gap.min():.4f}, {dt:.0f} s", flush=True)
            if not (drop_b or add_b or drop_s or add_s):
                break
            bore_on = (bore_on - drop_b) | add_b
            pairs_on = (pairs_on - drop_s) | add_s
        converged = not (drop_b or add_b or drop_s or add_s)
        return U, S, rf, R, gap, fs, bore_on, pairs_on, hist, converged


# --- one design, all forces ----------------------------------------------------------------------

def touching_area(model: Model, gap: np.ndarray) -> float:
    """Area of the bracket split-face facets whose every paired node is within TOUCH of the carrier."""
    qb = model.halves[0][0]
    g = np.full(len(qb.x), np.inf)
    g[model.S] = gap
    sb = model.split_b
    six = np.vstack([qb.mesh.facets[:, sb], qb.N + qb.mesh.f2e[:, sb]])
    gs = g[six]
    ok = np.isfinite(gs).all(axis=0) & (gs < TOUCH).all(axis=0)
    _, _, a = facet_geometry(qb.mesh, sb)
    return float(a[ok].sum())


def run_design(gap_mm: float, work: Path, forces) -> tuple[dict, dict]:
    p = replace(load_params((EX / "params.json").read_text()), split_gap=gap_mm)
    t0 = time.time()
    model = Model(p, work)
    out = {"split (mm)": gap_mm,
           "mesh": {"nodes (C3D10)": len(model.x), "elements": len(model.el),
                    "bracket split-face nodes paired with the carrier's face": len(model.S)},
           "forces": {}}
    viz = {"x": model.x, "x_real": model.x_real, "el": model.el, "part": model.part, "gap": gap_mm, "U": {},
           "p1": {}, "vm": {}, "seats": model.load_nodes, "params": p}
    bore_on, pairs_on = set(model.start), set()
    keep = away_from(model.x, model.load_nodes, 1.5)
    top = model.x[model.S, 2] > p.ax_z
    for F in forces:
        U, S, rf, R, gap, fs, bore_on, pairs_on, hist, ok = model.solve(work, F, bore_on, pairs_on,
                                                                         f"g{gap_mm:.1f}_F{F:.0f}")
        m = measures(S, model.build)
        i_min = int(np.argmin(gap))
        grip, push = [], []
        for k, (q, side, bn, _, _) in enumerate(model.halves):
            sel = model.part[model.bore] == k
            grip.append(round(float(np.clip(R[sel], 0, None).sum()), 1))
            push.append(round(float(sum(rf.get(int(n), np.zeros(3))[0] for n in model.bore[sel])), 1))
        out["forces"][f"{F:.0f}"] = {
            "converged": ok, "iterations": len(hist), "ccx (s)": round(sum(h["ccx (s)"] for h in hist), 1),
            "split gap (mm)": {"narrowest": round(float(gap.min()), 4), "widest": round(float(gap.max()), 4),
                               "mean": round(float(gap.mean()), 4),
                               "narrowest at (y, z mm)": [round(float(v), 1) for v in model.x[model.S[i_min], 1:]]},
            "split face in contact over whole facets (mm2)": round(touching_area(model, gap), 1),
            "split contact force (N)": {"total": round(float(fs.sum()), 1), "top ears": round(float(fs[top].sum()), 1),
                                        "bottom ears": round(float(fs[~top].sum()), 1)},
            "body: radial contact force, summed (N)": dict(zip(NAMES, grip)),
            "body: net push along X (N)": dict(zip(NAMES, push)),
            "peaks away from the screw seats": summarise(m, keep, model.x_real, model.part, NAMES),
        }
        viz["U"][F] = U.astype(np.float32)
        viz["p1"][F] = m["p1"].astype(np.float32)
        viz["vm"][F] = m["vm"].astype(np.float32)
        r = out["forces"][f"{F:.0f}"]
        print(f"split {gap_mm} mm, F {F:4.0f} N: gap {r['split gap (mm)']['narrowest']:.3f}..."
              f"{r['split gap (mm)']['widest']:.3f} mm, contact {r['split contact force (N)']['total']:7.1f} N, "
              f"grip {grip}, p1 {r['peaks away from the screw seats']['max principal (MPa)']}, "
              f"{len(hist)} it, {time.time() - t0:.0f} s", flush=True)
    return out, viz


# --- main ------------------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keep", help="keep the built STEPs and each design's results here (and, with "
                                   "CCX_SPLIT_KEEP=1, the decks)")
    ap.add_argument("--forces", type=float, nargs="*", default=FORCES)
    ap.add_argument("--gaps", type=float, nargs="*", default=GAPS, help="solve these designs only; with --keep, "
                                                                         "run each in its own process and plot "
                                                                         "once all are there")
    ap.add_argument("--plot-only", action="store_true", help="re-plot from the results in --keep")
    args = ap.parse_args()
    work = Path(args.keep) if args.keep else Path(tempfile.mkdtemp(prefix="ccx_split_"))
    work.mkdir(parents=True, exist_ok=True)
    if not args.plot_only:
        for g in args.gaps:
            t0 = time.time()
            res, viz = run_design(g, work, args.forces)
            res["run time (s)"] = round(time.time() - t0, 1)
            (work / f"split_{g:.1f}.pkl").write_bytes(pickle.dumps((res, viz)))
    done = {g: work / f"split_{g:.1f}.pkl" for g in GAPS}
    if not all(f.exists() for f in done.values()):
        print("not all designs solved yet:", [g for g, f in done.items() if not f.exists()])
        return
    out = {"what": "both half-collars in one CalculiX (ccx 2.21) model round a rigid O57 body, the four clamp "
                   "screws tightened past snug, for the 1.0 mm split the collar had and the 0.6 mm it has now",
           "settings": {"material": {"E (MPa)": E, "nu": NU, "note": "solid, isotropic PLA, linear elastic"},
                        "elements": "C3D10 on gmsh tets, as joint_fea.py and ccx_stress.py",
                        "body": "rigid O57, frictionless, 0.15 mm clear all round (an active set of radial "
                                "constraints)",
                        "split": f"frictionless, node to surface: SPRING2 springs of {K_SPLIT:.0e} N/mm from the "
                                 "bracket's split-face nodes to the carrier's face (*EQUATION), an active set",
                        "screws": "F in each M3, on the carrier's counterbore floors and the bracket's nut-pocket "
                                  "floors; the screws themselves are not modelled",
                        "peaks": "at least 1.5 mm from the screw seats; across layers uses each part's print "
                                 "direction (bracket world Y, carrier world X)"},
           "designs": {}}
    viz = {}
    for g, f in done.items():
        out["designs"][f"{g:.1f} mm"], viz[g] = pickle.loads(f.read_bytes())
    (HERE / "ccx_split.json").write_text(json.dumps(out, indent=2) + "\n")
    from split_plots import plot_all
    plot_all(out, viz, RENDERS)
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

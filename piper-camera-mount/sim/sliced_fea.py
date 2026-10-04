#!/usr/bin/env python3
"""As-printed FEA of the PiPER mount: the bracket, pod and carrier rebuilt from their sliced G-code.

ccx_stress.py and ccx_split.py treat each part as solid, isotropic PLA. A print is neither. It has
walls round the outside and 25 % grid infill inside, its beads are stiffer and stronger along their
length than across, and its layers bond more weakly than either. So here each part is rebuilt from
the G-code that slice_configs.py writes for it, in each of three configurations:

  h2d_pahtcf_06   H2D, PAHT-CF, 0.6 mm hardened nozzle, 0.30 mm layers (Bambu's recommendation)
  h2d_pahtcf_04   H2D, PAHT-CF, 0.4 mm hardened nozzle, 0.20 mm layers (the nozzle fitted now)
  a1m_pla_04      A1 mini, PLA Basic, 0.4 mm nozzle, 0.20 mm layers (for anyone without PAHT-CF)

- Material map. gcode_voxels.py rasterises every extrusion on the part's own plate at 0.1 mm, with
  its direction, in the STL's print frame. Each voxel (0.6 mm: 3 layers of 0.2 or 2 of 0.3) then
  holds some fraction of bead in some mix of directions. Its stiffness is the volume average of the
  bead's orthotropic stiffness turned to each direction (iso-strain, Voigt), with the space between
  infill lines left empty. Voxels under 15 % bead are dropped, as is anything not face-connected to
  the part.
- Bead properties. sim/bead_properties.json, axes 1 along the bead, 2 across it in the layer, 3 across
  the layers, back-calculated from Bambu's datasheets (bead_properties_2026-10-03.md). Dry.
- Failure. The strain at each voxel's centre gives the stress in each bead direction present
  (iso-strain), turned into that bead's axes. There are three Hashin-type modes, each a stress
  exposure that scales with the load (1 = failure): along the bead, between beads within a layer,
  and between layers. The largest is the voxel's failure index, and 1 / index is the factor on the
  load to the first failure.
- Frames. Each part's voxels are in its print frame. The print transforms of
  piper_mount.print_orientation place them in the world frame, so the loads and supports are
  ccx_stress.py's and ccx_split.py's, defined in world coordinates:

  clamp   bracket + carrier. A rigid, frictionless O57 body, 0.15 mm clear (an active set of radial
          penalty springs on the bores). A frictionless split: penalty springs from the bracket's
          split-face nodes to the carrier's face, across the 0.6 mm gap, also an active set. F in each
          M3 on the nut-pocket floors and head seats, from 50 to 1000 N.
  pod     bracket + pod, the pod tied to the seat (a bonded joint, as in joint_fea.py), the bore and
          the tab pad fixed. The HQ Camera's 83 g at 1 g along X, Y and Z, and 10 N on the pod's
          outer edge along X, Y and Z.
  yank    the carrier, its bore fixed: 10 N at the USB-C plug, carried to the four standoff seats as
          through a rigid board.

  zones   a solved clamp re-read (no solve): the peaks under the nuts and heads, at the split faces
          (contact edges, which don't converge with the voxel size), in the collar and ears away
          from both, and at the bracket's ear root, where ccx_split.py's solid PLA peaks.

- Checks. The same voxel grids filled solid with ccx's isotropic PLA (E 2400 MPa, nu 0.35), against
  ccx_split.json and ccx_stress.json (--solid). The clamp at 1.0, 0.8 and 0.6 mm (--h). Each
  raster's bead volume against the filament its G-code pushes.
- Solving. CG with pyamg's smoothed aggregation (--solver amg), or a sparse Cholesky through
  pypardiso (--solver direct: faster up to about 0.8 mm, but 14.5 GB of factor at 0.6 mm). At
  0.6 mm the clamp has 1.6 M unknowns; start it from a coarser solution with --warm-from 1.0, which
  cuts its contact iterations from 12-16 to 4-7 (8 to 15 minutes, about 8 GB).

    python piper-camera-mount/slice/slice_configs.py --bambu ~/bambu/squashfs-root   # the G-code
    pip install numba pyamg pypardiso trimesh opencv-python-headless cadquery gmsh scikit-fem shapely rtree networkx
    python piper-camera-mount/sim/sliced_fea.py [--configs ...] [--cases clamp zones pod yank] [--solid] [--h 0.6]
        [--solver amg|direct] [--warm-from 1.0] [--max-iter 16]

Out: sim/sliced_fea.json (merged, so cases can be run separately) and the cache in sim/build_sliced/.
"""
from __future__ import annotations

import argparse
import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from numba import njit
from scipy import ndimage
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
MOUNT = HERE.parent
EX = MOUNT / "exports"
SLICE = MOUNT / "slice"
CACHE = HERE / "build_sliced"
sys.path.insert(0, str(MOUNT / "cad"))
sys.path.insert(0, str(HERE))
from gcode_voxels import NAMES, parse, rasterize, volume_check  # noqa: E402
from joint_fea import BOSS_R, DIRS, G, M_CAM, PAD_R, PIXEL, load_params, rigid_fit, station  # noqa: E402
from voxel_fe import DirectSolver, Solver, VoxelModel, bond, isotropic, orthotropic, strains  # noqa: E402

CONFIGS = {
    "h2d_pahtcf_06": {"material": "PAHT-CF", "bed": (350.0, 320.0),
                      "label": "PAHT-CF, H2D, 0.6 mm nozzle, 0.30 mm layers"},
    "h2d_pahtcf_04": {"material": "PAHT-CF", "bed": (350.0, 320.0),
                      "label": "PAHT-CF, H2D, 0.4 mm nozzle, 0.20 mm layers"},
    "a1m_pla_04": {"material": "PLA", "bed": (180.0, 180.0),
                   "label": "PLA Basic, A1 mini, 0.4 mm nozzle, 0.20 mm layers"},
}
PLATES = {"bracket": 2, "pod": 3, "carrier": 4}      # slice_configs.py: one part per plate, bed-centred
DP = 0.1                    # mm, raster pixel
H_VOX = 0.6                 # mm, voxel (in plane; through the layers, the nearest whole number of layers)
F_MIN = 0.15                # least bead fraction a voxel keeps
NBIN = 36                   # 5 degree direction bins, centred on 0, 5, ..., 175
E_SOLID, NU_SOLID = 2400.0, 0.35        # ccx_stress.py's solid PLA, for the checks
GROUP = np.zeros(256, np.int64)         # feature -> 0 wall, 1 solid (skins, solid infill, bridges), 2 sparse
for _code, _name in NAMES.items():
    GROUP[_code] = 2 if _name == "Sparse infill" else 0 if "wall" in _name.lower() or "shell" in _name.lower() else 1
GROUPS = ("wall", "solid infill or skin", "sparse infill")
MODES = ("along the bead", "between beads in a layer", "between layers")
FORCES = (200, 1000)                                # N per M3: snug, and overtightened
ALPHA_FIX, ALPHA_CONTACT = 1e2, 3e1     # penalty stiffness, as multiples of the median diagonal of K
MAX_ITER = {"n": 10}                    # contact iterations per load; --max-iter
SOLVER = {"name": "amg"}            # or "direct"; set by --solver
SETTLED = 0.002                         # contact has settled when under this share of its rows change
REBUILD_FRAC = 0.01                     # AMG is rebuilt when over this share of the contact rows changed
BUMP_N, YANK_LEVER = 10.0, 10.0         # as ccx_stress.py
EXCL_LOAD, EXCL_SUPPORT = 1.5, 2.0      # mm: peaks are taken this far from loaded and from fixed nodes
EAR_R = 2.5                             # mm: "at the ear root" is within this of CalculiX's peak there
SPLIT_DEPTH = 1.5                       # mm: the split faces' zone, from each face into its part
RX90 = np.array([[1.0, 0, 0], [0, 0, -1], [0, 1, 0]])     # cadquery rotate about +X by 90: +Y -> +Z
RY90 = np.array([[0.0, 0, 1], [0, 1, 0], [-1, 0, 0]])     # about +Y by 90: -X -> +Z


# --- material -----------------------------------------------------------------------------------

def material(name: str) -> dict:
    """Bead properties (MPa) plus 'C', the 6 x 6 stiffness in bead axes, and 'fourier', the
    coefficients of C turned by theta about the build axis: c0 + a2 cos2t + b2 sin2t + a4 cos4t + b4 sin4t."""
    if name == "solid":
        m = {"C": isotropic(E_SOLID, NU_SOLID)}
    else:
        d = json.loads((HERE / "bead_properties.json").read_text())[name]
        m = {k: float(d[k]) for k in ("E1", "E2", "E3", "G12", "G13", "G23", "nu12", "nu13", "nu23", "Xt", "Xc",
                                      "Yt", "Yc", "Zt", "Zc", "S12", "S13", "S23")}
        m["C"] = orthotropic(m["E1"], m["E2"], m["E3"], m["G12"], m["G13"], m["G23"], m["nu12"], m["nu13"],
                             m["nu23"])
    th = np.arange(8) * np.pi / 8
    Cs = np.array([c_print(m["C"], t) for t in th]).reshape(8, 36)
    A = np.column_stack([np.ones(8), np.cos(2 * th), np.sin(2 * th), np.cos(4 * th), np.sin(4 * th)])
    m["fourier"] = np.linalg.lstsq(A, Cs, rcond=None)[0]                  # (5, 36)
    assert np.allclose(A @ m["fourier"], Cs, atol=1e-6 * abs(Cs).max())
    m["name"] = name
    return m


def q_bead(theta: float) -> np.ndarray:
    """Columns: the bead axes 1, 2, 3 in print coordinates, for a bead at theta (rad) in the layer."""
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def c_print(C: np.ndarray, theta: float) -> np.ndarray:
    M = bond(q_bead(theta))
    return M @ C @ M.T


def exposures(s: np.ndarray, m: dict) -> np.ndarray:
    """(n, 3) stress exposures (1 = failure) in bead axes, Voigt 11 22 33 23 13 12: along the bead
    (Hashin fibre mode), between beads in a layer (plane normal 2), between layers (plane normal 3)."""
    s1, s2, s3, t23, t13, t12 = s.T
    bead = np.where(s1 >= 0, np.sqrt((s1 / m["Xt"]) ** 2 + (t12 / m["S12"]) ** 2 + (t13 / m["S13"]) ** 2),
                    -s1 / m["Xc"])
    inl = np.sqrt((s2 / np.where(s2 >= 0, m["Yt"], m["Yc"])) ** 2 + (t12 / m["S12"]) ** 2 + (t23 / m["S23"]) ** 2)
    itl = np.sqrt((s3 / np.where(s3 >= 0, m["Zt"], m["Zc"])) ** 2 + (t13 / m["S13"]) ** 2 + (t23 / m["S23"]) ** 2)
    return np.column_stack([bead, inl, itl])


# --- G-code -> voxels ---------------------------------------------------------------------------

@njit(cache=True)
def _bin(cls, ang, inside, kvox, s, group, trig_tab, cnt, cin, trig, hist, feat):
    L, ny, nx = cls.shape
    for k in range(L):
        K = kvox[k]
        if K < 0:
            continue
        for j in range(ny):
            J = j // s
            for i in range(nx):
                I = i // s
                if inside[k, j, i]:
                    cin[K, J, I] += 1
                c = cls[k, j, i]
                if c == 0:
                    continue
                a = ang[k, j, i]
                cnt[K, J, I] += 1
                for q in range(4):
                    trig[K, J, I, q] += trig_tab[a, q]
                hist[K, J, I, ((a + 2) // 5) % 36] += 1
                feat[K, J, I, group[c]] += 1


def print_transform(part: str, p) -> tuple[np.ndarray, np.ndarray]:
    """(R, t): print = R @ world + t, the placement print_orientation gives each STL."""
    import cadquery as cq  # noqa: F401
    from piper_mount import make_bracket, make_carrier, make_pod
    if part == "bracket":
        R, shape = RX90, make_bracket(p).rotate((0, 0, 0), (1, 0, 0), 90)
    elif part == "carrier":
        R, shape = RY90, make_carrier(p).rotate((0, 0, 0), (0, 1, 0), 90)
    else:
        o, Rst = station(p)
        R = RX90 @ Rst
        shape = make_pod(p).translate(tuple(-o)).rotate((0, 0, 0), (0, 0, 1), -p.toe_deg)
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 90)
    bb = shape.val().BoundingBox()
    t = np.array([-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin])
    if part == "pod":
        t = t - R @ o
    return R, t


def transforms(p) -> dict:
    f = CACHE / "transforms.json"
    if f.exists():
        return {k: (np.array(v["R"]), np.array(v["t"])) for k, v in json.loads(f.read_text()).items()}
    out = {k: print_transform(k, p) for k in PLATES}
    CACHE.mkdir(exist_ok=True)
    f.write_text(json.dumps({k: {"R": R.tolist(), "t": t.tolist()} for k, (R, t) in out.items()}))
    return out


def voxel_grid(cfg: str, part: str, h: float) -> dict:
    """The part's G-code binned into voxels of h (in plane) by a whole number of layers. Cached."""
    f = CACHE / f"{cfg}_{part}_{h:.2f}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    t0 = time.time()
    gcode = (SLICE / f"build_{cfg}" / f"plate_{PLATES[part]}_{part}.gcode").read_text()
    bx, by = CONFIGS[cfg]["bed"]
    tp = parse(gcode, offset_xy=(bx / 2, by / 2))
    stl = EX / f"{part}.stl"
    r = rasterize(tp, stl, DP)
    vol = volume_check(tp, r)
    lh = float(np.median(r.h))
    assert np.allclose(r.h, lh, atol=1e-4), "layers of more than one height"
    s = int(round(h / DP))
    nl = max(1, int(round(h / lh)))
    hz = nl * lh
    L, ny, nx = r.cls.shape
    kvox = np.floor((r.z_top - r.h / 2) / hz).astype(np.int64)
    shape = (int(kvox.max()) + 1, (ny + s - 1) // s, (nx + s - 1) // s)
    a = np.radians(np.arange(180))
    tab = np.column_stack([np.cos(2 * a), np.sin(2 * a), np.cos(4 * a), np.sin(4 * a)])
    cnt = np.zeros(shape, np.int32)
    cin = np.zeros(shape, np.int32)
    trig = np.zeros(shape + (4,))
    hist = np.zeros(shape + (NBIN,), np.uint16)
    feat = np.zeros(shape + (3,), np.uint16)
    _bin(r.cls, r.ang, r.inside, kvox, s, GROUP, tab, cnt, cin, trig, hist, feat)
    # extents of the beads against the STL (in print x, y): a check on the placement
    import trimesh
    lo, hi = trimesh.load_mesh(stl).bounds
    occ = (r.cls > 0).any(axis=0)
    jj, ii = np.nonzero(occ)
    ext = {"beads x (mm)": [round(r.origin[0] + ii.min() * DP, 2), round(r.origin[0] + (ii.max() + 1) * DP, 2)],
           "beads y (mm)": [round(r.origin[1] + jj.min() * DP, 2), round(r.origin[1] + (jj.max() + 1) * DP, 2)],
           "STL x (mm)": [round(lo[0], 2), round(hi[0], 2)], "STL y (mm)": [round(lo[1], 2), round(hi[1], 2)],
           "top layer z (mm)": round(float(r.z_top[-1]), 3), "STL height (mm)": round(float(hi[2]), 3)}
    K, J, I = np.nonzero((cnt > 0) | (cin > 0))
    g = {"cfg": cfg, "part": part, "h": np.array([s * DP, s * DP, hz]), "origin": np.array([*r.origin, 0.0]),
         "layers per voxel": nl, "layer (mm)": lh, "npix": s * s * nl, "ijk": np.column_stack([I, J, K]),
         "cnt": cnt[K, J, I], "cin": cin[K, J, I], "trig": trig[K, J, I], "hist": hist[K, J, I],
         "feat": feat[K, J, I], "volume check": vol, "extent check": ext,
         "pixel volume (mm3)": DP * DP * lh, "raster (s)": round(time.time() - t0, 1)}
    CACHE.mkdir(exist_ok=True)
    f.write_bytes(pickle.dumps(g))
    return g


def largest_component(ijk: np.ndarray) -> np.ndarray:
    """Mask of the voxels in the largest face-connected component."""
    lo = ijk.min(axis=0)
    idx = ijk - lo
    grid = np.zeros(idx.max(axis=0) + 1, bool)
    grid[tuple(idx.T)] = True
    lab, n = ndimage.label(grid)
    if n <= 1:
        return np.ones(len(ijk), bool)
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    return lab[tuple(idx.T)] == np.argmax(sizes)


class Part:
    """One part's voxel model, its print transform, and what each voxel holds."""

    def __init__(self, name: str, g: dict, mat: dict, R: np.ndarray, t: np.ndarray, solid: bool = False,
                 assemble: bool = True):
        self.name, self.mat, self.R, self.t, self.solid = name, mat, R, t, solid
        N = g["npix"]
        frac = (g["cin"] if solid else g["cnt"]) / N
        keep = frac >= (0.5 if solid else F_MIN)
        conn = largest_component(g["ijk"][keep])
        sel = np.flatnonzero(keep)[conn]
        pv = g["pixel volume (mm3)"]
        self.stats = {"voxels": int(len(sel)), "voxel (mm)": [round(float(v), 3) for v in g["h"]],
                      "bead volume in the raster (mm3)": round(float(g["cnt"].sum() * pv), 1),
                      "bead volume kept (mm3)": round(float(g["cnt"][sel].sum() * pv), 1),
                      "STL volume in the raster (mm3)": round(float(g["cin"].sum() * pv), 1)}
        self.stats["bead volume dropped (%)"] = round(100 * (1 - self.stats["bead volume kept (mm3)"] /
                                                              self.stats["bead volume in the raster (mm3)"]), 2)
        self.ijk = g["ijk"][sel]
        self.cnt, self.hist, self.feat = g["cnt"][sel], g["hist"][sel].astype(np.float32), g["feat"][sel]
        self.frac = frac[sel]
        if solid:
            C = np.broadcast_to(mat["C"], (len(sel), 6, 6)).copy()
        else:
            coef = np.column_stack([self.cnt, g["trig"][sel]]) / N               # (n, 5)
            C = (coef @ mat["fourier"]).reshape(-1, 6, 6)
        self.model = VoxelModel(self.ijk, C, g["h"], g["origin"], assemble=assemble)
        self.xw = (self.model.x - t) @ R                                         # nodes, world
        self.cw = (g["origin"] + (self.ijk + 0.5) * g["h"] - t) @ R              # voxel centres, world
        self.surface = self.model.surface

    def world_dofs(self, nodes: np.ndarray, d: np.ndarray) -> np.ndarray:
        """Coefficients on each node's three print-frame dofs for the world component along d."""
        return np.broadcast_to(self.R @ np.asarray(d, float), (len(nodes), 3))


class System:
    """Several parts in one linear system, coupled only by penalty constraints."""

    def __init__(self, parts: list[Part]):
        self.parts = parts
        self.off = np.cumsum([0] + [3 * q.model.n_nodes for q in parts])
        self.n_nodes = int(self.off[-1] // 3)
        self.K = sp.block_diag([q.model.K for q in parts], format="csr")
        for q in parts:
            q.model.K = None                    # only the block matrix is used from here; saves memory
        d = self.K.diagonal()
        self.k0 = float(np.median(d[d > 0]))

    def rigid_modes(self) -> np.ndarray:
        """Six rigid-body modes per part, each part's own: AMG's near-null space. (Six shared by all the
        parts would halve the coarse grids, but CG then needs 1.5 to 3 times the iterations: the split
        holds the halves only along its normal, so they slide past each other freely, which a rigid
        motion of both together can't represent.)"""
        B = np.zeros((self.off[-1], 6 * len(self.parts)))
        for i, q in enumerate(self.parts):
            B[self.off[i]:self.off[i + 1], 6 * i:6 * i + 6] = q.model.rigid_modes()
        return B

    def dof(self, i: int, nodes: np.ndarray) -> np.ndarray:
        return self.off[i] + 3 * np.asarray(nodes)[:, None] + np.arange(3)


class Rows:
    """Linear constraint rows g0 + B u (sparse B), each with a penalty stiffness k."""

    def __init__(self, ndof: int):
        self.ndof = ndof
        self.r, self.c, self.v, self.g0, self.k = [], [], [], [], []
        self.n = 0

    def add(self, dofs: np.ndarray, coef: np.ndarray, g0: np.ndarray, k: float):
        """dofs, coef: (m, L) per row; g0: (m,)."""
        m = len(g0)
        self.r.append(np.repeat(self.n + np.arange(m), dofs.shape[1]))
        self.c.append(dofs.ravel())
        self.v.append(coef.ravel())
        self.g0.append(np.asarray(g0, float))
        self.k.append(np.full(m, k))
        self.n += m
        return np.arange(self.n - m, self.n)

    def done(self):
        self.B = sp.csr_matrix((np.concatenate(self.v), (np.concatenate(self.r), np.concatenate(self.c))),
                               shape=(self.n, self.ndof))
        self.g0 = np.concatenate(self.g0)
        self.k = np.concatenate(self.k)
        return self

    def penalty(self, on: np.ndarray):
        """K_P and f_P enforcing g0 + B u = 0 on the rows in `on` (bool mask)."""
        w = self.k * on
        P = (self.B.T @ sp.diags(w) @ self.B).tocsr()
        f = -(self.B.T @ (w * self.g0))
        return P, f


# --- selections (world frame) ---------------------------------------------------------------------

def radial(xw: np.ndarray, p) -> tuple[np.ndarray, np.ndarray]:
    d = np.column_stack([xw[:, 0] - p.ax_x, np.zeros(len(xw)), xw[:, 2] - p.ax_z])
    r = np.linalg.norm(d, axis=1)
    return r, d / r[:, None]


def bore_nodes(q: Part, p) -> np.ndarray:
    r, _ = radial(q.xw, p)
    h = float(q.model.h.max())
    sel = q.surface & (r < p.bore_r + 0.75 * h) & (q.xw[:, 1] > p.collar_y0 - 0.5) & (q.xw[:, 1] < p.collar_y1 + 0.5)
    return np.flatnonzero(sel)


def annulus(q: Part, centre_yz, r0: float, r1: float, x_lo: float, x_hi: float) -> np.ndarray:
    rr = np.hypot(q.xw[:, 1] - centre_yz[0], q.xw[:, 2] - centre_yz[1])
    return np.flatnonzero(q.surface & (rr >= r0 - 0.05) & (rr <= r1) & (q.xw[:, 0] >= x_lo) & (q.xw[:, 0] <= x_hi))


def screw_seats(q: Part, p, side: int) -> list[np.ndarray]:
    """Nodes under each M3's nut (bracket, side -1: the pocket floors, facing -X) or head (carrier,
    side +1: the counterbore floors, facing +X), as ccx_split.screw_loads."""
    h = float(q.model.h.max())
    out = []
    for y in p.clamp_y:
        for sz in (1, -1):
            z = p.ax_z + sz * p.clamp_r
            if side < 0:
                xf = p.ax_x - p.ear_w + p.m3_nut_depth
                n = annulus(q, (y, z), p.m3_clear_d / 2, 3.4, xf - 0.5 * h, xf + 0.75 * h)
            else:
                xf = p.ax_x + p.clamp_head_seat
                n = annulus(q, (y, z), p.m3_clear_d / 2, 3.4, xf - 0.75 * h, xf + 0.5 * h)
            assert len(n) >= 3, f"{q.name}: no seat for the M3 at y={y}, z={z:.1f}"
            out.append(n)
    return out


def split_pairs(qb: Part, qc: Part, p) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Bracket split-face nodes, each with the four carrier nodes of the face opposite it and their
    bilinear weights. The carrier's split face is the top of its print, so its nodes there are the
    topmost of each column of its grid."""
    h = float(qb.model.h.max())
    xs_b = p.ax_x - p.split_gap / 2
    sb = np.flatnonzero(qb.surface & (qb.xw[:, 0] > xs_b - 0.75 * h))
    hc = float(qc.model.h.max())
    cand = np.flatnonzero(qc.surface & (qc.xw[:, 0] < p.ax_x + p.split_gap / 2 + 0.75 * hc))
    nij = qc.model.node_ijk[cand]
    top = {}
    for n, (i, j, k) in zip(cand, nij):
        if (i, j) not in top or k > qc.model.node_ijk[top[(i, j)], 2]:
            top[(i, j)] = n
    pts = np.column_stack([np.full(len(sb), p.ax_x + p.split_gap / 2), qb.xw[sb, 1], qb.xw[sb, 2]])
    pp = pts @ qc.R.T + qc.t
    f = (pp[:, :2] - qc.model.origin[:2]) / qc.model.h[:2]
    i0 = np.floor(f).astype(int)
    d = f - i0
    S, M, W = [], [], []
    for s, (a, b), (u, v) in zip(sb, i0, d):
        corners = [(a, b), (a + 1, b), (a, b + 1), (a + 1, b + 1)]
        if not all(c in top for c in corners):
            continue
        S.append(s)
        M.append([top[c] for c in corners])
        W.append([(1 - u) * (1 - v), u * (1 - v), (1 - u) * v, u * v])
    return np.array(S), np.array(M), np.array(W)


def trilinear(q: Part, pts_w: np.ndarray):
    """For world points: the voxel of q holding each (or -1) and the trilinear weights on its 8 nodes."""
    pp = pts_w @ q.R.T + q.t
    f = (pp - q.model.origin) / q.model.h
    ijk = np.floor(f).astype(np.int64)
    d = f - ijk
    key = {tuple(v): n for n, v in enumerate(q.ijk)}
    el = np.array([key.get(tuple(v), -1) for v in ijk])
    from voxel_fe import CORNERS
    w = np.prod(np.where(CORNERS[None] == 1, d[:, None, :], 1 - d[:, None, :]), axis=2)    # (n, 8)
    return el, w


# --- solving ---------------------------------------------------------------------------------------

def solve(system: System, rows: Rows, on: np.ndarray, f_ext: np.ndarray, solver: Solver | None, x0=None,
          rebuild: bool = False, rtol: float = 1e-6):
    P, fP = rows.penalty(on)
    direct = SOLVER["name"] == "direct"
    if solver is None:
        solver = DirectSolver(system, P) if direct else Solver(system, P)
        what = f"Cholesky, {solver.nnz_L / 1e6:.0f} M nonzeros" if direct else "AMG setup"
        print(f"  K: {system.off[-1]} dofs, nnz {system.K.nnz}; {what} {solver.setup_s:.0f} s", flush=True)
    else:
        # both solvers rebuild (AMG) or refactorise (direct) themselves once CG stalls on the old one
        solver.set_operator(P, rebuild=rebuild)
    try:
        U, info = solver.solve(f_ext + fP, x0=x0, rtol=rtol, maxiter=400)
    except RuntimeError:
        solver.set_operator(P, rebuild=True)
        U, info = solver.solve(f_ext + fP, x0=x0, rtol=3 * rtol, maxiter=800)
        info["rebuilt"] = True
    return U, info, solver


def solver_info(solver) -> dict:
    if isinstance(solver, DirectSolver):
        return {"solver": "sparse Cholesky (MKL PARDISO), kept as CG's preconditioner",
                "factorisations": solver.factorisations, "factor nonzeros (M)": round(solver.nnz_L / 1e6, 1),
                "factorising (s)": round(solver.factor_s, 1)}
    return {"solver": "CG with smoothed-aggregation AMG (pyamg)", "AMG builds": solver.rebuilds,
            "AMG setup (s)": round(solver.setup_total_s, 1)}


def node_forces(system: System, i: int, nodes: np.ndarray, F_world: np.ndarray, f: np.ndarray | None = None):
    """Add a world force spread equally over nodes of part i."""
    f = np.zeros(system.off[-1]) if f is None else f
    q = system.parts[i]
    fp = q.R @ np.asarray(F_world, float) / len(nodes)
    np.add.at(f, system.dof(i, nodes), np.broadcast_to(fp, (len(nodes), 3)))
    return f


def part_u(system: System, U: np.ndarray, i: int) -> np.ndarray:
    return U[system.off[i]:system.off[i + 1]]


# --- results ---------------------------------------------------------------------------------------

def evaluate(q: Part, u: np.ndarray, keep: np.ndarray, signs=(1.0,)) -> dict:
    """Peaks over the voxels in `keep`. As-printed: the failure index (largest exposure over the bead
    directions present and the three modes), with its mode, direction, feature and place, plus the
    largest bead tension along and across the layers. Solid: von Mises, max principal and the normal
    stress across the layers, as ccx_stress.py. With signs (1, -1) the load is also reversed."""
    eps = strains(q.model, u)
    out = {}
    for sign in signs:
        e = sign * eps
        tag = "" if signs == (1.0,) else ("+" if sign > 0 else "-")
        if q.solid:
            s = np.einsum("nij,nj->ni", q.model.C, e)
            xx, yy, zz, yz, xz, xy = s.T
            vm = np.sqrt(0.5 * ((xx - yy) ** 2 + (yy - zz) ** 2 + (zz - xx) ** 2) + 3 * (xy ** 2 + yz ** 2 + xz ** 2))
            T = np.stack([np.stack([xx, xy, xz], -1), np.stack([xy, yy, yz], -1), np.stack([xz, yz, zz], -1)], -2)
            p1 = np.linalg.eigvalsh(T)[:, 2]
            res = {}
            for key, arr in (("von Mises (MPa)", vm), ("max principal (MPa)", p1), ("tension across layers (MPa)", zz)):
                i = np.flatnonzero(keep)[np.argmax(arr[keep])]
                res[key] = {"value": round(float(arr[i]), 3), "at (mm)": [round(float(c), 1) for c in q.cw[i]]}
            out[tag or "peaks"] = res
            continue
        fi = np.zeros(len(e))
        mode = np.zeros(len(e), int)
        angle = np.zeros(len(e))
        s3 = np.full(len(e), -np.inf)
        s1 = np.full(len(e), -np.inf)
        thr = np.maximum(1.0, 0.1 * q.cnt)
        for b in range(NBIN):
            sel = np.flatnonzero(q.hist[:, b] >= thr)
            if not len(sel):
                continue
            th = math.radians(5.0 * b)
            sb = e[sel] @ c_print(q.mat["C"], th).T
            sm = sb @ bond(q_bead(th).T).T
            ex = exposures(sm, q.mat)
            m = ex.max(axis=1)
            better = m > fi[sel]
            fi[sel[better]] = m[better]
            mode[sel[better]] = ex[better].argmax(axis=1)
            angle[sel[better]] = 5.0 * b
            s3[sel] = np.maximum(s3[sel], sm[:, 2])
            s1[sel] = np.maximum(s1[sel], sm[:, 0])
        k = np.flatnonzero(keep)
        i = k[np.argmax(fi[k])]
        res = {"failure index": round(float(fi[i]), 4), "mode": MODES[mode[i]],
               "bead direction in the layer (deg)": angle[i], "feature": GROUPS[int(np.argmax(q.feat[i]))],
               "bead fraction of the voxel": round(float(q.frac[i]), 2),
               "at (mm)": [round(float(c), 1) for c in q.cw[i]],
               "worst voxel per mode": {}}
        for mm, name in enumerate(MODES):
            km = k[mode[k] == mm]
            if len(km):
                j = km[np.argmax(fi[km])]
                res["worst voxel per mode"][name] = {"failure index": round(float(fi[j]), 4),
                                                     "at (mm)": [round(float(c), 1) for c in q.cw[j]]}
        j = k[np.argmax(s3[k])]
        res["largest bead tension across the layers (MPa)"] = {"value": round(float(s3[j]), 3),
                                                               "at (mm)": [round(float(c), 1) for c in q.cw[j]]}
        j = k[np.argmax(s1[k])]
        res["largest bead tension along the bead (MPa)"] = {"value": round(float(s1[j]), 3),
                                                            "at (mm)": [round(float(c), 1) for c in q.cw[j]]}
        out[tag or "peaks"] = res
        if tag == "" or sign > 0:
            q.last_fi = fi
    return out if signs != (1.0,) else out["peaks"]


def away(q: Part, nodes_list, r: float) -> np.ndarray:
    pts = np.concatenate([q.xw[n] for n in nodes_list if len(n)])
    d, _ = cKDTree(pts).query(q.cw, k=1)
    return d > r


# --- cases ---------------------------------------------------------------------------------------

def make_parts(cfg: str, names, p, h: float, solid: bool, assemble: bool = True) -> list[Part]:
    tr = transforms(p)
    mat = material("solid" if solid else CONFIGS[cfg]["material"])
    return [Part(n, voxel_grid(cfg, n, h), mat, *tr[n], solid=solid, assemble=assemble) for n in names]


def ccx_ear_root(F: int) -> np.ndarray:
    """Where ccx_split.py's solid PLA (0.6 mm split) has the bracket's peak max principal at F per M3."""
    forces = json.loads((HERE / "ccx_split.json").read_text())["designs"]["0.6 mm"]["forces"]
    k = min(forces, key=lambda f: abs(float(f) - F))
    return np.array(forces[k]["peaks away from the screw seats"]["max principal (MPa)"]["bracket"]["at (mm)"])


def warm_start(warm: dict, F: int, system: System, row_xw: np.ndarray, kind: np.ndarray, on: np.ndarray):
    """The contact set and displacements of a coarser solution (its viz pickle) at load F, carried to
    this model: each contact row takes the state of the nearest coarse row of its kind (the bracket's
    bore, the carrier's, the split), and each node the inverse-distance mean of the displacements of
    its four nearest coarse nodes. Only the start of the contact loop changes, not what it settles to."""
    c = warm["contact"][F]
    for k in range(3):
        idx, wk = np.flatnonzero(kind == k), c["kind"] == k
        _, j = cKDTree(c["xyz"][wk]).query(row_xw[idx])
        on[idx] = c["on"][wk][j]
    U = np.zeros(system.off[-1])
    for i, q in enumerate(system.parts):
        d, j = cKDTree(warm["xw"][q.name]).query(q.xw, k=4)
        w = 1.0 / np.maximum(d, 1e-6)
        uw = np.einsum("nk,nkc->nc", w / w.sum(axis=1, keepdims=True), warm["uw"][F][q.name][j])
        U[system.off[i]:system.off[i + 1]] = (uw @ q.R.T).ravel()      # world -> print-frame dofs
    return U


def case_clamp(cfg: str, p, h: float, solid: bool, forces=FORCES, warm: dict | None = None,
               check: str | None = None) -> tuple[dict, dict]:
    """check: "crowns" starts the contact loop as ccx_split.py does (the body within 30 degrees of each
    crown, the split open), to show the answer doesn't depend on the start; "bonded" never lets a bore
    node leave the body (radial only, still frictionless), to see how much that alone stiffens the
    collar."""
    t0 = time.time()
    qb, qc = make_parts(cfg, ("bracket", "carrier"), p, h, solid)
    system = System([qb, qc])
    rows = Rows(system.off[-1])
    kc, kf = ALPHA_CONTACT * system.k0, ALPHA_FIX * system.k0
    # the body
    body, crowns = [], []
    for i, (q, side) in enumerate(((qb, -1), (qc, 1))):
        n = bore_nodes(q, p)
        _, rh = radial(q.xw[n], p)
        coef = np.einsum("ij,nj->ni", q.R, rh)
        idx = rows.add(system.dof(i, n), coef, np.full(len(n), p.bore_r - p.body_r), kc)
        body.append((i, n, idx))
        target = np.array([p.ax_x + side * p.bore_r, (p.collar_y0 + p.collar_y1) / 2, p.ax_z])
        c = n[np.argmin(np.linalg.norm(q.xw[n] - target, axis=1))]
        for d in ([0, 1, 0], [0, 0, 1]):
            crowns.append(rows.add(system.dof(i, [c]), q.world_dofs([c], d), np.zeros(1), kf))
    # the split
    S, M, W = split_pairs(qb, qc, p)
    dofs = np.concatenate([system.dof(0, S), system.dof(1, M.ravel()).reshape(len(S), 12)], axis=1)
    coef = np.concatenate([-np.broadcast_to(qb.R @ [1.0, 0, 0], (len(S), 3)),
                           (W[:, :, None] * (qc.R @ [1.0, 0, 0])[None, None, :]).reshape(len(S), 12)], axis=1)
    split = rows.add(dofs, coef, np.full(len(S), p.split_gap), kc)
    rows.done()
    # the screws
    seats_b, seats_c = screw_seats(qb, p, -1), screw_seats(qc, p, 1)
    f1 = np.zeros(system.off[-1])
    for n in seats_b:
        node_forces(system, 0, n, [1.0, 0, 0], f1)
    for n in seats_c:
        node_forces(system, 1, n, [-1.0, 0, 0], f1)
    on = np.zeros(rows.n, bool)
    for c in crowns:
        on[c] = True
    for i, n, idx in body:          # start closed: the body all round and the split; tension drops out
        on[idx] = True
    on[split] = True
    if check == "crowns":
        on[split] = False
        for (i, n, idx), q, side in zip(body, (qb, qc), (-1, 1)):
            _, rh = radial(q.xw[n], p)
            on[idx] = rh[:, 0] * side > math.cos(math.radians(30.0))
    keep = [away(qb, seats_b, EXCL_LOAD), away(qc, seats_c, EXCL_LOAD)]
    out = {"config": cfg, "solid": solid, "voxel (mm)": h, "parts": {q.name: q.stats for q in (qb, qc)},
           "dofs": int(system.off[-1]), "split pairs": int(len(S)),
           "body nodes": {q.name: int(len(n)) for (i, n, _), q in zip(body, (qb, qc))},
           "seat nodes per screw": {"bracket": [int(len(n)) for n in seats_b],
                                    "carrier": [int(len(n)) for n in seats_c]},
           "forces": {}}
    viz = {"F": [], "fi": {}, "U": {}, "contact": {}, "uw": {},
           "xw": {q.name: q.xw.astype(np.float32) for q in (qb, qc)}}
    # each contact row's place (its bracket node, for the split) and kind, for warm starts
    contact = np.concatenate([b[2] for b in body] + [split])
    kind = np.full(rows.n, -1)
    row_xw = np.zeros((rows.n, 3))
    for (i, n, idx), q in zip(body, (qb, qc)):
        kind[idx], row_xw[idx] = i, q.xw[n]
    kind[split], row_xw[split] = 2, qb.xw[S]
    if warm is not None:
        out["warm start"] = f"contact set and displacements from the {warm['h']:.2f} mm solution"
    out["contact rows"] = int(len(contact))
    solver, U = None, None
    changes = 0
    n_rows = sum(len(b[2]) for b in body) + len(split)
    for F in forces:
        hist = []
        if warm is not None and F in warm.get("contact", {}):
            U = warm_start(warm, F, system, row_xw, kind, on)
        for it in range(MAX_ITER["n"]):
            # AMG: a fresh hierarchy once many contacts have flipped (the old one can take five times the CG
            # iterations); otherwise the old one, until CG stalls on it. The direct solver keeps its
            # factorisation until CG stalls, which at 1.0 mm is always the cheaper way
            many = SOLVER["name"] == "amg" and changes > REBUILD_FRAC * n_rows
            U, info, solver = solve(system, rows, on, F * f1, solver, x0=U, rebuild=many)
            gap = rows.g0 + rows.B @ U
            lam = -rows.k * gap * on                    # compression > 0 on active rows
            changes = 0
            for idx in [b[2] for b in body] + [split]:
                act = on[idx]
                tol = 1e-3 * max(1e-9, float(lam[idx].max()))
                drop = idx[act & (lam[idx] < -tol)] if not (check == "bonded" and idx is not split) else idx[:0]
                add = idx[~act & (gap[idx] < -1e-4)]
                on[drop] = False
                on[add] = True
                changes += len(drop) + len(add)
            hist.append({"iteration": it, "changes": changes, **info})
            print(f"  {cfg} {'solid' if solid else 'printed'} F {F} it {it}: changes {changes}, "
                  f"split on {int(on[split].sum())}, CG {info['cg_iterations']} ({info['solve_s']} s)", flush=True)
            n_rows = sum(len(b[2]) for b in body) + len(split)
            if changes <= SETTLED * n_rows:
                break
        gs = gap[split]
        res = {"converged": changes <= SETTLED * n_rows, "contact changes at the last iteration": changes,
               "iterations": len(hist), "CG iterations": sum(x["cg_iterations"] for x in hist),
               "split gap (mm)": {"narrowest": round(float(gs.min()), 4), "widest": round(float(gs.max()), 4),
                                  "mean": round(float(gs.mean()), 4)},
               "split contact force (N)": round(float(lam[split].sum()), 1),
               "body: radial contact force, summed (N)": {q.name: round(float(lam[idx].sum()), 1)
                                                         for (i, n, idx), q in zip(body, (qb, qc))},
               "peaks": {}}
        for i, q in enumerate((qb, qc)):
            res["peaks"][q.name] = evaluate(q, part_u(system, U, i), keep[i])
            if not solid:
                viz["fi"].setdefault(q.name, {})[F] = q.last_fi.astype(np.float32)
        # the bracket's ear root, where CalculiX's solid PLA peaks: the peak within EAR_R of that point
        xyz = ccx_ear_root(F)
        near = keep[0] & (np.linalg.norm(qb.cw - xyz, axis=1) < EAR_R)
        if near.any():
            res["at CalculiX's ear-root peak"] = {"point (mm)": [round(float(c), 1) for c in xyz], "radius (mm)": EAR_R,
                                                  "bracket": evaluate(qb, part_u(system, U, 0), near)}
        viz["U"][F] = U.astype(np.float32)
        viz["contact"][F] = {"xyz": row_xw[contact].astype(np.float32), "on": on[contact].copy(),
                             "kind": kind[contact]}
        viz["uw"][F] = {q.name: (part_u(system, U, i).reshape(-1, 3) @ q.R).astype(np.float32)
                        for i, q in enumerate((qb, qc))}
        viz["F"].append(F)
        out["forces"][str(F)] = res
        pk = res["peaks"]
        key = "max principal (MPa)" if solid else "failure index"
        vals = {k: (v[key]["value"] if solid else v[key]) for k, v in pk.items()}
        print(f"{cfg} {'solid' if solid else 'printed'} h {h} F {F}: gap {res['split gap (mm)']['narrowest']:.3f}, "
              f"split {res['split contact force (N)']} N, {key} {vals}, {time.time() - t0:.0f} s", flush=True)
    out.update(solver_info(solver))
    out["run time (s)"] = round(time.time() - t0, 1)
    viz.update({"cw": {q.name: q.cw for q in (qb, qc)}, "h": h})
    return out, viz


def case_pod(cfg: str, p, h: float, solid: bool) -> dict:
    """bracket + pod, bonded at the seat; bore and tab pad fixed. HQ at 1 g, and the bump."""
    t0 = time.time()
    qb, qp = make_parts(cfg, ("bracket", "pod"), p, h, solid)
    system = System([qb, qp])
    rows = Rows(system.off[-1])
    kf = ALPHA_FIX * system.k0
    bore = bore_nodes(qb, p)
    hb = float(qb.model.h.max())
    d_tab = np.min([np.hypot(qb.xw[:, 0] - x, qb.xw[:, 2] - z) for x, z in p.tab_holes], axis=0)
    pad = np.flatnonzero((qb.xw[:, 1] < p.collar_y0 + 0.5 * hb) & (d_tab < PAD_R))
    fixed = np.union1d(bore, pad)
    for c in range(3):
        e = np.zeros(3)
        e[c] = 1.0
        rows.add(system.dof(0, fixed), np.broadcast_to(e, (len(fixed), 3)), np.zeros(len(fixed)), kf)
    # the tie: the pod's front face (its first layer, z = 0 in its print frame) to the bracket below it
    o, Rst = station(p)
    front = np.flatnonzero(qp.model.node_ijk[:, 2] == 0)
    tied, n_tied = [], 0
    for depth in (0.6, 1.2):
        todo = np.setdiff1d(front, np.array(tied, int))
        el, w = trilinear(qb, qp.xw[todo] - depth * hb * Rst[1])
        ok = el >= 0
        if not ok.any():
            continue
        nodes_b = qb.model.conn[el[ok]]                          # (m, 8)
        for c in range(3):
            dofs = np.concatenate([system.dof(1, todo[ok]), system.dof(0, nodes_b.ravel()).reshape(-1, 24)], axis=1)
            coef = np.concatenate([np.broadcast_to(qp.R[:, c], (ok.sum(), 3)),
                                   -(w[ok][:, :, None] * qb.R[:, c][None, None, :]).reshape(-1, 24)], axis=1)
            rows.add(dofs, coef, np.zeros(ok.sum()), kf)
        tied += list(todo[ok])
    rows.done()
    on = np.ones(rows.n, bool)
    a_tied = len(tied) * float(qp.model.h[0] * qp.model.h[1])
    # loads: the HQ's boss end faces (the pod's top, station y = 0) and the pod's outer edge face
    st = (qp.xw - o) @ Rst.T                                     # station coordinates of the pod's nodes
    hh = p.hq_hole_pitch / 2
    d_boss = np.min([np.hypot(st[:, 0] - x, st[:, 2] - z) for x in (-hh, hh) for z in (-hh, hh)], axis=0)
    boss = np.flatnonzero((qp.model.node_ijk[:, 2] == qp.model.node_ijk[:, 2].max()) & (d_boss < BOSS_R))
    hp = float(qp.model.h.max())
    edge = np.flatnonzero(qp.surface & (st[:, 0] < p.pod_x_out + 0.75 * hp))
    cases = {}
    solver, U = None, None
    d_opt = None
    from piper_mount import optical_axes
    d_opt = np.array(optical_axes(p)["hq"][1].toTuple())
    keep_b = away(qb, [fixed], EXCL_SUPPORT)
    keep_p = away(qp, [boss, edge], EXCL_LOAD)
    out = {"config": cfg, "solid": solid, "voxel (mm)": h, "parts": {q.name: q.stats for q in (qb, qp)},
           "dofs": int(system.off[-1]),
           "fixed nodes": {"bore": int(len(bore)), "pad": int(len(pad))},
           "pod front-face nodes tied to the bracket": int(len(tied)),
           "tied area (mm2, nodes x voxel face)": round(a_tied, 0),
           "HQ boss nodes": int(len(boss)), "edge nodes": int(len(edge)), "cases": {}}
    for k, dname in enumerate(DIRS):
        F = np.eye(3)[k]
        f = node_forces(system, 1, boss, M_CAM * G * F)
        U, info, solver = solve(system, rows, on, f, solver, x0=None)
        up = part_u(system, U, 1).reshape(-1, 3)[boss] @ qp.R          # world displacements of the boss nodes
        ubar = up.mean(axis=0)
        _, th = rigid_fit(qp.xw[boss].T, up.T)
        tilt = np.linalg.norm(th - th.dot(d_opt) * d_opt)
        allu = np.concatenate([part_u(system, U, i).reshape(-1, 3) for i in range(2)])
        cases[f"HQ 1 g {dname}"] = {
            "mean displacement (um)": round(float(np.linalg.norm(ubar)) * 1e3, 4),
            "optical axis tilt (arcmin)": round(math.degrees(tilt) * 60, 5),
            "image shift (px)": round(p.lens_f * math.tan(tilt) / PIXEL, 5),
            "max displacement anywhere (um)": round(float(np.linalg.norm(allu, axis=1).max()) * 1e3, 4),
            "CG iterations": info["cg_iterations"]}
        f = node_forces(system, 1, edge, BUMP_N * F)
        U, info, solver = solve(system, rows, on, f, solver, x0=None)
        cases[f"bump {dname}"] = {q.name: evaluate(q, part_u(system, U, i), kk, signs=(1.0, -1.0))
                                  for i, (q, kk) in enumerate(((qb, keep_b), (qp, keep_p)))}
        cases[f"bump {dname}"]["CG iterations"] = info["cg_iterations"]
        print(f"{cfg} pod {dname}: {cases[f'HQ 1 g {dname}']}", flush=True)
    out["cases"] = cases
    out.update(solver_info(solver))
    out["run time (s)"] = round(time.time() - t0, 1)
    return out


def case_yank(cfg: str, p, h: float, solid: bool) -> dict:
    from ccx_stress import seat_forces
    from piper_mount import pi_holes
    t0 = time.time()
    (qc,) = make_parts(cfg, ("carrier",), p, h, solid)
    system = System([qc])
    rows = Rows(system.off[-1])
    bore = bore_nodes(qc, p)
    rows.add(system.dof(0, bore).reshape(-1, 1), np.ones((3 * len(bore), 1)), np.zeros(3 * len(bore)),
             ALPHA_FIX * system.k0)
    rows.done()
    on = np.ones(rows.n, bool)
    plug = np.array([p.pi_x + 1.6 + 3.3 / 2, p.y_max + 1.0 + YANK_LEVER, p.ax_z - 42.5 + (6.7 + 15.7) / 2])
    x_seat = p.carrier_x0 + p.carrier_t
    seats = []
    for y, z in pi_holes(p):
        n = annulus(qc, (y, z), p.m25_clear_d / 2, 3.0, x_seat - 0.75 * float(qc.model.h.max()), x_seat + 0.1)
        assert len(n) >= 3, f"no standoff seat at y={y}"
        seats.append(n)
    keep = away(qc, [bore], EXCL_SUPPORT) & away(qc, seats, EXCL_LOAD)
    out = {"config": cfg, "solid": solid, "voxel (mm)": h, "parts": {"carrier": qc.stats}, "dofs": int(system.off[-1]),
           "fixed bore nodes": int(len(bore)), "seat nodes": [int(len(n)) for n in seats], "cases": {}}
    solver = None
    for k, dname in enumerate(DIRS):
        _, fs = seat_forces(p, BUMP_N * np.eye(3)[k], plug)
        f = np.zeros(system.off[-1])
        for n, fi in zip(seats, fs):
            node_forces(system, 0, n, fi, f)
        U, info, solver = solve(system, rows, on, f, solver)
        out["cases"][f"yank {dname}"] = {"carrier": evaluate(qc, U, keep, signs=(1.0, -1.0)),
                                         "CG iterations": info["cg_iterations"],
                                         "max displacement (um)": round(float(np.linalg.norm(U.reshape(-1, 3),
                                                                                             axis=1).max()) * 1e3, 2)}
        print(f"{cfg} yank {dname}: {json.dumps(out['cases'][f'yank {dname}'])[:400]}", flush=True)
    out.update(solver_info(solver))
    out["run time (s)"] = round(time.time() - t0, 1)
    return out


def bearing_zone(cw: np.ndarray, p, side: int, r: float = 4.5, depth: float = 4.0) -> np.ndarray:
    """Voxels round an M3 nut (bracket, side -1) or head (carrier, side +1): within r of a screw axis
    and within depth of its seat face either way, so the walls of the nut pocket or counterbore too."""
    xf = p.ax_x - p.ear_w + p.m3_nut_depth if side < 0 else p.ax_x + p.clamp_head_seat
    lo, hi = xf - depth, xf + depth
    inside = np.zeros(len(cw), bool)
    for y in p.clamp_y:
        for sz in (1, -1):
            rr = np.hypot(cw[:, 1] - y, cw[:, 2] - (p.ax_z + sz * p.clamp_r))
            inside |= (rr < r) & (cw[:, 0] >= lo) & (cw[:, 0] <= hi)
    return inside


def split_zone(cw: np.ndarray, p, depth: float = SPLIT_DEPTH) -> np.ndarray:
    """Voxels within depth of the split plane (x = ax_x, world): the faces that press together. Their
    edges, at the screw holes and the ends of the ears, carry the contact's edge peaks."""
    return np.abs(cw[:, 0] - p.ax_x) < p.split_gap / 2 + depth


def clamp_zones(cfg: str, p, h: float, solid: bool = False) -> dict:
    """Re-evaluate a solved clamp (viz pickle) with the nut and head bearing zones apart: the peak
    outside them (the collar and ears as a structure) and inside them (bearing under the nut or head,
    where 1.0 mm voxels put a whole nut's load on a few nodes)."""
    viz = pickle.loads((CACHE / f"viz_{cfg}_{'solid' if solid else 'printed'}_{h:.2f}.pkl").read_bytes())
    qb, qc = make_parts(cfg, ("bracket", "carrier"), p, h, solid, assemble=False)
    system = argparse.Namespace(off=np.cumsum([0] + [3 * q.model.n_nodes for q in (qb, qc)]))   # dofs only
    out = {}
    for F in viz["F"]:
        U = viz["U"][F].astype(float)
        res = {}
        for i, (q, side) in enumerate(((qb, -1), (qc, 1))):
            zone = bearing_zone(q.cw, p, side)
            u = part_u(system, U, i)
            face = split_zone(q.cw, p)
            res[q.name] = {"outside the bearing zones": evaluate(q, u, ~zone),
                           "in the bearing zones": evaluate(q, u, zone),
                           "outside the bearing zones and the split faces": evaluate(q, u, ~zone & ~face),
                           "at the split faces, outside the bearing zones": evaluate(q, u, face & ~zone)}
        near = ~bearing_zone(qb.cw, p, -1) & (np.linalg.norm(qb.cw - ccx_ear_root(F), axis=1) < EAR_R)
        res["bracket at CalculiX's ear-root peak"] = evaluate(qb, part_u(system, U, 0), near)
        out[str(F)] = res
    # bearing stress by hand: F over the nut's (5.5 mm across flats) or head's (O5.5) ring on a O3.4 hole
    a_nut = 0.866 * 5.5 ** 2 - math.pi * (p.m3_clear_d / 2) ** 2
    a_head = math.pi / 4 * (5.5 ** 2 - p.m3_clear_d ** 2)
    out["bearing stress by hand (MPa per N of screw force)"] = {"nut on the bracket": round(1 / a_nut, 5),
                                                                "head on the carrier": round(1 / a_head, 5),
                                                                "areas (mm2)": [round(a_nut, 1), round(a_head, 1)]}
    return out


# --- main ------------------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--configs", nargs="*", default=list(CONFIGS))
    ap.add_argument("--cases", nargs="*", default=["clamp", "pod", "yank"])
    ap.add_argument("--solid", action="store_true", help="fill the voxels solid with ccx's isotropic PLA (the check)")
    ap.add_argument("--h", type=float, default=H_VOX, help="voxel size (mm)")
    ap.add_argument("--forces", type=float, nargs="*", default=FORCES)
    ap.add_argument("--solver", choices=("amg", "direct"), default="amg",
                    help="AMG-preconditioned CG (pyamg), or sparse Cholesky (pypardiso: faster up to about "
                         "0.8 mm, but its factor at 0.6 mm wants 14.5 GB)")
    ap.add_argument("--warm-from", type=float, default=None,
                    help="clamp: start the contact loop from the solution at this (coarser) voxel size")
    ap.add_argument("--check", choices=("crowns", "bonded"), default=None,
                    help="clamp: start as ccx_split.py does, or keep the bores on the body (see case_clamp)")
    ap.add_argument("--max-iter", type=int, default=MAX_ITER["n"], help="contact iterations per load, at most")
    args = ap.parse_args()
    SOLVER["name"] = args.solver
    MAX_ITER["n"] = args.max_iter
    p = load_params((EX / "params.json").read_text())
    out_f = HERE / "sliced_fea.json"
    for cfg in args.configs:
        for case in args.cases:
            key = f"{cfg} / {'solid' if args.solid else 'as printed'} / {args.h:.2f} mm / {case}"
            if case == "clamp":
                warm = None
                if args.warm_from:
                    wf = CACHE / f"viz_{cfg}_{'solid' if args.solid else 'printed'}_{args.warm_from:.2f}.pkl"
                    warm = pickle.loads(wf.read_bytes()) if wf.exists() else None
                    print(f"warm start from {wf.name}" if warm else f"no {wf.name}: a cold start", flush=True)
                res, viz = case_clamp(cfg, p, args.h, args.solid, [int(f) for f in args.forces], warm=warm,
                                      check=args.check)
                if args.check:
                    res["check"] = args.check
                    key = key + f" ({args.check})"
                tag = f"_{args.check}" if args.check else ""
                (CACHE / f"viz_{cfg}_{'solid' if args.solid else 'printed'}_{args.h:.2f}{tag}.pkl").write_bytes(
                    pickle.dumps(viz))
            elif case == "zones":
                res = clamp_zones(cfg, p, args.h, args.solid)
            elif case == "pod":
                res = case_pod(cfg, p, args.h, args.solid)
            else:
                res = case_yank(cfg, p, args.h, args.solid)
            slug = key.replace(" / ", "__").replace(" ", "_")
            (CACHE / f"result__{slug}.json").write_text(json.dumps({key: res}) + "\n")
            merge(out_f)


def merge(out_f: Path) -> None:
    """sim/sliced_fea.json from every run's own result file, so runs in parallel don't clobber each other."""
    allres = json.loads(out_f.read_text()) if out_f.exists() else {}
    for f in sorted(CACHE.glob("result__*.json")):
        allres.update(json.loads(f.read_text()))
    out_f.write_text(json.dumps(dict(sorted(allres.items())), indent=1) + "\n")


if __name__ == "__main__":
    main()

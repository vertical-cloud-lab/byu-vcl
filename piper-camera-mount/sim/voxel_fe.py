#!/usr/bin/env python3
"""Linear elasticity on a voxel grid: 8-node bricks, a full 6 x 6 stiffness per voxel, AMG-preconditioned CG.

The as-printed models in sliced_fea.py are voxels, because a toolpath is naturally a raster: each
voxel gets its own anisotropic stiffness (bead direction, walls vs sparse infill, layer interfaces),
which an unstructured tet mesh of the CAD solid can't carry without binning orientations.

- Voigt order everywhere: xx, yy, zz, yz, xz, xy, with engineering shear strains.
- Element: trilinear brick, 2 x 2 x 2 Gauss points. Every voxel is the same box, so the element
  stiffness is linear in the 21 independent entries of C: Ke = sum_ij C_ij K_ij, with the 21 basis
  matrices K_ij computed once. A chunk of elements is then one matrix product.
- Supports and contact are penalty springs on 3 x 3 diagonal blocks: k I for a fixed node, k n n^T
  for a node held along a normal n (frictionless contact, a sliding support).
- Solver: pyamg smoothed aggregation on 3 x 3 blocks, with the six rigid-body modes as its
  near-null space, as the preconditioner for CG. Or DirectSolver: a sparse Cholesky factorisation
  (MKL PARDISO), kept as CG's preconditioner while the contact set changes under it.
"""
from __future__ import annotations

import time

import numpy as np
import pyamg
import scipy.sparse as sp
from scipy.sparse.linalg import LinearOperator, cg

CORNERS = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
IU = np.triu_indices(6)


def b_matrix(xi: np.ndarray, h: np.ndarray) -> np.ndarray:
    """6 x 24 strain-displacement matrix of a brick of size h at natural coordinates xi in [-1, 1]^3."""
    s = 2 * CORNERS - 1
    dN = np.empty((8, 3))
    for k in range(3):
        o = [m for m in range(3) if m != k]
        dN[:, k] = s[:, k] / 8 * (1 + s[:, o[0]] * xi[o[0]]) * (1 + s[:, o[1]] * xi[o[1]]) * 2 / h[k]
    B = np.zeros((6, 24))
    for a in range(8):
        dx, dy, dz = dN[a]
        B[0, 3 * a], B[1, 3 * a + 1], B[2, 3 * a + 2] = dx, dy, dz
        B[3, 3 * a + 1], B[3, 3 * a + 2] = dz, dy
        B[4, 3 * a], B[4, 3 * a + 2] = dz, dx
        B[5, 3 * a], B[5, 3 * a + 1] = dy, dx
    return B


class Brick:
    """Basis stiffness matrices for one voxel size."""

    def __init__(self, h):
        self.h = np.asarray(h, float)
        g = 1 / np.sqrt(3)
        self.Bg = np.array([b_matrix(np.array([a, b, c]), self.h) for c in (-g, g) for b in (-g, g) for a in (-g, g)])
        self.Bc = b_matrix(np.zeros(3), self.h)
        vol = float(np.prod(self.h))
        self.Kb = np.empty((21, 576))
        for n, (i, j) in enumerate(zip(*IU)):
            E = np.zeros((6, 6))
            E[i, j] = E[j, i] = 1.0
            self.Kb[n] = (np.einsum("gai,ab,gbj->ij", self.Bg, E, self.Bg) * vol / 8).ravel()


def c21(C: np.ndarray) -> np.ndarray:
    """(..., 6, 6) -> (..., 21) upper triangle, as Brick.Kb expects."""
    return C[..., IU[0], IU[1]]


class VoxelModel:
    """Solid voxels at integer grid indices ijk (n, 3), each with a 6 x 6 stiffness C (n, 6, 6).
    origin + (ijk + 0.5) * h is a voxel centre; nodes sit at origin + node_ijk * h."""

    def __init__(self, ijk: np.ndarray, C: np.ndarray, h, origin, assemble: bool = True):
        self.ijk = np.asarray(ijk, np.int64)
        self.h = np.asarray(h, float)
        self.origin = np.asarray(origin, float)
        corner = (self.ijk[:, None, :] + CORNERS[None]).reshape(-1, 3)
        dims = corner.max(axis=0) + 1
        key = (corner[:, 0] * dims[1] + corner[:, 1]) * dims[2] + corner[:, 2]
        ukey, inv = np.unique(key, return_inverse=True)
        self.conn = inv.reshape(-1, 8)
        self.node_ijk = np.column_stack([ukey // (dims[1] * dims[2]), (ukey // dims[2]) % dims[1], ukey % dims[2]])
        self.x = self.origin + self.node_ijk * self.h
        self.n_nodes = len(ukey)
        self.brick = Brick(self.h)
        self.C = C
        self.K = self._assemble(c21(C)) if assemble else None      # not needed to re-read a solution
        # nodes on the outer surface: any of their 8 surrounding voxels missing
        cnt = np.bincount(self.conn.ravel(), minlength=self.n_nodes)
        self.surface = cnt < 8

    def _assemble(self, Cv: np.ndarray, chunk: int = 40000) -> sp.csr_matrix:
        t0 = time.time()
        ndof = 3 * self.n_nodes
        dofs = (3 * self.conn[:, :, None] + np.arange(3)).reshape(-1, 24).astype(np.int32)
        K = None
        for s in range(0, len(dofs), chunk):
            d = dofs[s:s + chunk]
            vals = Cv[s:s + chunk] @ self.brick.Kb
            rows = np.repeat(d, 24, axis=1).ravel()
            cols = np.tile(d, (1, 24)).ravel()
            Kc = sp.csr_matrix((vals.ravel(), (rows, cols)), shape=(ndof, ndof))
            K = Kc if K is None else K + Kc
        self.assembly_s = time.time() - t0
        return K

    def rigid_modes(self) -> np.ndarray:
        x = self.x - self.x.mean(axis=0)
        B = np.zeros((3 * self.n_nodes, 6))
        for k in range(3):
            B[k::3, k] = 1.0
        B[0::3, 3], B[1::3, 3] = -x[:, 1], x[:, 0]
        B[1::3, 4], B[2::3, 4] = -x[:, 2], x[:, 1]
        B[0::3, 5], B[2::3, 5] = x[:, 2], -x[:, 0]
        return B

    def penalty_matrix(self, nodes: np.ndarray, blocks: np.ndarray) -> sp.csr_matrix:
        """Sparse matrix with a 3 x 3 block (nodes, 3, 3) on each listed node's diagonal."""
        r = (3 * nodes[:, None, None] + np.arange(3)[None, :, None]).repeat(3, axis=2)
        c = (3 * nodes[:, None, None] + np.arange(3)[None, None, :]).repeat(3, axis=1)
        n = 3 * self.n_nodes
        return sp.csr_matrix((blocks.ravel(), (r.ravel(), c.ravel())), shape=(n, n))

    def stiffness_scale(self) -> float:
        return float(np.median(self.K.diagonal()[self.K.diagonal() > 0]))


class Solver:
    """K + P with an AMG hierarchy, reusable as a preconditioner when P changes a little (contact).

    The operator is applied as K u + P u, so K + P is only formed (as 3 x 3 blocks) to build a
    hierarchy. A hierarchy built for one contact set is kept for the next while CG still converges in
    `rebuild_after` iterations; past that it is rebuilt for the current operator and CG carries on from
    where it stopped. At 0.6 mm voxels a rebuild costs about as much as 25 CG iterations."""

    def __init__(self, model: VoxelModel, P: sp.csr_matrix, rebuild_after: int = 25):
        self.model, self.rebuild_after = model, rebuild_after
        self.rebuilds, self.setup_total_s, self.ml = 0, 0.0, None
        self.set_operator(P, rebuild=True)

    def set_operator(self, P: sp.csr_matrix, rebuild: bool = False):
        self.P = P.tocsr()
        n = self.P.shape[0]
        self.A = LinearOperator((n, n), matvec=lambda x: self.model.K @ x + self.P @ x, dtype=float)
        if rebuild or self.ml is None:
            self._build()

    def _build(self):
        t0 = time.time()
        self.ml = self.M = None
        Ab = (self.model.K + self.P).tobsr(blocksize=(3, 3))
        self.ml = pyamg.smoothed_aggregation_solver(
            Ab, B=self.model.rigid_modes(), strength=("symmetric", {"theta": 0.0}), smooth="jacobi",
            presmoother=("block_gauss_seidel", {"sweep": "symmetric"}),
            postsmoother=("block_gauss_seidel", {"sweep": "symmetric"}),
            max_coarse=300, max_levels=15, coarse_solver="splu")   # pyamg's default dense pinv stalls
        self.M = self.ml.aspreconditioner(cycle="V")
        self.rebuilds += 1
        self.setup_s = time.time() - t0
        self.setup_total_s += self.setup_s

    def solve(self, f: np.ndarray, x0: np.ndarray | None = None, rtol: float = 1e-8, maxiter: int = 2000):
        t0 = time.time()
        total, rebuilt = 0, False
        for attempt in range(2):
            it = [0]

            def cb(_):
                it[0] += 1
            limit = self.rebuild_after if attempt == 0 else maxiter
            u, info = cg(self.A, f, x0=x0, rtol=rtol, maxiter=limit, M=self.M, callback=cb)
            total += it[0]
            if info == 0:
                break
            if attempt == 1:
                raise RuntimeError(f"CG did not converge ({info}) in {it[0]} iterations on a fresh hierarchy")
            self._build()
            rebuilt, x0 = True, u
        return u, {"cg_iterations": total, "solve_s": round(time.time() - t0, 1), "rebuilt": rebuilt}


class DirectSolver:
    """K + P by sparse Cholesky (MKL PARDISO through pypardiso), with Solver's interface.

    At 0.6 mm voxels a clamp model has 1.6 M dofs or more. There pyamg's setup takes minutes and its
    smoothers run on one core, and the contact loop wants a new hierarchy whenever many contacts flip.
    A factorisation is one multithreaded pass instead. The contact loop changes P on a few hundred rows
    at a time, so the last factorisation is kept as CG's preconditioner on each new operator (the error
    is then a low-rank change, and CG removes it in a few iterations). It is redone only when CG needs
    more than `refactor_after` iterations, or when set_operator is told to rebuild. The operator is
    applied as K u + P u, so K + P is only ever formed as its upper triangle, for PARDISO."""

    def __init__(self, model, P: sp.csr_matrix, refactor_after: int = 30):
        self.model, self.refactor_after = model, refactor_after
        self.ps, self.factorisations, self.factor_s, self.stale = None, 0, 0.0, True
        self.Ku = sp.triu(model.K, format="csr")
        self.set_operator(P)
        self._factorise()

    def set_operator(self, P: sp.csr_matrix, rebuild: bool = False):
        self.P = P.tocsr()
        n = self.P.shape[0]
        self.A = LinearOperator((n, n), matvec=lambda x: self.model.K @ x + self.P @ x, dtype=float)
        self.stale = self.stale or rebuild

    def _factorise(self):
        from pypardiso import PyPardisoSolver
        t0 = time.time()
        if self.ps is not None:
            self.ps.free_memory(everything=True)
            self.ps = None
        U = (self.Ku + sp.triu(self.P, format="csr")).tocsr()
        U.sort_indices()
        ps = PyPardisoSolver(mtype=2)        # real symmetric positive definite: Cholesky, upper triangle
        ps.iparm[0] = 1                      # the values set here; defaults for the rest
        ps.iparm[1] = 3                      # nested dissection ordering, the parallel (OpenMP) METIS
        ps.iparm[9] = 8                      # pivot perturbation 1e-8, should a pivot be tiny
        ps.iparm[17] = -1                    # report the factor's nonzeros
        ps.set_phase(12)
        ps._call_pardiso(U, np.zeros(U.shape[0]))
        self.ps, self.U = ps, U
        self.nnz_L = int(ps.iparm[17])
        self.factorisations += 1
        self.stale = False
        self.setup_s = time.time() - t0
        self.factor_s += self.setup_s

    def _apply(self, r: np.ndarray) -> np.ndarray:
        self.ps.set_phase(33)
        return self.ps._call_pardiso(self.U, np.ascontiguousarray(r, dtype=float))

    def solve(self, f: np.ndarray, x0: np.ndarray | None = None, rtol: float = 1e-8, maxiter: int = 2000):
        t0 = time.time()
        if self.stale:
            self._factorise()
        n = len(f)
        M = LinearOperator((n, n), matvec=self._apply, dtype=float)
        total, refactored = 0, False
        for attempt in range(2):
            it = [0]

            def cb(_):
                it[0] += 1
            limit = self.refactor_after if attempt == 0 else maxiter
            u, info = cg(self.A, f, x0=x0, rtol=rtol, maxiter=limit, M=M, callback=cb)
            total += it[0]
            if info == 0:
                break
            if attempt == 1:
                raise RuntimeError(f"CG did not converge ({info}) in {it[0]} iterations on a fresh factorisation")
            self._factorise()
            refactored, x0 = True, u
        return u, {"cg_iterations": total, "solve_s": round(time.time() - t0, 1), "refactorised": refactored,
                   "factorisations so far": self.factorisations}


def strains(model: VoxelModel, U: np.ndarray) -> np.ndarray:
    """Strain at each voxel centre, (n, 6). U is (3 n_nodes,) or (n_nodes, 3)."""
    U = U.reshape(-1, 3)
    ue = U[model.conn].reshape(len(model.conn), 24)
    return ue @ model.brick.Bc.T


def stresses(model: VoxelModel, U: np.ndarray) -> np.ndarray:
    return np.einsum("nij,nj->ni", model.C, strains(model, U))


def isotropic(E: float, nu: float) -> np.ndarray:
    lam, mu = E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))
    C = np.zeros((6, 6))
    C[:3, :3] = lam
    C[np.arange(3), np.arange(3)] += 2 * mu
    C[np.arange(3, 6), np.arange(3, 6)] = mu
    return C


def orthotropic(E1, E2, E3, G12, G13, G23, nu12, nu13, nu23) -> np.ndarray:
    """Stiffness in the material axes (1, 2, 3), Voigt order 11 22 33 23 13 12."""
    S = np.zeros((6, 6))
    S[0, 0], S[1, 1], S[2, 2] = 1 / E1, 1 / E2, 1 / E3
    S[0, 1] = S[1, 0] = -nu12 / E1
    S[0, 2] = S[2, 0] = -nu13 / E1
    S[1, 2] = S[2, 1] = -nu23 / E2
    S[3, 3], S[4, 4], S[5, 5] = 1 / G23, 1 / G13, 1 / G12
    return np.linalg.inv(S)


def bond(R: np.ndarray) -> np.ndarray:
    """6 x 6 Bond matrix M for a rotation R (new_i = R_ij old_j): C_new = M C_old M^T, for stress-like
    Voigt vectors with engineering shear strain (the stiffness transformation)."""
    R = np.asarray(R)
    pairs = [(0, 0), (1, 1), (2, 2), (1, 2), (0, 2), (0, 1)]
    M = np.zeros(R.shape[:-2] + (6, 6))
    for I, (i, j) in enumerate(pairs):
        for J, (k, l) in enumerate(pairs):
            if J < 3:
                M[..., I, J] = R[..., i, k] * R[..., j, l]
            else:
                M[..., I, J] = R[..., i, k] * R[..., j, l] + R[..., i, l] * R[..., j, k]
    return M


def rotate_stress(s: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Voigt stress (..., 6) into axes rotated by R (rows = new axes in old coordinates)."""
    return np.einsum("...ij,...j->...i", bond(R), s)

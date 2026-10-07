"""Fitting planes, cylinders, spheres and tori to mesh vertices, and small mesh helpers."""
from collections import deque

import numpy as np
from scipy.optimize import least_squares


def orth_basis(a):
    t = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(a, t)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(a, e1)


def circle2d(x, y):
    A = np.c_[x, y, np.ones_like(x)]
    D, E, Fc = np.linalg.lstsq(A, -(x * x + y * y), rcond=None)[0]
    cx, cy = -D / 2, -E / 2
    return cx, cy, np.sqrt(max(cx * cx + cy * cy - Fc, 1e-12))


def dist(m, Q):
    """Signed distance of points Q from surface m (positive on the side the surface normal points to)."""
    t = m["type"]
    if t == "plane":
        return (Q - m["o"]) @ m["n"]
    if t == "sphere":
        return np.linalg.norm(Q - m["c"], axis=1) - m["r"]
    d = Q - m["c"]
    z = d @ m["a"]
    rho = np.linalg.norm(d - np.outer(z, m["a"]), axis=1)
    if t == "cylinder":
        return rho - m["r"]
    if t == "torus":
        return np.hypot(rho - m["R"], z) - m["r"]
    if t == "cone":  # apex c, axis a (opening direction), half angle h
        return rho * np.cos(m["h"]) - z * np.sin(m["h"])
    raise ValueError(t)


def normal(m, Q):
    """Unit normal of surface m at (points near) Q, pointing the way dist() grows."""
    t = m["type"]
    if t == "plane":
        return np.tile(m["n"], (len(Q), 1))
    if t == "sphere":
        d = Q - m["c"]
        return d / np.linalg.norm(d, axis=1)[:, None]
    d = Q - m["c"]
    z = d @ m["a"]
    radial = d - np.outer(z, m["a"])
    rho = np.linalg.norm(radial, axis=1)
    u = radial / rho[:, None]
    if t == "cylinder":
        return u
    if t == "torus":
        v = np.c_[rho - m["R"], z]
        v /= np.linalg.norm(v, axis=1)[:, None]
        return u * v[:, :1] + np.outer(v[:, 1], m["a"])
    if t == "cone":
        return u * np.cos(m["h"]) - np.outer(np.full(len(Q), np.sin(m["h"])), m["a"])
    raise ValueError(t)


def _lsq(fun, x0):
    return least_squares(fun, x0, method="lm", xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=300).x


def fit_plane(Q, N):
    c = Q.mean(0)
    n = np.linalg.svd(Q - c, full_matrices=False)[2][2]
    if n @ N.mean(0) < 0:
        n = -n
    return dict(type="plane", o=c, n=n)


def fit_sphere(Q, N):
    A = np.c_[2 * Q, np.ones(len(Q))]
    s = np.linalg.lstsq(A, (Q * Q).sum(1), rcond=None)[0]
    c0 = s[:3]
    r0 = np.sqrt(max(s[3] + c0 @ c0, 1e-12))

    def res(p):
        return np.linalg.norm(Q - p[:3], axis=1) - p[3]

    p = _lsq(res, np.r_[c0, r0])
    return dict(type="sphere", c=p[:3], r=abs(p[3]))


def fit_cylinder(Q, N, a0=None):
    if a0 is None:
        a0 = np.linalg.eigh(N.T @ N)[1][:, 0]
    e1, e2 = orth_basis(a0)
    q0 = Q.mean(0)
    cx, cy, r0 = circle2d((Q - q0) @ e1, (Q - q0) @ e2)
    c0 = q0 + cx * e1 + cy * e2

    def unpack(p):
        a = a0 + p[0] * e1 + p[1] * e2
        a /= np.linalg.norm(a)
        return c0 + p[2] * e1 + p[3] * e2, a, p[4]

    def res(p):
        c, a, r = unpack(p)
        d = Q - c
        return np.linalg.norm(d - np.outer(d @ a, a), axis=1) - r

    c, a, r = unpack(_lsq(res, [0, 0, 0, 0, r0]))
    c = c + ((q0 - c) @ a) * a
    return dict(type="cylinder", c=c, a=a, r=abs(r))


def torus_from_axis(Q, p0, a):
    z = (Q - p0) @ a
    rho = np.linalg.norm((Q - p0) - np.outer(z, a), axis=1)
    R, z0, r = circle2d(rho, z)
    return p0 + z0 * a, R, r


def fit_torus(Q, N, G):
    A = np.c_[np.cross(G, N), N]
    x = np.linalg.svd(A, full_matrices=False)[2][-1]
    d, m = x[:3], x[3:]
    if np.linalg.norm(d) < 1e-9:
        return None
    a0 = d / np.linalg.norm(d)
    p0 = np.cross(d, m) / (d @ d)
    c0, R0, r0 = torus_from_axis(Q, p0, a0)
    e1, e2 = orth_basis(a0)

    def unpack(p):
        a = a0 + p[0] * e1 + p[1] * e2
        a /= np.linalg.norm(a)
        return c0 + p[2:5], a, p[5], p[6]

    def res(p):
        c, a, R, r = unpack(p)
        d = Q - c
        z = d @ a
        rho = np.linalg.norm(d - np.outer(z, a), axis=1)
        return np.hypot(rho - R, z) - r

    c, a, R, r = unpack(_lsq(res, [0, 0, 0, 0, 0, R0, r0]))
    return dict(type="torus", c=c, a=a, R=R, r=abs(r))


ORDER = ["plane", "cylinder", "sphere", "torus"]


COS_N = np.cos(np.radians(8))


def normal_ok(m, N, G):
    """Facet normals agree with the surface normal at the facet centroids (either orientation)."""
    return bool((np.abs(np.sum(normal(m, G) * N, axis=1)) > COS_N).all())


def sane(m):
    """Reject degenerate fits: radii far beyond the part's size, spindle tori."""
    t = m["type"]
    if t in ("cylinder", "sphere"):
        return 0 < m["r"] < 60
    if t == "torus":
        return 0 < m["r"] < 20 and m["r"] < m["R"] < 60
    return True


def fit_best(Q, N, G, tol, kinds=ORDER):
    """Simplest surface fitting all points Q within tol; returns (model, max residual) or (None, best residual)."""
    best = (None, np.inf)
    for k in kinds:
        try:
            if k == "plane":
                m = fit_plane(Q, N)
            elif k == "sphere":
                m = fit_sphere(Q, N)
            elif k == "cylinder":
                m = fit_cylinder(Q, N)
            else:
                m = fit_torus(Q, N, G)
        except Exception:
            m = None
        if m is None:
            continue
        r = np.abs(dist(m, Q)).max()
        if not np.isfinite(r) or not sane(m):
            continue
        if r < tol and normal_ok(m, N, G):
            return m, r
        if r < best[1]:
            best = (m, r)
    return None, best[1]


def bfs_patch(seed, nbr, allowed, size):
    seen = {seed}
    q = deque([seed])
    out = []
    while q and len(out) < size:
        t = q.popleft()
        out.append(t)
        for u in nbr[t]:
            if u not in seen and allowed[u]:
                seen.add(u)
                q.append(u)
    return out

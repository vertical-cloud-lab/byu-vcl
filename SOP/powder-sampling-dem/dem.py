"""A small soft-sphere DEM for the powder-sampling animations.

Linear spring-dashpot normal force, Cundall-Strack tangential spring with Coulomb
friction, rolling resistance, and a constant pull-off force between particles in
contact (mild cohesion). Tools are rigid bodies that move on a prescribed path:
either a solid of revolution (a convex polygon in the r-z plane, so tubes, disks,
rods and cones) or a box. SI units throughout.

The particles are coarse-grained, about 1 mm across instead of 15-63 um, so this
shows how the bed moves around a tool at the scale of the tool, not what happens
at the scale of single particles. See README.md for what that does and doesn't
let us conclude.
"""

import math

import numpy as np
from numba import njit, prange

MAXC = 16  # contact-history slots per particle (particle-particle)
MAXW = 6  # contact-history slots per particle (particle-tool)

REVOLVE = 0
BOX = 1

FREE, DEAD, ASLEEP = 0, 1, 2


@njit(cache=True)
def _closest_revolve(lx, ly, lz, poly, npoly):
    """Closest surface point of a solid of revolution, in its local frame.

    Returns (nx, ny, nz, cx, cy, cz, d): unit vector from the point toward the
    surface, the surface point, and the signed distance (negative inside).
    """
    r = math.sqrt(lx * lx + ly * ly)
    if r > 1e-12:
        erx = lx / r
        ery = ly / r
    else:
        erx = 1.0
        ery = 0.0
    inside = True
    best_s = -1e30
    bnr = 0.0
    bnz = 0.0
    for k in range(npoly):
        ar = poly[k, 0]
        az = poly[k, 1]
        k2 = k + 1 if k + 1 < npoly else 0
        br = poly[k2, 0]
        bz = poly[k2, 1]
        if ar == 0.0 and br == 0.0:
            continue  # the axis is not a surface
        er = br - ar
        ez = bz - az
        L = math.sqrt(er * er + ez * ez)
        nr = ez / L
        nz = -er / L
        s = (r - ar) * nr + (lz - az) * nz
        if s > 0.0:
            inside = False
        if s > best_s:
            best_s = s
            bnr = nr
            bnz = nz
    if inside:
        c_r = r - best_s * bnr
        c_z = lz - best_s * bnz
        return (-bnr * erx, -bnr * ery, -bnz, c_r * erx, c_r * ery, c_z, best_s)
    best_d2 = 1e30
    c_r = 0.0
    c_z = 0.0
    for k in range(npoly):
        ar = poly[k, 0]
        az = poly[k, 1]
        k2 = k + 1 if k + 1 < npoly else 0
        br = poly[k2, 0]
        bz = poly[k2, 1]
        if ar == 0.0 and br == 0.0:
            continue
        er = br - ar
        ez = bz - az
        t = ((r - ar) * er + (lz - az) * ez) / (er * er + ez * ez)
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
        qr = ar + t * er
        qz = az + t * ez
        d2 = (qr - r) ** 2 + (qz - lz) ** 2
        if d2 < best_d2:
            best_d2 = d2
            c_r = qr
            c_z = qz
    d = math.sqrt(best_d2)
    if d < 1e-15:
        return (-erx, -ery, 0.0, c_r * erx, c_r * ery, c_z, 0.0)
    n_r = (c_r - r) / d
    n_z = (c_z - lz) / d
    return (n_r * erx, n_r * ery, n_z, c_r * erx, c_r * ery, c_z, d)


@njit(cache=True)
def _closest_box(lx, ly, lz, hx, hy, hz):
    cx = min(max(lx, -hx), hx)
    cy = min(max(ly, -hy), hy)
    cz = min(max(lz, -hz), hz)
    dx = cx - lx
    dy = cy - ly
    dz = cz - lz
    d2 = dx * dx + dy * dy + dz * dz
    if d2 > 0.0:
        d = math.sqrt(d2)
        return (dx / d, dy / d, dz / d, cx, cy, cz, d)
    px = hx - abs(lx)
    py = hy - abs(ly)
    pz = hz - abs(lz)
    if px <= py and px <= pz:
        s = 1.0 if lx >= 0 else -1.0
        return (-s, 0.0, 0.0, s * hx, ly, lz, -px)
    if py <= pz:
        s = 1.0 if ly >= 0 else -1.0
        return (0.0, -s, 0.0, lx, s * hy, lz, -py)
    s = 1.0 if lz >= 0 else -1.0
    return (0.0, 0.0, -s, lx, ly, s * hz, -pz)


@njit(cache=True)
def _build_grid(x, mode, cs):
    n = x.shape[0]
    lo = np.full(3, 1e30)
    hi = np.full(3, -1e30)
    nalive = 0
    for i in range(n):
        if mode[i] == DEAD:
            continue
        nalive += 1
        for a in range(3):
            if x[i, a] < lo[a]:
                lo[a] = x[i, a]
            if x[i, a] > hi[a]:
                hi[a] = x[i, a]
    dims = np.empty(3, np.int64)
    for a in range(3):
        lo[a] -= cs
        dims[a] = int((hi[a] - lo[a]) / cs) + 2
    ncell = dims[0] * dims[1] * dims[2]
    count = np.zeros(ncell, np.int64)
    cell_of = np.full(n, -1, np.int64)
    for i in range(n):
        if mode[i] == DEAD:
            continue
        ix = int((x[i, 0] - lo[0]) / cs)
        iy = int((x[i, 1] - lo[1]) / cs)
        iz = int((x[i, 2] - lo[2]) / cs)
        c = (iz * dims[1] + iy) * dims[0] + ix
        cell_of[i] = c
        count[c] += 1
    start = np.zeros(ncell, np.int64)
    acc = 0
    for c in range(ncell):
        start[c] = acc
        acc += count[c]
    fill = start.copy()
    ids = np.empty(nalive, np.int64)
    for i in range(n):
        c = cell_of[i]
        if c >= 0:
            ids[fill[c]] = i
            fill[c] += 1
    return lo, dims, start, count, ids


@njit(parallel=True, cache=True)
def _forces(x, v, w, rad, mass, inertia, mode, extf,
            lo, dims, start, count, ids, cs,
            hj, hxi, nhj, nhxi, wp, wxi, nwp, nwxi,
            gtype, gpoly, gnpoly, ghalf, gmu, gpos, grot, gvel, gomg, gon,
            kn, kt, beta, mu, mu_r, fcoh, gz, dt, F, T):
    n = x.shape[0]
    ng = gtype.shape[0]
    for i in prange(n):
        F[i, 0] = 0.0
        F[i, 1] = 0.0
        F[i, 2] = 0.0
        T[i, 0] = 0.0
        T[i, 1] = 0.0
        T[i, 2] = 0.0
        for k in range(MAXC):
            nhj[i, k] = -1
        for k in range(MAXW):
            nwp[i, k] = -1
        if mode[i] != FREE:
            continue
        mi = mass[i]
        ri = rad[i]
        fx = extf[i, 0]
        fy = extf[i, 1]
        fz = extf[i, 2] - mi * gz
        tx = 0.0
        ty = 0.0
        tz = 0.0
        nc = 0
        ix = int((x[i, 0] - lo[0]) / cs)
        iy = int((x[i, 1] - lo[1]) / cs)
        iz = int((x[i, 2] - lo[2]) / cs)
        for ddz in range(-1, 2):
            cz_ = iz + ddz
            if cz_ < 0 or cz_ >= dims[2]:
                continue
            for ddy in range(-1, 2):
                cy_ = iy + ddy
                if cy_ < 0 or cy_ >= dims[1]:
                    continue
                for ddx in range(-1, 2):
                    cx_ = ix + ddx
                    if cx_ < 0 or cx_ >= dims[0]:
                        continue
                    c = (cz_ * dims[1] + cy_) * dims[0] + cx_
                    for s in range(start[c], start[c] + count[c]):
                        j = ids[s]
                        if j == i:
                            continue
                        dx = x[j, 0] - x[i, 0]
                        dy = x[j, 1] - x[i, 1]
                        dz = x[j, 2] - x[i, 2]
                        rs = ri + rad[j]
                        d2 = dx * dx + dy * dy + dz * dz
                        if d2 >= rs * rs:
                            continue
                        d = math.sqrt(d2)
                        nx = dx / d
                        ny = dy / d
                        nz = dz / d
                        delta = rs - d
                        rj = rad[j]
                        # velocity of i relative to j at the contact point
                        vx = v[i, 0] - v[j, 0] + (w[i, 1] * nz - w[i, 2] * ny) * ri + (w[j, 1] * nz - w[j, 2] * ny) * rj
                        vy = v[i, 1] - v[j, 1] + (w[i, 2] * nx - w[i, 0] * nz) * ri + (w[j, 2] * nx - w[j, 0] * nz) * rj
                        vz = v[i, 2] - v[j, 2] + (w[i, 0] * ny - w[i, 1] * nx) * ri + (w[j, 0] * ny - w[j, 1] * nx) * rj
                        vn = vx * nx + vy * ny + vz * nz
                        meff = mi * mass[j] / (mi + mass[j])
                        gn = 2.0 * beta * math.sqrt(meff * kn)
                        fn = kn * delta + gn * vn
                        if fn < 0.0:
                            fn = 0.0
                        ftot = fn - fcoh
                        vtx = vx - vn * nx
                        vty = vy - vn * ny
                        vtz = vz - vn * nz
                        xix = 0.0
                        xiy = 0.0
                        xiz = 0.0
                        for k in range(MAXC):
                            if hj[i, k] < 0:
                                break
                            if hj[i, k] == j:
                                xix = hxi[i, k, 0]
                                xiy = hxi[i, k, 1]
                                xiz = hxi[i, k, 2]
                                break
                        p = xix * nx + xiy * ny + xiz * nz
                        xix = xix - p * nx + vtx * dt
                        xiy = xiy - p * ny + vty * dt
                        xiz = xiz - p * nz + vtz * dt
                        lim = mu * fn
                        xm = math.sqrt(xix * xix + xiy * xiy + xiz * xiz)
                        if kt * xm > lim and xm > 0.0:
                            sc = lim / (kt * xm)
                            xix *= sc
                            xiy *= sc
                            xiz *= sc
                        gt = gn
                        ftx = -kt * xix - gt * vtx
                        fty = -kt * xiy - gt * vty
                        ftz = -kt * xiz - gt * vtz
                        fm = math.sqrt(ftx * ftx + fty * fty + ftz * ftz)
                        if fm > lim and fm > 0.0:
                            sc = lim / fm
                            ftx *= sc
                            fty *= sc
                            ftz *= sc
                        if nc < MAXC:
                            nhj[i, nc] = j
                            nhxi[i, nc, 0] = xix
                            nhxi[i, nc, 1] = xiy
                            nhxi[i, nc, 2] = xiz
                            nc += 1
                        fx += -ftot * nx + ftx
                        fy += -ftot * ny + fty
                        fz += -ftot * nz + ftz
                        # torque (ri n) x Ft
                        tx += ri * (ny * ftz - nz * fty)
                        ty += ri * (nz * ftx - nx * ftz)
                        tz += ri * (nx * fty - ny * ftx)
                        # rolling resistance, capped so it can't reverse the spin in a step
                        wrx = w[i, 0] - w[j, 0]
                        wry = w[i, 1] - w[j, 1]
                        wrz = w[i, 2] - w[j, 2]
                        wm = math.sqrt(wrx * wrx + wry * wry + wrz * wrz)
                        if wm > 1e-12:
                            mr = mu_r * (ri * rj / (ri + rj)) * fn
                            cap = 0.5 * inertia[i] * wm / dt
                            if mr > cap:
                                mr = cap
                            tx -= mr * wrx / wm
                            ty -= mr * wry / wm
                            tz -= mr * wrz / wm
        # tools
        nw = 0
        for g in range(ng):
            if not gon[g]:
                continue
            ox = x[i, 0] - gpos[g, 0]
            oy = x[i, 1] - gpos[g, 1]
            oz = x[i, 2] - gpos[g, 2]
            # local = R^T (x - pos)
            lx = grot[g, 0, 0] * ox + grot[g, 1, 0] * oy + grot[g, 2, 0] * oz
            ly = grot[g, 0, 1] * ox + grot[g, 1, 1] * oy + grot[g, 2, 1] * oz
            lz = grot[g, 0, 2] * ox + grot[g, 1, 2] * oy + grot[g, 2, 2] * oz
            if gtype[g] == REVOLVE:
                lnx, lny, lnz, lcx, lcy, lcz, dd = _closest_revolve(lx, ly, lz, gpoly[g], gnpoly[g])
            else:
                lnx, lny, lnz, lcx, lcy, lcz, dd = _closest_box(lx, ly, lz, ghalf[g, 0], ghalf[g, 1], ghalf[g, 2])
            if dd >= ri:
                continue
            delta = ri - dd
            nx = grot[g, 0, 0] * lnx + grot[g, 0, 1] * lny + grot[g, 0, 2] * lnz
            ny = grot[g, 1, 0] * lnx + grot[g, 1, 1] * lny + grot[g, 1, 2] * lnz
            nz = grot[g, 2, 0] * lnx + grot[g, 2, 1] * lny + grot[g, 2, 2] * lnz
            # contact point (world, relative to tool origin)
            qx = grot[g, 0, 0] * lcx + grot[g, 0, 1] * lcy + grot[g, 0, 2] * lcz
            qy = grot[g, 1, 0] * lcx + grot[g, 1, 1] * lcy + grot[g, 1, 2] * lcz
            qz = grot[g, 2, 0] * lcx + grot[g, 2, 1] * lcy + grot[g, 2, 2] * lcz
            vwx = gvel[g, 0] + gomg[g, 1] * qz - gomg[g, 2] * qy
            vwy = gvel[g, 1] + gomg[g, 2] * qx - gomg[g, 0] * qz
            vwz = gvel[g, 2] + gomg[g, 0] * qy - gomg[g, 1] * qx
            vx = v[i, 0] + (w[i, 1] * nz - w[i, 2] * ny) * ri - vwx
            vy = v[i, 1] + (w[i, 2] * nx - w[i, 0] * nz) * ri - vwy
            vz = v[i, 2] + (w[i, 0] * ny - w[i, 1] * nx) * ri - vwz
            vn = vx * nx + vy * ny + vz * nz
            gn = 2.0 * beta * math.sqrt(mi * kn)
            fn = kn * delta + gn * vn
            if fn < 0.0:
                fn = 0.0
            vtx = vx - vn * nx
            vty = vy - vn * ny
            vtz = vz - vn * nz
            xix = 0.0
            xiy = 0.0
            xiz = 0.0
            for k in range(MAXW):
                if wp[i, k] < 0:
                    break
                if wp[i, k] == g:
                    xix = wxi[i, k, 0]
                    xiy = wxi[i, k, 1]
                    xiz = wxi[i, k, 2]
                    break
            p = xix * nx + xiy * ny + xiz * nz
            xix = xix - p * nx + vtx * dt
            xiy = xiy - p * ny + vty * dt
            xiz = xiz - p * nz + vtz * dt
            lim = gmu[g] * fn
            xm = math.sqrt(xix * xix + xiy * xiy + xiz * xiz)
            if kt * xm > lim and xm > 0.0:
                sc = lim / (kt * xm)
                xix *= sc
                xiy *= sc
                xiz *= sc
            ftx = -kt * xix - gn * vtx
            fty = -kt * xiy - gn * vty
            ftz = -kt * xiz - gn * vtz
            fm = math.sqrt(ftx * ftx + fty * fty + ftz * ftz)
            if fm > lim and fm > 0.0:
                sc = lim / fm
                ftx *= sc
                fty *= sc
                ftz *= sc
            if nw < MAXW:
                nwp[i, nw] = g
                nwxi[i, nw, 0] = xix
                nwxi[i, nw, 1] = xiy
                nwxi[i, nw, 2] = xiz
                nw += 1
            fx += -fn * nx + ftx
            fy += -fn * ny + fty
            fz += -fn * nz + ftz
            tx += ri * (ny * ftz - nz * fty)
            ty += ri * (nz * ftx - nx * ftz)
            tz += ri * (nx * fty - ny * ftx)
            wm = math.sqrt(w[i, 0] ** 2 + w[i, 1] ** 2 + w[i, 2] ** 2)
            if wm > 1e-12:
                mr = mu_r * ri * fn
                cap = 0.5 * inertia[i] * wm / dt
                if mr > cap:
                    mr = cap
                tx -= mr * w[i, 0] / wm
                ty -= mr * w[i, 1] / wm
                tz -= mr * w[i, 2] / wm
        F[i, 0] = fx
        F[i, 1] = fy
        F[i, 2] = fz
        T[i, 0] = tx
        T[i, 1] = ty
        T[i, 2] = tz


@njit(parallel=True, cache=True)
def _integrate(x, v, w, mass, inertia, mode, F, T, dt):
    for i in prange(x.shape[0]):
        if mode[i] != FREE:
            continue
        for a in range(3):
            v[i, a] += F[i, a] / mass[i] * dt
            w[i, a] += T[i, a] / inertia[i] * dt
            x[i, a] += v[i, a] * dt


@njit(cache=True)
def _advance_tools(gpos, grot, gvel, gomg, dt):
    for g in range(gpos.shape[0]):
        for a in range(3):
            gpos[g, a] += gvel[g, a] * dt
        wx = gomg[g, 0] * dt
        wy = gomg[g, 1] * dt
        wz = gomg[g, 2] * dt
        th = math.sqrt(wx * wx + wy * wy + wz * wz)
        if th < 1e-14:
            continue
        kx = wx / th
        ky = wy / th
        kz = wz / th
        c = math.cos(th)
        s = math.sin(th)
        C = 1.0 - c
        R = np.empty((3, 3))
        R[0, 0] = c + kx * kx * C
        R[0, 1] = kx * ky * C - kz * s
        R[0, 2] = kx * kz * C + ky * s
        R[1, 0] = ky * kx * C + kz * s
        R[1, 1] = c + ky * ky * C
        R[1, 2] = ky * kz * C - kx * s
        R[2, 0] = kz * kx * C - ky * s
        R[2, 1] = kz * ky * C + kx * s
        R[2, 2] = c + kz * kz * C
        grot[g] = R @ grot[g]


@njit(cache=True)
def run_steps(nsteps, x, v, w, rad, mass, inertia, mode, extf,
              hj, hxi, nhj, nhxi, wp, wxi, nwp, nwxi,
              gtype, gpoly, gnpoly, ghalf, gmu, gpos, grot, gvel, gomg, gon,
              kn, kt, beta, mu, mu_r, fcoh, gz, dt, cs, F, T):
    for s in range(nsteps):
        lo, dims, start, count, ids = _build_grid(x, mode, cs)
        # the contact histories swap buffers each step instead of being copied
        if s % 2 == 0:
            _forces(x, v, w, rad, mass, inertia, mode, extf,
                    lo, dims, start, count, ids, cs,
                    hj, hxi, nhj, nhxi, wp, wxi, nwp, nwxi,
                    gtype, gpoly, gnpoly, ghalf, gmu, gpos, grot, gvel, gomg, gon,
                    kn, kt, beta, mu, mu_r, fcoh, gz, dt, F, T)
        else:
            _forces(x, v, w, rad, mass, inertia, mode, extf,
                    lo, dims, start, count, ids, cs,
                    nhj, nhxi, hj, hxi, nwp, nwxi, wp, wxi,
                    gtype, gpoly, gnpoly, ghalf, gmu, gpos, grot, gvel, gomg, gon,
                    kn, kt, beta, mu, mu_r, fcoh, gz, dt, F, T)
        _integrate(x, v, w, mass, inertia, mode, F, T, dt)
        _advance_tools(gpos, grot, gvel, gomg, dt)
    if nsteps % 2 == 1:
        hj[:] = nhj
        hxi[:] = nhxi
        wp[:] = nwp
        wxi[:] = nwxi


# ---------------------------------------------------------------------------
# Python-side helpers


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def _omega_from(R0, R1, h):
    """Angular velocity that takes R0 to R1 in time h."""
    Q = R1 @ R0.T
    cth = max(-1.0, min(1.0, (np.trace(Q) - 1) / 2))
    th = math.acos(cth)
    if th < 1e-12:
        return np.zeros(3)
    ax = np.array([Q[2, 1] - Q[1, 2], Q[0, 2] - Q[2, 0], Q[1, 0] - Q[0, 1]]) / (2 * math.sin(th))
    return ax * th / h


class Tool:
    """A rigid primitive. `pose(t)` returns (position, rotation, on)."""

    def __init__(self, name, kind, poly=None, half=None, mu=0.3, pose=None, color=(0.6, 0.6, 0.65),
                 alpha=1.0, cut=True):
        self.name = name
        self.kind = kind
        self.poly = np.zeros((8, 2)) if poly is None else np.asarray(poly, float)
        self.half = np.zeros(3) if half is None else np.asarray(half, float)
        self.mu = mu
        self.pose = pose or (lambda t: (np.zeros(3), np.eye(3), True))
        self.color = color
        self.alpha = alpha
        self.cut = cut


def revolve_rect(r0, r1, z0, z1):
    """Counter-clockwise r-z rectangle: a tube wall (r0 > 0) or a disk/rod (r0 = 0)."""
    return [(r0, z0), (r1, z0), (r1, z1), (r0, z1)]


class Sim:
    def __init__(self, dt=2.5e-5, kn=50.0, e=0.3, mu=0.5, mu_r=0.08, bond=1.0, g=9.81,
                 rho=2680.0, d_mean=1.0e-3):
        self.dt = dt
        self.kn = kn
        self.kt = 2.0 / 7.0 * kn
        le = math.log(e)
        self.beta = -le / math.sqrt(math.pi ** 2 + le * le)
        self.mu = mu
        self.mu_r = mu_r
        self.g = g
        self.rho = rho
        m_mean = rho * math.pi / 6 * d_mean ** 3
        self.fcoh = bond * m_mean * g
        self.t = 0.0
        n0 = 0
        self.x = np.zeros((n0, 3))
        self.v = np.zeros((n0, 3))
        self.w = np.zeros((n0, 3))
        self.rad = np.zeros(n0)
        self.mode = np.zeros(n0, np.int64)
        self.extf = np.zeros((n0, 3))
        self.group = np.zeros(n0, np.int64)
        self.label = np.zeros(n0)
        self.tools = []
        # particles that leave this box (fell off a tray, say) are removed, or the neighbour grid
        # would grow without bound as they fall
        self.bounds = (np.array([-0.2, -0.2, -0.04]), np.array([0.2, 0.2, 0.2]))
        self._alloc_hist(n0)

    def _alloc_hist(self, n):
        self.hj = np.full((n, MAXC), -1, np.int64)
        self.hxi = np.zeros((n, MAXC, 3))
        self.wp = np.full((n, MAXW), -1, np.int64)
        self.wxi = np.zeros((n, MAXW, 3))

    @property
    def n(self):
        return self.x.shape[0]

    def add(self, x, r, group, label, v=None):
        k = len(r)
        if k == 0:
            return
        n = self.n
        self.x = np.vstack([self.x, x])
        self.v = np.vstack([self.v, np.zeros((k, 3)) if v is None else v])
        self.w = np.vstack([self.w, np.zeros((k, 3))])
        self.rad = np.concatenate([self.rad, r])
        self.mode = np.concatenate([self.mode, np.zeros(k, np.int64)])
        self.extf = np.vstack([self.extf, np.zeros((k, 3))])
        self.group = np.concatenate([self.group, np.full(k, group, np.int64) if np.isscalar(group) else group])
        self.label = np.concatenate([self.label, label])
        hj, hxi, wp, wxi = self.hj, self.hxi, self.wp, self.wxi
        self._alloc_hist(n + k)
        self.hj[:n] = hj
        self.hxi[:n] = hxi
        self.wp[:n] = wp
        self.wxi[:n] = wxi

    @property
    def mass(self):
        return self.rho * 4.0 / 3.0 * math.pi * self.rad ** 3

    def tool_arrays(self, t, h):
        P = max(1, len(self.tools))
        gtype = np.zeros(P, np.int64)
        gpoly = np.zeros((P, 8, 2))
        gnpoly = np.zeros(P, np.int64)
        ghalf = np.zeros((P, 3))
        gmu = np.zeros(P)
        gpos = np.zeros((P, 3))
        grot = np.tile(np.eye(3), (P, 1, 1))
        gvel = np.zeros((P, 3))
        gomg = np.zeros((P, 3))
        gon = np.zeros(P, np.bool_)
        for k, tl in enumerate(self.tools):
            gtype[k] = REVOLVE if tl.kind == "revolve" else BOX
            if tl.kind == "revolve":
                gpoly[k, : len(tl.poly)] = tl.poly
                gnpoly[k] = len(tl.poly)
            ghalf[k] = tl.half
            gmu[k] = tl.mu
            p0, R0, on0 = tl.pose(t)
            p1, R1, _ = tl.pose(t + h)
            gpos[k] = p0
            grot[k] = R0
            gvel[k] = (np.asarray(p1) - np.asarray(p0)) / h
            gomg[k] = _omega_from(np.asarray(R0), np.asarray(R1), h)
            gon[k] = on0
        return gtype, gpoly, gnpoly, ghalf, gmu, gpos, grot, gvel, gomg, gon

    def advance(self, nsteps, chunk=10, hook=None):
        """Run nsteps, re-reading the tool paths every `chunk` steps."""
        mass = self.mass
        inertia = 0.4 * mass * self.rad ** 2
        n = self.n
        F = np.zeros((n, 3))
        T = np.zeros((n, 3))
        nhj = np.empty_like(self.hj)
        nhxi = np.empty_like(self.hxi)
        nwp = np.empty_like(self.wp)
        nwxi = np.empty_like(self.wxi)
        cs = 2.0 * float(self.rad.max()) * 1.001
        done = 0
        while done < nsteps:
            k = min(chunk, nsteps - done)
            h = k * self.dt
            arrays = self.tool_arrays(self.t, h)
            lo, hi = self.bounds
            gone = (self.mode != DEAD) & np.any((self.x < lo) | (self.x > hi), axis=1)
            if gone.any():
                self.mode[gone] = DEAD
            if hook is not None:
                hook(self)
            run_steps(k, self.x, self.v, self.w, self.rad, mass, inertia, self.mode, self.extf,
                      self.hj, self.hxi, nhj, nhxi, self.wp, self.wxi, nwp, nwxi,
                      *arrays, self.kn, self.kt, self.beta, self.mu, self.mu_r, self.fcoh,
                      self.g, self.dt, cs, F, T)
            self.t += h
            done += k

    def tool_poses(self, t=None):
        t = self.t if t is None else t
        out = []
        for tl in self.tools:
            p, R, on = tl.pose(t)
            out.append((np.asarray(p, float).copy(), np.asarray(R, float).copy(), bool(on)))
        return out

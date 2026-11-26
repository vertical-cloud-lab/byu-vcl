"""EBSD on a polished section of a part: an orientation map simulated from the latent microstructure, then the analysis a
lab runs on it (grain reconstruction, grain size, equiaxed share, <100> fiber strength, indexing rate, KAM, phase map).

What is simulated (``_simulate``), for a section containing the build direction (map rows run along BD):

* **Grains.** Two Poisson-Voronoi tessellations: equiaxed grains (random orientations) and columnar grains (the seeds
  in a space compressed along BD by the aspect ratio, so cells are elongated along BD; <100> fiber along BD with a
  Rayleigh-distributed tilt of ``fiber_spread_deg``, random spin). Seed densities are set so that an ideal, infinite
  section has an area-weighted equivalent-circle diameter equal to the truth's ``grain_um`` (for 2-D Poisson-Voronoi
  the area-weighted ECD is 1.241 / sqrt(seed density), from the gamma fit of cell areas, shape 3.6; Ferenc & Neda,
  Physica A 385, 2007). Which tessellation a point belongs to follows melt-pool bands (period = melt-pool depth or
  2.5 columnar lengths, arcs of the hatch width; the bottom ``equiaxed_frac`` of each band is the fine-grain zone,
  as in Scalmalloy and Al-Zr: Spierings et al., Mater. Des. 115 (2017) 52). Equiaxed grains are 1.5 um in Al (the
  truth's own constant) and 0.6 x grain_um in Cu (assumed); columnar grains take the rest of the truth's mixture.
* **Intragranular misorientation**: a Gaussian random rotation field (correlation length 0.6 um, assumed) whose amplitude
  gives the truth's ``kam_deg`` at a 0.5 um step (assumed reference), so KAM rises with step size as it does in real
  maps; plus orientation noise of the indexing itself (about 0.35 deg between neighbours on good patterns, worse on
  poor ones: Humphreys, J. Mater. Sci. 36 (2001) 3833; Wright et al., Ultramicroscopy 111 (2011) 1053).
* **Pattern quality (band contrast)** per point: phase (FCC 0.92 Al / 0.88 Cu; beta' martensite 0.6, its laths are
  finer than the interaction volume, 0.75; kappa 0.7: assumed), lowered by stored strain, by unresolved second phases
  (Si network, kappa_III/IV, L1_2), next to grain boundaries (overlapping patterns), along polishing scratches;
  zero in pores (section circles of the truth's pore populations, sphere sections sampled the stereological way) and
  in hot cracks (lines along BD with the truth's length per area). A point indexes when its band contrast, with
  pattern-to-pattern scatter, clears a threshold (Hough indexing needs enough bands: Wright & Nowell, Microsc.
  Microanal. 12 (2006) 72). Low-quality points are sometimes misindexed (random, or the 60 deg <111> pseudo-symmetric
  solution of FCC).
* **Cu phases**: retained beta' in blobs (a thresholded random field at the truth's volume fraction), its own random
  martensite packets, under-indexed; coarse kappa_II as BCC points; beta'/kappa confusion 10 % (assumed: both are
  BCC-derived).

The analysis (``_analyse``) uses only the measured map: grains by flood fill over neighbours misoriented < 15 deg
(cubic symmetry, 24 operators), grains under 4 points removed, edge grains excluded from the size (ASTM E2627 practice),
area-weighted ECD, aspect ratio < 2 from the second moments for the equiaxed share, max multiples of random density of
the <100> pole along BD by a Gaussian kernel (5 deg) normalised by the kernel's expectation for a random texture,
KAM over first neighbours below 5 deg, and the beta' share of indexed points. Fidelity 'full' adds a Kikuchi pattern
(gnomonic projection, 20 kV relativistic wavelength, kinematic band intensities) and maps for figures; 'fast' samples
the lite chain's errors from ``calib_micro.json['ebsd']`` (``calibrate()``).

Powder lots are not mapped (the lab does EBSD on parts); ``measure`` returns {} for them. A map with fewer than 30 %
of its points indexed (it landed in a lack-of-fusion pore) is re-taken at another spot, at most twice (assumed).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from twin.instruments import micro

SPEC = dict(station="byu_sem", hours=0.75, consumables={"colloidal_silica_ml": 20.0, "polishing_cloth": 0.25},
            prep=dict(station="prep", hours=1.5, note="section, mount, grind, polish to 0.05 um colloidal silica"),
            note="EBSD map at 20 kV, 70 deg tilt, on the SEM station; one map per part (assumed)")

KV = 20.0
GB_DEG = 15.0                 # high-angle boundary threshold for grain reconstruction
KAM_MAX_DEG = 5.0             # KAM ignores neighbours misoriented by more (subgrain/grain boundaries)
BC_THRESH = 0.35              # indexing threshold on band contrast (assumed)
BC_SCATTER = 0.25             # pattern-to-pattern log scatter of band contrast (assumed)
MIN_GRAIN_PX = 4              # smallest grain kept (cleanup), points
KERNEL_DEG = 5.0              # kernel half-width for the <100>//BD density
ELL_UM, STEP_REF_UM = 0.6, 0.5   # orientation-field correlation length and the step the truth's KAM refers to
NOISE_DEG = 0.155             # per-component orientation noise on a good pattern (0.35 deg mean neighbour noise)
LITE = (80, 64, 5.0)          # nx, ny, step = grain/5
FULL = (400, 300, 10.0)       # nx, ny, step = grain/10
REMAP_BELOW = 0.3             # indexed share below which the map is re-taken at another spot (assumed)
KEYS = ["grain_um", "equiaxed_frac", "texture_mrd", "indexed_frac", "kam_deg", "beta_prime_frac"]


def wavelength_A(kv: float = KV) -> float:
    """Relativistic electron wavelength, lambda = h / sqrt(2 m e V (1 + e V / (2 m c^2))) = 12.2643 / sqrt(V (1 +
    0.97848e-6 V)) A (V in volts): 0.08588 A at 20 kV."""
    V = kv * 1e3
    return 12.2643 / math.sqrt(V * (1 + 0.97848e-6 * V))


# ------------------------------------------------------------------------------------------------ quaternions
def _qmul(a, b):
    aw, ax, ay, az = np.moveaxis(a, -1, 0)
    bw, bx, by, bz = np.moveaxis(b, -1, 0)
    return np.stack([aw * bw - ax * bx - ay * by - az * bz, aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw], -1)


def _qconj(q):
    return q * np.array([1.0, -1.0, -1.0, -1.0])


def _q_from_rotvec(w):
    """Rotation vectors (..., 3), radians -> unit quaternions."""
    ang = np.linalg.norm(w, axis=-1)
    s = np.where(ang > 1e-12, np.sin(ang / 2) / np.maximum(ang, 1e-12), 0.5)
    return np.concatenate([np.cos(ang / 2)[..., None], w * s[..., None]], -1)


def _q_axis_angle(axis, ang):
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis, axis=-1, keepdims=True)
    return np.concatenate([np.cos(np.asarray(ang) / 2)[..., None], axis * np.sin(np.asarray(ang) / 2)[..., None]], -1)


def _q_random(rng, n):
    """Uniform random orientations (Shoemake 1992)."""
    u1, u2, u3 = rng.random(n), rng.random(n), rng.random(n)
    return np.stack([np.sqrt(u1) * np.cos(2 * np.pi * u3), np.sqrt(1 - u1) * np.sin(2 * np.pi * u2),
                     np.sqrt(1 - u1) * np.cos(2 * np.pi * u2), np.sqrt(u1) * np.sin(2 * np.pi * u3)], -1)


def _q_fiber(rng, n, spread_deg):
    """<100> fiber along z (BD): random spin about crystal [001], then a tilt about an in-plane axis, Rayleigh(spread)."""
    spin = _q_axis_angle(np.tile([0.0, 0.0, 1.0], (n, 1)), rng.uniform(0, 2 * np.pi, n))
    psi = rng.uniform(0, 2 * np.pi, n)
    t = math.radians(spread_deg) * np.sqrt(-2 * np.log(np.maximum(rng.random(n), 1e-12)))
    tilt = _q_axis_angle(np.stack([np.cos(psi), np.sin(psi), np.zeros(n)], -1), t)
    return _qmul(tilt, spin)


def _qmat(q):
    """Rotation matrices (..., 3, 3) of unit quaternions (crystal -> sample)."""
    w, x, y, z = np.moveaxis(q, -1, 0)
    return np.stack([np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], -1),
                     np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], -1),
                     np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)], -2)


@lru_cache(maxsize=1)
def _cubic_ops():
    """The 24 proper rotations of m-3m as quaternions, and the matrix that gives (q * S_i).w for all i at once."""
    import itertools
    mats = []
    for p in itertools.permutations(range(3)):
        for s in itertools.product((1, -1), repeat=3):
            m = np.zeros((3, 3))
            for r, (c, sg) in enumerate(zip(p, s)):
                m[r, c] = sg
            if np.linalg.det(m) > 0:
                mats.append(m)
    qs = []
    for m in mats:
        w = math.sqrt(max(0.0, 1 + m[0, 0] + m[1, 1] + m[2, 2])) / 2
        x = math.copysign(math.sqrt(max(0.0, 1 + m[0, 0] - m[1, 1] - m[2, 2])) / 2, m[2, 1] - m[1, 2])
        y = math.copysign(math.sqrt(max(0.0, 1 - m[0, 0] + m[1, 1] - m[2, 2])) / 2, m[0, 2] - m[2, 0])
        z = math.copysign(math.sqrt(max(0.0, 1 - m[0, 0] - m[1, 1] + m[2, 2])) / 2, m[1, 0] - m[0, 1])
        qs.append([w, x, y, z])
    S = np.array(qs)
    return S, (S * np.array([1.0, -1.0, -1.0, -1.0])).T


def misorientation_deg(q1, q2):
    """Disorientation angle (deg) between orientations under cubic symmetry."""
    _, Mw = _cubic_ops()
    qr = _qmul(_qconj(q1), q2)
    w = np.abs(qr @ Mw).max(-1)
    return np.degrees(2 * np.arccos(np.clip(w, 0.0, 1.0)))


def _bd_crystal(q):
    """BD (sample z) in crystal coordinates: the third row of the crystal->sample matrix."""
    w, x, y, z = np.moveaxis(q, -1, 0)
    return np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], -1)


def ipf_rgb(q):
    """IPF-BD colours (red <001>, green <101>, blue <111>) of quaternions (..., 4) -> uint8 (..., 3)."""
    v = np.sort(np.abs(_bd_crystal(q)), axis=-1)          # a <= b <= c
    a, b, c = v[..., 0], v[..., 1], v[..., 2]
    rgb = np.stack([c - b, (b - a) * math.sqrt(2), a * math.sqrt(3)], -1)
    rgb = rgb / np.maximum(rgb.max(-1, keepdims=True), 1e-9)
    return (255 * np.sqrt(np.clip(rgb, 0, 1))).astype(np.uint8)


def _theta100_deg(q):
    """Angle between BD and the nearest crystal <100>."""
    v = np.abs(_bd_crystal(q))
    return np.degrees(np.arccos(np.clip(v.max(-1), 0.0, 1.0)))


@lru_cache(maxsize=4)
def _kernel_random_mean(w_deg=KERNEL_DEG):
    """E[K(theta)] for a random texture: theta (angle to the nearest of the six <100> poles) has density 3 sin(theta)
    below 45 deg; numerically over a fine grid of random directions above."""
    r = np.random.default_rng(12345)
    v = r.normal(size=(400000, 3))
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    th = np.degrees(np.arccos(np.abs(v).max(1)))
    return float(np.mean(np.exp(-th ** 2 / (2 * w_deg ** 2))))


def true_mrd(eq: float, spread_deg: float) -> float:
    """MRD of <100>//BD an infinite map would show: (1 - eq) x fiber + eq x random. For a Rayleigh tilt of width s,
    E[exp(-t^2 / 2w^2)] = w^2 / (w^2 + s^2)."""
    w, s = KERNEL_DEG, spread_deg
    fib = (w * w / (w * w + s * s)) / _kernel_random_mean()
    return float((1 - eq) * fib + eq)


# ------------------------------------------------------------------------------------------------ the map
def _grf(rng, shape, a_px):
    """Unit-variance Gaussian random field with correlation exp(-r^2 / (4 a^2)) (white noise through a Gaussian of
    std a pixels)."""
    w = rng.standard_normal(shape)
    if a_px < 0.35:
        return w
    f = ndimage.gaussian_filter(w, a_px, mode="wrap")
    return f / max(float(f.std()), 1e-9) if a_px < 1.0 else f * math.sqrt(4 * math.pi) * a_px


def _tess(rng, xs, ys, W, H, dens, compress=1.0, margin=0.0):
    """Nearest-seed labels of points (xs, ys) for a Poisson seed set of density ``dens`` per um^2 in a space whose y
    is divided by ``compress`` (seeds only over the points' bounding box plus a margin)."""
    x0, x1 = float(xs.min()) - margin, float(xs.max()) + margin
    y0, y1 = (float(ys.min()) - margin) / compress, (float(ys.max()) + margin) / compress
    n = max(int(rng.poisson(dens * compress * (x1 - x0) * (y1 - y0))), 1)
    seeds = np.column_stack([rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)])
    tree = cKDTree(seeds, balanced_tree=False, compact_nodes=False)
    _, lab = tree.query(np.column_stack([xs, ys / compress]))
    return lab, n


def _fine_fraction(pm):
    """Volume share of second phases too fine to index on their own (they lower the matrix's pattern quality)."""
    f = 0.0
    for p in pm["phases"]:
        if p["role"] == "matrix" or p["name"] in ("beta'", "kappa_II"):
            continue
        f += p["vol"]
    return f


def _vol(pm, name):
    return sum(p["vol"] for p in pm["phases"] if p["name"] == name)


def _step(d, div):
    return float(np.clip(d / div, 0.1, 5.0))


def _simulate(sample, campaign, rng, nx, ny, div):
    pm = micro.phase_model(sample, campaign, "part")
    al = campaign == "flaime_al"
    g = pm["grains"]
    d = float(max(g["d_um"], 0.3)) if np.isfinite(g["d_um"]) else 10.0
    eq = float(np.clip(g["equiaxed_frac"], 0, 1))
    asp, spread, kam0 = float(g["aspect"]), float(g["fiber_spread_deg"]), float(g["kam_deg"])
    step = _step(d, div)
    W, H = nx * step, ny * step
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny))
    xs, ys = ((ii + 0.5) * step).ravel(), ((jj + 0.5) * step).ravel()
    N = nx * ny
    # ---- populations: equiaxed (fine) and columnar grains, mixed so the area-weighted ECD is the truth's d
    d_eq = min(1.5, d) if al else 0.6 * d
    if eq >= 0.98:
        d_eq, d_col = d, d
    elif eq <= 0.02:
        d_col = d
    else:
        d_col = max((d - eq * d_eq) / (1 - eq), d_eq)
    lab = np.zeros(N, int)
    is_eq = np.zeros(N, bool)
    quats = []
    nlab = 0
    if eq < 0.98:
        dens = (1.241 / d_col) ** 2                          # per real um^2 (the affine map keeps the ECD law)
        lc, n = _tess(rng, xs, ys, W, H, dens, compress=asp, margin=d_col * math.sqrt(asp))
        lab = lc
        quats.append(_q_fiber(rng, n, spread))
        nlab = n
    if eq > 0.02:
        if eq >= 0.98:
            is_eq[:] = True
        else:
            mp = sample.get("melt_pool") or {}
            P = max(mp.get("D_um", 100.0) if al else 400.0, 2.5 * d_col * math.sqrt(asp))
            hw = (sample.get("proc") or {}).get("h_um", 110.0) if al else 1000.0
            A = 0.3 * P
            u = ((ys + rng.uniform(0, P) + A * (1 - np.abs(np.sin(np.pi * (xs + rng.uniform(0, hw)) / hw)))) / P) % 1.0
            is_eq = u < eq
        dens = (1.241 / d_eq) ** 2
        le, n = _tess(rng, xs[is_eq], ys[is_eq], W, H, dens, margin=d_eq) if is_eq.any() else (np.zeros(0, int), 1)
        lab[is_eq] = le + nlab
        quats.append(_q_random(rng, n))
        nlab += n
    q_grain = np.concatenate(quats, 0)
    phase = np.zeros(N, np.int8)                         # 0 FCC matrix, 1 beta', 2 kappa (BCC)
    bc = np.full(N, 0.92 if al else 0.88)
    kam_loc = np.full(N, kam0)
    # ---- Cu: retained beta' blobs (own packets, random), coarse kappa_II as BCC points
    if not al:
        fb = float(np.clip(_vol(pm, "beta'"), 0, 0.95))
        if fb > 0.003:
            a_px = max(0.5 * d / step, 1.0) / math.sqrt(2)
            field = _grf(rng, (ny, nx), a_px).ravel()
            from scipy.special import ndtri
            isb = field > ndtri(1 - fb)
            if isb.any():
                lb, n = _tess(rng, xs[isb], ys[isb], W, H, (1.241 / (d / 3)) ** 2, margin=d / 3)
                lab[isb] = lb + nlab
                q_grain = np.concatenate([q_grain, _q_random(rng, n)], 0)
                nlab += n
                phase[isb] = 1
                bc[isb] = 0.75
                kam_loc[isb] = 1.5
        fk = float(_vol(pm, "kappa_II"))
        if fk > 1e-4:
            isk = (rng.random(N) < fk) & (phase == 0)
            nk = int(isk.sum())
            if nk:
                lab[isk] = np.arange(nk) + nlab
                q_grain = np.concatenate([q_grain, _q_random(rng, nk)], 0)
                nlab += nk
                phase[isk] = 2
                bc[isk] = 0.70
    # ---- orientations: grain + intragranular field + (later) indexing noise
    e = max(1 - math.exp(-STEP_REF_UM ** 2 / (2 * ELL_UM ** 2)), 1e-6)
    sig = math.radians(kam0) / math.sqrt(16 * e / math.pi)
    a_px = (ELL_UM / step) / math.sqrt(2)
    rot = np.stack([_grf(rng, (ny, nx), a_px).ravel() for _ in range(3)], -1) * sig
    if not al:
        extra = (phase == 1)
        rot[extra] += rng.standard_normal((int(extra.sum()), 3)) * math.radians(1.0)
    q = _qmul(q_grain[lab], _q_from_rotvec(rot))
    # ---- pattern quality: strain, unresolved second phases, boundaries, scratches
    bc *= np.exp(-kam_loc / 4.0)
    bc *= max(1 - 1.5 * _fine_fraction(pm), 0.3)
    L2 = lab.reshape(ny, nx)
    gbm = np.zeros((ny, nx), bool)
    dx = L2[:, 1:] != L2[:, :-1]
    dy = L2[1:, :] != L2[:-1, :]
    gbm[:, 1:] |= dx
    gbm[:, :-1] |= dx
    gbm[1:, :] |= dy
    gbm[:-1, :] |= dy
    bc[gbm.ravel()] *= 0.75
    for _ in range(int(rng.poisson(1.0))):                      # polishing scratches (assumed: about one per map)
        ang = rng.uniform(0, np.pi)
        c0 = rng.uniform(0, W), rng.uniform(0, H)
        dist = np.abs((xs - c0[0]) * math.sin(ang) - (ys - c0[1]) * math.cos(ang))
        bc[dist < max(0.6 * step, 0.3)] *= 0.5
    # ---- pores and cracks: no pattern
    dead = np.zeros(N, bool)
    pores = pm.get("pores") or {}
    for t, pp in pores.items():
        nv = pp.get("n_per_mm3", 0.0) * 1e-9                  # per um^3
        if nv <= 0:
            continue
        s = math.log(pp["gsd"])
        mu = math.log(pp["d_med_um"])
        ED = math.exp(mu + s * s / 2)
        Dmax = math.exp(mu + s * s + 3 * s)
        ext = (W + Dmax) * (H + Dmax)
        k = int(rng.poisson(nv * ED * ext))
        for _ in range(min(k, 200)):
            D = math.exp(rng.normal(mu + s * s, s))           # size-biased: sections favour big spheres
            R = D / 2
            r = math.sqrt(max(R * R - (R * rng.random()) ** 2, 0.0))
            asp_p = pp.get("aspect", 1.0) if t == "lof" else 1.0
            rx, ry = r * math.sqrt(asp_p), r / math.sqrt(asp_p)
            cx, cy = rng.uniform(-Dmax / 2, W + Dmax / 2), rng.uniform(-Dmax / 2, H + Dmax / 2)
            i0, i1 = max(int((cx - rx) / step), 0), min(int((cx + rx) / step) + 1, nx)
            j0, j1 = max(int((cy - ry) / step), 0), min(int((cy + ry) / step) + 1, ny)
            if i0 >= i1 or j0 >= j1:
                continue
            sub_i, sub_j = np.meshgrid(np.arange(i0, i1), np.arange(j0, j1))
            inside = (((sub_i + 0.5) * step - cx) / max(rx, 1e-6)) ** 2 + (((sub_j + 0.5) * step - cy) / max(ry, 1e-6)) ** 2 <= 1
            dead[(sub_j[inside] * nx + sub_i[inside])] = True
    cr = pm.get("cracks") or {}
    rho = float(cr.get("density_mm_mm2", 0.0))
    if rho > 0:
        Ltot = rho * 1e-3 * W * H
        lmed = cr.get("len_med_um", 100.0)
        p_hit = min(1.0, cr.get("open_um", 1.5) / step)
        for _ in range(min(int(rng.poisson(Ltot / lmed)), 100)):
            L = lmed * math.exp(rng.normal(0, math.log(cr.get("len_gsd", 1.6))))
            x0, y0 = rng.uniform(0, W), rng.uniform(-L / 2, H)
            js = np.arange(max(int(y0 / step), 0), min(int((y0 + L) / step) + 1, ny))
            if not len(js):
                continue
            wig = np.cumsum(rng.normal(0, 0.25 * step, len(js)))
            is_ = np.clip(((x0 + wig) / step).astype(int), 0, nx - 1)
            hit = rng.random(len(js)) < p_hit
            dead[js[hit] * nx + is_[hit]] = True
    bc[dead] = 0.02
    # ---- indexing
    bcm = bc * np.exp(rng.normal(0, BC_SCATTER, N))
    idx = bcm > BC_THRESH
    sig_n = math.radians(NOISE_DEG) * np.sqrt(0.8 / np.maximum(bcm, 0.05))
    q = _qmul(q, _q_from_rotvec(rng.standard_normal((N, 3)) * sig_n[:, None]))
    p_mis = np.clip(0.03 * np.exp(-(bcm - BC_THRESH) / 0.15), 0, 0.5) * idx
    mis = rng.random(N) < p_mis
    nm = int(mis.sum())
    if nm:
        rnd = rng.random(nm) < 0.5
        twin = _q_axis_angle(np.tile([1.0, 1.0, 1.0], (nm, 1)), np.full(nm, math.radians(60.0)))
        q[mis] = np.where(rnd[:, None], _q_random(rng, nm), _qmul(q[mis], twin))
    ph_meas = phase.copy()
    if not al:
        sw = idx & (phase > 0) & (rng.random(N) < 0.10)         # beta' <-> kappa confusion
        ph_meas[sw] = 3 - phase[sw]
        fb_mis = idx & (phase == 0) & (rng.random(N) < 0.005)     # FCC points read as BCC
        ph_meas[fb_mis] = 1
    ph_meas[~idx] = -1
    q[~idx] = np.nan
    return dict(q=q.reshape(ny, nx, 4), phase=ph_meas.reshape(ny, nx), bc=bcm.reshape(ny, nx), step=step,
                nx=nx, ny=ny, true_lab=L2, pm=pm, d=d, eq=eq, spread=spread, kam0=kam0)


# ------------------------------------------------------------------------------------------------ the analysis
def _analyse(m, al):
    q, ph, step = m["q"], m["phase"], m["step"]
    ny, nx = ph.shape
    N = nx * ny
    idx = ph >= 0
    qf = q.reshape(N, 4)
    phf = ph.ravel()
    ids = np.arange(N).reshape(ny, nx)
    # neighbour pairs (right, down) of indexed points of one phase
    pa = np.concatenate([ids[:, :-1].ravel(), ids[:-1, :].ravel()])
    pb = np.concatenate([ids[:, 1:].ravel(), ids[1:, :].ravel()])
    ok = idx.ravel()[pa] & idx.ravel()[pb] & (phf[pa] == phf[pb])
    pa, pb = pa[ok], pb[ok]
    ang = misorientation_deg(qf[pa], qf[pb])
    same = ang < GB_DEG
    G = coo_matrix((np.ones(int(same.sum())), (pa[same], pb[same])), shape=(N, N))
    _, lab = connected_components(G, directed=False)
    lab = np.where(idx.ravel(), lab, -1)
    # grain stats from moments
    good = lab >= 0
    L = lab[good]
    xs = (ids.ravel() % nx)[good].astype(float)
    ys = (ids.ravel() // nx)[good].astype(float)
    nlab = int(lab.max()) + 1 if good.any() else 0
    cnt = np.bincount(L, minlength=nlab).astype(float)
    sx, sy = np.bincount(L, xs, nlab), np.bincount(L, ys, nlab)
    sxx, syy, sxy = np.bincount(L, xs * xs, nlab), np.bincount(L, ys * ys, nlab), np.bincount(L, xs * ys, nlab)
    gph = np.zeros(nlab, int)
    gph[L] = phf[good]
    edge = np.zeros(nlab, bool)
    border = np.concatenate([lab.reshape(ny, nx)[0], lab.reshape(ny, nx)[-1], lab.reshape(ny, nx)[:, 0],
                             lab.reshape(ny, nx)[:, -1]])
    edge[border[border >= 0]] = True
    keep = cnt >= MIN_GRAIN_PX
    with np.errstate(invalid="ignore", divide="ignore"):
        mx, my = sx / np.maximum(cnt, 1), sy / np.maximum(cnt, 1)
        cxx = sxx / np.maximum(cnt, 1) - mx * mx + 1 / 12
        cyy = syy / np.maximum(cnt, 1) - my * my + 1 / 12
        cxy = sxy / np.maximum(cnt, 1) - mx * my
        tr, det = cxx + cyy, cxx * cyy - cxy * cxy
        disc = np.sqrt(np.maximum(tr * tr / 4 - det, 0))
        l1, l2 = tr / 2 + disc, np.maximum(tr / 2 - disc, 1e-9)
        ar = np.sqrt(l1 / l2)
    mat = keep & (gph == 0)
    area = cnt * step * step
    ecd = np.sqrt(4 * area / np.pi)
    inner = mat & ~edge
    sel = inner if inner.sum() >= 5 else mat
    out = {}
    if sel.any():
        out["grain_um"] = float(np.sum(area[sel] * ecd[sel]) / np.sum(area[sel]))
        out["equiaxed_frac"] = float(np.sum(area[mat] * (ar[mat] < 2.0)) / max(np.sum(area[mat]), 1e-9))
    # texture: <100>//BD density over indexed matrix points
    mpts = idx.ravel() & (phf == 0)
    if mpts.sum() >= 20:
        th = _theta100_deg(qf[mpts])
        out["texture_mrd"] = float(np.mean(np.exp(-th ** 2 / (2 * KERNEL_DEG ** 2))) / _kernel_random_mean())
    out["indexed_frac"] = float(idx.mean())
    # KAM: first neighbours below 5 deg
    v = ang < KAM_MAX_DEG
    s = np.bincount(pa[v], ang[v], N) + np.bincount(pb[v], ang[v], N)
    c = np.bincount(pa[v], minlength=N) + np.bincount(pb[v], minlength=N)
    kam = np.where(c > 0, s / np.maximum(c, 1), np.nan)
    if (c > 0).any():
        out["kam_deg"] = float(np.nanmean(kam))
    if not al:
        n_i = max(int(idx.sum()), 1)
        out["beta_prime_frac"] = float(np.sum(phf == 1) / n_i)
    extra = dict(lab=lab.reshape(ny, nx), kam=kam.reshape(ny, nx), keep=keep, ar=ar, ecd=ecd, edge=edge)
    return out, extra


# ------------------------------------------------------------------------------------------------ Kikuchi pattern
def _fe(el, s):
    """Electron scattering amplitude, Z^0.75 exp(-1.5 s^2) (assumed shape; band intensities are relative)."""
    return micro.Z(el) ** 0.75 * np.exp(-1.5 * s * s)


@lru_cache(maxsize=16)
def _reflectors(struct_name, occ_key, a, max_idx=4, frac=0.03):
    st = micro.STRUCTURES[struct_name]
    occ = dict(occ_key)
    hkl = np.array([(h, k, l) for h in range(-max_idx, max_idx + 1) for k in range(-max_idx, max_idx + 1)
                    for l in range(-max_idx, max_idx + 1) if (h, k, l) > (0, 0, 0)], float)
    d = a / np.linalg.norm(hkl, axis=1)
    s = 1 / (2 * d)
    F = np.zeros(len(hkl), complex)
    B = st.get("B", 0.6)
    for site, pos in st["atoms"]:
        sites = dict(occ[site]) if site in occ else st["sites"][site]
        f = sum(x * _fe(e, s) for e, x in sites.items())
        F += f * np.exp(2j * np.pi * (hkl @ np.array(pos))) * np.exp(-B * s * s)
    I = np.abs(F) ** 2
    keep = (I > frac * I.max()) & (d > 0.55)
    return hkl[keep], d[keep], I[keep] / I.max()


def kikuchi_pattern(q, struct_name="fcc", a=None, sites=None, size=240, kv=KV, rng=None, counts=3000.0):
    """A gnomonic EBSD pattern for one orientation: bands of every reflector with |F|^2 above 3 % of the strongest,
    half-width = Bragg angle at the relativistic wavelength, intensity ~ |F|^2 (kinematic), on a background that falls
    off from below the pattern centre, with Poisson noise; circular phosphor screen. 70 deg sample tilt and the
    detector tilt are folded into one fixed rotation (assumed geometry: PC (0.5, 0.40), DD 0.65)."""
    st = micro.STRUCTURES[struct_name]
    a = a or st["a"]
    occ = tuple(sorted((k, tuple(sorted(v.items()))) for k, v in (sites or {}).items()))
    hkl, d, I = _reflectors(struct_name, occ, float(a))
    lam = wavelength_A(kv)
    sinb = lam / (2 * d)
    u = (np.arange(size) + 0.5) / size
    X, Y = np.meshgrid(u - 0.5, u - 0.40)
    r = np.stack([X, Y, np.full_like(X, 0.65)], -1)
    r /= np.linalg.norm(r, axis=-1, keepdims=True)
    tilt = math.radians(20.0)                                  # 90 - 70 deg
    Rds = np.array([[1, 0, 0], [0, math.cos(tilt), -math.sin(tilt)], [0, math.sin(tilt), math.cos(tilt)]])
    rs = r @ Rds.T
    Rm = _qmat(np.asarray(q, float))
    rc = rs @ Rm                                               # crystal frame: Rm^T r
    n = hkl / np.linalg.norm(hkl, axis=1, keepdims=True)
    img = np.zeros(X.shape)
    for ni, sb, w in zip(n, sinb, I):
        x = np.abs(rc @ ni)
        band = 1 / (1 + np.exp((x - sb) / (0.12 * sb)))
        edge = np.exp(-((x - sb) / (0.10 * sb)) ** 2)
        img += w * (band + 0.35 * edge)
    img = img / max(img.max(), 1e-9)
    rr = np.hypot(X, Y + 0.15)
    bg = np.exp(-rr ** 2 / (2 * 0.42 ** 2))
    lam_px = counts * bg * (0.55 + 0.45 * img)
    rng = rng or np.random.default_rng(0)
    pat = rng.poisson(lam_px).astype(float)
    pat = pat / ndimage.gaussian_filter(pat, size / 12)          # background division, as the acquisition does
    pat = (pat - pat.min()) / max(np.ptp(pat), 1e-9)
    mask = np.hypot(X, Y - 0.10) <= 0.5                         # the round screen, centred on the image
    return np.where(mask, pat, np.nan)


# ------------------------------------------------------------------------------------------------ fast mode
def _features(pm, campaign):
    g = pm["grains"]
    d = float(max(g["d_um"], 0.3)) if np.isfinite(g["d_um"]) else 10.0
    eq = float(np.clip(g["equiaxed_frac"], 0, 1))
    bp = float(np.clip(_vol(pm, "beta'"), 0, 1))
    por = float(max(pm.get("porosity", 0.0), 0.0))
    crack = float(max((pm.get("cracks") or {}).get("density_mm_mm2", 0.0), 0.0))
    step = _step(d, LITE[2])
    ld = math.log(d)
    return np.array([1.0, eq, eq * (1 - eq), ld, math.log(step / (d / LITE[2])), math.sqrt(por),
                     bp, bp * bp, float(g["kam_deg"]), _fine_fraction(pm), min(crack, 3.0), eq * ld, ld * ld,
                     math.sqrt(por) * ld])


def _truths(pm):
    g = pm["grains"]
    d = float(max(g["d_um"], 0.3)) if np.isfinite(g["d_um"]) else 10.0
    eq = float(np.clip(g["equiaxed_frac"], 0, 1))
    return dict(grain_um=d, equiaxed_frac=eq, texture_mrd=true_mrd(eq, g["fiber_spread_deg"]),
                kam_deg=float(g["kam_deg"]), beta_prime_frac=float(np.clip(_vol(pm, "beta'"), 0, 1)))


def _to_y(key, meas, tru):
    if key in ("grain_um", "texture_mrd"):
        return math.log(max(meas, 1e-6) / max(tru, 1e-6))
    if key == "kam_deg":
        return math.log(max(meas, 1e-4))
    if key == "indexed_frac":
        p = min(max(meas, 1e-4), 1 - 1e-4)
        return math.log(p / (1 - p))
    return meas - tru                                          # equiaxed_frac, beta_prime_frac (differences)


def _from_y(key, y, tru):
    if key in ("grain_um", "texture_mrd"):
        return tru * math.exp(y)
    if key == "kam_deg":
        return math.exp(y)
    if key == "indexed_frac":
        return 1 / (1 + math.exp(-y))
    return float(np.clip(tru + y, 0.0, 1.0))


_DEFAULT = {   # used until calibrate() has run: rough lite-chain behaviour (mean, sd of y)
    "grain_um": (-0.10, 0.15), "equiaxed_frac": (-0.05, 0.10), "texture_mrd": (0.0, 0.20),
    "indexed_frac": (2.5, 0.4), "kam_deg": (0.69, 0.05), "beta_prime_frac": (-0.10, 0.05)}


_KNN_CACHE: dict = {}


def _knn_table(cal, campaign):
    """Arrays of the calibration's per-sample table (standardised features, mean residual and within-sample sd)."""
    key = (campaign, id(cal))
    if key not in _KNN_CACHE:
        kn = cal.get("knn")
        if not kn:
            _KNN_CACHE[key] = None
        else:
            _KNN_CACHE[key] = dict(X=np.array(kn["X"]), mu=np.array(kn["mu"]), sd=np.array(kn["sd"]),
                                   r={k: np.array(v) for k, v in kn["r"].items()},
                                   s={k: np.array(v) for k, v in kn["s"].items()})
    return _KNN_CACHE[key]


def _fast(sample, campaign, rng):
    """Sample the lite chain's error: a linear model of its mean on the sample's state, corrected by the inverse-
    distance-weighted mean residual of the 5 nearest calibration samples (standardised feature space), and the pooled
    within-sample spread of those neighbours (the map-to-map repeatability on one part)."""
    pm = micro.phase_model(sample, campaign, "part")
    al = campaign == "flaime_al"
    tru = _truths(pm)
    x = _features(pm, campaign)
    cal = micro.calib("ebsd").get(campaign, {})
    tab = _knn_table(cal, campaign)
    nb = None
    if tab is not None:
        z = (x - tab["mu"]) / tab["sd"]
        dist = np.sum((tab["X"] - z) ** 2, axis=1)
        nb = np.argpartition(dist, min(4, len(dist) - 1))[:5]
    out = {}
    for k in KEYS:
        if al and k == "beta_prime_frac":
            continue
        c = cal.get(k)
        if c:
            mu = float(np.dot(c["mean"], x))
            sd = float(np.exp(np.dot(c["logsd"], x)))
            if nb is not None and k in tab["r"]:
                w = 1.0 / (dist[nb] + 0.05)                  # inverse-distance weights: local regression
                w = w / (w.sum() + 2.0)                       # shrink toward the linear model when far away
                mu += float(np.dot(w, tab["r"][k][nb]))
                sd = float(max(math.sqrt(np.dot(w, tab["s"][k][nb] ** 2) / max(w.sum(), 1e-9)), 0.15 * sd, 1e-4))
        else:
            mu, sd = _DEFAULT[k]
            if k == "kam_deg":
                mu += math.log(max(tru["kam_deg"], 0.05))
        y = mu + sd * rng.standard_normal()
        out[k] = _from_y(k, y, tru.get(k, 0.0))
    return out


# ------------------------------------------------------------------------------------------------ entry point
def measure(sample, campaign, rng, fidelity="fast", **kw):
    """grain_um (area-weighted ECD), equiaxed_frac, texture_mrd (<100>//BD), indexed_frac, kam_deg, beta_prime_frac
    (Cu). Parts only; a powder lot returns {}."""
    if micro.kind_of(sample) != "part":
        return {}
    al = campaign == "flaime_al"
    if fidelity == "fast":
        return _fast(sample, campaign, rng)
    nx, ny, div = FULL if fidelity == "full" else LITE
    nx, ny = kw.get("nx", nx), kw.get("ny", ny)
    best = None
    for _ in range(3):                  # a map that landed in a pore is re-taken elsewhere (assumed: 2 retries)
        m = _simulate(sample, campaign, rng, nx, ny, div)
        out, extra = _analyse(m, al)
        if best is None or out["indexed_frac"] > best[1]["indexed_frac"]:
            best = (m, out, extra)
        if out["indexed_frac"] >= REMAP_BELOW and "grain_um" in out:
            break
    m, out, extra = best
    if fidelity == "full":
        qf = m["q"]
        ipf = np.zeros(qf.shape[:2] + (3,), np.uint8)
        okp = m["phase"] >= 0
        ipf[okp] = ipf_rgb(qf[okp])
        lab = extra["lab"]
        gb = np.zeros(lab.shape, bool)
        gb[:, 1:] |= lab[:, 1:] != lab[:, :-1]
        gb[1:, :] |= lab[1:, :] != lab[:-1, :]
        # a Kikuchi pattern from the matrix grain nearest the map centre (and from beta' when present)
        cy, cx = np.array(lab.shape) // 2
        pts = np.argwhere(m["phase"] == 0)
        kik = {}
        if len(pts):
            j, i = pts[np.argmin(np.hypot(pts[:, 0] - cy, pts[:, 1] - cx))]
            mat = m["pm"]["phases"][0]
            at = micro.wt_to_at({e: 100 * v for e, v in mat["comp"].items()})
            kik["fcc"] = kikuchi_pattern(qf[j, i], "fcc", a=mat["a"], sites={"M": at}, rng=rng).astype(np.float32)
        pts = np.argwhere(m["phase"] == 1)
        if len(pts) and not al:
            j, i = pts[len(pts) // 2]
            kik["beta'"] = kikuchi_pattern(qf[j, i], "beta'", rng=rng).astype(np.float32)
        out["raw"] = dict(quat=qf.astype(np.float32), ipf=ipf, phase=m["phase"], grains=lab.astype(np.int32),
                          gb=gb, kam=extra["kam"].astype(np.float32), bc=m["bc"].astype(np.float32),
                          step_um=m["step"], kikuchi=kik, phase_names={
                              -1: "not indexed", 0: "FCC", 1: "beta'", 2: "kappa (BCC)"})
        if kw.get("with_truth"):                 # the latent grains/phases, for figure annotations only
            out["raw"]["true"] = _truths(m["pm"])
    return out


# ------------------------------------------------------------------------------------------------ calibration
def calibrate(n=40, reps=3, seed=0, verbose=True) -> dict:
    """Run the lite chain over representative parts of both campaigns (random designs and process settings from
    ``micro.random_samples`` plus the gallery alloys) and fit, per campaign and output, (1) a ridge-regularised linear
    model of the error's mean and log-spread on the sample-state features (``_features``) and (2) a per-sample table
    of mean residuals and within-sample spreads that the fast mode reads by nearest neighbours."""
    params = {}
    table = {}
    for camp in ("flaime_al", "onr_cu"):
        al = camp == "flaime_al"
        keys = [k for k in KEYS if not (al and k == "beta_prime_frac")]
        parts = [(p, reps) for _, p in micro.random_samples(camp, n, seed=seed)]
        parts += [(p, 8 * reps) for (_, p) in micro.gallery_samples()[camp].values()]   # reference alloys: more maps
        Xs, Ys = [], []                                  # per sample: features, (reps x keys) of y
        rng = np.random.default_rng(seed + 99)
        for part, nrep in parts:
            pm = micro.phase_model(part, camp, "part")
            x = _features(pm, camp)
            tru = _truths(pm)
            rows = []
            for _ in range(nrep):
                out = measure(part, camp, rng, fidelity="lite")
                if any(k not in out for k in keys):
                    continue
                rows.append([_to_y(k, out[k], tru.get(k, 0.0)) for k in keys])
            if len(rows) >= 2:
                Xs.append(x)
                Ys.append(np.array(rows))
        X = np.array(Xs)
        Xr = np.repeat(X, [len(y) for y in Ys], axis=0)
        Yr = np.concatenate(Ys, 0)
        lam = 1e-3 * np.eye(X.shape[1])
        lam[0, 0] = 0.0
        cp = {}
        mu_f, sd_f = X.mean(0), X.std(0)
        sd_f[sd_f < 1e-9] = 1.0
        knn = dict(X=((X - mu_f) / sd_f).round(4).tolist(), mu=mu_f.tolist(), sd=sd_f.tolist(), r={}, s={})
        for j, k in enumerate(keys):
            y = Yr[:, j]
            b = np.linalg.solve(Xr.T @ Xr + len(y) * lam, Xr.T @ y)
            r = y - Xr @ b
            zl = np.log(np.abs(r) + 1e-4)
            bs = np.linalg.solve(Xr.T @ Xr + len(y) * lam * 10, Xr.T @ zl)
            bs[0] += 0.635                                   # E[log|N(0, s)|] = log s - 0.635
            cp[k] = dict(mean=[float(v) for v in b], logsd=[float(v) for v in bs])
            rs = [Ys[i][:, j] - X[i] @ b for i in range(len(Ys))]
            knn["r"][k] = [round(float(v.mean()), 5) for v in rs]
            knn["s"][k] = [round(float(v.std(ddof=1)), 5) for v in rs]
            table[(camp, k)] = dict(n=len(y), y_mean=float(y.mean()), resid_sd=float(r.std()),
                                    within_sd=float(np.sqrt(np.mean(np.square(knn["s"][k])))))
        cp["knn"] = knn
        params[camp] = cp
    params["features"] = ["1", "eq", "eq(1-eq)", "ln d", "ln(step/(d/5))", "sqrt(porosity)", "beta'", "beta'^2",
                          "kam_true", "fine_frac", "crack", "eq ln d", "(ln d)^2", "sqrt(porosity) ln d"]
    params["y"] = {"grain_um": "ln(meas/true)", "texture_mrd": "ln(meas/true MRD)", "kam_deg": "ln(meas)",
                   "indexed_frac": "logit(meas)", "equiaxed_frac": "meas - true", "beta_prime_frac": "meas - true"}
    if verbose:
        for (c, k), v in table.items():
            print(f"{c:10s} {k:16s} n={v['n']:4d} y_mean={v['y_mean']:+.3f} resid_sd={v['resid_sd']:.3f} "
                  f"within_sd={v['within_sd']:.3f}")
    return params


def compare_fast_lite(n_draw=40, seed=1):
    """Fast vs lite on the gallery parts: mean and sd of each output (for the notes' table)."""
    rows = []
    G = micro.gallery_samples()
    for camp, d in G.items():
        for nm, (_, part) in d.items():
            r1, r2 = np.random.default_rng(seed), np.random.default_rng(seed + 1)
            L = [measure(part, camp, r1, "lite") for _ in range(n_draw)]
            F = [measure(part, camp, r2, "fast") for _ in range(n_draw)]
            tru = _truths(micro.phase_model(part, camp, "part"))
            for k in KEYS:
                if k not in F[0]:
                    continue
                lv = np.array([o[k] for o in L if k in o])
                fv = np.array([o[k] for o in F if k in o])
                rows.append((camp, nm, k, tru.get(k, float("nan")), lv.mean(), lv.std(), fv.mean(), fv.std()))
    return rows


# ------------------------------------------------------------------------------------------------ figures
def _ipf_key(ax):
    """The standard triangle of IPF colours."""
    n = 120
    img = np.ones((n, n, 4))
    for j in range(n):
        for i in range(n):
            # stereographic coordinates of the [001]-[101]-[111] triangle
            X, Y = i / (n - 1) * 0.42, j / (n - 1) * 0.37
            r2 = X * X + Y * Y
            v = np.array([2 * X, 2 * Y, 1 - r2]) / (1 + r2)
            a, b, c = np.sort(np.abs(v))
            if not (Y <= X + 1e-9 and v[0] <= v[2] + 1e-9 and v[1] <= v[0] + 1e-9):
                img[j, i, 3] = 0
                continue
            rgb = np.array([c - b, (b - a) * math.sqrt(2), a * math.sqrt(3)])
            img[j, i, :3] = np.sqrt(np.clip(rgb / max(rgb.max(), 1e-9), 0, 1))
    ax.imshow(img, origin="lower", extent=(0, 0.42, 0, 0.37))
    ax.text(0, -0.03, "001", ha="center", va="top", fontsize=7)
    ax.text(0.414, -0.03, "101", ha="center", va="top", fontsize=7)
    ax.text(0.366, 0.37, "111", ha="center", va="bottom", fontsize=7)
    ax.set_axis_off()


def _ipf_with_gb(raw, al=True, dark=True):
    img = raw["ipf"].astype(float) / 255
    img[raw["phase"] < 0] = 0.0 if dark else 1.0
    img[raw["gb"]] = 0.0
    if not al:
        img[raw["phase"] == 1] = img[raw["phase"] == 1] * 0.35 + 0.65 * np.array([0.55, 0.55, 0.55])
    return img


def gallery(outdir, samples=None):
    """ebsd.png (IPF-BD maps with boundaries, KAM or phase maps, measured vs true) and kikuchi.png."""
    from pathlib import Path
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    samples = samples or micro.gallery_samples()
    items = [(c, nm, part) for c, d in samples.items() for nm, (_, part) in d.items()]
    fig, axes = plt.subplots(2, len(items), figsize=(4.0 * len(items), 7.6), constrained_layout=True)
    res = {}
    for k, (camp, nm, part) in enumerate(items):
        rng = np.random.default_rng(7 + k)
        out = measure(part, camp, rng, fidelity="full", with_truth=True)
        res[(camp, nm)] = out
        raw = out["raw"]
        al = camp == "flaime_al"
        st = raw["step_um"]
        ny, nx = raw["phase"].shape
        ext = (0, nx * st, 0, ny * st)
        ax = axes[0, k]
        ax.imshow(_ipf_with_gb(raw, al), origin="lower", extent=ext, interpolation="nearest")
        ax.set_title(f"{nm}: IPF-BD (BD up), step {st:.2f} um", fontsize=9)
        ax.set_xlabel("um")
        t = raw["true"]
        lines = [f"grain {out.get('grain_um', float('nan')):.2f} um (true {t['grain_um']:.2f})",
                 f"equiaxed {out.get('equiaxed_frac', float('nan')):.2f} (true {t['equiaxed_frac']:.2f})",
                 f"<100>//BD {out.get('texture_mrd', float('nan')):.2f} MRD (ideal {t['texture_mrd']:.2f})",
                 f"indexed {out['indexed_frac']:.3f}, KAM {out.get('kam_deg', float('nan')):.2f} deg"]
        if not al:
            lines.append(f"beta' {out['beta_prime_frac']:.3f} (true {t['beta_prime_frac']:.3f})")
        ax2 = axes[1, k]
        if not al and t["beta_prime_frac"] > 0.01:
            cmap = matplotlib.colors.ListedColormap(["black", "#cfd8dc", "#e65100", "#1565c0"])
            ax2.imshow(raw["phase"] + 1, origin="lower", extent=ext, cmap=cmap, vmin=-0.5, vmax=3.5,
                       interpolation="nearest")
            ax2.set_title("phase map: FCC grey, beta' orange, kappa blue, black not indexed", fontsize=8)
        else:
            im = ax2.imshow(raw["kam"], origin="lower", extent=ext, cmap="magma", vmin=0, vmax=2.0,
                            interpolation="nearest")
            fig.colorbar(im, ax=ax2, shrink=0.7, label="KAM (deg)")
            ax2.set_title("KAM (first neighbours < 5 deg)", fontsize=9)
        ax2.text(0.02, 0.98, "\n".join(lines), transform=ax2.transAxes, va="top", fontsize=7.5,
                 bbox=dict(facecolor="white", alpha=0.85, edgecolor="none"))
    ins = axes[0, 0].inset_axes([0.70, 0.02, 0.28, 0.25])
    _ipf_key(ins)
    fig.suptitle("Simulated EBSD (20 kV, desktop SEM): maps and what the analysis extracted", fontsize=11)
    fig.savefig(outdir / "ebsd.png", dpi=110)
    plt.close(fig)
    # Kikuchi patterns: FCC Al, FCC Cu, beta'
    pats = []
    for camp, nm, key in (("flaime_al", "AlSi10Mg", "fcc"), ("onr_cu", "70-30 Cu-Ni", "fcc"), ("onr_cu", "NAB", "beta'")):
        r = res.get((camp, nm))
        kk = r["raw"]["kikuchi"] if r else {}
        if key in kk:
            lbl = "FCC" if key == "fcc" else "beta' (DO3 parent)"
            pats.append((f"{nm}: {lbl}", kk[key]))
    big = []
    rng = np.random.default_rng(3)
    q0 = _q_axis_angle(np.array([0.3, 0.2, 1.0]), math.radians(25))
    big.append(("FCC Al, a 4.05 A (400 px)", kikuchi_pattern(q0, "fcc", a=4.0496, sites={"M": {"Al": 1.0}}, size=400, rng=rng)))
    big.append(("FCC Cu, a 3.615 A (400 px)", kikuchi_pattern(q0, "fcc", a=3.6149, sites={"M": {"Cu": 1.0}}, size=400, rng=rng)))
    big.append(("beta' as DO3 Cu3Al, a 5.84 A (400 px)", kikuchi_pattern(q0, "beta'", size=400, rng=rng)))
    allp = big + pats
    fig, axes = plt.subplots(1, len(allp), figsize=(3.3 * len(allp), 3.6), constrained_layout=True)
    for ax, (t, p) in zip(np.atleast_1d(axes), allp):
        ax.imshow(p, cmap="gray", origin="upper")
        ax.set_title(t, fontsize=8)
        ax.set_axis_off()
    fig.suptitle(f"Simulated Kikuchi patterns, {KV:.0f} kV (lambda {wavelength_A():.4f} A), same orientation for the "
                 "first three; then patterns taken from the gallery maps", fontsize=9)
    fig.savefig(outdir / "kikuchi.png", dpi=110)
    plt.close(fig)
    return res


def _circle_rgba(img_rgb, size=512, dark_ring=True):
    from PIL import Image
    h, w = img_rgb.shape[:2]
    s = min(h, w)
    crop = img_rgb[(h - s) // 2:(h - s) // 2 + s, (w - s) // 2:(w - s) // 2 + s]
    im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8)).resize((size, size), Image.NEAREST)
    a = np.array(im.convert("RGBA"))
    yy, xx = np.mgrid[:size, :size]
    r = np.hypot(xx - size / 2 + 0.5, yy - size / 2 + 0.5)
    a[..., 3] = np.where(r <= size / 2 - 4, 255, 0)
    if dark_ring:
        ring = (r > size / 2 - 16) & (r <= size / 2 - 4)
        a[ring, :3] = 30
    return Image.fromarray(a)


def thumbnail_map(path, samples=None):
    """512x512 transparent icon: an IPF-BD map of columnar AlSi10Mg grains with dark boundaries, in a circle."""
    from pathlib import Path
    samples = samples or micro.gallery_samples()
    part = samples["flaime_al"]["AlSi10Mg"][1]
    out = measure(part, "flaime_al", np.random.default_rng(11), fidelity="full", nx=96, ny=96)
    raw = out["raw"]
    img = _ipf_with_gb(raw, True)
    img = img[::-1]                                               # BD up
    img[raw["gb"][::-1]] = 0.08
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    _circle_rgba(img).save(path)


def thumbnail_kikuchi(path, samples=None):
    """512x512 transparent icon: an FCC Kikuchi pattern on its round phosphor screen."""
    from pathlib import Path
    q0 = _q_axis_angle(np.array([0.3, 0.2, 1.0]), math.radians(25))
    p = kikuchi_pattern(q0, "fcc", a=4.0496, sites={"M": {"Al": 1.0}}, size=512, rng=np.random.default_rng(5),
                        counts=20000.0)
    p = np.nan_to_num(p, nan=0.0)
    p = ndimage.gaussian_filter(p, 1.2)                         # an icon: smooth the shot noise
    lo, hi = np.percentile(p[p > 0], [5, 99.5])
    p = np.clip((p - lo) / max(hi - lo, 1e-6), 0, 1) ** 1.6     # dark background, bright bands
    rgb = np.repeat(p[..., None], 3, -1)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    size = 512
    a = np.array(Image.fromarray((rgb * 255).astype(np.uint8)).convert("RGBA"))
    yy, xx = np.mgrid[:size, :size]
    u = (xx + 0.5) / size
    v = (yy + 0.5) / size
    r = np.hypot(u - 0.5, v - 0.5) * size
    alpha = np.where(r <= size / 2 - 2, 255, 0)
    ring = (r > size / 2 - 14) & (r <= size / 2 - 2)
    a[ring, :3] = 40
    a[..., 3] = alpha
    Image.fromarray(a).save(path)


if __name__ == "__main__":
    import sys
    import time
    p = calibrate(n=int(sys.argv[1]) if len(sys.argv) > 1 else 40, reps=3)
    micro.calib_write("ebsd", p)
    t = time.time()
    rows = compare_fast_lite(30)
    for r in rows:
        print("%-9s %-12s %-16s true %.3f lite %.3f+-%.3f fast %.3f+-%.3f" % r)
    print("compare %.1fs" % (time.time() - t))

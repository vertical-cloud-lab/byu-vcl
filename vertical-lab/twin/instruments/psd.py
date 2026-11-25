"""Laser-diffraction particle size: a Malvern Mastersizer 3000 with the Aero S dry dispersion unit, plus a Hall /
Carney flowability helper.

What the instrument does, and what this module simulates (ISO 13320:2020, *Particle size analysis - Laser diffraction
methods*; Malvern Panalytical, *Mastersizer 3000 user manual* MAN0474 and the Aero S dispersion guide,
https://www.malvernpanalytical.com/en/products/product-range/mastersizer-range/mastersizer-3000):

1. **The lot's true volume distribution** (``true_classes``): a mixture over the lot's atomizer runs, each a
   lognormal (d50, geometric SD) weighted by the powder it gave (``charge_g * usable_frac``; failed runs give none),
   as ``twin/physics.py`` makes them. On top of the droplets: **satellites** (fines welded to coarse hosts in flight:
   a share ``min(0.5, satellite_frac / 2)`` of the volume below d50 / 4 sits on hosts above d50, and a share
   ``1.5 satellite_frac`` of the hosts looks 12 % larger; assumed), **agglomerates** of cohesive fines (share ``1 / (1 + (d / d_coh)^3)`` of a class, apparent size 4x;
   d_coh = 15 um for Al and 8 um for Cu, from the Bond number's 1/(rho d^2) scaling, assumed) and, for re-used powder,
   **spatter** (``spatter_frac`` at 2 d50, from ``twin/instruments/reuse.py``).
2. **Dispersion** (Aero S, ``pressure_bar``, default 2 bar): agglomerates survive with exp(-P / P_agg) (P_agg 1.0 bar
   Al, 0.7 bar Cu, assumed), satellites detach with 1 - exp(-P / 8 bar) (welded, so few do; assumed) into a fine mode
   at 0.2 d50. Malvern's guidance is a pressure titration; metal powders are usually measured at 1-3 bar.
3. **Sampling**: the aliquot through the cell (2 g Al, 5 g Cu, assumed) holds a finite number of particles per size
   class, drawn Poisson; the few coarse particles make the coarse tail, and so d90, noisy (ISO 13320 section 6.2).
4. **Optics** (He-Ne, 632.8 nm, 50 log-spaced detectors 0.01-60 deg in full, 26 in lite): per particle, Fraunhofer
   diffraction a^2 (ka)^2 [J1(ka sin t)/(ka sin t)]^2 plus geometric reflection (a^2 / 4) R(i), i = (pi - t)/2, with
   Schlick's Fresnel approximation from the metal's complex index (Al 1.37 + 7.62i, Rakic 1995; Cu 0.27 + 3.41i,
   Johnson & Christy 1972; https://refractiveindex.info). Real atomized powder is rough and oxidised, so only part of
   its reflection is specular (``0.9 (1 - 0.3 sat) exp(-O / 20000 ppm)``, assumed); the rest goes to a Lambertian
   sphere's backward lobe. Non-spherical particles in random orientation broaden the apparent size by a lognormal of
   SD 0.6 (1 - sphericity) (assumed; sphericity 0.95 - 0.5 sat, the same relation as the SEM stub).
5. **Noise**: 0.4 % per detector plus a floor of 1e-4 of the largest signal, fixed per-detector gain errors of 0.3 %
   (one instrument), and aliquot to aliquot a riffling tilt (4 % per unit ln d) and a 0.6 % apparent-scale shift
   (dispersion, alignment) (all assumed), giving about 1 % d50 repeatability, as Malvern quotes for the Mastersizer
   3000 (ISO 13320 asks < 3 % RSD at d50).
6. **The analysis**, as the software does it: non-negative least squares of the detector signal against the optical
   model the operator picked, with smoothing (Tikhonov, second differences in log size, weight 0.3 of the data
   norm: the "general purpose" model; it broadens a narrow distribution a little, as the real analysis does). ``optical="mie"`` (default) uses the metal's index and a smooth sphere; ``optical="fraunhofer"`` has no
   reflection, so the wide-angle light that real particles reflect is read as fines (the known Fraunhofer artifact
   for metal powders). ``ri=(n, k)`` sets another index (e.g. Malvern's default 1.5 + 0.1i). Each result is the mean of
   ``n_meas`` aliquots (3 in full, 1 in lite). Then d10, d50, d90 (log-linear interpolation of the cumulative), span
   = (d90 - d10) / d50, the volume share in the campaign's cut (20-63 um Al LPBF, 45-150 um Cu DED) and below 15 um.

Fidelity: ``full`` (90 classes 0.5-2000 um, 50 detectors, 3 aliquots, ``raw`` for figures), ``lite`` (40 classes,
26 detectors, 1 aliquot; about 2 ms), ``fast`` (the lot's analytic d10/d50/d90 and fractions, with log-ratio or
additive deviations drawn from a multivariate normal whose mean is linear in the lot's state (satellites, fines,
gsd, d50, spatter) and whose covariance keeps d10/d50/d90 correlated; fitted by ``calibrate`` on the lite chain;
built-in defaults until ``calib_mech.json`` has a ``psd`` section).

``flow(sample)``: Hall (ASTM B213, 2.54 mm orifice, 50 g) or Carney (ASTM B964, 5.08 mm) flow time from Beverloo's
orifice law W = 0.58 rho_b sqrt(g) (D0 - 1.4 d)^2.5 (Beverloo, Leniger & van de Velde, Chem. Eng. Sci. 15, 1961;
x 1.3 for the 60 deg funnel, assumed),
slowed by cohesion through a granular Bond number on the Sauter diameter (van der Waals with nano-asperities: F =
A r_a / (12 z0^2) (1 + 2 sat), A = 6.5e-20 J, r_a = 12 nm, z0 = 0.4 nm, all assumed, set so that a 20-63 um
gas-atomized AlSi10Mg sits at the Hall funnel's edge) and Capece et al.'s ffc = 3.7 Bo^-0.27
(Powder Technol. 286, 2015, as recalled; check), and by satellites and low sphericity. No Hall flow below ffc 3.5,
no Carney flow below 2.2 (assumed). ``lof_factor`` is the suggested multiplier on LPBF lack-of-fusion porosity for a
powder that spreads badly: 1 for a Hall flow time under 60 s, rising 0.5 per 40 s beyond it, 1.8 for Carney-only,
2.5 for no flow (assumed; Spierings et al., Prog. Addit. Manuf. 1, 2016, show Hall flow alone predicts spreading
poorly, so this is a policy knob, not a law).
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from scipy.optimize import nnls
from scipy.special import j1, ndtr

CUTS = {"flaime_al": (20.0, 63.0), "onr_cu": (45.0, 150.0)}
FINES_UM = 15.0
LAMBDA_UM = 0.6328
RI = {"Al": (1.37, 7.62), "Cu": (0.27, 3.41)}           # 633 nm (refractiveindex.info: Rakic 1995; Johnson & Christy)
RHO_SOLID = {"Al": 2.68, "Cu": 8.7}                      # g/cm3, alloy-ish defaults
D_COH = {"Al": 15.0, "Cu": 8.0}                          # um, agglomeration onset (assumed, Bond-number scaling)
P_AGG = {"Al": 1.0, "Cu": 0.7}                           # bar (assumed)
P_SAT = 8.0                                              # bar (assumed)
ALIQUOT_G = {"Al": 2.0, "Cu": 5.0}                       # g per measurement (assumed)
GRIDS = {"full": (0.5, 2000.0, 90, 50, 3), "lite": (1.0, 1500.0, 40, 26, 1)}
OUT = ("d10_um", "d50_um", "d90_um", "span", "cut_frac", "fines_frac")

SPEC = dict(station="psd", instrument="Malvern Mastersizer 3000 + Aero S dry dispersion", hours=0.25,
            consumables={"sample_g_Al": 6.0, "sample_g_Cu": 15.0},
            note="3 aliquots of 2 g (Al) or 5 g (Cu), each consumed (dry dispersion); 15 min with cleaning (assumed)")


def _base(campaign):
    return "Al" if campaign == "flaime_al" else "Cu"


# ------------------------------------------------------------------------------------------------ the lot's truth
def runs_of(sample, campaign):
    """[(weight, d50_um, gsd)] of the powder the lot holds (weights sum to 1)."""
    out = []
    for r in sample.get("runs") or []:
        if r.get("failed"):
            continue
        w = r.get("charge_g", 300.0 if campaign == "flaime_al" else 800.0) * r.get("usable_frac", 0.9)
        if w > 0:
            out.append((w, float(r["d50_um"]), float(r.get("gsd", 1.6))))
    if not out:
        d50 = sample.get("d50_um")
        if d50 is None or not np.isfinite(d50):
            d50 = 35.0 if campaign == "flaime_al" else 60.0     # campaign._do_gas_atomize's medians
        out = [(1.0, float(d50), float(sample.get("gsd", 1.8)))]
    tot = sum(w for w, _, _ in out)
    return [(w / tot, d, g) for w, d, g in out]


def _cdf(x_um, runs):
    x = np.maximum(np.asarray(x_um, float), 1e-9)
    c = np.zeros_like(x)
    for w, d50, g in runs:
        c += w * ndtr(np.log(x / d50) / math.log(g))
    return c


def true_values(sample, campaign) -> dict:
    """The lot's own (primary droplet) d10, d50, d90, span, cut and fines shares: what fast mode perturbs."""
    runs = runs_of(sample, campaign)
    grid = np.exp(np.linspace(math.log(0.3), math.log(5000.0), 240))
    c = _cdf(grid, runs)
    sp = float(sample.get("spatter_frac", 0.0) or 0.0)
    if sp > 0:
        dm = math.exp(sum(w * math.log(d) for w, d, _ in runs))
        c = (1 - sp) * c + sp * ndtr(np.log(grid / (2.0 * dm)) / 0.35)
    lg = np.log(grid)
    q = {p: float(np.exp(np.interp(p, c, lg))) for p in (0.1, 0.5, 0.9)}
    lo, hi = CUTS[campaign]
    ci = np.interp(np.log([lo, hi, FINES_UM]), lg, c)
    return dict(d10_um=q[0.1], d50_um=q[0.5], d90_um=q[0.9], span=(q[0.9] - q[0.1]) / q[0.5],
                cut_frac=float(ci[1] - ci[0]), fines_frac=float(ci[2]))


# ------------------------------------------------------------------------------------------------ grids and optics
@lru_cache(maxsize=8)
def _grid(fid):
    lo, hi, n, ndet, _ = GRIDS[fid]
    edges = np.exp(np.linspace(math.log(lo), math.log(hi), n + 1))
    d = np.sqrt(edges[:-1] * edges[1:])
    th_edges = np.radians(np.exp(np.linspace(math.log(0.01), math.log(60.0), ndet + 1)))
    return edges, d, th_edges


def _schlick(R0, cos_i):
    return R0 + (1 - R0) * (1 - cos_i) ** 5


def _r0(ri):
    n, k = ri
    return ((n - 1) ** 2 + k ** 2) / ((n + 1) ** 2 + k ** 2)


@lru_cache(maxsize=32)
def _kernels(fid, ri):
    """Per unit particle volume, the light on each detector annulus: (diffraction, specular, diffuse) parts."""
    edges, d, th = _grid(fid)
    nsub = 6
    a = d[None, :] * 0.5                                       # um
    kx = 2 * math.pi / LAMBDA_UM
    vol = math.pi / 6 * d ** 3
    R0 = _r0(ri)
    Kd = np.zeros((len(th) - 1, len(d)))
    Ks, Kl = np.zeros_like(Kd), np.zeros_like(Kd)
    for j in range(len(th) - 1):
        t = np.exp(np.linspace(math.log(th[j]), math.log(th[j + 1]), nsub))[:, None]
        dom = 2 * math.pi * np.sin(t) * np.gradient(t[:, 0])[:, None]          # solid angle per sub-angle
        u = kx * a * np.sin(t)
        airy = np.where(u > 1e-8, (2 * j1(u) / np.maximum(u, 1e-12)) ** 2, 1.0)
        diff = a ** 2 * (kx * a) ** 2 / 4.0 * airy                                 # a^2 (ka)^2 [J1(u)/u]^2
        cos_i = np.cos((math.pi - t) / 2)
        spec = a ** 2 / 4.0 * _schlick(R0, cos_i)
        alpha = math.pi - t                                                       # phase angle, Lambert sphere
        lamb = a ** 2 * R0 * (np.sin(alpha) + (math.pi - alpha) * np.cos(alpha)) / (math.pi * 4.0) * (8 / 3)
        Kd[j] = (diff * dom).sum(0) / vol
        Ks[j] = (spec * dom).sum(0) / vol
        Kl[j] = (np.maximum(lamb, 0) * dom).sum(0) / vol
    return Kd, Ks, Kl


@lru_cache(maxsize=32)
def _inverse_setup(fid, ri, optical):
    edges, d, th = _grid(fid)
    Kd, Ks, _ = _kernels(fid, ri)
    K = Kd if optical == "fraunhofer" else Kd + Ks
    n = len(d)
    L = np.zeros((n - 2, n))
    for i in range(n - 2):
        L[i, i:i + 3] = (1.0, -2.0, 1.0)
    return K, L


def _blur(v, dlog, sig):
    if sig <= 1e-3:
        return v
    x = np.arange(len(v)) * dlog
    G = np.exp(-0.5 * ((x[:, None] - x[None, :]) / sig) ** 2)
    G /= G.sum(0, keepdims=True)
    return G @ v


def _shift(v, dlog, delta):
    """Move a distribution by delta in ln d (mass conserving, linear interpolation between classes)."""
    s = delta / dlog
    k = int(math.floor(s))
    f = s - k
    out = np.zeros_like(v)
    n = len(v)
    for src in range(n):
        for dst, w in ((src + k, 1 - f), (src + k + 1, f)):
            out[min(max(dst, 0), n - 1)] += w * v[src]
    return out


def detected_classes(sample, campaign, fid, pressure_bar=2.0):
    """The lot's volume distribution per class, and what the dispersion presents to the beam."""
    edges, d, _ = _grid(fid)
    dlog = math.log(edges[1] / edges[0])
    base = _base(campaign)
    runs = runs_of(sample, campaign)
    v_true = np.diff(_cdf(edges, runs))
    v_true[0] += _cdf(edges[:1], runs)[0]
    v_true[-1] += 1 - _cdf(edges[-1:], runs)[0]
    dm = math.exp(sum(w * math.log(d50) for w, d50, _ in runs))
    sp = float(sample.get("spatter_frac", 0.0) or 0.0)
    if sp > 0:
        spat = np.diff(ndtr(np.log(edges / (2.0 * dm)) / 0.35))
        v_true = (1 - sp) * v_true + sp * spat / max(spat.sum(), 1e-12)
    v = v_true.copy()
    sat = float(sample.get("satellite_frac", 0.05) or 0.05)
    # satellites: fine volume onto hosts above d50, hosts look 12 % larger; some detach under the jet
    fine = d < 0.25 * dm
    moved = v * fine * min(0.5, 0.5 * sat)
    m_s = moved.sum()
    v = v - moved
    host = (d > dm) * v
    if host.sum() > 0 and m_s > 0:
        det = 1 - math.exp(-pressure_bar / P_SAT)
        stuck = host / host.sum() * m_s * (1 - det)
        shell = host * min(1.0, 1.5 * sat)                      # satellited hosts, apparent size +12 %
        v = v - shell + _shift(shell + stuck, dlog, math.log(1.12))
        fm = np.diff(ndtr(np.log(edges / (0.2 * dm)) / 0.3))
        v = v + fm / max(fm.sum(), 1e-12) * m_s * det
    # agglomerates of cohesive fines that survive the jet
    agg = v / (1 + (d / D_COH[base]) ** 3) * math.exp(-pressure_bar / P_AGG[base])
    if agg.sum() > 1e-9:
        v = v - agg + _blur(_shift(agg, dlog, math.log(4.0)), dlog, 0.3)
    v = np.maximum(v, 0)
    return v_true / v_true.sum(), v / v.sum(), dm, sat


def _analyse(edges, v, campaign):
    c = np.concatenate([[0.0], np.cumsum(v)])
    c /= c[-1]
    lg = np.log(edges)
    cm = np.maximum.accumulate(c + np.arange(len(c)) * 1e-12)
    q = {p: float(np.exp(np.interp(p, cm, lg))) for p in (0.1, 0.5, 0.9)}
    lo, hi = CUTS[campaign]
    ci = np.interp(np.log([lo, hi, FINES_UM]), lg, c)
    return dict(d10_um=q[0.1], d50_um=q[0.5], d90_um=q[0.9], span=(q[0.9] - q[0.1]) / q[0.5],
                cut_frac=float(max(ci[1] - ci[0], 0.0)), fines_frac=float(max(ci[2], 0.0))), c


_GAIN = {}


def _gain(ndet):
    if ndet not in _GAIN:
        _GAIN[ndet] = 1 + 0.003 * np.random.default_rng(13320).standard_normal(ndet)
    return _GAIN[ndet]


def _chain(sample, campaign, rng, fid, optical="mie", ri=None, pressure_bar=2.0, n_meas=None, aliquot_g=None,
           smooth=0.3, f_spec=None):
    edges, d, th = _grid(fid)
    base = _base(campaign)
    ri_true = RI[base]
    ri_fit = tuple(ri) if ri is not None else ri_true
    n_meas = GRIDS[fid][4] if n_meas is None else int(n_meas)
    dlog = math.log(edges[1] / edges[0])
    v_true, v_det, dm, sat = detected_classes(sample, campaign, fid, pressure_bar)
    sph = float(np.clip(0.95 - 0.5 * sat, 0.6, 0.99))
    ox = float(sample.get("oxygen_ppm", 500.0) or 500.0)
    if f_spec is None:
        f_spec = 0.9 * (1 - 0.3 * sat) * math.exp(-ox / 20000.0)
    Kd, Ks, Kl = _kernels(fid, ri_true)
    Ktrue = Kd + f_spec * Ks + (1 - f_spec) * Kl
    K, L = _inverse_setup(fid, ri_fit, optical)
    rho = RHO_SOLID[base] * 1e-12                                   # g/um3
    m = (ALIQUOT_G[base] if aliquot_g is None else aliquot_g)
    npart_per_vol = m / (rho * math.pi / 6 * d ** 3)                # particles per unit volume fraction
    gain = _gain(len(th) - 1)
    results, vs, sigs = [], [], []
    for _ in range(n_meas):
        lam = v_det * npart_per_vol
        N = rng.poisson(np.minimum(lam, 1e15)).astype(float)
        vs_ = N / npart_per_vol
        vs_ = _blur(vs_ / max(vs_.sum(), 1e-30), dlog, 0.6 * (1 - sph))
        # aliquot-to-aliquot: riffling segregation tilts coarse vs fine, and the dispersion and beam alignment move
        # the apparent scale (assumed 4 % tilt per ln d and 0.6 % scale, so d50 repeats to about 1 %)
        vs_ = vs_ * np.exp(rng.normal(0, 0.04) * (np.log(d) - math.log(dm)))
        vs_ = _shift(vs_ / vs_.sum(), dlog, rng.normal(0, 0.006))
        s = Ktrue @ vs_
        s = s * gain
        s = s + rng.standard_normal(len(s)) * (0.004 * s + 1e-4 * s.max())
        s = np.maximum(s, 0)
        w = 1.0 / (0.004 * s + 1e-4 * s.max())
        A = K * w[:, None]
        cn = np.linalg.norm(A, axis=0)
        cn[cn == 0] = 1.0
        An = A / cn
        Ln = L / cn[None, :]
        Ln = Ln * (smooth * np.linalg.norm(An) / max(np.linalg.norm(Ln), 1e-30))
        M = np.vstack([An, Ln])
        b = np.concatenate([s * w, np.zeros(Ln.shape[0])])
        u, _ = nnls(M, b, maxiter=50 * M.shape[1])
        vh = u / cn
        vh = vh / max(vh.sum(), 1e-30)
        r, _c = _analyse(edges, vh, campaign)
        results.append(r)
        vs.append(vh)
        sigs.append((s, K @ vh * (s.sum() / max((K @ vh).sum(), 1e-30))))
    out = {k: float(np.mean([r[k] for r in results])) for k in OUT}
    vmean = np.mean(vs, 0)
    if fid == "full":
        out["d50_rsd"] = float(np.std([r["d50_um"] for r in results], ddof=1) / out["d50_um"]) if n_meas > 1 else None
        tv = _analyse(edges, v_true, campaign)[0]
        out["raw"] = dict(edges_um=edges, d_um=d, v_true=v_true, v_presented=v_det, v_meas=vmean,
                          v_meas_all=np.array(vs), cum_true=_analyse(edges, v_true, campaign)[1],
                          cum_meas=_analyse(edges, vmean, campaign)[1], angles_deg=np.degrees(np.sqrt(th[:-1] * th[1:])),
                          signal=sigs[0][0], fit=sigs[0][1], per_aliquot=results, truth=tv, cut=CUTS[campaign],
                          optical=optical, ri_fit=ri_fit, pressure_bar=pressure_bar, sphericity=sph)
    return out


# ------------------------------------------------------------------------------------------------ fast mode
_DEFAULT = {   # used until calib_mech.json has a psd section: (intercept, sat, fines, ln gsd, ln d50/50, spatter)
    "flaime_al": dict(coef=[[0.03, 0.30, 0.0, 0.0, 0.0, 0.0], [0.0, 0.10, 0.0, 0.0, 0.0, 0.3],
                            [0.0, 0.05, 0.0, 0.0, 0.0, 0.5], [0.0, -0.10, 0.0, 0.0, 0.0, 0.0],
                            [-0.01, 0.0, 0.0, 0.0, 0.0, 0.0]], cov=None, sd=[0.03, 0.012, 0.02, 0.01, 0.003]),
}


def _features(sample, campaign, tv):
    runs = runs_of(sample, campaign)
    g = math.exp(math.sqrt(sum(w * math.log(gg) ** 2 for w, _, gg in runs)))
    return [1.0, float(sample.get("satellite_frac", 0.05) or 0.05), tv["fines_frac"], math.log(g),
            math.log(tv["d50_um"] / 50.0), float(sample.get("spatter_frac", 0.0) or 0.0)]


def _targets(meas, tv):
    return [math.log(meas["d10_um"] / tv["d10_um"]), math.log(meas["d50_um"] / tv["d50_um"]),
            math.log(meas["d90_um"] / tv["d90_um"]), meas["cut_frac"] - tv["cut_frac"],
            meas["fines_frac"] - tv["fines_frac"]]


def _fast(sample, campaign, rng):
    from twin.instruments.mech import calib
    tv = true_values(sample, campaign)
    c = calib("psd").get(campaign) or _DEFAULT.get(campaign) or _DEFAULT["flaime_al"]
    x = np.array(_features(sample, campaign, tv))
    if "x_mean" in c:                       # centred features, clipped to the range calibrated on
        x[1:] = np.clip(x[1:], c["x_min"], c["x_max"]) - np.array(c["x_mean"])
    mu = np.array(c["coef"]) @ x
    if c.get("chol") is not None:
        e = mu + np.array(c["chol"]) @ rng.standard_normal(len(mu))
    else:
        e = mu + np.array(c["sd"]) * rng.standard_normal(len(mu))
    d10, d50, d90 = tv["d10_um"] * math.exp(e[0]), tv["d50_um"] * math.exp(e[1]), tv["d90_um"] * math.exp(e[2])
    d10, d90 = min(d10, d50 * 0.999), max(d90, d50 * 1.001)
    return dict(d10_um=d10, d50_um=d50, d90_um=d90, span=(d90 - d10) / d50,
                cut_frac=float(np.clip(tv["cut_frac"] + e[3], 0, 1)),
                fines_frac=float(np.clip(tv["fines_frac"] + e[4], 0, 1)))


def measure(sample, campaign, rng, fidelity="fast", optical="mie", ri=None, pressure_bar=2.0, n_meas=None, **kw):
    """d10_um d50_um d90_um span cut_frac fines_frac of a powder lot (``full`` adds ``raw`` and ``d50_rsd``)."""
    if fidelity == "fast" and optical == "mie" and ri is None and abs(pressure_bar - 2.0) < 1e-9:
        return _fast(sample, campaign, rng)
    fid = "full" if fidelity == "full" else "lite"
    return _chain(sample, campaign, rng, fid, optical=optical, ri=ri, pressure_bar=pressure_bar, n_meas=n_meas)


def calibrate(samples_by_campaign, rng, reps=3) -> dict:
    """Fit fast mode on the lite chain: deviations (log ratios for d10/d50/d90, differences for the shares) linear
    in the lot's state, with the residual covariance (as a Cholesky factor) so the quantiles stay correlated."""
    out = {}
    for campaign, pairs in samples_by_campaign.items():
        X, Y = [], []
        for lot, _part in pairs:
            tv = true_values(lot, campaign)
            for _ in range(reps):
                m = _chain(lot, campaign, rng, "lite")
                X.append(_features(lot, campaign, tv))
                Y.append(_targets(m, tv))
        X, Y = np.array(X), np.array(Y)
        xm, xlo, xhi = X[:, 1:].mean(0), X[:, 1:].min(0), X[:, 1:].max(0)
        X[:, 1:] -= xm                                                  # a feature that never varied gets 0
        coef = np.linalg.lstsq(X, Y, rcond=1e-6)[0].T                  # (5 outputs, 6 features)
        res = Y - X @ coef.T
        cov = np.cov(res.T) + np.eye(Y.shape[1]) * 1e-10
        out[campaign] = dict(coef=coef.tolist(), chol=np.linalg.cholesky(cov).tolist(), x_mean=xm.tolist(),
                             x_min=xlo.tolist(), x_max=xhi.tolist(),
                             sd=np.sqrt(np.diag(cov)).tolist(), n=int(len(Y)),
                             features="1 sat fines ln_gsd ln_d50/50 spatter",
                             targets="ln d10 ln d50 ln d90 (ratio to truth); cut, fines (difference)",
                             mean_bias=Y.mean(0).tolist())
    return {"psd": out}


# ------------------------------------------------------------------------------------------------ flowability
def flow(sample, campaign=None) -> dict:
    """Hall / Carney flow of a lot (see the module docstring for the assumed relations)."""
    campaign = campaign or sample.get("campaign", "flaime_al")
    base = _base(campaign)
    runs = runs_of(sample, campaign)
    sat = float(sample.get("satellite_frac", 0.05) or 0.05)
    sph = float(sample.get("sphericity", np.clip(0.95 - 0.5 * sat, 0.6, 0.99)))
    grid = np.exp(np.linspace(math.log(0.5), math.log(2000.0), 200))
    pdf = np.diff(_cdf(grid, runs))
    dc = np.sqrt(grid[:-1] * grid[1:])
    d32 = float(pdf.sum() / max((pdf / dc).sum(), 1e-12))             # Sauter mean, um (volume / surface)
    rho = RHO_SOLID[base] * 1000.0
    A, ra, z0 = 6.5e-20, 0.012e-6, 0.4e-9
    F = A * ra / (12 * z0 ** 2) * (1 + 2.0 * sat)
    Wp = rho * math.pi / 6 * (d32 * 1e-6) ** 3 * 9.81
    bo = F / Wp
    ffc = 3.7 * bo ** -0.27 * sph ** 2
    rho_b = rho * 0.60 * sph ** 1.5 * (1 - 0.3 * sat) / (1 + 0.15 * bo)   # apparent density (assumed packing)
    d_m = d32 * 1e-6

    def t_flow(D0):
        # Beverloo through a flat orifice, x 1.3 for the funnels' 60 deg cones (assumed hopper factor)
        W = 1.3 * 0.58 * rho_b * math.sqrt(9.81) * max(D0 - 1.4 * d_m, 1e-5) ** 2.5    # kg/s
        return 0.050 / W * (1 + 2.5 * sat) * (1 + 0.6 / max(ffc - 2.5, 0.1))

    hall = t_flow(2.54e-3) if ffc >= 3.5 else None
    carney = t_flow(5.08e-3) if ffc >= 2.2 else None
    if hall is not None and hall < 200:
        lof = 1.0 + 0.5 * max(0.0, (hall - 60.0) / 40.0)
    elif carney is not None:
        lof = 1.8
    else:
        lof = 2.5
    return dict(hall_s_50g=hall, carney_s_50g=carney, flows_hall=hall is not None, no_flow=carney is None,
                ffc=ffc, bond=bo, d32_um=d32, apparent_density_g_cm3=rho_b / 1000.0, sphericity=sph,
                lof_factor=lof)


# ------------------------------------------------------------------------------------------------ figures
def draw(res, axs):
    """Two axes: volume density (log x) with d10/d50/d90 and the cut shaded; cumulative undersize."""
    raw = res["raw"]
    e, d = raw["edges_um"], raw["d_um"]
    dl = np.diff(np.log10(e))
    ax = axs[0]
    lo, hi = raw["cut"]
    ax.axvspan(lo, hi, color="#2a9d8f", alpha=0.15, lw=0, label=f"cut {lo:g}-{hi:g} um")
    ax.plot(d, raw["v_true"] / dl * 100 / 100, color="0.55", lw=1.5, ls="--", label="lot (truth)")
    for v in raw["v_meas_all"]:
        ax.plot(d, v / dl, color="#e76f51", lw=0.6, alpha=0.5)
    ax.plot(d, raw["v_meas"] / dl, color="#e76f51", lw=2.0, label="measured (mean)")
    for k, ls in (("d10_um", ":"), ("d50_um", "-"), ("d90_um", ":")):
        ax.axvline(res[k], color="#264653", ls=ls, lw=1)
        ax.text(res[k], ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0 else 1, k[:3], fontsize=7, ha="center")
    ax.set_xscale("log")
    ax.set_xlabel("size (um)")
    ax.set_ylabel("volume density (frac / log10 d)")
    ax.legend(fontsize=7, frameon=False)
    ax = axs[1]
    ax.plot(e, raw["cum_true"] * 100, color="0.55", ls="--", lw=1.5, label="truth")
    ax.plot(e, raw["cum_meas"] * 100, color="#e76f51", lw=2, label="measured")
    ax.axvspan(lo, hi, color="#2a9d8f", alpha=0.15, lw=0)
    ax.axvline(FINES_UM, color="0.3", lw=0.8, ls=":")
    ax.set_xscale("log")
    ax.set_xlabel("size (um)")
    ax.set_ylabel("cumulative undersize (vol %)")
    ax.set_title(f"d50 {res['d50_um']:.1f} um, span {res['span']:.2f}, cut {100 * res['cut_frac']:.0f} %", fontsize=8)
    ax.legend(fontsize=7, frameon=False)


def thumb(ax, res=None):
    """Icon: a bold lognormal with the cut window shaded (transparent background is the caller's savefig)."""
    x = np.exp(np.linspace(math.log(5), math.log(400), 200))
    y = np.exp(-0.5 * (np.log(x / 60) / 0.45) ** 2)
    m = (x > 25) & (x < 110)
    ax.fill_between(x[m], 0, y[m], color="#2a9d8f", alpha=0.85, lw=0)
    ax.plot(x, y, color="#264653", lw=9, solid_capstyle="round")
    ax.set_xscale("log")
    ax.set_ylim(0, 1.15)
    ax.set_axis_off()

"""SEM: secondary-electron images of powder on carbon tape and backscattered-electron images of polished sections,
then the image analysis a lab runs on them (Hitachi TM4000-class desktop SEM, 15 kV).

**Powder (``measure_powder``).** The sieved cut of the lot (``micro.powder_population``: one lognormal per good
atomizer run, volume median d50 and geometric SD, cut 20-63 um for Al and 45-150 um for Cu, 4 % by mass leaking
through the sieves) is dispersed as a monolayer at 35 % area coverage (assumed) by random sequential placement that
lets neighbours touch. Particles are spheres, or for the share of the melt that ran cold (low true superheat)
elongated lumpy ligaments; a share ``satellite_frac`` of them carries 1-3 satellites (0.05-0.35 of the host's radius)
welded at random elevations. A height map gives the surface normals; the SE yield follows the secant of the local
tilt (the edge effect, Goldstein et al. 2018 ch. 3), the Everhart-Thornley detector side is brighter and the tape
behind a particle is shadowed; electron shot noise for the dwell. Analysis: Gaussian smoothing, a threshold above
the tape's histogram peak (Otsu's 1979 split falls between particle faces and their bright edges), hole filling,
distance transform and marker watershed to split touching particles (Beucher & Meyer 1993), border-touching
particles excluded, equivalent circle diameters weighted by volume for the d50,
circularity 4 pi A / P^2 (perimeter from crack-edge counts x pi/4), satellites as the residue of a morphological
opening still attached to a host.

**Section (``measure_section``).** A vertical section (the build direction up the image) through the part's pore
and crack populations (``micro.phase_model(..., 'part')``): pores sampled in a 3-D slab and cut by the plane (sizes
size-biased by their caliper, cut at a random height), lack-of-fusion pores as irregular oblate spheroids lying in
the layers, keyhole and gas pores spherical; hot cracks as tortuous traces along the build direction with micron
openings (partial-volume contrast when narrower than a pixel); phases by their backscatter coefficient (Reuter's
fit, ``micro.bse_eta``), resolved where larger than a pixel and averaged in otherwise; polishing scratches; shot
noise. Analysis: threshold at half the matrix level for pores plus a black top-hat for thin dark features, connected
components, moments (elongation, width) to call a feature a crack, circularity and elongation to call a pore lack of
fusion, skeleton length of the cracks. So the section's biases come out of the chain: the 2-D cut underestimates the
largest pore (DeHoff & Rhines 1968), pores below about two pixels vanish, cracks narrower than the pixel are found
in pieces, and a single field's porosity scatters with the few large pores in it.

**Fast mode.** ``measure_powder``: per-output regressions of the lite chain's bias and spread on the lot's state
(cut volume-median, irregular and satellite shares). ``measure_section``: the same stereological sampler as the
image (so the scatter from the few pores in a field and the cut's size bias are exact), followed by detection,
area, classification and crack-recovery transfer functions fitted on the lite chain (``calibrate``).

Field of view and pixel size are a trade-off and part of the physics: lite powder fields are 192 px at 2 (Al) / 4
(Cu) um per px, full 1024 px at 1 / 2 um; lite sections 256 px at 4 um (1.05 mm2), full 1024 px at 2 um (4.2 mm2,
a 2 x 2 mosaic of 512 px frames). The fast mode reproduces the lite chain. Every constant that is ours says
"assumed"; sources and the calibration are in notes/twin_instruments_micro.md.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage as ndi

from twin.instruments import micro

SPEC_POWDER = dict(station="byu_sem", hours=0.4, consumables={"carbon_tape_stub": 1},
                   note="powder on carbon tape, 3-5 fields at 100-300x, SE detector, 15 kV (assumed times)")
SPEC_SECTION = dict(station="byu_sem", hours=0.6, consumables={},
                    prep=dict(station="prep", hours=1.5, consumables={"hot_mount": 1, "polish_set": 1}),
                    note="sectioned along the build direction, mounted, polished to 0.05 um; BSE mosaic at 15 kV")
SPEC = dict(station="byu_sem", hours=SPEC_POWDER["hours"] + SPEC_SECTION["hours"],
            consumables={"carbon_tape_stub": 1}, prep=SPEC_SECTION["prep"], powder=SPEC_POWDER, section=SPEC_SECTION)

POWDER_PX = {"flaime_al": 1.0, "onr_cu": 2.0}     # um per px at full fidelity (lite: twice as coarse)
SECTION_PX = {"full": 2.0, "lite": 4.0}
NPX = {"full": 1024, "lite": 256}
NPX_POWDER_LITE = 192                              # lite powder field: 192 px (fewer particles, same analysis)
COVERAGE = 0.35                                    # area share of the tape covered by powder (assumed)
DOSE = 600.0                                       # primary electrons per pixel (e.g. 50 pA x 2 us) (assumed)
SE_YIELD = {"Al": 0.16, "Cu": 0.20, "tape": 0.06}  # effective SE yield x collection (assumed)
BSE_DOSE = 1000.0
BSE_COLLECT = 0.6
DET_ELEV = math.radians(30.0)                      # ET detector elevation seen from the stub (assumed)
SHADOW_ELEV = math.radians(45.0)                   # the collector field bends SE paths: shadows shorter (assumed)


# =================================================================================================== powder
def _cut_grid(pop, n=240):
    """Volume-density of the sieved cut on a log grid: mixture of the runs' lognormals (volume-weighted, median
    d50), inside the cut, plus the sieve leak spread over the rest. Returns (d, volume pdf)."""
    lo, hi = pop["cut"]
    d = np.exp(np.linspace(math.log(2.0), math.log(600.0), n))
    pdf = np.zeros(n)
    for c in pop["components"]:
        s = math.log(c["gsd"])
        pdf += c["w"] * np.exp(-0.5 * ((np.log(d) - math.log(c["d50"])) / s) ** 2) / s
    inside = (d >= lo) & (d <= hi)
    vin = pdf[inside].sum()
    vout = pdf[~inside].sum()
    leak = pop.get("sieve_leak", 0.04)
    if vout > 0 and vin > 0:
        pdf = np.where(inside, pdf, pdf * leak / (1 - leak) * vin / vout)
    return d, pdf / pdf.sum()


def _powder_state(pop):
    """The lot's own numbers the fast model regresses on: the cut's volume median, its irregular share and the
    satellite share (all hidden state, used only to sample the instrument's errors)."""
    d, pdf = _cut_grid(pop)
    cdf = np.cumsum(pdf)
    dv50 = float(np.interp(0.5, cdf, d))
    irr = float(sum(c["w"] * c["irregular"] for c in pop["components"]))
    return dict(dv50=dv50, irr=irr, sat=float(pop["satellite_frac"]))


def _draw_particles(pop, W, rng):
    """Particles of the sieved cut on a W x W um field: number-weighted sizes from the volume pdf (n ~ pdf / d^3)."""
    d, pdf = _cut_grid(pop)
    pn = pdf / d ** 3
    pn = pn / pn.sum()
    mean_area = float(np.sum(pn * math.pi / 4 * d ** 2))
    n = rng.poisson(COVERAGE * W * W / mean_area)
    idx = rng.choice(len(d), size=n, p=pn)
    dl = np.log(d)
    step = dl[1] - dl[0]
    D = np.exp(dl[idx] + rng.uniform(-0.5, 0.5, n) * step)
    D = np.sort(D)[::-1]                                     # place the large ones first
    irr_p = np.array([c["irregular"] for c in pop["components"]])
    wts = np.array([c["w"] for c in pop["components"]])
    p_irr = float(np.sum(irr_p * wts))
    parts = []
    X = np.empty(len(D))
    Y = np.empty(len(D))
    Rr = np.empty(len(D))
    k = 0
    tries = rng.uniform(0, 1, (len(D), 12, 2))
    for i, Di in enumerate(D):
        R = Di / 2
        for t in range(12):
            x, y = -R + tries[i, t, 0] * (W + 2 * R), -R + tries[i, t, 1] * (W + 2 * R)
            if k and np.any((X[:k] - x) ** 2 + (Y[:k] - y) ** 2 < ((Rr[:k] + R) * 0.94) ** 2):
                continue                                  # touching allowed, overlap not (assumed 6 %)
            X[k], Y[k], Rr[k] = x, y, R
            k += 1
            irregular = rng.random() < p_irr
            p = dict(x=x, y=y, R=R, irregular=irregular, sats=[])
            if irregular:
                p["aspect"] = float(np.clip(math.exp(rng.normal(math.log(1.9), 0.3)), 1.2, 4.0))
                p["ang"] = rng.uniform(0, math.pi)
                p["modes"] = [(kk, 0.10 * rng.normal() / kk ** 0.7, rng.uniform(0, 2 * math.pi)) for kk in range(2, 7)]
            if rng.random() < pop["satellite_frac"]:
                for _ in range(1 + rng.poisson(0.6)):
                    rs_ = R * float(np.clip(math.exp(rng.normal(math.log(0.14), 0.35)), 0.05, 0.35))
                    p["sats"].append(dict(r=rs_, phi=rng.uniform(0, 2 * math.pi),
                                          el=math.radians(rng.uniform(-10, 60))))
            parts.append(p)
            break
    return parts


_GRID: dict = {}


def _grid(N):
    if N not in _GRID:
        _GRID[N] = np.mgrid[0:N, 0:N].astype(np.float32)
    return _GRID[N]


def _texture(N, corr_px, rng):
    """A smooth random field: coarse noise, bilinearly upsampled with two small matrix products (a cheap stand-in for
    a Gaussian filter)."""
    n = max(int(N / corr_px) + 2, 3)
    key = (N, n)
    if key not in _INTERP:
        t = np.linspace(0, n - 1, N)
        _INTERP[key] = np.maximum(1 - np.abs(t[:, None] - np.arange(n)[None, :]), 0).astype(np.float32)
    A = _INTERP[key]
    c = rng.standard_normal((n, n)).astype(np.float32)
    return A @ c @ A.T


_INTERP: dict = {}


def _render_powder(parts, N, px, base, rng):
    """SE image (counts) of the particles: height map -> tilt -> secant law, detector side, shadows, shot noise."""
    z = np.zeros((N, N), np.float32)
    yy, xx = _grid(N)
    for p in parts:
        R = p["R"]
        objs = []
        if p["irregular"]:
            objs.append(("irr", p["x"], p["y"], R, p))
        else:
            objs.append(("sph", p["x"], p["y"], R, R))
        for s in p["sats"]:
            dist = (R + 0.7 * s["r"]) * math.cos(s["el"])
            reach = R * (p.get("aspect", 1.0) ** 0.5 if p["irregular"] else 1.0)
            dist *= reach / R
            sx, sy = p["x"] + dist * math.cos(s["phi"]), p["y"] + dist * math.sin(s["phi"])
            zc = R + (R + 0.7 * s["r"]) * math.sin(s["el"])
            objs.append(("sph", sx, sy, s["r"], zc))
        for kind, cx, cy, r, extra in objs:
            ext = r * (2.5 if kind == "irr" else 1.0) + px
            i0, i1 = max(int((cy - ext) / px), 0), min(int((cy + ext) / px) + 2, N)
            j0, j1 = max(int((cx - ext) / px), 0), min(int((cx + ext) / px) + 2, N)
            if i0 >= i1 or j0 >= j1:
                continue
            X = (xx[i0:i1, j0:j1] + 0.5) * px - cx
            Y = (yy[i0:i1, j0:j1] + 0.5) * px - cy
            if kind == "sph":
                zc = extra
                rr2 = X * X + Y * Y
                h = np.where(rr2 < r * r, zc + np.sqrt(np.maximum(r * r - rr2, 0)), 0.0)
            else:
                pp = extra
                a = r * pp["aspect"] ** 0.5
                b = r / pp["aspect"] ** 0.5
                ca, sa = math.cos(pp["ang"]), math.sin(pp["ang"])
                u, v = (X * ca + Y * sa) / a, (-X * sa + Y * ca) / b
                th = np.arctan2(v, u)
                rb = 1.0 + sum(A * np.cos(k * th + ph) for k, A, ph in pp["modes"])
                rho2 = (u * u + v * v) / np.maximum(rb, 0.3) ** 2
                h = np.where(rho2 < 1, b * (1 + np.sqrt(np.maximum(1 - rho2, 0))), 0.0)
            sub = z[i0:i1, j0:j1]
            np.maximum(sub, h.astype(np.float32), out=sub)
    gy, gx = np.gradient(z, px)
    g2 = gx * gx + gy * gy
    sec = np.minimum(np.sqrt(1 + g2), 8.0)
    on = z > 0.05 * px
    # surface normal . detector direction (detector towards -x, 30 deg up)
    ndot = (gx * math.cos(DET_ELEV) + math.sin(DET_ELEV)) / np.sqrt(1 + g2)
    det = 0.55 + 0.9 * np.clip(ndot, 0, 1)
    # shadow: the line from a point towards the detector passes under a particle
    t = math.tan(SHADOW_ELEV) * px
    X = np.arange(N, dtype=np.float32)[None, :] * t
    u = z + X
    cm = np.maximum.accumulate(u, axis=1)
    prev = np.concatenate([np.full((N, 1), -1e9, np.float32), cm[:, :-1]], axis=1)
    shadow = (prev - X) > z + 0.5 * px
    tex = _texture(N, 6.0, rng) * 0.4
    y_mat = SE_YIELD[base] * sec ** 0.9 * det
    y_sub = SE_YIELD["tape"] * (1 + 0.15 * tex) * np.where(shadow, 0.7, 1.0)
    sig = np.where(on, y_mat * np.where(shadow, 0.85, 1.0), y_sub)
    sig = ndi.gaussian_filter(sig, 0.5)
    counts = rng.poisson(DOSE * sig).astype(np.float32)
    return counts, z


def _bg_threshold(sm, k=5.0):
    """Background (tape) level from the histogram's peak and its lower half-width; threshold k sigma above it, and
    at least a quarter above. (Otsu's split falls between the particle faces and their bright edges on SE images.)"""
    hi = float(np.percentile(sm, 99.5))
    lo = float(sm.min())
    h, e = np.histogram(sm, bins=200, range=(lo, hi))
    c = (e[:-1] + e[1:]) / 2
    hs = ndi.uniform_filter1d(h.astype(float), 3)
    i = int(np.argmax(hs))
    mode = float(c[i])
    half = hs[i] / 2
    lo_i = i
    while lo_i > 0 and hs[lo_i] > half:
        lo_i -= 1
    hi_i = i
    while hi_i < len(hs) - 1 and hs[hi_i] > half:
        hi_i += 1
    hw = max(min(i - lo_i, hi_i - i), 1) * (c[1] - c[0])           # the narrower half-width at half maximum
    sig = hw / 1.1774
    return mode + max(k * sig, 0.25 * mode)


def _fill_holes(mask):
    """Fill holes: background components that do not touch the border."""
    bl, nb = ndi.label(~mask)
    if nb == 0:
        return mask
    edge = np.unique(np.concatenate([bl[0], bl[-1], bl[:, 0], bl[:, -1]]))
    outside = np.zeros(nb + 1, bool)
    outside[edge] = True
    outside[0] = True
    return mask | ~outside[bl]


def _perim_area(lab, n):
    """Area and perimeter (crack-edge count x pi/4, unbiased for random boundary orientations) of labels 1..n."""
    area = np.bincount(lab.ravel(), minlength=n + 1).astype(float)
    per = np.zeros(n + 1)
    for a, b in ((lab[:, :-1], lab[:, 1:]), (lab[:-1, :], lab[1:, :])):
        d = a != b
        per += np.bincount(a[d], minlength=n + 1)[: n + 1]
        per += np.bincount(b[d], minlength=n + 1)[: n + 1]
    # edges on the image border count too
    for edge in (lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]):
        per += np.bincount(edge, minlength=n + 1)[: n + 1]
    return area, per * math.pi / 4


def _disk(r):
    r = max(int(r), 1)
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r + 0.5


def analyze_powder(img, px, campaign):
    """The lab's analysis of an SE powder image: threshold, split, measure. Returns (result, extras for figures)."""
    from skimage.segmentation import watershed
    sm = ndi.gaussian_filter(img, 1.0)
    thr = _bg_threshold(sm)
    mask = _fill_holes(sm > thr)
    mask = ndi.binary_opening(mask, structure=np.ones((3, 3), bool))
    dt = ndi.distance_transform_edt(mask)
    r_typ = max(2.0 * float(dt[mask].mean()) if mask.any() else 3.0, 3.0)    # mean DT ~ r/3 for discs (x2: robust)
    size = 2 * int(max(2, round(0.45 * r_typ))) + 1
    peaks = (dt == ndi.maximum_filter(dt, size=size)) & (dt >= max(2.0, 0.25 * r_typ))
    markers, nm = ndi.label(peaks, structure=np.ones((3, 3)))
    if nm == 0:
        return dict(sphericity=float("nan"), satellite_frac=0.0, d50_img_um=float("nan"), n_particles=0), {}
    lab = watershed(-dt, markers, mask=mask)
    n = int(lab.max())
    area, per = _perim_area(lab, n)
    border = np.zeros(n + 1, bool)
    for edge in (lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]):
        border[np.unique(edge)] = True
    border[0] = True
    keep = (~border) & (area >= 12)
    ids = np.nonzero(keep)[0]
    ecd = 2 * np.sqrt(area[ids] / math.pi) * px
    circ = np.clip(4 * math.pi * area[ids] / np.maximum(per[ids], 1e-9) ** 2, 0, 1)
    if len(ids) == 0:
        return dict(sphericity=float("nan"), satellite_frac=0.0, d50_img_um=float("nan"), n_particles=0), {}
    w = ecd ** 3
    o = np.argsort(ecd)
    cw = np.cumsum(w[o]) / w.sum()
    d50 = float(np.interp(0.5, cw, ecd[o]))
    # satellites: what a disk opening (about a fifth of the median particle radius) removes and is still attached
    r_med = float(np.median(ecd)) / px / 2
    ro = max(1, int(round(0.22 * r_med)))
    opened = ndi.binary_opening(mask, structure=_disk(ro))
    resid = mask & ~opened
    rl, nr = ndi.label(resid, structure=np.ones((3, 3)))
    sat_hosts = set()
    blobs = []
    if nr:
        ra = np.bincount(rl.ravel(), minlength=nr + 1)
        touch = ndi.binary_dilation(opened) & resid
        att = np.bincount(rl[touch], minlength=nr + 1) > 0
        host = ndi.maximum(lab, rl, index=np.arange(1, nr + 1))
        hmin = ndi.minimum(np.where(lab > 0, lab, 10 ** 9), rl, index=np.arange(1, nr + 1))
        amin, amax = max(3.0, 0.12 * ro * ro), math.pi * (2.2 * ro) ** 2
        for k in range(1, nr + 1):
            # a neck between two touching particles belongs to two labels: not a satellite
            if att[k] and amin <= ra[k] <= amax and host[k - 1] == hmin[k - 1]:
                h = int(host[k - 1])
                if h > 0 and keep[h] and area[h] > 4 * ra[k]:
                    sat_hosts.add(h)
                    blobs.append(k)
    big = ecd >= 2 * 2 * ro * px
    n_hosts = int(big.sum()) or len(ids)
    satf = len([h for h in sat_hosts if 2 * math.sqrt(area[h] / math.pi) >= 4 * ro]) / n_hosts
    res = dict(sphericity=float(np.mean(circ)), satellite_frac=float(satf), d50_img_um=d50, n_particles=int(len(ids)))
    ext = dict(labels=lab, mask=mask, keep_ids=ids, ecd_um=ecd, circularity=circ, sat_hosts=sorted(sat_hosts),
               sat_blobs=np.isin(rl, blobs) if blobs else np.zeros_like(mask), threshold=thr, open_r_px=ro)
    return res, ext


def _powder_fast(pop, campaign, rng):
    st = _powder_state(pop)
    c = micro.calib("sem_powder").get(campaign) or _POWDER_DEFAULT[campaign]
    f = np.array([1.0, st["irr"], st["sat"], math.log(st["dv50"] / 50.0)])
    d50 = st["dv50"] * math.exp(float(np.dot(c["d50_mu"], f)) + c["d50_sd"] * rng.standard_normal())
    sph = float(np.clip(np.dot(c["sph_mu"], f) + c["sph_sd"] * rng.standard_normal(), 0, 1))
    n_mean = math.exp(float(np.dot(c["n_mu"], f)))
    n = int(max(rng.poisson(n_mean), 0))
    sm = float(np.clip(np.dot(c["sat_mu"], f), 0, 1))
    sd = math.sqrt(max(sm * (1 - sm), 0.0) / max(n, 1)) * c["sat_k"] + c["sat_sd0"]
    sat = float(np.clip(sm + sd * rng.standard_normal(), 0, 1))
    return dict(sphericity=sph, satellite_frac=sat, d50_img_um=float(d50), n_particles=n)


# defaults until calibrate() has run (overwritten by calib_micro.json)
_POWDER_DEFAULT = {
    "flaime_al": dict(d50_mu=[-0.03, 0.05, 0.02, 0.0], d50_sd=0.08, sph_mu=[0.9, -0.25, -0.1, 0.0], sph_sd=0.015,
                      n_mu=[4.0, 0.0, 0.0, -2.0], sat_mu=[0.02, 0.15, 0.6, 0.0], sat_k=1.0, sat_sd0=0.01),
    "onr_cu": dict(d50_mu=[-0.03, 0.05, 0.02, 0.0], d50_sd=0.08, sph_mu=[0.9, -0.25, -0.1, 0.0], sph_sd=0.015,
                   n_mu=[4.0, 0.0, 0.0, -2.0], sat_mu=[0.02, 0.15, 0.6, 0.0], sat_k=1.0, sat_sd0=0.01),
}


def measure_powder(sample, campaign, rng, fidelity="fast", **kw):
    """SE image of the lot's sieved powder and its analysis: sphericity (mean circularity), satellite share,
    volume-weighted d50 of the imaged particles, particles analysed."""
    pop = micro.powder_population(sample, campaign)
    if fidelity == "fast":
        return _powder_fast(pop, campaign, rng)
    full = fidelity == "full"
    base = micro.base_of(campaign)
    px = POWDER_PX[campaign] * (1.0 if full else 2.0)
    N = kw.get("npx", NPX["full"] if full else NPX_POWDER_LITE)
    W = N * px
    parts = _draw_particles(pop, W, rng)
    img, z = _render_powder(parts, N, px, base, rng)
    res, ext = analyze_powder(img, px, campaign)
    if full:
        res["raw"] = dict(image=img, height_um=z, px_um=px, fov_um=W, particles=parts, **ext,
                          state=_powder_state(pop))
    return res


# =================================================================================================== section
def _lognormal(rng, med, gsd, n):
    return med * np.exp(math.log(gsd) * rng.standard_normal(n))


def _draw_pores(pm, W, H, rng, margin=150.0):
    """Pore sections in the W x H um field: per type, the pores whose extent along the plane's normal crosses it
    (number n_v x area x mean caliper), sizes size-biased by that caliper, cut at a uniform height."""
    out = []
    A = (W + 2 * margin) * (H + 2 * margin) * 1e-6                    # mm2
    for t, p in pm["pores"].items():
        nv = p.get("n_per_mm3", 0.0)
        if nv <= 0:
            continue
        s = math.log(p["gsd"])
        asp = p["aspect"] if t == "lof" else 1.0
        ext = asp ** (1 / 3)
        lam = nv * A * p["d_med_um"] * math.exp(s * s / 2) * 1e-3 * ext
        n = rng.poisson(lam)
        if n == 0:
            continue
        D = p["d_med_um"] * math.exp(s * s) * np.exp(s * rng.standard_normal(n))
        u = rng.random(n)
        sc = np.sqrt(1 - u * u)
        a = D / 2 * asp ** (1 / 3) * sc
        c = D / 2 * asp ** (-2 / 3) * sc
        x = rng.uniform(-margin, W + margin, n)
        z = rng.uniform(-margin, H + margin, n)
        ang = rng.normal(0, 0.25, n) if t == "lof" else np.zeros(n)
        if t == "lof":
            amp = p["irregularity"] * 0.45 * rng.standard_normal((n, 6)) / np.arange(2, 8) ** 0.9
            pha = rng.uniform(0, 2 * math.pi, (n, 6))
        for i in range(n):
            q = dict(type=t, x=float(x[i]), z=float(z[i]), a=float(a[i]), c=float(c[i]), ang=float(ang[i]),
                     irr=float(p["irregularity"]))
            if t == "lof":
                q["amp"], q["pha"] = amp[i], pha[i]
            out.append(q)
    return out


def _draw_cracks(pm, grain_um, W, H, rng, margin=150.0):
    """Hot-crack traces: count from the density (mm/mm2) and mean length, lengths lognormal, a tortuous path up
    the build direction in steps of about a grain width (assumed), opening lognormal about ``open_um``."""
    cr = pm["cracks"]
    dens = cr["density_mm_mm2"]
    if dens <= 1e-5:
        return []
    s = math.log(cr["len_gsd"])
    EL = cr["len_med_um"] * math.exp(s * s / 2)
    A = (W + 2 * margin) * (H + 2 * margin)
    n = rng.poisson(dens * 1e-3 * A / EL)
    if n == 0:
        return []
    L = _lognormal(rng, cr["len_med_um"], cr["len_gsd"], n)
    w = cr["open_um"] * np.exp(0.35 * rng.standard_normal(n))
    step = max(0.8 * grain_um, 8.0)
    out = []
    for i in range(n):
        k = max(int(math.ceil(L[i] / step)), 1)
        th = -math.pi / 2 + cr.get("tortuosity", 0.25) * rng.standard_normal(k)   # up the image (z decreasing)
        ds = L[i] / k
        x = np.concatenate([[rng.uniform(-margin, W + margin)], np.zeros(k)])
        z = np.concatenate([[rng.uniform(-margin, H + margin)], np.zeros(k)])
        x[1:] = x[0] + np.cumsum(ds * np.cos(th))
        z[1:] = z[0] + np.cumsum(ds * np.sin(th))
        out.append(dict(x=x, z=z, w=float(w[i]), L=float(L[i])))
    return out


def _visible_len(cr, W, H):
    xm, zm = (cr["x"][1:] + cr["x"][:-1]) / 2, (cr["z"][1:] + cr["z"][:-1]) / 2
    seg = np.hypot(np.diff(cr["x"]), np.diff(cr["z"]))
    inside = (xm >= 0) & (xm <= W) & (zm >= 0) & (zm <= H)
    return float(seg[inside].sum())


def _grf(shape, corr_px, rng):
    f = _texture(shape[0], max(2.5 * corr_px, 2.0), rng)
    return (f - f.mean()) / (f.std() + 1e-9)


def _render_section(pm, pores, cracks, N, px, rng):
    """BSE image (counts) of the polished section. Returns (counts, pore coverage, crack coverage)."""
    W = N * px
    phases = pm["phases"]
    eta_m = phases[0]["eta"]
    eta = np.full((N, N), eta_m, np.float32)
    gd = pm.get("grains", {}).get("d_um", 20.0)
    for ph in phases[1:]:
        f = ph["vol"]
        if f < 1e-3:
            continue
        d_eta = ph["eta"] - eta_m
        size = gd if ph["name"] == "beta'" else (ph.get("size_um") or 0.5)
        if size >= 1.5 * px:
            g = _grf((N, N), size / px / 2.0, rng)
            thr = np.quantile(g[::3, ::3], 1 - f)
            m = np.clip((g - thr) * 3.0 + 0.5, 0, 1)
            eta += d_eta * m
        else:
            sp = math.sqrt(f * (1 - f)) * min(size / px, 1.0)
            eta += d_eta * np.clip(f + sp * rng.standard_normal((N, N)).astype(np.float32), 0, 1)
    yy, xx = _grid(N)
    cov_p = np.zeros((N, N), np.float32)
    for p in pores:
        R = max(p["a"], p["c"]) * (1 + 1.5 * p["irr"]) + px
        i0, i1 = max(int((p["z"] - R) / px), 0), min(int((p["z"] + R) / px) + 2, N)
        j0, j1 = max(int((p["x"] - R) / px), 0), min(int((p["x"] + R) / px) + 2, N)
        if i0 >= i1 or j0 >= j1:
            continue
        X = (xx[i0:i1, j0:j1] + 0.5) * px - p["x"]
        Z = (yy[i0:i1, j0:j1] + 0.5) * px - p["z"]
        ca, sa = math.cos(p["ang"]), math.sin(p["ang"])
        u, v = X * ca + Z * sa, -X * sa + Z * ca
        rho = np.sqrt((u / p["a"]) ** 2 + (v / p["c"]) ** 2)
        th = np.arctan2(v / p["c"], u / p["a"])
        if p["type"] == "lof":
            rb = 1.0 + sum(p["amp"][k - 2] * np.cos(k * th + p["pha"][k - 2]) for k in range(2, 8))
            rb = np.maximum(rb, 0.25)
        else:
            rb = 1.0
        # radial distance to the boundary in um, for a one-pixel antialiased edge
        scale = np.sqrt((p["a"] * np.cos(th)) ** 2 + (p["c"] * np.sin(th)) ** 2)
        dist = (rho - rb) * scale
        cov = np.clip(0.5 - dist / px, 0, 1).astype(np.float32)
        sub = cov_p[i0:i1, j0:j1]
        np.maximum(sub, cov, out=sub)
    cov_c = np.zeros((N, N), np.float32)
    for cr in cracks:
        w = cr["w"]
        for k in range(len(cr["x"]) - 1):
            x0, z0, x1, z1 = cr["x"][k], cr["z"][k], cr["x"][k + 1], cr["z"][k + 1]
            i0 = max(int((min(z0, z1) - w - px) / px), 0)
            i1 = min(int((max(z0, z1) + w + px) / px) + 2, N)
            j0 = max(int((min(x0, x1) - w - px) / px), 0)
            j1 = min(int((max(x0, x1) + w + px) / px) + 2, N)
            if i0 >= i1 or j0 >= j1:
                continue
            X = (xx[i0:i1, j0:j1] + 0.5) * px
            Z = (yy[i0:i1, j0:j1] + 0.5) * px
            dx, dz = x1 - x0, z1 - z0
            L2 = dx * dx + dz * dz + 1e-12
            t = np.clip(((X - x0) * dx + (Z - z0) * dz) / L2, 0, 1)
            d = np.hypot(X - x0 - t * dx, Z - z0 - t * dz)
            cov = np.clip((w + px) / 2 - d, 0, min(w, px)) / px
            sub = cov_c[i0:i1, j0:j1]
            np.maximum(sub, cov.astype(np.float32), out=sub)
    cov = 1 - (1 - cov_p) * (1 - cov_c)
    img = eta * (1 - cov) + 0.12 * eta_m * cov
    # polishing scratches: a few long faint grooves (assumed 2 per mm2, 2-5 % darker, 1 um wide)
    ns = rng.poisson(2.0 * (W * 1e-3) ** 2)
    for _ in range(ns):
        ang = rng.uniform(0, math.pi)
        x0, z0 = rng.uniform(0, W), rng.uniform(0, W)
        d = np.abs((xx + 0.5) * px - x0) * math.sin(ang) - ((yy + 0.5) * px - z0) * math.cos(ang)
        d = np.abs(d)
        img = img * (1 - rng.uniform(0.02, 0.05) * np.clip((1.0 + px) / 2 - d, 0, min(1.0, px)) / px)
    counts = rng.poisson(BSE_DOSE * BSE_COLLECT * np.maximum(img, 0)).astype(np.float32)
    return counts, cov_p, cov_c


def _shape_stats(lab, n):
    """Area, perimeter, elongation (major/minor from second moments), mean width (area/major) and circularity of
    labels 1..n (vectorized with bincount)."""
    area, per = _perim_area(lab, n)
    yy, xx = _grid(lab.shape[0]) if lab.shape[0] == lab.shape[1] else np.indices(lab.shape).astype(np.float32)
    lr = lab.ravel()
    sx = np.bincount(lr, xx.ravel(), n + 1)
    sy = np.bincount(lr, yy.ravel(), n + 1)
    sxx = np.bincount(lr, (xx * xx).ravel(), n + 1)
    syy = np.bincount(lr, (yy * yy).ravel(), n + 1)
    sxy = np.bincount(lr, (xx * yy).ravel(), n + 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.maximum(area, 1)
        mx, my = sx / a, sy / a
        cxx = sxx / a - mx * mx + 1 / 12
        cyy = syy / a - my * my + 1 / 12
        cxy = sxy / a - mx * my
        tr, det = cxx + cyy, cxx * cyy - cxy * cxy
        disc = np.sqrt(np.maximum(tr * tr / 4 - det, 0))
        l1, l2 = tr / 2 + disc, np.maximum(tr / 2 - disc, 1 / 12)
        major, minor = 4 * np.sqrt(l1), 4 * np.sqrt(l2)
        elong = major / minor
        width = area / np.maximum(major, 1)
        circ = np.clip(4 * math.pi * area / np.maximum(per, 1e-9) ** 2, 0, 1)
    return area, elong, width, major, circ, mx, my


def analyze_section(img, px):
    """The lab's analysis of a BSE section: pores and cracks, their sizes, shapes and lengths."""
    N = img.shape[0]
    sm = ndi.gaussian_filter(img, 0.8)
    level = float(np.median(sm[::2, ::2]))
    pore = sm < 0.5 * level
    # thin dark features: smoothed along the build direction (where hot cracks run), black top-hat across it, against
    # the shot noise of the matrix level (counts are Poisson) after that smoothing (1 / sqrt(4 pi sx sy))
    smv = ndi.gaussian_filter(img, (2.0, 0.6))
    bth = ndi.grey_closing(smv, size=(1, 5)) - smv
    sig = math.sqrt(max(level, 1.0)) / math.sqrt(4 * math.pi * 2.0 * 0.6)
    thin = bth > max(4.5 * sig, 0.06 * level)
    s8 = np.ones((3, 3))
    # 1. cracks: elongated thin components of the dark mask
    labd, nd = ndi.label(pore | thin, structure=s8)
    crackmask = np.zeros_like(pore)
    if nd:
        area_d, el_d, w_d, maj_d, _, _, _ = _shape_stats(labd, nd)
        crack_like = (el_d >= 4.0) & (w_d <= 3.5) & (maj_d >= 6)
        crack_like[0] = False
        crackmask = crack_like[labd]
    # 2. pores: the threshold mask outside the cracks
    labp, npo = ndi.label(pore & ~crackmask, structure=s8)
    cls = np.zeros(npo + 1, int)             # 0 dropped, 1 round, 2 lack of fusion
    if npo:
        area, elong, width, major, circ, mx, my = _shape_stats(labp, npo)
        keep = area >= 2
        keep[0] = False
        cls[keep] = 1
        cls[keep & (area >= 12) & ((circ < 0.55) | (elong > 2.2))] = 2
    else:
        area = np.zeros(1)
    a_pore = float(area[cls > 0].sum())
    a_crack = float(crackmask.sum())
    porosity = (a_pore + a_crack) / (N * N)
    ecd = 2 * np.sqrt(area / math.pi) * px
    dmax = float(ecd[cls > 0].max()) if np.any(cls > 0) else 0.0
    L = 0.0
    if a_crack > 0:
        from skimage.morphology import skeletonize
        sk = skeletonize(crackmask)
        h = sk[:, :-1] & sk[:, 1:]
        v = sk[:-1, :] & sk[1:, :]
        d1 = sk[:-1, :-1] & sk[1:, 1:] & ~(sk[:-1, 1:] | sk[1:, :-1])
        d2 = sk[:-1, 1:] & sk[1:, :-1] & ~(sk[:-1, :-1] | sk[1:, 1:])
        nseg = ndi.label(sk, structure=s8)[1]
        L = (h.sum() + v.sum() + math.sqrt(2) * (d1.sum() + d2.sum()) + nseg) * px      # + one pixel per trace
    A_mm2 = (N * px * 1e-3) ** 2
    lof = float(area[cls == 2].sum() / a_pore) if a_pore > 0 else 0.0
    res = dict(porosity=float(porosity), pore_dmax_um=dmax, crack_density=float(L * 1e-3 / A_mm2), lof_frac=lof,
               n_pores=int(np.sum(cls > 0)), n_cracks=int(ndi.label(crackmask, structure=s8)[1]) if a_crack else 0)
    ext = dict(labels=labp, cls=cls, area_px=area, ecd_um=ecd, crack_mask=crackmask, level=level, sigma=sig,
               crack_len_um=L)
    return res, ext


U_EDGES = [0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.5, 7.5, 10.0, 14.0, 20.0, 30.0, 50.0, 1e9]
_NB = len(U_EDGES) - 1
# transfer tables by true class (row 0 round, row 1 lack of fusion) and section diameter in pixels u (bins U_EDGES):
# detection probability, median measured/true area, log-sd, probability of being called lack of fusion. Defaults
# until calibrate() runs.
_SECTION_DEFAULT = dict(
    u_edges=U_EDGES, p_det=[[0, .05, .3, .6, .8, .9, .95, 1, 1, 1, 1, 1, 1, 1]] * 2,
    g_med=[[1.0] * _NB] * 2, g_sd=[[0.15] * _NB] * 2,
    p_lof=[[0, 0, 0, 0, 0, 0, .02, .05, .03, .01, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, .1, .3, .6, .8, .85, .9, .95, 1]],
    crack_v0=0.35, crack_w=0.25, crack_lbias=1.0, crack_lsd=0.15, crack_area_um=5.0, crack_min_um=24.0,
    crack_false_p=0.0, crack_fp_um=30.0, n_lite=256, px_lite=4.0)


def _section_fast(pm, campaign, rng):
    """The same stereological sampler as the image, then the lite chain's measured transfer functions."""
    c = dict(_SECTION_DEFAULT)
    c.update(micro.calib("sem_section"))
    N, px = int(c["n_lite"]), float(c["px_lite"])
    W = N * px
    A_um2 = W * W
    pores = _draw_pores(pm, W, W, rng)
    area_d, lofs, ecds = np.zeros(0), np.zeros(0, bool), np.zeros(0)
    if pores:
        a = np.array([p["a"] for p in pores])
        cc = np.array([p["c"] for p in pores])
        x = np.array([p["x"] for p in pores])
        z = np.array([p["z"] for p in pores])
        is_lof = np.array([p["type"] == "lof" for p in pores])
        area = math.pi * a * cc
        u = 2 * np.sqrt(area / math.pi) / px
        # field-edge truncation by the bounding-box overlap
        fx = np.clip((np.minimum(x + a, W) - np.maximum(x - a, 0)) / (2 * a), 0, 1)
        fz = np.clip((np.minimum(z + cc, W) - np.maximum(z - cc, 0)) / (2 * cc), 0, 1)
        vis = fx * fz
        k = np.clip(np.searchsorted(c["u_edges"], u, side="right") - 1, 0, _NB - 1)
        row = is_lof.astype(int)
        pdet = np.asarray(c["p_det"])[row, k]
        det = (rng.random(len(u)) < pdet) & (vis > 0)
        g = np.asarray(c["g_med"])[row, k] * np.exp(np.asarray(c["g_sd"])[row, k] * rng.standard_normal(len(u)))
        am = area * vis * g
        lofc = rng.random(len(u)) < np.asarray(c["p_lof"])[row, k]
        area_d, lofs = am[det], lofc[det]
        ecds = 2 * np.sqrt(area_d / math.pi)
    a_pore = float(np.sum(area_d))
    cracks = _draw_cracks(pm, pm.get("grains", {}).get("d_um", 10.0), W, W, rng)
    Lm = 0.0
    for cr in cracks:
        Lv = _visible_len(cr, W, W)
        if Lv <= 0:
            continue
        v = cr["w"] / px
        r = 1 / (1 + math.exp(-(math.log(max(v, 1e-3)) - math.log(c["crack_v0"])) / c["crack_w"]))
        Lm += Lv * r * c["crack_lbias"] * math.exp(c["crack_lsd"] * rng.standard_normal())
    if c["crack_false_p"] > 0 and rng.random() < c["crack_false_p"]:       # scratches, pore chains read as cracks
        Lm += c.get("crack_fp_um", 30.0) * math.exp(0.3 * rng.standard_normal())
    if Lm < c["crack_min_um"]:
        Lm = 0.0
    a_crack = Lm * c["crack_area_um"]
    por = (a_pore + a_crack) / A_um2
    return dict(porosity=float(por), pore_dmax_um=float(np.max(ecds)) if len(ecds) else 0.0,
                crack_density=float(Lm * 1e-3 / (A_um2 * 1e-6)),
                lof_frac=float(np.sum(area_d[lofs]) / a_pore) if a_pore > 0 else 0.0,
                n_pores=int(len(ecds)), n_cracks=int(Lm > 0))


def measure_section(sample, campaign, rng, fidelity="fast", **kw):
    """BSE image of a polished vertical section of the part and its analysis: porosity (area fraction of pores and
    cracks), largest pore's equivalent diameter, crack length per area (mm/mm2; 0 when none is found), and the share
    of the pore area that is lack of fusion by shape."""
    pm = micro.phase_model(sample, campaign, "part")
    if fidelity == "fast":
        return _section_fast(pm, campaign, rng)
    full = fidelity == "full"
    px = kw.get("px_um", SECTION_PX["full" if full else "lite"])
    N = kw.get("npx", NPX["full" if full else "lite"])
    W = N * px
    pores = _draw_pores(pm, W, W, rng)
    cracks = _draw_cracks(pm, pm.get("grains", {}).get("d_um", 10.0), W, W, rng)
    img, cov_p, cov_c = _render_section(pm, pores, cracks, N, px, rng)
    res, ext = analyze_section(img, px)
    if full or kw.get("keep_raw"):
        res["raw"] = dict(image=img, pore_cov=cov_p, crack_cov=cov_c, px_um=px, fov_um=W, pores=pores,
                          cracks=cracks, **ext)
    return res


# =================================================================================================== calibration
def _fit_ls(X, y, w=None):
    X, y = np.asarray(X, float), np.asarray(y, float)
    if w is not None:
        sw = np.sqrt(np.asarray(w, float))
        X, y = X * sw[:, None], y * sw
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def _logit_fit(x, yb, x0=0.0):
    """1-D logistic regression P(y) = 1/(1+exp(-(a + b (x - x0)))) by Newton's method."""
    x, yb = np.asarray(x, float) - x0, np.asarray(yb, float)
    a, b = 0.0, 1.0
    for _ in range(50):
        p = 1 / (1 + np.exp(-(a + b * x)))
        g = np.array([np.sum(yb - p), np.sum((yb - p) * x)])
        wv = p * (1 - p) + 1e-9
        H = np.array([[wv.sum(), (wv * x).sum()], [(wv * x).sum(), (wv * x * x).sum()]]) + 1e-6 * np.eye(2)
        step = np.linalg.solve(H, g)
        a, b = a + step[0], b + step[1]
        if np.abs(step).max() < 1e-6:
            break
    return float(a), float(b)


def calibrate(n=24, reps=6, seed=0, verbose=True):
    """Run the lite chain over representative lots and parts of both campaigns and fit the fast mode."""
    import time
    out = {"sem_powder": {}, "sem_section": {}}
    gal = micro.gallery_samples()
    rng = np.random.default_rng(seed)
    # ---------------- powder
    for camp in ("flaime_al", "onr_cu"):
        pairs = micro.random_samples(camp, n, seed=seed + 3) + list(gal[camp].values())
        F, Y = [], []
        t0 = time.time()
        for lot, _ in pairs:
            pop = micro.powder_population(lot, camp)
            st = _powder_state(pop)
            f = [1.0, st["irr"], st["sat"], math.log(st["dv50"] / 50.0)]
            for _ in range(reps):
                r = measure_powder(lot, camp, rng, fidelity="lite")
                if not np.isfinite(r["d50_img_um"]) or r["n_particles"] < 3:
                    continue
                F.append(f)
                Y.append([math.log(r["d50_img_um"] / st["dv50"]), r["sphericity"], r["satellite_frac"],
                          math.log(max(r["n_particles"], 1))])
        F, Y = np.array(F), np.array(Y)
        bd = _fit_ls(F, Y[:, 0])
        bs = _fit_ls(F, Y[:, 1])
        bt = _fit_ls(F, Y[:, 2])
        bn = _fit_ls(F, Y[:, 3])
        rd = Y[:, 0] - F @ bd
        rs = Y[:, 1] - F @ bs
        rt = Y[:, 2] - F @ bt
        sm = np.clip(F @ bt, 0, 1)
        nn = np.exp(Y[:, 3])
        binom = np.sqrt(np.maximum(sm * (1 - sm), 1e-6) / nn)
        k = float(np.sqrt(np.mean(rt ** 2) / np.mean(binom ** 2)))
        out["sem_powder"][camp] = dict(d50_mu=bd.round(5).tolist(), d50_sd=float(rd.std()),
                                       sph_mu=bs.round(5).tolist(), sph_sd=float(rs.std()),
                                       n_mu=bn.round(5).tolist(), sat_mu=bt.round(5).tolist(),
                                       sat_k=round(min(max(k, 0.3), 3.0), 4), sat_sd0=0.003,
                                       n_obs=int(len(Y)), features="1, irregular, satellite, ln(dv50/50)")
        if verbose:
            print(f"powder {camp}: {len(Y)} images in {time.time() - t0:.1f} s; d50 bias {bd.round(3)}, sd "
                  f"{rd.std():.3f}; sph {bs.round(3)} sd {rs.std():.3f}; sat {bt.round(3)}, k {k:.2f}", flush=True)
    # ---------------- section: object-level matching of the lite chain
    N, px = NPX["lite"], SECTION_PX["lite"]
    W = N * px
    rec, crk, fp, lrat = [], [], [], []
    t0 = time.time()
    for camp in ("flaime_al", "onr_cu"):
        pairs = micro.random_samples(camp, n, seed=seed + 5) + list(gal[camp].values())
        for _, part in pairs:
            pm = micro.phase_model(part, camp, "part")
            for _ in range(reps):
                pores = _draw_pores(pm, W, W, rng)
                cracks = _draw_cracks(pm, pm["grains"]["d_um"], W, W, rng)
                img, cov_p, cov_c = _render_section(pm, pores, cracks, N, px, rng)
                res, ext = analyze_section(img, px)
                lab, cls, area = ext["labels"], ext["cls"], ext["area_px"]
                tmp, cnt = [], {}
                for p in pores:
                    if not (0 < p["x"] < W and 0 < p["z"] < W):
                        continue
                    inside = (p["x"] - p["a"] > px) and (p["x"] + p["a"] < W - px) and (p["z"] - p["c"] > px) \
                        and (p["z"] + p["c"] < W - px)
                    i, j = min(int(p["z"] / px), N - 1), min(int(p["x"] / px), N - 1)
                    l = int(lab[i, j])
                    if l == 0 or cls[l] == 0:
                        win = lab[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2]
                        l = int(win.max()) if win.max() > 0 and cls[int(win.max())] > 0 else 0
                    ar = math.pi * p["a"] * p["c"]
                    tmp.append((p["type"] == "lof", 2 * math.sqrt(ar / math.pi) / px, l, ar, inside))
                    if l:
                        cnt[l] = cnt.get(l, 0) + 1
                for lof_, u_, l, ar, inside in tmp:
                    if l == 0:
                        rec.append((lof_, u_, 0, np.nan, 0))
                    elif cnt[l] == 1 and inside:
                        rec.append((lof_, u_, 1, float(area[l]) * px * px / ar, int(cls[l] == 2)))
                    else:          # cut by the field edge or merged: counts for detection and classification only
                        rec.append((lof_, u_, 1, np.nan, int(cls[l] == 2)))
                Lm = ext["crack_len_um"]
                if cracks:
                    # per-crack recovery: share of the trace's points that fall on detected crack pixels
                    dm = ndi.binary_dilation(ext["crack_mask"], iterations=1)
                    rl = 0.0
                    for cr in cracks:
                        tt = np.linspace(0, 1, 60)
                        xs = np.interp(tt * (len(cr["x"]) - 1), np.arange(len(cr["x"])), cr["x"])
                        zs = np.interp(tt * (len(cr["z"]) - 1), np.arange(len(cr["z"])), cr["z"])
                        ok = (xs > 0) & (xs < W) & (zs > 0) & (zs < W)
                        if ok.sum() < 3:
                            continue
                        hit = dm[(zs[ok] / px).astype(int), (xs[ok] / px).astype(int)]
                        Lv = _visible_len(cr, W, W)
                        crk.append([cr["w"] / px, float(hit.mean()), Lv])
                        rl += float(hit.mean()) * Lv
                    if rl > 0 and Lm > 0:
                        lrat.append(Lm / rl)
                else:
                    fp.append(Lm)
    R = np.array(rec, float)
    edges = np.array(U_EDGES)
    tabs = {k: np.zeros((2, _NB)) for k in ("p_det", "g_med", "g_sd", "p_lof")}
    cnts = np.zeros((2, _NB), int)
    for row in (0, 1):
        for k in range(_NB):
            m = (R[:, 0] == row) & (R[:, 1] >= edges[k]) & (R[:, 1] < edges[k + 1])
            cnts[row, k] = int(m.sum())
            if m.sum() < 5:                      # too few to estimate: filled below
                for key in tabs:
                    tabs[key][row, k] = np.nan
                continue
            tabs["p_det"][row, k] = R[m, 2].mean()
            d = m & (R[:, 2] > 0) & np.isfinite(R[:, 3])
            da = m & (R[:, 2] > 0)
            if d.sum() >= 5:
                lr = np.log(np.maximum(R[d, 3], 1e-3))
                tabs["g_med"][row, k] = float(np.exp(np.median(lr)))
                tabs["g_sd"][row, k] = float(1.4826 * np.median(np.abs(lr - np.median(lr))))
            else:
                tabs["g_med"][row, k] = tabs["g_sd"][row, k] = np.nan
            tabs["p_lof"][row, k] = float(R[da, 4].mean()) if da.sum() >= 5 else np.nan
    # fill bins with too few pores: detection and area transfer are about size, so from the other class first;
    # the lack-of-fusion call is about the class, so from the neighbouring bins first
    def _fill_nb(T, row):
        for k in list(range(_NB)) + list(range(_NB - 1, -1, -1)):
            if not np.isfinite(T[row, k]):
                nb = [T[row, j] for j in (k - 1, k + 1) if 0 <= j < _NB and np.isfinite(T[row, j])]
                if nb:
                    T[row, k] = nb[0]

    for key in tabs:
        T = tabs[key]
        if key == "p_lof":
            for row in (0, 1):
                _fill_nb(T, row)
        for row in (0, 1):
            bad = ~np.isfinite(T[row])
            T[row, bad] = T[1 - row, bad]
        for row in (0, 1):
            _fill_nb(T, row)
        T[~np.isfinite(T)] = {"p_det": 1.0, "g_med": 1.0, "g_sd": 0.15, "p_lof": 0.0}[key]
    C = np.array(crk, float) if crk else np.zeros((0, 3))
    if len(C) > 10:
        a_c, b_c = _logit_fit(np.log(np.maximum(C[:, 0], 1e-3)), C[:, 1])      # recovered share of each trace
        crack_w = 1.0 / max(b_c, 1e-3)
        crack_v0 = math.exp(-a_c / max(b_c, 1e-3))
    else:
        crack_v0, crack_w = 0.35, 0.25
    lb = np.array(lrat) if lrat else np.array([1.0])
    fpa = np.array(fp) if fp else np.zeros(1)
    out["sem_section"] = dict(u_edges=U_EDGES, **{k: np.round(v, 4).tolist() for k, v in tabs.items()},
                              bin_counts=cnts.tolist(), crack_v0=round(crack_v0, 4), crack_w=round(crack_w, 4),
                              crack_lbias=round(float(np.median(lb)), 4),
                              crack_lsd=round(float(1.4826 * np.median(np.abs(np.log(lb) - np.median(np.log(lb))))), 4),
                              crack_area_um=round(_crack_area_um(rng), 3), crack_min_um=24.0,
                              crack_false_p=round(float(np.mean(fpa > 0)), 4),
                              crack_fp_um=round(float(np.median(fpa[fpa > 0])) if np.any(fpa > 0) else 30.0, 2),
                              n_lite=N, px_lite=px, n_pores_matched=int(len(R)), n_cracks_matched=int(len(C)))
    if verbose:
        print(f"section: {len(R)} pores, {len(C)} cracks matched in {time.time() - t0:.1f} s", flush=True)
        for key in ("p_det", "g_med", "p_lof"):
            print("  ", key, np.round(tabs[key], 2).tolist(), flush=True)
        print("  cracks", {k: out["sem_section"][k] for k in ("crack_v0", "crack_w", "crack_lbias", "crack_lsd",
                                                             "crack_area_um", "crack_false_p", "crack_fp_um")})
    return out


def _crack_area_um(rng):
    """Area per unit crack length the lite analysis attributes to a crack (um), from a synthetic field of cracks."""
    pm = dict(phases=[dict(eta=0.153, vol=1.0, name="fcc")], pores={},
              cracks=dict(density_mm_mm2=2.0, len_med_um=150.0, len_gsd=1.5, open_um=1.5, tortuosity=0.25),
              grains=dict(d_um=10.0))
    N, px = NPX["lite"], SECTION_PX["lite"]
    ratios = []
    for _ in range(4):
        cracks = _draw_cracks(pm, 10.0, N * px, N * px, rng)
        img, _, _ = _render_section(pm, [], cracks, N, px, rng)
        res, ext = analyze_section(img, px)
        if res["crack_density"] > 0:
            L = res["crack_density"] * (N * px * 1e-3) ** 2 * 1e3
            a = float(ext["crack_mask"].sum()) * px * px
            ratios.append(a / L)
    return float(np.median(ratios)) if ratios else 3.0


# =================================================================================================== figures
def gallery(outdir, samples=None):
    """outdir/sem_powder.png and outdir/sem_section.png for the gallery alloys (full fidelity)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    samples = samples or micro.gallery_samples()
    items = [(c, a, lp) for c, d in samples.items() for a, lp in d.items()]
    # ---- powder
    fig, axes = plt.subplots(2, len(items), figsize=(3.6 * len(items), 7.4))
    for k, (camp, alloy, (lot, part)) in enumerate(items):
        rng = np.random.default_rng(100 + k)
        r = measure_powder(lot, camp, rng, fidelity="full")
        raw = r["raw"]
        img = raw["image"]
        ax = axes[0, k]
        ax.imshow(img, cmap="gray", vmin=0, vmax=np.percentile(img, 99.5))
        ax.set_title(f"{alloy}\nSE, {raw['px_um']:.0f} um/px, {raw['fov_um'] / 1000:.2f} mm field", fontsize=9)
        ax.axis("off")
        ax = axes[1, k]
        lab = raw["labels"]
        keep = np.zeros(lab.max() + 1, bool)
        keep[raw["keep_ids"]] = True
        col = np.random.default_rng(1).random((lab.max() + 1, 3)) * 0.7 + 0.3
        col[0] = 0
        rgb = col[lab] * keep[lab][..., None] + 0.25 * (~keep[lab])[..., None] * (lab > 0)[..., None]
        ax.imshow(rgb)
        sb = raw["sat_blobs"]
        if np.any(sb):
            yy, xx = np.nonzero(sb)
            ax.scatter(xx, yy, s=0.5, c="red", marker="s", linewidths=0)
        st = raw["state"]
        ax.set_title(f"watershed: n={r['n_particles']}, d50_img={r['d50_img_um']:.1f} um (cut dv50 {st['dv50']:.1f})\n"
                     f"sphericity {r['sphericity']:.3f}; satellites {r['satellite_frac']:.2f} (true {st['sat']:.2f}),"
                     f" irregular {st['irr']:.2f}", fontsize=7.5)
        ax.axis("off")
    fig.suptitle("SEM powder: secondary-electron images (top) and segmentation (bottom; grey = excluded at the "
                 "border, red = satellites found)", fontsize=10)
    fig.tight_layout()
    fig.savefig(outdir / "sem_powder.png", dpi=110)
    plt.close(fig)
    # ---- section
    fig, axes = plt.subplots(2, len(items), figsize=(3.6 * len(items), 7.4))
    for k, (camp, alloy, (lot, part)) in enumerate(items):
        rng = np.random.default_rng(200 + k)
        r = measure_section(part, camp, rng, fidelity="full")
        raw = r["raw"]
        img = raw["image"]
        ax = axes[0, k]
        ax.imshow(img, cmap="gray", vmin=0, vmax=np.percentile(img, 99.7))
        ax.set_title(f"{alloy}\nBSE, {raw['px_um']:.0f} um/px, {raw['fov_um'] / 1000:.1f} mm field, BD up",
                     fontsize=9)
        ax.axis("off")
        ax = axes[1, k]
        cls = raw["cls"][raw["labels"]]
        rgb = np.ones(img.shape + (3,)) * 0.93
        rgb[cls == 1] = (0.15, 0.45, 0.85)
        rgb[cls == 2] = (0.9, 0.55, 0.1)
        rgb[ndi.binary_dilation(raw["crack_mask"])] = (0.8, 0.1, 0.1)
        ax.imshow(rgb)
        pz = part.get("pores", {})
        ax.set_title(f"porosity {100 * r['porosity']:.2f} % (true {100 * part['porosity']:.2f}); dmax "
                     f"{r['pore_dmax_um']:.0f} um\ncracks {r['crack_density']:.2f} mm/mm2 (true "
                     f"{part['crack_density']:.2f}); LoF share {r['lof_frac']:.2f} (true "
                     f"{pz.get('lof', 0) / max(sum(v for kk, v in pz.items() if kk != 'crack'), 1e-9):.2f})",
                     fontsize=7.5)
        ax.axis("off")
    fig.suptitle("SEM section: backscattered-electron images (top) and analysis (bottom: blue round pores, orange "
                 "lack of fusion, red cracks)", fontsize=10)
    fig.tight_layout()
    fig.savefig(outdir / "sem_section.png", dpi=110)
    plt.close(fig)


def _icon(img, path, crop=None):
    from PIL import Image
    a = np.asarray(img, float)
    if crop:
        a = a[crop]
    lo, hi = np.percentile(a, 1), np.percentile(a, 99.5)
    g = np.clip((a - lo) / (hi - lo + 1e-9), 0, 1)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((512, 512), Image.LANCZOS)
    g = np.asarray(im, float) / 255
    yy, xx = np.mgrid[0:512, 0:512]
    r = np.hypot(xx - 255.5, yy - 255.5) / 256
    alpha = np.clip((1.0 - r) / 0.06, 0, 1)                  # circular mask with a soft edge
    rgba = np.zeros((512, 512, 4), np.uint8)
    rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = (40 + 215 * g).astype(np.uint8)
    rgba[..., 3] = (alpha * 255).astype(np.uint8)
    ring = (r > 0.955) & (r < 0.995)
    rgba[ring, :3] = 60
    Image.fromarray(rgba, "RGBA").save(path)


def thumbnail_powder(path, samples=None):
    samples = samples or micro.gallery_samples()
    lot, _ = samples["flaime_al"]["AlSi10Mg"]
    pop = micro.powder_population(lot, "flaime_al")
    pop = dict(pop, satellite_frac=0.35)
    rng = np.random.default_rng(7)
    N, px = 384, 0.6
    parts = _draw_particles(pop, N * px, rng)
    img, _ = _render_powder(parts, N, px, "Al", rng)
    _icon(ndi.gaussian_filter(img, 0.6), path)


def thumbnail_section(path, samples=None):
    samples = samples or micro.gallery_samples()
    _, part = samples["flaime_al"]["7075"]
    pm = micro.phase_model(part, "flaime_al", "part")
    pm = dict(pm, pores={k: dict(v, vol_frac=v["vol_frac"] * 6, n_per_mm3=v["n_per_mm3"] * 6)
                         for k, v in pm["pores"].items()})
    pm["pores"]["lof"] = dict(pm["pores"]["lof"], n_per_mm3=max(pm["pores"]["lof"]["n_per_mm3"], 1.0) * 30)
    rng = np.random.default_rng(11)
    N, px = 384, 1.5
    pores = _draw_pores(pm, N * px, N * px, rng)
    cracks = _draw_cracks(dict(pm, cracks=dict(pm["cracks"], open_um=4.0)), 10.0, N * px, N * px, rng)
    img, _, _ = _render_section(pm, pores, cracks, N, px, rng)
    _icon(ndi.gaussian_filter(img, 0.7), path)


if __name__ == "__main__":
    import sys
    cal = calibrate(n=int(sys.argv[1]) if len(sys.argv) > 1 else 24, reps=int(sys.argv[2]) if len(sys.argv) > 2 else 6)
    for key, val in cal.items():
        micro.calib_write(key, val)
    print("written", list(cal))

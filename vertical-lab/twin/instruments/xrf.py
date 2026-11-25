"""ED-XRF (Bruker S2 PUMA: Pd-anode tube, 50 W, SDD, helium flush): composition of a loose-powder lot in a cup, or of
a part's flat face.

Forward model, per measurement condition (assumed method, as S2 PUMA "SMART-QUANT"-type FP methods are set up):
light (12 kV, 4 mA, no filter, He: Mg, Al, Si), mid (30 kV, 1.6 mA, 100 um Al filter: Sc-Zn K, Ce and Er L) and
heavy (50 kV, 1 mA, 250 um Cu filter: Zr, Nb, Sn K), 100 s live each:

* **Tube spectrum**: Kramers continuum of the Pd anode through a 75 um Be window plus Pd L and K lines, through the
  filter (assumed shape).
* **Primary fluorescence**, the fundamental-parameter integral (Sherman, Spectrochim. Acta 7, 1955):
  I_i = G C_i omega_i p (1 - 1/r_i) Int N0(E) mu_i(E) / (mu_s(E)/sin psi1 + mu_s(E_i)/sin psi2) dE, psi = 45 deg; MACs,
  edges, jump ratios and line energies shared with twin/instruments/eds.py (Bearden 1967, Krause 1979; K lines of
  Zr, Nb, Sn added); secondary fluorescence from the other elements' lines (simplified Shiraiwa-Fujino form, assumed).
* **Path**: He flush with a residual-air fraction that varies run to run (0.3-2 %, assumed) and a 4 um prolene film
  under loose powder; Li has no usable line (invisible). Light elements are therefore poor: low yield, absorbed by
  film and path, and only the top few um of the powder speak for them.
* **Loose powder**: the surface roughness of a bed of particles much larger than a line's information depth lowers
  that line's intensity (particle-size effect, up to 15 %, assumed), and elements concentrated in coarse second phases
  are seen through a heterogeneity factor (1 - e^-D)/D with D the phase's absorption contrast times its size
  (mineralogical effect; Claisse & Samson, Adv. X-Ray Anal. 5, 1962; Bertin, Principles and Practice of X-Ray
  Spectrometric Analysis, 1975).
* **Detector and counting**: SDD resolution as eds.fwhm; peaks integrated in +-1 FWHM windows that also catch the
  overlapping lines (Mn K-beta in Fe K-alpha, Ni K-beta in Cu K-alpha, Cu K-beta in Zn K-alpha, Ti K-beta in Ce
  L-alpha, ...); background from Compton/Rayleigh scatter of the tube spectrum (strong in a light Al matrix, weak in
  Cu); Poisson counts.

Analysis: background from side windows, overlap correction with the software's line ratios (3 % error, assumed),
then FP iteration with the analysis model: nominal He (no air), the nominal MAC table, no roughness or heterogeneity
correction, results normalized to 100 % with the base element measured. The light-element under-reading, the scatter
background (LOD tens of ppm for transition metals in Al, higher in Cu) and the matrix effects come out of that.
Fidelity: 'lite'/'full' run the chain ('full' adds ``raw``: a synthesized spectrum per condition for the figure);
'fast' samples errors fitted to the lite chain (calib_micro.json, 'xrf').
"""
from __future__ import annotations

import math

import numpy as np

from twin.instruments import eds, micro

SPEC = dict(station="psd", hours=0.15, consumables={"xrf_cup": 1, "prolene_film": 1, "helium_L": 20},
            note="Bruker S2 PUMA, loose powder in a cup under He, three conditions of 100 s")

PSI1 = PSI2 = math.radians(45.0)
CONDITIONS = {"light": dict(kV=12.0, mA=4.0, filt=None, t=100.0),
              "mid": dict(kV=30.0, mA=1.6, filt=("Al", 2.70, 0.010), t=100.0),
              "heavy": dict(kV=50.0, mA=1.0, filt=("Cu", 8.96, 0.025), t=100.0)}
ASSIGN = {"Mg": "light", "Al": "light", "Si": "light", "Zr": "heavy", "Nb": "heavy", "Sn": "heavy"}
# lines for XRF: eds.LINES plus K lines the 50 kV tube excites (Bearden 1967); K yields Krause 1979
XLINES = {e: [l for l in v if l[0] in ("K", "L")] for e, v in eds.LINES.items() if e not in ("Li", "C", "O")}
XLINES["Zr"] = [("K", "Ka", 15.775, 1.0), ("K", "Kb", 17.668, 0.17)]
XLINES["Nb"] = [("K", "Ka", 16.615, 1.0), ("K", "Kb", 18.623, 0.17)]
XLINES["Sn"] = [("K", "Ka", 25.271, 1.0), ("K", "Kb", 28.486, 0.19)]
XOMEGA = dict(eds.OMEGA)
XOMEGA.update({("Zr", "K"): 0.730, ("Nb", "K"): 0.748, ("Sn", "K"): 0.860})
XPRINC = {e: ("L" if e in ("Ce", "Er") else "K") for e in XLINES}
_EG = {}


def _mac(E, el):
    if el == "Be":
        E = np.asarray(E, float)
        return 38.5 * 4 ** 3.66 / 9.012 * np.power(np.maximum(E, 0.02), -2.8)
    return eds.mac(E, el)


def tube(cond):
    """Tube spectrum (relative photons per keV per mA per s, before the specimen) on an energy grid."""
    c = CONDITIONS[cond]
    if cond in _EG:
        return _EG[cond]
    E = np.linspace(0.8, c["kV"] - 0.1, 90)
    N = 46.0 * (c["kV"] - E) / E * 1e6
    N = N * np.exp(-_mac(E, "Be") * 1.85 * 0.0075)
    lines = [(2.838, 0.5e6 * c["kV"] / 12.0)]                       # Pd L-alpha (assumed strength)
    if c["kV"] > 24.35:
        lines += [(21.12, 3.0e6 * ((c["kV"] / 24.35) - 1) ** 1.6), (23.82, 0.5e6 * ((c["kV"] / 24.35) - 1) ** 1.6)]
    for El, a in lines:
        i = np.argmin(abs(E - El))
        N[i] += a / (E[1] - E[0])
    if c["filt"]:
        el, rho, t = c["filt"]
        N = N * np.exp(-_mac(E, el) * rho * t)
    _EG[cond] = (E, N)
    return E, N


_ROWS = {}
_TMAC = {}


def _line_rows(els):
    key = tuple(els)
    if key in _ROWS:
        return _ROWS[key]
    rows = []
    for e in els:
        for fam, ln, El, w in XLINES.get(e, []):
            ed = eds.EDGES[e].get(fam) if not (e in ("Zr", "Nb", "Sn") and fam == "K") else \
                {"Zr": 17.998, "Nb": 18.986, "Sn": 29.200}[e]
            if ed is None:
                continue
            om = XOMEGA.get((e, fam), 0.0)
            if om <= 0:
                continue
            tot = sum(x[3] for x in XLINES[e] if x[0] == fam)
            rows.append((e, fam, ln, El, w / tot, ed, om))
    _ROWS[key] = rows
    return rows


def _tmac(cond, el):
    k = (cond, el)
    if k not in _TMAC:
        _TMAC[k] = eds.mac(tube(cond)[0], el)
    return _TMAC[k]


def intensities(wf, cond, mac_pert=None, rough=None, het=None, path_air=0.0, film=True, sec=True):
    """Net line intensities (relative counts per s) of every line of the elements in wf under one condition,
    vectorized over lines."""
    E, N = tube(cond)
    c = CONDITIONS[cond]
    dE = E[1] - E[0]
    els = [e for e, w in wf.items() if w > 0]
    rows = _line_rows(els)
    if not rows:
        return rows, np.zeros(0)
    w = np.array([wf[e] for e in els])
    T = np.stack([_tmac(cond, e) for e in els])                       # (n_el, nE)
    mus_E = w @ T
    El = np.array([r[3] for r in rows])
    ed = np.array([r[5] for r in rows])
    om = np.array([r[6] for r in rows])
    p = np.array([r[4] for r in rows])
    ie = np.array([els.index(r[0]) for r in rows])
    Ml = np.stack([eds.mac(El, k) for k in els], axis=1)               # (n_rows, n_el)
    if mac_pert:
        Ml = Ml * np.array([[mac_pert(f"{r[0]}{r[2]}", k) for k in els] for r in rows])
    mu_line = Ml @ w
    rj = np.array([eds.r_jump(r[0], r[1]) for r in rows])
    tau = T[ie] * (1 - 1 / rj)[:, None] * (E[None, :] > ed[:, None])
    integ = (N[None, :] * tau / (mus_E[None, :] / math.sin(PSI1) + mu_line[:, None] / math.sin(PSI2))).sum(1) * dE
    I = w[ie] * om * p * integ * c["mA"] * (ed < c["kV"])
    if sec and len(rows) > 1:      # secondary fluorescence by the other elements' lines (assumed simplified form)
        mu_ab = Ml[:, ie].T                                             # [a, b]: MAC of a's element at line b
        ok = (El[None, :] > ed[:, None]) & (ie[None, :] != ie[:, None]) & (I[None, :] > 0)
        ratio = w[ie][:, None] * mu_ab * (1 - 1 / rj)[:, None] / mu_line[None, :]
        L = 0.5 * (np.log1p(mu_line[None, :] / mu_line[:, None]) * mu_line[:, None] / mu_line[None, :] + 0.5)
        src = I / np.maximum(om * p, 1e-9)
        add = (np.where(ok, src[None, :] * ratio * L, 0.0)).sum(1) * om * p * 0.5
        I = I + add
    eff = eds.det_eff(El)
    air = np.exp(-eds.mac(El, "O") * 1.2e-3 * 2.0 * path_air)        # residual air in the He path (2 cm, as O)
    filmT = np.exp(-eds.mac(El, "C") * 0.90 * 4e-4 * 0.857) if film else 1.0
    I = I * eff * air * filmT
    if rough is not None:
        I = I * rough(rows)
    if het is not None:
        I = I * het(rows)
    return rows, I


G_CONST = None
SCATTER_K = 4.0        # scatter-background scale (assumed; sets transition-metal LODs at tens of ppm in Al)
SHELF = 0.012          # incomplete-charge shelf below each line, share of its counts per keV of shelf (assumed)


def _gconst():
    """Instrument constant: pure Cu K-alpha at the mid condition = 150 kcps (assumed)."""
    global G_CONST
    if G_CONST is None:
        rows, I = intensities({"Cu": 1.0}, "mid", film=False)
        i = [k for k, r in enumerate(rows) if r[2] == "Ka"][0]
        G_CONST = 1.5e5 / I[i]
    return G_CONST


def background(wf, cond, El):
    """Scattered tube spectrum under a line at El (cps per keV): Compton + Rayleigh, sigma_s ~ 0.2 (Z/13)^0.5 cm2/g
    against the specimen's absorption (assumed)."""
    E, N = tube(cond)
    zbar = sum(w * micro.Z(e) for e, w in wf.items())
    sig = 0.2 * (zbar / 13.0) ** 0.5
    mu = sum(w * eds.mac(El, e) for e, w in wf.items() if w > 0)
    n0 = np.interp(El, E, _smooth_tube(cond))
    return float(n0 * sig / (2 * mu) * CONDITIONS[cond]["mA"]) * SCATTER_K


_TS = {}


def _smooth_tube(cond):
    """The tube spectrum seen through the detector's resolution (for the scatter background)."""
    if cond not in _TS:
        E, N = tube(cond)
        k = np.exp(-0.5 * (np.arange(-3, 4) / 1.2) ** 2)
        _TS[cond] = np.convolve(N, k / k.sum(), mode="same")
    return _TS[cond]


def _cond_of(e, base):
    return ASSIGN.get(e, "mid")


def simulate(sample, campaign, rng, fidelity="lite"):
    kind = micro.kind_of(sample)
    pm = micro.phase_model(sample, campaign, kind)
    base = pm["base"]
    comp = dict(pm["composition"])
    for e, x in (pm.get("extra") or {}).items():
        comp[e] = comp.get(e, 0.0) + x
    s = sum(comp.values())
    wf = {e: v / s for e, v in comp.items() if v > 0}
    rho = sum(p["vol"] * p["density"] for p in pm["phases"])
    d50 = sum(c["w"] * c["d50"] for c in pm["powder"]["components"]) if kind == "powder" else None
    air = rng.uniform(0.003, 0.02)
    G = _gconst()

    def pert(line, absorber):
        return eds._pert("X" + line, absorber, 1.0 if line[:2] in ("Mg", "Al", "Si") else 5.0)

    a_ps = rng.uniform(0.10, 0.18)

    def _mu(El, wfx):
        return sum(w * eds.mac(El, k) for k, w in wfx.items() if w > 0 and k != "Li")

    def rough(rows):
        if kind != "powder":
            return np.ones(len(rows))
        El = np.array([r[3] for r in rows])
        delta_um = math.sin(PSI2) / (_mu(El, wf) * rho) * 1e4
        return 1 - a_ps * (1 - np.exp(-d50 / np.maximum(delta_um, 1e-3)))

    def het(rows):
        El = np.array([r[3] for r in rows])
        els_r = [r[0] for r in rows]
        mu_bar = _mu(El, wf)
        tot = np.zeros(len(rows))
        acc = np.zeros(len(rows))
        for ph in pm["phases"]:
            x = np.array([ph["comp"].get(e, 0.0) for e in els_r]) * ph["wt"]
            if not (x > 0).any():
                continue
            if ph["role"] == "matrix":
                acc += x
            else:
                D = (_mu(El, ph["comp"]) - mu_bar) * ph["density"] * (ph.get("size_um") or 0.5) * 1e-4
                H = np.where(np.abs(D) > 1e-6, (1 - np.exp(-D)) / np.where(np.abs(D) > 1e-6, D, 1.0), 1.0)
                acc += x * np.minimum(H, 1.5)
            tot += x
        return np.where(tot > 0, acc / np.maximum(tot, 1e-30), 1.0)

    space = micro.AL_ELEMENTS if base == "Al" else micro.CU_ELEMENTS
    els = [base] + [e for e in space if e != "Li"]
    meas = {}
    raw = {}
    wf_x = {e: v for e, v in wf.items() if e != "Li"}
    wf_abs = dict(wf)                       # Li absorbs nothing to speak of; kept for the matrix mass balance
    for cond in CONDITIONS:
        rows, I = intensities({e: v for e, v in wf_abs.items() if e != "Li"}, cond, mac_pert=pert, rough=rough,
                              het=het, path_air=air, film=(kind == "powder"))
        I = I * G
        t = CONDITIONS[cond]["t"]
        lines = [(r, v) for r, v in zip(rows, I)]
        for e in els:
            if _cond_of(e, base) != cond:
                continue
            fam = XPRINC.get(e, "K")
            pr = [r for r in XLINES[e] if r[0] == fam]
            if not pr:
                continue
            El = pr[0][2]
            F = float(eds.fwhm(El))
            sgm = F / 2.3548
            win = 0.0
            for (e2, fam2, ln2, El2, p2, ed2, om2), v in lines:
                s2 = float(eds.fwhm(El2)) / 2.3548
                frac = 0.5 * (math.erf((El + F - El2) / (s2 * math.sqrt(2))) - math.erf((El - F - El2) / (s2 * math.sqrt(2))))
                win += v * frac
            shelf = sum(v * SHELF / max(r[3], 0.5) for r, v in lines if r[3] > El + F)
            B = background(wf_x, cond, El) * G * 2 * F + shelf * 2 * F
            gross = rng.poisson((win + B) * t)
            side = rng.poisson(B * t * 2) / 2.0            # two side windows of the same width
            meas[e] = dict(gross=gross / t, bg=side / t, El=El, F=F, cond=cond, sd=math.sqrt(gross + side / 2) / t)
        if fidelity == "full":
            raw[cond] = (rows, I)
    return dict(meas=meas, wf=wf, base=base, kind=kind, raw=raw, air=air, a_ps=a_ps, rho=rho)


def quantify(meas, campaign, kind="powder"):
    """Overlap correction and FP iteration (nominal He, nominal MACs, no particle corrections), normalized."""
    base = micro.base_of(campaign)
    G = _gconst()
    net = {e: max(m["gross"] - m["bg"], 0.0) for e, m in meas.items()}
    sd = {e: m["sd"] for e, m in meas.items()}
    wf = {base: 0.9}
    for e in net:
        if e != base:
            wf[e] = 0.01
    s = sum(wf.values())
    wf = {e: v / s for e, v in wf.items()}
    for _ in range(3):
        pred = {}
        for cond in CONDITIONS:
            if not any(m["cond"] == cond for m in meas.values()):
                continue
            rows, I = intensities(wf, cond, film=(kind == "powder"))
            pred[cond] = [(r[0], r[3], v * G) for r, v in zip(rows, I)]
        # overlap correction: subtract the predicted contribution of the other elements' lines in each window
        corr = {}
        for e, m in meas.items():
            El, F = m["El"], m["F"]
            spill = 0.0
            own = 0.0
            for e2, El2, v in pred[m["cond"]]:
                s2 = float(eds.fwhm(El2)) / 2.3548
                frac = 0.5 * (math.erf((El + F - El2) / (s2 * math.sqrt(2))) - math.erf((El - F - El2) / (s2 * math.sqrt(2))))
                if e2 == e:
                    own += v * frac
                else:
                    spill += v * frac * 1.03          # the software's line ratios, 3 % off (assumed)
            corr[e] = (max(net[e] - spill, 0.0), own / max(wf.get(e, 1e-6), 1e-6))
        new = {e: c / max(k, 1e-30) for e, (c, k) in corr.items()}
        tot = sum(new.values()) or 1.0
        wf = {e: max(v / tot, 1e-6) for e, v in new.items()}
    comp, lod = {}, {}
    for e, (c, k) in corr.items():
        if e == base:
            continue
        cw = 100.0 * c / k / tot
        t = CONDITIONS[meas[e]["cond"]]["t"]
        lw = 100.0 * 3 * math.sqrt(max(meas[e]["bg"] * t, 1.0) * 2) / t / k / tot     # at least one count
        lod[e] = lw
        if cw > lw:
            comp[e] = float(cw)
    return comp, lod


def measure(sample, campaign, rng, fidelity="fast", **kw):
    if fidelity == "fast":
        return _fast(sample, campaign, rng)
    sim = simulate(sample, campaign, rng, fidelity)
    comp, lod = quantify(sim["meas"], campaign, sim["kind"])
    out = dict(comp=comp)
    if fidelity == "full":
        out["raw"] = dict(lod=lod, meas=sim["meas"], conditions=CONDITIONS, spectra=_spectra(sim),
                          true_wt={e: 100 * v for e, v in sim["wf"].items()}, air_frac=sim["air"])
    return out


def _spectra(sim):
    """A synthesized spectrum per condition for the figure (lines + scatter background, 20 eV channels)."""
    out = {}
    for cond, (rows, I) in sim["raw"].items():
        kv = CONDITIONS[cond]["kV"]
        E = np.arange(0.5, min(kv, 30.0), 0.02)
        y = np.zeros_like(E)
        for (e, fam, ln, El, p, ed, om), v in zip(rows, I):
            if v <= 0:
                continue
            s = float(eds.fwhm(El)) / 2.3548
            y += v * np.exp(-0.5 * ((E - El) / s) ** 2) / (s * math.sqrt(2 * math.pi)) * 0.02
        wf = {k: v for k, v in sim["wf"].items() if k != "Li"}
        zbar = sum(w * micro.Z(e) for e, w in wf.items())
        mu = sum(w * eds.mac(E, e) for e, w in wf.items() if w > 0)
        Et, _ = tube(cond)
        bg = np.interp(E, Et, _smooth_tube(cond)) * 0.2 * (zbar / 13.0) ** 0.5 / (2 * mu) \
            * CONDITIONS[cond]["mA"] * SCATTER_K * _gconst() * 0.02
        out[cond] = (E, (y + bg) * CONDITIONS[cond]["t"], [(r[0], r[2], r[3]) for r in rows])
    return out


def _fast(sample, campaign, rng):
    kind = micro.kind_of(sample)
    pm = micro.phase_model(sample, campaign, kind)
    base = pm["base"]
    comp = {e: v for e, v in pm["composition"].items() if e != base and v > 0}
    for e, x in (pm.get("extra") or {}).items():
        comp[e] = comp.get(e, 0.0) + x
    cal = micro.calib("xrf").get(campaign, {})
    space = micro.AL_ELEMENTS if base == "Al" else micro.CU_ELEMENTS
    out = {}
    for e in space:
        if e == "Li":
            continue
        p = cal.get(f"{e}|{kind}") or {}
        lod_med = p.get("lod_med", 0.005)
        c = comp.get(e, 0.0)
        if c <= 0:
            v = eds.false_positive(p, lod_med * math.exp(rng.normal(0, p.get("lod_sd", 0.2))), rng)
            if v is not None:
                out[e] = float(v)
            continue
        m1, m2 = eds.matrix_features(comp, base)
        m = eds.fast_value(c, lod_med, p, rng, (1.0, math.log10(max(c, 1e-4)), m1, m2))
        if m is not None:
            out[e] = float(m)
    return dict(comp=out)


def calibrate(n=40, reps=3, seed=0, verbose=True):
    """As eds.calibrate: bias on concentration and two matrix descriptors over sample means, within-sample spread,
    near-LOD detection curve, false positives."""
    rng = np.random.default_rng(seed)
    params, table = {}, []
    for camp in ("flaime_al", "onr_cu"):
        pairs = micro.random_samples(camp, n, seed=seed + 7) + list(micro.gallery_samples()[camp].values())
        rows = []
        sid = 0
        for lot, part in pairs:
            for s in (lot, part):
                sid += 1
                kind = micro.kind_of(s)
                pm = micro.phase_model(s, camp, kind)
                comp = {e: v for e, v in pm["composition"].items() if e != pm["base"] and v > 0}
                for e, x_ in (pm.get("extra") or {}).items():
                    comp[e] = comp.get(e, 0.0) + x_
                m1, m2 = eds.matrix_features(comp, pm["base"])
                for _ in range(reps):
                    sim = simulate(s, camp, rng, "lite")
                    cm, lod = quantify(sim["meas"], camp, kind)
                    for e in lod:
                        c = comp.get(e, 0.0)
                        rows.append((e, kind, c, cm.get(e), lod.get(e, np.nan), sid,
                                     (1.0, math.log10(max(c, 1e-4)), m1, m2)))
        cp = {}
        for e in sorted({r[0] for r in rows}):
            for kind in ("powder", "part"):
                R = [r for r in rows if r[0] == e and r[1] == kind]
                if not R:
                    continue
                lods = np.array([r[4] for r in R if np.isfinite(r[4]) and r[4] > 0])
                ent = dict(lod_med=float(np.median(lods)) if len(lods) else 0.005,
                           lod_sd=float(np.std(np.log(lods))) if len(lods) > 2 else 0.2)
                near = eds.fit_near_lod([(r[2], ent["lod_med"], r[3]) for r in R if 0 < r[2] < 3 * ent["lod_med"]])
                if near:
                    ent["near"] = near
                Z0 = [r for r in R if r[2] <= 0]
                fp = [r for r in Z0 if r[3] is not None]
                ent["fp_rate"] = len(fp) / max(len(Z0), 1)
                ent["fp_val"] = float(np.median([r[3] / r[4] for r in fp])) if fp else 1.2
                groups = {}
                for r in R:
                    if r[3] is not None and r[2] > 3 * ent["lod_med"]:
                        groups.setdefault(r[5], (r[6], []))[1].append(math.log(r[3] / r[2]))
                G = list(groups.values())
                if len(G) >= 5:
                    b, sv, between, within = eds.fit_grouped(G)
                    allr = [v for g in G for v in g[1]]
                    ent.update(b=b, s=sv, n=len(allr), n_samples=len(G), between_sd=between, within_sd=within)
                    table.append((camp, e, kind, len(G), float(np.mean(allr)), between, within, ent["lod_med"]))
                cp[f"{e}|{kind}"] = ent
        params[camp] = cp
    if verbose:
        print("campaign  el  kind   samples  mean log(meas/true)  between-sample sd  within sd  LOD wt%")
        for row in table:
            print("%-9s %-3s %-6s %3d %+.3f %.3f %.3f %.4f" % row)
    params["_table"] = [list(r) for r in table]
    return params


def gallery(outdir, samples):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pathlib import Path
    outdir = Path(outdir)
    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(2, 3)
    lot, part = samples["onr_cu"]["NAB"]
    r = measure(lot, "onr_cu", np.random.default_rng(2), fidelity="full")
    for k, cond in enumerate(CONDITIONS):
        ax = fig.add_subplot(gs[0, k])
        E, y, lines = r["raw"]["spectra"][cond]
        ax.semilogy(E, np.maximum(y, 0.5), color="0.3", lw=0.7)
        done = set()
        for e, ln, El in lines:
            if (e, ln[:2]) in done or El > E[-1]:
                continue
            done.add((e, ln[:2]))
            i = np.argmin(abs(E - El))
            if y[i] > 3 * np.median(y):
                ax.annotate(f"{e} {ln}", (El, y[i] * 1.3), fontsize=7, rotation=90, ha="center")
        c = CONDITIONS[cond]
        ax.set_title(f"NAB lot, {cond}: {c['kV']:.0f} kV, {c['t']:.0f} s", fontsize=9)
        ax.set_xlabel("energy (keV)")
    ax = fig.add_subplot(gs[1, :])
    names, true, meas, err = [], [], [], []
    rng = np.random.default_rng(6)
    for camp, d in samples.items():
        for nm, (lot, part) in d.items():
            pm = micro.phase_model(lot, camp, "powder")
            reps = [measure(lot, camp, rng, fidelity="lite")["comp"] for _ in range(4)]
            for e, v in sorted(pm["composition"].items(), key=lambda t: -t[1]):
                if e == pm["base"] or v < 0.05:
                    continue
                ms = [q.get(e, 0.0) for q in reps]
                names.append(f"{nm}\n{e}")
                true.append(v)
                meas.append(np.mean(ms))
                err.append(np.std(ms))
    x = np.arange(len(names))
    ax.bar(x - 0.2, true, 0.4, color="0.6", label="true (lot)")
    ax.bar(x + 0.2, meas, 0.4, yerr=err, color="C1", label="XRF lite, loose powder under He, mean of 4")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=7)
    ax.set_ylabel("wt%")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "xrf.png", dpi=130)
    plt.close(fig)


def thumbnail(path, samples):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lot, part = samples["onr_cu"]["NAB"]
    r = measure(lot, "onr_cu", np.random.default_rng(2), fidelity="full")
    E, y, _ = r["raw"]["spectra"]["mid"]
    fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
    ax = fig.add_axes([0.06, 0.08, 0.9, 0.86])
    yy = np.sqrt(np.maximum(y, 0))
    ax.fill_between(E, 0, yy, color="#fde7c8", lw=0)
    ax.plot(E, yy, color="white", lw=3)
    ax.set_xlim(3.5, 10.5)
    ax.set_ylim(0, yy.max() * 1.05)
    ax.axis("off")
    ax.text(0.97, 0.9, "XRF", transform=ax.transAxes, ha="right", va="top", fontsize=64, color="white",
            fontweight="bold")
    fig.savefig(path, transparent=True)
    plt.close(fig)


if __name__ == "__main__":
    micro.calib_write("xrf", calibrate())

"""Profilometry-based indentation plastometry (Plastometrex PLX-Benchtop): a 1 mm WC-Co ball pressed into the part,
the residual indent profiled with a stylus, and the Voce law found by fitting a model of the indent to the profile.

PIP proper (Campbell et al., Acta Mater. 168, 2019, https://doi.org/10.1016/j.actamat.2019.02.017; Clyne et al.,
Adv. Eng. Mater. 23, 2021, https://doi.org/10.1002/adem.202100437) iterates an axisymmetric FEM model of the test until
its residual profile matches the measured one. Here the forward model is analytical, so that the same iteration is
affordable inside a campaign; the inverse problem and its pathologies are the same:

* **Contact.** Mean pressure p_m = P / (pi a^2) = C sigma_rep, with Tabor's representative strain e_r = 0.2 a / R
  (Tabor, The Hardness of Metals, 1951) and sigma_rep = 0.7 sigma(e_r) + 0.3 sigma(e_r / 4) (the plastic zone's
  boundary is at low strain; weights assumed). C from Johnson's expanding-cavity model,
  C = (2/3)(1 + ln(E* a / (3 sigma_rep R))), capped at 3.0 (Johnson, Contact Mechanics, 1985, ch. 6).
* **Pile-up / sink-in.** Hill, Storakers & Zdunek (Proc. R. Soc. A 423, 1989,
  https://doi.org/10.1098/rspa.1989.0056): c^2 = a^2 / (2 R h) = 2.5 (2 - m) / (4 + m) for sigma ~ e^m, with m the
  Voce law's local exponent between e_r / 10 and e_r; friction trims pile-up (1 - 0.1 (mu - 0.2), assumed).
* **Unloading.** Hertzian elastic recovery against the indenter: h_e = 3 P / (4 E* a), residual crater radius
  1 / R_r = 1 / R - 3 P / (4 E* a^3) (Tabor's recovery argument). Inside the contact the residual profile is that
  spherical cap; outside, a pile-up lobe z_rim (1 + x / w) exp(-x / w), w = a (0.25 + m) (assumed), or a sink-in
  tail z_rim (a / r)^2.

**What the measurement sees.** The plastic zone (radius ~2.5 a, about 1-1.5 mm^3) is mostly sound metal: it holds the
part's fine gas porosity, and a lack-of-fusion void or keyhole only if one happens to sit there (Poisson draw from the
same pore populations as the tensile model, ``mech.defect_populations``); compressive loading closes cracks, which
cost the indentation at most 8 % at the densest network (assumed). So PIP reads close to the sound strength
(``ys_sound_MPa``) and over-reads a porous or cracked part against tensile. Columnar AM grains: the indent axis is the
build direction (Z), and the isotropic inversion returns about the mean of the Z and XY responses, so it under-reads
the XY tensile bar by half the Z/XY difference (Tang et al., Materialia 15, 2021,
https://doi.org/10.1016/j.mtla.2021.101017). The software's elastic modulus is the alloy family's handbook value
(71 GPa Al, 125 GPa Cu, assumed), not the part's. Profilometer: 0.15 um noise, polished-surface roughness 0.2 um
correlated over 20 um, tilt up to ~2 mrad removed by a line fit to the far field, the trace up to 10 um off centre
(all assumed, typical of a stylus instrument). Friction in the real contact varies (0.1-0.4) where the model assumes
0.2. Load: the operator aims at a contact radius of 0.6 R from a rough strength estimate (+-20 %, assumed).

**Output.** ys_MPa: the fitted curve's 0.2 % proof stress; uts_MPa: its engineering maximum (Considere); ue_pct: the
engineering strain there, a uniform elongation, not elongation at fracture (PIP cannot see fracture). The indentation
strains (2-20 %) bracket the necking strain, so the UTS is pinned and the yield is extrapolated: published PIP
agreement with tensile is about 5 % on UTS and about 10 % on yield for isotropic metals (Campbell 2019; Plastometrex,
https://www.plastometrex.com/the-pip-test), which the calibration table in notes/twin_instruments_mech.md checks.

``fast`` samples log(measured / sound) for each output from the state-dependent normal fitted by ``calibrate()``.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import least_squares

from twin.instruments import mech

R_BALL = 0.5                      # mm, 1 mm WC-Co ball
E_BALL, NU_BALL = 600e3, 0.22     # MPa (WC-Co)
LOAD_N = {"flaime_al": 500.0, "onr_cu": 1000.0}
E_ASSUMED = {"flaime_al": 71e3, "onr_cu": 125e3}
MU_MODEL = 0.2
SPEC = dict(station="pip", hours=0.3, indents=3, consumables=dict(polish_usd=5.0),
            note="Plastometrex PLX-Benchtop, 1 mm WC-Co ball, stylus profilometer, inverse fit of a Voce law")


def e_star(E, nu):
    return 1.0 / ((1 - nu * nu) / E + (1 - NU_BALL ** 2) / E_BALL)


def _sig(law, e):
    return float(mech.voce(e, law))


def contact(law, Es, P, R=R_BALL, mu=MU_MODEL):
    """Contact radius a (mm), loaded depth, recovery, crater radius, rim height and lobe width for a Voce law."""
    sy, d, th = law["s_y"], law["s_s"] - law["s_y"], law["theta0"]
    sig = lambda e: sy + d * (1.0 - math.exp(-th * e / d))
    a = math.sqrt(P / (math.pi * 3.0 * sig(0.14 * 0.4)))
    for _ in range(10):
        er = 0.2 * a / R
        srep = 0.7 * sig(er) + 0.3 * sig(er / 4)
        C = min(3.0, max(1.1, (2 / 3) * (1 + math.log(max(Es * a / (3 * srep * R), 1.0)))))
        a_new = math.sqrt(P / (math.pi * C * srep))
        if abs(a_new - a) < 1e-7 * a:
            a = a_new
            break
        a = a_new
    er = 0.2 * a / R
    s1, s0 = sig(er), sig(er / 10)
    m = math.log(s1 / s0) / math.log((er + s1 / Es) / (er / 10 + s0 / Es))
    m = min(max(m, 0.0), 0.6)
    c2 = 2.5 * (2 - m) / (4 + m) * (1 - 0.1 * (mu - 0.2))
    h_max = a * a / (2 * R * c2)
    h_e = 3 * P / (4 * Es * a)
    inv_Rr = 1 / R - 3 * P / (4 * Es * a ** 3)
    h_res = h_max - h_e
    z_rim = -h_res + a * a / 2 * inv_Rr
    w = a * (0.25 + m)
    return dict(a=a, h_max=h_max, h_res=h_res, inv_Rr=inv_Rr, z_rim=z_rim, w=w, m=m, c2=c2)


def profile(r, law, Es, P, mu=MU_MODEL):
    """Residual surface height (mm) at radius r (mm, array)."""
    c = contact(law, Es, P, mu=mu)
    r = np.abs(np.asarray(r, float))
    a = c["a"]
    inside = -c["h_res"] + r * r / 2 * c["inv_Rr"]
    x = np.maximum(r - a, 0.0) / c["w"]
    if c["z_rim"] >= 0:
        outside = c["z_rim"] * (1 + x) * np.exp(-x)
    else:
        outside = c["z_rim"] * (a / np.maximum(r, a)) ** 2
    return np.where(r <= a, inside, outside), c


# ---------------------------------------------------------------------------------------------- the local material
def local_state(sample, rng):
    """Strength factor of the ~1 mm^3 under the indent, and what was there."""
    pores = sample.get("pores") or {}
    gas = float(pores.get("gas", sample.get("porosity", 0.0) if not pores else 0.0))
    a_est = 0.33
    V = 2 / 3 * math.pi * (2.5 * a_est) ** 3
    p_big = 0.0
    hit = []
    for name, n_v, mu, s, af in mech.defect_populations(sample):
        if name in ("gas", "crack"):
            continue
        k = rng.poisson(n_v * V)
        if k:
            d = np.exp(mu + s * rng.normal(0, 1, min(k, 200))) * 1e-3          # mm
            depth_w = np.exp(-rng.random(len(d)) * 2.0)                          # deeper ones matter less
            p_big += float(np.sum(math.pi / 6 * d ** 3 * depth_w)) / V * (k / len(d))
            hit.append((name, int(k)))
    p_loc = min(gas * math.exp(rng.normal(0, 0.3)) + 0.5 * p_big, 0.4)
    cf = min(sample.get("crack_density", 0.0) / (2.0 if sample.get("campaign") == "flaime_al" else 1.5), 1.0)
    an = mech.anisotropy(sample)
    f = (1 - 1.5 * p_loc) * (1 - 0.08 * cf) * (1 - 0.5 * (1 - an["r_z"]))
    return f, dict(p_local=p_loc, voids_hit=hit, anisotropy=1 - 0.5 * (1 - an["r_z"]))


def choose_load(law, campaign, rng):
    """The operator's load: aim at a contact radius of 0.6 R (penetration ratio ~0.2) from a rough strength estimate
    (the family's Vickers or datasheet, +-20 %), rounded to 50 N, within the frame's 0.1-7.5 kN."""
    guess = _sig(law, 0.12) * math.exp(rng.normal(0, 0.2))
    P = math.pi * (0.6 * R_BALL) ** 2 * 3.0 * guess
    return float(min(max(round(P / 50.0) * 50.0, 100.0), 7500.0))


# ---------------------------------------------------------------------------------------------- the measurement
def _trace(law_true, Es_true, P, rng, n_pts, mu_true, half_mm=1.5):
    x = np.linspace(-half_mm, half_mm, n_pts)
    y0 = rng.normal(0, 0.010)
    xc = rng.normal(0, 0.02)
    z, c = profile(np.hypot(x - xc, y0), law_true, Es_true, P, mu=mu_true)
    # roughness: correlated over ~20 um (moving average of white noise), Ra ~ 0.2 um
    dx = x[1] - x[0]
    k = max(int(0.020 / dx), 1)
    white = rng.normal(0, 1, n_pts + 2 * k)
    rough = np.convolve(white, np.ones(2 * k + 1) / math.sqrt(2 * k + 1), mode="same")[k:-k] * 0.25e-3
    tilt = rng.normal(0, 2e-3)
    zm = z + rough + rng.normal(0, 0.15e-3, n_pts) + tilt * x + rng.normal(0, 0.5e-3)
    return x, zm, c


def _level(x, z, a_guess):
    far = np.abs(x) > min(3.2 * a_guess, 0.9 * np.max(np.abs(x)))
    A = np.column_stack([x[far], np.ones(far.sum())])
    k, b = np.linalg.lstsq(A, z[far], rcond=None)[0]
    z = z - (k * x + b)
    # centre: parabola through the bottom of the crater
    i0 = int(np.argmin(z))
    sel = np.abs(x - x[i0]) < 0.6 * a_guess
    if sel.sum() >= 5:
        cc = np.polyfit(x[sel], z[sel], 2)
        xc = -cc[1] / (2 * cc[0]) if cc[0] > 0 else x[i0]
    else:
        xc = x[i0]
    return x - xc, z


def invert(x, z, P, Es_assumed, guess=None, max_nfev=60):
    """Least-squares Voce fit to a levelled, centred profile (the PIP iteration, with the analytical model)."""
    zmin = float(-np.min(z))
    rim = float(np.max(np.abs(x)[np.argmax(z)])) if np.max(z) > 0 else None
    # Tabor start: the contact from the depth (c^2 ~ 1), p_m = 3 sigma
    a0 = math.sqrt(max(2 * R_BALL * zmin, 1e-4))
    s_r = P / (math.pi * a0 * a0) / 3.0
    p0 = np.log([0.7 * s_r, 0.6 * s_r, 12 * s_r]) if guess is None else np.log(guess)
    w = np.ones_like(z)
    w[np.abs(x) < 1.6 * a0] = 2.0                  # the crater and its rim carry the information

    def law_of(p):
        sy, ds, th = np.exp(p)
        return dict(s_y=sy, s_s=sy + ds, theta0=th)

    def res(p):
        zm, _ = profile(x, law_of(p), Es_assumed, P)
        return (zm - z) * 1e3 * w                  # um

    lo = np.log([5.0, 1.0, 50.0])
    hi = np.log([3000.0, 3000.0, 3e5])
    p0 = np.clip(p0, lo + 1e-6, hi - 1e-6)
    sol = least_squares(res, p0, bounds=(lo, hi), x_scale=1.0, max_nfev=max_nfev, method="trf")
    law = law_of(sol.x)
    return law, float(np.sqrt(np.mean(sol.fun ** 2))), rim


def outputs_of(law, E):
    """0.2 % proof stress, engineering UTS and uniform elongation of a Voce law (true -> nominal)."""
    ys = _sig(law, 0.002)
    eps = np.linspace(0, 1.2, 1201)
    se = mech.voce(eps, law) * np.exp(-eps)
    i = int(np.argmax(se))
    return dict(ys_MPa=float(ys), uts_MPa=float(se[i]), ue_pct=float(100 * (math.expm1(eps[i]) + se[i] / E)))


def _chain(sample, campaign, rng, fidelity, n_ind=3):
    law_m = mech.matrix_law(sample)
    E = 1e3 * mech.modulus_GPa(sample["composition"], 0.0, 25.0, mech.base_of(campaign))
    nu = mech.poisson(mech.base_of(campaign))
    Es_true = e_star(E, nu)
    Es_ass = e_star(E_ASSUMED.get(campaign, 100e3), nu)
    P = choose_load(law_m, campaign, rng)
    n_pts = 3001 if fidelity == "full" else 80
    outs, raw = [], []
    for i in range(n_ind):
        f, loc = local_state(sample, rng)
        law_t = dict(s_y=law_m["s_y"] * f, s_s=law_m["s_s"] * f, theta0=law_m["theta0"] * f)
        mu_true = rng.uniform(0.1, 0.4)
        x, zm, c = _trace(law_t, Es_true, P, rng, n_pts, mu_true)
        xl, zl = _level(x, zm, c["a"])
        if fidelity == "full":
            law, rms, rim = invert(xl, zl, P, Es_ass, max_nfev=120)
        else:
            law, rms, rim = invert(xl, zl, P, Es_ass, max_nfev=20)
        o = outputs_of(law, E_ASSUMED.get(campaign, 100e3))
        o.update(rms_um=rms, a_mm=c["a"], depth_um=c["h_res"] * 1e3, rim_um=c["z_rim"] * 1e3, p_local=loc["p_local"])
        outs.append(o)
        if fidelity == "full":
            zfit, _ = profile(xl, law, Es_ass, P)
            raw.append(dict(x_mm=xl, z_um=zl * 1e3, z_fit_um=zfit * 1e3, law_fit=law, law_true=law_t,
                            local=loc, mu=mu_true))
    out = dict(ys_MPa=float(np.mean([o["ys_MPa"] for o in outs])), uts_MPa=float(np.mean([o["uts_MPa"] for o in outs])),
               ue_pct=float(np.mean([o["ue_pct"] for o in outs])), n_indents=n_ind,
               indents=dict(ys_MPa=[o["ys_MPa"] for o in outs], uts_MPa=[o["uts_MPa"] for o in outs],
                            ue_pct=[o["ue_pct"] for o in outs], depth_um=[o["depth_um"] for o in outs]))
    if fidelity == "full":
        out["raw"] = dict(indents=raw, law_matrix=law_m, load_N=P, E_assumed=E_ASSUMED.get(campaign))
    return out


# ---------------------------------------------------------------------------------------------- fast mode
def _feat(sample):
    """Porosity, gas, lack of fusion, cracks, columnar share, the modulus the software assumes against the part's,
    and the matrix law's hardening (the inversion's bias depends on the curve's shape)."""
    f = mech.features(sample)
    camp = sample.get("campaign", "flaime_al")
    E = 1e3 * mech.modulus_GPa(sample["composition"], 0.0, 25.0, mech.base_of(camp))
    nu = mech.poisson(mech.base_of(camp))
    law = mech.matrix_law(sample)
    P = math.pi * (0.6 * R_BALL) ** 2 * 3.0 * _sig(law, 0.12)       # the operator's nominal load
    ct = contact(law, e_star(E, nu), P)                               # the indent the part makes ...
    ca = contact(law, e_star(E_ASSUMED.get(camp, 100e3), nu), P)     # ... and what the software expects of it
    return np.array([f["por"], f["gas"], f["lof"], min(f["crack"], 2.0), f["col"],
                     math.log(E / E_ASSUMED.get(camp, 100e3)), mech.hardening(sample), ct["m"],
                     (ct["h_res"] - ca["h_res"]) / ct["h_res"], (ct["z_rim"] - ca["z_rim"]) / ct["h_res"]])


def _ref(sample):
    st = sample["strength"]
    law = mech.matrix_law(sample)
    o = outputs_of(law, 1e3 * mech.modulus_GPa(sample["composition"], 0.0))
    return dict(ys_MPa=st["ys_sound_MPa"], uts_MPa=o["uts_MPa"], ue_pct=o["ue_pct"])


def _flat(mu, sd, n=10):
    return dict(mu=[mu] + [0] * n, lsd=[math.log(sd)] + [0] * n, xm=[0] * n, xs=[1] * n)


DEFAULTS = {"ys_MPa": _flat(0.0, 0.06), "uts_MPa": _flat(-0.01, 0.03), "ue_pct": _flat(0.1, 0.15), "corr": {}}


def _fast(sample, campaign, rng):
    p = mech.calib("pip") or DEFAULTS
    ref = _ref(sample)
    x = _feat(sample)
    out = {}
    z = rng.normal(0, 1)
    for k in ("ys_MPa", "uts_MPa", "ue_pct"):
        mu, sd = mech.two_level(p[k], x) if "eg" in p[k] else mech.ln_mean_sd(p[k], x)
        rho = p.get("corr", {}).get(k, 0.0) if k != "uts_MPa" else 1.0
        zk = rho * z + math.sqrt(max(1 - rho * rho, 0.0)) * rng.normal(0, 1)
        out[k] = float(ref[k] * math.exp(mu + sd * zk))
    out["n_indents"] = 3
    return out


def measure(sample, campaign, rng, fidelity="fast", **kw):
    if "strength" not in sample:
        return {}
    if fidelity == "fast":
        return _fast(sample, campaign, rng)
    return _chain(sample, campaign, rng, fidelity)


def calibrate(samples_by_campaign, rng, reps=4):
    from twin.instruments.calibrate_mech import fit_two_level
    X, G, Y = [], [], {k: [] for k in ("ys_MPa", "uts_MPa", "ue_pct")}
    for camp, items in samples_by_campaign.items():
        for j, (lot, part) in enumerate(items):
            ref = _ref(part)
            x = _feat(part)
            for _ in range(reps):
                r = _chain(part, camp, rng, "lite")
                X.append(x)
                G.append(f"{camp}{j}")
                for k in Y:
                    Y[k].append(math.log(max(r[k], 1e-3) / max(ref[k], 1e-3)))
    X, G = np.array(X), np.array(G)
    out = {k: fit_two_level(X, np.array(y), G) for k, y in Y.items()}
    # within-sample correlation of the ys / ue errors with the uts error (one indent set drives all three)
    dev = {}
    for k, y in Y.items():
        y = np.array(y)
        m = {u: y[G == u].mean() for u in np.unique(G)}
        dev[k] = y - np.array([m[u] for u in G])
    out["corr"] = {k: float(np.corrcoef(dev["uts_MPa"], dev[k])[0, 1]) for k in dev if k != "uts_MPa"}
    out["n"] = int(len(X))
    return {"pip": out}


# ---------------------------------------------------------------------------------------------- figures
def draw(res, axs, color="C0", label=None):
    ind = res["raw"]["indents"][0]
    ax = axs[0]
    ax.plot(ind["x_mm"], ind["z_um"], ".", ms=1.2, color="0.55", label="stylus trace")
    ax.plot(ind["x_mm"], ind["z_fit_um"], "-", lw=1.2, color=color, label="fitted model")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("height (um)")
    ax2 = axs[1]
    eps = np.linspace(0, 0.3, 300)
    for law, ls, lab in ((ind["law_true"], "--", "local truth"), (ind["law_fit"], "-", "PIP fit")):
        ax2.plot(100 * eps, mech.voce(eps, law), ls, color=color, lw=1.2, label=lab)
    ax2.set_xlabel("true plastic strain (%)")
    ax2.set_ylabel("true stress (MPa)")


def thumb(ax):
    x = np.linspace(-1.6, 1.6, 400)
    r = np.abs(x)
    z = np.where(r < 0.6, -1.0 + (r / 0.6) ** 2 * 1.18, 0.18 * (1 + (r - 0.6) / 0.25) * np.exp(-(r - 0.6) / 0.25))
    ax.plot(x, z, lw=13, color="#7a3fb0", solid_capstyle="round")
    t = np.linspace(0, 2 * np.pi, 100)
    ax.fill(0.55 * np.cos(t), 0.55 + 0.55 * np.sin(t) - 0.42, color="#8c8c8c", zorder=3)
    ax.set_xlim(-1.7, 1.7)
    ax.set_ylim(-1.3, 2.1)

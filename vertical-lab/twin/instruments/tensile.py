"""Tensile test (room temperature and 250 degC): three sub-size bars per test, the curves a frame records, and the
analysis a lab runs on them.

**Specimens.** Proportional flat bars, L0 = 5.65 sqrt(A0) (ISO 6892-1 Annex B): FLAIME 3 x 2 mm section (L0 14 mm,
EDM-cut from the printed block); ONR 6 x 3 mm (L0 24 mm, ASTM E8/E8M sub-size width). Gauge volume and section feed
the weakest-link fracture model in ``mech.py``; the neck's share of the gauge, sqrt(A0) / L0 (Barba's law), sets the
post-uniform elongation.

**The curve.** Elastic loading at the part's modulus (``mech.modulus_GPa``: composition, porosity, temperature) with
a seating toe; Voce plasticity (``mech.bar_law``: the truth's YS and UTS); necking past Considere's point (the neck
follows the same law locally, load (1 - a) sigma(e_n) exp(-e_n), extension (e_n - e_b) sqrt(A0)/L0); fracture at the
strain the specimen's largest defect allows (``mech.specimen_fractures``), so porous and cracked parts scatter more
and a crack-dominated bar can break before its 0.2 % offset. Strain control per ISO 6892-1 method A1: 0.00025 /s to
past yield, then 0.0067 /s. A clip-on extensometer (noise 1.5e-5, resolution 1e-5 strain, assumed class B1 per ISO
9513) and a 10 kN load cell (0.1 % of reading + 0.3 N, assumed); the crosshead record includes the frame and grip
compliance (3e-5 mm/N, assumed), which is why its apparent modulus is low. Data at 50 Hz (full) or 5 Hz (lite).

**Analysis** (ASTM E8/E8M, E111): modulus by least squares between 15 and 40 % of the maximum force, toe
compensation from its intercept, 0.2 % offset yield where the curve crosses the offset line (absent if the bar
breaks first), UTS the maximum stress, elongation at fracture the plastic strain (the elastic part at the last
force removed with the fitted modulus).

**Hot test** (``measure_hot``, 250 degC): ``strength_hot``, E at 250 degC, a furnace held to +-2 K (strength
-0.4 %/K, assumed) and a high-temperature extensometer with twice the noise.

``fast`` samples per-bar log errors whose mean and spread depend on porosity, lack of fusion and crack density,
fitted by ``calibrate()`` on the lite chain (``calib_mech.json``: "tensile", "tensile_hot").
"""
from __future__ import annotations

import math

import numpy as np

from twin.instruments import mech

SPEC = dict(station="tensile", hours=0.6, hours_hot=1.5, bars=3,
            consumables=dict(machining_usd_per_bar=40.0),          # EDM + shop, as the campaign charges (assumed)
            note="screw frame, 10 kN load cell, clip-on extensometer; 250 degC split furnace for the hot test")
GEOM = {"flaime_al": dict(w=3.0, t=2.0), "onr_cu": dict(w=6.0, t=3.0)}
RATE1, RATE2 = 2.5e-4, 6.7e-3          # 1/s, ISO 6892-1 method A1 ranges 2 and 4
C_MACHINE = 3.0e-5                     # mm/N, frame + grips (assumed)


def geometry(campaign: str) -> dict:
    g = GEOM.get(campaign, GEOM["flaime_al"])
    A = g["w"] * g["t"]
    L0 = 5.65 * math.sqrt(A)
    return dict(A=A, L0=L0, V=A * L0, k_neck=math.sqrt(A) / L0, w=g["w"], t=g["t"], L_par=L0 * 1.3)


def _curve(law, E, rel, eps_loc, e_b, elastic, cap, k_neck):
    """The true engineering stress-strain curve of one bar up to fracture: (strain, stress) arrays. ``rel`` is the
    weakest section's capacity relative to the bar law's."""
    sy0 = float(mech.eng_curve(law, 0.0))
    if elastic:
        s = np.linspace(0, cap, 40)
        return s / E, s
    s_el = np.linspace(0, sy0, 30)
    e_el = s_el / E
    ep = np.linspace(0, max(e_b, 1e-6), 80)
    s_pl = mech.eng_curve(law, ep)
    e_pl = np.expm1(ep) + s_pl / E
    parts_e, parts_s = [e_el, e_pl], [s_el, s_pl]
    if eps_loc > e_b:                               # the neck (at the defect section, or anywhere if none)
        en = np.linspace(e_b, eps_loc, 60)[1:]
        if eps_loc <= law["eu"]:                    # still hardening when it breaks: load stays at its capacity
            sn = np.full_like(en, s_pl[-1])
        else:
            sn = np.minimum(rel * mech.eng_curve(law, np.maximum(en, law["eu"])), s_pl[-1])
        e_n = np.expm1(e_b) + (en - e_b) * k_neck * rel + sn / E
        parts_e.append(e_n)
        parts_s.append(sn)
    return np.concatenate(parts_e), np.concatenate(parts_s)


def _record(e, s, E, rng, rate_hz, noise_x, geom, ys_est):
    """Resample the curve on the controller's time base and add the transducers' errors."""
    e = np.maximum.accumulate(e)
    switch = 2 * ys_est / E + 0.005
    t_of = np.where(e < switch, e / RATE1, switch / RATE1 + (e - switch) / RATE2)
    t = np.arange(0.0, t_of[-1], 1.0 / rate_hz)
    if len(t) < 12:
        t = np.linspace(0, t_of[-1], 12)
    ee = np.interp(t, t_of, e)
    ss = np.interp(ee, e, s)
    toe = 1.2e-4 * (1 - np.exp(-ss / (0.04 * max(ys_est, 1.0))))      # seating, before the grips bed in
    F = ss * geom["A"]
    Fm = F * (1 + rng.normal(0, 1e-3, len(F))) + rng.normal(0, 0.3, len(F))
    em = ee + toe + rng.normal(0, 1.5e-5 * noise_x, len(ee))
    em = np.round(em / 1e-5) * 1e-5
    cross = ee * geom["L_par"] + F * C_MACHINE
    return t, em, Fm / geom["A"], cross


def analyse(e, s):
    """ASTM E8 / E111 on one record: modulus, toe-corrected 0.2 % offset yield, UTS, plastic elongation."""
    imax = int(np.argmax(s))
    smax = float(s[imax])
    sel = np.where((s[:imax + 1] > 0.15 * smax) & (s[:imax + 1] < 0.40 * smax))[0]
    if len(sel) < 4:
        sel = np.arange(min(4, imax + 1))
    A = np.column_stack([e[sel], np.ones(len(sel))])
    k, c = np.linalg.lstsq(A, s[sel], rcond=None)[0]
    if k <= 0:
        k = 1e5
    e0 = -c / k                                     # toe compensation
    off = s - k * (e - e0 - 0.002)
    ys = None
    idx = np.where((off[1:] < 0) & (off[:-1] >= 0))[0]
    idx = idx[idx >= sel[-1]] if len(idx) else idx
    if len(idx):
        i = int(idx[0])
        f = off[i] / (off[i] - off[i + 1])
        ys = float(s[i] + f * (s[i + 1] - s[i]))
    el = max(float(e[-1] - e0 - s[-1] / k), 0.0) * 100.0
    return dict(E_GPa=float(k) / 1e3, ys_MPa=ys, uts_MPa=smax, el_pct=el)


def _chain(sample, campaign, rng, fidelity, hot, n=3, orientation="xy"):
    geom = geometry(campaign)
    law = mech.bar_law(sample, hot)
    T = 250.0 if hot else 25.0
    E = 1e3 * mech.modulus_GPa(sample["composition"], sample.get("porosity", 0.0), T, mech.base_of(campaign))
    st = mech._strength(sample, hot)
    el_target = None
    if orientation == "z":                          # bars along the build direction: columnar grains (mech.anisotropy)
        an = mech.anisotropy(sample)
        law = dict(law, s_y=law["s_y"] * an["r_z"], s_s=law["s_s"] * an["r_z"], theta0=law["theta0"] * an["r_z"])
        el_target = st["el_pct"] * an["el_z"]
    fr = mech.specimen_fractures(sample, law, geom, rng, n, hot, el_target)
    eps_loc_mean, a_mean = mech.eps_loc_for(sample, law, geom, hot, el_target)
    bars, raw = [], []
    rate = 50.0 if fidelity == "full" else 5.0
    for i in range(n):
        # bar-to-bar material variation (position in the build, local porosity: 1.2 % + 0.3 x porosity, assumed)
        k = math.exp(rng.normal(0, 0.012 + 0.3 * sample.get("porosity", 0.0)))
        if hot:
            k *= 1 - 0.004 * rng.normal(0, 2.0)
        lw = dict(law, s_y=law["s_y"] * k, s_s=law["s_s"] * k, theta0=law["theta0"] * k)
        # section measured with a micrometer (+-5 um per dimension, assumed): the stress the lab computes
        g_meas = (geom["w"] + rng.normal(0, 0.005)) * (geom["t"] + rng.normal(0, 0.005)) / geom["A"]
        loc = float(fr["eps_loc"][i])
        a = float(fr["a"][i])
        rel = min((1 - a) / (1 - a_mean), 1.0)
        cap = rel * float(mech.eng_curve(lw, min(loc, lw["eu"])))
        sy0 = float(mech.eng_curve(lw, 0.0))
        elastic = cap < sy0
        peak = float(mech.eng_curve(lw, lw["eu"]))
        grid = np.linspace(0, lw["eu"], 160)
        e_b = float(np.interp(min(cap, peak), mech.eng_curve(lw, grid), grid)) if not elastic else 0.0
        e, s = _curve(lw, E, rel, loc, e_b, elastic, cap, geom["k_neck"])
        t, em, sm, cross = _record(e, s, E, rng, rate, 2.0 if hot else 1.0, geom, st["ys_MPa"])
        sm = sm / g_meas
        res = analyse(em, sm)
        res.update(elastic_break=bool(elastic), defect_share=a, dmax_um=float(fr["dmax_um"][i]))
        bars.append(res)
        if fidelity == "full":
            raw.append(dict(t_s=t, strain=em, stress_MPa=sm, crosshead_mm=cross, true_strain=e, true_stress=s))
    out = _summarise(bars)
    if fidelity == "full":
        out["raw"] = dict(bars=raw, law=law, E_true_GPa=E / 1e3, geometry=geom, eps_loc=eps_loc_mean,
                          truth=dict(st) if isinstance(st, dict) else st)
    return out


def _summarise(bars):
    ys = [b["ys_MPa"] for b in bars if b["ys_MPa"] is not None]
    out = dict(uts_MPa=float(np.mean([b["uts_MPa"] for b in bars])), el_pct=float(np.mean([b["el_pct"] for b in bars])),
               n_bars=len(bars), E_GPa=float(np.mean([b["E_GPa"] for b in bars])),
               bars=dict(ys_MPa=[b["ys_MPa"] for b in bars], uts_MPa=[b["uts_MPa"] for b in bars],
                         el_pct=[b["el_pct"] for b in bars], E_GPa=[b["E_GPa"] for b in bars],
                         elastic_break=[b.get("elastic_break", False) for b in bars]))
    if ys:
        out["ys_MPa"] = float(np.mean(ys))
    return out


# ---------------------------------------------------------------------------------------------- fast mode
def _feat(sample, hot=False):
    """Porosity, lack of fusion, cracks, the truth's ductility and the largest-defect share's mean and spread."""
    f = mech.features(sample)
    camp = sample.get("campaign", "flaime_al")
    am, asd = mech.defect_stats(sample, geometry(camp))
    el = mech._strength(sample, hot)["el_pct"]
    return np.array([f["por"], f["lof"], math.log1p(f["crack"]), math.log(max(el, 0.05)), am, asd])


NF = 6


def _flat(mu, sd):
    return dict(mu=[mu] + [0] * NF, lsd=[math.log(sd)] + [0] * NF, xm=[0] * NF, xs=[1] * NF)


DEFAULTS = dict(ys=_flat(0.0, 0.015), uts=_flat(-0.01, 0.02), el=_flat(-0.02, 0.15), E=_flat(0.0, 0.01),
                noyield=dict(c=[-6.0] + [0] * NF, xm=[0] * NF, xs=[1] * NF))


def _fast(sample, campaign, rng, hot):
    p = mech.calib("tensile_hot" if hot else "tensile") or DEFAULTS
    st = mech._strength(sample, hot)
    x = _feat(sample, hot)
    E0 = mech.modulus_GPa(sample["composition"], sample.get("porosity", 0.0), 250.0 if hot else 25.0,
                          mech.base_of(campaign))
    nz = p["noyield"]
    zz = (x - np.asarray(nz["xm"])) / np.asarray(nz["xs"])
    pz = 1 / (1 + math.exp(-(nz["c"][0] + float(np.dot(nz["c"][1:], zz)))))
    m = {k: (mech.two_level(p[k], x) if "eg" in p[k] else mech.ln_mean_sd(p[k], x)) for k in ("ys", "uts", "el", "E")}
    bars = []
    for _ in range(3):
        brk = rng.random() < pz
        z = rng.normal(0, 1, 4)
        bars.append(dict(
            ys_MPa=None if brk else st["ys_MPa"] * math.exp(m["ys"][0] + m["ys"][1] * z[0]),
            uts_MPa=st["uts_MPa"] * math.exp(m["uts"][0] + m["uts"][1] * z[1]),
            el_pct=0.0 if brk else st["el_pct"] * math.exp(m["el"][0] + m["el"][1] * z[2]),
            E_GPa=E0 * math.exp(m["E"][0] + m["E"][1] * z[3]), elastic_break=bool(brk)))
    return _summarise(bars)


def measure(sample, campaign, rng, fidelity="fast", orientation="xy", **kw):
    """Three bars at room temperature. ``orientation='z'`` cuts them along the build direction (lower flow stress
    and elongation in a columnar part; the fast mode is calibrated for XY bars, so Z bars run the lite chain)."""
    if "strength" not in sample:
        return {}
    if fidelity == "fast" and orientation == "xy":
        return _fast(sample, campaign, rng, False)
    return _chain(sample, campaign, rng, "full" if fidelity == "full" else "lite", False, orientation=orientation)


def measure_hot(sample, campaign, rng, fidelity="fast", orientation="xy", **kw):
    """Three bars at 250 degC (``strength_hot``); absent when the campaign did not ask for the hot strength."""
    if sample.get("strength_hot") is None:
        return {}
    if fidelity == "fast" and orientation == "xy":
        return _fast(sample, campaign, rng, True)
    return _chain(sample, campaign, rng, "full" if fidelity == "full" else "lite", True, orientation=orientation)


# ---------------------------------------------------------------------------------------------- calibration
def _fit_bars(samples, rng, hot, reps):
    from twin.instruments.calibrate_mech import fit_two_level
    rows, gid = [], []
    for camp, items in samples.items():
        for j, (lot, part) in enumerate(items):
            if hot and not part.get("strength_hot"):
                continue
            st = mech._strength(part, hot)
            x = _feat(part, hot)
            E0 = mech.modulus_GPa(part["composition"], part.get("porosity", 0.0), 250.0 if hot else 25.0,
                                  mech.base_of(camp))
            for _ in range(reps):
                r = _chain(part, camp, rng, "lite", hot)
                for i in range(r["n_bars"]):
                    ys = r["bars"]["ys_MPa"][i]
                    rows.append((x, ys, r["bars"]["uts_MPa"][i], r["bars"]["el_pct"][i], r["bars"]["E_GPa"][i],
                                 ys is None, st, E0))
                    gid.append(f"{camp}{j}")
    X = np.array([r[0] for r in rows])
    ok = np.array([not r[5] for r in rows])
    ly = np.array([math.log(r[1] / r[6]["ys_MPa"]) if r[1] else 0.0 for r in rows])
    lu = np.array([math.log(r[2] / r[6]["uts_MPa"]) for r in rows])
    le = np.array([math.log(max(r[3], 1e-3) / r[6]["el_pct"]) for r in rows])
    lE = np.array([math.log(r[4] / r[7]) for r in rows])
    g = np.array(gid)
    out = dict(ys=fit_two_level(X[ok], ly[ok], g[ok]), uts=fit_two_level(X, lu, g), el=fit_two_level(X[ok], le[ok], g[ok]),
               E=fit_two_level(X, lE, g))
    # a break before the 0.2 % offset: logistic regression on the standardized features
    xm, xs = X.mean(0), np.where(X.std(0) > 1e-12, X.std(0), 1.0)
    yb = (~ok).astype(int)
    if 3 <= yb.sum() <= len(yb) - 3:
        from sklearn.linear_model import LogisticRegression
        lr = LogisticRegression(C=1.0, max_iter=1000).fit((X - xm) / xs, yb)
        c = [float(lr.intercept_[0])] + [float(v) for v in lr.coef_[0]]
    else:
        q = min(max(yb.mean(), 1e-4), 1 - 1e-4)
        c = [math.log(q / (1 - q))] + [0.0] * X.shape[1]
    out["noyield"] = dict(c=c, xm=[float(v) for v in xm], xs=[float(v) for v in xs])
    out["n_bars"] = len(rows)
    out["frac_noyield"] = float(yb.mean())
    return out


def calibrate(samples_by_campaign, rng, reps=3):
    return {"tensile": _fit_bars(samples_by_campaign, rng, False, reps),
            "tensile_hot": _fit_bars({"flaime_al": samples_by_campaign.get("flaime_al", [])}, rng, True, reps)}


# ---------------------------------------------------------------------------------------------- figures
def draw(res, ax, color=None, label=None):
    for i, b in enumerate(res["raw"]["bars"]):
        ax.plot(100 * b["strain"], b["stress_MPa"], lw=1.2, color=color, alpha=0.9 - 0.2 * i,
                label=label if i == 0 else None)
    if res.get("ys_MPa"):
        ax.axhline(res["ys_MPa"], color=color, lw=0.6, ls=":")
    ax.set_xlabel("engineering strain (%)")
    ax.set_ylabel("engineering stress (MPa)")


def thumb(ax):
    e = np.linspace(0, 1, 200)
    s = np.where(e < 0.08, e / 0.08 * 0.62, 0.62 + 0.38 * (1 - np.exp(-(e - 0.08) / 0.25)))
    s = np.where(e > 0.82, s * (1 - 2.5 * np.clip(e - 0.82, 0, None) ** 1.5), s)
    ax.plot(e[e <= 0.95], s[e <= 0.95], lw=14, color="#1f5fa8", solid_capstyle="round")
    ax.plot([0.95, 0.95], [s[e <= 0.95][-1], 0.25], lw=8, color="#1f5fa8", ls=(0, (1, 1.2)))
    ax.plot([0, 0, 1.02], [1.08, 0, 0], lw=7, color="#8c8c8c", solid_capstyle="round")
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(-0.08, 1.12)

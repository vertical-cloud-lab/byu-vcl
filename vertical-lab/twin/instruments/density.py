"""Archimedes density (ASTM B962 / ISO 3369 practice): a printed or deposited coupon weighed dry in air and suspended
in water on a 0.1 mg balance; relative density against the theoretical density of the DESIGNED composition.

**The weighings.** Coupon 10 x 10 x 10 mm (Al) or 10 x 10 x 5 mm (Cu), mass from its true density and porosity.
Balance readability 0.1 mg, repeatability 0.1 mg (assumed for an analytical balance with a density kit). The water's
density at the bath temperature from Tanaka et al.'s formula (Metrologia 38, 2001,
https://doi.org/10.1088/0026-1394/38/4/3); the room drifts 21 +- 1.5 degC and the thermometer reads +-0.2 K
(assumed). The submerged basket is tared, but the meniscus on its 0.2 mm wire varies by +-0.3 mg between weighings
(assumed, with a wetting agent). Bubbles cling to an as-built surface: exponential volume, mean 0.4 mm^3 (Al LPBF
coupon) or 0.8 mm^3 (DED, rougher), assumed; they add buoyancy, so density reads low. Air buoyancy on the dry
weighing is not corrected (common practice; 0.12 % of the mass).

**Open porosity.** Water fills surface-connected pores, so their volume is never counted and an unsealed porous part
reads denser than it is (ASTM B962 seals with oil or lacquer for this reason). Shares of each population that are
connected to the surface (assumed): lack of fusion 0.3 + 10 x its share (interconnected voids, capped at 1), keyholes
5 %, gas pores 2 %, cracks 80 %. ``sealed=True`` counts them, at the cost of a lacquer film whose own volume is
corrected to +-0.2 mm^3 (assumed).

**Reference density.** Rule of mixtures on specific volume (``twin.physics.density``) for the designed composition,
as a lab would compute it before it has an ICP-MS result: Mg, Zn or Li lost in the atomizer or under the laser, or a
primary former left undissolved, shift the true density and bias the relative density.

``fast``: the designed-versus-actual composition offset is computed exactly; the measurement's own error (open
porosity, bubbles, temperature) is sampled from the normal ``calibrate()`` fitted to the lite chain against lack of
fusion, porosity and cracks.
"""
from __future__ import annotations

import math

import numpy as np

from twin import physics as ph
from twin.instruments import mech

SPEC = dict(station="density", hours=0.5, consumables=dict(water_usd=0.1),
            note="analytical balance (0.1 mg) with a density kit; Archimedes in water")
COUPON_CM3 = {"flaime_al": 1.0, "onr_cu": 0.5}


def water_density(t_C: float) -> float:
    """g/cm^3, Tanaka et al. (2001), air-saturated water ~ (-0.0000028) neglected."""
    a1, a2, a3, a4, a5 = -3.983035, 301.797, 522528.9, 69.34881, 999.974950
    return a5 * (1 - (t_C + a1) ** 2 * (t_C + a2) / (a3 * (t_C + a4))) / 1000.0


def _design_comp(sample, campaign):
    d = dict(sample.get("design") or sample["composition"])
    bal = "Al" if campaign == "flaime_al" else "Cu"
    d = {e: float(v) for e, v in d.items() if e in ph.RHO and v > 0}
    if bal not in d or abs(sum(d.values()) - 100.0) > 0.5:
        d[bal] = 100.0 - sum(v for e, v in d.items() if e != bal)
    return d


def open_share(sample):
    pores = sample.get("pores") or {}
    lof = float(pores.get("lof", 0.0))
    op = lof * min(1.0, 0.3 + 10 * lof) + 0.05 * float(pores.get("keyhole", 0.0)) + 0.02 * float(pores.get("gas", 0.0))
    op += 0.8 * float(pores.get("crack", 0.004 * sample.get("crack_density", 0.0)))
    if not pores:
        op = 0.2 * sample.get("porosity", 0.0)
    return min(op, sample.get("porosity", 0.0))


def _chain(sample, campaign, rng, fidelity, sealed=False, _bubble=False):
    rho_s = ph.density(sample["composition"])                 # g/cm3, the metal itself
    por = float(sample.get("porosity", 0.0))
    V = COUPON_CM3.get(campaign, 1.0)
    m_true = rho_s * (1 - por) * V
    open_v = open_share(sample) * V if not sealed else 0.0
    closed_v = por * V - open_v
    T = 21.0 + rng.normal(0, 1.5)
    rho_w = water_density(T)
    bub = rng.exponential(0.4e-3 if campaign == "flaime_al" else 0.8e-3)       # cm3
    film = 0.0
    if sealed:
        film = rng.normal(0, 0.2e-3)
    rho_air = 0.0012
    m_air = m_true - rho_air * (V - por * V) + rng.normal(0, 1e-4)
    # submerged: metal + closed pores (empty) + bubbles displace water; open pores are flooded
    disp = V - open_v + bub + film
    m_wet = m_true - rho_w * disp + rng.normal(0, 1e-4) + rng.normal(0, 3e-4)
    m_air_r = round(m_air, 4)
    m_wet_r = round(m_wet, 4)
    T_read = T + rng.normal(0, 0.2)
    rho_meas = m_air_r * water_density(T_read) / (m_air_r - m_wet_r)
    rho_th = ph.density(_design_comp(sample, campaign))
    out = dict(rel_density=float(rho_meas / rho_th), density_g_cm3=float(rho_meas), rho_theoretical=float(rho_th))
    if _bubble:                                               # hidden state, for calibrate() only
        out["_bubble_cm3"] = float(bub)
    if fidelity == "full":
        out["raw"] = dict(m_air_g=m_air_r, m_wet_g=m_wet_r, T_C=T_read, rho_water=water_density(T_read),
                          bubble_mm3=bub * 1e3, open_porosity=open_v / V, closed_porosity=closed_v / V,
                          rho_actual_comp=rho_s, rel_true=1 - por, sealed=sealed)
    return out


def _feat(sample):
    f = mech.features(sample)
    return np.array([f["por"], f["lof"], min(f["crack"], 2.0)])


DEFAULTS = dict(mu=[0.001, 0.0, 0.0, 0.0], lsd=[math.log(0.001), 0, 0, 0], xm=[0, 0, 0], xs=[1, 1, 1])


_BUBBLE = {"flaime_al": 0.4e-3, "onr_cu": 0.8e-3}


def _expected(sample, campaign, bub_cm3):
    """The chain's reading without its noise: open pores flooded, a bubble's buoyancy, the designed reference."""
    V = COUPON_CM3.get(campaign, 1.0)
    por = sample["porosity"]
    disp = V * (1 - open_share(sample)) + bub_cm3
    return (1 - por) * V / disp * _offset(sample, campaign)


def _offset(sample, campaign):
    return ph.density(sample["composition"]) / ph.density(_design_comp(sample, campaign))


def measure(sample, campaign, rng, fidelity="fast", sealed=False, **kw):
    if "composition" not in sample or "porosity" not in sample:
        return {}
    if fidelity == "fast" and not sealed:
        p = mech.calib("density") or DEFAULTS
        mu, sd = mech.two_level(p, _feat(sample)) if "eg" in p else mech.ln_mean_sd(p, _feat(sample))
        rel = _expected(sample, campaign, rng.exponential(_BUBBLE[campaign])) + mu + sd * rng.normal(0, 1)
        return dict(rel_density=float(rel))
    return _chain(sample, campaign, rng, fidelity, sealed)


def calibrate(samples_by_campaign, rng, reps=6):
    from twin.instruments.calibrate_mech import fit_two_level
    X, y, G = [], [], []
    for camp, items in samples_by_campaign.items():
        for j, (lot, part) in enumerate(items):
            for _ in range(reps):
                r = _chain(part, camp, rng, "lite", _bubble=True)
                G.append(f"{camp}{j}")
                X.append(_feat(part))
                y.append(r["rel_density"] - _expected(part, camp, r["_bubble_cm3"]))
    return {"density": fit_two_level(np.array(X), np.array(y), np.array(G))}

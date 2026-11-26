"""Shared physics: material properties, the ultrasonic atomizer, and moving-heat-source melt pools.

Everything here is a closed form with its source; constants that are ours are marked "assumed" and listed in
notes/twin.md. The campaign truths (twin/truth_al.py, twin/truth_cu.py) build on these.

* **Atomizer** (AMAZEMET rePOWDER, 40 kHz). Median droplet size from Lang's capillary-wave relation,
  d50 = 0.34 (8 pi sigma / (rho f^2))^(1/3) (Lang, J. Acoust. Soc. Am. 34, 1962), which gives about 47 um for a copper
  melt at 40 kHz, as DAL PR 117 computes. Measured powders are about twice that (NAB at 40 kHz: d50 98 um, Uhlmann
  2024; CuSn8 63-150 um, Choma 2026), so the truth scales Lang by a coarsening factor that rises with the melt flow
  (pour pressure) and falls with plate amplitude (assumed form, anchored on those two). Size distribution lognormal,
  geometric SD 1.6 (assumed). Usable share 91 % at a good setting (the Oct 27 bronze run, DAL #219); one run in ten
  drips at the finale's settings (timelapse.py PARAMS run_fail_every), more when the melt is too cold.
* **Melt pools.** Rosenthal's moving point source on a thick plate (Rosenthal 1946) for the width and the cooling rate
  at the solidus; the normalized enthalpy dH/h_s = A P / (pi h_s sqrt(D v s^3)) (King et al., J. Mater. Process.
  Technol. 214, 2014) with keyhole onset at pi T_b / T_m; lack of fusion where (h/W)^2 + (t/D)^2 > 1 (Tang, Pistorius
  & Beuth, Addit. Manuf. 14, 2017).
"""
from __future__ import annotations

import math

import numpy as np

# elemental properties: density (g/cm3, solid at RT), boiling point (K), molar mass (CRC Handbook)
RHO = dict(Al=2.70, Cu=8.96, Ni=8.91, Fe=7.87, Mn=7.21, Cr=7.19, Si=2.33, Nb=8.57, Ti=4.51, Zr=6.52, Mg=1.74,
           Zn=7.14, Sc=2.99, Ce=6.77, Li=0.534, Sn=7.29, Er=9.07)
T_BOIL = dict(Al=2743.0, Cu=2835.0, Ni=3186.0, Fe=3134.0, Mn=2334.0, Cr=2944.0, Si=3538.0, Nb=5017.0, Ti=3560.0,
              Zr=4682.0, Mg=1363.0, Zn=1180.0, Sc=3109.0, Ce=3716.0, Li=1615.0, Sn=2875.0, Er=3141.0)
SURFACE_TENSION = dict(Al=0.87, Cu=1.30)        # N/m at the melting point (Keene, Int. Mater. Rev. 38, 1993)
LIQ_DENSITY = dict(Al=2375.0, Cu=7900.0)       # kg/m3 at the melting point


def density(wt: dict) -> float:
    """Rule of mixtures on specific volume, g/cm3."""
    return 100.0 / sum(w / RHO[e] for e, w in wt.items() if w > 0)


def lognorm_frac(d50, sg, lo, hi) -> float:
    """Mass fraction of a lognormal size distribution (median d50, geometric SD sg) between lo and hi (um)."""
    from math import erf, log, sqrt
    s = log(sg)
    cdf = lambda d: 0.5 * (1 + erf((log(d) - log(d50)) / (s * sqrt(2)))) if d > 0 else 0.0
    return max(0.0, cdf(hi) - cdf(lo))


def lang_d50_um(base: str, f_hz=40e3) -> float:
    s, r = SURFACE_TENSION[base], LIQ_DENSITY[base]
    return 0.34 * (8 * math.pi * s / (r * f_hz ** 2)) ** (1 / 3) * 1e6


def atomize(base: str, superheat_K: float, pour_mbar: float, amplitude: float, T_melt_C: float,
            rng: np.random.Generator, cut=(20.0, 63.0)) -> dict:
    """One run of the ultrasonic atomizer. Returns what the run did, not what is measured (truth)."""
    coarsen = 1.55 * (1 + 0.55 * (pour_mbar - 200.0) / 200.0) * (1.25 - 0.45 * (amplitude - 0.3) / 0.7)
    d50 = lang_d50_um(base) * coarsen * math.exp(rng.normal(0, 0.06))
    sg = 1.6
    # a cold melt freezes on the plate (the Oct 8 Al 6063 run dripped); too much flow floods it
    p_fail = 0.06 + 0.55 / (1 + math.exp((superheat_K - 70.0) / 14.0)) + 0.15 / (1 + math.exp(-(pour_mbar - 340) / 25))
    if base == "Cu" and T_melt_C > 1300.0:        # above the module's usual 1300 degC: crucible and plate wear
        p_fail += 0.10 * (T_melt_C - 1300.0) / 50.0
    failed = rng.random() < min(p_fail, 0.95)
    usable = 0.0 if failed else 0.91 * (1 - 0.25 / (1 + math.exp((superheat_K - 90) / 15)))
    fines = lognorm_frac(d50, sg, 0.0, 20.0)
    in_cut = lognorm_frac(d50, sg, *cut)
    sat = 0.05 + 0.25 * max(0.0, (pour_mbar - 250) / 150) + 0.1 * (1 - amplitude)   # satellite share, assumed
    oxygen = (350 if base == "Al" else 250) + 2.5 * superheat_K + 2500 * fines        # ppm, assumed
    return dict(failed=failed, p_fail=p_fail, d50_um=d50, gsd=sg, usable_frac=usable, cut_frac=in_cut,
                fines_frac=fines, satellite_frac=min(sat, 0.6), oxygen_ppm=oxygen)


def rosenthal(A: float, P: float, v: float, k: float, rho: float, cp: float, Tm: float, T0: float):
    """Thick-plate moving point source: melt-pool half-width (m) at the widest point, solving
    T - T0 = A P / (2 pi k R) exp(-v (R + x) / (2 a)) on a grid behind the source; cooling rate at Tm (K/s) on the
    centreline, 2 pi k (Tm - T0)^2 v / (A P) (Rosenthal 1946)."""
    a = k / (rho * cp)
    q = A * P / (2 * math.pi * k)
    best = 0.0
    for x in np.linspace(-4e-3, 2e-4, 400):        # behind (negative) to just ahead of the source
        # solve for the radius R on this line where T = Tm, then y = sqrt(R^2 - x^2)
        lo, hi = abs(x) + 1e-9, 5e-3
        f = lambda R: q / R * math.exp(-v * (R + x) / (2 * a)) - (Tm - T0)
        if f(lo) <= 0:
            continue
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        y = math.sqrt(max(lo * lo - x * x, 0.0))
        best = max(best, y)
    cool = 2 * math.pi * k * (Tm - T0) ** 2 * v / (A * P)
    return best, cool


def normalized_enthalpy(A, P, v, k, rho, cp, Tm_K, spot_radius):
    a = k / (rho * cp)
    hs = rho * cp * Tm_K
    return A * P / (math.pi * hs * math.sqrt(a * v * spot_radius ** 3))

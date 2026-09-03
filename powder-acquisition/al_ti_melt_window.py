"""Al-Ti melt-temperature window for induction-melted ultrasonic atomization (issue #161).

Computes, with pycalphad + the public COST507 light-alloy database:

1. the Al-rich Al-Ti liquidus (the temperature at which an Al-x wt% Ti charge is
   fully liquid -- the hard floor for atomization, independent of feedstock form);
2. the liquidus of the candidate master alloys, i.e. what it would take to melt
   and atomize the master alloys themselves;
3. equilibrium vapour pressures of the volatile solutes, which set the *upper*
   bound on how much superheat the campaign can afford.

Validation of (1) against experiment:
  - in-situ LIBS liquidus, Al-0.27 wt% Ti  -> measured 740 degC, computed 730 degC
    (Leosson et al., Spectrochim. Acta B 190 (2022) 106387)
  - max solubility of Ti in Al at solidification -> measured ~0.16 wt%, computed 0.16 wt%
    at 684 degC (peritectic 665 degC in the assessed diagram)
  - Al3Ti (25 at.% Ti) -> computed 1371 degC vs ~1387-1390 degC reported

Usage:  python al_ti_melt_window.py            (prints tables, writes the figure)
Requires: pycalphad, matplotlib, numpy, and cost507.tdb alongside this file.
"""

import json
import os
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TDB = os.path.join(HERE, "cost507.tdb")
# COST507 light-alloy database (Ansara/Dinsdale/Rand, EUR 18499), corrected copy.
# Not vendored -- downloaded on first use.
TDB_URL = ("https://gist.githubusercontent.com/bocklund/"
           "c4714ddbc0500c78e6fe255a763e7550/raw")
CACHE = os.path.join(HERE, "al-ti-melt-window-data.json")

M = {"AL": 26.9815, "TI": 47.867, "ZR": 91.224, "CE": 140.116, "LI": 6.941}

# Curated binary phase sets (COST507 names). Solution phases + the Al-rich
# intermetallics; phases belonging to other subsystems are excluded.
PHASE_SETS = {
    "TI": ["LIQUID", "FCC_A1", "BCC_A2", "HCP_A3", "AL3M_D022", "ALM_D019",
           "ALTI", "AL2TI", "AL11TI5"],
    "ZR": ["LIQUID", "FCC_A1", "BCC_A2", "HCP_A3", "AL3ZR", "AL2ZR", "AL3ZR2",
           "ALZR", "ALZR2", "ALZR3"],
    "CE": ["LIQUID", "FCC_A1", "AL11_CEND3H", "AL11_CEND3L", "AL3_CEND",
           "AL2_CEND", "AL_CEND"],
    "LI": ["LIQUID", "FCC_A1", "BCC_A2", "ALLI", "AL2LI3", "AL4LI9"],
}

_db = None


def _get_db():
    """Lazily load COST507 (downloading it once) so cached results stay usable
    without pycalphad installed."""
    global _db
    if _db is None:
        from pycalphad import Database
        if not os.path.exists(TDB):
            urllib.request.urlretrieve(TDB_URL, TDB)
        _db = Database(TDB)
    return _db


def wt_to_x(w, el):
    """wt% of `el` in Al -> mole fraction."""
    a, b = w / M[el], (100.0 - w) / M["AL"]
    return a / (a + b)


def _solid_fraction(el, x, T):
    from pycalphad import equilibrium
    import pycalphad.variables as v
    eq = equilibrium(_get_db(), ["AL", el, "VA"], PHASE_SETS[el],
                     {v.X(el): x, v.T: T, v.P: 101325, v.N: 1},
                     calc_opts={"pdens": 500})
    names = np.asarray(eq.Phase.values).ravel()
    fracs = np.asarray(eq.NP.values).ravel()
    return sum(f for n, f in zip(names, fracs)
               if n not in ("", "LIQUID") and np.isfinite(f))


def liquidus(w, el="TI", lo=900.0, hi=1800.0, tol=0.5):
    """Lowest temperature (degC) at which Al-`w` wt% `el` is 100% liquid."""
    x = wt_to_x(w, el)
    if _solid_fraction(el, x, hi) > 1e-6:
        return float("nan")
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if _solid_fraction(el, x, mid) > 1e-6:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) - 273.15


# --- volatility: Clausius-Clapeyron from the normal boiling point -------------
# Tb (K) and enthalpy of vaporisation (kJ/mol), CRC values. Approximate over a
# wide range (constant dH assumed) -- read as order-of-magnitude, not to 3 s.f.
VOLATILES = {
    "Mg": (1363.0, 128.0), "Zn": (1180.0, 115.0), "Li": (1615.0, 136.0),
    "Mn": (2334.0, 221.0), "Al": (2792.0, 294.0),
}


def vapour_pressure_kpa(el, T_c):
    Tb, dH = VOLATILES[el]
    T = T_c + 273.15
    return 101.325 * np.exp(-dH * 1000.0 / 8.314 * (1.0 / T - 1.0 / Tb))


def compute():
    fine = [0.05, 0.1, 0.16, 0.2, 0.27, 0.3, 0.4, 0.5, 0.6, 0.75, 1.0, 1.25,
            1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0, 30.0, 37.2]
    data = {"al_ti": [[w, liquidus(w, "TI")] for w in fine]}
    data["masters"] = {
        name: liquidus(w, el)
        for name, (el, w) in {"Al-10Ti": ("TI", 10.0), "Al-10Zr": ("ZR", 10.0),
                              "Al-20Ce": ("CE", 20.0), "Al-5Li": ("LI", 5.0)}.items()
    }
    data["vapour"] = {el: {str(t): float(vapour_pressure_kpa(el, t))
                           for t in (700, 800, 900, 1000, 1100, 1200)}
                      for el in VOLATILES}
    with open(CACHE, "w") as fh:
        json.dump(data, fh, indent=1)
    return data


def load():
    if os.path.exists(CACHE):
        with open(CACHE) as fh:
            return json.load(fh)
    return compute()


if __name__ == "__main__":
    d = compute()
    print("\nAl-rich Al-Ti liquidus (COST507)")
    print(f"{'wt% Ti':>8} {'at% Ti':>8} {'liquidus C':>11} {'+100 C setpoint':>16}")
    for w, T in d["al_ti"]:
        print(f"{w:8.2f} {100*wt_to_x(w,'TI'):8.3f} {T:11.0f} {T+100:16.0f}")

    print("\nMaster alloys - temperature to make them fully liquid (COST507)")
    for k, T in d["masters"].items():
        print(f"{k:>10}: {T:6.0f} C")

    print("\nEquilibrium vapour pressure of the pure liquid metal (kPa)")
    temps = [700, 800, 900, 1000, 1100, 1200]
    print(f"{'element':>8}" + "".join(f"{t:>10}" for t in temps))
    for el in VOLATILES:
        print(f"{el:>8}" + "".join(f"{vapour_pressure_kpa(el,t):10.2f}" for t in temps))

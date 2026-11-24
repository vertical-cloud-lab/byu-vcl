"""Fast thermodynamics for the twin: thousands of compositions a second, checked against pycalphad.

**Aluminium: a dilute multicomponent Scheil model.** Each solute i has a liquidus slope m_i (K per wt%) and a
partition coefficient k_i at the Al corner. During Scheil solidification its liquid concentration is
c_i (1 - f_s)^(k_i - 1), capped at its binary eutectic composition once the liquid reaches it (the eutectic takes up
the excess), and the temperature is T_m + sum_i m_i C_L,i. From that one curve the model reads the liquidus, the
freezing range to 98 % solid, Kou's crack index |dT/d(f_s^1/2)| over f_s^1/2 = 0.87-0.94 (Kou, Acta Mater. 88, 2015),
the liquid left when the first eutectic starts (back-filling), and the growth-restriction factor
Q = sum m_i c_i (k_i - 1) (Easton & StJohn, Metall. Mater. Trans. A 30, 1999). Peritectic formers (Zr, Ti, Cr) and
hypereutectic Sc form a primary intermetallic above their invariant composition; its liquidus is
T_inv + A (c - w_inv)^n, fitted to pycalphad (COST 507 for Al-Zr, MatCalc mc_al for the rest; data in ``AL_PRIMARY``).

Two parameter sets, which is where the simulator's blind spots come from:

* ``truth``: the assessed binary diagrams (Easton & StJohn's table; Al-Sc, Al-Li, Al-Ce, Al-Er from the diagrams;
  Zn and Sn from the databases, which agree with the diagrams) and COST 507's primary Al3Zr.
* ``open``: what pycalphad on the open databases gives (``data/al_dilute.json``, computed by
  ``python3 -m twin.calphad al-dilute``). MatCalc mc_al puts Zr's and Sc's partition coefficients on the wrong side
  of 1, gives Ni a k twenty times too large, has no primary Al3Zr below 1 wt% Zr, and no database here has Er at all
  (the open node treats Er as absent). These are the open-CALPHAD node's errors in the twin; they are the databases'
  own, found on this runner, not invented.

**Copper: an emulator of pycalphad equilibrium (MatCalc mc_ni).** ``data/cu_calphad.json`` holds equilibrium
liquidus, solidus and phase amounts (alpha, beta, kappa) at 1000-700 degC for ~480 Sobol compositions of the ONR
space (``python3 -m twin.calphad cu-design``). A radial-basis-function interpolant over them is the ``open`` view;
``truth`` adds the database's known errors against the handbook (DAL PR 117 pycalphad-cu/README.md: the NAB liquidus
51 degC too high, 90-10 Cu-Ni 18 degC too low).
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
AL_TM_C = 660.32

# k, m (K/wt%), source. Easton & StJohn 1999, Table I, unless noted.
AL_TRUTH = {
    "Ti": (7.8, 33.3, "Easton & StJohn 1999"), "Zr": (2.5, 4.5, "Easton & StJohn 1999"),
    "Cr": (2.0, 3.5, "Easton & StJohn 1999"), "Si": (0.11, -6.6, "Easton & StJohn 1999"),
    "Ni": (0.007, -3.3, "Easton & StJohn 1999"), "Mg": (0.51, -6.2, "Easton & StJohn 1999"),
    "Fe": (0.02, -3.0, "Easton & StJohn 1999"), "Cu": (0.17, -3.4, "Easton & StJohn 1999"),
    "Mn": (0.94, -1.6, "Easton & StJohn 1999"),
    "Sc": (0.69, -9.9, "Al-Sc diagram: eutectic 0.55 wt% at 655 degC, max solubility 0.38 wt%"),
    "Li": (0.48, -7.3, "Al-Li diagram: eutectic about 8.3 wt% at 600 degC, max solubility about 4 wt% (approx.)"),
    "Ce": (0.002, -1.9, "Al-Ce diagram: eutectic about 10-12 wt% at 640 degC, negligible solubility (approx.)"),
    "Er": (0.02, -0.9, "Al-Er diagram: eutectic about 6 wt% at 655 degC (approx.)"),
    "Zn": (0.42, -1.65, "pycalphad, MatCalc mc_al (agrees with the Al-Zn diagram's slope)"),
    "Sn": (0.036, -1.47, "pycalphad, COST 507"),
}
# binary eutectics (wt%, degC) that cap a solute's liquid concentration; peritectic formers have none
AL_EUTECTIC = {"Si": (12.6, 577.0), "Cu": (33.2, 548.0), "Mg": (35.0, 450.0), "Zn": (94.9, 382.0),
               "Fe": (1.8, 655.0), "Mn": (1.9, 658.0), "Ni": (6.1, 640.0), "Ce": (11.0, 640.0),
               "Sc": (0.55, 655.0), "Er": (6.0, 655.0), "Li": (8.3, 600.0), "Sn": (99.5, 228.0)}
# solute content (mass fraction) of the second phase each eutectic forms: Si, Al2Cu, Al3Mg2, (Zn), Al13Fe4, Al6Mn,
# Al3Ni, Al11Ce3, Al3Sc, Al3Er, AlLi, (Sn)
AL_EUT_PHASE_X = {"Si": 1.0, "Cu": 0.53, "Mg": 0.37, "Zn": 1.0, "Fe": 0.40, "Mn": 0.25, "Ni": 0.42, "Ce": 0.68,
                  "Sc": 0.36, "Er": 0.67, "Li": 0.20, "Sn": 1.0}
# primary intermetallic above the invariant: (w_inv wt%, T_inv degC, A, n, phase, potency as an Al nucleant,
# source of the fit). potency: Al3Sc best (smallest misfit), then Al3Zr, Al3Er, Al3Ti; others are not nucleants.
AL_PRIMARY = {
    "Zr": (0.11, 660.8, 248.0, 0.56, "Al3Zr", 1.0, "pycalphad COST 507: 759/833/893 degC at 0.3/0.6/1.0 wt%"),
    "Sc": (0.55, 655.0, 141.0, 0.18, "Al3Sc", 1.6, "pycalphad mc_al: 737/765 degC at 0.6/0.8 wt%"),
    "Ti": (0.15, 665.0, 252.0, 0.74, "Al3Ti", 0.5, "pycalphad mc_al: 727/781 degC at 0.3/0.5 wt%"),
    "Cr": (0.41, 661.0, 52.5, 0.72, "Al13Cr2", 0.0, "pycalphad mc_al: 697/765 degC at 1/3 wt%"),
    "Mn": (1.9, 658.0, 4.15, 1.98, "Al6Mn", 0.0, "pycalphad mc_al: 663/697 degC at 3/5 wt%"),
    "Fe": (1.8, 655.0, 40.0, 1.0, "Al13Fe4", 0.0, "pycalphad mc_al: 663 degC at 2 wt%"),
    "Er": (6.0, 655.0, 30.0, 1.0, "Al3Er", 0.6, "assumed"),
}
# Under LPBF's cooling, Al3(Sc,Zr,Er) nucleates from a supersaturated melt below the equilibrium invariant
# (Spierings et al. 2017; Martin et al. 2017): the threshold the truth uses, wt%.
LPBF_NUCLEANT_THRESHOLD = {"Zr": 0.25, "Sc": 0.25, "Er": 0.3, "Ti": 0.3}


def _open_params() -> dict:
    """k, m from pycalphad on the open databases (data/al_dilute.json); Er missing."""
    p = DATA / "al_dilute.json"
    out = {}
    if p.exists():
        d = json.loads(p.read_text())
        for el, r in d["solutes"].items():
            e = el.capitalize()
            if "k" in r and "error" not in r and "binary diagram" not in r.get("db", ""):
                out[e] = (float(r["k"]), float(r["m_K_per_wt"]), f"pycalphad {r['db']}")
    # Sc: the probe found no field at 0.2 wt% with 0.1 K steps; the fine scan (0.01 K) gave k 1.34, m +1.5
    out.setdefault("Sc", (1.34, 1.50, "pycalphad mc_al, fine scan (twin/calphad.py notes)"))
    out.setdefault("Li", (0.87, -0.23, "pycalphad COST 507 (no Li in its FCC_A1: unreliable)"))
    return out


class AlSolidification:
    """Dilute multicomponent Scheil for Al alloys. kind: 'truth' or 'open'."""

    FS = np.concatenate([np.linspace(0, 0.9, 181), np.linspace(0.9, 0.995, 96)[1:]])

    def __init__(self, kind: str = "truth"):
        self.kind = kind
        self.params = dict(AL_TRUTH) if kind == "truth" else _open_params()

    def run(self, wt: dict) -> dict:
        fs = self.FS
        T = np.full_like(fs, AL_TM_C)
        first_eut = 1.0
        eut_phase = 0.0
        eut_by = {}
        Q = 0.0
        used = {}
        for el, c in wt.items():
            if el == "Al" or c <= 0:
                continue
            if el not in self.params:            # the open databases have no Er
                continue
            k, m, _ = self.params[el]
            used[el] = c
            c_eff = c
            prim = AL_PRIMARY.get(el)
            if self.kind == "truth" and prim and c > prim[0] and prim[0] < AL_EUTECTIC.get(el, (1e9,))[0]:
                c_eff = prim[0]                  # the primary intermetallic takes the excess
            if self.kind == "truth" and el == "Sc" and c > AL_EUTECTIC["Sc"][0]:
                c_eff = AL_EUTECTIC["Sc"][0]
            cl = c_eff * np.power(np.maximum(1 - fs, 1e-6), k - 1.0)
            cap = AL_EUTECTIC.get(el)
            if cap and k < 1:
                hit = cl >= cap[0]
                if hit.any():
                    f_on = float(fs[np.argmax(hit)])
                    first_eut = min(first_eut, f_on)
                    # lever rule: the liquid left at the eutectic, times the eutectic's second-phase share
                    share = (1.0 - f_on) * cap[0] / AL_EUT_PHASE_X.get(el, 1.0) / 100.0
                    eut_phase += share
                    eut_by[el] = share
                cl = np.minimum(cl, cap[0])
            T += m * cl
            Q += m * c_eff * (k - 1.0)
        # the liquid's temperature cannot fall below the lowest eutectic among the solutes it carries (minus a
        # few K for a multicomponent eutectic)
        floors = [AL_EUTECTIC[e][1] for e in used if e in AL_EUTECTIC]
        if floors:
            T = np.maximum(T, min(floors) - 10.0 * (len(floors) - 1))
        TL_alpha = float(T[0])
        TL = TL_alpha
        primary = {}
        if self.kind == "truth":
            for el, c in used.items():
                p = AL_PRIMARY.get(el)
                if p and c > p[0]:
                    t = p[1] + p[2] * (c - p[0]) ** p[3]
                    primary[el] = dict(phase=p[4], T_C=t, excess_wt=c - p[0])
                    TL = max(TL, t)
        i98 = int(np.searchsorted(fs, 0.98))
        T98 = float(T[min(i98, len(T) - 1)])
        r = np.sqrt(fs)
        sel = (r >= 0.87) & (r <= 0.94)
        csi = float(abs(np.polyfit(r[sel], T[sel], 1)[0]))
        # nucleants for LPBF: wt% of Al3(Sc,Zr,Er,Ti) formers above the LPBF threshold, weighted by potency
        nuc = 0.0
        if self.kind == "truth":
            for el, thr in LPBF_NUCLEANT_THRESHOLD.items():
                c = used.get(el, 0.0)
                if c > thr:
                    nuc += AL_PRIMARY[el][5] * (c - thr)
        return dict(T_liquidus_C=TL, T_alpha_liquidus_C=TL_alpha, T_98_C=T98, freezing_range_K=TL_alpha - T98,
                    kou_index_K=csi, liquid_at_first_eutectic=1.0 - first_eut, eutectic_phase_frac=min(eut_phase, 0.5), eutectic_by=eut_by,
                    Q_K=Q, nucleant_wt=nuc,
                    primary=primary, elements_seen=sorted(used))


# ------------------------------------------------------------------------------------------------------------- copper
CU_KEYS = ["liquidus_C", "solidus_C", "beta_1000", "beta_900", "beta_800", "kappa_700", "alpha_700", "beta_lowest_C"]
CU_ORDER = ["Ni", "Al", "Fe", "Mn", "Cr", "Si", "Nb", "Ti"]
CU_SCALE = np.array([30.0, 9.5, 4.5, 4.0, 0.7, 0.5, 0.8, 0.5])


def _cu_rows():
    d = json.loads((DATA / "cu_calphad.json").read_text())
    X, Y = [], []
    for p in d["points"]:
        if "error" in p or not np.isfinite(p.get("liquidus_C", np.nan)) or not np.isfinite(p.get("solidus_C", np.nan)):
            continue
        w = p["wt"]
        X.append([w.get(e.upper(), 0.0) for e in CU_ORDER])
        ph = p["phases"]

        def g(t, key):
            return (ph.get(t) or {}).get(key, 0.0) or 0.0
        bl = p["beta_lowest_C"] if np.isfinite(p.get("beta_lowest_C", np.nan)) else 600.0
        Y.append([p["liquidus_C"], p["solidus_C"], g("1000", "beta"), g("900", "beta"), g("800", "beta"),
                  g("700", "kappa"), g("700", "alpha"), bl])
    return np.array(X), np.array(Y)


@lru_cache(maxsize=1)
def _cu_model():
    from scipy.interpolate import RBFInterpolator
    X, Y = _cu_rows()
    Xn = X / CU_SCALE
    return RBFInterpolator(Xn, Y, kernel="thin_plate_spline", smoothing=1e-3, degree=1), len(X)


def cu_holdout(frac=0.15, seed=0) -> dict:
    """RMSE of the emulator on held-out pycalphad points (the emulator's own error, reported in notes/twin.md)."""
    from scipy.interpolate import RBFInterpolator
    X, Y = _cu_rows()
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(X))
    n = int(frac * len(X))
    te, tr = idx[:n], idx[n:]
    f = RBFInterpolator(X[tr] / CU_SCALE, Y[tr], kernel="thin_plate_spline", smoothing=1e-3, degree=1)
    P = f(X[te] / CU_SCALE)
    rmse = np.sqrt(np.mean((P - Y[te]) ** 2, axis=0))
    return dict(n_train=len(tr), n_test=n, rmse=dict(zip(CU_KEYS, [round(float(v), 4) for v in rmse])))


class CuThermo:
    """kind 'open': the mc_ni emulator. 'truth': the emulator corrected to the handbook where DAL found the database
    off (NAB liquidus 51 degC high, 90-10 Cu-Ni 18 degC low)."""

    def __init__(self, kind: str = "truth"):
        self.kind = kind

    def run(self, wt: dict) -> dict:
        f, _ = _cu_model()
        x = np.array([[wt.get(e, 0.0) for e in CU_ORDER]]) / CU_SCALE
        y = f(x)[0]
        out = dict(zip(CU_KEYS, [float(v) for v in y]))
        for k in ("beta_1000", "beta_900", "beta_800", "kappa_700", "alpha_700"):
            out[k] = float(np.clip(out[k], 0.0, 1.0))
        if self.kind == "truth":
            al, ni = wt.get("Al", 0.0), wt.get("Ni", 0.0)
            out["liquidus_C"] += -51.0 * min(al / 9.2, 1.2) + 18.0 * math.exp(-((ni - 10.0) / 12.0) ** 2)
            out["solidus_C"] += 7.0 * min(al / 9.2, 1.2) - 5.0 * math.exp(-((ni - 10.0) / 12.0) ** 2)
            out["solidus_C"] = min(out["solidus_C"], out["liquidus_C"] - 3.0)
        out["freezing_range_K"] = out["liquidus_C"] - out["solidus_C"]
        return out

"""Liquidus of Al-y M binary master alloys versus y (issue #161, 2026-10-07).

Companion to design_space_reachability.py: that script gives the *minimum* non-Al fraction
y a master alloy needs so the design space stays reachable; this one gives the *maximum*
y we can make or re-melt in-house, from the binary liquidus:

  * liquidus + 100 C superheat <= 1300 C  -> the master can be melted and atomized on the
    rePOWDER induction module (make master-alloy *powder* in-house, or re-melt it);
  * otherwise it needs the arc melter (#223), after which it is dosed as crushed pieces
    (brittle, intermetallic-rich masters) or as lumps.

Uses pycalphad with the public COST507 light-alloy database (same copy and download path
as al_ti_melt_window.py) for Ti, Zr, Ce, Li, Mg, Mn, Cr, Fe, Si, Cu, Zn, Sn and the Dupin,
Ansara & Sundman (2001) Al-Ni assessment (al_ni_phase_diagram.py) for Ni. Sc and Er are not
in COST507; their liquidus values are taken from the assessed diagrams in the report.

One equilibrium call per composition over a temperature grid (20 K steps), so the liquidus
is resolved to +/-10 C -- enough to place a master on the right side of the 1300 C line.

    python master_alloy_liquidus.py            # writes master-alloy-liquidus-data.json
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import al_ti_melt_window as mw  # noqa: E402  (COST507 download + path)
import al_ni_phase_diagram as ni  # noqa: E402  (Dupin 2001 Al-Ni TDB)

OUT = os.path.join(HERE, "master-alloy-liquidus-data.json")

MOLAR_MASS = {"AL": 26.9815, "TI": 47.867, "ZR": 91.224, "CE": 140.116, "LI": 6.941,
              "MG": 24.305, "MN": 54.938, "CR": 51.996, "FE": 55.845, "SI": 28.085,
              "CU": 63.546, "ZN": 65.38, "SN": 118.71, "NI": 58.693}

# y grid (wt.% of the solute in the master), chosen to bracket the commercial grades and
# the reachability floors.
Y_GRID = [2, 5, 10, 15, 20, 30, 50]

T_GRID_K = np.arange(600 + 273.15, 1800 + 273.15 + 1, 20.0)
INDUCTION_LIMIT_C = 1300.0
SUPERHEAT_C = 100.0


def wt_to_x(w, el):
    a, b = w / MOLAR_MASS[el], (100.0 - w) / MOLAR_MASS["AL"]
    return a / (a + b)


def binary_phases(db, el):
    """Phases that can exist with only {AL, el, VA}: every sublattice admits at least one
    species made of those components (pycalphad's filter_phases rule, written out so it
    does not depend on the pycalphad version)."""
    allowed = {"AL", el, "VA"}
    keep = []
    for name, ph in db.phases.items():
        if name == "GAS" or "AMORPHOUS" in name:
            continue  # not relevant to a liquidus at 1 atm
        if all(any(set(sp.constituents).issubset(allowed) for sp in subl)
               for subl in ph.constituents):
            keep.append(name)
    return sorted(keep)


def liquidus_from_sweep(db, phases, el, w):
    from pycalphad import equilibrium
    import pycalphad.variables as v
    x = wt_to_x(w, el)
    eq = equilibrium(db, ["AL", el, "VA"], phases,
                     {v.X(el): x, v.T: T_GRID_K, v.P: 101325, v.N: 1},
                     calc_opts={"pdens": 400})
    names = np.asarray(eq.Phase.values)   # (..., T, vertex)
    fracs = np.asarray(eq.NP.values)
    names = names.reshape(len(T_GRID_K), -1)
    fracs = fracs.reshape(len(T_GRID_K), -1)
    solid = np.array([
        sum(f for n, f in zip(nn, ff) if n not in ("", "LIQUID") and np.isfinite(f))
        for nn, ff in zip(names, fracs)
    ])
    liquid_idx = np.where(solid <= 1e-6)[0]
    if len(liquid_idx) == 0:
        return float("nan")
    # first temperature at which everything above is liquid too
    k = liquid_idx[0]
    while k + 1 < len(solid) and (solid[k:] > 1e-6).any():
        k = np.where(solid > 1e-6)[0].max() + 1
        break
    return float(T_GRID_K[k] - 273.15)


def main():
    from pycalphad import Database
    cost = mw._get_db()
    nidb = Database(ni._tdb_path())
    results = {"T_step_C": 20.0, "induction_limit_C": INDUCTION_LIMIT_C,
               "superheat_C": SUPERHEAT_C, "liquidus_C": {}, "sources": {
                   "COST507": "Ansara/Dinsdale/Rand EUR 18499 (corrected copy, see al_ti_melt_window.py)",
                   "NI": "Dupin, Ansara & Sundman, Calphad 25 (2001) 279"}}
    elements = ["TI", "ZR", "CE", "LI", "MG", "MN", "CR", "FE", "SI", "CU", "ZN", "SN", "NI"]
    for el in elements:
        db = nidb if el == "NI" else cost
        try:
            phases = binary_phases(db, el)
        except Exception as e:  # noqa: BLE001
            print(el, "phase filter failed:", e, flush=True)
            continue
        row = {}
        t0 = time.time()
        for w in Y_GRID:
            try:
                row[str(w)] = liquidus_from_sweep(db, phases, el, float(w))
            except Exception as e:  # noqa: BLE001
                row[str(w)] = None
                print(el, w, "failed:", str(e)[:120], flush=True)
        results["liquidus_C"][el] = row
        print(f"{el}: " + ", ".join(f"{w}%: {row[str(w)]}" for w in Y_GRID)
              + f"   ({time.time()-t0:.0f} s)", flush=True)
        with open(OUT, "w") as fh:
            json.dump(results, fh, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()

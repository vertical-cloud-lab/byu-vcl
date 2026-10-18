"""Arithmetic checks on numbers in the batch-1 Edison answers, and the few
numbers the synthesis in README.md adds. Writes check_numbers.json.

Run from the repo root: python alloy-corrosion/copper-ded-edison/check_numbers.py
"""

import json
import math
import pathlib

F = 96485.0            # C/mol
D_O2 = 2.0e-5          # cm2/s, O2 in seawater near 20-25 C
C_O2 = 0.25e-6         # mol/cm3 (0.25 mM), air-saturated water, as c1-01 assumes
WELL_UL = 150.0        # uL per well
AREAS = (0.07, 0.13)   # cm2, 3-4 mm O-ring wells

out = {}

# c1-10: charge to reduce 1 nm of oxide, Q/A = n F rho d / M
for name, rho, molar, n, edison in (("Cu2O", 6.0, 143.09, 2, 0.81),
                                     ("CuO", 6.31, 79.55, 2, 2.1)):
    mc_per_nm = n * F * rho * 1e-7 / molar * 1e3
    out[f"{name}_mC_per_cm2_per_nm"] = {
        "computed": round(mc_per_nm, 3), "edison_c1_10": edison,
        "agrees": abs(mc_per_nm - edison) / edison < 0.05}
cu2o = out["Cu2O_mC_per_cm2_per_nm"]["computed"]
out["Cu2O_1nm_uC_per_well"] = [round(cu2o * a * 1e3, 1) for a in AREAS]
out["Cu2O_1nm_seconds_at_25uA_cm2"] = round(cu2o * 1e-3 / 25e-6, 1)

# c1-01: O2 held by one well, and how long it lasts at a given cathodic current
o2_mol = C_O2 * WELL_UL * 1e-3
o2_mC = 4 * F * o2_mol * 1e3
out["O2_inventory_nmol"] = round(o2_mol * 1e9, 1)
out["O2_inventory_mC_4e"] = round(o2_mC, 2)
# c1-01 says 24 min at 10 uA and 48 min at 5 uA total, and calls that
# "typical Cu-Ni corrosion currents". On a 0.07-0.13 cm2 spot those are
# 38-143 uA/cm2. Fresh Cu-Ni and NAB icorr in the answers is 1-11 uA/cm2.
out["O2_inventory_minutes"] = {
    f"{i_ua_cm2}uA_cm2_on_{a}cm2": round(o2_mC * 1e-3 / (i_ua_cm2 * 1e-6 * a) / 60)
    for i_ua_cm2 in (1, 5, 11) for a in AREAS}
out["c1_01_total_currents_as_uA_cm2"] = {
    f"{i_ua}uA": [round(i_ua / a) for a in AREAS] for i_ua in (5, 10)}
# The O2 that runs short is at the metal, not in the well: in still liquid the
# diffusion-limited O2 current falls as the depleted layer grows (Cottrell).
out["O2_limiting_uA_cm2_still_liquid"] = {
    f"{m}min": round(4 * F * C_O2 * math.sqrt(D_O2 / (math.pi * m * 60)) * 1e6, 1)
    for m in (1, 5, 30, 60)}
# Same current in a bulk cell whose natural convection holds the layer at 0.2-0.5 mm
out["O2_limiting_uA_cm2_bulk_delta_0p2_to_0p5mm"] = [
    round(4 * F * D_O2 * C_O2 / (d * 0.1) * 1e6) for d in (0.2, 0.5)]
# During a polarization the counter reduces O2 at the full cell current
out["O2_inventory_seconds_at_reversal_current"] = {
    f"{j}mA_cm2_on_{a}cm2": round(o2_mC * 1e-3 / (j * 1e-3 * a))
    for j in (1, 10) for a in AREAS}

# c1-01 (d): acid or base made by the counter, per mC, in one well
out["counter_mM_per_mC_in_150uL"] = round(1e-3 / F / (WELL_UL * 1e-6) * 1e3, 4)

# c1-01 (c): chloride rise when water evaporates
out["chloride_rise_pct_for_loss_uL"] = {
    str(v): round((WELL_UL / (WELL_UL - v) - 1) * 100) for v in (15, 30, 50)}

# c1-06: half-life implied by "10 mg/L fell to 1.2 mg/L in 1 day" (it also quotes ~20 min)
out["sulfide_half_life_h_from_10_to_1p2_mg_L_in_24h"] = round(24 * math.log(2) / math.log(10 / 1.2), 1)

# c1-02: whole-spot current at the reversal thresholds in the answers
out["spot_current_uA_at_reversal"] = {
    f"{j}mA_cm2": [round(j * 1e3 * a) for a in AREAS] for j in (1, 3, 10)}
# Luo 2026's 1:50 NAB/duplex galvanic current density, on a CubXL spot
out["spot_current_uA_at_38uA_cm2"] = [round(38 * a, 1) for a in AREAS]

# c1-07: flow through a 1 mm nozzle at Metikos-Hukovic 2011's jet speeds
nozzle_cm2 = math.pi * 0.05 ** 2
out["nozzle_1mm_L_per_min"] = {
    str(v): round(v * 100 * nozzle_cm2 * 60 / 1000, 3) for v in (2.7, 6.4, 8.3)}

path = pathlib.Path(__file__).with_name("check_numbers.json")
path.write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))

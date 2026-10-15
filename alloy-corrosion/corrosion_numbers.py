"""Reproduce every computed number in this folder's README and protocol.

Run `python corrosion_numbers.py`; it prints a summary and writes corrosion_numbers.json.
Standard library only.

Inputs that are measured or specified elsewhere:
- Composition spread: the spec limits and 4047 fractions of the atomizer runs plan,
  atomizer-runs/plan-adv-mater/plan_numbers.py at cad4e6d (from PR #232).
- Mg2Si mass ratio from atomic masses (Mg 24.305, Si 28.086 g/mol).

Everything else is an assumption, labelled ASSUMED, to be replaced by measurement:
cell size, electrolyte volume, current densities, scan ranges and charges.
"""

import json
import math

F = 96485.332  # C/mol
M_AL, M_MG, M_SI = 26.982, 24.305, 28.086  # g/mol
MG_TO_SI_IN_MG2SI = 2 * M_MG / M_SI  # mass ratio of Mg to Si in Mg2Si, ~1.73

# --- Composition spread, copied from the atomizer runs plan (cad4e6d) ---
SPREAD_WT_PCT = [0.0, 7.5, 15.0, 22.5, 30.0]  # 4047 powder in the charge
SPEC = {  # wt%, (min, max); 4047 Mg minimum taken as 0, as in the plan
    "6063": {"Si": (0.20, 0.60), "Mg": (0.45, 0.90)},
    "4047": {"Si": (11.0, 13.0), "Mg": (0.0, 0.10)},
}

# --- Cell, ASSUMED: an FKM O-ring sets the exposed area, a wider bore above it holds the liquid ---
ORING_ID_MM = [3.0, 4.0, 5.0]
WELL_BORE_MM = 8.0
CELL_VOLUME_UL = 150.0
P20_MAX_UL, P20_MIN_UL = 20.0, 2.0

# --- Currents, ASSUMED ranges to size the potentiostat, not literature values ---
RP_OHM_CM2 = [1e4, 1e5, 1e6]  # polarization resistance, passive Al alloy in NaCl
LPR_AMPLITUDE_V = 0.010  # +/-10 mV around OCP (ASTM G59 uses a small window like this)
PIT_THRESHOLDS_A_CM2 = [10e-6, 100e-6]  # current density that defines E_pit
REVERSAL_A_CM2 = 1e-3  # reverse the scan here (ASTM G61 uses 5 mA/cm2; lowered for a small well)

# --- Charge passed in one cyclic polarization, ASSUMED ---
CHARGES_C = [1e-3, 10e-3, 100e-3]
ICP_MAX_TDS_FRAC = 0.002  # 0.2 % total dissolved solids, a common ICP-MS limit (ASSUMED)
NACL_G_PER_L_AT_0P6M = 0.6 * 58.44

# --- Reference electrode leak, ASSUMED 1 uL of its 3 M KCl filling into the well ---
KCL_FILL_M, KCL_LEAK_UL = 3.0, 1.0

# --- Chloride series mixed in the well from stocks, ASSUMED ---
STOCKS_M = [0.6, 0.06, 0.006]
TARGETS_M = [0.006, 0.01, 0.02, 0.06, 0.1, 0.2, 0.6]

# --- Time per spot, ASSUMED scan ranges ---
OCP_MIN = 30.0
CPP_START_BELOW_OCP_V = 0.050
CPP_UP_V, CPP_DOWN_V = 0.300, 0.400  # up to reversal, then back down to repassivation
RATES_V_S = {"ASTM G61 (0.6 V/h)": 0.6 / 3600, "screening (1 mV/s)": 1e-3}
NIGHT_H = 12.0


def area_cm2(d_mm):
    return math.pi * (d_mm / 10) ** 2 / 4


def spread():
    """Si, Mg and Si beyond what Mg2Si can bind, at spec midpoints and extremes."""
    rows = []
    for pct in SPREAD_WT_PCT:
        x = pct / 100
        comp = {}
        for el in ("Si", "Mg"):
            lo = (1 - x) * SPEC["6063"][el][0] + x * SPEC["4047"][el][0]
            hi = (1 - x) * SPEC["6063"][el][1] + x * SPEC["4047"][el][1]
            comp[el] = (lo, hi, (lo + hi) / 2)
        si_lo, si_hi, si_mid = comp["Si"]
        mg_lo, mg_hi, mg_mid = comp["Mg"]
        rows.append({
            "powder_wt_pct": pct,
            "Si_mid": round(si_mid, 2),
            "Mg_mid": round(mg_mid, 2),
            "Mg_over_Si_mid": round(mg_mid / si_mid, 2),
            # Si left over once all Mg is bound as Mg2Si; negative means Mg in excess
            "excess_Si_mid": round(si_mid - mg_mid / MG_TO_SI_IN_MG2SI, 2),
            "excess_Si_range": [round(si_lo - mg_hi / MG_TO_SI_IN_MG2SI, 2),
                                round(si_hi - mg_lo / MG_TO_SI_IN_MG2SI, 2)],
        })
    return rows


def currents():
    out = {}
    for d in ORING_ID_MM:
        a = area_cm2(d)
        out[f"{d:g} mm"] = {
            "area_cm2": round(a, 4),
            "lpr_current_nA": {f"{rp:.0e} ohm cm2": round(LPR_AMPLITUDE_V * a / rp * 1e9, 1)
                               for rp in RP_OHM_CM2},
            "pit_threshold_uA": {f"{t * 1e6:g} uA/cm2": round(t * a * 1e6, 2)
                                 for t in PIT_THRESHOLDS_A_CM2},
            "reversal_uA": round(REVERSAL_A_CM2 * a * 1e6, 1),
        }
    return out


def dissolution():
    """Al dissolved for a given charge (all anodic charge to Al3+), and what ICP sees."""
    v_l = CELL_VOLUME_UL * 1e-6
    min_dilution = NACL_G_PER_L_AT_0P6M / 1000 / ICP_MAX_TDS_FRAC
    rows = []
    for q in CHARGES_C:
        ug = q / (3 * F) * M_AL * 1e6
        mg_l = ug / 1000 / v_l
        rows.append({
            "charge_mC": q * 1e3,
            "Al_ug": round(ug, 2),
            "Al_mg_per_L_in_cell": round(mg_l, 1),
            "Al_ug_per_L_after_min_dilution": round(mg_l * 1000 / min_dilution, 0),
        })
    return {"min_dilution_for_0.6M_NaCl": round(min_dilution, 1), "rows": rows}


def counter_products():
    """OH- the counter electrode makes while the sample is anodic (one per electron),
    as a concentration in the cell if none of it were neutralised by the dissolving Al3+."""
    v_l = CELL_VOLUME_UL * 1e-6
    return {f"{q * 1e3:g} mC": round(q / F / v_l * 1e3, 2) for q in CHARGES_C}


def kcl_leak():
    added_mm = KCL_FILL_M * KCL_LEAK_UL / (CELL_VOLUME_UL + KCL_LEAK_UL) * 1000
    return {"added_chloride_mM": round(added_mm, 1),
            "vs_targets": {f"{c:g} M": f"+{added_mm / (c * 1000) * 100:.0f} %" for c in TARGETS_M}}


def mixing():
    """Volumes of two stocks that make each target chloride level in the well.

    A target equal to a stock uses that stock alone. Otherwise take the bracketing pair
    whose smaller volume is largest, and require every volume to be >= the P20 minimum.
    """
    rows = []
    for c in TARGETS_M:
        if c in STOCKS_M:
            parts = {c: CELL_VOLUME_UL}
        else:
            best = None
            for hi in STOCKS_M:
                for lo in STOCKS_M:
                    if not lo < c < hi:
                        continue
                    v_hi = CELL_VOLUME_UL * (c - lo) / (hi - lo)
                    pair = {hi: v_hi, lo: CELL_VOLUME_UL - v_hi}
                    if min(pair.values()) >= P20_MIN_UL and (
                            best is None or min(pair.values()) > min(best.values())):
                        best = pair
            parts = best
        if parts is None:
            rows.append({"target_M": c, "note": f"no stock pair keeps both volumes >= {P20_MIN_UL:g} uL"})
            continue
        rows.append({"target_M": c,
                     "stocks_uL": {f"{s:g} M": round(v, 1) for s, v in parts.items()},
                     "p20_transfers": sum(math.ceil(v / P20_MAX_UL) for v in parts.values())})
    return rows


def timing():
    lpr_s = 2 * LPR_AMPLITUDE_V / RATES_V_S["ASTM G61 (0.6 V/h)"]
    out = {}
    for name, r in RATES_V_S.items():
        cpp_s = (CPP_START_BELOW_OCP_V + CPP_UP_V + CPP_DOWN_V) / r
        spot_min = OCP_MIN + lpr_s / 60 + cpp_s / 60
        out[name] = {"lpr_min": round(lpr_s / 60, 1), "cpp_min": round(cpp_s / 60, 1),
                     "spot_min": round(spot_min, 0),
                     "spots_per_night": int(NIGHT_H * 60 // spot_min)}
    return out


def main():
    out = {
        "mg_to_si_in_mg2si": round(MG_TO_SI_IN_MG2SI, 3),
        "spread": spread(),
        "currents": currents(),
        "dissolution": dissolution(),
        "counter_OH_mM_if_unneutralised": counter_products(),
        "kcl_leak": kcl_leak(),
        "mixing": mixing(),
        "timing": timing(),
        "p20_transfers_to_fill_cell": math.ceil(CELL_VOLUME_UL / P20_MAX_UL),
        "well_bore_uL_per_mm": round(math.pi * (WELL_BORE_MM / 2) ** 2, 1),
    }

    print(f"Mg:Si mass ratio in Mg2Si = {out['mg_to_si_in_mg2si']}")
    print("\nComposition spread (spec midpoints; excess Si = Si not bound as Mg2Si)")
    for r in out["spread"]:
        print(f"  {r['powder_wt_pct']:4.1f} wt% 4047: Si {r['Si_mid']:.2f}, Mg {r['Mg_mid']:.2f}, "
              f"Mg/Si {r['Mg_over_Si_mid']:.2f}, excess Si {r['excess_Si_mid']:+.2f} "
              f"(range {r['excess_Si_range'][0]:+.2f} to {r['excess_Si_range'][1]:+.2f}) wt%")
    print("\nCurrents by O-ring inner diameter")
    for k, v in out["currents"].items():
        print(f"  {k}: {v['area_cm2']} cm2; LPR at +/-10 mV {v['lpr_current_nA']} nA; "
              f"E_pit threshold {v['pit_threshold_uA']} uA; reversal {v['reversal_uA']} uA")
    d = out["dissolution"]
    print(f"\nDissolved Al in {CELL_VOLUME_UL:g} uL (0.6 M NaCl needs >= {d['min_dilution_for_0.6M_NaCl']}x dilution for ICP)")
    for r in d["rows"]:
        print(f"  {r['charge_mC']:g} mC -> {r['Al_ug']} ug Al, {r['Al_mg_per_L_in_cell']} mg/L in the cell, "
              f"{r['Al_ug_per_L_after_min_dilution']:.0f} ug/L after dilution")
    print(f"OH- from the counter electrode, mM in the cell if nothing neutralised it: {out['counter_OH_mM_if_unneutralised']}")
    k = out["kcl_leak"]
    print(f"\n{KCL_LEAK_UL:g} uL of {KCL_FILL_M:g} M KCl into {CELL_VOLUME_UL:g} uL adds {k['added_chloride_mM']} mM Cl-: {k['vs_targets']}")
    print("\nChloride series mixed in the well")
    for r in out["mixing"]:
        print("  ", r)
    print(f"\nFilling one cell takes {out['p20_transfers_to_fill_cell']} P20 transfers; "
          f"the {WELL_BORE_MM:g} mm bore holds {out['well_bore_uL_per_mm']} uL per mm")
    print("\nTime per spot (OCP 30 min + LPR + cyclic polarization)")
    for k2, v in out["timing"].items():
        print(f"  {k2}: LPR {v['lpr_min']} min, CPP {v['cpp_min']} min, spot {v['spot_min']:.0f} min, "
              f"{v['spots_per_night']} spots per {NIGHT_H:g} h night")

    with open("corrosion_numbers.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()

"""Reproduce every computed number in this folder's protocol.md (the copper version).

Run `python copper_numbers.py` from any directory; it prints a summary and writes
copper_numbers.json next to this file. Standard library only.

Inputs that are measured or specified elsewhere:
- O-ring sizes: the AS568 dash-number table (-006, -008, -010, all 1.78 mm cross-section).
- Copper release rates of 90/10 Cu-Ni: Earley et al. 2020, as read in Edison answer c1-03.
- Cu detection limit of their ICP-MS method, 0.13 ug/L: the same answer.
- Copper in ASTM D1141's heavy-metal stock (No. 3): 0.396 g Cu(NO3)2.3H2O in 10 L of stock,
  10 mL of stock per 10 L of substitute ocean water. Read from copies of the standard found by
  search on 2026-10-18, not from ASTM's own text: check it against the standard before relying
  on it.

Everything else is an assumption, labelled ASSUMED, to be replaced by measurement:
volumes, tolerances, Tafel slopes, corrosion currents, timings.
"""

import json
import math
import pathlib

F = 96485.332  # C/mol
M = {"Cu": 63.546, "Ni": 58.693, "Al": 26.982, "Fe": 55.845, "Mn": 54.938, "S": 32.06}
CHARGE = {"Cu(I)": ("Cu", 1), "Cu(II)": ("Cu", 2), "Ni(II)": ("Ni", 2), "Al(III)": ("Al", 3),
          "Fe(II)": ("Fe", 2), "Mn(II)": ("Mn", 2)}

# --- Wells: AS568 FKM O-rings. The wetted area is set by the inner diameter. ---
ORINGS_MM = {"-006": 2.90, "-008": 4.47, "-010": 6.07}  # inner diameters
ORING_CS_MM = 1.78
LID_BORE_MM = {"-006": 8.0, "-008": 10.0, "-010": 12.0}  # ASSUMED: bore above the O-ring step
WELL_UL = 150.0            # ASSUMED, as in the Al plan
RINSE_UL = 150.0           # ASSUMED: one DI rinse collected with the liquid
PLACEMENT_TOL_MM = 0.5     # ASSUMED: piece-to-lid placement tolerance by hand in the tray pocket

# --- Cap seal: the electrode cap seals the bore above the liquid, with a pinhole vent ---
HEADSPACE_UL = 80.0        # ASSUMED: bore above the meniscus plus the cap's own cavity
O2_AIR_FRAC = 0.2095
MOLAR_GAS_L = 24.1         # L/mol at 21 C, 1 atm
C_O2_MM = 0.25             # mM, air-saturated, as c1-01 and ../copper-ded-edison/check_numbers.py assume
VENT_D_MM, VENT_L_MM = 0.3, 3.0   # ASSUMED pinhole vent through the cap top
D_WATER_AIR = 0.25         # cm2/s, water vapour in air near 20-25 C
SAT_VAPOUR_G_CM3 = 19.4e-6  # g/cm3 at 22 C
LAB_RH = 0.40              # ASSUMED lab relative humidity

# --- Electrolyte ---
P20_MAX_UL, MIN_TRANSFER_UL = 20.0, 15.0  # the P20 goes down to 2 uL; 15 uL is this plan's floor
SULFIDE_STOCKS_MG_L = [10.0, 0.1]         # ASSUMED stocks, mg/L S as Na2S, made up in the same ASW
SULFIDE_TARGETS_MG_L = [0.0, 0.01, 0.1, 1.0, 10.0]  # c1-06's series
D1141_STOCK3_CUNO3_G_PER_10L = 0.396      # see the docstring
D1141_STOCK3_ML_PER_10L = 10.0
M_CUNO3_3H2O = 241.60                     # g/mol
ASW_ALKALINITY_MM = 2.4                   # ASSUMED, seawater-like; D1141 adds NaHCO3

# --- Acid at collection ---
ACID_UL, ACID_M = 20.0, 1.0               # ASSUMED: 20 uL of 1 M trace-metal HNO3 per tube

# --- ICP-MS ---
EARLEY_UG_CM2_DAY = {"initial, high": 200.0, "initial, low": 100.0,
                     "30 d mesh": 3.9, "30 d sheet": 1.4}  # 90/10 Cu-Ni, natural seawater (c1-03)
ICP_DILUTION = 10.0                       # c1-03: 5-10x before ICP-MS
CU_MDL_UG_L = 0.13                        # Earley 2020's method detection limit (c1-03)
ASW_TDS_G_L = 35.0                        # seawater salinity, ASSUMED for D1141
ICP_MAX_TDS_G_L = 2.0                     # ASSUMED 0.2 % total dissolved solids, as ../corrosion_numbers.py

# --- Currents and charges ---
LPR_AMPLITUDE_V = 0.010
RP_OHM_CM2 = [400.0, 1000.0, 8000.0, 50000.0]
# 0.4-1.3 kOhm cm2 under a jet and 6-8 kOhm cm2 in still liquid (c1-07); 50 kOhm cm2 is of the
# order of the film resistance Song 2024 fits for 70/30 WAAM (c1-05), used only as an upper bound.
ICORR_UA_CM2 = [1.0, 5.0, 11.0]           # fresh Cu-Ni and NAB range (c1-01 correction, c1-06)
TAFEL_A_V, TAFEL_C_V = 0.060, 0.120       # ASSUMED anodic (CuCl2- transport) and cathodic slopes
HOLD_MV, HOLD_MIN = 50.0, 10.0            # ASSUMED anodic hold above OCP and its length
HOLD_CHARGE_CAP_MC = 3.0                  # ASSUMED charge budget per hold
REVERSALS_MA_CM2 = [1.0, 10.0]            # 1 = the Al plan; 10 = Shahriari 2023 (c1-02)
SCAN_V_S = {"1 mV/s": 1e-3, "0.167 mV/s (0.6 V/h)": 0.6 / 3600}

# --- Bench calibration cell, galvanic couples, oxide coulometry ---
BULK_AREA_CM2, BULK_ML = 1.0, 200.0       # c1-01's comparison cell
GALVANIC_UA_CM2 = {"Luo 2026 NAB/duplex 1:50, at the start (c1-02)": 38.0,
                   "Xing 2023 90/10 HAZ vs weld, at the start (c1-04)": 4.43}
OXIDE_MC_CM2_PER_NM = {"Cu2O": 0.81, "CuO": 1.53}  # ../copper-ded-edison/check_numbers.json

# --- Timing, ASSUMED (protocol section 4) ---
STEPS_MIN = {"fill": 4, "leak check": 2, "cap on": 1, "OCP": 30, "LPR": 2, "rest": 5,
             "anodic hold": HOLD_MIN, "OCP after hold": 5, "decap and rinse cap": 1,
             "collect and acidify": 6, "image": 1}
WELLS_PER_NIGHT = 8   # 3 pieces x (main + companion) + fixture blank + carry-over blank
NIGHT_H = 12.0
# Liquid contact, first fill drop to collection: every step up to the decap, plus half the collection
CONTACT_MIN = sum(v for k, v in STEPS_MIN.items() if k not in ("collect and acidify", "image")) \
    + STEPS_MIN["collect and acidify"] / 2


def area_cm2(d_mm):
    return math.pi * (d_mm / 20.0) ** 2


def wells():
    out = {}
    for dash, d in ORINGS_MM.items():
        a = area_cm2(d)
        bore = LID_BORE_MM[dash]
        out[dash] = {
            "id_mm": d, "cs_mm": ORING_CS_MM, "od_mm": round(d + 2 * ORING_CS_MM, 2),
            "area_cm2": round(a, 4),
            "volume_to_area_mL_cm2": round(WELL_UL / 1000 / a, 2),
            "lid_bore_mm": bore,
            "bore_uL_per_mm": round(math.pi * (bore / 2) ** 2, 1),
            # a well wholly inside one zone needs the zone this wide at the well
            "min_zone_width_mm": round(2 * (d / 2 + PLACEMENT_TOL_MM), 2),
        }
    out["bulk_cell_1cm2_200mL_volume_to_area_mL_cm2"] = 200.0
    return out


def cap_seal():
    head_o2_nmol = O2_AIR_FRAC * HEADSPACE_UL * 1e-6 / MOLAR_GAS_L * 1e9
    liquid_o2_nmol = C_O2_MM * 1e-3 * WELL_UL * 1e-6 * 1e9
    vent_area = math.pi * (VENT_D_MM / 20.0) ** 2
    loss_g_s = D_WATER_AIR * vent_area * SAT_VAPOUR_G_CM3 * (1 - LAB_RH) / (VENT_L_MM / 10.0)
    loss_ul_h = loss_g_s * 3600 * 1000  # 1 mg ~ 1 uL
    return {
        "headspace_O2_nmol": round(head_o2_nmol, 0),
        "dissolved_O2_nmol": round(liquid_o2_nmol, 1),
        "headspace_over_dissolved": round(head_o2_nmol / liquid_o2_nmol, 1),
        "vent_water_loss_uL_per_h": round(loss_ul_h, 3),
        "chloride_rise_pct_per_h_through_vent": round(loss_ul_h / WELL_UL * 100, 3),
    }


def sulfide_mixing():
    rows = []
    for c in SULFIDE_TARGETS_MG_L:
        if c == 0:
            parts = {"ASW": WELL_UL}
        elif c in SULFIDE_STOCKS_MG_L:
            parts = {f"{c:g} mg/L stock": WELL_UL}
        else:
            stock = min(s for s in SULFIDE_STOCKS_MG_L if s > c)
            v = WELL_UL * c / stock
            parts = {"ASW": WELL_UL - v, f"{stock:g} mg/L stock": v}
        ok = all(v >= MIN_TRANSFER_UL for v in parts.values())
        rows.append({"target_mg_L_S": c,
                     "uL": {k: round(v, 1) for k, v in parts.items()},
                     "p20_transfers": sum(math.ceil(v / P20_MAX_UL) for v in parts.values()),
                     "every_transfer_at_least_15uL": ok,
                     "S_ug_in_well": round(c * WELL_UL * 1e-6 * 1e3, 4)})
    return rows


def d1141_copper():
    cu_g_stock = D1141_STOCK3_CUNO3_G_PER_10L * M["Cu"] / M_CUNO3_3H2O  # g Cu in 10 L of stock
    cu_ug_l_asw = cu_g_stock / 10.0 * 1e6 * (D1141_STOCK3_ML_PER_10L / 10000.0)
    return {"Cu_ug_L_in_ASW_with_stock3": round(cu_ug_l_asw, 1),
            "Cu_ng_in_one_150uL_well": round(cu_ug_l_asw * WELL_UL * 1e-6 * 1e3, 2)}


def acid():
    tube_ul = WELL_UL + RINSE_UL + ACID_UL
    h_umol = ACID_UL * ACID_M - ASW_ALKALINITY_MM * WELL_UL * 1e-3
    h_m = h_umol * 1e-6 / (tube_ul * 1e-6)
    return {"tube_uL": tube_ul, "HNO3_final_mM": round(ACID_UL * ACID_M / tube_ul * 1e3, 1),
            "H_final_mM_after_alkalinity": round(h_m * 1e3, 1), "pH_approx": round(-math.log10(h_m), 2)}


def mass_per_mC():
    return {k: round(1e-3 / (n * F) * M[el] * 1e6, 4) for k, (el, n) in CHARGE.items()}  # ug per mC


def icp():
    tube_ul = WELL_UL + RINSE_UL + ACID_UL
    tds_tube = ASW_TDS_G_L * WELL_UL / tube_ul
    out = {"tube_uL": tube_ul,
           "TDS_g_L_in_tube": round(tds_tube, 1),
           "TDS_g_L_after_dilution": round(tds_tube / ICP_DILUTION, 2),
           "min_dilution_for_TDS_limit": round(tds_tube / ICP_MAX_TDS_G_L, 1),
           "by_rate": {}}
    for name, rate in EARLEY_UG_CM2_DAY.items():
        per_well = {}
        for dash, d in ORINGS_MM.items():
            a = area_cm2(d)
            ng = rate * a * CONTACT_MIN / 1440.0 * 1e3
            ug_l_tube = ng / tube_ul  # ng/uL == mg/L; *1e3 -> ug/L; ng/uL*1000 = ug/L
            per_well[dash] = {
                "Cu_ng": round(ng, 2),
                "ug_L_in_150uL_well": round(ng / WELL_UL * 1e3, 1),
                "ug_L_in_tube": round(ug_l_tube * 1e3, 1),
                "ug_L_after_dilution": round(ug_l_tube * 1e3 / ICP_DILUTION, 2),
                "times_MDL_after_dilution": round(ug_l_tube * 1e3 / ICP_DILUTION / CU_MDL_UG_L, 0),
            }
        mol_cm2_s = rate * 1e-6 / M["Cu"] / 86400.0
        out["by_rate"][name] = {
            "ug_cm2_day": rate,
            "equivalent_uA_cm2_n1": round(mol_cm2_s * F * 1e6, 3),
            "equivalent_uA_cm2_n2": round(2 * mol_cm2_s * F * 1e6, 3),
            "wells": per_well,
        }
    return out


def counter_oh():
    return {"OH_mM_per_mC_in_150uL": round(1e-3 / F / (WELL_UL * 1e-6) * 1e3, 4)}


def lpr():
    out = {}
    for dash, d in ORINGS_MM.items():
        a = area_cm2(d)
        out[dash] = {f"{rp:g} ohm cm2": round(LPR_AMPLITUDE_V * a / rp * 1e9, 1) for rp in RP_OHM_CM2}
    return {"current_nA_at_10mV": out}


def hold():
    """Net anodic current at OCP + HOLD_MV with Tafel kinetics either side of icorr, and what
    a 10 min hold puts into the well. Two cathodic cases: Tafel, and transport-limited (flat)."""
    a = area_cm2(ORINGS_MM["-006"])
    up = 10 ** (HOLD_MV / 1000 / TAFEL_A_V)
    rows = []
    for icorr in ICORR_UA_CM2:
        for case, cath in (("cathodic Tafel 120 mV/dec", 10 ** (-HOLD_MV / 1000 / TAFEL_C_V)),
                           ("cathodic transport-limited", 1.0)):
            j = icorr * (up - cath)  # uA/cm2, net anodic
            q_mc = j * 1e-6 * a * HOLD_MIN * 60 * 1e3
            cu_ug = q_mc * mass_per_mC()["Cu(I)"]
            rows.append({"icorr_uA_cm2": icorr, "case": case, "net_uA_cm2": round(j, 1),
                         "spot_uA": round(j * a, 2), "charge_mC_10min": round(q_mc, 2),
                         "Cu_ug_if_all_Cu(I)": round(cu_ug, 2),
                         "Cu_mg_L_in_150uL": round(cu_ug / WELL_UL * 1e3, 1),
                         "hits_charge_cap": q_mc > HOLD_CHARGE_CAP_MC})
    return {"area_cm2": round(a, 4), "anodic_gain_at_hold": round(up, 2),
            "charge_cap_mC": HOLD_CHARGE_CAP_MC,
            "charge_cap_Cu_ug_n1": round(HOLD_CHARGE_CAP_MC * mass_per_mC()["Cu(I)"], 2),
            "rows": rows}


def cyclic():
    """Order-of-magnitude charge of one cyclic polarization reversed at a current threshold, if
    the anodic current rises exponentially (TAFEL_A_V per decade): the forward charge is about
    i_rev * A * (b / ln 10) / scan rate, and the reverse branch is taken as equal to it."""
    a = area_cm2(ORINGS_MM["-006"])
    o2_mc = 4 * F * C_O2_MM * 1e-3 * WELL_UL * 1e-6 * 1e3
    rows = []
    for j in REVERSALS_MA_CM2:
        i_a = j * 1e-3 * a
        for name, rate in SCAN_V_S.items():
            q = 2 * i_a * (TAFEL_A_V / math.log(10)) / rate  # C
            cu_ug = q * 1e3 * mass_per_mC()["Cu(I)"]
            rows.append({"reversal_mA_cm2": j, "scan": name, "spot_uA_at_reversal": round(i_a * 1e6, 1),
                         "charge_mC": round(q * 1e3, 1), "Cu_ug_if_all_Cu(I)": round(cu_ug, 1),
                         "Cu_mg_L_in_150uL": round(cu_ug / WELL_UL * 1e3, 0),
                         "counter_OH_mM_if_unbuffered": round(q / F / (WELL_UL * 1e-6) * 1e3, 2),
                         "O2_inventory_lasts_s_at_reversal": round(o2_mc * 1e-3 / i_a, 0)})
    return {"area_cm2": round(a, 4), "O2_inventory_mC": round(o2_mc, 2), "rows": rows}


def bulk_cell():
    """The same Earley release rates on the bench calibration cell: 1 cm2 in 200 mL."""
    out = {}
    for name, rate in EARLEY_UG_CM2_DAY.items():
        ug = rate * BULK_AREA_CM2 * CONTACT_MIN / 1440.0
        out[name] = {"Cu_ug": round(ug, 3), "ug_L_in_200mL": round(ug / (BULK_ML / 1000), 2)}
    return out


def zra():
    """Galvanic current densities quoted in c1-02 and c1-04, as currents on a -006-sized anode
    and on a 1 cm2 bench anode."""
    a = area_cm2(ORINGS_MM["-006"])
    return {name: {"uA_cm2": j, "uA_on_0p0661cm2": round(j * a, 3), "uA_on_1cm2": j}
            for name, j in GALVANIC_UA_CM2.items()}


def coulometry():
    """Galvanostatic oxide reduction on a -006 spot (c1-10, with the CuO correction)."""
    a = area_cm2(ORINGS_MM["-006"])
    out = {"spot_uA_at_20_30_uA_cm2": [round(20 * a, 2), round(30 * a, 2)]}
    for ox, mc in OXIDE_MC_CM2_PER_NM.items():
        out[ox] = {"uC_per_nm_on_spot": round(mc * a * 1e3, 1),
                   "s_per_nm_at_25uA_cm2": round(mc * 1e-3 / 25e-6, 1)}
    return out


def timing():
    per_well = sum(STEPS_MIN.values())
    return {"steps_min": STEPS_MIN, "per_well_cycle_min": per_well,
            "liquid_contact_min": CONTACT_MIN,
            "wells_per_night": WELLS_PER_NIGHT,
            "night_h": round(WELLS_PER_NIGHT * per_well / 60, 1),
            "fits_in_night": WELLS_PER_NIGHT * per_well / 60 <= NIGHT_H,
            "tubes_per_night": WELLS_PER_NIGHT + 1,  # + the stock blank
            "tips_per_night_min": 2 * WELLS_PER_NIGHT + 1}  # fill + collect per well, one acid tip


def main():
    out = {
        "wells": wells(),
        "cap_seal": cap_seal(),
        "sulfide_mixing": sulfide_mixing(),
        "d1141_heavy_metal_stock_copper": d1141_copper(),
        "acid_at_collection": acid(),
        "ug_per_mC": mass_per_mC(),
        "icp_ms": icp(),
        "counter": counter_oh(),
        "lpr": lpr(),
        "anodic_hold": hold(),
        "cyclic_polarization": cyclic(),
        "bulk_cell": bulk_cell(),
        "zra": zra(),
        "coulometry": coulometry(),
        "timing": timing(),
    }
    w = out["wells"]
    print("Wells (AS568, 1.78 mm cross-section)")
    for dash in ORINGS_MM:
        r = w[dash]
        print(f"  {dash}: ID {r['id_mm']} mm, OD {r['od_mm']} mm, {r['area_cm2']} cm2, "
              f"{r['volume_to_area_mL_cm2']} mL/cm2 at {WELL_UL:g} uL, zone >= {r['min_zone_width_mm']} mm wide")
    c = out["cap_seal"]
    print(f"\nCap seal: headspace O2 {c['headspace_O2_nmol']:.0f} nmol vs {c['dissolved_O2_nmol']} nmol dissolved "
          f"({c['headspace_over_dissolved']}x); vent loses {c['vent_water_loss_uL_per_h']} uL/h")
    print("\nSulfide series, per 150 uL well (ASW first, sulfide last)")
    for r in out["sulfide_mixing"]:
        print(f"  {r['target_mg_L_S']:g} mg/L: {r['uL']}, {r['p20_transfers']} transfers, {r['S_ug_in_well']} ug S")
    print(f"\nD1141 with its heavy-metal stock: {out['d1141_heavy_metal_stock_copper']}")
    print(f"Acid at collection: {out['acid_at_collection']}")
    print(f"ug of metal per mC: {out['ug_per_mC']}")
    i = out["icp_ms"]
    print(f"\nICP-MS: tube {i['tube_uL']:g} uL, TDS {i['TDS_g_L_in_tube']} g/L, "
          f"{i['TDS_g_L_after_dilution']} g/L after {ICP_DILUTION:g}x")
    for name, r in i["by_rate"].items():
        wv = r["wells"]["-006"]
        print(f"  {name} ({r['ug_cm2_day']:g} ug/cm2/day = {r['equivalent_uA_cm2_n1']} uA/cm2 as Cu(I)): "
              f"-006 well {wv['Cu_ng']} ng, {wv['ug_L_in_tube']} ug/L in the tube, "
              f"{wv['ug_L_after_dilution']} ug/L after dilution = {wv['times_MDL_after_dilution']:.0f}x MDL")
    print(f"\nCounter: {out['counter']}")
    print(f"LPR at +/-10 mV, nA: {out['lpr']['current_nA_at_10mV']}")
    print("\nAnodic hold, OCP + 50 mV for 10 min on the -006 well")
    for r in out["anodic_hold"]["rows"]:
        print(f"  icorr {r['icorr_uA_cm2']:g}, {r['case']}: {r['spot_uA']} uA, {r['charge_mC_10min']} mC, "
              f"{r['Cu_mg_L_in_150uL']} mg/L Cu, over cap: {r['hits_charge_cap']}")
    print("\nCyclic polarization, -006 well")
    for r in out["cyclic_polarization"]["rows"]:
        print(f"  reverse at {r['reversal_mA_cm2']:g} mA/cm2, {r['scan']}: {r['charge_mC']} mC, "
              f"{r['Cu_mg_L_in_150uL']:.0f} mg/L Cu, OH- {r['counter_OH_mM_if_unbuffered']} mM, "
              f"O2 gone in {r['O2_inventory_lasts_s_at_reversal']:.0f} s at reversal")
    print(f"\nBulk cell (1 cm2, 200 mL): {out['bulk_cell']}")
    print(f"Galvanic currents: {out['zra']}")
    print(f"Oxide coulometry: {out['coulometry']}")
    t = out["timing"]
    print(f"\nTiming: {t['per_well_cycle_min']} min per well, {t['wells_per_night']} wells = {t['night_h']} h; "
          f"{t['tubes_per_night']} tubes, >= {t['tips_per_night_min']} tips")

    path = pathlib.Path(__file__).with_name("copper_numbers.json")
    path.write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()

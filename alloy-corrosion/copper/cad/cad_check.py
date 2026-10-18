"""Force, seal and fit checks for the copper electrode cap, lid and tray in cad_cu_cell.py.
Writes cad_check.json. Every number in cad/README.md comes from here.

Sources and models (each is stated again next to its number in the JSON):
- O-ring load: Lindley's formula for a ring section squeezed between flat plates,
  F/L = E d (1.25 e^1.5 + 50 e^6), with E from Shore A hardness by Gent's relation,
  E [MPa] = 0.0981 (56 + 7.62336 S) / (0.137505 (254 - 2.54 S)). FKM 70-80 A, 75 A nominal.
- AS568 tolerances for the -006 and -016 (cross-section 0.070 +/- 0.003 in) and printed
  gland dimensions to +/- 0.05 mm after a calibration print (an assumption).
- Electromagnet: the uxcell / Adafruit P25/20 (25 x 20 mm, 5 V, 0.3 A, centre pole 12 mm,
  rated "5 kg minimum" holding: Adafruit product 3873). No gap curve is published for it, so
  the shape of the curve is taken from the same-size Eclipse Magnetics M52172 (25 x 20 mm,
  15 kg at zero gap on a 3 mm armature; its datasheet table, normalised). A thin steel disc
  saturates: the flux from the centre pole crosses the disc's rim at r = 6 mm, so the disc
  carries at most B_sat 2 pi r t; force scales with flux squared.
- Hold-down magnets: supermagnete S-04-02-N, 4 x 2 mm N45, 4.12 N on a thick steel plate.
- Vapour transport: water vapour in air D = 0.25 cm2/s, saturated vapour 19.4 g/m3 at 22 C,
  room RH 40 %. Air viscosity 1.81e-5 Pa s, density 1.2 kg/m3.

    python cad_check.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
META = json.loads((HERE / "cad_parts.json").read_text())
P = META["parameters"]

CS_TOL = 0.003 * 25.4          # AS568 cross-section tolerance, mm
PRINT_TOL = 0.05               # gland dimensions after a calibration print, mm (assumed)
F_RATED = 50.0                 # N, P25/20 "5 kg minimum"
GAP_CURVE = [(0.00, 15.00), (0.09, 5.10), (0.18, 2.20), (0.27, 1.20), (0.36, 0.80), (0.59, 0.40), (1.00, 0.20)]  # M52172, kg
B_SAT, R_POLE = 1.6, 6.0e-3    # T for low-carbon steel; P25/20 centre pole radius, m
A_CORE = math.pi * 6.0e-3 ** 2
A_SHELL = math.pi * (12.5e-3 ** 2 - 10.5e-3 ** 2)  # 2 mm shell wall: ASSUMED
MU0 = 4e-7 * math.pi
D_V, C_SAT, RH_ROOM = 0.25, 19.4e-6, 0.40  # cm2/s, g/cm3, -
MU_AIR, RHO_AIR = 1.81e-5, 1.2


def E_shore(S):
    return 0.0981 * (56 + 7.62336 * S) / (0.137505 * (254 - 2.54 * S))


def lindley(E, d, e):
    """N per mm of seal length; E in MPa, d in mm, e fractional squeeze."""
    return E * d * (1.25 * e ** 1.5 + 50 * e ** 6)


def gap_factor(g):
    gs, fs = zip(*GAP_CURVE)
    return float(np.interp(g, gs, np.array(fs) / fs[0]))


def phi_rated():
    return math.sqrt(2 * MU0 * F_RATED / (1 / A_CORE + 1 / A_SHELL))


def sat_factor(t_mm):
    return min(1.0, (B_SAT * 2 * math.pi * R_POLE * t_mm * 1e-3 / phi_rated()) ** 2)


def magnet_force(t_mm, g_mm):
    """Available pull, N: the smaller of the disc-saturation limit and the gap curve."""
    return F_RATED * min(sat_factor(t_mm), gap_factor(g_mm))


def volume(name):
    return cq.importers.importStep(str(HERE / f"{name}.step")).val().Volume()  # mm3


def r3(x):
    return round(x, 3) if isinstance(x, float) else x


def main():
    out = {"sources": __doc__.split("Sources and models")[1].split("python cad_check.py")[0].strip()}
    E = {S: E_shore(S) for S in (70, 75, 80)}
    out["E_MPa_by_shore_A_gent"] = {str(S): round(v, 2) for S, v in E.items()}

    # ---- a. face seal, AS568-006 in the counterbore
    cs, idd, h = P["face_oring_cs"], P["face_oring_id"], P["cbore_h"]
    area = math.pi / 4 * cs ** 2
    sq = lambda c, hh: (c - hh) / c
    squeeze = {"nominal": sq(cs, h), "min": sq(cs - CS_TOL, h + PRINT_TOL), "max": sq(cs + CS_TOL, h - PRINT_TOL)}
    gland = h * (P["cbore_d"] / 2 - P["throat_d"] / 2)  # the inside is open to the throat
    L = math.pi * (idd + cs)
    face = {"squeeze_pct": {k: round(v * 100, 1) for k, v in squeeze.items()},
            "gland_fill_pct": round(area / gland * 100, 1),
            "stretch_pct": 0.0,
            "free_OD_mm": round(idd + 2 * cs, 2), "counterbore_d_mm": P["cbore_d"],
            "squeezed_section": "stadium of equal area, 1.40 mm tall: contact on the metal r %.2f-%.2f mm, inner bulge at r %.2f mm"
                                % (*META["face_oring_contact_on_metal_r"], META["face_oring_inner_bulge_r"]),
            "seal_length_mm": round(L, 2)}
    loads = {}
    for S in (70, 75, 80):
        for k, e in squeeze.items():
            loads[f"{S}A_{k}"] = round(lindley(E[S], cs if k == "nominal" else (cs - CS_TOL if k == "min" else cs + CS_TOL), e) * L, 1)
    face["force_N"] = loads
    F_face = loads["75A_nominal"]
    F_face_max = max(loads.values())
    face["two_M3_screws"] = {"preload_each_N_for_2x_the_worst_case_ring_load": round(F_face_max, 1),
                             "torque_mNm_at_K_0.2": round(0.2 * F_face_max * 3.0, 1),
                             "note": "finger-tight with a hex key; heat-set M3 inserts in PETG hold several hundred N"}
    # lid bending, conservative: simply supported between the screws, centre load, section reduced by the bore
    b = P["lid_x"] - P["bore_d"]
    t = P["lid_top"] - P["cbore_h"]
    I = b * t ** 3 / 12
    span = 2 * P["clamp_y"]
    face["lid_bow_mm_upper_bound"] = {"PETG_E_2000MPa": round(F_face_max * span ** 3 / (48 * 2000 * I), 4),
                                      "PETG_creep_E_1000MPa_overnight": round(F_face_max * span ** 3 / (48 * 1000 * I), 4),
                                      "squeeze_mm": round(cs - h, 3)}
    # where the squeezed ring meets the metal: three estimates of the contact half-width
    R = cs / 2
    d_side = (cs - h) / 2
    a_stadium = (META["face_oring_contact_on_metal_r"][1] - META["face_oring_contact_on_metal_r"][0]) / 2
    a_hertz = math.sqrt(4 * lindley(E[75], cs, squeeze["nominal"]) * R / (math.pi * E[75] / 0.75))
    a_chord = math.sqrt(2 * R * d_side - d_side ** 2)
    rc = idd / 2 + cs / 2
    face["wetted_spot"] = {
        "ring_centre_radius_mm": round(rc, 3),
        "contact_half_width_mm": {"stadium_equal_area": round(a_stadium, 3), "hertz_line_contact_with_lindley_load": round(a_hertz, 3),
                                  "geometric_chord_upper_bound": round(a_chord, 3)},
        "wetted_radius_mm": [round(rc - a_chord, 3), round(rc - a_stadium, 3)],
        "wetted_area_cm2": [round(math.pi * ((rc - a_chord) / 10) ** 2, 4), round(math.pi * ((rc - a_stadium) / 10) ** 2, 4)],
        "nominal_area_from_ID_cm2": round(math.pi * (idd / 20) ** 2, 4),
        "ratio_to_nominal": [round(((rc - a_chord) / (idd / 2)) ** 2, 2), round(((rc - a_stadium) / (idd / 2)) ** 2, 2)],
        "ring_can_shift_off_axis_mm": round(P["cbore_d"] / 2 - (rc + a_stadium + h / 2), 3),
        "meaning": "the liquid wets the metal out to the inner edge of the ring's contact, not to the ring's ID: "
                   "the annulus between is a thin crevice under the ring's curved inner face"}
    out["a_face_seal_AS568_006"] = face

    # ---- b. radial seal, AS568-016 on the 16 mm boss (the O-ring cap)
    cs2, id2 = P["rad_oring_cs"], P["rad_oring_id"]
    gd, gw, rod = P["gland_depth"], P["groove_w"], P["boss_d"]
    area2 = math.pi / 4 * cs2 ** 2
    sq2 = {"nominal": (cs2, gd), "min": (cs2 - CS_TOL, gd + 2 * PRINT_TOL / 2 * 2 / 2), "max": (cs2 + CS_TOL, gd - PRINT_TOL)}
    sq2 = {"nominal": (cs2, gd), "min": (cs2 - CS_TOL, gd + PRINT_TOL), "max": (cs2 + CS_TOL, gd - PRINT_TOL)}
    L2 = math.pi * rod
    rad = {"gland_depth_mm": gd, "groove_width_mm": gw, "groove_bottom_d_mm": rod + 2 * gd,
           "squeeze_pct": {k: round(sq(c, hh) * 100, 1) for k, (c, hh) in sq2.items()},
           "gland_fill_pct": round(area2 / (gd * gw) * 100, 1),
           "ID_interference_pct": round((rod - id2) / id2 * 100, 2),
           "OD_vs_groove_bottom_mm": round(id2 + 2 * cs2 - (rod + 2 * gd), 3),
           "guidance": "squeeze 10-16 % is Parker's reciprocating-seal range for 0.070 in sections; static radial glands run 16-30 %"}
    normal = {k: lindley(E[75], c, sq(c, hh)) * L2 for k, (c, hh) in sq2.items()}
    rad["normal_force_N_75A"] = {k: round(v, 1) for k, v in normal.items()}
    rad["normal_force_N_70_80A_nominal"] = [round(lindley(E[70], cs2, sq(cs2, gd)) * L2, 1), round(lindley(E[80], cs2, sq(cs2, gd)) * L2, 1)]
    fr = {}
    for mu in (0.2, 0.4, 0.6):
        for brk in (1.0, 1.5, 2.0):
            fr[f"mu{mu}_breakaway{brk}"] = {k: round(mu * brk * v, 1) for k, v in normal.items()}
    rad["friction_N"] = fr
    rad["insertion_push_N_mu0.2_to_0.6_nominal"] = [round(0.2 * normal["nominal"], 1), round(0.6 * normal["nominal"], 1)]
    rad["extraction_pull_N_range"] = [round(0.2 * normal["min"], 1), round(0.6 * 2.0 * normal["max"], 1)]
    out["b_radial_seal_AS568_016"] = rad

    # ---- magnet
    mag = {"model": "F = 50 N x min(disc saturation, gap curve); gap curve normalised from Eclipse M52172 (25 x 20 mm)",
           "gap_curve_normalised": {f"{g:.2f}mm": round(f / GAP_CURVE[0][1], 3) for g, f in GAP_CURVE},
           "rated_flux_uWb": round(phi_rated() * 1e6, 1),
           "disc_saturation_factor": {f"{t}mm": round(sat_factor(t), 3) for t in (0.5, 0.8, 1.0, 1.5, 2.0)},
           "available_N": {f"disc_{t}mm": {f"gap_{g:.2f}mm": round(magnet_force(t, g), 1) for g in (0.0, 0.05, 0.09, 0.18, 0.36, 1.0)}
                           for t in (0.5, 1.0, 1.5)}}
    out["magnet_P25_20"] = mag

    # ---- weights
    rho_petg = 1.27e-3  # g/mm3
    m = {"cap_body_petg_g": volume("electrode_cap") * rho_petg, "carrier_petg_g": volume("electrode_carrier") * rho_petg,
         "steel_disc_g": volume("steel_disc") * 7.85e-3, "reference_g_assumed": 0.3,
         "pt_coil_g": volume("pt_coil") * 21.45e-3, "pogo_pins_g_assumed": 0.2, "hold_steel_g": volume("cap_hold_steel") * 7.85e-3}
    m["total_g"] = sum(m.values())
    m = {k: round(v, 2) for k, v in m.items()}
    m["oring_cap_body_petg_g"] = round(volume("electrode_cap_oring") * rho_petg, 2)
    out["cap_mass"] = m
    W_cap = m["total_g"] * 9.81e-3

    # ---- margins for the O-ring cap
    need = {"nominal_mu0.4_breakaway1.5": 0.4 * 1.5 * normal["nominal"], "worst_mu0.6_breakaway2_max_squeeze": 0.6 * 2.0 * normal["max"],
            "best_mu0.2_min_squeeze": 0.2 * normal["min"]}
    marg = {}
    for t in (0.5, 1.0, 1.5):
        for g in (0.0, 0.09, 0.18):
            avail = magnet_force(t, g)
            marg[f"disc_{t}mm_gap_{g:.2f}mm"] = {k: round(avail / (v + W_cap), 2) for k, v in need.items()}
    out["oring_cap_pull_margin_available_over_needed"] = marg

    # ---- recommended cap: clearance skirt, magnetic hold-down
    c = P["skirt_clear"]
    Lland = P["boss_h"] - P["boss_chamfer"]  # cylindrical land length, mm
    rec = {"radial_clearance_mm": c, "land_length_mm": Lland}
    A_bore = math.pi * (P["bore_d"] / 20) ** 2 - math.pi * (P["ref_d"] / 20) ** 2  # cm2, annulus round the reference
    h_liq_top = 4.5  # mm above the metal (sim_well: ~4.5 with the reference in)
    L_s = (P["lid_top"] + P["boss_h"] + 0.3 - h_liq_top) / 10  # cm, liquid surface to the cap ceiling
    for cc in (c - PRINT_TOL, c, c + PRINT_TOL, 0.22):
        A_gap = math.pi * (P["boss_d"] / 10) * (cc / 10)
        G_g = D_V * A_gap / (Lland / 10)
        G_s = D_V * A_bore / L_s
        rh_head = (G_s + G_g * RH_ROOM) / (G_s + G_g)
        J = G_g * C_SAT * (rh_head - RH_ROOM) * 3600 * 1e3  # mg/h = uL/h
        rec[f"clearance_{cc:.2f}mm"] = {"evaporation_uL_per_h": round(J, 2), "pct_of_150uL_per_63min": round(J * 63 / 60 / 150 * 100, 2),
                                        "headspace_RH_pct": round(rh_head * 100, 1)}
    # no cap at all: diffusion up the bore and the boss to open air, with an end correction
    L_open = (P["lid_top"] + P["boss_h"] - h_liq_top) / 10 + 0.8 * P["bore_d"] / 20
    J_open = D_V * (math.pi * (P["bore_d"] / 20) ** 2) / L_open * C_SAT * (1 - RH_ROOM) * 3600 * 1e3
    rec["no_cap_evaporation_uL_per_h"] = round(J_open, 2)
    # air pushed out through the clearance as the skirt slides on (laminar annulus)
    A_in = math.pi * ((P["boss_d"] / 2 + c) * 1e-3) ** 2
    for v in (5.0, 20.0):
        Q = A_in * v * 1e-3
        dP = 12 * MU_AIR * (Lland * 1e-3) * Q / (math.pi * P["boss_d"] * 1e-3 * (c * 1e-3) ** 3)
        rec[f"press_on_dP_Pa_at_{v:.0f}mm_s"] = round(dP, 1)
    # hold-down: two 4 x 2 mm N45 discs through a 0.4 mm skin onto 3 x 2 mm steel slugs
    F_contact = 4.12
    derate = (0.35 * 0.8 * 0.7, 0.5 * 0.8 * 0.7)  # 0.45 mm gap; steel 2 mm thick; steel 3 mm on a 4 mm magnet. ESTIMATES
    hold = [2 * F_contact * k for k in derate]
    rec["hold_down"] = {
        "per_magnet_N_at_contact_supplier": F_contact,
        "derating_assumed": "x0.35-0.5 for the 0.4 mm skin plus 0.05 mm, x0.8 for 2 mm of steel, x0.7 for a 3 mm slug on a 4 mm magnet",
        "two_magnets_N": [round(v, 2) for v in hold],
        "cap_weight_N": round(W_cap, 3),
        "pin_force_total_N_max_half_the_weakest_hold_down": round(hold[0] / 2, 2),
        "rule": "pick spring pins of at most 0.4 N each at the seated stroke (0.93 mm), so the magnets hold the cap "
                "down with a factor of 2; P75-class pins can be 1 N or more, so measure before use",
        "electromagnet_must_lift_N": round(hold[1] + W_cap, 2),
        "electromagnet_margin_disc1mm": {f"gap_{g:.2f}mm": round(magnet_force(1.0, g) / (hold[1] + W_cap), 1) for g in (0.0, 0.09, 0.18, 0.36)},
        "clocking": "the two magnets pull the cap's steel slugs into line, so the pins land on the +/-30 deg pads; "
                    "0 and 180 deg are both stable, so set the cap's index mark by hand at the park cup"}
    out["recommended_clearance_cap"] = rec

    # ---- the O-ring cap's press-on transient, with and without its 0.3 mm vent
    z_ring_low = P["groove_z"][0] + (P["groove_z"][1] - P["groove_z"][0] - 1.94) / 2 - 0.1
    stroke = P["boss_h"] - z_ring_low  # cap height above seated when the ring meets the boss
    A_head = math.pi * (P["boss_d"] / 2 + c) ** 2  # mm2
    V1 = math.pi * ((P["bore_d"] / 2) ** 2 - (P["ref_d"] / 2) ** 2) * (P["lid_top"] + P["boss_h"] - h_liq_top) + A_head * 0.3 - 60.0  # minus the carrier
    V0 = V1 + A_head * stroke
    vent = {"trapped_stroke_mm": round(stroke, 2), "headspace_seated_uL": round(V1, 0), "headspace_at_engagement_uL": round(V0, 0)}
    P_ratio = V0 / V1
    vent["no_vent"] = {"pressure_rise_bar": round((P_ratio - 1) * 1.013, 2), "force_on_cap_N": round((P_ratio - 1) * 0.1013 * A_head, 1),
                       "consequence": "the cap needs that much extra push and springs back off when the magnet lets go"}
    d_v, L_v = P["vent_d"] * 1e-3, (9.0 - P["ceiling_z"]) * 1e-3
    for v in (5.0, 20.0):
        Q = A_head * 1e-6 * v * 1e-3
        dP = 128 * MU_AIR * L_v * Q / (math.pi * d_v ** 4) + 0.5 * RHO_AIR * (Q / (math.pi * d_v ** 2 / 4)) ** 2
        vent[f"with_vent_dP_kPa_at_{v:.0f}mm_s"] = round(dP / 1e3, 2)
        vent[f"with_vent_force_on_cap_N_at_{v:.0f}mm_s"] = round(dP * A_head * 1e-6, 2)
    vent["face_seal_holds"] = "yes: a squeezed O-ring face seal holds far more than a few kPa; the risk without the vent is the cap popping, not a leak"
    out["oring_cap_press_on_transient"] = vent

    # ---- d. geometry
    geo = {"reference_tip_above_metal_mm": round(P["lid_top"] + META["placement"]["reference_tip_C"], 3),
           "cap_edge_to_neighbour_lid_edge_mm": round((P["stations_x"][1] - P["stations_x"][0]) - P["lid_x"] / 2 - P["cap_d"] / 2, 2),
           "cap_edge_to_neighbour_pads_mm": round((P["stations_x"][1] - P["stations_x"][0]) - P["pad_r"][1] - P["cap_d"] / 2, 2),
           "flange_overhang_above_neighbour_lid_top_mm": round(P["flange_z"], 2),
           "mount_IR_housing_inner_faces_from_axis_mm": 17.0,
           "cap_flange_radius_mm": P["flange_d"] / 2,
           "clearance_to_IR_housings_mm": round(17.0 - P["flange_d"] / 2, 2),
           "vial_cap_outer_d_mm": 28.0,
           "IR_beam": "crosses the magnet axis just below the magnet face (PANDA-film Fig. 2B); the cap's 28 mm flange and 25 mm body are solid there, as a vial cap is",
           "carried_below_carriage_mm": {"pogo_pin_tips_free": round(16 + P["cap_top"] + P["pin_protrude"] + 0.4, 2),
                                         "reference_tip": round(16 + P["cap_top"] + P["lid_top"] - P["ref_tip_w"], 2),
                                         "coil_bottom": round(16 + P["cap_top"] + P["lid_top"] - P["coil_z_w"][0] + P["coil_wire"] / 2, 3),
                                         "carrier_legs_bottom_lowest": round(16 + P["cap_top"] + P["lid_top"] - P["leg_bottom_w"], 2)},
           "seated_lowest_parts_above_metal_mm": {"carrier_legs": P["leg_bottom_w"], "coil": round(P["coil_z_w"][0] - P["coil_wire"] / 2, 3),
                                                  "throat_top": P["throat_top"]}}
    # interference between the seated parts (mm3); the pins are drawn free, 1.0 mm out, so they overlap the lid
    ld = lambda n: cq.importers.importStep(str(HERE / f"{n}.step")).val()
    up = lambda s: s.translate(cq.Vector(0, 0, P["lid_top"]))
    lid, cap, capo, car = ld("well_lid"), ld("electrode_cap"), ld("electrode_cap_oring"), ld("electrode_carrier")
    ref, coil, pins, ring, cpn = ld("ag_agcl_ref"), ld("pt_coil"), ld("cap_pogo_pins"), ld("face_oring_006"), ld("coupon_20x20x6")
    pairs = {"cap_vs_lid": (up(cap), lid), "oring_cap_vs_lid": (up(capo), lid), "carrier_vs_lid": (up(car), lid),
             "carrier_vs_cap": (car, cap), "reference_vs_lid": (up(ref), lid), "coil_vs_lid": (up(coil), lid),
             "coil_vs_carrier": (coil, car), "face_oring_vs_lid": (ring, lid), "face_oring_vs_coupon": (ring, cpn),
             "lid_vs_coupon": (lid, cpn), "pins_drawn_free_vs_lid": (up(pins), lid)}
    geo["interference_mm3"] = {k: round(a.intersect(b).Volume(), 3) for k, (a, b) in pairs.items()}
    out["d_geometry"] = geo

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, float):
            return round(o, 3)
        return o
    (HERE / "cad_check.json").write_text(json.dumps(clean(out), indent=1) + "\n")
    print(json.dumps(clean({k: v for k, v in out.items() if k != "sources"}), indent=1))


if __name__ == "__main__":
    main()

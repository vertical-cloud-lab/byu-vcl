"""The CubXL's corrosion well on tray A (DAL PR #180's copper deck): how much water and sulfide a spot loses, how long
the head works on a spot with each pipette choice, and how accurate each choice is at the volumes actually moved.
For notes/cubxl_pipettes.md (#303, PR #318; Sterling, 2026-11-20).

    python3 cubxl_evap.py            # -> out/cubxl_evap.json, out/cubxl_evap.png

Every number is a first-order estimate. Each constant names its source, or says "assumed".

* **Water.** Diffusion of water vapour from the liquid surface up the well's bore and out through whatever covers it,
  as DAL's own cap check does (digital-alloy-lab PR #180, ``copper/cad/cad_check.py`` at 633995b: D = 0.25 cm2/s,
  19.4 g/m3 saturated at 22 C, room RH 40 %, an end correction of 0.8 r at an open mouth). Added here: seawater's
  lower vapour pressure, other RH and temperatures, and moving air over the mouth (a laminar boundary layer in series
  with the still air in the bore).
* **Sulfide.** H2S leaves through the same paths. Only the H2S fraction is volatile (2.3 % of the total at pH 8.2 in
  seawater), and the total sulfide has to diffuse up through the unstirred well to reach the surface, so a 1-D
  diffusion model of the well with that escape at the top. The copper itself takes up sulfide too; that sink is
  estimated separately, not modelled.
* **Head time.** Step times measured on the CubXL itself (byu-vcl cubos/results/pipette_test_20261007 and
  pipette_test_mix_20261009b: GRBL F3000, 300 mm/s2), applied to each option's list of moves.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# ---------------------------------------------------------------------------------------------------------------------
# Air, water and H2S
# ---------------------------------------------------------------------------------------------------------------------
R = 8.314462
M_W = 18.015e-3                                   # kg/mol
T_ROOM = 22.0                                     # C, DAL's cad_check.py
A_W_SEAWATER = 0.981                              # water activity of S 35 seawater (vapour pressure 1.8-1.9 % lower)
A_W_TUBE = 0.99                                   # the tube: 150 uL well + 150 uL DI + 20 uL 1 M HNO3, about half-strength
NU_AIR = 1.53e-5                                  # m2/s at 22 C
D_S_AQ = 1.60e-9                                  # m2/s, total sulfide (HS-, H2S) in water at 22 C: HS- 1.73e-9 at 25 C
#                                                   (Li & Gregory 1974) scaled by T/viscosity
PK1_H2S = None                                    # computed below (Millero, Plese & Fernandez 1988, seawater)
H_CP_H2S_298 = 1.0e-3                             # mol/(m3 Pa), Sander 2015 compilation; d ln H / d(1/T) = 2100 K
PH_WELL = 8.2                                     # protocol.md section 3: D1141 ASW at pH 8.2


def p_sat(t_c: float) -> float:
    """Saturation vapour pressure of water, Pa (Magnus form, Alduchov & Eskridge 1996)."""
    return 610.94 * math.exp(17.625 * t_c / (t_c + 243.04))


def c_sat(t_c: float) -> float:
    """Saturated water vapour density, kg/m3 (19.4 g/m3 at 22 C, DAL's figure)."""
    return p_sat(t_c) * M_W / (R * (t_c + 273.15))


def d_water_air(t_c: float) -> float:
    """Water vapour in air, m2/s (Massman 1998: 0.2178 cm2/s at 0 C, x (T/273.15)^1.81; 0.25 cm2/s at 22 C)."""
    return 0.2178e-4 * ((t_c + 273.15) / 273.15) ** 1.81


def d_h2s_air(t_c: float) -> float:
    """H2S in air, m2/s (Fuller-Schettler-Giddings: 0.162 cm2/s at 22 C), scaled as T^1.75."""
    return 0.162e-4 * ((t_c + 273.15) / 295.15) ** 1.75


def pk1_h2s(t_c: float, sal: float = 35.0) -> float:
    """First dissociation constant of H2S in seawater (Millero, Plese & Fernandez 1988, Limnol. Oceanogr. 33:269)."""
    t = t_c + 273.15
    return -98.080 + 5765.4 / t + 15.0455 * math.log(t) - 0.157 * sal ** 0.5 + 0.0135 * sal


def h2s_fraction(ph: float, t_c: float) -> float:
    return 1.0 / (1.0 + 10 ** (ph - pk1_h2s(t_c)))


def k_aw_h2s(t_c: float) -> float:
    """Dimensionless air/water partition coefficient of H2S (gas over liquid concentration)."""
    t = t_c + 273.15
    h = H_CP_H2S_298 * math.exp(2100.0 * (1 / t - 1 / 298.15))
    return 1.0 / (h * R * t)


# ---------------------------------------------------------------------------------------------------------------------
# The well, its cap, the tube and the stock vial (DAL PR #180 at 633995b: copper/cad/cad_parts.json, protocol.md)
# ---------------------------------------------------------------------------------------------------------------------
WELL = dict(throat_r=1.45, throat_h=1.6, bore_r=4.0, bore_top=10.0,   # mm above the metal; lid_top 6 + boss_h 4
            ref_r=1.0, ref_tip=3.0, ceiling=10.3,                     # the cap's ceiling 0.3 mm over the boss
            boss_d=16.0, skirt_gap=0.12, land=3.2,                    # the clearance cap: 0.12 mm over a 3.2 mm land
            vent_d=0.3, vent_len=6.0,                                 # the O-ring cap's vent; its length is assumed
            fill_ul=150.0)
TUBE = dict(level=18.2, top=31.2, r=3.2, ul=320.0)                   # instruments_lab._TUBE_IN, tube_level(320)
VIAL = dict(body_r=12.6, neck_r=8.0, head=14.0, neck=8.0, ml=18.0)    # 20 mL vial, 18 mL: body from the clip's model
#                                                                       (25.2 mm inside); neck radius and lengths assumed
CUP = dict(r=6.0, recess=12.0, ml=3.0)                                # 4 mL rinse cup, assumed geometry


def well_level(ul: float, capped: bool = False) -> float:
    """mm above the metal (instruments_lab.well_level, DAL's render_cubxl_cu.well_level)."""
    w = WELL
    a2 = math.pi * w["throat_r"] ** 2
    throat = a2 * w["throat_h"]
    lvl = ul / a2 if ul <= throat else w["throat_h"] + (ul - throat) / (math.pi * w["bore_r"] ** 2)
    if capped and lvl > w["ref_tip"]:
        lvl = w["ref_tip"] + (lvl - w["ref_tip"]) * w["bore_r"] ** 2 / (w["bore_r"] ** 2 - w["ref_r"] ** 2)
    return lvl


def surface_area_mm2(ul: float) -> float:
    w = WELL
    throat = math.pi * w["throat_r"] ** 2 * w["throat_h"]
    return math.pi * (w["throat_r"] if ul <= throat else w["bore_r"]) ** 2


def sherwood_ext(d_m: float, u: float, d_gas: float) -> float:
    """Mass transfer from a flush disc of diameter d into the air above it, Sh = k d / D. Still air: a disc in a plane
    wall (8/pi, the 0.8 r end correction DAL uses). Moving air at u: the laminar flat plate (0.664 Re^0.5 Sc^(1/3), the
    plate starting at the disc, so an upper estimate), blended with the still-air value (Churchill-type, cube root)."""
    sh0 = 8.0 / math.pi
    if u <= 0:
        return sh0
    re, sc = u * d_m / NU_AIR, NU_AIR / d_gas
    shf = 0.664 * re ** 0.5 * sc ** (1 / 3)
    return (sh0 ** 3 + shf ** 3) ** (1 / 3)


def g_open_well(ul: float, d_gas: float, u: float, flushed: bool = False) -> float:
    """Conductance (m3/s) from the liquid surface to the air outside an uncapped well: the still air in the bore over
    the liquid (unless `flushed`: the bound where moving air sweeps the whole bore) in series with the air outside."""
    w = WELL
    r = (w["bore_r"] if ul > math.pi * w["throat_r"] ** 2 * w["throat_h"] else w["throat_r"]) * 1e-3
    a = math.pi * r ** 2
    recess = 0.0 if flushed else (w["bore_top"] - well_level(ul)) * 1e-3
    delta = 2 * w["bore_r"] * 1e-3 / sherwood_ext(2 * w["bore_r"] * 1e-3, u, d_gas)
    return d_gas * a / (recess + delta * (r / (w["bore_r"] * 1e-3)))


def g_clearance_cap(d_gas: float) -> float:
    """DAL's clearance cap: liquid surface to the ceiling round the reference, then out through the 0.12 mm skirt gap."""
    w = WELL
    a_ann = math.pi * (w["bore_r"] ** 2 - w["ref_r"] ** 2) * 1e-6
    l_s = (w["ceiling"] - well_level(w["fill_ul"], capped=True)) * 1e-3
    g_s = d_gas * a_ann / l_s
    g_g = d_gas * math.pi * w["boss_d"] * w["skirt_gap"] * 1e-6 / (w["land"] * 1e-3)
    return 1.0 / (1.0 / g_s + 1.0 / g_g)


def g_oring_cap(d_gas: float, vent_len_mm: float | None = None) -> float:
    """DAL's fallback O-ring cap (``electrode_cap_oring``), sealed but for its 0.3 mm vent."""
    w = WELL
    a_ann = math.pi * (w["bore_r"] ** 2 - w["ref_r"] ** 2) * 1e-6
    l_s = (w["ceiling"] - well_level(w["fill_ul"], capped=True)) * 1e-3
    g_s = d_gas * a_ann / l_s
    vl = (vent_len_mm or w["vent_len"]) * 1e-3
    g_v = d_gas * math.pi * (w["vent_d"] * 1e-3 / 2) ** 2 / vl
    return 1.0 / (1.0 / g_s + 1.0 / g_v)


def g_tube(d_gas: float, u: float) -> float:
    r = TUBE["r"] * 1e-3
    delta = 2 * r / sherwood_ext(2 * r, u, d_gas)
    return d_gas * math.pi * r ** 2 / ((TUBE["top"] - TUBE["level"]) * 1e-3 + delta)


def g_vial_open(d_gas: float, u: float) -> float:
    v = VIAL
    a1, a2 = math.pi * (v["body_r"] * 1e-3) ** 2, math.pi * (v["neck_r"] * 1e-3) ** 2
    delta = 2 * v["neck_r"] * 1e-3 / sherwood_ext(2 * v["neck_r"] * 1e-3, u, d_gas)
    res = v["head"] * 1e-3 / (d_gas * a1) + v["neck"] * 1e-3 / (d_gas * a2) + delta / (d_gas * a2)
    return 1.0 / res


def g_cup_open(d_gas: float, u: float) -> float:
    r = CUP["r"] * 1e-3
    delta = 2 * r / sherwood_ext(2 * r, u, d_gas)
    return d_gas * math.pi * r ** 2 / (CUP["recess"] * 1e-3 + delta)


def water_flux_ul_h(g: float, t_c: float, rh: float, a_w: float, t_air: float | None = None) -> float:
    """Evaporation, uL/h, through conductance g (m3/s): liquid at t_c, air of relative humidity rh at t_air."""
    t_air = t_c if t_air is None else t_air
    dc = a_w * c_sat(t_c) - rh * c_sat(t_air)          # kg/m3
    return max(0.0, g * dc) * 3600 * 1e6               # kg/s -> mg/h = uL/h


# ---------------------------------------------------------------------------------------------------------------------
# Conditions: the room, and the inside of a ventilated VLM
# ---------------------------------------------------------------------------------------------------------------------
# services.md (round 12): a VLM holding a printer at work and a furnace needs 1100-2200 m3/h for a 5-10 K rise; over the
# enclosure's 2.83 x 3.12 m plan that is 0.035-0.069 m/s on average. 0.3 m/s stands for a spot near an inlet (assumed).
VLM_PLAN_M2 = 2.83 * 3.12
U_VLM = (1100 / 3600 / VLM_PLAN_M2, 2200 / 3600 / VLM_PLAN_M2)
CASES = {
    "room, still, 40 % RH": dict(t=T_ROOM, rh=0.40, u=0.0),
    "room, still, 20 % RH (dry winter)": dict(t=T_ROOM, rh=0.20, u=0.0),
    "room, still, 60 % RH": dict(t=T_ROOM, rh=0.60, u=0.0),
    # inside the VLM: 5 K over the room (the ventilation's design rise), the room's air at 40 % RH, so 30 % in there
    "VLM, 0.07 m/s, 27 C, room air at 40 %": dict(t=T_ROOM + 5, rh=0.40 * c_sat(T_ROOM) / c_sat(T_ROOM + 5),
                                                    u=round(U_VLM[1], 3)),
    "VLM, 0.3 m/s, 27 C, room air at 20 %": dict(t=T_ROOM + 5, rh=0.20 * c_sat(T_ROOM) / c_sat(T_ROOM + 5), u=0.3),
}

# ---------------------------------------------------------------------------------------------------------------------
# The head's time: CubXL step times, measured
# ---------------------------------------------------------------------------------------------------------------------
STEP_S = dict(pick_up_tip=8.4, aspirate=12.8, dispense=7.2, move_33mm=5.0, decap=7.3, cap=7.0, drop_tip=12.8,
              mix_cycle=46.2 / 3)  # pipette_test_20261007 SUMMARY.md; mix: pipette_test_mix_20261009b (3 cycles)
V_XY, A_XY = 50.0, 300.0           # F3000 mm/min, $120-$122 300 mm/s2 (grbl_before.json)
P20_PLUNGER_S_PER_UL = 5.0 / 20.0  # ASPIRATE 20 took 5.00 s (plunger_trace)


def t_xy(d: float) -> float:
    return d / V_XY + V_XY / A_XY if d > V_XY ** 2 / A_XY else 2 * math.sqrt(d / A_XY)


MOVE_OVERHEAD = STEP_S["move_33mm"] - t_xy(33.0)    # Z up to the safe plane and down again, CubOS's round trips


def t_move(a, b) -> float:
    return MOVE_OVERHEAD + t_xy(math.dist(a, b))


# DAL's deck at 633995b (protocol.md section 2): CubOS deck x, y of each target
DECK = dict(S1=(185.0, 240.0), ASW=(318.0, 101.0), S10=(318.0, 134.0), S01=(318.0, 167.0), DI=(318.0, 200.0),
            ACID=(318.0, 68.0), TUBE=(176.0, 36.0), RACK1=(291.3, 89.0), RACK2=(108.0, 89.0), WASTE=(385.0, 150.0),
            P300RACK=(108.0, 89.0))


def transfer_s(src, dst, ul: float, plunger_s_per_ul: float, back: bool = True) -> float:
    asp = STEP_S["aspirate"] - 20 * P20_PLUNGER_S_PER_UL + ul * plunger_s_per_ul
    return asp + t_move(src, dst) + STEP_S["dispense"] + (t_move(dst, src) if back else 0.0)


def spot_plan(option: str, p300_s_per_ul: float) -> dict:
    """The head's moves for one main spot at 1 mg/L S (135 uL ASW + 15 uL of the 10 mg/L stock), its collection with one
    150 uL DI rinse, and the acid. Returns seconds per phase, transfers and tips."""
    d = DECK
    p20, p300 = P20_PLUNGER_S_PER_UL, p300_s_per_ul
    fill = col = acid = 0.0
    n_tr = tips = 0
    if option == "P20 only (now)":
        fill += STEP_S["pick_up_tip"] + t_move(d["RACK1"], d["ASW"]) + STEP_S["decap"]
        fill += 7 * transfer_s(d["ASW"], d["S1"], 19.3, p20)
        fill += t_move(d["ASW"], d["S10"]) + STEP_S["decap"] + transfer_s(d["S10"], d["S1"], 15.0, p20, back=False)
        fill += t_move(d["S1"], d["S10"]) + STEP_S["cap"] + t_move(d["S10"], d["ASW"]) + STEP_S["cap"]
        fill += t_move(d["ASW"], d["WASTE"]) + STEP_S["drop_tip"]
        n_tr += 8
        tips += 1
        # collect: 8 x 18.75 from S1 to the tube; a new tip draws 8 x 18.75 DI into S1, then carries the rinse to the tube
        col += STEP_S["pick_up_tip"] + 8 * transfer_s(d["S1"], d["TUBE"], 18.75, p20) + STEP_S["drop_tip"]
        col += STEP_S["pick_up_tip"] + STEP_S["decap"] + 8 * transfer_s(d["DI"], d["S1"], 18.75, p20) + STEP_S["cap"]
        col += 8 * transfer_s(d["S1"], d["TUBE"], 18.75, p20) + STEP_S["drop_tip"]
        n_tr += 24
        tips += 2
    elif option in ("P20 + P300", "Flex 1-Channel 1000 uL"):
        flex = option.startswith("Flex")
        big = p300
        # ASW 135 uL in one transfer with the big pipette; flex: the same 200 uL tip then draws the 15 uL of sulfide
        fill += STEP_S["pick_up_tip"] + STEP_S["decap"] + transfer_s(d["ASW"], d["S1"], 135.0, big, back=False)
        fill += t_move(d["S1"], d["ASW"]) + STEP_S["cap"]
        if flex:
            fill += t_move(d["ASW"], d["S10"]) + STEP_S["decap"]
            fill += transfer_s(d["S10"], d["S1"], 15.0, big, back=False) + 3 * STEP_S["mix_cycle"]
            fill += t_move(d["S1"], d["S10"]) + STEP_S["cap"] + STEP_S["drop_tip"]
            tips += 1
        else:
            fill += STEP_S["drop_tip"] + STEP_S["pick_up_tip"] + STEP_S["decap"]
            fill += transfer_s(d["S10"], d["S1"], 15.0, p20, back=False) + 3 * STEP_S["mix_cycle"]
            fill += t_move(d["S1"], d["S10"]) + STEP_S["cap"] + STEP_S["drop_tip"]
            tips += 2
        n_tr += 2
        # collect: 150 uL out; a new tip draws 150 uL DI into S1, mixes, carries it to the tube
        col += STEP_S["pick_up_tip"] + transfer_s(d["S1"], d["TUBE"], 150.0, big) + STEP_S["drop_tip"]
        col += STEP_S["pick_up_tip"] + STEP_S["decap"] + transfer_s(d["DI"], d["S1"], 150.0, big) + STEP_S["cap"]
        col += 2 * STEP_S["mix_cycle"] + transfer_s(d["S1"], d["TUBE"], 150.0, big) + STEP_S["drop_tip"]
        n_tr += 3
        tips += 2
    # the acid: the night's one acid tip from rack 2 and back, 20 uL from the capped acid vial, from above the tube rim
    acid += STEP_S["decap"] + STEP_S["pick_up_tip"] + transfer_s(d["ACID"], d["TUBE"], 20.0, p20, back=False)
    acid += t_move(d["TUBE"], d["RACK2"]) + STEP_S["drop_tip"] + t_move(d["RACK2"], d["ACID"]) + STEP_S["cap"]
    n_tr += 1
    return dict(fill_min=fill / 60, collect_min=col / 60, acid_min=acid / 60,
                head_min=(fill + col + acid) / 60, transfers=n_tr, tips_per_spot=tips)


# ---------------------------------------------------------------------------------------------------------------------
# Water lost from a spot
# ---------------------------------------------------------------------------------------------------------------------
SPOT_PHASES = [("leak check, open", 2.0, "open"), ("cap going on, open", 1.0, "open"),
               ("OCP, EIS, LPR, rest, hold, OCP: capped", 52.0, "cap")]   # protocol.md section 4; copper_numbers timing


def fill_schedule(option: str, fill_min: float) -> list[tuple[float, float]]:
    """(time from the first dispense, uL added). P20: 7 x 19.3 + 15, evenly over the fill; one transfer per pipette
    otherwise."""
    if option == "P20 only (now)":
        vols = [19.3] * 7 + [15.0]
    else:
        vols = [135.0, 15.0]
    n = len(vols)
    span = fill_min * 60 * (n - 1) / n if n > 1 else 0.0
    return [(span * i / max(1, n - 1), v) for i, v in enumerate(vols)]


def water_loss_spot(case: dict, option: str, fill_min: float, cap: str = "clearance") -> dict:
    t_c, rh, u = case["t"], case["rh"], case["u"]
    dg = d_water_air(t_c)
    sched = fill_schedule(option, fill_min)
    # the fill: the well is open, its volume steps up at each transfer
    lost, vol, out = 0.0, 0.0, {}
    for i, (t0, v) in enumerate(sched):
        vol += v
        t1 = sched[i + 1][0] if i + 1 < len(sched) else t0
        if t1 > t0:
            lost += water_flux_ul_h(g_open_well(vol, dg, u), t_c, rh, A_W_SEAWATER) * (t1 - t0) / 3600
    out["fill_uL"] = lost
    for name, minutes, kind in SPOT_PHASES:
        if kind == "open":
            g = g_open_well(WELL["fill_ul"], dg, u)
        else:
            g = g_clearance_cap(dg) if cap == "clearance" else g_oring_cap(dg)
        dl = water_flux_ul_h(g, t_c, rh, A_W_SEAWATER) * minutes / 60
        out[name] = dl
        lost += dl
    out["total_uL"] = lost
    out["pct_of_150uL"] = 100 * lost / WELL["fill_ul"]
    out["chloride_rise_pct"] = 100 * (WELL["fill_ul"] / (WELL["fill_ul"] - lost) - 1)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Sulfide lost from the well as H2S: 1-D diffusion in the well's liquid, escape at the top
# ---------------------------------------------------------------------------------------------------------------------
def k_eff_h2s(g_gas: float, ul: float, t_c: float) -> float:
    """Escape velocity (m/s) of total dissolved sulfide at the surface: the gas path's conductance per unit surface,
    times the air/water partition of H2S, times the H2S share of the total."""
    a = surface_area_mm2(ul) * 1e-6
    return g_gas / a * k_aw_h2s(t_c) * h2s_fraction(PH_WELL, t_c)


def sulfide_run(segments, layers, depth_mm: float, n: int = 300, dt: float = 0.5) -> dict:
    """Implicit finite differences on a column of the well's liquid, equivalent depth `depth_mm` (volume / surface).
    `layers`: list of (t_s, thickness_mm, concentration) added on top at t_s (a dispense from above, unmixed), or
    (t_s, None, 'mix') to mix the column. `segments`: list of (t_end_s, k_eff m/s). Returns time series of the total
    left (relative to everything added) and of the concentration at the metal."""
    h = depth_mm * 1e-3
    dz = h / n
    c = np.zeros(n)
    top = 0                                   # number of filled cells, from the bottom
    t, k_i, li = 0.0, 0, 0
    events = sorted(layers, key=lambda x: x[0])
    added = 0.0
    ts, tot, bottom = [], [], []
    t_end = segments[-1][0]
    while t < t_end - 1e-9:
        while li < len(events) and events[li][0] <= t + 1e-9:
            _, thick, conc = events[li]
            if conc == "mix":
                c[:top] = c[:top].mean()
            else:
                m = max(1, int(round(thick * 1e-3 / dz)))
                m = min(m, n - top)
                c[top:top + m] = conc
                top += m
                added += conc * m * dz
            li += 1
        while k_i < len(segments) - 1 and segments[k_i][0] <= t + 1e-9:
            k_i += 1
        k = segments[k_i][1]
        if top > 1:
            # (I - dt D L) c_new = c, Robin at the top cell: flux k c out, no flux at the metal
            m = top
            r = D_S_AQ * dt / dz ** 2
            main = np.full(m, 1 + 2 * r)
            main[0] = 1 + r
            main[-1] = 1 + r + k * dt / dz
            off = np.full(m - 1, -r)
            c[:m] = _thomas(off, main, off, c[:m])
        t += dt
        if int(t / dt) % 20 == 0:
            ts.append(t)
            tot.append(c[:top].sum() * dz / added if added else 1.0)
            bottom.append(c[0])
    return dict(t=np.array(ts), left=np.array(tot), bottom=np.array(bottom))


def _thomas(a, b, c, d):
    n = len(b)
    cp, dp = np.zeros(n - 1), np.zeros(n)
    cp[0], dp[0] = c[0] / b[0], d[0] / b[0]
    for i in range(1, n):
        den = b[i] - a[i - 1] * cp[i - 1]
        if i < n - 1:
            cp[i] = c[i] / den
        dp[i] = (d[i] - a[i - 1] * dp[i - 1]) / den
    x = np.zeros(n)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def sulfide_scenarios(case: dict) -> dict:
    """The 1 mg/L S well (135 uL ASW + 15 uL of 10 mg/L), from the moment the sulfide lands, through the measurement."""
    t_c, u = case["t"], case["u"]
    dg = d_h2s_air(t_c)
    v = WELL["fill_ul"]
    depth = v / surface_area_mm2(v)                     # equivalent depth, mm
    k_open = k_eff_h2s(g_open_well(v, dg, u), v, t_c)
    k_clear = k_eff_h2s(g_clearance_cap(dg), v, t_c)
    k_oring = k_eff_h2s(g_oring_cap(dg), v, t_c)
    asw_mm = 135.0 / surface_area_mm2(v)
    s_mm = 15.0 / surface_area_mm2(v)
    meas = 52 * 60.0
    sc = {}
    # A: DAL's order as drawn: sulfide last, no mixing, leak check (2 min) and cap-on (1 min) open, clearance cap
    sc["A. sulfide last, unmixed; 3 min open; clearance cap (as planned)"] = dict(
        layers=[(0, asw_mm, 0.0), (0, s_mm, 10.0)], segments=[(180, k_open), (180 + meas, k_clear)], t_cap=180)
    sc["B. as A, mixed after the sulfide"] = dict(
        layers=[(0, asw_mm, 0.0), (0, s_mm, 10.0), (0.5, None, "mix")],
        segments=[(180, k_open), (180 + meas, k_clear)], t_cap=180)
    sc["C. mixed; leak check before the sulfide (30 s open); clearance cap"] = dict(
        layers=[(0, asw_mm, 0.0), (0, s_mm, 10.0), (0.5, None, "mix")],
        segments=[(30, k_open), (30 + meas, k_clear)], t_cap=30)
    sc["D. as C, O-ring cap with its 0.3 mm vent"] = dict(
        layers=[(0, asw_mm, 0.0), (0, s_mm, 10.0), (0.5, None, "mix")],
        segments=[(30, k_open), (30 + meas, k_oring)], t_cap=30)
    out = {}
    # E: the bound if evaporative cooling stirs the well (see the notes): well mixed throughout, the gas path limits
    t_e = np.linspace(0, 180 + meas, 400)
    kt = np.where(t_e <= 180, k_open * t_e, k_open * 180 + k_clear * (t_e - 180))
    left_e = np.exp(-kt / (depth * 1e-3))
    win_e = (t_e >= 180) & (t_e <= 180 + meas)
    out["E. bound: the well stirred throughout (convection); 3 min open; clearance cap"] = dict(
        left_at_cap_pct=float(100 * np.interp(180, t_e, left_e)), left_at_end_pct=float(100 * left_e[-1]),
        metal_mean_pct_of_nominal=float(100 * left_e[win_e].mean()),
        metal_at_cap_pct_of_nominal=float(100 * np.interp(180, t_e, left_e)),
        series=dict(t_min=(t_e / 60).round(3).tolist()[::2], left_pct=(100 * left_e).round(2).tolist()[::2],
                    metal_pct=(100 * left_e).round(2).tolist()[::2]), t_cap_min=3.0)
    for name, s in sc.items():
        r = sulfide_run(s["segments"], s["layers"], depth)
        t_cap = s["t_cap"]
        win = (r["t"] >= t_cap) & (r["t"] <= t_cap + meas)
        c_target = 1.0                                   # mg/L, nominal
        out[name] = dict(
            left_at_cap_pct=float(100 * np.interp(t_cap, r["t"], r["left"])),
            left_at_end_pct=float(100 * r["left"][-1]),
            metal_mean_pct_of_nominal=float(100 * r["bottom"][win].mean() / c_target),
            metal_at_cap_pct_of_nominal=float(100 * np.interp(t_cap, r["t"], r["bottom"]) / c_target),
            series=dict(t_min=(r["t"] / 60).round(3).tolist()[::6], left_pct=(100 * r["left"]).round(2).tolist()[::6],
                        metal_pct=(100 * r["bottom"] / c_target).round(2).tolist()[::6]),
            t_cap_min=t_cap / 60)
    meta = dict(k_open_um_s=k_open * 1e6, k_clearance_cap_um_s=k_clear * 1e6, k_oring_cap_um_s=k_oring * 1e6,
                equivalent_depth_mm=depth, h2s_fraction_pct=100 * h2s_fraction(PH_WELL, t_c),
                pk1=pk1_h2s(t_c), k_aw=k_aw_h2s(t_c), d_aq_m2_s=D_S_AQ, d_gas_m2_s=dg,
                diffusion_time_over_depth_min=(depth * 1e-3) ** 2 / D_S_AQ / 60)
    return dict(scenarios=out, constants=meta)


def sulfide_stock_fill(case: dict, fill_min_p20: float, fill_min_big: float) -> dict:
    """The 10 mg/L well is 150 uL of the stock itself: 8 P20 transfers over the fill, or one big transfer."""
    t_c, u = case["t"], case["u"]
    dg = d_h2s_air(t_c)
    v = WELL["fill_ul"]
    depth = v / surface_area_mm2(v)
    k_open = k_eff_h2s(g_open_well(v, dg, u), v, t_c)
    k_clear = k_eff_h2s(g_clearance_cap(dg), v, t_c)
    res = {}
    for name, n_tr, fmin in (("P20, 8 transfers", 8, fill_min_p20), ("one transfer", 1, fill_min_big)):
        vols = [19.3] * 7 + [15.0] if n_tr == 8 else [150.0]
        span = fmin * 60 * (n_tr - 1) / n_tr if n_tr > 1 else 0.0
        layers = [(span * i / max(1, n_tr - 1), vv / surface_area_mm2(v), 10.0) for i, vv in enumerate(vols)]
        t_cap = span + 180
        r = sulfide_run([(t_cap, k_open), (t_cap + 52 * 60, k_clear)], layers, depth)
        res[name] = dict(fill_open_min=t_cap / 60, left_at_cap_pct=float(100 * np.interp(t_cap, r["t"], r["left"])),
                         left_at_end_pct=float(100 * r["left"][-1]))
    return res


def sulfide_stock_opening(case: dict, t_open_s: float, head_ml: float = 4.0) -> dict:
    """H2S lost from an 18 mL sulfide stock each time its cap comes off: the headspace (in equilibrium, assumed swept
    out) plus what leaves the liquid while the vial is open (semi-infinite liquid, escape velocity k at the surface:
    Carslaw & Jaeger's Robin solution)."""
    from math import erfc
    t_c, u = case["t"], case["u"]
    part = k_aw_h2s(t_c) * h2s_fraction(PH_WELL, t_c)
    head = part * head_ml / VIAL["ml"]
    a = math.pi * (VIAL["body_r"] * 1e-3) ** 2
    k = g_vial_open(d_h2s_air(t_c), u) / a * part
    hh = k / D_S_AQ
    x = hh * math.sqrt(D_S_AQ * t_open_s)
    m_per_area = (D_S_AQ / k) * (math.exp(x * x) * erfc(x) - 1 + 2 * x / math.sqrt(math.pi)) if x < 25 else \
        2 * math.sqrt(D_S_AQ * t_open_s / math.pi) - D_S_AQ / k
    open_loss = m_per_area * a / (VIAL["ml"] * 1e-6)
    return dict(t_open_s=t_open_s, headspace_pct=100 * head, open_pct=100 * open_loss,
                per_opening_pct=100 * (head + open_loss))


# ---------------------------------------------------------------------------------------------------------------------
# Tubes overnight, stock vials, rinse cups
# ---------------------------------------------------------------------------------------------------------------------
PDMS_P_WATER_BARRER = 36000.0      # water vapour in PDMS, literature range about 20,000-40,000 Barrer (assumed value)
PDMS_T_MM = 2.0                    # the cap's PDMS fill over the vial's mouth: assumed


def pdms_cap_ul_day(t_c: float, rh: float) -> float:
    p = PDMS_P_WATER_BARRER * 1e-10                    # cm3(STP) cm / (cm2 s cmHg)
    a = math.pi * (VIAL["neck_r"] / 10) ** 2          # cm2
    dp = p_sat(t_c) * (A_W_SEAWATER - rh) / 1333.22   # cmHg
    q = p * a * dp / (PDMS_T_MM / 10)                 # cm3(STP)/s
    return q / 22414.0 * 18.015 * 1000 * 86400       # mg/day = uL/day


def leaky_cap_ul_day(t_c: float, rh: float, gap_mm: float = 0.05, land_mm: float = 2.0) -> float:
    dg = d_water_air(t_c)
    g_gap = dg * math.pi * 2 * VIAL["neck_r"] * 1e-3 * gap_mm * 1e-3 / (land_mm * 1e-3)
    a1, a2 = math.pi * (VIAL["body_r"] * 1e-3) ** 2, math.pi * (VIAL["neck_r"] * 1e-3) ** 2
    g_in = 1.0 / (VIAL["head"] * 1e-3 / (dg * a1) + VIAL["neck"] * 1e-3 / (dg * a2))
    g = 1.0 / (1.0 / g_in + 1.0 / g_gap)
    return water_flux_ul_h(g, t_c, rh, A_W_SEAWATER) * 24


# ---------------------------------------------------------------------------------------------------------------------
# Accuracy at the volumes moved (filled from Opentrons' published specifications; see SPECS)
# ---------------------------------------------------------------------------------------------------------------------
# Opentrons' published figures (read 2026-11-20). OT-2 GEN2: the GEN2 pipette white paper, Table 1; Flex: the
# "Pipette Accuracy" tech data sheet (May 2026), by tip
_WP = "https://insights.opentrons.com/hubfs/Products/Pipettes/GEN2%20Pipette%20White%20Paper.pdf"
_TDS = "https://insights.opentrons.com/hubfs/Products/Pipettes/Tech%20Data%20Sheet_Pipette%20Accuracy.pdf"
SPECS: dict[str, dict] = {
    "P20": dict(points=[(1.0, 15.0, 5.0), (10.0, 2.0, 1.0), (20.0, 1.5, 0.8)], source=_WP),
    "P300": dict(points=[(20.0, 4.0, 2.5), (150.0, 1.0, 0.4), (300.0, 0.6, 0.3)], source=_WP),
    "Flex 1000, 50 uL tip": dict(points=[(5.0, 5.0, 2.5), (50.0, 0.5, 0.3)], source=_TDS),
    "Flex 1000, 200 uL tip": dict(points=[(200.0, 0.5, 0.15)], source=_TDS),
    "Flex 50, 50 uL tip": dict(points=[(1.0, 8.0, 7.0), (10.0, 1.5, 0.5), (50.0, 1.25, 0.4)], source=_TDS),
}
# plunger: ul per mm of travel (Opentrons shared-data pipetteModelSpecs.json piecewise tables at these volumes)
UL_PER_MM = {"P20": 0.76, "P300": 9.18}
PRICES_USD = {"OT-2 GEN2 P20 single (999-00002)": 2950, "OT-2 GEN2 P300 single (999-00003)": 2950,
              "Flex 1-Channel 5-1000 uL (999-00187)": 3600, "Flex 1-Channel 1-50 uL (999-00186)": 3600,
              "OT-2 20 or 300 uL tips, per rack of 96": 8.50, "Flex tips, per rack of 96": 16.0}


def spec_at(name: str, ul: float) -> tuple[float, float]:
    pts = sorted(SPECS[name]["points"])
    v = [p[0] for p in pts]
    if ul < v[0] or ul > v[-1]:
        return float("nan"), float("nan")
    lv = np.log(v)
    return (float(np.interp(math.log(ul), lv, [p[1] for p in pts])),
            float(np.interp(math.log(ul), lv, [p[2] for p in pts])))


def series_error(name: str, ul: float, n: int) -> dict:
    """n equal transfers: the systematic error adds in step (same %), the random error falls as 1/sqrt(n)."""
    pts = SPECS[name]["points"]
    if len(pts) == 1:                                  # one published point: only that volume is specified
        sys_, cv = (pts[0][1], pts[0][2]) if abs(ul - pts[0][0]) < 1e-6 else (float("nan"), float("nan"))
        return dict(per_transfer_uL=ul, n=n, systematic_pct=sys_, cv_pct=cv, note=f"specified at {pts[0][0]} uL only")
    sys_, cv = spec_at(name, ul)
    return dict(per_transfer_uL=ul, n=n, systematic_pct=sys_, cv_pct=cv / math.sqrt(n) if cv == cv else cv)


def main(argv):
    OUT.mkdir(exist_ok=True)
    res = dict(inputs=dict(well=WELL, tube=TUBE, vial=VIAL, cup=CUP, steps_s=STEP_S, u_vlm_m_s=U_VLM,
                           cases=CASES, deck=DECK))
    p300_s_per_ul = P300_PLUNGER_S_PER_UL
    plans = {o: spot_plan(o, p300_s_per_ul) for o in ("P20 only (now)", "P20 + P300", "Flex 1-Channel 1000 uL")}
    res["head_time"] = plans
    water = {}
    for cname, case in CASES.items():
        water[cname] = {o: water_loss_spot(case, o, plans[o]["fill_min"]) for o in plans}
        water[cname]["P20 only (now), O-ring cap"] = water_loss_spot(case, "P20 only (now)",
                                                                    plans["P20 only (now)"]["fill_min"], cap="oring")
        dg = d_water_air(case["t"])
        water[cname]["rates_uL_h"] = dict(
            open_well=water_flux_ul_h(g_open_well(150, dg, case["u"]), case["t"], case["rh"], A_W_SEAWATER),
            open_well_bore_flushed_bound=water_flux_ul_h(g_open_well(150, dg, case["u"], flushed=True), case["t"],
                                                         case["rh"], A_W_SEAWATER),
            clearance_cap=water_flux_ul_h(g_clearance_cap(dg), case["t"], case["rh"], A_W_SEAWATER),
            oring_cap_vent=water_flux_ul_h(g_oring_cap(dg), case["t"], case["rh"], A_W_SEAWATER),
            tube_320uL=water_flux_ul_h(g_tube(dg, case["u"]), case["t"], case["rh"], A_W_TUBE),
            stock_vial_open=water_flux_ul_h(g_vial_open(dg, case["u"]), case["t"], case["rh"], A_W_SEAWATER),
            rinse_cup_open=water_flux_ul_h(g_cup_open(dg, case["u"]), case["t"], case["rh"], A_W_SEAWATER))
        water[cname]["stock_cap_uL_day"] = dict(pdms_sealed=pdms_cap_ul_day(case["t"], case["rh"]),
                                                gap_50um=leaky_cap_ul_day(case["t"], case["rh"]))
    res["water"] = water
    base = CASES["room, still, 40 % RH"]
    res["sulfide"] = {c: sulfide_scenarios(CASES[c]) for c in ("room, still, 40 % RH",
                                                                "VLM, 0.07 m/s, 27 C, room air at 40 %")}
    res["sulfide_10mgL_well"] = sulfide_stock_fill(base, plans["P20 only (now)"]["fill_min"],
                                                   plans["P20 + P300"]["fill_min"] / 2)
    # copper as a sulfide sink (not modelled): Cu(I) released over a 63 min spot at DAL's 1-11 uA/cm2, wetted 0.10-0.126
    f = 96485.0
    cu_nmol = [i * 1e-6 * a * 63 * 60 / f * 1e9 for i, a in ((1.0, 0.101), (11.0, 0.126))]
    res["copper_sink"] = dict(cu_I_nmol_63min=cu_nmol, s_bound_as_cu2s_nmol=[x / 2 for x in cu_nmol],
                              s_in_well_nmol={"1 mg/L": 0.150e-6 / 32.06e-6 * 1e3, "10 mg/L": 1.5e-6 / 32.06e-6 * 1e3})
    # does evaporative cooling stir the well (scenario E's premise)? Heat leaves the surface at J x 2450 J/g and comes up
    # through the liquid from the metal; Pearson's onset of Marangoni convection is Ma about 80 (conducting floor, free
    # top), Rayleigh's 1101 (rigid floor, free top)
    marg = {}
    dgw = d_water_air(T_ROOM)
    for nm, gw in (("open well", g_open_well(150, dgw, 0.0)), ("clearance cap", g_clearance_cap(dgw)),
                   ("O-ring cap", g_oring_cap(dgw))):
        j = water_flux_ul_h(gw, T_ROOM, 0.40, A_W_SEAWATER)
        q = j * 1e-3 / 3600 * 2450.0 / (surface_area_mm2(150) * 1e-6)
        hh = 150 / surface_area_mm2(150) * 1e-3
        dt_k = q * hh / 0.60
        marg[nm] = dict(evaporation_uL_h=j, cooling_W_m2=q, surface_cooler_by_K=dt_k,
                        marangoni=1.5e-4 * dt_k * hh / (0.955e-3 * 1.43e-7),
                        rayleigh=9.81 * 2.2e-4 * dt_k * hh ** 3 / (0.955e-6 * 1.43e-7))
    res["evaporative_cooling"] = dict(cases=marg, onset_marangoni=80, onset_rayleigh=1101)
    # the sulfide stock, opened for one draw (cap off, aspirate, to S1 and back, cap on: about 40 s) or for the eight
    # P20 draws of a well made of stock alone (0.1 or 10 mg/L): the P20 fill time
    one = STEP_S["decap"] + transfer_s(DECK["S10"], DECK["S1"], 15.0, P20_PLUNGER_S_PER_UL) + STEP_S["cap"]
    res["sulfide_stock_per_opening"] = {
        "one draw": sulfide_stock_opening(base, one),
        "eight P20 draws (a well of stock alone)": sulfide_stock_opening(base, plans["P20 only (now)"]["fill_min"] * 60),
        "one P300 draw (a well of stock alone)": sulfide_stock_opening(
            base, STEP_S["decap"] + transfer_s(DECK["S10"], DECK["S1"], 150.0, p300_s_per_ul) + STEP_S["cap"])}
    if SPECS:
        acc = {}
        acc["P20 only (now)"] = dict(asw=series_error("P20", 19.3, 7), sulfide=series_error("P20", 15.0, 1),
                                     collect=series_error("P20", 18.75, 8), acid=series_error("P20", 20.0, 1))
        acc["P20 + P300"] = dict(asw=series_error("P300", 135.0, 1), sulfide=series_error("P20", 15.0, 1),
                                 collect=series_error("P300", 150.0, 1), acid=series_error("P20", 20.0, 1))
        acc["Flex 1-Channel 1000 uL"] = dict(
            asw_200uL_tip=series_error("Flex 1000, 200 uL tip", 135.0, 1),
            asw_50uL_tip_3x45=series_error("Flex 1000, 50 uL tip", 45.0, 3),
            sulfide_50uL_tip=series_error("Flex 1000, 50 uL tip", 15.0, 1),
            collect_200uL_tip=series_error("Flex 1000, 200 uL tip", 150.0, 1),
            acid_50uL_tip=series_error("Flex 1000, 50 uL tip", 20.0, 1))
        acc["P300 at 20 uL (if it took the acid)"] = dict(acid=series_error("P300", 20.0, 1))
        res["prices_usd"] = PRICES_USD
        res["accuracy"] = acc
        res["specs"] = SPECS
    (OUT / "cubxl_evap.json").write_text(json.dumps(res, indent=1, default=float))
    if "nofig" not in argv:
        figure(res)
    return res


# the plunger runs at the P20's measured 26.8 mm in 5.0 s; the P300 moves 9.18 uL a mm against the P20's 0.76
P300_PLUNGER_S_PER_UL = P20_PLUNGER_S_PER_UL * UL_PER_MM["P20"] / UL_PER_MM["P300"]


SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")          # categorical slots 1-4, fixed order (validated)
BLUES = ("#9ec5f4", "#4a90e2", "#1d5aa8")                       # one hue, light -> dark: milder -> harsher air
FIG_CASES = ("room, still, 40 % RH", "room, still, 20 % RH (dry winter)", "VLM, 0.07 m/s, 27 C, room air at 40 %")
FIG_CASE_LABEL = ("room 22 C, 40 % RH, still", "room 22 C, 20 % RH (dry winter), still",
                  "inside the VLM: 27 C, 30 % RH, 0.07 m/s")


def _style(ax, title):
    ax.set_facecolor(SURFACE)
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
    for k in ("left", "bottom"):
        ax.spines[k].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=8)


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(13.5, 9.0), dpi=150, facecolor=SURFACE)
    # (a) water lost from the well in one spot
    ax = axs[0, 0]
    rows = ("P20 only (now)", "P20 + P300", "Flex 1-Channel 1000 uL", "P20 only (now), O-ring cap")
    labels = ("P20 only (now), clearance cap", "P20 + P300, clearance cap", "Flex 1000, clearance cap",
              "P20 only, O-ring cap + 0.3 mm vent")
    hgt = 0.26
    for j, c in enumerate(FIG_CASES):
        vals = [res["water"][c][r]["pct_of_150uL"] for r in rows]
        y = np.arange(len(rows)) + (j - 1) * (hgt + 0.02)
        ax.barh(y, vals, height=hgt, color=BLUES[j], label=FIG_CASE_LABEL[j], edgecolor=SURFACE, lw=1)
        for yy, v in zip(y, vals):
            ax.text(v + 0.04, yy, f"{v:.1f} %", va="center", fontsize=8, color=INK2)
    ax.set_yticks(np.arange(len(rows)), labels, fontsize=9, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 3.3)
    ax.set_xlabel("water lost from the 150 \u00b5L well in one spot, % (fill, leak check, cap on, 52 min capped)",
                  fontsize=9, color=INK2)
    ax.grid(axis="y", visible=False)
    _style(ax, "a  Water: 1-3 % of the well per spot, whatever the pipette")
    ax.legend(fontsize=8, frameon=False, loc="lower right", labelcolor=INK2)
    # (b) the open collection tubes, waiting for the morning
    ax = axs[0, 1]
    hrs = np.linspace(0, 12, 121)
    for j, c in enumerate(FIG_CASES):
        rate = res["water"][c]["rates_uL_h"]["tube_320uL"]
        pct = 100 * rate * hrs / TUBE["ul"]
        ax.plot(hrs, pct, color=BLUES[j], lw=2, label=FIG_CASE_LABEL[j])
        ax.text(12.15, pct[-1], f"{pct[-1]:.0f} %", va="center", fontsize=8, color=INK2)
    ax.axvspan(3, 11, color=GRID, alpha=0.5, lw=0)
    ax.text(7, 0.6, "the last to the first tube of an 8-spot night,\nif a person caps them 3 h after the last spot",
            ha="center", fontsize=8, color=INK2)
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, None)
    ax.set_xlabel("hours the open 0.5 mL tube (320 \u00b5L) waits", fontsize=9, color=INK2)
    ax.set_ylabel("% of the tube's liquid evaporated", fontsize=9, color=INK2)
    lo = 100 * res["water"][FIG_CASES[0]]["rates_uL_h"]["tube_320uL"] * 3 / TUBE["ul"]
    hi = 100 * res["water"][FIG_CASES[-1]]["rates_uL_h"]["tube_320uL"] * 11 / TUBE["ul"]
    _style(ax, f"b  Open ICP-MS tubes, waiting for the morning: {lo:.0f}-{hi:.0f} %")
    ax.legend(fontsize=8, frameon=False, loc="upper left", labelcolor=INK2)
    # (c), (d) sulfide in the 1 mg/L well
    sc = res["sulfide"]["room, still, 40 % RH"]["scenarios"]
    keys = [k for k in sc if not k.startswith("E")]
    short = {"A": "A  as planned: sulfide last, unmixed,\n   3 min open, clearance cap",
             "B": "B  mixed after the sulfide", "C": "C  mixed, leak check first (30 s open)",
             "D": "D  mixed, leak check first,\n   O-ring cap with 0.3 mm vent"}
    for ax, field, title, ylab in (
            (axs[1, 0], "left_pct", "c  Sulfide left in the 1 mg/L well, as H\u2082S escapes",
             "% of the sulfide dose still in the well"),
            (axs[1, 1], "metal_pct", "d  Sulfide at the metal (the well's floor)",
             "% of the nominal 1 mg/L at the metal")):
        e = sc[[k for k in sc if k.startswith("E")][0]]["series"]
        ax.plot(e["t_min"], e[field], color=MUTED, lw=1.2, ls=(0, (4, 3)))
        ends = {k[0]: sc[k]["series"][field][-1] for k in keys}
        nudge = {"B": -3.5, "C": +3.5} if abs(ends["B"] - ends["C"]) < 7 else {}
        for j, k in enumerate(keys):
            se = sc[k]["series"]
            ax.plot(se["t_min"], se[field], color=SERIES[j], lw=2)
            ax.text(se["t_min"][-1] + 0.8, se[field][-1] + nudge.get(k[0], 0.0), short[k[0]], va="center",
                    fontsize=7.5, color=INK2, linespacing=1.0)
        ax.text(5.2, 47, "E  bound: the whole well stirred\n   by evaporative cooling", va="center", fontsize=7.5,
                color=MUTED)
        ax.axvline(3, color=AXIS, lw=1)
        ax.text(3.6, 103, "cap on (A, B)", fontsize=7.5, color=INK2)
        ax.set_xlim(0, 80)
        ax.set_ylim(0, 110)
        ax.set_xticks([0, 10, 20, 30, 40, 50])
        ax.set_xlabel("minutes after the sulfide goes in (the measurement ends at 55 min)", fontsize=9,
                      color=INK2)
        ax.set_ylabel(ylab, fontsize=9, color=INK2)
        _style(ax, title)
    fig.suptitle("CubXL corrosion well (DAL PR #180): evaporation and sulfide loss, first-order estimates "
                 "(cubxl_evap.py)", x=0.01, ha="left", fontsize=12.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT / "cubxl_evap.png", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1:])

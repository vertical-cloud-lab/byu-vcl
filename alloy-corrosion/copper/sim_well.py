"""Transport in one CubXL corrosion well against a bulk cell, for copper alloys.

Writes sim_well.json (every number the README quotes), sim_well.png (the
figure) and sim_well_fields.npz (O2 and Cu(I) fields that render_cubxl_cu.py
draws inside the animated well).

What it models. A 2D axisymmetric finite-volume model of the well that the
aluminium plan proposes (../cubxl-setup.md section 3, ../plot_deck_layout.py
draw_well): the AS568-006 FKM O-ring sets the exposed spot (ID 2.90 mm), the
lid's 1.6 mm throat sits above it, an 8 mm bore above that holds the rest of
150 uL, and the electrode cap's 2 mm reference capillary comes down the axis to
1.5 mm above the metal, with a Pt coil around it. The cap seals the headspace,
so the liquid surface stays air-saturated and nothing evaporates.

Two dissolved species diffuse in the liquid:
- O2, consumed at the spot by O2 + 2H2O + 4e- -> 4OH- with Tafel kinetics,
  supplied only by the air-saturated free surface;
- Cu(I) (CuCl2-), made at the spot by anodic dissolution (n = 1, as in
  chloride), carried as a tracer: its concentration does not feed back on the
  kinetics.

At open circuit the metal is equipotential and its net current is zero, so the
mixed potential is solved at every time step. The bulk cell it is compared with
is a 1 cm2 spot in about 200 mL, where natural convection holds a Nernst
diffusion layer of delta = 0.2-0.5 mm (0.3 mm by default) and the dissolved Cu
is diluted away.

The kinetics are set relative to the bulk cell, not taken from any one paper:
each case fixes the bulk-cell corrosion current i_corr,b and puts the bulk
E_corr at 0, with an anodic Tafel slope b_a = 60 mV/dec and a cathodic one
b_c = 120 mV/dec. The well then sees the same metal with less oxygen. The
question it answers is the calibration question of c1-01: how far can the well
alone move E_corr, R_p and the dissolved-Cu signal, and how fast.

Not modelled: double-layer charging, the Cu2O film's growth, Cu(I) oxidation to
Cu(II) and its precipitation, the counter's own products (OH-, Cl2) beyond its
O2 demand, migration, and natural convection inside the well. Each is named in
the README where it matters.

    python sim_well.py          # about 3 min on 4 cores
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
F = 96485.332  # C/mol
LN10 = math.log(10.0)

# --- Electrolyte: ASTM D1141 substitute ocean water, 25 C. ASSUMED values, not measured here ---
C_O2_SAT = 0.21e-6   # mol/cm3: air-saturated seawater, S = 35, 25 C (about 6.7 mg/L)
D_O2 = 2.0e-5        # cm2/s, O2 in seawater, as ../copper-ded-edison/check_numbers.py
D_CU = 8.0e-6        # cm2/s, CuCl2-: ASSUMED, typical of a singly charged complex ion
KAPPA = 0.053        # S/cm, seawater S = 35 at 25 C
DELTA_BULK = (0.02, 0.03, 0.05)  # cm, natural-convection Nernst layer in a bulk cell
B_A, B_C = 0.060, 0.120  # V/decade, ASSUMED Tafel slopes

H = 0.005  # cm: 0.05 mm grid
DT = 1.0   # s


@dataclass
class Geometry:
    """Axisymmetric well. Lengths in cm. z = 0 is the metal face."""
    name: str
    a: float = 0.145          # spot radius: AS568-006 ID 2.90 mm
    z_step: float = 0.16      # throat height (lid bore below the 8 mm bore)
    r_bore: float = 0.40      # 8 mm bore
    v_ul: float = 150.0
    r_cap: float = 0.10       # 2 mm reference capillary on the axis
    z_tip: float | None = 0.15  # capillary tip height; None = no capillary in the liquid
    coil: bool = True         # five turns of 0.25 mm Pt at r 2.5-2.75 mm
    nr: int = field(init=False)
    nz: int = field(init=False)
    h_liq: float = field(init=False)

    def __post_init__(self):
        v = self.v_ul * 1e-3
        throat = math.pi * self.a ** 2 * self.z_step
        if self.z_tip is None:
            self.h_liq = self.z_step + (v - throat) / (math.pi * self.r_bore ** 2)
        else:
            # the capillary displaces liquid wherever it is submerged
            below_step = math.pi * self.r_cap ** 2 * max(self.z_step - self.z_tip, 0.0)
            start = max(self.z_tip, self.z_step)
            ann = math.pi * (self.r_bore ** 2 - self.r_cap ** 2)
            # liquid between z_step and start (if the tip is above the step) is a full disc
            full = math.pi * self.r_bore ** 2 * (start - self.z_step)
            self.h_liq = start + (v - throat + below_step - full) / ann
        self.nr = round(self.r_bore / H)
        self.nz = round(self.h_liq / H)


def build_mask(g: Geometry):
    r = (np.arange(g.nr) + 0.5) * H
    z = (np.arange(g.nz) + 0.5) * H
    R, Z = np.meshgrid(r, z, indexing="ij")
    liquid = ((R < g.a) & (Z < g.z_step)) | ((R < g.r_bore) & (Z >= g.z_step))
    if g.z_tip is not None:
        liquid &= ~((R < g.r_cap) & (Z >= g.z_tip))
    coil = np.zeros_like(liquid)
    if g.coil:
        for zc in (0.24, 0.28, 0.32, 0.36, 0.40):
            if zc + 0.0125 < g.h_liq:
                coil |= (R > 0.25) & (R < 0.275) & (np.abs(Z - zc) < 0.0125)
    liquid &= ~coil
    return r, z, liquid, coil


class Model:
    """Finite volumes on the liquid cells; implicit Euler; Woodbury update for the spot."""

    def __init__(self, g: Geometry):
        self.g = g
        self.r, self.z, self.liq, self.coil = build_mask(g)
        idx = -np.ones(self.liq.shape, dtype=int)
        idx[self.liq] = np.arange(self.liq.sum())
        self.idx = idx
        self.n = int(self.liq.sum())
        self.vol = np.zeros(self.n)
        nr, nz = self.liq.shape
        rows, cols, vals = [], [], []  # unit-D conductances between liquid cells
        self.surf_g = np.zeros(self.n)  # unit-D half-cell conductance to the free surface
        self.coil_area = np.zeros(self.n)  # wetted coil area next to each liquid cell
        for i in range(nr):
            for k in range(nz):
                p = idx[i, k]
                if p < 0:
                    continue
                ri = self.r[i]
                self.vol[p] = 2 * math.pi * ri * H * H
                if i + 1 < nr and idx[i + 1, k] >= 0:
                    gfac = 2 * math.pi * (i + 1) * H * H / H
                    q = idx[i + 1, k]
                    rows += [p, q]; cols += [q, p]; vals += [gfac, gfac]
                if k + 1 < nz and idx[i, k + 1] >= 0:
                    gfac = 2 * math.pi * ri * H / H
                    q = idx[i, k + 1]
                    rows += [p, q]; cols += [q, p]; vals += [gfac, gfac]
                if k == nz - 1:
                    self.surf_g[p] = 2 * math.pi * ri * H / (H / 2)
                # faces shared with the Pt coil
                for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ii, kk = i + di, k + dk
                    if 0 <= ii < nr and 0 <= kk < nz and self.coil[ii, kk]:
                        area = 2 * math.pi * (ri + di * H / 2) * H if di else 2 * math.pi * ri * H
                        self.coil_area[p] += area
        off = sp.coo_matrix((vals, (rows, cols)), shape=(self.n, self.n)).tocsr()
        self.lap = off - sp.diags(np.asarray(off.sum(axis=1)).ravel())  # unit-D Laplacian (negative definite)
        # spot cells: bottom row, r < a
        self.spot = np.array([idx[i, 0] for i in range(nr) if self.r[i] < g.a and idx[i, 0] >= 0])
        self.spot_area = np.array([2 * math.pi * self.r[i] * H for i in range(nr) if self.r[i] < g.a and idx[i, 0] >= 0])
        self.A = self.spot_area.sum()
        self._lu = {}

    # -- linear algebra ------------------------------------------------------
    def factor(self, key, D, dirichlet_surface, extra_diag=None):
        if key in self._lu:
            return self._lu[key]
        diag = self.vol / DT + (D * self.surf_g if dirichlet_surface else 0.0)
        if extra_diag is not None:
            diag = diag + extra_diag
        M = sp.diags(diag) - D * self.lap
        lu = spla.splu(M.tocsc())
        P = np.zeros((self.n, len(self.spot)))
        P[self.spot, np.arange(len(self.spot))] = 1.0
        Z = lu.solve(P)
        W = Z[self.spot, :]
        self._lu[key] = (lu, Z, W)
        return self._lu[key]

    def to_grid(self, c):
        out = np.full(self.liq.shape, np.nan)
        out[self.liq] = c
        return out


def k_eff(kc, D):
    """Series of surface kinetics and the half-cell diffusion distance."""
    return kc * (D / (H / 2)) / (kc + D / (H / 2))


@dataclass
class Kinetics:
    """Relative to the bulk cell: bulk E_corr = 0 V, bulk i_corr = icorr (A/cm2)."""
    icorr: float
    delta: float = 0.03

    def __post_init__(self):
        ilim = 4 * F * C_O2_SAT * D_O2 / self.delta
        if self.icorr >= ilim:
            raise ValueError("bulk i_corr must be below the bulk O2 limit")
        self.kc0 = 1.0 / (4 * F * C_O2_SAT / self.icorr - self.delta / D_O2)
        self.theta_kin = (1 / self.kc0) / (1 / self.kc0 + self.delta / D_O2)

    def ia(self, E):
        return self.icorr * 10 ** (E / B_A)

    def kc(self, E):
        return self.kc0 * 10 ** (-E / B_C)

    def bulk_ic(self, E, delta=None):
        d = self.delta if delta is None else delta
        return 4 * F * C_O2_SAT / (1 / self.kc(E) + d / D_O2)

    def bulk_rp(self):
        """Ohm cm2, linearised at the bulk E_corr."""
        return 1.0 / (self.icorr * LN10 * (1 / B_A + self.theta_kin / B_C))


def run(model: Model, kin: Kinetics | None, steps, snap_times=(), limiting=False):
    """steps: list of (name, seconds, mode, value). mode: 'ocp', 'hold' (E = value, V vs bulk
    E_corr), 'hold_rel' (E = last OCP + value), 'lpr' (sweep +/- value V about last OCP at
    0.167 mV/s, from -value), 'cathodic_rel' (hold at last OCP + value, dissolved Cu(I) replates
    at the spot). limiting=True: the spot is an O2 sink at c = 0 (k -> infinity), no Cu."""
    m = model
    cO = np.full(m.n, C_O2_SAT)
    cC = np.zeros(m.n)
    t, E, E_ocp = 0.0, 0.0, 0.0
    rec = {"t": [], "E": [], "I": [], "ic": [], "ia": [], "o2_spot": [], "cu_mol": [], "cu_spot": [], "phase": [], "counter_o2_mol": 0.0, "replated_mol": 0.0}
    snaps = {}
    snap_times = sorted(snap_times)
    si = 0
    I_prev = 0.0
    for name, dur, mode, val in steps:
        nsteps = int(round(dur / DT))
        replate = mode == "cathodic_rel"
        cu_extra = None
        if replate:
            cu_extra = np.zeros(m.n)
            cu_extra[m.spot] = m.spot_area * D_CU / (H / 2)
        luO, ZO, WO = m.factor("O2", D_O2, True)
        luC, _, _ = m.factor("Cu_replate" if replate else "Cu", D_CU, False, cu_extra)
        E_start = E_ocp
        for s in range(nsteps):
            bO = m.vol / DT * cO + D_O2 * m.surf_g * C_O2_SAT
            # the counter reduces O2 at whatever current the metal is passing anodically (explicit)
            if I_prev > 0 and m.coil_area.sum() > 0:
                demand = I_prev / (4 * F) * DT  # mol this step
                avail = (m.vol * cO * (m.coil_area > 0)).sum()
                take = min(demand, 0.5 * avail)
                bO -= (take / DT) * (m.coil_area / m.coil_area.sum())
                rec["counter_o2_mol"] += take
            yO = luO.solve(bO)
            ys = yO[m.spot]

            def o2_terms(Ev):
                if limiting:
                    d = m.spot_area * (D_O2 / (H / 2))
                else:
                    d = m.spot_area * k_eff(kin.kc(Ev), D_O2)
                sO = np.linalg.solve(np.eye(len(d)) + WO * d[None, :], ys)
                return d, sO

            def net(Ev):
                d, sO = o2_terms(Ev)
                return kin.ia(Ev) * m.A - 4 * F * float(d @ sO)

            if limiting:
                Ev = 0.0
            elif mode == "ocp":
                lo, hi = E - 0.4, E + 0.4
                Ev = brentq(net, lo, hi, xtol=1e-7)
            elif mode == "hold":
                Ev = val
            elif mode in ("hold_rel", "cathodic_rel"):
                Ev = E_start + val
            elif mode == "lpr":
                Ev = E_start - val + 1.667e-4 * (s + 1) * DT
            else:
                raise ValueError(mode)
            d, sO = o2_terms(Ev)
            cO = yO - ZO @ (d * sO)
            np.clip(cO, 0.0, None, out=cO)
            Ic = -4 * F * float(d @ sO)
            Ia = 0.0 if limiting else kin.ia(Ev) * m.A
            bC = m.vol / DT * cC
            if not limiting:
                bC[m.spot] += m.spot_area * kin.ia(Ev) / F
            cC_new = luC.solve(bC)
            if replate:
                rec["replated_mol"] += float((m.spot_area * D_CU / (H / 2) * cC_new[m.spot]).sum()) * DT
            cC = cC_new
            E = Ev
            if mode == "ocp":
                E_ocp = Ev
            t += DT
            I_prev = Ia + Ic
            rec["t"].append(t); rec["E"].append(Ev); rec["I"].append(I_prev)
            rec["ic"].append(Ic / m.A); rec["ia"].append(Ia / m.A)
            rec["o2_spot"].append(float(cO[m.spot[0]])); rec["cu_mol"].append(float((m.vol * cC).sum()))
            rec["cu_spot"].append(float(cC[m.spot[0]])); rec["phase"].append(name)
            while si < len(snap_times) and t >= snap_times[si] - 1e-9:
                snaps[snap_times[si]] = (m.to_grid(cO), m.to_grid(cC))
                si += 1
    for k in ("t", "E", "I", "ic", "ia", "o2_spot", "cu_mol", "cu_spot"):
        rec[k] = np.asarray(rec[k])
    return rec, snaps


def at(rec, key, t_s):
    i = int(np.searchsorted(rec["t"], t_s - 1e-9))
    return float(rec[key][min(i, len(rec[key]) - 1)])


def cottrell(t):
    return 4 * F * C_O2_SAT * np.sqrt(D_O2 / (np.pi * t))


# ---------------------------------------------------------------------------
def laplace(g: Geometry):
    """Primary current distribution: spot at 0 V, Pt coil at 1 V, every other boundary
    insulating. Returns the total resistance, the uncompensated resistance seen at the
    capillary tip, and the spread of current density across the spot."""
    m = Model(g)
    diag = np.zeros(m.n)
    b = np.zeros(m.n)
    gs = m.spot_area * KAPPA / (H / 2)
    diag[m.spot] += gs
    gc = m.coil_area * KAPPA / (H / 2)
    diag += gc
    b += gc * 1.0
    M = sp.diags(diag) - KAPPA * m.lap
    phi = spla.spsolve(M.tocsc(), b)
    I = float((gs * phi[m.spot]).sum())  # A per volt
    jj = gs * phi[m.spot] / m.spot_area
    out = {"R_cell_ohm": 1.0 / I}
    if g.z_tip is not None:
        k_tip = round(g.z_tip / H) - 1
        cells = [m.idx[i, k_tip] for i in range(g.nr) if m.r[i] < g.r_cap and m.idx[i, k_tip] >= 0]
        w = np.array([m.vol[c] for c in cells])
        phi_ref = float((phi[cells] * w).sum() / w.sum())
        out["R_u_ohm"] = phi_ref / I
    out["spot_j_edge_over_mean"] = float(jj[-1] / (jj * m.spot_area).sum() * m.A)
    out["spot_j_centre_over_mean"] = float(jj[0] / (jj * m.spot_area).sum() * m.A)
    return out


# ---------------------------------------------------------------------------
def main():
    out = {"assumed": {"C_O2_sat_mM": C_O2_SAT * 1e6, "D_O2_cm2_s": D_O2, "D_CuCl2_cm2_s": D_CU,
                       "kappa_S_cm": KAPPA, "bulk_delta_mm": [d * 10 for d in DELTA_BULK],
                       "b_a_V_dec": B_A, "b_c_V_dec": B_C, "grid_mm": H * 10, "dt_s": DT}}

    G1 = Geometry("A: the aluminium plan's cap (tip 1.5 mm up, in the throat)")
    G2 = Geometry("B: tip raised to 3.0 mm, in the bore", z_tip=0.30)
    G3 = Geometry("AS568-008 well (ID 4.47 mm), tip 3.0 mm", a=0.2235, z_tip=0.30)
    G4 = Geometry("AS568-010 well (ID 6.07 mm), tip 3.0 mm", a=0.3035, z_tip=0.30)
    G0 = Geometry("open well, no capillary", z_tip=None, coil=False)
    geoms = {"A": G1, "B": G2, "008": G3, "010": G4, "open": G0}
    out["geometry"] = {k: {"name": g.name, "spot_area_cm2": round(math.pi * g.a ** 2, 4), "liquid_height_mm": round(g.h_liq * 10, 2),
                           "tip_mm": None if g.z_tip is None else g.z_tip * 10} for k, g in geoms.items()}

    # 0. Check the solver against Cottrell: a spot as wide as the bore, no throat, no cap
    Gv = Geometry("validation", a=0.40, z_step=0.0, z_tip=None, coil=False, v_ul=500.0)
    mv = Model(Gv)
    rv, _ = run(mv, None, [("ocp", 600, "ocp", 0)], limiting=True)
    out["validation_vs_cottrell"] = {f"{s}s": round(-at(rv, "ic", s) / float(cottrell(s)), 3) for s in (30, 120, 300, 600)}

    # 1. Oxygen-limited current density at the spot, one hour, each geometry
    lim = {}
    times = [60, 300, 600, 1800, 3600]
    for k, g in geoms.items():
        m = Model(g)
        rec, _ = run(m, None, [("ocp", 3600, "ocp", 0)], limiting=True)
        lim[k] = rec
        out.setdefault("O2_limited_uA_cm2", {})[k] = {f"{t // 60}min": round(-at(rec, "ic", t) * 1e6, 2) for t in times}
    out["O2_limited_uA_cm2"]["1D_cottrell"] = {f"{t // 60}min": round(float(cottrell(t)) * 1e6, 2) for t in times}
    out["O2_limited_uA_cm2"]["bulk_cell"] = {f"delta_{d * 10:.1f}mm": round(4 * F * C_O2_SAT * D_O2 / d * 1e6, 1) for d in DELTA_BULK}

    # 2. Mixed potential at open circuit: the same metal in the well and in the bulk cell
    icorrs = [1e-6, 2e-6, 5e-6, 10e-6, 20e-6]
    mix = {}
    for key in ("A", "B"):
        m = Model(geoms[key])
        for ic in icorrs:
            kin = Kinetics(ic)
            rec, _ = run(m, kin, [("ocp", 3600, "ocp", 0)])
            mix[(key, round(ic * 1e6))] = rec
            out.setdefault("ocp_in_well", {}).setdefault(key, {})[f"{ic * 1e6:g}uA_cm2"] = {
                "E_shift_mV": {f"{t // 60}min": round(at(rec, "E", t) * 1e3, 1) for t in times},
                "icorr_ratio_well_over_bulk": {f"{t // 60}min": round(at(rec, "ia", t) / ic, 3) for t in times},
                "bulk_kinetic_fraction_of_cathodic": round(kin.theta_kin, 3)}
    # the same comparison for the calibration well sizes, at one i_corr
    for key in ("008", "010"):
        m = Model(geoms[key])
        kin = Kinetics(5e-6)
        rec, _ = run(m, kin, [("ocp", 1800, "ocp", 0)])
        out.setdefault("ocp_in_well", {}).setdefault(key, {})["5uA_cm2"] = {
            "E_shift_mV": {f"{t // 60}min": round(at(rec, "E", t) * 1e3, 1) for t in times if t <= 1800},
            "icorr_ratio_well_over_bulk": {f"{t // 60}min": round(at(rec, "ia", t) / 5e-6, 3) for t in times if t <= 1800}}
    # bulk-cell sensitivity to its own boundary layer
    for ic in icorrs:
        kin = Kinetics(ic)
        rows = {}
        for d in DELTA_BULK:
            Ec = brentq(lambda E: kin.ia(E) - kin.bulk_ic(E, d), -0.3, 0.3)
            rows[f"delta_{d * 10:.1f}mm"] = {"E_shift_mV": round(Ec * 1e3, 1), "icorr_ratio": round(kin.ia(Ec) / ic, 3)}
        out.setdefault("bulk_cell_delta_sensitivity", {})[f"{ic * 1e6:g}uA_cm2"] = rows

    # 3. The protocol's main sequence in the well, i_corr,b = 5 uA/cm2, with an LPR fit
    seq_steps = [("OCP", 1800, "ocp", 0), ("LPR", 120, "lpr", 0.010), ("rest", 300, "ocp", 0),
                 ("anodic hold +50 mV", 600, "hold_rel", 0.050), ("OCP after", 300, "ocp", 0)]
    snap_t = [5, 60, 300, 900, 1800, 2100, 2820, 3120]
    seqs = {}
    for key in ("A", "B"):
        m = Model(geoms[key])
        kin = Kinetics(5e-6)
        rec, snaps = run(m, kin, seq_steps, snap_times=snap_t)
        seqs[key] = (m, kin, rec, snaps)
        ph = np.array(rec["phase"])
        lpr = ph == "LPR"
        Es, Is = rec["E"][lpr], rec["I"][lpr]
        slope = np.polyfit(Is, Es, 1)[0]  # V per A
        rp_well = slope * m.A
        hold = ph == "anodic hold +50 mV"
        q_hold = float(rec["I"][hold].sum() * DT)
        q_all = float(np.clip(rec["ia"], 0, None).sum() * DT * m.A)
        cu_mol = float(rec["cu_mol"][-1])
        out.setdefault("sequence", {})[key] = {
            "E_ocp_end_mV_vs_bulk": round(at(rec, "E", 1800) * 1e3, 1),
            "Rp_well_ohm_cm2": round(rp_well), "Rp_bulk_ohm_cm2": round(kin.bulk_rp()),
            "Rp_ratio_well_over_bulk": round(rp_well / kin.bulk_rp(), 3),
            "lpr_current_range_nA": [round(float(Is.min()) * 1e9, 1), round(float(Is.max()) * 1e9, 1)],
            "anodic_hold_current_uA": [round(float(rec["I"][hold].min()) * 1e6, 3), round(float(rec["I"][hold].max()) * 1e6, 3)],
            "anodic_hold_charge_mC": round(q_hold * 1e3, 3),
            # the bulk cell held at its own E_corr + 50 mV, for comparison
            "anodic_hold_bulk_uA_cm2": round((kin.ia(0.05) - kin.bulk_ic(0.05)) * 1e6, 2),
            "anodic_hold_well_over_bulk": round(float(rec["I"][hold].mean()) / m.A / (kin.ia(0.05) - kin.bulk_ic(0.05)), 3),
            "anodic_charge_total_mC": round(q_all * 1e3, 3),
            "cu_dissolved_ng": round(cu_mol * 63.546 * 1e9, 1),
            "cu_in_150uL_ug_L": round(cu_mol * 63.546 * 1e6 / 150e-6, 1),
            "cu_in_tube_after_rinse_acid_ug_L": round(cu_mol * 63.546 * 1e6 / 320e-6, 1),
            "cu_near_spot_max_uM": round(float(rec["cu_spot"].max()) * 1e9, 1),
            "counter_O2_used_nmol": round(rec["counter_o2_mol"] * 1e9, 3),
            "O2_at_spot_centre_end_of_OCP_pct_sat": round(at(rec, "o2_spot", 1800) / C_O2_SAT * 100, 1),
        }

    # Cu(I) at the metal in the bulk cell at the same i_corr: a steady Nernst layer for CuCl2-,
    # thinner than O2's by (D_Cu / D_O2)^(1/3)
    d_cu = 0.03 * (D_CU / D_O2) ** (1 / 3)
    out["cu_at_metal_bulk_cell_uM_at_5uA_cm2"] = round(5e-6 / F * d_cu / D_CU * 1e9, 1)
    # Cu2O + 2H+ + 4Cl- -> 2CuCl2- + H2O, standard free energies (kJ/mol, NBS tables): an
    # order-of-magnitude marker for when dissolved Cu(I) should start precipitating as oxide
    dG = 2 * (-240.1) + (-237.129) - (-146.0) - 4 * (-131.228)
    logK = -dG * 1e3 / (LN10 * 8.314462 * 298.15)
    out["cu2o_solubility_as_CuCl2_uM_pH8p2_Cl0p55M"] = round(10 ** (logK / 2) * 10 ** -8.2 * 0.55 ** 2 * 1e6, 1)

    # 4. A cathodic hold after the anodic hold replates the dissolved Cu(I) (cap B)
    m = seqs["B"][0]
    kin = Kinetics(5e-6)
    rec_c, _ = run(m, kin, seq_steps[:4] + [("cathodic hold -300 mV", 600, "cathodic_rel", -0.300)])
    before = float(rec_c["cu_mol"][np.array(rec_c["phase"]) == "anodic hold +50 mV"][-1])
    out["cathodic_hold_after_anodic"] = {
        "cu_in_liquid_before_ng": round(before * 63.546e9, 1),
        "cu_in_liquid_after_10min_ng": round(float(rec_c["cu_mol"][-1]) * 63.546e9, 1),
        "replated_pct": round((1 - float(rec_c["cu_mol"][-1]) / before) * 100, 1),
        "cathodic_current_density_end_uA_cm2": round(float(rec_c["ic"][-1]) * 1e6, 2)}

    # 5. Ohmic drop between the spot and the reference tip
    for key in ("A", "B", "008", "010"):
        res = laplace(geoms[key])
        A = math.pi * geoms[key].a ** 2
        res["iR_mV"] = {lab: round(res["R_u_ohm"] * j * A * 1e3, 3) for lab, j in
                        (("LPR_100nA_cm2", 1e-7), ("hold_50uA_cm2", 5e-5), ("reversal_1mA_cm2", 1e-3), ("reversal_10mA_cm2", 1e-2))}
        out.setdefault("ohmic", {})[key] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}
    # a disc in an infinite electrolyte, for scale: R = 1/(4 kappa a)
    out["ohmic"]["disc_in_infinite_liquid_ohm"] = round(1 / (4 * KAPPA * 0.145), 1)

    (HERE / "sim_well.json").write_text(json.dumps(out, indent=1) + "\n")

    # fields for the animation: cap B (the copper cap), the main sequence
    m, kin, rec, snaps = seqs["B"]
    np.savez_compressed(HERE / "sim_well_fields.npz",
                        r=m.r, z=m.z, liquid=m.liq, coil=m.coil,
                        times=np.array(sorted(snaps)),
                        o2=np.array([snaps[t][0] for t in sorted(snaps)]) / C_O2_SAT,
                        cu=np.array([snaps[t][1] for t in sorted(snaps)]) * 1e9,
                        trace_t=rec["t"], trace_E=rec["E"], trace_I=rec["I"],
                        a=m.g.a, z_step=m.g.z_step, r_bore=m.g.r_bore, h_liq=m.g.h_liq, z_tip=m.g.z_tip, r_cap=m.g.r_cap)

    plot(out, lim, mix, seqs, geoms)
    print(json.dumps({k: out[k] for k in ("validation_vs_cottrell", "O2_limited_uA_cm2", "sequence", "cathodic_hold_after_anodic", "ohmic")}, indent=1))


# ---------------------------------------------------------------------------
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.6)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    for s in ax.spines.values():
        s.set_color(GRID)


def plot(out, lim, mix, seqs, geoms):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    blues = LinearSegmentedColormap.from_list("blues", ["#0d366b", "#256abf", "#6da7ec", "#cde2fb"])
    fig = plt.figure(figsize=(15, 9.2), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.05, 1, 1], wspace=0.28, hspace=0.38)

    # A: O2 field at the end of the 30 min OCP, cap B, mirrored about the axis
    ax = fig.add_subplot(gs[0, 0])
    m, kin, rec, snaps = seqs["B"]
    o2 = snaps[1800][0] / C_O2_SAT
    full = np.concatenate([o2[::-1, :], o2], axis=0).T
    rr = np.concatenate([-m.r[::-1], m.r]) * 10
    zz = m.z * 10
    im = ax.pcolormesh(rr, zz, full, cmap=blues, vmin=0, vmax=1, shading="nearest")
    ax.set_aspect("equal")
    ax.set_facecolor("#f3e3d6")
    ax.set_xlim(-4.3, 4.3); ax.set_ylim(-0.7, 5.3)
    ax.axhline(0, color="#b87333", lw=3)
    ax.text(0, -0.12, "metal: 2.90 mm spot", ha="center", va="top", fontsize=7.5, color=INK2)
    ax.add_patch(plt.Rectangle((-1.0, m.g.z_tip * 10), 2.0, 5, fc="#eeeeea", ec=INK2, lw=0.8))
    ax.text(0, 3.9, "Ag/AgCl\ncapillary", ha="center", fontsize=7, color=INK2)
    ax.text(3.0, 3.25, "Pt\ncoil", ha="left", va="center", fontsize=7, color=INK2)
    ax.text(2.5, 4.62, "air-saturated surface", ha="center", va="bottom", fontsize=7, color=INK2)
    ax.text(2.6, 1.0, "lid", ha="center", fontsize=7, color=INK2)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("O2, fraction of saturation", fontsize=7.5, color=INK2)
    cb.ax.tick_params(labelsize=7, colors=MUTED)
    ax.set_xlabel("r, mm", fontsize=8, color=INK2); ax.set_ylabel("z, mm", fontsize=8, color=INK2)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    ax.set_title("A  O2 in the well after 30 min at open circuit\n(i_corr,b = 5 µA/cm², cap B: the copper cap)", fontsize=9, color=INK, loc="left")

    # B: O2-limited current density
    ax = fig.add_subplot(gs[0, 1]); style(ax)
    tmin = lim["A"]["t"] / 60
    for key, col, lab in (("A", ORANGE, "well, cap A (tip 1.5 mm)"), ("B", BLUE, "well, cap B (tip 3.0 mm)"), ("open", AQUA, "well, no cap in the liquid")):
        ax.plot(lim[key]["t"] / 60, -lim[key]["ic"] * 1e6, color=col, lw=2, label=lab)
    t = np.linspace(0.5, 60, 300)
    ax.plot(t, cottrell(t * 60) * 1e6, color=MUTED, lw=1.2, ls="--", label="1D estimate (Cottrell)")
    lo, hi = (4 * F * C_O2_SAT * D_O2 / d * 1e6 for d in (DELTA_BULK[2], DELTA_BULK[0]))
    ax.axhspan(lo, hi, color="#e6e5df", lw=0)
    ax.text(31, (lo * hi) ** 0.5, f"bulk cell, δ 0.2–0.5 mm: {lo:.0f}–{hi:.0f}", fontsize=7, color=INK2, va="center")
    ax.set_yscale("log"); ax.set_ylim(0.8, 200); ax.set_xlim(0, 60)
    ax.set_xlabel("minutes after the cap goes on", fontsize=8, color=INK2)
    ax.set_ylabel("O2-limited current density, µA/cm²", fontsize=8, color=INK2)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    ax.set_title("B  The most O2 the spot can get", fontsize=9, color=INK, loc="left")

    # C: icorr ratio at 30 min vs bulk icorr
    ax = fig.add_subplot(gs[0, 2]); style(ax)
    xs = np.array([1, 2, 5, 10, 20])
    for key, col, lab in (("A", ORANGE, "cap A"), ("B", BLUE, "cap B")):
        for tt, mk, ls in ((300, "o", ":"), (1800, "o", "-")):
            ys = [at(mix[(key, int(ic))], "ia", tt) / (ic * 1e-6) for ic in xs]
            ax.plot(xs, ys, color=col, lw=2 if tt == 1800 else 1.2, ls=ls, marker=mk, ms=4 if tt == 300 else 6,
                    label=f"{lab}, {tt // 60} min")
    ax.axhline(1, color=MUTED, lw=1)
    ax.set_xscale("log"); ax.set_ylim(0, 1.05)
    ax.set_xticks(xs); ax.set_xticklabels([str(x) for x in xs])
    ax.set_xlabel("i_corr of the same metal in a bulk cell, µA/cm²", fontsize=8, color=INK2)
    ax.set_ylabel("i_corr in the well ÷ i_corr in the bulk cell", fontsize=8, color=INK2)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    ax.set_title("C  What the well alone does to i_corr", fontsize=9, color=INK, loc="left")

    # D: E_corr shift vs time
    ax = fig.add_subplot(gs[1, 0]); style(ax)
    for ic, col in ((1e-6, AQUA), (5e-6, BLUE), (20e-6, ORANGE)):
        rec = mix[("A", round(ic * 1e6))]
        ax.plot(rec["t"] / 60, rec["E"] * 1e3, color=col, lw=2, label=f"i_corr,b {ic * 1e6:g} µA/cm²")
    ax.axhline(0, color=MUTED, lw=1)
    ax.text(59, 1.5, "bulk-cell E_corr", ha="right", fontsize=7, color=INK2)
    ax.set_xlim(0, 60)
    ax.set_xlabel("minutes at open circuit", fontsize=8, color=INK2)
    ax.set_ylabel("E_corr in the well − bulk E_corr, mV", fontsize=8, color=INK2)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    ax.set_title("D  E_corr drifts as the well's O2 runs down (cap A)", fontsize=9, color=INK, loc="left")

    # E: the protocol's sequence
    ax = fig.add_subplot(gs[1, 1]); style(ax)
    for key, col, lab in (("A", ORANGE, "cap A"), ("B", BLUE, "cap B")):
        rec = seqs[key][2]
        ax.plot(rec["t"] / 60, rec["I"] * 1e9, color=col, lw=1.6, label=lab)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xlabel("minutes", fontsize=8, color=INK2)
    ax.set_ylabel("current through the spot, nA (symlog)", fontsize=8, color=INK2)
    for x0, x1, lab in ((0, 30, "OCP"), (30, 32, "LPR"), (32, 37, "rest"), (37, 47, "+50 mV hold"), (47, 52, "OCP")):
        ax.text((x0 + x1) / 2, 4000, lab, ha="center", fontsize=6.5, color=INK2, rotation=90 if x1 - x0 < 6 else 0)
        ax.axvline(x1, color=GRID, lw=0.8)
    ax.set_xlim(0, 52); ax.set_ylim(-2e3, 1e4)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    ax.set_title("E  One spot of the copper protocol (i_corr,b 5 µA/cm²)", fontsize=9, color=INK, loc="left")

    # F: dissolved Cu in the well
    ax = fig.add_subplot(gs[1, 2]); style(ax)
    for key, col, lab in (("A", ORANGE, "cap A"), ("B", BLUE, "cap B")):
        rec = seqs[key][2]
        ax.plot(rec["t"] / 60, rec["cu_mol"] * 63.546e9, color=col, lw=2, label=lab)
    ax.set_xlabel("minutes", fontsize=8, color=INK2)
    ax.set_ylabel("Cu dissolved into the well, ng", fontsize=8, color=INK2)
    ax.set_xlim(0, 52)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    s = out["sequence"]["A"]
    ax.text(2, s["cu_dissolved_ng"] * 0.8, f"cap A: {s['cu_dissolved_ng']:.0f} ng in 52 min,\n{s['cu_in_tube_after_rinse_acid_ug_L']:.0f} µg/L in the 320 µL tube",
            ha="left", va="top", fontsize=7, color=INK2)
    ax.set_title("F  The ICP-MS signal: Cu leaving the spot", fontsize=9, color=INK, loc="left")

    fig.text(0.5, 0.012, "Model, not measurement: 2D axisymmetric diffusion in a sealed 150 µL well (AS568-006 spot, 8 mm bore), Tafel kinetics set so the bulk cell "
             "(δ 0.3 mm) has E_corr 0 and the stated i_corr; b_a 60, b_c 120 mV/dec. No film growth, no Cu(I) oxidation, no convection in the well.",
             ha="center", fontsize=7.5, color=INK2)
    fig.savefig(HERE / "sim_well.png", dpi=150, facecolor=SURFACE, bbox_inches="tight")


if __name__ == "__main__":
    main()

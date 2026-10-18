"""Higher-fidelity model of one CubXL copper corrosion well, against a bulk cell.

Writes sim_well_hf.json (every number sim_well_hf.md quotes), sim_well_hf.png (the figure)
and sim_well_hf_fields.npz (fields for render_cubxl_cu.py, same keys as sim_well_fields.npz,
plus pH and film).

What it adds to sim_well.py, which carried dissolved copper as a passive tracer under Tafel
kinetics set relative to the bulk cell:

- Copper dissolves by the accepted chloride mechanism, Cu + 2Cl- = CuCl2- + e-, nearly
  reversible and largely limited by transport of CuCl2- away from the metal (Hauser and
  Newman 1988; Deslouis et al. 1988). The CuCl2- at the metal is held near its Nernst value,
  so copper that piles up in the still well throttles further dissolution.
- A Cu2O film forms where the liquid at the metal is supersaturated in Cu2O at the local pH,
  and its thickness throttles dissolution. Its one free constant is calibrated, per alloy, to
  the published decay of i_corr with immersion time.
- Cu(I) is oxidised by dissolved O2 in the liquid (Sharma and Millero 1988 rate constants for
  Cu+ and CuCl0, with Cu(I) chloride speciation). Cu(II) is its own species, and is reduced
  back to Cu(I) at the metal (comproportionation with the metal).
- Cu2O also precipitates in the liquid and redissolves when undersaturated.
- Alkalinity is a transported species: OH- from O2 reduction, from Cu(I) oxidation and from
  the counter; consumed by Cu2O precipitation and Al hydrolysis. pH comes from the seawater
  carbonate and borate system (closed: the cap seals the headspace).
- Double-layer charging, and the electrolyte potential (secondary current distribution with
  seawater's conductivity), lagged one 1 s step, so the reference-tip iR and any ohmic
  shielding of the crevice come out of the model.
- The O-ring's compressed cross-section: an AS568-006 ring squeezed 21 % to 1.40 mm is
  modelled as a stadium of conserved area, so the metal is wetted out to where the flat contact
  begins (r = 2.00 mm, not the nominal 1.45 mm), with a narrowing crevice between the ring's
  lower inner curve and the metal. A non-uniform grid (4 um at the metal, 10 um across the
  crevice) resolves it.
- NAB gets a second anodic path for its Al- and Fe-rich phases (Tafel, b_a 60 mV/dec), which
  its published E_corr and R_p require: at -0.26 V SCE the CuCl2- path alone carries only
  a few per cent of NAB's measured current.
- Kinetics per alloy, calibrated so the bulk cell (1 cm2, 0.3 mm Nernst layer for O2) gives the
  published R_p (C70600, C71500: Metikos-Hukovic 2011; C95800: Ding 2019 with its E_corr).
  E_corr for the two Cu-Ni alloys is then a prediction, checked against the published range.

Not modelled: natural convection (subcritical, estimated below), migration (0.7 M supporting
electrolyte), CuCl salt films, Cu2(OH)3Cl, film reduction at cathodic potentials, the
counter's chlorine, Ni and Fe dissolution, and roughness at the O-ring's contact line.

    python sim_well_hf.py            # about 10 min on 4 cores
    python sim_well_hf.py --quick    # skip the grid-convergence run
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.linalg import lu_factor, lu_solve, solve_banded
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
F = 96485.332
RG = 8.314462
TK = 298.15
FRT = F / (RG * TK)
LN10 = math.log(10.0)

# ------------------------------------------------------------------ electrolyte: ASTM D1141, 25 C
C_O2_SAT = 0.21e-6  # mol/cm3, air-saturated seawater S 35, 25 C (as sim_well.py)
D = {"O2": 1.9e-5, "Cu1": 8.0e-6, "Cu2": 7.0e-6, "TA": 1.1e-5, "Al": 5.0e-6}  # cm2/s
KAPPA = 0.053  # S/cm
CL_M = 0.546  # mol/L chloride, D1141 (19.4 g/kg)
I_STR = 0.70


def davies(z, I=I_STR):
    return 10 ** (-0.51 * z * z * (math.sqrt(I) / (1 + math.sqrt(I)) - 0.3 * I))


G1, G2 = davies(1), davies(2)
A_CL = G1 * CL_M
E_SCE = 0.2412  # V vs SHE
# NBS standard free energies of formation, kJ/mol
DG = {"CuCl2-": -240.1, "Cl-": -131.228, "H2O": -237.129, "Cu2O": -146.0}
E0_CUCL2 = -(2 * DG["Cl-"] - DG["CuCl2-"]) * 1e3 / F  # CuCl2- + e- = Cu + 2Cl-, V vs SHE
LOGK_CU2O = -(2 * DG["CuCl2-"] + DG["H2O"] - DG["Cu2O"] - 4 * DG["Cl-"]) * 1e3 / (LN10 * RG * TK)
E_CU2O_PH0 = -(DG["H2O"] - DG["Cu2O"]) * 1e3 / (2 * F)  # Cu2O + 2H+ + 2e- = 2Cu + H2O, V vs SHE


def csat_cu2o(ph):
    """CuCl2- in equilibrium with Cu2O, mol/cm3: Cu2O + 2H+ + 4Cl- = 2CuCl2- + H2O."""
    return 10 ** (LOGK_CU2O / 2) * 10.0 ** (-ph) * A_CL ** 2 / G1 * 1e-3 * CU1_TOTAL_PER_CUCL2


# carbonate and borate, seawater S 35, 25 C, total scale (Lueker 2000 K1 K2; Dickson 1990 KB; Millero 1995 KW)
DIC, BT = 2.39e-3, 0.437e-3  # mol/L, from D1141's NaHCO3 0.201 g/L and H3BO3 0.027 g/L
K1, K2, KB, KW = 10 ** -5.847, 10 ** -8.966, 10 ** -8.597, 10 ** -13.217
PH0 = 8.2


def ta_of_ph(ph):
    h = 10.0 ** (-np.asarray(ph, float))
    return DIC * (K1 * h + 2 * K1 * K2) / (h * h + K1 * h + K1 * K2) + BT * KB / (KB + h) + KW / h - h


PH_GRID = np.linspace(1.0, 12.5, 5751)
TA_GRID = ta_of_ph(PH_GRID)
TA0 = float(ta_of_ph(PH0))


def ph_of(dta):
    """Excess alkalinity (mol/cm3 of OH- added) -> pH, closed system."""
    return np.interp(TA0 + np.asarray(dta) * 1e3, TA_GRID, PH_GRID)


# ------------------------------------------------------------------ kinetics shared by the alloys
K0 = 1.0e-2        # cm/s, film-free Cu/CuCl2- exchange conductance: 'nearly reversible' (ASSUMED value)
ALPHA_C = 0.5      # O2 reduction transfer coefficient: b_c = 118 mV/dec (ASSUMED, typical)
E_REF = -0.25      # V vs SCE, where k_O2 is quoted
B_AL = 0.060       # V/dec, NAB's Al/Fe-phase path (ASSUMED)
C_DL = 30e-6       # F/cm2 (ASSUMED; Hauser and Newman 1988 used 10 uF/cm2)
K_P_HOM = 0.01     # 1/s, Cu2O precipitation in the liquid when supersaturated (ASSUMED)
K_P_SURF = 1.0e-4  # cm/s, Cu2O growth onto the film when the liquid at the metal is supersaturated (ASSUMED)
K_CU2_RED = 1.0e-3  # cm/s, Cu(II) + Cu -> 2 Cu(I) at the metal (ASSUMED fast)
BETA_FILM = 0.3    # fraction of the Cu oxidised that stays as Cu2O on the metal (solid-state growth, ASSUMED)
V_FILM = 143.09 / 6.0 / 2  # cm3 of Cu2O per mol of Cu


def k_ox_air():
    """Pseudo-first-order oxidation of total Cu(I) in air-saturated seawater, 1/s.
    Sharma and Millero 1988: Cu+ 14.1 /s, CuCl0 3.9 /s; CuCl2- and CuCl3 2- taken as unreactive.
    Speciation: log beta 2.7, 5.5, 5.7 at I = 0 (ASSUMED), Davies-corrected to I = 0.7."""
    b1 = 10 ** 2.7 * G1 * G1
    b2 = 10 ** 5.5 * G1 * G1 ** 2 / G1
    b3 = 10 ** 5.7 * G1 * G1 ** 3 / G2
    cl = CL_M
    den = 1 + b1 * cl + b2 * cl ** 2 + b3 * cl ** 3
    a0, a1 = 1 / den, b1 * cl / den
    return 14.1 * a0 + 3.9 * a1, {"frac_Cu+": a0, "frac_CuCl0": a1, "frac_CuCl2-": b2 * cl ** 2 / den, "frac_CuCl3_2-": b3 * cl ** 3 / den}


K_OX, CU1_SPECIATION = k_ox_air()
# The Nernst and Cu2O-solubility relations fix CuCl2- itself; transport carries all the Cu(I) chloro complexes.
CU1_TOTAL_PER_CUCL2 = 1.0 / CU1_SPECIATION["frac_CuCl2-"]


@dataclass
class Alloy:
    key: str
    name: str
    x_cu: float           # Cu mole fraction, taken as its activity (ideal solution, ASSUMED)
    rp_target: float      # ohm cm2, bulk cell
    t_cal_s: float        # when the cited R_p was measured
    tau_h: float          # parabolic decay time of i_corr, i0 / sqrt(1 + t / tau)
    ec_target: float | None = None  # V vs SCE, fitted only for NAB
    al_path: bool = False
    k_o2: float = 1e-3    # cm/s at E_REF, fitted
    i_al0: float = 0.0    # A/cm2 at ec_target, fitted
    gamma_star: float = 1e-8  # mol/cm2 of Cu in the film that halves K, fitted
    q_star: float = 1.0       # C/cm2 of Al-path charge that halves the Al path (its oxide film), fitted

    def c_eq(self, E):
        """CuCl2- at the metal in equilibrium with the alloy, mol/cm3. E in V vs SCE."""
        return self.x_cu * A_CL ** 2 / G1 * np.exp(FRT * (np.asarray(E) + E_SCE - E0_CUCL2)) * 1e-3 * CU1_TOTAL_PER_CUCL2

    def k_c(self, E):
        return self.k_o2 * np.exp(-ALPHA_C * FRT * (np.asarray(E) - E_REF))

    def i_al(self, E, q=0.0):
        """NAB's Al/Fe-phase path, A/cm2, throttled by its own oxide: q is the Al-path charge passed, C/cm2.
        At a fixed potential this gives i0 / sqrt(1 + t / tau) with tau = q_star / (2 i0)."""
        if not self.al_path:
            return 0.0 * np.asarray(E)
        return self.i_al0 * 10 ** ((np.asarray(E) - self.ec_target) / B_AL) / (1.0 + np.asarray(q) / self.q_star)

    def K(self, gamma):
        return K0 / (1.0 + np.asarray(gamma) / self.gamma_star)


def ALLOYS():
    return {
        # Metikos-Hukovic 2011 (Desalination 276:228), via Edison c1-05: Cu-10Ni / Cu-30Ni, 3.5 % NaCl pH 7.9,
        # stagnant, 3 h, EIS-derived R_p 6.0 / 8.3 kohm cm2. tau: Kear 2004 review 12 -> 5 uA/cm2 in 20-22 h (c1-02),
        # Yuan 2007 70/30: 8.44 -> 1.01 uA/cm2 in 10 days (c1-02).
        "C70600": Alloy("C70600", "90/10 Cu-Ni", 0.877, 6000.0, 3 * 3600.0, 4.4),
        "C71500": Alloy("C71500", "70/30 Cu-Ni", 0.666, 8300.0, 3 * 3600.0, 3.5),
        # Ding 2019 (Materials 12:209), via Edison c1-02: cast C95800, 3.5 % NaCl, fresh: E_corr -0.260 V SCE
        # (OCP -0.264), R_f + R_ct 1761 + 318 ohm cm2, i_corr 11.35 -> 3.78 uA/cm2 in 240 h.
        "C95800": Alloy("C95800", "NAB", 0.713, 2079.0, 3600.0, 30.0, ec_target=-0.262, al_path=True),
    }


def keff(k, Dc, hz):
    """Surface rate constant in series with the half-cell diffusion distance."""
    g = Dc / hz
    return k * g / (k + g)


# ------------------------------------------------------------------ the protocol sequence
SEQ = [("OCP", 1800, "ocp", 0.0), ("LPR", 120, "lpr", 0.010), ("rest", 300, "ocp", 0.0),
       ("anodic hold +50 mV", 600, "hold_rel", 0.050), ("OCP after", 300, "ocp", 0.0)]
SEQ_CATH = SEQ[:4] + [("cathodic hold -300 mV", 600, "hold_rel", -0.300)]
LPR_RATE = 1.667e-4  # V/s


def potential_for(mode, val, E_start, s, dt):
    if mode == "hold_rel":
        return E_start + val
    if mode == "lpr":
        return E_start - val + LPR_RATE * (s + 1) * dt
    raise ValueError(mode)


# ------------------------------------------------------------------ the bulk cell: 1D Nernst layers
class Bulk1D:
    """1 cm2 of metal under stagnant Nernst layers, delta_i = delta_O2 (D_i / D_O2)^(1/3), bulk values beyond.
    Same surface and liquid chemistry as the well."""

    def __init__(self, alloy: Alloy, delta=0.03, dx=5e-4):
        self.al, self.dx = alloy, dx
        self.n = {k: max(4, int(round(delta * (D[k] / D["O2"]) ** (1 / 3) / dx))) for k in D}
        self.N = max(self.n.values())
        self.reset()

    def reset(self):
        N = self.N
        self.c = {"O2": np.full(N, C_O2_SAT), "Cu1": np.zeros(N), "Cu2": np.zeros(N), "TA": np.zeros(N), "Al": np.zeros(N)}
        self.susp = np.zeros(N)
        self.gamma = 0.0
        self.q_al = 0.0
        self.E = 0.0
        self.fresh = True
        self.out = {"Cu": 0.0}  # Cu that left through the outer edge, mol/cm2
        self.q_cu = 0.0  # net Cu dissolved, mol/cm2

    def _mat(self, k, dt):
        n, dx, Dk = self.n[k], self.dx, D[k]
        g = Dk / dx
        main = np.full(n, dx / dt + 2 * g)
        main[0] = dx / dt + g
        main[-1] = dx / dt + g + Dk / (dx / 2)  # Dirichlet to the bulk value beyond
        if k == "Cu2":
            main[0] += keff(K_CU2_RED, Dk, dx / 2)
        ab = np.zeros((3, n))
        ab[0, 1:] = -g
        ab[1] = main
        ab[2, :-1] = -g
        e0 = np.zeros(n)
        e0[0] = 1.0
        z = solve_banded((1, 1), ab, e0)
        return ab, z

    def step_setup(self, dt):
        if getattr(self, "_dt", None) != dt:
            self._m = {k: self._mat(k, dt) for k in D}
            self._dt = dt

    def step(self, dt, mode, Eset=None, grow=True):
        """Advance dt. mode 'ocp' solves the mixed potential; 'pot' holds Eset. grow=False freezes the films."""
        al, dx = self.al, self.dx
        self.step_setup(dt)
        bulk = {"O2": C_O2_SAT, "Cu1": 0.0, "Cu2": 0.0, "TA": 0.0, "Al": 0.0}
        y = {}
        for k in ("Cu2", "O2", "Cu1"):
            n = self.n[k]
            b = self.c[k][:n] * dx / dt
            b[-1] += D[k] / (dx / 2) * bulk[k]
            if k == "Cu1":
                b[0] += J2
            y[k] = solve_banded((1, 1), self._m[k][0], b)
            if k == "Cu2":
                J2 = keff(K_CU2_RED, D["Cu2"], dx / 2) * y[k][0]  # mol/cm2/s reduced to Cu(I)
        zO, zC = self._m["O2"][1], self._m["Cu1"][1]
        wO, wC = zO[0], zC[0]
        dC = keff(al.K(self.gamma), D["Cu1"], dx / 2)
        E_prev = self.E
        cdl = 0.0 if self.fresh else C_DL

        dL = (1 - BETA_FILM) * dC  # the liquid gets (1 - beta) of the Cu oxidised

        def parts(E):
            dO = keff(al.k_c(E), D["O2"], dx / 2)
            sO = y["O2"][0] / (1 + wO * dO)
            ceq = float(al.c_eq(E))
            sC = (y["Cu1"][0] + wC * dL * ceq) / (1 + wC * dL)
            JL = dL * (ceq - sC)  # Cu(I) into the liquid; negative = replating from it
            JO, JC = dO * sO, (JL / (1 - BETA_FILM) if JL > 0 else JL)
            ia = float(al.i_al(E, self.q_al))
            return JO, JC, ia, F * JC + ia - 4 * F * JO - F * J2

        if mode == "ocp":
            lo, hi = (-0.9, 0.5) if self.fresh else (E_prev - 0.4, E_prev + 0.4)
            Ev = brentq(lambda E: parts(E)[3] + cdl * (E - E_prev) / dt, lo, hi, xtol=1e-8)
        else:
            Ev = Eset
        JO, JC, ia, inet = parts(Ev)
        idl = cdl * (Ev - E_prev) / dt
        self.fresh = False
        if grow:
            self.q_al += ia * dt
        self.c["O2"][:self.n["O2"]] = y["O2"] - zO * JO
        JL = JC * (1 - BETA_FILM) if JC > 0 else JC
        self.c["Cu1"][:self.n["Cu1"]] = y["Cu1"] + zC * JL
        self.c["Cu2"][:self.n["Cu2"]] = y["Cu2"]
        self.q_cu += JC * dt
        jf = JC - JL  # solid-state film growth; replating takes Cu(I) from the liquid only
        if grow:
            self.gamma += jf * dt
        film_oh = -jf
        # outer-edge losses of copper
        for k in ("Cu1", "Cu2"):
            self.out["Cu"] += D[k] / (dx / 2) * self.c[k][self.n[k] - 1] * dt
        # alkalinity and Al: sources at the metal
        for k, src in (("TA", 4 * JO - ia / F + film_oh), ("Al", ia / (3 * F))):
            n = self.n[k]
            b = self.c[k][:n] * dx / dt
            b[0] += src
            self.c[k][:n] = solve_banded((1, 1), self._m[k][0], b)
        self._react(dt, grow)
        self.E = Ev
        return {"E": Ev, "I": inet + idl, "JO": JO, "JC": JC, "ia": ia, "J2": J2, "idl": idl}

    def _react(self, dt, film):
        c, dx = self.c, self.dx
        x = c["Cu1"] * (1 - np.exp(-K_OX * c["O2"] / C_O2_SAT * dt))
        x = np.minimum(x, 4 * c["O2"])
        c["Cu1"] -= x; c["Cu2"] += x; c["O2"] -= x / 4; c["TA"] += x
        cs = csat_cu2o(ph_of(c["TA"]))
        ex = c["Cu1"] - cs
        p = np.where(ex > 0, ex * (1 - math.exp(-K_P_HOM * dt)), 0.0)
        dis = np.where(ex < 0, np.minimum(self.susp / dx, -ex * (1 - math.exp(-K_P_HOM * dt))), 0.0)
        c["Cu1"] += dis - p; c["TA"] += dis - p; self.susp += (p - dis) * dx
        if film:
            ex0 = c["Cu1"][0] - cs[0]
            if ex0 > 0:
                ps = min(K_P_SURF * ex0 * dt, ex0 * dx)
                c["Cu1"][0] -= ps / dx; c["TA"][0] -= ps / dx; self.gamma += ps
        for k in ("Cu1", "Cu2", "TA", "Al"):  # beyond each species' own layer: bulk
            c[k][self.n[k]:] = 0.0
        c["O2"][self.n["O2"]:] = C_O2_SAT

    def inventory(self):
        dx = self.dx
        return {"liquid": float((self.c["Cu1"] + self.c["Cu2"]).sum() * dx), "susp": float(self.susp.sum()),
                "film": self.gamma, "out": self.out["Cu"], "dissolved": self.q_cu}

    # -- calibration helpers
    def ocp_run(self, t_end, dt=10.0, t_fine=600.0):
        """Open circuit from a fresh surface. Returns (t, E, i_anodic) arrays."""
        self.reset()
        ts, Es, ias = [], [], []
        t = 0.0
        while t < t_end - 1e-9:
            h = 1.0 if t < 60 else (5.0 if t < t_fine else dt)
            r = self.step(h, "ocp")
            t += h
            ts.append(t); Es.append(r["E"]); ias.append(F * r["JC"] + r["ia"])
        return np.array(ts), np.array(Es), np.array(ias)

    def rp_now(self, dE=0.001, t_hold=120.0, dt=2.0):
        """R_p from the current state: potentiostatic holds at E_corr +/- dE with the film frozen."""
        state = self._save()
        Ec = self.E
        I = []
        for s in (+1, -1):
            self._load(state)
            for _ in range(int(t_hold / dt)):
                r = self.step(dt, "pot", Ec + s * dE, grow=False)
            I.append(r["I"] - r["idl"])
        self._load(state)
        return 2 * dE / (I[0] - I[1])

    def _save(self):
        return ({k: v.copy() for k, v in self.c.items()}, self.susp.copy(), self.gamma, self.E, dict(self.out), self.q_cu, self.q_al, self.fresh)

    def _load(self, s):
        self.c = {k: v.copy() for k, v in s[0].items()}
        self.susp, self.gamma, self.E, self.out, self.q_cu, self.q_al, self.fresh = s[1].copy(), s[2], s[3], dict(s[4]), s[5], s[6], s[7]


def calibrate(al: Alloy, log=print):
    """Fit k_O2 (and i_Al0 for NAB) to the cited bulk R_p at t_cal (and E_corr for NAB), and gamma_star
    to the cited parabolic decay time tau. Alternates three times."""
    b = Bulk1D(al)
    t_cal = al.t_cal_s

    def rp_at_tcal():
        b.ocp_run(t_cal, dt=30.0)
        return b.rp_now(), b.E

    for it in range(3 if al.al_path else 4):
        if al.al_path:
            def resid_ial(log_ial):
                al.i_al0 = 10 ** log_ial

                def resid_k(log_k):
                    al.k_o2 = 10 ** log_k
                    b.ocp_run(t_cal, dt=30.0)
                    return b.E - al.ec_target
                try:
                    al.k_o2 = 10 ** brentq(resid_k, -8, -1, xtol=2e-4)
                except ValueError:  # the cathode cannot carry this Al path at the target E_corr
                    return -5.0
                rp, _ = rp_at_tcal()
                return math.log(rp / al.rp_target)
            al.i_al0 = 10 ** brentq(resid_ial, -6.5, -4.6, xtol=2e-4)
        else:
            def resid(log_k):
                al.k_o2 = 10 ** log_k
                rp, _ = rp_at_tcal()
                return math.log(rp / al.rp_target)
            al.k_o2 = 10 ** brentq(resid, -9, 0, xtol=1e-4)
        tau = al.tau_h * 3600.0
        target = math.sqrt((1 + 300.0 / tau) / 2.0)
        if al.al_path:
            # NAB's decay is its Al path's oxide (the Cu path is below Cu2O saturation at -0.26 V). Start from the
            # fixed-potential result q* = 2 i0 tau, then fit it at open circuit, where E_corr drifts up as the path passivates.
            def resid_q(log_q):
                al.q_star = 10 ** log_q
                t, E, ia = b.ocp_run(tau, dt=120.0)
                return math.log(ia[-1] / np.interp(300.0, t, ia)) - math.log(target)
            q0 = math.log10(2 * al.i_al0 * tau)
            try:
                al.q_star = 10 ** brentq(resid_q, q0 - 3, q0 + 1, xtol=1e-3)
            except ValueError:
                al.q_star = 10 ** q0
                log(f"  {al.key}: q_star bracket failed, using 2 i0 tau")
            rp, Ec = rp_at_tcal()
            log(f"  {al.key} pass {it + 1}: k_O2 {al.k_o2:.3e} cm/s, i_Al0 {al.i_al0:.3e} A/cm2, q* {al.q_star:.3e} C/cm2, "
                f"R_p(t_cal) {rp:.0f}, E_corr(t_cal) {Ec * 1e3:.1f} mV SCE")
            continue

        def resid_g(log_g):
            al.gamma_star = 10 ** log_g
            t, E, ia = b.ocp_run(tau, dt=60.0)
            i300 = np.interp(300.0, t, ia)
            return math.log(ia[-1] / i300) - math.log(target)
        try:
            al.gamma_star = 10 ** brentq(resid_g, -14, -4, xtol=1e-3)
        except ValueError:
            log(f"  {al.key}: gamma_star bracket failed")
        rp, Ec = rp_at_tcal()
        log(f"  {al.key} pass {it + 1}: k_O2 {al.k_o2:.3e} cm/s, i_Al0 {al.i_al0:.3e}, gamma* {al.gamma_star:.3e} mol/cm2, "
            f"R_p(t_cal) {rp:.0f}, E_corr(t_cal) {Ec * 1e3:.1f} mV SCE")
    return b


def run_bulk(al: Alloy, steps, dt=1.0):
    b = Bulk1D(al)
    rec = {k: [] for k in ("t", "E", "I", "ia", "ic", "phase")}
    t, E_ocp = 0.0, None
    for name, dur, mode, val in steps:
        E_start = b.E
        for s in range(int(round(dur / dt))):
            if mode == "ocp":
                r = b.step(dt, "ocp")
            else:
                r = b.step(dt, "pot", potential_for(mode, val, E_start, s, dt))
            t += dt
            rec["t"].append(t); rec["E"].append(r["E"]); rec["I"].append(r["I"])
            rec["ia"].append(F * r["JC"] + r["ia"]); rec["ic"].append(-4 * F * r["JO"] - F * r["J2"]); rec["phase"].append(name)
    for k in ("t", "E", "I", "ia", "ic"):
        rec[k] = np.array(rec[k])
    rec["inv"] = b.inventory()
    return rec


# ------------------------------------------------------------------ the well: 2D axisymmetric, non-uniform grid
CS, SQUEEZED = 0.178, 0.140       # O-ring cross-section and squeezed height, cm
R_RING = 0.145 + CS / 2           # 0.234: centre of the section
RHO = SQUEEZED / 2
W_FLAT = (math.pi / 4 * CS ** 2 - math.pi * RHO ** 2) / SQUEEZED
R_CONTACT = R_RING - W_FLAT / 2   # inner edge of the flat contact with the metal
A_NOM = 0.145
Z_THROAT, R_THROAT, R_BORE, R_CAP, Z_TIP = 0.160, 0.145, 0.40, 0.10, 0.30
COIL_Z = (0.24, 0.28, 0.32, 0.36, 0.40)
V_UL = 150.0


def _faces_uniform(a, b, h):
    n = max(1, int(math.ceil((b - a) / h - 1e-9)))
    return list(np.linspace(a, b, n + 1)[1:])


@dataclass
class WellGeom:
    ref: int = 1
    validation: bool = False  # Cottrell check: flat spot as wide as the bore, no ring, cap or coil, 1 cm deep

    def build(self):
        ref = self.ref
        hc, hf = 0.005 / ref, 0.001 / ref
        if self.validation:
            rf = [0.0] + _faces_uniform(0, R_BORE, hc)
        else:
            rf = [0.0] + _faces_uniform(0, 0.12, hc) + _faces_uniform(0.12, 0.205, hf) + _faces_uniform(0.205, R_BORE, hc)
        rf = np.array(rf)
        zf = [0.0]
        dz, q = 0.0004 / ref, 1.25 ** (1 / ref)
        while dz < hc:
            zf.append(zf[-1] + dz)
            dz *= q
        top_guess = 1.0 if self.validation else 0.60
        if self.validation:
            zf += _faces_uniform(zf[-1], top_guess, hc)
        else:
            zf += _faces_uniform(zf[-1], SQUEEZED, hc) + _faces_uniform(SQUEEZED, Z_THROAT, hc)
            zf += _faces_uniform(Z_THROAT, Z_TIP, hc) + _faces_uniform(Z_TIP, top_guess, hc)
        zf = np.array(zf)
        rc, zc = 0.5 * (rf[1:] + rf[:-1]), 0.5 * (zf[1:] + zf[:-1])
        liq, coil = self.mask(rc, zc)
        if not self.validation:
            # cut the top so the liquid is 150 uL; the last row is trimmed to make it exact
            dr2 = np.pi * (rf[1:] ** 2 - rf[:-1] ** 2)
            dzv = np.diff(zf)
            vrow = (liq * dr2[:, None]).sum(axis=0) * dzv
            cum = np.cumsum(vrow)
            k = int(np.searchsorted(cum, V_UL * 1e-3))
            prev = cum[k - 1] if k else 0.0
            frac = (V_UL * 1e-3 - prev) / vrow[k]
            if frac < 0.35:  # merge a thin last row into the one below
                k -= 1
                frac = 1 + frac * vrow[k + 1] / vrow[k]
            zf = np.r_[zf[:k + 1], zf[k] + frac * dzv[k]]
            zc = 0.5 * (zf[1:] + zf[:-1])
            liq, coil = self.mask(rc, zc)
        self.rf, self.zf, self.rc, self.zc, self.liq, self.coil = rf, zf, rc, zc, liq, coil
        return self

    def mask(self, rc, zc):
        R, Z = np.meshgrid(rc, zc, indexing="ij")
        if self.validation:
            return np.ones_like(R, dtype=bool), np.zeros_like(R, dtype=bool)
        rin = R_CONTACT - np.sqrt(np.clip(RHO ** 2 - (Z - RHO) ** 2, 0.0, None))
        liq = np.where(Z < SQUEEZED, R < rin, np.where(Z < Z_THROAT, R < R_THROAT, R < R_BORE))
        liq &= ~((R < R_CAP) & (Z >= Z_TIP))
        coil = np.zeros_like(liq)
        for z0 in COIL_Z:
            coil |= (R > 0.250) & (R < 0.275) & (np.abs(Z - z0) < 0.0125)
        return liq & ~coil, coil


class Well:
    def __init__(self, geom: WellGeom, dt=1.0):
        g = geom.build() if not hasattr(geom, "liq") else geom
        self.g, self.dt = g, dt
        rf, zf, rc, zc, liq = g.rf, g.zf, g.rc, g.zc, g.liq
        nr, nz = liq.shape
        idx = -np.ones(liq.shape, dtype=int)
        idx[liq] = np.arange(liq.sum())
        self.idx, self.n = idx, int(liq.sum())
        dr2 = np.pi * (rf[1:] ** 2 - rf[:-1] ** 2)
        dzv = np.diff(zf)
        I, K = np.nonzero(liq)
        p = idx[I, K]
        self.vol = np.zeros(self.n)
        self.vol[p] = dr2[I] * dzv[K]
        rows, cols, vals = [], [], []
        # radial faces
        a = liq[:-1, :] & liq[1:, :]
        ii, kk = np.nonzero(a)
        gr = 2 * np.pi * rf[ii + 1] * dzv[kk] / (rc[ii + 1] - rc[ii])
        rows += [idx[ii, kk], idx[ii + 1, kk]]; cols += [idx[ii + 1, kk], idx[ii, kk]]; vals += [gr, gr]
        a = liq[:, :-1] & liq[:, 1:]
        ii, kk = np.nonzero(a)
        gz = dr2[ii] / (zc[kk + 1] - zc[kk])
        rows += [idx[ii, kk], idx[ii, kk + 1]]; cols += [idx[ii, kk + 1], idx[ii, kk]]; vals += [gz, gz]
        off = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(self.n, self.n)).tocsr()
        self.lap = off - sp.diags(np.asarray(off.sum(axis=1)).ravel())
        # free surface (top row)
        self.top = np.zeros(self.n)
        ii = np.nonzero(liq[:, -1])[0]
        self.top[idx[ii, nz - 1]] = dr2[ii] / (dzv[-1] / 2)
        # metal: bottom row
        mi = np.nonzero(liq[:, 0])[0]
        self.metal = idx[mi, 0]
        self.m_r = rc[mi]
        self.m_rf = (rf[mi], rf[mi + 1])
        self.m_area = dr2[mi]
        self.A = float(self.m_area.sum())
        self.hz0 = dzv[0] / 2
        self.m_vol = self.vol[self.metal]
        # coil faces
        self.coil_area = np.zeros(self.n)
        coil = g.coil
        for di, dk in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            I2, K2 = I + di, K + dk
            ok = (I2 >= 0) & (I2 < nr) & (K2 >= 0) & (K2 < nz)
            hit = np.zeros_like(ok)
            hit[ok] = coil[I2[ok], K2[ok]]
            if di:
                face = 2 * np.pi * np.where(di > 0, rf[np.minimum(I + 1, nr)], rf[I]) * dzv[K]
            else:
                face = dr2[I]
            np.add.at(self.coil_area, p[hit], face[hit])
        self.coil_w = self.coil_area / max(self.coil_area.sum(), 1e-30)
        # the reference tip: cells in the row just below the capillary, r < R_CAP
        if not g.validation:
            ktip = int(np.argmin(np.abs(zf - Z_TIP))) - 1
            tip = [idx[i, ktip] for i in range(nr) if rc[i] < R_CAP and idx[i, ktip] >= 0]
            self.tip = np.array(tip)
            self.tip_w = self.vol[self.tip] / self.vol[self.tip].sum()
        self.lu = {}
        self.region_nom = self.m_r < A_NOM

    def factor(self, key, Dk, dirichlet_top=False, robin=None):
        if key in self.lu:
            return self.lu[key]
        diag = self.vol / self.dt + (Dk * self.top if dirichlet_top else 0.0)
        if robin is not None:
            diag = diag.copy()
            diag[self.metal] += robin
        M = (sp.diags(diag) - Dk * self.lap).tocsc()
        lu = spla.splu(M)
        Z = W = None
        if key in ("O2", "Cu1"):
            P = np.zeros((self.n, len(self.metal)))
            P[self.metal, np.arange(len(self.metal))] = 1.0
            Z = lu.solve(P)
            W = Z[self.metal, :]
        self.lu[key] = (lu, Z, W)
        return self.lu[key]

    def phi_solver(self):
        if "phi" not in self.lu:
            M = (-KAPPA * self.lap).tolil()
            p0 = self.tip[0]
            M[p0, p0] = M[p0, p0] + 1e3
            self.lu["phi"] = (spla.splu(M.tocsc()), None, None)
        return self.lu["phi"][0]

    def to_grid(self, c):
        out = np.full(self.g.liq.shape, np.nan)
        out[self.g.liq] = c
        return out


def run_well(w: Well, al: Alloy, steps, snap_times=(), limiting=False, log=None):
    """The protocol in the well. limiting=True: O2-limited spot (c = 0), nothing else (Cottrell check)."""
    dt, n, m = w.dt, w.n, len(w.metal)
    c = {"O2": np.full(n, C_O2_SAT), "Cu1": np.zeros(n), "Cu2": np.zeros(n), "TA": np.zeros(n), "Al": np.zeros(n)}
    susp = np.zeros(n)
    gamma = np.zeros(m)
    q_al = np.zeros(m)
    dphi = np.zeros(m)
    luO, ZO, WO = w.factor("O2", D["O2"], True)
    if limiting:
        dO = w.m_area * D["O2"] / w.hz0
        luL = spla.splu((sp.diags(w.vol / dt + D["O2"] * w.top) - D["O2"] * w.lap + sp.diags(np.bincount(w.metal, dO, n))).tocsc())
        rec = {"t": [], "i_lim": []}
        t = 0.0
        for name, dur, mode, val in steps:
            for s in range(int(round(dur / dt))):
                c["O2"] = luL.solve(w.vol / dt * c["O2"] + D["O2"] * w.top * C_O2_SAT)
                t += dt
                rec["t"].append(t); rec["i_lim"].append(4 * F * float((dO * c["O2"][w.metal]).sum()) / w.A)
        return {k: np.array(v) for k, v in rec.items()}
    luC, ZC, WC = w.factor("Cu1", D["Cu1"])
    d2 = w.m_area * keff(K_CU2_RED, D["Cu2"], w.hz0)
    lu2 = w.factor("Cu2", D["Cu2"], robin=d2)[0]
    luT = w.factor("TA", D["TA"])[0]
    luA = w.factor("Al", D["Al"])[0]
    luP = w.phi_solver()
    eye = np.eye(m)
    rec = {k: [] for k in ("t", "E", "I", "ia", "ic", "ia_nom", "ia_crev", "ic_nom", "ic_crev", "idl", "o2_centre", "o2_crev",
                           "cu1_mol", "cu2_mol", "susp_mol", "film_mol", "q_cu_mol", "ph_centre", "ph_crev", "cu_centre", "cu_crev",
                           "dphi_max_mV", "phi_tip_mV", "phase")}
    rec["counter_o2_mol"] = 0.0
    snaps, si = {}, 0
    snap_times = sorted(snap_times)
    t, E, E_prev, I_prev = 0.0, 0.0, 0.0, 0.0
    q_cu = 0.0
    j_crev = int(np.argmin(np.abs(w.m_r - 0.17)))
    for name, dur, mode, val in steps:
        E_start = E
        for s in range(int(round(dur / dt))):
            # 1 Cu(II): reduced at the metal (fixed Robin)
            c2 = lu2.solve(w.vol / dt * c["Cu2"])
            J2 = d2 * c2[w.metal]
            # 2 O2, with the counter's demand from the last step's net anodic current
            bO = w.vol / dt * c["O2"] + D["O2"] * w.top * C_O2_SAT
            if I_prev > 0 and w.coil_area.sum() > 0:
                demand = I_prev / (4 * F) * dt
                avail = float((w.vol * c["O2"] * (w.coil_area > 0)).sum())
                take = min(demand, 0.5 * avail)
                bO -= take / dt * w.coil_w
                rec["counter_o2_mol"] += take
            yO = luO.solve(bO)
            # 3 Cu(I), with the Cu(I) made from Cu(II) at the metal
            bC = w.vol / dt * c["Cu1"]
            bC[w.metal] += J2
            yC = luC.solve(bC)
            yOs, yCs = yO[w.metal], yC[w.metal]
            beta = 0.0 if (mode == "hold_rel" and val < 0) else BETA_FILM  # replating takes Cu(I) from the liquid only
            dC = w.m_area * keff(al.K(gamma), D["Cu1"], w.hz0) * (1 - beta)  # the liquid's share
            luM = lu_factor(eye + WC * dC[None, :])
            E_prevstep = E

            def parts(Ev):
                El = Ev - dphi
                dO = w.m_area * keff(al.k_c(El), D["O2"], w.hz0)
                sO = np.linalg.solve(eye + WO * dO[None, :], yOs)
                ceq = al.c_eq(El)
                sC = lu_solve(luM, yCs + WC @ (dC * ceq))
                JL = dC * (ceq - sC)  # Cu(I) into the liquid; negative = replating from it
                JO, JC = dO * sO, np.where(JL > 0, JL / (1 - beta), JL)
                ia_l = w.m_area * al.i_al(El, q_al)
                return dO, sO, ceq, sC, JO, JC, ia_l

            cdl = 0.0 if t == 0 else C_DL

            def net(Ev):
                _, _, _, _, JO, JC, ia_l = parts(Ev)
                return F * JC.sum() + ia_l.sum() - 4 * F * JO.sum() - F * J2.sum() + cdl * w.A * (Ev - E_prevstep) / dt

            if mode == "ocp":
                lo, hi = (-0.9, 0.5) if t == 0 else (E_prevstep - 0.3, E_prevstep + 0.3)
                E = brentq(net, lo, hi, xtol=1e-7)
            else:
                E = potential_for(mode, val, E_start, s, dt)
            dO, sO, ceq, sC, JO, JC, ia_l = parts(E)
            q_al += ia_l / w.m_area * dt
            idl_cells = cdl * w.m_area * (E - E_prevstep) / dt
            c["O2"] = yO - ZO @ (dO * sO)
            np.clip(c["O2"], 0.0, None, out=c["O2"])
            JL = np.where(JC > 0, JC * (1 - beta), JC)
            c["Cu1"] = yC + ZC @ JL
            c["Cu2"] = c2
            q_cu += float(JC.sum()) * dt
            jf = JC - JL
            gamma += jf / w.m_area * dt
            i_cells = F * JC + ia_l - 4 * F * JO - F * J2 + idl_cells  # A per metal cell, into the liquid
            I_net = float(i_cells.sum())
            # 4 alkalinity and Al
            bT = w.vol / dt * c["TA"]
            bT[w.metal] += 4 * JO - ia_l / F - jf
            bT += (I_net / F) * w.coil_w  # counter: OH- when cathodic (I_net > 0), H+ when anodic
            c["TA"] = luT.solve(bT)
            bA = w.vol / dt * c["Al"]
            bA[w.metal] += ia_l / (3 * F)
            c["Al"] = luA.solve(bA)
            # 5 homogeneous chemistry, split
            x = c["Cu1"] * (1 - np.exp(-K_OX * c["O2"] / C_O2_SAT * dt))
            x = np.minimum(x, 4 * c["O2"])
            c["Cu1"] -= x; c["Cu2"] += x; c["O2"] -= x / 4; c["TA"] += x
            ph = ph_of(c["TA"])
            cs = csat_cu2o(ph)
            ex = c["Cu1"] - cs
            pp = np.where(ex > 0, ex * (1 - math.exp(-K_P_HOM * dt)), 0.0)
            dis = np.where(ex < 0, np.minimum(susp / w.vol, -ex * (1 - math.exp(-K_P_HOM * dt))), 0.0)
            c["Cu1"] += dis - pp; c["TA"] += dis - pp; susp += (pp - dis) * w.vol
            exm = c["Cu1"][w.metal] - cs[w.metal]
            ps = np.where(exm > 0, np.minimum(K_P_SURF * w.m_area * exm * dt, exm * w.m_vol), 0.0)
            c["Cu1"][w.metal] -= ps / w.m_vol; c["TA"][w.metal] -= ps / w.m_vol
            gamma += ps / w.m_area
            # 6 electrolyte potential from this step's currents, used (lagged) next step
            src = np.zeros(n)
            np.add.at(src, w.metal, i_cells)
            src -= I_net * w.coil_w
            phi = luP.solve(src)
            phi_tip = float((phi[w.tip] * w.tip_w).sum())
            dphi = phi[w.metal] - phi_tip
            E_prev, I_prev = E, I_net
            t += dt
            ia_c = F * JC + ia_l
            ic_c = -4 * F * JO - F * J2
            nom = w.region_nom
            rec["t"].append(t); rec["E"].append(E); rec["I"].append(I_net); rec["idl"].append(float(idl_cells.sum()))
            rec["ia"].append(float(ia_c.sum())); rec["ic"].append(float(ic_c.sum()))
            rec["ia_nom"].append(float(ia_c[nom].sum())); rec["ia_crev"].append(float(ia_c[~nom].sum()))
            rec["ic_nom"].append(float(ic_c[nom].sum())); rec["ic_crev"].append(float(ic_c[~nom].sum()))
            rec["o2_centre"].append(float(c["O2"][w.metal[0]])); rec["o2_crev"].append(float(c["O2"][w.metal[j_crev]]))
            rec["cu1_mol"].append(float((w.vol * c["Cu1"]).sum())); rec["cu2_mol"].append(float((w.vol * c["Cu2"]).sum()))
            rec["susp_mol"].append(float(susp.sum())); rec["film_mol"].append(float((gamma * w.m_area).sum()))
            rec["q_cu_mol"].append(q_cu)
            rec["ph_centre"].append(float(ph[w.metal[0]])); rec["ph_crev"].append(float(ph[w.metal[j_crev]]))
            rec["cu_centre"].append(float(c["Cu1"][w.metal[0]] + c["Cu2"][w.metal[0]]))
            rec["cu_crev"].append(float(c["Cu1"][w.metal[j_crev]] + c["Cu2"][w.metal[j_crev]]))
            rec["dphi_max_mV"].append(float(np.abs(dphi).max() * 1e3)); rec["phi_tip_mV"].append(phi_tip * 1e3)
            rec["phase"].append(name)
            while si < len(snap_times) and t >= snap_times[si] - 1e-9:
                snaps[snap_times[si]] = {"o2": w.to_grid(c["O2"] / C_O2_SAT), "cu": w.to_grid((c["Cu1"] + c["Cu2"]) * 1e9),
                                         "cu1": w.to_grid(c["Cu1"] * 1e9), "ph": w.to_grid(ph), "phi": w.to_grid((phi - phi_tip) * 1e3),
                                         "ia_density": ia_c / w.m_area, "ic_density": ic_c / w.m_area, "film": gamma.copy()}
                si += 1
            if log and int(t) % 600 == 0:
                log(f"    t {t:5.0f} s  E {E * 1e3:7.1f} mV  I {I_net * 1e9:8.2f} nA  pH {ph[w.metal[0]]:.3f}")
    for k in list(rec):
        if k not in ("phase", "counter_o2_mol"):
            rec[k] = np.array(rec[k])
    rec["al_mol"] = float((w.vol * c["Al"]).sum())
    return rec, snaps


# ------------------------------------------------------------------ analysis helpers
def at(rec, key, t_s):
    i = int(np.searchsorted(rec["t"], t_s - 1e-9))
    return float(rec[key][min(i, len(rec[key]) - 1)])


def lpr_rp(rec, area, skip_s=10):
    """R_p from the LPR sweep's E-I slope, leaving out the first skip_s seconds (the charging transient of the
    -10 mV step into the sweep)."""
    ph = np.array(rec["phase"])
    sel = ph == "LPR"
    sel[np.nonzero(sel)[0][:skip_s]] = False
    slope = np.polyfit(rec["I"][sel], rec["E"][sel], 1)[0]
    return slope * area


def cottrell(t):
    return 4 * F * C_O2_SAT * np.sqrt(D["O2"] / (np.pi * t))


def summarise_well(w: Well, al: Alloy, rec, bulk):
    ph = np.array(rec["phase"])
    hold = ph == "anodic hold +50 mV"
    A_wet, A_nom = w.A, math.pi * A_NOM ** 2
    rp_nom, rp_wet = lpr_rp(rec, A_nom), lpr_rp(rec, A_wet)
    rp_bulk = lpr_rp(bulk, 1.0)
    e_bulk_30 = at(bulk, "E", 1800)
    cu_liq = rec["cu1_mol"][-1] + rec["cu2_mol"][-1] + rec["susp_mol"][-1]
    film = rec["film_mol"][-1]
    q_an = float(np.clip(rec["ia"], 0, None).sum() * w.dt)  # anodic charge passed (Cu + Al paths), C
    q_net = float(rec["I"].sum() * w.dt)
    t30 = 1800
    out = {
        "E_corr_30min_mV_SCE": round(at(rec, "E", t30) * 1e3, 1),
        "E_corr_30min_bulk_mV_SCE": round(e_bulk_30 * 1e3, 1),
        "E_corr_shift_well_minus_bulk_mV": {f"{tt // 60}min": round((at(rec, "E", tt) - at(bulk, "E", tt)) * 1e3, 1) for tt in (60, 300, 900, 1800)},
        "i_corr_30min_uA_cm2_wetted_area": round(at(rec, "ia", t30) / A_wet * 1e6, 3),
        "i_corr_30min_uA_cm2_nominal_area": round(at(rec, "ia", t30) / A_nom * 1e6, 3),
        "i_corr_30min_bulk_uA_cm2": round(at(bulk, "ia", t30) * 1e6, 3),
        "i_corr_ratio_well_over_bulk_30min": round(at(rec, "ia", t30) / A_wet / at(bulk, "ia", t30), 3),
        "Rp_well_nominal_area_ohm_cm2": round(rp_nom), "Rp_well_wetted_area_ohm_cm2": round(rp_wet), "Rp_bulk_ohm_cm2": round(rp_bulk),
        "Rp_ratio_nominal_over_bulk": round(rp_nom / rp_bulk, 3), "Rp_ratio_wetted_over_bulk": round(rp_wet / rp_bulk, 3),
        "hold_current_uA": [round(float(rec["I"][hold].min()) * 1e6, 4), round(float(rec["I"][hold].max()) * 1e6, 4)],
        "hold_mean_uA_cm2_wetted": round(float(rec["I"][hold].mean()) / A_wet * 1e6, 3),
        "hold_mean_bulk_uA_cm2": round(float(bulk["I"][np.array(bulk["phase"]) == "anodic hold +50 mV"].mean()) * 1e6, 3),
        "hold_ratio_well_over_bulk": round(float(rec["I"][hold].mean()) / A_wet / float(bulk["I"][np.array(bulk["phase"]) == "anodic hold +50 mV"].mean()), 3),
        "hold_charge_mC": round(float(rec["I"][hold].sum() * w.dt) * 1e3, 4),
        "anodic_charge_mC": round(q_an * 1e3, 4), "net_charge_mC": round(q_net * 1e3, 4),
        "cu_dissolved_ng": round(rec["q_cu_mol"][-1] * 63.546e9, 1),
        "cu_in_liquid_ng": {"CuI": round(rec["cu1_mol"][-1] * 63.546e9, 1), "CuII": round(rec["cu2_mol"][-1] * 63.546e9, 1),
                            "Cu2O_suspended": round(rec["susp_mol"][-1] * 63.546e9, 1)},
        "cu_in_film_ng": round(film * 63.546e9, 1),
        "cu_to_tube_ng": round(cu_liq * 63.546e9, 1),
        "cu_in_150uL_ug_L": round(cu_liq * 63.546e6 / 150e-6, 1),
        "cu_in_320uL_tube_ug_L": round(cu_liq * 63.546e6 / 320e-6, 1),
        "fraction_of_dissolved_cu_reaching_tube": round(cu_liq / max(rec["q_cu_mol"][-1], 1e-30), 3),
        "cu_as_charge_mC_if_CuI": round(cu_liq * F * 1e3, 4),
        "mass_balance_error_pct": round((cu_liq + film - rec["q_cu_mol"][-1]) / max(rec["q_cu_mol"][-1], 1e-30) * 100, 3),
        "crevice_share_of_anodic_current": {lab: round(at(rec, "ia_crev", tt) / max(at(rec, "ia", tt), 1e-30), 3)
                                            for lab, tt in (("OCP_30min", 1800), ("LPR_end", 1920), ("hold_end", 2820))},
        "crevice_share_of_cathodic_current": {lab: round(at(rec, "ic_crev", tt) / min(at(rec, "ic", tt), -1e-30), 3)
                                              for lab, tt in (("OCP_30min", 1800), ("LPR_end", 1920), ("hold_end", 2820))},
        "O2_pct_sat_centre_30min": round(at(rec, "o2_centre", 1800) / C_O2_SAT * 100, 1),
        "O2_pct_sat_crevice_r1p7_30min": round(at(rec, "o2_crev", 1800) / C_O2_SAT * 100, 1),
        "pH_centre": {lab: round(at(rec, "ph_centre", tt), 3) for lab, tt in (("OCP_30min", 1800), ("hold_end", 2820), ("end", 3120))},
        "pH_crevice_r1p7": {lab: round(at(rec, "ph_crev", tt), 3) for lab, tt in (("OCP_30min", 1800), ("hold_end", 2820), ("end", 3120))},
        "dissolved_cu_at_metal_uM": {lab: round(at(rec, "cu_centre", tt) * 1e9, 1) for lab, tt in (("OCP_30min", 1800), ("hold_end", 2820))},
        "dissolved_cu_in_crevice_uM": {lab: round(at(rec, "cu_crev", tt) * 1e9, 1) for lab, tt in (("OCP_30min", 1800), ("hold_end", 2820))},
        "max_ohmic_nonuniformity_on_metal_uV": {lab: round(at(rec, "dphi_max_mV", tt) * 1e3, 2) for lab, tt in (("OCP_30min", 1800), ("LPR_end", 1920), ("hold_end", 2820))},
        "counter_O2_used_nmol": round(rec["counter_o2_mol"] * 1e9, 3),
        "double_layer_charge_in_LPR_pct": round(float(np.abs(rec["idl"][ph == "LPR"]).sum() / np.abs(rec["I"][ph == "LPR"]).sum() * 100), 2),
    }
    if al.al_path:
        out["al_released_ng"] = round(rec["al_mol"] * 26.98e9, 1)
        out["al_in_320uL_tube_ug_L"] = round(rec["al_mol"] * 26.98e6 / 320e-6, 1)
    return out


def convection_estimates():
    """Rayleigh numbers for the 4.4 mm column, against the 1101 of a layer with a rigid bottom and free top."""
    g, nu, kT, alphaT, L = 981.0, 0.0095, 1.46e-3, 2.6e-4, 0.44  # cgs, seawater 25 C
    out = {"L_cm": L, "Ra_critical_rigid_free_infinite_layer": 1101}
    for dT in (0.1, 1.0):
        out[f"thermal_bottom_heated_dT_{dT}K"] = round(g * alphaT * dT * L ** 3 / (nu * kT), 1)
    # O2 depletion at the metal: removing O2 (32 g/mol, partial molar volume ~ 28-32 cm3/mol) changes density by
    # -c (M - rho V); the sign depends on V, so bound it.
    for V in (28.0, 32.0):
        drho = -C_O2_SAT * (32.0 - 1.025 * V)  # g/cm3, bottom minus top when the bottom is fully depleted
        out[f"solutal_O2_V{V:.0f}"] = round(g * (-drho / 1.025) * L ** 3 / (nu * D["O2"]), 1)
    # dissolved Cu at the bottom makes it denser: stable. Report the stabilising number at 100 uM CuCl2- (~ +120 g/mol net)
    out["solutal_Cu_100uM_stabilising"] = round(-g * (100e-9 * 120.0 / 1.025) * L ** 3 / (nu * D["Cu1"]), 1)
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip the h/2 grid-convergence run")
    args = ap.parse_args()
    global K_OX, BETA_FILM
    t0 = time.time()

    def log(s):
        print(f"[{time.time() - t0:6.0f} s] {s}", flush=True)

    out = {"constants": {
        "C_O2_sat_mM": C_O2_SAT * 1e6, "D_cm2_s": D, "kappa_S_cm": KAPPA, "Cl_M": CL_M, "gamma_1": round(G1, 3),
        "E0_CuCl2_Cu_V_SHE": round(E0_CUCL2, 4), "logK_Cu2O_to_CuCl2": round(LOGK_CU2O, 3),
        "E_Cu2O_Cu_pH8p2_V_SCE": round(E_CU2O_PH0 - 0.05916 * PH0 - E_SCE, 4),
        "CuCl2_sat_Cu2O_pH8p2_uM": round(csat_cu2o(PH0) * 1e9, 2),
        "k_ox_CuI_air_per_s": round(K_OX, 6), "CuI_half_life_air_s": round(math.log(2) / K_OX, 1),
        "CuI_speciation": {k: float(f"{v:.3e}") for k, v in CU1_SPECIATION.items()},
        "TA0_mM": round(TA0 * 1e3, 4), "buffer_capacity_mM_per_pH_at_8p2": round(float((ta_of_ph(8.21) - ta_of_ph(8.19)) / 0.02 * 1e3), 3),
        "K0_cm_s": K0, "alpha_c": ALPHA_C, "b_c_mV_dec": round(LN10 / (ALPHA_C * FRT) * 1e3, 1), "b_Al_mV_dec": B_AL * 1e3,
        "C_dl_uF_cm2": C_DL * 1e6, "k_p_hom_per_s": K_P_HOM, "k_p_surf_cm_s": K_P_SURF, "k_CuII_red_cm_s": K_CU2_RED,
        "oring": {"squeezed_height_mm": SQUEEZED * 10, "squeeze_pct": round((1 - SQUEEZED / CS) * 100, 1),
                  "flat_contact_inner_r_mm": round(R_CONTACT * 10, 4), "section_innermost_r_mm": round((R_CONTACT - RHO) * 10, 4),
                  "flat_width_mm": round(W_FLAT * 10, 4)}}}
    out["geometry"] = {"nominal_area_cm2": round(math.pi * A_NOM ** 2, 5), "wetted_area_exact_cm2": round(math.pi * R_CONTACT ** 2, 5),
                       "wetted_over_nominal": round(R_CONTACT ** 2 / A_NOM ** 2, 3)}
    out["convection"] = convection_estimates()

    # 0 Cottrell check
    wv = Well(WellGeom(validation=True))
    rv = run_well(wv, None, [("ocp", 600, "ocp", 0)], limiting=True)
    out["check_cottrell"] = {f"{s}s": round(float(rv["i_lim"][s - 1] / cottrell(s)), 4) for s in (30, 120, 300, 600)}
    log(f"Cottrell {out['check_cottrell']}")

    # 1 calibrate each alloy's bulk cell
    alloys = ALLOYS()
    out["calibration"] = {}
    for key, al in alloys.items():
        log(f"calibrating {key}")
        if al.al_path:  # NAB's Cu2O film (when the liquid at the metal ever saturates) behaves as 90/10's: ASSUMED
            al.gamma_star = alloys["C70600"].gamma_star
        b = calibrate(al, log)
        t, E, ia = b.ocp_run(al.tau_h * 3600 * 2, dt=60.0)
        rp_cal = (b.ocp_run(al.t_cal_s, dt=30.0), b.rp_now())[1]
        out["calibration"][key] = {
            "name": al.name, "x_Cu": al.x_cu, "k_O2_cm_s_at_-0.25V_SCE": float(f"{al.k_o2:.4e}"), "i_Al0_A_cm2": float(f"{al.i_al0:.4e}"),
            "gamma_star_mol_cm2": float(f"{al.gamma_star:.4e}"), "gamma_star_nm_Cu2O": round(al.gamma_star * V_FILM * 1e7, 3),
            "target_Rp_ohm_cm2": al.rp_target, "model_Rp_at_t_cal_ohm_cm2": round(rp_cal), "t_cal_h": al.t_cal_s / 3600,
            "target_E_corr_V_SCE": al.ec_target, "model_E_corr_at_t_cal_V_SCE": round(b.E, 4),
            "model_i_corr_uA_cm2": {f"{h}h": round(float(np.interp(h * 3600, t, ia)) * 1e6, 3) for h in (0.1, 0.5, 1, 3, al.tau_h)},
            "target_tau_h": al.tau_h,
            "model_decay_at_tau": round(float(np.interp(al.tau_h * 3600, t, ia) / np.interp(300, t, ia)), 4),
            "target_decay_at_tau": round(math.sqrt((1 + 300 / (al.tau_h * 3600)) / 2), 4)}
    out["calibration"]["C70600"]["literature_E_corr_V_SCE"] = "-0.220 to -0.233 (Mantzavinos 2001, ASW 20 C, via Edison c1-03)"

    # 2 the protocol in the bulk cell and in the well, each alloy
    snap_t = [5, 60, 300, 900, 1800, 2100, 2820, 3120]
    g1 = WellGeom(ref=1).build()
    w1 = Well(g1)
    out["grid"] = {"cells_liquid": w1.n, "metal_cells": len(w1.metal), "first_cell_um": round(float(np.diff(g1.zf)[0]) * 1e4, 2),
                   "wetted_area_resolved_cm2": round(w1.A, 5), "liquid_uL": round(float(w1.vol.sum()) * 1e3, 2),
                   "liquid_height_mm": round(float(g1.zf[-1]) * 10, 3)}
    out["wells"], recs, bulks = {}, {}, {}
    for key, al in alloys.items():
        log(f"bulk sequence {key}")
        bulks[key] = run_bulk(al, SEQ)
        log(f"well sequence {key}")
        rec, snaps = run_well(w1, al, SEQ, snap_times=snap_t if key == "C71500" else (), log=log)
        recs[key] = (rec, snaps)
        out["wells"][key] = summarise_well(w1, al, rec, bulks[key])
        log(json.dumps(out["wells"][key])[:600])

    # 3 cathodic hold after the anodic hold, C71500
    al = alloys["C71500"]
    rc_, _ = run_well(w1, al, SEQ_CATH)
    ph_ = np.array(rc_["phase"])
    before = float((rc_["cu1_mol"] + rc_["cu2_mol"] + rc_["susp_mol"])[ph_ == "anodic hold +50 mV"][-1])
    after = float(rc_["cu1_mol"][-1] + rc_["cu2_mol"][-1] + rc_["susp_mol"][-1])
    out["cathodic_hold_C71500"] = {"cu_in_liquid_before_ng": round(before * 63.546e9, 1), "cu_in_liquid_after_10min_ng": round(after * 63.546e9, 1),
                                   "replated_pct": round((1 - after / before) * 100, 1),
                                   "cathodic_current_density_end_uA_cm2_wetted": round(float(rc_["I"][-1]) / w1.A * 1e6, 2),
                                   "pH_centre_end": round(float(rc_["ph_centre"][-1]), 3)}
    log(f"cathodic {out['cathodic_hold_C71500']}")

    # 4 sensitivity: Cu(I) oxidation ten times slower
    k_keep = K_OX
    K_OX = k_keep / 10
    rs, _ = run_well(w1, al, SEQ)
    out["sensitivity_C71500"] = {"CuI_oxidation_10x_slower": {k: summarise_well(w1, al, rs, bulks["C71500"])[k] for k in
                                                               ("E_corr_30min_mV_SCE", "Rp_well_nominal_area_ohm_cm2", "hold_mean_uA_cm2_wetted",
                                                                "cu_to_tube_ng", "fraction_of_dissolved_cu_reaching_tube", "O2_pct_sat_centre_30min")}}
    K_OX = k_keep
    # and the film's share of the Cu oxidised, recalibrating gamma* each time
    b_keep = BETA_FILM
    for beta in (0.1, 0.6):
        BETA_FILM = beta
        alb = ALLOYS()["C71500"]
        calibrate(alb, lambda s_: None)
        bb = run_bulk(alb, SEQ)
        rb, _ = run_well(w1, alb, SEQ)
        sb = summarise_well(w1, alb, rb, bb)
        out["sensitivity_C71500"][f"film_share_beta_{beta}"] = {"k_O2": float(f"{alb.k_o2:.4e}"), "gamma_star": float(f"{alb.gamma_star:.4e}"),
                                                                **{k: sb[k] for k in ("E_corr_30min_mV_SCE", "E_corr_30min_bulk_mV_SCE", "Rp_well_nominal_area_ohm_cm2",
                                                                                      "Rp_bulk_ohm_cm2", "hold_mean_uA_cm2_wetted", "cu_to_tube_ng", "cu_in_film_ng",
                                                                                      "fraction_of_dissolved_cu_reaching_tube")}}
    BETA_FILM = b_keep
    log(f"sensitivity {out['sensitivity_C71500']}")

    # 5 grid convergence, C71500
    if not args.quick:
        g2 = WellGeom(ref=2).build()
        w2 = Well(g2)
        log(f"h/2 grid: {w2.n} liquid cells, {len(w2.metal)} metal cells")
        r2, _ = run_well(w2, al, SEQ, log=log)
        s1, s2 = out["wells"]["C71500"], summarise_well(w2, al, r2, bulks["C71500"])
        keys = ("E_corr_30min_mV_SCE", "Rp_well_nominal_area_ohm_cm2", "hold_mean_uA_cm2_wetted", "cu_dissolved_ng", "cu_to_tube_ng",
                "cu_in_film_ng", "O2_pct_sat_centre_30min")
        out["check_grid_C71500"] = {"h": {k: s1[k] for k in keys}, "h_over_2": {k: s2[k] for k in keys},
                                    "wetted_area_cm2": {"h": round(w1.A, 5), "h_over_2": round(w2.A, 5)},
                                    "crevice_share_OCP": {"h": s1["crevice_share_of_anodic_current"]["OCP_30min"], "h_over_2": s2["crevice_share_of_anodic_current"]["OCP_30min"]}}
        log(f"grid {out['check_grid_C71500']}")

    # 6 the old model's numbers for comparison (cap B, 5 uA/cm2)
    old = json.loads((HERE / "sim_well.json").read_text())
    out["old_sim_well_capB"] = {k: old["sequence"]["B"][k] for k in ("E_ocp_end_mV_vs_bulk", "Rp_ratio_well_over_bulk", "anodic_hold_well_over_bulk",
                                                                    "cu_dissolved_ng", "O2_at_spot_centre_end_of_OCP_pct_sat")}
    out["old_sim_well_capB"]["replated_pct"] = old["cathodic_hold_after_anodic"]["replated_pct"]
    out["runtime_s"] = round(time.time() - t0)
    (HERE / "sim_well_hf.json").write_text(json.dumps(out, indent=1) + "\n")

    # fields for the renderer, resampled to a regular 0.05 mm grid
    rec, snaps = recs["C71500"]
    save_fields(g1, w1, rec, snaps)
    plot(out, w1, recs, bulks)
    log("done")


def save_fields(g, w, rec, snaps):
    H = 0.005
    nr, nz = int(round(R_BORE / H)), int(math.ceil(g.zf[-1] / H))
    r = (np.arange(nr) + 0.5) * H
    z = (np.arange(nz) + 0.5) * H
    ii = np.clip(np.searchsorted(g.rf, r) - 1, 0, len(g.rc) - 1)
    kk = np.clip(np.searchsorted(g.zf, z) - 1, 0, len(g.zc) - 1)
    inside = z[None, :] < g.zf[-1]

    def res(a):
        out = a[np.ix_(ii, kk)].copy()
        out[:, ~inside[0]] = np.nan
        return out
    times = np.array(sorted(snaps))
    liq = ~np.isnan(res(np.where(g.liq, 1.0, np.nan)))
    coil = g.coil[np.ix_(ii, kk)]
    np.savez_compressed(HERE / "sim_well_hf_fields.npz", r=r, z=z, liquid=liq, coil=coil, times=times,
                        o2=np.array([res(snaps[t]["o2"]) for t in times]), cu=np.array([res(snaps[t]["cu"]) for t in times]),
                        ph=np.array([res(snaps[t]["ph"]) for t in times]),
                        film=np.array([snaps[t]["film"] for t in times]), film_r=w.m_r,
                        trace_t=rec["t"], trace_E=rec["E"], trace_I=rec["I"],
                        a=A_NOM, a_wetted=R_CONTACT, z_step=Z_THROAT, r_bore=R_BORE, h_liq=float(g.zf[-1]), z_tip=Z_TIP, r_cap=R_CAP,
                        oring=np.array([R_RING, RHO, W_FLAT, SQUEEZED]))


# ------------------------------------------------------------------ figure
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
COL = {"C70600": "#1baf7a", "C71500": "#2a78d6", "C95800": "#eb6834"}


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, lw=0.6)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    for s in ax.spines.values():
        s.set_color(GRID)


def plot(out, w, recs, bulks):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.patches import Polygon, Rectangle

    blues = LinearSegmentedColormap.from_list("blues", ["#0d366b", "#256abf", "#6da7ec", "#cde2fb"])
    fig = plt.figure(figsize=(16, 9.6), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.1, 1, 1], wspace=0.30, hspace=0.40)
    g = w.g
    rec, snaps = recs["C71500"]

    # A: O2 and the O-ring section after 30 min, C71500
    ax = fig.add_subplot(gs[0, 0])
    o2 = snaps[1800]["o2"]
    full = np.concatenate([o2[::-1, :], o2], axis=0).T
    rr = np.concatenate([-g.rf[::-1], g.rf[1:]]) * 10
    im = ax.pcolormesh(rr, g.zf * 10, full, cmap=blues, vmin=0, vmax=1, shading="flat")
    th = np.linspace(-math.pi / 2, math.pi / 2, 40)
    sec = np.r_[np.c_[R_CONTACT + W_FLAT + RHO * np.cos(th), RHO + RHO * np.sin(th)],
                np.c_[R_CONTACT - RHO * np.cos(th), RHO - RHO * np.sin(th)]] * 10
    for sgn in (1, -1):
        ax.add_patch(Polygon(np.c_[sgn * sec[:, 0], sec[:, 1]], closed=True, fc="#1d1d1d", ec="none"))
        ax.add_patch(Rectangle((sgn * 1.45 if sgn > 0 else -3.65, 1.40), 2.20, 0.20, fc="#e9a47c", ec="none"))
        ax.add_patch(Rectangle((sgn * 3.65 if sgn > 0 else -4.6, 0.0), 0.95, 1.60, fc="#e9a47c", ec="none"))
    ax.add_patch(Rectangle((-1.0, 3.0), 2.0, 2.0, fc="#eeeeea", ec=INK2, lw=0.8))
    ax.axhline(0, color="#b87333", lw=3)
    ax.set_aspect("equal"); ax.set_xlim(-4.3, 4.3); ax.set_ylim(-0.4, g.zf[-1] * 10 + 0.3)
    ax.set_facecolor("#f3e3d6")
    ax.text(0, 3.9, "Ag/AgCl", ha="center", fontsize=7, color=INK2)
    ax.text(0, -0.12, f"wetted metal Ø{2 * R_CONTACT * 10:.2f} mm (nominal Ø2.90)", ha="center", va="top", fontsize=7, color=INK2)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("O₂, fraction of saturation", fontsize=7.5, color=INK2)
    cb.ax.tick_params(labelsize=7, colors=MUTED)
    ax.set_xlabel("r, mm", fontsize=8, color=INK2); ax.set_ylabel("z, mm", fontsize=8, color=INK2)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    ax.set_title("A  O₂ after 30 min at open circuit, C71500,\nwith the squeezed O-ring's section (black)", fontsize=9, color=INK, loc="left")

    # B: crevice close-up: anodic and cathodic current density along the metal, three moments
    ax = fig.add_subplot(gs[0, 1]); style(ax)
    for tt, ls, lab in ((1800, "-", "OCP, 30 min"), (2820, "--", "end of +50 mV hold")):
        s = snaps[tt]
        ax.plot(w.m_r * 10, s["ia_density"] * 1e6, color=COL["C71500"], lw=1.8, ls=ls, label=f"anodic, {lab}")
        ax.plot(w.m_r * 10, -s["ic_density"] * 1e6, color="#c0392b", lw=1.4, ls=ls, label=f"cathodic, {lab}")
    ax.axvline(1.45, color=MUTED, lw=1)
    ax.text(1.43, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 1, "nominal edge", ha="right", fontsize=7, color=INK2)
    ax.axvspan(1.45, R_CONTACT * 10, color="#efe9e2", lw=0)
    ax.set_yscale("log"); ax.set_xlim(0, R_CONTACT * 10 + 0.05)
    ax.set_xlabel("r on the metal, mm", fontsize=8, color=INK2)
    ax.set_ylabel("current density, µA/cm²", fontsize=8, color=INK2)
    ax.legend(fontsize=6.5, frameon=False, loc="lower left")
    ax.set_title("B  Where the current flows: open spot vs the crevice\nunder the ring (shaded), C71500", fontsize=9, color=INK, loc="left")

    # C: E_corr in well and bulk, three alloys
    ax = fig.add_subplot(gs[0, 2]); style(ax)
    for key, (r_, _) in recs.items():
        ax.plot(r_["t"] / 60, r_["E"] * 1e3, color=COL[key], lw=2, label=f"{key} well")
        ax.plot(bulks[key]["t"] / 60, bulks[key]["E"] * 1e3, color=COL[key], lw=1.2, ls=":", label=f"{key} bulk cell")
    ax.set_xlim(0, 52)
    ax.set_xlabel("minutes", fontsize=8, color=INK2); ax.set_ylabel("E, mV vs SCE", fontsize=8, color=INK2)
    ax.legend(fontsize=6.5, frameon=False, loc="lower right", ncol=2)
    ax.set_title("C  Potential through the sequence (OCP, LPR, rest,\n+50 mV hold, OCP): well vs bulk cell", fontsize=9, color=INK, loc="left")

    # D: current through the spot
    ax = fig.add_subplot(gs[1, 0]); style(ax)
    for key, (r_, _) in recs.items():
        ax.plot(r_["t"] / 60, r_["I"] * 1e9, color=COL[key], lw=1.5, label=key)
    ax.set_yscale("symlog", linthresh=10)
    for x0, x1, lab in ((0, 30, "OCP"), (30, 32, "LPR"), (32, 37, "rest"), (37, 47, "+50 mV hold"), (47, 52, "OCP")):
        ax.axvline(x1, color=GRID, lw=0.8)
        ax.text((x0 + x1) / 2, 2.5e4, lab, ha="center", fontsize=6.5, color=INK2, rotation=90 if x1 - x0 < 6 else 0)
    ax.set_xlim(0, 52); ax.set_ylim(-3e3, 6e4)
    ax.set_xlabel("minutes", fontsize=8, color=INK2); ax.set_ylabel("current through the spot, nA (symlog)", fontsize=8, color=INK2)
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    ax.set_title("D  Current the potentiostat sees, per alloy", fontsize=9, color=INK, loc="left")

    # E: where the copper goes, C71500
    ax = fig.add_subplot(gs[1, 1]); style(ax)
    tm = rec["t"] / 60
    ax.plot(tm, rec["q_cu_mol"] * 63.546e9, color=INK, lw=2, label="Cu dissolved from the metal")
    ax.plot(tm, rec["cu1_mol"] * 63.546e9, color=COL["C71500"], lw=1.6, label="Cu(I) in the liquid")
    ax.plot(tm, rec["cu2_mol"] * 63.546e9, color="#7a5fc0", lw=1.6, label="Cu(II) in the liquid")
    ax.plot(tm, rec["susp_mol"] * 63.546e9, color="#b87333", lw=1.6, label="Cu₂O suspended")
    ax.plot(tm, rec["film_mol"] * 63.546e9, color="#c0392b", lw=1.6, label="Cu₂O on the metal (film)")
    ax.set_xlim(0, 52)
    ax.set_xlabel("minutes", fontsize=8, color=INK2); ax.set_ylabel("ng of Cu", fontsize=8, color=INK2)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left")
    ax.set_title("E  Where the copper goes, C71500 (the tube gets the liquid,\nnot the film)", fontsize=9, color=INK, loc="left")

    # F: well / bulk biases per alloy, and pH
    ax = fig.add_subplot(gs[1, 2]); style(ax)
    keys = list(recs)
    xs = np.arange(len(keys))
    W_ = out["wells"]
    bars = [("i_corr_ratio_well_over_bulk_30min", "i_corr, 30 min"), ("Rp_ratio_nominal_over_bulk", "R_p (nominal area)"),
            ("Rp_ratio_wetted_over_bulk", "R_p (wetted area)"), ("hold_ratio_well_over_bulk", "hold current")]
    cols = ["#2a78d6", "#eb6834", "#f2b591", "#1baf7a"]
    for j, ((k, lab), cc) in enumerate(zip(bars, cols)):
        vals = [W_[a][k] for a in keys]
        ax.bar(xs + (j - 1.5) * 0.2, vals, 0.19, color=cc, label=lab)
        for x_, v in zip(xs + (j - 1.5) * 0.2, vals):
            ax.text(x_, v + 0.03, f"{v:.2f}", ha="center", fontsize=6, color=INK2)
    ax.axhline(1, color=MUTED, lw=1)
    ax.set_xticks(xs); ax.set_xticklabels([f"{k}\n{ALLOYS()[k].name}" for k in keys], fontsize=7.5, color=INK2)
    ax.set_ylabel("well ÷ bulk cell", fontsize=8, color=INK2)
    ax.legend(fontsize=6.5, frameon=False, loc="upper left", ncol=2)
    ax.set_title("F  What the well does to each number", fontsize=9, color=INK, loc="left")

    fig.text(0.5, 0.012, "Model, not measurement. 2D axisymmetric reaction-transport in the sealed 150 µL well (AS568-006 squeezed 21 %, wetted to r 2.00 mm), "
             "Cu + 2Cl⁻ ⇌ CuCl₂⁻ + e⁻ with a Cu₂O film, O₂ reduction, Cu(I) oxidation, Cu₂O precipitation, buffered pH, double layer and electrolyte potential. "
             "Bulk cells calibrated to published R_p (and E_corr for NAB).", ha="center", fontsize=7.2, color=INK2, wrap=True)
    fig.savefig(HERE / "sim_well_hf.png", dpi=150, facecolor=SURFACE, bbox_inches="tight")


if __name__ == "__main__":
    main()

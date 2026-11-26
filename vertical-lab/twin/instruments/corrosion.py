"""The ONR campaign's seawater corrosion instruments: the CubXL electrochemical screen on a 0.071 cm^2 O-ring well,
and the 30-day immersion with mass loss, an SEM cross-section and ICP-MS of the solution.

Both are driven by the deposit's hidden state: ``sample['corrosion']`` from ``truth_cu.CuTruth.corrosion`` (the
long-term rate ``rate_um_yr``, the 30-day selective ``attack_um``, the one-hour ``early_rate_um_yr``, the breakdown
potential ``Eb_mV`` and the film's time constant ``film_days``), plus the part's composition, porosity, pore
populations and retained beta'. Each instrument makes the raw data a real one would (potential transients, a
polarization curve, an impedance spectrum, balance readings, attack depths per SEM field, ICP-MS counts) and then runs
the analysis a lab runs on it, so the numbers carry the analysis's biases as well as noise.

**Screen** (``measure_screen``; the CubXL protocol of notes/cubxl_corrosion.md, with the OCP stretched to an hour):

1. *OCP*, 60 min (``ocp_min``): a freshly ground Cu alloy ennobles as its Cu2O film forms,
   E(t) = E_inf + dE0 exp(-t/tau) + a random walk + white noise; the reported OCP is the mean of the last 2 min.
   E_inf vs Ag/AgCl (3 M KCl) rises with Ni, Al and dissolved Fe and falls with beta' (assumed, anchored on the
   galvanic series in seawater, ASTM G82, https://www.astm.org/g0082-98r21.html: Cu about -0.30 V, 90-10 about
   -0.25 V, 70-30 about -0.20 V vs SCE); dE0 = -60 mV and tau = 15 min (assumed).
2. *EIS at OCP*, 100 kHz to 10 mHz, 10 mV rms: a Randles circuit, R_u + 1/(Q (j w)^n + 1/(R_ct + Z_W)), with a
   constant-phase element (Brug et al. 1984, https://doi.org/10.1016/S0022-0728(84)80225-5) and a finite-length
   Warburg Z_W = R_W tanh(sqrt(j w tau_W))/sqrt(j w tau_W) for O2 and CuCl2- diffusion (Orazem & Tribollet,
   *Electrochemical Impedance Spectroscopy*, Wiley 2008). R_ct + R_W is the kinetic curve's own polarization
   resistance; the diffusion share (25 %), Q (40 uF s^(n-1)/cm^2), n (0.86) and tau_W (5 s) are assumed. Noise is
   0.3 % of |Z| plus the OCP drift's non-stationarity at low frequency. The spectrum is fitted for R_ct by complex
   non-linear least squares (modulus weighting), as ZView or Gamry Echem Analyst would.
3. *LPR*, +-10 mV about the OCP measured just before, at 0.167 mV/s (ASTM G59, https://www.astm.org/g0059-97r20.html):
   the current comes from a mixed-potential kinetic curve (anodic Cu -> CuCl2- Tafel slope about 60 mV/decade,
   Kear, Barker & Walsh, Corros. Sci. 46, 2004, https://doi.org/10.1016/S0010-938X(02)00257-3; an O2-reduction
   cathode with a limiting current, 25 uA/cm^2 for a quiescent 4 mm deep well, assumed), solved at every point with
   the uncompensated resistance R_u (60 Ohm in ASW, DAL's well number; scaled by conductivity) in series, plus the
   double-layer charging current, the OCP drift during the scan and the potentiostat's current noise. R_p is the
   slope of E against i; so an uncompensated R_u and an OCP still drifting in the scan direction both read high.
4. *Cyclic polarization* (ASTM G61, https://www.astm.org/g0061-86r18.html, at 1 mV/s for the screen instead of
   G61's 0.167, and reversed at 1 mA/cm^2 instead of 5 to spare the spot's ICP tube; both assumed): the anodic branch
   is the active Tafel line capped by a film-limited plateau (falling with Ni and Al, rising with beta'; assumed) and
   a breakdown above E_b (the truth's Eb_mV, +40 mV per decade of scan rate above G61's, -400 mV per unit porosity,
   25 mV spot-to-spot scatter, and an 8 % chance of crevice attack under the O-ring 100 mV lower: all assumed). The
   reverse scan carries the sites that broke down, so it closes on the forward curve at E_rp = E_b minus a hysteresis
   that grows with beta', the selective attack and porosity (assumed). Analysis: a Butler-Volmer fit of the forward
   scan within -100..+30 mV of E_corr gives the Tafel slopes and Stern-Geary's B = ba bc / (2.303 (ba + bc))
   (Stern & Geary, J. Electrochem. Soc. 104, 1957, https://doi.org/10.1149/1.2428496); E_b is where the forward
   current first reaches 100 uA/cm^2 (a common lab rule, assumed), E_rp where the reverse scan crosses the forward.
5. i_corr = B / R_p and the early rate by Faraday's law, CR = 3.27 i_corr EW / rho (ASTM G102,
   https://www.astm.org/g0102-89r15e01.html), with EW = 1/sum(n_i f_i / M_i) and rho from the *designed*
   composition, as a lab does (Cu, Ni, Fe, Mn as 2+, Al and Cr 3+, Si and Ti 4+, Nb 5+).

Nuisances: room temperature 22 +- 1 degC (Arrhenius, 20 kJ/mol for a diffusion-dominated early rate, assumed),
dissolved O2 +- 8 % in a 150 uL well (rate ~ DO^0.6, assumed), the wetted area +- 4 % (O-ring seating) and larger by
1.5 x porosity where pores open to the surface (assumed), 18 % spot-to-spot scatter of i_corr on a 3 mm spot of a
DED deposit (assumed).

**Immersion** (``measure_immersion``; ASTM G31, https://www.astm.org/g0031-21.html, 30 days in 200 mL of ASTM D1141
substitute ocean water, quiescent, 22 degC): a 20 x 10 x 3 mm coupon (assumed). The rate decays as the film matures,
r(t) = r_inf + (r_1h - r_inf) exp(-t / film_days), from the truth's early to its long-term rate, so the 30-day mean
is r_inf + (r_1h - r_inf) (tau/30)(1 - exp(-30/tau)) (the campaign's stand-in used r_inf (1 + 1.5 exp(-30/tau))).

* *Mass loss* (ASTM G1, https://www.astm.org/g0001-03r17e01.html): 45 % of the corroded metal stays on the coupon as
  Cu2O / Cu2(OH)3Cl (1.4 g per g of metal, assumed); each acid cleaning cycle removes 80 % of what product is left and
  0.04 mg of base metal (assumed); six cycles weighed on a 0.1 mg balance (0.05 mg repeatability); the G1 graphical
  method extrapolates cycles 3-6 back to zero. Rate = 8.76e7 W / (A T rho), with calipered dimensions.
* *Selective attack* (SEM cross-section): attack sites (beta' and kappa islands, 20 per mm, assumed) with
  exponential depths whose expected maximum over 10 mm of section is the truth's attack_um; the lab images 10 fields
  of 250 um (2.5 mm) and reports the deepest (ASTM G46, https://www.astm.org/g0046-21.html), so it under-reads by
  about a fifth and scatters like a Gumbel maximum (Shibata, Corrosion 52, 1996, https://doi.org/10.5006/1.3292074).
  Depths under 0.5 um are hidden by edge rounding; surface pores cut by the section are mistaken for attack with
  probability 0.05 (gas or keyhole pores, round) or 0.1 (lack of fusion, irregular) (assumed); below 0.05 um of
  true attack there are no attack sites to find.
* *ICP-MS* of four 10 mL draws (days 1, 7, 14, 30): dissolved metal is what the film does not keep (Cu 55 %, Ni 35 %
  since the film is Ni-enriched, assumed), less 10 % lost to the walls and precipitate (assumed); 50 x dilution in
  2 % HNO3, matrix-matched calibration (3 % RSD), the salts' blank (Cu 1.5 +- 0.5, Ni 0.3 +- 0.2 ppb, assumed)
  subtracted, LOD 3 sd of the blank. Reported: the day-30 draw (ppb = ug/L), absent below the LOD.

**Fast fidelity.** Closed-form references carry the deterministic physics (the kinetic curve's R_p and B, the wetted
area, R_u, the scan-rate offset and the 100 uA/cm^2 criterion applied to the noise-free curve, the hysteresis, the
film-kinetics 30-day rate, the dissolved metal); the residuals of the lite chain against them (log ratios for R_p, B,
R_ct, the 30-day rate and the ICP concentrations; mV differences for OCP, E_b and E_rp) are a multivariate normal
whose mean is linear in a few state features (log early rate, porosity, beta', Ni, Al) for the log quantities and a
constant for the potentials, fitted by Huber-robust least squares, with a pooled covariance (so R_p and R_ct, or E_b
and E_rp, stay correlated as in the chain); ``calibrate()`` fits them and ``calibrate_mech.py`` stores them in
``calib_mech.json``. The crevice events and the
SEM's extreme-value sampling are drawn the same way as in the lite chain. A screen with a non-default protocol
(``ocp_min``, scan rate, electrolyte, IR compensation) has no calibration, so fast mode runs the lite chain for it.

Limits: the kinetics are seawater's whatever the electrolyte (the dilute NaCl stocks only change R_u); no galvanic
coupling to the substrate, no flow, no sulfide; the film is a time constant, not a growing layer; the SEM sampling
assumes the attack sites are independent; the ICP model ignores Cu re-deposition.
"""
from __future__ import annotations

import math

import numpy as np

from twin.physics import density as _alloy_density

# ----------------------------------------------------------------------------------------------- constants
AREA_CM2 = 0.071             # O-ring well, nominal wetted area
T_NOM_C = 22.0               # lab temperature (assumed)
RU_ASW_OHM = 60.0            # uncompensated resistance of the well in ASW (DAL's Randles number for the cell)
K_G102 = 3.27                # CR [um/yr] = K i [uA/cm2] EW / rho [g/cm3]  (ASTM G102)
K_G1 = 8.76e7                # CR [um/yr] = K W [g] / (A [cm2] T [h] rho)  (ASTM G1)
EA_J = 20e3                  # J/mol, temperature dependence of the rate (assumed)
R_GAS = 8.314462618
VALENCE = dict(Cu=2, Ni=2, Fe=2, Mn=2, Al=3, Cr=3, Si=4, Nb=5, Ti=4)
MOLAR = dict(Cu=63.546, Ni=58.693, Fe=55.845, Mn=54.938, Al=26.982, Cr=51.996, Si=28.086, Nb=92.906, Ti=47.867)
KAPPA_REL = {"asw": 1.0, "nacl_0.6": 1.02, "nacl_0.06": 0.12, "nacl_0.006": 0.013}   # conductivity vs ASW
DEFAULT_SCREEN = dict(ocp_min=60.0, eis=True, cp=True, cp_rate_mV_s=1.0, electrolyte="asw", ir_comp=0.0)
DEFAULT_IMM = dict(days=30.0, fields=10)
I_THR = 100.0                # uA/cm2, breakdown criterion (assumed lab rule)
I_REV = 1000.0               # uA/cm2, reversal current (assumed; G61 uses 5 mA/cm2)
E_MAX = 1200.0               # mV vs Ag/AgCl, the scan's upper limit
B_DEFAULT = 22.0             # mV, Stern-Geary B used on a spot without a CP (assumed, ba 65 / bc 200 mV/dec)
P_CREVICE = 0.08             # crevice attack under the O-ring during the CP (assumed)
SIG_RW = 0.03                # mV/sqrt(s), OCP random walk (assumed)
F_FILM = 0.5                 # reverse-scan current below E_rp relative to forward (film thickened; assumed)
# immersion
COUPON_MM = (20.0, 10.0, 3.0)
V_SOL_L, DRAW_L, DRAW_DAYS, DF = 0.200, 0.010, (1.0, 7.0, 14.0, 30.0), 50.0
RETAIN = dict(Cu=0.45, Ni=0.65, Fe=0.8, Mn=0.3, Al=0.85, Cr=0.8, Si=0.9, Nb=0.9, Ti=0.9)   # kept by the film
BLANK = dict(Cu=(1.5, 0.5), Ni=(0.3, 0.2))     # ppb in the ASW, mean and sd (assumed)
INST_SD = 0.005 * DF         # ppb in the sample, the instrument's noise at the diluted level (assumed)
LOD = {e: 3.0 * math.hypot(s, INST_SD) for e, (m, s) in BLANK.items()}
SITES_PER_MM, FIELD_MM, L_REF_MM, SEM_LOD_UM = 20.0, 0.25, 10.0, 0.5
PORE_D_MM = dict(gas=0.02, keyhole=0.04, lof=0.06)
PORE_MIS = dict(gas=0.05, keyhole=0.05, lof=0.10)

SPEC = dict(
    screen=dict(station="cubxl", hours=1.6, note="OCP 60 min, EIS 10 min, LPR 2 min, rest 5 min, CP about 15 min, "
                "handling 5 min (the campaign books 1.2 h for the protocol's 20 min OCP)",
                consumables=dict(p20_tips=3, asw_mL=0.3, hno3_1M_uL=20, tube_0p5mL=1, oring_as568_006=1,
                                 sic_paper=2),
                usd_assumed=dict(p20_tips=0.10, asw_mL=0.06, tube_0p5mL=0.05, oring_as568_006=0.50, sic_paper=1.0)),
    immersion=dict(station="immersion", hours=720.0, note="30 days in 200 mL ASW; then G1 cleaning (0.5 h), "
                   "an SEM cross-section (1 h) and four ICP-MS draws",
                   consumables=dict(asw_mL=200, pp_bottle_250mL=1, coupon_machining=1, sem_mount=1, icpms_draws=4),
                   usd_assumed=dict(asw_mL=0.06, pp_bottle_250mL=3.0, coupon_machining=40.0, sem_mount=15.0)),
)


def _calib(name):
    try:
        from twin.instruments.mech import calib
        return calib(name) or {}
    except Exception:          # mech.py missing or mid-edit: run on the defaults
        return {}


# ----------------------------------------------------------------------------------------------- material state
def equivalent_weight(comp: dict) -> float:
    """ASTM G102 equivalent weight, g per equivalent: 1 / sum(n_i f_i / M_i) over the elements present."""
    s = sum(VALENCE[e] * w / 100.0 / MOLAR[e] for e, w in comp.items() if e in VALENCE and w > 0)
    return 1.0 / s if s > 0 else MOLAR["Cu"] / 2


def _rho(comp: dict) -> float:
    return _alloy_density({e: w for e, w in comp.items() if w > 0 and e in MOLAR})


def _base(sample: dict) -> dict:
    """The deposit's nominal electrochemistry at the lab's conditions (no spot-to-spot or nuisance variation)."""
    c, comp = sample["corrosion"], sample["composition"]
    ni, al, fe = comp.get("Ni", 0.0), comp.get("Al", 0.0), comp.get("Fe", 0.0)
    fe_ss = min(fe, 2.3 + 0.3 * al)
    por = float(sample.get("porosity", 0.0))
    bp = float(sample.get("beta_prime", 0.0))
    ew, rho = equivalent_weight(comp), _rho(comp)
    icorr = max(c["early_rate_um_yr"], 1e-3) * rho / (K_G102 * ew)                 # uA/cm2 at one hour
    return dict(icorr=icorr, ba=58.0 * (1 + 0.008 * ni + 0.02 * al), bc=150.0 * (1 + 0.005 * ni), iL=25.0,
                ipass=40.0 / (1 + ni / 10.0) / (1 + al / 5.0) * (1 + 5 * bp),
                E_inf=-300.0 + 4.4 * ni + 5.0 * min(al, 10.0) + 8.0 * fe_ss - 50.0 * bp, dE0=-60.0, tau_min=15.0,
                Eb=float(c["Eb_mV"]), dEh=80.0 + 250.0 * bp + 4.0 * min(c.get("attack_um", 0.0), 40.0)
                + 300.0 * min(por, 0.2), w=0.25, Q=40e-6, n=0.86 - 0.1 * bp, tau_w=5.0, por=por, bp=bp, ni=ni,
                al=al, ew=ew, rho=rho)


def _kin(icorr, ba, bc, iL, ipass, Ecorr, Eb, sbd=15.0):
    iL, ipass = max(iL, 2.5 * icorr), max(ipass, 3.0 * icorr)
    return dict(ia0=1.0 / (1.0 / icorr - 1.0 / ipass), ic0=icorr / (1.0 - icorr / iL), ba=ba, bc=bc, iL=iL,
                ipass=ipass, Ecorr=Ecorr, Eb=Eb, sbd=sbd)


def _anodic(E, k):
    """Anodic current density (uA/cm2, true area) at interface potential E (mV): active Tafel line in series with
    the film-limited plateau, plus the breakdown term."""
    ia = k["ia0"] * np.power(10.0, np.clip((E - k["Ecorr"]) / k["ba"], -40, 40))
    return 1.0 / (1.0 / ia + 1.0 / k["ipass"]) + k["ipass"] * np.exp(np.clip((E - k["Eb"]) / k["sbd"], -80, 80))


def _cathodic(E, k):
    ic = k["ic0"] * np.power(10.0, np.clip(-(E - k["Ecorr"]) / k["bc"], -40, 40))
    return ic / (1.0 + ic / k["iL"])


def _rp_kin(k):
    """Polarization resistance of the kinetic curve at E_corr, Ohm cm2 (true area)."""
    d = 0.05
    E = np.array([k["Ecorr"] - d, k["Ecorr"] + d])
    i = _anodic(E, k) - _cathodic(E, k)
    return 1000.0 * 2 * d / (i[1] - i[0])


def _eb_nominal(b: dict, shift: float = 0.0):
    """Breakdown seen by the CP's criterion on the noise-free curve: (E_b of the kinetics, the potential where the
    forward current reaches I_THR on the nominal area, E_rp of the kinetics), mV."""
    a_rel = 1 + 1.5 * min(b["por"], 0.3)
    Eb_k = max(b["Eb"] + 40.0 * math.log10(DEFAULT_SCREEN["cp_rate_mV_s"] / 0.1667) - 400.0 * min(b["por"], 0.2)
               + shift, b["E_inf"] + 60.0)
    k = _kin(b["icorr"], b["ba"], b["bc"], b["iL"], b["ipass"], b["E_inf"], Eb_k)
    E = np.arange(b["E_inf"] + 30.0, E_MAX, 2.0)
    i = (_anodic(E, k) - _cathodic(E, k)) * a_rel
    up = np.nonzero(i >= I_THR)[0]
    if up.size and up[0] > 0:
        j = int(up[0])
        l0, l1 = math.log10(max(i[j - 1], 1e-9)), math.log10(i[j])
        Eb_m = float(E[j - 1] + 2.0 * (2.0 - l0) / max(l1 - l0, 1e-9))
    else:
        Eb_m = Eb_k
    return Eb_k, Eb_m, max(Eb_k - b["dEh"], b["E_inf"] + 20.0), k


def _refs(sample: dict, b: dict) -> dict:
    """What the screen would read without noise or analysis error, from the hidden state at nominal conditions (the
    wetted area included); the fast mode adds the calibrated residuals to these."""
    a_rel = 1 + 1.5 * min(b["por"], 0.3)
    Eb_k, Eb_m, Erp, k = _eb_nominal(b)
    rp = _rp_kin(k)
    return dict(rp=rp, B=b["icorr"] * rp / 1000.0, rp_m=rp / a_rel + RU_ASW_OHM * AREA_CM2,
                rct=(1 - b["w"]) * rp / a_rel,
                ocp=b["E_inf"] + b["dE0"] * math.exp(-DEFAULT_SCREEN["ocp_min"] / b["tau_min"]), Eb=Eb_m, Erp=Erp,
                Eb_true=b["Eb"])


def _feat_screen(sample, b):
    return np.array([math.log(max(sample["corrosion"]["early_rate_um_yr"], 1e-3) / 20.0), b["por"], b["bp"],
                     b["ni"] / 30.0, b["al"] / 10.0])


def _arr(T):
    return math.exp(-EA_J / R_GAS * (1.0 / (T + 273.15) - 1.0 / (T_NOM_C + 273.15)))


# ----------------------------------------------------------------------------------------------- electrochemistry
def _solve(Eapp, fn, ru_area):
    """Interface potential E (mV) with E + i(E) R_u A / 1000 = E_app: Newton from E_app (the IR drop is small in
    seawater), with bisection (h is monotone in E) wherever Newton has not converged."""
    Eapp = np.asarray(Eapp, float)
    g = ru_area * 1e-3
    E = Eapp.copy()
    if g < 0.05:
        for _ in range(5):
            i = fn(E)
            h = E + i * g - Eapp
            d = 1.0 + (fn(E + 0.01) - i) / 0.01 * g
            E = E - h / np.maximum(d, 1.0)
        i = fn(E)
        if np.all(np.abs(E + i * g - Eapp) < 1e-6):
            return E, i
    lo, hi = Eapp - 3000.0, Eapp + 300.0
    for _ in range(36):
        mid = 0.5 * (lo + hi)
        pos = mid + fn(mid) * g - Eapp > 0
        hi = np.where(pos, mid, hi)
        lo = np.where(pos, lo, mid)
    E = 0.5 * (lo + hi)
    return E, fn(E)


def _randles(f, Rs, Q, n, Rct, Rw, tw):
    jw = 2j * np.pi * f
    s = np.sqrt(jw * tw)
    th = np.tanh(np.minimum(s.real, 20.0) + 1j * s.imag)
    zw = Rw * th / s
    return Rs + 1.0 / (Q * jw ** n + 1.0 / (Rct + zw))


def _fit_eis(f, Z):
    """Complex non-linear least squares of the Randles + CPE + finite Warburg circuit (modulus weighting), with the
    analytic Jacobian."""
    from scipy.optimize import least_squares
    Rs0 = max(Z.real[0], 1e-3)
    Rlow = max(Z.real[-1] - Rs0, 1.0)
    mid = f > 0.05
    fstar = f[mid][np.argmax(-Z.imag[mid])] if mid.any() else 1.0
    n0 = 0.85
    Q0 = 1.0 / (0.75 * Rlow * (2 * np.pi * fstar) ** n0)
    p0 = np.array([math.log(Rs0), math.log(Q0), 0.847, math.log(0.75 * Rlow), math.log(0.25 * Rlow), math.log(3.0)])
    mag = np.abs(Z)
    jw = 2j * np.pi * f
    ljw = np.log(jw)

    def unpack(p):
        return (math.exp(p[0]), math.exp(p[1]), 0.5 + 0.5 / (1 + math.exp(-p[2])), math.exp(p[3]), math.exp(p[4]),
                math.exp(min(p[5], 12.0)))

    def parts(p):
        Rs, Q, n, Rct, Rw, tw = unpack(p)
        s_ = np.sqrt(jw * tw)
        th = np.tanh(np.minimum(s_.real, 20.0) + 1j * s_.imag)
        zw = Rw * th / s_
        cpe = Q * np.exp(n * ljw)
        Y = cpe + 1.0 / (Rct + zw)
        return Rs, Q, n, Rct, Rw, tw, s_, th, zw, cpe, Y

    def res(p):
        Rs, Q, n, Rct, Rw, tw, s_, th, zw, cpe, Y = parts(p)
        d = (Rs + 1.0 / Y - Z) / mag
        return np.concatenate([d.real, d.imag])

    def jac(p):
        Rs, Q, n, Rct, Rw, tw, s_, th, zw, cpe, Y = parts(p)
        dZdY = -1.0 / Y ** 2
        dYdR = -1.0 / (Rct + zw) ** 2
        sig = 1.0 / (1 + math.exp(-p[2]))
        cols = [np.full(f.size, Rs, complex), dZdY * cpe, dZdY * cpe * ljw * 0.5 * sig * (1 - sig),
                dZdY * dYdR * Rct, dZdY * dYdR * zw,
                dZdY * dYdR * Rw * ((1 - th ** 2) * s_ - th) / (2 * s_) * (1.0 if p[5] < 12.0 else 0.0)]
        J = np.array(cols).T / mag[:, None]
        return np.vstack([J.real, J.imag])

    try:
        p = least_squares(res, p0, jac=jac, method="lm", xtol=1e-9, max_nfev=400).x
    except Exception:
        p = p0
    Rs, Q, n, Rct, Rw, tw = unpack(p)
    return dict(Rs=Rs, Q=Q, n=n, Rct=Rct, Rw=Rw, tau_w=tw)


def _fit_tafel(E, i, Eoc):
    """Butler-Volmer fit, i = i_corr (10^((E-Ec)/ba) - 10^(-(E-Ec)/bc)), within -100..+30 mV of E_corr, on an asinh
    scale (log-like away from E_corr, linear through zero), with the analytic Jacobian."""
    from scipy.optimize import least_squares
    m = (E - Eoc >= -100.0) & (E - Eoc <= 30.0)
    Ew, iw = E[m], i[m]
    if len(Ew) < 6:
        return None
    s = 0.05
    L10 = math.log(10.0)

    def terms(p):
        ic, ba, bc = math.exp(p[0]), math.exp(p[2]), math.exp(p[3])
        x = Ew - p[1]
        P = np.power(10.0, np.clip(x / ba, -40, 40))
        N = np.power(10.0, np.clip(-x / bc, -40, 40))
        return ic, ba, bc, x, P, N, ic * (P - N)

    def res(p):
        return np.arcsinh(terms(p)[-1] / s) - np.arcsinh(iw / s)

    def jac(p):
        ic, ba, bc, x, P, N, mdl = terms(p)
        w = 1.0 / (s * np.sqrt(1.0 + (mdl / s) ** 2))
        return np.column_stack([mdl, -ic * L10 * (P / ba + N / bc), -ic * P * L10 * x / ba,
                                -ic * N * L10 * x / bc]) * w[:, None]

    ig = max(float(np.median(np.abs(iw))) * 0.3, 1e-3)
    try:
        sol = least_squares(res, [math.log(ig), Eoc, math.log(60.0), math.log(150.0)], jac=jac, method="lm",
                            max_nfev=300)
        ic, Ec, ba, bc = math.exp(sol.x[0]), sol.x[1], math.exp(sol.x[2]), math.exp(sol.x[3])
    except Exception:
        return None
    if not (15.0 <= ba <= 400.0 and 15.0 <= bc <= 600.0):
        return None
    return dict(icorr=ic, Ecorr=Ec, ba=ba, bc=bc, B=ba * bc / (2.303 * (ba + bc)))


def _screen_chain(sample, rng, fid, opt):
    """The screen as the CubXL runs it: returns (measured values, info for calibration and figures)."""
    b = _base(sample)
    full = fid == "full"
    design = sample.get("design") or sample["composition"]
    ew_lab, rho_lab = equivalent_weight(design), _rho(design)
    # the spot and the day
    T = T_NOM_C + rng.normal(0, 1.0)
    do = math.exp(rng.normal(0, 0.08))
    icorr = b["icorr"] * math.exp(rng.normal(0, 0.18)) * _arr(T) * do ** 0.6
    tf = (T + 273.15) / (T_NOM_C + 273.15)
    ba = b["ba"] * tf * math.exp(rng.normal(0, 0.05))
    bc = b["bc"] * tf * math.exp(rng.normal(0, 0.05))
    iL = b["iL"] * do * (1 + 0.02 * (T - T_NOM_C)) * math.exp(rng.normal(0, 0.1))
    ipass = b["ipass"] * math.exp(rng.normal(0, 0.15))
    a_rel = math.exp(rng.normal(0, 0.04)) * (1 + 1.5 * min(b["por"], 0.3))
    kappa = KAPPA_REL[opt["electrolyte"]] * (1 + 0.02 * (T - 25.0))
    ru = RU_ASW_OHM / kappa * math.exp(rng.normal(0, 0.05))
    ru_area = ru * AREA_CM2 * a_rel * (1.0 - opt["ir_comp"])
    E_inf = b["E_inf"] + rng.normal(0, 8.0)
    dE0 = b["dE0"] * math.exp(rng.normal(0, 0.3))
    tau_s = b["tau_min"] * 60.0 * math.exp(rng.normal(0, 0.3))
    crev = rng.random() < P_CREVICE
    shift = -abs(rng.normal(100.0, 30.0)) if crev else 0.0
    Eb_eff = b["Eb"] + 40.0 * math.log10(opt["cp_rate_mV_s"] / 0.1667) - 400.0 * min(b["por"], 0.2) \
        + rng.normal(0, 25.0) + shift
    dEh = b["dEh"] * math.exp(rng.normal(0, 0.15))
    w = float(np.clip(b["w"] * math.exp(rng.normal(0, 0.15)), 0.05, 0.6))
    Q = b["Q"] * math.exp(rng.normal(0, 0.1))
    n = float(np.clip(b["n"] + rng.normal(0, 0.02), 0.6, 0.98))
    tw = b["tau_w"] * math.exp(rng.normal(0, 0.3))
    c_dl = Q * 1e6                                    # uF/cm2, for the charging current (approximately)

    def ecorr(t):
        return E_inf + dE0 * np.exp(-np.asarray(t, float) / tau_s) + rw_end

    def drift(t):                                     # mV/s
        return -dE0 / tau_s * math.exp(-t / tau_s)

    def i_noise(i):
        return rng.normal(0, 1, np.shape(i)) * (0.002 * np.abs(i) + 0.003)

    # 1. OCP
    dt = 1.0 if full else 30.0
    n_ocp = int(round(opt["ocp_min"] * 60.0 / dt))
    t = np.arange(1, n_ocp + 1) * dt
    rw = np.cumsum(rng.normal(0, SIG_RW * math.sqrt(dt), n_ocp))
    rw_end = float(rw[-1])
    E_ocp = E_inf + dE0 * np.exp(-t / tau_s) + rw + rng.normal(0, 0.15, n_ocp)
    ocp = float(np.mean(E_ocp[-max(int(round(120.0 / dt)), 1):]))
    t_now = float(t[-1])
    out = dict(ocp_mV=ocp)
    info = dict(crevice=crev, crevice_shift=shift, T_C=T, DO_rel=do, area_rel=a_rel, Ru_ohm=ru,
                Eb_eff=Eb_eff, icorr_true=icorr)
    raw = dict(ocp_t_s=t, ocp_E_mV=E_ocp) if full else {}
    # 2. EIS at OCP
    if opt["eis"]:
        te = t_now + 300.0
        Ec = float(ecorr(te))
        k = _kin(icorr, ba, bc, iL, ipass, Ec, max(Eb_eff, Ec + 60.0))
        rp_t = _rp_kin(k)
        f = np.logspace(5, -2, 71 if full else 29)
        Z = ru * AREA_CM2 + _randles(f, 0.0, Q, n, (1 - w) * rp_t, w * rp_t, tw) / a_rel
        sig = 0.003 + 0.1 * abs(drift(te)) / (f * 14.1)
        Z = Z * (1 + rng.normal(0, 1, f.size) * sig + 1j * rng.normal(0, 1, f.size) * sig)
        fit = _fit_eis(f, Z)
        out["rct_ohm_cm2"] = fit["Rct"]
        info.update(rct_true=(1 - w) * rp_t / a_rel)
        if full:
            zf = _randles(f, fit["Rs"], fit["Q"], fit["n"], fit["Rct"], fit["Rw"], fit["tau_w"])
            raw.update(eis_f_Hz=f, eis_Zre=Z.real, eis_Zim=Z.imag, eis_fit=fit, eis_fit_Zre=zf.real,
                       eis_fit_Zim=zf.imag)
        t_now += 600.0
    # 3. LPR (ASTM G59), the OCP re-read for 10 s first
    t_now += 10.0
    rate = 0.1667
    Eoc = float(ecorr(t_now)) + rng.normal(0, 0.05)
    Eapp = Eoc + np.linspace(-10.0, 10.0, 201 if full else 21)
    tt = t_now + (Eapp - Eapp[0]) / rate
    k = _kin(icorr, ba, bc, iL, ipass, ecorr(tt), max(Eb_eff, float(ecorr(t_now)) + 60.0))
    _, i_far = _solve(Eapp, lambda E: _anodic(E, k) - _cathodic(E, k), ru_area)
    i_m = (i_far + c_dl * rate * 1e-3) * a_rel
    i_m = i_m + i_noise(i_m)
    slope, icpt = np.polyfit(i_m, Eapp, 1)
    rp = float(slope) * 1000.0
    info.update(rp_true=_rp_kin(_kin(icorr, ba, bc, iL, ipass, Eoc, max(Eb_eff, Eoc + 60.0))))
    if full:
        raw.update(lpr_E_mV=Eapp, lpr_i_uA_cm2=i_m, lpr_fit=dict(slope_mV_per_uA_cm2=float(slope),
                                                                 intercept_mV=float(icpt)), lpr_Eoc_mV=Eoc)
    t_now = float(tt[-1]) + 300.0
    # 4. cyclic polarization (ASTM G61 shape), last on the spot
    B, taf = B_DEFAULT, None
    if opt["cp"]:
        t_now += 10.0
        Ec0 = float(ecorr(t_now))
        Eoc2 = Ec0 + rng.normal(0, 0.05)
        Eb_k = max(Eb_eff, Ec0 + 60.0)
        r_cp = opt["cp_rate_mV_s"]
        step = 1.0 if full else 5.0
        # the forward scan, computed up to a little past where it should reverse (all of it if it does not)
        E_top = min(Eb_k + 15.0 * math.log(4 * I_REV / max(ipass, 1e-3)) + 4 * I_REV * ru_area * 1e-3 + 40.0, E_MAX)
        for E_end in (E_top, E_MAX):
            Ef = np.arange(Eoc2 - 150.0, E_end + step / 2, step)
            tf_ = t_now + (Ef - Ef[0]) / r_cp
            kf = _kin(icorr, ba, bc, iL, ipass, ecorr(tf_), Eb_k)
            Etrue_f, i_f = _solve(Ef, lambda E: _anodic(E, kf) - _cathodic(E, kf), ru_area)
            if i_f[-1] * a_rel >= 1.2 * I_REV or E_end >= E_MAX:
                break
        i_fm = (i_f + c_dl * r_cp * 1e-3) * a_rel
        i_fm = i_fm + i_noise(i_fm)
        hit = np.nonzero(i_fm >= I_REV)[0]
        j_ap = int(hit[0]) if hit.size else len(Ef) - 1
        Ef, i_fm, Etrue_f, tf_ = Ef[:j_ap + 1], i_fm[:j_ap + 1], Etrue_f[:j_ap + 1], tf_[:j_ap + 1]
        E_ap, t_ap = float(Etrue_f[-1]), float(tf_[-1])
        k_ap = _kin(icorr, ba, bc, iL, ipass, float(ecorr(t_ap)), Eb_k)
        Erp_t = min(max(Eb_k - dEh, Ec0 + 20.0), E_ap - 20.0)
        A_ap, A_rp = float(_anodic(np.array(E_ap), k_ap)), float(_anodic(np.array(Erp_t), k_ap))
        s_r = (E_ap - Erp_t) / math.log(max(A_ap / max(A_rp, 1e-12), 1.0001))
        P0 = (1 - F_FILM) * A_ap
        Er = np.arange(Ef[-1], Eoc2 - 50.0 - step / 2, -step)
        tr = t_ap + (Ef[-1] - Er) / r_cp
        kr = _kin(icorr, ba, bc, iL, ipass, ecorr(tr), Eb_k)

        def i_rev(E):
            return F_FILM * _anodic(E, kr) + P0 * np.exp(np.clip((E - E_ap) / s_r, -80, 5)) - _cathodic(E, kr)

        _, i_r = _solve(Er, i_rev, ru_area)
        i_rm = (i_r - c_dl * r_cp * 1e-3) * a_rel
        i_rm = i_rm + i_noise(i_rm)
        # analysis: Tafel fit -> B; E_b at 100 uA/cm2; E_rp where the loop closes
        taf = _fit_tafel(Ef, i_fm, Eoc2)
        if taf is not None:
            B = float(np.clip(taf["B"], 5.0, 80.0))
        up = np.nonzero((Ef > Eoc2 + 30.0) & (i_fm >= I_THR))[0]
        if up.size and up[0] > 0:
            j = int(up[0])
            l0, l1 = math.log10(max(i_fm[j - 1], 1e-6)), math.log10(i_fm[j])
            out["Eb_mV"] = float(Ef[j - 1] + (Ef[j] - Ef[j - 1]) * (2.0 - l0) / max(l1 - l0, 1e-9))
        i_fi = np.interp(Er, Ef, i_fm)
        d = i_rm - i_fi
        pos = np.nonzero(d > 0.05 * np.abs(i_fi))[0]
        if pos.size:
            neg = np.nonzero((np.arange(d.size) > pos[0]) & (d < 0))[0]
            if neg.size:
                j = int(neg[0])
                out["Erp_mV"] = float(Er[j - 1] + (Er[j] - Er[j - 1]) * d[j - 1] / (d[j - 1] - d[j]))
        info.update(Erp_true=Erp_t, E_apex=E_ap)
        if full:
            raw.update(cp_E_mV=np.concatenate([Ef, Er]), cp_i_uA_cm2=np.concatenate([i_fm, i_rm]),
                       cp_dir=np.concatenate([np.ones(Ef.size), -np.ones(Er.size)]), cp_Eoc_mV=Eoc2, tafel=taf,
                       cp_rate_mV_s=r_cp, i_thr_uA_cm2=I_THR)
    icorr_m = B / rp * 1000.0
    out.update(rp_ohm_cm2=rp, icorr_uA_cm2=icorr_m, early_rate_um_yr=K_G102 * icorr_m * ew_lab / rho_lab)
    info.update(B=B, tafel=taf)
    if full:
        raw.update(B_mV=B, EW=ew_lab, rho=rho_lab, area_cm2=AREA_CM2, conditions=dict(T_C=T, DO_rel=do, Ru_ohm=ru,
                                                                                         crevice=bool(crev)))
        out["raw"] = raw
    return out, info


# ----------------------------------------------------------------------------------------------- immersion
def _r30(r_inf, r0, tau_d, days):
    return r_inf + (r0 - r_inf) * tau_d / days * (1.0 - math.exp(-days / tau_d))


def _mass_loss_g(r_inf, r0, tau_d, rho, area, days):
    th, tau_h = days * 24.0, tau_d * 24.0
    return rho * area / K_G1 * (r_inf * th + (r0 - r_inf) * tau_h * (1.0 - math.exp(-th / tau_h)))


def _icp(Wfun, comp, f_ads):
    """True concentration (ppb) of Cu and Ni in each draw, given the corroded mass W(t_days) in g."""
    out = {e: [] for e in ("Cu", "Ni")}
    for e in out:
        removed = 0.0
        for kk, day in enumerate(DRAW_DAYS):
            m_ug = Wfun(day) * 1e6 * comp.get(e, 0.0) / 100.0 * (1 - RETAIN[e]) * (1 - f_ads)
            V = V_SOL_L - DRAW_L * kk
            C = max(m_ug - removed, 0.0) / V
            out[e].append(C)
            removed += C * DRAW_L
    return out


def _imm_refs(sample):
    c, comp = sample["corrosion"], sample["composition"]
    rho = _rho(comp)
    L, W_, H = COUPON_MM
    A = 2 * (L * W_ + L * H + W_ * H) / 100.0
    days = DEFAULT_IMM["days"]
    Wf = lambda d: _mass_loss_g(c["rate_um_yr"], c["early_rate_um_yr"], c["film_days"], rho, A, d)
    conc = _icp(Wf, comp, 0.0)
    return dict(r30=_r30(c["rate_um_yr"], c["early_rate_um_yr"], c["film_days"], days), cu=conc["Cu"][-1],
                ni=conc["Ni"][-1], W=Wf(days))


def _feat_imm(sample):
    r = _imm_refs(sample)
    return np.array([math.log(max(r["r30"], 1e-3) / 10.0), float(sample.get("porosity", 0.0)),
                     float(sample.get("beta_prime", 0.0)), sample["composition"].get("Ni", 0.0) / 30.0])


def _attack_scale(attack):
    return attack / (math.log(SITES_PER_MM * L_REF_MM) + 0.5772)


def _pore_lambda(sample, length_mm):
    """Expected number of surface pores cut by the section edge and mistaken for attack, per type."""
    pores = sample.get("pores") or {}
    return {t: 1.5 * max(pores.get(t, 0.0), 0.0) / PORE_D_MM[t] * length_mm * PORE_MIS[t] for t in PORE_D_MM}


def _sem_attack(sample, rng, n_fields, full):
    """Attack depth per SEM field (um): selective attack sites plus mistaken surface pores; the deepest is reported."""
    attack = float(sample["corrosion"].get("attack_um", 0.0))
    m = _attack_scale(attack)
    fmax = np.zeros(n_fields)
    prof = None
    lam = _pore_lambda(sample, FIELD_MM)
    sites_all = []
    for j in range(n_fields):
        depths = []
        if attack > 0.05:
            ns = rng.poisson(SITES_PER_MM * FIELD_MM)
            if ns:
                d = rng.exponential(m, ns) + rng.normal(0, 0.2, ns)
                xs = rng.uniform(0, FIELD_MM * 1000, ns)
                depths.extend(np.round(d, 1).tolist())
                sites_all.append((j, xs, d))
        for t, lt in lam.items():
            npore = rng.poisson(lt)
            if npore:
                depths.extend((PORE_D_MM[t] * 1000 * rng.uniform(0.3, 1.0, npore)).tolist())
        vis = [x for x in depths if x >= SEM_LOD_UM]
        fmax[j] = max(vis) if vis else 0.0
    if full:
        jd = int(np.argmax(fmax))
        x = np.arange(0.0, FIELD_MM * 1000, 0.5)
        y = np.zeros_like(x)
        for (j, xs, ds) in sites_all:
            if j == jd:
                for x0, d0 in zip(xs, ds):
                    if d0 > 0:
                        wdt = 2.0 + 1.5 * d0
                        y = np.maximum(y, d0 * np.sqrt(np.clip(1 - ((x - x0) / wdt) ** 2, 0, None)))
        y = y + np.abs(rng.normal(0, 0.1, x.size))
        prof = (x, y)
    return fmax, prof


def _attack_fast(sample, rng, n_fields):
    """The same distribution as ``_sem_attack``, drawn in closed form: the maximum of N exponential depths."""
    attack = float(sample["corrosion"].get("attack_um", 0.0))
    best = 0.0
    if attack > 0.05:
        N = rng.poisson(SITES_PER_MM * FIELD_MM * n_fields)
        if N:
            d = -_attack_scale(attack) * math.log(max(1.0 - rng.random() ** (1.0 / N), 1e-300)) + rng.normal(0, 0.2)
            best = round(d, 1)
    for t, lt in _pore_lambda(sample, FIELD_MM * n_fields).items():
        npore = rng.poisson(lt)
        if npore:
            best = max(best, float(PORE_D_MM[t] * 1000 * rng.uniform(0.3, 1.0, npore).max()))
    return best if best >= SEM_LOD_UM else 0.0


def _imm_chain(sample, rng, fid, opt):
    c, comp = sample["corrosion"], sample["composition"]
    full = fid == "full"
    design = sample.get("design") or comp
    rho, rho_lab = _rho(comp), _rho(design)
    days = opt["days"]
    T = T_NOM_C + rng.normal(0, 0.7)
    fac = _arr(T) * math.exp(rng.normal(0, 0.05)) ** 0.6 * math.exp(rng.normal(0, 0.06))
    r_inf, r0 = c["rate_um_yr"] * fac, c["early_rate_um_yr"] * fac
    tau_d = c["film_days"] * math.exp(rng.normal(0, 0.1))
    dims = np.array(COUPON_MM) * np.exp(rng.normal(0, 0.005, 3))
    L, W_, H = dims
    A = 2 * (L * W_ + L * H + W_ * H) / 100.0
    m0 = rho * L * W_ * H / 1000.0 * (1 - min(float(sample.get("porosity", 0.0)), 0.4))
    Wfun = lambda d: _mass_loss_g(r_inf, r0, tau_d, rho, A, d)
    W = Wfun(days)
    bal = lambda m: np.round((np.asarray(m) + rng.normal(0, 0.05e-3, np.shape(m))) / 1e-4) * 1e-4
    m0_m = float(bal(m0))
    P = 0.45 * W * 1.4
    q = float(np.clip(0.8 * math.exp(rng.normal(0, 0.1)), 0.3, 0.95))
    cb = 0.04e-3 * A / 5.8 * math.exp(rng.normal(0, 0.2))
    kcyc = np.arange(0, 7)
    m_true = m0 - W + P * (1 - q) ** kcyc - kcyc * cb
    m_read = bal(m_true)
    sl, ic = np.polyfit(kcyc[3:], m_read[3:], 1)
    W_m = m0_m - float(ic)
    dims_m = np.round(dims + rng.normal(0, 0.01, 3), 2)
    A_m = 2 * (dims_m[0] * dims_m[1] + dims_m[0] * dims_m[2] + dims_m[1] * dims_m[2]) / 100.0
    out = dict(rate30_um_yr=K_G1 * W_m / (A_m * days * 24.0 * rho_lab))
    # SEM cross-section
    fmax, prof = _sem_attack(sample, rng, opt["fields"], full)
    out["attack_um"] = float(fmax.max())
    # ICP-MS
    f_ads = float(np.clip(0.1 * math.exp(rng.normal(0, 0.3)), 0.0, 0.5))
    conc = _icp(Wfun, comp, f_ads)
    meas = {}
    for e in ("Cu", "Ni"):
        bl = max(rng.normal(*BLANK[e]), 0.0)
        vals = [(Cv + bl) * math.exp(rng.normal(0, 0.01)) * math.exp(rng.normal(0, 0.03)) + rng.normal(0, INST_SD)
                - BLANK[e][0] for Cv in conc[e]]
        meas[e] = vals
        if vals[-1] >= LOD[e]:
            out[e.lower() + "_ppb"] = float(vals[-1])
    info = dict(W_true_g=W, fac=fac, f_ads=f_ads)
    if full:
        out["raw"] = dict(cycles=kcyc, mass_mg=m_read * 1e3, m0_mg=m0_m * 1e3, fit=dict(slope_mg=sl * 1e3,
                          intercept_mg=ic * 1e3), area_cm2=A_m, hours=days * 24.0, mass_loss_mg=W_m * 1e3,
                          sem_field_max_um=fmax, sem_profile_x_um=prof[0], sem_profile_depth_um=prof[1],
                          sem_lod_um=SEM_LOD_UM, icp_days=np.array(DRAW_DAYS), icp_cu_ppb=np.array(meas["Cu"]),
                          icp_ni_ppb=np.array(meas["Ni"]), lod_ppb=dict(LOD))
    return out, info


# ----------------------------------------------------------------------------------------------- fast mode
_SCREEN_KEYS = ["ln_rp", "ln_B", "ln_rct", "d_ocp_mV", "d_Eb_mV", "d_Erp_mV"]
_IMM_KEYS = ["ln_r30", "ln_cu", "ln_ni"]
# fallbacks before calibration: a copy of calibrate()'s fit on 2026-11-25 (63 parts x 4 lite runs)
_DEF_SCREEN = dict(coef=[[0.1269, -0.2839, 0.3036, 0.308, -0.248, -0.04751], [0.651, -0.7358, -0.2723, 1.108, -0.5832, -0.2022], [0.1144, -0.2652, 0.2645, 0.3139, -0.2382, -0.04816], [-0.6377, 0, 0, 0, 0, 0], [-0.3546, 0, 0, 0, 0, 0], [-0.1059, 0, 0, 0, 0, 0]],
                   cov=[[0.02574, -0.008334, 0.0251, -0.1847, 0.09623, -0.1516], [-0.008334, 0.01107, -0.007776, 0.1035, 0.4218, 0.4112], [0.0251, -0.007776, 0.02728, -0.1782, -0.00502, -0.2767], [-0.1847, 0.1035, -0.1782, 78.53, -6.424, -20.06], [0.09623, 0.4218, -0.00502, -6.424, 727.1, 648], [-0.1516, 0.4112, -0.2767, -20.06, 648, 1020]],
                   x_lo=[-0.459, 0.003, 0.0, 0.0, 0.0], x_hi=[0.879, 0.082, 0.475, 1.0, 0.918])
_DEF_IMM = dict(coef=[[-0.008583, 0.01759, -0.6556, 0.1067, 0.04769], [-0.1239, 0.02741, -0.4272, 0.09321, 0.06248], [-0.144, 0.05918, -0.3757, 0.157, 0.07332]],
                cov=[[0.005587, 0.005405, 0.004861], [0.005405, 0.007847, 0.006104], [0.004861, 0.006104, 0.00658]],
                x_lo=[-0.159, 0.003, 0.0, 0.0], x_hi=[1.478, 0.082, 0.475, 1.0])


_ROOTS: dict = {}


def _mvn(cal, x, rng, dflt):
    coef = np.asarray(cal.get("coef", dflt["coef"]), float)
    x = np.clip(x, cal.get("x_lo", dflt["x_lo"]), cal.get("x_hi", dflt["x_hi"]))
    mu = coef @ np.concatenate([[1.0], x])
    hit = _ROOTS.get(id(cal))
    if hit is not None and hit[0] is cal:
        L = hit[1]
    else:
        cov = np.asarray(cal.get("cov", dflt["cov"]), float)
        w, V = np.linalg.eigh(0.5 * (cov + cov.T))           # a square root that tolerates a pooled, not quite
        L = V * np.sqrt(np.clip(w, 1e-12, None))               # positive-definite covariance
        _ROOTS[id(cal)] = (cal, L)
    return mu + L @ rng.standard_normal(len(mu))


def _screen_fast(sample, rng, opt):
    b = _base(sample)
    r = _refs(sample, b)
    cal = _calib("corrosion_screen")
    e = _mvn(cal, _feat_screen(sample, b), rng, _DEF_SCREEN)
    design = sample.get("design") or sample["composition"]
    rp = r["rp_m"] * math.exp(e[0])
    B = float(np.clip(r["B"] * math.exp(e[1]), 5.0, 80.0)) if opt["cp"] else B_DEFAULT
    icorr = B / rp * 1000.0
    out = dict(ocp_mV=r["ocp"] + e[3], rp_ohm_cm2=rp, icorr_uA_cm2=icorr,
               early_rate_um_yr=K_G102 * icorr * equivalent_weight(design) / _rho(design))
    if opt["eis"]:
        out["rct_ohm_cm2"] = r["rct"] * math.exp(e[2])
    if opt["cp"]:
        Eb, Erp = r["Eb"], r["Erp"]
        if rng.random() < P_CREVICE:
            _, Eb, Erp, _ = _eb_nominal(b, -abs(rng.normal(100.0, 30.0)))
        out["Eb_mV"] = Eb + e[4]
        out["Erp_mV"] = min(Erp + e[5], out["Eb_mV"] - 5.0)
    return out


def _imm_fast(sample, rng, opt):
    r = _imm_refs(sample)
    cal = _calib("immersion")
    e = _mvn(cal, _feat_imm(sample), rng, _DEF_IMM)
    out = dict(rate30_um_yr=r["r30"] * math.exp(e[0]), attack_um=_attack_fast(sample, rng, opt["fields"]))
    for el, ref, ee in (("Cu", r["cu"], e[1]), ("Ni", r["ni"], e[2])):
        v = ref * math.exp(ee) + rng.normal(0, math.hypot(BLANK[el][1], INST_SD))
        if v >= LOD[el]:
            out[el.lower() + "_ppb"] = float(v)
    return out


# ----------------------------------------------------------------------------------------------- the contract
def _opts(dflt, kw):
    o = dict(dflt)
    o.update({k: v for k, v in kw.items() if k in dflt})
    return o


def measure_screen(sample: dict, campaign: str, rng, fidelity: str = "fast", **kw) -> dict:
    """The CubXL screen on one spot: ocp_mV, rp_ohm_cm2, icorr_uA_cm2, early_rate_um_yr, rct_ohm_cm2 (with
    ``eis``), Eb_mV and Erp_mV (with ``cp``). kw: ocp_min, eis, cp, cp_rate_mV_s, electrolyte, ir_comp."""
    if campaign != "onr_cu" or "corrosion" not in sample:
        return {}
    opt = _opts(DEFAULT_SCREEN, kw)
    if fidelity == "fast" and all(opt[k] == DEFAULT_SCREEN[k] for k in ("ocp_min", "cp_rate_mV_s", "electrolyte",
                                                                         "ir_comp")):
        return _screen_fast(sample, rng, opt)
    return _screen_chain(sample, rng, "full" if fidelity == "full" else "lite", opt)[0]


def measure_immersion(sample: dict, campaign: str, rng, fidelity: str = "fast", **kw) -> dict:
    """The 30-day immersion of a coupon: rate30_um_yr, attack_um, cu_ppb and ni_ppb (above the LOD). kw: days,
    fields (SEM fields imaged)."""
    if campaign != "onr_cu" or "corrosion" not in sample:
        return {}
    opt = _opts(DEFAULT_IMM, kw)
    if fidelity == "fast" and opt["days"] == DEFAULT_IMM["days"]:
        return _imm_fast(sample, rng, opt)
    return _imm_chain(sample, rng, "full" if fidelity == "full" else "lite", opt)[0]


# ----------------------------------------------------------------------------------------------- calibration
def _fit_mvn(X, E, k=1.5, iters=8, const=()):
    """Mean of each residual linear in the features, fitted by Huber's iteratively reweighted least squares (so the
    lite chain's rare edge cases, such as E_rp pinned near E_corr, do not tilt the fit), and the covariance of the
    residuals of the runs within 4 robust sd on every output. Outputs in ``const`` get an intercept only: their
    state dependence is already in the closed-form reference (the potentials)."""
    X, E = np.asarray(X, float), np.asarray(E, float)
    A = np.column_stack([np.ones(len(X)), X])
    coef = np.linalg.lstsq(A, E, rcond=None)[0]           # (1 + n_feat) x n_out
    sd = np.ones(E.shape[1])
    for j in range(E.shape[1]):
        Aj = A[:, :1] if j in const else A
        c = np.linalg.lstsq(Aj, E[:, j], rcond=None)[0]
        for _ in range(iters):
            r = E[:, j] - Aj @ c
            sd[j] = max(1.4826 * np.median(np.abs(r - np.median(r))), 1e-9)
            w = np.minimum(1.0, k * sd[j] / np.maximum(np.abs(r), 1e-12))
            sw = np.sqrt(w)
            c = np.linalg.lstsq(Aj * sw[:, None], E[:, j] * sw, rcond=None)[0]
        coef[:, j] = 0.0
        coef[:len(c), j] = c
    res = E - A @ coef
    ok = np.all(np.abs(res) < 4 * sd, axis=1)
    cov = res[ok].T @ res[ok] / max(ok.sum() - A.shape[1], 1)
    return coef.T, cov, res


def calibrate(samples_by_campaign: dict, rng, reps: int = 4) -> dict:
    """Fit the fast mode's residual distributions on the lite chain over the campaign's representative parts."""
    parts = [p for _, p in samples_by_campaign.get("onr_cu", []) if "corrosion" in p and p.get("mode") != "preplaced"]
    XS, ES, XI, EI, EI2 = [], [], [], [], []
    for p in parts:
        b = _base(p)
        r = _refs(p, b)
        xs = _feat_screen(p, b)
        ri = _imm_refs(p)
        xi = _feat_imm(p)
        for _ in range(reps):
            o, info = _screen_chain(p, rng, "lite", DEFAULT_SCREEN)
            if all(k in o for k in ("rct_ohm_cm2", "Eb_mV", "Erp_mV")):
                Eb_r, Erp_r = r["Eb"], r["Erp"]
                if info["crevice_shift"]:
                    _, Eb_r, Erp_r, _ = _eb_nominal(b, info["crevice_shift"])
                ES.append([math.log(o["rp_ohm_cm2"] / r["rp_m"]), math.log(info["B"] / r["B"]),
                           math.log(o["rct_ohm_cm2"] / r["rct"]), o["ocp_mV"] - r["ocp"], o["Eb_mV"] - Eb_r,
                           o["Erp_mV"] - Erp_r])
                XS.append(xs)
            oi, _ = _imm_chain(p, rng, "lite", DEFAULT_IMM)
            row = [math.log(oi["rate30_um_yr"] / ri["r30"]), math.log(max(oi.get("cu_ppb", LOD["Cu"]), 1e-3) / ri["cu"])]
            if "ni_ppb" in oi and ri["ni"] > 0:
                EI.append(row + [math.log(oi["ni_ppb"] / ri["ni"])])
                XI.append(xi)
            else:
                EI2.append((xi, row))
    cs, covs, res_s = _fit_mvn(XS, ES, const=(3, 4, 5))
    XS = np.asarray(XS)
    out = {"corrosion_screen": dict(keys=_SCREEN_KEYS, features=["ln(early/20)", "porosity", "beta_prime", "Ni/30",
                                                                 "Al/10"],
                                    coef=cs.tolist(), cov=covs.tolist(), x_lo=XS.min(0).tolist(),
                                    x_hi=XS.max(0).tolist(), n=len(XS), p_crevice=P_CREVICE,
                                    check=dict(mean=np.mean(ES, 0).tolist(), sd=np.std(ES, 0).tolist()))}
    if len(EI) >= 12:
        ci, covi, _ = _fit_mvn(XI, EI)
        XI_all = np.asarray(XI + [x for x, _ in EI2])
        if EI2:     # the r30 and Cu rows of Ni-free alloys refine their own means
            ci2, cov2, _ = _fit_mvn([x for x, _ in EI2] + XI, [rw for _, rw in EI2] + [e[:2] for e in EI])
            ci[:2], covi[:2, :2] = ci2, cov2
        out["immersion"] = dict(keys=_IMM_KEYS, features=["ln(r30/10)", "porosity", "beta_prime", "Ni/30"],
                                coef=ci.tolist(), cov=covi.tolist(), x_lo=XI_all.min(0).tolist(),
                                x_hi=XI_all.max(0).tolist(), n=len(EI) + len(EI2),
                                check=dict(mean=np.mean(EI, 0).tolist(), sd=np.std(EI, 0).tolist()))
    return out


# ----------------------------------------------------------------------------------------------- figures
def draw_screen(res: dict, axs) -> None:
    """OCP, LPR, Nyquist and cyclic polarization of a 'full' screen result on four axes."""
    r = res["raw"]
    a = axs[0]
    a.plot(r["ocp_t_s"] / 60.0, r["ocp_E_mV"], lw=1, color="#2b6cb0")
    a.axhline(res["ocp_mV"], color="#c05621", lw=1, ls="--", label=f"OCP {res['ocp_mV']:.0f} mV")
    a.set(xlabel="time (min)", ylabel="E vs Ag/AgCl (mV)", title="open-circuit potential")
    a.legend(fontsize=7, frameon=False)
    a = axs[1]
    a.plot(r["lpr_i_uA_cm2"], r["lpr_E_mV"] - r["lpr_Eoc_mV"], ".", ms=2, color="#2b6cb0")
    ii = np.linspace(r["lpr_i_uA_cm2"].min(), r["lpr_i_uA_cm2"].max(), 2)
    fit = r["lpr_fit"]
    a.plot(ii, fit["slope_mV_per_uA_cm2"] * ii + fit["intercept_mV"] - r["lpr_Eoc_mV"], color="#c05621", lw=1.2,
           label=f"Rp {res['rp_ohm_cm2'] / 1e3:.1f} kOhm cm2")
    a.set(xlabel="i (uA/cm2)", ylabel="E - Eoc (mV)", title="LPR +-10 mV")
    a.legend(fontsize=7, frameon=False)
    a = axs[2]
    if "eis_Zre" in r:
        a.plot(r["eis_Zre"] / 1e3, -r["eis_Zim"] / 1e3, "o", ms=2.5, mfc="none", color="#2b6cb0", label="measured")
        a.plot(r["eis_fit_Zre"] / 1e3, -r["eis_fit_Zim"] / 1e3, color="#c05621", lw=1.2,
               label=f"Randles fit, Rct {res['rct_ohm_cm2'] / 1e3:.1f} k")
        a.set_aspect("equal", adjustable="datalim")
        a.legend(fontsize=7, frameon=False)
    a.set(xlabel="Z' (kOhm cm2)", ylabel="-Z'' (kOhm cm2)", title="EIS (Nyquist)")
    a = axs[3]
    if "cp_E_mV" in r:
        fw = r["cp_dir"] > 0
        a.semilogx(np.abs(r["cp_i_uA_cm2"][fw]), r["cp_E_mV"][fw], lw=1, color="#2b6cb0", label="forward")
        a.semilogx(np.abs(r["cp_i_uA_cm2"][~fw]), r["cp_E_mV"][~fw], lw=1, color="#805ad5", label="reverse")
        for key, col in (("Eb_mV", "#c53030"), ("Erp_mV", "#2f855a")):
            if key in res:
                a.axhline(res[key], color=col, ls="--", lw=0.9, label=f"{key[:-3]} {res[key]:.0f} mV")
        a.legend(fontsize=7, frameon=False)
    a.set(xlabel="|i| (uA/cm2)", ylabel="E vs Ag/AgCl (mV)", title="cyclic polarization")


def draw_immersion(res: dict, axs) -> None:
    """G1 cleaning plot (mass vs cycle with the extrapolation) and the SEM attack per field, with the ICP draws."""
    r = res["raw"]
    a = axs[0]
    a.plot(r["cycles"], r["mass_mg"], "o", color="#2b6cb0", label="weighed")
    kk = np.linspace(0, r["cycles"][-1], 2)
    a.plot(kk, r["fit"]["slope_mg"] * kk + r["fit"]["intercept_mg"], color="#c05621", lw=1.2,
           label=f"G1 extrapolation: loss {r['mass_loss_mg']:.2f} mg")
    a.axhline(r["m0_mg"], color="0.5", lw=0.8, ls=":", label="before exposure")
    a.set(xlabel="cleaning cycle", ylabel="coupon mass (mg)",
          title=f"30-day mass loss: {res['rate30_um_yr']:.1f} um/yr")
    a.legend(fontsize=7, frameon=False)
    a = axs[1]
    a.bar(np.arange(1, len(r["sem_field_max_um"]) + 1), r["sem_field_max_um"], color="#805ad5")
    a.axhline(r["sem_lod_um"], color="0.5", lw=0.8, ls=":")
    icp = f"ICP day 30: Cu {r['icp_cu_ppb'][-1]:.0f} ppb, Ni {r['icp_ni_ppb'][-1]:.0f} ppb"
    a.set(xlabel="SEM field", ylabel="deepest attack (um)", title=f"attack {res['attack_um']:.1f} um\n{icp}")


def thumb(ax) -> None:
    """A bold cyclic-polarization icon (the V at E_corr, the passive-like plateau, breakdown with a marker, and the
    reverse loop closing on the forward scan) on a transparent axes, legible at 120 px."""
    k = _kin(1.5, 58.0, 150.0, 25.0, 12.0, -200.0, 250.0)
    E = np.linspace(-330, 420, 400)
    i_f = np.maximum(np.abs(_anodic(E, k) - _cathodic(E, k)), 0.08)
    E_ap, E_rp = E[-1], 60.0
    A_ap, A_rp = float(_anodic(np.array(E_ap), k)), float(_anodic(np.array(E_rp), k))
    s_r = (E_ap - E_rp) / math.log(A_ap / A_rp)
    Er = np.linspace(E_ap, -40.0, 250)
    i_r = np.abs(F_FILM * _anodic(Er, k) + (1 - F_FILM) * A_ap * np.exp((Er - E_ap) / s_r) - _cathodic(Er, k))
    ax.plot(np.log10(i_f), E, color="#2b6cb0", lw=12, solid_capstyle="round", solid_joinstyle="round")
    ax.plot(np.log10(i_r), Er, color="#d53f8c", lw=12, solid_capstyle="round", solid_joinstyle="round")
    Eb = 250.0 + 15.0 * math.log(100.0 / 12.0)
    ax.plot([2.0], [Eb], "o", ms=34, color="#dd6b20", mec="white", mew=4)
    ax.set_xlim(-1.4, 3.4)
    ax.set_ylim(-350, 450)
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

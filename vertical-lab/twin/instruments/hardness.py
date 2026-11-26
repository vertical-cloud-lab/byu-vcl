"""Hardness: Vickers microhardness (Mitutoyo HM-220, HV0.5) and nanoindentation (KLA iMicro, Berkovich, Oliver-Pharr).

**Vickers** (ISO 6507-1 / ASTM E384). The true hardness of the metal under an indent follows Tabor's relation,
HV ~ C sigma(e_r) with C = 3 and e_r = 8 % (Tabor, The Hardness of Metals, 1951), on the sound matrix law
(``mech.matrix_law``) and the build's texture (as the PIP sees it). The indentation size effect is Nix-Gao's,
H = H0 sqrt(1 + h* / h) (Nix & Gao, J. Mech. Phys. Solids 46, 1998, https://doi.org/10.1016/S0022-5096(97)00086-0),
h* = 0.6 um Al, 1.0 um Cu (assumed), at the indent's depth h = d / 7. Each of 5 indents (HV0.5, F = 4.903 N) has a
plastic zone of about 1.5 d across; pores of the part's populations fall in it as a Poisson draw, and pore volume
there softens the indent by twice its share (assumed); an indent that lands on a large void (> 30 % of the zone) is
rejected and redone, as ISO 6507 requires of a misshapen indent. The diagonals are read optically: +-0.4 um plus
0.4 % of d per diagonal (assumed for a 50x objective and an operator), and HV = 1.8544 F / d^2 (F in kgf, d in mm).

**Nanoindentation** (Oliver & Pharr, J. Mater. Res. 7, 1992, https://doi.org/10.1557/JMR.1992.1564). Load-controlled
to 50 mN (Al) or 80 mN (Cu), 16 indents (9 in lite). True hardness: Tabor at the Berkovich's 7.2 % representative
strain with Nix-Gao (h* above); the indent's plastic zone (~7 h) samples one grain or a few, so grain-orientation
scatter is 6 % in H and 2 % (Al, Zener ratio 1.2) or 8 % (Cu, 3.2) in E, divided by the root of the grains sampled
(assumed); an indent can land in beta' (Cu: H x 1.4, E x 0.9, assumed). Oliver-Pharr's contact model assumes sink-in,
so where the metal piles up (Hill's c^2 > 1: low work hardening) the true contact area exceeds the computed one and H
and E read high (Bolshakov & Pharr, J. Mater. Res. 13, 1998, https://doi.org/10.1557/JMR.1998.0146): A_true / A_OP =
1 + 0.6 (c^2 - 1) (assumed magnitude). Thermal drift 0.05 nm/s +- 0.03 nm/s after correction (assumed), tip area
function A = 24.5 h_c^2 + C1 h_c with a 5 % error in the calibrated C1 (assumed), diamond E = 1141 GPa, nu = 0.07.
The analysis: stiffness from a quadratic fit to the top 60 % of the unloading curve, h_c = h_max - 0.75 P / S,
E_r = sqrt(pi) S / (2 beta sqrt(A)), beta = 1.034, then the sample modulus with the alloy's Poisson ratio.

``fast`` samples log(measured / Tabor value) per output from the state-dependent normal ``calibrate()`` fitted.
"""
from __future__ import annotations

import math

import numpy as np

from twin.instruments import mech

G = 9.80665
SPEC = dict(vickers=dict(station="hardness", hours=0.25, indents=5, consumables=dict(polish_usd=5.0),
                         note="Mitutoyo HM-220, HV0.5"),
            nanoindent=dict(station="nanoindent", hours=1.0, indents=16, consumables=dict(polish_usd=10.0),
                            note="KLA iMicro, Berkovich, Oliver-Pharr"))
H_STAR_UM = {"Al": 0.6, "Cu": 1.0}
E_DIAMOND, NU_DIAMOND = 1141.0, 0.07


def _tabor_MPa(sample, strain):
    law = mech.matrix_law(sample)
    an = mech.anisotropy(sample)
    return 3.0 * float(mech.voce(strain, law)) * (1 - 0.5 * (1 - an["r_z"]))


def _zone_porosity(sample, rng, zone_mm):
    """Pore volume share in a hemispherical zone of diameter zone_mm: a Poisson draw of each population."""
    V = 2 / 3 * math.pi * (zone_mm / 2) ** 3
    tot = 0.0
    for name, n_v, mu, s, af in mech.defect_populations(sample):
        if name == "crack":
            continue
        k = rng.poisson(n_v * V)
        if k:
            d = np.exp(mu + s * rng.normal(0, 1, min(k, 50))) * 1e-3
            v = np.minimum(math.pi / 6 * d ** 3, V)          # a pore bigger than the zone fills it
            tot += float(np.sum(v)) * k / len(d)
    return min(tot / V, 1.0)


# ---------------------------------------------------------------------------------------------- Vickers
def _vickers_chain(sample, campaign, rng, fidelity, n=5):
    base = mech.base_of(campaign)
    hv0 = _tabor_MPa(sample, 0.08) / G                        # kgf/mm^2
    F = 0.5                                                   # kgf
    hs = H_STAR_UM[base] * 1e-3
    vals, diag, rejected = [], [], 0
    while len(vals) < n and rejected < 20:
        d = math.sqrt(1.8544 * F / hv0)
        for _ in range(4):                                    # Nix-Gao at the indent's own depth
            hv = hv0 * math.sqrt(1 + hs / (d / 7.0))
            d = math.sqrt(1.8544 * F / hv)
        p = _zone_porosity(sample, rng, 1.5 * d)
        if p > 0.3:
            rejected += 1
            continue
        hv_loc = hv * (1 - 2.0 * p) * math.exp(rng.normal(0, 0.02))      # 2 %: local microstructure (assumed)
        d_true = math.sqrt(1.8544 * F / hv_loc)
        d1 = d_true * (1 + rng.normal(0, 0.004)) + rng.normal(0, 0.4e-3)
        d2 = d_true * (1 + rng.normal(0, 0.004)) + rng.normal(0, 0.4e-3)
        dm = 0.5 * (d1 + d2)
        vals.append(1.8544 * F / dm ** 2)
        diag.append((d1 * 1e3, d2 * 1e3))
    out = dict(hv=float(np.mean(vals)), hv_sd=float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0, n_indents=len(vals),
               rejected=rejected)
    if fidelity == "full":
        out["raw"] = dict(hv=vals, diagonals_um=diag, hv_tabor=hv0)
    return out


# ---------------------------------------------------------------------------------------------- nanoindentation
def _nano_one(sample, campaign, rng, n_pts, pmax_mN):
    base = mech.base_of(campaign)
    nu = mech.poisson(base)
    E = mech.modulus_GPa(sample["composition"], 0.0, 25.0, base)
    H0 = _tabor_MPa(sample, 0.072) / 1e3 * (2.8 / 3.0)       # GPa; Berkovich constraint ~2.8
    hs = H_STAR_UM[base]
    grain = max(float(sample.get("grain_um", 10.0)), 0.5)
    # depth estimate, then the size effect at that depth
    h = math.sqrt(pmax_mN * 1e-3 / (H0 * 1e9) / 24.5) * 1e6     # um
    for _ in range(4):
        H = H0 * math.sqrt(1 + hs / h)
        h = math.sqrt(pmax_mN * 1e-3 / (H * 1e9) / 24.5) * 1e6
    n_gr = max(1.0, (7 * h / grain) ** 2)
    sdE = (0.02 if base == "Al" else 0.08) / math.sqrt(n_gr)
    H *= math.exp(rng.normal(0, 0.06 / math.sqrt(n_gr)))
    Ei = E * math.exp(rng.normal(0, sdE))
    if rng.random() < float(sample.get("beta_prime", 0.0)):
        H *= 1.4
        Ei *= 0.9
    # pile-up (Hill's c^2 from the matrix law's local exponent)
    law = mech.matrix_law(sample)
    s1, s0 = float(mech.voce(0.072, law)), float(mech.voce(0.0072, law))
    m = min(max(math.log(s1 / s0) / math.log((0.072 + s1 / E / 1e3) / (0.0072 + s0 / E / 1e3)), 0.0), 0.6)
    c2 = 2.5 * (2 - m) / (4 + m)
    k_pu = 1 + 0.6 * max(c2 - 1, 0.0)
    Er = 1 / ((1 - nu ** 2) / Ei + (1 - NU_DIAMOND ** 2) / E_DIAMOND)             # GPa
    P = pmax_mN * 1e-3
    A_true = P / (H * 1e9) * 1e12                                                 # um^2
    beta = 1.034
    S = 2 * beta * math.sqrt(A_true * 1e-12) * Er * 1e9 / math.sqrt(math.pi)      # N/m
    A_op = A_true / k_pu
    C1_true = 2.0                                                                 # um, tip rounding (assumed)
    hc = (-C1_true + math.sqrt(C1_true ** 2 + 4 * 24.5 * A_op)) / (2 * 24.5)       # um
    hmax = hc + 0.75 * P / S * 1e6
    hf = hmax - 1.5 * P / S * 1e6
    # load-displacement record: loading P = P (h / hmax)^2, hold, unloading power law m = 1.5
    t_load, t_hold, t_un = 20.0, 10.0, 20.0
    nl = max(n_pts // 2, 10)
    hl = np.linspace(0, hmax, nl)
    Pl = P * (hl / hmax) ** 2
    hu = np.linspace(hmax, hf + 0.25 * (hmax - hf), nl)
    Pu = P * ((hu - hf) / (hmax - hf)) ** 1.5
    drift = rng.normal(0.0, 0.03) * 1e-3                                          # um/s residual after correction
    tl = np.linspace(0, t_load, nl)
    tu = t_load + t_hold + np.linspace(0, t_un, nl)
    hl_m = hl + drift * tl + rng.normal(0, 0.0005, nl)
    hu_m = hu + drift * tu + rng.normal(0, 0.0005, nl)
    Pl_m = Pl + rng.normal(0, 2e-7, nl)
    Pu_m = Pu + rng.normal(0, 2e-7, nl)
    # the analysis
    sel = Pu_m > 0.4 * P
    cc = np.polyfit(hu_m[sel], Pu_m[sel], 2)
    hm = float(hu_m[0])
    S_m = (2 * cc[0] * hm + cc[1]) * 1e6                                          # N/m
    hc_m = hm - 0.75 * P / S_m * 1e6
    C1 = C1_true * (1 + rng.normal(0, 0.05))
    A_m = 24.5 * hc_m ** 2 + C1 * hc_m
    H_m = P / (A_m * 1e-12) / 1e9
    Er_m = math.sqrt(math.pi) * S_m / (2 * beta * math.sqrt(A_m * 1e-12)) / 1e9
    E_m = (1 - nu ** 2) / (1 / Er_m - (1 - NU_DIAMOND ** 2) / E_DIAMOND)
    return dict(H=H_m, E=E_m, h=(hl_m, Pl_m, hu_m, Pu_m), hmax=hm)


def _nano_chain(sample, campaign, rng, fidelity):
    n = 16 if fidelity == "full" else 9
    pmax = 50.0 if campaign == "flaime_al" else 80.0
    res = [_nano_one(sample, campaign, rng, 400 if fidelity == "full" else 24, pmax) for _ in range(n)]
    Hs, Es = [r["H"] for r in res], [r["E"] for r in res]
    out = dict(H_GPa=float(np.mean(Hs)), E_GPa=float(np.mean(Es)), H_sd=float(np.std(Hs, ddof=1)),
               E_sd=float(np.std(Es, ddof=1)), n_indents=n)
    if fidelity == "full":
        out["raw"] = dict(H=Hs, E=Es, curves=[r["h"] for r in res], pmax_mN=pmax)
    return out


# ---------------------------------------------------------------------------------------------- fast mode
def _feat(sample):
    """Porosity, gas, lack of fusion, columnar share, beta', hardening (pile-up), strength (size effect) and grain
    size (orientation averaging)."""
    f = mech.features(sample)
    law = mech.matrix_law(sample)
    return np.array([f["por"], f["gas"], f["lof"], f["col"], f["beta"], mech.hardening(sample),
                     math.log(float(mech.voce(0.08, law))), math.log(max(float(sample.get("grain_um", 10.0)), 0.5))])


def _ref(sample, campaign):
    base = mech.base_of(campaign)
    return dict(hv=_tabor_MPa(sample, 0.08) / G, H_GPa=_tabor_MPa(sample, 0.072) / 1e3 * (2.8 / 3.0),
                E_GPa=mech.modulus_GPa(sample["composition"], 0.0, 25.0, base))


def _flat(mu, sd, n=8):
    return dict(mu=[mu] + [0] * n, lsd=[math.log(sd)] + [0] * n, xm=[0] * n, xs=[1] * n)


DEF = dict(hv=_flat(0.02, 0.012), H_GPa=_flat(0.25, 0.03), E_GPa=_flat(0.05, 0.02))


def _fast(sample, campaign, rng, keys, name):
    p = mech.calib(name) or DEF
    ref = _ref(sample, campaign)
    x = _feat(sample)
    out = {}
    for k in keys:
        mu, sd = mech.two_level(p[k], x) if "eg" in p[k] else mech.ln_mean_sd(p[k], x)
        out[k] = float(ref[k] * math.exp(mu + sd * rng.normal(0, 1)))
    return out


def measure_vickers(sample, campaign, rng, fidelity="fast", **kw):
    if "strength" not in sample:
        return {}
    if fidelity == "fast":
        out = _fast(sample, campaign, rng, ("hv",), "vickers")
        out["n_indents"] = 5
        return out
    return _vickers_chain(sample, campaign, rng, fidelity)


def measure_nanoindent(sample, campaign, rng, fidelity="fast", **kw):
    if "strength" not in sample:
        return {}
    if fidelity == "fast":
        out = _fast(sample, campaign, rng, ("H_GPa", "E_GPa"), "nanoindent")
        out["n_indents"] = 9
        return out
    return _nano_chain(sample, campaign, rng, fidelity)


def calibrate(samples_by_campaign, rng, reps=5):
    from twin.instruments.calibrate_mech import fit_two_level
    rows = {"vickers": ([], {"hv": []}), "nanoindent": ([], {"H_GPa": [], "E_GPa": []})}
    G = []
    for camp, items in samples_by_campaign.items():
        for j, (lot, part) in enumerate(items):
            ref = _ref(part, camp)
            x = _feat(part)
            for _ in range(reps):
                G.append(f"{camp}{j}")
                v = _vickers_chain(part, camp, rng, "lite")
                rows["vickers"][0].append(x)
                rows["vickers"][1]["hv"].append(math.log(v["hv"] / ref["hv"]))
                nn = _nano_chain(part, camp, rng, "lite")
                rows["nanoindent"][0].append(x)
                rows["nanoindent"][1]["H_GPa"].append(math.log(nn["H_GPa"] / ref["H_GPa"]))
                rows["nanoindent"][1]["E_GPa"].append(math.log(nn["E_GPa"] / ref["E_GPa"]))
    out = {}
    for name, (X, Y) in rows.items():
        X = np.array(X)
        out[name] = {k: fit_two_level(X, np.array(y), np.array(G)) for k, y in Y.items()}
        out[name]["n"] = int(len(X))
    return out


# ---------------------------------------------------------------------------------------------- figures
def draw(res_v, res_n, axs, color="C0", label=None):
    ax = axs[0]
    hv = res_v["raw"]["hv"]
    ax.plot(np.arange(1, len(hv) + 1), hv, "o", color=color, label=label)
    ax.axhline(res_v["hv"], color=color, lw=0.8)
    ax.set_xlabel("indent")
    ax.set_ylabel("HV0.5")
    ax2 = axs[1]
    for i, (hl, Pl, hu, Pu) in enumerate(res_n["raw"]["curves"][:6]):
        ax2.plot(hl * 1e3, Pl * 1e3, color=color, lw=0.8, alpha=0.8, label=label if i == 0 else None)
        ax2.plot(hu * 1e3, Pu * 1e3, color=color, lw=0.8, alpha=0.8)
    ax2.set_xlabel("depth (nm)")
    ax2.set_ylabel("load (mN)")


def thumb(ax):
    # a Vickers indent: the square pyramid seen from above, its diagonals, and a load arrow
    sq = np.array([[0, 1], [1, 0], [0, -1], [-1, 0], [0, 1]])
    ax.fill(sq[:, 0], sq[:, 1] - 0.25, color="#d9822b", alpha=0.35)
    ax.plot(sq[:, 0], sq[:, 1] - 0.25, lw=10, color="#d9822b", solid_joinstyle="round")
    ax.plot([-1, 1], [-0.25, -0.25], lw=5, color="#8a4b10")
    ax.plot([0, 0], [0.75, -1.25], lw=5, color="#8a4b10")
    ax.annotate("", xy=(0, 1.0), xytext=(0, 1.9), arrowprops=dict(arrowstyle="-|>", lw=10, color="#8c8c8c",
                                                                  mutation_scale=60))
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.5, 2.0)

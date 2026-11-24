"""FLAIME's ground truth: what an aluminium alloy actually does, from powder to tensile bar, and what each simulator
and instrument reports about it.

The truth is physics with its gaps left in on purpose. Each node is a closed form (twin/physics.py, twin/thermo.py)
plus three things the simulators cannot see, because the real lab cannot either until it measures:

1. **Nucleants.** Al3(Sc,Zr,Er,Ti) formed above an LPBF threshold refine the grains and suppress hot cracking
   (Martin et al., Nature 549, 2017; Spierings et al. 2017). No Scheil calculation sees grain morphology, so no
   CALPHAD node reports it; ``kappa`` scales the effect (1: as in Zr-inoculated 7075; 0: none), as in DAL's
   preliminary benchmark (benchmarks/bofn-prelim).
2. **The open database's own errors** (twin/thermo.py): Zr and Sc on the wrong side of k = 1, no primary Al3Zr, no
   Er. The open node inherits them; the TC-Python node does not (it reads the truth with a small error).
3. **Unmodelled metallurgy**: a smooth random field over composition (random Fourier features, fixed by the seed)
   adds a few percent to strength and ductility, so no policy can recover the truth by fitting the closed forms.

Process effects that tie the nodes together: a melt set below the true liquidus leaves Zr, Ti or Sc undissolved (so a
campaign that trusted the open database's 659 degC for Al-0.6Zr atomizes a leaner alloy than it designed); Mg, Zn
and Li boil off in the atomizer and again under the laser; lack of fusion and keyholing come from the melt pool's
size, which depends on the alloy's conductivity and boiling point.

Calibration targets (nominal handbook or datasheet values, LPBF condition; the check is ``reference_table()``):
AlSi10Mg as built YS 240-280 MPa, EL 4-8 %; Scalmalloy aged YS 450-520 MPa, EL 8-14 %; Al-Mn-Cr-Zr aged YS 350-450
MPa; 7075 and 2024 without inoculants crack. Every coefficient below that is ours says "assumed".
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from twin import physics as ph
from twin import thermo, usgs
from twin.spaces import AL

ELEMENTS = AL.elements
# thermal-conductivity reduction per wt% in solution (assumed; AlSi10Mg -> about 160 W/mK near the melting point)
K_RED = dict(Si=0.03, Mg=0.06, Cu=0.04, Zn=0.02, Mn=0.20, Cr=0.25, Zr=0.15, Ti=0.25, Fe=0.10, Ni=0.05, Sc=0.10,
             Li=0.15, Er=0.05, Ce=0.02, Sn=0.02)
# solute LPBF keeps in solution as built (wt%, assumed from extended-solubility reports)
RETAIN = dict(Mn=4.0, Cr=1.0, Zr=0.8, Sc=0.6, Fe=0.5, Ni=0.2, Ti=0.4, Er=0.3, Ce=0.05, Si=2.0, Mg=5.0, Cu=2.5,
              Zn=8.0, Li=2.0, Sn=0.05)
# solid-solution strengthening, MPa per wt%^0.75 (assumed; Mg from Al-Mg alloys, Mn from LPBF Al-Mn alloys)
H_SS = dict(Mg=18, Cu=12, Zn=4, Si=8, Mn=32, Cr=25, Li=12, Fe=20, Ni=10, Ti=15, Zr=15, Sc=20, Er=10, Ce=5, Sn=2)
# evaporation: share lost = 1 - exp(-E / E_i), E the energy per volume (J/mm3) under the laser; and in the atomizer
# 1 - exp(-(superheat/S_i)^2) (assumed)
E_EVAP = dict(Zn=150.0, Mg=300.0, Li=250.0)
S_EVAP = dict(Zn=260.0, Mg=420.0, Li=380.0)
L12 = dict(Sc=0.357, Zr=0.5298, Er=0.674)       # mass fraction of the element in Al3X
K_L12 = dict(Sc=2500.0, Zr=1200.0, Er=1500.0)  # MPa per sqrt(volume fraction), assumed: Al3Sc finest
SPOT_R = 40e-6                                  # m, Aconity MIDI spot radius (assumed: 80 um spot)


class RandomField:
    """A smooth random function of composition (random Fourier features), fixed by the seed."""

    def __init__(self, seed: int, dim: int, n=24, scale=0.35):
        r = np.random.default_rng(seed)
        self.W = r.normal(0, 1 / scale, (n, dim))
        self.b = r.uniform(0, 2 * np.pi, n)
        self.a = r.normal(0, 1, n) / math.sqrt(n / 2)

    def __call__(self, u):
        return float(self.a @ np.cos(self.W @ u + self.b))


def _comp_vec(comp):
    return np.array([comp.get(e, 0.0) / AL.bounds[e][1] for e in ELEMENTS])


class AlTruth:
    base = "Al"

    def __init__(self, seed: int = 0, kappa: float = 1.0):
        self.seed, self.kappa = seed, kappa
        self.th, self.open = thermo.AlSolidification("truth"), thermo.AlSolidification("open")
        self.f_ys = RandomField(seed * 7919 + 1, len(ELEMENTS))
        self.f_el = RandomField(seed * 7919 + 2, len(ELEMENTS))

    # ------------------------------------------------------------------------------------------------ thermodynamics
    @lru_cache(maxsize=200000)
    def _thermo(self, key):
        return self.th.run(dict(key))

    def thermo(self, comp: dict) -> dict:
        return self._thermo(tuple(sorted((k, round(v, 4)) for k, v in comp.items())))

    # ------------------------------------------------------------------------------------------------ simulators
    def sim_open(self, comp: dict) -> dict:
        """pycalphad on the open databases, as the fast dilute model (deterministic, biased)."""
        r = self.open.run(comp)
        return dict(liquidus_C=r["T_liquidus_C"], freezing_range_K=r["freezing_range_K"], kou_K=r["kou_index_K"],
                    Q_K=r["Q_K"], eutectic_liquid=r["liquid_at_first_eutectic"])

    def sim_tc(self, comp: dict, rng) -> dict:
        """Thermo-Calc TCAL Scheil (stand-in): the truth's thermodynamics with a few percent error; no grains."""
        r = self.thermo(comp)
        e = lambda s: math.exp(rng.normal(0, s))
        return dict(liquidus_C=r["T_liquidus_C"] + rng.normal(0, 4.0), freezing_range_K=r["freezing_range_K"] * e(0.05),
                    kou_K=1.3 * r["kou_index_K"] * e(0.08), Q_K=r["Q_K"] * e(0.05),
                    eutectic_liquid=r["liquid_at_first_eutectic"])

    def sim_am(self, comp: dict, proc: dict, rng) -> dict:
        """Thermo-Calc AM Module (stand-in): melt-pool size and the defect indices for these settings, 10 % error."""
        mp = self.melt_pool(comp, proc)
        e = lambda s: math.exp(rng.normal(0, s))
        return dict(width_um=mp["W_um"] * e(0.1), depth_um=mp["D_um"] * e(0.1), lof_index=mp["lof"] * e(0.1),
                    keyhole_index=mp["kh"] * e(0.1), cooling_K_s=mp["cool"] * e(0.15))

    # ------------------------------------------------------------------------------------------------ powder
    def atomize(self, comp: dict, proc: dict, set_TL_C: float, rng) -> dict:
        """One atomizer run of a designed composition. The melt is set to the liquidus the campaign believes
        (`set_TL_C`, from whichever CALPHAD node it ran) plus the superheat; below the true liquidus, the primary
        formers don't all dissolve."""
        th = self.thermo(comp)
        T_melt = set_TL_C + proc["superheat_K"]
        actual = dict(comp)
        undissolved = {}
        for el, p in thermo.AL_PRIMARY.items():
            c = comp.get(el, 0.0)
            if c > p[0] and T_melt < p[1] + p[2] * (c - p[0]) ** p[3]:
                # dissolved up to the composition whose liquidus is T_melt
                cmax = p[0] + max(0.0, (T_melt - p[1]) / p[2]) ** (1 / p[3]) if T_melt > p[1] else p[0]
                undissolved[el] = c - cmax
                actual[el] = cmax
        true_superheat = T_melt - th["T_liquidus_C"]
        for el, s in S_EVAP.items():
            if actual.get(el, 0) > 0:
                actual[el] *= math.exp(-(max(T_melt - th["T_alpha_liquidus_C"], 0) / s) ** 2)
        actual["Al"] = 100.0 - sum(v for k, v in actual.items() if k != "Al")
        run = ph.atomize("Al", max(true_superheat, -50.0), proc["pour_mbar"], proc["amplitude"], T_melt, rng,
                         cut=(20.0, 63.0))
        run.update(composition=actual, undissolved=undissolved, T_melt_C=T_melt, true_superheat_K=true_superheat)
        return run

    # ------------------------------------------------------------------------------------------------ LPBF
    def props(self, comp):
        k = 210.0 / (1 + sum(K_RED.get(e, 0.0) * w for e, w in comp.items() if e != "Al"))
        rho = ph.density(comp) * 1000.0
        th = self.thermo(comp)
        Tm = th["T_alpha_liquidus_C"] + 273.15
        vol = comp.get("Mg", 0) + comp.get("Zn", 0) + comp.get("Li", 0)
        Tb = 2743.0 - 60.0 * vol
        A = min(0.30 + 0.003 * (100 - comp.get("Al", 100)), 0.45)
        return k, rho, 1100.0, Tm, Tb, A

    @lru_cache(maxsize=200000)
    def _melt_pool(self, ckey, pkey):
        comp, proc = dict(ckey), dict(pkey)
        k, rho, cp, Tm, Tb, A = self.props(comp)
        T0 = proc["T0_C"] + 273.15
        P, v = proc["P_W"], proc["v_mm_s"] * 1e-3
        half, cool = ph.rosenthal(A, P, v, k, rho, cp, Tm, T0)
        dh = ph.normalized_enthalpy(A, P, v, k, rho, cp, Tm, SPOT_R)
        thr = math.pi * Tb / Tm
        kh = dh / thr
        W = max(2 * half, 30e-6)
        D = 0.5 * W * (1 + max(0.0, kh - 0.6)) ** 1.0
        h, t = proc["h_um"] * 1e-6, proc["t_um"] * 1e-6
        lof = (h / W) ** 2 + (t / D) ** 2
        Ev = P / (proc["v_mm_s"] * proc["h_um"] * 1e-3 * proc["t_um"] * 1e-3)   # J/mm3
        return dict(W_um=W * 1e6, D_um=D * 1e6, cool=cool, kh=kh, lof=lof, Ev=Ev)

    def melt_pool(self, comp, proc):
        ck = tuple(sorted((k, round(v, 4)) for k, v in comp.items()))
        pk = tuple(sorted((k, round(v, 4)) for k, v in proc.items() if k in ("P_W", "v_mm_s", "h_um", "t_um", "T0_C")))
        return self._melt_pool(ck, pk)

    def build(self, lot: dict, proc: dict, rng) -> dict:
        """One cube (or bar) printed from a powder lot at these settings: the true part."""
        comp = dict(lot["composition"])
        mp = self.melt_pool(comp, proc)
        for el, E in E_EVAP.items():
            if comp.get(el, 0) > 0:
                comp[el] *= math.exp(-mp["Ev"] / E)
        comp["Al"] = 100.0 - sum(v for k, v in comp.items() if k != "Al")
        th = self.thermo(comp)
        vol = comp.get("Mg", 0) + comp.get("Zn", 0) + comp.get("Li", 0)
        p_lof = 0.12 / (1 + math.exp(-(mp["lof"] - 1.0) / 0.12))
        p_kh = 0.04 / (1 + math.exp(-(mp["kh"] * (1 + 0.03 * vol) - 1.0) / 0.12))
        p_gas = 0.001 + 2.0 * lot["oxygen_ppm"] * 1e-6 + 0.004 * lot["satellite_frac"]
        psi = 1 - math.exp(-th["nucleant_wt"] / 0.25)
        csi = 1.3 * th["kou_index_K"] * (1 - self.kappa * 0.85 * psi) * (1 - 0.15 * (proc["T0_C"] - 25) / 175)
        crack = 2.0 / (1 + math.exp(-(csi - 280.0) / 60.0))       # crack density, mm per mm^2
        porosity = min(p_lof + p_kh + p_gas + 0.004 * crack, 0.5)
        lam = 43.0 * max(mp["cool"], 1e3) ** -0.324                 # um, cell spacing
        d = psi * 1.5 + (1 - psi) * 25.0 / (1 + max(th["Q_K"], 0) / 30.0)
        return dict(composition=comp, porosity=porosity, rel_density=1 - porosity, crack_density=crack,
                    crack_free=crack < 0.05, csi_K=csi, equiaxed=psi, cell_um=lam, grain_um=d, melt_pool=mp,
                    thermo=th)

    def strength(self, part: dict, temp_C: float = 25.0) -> dict:
        """Yield, tensile strength and elongation after the alloy family's standard heat treatment."""
        comp, th = part["composition"], part["thermo"]
        ss = {e: min(comp.get(e, 0.0), RETAIN[e]) for e in ELEMENTS}
        for el, p in thermo.AL_PRIMARY.items():                       # the primary intermetallic took its excess
            if comp.get(el, 0) > p[0]:
                ss[el] = min(ss[el], p[0] + 0.7 * (comp[el] - p[0]))
        f_e = {e: 0.8 * ss[e] / L12[e] for e in L12}                     # vol% (approx. wt%) of Al3X
        f_l12 = sum(f_e.values())
        k_l12 = sum(K_L12[e] * f_e[e] for e in L12) / f_l12 if f_l12 > 0 else 0.0
        for e in L12:
            ss[e] *= 0.2
        mg2si = min(ss["Mg"] / 1.73, ss["Si"]) * 2.73 * 0.6
        theta = ss["Cu"] / 0.53 * 0.6
        eta = min(ss["Zn"] / 2.7, ss["Mg"]) * 3.7 * 0.6
        delta = ss["Li"] / 0.08 * 0.3
        f_age = mg2si + theta + eta + delta                              # vol%
        ss["Mg"] = max(ss["Mg"] - 0.6 * min(ss["Mg"], ss["Si"] * 1.73) - 0.6 * min(ss["Mg"], ss["Zn"] / 2.7), 0)
        ss["Cu"] *= 0.4
        ss["Zn"] *= 0.4
        ss["Si"] = max(ss["Si"] - 0.6 * min(ss["Mg"] / 1.73, ss["Si"]), 0)
        s_ss = sum(H_SS[e] * ss[e] ** 0.75 for e in ELEMENTS if ss[e] > 0)
        s_hp = 70.0 / math.sqrt(part["grain_um"])
        # LPBF keeps the sluggish solutes in solution, so their equilibrium eutectic mostly never forms
        f2 = min(sum(v * (1.0 if comp.get(e, 0) > RETAIN.get(e, 0) or e in ("Si", "Ce", "Cu", "Ni", "Fe", "Er")
                          else 0.2) for e, v in th["eutectic_by"].items()), 0.5)
        s_cell = 546.0 * math.sqrt(f2) * math.sqrt(0.5 / max(part["cell_um"], 0.1))
        s_l12 = k_l12 * math.sqrt(f_l12 / 100.0)
        s_age = 1000.0 * math.sqrt(f_age / 100.0)
        s_ppt = math.sqrt(s_l12 ** 2 + s_age ** 2)
        u = _comp_vec(comp)
        ys = (15.0 + s_ss + s_hp + s_cell + s_ppt) * (1 + 0.06 * self.f_ys(u))
        if temp_C > 100:
            slow = sum(ss[e] for e in ("Mn", "Cr", "Fe", "Zr", "Sc", "Er")) / max(sum(ss.values()), 1e-9)
            r = ((0.55 + 0.3 * slow) * s_ss + 0.7 * s_hp + 0.5 * s_cell + 0.85 * s_l12 + 0.3 * s_age) / \
                max(s_ss + s_hp + s_cell + s_l12 + s_age, 1e-9)
            ys *= r
        brittle = 2.25 * f2 * (1 - 0.6 * min(comp.get("Ce", 0) / 6, 1)) + 0.05 * f_l12 \
            + sum(0.25 * max(0.0, comp.get(e, 0) - RETAIN[e]) for e in ("Cr", "Mn", "Fe", "Ti", "Ni"))
        el = (30.0 * math.exp(-ys / 450.0) + 2.0) * math.exp(-4.0 * brittle) * (1 + 0.08 * self.f_el(u))
        crack_frac = min(part["crack_density"] / 2.0, 1.0)
        por = part["porosity"]
        ys_m = ys * (1 - 1.5 * por) * (1 - 0.5 * crack_frac)
        el_m = max(el * (1 - 6 * por) * (1 - 0.9 * crack_frac), 0.2)
        uts = ys_m * (1.1 + 0.6 * el_m / (el_m + 10.0))
        return dict(ys_MPa=ys_m, uts_MPa=uts, el_pct=el_m, ys_sound_MPa=ys, parts=dict(
            ss=s_ss, hp=s_hp, cell=s_cell, l12=s_l12, age=s_age))

    # ------------------------------------------------------------------------------------------------ objectives
    @staticmethod
    def burden(comp: dict) -> dict:
        return usgs.mineral_burden(comp, base="Al")


def reference_table(seed=0) -> list:
    """The reference alloys through the truth at a sound process point (the calibration check in notes/twin.md)."""
    from twin.spaces import REFERENCE
    t = AlTruth(seed)
    rng = np.random.default_rng(0)
    out = []
    proc = dict(superheat_K=150, pour_mbar=200, amplitude=0.8, P_W=300, v_mm_s=1000, h_um=110, t_um=30, T0_C=150)
    for name, wt in REFERENCE["flaime_al"].items():
        comp = dict(wt)
        comp["Al"] = 100 - sum(wt.values())
        th = t.thermo(comp)
        lot = t.atomize(comp, proc, th["T_liquidus_C"], rng)
        part = t.build(lot, proc, rng)
        s = t.strength(part)
        hot = t.strength(part, 250)
        out.append(dict(alloy=name, ys=round(s["ys_MPa"]), el=round(s["el_pct"], 1), hot_ys_250=round(hot["ys_MPa"]),
                        rel_density=round(part["rel_density"], 4), crack_density=round(part["crack_density"], 3),
                        csi=round(part["csi_K"]), equiaxed=round(part["equiaxed"], 2),
                        cmdri=round(AlTruth.burden(comp)["cmdri_log"], 4), mbs=round(AlTruth.burden(comp)["mbs_lin"], 4)))
    for name, wt in {"7075": {"Zn": 5.6, "Mg": 2.5, "Cu": 1.6, "Cr": 0.23},
                     "7075 + 1 Zr": {"Zn": 5.6, "Mg": 2.5, "Cu": 1.6, "Cr": 0.23, "Zr": 1.0},
                     "2024": {"Cu": 4.4, "Mg": 1.5, "Mn": 0.6}}.items():
        comp = dict(wt)
        comp["Al"] = 100 - sum(wt.values())
        th = t.thermo(comp)
        lot = t.atomize(comp, proc, th["T_liquidus_C"], rng)
        part = t.build(lot, proc, rng)
        s = t.strength(part)
        out.append(dict(alloy=name, ys=round(s["ys_MPa"]), el=round(s["el_pct"], 1), rel_density=round(part["rel_density"], 4),
                        crack_density=round(part["crack_density"], 3), csi=round(part["csi_K"]),
                        equiaxed=round(part["equiaxed"], 2)))
    return out

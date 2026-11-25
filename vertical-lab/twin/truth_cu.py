"""The ONR campaign's ground truth: a copper alloy powder through blown-powder DED, tensile and seawater tests, and
what each simulator and instrument reports about it.

Built the same way as twin/truth_al.py, on the ONR proposal's own physics (DAL PR 117, onr-yip-technical-proposal-
cu-ded.tex, "Scientific concepts" and Task 2):

* **Thermodynamics**: the mc_ni emulator (twin/thermo.py), corrected to the handbook where the open database is off.
  The open node sees the uncorrected emulator (NAB liquidus 51 degC high).
* **DED**: Rosenthal's moving point source for the melt pool and the cooling rate through solidification (the
  proposal's heat-flow model, without Carderock's temperature-dependent properties); catchment from the melt pool's
  width against the powder stream; lack of fusion where the line energy cannot melt what is caught; Mn lost to
  evaporation in proportion to the excess energy ("manganese and aluminum can be lost to evaporation").
* **Retained beta'**: the share of the high-temperature beta (CALPHAD, 900 degC) kept as martensite rises with the
  cooling rate and falls as later layers temper the deposit (the proposal's Advance 3: "which phases can form as the
  deposit solidifies and which can form or dissolve as it is reheated"). Retained beta' corrodes selectively in
  seawater (Liu 2021, Dobson 2024, cited there).
* **Seawater**: a long-term film-controlled rate falling with Ni (the Cu-Ni film), improved by about 1.5 % Fe in
  solution, Al's oxide and a little Mn; selective attack from beta' and the kappa phases. The one-hour screen measures
  the early rate, before the film matures, so it ranks candidates only partly as the 30-day immersion does (the
  proposal's H5 is about exactly that gap).

Calibration targets: 70-30 Cu-Ni YS 140-170 MPa, EL 35-45 %; 90-10 YS 100-130, EL 35-45 %; DED NAB YS 300-420, EL
10-25 %; long-term quiescent seawater 2-25 um/yr for Cu-Ni (Cu-Ni Association figures), with 70-30 below 90-10.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

from twin import physics as ph
from twin import thermo
from twin.spaces import CU
from twin.truth_al import RandomField

ELEMENTS = CU.elements
STREAM_W = 1.2e-3          # m, powder stream at the melt pool (assumed)
SPOT_R = 0.4e-3            # m (assumed; MX-Lab and X2 spots are about 0.8-1.2 mm)
MODES = {                  # how a deposit is made: tempering of the bulk by later passes, heat accumulation,
    "preplaced": dict(temper=0.0, T0_add=0.0, note="powder spread in grooves, melted by the laser (Utah)"),
    "blown_small": dict(temper=0.35, T0_add=120.0, note="tracks, walls, small blocks from a 0.5 kg lot (Utah)"),
    "blown_large": dict(temper=0.5, T0_add=200.0, note="blocks for bars, coupons and repairs from 2 kg (Mines)"),
}


def _vec(comp):
    return np.array([comp.get(e, 0.0) / CU.bounds[e][1] for e in ELEMENTS])


class CuTruth:
    base = "Cu"

    def __init__(self, seed: int = 0, kappa_beta: float = 1.0, gamma2: float = 0.0):
        self.seed, self.kappa_beta = seed, kappa_beta
        # round 2 (the copper investigation): an effect the CALPHAD nodes don't report. Above about
        # Al = 8.2 + Ni/2 wt% the bronze keeps gamma-2 (Cu9Al4), which corrodes selectively in seawater and
        # embrittles it (the Weill-Couly/Meigh rule for NAB). 0: absent (round 1's truth); 1: on.
        self.gamma2 = gamma2
        self.th, self.open = thermo.CuThermo("truth"), thermo.CuThermo("open")
        self.f_ys = RandomField(seed * 104729 + 1, len(ELEMENTS))
        self.f_el = RandomField(seed * 104729 + 2, len(ELEMENTS))
        self.f_cr = RandomField(seed * 104729 + 3, len(ELEMENTS))

    @lru_cache(maxsize=200000)
    def _thermo(self, key):
        return self.th.run(dict(key))

    def thermo(self, comp):
        return self._thermo(tuple(sorted((k, round(v, 4)) for k, v in comp.items() if k != "Cu")))

    # ---------------------------------------------------------------------------------------------- simulators
    def sim_open(self, comp):
        r = self.open.run(comp)
        return dict(liquidus_C=r["liquidus_C"], solidus_C=r["solidus_C"], freezing_range_K=r["freezing_range_K"],
                    beta_900=r["beta_900"], kappa_700=r["kappa_700"])

    def sim_tc(self, comp, rng):
        r = self.thermo(comp)
        return dict(liquidus_C=r["liquidus_C"] + rng.normal(0, 5), solidus_C=r["solidus_C"] + rng.normal(0, 5),
                    freezing_range_K=max(r["freezing_range_K"] + rng.normal(0, 5), 1.0),
                    beta_900=float(np.clip(r["beta_900"] + rng.normal(0, 0.03), 0, 1)),
                    kappa_700=float(np.clip(r["kappa_700"] + rng.normal(0, 0.01), 0, 1)))

    def sim_heatflow(self, comp, proc, rng):
        """Rosenthal + CALPHAD along the thermal history (Advance 3), as computed on HPC: cooling rate, peak reheat,
        predicted retained beta'. 15 % error on the heat flow."""
        mp = self.melt_pool(comp, proc, "blown_small")
        th = self.thermo(comp)
        cool = mp["cool"] * math.exp(rng.normal(0, 0.15))
        pred = th["beta_900"] * _retain(cool) * (1 - MODES["blown_small"]["temper"])
        return dict(cooling_K_s=cool, width_um=mp["W"] * 1e6 * math.exp(rng.normal(0, 0.1)),
                    beta_prime_pred=float(np.clip(pred + rng.normal(0, 0.03), 0, 1)), energy_ratio=mp["ratio"])

    # ---------------------------------------------------------------------------------------------- powder
    def atomize(self, comp, proc, set_TL_C, rng):
        th = self.thermo(comp)
        T_melt = set_TL_C + proc["superheat_K"]
        actual = dict(comp)
        if actual.get("Mn", 0) > 0:                       # Mn boils off a little in the crucible
            actual["Mn"] *= math.exp(-max(T_melt - th["liquidus_C"], 0) / 900.0)
        undissolved = {}
        if T_melt < th["liquidus_C"]:                     # a cold melt: the last-dissolving additions stay behind
            short = (th["liquidus_C"] - T_melt) / 100.0
            for el in ("Nb", "Ti", "Cr", "Fe"):
                if actual.get(el, 0) > 0:
                    lost = actual[el] * min(short, 0.9)
                    undissolved[el] = lost
                    actual[el] -= lost
        actual["Cu"] = 100.0 - sum(v for k, v in actual.items() if k != "Cu")
        run = ph.atomize("Cu", T_melt - th["liquidus_C"], proc["pour_mbar"], proc["amplitude"], T_melt, rng,
                         cut=(45.0, 150.0))
        carbon = 30 + 0.5 * max(T_melt - 1100, 0) * (0.3 if (comp.get("Ni", 0) + comp.get("Fe", 0)) > 1 else 1.0)
        run.update(composition=actual, undissolved=undissolved, T_melt_C=T_melt, carbon_ppm=carbon,
                   true_superheat_K=T_melt - th["liquidus_C"])
        return run

    # ---------------------------------------------------------------------------------------------- DED
    def props(self, comp):
        k = 390.0 / (1 + 0.35 * comp.get("Ni", 0) + 0.6 * comp.get("Al", 0) + 0.8 * comp.get("Fe", 0)
                     + 0.6 * comp.get("Mn", 0) + 1.0 * sum(comp.get(e, 0) for e in ("Cr", "Si", "Nb", "Ti")))
        rho = ph.density(comp) * 1000.0
        A = float(np.clip(0.15 + 0.004 * comp.get("Ni", 0) + 0.01 * comp.get("Al", 0) + 0.01 * comp.get("Fe", 0),
                          0.1, 0.45))
        Tm = self.thermo(comp)["liquidus_C"] + 273.15
        return k, rho, 480.0, Tm, A

    @lru_cache(maxsize=200000)
    def _mp(self, ckey, pkey, mode):
        comp, proc = dict(ckey), dict(pkey)
        k, rho, cp, Tm, A = self.props(comp)
        T0 = 298.15 + MODES[mode]["T0_add"]
        P, v = proc["P_W"], proc["v_mm_min"] / 60.0 * 1e-3
        half, cool = ph.rosenthal(A, P, v, k, rho, cp, Tm, T0)
        W = max(2 * half, 0.2e-3)
        catch = min(1.0, W / STREAM_W) * 0.9
        mdot = proc["feed_g_min"] / 60.0 * 1e-3                     # kg/s
        need = catch * mdot * (cp * (Tm - 298.15) + 2.05e5)          # W to melt what is caught (latent heat of Cu)
        ratio = A * P * 0.5 / max(need, 1e-9)                         # about half the absorbed power heats the substrate
        return dict(W=W, cool=cool, catch=catch, ratio=ratio)

    def melt_pool(self, comp, proc, mode):
        ck = tuple(sorted((k, round(v, 4)) for k, v in comp.items()))
        pk = tuple(sorted((k, round(v, 4)) for k, v in proc.items() if k in ("P_W", "v_mm_min", "feed_g_min")))
        return self._mp(ck, pk, mode)

    def deposit(self, lot, proc, mode, rng, substrate=None):
        comp = dict(lot["composition"])
        mp = self.melt_pool(comp, proc, mode)
        r = mp["ratio"]
        if comp.get("Mn", 0) > 0:
            comp["Mn"] *= math.exp(-0.06 * max(r - 1.0, 0))
        if comp.get("Al", 0) > 0:
            comp["Al"] *= math.exp(-0.01 * max(r - 1.0, 0))
        comp["Cu"] = 100.0 - sum(v for k, v in comp.items() if k != "Cu")
        th = self.thermo(comp)
        lof = 0.08 / (1 + math.exp(-(1.3 - r) / 0.15))
        kh = 0.02 / (1 + math.exp(-(r - 4.5) / 0.4))
        gas = 0.002 + 1.5e-6 * lot["oxygen_ppm"] + 2e-6 * lot.get("carbon_ppm", 0)
        if mode == "preplaced":                                       # pre-placed powder melts with less porosity
            lof *= 0.5
        porosity = min(lof + kh + gas, 0.4)
        beta_p = th["beta_900"] * _retain(mp["cool"]) * (1 - MODES[mode]["temper"]) * self.kappa_beta
        si_x = max(comp.get("Si", 0) - (0.1 if comp.get("Nb", 0) <= 0 else 0.5), 0)
        # the open database has no Ni-Ti, Ni-Nb or silicide phases (DAL's phase list), so where Si, Nb or Ti are
        # present its solidus runs low; the truth caps the freezing range it inherits from the emulator
        fr = min(th["freezing_range_K"], 120.0)
        idx = fr * (1 + 3 * si_x + 0.8 * comp.get("Ti", 0) + 0.3 * comp.get("Nb", 0)) \
            + 300.0 * max(beta_p - 0.3, 0)
        crack = 1.5 / (1 + math.exp(-(idx - 170.0) / 25.0))
        dil = 0.05 + 0.4 / (1 + math.exp(-(r - 2.5) / 0.8))
        d = 250.0 * max(mp["cool"], 10.0) ** -0.25
        fusion_ok = None
        if substrate is not None:                                    # a repair coupon on cast NAB or wrought 70-30
            mismatch = abs(comp.get("Al", 0) - substrate.get("Al", 0)) / 9.5 + abs(comp.get("Ni", 0) - substrate.get("Ni", 0)) / 30
            fusion_ok = bool(crack < 0.1 and 0.08 <= dil <= 0.4 and porosity < 0.02 and mismatch < 0.9)
        return dict(mode=mode, composition=comp, thermo=th, porosity=porosity, rel_density=1 - porosity,
                    crack_density=crack, crack_free=crack < 0.05, beta_prime=beta_p, dilution=dil, grain_um=d,
                    catchment=mp["catch"], energy_ratio=r, cooling_K_s=mp["cool"], fusion_ok=fusion_ok,
                    temper=MODES[mode]["temper"], pores=dict(lof=lof, keyhole=kh, gas=gas),
                    oxygen_ppm=lot["oxygen_ppm"], carbon_ppm=lot.get("carbon_ppm", 0.0), proc=dict(proc))

    # round 2: blended elemental powders alloyed in the melt pool (the MX-Lab's hoppers; bottleneck.py's DED front
    # end). How readily each addition dissolves in a copper melt pool, 0 (at once) to 1 (barely), assumed: Fe and Cr
    # have miscibility gaps or slow dissolution in liquid Cu, Nb and Ti are refractory, Ni and Mn dissolve fast,
    # Al and Si melt.
    BLEND_K = dict(Ni=0.25, Al=0.0, Fe=1.0, Mn=0.08, Cr=1.0, Si=0.1, Nb=1.0, Ti=0.5)
    BLEND_TM = dict(Ni=1455.0, Al=660.0, Fe=1538.0, Mn=1246.0, Cr=1907.0, Si=1414.0, Nb=2477.0, Ti=1668.0)

    def blend_deposit(self, comp, proc, rng, oxygen_ppm=900.0):
        """Blocks deposited from a blend of elemental powders mixed to the design's composition. The pool alloys
        most of it; what does not dissolve stays as particles and composition swings (``inhomogeneity``), which
        add porosity, lower ductility and set up galvanic couples in seawater. Thermal history as blown_small."""
        lot = dict(composition=dict(comp), oxygen_ppm=oxygen_ppm, satellite_frac=0.0, carbon_ppm=40.0)
        part = self.deposit(lot, proc, "blown_small", rng)
        mp = self.melt_pool(comp, proc, "blown_small")
        T_pool = self.thermo(comp)["liquidus_C"] + float(np.clip(150.0 * (mp["ratio"] - 1.0), 0.0, 600.0))
        und, inh = {}, 0.0
        for el, w in comp.items():
            if el == "Cu" or w <= 0:
                continue
            k = self.BLEND_K.get(el, 0.3)
            f = k / (1.0 + math.exp((T_pool - self.BLEND_TM.get(el, 1400.0) + 150.0) / 120.0))
            f = float(np.clip(f + rng.normal(0, 0.03), 0.0, 1.0))
            und[el] = w * f
            inh += (w / 100.0) * f + 0.002 * w * k
        achieved = {e: (w - und.get(e, 0.0)) if e != "Cu" else w for e, w in part["composition"].items()}
        achieved["Cu"] = 100.0 - sum(v for e, v in achieved.items() if e != "Cu")
        th = self.thermo(achieved)
        part.update(composition=achieved, thermo=th, blend=True, inhomogeneity=inh, undissolved=und,
                    beta_prime=float(np.clip(th["beta_900"] * _retain(mp["cool"]) * (1 - MODES["blown_small"]["temper"])
                                             * self.kappa_beta * (1 + rng.normal(0, 0.1)), 0, 1)))
        part["porosity"] = min(part["porosity"] + 0.006 + 0.05 * inh, 0.4)
        part["rel_density"] = 1 - part["porosity"]
        part["pores"] = dict(part.get("pores", {}), gas=part.get("pores", {}).get("gas", 0) + 0.006 + 0.05 * inh)
        part["crack_density"] = part["crack_density"] * (1 + 2 * inh)
        part["crack_free"] = part["crack_density"] < 0.05
        return part

    def strength(self, part):
        c, th = part["composition"], part["thermo"]
        fe_ss = min(c.get("Fe", 0), 2.3 + 0.3 * c.get("Al", 0))
        kappa = th["kappa_700"] * (0.5 + part["temper"])
        ss = 45 + 2.6 * c.get("Ni", 0) + 14 * c.get("Al", 0) + 6 * c.get("Mn", 0) + 5 * fe_ss \
            + 25 * c.get("Cr", 0) + 20 * c.get("Si", 0) + 30 * c.get("Nb", 0) + 20 * c.get("Ti", 0)
        ys = (ss + 400 * math.sqrt(max(kappa, 0)) + 250 * part["beta_prime"] + 150 / math.sqrt(part["grain_um"])) \
            * (1 + 0.05 * self.f_ys(_vec(c)))
        crack_frac = min(part["crack_density"] / 1.5, 1)
        por = part["porosity"]
        el = 45 * math.exp(-ys / 600) * (1 - 1.5 * min(part["beta_prime"], 0.5)) * (1 + 0.06 * self.f_el(_vec(c))) \
            * math.exp(-3 * max(c.get("Fe", 0) - fe_ss, 0))
        ys_m = ys * (1 - 1.5 * por) * (1 - 0.4 * crack_frac)
        el_m = max(el * (1 - 6 * por) * (1 - 0.9 * crack_frac), 0.3)
        if part.get("blend"):                      # undissolved particles: crack starters
            el_m = max(el_m * math.exp(-4.0 * part.get("inhomogeneity", 0.0)), 0.3)
        g2 = self.gamma2 * max(c.get("Al", 0.0) - (8.2 + 0.5 * c.get("Ni", 0.0)), 0.0)
        if g2 > 0:
            el_m = max(el_m * math.exp(-1.2 * g2), 0.3)
        return dict(ys_MPa=ys_m, uts_MPa=ys_m * (1.3 + 0.9 * el_m / (el_m + 20)), el_pct=el_m, ys_sound_MPa=ys)

    def corrosion(self, part):
        """True long-term rate (um/yr), 30-day selective attack depth (um), and the early (one-hour) rate."""
        c, th = part["composition"], part["thermo"]
        ni, al, fe, mn = c.get("Ni", 0), c.get("Al", 0), c.get("Fe", 0), c.get("Mn", 0)
        fe_ss = min(fe, 2.3 + 0.3 * al)
        g_fe = 1 - 0.3 * math.exp(-((fe_ss - 1.5) / 1.0) ** 2) + 0.25 * max(fe - fe_ss, 0)
        g_al = 1 / (1 + 0.12 * al)
        g_mn = 1 - 0.04 * min(mn, 2.0)
        g_cr = 1 - 0.1 * min(c.get("Cr", 0) / 0.7, 1)
        rate = 35.0 / (1 + ni / 8) * g_fe * g_al * g_mn * g_cr * (1 + 10 * part["porosity"]) \
            * (1 + 0.08 * self.f_cr(_vec(c)))
        attack = 2.5 * (al / 9.2) ** 2 * (1 + 5 * th["kappa_700"]) + 45 * part["beta_prime"] ** 1.1
        early = 35.0 / (1 + ni / 25) * g_al ** 0.5 * (1 + 2 * part["beta_prime"])
        eb = 50 + 8 * ni + 15 * al - 300 * part["beta_prime"]
        g2 = self.gamma2 * max(al - (8.2 + 0.5 * ni), 0.0)
        if g2 > 0:                                 # gamma-2 corrodes selectively
            rate *= 1 + 2.5 * g2
            attack += 25.0 * g2
            early *= 1 + 1.5 * g2
        if part.get("blend"):                      # composition swings: local galvanic couples
            inh = part.get("inhomogeneity", 0.0)
            rate *= 1 + 3 * inh
            early *= 1 + 4 * inh
            attack += 20 * inh
            eb -= 400 * inh
        return dict(rate_um_yr=rate, attack_um=attack, early_rate_um_yr=early, Eb_mV=eb,
                    film_days=12 * (1.5 if fe_ss < 0.5 else 1.0))


def _retain(cool):
    """Share of the high-temperature beta kept as beta' martensite at a cooling rate (K/s), assumed logistic in
    log10 (half at about 200 K/s)."""
    return 1 / (1 + math.exp(-(math.log10(max(cool, 1.0)) - 2.3) / 0.35))


def reference_table(seed=0):
    from twin.spaces import REFERENCE
    t = CuTruth(seed)
    rng = np.random.default_rng(0)
    proc = dict(superheat_K=120, pour_mbar=220, amplitude=0.8, P_W=600, v_mm_min=600, feed_g_min=6)
    out = []
    for name, wt in REFERENCE["onr_cu"].items():
        comp = dict(wt)
        comp["Cu"] = 100 - sum(wt.values())
        lot = t.atomize(comp, proc, t.thermo(comp)["liquidus_C"], rng)
        part = t.deposit(lot, proc, "blown_large", rng)
        s, cr = t.strength(part), t.corrosion(part)
        out.append(dict(alloy=name, ys=round(s["ys_MPa"]), el=round(s["el_pct"], 1), rel_density=round(part["rel_density"], 4),
                        crack=round(part["crack_density"], 3), beta_prime=round(part["beta_prime"], 3),
                        rate=round(cr["rate_um_yr"], 1), attack=round(cr["attack_um"], 1),
                        early=round(cr["early_rate_um_yr"], 1), cool=round(part["cooling_K_s"]),
                        ratio=round(part["energy_ratio"], 2), catch=round(part["catchment"], 2)))
    return out

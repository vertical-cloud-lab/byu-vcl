"""Powder reuse: what a build (LPBF) or a deposit (DED) gives back to the lot, and in what state.

The campaign can print many times from one atomizer lot only if the powder it did not fuse comes back. These two
closed forms say how much comes back and how it has changed, so a policy can trade powder against quality. Both take
the campaign's lot-truth dict and return ``(grams_back, new_state)``: the state of the RETURNED powder only (a full
lot-like copy; the engine blends it by mass with the powder that never left the lot). The input is not mutated.

**LPBF** (``after_build``; magnitudes from AlSi10Mg reuse studies, coefficients assumed):

* *How much returns.* The unfused powder (spread - fused) is sieved through the cut's top sieve. Losses: machine
  dead volume, overflow and sieve hang-up 3 % (assumed); fines taken by the gas flow and the sieve (half the < 20 um
  share plus 0.5 %); partially sintered powder from the tracks' halo (0.3 g per g fused, 90 % of it caught as
  oversize). That gives the 85-95 % recovery the industry quotes; it is clipped to that range.
* *Oxygen.* Two sources (Raza et al., *Degradation of AlSi10Mg powder during laser based powder bed fusion
  processing*, Mater. Des. 198, 2021, https://research.chalmers.se/publication/521110/file/521110_Fulltext.pdf: the
  oxide on reused powder grew to about 38 nm over 30 months of production; spatter carries thick oxide):
  (a) the bed's own oxide grows about 0.5 nm a build at a 150 degC plate (assumed from that rate, taking about 70
  builds in the 30 months; Arrhenius-like
  factor exp((T0 - 150) / 80)), which is 6 delta / d x (rho_oxide / rho_metal) x the oxide's oxygen mass fraction
  (Al2O3 0.47, Cu2O 0.11); (b) spatter (3 % of the fused mass at 60 J/mm3, rising as sqrt(E/60), assumed; half lands
  in the bed, 40 % of that passes the sieve) carrying 6000 ppm O (Al) or 3000 ppm (Cu) (assumed). A 45 um AlSi10Mg
  powder then gains about 50 ppm a build, half again over ten builds and double over about twenty, the order of the
  rise Slotwinski et al. ("almost double") and Weiss et al. (oxygen up over 10 cycles) report (cited in Fiegl et
  al., *Effect of AlSi10Mg0.4 long-term reused powder in PBF-LB/M on the mechanical properties*, Mater. Des. 212,
  2021, https://research.chalmers.se/en/publication/526911, who also found porosity x4 and strength -15 % for
  long-term reused powder).
* *Shape and size.* Handling knocks off 3 % of the satellites, spatter and sintered necks add 0.6 % x E/60 (assumed).
  The fines lost and the spatter kept move d50 up about 1 % a build and narrow the distribution (gsd -0.4 %),
  as Cordova, Campos & Tinga report for reused AlSi10Mg, Ti-6Al-4V and IN718 (*Revealing the effects of powder reuse
  for selective laser melting by powder characterization*, JOM 71, 2019,
  https://link.springer.com/article/10.1007/s11837-018-3305-2); spatter kept is tracked as ``spatter_frac``, which
  ``psd.measure`` shows as a coarse mode. Del Re et al. (Int. J. Adv. Manuf. Technol. 97, 2018) saw tensile
  properties fall over 8 reuses: the twin carries that through oxygen and satellites into the truth's gas porosity.
* Composition is unchanged (the Mg and Zn that boil off leave with the fused tracks and the spatter; assumed).

**DED** (``after_ded``; Terrassa, Haley, MacDonald & Schoenung, *Reuse of powder feedstock for directed energy
deposition*, Powder Technol. 338, 2018, https://www.osti.gov/pages/biblio/1693671: most fed powder is not caught;
reused powder has more agglomerates and non-spherical particles and the spherical ones fewer satellites):

* *How much returns.* The overspray is grams_fed x (1 - catchment). 65 % of it is swept up from the chamber
  (assumed; blown powder scatters into corners and onto the part) and sieved back to the 45-150 um cut, which
  removes the agglomerates and partly melted particles (> 150 um) and the fines (8 % of the swept powder in all,
  assumed).
* *Oxygen.* The DED heads run under a local argon shroud, so the overspray that crossed the beam or the plume
  (10 % x P / 600 W, assumed) comes back with an oxide shell (2000 ppm Cu, 4000 ppm Al, assumed), half of it
  removed with the agglomerates; handling in air adds 20 ppm (assumed). Carbon has no source here and is carried.
* *Shape and size.* Satellites: x 0.9 (knocked off) + 0.03 x the heated share / 0.1 (assumed); sieving to the cut
  moves d50 up about 2 % and narrows the gsd 1 % (assumed); 0.5 % spatter kept.
"""
from __future__ import annotations

import copy
import math

import numpy as np

from twin.physics import lognorm_frac

CUTS = {"flaime_al": (20.0, 63.0), "onr_cu": (45.0, 150.0)}
OXIDE = {"flaime_al": dict(rho_ox=3.95, rho_m=2.68, o_frac=0.47, spatter_ppm=6000.0, shell_ppm=4000.0),
         "onr_cu": dict(rho_ox=6.0, rho_m=8.7, o_frac=0.112, spatter_ppm=3000.0, shell_ppm=2000.0)}


def _campaign(state):
    c = state.get("campaign")
    if c in CUTS:
        return c
    comp = state.get("composition") or {}
    return "onr_cu" if comp.get("Cu", 0) > 50 else "flaime_al"


def _d50(state):
    runs = [r for r in state.get("runs") or [] if not r.get("failed")]
    if runs:
        w = np.array([r.get("charge_g", 1.0) * r.get("usable_frac", 1.0) for r in runs], float)
        w = w / w.sum() if w.sum() > 0 else np.ones(len(runs)) / len(runs)
        return float(math.exp(sum(wi * math.log(r["d50_um"]) for wi, r in zip(w, runs))))
    d = state.get("d50_um")
    return float(d) if d is not None and np.isfinite(d) else 40.0


def _resize(state, campaign, dln_d50, dln_gsd):
    """Shift every run's (and the top-level) d50 and gsd, and recompute the shares the truth keeps per run."""
    lo, hi = CUTS[campaign]
    for r in state.get("runs") or []:
        r["d50_um"] = float(r["d50_um"]) * math.exp(dln_d50)
        r["gsd"] = max(float(r.get("gsd", 1.6)) * math.exp(dln_gsd), 1.05)
        r["fines_frac"] = lognorm_frac(r["d50_um"], r["gsd"], 0.0, 20.0)
        r["cut_frac"] = lognorm_frac(r["d50_um"], r["gsd"], lo, hi)
    if state.get("d50_um") is not None and np.isfinite(state["d50_um"]):
        state["d50_um"] = float(state["d50_um"]) * math.exp(dln_d50)
    state["gsd"] = max(float(state.get("gsd", 1.8 if not state.get("runs") else 1.6)) * math.exp(dln_gsd), 1.05)


def _fines(state, campaign):
    runs = [r for r in state.get("runs") or [] if not r.get("failed")]
    if runs:
        return float(np.mean([r.get("fines_frac", 0.0) for r in runs]))
    return lognorm_frac(_d50(state), float(state.get("gsd", 1.8)), 0.0, 20.0)


def after_build(lot_state: dict, grams_spread: float, grams_fused: float, process: dict, rng) -> tuple:
    """LPBF: (grams of powder back to the lot, the returned powder's state). See the module docstring."""
    st = copy.deepcopy(lot_state)
    campaign = _campaign(st)
    ox = OXIDE[campaign]
    process = process or {}
    spread, fused = max(float(grams_spread), 0.0), max(float(grams_fused), 0.0)
    fused = min(fused, spread)
    unfused = spread - fused
    if unfused <= 0:
        st["reuse"] = st.get("reuse", 0) + 1
        return 0.0, st
    try:
        Ev = process["P_W"] / (process["v_mm_s"] * process["h_um"] * 1e-3 * process["t_um"] * 1e-3)
    except (KeyError, TypeError, ZeroDivisionError):
        Ev = 60.0
    e = max(Ev / 60.0, 0.1)
    T0 = float(process.get("T0_C", 150.0))
    fines = _fines(st, campaign)
    # mass
    handling = 0.03 * math.exp(rng.normal(0, 0.2))
    fines_lost = 0.5 * fines + 0.005
    halo = min(0.3 * fused / unfused, 0.3) * 0.9
    spatter_bed = 0.03 * math.sqrt(e) * fused * 0.5
    spatter_kept = 0.4 * spatter_bed
    back = unfused * (1 - handling - fines_lost - halo) + spatter_kept
    back = float(np.clip(back, 0.85 * unfused, 0.95 * unfused))
    # oxygen: bulk oxide growth + spatter mixed back
    d_m = _d50(st) * 1e-6
    ddelta = 0.5e-9 * math.exp((T0 - 150.0) / 80.0) * math.exp(rng.normal(0, 0.15))
    dO_bulk = 6 * ddelta / d_m * ox["rho_ox"] / ox["rho_m"] * ox["o_frac"] * 1e6
    sp_share = spatter_kept / back
    O0 = float(st.get("oxygen_ppm", 500.0) or 500.0)
    st["oxygen_ppm"] = (O0 + dO_bulk) * (1 - sp_share) + ox["spatter_ppm"] * sp_share
    sat = float(st.get("satellite_frac", 0.05) or 0.05)
    st["satellite_frac"] = float(min(sat * 0.97 + 0.006 * e, 0.8))
    sp0 = float(st.get("spatter_frac", 0.0) or 0.0)
    st["spatter_frac"] = float(min(sp0 * 0.6 + sp_share, 0.2))          # the sieve takes 40 % of the old spatter
    _resize(st, campaign, 0.012 * (1 + fines_lost * 5), -0.004)
    st["reuse"] = st.get("reuse", 0) + 1
    st["reuse_history"] = list(st.get("reuse_history", [])) + [dict(kind="lpbf", spread_g=spread, fused_g=fused,
                                                                   back_g=back, dO_ppm=st["oxygen_ppm"] - O0)]
    return back, st


def after_ded(lot_state: dict, grams_fed: float, catchment: float, process: dict, rng) -> tuple:
    """DED: (grams of overspray back to the lot after sweeping and sieving, its state). ``catchment`` is the share
    of the fed powder the melt pool caught (``truth_cu.CuTruth.deposit``'s ``catchment``)."""
    st = copy.deepcopy(lot_state)
    campaign = _campaign(st)
    ox = OXIDE[campaign]
    process = process or {}
    fed = max(float(grams_fed), 0.0)
    catch = float(np.clip(catchment, 0.0, 1.0))
    over = fed * (1 - catch)
    swept = over * float(np.clip(0.65 * math.exp(rng.normal(0, 0.08)), 0.4, 0.85))
    back = swept * (1 - 0.08 * math.exp(rng.normal(0, 0.2)))
    P = float(process.get("P_W", 600.0))
    heated = float(np.clip(0.10 * P / 600.0, 0.0, 0.4))
    O0 = float(st.get("oxygen_ppm", 300.0) or 300.0)
    st["oxygen_ppm"] = O0 * (1 - 0.5 * heated) + 0.5 * heated * ox["shell_ppm"] + 20.0 * math.exp(rng.normal(0, 0.2))
    if st["oxygen_ppm"] < O0:                       # a lot already above the shell's level only gains the handling
        st["oxygen_ppm"] = O0 + 20.0
    sat = float(st.get("satellite_frac", 0.05) or 0.05)
    st["satellite_frac"] = float(min(sat * 0.9 + 0.03 * heated / 0.1, 0.8))
    st["spatter_frac"] = float(min(float(st.get("spatter_frac", 0.0) or 0.0) * 0.5 + 0.005, 0.2))
    st["carbon_ppm"] = float(st.get("carbon_ppm", 0.0) or 0.0)
    _resize(st, campaign, 0.02, -0.01)
    st["reuse"] = st.get("reuse", 0) + 1
    st["reuse_history"] = list(st.get("reuse_history", [])) + [dict(kind="ded", fed_g=fed, catchment=catch,
                                                                   back_g=back, dO_ppm=st["oxygen_ppm"] - O0)]
    return back, st


# ------------------------------------------------------------------------------------------------ figure
def _demo_lot(campaign):
    al = campaign == "flaime_al"
    d50, g = (45.0, 1.6) if al else (75.0, 1.6)
    lo, hi = CUTS[campaign]
    run = dict(d50_um=d50, gsd=g, usable_frac=0.91, failed=False, charge_g=300.0 if al else 800.0,
               cut_frac=lognorm_frac(d50, g, lo, hi), fines_frac=lognorm_frac(d50, g, 0, 20.0))
    return dict(campaign=campaign, composition={"Al": 89.65, "Si": 10.0, "Mg": 0.35} if al else
                {"Cu": 68.8, "Ni": 30.0, "Fe": 0.6, "Mn": 0.6}, oxygen_ppm=900.0 if al else 300.0,
                satellite_frac=0.07, carbon_ppm=0.0 if al else 40.0, runs=[run], reuse=0)


def cycles(campaign, n=10, rng=None):
    """n reuse cycles of a demonstration lot: LPBF builds for Al (440 g spread, 30 g fused), DED for Cu (450 g fed,
    catchment 0.6). Returns per-cycle oxygen, d50, satellites and grams back."""
    rng = np.random.default_rng(0) if rng is None else rng
    st = _demo_lot(campaign)
    rows = [dict(cycle=0, oxygen_ppm=st["oxygen_ppm"], d50_um=_d50(st), satellite_frac=st["satellite_frac"], back_g=None)]
    for i in range(n):
        if campaign == "flaime_al":
            back, st = after_build(st, 440.0, 30.0, dict(P_W=300, v_mm_s=1000, h_um=110, t_um=30, T0_C=150), rng)
        else:
            back, st = after_ded(st, 450.0, 0.6, dict(P_W=600, v_mm_min=600, feed_g_min=6), rng)
        rows.append(dict(cycle=i + 1, oxygen_ppm=st["oxygen_ppm"], d50_um=_d50(st), satellite_frac=st["satellite_frac"],
                         back_g=back))
    return rows


def draw(axs, n=10):
    """Two axes: oxygen vs reuse cycle; d50 (relative) and satellites vs cycle, for an AlSi10Mg-like lot (LPBF) and
    a 70-30 Cu-Ni lot (DED)."""
    for campaign, col, lab in (("flaime_al", "#e76f51", "AlSi10Mg, LPBF"), ("onr_cu", "#2a9d8f", "70-30 Cu-Ni, DED")):
        rows = cycles(campaign, n)
        c = [r["cycle"] for r in rows]
        axs[0].plot(c, [r["oxygen_ppm"] for r in rows], "o-", color=col, label=lab, ms=3)
        axs[1].plot(c, [r["d50_um"] / rows[0]["d50_um"] for r in rows], "o-", color=col, ms=3, label=f"{lab}: d50")
        axs[1].plot(c, [r["satellite_frac"] / rows[0]["satellite_frac"] for r in rows], "s--", color=col, ms=3,
                    label=f"{lab}: satellites")
    axs[0].set_xlabel("reuse cycle")
    axs[0].set_ylabel("oxygen (ppm)")
    axs[0].legend(fontsize=7, frameon=False)
    axs[1].set_xlabel("reuse cycle")
    axs[1].set_ylabel("relative to virgin")
    axs[1].legend(fontsize=6, frameon=False)

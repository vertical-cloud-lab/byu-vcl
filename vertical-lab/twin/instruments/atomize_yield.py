"""The atomizer's mass balance as the lab weighs it, the sieving into the campaign's cut, and the crucible choice.

**Measured per run** (``measure``; the AMAZEMET rePOWDER runs of a lot, ``sample['runs']``): the charge is weighed
(0.01 g top-loading balance, assumed; plus 0.01 % calibration error), the powder is taken from the collection
container through a 250 um scalping sieve (the lab's "usable", DAL #219: 91 % of the Oct 27 bronze charge) and
weighed in its jar, less what stays in the container and on the brush (0.3 +- 0.15 % of it, assumed). What did not
become usable powder is where the truth leaves it, partitioned as the lab finds it (all shares assumed, anchored on
DAL #219 and the SOP's "slag out" step): the heel and skull in the crucible (the floor cone and wall film, 2.5 cm3
in the 225 cm3 crucible and 3.5 cm3 in the 400, plus a dross skin of 1.0 % of the charge for Al and 0.5 % for Cu),
then the rest split 30 % oversize (> 250 um spheres and flakes), 35 % splat on the plate and chamber, 10 % fines
carried to the filter, 25 % unaccounted (oxide, chamber dust, vapour), each share varying 20 % run to run. A failed
run (a drip or a frozen nozzle, as ``twin/physics.py`` decides) leaves 70 % of its charge as a skull and 30 % as a
blob on the plate, and no usable powder.

**Sieving into the cut** (20-63 um for Al LPBF, 45-150 um for Cu DED): the lot's usable powder, as it lies on the
sieve (satellites attached, part of the agglomerates intact: ``psd.detected_classes`` at 0.5 bar equivalent), goes
through a two-sieve stack in batches (150 g Al, 500 g Cu, assumed) for ``sieve_min`` (20 min Al, 15 min Cu). Passage
per presentation for a sphere of diameter d through a square aperture a with wire w is ((a - d) / (a + w))^2
(Gaudin, *Principles of Mineral Dressing*, 1939), averaged over the aperture tolerance of ISO 3310-1 (SD 5 % of a,
assumed); 200 presentations a minute (assumed) slowed by bed depth (1 / (1 + m / m_ref), m_ref 100 g Al, 300 g Cu) and
by blinding, which closes the open area with a time constant of 60 min / (1 + 10 f_near) where f_near is the share
within 15 % of the aperture (assumed). The 20 um sieve for Al needs air-jet or ultrasonic help and still passes only
80 % of what it would (cohesive fines; assumed). Wires: ISO 3310-1 nominal (63 um: 45 um wire; 20 um: 20 um; 45 um:
32 um; 150 um: 100 um). 0.4 % of the feed hangs up in the meshes and is lost (assumed). Standards: ASTM B214 (sieve
analysis of metal powders), ISO 2591-1 (test sieving), ISO 3310-1 (test sieves).

Fidelity: ``full`` (90 size classes, the sieving-time curve and a per-run mass table in ``raw``), ``lite`` (40 classes),
``fast`` (charge weighed exactly as in the chain; collected and cut as the truth's sums times log-normal factors whose
mean is linear in the lot's state (cut share, gsd, d50 against the top aperture, satellites), fitted by
``calibrate`` on the lite chain; built-in defaults until ``calib_mech.json`` has a ``yield`` section).

**Crucibles** (``crucible_options``, ``charge_plan``): the rePOWDER's standard 225 cm3 graphite crucible (57.1 mm bore,
88 mm deep in the lab's model) and the 400 cm3 upgrade (DAL #219; 70 mm bore and 104 mm deep assumed). Fill styles:
``cups``, four 2.5 in cups round the sealing rod holding about 59 cm3 of metal in the 225 (notes/alloy_charge.md; the
lab's Al-10Si cup runs are 157-180 g), six in the wider 400 (assumed); ``rod``, rod pieces to 63 % of the crucible's
volume, as the Oct 27 run put 1,080 g of bronze (142.5 cm3) in the 225 as four rod pieces (DAL #219, PR 230). Melt-down
is a 25 K/min ramp (graphite thermal-shock limit, assumed), a 10 min soak plus 2 min per 100 cm3 and the charge's
sensible and latent heat at 2 kW net (assumed); the pour is Bernoulli flow through the 0.6 mm nozzle under the pour
pressure plus the melt's head; cool-down to opening is Newtonian (tau 35 min, scaled with the thermal mass^(1/3),
assumed). A taller, wider melt is less uniform (axial 4 K (Al) or 6 K (Cu) x (h / 56 mm)^2 plus radial 1.5 or 2 K x
(r / 28.55 mm)^2, assumed), so the nozzle sees a superheat lower by half that spread; that and the longer pour (half the
drip hazard taken as per unit pour time, assumed) give ``p_fail_add``, using ``twin/physics.py``'s failure law.
Consumables use ``twin/supply.py``'s item keys and the campaign's per-run rates; the 400 cm3 crucible costs about
$700 against the 225's $450 (assumed), so it is charged as 1.56 ``graphite_crucible`` units per crucible life.
"""
from __future__ import annotations

import math

import numpy as np

from twin.instruments import psd

CUTS = psd.CUTS
DEFAULT_CHARGE = {"flaime_al": 300.0, "onr_cu": 800.0}
RHO_SOLID = {"flaime_al": 2.68, "onr_cu": 8.7}         # g/cm3 defaults (alloy from composition when given)
RHO_LIQ = {"flaime_al": 2.37, "onr_cu": 7.9}           # g/cm3 (twin/physics.py LIQ_DENSITY)
WIRE_UM = {20.0: 20.0, 45.0: 32.0, 63.0: 45.0, 150.0: 100.0}   # ISO 3310-1 nominal wire diameters
SIEVE_MIN = {"flaime_al": 20.0, "onr_cu": 15.0}
BATCH_G = {"flaime_al": 150.0, "onr_cu": 500.0}
M_REF = {"flaime_al": 100.0, "onr_cu": 300.0}
PARTITION = dict(oversize=0.30, splat=0.35, filter=0.10, unaccounted=0.25)   # of the non-usable rest (assumed)
OUT = ("charge_g", "collected_g", "yield_frac", "cut_g", "cut_yield_frac")

SPEC = dict(station="sieve", instrument="balance (0.01 g) + sieve shaker (Al: air-jet for 20 um)", hours=0.75,
            consumables={}, note="weighing in the atomizer's own run time; sieving 0.75 h a lot (campaign route)")

CRUCIBLES = {
    225: dict(name="standard 225 cm3 graphite crucible", volume_cm3=225.0, bore_mm=57.1, depth_mm=88.0,
              heel_cm3=2.5, cups=4, price_usd=450.0, source="AMAZEMET rePOWDER standard; DAL #219; model bore"),
    400: dict(name="400 cm3 upgrade crucible", volume_cm3=400.0, bore_mm=70.0, depth_mm=104.0, heel_cm3=3.5,
              cups=6, price_usd=700.0, source="DAL #219 (upgrade discussed); bore, depth, cups and price assumed"),
}
CUP_METAL_CM3 = 59.0 / 4                               # one 2.5 in cup's metal (notes/alloy_charge.md)
ROD_FILL = 142.5 / 225.0                               # Oct 27: 142.5 cm3 of bronze in the 225 (DAL #219)
# per-run consumables the campaign charges now (twin/campaign.py), in twin/supply.py units
RUN_CONS = {"flaime_al": {"argon": 0.07, "cc_plate": 1 / 5, "graphite_crucible": 1 / 12, "bn_spray": 1 / 300},
            "onr_cu": {"argon": 0.16, "cc_plate": 1.0, "bn_nozzle": 1.0, "graphite_crucible": 1 / 6,
                       "bn_spray": 1 / 300}}


# ------------------------------------------------------------------------------------------------ crucible planning
def crucible_options() -> dict:
    return {k: dict(v) for k, v in CRUCIBLES.items()}


def _p_fail(superheat_K, pour_mbar):
    """twin/physics.py's failure law (without the Cu > 1300 degC wear term)."""
    return 0.06 + 0.55 / (1 + math.exp((superheat_K - 70.0) / 14.0)) + 0.15 / (1 + math.exp(-(pour_mbar - 340) / 25))


def charge_plan(campaign, crucible_cm3=225, fill=None, comp=None, superheat_K=None, pour_mbar=None,
                liquidus_C=None) -> dict:
    """Charge per run, run time, heel, melt uniformity, extra failure risk and consumables for a crucible and fill.

    ``fill``: 'cups' or 'rod' (None: the campaign's default, cups for Al as the lab's Al-10Si runs, rod pieces for Cu
    as the Oct 27 NAB run). ``comp`` (wt%) sets the alloy's density; superheat, pour and liquidus default to the
    reference process points."""
    if int(crucible_cm3) not in CRUCIBLES:
        raise ValueError("crucible_cm3 must be 225 or 400")
    cr = CRUCIBLES[int(crucible_cm3)]
    al = campaign == "flaime_al"
    fill = fill or ("cups" if al else "rod")
    if comp:
        from twin.physics import density
        rho = density({k: v for k, v in comp.items() if v > 0})
    else:
        rho = RHO_SOLID[campaign]
    rho_l = RHO_LIQ[campaign] * rho / RHO_SOLID[campaign]
    if fill == "cups":
        metal_cm3, pieces = cr["cups"] * CUP_METAL_CM3, cr["cups"]
    elif fill == "rod":
        metal_cm3, pieces = ROD_FILL * cr["volume_cm3"], 4 if crucible_cm3 == 225 else 6
    else:
        raise ValueError("fill must be 'cups' or 'rod'")
    charge = metal_cm3 * rho
    melt_cm3 = charge / rho_l
    r_cm = cr["bore_mm"] / 20.0
    h_mm = melt_cm3 / (math.pi * r_cm ** 2) * 10.0
    sh = superheat_K if superheat_K is not None else (150.0 if al else 120.0)
    pour = pour_mbar if pour_mbar is not None else (200.0 if al else 220.0)
    TL = liquidus_C if liquidus_C is not None else (600.0 if al else 1080.0)
    T = TL + sh
    # melt-down: ramp, soak, the charge's heat at 2 kW net (cp 1.1 / 0.45 J/gK, L 397 / 205 J/g)
    cp, Lh = (1.1, 397.0) if al else (0.45, 205.0)
    ramp_min = (T - 25.0) / 25.0
    soak_min = 10.0 + 2.0 * melt_cm3 / 100.0
    heat_min = charge * (cp * (T - 25.0) + Lh) / 2000.0 / 60.0
    head_mbar = rho_l * 1000 * 9.81 * (h_mm / 2000.0) / 100.0              # mean head over the drain
    v = math.sqrt(2 * (pour + head_mbar) * 100.0 / (rho_l * 1000))
    q_cm3_s = 0.8 * math.pi * (0.3e-3) ** 2 * v * 1e6
    pour_s = melt_cm3 / q_cm3_s
    thermal = (charge + 600.0 * cr["volume_cm3"] / 225.0) / (172.0 + 600.0)     # charge + crucible (600 g, assumed)
    cool_min = 35.0 * thermal ** (1 / 3) * math.log((T - 25.0) / 175.0)
    run_min = 9 + 21 + ramp_min + soak_min + heat_min + pour_s / 60 + cool_min + 10
    heel_g = cr["heel_cm3"] * rho_l + (0.010 if al else 0.005) * charge
    dT = ((4.0 if al else 6.0) * (h_mm / 56.0) ** 2 + (1.5 if al else 2.0) * (r_cm / 2.855) ** 2)
    ref = charge_plan_ref(campaign, sh, pour)
    p0 = _p_fail(sh, pour)
    p_here = 0.5 * _p_fail(sh - dT / 2, pour + head_mbar) * (1 + pour_s / ref["pour_s"]) \
        if ref is not None else p0
    p_add = max(min(p_here, 0.95) - (ref["p"] if ref is not None else p0), 0.0)
    cons = dict(RUN_CONS[campaign])
    if int(crucible_cm3) == 400:
        cons["graphite_crucible"] *= cr["price_usd"] / CRUCIBLES[225]["price_usd"]
    cons["argon"] *= run_min / (150.0 if al else 180.0)
    coarsen = (1 + 0.55 * (pour + head_mbar - 200) / 200) / (1 + 0.55 * (pour - 200) / 200)
    return dict(campaign=campaign, crucible_cm3=int(crucible_cm3), fill=fill, pieces=pieces, charge_g=charge,
                metal_cm3=metal_cm3, melt_cm3=melt_cm3, melt_height_mm=h_mm, fill_frac=melt_cm3 / cr["volume_cm3"],
                meltdown_min=ramp_min + soak_min + heat_min, pour_s=pour_s, cool_min=cool_min, run_h=run_min / 60.0,
                heel_g=heel_g, heel_frac=heel_g / charge, dT_melt_K=dT, head_mbar=head_mbar, d50_factor=coarsen,
                p_fail_add=p_add, consumables=cons,
                note=f"{cr['name']}, {fill}: {charge:.0f} g a run ({metal_cm3:.0f} cm3 of metal), melt {h_mm:.0f} mm "
                     f"deep, +-{dT / 2:.1f} K across it; {run_min / 60:.1f} h a run; prices and the 400's geometry "
                     f"assumed")


def charge_plan_ref(campaign, sh, pour):
    """The reference the extra risk is measured from: the 225 cm3 crucible in its default fill."""
    al = campaign == "flaime_al"
    cr = CRUCIBLES[225]
    rho_l = RHO_LIQ[campaign]
    metal = (cr["cups"] * CUP_METAL_CM3) if al else ROD_FILL * cr["volume_cm3"]
    melt = metal * RHO_SOLID[campaign] / rho_l
    r_cm = cr["bore_mm"] / 20.0
    h_mm = melt / (math.pi * r_cm ** 2) * 10.0
    head = rho_l * 1000 * 9.81 * (h_mm / 2000.0) / 100.0
    v = math.sqrt(2 * (pour + head) * 100.0 / (rho_l * 1000))
    pour_s = melt / (0.8 * math.pi * (0.3e-3) ** 2 * v * 1e6)
    dT = (4.0 if al else 6.0) * (h_mm / 56.0) ** 2 + (1.5 if al else 2.0)
    return dict(pour_s=pour_s, p=min(_p_fail(sh - dT / 2, pour + head), 0.95))


# ------------------------------------------------------------------------------------------------ the mass balance
def _run_balance(r, campaign, rng, crucible_cm3):
    al = campaign == "flaime_al"
    ch = float(r.get("charge_g", DEFAULT_CHARGE[campaign]))
    rho_l = RHO_LIQ[campaign]
    cr = CRUCIBLES[int(crucible_cm3)]
    if r.get("failed"):
        skull = 0.7 * ch * math.exp(rng.normal(0, 0.1))
        skull = min(skull, 0.95 * ch)
        return dict(charge_g=ch, usable_g=0.0, oversize_g=0.0, heel_g=skull, splat_g=ch - skull, filter_g=0.0,
                    unaccounted_g=0.0, failed=True)
    usable = ch * float(r["usable_frac"])
    rest = ch - usable
    heel = min(cr["heel_cm3"] * rho_l * math.exp(rng.normal(0, 0.15)) + (0.010 if al else 0.005) * ch, 0.6 * rest)
    w = {k: v * math.exp(rng.normal(0, 0.2)) for k, v in PARTITION.items()}
    tot = sum(w.values())
    left = rest - heel
    parts = {k: left * v / tot for k, v in w.items()}
    return dict(charge_g=ch, usable_g=usable, oversize_g=parts["oversize"], heel_g=heel, splat_g=parts["splat"],
                filter_g=parts["filter"], unaccounted_g=parts["unaccounted"], failed=False)


def _passage(d, a, wire, n_trials, eff=1.0):
    """Share of particles of diameter d (array) through aperture a after n_trials presentations (ISO 3310-1 spread)."""
    x = np.array([-2.02018, -0.958572, 0.0, 0.958572, 2.02018])          # Gauss-Hermite (probabilists'), 5 points
    wq = np.array([0.0199532, 0.393619, 0.945309, 0.393619, 0.0199532])
    wq = wq / wq.sum()
    out = np.zeros_like(d, dtype=float)
    for xi, wi in zip(x, wq):
        ak = a * (1 + 0.05 * xi)
        p = np.where(d < ak, ((ak - d) / (ak + wire)) ** 2, 0.0) * eff
        out += wi * (1 - (1 - np.clip(p, 0, 1)) ** n_trials)
    return out


def sieve(feed_g, v, edges, campaign, rng, minutes=None, curve=False, sub=8):
    """Split a feed (mass, volume share per size class between ``edges``) on the cut's two sieves. Each class is
    split into ``sub`` log-spaced slices so the apertures fall inside classes, not on their centres."""
    lo, hi = CUTS[campaign]
    le = np.log(edges)
    fine_e = np.exp(np.concatenate([np.linspace(le[i], le[i + 1], sub + 1)[:-1] for i in range(len(v))] + [le[-1:]]))
    d = np.sqrt(fine_e[:-1] * fine_e[1:])
    v = np.repeat(np.asarray(v, float) / sub, sub)
    minutes = SIEVE_MIN[campaign] if minutes is None else minutes
    n_batch = max(1, math.ceil(feed_g / BATCH_G[campaign]))
    m_b = feed_g / n_batch
    rate = 200.0 / (1 + m_b / M_REF[campaign]) * math.exp(rng.normal(0, 0.1))    # presentations a minute

    def eff_trials(a, t):
        near = float(v[(d > 0.85 * a) & (d < 1.15 * a)].sum())
        tau = 60.0 / (1 + 10 * near)
        return rate * tau * (1 - math.exp(-t / tau))

    eff_lo = 0.8 if campaign == "flaime_al" else 1.0

    def split(t):
        p_top = _passage(d, hi, WIRE_UM[hi], eff_trials(hi, t))
        through = v * p_top
        p_bot = _passage(d, lo, WIRE_UM[lo], eff_trials(lo, t), eff_lo)
        pan = through * p_bot
        return float((v - through).sum()), float((through - pan).sum()), float(pan.sum()), p_top, p_bot

    top, cut, pan, p_top, p_bot = split(minutes)
    loss = 0.004 * math.exp(rng.normal(0, 0.3))
    out = dict(top_frac=top * (1 - loss), cut_frac=cut * (1 - loss), pan_frac=pan * (1 - loss) + 0.0, loss_frac=loss,
               p_top=p_top, p_bot=p_bot, d_sieve_um=d, batches=n_batch, minutes=minutes)
    if curve:
        ts = np.linspace(0.5, 2 * minutes, 24)
        out["time_min"] = ts
        out["cut_vs_time"] = np.array([split(t)[1] * (1 - loss) for t in ts])
    return out


def _bal(rng, g):
    return g * (1 + rng.normal(0, 1e-4)) + rng.normal(0, 0.006)


def _true_sums(sample, campaign):
    runs = sample.get("runs") or []
    ch = sum(float(r.get("charge_g", DEFAULT_CHARGE[campaign])) for r in runs)
    good = [r for r in runs if not r.get("failed")]
    col = sum(float(r.get("charge_g", DEFAULT_CHARGE[campaign])) * r["usable_frac"] for r in good)
    cut = sum(float(r.get("charge_g", DEFAULT_CHARGE[campaign])) * r["usable_frac"] * r["cut_frac"] for r in good)
    return ch, col, cut


def _chain(sample, campaign, rng, fid, crucible_cm3=225, sieve_min=None):
    runs = sample.get("runs") or []
    table = [_run_balance(r, campaign, rng, crucible_cm3) for r in runs]
    charge_m = sum(_bal(rng, t["charge_g"]) for t in table)
    usable = sum(t["usable_g"] for t in table)
    left = 0.003 * usable * math.exp(rng.normal(0, 0.5)) if usable > 0 else 0.0
    collected = max(_bal(rng, usable - left), 0.0) if usable > 0 else max(rng.normal(0, 0.006), 0.0)
    out = dict(charge_g=charge_m, collected_g=collected, yield_frac=collected / charge_m if charge_m > 0 else 0.0)
    sv = None
    if collected > 0.5:
        edges, d, _ = psd._grid(fid)
        _vt, v, _dm, _sat = psd.detected_classes(sample, campaign, fid, pressure_bar=0.5)
        sv = sieve(collected, v, edges, campaign, rng, sieve_min, curve=(fid == "full"), sub=8 if fid == "lite" else 4)
        cut_g = max(_bal(rng, collected * sv["cut_frac"]), 0.0)
    else:
        cut_g = 0.0
    out.update(cut_g=cut_g, cut_yield_frac=cut_g / charge_m if charge_m > 0 else 0.0)
    if fid == "full":
        raw = dict(runs={k: [t[k] for t in table] for k in table[0]} if table else {}, left_in_container_g=left)
        if sv is not None:
            raw.update(sieve={k: (val.tolist() if isinstance(val, np.ndarray) else val) for k, val in sv.items()},
                       d_um=d, feed_v=v, cut=CUTS[campaign])
        out["raw"] = raw
    return out


# ------------------------------------------------------------------------------------------------ fast mode
_DEFAULT = {"flaime_al": dict(col=[-0.003, 0, 0, 0, 0], col_sd=0.0015, cut=[-0.03, 0.0, 0.0, 0.0, 0.0], cut_sd=0.02),
            "onr_cu": dict(col=[-0.003, 0, 0, 0, 0], col_sd=0.0015, cut=[-0.03, 0.0, 0.0, 0.0, 0.0], cut_sd=0.01)}


def _features(sample, campaign):
    tv = psd.true_values(sample, campaign)
    runs = psd.runs_of(sample, campaign)
    g = math.exp(math.sqrt(sum(w * math.log(gg) ** 2 for w, _, gg in runs)))
    return [1.0, tv["cut_frac"], math.log(g), math.log(tv["d50_um"] / CUTS[campaign][1]),
            float(sample.get("satellite_frac", 0.05) or 0.05)]


def _fast(sample, campaign, rng):
    from twin.instruments.mech import calib
    ch, col, cut = _true_sums(sample, campaign)
    n = len(sample.get("runs") or [])
    charge_m = ch * (1 + rng.normal(0, 1e-4)) + rng.normal(0, 0.006 * math.sqrt(max(n, 1)))
    if col <= 0:
        return dict(charge_g=charge_m, collected_g=0.0, yield_frac=0.0, cut_g=0.0, cut_yield_frac=0.0)
    c = calib("yield").get(campaign) or _DEFAULT[campaign]
    x = np.array(_features(sample, campaign))
    if "col2" in c:                         # two-level (between-lot table + within-lot spread), see calibrate()
        from twin.instruments.mech import two_level
        xc = np.clip(x[1:], c["x_min"], c["x_max"])
        mc, sc = two_level(c["col2"], xc)
        mk, sk = two_level(c["cut2"], xc)
        col_m = col * math.exp(mc + sc * rng.normal())
        cut_m = min(cut * math.exp(mk + sk * rng.normal()), col_m) if cut > 0 else 0.0
        return dict(charge_g=charge_m, collected_g=col_m, yield_frac=col_m / charge_m, cut_g=cut_m,
                    cut_yield_frac=cut_m / charge_m)
    if "x_mean" in c:                       # centred features, clipped to the range calibrated on
        x[1:] = np.clip(x[1:], c["x_min"], c["x_max"]) - np.array(c["x_mean"])
    col_m = col * math.exp(float(np.dot(c["col"], x)) + c["col_sd"] * rng.normal())
    cut_m = cut * math.exp(float(np.dot(c["cut"], x)) + c["cut_sd"] * rng.normal()) if cut > 0 else 0.0
    cut_m = min(cut_m, col_m)
    return dict(charge_g=charge_m, collected_g=col_m, yield_frac=col_m / charge_m, cut_g=cut_m,
                cut_yield_frac=cut_m / charge_m)


def measure(sample, campaign, rng, fidelity="fast", crucible_cm3=225, sieve_min=None, **kw):
    """charge_g collected_g yield_frac cut_g cut_yield_frac of a lot's atomizer runs (``full`` adds ``raw``). A lot
    with no runs (bought, gas-atomized) has no atomizer mass balance: {}."""
    if not sample.get("runs"):
        return {}
    if fidelity == "fast" and sieve_min is None:
        return _fast(sample, campaign, rng)
    return _chain(sample, campaign, rng, "full" if fidelity == "full" else "lite", crucible_cm3, sieve_min)


def calibrate(samples_by_campaign, rng, reps=4) -> dict:
    """Fit fast mode: ln(measured / truth's sum) of the collected and the cut mass, linear in the lot's state."""
    from twin.instruments.calibrate_mech import fit_two_level
    out = {}
    for campaign, pairs in samples_by_campaign.items():
        X, yc, yk, G = [], [], [], []
        for j, (lot, _part) in enumerate(pairs):
            ch, col, cut = _true_sums(lot, campaign)
            if col <= 0 or cut <= 0:
                continue
            x = _features(lot, campaign)
            for _ in range(reps):
                m = _chain(lot, campaign, rng, "lite")
                if m["cut_g"] <= 0:
                    continue
                X.append(x)
                G.append(j)
                yc.append(math.log(m["collected_g"] / col))
                yk.append(math.log(m["cut_g"] / cut))
        X = np.array(X)
        two = dict(col2=fit_two_level(X[:, 1:], np.array(yc), np.array(G)),
                   cut2=fit_two_level(X[:, 1:], np.array(yk), np.array(G)))
        xm, xlo, xhi = X[:, 1:].mean(0), X[:, 1:].min(0), X[:, 1:].max(0)
        X[:, 1:] -= xm
        bc = np.linalg.lstsq(X, np.array(yc), rcond=1e-6)[0]
        bk = np.linalg.lstsq(X, np.array(yk), rcond=1e-6)[0]
        out[campaign] = dict(col=bc.tolist(), col_sd=float(np.std(np.array(yc) - X @ bc)),
                             cut=bk.tolist(), cut_sd=float(np.std(np.array(yk) - X @ bk)), n=int(len(X)),
                             x_mean=xm.tolist(), x_min=xlo.tolist(), x_max=xhi.tolist(),
                             features="1 cut_frac ln_gsd ln(d50/cut_hi) sat",
                             mean_log_ratio=dict(collected=float(np.mean(yc)), cut=float(np.mean(yk))), **two)
    return {"yield": out}


# ------------------------------------------------------------------------------------------------ figures
COLORS = dict(usable_g="#2a9d8f", oversize_g="#e9c46a", heel_g="#6d597a", splat_g="#e76f51", filter_g="#90be6d",
              unaccounted_g="0.7")


def draw(res, axs):
    """Two axes: the per-run mass balance (stacked bars) and the sieve split of the usable powder."""
    raw = res["raw"]
    ax = axs[0]
    runs = raw["runs"]
    n = len(runs.get("charge_g", []))
    bottom = np.zeros(n)
    for k, col in COLORS.items():
        vals = np.array(runs[k])
        ax.bar(np.arange(n) + 1, vals, bottom=bottom, color=col, label=k.replace("_g", ""), width=0.7)
        bottom += vals
    for i, f in enumerate(runs.get("failed", [])):
        if f:
            ax.text(i + 1, bottom[i] * 1.01, "failed", ha="center", fontsize=7)
    ax.set_xlabel("run")
    ax.set_ylabel("mass (g)")
    ax.set_title(f"yield {100 * res['yield_frac']:.1f} % usable of {res['charge_g']:.0f} g", fontsize=8)
    ax.legend(fontsize=6, frameon=False, ncol=2)
    ax = axs[1]
    sv = raw.get("sieve")
    if sv:
        lo, hi = raw["cut"]
        fr = [sv["top_frac"], sv["cut_frac"], sv["pan_frac"], sv["loss_frac"]]
        labels = [f"> {hi:g} um", f"cut {lo:g}-{hi:g}", f"< {lo:g} um", "lost"]
        ax.bar(range(4), np.array(fr) * res["collected_g"], color=["#e9c46a", "#2a9d8f", "#90be6d", "0.7"])
        ax.set_xticks(range(4))
        ax.set_xticklabels(labels, fontsize=7)
        ax.set_ylabel("mass (g)")
        ax.set_title(f"cut {res['cut_g']:.0f} g ({100 * res['cut_yield_frac']:.1f} % of charge)", fontsize=8)
        if "time_min" in sv:
            ax2 = ax.inset_axes([0.62, 0.55, 0.35, 0.4])
            ax2.plot(sv["time_min"], np.array(sv["cut_vs_time"]) * res["collected_g"], color="#264653")
            ax2.axvline(sv["minutes"], color="0.5", ls=":", lw=0.8)
            ax2.set_xlabel("sieving (min)", fontsize=6)
            ax2.tick_params(labelsize=6)


def thumb(ax, res=None):
    """Icon: a charge bar split into powder (cut highlighted), heel and splat."""
    segs = [(0.18, "#2a9d8f"), (0.55, "#8ecae6"), (0.12, "#e9c46a"), (0.15, "#6d597a")]
    y = 0.0
    for h, c in segs:
        ax.bar(0.5, h, bottom=y, width=0.55, color=c, edgecolor="#264653", lw=5)
        y += h
    ax.plot([0.12, 0.12], [0, 1.0], color="#264653", lw=7, solid_capstyle="round")
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.02, 1.05)
    ax.set_axis_off()

"""Instrument simulators: what each of the vertical lab's instruments would report about a powder lot or a part.

Round 2 of the twin (PR 318, 2026-11-25): every characterization, synthesis and processing module the lab has is a
simulator that makes the raw data a real instrument makes (micrographs, spectra, patterns, curves) from the
artifact's hidden state, and then runs the analysis a lab would run on that raw data. The measured numbers carry the
errors, biases, detection limits and correlations that come from that chain, not a Gaussian added to the truth.

Contract, shared by ``twin/campaign.py`` and every module here::

    measure(name, sample, campaign, rng, fidelity="fast", **kw) -> dict

* ``name``: a key of ``INSTRUMENTS``.
* ``sample``: the truth's dict for the artifact. A powder lot is ``Campaign._lot_truth[lot]`` (composition, oxygen_ppm,
  satellite_frac, carbon_ppm, runs: the atomizer runs from ``truth.atomize``, each with d50_um, gsd, usable_frac,
  cut_frac, fines_frac, failed, composition, undissolved, T_melt_C, true_superheat_K, charge_g). A part is
  ``truth_al.AlTruth.build(...)`` or ``truth_cu.CuTruth.deposit(...)`` (composition, porosity, pores {lof, keyhole,
  gas}, rel_density, crack_density, grain_um, thermo, ... see those functions). The campaign adds ``campaign``
  ('flaime_al' | 'onr_cu'), ``design`` (the designed composition, wt%), ``strength`` (``truth.strength(part)``),
  ``strength_hot`` (Al, at 250 degC, when asked), ``corrosion`` (Cu, ``truth.corrosion(part)``), ``oxygen_ppm`` and
  ``satellite_frac`` of the lot it came from, and ``reuse`` (how many builds its powder has been through).
* ``fidelity``: ``"fast"`` (the analysis errors sampled from distributions calibrated on the full chain; < 1 ms),
  ``"lite"`` (small raw data and the real analysis; < 30 ms), ``"full"`` (publication-size raw data and the real
  analysis; the result also has ``raw``).
* returns the measured scalars named in ``OUTPUTS``; a quantity the instrument cannot see for this sample is absent.

Each module also has ``SPEC`` (station, hours, consumables) that ``twin/facility.py`` and ``twin/econ.py`` use. Until
a module exists, ``_stub`` below stands in for it with plain noise, so the campaign always runs.
"""
from __future__ import annotations

import importlib
import math

import numpy as np

# name -> (module, function), and the outputs every implementation returns (when the sample allows)
INSTRUMENTS = {
    "yield": ("atomize_yield", "measure", "charge_g collected_g yield_frac cut_g cut_yield_frac"),
    "psd": ("psd", "measure", "d10_um d50_um d90_um span cut_frac fines_frac"),
    "sem_powder": ("sem", "measure_powder", "sphericity satellite_frac d50_img_um n_particles"),
    "eds": ("eds", "measure", "comp lod"),
    "xrf": ("xrf", "measure", "comp"),
    "icpms": ("icpms", "measure", "comp"),
    "xrd_powder": ("xrd", "measure_powder", "phases a_fcc_A solute_ss_wt crystallite_nm"),
    "density": ("density", "measure", "rel_density"),
    "sem_section": ("sem", "measure_section", "porosity pore_dmax_um crack_density lof_frac"),
    "ebsd": ("ebsd", "measure", "grain_um equiaxed_frac texture_mrd indexed_frac kam_deg beta_prime_frac"),
    "xrd_part": ("xrd", "measure_part", "phases a_fcc_A beta_prime_frac microstrain"),
    "pip": ("pip", "measure", "ys_MPa uts_MPa ue_pct"),
    "vickers": ("hardness", "measure_vickers", "hv"),
    "nanoindent": ("hardness", "measure_nanoindent", "H_GPa E_GPa"),
    "tensile": ("tensile", "measure", "ys_MPa uts_MPa el_pct n_bars"),
    "tensile_hot": ("tensile", "measure_hot", "ys_MPa uts_MPa el_pct n_bars"),
    "corrosion_screen": ("corrosion", "measure_screen",
                         "ocp_mV rp_ohm_cm2 icorr_uA_cm2 early_rate_um_yr Eb_mV Erp_mV rct_ohm_cm2"),
    "immersion": ("corrosion", "measure_immersion", "rate30_um_yr attack_um cu_ppb ni_ppb"),
}
OUTPUTS = {k: v[2].split() for k, v in INSTRUMENTS.items()}
_cache: dict = {}


def implementation(name: str):
    """The module's function if it exists, else the stub (and which one it is)."""
    if name in _cache:
        return _cache[name]
    mod, fn, _ = INSTRUMENTS[name]
    import os
    if os.environ.get("TWIN_INSTRUMENTS") == "stub":        # development: the plain stand-ins only
        _cache[name] = ((lambda s, c, r, fidelity="fast", _n=name, **kw: _stub(_n, s, c, r)), "stub")
        return _cache[name]
    try:
        f = getattr(importlib.import_module(f"twin.instruments.{mod}"), fn)
        src = mod
    except (ImportError, AttributeError):
        f, src = (lambda s, c, r, fidelity="fast", _n=name, **kw: _stub(_n, s, c, r)), "stub"
    _cache[name] = (f, src)
    return _cache[name]


def measure(name: str, sample: dict, campaign: str, rng, fidelity: str = "fast", **kw) -> dict:
    f, _ = implementation(name)
    return f(sample, campaign, rng, fidelity=fidelity, **kw)


# ------------------------------------------------------------------------------------------------- stand-ins
def _ln(rng, s):
    return math.exp(rng.normal(0, s))


def _stub(name, s, campaign, rng):
    al = campaign == "flaime_al"
    bal = "Al" if al else "Cu"
    if name == "yield":
        runs = [r for r in s.get("runs", [])]
        ch = sum(r.get("charge_g", 300.0 if al else 800.0) for r in runs) or 1.0
        good = [r for r in runs if not r.get("failed")]
        col = sum(r.get("charge_g", 300.0 if al else 800.0) * r["usable_frac"] for r in good)
        cut = sum(r.get("charge_g", 300.0 if al else 800.0) * r["usable_frac"] * r["cut_frac"] for r in good)
        return dict(charge_g=ch, collected_g=col + rng.normal(0, 0.05), yield_frac=col / ch, cut_g=cut,
                    cut_yield_frac=cut / ch)
    if name == "psd":
        d50 = s.get("d50_um", 60.0)
        return dict(d10_um=d50 * 0.55 * _ln(rng, 0.05), d50_um=d50 * _ln(rng, 0.03), d90_um=d50 * 1.8 * _ln(rng, 0.05),
                    span=1.3 * _ln(rng, 0.05), cut_frac=float(np.clip(s.get("cut_frac", 0.3) + rng.normal(0, 0.02), 0, 1)),
                    fines_frac=float(np.clip(s.get("fines_frac", 0.05) + rng.normal(0, 0.01), 0, 1)))
    if name == "sem_powder":
        return dict(sphericity=float(np.clip(0.92 - 0.5 * s.get("satellite_frac", 0.1) + rng.normal(0, 0.02), 0, 1)),
                    satellite_frac=float(np.clip(s.get("satellite_frac", 0.1) + rng.normal(0, 0.03), 0, 1)),
                    d50_img_um=s.get("d50_um", 60.0) * _ln(rng, 0.08), n_particles=300)
    if name in ("eds", "xrf", "icpms"):
        sd = dict(eds=0.08, xrf=0.04, icpms=0.02)[name]
        return dict(comp={e: v * _ln(rng, sd) for e, v in s["composition"].items() if e != bal and v > 0})
    if name == "xrd_powder":
        return dict(phases={}, a_fcc_A=(4.0496 if al else 3.615) + rng.normal(0, 2e-4), solute_ss_wt=None,
                    crystallite_nm=80.0 * _ln(rng, 0.2))
    if name == "density":
        return dict(rel_density=float(np.clip(s["rel_density"] + rng.normal(0, 0.002), 0, 1)))
    if name == "sem_section":
        cd = s.get("crack_density", 0.0) * _ln(rng, 0.2)
        return dict(porosity=max(s.get("porosity", 0.0) * _ln(rng, 0.25), 0.0), pore_dmax_um=60.0 * _ln(rng, 0.3),
                    crack_density=cd if cd > 0.02 else 0.0, lof_frac=0.5)
    if name == "ebsd":
        out = dict(grain_um=s.get("grain_um", 10.0) * _ln(rng, 0.1), equiaxed_frac=float(np.clip(
            s.get("equiaxed", 0.0) + rng.normal(0, 0.05), 0, 1)), texture_mrd=3.0 * _ln(rng, 0.2), indexed_frac=0.9,
            kam_deg=0.8 * _ln(rng, 0.2))
        if not al:
            out["beta_prime_frac"] = float(np.clip(s.get("beta_prime", 0.0) + rng.normal(0, 0.04), 0, 1))
        return out
    if name == "xrd_part":
        out = dict(phases={}, a_fcc_A=(4.0496 if al else 3.615) + rng.normal(0, 2e-4), microstrain=1e-3 * _ln(rng, 0.3))
        if not al:
            out["beta_prime_frac"] = float(np.clip(s.get("beta_prime", 0.0) + rng.normal(0, 0.03), 0, 1))
        return out
    if name == "pip":
        st = s["strength"]
        return dict(ys_MPa=st["ys_sound_MPa"] * (1 - 0.5 * s.get("porosity", 0)) * _ln(rng, 0.05),
                    uts_MPa=st["uts_MPa"] * _ln(rng, 0.04), ue_pct=max(st["el_pct"] * 0.6, 0.5) * _ln(rng, 0.25))
    if name == "vickers":
        st = s["strength"]
        return dict(hv=(st["ys_sound_MPa"] + st["uts_MPa"]) / 2 / 3.0 / 9.807 * 3 * _ln(rng, 0.04))
    if name == "nanoindent":
        st = s["strength"]
        return dict(H_GPa=st["ys_sound_MPa"] * 3.2e-3 * _ln(rng, 0.08), E_GPa=(70.0 if al else 130.0) * _ln(rng, 0.05))
    if name in ("tensile", "tensile_hot"):
        st = s["strength_hot"] if name == "tensile_hot" else s["strength"]
        return dict(ys_MPa=st["ys_MPa"] * _ln(rng, 0.04 / math.sqrt(3)), uts_MPa=st["uts_MPa"] * _ln(rng, 0.03 / math.sqrt(3)),
                    el_pct=st["el_pct"] * _ln(rng, 0.12 / math.sqrt(3)), n_bars=3)
    if name == "corrosion_screen":
        c = s["corrosion"]
        return dict(early_rate_um_yr=c["early_rate_um_yr"] * _ln(rng, 0.3), Eb_mV=c["Eb_mV"] + rng.normal(0, 30))
    if name == "immersion":
        c = s["corrosion"]
        r30 = c["rate_um_yr"] * (1 + 1.5 * math.exp(-30 / c["film_days"]))
        return dict(rate30_um_yr=r30 * _ln(rng, 0.12),
                    attack_um=max(c["attack_um"] * _ln(rng, 0.25) + rng.normal(0, 0.5), 0.0))
    raise KeyError(name)

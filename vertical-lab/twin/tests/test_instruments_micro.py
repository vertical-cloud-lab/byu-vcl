"""Checks of the microscopy, diffraction and chemistry simulators (twin/instruments: micro, xrd, sem, eds, ebsd, xrf,
icpms): the contract's outputs in every fidelity, fast vs lite agreement, timings, and reference-alloy sanity.

    nice -n 10 python -m pytest -q twin/tests/test_instruments_micro.py      # ~30-50 s
"""
from __future__ import annotations

import math
import time

import numpy as np
import pytest

from twin.instruments import OUTPUTS, implementation, measure, micro

MICRO = {"sem_powder": "powder", "eds": "powder", "xrf": "powder", "icpms": "powder", "xrd_powder": "powder",
         "sem_section": "part", "ebsd": "part", "xrd_part": "part"}
# outputs that are absent by design for a campaign (the instrument cannot see them in that alloy)
ABSENT_OK = {("ebsd", "flaime_al"): {"beta_prime_frac"}, ("xrd_part", "flaime_al"): {"beta_prime_frac"}}


@pytest.fixture(scope="module")
def G():
    return micro.gallery_samples()


def _sample(G, inst, camp, alloy):
    lot, part = G[camp][alloy]
    return lot if MICRO[inst] == "powder" else part


@pytest.mark.parametrize("inst", list(MICRO))
def test_implemented(inst):
    _, src = implementation(inst)
    assert src != "stub", f"{inst} still runs on the stub"


@pytest.mark.parametrize("inst", list(MICRO))
@pytest.mark.parametrize("camp,alloy", [("flaime_al", "AlSi10Mg"), ("onr_cu", "NAB")])
def test_outputs_all_fidelities(G, inst, camp, alloy):
    s = _sample(G, inst, camp, alloy)
    for fid in ("fast", "lite", "full"):
        r = measure(inst, s, camp, np.random.default_rng(1), fidelity=fid)
        need = set(OUTPUTS[inst]) - ABSENT_OK.get((inst, camp), set())
        missing = need - set(r)
        assert not missing, f"{inst} {camp} {fid}: missing {missing}"
        if fid == "full":
            assert "raw" in r, f"{inst} full has no raw data"
        else:
            assert "raw" not in r
        # deterministic given the rng
        r2 = measure(inst, s, camp, np.random.default_rng(1), fidelity=fid)
        for k in OUTPUTS[inst]:
            if isinstance(r.get(k), float):
                assert r[k] == r2[k], f"{inst} {fid} {k} not deterministic"


# fast vs lite: outputs compared, as (instrument, campaign, alloy, key, absolute tolerance floor)
PAIRS = [
    ("xrd_powder", "flaime_al", "AlSi10Mg", "a_fcc_A", 2e-4), ("xrd_part", "onr_cu", "NAB", "a_fcc_A", 2e-4),
    ("xrd_part", "onr_cu", "NAB", "beta_prime_frac", 0.02), ("xrd_part", "flaime_al", "AlSi10Mg", "phase.Si", 0.01),
    ("eds", "flaime_al", "AlSi10Mg", "comp.Si", 0.3), ("eds", "onr_cu", "NAB", "comp.Al", 0.3),
    ("eds", "onr_cu", "70-30 Cu-Ni", "comp.Ni", 0.6),
    ("xrf", "onr_cu", "70-30 Cu-Ni", "comp.Ni", 0.5), ("xrf", "flaime_al", "7075", "comp.Zn", 0.2),
    ("icpms", "onr_cu", "NAB", "comp.Fe", 0.1), ("icpms", "flaime_al", "AlSi10Mg", "comp.Si", 0.3),
    ("sem_powder", "flaime_al", "AlSi10Mg", "d50_img_um", 2.0), ("sem_powder", "onr_cu", "NAB", "sphericity", 0.02),
    ("sem_section", "flaime_al", "7075", "crack_density", 0.1), ("sem_section", "onr_cu", "NAB", "porosity", 0.004),
    ("ebsd", "flaime_al", "AlSi10Mg", "grain_um", 0.8), ("ebsd", "onr_cu", "NAB", "beta_prime_frac", 0.03),
    ("ebsd", "flaime_al", "Scalmalloy", "equiaxed_frac", 0.05),
]


def _get(r, key):
    if key.startswith("comp."):
        return r.get("comp", {}).get(key[5:])
    if key.startswith("phase."):
        return r.get("phases", {}).get(key[6:], 0.0)
    return r.get(key)


@pytest.mark.parametrize("inst,camp,alloy,key,tol", PAIRS)
def test_fast_matches_lite(G, inst, camp, alloy, key, tol):
    """Means over 40 draws agree within 3 standard errors plus a small floor (the fast mode is calibrated on the
    lite chain; both are measurements, so neither is the truth)."""
    s = _sample(G, inst, camp, alloy)
    n = 40
    vals = {}
    for fid in ("lite", "fast"):
        rng = np.random.default_rng(11)
        v = [_get(measure(inst, s, camp, rng, fidelity=fid), key) for _ in range(n)]
        vals[fid] = np.array([x for x in v if x is not None], float)
    L, F = vals["lite"], vals["fast"]
    assert len(L) >= n // 2 and len(F) >= n // 2, f"{inst} {key}: reported in lite {len(L)}, fast {len(F)} of {n}"
    se = math.sqrt(L.var() / len(L) + F.var() / len(F))
    assert abs(F.mean() - L.mean()) <= 3 * se + tol, \
        f"{inst} {alloy} {key}: lite {L.mean():.4g}+-{L.std():.3g}, fast {F.mean():.4g}+-{F.std():.3g}"
    # spreads within a factor of ~2.5 of each other (when lite has any spread)
    if L.std() > tol / 2:
        assert 0.4 < (F.std() + 1e-12) / L.std() < 2.5, f"{inst} {key}: sd lite {L.std():.3g} fast {F.std():.3g}"


@pytest.mark.parametrize("inst", list(MICRO))
def test_timings(G, inst):
    """CPU time per call: fast < 1 ms, lite < 30 ms (medians, so a loaded runner's stalls do not count)."""
    for camp, alloy in (("flaime_al", "AlSi10Mg"), ("onr_cu", "NAB")):
        s = _sample(G, inst, camp, alloy)
        rng = np.random.default_rng(2)
        for fid, lim, n in (("fast", 1e-3, 60), ("lite", 30e-3, 8)):
            measure(inst, s, camp, rng, fidelity=fid)          # warm caches
            t = []
            for _ in range(n):
                t0 = time.process_time()
                measure(inst, s, camp, rng, fidelity=fid)
                t.append(time.process_time() - t0)
            assert np.median(t) < lim, f"{inst} {camp} {fid}: {1e3 * np.median(t):.2f} ms"


def test_reference_alloys(G):
    rng = np.random.default_rng(5)
    # AlSi10Mg: Si is seen by XRD (powder and part), a_fcc near 4.05 A, EDS reads ~10 % Si
    lot, part = G["flaime_al"]["AlSi10Mg"]
    for f, s in (("xrd_powder", lot), ("xrd_part", part)):
        r = measure(f, s, "flaime_al", rng, fidelity="lite")
        assert r["phases"].get("Si", 0) > 0.04, r["phases"]
        assert abs(r["a_fcc_A"] - 4.05) < 0.01
    assert 8.0 < measure("eds", lot, "flaime_al", rng, fidelity="lite")["comp"]["Si"] < 12.0
    # Scalmalloy's Mg expands the lattice; 7075 cracks
    r = measure("xrd_part", G["flaime_al"]["Scalmalloy"][1], "flaime_al", rng, fidelity="lite")
    assert 4.052 < r["a_fcc_A"] < 4.07
    assert measure("sem_section", G["flaime_al"]["7075"][1], "flaime_al", rng, fidelity="lite")["crack_density"] > 0.3
    # Cu: 70-30 Cu-Ni near 3.588 A (Vegard), NAB shows beta' (and kappa) by XRD and beta' by EBSD (under-counted)
    r = measure("xrd_part", G["onr_cu"]["70-30 Cu-Ni"][1], "onr_cu", rng, fidelity="lite")
    assert abs(r["a_fcc_A"] - 3.588) < 0.004 and abs(r["a_fcc_A"] - 3.61) < 0.04
    nab = G["onr_cu"]["NAB"][1]
    r = measure("xrd_part", nab, "onr_cu", rng, fidelity="lite")
    assert r["beta_prime_frac"] > 0.1 and any(k.startswith("kappa") for k in r["phases"]), r["phases"]
    assert 3.62 < r["a_fcc_A"] < 3.66
    e = np.mean([measure("ebsd", nab, "onr_cu", rng, fidelity="lite")["beta_prime_frac"] for _ in range(6)])
    assert 0.03 < e < r["beta_prime_frac"] + 0.05
    # Li is invisible to EDS and XRF
    li = dict(lot, composition=dict(lot["composition"], Li=1.5, Al=lot["composition"]["Al"] - 1.5))
    assert "Li" not in measure("eds", li, "flaime_al", rng, fidelity="lite")["comp"]
    assert "Li" not in measure("xrf", li, "flaime_al", rng, fidelity="lite")["comp"]


def test_phase_model_balances(G):
    """The latent microstructure conserves mass and puts the matrix lattice where Vegard says."""
    for camp, alloys in G.items():
        for alloy, (lot, part) in alloys.items():
            for kind, s in (("powder", lot), ("part", part)):
                pm = micro.phase_model(s, camp, kind)
                assert abs(sum(p["wt"] for p in pm["phases"]) - 1) < 1e-9
                assert abs(sum(p["vol"] for p in pm["phases"]) - 1) < 1e-9
                for el, w in s["composition"].items():
                    if el == pm["base"] or w < 0.05:
                        continue
                    tot = sum(p["wt"] * p["comp"].get(el, 0.0) for p in pm["phases"]) * 100
                    assert abs(tot - w) < 0.25 * w + 0.1, f"{alloy} {kind} {el}: {tot:.3f} vs {w:.3f}"

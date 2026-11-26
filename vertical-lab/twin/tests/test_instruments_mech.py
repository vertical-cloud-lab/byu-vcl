"""Tests for the mechanical, powder and corrosion instrument simulators (twin/instruments/: mech, tensile, pip,
hardness, density, psd, atomize_yield, reuse, corrosion). Run from vertical-lab:

    nice -n 10 /tmp/venv/bin/python -m pytest -q twin/tests/test_instruments_mech.py
"""
from __future__ import annotations

import math
import time

import numpy as np
import pytest

from twin import instruments as ins
from twin.instruments import calibrate_mech as cm

MINE = ["yield", "psd", "density", "pip", "vickers", "nanoindent", "tensile", "tensile_hot", "corrosion_screen",
        "immersion"]
LOT_INSTR = {"yield", "psd"}


@pytest.fixture(scope="module")
def refs():
    return cm.reference_samples(seed=0)


def _sample(name, lot, part):
    return lot if name in LOT_INSTR else part


def _applies(name, part):
    if name in ("corrosion_screen", "immersion"):
        return part["campaign"] == "onr_cu"
    if name == "tensile_hot":
        return part.get("strength_hot") is not None
    return True


@pytest.mark.parametrize("name", MINE)
def test_implemented(name):
    f, src = ins.implementation(name)
    assert src != "stub", f"{name} still uses the stub"


@pytest.mark.parametrize("fidelity", ["fast", "lite", "full"])
@pytest.mark.parametrize("label", ["AlSi10Mg", "C95800 NAB"])
def test_output_keys(refs, label, fidelity):
    lot, part = refs[label]
    camp = part["campaign"]
    for name in MINE:
        rng = np.random.default_rng(1)
        r = ins.measure(name, _sample(name, lot, part), camp, rng, fidelity=fidelity, unknown_kw=1)
        if not _applies(name, part):
            assert not r or all(v is None for v in r.values()) or name == "tensile_hot"
            continue
        missing = [k for k in ins.OUTPUTS[name] if k not in r]
        assert not missing, f"{name} [{fidelity}] lacks {missing}"
        if fidelity == "full" and name not in ("density",):
            assert "raw" in r, f"{name} full has no raw"


@pytest.mark.parametrize("name", MINE)
def test_deterministic(refs, name):
    lot, part = refs["C95800 NAB"] if name in ("corrosion_screen", "immersion") else refs["AlSi10Mg"]
    s = _sample(name, lot, part)
    a = ins.measure(name, s, part["campaign"], np.random.default_rng(7), fidelity="lite")
    b = ins.measure(name, s, part["campaign"], np.random.default_rng(7), fidelity="lite")
    for k in ins.OUTPUTS[name]:
        if k in a and isinstance(a[k], (int, float)):
            assert a[k] == b[k], (name, k)


def _timed(name, s, camp, fidelity, n):
    """Median CPU time per call (process time, so a runner shared with other jobs does not fail the test)."""
    rng = np.random.default_rng(3)
    ins.measure(name, s, camp, rng, fidelity=fidelity)               # warm caches
    t = time.process_time()
    for _ in range(n):
        ins.measure(name, s, camp, rng, fidelity=fidelity)
    return (time.process_time() - t) / n


@pytest.mark.parametrize("name", MINE)
def test_timings(refs, name):
    lot, part = refs["C95800 NAB"] if name in ("corrosion_screen", "immersion") else refs["AlSi10Mg"]
    s = _sample(name, lot, part)
    t_fast = _timed(name, s, part["campaign"], "fast", 200)
    t_lite = _timed(name, s, part["campaign"], "lite", 10)
    assert t_fast < 1e-3, f"{name} fast {t_fast * 1e3:.2f} ms"
    assert t_lite < 30e-3, f"{name} lite {t_lite * 1e3:.1f} ms"


def _logs(name, s, camp, fidelity, key, n, seed):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        v = ins.measure(name, s, camp, rng, fidelity=fidelity).get(key)
        if isinstance(v, (int, float)) and v > 0:
            out.append(math.log(v))
    return np.array(out)


AGREE = [("tensile", "ys_MPa"), ("tensile", "uts_MPa"), ("tensile", "el_pct"), ("pip", "ys_MPa"), ("pip", "uts_MPa"),
         ("pip", "ue_pct"), ("vickers", "hv"), ("nanoindent", "H_GPa"), ("nanoindent", "E_GPa"),
         ("density", "rel_density"), ("psd", "d50_um"), ("psd", "cut_frac"), ("yield", "cut_g"),
         ("corrosion_screen", "early_rate_um_yr"), ("corrosion_screen", "Eb_mV"), ("immersion", "rate30_um_yr")]


@pytest.mark.parametrize("name,key", AGREE)
def test_fast_matches_lite(refs, name, key):
    """fast and lite agree statistically, including the state-dependent bias (sound and porous samples)."""
    labels = ["C71500 70-30 Cu-Ni", "C95800 NAB"] if name in ("corrosion_screen", "immersion") else \
        ["AlSi10Mg", "7075 porous, cracked", "C95800 NAB"]
    for lab in labels:
        lot, part = refs[lab]
        s = _sample(name, lot, part)
        if key == "Eb_mV":
            f = np.array([ins.measure(name, s, part["campaign"], np.random.default_rng(i), "fast").get(key, np.nan)
                          for i in range(60)])
            l = np.array([ins.measure(name, s, part["campaign"], np.random.default_rng(1000 + i), "lite").get(key, np.nan)
                          for i in range(30)])
            f, l = f[np.isfinite(f)], l[np.isfinite(l)]
            if len(l) < 5:
                continue
            se = math.sqrt(np.var(f) / len(f) + np.var(l) / len(l))
            assert abs(f.mean() - l.mean()) < 4 * se + 25, (lab, f.mean(), l.mean())
            continue
        f = _logs(name, s, part["campaign"], "fast", key, 60, 11)
        l = _logs(name, s, part["campaign"], "lite", key, 30, 12)
        if len(l) < 5 or len(f) < 5:
            continue
        se = math.sqrt(np.var(f) / len(f) + np.var(l) / len(l))
        tol = 4 * se + 0.04 + (0.10 if "porous" in lab else 0.0)
        assert abs(f.mean() - l.mean()) < tol, (lab, key, math.exp(f.mean()), math.exp(l.mean()))
        sf, sl = f.std(), l.std()
        if sl > 0.01 or sf > 0.01:
            assert 0.33 < (sf + 1e-3) / (sl + 1e-3) < 3.0, (lab, key, sf, sl)


# ------------------------------------------------------------------------------------------------- sanity
def test_alsi10mg_tensile_near_truth(refs):
    lot, part = refs["AlSi10Mg"]
    st = part["strength"]
    r = [ins.measure("tensile", part, "flaime_al", np.random.default_rng(i), "lite") for i in range(10)]
    ys = np.mean([x["ys_MPa"] for x in r])
    uts = np.mean([x["uts_MPa"] for x in r])
    el = np.mean([x["el_pct"] for x in r])
    assert abs(ys / st["ys_MPa"] - 1) < 0.03
    assert abs(uts / st["uts_MPa"] - 1) < 0.04
    assert abs(el / st["el_pct"] - 1) < 0.15
    assert all(x["n_bars"] == 3 for x in r)


def test_porous_bars_scatter_more_and_can_break_before_yield(refs):
    _, sound = refs["AlSi10Mg"]
    _, bad = refs["7075 porous, cracked"]
    cv = []
    noy = 0
    for part in (sound, bad):
        el = []
        for i in range(15):
            r = ins.measure("tensile", part, "flaime_al", np.random.default_rng(100 + i), "lite")
            el += r["bars"]["el_pct"]
            if part is bad:
                noy += sum(v is None for v in r["bars"]["ys_MPa"])
        el = np.array(el)
        cv.append(el.std() / max(el.mean(), 1e-6))
    assert cv[1] > cv[0]
    assert noy > 0, "a crack-dominated part should sometimes break before its 0.2 % offset"


@pytest.mark.parametrize("fidelity", ["lite", "fast"])
def test_pip_overreads_porous_part(refs, fidelity):
    _, bad = refs["7075 porous, cracked"]
    _, sound = refs["AlSi10Mg"]
    ratio = {}
    for lab, part in (("bad", bad), ("sound", sound)):
        p = np.mean([ins.measure("pip", part, "flaime_al", np.random.default_rng(i), fidelity)["ys_MPa"] for i in range(6)])
        t = np.mean([ins.measure("tensile", part, "flaime_al", np.random.default_rng(i), fidelity).get("ys_MPa", np.nan)
                     for i in range(6)])
        ratio[lab] = p / t
    assert ratio["bad"] > 1.4
    assert abs(ratio["sound"] - 1) < 0.12


def test_pip_ductility_is_uniform_not_fracture(refs):
    _, part = refs["C70600 90-10 Cu-Ni"]
    r = ins.measure("pip", part, "onr_cu", np.random.default_rng(0), "lite")
    assert r["ue_pct"] < part["strength"]["el_pct"]


def test_density_designed_reference_and_open_porosity(refs):
    from twin.instruments import density
    _, sc = refs["Scalmalloy"]          # Mg boiled off: denser than designed, reads high
    r = density.measure(sc, "flaime_al", np.random.default_rng(0), "lite")
    assert r["rel_density"] > 1 - sc["porosity"]
    _, bad = refs["7075 porous, cracked"]
    un = density.measure(bad, "flaime_al", np.random.default_rng(0), "lite")["rel_density"]
    se = density.measure(bad, "flaime_al", np.random.default_rng(0), "lite", sealed=True)["rel_density"]
    assert un > se + 0.05                # open porosity is flooded unless sealed


def test_crucible_400_holds_more():
    from twin.instruments import atomize_yield as ay
    opts = ay.crucible_options()
    assert opts
    for camp in ("flaime_al", "onr_cu"):
        a = ay.charge_plan(camp, 225)
        b = ay.charge_plan(camp, 400)
        for k in ("charge_g", "run_h", "consumables", "p_fail_add", "note"):
            assert k in a and k in b
        assert b["charge_g"] > a["charge_g"] > 0


def test_reuse_raises_oxygen(refs):
    from twin.instruments import reuse
    lot, _ = refs["AlSi10Mg"]
    g, new = reuse.after_build(lot, 300.0, 30.0, {}, np.random.default_rng(0))
    assert 0 < g < 300.0
    assert new["oxygen_ppm"] > lot["oxygen_ppm"]
    assert lot.get("reuse", 0) == 0                # the input is not mutated
    lot_cu, _ = refs["C95800 NAB"]
    g2, new2 = reuse.after_ded(lot_cu, 500.0, 0.8, {}, np.random.default_rng(0))
    assert 0 < g2 < 500.0 * 0.2 + 1e-9 or 0 < g2 < 500.0
    assert new2["oxygen_ppm"] > lot_cu["oxygen_ppm"]


def test_flow_helper(refs):
    from twin.instruments import psd
    lot, _ = refs["AlSi10Mg"]
    f = psd.flow(lot)
    assert isinstance(f, dict) and f


def test_corrosion_tracks_truth(refs):
    """The screen's early rate and the immersion's attack rank 70-30 against NAB as the truth does."""
    _, cuni = refs["C71500 70-30 Cu-Ni"]
    _, nab = refs["C95800 NAB"]
    for fid in ("lite", "fast"):
        a = np.mean([ins.measure("immersion", nab, "onr_cu", np.random.default_rng(i), fid)["attack_um"] for i in range(8)])
        b = np.mean([ins.measure("immersion", cuni, "onr_cu", np.random.default_rng(i), fid)["attack_um"] for i in range(8)])
        assert a > b
    assert ins.measure("corrosion_screen", cuni, "flaime_al", np.random.default_rng(0), "lite") == {}

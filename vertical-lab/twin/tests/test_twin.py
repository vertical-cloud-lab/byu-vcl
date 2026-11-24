"""Checks on the twin: the rules, the physics anchors, the market, the calendar, and that the two campaigns stay apart.

    cd vertical-lab && python3 -m pytest -q twin/tests
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from twin import campaign as C
from twin import facility as F
from twin import policies as P
from twin import spaces, supply, thermo, truth_al, truth_cu, usgs


# ------------------------------------------------------------------------------------------------- the search spaces
@pytest.mark.parametrize("space", [spaces.AL, spaces.CU])
def test_samples_follow_the_proposals_rules(space):
    pts = space.sample(300, seed=1, kind="sobol")
    assert len(pts) == 300
    for p in pts:
        assert space.check(p) == [], space.check(p)
        assert space.composition(p)[space.balance] >= space.min_balance - 1e-6


@pytest.mark.parametrize("space", [spaces.AL, spaces.CU])
def test_encode_decode_round_trip(space):
    for p in space.sample(20, seed=2):
        d = space.decode(space.encode(p))
        for k, v in p.items():
            assert d[k] == pytest.approx(v, rel=1e-6, abs=1e-9)


def test_copper_rules_are_repaired():
    d = {e: 0.0 for e in spaces.CU.elements}
    d.update(Al=8.0, Fe=4.0, Ni=1.0, Cr=0.5, Nb=0.5, Si=0.3)
    r = spaces.CU.repair(d)
    assert r["Cr"] == r["Nb"] == r["Si"] == 0.0            # Cu-Ni-only additions removed above 3 % Al
    assert r["Ni"] >= r["Fe"]                                # above 7 % Al, Ni >= Fe


# ------------------------------------------------------------------------------------------------- database lookups
def test_mineral_burden_orders_the_reference_alloys():
    a = usgs.mineral_burden({"Al": 89.65, "Si": 10.0, "Mg": 0.35})
    s = usgs.mineral_burden({"Al": 94.4, "Mg": 4.6, "Sc": 0.7, "Zr": 0.3})
    assert s["mbs_lin"] > 10 * a["mbs_lin"]                  # scandium dominates Scalmalloy's burden
    for el in ("Mn", "Sc", "Nb"):
        assert usgs.nir(el) == pytest.approx(1.0)
    assert 0 < usgs.nir("Ce") < 1                            # rare earths' compounds row


# ------------------------------------------------------------------------------------------------- thermodynamics
def test_fast_scheil_orders_crack_susceptibility():
    tr = thermo.AlSolidification("truth")
    k = lambda wt: tr.run(wt)["kou_index_K"]
    assert k({"Al": 89.65, "Si": 10.0, "Mg": 0.35}) < 100 < k({"Al": 88.1, "Zn": 5.6, "Mg": 2.5, "Cu": 1.6, "Cr": 0.2})


def test_open_database_blind_spots():
    tr, op = thermo.AlSolidification("truth"), thermo.AlSolidification("open")
    zr = {"Al": 99.4, "Zr": 0.6}
    assert tr.run(zr)["T_liquidus_C"] > 800 > op.run(zr)["T_liquidus_C"]     # no primary Al3Zr in mc_al
    assert tr.params["Zr"][0] > 1 > op.params["Zr"][0]                         # k on the wrong side of 1
    assert "Er" not in op.params                                                # no open database has Er


def test_copper_emulator_and_its_correction():
    nab = {"Al": 9.2, "Ni": 4.5, "Fe": 4.0, "Mn": 1.2}
    o, t = thermo.CuThermo("open").run(nab), thermo.CuThermo("truth").run(nab)
    assert 30 < o["liquidus_C"] - t["liquidus_C"] < 70                          # DAL: the NAB liquidus 51 degC high
    assert o["beta_900"] > 0.4                                                  # beta at 900 degC in NAB
    cuni = thermo.CuThermo("truth").run({"Ni": 30.0, "Fe": 0.6, "Mn": 0.6})
    assert 1200 < cuni["liquidus_C"] < 1270


# ------------------------------------------------------------------------------------------------- ground truth
def test_aluminium_reference_alloys():
    rows = {r["alloy"]: r for r in truth_al.reference_table()}
    assert 230 <= rows["AlSi10Mg"]["ys"] <= 320 and 4 <= rows["AlSi10Mg"]["el"] <= 9
    assert rows["7075"]["crack_density"] > 1.0                                  # 7075 cracks under LPBF
    assert rows["7075 + 1 Zr"]["crack_density"] < 0.05                          # ... unless inoculated (Martin 2017)
    assert rows["Scalmalloy"]["ys"] > 400


def test_copper_reference_alloys():
    rows = {r["alloy"].split()[0]: r for r in truth_cu.reference_table()}
    assert 130 <= rows["C71500"]["ys"] <= 180
    assert 100 <= rows["C70600"]["ys"] <= 140
    assert rows["C95800"]["beta_prime"] > 0.1 and rows["C95800"]["attack"] > 3
    t = truth_cu.CuTruth(0)
    part = lambda wt: dict(composition=wt, thermo=t.thermo(wt), porosity=0.003, beta_prime=0.0, temper=0.5)
    r7030 = t.corrosion(part({"Ni": 30.0, "Fe": 0.6, "Mn": 0.6, "Cu": 68.8}))["rate_um_yr"]
    r9010 = t.corrosion(part({"Ni": 10.0, "Fe": 1.4, "Mn": 0.8, "Cu": 87.8}))["rate_um_yr"]
    assert r7030 < r9010


# ------------------------------------------------------------------------------------------------- the market
def test_market_is_reproducible_and_scenarios_differ():
    a, b = supply.Market("historical", 5, 400), supply.Market("historical", 5, 400)
    assert a.index("Ni", 200) == b.index("Ni", 200)
    calm = supply.Market("calm", 5, 400)
    assert calm.events == []
    ec = supply.Market("export_controls", 5, 400)
    assert ec.lead_mult["Sc"][100] > 2.0 and ec.index("Sc", 60) > ec.index("Sc", 0) * 1.3
    tar = supply.Market("tariffs", 5, 400)
    it = supply.ITEMS["al_bar_hp"]
    assert tar.price(it, 0) > calm.price(it, 0)


def test_charge_bill_adds_up():
    comp = {"Al": 93.0, "Mg": 4.0, "Si": 2.0, "Sc": 0.5, "Zr": 0.5}
    bill = supply.charge_bill("flaime_al", comp, 0.3)
    el = sum(q * supply.ITEMS[k].frac for k, q in bill.items() if supply.ITEMS[k].element != "Al") \
        + bill["al_bar_hp"]
    assert el == pytest.approx(0.3, rel=1e-6)


# ------------------------------------------------------------------------------------------------- the calendar
def test_bookings_respect_calendars_and_do_not_overlap():
    f = F.Facility("proposed", 0, 5000.0)
    r = f.res["atomizer"]
    spans = [r.book(0.0, 2.5, "a" if i % 2 else "b", "x", changeover_h=3.0) for i in range(20)]
    for (s1, e1), (s2, e2) in zip(sorted(spans), sorted(spans)[1:]):
        assert e1 <= s2 + 1e-9
    for s, e in spans:
        day = int(s // 24) % 7
        assert day <= 5                                      # Monday to Saturday
    m = f.res["utah_midi"]
    starts = sorted(m.book(0.0, 5.0, "a", "p")[0] for _ in range(9))
    for i in range(len(starts) - 3):
        assert starts[i + 3] - starts[i] >= 7 * 24 - 1e-6   # at most three builds a week


# ------------------------------------------------------------------------------------------------- the two campaigns
def _twin(pol_al, pol_cu, days=90, seed=0):
    specs = {"flaime_al": C.Spec("flaime_al", 60_000, 12, seed), "onr_cu": C.Spec("onr_cu", 30_000, 6, seed)}
    pols = {"flaime_al": P.POLICIES[pol_al]("flaime_al", seed), "onr_cu": P.POLICIES[pol_cu]("onr_cu", seed)}
    return C.Twin(specs, pols, "historical", "proposed", seed, days)


def test_twin_runs_and_stays_within_budget():
    tw = _twin("random", "random")
    out = tw.run()
    for k, c in tw.campaigns.items():
        assert out[k]["spent"] <= c.spec.budget_usd * 1.25    # one action may overshoot the last dollars
        for d in c.demonstrated:
            assert 0.0 <= d["u"] <= 1.0


def test_the_campaigns_keep_their_own_truths():
    """A campaign's ground truth depends on its own seed only: another campaign's policy cannot change it."""
    a, b = _twin("random", "random", days=10), _twin("random", "tiered", days=10)
    d = spaces.AL.sample(1, seed=7)[0]
    comp = spaces.AL.composition(d)
    ta, tb = a.campaigns["flaime_al"].truth, b.campaigns["flaime_al"].truth
    assert ta.thermo(comp) == tb.thermo(comp)
    assert ta.f_ys(truth_al._comp_vec(comp)) == tb.f_ys(truth_al._comp_vec(comp))


def test_the_runs_are_reproducible():
    s1, s2 = _twin("random", "random", days=60, seed=3).run(), _twin("random", "random", days=60, seed=3).run()
    for k in ("flaime_al", "onr_cu"):
        assert s1[k]["spent"] == pytest.approx(s2[k]["spent"])
        assert s1[k]["n_lots"] == s2[k]["n_lots"]

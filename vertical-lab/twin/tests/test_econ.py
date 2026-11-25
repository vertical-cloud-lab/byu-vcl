"""Checks of the economics layer (twin/econ.py, twin/cloud.py, twin/accel.py). No twin runs; a few seconds."""
import math

import numpy as np
import pytest

from twin import accel as AC
from twin import cloud as CL
from twin import econ as E


# ------------------------------------------------------------------------------------------------ accel
def test_km_median_without_censoring_is_the_median():
    assert AC.km_median([5, 1, 3, 2, 4], [1] * 5) == 3.0


def test_km_median_with_censoring():
    # two of five reach by t=2, the rest censored later: S stays at 0.6 > 0.5, so the median is unbounded
    assert math.isinf(AC.km_median([1, 2, 9, 9, 9], [1, 1, 0, 0, 0]))
    # three of five reach: S falls to 0.4 at t=3
    assert AC.km_median([1, 2, 3, 9, 9], [1, 1, 1, 0, 0]) == 3.0
    # a censoring before the events shrinks the risk set: S(1) = 3/4, S(2) = 3/4 * 2/3 = 0.5
    assert AC.km_median([0.5, 1, 2, 3], [0, 1, 1, 1]) == 2.0


def _curves(days_to_hit, n_points=4, horizon=365.0):
    out = []
    for d in days_to_hit:
        cur = [[d * (i + 1) / n_points, 1000.0 * (i + 1), 0.2 + 0.6 * (i + 1) / n_points] for i in range(n_points)]
        out.append(dict(curve=cur, spent=cur[-1][1], horizon_days=horizon))
    return out


def test_acceleration_factor_of_a_twice_as_fast_arm():
    ref = _curves([100, 120, 140, 160, 180])
    new = _curves([50, 60, 70, 80, 90])
    a = AC.acceleration_factor(ref, new, 0.8, "days", n_boot=300)
    assert a["af"] == pytest.approx(2.0)
    assert a["lo"] <= 2.0 <= a["hi"]
    assert a["hit_ref"] == 1.0 and a["hit_new"] == 1.0


def test_acceleration_factor_bound_when_the_reference_rarely_reaches():
    ref = [dict(curve=[[400.0, 1.0, 0.1]], spent=1.0, horizon_days=365.0)] * 4 + _curves([200])
    new = _curves([50, 60, 70])
    a = AC.acceleration_factor(ref, new, 0.8, "days", n_boot=200)
    assert math.isinf(a["af"]) and a["bound_kind"] == "lower"
    assert a["af_bound"] == pytest.approx(365.0 / 60.0)            # censored at the horizon


def test_enhancement_factor():
    ref = [dict(curve=[[10, 1, 0.2], [20, 2, 0.4]]), dict(curve=[[10, 1, 0.2], [20, 2, 0.4]])]
    new = [dict(curve=[[10, 1, 0.4], [20, 2, 0.8]]), dict(curve=[[10, 1, 0.4], [20, 2, 0.8]])]
    e = AC.enhancement_factor(ref, new, 1, "experiments", n_boot=100)
    assert e["ef"] == pytest.approx(2.0)


def test_compare_gives_time_and_cost_ratios():
    ref = _curves([100, 120, 140])
    new = _curves([50, 60, 70])
    c = AC.compare(ref, new, 0.8, n_boot=100)
    assert c["days"]["af"] == pytest.approx(2.0)
    assert c["cost"]["cash"]["ratio"] == pytest.approx(1.0)    # same spend at the target in both arms
    assert "faster" in AC.headline(c)


# ------------------------------------------------------------------------------------------------ queueing
def test_kingman_mm1_and_monotone():
    # M/M/1: Wq = rho / (1 - rho) * ts exactly
    assert CL.kingman_wq(0.5, 1, 1, 2.0) == pytest.approx(2.0)
    w = [CL.kingman_wq(r, 1, 0.5, 1.0) for r in (0.1, 0.5, 0.8, 0.95)]
    assert all(a < b for a, b in zip(w, w[1:]))
    assert CL.kingman_wq(0.5, 1, 1, 1.0, m=2) < CL.kingman_wq(0.5, 1, 1, 1.0, m=1)
    assert math.isinf(CL.kingman_wq(1.0, 1, 1, 1.0))


# ------------------------------------------------------------------------------------------------ econ
def test_equipment_tables_are_sourced():
    for f in ("vertical_lab", "conventional"):
        for it in E.items(f):
            assert it.price > 0 and it.qty > 0 and it.life > 0
            assert it.src, it.key
            assert it.kind in ("procurement", "list", "estimate", "assumed", "owned")
            assert 0 <= it.service < 0.2 and 0 <= it.duty <= 1
    assert E.capex("vertical_lab") > 5 * E.capex("conventional")


def test_crf_and_annual_cost():
    assert E.crf(10, 0.0) == pytest.approx(0.1)
    assert E.crf(10, 0.05) > 0.1
    a = E.annual_cost("vertical_lab")
    assert a["total"] == pytest.approx(sum(v for k, v in a.items() if k != "total"))
    assert E.annual_cost("vertical_lab", include_capex=False)["capex"] == 0.0


def test_available_hours():
    assert E.available_hours("24/7", 1) == pytest.approx(8760.0)
    assert E.available_hours("24/7", 2) == pytest.approx(2 * 8760.0)
    assert E.available_hours("day", 1) == pytest.approx(45 * 8760 / 168)
    assert E.available_hours("day6", 1, station="atomizer") == pytest.approx(16 * 2.5 * 8760 / 168)


INFO = {"atomizer": dict(hours="day6", units=1), "utah_midi": dict(hours="24/7", units=1),
        "byu_sem": dict(hours="24/7", units=1)}
HOURS = {"flaime_al": {"atomizer": [500.0, 200], "utah_midi": [300.0, 60], "byu_sem": [100.0, 150]},
         "onr_cu": {"atomizer": [200.0, 80], "byu_sem": [50.0, 40]}}


def _fixed_total(f):
    st, ov = E.station_fixed(f)
    return sum(v["capex"] + v["service"] + v["utilities"] for v in st.values()) + sum(ov.values())


def test_allocation_absorbs_everything_when_the_campaigns_are_alone():
    al = E.allocate("vertical_lab", HOURS, info=INFO)
    charged = sum(al[c][k] for c in ("flaime_al", "onr_cu") for k in ("capex", "service", "utilities", "labour"))
    assert charged == pytest.approx(_fixed_total("vertical_lab"), rel=1e-6)


def test_outside_users_lower_the_campaigns_share_smoothly():
    tot = []
    for u in (None, 1e-4, 0.05, 0.3, 0.6, 0.9):
        al = E.allocate("vertical_lab", HOURS, info=INFO, utilization=u)
        tot.append(sum(al[c]["capex"] for c in ("flaime_al", "onr_cu")))
    assert all(a >= b - 1e-6 for a, b in zip(tot, tot[1:]))
    assert tot[1] == pytest.approx(tot[0], rel=0.01)        # no jump at u -> 0
    assert tot[-1] < 0.2 * tot[0]


def test_split_cash():
    sb = {"order": 100.0, "print": 50.0, "NSL": 10.0}
    assert E.split_cash(sb, "proposed") == dict(consumables=100.0, outside_fees=60.0)
    assert E.split_cash(sb, "vertical_lab") == dict(consumables=150.0, outside_fees=10.0)


def _run(facility):
    curve = [[100.0, 20000.0, 0.3], [200.0, 40000.0, 0.65]]
    camp = lambda n: dict(spent=50000.0, best=0.65, curve=curve, n_demonstrated=n, n_lots=3 * n, n_builds=2 * n,
                          n_designs=10 * n, n_sims=10 * n, spend_by={"order": 30000.0, "print": 20000.0})
    return dict(cfg=dict(facility=facility, policy="cost_aware", seed=0, horizon_days=365),
                campaigns={"flaime_al": camp(10), "onr_cu": camp(2)},
                utilization={"atomizer": 0.08, "utah_midi": 0.02})


def test_cost_per_experiment_and_campaign_cost():
    for f in ("proposed", "vertical_lab"):
        r = _run(f)
        a = E.cost_per_experiment(r, include_capex=True)
        b = E.cost_per_experiment(r, include_capex=False)
        assert a["both"]["n"] == 12
        assert a["both"]["per_total"] > b["both"]["per_total"] > 0
        assert b["both"]["per"]["capex"] == 0.0
        c = E.campaign_cost(r, "flaime_al", 0.6)
        assert c["reached"] and c["days"] == 200.0 and c["cash"] == 40000.0
        assert c["full"] >= c["operating"] >= c["cash"]
    # the conventional lab pays people by the hour; the vertical lab has fixed staff
    assert E.run_ledger(_run("proposed"))["flaime_al"]["labour_h"] > 0
    assert E.run_ledger(_run("vertical_lab"))["flaime_al"]["labour_h"] == 0


def test_depreciation_curve_falls_with_utilization():
    d = E.depreciation_curve("vertical_lab", "flaime_al", [0.1, 0.3, 0.6, 0.9])
    y = d["per_experiment"]
    assert all(a > b for a, b in zip(y, y[1:]))
    assert y[0] / y[-1] == pytest.approx(9.0, rel=0.01)       # 1/u


# ------------------------------------------------------------------------------------------------ cloud
def _events():
    ev = dict(meta=dict(horizon_days=365), stations={k: dict(name=k, units=v["units"], hours=v["hours"], external=False)
                                                     for k, v in INFO.items()}, events=[], results=[])
    rng = np.random.default_rng(0)
    for i, t in enumerate(np.sort(rng.uniform(0, 8000, 120))):
        ev["events"].append(dict(t0_h=float(t), t1_h=float(t) + 2.5, station="atomizer", campaign="flaime_al",
                                 what="atomize", design=i, node="powder"))
        ev["events"].append(dict(t0_h=float(t) + 3, t1_h=float(t) + 8, station="utah_midi", campaign="flaime_al",
                                 what="print", design=i, node="print"))
        ev["results"].append(dict(t_h=float(t) + 200, campaign="flaime_al", type="demonstrated", design=i))
    return ev


def test_utilization_and_fill():
    ev = _events()
    U = CL.utilization(ev)
    assert U["atomizer"]["busy_h"] == pytest.approx(300.0)
    assert U["utah_midi"]["util"] == pytest.approx(600.0 / 8760.0)
    F = CL.fill(U, 0.5)
    m = F["utah_midi"]
    assert m["ext_h"] == pytest.approx(0.5 * 8760 - 600.0)
    assert m["revenue"] == pytest.approx(m["ext_h"] * m["usd_per_h"])
    assert m["util_after"] == pytest.approx(0.5)
    Fd = CL.fill(U, 0.5, demand_h_week=10.0)
    assert Fd["utah_midi"]["ext_h"] == pytest.approx(10.0 * 8760 / 168)
    assert CL.capex_recovery(F)["revenue"] > 0


def test_slowdown_grows_with_utilization():
    sd = CL.slowdown(_events(), "flaime_al", levels=(0.2, 0.5, 0.8))
    assert sd["factor"][0] >= 1.0
    assert sd["factor"][0] < sd["factor"][1] < sd["factor"][2]


def test_external_callable_books_jobs_into_a_facility():
    from twin import facility as FAC
    fac = FAC.Facility("vertical_lab", 0, 400 * 24.0)
    CL.external_callable({"utah_midi": 876.0, "byu_sem": 100.0}, 365 * 24.0, seed=1)(fac)
    ext = [j for j in fac.res["utah_midi"].jobs if j[2] == "external"]
    assert 80 <= len(ext) <= 140                                  # about 876 h / 8 h jobs
    assert fac.n_external >= len(ext)

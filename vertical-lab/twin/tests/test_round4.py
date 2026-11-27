"""Round 4: build-out, ramp-up, routes and plans (twin/round4.py, twin/bench4.py)."""
import math

import pytest

from twin import bench2 as B2
from twin import campaign as C
from twin import econ as E
from twin import round4 as R4


def test_learning_curve_fit():
    prof = R4.fit_learning()
    best = min(prof.items(), key=lambda kv: kv[1][1])
    assert best[0] == pytest.approx(R4.LEARN["N_L"], abs=3.0)
    assert prof[R4.LEARN["N_L"]][0] == pytest.approx(R4.LEARN["P0"], abs=0.05)
    assert len(R4.ATOMIZER_RUNS) == 10


def test_build_schedule_plans():
    ext = R4.build_schedule(0, "external")
    assert ext["stations"] == {} and ext["payments"] == [] and ext["start_h"] == 0.0
    par, wait = R4.build_schedule(0, "parallel"), R4.build_schedule(0, "wait")
    assert par["start_h"] == 0.0
    assert wait["start_h"] == pytest.approx(wait["full_h"])
    assert wait["full_h"] >= wait["cell_h"] and wait["full_h"] >= max(wait["stations"].values())
    # the room comes first: nothing is installed before the fit-out is done
    room = max(par["items"][k]["online_h"] for k in R4.ROOM)
    for k, it in par["items"].items():
        if k not in R4.ROOM:
            assert it["install_h"] >= room - 1e-6
    # every vertical-lab item but the owned atomizer and DAL's CubXL is paid for, deposits included
    owned = sum(it.capex for it in E.items("vertical_lab") if it.kind == "owned" or it.key == "cubxl")
    paid = sum(u for _, u, _ in par["payments"])
    listed = sum(it.capex for it in E.items("vertical_lab") if it.key in R4.BUILD) - owned
    assert paid == pytest.approx(listed, rel=1e-6)


def _twin(plan, days=60, seed=0, opts=None):
    from twin.bench4 import make_policies
    pols = make_policies("fast", seed)
    specs = {k: C.Spec(k, B2.BUDGET[k] * days / 365.0, B2.WIP[k], seed, 1.0, stock="stocked") for k in pols}
    return R4.Twin4(specs, pols, plan=plan, seed=seed, horizon_days=days, opts=opts)


def test_routes_by_plan():
    f_ext = R4.Facility4("external", 0, 1000 * 24.0)
    f_wait = R4.Facility4("wait", 0, 1000 * 24.0)
    f_par = R4.Facility4("parallel", 0, 1000 * 24.0)
    assert not any(k.endswith("@vcl") for k in f_ext.res)
    assert f_wait.routes["utah_midi"] == ["utah_midi@vcl"]
    assert set(f_par.routes["utah_midi"]) == {"utah_midi", "utah_midi@vcl", "lpbf_3dpt"}
    # before the in-house MIDI is online, a print goes to a partner; long after, with nothing booked, in house
    t_on = f_par.res["utah_midi@vcl"].online_h
    assert f_par.pick("utah_midi", 0.0, 5.0, "flaime_al", "print") in ("utah_midi", "lpbf_3dpt")
    assert f_par.pick("utah_midi", t_on + 500 * 24.0, 5.0, "flaime_al", "print") == "utah_midi@vcl"


def test_ramp_up_state():
    f = R4.Facility4("parallel", 0, 1000 * 24.0)
    a = f.res["atomizer"]
    assert a.n == R4.LEARN["N_ATOMIZER_DAY0"]
    assert a.p_fail() == pytest.approx(math.exp(-10 / R4.LEARN["N_L"]))
    m = f.res["utah_midi@vcl"]
    assert m.n == 0 and m.p_fail() == pytest.approx(1.0) and m.factor() == pytest.approx(R4.LEARN["F0"])
    m.n = 200
    assert m.p_fail() < 1e-6 and m.factor() == pytest.approx(1.0, abs=1e-6)


def test_short_runs():
    for plan in ("parallel", "external"):
        tw = _twin(plan, 45)
        s = tw.run()
        rep = tw.report()
        assert rep["plan"] == plan
        assert s["flaime_al"]["n_lots"] > 0
        assert "atomizer" in rep["monthly"] and sum(rep["monthly"]["atomizer"]["jobs"]) > 0
    # the wait plan does nothing before the cell is complete
    tw = _twin("wait", 45)
    tw.run()
    assert all(not c.lots for c in tw.campaigns.values())


def test_provenance_visit_and_offsets():
    tw = _twin("parallel", 60, opts=dict(provenance="all"))
    tw.run()
    F = tw.fac4
    for k, t in F.offset_known.items():
        if t is not None:
            sd = R4.OFFSETS[k][1]
            assert abs(F.offset_est[k] - F.offset[k]) < 5 * R4.PROVENANCE["residual"] * sd
    assert all(v == 0.0 for k, v in R4.Facility4("parallel", 0, 1000.0).offset_est.items())

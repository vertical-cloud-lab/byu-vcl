"""Round 3's engine and policies (twin/campaign.py Twin(mode="async"), twin/facility.py physical capacity,
twin/opt/tinygp.py, twin/opt/policies3.py, twin/opt/net3.py)."""
import json
from pathlib import Path

import numpy as np
import pytest

from twin import campaign as C
from twin import facility as F

ROOT = Path(__file__).resolve().parents[2]


def _twin(policy="heuristic", days=120, facility="vertical_lab", seed=0, cu_budget=60_000.0):
    from twin.opt import policies3 as P3
    specs = {"flaime_al": C.Spec("flaime_al", 120_000.0, 24, seed, stock="stocked"),
             "onr_cu": C.Spec("onr_cu", cu_budget, 8, seed, stock="stocked")}
    pols = {k: P3.make3(policy, k, seed) for k in specs}
    return C.Twin(specs, pols, facility=facility, seed=seed, horizon_days=days, mode="async")


def test_round2_reproduces_on_the_refactored_engine():
    """find + commit is book: round 2's heuristic, seed 0, gives the committed result exactly."""
    from twin import bench2 as B
    ref = next(json.loads(l) for l in (ROOT / "out/twin2/runs/main.jsonl").read_text().splitlines()
               if json.loads(l)["cfg"]["policy"] == "heuristic" and json.loads(l)["cfg"]["seed"] == 0)
    r = B.run_one(B._cfg("heuristic", 0))
    for k in ("flaime_al", "onr_cu"):
        assert r["campaigns"][k]["best_new"] == ref["campaigns"][k]["best_new"]
        assert round(r["campaigns"][k]["spent"], 2) == round(ref["campaigns"][k]["spent"], 2)
        assert r["campaigns"][k]["n_demonstrated"] == ref["campaigns"][k]["n_demonstrated"]


def test_tinygp_matches_the_fitted_node():
    from twin.opt.gp import Node
    from twin.opt.tinygp import TinyGP
    rng = np.random.default_rng(1)
    X = rng.random((30, 4))
    y = np.cos(X @ np.array([1.0, 2.0, -1.0, 0.5])) + 0.05 * rng.standard_normal(30)
    n = Node("gp", 4, seed=0)
    n.fit(X, y)
    g = TinyGP(n)
    U = rng.random((9, 4))
    m1, s1 = n.predict(U)
    m2, s2 = g.predict(U)
    assert np.allclose(m1, m2, atol=1e-6) and np.allclose(s1, s2, atol=1e-6)
    # the kriging believer: a pseudo-observation at the mean leaves the mean and shrinks the variance there
    g2 = g.with_rows(U[:1], m2[:1])
    m3, s3 = g2.predict(U[:1])
    assert abs(m3[0] - m2[0]) < 1e-3 and s3[0] < s2[0]


@pytest.fixture(scope="module")
def run120():
    tw = _twin("heuristic", 120)
    tw.run()
    return tw


def test_no_station_line_overlaps_and_fixtures_hold(run120):
    f = next(iter(run120.facilities.values()))
    for k, r in f.res.items():
        for ln in r.lines:
            for a, b in zip(zip(ln.s, ln.e), list(zip(ln.s, ln.e))[1:]):
                assert a[1] <= b[0] + 1e-6, k
    # at no time are more coupons in immersion than positions
    jobs = sorted((j[0], j[1]) for j in f.res["immersion"].jobs)
    for t, _ in jobs:
        assert sum(1 for a, b in jobs if a <= t < b) <= f.res["immersion"].st.units


def test_helpers_are_booked_with_their_steps(run120):
    """Every in-house step of the vertical lab books a robot at its start; the atomizer books the technician."""
    f = next(iter(run120.facilities.values()))
    robot = {round(j[0], 6) for j in f.res["robot"].jobs}
    op = {round(j[0], 6) for j in f.res["operator"].jobs}
    for j in f.res["atomizer"].jobs:
        assert round(j[0], 6) in robot and round(j[0], 6) in op
    for j in f.res["utah_midi"].jobs:
        assert round(j[0], 6) in robot
    assert f.helper_misses == 0


def test_spending_stays_within_the_plan(run120):
    for c in run120.campaigns.values():
        led = sorted(c.ledger, key=lambda r: r[0])
        tot = 0.0
        for t, usd, what in led:
            tot += usd
        # the plan is checked before each action; an action's own cost may run past its estimate a little
        assert c.spent <= c.plan(run120.h) * 1.10 + 500.0


def test_gate_refuses_a_busy_station():
    tw = _twin("heuristic", 30)
    c = tw.campaigns["flaime_al"]
    r = c.fac.res["utah_midi"]
    s, d, i = r.find(10.0, 200.0, "flaime_al")
    r.commit(s, d, i, "flaime_al", "block")
    lot = {"id": 1, "design": 1, "measured": {}, "remaining_g": 100.0}
    c.lots[1] = lot
    assert not c.gate_ok(dict(kind="print", lot=1, params=[{}]), 20.0)
    assert c.gate_ok(dict(kind="print", lot=1, params=[{}]), s + d + 1.0)


def test_interim_readings_and_stop():
    """A coupon's interim readings fall toward its 30-day rate (the film), and a stop frees its position."""
    tw = _twin("heuristic", 200)
    tw.run()
    c = tw.campaigns["onr_cu"]
    done = [D for D in c.deposits.values() if isinstance(D.get("immersion"), dict) and D.get("imm_interim")]
    assert done, "no coupon finished in 200 days"
    for D in done:
        r = {d: m["rate_um_yr"] for d, m in D["imm_interim"].items()}
        assert set(r) == set(C.Campaign.IMM_DAYS)
        assert 0.2 < r[14] / D["immersion"]["rate30_um_yr"] < 5.0
    # stop one running coupon by hand on a fresh twin
    tw2 = _twin("heuristic", 90)
    tw2.run()
    c2 = tw2.campaigns["onr_cu"]
    running = [k for k, x in c2._imm.items() if x.get("stopped") is None and not x.get("final") and x.get("aid")]
    if running:
        k = running[0]
        h = c2._imm[k]["handle"]
        t_stop = c2._imm[k]["t_in"] + 3 * 24.0 + 1.0
        assert c2.submit3(dict(kind="stop", deposit=k), t_stop) == "ok"
        ln = c2.fac.res["immersion"].lines[h[0]]
        assert any(abs(a - h[1]) < 1e-9 and abs(b - t_stop) < 1e-9 for a, b in zip(ln.s, ln.e))
        assert c2._imm[k]["aid"] in c2.cancelled


def test_net3_runs_a_short_twin():
    for name in ("bofn3", "pkgfn3"):
        tw = _twin(name, 60)
        s = tw.run()
        assert s["flaime_al"]["n_lots"] > 0
        assert s["onr_cu"]["spent"] > 0

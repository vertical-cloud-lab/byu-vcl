"""Round 5's engine (twin/round5.py) and runner (twin/bench5.py): short runs only (a minute in all)."""
from __future__ import annotations

import json
import os

import numpy as np
import pytest

os.environ.setdefault("TWIN5_OUT", "/tmp/twin5_test")

from twin import bench5 as B5  # noqa: E402
from twin import round4 as R4  # noqa: E402
from twin import round5 as R5  # noqa: E402

H = 24.0


def _short(cfg, days):
    os.environ["TWIN5_DAYS"] = str(days)
    try:
        out, tw = B5.simulate(cfg)
    finally:
        os.environ.pop("TWIN5_DAYS", None)
    return out, tw


def test_round4_schedule_hook_is_round4s():
    f = R4.Facility4("parallel", 3, 1000 * H)
    assert f.sched == R4.build_schedule(3, "parallel")


def test_facility_window_and_installation():
    for seed in range(12):
        s = R5.build_schedule5(seed, "parallel")
        assert 60 * H <= s["room_h"] <= 100 * H
        for k, it in s["items"].items():
            assert it["install_h"] >= s["room_h"] - 1e-9, k
            assert it["online_h"] >= it["install_h"]
    assert R5.build_schedule5(0, "external")["items"] == {}


def test_used_rule_picks_only_used_markets_and_saves_days():
    s = R5.build_schedule5(0, "parallel")
    assert s["used"], "the rule picks some station"
    for k, u in s["used"].items():
        assert k in R5.USED_OK
        assert u["expected_days_saved"] >= R5.USED["rule_days"]
    s2 = R5.build_schedule5(0, "parallel", dict(used=False))
    assert s2["used"] == {}


def test_money_at_t0_and_atomizer_cap_in_the_conventional_lab():
    out, tw = _short(B5._cfg("conventional", "external", "fast", "lean", 1), 70)
    for c in tw.campaigns.values():
        assert c.plan(0.0) == c.spec.budget_usd
    R = tw.fac4.res["atomizer"]
    assert R.switch_h is None
    weeks = {}
    for j in R.jobs:
        if j[3] == "atomize" and j[0] < 70 * H:
            weeks[int(j[0] // (7 * H))] = weeks.get(int(j[0] // (7 * H)), 0) + 1
            day = int(j[0] // H) % 7
            assert day in ((0, 1, 2) if j[2] == "flaime_al" else (4,))
            assert round(j[0] % H, 3) in (8.0, 13.0)
    assert weeks and max(weeks.values()) <= 8
    assert out["r5"]["notes"] == list(R5.NOTES_APPLIED)


def test_decision_windows():
    d = R5.Decide("nominal", "conventional", {"flaime_al": "human", "onr_cu": "human"})
    assert d.classify("flaime_al", {"type": "test"}) == "meeting"
    assert d.classify("flaime_al", {"type": "lot"}) == "review"
    assert d.classify("onr_cu", {"type": "imm_final_book"}) is None
    fri13 = 4 * H + 13.0
    assert d.due("flaime_al", "meeting", fri13, 0.0, 1)
    assert not d.due("flaime_al", "meeting", fri13 + 1.0, 0.0, 1)
    assert not d.due("flaime_al", "review", 1 * H + 13.0, 1 * H, 1)       # one result, waited 13 h: not yet
    assert d.due("flaime_al", "review", 1 * H + 13.0, 1 * H, 2)           # two results: decided at the review
    v = R5.Decide("nominal", "vertical", {"flaime_al": "human", "onr_cu": "auto"})
    assert v.classify("flaime_al", {"type": "lot"}) is None                # routine steps run by themselves
    assert v.classify("onr_cu", {"type": "cu_test"}) is None
    t = v.signoff_time(4 * H + 15.0)                                       # Friday 15:00 -> Monday 10:00
    assert t == 7 * H + 10.0
    assert R5.Decide("none", "conventional", {"flaime_al": "human"}).classify("flaime_al", {"type": "test"}) is None


def test_hpc_stream_and_reproducibility():
    cfg = B5._cfg("vertical", "parallel", "fast", "reorder", 2)
    a, tw = _short(cfg, 30)
    b, _ = _short(cfg, 30)
    for k in ("seconds", "gp", "env", "code"):
        a.pop(k, None)
        b.pop(k, None)
    assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    hp = a["r5"]["hpc"]
    for k, c in hp["campaigns"].items():
        assert c["evaluated"] == pytest.approx(R5.HPC["cores"] / R5.HPC["core_h"] * 24 * 31, rel=0.05)
        assert c["materialized"] <= R5.HPC["add_per_day"] * 31 + 1
        vis = sum(1 for x in tw.campaigns[k].sims if x.get("stream"))
        assert vis <= R5.HPC["keep"] + 64


def test_counters_and_idle_report_shapes():
    out, _ = _short(B5._cfg("vertical", "parallel", "fast", "lean", 0), 40)
    for k in ("flaime_al", "onr_cu"):
        c = out["r5"]["counters"][k]
        assert c["lots_made"] >= c["alloys_made"] >= 0
        assert set(out["r5"]["idle"]["stretches"][k]) == {"atomizer", "fab"}
        assert out["r5"]["stock"][k]["mode"] == "lean"

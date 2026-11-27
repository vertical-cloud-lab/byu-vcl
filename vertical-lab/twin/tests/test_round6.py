"""Round 6's engine (twin/round6.py), policies (twin/opt/net6.py) and runner (twin/bench6.py): short runs only."""
from __future__ import annotations

import json
import math
import os

import pytest

os.environ.setdefault("TWIN6_OUT", "/tmp/twin6_test")

from twin import bench6 as B6  # noqa: E402
from twin import round5 as R5  # noqa: E402
from twin import round6 as R6  # noqa: E402
from twin.opt import net6  # noqa: E402

H = 24.0


def _short(cfg, days):
    os.environ["TWIN6_DAYS"] = str(days)
    try:
        out, tw = B6.simulate(cfg)
    finally:
        os.environ.pop("TWIN6_DAYS", None)
    return out, tw


# ------------------------------------------------------------------------------------------------- the build-out
def test_schedule_without_a_market_file_is_round5s():
    for seed in (0, 3, 7):
        for plan in ("parallel", "wait", "external"):
            a, b = R6.build_schedule6(seed, plan, market={}), R5.build_schedule5(seed, plan)
            assert a["payments"] == b["payments"], (seed, plan)
            assert a["stations"] == b["stations"] and a["cell_h"] == b["cell_h"] and a["room_h"] == b["room_h"]
            assert {k: v["online_h"] for k, v in a["items"].items()} == {k: v["online_h"] for k, v in b["items"].items()}
            assert sorted(a["used"]) == sorted(b["used"])
            assert a["used_source"] == "round 5's stand-ins"


def test_market_file_replaces_a_stations_numbers(tmp_path):
    p = tmp_path / "summary.csv"
    p.write_text("station_key,n_listings,used_ok,price_frac,lead_w,p_fault,refurb_w,refurb_frac\n"
                 "sem,14,true,0.30,5,0.4,8,0.2\n"          # a real market, cheaper and slower than the stand-in
                 "edm,3,false,,,,,\n"                      # no real market after all
                 "midi,2,true,0.6,3,0.3,6,0.15\n")         # a market for a station round 5 never bought used
    m = R6.load_market(p)
    assert set(m) == {"sem", "edm", "midi"} and m["sem"]["price_frac"] == 0.30 and m["edm"]["ok"] is False
    assert "price_frac" not in m["edm"]                    # an empty field keeps round 5's number
    ps = R6.used_params("sem", m)
    assert ps["lead_w"] == 5 and ps["p_fault"] == 0.4 and ps["refurb_sigma"] == R5.USED["refurb_sigma"]
    assert R6.used_params("xrd", m)["source"].startswith("round 5")
    assert R6.used_rule6("edm", R6.used_params("edm", m))["ok"] is False
    s = R6.build_schedule6(0, "parallel", market=m)
    s5 = R5.build_schedule5(0, "parallel")
    assert "edm" in s5["used"] and "edm" not in s["used"]
    assert s["used_source"] == "out/twin6/market/summary.csv"
    if "midi" in s["used"]:
        assert s["used"]["midi"]["price_frac"] == 0.6
    for k, it in s["items"].items():
        assert it["install_h"] >= s["room_h"] - 1e-9 or k == "services"


# ------------------------------------------------------------------------------------------------- crucibles
def test_crucible_pool_keeps_the_cycle_or_one_a_day():
    run, turn = 2.2, 15.0
    full = R6.CruciblePool("flaime_al", 1, 8, 0.0, turn)       # eight in rotation from the start
    t, starts = 0.0, []
    for _ in range(40):
        s = full.earliest(t, run)
        full.take(s, run)
        starts.append(s)
        t = s + run                                            # the atomizer is free again
    assert starts == pytest.approx([i * run for i in range(40)])   # never waits for a crucible
    one = R6.CruciblePool("flaime_al", 1, 8, 1e9, turn)        # the pool never arrives: one crucible
    t, starts = 0.0, []
    for _ in range(5):
        s = one.earliest(t, run)
        one.take(s, run)
        starts.append(s)
        t = s + run
    assert starts == pytest.approx([i * (run + turn) for i in range(5)])   # one run per 17.2 h
    late = R6.CruciblePool("flaime_al", 1, 8, 100.0, turn)     # the pool arrives at hour 100
    late.take(0.0, run)
    assert late.earliest(5.0, run) == pytest.approx(run + turn)
    assert late.earliest(150.0, run) == pytest.approx(150.0)
    assert late.report(1e9)["melts"] == 1


def test_crucibles_in_a_facility():
    f = R6.Facility6("parallel", 0, 1000 * H, dict(lab="vertical"))
    g = R6.Facility6("external", 0, 1000 * H, dict(lab="conventional"))
    for fam in ("flaime_al", "onr_cu"):
        assert f.crucibles[fam]["arrive_h"] == g.crucibles[fam]["arrive_h"]      # the same draw in both labs
        assert f.crucibles[fam]["n"] == R6.CRUCIBLES["n"]["vertical"][fam] and g.crucibles[fam]["n"] == 3
        assert f.derived_start_h(fam) == max(f.cell_h, f.crucibles[fam]["arrive_h"])
        assert g.derived_start_h(fam) is None
    late = R6.Facility6("parallel", 0, 1000 * H, dict(lab="vertical", crucibles=dict(late_d=240.0)))
    assert late.crucibles["flaime_al"]["arrive_h"] == pytest.approx(f.crucibles["flaime_al"]["arrive_h"] + 240 * H)
    assert late.derived_start_h("flaime_al") > late.cell_h


# ------------------------------------------------------------------------------------------------- money
def test_money_is_tracked_not_limited():
    out, tw = _short(B6._cfg("conventional", "external", "fast", "reorder", 1), 100)
    for k, c in tw.campaigns.items():
        assert c.budget_left == math.inf and c.plan(0.0) == math.inf and c.wip_reserve(0.0) == 0.0
        assert not {"money", "plan", "money_wip", "plan_reserve", "plan_wait"} & set(c.status_log), c.status_log
        cash = sum(u for _, u, cat, _ in c.cash if cat != "stages")
        assert cash == pytest.approx(c.spent, abs=0.01)          # every dollar of the ledger has a category
        assert {cat for _, _, cat, _ in c.cash} <= set(R6.CATS)
    sp = out["r6"]["spend"]
    assert set(sp["totals"]["lab"]) == set(R6.LAB_CATS) and sp["totals"]["lab"]["capital_new"] == 0   # nothing built
    assert sp["totals"]["lab"]["labour"] > 0 and sp["totals"]["lab"]["facility"] > 0
    for k in tw.campaigns:
        for cat in R6.CATS:
            w = sp["campaigns"][k][cat]
            assert all(b >= a - 1e-6 for a, b in zip(w, w[1:])) or cat == "stock"      # cumulative
        assert sp["campaigns"][k]["stock"][-1] == pytest.approx(sp["totals"]["campaigns"][k]["stock"], abs=0.01)
    json.dumps(out, allow_nan=False)                             # no infinity leaks into a row


def test_spend_exceeds_round5s_budget_when_the_lab_can_use_it():
    out, tw = _short(B6._cfg("vertical", "parallel", "fast", "reorder", 0), 300)
    al = out["campaigns"]["flaime_al"]
    assert al["spent"] > R6.REFERENCE_USD["flaime_al"]            # round 5 stopped at $240k
    lab = out["r6"]["spend"]["totals"]["lab"]
    assert lab["capital_new"] > 1e6 and lab["capital_used"] > 0
    cr = out["r6"]["crucibles"]
    assert cr["derived_cycle_start_d"] == pytest.approx(cr["cell_d"])     # the pool is in long before the cell
    assert cr["families"]["flaime_al"]["melts"] > 300
    assert out["r6"]["money"]["limited"] is False


# ------------------------------------------------------------------------------------------------- the stream
def test_stream_at_scale_keeps_memory_small_and_designs_recoverable():
    out, tw = _short(B6._cfg("conventional", "external", "fast", "lean", 2, hpc=dict(scale=16)), 20)
    for k, c in tw.campaigns.items():
        S = tw.stream[k]
        hp = out["r6"]["hpc"]
        assert hp["keep"] == 128 * 16 and hp["add_per_day"] == 64 * 16
        assert S["materialized"] > 15000 and len(S["pool"]) <= hp["keep"]
        assert len(c.designs) < S["materialized"] / 4 and c._gone > 0
        assert sum(1 for x in c.sims if x.get("stream")) <= hp["keep"] + len(c._refs)
        # a candidate dropped from memory comes back, the same design under the same id
        starts, metas = c._batches
        j, did = next((j, d) for j in range(3, 60) if metas[j][2] is None
                      for d in range(starts[j], starts[j] + metas[j][1]) if d not in c.designs)
        design = c._vi[did]
        assert c.design_id(design) == did and did in c.designs
        again = c.space.sample(metas[j][1], seed=metas[j][0])[did - starts[j]]
        assert design == again
        with pytest.raises(KeyError):
            c._vi[10 ** 9]


def test_a_repeated_composition_is_never_dropped():
    out, tw = _short(B6._cfg("vertical", "parallel", "fast", "reorder", 0), 12)
    c = tw.campaigns["onr_cu"]
    for x in c.sims:                                              # every result's design is still there
        assert x["design"] in c.designs or c._restore(x["design"]) is not None


# ------------------------------------------------------------------------------------------------- policies, the grid
def test_network_policies_have_no_money_rules():
    for name in ("bofn3", "pkgfn3"):
        for key in ("flaime_al", "onr_cu"):
            p = net6.make6(name, key, 0)
            assert p.can_start_new(dict(budget_left=0.0)) and p._screen_share_ok(dict(spent=0.0))
            assert p.name == name and p.denom == "time"
    assert net6.make6("pkgfn3", "onr_cu", 0).acq == "kg" and net6.make6("bofn3", "onr_cu", 0).acq == "ei"


def test_grid():
    ids = B6.by_id()
    assert len(ids) == sum(len(v) for v in B6.EXPERIMENTS.values())
    groups = {}
    for name, cfgs in B6.EXPERIMENTS.items():
        for c in cfgs:
            groups.setdefault((name, B6.group_key(c)), []).append(c["seed"])
    assert all(sorted(s) == list(range(16)) for s in groups.values())         # 16 seeds for every arm
    for name in B6.EXPERIMENTS:                                              # every sensitivity with all three
        pols = {c["policy"] for c in B6.EXPERIMENTS[name]}
        assert pols == {"fast", "bofn3", "pkgfn3"}, name
    assert len(B6.EXPERIMENTS["arms"]) == 4 * 3 * 16
    assert set(B6.TIERS) == set(B6.EXPERIMENTS)
    c = B6._cfg("vertical", "parallel", "fast", "reorder", 3, decisions="slow", late=240, hpc=16)
    assert B6.run_id(c) == "r6_vertical_parallel_fast_reorder_s3_dec-slow_hpc16_late240"
    order = [B6.run_id(c) for _, c in B6.order([(n, c) for n, cs in B6.EXPERIMENTS.items() for c in cs])]
    assert order[0].startswith("r6_") and "_s0" in order[0] and len(set(order)) == len(order)

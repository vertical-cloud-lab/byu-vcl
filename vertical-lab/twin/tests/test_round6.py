"""Round 6's engine (twin/round6.py), policies (twin/opt/net6.py) and runner (twin/bench6.py): short runs only."""
from __future__ import annotations

import json
import math
import os

import numpy as np
import pytest

os.environ.setdefault("TWIN6_OUT", "/tmp/twin6_test")

from twin import bench6 as B6  # noqa: E402
from twin import round4 as R4  # noqa: E402
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
    other = next(sc for sc in B6.HPC_SCALES if sc != B6.HPC_SCALE)
    c = B6._cfg("vertical", "parallel", "fast", "reorder", 3, decisions="slow", late=240, hpc=other)
    assert B6.run_id(c) == f"r6_vertical_parallel_fast_reorder_s3_dec-slow_hpc{other}_late240"
    scales = sorted({c["opts"]["hpc"]["scale"] for n in B6.EXPERIMENTS for c in B6.EXPERIMENTS[n]})
    assert scales == sorted(B6.HPC_SCALES)                                   # every scale is in the grid once
    assert B6.run_id(B6._cfg("vertical", "parallel", "fast", "reorder", 3)) == "r6_vertical_parallel_fast_reorder_s3"
    assert B6._cfg("vertical", "parallel", "fast", "reorder", 3)["opts"]["hpc"]["scale"] == B6.HPC_SCALE
    order = [B6.run_id(c) for _, c in B6.order([(n, c) for n, cs in B6.EXPERIMENTS.items() for c in cs])]
    assert order[0].startswith("r6_") and "_s0" in order[0] and len(set(order)) == len(order)


# ------------------------------------------------------------------------------------------------- round 6 additions
SURVEY_COLS = ["lab", "station", "component", "item", "qty", "new_usd_each", "new_lead_w_vendor", "new_lead_text",
               "twin_lead_w", "market", "used_ok", "n_listings", "n_north_america", "n_priced", "n_current_bids",
               "n_exact", "n_family", "n_substitute", "median_used_usd", "median_exact_family_usd",
               "n_priced_exact_family", "p25_used_usd", "p75_used_usd", "min_used_usd", "max_used_usd",
               "median_bid_usd", "discount_vs_new", "freight_rigging_usd", "median_delivered_usd", "price_frac",
               "lead_w", "lead_sigma", "new_parts_lead_w", "lead_w_with_new_parts", "p_fault", "p_fault_best",
               "refurb_w", "refurb_sigma", "refurb_frac",
               "refurb_source", "extra_com_w", "share_as_is", "share_used", "share_tested", "share_refurb_or_warranty",
               "share_new_surplus", "share_of_new_bought_used", "wt", "new_source", "note"]


def test_market_file_in_the_surveys_own_format(tmp_path):
    """twin/market6.py (issue 424) writes one row per station and, for a station that is several machines, one per
    machine as well: only the station's own row counts."""
    import csv
    rows = [dict(station="sem", component="", market="yes", used_ok="True", n_listings="12", price_frac="0.31",
                 lead_w="3.5", lead_sigma="0.4", p_fault="0.18", refurb_w="5", refurb_sigma="0.4", refurb_frac="0.12",
                 extra_com_w="1.5", median_delivered_usd="61000", new_usd_each="196000"),
            dict(station="machining", component="lathe", market="yes", used_ok="", n_listings="30",
                 price_frac="0.2", lead_w="2"),                                  # a component: not read
            dict(station="machining", component="(station)", market="yes (lathe)", used_ok="True", n_listings="31",
                 price_frac="0.7", lead_w="2.5", new_parts_lead_w="20", lead_w_with_new_parts="20", p_fault="0.2"),
            dict(station="pip", component="", market="none", used_ok="False", n_listings="0")]
    p = tmp_path / "summary.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=SURVEY_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in SURVEY_COLS})
    m = R6.load_market(p)
    assert set(m) == {"sem", "machining", "pip"}
    assert m["machining"]["price_frac"] == 0.7 and m["machining"]["market_text"] == "yes (lathe)"
    # bought partly used, the cell is on site when its new parts are: the station's lead, not its used parts'
    assert (m["machining"]["lead_w"], m["machining"]["lead_w_used_parts"]) == (20.0, 2.5)
    assert m["pip"]["ok"] is False and "price_frac" not in m["pip"]
    ps = R6.used_params("sem", m)
    assert (ps["ok"], ps["price_frac"], ps["lead_w"], ps["p_fault"], ps["refurb_w"]) == (True, 0.31, 3.5, 0.18, 5.0)
    assert ps["market"] == "yes" and "summary.csv" in ps["source"]
    assert R6.market_sha256(p) is not None and R6.market_sha256(tmp_path / "none.csv") is None
    f = R6.Facility6("parallel", 0, 1000 * H, dict(lab="vertical", market_csv=str(p)))
    assert f.market_sha == R6.market_sha256(p) and f.sched["used_source"] == "out/twin6/market/summary.csv"


class _RowWise:
    """A stand-in for a fitted GP node whose prediction for a row depends on that row alone (sums along the row),
    so that batched and one-at-a-time predictions must agree exactly."""

    def __init__(self, d, seed=5):
        r = np.random.default_rng(seed)
        self.w1, self.w2 = r.normal(size=d), r.normal(size=d)

    def ready(self):
        return True

    def predict(self, X):
        X = np.asarray(X, float)
        return (X * self.w1).sum(axis=1), np.abs((X * self.w2).sum(axis=1)) + 0.01


def test_faster_atomizer_search_is_the_same_search():
    import copy

    from twin.opt import policies2 as P2
    out, tw = _short(B6._cfg("conventional", "external", "bofn3", "lean", 0), 4)
    for k, c in tw.campaigns.items():
        pol = c.policy
        v = c.view(tw.h)
        dids = [s["design"] for s in v["sims"] if s["kind"] == pol.sim_kind][:40]
        assert len(dids) >= 20
        d = len(pol.atom_x(v, dids[0], v["design_inputs"][dids[0]]))
        pol.nodes["atomize"] = [_RowWise(d)]
        g0 = copy.deepcopy(pol.gen.bit_generator.state)
        for did in dids[:6]:
            pol.gen.bit_generator.state = copy.deepcopy(g0)
            a = P2.BOFN.atomizer_settings(pol, v, did, dict(v["design_inputs"][did]))
            ga = copy.deepcopy(pol.gen.bit_generator.state)
            pol.gen.bit_generator.state = copy.deepcopy(g0)
            b = pol.atomizer_settings(v, did, dict(v["design_inputs"][did]))
            assert a == b and pol.gen.bit_generator.state == ga       # the same choice, the same draws used
        pol.gen.bit_generator.state = copy.deepcopy(g0)
        p_one = N3_p_powder(pol, v, dids)
        pol.gen.bit_generator.state = copy.deepcopy(g0)
        p_batch = pol._p_powder(v, dids)
        assert np.array_equal(p_one, p_batch)


def N3_p_powder(pol, v, dids):
    from twin.opt import net3 as N3
    return N3.Net3._p_powder(pol, v, dids)


def test_the_portable_pin():
    from twin import repro as R
    pin = R.PINS["portable"]
    for k, v in R.PINS["avx2"].items():
        assert pin[k] == v                                       # round 5's pin, and more
    assert pin["MKL_CBWR"] == "COMPATIBLE" and pin["OPENBLAS_L2_SIZE"] == "256"
    assert set(pin["NPY_DISABLE_CPU_FEATURES"].split(",")) >= {"X86_V4", "AVX512_ICL", "AVX512_SPR"}
    fp = dict(pin="portable", hash_pinned=True, pin_late=False, numpy_simd=dict(enabled=["X86_V3"]),
              mkl=dict(cnr="COMPATIBLE", threads=1), blas=[], torch_cpu="AVX2", torch_threads=1,
              pin_env=dict(pin))
    assert R.problems6(fp) == []
    bad = dict(fp, pin_env={k: v for k, v in pin.items() if k != "OPENBLAS_L2_SIZE"})
    assert any("OPENBLAS_L2_SIZE" in x for x in R.problems6(bad))
    assert B6.PIN == "portable" and B6.timings({}) == {}


def test_engine_reads_the_committed_survey_as_market6_does():
    """Every station the automated lab builds: the engine's reading of out/twin6/market/summary.csv gives the same
    eight numbers and the same used_ok as the survey's own reader (twin/market6.py used_params)."""
    from twin import market6 as M6
    m, m6 = R6.load_market(), M6.load()
    assert m, "out/twin6/market/summary.csv is missing"
    for k in R4.BUILD:
        p, q = R6.used_params(k, m), M6.used_params(k, m6)
        for f in ("ok", "lead_w", "lead_sigma", "price_frac", "p_fault", "refurb_w", "refurb_sigma", "refurb_frac",
                  "extra_com_w"):
            assert p[f] == q[f], (k, f, p[f], q[f])


def test_stations_without_a_used_market():
    """The survey found no used market the lab would buy from for these (Sterling's list on PR 427, and the rest):
    they are bought new in every seed, and every row says so per station."""
    none = R6.no_used_market()
    assert {"pip", "nanoindenter", "chamber", "carvera"} <= set(none)
    assert not {"edm", "instron"} & set(none)
    m = R6.load_market()
    for seed in range(6):
        s = R6.build_schedule6(seed, "parallel", market=m)
        assert not set(s["used"]) & set(none)
        assert set(s["used"]) <= {k for k, v in s["used_rule"].items() if v["bought_used"]}
        assert all(not v["bought_used"] for k, v in s["used_rule"].items() if k in none)
    assert not R6.build_schedule6(0, "parallel", opts=dict(used=False), market=m)["used"]


def test_timings_use_measured_variant_ratios():
    """A lean-stock group and the automated lab's wait plan are priced from the stocked parallel arm times the ratio a
    two-year run measured (its own policy's, else its class's), the stream's cost taken out first."""
    g = {"r6_vertical_parallel_bofn3_reorder": {"full": dict(seconds=1, cpu_seconds=7000, scale=64)},
         "r6_vertical_parallel_pkgfn3_reorder": {"full": dict(seconds=1, cpu_seconds=8000, scale=64)},
         "r6_vertical_parallel_bofn3_lean": {"full": dict(seconds=1, cpu_seconds=9000, scale=64)},
         "r6_vertical_wait_bofn3_reorder": {"full": dict(seconds=1, cpu_seconds=4000, scale=64)}}
    k = {"gp": {"vertical": 0.05, "conventional": 0.05}, "fast": {"vertical": 0.03, "conventional": 0.03}}
    tm = B6.timings(g, k)
    s = 0.05 * 64 * B6.DAYS
    lean, wait = (9000 - s) / (7000 - s), (4000 - s) / (7000 - s)
    assert tm["r6_vertical_parallel_bofn3_lean"]["how"].startswith("measured")
    assert math.isclose(tm["r6_vertical_parallel_pkgfn3_lean"]["seconds_2y"], (8000 - s) * lean + s, abs_tol=0.1)
    assert math.isclose(tm["r6_vertical_parallel_pkgfn3_lean_dec-slow"]["seconds_2y"], (8000 - s) * lean + s,
                        abs_tol=0.1)
    assert math.isclose(tm["r6_vertical_wait_pkgfn3_reorder"]["seconds_2y"], (8000 - s) * wait + s, abs_tol=0.1)
    assert "round 5's" in tm["r6_vertical_external_pkgfn3_reorder"]["how"]          # not measured: round 5's ratio
    assert math.isclose(tm["r6_vertical_parallel_pkgfn3_reorder_hpc16"]["seconds_2y"], 8000 - 0.05 * 48 * B6.DAYS,
                        abs_tol=0.1)

"""The queue model behind notes/vertical_lab_worth_it.md (twin/worth_it.py, issue #407).

Small synthetic logs check the mechanics (a tray's handling time, the tray lock, the aisle rule, the attended time,
the outside load's rate); the committed event logs check that the replay reproduces the twin when handling takes no
time, and that every internal step finishes.
"""
import math

import pytest

from twin import worth_it as W

LOG = W.EVENTS / "r3_vertical_lab_bofn3_s0.json.xz"
ZERO = dict(v_mm=1e6, a_mm=1e9, t_dock=0.0, t_arm=0.0, t_rack=0.0, t_fetch=0.0, t_store=0.0, t_tray_loc=0.0)


def _log(events, days=3):
    stations = {k: dict(name=k, units=W.DEFAULT_UNITS.get(k, 1), hours="24/7", external=False) for k in W.STATIONS}
    stations.update(robot=dict(units=2, hours="24/7", external=False), operator=dict(units=1, hours="day6"))
    evs = [dict(t0_h=t0, t1_h=t1, station=st, campaign="flaime_al", what="x", design=d, node="n")
           for st, t0, t1, d in events]
    return dict(meta=dict(horizon_days=days, cfg={}), stations=stations, events=evs,
                designs={"flaime_al": {}, "onr_cu": {}}, results=[], curves={})


def _run(log, layout, n_mm, **prm):
    sim = W.Sim(log, layout, n_mm, 0.0, W.Params(**prm), seed=0)
    out = sim.run()
    return sim, out


def test_drive_time_is_a_trapezoid_or_a_triangle():
    p = W.Params(v_mm=0.8, a_mm=0.3)
    assert W.drive_s(0.0, p) == 0.0
    assert W.drive_s(10.0, p) == pytest.approx(10.0 / 0.8 + 0.8 / 0.3)
    assert W.drive_s(1.0, p) == pytest.approx(2.0 * math.sqrt(1.0 / 0.3))
    d = 0.8 ** 2 / 0.3                     # the two meet where the unit just reaches its top speed
    assert W.drive_s(d, p) == pytest.approx(W.drive_s(d * (1 + 1e-9), p), rel=1e-6)


@pytest.mark.parametrize("prefetch", [False, True])
def test_one_tray_step_takes_the_drive_the_dock_the_fetch_and_the_load(prefetch):
    p = W.Params(prefetch=prefetch)
    sim, _ = _run(_log([("byu_sem", 1.0, 2.0, 1)]), "vlm", 1, prefetch=prefetch, credit_h=0.0)
    j = sim.jobs[0]
    drive = W.drive_s(W.vert_dist(W.VERT_CHARGER, W.VERT_DOCKS["vlm1"]), p)
    fetch_wait = 0.0 if prefetch else p.t_fetch           # the drive (> 26 s) hides a fetch started at once
    loaded = 1.0 + (drive + p.t_dock + fetch_wait + p.t_tray_loc + p.t_arm + p.t_rack) / 3600.0
    # the unit has nothing else to do, so it lets the tray go and the run starts when the tray is back in its slot
    assert j["t_start"] == pytest.approx(loaded + p.t_store / 3600.0)
    assert j["t_end"] == pytest.approx(j["t_start"] + 1.0)


def test_a_running_instrument_holds_its_tray_so_its_neighbour_waits():
    events = [("byu_sem", 1.0, 3.0, 1), ("psd", 1.2, 1.7, 2)]   # SEM on tray D, the Mastersizer on tray E
    sim, _ = _run(_log(events), "vlm", 1)
    assert sim.jobs[1]["t_start"] < sim.jobs[0]["t_end"]        # different trays: no wait
    events = [("byu_sem", 1.0, 3.0, 1), ("density", 1.2, 1.7, 2)]
    log = _log(events)
    W.STATIONS["_xrd_on_D"] = dict(flat="D1", vert=[W._T(1, "D")])
    try:
        log["events"][1]["station"] = "_xrd_on_D"
        log["stations"]["_xrd_on_D"] = dict(units=1, hours="24/7", external=False)
        sim, _ = _run(log, "vlm", 1)
        assert sim.jobs[1]["t_start"] >= sim.jobs[0]["t_end"]   # the same tray: it waits for the SEM's run
        sim, _ = _run(log, "vlm", 1, lock="never")
        assert sim.jobs[1]["t_start"] < sim.jobs[0]["t_end"]
        sim, _ = _run(log, "flat", 1)
        assert sim.jobs[1]["t_start"] < sim.jobs[0]["t_end"]    # on benches nothing moves
    finally:
        del W.STATIONS["_xrd_on_D"]


def test_one_unit_in_an_aisle_at_a_time_on_the_flat_plan():
    assert W.flat_aisle("D1") == W.flat_aisle("F0") != W.flat_aisle("D0")
    events = [("psd", 1.0, 2.0, 1), ("prep", 1.0, 2.0, 2)]      # docks D1 and F0, the same aisle
    sim, _ = _run(_log(events), "flat", 2)
    a, b = sorted(sim.jobs, key=lambda j: j["t_start"])
    sim2, _ = _run(_log(events), "flat", 2, aisle_exclusive=False)
    a2, b2 = sorted(sim2.jobs, key=lambda j: j["t_start"])
    assert b["t_start"] > b2["t_start"]


def test_attended_time_by_mode():
    assert W.attend_h("doser", 2.0, "none") == 0.0
    assert W.attend_h("doser", 2.0, "pr332") == pytest.approx(1.6)
    assert W.attend_h("doser", 2.0, "cells") == 0.0              # the powder line has its own cell
    assert W.attend_h("xrd", 0.75, "cells") == pytest.approx(0.375)
    assert W.attend_h("furnace", 4.0, "cells") == pytest.approx(0.05)
    assert W.attend_h("furnace", 0.01, "cells") == pytest.approx(0.01)   # never more than the step
    assert W.attend_h("immersion", 720.0, "pr332") == 0.0
    with pytest.raises(ValueError):
        W.attend_h("xrd", 1.0, "some")


def test_the_twins_transfer_is_inside_the_step():
    sim0, _ = _run(_log([("byu_sem", 1.0, 2.0, 1)]), "flat", 1, credit_h=0.0)
    sim1, _ = _run(_log([("byu_sem", 1.0, 2.0, 1)]), "flat", 1)
    assert sim1.jobs[0]["t_end"] == pytest.approx(sim0.jobs[0]["t_end"] - 0.1)
    sim2, _ = _run(_log([("byu_icpms", 1.0, 1.1, 1)]), "flat", 1)      # never more than half a short step
    assert sim2.jobs[0]["t_end"] - sim2.jobs[0]["t_start"] == pytest.approx(0.05)


def test_one_unit_charges_at_a_time():
    sim = W.Sim(_log([], days=30), "flat", 2, 0.6, W.Params(attend="cells"), seed=1)     # both units saturated
    seen = []
    orig = sim._on_charged

    def charged(m):
        seen.append(sum(1 for o in sim.mm if o["charging"]))
        orig(m)
    sim._on_charged = charged
    sim.run()
    assert seen and max(seen) <= 2
    assert sum(1 for n in seen if n == 2) <= len(seen) // 4      # both at once only when one is out of reserve


def test_attended_time_holds_the_unit_and_the_opening_but_not_the_run():
    events = [("xrd", 1.0, 2.0, 1)]
    sim0, out0 = _run(_log(events), "vlm", 1)
    sim1, out1 = _run(_log(events), "vlm", 1, attend="cells")
    assert sim1.jobs[0]["t_end"] == pytest.approx(sim0.jobs[0]["t_end"], abs=1e-9)   # the run keeps its length
    assert out1["mm_busy"] > out0["mm_busy"]
    assert out1["openings"][1]["busy"] > out0["openings"][1]["busy"]


def test_outside_catalogue_is_the_twins():
    cloud = pytest.importorskip("twin.cloud")
    want = {}
    for c in cloud.CATALOGUE:
        if c["station"] in ("atomizer", "byu_icpms"):
            continue
        want.setdefault(c["station"], []).append((c["h"], c["cv"]))
    assert {k: sorted(v) for k, v in want.items()} == {k: sorted(v) for k, v in W.EXT_JOBS.items()}


def test_outside_jobs_arrive_at_the_rate_that_gives_the_load():
    sim = W.Sim(_log([], days=400), "flat", 2, 0.3, W.Params(), seed=3)
    hours = {}
    for _, _, kind, j in sim.heap:
        if kind == "release" and j["ext"]:
            hours[j["station"]] = hours.get(j["station"], 0.0) + j["dur"]
    for st in ("psd", "xrd", "pip", "tensile"):
        units = W.EXT_UNITS.get(st, len(sim.units[st]))
        assert hours[st] / (sim.H * units) == pytest.approx(0.3, rel=0.06), st


def test_internal_steps_wait_for_their_predecessor():
    log = _log([("psd", 1.0, 2.0, 7), ("byu_sem", 2.0, 3.0, 7), ("byu_sem", 2.5, 3.0, 8)])
    jobs = W.internal_jobs(log)
    assert (jobs[1]["pred"], jobs[1]["pred_kind"]) == (0, "chain")       # the same design: needs the sample
    assert (jobs[2]["pred"], jobs[2]["pred_kind"]) == (0, "decision")    # a new design: waits for the result


@pytest.mark.skipif(not LOG.exists(), reason="needs the committed event logs (out/twin3b/events)")
@pytest.mark.parametrize("layout", ["flat", "vlm"])
def test_with_no_handling_time_the_replay_is_the_twin(layout):
    log = W.load_log(LOG)
    sim = W.Sim(log, layout, 2, 0.0, W.Params(lock="never", credit_h=0.0, **ZERO), seed=0)
    out = sim.run()
    n = sum(1 for j in sim.jobs if j["t0"] < sim.H)
    assert out["internal"]["done"] == n
    # within a second: the "zero" drive still takes d / v + v / a = 1 ms each
    assert max(abs(sim.t_end[j["id"]] - j["t1"]) for j in sim.jobs if j["id"] in sim.t_end) < 1.0 / 3600
    # with the twin's 6 min transfer credited back, no step ends later than the twin's
    sim = W.Sim(log, layout, 2, 0.0, W.Params(lock="never", **ZERO), seed=0)
    sim.run()
    assert max(sim.t_end[j["id"]] - j["t1"] for j in sim.jobs if j["id"] in sim.t_end) < 1.0 / 3600


@pytest.mark.skipif(not LOG.exists(), reason="needs the committed event logs (out/twin3b/events)")
@pytest.mark.parametrize("layout,n_mm,attend", [("vlm", 1, "none"), ("flat", 2, "none"), ("vlm", 2, "cells")])
def test_every_internal_step_finishes(layout, n_mm, attend):
    log = W.load_log(LOG)
    sim = W.Sim(log, layout, n_mm, 0.0, W.Params(attend=attend), seed=0)
    out = sim.run()
    assert out["internal"]["done"] == sum(1 for j in sim.jobs if j["t0"] < sim.H)
    assert -0.1 <= out["internal"]["end_delay_h"] < 2.0     # the twin's 6 min is credited back, so it can be < 0
    assert 0.0 < out["mm_busy"] < 0.1


@pytest.mark.skipif(not LOG.exists(), reason="needs the committed event logs (out/twin3b/events)")
def test_days_to_targets_move_with_the_replay():
    pytest.importorskip("numpy")
    log = W.load_log(LOG)
    jobs = W.internal_jobs(log)
    refs = W.reference_filter(log)
    base = W.days_to_targets(log, jobs, None, refs)
    same = W.days_to_targets(log, jobs, {j["id"]: j["t1"] for j in jobs}, refs)
    later = W.days_to_targets(log, jobs, {j["id"]: j["t1"] + 24.0 for j in jobs}, refs)
    assert same == base
    for k, d in base.items():
        if d is not None:
            assert later[k] == pytest.approx(d + 1.0)

"""Checks of the animated lab's schedule (twin/video/lab3d_sched.py): no VTK, a second or two."""
import math
import re
from pathlib import Path

import numpy as np
import pytest

from twin.video import data as D
from twin.video import lab3d_sched as LS

HERE = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def kin():
    if not LS.KIN.exists():
        pytest.skip("out/twin2/video/lab3d/kin.json not built")
    return LS.load_kin()


@pytest.fixture(scope="module")
def week(kin):
    R = D.Replay(D.EVENTS_DIR / "vertical_lab_bofn_blend_s0.json")
    clock = LS.Clock.linear(24.0 * 119, 2.8, 60.0)
    return R, LS.plan(R, kin, clock)


def test_tower_timings_are_the_set_up_movies():
    """The scheduler's tower timings are setup_lab.TwoLab.fetch/store's: lift at 1333 mm/s (at least 0.6 s), 2.2 s
    slides, 0.7 s shutter."""
    src = (HERE / "setup_lab.py").read_text()
    body = src[src.index("    def fetch(self, k, label, caption, fast=1.0"):src.index("def add_tray(")]
    assert "abs(self.lift_z - zs) / 1333" in body and "abs(zs - zt) / 1333" in body
    assert body.count("2.2 * fast") == 4 and body.count("0.7 * fast") == 4
    assert "mint=0.6" in body
    assert (LS.LIFT_MM_S, LS.LIFT_MIN_S, LS.SLIDE_S, LS.SHUTTER_S) == (1333.0, 0.6, 2.2, 0.7)


def test_mir_figures_are_warehouses():
    src = (HERE / "warehouse.py").read_text()
    assert re.search(r"^SPEED = 1500\.0", src, re.M)
    assert "abs(turn) / 60.0" in src
    assert (LS.DRIVE_MM_S, LS.TURN_DEG_S) == (1500.0, 60.0)


def test_profiles_end_where_they_should(kin):
    yo, zo = kin["open"]
    for k, t in kin["trays"].items():
        f = LS.fetch_profile(kin, k, kin["lift_home"])
        assert f[-2][1] == "slide" and f[-2][3] == yo
        s = LS.store_profile(kin, k)
        assert s[-1][1] == "slide" and s[-1][3] == t["y"] and s[-2][3] == t["z"]
        assert 6.0 < LS.profile_seconds(f) < 20.0 and 6.0 < LS.profile_seconds(s) < 20.0


def test_routes_end_on_their_docks(kin):
    fl = LS.Floor(kin)
    places = list(kin["docks"]) + list(range(len(kin["chargers"])))
    for a in places:
        for b in places:
            if a == b:
                continue
            segs = fl.route(a, b)
            end = LS.segs_end(segs, fl.place(a)[0])
            p1 = fl.place(b)[0]
            assert math.hypot(end[0] - p1[0], end[1] - p1[1]) < 1.0, (a, b)
            assert abs(LS._wrap(end[2] - p1[2])) < 0.6, (a, b)
            # every drive leg is straight along x or y (pivots between), so a unit stays on the floor's lines
            for dur, p, q in segs:
                assert dur >= 0
                if (p[0], p[1]) != (q[0], q[1]):
                    assert abs(p[0] - q[0]) < 1e-6 or abs(p[1] - q[1]) < 1e-6, (a, b, p, q)


def test_moves_never_overlap(week):
    R, p = week
    for s, ms in p.towers.items():
        for m0, m1 in zip(ms, ms[1:]):
            assert m1.v0 >= m0.v1 - 1e-9, (s, m0, m1)
        # fetch and store alternate, each store taking back the tray fetched
        for m0, m1 in zip(ms, ms[1:]):
            assert m0.kind != m1.kind
            if m0.kind == "fetch":
                assert m1.tray == m0.tray
    for acts in p.units:
        for a0, a1 in zip(acts, acts[1:]):
            assert a1.v0 >= a0.v1 - 1e-9


def test_a_unit_works_at_the_opening_while_its_tray_is_there(week):
    R, p = week
    n = 0
    for acts in p.units:
        for a in acts:
            if a.kind != "work" or a.where not in ("vlm", "vlm2"):
                continue
            s = 1 if a.where == "vlm" else 2
            for v in np.linspace(a.v0, a.v1, 5)[1:-1]:
                st = p.tower_state(s, v)
                assert st["out"] is not None, (a, v)
            n += 1
    assert n > 5


def test_idle_trays_stay_home_and_drawn_requests_were_drawn(week, kin):
    R, p = week
    for v in np.linspace(0, 60, 241):
        for s, ts in p.state(v)["towers"].items():
            assert len(ts["trays"]) <= 1                  # one extractor: one tray out of its slot at a time
            for k in ts["trays"]:
                assert kin["trays"][k]["shuttle"] == s
    shown = {}                                          # tray -> [(fetch starts, store ends)]
    for s, ms in p.towers.items():
        for m0, m1 in zip(ms, ms[1:] + [None]):
            if m0.kind == "fetch":
                shown.setdefault(m0.tray, []).append((m0.v0, m1.v1 if m1 is not None else 1e9))
    for r in p.reqs:
        if r.kind == "tray" and r.drawn:
            # served by a presentation of its tray that starts after it reaches the clock, or was already out
            assert any(a >= r.v - 1e-6 or a <= r.v <= b for a, b in shown.get(r.where, [])), r
    c = p.counts
    assert 0 < c["tray_drawn"] <= c["tray_asked"] and 0 < c["floor_drawn"] <= c["floor_asked"]


def test_plan_is_deterministic(week, kin):
    R, p = week
    p2 = LS.plan(R, kin, LS.Clock.linear(24.0 * 119, 2.8, 60.0))
    assert [p.key(v) for v in np.linspace(0, 60, 61)] == [p2.key(v) for v in np.linspace(0, 60, 61)]


def test_move_rate():
    assert LS.move_rate(1.0) == LS.MOVE_RATE
    assert LS.move_rate(1e3) == 2 * LS.MOVE_RATE
    assert LS.move_rate(10.0) > LS.move_rate(5.0)

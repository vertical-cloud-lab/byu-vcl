"""The two-year cut (twin/video/cut5.py, replay5.py, data5.py) against round 5's committed results.

    TWIN_VIDEO_ROUND=5 python -m pytest -q twin/tests/test_video_round5.py

What the issue asked of the replay and of the cut's own lines, as checks: one seed for the whole replay, and it is
the one the round's notes name; every counter on screen ends on the row's own; the clock is continuous from day 0 to
the horizon; a flat best-so-far curve always has a reason; the cut's own lines hold no typed-in number; and the round
is one switch.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[2]
if os.environ.get("TWIN_VIDEO_ROUND", "") not in ("5",):
    pytest.skip("round 5's cut: run with TWIN_VIDEO_ROUND=5", allow_module_level=True)

sys.path.insert(0, str(HERE))
from twin.video import data as D          # noqa: E402
from twin.video import data5 as D5        # noqa: E402
from twin.video import replay5 as R5      # noqa: E402


def test_the_round_is_one_switch():
    assert D.ROUND == 5 and D.R5
    assert D.RES == HERE / "out" / "twin5" and D.VID == HERE / "out" / "twin5" / "video"
    # another round reads its own folder: nothing but the environment variable changes
    out = subprocess.run([sys.executable, "-c", "from twin.video import data as D; print(D.ROUND, D.RES.name, D.VID.parent.name)"],
                         cwd=HERE, env=dict(os.environ, TWIN_VIDEO_ROUND="6"), capture_output=True, text=True)
    assert out.stdout.split() == ["6", "twin6", "twin6"], out.stderr[-400:]


def test_the_replayed_seed_is_the_one_the_notes_name():
    I = D5.info()
    assert I["is_median_seed"]
    assert I["arm"] == "r5_vertical_parallel_bofn3_reorder" and I["conv_arm"] == "r5_conventional_external_bofn3_reorder"
    # notes/twin_round5.md, section 7.13, and tables.md's "Median seed for both campaigns together"
    notes = (HERE / "notes" / "twin_round5.md").read_text()
    m = re.search(r"\| automated, stocked, BOFN \| (\d+) \| (\d+), (\d+) \((\d+), (\d+)\) \| (\d+), (\d+) \((\d+), (\d+)\)", notes)
    assert m, "the notes' row for the replayed arm"
    seed, a1, a2, ma1, ma2, c1, c2, mc1, mc2 = (int(x) for x in m.groups())
    assert I["seed"] == seed
    d = I["auto"]["campaigns"]
    assert [round(d["flaime_al"]["days"][t]["day"]) for t in ("T1", "T2")] == [a1, a2]
    assert [round(d["onr_cu"]["days"][t]["day"]) for t in ("T1", "T2")] == [c1, c2]
    ms = I["median_seed"]["medians"]
    assert [round(ms[k]) for k in ("flaime_al|T1", "flaime_al|T2", "onr_cu|T1", "onr_cu|T2")] == [ma1, ma2, mc1, mc2]
    tables = (HERE / "out" / "twin5" / "tables.md").read_text()
    assert f"| `{I['arm']}` | {seed} |" in tables


def test_one_seed_for_the_whole_replay_in_both_labs():
    I = D5.info()
    a, c = R5.R("auto"), R5.R("conv")
    assert a.path.name == f"{I['arm']}_s{I['seed']}.json.xz" and c.path.name == f"{I['conv_arm']}_s{I['seed']}.json.xz"
    assert a.seed == c.seed == I["seed"]
    assert a.meta["policy"] == c.meta["policy"] and a.meta["stock"] == c.meta["stock"]
    # every 3-D job draws the same clock over the same run
    js = R5.jobs()
    assert {j["clock"] for j in js} == {"replay5"} and {j["dur"] for j in js} == {R5.tl().dur}
    assert js[0]["v0"] == 0.0 and max(j["v1"] for j in js) == pytest.approx(R5.tl().dur)


def test_counters_end_on_the_rows_own():
    for which in ("auto", "conv"):
        r = R5.R(which)
        assert r.check_counters() == []
        for c in D5.CAMPS:
            n = r.counts(c, r.horizon_h + 1)
            row = r.part_info["campaigns"][c]["counters"]
            assert n["lots"] == row["lots_made"] and n["made"] == row["alloys_made"]
            assert n["built"] == row["alloys_printed"] and n["tested"] == row["alloys_tested"]
            assert n["designed"] == pytest.approx(r.part_info["campaigns"][c]["hpc"]["evaluated"])
            # counters never go down
            seq = [r.counts(c, h) for h in np.linspace(0, r.horizon_h, 200)]
            for k in ("designed", "lots", "made", "built", "tested"):
                v = [s[k] for s in seq]
                assert all(b >= a for a, b in zip(v, v[1:]))


def test_the_clock_is_continuous_from_day_0_to_the_horizon():
    T = R5.tl()
    ts = np.linspace(0, T.dur, 4000)
    hs = np.array([T.lab(t)[0] for t in ts])
    assert hs[0] == 0.0 and hs[-1] == pytest.approx(T.horizon, abs=1.0)
    assert np.all(np.diff(hs) >= 0)
    assert np.diff(hs).max() < 2.5 * 24 * (ts[1] - ts[0]) * 6       # no jump: never more than a few days a frame step
    assert T.video(T.R.room_h) < T.video(T.R.cell_h) < T.dur


def test_spend_is_the_runs_own_curve():
    I = D5.info()
    for which in ("auto", "conv"):
        r = R5.R(which)
        for c in D5.CAMPS:
            cc = I[which]["campaigns"][c]
            assert r.spent_at(c, r.horizon_h) == pytest.approx(cc["spend_curve"][-1][1])
            assert r.spent_at(c, r.horizon_h) <= cc["spent"] + 1.0
            v = [r.spent_at(c, h) for h in np.linspace(0, r.horizon_h, 300)]
            assert all(b >= a - 1e-6 for a, b in zip(v, v[1:]))


def test_a_flat_curve_says_why():
    r = R5.R("auto")
    for c in D5.CAMPS:
        n_flat = 0
        for d in range(5, int(r.horizon_days), 5):
            f = r.flat(c, d * 24.0)
            if f is None:
                continue
            n_flat += 1
            assert f["since"] <= d <= f["until"]
            assert all(isinstance(w, str) and w for _, w in f["reasons"])
        assert n_flat > 20
    # the reasons the issue names all occur in this seed: stock, a 30-day immersion, the queue for a station
    seen = set()
    for c in D5.CAMPS:
        for d in range(5, int(r.horizon_days), 3):
            f = r.flat(c, d * 24.0)
            if f:
                seen |= {k for k, _ in f["reasons"]}
    assert {"stock", "immersion", "queue"} <= seen, seen


def test_the_cuts_own_lines_hold_no_typed_number():
    from twin.video import cut5
    rows = cut5.check_own()
    assert rows
    for ln in cut5.resolved():
        assert "{" not in ln["text"]
    f = cut5.facts()
    I = D5.info()
    assert f["seed"] == str(I["seed"]) and f["n_seeds"] == str(I["n_seeds"])
    assert f["auto_al_T1"] == f"{I['auto']['campaigns']['flaime_al']['days']['T1']['day']:.0f}"


def test_parts_of_the_lab_come_online_in_the_twins_order():
    po = R5.part_online()
    r = R5.R()
    assert po["room"] == r.room_h
    assert po["m:aconity"] == r.station_online["utah_midi"] and po["m:ded"] == r.station_online["utah_mxlab"]
    assert po["shuttle1"] == r.build["shuttle"]["online_h"]
    assert all(h >= r.room_h for h in po.values())          # nothing is installed before the space is ready
    a0, a1 = R5.build_alpha(0.0), R5.build_alpha(r.horizon_h)
    assert all(v == R5.GHOST for v in a0.values()) and all(v == 1.0 for v in a1.values())
    # moves only from the cell's integration
    assert float(R5.moves_view().t0.min()) >= r.cell_h

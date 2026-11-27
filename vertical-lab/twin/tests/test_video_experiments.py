"""The experiments chapter (twin/video/experiments.py): the alloys it follows come from the committed logs, the
curves it draws are the twin's own, its numbers are the ones in facts.json, and its narration says only those.

    TWIN_VIDEO_ROUND=3b python -m pytest -q twin/tests/test_video_experiments.py

No frame is encoded here; one frame of each part is drawn at a quarter of the size.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

os.environ.setdefault("TWIN_VIDEO_ROUND", "3b")
HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))

from twin.video import data as D          # noqa: E402
from twin.video import exp_data as X      # noqa: E402

pytestmark = pytest.mark.skipif(not D.R3B, reason="the chapter follows round 3b's replay (TWIN_VIDEO_ROUND=3b)")


def test_follow_comes_from_the_logs():
    """The two alloys are the ones that took each replayed run past its target, read from the committed event logs."""
    f = X.follow()
    parts = {p["campaign"]: p for p in D.replay3b_parts()}
    assert set(f) == set(parts) == {"flaime_al", "onr_cu"}
    for c, a in f.items():
        ev = D._load_json(parts[c]["events"])
        assert a["seed"] == parts[c]["seed"] == ev["meta"]["cfg"]["seed"]
        assert abs(a["day"] - float(parts[c]["day"])) < 1.0            # demonstrated on the median seed's day
        row = [r for r in ev["results"] if r["campaign"] == c and r["type"] == "demonstrated"
               and r["design"] == a["design"]]
        assert len(row) == 1 and row[0]["u_true"] == row[0]["best_true"] == a["u_true"] > 0
        assert a["composition"] == ev["designs"][c][str(a["design"])]
        before = [r["best_true"] for r in ev["results"] if r["campaign"] == c and r["type"] == "demonstrated"
                  and r["t_h"] < row[0]["t_h"]]
        assert max(before) < a["u_true"]                                # it set the run's best so far


def test_same_hidden_alloy_as_the_run():
    """Made again through the truth with the run's seed, the part's true strength is the log's alloy (other process
    settings, so not the same number): within 6 % in yield and 2 points in elongation."""
    f = X.follow()
    for c in f:
        a = X.alloy(c)
        s = a.part["strength"]
        assert abs(s["ys_MPa"] / f[c]["ys"] - 1) < 0.06, (c, s["ys_MPa"], f[c]["ys"])
        assert abs(s["el_pct"] - f[c]["el"]) < 2.0, (c, s["el_pct"], f[c]["el"])


def test_scheil_curve_is_the_twins():
    """exp_data.scheil_twin keeps the curve twin.thermo.AlSolidification.run reads its numbers from: the same
    numbers, exactly, for the alloy followed and for the reference alloys, in both parameter sets."""
    from twin import thermo
    from twin.spaces import REFERENCE
    comps = [X.alloy("flaime_al").comp] + [dict(wt, Al=100.0 - sum(wt.values()))
                                           for wt in REFERENCE["flaime_al"].values()]
    for comp in comps:
        for kind in ("open", "truth"):
            c = X.scheil_twin(kind, comp)
            r = thermo.AlSolidification(kind).run(dict(comp))
            assert c["T_alpha_liquidus_C"] == r["T_alpha_liquidus_C"]
            assert c["T_98_C"] == r["T_98_C"]
            assert c["kou_index_K"] == r["kou_index_K"]
            assert c["Q_K"] == r["Q_K"]
            assert abs((c["T_alpha_liquidus_C"] - c["T_98_C"]) - r["freezing_range_K"]) < 1e-9
            assert {e: p["T_C"] for e, p in c["primary"].items()} == {e: p["T_C"] for e, p in r["primary"].items()}
            assert len(c["fs"]) == len(c["T_C"]) and np.all(np.diff(c["fs"]) > 0)


def test_open_scheil_is_for_this_alloy():
    """The committed pycalphad + scheil run is for the alloy followed, names what the database lacks, and freezes."""
    d = X.scheil_open()
    a = X.alloy("flaime_al")
    assert d is not None, "run python -m twin.video.exp_data scheil"
    assert set(d["wt"]) | set(d["left_out"]) == set(a.design)
    assert all(abs(d["wt"][e] - a.design[e]) < 1e-9 for e in d["wt"])
    assert set(d["left_out"]) == {"Li", "Er", "Sn"}                      # not in MatCalc mc_al
    fs = d["fraction_solid"]
    assert fs[0] == 0.0 and fs[-1] > 0.999 and np.all(np.diff(fs) >= -1e-9)
    assert "FCC_A1" in d["phases"] and d["phases"]["FCC_A1"][-1] > 0.85
    assert "pycalphad" in d["tools"] and "scheil" in d["tools"] and "MatCalc" in d["database"]


def test_melt_pool_is_the_twins():
    """The field the AM segment draws has the twin's own melt pool in it: the liquidus isotherm's half-width on the
    surface is the twin's (Rosenthal's point source, twin/physics.py), and the probe's history peaks above it."""
    a = X.alloy("flaime_al")
    mp = a.melt_pool()
    top, y = mp["top_C"], mp["y_um"]
    molten = (top >= mp["liquidus_C"]).any(axis=1)
    half = float(np.abs(y[molten]).max())
    assert abs(2 * half / mp["twin"]["W_um"] - 1) < 0.06, (2 * half, mp["twin"]["W_um"])
    assert mp["hist_peak_C"] > mp["liquidus_C"] and mp["hist_cool_K_s"] > 1e5
    assert mp["proc"]["P_W"] == a.cubes()[a.best]["P_W"] and mp["proc"]["v_mm_s"] == a.cubes()[a.best]["v_mm_s"]


def test_facts_are_current():
    """facts.json is what the models give now (a rebuild shows the numbers the file has)."""
    have = json.loads(X.FACTS_JSON.read_text())
    now = json.loads(json.dumps(X.facts(), default=str))

    def close(a, b, path=""):
        if isinstance(a, dict):
            assert isinstance(b, dict) and set(a) == set(b), path
            for k in a:
                close(a[k], b[k], f"{path}.{k}")
        elif isinstance(a, list):
            assert len(a) == len(b), path
            for i, (x, y) in enumerate(zip(a, b)):
                close(x, y, f"{path}.{i}")
        elif isinstance(a, float) or isinstance(b, float):
            assert a == pytest.approx(b, rel=1e-6, abs=1e-9), path
        else:
            assert a == b, path
    close(have, now)


def test_only_the_open_node_ran():
    """What the chapter says about the simulation nodes: in round 3b's committed logs every simulation call is the
    open-database node, and no hot tensile test was booked (the full count is in facts.json; three logs here)."""
    sk = X.load_facts()["sim_kinds"]
    assert set(sk["calls"]) == {"sim_open"} and sk["hot_tests"] == 0 and sk["logs"] == len(list(
        D.EVENTS_DIR.glob("*.json*")))
    for p in sorted(D.EVENTS_DIR.glob("*bofn3_s0*"))[:1] + sorted(D.EVENTS_DIR.glob("*tiered_s1*"))[:1] + \
            sorted(D.EVENTS_DIR.glob("*pkgfn3_s2*"))[:1]:
        ev = D._load_json(p)
        assert {e["what"] for e in ev["events"] if e["station"] == "hpc"} <= {"sim_open"}
        assert not any(e["station"] == "tensile_hot" for e in ev["events"])


def _small(code: str) -> dict:
    """Run a snippet in a process drawing at 480 x 270 (style reads the size when it is imported)."""
    env = dict(os.environ, TWIN_VIDEO_ROUND="3b", TWIN_VIDEO_SIZE="480x270")
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_every_part_draws_and_says_where_it_comes_from():
    out = _small(
        "import json\n"
        "from twin.video import experiments as E, exp_draw as G\n"
        "rows = {}\n"
        "for k in E.keys():\n"
        "    s = E.segment(k)\n"
        "    shapes = [list(s.frame(t).shape) for t in (0.0, s.DURATION * 0.5, s.DURATION)]\n"
        "    rows[k] = dict(dur=float(s.DURATION), shapes=shapes, caps=[list(c) for c in s.captions],\n"
        "                   marks=dict(s.marks), kinds=[x[0] for x in s.sources], n=len(s.sources))\n"
        "    s.close()\n"
        "print(json.dumps(dict(rows=rows, kinds=sorted(G.KIND), total=E.total())))\n")
    rows = out["rows"]
    assert list(rows) == ["intro", "composition", "scheil", "am", "atomize", "print", "sem", "mech", "corrosion",
                          "outro"]
    for k, r in rows.items():
        assert r["dur"] > 5 and all(sh == [270, 480, 3] for sh in r["shapes"]), k
        assert r["n"] >= 1 and set(r["kinds"]) <= set(out["kinds"]), k
        assert all(0 <= a < b <= r["dur"] + 1e-6 and s for a, b, s in r["caps"]), k
        assert all(0 <= t <= r["dur"] for t in r["marks"].values()), k
        last = 0.0
        for a, b, _ in sorted(r["caps"]):                    # one caption at a time
            assert a >= last - 1e-6, k
            last = b
    # what is not the twin's output is said to be something else
    assert "illus" in rows["mech"]["kinds"] and "sim" in rows["mech"]["kinds"]
    assert "real" in rows["atomize"]["kinds"] and "calc" in rows["scheil"]["kinds"]


def test_narration_says_only_what_facts_have():
    out = _small(
        "import json, io, contextlib\n"
        "from twin.video import experiments as E\n"
        "N = E.narration()\n"
        "buf = io.StringIO()\n"
        "with contextlib.redirect_stdout(buf):\n"
        "    rows = E.check_numbers()\n"
        "mk = E.marks()\n"
        "lines = N.lines()\n"
        "segs = [p['name'] for p in E.plan()]\n"
        "print(json.dumps(dict(n=len(rows), ok=all(r['ok'] for r in rows), ids=[l['id'] for l in lines],\n"
        "    missing=[l['id'] for l in lines if l.get('mark') and l['mark'] not in mk],\n"
        "    badseg=[l['id'] for l in lines if not l.get('mark') and l.get('seg') not in segs],\n"
        "    words=sum(len(l['text'].split()) for l in lines), total=E.total())))\n")
    assert out["ok"] and not out["missing"] and not out["badseg"]
    assert len(out["ids"]) == len(set(out["ids"])) >= 15
    assert {"dag1", "dag2", "dag3", "dag4"} <= set(out["ids"])           # the old chapter's four lines are kept


def test_kept_lines_are_the_cuts():
    """The chapter keeps the old chapter's four lines word for word (round 3b's script)."""
    old = {ln["id"]: ln["text"] for ln in json.loads((HERE / "twin/video/narration3b.json").read_text())["lines"]}
    new = {ln["id"]: ln["text"] for ln in json.loads((HERE / "twin/video/narration_exp.json").read_text())["lines"]}
    for k in ("dag1", "dag2", "dag3", "dag4"):
        assert new[k] == old[k], k


def test_record_matches_the_script():
    """If the preview has been built: its record places every line of the script, none pushed late or cut off, and
    the description says what is simulated."""
    rec_p = X.OUT / "record.json"
    if not rec_p.exists():
        pytest.skip("the preview has not been built")
    rec = json.loads(rec_p.read_text())
    script = json.loads((HERE / "twin/video/narration_exp.json").read_text())["lines"]
    placed = rec["narration"]["placed"]
    assert [p["id"] for p in sorted(placed, key=lambda p: p["t"])] and {p["id"] for p in placed} == {
        ln["id"] for ln in script}
    assert all(not p["warn"] for p in placed), [p for p in placed if p["warn"]]
    assert {p["text"] for p in placed} == {ln["text"] for ln in script}
    assert abs(rec["seconds"] - rec["total_s"]) < 0.5
    meta = json.loads((X.OUT / "youtube_meta.json").read_text())
    assert "simulated" in meta["description"].lower() and "PREVIEW" in meta["title"]
    assert "Thermo-Calc output" in meta["description"]

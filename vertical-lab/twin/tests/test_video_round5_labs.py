"""The two-year cut's lab comparison and takeaway (twin/video/figs5_labs.py, numbers5.py, narration5_labs.json) say
only what the round's tables say.

    python -m pytest -q twin/tests/test_video_round5_labs.py

The video's data adapter reads TWIN_VIDEO_ROUND when it is imported, so each check runs in its own process with
TWIN_VIDEO_ROUND=5 (or TWIN_VIDEO_TEST_ROUND, to try a later round). Needs numpy and pillow only (no speech model, no
3-D stack, no ffmpeg).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/
ROUND = os.environ.get("TWIN_VIDEO_TEST_ROUND", "5")


def _run(code: str) -> str:
    env = dict(os.environ, TWIN_VIDEO_ROUND=ROUND)
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return r.stdout


def _last(out: str):
    return json.loads(out.strip().splitlines()[-1])


def test_every_spoken_number_and_claim_matches():
    """Each number a line speaks is a placeholder read from numbers5.numbers(); no figure is typed into a line; every
    line's claims hold (or an alternative's do); every worded statement on a card holds."""
    out = _run("from twin.video import figs5_labs as F; rows = F.check_numbers(); print('ROWS', len(rows))")
    assert "ROWS" in out and "BAD" not in out


def test_the_like_for_like_cells_are_tables_md():
    """The like-for-like card's 24 cells, printed the way twin.like5 prints them, are the rows of tables.md's first
    table as printed (so a number on the card is a number in the tables, not only in the json beside them)."""
    out = _run("""
import json
from twin.video import numbers5 as N
n = N.numbers()
L = n["labs"]
rows = []
for c, cw in ((N.AL, "Aluminium"), (N.CU, "Copper")):
    for tn in ("T1", "T2"):
        for p in N.POLS:
            nm = L["names"][p][c]
            cells = []
            for q in ("lean", "stocked", "round3", "rev"):
                x = L["days"][c][tn][p][q]
                cells.append(f"{x['printed']}; {x['hit_new']}/{x['n']} vs {x['hit_ref']}/{x['n']}")
            rows.append(f"| {cw} {tn} | {nm} | {nm} | " + " | ".join(cells) + " |")
print(json.dumps(rows))
""")
    md = (HERE / "out" / f"twin{ROUND}" / "tables.md").read_text().splitlines()
    rows = _last(out)
    assert len(rows) == 12
    for r in rows:
        assert r in md, r


def test_days_money_and_costs_are_tables_md():
    """The median days, the days at which 90 % of the money was spent, the money factors and the costs per alloy the
    cards show are the tables' own, as printed."""
    out = _run("""
import json
from twin.video import numbers5 as N
n = N.numbers()
A, U, E, M = n["labs"]["arms"], n["labs"]["usd"], n["econ"], n["money"]
d = lambda v: ">730" if v is None or v == float("inf") else f"{v:.0f}"
out = dict(arms=[], usd=[], econ=[], fixed=[])
for k, a in A.items():
    al, cu = a[N.AL], a[N.CU]
    out["arms"].append(f"| `{a['key']}` | {a['n']} | {al['T1']['hit']}/{al['T1']['n']}; {d(al['T1']['day'])} | "
                       f"{al['T2']['hit']}/{al['T2']['n']}; {d(al['T2']['day'])} | "
                       f"{cu['T1']['hit']}/{cu['T1']['n']}; {d(cu['T1']['day'])} | "
                       f"{cu['T2']['hit']}/{cu['T2']['n']}; {d(cu['T2']['day'])} | "
                       f"{al['best']:.2f} ± {al['best_se']:.2f} | {cu['best']:.2f} ± {cu['best_se']:.2f} | "
                       f"{d(al['d90'])}, {d(cu['d90'])} |")
for c, cw in ((N.AL, "Aluminium"), (N.CU, "Copper")):
    for tn in ("T1", "T2"):
        for p in N.POLS:
            nm = n["labs"]["names"][p][c]
            out["usd"].append(f"| {cw} {tn} | {nm} | {nm} | {U[c][tn][p]['lean']['printed']} | "
                              f"{U[c][tn][p]['stocked']['printed']} |")
lab_w = {"vertical": "automated", "conventional": "conventional"}
for k, v in E["arms"].items():
    lab, p, st = k.split("|")
    for c, cw in ((N.AL, "Aluminium"), (N.CU, "Copper")):
        if (p == "fast") != (n["labs"]["names"][p][c] in ("heuristic", "funnel")):
            continue
        x = v[c]
        out["econ"].append(f"| {lab_w[lab]}, {n['labs']['names'][p][c]}, {'stocked' if st == 'reorder' else 'lean'} "
                           f"| {cw} | ${x['total_2y']:,.0f} | {x['alloys']:.1f} | ${x['per_alloy']:,.0f} | "
                           f"${x['per_alloy_campaign']:,.0f} |")
fy = E["fixed_year"]
out["fixed"] = (f"Fixed costs a year: vertical ${fy['vertical']['total']:,.0f} (depreciation "
                f"${fy['vertical']['capex']:,.0f}); conventional ${fy['conventional']['total']:,.0f} (depreciation "
                f"${fy['conventional']['capex']:,.0f}).")
out["d90"] = [M["d90"]["auto"][N.AL]["day"], M["d90"]["auto"][N.CU]["day"], n["replay"]["arm"], n["replay"]["seed"]]
print(json.dumps(out))
""")
    md = (HERE / "out" / f"twin{ROUND}" / "tables.md").read_text()
    lines = md.splitlines()
    got = _last(out)
    assert len(got["arms"]) == 12 and len(got["usd"]) == 12
    for r in got["arms"] + got["usd"]:
        assert r in lines, r
    for r in got["econ"]:                              # the table's row starts with these six columns
        assert any(ln.startswith(r) for ln in lines), r
    assert got["fixed"] in md
    # the replayed arm is the one tables.md names the median seed of, and its 90 % days are that arm's row
    arm, seed = got["d90"][2], got["d90"][3]
    assert any(ln.startswith(f"| `{arm}` | {seed} |") for ln in lines)


def test_lines_are_recorded_as_they_resolve_and_do_not_overlap():
    """Every line's committed audio was spoken from the text the line resolves to now (so no stale number is heard),
    the lines follow each other without overlapping, and each segment outlasts its lines."""
    out = _run("""
import json
from twin.video import figs5_labs as F
rec = json.loads((F.NDIR / "lines.json").read_text())["lines"]
out = dict(segs=[(n, d) for n, d, _, _ in F.SEGMENTS], lines=[])
for seg in ("labs", "takeaway"):
    for r in F.narration_lines(seg):
        out["lines"].append(dict(seg=seg, id=r["id"], t=r["t"], end=r["end"], text=r["text"],
                                 flac=r["flac"].exists(), spoken=rec.get(r["id"], {}).get("text"),
                                 seconds=rec.get(r["id"], {}).get("seconds")))
print(json.dumps(out))
""")
    got = _last(out)
    segs = dict(got["segs"])
    assert set(segs) == {"labs", "takeaway"}
    assert 120 <= segs["labs"] <= 175 and 30 <= segs["takeaway"] <= 55
    ids = [r["id"] for r in got["lines"]]
    assert len(ids) == len(set(ids))
    for seg in segs:
        rows = [r for r in got["lines"] if r["seg"] == seg]
        assert rows
        for a, b in zip(rows[:-1], rows[1:]):
            assert b["t"] >= a["end"] + 0.4, (a["id"], b["id"])
        assert segs[seg] >= rows[-1]["end"] + 1.0
        for r in rows:
            assert r["flac"] and r["spoken"] == r["text"], r["id"]
            assert abs((r["end"] - r["t"]) - r["seconds"]) < 0.02, r["id"]
            assert "simulated" in " ".join(x["text"].lower() for x in rows)


def test_every_card_state_draws():
    """One frame per card state, at the cut's size, each different from the one before."""
    out = _run("""
import json
import numpy as np
from twin.video import figs5_labs as F
fn = dict((n, f) for n, _, f, _ in F.SEGMENTS)
prev, rows = None, []
for seg, t, lab in F.still_times():
    fr = np.asarray(fn[seg](t))
    rows.append([lab, list(fr.shape), str(fr.dtype), bool(prev is None or (fr != prev).any()), float(fr.mean())])
    prev = fr
caps = {n: F.captions(n) for n in fn}
print(json.dumps(dict(rows=rows, caps=caps)))
""")
    got = _last(out)
    assert len(got["rows"]) >= 15
    for lab, shape, dtype, differs, mean in got["rows"]:
        assert shape == [1080, 1920, 3] and dtype == "uint8", lab
        assert mean > 14.0, lab                        # not the bare background
        assert differs or lab == "end", lab             # each line brings something in; the end holds the last
    for name, caps in got["caps"].items():
        assert caps and caps[0][0] == 0.0
        assert all("imulated" in c[2] for c in caps), name


def test_a_round_without_a_money_limit_changes_the_words():
    """Round 6 removes the money limit and tracks spending instead. With no budget in the rows, the lines about the
    money running out give way to their alternatives, the check still passes, and the money card and the takeaway
    draw without the budget line and the 90 % marks."""
    out = _run("""
import copy, json
import numpy as np
from twin.video import numbers5 as N
from twin.video import figs5_labs as F
base = F.lines()
n = copy.deepcopy(N.numbers())
for c in n["money"]["budget"]:
    n["money"]["budget"][c] = None
for k in n["money"]["end"]:
    for c in n["money"]["end"][k]:
        n["money"]["end"][k][c]["share"] = None
for k in n["money"]["traces"]:
    for c in n["money"]["traces"][k]:
        n["money"]["traces"][k][c]["budget"] = None
N._N.clear(); N._N.update(n)
F._CACHE.clear()
cl = N.claims_by_key()
alt = {ln["id"]: ln["variant"] for ln in F.lines()}
rows = F.check_numbers(verbose=False)
L = F.layout("labs")
t = [r for r in L["lines"] if r["id"] == "mon3"][0]["end"]
fr = np.asarray(F.labs_frame(t))
tk = np.asarray(F.takeaway_frame(F.layout("takeaway")["duration"] - 1.0))
print(json.dumps(dict(limit=cl["money_limit"][1], runs_out=cl["money_runs_out"][1], alt=alt,
                      was={ln["id"]: ln["variant"] for ln in base}, rows=len(rows),
                      texts={ln["id"]: ln["text"] for ln in F.lines() if ln["id"] in ("mon1", "mon2", "take3")},
                      shapes=[list(fr.shape), list(tk.shape)])))
""")
    got = _last(out)
    assert got["limit"] is False and got["runs_out"] is False
    assert all(v == 0 for v in got["was"].values())                    # round 5: every line is said as written
    assert got["alt"]["mon1"] == 1 and got["alt"]["mon2"] == 1 and got["alt"]["take3"] == 1
    assert all(v == 0 for k, v in got["alt"].items() if k not in ("mon1", "mon2", "take3"))
    assert "percent" not in got["texts"]["mon1"] and "idles" not in got["texts"]["mon1"]
    assert "months" not in got["texts"]["take3"]
    assert got["shapes"] == [[1080, 1920, 3], [1080, 1920, 3]]


def test_a_claim_that_fails_stops_the_build():
    """If a later round's numbers no longer show what a line or a card says, the check names it and stops."""
    env = dict(os.environ, TWIN_VIDEO_ROUND=ROUND)
    code = """
import copy
from twin.video import numbers5 as N
from twin.video import figs5_labs as F
n = copy.deepcopy(N.numbers())
for p in N.OPTS:                                   # as if copper's optimizers no longer led
    for q in ("lean", "stocked"):
        for tn in ("T1", "T2"):
            n["labs"]["days"][N.CU][tn][p][q].update(kind="factor", af=0.9, lo=0.6, hi=1.3, half=False)
N._N.clear(); N._N.update(n)
F._CACHE.clear()
F.check_numbers(verbose=False)
"""
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=900)
    assert r.returncode != 0
    msg = r.stdout + r.stderr
    assert "lab4" in msg and "no alternative fits" in msg and "a card says" in msg

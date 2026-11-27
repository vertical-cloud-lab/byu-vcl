"""Round 3b's re-cut of the campaign video says only what round 3b's tables and round 3's summaries say.

    python -m pytest -q twin/tests/test_video_round3b.py

The video's data adapter reads TWIN_VIDEO_ROUND when it is imported, so each check runs in its own process with
TWIN_VIDEO_ROUND=3b. Needs numpy and pillow only (no speech model, no 3-D stack, no ffmpeg).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/


def _run(code: str, rnd: str = "3b") -> str:
    env = dict(os.environ, TWIN_VIDEO_ROUND=rnd, TWIN_VIDEO_NARRATION="1", TWIN_VIDEO_LAB3D="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return r.stdout


def _last(out: str):
    return json.loads(out.strip().splitlines()[-1])


def test_every_spoken_number_and_claim_matches():
    """narration3b.json: each number a line speaks is the committed value at its path, in its format; no line holds a
    figure without a source; and what the cards say in words holds (numbers3b.claims)."""
    out = _run("from twin.video import narration as N; rows = N.check_numbers(); print('ROWS', len(rows))")
    assert "ROWS" in out and "BAD" not in out


def test_the_cards_cells_are_tables_md():
    """The cells the cut leads with, printed the way twin.like3b prints them, are in out/twin3b/tables.md as printed
    (so a number on a card is a number in the tables, not only in the json beside them)."""
    out = _run("""
import json, math
from twin.video import numbers3b as NB
n = NB.numbers()
def fmt(c, first=True):
    lo = '∞' if not math.isfinite(c['lo']) else ('0' if c['lo'] == 0 else f"{c['lo']:.1f}")
    hi = '∞' if not math.isfinite(c['hi']) else f"{c['hi']:.1f}"
    s = f"{c['af']:.1f}x ({lo}-{hi}); {c['hit_new']}/{c['n']} vs {c['hit_ref']}/{c['n']}"
    return s + (f"; first in {c['first_new']}/{c['n']}" if first else '')
L, R3, S = n['lab']['like'], n['lab']['round3'], n['stock']['vertical_lab']
al, cu = 'flaime_al', 'onr_cu'
cells = dict(
    al_t2_bofn=fmt(L[al]['T2']['bofn_thumb']['days']), al_t2_pkgfn=fmt(L[al]['T2']['pkgfn_thumb']['days']),
    cu_t2_funnel=fmt(L[cu]['T2']['same_funnel']['days']), al_t1_heur=fmt(L[al]['T1']['same_heur']['days']),
    cu_t1_funnel=fmt(L[cu]['T1']['same_funnel']['days']), al_t2_bofn_same=fmt(L[al]['T2']['bofn_same']['days']),
    al_t2_pkgfn_same=fmt(L[al]['T2']['pkgfn_same']['days']), r3_al_t2_pkgfn=fmt(R3[al]['T2']['pkgfn_thumb']['days']),
    r3_cu_t2_funnel=fmt(R3[cu]['T2']['same_funnel']['days']),
    stock_bofn=fmt(S['bofn3'][al]['T2']['days'], False), stock_pkgfn=fmt(S['pkgfn3'][al]['T2']['days'], False),
    usd_al_bofn=fmt(L[al]['T2']['bofn_thumb']['usd'], False), usd_cu_funnel=fmt(L[cu]['T2']['same_funnel']['usd'], False))
print(json.dumps(cells, ensure_ascii=False))
""")
    cells = _last(out)
    tables = (HERE / "out" / "twin3b" / "tables.md").read_text()
    for name, cell in cells.items():
        assert cell in tables, (name, cell)
    assert cells["al_t2_bofn"].startswith("1.8x (1.3-∞); 11/12 vs 6/12")
    assert cells["cu_t2_funnel"].startswith("3.2x (1.9-4.8); 10/12 vs 9/12")
    assert cells["stock_bofn"].startswith("1.9x") and cells["stock_pkgfn"].startswith("2.2x")
    assert cells["al_t2_bofn_same"].startswith("0.9x") and cells["al_t2_pkgfn_same"].startswith("1.0x")


def test_a_lower_bound_is_shown_as_one():
    """Aluminium's halfway target against the rule of thumb: the conventional lab got there in 6 of 12 runs, so the
    cut says 'at least', as round 3's cut did; copper's funnel is a factor with both medians."""
    out = _run("import json; from twin.video import numbers3b as NB; n = NB.numbers(); L = n['lab']['like']; "
               "print(json.dumps(dict(a=NB.big(L['flaime_al']['T2']['bofn_thumb']['days']), "
               "b=NB.big(L['flaime_al']['T2']['pkgfn_thumb']['days']), "
               "c=NB.big(L['onr_cu']['T2']['same_funnel']['days']), "
               "u=NB.big(L['flaime_al']['T2']['bofn_thumb']['usd']))))")
    n = _last(out)
    assert n == dict(a="at least 1.8x", b="at least 1.8x", c="3.2x", u="at least 2.2x")


def test_the_replay_is_the_two_median_seeds_from_committed_logs():
    """The replay's two runs are the ones like3b.json names for the replay arm; each log is committed in
    out/twin3b/events and is its committed run (its best-so-far curve is the row's, point for point); round 3b's
    seed-0 log is round 3's own; the cut changes run at the phase it says, after seed 0's aluminium passed both
    targets and before seed 5's copper reaches its first; and each question goes to the run on screen."""
    out = _run("""
import json, numpy as np
from twin.video import data as D, compose as C
R, tl = C.S('R'), C.S('tl')
ok = [bool(all(np.allclose(r.curves_all[c], np.array(r.row['campaigns'][c]['curve']).reshape(-1, 3), atol=1e-3)
           for c in D.CAMPAIGNS)) for r in R.runs]
same = D._load_json(R.runs[0].path) == json.loads((D.OUT3 / 'events' / 'r3_vertical_lab_bofn3_s0.json').read_text())
h = R.switch_h
print(json.dumps(dict(
    paths=[str(r.path.relative_to(D.HERE)) for r in R.runs], seeds=[r.seed for r in R.runs],
    policy=[r.policy for r in R.runs], ok=ok, same=bool(same), parts=[[q['campaign'], q['target'], q['seed'],
    round(q['day'])] for q in R.parts], switch_day=int(h // 24) + 1, at_phase=abs(tl.switch_t - tl.phase_t[C.SWITCH_PHASE]) < 1e-9,
    before=R.part_index(h - 1.0), after=R.part_index(h + 1.0),
    al_before=R.best_at('flaime_al', h - 1.0), al_after=R.best_at('flaime_al', h + 1.0),
    a_best=R.runs[0].best_at('flaime_al', h - 1.0), b_best=R.runs[1].best_at('flaime_al', h + 1.0),
    cu_end=R.best_at('onr_cu', 364 * 24.0), b_cu_end=R.runs[1].best_at('onr_cu', 364 * 24.0),
    helpers=sorted((set(R.runs[0].station.tolist()) | set(R.runs[1].station.tolist())) & set(D.HELPERS)))))
""")
    n = _last(out)
    assert n["paths"] == ["out/twin3b/events/r3_vertical_lab_bofn3_s0.json.xz",
                          "out/twin3b/events/r3_vertical_lab_bofn3_s5.json.xz"]
    assert n["seeds"] == [0, 5] and n["policy"] == ["bofn3", "bofn3"] and n["ok"] == [True, True] and n["same"]
    assert n["parts"] == [["flaime_al", "T2", 0, 96], ["onr_cu", "T1", 5, 221]]
    assert n["at_phase"] and 96 < n["switch_day"] < 221
    assert (n["before"], n["after"]) == (0, 1)
    assert n["al_before"] == n["a_best"] and n["al_after"] == n["b_best"] and n["cu_end"] == n["b_cu_end"]
    assert n["helpers"] == []


def test_the_3d_jobs_follow_the_two_runs():
    """Each 3-D job names the run it draws: the first before the change of camera at SWITCH_PHASE, the second from
    it; the second run's move plan starts before it is on screen."""
    out = _run("""
import json
from twin.video import compose as C, lab3d_cut as LC
jobs = LC.replay_jobs()
tl = C.S('tl')
print(json.dumps(dict(n=len(jobs), runs=sorted({(j['phase'] >= C.SWITCH_PHASE, j['run']) for j in jobs}),
    lead=[tl.switch_t - j['clock_v0'] for j in jobs if j['phase'] >= C.SWITCH_PHASE][0],
    a_end=[abs(j['clock_v1'] - tl.switch_t) < 1e-3 for j in jobs if j['phase'] < C.SWITCH_PHASE][0])))
""")
    n = _last(out)
    assert n["runs"] == [[False, "r3_vertical_lab_bofn3_s0.json.xz"], [True, "r3_vertical_lab_bofn3_s5.json.xz"]]
    assert n["lead"] > 5.0 and n["a_end"]


def test_round_3s_pairing_is_only_ever_labelled_as_round_3s():
    """A line that speaks a factor of round 3's pairing (a stocked automated lab against a conventional lab ordering
    as it goes) says it is round three's; and the lines that lead the lab comparison say the labs are like for
    like."""
    S = json.loads((HERE / "twin" / "video" / "narration3b.json").read_text())["lines"]
    old = [ln for ln in S if any("lab.round3." in p for _, p, _ in ln.get("nums", []))]
    assert old and all("Round three" in ln["text"] for ln in old)
    by = {ln["id"]: ln["text"] for ln in S}
    for k in ("fig3", "lfl1", "take2"):
        assert "like for like" in by[k]
    assert "Stocking is its own effect, and it is not the lab's" in by["stk1"]
    assert "does not win" in by["tie1"] and "about a tie" in by["tie1"]
    assert "leaves out fixed costs" in by["cost1"] and "Fixed costs" in by["take3"]
    assert "seed zero" in by["seed1"] and "seed five" in by["seed1"] and "seed five" in by["mid1"]
    assert not any("never reach" in t for t in by.values())          # the dropped copper line and badge


def test_unchanged_lines_keep_round_3s_recorded_audio():
    """A line whose text is round 3's is round 3's recording, byte for byte; the rest are new."""
    a = json.loads((HERE / "out" / "twin3" / "video" / "narration" / "lines.json").read_text())
    b = json.loads((HERE / "out" / "twin3b" / "video" / "narration" / "lines.json").read_text())
    assert (b["voice_id"], b["speed"], b["model_sha256"]) == (a["voice_id"], a["speed"], a["model_sha256"])
    S = {ln["id"]: ln["text"] for ln in json.loads((HERE / "twin" / "video" / "narration3b.json").read_text())["lines"]}
    assert set(S) == set(b["lines"])
    same = [k for k in S if k in a["lines"] and a["lines"][k]["text"] == S[k]]
    assert len(same) >= 15
    for k in same:
        assert b["lines"][k]["sha256"] == a["lines"][k]["sha256"], k


def test_round_3s_cut_is_unchanged_by_the_switch():
    """TWIN_VIDEO_ROUND=3 still gives round 3's cut: its own script, its segments, its single replayed run."""
    out = _run("import json; from twin.video import data as D, compose as C, narration as N; rec = C.plan_record(); "
               "print(json.dumps(dict(r3b=D.R3B, script=N.SCRIPT.name, segs=[s['name'] for s in rec['segments']], "
               "total=rec['total_s'], vid=str(D.VID.relative_to(D.HERE)), run=C.S('R').path.name)))", rnd="3")
    n = _last(out)
    assert n == dict(r3b=False, script="narration3.json", total=858.5, vid="out/twin3/video",
                     run="r3_vertical_lab_bofn3_s0.json",
                     segs=["title", "simulated", "changes", "dag", "figures", "assume", "replay", "results",
                           "takeaway", "notes"])

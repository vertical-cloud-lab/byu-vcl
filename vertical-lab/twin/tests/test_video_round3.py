"""Round 3's video says only what round 3's committed summaries say.

    python -m pytest -q twin/tests/test_video_round3.py

The video's data adapter reads TWIN_VIDEO_ROUND when it is imported, so each check runs in its own process with
TWIN_VIDEO_ROUND=3. Needs numpy only (no speech model, no 3-D stack).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/


def _run(code: str) -> str:
    env = dict(os.environ, TWIN_VIDEO_ROUND="3", TWIN_VIDEO_NARRATION="1", TWIN_VIDEO_LAB3D="1")
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return r.stdout


def test_every_spoken_number_and_claim_matches_the_summaries():
    """narration3.json: each number a line speaks is the committed value at its path, in its format; no line holds a
    figure without a source; and what the cards say in words holds (numbers3.claims)."""
    out = _run("from twin.video import narration as N; rows = N.check_numbers(); print('ROWS', len(rows))")
    assert "ROWS" in out and "BAD" not in out


def test_the_cards_numbers_are_the_tables():
    """A few of numbers3's values against out/twin3/fig/tables.md and notes/twin_round3.md as printed."""
    out = _run("import json; from twin.video import numbers3 as N3; n = N3.numbers(); "
               "print(json.dumps(dict(al=n['main']['bofn3']['flaime_al'], cu=n['main']['tiered']['onr_cu'], "
               "money=n['cu_money']['bofn3']['own'], lab=n['labs']['onr_cu']['same']['T2'], "
               "thumb=n['labs']['flaime_al']['thumb']['T2'], replay=n['replay']['policy'], "
               "seed=n['replay']['seed']), default=str))")
    n = json.loads(out.strip().splitlines()[-1])
    assert round(n["al"]["best"], 2) == 0.73 and n["al"]["T2"]["hit"] == 11 and round(n["al"]["T2"]["day"]) == 96
    assert round(n["cu"]["best"], 2) == 0.69 and n["cu"]["T2"]["hit"] == 10 and round(n["cu"]["T2"]["day"]) == 148
    assert round(n["money"]["mean"], 2) == 0.14 and n["money"]["ahead"] == 4      # tables.md, cu_money: 4 seeds
    assert n["lab"]["kind"] == "factor" and round(n["lab"]["af"], 1) == 3.8
    assert n["thumb"]["kind"] == "at_least" and n["thumb"]["hit_ref"] == 6 and round(n["thumb"]["af"], 1) == 4.0
    assert n["replay"] == "bofn3" and n["seed"] == 0


def test_the_replay_is_a_committed_run():
    """The replayed event log is the committed one, and its run is in main.jsonl: the log's own best-so-far curve (all
    alloys) is that row's, point for point."""
    out = _run("import json, numpy as np; from twin.video import data as D; R = D.Replay(); "
               "ok = all(np.allclose(R.curves_all[c], np.array(R.row['campaigns'][c]['curve']).reshape(-1, 3), "
               "atol=1e-3) for c in D.CAMPAIGNS); "
               "print(json.dumps(dict(ok=bool(ok), path=str(R.path.relative_to(D.HERE)), "
               "helpers=sorted(set(R.station.tolist()) & set(D.HELPERS)))))")
    n = json.loads(out.strip().splitlines()[-1])
    assert n["ok"] and n["path"] == "out/twin3/events/r3_vertical_lab_bofn3_s0.json" and n["helpers"] == []

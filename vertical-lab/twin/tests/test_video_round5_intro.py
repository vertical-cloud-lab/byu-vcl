"""The two-year cut's opening and closing cards (twin/video/figs5_intro.py) say only what round 5's code, tables and
rows say.

    python -m pytest -q twin/tests/test_video_round5_intro.py

The video's data adapter reads TWIN_VIDEO_ROUND when it is imported, so each check runs in its own process with
TWIN_VIDEO_ROUND=5. Needs numpy, pillow and num2words (no speech model, no 3-D stack, no ffmpeg).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/
VIDEO = HERE / "twin" / "video"


def _run(code: str, rnd: str = "5", **env_more) -> str:
    env = dict(os.environ, TWIN_VIDEO_ROUND=rnd, **env_more)
    r = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env, capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-3000:]
    return r.stdout


def _last(out: str):
    return json.loads(out.strip().splitlines()[-1])


def test_every_line_says_only_numbers_from_numbers_and_the_claims_hold():
    """Each line is rendered from numbers(): a figure no placeholder produced fails, so does a claim the numbers
    don't bear out, a recorded line whose text is no longer the rendered one, and a stale numbers_intro.json."""
    out = _run("from twin.video import figs5_intro as F; rows = F.check_numbers(); print('ROWS', len(rows))")
    assert "ROWS" in out and "BAD" not in out


def test_no_number_is_typed_into_a_line():
    """In the script, every digit sits inside a {path|format} placeholder."""
    js = json.loads((VIDEO / "narration5_intro.json").read_text())
    ids = [ln["id"] for ln in js["lines"]]
    assert len(ids) == len(set(ids))
    assert all(re.match(r"(chg|cnt|atm|note)\d+$", i) for i in ids), ids       # unique across the cut by prefix
    for ln in js["lines"]:
        bare = re.sub(r"\{[^{}|]+\|[^{}]+\}", "", ln["text"])
        assert not re.search(r"\d", bare), (ln["id"], bare)
        assert ln["seg"] in ("changes", "counters", "atomizer", "notes")


def test_numbers_are_the_rounds_own():
    """numbers() against the sources read here independently: like5.json, tables.md as printed, twin/round5.py, and
    the replayed run's own event log."""
    n = _last(_run("""
import json
from twin.video import figs5_intro as F
n = F.numbers()['intro']
n['replay'].pop('curves')
print(json.dumps(n))
"""))
    like = json.loads((HERE / "out" / "twin5" / "like5.json").read_text())
    assert n["targets"] == like["targets"]
    tables = (HERE / "out" / "twin5" / "tables.md").read_text()
    arm, seed = n["replay"]["arm"], n["replay"]["seed"]
    assert arm == "r5_vertical_parallel_bofn3_reorder" and n["replay"]["conv_arm"] == \
        "r5_conventional_external_bofn3_reorder"
    # the median seed for both campaigns together, as the tables print it
    assert re.search(rf"\| `{arm}` \| {seed} \| .*`out/twin5/events/{arm}_s{seed}\.json\.xz` \|", tables)
    assert n["replay"]["events"] == f"{arm}_s{seed}.json.xz"
    assert (HERE / "out" / "twin5" / "events" / n["replay"]["events"]).exists()
    assert (HERE / "out" / "twin5" / "events" / n["replay"]["conv_events"]).exists()
    # the arm's mean counters, as the tables print them (designed there is 'seen by the policy' here)
    for camp, word in (("flaime_al", "Aluminium"), ("onr_cu", "Copper")):
        a = n["counters"]["arm"][camp]
        row = f"| `{arm}` | {word} | {a['seen']:.0f} | {a['lots_made']:.0f} | {a['alloys_made']:.0f} | " \
              f"{a['alloys_printed']:.0f} | {a['alloys_tested']:.0f} |"
        assert row in tables, row
    # the replayed run's own counters, from its event log's results
    import lzma
    log = json.load(lzma.open(HERE / "out" / "twin5" / "events" / n["replay"]["events"], "rt"))
    for camp in ("flaime_al", "onr_cu"):
        tested = len({r["design"] for r in log["results"] if r["campaign"] == camp and r["type"] == "demonstrated"})
        assert n["counters"]["run"][camp]["alloys_tested"] == tested, (camp, tested)
    # aluminium's powder lots are the log's lot results one for one (copper's log also lists lots the row's counter,
    # len(Campaign.lots), doesn't hold: 34 lot results against 29, so the cards use the row's counter for both)
    lots = sum(1 for r in log["results"] if r["campaign"] == "flaime_al" and r["type"] == "lot")
    assert n["counters"]["run"]["flaime_al"]["lots_made"] == lots, lots
    # the round's code
    sys.path.insert(0, str(HERE))
    from twin import round5 as R5
    assert (n["room"]["lo"], n["room"]["hi"]) == R5.ROOM_DAYS
    assert n["used"]["rule_days"] == R5.USED["rule_days"]
    assert n["hpc"]["cores"] == R5.HPC["cores"] and n["hpc"]["add_per_day"] == R5.HPC["add_per_day"]
    assert n["hpc"]["per_day"] == R5.HPC["cores"] * 24 / R5.HPC["core_h"]
    assert n["atomizer"]["run_h"] == R5.ATOM_RUN_H
    assert n["atomizer"]["manual_week"] == 8 and round(n["atomizer"]["week_247"]["flaime_al"]) == 76
    assert n["decisions"]["signoff_usd"] == R5.DECISIONS["nominal"]["signoff"]["usd"]
    assert n["decisions"]["meeting_day"] == "Friday"
    assert n["money"]["flaime_al"] == 240000 and n["money"]["onr_cu"] == 120000 and n["money"]["same_in_both_labs"]


def test_cited_constants_are_in_their_sources():
    """The three things no data file holds are constants with their source beside them; each is in that source."""
    n = _last(_run("""
import json
from twin.video import figs5_intro as F
n = F.numbers()['intro']
print(json.dumps(dict(cru=n['atomizer']['crucibles'], rec=n['atomizer']['record'], imm=n['immersion_days'])))
"""))
    notes = " ".join((HERE / "notes" / "twin_round5.md").read_text().split())
    cru = n["cru"]
    assert f"needs {cru['need_lo']}-{cru['need_hi']} coated crucibles per alloy family in rotation" in notes
    assert f"out of service about {cru['dry_h_lo']}-{cru['dry_h_hi']} h" in notes
    assert f"the lab has one per family now, which allows at most {cru['runs_day_now']} run a day" in notes
    assert cru["now"] == 1
    rec = n["rec"]
    assert f"the lab's record is {rec['runs']} runs in {rec['days']} days" in notes
    assert "1.6-1.7 a week" in notes and 1.6 <= rec["per_week"] <= 1.7
    assert "8320f13" in rec["source"]
    camp = (HERE / "twin" / "campaign.py").read_text()
    assert f'"immersion": ([], "immersion", {n["imm"] * 24:.1f})' in camp


def test_the_cut_interface_and_the_timing():
    """SEGMENTS, captions() and narration_lines() as twin/video/cut5.py calls them; the lines of a segment don't
    overlap and end before it does; every line is recorded as rendered; a frame of every segment draws."""
    out = _last(_run("""
import json
import numpy as np
from twin.video import figs5_intro as F
segs = {}
for name, dur, fn, title in F.SEGMENTS:
    ls = F.narration_lines(name)
    fr = fn(dur - 0.2)
    segs[name] = dict(dur=dur, title=title, shape=list(fr.shape), dtype=str(fr.dtype), lit=int((fr > 60).sum()),
                      first=int((fn(0.0) > 60).sum()), caps=len(F.captions(name)),
                      lines=[dict(id=l['id'], t=l['t'], end=l['end'], text=l['text'],
                                  flac=bool(l['flac'] and l['flac'].exists())) for l in ls])
rendered = {l['id']: l['text'] for l in F.lines()}
print(json.dumps(dict(segs=segs, rendered=rendered)))
""", TWIN_VIDEO_SIZE="480x270"))
    segs = out["segs"]
    assert list(segs) == ["changes", "counters", "atomizer", "notes"]
    seen = set()
    for name, s in segs.items():
        assert s["shape"] == [270, 480, 3] and s["dtype"] == "uint8"
        assert s["lit"] > s["first"] > 0                 # the card fills in as its lines are said
        assert s["caps"] >= 3 and s["lines"]
        free = 0.0
        for ln in s["lines"]:
            assert ln["id"] not in seen
            seen.add(ln["id"])
            assert ln["t"] >= free + 0.5 or free == 0.0, (name, ln["id"])
            assert ln["flac"], ln["id"]
            assert ln["text"] == out["rendered"][ln["id"]], ln["id"]
            free = ln["end"]
        assert free + 1.0 <= s["dur"], name
    assert 30 <= segs["changes"]["dur"] <= 50 and 20 <= segs["atomizer"]["dur"] <= 40
    assert 40 <= segs["counters"]["dur"] <= 75 and 20 <= segs["notes"]["dur"] <= 35


def test_the_audit_words_are_on_the_cards_and_in_the_lines():
    """'Simulated' where it applies; the design target labelled as one, next to the lab's record; the line on early
    stopping on screen and spoken; 'designed', 'made' and 'tested' each defined."""
    src = (VIDEO / "figs5_intro.py").read_text()
    js = {ln["id"]: ln["text"] for ln in json.loads((VIDEO / "narration5_intro.json").read_text())["lines"]}
    assert '"Early stopping: only promising alloys finish every step."' in src
    assert "Early stopping means only promising alloys finish every step." in js["cnt3"]
    assert "Designed means computed candidates" in js["cnt1"] and "outside the experiments' cost" in js["cnt1"]
    assert "Made means powder lots, or alloys made" in js["cnt2"]
    assert "Tested means alloys through the full chain" in js["cnt2"]
    assert '"DESIGN TARGET"' in src and "THE LAB'S RECORD" in src and '"ASSUMED"' in src
    assert "design target, not a demonstrated rate" in js["atm1"] and "The lab's record so far" in js["atm2"]
    assert "Everything here is simulated" in js["note1"] and "stand-ins" in js["note1"]
    assert "stand-in" in js["chg2"]
    assert "not as a budget bar" in js["cnt5"] and "the replay says why" in js["cnt5"]
    assert src.count('tag="SIMULATED"') == 1             # the default tag of every card's title

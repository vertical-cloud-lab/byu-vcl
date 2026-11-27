"""YouTube metadata for the two-year cut (twin/video/cut5.py; rounds 5 and later): title, description, tags, privacy
-> out/twin<R>/video/youtube_meta_twoyears.json.

    TWIN_VIDEO_ROUND=5 python -m twin.video.meta5          # from out/twin5/video/twoyears_record.json, else the plan

Nothing in the description is typed in: each paragraph is made of the cut's own lines as they are spoken, each of
which its module has already checked against the round's tables (figs5_labs.check_numbers, figs5_intro.check_numbers,
cut5.check_own, floorspace_cut, experiments.check_numbers), plus the replayed run's facts (cut5.facts) and the
atomizer footage's credits as the manifest gives them (exp_atomize.al_footage). The chapters are the cut's as built.

The round is the one switch. Round 5 is the preview: unlisted, "(preview)" in the title, and a line that says it
will be re-rendered from round 6's results. Any later round is public, with subscribers not notified (issue 425).
TWIN_VIDEO_PRIVACY overrides the privacy.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from . import data as D
from . import meta as M

PREVIEW = str(D.ROUND) == "5"
PR = int(os.environ.get("TWIN_VIDEO_PR", "428"))
ISSUE = 425
OLD = "97BZNOI5V1w"                       # round 3b's cut, which changed seed partway through its replay
TAGS = M.TAGS + ["Kardex Shuttle", "MiR250", "UR12e", "narrated", "BOFN", "pKGFN", "CALPHAD", "Scheil",
                 "SEM", "floor space", "like for like"]
NAME = "youtube_meta_twoyears.json"


def privacy() -> str:
    return os.environ.get("TWIN_VIDEO_PRIVACY") or ("unlisted" if PREVIEW else "public")


def title() -> str:
    from . import cut5 as C5
    f = C5.facts()
    words = {"one year": "One simulated year", "two years": "Two simulated years"}.get(f["years"],
                                                                                     f"{f['years']} (simulated)")
    t = f"{words} of alloy discovery, from the day the money arrives: round {f['round']}"
    t += " (preview)" if PREVIEW else " (digital twin)"
    return t[:100]


def _lines() -> dict:
    """{id: text} of every line the cut speaks, as spoken."""
    from . import cut5 as C5
    out = {ln["id"]: ln["text"] for ln in C5.resolved()}
    for name in ("figs5_intro", "figs5_labs"):
        m, _ = C5._mod(name)
        if m is not None:
            out.update({ln["id"]: ln["text"] for ln in m.lines()})
    fc, _ = C5._mod("floorspace_cut")
    if fc is not None:
        out.update({"fs." + ln["id"]: ln["text"] for ln in fc.narration_lines()})
    ex, _ = C5._mod("experiments")
    if ex is not None:
        out.update({"exp." + ln["id"]: ln["text"] for ln in ex.script(write=False)})
    return out


def _say(L: dict, *ids) -> str:
    return " ".join(L[i] for i in ids if i in L)


def footage_credits() -> str:
    """The aluminium runs the atomizing step shows, as the manifest names them: 'run 4yghtr (Al 6063) and ...'."""
    from . import exp_atomize as EA
    ft = EA.al_footage()
    runs, issues = [], []
    for beat in ("melt", "pour", "jar"):
        if beat in ft:
            c = ft[beat]["credit"]
            item = f"{c['run']} ({c['alloy']}, {c['day']})" if beat != "jar" else None
            if item and item not in runs:
                runs.append(item)
            if c["issue"] not in issues:
                issues.append(c["issue"])
    return " and ".join(runs) + (", " + ", ".join(issues) if issues else "")


def description(rec: dict, commit: str) -> str:
    from . import cut5 as C5
    f = C5.facts()
    L = _lines()
    head = ("A simulated benchmark, not lab results: two alloy-discovery campaigns replayed for "
            f"{f['years']} in a digital twin of BYU's Vertical Cloud Lab design, from the day the money arrives. "
            "FLAIME searches aluminium alloys for laser powder bed fusion, ONR copper alloys for blown-powder DED; "
            "they share one lab. Narrated by a synthetic voice: Kokoro v1.0 (open weights), its stock voice af_heart.")
    if PREVIEW:
        head += (f" This is a preview made from round {f['round']}'s results; the same cut will be re-rendered from "
                 "round 6's.")
    pieces = [
        head,
        "The replay, one seed for its whole length: " + _say(L, "rep2", "rep5", "rep6"),
        "The two labs, like for like: " + _say(L, "lab2", "lab3", "lab4"),
        _say(L, "nw1", "nw2", "nw3", "nw4"),
        _say(L, "mon1", "mon2", "mon3"),
        "Floor space (design layouts, not built labs): " + _say(L, "fs.f11", "fs.f12"),
        ("Real: the lab design and its 3-D model; the lab's own atomizer footage and powder photo, from its aluminium "
         f"runs {footage_credits()}; the search spaces in the two proposals; published prices. Simulated: every "
         "alloy, every measurement and every result. The atomizer's cycle and its crucibles are design targets, "
         "shown next to the lab's record. The heat-treatment profile drawn is illustrative."),
        (f"What changed from round 3b's cut ({OLD}, whose replay changed seed partway through): one continuous "
         f"replay of {f['years']} on one seed, both campaigns together, from day 0 through the build-out; each "
         "experiment beside its data (SEM detectors, a direct age, tensile plotted live, the periodic table, "
         "Scheil and AM stand-ins); floor space at matched capacity; aluminium footage for aluminium; counters "
         "that say what they count, and why a curve is flat; spending over time instead of a budget bar."),
        (f"Code: https://github.com/{M.REPO}/tree/{commit}/vertical-lab/twin (the cut: twin/video/cut5.py; notes: "
         f"notes/twin_video.md)\nPR: https://github.com/{M.REPO}/pull/{PR}"),
    ]
    chap = "Chapters\n" + "".join(f"{M.stamp(t)} {ttl}\n" for t, ttl in M.chapters(rec))
    drop = [5, 7]                          # what a long description gives up first: floor space, then what changed
    keep = list(pieces)                    # (the video and the PR say both)

    def join(ps):
        return "\n\n".join(p for p in ps if p) + "\n\n" + chap
    out = join(keep)
    while len(out.encode()) > M.DESC_BYTES and drop:
        keep[drop.pop(0)] = None
        out = join(keep)
    if len(out.encode()) > M.DESC_BYTES:
        raise SystemExit(f"the description is {len(out.encode())} bytes, over {M.DESC_BYTES}")
    return out


def write(rec: dict) -> dict:
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=D.HERE).stdout.strip()
    meta = dict(title=title(), description=description(rec, commit), tags=TAGS, categoryId="28",
                privacy=privacy(), notifySubscribers=False, file=rec.get("file"), seconds=rec.get("seconds"),
                chapters=[dict(stamp=M.stamp(t), title=ttl) for t, ttl in M.chapters(rec)], commit=commit,
                round=str(D.ROUND), preview=PREVIEW, replay=rec.get("replay"), issue=ISSUE, pr=PR)
    D.VID.mkdir(parents=True, exist_ok=True)
    (D.VID / NAME).write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return meta


if __name__ == "__main__":
    from . import cut5 as C5
    p = D.VID / f"{C5.NAME}_record.json"
    rec = json.loads(p.read_text()) if p.exists() else C5.plan_record()
    m = write(rec) if p.exists() else dict(title=title(), description=description(rec, "HEAD"))
    print(m["title"], f"({len(m['title'])} characters)")
    print(m["description"])
    print(len(m["description"].encode()), "bytes")

"""YouTube metadata for round 3b's re-cut of the campaign video (TWIN_VIDEO_ROUND=3b): title, description and tags ->
out/twin3b/video/youtube_meta_lab3d_narrated.json. The description says what the cards say, every number read from
numbers3b.numbers() (out/twin3b/like3b.json, which is what tables.md prints, on top of round 3's committed summaries),
with the chapter list from the cut as built.

    TWIN_VIDEO_ROUND=3b TWIN_VIDEO_LAB3D=1 TWIN_VIDEO_NARRATION=1 python -m twin.video.meta3b   # from the record

The wording keeps round 3's rules (DAL's audit of round 2's video, digital-alloy-lab PR 293) and adds round 3b's: the
lab comparison leads with like for like; the stock is stated as stocking, never as the lab's factor; a factor of round
3's pairing is labelled as that, beside the like-for-like one; where the automated lab doesn't win is said; the cost
is campaign spend, with fixed costs left out; and each replayed seed is named.
"""
from __future__ import annotations

import json
import subprocess
import sys

from . import data as D
from . import meta as M
from . import numbers3b as NB
from . import style as St

TITLE = "A simulated year of alloy discovery in an automated lab: round 3b, like for like (digital twin)"
TAGS = M.TAGS + ["Kardex Shuttle", "MiR250", "UR12e", "narrated", "pKGFN", "BOFN", "CALPHAD", "like for like"]
PR = f"https://github.com/{M.REPO}/pull/400"
AUDIT = "https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/293"
ROUND3 = "https://www.youtube.com/watch?v=7DjfEBGe4Jw"
ROUND2 = "https://www.youtube.com/watch?v=Pz7hxqfODmE"
AL, CU = NB.AL, NB.CU


def description(rec: dict, commit: str) -> str:
    n = NB.numbers()
    like, r3, st = n["lab"]["like"], n["lab"]["round3"], n["stock"]["vertical_lab"]
    Mn, T, rr, rep = n["main"], n["targets"], n["reruns"], n["replay"]
    a, b = rep["parts"]
    bt, pt = like[AL]["T2"]["bofn_thumb"]["days"], like[AL]["T2"]["pkgfn_thumb"]["days"]
    cf = like[CU]["T2"]["same_funnel"]["days"]
    h1, f1 = like[AL]["T1"]["same_heur"]["days"], like[CU]["T1"]["same_funnel"]["days"]
    sb, sp = st["bofn3"][AL]["T2"]["days"], st["pkgfn3"][AL]["T2"]["days"]
    bs, ps = like[AL]["T2"]["bofn_same"]["days"], like[AL]["T2"]["pkgfn_same"]["days"]
    cb = like[CU]["T1"]["bofn_same"]["days"]
    ub, uf = like[AL]["T2"]["bofn_thumb"]["usd"], like[CU]["T2"]["same_funnel"]["usd"]
    r3p, r3c = r3[AL]["T2"]["pkgfn_thumb"]["days"], r3[CU]["T2"]["same_funnel"]["days"]
    fy = n["cost"]["fixed_year"]
    atw, atl = n["atomizer"]["twin"], n["atomizer"]["lab"]
    x1, rng = NB.x1, NB.rng
    pieces = [
        "A simulated benchmark, not lab results: two alloy-discovery campaigns replayed for a whole year in a digital "
        "twin of BYU's Vertical Cloud Lab design. FLAIME searches aluminium alloys for laser powder bed fusion, ONR "
        "copper alloys for blown-powder DED; they share one lab, one atomizer and one calendar. A re-cut of round 3's "
        f"video ({ROUND3}) with round 3b's results: the two labs compared like for like. Narrated by a synthetic "
        "voice: Kokoro v1.0 (open weights), its stock voice af_heart.",
        "The lab against a conventional lab, like for like: both order their metal as they go (the automated lab's "
        "one-year runs against the conventional lab's three-year runs).\n"
        f"- Aluminium, halfway target: BOFN and pKGFN at least {x1(bt['af'])} sooner than a conventional lab run by "
        f"rule of thumb (day {bt['m_new']:.0f} against day {bt['m_ref']:.0f}; {bt['hit_new']} of 12 runs got there "
        f"against {bt['hit_ref']} of 12, so a lower bound).\n"
        f"- Copper, halfway target: {x1(cf['af'])} sooner with tiered screening in both labs (95% interval "
        f"{rng(cf['lo'], cf['hi'])}; {cf['hit_new']} of 12 against {cf['hit_ref']} of 12).\n"
        f"- To the best existing alloy on this synthetic benchmark: {x1(h1['af'])} ({rng(h1['lo'], h1['hi'])}) with the "
        f"heuristic in both labs on aluminium, {x1(f1['af'])} ({rng(f1['lo'], f1['hi'])}) with tiered screening in "
        "both on copper.",
        "Stocking is its own effect, not the lab's: with its metal on the shelf from day 0, the automated lab gets "
        f"BOFN and pKGFN to aluminium's halfway target {x1(sb['af'])} and {x1(sp['af'])} sooner than when it orders "
        f"as it goes. Round 3's {x1(r3p['af'])} (aluminium) and {x1(r3c['af'])} (copper) set a stocked automated lab "
        f"against a conventional lab ordering as it goes: {x1(r3p['af'])} is the lab's {x1(pt['af'])} times the "
        f"stock's {x1(sp['af'])}.",
        "Where the automated lab doesn't win: against the same optimizer in a conventional lab, both ordering as "
        f"they go, it is about a tie on aluminium's halfway target ({x1(bs['af'])} for BOFN, {x1(ps['af'])} for pKGFN; "
        f"{bs['n']} seeds), and the conventional lab, with three years and three years' money, reached copper's best "
        f"existing alloy in more of those seeds ({cb['hit_ref']} of {cb['n']} against {cb['hit_new']} of {cb['n']} for "
        "BOFN).",
        "Cost, on one basis: campaign spend to the target, both labs ordering as they go. At least "
        f"{x1(ub['af'])} less to aluminium's halfway target (BOFN against rule of thumb) and {x1(uf['af'])} less to "
        f"copper's (tiered screening in both; {rng(uf['lo'], uf['hi'])}); about the same, or more, against the same "
        "optimizer. Fixed costs are left out (staff, equipment, the building): round 3 put them at "
        f"{St.money(fy['vertical'])} a year for the automated lab against {St.money(fy['conventional'])}.",
        f"The replay is time-aware BOFN in the stocked automated lab on its median seeds, from the committed event "
        f"logs: seed {a['seed']} to day {rep['switch_day']} (the median seed for aluminium's halfway target, day "
        f"{a['day']:.0f}), then seed {b['seed']} (the median seed for copper's best existing alloy, day "
        f"{b['day']:.0f}).",
        f"The policies in the stocked automated lab ({Mn['bofn3'][AL]['n']} simulated one-year runs each, as in round "
        f"3): on aluminium BOFN and pKGFN finished highest ({Mn['bofn3'][AL]['best']:.2f}, "
        f"{Mn['pkgfn3'][AL]['best']:.2f}); on copper tiered CALPHAD screening still finished ahead "
        f"({Mn['tiered'][CU]['best']:.2f} against {Mn['bofn3'][CU]['best']:.2f} and {Mn['pkgfn3'][CU]['best']:.2f}), "
        "and money, not capacity, was the limit.",
        f"The targets: the first is the best existing alloy on this synthetic benchmark ({T['ref'][AL]} "
        f"{T['T1'][AL]:.2f}, {T['ref'][CU]} {T['T1'][CU]:.2f}); one random design in {T['one_in']} beats it. The "
        f"halfway target ({T['T2'][AL]:.2f}, {T['T2'][CU]:.2f}) is halfway from there to the best alloy the twin's "
        "own search found.",
        f"The atomizer runs at design targets, not demonstrated rates: in the twin, {atw['slots_week']} start slots a "
        f"week (about {rep['atomizer_runs_week']:.0f} used) and a {100 * atw['p_fail_base']:.0f}% base chance of "
        f"failure; the lab's record so far is {atl['runs_week']:.1f} runs a week, with problems in "
        f"{atl['runs'] - atl['good']} of {atl['runs']} runs. Real: the lab design's 3-D renders, the atomizer "
        "footage, the search spaces, USGS prices. Simulated: the alloys, every measurement and every result.",
        f"Round 3's runs rerun under a pinned numerical set-up: {rr['identical']} of {rr['rerun']} identical, the "
        f"other {rr['last_bit']} to the last bit of a utility.",
        f"Round 3's video: {ROUND3}\nRound 2's video: {ROUND2}\nThe audit the wording follows: {AUDIT}",
        f"Code: https://github.com/{M.REPO}/tree/{commit}/vertical-lab/twin (video: twin/video; script: "
        f"twin/video/narration3b.json; write-up: notes/twin_round3b.md, notes/twin_video.md)\nPR: {PR}",
    ]
    chap = "Chapters\n" + "".join(f"{M.stamp(t)} {title}\n" for t, title in M.chapters(rec))
    drop = [9, 8, 7, 6]                                 # the pieces a long description gives up first: the reruns,
    out = "\n\n".join(pieces) + "\n\n" + chap           # the atomizer, the targets, the policies
    while len(out.encode()) > M.DESC_BYTES and drop:
        pieces[drop.pop(0)] = None
        out = "\n\n".join(p for p in pieces if p) + "\n\n" + chap
    return out


def write(rec: dict) -> dict:
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=D.HERE).stdout.strip()
    meta = dict(title=TITLE[:100], description=description(rec, commit), tags=TAGS, categoryId="28",
                privacy="public", notifySubscribers=False, file=rec.get("file"), seconds=rec.get("seconds"),
                chapters=[dict(stamp=M.stamp(t), title=ttl) for t, ttl in M.chapters(rec)], commit=commit,
                placeholder=rec.get("placeholder"), replay=rec.get("replay"))
    (D.VID / "youtube_meta_lab3d_narrated.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return meta


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "final3d_narrated_record.json"
    p = D.VID / name
    if p.exists():
        m = write(json.loads(p.read_text()))
    else:                                               # before the cut is built: the plan's chapters
        from . import compose as C
        commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                                cwd=D.HERE).stdout.strip()
        m = dict(title=TITLE[:100], description=description(C.plan_record(), commit))
    print(m["title"], f"({len(m['title'])} characters)")
    print(m["description"])
    print(len(m["description"].encode()), "bytes")

"""YouTube metadata for round 3's campaign video (TWIN_VIDEO_ROUND=3): title, description and tags ->
out/twin3/video/youtube_meta_lab3d_narrated.json. The description says what the cards say, every number read from
numbers3.numbers() (round 3's committed summaries), with the chapter list from the cut as built.

    TWIN_VIDEO_ROUND=3 TWIN_VIDEO_LAB3D=1 TWIN_VIDEO_NARRATION=1 python -m twin.video.meta3   # from the record

The wording follows DAL's audit of round 2's video (digital-alloy-lab PR 293): no lab-against-lab factor in the
headline, each factor with which lab is stocked and its run counts, a lower bound called one, the cost on one basis,
the first target called what it is with the halfway target beside it, and the replayed seed named.
"""
from __future__ import annotations

import json
import subprocess
import sys

from . import data as D
from . import meta as M
from . import numbers3 as N3

TITLE = "A simulated year of alloy discovery in an automated lab: round 3 (digital twin benchmark)"
TAGS = M.TAGS + ["Kardex Shuttle", "MiR250", "UR12e", "narrated", "pKGFN", "BOFN", "CALPHAD"]
PR = f"https://github.com/{M.REPO}/pull/394"
AUDIT = "https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/293"
ROUND2 = "https://www.youtube.com/watch?v=Pz7hxqfODmE"


def description(rec: dict, commit: str) -> str:
    n = N3.numbers()
    Mn, al, cu = n["main"], "flaime_al", "onr_cu"
    T, cm, L = n["targets"], n["cu_money"], n["labs"]
    b, p, h, f = Mn["bofn3"], Mn["pkgfn3"], Mn["heuristic"], Mn["tiered"]
    same_cu, thumb_al = L[cu]["same"]["T2"], L[al]["thumb"]["T2"]
    same_al, thumb_cu = L[al]["same"]["T2"], L[cu]["thumb"]["T2"]
    cst, K = n["cost"]["to_T1"], n["cost"]["per_alloy"]
    rep, atw, atl = n["replay"], n["atomizer"]["twin"], n["atomizer"]["lab"]
    from . import style as St
    pieces = [
        "A simulated benchmark, not lab results: two alloy-discovery campaigns replayed for a whole year in a digital "
        "twin of BYU's Vertical Cloud Lab design. FLAIME searches aluminium alloys for laser powder bed fusion and ONR "
        "copper alloys for blown-powder DED; both share one lab, one atomizer and one calendar. Round 3 of the twin: "
        "no cap on work in flight, decisions every simulated hour, one spending plan, interim immersion readings, "
        "pKGFN. Narrated by a synthetic voice: Kokoro v1.0 (open weights, run locally), its stock voice af_heart.",
        f"What it found ({b[al]['n']} simulated one-year runs per policy):\n"
        f"- Aluminium: time-aware BOFN and pKGFN reached the halfway target on day {b[al]['T2']['day']:.0f} and day "
        f"{p[al]['T2']['day']:.0f} ({b[al]['T2']['hit']} and {p[al]['T2']['hit']} of 12 runs) and finished at "
        f"{b[al]['best']:.2f} and {p[al]['best']:.2f}. A metallurgist's heuristic reached the best existing alloy's "
        f"score first (day {h[al]['T1']['day']:.0f}) and then stalled.\n"
        f"- Copper: tiered CALPHAD screening still finished ahead ({f[cu]['best']:.2f} against {b[cu]['best']:.2f} "
        f"for BOFN and {p[cu]['best']:.2f} for pKGFN) and reached the halfway target on day {f[cu]['T2']['day']:.0f} "
        f"({f[cu]['T2']['hit']} of 12 runs). Copper was limited by money, not capacity: with three times the copper "
        f"money, BOFN and pKGFN gained {cm['bofn3']['own']['mean']:.2f} and {cm['pkgfn3']['own']['mean']:.2f} "
        f"({cm['bofn3']['n']} runs each) and drew level on the final alloy.",
        "Against a conventional lab, to the halfway target (a stocked automated lab, one-year runs, against a "
        "conventional lab ordering metal as it goes, three-year runs). The same policy in both labs: copper "
        f"{N3.x1(same_cu['af'])} sooner with tiered screening (95% interval {N3.rng(same_cu['lo'], same_cu['hi'])}; "
        f"{same_cu['hit_new']} of 12 runs against {same_cu['hit_ref']} of 12), and no speed-up on aluminium with the "
        f"heuristic ({same_al['hit_new']} of 12 runs against {same_al['hit_ref']} of 12). Against a conventional lab "
        f"run by rule of thumb: aluminium at least {N3.x1(thumb_al['af'])} sooner with pKGFN (the conventional lab "
        f"got there in {thumb_al['hit_ref']} of 12 runs, so this is a lower bound), and no factor on copper "
        f"({thumb_cu['hit_new']} of 12 runs against {thumb_cu['hit_ref']} of 12). Not run in round 3: both labs "
        "ordering metal as they go (so the stock's share of a factor is not known), and BOFN or pKGFN in the "
        "conventional lab.",
        f"Cost, equipment included: reaching the first target cost {cst[al]['full_alone']['ratio']:.1f}x the "
        f"conventional lab's cost for aluminium (95% interval {N3.rng(cst[al]['full_alone']['lo'], cst[al]['full_alone']['hi'])}) "
        f"and {cst[cu]['full_alone']['ratio']:.1f}x for copper "
        f"({N3.rng(cst[cu]['full_alone']['lo'], cst[cu]['full_alone']['hi'])}). A demonstrated alloy cost "
        f"{St.money(K['both|vertical lab, campaigns only, with capex'])} against "
        f"{St.money(K['both|conventional, with capex'])} while the two campaigns carry the lab alone; they use "
        f"{100 * n['util']['capex_weighted']:.0f}% of its capacity.",
        f"The targets: the first is the best existing alloy on this synthetic benchmark ({T['ref'][al]} "
        f"{T['T1'][al]:.2f}, {T['ref'][cu]} {T['T1'][cu]:.2f}); one random design in {T['one_in']} beats it. The "
        f"halfway target ({T['T2'][al]:.2f}, {T['T2'][cu]:.2f}) is halfway from there to the best alloy the twin's "
        "own search found.",
        f"The replay is seed {rep['seed']} of {rep['n']} of time-aware BOFN, the one seed whose event log round 3 "
        f"kept: the median seed for aluminium (halfway target on day {rep[al]['T2']['day']:.0f}), and one of the "
        f"{rep['n'] - rep[cu]['T1']['hits']} seeds that never reach copper's first target (the median seed gets "
        f"there on day {rep[cu]['T1']['median']:.0f}).",
        f"The atomizer runs at design targets, not demonstrated rates: in the twin, {atw['slots_week']} start slots "
        f"a week (about {rep['atomizer_runs_week']:.0f} used) and a {100 * atw['p_fail_base']:.0f}% base chance of "
        f"failure; the lab's own record so far is {atl['runs_week']:.1f} runs a week, with problems in "
        f"{atl['runs'] - atl['good']} of {atl['runs']} runs. Real: the lab design's 3-D renders, the atomizer "
        "footage, the search spaces, USGS prices. Simulated: the alloys, every measurement (modelled noise not yet "
        "calibrated on the lab's instruments) and every result.",
        f"The wording follows the audit of round 2's video: {AUDIT}\nRound 2's video: {ROUND2}",
        f"Code: https://github.com/{M.REPO}/tree/{commit}/vertical-lab/twin (video: twin/video; script: "
        f"twin/video/narration3.json; write-up: notes/twin_round3.md, notes/twin_video.md)\nPR: {PR}",
    ]
    chap = "Chapters\n" + "".join(f"{M.stamp(t)} {title}\n" for t, title in M.chapters(rec))
    out = "\n\n".join(pieces) + "\n\n" + chap
    while len(out.encode()) > M.DESC_BYTES and len(pieces) > 5:     # keep the findings and every timestamp
        pieces.pop(-3)
        out = "\n\n".join(pieces) + "\n\n" + chap
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
    m = write(json.loads((D.VID / name).read_text()))
    print(m["title"])
    print(m["description"])
    print(len(m["description"].encode()), "bytes")

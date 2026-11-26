"""YouTube metadata for the campaign video: title, description (the takeaway's numbers, what is simulated, the
sources, and a chapter list whose timestamps come from the cut as built) and tags -> out/twin2/video/youtube_meta.json.

    python -m twin.video.meta            # rebuild youtube_meta.json from out/twin2/video/final_record.json

Every number in the description is read through data.py, as on screen.
"""
from __future__ import annotations

import json
import subprocess
import sys

from . import data as D

REPO = "vertical-cloud-lab/byu-vcl"
PR = f"https://github.com/{REPO}/pull/318"
TITLE = "A year of alloy discovery in an automated lab: a simulated benchmark (digital twin)"
TAGS = ["vertical cloud lab", "BYU", "self-driving lab", "laboratory automation", "digital twin", "alloy development",
        "aluminium alloys", "copper alloys", "laser powder bed fusion", "directed energy deposition",
        "Bayesian optimization", "function networks", "materials acceleration platform", "simulated benchmark"]
GAP = 10.0                       # YouTube: chapters at least 10 s long, the first at 0:00
DESC_BYTES = 4850


def stamp(t: float) -> str:
    t = int(round(t))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def chapters(rec: dict) -> list:
    out = []
    total = float(rec.get("seconds") or rec["total_s"])
    for t, title in sorted(rec["chapters"]):
        if out and t - out[-1][0] < GAP:
            if out[-1][1] == "Title":                # the short title card gives its 0:00 to what follows it
                out[-1] = (out[-1][0], title)
            continue
        if total - t < GAP:
            continue
        out.append((t, title))
    if out:
        out[0] = (0.0, out[0][1])
    return out


def _x(v, at_least=False):
    if v is None:
        return "pending"
    return f"{'at least ' if at_least else ''}{v:.1f}x"


def _pct(v):
    return "pending" if v is None else f"{100 * v:.0f}%"


def _caveats(policy: str) -> list:
    """The comparisons the takeaway doesn't carry: the automated lab against the conventional lab run with a
    metallurgist's heuristic, and where BOFN doesn't win (from econ_summary.json and bench2_summary.json)."""
    import math
    out = []
    try:
        acc = (D.econ().get("raw") or {}).get("acceleration") or {}
        nm = next((n for n in acc if n.startswith(f"vertical lab + {policy} vs") and n.endswith("+ heuristic")), None)
        bits = []
        for c, lab in (("flaime_al", "FLAIME"), ("onr_cu", "ONR")):
            af = ((((acc.get(nm) or {}).get(c) or {}).get("compare") or {}).get("days") or {}).get("af") if nm else None
            if af is not None and math.isfinite(float(af)):
                bits.append(f"{lab} {float(af):.1f}x")
        if bits:
            out.append("Against the conventional lab run with a metallurgist's heuristic instead: " + ", ".join(bits) +
                       " faster to the same target; there the automated lab costs more unless outside users share it "
                       "(notes/twin_econ.md).")
    except Exception:                                   # noqa: BLE001
        pass
    try:
        E = json.loads((D.OUT2 / "bench2_summary.json").read_text())["experiments"]
        g = lambda exp, key: E[exp][key]["campaigns"]["onr_cu"]["best_mean"]
        t, b = g("main", "vertical_lab_tiered"), g("main", "vertical_lab_bofn_blend")
        th, bh = g("cu_hidden", "vertical_lab_tiered_cu_hidden-1.0"), g("cu_hidden", "vertical_lab_bofn_blend_cu_hidden-1.0")
        out.append(f"Where BOFN doesn't win: on copper, tiered CALPHAD screening finished ahead of BOFN with blend "
                   f"screening ({t:.2f} against {b:.2f}; with a hidden gamma-2 corrosion effect, {th:.2f} against "
                   f"{bh:.2f}); on aluminium a metallurgist's heuristic reaches the state of the art sooner, and BOFN's "
                   "lead is in the final alloy.")
    except Exception:                                   # noqa: BLE001
        pass
    return out


LAB3D_TITLE = "A year of alloy discovery in an automated lab, animated: a simulated benchmark (digital twin)"
LAB3D_PR = f"https://github.com/{REPO}/pull/393"
LAB3D_NOTE = ("This cut's replay animates PR 318's 3-D lab from the twin's event log: every tray presented at a Kardex "
              "Shuttle's opening and every MiR250 + UR12e visit to a dock comes from a booking (a station on a tray has "
              "its tray brought to the opening at the booking's start and end; a floor machine has a unit dock at its "
              "front), and idle trays stay in their slots. The clock runs at 1.5-60 lab hours a second, so the moves "
              "run on their own clock, 8-16 times real time, with the tower's and the MiR250's own timings, each "
              "starting when the clock reaches its booking; when they can't keep up, each Shuttle and unit takes the "
              "latest request, and the panel at the bottom counts how many were drawn.\n\n")


def description(rec: dict, commit: str, lab3d: bool = False) -> str:
    R = D.Replay()
    hd = D.headline(R)
    lines = []
    for c, name in (("flaime_al", "FLAIME (Al alloys for laser powder bed fusion)"),
                    ("onr_cu", "ONR (Cu alloys for blown-powder DED)")):
        h = hd.get(c, {})
        costs = h.get("costs") or {}
        parts = [f"{lab} {_pct((costs.get(k) or {}).get('ratio'))}" for k, lab in
                 (("op_alone", "operating, no capex"), ("full_alone", "full, with capex"),
                  ("op_shared", "operating, lab shared with outside users"),
                  ("full_shared", "full, lab shared with outside users")) if costs.get(k)]
        lines.append(f"- {name}: reached the state-of-the-art target {_x(h.get('accel'), h.get('accel_at_least'))} "
                     f"faster. Its cost against the conventional lab's: " + "; ".join(parts) + ".")
    cmp_ = hd.get("comparison") or "the benchmark curves"
    head = ("A simulated benchmark, not lab results: two alloy-discovery campaigns replayed for a whole year in a "
            "digital twin of BYU's Vertical Cloud Lab design (PR 318), against the same campaigns run the "
            "conventional way (partner facilities and core facilities).\n\n"
            "FLAIME searches aluminium alloys for laser powder bed fusion and ONR copper alloys for blown-powder DED. "
            "Both share one lab, one atomizer and one calendar. The video shows the two function networks, the "
            "figures we track, the year at increasing speed (one alloy start to finish on day 1, then " +
            ("the 3-D lab moved by the event log, up close and then from above" if lab3d else
             "the station cameras, then the whole lab with each station lit by the event log") +
            "), and the results.\n\n" + (LAB3D_NOTE if lab3d else "") +
            f"In this simulated benchmark ({cmp_}):\n" + "\n".join(lines) + "\n" +
            "".join(f"{x}\n" for x in _caveats(R.policy)) + "\n"
            "Real: the lab design's 3-D renders, the atomizer footage, the search spaces (the proposals), USGS prices "
            "and the economics' sources. Assumed: station times, fees and outside-facility delays. Simulated: the "
            "alloys' properties, every measurement and every result.\n\n" +
            ("Narrated by a synthetic voice: Kokoro v1.0 (open weights, run locally), its stock voice af_heart. The "
             "script, with timestamps, is in notes/twin_video.md; subtitles in "
             "out/twin2/video/narration/narration.srt.\n\n" if rec.get("narration") else "") +
            f"Code: https://github.com/{REPO}/tree/{commit}/vertical-lab/twin (video: twin/video, write-up "
            f"notes/twin_video.md)\nPR: {LAB3D_PR + ' (the twin), ' + PR + ' (the lab design)' if lab3d else PR}\n\n")
    chap = "Chapters\n" + "".join(f"{stamp(t)} {title}\n" for t, title in chapters(rec))
    s = head + chap
    while len(s.encode()) > DESC_BYTES and lines:     # keep every timestamp; trim the prose
        head = head[: max(0, len(head) - 200)]
        s = head + chap
    return s


NARRATED_TITLE = "A year of alloy discovery in an automated lab, narrated: a simulated benchmark (digital twin)"


def _f(v, nd=1) -> str:
    import math
    return "unbounded" if v is None or not math.isfinite(float(v)) else (f"{v:.0f}" if v == 0 else f"{v:.{nd}f}")


def description_narrated(rec: dict, commit: str, lab3d: bool = False) -> str:
    """The narrated cut's description: the findings in the words DAL's audit of the first cut suggested
    (digital-alloy-lab PR 293 §4), each number read from econ_summary.json, bench2_summary.json and oracle.json as
    the narration and the captions say them."""
    from . import figs_anim as F
    R = D.Replay()
    hd = D.headline(R)
    E = D.econ(R.policy)
    aud = F.audit_numbers()
    fa, fc = hd.get("flaime_al", {}), hd.get("onr_cu", {})
    ca, cc = fa.get("costs") or {}, fc.get("costs") or {}
    acc = (E.get("raw") or {}).get("acceleration") or {}
    nm = next((n for n in acc if n.startswith(f"vertical lab + {R.policy} vs") and n.endswith("+ heuristic")), None)
    ha = (((acc.get(nm) or {}).get("flaime_al") or {}).get("compare") or {}) if nm else {}
    hc = (((acc.get(nm) or {}).get("onr_cu") or {}).get("compare") or {}) if nm else {}
    lean, cu = aud.get("lean_af") or {}, aud.get("cu24") or {}
    n_c = fc.get("n_conv") or 12
    seed_day = next((x for x, y in R.curve_upto("flaime_al", R.horizon_h, "days") if y >= hd["target"]["flaime_al"]),
                    None)
    fr = aud.get("frac_random")
    B = json.loads((D.OUT2 / "bench2_summary.json").read_text())["experiments"]["main"]
    t12 = B["vertical_lab_tiered"]["campaigns"]["onr_cu"]["best_mean"]
    b12 = B["vertical_lab_bofn_blend"]["campaigns"]["onr_cu"]["best_mean"]
    pieces = [
        "A simulated benchmark, not lab results: two alloy-discovery campaigns replayed for a whole year in a digital "
        "twin of BYU's Vertical Cloud Lab design (PR 318). FLAIME searches aluminium alloys for laser powder bed "
        "fusion and ONR copper alloys for blown-powder DED; both share one lab, one atomizer and one calendar. "
        "Narrated by a synthetic voice: Kokoro v1.0 (open weights, run locally), its stock voice af_heart.",
        f"In this simulated benchmark, a stocked automated lab reached a new alloy better than the reference alloy "
        f"sooner than a conventional lab that orders metal as it goes: aluminium in {_f(fa.get('days_auto'), 0)} days "
        f"against {_f(fa.get('days_conv'), 0)} ({_f(fa.get('accel'))}x, 95% interval {_f(fa.get('accel_lo'))} to "
        f"{_f(fa.get('accel_hi'))}), copper in {_f(fc.get('days_auto'), 0)} days against at least "
        f"{_f(fc.get('days_conv'), 0)} (at least {_f(fc.get('accel'))}x; the conventional lab got there in "
        f"{round((fc.get('hit_conv') or 0) * n_c)} of {n_c} three-year runs). Most of aluminium's gain is the stock: "
        f"with both labs ordering as they go it is {_f(lean.get('af'))}x ({_f(lean.get('lo'))} to "
        f"{_f(lean.get('hi'))}). Copper's comparison also changes the method: the automated lab screens powder "
        "blends first.",
        f"To get there, the automated lab cost {F._x2((ca.get('full_alone') or {}).get('ratio'))} as much for "
        f"aluminium and {F._x2((cc.get('full_alone') or {}).get('ratio'))} for copper, equipment included "
        f"({F._x1((ca.get('cash') or {}).get('ratio'))} and {F._x1((cc.get('cash') or {}).get('ratio'))} counting "
        "only what the campaigns spent). Equipment included, it costs less than the conventional lab only for copper, "
        "and only if outside users rent its idle hours, which this model assumes and does not show.",
        f"The target is the reference alloy's score on the twin's synthetic alloy model (AlSi10Mg, C95800). One "
        f"random design in {round(1 / fr) if fr else 12} beats it, so reaching it measures how fast a lab makes and "
        "tests its first alloys, not a discovery.",
        f"Against a conventional lab run by a metallurgist's rules of thumb, the automated lab is no faster on "
        f"aluminium ({(ha.get('days') or {}).get('af', float('nan')):.2f}x, {_f((ha.get('days') or {}).get('lo'))} to "
        f"{_f((ha.get('days') or {}).get('hi'))}) at "
        f"{F._x1(((ha.get('cost') or {}).get('operating, alone') or {}).get('ratio'))} the operating cost, and "
        f"{F._x1((hc.get('days') or {}).get('af'))} faster on copper ({_f((hc.get('days') or {}).get('lo'))} to "
        f"{_f((hc.get('days') or {}).get('hi'))}).",
        f"Where BOFN doesn't win: on copper, tiered CALPHAD screening finished ahead of BOFN with blend screening, "
        f"{cu['tiered'][0]:.2f} against {cu['blend'][0]:.2f} over {cu['tiered'][1]} seeds ({t12:.2f} against "
        f"{b12:.2f} in the first 12); plain BOFN did no better than random ({cu['bofn']:.2f} against "
        f"{cu['random']:.2f})." if cu else "",
        f"The replay is one seed of {fa.get('n_auto') or 12}: in it, aluminium reaches the target on day "
        f"{_f(seed_day, 0)}; the median seed takes {_f(fa.get('days_auto'), 0)} days." if seed_day else "",
        (LAB3D_NOTE.strip() if lab3d else ""),
        "Real: the lab design's 3-D renders, the atomizer footage, the search spaces (the proposals), USGS prices and "
        "the economics' sources. Assumed: station times, fees and outside-facility delays; the automated lab's stock "
        "on day 0; the atomizer's failure rate and yield; who staffs the automated lab. Simulated: the alloys' "
        "properties, every measurement (with modelled noise not yet calibrated on the lab's instruments) and every "
        "result. The audit this wording follows: https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/293",
        f"Code: https://github.com/{REPO}/tree/{commit}/vertical-lab/twin (video: twin/video; script, with timestamps: "
        "notes/twin_video.md)\nPR: https://github.com/vertical-cloud-lab/byu-vcl/pull/393",
    ]
    head = "\n\n".join(x for x in pieces if x) + "\n\n"
    chap = "Chapters\n" + "".join(f"{stamp(t)} {title}\n" for t, title in chapters(rec))
    out = head + chap
    while len(out.encode()) > DESC_BYTES and len(pieces) > 3:   # keep the findings and every timestamp
        pieces.pop(-3)
        head = "\n\n".join(x for x in pieces if x) + "\n\n"
        out = head + chap
    return out


def write(rec: dict, lab3d: bool = False, narrated: bool = False) -> dict:
    """youtube_meta.json (the public cut), youtube_meta_lab3d.json (the animated cut: unlisted), and with the narration
    (compose.NARRATE) youtube_meta[_lab3d]_narrated.json (unlisted)."""
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=D.HERE).stdout.strip()
    title = NARRATED_TITLE if narrated else (LAB3D_TITLE if lab3d else TITLE)
    meta = dict(title=title[:100], description=(description_narrated(rec, commit, lab3d) if narrated else
                                                description(rec, commit, lab3d)),
                tags=TAGS + (["Kardex Shuttle", "MiR250", "UR12e"] if lab3d else []) + (["narrated"] if narrated
                                                                                        else []), categoryId="28",
                privacy="unlisted" if (lab3d or narrated) else "public", notifySubscribers=False,
                file=rec.get("file"), seconds=rec.get("seconds"),
                chapters=[dict(stamp=stamp(t), title=ttl) for t, ttl in chapters(rec)],
                commit=commit, placeholder=rec.get("placeholder"), replay=rec.get("replay"))
    name = ("youtube_meta_lab3d" if lab3d else "youtube_meta") + ("_narrated" if narrated else "") + ".json"
    (D.VID / name).write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return meta


if __name__ == "__main__":
    rec = json.loads((D.VID / (sys.argv[1] if len(sys.argv) > 1 else "final_record.json")).read_text())
    m = write(rec)
    print(m["title"])
    print(m["description"])

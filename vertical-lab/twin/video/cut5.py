"""The two-year cut (rounds 5 and later): one continuous replay from the day the money arrives, with every module.

    export TWIN_VIDEO_ROUND=5            # the one switch: 6 re-renders the same cut from round 6's results
    python -m twin.video.cut5 all        # numbers, checks, speech, the 3-D track, the encode, the record, the sheet
    python -m twin.video.cut5 plan       # the segments with their times, the chapters, each line's place
    python -m twin.video.cut5 check      # every spoken number and worded claim against the round's tables
    python -m twin.video.cut5 stills 30 400 ...      # frames of the cut at those seconds -> /tmp/vid/cut5_<t>.png
    python -m twin.video.cut5 finish [segment ...]   # encode only those segments again, then the join and the sound
    python -m twin.video.cut5 script     # the narration in order with its times -> out/twin<R>/video/twoyears_script.md

The segments, in order, and the module each comes from:

    title        this module
    simulated    compose.simulated_frame: the lab and the two search spaces
    changes      figs5_intro: what the round changed in the twin
    experiments  experiments.Chapter: each step of the two networks as the experiment and its data (PR 403)
    counters     figs5_intro: designed / made / tested, early stopping, how to read the replay's plots
    atomizer     figs5_intro: the atomizer's design targets next to the lab's record
    replay       replay5: day 0 to the horizon on one seed, both campaigns
    labs         figs5_labs: the lab comparison, like for like first; where the automated lab doesn't win; spending
    floorspace   floorspace_cut: three labs on floor space, capacity matched (PR 406)
    takeaway     figs5_labs
    notes        figs5_intro: real, assumed, simulated

Every module keeps its own lines, its own recorded audio and its own check of the numbers it speaks; this module
places them on the cut (each segment's lines at their times in it), mixes one track and writes the subtitles. Its own
lines (the opening and the replay's, narration5.json) are templates filled from facts(), which reads the replayed
run from data5: no number in them is typed.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

from . import compose as C
from . import data as D
from . import data5 as D5
from . import replay5 as R5
from . import style as St

if not D.R5:
    raise SystemExit("twin.video.cut5 is the cut of rounds 5 and later: set TWIN_VIDEO_ROUND=5 (or 6)")

HERE = D.HERE
FPS = 30
W, H = St.W, St.H
px = St.px
VID = D.VID
TMP = VID / "parts"
NAME = "twoyears"                                   # out/twin<R>/video/twoyears.mp4
SCRIPT = Path(__file__).with_name("narration5.json")
NDIR = VID / "narration"
HPD = 24.0
ROUND = D.ROUND
_S: dict = {}


def _init():
    """compose's shared state, for the pieces of it this cut reuses (the opening's lab clips and search spaces, the
    docked networks): the replay is this round's, never compose's own."""
    if "init" not in _S:
        C._S["R"] = R5.R()
        C._S["tl"] = R5.tl()
        _S["init"] = True


# ================================================================================================== the title
def _years() -> str:
    y = R5.R().horizon_days / 365.0
    n = int(round(y))
    words = {1: "One", 2: "Two", 3: "Three"}.get(n, str(n))
    return f"{words} simulated year{'s' if n != 1 else ''}"


TITLE_DUR = 13.0


def title_frame(t: float) -> np.ndarray:
    _init()
    I = D5.info()
    be = C.S("be")
    fr = np.asarray(be.base("high", 1.0 + 0.04 * t / 8.0, (0.5, 0.5))).copy()
    St.dim(fr, 0.26)
    k = St.window(t, 0.2, TITLE_DUR, 0.8)
    im, d = St.layer()
    d.text((W / 2, px(318)), f"{_years()} of alloy discovery,", font=St.font(62, bold=True), fill=St.INK, anchor="mm")
    d.text((W / 2, px(396)), "from the day the money arrives", font=St.font(62, bold=True), fill=St.INK, anchor="mm")
    d.text((W / 2, px(474)), f"Round {I['round']} of a digital-twin benchmark: one seed, both campaigns, both labs",
           font=St.font(32), fill=St.INK2, anchor="mm")
    y = px(566)
    for c in D.CAMPAIGNS:
        f = St.font(28)
        txt = St.CAMP_LONG[c]
        tw = St.text_w(f, txt) + px(36)
        x0 = (W - tw) / 2
        d.rounded_rectangle((x0, y - px(4), x0 + px(22), y + px(28)), radius=px(4), fill=St.CAMP[c])
        d.text((x0 + px(36), y + px(12)), txt, font=f, fill=St.INK, anchor="lm")
        y += px(52)
    d.text((W / 2, px(770)), "BYU Vertical Cloud Lab, PR 318's lab design. No real experiments: every result is "
           "simulated.", font=St.font(24), fill=St.INK2, anchor="mm")
    d.text((W / 2, px(816)), f"The replay is seed {I['seed']} of {I['n_seeds']}, for its whole length. Earlier cuts are "
           "linked in the description.", font=St.font(20), fill=St.INK2, anchor="mm")
    St.paste(fr, im, 0, 0, k)
    return fr


def simulated_frame(t: float) -> np.ndarray:
    _init()
    return C.simulated_frame(t)


def replay_frame(t: float) -> np.ndarray:
    _init()
    return R5.replay_frame(t)


# ================================================================================================== the modules
def _missing_frame(name: str, why: str):
    def fn(t: float) -> np.ndarray:
        fr = St.blank()
        im, d = St.layer()
        d.text((W / 2, H / 2 - px(20)), f"[{name}: not built]", font=St.font(48, bold=True), fill=St.WARN, anchor="mm")
        d.text((W / 2, H / 2 + px(40)), why[:120], font=St.font(22), fill=St.INK2, anchor="mm")
        St.paste(fr, im, 0, 0)
        return fr
    return fn


def _mod(name: str):
    """A segment module, or (None, why) while it does not import."""
    import importlib
    try:
        return importlib.import_module(f"twin.video.{name}"), ""
    except Exception as e:                                  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


ORDER = ("title", "simulated", "changes", "experiments", "counters", "atomizer", "replay", "labs", "floorspace",
         "takeaway", "notes")
CARDS = {"changes": ("figs5_intro", "What changed in the twin"),
         "counters": ("figs5_intro", "Counters, early stopping, and how to read the replay"),
         "atomizer": ("figs5_intro", "The atomizer: design targets next to the lab's record"),
         "notes": ("figs5_intro", "Notes: real, assumed, simulated"),
         "labs": ("figs5_labs", "The lab comparison, like for like"), "takeaway": ("figs5_labs", "The takeaway")}


def segment(name: str) -> dict:
    """One segment: dict(name, dur, fn, title, lines (a function returning its placed lines), caps, missing). Only its
    own module is loaded, so a worker encoding one segment doesn't build the others."""
    key = ("seg", name)
    if key in _S:
        return _S[key]
    I = D5.info()

    def seg(dur, fn, title, lines=None, caps=None, missing=""):
        return dict(name=name, dur=float(dur), fn=fn, title=title, lines=lines or (lambda: []),
                    caps=caps or (lambda: []), missing=missing)

    def lost(why, title):
        return seg(6.0, _missing_frame(name, why), title, missing=why)
    if name == "title":
        out = seg(TITLE_DUR, title_frame, f"{_years()} of alloy discovery: round {I['round']}",
                  lines=lambda: own_lines("title"))
    elif name == "simulated":
        out = seg(C.SIM_DUR, simulated_frame, "What is simulated: the lab and two search spaces",
                  lines=lambda: own_lines("simulated"), caps=lambda: C.SIM_CAPS)
    elif name == "replay":
        out = seg(R5.tl().dur, replay_frame, f"The replay: {facts()['years']} on one seed",
                  lines=lambda: own_lines("replay"), caps=R5.captions)
    elif name in CARDS:
        mod_name, title = CARDS[name]
        m, why = _mod(mod_name)
        got = {x[0]: x for x in m.SEGMENTS} if m is not None else {}
        if name in got:
            _, dur, fn, ttl = got[name]
            out = seg(dur, fn, ttl, lines=lambda: m.narration_lines(name), caps=lambda: m.captions(name))
        else:
            out = lost(why or f"{mod_name} has no segment '{name}'", title)
    elif name == "experiments":
        title = "The function networks: each experiment beside its data"
        ex, why = _mod("experiments")
        try:
            if ex is None:
                raise ImportError(why)
            if not hasattr(ex, "narration_lines"):
                raise AttributeError("experiments.narration_lines is missing")
            ch = ex.Chapter()
            out = seg(float(ch.DURATION), ch.frame, title, lines=lambda: ex.narration_lines(),
                      caps=lambda: list(getattr(ch, "captions", [])))
        except Exception as e:                              # noqa: BLE001
            out = lost(f"{type(e).__name__}: {e}", title)
    elif name == "floorspace":
        title = "Floor space: three labs, capacity matched"
        fc, why = _mod("floorspace_cut")
        try:
            if fc is None:
                raise ImportError(why)
            if not (hasattr(fc, "segment_frame") and hasattr(fc, "narration_lines")):
                raise AttributeError("floorspace_cut.segment_frame / narration_lines are missing")
            out = seg(float(fc.Cut().T), fc.segment_frame, title, lines=lambda: fc.narration_lines())
        except Exception as e:                              # noqa: BLE001
            out = lost(f"{type(e).__name__}: {e}", title)
    else:
        raise KeyError(name)
    _S[key] = out
    return out


def segments() -> list:
    return [segment(n) for n in ORDER]


def missing() -> list:
    return [(s["name"], s["missing"]) for s in segments() if s["missing"]]


# ================================================================================================== this cut's lines
def _fmt_day(x: dict, horizon: float) -> str:
    return f"{x['day']:.0f}" if x["hit"] else None


def facts() -> dict:
    """What this module's own lines and on-screen words say, read from the replayed run (data5.info(): the two rows
    of the replayed seed, and the round's median_seed and arm statistics). Strings as they are shown and spoken, and
    booleans for the lines' `when`."""
    if "facts" in _S:
        return _S["facts"]
    I = D5.info()
    ra, rc = R5.R("auto"), R5.R("conv")
    hz = I["horizon_days"]
    f: dict = dict(round=str(I["round"]), seed=str(I["seed"]), n_seeds=str(I["n_seeds"]), horizon=f"{hz:.0f}",
                   years={1: "one year", 2: "two years", 3: "three years"}.get(int(round(hz / 365)),
                                                                                f"{hz / 365:.0f} years"),
                   policy=I["policy_words"], stock=I["stock_words"], is_median=bool(I["is_median_seed"]))
    if ra.room_h is not None:
        f["room_day"] = f"{ra.room_h / HPD:.0f}"
    if ra.cell_h is not None:
        f["cell_day"] = f"{ra.cell_h / HPD:.0f}"
    f["n_stations"] = str(len(ra.station_online))
    for lab, part in (("auto", I["auto"]), ("conv", I["conv"])):
        for c, cn in (("flaime_al", "al"), ("onr_cu", "cu")):
            cc = part["campaigns"][c]
            for tn in ("T1", "T2"):
                x = cc["days"][tn]
                f[f"{lab}_{cn}_{tn}_hit"] = bool(x["hit"])
                if x["hit"]:
                    f[f"{lab}_{cn}_{tn}"] = f"{x['day']:.0f}"
            f[f"{lab}_{cn}_best"] = f"{cc['best_new']:.2f}"
            f[f"{lab}_{cn}_both"] = bool(cc["days"]["T1"]["hit"] and cc["days"]["T2"]["hit"])
            f[f"{lab}_{cn}_same_day"] = bool(f[f"{lab}_{cn}_both"] and
                                              abs(cc["days"]["T1"]["day"] - cc["days"]["T2"]["day"]) < 0.5)
    for k in ("flaime_al|T1", "flaime_al|T2", "onr_cu|T1", "onr_cu|T2"):
        c, tn = k.split("|")
        st = I["arm_stats"][f"auto|{c}|{tn}"]
        f[f"arm_{'al' if c == 'flaime_al' else 'cu'}_{tn}_hit"] = str(st["hit"])
    # money: does the automated lab's seed spend its money, and when is 90 % of it gone
    budget = sum(ra.budget[c] for c in D.CAMPAIGNS)
    f["has_limit"] = bool(0 < budget < 1e12)
    if f["has_limit"]:
        f["budget"] = D5._usd(budget)
    d90 = R5.d_spent("auto")
    f["money_spent"] = bool(d90 is not None)                # the automated lab's seed spends that share of its money
    f["pct_spent"] = f"{R5.PCT_SPENT * 100:.0f}"
    if d90 is not None:
        f["d90"] = f"{d90:.0f}"
    f["conv_money_spent"] = bool(R5.d_spent("conv") is not None)
    f["auto_spent"] = D5._usd(sum(ra.spent_at(c, ra.horizon_h) for c in D.CAMPAIGNS))
    f["conv_spent"] = D5._usd(sum(rc.spent_at(c, rc.horizon_h) for c in D.CAMPAIGNS))
    # the long flat at the end: from which day neither campaign's best new alloy moves again
    last = max([max(ra._improve[c]) if ra._improve[c] else 0.0 for c in D.CAMPAIGNS])
    f["last_improve"] = f"{last:.0f}"
    f["flat_days"] = f"{hz - last:.0f}"
    f["long_flat"] = bool(hz - last > 120.0)
    # which of the replay's lines hold for this seed (a line is spoken only when its `when` does)
    f["money_story"] = bool(f["money_spent"] and f["long_flat"] and d90 is not None and d90 >= last - 1.0
                            and not f["conv_money_spent"])
    f["al_story"] = bool(f["auto_al_both"] and not f["auto_al_same_day"] and f["conv_al_both"])
    f["cu_story"] = bool(f["auto_cu_same_day"] and not f["conv_cu_T1_hit"] and not f["conv_cu_T2_hit"])
    f["has_room"] = bool("room_day" in f)
    f["has_cell"] = bool("cell_day" in f)
    _S["facts"] = f
    return f


_PLACE = re.compile(r"\{(\w+)\}")
NUMBER_WORDS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                "thirteen", "fourteen", "fifteen", "sixteen", "twenty", "thirty", "hundred", "thousand", "million",
                "half", "twice", "third", "quarter", "double")
# phrases that hold a number word or a figure and are not data: the two campaigns and the two proposals are the
# benchmark's own, "3-D" is a name
WORDS_OK = ("one seed", "one lab", "one atomizer", "no one", "one by one", "one run", "the one", "one clock",
            "two alloy discovery campaigns", "the two proposals", "3-d")


def script() -> dict:
    return json.loads(SCRIPT.read_text())


def resolved() -> list:
    """This cut's own lines with their text filled from facts(): [dict(id, seg, at | mark, offset, text, src, used)].
    A line whose `when` fact is false is left out (and its `unless` the other way round)."""
    f = facts()
    out = []
    for ln in script()["lines"]:
        if ln.get("when") and not f.get(ln["when"]):
            continue
        if ln.get("unless") and f.get(ln["unless"]):
            continue
        used = _PLACE.findall(ln["text"])
        miss = [k for k in used if k not in f or isinstance(f[k], bool)]
        if miss:
            raise SystemExit(f"narration5.json line {ln['id']}: no fact for {miss}")
        out.append(dict(ln, template=ln["text"], text=_PLACE.sub(lambda m: str(f[m.group(1)]), ln["text"]), used=used))
    return out


def check_own() -> list:
    """Every figure in this cut's own lines comes from facts() (no digit is typed into a template), and no number
    word is typed in either, except in WORDS_OK. Returns the rows; raises SystemExit otherwise."""
    bad, rows = [], []
    for ln in resolved():
        low = _PLACE.sub(" ", ln["template"]).lower()
        for ok in WORDS_OK:
            low = low.replace(ok, " ")
        for fig in re.findall(r"\d+(?:\.\d+)?", low):
            bad.append(f"{ln['id']}: the figure {fig} is typed in")
        for w in NUMBER_WORDS:
            if re.search(rf"\b{w}\b", low):
                bad.append(f"{ln['id']}: the number word '{w}' is typed in")
        for k in ln["used"]:
            rows.append(dict(id=ln["id"], fact=k, says=str(facts()[k])))
    if bad:
        raise SystemExit("narration5.json:\n  " + "\n  ".join(bad))
    return rows


def own_marks() -> dict:
    return {f"replay.{k}": v for k, v in R5.marks().items()}


def speak_own() -> dict:
    """This cut's own lines spoken (Kokoro, through narration.py) into out/twin<R>/video/narration/; the resolved
    script beside them."""
    from . import narration as N
    NDIR.mkdir(parents=True, exist_ok=True)
    rs = resolved()
    (NDIR / "script.json").write_text(json.dumps(dict(
        about=f"twin/video/narration5.json with its facts filled in for round {ROUND} (cut5.resolved())",
        lines=[{k: v for k, v in ln.items() if k != "used"} for ln in rs]), indent=1, ensure_ascii=False) + "\n")
    sc = script()
    N.configure(script=NDIR / "script.json", ndir=NDIR, say=sc.get("say") or {}, ipa=sc.get("ipa") or {})
    return N.speak_all()


def own_lines(seg: str) -> list:
    """[dict(id, t (seconds into the segment), text, flac)] of this cut's own lines in segment `seg`."""
    mk = R5.marks() if seg == "replay" else {}
    out = []
    for ln in resolved():
        if ln["seg"] != seg:
            continue
        if ln.get("mark"):
            if ln["mark"] not in mk:
                print(f"  narration: {ln['id']}: no mark {ln['mark']}; left out", flush=True)
                continue
            t = mk[ln["mark"]] + float(ln.get("offset", 0.0))
        else:
            t = float(ln.get("at", 0.0))
        out.append(dict(id=ln["id"], t=round(max(0.0, t), 2), text=ln["text"], flac=NDIR / f"{ln['id']}.flac"))
    return sorted(out, key=lambda r: r["t"])


# ================================================================================================== the plan
def plan_record() -> dict:
    segs = segments()
    out, t, chapters = [], 0.0, []
    for s in segs:
        out.append(dict(name=s["name"], start_s=round(t, 2), seconds=round(s["dur"], 2), title=s["title"],
                        missing=s["missing"] or None))
        if s["name"] == "replay":
            for tt, ttl in R5.tl().marks():
                chapters.append((round(t + tt, 1), ttl))
        elif s["name"] != "title":
            chapters.append((round(t, 1), s["title"]))
        else:
            chapters.append((0.0, s["title"]))
        t += s["dur"]
    return dict(segments=out, total_s=round(t, 2), chapters=chapters)


GAP_MIN = 0.45
LINE_RMS_DB = -19.0
SR, OUT_SR = 24000, 48000


def placed_lines(rec: dict) -> list:
    """Every line of every segment at its time in the cut: [dict(id, seg, t, end, text, flac, warn)]. A line that
    would start before the one before it has ended is pushed later, and one that runs past its segment's end is
    reported."""
    import soundfile as sf
    seg0 = {s["name"]: (s["start_s"], s["start_s"] + s["seconds"]) for s in rec["segments"]}
    rows = []
    for s in segments():
        if s["missing"]:
            continue
        for ln in s["lines"]():
            rows.append(dict(id=ln["id"], seg=s["name"], t0=seg0[s["name"]][0] + float(ln["t"]), text=ln["text"],
                             flac=str(ln["flac"])))
    rows.sort(key=lambda r: r["t0"])
    free, out = 0.0, []
    for r in rows:
        p = Path(r["flac"])
        warn = []
        if not p.exists():
            out.append(dict(r, t=None, end=None, warn=["no audio: " + p.name]))
            continue
        n = sf.info(str(p))
        dur = n.frames / n.samplerate
        t = max(r["t0"], free + GAP_MIN)
        if t - r["t0"] > 0.3:
            warn.append(f"pushed {t - r['t0']:.1f} s later")
        end = t + dur
        if end > seg0[r["seg"]][1] + 0.05:
            warn.append(f"runs {end - seg0[r['seg']][1]:.1f} s past the end of {r['seg']}")
        free = end
        out.append(dict(id=r["id"], seg=r["seg"], t=round(t, 2), end=round(end, 2), text=r["text"], flac=r["flac"],
                        warn=warn))
    return out


def track(rec: dict, wav: Path, srt: Path | None = None) -> list:
    """One 48 kHz mono WAV of the cut's length with every line at its time, each levelled to LINE_RMS_DB."""
    import soundfile as sf
    from scipy.signal import resample_poly
    total = rec["total_s"]
    rows = placed_lines(rec)
    tr = np.zeros(int((total + 1.0) * OUT_SR), np.float32)
    ok = []
    for r in rows:
        if r["t"] is None:
            print(f"  narration: {r['id']}: {'; '.join(r['warn'])}; left out", flush=True)
            continue
        y, sr = sf.read(r["flac"], dtype="float32")
        if y.ndim > 1:
            y = y.mean(1)
        rms, peak = float(np.sqrt(np.mean(y ** 2))) + 1e-9, float(np.abs(y).max()) + 1e-9
        y = y * min(10 ** (LINE_RMS_DB / 20) / rms, 0.84 / peak)
        if sr != OUT_SR:
            g = math.gcd(OUT_SR, sr)
            y = resample_poly(y, OUT_SR // g, sr // g).astype(np.float32)
        i0 = int(round(r["t"] * OUT_SR))
        n = max(0, min(len(y), len(tr) - i0))
        tr[i0:i0 + n] += y[:n]
        ok.append(r)
        for w_ in r["warn"]:
            print(f"  narration: {r['id']}: {w_}", flush=True)
    tr = tr[:int(total * OUT_SR)]
    sf.write(str(wav), tr, OUT_SR, subtype="PCM_16")
    if srt is not None:
        from .narration import _stamp
        srt.write_text("".join(f"{i + 1}\n{_stamp(p['t'])} --> {_stamp(p['end'])}\n{p['text']}\n\n"
                               for i, p in enumerate(ok)))
    sp = sum(p["end"] - p["t"] for p in ok)
    print(f"narration: {len(ok)} lines, {sp / 60:.1f} min spoken of {total / 60:.1f}", flush=True)
    return rows


# ================================================================================================== the encode
FADE = 0.35


def render_piece(name: str, a: float, b: float, out: Path, preset: str) -> dict:
    seg = segment(name)
    fn, dur = seg["fn"], seg["dur"]
    enc = C.encoder(out, preset)
    n = int(round((b - a) * FPS))
    t0, c0 = time.time(), time.process_time()
    for k in range(n):
        tt = a + k / FPS
        fr = fn(tt)
        kf = min(1.0, tt / FADE, (dur - tt) / FADE)
        if kf < 1.0:
            fr = St.dim(np.array(fr, copy=True), max(0.0, kf))
        enc.stdin.write(np.ascontiguousarray(fr, np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    return dict(name=name, a=a, b=b, frames=n, wall=round(time.time() - t0, 1), cpu=round(time.process_time() - c0, 1))


def _pieces(rec: dict, only: list | None = None) -> list:
    out = []
    CH = 30.0
    for s in rec["segments"]:
        a, dur, k = 0.0, s["seconds"], 0
        while a < dur - 1e-6:
            b = min(dur, a + CH)
            if dur - b < 8.0:
                b = dur
            out.append((s["name"], a, b, TMP / f"{NAME}_{len(out):03d}_{s['name']}_{k}.mp4"))
            a, k = b, k + 1
    if only:
        return [p for p in out if p[0] in only], out
    return out, out


def _run_pieces(pieces: list, preset: str, workers: int) -> list:
    TMP.mkdir(parents=True, exist_ok=True)
    todo = sorted(pieces, key=lambda p: -(p[2] - p[1]) * (2.0 if p[0] in ("replay", "floorspace") else 1.0))
    running, logs = [], []
    while todo or running:
        while todo and len(running) < workers:
            name, a, b, out = todo.pop(0)
            p = subprocess.Popen([sys.executable, "-m", "twin.video.cut5", "piece", name, f"{a:.4f}", f"{b:.4f}",
                                  str(out), preset], cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True)
            running.append((p, name, a, b, out))
        time.sleep(0.5)
        for item in list(running):
            p = item[0]
            if p.poll() is not None:
                running.remove(item)
                txt = p.stdout.read()
                last = txt.strip().splitlines()[-1] if txt.strip() else ""
                logs.append(last)
                print(f"  {item[1]} {item[2]:.1f}-{item[3]:.1f}: rc {p.returncode} {last[:150]}", flush=True)
                if p.returncode != 0:
                    print(txt[-4000:], flush=True)
                    raise SystemExit(f"piece {item[1]} failed")
    return logs


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                          cwd=HERE).stdout.strip()


def build(only: list | None = None) -> dict:
    """The encode: every segment in pieces (or only the named ones again), the join, the narration, the record."""
    t_start = time.time()
    workers = int(os.environ.get("TWIN_VIDEO_WORKERS", "4"))
    preset = os.environ.get("TWIN_VIDEO_PRESET", "medium")
    miss = missing()
    if miss and os.environ.get("TWIN_VIDEO_ALLOW_MISSING") != "1":
        raise SystemExit("segments not built: " + "; ".join(f"{n} ({w})" for n, w in miss))
    rec = plan_record()
    todo, every = _pieces(rec, only)
    if not R5.have_tracks():
        raise SystemExit("the replay's 3-D track is not rendered: python -m twin.video.lab3d5 run")
    print(f"{NAME}: {len(todo)} of {len(every)} pieces, {workers} workers, preset {preset}", flush=True)
    _run_pieces(todo, preset, workers)
    silent = VID / f"{NAME}_silent.mp4"
    C.TMP.mkdir(parents=True, exist_ok=True)
    C.concat([p[3] for p in every], silent)
    wav = TMP / f"{NAME}.wav"
    rows = track(rec, wav, VID / f"{NAME}.srt")
    dst = VID / f"{NAME}.mp4"
    flt = C.loudnorm_filter(wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", flt, "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags",
                    "+faststart", str(dst)], check=True)
    silent.unlink(missing_ok=True)
    I = D5.info()
    rec.update(file=str(dst.relative_to(HERE)), seconds=C._duration(dst), round=ROUND, commit=commit(),
               replay=dict(run=I["auto"]["run_id"], conventional=I["conv"]["run_id"], seed=I["seed"],
                           n_seeds=I["n_seeds"], is_median_seed=I["is_median_seed"]),
               narration=dict(placed=[{k: v for k, v in r.items() if k != "flac"} for r in rows],
                              voice="Kokoro v1.0 af_heart (open weights), speed 0.96", srt=f"{NAME}.srt"),
               wall_s=round(time.time() - t_start, 1), preset=preset, workers=workers,
               built_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), missing=miss or None)
    (VID / f"{NAME}_record.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("file", "seconds", "commit", "wall_s")}), flush=True)
    return rec


# ================================================================================================== checks
def check() -> dict:
    """Every module's own check of the numbers it speaks and shows, then this cut's: its own lines' figures all come
    from facts(), the replay's counters end on the row's own, and the replayed seed is the one the round's notes
    name. Raises SystemExit on any failure."""
    out = {}
    rows = check_own()
    out["own"] = dict(lines=len(resolved()), figures=len(rows))
    for nm in ("auto", "conv"):
        bad = R5.R(nm).check_counters()
        if bad:
            raise SystemExit(f"the replay's counters ({nm}) don't end on the row's own: {bad}")
    I = D5.info()
    if not I["is_median_seed"] and not os.environ.get("TWIN_VIDEO_SEED"):
        raise SystemExit("the replayed seed is not the arm's median seed")
    out["replay"] = dict(seed=I["seed"], is_median_seed=I["is_median_seed"], counters="end on the rows' own")
    for mod in ("figs5_intro", "figs5_labs", "experiments", "floorspace_cut"):
        m, why = _mod(mod)
        if m is None or not hasattr(m, "check_numbers"):
            out[mod] = f"not checked: {why or 'no check_numbers()'}"
            continue
        r = m.check_numbers()
        out[mod] = dict(checked=len(r) if hasattr(r, "__len__") else True)
    (VID / f"{NAME}_check.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


# ================================================================================================== stills, sheet
def frame_at(t: float) -> np.ndarray:
    acc = 0.0
    for s in segments():
        if t < acc + s["dur"]:
            return s["fn"](t - acc)
        acc += s["dur"]
    s = segments()[-1]
    return s["fn"](s["dur"] - 0.05)


def stills(times: list):
    Path("/tmp/vid").mkdir(exist_ok=True)
    for t in times:
        c0 = time.process_time()
        fr = frame_at(float(t))
        Image.fromarray(np.ascontiguousarray(fr)).save(f"/tmp/vid/cut5_{float(t):06.1f}.png")
        print(f"{float(t):7.1f} s: {1000 * (time.process_time() - c0):.0f} ms cpu", flush=True)


def sheet_moments(rec: dict) -> list:
    """(time, label) of the contact sheet's frames: every segment, and the replay's stages."""
    seg0 = {s["name"]: (s["start_s"], s["seconds"]) for s in rec["segments"]}
    mk = R5.marks()
    out = []

    def at(name, frac, label):
        if name in seg0:
            out.append((seg0[name][0] + frac * seg0[name][1], label))
    at("title", 0.5, "title")
    at("simulated", 0.75, "the search spaces")
    at("changes", 0.8, "what changed")
    for fr_, lab in ((0.12, "composition"), (0.25, "Scheil"), (0.36, "AM module"), (0.46, "atomizing"),
                     (0.66, "SEM"), (0.78, "heat treatment, tensile"), (0.9, "corrosion")):
        at("experiments", fr_, f"experiments: {lab}")
    at("counters", 0.6, "counters")
    at("atomizer", 0.8, "atomizer: design targets")
    r0 = seg0["replay"][0]
    for key, lab in (("day.30", "replay: before the space"), ("room", "replay: the space is ready"),
                     ("cell", "replay: the cell"), ("hit.flaime_al.T2", "replay: aluminium's targets"),
                     ("hit.onr_cu.T1", "replay: copper's targets"), ("day.400", "replay: day 400"),
                     ("day.600", "replay: day 600")):
        if key in mk:
            out.append((r0 + mk[key] + 3.0, lab))
    for fr_, lab in ((0.2, "labs: like for like"), (0.5, "labs: where it doesn't win"), (0.9, "labs: spending")):
        at("labs", fr_, lab)
    for fr_, lab in ((0.15, "floor space: conventional"), (0.5, "floor space: vertical"), (0.85, "floor space: capacity")):
        at("floorspace", fr_, lab)
    at("takeaway", 0.7, "takeaway")
    at("notes", 0.6, "notes")
    return [(min(t, rec["total_s"] - 0.2), lab) for t, lab in out]


def sheet(video: Path, dst: Path, rec: dict, cols: int = 5):
    ms = sheet_moments(rec)
    tw, th = 384, 216
    rows = int(math.ceil(len(ms) / cols))
    im = Image.new("RGB", (cols * tw, rows * (th + 26)), (13, 16, 21))
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    for i, (t, lab) in enumerate(ms):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf",
                            f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
        if len(r.stdout) == tw * th * 3:
            fr = Image.frombytes("RGB", (tw, th), r.stdout)
            x, y = (i % cols) * tw, (i // cols) * (th + 26)
            im.paste(fr, (x, y))
            d.text((x + 6, y + th + 5), f"{int(t // 60)}:{int(t % 60):02d}  {lab}", font=St.font(14), fill=St.INK)
    im.save(dst)
    return dst


# ================================================================================================== the script
def write_script(rec: dict) -> Path:
    """The cut's narration in order, as spoken, each line at its time: out/twin<R>/video/twoyears_script.md. Where
    each line's template lives is listed at the top (the templates are what to edit; this file is written)."""
    from . import meta as M
    rows = [r for r in placed_lines(rec) if r["t"] is not None]
    titles = {s["name"]: s["title"] for s in rec["segments"]}
    src = {"title": "twin/video/narration5.json", "simulated": "twin/video/narration5.json",
           "replay": "twin/video/narration5.json", "changes": "twin/video/narration5_intro.json",
           "counters": "twin/video/narration5_intro.json", "atomizer": "twin/video/narration5_intro.json",
           "notes": "twin/video/narration5_intro.json", "labs": "twin/video/narration5_labs.json",
           "takeaway": "twin/video/narration5_labs.json", "experiments": "twin/video/narration_exp5.json",
           "floorspace": "twin/video/narration_floorspace.json"}
    out = [f"# The two-year cut's script, round {ROUND}", "",
           f"Every line as spoken in `{NAME}.mp4`, at its time ({len(rows)} lines). Written by "
           "`python -m twin.video.cut5 script` from the templates, filled from the round's tables; edit the templates, "
           "not this file. Templates by part:", ""]
    for seg in [s["name"] for s in rec["segments"]]:
        if seg in src:
            out.append(f"- {titles[seg]}: `{src[seg]}`")
    cur = None
    for r in rows:
        if r["seg"] != cur:
            cur = r["seg"]
            out += ["", f"## {M.stamp(next(s['start_s'] for s in rec['segments'] if s['name'] == cur))} "
                        f"{titles.get(cur, cur)}", ""]
        out.append(f"- **{M.stamp(r['t'])}** ({r['id']}) {r['text']}")
    dst = VID / f"{NAME}_script.md"
    dst.write_text("\n".join(out) + "\n")
    return dst


# ================================================================================================== metadata
def meta(rec: dict) -> dict:
    from . import meta5
    return meta5.write(rec)


# ================================================================================================== everything
def everything():
    t0 = time.time()
    VID.mkdir(parents=True, exist_ok=True)
    D5.prepare()
    print("check:", json.dumps(check()), flush=True)
    speak_own()
    from . import lab3d5
    lab3d5.run_jobs(R5.jobs(), int(os.environ.get("TWIN_VIDEO_WORKERS", "3")))
    rec = build()
    write_script(rec)
    meta(rec)
    sheet(VID / f"{NAME}.mp4", VID / f"{NAME}_sheet.png", rec)
    print(f"all: {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "plan"
    if cmd == "piece":
        print(json.dumps(render_piece(a[1], float(a[2]), float(a[3]), Path(a[4]), a[5])), flush=True)
    elif cmd == "plan":
        rec = plan_record()
        for s in rec["segments"]:
            print(f"{int(s['start_s'] // 60):3d}:{s['start_s'] % 60:04.1f}  {s['seconds']:6.1f} s  {s['name']:12s} "
                  f"{s['title']}" + (f"   !! MISSING: {s['missing'][:80]}" if s["missing"] else ""))
        print(f"total {rec['total_s'] / 60:.1f} min")
        for t, ttl in rec["chapters"]:
            print(f"   {int(t // 60)}:{int(t % 60):02d} {ttl}")
        for r in placed_lines(rec):
            if r["t"] is None:
                print(f"   --:--  {r['seg']:11s} {r['id']:8s} {r['text'][:80]}   !! {'; '.join(r['warn'])}")
            else:
                print(f"{int(r['t'] // 60):3d}:{r['t'] % 60:04.1f}-{int(r['end'] // 60)}:{r['end'] % 60:04.1f}  "
                      f"{r['seg']:11s} {r['id']:8s} {r['text'][:80]}" + (f"   !! {'; '.join(r['warn'])}" if r["warn"] else ""))
    elif cmd == "check":
        print(json.dumps(check(), indent=1))
    elif cmd == "facts":
        print(json.dumps(facts(), indent=1))
    elif cmd == "tts":
        au = speak_own()
        print(f"{len(au)} lines spoken into {NDIR}")
    elif cmd == "stills":
        stills(a[1:] or [5, 30])
    elif cmd == "build":
        build()
    elif cmd == "finish":
        rec = build(a[1:] or None)
        write_script(rec)
        meta(rec)
        sheet(VID / f"{NAME}.mp4", VID / f"{NAME}_sheet.png", rec)
    elif cmd == "meta":
        meta(json.loads((VID / f"{NAME}_record.json").read_text()))
    elif cmd == "script":
        p = VID / f"{NAME}_record.json"
        print(write_script(json.loads(p.read_text()) if p.exists() else plan_record()))
    elif cmd == "sheet":
        sheet(VID / f"{NAME}.mp4", VID / f"{NAME}_sheet.png", json.loads((VID / f"{NAME}_record.json").read_text()))
    elif cmd == "all":
        everything()
    else:
        raise SystemExit(__doc__)

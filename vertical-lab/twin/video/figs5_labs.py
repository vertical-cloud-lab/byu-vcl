"""The lab comparison and the takeaway of the two-year cut (TWIN_VIDEO_ROUND=5 and later), drawn with PIL frame by frame
like figs3b's cards.

    python -m twin.video.figs5_labs nums            # every spoken number and worded claim against the round's tables
    python -m twin.video.figs5_labs tts             # speak the lines whose text changed (Kokoro) -> narration_labs/
    python -m twin.video.figs5_labs plan            # each line's time in its segment
    python -m twin.video.figs5_labs stills [dir]    # one still per card state -> /tmp/d1 (or dir)
    python -m twin.video.figs5_labs check           # the lines heard back by faster-whisper -> narration_labs/check.json

The cut calls: SEGMENTS = [(name, duration, frame function, chapter title)]; captions(name) -> [(t0, t1, text)];
narration_lines(name) -> [dict(id, t, text, flac)]; check_numbers(), which raises on a mismatch.

`labs` has four parts, each a card that comes in when its first line starts:
  like    like for like, as the round's tables give it: target x policy (the same in both labs) x both ordering as
          they go / both stocked: the factor, its 95 % paired interval, the seeds that got there in each lab
  nowin   where the automated lab doesn't win
  win     where it does
  money   money as spending: each lab's cumulative campaign spend against the day (the arm the cut replays and the
          same policy and stock rule in the conventional lab: the median and the quartiles over the seeds, the
          replayed seed drawn on its own), then the cost per alloy with fixed costs and to each target with equipment
`takeaway` is one card of three blocks.

Every number is numbers5.numbers(): out/twin<R>/like<R>.json (what tables.md prints) and the rows' own spend traces.
Nothing is typed in: the lines' numbers are placeholders (narration5_labs.json), and every worded statement of a card
or a line is a claim that numbers5.claims_by_key() computes. check_numbers() fails on a digit outside a placeholder,
on a line whose claims fail with no alternative that fits, and on a card whose claims fail, so a later round that
changes an outcome stops the build instead of saying something false. The money card draws whatever the round's
spend traces are: with no money limit in the rows (round 6) it drops the budget line and the 90 % marks, and the
lines about the money running out give way to their alternatives.

Nothing here is timed by hand: layout() places each line after the one before from the recorded lengths, each card
part appears at its line, and a segment is as long as its lines.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import data as D
from . import figs_anim as F
from . import numbers5 as N5
from . import style as St
from .style import px

W, H = St.W, St.H
AL, CU = N5.AL, N5.CU
SCRIPT = Path(__file__).with_name("narration5_labs.json")
NDIR = D.VID / "narration_labs"                       # committed: each line's FLAC, lines.json, script.json, check.json
CAMP_WORD = {AL: "Aluminium", CU: "Copper"}
TN_WORD = {"T1": "the best existing alloy on this synthetic benchmark", "T2": "the halfway target"}
LEAD, GAP, PART_GAP, TAIL = 0.9, 0.6, 1.5, 2.4        # s: before a segment's first line, between lines, between
PART_IN = 0.9                                         # parts, after the last line; a part's card leads its line
TITLES = {"labs": "The lab comparison, like for like", "takeaway": "The takeaway"}
# the worded statements the cards themselves make (titles, tiles, captions): all must hold, or the build stops
CARD_CLAIMS = ["one_n", "al_T1_heur_tie", "al_T1_opt_not_clear", "al_T2_heur_half", "al_T2_heur_no_lead",
               "al_T2_opt_sooner", "al_T2_opt_intervals", "cu_funnel_sooner", "cu_opt_at_least", "cu_opt_fewer_seeds",
               "cu_wins", "cu_best_higher", "cu_inhouse_most", "opt_later_T1", "policy_over_lab", "rev_keeps_up",
               "usd_no_lower", "usd_cu_more", "per_alloy_dearer", "per_alloy_campaign_cheaper", "fixed_higher",
               "to_target_dearer", "al_T1_partner_most", "stock_decides_al_T1", "replay_median_seed"]


def _n() -> dict:
    return N5.numbers()


# =============================================================================================== the lines
_PH = re.compile(r"\{([^{}]+)\}")
_CACHE: dict = {}


def _get(path: str, n: dict):
    """A dotted path in numbers5.numbers(); a key may itself hold dots or bars: the longest match wins."""
    cur, rest = n, path
    while rest:
        if not isinstance(cur, dict):
            raise KeyError(path)
        key = next((k for k in sorted(cur, key=len, reverse=True) if rest == k or rest.startswith(k + ".")), None)
        if key is None:
            raise KeyError(f"{path}: no key at '{rest}'")
        cur, rest = cur[key], rest[len(key) + 1:]
    return cur


def _value(expr: str, n: dict):
    m = re.match(r"^(.*?)([*/])(\d+(?:\.\d+)?)$", expr)
    if m:
        v = float(_get(m.group(1), n))
        return v * float(m.group(3)) if m.group(2) == "*" else v / float(m.group(3))
    return _get(expr, n)


def _fill(ph: str, n: dict) -> tuple:
    """One placeholder -> (the words, [(what it shows, its path, the value)])."""
    body, _, fmt = ph.partition(":")
    expr, _, kind = body.partition("~")
    if kind in ("span", "span0"):
        s = _get(expr, n)
        f = fmt or (".0f" if kind == "span0" else ".1f")
        a, b = format(float(s["lo"]), f), format(float(s["hi"]), f)
        return (a if a == b else f"{a} to {b}"), [(a, expr + ".lo", float(s["lo"])), (b, expr + ".hi", float(s["hi"]))]
    v = _value(expr, n)
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        raise ValueError(f"{expr} is {v}")
    shown = f"{int(round(float(v))):d}" if fmt == "d" else format(float(v), fmt or ".1f")
    return shown, [(shown, expr, float(v))]


def render(text: str, n: dict | None = None) -> tuple:
    """A line's template with its numbers filled in -> (the text, [(shown, path, value)])."""
    n = n or _n()
    used: list = []

    def sub(m):
        words, rows = _fill(m.group(1), n)
        used.extend(rows)
        return words
    return _PH.sub(sub, text), used


def script() -> dict:
    return json.loads(SCRIPT.read_text())


def lines(seg: str | None = None) -> list:
    """The lines as they are to be said, in order: each with the text its claims allow (`variant`: 0 the line's own,
    k its k-th alternative, None when its claims fail and no alternative fits), rendered, with its numbers."""
    key = ("lines", D.ROUND)
    if key not in _CACHE:
        cl = {k: ok for k, (_, ok) in N5.claims_by_key().items()}
        out = []
        for ln in script()["lines"]:
            cand = [dict(text=ln["text"], claims=ln.get("claims", []), unless=[])] + list(ln.get("alt", []))
            pick = None
            for i, c in enumerate(cand):
                if all(cl.get(k, False) for k in c.get("claims", [])) and \
                        all(not cl.get(k, False) for k in c.get("unless", [])):
                    pick = i
                    break
            c = cand[pick if pick is not None else 0]
            try:
                text, nums = render(c["text"])
                err = None
            except Exception as e:                      # noqa: BLE001
                text, nums, err = c["text"], [], f"{type(e).__name__}: {e}"
            out.append(dict(id=ln["id"], seg=ln["seg"], part=ln.get("part"), gap=float(ln.get("gap", GAP)),
                            text=text, template=c["text"], nums=nums, variant=pick, src=ln.get("src", ""),
                            claims=c.get("claims", []), failing=[k for k in c.get("claims", []) if not cl.get(k)],
                            error=err))
        _CACHE[key] = out
    return [ln for ln in _CACHE[key] if seg is None or ln["seg"] == seg]


def _seconds() -> dict:
    p = NDIR / "lines.json"
    if "sec" not in _CACHE:
        rec = json.loads(p.read_text()) if p.exists() else {"lines": {}}
        _CACHE["sec"] = {k: (v["seconds"], v["text"]) for k, v in rec.get("lines", {}).items()}
    return _CACHE["sec"]


def layout(seg: str) -> dict:
    """Where each line of a segment starts, from the recorded lengths (a line not yet recorded, or recorded with
    another text, is estimated from its words): {"lines": [...with t, end], "parts": {part: t0}, "duration": s}."""
    key = ("layout", seg)
    if key in _CACHE:
        return _CACHE[key]
    sec = _seconds()
    t, parts, rows = 0.0, {}, []
    for i, ln in enumerate(lines(seg)):
        have = sec.get(ln["id"])
        dur = have[0] if have and have[1] == ln["text"] else 0.5 + 0.40 * len(ln["text"].split())
        if ln["part"]:
            start = (t + PART_GAP) if i else LEAD
            parts[ln["part"]] = max(0.0, start - PART_IN)
            t = start
        else:
            t = t + ln["gap"]
        rows.append(dict(ln, t=round(t, 2), end=round(t + dur, 2), seconds=round(dur, 2),
                         recorded=bool(have and have[1] == ln["text"])))
        t = t + dur
    out = dict(lines=rows, parts=parts, duration=round(t + TAIL, 1))
    _CACHE[key] = out
    return out


def cue(line_id: str, seg: str) -> float:
    for r in layout(seg)["lines"]:
        if r["id"] == line_id:
            return r["t"]
    return 1e9                                           # a line the script no longer has: its part never comes in


def narration_lines(name: str) -> list:
    """What the cut mixes in: each line of segment `name` with its start (s into the segment), text and FLAC."""
    return [dict(id=r["id"], t=r["t"], end=r["end"], text=r["text"], flac=NDIR / f"{r['id']}.flac", src=r["src"])
            for r in layout(name)["lines"]]


def check_numbers(verbose: bool = True) -> list:
    """Every figure a line speaks is a placeholder read from numbers5.numbers() (so it is the tables' at this commit);
    no digit is typed into a line; every line's claims hold (or an alternative's do); every card's claims hold.
    Returns the rows; raises SystemExit on any failure."""
    cl = N5.claims_by_key()
    rows, bad = [], []
    for ln in lines():
        raw = _PH.sub("", ln["template"])
        typed = re.findall(r"\d+(?:\.\d+)?", raw)
        for shown, path, v in ln["nums"]:
            ok = shown in ln["text"] and math.isfinite(v)
            rows.append(dict(id=ln["id"], says=shown, path=path, value=v, ok=ok))
            if not ok:
                bad.append(f"{ln['id']}: {shown} <- {path} = {v}")
        if typed:
            bad.append(f"{ln['id']}: figures typed into the text, not read from the numbers: {typed}")
        if ln["error"]:
            bad.append(f"{ln['id']}: {ln['error']}")
        if ln["variant"] is None:
            bad.append(f"{ln['id']}: says what this round's numbers don't show ("
                       + "; ".join(cl[k][0] if k in cl else f"unknown claim {k}" for k in ln["failing"])
                       + ") and no alternative fits: reword it in narration5_labs.json")
    for k in CARD_CLAIMS:
        if k not in cl or not cl[k][1]:
            bad.append(f"a card says what this round's numbers don't show: [{k}] {cl.get(k, ('?',))[0]}: rework "
                       "figs5_labs.py")
    if verbose:
        for r in rows:
            print(f"{'ok ' if r['ok'] else 'BAD'} {r['id']:6s} says {r['says']:>6s} <- {r['path']} = {r['value']:.4f}")
        for k, (c, ok) in cl.items():
            print(f"{'ok ' if ok else 'no '} claim [{k}] {c}")
        for ln in lines():
            if ln["variant"]:
                print(f"note: {ln['id']} is said in its alternative {ln['variant']}")
    if bad:
        raise SystemExit("figs5_labs: " + "\n  ".join([f"{len(bad)} problems:"] + bad))
    if verbose:
        print(f"{len(rows)} spoken numbers and {len(cl)} claims ({len(CARD_CLAIMS)} of them the cards'), all as "
              f"out/twin{D.ROUND}'s tables have them")
    return rows


def speak(only: set | None = None) -> dict:
    """The lines as they resolve now, spoken by Kokoro where their text changed (narration.speak_all on a resolved
    copy of the script, narration_labs/script.json). Run in a process of its own: it points narration.py at this
    chapter's script and audio."""
    from . import narration as NA
    NDIR.mkdir(parents=True, exist_ok=True)
    sc = script()
    res = dict(about="narration5_labs.json with its numbers filled in from numbers5.numbers(): what was spoken",
               lines=[dict(id=ln["id"], text=ln["text"]) for ln in lines()])
    (NDIR / "script.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    NA.configure(script=NDIR / "script.json", ndir=NDIR, say=sc.get("say") or {}, ipa=sc.get("ipa") or {})
    au = NA.speak_all(only)
    _CACHE.clear()
    return au


def check_audio(models=("small.en",)) -> list:
    from . import narration as NA
    sc = script()
    NA.configure(script=NDIR / "script.json", ndir=NDIR, say=sc.get("say") or {}, ipa=sc.get("ipa") or {})
    return NA.check(models)


# ============================================================================================ drawing helpers
def _new() -> tuple:
    im = Image.new("RGB", (W, H), St.BG)
    return im, ImageDraw.Draw(im)


def _para(d, x, y, text, f, fill, width, lh, anchor="la", max_lines=None) -> float:
    ls = St.wrap(text, f, width)
    if max_lines:
        ls = ls[:max_lines]
    for i, ln in enumerate(ls):
        d.text((x, y + i * lh), ln, font=f, fill=fill, anchor=anchor)
    return y + len(ls) * lh


def _parts(d, im, t, T, fns, total):
    """Each part's card, cross-faded at the part boundaries."""
    for i, fn in enumerate(fns):
        a, b = T[i], T[i + 1]
        k = min(St.ramp(t, a, a + 0.6) if a > 0 else 1.0, 1.0 - St.ramp(t, b - 0.5, b) if b < total else 1.0)
        if k <= 0.003:
            continue
        if k >= 0.997:
            fn(d, im, t)
        else:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fn(ImageDraw.Draw(lay), lay, t)
            F._over(im, lay, k)


def _tile(d, box, k, bg=St.BG):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0, x1, y1), radius=px(16), fill=St.mix(bg, St.SURF, k),
                        outline=St.mix(bg, St.RULE, k), width=px(1))
    return St.mix(bg, St.SURF, k)


def _usd(v) -> str:
    """$24.7k, $1.18M, $121k: as notes/twin_round5.md writes them."""
    v = float(v)
    if v >= 1e6:
        return f"${v / 1e6:.2f}M"
    if v >= 109950:
        return f"${v / 1e3:.0f}k"
    return f"${v / 1e3:.1f}k"


def _seeds(c: dict) -> str:
    return f"{c['hit_new']}/{c['n']} vs {c['hit_ref']}/{c['n']}"


def _sp(s: dict, fmt=".1f", unit="×") -> str:
    a, b = format(s["lo"], fmt), format(s["hi"], fmt)
    return f"{a}{unit}" if a == b else f"{a}{unit} to {b}{unit}"


def _isp(s: dict) -> str:
    return f"{s['lo']}" if s["lo"] == s["hi"] else f"{s['lo']} to {s['hi']}"


# ================================================================================================ the labs card
def labs_T() -> tuple:
    L = layout("labs")
    order = [p for p in ("like", "nowin", "win", "money") if p in L["parts"]]
    return tuple(L["parts"][p] for p in order) + (L["duration"],), order


def _part_t(part: str) -> float:
    return layout("labs")["parts"].get(part, 1e9)


def labs_caps() -> list:
    n = _n()
    T, order = labs_T()
    ns = n["labs"]["n_seeds"]
    M = n["money"]
    words = {
        "like": f"Like for like: the same policy and the same stock rule in both labs. {ns} simulated two-year runs "
                "per arm, the same seeds in both labs, from the day the money arrives.",
        "nowin": "Where the automated lab doesn't win, like for like: the same policy and the same stock rule in "
                 "both labs unless a tile says otherwise. Simulated.",
        "win": "Where the automated lab does win, like for like. Simulated.",
        "money": ("Money as spending: each campaign's cumulative simulated spend against the day, BOFN in both labs, "
                  "both stocked. " + ("Both labs have two years' money from day 0." if M["budget"][AL] else
                                      "Neither lab has a money limit.")),
    }
    return [(T[i], T[i + 1], words[p]) for i, p in enumerate(order)]


def labs_frame(t: float, captions: bool = True) -> np.ndarray:
    im, d = _new()
    T, order = labs_T()
    if captions:
        F._header(d, TITLES["labs"], labs_caps(), t, total=T[-1])
    else:
        d.text((px(80), px(44)), TITLES["labs"], font=St.font(44, bold=True), fill=St.INK)
    fns = dict(like=_p_like, nowin=_p_nowin, win=_p_win, money=_p_money)
    _parts(d, im, t, T, [fns[p] for p in order], T[-1])
    return np.asarray(im)


# ------------------------------------------------------------------------------------------- part 1: like for like
FX = (0.5, 4.0)                                       # the factor axis (log): half as soon .. four times sooner


def _fx(x0, x1, v):
    lo, hi = math.log(FX[0]), math.log(FX[1])
    u = (math.log(min(max(v, FX[0] / 1.2), FX[1] * 1.2)) - lo) / (hi - lo)
    return x0 + (x1 - x0) * min(1.0, max(0.0, u))


def _arrow(d, xa, xb, y, col, w):
    """A line from xa to xb with a head at xb."""
    s = 1 if xb >= xa else -1
    h = px(9)
    d.line([(xa, y), (xb - s * h, y)], fill=col, width=w)
    d.polygon([(xb, y), (xb - s * h, y - h * 0.62), (xb - s * h, y + h * 0.62)], fill=col)


def _forest(d, x0, x1, y, c, col, filled, k, bg):
    """One cell on the factor axis: its estimate and 95 % interval; a bound as a bar with an arrow away from it."""
    cc = St.mix(bg, col, k)
    w = px(3)
    r = px(7)
    if c is None or c["kind"] == "none":
        return
    if c["kind"] in ("at_least", "at_most"):
        xb = _fx(x0, x1, c["af"])
        d.line([(xb, y - px(9)), (xb, y + px(9))], fill=cc, width=px(4))
        _arrow(d, xb, x1 if c["kind"] == "at_least" else x0, y, cc, w)
        return
    lo, hi = c["lo"], c["hi"]
    open_lo, open_hi = (lo is None or lo < FX[0]), (hi is None or not math.isfinite(hi) or hi > FX[1])
    xa = x0 if open_lo else _fx(x0, x1, lo)
    xb = x1 if open_hi else _fx(x0, x1, hi)
    if open_lo and open_hi:                              # the interval tells nothing: 0 to unbounded
        St.dashed_line(d, [(x0, y), (x1, y)], St.mix(bg, St.INK3, k), width=px(2), dash=px(6), gap=px(5))
    else:
        if open_hi:
            _arrow(d, xa, x1, y, cc, w)
        elif open_lo:
            _arrow(d, xb, x0, y, cc, w)
        else:
            d.line([(xa, y), (xb, y)], fill=cc, width=w)
        for xe, op in ((xa, open_lo), (xb, open_hi)):
            if not op:
                d.line([(xe, y - px(6)), (xe, y + px(6))], fill=cc, width=px(2))
    xm = _fx(x0, x1, c["af"])
    if filled:
        d.ellipse((xm - r, y - r, xm + r, y + r), fill=cc, outline=bg, width=px(1))
    else:
        d.ellipse((xm - r, y - r, xm + r, y + r), fill=bg, outline=cc, width=px(3))


def _cell_text(d, x, xr, y, c, k, bg):
    """The factor, its interval and the seeds there, as tables.md gives them."""
    ink, ink2 = St.mix(bg, St.INK, k), St.mix(bg, St.INK2, k)
    fb, fs = St.font(23, bold=True), St.font(16)
    if c is None:
        d.text((x, y), "not enough seeds", font=fs, fill=ink2, anchor="lm")
        return
    xx = x
    if c["kind"] in ("at_least", "at_most"):
        w_ = "at least" if c["kind"] == "at_least" else "at most"
        d.text((xx, y + px(1)), w_, font=fs, fill=ink, anchor="lm")
        xx += St.text_w(fs, w_) + px(7)
        d.text((xx, y), N5.x1(c["af"]), font=fb, fill=ink, anchor="lm")
    elif c["kind"] == "none":
        d.text((xx, y), "no factor", font=fs, fill=ink2, anchor="lm")
    else:
        vague = c["lo"] == 0 and not math.isfinite(c["hi"])
        d.text((xx, y), N5.x1(c["af"]), font=fb, fill=ink2 if vague else ink, anchor="lm")
        xx += St.text_w(fb, N5.x1(c["af"])) + px(10)
        d.text((xx, y + px(1)), N5.rng(c), font=fs, fill=ink2, anchor="lm")
    d.text((xr, y + px(1)), _seeds(c), font=St.font(17), fill=ink, anchor="rm")


def _p_like(d, lay, t):
    n = _n()
    Dd, names, T = n["labs"]["days"], n["labs"]["names"], n["labs"]["targets"]
    t0 = labs_T()[0][0]
    cues = {(AL, "T1"): cue("lab2", "labs") - 0.4, (AL, "T2"): cue("lab3", "labs") - 0.4,
            (CU, "T1"): cue("lab4", "labs") - 0.4, (CU, "T2"): cue("lab4", "labs") + 0.6}
    y_top, ph = px(196), px(724)
    for i, camp in enumerate((AL, CU)):
        x0 = px(80) + i * px(900)
        x1 = x0 + px(860)
        kp = St.ramp(t, t0 + 0.2 + 0.3 * i, t0 + 0.9 + 0.3 * i)
        if kp <= 0:
            continue
        surf = _tile(d, (x0, y_top, x1, y_top + ph), kp)
        ink, ink2 = St.mix(St.BG, St.INK, kp), St.mix(St.BG, St.INK2, kp)
        F.swatch(d, x0 + px(24), y_top + px(20), St.mix(St.BG, St.CAMP[camp], kp), s=20)
        d.text((x0 + px(56), y_top + px(12)), CAMP_WORD[camp], font=St.font(28, bold=True), fill=ink)
        ax0, ax1 = x0 + px(176), x0 + px(416)
        tx, txr = x0 + px(436), x1 - px(22)
        d.text((txr, y_top + px(22)), "seeds there: automated vs conventional", font=St.font(15), fill=ink2,
               anchor="ra")
        # the factor axis, once a panel
        ya = y_top + px(78)
        for v in (0.5, 1.0, 2.0, 4.0):
            xv = _fx(ax0, ax1, v)
            d.text((xv, ya), f"{v:g}×", font=St.font(15, bold=(v == 1.0)), fill=ink if v == 1.0 else ink2, anchor="md")
        d.text((tx, ya), "factor, 95 % interval", font=St.font(15), fill=ink2, anchor="ld")
        yb = y_top + px(92)
        for j, tn in enumerate(("T1", "T2")):
            kb = St.ramp(t, cues[(camp, tn)], cues[(camp, tn)] + 0.8) * kp
            yy = yb + j * px(312)
            hi_, h2 = St.mix(surf, St.INK, max(kb, 0.45 * kp)), St.mix(surf, St.INK2, max(kb, 0.45 * kp))
            d.line([(x0 + px(22), yy), (x1 - px(22), yy)], fill=St.mix(St.BG, St.RULE, kp), width=px(1))
            head = "To " + TN_WORD[tn]
            d.text((x0 + px(24), yy + px(10)), head, font=St.font(19, bold=True), fill=hi_)
            d.text((x0 + px(24) + St.text_w(St.font(19, bold=True), head) + px(10), yy + px(13)),
                   f"({T[tn][camp]:.2f})", font=St.font(16), fill=h2)
            y_r0 = yy + px(44)
            x1v = _fx(ax0, ax1, 1.0)
            d.line([(x1v, y_r0 - px(2)), (x1v, y_r0 + 3 * px(88) - px(14))], fill=St.mix(surf, St.RULE, kp),
                   width=px(2))
            for r, pol in enumerate(N5.POLS):
                yr = y_r0 + r * px(88)
                kr = St.ramp(t, cues[(camp, tn)] + 0.25 * r, cues[(camp, tn)] + 0.8 + 0.25 * r) * kp
                kl = max(kr, 0.45 * kp)                      # the rows' names from the start, their values at the cue
                d.text((x0 + px(24), yr + px(20)), names[pol][camp], font=St.font(20, bold=True),
                       fill=St.mix(surf, St.INK, kl), anchor="lm")
                d.text((x0 + px(24), yr + px(48)), "in both labs", font=St.font(14), fill=St.mix(surf, St.INK2, kl),
                       anchor="lm")
                if kr <= 0:
                    continue
                for q, pair in enumerate(("lean", "stocked")):
                    c = Dd[camp][tn][pol][pair]
                    yl = yr + px(20) + q * px(38)
                    _forest(d, ax0, ax1, yl, c, St.CAMP[camp], pair == "stocked", kr, surf)
                    _cell_text(d, tx, txr, yl, c, kr, surf)
    # how to read it
    kf = St.ramp(t, t0 + 1.2, t0 + 2.0)
    ink2 = St.mix(St.BG, St.INK2, kf)
    yl = y_top + ph + px(28)
    x = px(80)
    for filled, words in ((False, "both labs ordering metal as they go"), (True, "both labs stocked")):
        r = px(7)
        cc = St.mix(St.BG, St.INK, kf)
        if filled:
            d.ellipse((x, yl - r, x + 2 * r, yl + r), fill=cc)
        else:
            d.ellipse((x, yl - r, x + 2 * r, yl + r), fill=St.BG, outline=cc, width=px(3))
        d.text((x + px(24), yl), words, font=St.font(17), fill=ink2, anchor="lm")
        x += px(24) + St.text_w(St.font(17), words) + px(34)
    d.line([(x, yl), (x + px(44), yl)], fill=St.mix(St.BG, St.INK, kf), width=px(3))
    d.text((x + px(54), yl), "95 % interval, paired over the seeds", font=St.font(17), fill=ink2, anchor="lm")
    x += px(54) + St.text_w(St.font(17), "95 % interval, paired over the seeds") + px(34)
    d.line([(x, yl - px(9)), (x, yl + px(9))], fill=St.mix(St.BG, St.INK, kf), width=px(4))
    _arrow(d, x, x + px(44), yl, St.mix(St.BG, St.INK, kf), px(3))
    d.text((x + px(54), yl), "at least: fewer than half the conventional lab's seeds got there", font=St.font(17),
           fill=ink2, anchor="lm")
    _para(d, px(80), yl + px(24), "Factor: the conventional lab's median day to the target over the automated lab's "
          "(Kaplan-Meier medians over the seeds; a seed that never gets there is censored at the end of its two "
          "years). Right of 1×, the automated lab is sooner; an interval that crosses 1× is not clear of a tie. "
          "The policies: a metallurgist's heuristic (aluminium) and a tiered screening funnel (copper), then BOFN and "
          "pKGFN on both.", St.font(17), ink2, px(1760), px(25))


# -------------------------------------------------------------------------------- part 2: where it doesn't win
def _p_nowin(d, lay, t):
    n = _n()
    S, Dd, A, NW, E = n["labs"]["sum"], n["labs"]["days"], n["labs"]["arms"], n["nowin"], n["econ"]
    U = n["labs"]["usd"]
    ns = n["labs"]["n_seeds"]
    c1, c2, c3, c4 = (cue(k, "labs") for k in ("nw1", "nw2", "nw3", "nw4"))
    c0 = _part_t("nowin") + 0.45                         # the first tile comes in with the card, ahead of its line
    tw, th, gx, gy = px(573), px(412), px(20), px(20)
    X0, Y0 = px(80), px(196)

    def tile(i, t_in, camp, head):
        col, row = i % 3, i // 3
        x0, y0 = X0 + col * (tw + gx), Y0 + row * (th + gy)
        k = St.ramp(t, t_in - 0.4, t_in + 0.4)
        surf = _tile(d, (x0, y0, x0 + tw, y0 + th), k)
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        F.swatch(d, x0 + px(22), y0 + px(24), St.mix(St.BG, St.CAMP[camp] if camp else St.INK2, k), s=18)
        yy = _para(d, x0 + px(52), y0 + px(16), head, St.font(22, bold=True), ink, tw - px(74), px(29), max_lines=2)
        return x0 + px(22), max(yy + px(10), y0 + px(86)), tw - px(44), ink, ink2, k

    # 1: aluminium's first target is a tie
    h, o = S["al_T1_heur"], S["al_T1_opt"]
    x, y, w, ink, ink2, k = tile(0, c0, AL, "Aluminium's best existing alloy: a tie")
    d.text((x, y), " and ".join(N5.x1(Dd[AL]["T1"]["fast"][q]["af"]) for q in ("lean", "stocked")),
           font=St.font(44, bold=True), fill=ink)
    y += px(58)
    y = _para(d, x, y, "with the heuristic in both labs (ordering as they go, then stocked); intervals "
              + " and ".join(N5.rng(Dd[AL]["T1"]["fast"][q]) for q in ("lean", "stocked")), St.font(17), ink2, w,
              px(24))
    y = _para(d, x, y + px(8), f"With BOFN or pKGFN in both labs: {_sp(o['af'])}, and all {o['cells']} intervals "
              f"include 1 (from {_sp(o['ci_lo'], '.2f', '')} up to {_sp(o['ci_hi'], '.2f', '')}).", St.font(18), ink,
              w, px(25))
    pa, pc = NW["partner_al_T1"]["auto_stocked"], NW["partner_al_T1"]["conv_stocked"]
    _para(d, x, y + px(8), f"Heuristic, both stocked: in {pa['partner']} of {pa['of']} seeds the automated lab's "
          f"first alloy past the target was printed at a partner ({pc['partner']} of {pc['of']} in the conventional "
          f"lab). Its own printer is online around day {NW['online']['midi']:.0f} (median).",
          St.font(17), ink2, w, px(24))
    # 2: the halfway target with the heuristic
    hh = S["al_T2_heur"]
    x, y, w, ink, ink2, k = tile(1, c1 + 3.2, AL, "Aluminium's halfway target with the heuristic: no lead")
    for q, words in (("lean", "ordering as they go"), ("stocked", "both stocked")):
        c = hh[q]
        d.text((x, y), f"{c['hit_new']} vs {c['hit_ref']}", font=St.font(40, bold=True), fill=ink)
        xx = x + St.text_w(St.font(40, bold=True), f"{c['hit_new']} vs {c['hit_ref']}") + px(14)
        d.text((xx, y + px(6)), f"of {c['n']} seeds there, automated vs", font=St.font(17), fill=ink2)
        d.text((xx, y + px(30)), f"conventional, {words}", font=St.font(17), fill=ink2)
        y += px(66)
    _para(d, x, y + px(6), "About half the seeds get there in either lab. With both stocked the conventional lab gets "
          f"there in at least as many, so the factor is a bound below 1 ({N5.big(hh['stocked'])}). With BOFN or "
          f"pKGFN, {_isp(NW['policy']['al_T2_hits_opt'])} of {ns} seeds get there in either lab.", St.font(17), ink2,
          w, px(24))
    # 3: the optimizers reach the first target later
    P = NW["policy"]
    x, y, w, ink, ink2, k = tile(2, c2, AL, "The optimizers reach aluminium's first target later")
    dv = lambda lab, pol, st: A[f"{lab}|{pol}|{st}"][AL]["T1"]["day"]
    d.text((x, y), f"day {dv('vertical', 'bofn3', 'reorder'):.0f}", font=St.font(44, bold=True), fill=ink)
    xx = x + St.text_w(St.font(44, bold=True), f"day {dv('vertical', 'bofn3', 'reorder'):.0f}") + px(14)
    d.text((xx, y + px(8)), "BOFN, against", font=St.font(17), fill=ink2)
    d.text((xx, y + px(31)), f"day {dv('vertical', 'fast', 'reorder'):.0f} with the heuristic", font=St.font(17),
           fill=ink)
    y += px(64)
    y = _para(d, x, y, "median day to the best existing alloy, the stocked automated lab; pKGFN: day "
              f"{dv('vertical', 'pkgfn3', 'reorder'):.0f}", St.font(17), ink2, w, px(24))
    y = _para(d, x, y + px(8), f"Over both stock rules: day {_sp(P['auto_opt'], '.0f', '')} with an optimizer against "
              f"day {_sp(P['auto_heur'], '.0f', '')} in the automated lab; day {_sp(P['conv_opt'], '.0f', '')} "
              f"against day {_sp(P['conv_heur'], '.0f', '')} in the conventional lab.", St.font(17), ink2, w, px(24))
    _para(d, x, y + px(8), "But they are the policies that reach the halfway target: "
          f"{_isp(P['al_T2_hits_opt'])} of {ns} seeds in either lab, against {_isp(P['al_T2_hits_heur'])} with the "
          "heuristic.", St.font(18), ink, w, px(25))
    # 4: a stocked conventional lab keeps up with a lean automated lab
    R = NW["rev"]
    x, y, w, ink, ink2, k = tile(3, c3, AL, "A stocked conventional lab keeps up")
    d.text((x, y), _sp(R["al_T1"]), font=St.font(44, bold=True), fill=ink)
    y += px(58)
    y = _para(d, x, y, "against an automated lab ordering its metal as it goes, to aluminium's best existing alloy: "
              "below 1×, the conventional lab is sooner", St.font(17), ink2, w, px(24))
    for pol in N5.POLS:
        c = R["cells"][pol]
        d.text((x, y + px(10)), n["labs"]["names"][pol][AL], font=St.font(17, bold=True), fill=ink)
        d.text((x + px(112), y + px(10)), f"{N5.x1(c['af'])} ({N5.rng(c)})", font=St.font(17), fill=ink)
        d.text((x + w, y + px(11)), f"conventional first in {c['first_ref']} of {c['n']}", font=St.font(15),
               fill=ink2, anchor="ra")
        y += px(29)
    _para(d, x, y + px(16), "The other way round (the automated lab stocked, the conventional lab ordering as it "
          f"goes): {_sp(R['round3'])}. On this target the stock decides which lab is sooner.", St.font(17), ink2, w,
          px(24))
    # 5: campaign money to a target
    UU = NW["usd"]
    x, y, w, ink, ink2, k = tile(4, c4, None, "Campaign money to a target: no lower")
    d.text((x, y), _sp(UU["al_stocked"]), font=St.font(44, bold=True), fill=ink)
    y += px(58)
    y = _para(d, x, y, "the conventional lab's spend to aluminium's targets over the automated lab's, both stocked: "
              "every interval includes 1", St.font(17), ink2, w, px(24))
    y = _para(d, x, y + px(8), f"Both ordering as they go, with an optimizer: {_sp(UU['al_lean_opt'])}: the "
              "automated lab spent more.", St.font(18), ink, w, px(25))
    _para(d, x, y + px(8), f"Copper, the funnel: {_sp(UU['cu_funnel'])}. Fixed costs and equipment are left out of "
          "this basis.", St.font(17), ink2, w, px(24))
    # 6: per alloy, with fixed costs
    ea = E["arms"]
    x, y, w, ink, ink2, k = tile(5, c4 + 4.0, None, "Per new alloy tested, with fixed costs: dearer")
    a_, c_ = ea["vertical|bofn3|reorder"][AL]["per_alloy"], ea["conventional|bofn3|reorder"][AL]["per_alloy"]
    d.text((x, y), _usd(a_), font=St.font(44, bold=True), fill=ink)
    xx = x + St.text_w(St.font(44, bold=True), _usd(a_)) + px(14)
    d.text((xx, y + px(8)), f"against {_usd(c_)}", font=St.font(22, bold=True), fill=ink)
    d.text((xx, y + px(36)), "per aluminium alloy, BOFN, stocked", font=St.font(15), fill=ink2)
    y += px(66)
    fy = E["fixed_year"]
    y = _para(d, x, y, f"Heuristic: {_usd(ea['vertical|fast|reorder'][AL]['per_alloy'])} against "
              f"{_usd(ea['conventional|fast|reorder'][AL]['per_alloy'])}. Copper with BOFN: "
              f"{_usd(ea['vertical|bofn3|reorder'][CU]['per_alloy'])} against "
              f"{_usd(ea['conventional|bofn3|reorder'][CU]['per_alloy'])}.", St.font(18), ink, w, px(25))
    _para(d, x, y + px(8), f"Fixed costs a year (depreciation, service, utilities and space, fixed staff): "
          f"{_usd(fy['vertical']['total'])} against {_usd(fy['conventional']['total'])}. On campaign money alone "
          f"the automated lab's alloy is cheaper: {_usd(ea['vertical|bofn3|reorder'][AL]['per_alloy_campaign'])} "
          f"against {_usd(ea['conventional|bofn3|reorder'][AL]['per_alloy_campaign'])}.", St.font(17), ink2, w,
          px(24))


# ------------------------------------------------------------------------------------ part 3: where it does win
def _p_win(d, lay, t):
    n = _n()
    S, NW, Wn = n["labs"]["sum"], n["nowin"], n["win"]
    ns = n["labs"]["n_seeds"]
    t0 = cue("lab5", "labs")
    cf, co = S["cu_funnel"], S["cu_opt"]
    y0, y1 = px(200), px(900)
    # copper
    k = St.ramp(t, _part_t("win") + 0.05, _part_t("win") + 0.85)
    x0, x1 = px(80), px(1100)
    surf = _tile(d, (x0, y0, x1, y1), k)
    ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
    w = x1 - x0 - px(60)
    F.swatch(d, x0 + px(26), y0 + px(26), St.mix(St.BG, St.CAMP[CU], k), s=22)
    d.text((x0 + px(60), y0 + px(16)), "Copper: sooner with every policy, in every pairing",
           font=St.font(31, bold=True), fill=ink)
    y = y0 + px(84)
    for big_, words, sub in (
            (_sp(cf["af"]), "sooner with the funnel in both labs",
             f"to both targets, in both pairings; first in {_isp(cf['first_new'])} of {ns} seeds; seeds there: "
             f"{_isp(cf['hit_new'])} against {_isp(cf['hit_ref'])}"),
            ("at least " + _sp(co["af"]), "with BOFN or pKGFN",
             f"seeds at the first target: {_isp(co['T1']['hit_new'])} of {ns} against {_isp(co['T1']['hit_ref'])}; "
             f"at the halfway target: {_isp(co['T2']['hit_new'])} against {_isp(co['T2']['hit_ref'])}")):
        fbig = St.font(54, bold=True)
        d.text((x0 + px(30), y), big_, font=fbig, fill=ink)
        d.text((x0 + px(30) + St.text_w(fbig, big_) + px(18), y + px(26)), words, font=St.font(22), fill=ink)
        y = _para(d, x0 + px(30), y + px(78), sub, St.font(20), ink2, w, px(29)) + px(22)
    k2 = St.ramp(t, t0 + 5.0, t0 + 5.8) * k
    i1, i2 = St.mix(surf, St.INK, k2), St.mix(surf, St.INK2, k2)
    d.line([(x0 + px(30), y), (x1 - px(30), y)], fill=St.mix(surf, St.RULE, k2), width=px(1))
    y = _para(d, x0 + px(30), y + px(18), "Where the lead comes from: its own DED machine", St.font(25, bold=True),
              i1, w, px(34))
    y = _para(d, x0 + px(30), y + px(8), f"In {_isp(Wn['cu_inhouse'])} of {ns} seeds, depending on the arm, the first "
              "copper alloy past the best existing alloy was deposited in house; every one of the conventional "
              f"lab's came from a partner. The in-house machine is online around day {NW['online']['mxlab']:.0f} "
              "(median).", St.font(20), i2, w, px(29))
    _para(d, x0 + px(30), y + px(12), "Its final copper alloys are at least as good: "
          f"{_sp(Wn['cu_best']['auto'], '.2f', '')} against {_sp(Wn['cu_best']['conv'], '.2f', '')} (mean utility of "
          "the best new alloy, by arm).", St.font(20), i1, w, px(29))
    # aluminium's halfway target
    ao = S["al_T2_opt"]
    k3 = St.ramp(t, t0 + 9.0, t0 + 9.8)
    xa0, xa1 = px(1120), px(1840)
    wa = xa1 - xa0 - px(60)
    _tile(d, (xa0, y0, xa1, y1), k3)
    ink, ink2 = St.mix(St.BG, St.INK, k3), St.mix(St.BG, St.INK2, k3)
    F.swatch(d, xa0 + px(26), y0 + px(26), St.mix(St.BG, St.CAMP[AL], k3), s=22)
    yy = _para(d, xa0 + px(60), y0 + px(16), "Aluminium's halfway target, with an optimizer in both labs",
               St.font(31, bold=True), ink, xa1 - xa0 - px(86), px(40))
    d.text((xa0 + px(30), yy + px(16)), _sp(ao["af"]), font=St.font(54, bold=True), fill=ink)
    d.text((xa0 + px(30) + St.text_w(St.font(54, bold=True), _sp(ao["af"])) + px(18), yy + px(42)), "sooner",
           font=St.font(22), fill=ink)
    yy = _para(d, xa0 + px(30), yy + px(96), "BOFN and pKGFN, both pairings. The automated lab gets there in "
               f"{_isp(ao['hit_new'])} of {ns} seeds, the conventional lab in {_isp(ao['hit_ref'])}; the automated "
               f"lab is first in {_isp(ao['first_new'])}.", St.font(20), ink2, wa, px(29))
    yy = _para(d, xa0 + px(30), yy + px(16), "With both labs ordering as they go the intervals clear 1 (from "
               f"{_sp(ao['ci_lo_lean'], '.2f', '')}); with both stocked they just include it (from "
               f"{_sp(ao['ci_lo_stocked'], '.2f', '')}).", St.font(20), ink, wa, px(29))
    _para(d, xa0 + px(30), yy + px(16), "With the heuristic there is no lead: for this target the policy does more "
          "than the lab.", St.font(20), ink2, wa, px(29))


# ------------------------------------------------------------------------------------ part 4: money as spending
def _tick_usd(v) -> str:
    return "$0" if v == 0 else (f"${v / 1e6:g}M" if v >= 1e6 else f"${v / 1e3:g}k")


def _spend_plot(d, lay, box, camp, t_sweep, k, kc, kend):
    """One campaign's cumulative spend against the day: the automated lab (the campaign's colour: quartile band,
    median, the replayed seed) and the conventional lab (grey: band, dashed median, the same seed)."""
    n = _n()
    M = n["money"]
    tr_a, tr_c = M["traces"]["auto"].get(camp), M["traces"]["conv"].get(camp)
    if not tr_a:
        return
    bud = M["budget"].get(camp)
    hz = M["horizon"]
    ymax = (bud * 1.08) if bud else 1.12 * max(max(tr_a["hi"]), max(tr_c["hi"]) if tr_c else 0.0)
    ax = F.Ax(box, (0.0, hz), (0.0, ymax), "days", "usd")
    ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
    col = St.CAMP[camp]
    f = St.font(17)
    for v in St.nice_ticks(0, ymax, 4):
        y = ax.Y(v)
        d.line([(ax.x0, y), (ax.x1, y)], fill=St.mix(St.BG, St.GRID, k), width=1)
        d.text((ax.x0 - px(8), y), _tick_usd(v), font=f, fill=ink2, anchor="rm")
    d.line([(ax.x0, ax.y1), (ax.x1, ax.y1)], fill=St.mix(St.BG, St.RULE, k), width=px(1))
    for v in sorted({0.0, 180.0, 365.0, 545.0, hz}):
        if v > hz:
            continue
        x = ax.X(v)
        d.line([(x, ax.y1), (x, ax.y1 + px(5))], fill=St.mix(St.BG, St.RULE, k), width=1)
        d.text((x, ax.y1 + px(8)), f"{v:.0f}", font=f, fill=ink2, anchor="ma")
    d.text(((ax.x0 + ax.x1) / 2, ax.y1 + px(36)), "days since the money arrived", font=St.font(18), fill=ink2,
           anchor="ma")
    F.swatch(d, ax.x0, ax.y0 - px(46), St.mix(St.BG, col, k), s=18)
    d.text((ax.x0 + px(28), ax.y0 - px(50)), f"{CAMP_WORD[camp]}: cumulative campaign spend",
           font=St.font(22, bold=True), fill=ink)
    if bud:
        ax.dotted_h(d, bud, St.mix(St.BG, St.TARGET, k), r=px(1.8), gap=px(9))
        F.label_box(d, (ax.x0 + px(10), ax.Y(bud) - px(8)), f"two years' money: {_usd(bud)}", St.font(16),
                    ink2, anchor="ld", pad=px(3))
        y90 = ax.Y(M["share"] * bud)
        St.dashed_line(d, [(ax.x0, y90), (ax.x1, y90)], St.mix(St.BG, St.INK3, k), width=1, dash=px(4), gap=px(6))
        d.text((ax.x1 + px(8), y90), f"{M['share_pct']:.0f} %", font=St.font(15), fill=ink2, anchor="lm")
    upto = hz * St.ease(t_sweep / 6.0)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    series = ((tr_c, St.BASE, True, kc), (tr_a, col, False, 1.0))
    for tr, cc, dashed, kk in series:
        if not tr or kk <= 0:
            continue
        xs = np.array(tr["days"], float)
        m = xs <= min(upto, hz) + 1e-6
        if m.sum() >= 2:
            ax.band(od, list(xs[m]), list(np.array(tr["q25"])[m]), list(np.array(tr["q75"])[m]), cc,
                    alpha=0.20 * k * kk)
    if lay.mode == "RGB":
        lay.paste(over, (0, 0), over)
    else:
        lay.alpha_composite(over)
    for tr, cc, dashed, kk in series:
        if not tr or kk <= 0:
            continue
        xs = np.array(tr["days"], float)
        m = xs <= min(upto, hz) + 1e-6
        if m.sum() < 2:
            continue
        cck = St.mix(St.BG, cc, k * kk)
        if tr.get("seed"):
            pts = [(float(a), float(b)) for a, b in zip(xs[m], np.array(tr["seed"])[m])]
            d.line(ax.P(pts), fill=St.mix(St.BG, St.mix(cc, St.INK, 0.45), 0.75 * k * kk), width=px(1))
        pts = [(float(a), float(b)) for a, b in zip(xs[m], np.array(tr["median"])[m])]
        if dashed:
            St.dashed_line(d, ax.P(pts), cck, width=px(3), dash=px(9), gap=px(6))
        else:
            d.line(ax.P(pts), fill=cck, width=px(4), joint="curve")
    # the 90 % mark of the automated lab (the tables' median day over seeds), and each lab's end
    d90 = M["d90"]["auto"][camp]
    if bud and d90["day"] is not None and d90["day"] < hz and 2 * d90["n"] > d90["of"]:
        km = St.ramp(upto, d90["day"], d90["day"] + 30.0) * k
        if km > 0:
            x = ax.X(d90["day"])
            d.line([(x, ax.Y(M["share"] * bud)), (x, ax.y1)], fill=St.mix(St.BG, St.INK, km), width=px(2))
            F.label_box(d, (x + px(8), ax.y1 - px(36)), f"day {d90['day']:.0f}", St.font(22, bold=True),
                        St.mix(St.BG, St.INK, km), anchor="la", pad=px(4))
            d.text((x + px(8), ax.y1 - px(66)), f"{M['share_pct']:.0f} % spent (median of {d90['of']} seeds)",
                   font=St.font(15), fill=St.mix(St.BG, St.INK2, km), anchor="la")
    if kend > 0:
        for key, tr, yoff in (("conv", tr_c, 0), ("auto", tr_a if not bud else None, 0)):
            if not tr:
                continue
            e = M["end"][key][camp]
            big_ = f"{100 * e['share']:.0f} %" if e.get("share") else _usd(e["median"])
            kk = kend * k
            d.text((ax.x1 + px(8), ax.Y(e["median"]) - px(2)), big_, font=St.font(19, bold=True),
                   fill=St.mix(St.BG, St.INK, kk), anchor="lm")
            d.text((ax.x1 + px(8), ax.Y(e["median"]) + px(18)), "conventional" if key == "conv" else "automated",
                   font=St.font(13), fill=St.mix(St.BG, St.INK2, kk), anchor="lm")


def _p_money(d, lay, t):
    n = _n()
    M, E = n["money"], n["econ"]
    ns = n["labs"]["n_seeds"]
    names = n["labs"]["names"]
    t1, t2, t3 = (cue(k, "labs") for k in ("mon1", "mon2", "mon3"))
    k = St.ramp(t, _part_t("money") + 0.05, _part_t("money") + 0.85)
    kc = St.ramp(t, t1 + 2.0, t1 + 3.0)                   # the conventional lab's curve, beside the automated lab's
    kend = St.ramp(t, t2 + 3.0, t2 + 3.8)
    for i, camp in enumerate((AL, CU)):
        bx = px(160) + i * px(590)
        _spend_plot(d, lay, (bx, px(280), bx + px(440), px(680)), camp, t - t1 - 0.5, k, kc, kend)
    # legend
    ly = px(762)
    ink2 = St.mix(St.BG, St.INK2, k)
    x = px(100)
    d.line([(x, ly - px(3)), (x + px(40), ly - px(3))], fill=St.mix(St.BG, St.CAMP[AL], k), width=px(3))
    d.line([(x, ly + px(3)), (x + px(40), ly + px(3))], fill=St.mix(St.BG, St.CAMP[CU], k), width=px(3))
    d.text((x + px(50), ly), f"automated lab, BOFN, stocked: median of {ns} seeds", font=St.font(17), fill=ink2,
           anchor="lm")
    St.dashed_line(d, [(x + px(540), ly), (x + px(580), ly)], St.mix(St.BG, St.BASE, k * kc), width=px(3), dash=px(8),
                   gap=px(5))
    d.text((x + px(590), ly), f"conventional lab, BOFN, stocked: median of {ns} seeds", font=St.font(17),
           fill=St.mix(St.BG, St.INK2, k * kc), anchor="lm")
    hz = M["horizon"]
    d.text((x, ly + px(30)), f"bands: the middle half of the seeds;  thin lines: seed {n['replay']['seed']}, the seed "
           f"the replay shows, in each lab;  at the right: the share spent by day {hz:.0f}" if M["budget"][AL] else
           f"bands: the middle half of the seeds;  thin lines: seed {n['replay']['seed']}, the seed the replay shows, "
           f"in each lab;  at the right: spent by day {hz:.0f}", font=St.font(17), fill=ink2, anchor="lm")
    if M["budget"][AL]:
        ch = M["d90_cheap"]
        dd = lambda q: (f"day {q['day']:.0f}" if 2 * q["n"] > q["of"] and q["day"] < hz else "not in two years")
        _para(d, x, ly + px(58), f"With the heuristic and the funnel, {M['share_pct']:.0f} % is spent by "
              f"{dd(ch['auto'][AL])} (aluminium) and {dd(ch['auto'][CU])} (copper) in the automated lab, and by "
              f"{dd(ch['conv'][AL])} and {dd(ch['conv'][CU])} in the conventional lab. Once its money is spent the "
              "automated lab idles: a lab that fast would be planned with more money or paced spending, which this "
              "round did not run.", St.font(17), ink2, px(1140), px(25))
    else:
        _para(d, x, ly + px(58), "This round has no money limit: the curves are what each lab spent, not what it "
              "was allowed.", St.font(17), ink2, px(1140), px(25))
    # ---- the cost table, as the voice reaches it
    kt = St.ramp(t, t3 - 0.5, t3 + 0.3)
    x0, y0, x1, y1 = px(1300), px(206), px(1840), px(960)
    surf = _tile(d, (x0, y0, x1, y1), kt)
    ink, ink2 = St.mix(St.BG, St.INK, kt), St.mix(St.BG, St.INK2, kt)
    d.text((x0 + px(22), y0 + px(14)), "Cost per new alloy tested,", font=St.font(24, bold=True), fill=ink)
    d.text((x0 + px(22), y0 + px(45)), "with fixed costs", font=St.font(24, bold=True), fill=ink)
    d.text((x1 - px(22), y0 + px(92)), "automated   conventional", font=St.font(15), fill=ink2, anchor="ra")
    y = y0 + px(116)
    ea = E["arms"]
    for camp in (AL, CU):
        F.swatch(d, x0 + px(22), y + px(5), St.mix(St.BG, St.CAMP[camp], kt), s=15)
        d.text((x0 + px(46), y), CAMP_WORD[camp], font=St.font(19, bold=True), fill=ink)
        y += px(31)
        for pol in ("bofn3", "pkgfn3", "fast"):
            a_, c_ = ea[f"vertical|{pol}|reorder"][camp], ea[f"conventional|{pol}|reorder"][camp]
            lead = camp == AL and pol == "bofn3"
            fr = St.font(21, bold=True) if lead else St.font(19)
            d.text((x0 + px(46), y), names[pol][camp], font=St.font(19), fill=ink)
            d.text((x1 - px(150), y), _usd(a_["per_alloy"]), font=fr, fill=ink, anchor="ra")
            d.text((x1 - px(22), y), _usd(c_["per_alloy"]), font=fr, fill=ink, anchor="ra")
            y += px(30)
        y += px(8)
    d.line([(x0 + px(22), y), (x1 - px(22), y)], fill=St.mix(surf, St.RULE, kt), width=px(1))
    y += px(12)
    fy = E["fixed_year"]
    so = E["sum"]
    wt = x1 - x0 - px(44)
    y = _para(d, x0 + px(22), y, "On campaign money alone an aluminium alloy costs less in the automated lab: "
              f"{_usd(1e3 * so['al_opt_campaign']['auto']['lo'])} to {_usd(1e3 * so['al_opt_campaign']['auto']['hi'])} "
              f"against {_usd(1e3 * so['al_opt_campaign']['conv']['lo'])} with an optimizer.", St.font(17), ink2,
              wt, px(24))
    y = _para(d, x0 + px(22), y + px(10), f"Fixed costs a year: {_usd(fy['vertical']['total'])} against "
              f"{_usd(fy['conventional']['total'])} (depreciation, service, utilities and space, fixed staff), the "
              "automated lab's charged in full from day 0.", St.font(17), ink2, wt, px(24))
    tt = so["to_target"]
    _para(d, x0 + px(22), y + px(10), f"To each target with its equipment: ${tt['auto']['lo']:.1f}M to "
          f"${tt['auto']['hi']:.1f}M committed, against ${tt['conv']['lo']:.0f}k to ${tt['conv']['hi']:.0f}k.",
          St.font(18, bold=True), ink, wt, px(25))
    d.text((x0 + px(22), y1 - px(30)), "Stocked arms; medians over seeds. Simulated; round 3's cost model.",
           font=St.font(14), fill=ink2)


# ================================================================================================ the takeaway
def takeaway_caps() -> list:
    n = _n()
    return [(0.0, layout("takeaway")["duration"],
             f"Like for like: the same policy and the same stock rule in both labs, {n['labs']['n_seeds']} simulated "
             "two-year runs per arm.")]


def takeaway_frame(t: float, captions: bool = True) -> np.ndarray:
    n = _n()
    S, NW, M, E = n["labs"]["sum"], n["nowin"], n["money"], n["econ"]
    ns = n["labs"]["n_seeds"]
    im, d = _new()
    total = layout("takeaway")["duration"]
    if captions:
        F._header(d, TITLES["takeaway"], takeaway_caps(), t, total=total)
    else:
        d.text((px(80), px(44)), TITLES["takeaway"], font=St.font(44, bold=True), fill=St.INK)
    c1, c2, c3 = (cue(k, "takeaway") for k in ("take1", "take2", "take3"))
    cf, co, ao = S["cu_funnel"], S["cu_opt"], S["al_T2_opt"]
    ea = E["arms"]
    bud = M["budget"][AL]
    rows = [
        (c1, CU, "Copper: sooner in the automated lab, with every policy",
         [(_sp(cf["af"]), "with the funnel"), ("at least " + N5.x1(co["af"]["lo"]), "with BOFN or pKGFN")],
         f"Seeds at the first target with an optimizer: {_isp(co['T1']['hit_new'])} of {ns} against "
         f"{_isp(co['T1']['hit_ref'])}. Mostly its own DED machine, in house from around day "
         f"{NW['online']['mxlab']:.0f}."),
        (c2, AL, "Aluminium: a tie on the first target; ahead on the halfway target only with an optimizer",
         [(_sp(S["al_T1_heur"]["af"]) if S["al_T1_heur"]["af"]["lo"] != S["al_T1_heur"]["af"]["hi"] else
           N5.x1(S["al_T1_heur"]["af"]["lo"]), "first target, heuristic: a tie"),
          (_sp(ao["af"]), "halfway target, BOFN or pKGFN in both labs")],
         f"The policy does more than the lab: BOFN and pKGFN reach the halfway target in "
         f"{_isp(NW['policy']['al_T2_hits_opt'])} of {ns} seeds in either lab, the heuristic in "
         f"{_isp(NW['policy']['al_T2_hits_heur'])}. With an optimizer the first target is {_sp(S['al_T1_opt']['af'])} "
         "sooner, and every interval includes 1."),
        (c3, None, "Not cheaper",
         ([(f"about {_isp({k_: int(v) for k_, v in n['take']['months'].items() if k_ in ('lo', 'hi')})} months",
            "to spend two years' money (BOFN, stocked)")] if bud else []) +
         [(f"{_usd(ea['vertical|bofn3|reorder'][AL]['per_alloy'])} against "
           f"{_usd(ea['conventional|bofn3|reorder'][AL]['per_alloy'])}", "per aluminium alloy, with fixed costs")],
         (f"{M['share_pct']:.0f} % of the money is spent by day {M['d90']['auto'][AL]['day']:.0f} (aluminium) and "
          f"{M['d90']['auto'][CU]['day']:.0f} (copper); then the lab idles. " if bud else "")
         + "Campaign money to a target is no lower."),
    ]
    y = px(200)
    for t_in, camp, head, bigs, small in rows:
        k = St.ramp(t, t_in - 0.4, t_in + 0.4)
        surf = _tile(d, (px(80), y, px(1840), y + px(246)), k)
        ink, ink2 = St.mix(St.BG, St.INK, k), St.mix(St.BG, St.INK2, k)
        F.swatch(d, px(108), y + px(26), St.mix(St.BG, St.CAMP[camp] if camp else St.INK2, k), s=20)
        d.text((px(142), y + px(18)), head, font=St.font(28, bold=True), fill=ink)
        x = px(108)
        for big_, words in bigs:
            fb = St.font(46, bold=True)
            d.text((x, y + px(70)), big_, font=fb, fill=ink)
            d.text((x, y + px(130)), words, font=St.font(18), fill=ink2)
            x += max(St.text_w(fb, big_), St.text_w(St.font(18), words)) + px(70)
        _para(d, px(108), y + px(168), small, St.font(19), ink2, px(1700), px(27), max_lines=2)
        y += px(264)
    kf = St.ramp(t, c1 + 1.0, c1 + 1.8)
    _para(d, px(80), y + px(4), "Simulated: synthetic truths, simulated instruments, assumed capacities, prices, lead "
          "times and schedules. It shows how the labs, plans and policies interact in the model, not what the real "
          "lab will find.", St.font(18), St.mix(St.BG, St.INK2, kf), px(1760), px(26))
    return np.asarray(im)


# ================================================================================================ the interface
def captions(name: str) -> list:
    return labs_caps() if name == "labs" else takeaway_caps()


def _segments() -> list:
    return [("labs", float(layout("labs")["duration"]), labs_frame, TITLES["labs"]),
            ("takeaway", float(layout("takeaway")["duration"]), takeaway_frame, TITLES["takeaway"])]


class _Segs(list):
    """SEGMENTS, built on first use (the lengths come from the recorded lines)."""

    def _fill(self):
        if not list.__len__(self):
            list.extend(self, _segments())

    def __iter__(self):
        self._fill()
        return list.__iter__(self)

    def __len__(self):
        self._fill()
        return list.__len__(self)

    def __getitem__(self, i):
        self._fill()
        return list.__getitem__(self, i)

    def __add__(self, other):
        return list(self) + list(other)

    def __radd__(self, other):
        return list(other) + list(self)

    def __repr__(self):
        self._fill()
        return list.__repr__(self)


SEGMENTS = _Segs()


def segments() -> list:
    """SEGMENTS as a plain list."""
    return list(SEGMENTS)


def still_times() -> list:
    """(segment, seconds, label): one moment per card state, for a look at every card."""
    out = []
    L = layout("labs")
    for r in L["lines"]:
        out.append(("labs", r["end"] - 0.3, r["id"]))
    for p, t0 in L["parts"].items():
        out.append(("labs", t0 + 0.3, f"fade_{p}"))
    out.append(("labs", L["duration"] - 0.6, "end"))
    for r in layout("takeaway")["lines"]:
        out.append(("takeaway", r["end"] - 0.3, r["id"]))
    out.append(("takeaway", layout("takeaway")["duration"] - 0.6, "end"))
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "nums":
        check_numbers()
    elif cmd == "tts":
        au = speak(set(sys.argv[2:]) or None)
        print(f"{len(au)} lines in {NDIR}")
    elif cmd == "check":
        check_audio()
    elif cmd == "plan":
        for seg in ("labs", "takeaway"):
            L = layout(seg)
            print(f"{seg}: {L['duration']:.1f} s; parts {L['parts']}")
            for r in L["lines"]:
                print(f"  {r['t']:6.1f}-{r['end']:6.1f}  {r['id']:6s} {'' if r['recorded'] else '(est) '}{r['text']}")
    elif cmd == "stills":
        out = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/d1")
        out.mkdir(parents=True, exist_ok=True)
        fn = dict(labs=labs_frame, takeaway=takeaway_frame)
        want = set(sys.argv[3:])
        for seg, tt, lab in still_times():
            if want and lab not in want:
                continue
            Image.fromarray(fn[seg](tt)).save(out / f"{seg}_{lab}.png")
            print(f"{seg} {tt:6.1f} s -> {out}/{seg}_{lab}.png", flush=True)
    else:
        raise SystemExit(__doc__)

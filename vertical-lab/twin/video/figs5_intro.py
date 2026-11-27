"""The two-year cut's opening and closing cards (TWIN_VIDEO_ROUND=5, or a later round; twin/video/cut5.py calls them):

    changes     what the round changed in the twin: two years from the day the money arrives
    counters    the three counters (designed, made, tested), the line on early stopping, and how to read the replay's
                plots (best new alloy so far against the two targets, both labs; money as cumulative spend per lab; why
                best-so-far is flat)
    atomizer    the automated atomizer's design target, labelled as one, next to the lab's record
    notes       what is real, what is assumed or a stand-in, and what is simulated

    python -m twin.video.figs5_intro numbers     # out/twin<ROUND>/video/numbers_intro.json, and the claims
    python -m twin.video.figs5_intro nums        # every line rendered; every figure in it must be a placeholder
    python -m twin.video.figs5_intro tts         # speak the lines whose text changed (Kokoro) -> narration_intro/
    python -m twin.video.figs5_intro check       # heard back by faster-whisper -> narration_intro/check.json
    python -m twin.video.figs5_intro plan        # each line's time in its segment, and the segments' lengths
    python -m twin.video.figs5_intro stills      # every card state -> /tmp/vid/intro/<segment>_<t>.png

For the cut: SEGMENTS = [(name, seconds, frame function, chapter title)], captions(name), narration_lines(name),
check_numbers().

Every number on a card or in a line comes from numbers(): the round's own code (twin/round<ROUND>.py: ROOM_DAYS, USED,
DECISIONS, ATOM_MANUAL, ATOM_RUN_H, HPC), its comparison file (out/twin<ROUND>/like<ROUND>.json: the targets) and its
rows (twin.like<ROUND>.load_all: the replayed run's counters, HPC stream, atomizer runs, dates, curves and idle report;
the arm's means). Three things are constants with their source beside them (CITED below): the crucibles, which only
the round's notes state; the lab's own atomizer record, which is numbers3.LAB_ATOMIZER (DAL's runs.csv); and the
immersion's length, which twin/campaign.py holds inside a method. Nothing else is typed in. The lines' numbers are
placeholders filled from the same dict (narration5_intro.json), so the voice can only say what the cards show.

The cards are built as round 3's (figs3.py): drawn with PIL frame by frame, each part appearing when the narration
names it. A line's time is not typed in either: the lines of a segment follow one another, each after the one before
has ended (timing() reads their recorded lengths), so the segments re-time themselves when a line is spoken again.
"""
from __future__ import annotations

import datetime as dt
import functools
import importlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import data as D
from . import style as St
from .style import px

W, H = St.W, St.H
SCRIPT = Path(__file__).with_name("narration5_intro.json")
NDIR = D.VID / "narration_intro"                    # committed: each line's FLAC, lines.json, script.json
NUMBERS = D.VID / "numbers_intro.json"
CAMP_WORD = {"flaime_al": "aluminium", "onr_cu": "copper"}

# the run the cut replays: the stocked automated lab with BOFN on both campaigns, on the arm's median seed for both
# campaigns together (twin.like<ROUND>.median_seed, section 7.13 of notes/twin_round5.md), and the same seed, policy
# and stock rule in the conventional lab beside it. (lab, plan, policy, stock), as twin.like<ROUND>.gk takes them.
REPLAY_ARM = ("vertical", "parallel", "bofn3", "reorder")
CONV_ARM = ("conventional", "external", "bofn3", "reorder")

# ------------------------------------------------------------------------------------------- constants, with sources
CITED = dict(
    # only the round's notes state these (no code or data file does): notes/twin_round5.md, section 2
    crucibles=dict(need_lo=6, need_hi=8, now=1, dry_h_lo=14, dry_h_hi=16, runs_day_now=1,
                   source="notes/twin_round5.md section 2: 'Each crucible is out of service about 14-16 h for its "
                          "overnight BN dry, so a cycle of 2-3 h needs 6-8 coated crucibles per alloy family in "
                          "rotation; the lab has one per family now, which allows at most 1 run a day' (from DAL's "
                          "atomizer SOP, PR 253, and DAL #219 and #256)"),
    # twin/campaign.py, Campaign's step table: "immersion": ([], "immersion", 720.0) hours
    immersion_h=720.0,
    immersion_source="twin/campaign.py: \"immersion\": ([], \"immersion\", 720.0)",
)
WEEKDAY = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")     # day 0 is a Monday

# what each round changed (the card's items): (head, body, (line id, the phrase that names it)). Bodies are format
# strings over numbers()["intro"] (see _fill). A round without an entry shows round 5's and fails claims(), so a
# re-render for a later round says that this card and its two lines need that round's own words.
CHANGES = {5: [
    ("All the money on day 0",
     "Two years of each campaign's money from the start, in both labs: aluminium {money_al}, copper {money_cu}. No "
     "spending plan.", ("chg1", "Each campaign")),
    ("The facility is ready between day {room_lo} and day {room_hi}",
     "Drawn per seed: a stand-in. In the replayed run it is ready on day {room_run}.", ("chg1", "The facility")),
    ("Equipment ordered on day 0, some of it used",
     "Installed once the space is ready. Bought used where a used market exists and that saves at least {used_days} "
     "expected days.", ("chg1", "and the equipment")),
    ("Experiments from day 0",
     "Through partners and BYU's existing equipment, while the automated lab is built.", ("chg2", "Experiments")),
    ("Decisions made by people take time",
     "Conventional lab: a review on working days and a {meeting_day} meeting. Automated lab: its own decisions every "
     "hour, and a person's sign-off for a step over {signoff}.", ("chg2", "Decisions made")),
    ("The atomizer: {manual_week} runs a week, or 24/7",
     "Conventional lab: at most {manual_week} a week. Automated lab: the same until its cell is integrated, then 24/7 "
     "(around the clock) at a derived cycle, a design target.", ("chg2", "The conventional lab")),
    ("A continuous HPC stream of candidates",
     "{hpc_day} computed candidates a day on a stand-in allocation of {hpc_cores} cores, outside the campaigns' "
     "money.", ("chg2", "And the HPC")),
]}


# ================================================================================================== the numbers
def _mod(stem: str):
    """twin.<stem><ROUND>, or round 5's where a later round keeps it (the module used is recorded in numbers())."""
    for r in (D.ROUND, 5):
        try:
            return importlib.import_module(f"twin.{stem}{r}"), r
        except ImportError:
            continue
    raise ImportError(f"twin.{stem}{D.ROUND}")


def _rk(row: dict) -> dict:
    """A row's round block (r5 in round 5's rows)."""
    return row.get(f"r{D.ROUND}") or row["r5"]


def _clean(x):
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    return x


@functools.lru_cache(maxsize=1)
def numbers() -> dict:
    """{"intro": {...}}: every number these cards and lines use, read from the round's code, comparison file and
    rows. Written to out/twin<ROUND>/video/numbers_intro.json by write_numbers()."""
    sys.path.insert(0, str(D.HERE))
    L, like_r = _mod("like")
    R5, round_r = _mod("round")
    from . import numbers3 as N3                    # the lab's own atomizer record (DAL's runs.csv), as round 3 read it
    like = json.loads((D.RES / f"like{D.ROUND}.json").read_text())
    T = like["targets"]
    A = L.load_all()
    key, ckey = L.gk(*REPLAY_ARM), L.gk(*CONV_ARM)
    arm, carm = A[key], A[ckey]
    ms = L.median_seed(arm, T)
    seed = int(ms["seed"])
    row, crow = arm[seed], carm[seed]
    rk = _rk(row)
    hpc = rk["hpc"]
    days = float(getattr(L, "HORIZON", row["cfg"]["days"]))
    camps = list(D.CAMPAIGNS)

    def cnt(c, src):
        return dict(seen=src["designed"], lots_made=src["lots_made"], alloys_made=src["alloys_made"],
                    alloys_printed=src["alloys_printed"], alloys_tested=src["alloys_tested"])
    arm_cnt = L.counters(A, key)
    counters = dict(
        run={c: dict(cnt(c, rk["counters"][c]), designed_hpc=hpc["campaigns"][c]["evaluated"]) for c in camps},
        arm={c: dict(cnt(c, arm_cnt[c]),
                     designed_hpc=float(np.mean([_rk(r)["hpc"]["campaigns"][c]["evaluated"] for r in arm.values()])))
             for c in camps},
        n_seeds=len(arm))

    man = R5.ATOM_MANUAL
    manual_week = len(man["starts"]) * sum(len(v) for v in man["campaign_weekdays"].values())
    run_h = dict(R5.ATOM_RUN_H)
    rec = dict(N3.LAB_ATOMIZER)
    first, last = dt.date.fromisoformat(rec["first"]), dt.date.fromisoformat(rec["last"])
    rec_days = (last - first).days + 1
    cru = {k: v for k, v in CITED["crucibles"].items()}
    atom = rk["atom"]
    dec = R5.DECISIONS["nominal"]
    money = {c: row["campaigns"][c]["budget"] for c in camps}

    def curves(r):
        out = {}
        for c in camps:
            cc = r["campaigns"][c]
            out[c] = dict(best=[[round(float(a), 3), round(float(b), 4)] for a, _, b in cc.get("curve_new") or []],
                          spend=[[round(float(a), 2), round(float(b), 2)] for a, b in cc.get("spend_curve") or []])
        return out

    # why best-so-far can be flat: the three the request names, and money where the replayed run's own idle report
    # has a stretch whose cause is money (a round with no money limit has none, and the card and the line drop it)
    causes = set()
    for c in camps:
        for grp in rk["idle"]["stretches"][c].values():
            for s in grp:
                causes.add(str(s["cause"]))
    imm_days = CITED["immersion_h"] / 24.0
    flat = ["waiting for stock", f"a {_word(imm_days)}-day immersion", "the queue for a station"]
    flat_screen = ["waiting for stock", f"a {imm_days:.0f}-day immersion", "the queue for a station"]
    has_money = any("money" in c for c in causes)
    if has_money:
        flat.append("money")
        flat_screen.append("money")
    intro = dict(
        round=D.ROUND, like_module=f"twin.like{like_r}", round_module=f"twin.round{round_r}",
        horizon_days=days, horizon_years=days / 365.0,
        money=dict(money, total=sum(money.values()),
                   same_in_both_labs=all(crow["campaigns"][c]["budget"] == money[c] for c in camps)),
        room=dict(lo=R5.ROOM_DAYS[0], hi=R5.ROOM_DAYS[1], run_day=rk["room_h"] / 24.0, source=R5.ROOM_SOURCE),
        used=dict(rule_days=R5.USED["rule_days"], price_frac=R5.USED["price_frac"],
                  bought_run=sorted(rk.get("used") or {}), source=R5.USED["source"]),
        decisions=dict(signoff_usd=dec["signoff"]["usd"],
                       meeting_day=WEEKDAY[dec["conventional"]["meeting"]["days"][0]], source=dec["source"]),
        hpc=dict(cores=hpc["cores"], per_day=hpc["per_day"], add_per_day=hpc["add_per_day"], keep=hpc["keep"],
                 evaluated={c: hpc["campaigns"][c]["evaluated"] for c in camps},
                 evaluated_m={c: hpc["campaigns"][c]["evaluated"] / 1e6 for c in camps},
                 source=R5.HPC["source"]),
        counters=counters,
        targets={tn: {c: T[tn][c] for c in camps} for tn in ("T1", "T2")},
        atomizer=dict(
            manual_week=manual_week, starts_day=len(man["starts"]),
            days_week=sum(len(v) for v in man["campaign_weekdays"].values()),
            al_days=[WEEKDAY[i] for i in man["campaign_weekdays"]["flaime_al"]],
            cu_days=[WEEKDAY[i] for i in man["campaign_weekdays"]["onr_cu"]], manual_source=man["source"],
            run_h=run_h, week_247={c: 168.0 / run_h[c] for c in camps},
            crucibles=cru,
            record=dict(runs=rec["runs"], first=rec["first"], last=rec["last"], days=rec_days,
                        per_week=rec["runs"] / (rec_days / 7.0), source=rec["source"]),
            run=dict(runs=atom["runs"], al=atom["runs_by"]["flaime_al"], cu=atom["runs_by"]["onr_cu"],
                     switch_day=atom["switch_h"] / 24.0, cell_day=row["r4"]["cell_h"] / 24.0)),
        immersion_days=imm_days,
        flat=dict(words=", ".join(flat[:-1]) + ", or " + flat[-1], screen=flat_screen, money=has_money,
                  causes=sorted(causes)),
        replay=dict(arm=key, conv_arm=ckey, seed=seed, n_seeds=len(arm), score=float(ms["score"]),
                    events=Path(row["events_file"]).name if row.get("events_file") else Path(ms["events"]).name,
                    conv_events=Path(crow["events_file"]).name if crow.get("events_file") else None,
                    policy={c: L.POL[REPLAY_ARM[2]][c] for c in camps},
                    days={k: float(v) for k, v in ms["days"].items()},
                    medians={k: float(v) for k, v in ms["medians"].items()},
                    curves=dict(auto=curves(row), conv=curves(crow))),
    )
    return _clean(dict(intro=intro))


@functools.lru_cache(maxsize=1)
def _n() -> dict:
    """What the cards draw from: the written numbers_intro.json when it is there (a frame worker then starts without
    reading every row), else numbers(). check_numbers() fails if the file is not what numbers() gives now."""
    if NUMBERS.exists() and not os.environ.get("TWIN_VIDEO_INTRO_FRESH"):
        try:
            return json.loads(NUMBERS.read_text())["intro"]
        except Exception:                               # noqa: BLE001  (mid-write)
            pass
    return numbers()["intro"]


def write_numbers() -> Path:
    NUMBERS.parent.mkdir(parents=True, exist_ok=True)
    NUMBERS.write_text(json.dumps(numbers(), indent=1) + "\n")
    _n.cache_clear()
    return NUMBERS


def numbers_file_current() -> bool:
    """The written file is what numbers() gives now (the cards draw from the file)."""
    try:
        return json.loads(NUMBERS.read_text()) == json.loads(json.dumps(numbers()))
    except Exception:                                   # noqa: BLE001
        return False


def claims() -> list:
    """[(what a card or a line says in words, whether the numbers bear it out)]."""
    n = numbers()["intro"]
    cr, ca = n["counters"]["run"], n["counters"]["arm"]
    at = n["atomizer"]
    out = [
        ("the numbers file the cards draw from (numbers_intro.json) is what numbers() gives now",
         numbers_file_current()),
        (f"the 'what changed' card and its two lines are written for round {n['round']}", n["round"] in CHANGES),
        ("the replayed seed is the arm's median seed for both campaigns together, and the conventional lab's run is "
         "the same seed, policy and stock rule", n["replay"]["conv_arm"].replace("conventional_external", "") ==
         n["replay"]["arm"].replace("vertical_parallel", "")),
        ("each campaign has a fixed amount of money from day 0, the same in both labs",
         all(math.isfinite(float(n["money"][c])) and n["money"][c] > 0 for c in D.CAMPAIGNS)
         and bool(n["money"]["same_in_both_labs"])),
        ("the replayed run's facility day lies in the window", n["room"]["lo"] <= n["room"]["run_day"] <= n["room"]["hi"]),
        ("designed (computed on the HPC) is the stream's daily count over the run's days, the same for both campaigns",
         all(abs(n["hpc"]["evaluated"][c] / n["hpc"]["per_day"] - n["horizon_days"]) < 1.0 for c in D.CAMPAIGNS)),
        ("the daily count is the allocation's: cores x 24 h over the core-hours a candidate takes (0.05)",
         abs(n["hpc"]["cores"] * 24.0 / 0.05 - n["hpc"]["per_day"]) < 1e-6),
        ("'the horizon is two years'", abs(n["horizon_years"] - 2.0) < 1e-9),
        ("early stopping: fewer alloys are tested than printed or deposited, and no more printed than made, in the "
         "replayed run and in the arm's means",
         all(src[c]["alloys_tested"] < src[c]["alloys_printed"] <= src[c]["alloys_made"] + 1e-9
             for src in (cr, ca) for c in D.CAMPAIGNS)),
        ("copper's alloys made outnumber its powder lots in the replayed run (most are blends of powders already made)",
         cr["onr_cu"]["alloys_made"] > cr["onr_cu"]["lots_made"]),
        ("the conventional lab's atomizer: at most 8 runs a week (note 1)", at["manual_week"] == 8),
        ("the 24/7 design target is far above the assumed manual rate, which is above the lab's record",
         at["week_247"]["flaime_al"] > at["manual_week"] > at["record"]["per_week"]),
        ("the design target needs more crucibles per family than the lab has",
         at["crucibles"]["need_lo"] > at["crucibles"]["now"]),
        ("in the replayed run the design cycle applies from the day the cell is integrated",
         abs(at["run"]["switch_day"] - at["run"]["cell_day"]) < 1e-6),
        ("the two targets are ordered: the halfway target is above the best existing alloy",
         all(n["targets"]["T2"][c] > n["targets"]["T1"][c] for c in D.CAMPAIGNS)),
        ("'or money' is said and shown only if the replayed run's idle report has a stretch whose cause is money",
         n["flat"]["money"] == any("money" in c for c in n["flat"]["causes"])),
    ]
    return [(c, bool(ok)) for c, ok in out]


# ================================================================================================== the script
_PH = re.compile(r"\{([^{}|]+)\|([^{}]+)\}")
_FIG = re.compile(r"(?<![\w.,-])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\w-])|(?<![\w-])\d+(?:\.\d+)?(?![\w-])")
_BIG = re.compile(r"(?<![\w.,-])\d{1,3}(?:,\d{3})+(?![\w-])")


def _word(v) -> str:
    from num2words import num2words
    return num2words(int(round(float(v))))


def _get(n: dict, path: str):
    cur = n
    for k in path.split("."):
        cur = cur[k]
    return cur


def _fmt(v, fmt: str) -> str:
    if fmt == "s":
        return str(v)
    if fmt == "w":
        return _word(v)
    if fmt == "d":
        return f"{int(round(float(v))):d}"
    if fmt == ",d":
        return f"{int(round(float(v))):,d}"
    return format(float(v), fmt)


def render(tpl: str, n: dict | None = None) -> tuple:
    """A line's text with its placeholders filled from numbers(), and what filled them: [(shown, path, format)]."""
    n = numbers() if n is None else n
    nums = []

    def sub(m):
        shown = _fmt(_get(n, m.group(1)), m.group(2))
        nums.append([shown, m.group(1), m.group(2)])
        return shown
    return _PH.sub(sub, tpl), nums


def raw_lines() -> list:
    return json.loads(SCRIPT.read_text())["lines"]


def lines() -> list:
    """The script, rendered: each line with its text and nums as numbers() gives them now."""
    out = []
    for ln in raw_lines():
        text, nums = render(ln["text"])
        out.append(dict(ln, template=ln["text"], text=text, nums=nums))
    return out


def say_more(texts) -> dict:
    """Respellings for the voice that the cut's own (narration.SAY) lack: a number with a thousands separator is said
    in words, because the phonemizer reads its comma as a pause ('122, 880')."""
    out = {}
    for t in texts:
        for tok in _BIG.findall(t):
            w = _word(int(tok.replace(",", "")))
            out[tok] = w.replace(" and ", " ").replace(",", "")
    return out


def check_numbers(quiet: bool = False) -> list:
    """Every line rendered from numbers(): a figure in a line that no placeholder produced is a typed-in number, and
    fails. So does a claim that the numbers don't bear out, and a recorded line whose text is no longer the rendered
    one (speak it again). Returns the rows; raises SystemExit on a mismatch."""
    rows, bad = [], []
    rec = _record()
    for ln in lines():
        shown = {s for s, _, f in ln["nums"]}
        for s, path, f in ln["nums"]:
            rows.append(dict(id=ln["id"], says=s, path=path, fmt=f, ok=s in ln["text"]))
        for fig in _FIG.findall(ln["text"]):
            if fig not in shown:
                rows.append(dict(id=ln["id"], says=fig, path=None, fmt=None, ok=False))
        if re.search(r"\d", _PH.sub("", ln["template"])):
            rows.append(dict(id=ln["id"], says="a digit outside a placeholder", path=None, fmt=None, ok=False))
        have = rec.get("lines", {}).get(ln["id"])
        if have is not None and have.get("text") != ln["text"]:
            rows.append(dict(id=ln["id"], says="recorded text differs: speak it again", path=None, fmt=None, ok=False))
    bad = [r for r in rows if not r["ok"]]
    cl = claims()
    wrong = [c for c, ok in cl if not ok]
    if not quiet:
        for r in rows:
            print(f"{'ok ' if r['ok'] else 'BAD'} {r['id']:6s} says {r['says']:10s} <- {r['path']} ({r['fmt']})")
        for c, ok in cl:
            print(f"{'ok ' if ok else 'BAD'} claim: {c}")
    if bad or wrong:
        raise SystemExit(f"{len(bad)} spoken numbers and {len(wrong)} claims don't hold against numbers()")
    if not quiet:
        print(f"{len(rows)} spoken numbers and {len(cl)} claims, all as numbers() has them")
    return rows


# ================================================================================================== the timing
CPS = 14.5                      # characters a second, for a line not recorded yet (the voice at 0.96 speed)
LEAD = {"changes": 0.9, "counters": 0.9, "atomizer": 0.9, "notes": 1.0}     # the first line's start
GAP = 0.7                       # silence between two lines of a segment
TAIL = 1.8                      # the card stays this long after its last line
ORDER = ("changes", "counters", "atomizer", "notes")


def _record() -> dict:
    p = NDIR / "lines.json"
    try:
        return json.loads(p.read_text())
    except Exception:                                   # noqa: BLE001  (not spoken yet)
        return {"lines": {}}


@functools.lru_cache(maxsize=1)
def timing() -> dict:
    """{"lines": {id: {seg, t0, t1, text}}, "dur": {segment: seconds}}: each line's start and end in its segment.
    Lengths are the recordings' (narration_intro/lines.json), or an estimate from the text until a line is spoken."""
    rec = _record().get("lines", {})
    out, dur = {}, {}
    free = {}
    for ln in raw_lines():
        seg = ln["seg"]
        have = rec.get(ln["id"])
        text = have["text"] if have else _PH.sub("0", ln["text"])
        secs = float(have["seconds"]) if have else len(text) / CPS
        t0 = LEAD[seg] if seg not in free else free[seg] + GAP + float(ln.get("gap", 0.0))
        t0 = round(max(t0, float(ln.get("at", 0.0))), 2)
        out[ln["id"]] = dict(seg=seg, t0=t0, t1=round(t0 + secs, 2), text=text, recorded=bool(have))
        free[seg] = t0 + secs
    for seg in ORDER:
        dur[seg] = math.ceil((free.get(seg, 6.0) + TAIL) * 10.0) / 10.0
    return dict(lines=out, dur=dur)


def cue(line_id: str, phrase: str | None = None, lead: float = 0.25) -> float:
    """Seconds into its segment at which a line starts, or at which it reaches `phrase` (by the phrase's place in
    the text, a little early), so a card's parts follow the voice."""
    ln = timing()["lines"].get(line_id)
    if ln is None:
        return 0.0
    if not phrase:
        return ln["t0"]
    i = ln["text"].find(phrase)
    if i < 0:
        return ln["t0"]
    return max(ln["t0"], ln["t0"] + (ln["t1"] - ln["t0"]) * i / max(1, len(ln["text"])) - lead)


def K(t: float, line_id: str, phrase: str | None = None, dur: float = 0.6) -> float:
    """0 to 1 as a part appears, from the moment its line (or its phrase in it) is reached."""
    t0 = cue(line_id, phrase)
    return St.ramp(t, t0, t0 + dur)


# ================================================================================================== drawing
def _new() -> tuple:
    im = Image.new("RGB", (W, H), St.BG)
    return im, ImageDraw.Draw(im)


def _para(d, x, y, text, f, fill, width, lh, max_lines=None, anchor="la") -> float:
    """Wrapped text from (x, y); returns the y under it."""
    ls = St.wrap(text, f, width)
    if max_lines:
        ls = ls[:max_lines]
    for i, ln in enumerate(ls):
        d.text((x, y + i * lh), ln, font=f, fill=fill, anchor=anchor)
    return y + len(ls) * lh


def _pill(d, x, y, text, k=1.0, col=St.INK, bg=St.BG, size=16, right=False, fill=None) -> int:
    """A small outlined label (a tag); returns its width. right: x is its right edge."""
    f = St.font(size, bold=True)
    w, h = St.text_w(f, text) + px(26), px(size * 1.95)
    if right:
        x -= w
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, outline=St.mix(bg, col, k), width=px(2),
                        fill=fill)
    d.text((x + w / 2, y + h / 2), text, font=f, fill=St.mix(bg, col, k), anchor="mm")
    return w


def _title(d, text, sub=None, tag="SIMULATED"):
    d.text((px(80), px(44)), text, font=St.font(44, bold=True), fill=St.INK)
    if sub:
        _para(d, px(80), px(112), sub, St.font(25), St.INK2, px(1560), px(35), max_lines=2)
    if tag:
        _pill(d, px(1840), px(54), tag, col=St.INK2, right=True)


def _panel(d, box, k=1.0):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0, x1, y1), radius=px(16), fill=St.mix(St.BG, St.SURF, k),
                        outline=St.mix(St.BG, St.RULE, k), width=px(1))


def _on(kp: float):
    """Colours for what stands on a panel that is itself fading in with kp: c(colour, k) is the colour at k over
    the panel as it is now, and never ahead of the panel (so nothing on it shows before it does)."""
    bg = St.mix(St.BG, St.SURF, kp)

    def c(col, k=1.0):
        return St.mix(bg, col, min(k, kp))
    c.bg = bg
    return c


def _fill(s: str) -> str:
    n = _n()
    return s.format(money_al=St.money(n["money"]["flaime_al"]), money_cu=St.money(n["money"]["onr_cu"]),
                    room_lo=f"{n['room']['lo']:.0f}", room_hi=f"{n['room']['hi']:.0f}",
                    room_run=f"{n['room']['run_day']:.0f}", used_days=f"{n['used']['rule_days']:.0f}",
                    meeting_day=n["decisions"]["meeting_day"], signoff=f"${n['decisions']['signoff_usd']:,.0f}",
                    manual_week=f"{n['atomizer']['manual_week']:d}", hpc_day=f"{n['hpc']['per_day']:,.0f}",
                    hpc_cores=f"{n['hpc']['cores']:d}")


def _years() -> str:
    return _word(_n()["horizon_years"])


def _seed_words() -> str:
    r = _n()["replay"]
    pol = r["policy"]["flaime_al"]
    return f"seed {r['seed']} of {r['n_seeds']}, {pol} in the stocked automated lab"


# ===================================================================================== what the round changed
def changes_items() -> list:
    return CHANGES.get(D.ROUND, CHANGES[5])


def changes_frame(t: float) -> np.ndarray:
    n = _n()
    im, d = _new()
    _title(d, f"Round {n['round']}: {_years()} years from the day the money arrives",
           "What changed in the twin since the last cut. Everything is simulated, and every lead time, price and "
           "decision window is a stand-in.")
    items = changes_items()
    half = (len(items) + 1) // 2
    y_last = px(226)
    for i, (head, body, (lid, phrase)) in enumerate(items):
        col, row = (0, i) if i < half else (1, i - half)
        x, y = px(80 + 920 * col), px(226 + 186 * row)
        k = K(t, lid, phrase)
        d.rounded_rectangle((x, y + px(9), x + px(16), y + px(25)), radius=px(4), fill=St.mix(St.BG, St.INK2, k))
        d.text((x + px(36), y), _fill(head), font=St.font(28, bold=True), fill=St.mix(St.BG, St.INK, k))
        yy = _para(d, x + px(36), y + px(44), _fill(body), St.font(21), St.mix(St.BG, St.INK2, k), px(800), px(30))
        if col == 1:
            y_last = max(y_last, yy)
    ks = K(t, "chg2", "Every lead time")
    x0, y0 = px(1000), max(y_last + px(34), px(226 + 186 * (len(items) - half)))
    d.rounded_rectangle((x0, y0, px(1840), y0 + px(136)), radius=px(14), outline=St.mix(St.BG, St.RULE, ks),
                        width=px(2))
    _pill(d, x0 + px(22), y0 + px(18), "STAND-INS", ks, col=St.INK)
    _para(d, x0 + px(22), y0 + px(60), "No vendor has given a lead time, and no used-equipment price or risk has "
          "been quoted.", St.font(21), St.mix(St.BG, St.INK2, ks), px(800), px(30))
    d.text((px(80), px(1006)), f"Sources: twin/round{n['round']}.py (ROOM_DAYS, USED, DECISIONS, ATOM_MANUAL, HPC), "
           f"notes/twin_round{n['round']}.md, and the replayed run's own row ({_seed_words()}).",
           font=St.font(17), fill=St.INK2)
    return np.asarray(im)


# ===================================================================================== the counters, and the plots
def _stage_rows() -> list:
    return [("designed", "computed on the HPC", "designed_hpc", False),
            ("seen by the policy", "", "seen", False),
            ("powder lots made", "", "lots_made", True),
            ("alloys made", "", "alloys_made", True),
            ("alloys printed or deposited", "", "alloys_printed", True),
            ("alloys tested", "the full chain", "alloys_tested", True)]


def _count(v: float) -> str:
    v = float(v)
    if v >= 1e6:
        return f"{v / 1e6:.1f} million"
    return f"{v:,.0f}"


def _counters_card(t: float) -> np.ndarray:
    n = _n()
    cr, ca = n["counters"]["run"], n["counters"]["arm"]
    hp = n["hpc"]
    im, d = _new()
    _title(d, "Three counters, three meanings",
           "They run through the replay for both campaigns. On the right, the replayed run's own totals at the end "
           f"of its {_years()} years.")
    # ---- left: the three words
    x = px(80)
    k1 = K(t, "cnt1", "Designed means")
    d.text((x, px(206)), "Designed", font=St.font(36, bold=True), fill=St.mix(St.BG, St.INK, k1))
    _para(d, x, px(258), "Computed candidates: an open-CALPHAD stream on the HPC, at full capacity and outside the "
          "experiments' cost.", St.font(22), St.mix(St.BG, St.INK2, k1), px(820), px(31))
    t1b = cue("cnt1", "a stream on the HPC")
    k1b = St.ramp(t, t1b, t1b + 0.6)
    d.text((x, px(332)), f"{hp['per_day']:,.0f} a day", font=St.font(50, bold=True), fill=St.mix(St.BG, St.INK, k1b))
    k1c = St.ramp(t, t1b + 1.2, t1b + 1.8)
    d.text((x, px(402)), f"{hp['evaluated_m']['flaime_al']:.1f} million per campaign in {_years()} years, on a "
           f"stand-in allocation of {hp['cores']} cores", font=St.font(21), fill=St.mix(St.BG, St.INK2, k1c))
    k1d = K(t, "cnt1", "The policy sees")
    d.text((x, px(434)), f"The policy sees {hp['add_per_day']} new ones a day, and keeps the newest {hp['keep']} "
           "in view", font=St.font(21), fill=St.mix(St.BG, St.INK2, k1d))
    k2 = K(t, "cnt2")
    d.text((x, px(508)), "Made", font=St.font(36, bold=True), fill=St.mix(St.BG, St.INK, k2))
    _para(d, x, px(560), "Powder lots, or alloys made: an alloy counts once, however many lots it has.",
          St.font(22), St.mix(St.BG, St.INK2, k2), px(820), px(31))
    k3 = K(t, "cnt2", "Tested means")
    d.text((x, px(634)), "Tested", font=St.font(36, bold=True), fill=St.mix(St.BG, St.INK, k3))
    _para(d, x, px(686), "Alloys through the full chain: aluminium's tensile test; copper's tensile test and "
          f"{n['immersion_days']:.0f}-day immersion on a large deposit.", St.font(22), St.mix(St.BG, St.INK2, k3),
          px(820), px(31))
    # ---- right: the replayed run
    box = (px(960), px(202), px(1840), px(846))
    kp = K(t, "cnt1", "Designed means")
    _panel(d, box, kp)
    cp = _on(kp)
    bx, by = box[0] + px(28), box[1]
    d.text((bx, by + px(20)), "The replayed run", font=St.font(26, bold=True), fill=cp(St.INK, kp))
    d.text((bx, by + px(58)), f"{_seed_words()}; in brackets, the arm's mean over its {n['counters']['n_seeds']} "
           "seeds", font=St.font(17), fill=cp(St.INK2, kp))
    cx = {"flaime_al": box[0] + px(330), "onr_cu": box[0] + px(606)}
    bar_w = px(120)
    for c in D.CAMPAIGNS:
        d.rounded_rectangle((cx[c], by + px(106), cx[c] + px(16), by + px(122)), radius=px(4),
                            fill=cp(St.CAMP[c], kp))
        d.text((cx[c] + px(26), by + px(101)), CAMP_WORD[c], font=St.font(21, bold=True),
               fill=cp(St.INK, kp))
    vmax = max(cr[c][key] for c in D.CAMPAIGNS for _, _, key, bar in _stage_rows() if bar)
    kb = K(t, "cnt2", dur=0.8)
    cues = {"designed_hpc": k1c, "seen": K(t, "cnt1", "The policy sees"),
            "lots_made": K(t, "cnt2"), "alloys_made": K(t, "cnt2"), "alloys_printed": K(t, "cnt2", "Tested means"),
            "alloys_tested": K(t, "cnt2", "Tested means")}
    for i, (lab, sub, key, bar) in enumerate(_stage_rows()):
        y = by + px(150 + 74 * i)
        kr = cues[key]
        d.line([(bx, y - px(12)), (box[2] - px(28), y - px(12))], fill=cp(St.GRID, kp), width=px(1))
        d.text((bx, y + px(4)), lab, font=St.font(20), fill=cp(St.INK, kr))
        if sub:
            d.text((bx, y + px(32)), sub, font=St.font(15), fill=cp(St.INK2, kr))
        for c in D.CAMPAIGNS:
            v, m = cr[c][key], ca[c][key]
            x0 = cx[c]
            if bar:
                kv = kr
                wv = max(px(3), int(round(bar_w * v / vmax * St.ease(kr))))
                d.rounded_rectangle((x0, y + px(10), x0 + wv, y + px(26)), radius=px(4),
                                    fill=cp(St.CAMP[c], kr))
                d.rectangle((x0, y + px(10), x0 + min(wv, px(4)), y + px(26)), fill=cp(St.CAMP[c], kr))
                tx = x0 + int(round(bar_w * v / vmax)) + px(12)
                d.text((tx, y + px(3)), _count(v), font=St.font(24, bold=True), fill=cp(St.INK, kv))
                tw = St.text_w(St.font(24, bold=True), _count(v))
                d.text((tx + tw + px(8), y + px(9)), f"({_count(m)})", font=St.font(16),
                       fill=cp(St.INK2, kv))
            else:
                d.text((x0, y + px(3)), _count(v), font=St.font(24, bold=True), fill=cp(St.INK, kr))
                if key != "designed_hpc":
                    tw = St.text_w(St.font(24, bold=True), _count(v))
                    d.text((x0 + tw + px(8), y + px(9)), f"({_count(m)})", font=St.font(16),
                           fill=cp(St.INK2, kr))
    if cr["onr_cu"]["alloys_made"] > cr["onr_cu"]["lots_made"]:
        d.line([(bx, box[3] - px(52)), (box[2] - px(28), box[3] - px(52))], fill=cp(St.GRID, kp),
               width=px(1))
        d.text((bx, box[3] - px(38)), "Copper's alloys made outnumber its powder lots: most are blends of powders "
               "already made.", font=St.font(16), fill=cp(St.INK2, kb))
    # ---- the banner
    ke = K(t, "cnt3", "Early stopping")
    y0 = px(882)
    d.rounded_rectangle((px(80), y0, px(1840), y0 + px(104)), radius=px(16), fill=St.mix(St.BG, St.SURF, ke),
                        outline=St.mix(St.BG, St.INK2, ke), width=px(2))
    d.text((px(960), y0 + px(52)), "Early stopping: only promising alloys finish every step.",
           font=St.font(34, bold=True), fill=St.mix(St.BG, St.INK, ke), anchor="mm")
    return np.asarray(im)


def _step(points: list, x_end: float) -> list:
    """A best-so-far curve as a step line from (0, 0) to x_end."""
    out, best = [(0.0, 0.0)], 0.0
    for x, y in points:
        if x > x_end:
            break
        if y > best:
            out += [(x, best), (x, y)]
            best = y
    out.append((x_end, best))
    return out


def _spend_total(cur: dict, x_end: float) -> list:
    """Both campaigns' cumulative spend, summed, at each of the first campaign's days up to x_end."""
    xs = sorted({p[0] for c in cur.values() for p in c["spend"] if p[0] <= x_end} | {x_end})
    out = []
    for x in xs:
        tot = 0.0
        for c in cur.values():
            sp = np.array(c["spend"], float).reshape(-1, 2)
            tot += float(np.interp(x, sp[:, 0], sp[:, 1])) if len(sp) else 0.0
        out.append((x, tot))
    return out


def _plot(d, box, xr, yr, xt, yt, yfmt, c=None):
    """Recessive axes on a panel: hairline grid at the y ticks, tick labels in the secondary ink. Returns the two
    data -> pixel maps. c: the panel's colours (_on)."""
    x0, y0, x1, y1 = box
    c = c or _on(1.0)

    def fx(v):
        return x0 + (x1 - x0) * (v - xr[0]) / (xr[1] - xr[0])

    def fy(v):
        return y1 - (y1 - y0) * (v - yr[0]) / (yr[1] - yr[0])
    for v in yt:
        d.line([(x0, fy(v)), (x1, fy(v))], fill=c(St.GRID), width=px(1))
        d.text((x0 - px(10), fy(v)), yfmt(v), font=St.font(16), fill=c(St.INK2), anchor="rm")
    d.line([(x0, y1), (x1, y1)], fill=c(St.RULE), width=px(1))
    for v in xt:
        d.line([(fx(v), y1), (fx(v), y1 + px(6))], fill=c(St.RULE), width=px(1))
        d.text((fx(v), y1 + px(10)), f"{v:.0f}", font=St.font(16), fill=c(St.INK2), anchor="ma")
    d.text(((x0 + x1) / 2, y1 + px(36)), "days since the money arrived", font=St.font(16),
           fill=c(St.INK2), anchor="ma")
    return fx, fy


def _key(d, x, y, kind, col, label, k=1.0, c=None) -> int:
    """One legend entry: a sample of the line as it is drawn, then its name in a text ink. Returns the x after it."""
    c = c or _on(1.0)
    yy = y + px(11)
    if kind == "dash":
        St.dashed_line(d, [(x, yy), (x + px(46), yy)], fill=c(col, k), width=px(3), dash=px(10),
                       gap=px(7))
    elif kind == "dot":
        St.dashed_line(d, [(x, yy), (x + px(46), yy)], fill=c(col, k), width=px(2), dash=px(3),
                       gap=px(6))
    else:
        d.line([(x, yy), (x + px(46), yy)], fill=c(col, k), width=px(4))
    f = St.font(17)
    d.text((x + px(56), y), label, font=f, fill=c(St.INK, k))
    return x + px(56) + St.text_w(f, label) + px(30)


def _plots_card(t: float) -> np.ndarray:
    n = _n()
    rp = n["replay"]
    camp = "flaime_al"
    X = float(n["horizon_days"])
    im, d = _new()
    _title(d, "Reading the replay's plots",
           f"The replayed run: seed {rp['seed']} of {rp['n_seeds']}, {rp['policy'][camp]} in both labs, both "
           "stocked. Everything is simulated.")
    xt = [v for v in range(0, int(X) + 1, 100)]
    # ---- left: best new alloy so far
    box = (px(80), px(202), px(1000), px(812))
    _panel(d, box)
    d.text((box[0] + px(28), box[1] + px(18)), f"Best new alloy tested so far: {CAMP_WORD[camp]}",
           font=St.font(25, bold=True), fill=St.INK)
    cu = "onr_cu"
    d.text((box[0] + px(28), box[1] + px(54)), "true utility on the twin's synthetic alloy model, 0 to 1 (copper's "
           f"two targets: {n['targets']['T1'][cu]:.2f} and {n['targets']['T2'][cu]:.2f})",
           font=St.font(17), fill=St.INK2)
    ks = K(t, "cnt4", "the solid curve")
    kd = K(t, "cnt4", "the dashed curve")
    kt = K(t, "cnt4", "The dotted lines")
    kt2 = K(t, "cnt4", "two targets")
    xk = _key(d, box[0] + px(28), box[1] + px(88), "solid", St.CAMP[camp], "automated lab", ks)
    xk = _key(d, xk, box[1] + px(88), "dash", St.BASE, "conventional lab, same seed and policy", kd)
    _key(d, xk, box[1] + px(88), "dot", St.TARGET, "targets", kt)
    area = (box[0] + px(78), box[1] + px(140), box[2] - px(36), box[3] - px(72))
    best_a = _step(rp["curves"]["auto"][camp]["best"], X)
    best_c = _step(rp["curves"]["conv"][camp]["best"], X)
    top = max(0.8, math.ceil(max(p[1] for p in best_a + best_c) * 10.0 + 0.5) / 10.0)
    fx, fy = _plot(d, area, (0.0, X), (0.0, top), xt, [v / 10.0 for v in range(0, int(top * 10) + 1, 2)],
                   lambda v: f"{v:.1f}")
    for tn, kk, words in (("T1", kt, "the best existing alloy on this synthetic benchmark"),
                          ("T2", kt2, "the halfway target")):
        v = n["targets"][tn][camp]
        St.dashed_line(d, [(area[0], fy(v)), (area[2], fy(v))], fill=St.mix(St.SURF, St.TARGET, kk), width=px(2),
                       dash=px(3), gap=px(6))
        d.text((area[2] - px(6), fy(v) - px(8)), f"{words}: {v:.2f}", font=St.font(17),
               fill=St.mix(St.SURF, St.INK, kk), anchor="rs")
    St.dashed_line(d, [(fx(a), fy(b)) for a, b in best_c], fill=St.mix(St.SURF, St.BASE, kd), width=px(3),
                   dash=px(10), gap=px(7))
    d.line([(fx(a), fy(b)) for a, b in best_a], fill=St.mix(St.SURF, St.CAMP[camp], ks), width=px(4), joint="curve")
    # ---- right: cumulative spend per lab
    box2 = (px(1040), px(202), px(1840), px(812))
    k5 = K(t, "cnt5")
    _panel(d, box2, k5)
    c5 = _on(k5)
    d.text((box2[0] + px(28), box2[1] + px(18)), "Campaign money spent so far, in each lab",
           font=St.font(25, bold=True), fill=c5(St.INK))
    d.text((box2[0] + px(28), box2[1] + px(54)), "cumulative, both campaigns; equipment and fixed costs are not in it",
           font=St.font(17), fill=c5(St.INK2))
    xk = _key(d, box2[0] + px(28), box2[1] + px(88), "solid", St.INK, "automated lab", k5, c5)
    _key(d, xk, box2[1] + px(88), "dash", St.BASE, "conventional lab", k5, c5)
    area2 = (box2[0] + px(92), box2[1] + px(140), box2[2] - px(36), box2[3] - px(72))
    sp_a = _spend_total(rp["curves"]["auto"], X)
    sp_c = _spend_total(rp["curves"]["conv"], X)
    total = float(n["money"]["total"])
    ymax = max(max(p[1] for p in sp_a + sp_c), total if math.isfinite(total) else 0.0)
    step = 100e3 if ymax > 250e3 else 50e3
    ytop = math.ceil(ymax / step + 0.25) * step
    fx2, fy2 = _plot(d, area2, (0.0, X), (0.0, ytop), xt, [v * step for v in range(0, int(ytop / step) + 1)],
                     lambda v: "$0" if v == 0 else f"${v / 1e3:.0f}k", c5)
    if n["money"]["same_in_both_labs"] and math.isfinite(total):
        d.line([(area2[0], fy2(total)), (area2[2], fy2(total))], fill=c5(St.RULE), width=px(1))
        d.text((area2[2] - px(6), fy2(total) - px(8)), f"all the money a lab has for both campaigns: {St.money(total)}",
               font=St.font(16), fill=c5(St.INK2), anchor="rs")
    St.dashed_line(d, [(fx2(a), fy2(b)) for a, b in sp_c], fill=c5(St.BASE), width=px(3),
                   dash=px(10), gap=px(7))
    d.line([(fx2(a), fy2(b)) for a, b in sp_a], fill=c5(St.INK), width=px(4), joint="curve")
    # ---- the strip: why flat
    kf = K(t, "cnt5", "And when best so far")
    y0 = px(846)
    d.rounded_rectangle((px(80), y0, px(1840), y0 + px(128)), radius=px(16), fill=St.mix(St.BG, St.SURF, kf),
                        outline=St.mix(St.BG, St.RULE, kf), width=px(1))
    cf = _on(kf)
    d.text((px(108), y0 + px(22)), "When best so far is flat, the replay says why", font=St.font(26, bold=True),
           fill=cf(St.INK))
    d.text((px(108), y0 + px(66)), "from the run's own idle-cause report (its daily log)", font=St.font(17),
           fill=cf(St.INK2))
    xp = px(840)
    t_why = cue("cnt5", "the replay says why")
    for i, w in enumerate(n["flat"]["screen"]):
        kk = St.ramp(t, t_why + 0.35 * i, t_why + 0.35 * i + 0.5)
        xp += _pill(d, xp, y0 + px(44), w, min(kk, kf), col=St.INK, bg=cf.bg, size=19) + px(16)
    return np.asarray(im)


def counters_frame(t: float) -> np.ndarray:
    tb = cue("cnt4") - 0.9                              # the plots' card takes over just before its first line
    if t <= tb:
        return _counters_card(t)
    if t >= tb + 0.6:
        return _plots_card(t)
    k = St.ease((t - tb) / 0.6)
    a, b = _counters_card(t).astype(np.float32), _plots_card(t).astype(np.float32)
    return (a * (1 - k) + b * k).astype(np.uint8)


# ===================================================================================== the atomizer's design target
def _date_words(a: str, b: str) -> str:
    da, db = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return f"{da.day} {da:%B} to {db.day} {db:%B} {db.year}"


def _big(d, x, y, big, unit, sub, k, width, c=None):
    """A big number with its unit beside it and a line or two under it; returns the y under it. c: the colours of
    the panel it stands on (_on)."""
    c = c or _on(1.0)
    f = St.font(56, bold=True)
    d.text((x, y), big, font=f, fill=c(St.INK, k))
    if unit:
        d.text((x + St.text_w(f, big) + px(14), y + px(27)), unit, font=St.font(25, bold=True), fill=c(St.INK, k))
    return _para(d, x, y + px(76), sub, St.font(20), c(St.INK2, k), width, px(29))


def atomizer_frame(t: float) -> np.ndarray:
    n = _n()
    at = n["atomizer"]
    cru, rec, run = at["crucibles"], at["record"], at["run"]
    im, d = _new()
    _title(d, "The atomizer: a design target, next to the lab's record",
           "Once its cell is integrated, the automated lab's simulated atomizer runs at a design target, not at a "
           "rate the lab has demonstrated.")
    Y0, Y1 = px(206), px(870)
    P = [(px(80), px(700)), (px(730), px(1290)), (px(1320), px(1840))]
    # ---- 1: the design target
    k0 = K(t, "atm1", "Once its cell")
    _panel(d, (P[0][0], Y0, P[0][1], Y1), k0)
    c0 = _on(k0)
    x = P[0][0] + px(28)
    kt = max(0.45 * k0, K(t, "atm1", "That is a design target"))
    _pill(d, x, Y0 + px(22), "DESIGN TARGET", min(kt, k0), col=St.INK, bg=c0.bg, size=18)
    d.text((x, Y0 + px(70)), "The automated lab, once its cell is integrated", font=St.font(20), fill=c0(St.INK2))
    wd = P[0][1] - P[0][0] - px(56)
    _big(d, x, Y0 + px(118), f"{at['run_h']['flaime_al']:.1f} h", "per aluminium composition",
         f"end to end, derived step by step from the lab's run records (copper: {at['run_h']['onr_cu']:.1f} h)",
         K(t, "atm1", "about"), wd, c0)
    _big(d, x, Y0 + px(298), f"{at['week_247']['flaime_al']:.0f}", "a week",
         "aluminium compositions at 24/7 (around the clock)", K(t, "atm1", ", or "), wd, c0)
    _big(d, x, Y0 + px(478), f"{cru['need_lo']} to {cru['need_hi']}", "crucibles",
         f"per alloy family, pre-coated and in rotation: each is out {cru['dry_h_lo']} to {cru['dry_h_hi']} h while "
         "its coat dries", K(t, "atm2"), wd, c0)
    # ---- 2: the lab's record
    k2 = K(t, "atm2", "and the lab has")
    _panel(d, (P[1][0], Y0, P[1][1], Y1), k2)
    c2 = _on(k2)
    x = P[1][0] + px(28)
    _pill(d, x, Y0 + px(22), "THE LAB'S RECORD", k2, col=St.INK, bg=c2.bg, size=18)
    d.text((x, Y0 + px(70)), "The lab's own atomizer so far, run by people", font=St.font(20), fill=c2(St.INK2))
    wd = P[1][1] - P[1][0] - px(56)
    kr = K(t, "atm2", "The lab's record")
    _big(d, x, Y0 + px(118), f"{rec['runs']}", "runs",
         f"in {rec['days']} days, {_date_words(rec['first'], rec['last'])}", kr, wd, c2)
    _big(d, x, Y0 + px(298), f"{rec['per_week']:.1f}", "a week", f"over those {rec['days']} days",
         K(t, "atm2", "about"), wd, c2)
    _big(d, x, Y0 + px(478), f"{cru['now']}", "crucible",
         f"per alloy family now, which allows at most {cru['runs_day_now']} run a day", k2, wd, c2)
    # ---- 3: the assumed manual rate
    k3 = K(t, "atm2", "Before the cell")
    _panel(d, (P[2][0], Y0, P[2][1], Y1), k3)
    c3 = _on(k3)
    x = P[2][0] + px(28)
    _pill(d, x, Y0 + px(22), "ASSUMED", k3, col=St.INK, bg=c3.bg, size=18)
    wd = P[2][1] - P[2][0] - px(56)
    _para(d, x, Y0 + px(70), "The conventional lab, and the automated lab before its cell", St.font(20),
          c3(St.INK2), wd, px(29))
    al, cu = at["al_days"], at["cu_days"]
    _big(d, x, Y0 + px(298), f"{at['manual_week']}", "a week",
         f"at most: {at['starts_day']} attended starts a day on {at['days_week']} days (aluminium {al[0]} to "
         f"{al[-1]}, copper {cu[0]})", k3, wd, c3)
    # ---- the replayed run, and the sources
    kf = K(t, "atm2", "The lab's record")
    d.text((px(80), px(900)), f"In the replayed run: {run['runs']:,} simulated atomizer runs in {_years()} years "
           f"({run['al']:,} aluminium, {run['cu']:,} copper). The design cycle applies from day "
           f"{run['switch_day']:.0f}, when its cell is integrated.", font=St.font(21),
           fill=St.mix(St.BG, St.INK2, kf))
    _para(d, px(80), px(950), f"Sources: twin/round{n['round']}.py (ATOM_RUN_H, the charge plan's hours; "
          f"ATOM_MANUAL); notes/twin_round{n['round']}.md, section 2 (the cycle's derivation and the crucibles); the "
          "lab's atomizer log, digital-alloy-lab atomizer-runs/runs.csv at 8320f13 (the record).", St.font(17),
          St.INK2, px(1760), px(26))
    return np.asarray(im)


# ===================================================================================== the closing notes
def footage_items() -> list:
    """The atomizer clips the cut uses, each with its run and alloy: out/twin<ROUND>/video/footage_used.json, a list
    of {"run", "alloy", "date"} the cut writes (twin/video/cut5.py). Until it exists the card says where the names
    are."""
    p = D.VID / "footage_used.json"
    try:
        js = json.loads(p.read_text())
        out = []
        for f in js if isinstance(js, list) else js.get("clips", []):
            bits = [str(f[k]) for k in ("alloy", "date") if f.get(k)]
            out.append(f"run {f['run']}" + (f" ({', '.join(bits)})" if bits else ""))
        if out:
            return out
    except Exception:                                   # noqa: BLE001  (not written yet)
        pass
    return []


def notes_columns() -> list:
    n = _n()
    clips = footage_items()
    foot = ("The lab's own atomizer footage: " + "; ".join(clips)) if clips else \
        "The lab's own atomizer footage: each clip's run and alloy is named on screen"
    return [
        ("Real", [
            "The lab's design and its 3-D model (PR 318), makers' published sizes",
            foot,
            "The search spaces and rules: the FLAIME and ONR proposals",
            "Published prices: USGS Mineral Commodity Summaries 2026",
        ]),
        ("Assumed, and stand-ins", [
            f"The facility window (day {n['room']['lo']:.0f} to {n['room']['hi']:.0f}) and every lead time",
            "Used-equipment prices and risks",
            "Decision windows for people, and the sign-off",
            f"The HPC allocation ({n['hpc']['cores']} cores)",
            "The atomizer's design cycle and its spare crucibles: a design target, not the lab's record",
            "The stock rule, station times, fees and capacities",
        ]),
        ("Simulated", [
            "Every alloy's properties: a synthetic truth, calibrated on reference alloys",
            "Every measurement, with modelled noise not yet calibrated on the lab's instruments",
            "Both campaigns in both labs: every booking, result and dollar",
            "The policies' choices",
        ]),
    ]


@functools.lru_cache(maxsize=1)
def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                              cwd=D.HERE).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def notes_meta() -> list:
    n = _n()
    rp = n["replay"]
    r = n["round"]
    return [f"Replayed run: {rp['events']} (seed {rp['seed']} of {rp['n_seeds']}, the arm's median seed for both "
            "campaigns)",
            f"Beside it, the conventional lab's same seed, policy and stock rule: {rp['conv_events'] or 'its row'}",
            f"Results: out/twin{r}/like{r}.json and tables.md, from the rows in out/twin{r}/runs; write-up in "
            f"notes/twin_round{r}.md and notes/twin_video.md",
            f"Code: github.com/vertical-cloud-lab/byu-vcl, vertical-lab/twin/video (commit {_commit()})",
            "Narration: a synthetic voice, Kokoro v1.0 (open weights, run locally); nobody's voice is cloned"]


def notes_frame(t: float) -> np.ndarray:
    im, d = _new()
    d.text((px(80), px(60)), "A synthetic benchmark", font=St.font(48, bold=True), fill=St.INK)
    d.text((px(80), px(128)), "What is real, what is assumed and what is simulated in this video",
           font=St.font(26), fill=St.INK2)
    cues = [K(t, "note1", "Everything here"), K(t, "note1", "The facility window"), K(t, "note1", "Everything here")]
    order = {"Real": 0.0, "Assumed, and stand-ins": cues[1], "Simulated": cues[2]}
    f = St.font(21)
    for i, (head, items) in enumerate(notes_columns()):
        x = px(80 + 600 * i)
        k = St.ramp(t, 0.3, 1.0) if head == "Real" else order[head]
        d.text((x, px(206)), head, font=St.font(31, bold=True), fill=St.mix(St.BG, St.INK, k))
        y = px(262)
        for it in items:
            for j, ln in enumerate(St.wrap(it, f, px(520))):
                d.text((x + (px(22) if j else 0), y), ("- " if j == 0 else "") + ln, font=f,
                       fill=St.mix(St.BG, St.INK2, k))
                y += px(31)
            y += px(13)
    y = px(800)
    d.line([(px(80), y - px(22)), (px(1840), y - px(22))], fill=St.RULE, width=px(1))
    for ln in notes_meta():
        y = _para(d, px(80), y, ln, St.font(20), St.INK2, px(1760), px(31)) + px(2)
    d.text((px(80), px(1006)), "It shows how two lab designs and their policies interact in a model, not what the "
           "real lab will find.", font=St.font(21, bold=True), fill=St.mix(St.BG, St.INK, K(t, "note1", "It shows")))
    return np.asarray(im)


# ================================================================================================== for the cut
FRAMES = {"changes": changes_frame, "counters": counters_frame, "atomizer": atomizer_frame, "notes": notes_frame}
TITLES = {"changes": f"Round {D.ROUND}: what changed in the twin",
          "counters": "The counters, and how to read the replay's plots",
          "atomizer": "The atomizer: a design target, next to the lab's record",
          "notes": "Notes: real, assumed, simulated"}
SEGMENTS = [(name, float(timing()["dur"][name]), FRAMES[name], TITLES[name]) for name in ORDER]
CHANGES_DURATION, COUNTERS_DURATION, ATOMIZER_DURATION, NOTES_DURATION = (s[1] for s in SEGMENTS)


def captions(name: str) -> list:
    """[(t0, t1, what is on screen)] for a segment: each card part from the moment it appears to the segment's end
    (the cards keep what they have shown). For the plan table beside the narration."""
    tm = timing()
    end = tm["dur"][name]
    if name == "changes":
        out = [(round(cue(lid, ph), 2), end, _fill(head)) for head, _, (lid, ph) in changes_items()]
        return out + [(round(cue("chg2", "Every lead time"), 2), end, "stand-ins: no vendor lead time or used price "
                                                                      "has been quoted")]
    if name == "counters":
        tb = round(cue("cnt4") - 0.9, 2)
        return [(round(cue("cnt1", "Designed means"), 2), tb, "Designed: computed candidates on the HPC, a day and "
                                                              "per campaign; the replayed run's totals"),
                (round(cue("cnt2"), 2), tb, "Made: powder lots, or alloys made; Tested: alloys through the full "
                                            "chain; the replayed run's bars"),
                (round(cue("cnt3", "Early stopping"), 2), tb, "Early stopping: only promising alloys finish every "
                                                              "step."),
                (tb, end, "best new alloy tested so far: automated lab solid, conventional lab dashed, the two "
                          "targets dotted"),
                (round(cue("cnt5"), 2), end, "campaign money spent so far, in each lab"),
                (round(cue("cnt5", "And when best so far"), 2), end, "when best so far is flat, the replay says why")]
    if name == "atomizer":
        return [(round(cue("atm1", "Once its cell"), 2), end, "DESIGN TARGET: hours per aluminium composition, runs "
                                                               "a week at 24/7"),
                (round(cue("atm2"), 2), end, "crucibles per alloy family: needed, and what the lab has"),
                (round(cue("atm2", "The lab's record"), 2), end, "THE LAB'S RECORD: runs a week, runs and days"),
                (round(cue("atm2", "Before the cell"), 2), end, "ASSUMED: the manual rate a week")]
    if name == "notes":
        return [(0.3, end, "Real"), (round(cue("note1", "Everything here"), 2), end, "Simulated"),
                (round(cue("note1", "The facility window"), 2), end, "Assumed, and stand-ins"),
                (0.0, end, "the replayed run's file, the results' files, the commit, the voice")]
    raise KeyError(name)


def narration_lines(name: str) -> list:
    """A segment's lines for the cut's track: [dict(id, t (seconds into the segment), end, text, flac, src)]. The text
    is the recorded one (narration_intro/lines.json); a line not spoken yet has flac None."""
    tm = timing()["lines"]
    src = {ln["id"]: ln.get("src", "") for ln in raw_lines()}
    out = []
    for lid, v in tm.items():
        if v["seg"] != name:
            continue
        p = NDIR / f"{lid}.flac"
        out.append(dict(id=lid, t=v["t0"], end=v["t1"], text=v["text"], flac=p if (v["recorded"] and p.exists())
                        else None, src=src.get(lid, "")))
    return out


# ================================================================================================== the voice
def _configure():
    """This script on the cut's voice and machinery (narration.py), with its audio in narration_intro/."""
    from . import narration as N
    ls = lines()
    NDIR.mkdir(parents=True, exist_ok=True)
    script = NDIR / "script.json"
    script.write_text(json.dumps(dict(
        about="narration5_intro.json rendered from numbers() (twin/video/figs5_intro.py): what the voice says and the "
              "subtitles show; nums: what filled each placeholder [shown, path in numbers_intro.json, format]",
        lines=[dict(id=ln["id"], seg=ln["seg"], text=ln["text"], src=ln.get("src", ""), nums=ln["nums"])
               for ln in ls]), indent=1, ensure_ascii=False) + "\n")
    N.configure(script=script, ndir=NDIR, say=say_more([ln["text"] for ln in ls]))
    return N


def tts(only: set | None = None) -> dict:
    N = _configure()
    au = N.speak_all(only)
    timing.cache_clear()
    return au


def heard_back(models=("small.en",)) -> list:
    N = _configure()
    return N.check(models)


def plan() -> str:
    tm = timing()
    out = []
    for seg in ORDER:
        out.append(f"{seg}: {tm['dur'][seg]:.1f} s")
        for lid, v in tm["lines"].items():
            if v["seg"] == seg:
                out.append(f"  {v['t0']:6.2f}-{v['t1']:6.2f}  {lid:6s} {'' if v['recorded'] else '(estimate) '}"
                           f"{v['text'][:110]}")
    return "\n".join(out)


def stills(dst: Path = Path("/tmp/vid/intro"), times: dict | None = None) -> list:
    """Every card state: each segment at the end of each of its lines and at its end."""
    dst.mkdir(parents=True, exist_ok=True)
    tm = timing()
    out = []
    for name, dur, fn, _ in SEGMENTS:
        ts = (times or {}).get(name) or sorted({round(v["t1"] + 0.3, 1) for v in tm["lines"].values()
                                                if v["seg"] == name} | {round(dur - 0.1, 1)})
        for tt in ts:
            p = dst / f"{name}_{tt:05.1f}.png"
            Image.fromarray(fn(float(tt))).save(p)
            out.append(p)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "numbers":
        print(write_numbers())
        for c, ok in claims():
            print(f"{'ok ' if ok else 'BAD'} claim: {c}")
    elif cmd == "nums":
        write_numbers()
        check_numbers()
    elif cmd == "tts":
        a = tts(set(sys.argv[2:]) or None)
        print(f"{len(a)} lines, {sum(len(y) for y in a.values()) / 24000 / 60:.2f} min of speech in {NDIR}")
        print(plan())
    elif cmd == "check":
        heard_back(tuple(sys.argv[2:]) or ("small.en",))
    elif cmd == "plan":
        print(plan())
    elif cmd == "stills":
        for p in stills():
            print(p)
    else:
        raise SystemExit(__doc__)

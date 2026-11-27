"""The function-network chapter with the experiments in it: each step of the two networks shown as the experiment and
the data it makes, for one alloy of each campaign (twin/video/experiments.py; notes/twin_video.md).

    python -m twin.video.experiments plan             # the segments and their times; where each line falls
    python -m twin.video.experiments stills [t ...]   # frames of the chapter at times t (s) -> /tmp/vid/chapter_<t>.png
    python -m twin.video.experiments nums             # every number the narration speaks, against facts.json
    python -m twin.video.experiments tts [id ...]     # speak the lines (Kokoro) -> out/twin3b/video/experiments/narration/
    python -m twin.video.experiments check            # the lines heard back by faster-whisper -> narration/check.json
    python -m twin.video.experiments build            # the standalone preview: experiments_preview.mp4, record.json,
                                                      # sheet.png, youtube_meta.json (TWIN_VIDEO_WORKERS, default 4)
    python -m twin.video.experiments segment KEY      # one segment alone -> experiments/segment_KEY.mp4 (no sound)

Run with TWIN_VIDEO_ROUND=3b (the alloys followed come from round 3b's replay; twin/video/exp_data.py).

The chapter replaces the build of the two networks in ``dag_anim.Dag.intro_frame`` (about 1:40 to 3:17 of round 3b's
cut) and keeps its points. Its parts, each a module of its own that another cut can use alone:

    intro         the two networks (dag_anim's cards), and how to read the labels that follow     this module
    composition   one aluminium and one copper design on the periodic table and in its space      exp_composition.py
    scheil        Scheil solidification: what the CALPHAD node computes and what the network uses exp_scheil.py
    am            the twin's stand-in for the AM Module: a laser track, the melt pool, a point     exp_am.py
    atomize       the atomizer (the lab's footage) and the powder's size distribution and yield    exp_atomize.py
    print         nine cubes at nine settings, their density and crack readings                    exp_print.py
    sem           one beam, four signals: SE, BSE, EDS, EBSD, and which the network uses           exp_sem.py
    mech          heat treatment, then the tensile test to fracture                                exp_mech.py
    corrosion     copper: the one-hour screen and the 30-day immersion with its interim readings   exp_corrosion.py
    outro         both networks at once, then collapsed to the icons the replay lights             dag_anim (its tail)

``Chapter()`` is the whole thing behind the interface the cut uses for the old one (``intro_frame(t)``, ``DURATION``,
``captions``), plus ``marks`` for the narration. To drop it into a cut: give compose.segments() ``Chapter().frame`` and
its duration in place of the Dag's, add its marks to narration.marks(), and move the lines of narration_exp.json into
the cut's script (their ``seg`` becomes the cut's segment name; the marks are already named by part).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import data as D
from . import exp_data as X
from . import exp_draw as G
from . import style as St
from .exp_draw import Canvas, Segment, lin, ramp
from .style import BG, CAMP, INK, INK2, H, W

FPS = 30
OUT = X.OUT
TMP = OUT / "parts"
SCRIPT = Path(__file__).with_name("narration_exp.json")
NDIR = OUT / "narration"
PREVIEW = OUT / "experiments_preview.mp4"
FADE = 0.35
# (key, module, class): the chapter's parts in order
PARTS = [("intro", "experiments", "Intro"), ("composition", "exp_composition", "Composition"),
         ("scheil", "exp_scheil", "Scheil"), ("am", "exp_am", "AMModule"), ("atomize", "exp_atomize", "Atomize"),
         ("print", "exp_print", "Print"), ("sem", "exp_sem", "SEM"), ("mech", "exp_mech", "Mech"),
         ("corrosion", "exp_corrosion", "Corrosion"), ("outro", "experiments", "Outro")]
ONLY = [k for k in os.environ.get("TWIN_EXP_PARTS", "").split(",") if k]     # a subset, while segments are being written
# how the voice says what the lines of this chapter add (narration.SAY / IPA are the cut's and stay as they are)
SAY_MORE = {"EBSD": "E B S D", "UTS": "U T S", "micrometres": "micrometers"}
# "a Scheil": a lone article before a respelled word is read as the letter ("ay Scheil"); "AM" as letters came
# out "uh em" after "the" (both found by reading the phonemes back)
IPA_MORE = {"a Scheil": "ɐ ʃˈaɪl", "Scheil": "ʃˈaɪl", "AM": "ˌeɪ ˈɛm"}
MORE_WORDS = {"thirty": 30, "sixty": 60, "fifteen": 15, "fourteen": 14, "hundred": 100}


def alloy_name(comp: dict, base: str, n: int | None = None) -> str:
    """Al-3.3Mn-0.8Cr-...: the additions in wt%, largest first (n: only the n largest, then '...')."""
    adds = sorted(((v, e) for e, v in comp.items() if e != base and v > 0), reverse=True)
    parts = [f"{v:.1f}{e}" if v >= 0.095 else f"{v:.2f}{e}" for v, e in adds[:n]]
    return base + "-" + "-".join(parts) + ("-..." if n and len(adds) > n else "")


# ================================================================================================ intro and outro
@lru_cache(maxsize=1)
def _dag():
    from .dag_anim import Dag
    return Dag()


class Intro(Segment):
    """The two networks, as the cut has always drawn them (dag_anim's cards and lanes), built quickly; a pulse along
    each, since each step's results feed the next; then what follows and how its labels read."""
    key = "intro"
    title = "Two campaigns, one lab: the function networks"
    DURATION = 27.0
    T_LANE = {"flaime_al": (1.0, 4.6), "onr_cu": (5.0, 9.4)}
    T_PULSE = (9.8, 14.4)
    T_LEGEND = 15.0

    def __init__(self):
        super().__init__()
        self.captions = [
            (0.6, 9.6, "Each campaign is a network of models and measurements. Each node is a step the lab runs."),
            (9.8, 14.6, "Each step's results feed the next. BOFN models every step, not just the final score."),
            (15.0, 26.6, "Next: every step as the experiment and the data it makes, for one alloy of each campaign."),
        ]
        self.marks = {"intro.lanes": self.T_LANE["flaime_al"][0], "intro.pulse": self.T_PULSE[0],
                      "intro.legend": self.T_LEGEND}
        self.sources = [("sim", "the two networks: twin/video/data.py NETWORKS (the campaigns' steps)")]
        self._legend = None

    def _n_done(self, t: float) -> tuple:
        dag = _dag()
        out, part = {}, {}
        for c in D.CAMPAIGNS:
            n = len(dag.nodes[c])
            a, b = self.T_LANE[c]
            f = lin(t, a, b) * n
            out[c] = int(f) if t >= a else -1
            part[c] = f - int(f)
        return out, part

    def _legend_img(self):
        """What follows, and how to read its labels: drawn once, in the gap between the two lanes."""
        if self._legend is None:
            from . import dag_anim as DA
            f = X.follow()
            top = DA.LANE["flaime_al"]["top"] + DA.LANE["flaime_al"]["h"] + 40
            bot = DA.LANE["onr_cu"]["label_y"] - 16
            cv = Canvas(np.zeros((H, W, 3), np.uint8))
            cv.rect((60, top, 1860, bot), fill=G.CARD_FILL, outline=G.CARD_EDGE, width=2, radius=14)
            xr = 1178
            x, y = 88, top + 16
            cv.text(x, y, "What follows: one alloy from each campaign, step by step", 26, bold=True)
            y += 46
            for c in D.CAMPAIGNS:
                a = f[c]
                base = "Al" if c == "flaime_al" else "Cu"
                cv.rect((x, y + 2, x + 7, y + 56), fill=CAMP[c], radius=3)
                cv.text(x + 20, y, f"{X.CAMP_WORD[c].capitalize()}: {alloy_name(a['composition'], base, 6)}", 22,
                        bold=True)
                what = "the halfway target" if a["target"] == "T2" else \
                    "the best existing alloy on this synthetic benchmark"
                line = f"design {a['design']} of seed {a['seed']}: it took this replayed run past {what} on day " \
                       f"{a['day']:.0f}"
                size = 19
                while size > 16 and cv.text_w(line, size, cond=True) > xr - 60 - x:
                    size -= 1
                cv.text(x + 20, y + 32, line, size, fill=INK2, cond=True)
                y += 68
            cv.text(x, y + 2, "Each is made again by the twin's own models and measured by its instrument simulators.",
                    19, fill=INK2, cond=True)
            cv.line([(xr - 30, top + 20), (xr - 30, bot - 20)], (52, 56, 64), 2)
            cv.text(xr, top + 16, "How to read the labels", 26, bold=True)
            rows = [("sim", "", "the twin's own output for that alloy"),
                    ("calc", "", "an open CALPHAD tool, an open database"),
                    ("illus", "", "a schematic, drawn to explain"),
                    ("real", "", "footage from the lab itself"),
                    ("render", "", "the lab as designed (PR 318's renders)")]
            yy = top + 62
            for kind, _, words in rows:
                w = cv.tag(xr, yy, kind, "", size=18)
                cv.text(xr + w + 14, yy + 15, words, 20, fill=INK, anchor="lm")
                yy += (bot - top - 78) / len(rows)
            self._legend = (cv.frame(), (60, top, 1860, bot))
        return self._legend

    def frame(self, t: float) -> np.ndarray:
        t = max(0.0, min(float(t), self.DURATION))
        if abs(St.S - 1.0) > 1e-6:                          # dag_anim is laid out for 1920 x 1080 only
            cv = Canvas()
            cv.text(W / St.S / 2, 500, self.title, 40, bold=True, anchor="mm")
            return cv.frame()
        dag = _dag()
        n_all = {c: len(dag.nodes[c]) for c in D.CAMPAIGNS}
        done, part = self._n_done(t)
        if t >= self.T_PULSE[0]:
            lit = set()
            v = lin(t, *self.T_PULSE)
            if 0 < v < 1:
                for c in D.CAMPAIGNS:
                    pos = v * (n_all[c] + 1.5) - 0.5
                    lit |= {(c, i) for i in range(n_all[c]) if abs(pos - i) < 0.75}
            fr = dag._static(n_all, frozenset(lit)).copy()
        else:
            n0 = {c: max(0, min(n_all[c], done[c])) for c in D.CAMPAIGNS}
            fr = dag._static(n0).copy()
            for c in D.CAMPAIGNS:                            # the next card of the lane being built fades in
                if 0 <= done[c] < n_all[c] and part[c] > 0:
                    n1 = dict(n0)
                    n1[c] = n0[c] + 1
                    nxt = dag._static(n1)
                    k = np.uint16(round(St.ease(part[c]) * 256))
                    fr = ((nxt.astype(np.uint16) * k + fr.astype(np.uint16) * (256 - k)) >> 8).astype(np.uint8)
        a = ramp(t, self.T_LEGEND, self.T_LEGEND + 0.8)
        if a > 0.004:
            img, (x0, y0, x1, y1) = self._legend_img()
            sub = fr[y0:y1 + 1, x0:x1 + 1]
            k = np.uint16(round(a * 256))
            sub[:] = ((img[y0:y1 + 1, x0:x1 + 1].astype(np.uint16) * k + sub.astype(np.uint16) * (256 - k)) >> 8)
        cv = Canvas(fr)
        s, ca = self.caption_at(t)
        if s:
            cv.text(960, 1004, s, 28, fill=INK, anchor="mm", a=ca)
        return cv.frame()


class Outro(Segment):
    """The chapter's end is the old one's: both networks at once and what they share, then the cards collapse to the
    icons the replay lights (dag_anim.Dag.intro_frame from its 'both' stage to the end of 'icons')."""
    key = "outro"
    title = "Both campaigns, one lab"

    def __init__(self):
        super().__init__()
        dag = _dag()
        self.t0 = dag.T["both"][0]
        self.DURATION = round(dag.T["icons"][1] - self.t0, 2)
        self.captions = [(a - self.t0, b - self.t0, s) for a, b, s in dag.captions if b > self.t0]
        self.marks = {"outro.both": 0.0, "outro.collapse": dag.T["collapse"][0] - self.t0,
                      "outro.icons": dag.T["icons"][0] - self.t0}
        self.sources = [("sim", "dag_anim.Dag: the cut's own closing of the chapter, unchanged")]

    def frame(self, t: float) -> np.ndarray:
        t = max(0.0, min(float(t), self.DURATION))
        if abs(St.S - 1.0) > 1e-6:
            cv = Canvas()
            cv.text(W / St.S / 2, 500, self.title, 40, bold=True, anchor="mm")
            return cv.frame()
        return _dag().intro_frame(self.t0 + t)


# ================================================================================================ the chapter
_SEG: dict = {}


def keys() -> list:
    return [k for k, _, _ in PARTS if not ONLY or k in ONLY]


def segment(key: str) -> Segment:
    if key not in _SEG:
        import importlib
        mod, cls = next((m, c) for k, m, c in PARTS if k == key)
        _SEG[key] = getattr(importlib.import_module(f"twin.video.{mod}"), cls)()
    return _SEG[key]


def plan() -> list:
    """[{name, title, start_s, seconds}] of the chapter's parts in order."""
    out, t = [], 0.0
    for k in keys():
        s = segment(k)
        out.append(dict(name=k, title=s.title, start_s=round(t, 3), seconds=round(float(s.DURATION), 3)))
        t += float(s.DURATION)
    return out


def total() -> float:
    p = plan()
    return p[-1]["start_s"] + p[-1]["seconds"]


def marks() -> dict:
    """Named moments of the chapter (s from its start): <part>.start and each part's own marks."""
    out = {}
    for p in plan():
        out[f"{p['name']}.start"] = p["start_s"]
        for name, t in segment(p["name"]).marks.items():
            out[name] = round(p["start_s"] + float(t), 2)
    return out


def captions() -> list:
    return [(round(p["start_s"] + a, 2), round(p["start_s"] + b, 2), s) for p in plan()
            for a, b, s in segment(p["name"]).captions]


def part_frame(key: str, t: float) -> np.ndarray:
    """One part's frame, faded in from black and out to it like every segment of the cut."""
    seg = segment(key)
    fr = seg.frame(t)
    kf = min(1.0, t / FADE, (float(seg.DURATION) - t) / FADE)
    if kf < 1.0:
        fr = St.dim(np.array(fr, copy=True), max(0.0, kf))
    return fr


class Chapter:
    """The whole chapter behind the old one's interface."""

    def __init__(self):
        self.plan = plan()
        self.DURATION = total()
        self.captions = captions()
        self.marks = marks()
        self.T = {p["name"]: (p["start_s"], p["start_s"] + p["seconds"]) for p in self.plan}

    def frame(self, t: float) -> np.ndarray:
        t = max(0.0, min(float(t), self.DURATION - 1e-6))
        for p in self.plan:
            if t < p["start_s"] + p["seconds"]:
                return part_frame(p["name"], t - p["start_s"])
        return part_frame(self.plan[-1]["name"], self.plan[-1]["seconds"])

    intro_frame = frame


# ================================================================================================ encoding
def render_piece(key: str, a: float, b: float, out: Path, preset: str) -> dict:
    from . import compose as C
    enc = C.encoder(Path(out), preset, FPS)
    n = int(round((b - a) * FPS))
    t0 = time.time()
    for k in range(n):
        enc.stdin.write(np.ascontiguousarray(part_frame(key, a + k / FPS), np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    segment(key).close()
    return dict(name=key, a=a, b=b, frames=n, wall=round(time.time() - t0, 1))


def _pieces(names: list, chunk: float = 9.0) -> list:
    out = []
    for p in plan():
        if p["name"] not in names:
            continue
        n = max(1, int(np.ceil(p["seconds"] / chunk)))
        cuts = [round(p["seconds"] * i / n * FPS) / FPS for i in range(n + 1)]
        for i in range(n):
            out.append((p["name"], cuts[i], cuts[i + 1], TMP / f"{p['name']}_{i:02d}.mp4"))
    return out


def _run_pieces(pieces: list, preset: str, workers: int):
    TMP.mkdir(parents=True, exist_ok=True)
    todo, running = list(pieces), []
    env = dict(os.environ)
    while todo or running:
        while todo and len(running) < workers:
            name, a, b, out = todo.pop(0)
            p = subprocess.Popen([sys.executable, "-m", "twin.video.experiments", "piece", name, f"{a:.4f}", f"{b:.4f}",
                                  str(out), preset], cwd=D.HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, env=env)
            running.append((p, name, a, b, time.time()))
        time.sleep(0.4)
        for item in list(running):
            p = item[0]
            if p.poll() is not None:
                running.remove(item)
                txt = p.stdout.read()
                last = txt.strip().splitlines()[-1] if txt.strip() else ""
                print(f"  {item[1]} {item[2]:.1f}-{item[3]:.1f}: rc {p.returncode}, {time.time() - item[4]:.0f} s "
                      f"{last[:120]}", flush=True)
                if p.returncode != 0:
                    print(txt[-4000:], flush=True)
                    raise SystemExit(f"piece {item[1]} failed")


def _concat(parts: list, dst: Path):
    lst = TMP / f"{dst.stem}_list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)


# ================================================================================================ narration
def narration():
    """twin/video/narration.py on this chapter's script and audio (see narration.configure)."""
    from . import narration as N
    if N.SCRIPT != SCRIPT:
        N.configure(SCRIPT, NDIR, SAY_MORE, IPA_MORE)
    return N


def record_plan() -> dict:
    return dict(segments=plan(), total_s=total())


def check_numbers() -> list:
    """Every number a line speaks (its ``nums``: [the figure or word in the text, its path in facts.json, its
    format]) against facts.json, and every figure in a line covered by its nums. Raises SystemExit on a mismatch."""
    import re
    N = narration()
    facts = X.load_facts()
    words = dict(N.WORDS, **MORE_WORDS)
    rows, bad = [], []
    for ln in N.lines():
        covered = set()
        for tok, path, fmt in ln.get("nums", []):
            v = N._resolve(path, facts)
            shown = f"{round(v):d}" if fmt == "d" else format(v, fmt)
            want = str(words[tok.lower()]) if tok.lower() in words else tok.replace(",", "")
            ok = shown == want and tok in ln["text"]
            rows.append(dict(id=ln["id"], says=tok, path=path, value=v, shown=shown, ok=ok))
            covered.add(tok)
            if not ok:
                bad.append(rows[-1])
        for fig in re.findall(r"(?<![\w-])\d+(?:,\d{3})*(?:\.\d+)?(?![\w-])", ln["text"]):
            if fig not in covered:
                rows.append(dict(id=ln["id"], says=fig, path=None, value=None, shown=None, ok=False))
                bad.append(rows[-1])
    for r in rows:
        print(f"{'ok ' if r['ok'] else 'BAD'} {r['id']:8s} says {r['says']:10s} {r['shown']!s:10s} <- {r['path']}")
    if bad:
        raise SystemExit(f"{len(bad)} spoken numbers don't match facts.json")
    print(f"{len(rows)} spoken numbers, all as facts.json has them")
    return rows


# ================================================================================================ the preview
def _commit() -> str:
    r = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=D.HERE, capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def sheet_moments() -> list:
    """Sixteen chosen moments of the chapter, from the parts' own marks."""
    mk, pl = marks(), {p["name"]: p for p in plan()}

    def end(k, back=1.2):
        return pl[k]["start_s"] + pl[k]["seconds"] - back
    want = [("intro", lambda: end("intro", 2.0), "The networks, and the labels"),
            ("composition", lambda: mk.get("composition.al.space", pl["composition"]["start_s"] + 8) + 5.0,
             "Composition: aluminium"),
            ("composition", lambda: end("composition"), "Composition: copper"),
            ("scheil", lambda: mk.get("scheil.truth", pl["scheil"]["start_s"] + 16) + 2.5, "Scheil: three curves"),
            ("scheil", lambda: end("scheil"), "Scheil: what the network takes"),
            ("am", lambda: mk.get("am.history", pl["am"]["start_s"] + 12) + 3.0, "The AM-module stand-in"),
            ("am", lambda: end("am"), "What the twin takes from it"),
            ("atomize", lambda: mk.get("atomize.pour", pl["atomize"]["start_s"] + 8) + 2.0, "Atomizing (real footage)"),
            ("atomize", lambda: end("atomize"), "The powder's size and yield"),
            ("print", lambda: end("print"), "Nine cubes, nine settings"),
            ("sem", lambda: mk.get("sem.ebsd", pl["sem"]["start_s"] + 22) + 2.0, "SEM: four signals"),
            ("sem", lambda: end("sem"), "Which the network uses"),
            ("mech", lambda: mk["mech.furnace"] + 6.5, "Heat treatment (illustrative)"),
            ("mech", lambda: end("mech"), "The tensile test"),
            ("corrosion", lambda: mk.get("corrosion.scans", pl["corrosion"]["start_s"] + 12) + 2.0,
             "Copper: the one-hour screen"),
            ("corrosion", lambda: end("corrosion"), "Thirty days in seawater")]
    return [(round(float(fn()), 2), lab) for k, fn, lab in want if k in pl]


def meta(rec: dict) -> dict:
    """The preview's title and description for YouTube (private): what it is, what is simulated, its parts."""
    f = X.follow()
    al, cu = f["flaime_al"], f["onr_cu"]
    c = rec["commit"]
    base = f"https://github.com/vertical-cloud-lab/byu-vcl/blob/{c}/vertical-lab"
    lines = [
        "PREVIEW for review, not a public cut: the function-network chapter of the twin's campaign video, rebuilt to "
        "show each step as the experiment and the data it makes.",
        "",
        "Everything is simulated unless a label on screen says otherwise. The curves, micrographs and maps are the "
        "digital twin's own models and instrument simulators run for two alloys of round 3b's replay: aluminium "
        f"design {al['design']} of seed {al['seed']} ({alloy_name(al['composition'], 'Al', 5)}) and copper design "
        f"{cu['design']} of seed {cu['seed']} ({alloy_name(cu['composition'], 'Cu')}). They are those alloys' simulated "
        "data, not the replayed runs' own draws, at stated example settings. Schematics are labelled illustrative; "
        "the atomizer footage is the lab's own (630 bronze, 27 Oct 2026: another alloy); the pictures of stations are "
        "the lab's 3-D model. Nothing here is Thermo-Calc output or real SEM data.",
        "",
    ]
    for p in rec["segments"]:
        t = p["start_s"]
        lines.append(f"{int(t // 60)}:{int(t % 60):02d} {p['title']}")
    lines += ["",
              f"Code: {base}/twin/video/experiments.py (built from {c})",
              f"Notes: {base}/notes/twin_video.md",
              "Voice: Kokoro v1.0, af_heart (open weights; nobody's voice cloned).",
              "PR: https://github.com/vertical-cloud-lab/byu-vcl/pull/403"]
    return dict(title="PREVIEW: the function networks, step by step, with the experiments (simulated; twin video)",
                description="\n".join(lines), tags=["digital twin", "alloy discovery", "self-driving lab", "CALPHAD",
                                                    "Scheil", "laser powder bed fusion", "SEM", "EBSD", "tensile test",
                                                    "corrosion", "BYU", "vertical cloud lab", "simulated"],
                categoryId="28", commit=c)


def build(names: list | None = None, preset: str | None = None) -> dict:
    """The standalone preview: every part's pieces encoded in parallel, joined without re-encoding, the narration
    placed and mixed in; then the record, the description and the contact sheet. names: encode only these parts
    again (the others' pieces are reused)."""
    from . import compose as C
    t_start = time.time()
    preset = preset or os.environ.get("TWIN_VIDEO_PRESET", "medium")
    workers = int(os.environ.get("TWIN_VIDEO_WORKERS", "4"))
    pl = plan()
    allp = _pieces([p["name"] for p in pl])
    todo = [q for q in allp if (names is None or q[0] in names) or not Path(q[3]).exists()]
    print(f"{len(pl)} parts, {total():.1f} s; encoding {len(todo)} of {len(allp)} pieces on {workers} workers "
          f"({preset})", flush=True)
    _run_pieces(todo, preset, workers)
    OUT.mkdir(parents=True, exist_ok=True)
    _concat([q[3] for q in allp], PREVIEW)
    N = narration()
    rec = record_plan()
    dur = C._duration(PREVIEW) or rec["total_s"]
    wav = TMP / "narration.wav"
    placed = N.track(rec, marks(), dur, wav, NDIR / "narration.srt")
    C.mux(PREVIEW, wav)
    rec.update(file=PREVIEW.name, seconds=C._duration(PREVIEW), fps=FPS, size=[W, H], commit=_commit(),
               sha256=hashlib.sha256(PREVIEW.read_bytes()).hexdigest(), bytes=PREVIEW.stat().st_size,
               marks=marks(), captions=[list(c) for c in captions()], follow=X.load_facts()["follow"],
               sources={p["name"]: [list(s) for s in segment(p["name"]).sources] for p in pl},
               narration=dict(voice=f"Kokoro v1.0 {N.VOICE}, speed {N.SPEED}", lines=len(placed),
                              spoken_s=round(sum(p["end"] - p["t"] for p in placed), 1), placed=placed),
               chapters=[[p["start_s"], p["title"]] for p in pl], build_minutes=round((time.time() - t_start) / 60, 1))
    (OUT / "record.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    (OUT / "youtube_meta.json").write_text(json.dumps(meta(rec), indent=1, ensure_ascii=False) + "\n")
    C.sheet_at(PREVIEW, OUT / "sheet.png", sheet_moments())
    print(f"{PREVIEW}: {rec['seconds']} s, {rec['bytes'] / 1e6:.1f} MB, {rec['build_minutes']} min", flush=True)
    return rec


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "plan"
    if cmd == "piece":
        print(json.dumps(render_piece(a[1], float(a[2]), float(a[3]), Path(a[4]), a[5])))
    elif cmd == "plan":
        for p in plan():
            print(f"{int(p['start_s'] // 60)}:{p['start_s'] % 60:04.1f}  {p['seconds']:5.1f} s  {p['name']:12s} "
                  f"{p['title']}")
        print(f"total {total():.1f} s")
        if SCRIPT.exists():
            N = narration()
            import tempfile
            placed = N.track(record_plan(), marks(), total(), Path(tempfile.gettempdir()) / "exp_narration.wav")
            for p in placed:
                print(f"{N.clock(p['t']):>7s}-{N.clock(p['end']):>7s}  {p['seg']:11s} {p['id']:8s} {p['text'][:88]}"
                      + (f"   !! {'; '.join(p['warn'])}" if p["warn"] else ""))
    elif cmd == "stills":
        ch = Chapter()
        os.makedirs("/tmp/vid", exist_ok=True)
        from PIL import Image
        for tt in [float(v) for v in a[1:]] or [m[0] for m in sheet_moments()]:
            Image.fromarray(ch.frame(tt)).save(f"/tmp/vid/chapter_{tt:06.1f}.png")
            print(f"/tmp/vid/chapter_{tt:06.1f}.png")
    elif cmd == "nums":
        check_numbers()
    elif cmd == "tts":
        au = narration().speak_all(set(a[1:]) or None)
        print(f"{len(au)} lines, {sum(len(y) for y in au.values()) / 24000 / 60:.2f} min of speech in {NDIR}")
    elif cmd == "check":
        narration().check()
    elif cmd == "segment":
        TMP.mkdir(parents=True, exist_ok=True)
        ps = _pieces([a[1]])
        _run_pieces(ps, os.environ.get("TWIN_VIDEO_PRESET", "veryfast"), int(os.environ.get("TWIN_VIDEO_WORKERS", "4")))
        _concat([q[3] for q in ps], OUT / f"segment_{a[1]}.mp4")
        print(OUT / f"segment_{a[1]}.mp4")
    elif cmd == "build":
        build(a[1:] or None)
    else:
        raise SystemExit(__doc__)

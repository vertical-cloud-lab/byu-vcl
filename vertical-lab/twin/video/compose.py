"""The campaign video, cut and encoded: every segment's frames from the other modules, the replay's clock, cameras and
overlays, the encode (segments in parallel, joined without re-encoding), the chapter record and the contact sheet.

    python -m twin.video.compose preview            # out/twin2/video/preview.mp4 (about 50 s), veryfast
    python -m twin.video.compose final              # out/twin2/video/campaign.mp4, youtube_meta.json, sheet.png
    python -m twin.video.compose stills [t ...]     # frames of the full cut at times t (s) -> /tmp/vid/cut_<t>.png
    python -m twin.video.compose plan               # the segments, their start times and the replay's phases

Options (environment): TWIN_VIDEO_WORKERS (parallel encoders, default 2), TWIN_VIDEO_EVENTS / TWIN_VIDEO_RUN (the run
replayed, see data.py), TWIN_VIDEO_PRESET (x264 preset; preview veryfast, final medium).
Segments: title, simulated (the lab and the two search spaces), dag (dag_anim), figures (figs_anim.explain_frame),
replay (this module), results (figs_anim.results_frame), takeaway, notes.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import assets as A
from . import data as D
from . import style as St

FPS = 30
R3B = D.R3B                      # round 3b's re-cut of round 3's video (TWIN_VIDEO_ROUND=3b)
VID = D.VID
# the narrated cut (twin/video/narration.py): TWIN_VIDEO_NARRATION=1. It keeps its own files (campaign_narrated.mp4,
# final_narrated_record.json, youtube_meta_narrated.json, sheet_narrated.png), so the cut without narration and its
# records stay as they were; the takeaway and the notes are longer, to fit their lines.
NARRATE = os.environ.get("TWIN_VIDEO_NARRATION", "0") == "1"
NAR = "_narrated" if NARRATE else ""
TMP = VID / "parts"
W, H = St.W, St.H
px = St.px

# ============================================================================================ shared state (lazy)
_S: dict = {}


def S(key):
    """Shared objects, built on first use in this process."""
    if key in _S:
        return _S[key]
    if key == "R":
        v = D.replay()
        if R3B:                                         # two runs: the timeline says where the replay changes run
            _S["R"] = v
            v.switch_h = S("tl").switch_h
    elif key == "B":
        v = D.bench([S("R")])
    elif key == "E":
        v = D.econ()
    elif key == "dag":
        from .dag_anim import Dag
        v = Dag()
    elif key == "figs":
        from . import figs_anim as F
        F.context(S("R"), S("B"))
        v = F
    elif key == "figs3":                                # round 3's cards (TWIN_VIDEO_ROUND=3), or round 3b's (3b)
        if R3B:
            from . import figs3b as F3
        else:
            from . import figs3 as F3
        S("figs")
        v = F3
    elif key == "plots":
        v = S("figs").PlotPanel(S("R"), S("B"))
    elif key == "be":
        from .birdseye import Birdseye
        v = Birdseye(S("R"))
    elif key == "pt":
        from . import ptable as P
        v = P
    elif key == "pool":
        v = A.Pool(keep=16)
    elif key == "tl":
        v = Timeline(S("R"))
    else:
        raise KeyError(key)
    _S[key] = v
    return v


def placeholder() -> bool:
    return bool(S("R").placeholder or S("B").get("placeholder") or S("E").get("placeholder"))


def tag_placeholder(fr: np.ndarray):
    if not placeholder():
        return fr
    im, d = St.layer(px(360), px(40))
    d.rounded_rectangle((0, 0, px(359), px(39)), radius=px(8), fill=(150, 30, 30, 235))
    d.text((px(180), px(20)), "PLACEHOLDER DATA", font=St.font(20, bold=True), fill=St.INK, anchor="mm")
    St.paste(fr, im, (W - px(360)) // 2, H - px(52))
    return fr


def caption_bar(fr: np.ndarray, text: str, a: float = 1.0, y: float = 1000, size: float = 26):
    """A centred caption on a soft dark pill (the cards' and the lab footage's captions)."""
    if a <= 0 or not text:
        return fr
    f = St.font(size)
    lines = St.wrap(text, f, px(1500))
    lh = px(size * 1.35)
    wmax = max(St.text_w(f, ln) for ln in lines) + px(40)
    hh = lh * len(lines) + px(18)
    im, d = St.layer(wmax, hh)
    d.rounded_rectangle((0, 0, wmax - 1, hh - 1), radius=px(10), fill=St.SURF + (225,))
    for i, ln in enumerate(lines):
        d.text((wmax / 2, px(9) + lh * i + lh / 2), ln, font=f, fill=St.INK, anchor="mm")
    St.paste(fr, im, (W - wmax) // 2, int(px(y) - hh), a)
    return fr


# ================================================================================================ the title
TITLE = "A year of alloy discovery in an automated lab"
SUBTITLE = "Two campaigns replayed in a digital twin: a simulated benchmark"
ROUND3 = D.ROUND == 3
if ROUND3:
    TITLE = "A simulated year of alloy discovery in an automated lab"
    SUBTITLE = "Round 3 of a digital-twin benchmark: two campaigns, replayed"
if R3B:
    SUBTITLE = "Round 3b of a digital-twin benchmark: the lab comparison, like for like"
TITLE_DUR = 14.5 if R3B else 8.0      # round 3b: the card stays while the opening line says what this cut compares


def title_frame(t: float) -> np.ndarray:
    be = S("be")
    fr = np.asarray(be.base("high", 1.0 + 0.04 * t / 8.0, (0.5, 0.5))).copy()
    St.dim(fr, 0.28)
    k = St.window(t, 0.2, TITLE_DUR, 0.8)
    im, d = St.layer()
    if ROUND3:
        d.text((W / 2, px(330)), "A simulated year of alloy discovery", font=St.font(64, bold=True), fill=St.INK,
               anchor="mm")
        d.text((W / 2, px(408)), "in an automated lab", font=St.font(64, bold=True), fill=St.INK, anchor="mm")
    else:
        d.text((W / 2, px(400)), TITLE, font=St.font(64, bold=True), fill=St.INK, anchor="mm")
    d.text((W / 2, px(480)), SUBTITLE, font=St.font(34), fill=St.INK2, anchor="mm")
    y = px(580)
    for c in D.CAMPAIGNS:
        f = St.font(28)
        txt = St.CAMP_LONG[c]
        tw = St.text_w(f, txt) + px(36)
        x0 = (W - tw) / 2
        d.rounded_rectangle((x0, y - px(4), x0 + px(22), y + px(28)), radius=px(4), fill=St.CAMP[c])
        d.text((x0 + px(36), y + px(12)), txt, font=f, fill=St.INK, anchor="lm")
        y += px(52)
    d.text((W / 2, px(800)), "BYU Vertical Cloud Lab, PR 318's lab design. No real experiments: every result is "
           "simulated.", font=St.font(24), fill=St.INK2, anchor="mm")
    if R3B:
        d.text((W / 2, px(846)), "A re-cut of round 3's video with round 3b's results. Both earlier videos and the "
               "audit are linked in the description.", font=St.font(20), fill=St.INK2, anchor="mm")
    elif ROUND3:
        d.text((W / 2, px(846)), "Round 2's video and its audit are linked in the description.", font=St.font(20),
               fill=St.INK2, anchor="mm")
    St.paste(fr, im, 0, 0, k)
    return fr


# ============================================================================= what is simulated (the lab, the spaces)
def _setup_shots():
    m = json.loads((A.OUT / "setup_lab.json").read_text())
    fps = float(m["fps"])
    subs = m["substeps"]

    def first(prefix, contains=""):
        for s in subs:
            if s["label"].startswith(prefix) and contains in (s.get("caption") or ""):
                return s["start_frame"] / fps
        return None
    t_units = first("6/9", "first MiR250") or 56.0
    t_tray = first("7/9", "Tray D") or 82.0
    t_end = first("9/9") or 110.0
    return [("setup_lab", t_units, t_units + 7.5, "the two mobile arms (MiR250 + UR) are built"),
            ("setup_lab", t_tray, t_tray + 6.0, "a tray of instruments comes to a Shuttle's opening"),
            ("setup_lab", t_end, min(t_end + 10.0, 121.5), "the lab as set up")]


SIM_DUR = 46.0
SIM_LAB = 18.0            # seconds of lab footage, then the two search spaces
SIM_CAPS = [
    (0.0, SIM_LAB, "The lab: PR 318's vertical cloud lab design. Two Kardex Shuttles hold the instruments on trays; "
                   "floor machines atomize, print and test; two mobile arms move the samples."),
    (SIM_LAB, SIM_LAB + 14, "FLAIME searches aluminium alloys for laser powder bed fusion: Al plus 15 elements, "
                            "within these bounds."),
    (SIM_LAB + 14, SIM_DUR, "ONR searches copper alloys for blown-powder DED: Cu plus 8 elements. Both campaigns "
                            "share the lab, the atomizer and the calendar."),
]


def simulated_frame(t: float) -> np.ndarray:
    if t < SIM_LAB:
        shots = _setup_shots()
        lens = [s[2] - s[1] for s in shots]
        tot = sum(lens)
        u = t / SIM_LAB * tot
        i = 0
        while i < len(shots) - 1 and u > lens[i]:
            u -= lens[i]
            i += 1
        clip, a, b, lab = shots[i]
        r = S("pool").get(("setup", i), lambda: A.Reader(clip, a, b, W, H, speed=1.0, fps=FPS))
        fr = r.frame(min(u, b - a - 0.05)).copy()
        chip = A.label_chip(lab, 22)
        St.paste(fr, chip, px(40), px(36))
        k = 1.0 - St.ramp(t, SIM_LAB - 0.6, SIM_LAB)
        if k < 1:
            St.dim(fr, k)
    else:
        fr = St.blank()
        P = S("pt")
        ts = t - SIM_LAB
        camp = "flaime_al" if ts < 14 else "onr_cu"
        t0 = 0.0 if camp == "flaime_al" else 14.0
        rev = St.ease_out((ts - t0) / 7.0)
        im = P.bounds_figure(camp, px(1700), px(760), reveal=rev)
        a = St.window(ts, t0, t0 + 14 if camp == "flaime_al" else SIM_DUR - SIM_LAB, 0.6)
        St.paste(fr, im, (W - px(1700)) // 2, px(90), a)
    for t0, t1, txt in SIM_CAPS:
        if t0 <= t < t1:
            caption_bar(fr, txt, St.window(t, t0, t1, 0.5), y=1052)
    return fr


# ================================================================================================= the replay
REPLAY_DUR = 360.0
POV_MAX = 80.0                    # seconds of video for day 1, one alloy start to finish
# after day 1: (share of the rest of the replay, mode, view, zoom from, zoom to)
PHASES = [
    (0.00, "grid", 4, None, None),
    (0.12, "grid", 9, None, None),
    (0.28, "be", "high", 1.45, 1.22),
    (0.48, "grid", 9, None, None),
    (0.58, "be", "sw", 1.15, 1.0),
    (0.74, "be", "se", 1.15, 1.0),
    (0.88, "be", "high", 1.2, 1.0),
]
# TWIN_VIDEO_LAB3D=1 (the animated cut, `final3d`): the same shares, each a camera on PR 318's 3-D lab moved by the event
# log (lab3d.py), and an inset of the two Shuttles up close from a second camera where `pip` is set
LAB3D = os.environ.get("TWIN_VIDEO_LAB3D", "0") == "1"
PHASES3D = [
    (0.00, "3d", "towers_c", None),
    (0.12, "3d", "plan", "towers_c"),
    (0.28, "3d", "high", "towers_c"),
    (0.48, "3d", "towers_c", None),
    (0.58, "3d", "sw", None),
    (0.74, "3d", "se", "towers_c"),
    (0.88, "3d", "high", None),
]
if LAB3D:
    PHASES = [(a, b, c, None, None) for a, b, c, _ in PHASES3D]
SPEED_SHAPE = [(0.0, 1.0), (0.10, 3.0), (0.28, 10.0), (0.55, 28.0), (1.0, 40.0)]   # relative lab h per video s
# round 3b: the replay is the replay arm's median seed for aluminium's halfway target until this phase starts, and its
# median seed for copper's best existing alloy from there (data.Replay2). The phase is the cut to "month by month": by
# then the first seed's aluminium is past both targets, and the second's copper has not reached its first.
SWITCH_PHASE = 4
SWITCH_CARD_S = 7.0               # seconds the card that says so stays up
POV_SECONDS = {"charge": 7.0, "atomize": 12.0, "powder QC": 5.5, "print": 8.0, "test": 6.0, "section": 6.0,
               "pip": 6.0, "screen": 7.0, "immersion": 7.0, "tensile": 6.0}
STATION_NAME = {"shop": "machining cell", "doser": "doser + vacuum press (tray B)", "atomizer": "rePowder atomizer",
                "sieve": "sieving cell", "psd": "Mastersizer (tray E)", "byu_sem": "SEM + EDS (tray D)",
                "byu_icpms": "ICP-MS", "density": "density, cracks (VHX, tray K)", "edm": "wire EDM",
                "furnace": "furnace (tray F)", "tensile": "tensile (Instron, zwickiLine)", "tensile_hot":
                    "tensile at 250 C", "utah_midi": "LPBF (Aconity MIDI)", "utah_mxlab": "DED (InssTek MX-Lab)",
                "mines_x2": "DED (Mines X2, outside)", "nsl": "NSL Analytical (outside)", "cubxl":
                    "corrosion (CubXL, tray A)", "immersion": "immersion (tray A)", "xrd": "XRD (tray D)",
                "xrf": "XRF (tray M)", "prep": "metallography (tray F)", "hardness": "micro-Vickers (tray L)",
                "nanoindent": "nanoindenter (tray E)", "pip": "PIP (tray E)", "hpc": "BYU HPC"}
WHAT_WORDS = {"charge": "charging cups", "atomize": "atomizing", "powder QC": "powder checks", "print": "printing (LPBF)",
              "test": "heat treat, EDM, tensile", "section": "sectioning", "pip": "PIP", "screen": "corrosion screen",
              "immersion": "30-day immersion", "tensile": "DED bars, tensile", "blown_small": "DED blocks",
              "blown_large": "DED bars", "preplaced": "DED (preplaced)", "nsl": "chemistry (outside)",
              "promote": "full plate, E8 bars", "gas_atomize": "gas atomization (outside)",
              "blend_ded": "DED blend screen"}
DENSITY_SHOT = ("alloy_characterize", 1277 / 6, 1392 / 6, "density and cracks: VHX imaging (tray K)")


SHOT_BY = {  # (what, station) -> (shot kind, index), where the station alone would pick the wrong footage
    ("powder QC", "sieve"): ("powder QC", 0), ("powder QC", "xrd"): ("powder QC", 1),
    ("powder QC", "psd"): ("powder QC", 2), ("powder QC", "byu_sem"): ("powder QC", 3),
    ("powder QC", "xrf"): ("powder QC", 4), ("print", "utah_midi"): ("print", 1),
    ("print", "byu_sem"): ("section", 3), ("section", "byu_sem"): ("section", 3), ("test", "byu_sem"): ("section", 3),
    ("test", "edm"): ("test", 1), ("test", "furnace"): ("test", 2), ("test", "tensile"): ("test", 3),
    ("test", "tensile_hot"): ("test", 3), ("promote", "utah_midi"): ("print", 1), ("promote", "edm"): ("test", 1),
    ("promote", "furnace"): ("test", 2), ("promote", "tensile"): ("test", 3), ("promote", "tensile_hot"): ("test", 3),
    ("charge", "shop"): ("machine", 0), ("charge", "doser"): ("charge", 0),
    ("pip", "prep"): ("section", 2), ("pip", "furnace"): ("test", 2), ("pip", "pip"): ("pip", 0),
}


def _shot_of(what: str, station: str, k: int = 0):
    """The footage for an event: by (what, station), else by its station, else by its kind."""
    if station == "density":
        return DENSITY_SHOT
    if (what, station) in SHOT_BY:
        kind, i = SHOT_BY[(what, station)]
        lst = A.SHOTS[kind]
        return lst[i % len(lst)]
    kind = A.STATION_SHOT.get(station)
    if what in ("charge", "atomize") or kind is None or kind in ("sim", "offsite"):
        lst = A.shots_for(what)
    else:
        lst = A.shots_for(kind)
        pick = A.STATION_PICK.get(station)
        if pick is not None and lst:
            lst = lst[pick % len(lst):] + lst[:pick % len(lst)]
    if not lst:
        return None
    return lst[k % len(lst)]


class Timeline:
    """Video seconds of the replay -> lab hours, the camera mode, and the shots of day 1.

    Day 1 follows one alloy (the first of FLAIME's to reach its tensile test) through every step it takes, a shot per
    step, lab time running at whatever speed fits the step into its shot (the clock shows it). After it, the speed
    rises smoothly (SPEED_SHAPE, scaled so the year ends with the replay) and the cameras pull back: a 2 x 2 and a
    3 x 3 grid of station cameras, then the birds-eye views with beacons lit by the event log."""

    def __init__(self, R: D.Replay, duration: float = REPLAY_DUR):
        self.R, self.dur = R, duration
        self.horizon = R.horizon_h
        self.pov = self._pov()
        self.t_pov = self.pov[-1]["v1"] if self.pov else 0.0
        self.l_pov = self.pov[-1]["l1"] if self.pov else 0.0
        # the ramp after day 1
        n = 4000
        self.vg = np.linspace(self.t_pov, duration, n)
        u = (self.vg - self.t_pov) / max(1e-6, duration - self.t_pov)
        xs, ys = zip(*SPEED_SHAPE)
        shape = np.exp(np.interp(u, xs, np.log(ys)))
        dv = np.diff(self.vg)
        integ = np.concatenate([[0.0], np.cumsum(0.5 * (shape[1:] + shape[:-1]) * dv)])
        k = (self.horizon - self.l_pov) / integ[-1]
        self.speed_g = shape * k
        self.lab_g = self.l_pov + integ * k
        self.phase_t = [self.t_pov + p[0] * (duration - self.t_pov) for p in PHASES]
        self.switch_t = self.phase_t[SWITCH_PHASE]         # round 3b: the second run takes over here
        self.switch_h = float(np.interp(self.switch_t, self.vg, self.lab_g))
        self.grid_st = {4: self._grid_stations(4), 9: self._grid_stations(9)}

    # ------------------------------------------------------------------------------------------------ day 1
    def _pov(self) -> list:
        R = self.R
        i = R.first_event("flaime_al", nodes=("test",))
        if i is None:
            i = R.first_event("flaime_al", whats=("print",)) or R.first_event("flaime_al", whats=("atomize",))
        if i is None:
            return []
        des = R.design[i]
        evs = [j for j in np.argsort(R.t0, kind="stable") if R.design[j] == des and R.camp[j] == "flaime_al"
               and not str(R.what[j]).startswith("sim")]
        node_i = R.node[i]
        t_end = max(R.t1[j] for j in evs if R.node[j] == node_i and R.t0[j] < R.t0[i] + 24.0)
        evs = [j for j in evs if R.t0[j] < t_end]
        steps = []                                       # (what, station, lab start): each step shown once
        seen = set()
        for j in evs:
            what, st = R.what[j], R.station[j]
            if st == "shop" and what != "charge":
                continue
            sh = _shot_of(what, st)
            if sh is None or (what, st) in seen or sh in [x[3] for x in steps]:
                continue                                 # a repeat (a second lot, a second look): its time goes on
            seen.add((what, st))                         # in the shot before it
            steps.append((what, st, float(R.t0[j]), sh))
        steps = [x[:3] for x in steps][:16]
        if not steps:
            return []
        shots = []
        for n_, (what, st, l0) in enumerate(steps):
            l1 = steps[n_ + 1][2] if n_ + 1 < len(steps) else float(t_end)
            if n_ == 0:
                l0 = 0.0                                 # the clock starts at Monday 00:00
            if what == "charge" and st == "doser":      # dosed by weight, then pressed under vacuum
                mid = l0 + 0.5 * (l1 - l0)
                shots.append(dict(shot=A.SHOTS["charge"][0], what=what, station=st, design=des, l0=l0, l1=mid,
                                  dur=5.5))
                shots.append(dict(shot=A.SHOTS["charge"][1], what=what, station=st, design=des, l0=mid, l1=l1,
                                  dur=5.0))
                continue
            if what == "atomize":                        # the melt, then the pour: the lab's own footage
                mid = l0 + 0.45 * (l1 - l0)
                shots.append(dict(shot=A.SHOTS["atomize"][1], what=what, station=st, design=des, l0=l0, l1=mid,
                                  dur=6.0))
                shots.append(dict(shot=A.SHOTS["atomize"][2], what=what, station=st, design=des, l0=mid, l1=l1,
                                  dur=6.5))
                continue
            dur = 5.0 if st in ("psd", "byu_sem", "density", "sieve") else POV_SECONDS.get(what, 6.0)
            shots.append(dict(shot=_shot_of(what, st), what=what, station=st, design=des, l0=l0, l1=max(l1, l0 + 0.05),
                              dur=dur))
        tot = sum(s_["dur"] for s_ in shots)
        scale = min(1.0, POV_MAX / tot)
        v = 0.0
        for s_ in shots:
            s_["v0"] = v
            s_["v1"] = v = v + s_["dur"] * scale
        return shots

    def _grid_stations(self, n: int) -> list:
        """The n stations busiest over the year (hours booked per unit), that have footage or a floor spot."""
        R = self.R
        hours: dict = {}
        for a, b, st in zip(R.t0, R.t1, R.station):
            hours[st] = hours.get(st, 0.0) + (min(b, self.horizon) - a)
        units = {k: max(1, int(v.get("units", 1) or 1)) for k, v in R.stations.items()}
        ok = [s for s in hours if A.STATION_SHOT.get(s) not in (None, "sim", "offsite")
              and not R.stations.get(s, {}).get("external") and s not in ("immersion", "shop")]
        ok.sort(key=lambda s: -hours[s] / units.get(s, 1))
        want = {4: ["atomizer", "utah_midi", "utah_mxlab", "tensile"],
                9: ["doser", "atomizer", "sieve", "byu_sem", "utah_midi", "utah_mxlab", "furnace", "tensile",
                    "cubxl"]}.get(n, [])
        pick = [s for s in want if s in R.stations][:n]
        pick += [s for s in ok if s not in pick][: n - len(pick)]
        return pick

    # ---------------------------------------------------------------------------------------------- queries
    def lab(self, t: float) -> tuple:
        """(lab hours, lab hours per video second) at t seconds into the replay."""
        if t < self.t_pov:
            for s in self.pov:
                if s["v0"] <= t < s["v1"]:
                    u = (t - s["v0"]) / (s["v1"] - s["v0"])
                    return s["l0"] + u * (s["l1"] - s["l0"]), (s["l1"] - s["l0"]) / (s["v1"] - s["v0"])
        t = min(max(t, self.t_pov), self.dur)
        return float(np.interp(t, self.vg, self.lab_g)), float(np.interp(t, self.vg, self.speed_g))

    def pov_at(self, t: float):
        for s in self.pov:
            if s["v0"] <= t < s["v1"]:
                return s
        return None

    def phase(self, t: float) -> int:
        i = 0
        for j, pt in enumerate(self.phase_t):
            if t >= pt:
                i = j
        return i

    def marks(self) -> list:
        """(seconds into the replay, chapter title)."""
        out = [(0.0, "The first alloy, start to finish")]
        names = {0: "Day by day: station cameras", 2: "Week by week: the whole lab",
                 4: "Month by month, to the end of the year"}
        if LAB3D:
            names[0] = "Day by day: the lab up close, moved by the event log"
        if R3B:                                             # which seed each stretch is
            sa, sb = (q["seed"] for q in self.R.parts)
            out = [(0.0, f"The first alloy, start to finish (seed {sa})")]
            names = {k: v + f" (seed {sa if k < SWITCH_PHASE else sb})" for k, v in names.items()}
        for i, tt in enumerate(self.phase_t):
            if i in names:
                out.append((tt, names[i]))
        return out


def speed_words(sp: float) -> str:
    """'1 s of video = 12 min of lab time' for lab hours per video second."""
    h = sp
    if h < 1.0:
        lab = f"{h * 60:.0f} min"
    elif h < 48:
        lab = f"{h:.1f} h" if h < 10 else f"{h:.0f} h"
    else:
        lab = f"{h / 24:.1f} days"
    return f"1 s of video = {lab} of lab time"


DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def clock_panel(t_h: float, sp: float) -> Image.Image:
    w, h = px(470), px(118)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(12), fill=St.SURF + (int(255 * St.PANEL_A),))
    day = int(t_h // 24)
    hod = t_h - day * 24
    hh, mm = int(hod), int((hod - int(hod)) * 60)
    d.text((px(18), px(12)), f"Day {day + 1}", font=St.font(40, bold=True), fill=St.INK)
    x = px(18) + St.text_w(St.font(40, bold=True), f"Day {day + 1}") + px(16)
    d.text((x, px(26)), f"{DOW[day % 7]} {hh:02d}:{mm:02d}", font=St.font(26, mono=True), fill=St.INK)
    d.text((px(18), px(64)), speed_words(sp), font=St.font(19), fill=St.INK2)
    # the year as a bar
    x0, x1, y = px(18), w - px(18), px(98)
    hz = S("R").horizon_days
    d.rounded_rectangle((x0, y, x1, y + px(6)), radius=px(3), fill=(70, 73, 80, 255))
    xe = x0 + (x1 - x0) * min(1.0, t_h / 24 / hz)
    d.rounded_rectangle((x0, y, max(x0 + px(6), xe), y + px(6)), radius=px(3), fill=St.INK + (255,))
    return im


POV_CARD = (700, 250)            # covers the clips' burnt-in gauge tables (up to 0.38 W x 0.31 H of the source)


def pov_card(t_h: float, sp: float, head: str, sub: str) -> Image.Image:
    """Day 1's corner card: the clock, the speed, the year, then the step on screen. Opaque and flush with the
    corner, so nothing of a clip's own gauge table shows round it."""
    w, h = px(POV_CARD[0]), px(POV_CARD[1])
    im, d = St.layer(w, h)
    r = px(14)
    d.rounded_rectangle((-r, -r, w - 1, h - 1), radius=r, fill=St.SURF + (255,))
    day = int(t_h // 24)
    hod = t_h - day * 24
    hh, mm = int(hod), int((hod - int(hod)) * 60)
    x0 = px(40)
    d.text((x0, px(28)), f"Day {day + 1}", font=St.font(40, bold=True), fill=St.INK)
    x = x0 + St.text_w(St.font(40, bold=True), f"Day {day + 1}") + px(16)
    d.text((x, px(42)), f"{DOW[day % 7]} {hh:02d}:{mm:02d}", font=St.font(26, mono=True), fill=St.INK)
    d.text((x0, px(82)), speed_words(sp), font=St.font(19), fill=St.INK2)
    hz = S("R").horizon_days
    xb0, xb1, yb = x0, w - px(40), px(114)
    d.rounded_rectangle((xb0, yb, xb1, yb + px(6)), radius=px(3), fill=(70, 73, 80, 255))
    xe = xb0 + (xb1 - xb0) * min(1.0, t_h / 24 / hz)
    d.rounded_rectangle((xb0, yb, max(xb0 + px(6), xe), yb + px(6)), radius=px(3), fill=St.INK + (255,))
    d.line((x0, px(140), w - px(40), px(140)), fill=St.RULE + (255,), width=px(1))
    d.rounded_rectangle((x0, px(158), x0 + px(14), px(172)), radius=px(3), fill=St.CAMP["flaime_al"])
    d.text((x0 + px(24), px(150)), head, font=St.font(24, bold=True), fill=St.INK)
    for i, ln in enumerate(St.wrap(sub, St.font(19), w - px(80))[:2]):
        d.text((x0, px(190) + i * px(26)), ln, font=St.font(19), fill=St.INK2)
    return im


def frost(cell: np.ndarray, fw: float = 0.40, fh: float = 0.27):
    """Blur and darken a camera cell's top-left corner, where its clip drew a gauge table."""
    from PIL import ImageFilter
    h, w = cell.shape[:2]
    bw, bh = int(w * fw), int(h * fh)
    sub = Image.fromarray(np.ascontiguousarray(cell[:bh, :bw])).filter(ImageFilter.GaussianBlur(max(3, w / 90)))
    a = np.asarray(sub).astype(np.uint16)
    cell[:bh, :bw] = ((a * 110) >> 8).astype(np.uint8)
    return cell


def counters_panel(t_h: float) -> Image.Image:
    R = S("R")
    w, h = px(450), px(150)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(12), fill=St.SURF + (int(255 * St.PANEL_A),))
    d.text((px(16), px(10)), ("simulated so far" if ROUND3 else "so far") + ": alloys designed / made / tested",
           font=St.font(16), fill=St.INK2)
    y = px(36)
    tg = S("B")["target"]
    for c in D.CAMPAIGNS:
        n = R.counts(c, t_h)
        d.rounded_rectangle((px(16), y + px(5), px(30), y + px(19)), radius=px(3), fill=St.CAMP[c])
        d.text((px(38), y), St.CAMP_NAME[c], font=St.font(21, bold=True), fill=St.INK)
        d.text((px(140), y), f"{n['designed']} / {n['made']} / {n['tested']}", font=St.font(21, bold=True),
               fill=St.INK)
        best = R.best_at(c, t_h)
        if ROUND3:
            d.text((px(38), y + px(27)), f"spent {St.money(R.spent_at(c, t_h))}   best new {best:.2f} "
                   f"(targets {tg[c]:.2f}, {D.targets2()[c]:.2f})", font=St.font(16), fill=St.INK2)
        else:
            d.text((px(38), y + px(27)), f"spent {St.money(R.spent_at(c, t_h))}   best {best:.2f} "
                   f"(target {tg[c]:.2f})", font=St.font(17), fill=St.INK2)
        y += px(56)
    return im


def now_pill(text: str, sub: str = "") -> Image.Image:
    f, f2 = St.font(24, bold=True), St.font(18)
    w = max(St.text_w(f, text), St.text_w(f2, sub) if sub else 0) + px(40)
    w = min(w, px(880))
    h = px(44) + (px(26) if sub else 0)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(12), fill=St.SURF + (int(255 * St.PANEL_A),))
    d.text((w / 2, px(22)), text, font=f, fill=St.INK, anchor="mm")
    if sub:
        d.text((w / 2, px(55)), sub, font=f2, fill=St.INK2, anchor="mm")
    return im


def _empty_panel(title: str, note: str) -> Image.Image:
    w, h = px(450), px(110)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(12), fill=St.SURF + (int(255 * St.PANEL_A),))
    d.text((px(16), px(12)), title, font=St.font(19, bold=True), fill=St.INK)
    for i, ln in enumerate(St.wrap(note, St.font(17), w - px(32))[:2]):
        d.text((px(16), px(46) + i * px(24)), ln, font=St.font(17), fill=St.INK2)
    return im


_PT_CACHE: dict = {}


def ptable_overlay(key, make):
    """The periodic-table panel, redrawn only when what it shows changes."""
    if _PT_CACHE.get("key") != key:
        _PT_CACHE["key"] = key
        _PT_CACHE["im"] = make()
    return _PT_CACHE["im"]


GRID_BOX = (16, 150, 1264, 700)      # the cameras' wall: clear of the clock, counters, compositions, plots and DAG


def _grid_frame(t: float, t_h: float, sp: float, n: int, t_mode: float) -> np.ndarray:
    R = S("R").part(t_h)
    tl = S("tl")
    sts = tl.grid_st[n]
    cols = 2 if n == 4 else 3
    rows = (len(sts) + cols - 1) // cols
    gx, gy, gw, gh = (px(v) for v in GRID_BOX)
    gap = px(8)
    ch = (gh - gap * (rows - 1)) // rows
    cw = int(ch * 16 / 9)
    if cw * cols + gap * (cols - 1) > gw:
        cw = (gw - gap * (cols - 1)) // cols
        ch = int(cw * 9 / 16)
    x_off = gx + (gw - (cw * cols + gap * (cols - 1))) // 2
    fr = St.blank()
    span = max(3.0, sp * 1.5)
    busy = R.busy_stations(t_h, span)
    pool = S("pool")
    for i, st in enumerate(sts):
        x, y = x_off + (i % cols) * (cw + gap), gy + (i // cols) * (ch + gap)
        sh = _shot_of(A.STATION_SHOT.get(st, ""), st)
        if st == "utah_mxlab" or A.STATION_SHOT.get(st) == "ded" or sh is None:
            cell = _ded_cell(cw, ch, t_h, span)
        else:
            clip, a, b, lab = sh
            r = pool.get(("cell", st, cw), lambda: A.Reader(clip, a, b, cw, ch, speed=1.6, fps=FPS))
            cell = frost(r.frame(t - t_mode + 1.3 * i).copy())
        on = st in busy
        if not on:
            St.dim(cell, 0.40)
        fr[y:y + ch, x:x + cw] = cell[:ch, :cw]
        camps = sorted(busy.get(st, (set(), 0))[0])
        lab = STATION_NAME.get(st, st)
        if st == "utah_mxlab":
            lab += ", no 3-D model yet"
            if any(R.what[k] == "blend_ded" and R.station[k] == st for k in R.active(t_h, span)):
                lab += " · blend"                       # copper's blended-powder screens
        chip = A.label_chip(lab if on else f"{lab}: idle", 16 if n == 9 else 20, pad=6)
        St.paste(fr, chip, x + px(6), y + px(10))
        if on:
            bar_w = cw // max(1, len(camps))
            for j, c in enumerate(camps):
                fr[y:y + px(5), x + j * bar_w:x + (j + 1) * bar_w] = St.CAMP[c]
    return fr


_SHADE: dict = {}


def shade_corner(fr: np.ndarray):
    """Darken the top-left corner and the top edge of a lab clip, where its own gauge table was drawn."""
    if "a" not in _SHADE:
        yy, xx = np.mgrid[0:px(260), 0:px(640)].astype(np.float32)
        r = np.sqrt((xx / px(640)) ** 2 + (yy / px(260)) ** 2)
        a = np.clip(1.15 - r, 0, 1) ** 1.2 * 0.9
        _SHADE["a"] = (256 * (1 - a)).astype(np.uint16)[..., None]
    k = _SHADE["a"]
    sub = fr[:k.shape[0], :k.shape[1]]
    sub[:] = ((sub.astype(np.uint16) * k) >> 8).astype(np.uint8)
    return fr


def _ded_cell(cw, ch, t_h, span) -> np.ndarray:
    """The DED machine has no 3-D render: a close birds-eye crop around its floor spot, lit like the beacons."""
    be = S("be")
    view = "se" if "se" in be.views else next(iter(be.views))
    _, anc = be.anchor_of(view, "utah_mxlab")
    sw, sh = be.views[view]["size"]
    foc = (anc[0] / sw, anc[1] / sh) if anc else (0.5, 0.5)
    big = be.frame(t_h, span, view=view, zoom=2.6, focus=foc, legend=False, offsite=False, labels=False)
    return np.asarray(Image.fromarray(big).resize((cw, ch), Image.BILINEAR)).copy()


def replay_frame(t: float) -> np.ndarray:
    tl, R = S("tl"), S("R")
    t_h, sp = tl.lab(t)
    t_h = min(t_h, R.horizon_h - 1e-3)
    span = max(0.25, sp * 0.6)
    # ------------------------------------------------------------------ the picture
    pov = tl.pov_at(t)
    if pov is not None:
        clip, a, b, lab = pov["shot"]
        r = S("pool").get(("pov", clip, round(a, 2)), lambda: A.Reader(clip, a, b, W, H, speed=1.0, fps=FPS))
        fr = r.frame(t - pov["v0"]).copy()
        k_in = St.ramp(t, pov["v0"], pov["v0"] + 0.35)
        if k_in < 1 and pov is not tl.pov[0]:
            St.dim(fr, 0.35 + 0.65 * k_in)
        mode_txt = None
        ref = _ref_name("flaime_al", pov["design"]) if ROUND3 else None
        card = pov_card(t_h, sp, f"FLAIME alloy #{pov['design']}: {WHAT_WORDS.get(pov['what'], pov['what'])}",
                        (f"The reference alloy {ref}, made first. " if ref else "") + lab[0].upper() + lab[1:])
    else:
        i = tl.phase(t)
        fr = _phase_picture(i, t, t_h, sp)
        t_next = tl.phase_t[i + 1] if i + 1 < len(tl.phase_t) else None
        if t_next is not None and t > t_next - 0.6:                 # crossfade into the next mode
            nxt = _phase_picture(i + 1, t, t_h, sp)
            u = St.ease((t - (t_next - 0.6)) / 0.6)
            fr = (fr.astype(np.float32) * (1 - u) + nxt.astype(np.float32) * u).astype(np.uint8)
        elif t < tl.t_pov + 0.6:
            u = St.ease((t - tl.t_pov) / 0.6)
            St.dim(fr, 0.35 + 0.65 * u)
        scale = "Day by day" if sp < 12 else ("Week by week" if sp < 30 else "Month by month")
        nf = {c: R.wip(t_h, c) for c in D.CAMPAIGNS}
        mode_txt = (f"{scale}: {nf['flaime_al']} FLAIME and {nf['onr_cu']} ONR alloys " +
                    ("in the lab" if ROUND3 else "in progress"),
                    "station cameras, lit while a campaign runs there" if PHASES[i][1] == "grid" else
                    ("the 3-D lab moved by the simulated event log: trays to the openings, units to the docks"
                     if ROUND3 else "the 3-D lab moved by the event log: trays to the openings, units to the docks")
                    if PHASES[i][1] == "3d" else "the whole lab: a beacon lights while a station runs")
    # ------------------------------------------------------------------ overlays
    if mode_txt is None:
        St.paste(fr, card, 0, 0)
    else:
        St.paste(fr, clock_panel(t_h, sp), px(24), px(20))
        pill = now_pill(*mode_txt)
        St.paste(fr, pill, (px(520) + px(1400) - pill.width) // 2, px(24))
    k_right = 1.0                                  # the right-hand panels step aside for the lab's own footage
    if pov is not None and A.anchor_of(pov["shot"][0], pov["shot"][1]) == "r":
        k_right = 1.0 - min(St.ramp(t, pov["v0"], pov["v0"] + 0.5), 1.0 - St.ramp(t, pov["v1"] - 0.5, pov["v1"]))
    St.paste(fr, counters_panel(t_h), px(1446), px(20), k_right)
    P = S("pt")
    if pov is not None:
        des = pov["design"]
        comp = R.designs["flaime_al"].get(str(des), {})
        im = ptable_overlay(("pov", des), lambda: P.composition_panel(
            "flaime_al", comp, px(450), px(300), title=f"FLAIME alloy #{des}, in flight"))
    else:
        q = round(t * 2) / 2                                      # twice a second
        items = []
        for c in D.CAMPAIGNS:
            items += [(c,) + tuple(x) for x in R.in_progress(t_h, c, n=3)]
        items = items[:6]
        key = ("multi", tuple((x[0], x[1], x[3]) for x in items), q if not items else None)
        if items:
            im = ptable_overlay(key, lambda: P.multiples_panel(items, px(450), px(300),
                                                               title="Compositions in the lab" if ROUND3 else
                                                               "Compositions in progress"))
        else:
            im = ptable_overlay(key, lambda: _empty_panel("Compositions in the lab" if ROUND3 else
                                                          "Compositions in progress", "none: both campaigns are "
                                                          "waiting (results, budget or the calendar)"))
    St.paste(fr, im, px(1446), px(186), k_right)
    St.paste(fr, S("plots").draw(t_h), px(1296), px(640), k_right)
    if NARRATE and R3B:                            # round 3b: which seed is on screen, for each of the two
        b = seed_badge3b(t_h)
        St.paste(fr, b, px(866), px(1076) - b.height)
    elif NARRATE and ROUND3:                       # DAL's audit (PR 293): which seed this is, all the way through
        b = seed_badge()
        St.paste(fr, b, px(866), px(1076) - b.height)  # under the moves panel (866, 900, 420 x 104)
    elif NARRATE:                                  # DAL's audit (PR 293 §4): say which seed this is, all the way
        St.paste(fr, seed_badge(), px(866), px(1014))
    dag = S("dag")
    lit = {k: dag.intensity(v) for k, v in R.lit(t_h, span).items()}
    x, y, _, _ = dag.DOCK
    St.paste(fr, dag.overlay(lit, t=t), px(x), px(y))
    if R3B:                                        # a tag as a campaign passes a target; the card at the change of seed
        for im_, k in target_tags(t):
            St.paste(fr, im_, px(1296), px(632) - im_.height, k * k_right)
        k = min(St.ramp(t, tl.switch_t - 0.3, tl.switch_t + 0.4), 1.0 - St.ramp(t, tl.switch_t + SWITCH_CARD_S - 0.6,
                                                                              tl.switch_t + SWITCH_CARD_S))
        if k > 0.003:
            c = switch_card()
            St.paste(fr, c, px(SWITCH_CARD_XY[0]), px(SWITCH_CARD_XY[1]), k)
    return tag_placeholder(fr)


_BADGE: dict = {}
_REFN: dict = {}


def _ref_name(camp: str, design) -> str | None:
    """The reference alloy a design is, if it is one (twin.spaces.REFERENCE, within 0.06 wt% on every element, as
    twin.bench3 marks them), else None."""
    key = (camp, str(design))
    if key not in _REFN:
        name = None
        try:
            sys.path.insert(0, str(D.HERE))
            from twin import spaces as SP
            comp = S("R").designs[camp].get(str(design), {})
            for nm, w in SP.REFERENCE[camp].items():
                if all(abs(comp.get(e, 0.0) - w.get(e, 0.0)) < 0.06 for e in SP.SPACES[camp].elements):
                    name = nm
                    break
        except Exception:                               # noqa: BLE001
            pass
        _REFN[key] = name
    return _REFN[key]


def seed_badge() -> Image.Image:
    """The replayed run among its twelve: the day its aluminium campaign first reaches the target, against the median
    seed's (econ_summary.json), as the narration says it."""
    if "im" not in _BADGE and ROUND3:
        _BADGE["im"] = _seed_badge3()
    if "im" not in _BADGE:
        R, B = S("R"), S("B")
        tg = B["target"]["flaime_al"]
        cur = R.curve_upto("flaime_al", R.horizon_h, "days")
        hit = next((x for x, y in cur if y >= tg - 1e-9), None)
        med = ((S("E").get("accel") or {}).get("flaime_al") or {}).get("median_new")
        n = ((S("E").get("accel") or {}).get("flaime_al") or {}).get("n_new") or 12
        txt = (f"One seed of {n}: here aluminium reaches the target on day {hit:.0f}; the median seed takes "
               f"{med:.0f} days" if hit is not None and med else f"One seed of {n}")
        f = St.font(15)
        lines = St.wrap(txt, f, px(400))[:2]
        w, h = px(420), px(12) + px(20) * len(lines)
        im, d = St.layer(w, h)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(8), fill=St.SURF + (int(255 * St.PANEL_A),))
        for i, ln in enumerate(lines):
            d.text((px(10), px(6) + i * px(20)), ln, font=f, fill=St.INK2)
        _BADGE["im"] = im
    return _BADGE["im"]


def seed_words3() -> str:
    """Which seed the replay is, and where it sits among the 12 (numbers3: the committed runs): the audit's "a
    typical seed (near the median time to target), not the luckiest, and say which seed it is"."""
    from . import numbers3 as N3
    rep = N3.numbers()["replay"]
    al, cu = rep["flaime_al"]["T2"], rep["onr_cu"]["T1"]
    pol = {"bofn3": "time-aware BOFN", "pkgfn3": "time-aware pKGFN"}.get(rep["policy"], rep["policy"])
    out = f"Seed {rep['seed']} of {rep['n']}, {pol}. "
    if al["day"] is not None and al["median"] is not None:
        out += (f"Aluminium: the median seed (halfway target on day {al['day']:.0f}). "
                if abs(al["day"] - al["median"]) < 0.5 else
                f"Aluminium: halfway target on day {al['day']:.0f} (median {al['median']:.0f}). ")
    if cu["day"] is None:
        out += (f"Copper: one of the {rep['n'] - cu['hits']} seeds that never reach the first target (median: day "
                f"{cu['median']:.0f}).")
    else:
        out += f"Copper: first target on day {cu['day']:.0f} (median {cu['median']:.0f})."
    return out


# ------------------------------------------------------------------------------ round 3b: two seeds, each named
TARGET_WORDS = {"T1": "the best existing alloy on this synthetic benchmark", "T2": "the halfway target"}
SWITCH_CARD_XY = (300, 300)       # the card's top left: over the lab's picture, clear of the clock and the panels


def replay3b() -> dict:
    """Round 3b's replay as the numbers have it (numbers3b.numbers()["replay"]): the two parts with their seeds, what
    each is the median seed for and on which day, and the day of the clock at the switch."""
    from . import numbers3b as N3B
    return N3B.numbers()["replay"]


def seed_words3b(i: int) -> str:
    """The badge while part i of round 3b's replay is on screen: which seed it is and what it is the median seed for
    (like3b.json median_seeds), and which seed the rest of the year is."""
    rep_ = replay3b()
    q, o = rep_["parts"][i], rep_["parts"][1 - i]
    camp = {"flaime_al": "aluminium", "onr_cu": "copper"}
    pol = {"bofn3": "time-aware BOFN", "pkgfn3": "time-aware pKGFN"}.get(rep_["policy"], rep_["policy"])
    what = "halfway target" if q["target"] == "T2" else "best existing alloy"
    what_o = "halfway target" if o["target"] == "T2" else "best existing alloy"
    out = (f"Seed {q['seed']} of {rep_['n']}, {pol}, the stocked automated lab. The median seed for "
           f"{camp[q['campaign']]}'s {what}: day {q['day']:.0f}. ")
    out += (f"{'From' if i == 0 else 'Until'} day {rep_['switch_day']}: seed {o['seed']}, the median seed for "
            f"{camp[o['campaign']]}'s {what_o} (day {o['day']:.0f}).")
    return out


def seed_badge3b(t_h: float) -> Image.Image:
    i = S("R").part_index(t_h)
    if ("3b", i) not in _BADGE:
        f = St.font(13.5)
        lines = St.wrap(seed_words3b(i), f, px(404))[:4]
        w, h = px(420), px(12) + px(19) * len(lines)
        im, d = St.layer(w, h)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(8), fill=St.SURF + (242,))
        for j, ln in enumerate(lines):
            d.text((px(10), px(6) + j * px(19)), ln, font=f, fill=St.INK2)
        _BADGE[("3b", i)] = im
    return _BADGE[("3b", i)]


TAG_S = 8.0                       # seconds a target tag stays above the plots


def target_events() -> list:
    """Round 3b's replay: [(seconds into the replay, campaign, words, small words)] for each target a campaign passes
    while its run is on screen (the first run before the switch, the second after), from each run's own days."""
    if "events" not in _BADGE:
        tl, rep_ = S("tl"), replay3b()
        camp = {"flaime_al": "FLAIME (aluminium)", "onr_cu": "ONR (copper)"}
        out = []
        for i, q in enumerate(rep_["parts"]):
            for c in D.CAMPAIGNS:
                d1, d2 = q["days"][c]["T1"], q["days"][c]["T2"]
                hits = q["arm_hits"][c]
                ev = []
                if d1 is not None and d2 is not None and abs(d1 - d2) < 0.5:
                    ev.append((d1, "past both targets", "T2"))
                else:
                    if d1 is not None:
                        ev.append((d1, "past the best existing alloy on this synthetic benchmark", "T1"))
                    if d2 is not None:
                        ev.append((d2, "past the halfway target", "T2"))
                for day, words, tn in ev:
                    on_screen = (day * D.HPD < rep_["switch_h"]) if i == 0 else (day * D.HPD >= rep_["switch_h"])
                    if not on_screen:
                        continue
                    med = (q["campaign"], q["target"]) == (c, tn)
                    small = (f"seed {q['seed']}: the median seed for this target ({hits[tn]} of {q['of']} seeds reach "
                             "it)" if med else f"seed {q['seed']}; {hits[tn]} of {q['of']} seeds reach it")
                    out.append((float(np.interp(day * D.HPD, tl.lab_g, tl.vg)), c,
                                f"{camp[c]}: {words}, day {day:.0f}", small))
        _BADGE["events"] = sorted(out)
    return _BADGE["events"]


def target_tags(t: float) -> list:
    """[(image, opacity)] of the tags on screen at t seconds into the replay."""
    out = []
    for v, c, words, small in target_events():
        k = min(St.ramp(t, v, v + 0.5), 1.0 - St.ramp(t, v + TAG_S - 0.6, v + TAG_S))
        if k <= 0.003:
            continue
        key = ("tag", v, c)
        if key not in _BADGE:
            w = px(600)
            f1, f2 = St.font(17, bold=True), St.font(14)
            lines = St.wrap(words, f1, w - px(52))[:2]
            h = px(14) + px(24) * len(lines) + px(24)
            im, d = St.layer(w, h)
            d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(10), fill=St.SURF + (244,), outline=St.CAMP[c] + (255,),
                                width=px(2))
            d.rounded_rectangle((px(14), px(13), px(28), px(27)), radius=px(3), fill=St.CAMP[c] + (255,))
            for j, ln in enumerate(lines):
                d.text((px(38), px(8) + j * px(24)), ln, font=f1, fill=St.INK)
            d.text((px(38), px(10) + px(24) * len(lines)), small, font=f2, fill=St.INK2)
            _BADGE[key] = im
        out.append((_BADGE[key], k))
    return out[-1:]


def switch_card() -> Image.Image:
    """The card at the switch: the second seed, what it is the median seed for, and where its own year stands."""
    if "card" not in _BADGE:
        rep_ = replay3b()
        a, b = rep_["parts"]
        camp = {"flaime_al": "aluminium", "onr_cu": "copper"}
        w, h = px(940), px(250)
        im, d = St.layer(w, h)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(16), fill=St.SURF + (244,), outline=St.RULE + (255,),
                            width=px(2))
        d.text((px(32), px(22)), f"From here: seed {b['seed']} of {rep_['n']}", font=St.font(40, bold=True),
               fill=St.INK)
        d.text((px(32), px(80)), f"the median seed for {camp[b['campaign']]}'s best existing alloy on this synthetic "
               f"benchmark: day {b['day']:.0f}", font=St.font(22, bold=True), fill=St.INK)
        y = px(124)
        for ln in St.wrap(f"The same simulated lab and policy (time-aware BOFN), another seed's year. Days 1 to "
                          f"{rep_['switch_day']} were seed {a['seed']}, the median seed for {camp[a['campaign']]}'s "
                          f"halfway target (day {a['day']:.0f}). The plots now draw seed {b['seed']}'s own year so "
                          f"far: {rep_['b_so_far']}.", St.font(19), w - px(64))[:4]:
            d.text((px(32), y), ln, font=St.font(19), fill=St.INK2)
            y += px(27)
        _BADGE["card"] = im
    return _BADGE["card"]


def _seed_badge3() -> Image.Image:
    f = St.font(13.5)
    lines = St.wrap(seed_words3(), f, px(404))[:4]
    w, h = px(420), px(12) + px(19) * len(lines)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(8), fill=St.SURF + (242,))
    for i, ln in enumerate(lines):
        d.text((px(10), px(6) + i * px(19)), ln, font=f, fill=St.INK2)
    return im


def _phase_picture(i: int, t: float, t_h: float, sp: float) -> np.ndarray:
    tl = S("tl")
    p = PHASES[i]
    t0 = tl.phase_t[i]
    t1 = tl.phase_t[i + 1] if i + 1 < len(tl.phase_t) else tl.dur
    if p[1] == "grid":
        return _grid_frame(t, t_h, sp, p[2], t0)
    if p[1] == "3d":
        from . import lab3d_cut as LC
        return LC.replay_picture(i, t, t_h, sp)
    be = S("be")
    u = St.ease((t - t0) / max(1e-6, t1 - t0))
    zoom = p[3] + (p[4] - p[3]) * u
    view = p[2] if p[2] in be.views else "high"
    foc = be.best_focus(view, zoom)
    return be.frame(t_h, max(1.0, sp * 0.8), view=view, zoom=zoom, focus=foc)


# ================================================================================ figures, results, takeaway, notes
def figures_frame(t: float) -> np.ndarray:
    fr = np.array((S("figs3") if ROUND3 else S("figs")).explain_frame(t), copy=True)
    dag = S("dag")
    x, y, _, _ = dag.DOCK
    St.paste(fr, dag.overlay({}, alpha=0.82), px(x), px(y))
    return tag_placeholder(fr)


def results_frame(t: float) -> np.ndarray:
    fr = np.array((S("figs3") if ROUND3 else S("figs")).results_frame(t), copy=True)
    return tag_placeholder(fr)


def takeaway_frame(t: float) -> np.ndarray:
    return tag_placeholder(np.array((S("figs3") if ROUND3 else S("figs")).takeaway_frame(t), copy=True))


def labs_frame(t: float) -> np.ndarray:                # round 3b: the lab comparison, like for like
    return tag_placeholder(np.array(S("figs3").labs_frame(t), copy=True))


def changes_frame(t: float) -> np.ndarray:             # round 3: what changed in the twin
    return np.array(S("figs3").changes_frame(t), copy=True)


def assume_frame(t: float) -> np.ndarray:              # round 3: the atomizer's design targets against the record
    return np.array(S("figs3").assume_frame(t), copy=True)


NOTES_DURATION = 26.0 if NARRATE else 15.0          # the closing line takes 24 s
NOTES = [
    ("Real", ["The lab's design: PR 318's 3-D renders, makers' published sizes",
              "The atomizer footage and photos: the lab's own runs (DAL #159, #219)",
              "Search spaces and rules: the FLAIME and ONR proposals",
              "Prices and import reliance: USGS Mineral Commodity Summaries 2026",
              "Equipment prices, rates and wages: econ_summary.json's sources"]),
    ("Assumed", ["Station times, fees and calendars (twin/facility.py)",
                 "Outside facilities' booking and turnaround times",
                 "Outside users' demand for the lab's spare hours",
                 "Each assumption is marked in notes/twin.md"]),
    ("Simulated", ["The alloys' properties: textbook forms calibrated on reference alloys",
                   "Every measurement, with noise (twin/instruments)",
                   "Both campaigns, every booking and every result: the twin's event log",
                   "The optimizer's choices (twin/policies.py, twin/opt/)"]),
]


# the narrated cut's notes, with what DAL's audit (digital-alloy-lab PR 293 §4) found missing from "Assumed" and its
# wording for the instruments' noise
NOTES_NARRATED = [
    NOTES[0],
    ("Assumed", ["Station times, fees and calendars (twin/facility.py)",
                 "Outside facilities' booking and turnaround times",
                 "Outside users' demand for the lab's spare hours",
                 "The automated lab's feedstock stock on day 0; the atomizer's failure rate and yield; who staffs the "
                 "automated lab",
                 "Each assumption is marked in notes/twin.md"]),
    ("Simulated", ["The alloys' properties: textbook forms calibrated on reference alloys",
                   "Every measurement, with modelled noise not yet calibrated on the lab's instruments",
                   "Both campaigns, every booking and every result: the twin's event log",
                   "The optimizer's choices (twin/policies.py, twin/opt/)"]),
]


# round 3's notes: what DAL's audit (PR 293, sections 1 row 13 and 2) found missing from "Assumed", and round 3's own
# choices (notes/twin_round3.md, Limits)
NOTES_R3 = [
    ("Real", ["The lab's design: PR 318's 3-D renders, makers' published sizes",
              "The atomizer footage and photos: the lab's own runs (DAL #159, #219)",
              "Search spaces and rules: the FLAIME and ONR proposals",
              "Prices and import reliance: USGS Mineral Commodity Summaries 2026",
              "Equipment prices, rates and wages: econ_summary.json's sources"]),
    ("Assumed", ["The atomizer's runs a week, failure rate and yield: design targets, not the lab's record",
                 "Station times, fees, calendars and capacities (twin/facility.py)",
                 "The automated lab's stock on day 0, and who staffs it",
                 "Round 3's choices: the spending plan, the atomizer's weekly split, robot and operator times",
                 "Outside facilities' booking and turnaround times",
                 "Each assumption is marked in notes/twin_round3.md"]),
    ("Simulated", ["The alloys' properties: textbook forms calibrated on reference alloys",
                   "Every measurement, with modelled noise not yet calibrated on the lab's instruments",
                   "Both campaigns, every booking and every result: the twin's event log",
                   "The policies' choices (twin/opt/policies3.py, net3.py)"]),
]


# round 3b's notes: round 3's, with what round 3b adds to "Assumed" (its two stock arms) and where its results are
NOTES_R3B = [
    NOTES_R3[0],
    ("Assumed", ["The atomizer's runs a week, failure rate and yield: design targets, not the lab's record",
                 "Station times, fees, calendars and capacities (twin/facility.py)",
                 "The stock: about a month's metal, bought on day 0 (in round 3b's runs, for either lab)",
                 "Round 3's choices: the spending plan, the atomizer's weekly split, robot and operator times",
                 "Outside facilities' booking and turnaround times",
                 "Each assumption is marked in notes/twin_round3.md and twin_round3b.md"]),
    NOTES_R3[2],
]


def notes_frame(t: float) -> np.ndarray:
    fr = St.blank()
    im, d = St.layer()
    d.text((px(80), px(70)), "A synthetic benchmark", font=St.font(48, bold=True), fill=St.INK)
    d.text((px(80), px(138)), "What is real, what is assumed and what is simulated in this video",
           font=St.font(26), fill=St.INK2)
    for i, (head, items) in enumerate(NOTES_R3B if R3B else NOTES_R3 if ROUND3 else
                                      (NOTES_NARRATED if NARRATE else NOTES)):
        x = px(80) + i * px(600)
        k = St.ramp(t, 0.4 + 0.5 * i, 1.2 + 0.5 * i)
        d.text((x, px(230)), head, font=St.font(32, bold=True), fill=St.mix(St.BG, St.INK, k))
        y = px(290)
        for it in items:
            for j, ln in enumerate(St.wrap(it, St.font(22), px(540))):
                d.text((x + (px(22) if j else 0), y), ("- " if j == 0 else "") + ln, font=St.font(22),
                       fill=St.mix(St.BG, St.INK2, k))
                y += px(32)
            y += px(14)
    meta = _meta_lines()
    y = px(780)
    for ln in meta:
        d.text((px(80), y), ln, font=St.font(21), fill=St.INK2)
        y += px(32)
    St.paste(fr, im, 0, 0, St.window(t, 0.0, NOTES_DURATION, 0.6))
    return fr


def _meta_lines() -> list:
    R = S("R")
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=D.HERE).stdout.strip()
    if R3B:
        a, b = R.runs
        return [f"Replayed runs: {a.path.name} to day {replay3b()['switch_day']}, then {b.path.name} (seeds {a.seed} "
                f"and {b.seed} of 12, policy {a.policy})",
                "Results: out/twin3b/like3b.json and tables.md (the lab comparison), out/twin3/runs and fig/numbers.json; "
                "the cards' numbers: out/twin3b/video/numbers.json",
                f"Code: github.com/vertical-cloud-lab/byu-vcl, vertical-lab/twin/video (commit {commit}); "
                "write-up in notes/twin_round3b.md, twin_round3.md and twin_video.md",
                "Renders: PR 318's chapters, reused. Narration: a synthetic voice, Kokoro v1.0 (open weights, run "
                "locally), script in twin/video/narration3b.json"]
    if ROUND3:
        return [f"Replayed run: {R.path.name} (seed {R.seed} of 12, policy {R.policy}); {len(R.ev):,} station "
                f"bookings over {R.horizon_days:.0f} days",
                "Results: out/twin3/runs, fig/numbers.json and econ/econ_summary.json; the cards' numbers: "
                "out/twin3/video/numbers.json",
                f"Code: github.com/vertical-cloud-lab/byu-vcl, vertical-lab/twin/video (commit {commit}); "
                "write-up in notes/twin_round3.md and notes/twin_video.md",
                "Renders: PR 318's chapters, reused. Narration: a synthetic voice, Kokoro v1.0 (open weights, run "
                "locally), script in twin/video/narration3.json"]
    return [f"Replayed run: {R.path.name} (policy {R.policy}, facility {R.facility}); "
            f"{len(R.ev):,} bookings over {R.horizon_days:.0f} days",
            f"Benchmark: out/twin2/bench2_summary.json; economics: out/twin2/econ/econ_summary.json",
            f"Code: github.com/vertical-cloud-lab/byu-vcl, vertical-lab/twin/video (commit {commit}); "
            "write-up in notes/twin.md and notes/twin_video.md",
            "Renders: PR 318's chapters, reused. " + (
                "Narration: a synthetic voice, Kokoro v1.0 (open weights, run locally), script in "
                "twin/video/narration.json" if NARRATE else "Captions only, no narration.")]


# ================================================================================================== the cut
def segments() -> list:
    """[(name, duration, frame function, chapter title)] in order."""
    dag = S("dag")
    F = S("figs")
    if R3B:
        F3 = S("figs3")
        return [
            ("title", TITLE_DUR, title_frame, "A simulated year of alloy discovery: round 3b, like for like"),
            ("simulated", SIM_DUR, simulated_frame, "What is simulated: the lab and two search spaces"),
            ("changes", float(F3.CHANGES_DURATION), changes_frame, "Rounds 3 and 3b: what changed in the twin"),
            ("dag", float(dag.DURATION), dag.intro_frame, "The function networks"),
            ("figures", float(F3.EXPLAIN_DURATION), figures_frame, "The figures we track, the two targets, and "
                                                                 "like for like"),
            ("assume", float(F3.ASSUME_DURATION), assume_frame, "The atomizer: design targets, not demonstrated "
                                                               "rates"),
            ("replay", REPLAY_DUR, replay_frame, "The campaign year, replayed"),
            ("results", float(F3.RESULTS_DURATION), results_frame, "Results: the policies in the automated lab"),
            ("labs", float(F3.LABS_DURATION), labs_frame, "The lab comparison, like for like"),
            ("takeaway", float(F3.TAKEAWAY_DURATION), takeaway_frame, "The takeaway"),
            ("notes", NOTES_DURATION, notes_frame, "Notes: real, assumed, simulated"),
        ]
    if ROUND3:
        F3 = S("figs3")
        return [
            ("title", 8.0, title_frame, "Title"),
            ("simulated", SIM_DUR, simulated_frame, "What is simulated: the lab and two search spaces"),
            ("changes", float(F3.CHANGES_DURATION), changes_frame, "Round 3: what changed in the twin"),
            ("dag", float(dag.DURATION), dag.intro_frame, "The function networks"),
            ("figures", float(F3.EXPLAIN_DURATION), figures_frame, "The figures we track, and the two targets"),
            ("assume", float(F3.ASSUME_DURATION), assume_frame, "The atomizer: design targets, not demonstrated "
                                                               "rates"),
            ("replay", REPLAY_DUR, replay_frame, "The campaign year, replayed"),
            ("results", float(F3.RESULTS_DURATION), results_frame, "Results"),
            ("takeaway", float(F3.TAKEAWAY_DURATION), takeaway_frame, "The takeaway"),
            ("notes", NOTES_DURATION, notes_frame, "Notes: real, assumed, simulated"),
        ]
    return [
        ("title", 8.0, title_frame, "Title"),
        ("simulated", SIM_DUR, simulated_frame, "What is simulated: the lab and two search spaces"),
        ("dag", float(dag.DURATION), dag.intro_frame, "The function networks"),
        ("figures", float(F.EXPLAIN_DURATION), figures_frame, "The figures we track"),
        ("replay", REPLAY_DUR, replay_frame, "The campaign year, replayed"),
        ("results", float(F.RESULTS_DURATION), results_frame, "Results"),
        ("takeaway", float(F.TAKEAWAY_DURATION), takeaway_frame, "The takeaway"),
        ("notes", NOTES_DURATION, notes_frame, "Notes: real, assumed, simulated"),
    ]


def plan_record() -> dict:
    """Start times of the segments and the replay's chapter marks (for the description)."""
    segs = segments()
    out, t = [], 0.0
    chapters = []
    for name, dur, _, title in segs:
        out.append(dict(name=name, start_s=round(t, 2), seconds=round(dur, 2), title=title))
        if name == "replay":
            for tt, ttl in S("tl").marks():
                chapters.append((round(t + tt, 1), ttl))
        else:
            chapters.append((round(t, 1), title))
        t += dur
    return dict(segments=out, total_s=round(t, 2), chapters=chapters)


PREVIEW_SLICES = [  # (segment, from s, seconds): about 50 s that touch every part of the pipeline
    ("title", 1.0, 3.0), ("simulated", 4.0, 3.0), ("simulated", 22.0, 3.5), ("dag", 20.0, 4.0), ("dag", 95.0, 4.0),
    ("figures", 44.0, 4.0), ("replay", 8.0, 5.0), ("replay", 40.0, 3.0), ("replay", None, 4.0),
    ("replay", "grid9", 4.0), ("replay", "be", 5.0), ("replay", "be_end", 3.0), ("results", 14.0, 3.5),
    ("results", 70.0, 3.0), ("takeaway", 5.0, 3.0), ("notes", 4.0, 2.0)]


def _resolve_slices(slices) -> list:
    tl = S("tl")
    segs = {n: (d, f) for n, d, f, _ in segments()}
    out = []
    for name, a, dur in slices:
        if name == "replay" and not isinstance(a, (int, float)):
            if a is None:
                a = tl.phase_t[0] + 3.0
            elif a == "grid9":
                a = tl.phase_t[1] + 4.0
            elif a == "be":
                a = tl.phase_t[2] + 6.0
            elif a == "be_end":
                a = tl.dur - 6.0
        a = min(float(a), segs[name][0] - dur)
        out.append((name, max(0.0, a), dur))
    return out


def encoder(path: Path, preset: str, fps_in: int = FPS):
    return subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate",
         str(fps_in), "-i", "-", "-an", "-c:v", "libx264", "-preset", preset, "-crf", "20", "-pix_fmt", "yuv420p",
         "-threads", "2", "-r", str(FPS), "-g", str(2 * FPS), "-video_track_timescale", "15360", str(path)],
        stdin=subprocess.PIPE)


FADE = 0.35                      # seconds of fade at each end of a segment


def render_piece(name: str, a: float, b: float, out: Path, preset: str, fps_in: int = FPS) -> dict:
    """Frames [a, b) of one segment into an MP4 (the unit the workers run)."""
    segs = {n: (f, d) for n, d, f, _ in segments()}
    fn, dur = segs[name]
    enc = encoder(out, preset, fps_in)
    n = int(round((b - a) * fps_in))
    t0 = time.time()
    c0 = time.process_time()
    for k in range(n):
        tt = a + k / fps_in
        fr = fn(tt)
        kf = min(1.0, tt / FADE, (dur - tt) / FADE)             # every segment fades in from black and out to it
        if kf < 1.0:
            fr = St.dim(np.array(fr, copy=True), max(0.0, kf))
        enc.stdin.write(np.ascontiguousarray(fr, np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    S("pool").close()
    return dict(name=name, a=a, b=b, frames=n, wall=round(time.time() - t0, 1), cpu=round(time.process_time() - c0, 1))


def _run_pieces(pieces: list, preset: str, workers: int) -> list:
    """Each piece in its own process (python -m twin.video.compose piece ...), `workers` at a time."""
    TMP.mkdir(parents=True, exist_ok=True)
    todo = list(pieces)
    running: list = []
    logs = []
    while todo or running:
        while todo and len(running) < workers:
            name, a, b, out = todo.pop(0)
            p = subprocess.Popen([sys.executable, "-m", "twin.video.compose", "piece", name, f"{a:.4f}", f"{b:.4f}",
                                  str(out), preset], cwd=D.HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True)
            running.append((p, name, a, b, out, time.time()))
        time.sleep(0.5)
        for item in list(running):
            p = item[0]
            if p.poll() is not None:
                running.remove(item)
                txt = p.stdout.read()
                logs.append(txt.strip().splitlines()[-1] if txt.strip() else "")
                print(f"  {item[1]} {item[2]:.1f}-{item[3]:.1f}: rc {p.returncode} {logs[-1][:160]}", flush=True)
                if p.returncode != 0:
                    print(txt[-3000:], flush=True)
                    raise SystemExit(f"piece {item[1]} failed")
    return logs


def concat(parts: list, dst: Path):
    lst = TMP / f"{dst.stem}_list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)


def build(kind: str):
    t_start = time.time()
    workers = int(os.environ.get("TWIN_VIDEO_WORKERS", "2"))
    preset = os.environ.get("TWIN_VIDEO_PRESET", "veryfast" if kind == "preview" else "medium")
    VID.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    rec = plan_record()
    if kind == "final3d" and not LAB3D:
        raise SystemExit("final3d needs TWIN_VIDEO_LAB3D=1 in the environment (the pieces run in their own processes)")
    if kind == "final3d":
        from . import lab3d_cut as LC
        LC.run_jobs(LC.replay_jobs(), workers)       # the 3-D track first (each worker builds the scene once)
    if kind == "preview":
        sl = _resolve_slices(PREVIEW_SLICES)
        pieces = [(n, a, a + d, TMP / f"preview_{i:02d}_{n}.mp4") for i, (n, a, d) in enumerate(sl)]
        dst = VID / "preview.mp4"
    else:
        pieces = []
        CH = 45.0                                       # long segments in chunks, so the workers share them
        for s in rec["segments"]:
            a, dur = 0.0, s["seconds"]
            k = 0
            while a < dur - 1e-6:
                b = min(dur, a + CH)
                if dur - b < 8.0:
                    b = dur
                pieces.append((s["name"], a, b, TMP / f"{kind}_{len(pieces):02d}_{s['name']}_{k}.mp4"))
                a, k = b, k + 1
        pieces.sort(key=lambda p: -(p[2] - p[1]) * (2.0 if p[0] == "replay" else 1.0))   # longest first
        order = {id(p): i for i, p in enumerate(pieces)}
        dst = VID / (("campaign_lab3d" if kind == "final3d" else "campaign") + NAR + ".mp4")
    print(f"{kind}: {len(pieces)} pieces, {workers} workers, preset {preset}", flush=True)
    logs = _run_pieces(pieces, preset, workers)
    parts = [p[3] for p in sorted(pieces, key=lambda p: str(p[3]))]
    concat(parts, dst)
    if NARRATE and kind in ("final", "final3d"):
        rec["narration"] = narrate(dst, rec, kind)
    cpu = 0.0
    for ln in logs:
        try:
            cpu += json.loads(ln).get("cpu", 0.0)
        except Exception:                               # noqa: BLE001
            pass
    info = dict(kind=kind, file=str(dst.relative_to(D.HERE)), seconds=_duration(dst), wall_s=round(time.time() -
                t_start, 1), python_cpu_s=round(cpu, 1), preset=preset, workers=workers, placeholder=placeholder(),
                replay=([r.path.name for r in S("R").runs] if R3B else S("R").path.name),
                built_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))
    rec.update(info)
    (VID / f"{kind}{NAR if kind in ('final', 'final3d') else ''}_record.json").write_text(json.dumps(rec, indent=1) +
                                                                                       "\n")
    if kind == "final":
        from . import meta
        meta.write(rec, narrated=NARRATE)
        sheet(dst, VID / f"sheet{NAR}.png", rec)
    if kind == "final3d":
        from . import meta
        if R3B:
            from . import meta3b
            meta3b.write(rec)
        elif ROUND3:
            from . import meta3
            meta3.write(rec)
        else:
            meta.write(rec, lab3d=True, narrated=NARRATE)
        sheet(dst, VID / f"sheet_lab3d{NAR}.png", rec)
    print(json.dumps(info), flush=True)
    return rec


def _duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 2)
    except ValueError:
        return 0.0


def sheet(video: Path, dst: Path, rec: dict, n: int = 12):
    """Twelve frames across the cut, 4 x 3, each named by its chapter."""
    total = rec.get("seconds") or rec["total_s"]
    marks = sorted(rec["chapters"])
    ts = [total * (i + 0.5) / n for i in range(n)]
    w, h = 480, 270
    out = Image.new("RGB", (4 * w, 3 * (h + 34)), St.BG)
    d = ImageDraw.Draw(out)
    for i, tt in enumerate(ts):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{tt:.2f}", "-i", str(video), "-vframes", "1", "-f",
                            "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-"], capture_output=True)
        if len(r.stdout) >= w * h * 3:
            im = Image.fromarray(np.frombuffer(r.stdout[:w * h * 3], np.uint8).reshape(h, w, 3))
            out.paste(im, ((i % 4) * w, (i // 4) * (h + 34)))
        ch = [m for m in marks if m[0] <= tt]
        lab = f"{int(tt // 60)}:{int(tt % 60):02d}  {ch[-1][1] if ch else ''}"
        d.text(((i % 4) * w + 8, (i // 4) * (h + 34) + h + 6), lab[:52], font=St.font(15 / St.S), fill=St.INK)
    out.save(dst, optimize=True)


def stills(times: list):
    """Frames of the full cut at the given times (s), to /tmp/vid/cut_<t>.png."""
    segs = segments()
    starts, t = [], 0.0
    for name, dur, fn, _ in segs:
        starts.append((t, t + dur, name, fn))
        t += dur
    Path("/tmp/vid").mkdir(exist_ok=True)
    for tt in times:
        for a, b, name, fn in starts:
            if a <= tt < b:
                c0 = time.process_time()
                fr = fn(tt - a)
                Image.fromarray(np.ascontiguousarray(fr)).save(f"/tmp/vid/cut_{tt:06.1f}.png")
                print(f"{tt:7.1f} s  {name} +{tt - a:6.1f}  {1000 * (time.process_time() - c0):6.0f} ms cpu",
                      flush=True)
                break


# ================================================================================================ the narration
def narrate(video: Path, rec: dict, kind: str) -> dict:
    """The narration (twin/video/narration.py) placed on the cut as built, mixed into one track and muxed in as AAC;
    its subtitles beside the cut (<stem>.srt) and in out/twin2/video/narration/narration.srt."""
    from . import narration as N
    total = _duration(video) or rec["total_s"]
    wav = TMP / f"{video.stem}_narration.wav"
    placed = N.track(rec, N.marks(rec), total, wav, video.with_suffix(".srt"))
    if kind in ("final", "final3d"):
        (N.NDIR / "narration.srt").write_text(video.with_suffix(".srt").read_text())
    mux(video, wav)
    return dict(voice=f"Kokoro v1.0 {N.VOICE}, speed {N.SPEED}", lines=len(placed),
                spoken_s=round(sum(p["end"] - p["t"] for p in placed), 1), placed=placed)


LOUDNESS = dict(I=-16.0, TP=-1.5, LRA=11.0)        # the track's integrated loudness (LUFS) and true peak (dBTP)


def loudnorm_filter(wav: Path) -> str:
    """ffmpeg's loudnorm, two passes: measure the narration track, then one linear gain to LOUDNESS (YouTube plays
    at -14 LUFS and only turns louder videos down; the lines as levelled come to about -20.5 LUFS)."""
    t = LOUDNESS
    base = f"loudnorm=I={t['I']}:TP={t['TP']}:LRA={t['LRA']}"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav), "-af", base + ":print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return (f"{base}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
            f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


def mux(video: Path, wav: Path):
    """The narration track into the cut, the picture copied: loudness-normalised (loudnorm_filter), AAC 192k, 48 kHz,
    stereo (the mono voice in both). The video may already carry a track: it is replaced."""
    silent = video.with_name(video.stem + "_silent.mp4")
    video.replace(silent)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", loudnorm_filter(wav), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-ac", "2", "-shortest", "-movflags", "+faststart", str(video)], check=True)
    silent.unlink()


def narrated_preview(seconds: float = 60.0, render: bool = True) -> dict:
    """About a minute of the narrated cut: the opening (the title and the lab, what is simulated and what is real),
    then the switch to the whole lab from above, each with its own lines; their audio is cut from the full cut's
    narration track at the same times, so the preview hears exactly what the cut will."""
    import soundfile as sf
    from . import narration as N
    rec = plan_record()
    mk = N.marks(rec)
    seg0 = {s["name"]: s["start_s"] for s in rec["segments"]}
    TMP.mkdir(parents=True, exist_ok=True)
    full = TMP / "npreview_full.wav"
    placed = N.track(rec, mk, rec["total_s"], full)
    ends = {p["id"]: p["end"] for p in placed}
    a_end = max(seg0["simulated"] + SIM_LAB, ends.get("open2", 0.0) + 0.8)       # the opening: to the lab footage's end
    opening = [("title", 0.0, seg0["simulated"]), ("simulated", 0.0, a_end - seg0["simulated"])]
    r0 = seg0["replay"]
    if "replay.lab3d" in mk:                            # the animated cut: the 3-D lab taking over, then from above
        t1, t2 = mk["replay.lab3d"], mk["replay.from_above"]
        e1 = ends.get("lab0", t1 + 13.0) + 1.0
        slices = opening + [("replay", t1 - 0.7 - r0, e1 - t1 + 0.7)]
        used = a_end + (e1 - t1 + 0.7)
        slices.append(("replay", t2 - 1.2 - r0, max(4.0, seconds - used)))
    else:
        t_lab = mk.get("replay.from_above", mk.get("replay.whole_lab", r0 + 158.0))
        b0 = t_lab - 2.5
        b1 = min(t_lab + max(0.0, seconds - a_end - 2.5), rec["total_s"])
        slices = opening + [("replay", b0 - r0, b1 - b0)]
    pieces = [(n, a, a + d, TMP / f"npreview_{i:02d}_{n}.mp4") for i, (n, a, d) in enumerate(slices)]
    dst = VID / "preview_narrated.mp4"
    if render:                                          # render=False: the record and metadata of the file as built
        workers = int(os.environ.get("TWIN_VIDEO_WORKERS", "2"))
        preset = os.environ.get("TWIN_VIDEO_PRESET", "medium")
        _run_pieces(pieces, preset, workers)
        concat([p[3] for p in pieces], dst)
        y, sr = sf.read(str(full), dtype="float32")
        cut = [y[int(round((seg0[n] + a) * sr)):int(round((seg0[n] + a) * sr)) + int(round(d * sr))]
               for n, a, d in slices]
        wav = TMP / "npreview.wav"
        sf.write(str(wav), np.concatenate(cut), sr, subtype="PCM_16")
        mux(dst, wav)
    shift, k = [], 0.0                                  # windows of the cut the preview plays without a break
    for n, a, d in slices:
        x0 = seg0[n] + a
        if shift and abs(shift[-1][1] - x0) < 0.05:
            shift[-1] = (shift[-1][0], x0 + d, shift[-1][2])
        else:
            shift.append((x0, x0 + d, k))
        k += d
    lines = [dict(p, t_preview=round(p["t"] - x0 + k0, 2)) for p in placed for x0, x1, k0 in shift
             if x0 - 0.05 <= p["t"] and p["end"] <= x1 + 0.05]
    out = dict(file=str(dst.relative_to(D.HERE)), seconds=_duration(dst), slices=[dict(segment=n, start=round(a, 2),
               seconds=round(d, 2)) for n, a, d in slices], lines=lines,
               built_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))
    (VID / "preview_narrated_record.json").write_text(json.dumps(out, indent=1) + "\n")
    preview_meta(out)
    print(json.dumps({k: v for k, v in out.items() if k != "lines"}), flush=True)
    return out


def preview_meta(rec: dict) -> dict:
    """youtube_meta_preview_narrated.json: the narrated preview's title and description (unlisted, for review)."""
    from . import narration as N
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=D.HERE).stdout.strip()
    said = "".join(f"\n{int(x['t_preview'] // 60)}:{int(x['t_preview'] % 60):02d}  {x['text']}" for x in rec["lines"])
    desc = ("A preview, for review: the narrated campaign video's opening (what is simulated and what is real), then "
            "the replay's switch from day 1 to the animated 3-D lab and the first view of the whole lab from above. "
            "Simulated, not lab results.\n\n"
            f"The voice is synthetic: Kokoro v1.0 (open weights, run locally), its stock voice {N.VOICE}, no voice "
            "cloned or imitated. What it says, at its times in this preview:" + said + "\n\n"
            f"Code: https://github.com/vertical-cloud-lab/byu-vcl/tree/{commit}/vertical-lab/twin/video "
            "(narration.py, narration.json)\nPR: https://github.com/vertical-cloud-lab/byu-vcl/pull/393\n")
    meta = dict(title="Preview: the campaign video, narrated (digital twin, simulated benchmark)", description=desc,
                tags=["vertical cloud lab", "BYU", "digital twin", "laboratory automation", "self-driving lab",
                      "narrated", "simulated"], categoryId="28", privacy="unlisted", notifySubscribers=False,
                file=rec["file"], seconds=rec["seconds"], commit=commit)
    (VID / "youtube_meta_preview_narrated.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return meta


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "preview"
    if cmd == "piece":
        name, a, b, out, preset = args[1], float(args[2]), float(args[3]), Path(args[4]), args[5]
        print(json.dumps(render_piece(name, a, b, out, preset)), flush=True)
    elif cmd in ("preview", "final", "final3d"):
        build(cmd)
    elif cmd == "npreview":                             # the narrated preview: the opening and the switch to the lab
        narrated_preview(render="--meta-only" not in args)
    elif cmd == "remux":                                # remux <video> <wav>: the narration track again, picture copied
        mux(Path(args[1]), Path(args[2]))
    elif cmd == "stills":
        stills([float(x) for x in args[1:]])
    elif cmd == "plan":
        rec = plan_record()
        for s in rec["segments"]:
            print(f"{s['start_s']:7.1f}  {s['seconds']:6.1f}  {s['name']:10s} {s['title']}")
        tl = S("tl")
        print(f"replay: day 1 in {tl.t_pov:.1f} s ({len(tl.pov)} shots, to lab hour {tl.l_pov:.1f}); phases at",
              [round(x, 1) for x in tl.phase_t])
        for s in tl.pov:
            print(f"   {s['v0']:5.1f}-{s['v1']:5.1f}  lab {s['l0']:6.2f}-{s['l1']:6.2f} h  {s['what']:10s} "
                  f"{s['station']:10s} {s['shot'][3]}")
        for x in (tl.t_pov, tl.phase_t[1], tl.phase_t[2], tl.phase_t[4], tl.dur - 1):
            lh, sp = tl.lab(x)
            print(f"   t {x:6.1f} s: day {lh / 24:6.1f}, {sp:6.2f} h/s")
        print("grid stations", tl.grid_st)
        print("chapters", rec["chapters"], "total", rec["total_s"])
    else:
        raise SystemExit(__doc__)

"""The two-year replay of rounds 5 and later: one seed, both campaigns, from the day the money arrives to the horizon.

    TWIN_VIDEO_ROUND=5 python -m twin.video.replay5 plan            # the clock, the phases and the 3-D jobs
    TWIN_VIDEO_ROUND=5 python -m twin.video.replay5 stills 20 150   # frames at those seconds -> /tmp/vid/replay5_*.png

The run is data5.Replay5("auto"): the automated lab's seed that the round's notes name as its arm's median seed for
both campaigns together. It is never changed: every plot, counter and lit station on screen is that one run, and the
dashed curves are the conventional lab's same seed with the same policy and stock rule (data5.Replay5("conv")).

What is on screen:
* the 3-D lab (PR 318's scene, lab3d5.py), each part a ghost until the twin has it online, then moved by the run's
  own bookings once the cell is integrated (lab3d_sched), with the stations lit from the event log;
* the clock, with how fast it runs (Timeline5: more video for the days in which more happens);
* the build-out: the money, the space, each station online, the cell;
* what runs outside the new lab meanwhile (BYU's existing equipment and the partners);
* counters as the round defines them (designed on the HPC stream, powder lots and alloys made, printed or deposited,
  tested through the full chain);
* each campaign's best new alloy so far against both targets, with a tag as a target is passed, and, while the curve
  is flat, why (data5.Replay5.flat: the run's idle-cause report, its stock log and its bookings);
* cumulative spend per lab, not a budget bar;
* the seed, for the whole replay.
"""
from __future__ import annotations

import copy
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from . import data as D
from . import data5 as D5
from . import lab3d_sched as LS
from . import style as St

HERE = D.HERE
FPS = 30
W, H = St.W, St.H
px = St.px
HPD = 24.0
CAMPS = D.CAMPAIGNS
REPLAY_DUR = float(os.environ.get("TWIN_VIDEO_REPLAY_S", "330"))
TMP = D.VID / "parts" / "lab3d"
L3FPS = 10                      # 3-D renders a second (each held for three frames of the cut)
XF = 0.6                        # seconds of crossfade into a phase: its track starts this much early
CHUNK = 24.0                    # seconds of track per render job
PIP = dict(box=(440, 132, 384, 216), size=(960, 540), view="towers_c")
_S: dict = {}


def R(which: str = "auto") -> D5.Replay5:
    if ("R", which) not in _S:
        _S[("R", which)] = D5.Replay5(which)
    return _S[("R", which)]


def lab_view() -> D5.Replay5:
    """The run's bookings inside the new lab only: its own stations (<kind>@vcl), and the atomizer from the day the
    cell is integrated (robots tend it; before that people run it, as in the conventional lab). The 3-D lab is moved
    and lit by these; everything else shows in the 'outside the new lab' panel."""
    if "lab" not in _S:
        r = R()
        cell = r.cell_h if r.cell_h is not None else float("inf")
        m = (r.where == "lab") | ((r.station == "atomizer") & (r.t0 >= cell))
        v = copy.copy(r)
        idx = np.nonzero(m)[0]
        v.t0, v.t1, v.camp, v.station, v.where, v.node = (a[idx] for a in (r.t0, r.t1, r.camp, r.station, r.where,
                                                                             r.node))
        v.what = [r.what[i] for i in idx]
        v.design = [r.design[i] for i in idx]
        v.ev = [r.ev[i] for i in idx]
        v.stations = {k: s for k, s in r.stations.items() if k in r.station_online or k == "atomizer"}
        _S["lab"] = v
    return _S["lab"]


def moves_view() -> D5.Replay5:
    """lab_view() from the cell's integration on: before it people run each station as it comes online, so no tray is
    presented and no unit drives."""
    if "moves" not in _S:
        r = lab_view()
        cell = R().cell_h if R().cell_h is not None else float("inf")
        v = copy.copy(r)
        idx = np.nonzero(r.t0 >= cell)[0]
        v.t0, v.t1, v.camp, v.station, v.where, v.node = (a[idx] for a in (r.t0, r.t1, r.camp, r.station, r.where,
                                                                             r.node))
        v.what = [r.what[i] for i in idx]
        v.design = [r.design[i] for i in idx]
        v.ev = [r.ev[i] for i in idx]
        _S["moves"] = v
    return _S["moves"]


# ================================================================================================== the clock
class Timeline5:
    """Video seconds of the replay <-> lab hours, day 0 to the horizon, and the cameras.

    The clock is continuous and never jumps. It gives each lab day video time in proportion to 1 + 3 sqrt(a), a being
    the day's share of the busiest fortnight's bookings (the HPC's left out), plus a little more around each of the
    build-out's dates and each target's day, so they can be read. A round in which the lab idles (round 5, once the
    money is spent) passes those months quickly; one in which it never does keeps a steadier pace."""

    def __init__(self, r: D5.Replay5, dur: float = REPLAY_DUR):
        self.R, self.dur = r, float(dur)
        self.horizon = r.horizon_h
        nd = int(round(r.horizon_days))
        act = np.zeros(nd + 1)
        for t0, st in zip(r.t0, r.station):
            if st != "hpc" and t0 < self.horizon:
                act[int(t0 // HPD)] += 1
        k = np.ones(15) / 15.0
        sm = np.convolve(np.pad(act, 7, mode="edge"), k, mode="valid")
        w = 1.0 + 3.0 * np.sqrt(sm / max(sm.max(), 1e-9))
        days = np.arange(nd + 1)
        marks = [h / HPD for h, key, _ in r.milestones() if key in ("money", "room", "cell")]
        for c in CAMPS:
            marks += [x["day"] for x in r.part_info["campaigns"][c]["days"].values() if x["hit"]]
        for m in marks:
            w += 5.0 * np.exp(-0.5 * ((days - m) / 1.6) ** 2)
        w[:4] += 4.0                                        # the first days, where the money arrives
        cum = np.concatenate([[0.0], np.cumsum(w)])
        self.vg = cum * self.dur / cum[-1]                  # video second at the start of each lab day
        self.dg = np.arange(nd + 2, dtype=float)
        self.room_v = self.video(r.room_h) if r.room_h is not None else 0.0
        self.cell_v = self.video(r.cell_h) if r.cell_h is not None else 0.0
        self.phases = self._phases()
        self.phase_t = [p[0] for p in self.phases]

    def lab(self, t: float) -> tuple:
        """(lab hours, lab hours per video second) at t seconds into the replay."""
        t = min(max(t, 0.0), self.dur)
        d = float(np.interp(t, self.vg, self.dg))
        i = min(max(int(np.searchsorted(self.vg, t, side="right")) - 1, 0), len(self.vg) - 2)
        sp = HPD / max(self.vg[i + 1] - self.vg[i], 1e-9)
        return min(d * HPD, self.horizon), float(sp)

    def video(self, lab_h: float) -> float:
        return float(np.interp(lab_h / HPD, self.dg, self.vg))

    def _phases(self) -> list:
        """[(start s, view, inset view or None, words)]: the ghost lab from above; the space ready and the stations
        coming in; the cell's first weeks at the Shuttles' openings; then the whole lab from several sides."""
        out = [(0.0, "high5", None, "Before the space is ready")]
        if self.room_v > 2.0:
            out.append((self.room_v, "sw5", None, "The space is ready: equipment comes in"))
        if self.cell_v > out[-1][0] + 6.0:
            out.append((self.cell_v, "towers_c", None, "The cell is integrated: robots run the stations"))
        cyc = [("high5", "towers_c"), ("plan5", None), ("se5", None), ("high5", "towers_c"), ("sw5", None),
               ("high5", None)]
        t = max(self.cell_v, out[-1][0]) + 26.0
        i = 0
        while t < self.dur - 20.0:
            v, pip = cyc[i % len(cyc)]
            out.append((t, v, pip, "The whole lab"))
            t += 38.0
            i += 1
        return out

    def phase(self, t: float) -> int:
        i = 0
        for j, pt in enumerate(self.phase_t):
            if t >= pt:
                i = j
        return i

    def span(self, i: int) -> tuple:
        return self.phase_t[i], (self.phase_t[i + 1] if i + 1 < len(self.phase_t) else self.dur)

    def marks(self) -> list:
        """(seconds into the replay, chapter title)."""
        r = self.R
        out = [(0.0, f"Day 0: the money arrives (seed {r.seed})")]
        if self.room_v > 2.0:
            out.append((self.room_v, f"Day {r.room_h / HPD:.0f}: the space is ready, equipment comes in"))
        if self.cell_v > self.room_v + 6.0:
            out.append((self.cell_v, f"Day {r.cell_h / HPD:.0f}: the cell is integrated"))
        for c in CAMPS:
            for tn, x in r.part_info["campaigns"][c]["days"].items():
                if x["hit"]:
                    out.append((self.video(x["day"] * HPD), f"Day {x['day']:.0f}: {'aluminium' if c == 'flaime_al' else 'copper'} "
                                                           f"passes {'its first target' if tn == 'T1' else 'the halfway target'}"))
        out.sort()
        merged = []
        for t, ttl in out:                                  # chapters at least 12 s apart (YouTube's minimum is 10)
            if merged and t - merged[-1][0] < 12.0:
                continue
            merged.append((round(t, 1), ttl))
        return merged


def tl() -> Timeline5:
    if "tl" not in _S:
        _S["tl"] = Timeline5(R())
    return _S["tl"]


# ============================================================================================ the cameras
def _project(cam, va, pts, size=(W, H)) -> np.ndarray:
    """World points -> pixels for a camera (position, focal point, view up) with a vertical view angle (VTK's)."""
    pos, foc, up = (np.asarray(v, float) for v in cam)
    f = foc - pos
    f /= np.linalg.norm(f)
    r_ = np.cross(f, up)
    r_ /= np.linalg.norm(r_)
    u = np.cross(r_, f)
    d = np.atleast_2d(np.asarray(pts, float)) - pos
    xc, yc, zc = d @ r_, d @ u, d @ f
    t = math.tan(math.radians(va) / 2.0)
    return np.stack([(xc / (zc * t * size[0] / size[1]) + 1.0) * 0.5 * size[0], (1.0 - yc / (zc * t)) * 0.5 * size[1]], 1)


def fit_view(name: str, free=None) -> tuple:
    """lab3d's camera `name`, pulled back (a wider angle) and moved sideways until every station the twin books, both
    Shuttles' openings and the chargers lie inside the part of the frame the replay's panels leave free."""
    from . import lab3d as L3
    free = free or FREE
    kin = LS.load_kin()
    keys = [k for k in kin["world"] if k in set(LS.DOCK_OF.values()) | {"open1", "open2", "charger1", "charger2"}]
    pts = np.array([kin["world"][k] for k in keys], float)
    cam, va = L3.VIEWS[name]
    cam = [np.array(v, float) for v in cam]
    x0, y0, x1, y1 = (px(v) for v in free)
    pad = px(70)
    for _ in range(6):
        xy = _project(cam, va, pts)
        bx0, by0, bx1, by1 = xy[:, 0].min() - pad, xy[:, 1].min() - pad, xy[:, 0].max() + pad, xy[:, 1].max() + pad
        sc = min(1.0, (x1 - x0) / (bx1 - bx0), (y1 - y0) / (by1 - by0))
        va = math.degrees(2.0 * math.atan(math.tan(math.radians(va) / 2.0) / sc))
        xy = _project(cam, va, pts)
        cx, cy = (xy[:, 0].min() + xy[:, 0].max()) / 2, (xy[:, 1].min() + xy[:, 1].max()) / 2
        dx, dy = cx - (x0 + x1) / 2, cy - (y0 + y1) / 2
        pos, foc, up = cam
        f = foc - pos
        dist = float(np.linalg.norm(f))
        f /= dist
        r_ = np.cross(f, up)
        r_ /= np.linalg.norm(r_)
        u = np.cross(r_, f)
        wpp = 2.0 * dist * math.tan(math.radians(va) / 2.0) / H       # world mm per pixel at the focal distance
        shift = r_ * dx * wpp - u * dy * wpp
        cam = [pos + shift, foc + shift, up]
    return [tuple(float(x) for x in v) for v in cam], float(va)


def register_views() -> dict:
    """The replay's whole-lab cameras, 'high5', 'sw5', 'se5' and 'plan5', added to lab3d.VIEWS (lab3d_cut projects with
    it, lab3d5 renders with it)."""
    from . import lab3d as L3
    for nm in ("high", "sw", "se", "plan"):
        if nm + "5" not in L3.VIEWS:
            L3.VIEWS[nm + "5"] = fit_view(nm)
    return L3.VIEWS


VIEW5 = {"high": "high5", "sw": "sw5", "se": "se5", "plan": "plan5"}


# ============================================================================================ the build-out in 3-D
GHOST = 0.13                    # a part of the lab the twin does not have online yet
TRAY_STATIONS: dict = {}
for _st, _k in LS.TRAY_OF.items():
    TRAY_STATIONS.setdefault(_k, []).append(_st)
MACHINE_STATION = {v: k for k, v in LS.DOCK_OF.items()}        # scene machine -> twin station kind
MACHINE_ITEM = {"glovebox": "glovebox"}                         # scene machine -> build item, where no station is
OWNED_FROM_ROOM = ("repowder", "fumehood")                      # the lab's own atomizer and hood: in once the space is


def part_online() -> dict:
    """{scene part: lab hour from which it is solid}; a part not listed stays a ghost (it is in the lab's design, not
    in the twin's build-out). Parts: 'room', 'shuttle1', 'shuttle2', 'units', 'chargers', 't:<tray>', 'm:<machine>'."""
    r = R()
    b = r.build
    room = float(r.room_h or 0.0)

    def item(k, default=None):
        return float(b[k]["online_h"]) if k in b else default
    out = {"room": room}
    sh = item("shuttle", room)
    out["shuttle1"] = out["shuttle2"] = sh
    out["units"] = out["chargers"] = item("units", room)
    kin = LS.load_kin()
    for k in kin["trays"]:
        hs = [r.online(s) for s in TRAY_STATIONS.get(k, []) if math.isfinite(r.online(s))]
        if any(s in ("cubxl", "immersion") for s in TRAY_STATIONS.get(k, [])):
            hs.append(room)                                 # DAL's own CubXL: used from day 0, in once the space is
        out[f"t:{k}"] = min(hs) if hs else sh               # a tray the twin books nothing on: with its Shuttle
    for m, st in MACHINE_STATION.items():
        if math.isfinite(r.online(st)):
            out[f"m:{m}"] = r.online(st)
    for m, it in MACHINE_ITEM.items():
        if item(it) is not None:
            out[f"m:{m}"] = item(it)
    for m in OWNED_FROM_ROOM:
        out.setdefault(f"m:{m}", room)
        out[f"m:{m}"] = min(out[f"m:{m}"], room) if m == "repowder" else out[f"m:{m}"]
    return out


def build_alpha(t_h: float) -> dict:
    """{scene part: 1.0 (online) or GHOST} at lab hour t_h; parts never online are not listed (lab3d5 ghosts them)."""
    return {k: (1.0 if t_h >= h else GHOST) for k, h in part_online().items()}


def build_key(t_h: float) -> tuple:
    return tuple(sorted(k for k, a in build_alpha(t_h).items() if a >= 1.0))


# ============================================================================================ the 3-D jobs
def jobs() -> list:
    """(registers the replay's cameras first) The replay's 3-D jobs: each phase's camera over its span (from XF before it), in chunks, and the inset's camera
    where the phase has one. Each job names the clock's span, so the workers' plans are the cut's."""
    register_views()
    T = tl()
    out = []
    for i, (a, view, pip, _) in enumerate(T.phases):
        a, b = T.span(i)
        a0 = max(0.0, a - (XF if i else 0.0))
        for track, vw, x0, x1, size in (("main", view, a0, b, [W, H]), ("pip", pip, a + 1.0, b - 1.0, list(PIP["size"]))):
            if vw is None or x1 - x0 < 1.0:
                continue
            k, x = 0, x0
            while x < x1 - 1e-6:
                y = min(x1, x + CHUNK)
                if x1 - y < 6.0:
                    y = x1
                out.append(dict(clock="replay5", round=D.ROUND, dur=T.dur, v0=round(x, 4), v1=round(y, 4),
                                views=[[0.0, 1e9, vw]], size=size, fps=L3FPS, phase=i, track=track,
                                out=str(TMP / f"r5_p{i}_{track}_{k}_{vw}")))
                x, k = y, k + 1
    return out


def clock() -> LS.Clock:
    T = tl()
    vs = np.linspace(0.0, T.dur, 12000)
    hs = np.maximum.accumulate(np.array([T.lab(x)[0] for x in vs]))
    return LS.Clock(vs, hs)


def plan():
    """The tower and unit moves over the whole replay, from the run's bookings in the new lab after its cell."""
    if "plan" not in _S:
        p = LS.plan(moves_view(), LS.load_kin(), clock())
        p.R = moves_view()
        _S["plan"] = p
    return _S["plan"]


# ================================================================================================== the panels
COL_X, COL_W = 1376, 520        # the right-hand column (1920 x 1080 px)
LEFT_X, LEFT_W = 24, 400
BOX = dict(clock=(LEFT_X, 20, LEFT_W, 104), build=(LEFT_X, 132, LEFT_W, 250), outside=(LEFT_X, 390, LEFT_W, 210),
           counters=(COL_X, 20, COL_W, 158), flaime_al=(COL_X, 186, COL_W, 236), onr_cu=(COL_X, 430, COL_W, 236),
           spend=(COL_X, 674, COL_W, 214), seed=(COL_X, 896, COL_W, 164), moves=(870, 956, 420, 104),
           pill=(440, 20, 920, 66))
FREE = (452, 110, 1352, 850)    # where the lab's picture is clear of the panels (x0, y0, x1, y1)
CAMP_WORD = {"flaime_al": "Aluminium (FLAIME)", "onr_cu": "Copper (ONR)"}
CAMP_METAL = {"flaime_al": "aluminium", "onr_cu": "copper"}
TARGET_WORDS = {"T1": "the best existing alloy on this synthetic benchmark", "T2": "the halfway target"}
OUTSIDE_NAME = {  # a booking outside the new lab: where it ran (data5.Replay5.where 'own' or 'partner')
    "atomizer": "the atomizer, run by people", "utah_midi": "partner: Utah's Aconity MIDI (LPBF)",
    "lpbf_3dpt": "partner: 3D Powder Tech (LPBF)", "utah_mxlab": "partner: Utah's MX-Lab (DED)",
    "mines_x2": "partner: Mines' FormAlloy X2 (DED)", "valimet": "partner: Valimet (gas atomizing)",
    "ames": "partner: Ames Lab (gas atomizing)", "nsl": "partner: NSL Analytical (chemistry)",
    "doser": "BYU: dosing and pressing charges", "shop": "BYU: machining cups, plugs and bars",
    "sieve": "BYU: sieving", "psd": "BYU: powder size and flow", "byu_sem": "BYU: SEM + EDS",
    "byu_icpms": "BYU: ICP-MS", "density": "BYU: density and cracks", "prep": "BYU: sectioning and polishing",
    "hardness": "BYU: hardness", "furnace": "BYU: furnaces", "tensile": "BYU: tensile frames",
    "tensile_hot": "BYU: hot tensile", "edm": "wire EDM service", "pip": "PIP service",
    "cubxl": "BYU: corrosion screen (CubXL)", "immersion": "BYU: immersion vials", "xrd": "BYU: XRD", "xrf": "BYU: XRF",
}
_IM: dict = {}


def _panel(w: int, h: int, a: float | None = None):
    im, d = St.layer(px(w), px(h))
    d.rounded_rectangle((0, 0, px(w) - 1, px(h) - 1), radius=px(12),
                        fill=St.SURF + (int(255 * (St.PANEL_A if a is None else a)),))
    return im, d


def _fit(text: str, font, width: float) -> str:
    """text, cut at a word and closed with an ellipsis if it is wider than width (never cut mid-word)."""
    if St.text_w(font, text) <= width:
        return text
    words = text.split(" ")
    while len(words) > 1 and St.text_w(font, " ".join(words) + " …") > width:
        words.pop()
    return " ".join(words).rstrip(",;:") + " …"


def _cached(key, make):
    if key not in _IM:
        if len(_IM) > 400:
            _IM.clear()
        _IM[key] = make()
    return _IM[key]


def speed_words(sp: float) -> str:
    d = sp / HPD
    lab = f"{sp:.0f} h" if d < 1.0 else (f"{d:.1f} days" if d < 10 else f"{d:.0f} days")
    return f"1 s of video = {lab} of lab time"


def clock_panel(t_h: float, sp: float) -> Image.Image:
    r, T = R(), tl()
    x_, y_, w, h = BOX["clock"]
    day = int(t_h // HPD)
    key = ("clock", day, round(sp / HPD, 1) if sp >= HPD else round(sp))
    def make():
        im, d = _panel(w, h, 0.90)
        f = St.font(40, bold=True)
        d.text((px(18), px(10)), f"Day {day}", font=f, fill=St.INK)
        x = px(18) + St.text_w(f, f"Day {day}") + px(14)
        d.text((x, px(27)), f"of {r.horizon_days:.0f}   (year {min(day // 365 + 1, int(math.ceil(r.horizon_days / 365)))})",
               font=St.font(22), fill=St.INK2)
        d.text((px(18), px(60)), speed_words(sp), font=St.font(18), fill=St.INK2)
        x0, x1, y = px(18), px(w - 18), px(88)
        d.rounded_rectangle((x0, y, x1, y + px(6)), radius=px(3), fill=(70, 73, 80, 255))
        xe = x0 + (x1 - x0) * min(1.0, t_h / r.horizon_h)
        d.rounded_rectangle((x0, y, max(x0 + px(6), xe), y + px(6)), radius=px(3), fill=St.INK + (255,))
        for hh in (r.room_h, r.cell_h):                     # the space ready, the cell integrated
            if hh is not None and r.which == "auto":
                xm = x0 + (x1 - x0) * hh / r.horizon_h
                d.line([(xm, y - px(4)), (xm, y + px(10))], fill=St.WARN + (255,), width=px(2))
        return im
    return _cached(key, make)


def stage(t_h: float) -> tuple:
    """(headline, sub) for the pill at the top: where the build-out stands on this day."""
    r = R()
    d = t_h / HPD
    room, cell = (r.room_h or 0.0) / HPD, (r.cell_h if r.cell_h is not None else float("inf")) / HPD
    on = sum(1 for h in r.station_online.values() if h <= t_h)
    n = len(r.station_online)
    if d < room:
        return (f"No lab yet: everything is ordered, and the space is ready on day {room:.0f}",
                "simulated: experiments already run on BYU's existing equipment and at the partners")
    if d < cell:
        return (f"The space is ready: {on} of {n} stations online, run by people",
                f"simulated: the cell (both Shuttles, the mobile units, their docks) is integrated on day {cell:.0f}")
    if on < n:
        return (f"The cell is integrated: robots run the lab; {on} of {n} stations online",
                "simulated: the 3-D lab is moved by the run's own bookings (trays to the openings, units to the docks)")
    return ("The whole lab is online: robots run it round the clock",
            "simulated: the 3-D lab is moved by the run's own bookings (trays to the openings, units to the docks)")


def stage_pill(t_h: float) -> Image.Image:
    head, sub = stage(t_h)
    def make():
        x_, y_, w, h = BOX["pill"]
        im, d = _panel(w, h, 0.90)
        s1 = 22.0
        while St.text_w(St.font(s1, bold=True), head) > px(w - 28) and s1 > 13:
            s1 -= 0.5
        s2 = 16.0
        while St.text_w(St.font(s2), sub) > px(w - 28) and s2 > 11:
            s2 -= 0.5
        d.text((px(w) / 2, px(22)), head, font=St.font(s1, bold=True), fill=St.INK, anchor="mm")
        d.text((px(w) / 2, px(48)), sub, font=St.font(s2), fill=St.INK2, anchor="mm")
        return im
    return _cached(("pill", head, sub), make)


def build_rows() -> list:
    """The build-out's rows: (lab hour or None, words)."""
    r = R()
    b = r.build
    rows = [(0.0, "The money arrives; all is ordered")]
    if r.room_h is not None:
        rows.append((float(r.room_h), "The space is ready"))
    so = sorted(r.station_online.values())
    if so:
        rows.append((float(so[0]), f"The first of {len(so)} stations online"))
    if "shuttle" in b:
        rows.append((float(b["shuttle"]["online_h"]), "Both Kardex Shuttles in"))
    if r.cell_h is not None:
        rows.append((float(r.cell_h), "Cell integrated: robots run it"))
    for st, words in (("utah_midi", "LPBF in house (Aconity MIDI)"), ("utah_mxlab", "DED in house (MX-Lab)")):
        if st in r.station_online:
            rows.append((float(r.station_online[st]), words))
    return sorted(rows)


def build_panel(t_h: float) -> Image.Image:
    r = R()
    rows = build_rows()
    done = sum(1 for h, _ in rows if h <= t_h)
    on = sum(1 for h in r.station_online.values() if h <= t_h)
    def make():
        x_, y_, w, h = BOX["build"]
        im, d = _panel(w, h, 0.90)
        d.text((px(16), px(10)), "The build-out (simulated; leads are stand-ins)", font=St.font(14, bold=True),
               fill=St.INK2)
        y = px(38)
        for i, (hh, words) in enumerate(rows):
            ok = hh <= t_h
            cy = y + px(11)
            if ok:
                d.ellipse((px(18), cy - px(6), px(30), cy + px(6)), fill=St.GOOD + (255,))
            else:
                d.ellipse((px(18), cy - px(6), px(30), cy + px(6)), outline=St.INK3 + (255,), width=px(2))
            d.text((px(38), y), f"day {hh / HPD:.0f}", font=St.font(15, bold=True), fill=St.INK if ok else St.INK3)
            d.text((px(112), y), words, font=St.font(15), fill=St.INK if ok else St.INK3)
            y += px(27)
        d.text((px(16), px(BOX['build'][3] - 26)), f"stations online: {on} of {len(r.station_online)}",
               font=St.font(15), fill=St.INK2)
        return im
    return _cached(("build", done, on), make)


def outside_now(t_h: float, span_h: float) -> list:
    """[(station kind, where, campaigns)] of the bookings running outside the new lab over [t_h - span_h, t_h]."""
    r = R()
    cell = r.cell_h if r.cell_h is not None else float("inf")
    out: dict = {}
    for i in r.active(t_h, span_h):
        st, wh = str(r.station[i]), str(r.where[i])
        if st == "hpc" or wh == "lab" or (st == "atomizer" and r.t0[i] >= cell):
            continue
        out.setdefault((st, wh), set()).add(str(r.camp[i]))
    order = {"partner": 0, "own": 1}
    return sorted(((st, wh, sorted(c)) for (st, wh), c in out.items()), key=lambda x: (order.get(x[1], 2), x[0]))


def outside_panel(t_h: float, span_h: float) -> Image.Image:
    rows = outside_now(t_h, span_h)
    key = ("outside", tuple((a, b, tuple(c)) for a, b, c in rows))
    def make():
        x_, y_, w, h = BOX["outside"]
        im, d = _panel(w, h, 0.90)
        d.text((px(16), px(10)), "Running outside the new lab (simulated)", font=St.font(15, bold=True), fill=St.INK2)
        y = px(36)
        if not rows:
            d.text((px(16), y), "nothing right now", font=St.font(16), fill=St.INK3)
        for st, wh, camps in rows[:6]:
            x = px(16)
            for c in CAMPS:
                if c in camps:
                    d.rounded_rectangle((x, y + px(5), x + px(10), y + px(17)), radius=px(2), fill=St.CAMP[c] + (255,))
                x += px(14)
            name = OUTSIDE_NAME.get(st, st)
            f = St.font(16)
            while St.text_w(f, name) > px(w - 60) and len(name) > 12:
                name = name[:-2]
            d.text((x + px(4), y), name, font=f, fill=St.INK)
            y += px(27)
        if len(rows) > 6:
            d.text((px(16), y), f"and {len(rows) - 6} more", font=St.font(15), fill=St.INK2)
        return im
    return _cached(key, make)


def _num(v: float) -> str:
    return f"{v / 1e6:.1f} M" if v >= 1e6 else f"{v:,.0f}"


def counters_panel(t_h: float) -> Image.Image:
    r = R()
    n = {c: r.counts(c, t_h) for c in CAMPS}
    key = ("cnt",) + tuple((round(n[c]["designed"] / 1e5), n[c]["lots"], n[c]["made"], n[c]["built"], n[c]["tested"])
                           for c in CAMPS)
    def make():
        x_, y_, w, h = BOX["counters"]
        im, d = _panel(w, h, 0.93)
        d.text((px(16), px(9)), "Counters, simulated: this seed, the automated lab", font=St.font(14, bold=True),
               fill=St.INK2)
        cols = [("designed", "designed", 112), ("lots", "powder lots", 210), ("made", "alloys made", 310),
                ("built", "printed", 400), ("tested", "tested", 474)]
        sub = {"designed": "(on the HPC)", "built": "or deposited", "tested": "(full chain)"}
        for k, name, cx in cols:
            d.text((px(cx), px(40)), name, font=St.font(14, bold=True), fill=St.INK2, anchor="ma")
            if k in sub:
                d.text((px(cx), px(57)), sub[k], font=St.font(12), fill=St.INK3, anchor="ma")
        y = px(76)
        for c in CAMPS:
            d.rounded_rectangle((px(16), y + px(6), px(28), y + px(18)), radius=px(3), fill=St.CAMP[c] + (255,))
            d.text((px(34), y + px(1)), "Al" if c == "flaime_al" else "Cu", font=St.font(18, bold=True), fill=St.INK)
            for k, name, cx in cols:
                d.text((px(cx), y), _num(n[c][k]), font=St.font(19, bold=True), fill=St.INK, anchor="ma")
            y += px(27)
        d.text((px(16), px(BOX['counters'][3] - 24)), "early stopping: only promising alloys finish every step",
               font=St.font(14), fill=St.INK2)
        return im
    return _cached(key, make)


class Plot:
    """A small line plot drawn with PIL: axes in a panel, x in days."""

    def __init__(self, w: int, h: int, x1: float, y1: float, left: int = 50, right: int = 14, top: int = 34,
                 bottom: int = 26):
        self.w, self.h, self.x1, self.y1 = w, h, x1, y1
        self.box = (px(left), px(top), px(w - right), px(h - bottom))

    def xy(self, x: float, y: float) -> tuple:
        x0, y0, x1, y1 = self.box
        return x0 + (x1 - x0) * min(max(x / self.x1, 0.0), 1.0), y1 - (y1 - y0) * min(max(y / self.y1, 0.0), 1.05)

    def axes(self, d, yticks, yfmt, xticks):
        x0, y0, x1, y1 = self.box
        for v in yticks:
            _, yy = self.xy(0, v)
            d.line([(x0, yy), (x1, yy)], fill=St.GRID + (255,), width=1)
            d.text((x0 - px(6), yy), yfmt(v), font=St.font(13), fill=St.INK3, anchor="rm")
        for v in xticks:
            xx, _ = self.xy(v, 0)
            d.line([(xx, y1), (xx, y1 + px(4))], fill=St.RULE + (255,), width=1)
            d.text((xx, y1 + px(6)), f"{v:.0f}", font=St.font(13), fill=St.INK3, anchor="ma")
        d.line([(x0, y1), (x1, y1)], fill=St.RULE + (255,), width=1)
        d.text((x1, y1 + px(6)), "day", font=St.font(13), fill=St.INK3, anchor="ra")

    def step(self, pts, t_day: float, first: float = 0.0) -> list:
        """A best-so-far step curve's screen points up to t_day: pts [(day, value)], value held between points."""
        out, v = [self.xy(0.0, first)], first
        for dd, val in pts:
            if dd > t_day:
                break
            out.append(self.xy(dd, v))
            v = max(v, val)
            out.append(self.xy(dd, v))
        out.append(self.xy(t_day, v))
        return out


def _xticks(h: float) -> list:
    return [v for v in St.nice_ticks(0, h, 5) if v <= h + 1e-6]


def best_panel(c: str, t_h: float) -> Image.Image:
    """The campaign's best new alloy so far: this seed in the automated lab (its colour), the conventional lab's same
    seed dashed, both targets dotted; and, while the curve is flat, since when and why."""
    ra, rc = R("auto"), R("conv")
    I = D5.info()
    d_now = t_h / HPD
    q = round(d_now * 2) / 2
    fl = ra.flat(c, t_h)
    fkey = None if fl is None else (round(fl["since"]), tuple(w for _, w in fl["reasons"][:2]))
    key = ("best", c, q, fkey)
    def make():
        x_, y_, w, h = BOX[c]
        im, d = _panel(w, h, 0.93)
        T1, T2 = I["targets"]["T1"][c], I["targets"]["T2"][c]
        ymax = max(0.9, float(max(ra.curves[c][:, 2].max() if len(ra.curves[c]) else 0.0,
                                  rc.curves[c][:, 2].max() if len(rc.curves[c]) else 0.0)) * 1.08)
        P = Plot(w, h - 46, ra.horizon_days, ymax)
        d.text((px(16), px(8)), f"{CAMP_WORD[c]}: best new alloy so far", font=St.font(16, bold=True), fill=St.INK)
        P.axes(d, [v for v in (0.0, 0.2, 0.4, 0.6, 0.8) if v <= ymax], lambda v: f"{v:.1f}", _xticks(ra.horizon_days))
        x0, y0, x1, y1 = P.box
        for tn, tv, words, below in (("T1", T1, "best existing alloy", True), ("T2", T2, "halfway target", False)):
            _, yy = P.xy(0, tv)
            St.dashed_line(d, [(x0, yy), (x1, yy)], fill=St.TARGET + (255,), width=px(2), dash=px(3), gap=px(5))
            d.text((x0 + px(6), yy + (px(3) if below else -px(2))), f"{words} {tv:.2f}", font=St.font(12),
                   fill=St.INK2, anchor="la" if below else "ld")
        pc = P.step([(a, b) for a, _, b in rc.curves[c]], d_now)
        St.dashed_line(d, pc, fill=St.BASE + (255,), width=px(3), dash=px(9), gap=px(6))
        vc = rc.best_at(c, t_h)
        if vc > 0:
            qx, qy = pc[-1]
            below = vc <= ra.best_at(c, t_h)
            d.text((qx + (px(8) if qx < x1 - px(60) else -px(8)), qy + (px(4) if below else -px(6))), f"{vc:.2f}",
                   font=St.font(14, bold=True), fill=St.BASE,
                   anchor=("l" if qx < x1 - px(60) else "r") + ("a" if below else "d"))
        pa = P.step([(a, b) for a, _, b in ra.curves[c]], d_now)
        d.line(pa, fill=St.CAMP[c] + (255,), width=px(4), joint="curve")
        cx, cy = pa[-1]
        d.ellipse((cx - px(5), cy - px(5), cx + px(5), cy + px(5)), fill=St.CAMP[c] + (255,), outline=(255, 255, 255, 255))
        d.text((cx + (px(8) if cx < x1 - px(60) else -px(8)), cy - px(6)), f"{ra.best_at(c, t_h):.2f}",
               font=St.font(15, bold=True), fill=St.INK, anchor="ld" if cx < x1 - px(60) else "rd")
        # the strip under the plot: why the curve is flat, or that it is moving
        ys = px(h - 44)
        d.line([(px(12), ys), (px(w - 12), ys)], fill=St.GRID + (255,), width=1)
        if fl is None:
            d.text((px(16), ys + px(8)), "automated lab, this seed (solid); conventional, same seed (dashed)",
                   font=St.font(13), fill=St.INK2)
        else:
            n_new = int((ra.curves[c][:, 0] <= d_now).sum())
            head = (f"flat since day {fl['since']:.0f}" if not fl["first"] else "no new alloy tested yet" if n_new == 0
                    else f"{n_new} new alloy{'s' if n_new != 1 else ''} tested, none past its gates")
            rs = [wds for _, wds in fl["reasons"][:2]] or ["results still in flight"]
            f1, f2 = St.font(14, bold=True), St.font(14)
            right = px(w - 14)
            d.text((px(16), ys + px(5)), head + ". Why:", font=f1, fill=St.WARN)
            xx = px(16) + St.text_w(f1, head + ". Why: ")
            # two lines at most, each kept inside the panel: the first reason beside the head when it fits there,
            # else on the second line; the second reason after it on the second line, when there is room
            if xx + St.text_w(f2, rs[0]) <= right:
                d.text((xx, ys + px(5)), rs[0], font=f2, fill=St.INK)
                if len(rs) > 1:
                    d.text((px(16), ys + px(24)), _fit("and " + rs[1], f2, right - px(16)), font=f2, fill=St.INK)
            else:
                line2 = rs[0] + ("; and " + rs[1] if len(rs) > 1 else "")
                if St.text_w(f2, line2) > right - px(16):
                    line2 = rs[0]
                d.text((px(16), ys + px(24)), _fit(line2, f2, right - px(16)), font=f2, fill=St.INK)
        return im
    return _cached(key, make)


PCT_SPENT = 0.9                 # "the money is spent": this share of it (twin.like5.money_out's)


def d_spent(which: str = "auto") -> float | None:
    """The day by which the lab's seed has spent PCT_SPENT of both campaigns' money together (None: it never does,
    or the round has no limit)."""
    r = R(which)
    budget = sum(r.budget[c] for c in CAMPS)
    if not (0 < budget < 1e12):
        return None
    days = np.arange(0.0, r.horizon_days + 1.0)
    tot = sum(np.interp(days, r.spend[c][:, 0], r.spend[c][:, 1]) for c in CAMPS)
    i = np.nonzero(tot >= PCT_SPENT * budget)[0]
    return float(days[i[0]]) if len(i) else None


def spend_panel(t_h: float) -> Image.Image:
    """Cumulative spend per lab over time (both campaigns together; the automated lab's two campaigns thin), with the
    two years' money as a line where the round has a limit. Not a budget bar: round 6 tracks spending, with no limit."""
    ra, rc = R("auto"), R("conv")
    d_now = t_h / HPD
    q = round(d_now * 2) / 2
    def make():
        x_, y_, w, h = BOX["spend"]
        im, d = _panel(w, h, 0.93)
        tot = {nm: sum(float(r_.spend[c][:, 1].max()) for c in CAMPS) for nm, r_ in (("a", ra), ("c", rc))}
        budget = sum(ra.budget[c] for c in CAMPS)
        has_limit = budget > 0 and budget < 1e12
        ymax = max(max(tot.values()), budget if has_limit else 0.0) * 1.1 or 1.0
        P = Plot(w, h, ra.horizon_days, ymax, top=62)
        d.text((px(16), px(8)), "Cumulative spend per lab, both campaigns (simulated)", font=St.font(15, bold=True),
               fill=St.INK)

        step = 100e3 if ymax <= 600e3 else 250e3 if ymax <= 1.6e6 else 1e6
        P.axes(d, [v for v in np.arange(0, ymax, step)], lambda v: f"${v / 1e3:.0f}k" if v < 1e6 else f"${v / 1e6:.1f}M",
               _xticks(ra.horizon_days))
        x0, y0, x1, y1 = P.box
        if has_limit:
            _, yy = P.xy(0, budget)
            St.dashed_line(d, [(x0, yy), (x1, yy)], fill=St.TARGET + (255,), width=px(2), dash=px(3), gap=px(5))
            d.text((x0 + px(6), yy + px(3)), f"two years' money, all at day 0: {D5._usd(budget)}", font=St.font(12),
                   fill=St.INK2, anchor="la")
        days = np.arange(0.0, d_now + 0.5, 1.0)
        if len(days) < 2:
            days = np.array([0.0, max(d_now, 0.01)])
        for c in CAMPS:                                     # the automated lab's campaigns, thin
            ys = np.interp(days, ra.spend[c][:, 0], ra.spend[c][:, 1])
            d.line([P.xy(a, b) for a, b in zip(days, ys)], fill=St.CAMP[c] + (255,), width=px(2))
        yc = sum(np.interp(days, rc.spend[c][:, 0], rc.spend[c][:, 1]) for c in CAMPS)
        St.dashed_line(d, [P.xy(a, b) for a, b in zip(days, yc)], fill=St.BASE + (255,), width=px(3), dash=px(9), gap=px(6))
        ya = sum(np.interp(days, ra.spend[c][:, 0], ra.spend[c][:, 1]) for c in CAMPS)
        d.line([P.xy(a, b) for a, b in zip(days, ya)], fill=St.INK + (255,), width=px(4), joint="curve")
        d9 = d_spent("auto")
        if d9 is not None and d_now >= d9:                  # where the automated lab's money is spent
            cx, cy = P.xy(d9, PCT_SPENT * budget)
            d.ellipse((cx - px(5), cy - px(5), cx + px(5), cy + px(5)), fill=St.WARN + (255,))
            d.text((cx + px(10), cy + px(12)), f"{PCT_SPENT * 100:.0f} % spent by day {d9:.0f}", font=St.font(13, bold=True),
                   fill=St.WARN, anchor="la")
        x, yl = px(16), px(40)                              # the legend, with each line's value now
        f = St.font(13, bold=True)
        d.line([(x, yl), (x + px(22), yl)], fill=St.INK + (255,), width=px(4))
        txt = f"automated {D5._usd(ya[-1])}"
        d.text((x + px(27), yl), txt, font=f, fill=St.INK, anchor="lm")
        x += px(37) + St.text_w(f, txt)
        St.dashed_line(d, [(x, yl), (x + px(26), yl)], fill=St.BASE + (255,), width=px(3), dash=px(8), gap=px(5))
        txt = f"conventional {D5._usd(yc[-1])}"
        d.text((x + px(31), yl), txt, font=f, fill=St.BASE, anchor="lm")
        x += px(41) + St.text_w(f, txt)
        for c in CAMPS:
            d.line([(x, yl), (x + px(16), yl)], fill=St.CAMP[c] + (255,), width=px(2))
            d.text((x + px(20), yl), "Al" if c == "flaime_al" else "Cu", font=St.font(13), fill=St.INK2, anchor="lm")
            x += px(46)
        return im
    return _cached(("spend", q), make)


def seed_badge() -> Image.Image:
    """Which seed is on screen, for the whole replay: the seed, the arm, why this seed, and what is dashed."""
    I = D5.info()
    def make():
        x_, y_, w, h = BOX["seed"]
        im, d = _panel(w, h, 0.90)
        ms = I["median_seed"]
        a = I["auto"]["campaigns"]

        def dd(x):
            return f"{x['day']:.0f}" if x["hit"] else f">{I['horizon_days']:.0f}"

        def md(k):
            v = ms["medians"][k]
            return f"{v:.0f}" if v < I["horizon_days"] else f">{I['horizon_days']:.0f}"
        d.text((px(16), px(10)), f"Seed {I['seed']} of {I['n_seeds']}, for the whole replay", font=St.font(22, bold=True),
               fill=St.INK)
        lines = [
            f"The automated lab, {I['stock_words']}, {I['policy_words']} on both campaigns.",
            (f"The arm's median seed for both campaigns (round {I['round']}'s notes)."
             if I["is_median_seed"] else "Not the arm's median seed: chosen by hand for a look."),
            f"Days to the targets, this seed: Al {dd(a['flaime_al']['days']['T1'])}, "
            f"{dd(a['flaime_al']['days']['T2'])}; Cu {dd(a['onr_cu']['days']['T1'])}, {dd(a['onr_cu']['days']['T2'])}.",
            f"The arm's medians, {I['n_seeds']} seeds: Al {md('flaime_al|T1')}, {md('flaime_al|T2')}; "
            f"Cu {md('onr_cu|T1')}, {md('onr_cu|T2')}.",
            f"Dashed: the conventional lab's seed {I['seed']}, same policy and stock.",
        ]
        y = px(44)
        for ln in lines:
            d.text((px(16), y), ln, font=St.font(14), fill=St.INK2 if "Dashed" in ln else St.INK)
            y += px(23)
        return im
    return _cached(("seed",), make)


TAG_S = 9.0


def target_events() -> list:
    """[(seconds into the replay, campaign, target, day, words)] as the replayed seed passes each target."""
    T, I = tl(), D5.info()
    out = []
    for c in CAMPS:
        days = I["auto"]["campaigns"][c]["days"]
        both = days["T1"]["hit"] and days["T2"]["hit"] and abs(days["T1"]["day"] - days["T2"]["day"]) < 1e-6
        for tn in ("T1", "T2"):
            x = days[tn]
            if not x["hit"] or (both and tn == "T2"):
                continue
            st = I["arm_stats"][f"auto|{c}|{tn}"]
            what = "both targets" if both else TARGET_WORDS[tn]
            hits = st["hit"] if not both else min(st["hit"], I["arm_stats"][f"auto|{c}|T2"]["hit"])
            short = "both targets" if both else ("its first target" if tn == "T1" else "the halfway target")
            cd = I["conv"]["campaigns"][c]["days"]
            cds = [cd[k] for k in (("T1", "T2") if both else (tn,))]
            conv = ("the conventional lab's seed: " + (" and ".join(f"day {z['day']:.0f}" for z in cds)
                                                      if all(z["hit"] for z in cds) else
                                                      f"not within {I['horizon_days']:.0f} days"))
            sub = (f"{what}; " if not both else "") + f"{conv}; {hits} of {st['n']} seeds get there"
            out.append((T.video(x["day"] * HPD), c, tn, x["day"],
                        f"Day {x['day']:.0f}: {CAMP_METAL[c]}'s best new alloy passes {short}", sub))
    return sorted(out)


def target_tags(t: float) -> list:
    out = []
    for tv, c, tn, day, head, sub in target_events():
        k = min(St.ramp(t, tv, tv + 0.4), 1.0 - St.ramp(t, tv + TAG_S - 0.6, tv + TAG_S))
        if k <= 0.003:
            continue
        def make(head=head, sub=sub, c=c):
            f, f2 = St.font(19, bold=True), St.font(14)
            w = min(px(790), max(St.text_w(f, head), St.text_w(f2, sub)) + px(52))
            im, d = St.layer(w, px(62))
            d.rounded_rectangle((0, 0, w - 1, px(62) - 1), radius=px(10), fill=(18, 20, 24, 240),
                                outline=St.CAMP[c] + (255,), width=px(2))
            d.rounded_rectangle((px(12), px(12), px(24), px(24)), radius=px(3), fill=St.CAMP[c] + (255,))
            d.text((px(34), px(8)), head, font=f, fill=St.INK)
            d.text((px(34), px(34)), sub, font=f2, fill=St.INK2)
            return im
        out.append((_cached(("tag", c, tn), make), k, c))
    return out


# ================================================================================================== the picture
def _state() -> dict:
    if "st" not in _S:
        register_views()
        from . import lab3d_cut as LC
        from .birdseye import Birdseye
        kin = LS.load_kin()
        groups: dict = {}
        for j in jobs():
            groups.setdefault((j["phase"], j["track"]), []).append(j)
        be = Birdseye(lab_view())
        be.avoid = [(px(x), px(y), px(x + w), px(y + h)) for x, y, w, h in BOX.values()] + \
                   [(px(24), px(860), px(844), px(1060))]
        be.offsite = []
        _S["st"] = dict(kin=kin, LC=LC, be=be, tracks={k: LC.Tracks(v) for k, v in groups.items()}, anc={},
                        all_st=dict(lab_view().stations))
    return _S["st"]


def have_tracks() -> bool:
    return all(Path(j["out"]).with_suffix(".mp4").exists() for j in jobs())


def picture(i: int, t: float, t_h: float, sp: float) -> np.ndarray:
    """Phase i of the replay at t: the 3-D track, the stations lit, the tags on what moves, the inset."""
    st = _state()
    LC, be, kin = st["LC"], st["be"], st["kin"]
    T = tl()
    _, view, pip, _ = T.phases[i]
    a, b = T.span(i)
    if os.environ.get("TWIN_VIDEO_NO3D") == "1" or not have_tracks():       # stills before the 3-D track exists
        img = np.full((H, W, 3), 38, np.uint8)
    else:
        img = st["tracks"][(i, "main")].frame(t)
    if view not in st["anc"]:
        st["anc"][view] = LC.anchors(view, kin)
    r = R()
    be.R.stations = {k: v for k, v in st["all_st"].items()
                     if (r.online(k) <= t_h) or (k == "atomizer" and r.cell_h is not None and t_h >= r.cell_h)}
    sh_on = "shuttle" not in r.build or t_h >= float(r.build["shuttle"]["online_h"])
    base = view[:-1] if view.endswith("5") else view
    be.show_chips = sh_on and base in LC.CHIPS
    be.chip_dx = LC.CHIPS.get(base, {1: 0.0, 2: 0.0})
    be.chip_avoid = True
    fr = be.frame_live(img, st["anc"][view], t_h, max(1.0, sp * 0.8), offsite=False, legend=False)
    placed = [(px(x), px(y), px(x + w), px(y + h)) for x, y, w, h in BOX.values()]
    if r.cell_h is not None and t_h >= r.cell_h:
        LC.moving_tags(fr, plan(), t, view, placed)
    pip_on = pip is not None and (i, "pip") in st["tracks"] and a + 1.0 <= t < b - 1.0 and have_tracks()
    if pip_on:
        k = min(1.0, (t - a - 1.0) / 0.4, (b - 1.0 - t) / 0.4)
        im, x, y = LC.pip_frame(st["tracks"][(i, "pip")].frame(t), PIP["box"], "Shuttles up close (second camera)", k)
        St.paste(fr, im, x, y, max(0.0, k))
    return fr


def moves_panel(t: float, t_h: float, sp: float) -> Image.Image | None:
    r = R()
    if r.cell_h is None or t_h < r.cell_h:
        return None
    LC = _state()["LC"]
    return LC.moves_panel(plan(), t, t_h - 168.0, t_h, LS.move_rate(sp), "the last 7 days")


def ghost_legend(t_h: float) -> Image.Image | None:
    """While any part of the lab is still a ghost: what a ghost is."""
    po = part_online()
    coming = any(h > t_h for h in po.values())
    kin = LS.load_kin()
    never = [k for k in kin["docks"] if f"m:{k}" not in po and k not in ("vlm", "vlm2")] + \
            [k for k in kin["world"] if k in ("eos_m400", "meltio_cell") and f"m:{k}" not in po]
    if not coming and not never:
        return None
    txt = ("see-through: ordered, not online yet" if coming else
           "see-through: in the lab's design, not in the twin's build-out")
    def make():
        f = St.font(15)
        w = St.text_w(f, txt) + px(28)
        im, d = St.layer(w, px(30))
        d.rounded_rectangle((0, 0, w - 1, px(30) - 1), radius=px(8), fill=(18, 20, 24, 215))
        d.text((px(14), px(15)), txt, font=f, fill=St.INK, anchor="lm")
        return im
    return _cached(("ghost", txt), make)


def replay_frame(t: float) -> np.ndarray:
    T, r = tl(), R()
    t_h, sp = T.lab(t)
    t_h = min(t_h, r.horizon_h - 1e-3)
    span = max(1.0, sp * 0.6)
    i = T.phase(t)
    fr = picture(i, t, t_h, sp)
    t_next = T.phase_t[i + 1] if i + 1 < len(T.phase_t) else None
    if t_next is not None and t > t_next - XF:
        nxt = picture(i + 1, t, t_h, sp)
        u = St.ease((t - (t_next - XF)) / XF)
        fr = (fr.astype(np.float32) * (1 - u) + nxt.astype(np.float32) * u).astype(np.uint8)
    St.paste(fr, clock_panel(t_h, sp), px(BOX["clock"][0]), px(BOX["clock"][1]))
    St.paste(fr, stage_pill(t_h), px(BOX["pill"][0]), px(BOX["pill"][1]))
    St.paste(fr, build_panel(t_h), px(BOX["build"][0]), px(BOX["build"][1]))
    St.paste(fr, outside_panel(t_h, span), px(BOX["outside"][0]), px(BOX["outside"][1]))
    St.paste(fr, counters_panel(t_h), px(BOX["counters"][0]), px(BOX["counters"][1]))
    for c in CAMPS:
        St.paste(fr, best_panel(c, t_h), px(BOX[c][0]), px(BOX[c][1]))
    St.paste(fr, spend_panel(t_h), px(BOX["spend"][0]), px(BOX["spend"][1]))
    St.paste(fr, seed_badge(), px(BOX["seed"][0]), px(BOX["seed"][1]))
    mp = moves_panel(t, t_h, sp)
    if mp is not None:
        St.paste(fr, mp, px(BOX["moves"][0]), px(BOX["moves"][1]))
    gl = ghost_legend(t_h)
    if gl is not None:
        St.paste(fr, gl, px(440), px(92))
    from . import compose as C
    dag = C.S("dag")
    lit = {k: dag.intensity(v) for k, v in r.lit(t_h, span).items()}
    x, y, _, _ = dag.DOCK
    St.paste(fr, dag.overlay(lit, t=t), px(x), px(y))
    for im_, k, c in target_tags(t):
        St.paste(fr, im_, px(COL_X) - im_.width - px(12), px(BOX[c][1] + (176 if c == "flaime_al" else 40)), k)
    return fr


def captions() -> list:
    """(t0, t1, text) of what the replay says on screen at each time, for the narration's plan."""
    T = tl()
    out = []
    for (a, ttl), b in zip(T.marks(), [m[0] for m in T.marks()[1:]] + [T.dur]):
        out.append((a, b, f"chapter: {ttl}"))
    for tv, c, tn, day, head, sub in target_events():
        out.append((tv, tv + TAG_S, f"{head} ({sub})"))
    return out


def marks() -> dict:
    """Named moments of the replay (seconds into it) that narration lines anchor on."""
    T, r = tl(), R()
    out = {"start": 0.0, "room": T.room_v, "cell": T.cell_v, "end": T.dur}
    for tv, c, tn, day, head, sub in target_events():
        out[f"hit.{c}.{tn}"] = tv
    for i, pt in enumerate(T.phase_t):
        out[f"phase.{i}"] = pt
    for c in CAMPS:                                         # the last time the curve moved: the long flat begins
        if r._improve[c]:
            out[f"last.{c}"] = T.video(r._improve[c][-1] * HPD)
    d9 = d_spent("auto")
    if d9 is not None:
        out["spent"] = T.video(d9 * HPD)
    for d in range(0, int(r.horizon_days) + 1, 10):
        out[f"day.{d}"] = T.video(d * HPD)
    return {k: round(float(v), 2) for k, v in out.items()}


def stills(times: list):
    Path("/tmp/vid").mkdir(exist_ok=True)
    import time as _t
    for t in times:
        c0 = _t.process_time()
        fr = replay_frame(float(t))
        Image.fromarray(np.ascontiguousarray(fr)).save(f"/tmp/vid/replay5_{float(t):05.1f}.png")
        print(f"{float(t):6.1f} s (day {tl().lab(float(t))[0] / HPD:.0f}): {1000 * (_t.process_time() - c0):.0f} ms cpu",
              flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        T = tl()
        r = R()
        print(f"replay: {r.path.name}, {T.dur:.0f} s for {r.horizon_days:.0f} days; room day "
              f"{(r.room_h or 0) / HPD:.1f} at {T.room_v:.1f} s, cell day {(r.cell_h or 0) / HPD:.1f} at {T.cell_v:.1f} s")
        for d in (0, 30, 67, 100, 161, 182, 250, 291, 350, 450, 600, 730):
            v = T.video(d * HPD)
            print(f"  day {d:4d} at {v:6.1f} s, {T.lab(v)[1] / HPD:5.2f} lab days a second")
        for i, (a, view, pip, words) in enumerate(T.phases):
            a, b = T.span(i)
            print(f"  phase {i}: {a:6.1f}-{b:6.1f} s  day {T.lab(a)[0] / HPD:5.0f}-{T.lab(b)[0] / HPD:5.0f}  {view:9s} "
                  f"{pip or '-':9s} {words}")
        js = jobs()
        print(f"  {len(js)} 3-D jobs, {sum((j['v1'] - j['v0']) * j['fps'] for j in js):.0f} frames; marks:")
        for t, ttl in T.marks():
            print(f"    {t:6.1f} s  {ttl}")
        po = part_online()
        print("  parts online (day):", {k: round(v / HPD, 1) for k, v in sorted(po.items(), key=lambda kv: kv[1])})
        lv, mv = lab_view(), moves_view()
        print(f"  bookings: {len(r.ev)} in the run, {len(lv.ev)} in the new lab, {len(mv.ev)} after the cell")
    elif cmd == "stills":
        stills(sys.argv[2:] or [10, 40, 80, 150, 250, 320])
    else:
        raise SystemExit(__doc__)

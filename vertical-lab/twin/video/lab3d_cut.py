"""The animated lab, cut: the 3-D renders (lab3d.py) under the replay's overlays, and the jobs that make them.

    cd vertical-lab
    python -m twin.video.lab3d_cut preview          # one simulated week from above, 60 s -> out/twin2/video/lab3d_week.mp4
    python -m twin.video.lab3d_cut stills 5 30      # composed frames of the preview at those seconds -> /tmp/vid/

The 3-D track is rendered first, by lab3d.py workers (each builds PR 318's scene once, 90-115 s, 3 GB) into
intermediate MP4s at lab3d.RENDER_FPS, split across TWIN_VIDEO_WORKERS processes; the cut then reads them back frame by
frame at 30 fps and draws the overlays on top: the clock, the stations lit from the event log (birdseye.Birdseye on
the render's own projected anchors), the docked networks (dag_anim), the compositions in progress as periodic-table
heatmaps (ptable), the live best-so-far plots (figs_anim.PlotPanel), and, new here, a tag on each tray presented and
each unit on the move, and a line saying how fast the moves are drawn and how many of the week's requests fit.
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
from PIL import Image

from . import compose as C
from . import data as D
from . import lab3d_sched as LS
from . import style as St

HERE = D.HERE
FPS = 30
W, H = St.W, St.H
px = St.px
TMP = D.VID / "parts" / "lab3d"
L3FPS = 15                     # renders a second, day by day (and the preview's week)
L3FPS_FAST = 10                # from week by week on (15-60 lab hours a second): each render held for three frames

# the preview: one simulated week, Monday 00:00 of week 18 (day 120) to the next Monday, at 2.8 lab hours a second
WEEK = dict(lab_h0=24.0 * 119, hours_per_s=2.8, seconds=60.0)
PIP = dict(view="towers_c", t0=6.0, t1=54.0, box=(24, 236, 384, 216), size=(960, 540))

def views() -> dict:
    from .lab3d import VIEWS
    return VIEWS


# ============================================================================================ projection
def project(view: str, pts: np.ndarray, size=(W, H)) -> np.ndarray:
    """World points (n, 3) -> pixels (n, 2) for a lab3d camera: VTK's perspective with a vertical view angle."""
    (pos, foc, up), va = views()[view]
    pos, foc, up = (np.asarray(v, float) for v in (pos, foc, up))
    f = foc - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    d = np.atleast_2d(np.asarray(pts, float)) - pos
    xc, yc, zc = d @ r, d @ u, d @ f
    t = math.tan(math.radians(va) / 2.0)
    asp = size[0] / size[1]
    x = xc / (zc * t * asp)
    y = yc / (zc * t)
    return np.stack([(x + 1.0) * 0.5 * size[0], (1.0 - y) * 0.5 * size[1]], 1)


def anchors(view: str, kin: dict) -> dict:
    keys = list(kin["world"])
    xy = project(view, np.array([kin["world"][k] for k in keys]))
    return {k: [float(a), float(b), 0.5] for k, (a, b) in zip(keys, xy)}


# ============================================================================================ reading the renders
class Track:
    """Frames of one rendered job (an intermediate MP4 at its own fps), read in order."""

    def __init__(self, path: Path, v0: float, fps: float, size=(W, H)):
        self.path, self.v0, self.fps, self.size = Path(path), float(v0), float(fps), size
        self.p = None
        self.k = -1
        self.last = None

    def frame(self, v: float) -> np.ndarray:
        k = max(0, int(math.floor((v - self.v0) * self.fps + 1e-6)))
        if self.p is None or k < self.k:
            self.close()
            self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(self.path), "-f", "rawvideo", "-pix_fmt",
                                       "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                      bufsize=self.size[0] * self.size[1] * 3 * 2)
            self.k = -1
        n = self.size[0] * self.size[1] * 3
        while self.k < k:
            buf = self.p.stdout.read(n)
            if len(buf) < n:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(self.size[1], self.size[0], 3)
            self.k += 1
        if self.last is None:
            self.last = np.zeros((self.size[1], self.size[0], 3), np.uint8)
        return self.last

    def close(self):
        if self.p is not None:
            try:
                self.p.stdout.close()
                self.p.kill()
            except Exception:                              # noqa: BLE001
                pass
            self.p = None


class Tracks:
    """The jobs of one track (a view over a time range, split into chunks), as one reader."""

    def __init__(self, jobs: list):
        self.jobs = sorted(jobs, key=lambda j: j["v0"])
        self.readers = {}

    def frame(self, v: float) -> np.ndarray:
        for j in self.jobs:
            if j["v0"] - 1e-6 <= v < j["v1"] + 1e-6:
                key = j["out"]
                if key not in self.readers:
                    for kk in list(self.readers):
                        self.readers.pop(kk).close()
                    size = tuple(j.get("size", (W, H)))
                    self.readers[key] = Track(Path(j["out"]).with_suffix(".mp4"), j["v0"], j["fps"], size)
                return self.readers[key].frame(v)
        j = self.jobs[-1] if v >= self.jobs[-1]["v1"] else self.jobs[0]
        return self.frame(min(max(v, j["v0"]), j["v1"] - 1e-3))


# ============================================================================================ the jobs
def _done(j: dict) -> bool:
    rec = Path(j["out"]).with_suffix(".json")
    if not (rec.exists() and Path(j["out"]).with_suffix(".mp4").exists()):
        return False
    try:
        return json.loads(rec.read_text()).get("job") == j
    except Exception:                                      # noqa: BLE001
        return False


def run_jobs(jobs: list, workers: int):
    """The jobs not already done (same job, MP4 and record present), in `workers` lab3d processes, each rendering a
    batch of jobs of one frame size with one scene build: xvfb-run, VIZ3D_SIZE from the batch, LP_NUM_THREADS
    (llvmpipe's threads; TWIN_VIDEO_LP_THREADS, default 2, so three workers share the runner's four cores without
    twelve render threads fighting over them). Each worker holds the whole scene, about 3 GB."""
    todo = [j for j in jobs if not _done(j)]
    if not todo:
        return
    by_size: dict = {}
    for j in todo:
        by_size.setdefault(tuple(j.get("size", (W, H))), []).append(j)
    cost = {s: sum((j["v1"] - j["v0"]) * j["fps"] * (s[0] * s[1]) / (W * H) ** 0.5 / (W * H) ** 0.5 for j in js)
            for s, js in by_size.items()}
    tot = sum(cost.values()) or 1.0
    ks = {s: max(1, min(len(js), round(workers * cost[s] / tot))) for s, js in by_size.items()}
    while sum(ks.values()) > max(workers, len(ks)):       # never more processes than workers (3 GB each)
        big = max(ks, key=lambda s: ks[s])
        ks[big] -= 1
    batches = []
    for s, js in by_size.items():                         # workers in proportion to each size's renders
        k = ks[s]
        per = [[] for _ in range(k)]
        load = [0.0] * k
        for j in sorted(js, key=lambda j: -(j["v1"] - j["v0"]) * j["fps"]):
            i = int(np.argmin(load))
            per[i].append(j)
            load[i] += (j["v1"] - j["v0"]) * j["fps"]
        batches += [(s, sorted(b, key=lambda j: j["v0"])) for b in per if b]
    t0 = time.time()
    procs = []
    for n, (size, batch) in enumerate(batches):
        bp = TMP / f"batch_{n}_{size[0]}x{size[1]}.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps(batch))
        env = dict(os.environ, VIZ3D_SIZE=f"{size[0]}x{size[1]}",
                   LP_NUM_THREADS=os.environ.get("TWIN_VIDEO_LP_THREADS", "2"))
        log = open(bp.with_suffix(".log"), "w")
        p = subprocess.Popen(["xvfb-run", "-a", "-s", f"-screen 0 {max(size[0], 1280)}x{max(size[1], 720)}x24",
                              sys.executable, "-m", "twin.video.lab3d", "render", str(bp)], cwd=HERE, env=env,
                             stdout=log, stderr=subprocess.STDOUT)
        procs.append((p, bp, log, len(batch)))
        print(f"  3-D batch {n}: {len(batch)} jobs at {size[0]}x{size[1]}", flush=True)
    for p, bp, log, nb in procs:
        p.wait()
        log.close()
        print(f"  3-D {bp.name}: rc {p.returncode}, {time.time() - t0:.0f} s", flush=True)
        if p.returncode != 0:
            raise SystemExit(f"3-D batch {bp} failed: see {bp.with_suffix('.log')}")
    bad = [j["out"] for j in jobs if not _done(j)]
    if bad:
        raise SystemExit(f"3-D jobs missing after the run: {bad}")


def week_jobs() -> list:
    """The preview's 3-D jobs: the high view in three chunks and the towers' close-up for the inset."""
    base = dict(clock="week", **WEEK, fps=L3FPS)
    out = []
    for i, (a, b) in enumerate(((0.0, 20.0), (20.0, 40.0), (40.0, 60.0))):
        out.append(dict(base, v0=a, v1=b, views=[[0.0, 1e9, "high"]], out=str(TMP / f"week_high_{i}"), size=[W, H]))
    out.append(dict(base, v0=PIP["t0"], v1=PIP["t1"], views=[[0.0, 1e9, PIP["view"]]], out=str(TMP / "week_pip"),
                    size=list(PIP["size"])))
    return out


# ============================================================================================ the overlays
STATION_WORDS = {"atomizer": "atomizer", "sieve": "sieving", "utah_midi": "LPBF (MIDI)", "edm": "wire EDM",
                 "tensile": "tensile", "tensile_hot": "tensile, hot", "utah_mxlab": "DED", "byu_icpms": "ICP-MS",
                 "doser": "doser, press", "psd": "particle size", "byu_sem": "SEM", "xrd": "XRD", "xrf": "XRF",
                 "furnace": "furnace", "prep": "metallography", "hardness": "Vickers", "nanoindent": "nanoindenter",
                 "pip": "PIP", "cubxl": "corrosion", "immersion": "immersion", "density": "density", "shop": "machining"}
DOCK_WORDS = {"repowder": "the atomizer", "sieve_cell": "the sieving cell", "aconity": "the Aconity MIDI",
              "wire_edm": "the wire EDM", "instron_small": "the Instron", "instron_floor": "the Instron 68FM",
              "ded": "the DED machine", "fumehood": "the ICP-MS hood", "vlm": "Shuttle 1's opening",
              "vlm2": "Shuttle 2's opening", "glovebox": "the glovebox", "packaging": "packaging"}


def _tag(text: str, col=None, size: float = 16) -> Image.Image:
    f = St.font(size, bold=True)
    w = St.text_w(f, text) + px(18) + (px(14) if col else 0)
    h = px(size * 1.55)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(6), fill=(18, 20, 24, 215))
    x = px(9)
    if col:
        d.rounded_rectangle((x, h / 2 - px(5), x + px(10), h / 2 + px(5)), radius=px(2), fill=tuple(col) + (255,))
        x += px(14)
    d.text((x, h / 2), text, font=f, fill=St.INK + (255,), anchor="lm")
    return im


def _req_words(r) -> tuple:
    """(text, campaign colour) for a request."""
    R = C.S("R")
    des = R.design[r.event] if r.event < len(R.design) else None
    camp = St.CAMP_NAME.get(r.campaign, r.campaign)
    who = f"{camp} #{des}" if des is not None else camp
    return f"{STATION_WORDS.get(r.station, r.station)}, {who}", St.CAMP.get(r.campaign)


def _free(box, placed) -> bool:
    return not any(not (box[2] <= p[0] or p[2] <= box[0] or box[3] <= p[1] or p[3] <= box[1]) for p in placed)


def _put(fr, tg, cx, y, placed, step: int, tries: int = 4) -> bool:
    """Paste tag tg centred on cx at y, moving it by `step` px until it is clear of what is placed."""
    x = int(cx - tg.width / 2)
    for _ in range(tries):
        box = (x, int(y), x + tg.width, int(y) + tg.height)
        if 0 <= box[0] and box[2] <= W and 0 <= box[1] and box[3] <= H and _free(box, placed):
            St.paste(fr, tg, box[0], box[1])
            placed.append(box)
            return True
        y += step
    return False


def moving_tags(fr: np.ndarray, plan, v: float, view: str, placed: list):
    """A tag over each tray presented (or on its way), above its Shuttle's opening, and one under each unit driving or
    working."""
    kin = plan.kin
    st = plan.state(v)
    for s, ts in sorted(st["towers"].items()):
        m = ts.get("move")
        k = ts["out"] or ts["moving"]
        r = getattr(m, "req", None) if m is not None else None
        if not k or r is None:
            continue
        words, col = _req_words(r)
        if ts["moving"]:
            txt = f"tray {k} {'out to the opening' if m.kind == 'fetch' else 'back to its slot'}"
        else:
            txt = f"tray {k}: {words}"
        x0 = kin["shuttle_x"][str(s)]
        xy = project(view, np.array([[x0, kin["open"][0] - 600.0, 2100.0]]))[0]
        tg = _tag(txt, col, size=14)
        _put(fr, tg, xy[0], xy[1] - tg.height - px(6), placed, -tg.height - px(4))
    for u, us in enumerate(st["units"]):
        a = us.get("act")
        if a is None or (a.kind not in ("drive", "work", "wait")) or v >= a.v1:
            continue
        if a.kind == "drive" and not isinstance(a.where, str):
            txt = f"unit {u + 1}: to its charger"
        elif a.kind == "drive":
            txt = f"unit {u + 1} to {DOCK_WORDS.get(a.where, a.where)}"
        else:
            txt = f"unit {u + 1} at {DOCK_WORDS.get(a.where, a.where)}"
        col = None
        if a.job is not None and a.job.req is not None:
            col = St.CAMP.get(a.job.req.campaign)
        x_, y_, _ = us["pose"]
        xy = project(view, np.array([[x_, y_ - 500.0, 0.0]]))[0]
        tg = _tag(txt, col, size=14)
        _put(fr, tg, xy[0], xy[1] + px(6), placed, tg.height + px(4))


_MP: dict = {}


def moves_panel(plan, v: float, h0: float, h1: float, rate: float, when: str = "this week") -> Image.Image:
    """How the moves are drawn, and how many of this stretch's requests fit (redrawn when its text changes)."""
    c = plan.lab_counts(round(h0 * 2) / 2, round(h1 * 2) / 2)
    key = (id(plan), tuple(sorted(c.items())), round(rate), when)
    if key in _MP:
        return _MP[key]
    if len(_MP) > 64:
        _MP.clear()
    _MP[key] = im = _moves_panel(c, rate, when)
    return im


def _moves_panel(c: dict, rate: float, when: str) -> Image.Image:
    w, h = px(420), px(104)
    im, d = St.layer(w, h)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=px(12), fill=St.SURF + (int(255 * St.PANEL_A),))
    d.text((px(16), px(10)), f"Moves drawn at {rate:.0f}x real time", font=St.font(18, bold=True), fill=St.INK)
    d.text((px(16), px(36)), f"a tray change: about {10.0 / rate:.1f} s here, 8-12 s in the lab", font=St.font(16),
           fill=St.INK2)
    d.text((px(16), px(60)), f"{when}: {c['tray_drawn']} of {c['tray_asked']} tray requests drawn,",
           font=St.font(16), fill=St.INK2)
    d.text((px(16), px(80)), f"{c['floor_drawn']} of {c['floor_asked']} machine visits", font=St.font(16),
           fill=St.INK2)
    return im


def pip_frame(img: np.ndarray, box, label: str, a: float) -> tuple:
    x, y, w, h = (px(v) for v in box)
    small = Image.fromarray(np.ascontiguousarray(img)).resize((w, h), Image.BILINEAR)
    frame = Image.new("RGBA", (w + px(6), h + px(6)), (18, 20, 24, 235))
    frame.paste(small, (px(3), px(3)))
    from PIL import ImageDraw
    d = ImageDraw.Draw(frame)
    f = St.font(16, bold=True)
    tw = St.text_w(f, label) + px(18)
    d.rounded_rectangle((px(8), px(8), px(8) + tw, px(8) + px(26)), radius=px(6), fill=(18, 20, 24, 215))
    d.text((px(17), px(21)), label, font=f, fill=St.INK + (255,), anchor="lm")
    return frame, x - px(3), y - px(3)


class WeekCut:
    """The preview: one simulated week from above, its overlays drawn per frame."""

    def __init__(self):
        self.kin = LS.load_kin()
        self.clock = LS.Clock.linear(WEEK["lab_h0"], WEEK["hours_per_s"], WEEK["seconds"])
        self.R = C.S("R")
        self.plan = LS.plan(self.R, self.kin, self.clock)
        jobs = week_jobs()
        self.main = Tracks([j for j in jobs if "pip" not in j["out"]])
        self.pip = Tracks([j for j in jobs if "pip" in j["out"]])
        self.anc = anchors("high", self.kin)
        be = C.S("be")
        be.chip_dx = {1: -150.0, 2: 150.0}
        be.chip_avoid = True
        be.avoid = list(be.avoid) + [(px(866), px(900), px(1286), px(1004))]       # the moves panel
        self.be = be
        self.rate = LS.move_rate(WEEK["hours_per_s"])

    def frame(self, t: float) -> np.ndarray:
        R, be, kin = self.R, self.be, self.kin
        t_h = self.clock.lab(t)
        sp = WEEK["hours_per_s"]
        img = self.main.frame(t)
        span = max(0.25, sp * 0.6)
        pip_on = PIP["t0"] + 0.4 <= t < PIP["t1"] - 0.4
        avoid0 = list(be.avoid)
        if pip_on:
            x, y, w, h = PIP["box"]
            be.avoid = avoid0 + [(px(x), px(y), px(x + w), px(y + h))]
        fr = be.frame_live(img, self.anc, t_h, span, offsite=True)
        be.avoid = avoid0
        placed = []
        moving_tags(fr, self.plan, t, "high", placed)
        a = min(1.0, (t - PIP["t0"]) / 0.4, (PIP["t1"] - t) / 0.4)
        if a > 0:
            im, x, y = pip_frame(self.pip.frame(min(max(t, PIP["t0"]), PIP["t1"] - 1e-3)), PIP["box"],
                                 "Shuttles up close (second camera)", a)
            St.paste(fr, im, x, y, a)
        St.paste(fr, C.clock_panel(t_h, sp), px(24), px(20))
        St.paste(fr, moves_panel(self.plan, t, WEEK["lab_h0"], WEEK["lab_h0"] + 168.0, self.rate), px(866), px(900))
        nf = {c: R.wip(t_h, c) for c in D.CAMPAIGNS}
        pill = C.now_pill(f"One simulated week: {nf['flaime_al']} FLAIME and {nf['onr_cu']} ONR alloys in progress",
                          "the 3-D lab moved by the event log: trays to the openings, units to the docks")
        St.paste(fr, pill, (px(520) + px(1400) - pill.width) // 2, px(24))
        St.paste(fr, C.counters_panel(t_h), px(1446), px(20))
        P = C.S("pt")
        q = round(t * 2) / 2
        items = []
        for c in D.CAMPAIGNS:
            items += [(c,) + tuple(x) for x in R.in_progress(t_h, c, n=3)]
        items = items[:6]
        key = ("multi", tuple((x[0], x[1], x[3]) for x in items), q if not items else None)
        if items:
            im = C.ptable_overlay(key, lambda: P.multiples_panel(items, px(450), px(300),
                                                                 title="Compositions in progress"))
        else:
            im = C.ptable_overlay(key, lambda: C._empty_panel("Compositions in progress", "none right now"))
        St.paste(fr, im, px(1446), px(186))
        St.paste(fr, C.S("plots").draw(t_h), px(1296), px(640))
        dag = C.S("dag")
        lit = {k: dag.intensity(v) for k, v in R.lit(t_h, span).items()}
        x, y, _, _ = dag.DOCK
        St.paste(fr, dag.overlay(lit, t=t), px(x), px(y))
        kf = min(1.0, t / C.FADE, (WEEK["seconds"] - t) / C.FADE)
        if kf < 1.0:
            fr = St.dim(np.array(fr, copy=True), max(0.0, kf))
        return C.tag_placeholder(fr)


# ============================================================================================ the replay's 3-D phases
XF = 0.6                       # compose.replay_frame's crossfade into the next phase: that phase's track starts early
CHUNK = 24.0                   # seconds of track per render job
CHIPS = {"high": {1: -150.0, 2: 150.0}, "sw": {1: -130.0, 2: 130.0}, "se": {1: -130.0, 2: 130.0}}
_REPLAY: dict = {}


def _phase_span(i: int) -> tuple:
    tl = C.S("tl")
    a = tl.phase_t[i]
    b = tl.phase_t[i + 1] if i + 1 < len(tl.phase_t) else tl.dur
    return a, b


def replay_jobs() -> list:
    """The animated cut's 3-D jobs: each phase's camera over its span (from XF before it, for the crossfade in), in
    chunks of CHUNK seconds, and the inset's camera where the phase has one."""
    tl = C.S("tl")
    base = dict(clock="replay", clock_v0=round(tl.t_pov, 4), clock_v1=round(tl.dur, 4))
    out = []
    for i, ph in enumerate(C.PHASES3D):
        a, b = _phase_span(i)
        base["fps"] = L3FPS if i < 2 else L3FPS_FAST
        a0 = max(tl.t_pov, a - (XF if i else 0.0))
        for track, view, x0, x1, size in (("main", ph[2], a0, b, [W, H]),
                                          ("pip", ph[3], a + 1.0, b - 1.0, list(PIP["size"]))):
            if view is None or x1 - x0 < 1.0:
                continue
            k, x = 0, x0
            while x < x1 - 1e-6:
                y = min(x1, x + CHUNK)
                if x1 - y < 6.0:
                    y = x1
                out.append(dict(base, v0=round(x, 4), v1=round(y, 4), views=[[0.0, 1e9, view]], size=size,
                                out=str(TMP / f"replay_p{i}_{track}_{k}_{view}"), phase=i, track=track))
                x, k = y, k + 1
    return out


def replay_state() -> dict:
    if not _REPLAY:
        tl = C.S("tl")
        kin = LS.load_kin()
        clock = LS.Clock.from_timeline(tl, round(tl.t_pov, 4), round(tl.dur, 4))
        _REPLAY.update(kin=kin, clock=clock, plan=LS.plan(C.S("R"), kin, clock), anc={}, tracks={})
        groups: dict = {}
        for j in replay_jobs():
            groups.setdefault((j["phase"], j["track"]), []).append(j)
        _REPLAY["tracks"] = {k: Tracks(v) for k, v in groups.items()}
    return _REPLAY


def replay_picture(i: int, t: float, t_h: float, sp: float) -> np.ndarray:
    """Phase i of the animated replay at t: the 3-D track, the stations lit, the tags on what moves, the inset and the
    moves panel. compose.replay_frame draws the clock, counters, compositions, plots and networks over it."""
    st = replay_state()
    ph = C.PHASES3D[i]
    view = ph[2]
    kin, plan = st["kin"], st["plan"]
    img = st["tracks"][(i, "main")].frame(t)
    if view not in st["anc"]:
        st["anc"][view] = anchors(view, kin)
    be = C.S("be")
    a, b = _phase_span(i)
    pip_on = ph[3] is not None and (i, "pip") in st["tracks"] and a + 1.0 <= t < b - 1.0
    avoid0 = list(be.avoid)
    # round 3's cut keeps the seed badge under the moves panel (compose.seed_badge): the panel sits 22 px higher and
    # the chips and tags keep clear of both
    y_mp = 878 if D.ROUND == 3 else 900
    be.avoid = avoid0 + [(px(866), px(y_mp), px(1286), px(1080 if D.ROUND == 3 else 1004))]
    if pip_on:
        x, y, w, h = PIP["box"]
        be.avoid.append((px(x), px(y), px(x + w), px(y + h)))
    be.show_chips = view in CHIPS
    be.chip_dx = CHIPS.get(view, {1: 0.0, 2: 0.0})
    be.chip_avoid = True
    fr = be.frame_live(img, st["anc"][view], t_h, max(1.0, sp * 0.8), offsite=True)
    be.avoid = avoid0
    be.show_chips, be.chip_avoid, be.chip_dx = True, False, {1: 0.0, 2: 0.0}
    placed = [(px(866), px(y_mp), px(1286), px(1080))] if D.ROUND == 3 else []
    moving_tags(fr, plan, t, view, placed)
    if pip_on:
        k = min(1.0, (t - a - 1.0) / 0.4, (b - 1.0 - t) / 0.4)
        im, x, y = pip_frame(st["tracks"][(i, "pip")].frame(t), PIP["box"],
                             "Shuttles up close (second camera)", k)
        St.paste(fr, im, x, y, max(0.0, k))
    rate = LS.move_rate(sp)
    St.paste(fr, moves_panel(plan, t, t_h - 168.0, t_h, rate, "the last 7 days"), px(866), px(y_mp))
    return fr


# ============================================================================================ encoding
_CUT: dict = {}


def cut():
    if "w" not in _CUT:
        _CUT["w"] = WeekCut()
    return _CUT["w"]


def piece(a: float, b: float, out: Path, preset: str):
    wc = cut()
    enc = C.encoder(out, preset)
    n = int(round((b - a) * FPS))
    t0 = time.time()
    for k in range(n):
        fr = wc.frame(a + k / FPS)
        enc.stdin.write(np.ascontiguousarray(fr, np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    return dict(a=a, b=b, frames=n, wall=round(time.time() - t0, 1))


def build_week(workers: int, preset: str) -> Path:
    t0 = time.time()
    TMP.mkdir(parents=True, exist_ok=True)
    run_jobs(week_jobs(), workers)
    print(f"3-D done in {time.time() - t0:.0f} s", flush=True)
    pieces = []
    for i, (a, b) in enumerate(((0.0, 20.0), (20.0, 40.0), (40.0, 60.0))):
        pieces.append((a, b, TMP / f"week_cut_{i}.mp4"))
    running = []
    todo = list(pieces)
    while todo or running:
        while todo and len(running) < workers:
            a, b, out = todo.pop(0)
            p = subprocess.Popen([sys.executable, "-m", "twin.video.lab3d_cut", "piece", f"{a}", f"{b}", str(out),
                                  preset], cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            running.append((p, out))
        time.sleep(1.0)
        for item in list(running):
            p, out = item
            if p.poll() is not None:
                running.remove(item)
                txt = p.stdout.read()
                print(f"  cut {out.name}: rc {p.returncode} {txt.strip().splitlines()[-1][:200] if txt.strip() else ''}",
                      flush=True)
                if p.returncode != 0:
                    print(txt[-3000:])
                    raise SystemExit("cut piece failed")
    dst = D.VID / "lab3d_week.mp4"
    C.concat([p[2] for p in pieces], dst)
    print(f"{dst}: {C._duration(dst)} s, {time.time() - t0:.0f} s in all", flush=True)
    return dst


def week_meta(dst: Path) -> Path:
    """Title, description and tags of the preview -> out/twin2/video/lab3d_week_meta.json (unlisted)."""
    wc = cut()
    c = wc.plan.counts
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=HERE).stdout.strip()
    day0 = int(WEEK["lab_h0"] // 24) + 1
    desc = (
        "A preview, for review: one simulated week (days " f"{day0}-{day0 + 6}" ") of the digital twin's replayed "
        "year, with PR 318's 3-D lab moved by the twin's event log. Simulated, not lab results.\n\n"
        "Every tray presented at a Kardex Shuttle's opening and every MiR250 + UR12e visit to a dock comes from a "
        "booking in the event log (out/twin2/events/vertical_lab_bofn_blend_s0.json): a station on a tray has its tray "
        "brought to the opening when the booking starts and again when it ends, and a floor machine has a unit dock at "
        "its front. Idle trays stay in their slots.\n\n"
        f"The clock runs at {WEEK['hours_per_s']:.1f} lab hours a second. At that speed a tray change (8-12 s with "
        "the tower's own timings) would last a few thousandths of a second, so the moves run on their own clock, "
        f"{wc.rate:.0f} times real time, each starting when the clock reaches its booking: the lift at 1333 mm/s, "
        "the 2.2 s slides, the 0.7 s shutter, the MiR250 at 1.5 m/s pivoting at 60 deg/s, the arm's pick and place. "
        "When the moves can't keep up, each Shuttle and unit takes the latest request. This week: "
        f"{c['tray_drawn']} of {c['tray_asked']} tray requests and {c['floor_drawn']} of {c['floor_asked']} machine "
        "visits are drawn (the panel at the bottom says so).\n\n"
        "Overlays as in the campaign video: stations lit from the event log, the two function networks, the "
        "compositions in progress, the live best-so-far plots. The inset is a second camera on the two Shuttles.\n\n"
        f"Code: https://github.com/vertical-cloud-lab/byu-vcl/tree/{commit}/vertical-lab/twin/video "
        "(lab3d.py, lab3d_sched.py, lab3d_cut.py)\n"
        "PR: https://github.com/vertical-cloud-lab/byu-vcl/pull/393\n")
    meta = dict(title="Preview: one simulated week of the automated lab, moved by the event log (digital twin)",
                description=desc, tags=["vertical cloud lab", "BYU", "digital twin", "laboratory automation",
                                        "self-driving lab", "Kardex Shuttle", "MiR250", "UR12e", "simulated"],
                categoryId="28", privacy="unlisted", notifySubscribers=False, file=str(dst.relative_to(HERE)),
                seconds=C._duration(dst), commit=commit, counts=c)
    out = D.VID / "lab3d_week_meta.json"
    out.write_text(json.dumps(meta, indent=1) + "\n")
    return out


def stills(times: list):
    Path("/tmp/vid").mkdir(exist_ok=True)
    wc = cut()
    for t in times:
        c0 = time.process_time()
        fr = wc.frame(t)
        Image.fromarray(np.ascontiguousarray(fr)).save(f"/tmp/vid/week_{t:05.1f}.png")
        print(f"{t:6.1f} s: {1000 * (time.process_time() - c0):.0f} ms cpu", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "preview"
    if cmd == "piece":
        print(json.dumps(piece(float(args[1]), float(args[2]), Path(args[3]), args[4])), flush=True)
    elif cmd == "preview":
        build_week(int(os.environ.get("TWIN_VIDEO_WORKERS", "3")), os.environ.get("TWIN_VIDEO_PRESET", "medium"))
    elif cmd == "jobs":
        run_jobs(week_jobs(), int(os.environ.get("TWIN_VIDEO_WORKERS", "3")))
    elif cmd == "stills":
        stills([float(x) for x in args[1:]])
    elif cmd == "meta":
        print(week_meta(D.VID / "lab3d_week.mp4"))
    else:
        raise SystemExit(__doc__)

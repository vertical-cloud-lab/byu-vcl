"""The lab's own renders, cut to the step that is happening: which clip and which seconds show each kind of event, the
crop that drops a clip's burnt-in title and caption band, and a seekable ffmpeg reader.

Clip times come from the sub-step JSON each render wrote beside itself (out/<clip>.json: its fps and every sub-step's
frames; longform.py reads the same files). The 1080p renders in out/hd/ match out/<clip>.json frame for frame, except
alloy_atomize, whose out/hd/ copy is an older cut: the 720p out/mp4/ one is used for it.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

from . import style as St
from .data import HERE, VID

OUT = HERE / "out"
CACHE = VID / "cache"


def src(clip: str) -> Path:
    """The best render of a clip: out/hd/ (1080p) when it matches its sub-step JSON, else out/mp4/ (720p)."""
    hd, sd = OUT / "hd" / f"{clip}.mp4", OUT / "mp4" / f"{clip}.mp4"
    if clip != "alloy_atomize" and hd.exists():
        return hd
    return sd


def _sub(clip: str, frm: int) -> float:
    """A frame number of out/<clip>.json in seconds."""
    m = json.loads((OUT / f"{clip}.json").read_text())
    return frm / float(m["fps"])


# Every kind of event the twin logs ('what') -> shots that show it: (clip, from s, to s, label). The seconds are sub-step
# boundaries of out/<clip>.json (see notes/twin_video.md for the captions they carry).
SHOTS = {
    "charge": [("alloy_charge", 24.5, 41.7, "charge: dosing Si into a cup (multi-doser, tray B)"),
               ("alloy_charge", 101.3, 115.1, "charge: the cup pressed under vacuum (tray B)")],
    "atomize": [("alloy_atomize", 81.9, 94.9, "atomize: the cups go into the crucible"),
                ("alloy_atomize", 211.3, 219.9, "atomize: the melt (real footage, right)"),
                ("alloy_atomize", 236.5, 243.9, "atomize: the pour (real footage, right)")],
    "powder QC": [("alloy_print", 61.9, 75.3, "powder: sieving"),
                  ("alloy_powder", 439 / 6, 507 / 6, "powder: XRD (tray D)"),
                  ("alloy_powder", 864 / 6, 964 / 6, "powder: size distribution (tray E)"),
                  ("alloy_powder", 569 / 6, 650 / 6, "powder: SEM (tray D)"),
                  ("alloy_powder", 1154 / 6, 1251 / 6, "powder: XRF (tray M)")],
    "print": [("alloy_print", 229.9, 241.0, "LPBF: the powder into the MIDI"),
              ("alloy_print", 248.8, 271.6, "LPBF: the print, cut open")],
    "test": [("alloy_workflow", 9.8, 26.8, "test: depowdering the plate"),
             ("alloy_workflow", 112.7, 127.5, "test: wire EDM"),
             ("alloy_workflow", 1418 / 6, 1535 / 6, "test: heat treat and quench (tray F)"),
             ("alloy_workflow", 1942 / 6, 2011 / 6, "test: tensile")],
    "section": [("alloy_prep", 39 / 6, 71 / 6, "section: cutting the slice"),
                ("alloy_prep", 760 / 6, 801 / 6, "section: hot mounting (tray F)"),
                ("alloy_prep", 1060 / 6, 1153 / 6, "section: polishing (tray F)"),
                ("alloy_characterize", 165 / 6, 274 / 6, "section: SEM and EDS (tray D)"),
                ("alloy_characterize", 975 / 6, 1060 / 6, "section: micro-Vickers (tray L)")],
    "pip": [("alloy_characterize", 640 / 6, 738 / 6, "PIP: indentation plastometry (tray E)"),
            ("alloy_characterize", 493 / 6, 560 / 6, "nanoindentation (tray E)")],
    "screen": [("vlm_workflow", 68.2, 85.5, "corrosion: tray A, the CubXL"),
               ("vlm_workflow", 85.5, 103.1, "corrosion screen (CubXL)")],
    "immersion": [("icpms", 17.5, 41.8, "immersion: samples diluted for ICP-MS"),
                  ("icpms", 48.8, 78.2, "ICP-MS")],
}
SHOTS["machine"] = [("machining_cell", 0.3, 14.8, "charge: a cup turned from bar (machining cell)")]
SHOTS["tensile"] = [SHOTS["test"][3], SHOTS["test"][1]]
SHOTS["promote"] = SHOTS["print"][1:] + SHOTS["test"]
ALIAS = {"blown_small": "ded", "blown_large": "ded", "preplaced": "ded", "blend_ded": "ded", "nsl": "offsite", "gas_atomize": "offsite",
         "sim_open": "sim", "sim_tc": "sim", "sim_am": "sim", "sim_heat": "sim"}
# station -> the shot kind its multi-camera cell plays
STATION_SHOT = {"doser": "charge", "shop": "machine", "atomizer": "atomize", "sieve": "powder QC", "psd": "powder QC",
                "xrd": "powder QC", "xrf": "powder QC", "byu_sem": "section", "utah_midi": "print", "density": "print",
                "edm": "test", "furnace": "test", "tensile": "test", "tensile_hot": "test", "prep": "section",
                "hardness": "section", "nanoindent": "pip", "pip": "pip", "cubxl": "screen", "immersion": "screen",
                "byu_icpms": "immersion", "utah_mxlab": "ded", "mines_x2": "offsite", "nsl": "offsite",
                "hpc": "sim", "valimet": "offsite", "ames": "offsite"}
STATION_PICK = {"sieve": 0, "xrd": 1, "psd": 2, "byu_sem": 3, "xrf": 4, "edm": 1, "furnace": 2, "tensile": 3,
                "tensile_hot": 3, "prep": 2, "hardness": 4, "nanoindent": 1, "pip": 0, "immersion": 1,
                "byu_icpms": 1, "cubxl": 1, "density": 1, "doser": 0, "shop": 1}


def shots_for(what: str) -> list:
    return SHOTS.get(what) or SHOTS.get(ALIAS.get(what, ""), [])


# ------------------------------------------------------------------------------------------------- the crop
def _grab(path: Path, t: float) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-vframes", "1", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    w, h = probe(path)[:2]
    return np.frombuffer(r.stdout[:w * h * 3], np.uint8).reshape(h, w, 3)


_PROBE: dict = {}


def probe(path: Path) -> tuple:
    k = str(path)
    if k not in _PROBE:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                           capture_output=True, text=True, check=True)
        js = json.loads(r.stdout)
        s = js["streams"][0]
        num, den = s["r_frame_rate"].split("/")
        _PROBE[k] = (int(s["width"]), int(s["height"]), float(num) / float(den), float(js["format"]["duration"]))
    return _PROBE[k]


def band_top(img: np.ndarray) -> int:
    """The top of a render's caption band: the dark blue rule over the near-white band at the bottom (scene.py), found
    as the lowest-but-one long run of rows whose middle is blue; the frame's height if there is none."""
    h = img.shape[0]
    mid = img[:, img.shape[1] // 8: img.shape[1] * 7 // 8].astype(np.int16)
    r, g, b = mid[..., 0].mean(1), mid[..., 1].mean(1), mid[..., 2].mean(1)
    blue = (b > r + 40) & (b > g + 25) & (r < 90)
    rows = [y for y in range(int(h * 0.55), h) if blue[y]]
    if rows:
        return int(min(rows))
    light = (mid.min(2).mean(1) > 228)                  # no rule: the light band itself
    y = h - 1
    while y > h * 0.6 and light[y]:
        y -= 1
    return y + 1 if y < h - 4 else h


TOP_CUT = 0.15
# shots whose right-hand side is the lab's own footage (the render beside it): cropped flush right, and compose clears
# its right-hand panels while they play
RIGHT = {("alloy_atomize", 211.3), ("alloy_atomize", 236.5)}


def anchor_of(clip: str, t0: float) -> str:
    return "r" if (clip, round(t0, 1)) in RIGHT else "c"


def crop_box(clip: str, t0: float, t1: float) -> tuple:
    """(x, y, w, h) in the clip's pixels: below its title row, above its tallest caption band over [t0, t1], at 16:9.
    Cached in out/twin2/video/cache/crops.json."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cf = CACHE / "crops.json"
    cache = json.loads(cf.read_text()) if cf.exists() else {}
    anchor = anchor_of(clip, t0)
    key = f"{src(clip).name}|{src(clip).parent.name}|{t0:.2f}|{t1:.2f}|{TOP_CUT}|{anchor}"
    if key in cache:
        return tuple(cache[key])
    p = src(clip)
    W_, H_ = probe(p)[:2]
    top = int(round(H_ * TOP_CUT))                       # the title box and step badge, and gauge rows under them
    bot = H_
    for u in (0.1, 0.5, 0.9):
        try:
            bot = min(bot, band_top(_grab(p, t0 + (t1 - t0) * u)))
        except Exception:                               # noqa: BLE001
            pass
    bot = max(bot - 3, int(H_ * 0.72))
    h = bot - top
    w = int(h * 16 / 9)
    w = min(w, W_)
    h = int(w * 9 / 16)
    x = (W_ - w) // 2 if anchor == "c" else W_ - w
    box = (x, top, w, h)
    cache[key] = box
    cf.write_text(json.dumps(cache, indent=0))
    return box


# ------------------------------------------------------------------------------------------------ the reader
class Reader:
    """Frames of one shot, [t0, t1] of a clip, cropped and scaled to (w, h), played at `speed`, looped; read
    sequentially from one ffmpeg process, restarted when asked to seek backwards or far ahead."""

    def __init__(self, clip: str, t0: float, t1: float, w: int, h: int, speed: float = 1.0, fps: float = 30.0):
        self.clip, self.t0, self.t1, self.w, self.h, self.speed, self.fps = clip, t0, t1, w, h, speed, fps
        self.path = src(clip)
        self.box = crop_box(clip, t0, t1)
        self.p = None
        self.pos = None                                 # index of the next frame the pipe gives
        self.last = None
        self.span = max(0.5, (t1 - t0) / speed)        # seconds of output per loop

    def _start(self, k: int):
        self.close()
        off = (k / self.fps) * self.speed
        x, y, w, h = self.box
        vf = (f"crop={w}:{h}:{x}:{y},setpts=(PTS-STARTPTS)/{self.speed},fps={self.fps},"
              f"scale={self.w}:{self.h}:flags=bicubic")
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-threads", "1", "-ss", f"{self.t0 + off:.3f}", "-i", str(self.path),
             "-t", f"{max(0.2, self.t1 - self.t0 - off):.3f}", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=self.w * self.h * 3 * 2)
        self.pos = k

    def frame(self, t: float) -> np.ndarray:
        """The frame t seconds into the shot (looping)."""
        k = int((t % self.span) * self.fps + 1e-6)
        if self.p is None or self.pos is None or k < self.pos or k > self.pos + 90:
            self._start(k)
        n = self.w * self.h * 3
        while self.pos <= k:
            buf = self.p.stdout.read(n) if self.p else b""
            if len(buf) < n:                            # ran out (the clip's end): hold the last frame
                if self.last is None:
                    self.last = np.zeros((self.h, self.w, 3), np.uint8)
                self.pos = k + 1
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.pos += 1
        return self.last

    def close(self):
        if self.p is not None:
            try:
                self.p.stdout.close()
                self.p.kill()
                self.p.wait(timeout=2)
            except Exception:                           # noqa: BLE001
                pass
        self.p = None


class Pool:
    """Readers by key, closed when not asked for in a while (so a long render holds a handful of ffmpeg processes)."""

    def __init__(self, keep: int = 14):
        self.r: dict = {}
        self.age: dict = {}
        self.tick = 0
        self.keep = keep

    def get(self, key, make):
        self.tick += 1
        if key not in self.r:
            self.r[key] = make()
        self.age[key] = self.tick
        if len(self.r) > self.keep:
            for k in sorted(self.r, key=lambda k: self.age[k])[: len(self.r) - self.keep]:
                self.r.pop(k).close()
                self.age.pop(k, None)
        return self.r[key]

    def close(self):
        for r in self.r.values():
            r.close()
        self.r.clear()


def still(clip_path: Path, t: float, w: int, h: int, box=None) -> np.ndarray:
    """One frame of a video, cropped and scaled (cached on disk)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = f"{Path(clip_path).stem}_{t:.2f}_{w}x{h}_{'-'.join(map(str, box)) if box else 'full'}.png"
    f = CACHE / key
    from PIL import Image
    if f.exists():
        return np.asarray(Image.open(f).convert("RGB"))
    img = _grab(Path(clip_path), t)
    if box:
        x, y, bw, bh = box
        img = img[y:y + bh, x:x + bw]
    im = Image.fromarray(np.ascontiguousarray(img)).resize((w, h), Image.LANCZOS)
    im.save(f)
    return np.asarray(im)


def label_chip(text: str, size: float = 20, pad: float = 8):
    """A small dark chip with a label, for a camera cell."""
    from PIL import Image, ImageDraw
    f = St.font(size, bold=True)
    w = St.text_w(f, text) + 2 * St.px(pad)
    h = St.px(size * 1.25) + 2 * St.px(pad * 0.6)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=St.px(6), fill=St.SURF + (215,))
    d.text((St.px(pad), h / 2), text, font=f, fill=St.INK, anchor="lm")
    return im

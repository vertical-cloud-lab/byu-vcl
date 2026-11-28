"""A short highlight of the vertical lab's latest work: the alloy route from round 16's long-form, what the lab model
gained since round 15, the digital twin's latest results, and the whole lab at speed, each shot under a caption naming
the instruments in it.

Sterling, PR #390 (2026-11-28): "can we get this updated with the most recent vertical lab progress across all of this
repo (see all issue and PR comments via gh API) and DAL (if applicable)? Re-uploaded to YouTube. Public with notify
subscribers."

It replaces the first edition, Sterling's PR #318 request of 2026-11-25 ("Cut a 2 to 3 minute highlight of round 15's
long-form: one shot from each chapter of the alloy route ..., then the whole lab at speed, with short captions naming
each instrument"). That edition's script is this file at d349073 and its outputs stay in out/highlight/ (the MP4,
stills/, highlight.json); this edition's go to out/highlight/2026-11-28/.

No renders survive their runners (out/r16/ and the twin's video folders are git-ignored), so every shot is cut from a
video as YouTube serves it, fetched only around each shot: its HLS stream (H.264 at 30 fps, the highest bitrate YouTube
offers for it). YouTube refuses player requests from GitHub's runners, so `fetch` goes through a lab Pi's network over
an SSH SOCKS tunnel, rate-capped for the Pi's Wi-Fi:

    ssh -D 127.0.0.1:1080 -N -f <user>@<pi>                       # any lab Pi this run can reach
    python3 highlight.py fetch --proxy socks5h://127.0.0.1:1080   # each shot's segments, into $HIGHLIGHT_CACHE
    python3 highlight.py sheets                                    # 2 fps contact sheets, to set in and out points
    python3 highlight.py bandscan                                  # each shot's band covers the source's own band
    python3 highlight.py build                                     # out/highlight/2026-11-28/: MP4, stills, sheet
    python3 highlight.py upload --privacy public --notify          # on the lab's channel

Each shot keeps its source's picture as it was, with its title bar and status panel. Only the source's caption band
(a sentence that a highlight would cut off mid-step) is covered, by a band in the long-form's style naming the
instruments in the shot. The narration is left out for the same reason: its lines don't start or stop with the shots.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import longform as L  # noqa: E402  (its card style and fonts, so the cards match the long-form's)

EDITION = "2026-11-28"
OUT = HERE / "out" / "highlight" / EDITION
CACHE = Path(os.environ.get("HIGHLIGHT_CACHE", "/tmp/vertical_lab_highlight"))
NAME = f"vertical_lab_highlight_{EDITION}"
W, H, FPS = 1280, 720, 30
PAD = 4.0                                       # seconds fetched either side of a shot, room to move its in/out
XFADE = 0.5                                     # dissolve between parts
TITLE_S, END_S = 5.0, 7.0
REPO = "vertical-cloud-lab/byu-vcl"
DAL = "vertical-cloud-lab/digital-alloy-lab"
ARM = "arm: UR12e on a MiR250"

# Every source is on the lab's channel. itag: the HLS stream cut from (1080p sources are scaled to 720p once, when the
# window is cut).
SOURCES = {
    "r16": dict(id="YWbplBXPC84", itag="232", size=(1280, 720), short="round 16's long-form",
                title="The vertical cloud lab, start to finish (3-D, round 16)", length="1:31:05", pr=318),
    "twin": dict(id="Ty6njW-GF74", itag="270", size=(1920, 1080), short="the twin's two-year cut",
                 title="Two simulated years of alloy discovery, from the day the money arrives: round 5 (preview)",
                 length="19:54", pr=428),
}


def url(src: str, t: float | None = None) -> str:
    vid = SOURCES[src]["id"]
    return f"https://youtu.be/{vid}" + (f"?t={int(t)}" if t is not None else "")


# t0/t1/still: seconds in the source. band_top: 2 px above the highest the source's caption band reaches in the shot
# (the long-form's navy rule is at 668, 644, 620 or 596 for one to four lines; `bandscan` measures it), so one band of
# ours covers it for the whole shot. band_until: shot seconds after which the band comes off (the finale's last
# seconds are the long-form's own "first year" card, which has no caption band). sec: the section, named in the band.
SHOTS = [
    # ---- the alloy route, round 16 (the first edition's moments, in round 16's renders where it has them)
    dict(key="charge", src="r16", sec="The alloy route", tag="1/7", title="The charge", arm=ARM,
         t0=1167.0, t1=1178.0, still=1167.27, band_top=618,
         caption="powder-doser's chain carousel v5 · A&D HR-202i balance · Specac Atlas Autotouch 15T vacuum press",
         what="A 5N Al cup from the rack to the doser's shuttle; module 6 docks, tilts and doses Si onto the balance."),
    dict(key="atomize", src="r16", sec="The alloy route", tag="2/7", title="Melt and atomize",
         arm="arms: two UR12e on MiR250s", t0=1713.0, t1=1725.6, still=1723.96, band_top=594,
         caption="AMAZEMET rePowder ultrasonic atomizer, cut open for the pour",
         what="Both arms on the plate's landing stage; the melt pours onto the vibrating plate and atomizes."),
    dict(key="sieve", src="r16", sec="The alloy route", tag="3/7", title="Sieve and print", arm=ARM,
         t0=2861.0, t1=2873.0, still=2872.07,
         caption="Retsch AS 200 sieve shaker, in a downdraft enclosure",
         what="The stack sieves under its clamped lid, drawn see-through; each fraction tinted under a legend."),
    dict(key="powder", src="r16", sec="The alloy route", tag="4/7", title="The powder, checked", arm=ARM,
         t0=3147.0, t1=3160.5, still=3160.07,
         caption="Rigaku MiniFlex benchtop powder XRD, its housing drawn see-through",
         what="The holder in, the door shut; the scan; the pattern (computed, not measured)."),
    dict(key="tensile", src="r16", sec="The alloy route", tag="5/7", title="Depowder, cut, heat treat, test", arm=ARM,
         t0=3607.5, t1=3620.0, still=3618.97, band_top=618,
         caption="Instron 68FM-100 · 3119-608 environmental chamber · AVE 2 video extensometer",
         what="A bar in the grips, the chamber cut away, the pull (curve illustrative), broken."),
    dict(key="prep", src="r16", sec="The alloy route", tag="6/7", title="Sample prep", arm=ARM,
         t0=3894.0, t1=3906.2, still=3895.86,
         caption="LECO PX500 grinder-polisher and its magazine of pre-loaded discs",
         what="The arm puts the 320-grit disc on the magnetic platen; the pistons press the mounts down."),
    dict(key="characterize", src="r16", sec="The alloy route", tag="7/7", title="Characterizing the build", arm=ARM,
         t0=4039.0, t1=4051.0, still=4050.06,
         caption="Hitachi TM4000PlusII tabletop SEM · Oxford Instruments AZtecOne EDS",
         what="The conductive mount into the SEM's grounded holder cup; pump-down; a BSE image (illustrative)."),
    # ---- the real lab (DAL): the excerpts of the lab's own Oct 27 run that round 16's chapter 2 also uses
    dict(key="real", kind="real", sec="In the real lab", tag="", title="The lab's own atomizer (DAL)",
         arm="real footage and photo", band_top=618, still=6.0,
         clips=[("out/footage/nab_melt3.mp4", 1.0, 4.5), ("out/footage/nab_pour1.mp4", 0.0, 7.5)],
         source_s=[[329.0, 332.5], [497.0, 504.5]],   # the same seconds in 2brsz-90seg (out/footage/manifest.json)
         photo="out/footage/nab_k7m2q9_sieved_three_jars.jpg",
         badges=("REAL FOOTAGE · 27 OCT 2026", "REAL PHOTO · 29 OCT 2026 · SIEVED: <63, 64-250, >250 µm"),
         caption="AMAZEMET rePowder, 27 Oct 2026: 630 bronze molten, then atomizing on the plate "
                 "(youtu.be/2brsz-90seg) "
                 "· with 28 Oct's run, 1,015 g sieved under 250 µm from 1,938 g charged (DAL PR 286)",
         what="The lab's own run k7m2q9: the melt through the furnace port, the jet atomizing through the view port, "
              "and its sieved powder."),
    # ---- what the lab model gained since round 15 (PRs #353, #369-#379 merged into #318, and #371 in round 16)
    dict(key="plate", src="r16", sec="New in the lab", tag="", title="Automating the atomizer (#353)", arm=ARM,
         t0=2264.4, t1=2275.7, still=2265.4,
         caption="The arm swaps rePowder's ultrasonic plate: the old one off its M8 stud to its labelled slot, "
                 "a W-coated plate on",
         what="One of eight atomizer turnaround clips: the old plate slid off its stud, the new one slid on."),
    dict(key="coupling", src="r16", sec="New in the lab", tag="", title="Services on every tray", arm="",
         t0=254.0, t1=265.0, still=262.0,
         caption="Stäubli CombiTac dock: power, Ethernet, air, N2 and "
                 "chilled water mate in a set order; each powered tray has a UPS",
         what="The dock's head comes in; the last 15 mm of the electrical frame at Staubli's mating speed."),
    dict(key="safety", src="r16", sec="New in the lab", tag="", title="Safety assets (#379)", arm="",
         t0=539.8, t1=550.8, still=545.0,
         caption="Amerex B570 Class D extinguishers, 30 lb of Super D: on "
                 "every MiR250 in an 811 bracket, and at each powder station",
         what="The B570 strapped into its 811 bracket on the MiR250's cabinet, ready for anyone near the robot."),
    dict(key="floor", src="r16", sec="New in the lab", tag="", title="Cleaning the floor (#369)",
         arm="unit 3: UR12e on a MiR250", t0=5089.2, t1=5100.2, still=5094.0,
         caption="Unit 3 squeegees the floor on a Nilfisk CFM 118EXP "
                 "explosion-proof vacuum's hose, then its camera checks the colour",
         what="Two lanes of the squeegee along the atomizer's front, then the colour check (NFPA 484)."),
    dict(key="waste", src="r16", sec="New in round 16", tag="", title="Waste (#371)", arm="a person, not an arm",
         t0=5310.0, t1=5322.0, still=5320.0,
         caption="A person changes the 118EXP's liner: sealed in place, "
                 "lifted out to the Al-family pail. Powder waste never rides a MiR250",
         what="Vacuum unplugged, head off, the liner sealed in place and carried to its family's pail."),
    dict(key="scaleup", src="r16", sec="New in the lab", tag="", title="Scaling up", arm="",
         t0=4736.0, t1=4747.0, still=4744.0, band_top=618,
         caption="EOS M 400-4: four lasers on one 400 x 400 mm build, two Sentinel-1 antenna brackets after RUAG's "
                 "case study (shape ours)",
         what="The EOS's four lasers on the case study's two brackets, drawn see-through."),
    # ---- the digital twin, round 5 (all simulated), scaled to fit above the band so none of its panels is covered
    dict(key="replay", src="twin", fit="1b1d21", sec="The digital twin, round 5", tag="",
         title="Two simulated years", arm="simulated", t0=556.0, t1=567.5, still=562.0,
         caption="From day 161 the run's own bookings move the 3-D lab: "
                 "trays to the openings, units to the docks (seed 1 of 16)",
         what="Days 161-176 on seed 1 of 16: the Shuttles and units integrated; the replay drives the model."),
    dict(key="compare", src="twin", fit="0d1117", sec="The digital twin, round 5", tag="",
         title="The two labs, like for like", arm="simulated, 16 runs an arm", t0=858.3, t1=869.3, still=866.0,
         caption="Copper: 1.5-2.1x sooner in the automated lab with the "
                 "funnel, 2x or more with BOFN or pKGFN. Aluminium's first: a tie",
         what="Days to each target over 16 seeds an arm, the same policy and stock rule in both labs."),
    dict(key="floorspace", src="twin", fit="e2e3dd", sec="The digital twin, round 5", tag="",
         title="Floor space (#406)", arm="design layouts", t0=1100.0, t1=1111.0, still=1106.0,
         caption="The same 45 tray positions: 3,029 sq ft in the vertical lab against 6,192 laid out flat for robots, "
                 "51 % less floor",
         what="Three layouts side by side, then the Shuttles' 45 trays as bench positions."),
    # ---- the finale
    dict(key="lab", src="r16", sec="", tag="", title="The whole lab at speed: a model year, week by week, "
         "then month by month", arm="", t0=5436.0, t1=5453.4, still=5442.43, band_top=618, band_until=12.38,
         caption="Two 30 ft Kardex Shuttle XP 500s, the floor machines, two UR12e arms on MiR250s and unit 3, "
                 "the floor cleaner",
         what="The counters run to the first year's totals, then the long-form's own 'first year' card."),
]
BAND_TOP = 642                                  # a two-line caption band: its rule is at 644


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)


def stamp(t: float) -> str:
    t = int(round(t))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def head(s: dict) -> str:
    return " · ".join(x for x in (s["sec"], f"{s['tag']}  {s['title']}".strip()) if x)


def dur(s: dict) -> float:
    return sum(b - a for _, a, b in s["clips"]) if s.get("kind") == "real" else s["t1"] - s["t0"]


def cut(s: dict) -> bool:
    """A shot cut from a YouTube source (the real lab's is built from committed excerpts instead)."""
    return s.get("kind") != "real"


FIT_H = 642                                     # a fitted source's height: it sits whole above a 78 px band
FIT_W = round(W * FIT_H / H / 2) * 2            # 1142


# ===================================================================================================== fetch
def hls_segments(playlist: Path) -> list[tuple[float, float, str]]:
    segs, t, dur = [], 0.0, 0.0
    for line in playlist.read_text().splitlines():
        line = line.strip()
        if line.startswith("#EXTINF:"):
            dur = float(line[8:].split(",")[0])
        elif line and not line.startswith("#"):
            segs.append((t, dur, line))
            t += dur
    return segs


def source(src: str, proxy: str) -> list[tuple[float, float, str]]:
    """The source's segment list (its playlist fetched once, through `proxy`)."""
    d = CACHE / src
    d.mkdir(parents=True, exist_ok=True)
    info, playlist = d / "info.json", d / f"itag{SOURCES[src]['itag']}.m3u8"
    if not info.exists():
        r = run(sys.executable, "-m", "yt_dlp", "--proxy", proxy, "--js-runtimes", "node", "-J",
                f"https://www.youtube.com/watch?v={SOURCES[src]['id']}", capture_output=True)
        info.write_bytes(r.stdout)
    if not playlist.exists():
        fmt = next(f for f in json.loads(info.read_text())["formats"] if f["format_id"] == SOURCES[src]["itag"])
        run("curl", "-sfL", "--max-time", "60", "--proxy", proxy, "-o", playlist, fmt["url"])
    return hls_segments(playlist)


def fetch(proxy: str, rate: str = "1M", only: set | None = None):
    """Only the HLS segments that cover each shot (plus PAD), through `proxy`, at most `rate` bytes/s each."""
    for s in SHOTS:
        if (only and s["key"] not in only) or not cut(s):
            continue
        segs = source(s["src"], proxy)
        seg_dir = CACHE / s["src"] / "seg"
        seg_dir.mkdir(exist_ok=True)
        a, b = max(0.0, s["t0"] - PAD), s["t1"] + PAD
        meta = CACHE / f"{s['key']}.json"
        if meta.exists():
            m = json.loads(meta.read_text())
            if m.get("src") == s["src"] and m["start"] <= s["t0"] and m["end"] >= s["t1"]:
                continue                        # the window already covers the shot
        idx = [i for i, (t, d, _) in enumerate(segs) if t + d > a and t < b]
        for i in idx:
            p = seg_dir / f"{i:05d}.ts"
            if not (p.exists() and p.stat().st_size > 1000):
                run("curl", "-sfL", "--retry", "3", "--max-time", "120", "--proxy", proxy, "--limit-rate", rate,
                    "-o", p, segs[i][2])           # -L: the 1080p streams' segments answer with a redirect
                if p.stat().st_size < 1000:
                    raise SystemExit(f"{p}: {p.stat().st_size} bytes; the playlist's URLs may have expired")
        raw = CACHE / f"{s['key']}.ts"
        with open(raw, "wb") as fo:
            for i in idx:
                fo.write((seg_dir / f"{i:05d}.ts").read_bytes())
        # The segments carry the source's own timestamps, a little later than the playlist's sums. Input seeking in a
        # transport stream drops frames up to the next keyframe, so decode from the start and trim on those
        # timestamps; near-lossless, so the cut is frame-exact and the stills lose nothing more. A 1080p source is
        # scaled to 720p here, once.
        first = float(run("ffprobe", "-v", "error", "-show_entries", "format=start_time", "-of", "csv=p=0", raw,
                          capture_output=True, text=True).stdout)
        off = first - segs[idx[0]][0]
        vf = f"trim=start={a + off:.4f}:end={b + off:.4f},setpts=PTS-STARTPTS"
        if tuple(SOURCES[s["src"]]["size"]) != (W, H):
            vf += f",scale={W}:{H}:flags=lanczos"
        win = CACHE / f"{s['key']}.mkv"
        run("ffmpeg", "-v", "error", "-y", "-copyts", "-i", raw, "-vf", vf, "-an", "-c:v", "libx264",
            "-crf", "8", "-preset", "veryfast", "-threads", "2", win)
        meta.write_text(json.dumps({"src": s["src"], "start": a, "end": b, "segments": [idx[0], idx[-1]]}))
        raw.unlink()
        print(f"{s['key']}: {s['src']} {a:.2f}-{b:.2f} s, segments {idx[0]}-{idx[-1]}", flush=True)


def window(s: dict) -> tuple[Path, float]:
    p = CACHE / f"{s['key']}.mkv"
    if not p.exists():
        raise SystemExit(f"{p} missing: run `python3 highlight.py fetch` first")
    m = json.loads((CACHE / f"{s['key']}.json").read_text())
    if not (m["start"] <= s["t0"] + 1e-6 and s["t1"] <= m["end"] + 0.05):
        raise SystemExit(f"{s['key']}: the window {m['start']:.2f}-{m['end']:.2f} doesn't cover the shot; fetch again")
    return p, m["start"]


# ===================================================================================================== choosing
def sheets(only: set | None = None, fps: float = 1.0, cols: int = 10):
    """A contact sheet of each shot's whole window (1 fps), every frame stamped with its source time, outside red."""
    import numpy as np
    out = CACHE / "sheets"
    out.mkdir(exist_ok=True)
    tw, th = 240, 135
    for s in SHOTS:
        if (only and s["key"] not in only) or not cut(s):
            continue
        src, start = window(s)
        r = run("ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={fps}:round=down,scale={tw}:{th}", "-f", "rawvideo",
                "-pix_fmt", "rgb24", "-", capture_output=True)
        fr = np.frombuffer(r.stdout, np.uint8).reshape(-1, th, tw, 3)
        rows = (len(fr) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 4), rows * (th + 18)), (255, 255, 255))
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(fr):
            x, y = (i % cols) * (tw + 4), (i // cols) * (th + 18)
            sheet.paste(Image.fromarray(f), (x, y))
            t = start + i / fps
            inside = s["t0"] - 0.5 / fps <= t <= s["t1"] + 0.5 / fps
            d.text((x + 2, y + th + 1), f"{t:.1f}" + ("" if inside else " (out)"), fill=(0, 0, 0) if inside
                   else (190, 0, 0), font=L.font(13))
        sheet.save(out / f"{s['key']}.jpg", quality=78)
        print(out / f"{s['key']}.jpg")


# ===================================================================================================== build
def bandscan():
    """The rows where the long-form's caption band starts in each of its shots (its full-width navy rule), at 6 fps."""
    import numpy as np
    for s in SHOTS:
        if not cut(s) or s.get("fit"):          # the real lab's band is ours alone; a fitted shot's sits below it
            continue
        src, start = window(s)
        d = min(s["t1"] - s["t0"], s.get("band_until", 1e9))
        r = run("ffmpeg", "-v", "error", "-ss", f"{s['t0'] - start:.3f}", "-i", src, "-t", f"{d:.3f}", "-vf",
                "fps=6,crop=1280:200:0:520", "-f", "rawvideo", "-pix_fmt", "rgb24", "-", capture_output=True)
        fr = np.frombuffer(r.stdout, np.uint8).reshape(-1, 200, W, 3).astype(int)
        tops = []
        for f in fr:
            rows = [y for y in range(200) if (f[y, :, 2] - f[y, :, 0]).mean() > 60 and f[y, :, 2].mean() > 110]
            tops.append(520 + rows[0] if rows else None)
        seen = sorted({t for t in tops if t})
        print(f"{s['key']}: rule at {seen}; band_top {s.get('band_top', BAND_TOP)}"
              f"{'  TOO LOW' if seen and min(seen) < s.get('band_top', BAND_TOP) + 2 else ''}")


def band(s: dict) -> Image.Image:
    """The long-form's caption band (light, under a navy rule): the section and shot on top, the instruments below."""
    top = s.get("band_top", BAND_TOP)
    im = Image.new("RGB", (W, H - top), (244, 245, 247))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 1), fill=L.BLUE)
    x, w = 28, W - 56
    fh, fa = L.font(22, bold=True), L.font(18)
    size = 22
    while True:
        fc = L.font(size)
        lines = L.wrap(d, s["caption"], fc, w)
        if len(lines) == 1 or size <= 18 or (H - top) > 90:
            break
        size -= 1
    rows = 1 + len(lines)
    line_h = int(fh.size * 1.32)
    y = 2 + ((H - top - 2) - rows * line_h) // 2 + 2
    d.text((x, y), head(s), font=fh, fill=L.BLUE)
    if s.get("arm"):
        d.text((x + w - d.textlength(s["arm"], font=fa), y + 3), s["arm"], font=fa, fill=L.GREY)
    for ln in lines:
        y += line_h
        d.text((x, y), ln, font=fc, fill=L.INK)
    return im


def frame(src: Path, t: float) -> Image.Image:
    r = run("ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-f", "image2pipe",
            "-vcodec", "png", "-", capture_output=True)
    from io import BytesIO
    return Image.open(BytesIO(r.stdout)).convert("RGB")


def x264(crf: int, preset: str) -> list[str]:
    return ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-threads", os.environ.get("FFMPEG_THREADS", "2")]


def part_card(png: Path, seconds: float, dst: Path):
    run("ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", FPS, "-i", png, "-t", f"{seconds:.3f}",
        *x264(12, "veryfast"), dst)


def part_shot(s: dict, tmp: Path) -> Path:
    src, start = window(s)
    bp = tmp / f"band_{s['key']}.png"
    band(s).save(bp)
    dur = s["t1"] - s["t0"]
    until = s.get("band_until", dur + 1)
    dst = tmp / f"shot_{s['key']}.mp4"
    fit = (f",scale={FIT_W}:{FIT_H}:flags=lanczos,pad={W}:{H}:{(W - FIT_W) // 2}:0:color=0x{s['fit']}"
           if s.get("fit") else "")
    run("ffmpeg", "-v", "error", "-y", "-ss", f"{s['t0'] - start:.3f}", "-i", src, "-i", bp, "-filter_complex",
        f"[0:v]fps={FPS}{fit},format=rgb24[v];[v][1:v]overlay=0:{s.get('band_top', BAND_TOP)}:"
        f"enable='lt(t,{until:.3f})',format=yuv420p[o]", "-map", "[o]", "-t", f"{dur:.3f}",
        *x264(12, "veryfast"), dst)
    return dst


def fitted(s: dict, im: Image.Image) -> Image.Image:
    """A fitted source's frame as the cut shows it: whole, scaled to FIT_H, centred on its own background."""
    if not s.get("fit"):
        return im
    bg = Image.new("RGB", (W, H), tuple(int(s["fit"][i:i + 2], 16) for i in (0, 2, 4)))
    bg.paste(im.resize((FIT_W, FIT_H), Image.LANCZOS), ((W - FIT_W) // 2, 0))
    return bg


REAL_BG = (28, 30, 34)
REAL_TOP, REAL_H = 46, 560                      # the excerpts and the photo: their top and height


def real_background(s: dict) -> tuple[Image.Image, tuple[int, int, int]]:
    """The real lab's frame without its footage: the photo, the two badges and the band; and where the footage goes."""
    im = Image.new("RGB", (W, H), REAL_BG)
    d = ImageDraw.Draw(im)
    vw = round(406 / 720 * REAL_H / 2) * 2      # the excerpts are 406 x 720, upright
    vx = 40
    ph = Image.open(HERE / s["photo"]).convert("RGB")
    pw = round(ph.width / ph.height * REAL_H)
    px = W - 40 - pw
    im.paste(ph.resize((pw, REAL_H), Image.LANCZOS), (px, REAL_TOP))
    fb = L.font(16, bold=True)
    for x, text in zip((vx, px), s["badges"]):
        tw = d.textlength(text, font=fb)
        d.rectangle((x, REAL_TOP - 30, x + tw + 16, REAL_TOP - 6), fill=(178, 34, 34))
        d.text((x + 8, REAL_TOP - 28), text, font=fb, fill=(255, 255, 255))
    im.paste(band(s), (0, s.get("band_top", BAND_TOP)))
    return im, (vx, vw, REAL_H)


def part_real(s: dict, tmp: Path) -> Path:
    bg, (vx, vw, vh) = real_background(s)
    bp = tmp / f"bg_{s['key']}.png"
    bg.save(bp)
    inputs, chain = ["-loop", "1", "-framerate", str(FPS), "-i", bp], []
    for i, (f, a, b) in enumerate(s["clips"]):
        inputs += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", HERE / f]
        chain.append(f"[{i + 1}:v]fps={FPS},scale={vw}:{vh}:flags=lanczos,setsar=1,setpts=PTS-STARTPTS[c{i}]")
    n = len(s["clips"])
    chain.append("".join(f"[c{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]")
    chain.append(f"[0:v][v]overlay={vx}:{REAL_TOP}:shortest=1,format=yuv420p[o]")
    dst = tmp / f"shot_{s['key']}.mp4"
    run("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[o]",
        "-t", f"{dur(s):.3f}", *x264(12, "veryfast"), dst)
    return dst


def cards() -> tuple[Image.Image, Image.Image]:
    title = L.card_image("The vertical cloud lab, as of 28 November 2026",
                         "The alloy route, what's new, and the digital twin",
                         ["Seven shots of the alloy route from round 16's long-form, one of the lab's own atomizer, "
                          "six of what the lab model gained since round 15, three from the digital twin's round 5, "
                          "then the whole lab at speed.",
                          "Apart from the real atomizer, a 3-D animation of a design study and a simulated benchmark, "
                          "not footage of a working lab."])
    end = L.card_image("The full videos", "Where every shot comes from",
                       [f"The lab, start to finish (round 16, 1:31:05): youtu.be/{SOURCES['r16']['id']}",
                        f"The twin's two years (round 5, 19:54): youtu.be/{SOURCES['twin']['id']}",
                        "Code and notes: github.com/vertical-cloud-lab/byu-vcl (folder vertical-lab/, PRs #318, "
                        "#390, #405, #428); the atomizer's real runs: vertical-cloud-lab/digital-alloy-lab.",
                        "The twin's figures are simulated: synthetic truths, simulated instruments, assumed "
                        "capacities and prices. Its round 6 is running."])
    return title, end


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stills").mkdir(exist_ok=True)
    tmp = CACHE / "build"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)

    title, end = cards()
    title.save(tmp / "title.png")
    end.save(tmp / "end.png")
    parts = [(tmp / "title.mp4", TITLE_S)]
    part_card(tmp / "title.png", TITLE_S, parts[0][0])
    for s in SHOTS:
        parts.append((part_shot(s, tmp) if cut(s) else part_real(s, tmp), dur(s)))
        print(f"  {s['key']}: {dur(s):.2f} s", flush=True)
    parts.append((tmp / "end.mp4", END_S))
    part_card(tmp / "end.png", END_S, parts[-1][0])

    # dissolves between the parts: each part starts XFADE before the previous one ends
    starts, t = [], 0.0
    for i, (_, d) in enumerate(parts):
        starts.append(t)
        t += d - (XFADE if i < len(parts) - 1 else 0)
    total = t
    inputs, chain, prev = [], [], "[0:v]"
    for p, _ in parts:
        inputs += ["-i", p]
    for i in range(1, len(parts)):
        out = f"[x{i}]" if i < len(parts) - 1 else "[out]"
        chain.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={starts[i]:.3f}{out}")
        prev = out
    mp4 = OUT / f"{NAME}.mp4"
    run("ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain), "-map", "[out]",
        *x264(20, "slow"), "-profile:v", "high", "-movflags", "+faststart", mp4)

    # the stills: the same frame as the cut shows it, from the near-lossless window, band and all
    stills = []
    for n, s in enumerate(SHOTS, 1):
        if not cut(s):                          # the real lab's still: its own frame of the built part
            im = frame(tmp / f"shot_{s['key']}.mp4", s["still"])
        else:
            src, start = window(s)
            im = fitted(s, frame(src, s["still"] - start))
            if s["still"] - s["t0"] < s.get("band_until", 1e9):
                im.paste(band(s), (0, s.get("band_top", BAND_TOP)))
        p = OUT / "stills" / f"{n:02d}_{s['key']}.png"
        im.save(p, optimize=True)
        stills.append(p)
    cols = 4
    rows = (len(stills) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480 + (cols + 1) * 8, rows * 270 + (rows + 1) * 8), (246, 247, 249))
    for n, p in enumerate(stills):
        th = Image.open(p).resize((480, 270), Image.LANCZOS)
        sheet.paste(th, (8 + (n % cols) * 488, 8 + (n // cols) * 278))
    sheet.save(OUT / "highlight_sheet.png", optimize=True)

    rec = json.loads((OUT / "highlight.json").read_text()) if (OUT / "highlight.json").exists() else {}
    rec.update({
        "name": NAME, "edition": EDITION, "seconds": round(total, 2), "size": [W, H], "fps": FPS, "built":
        dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {k: {"video": f"https://www.youtube.com/watch?v={v['id']}", "itag": v["itag"],
                        "size": list(v["size"]), "title": v["title"], "length": v["length"], "pr": v["pr"]}
                    for k, v in SOURCES.items()},
        "first_edition": "out/highlight/highlight.json (round 15, https://www.youtube.com/watch?v=lnpVq8JvnJM)",
        "mp4_sha256": sha256(mp4), "mp4_bytes": mp4.stat().st_size,
        "parts": [{"part": "title card", "start_s": 0.0, "seconds": TITLE_S}] + [
            {"part": s["key"], "section": s["sec"], "chapter": f"{s['tag']} {s['title']}".strip(),
             "start_s": round(starts[i + 1], 2), "seconds": round(dur(s), 2), "caption": s["caption"],
             "arm": s["arm"], "what": s["what"], "still": f"stills/{i + 1:02d}_{s['key']}.png",
             **({"src": s["src"], "src_s": [s["t0"], s["t1"]], "src_link": url(s["src"], s["t0"]),
                 "still_src_s": s["still"]} if cut(s) else
                {"src": "committed excerpts", "clips": [list(c) for c in s["clips"]], "photo": s["photo"],
                 "source": "https://youtu.be/2brsz-90seg", "source_s": s["source_s"],
                 "src_link": f"https://youtu.be/2brsz-90seg?t={int(s['source_s'][-1][0])}"})}
            for i, s in enumerate(SHOTS)] + [
            {"part": "end card", "start_s": round(starts[-1], 2), "seconds": END_S}],
    })
    (OUT / "highlight.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    print(f"{mp4}: {total:.1f} s, {mp4.stat().st_size / 1e6:.1f} MB")


# ===================================================================================================== upload
def description(rec: dict, commit: str) -> str:
    r16, tw = SOURCES["r16"], SOURCES["twin"]
    lines = ["Where BYU's vertical cloud lab design study stands on 28 November 2026: seven shots of the alloy route "
             "in 3-D, one of the lab's own atomizer, six of what the lab model gained since round 15, three from the "
             "digital twin's latest finished round, then the whole lab at speed. Each caption names the instruments "
             "or the result in the shot; the sources' own captions and narration are left out.", ""]
    shots = [p for p in rec["parts"] if "caption" in p]
    for i, p in enumerate(shots):
        t = 0.0 if i == 0 else p["start_s"]          # the first chapter takes in the title card
        name = p["chapter"] if not p["section"] else f"{p['section']}: {p['chapter']}"
        lines.append(f"{stamp(t)} {name}")
    lines += ["", "Each shot in its full video:"]
    lines += [f"{p['chapter']}: {p['src_link']}" for p in shots]
    lines += ["",
              f"The lab, start to finish (round 16, {r16['length']}): https://www.youtube.com/watch?v={r16['id']}",
              f"The twin's two simulated years (round 5, {tw['length']}): https://www.youtube.com/watch?v={tw['id']}",
              "",
              "A 3-D animation of a design study at BYU's Vertical Cloud Lab, not footage of a working lab: two Kardex "
              "vertical lift modules hold the instruments on powered trays, and UR12e arms (the UR10e, renamed in "
              "2025) on MiR250 mobile bases work at their openings and at the floor machines. Panels that aren't "
              "measured are badged computed or illustrative.",
              "The digital twin's results are simulated: synthetic truths, simulated instruments, and assumed "
              "capacities, prices, lead times and schedules. Its atomizer rates are design targets, not the lab's "
              "record. Round 5 is its latest finished round (16 runs an arm, like for like); round 6 is running.",
              "",
              "In the real lab (https://github.com/" + DAL + "): the AMAZEMET rePowder logged 10 runs from 2 Oct to "
              "13 Nov 2026, five of aluminium alloys and five of 630 nickel aluminium bronze. The bronze of 27 and 28 "
              "Oct, sieved together, gave 1,015 g under 250 um from 1,938 g charged (DAL PR 286). It hasn't run since "
              "13 Nov, when a run burned the collection cup's seals; the next runs wait on a new cup (DAL #269). The "
              "lab's own powder hasn't been printed yet; AlSi10Mg printed at the University of Utah from bought powder "
              "gave a yield strength of 228 +/- 13 MPa and a UTS of 376 +/- 10 MPa (DAL PR 288).",
              "",
              "An open question, in PR #410 (under review): is the vertical lift worth it? In the twin's own logs the "
              "mobile manipulators are 1-2 % busy, so transport doesn't bind; the gain is floor space (29 % less "
              "for today's 43 instruments, 51 % at the Shuttles' full 45 trays). "
              f"https://github.com/{REPO}/pull/410",
              "",
              f"Cut with https://github.com/{REPO}/blob/{commit}/vertical-lab/highlight.py from the videos as YouTube "
              "serves them.",
              f"Code, notes and sources: https://github.com/{REPO}/tree/{commit}/vertical-lab",
              f"PR: https://github.com/{REPO}/pull/390"]
    return "\n".join(lines)


def upload(privacy: str = "public", notify: bool = True):
    import youtube_upload as Y
    from googleapiclient.http import MediaFileUpload
    sys.path.insert(0, str(HERE.parent))
    from youtube.yt_service import get_youtube_service, with_triggering_link

    rec = json.loads((OUT / "highlight.json").read_text())
    mp4 = OUT / f"{NAME}.mp4"
    digest = sha256(mp4)
    for v in rec.get("youtube", []):
        if v["sha256"] == digest:
            print(f"already up: https://www.youtube.com/watch?v={v['id']}")
            return v["id"]
    commit = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True,
                            cwd=HERE).stdout.strip()
    yt = get_youtube_service("upload")
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    if me != Y.CHANNEL:
        raise SystemExit(f"the token is for channel {me}, not {Y.CHANNEL}")
    title = "The vertical cloud lab, November 2026: the alloy route, what's new, and the digital twin (3-D)"[:100]
    desc = with_triggering_link(description(rec, commit))
    body = {"snippet": {"title": title, "description": desc, "tags": Y.TAGS + ["highlights", "digital twin"],
                        "categoryId": "28", "defaultLanguage": "en"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "embeddable": True}}
    req = yt.videos().insert(part="snippet,status", body=body, notifySubscribers=notify,
                             media_body=MediaFileUpload(str(mp4), mimetype="video/mp4", chunksize=8 << 20,
                                                        resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {status.progress():.0%}", flush=True)
    vid = resp["id"]
    rec.setdefault("youtube", []).append(dict(
        id=vid, url=f"https://www.youtube.com/watch?v={vid}", sha256=digest, privacy=privacy, title=title,
        notified_subscribers=notify, description_commit=commit,
        uploaded=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    (OUT / "highlight.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    (OUT / "youtube_description.txt").write_text(desc + "\n")
    print(f"https://www.youtube.com/watch?v={vid}")
    return vid


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["fetch", "sheets", "build", "upload", "bands", "bandscan", "cards"])
    ap.add_argument("keys", nargs="*", help="only these shots (fetch, sheets)")
    ap.add_argument("--proxy", default="socks5h://127.0.0.1:1080")
    ap.add_argument("--rate", default="1M")
    ap.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    ap.add_argument("--notify", action="store_true", help="notify the channel's subscribers (upload)")
    a = ap.parse_args()
    only = set(a.keys) or None
    if a.cmd == "fetch":
        fetch(a.proxy, a.rate, only)
    elif a.cmd == "sheets":
        sheets(only)
    elif a.cmd == "build":
        build()
    elif a.cmd == "bandscan":                    # where the long-form's own band starts, frame by frame
        bandscan()
    elif a.cmd in ("bands", "cards"):            # the caption bands and cards alone, to read them
        (CACHE / "bands").mkdir(parents=True, exist_ok=True)
        if a.cmd == "bands":
            for s in SHOTS:
                band(s).save(CACHE / "bands" / f"{s['key']}.png")
        else:
            for n, im in zip(("title", "end"), cards()):
                im.save(CACHE / "bands" / f"card_{n}.png")
        print(CACHE / "bands")
    else:
        upload(a.privacy, a.notify)

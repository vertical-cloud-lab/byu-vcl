"""A 2:49 highlight of round 15's long-form: one shot from each chapter of the alloy route, then the whole lab at
speed, each under a short caption naming the instruments in it, and one full-resolution still per chapter.

Sterling, 2026-11-25 (PR #318): "Cut a 2 to 3 minute highlight of round 15's long-form: one shot from each chapter of
the alloy route (charge, atomize, sieve and print, powder checks, machining and tensile, sample prep,
characterization), then the whole lab at speed, with short captions naming each instrument. Upload it unlisted, and
commit 8 full-resolution stills, one per chapter, as PNGs on the branch."

    python3 highlight.py fetch     # the long-form's 720p segments that cover the shots, into HIGHLIGHT_CACHE
    python3 highlight.py           # -> out/highlight/vertical_lab_highlight.mp4, the 8 stills, highlight.json
    python3 highlight.py sheet     # out/highlight/sheet.jpg, the 8 stills on one page (for the PR)
    python3 highlight.py upload    # unlisted on the lab's channel; the video id goes into highlight.json

Where the frames come from. Round 15 drew its clips into out/r15/, which is git-ignored and went with that run's
runner (only chapter 2's 720p MP4 was committed), and the 1:28:55 join itself was never committed (too big for git).
So the one copy of round 15's frames is the long-form on YouTube, 79FL6mTFSsI. Its 720p H.264 HLS stream (itag 232,
about 2.5 Mbit/s, 5.333 s segments) is the best YouTube serves, and its segments carry the long-form's own timestamps,
so a shot is cut at the long-form's own times (each shot's start and end are clear of the clips' half-second
dissolves). Only the segments that cover a shot are fetched (39 of 1,001, 21 MB). YouTube refuses to play videos to a
GitHub runner ("Sign in to confirm you're not a bot", CLAUDE.md), so `fetch` goes through a SOCKS tunnel to a lab Pi:

    ssh -o ExitOnForwardFailure=yes -D 127.0.0.1:1080 -N -f "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME"
    HIGHLIGHT_PROXY=socks5://127.0.0.1:1080 python3 highlight.py fetch

The Pi only relays (nothing is installed or written on it), and every request is rate-capped (HIGHLIGHT_RATE, 3M).
Needs yt-dlp (with a JS runtime: node), curl and ffmpeg.

The captions. Each clip's own caption band (one to four lines of detail, cut mid-sentence by a short shot) is covered
by a band of the same style carrying the chapter, the instruments in view and one line of what they are doing; the
title bar, status panel, labels, data panels and REAL FOOTAGE badges are the long-form's own. The band is two lines
tall at least, and as tall as the tallest of the clip's own bands in that shot, measured on the frames (its 2 px blue
top rule), so nothing of the old text shows. The stills are the same frames under the same band, composed from the
decoded frame (one encode, not two).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import longform as lf       # the long-form's own card, fonts and colours (1280 x 720, K = 1)

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "highlight"
NAME = "vertical_lab_highlight"
VIDEO = "79FL6mTFSsI"                                  # round 15's long-form, public, 1:28:55, 2026-11-24
ITAG = "232"                                           # 1280 x 720 H.264 HLS, the highest-rate 720p YouTube serves
CACHE = Path(os.environ.get("HIGHLIGHT_CACHE", "/tmp/highlight_hls"))
PROXY = os.environ.get("HIGHLIGHT_PROXY", "")          # e.g. socks5://127.0.0.1:1080, a tunnel through a lab Pi
RATE = os.environ.get("HIGHLIGHT_RATE", "3M")          # curl --limit-rate: the Pi is on the lab's Wi-Fi
W, H, FPS = 1280, 720, 30
FADE = 0.25                                            # a dip through black between shots, each side
MIN_BAND = 77                                          # px: two lines of caption, as tall as a two-line clip band
CARD_S, END_S = 5.5, 6.0
PAPER = (246, 247, 249)                                # the long-form's band and card background
X264 = ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", str(FPS)]
LONGFORM = f"https://www.youtube.com/watch?v={VIDEO}"
REPO = "vertical-cloud-lab/byu-vcl"

# One shot per chapter, in the long-form's own seconds (out/longform.json at 4f9ec11 has each clip's start). `names` is
# what is in view; `what` is one line of what it is doing, from the clip's own captions and notes. `still` is the frame
# kept as the chapter's PNG. The finale is two pieces: the lab at speed, week by week and month by month, then the
# first year's card (which carries its own text, so no band over it).
SHOTS = [
    dict(key="charge", tag="1/7  Charge", t0=1166.10, t1=1183.40, still=1176.0,
         chapter="Alloy route 1/7: the charge cups, machined, dosed, weighed and pressed under vacuum",
         names="Multi-doser (chain carousel v5) over an A&D HR-202i · Specac Atlas Autotouch vacuum press",
         what="Tray B at the opening: the arm brings each Al cup to the doser, dosed with Si by weight (shown faster)"),
    dict(key="atomize", tag="2/7  Atomize", t0=1693.70, t1=1710.30, still=1702.0,
         chapter="Alloy route 2/7: melt and atomize in the rePowder",
         names="AMAZEMET rePowder ultrasonic atomizer · both MiR250 + UR12e units steering its plate",
         what="The melt stream sprays off the vibrating plate as powder; the lab's own bronze run beside the model"),
    dict(key="sieve_print", tag="3/7  Sieve and print", t0=2830.20, t1=2847.40, still=2846.0,
         chapter="Alloy route 3/7: sieve and print",
         names="Retsch AS 200 sieve shaker",
         what="The arm clamps the stack and the shaker sorts the powder; the 20–63 µm cut feeds the Aconity MIDI"),
    dict(key="powder", tag="4/7  Powder checks", t0=3194.60, t1=3211.90, still=3207.0,
         chapter="Alloy route 4/7: the powder, checked",
         names="Malvern Mastersizer 3000 + Aero S, laser diffraction, in cutaway",
         what="Size distribution: the lab's own Al 4047 powder counted by SEM; the laser result is computed"),
    dict(key="tensile", tag="5/7  Machining and tensile", t0=3621.00, t1=3638.40, still=3635.0,
         chapter="Alloy route 5/7: depowder, cut, heat treat, tensile at room and elevated temperature",
         names="Instron 68FM-100 with a 3119-608 environmental chamber",
         what="A heat-treated bar, cut from the build on the wire EDM, pulled at 200 °C (the curve is illustrative)"),
    dict(key="prep", tag="6/7  Sample prep", t0=3862.50, t1=3879.75, still=3868.0,
         chapter="Alloy route 6/7: sample prep: section, mount, grind and polish",
         names="LECO PX500 grinder/polisher · a magazine of pre-loaded discs (ours)",
         what="The arm sets the 320-grit disc on the magnetic platen; the head's pistons press the mounts down"),
    dict(key="characterize", tag="7/7  Characterization", t0=4015.00, t1=4032.60, still=4023.0,
         chapter="Alloy route 7/7: characterizing the build",
         names="Hitachi TM4000PlusII SEM · Oxford AZtecOne EDS",
         what="BSE image and EDS maps of the polished section: illustrative; the inset is the lab's own powder"),
    dict(key="whole_lab", tag="The whole lab at speed", t0=5288.75, t1=5318.45, still=5316.0,
         chapter="The whole lab at speed: an hour, a day, a week, a month",
         names="Both Kardex Shuttles, the floor machines and the arms, a year sped up",
         what="From the lab's schedule model, not measurements: alloys atomized, printed and fully tested",
         more=[dict(t0=5319.60, t1=5326.60, band=False)]),
]


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)


# ---------------------------------------------------------------------------------------------------------- fetch
def fetch():
    """The long-form's HLS playlist (itag 232) through the proxy, then only the segments that cover the shots."""
    if not PROXY:
        print("HIGHLIGHT_PROXY is not set: YouTube refuses runners, so this will likely fail (see the docstring)")
    CACHE.mkdir(parents=True, exist_ok=True)
    proxy = ["--proxy", PROXY] if PROXY else []
    info = subprocess.run(["yt-dlp", *proxy, "--js-runtimes", "node", "-j", LONGFORM], check=True,
                          capture_output=True, text=True).stdout
    fmt = next(f for f in json.loads(info)["formats"] if f["format_id"] == ITAG)
    curl = ["curl", "-s", "--fail", "--retry", "3", "--max-time", "120", "--limit-rate", RATE]
    if PROXY:
        curl += ["--socks5-hostname", PROXY.split("://", 1)[-1]]
    run(*curl, "-o", CACHE / "playlist.m3u8", fmt["url"])
    segs = playlist()
    need = sorted({i for i, s, d, _ in segs for a, b in windows() if s < b + 0.5 and s + d > a - 0.5})
    for i in need:
        p = CACHE / f"seg_{i:04d}.ts"
        if not (p.exists() and p.stat().st_size > 1000):
            run(*curl, "-o", p, segs[i][3])
    mb = sum((CACHE / f"seg_{i:04d}.ts").stat().st_size for i in need) / 1e6
    print(f"{len(need)} of {len(segs)} segments, {mb:.1f} MB in {CACHE}")


def playlist():
    """[(index, start s, duration s, url)] from the cached media playlist."""
    segs, t, dur = [], 0.0, None
    for line in (CACHE / "playlist.m3u8").read_text().splitlines():
        if line.startswith("#EXTINF:"):
            dur = float(line[8:].split(",")[0])
        elif line and not line.startswith("#"):
            segs.append((len(segs), t, dur, line))
            t += dur
    return segs


def windows():
    for s in SHOTS:
        yield s["t0"], s["t1"]
        for m in s.get("more", []):
            yield m["t0"], m["t1"]


def source(t0: float, t1: float, tmp: Path) -> tuple[Path, float]:
    """The cached segments that cover [t0, t1], joined (MPEG-TS joins by concatenation); returns the file and the
    long-form time of its first frame. ffmpeg starts a file's clock at 0, so a frame at time u is long-form s0 + u."""
    use = [(i, s) for i, s, d, _ in playlist() if s < t1 and s + d > t0]
    missing = [i for i, _ in use if not (CACHE / f"seg_{i:04d}.ts").exists()]
    if missing:
        raise SystemExit(f"segments {missing} are not in {CACHE}: run `python3 highlight.py fetch` first")
    dst = tmp / f"src_{t0:.2f}.ts"
    with open(dst, "wb") as fo:
        for i, _ in use:
            fo.write((CACHE / f"seg_{i:04d}.ts").read_bytes())
    return dst, use[0][1]


def frames(src: Path, start: float, seconds: float, step: float) -> list[np.ndarray]:
    """Frames every `step` s over [start, start + seconds) of `src`, as RGB arrays."""
    n = max(1, int(seconds / step))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf",
                          f"trim=start={start:.4f}:duration={seconds:.4f},setpts=PTS-STARTPTS,fps={1 / step:.6f}",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         check=True, capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8)
    return [f for f in a.reshape(-1, H, W, 3)]


def band_top(img: np.ndarray) -> int | None:
    """The top of the clip's own caption band: its 2 px blue rule (about RGB 30, 60, 130) across the whole width, with
    the band's pale paper under it. None if the frame has no band (a full-frame card)."""
    a = img[540:].astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    rule = ((b > r + 40) & (b > g + 15) & (b < 190)).mean(axis=1) > 0.95
    for y in np.flatnonzero(rule):
        below = a[y + 3:y + 9]
        if len(below) and (below.mean(axis=2) > 225).mean() > 0.6:
            return 540 + int(y)
    return None


# ------------------------------------------------------------------------------------------------------- drawing
def band_png(shot: dict, top: int) -> Image.Image:
    """A band from `top` down: the chapter in a blue tab, the instruments in bold, one line of what they do."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, top, W, H), fill=PAPER + (255,))
    d.rectangle((0, top, W, top + 2), fill=lf.BLUE + (255,))
    ft, fn, fw = lf.font(19, bold=True), lf.font(23, bold=True), lf.font(18)
    x0, pad = 22, 14
    tab_w = int(d.textlength(shot["tag"], font=ft)) + 2 * pad
    room = W - x0 - tab_w - 18 - 22
    names, what = fit(d, shot["names"], fn, room, 23, True), fit(d, shot["what"], fw, room, 18, False)
    h_text = names.size + 9 + what.size
    y = top + 2 + (H - top - 2 - h_text) // 2
    d.rounded_rectangle((x0, y - 3, x0 + tab_w, y + names.size + 7), radius=6, fill=lf.BLUE + (255,))
    d.text((x0 + pad, y + 1), shot["tag"], font=ft, fill=(255, 255, 255, 255))
    xt = x0 + tab_w + 18
    d.text((xt, y), shot["names"], font=names, fill=lf.INK + (255,))
    d.text((xt, y + names.size + 9), shot["what"], font=what, fill=lf.GREY + (255,))
    return im


def fit(d: ImageDraw.ImageDraw, text: str, f, room: int, size: int, bold: bool):
    """The font at `size`, shrunk a point at a time until `text` fits on one line in `room` px."""
    while d.textlength(text, font=f) > room and size > 14:
        size -= 1
        f = lf.font(size, bold=bold)
    if d.textlength(text, font=f) > room:
        raise SystemExit(f"caption too long for one line: {text!r}")
    return f


def card(over: str, title: str, lines: list[str], foot: str | None = None) -> Image.Image:
    return lf.card_image(over, title, lines, foot)


# -------------------------------------------------------------------------------------------------------- pieces
def encode_piece(src: Path, start: float, seconds: float, overlay: Path | None, dst: Path):
    """[start, start + seconds) of `src` at 30 fps, under `overlay`, dipping through black at both ends."""
    fades = f"fade=t=in:st=0:d={FADE},fade=t=out:st={seconds - FADE:.4f}:d={FADE}"
    cut = f"trim=start={start:.4f}:duration={seconds:.4f},setpts=PTS-STARTPTS,fps={FPS}"
    if overlay:
        graph = f"[0:v]{cut}[v];[v][1:v]overlay=0:0,{fades},format=yuv420p[o]"
        run("ffmpeg", "-v", "error", "-i", src, "-i", overlay, "-filter_complex", graph, "-map", "[o]", "-an",
            *X264, "-crf", "10", "-preset", "veryfast", "-y", dst)
    else:
        run("ffmpeg", "-v", "error", "-i", src, "-vf", f"{cut},{fades},format=yuv420p", "-an",
            *X264, "-crf", "10", "-preset", "veryfast", "-y", dst)


def encode_card(img: Image.Image, seconds: float, dst: Path, tmp: Path):
    p = tmp / f"{dst.stem}.png"
    img.convert("RGB").save(p)
    run("ffmpeg", "-v", "error", "-loop", "1", "-framerate", FPS, "-t", f"{seconds:.3f}", "-i", p, "-vf",
        f"fade=t=in:st=0:d={FADE},fade=t=out:st={seconds - FADE:.4f}:d={FADE},format=yuv420p",
        *X264, "-crf", "10", "-preset", "veryfast", "-y", dst)


def stamp(t: float) -> str:
    m, s = divmod(int(t), 60)
    return f"{m}:{s:02d}" if m < 60 else f"{m // 60}:{m % 60:02d}:{s:02d}"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="highlight_"))
    parts, record, t = [], [], 0.0
    title = card("The vertical cloud lab, round 15: highlights", "The alloy route in under three minutes",
                 ["One shot from each chapter, from dosing the charge cups to characterizing the printed build, then "
                  "the whole lab at speed. Each caption names the instruments in view.",
                  "Cut from the 1:28:55 long-form, youtu.be/" + VIDEO + ": a 3-D animation of a lab that isn't built "
                  "yet, from the makers' published figures and our own designs. Real footage and data are badged."])
    parts.append(tmp / "00_title.mp4")
    encode_card(title, CARD_S, parts[-1], tmp)
    t += CARD_S
    for n, shot in enumerate(SHOTS, 1):
        src, s0 = source(shot["t0"], shot["t1"], tmp)
        dur = shot["t1"] - shot["t0"]
        tops = [band_top(f) for f in frames(src, shot["t0"] - s0, dur, 0.25)]
        found = [y for y in tops if y is not None]
        if len(found) < 0.8 * len(tops):
            raise SystemExit(f"{shot['key']}: the clip's caption band was found in {len(found)} of {len(tops)} frames")
        top = min(min(found) - 1, H - MIN_BAND)
        band = band_png(shot, top)
        bp = tmp / f"band_{n}.png"
        band.save(bp)
        start = t if n > 1 else 0.0                  # chapter 1 starts at 0:00, with the title card (YouTube: >= 10 s)
        parts.append(tmp / f"{n:02d}_{shot['key']}.mp4")
        encode_piece(src, shot["t0"] - s0, dur, bp, parts[-1])
        t += dur
        pieces = [dict(t0=shot["t0"], t1=shot["t1"], band_top=top)]
        for m, more in enumerate(shot.get("more", []), 1):
            msrc, ms0 = source(more["t0"], more["t1"], tmp)
            mdur = more["t1"] - more["t0"]
            parts.append(tmp / f"{n:02d}_{shot['key']}_{m}.mp4")
            encode_piece(msrc, more["t0"] - ms0, mdur, bp if more.get("band", True) else None, parts[-1])
            t += mdur
            pieces.append(dict(t0=more["t0"], t1=more["t1"], band_top=top if more.get("band", True) else None))
        # the still: the decoded frame under the same band, saved once as PNG
        f = frames(src, shot["still"] - s0, 1 / FPS, 1 / FPS)[0]
        still = Image.fromarray(f).convert("RGBA")
        still.alpha_composite(band)
        sp = OUT / f"{n:02d}_{shot['key']}.png"
        still.convert("RGB").save(sp, optimize=True)
        record.append(dict(n=n, key=shot["key"], tag=shot["tag"].replace("  ", " "), names=shot["names"],
                           what=shot["what"], chapter=shot["chapter"], starts_s=round(start, 2),
                           longform=[dict(t0=p["t0"], t1=p["t1"], at=stamp(p["t0"]),
                                          link=f"https://youtu.be/{VIDEO}?t={int(p['t0'])}", band_top_px=p["band_top"])
                                     for p in pieces],
                           still=str(sp.relative_to(HERE)), still_longform_s=shot["still"]))
        print(f"{n} {shot['key']:13s} {dur:5.1f} s from {stamp(shot['t0'])}, band from y={top}, {sp.name}", flush=True)
    end = card("The full version", "1:28:55, 67 chapters, narrated: youtu.be/" + VIDEO,
               ["Every station, the turnaround of the atomizer, the services, safety, upkeep, the floor and the waste, "
                "and the way from one alloy a day to ten.",
                "Code, notes and every source: github.com/vertical-cloud-lab/byu-vcl, PR #318 (folder vertical-lab/). "
                "The docks, fixtures and cells are our designs; the year's counts are a model, not measurements."])
    parts.append(tmp / "99_end.mp4")
    encode_card(end, END_S, parts[-1], tmp)
    t += END_S
    # one encode of the whole cut from the near-lossless pieces
    lst = tmp / "parts.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    dst = OUT / f"{NAME}.mp4"
    run("ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, *X264, "-crf",
        os.environ.get("HIGHLIGHT_CRF", "20"), "-preset", "slow", "-g", str(2 * FPS), "-movflags", "+faststart",
        "-an", "-y", dst)
    secs = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(dst)], check=True, capture_output=True, text=True).stdout)
    old = load()
    rec = dict(name=NAME, seconds=round(secs, 2), size=[W, H], fps=FPS, built=dt.datetime.now(dt.timezone.utc)
               .strftime("%Y-%m-%dT%H:%M:%SZ"), mp4=str(dst.relative_to(HERE)), sha256=sha(dst),
               mb=round(dst.stat().st_size / 1e6, 1),
               source=dict(longform=LONGFORM, itag=ITAG, note="YouTube's 720p H.264 HLS copy of round 15's long-form; "
                           "round 15's own renders (out/r15/) were not kept"),
               shots=record, youtube=old.get("youtube"))
    if rec["youtube"] and rec["youtube"].get("sha256") != rec["sha256"]:
        rec["youtube"]["superseded_by_rebuild"] = True
    (OUT / "highlight.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    shutil.rmtree(tmp)
    print(f"{dst.relative_to(HERE)}: {secs:.1f} s ({stamp(secs)}), {rec['mb']} MB")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load() -> dict:
    p = OUT / "highlight.json"
    return json.loads(p.read_text()) if p.exists() else {}


def sheet():
    """The 8 stills, 2 x 4 at 640 x 360, for the PR description."""
    rec = load()
    im = Image.new("RGB", (2 * 640, 4 * 360), "white")
    for k, s in enumerate(rec["shots"]):
        im.paste(Image.open(HERE / s["still"]).convert("RGB").resize((640, 360), Image.LANCZOS),
                 ((k % 2) * 640, (k // 2) * 360))
    im.save(OUT / "sheet.jpg", quality=88)
    print(OUT / "sheet.jpg")


# -------------------------------------------------------------------------------------------------------- upload
TITLE = "The vertical cloud lab in under three minutes: the alloy route, chapter by chapter (3-D, round 15)"


def description(rec: dict, branch: str) -> str:
    lines = ["Highlights of the vertical cloud lab's round-15 long-form (1:28:55, 67 chapters, narrated): " + LONGFORM,
             "", "One shot from each chapter of the alloy route, then the whole lab at speed, each under a short "
             "caption naming the instruments in view. A design study of an automated alloy lab at BYU's Vertical Cloud "
             "Lab: two Kardex vertical lift modules hold the instruments on powered trays, and UR12e arms on MiR250 "
             "mobile bases work at their openings and at the floor machines.", "",
             "A 3-D animation, not footage of a working lab: makers' published sizes and photos, our own designs where "
             "nothing exists yet. Real footage and data are badged. Silent; the long-form has the narration.", "",
             "Chapters, each with the shot's place in the long-form"]
    for s in rec["shots"]:
        lf_ = s["longform"][0]
        at = f"in the long-form at {lf_['at']}: {lf_['link']}"
        lines.append(f"{stamp(s['starts_s'])} {s['tag']}: {s['names']} · {at}")
    lines += ["", f"Cut by highlight.py: https://github.com/{REPO}/tree/{branch}/vertical-lab",
              f"The long-form's PR: https://github.com/{REPO}/pull/318"]
    return "\n".join(lines)


def upload(branch: str):
    rec = load()
    if (rec.get("youtube") or {}).get("sha256") == rec["sha256"]:
        print("already uploaded:", rec["youtube"]["url"])
        return
    sys.path.insert(0, str(HERE.parent / "youtube"))
    from yt_service import upload_video
    desc = description(rec, branch)
    vid = upload_video(str(HERE / rec["mp4"]), TITLE, desc, privacy="unlisted",
                       tags=["vertical cloud lab", "self-driving lab", "Kardex", "vertical lift module", "UR12e",
                             "MiR250", "alloy", "atomizer", "AMAZEMET rePowder", "laser powder bed fusion", "BYU"])
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["youtube"] = dict(id=vid, url=f"https://www.youtube.com/watch?v={vid}", privacy="unlisted", title=TITLE,
                          sha256=rec["sha256"], uploaded=now)
    (OUT / "highlight.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    print(rec["youtube"]["url"])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "fetch":
        fetch()
    elif cmd == "build":
        build()
    elif cmd == "sheet":
        sheet()
    elif cmd == "upload":
        upload(sys.argv[2] if len(sys.argv) > 2 else "claude/round15-highlight")
    elif cmd == "description":
        print(description(load(), sys.argv[2] if len(sys.argv) > 2 else "claude/round15-highlight"))
    else:
        raise SystemExit(__doc__)

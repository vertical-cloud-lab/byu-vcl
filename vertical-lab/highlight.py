"""A 2-3 minute highlight of round 15's long-form: one shot from each chapter of the alloy route, then the whole lab
at speed, each under a short caption naming the instruments in the shot.

Sterling, PR #318 (2026-11-25): "Cut a 2 to 3 minute highlight of round 15's long-form: one shot from each chapter of
the alloy route (charge, atomize, sieve and print, powder checks, machining and tensile, sample prep,
characterization), then the whole lab at speed, with short captions naming each instrument. Upload it unlisted, and
commit 8 full-resolution stills, one per chapter, as PNGs on the branch."

Round 15's chapter renders went with its runner (out/r15/ is git-ignored), so the shots are cut from the long-form as
YouTube serves it (https://www.youtube.com/watch?v=79FL6mTFSsI): its 720p HLS stream (itag 232, H.264 at 30 fps, the
highest bitrate YouTube offers for it), fetched only around each shot. YouTube refuses player requests from GitHub's
runners, so `fetch` goes through a lab Pi's network over an SSH SOCKS tunnel, rate-capped for the Pi's Wi-Fi:

    ssh -D 127.0.0.1:1080 -N -f <user>@<pi>                       # any lab Pi this run can reach
    python3 highlight.py fetch --proxy socks5h://127.0.0.1:1080   # the shots' 720p segments, into $HIGHLIGHT_CACHE
    python3 highlight.py build                                     # out/highlight/: the MP4, 8 stills, a sheet
    python3 highlight.py upload                                    # unlisted, on the lab's channel

Each shot keeps the long-form's picture as it was, with its title bar and status panel. Only its caption band (the
sub-step's sentence, which a highlight would cut off mid-step) is covered, by a band in the same style naming the
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

OUT = HERE / "out" / "highlight"
CACHE = Path(os.environ.get("HIGHLIGHT_CACHE", "/tmp/vertical_lab_highlight"))
NAME = "vertical_lab_highlight_r15"
LONGFORM_ID = "79FL6mTFSsI"                     # round 15's long-form, public, 1:28:55
LONGFORM_URL = f"https://www.youtube.com/watch?v={LONGFORM_ID}"
ITAG = "232"                                    # 1280 x 720, H.264, HLS
W, H, FPS = 1280, 720, 30
PAD = 1.5                                       # seconds fetched either side of a shot
XFADE = 0.5                                     # dissolve between parts
TITLE_S, END_S = 5.0, 6.0
REPO = "vertical-cloud-lab/byu-vcl"
ARM = "arm: UR12e on a MiR250"

# t0/t1/still are seconds in the long-form. band_top: 2 px above the highest the long-form's caption band reaches in
# the shot (its navy rule is at 668, 644, 620 or 596 for one to four lines; `python3 highlight.py bandscan` measures
# it), so one band of ours covers it for the whole shot. band_until: shot seconds after which the band comes off (the
# finale's last seconds are its own "first year" card, which has no caption band).
SHOTS = [
    dict(key="charge", short="The charge", tag="1/7", title="The charge", arm=ARM,
         t0=1139.35, t1=1159.4, still=1140.8, band_top=618,
         caption="powder-doser's chain carousel v5 · A&D HR-202i balance · Specac Atlas Autotouch 15T vacuum press",
         what="A 5N Al cup from the rack to the doser's shuttle; module 6 docks, tilts and doses Si onto the balance."),
    dict(key="atomize", short="Melt and atomize", tag="2/7", title="Melt and atomize", arm="arms: two UR12e on MiR250s",
         t0=1682.9, t1=1699.35, still=1697.5, band_top=594,
         caption="AMAZEMET rePowder ultrasonic atomizer, cut open for the pour",
         what="Both arms on the plate's landing stage; the melt pours onto the vibrating plate and atomizes."),
    dict(key="sieve", short="Sieve and print", tag="3/7", title="Sieve and print", arm=ARM,
         t0=2831.0, t1=2849.8, still=2845.6,
         caption="Retsch AS 200 sieve shaker, in a downdraft enclosure",
         what="The arm clamps the lid; the stack sieves, drawn see-through; each fraction tinted, then grey again."),
    dict(key="powder", short="The powder, checked", tag="4/7", title="The powder, checked", arm=ARM,
         t0=3114.0, t1=3134.3, still=3133.6,
         caption="Rigaku MiniFlex benchtop powder XRD, its housing drawn see-through",
         what="The arm loads the zero-background holder; the scan; the pattern (computed, not measured)."),
    dict(key="tensile", short="Depowder, cut, heat treat, test", tag="5/7", title="Depowder, cut, heat treat, test",
         arm=ARM, t0=3575.8, t1=3595.8, still=3592.5, band_top=618,
         caption="Instron 68FM-100 · 3119-608 environmental chamber · AVE 2 video extensometer",
         what="A bar into the lower grip, the chamber cut away, the pull (curve illustrative), broken."),
    dict(key="prep", short="Sample prep", tag="6/7", title="Sample prep", arm=ARM,
         t0=3863.9, t1=3879.75, still=3869.4,
         caption="LECO PX500 grinder-polisher and its magazine of pre-loaded discs",
         what="The arm puts the 320-grit disc on the magnetic platen; the pistons press the mounts down."),
    dict(key="characterize", short="Characterizing the build", tag="7/7", title="Characterizing the build", arm=ARM,
         t0=4006.9, t1=4024.6, still=4023.6,
         caption="Hitachi TM4000PlusII tabletop SEM · Oxford Instruments AZtecOne EDS",
         what="The conductive mount into the SEM's grounded holder cup; pump-down; a BSE image (illustrative)."),
    dict(key="lab", short="The whole lab at speed", tag="",
         title="The whole lab at speed: a model year, week by week, then month by month", arm="",
         t0=5297.6, t1=5323.6, still=5312.6, band_top=618, band_until=20.95,
         caption="Two 30 ft Kardex Shuttle XP 500s with 19 trays, the floor machines and two UR12e arms on MiR250s",
         what="The counters run to the first year's totals, then the long-form's own 'first year' card."),
]
BAND_TOP = 642                                  # a two-line caption band: its rule is at 644


def run(*args, **kw):
    return subprocess.run([str(a) for a in args], check=True, **kw)


def stamp(t: float) -> str:
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def fetch(proxy: str, rate: str = "1M"):
    """Only the HLS segments that cover each shot (plus PAD), through `proxy`, at most `rate` bytes/s each."""
    CACHE.mkdir(parents=True, exist_ok=True)
    seg_dir = CACHE / "seg"
    seg_dir.mkdir(exist_ok=True)
    info = CACHE / "info.json"
    if not info.exists():
        r = run(sys.executable, "-m", "yt_dlp", "--proxy", proxy, "--js-runtimes", "node", "-J", LONGFORM_URL,
                capture_output=True)
        info.write_bytes(r.stdout)
    fmt = next(f for f in json.loads(info.read_text())["formats"] if f["format_id"] == ITAG)
    playlist = CACHE / f"itag{ITAG}.m3u8"
    if not playlist.exists():
        run("curl", "-sf", "--max-time", "60", "--proxy", proxy, "-o", playlist, fmt["url"])
    segs = hls_segments(playlist)
    for s in SHOTS:
        a, b = s["t0"] - PAD, s["t1"] + PAD
        idx = [i for i, (t, d, _) in enumerate(segs) if t + d > a and t < b]
        for i in idx:
            p = seg_dir / f"{i:05d}.ts"
            if not (p.exists() and p.stat().st_size > 1000):
                run("curl", "-sf", "--retry", "3", "--max-time", "120", "--proxy", proxy, "--limit-rate", rate,
                    "-o", p, segs[i][2])
        raw = CACHE / f"{s['key']}.ts"
        with open(raw, "wb") as fo:
            for i in idx:
                fo.write((seg_dir / f"{i:05d}.ts").read_bytes())
        # The segments carry the long-form's own timestamps, one frame later than the playlist's sums. Input
        # seeking in a transport stream drops frames up to the next keyframe, so decode from the start and trim on
        # those timestamps; near-lossless, so the cut is frame-exact and the stills lose nothing more.
        first = float(run("ffprobe", "-v", "error", "-show_entries", "format=start_time", "-of", "csv=p=0", raw,
                          capture_output=True, text=True).stdout)
        off = first - segs[idx[0]][0]
        win = CACHE / f"{s['key']}.mkv"
        run("ffmpeg", "-v", "error", "-y", "-copyts", "-i", raw, "-vf",
            f"trim=start={a + off:.4f}:end={b + off:.4f},setpts=PTS-STARTPTS", "-an", "-c:v", "libx264",
            "-crf", "8", "-preset", "veryfast", "-threads", "2", win)
        (CACHE / f"{s['key']}.json").write_text(json.dumps({"start": a, "end": b, "segments": [idx[0], idx[-1]]}))
        raw.unlink()
        print(f"{s['key']}: {a:.2f}-{b:.2f} s, segments {idx[0]}-{idx[-1]}", flush=True)


def window(s: dict) -> tuple[Path, float]:
    p = CACHE / f"{s['key']}.mkv"
    if not p.exists():
        raise SystemExit(f"{p} missing: run `python3 highlight.py fetch` first")
    return p, json.loads((CACHE / f"{s['key']}.json").read_text())["start"]


# ===================================================================================================== build
def bandscan():
    """The rows where the long-form's caption band starts in each shot (its full-width navy rule), at 6 fps."""
    import numpy as np
    for s in SHOTS:
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
    """The long-form's caption band (light, under a navy rule), with the chapter on top and the instruments below."""
    top = s.get("band_top", BAND_TOP)
    im = Image.new("RGB", (W, H - top), (244, 245, 247))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 1), fill=L.BLUE)
    x, w = 28, W - 56
    head = f"{s['tag']}  {s['title']}".strip()
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
    d.text((x, y), head, font=fh, fill=L.BLUE)
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
    run("ffmpeg", "-v", "error", "-y", "-ss", f"{s['t0'] - start:.3f}", "-i", src, "-i", bp, "-filter_complex",
        f"[0:v]fps={FPS},format=rgb24[v];[v][1:v]overlay=0:{s.get('band_top', BAND_TOP)}:"
        f"enable='lt(t,{until:.3f})',format=yuv420p[o]", "-map", "[o]", "-t", f"{dur:.3f}",
        *x264(12, "veryfast"), dst)
    return dst


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stills").mkdir(exist_ok=True)
    tmp = CACHE / "build"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)

    title = L.card_image("Highlights of round 15's long-form", "The vertical cloud lab: the alloy route in eight shots",
                         ["One shot from each chapter of the alloy route, from the charge cups to characterizing the "
                          "build, then the whole lab at speed.",
                          "A 3-D animation of a design study, not footage of a working lab."])
    end = L.card_image("The full video", "The vertical cloud lab, start to finish",
                       [f"1:28:55 in 67 chapters, narrated: youtube.com/watch?v={LONGFORM_ID}",
                        "Code, notes and every source: github.com/vertical-cloud-lab/byu-vcl, PR #318 "
                        "(folder vertical-lab/).",
                        "Sizes are the makers' published figures where they exist; each notes file says which of "
                        "the designs are ours and which numbers are assumed."])
    title.save(tmp / "title.png")
    end.save(tmp / "end.png")
    parts = [(tmp / "title.mp4", TITLE_S)]
    part_card(tmp / "title.png", TITLE_S, parts[0][0])
    for s in SHOTS:
        parts.append((part_shot(s, tmp), s["t1"] - s["t0"]))
        print(f"  {s['key']}: {s['t1'] - s['t0']:.2f} s", flush=True)
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
        src, start = window(s)
        im = frame(src, s["still"] - start)
        if s["still"] - s["t0"] < s.get("band_until", 1e9):
            im.paste(band(s), (0, s.get("band_top", BAND_TOP)))
        p = OUT / "stills" / f"{n}_{s['key']}.png"
        im.save(p, optimize=True)
        stills.append(p)
    sheet = Image.new("RGB", (4 * 480 + 5 * 8, 2 * 270 + 3 * 8), (246, 247, 249))
    for n, p in enumerate(stills):
        th = Image.open(p).resize((480, 270), Image.LANCZOS)
        sheet.paste(th, (8 + (n % 4) * 488, 8 + (n // 4) * 278))
    sheet.save(OUT / "highlight_sheet.png", optimize=True)

    rec = json.loads((OUT / "highlight.json").read_text()) if (OUT / "highlight.json").exists() else {}
    rec.update({
        "name": NAME, "seconds": round(total, 2), "size": [W, H], "fps": FPS, "built":
        dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {"video": LONGFORM_URL, "itag": ITAG, "note": "round 15's long-form, cut from YouTube's 720p HLS"},
        "mp4_sha256": sha256(mp4), "mp4_bytes": mp4.stat().st_size,
        "parts": [{"part": "title card", "start_s": 0.0, "seconds": TITLE_S}] + [
            {"part": s["key"], "chapter": f"{s['tag']} {s['title']}".strip(), "short": s["short"],
             "start_s": round(starts[i + 1], 2), "seconds": round(s["t1"] - s["t0"], 2), "longform_s": [s["t0"], s["t1"]],
             "longform_link": f"https://youtu.be/{LONGFORM_ID}?t={int(s['t0'])}", "caption": s["caption"],
             "arm": s["arm"], "what": s["what"], "still": f"stills/{i + 1}_{s['key']}.png",
             "still_longform_s": s["still"]} for i, s in enumerate(SHOTS)] + [
            {"part": "end card", "start_s": round(starts[-1], 2), "seconds": END_S}],
    })
    (OUT / "highlight.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    print(f"{mp4}: {total:.1f} s, {mp4.stat().st_size / 1e6:.1f} MB")


# ===================================================================================================== upload
def description(rec: dict, commit: str) -> str:
    lines = [f"Highlights of the vertical cloud lab's round-15 long-form, {LONGFORM_URL} (1:28:55, 67 chapters): one "
             "shot from each chapter of the alloy route, then the whole lab at speed. Each caption names the "
             "instruments in the shot; the long-form's own captions and narration are left out.", ""]
    shots = [p for p in rec["parts"] if "longform_s" in p]
    for i, p in enumerate(shots):
        t = 0.0 if i == 0 else p["start_s"]          # the first chapter takes in the title card
        lines.append(f"{stamp(t)} {p['short']}: {p['caption']}")
    lines += ["", "Each shot in the full video:"]
    lines += [f"{p['short']}: {p['longform_link']}" for p in shots]
    lines += ["", "A 3-D animation of a design study at BYU's Vertical Cloud Lab, not footage of a working lab: two "
              "Kardex vertical lift modules hold the instruments on powered trays, and UR12e arms (the UR10e, renamed "
              "in 2025) on MiR250 mobile bases work at their openings and at the floor machines. Panels that aren't "
              "measured are badged computed or illustrative.", "",
              f"Cut with https://github.com/{REPO}/blob/{commit}/vertical-lab/highlight.py from the long-form as "
              "YouTube serves it (720p).",
              f"Code, notes and sources: https://github.com/{REPO}/tree/{commit}/vertical-lab",
              f"PR: https://github.com/{REPO}/pull/318"]
    return "\n".join(lines)


def upload(privacy: str = "unlisted"):
    sys.path.insert(0, str(HERE.parent))
    import youtube_upload as Y
    from googleapiclient.http import MediaFileUpload
    from youtube.yt_service import get_youtube_service, with_triggering_link

    rec = json.loads((OUT / "highlight.json").read_text())
    mp4 = OUT / f"{NAME}.mp4"
    digest = sha256(mp4)
    for v in rec.get("youtube", []):
        if v["sha256"] == digest:
            print(f"already up: https://www.youtube.com/watch?v={v['id']}")
            return v["id"]
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                            cwd=HERE).stdout.strip()
    yt = get_youtube_service("upload")
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    if me != Y.CHANNEL:
        raise SystemExit(f"the token is for channel {me}, not {Y.CHANNEL}")
    title = "Vertical cloud lab: the alloy route in eight shots (round 15 highlights, 3-D)"[:100]
    desc = with_triggering_link(description(rec, commit))
    body = {"snippet": {"title": title, "description": desc, "tags": Y.TAGS + ["highlights"], "categoryId": "28",
                        "defaultLanguage": "en"},
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False, "embeddable": True}}
    req = yt.videos().insert(part="snippet,status", body=body, notifySubscribers=False,
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
        notified_subscribers=False,
        description_commit=commit, uploaded=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    (OUT / "highlight.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    (OUT / "youtube_description.txt").write_text(desc + "\n")
    print(f"https://www.youtube.com/watch?v={vid}")
    return vid


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=["fetch", "build", "upload", "bands", "bandscan"])
    ap.add_argument("--proxy", default="socks5h://127.0.0.1:1080")
    ap.add_argument("--rate", default="1M")
    a = ap.parse_args()
    if a.cmd == "fetch":
        fetch(a.proxy, a.rate)
    elif a.cmd == "build":
        build()
    elif a.cmd == "bandscan":                    # where the long-form's own band starts, frame by frame
        bandscan()
    elif a.cmd == "bands":                       # the caption bands alone, to read them
        (CACHE / "bands").mkdir(parents=True, exist_ok=True)
        for s in SHOTS:
            band(s).save(CACHE / "bands" / f"{s['key']}.png")
        print(CACHE / "bands")
    else:
        upload()

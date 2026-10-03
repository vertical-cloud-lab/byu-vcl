"""Build the narrated Al cup and plug tutorial (#248) from narration.py.

    python build.py            # -> out/al_cups_plugs_tutorial.mp4, captions.srt, chapters.txt, contact_sheet.jpg

Needs ffmpeg, edge-tts, pillow, numpy and opencv-python-headless. Inputs:
  - the CAD clips, drawing and render from PR #232: ../cad/... if present, otherwise read from its commit with git
  - assets/: the two photos from #222 (resized, metadata stripped)
  - Gage's lathe Short, z6rwmQW_3Vg.v480.mp4 + .m4a, in $SHORT_DIR (default /tmp/al/clip). YouTube refuses player
    requests from GitHub runners, so fetch it on a stream-cam Pi (CLAUDE.md, "Reading the livestream archive back"):
      ~/.venvs/ytframes/bin/yt-dlp --js-runtimes node --limit-rate 3M -f 231 -o z6rwmQW_3Vg.v480.mp4 <url>
      ~/.venvs/ytframes/bin/yt-dlp --js-runtimes node --limit-rate 3M -f "ba[ext=m4a]" -o z6rwmQW_3Vg.m4a <url>
    (the https DASH format 135 returned 403; 231 is the same 480x854 stream over HLS)

The CAD clips predate the as-made parts, so their out-of-date callouts ("2.5 in", "1 mm", "+ .001 in") are inpainted
and redrawn with the numbers from #222 (FIXES below), and their caption line is cropped off. Captions are drawn into
the frames: the upload token can't add a caption track (that needs youtube.force-ssl).
"""
import concurrent.futures as cf
import hashlib
import os
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from narration import SEGMENTS, SHORT, VOICE

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGE = os.path.dirname(HERE)  # atomizer-charge/
REPO = os.path.dirname(CHARGE)
PR232_COMMIT = "323adba"  # head of PR #232 when this was built
SHORT_DIR = os.environ.get("SHORT_DIR", "/tmp/al/clip")
CACHE = os.environ.get("TUTORIAL_CACHE", "/tmp/al/cache")
OUT = os.path.join(HERE, "out")
NAME = "al_cups_plugs_tutorial"

W, H, FPS, SR = 1280, 720, 30, 44100
TOP, BAND = 64, 624  # title bar is 0-64, caption band 624-720
NAVY, SLATE, LIGHT = (16, 24, 32), (28, 36, 46), (250, 250, 250)
WHITE, MUTED, AMBER, INK = (255, 255, 255), (150, 165, 180), (240, 184, 72), (30, 34, 40)
LEAD, GAP, TAIL = 0.45, 0.35, 0.7  # seconds of silence before, between and after sentences
SHOP_UNDER_VOICE = 0.12  # level of the shop audio under the narration, relative to its normalized level

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_fonts = {}


def font(size, style=""):
    key = (size, style)
    if key not in _fonts:
        name = {"": "DejaVuSans", "b": "DejaVuSans-Bold", "i": "DejaVuSans-Oblique"}[style]
        _fonts[key] = ImageFont.truetype(f"{FONT_DIR}/{name}.ttf", size)
    return _fonts[key]


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd)) + "\n" + r.stderr.decode(errors="replace")[-3000:])
    return r


def charge_file(rel):
    """A file under atomizer-charge/ (PR #232), from the working tree if merged, else from the PR's commit."""
    local = os.path.join(CHARGE, rel)
    if os.path.exists(local):
        return local
    cached = os.path.join(CACHE, "pr232", rel)
    if not os.path.exists(cached):
        os.makedirs(os.path.dirname(cached), exist_ok=True)
        blob = run(["git", "-C", REPO, "show", f"{PR232_COMMIT}:atomizer-charge/{rel}"]).stdout
        open(cached, "wb").write(blob)
    return cached


# ---------------------------------------------------------------- audio

def tts(text):
    """Steffan saying `text`, as mono float32 at SR. Cached by text."""
    os.makedirs(f"{CACHE}/tts", exist_ok=True)
    h = hashlib.sha1(f"{VOICE}|{text}".encode()).hexdigest()[:16]
    mp3, wav = f"{CACHE}/tts/{h}.mp3", f"{CACHE}/tts/{h}.wav"
    if not os.path.exists(wav):
        for attempt in range(4):
            try:
                run(["edge-tts", "--voice", VOICE, "--text", text, "--write-media", mp3])
                break
            except RuntimeError:
                if attempt == 3:
                    raise
        run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav])
    return read_wav(wav)


def read_wav(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a


def short_audio(t0, t1):
    path = f"{CACHE}/short_{t0:.2f}_{t1:.2f}.wav"
    if not os.path.exists(path):
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i",
             f"{SHORT_DIR}/{SHORT}.m4a", "-ac", "1", "-ar", str(SR), path])
    return read_wav(path)


def loud(a):
    """90th percentile of 50 ms RMS: a speech level that ignores the pauses."""
    n = int(0.05 * SR)
    k = len(a) // n
    if k == 0:
        return 1e-6
    rms = np.sqrt((a[:k * n].reshape(k, n) ** 2).mean(axis=1))
    return float(np.percentile(rms, 90)) + 1e-6


def silence(sec):
    return np.zeros(int(round(sec * SR)), dtype=np.float32)


def fit(a, n):
    return a[:n] if len(a) >= n else np.concatenate([a, np.zeros(n - len(a), dtype=np.float32)])


# ---------------------------------------------------------------- text and frames

def wrap(text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if fnt.getlength(trial) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def base(content_bg, title):
    im = Image.new("RGB", (W, H), content_bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, TOP], fill=NAVY)
    d.rectangle([0, BAND, W, H], fill=NAVY)
    if title:
        d.text((36, 15), title, font=font(30, "b"), fill=WHITE)
    tag = "Al cups and plugs · #248"
    d.text((W - 36 - font(18).getlength(tag), 23), tag, font=font(18), fill=MUTED)
    return im


def draw_caption(im, cue):
    if not cue:
        return im
    text, live = cue
    style = "i" if live else ""
    for size in (27, 24, 21):
        lines = wrap(text, font(size, style), 1200)
        if len(lines) * (size + 8) <= 88:
            break
    d = ImageDraw.Draw(im)
    lh = size + 8
    y = BAND + (H - BAND - len(lines) * lh) // 2 + 1
    for line in lines:
        f = font(size, style)
        d.text(((W - f.getlength(line)) / 2, y), line, font=f, fill=AMBER if live else WHITE)
        y += lh
    return im


def paste_fit(im, src, box, bg):
    x0, y0, x1, y1 = box
    s = src.copy()
    s.thumbnail((x1 - x0, y1 - y0), Image.LANCZOS)
    if s.mode == "RGBA":
        flat = Image.new("RGB", s.size, bg)
        flat.paste(s, mask=s.split()[3])
        s = flat
    im.paste(s.convert("RGB"), (x0 + (x1 - x0 - s.width) // 2, y0 + (y1 - y0 - s.height) // 2))
    return s.size


def draw_notes(im, notes, x, y, width, color, size=26):
    d = ImageDraw.Draw(im)
    for note in notes:
        lines = wrap(note, font(size), width - 28)
        d.ellipse([x, y + size // 2 - 4, x + 9, y + size // 2 + 5], fill=AMBER)
        for line in lines:
            d.text((x + 24, y), line, font=font(size), fill=color)
            y += size + 8
        y += 14
    return y


# ---------------------------------------------------------------- CAD clips: fix the callouts

# (frames, approximate box in the 720x410 GIF, text there now, text to draw, style, dark threshold, white box?)
FIXES = {
    "machining_cup": [
        (range(26, 43), (16, 16, 290, 42), "3 of 4  Cut it off at 2.5 in", "3 of 4  Cut it off at 2.75 in", "b", 70,
         False),
        ([58], (498, 112, 645, 132), "1/2 in hole, 1.9 in deep", "1/2 in drill, 2.25 in deep", "", 110, False),
        ([58], (498, 212, 585, 232), "3.2 mm wall", "1/8 in wall", "", 110, False),
    ],
    "machining_plug": [
        (range(30, 37), (16, 52, 205, 70), "close up - this corner is 0.3 mm", "close up - this corner is .015 in",
         "i", 150, False),
        (range(33, 37), (428, 96, 518, 115), "0.3 mm break", ".015 in break", "", 110, True),
        ([68], (296, 56, 424, 80), "cup's hole + .001 in", "cup's hole + .0005 to .0008 in", "", 110, True),
        ([68], (485, 90, 585, 106), "1 mm air hole,", "#60 air hole,", "", 110, False),
        ([68], (485, 186, 656, 204), "0.3 mm break - deburr only,", ".015 in break - deburr only,", "", 110, False),
        ([68], (485, 316, 676, 336), "1.5 mm taper - this end goes in", "15° taper - this end goes in", "", 110,
         False),
    ],
    "fill_and_vent": [
        ([42], (443, 146, 568, 166), "1 mm hole in the lid", "#60 hole in the plug", "", 110, False),
    ],
}
GIF_CROP = 372  # the clip's own caption line sits at y 377-388


def gif_frames(name):
    im = Image.open(charge_file(f"cad/anim/{name}.gif"))
    frames, durs = [], []
    try:
        while True:
            frames.append(im.convert("RGB").copy())
            durs.append(im.info.get("duration", 100) / 1000)
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    for frames_idx, box, old, new, style, thr, white in FIXES.get(name, []):
        for i in frames_idx:
            frames[i] = fix_text(frames[i], box, old, new, style, thr, white)
    return [f.crop((0, 0, f.width, GIF_CROP)) for f in frames], durs


def fix_text(img, box, old, new, style, thr, white):
    a = np.asarray(img).copy()
    x0, y0, x1, y1 = box
    region = a[y0:y1, x0:x1].astype(int).sum(axis=2) / 3
    ys, xs = np.where(region < thr)
    if len(xs) == 0:
        raise RuntimeError(f"no text found for {old!r}")
    bx0, by0, bx1, by1 = x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1
    color = tuple(int(c) for c in np.percentile(a[y0:y1, x0:x1][region < thr], 10, axis=0))
    mask = np.zeros(a.shape[:2], np.uint8)
    mask[y0:y1, x0:x1][region < thr] = 255
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    a = cv2.inpaint(a[:, :, ::-1].copy(), mask, 3, cv2.INPAINT_TELEA)[:, :, ::-1]
    out = Image.fromarray(np.ascontiguousarray(a))
    size = min(range(8, 30), key=lambda s: abs(font(s, style).getlength(old) - (bx1 - bx0)))
    size += style == ""  # the threshold trims the anti-aliased ends, so regular labels measure a size small
    f = font(size, style)
    ox, oy = f.getbbox(old)[:2]
    d = ImageDraw.Draw(out)
    if white:
        nb = f.getbbox(new)
        d.rectangle([bx0 - 3, by0 - 3, bx0 + nb[2] - ox + 3, by1 + 3], fill=(255, 255, 255))
    d.text((bx0 - ox, by0 - oy), new, font=f, fill=color)
    return out


# ---------------------------------------------------------------- the short

def short_frames(t0, dur, size):
    """Frames of the lathe Short from t0 for dur seconds at FPS, scaled to size; holds the last frame past the end."""
    w, h = size
    r = run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", f"{SHORT_DIR}/{SHORT}.v480.mp4",
             "-vf", f"scale={w}:{h}:flags=lanczos,fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    raw = r.stdout
    n = len(raw) // (w * h * 3)
    frames = [Image.frombuffer("RGB", (w, h), raw[i * w * h * 3:(i + 1) * w * h * 3]) for i in range(n)]
    need = int(round(dur * FPS))
    return frames + [frames[-1]] * max(0, need - len(frames))


# ---------------------------------------------------------------- plan: audio, cues, and a frame function per segment

def voice_track(sentences, voices, t=0.0):
    """Lay sentences end to end from t; returns audio, cues [(t0, t1, (caption, live))], end time."""
    parts, cues = [], []
    for (caption, _), v in zip(sentences, voices):
        d = len(v) / SR
        parts.append((t, v))
        cues.append((t, t + d, (caption, False)))
        t += d + GAP
    return parts, cues, t - GAP if sentences else t


def mix(parts, total):
    out = np.zeros(int(round(total * SR)) + SR, dtype=np.float32)
    for t, v in parts:
        i = int(round(t * SR))
        out[i:i + len(v)] += v[:len(out) - i]
    return out[:int(round(total * SR))]


def plan():
    texts = []
    for kind, spec, body in SEGMENTS:
        sents = [s for step in body for s in step] if kind == "gif" else body
        texts += [spoken or caption for caption, spoken in sents]
    with cf.ThreadPoolExecutor(4) as ex:
        voices = dict(zip(texts, ex.map(tts, texts)))
    narration_level = loud(np.concatenate(list(voices.values())))

    segs = []
    for kind, spec, body in SEGMENTS:
        if kind == "gif":
            frames, durs = gif_frames(spec["gif"])
            starts = spec["steps"] + [len(frames)]
            t, parts, cues, timeline = LEAD, [], [], []
            for k, step in enumerate(body):
                idx = list(range(starts[k], starts[k + 1]))
                vs = [voices[sp or c] for c, sp in step]
                p, c, end = voice_track(step, vs, t)
                parts += p
                cues += c
                natural = sum(durs[i] for i in idx)
                step_len = max(natural, end - t + GAP)
                acc = t
                for i in idx:
                    timeline.append((acc, i))
                    acc += durs[i]
                t += step_len
            total = t + TAIL - GAP
            segs.append(dict(kind=kind, spec=spec, total=total, audio=mix(parts, total), cues=cues,
                             frames=frames, timeline=timeline))
        elif kind == "clip":
            t0, t1 = spec["start"], spec["end"]
            a = short_audio(t0, t1)
            a = a * min(6.0, narration_level / loud(a))
            total = t1 - t0 + 0.25
            cues = [(c0 - t0, c1 - t0, (f"“{text}”", True)) for c0, c1, text in spec["captions"]]
            segs.append(dict(kind=kind, spec=spec, total=total, audio=fit(a, int(round(total * SR))), cues=cues))
        else:
            vs = [voices[sp or c] for c, sp in body]
            parts, cues, end = voice_track(body, vs, LEAD)
            total = end + TAIL
            audio = mix(parts, total)
            if kind == "clip_vo":
                shop = short_audio(spec["start"], min(94.3, spec["start"] + total))
                shop = shop * min(6.0, narration_level / loud(shop)) * SHOP_UNDER_VOICE
                audio = audio + fit(shop, len(audio))
            segs.append(dict(kind=kind, spec=spec, total=total, audio=audio, cues=cues))
    return segs


# ---------------------------------------------------------------- render

def static_frame(seg):
    kind, spec = seg["kind"], seg["spec"]
    if kind == "card":
        im = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(im)
        y = 150 if "lines" not in spec else 110
        for line in wrap(spec["title"], font(56, "b"), 1100):
            d.text((90, y), line, font=font(56, "b"), fill=WHITE)
            y += 70
        y += 18
        for line in wrap(spec["sub"], font(30), 1100):
            d.text((90, y), line, font=font(30), fill=(201, 214, 226))
            y += 42
        y += 24
        for line in spec.get("lines", []):
            d.text((90, y), line, font=font(24), fill=MUTED)
            y += 36
        d.text((90, BAND - 52), spec["footer"], font=font(22), fill=MUTED)
        d.line([90, BAND - 70, 400, BAND - 70], fill=AMBER, width=3)
        return im
    if kind == "image":
        bg = LIGHT if spec["bg"] == "light" else SLATE
        im = base(bg, spec["title"])
        path = spec["path"]
        src = Image.open(charge_file(path) if path.startswith("cad/") else os.path.join(CHARGE, path))
        if spec["notes"]:
            paste_fit(im, src, (30, TOP + 12, 790, BAND - 12), bg)
            draw_notes(im, spec["notes"], 830, TOP + 70, 420, INK if bg == LIGHT else WHITE)
        else:
            paste_fit(im, src, (20, TOP + 8, W - 20, BAND - 8), bg)
        return im
    if kind == "slide":
        im = base(SLATE, spec["title"])
        d = ImageDraw.Draw(im)
        if "bullets" in spec:
            y = TOP + 50
            for b in spec["bullets"]:
                for j, line in enumerate(wrap(b, font(30), 1150)):
                    d.text((60 + (0 if j == 0 else 34), y), line, font=font(30), fill=WHITE)
                    y += 40
                y += 22
        else:
            tbl = spec["table"]
            xs, widths = [40, 260, 760], [210, 480, 480]
            y = TOP + 26
            for r, row in enumerate([tbl["head"]] + tbl["rows"]):
                f = font(23, "b") if r == 0 else font(23)
                cells = [wrap(c, f, wd) for c, wd in zip(row, widths)]
                hgt = max(len(c) for c in cells) * 30
                for c, x in zip(cells, xs):
                    yy = y
                    for line in c:
                        color = AMBER if r == 0 else (WHITE if x != 760 else MUTED)
                        d.text((x, yy), line, font=f, fill=color)
                        yy += 30
                y += hgt + 12
                d.line([40, y - 6, W - 40, y - 6], fill=(60, 72, 86), width=1)
        return im
    raise ValueError(kind)


def clip_canvas(spec, live):
    im = base(SLATE, spec["title"])
    d = ImageDraw.Draw(im)
    d.text((480, TOP + 40), spec["credit"], font=font(20), fill=MUTED)
    if live:
        d.text((480, TOP + 72), "Original audio", font=font(20, "b"), fill=AMBER)
    draw_notes(im, spec["notes"], 480, TOP + 130, 740, WHITE, size=30)
    return im


VID_BOX = (96, TOP + 10, 96 + 304, TOP + 10 + 540)


def render(segs, out_mp4, wav_path):
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav_path, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-movflags", "+faststart", "-shortest", out_mp4],
        stdin=subprocess.PIPE)
    for n, seg in enumerate(segs):
        nframes = int(round(seg["total"] * FPS))
        kind, spec = seg["kind"], seg["spec"]
        cache = {}
        if kind in ("clip", "clip_vo"):
            canvas = clip_canvas(spec, kind == "clip")
            vid = short_frames(spec["start"], nframes / FPS, (VID_BOX[2] - VID_BOX[0], VID_BOX[3] - VID_BOX[1]))
        elif kind == "gif":
            canvas = base((252, 252, 252), spec["title"])
            scaled = {}
        else:
            canvas = static_frame(seg)
        for k in range(nframes):
            t = k / FPS
            cue = next((c[2] for c in seg["cues"] if c[0] <= t < c[1] + GAP * 0.8), None)
            if kind in ("card", "image", "slide"):
                key = cue
                if key not in cache:
                    cache[key] = draw_caption(canvas.copy(), cue).tobytes()
                enc.stdin.write(cache[key])
                continue
            im = canvas.copy()
            if kind == "gif":
                i = [fi for ft, fi in seg["timeline"] if ft <= t][-1] if t >= seg["timeline"][0][0] else 0
                if i not in scaled:
                    g = seg["frames"][i]
                    s = min(W / g.width, (BAND - TOP) / g.height)
                    scaled[i] = g.resize((int(g.width * s), int(g.height * s)), Image.LANCZOS)
                g = scaled[i]
                im.paste(g, ((W - g.width) // 2, TOP))
            else:
                im.paste(vid[min(k, len(vid) - 1)], VID_BOX[:2])
            enc.stdin.write(draw_caption(im, cue).tobytes())
        print(f"segment {n:2d} {kind:8s} {seg['total']:6.1f}s", flush=True)
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg encode failed")


def stamp(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    os.makedirs(OUT, exist_ok=True)
    segs = plan()
    # frame-accurate segment starts, so captions and chapters match the video
    starts, t = [], 0.0
    for s in segs:
        s["total"] = int(round(s["total"] * FPS)) / FPS
        s["audio"] = fit(s["audio"], int(round(s["total"] * SR)))
        starts.append(t)
        t += s["total"]
    audio = np.concatenate([s["audio"] for s in segs])
    audio *= min(1.0, 0.95 / (np.abs(audio).max() + 1e-9))
    wav_path = f"{CACHE}/{NAME}.wav"
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1), w.setsampwidth(2), w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())

    mp4 = os.path.join(OUT, f"{NAME}.mp4")
    render(segs, mp4, wav_path)

    with open(os.path.join(OUT, "captions.srt"), "w") as f:
        k = 0
        for s, st in zip(segs, starts):
            for c0, c1, (text, live) in s["cues"]:
                k += 1
                f.write(f"{k}\n{srt_time(st + c0)} --> {srt_time(st + min(c1, s['total']))}\n{text}\n\n")
    chapters = [(st, s["spec"]["chapter"]) for s, st in zip(segs, starts) if "chapter" in s["spec"]]
    with open(os.path.join(OUT, "chapters.txt"), "w") as f:
        f.writelines(f"{stamp(st)} {name}\n" for st, name in chapters)

    # contact sheet: one frame from the middle of each segment
    thumbs = []
    for s, st in zip(segs, starts):
        r = run(["ffmpeg", "-v", "error", "-ss", f"{st + s['total'] * 0.6:.2f}", "-i", mp4, "-frames:v", "1",
                 "-vf", "scale=320:180", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        thumbs.append(Image.frombuffer("RGB", (320, 180), r.stdout[:320 * 180 * 3]))
    cols = 4
    sheet = Image.new("RGB", (cols * 320, -(-len(thumbs) // cols) * 180), "black")
    for i, th in enumerate(thumbs):
        sheet.paste(th, ((i % cols) * 320, (i // cols) * 180))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=85)
    print(f"{mp4}: {t / 60:.1f} min, {len(segs)} segments")


if __name__ == "__main__":
    sys.exit(main())

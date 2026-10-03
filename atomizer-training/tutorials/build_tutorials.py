"""Assemble narrated tutorial videos from the step GIFs, title cards and clips of the training videos.

Segments:
  card  — a title/section slide with synthetic narration
  gif   — one step animation from ../viz/out/<name>.gif with synthetic narration (last frame held while the voice finishes)
  clip  — a cut of a training video (local 360p + audio copies), i.e. the trainer's own words, with a lower-third caption

Synthetic narration is Microsoft Edge TTS voice en-US-SteffanNeural at 1x (`edge-tts`). Human narration is used wherever the
training videos have the trainer explaining the step. Output: ./out/<tutorial>.mp4 (1280x720, h264 + aac). The narration
text lives in scripts.py so it can be reviewed and edited without touching the build.

    python build_tutorials.py             # all
    python build_tutorials.py 02-during   # one
Set ATOMIZER_DL to the folder holding <id>.v360.mp4 and <id>.m4a (default /tmp/work/dl).
"""
import json, math, os, shutil, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont
from scripts import TUTORIALS, VOICE

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl")
OUT = f"{HERE}/out"; TMP = f"{HERE}/tmp"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TITLES = {v["id"]: v["title"] for v in json.load(open(f"{ROOT}/videos.json"))}
W, H, FPS = 1280, 720, 30
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-2000:])
    return r


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


def tts(text, path):
    if not os.path.exists(path):
        run(["edge-tts", "--voice", VOICE, "--text", text, "--write-media", path])
    return duration(path)


def card_png(title, sub, path):
    im = Image.new("RGB", (W, H), "#101820"); d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(FONTB, 54); f2 = ImageFont.truetype(FONT, 30); f3 = ImageFont.truetype(FONT, 22)
    y = 200
    for line in textwrap.wrap(title, 36):
        d.text((90, y), line, font=f1, fill="white"); y += 68
    y += 20
    for line in textwrap.wrap(sub, 70):
        d.text((90, y), line, font=f2, fill="#c9d6e2"); y += 42
    d.text((90, H - 70), "BYU Vertical Cloud Lab · AMAZEMET rePowder · draft for review", font=f3, fill="#7f8c99")
    im.save(path)


def seg_card(i, title, sub, narration):
    png = f"{TMP}/card_{i}.png"; mp3 = f"{TMP}/card_{i}.mp3"; out = f"{TMP}/seg_{i}.mp4"
    card_png(title, sub, png); d = tts(narration, mp3) + 0.6
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", png, "-i", mp3, "-t", f"{d:.2f}",
         "-af", "apad", "-shortest", *ENC, out])
    return out


def seg_gif(i, name, narration):
    gif = f"{ROOT}/viz/out/{name}.gif"; mp3 = f"{TMP}/gif_{i}.mp3"; out = f"{TMP}/seg_{i}.mp4"
    d_audio = tts(narration, mp3) + 0.6
    im = Image.open(gif); frames = []
    try:
        while True:
            frames.append(im.convert("RGB").copy()); im.seek(im.tell() + 1)
    except EOFError:
        pass
    gif_fps = 10; n_needed = int(math.ceil(d_audio * gif_fps))
    if len(frames) < n_needed:
        frames += [frames[-1]] * (n_needed - len(frames))
    fdir = f"{TMP}/gif_{i}_frames"; shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    for k, fr in enumerate(frames):
        canvas = Image.new("RGB", (W, H), "white"); fr2 = fr.resize((960, 720), Image.LANCZOS)
        canvas.paste(fr2, (160, 0)); canvas.save(f"{fdir}/f_{k:05d}.png")
    run(["ffmpeg", "-y", "-v", "error", "-framerate", str(gif_fps), "-i", f"{fdir}/f_%05d.png", "-i", mp3,
         "-af", "apad", "-shortest", *ENC, out])
    shutil.rmtree(fdir, ignore_errors=True)
    return out


def seg_clip(i, vid, start, dur, speaker):
    out = f"{TMP}/seg_{i}.mp4"
    v = f"{DL}/{vid}.v360.mp4"; a = f"{DL}/{vid}.m4a"
    if not (os.path.exists(v) and os.path.exists(a)):
        raise FileNotFoundError(f"{vid}: need {v} and {a}")
    mm = f"{int(start)//60:02d}:{int(start)%60:02d}"
    label = f"{speaker} · {TITLES.get(vid, vid)} · {mm}".replace(":", "\\:").replace("'", "’")
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
          f"drawbox=x=0:y=ih-64:w=iw:h=64:color=black@0.55:t=fill,"
          f"drawtext=fontfile={FONT}:text='{label}':x=24:y=h-46:fontsize=26:fontcolor=white")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", v,
         "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", a, "-map", "0:v:0", "-map", "1:a:0", "-vf", vf,
         "-af", "apad", "-shortest", *ENC, out])
    return out


def build(key):
    t = TUTORIALS[key]; os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    segs = []
    for i, seg in enumerate(t["segments"]):
        kind = seg[0]
        if kind == "card":
            segs.append(seg_card(f"{key}_{i}", seg[1], seg[2], seg[3]))
        elif kind == "gif":
            segs.append(seg_gif(f"{key}_{i}", seg[1], seg[2]))
        elif kind == "clip":
            segs.append(seg_clip(f"{key}_{i}", seg[1], seg[2], seg[3], seg[4]))
        print(key, i, kind, f"{duration(segs[-1]):.1f}s", flush=True)
    lst = f"{TMP}/{key}.txt"
    open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
    out = f"{OUT}/{key}.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    print(key, "->", out, f"{duration(out)/60:.1f} min", flush=True)
    return out


if __name__ == "__main__":
    for k in (sys.argv[1:] or list(TUTORIALS)):
        build(k)

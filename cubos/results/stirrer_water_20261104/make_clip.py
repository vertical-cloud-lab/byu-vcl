"""Cut camera 1's video into a short clip with the stirrer's status burned in.

usage: make_clip.py <label> <out-stem> <HH:MM:SS.s>-<HH:MM:SS.s> [...more ranges]

Each frame gets its UTC time, the speed asked for, and the last status reply from the Uno
at or before that frame (Hall rpm, duty, stalled). Writes <out-stem>.mp4 (30 fps, H.264)
and <out-stem>.gif (15 fps, 640 px wide) with ffmpeg.
"""
import json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

label, stem, ranges = sys.argv[1], sys.argv[2], sys.argv[3:]


def secs(hms):
    h, m, s = hms.rstrip("Z").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


t0 = secs(json.load(open(f"{label}_camera.json"))["first_bytes_utc"])
pts = [float(l) for l in open(f"{label}_pts.txt") if l.strip() and not l.startswith("#")]
events = [json.loads(l) for l in open(f"{label}.jsonl")]
for e in events:
    e["s"] = secs(e["utc"])
data = open(f"{label}.mjpeg", "rb").read()
offs, i = [], 0
while True:
    a = data.find(b"\xff\xd8", i)
    b = data.find(b"\xff\xd9", a + 2) if a >= 0 else -1
    if b < 0:
        break
    offs.append((a, b + 2))
    i = b + 2

try:
    font = ImageFont.truetype("DejaVuSans.ttf", 17)
    small = ImageFont.truetype("DejaVuSans.ttf", 14)
except OSError:
    font = small = ImageFont.load_default()


def caption(t):
    asked, status = "stirrer off", None
    for e in events:
        if e["s"] > t:
            break
        if e.get("event") == "step":
            asked = f"asked: {e['cmd'].split(',')[1]} rpm"
        elif e.get("event") in ("stop", "stop_file"):
            asked = "asked: stop"
        if "duty" in e:
            status = e
    hms = f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:04.1f} UTC"
    if status is None:
        return hms, asked, "Hall: no reply yet"
    st = " · STALLED, fan off" if status["stalled"] else ""
    return hms, asked, f"Hall: {status['rpm']:.0f} rpm · duty {status['duty']:.2f}{st}"


with tempfile.TemporaryDirectory() as tmp:
    n = 0
    for r in ranges:
        lo, hi = (secs(x) for x in r.split("-"))
        for k, p in enumerate(pts):
            t = t0 + p / 1000
            if not lo <= t <= hi:
                continue
            a, b = offs[k]
            im = Image.open(io.BytesIO(data[a:b])).convert("RGB")
            d = ImageDraw.Draw(im)
            hms, asked, hall = caption(t)
            d.rectangle((0, 0, im.width, 26), fill=(0, 0, 0))
            d.text((8, 4), f"{hms}   {asked}   {hall}", font=font, fill=(255, 255, 0))
            d.rectangle((0, im.height - 22, im.width, im.height), fill=(0, 0, 0))
            d.text((8, im.height - 19), "CubXL Pi camera 1, cropped to the vial on the compact "
                   "stirrer · 2026-11-04", font=small, fill=(230, 230, 230))
            im.save(f"{tmp}/f{n:05d}.png")
            n += 1
    print("frames", n)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", f"{tmp}/f%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-movflags", "+faststart",
                    f"{stem}.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{stem}.mp4", "-vf",
                    "fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];"
                    "[b][p]paletteuse=dither=bayer:bayer_scale=4", f"{stem}.gif"], check=True)
for ext in ("mp4", "gif"):
    print(f"{stem}.{ext}", round(Path(f"{stem}.{ext}").stat().st_size / 1e6, 2), "MB")

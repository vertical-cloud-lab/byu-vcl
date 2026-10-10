"""Put phone videos of a run on the wall clock, using the pixelated picam-ot2 room stream as the reference.

The stream burns lab local time into every frame (YYYY-MM-DD_HH-MM-SS, docs/stream-cams.md), so its clock can be read
off the picture. The phone videos carry no recording time on YouTube (no creation time in fileDetails, recordingDetails
empty), but the phone is worn on the operator's collar: its picture moves when the operator moves, and the ceiling
camera sees the operator move. Cross-correlating the two movement series finds each video's offset in the stream.

    python stream_sync.py clock STREAM.mp4 OUT.csv              # OCR the overlay every 30 s; prints the implied start
    python stream_sync.py motion STREAM.mp4 OUT.npy --grid      # stream: change per 0.5 s on a 4x4 grid below the overlay
    python stream_sync.py motion PHONE.mp4 OUT.npy              # phone: change per 0.5 s of the whole picture
    python stream_sync.py align STREAM.npy START PHONE.npy ...  # START = the stream's offset 0 in lab time, HH:MM:SS
    python stream_sync.py sheet RUN.json VIDEO_ID STEP FROM TO OUT.jpg   # phone frames with the stream frame inset

RUN.json (see ../runs/2026-10-06/alignment.json) names the stream file, its start and each video's file and offset.
Needs ffmpeg, tesseract, numpy and Pillow. Streams are 256x144 at 2 fps; phone videos any size.
"""
import argparse, csv, datetime as dt, io, json, math, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

CLOCK = re.compile(r"(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def frames(path, fps, w, h, extra=""):
    """Yield gray frames (h, w) as int16 at `fps`."""
    vf = f"fps={fps},scale={w}:{h}:flags=area" + extra
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", "1", "-i", path, "-vf", vf, "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            return
        yield np.frombuffer(b, np.uint8).reshape(h, w).astype(np.int16)


def cmd_clock(a):
    """Crop the overlay every 30 s (exact frame times from showinfo), OCR it, and check that time = start + offset."""
    tmp = a.out + "_crops"; os.makedirs(tmp, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-i", a.stream, "-vf",
                        "select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,29.99)',showinfo,crop=190:28:2:2",
                        "-vsync", "vfr", "-start_number", "0", f"{tmp}/%06d.png"], capture_output=True, text=True)
    pts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]
    env = dict(os.environ, OMP_THREAD_LIMIT="1")  # tesseract's own threads, times four workers, crawl

    def ocr(i):
        im = Image.open(f"{tmp}/{i:06d}.png").convert("L")
        im = ImageOps.invert(im.resize((im.width * 4, im.height * 4), Image.LANCZOS)).point(lambda v: 0 if v < 100 else 255)
        f = f"{tmp}/ocr_{i:06d}.png"; ImageOps.expand(im, 20, fill=255).save(f)
        out = subprocess.run(["tesseract", f, "-", "--psm", "7", "-c", "tessedit_char_whitelist=0123456789-_"],
                             capture_output=True, text=True, env=env).stdout.strip()
        os.remove(f)
        return out
    with ThreadPoolExecutor(4) as ex:
        texts = list(ex.map(ocr, range(len(pts))))
    starts = {}
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["stream_offset_s", "overlay", "implied_start"])
        for t, txt in zip(pts, texts):
            m = CLOCK.fullmatch(txt)
            s = (dt.datetime(*map(int, m.groups())) - dt.timedelta(seconds=t)).strftime("%H:%M:%S") if m else ""
            w.writerow([f"{t:.3f}", txt, s])
            if s:
                starts[s] = starts.get(s, 0) + 1
    print(f"{len(pts)} crops, {sum(starts.values())} read; implied start (time - offset):",
          sorted(starts.items(), key=lambda kv: -kv[1])[:4])


def cmd_motion(a):
    out, prev = [], None
    if a.grid:  # the stream: native 256x144, skip the overlay's rows, 4x4 cells
        for f in frames(a.video, 2, 256, 144):
            body = f[24:, :]
            out.append(np.zeros(16) if prev is None else np.abs(body - prev).reshape(4, 30, 4, 64).mean(axis=(1, 3)).ravel())
            prev = body
    else:
        for f in frames(a.video, 2, 64, 36):
            out.append(0.0 if prev is None else float(np.abs(f - prev).mean()))
            prev = f
    np.save(a.out, np.array(out, np.float32)); print(a.video, len(out) / 2, "s")


def prep(x, k=4):
    x = np.log1p(np.maximum(x, 0))
    return np.convolve(x, np.ones(k) / k, mode="same")


def ncc(sig, ref):
    """Pearson correlation of `sig` with every window of `ref`."""
    n = len(sig); s = (sig - sig.mean()) / (sig.std() + 1e-9)
    c = np.convolve(ref, np.ones(n), "valid"); c2 = np.convolve(ref ** 2, np.ones(n), "valid")
    sd = np.sqrt(np.maximum(c2 / n - (c / n) ** 2, 1e-12))
    return np.correlate(ref, s, "valid") / n / sd


def cmd_align(a):
    ref = np.load(a.stream_motion)
    ref = prep(ref.sum(axis=1) if ref.ndim == 2 else ref)
    start = dt.datetime.strptime(a.start, "%H:%M:%S")
    result = {}
    for path in a.phone_motion:
        vid = os.path.basename(path).split("_")[0].split(".")[0]
        sig = prep(np.load(path)); r = ncc(sig, ref); i = int(np.argmax(r))
        runner = max(r[j] for j in range(len(r)) if abs(j - i) > 120)
        halves = []
        for part, off in ((sig[:len(sig) // 2], 0), (sig[len(sig) // 2:], len(sig) // 2)):
            rr = ncc(part, ref); lo = max(0, i + off - 2400); j = lo + int(np.argmax(rr[lo:i + off + 2400]))
            halves.append(round((j - off) / 2, 1))
        t0 = start + dt.timedelta(seconds=i / 2); t1 = t0 + dt.timedelta(seconds=len(sig) / 2)
        result[vid] = {"stream_offset_s": i / 2, "r": round(float(r[i]), 3), "runner_up_r": round(float(runner), 3),
                       "halves_offset_s": halves, "start": t0.strftime("%H:%M:%S"), "end": t1.strftime("%H:%M:%S")}
        print(vid, result[vid])
    if a.out:
        json.dump(result, open(a.out, "w"), indent=1)


def grab(path, t, w, h, flags):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-vf",
                        f"scale={w}:{h}:flags={flags}", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def cmd_sheet(a):
    run = json.load(open(a.run)); v = run["videos"][a.video_id]
    start = dt.datetime.strptime(run["stream_start"], "%H:%M:%S")
    times = [a.t_from + i * a.step for i in range(int((a.t_to - a.t_from) / a.step) + 1)]
    font = ImageFont.truetype(FONT, 13); cols = 5; tw, th = 384, 234
    sheet = Image.new("RGB", (cols * tw, math.ceil(len(times) / cols) * th), "white"); d = ImageDraw.Draw(sheet)
    for k, t in enumerate(times):
        im = grab(v["file"], t, 384, 216, "bicubic")
        im.paste(grab(run["stream_file"], v["stream_offset_s"] + t, 144, 81, "area"), (238, 133))
        x, y = (k % cols) * tw, (k // cols) * th
        sheet.paste(im, (x, y + 18))
        wall = start + dt.timedelta(seconds=v["stream_offset_s"] + t)
        d.text((x + 3, y + 2), f"{int(t // 60):02d}:{int(t % 60):02d}  ({wall:%H:%M:%S})", fill="black", font=font)
    sheet.save(a.out, quality=72, optimize=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0]); sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("clock"); s.add_argument("stream"); s.add_argument("out"); s.set_defaults(fn=cmd_clock)
    s = sub.add_parser("motion"); s.add_argument("video"); s.add_argument("out"); s.add_argument("--grid", action="store_true")
    s.set_defaults(fn=cmd_motion)
    s = sub.add_parser("align"); s.add_argument("stream_motion"); s.add_argument("start"); s.add_argument("phone_motion", nargs="+")
    s.add_argument("--out"); s.set_defaults(fn=cmd_align)
    s = sub.add_parser("sheet"); s.add_argument("run"); s.add_argument("video_id"); s.add_argument("step", type=float)
    s.add_argument("t_from", type=float); s.add_argument("t_to", type=float); s.add_argument("out"); s.set_defaults(fn=cmd_sheet)
    a = p.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()

"""Frames of YouTube videos for register.py, fetched through a stream-cam Pi (#303).

YouTube refuses player extraction from a GitHub Actions runner ("Sign in to confirm you're not a bot"), but not from
the Pi's residential IP, so the fetching runs there over Tailscale SSH (``RPI_STREAM_CAM_USERNAME`` and
``RPI_STREAM_CAM_HOSTNAME``; the Pi has yt-dlp in ``~/.venvs/ytframes`` and node for its JS challenges). Downloads
stay small: storyboards are a few hundred kB of thumbnails, and each frame is one HTTP range read of the 720p stream
by the Pi's own ffmpeg, so whole videos never cross the Pi's Wi-Fi.

    python3 frames.py list "https://www.youtube.com/@Rigaku/search?query=MiniFlex"   # ids and titles (no Pi needed)
    python3 frames.py storyboard VIDEO_ID [...]     # .frames/contact/<id>_NN.jpg: thumbnails every few s, timed
    python3 frames.py grab VIDEO_ID T [T ...]       # .frames/<id>_<T>.jpg at 1280x720 (T in seconds)
    python3 frames.py grid IMAGE [STEP [x0,y0,x1,y1]]  # IMAGE_grid.jpg with labelled pixel lines, to read picks off

Pick from the contact sheets the moments that show the machine whole from different sides, grab those, read
anchor pixels off the gridded copies, and copy the chosen frames to ``refs/<key>/<view>.jpg`` with their picks in
``<view>.json`` (see register.py). ``.frames/`` is scratch space and is not committed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRATCH = HERE / ".frames"

PI_STORYBOARD = r'''
import json, os, sys, time, urllib.request
import yt_dlp
root = os.path.expanduser("~/ytframes/sb")
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
opts = {"quiet": True, "no_warnings": True, "skip_download": True, "js_runtimes": {"node": {"path": "/usr/bin/node"}}}
for vid in sys.argv[1:]:
    out = os.path.join(root, vid)
    os.makedirs(out, exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info("https://www.youtube.com/watch?v=" + vid, download=False)
    except Exception as e:
        print(json.dumps({"id": vid, "error": str(e)[:200]}), flush=True)
        continue
    sb = sorted((f for f in info["formats"] if str(f.get("format_id", "")).startswith("sb")),
                key=lambda f: -(f.get("width") or 0))
    if not sb:
        print(json.dumps({"id": vid, "error": "no storyboard"}), flush=True)
        continue
    f = sb[0]
    frags = []
    for i, fr in enumerate(f.get("fragments", [])):
        p = os.path.join(out, "sheet_%03d.jpg" % i)
        if not os.path.exists(p):
            req = urllib.request.Request(fr["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                open(p, "wb").write(r.read())
            time.sleep(0.2)
        frags.append({"file": os.path.basename(p), "duration": fr.get("duration")})
    meta = {"id": vid, "title": info.get("title"), "duration": info.get("duration"), "rows": f.get("rows"),
            "columns": f.get("columns"), "width": f.get("width"), "height": f.get("height"), "fragments": frags}
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"))
    print(json.dumps({k: meta[k] for k in ("id", "title", "duration")}), flush=True)
'''

PI_FRAMES = r'''
import json, os, subprocess, sys, time
import yt_dlp
jobs = json.load(sys.stdin)
out = os.path.expanduser("~/ytframes/fr")
os.makedirs(out, exist_ok=True)
opts = {"quiet": True, "no_warnings": True, "skip_download": True, "js_runtimes": {"node": {"path": "/usr/bin/node"}}}
for j in jobs:
    with yt_dlp.YoutubeDL(opts) as y:
        info = y.extract_info("https://www.youtube.com/watch?v=" + j["id"], download=False)
    fmts = {f["format_id"]: f for f in info["formats"]}
    f = next((fmts[k] for k in ("136", "398", "247", "135", "134", "18") if k in fmts and fmts[k].get("url")), None)
    if f is None:
        print(json.dumps({"id": j["id"], "error": "no video format"}), flush=True)
        continue
    hdrs = "".join("%s: %s\r\n" % kv for kv in (f.get("http_headers") or {}).items())
    for t in j["t"]:
        p = os.path.join(out, "%s_%06.1f.jpg" % (j["id"], t))
        if not os.path.exists(p):
            subprocess.run(["/usr/bin/ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-headers", hdrs,
                            "-ss", "%.2f" % t, "-i", f["url"], "-frames:v", "1", "-q:v", "2", p],
                           capture_output=True, text=True, timeout=180)
        print(json.dumps({"id": j["id"], "t": t, "ok": os.path.exists(p)}), flush=True)
'''


def _ssh(cmd: str, stdin: str | None = None, timeout=1800) -> str:
    user, host = os.environ["RPI_STREAM_CAM_USERNAME"], os.environ["RPI_STREAM_CAM_HOSTNAME"]
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o",
                        "ConnectTimeout=30", f"{user}@{host}", cmd], input=stdin, capture_output=True, text=True,
                       timeout=timeout)
    if r.returncode:
        raise RuntimeError(f"ssh failed ({r.returncode}): {r.stderr.replace(host, '<pi>')[-400:]}")
    return r.stdout


def _pull(remote_dir: str, local: Path, names: list[str]) -> None:
    """tar the named files (relative to remote_dir) on the Pi and unpack them into local."""
    user, host = os.environ["RPI_STREAM_CAM_USERNAME"], os.environ["RPI_STREAM_CAM_HOSTNAME"]
    local.mkdir(parents=True, exist_ok=True)
    ssh = subprocess.Popen(["ssh", "-o", "BatchMode=yes", f"{user}@{host}",
                            f"cd {remote_dir} && tar cf - " + " ".join(names)], stdout=subprocess.PIPE)
    subprocess.run(["tar", "xf", "-", "-C", str(local)], stdin=ssh.stdout, check=True)
    ssh.wait()


def storyboard(ids: list[str]) -> list[Path]:
    _ssh("cat > /tmp/vcl_storyboard.py", PI_STORYBOARD)
    print(_ssh("~/.venvs/ytframes/bin/python /tmp/vcl_storyboard.py " + " ".join(ids)), end="")
    _pull("~/ytframes/sb", SCRATCH / "sb", ids)
    return contact(ids)


def contact(ids: list[str], per=48) -> list[Path]:
    """Tile each video's storyboard thumbnails into sheets with the time burned into each."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    out = SCRATCH / "contact"
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for vid in ids:
        d = SCRATCH / "sb" / vid
        if not (d / "meta.json").exists():
            continue
        m = json.loads((d / "meta.json").read_text())
        w, h, R, C = m["width"], m["height"], m["rows"], m["columns"]
        thumbs, t = [], 0.0
        for fr in m["fragments"]:
            im = Image.open(d / fr["file"]).convert("RGB")
            nr, nc = im.height // h, im.width // w
            dt = (fr["duration"] or 0) / (R * C) if fr["duration"] else 0
            for k in range(nr * nc):
                if t >= (m["duration"] or 1e9):
                    break
                r, c = divmod(k, nc)
                thumbs.append((t, im.crop((c * w, r * h, (c + 1) * w, (r + 1) * h))))
                t += dt
        cols = 8 if w > h else 12
        for s in range(0, len(thumbs), per):
            chunk = thumbs[s:s + per]
            rows = (len(chunk) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w, rows * h), "white")
            dr = ImageDraw.Draw(sheet)
            for i, (tt, im) in enumerate(chunk):
                x, y = (i % cols) * w, (i // cols) * h
                sheet.paste(im, (x, y))
                dr.rectangle((x, y, x + 58, y + 20), fill="black")
                dr.text((x + 3, y + 1), "%d:%02d" % (tt // 60, tt % 60), fill="yellow", font=font)
            p = out / f"{vid}_{s // per:02d}.jpg"
            sheet.save(p, quality=85)
            paths.append(p)
            print(p)
    return paths


def grab(vid: str, times: list[float]) -> list[Path]:
    _ssh("cat > /tmp/vcl_frames.py", PI_FRAMES)
    print(_ssh("~/.venvs/ytframes/bin/python /tmp/vcl_frames.py", json.dumps([{"id": vid, "t": times}])), end="")
    names = ["%s_%06.1f.jpg" % (vid, t) for t in times]
    _pull("~/ytframes/fr", SCRATCH, names)
    return [SCRATCH / n for n in names]


def grid(src: str, step=50, crop=None) -> Path:
    """A copy of the image with labelled pixel lines every `step` px (magenta every second one)."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(src).convert("RGB")
    ox = oy = 0
    if crop:
        im = im.crop(crop)
        ox, oy = crop[0], crop[1]
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    for X in range((ox // step + 1) * step, ox + im.width, step):
        d.line([(X - ox, 0), (X - ox, im.height)], fill=(255, 0, 255) if X % (2 * step) == 0 else (0, 200, 255))
        d.text((X - ox + 2, 2), str(X), fill=(255, 255, 0), font=f)
    for Y in range((oy // step + 1) * step, oy + im.height, step):
        d.line([(0, Y - oy), (im.width, Y - oy)], fill=(255, 0, 255) if Y % (2 * step) == 0 else (0, 200, 255))
        d.text((2, Y - oy + 2), str(Y), fill=(255, 255, 0), font=f)
    out = Path(src).with_name(Path(src).stem + "_grid.jpg")
    im.save(out, quality=92)
    print(out)
    return out


def listing(url: str) -> None:
    """Ids, titles and lengths of a channel, playlist or search page (works from the runner; no Pi needed)."""
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--print", "%(id)s | %(title)s | %(duration)s", url],
                       capture_output=True, text=True, timeout=300)
    print(r.stdout or r.stderr[-500:])


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "list":
        listing(args[0])
    elif cmd == "storyboard":
        storyboard(args)
    elif cmd == "grab":
        grab(args[0], [float(t) for t in args[1:]])
    elif cmd == "grid":
        grid(args[0], int(args[1]) if len(args) > 1 else 50,
             tuple(int(v) for v in args[2].split(",")) if len(args) > 2 else None)
    else:
        sys.exit(__doc__)

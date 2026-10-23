#!/usr/bin/env python3
"""Cut a Studio session recording into the video to publish, by wall-clock time.

    python cut_recording.py SEGMENT_DIR PLAN.json OUT.mp4

The recorder writes 5 min segments named raw_<UTC start>.mkv (ffmpeg `-f segment -strftime 1`),
so a wall-clock instant maps to a segment and an offset inside it. PLAN.json lists the parts to
keep, each {"from": "HH:MM:SS", "to": "HH:MM:SS", "speed": N, "label": "..."}, plus "day"
("YYYY-MM-DD") and "blur": [[from, to], ...], the stretches where Studio's camera pane shows the
room. In those, the pane's two upper corners are blurred, where people walking past show up
(README.md, "Recording and keeping the sent file"). Whatever isn't in a part is dropped: the
login, where the e-mail address is on screen, must never be in one.
Writes OUT.mp4 and OUT_chapters.txt (YouTube chapter lines).
"""
import datetime as dt, glob, json, os, re, subprocess, sys, tempfile

SEG_DIR, PLAN, OUT = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLUR_BOXES = [(274, 136, 244, 341), (1085, 136, 213, 274)]   # x, y, w, h on the 1920x1080 screen
DAY = dt.date.fromisoformat(PLAN["day"])


def at(hms):
    return dt.datetime.combine(DAY, dt.time.fromisoformat(hms), tzinfo=dt.timezone.utc)


segs = []
for p in sorted(glob.glob(os.path.join(SEG_DIR, "raw_*.mkv"))):
    t = dt.datetime.strptime(re.search(r"raw_(\d{8}T\d{6}Z)", p).group(1), "%Y%m%dT%H%M%SZ")
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", p], capture_output=True, text=True).stdout.strip()
    try:
        dur = float(out)
    except ValueError:   # the segment still being written has no duration yet
        dur = (dt.datetime.utcnow() - t).total_seconds() - 5
    segs.append((t.replace(tzinfo=dt.timezone.utc), dur, p))


def blur_filter(t0, t1):
    """boxblur on the camera corners while [t0, t1) overlaps a blur stretch, else a pass-through."""
    spans = []
    for a, b in PLAN.get("blur", []):
        a, b = max(at(a), t0), min(at(b), t1)
        if a < b:
            spans.append(((a - t0).total_seconds(), (b - t0).total_seconds()))
    if not spans:
        return "[0:v]null[b]"
    en = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in spans)
    f, last = [], "0:v"
    for i, (x, y, w, h) in enumerate(BLUR_BOXES):
        f.append(f"[{last}]split[m{i}][c{i}];[c{i}]crop={w}:{h}:{x}:{y},boxblur=24:3[bl{i}];"
                 f"[m{i}][bl{i}]overlay={x}:{y}:enable='{en}'[o{i}]")
        last = f"o{i}"
    return ";".join(f) + f";[{last}]null[b]"


tmp = tempfile.mkdtemp()
pieces, chapters, clock = [], [], 0.0
for k, part in enumerate(PLAN["parts"]):
    t0, t1 = at(part["from"]), at(part["to"])
    speed, label = part.get("speed", 1), part["label"]
    chapters.append((clock, label))
    for s_start, s_dur, path in segs:
        a, b = max(t0, s_start), min(t1, s_start + dt.timedelta(seconds=s_dur))
        if a >= b:
            continue
        out = os.path.join(tmp, f"p{len(pieces):03d}.mp4")
        tag = f"{speed:g}x speed" if speed != 1 else "real time"
        vf = (blur_filter(a, b) + f";[b]setpts=PTS/{speed},fps=15,"
              f"drawtext=fontfile={FONT}:text='{tag}':x=w-tw-24:y=h-th-20:fontsize=26:fontcolor=white:"
              f"box=1:boxcolor=black@0.55:boxborderw=8[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(a - s_start).total_seconds():.2f}",
                        "-to", f"{(b - s_start).total_seconds():.2f}", "-i", path, "-filter_complex", vf,
                        "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
                        "-pix_fmt", "yuv420p", out], check=True)
        pieces.append(out)
        clock += (b - a).total_seconds() / speed

with open(os.path.join(tmp, "list.txt"), "w") as f:
    f.writelines(f"file '{p}'\n" for p in pieces)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i",
                os.path.join(tmp, "list.txt"), "-c", "copy", "-movflags", "+faststart", OUT], check=True)
with open(os.path.splitext(OUT)[0] + "_chapters.txt", "w") as f:
    for c, label in chapters:
        f.write(f"{int(c // 60)}:{int(c % 60):02d} {label}\n")
print(open(os.path.splitext(OUT)[0] + "_chapters.txt").read(), end="")
print(f"{OUT}: {os.path.getsize(OUT) / 1e6:.1f} MB, {clock / 60:.1f} min")

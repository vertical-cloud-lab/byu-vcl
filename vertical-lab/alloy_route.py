"""The alloy route, start to finish (#303): the seven chapters joined into one MP4, each with a title card and then
the route's function network (``route_dag.py``: DAL's ONR YIP DAG, brought in a stage at a time) before it.

    python3 alloy_route.py        # -> out/mp4/alloy_route.mp4, out/alloy_route.json, out/alloy_route_sheet.png

1. ``alloy_charge.py``: the charge cups, four 5N Al and four OFE Cu, dosed by the multi-doser through one funnel per
   powder, weighed on an A&D HR-202i, and their plugs pressed home under vacuum (``alloy_press.py``: a Specac Atlas
   Autotouch 15T and the lab's evacuable die; VLM, tray B)
2. ``alloy_atomize.py``: the Al cups melted in the rePowder and atomized
3. ``alloy_print.py``: the powder sieved to the LPBF cut and printed in the Aconity MIDI
4. ``alloy_powder.py`` (round 8): the retained powder through laser diffraction, powder XRD, XRF and the SEM
5. ``alloy_workflow.py``: depowder, the wire EDM, heat treatment, tensile tests at room and elevated temperature
6. ``alloy_prep.py`` (round 8): sectioning, hot mounting, grinding and polishing
7. ``alloy_characterize.py``: the mounts through the characterization trays at the VLM's opening

Each chapter renders on its own (its GIF, MP4 and JSON). This only joins the MP4s: they are re-encoded once, so the
cards (drawn here with PIL) and the clips don't have to share an encoder's settings.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from scene import OUT, font

CHAPTERS = [
    ("alloy_charge", "1/7  The charge",
     "Four 5N Al and four oxygen-free Cu charge cups on tray B of the VLM: dosed by the multi-doser through one "
     "funnel per powder, weighed on an A&D HR-202i, topped up to the plug, and the plug pressed home under vacuum "
     "in a Specac Atlas Autotouch 15T"),
    ("alloy_atomize", "2/7  Melt and atomize",
     "The four Al cups melted in the rePowder's induction furnace and atomized ultrasonically under argon, cut "
     "with the lab's own footage"),
    ("alloy_print", "3/7  Sieve and print",
     "The arm runs a sieving cell: it stacks the sieves, the AS 200 shakes them, and a tipper empties each into its "
     "own labelled jar. The LPBF cut is printed into tensile bars in the Aconity MIDI"),
    ("alloy_powder", "4/7  The powder, checked",
     "While the build prints, a retained sample of the sieved cut goes round the trays: laser diffraction, powder "
     "XRD after its sample prep, XRF and the SEM"),
    ("alloy_workflow", "5/7  Cut, heat treat and test",
     "The build depowdered, the bars cut off in the wire EDM and caught, rinsed, heat treated as tensile specimens, "
     "and pulled with automatic loading at room and elevated temperature"),
    ("alloy_prep", "6/7  Sample prep",
     "Sections cut from the build, hot-mounted in conductive compound or set in a steel mount, then ground and "
     "polished with every paper and cloth change shown"),
    ("alloy_characterize", "7/7  Characterize",
     "The mounts through the characterization trays: the VLM brings each tray to the opening, the arm loads each "
     "instrument, and each shows its data"),
]
SIZE, FPS, CARD_S = (1280, 720), 15, 3.0
# the 2 x 2 sheet: a picture of each chapter at work (a still it saves, or a frame of its MP4 as a fraction of its
# length, so a re-rendered chapter of another length still gives the same moment); <key>_still.png if the named still
# is missing
SHEET = {"alloy_charge": "alloy_charge_press.png", "alloy_atomize": "alloy_atomize_still.png",
         "alloy_print": 0.908, "alloy_powder": "alloy_powder_still.png", "alloy_workflow": "alloy_workflow_cut.png",
         "alloy_prep": "alloy_prep_still.png", "alloy_characterize": "alloy_characterize_still.png",
         "dag": "dag/route_dag_ch7.png"}
BLUE = (30, 60, 140)


def card(title: str, sub: str, path: Path):
    im = Image.new("RGB", SIZE, (246, 247, 249))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, SIZE[0], 10), fill=BLUE)
    d.text((80, 200), "The alloy route, start to finish", font=font(30), fill=(110, 114, 120))
    d.text((80, 250), title, font=font(64, bold=True), fill=BLUE)
    words, lines, cur = sub.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 62:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    for k, ln in enumerate(lines):
        d.text((80, 360 + 44 * k), ln, font=font(32), fill=(40, 42, 46))
    d.text((80, SIZE[1] - 70), "Vertical Cloud Lab @ BYU, byu-vcl #303", font=font(22), fill=(110, 114, 120))
    im.save(path)


def duration(path: Path) -> float:
    r = subprocess.run(["ffmpeg", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def main():
    tmp = Path(tempfile.mkdtemp())
    parts, chapters, t = [], [], 0.0
    for ci, (key, title, sub) in enumerate(CHAPTERS, 1):
        mp4 = OUT / "mp4" / f"{key}.mp4"
        png = tmp / f"{key}_card.png"
        if not mp4.exists():
            sub = sub + " (not rendered yet)"
        card(title, sub, png)
        clip = tmp / f"{key}_card.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(CARD_S), "-i", str(png),
                        "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)], check=True)
        parts.append(clip)
        t += CARD_S
        dag = OUT / "mp4" / "dag" / f"route_dag_ch{ci}.mp4"
        if dag.exists():
            parts.append(dag)
            t += duration(dag)
        if mp4.exists():
            d = duration(mp4)
            chapters.append(dict(key=key, title=title, start_s=round(t, 1), seconds=round(d, 1),
                                 source=f"{key}.py", mp4=f"out/mp4/{key}.mp4"))
            parts.append(mp4)
            t += d
        else:
            chapters.append(dict(key=key, title=title, start_s=None, seconds=0, missing=True))
    # Each part is brought to one size and frame rate on its own before the join. The concat demuxer takes its
    # timing from the first file, so a chapter rendered at 10 fps (VIZ3D_FPS=10) among 15 fps ones came out short.
    norm = []
    for i, part in enumerate(parts):
        out = tmp / f"n{i:02d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(part),
                        "-vf", f"scale={SIZE[0]}:{SIZE[1]}:force_original_aspect_ratio=decrease,"
                               f"pad={SIZE[0]}:{SIZE[1]}:(ow-iw)/2:(oh-ih)/2:color=white,fps={FPS}",
                        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p",
                        "-video_track_timescale", "15360", str(out)], check=True)
        norm.append(out)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in norm))
    dst = OUT / "mp4" / "alloy_route.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)
    (OUT / "alloy_route.json").write_text(json.dumps(dict(name="alloy_route", seconds=round(t, 1),
                                                          card_seconds=CARD_S, chapters=chapters), indent=1) + "\n")
    # a 2 x 4 sheet of each chapter's still and the network, for the README
    w, h = 640, 360
    sheet = Image.new("RGB", (2 * w, 4 * h), "white")
    for i, k in enumerate([c[0] for c in CHAPTERS] + ["dag"]):
        src = SHEET[k]
        if isinstance(src, float):
            p = tmp / f"{k}_frame.png"
            mp4, meta = OUT / "mp4" / f"{k}.mp4", OUT / f"{k}.json"
            if mp4.exists():
                n = json.loads(meta.read_text())["n_frames"] if meta.exists() else int(duration(mp4) * FPS)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf",
                                f"select=eq(n\\,{int(src * (n - 1))})", "-vframes", "1", str(p)], check=True)
        else:
            p = OUT / src
            if not p.exists():
                p = OUT / f"{k}_still.png"
        if p.exists():
            sheet.paste(Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS), ((i % 2) * w, (i // 2) * h))
    sheet.save(OUT / "alloy_route_sheet.png")
    print(f"alloy_route: {t:.1f} s, {dst.stat().st_size / 1e6:.1f} MB; chapters: "
          + ", ".join(f"{c['key']} {c['seconds']} s" for c in chapters), flush=True)


if __name__ == "__main__":
    main()

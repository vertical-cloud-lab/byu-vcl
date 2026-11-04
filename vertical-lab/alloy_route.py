"""The alloy route, start to finish (#303): the four chapters joined into one MP4, with a title card before each.

    python3 alloy_route.py        # -> out/mp4/alloy_route.mp4, out/alloy_route.json, out/alloy_route_sheet.png

1. ``alloy_charge.py``: the charge cups, 5N Al and OFE Cu, filled by the multi-doser and their plugs pressed home
   under vacuum (``alloy_press.py``: a Specac Atlas Autotouch 15T and the lab's evacuable die; VLM, tray B)
2. ``alloy_atomize.py``: the Al cups melted in the rePowder and atomized
3. ``alloy_print.py``: the powder sieved to the LPBF cut and printed in the Aconity MIDI
4. ``alloy_workflow.py`` (round 4): the build plate to the wire EDM, a tensile bar to the Instron 68FM-100

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
    ("alloy_charge", "1/4  The charge",
     "Charge cups turned from 5N Al and oxygen-free Cu bar, filled to the plug by the multi-doser, then the plug "
     "pressed home at 3.2 t under vacuum in a Specac Autotouch, on tray B of the VLM"),
    ("alloy_atomize", "2/4  Melt and atomize",
     "The four Al cups melted in the rePowder's induction furnace and atomized ultrasonically under argon, cut "
     "with the lab's own footage of its bronze and Al runs"),
    ("alloy_print", "3/4  Sieve and print",
     "The powder sieved to the LPBF cut, then printed into tensile bars in the Aconity MIDI"),
    ("alloy_workflow", "4/4  Cut and test",
     "The build plate to the wire EDM, a tensile bar to the Instron 68FM-100"),
]
SIZE, FPS, CARD_S = (1280, 720), 15, 3.0
# the 2 x 2 sheet: a picture of each chapter at work (a still it saves, or a frame of its MP4 as a fraction of its
# length, so a re-rendered chapter of another length still gives the same moment); <key>_still.png if the named still
# is missing
SHEET = {"alloy_charge": "alloy_charge_press.png", "alloy_atomize": "alloy_atomize_still.png",
         "alloy_print": 0.908, "alloy_workflow": "alloy_workflow_cut.png"}
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
    for key, title, sub in CHAPTERS:
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
        if mp4.exists():
            d = duration(mp4)
            chapters.append(dict(key=key, title=title, start_s=round(t, 1), seconds=round(d, 1),
                                 source=f"{key}.py", mp4=f"out/mp4/{key}.mp4"))
            parts.append(mp4)
            t += d
        else:
            chapters.append(dict(key=key, title=title, start_s=None, seconds=0, missing=True))
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    dst = OUT / "mp4" / "alloy_route.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-vf", f"scale={SIZE[0]}:{SIZE[1]}:force_original_aspect_ratio=decrease,"
                           f"pad={SIZE[0]}:{SIZE[1]}:(ow-iw)/2:(oh-ih)/2:color=white,fps={FPS}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(dst)], check=True)
    (OUT / "alloy_route.json").write_text(json.dumps(dict(name="alloy_route", seconds=round(t, 1),
                                                          card_seconds=CARD_S, chapters=chapters), indent=1) + "\n")
    # a 2 x 2 sheet of each chapter's still, for the README
    w, h = 640, 360
    sheet = Image.new("RGB", (2 * w, 2 * h), "white")
    for i, (k, _, _) in enumerate(CHAPTERS):
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

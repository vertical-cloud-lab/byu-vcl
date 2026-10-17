"""Ronnie's magnet spot, beside the same corner of the real machine: writes spot.png.

The two photos are keyframes from the training recordings, committed on the PR #255 branch
(`atomizer-training/keyframes/sop/`). They are read straight from git, so fetch that branch first:

    git fetch origin claude/issue-124-20261003-0335
    python make_spot_figure.py
"""
import io
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BRANCH = "origin/claude/issue-124-20261003-0335"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
H = 360                       # panel height, px
ARROW = (255, 140, 0)         # orange: reads on the blue panels and the steel


def keyframe(name: str) -> Image.Image:
    blob = subprocess.run(["git", "show", f"{BRANCH}:atomizer-training/keyframes/sop/{name}.jpg"],
                          capture_output=True, check=True, cwd=HERE).stdout
    im = Image.open(io.BytesIO(blob)).convert("RGB")
    return im.resize((round(im.width * H / im.height), H), Image.LANCZOS)


def arrow(d: ImageDraw.ImageDraw, tail, head, width=5):
    import math
    d.line([tail, head], fill=(0, 0, 0), width=width + 4)
    d.line([tail, head], fill=ARROW, width=width)
    ang = math.atan2(head[1] - tail[1], head[0] - tail[0])
    pts = [head] + [(head[0] - 20 * math.cos(ang + s * 0.45), head[1] - 20 * math.sin(ang + s * 0.45)) for s in (1, -1)]
    d.polygon(pts, fill=ARROW, outline=(0, 0, 0))


def label(d: ImageDraw.ImageDraw, xy, text, font):
    x, y = xy
    box = d.multiline_textbbox((x, y), text, font=font, spacing=3)
    d.rectangle([box[0] - 5, box[1] - 4, box[2] + 5, box[3] + 4], fill=(255, 255, 255), outline=(0, 0, 0))
    d.multiline_text((x, y), text, font=font, fill=(0, 0, 0), spacing=3)


def main():
    f = ImageFont.truetype(FONT, 17)
    fb = ImageFont.truetype(BOLD, 18)

    # 1. Ronnie's circle, drawn on our CAD render (atomizer-training/viz3d/out/machine.png)
    a = Image.open(HERE / "circle_on_render.png").convert("RGB")
    a = a.resize((round(a.width * H / a.height), H), Image.LANCZOS)

    # 2. The corner above the atomization chamber: black hoses leave the cabinet's left side and
    #    loop into the furnace (T7 20:04)
    b = keyframe("FDRTt68Vfvo_01204")
    db = ImageDraw.Draw(b)
    arrow(db, (250, 175), (215, 102))
    label(db, (150, 180), "black hoses from the cabinet\ninto the furnace: the coil leads", f)
    label(db, (330, 300), "top of the atomization chamber", f)

    # 3. The cabinet's left side door being closed (T1 04:06). The same hoses are just past its
    #    free edge; behind it are the air, argon and pneumatics, and the coolant flow check
    c = keyframe("wRc8p2_FnJo_00246")
    dc = ImageDraw.Draw(c)
    arrow(dc, (520, 330), (585, 215))
    label(dc, (300, 300), "the same black hoses", f)
    label(dc, (285, 105), "left side door", f)

    gap, top, bottom = 16, 34, 64
    W = a.width + b.width + c.width + 4 * gap
    out = Image.new("RGB", (W, top + H + bottom), "white")
    d = ImageDraw.Draw(out)
    x = gap
    for im, title in ((a, "Your circle, on our CAD render"),
                      (b, "The same corner on the machine (T7 20:04)"),
                      (c, "Cabinet's left side door (T1 04:06)")):
        out.paste(im, (x, top))
        d.text((x, 8), title, font=fb, fill=(0, 0, 0))
        x += im.width + gap
    d.text((gap, top + H + 10),
           "Stick the magnet on bare painted panel at least a hand's width (about 10 cm) from the black hoses, "
           "and look at what is behind the panel first.", font=f, fill=(0, 0, 0))
    d.text((gap, top + H + 34),
           "Photos: keyframes of the training recordings (PR #255). Render: atomizer-training/viz3d.",
           font=ImageFont.truetype(FONT, 14), fill=(90, 90, 90))
    out.save(HERE / "spot.png", optimize=True)
    print("spot.png", out.size)


if __name__ == "__main__":
    main()

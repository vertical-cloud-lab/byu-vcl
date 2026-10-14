#!/usr/bin/env python3
"""Turn a run's robot-camera step photos into one captioned GIF, in step order.

    python3 snapshot_gif.py OUT.gif "trip 1=enc1/" "paint=paint/" "trip 2=enc2/" [--width 480]

Each argument is ``caption=folder``; the folder's ``NN_label[_robot].jpg`` photos
(the drivers' step photos, already turned upright) go in by their step number,
each captioned with the part's name and the step's label, so the GIF reads as
the run went. Photos of the same step taken twice are kept once.
"""
import argparse
import glob
import os
import re

from PIL import Image, ImageDraw


def frames(folder):
    out = {}
    for p in glob.glob(os.path.join(folder, "*.jpg")):
        m = re.match(r"(\d+)_(.+?)(_robot)?\.jpg$", os.path.basename(p))
        if m and not m.group(2).endswith("_live"):
            out.setdefault(int(m.group(1)), (m.group(2), p))
    return [out[k] for k in sorted(out)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out")
    ap.add_argument("parts", nargs="+", help="caption=folder")
    ap.add_argument("--width", type=int, default=400)
    ap.add_argument("--colors", type=int, default=48)
    ap.add_argument("--ms", type=int, default=450, help="milliseconds per frame")
    a = ap.parse_args()
    imgs = []
    for part in a.parts:
        cap, _, folder = part.partition("=")
        for label, path in frames(folder):
            im = Image.open(path).convert("RGB")
            im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            text = f"{cap}: {label}"
            d.rectangle((0, 0, a.width, 16), fill=(0, 0, 0))
            d.text((4, 2), text, fill=(255, 255, 255))
            imgs.append(im.quantize(colors=a.colors, method=Image.Quantize.MEDIANCUT))
    imgs[0].save(a.out, save_all=True, append_images=imgs[1:], duration=a.ms, loop=0, optimize=True)
    print(f"{a.out}: {len(imgs)} frames, {os.path.getsize(a.out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

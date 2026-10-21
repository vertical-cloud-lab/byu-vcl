"""Black out the EZstat PC's Windows username wherever OCR finds it, plus extra boxes.

    python redact_png.py IN.png OUT.png [x0,y0,x1,y1 ...]

The username is read from POTENTIOSTAT_PC_USERNAME and never printed: the
output is only how many words matched and where. Desktop labels are white on
a blue gradient and often truncated ("Melodie_sa..."), so OCR runs on a 3x
upscale, both as is and inverted, and a word counts as a match if it contains
the username, is within one edit of it, or is a truncated start of it. Look
at the result anyway: OCR misses things, and extra boxes are for those.
"""

import csv
import io
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageOps

SCALE = 3
PAD = 3


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def edit_distance(a, b):
    row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, row[0] = row[0], i
        for j, cb in enumerate(b, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (ca != cb))
    return row[-1]


def is_match(word, user):
    return (user in word
            or edit_distance(word, user) <= 1
            or (len(word) >= 4 and user.startswith(word))
            or (len(word) >= 4 and word.startswith(user[:4]) and edit_distance(word, user + "pc") <= 2))


def ocr_boxes(img):
    gray = ImageOps.grayscale(img).resize((img.width * SCALE, img.height * SCALE), Image.LANCZOS)
    for variant in (gray, ImageOps.invert(gray)):
        buf = io.BytesIO()
        variant.save(buf, "PNG")
        tsv = subprocess.run(["tesseract", "stdin", "stdout", "--psm", "11", "tsv"],
                             input=buf.getvalue(), capture_output=True, check=True).stdout
        for row in csv.DictReader(io.StringIO(tsv.decode()), delimiter="\t",
                                  quoting=csv.QUOTE_NONE):
            text = (row.get("text") or "").strip()
            if text:
                left, top = int(row["left"]) // SCALE, int(row["top"]) // SCALE
                yield (norm(text), (left, top,
                                    left + int(row["width"]) // SCALE + 1,
                                    top + int(row["height"]) // SCALE + 1))


def main(src, dst, extra):
    user = norm(os.environ["POTENTIOSTAT_PC_USERNAME"])
    img = Image.open(src).convert("RGB")
    words = list(ocr_boxes(img))
    hits = [box for word, box in words if word and is_match(word, user)]
    print(f"OCR words: {len(words)}; username matches: {len(hits)} {hits}")
    boxes = hits + [tuple(int(v) for v in b.split(",")) for b in extra]
    draw = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in boxes:
        draw.rectangle((x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD), fill=(0, 0, 0))
    img.save(dst, optimize=True)
    print(f"boxes drawn: {len(boxes)} -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

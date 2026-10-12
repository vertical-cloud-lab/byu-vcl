"""Cut sb0 storyboard sheets into time-stamped tiles and pack them into review sheets.

tiles.py INFO_JSONL SB_DIR OUT_DIR PREFIX ID[:STEP][,ID[:STEP]...] [STEP]
Every tile is labelled "<id> mm:ss" (or h:mm:ss). STEP keeps every Nth tile,
per video or for all; about one tile per 4 s of video was enough here.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
info, sbdir, out, prefix, idarg = sys.argv[1:6]
step = int(sys.argv[6]) if len(sys.argv) > 6 else 1
ids, steps = [], {}
for x in idarg.split(","):
    vid, _, s = x.partition(":")
    ids.append(vid)
    steps[vid] = int(s) if s else step
recs = {}
for l in open(info):
    r = json.loads(l)
    recs[r["id"]] = r
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
W, H = 1920, 1080
os.makedirs(out, exist_ok=True)
def fmt(t):
    t = int(t); h, m, s = t // 3600, t % 3600 // 60, t % 60
    return "%d:%02d:%02d" % (h, m, s) if h else "%d:%02d" % (m, s)
tiles = []  # (img, label)
for vid in ids:
    r = recs[vid]; sb = r["sb"]["sb0"]
    tw, th, rows, cols, fps = sb["width"], sb["height"], sb["rows"], sb["columns"], sb["fps"]
    k = 0
    for i in range(len(sb["fragments"])):
        p = os.path.join(sbdir, vid, "%03d.img" % i)
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            k += rows * cols; continue
        for rr in range(rows):
            for cc in range(cols):
                t = k / fps
                k += 1
                if r.get("duration") and t > r["duration"]:
                    continue
                box = (cc * tw, rr * th, cc * tw + tw, rr * th + th)
                if box[2] > im.width or box[3] > im.height:
                    continue
                tile = im.crop(box)
                if tile.getextrema()[0][1] < 8:  # empty black padding tile
                    continue
                if (k - 1) % steps[vid] == 0:
                    tiles.append((tile, "%s %s" % (vid, fmt(t))))
# pack: rows of height 180+16, left to right
CH = 180 + 16
sheets, sheet, d, x, y = [], None, None, 0, 0
def new():
    s = Image.new("RGB", (W, H), (40, 40, 40)); return s, ImageDraw.Draw(s)
for tile, label in tiles:
    if tile.height != 180:
        tile = tile.resize((max(1, round(tile.width * 180 / tile.height)), 180))
    if sheet is None:
        sheet, d = new(); x = y = 0
    if x + tile.width > W:
        x = 0; y += CH
    if y + CH > H:
        sheets.append(sheet); sheet, d = new(); x = y = 0
    sheet.paste(tile, (x, y))
    d.text((x + 2, y + 181), label, fill="yellow", font=font)
    x += tile.width + 2
if sheet is not None:
    sheets.append(sheet)
for n, s in enumerate(sheets):
    s.save(os.path.join(out, "%s_%03d.jpg" % (prefix, n)), quality=85)
print(prefix, "tiles", len(tiles), "sheets", len(sheets))

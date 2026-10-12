"""Build a chronological time-lapse of storyboard tiles from livestream archives.

timelapse.py INFO_JSONL TITLE_PREFIX SPACING_S OUT_DIR SHEET_PREFIX [MIN_BRIGHTNESS]
Samples one storyboard tile every SPACING_S seconds of each archive whose title
starts with TITLE_PREFIX, downloads only the sheets it needs, labels each tile
with lab local time (UTC-6), drops dark tiles, and packs them into sheets.
With DEDUP=N in the environment, a tile is kept only if at least N of its
64x36 pixels changed against the last kept tile (or a day has passed), so a
static camera collapses to the moments when something moved. 12 worked here.
"""
import json, os, sys, urllib.request, datetime, concurrent.futures as cf
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageStat
info, prefix, spacing, out, sprefix = sys.argv[1:6]
spacing = float(spacing)
minb = float(sys.argv[6]) if len(sys.argv) > 6 else 25
cache = "/tmp/yt/sbcache"
os.makedirs(cache, exist_ok=True); os.makedirs(out, exist_ok=True)
recs = [json.loads(l) for l in open(info)]
recs = [r for r in recs if r.get("ok") and (r.get("title") or "").startswith(prefix) and r["sb"].get("sb0")]
want = []  # (local_dt, vid, t, sheet_idx, pos, url, tw, th, cols)
for r in recs:
    sb = r["sb"]["sb0"]; fps = sb["fps"]; per = sb["rows"] * sb["columns"]
    t0 = r.get("release_timestamp") or r.get("timestamp")
    dur = r.get("duration") or 0
    t = 0.0
    while t < dur:
        k = int(round(t * fps)); si, pos = divmod(k, per)
        if si < len(sb["fragments"]):
            loc = datetime.datetime.fromtimestamp(t0 + t, datetime.UTC) - datetime.timedelta(hours=6)
            want.append((loc, r["id"], t, si, pos, sb["fragments"][si][0], sb["width"], sb["height"], sb["columns"]))
        t += spacing
want.sort()
def get(item):
    vid, si, url = item
    p = os.path.join(cache, "%s_%04d.img" % (vid, si))
    if not os.path.exists(p):
        for _ in range(3):
            try:
                data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
                open(p, "wb").write(data); break
            except Exception:
                pass
    return p
needed = sorted({(w[1], w[3], w[5]) for w in want})
with cf.ThreadPoolExecutor(16) as ex:
    list(ex.map(get, needed))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
tiles = []; tiles_sig = []; tiles_loc = []
DEDUP = float(os.environ.get("DEDUP", "0"))
for loc, vid, t, si, pos, url, tw, th, cols in want:
    p = os.path.join(cache, "%s_%04d.img" % (vid, si))
    try:
        im = Image.open(p).convert("RGB")
    except Exception:
        continue
    r_, c_ = divmod(pos, cols)
    box = (c_ * tw, r_ * th, c_ * tw + tw, r_ * th + th)
    if box[2] > im.width or box[3] > im.height:
        continue
    tile = im.crop(box)
    if ImageStat.Stat(tile.convert("L")).mean[0] < minb:
        continue
    if tile.width >= tile.height and tile.size != (320, 180):
        tile = tile.resize((320, 180))
    elif tile.width < tile.height:
        tile = tile.resize((round(tile.width * 180 / tile.height), 180))
    sig = np.asarray(tile.convert("L").resize((64, 36)), dtype=np.float32)
    sig[:4, :26] = 0  # timestamp overlay, top left
    if DEDUP and tiles_sig:
        d = sig - tiles_sig[-1]
        d -= np.median(d)  # ignore global exposure shifts
        changed = int((np.abs(d) > 30).sum())
        if changed < DEDUP and (loc - tiles_loc[-1]).total_seconds() < 86400:
            continue
    tiles_sig.append(sig); tiles_loc.append(loc)
    tiles.append((tile, "%s %s %s" % (loc.strftime("%m-%d %H:%M"), vid, "%d:%02d:%02d" % (t // 3600, t % 3600 // 60, t % 60))))
W, H, CH = 1932, 990, 198
n = 0
sheet = None
for tile, label in tiles:
    lw = max(tile.width, 8 * len(label) if tile.width >= tile.height else 0)
    slot = max(tile.width, 104) + 2
    if sheet is None:
        sheet = Image.new("RGB", (W, H), (40, 40, 40)); d = ImageDraw.Draw(sheet); x = y = 0
    if x + slot > W:
        x = 0; y += CH
    if y + CH > H:
        sheet.save(os.path.join(out, "%s_%03d.jpg" % (sprefix, n)), quality=85); n += 1
        sheet = Image.new("RGB", (W, H), (40, 40, 40)); d = ImageDraw.Draw(sheet); x = y = 0
    sheet.paste(tile, (x, y))
    if tile.width >= tile.height:
        d.text((x + 2, y + 182), label, fill="yellow", font=font)
    else:  # narrow tile: two short lines
        parts = label.split(" ")
        d.text((x + 1, y + 2), " ".join(parts[:2]), fill="yellow", font=font)
        d.text((x + 1, y + 182), parts[2][:11] + " " + parts[3], fill="yellow", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10))
    x += slot
if sheet is not None:
    sheet.save(os.path.join(out, "%s_%03d.jpg" % (sprefix, n)), quality=85); n += 1
print(sprefix, "archives", len(recs), "samples", len(want), "kept", len(tiles), "sheets", n)

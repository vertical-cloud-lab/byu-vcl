#!/usr/bin/env python3
"""The atomizer-automation clips (#353) joined in the order of a run's turnaround, with a title card before each, and
the PR's sheets and BoM.

    python3 atom_reel.py            # out/mp4/atom_reel.mp4 + out/atom/atom_reel.json (chapters), from the clips there are
    python3 atom_reel.py sheet      # out/atom/atom_sheet.png: one still per clip
    python3 atom_reel.py bom        # out/atom/bom.json and out/atom/bom.md from out/atom/*_bom.json
    python3 atom_reel.py gifs       # any clip GIF over 4.9 MB re-made from its MP4 (640 px, fewer frames, lossy)
    python3 atom_reel.py upload     # the reel to the lab's YouTube channel, unlisted, chapters in the description,
                                    # recorded in out/youtube.json (needs YOUTUBE_UPLOAD_TOKEN_PICKLE_B64)

Clips that haven't been rendered are skipped and listed. The join re-encodes everything to 1280 x 720, 15 fps.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
ATOM = OUT / "atom"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SIZE, FPS = (1280, 720), 15

# the turnaround after a run, in order: (clip, chapter title, one line on the card)
ORDER = [
    ("atom_cameras", "The melt and the stream, watched",
     "DAL PR 189's three viewport cameras and their displays: the melt through the lid window, the stream on the plate"),
    ("atom_latch", "The furnace latch, unclamped and clamped",
     "The over-centre latch as the training video shows it: the lever, the loop, the keeper, the bolt"),
    ("atom_container", "The powder down and the container off",
     "Brushed into the container, its valve shut, one arm holding it while the other opens the clamp"),
    ("atom_vacuum", "Vacuuming the chamber",
     "The Nilfisk CFM 118EXP: the continuity check, the equalization touch, slow passes, run-on, settle"),
    ("atom_plate", "Swapping the plate",
     "The door, the upper sonotrode off, the plate to its alloy's slot, the new plate at 50 N·m, the wet test"),
    ("atom_crucible_out", "Taking the furnace apart",
     "Thermocouple, sealing rod, insulation; the crucible off its graphite nut, held from below"),
    ("atom_bn", "Cleaning the crucible and recoating it with BN",
     "Skull out, loose coat scraped back, dust vacuumed; light BN passes in the hood; overnight; the check"),
    ("atom_crucible_in", "The rebuild, and the graphite nut from below",
     "Nozzle, holder, seal, insulation; the crucible into the coil; the nut threaded on while the crucible is held"),
]


def card(title: str, line: str, k: int, n: int) -> Image.Image:
    im = Image.new("RGB", SIZE, (250, 250, 250))
    d = ImageDraw.Draw(im)
    f1, f2, f3 = ImageFont.truetype(FONT_B, 44), ImageFont.truetype(FONT, 26), ImageFont.truetype(FONT, 22)
    d.text((80, 250), f"Automating the atomizer, {k} of {n}", font=f3, fill=(120, 120, 120))
    d.text((80, 290), title, font=f1, fill=(20, 20, 20))
    words, rows, cur = line.split(), [], ""
    for w in words:
        if d.textlength(cur + " " + w, font=f2) > SIZE[0] - 160:
            rows.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    rows.append(cur)
    for i, r in enumerate(rows):
        d.text((80, 370 + 36 * i), r, font=f2, fill=(60, 60, 60))
    d.rectangle((80, 352, 260, 356), fill=(178, 34, 34))
    return im


def duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def reel():
    have = [(c, t, l) for c, t, l in ORDER if (OUT / "mp4" / f"{c}.mp4").exists()]
    missing = [c for c, _, _ in ORDER if (OUT / "mp4" / f"{c}.mp4").exists() is False]
    if not have:
        sys.exit("no clips rendered yet")
    tmp = Path(tempfile.mkdtemp(prefix="atom_reel_"))
    parts, chapters, t = [], [], 0.0
    for k, (c, title, line) in enumerate(have, 1):
        png = tmp / f"card{k}.png"
        card(title, line, k, len(have)).save(png)
        cp = tmp / f"card{k}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(png), "-t", "2.5", "-r", str(FPS),
                        "-vf", f"scale={SIZE[0]}:{SIZE[1]},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "20", "-threads", "2", str(cp)], check=True)
        clip = tmp / f"clip{k}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(OUT / "mp4" / f"{c}.mp4"), "-r", str(FPS),
                        "-vf", f"scale={SIZE[0]}:{SIZE[1]},format=yuv420p", "-an", "-c:v", "libx264", "-preset",
                        "veryfast", "-crf", "21", "-threads", "2", str(clip)], check=True)
        chapters.append(dict(clip=c, title=title, start_s=round(t, 1)))
        t += duration(cp) + duration(clip)
        parts += [cp, clip]
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    dst = OUT / "mp4" / "atom_reel.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)
    ATOM.mkdir(parents=True, exist_ok=True)
    meta = dict(file=str(dst.relative_to(HERE)), duration_s=round(t, 1), chapters=chapters, missing=missing)
    (ATOM / "atom_reel.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"{dst}: {t / 60:.1f} min, {len(have)} clips, {dst.stat().st_size / 1e6:.1f} MB; missing: {missing}")
    for ch in chapters:
        m, s = divmod(int(ch["start_s"]), 60)
        print(f"{m}:{s:02d} {ch['title']}")


def sheet():
    tiles = []
    for c, title, _ in ORDER:
        p = OUT / f"{c}_still.png"
        if p.exists():
            tiles.append((title, Image.open(p).convert("RGB")))
    if not tiles:
        sys.exit("no stills yet")
    tw, th, cols = 640, 360, 2
    rows = (len(tiles) + cols - 1) // cols
    im = Image.new("RGB", (tw * cols, (th + 34) * rows), "white")
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_B, 20)
    for i, (title, t) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 34)
        im.paste(t.resize((tw, th), Image.LANCZOS), (x, y + 34))
        d.text((x + 10, y + 6), f"{i + 1}. {title}", font=f, fill=(20, 20, 20))
    ATOM.mkdir(parents=True, exist_ok=True)
    im.save(ATOM / "atom_sheet.png", optimize=True)
    print(ATOM / "atom_sheet.png", len(tiles), "tiles")


def bom():
    rows = []
    for p in sorted(ATOM.glob("*_bom.json")):
        topic = p.stem.replace("_bom", "")
        try:
            items = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            print(f"skipping {p.name}: {e}")
            continue
        if isinstance(items, dict):
            items = items.get("items", [])
        for it in items:
            rows.append(dict(topic=topic, **it))
    (ATOM / "bom.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    tot_buy = sum((r.get("unit_usd") or 0) * (r.get("qty") or 1) for r in rows if str(r.get("status", "")).startswith("to buy"))
    lines = ["| For | Item | Maker / part no. | Qty | Unit (USD) | Status | Source |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        src = r.get("source") or ""
        src = f"[link]({src})" if str(src).startswith("http") else src
        u = r.get("unit_usd")
        lines.append(f"| {r['topic']} | {r.get('item', '')} | {r.get('maker', '') or ''} {r.get('part_no', '') or ''} | "
                     f"{r.get('qty', '')} | {'' if u is None else f'{u:,.0f}'} | {r.get('status', '')} | {src} |")
    lines.append(f"\nPriced items still to buy: about ${tot_buy:,.0f} (items without a price are not counted).")
    (ATOM / "bom.md").write_text("\n".join(lines) + "\n")
    print(f"{len(rows)} BoM rows; to buy, priced: ${tot_buy:,.0f}")


def gifs(limit_mb: float = 4.9):
    """Re-make a clip's GIF from its MP4 when scene.py's GIF came out too big for GitHub to show comfortably."""
    for c, _, _ in ORDER:
        g, m = OUT / f"{c}.gif", OUT / "mp4" / f"{c}.mp4"
        if not g.exists() or not m.exists() or g.stat().st_size <= limit_mb * 1e6:
            continue
        for w, fps, lossy in ((640, 6, 80), (560, 5, 100), (480, 4, 120)):
            tmp = Path(tempfile.mkdtemp(prefix="atom_gif_"))
            pal = tmp / "pal.png"
            vf = f"fps={fps},scale={w}:-2:flags=lanczos"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(m), "-vf", vf + ",palettegen=max_colors=128",
                            str(pal)], check=True)
            raw = tmp / "raw.gif"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(m), "-i", str(pal), "-lavfi",
                            vf + " [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=4", str(raw)], check=True)
            subprocess.run(["gifsicle", "-O3", f"--lossy={lossy}", "-o", str(g), str(raw)], check=True)
            if g.stat().st_size <= limit_mb * 1e6:
                break
        print(f"{g.name}: {g.stat().st_size / 1e6:.2f} MB ({w} px, {fps} fps)")


def upload():
    import datetime as dt
    import youtube_upload as YU
    sys.path.insert(0, str(HERE.parent))
    from googleapiclient.http import MediaFileUpload
    from youtube.yt_service import get_youtube_service

    rel = "atom_reel.mp4"
    meta = json.loads((ATOM / "atom_reel.json").read_text())
    rec = YU.load_record()
    digest = YU.sha256(OUT / "mp4" / rel)
    if YU.current(rec, rel, digest):
        sys.exit("already up: " + YU.current(rec, rel, digest)["id"])
    commit = YU.commit_of(rel)
    chap = []
    for ch in meta["chapters"]:
        m, s_ = divmod(int(ch["start_s"]), 60)
        chap.append(f"{m}:{s_:02d} {ch['title']}")
    branch = "claude/issue-303-atomizer-automation"
    text = ("Automating the AMAZEMET rePowder ultrasonic atomizer with two mobile manipulators (MiR250 + UR10e): every "
            "manual step of the lab's turnaround after a run, from the lab's own SOP (vertical-cloud-lab/"
            "digital-alloy-lab PRs 253, 178, 220, 189; byu-vcl PR 80). Rendered from CAD models, not filmed. "
            "Tools and fixtures marked ours are designs, not built.\n\n" + "\n".join(chap) +
            f"\n\nCode, notes and sources: https://github.com/{YU.REPO}/tree/{commit}/vertical-lab "
            f"(notes/atomizer_automation.md, notes/atom_*.md)\n\nPull request: https://github.com/{YU.REPO}/pull/353")
    title = "Vertical cloud lab: automating the atomizer, the turnaround after a run (3-D animation)"
    yt = get_youtube_service("upload")
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    if me != YU.CHANNEL:
        sys.exit("wrong channel")
    body = {"snippet": {"title": title[:100], "description": YU.fit_bytes(text, YU.DESC_BYTES), "tags": YU.TAGS,
                        "categoryId": "28", "defaultLanguage": "en"},
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False, "embeddable": True}}
    media = MediaFileUpload(str(OUT / "mp4" / rel), mimetype="video/mp4", chunksize=8 << 20, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=False)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["videos"].setdefault(rel, []).append(dict(id=resp["id"], sha256=digest, bytes=(OUT / "mp4" / rel).stat().st_size,
                                                  commit=commit, uploaded=now, title=title, privacy="unlisted",
                                                  branch=branch))
    YU.save_record(rec)
    print("https://www.youtube.com/watch?v=" + resp["id"])


if __name__ == "__main__":
    {"sheet": sheet, "bom": bom, "upload": upload, "gifs": gifs}.get(sys.argv[1] if len(sys.argv) > 1 else "", reel)()

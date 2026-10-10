"""Pair every video moment cited in sop.md with a frame from that moment.

Scans sop.md for the embed links (youtube.com/embed/<id>?start=<s>), grabs one frame at that second from the local 360p
copy of the video (ffmpeg -ss), saves it 320 px wide under keyframes/sop/, and writes keyframes/sop-frames.md: a table of
step text | frame | links, in the order the SOP cites them. Frames are the caption start time, so they show the scene
within a few seconds of the words."""
import os, re, subprocess, json, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl")
sop = open(f"{ROOT}/sop.md", encoding="utf-8").read()
meta = {v["id"]: v for v in json.load(open(f"{ROOT}/videos.json"))}
links = re.findall(r"\[([^\]]+)\]\(https://www\.youtube\.com/embed/([A-Za-z0-9_-]{11})\?start=(\d+)\)", sop)
os.makedirs(f"{ROOT}/keyframes/sop", exist_ok=True)
rows, seen, missing = [], set(), 0
for text, vid, s in links:
    key = (vid, int(s))
    if key in seen: continue
    seen.add(key)
    out = f"{ROOT}/keyframes/sop/{vid}_{int(s):05d}.jpg"
    src = f"{DL}/{vid}.v360.mp4"
    if not os.path.exists(out) and os.path.exists(src):
        subprocess.run(["ffmpeg", "-v", "error", "-ss", str(int(s)), "-i", src, "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "6", out], capture_output=True)
    ok = os.path.exists(out)
    missing += 0 if ok else 1
    mm = f"{int(s)//60:02d}:{int(s)%60:02d}"
    img = f"![{vid} {mm}](sop/{os.path.basename(out)})" if ok else "_(video not downloaded yet)_"
    rows.append(f"| {html.escape(text)} | {img} | {meta.get(vid, {}).get('title', vid)} · [{mm} paused](https://www.youtube.com/embed/{vid}?start={s}) · [▶](https://www.youtube.com/watch?v={vid}&t={s}s) |")
md = ["# Frames for every moment the SOP cites", "",
      f"One frame per unique video moment linked from [`../sop.md`](../sop.md), grabbed at the cited second from the 360p copy ({len(rows)} moments, {missing} without a local video yet). "
      "The frame is from the caption start time, so it shows what was on screen when the sentence began; use the paused link to watch it.", "",
      "| SOP reference | frame | video · links |", "| --- | --- | --- |"] + rows
open(f"{ROOT}/keyframes/sop-frames.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
print(len(rows), "moments,", missing, "missing")

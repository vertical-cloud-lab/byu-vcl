"""Write keyframes/README.md: one contact sheet per video (scene changes + one frame every 2 min), in run order."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KF = os.environ.get("ATOMIZER_KF", "/tmp/work/keyframes")
videos = {v["id"]: v for v in json.load(open(f"{ROOT}/videos.json"))}
order = [l.strip() for l in open(f"{HERE}/video_ids.txt") if l.strip()]
out = ["# Keyframes", "",
       "One contact sheet per video: every scene change ffmpeg detects (`select=gt(scene,0.3)`, thinned to about one per minute) plus one frame "
       "every two minutes, each tile labelled with its `mm:ss`. They are a visual table of contents for [`../timestamps.md`](../timestamps.md): find the "
       "moment on the sheet, then open the paused link with the same time. [`sop-frames.md`](sop-frames.md) has one frame for every moment the SOP cites.",
       "", "Frames are 360p (the Pi-fetched copy), good enough to recognise a scene, not to read the HMI. Regenerate with `tools/keyframes.py`.", ""]
for vid in order:
    v = videos[vid]; sheet = f"{ROOT}/keyframes/{vid}_sheet.jpg"; idx = f"{KF}/{vid}.json"
    n = len(json.load(open(idx))["frames"]) if os.path.exists(idx) else 0
    out.append(f"## {v['title']}")
    out.append(f"`{vid}` · {v['published'][:10]} · {n} frames · [open paused](https://www.youtube.com/embed/{vid}?start=0) · [▶ watch](https://www.youtube.com/watch?v={vid})")
    out.append("")
    out.append(f"![{v['title']}]({vid}_sheet.jpg)" if os.path.exists(sheet) else "_sheet not generated yet_")
    out.append("")
open(f"{ROOT}/keyframes/README.md", "w", encoding="utf-8").write("\n".join(out))
print("keyframes/README.md written")

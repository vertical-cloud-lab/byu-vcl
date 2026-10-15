"""Write keyframes/README.md: one contact sheet per video (scene changes + one frame every 2 min), in run order.
Frame counts come from the per-video index JSONs that tools/keyframes.py writes to $ATOMIZER_KF (default /tmp/work/keyframes)."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KF = os.environ.get("ATOMIZER_KF", "/tmp/work/keyframes")
videos = {v["id"]: v for v in json.load(open(f"{ROOT}/videos.json"))}
order = [l.strip() for l in open(f"{HERE}/video_ids.txt") if l.strip()]
out = ["# Keyframes", "",
       "One contact sheet per video: every scene change ffmpeg detects (`select=gt(scene,0.3)`, thinned to about one per minute) plus one frame "
       "every two minutes, each tile labelled with the `mm:ss` of its own frame. A scene change keeps ffmpeg's timestamp for that frame, and the "
       "two-minute frames are taken with an accurate seek at exactly 00:00, 02:00, 04:00, …, so every label is the true time of the frame above it "
       "(a frame less than 8 s after the previous tile is left out). They are a visual table of contents for [`../timestamps.md`](../timestamps.md): "
       "find the moment on the sheet, then open the paused link with the same time. [`sop-frames.md`](sop-frames.md) has one frame for every moment the SOP cites.",
       "", "Frames come from the Pi-fetched low-resolution copies (640×360 for landscape videos, 144×256 for portrait phone videos), good enough to recognise a scene, not to read the HMI; full-resolution frames of a given moment can be pulled with `tools/hls_sections.py`. Regenerate the sheets with `tools/keyframes.py` "
       "and this page with `tools/make_keyframes_readme.py`.", ""]
for vid in order:
    v = videos[vid]; sheet = f"{ROOT}/keyframes/{vid}_sheet.jpg"; idx = f"{KF}/{vid}.json"
    if not os.path.exists(idx): raise SystemExit(f"{idx} missing: run tools/keyframes.py first (the frame counts must match the sheets)")
    n = len(json.load(open(idx))["frames"])
    out.append(f"## {v['title']}")
    out.append(f"`{vid}` · {v['published'][:10]} · {n} frames · [open paused](https://www.youtube.com/embed/{vid}?start=0) · [▶ watch](https://www.youtube.com/watch?v={vid})")
    out.append("")
    out.append(f"![{v['title']}]({vid}_sheet.jpg)" if os.path.exists(sheet) else "_sheet not generated yet_")
    out.append("")
open(f"{ROOT}/keyframes/README.md", "w", encoding="utf-8").write("\n".join(out))
print("keyframes/README.md written")

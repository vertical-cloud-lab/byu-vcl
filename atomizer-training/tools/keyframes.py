"""Keyframes + contact sheets for each downloaded 360p video. Every tile is labelled with the exact time of its frame:
- scene changes: ffmpeg `select=gt(scene,0.3)`, times from `showinfo` pts_time, thinned evenly to about one per minute (at least 12);
- one frame every 2 min, at exactly 00:00, 02:00, 04:00, ... (< duration): one accurate seek per frame (`-ss T` before `-i`
  decodes from the preceding keyframe up to T, so the frame is the one at T, not the nearest keyframe).
The two sets are merged in time order and a frame less than 8 s after the last one kept is dropped; whichever is kept keeps its own time.
Reads $ATOMIZER_DL/<id>.v360.mp4 (default /tmp/work/dl); writes 480 px wide JPEGs and <id>.json (the index) to $ATOMIZER_KF
(default /tmp/work/keyframes), and the contact sheet to $ATOMIZER_SHEETS (default ../keyframes/<id>_sheet.jpg).
Usage: python keyframes.py [id ...]   (default: every id in video_ids.txt; a video whose index JSON exists is skipped)."""
import subprocess, json, os, sys, re, glob, math
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl"); OUT = os.environ.get("ATOMIZER_KF", "/tmp/work/keyframes")
SHEETS = os.environ.get("ATOMIZER_SHEETS", f"{ROOT}/keyframes")
TITLES = {v["id"]: v["title"] for v in json.load(open(f"{ROOT}/videos.json"))}
FF = ["ffmpeg", "-nostdin", "-threads", "2"]  # 2 decoder threads: this shares a 4-core machine
def mmss(t): return f"{int(t//60):02d}:{int(t%60):02d}"
def duration(path):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path],capture_output=True,text=True).stdout.strip() or 0)
def scene(vid, path, thresh=0.30):
    d = f"{OUT}/{vid}"; os.makedirs(d, exist_ok=True)
    r = subprocess.run(FF + ["-v","info","-nostats","-i",path,"-vf",f"select='gt(scene,{thresh})',scale=480:-2,showinfo","-vsync","vfr","-q:v","4",f"{d}/s_%04d.jpg"],capture_output=True,text=True)
    times = [float(x) for x in re.findall(r"pts_time:\s*([0-9.]+)", r.stderr)]
    files = sorted(glob.glob(f"{d}/s_*.jpg"))
    return list(zip(times, files))
def periodic(vid, path, dur, every=120):
    d = f"{OUT}/{vid}"; os.makedirs(d, exist_ok=True); out = []
    for T in range(0, math.ceil(dur), every):
        f = f"{d}/p_{T:05d}.jpg"
        subprocess.run(FF + ["-v","error","-ss",str(T),"-i",path,"-frames:v","1","-vf","scale=480:-2","-q:v","4","-y",f],capture_output=True)
        if os.path.exists(f): out.append((float(T), f))
        else: print(f"  {vid}: no frame at {mmss(T)} ({T} s of {dur:.1f} s)", flush=True)
    return out
def contact_sheet(vid, frames, cols=6, tw=240):
    if not frames: return
    th = None; tiles = []
    for t, f in frames:
        im = Image.open(f); im.thumbnail((tw, tw)); tiles.append((t, im))
        th = max(th or 0, im.height)
    rows = math.ceil(len(tiles)/cols); hdr = 26; lab = 14
    sheet = Image.new("RGB", (cols*tw, hdr + rows*(th+lab)), "white")
    dr = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12); fontb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception: font = fontb = ImageFont.load_default()
    dr.text((6, 5), f"{TITLES.get(vid, vid)}  —  youtu.be/{vid}  ({len(tiles)} frames: scene changes + every 2 min)", fill="black", font=fontb)
    for i, (t, im) in enumerate(tiles):
        x = (i % cols)*tw; y = hdr + (i//cols)*(th+lab)
        sheet.paste(im, (x, y)); dr.text((x+3, y+th), mmss(t), fill="black", font=font)
    os.makedirs(SHEETS, exist_ok=True)
    sheet.save(f"{SHEETS}/{vid}_sheet.jpg", quality=80, optimize=True)
def run(vid):
    path = f"{DL}/{vid}.v360.mp4"
    if not os.path.exists(path) or os.path.exists(f"{OUT}/{vid}.json"): return False
    for f in glob.glob(f"{OUT}/{vid}/[sp]_*.jpg"): os.remove(f)  # stale frames from an interrupted run would be globbed in
    dur = duration(path)
    sc = scene(vid, path)
    # cap scene frames to ~1 per minute by thinning evenly
    cap = max(12, int(dur/60))
    if len(sc) > cap:
        step = len(sc)/cap; sc = [sc[int(i*step)] for i in range(cap)]
    pe = periodic(vid, path, dur)
    kind = {f: k for k, fs in (("scene", sc), ("periodic", pe)) for _, f in fs}
    frames = sorted(sc + pe, key=lambda x: x[0])
    # drop near-duplicates within 8 s (every time is exact, so the frame kept carries its own time)
    kept = []
    for t, f in frames:
        if kept and t - kept[-1][0] < 8: continue
        kept.append((t, f))
    json.dump({"video_id": vid, "duration": dur, "frames": [{"t": round(t,2), "mmss": mmss(t), "kind": kind[f], "file": os.path.relpath(f, OUT)} for t, f in kept]}, open(f"{OUT}/{vid}.json","w"), indent=0)
    contact_sheet(vid, kept)
    print(vid, f"{dur/60:.1f} min", len(sc), "scene +", len(pe), "periodic ->", len(kept), "kept", flush=True)
    return True
if __name__ == "__main__":
    ids = sys.argv[1:] or [l.strip() for l in open(f"{HERE}/video_ids.txt") if l.strip()]
    for vid in ids: run(vid)

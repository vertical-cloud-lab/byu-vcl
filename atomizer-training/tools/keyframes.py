"""Keyframes + contact sheets for each downloaded 360p video.
scene-change frames (ffmpeg select) + one frame every 2 min; 480 px wide JPEGs; index.json; one contact sheet per video."""
import subprocess, json, os, sys, re, glob, math
from PIL import Image, ImageDraw, ImageFont
DL = "/tmp/work/dl"; OUT = "/tmp/work/keyframes"
TITLES = {v["id"]: v["title"] for v in json.load(open("/tmp/work/channel_videos.json"))}
def mmss(t): return f"{int(t//60):02d}:{int(t%60):02d}"
def duration(path):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",path],capture_output=True,text=True).stdout.strip() or 0)
def scene(vid, path, thresh=0.30):
    d = f"{OUT}/{vid}"; os.makedirs(d, exist_ok=True)
    r = subprocess.run(["ffmpeg","-v","info","-nostats","-i",path,"-vf",f"select='gt(scene,{thresh})',scale=480:-2,showinfo","-vsync","vfr","-q:v","4",f"{d}/s_%04d.jpg"],capture_output=True,text=True)
    times = [float(x) for x in re.findall(r"pts_time:\s*([0-9.]+)", r.stderr)]
    files = sorted(glob.glob(f"{d}/s_*.jpg"))
    return list(zip(times, files))
def periodic(vid, path, every=120):
    d = f"{OUT}/{vid}"; os.makedirs(d, exist_ok=True)
    subprocess.run(["ffmpeg","-v","error","-skip_frame","nokey","-i",path,"-vf",f"fps=1/{every},scale=480:-2","-q:v","4",f"{d}/p_%04d.jpg"],capture_output=True)
    files = sorted(glob.glob(f"{d}/p_*.jpg"))
    return [(i*every, f) for i, f in enumerate(files)]
def contact_sheet(vid, frames, cols=6, tw=240):
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
    sheet.save(f"{OUT}/{vid}_sheet.jpg", quality=80, optimize=True)
def run(vid):
    path = f"{DL}/{vid}.v360.mp4"
    if not os.path.exists(path) or os.path.exists(f"{OUT}/{vid}.json"): return False
    dur = duration(path)
    sc = scene(vid, path)
    # cap scene frames to ~1 per minute by thinning evenly
    cap = max(12, int(dur/60))
    if len(sc) > cap:
        step = len(sc)/cap; sc = [sc[int(i*step)] for i in range(cap)]
    pe = periodic(vid, path)
    frames = sorted(sc + pe, key=lambda x: x[0])
    # drop near-duplicates within 8 s
    kept = []
    for t, f in frames:
        if kept and t - kept[-1][0] < 8: continue
        kept.append((t, f))
    json.dump({"video_id": vid, "duration": dur, "frames": [{"t": round(t,2), "mmss": mmss(t), "file": os.path.relpath(f, OUT)} for t, f in kept]}, open(f"{OUT}/{vid}.json","w"), indent=0)
    contact_sheet(vid, kept)
    print(vid, f"{dur/60:.1f} min", len(sc), "scene +", len(pe), "periodic ->", len(kept), "kept", flush=True)
    return True
if __name__ == "__main__":
    ids = sys.argv[1:] or [l.strip() for l in open("/tmp/work/ids.txt") if l.strip()]
    for vid in ids: run(vid)

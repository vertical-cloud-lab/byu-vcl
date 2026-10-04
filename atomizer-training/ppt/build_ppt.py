"""Build the slide versions of the 3D step animations: one short caption at a time, a short spoken line for each, and the
animation at its own speed (the same as in the tutorials' GIFs and videos).

Input: ../viz3d/out/clean/<name>.mp4 and .json, the animation rendered with no text at all, at 1920 x 1080 and 30 fps:

    cd ../viz3d && VIZ3D_CLEAN=1 VIZ3D_SIZE=1920x1080 VIZ3D_FPS=30 \\
        xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py 03_furnace_load 02_stack

Captions and narration: captions.py, which also holds the rules this checks before building. Voice: Microsoft Edge TTS,
the tutorials' VOICE (../tutorials/scripts.py), at 1x. Output: videos/<name>.mp4 (1920 x 1080, 30 fps, h264 + aac;
committed, so they can go straight into a slide), script.md (every caption with its times, and how long its line takes)
and <name>_sheet.jpg (one frame per caption, for checking).

    python build_ppt.py                         # both
    python build_ppt.py 02_stack                # one
    python build_ppt.py --check                 # rules and timing only: needs the .json and the TTS, not the MP4
    python build_ppt.py upload --ref <sha>      # upload videos/*.mp4 unlisted (upload-only token), ids into uploads.json
"""
import argparse, hashlib, json, os, subprocess, sys, time
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
sys.path.insert(0, f"{ROOT}/tutorials")
from scripts import VOICE
from captions import CLIPS, END_HOLD, LEAD, MAX_WORDS, MIN_DWELL, SPARE

CLEAN = f"{ROOT}/viz3d/out/clean"
OUT = f"{HERE}/videos"; TMP = f"{HERE}/tmp"; LOG = f"{HERE}/uploads.json"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
NAVY = (30, 60, 140)                                            # the animations' step-label colour
AUDIO = "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100"         # as the tutorials
PR = "https://github.com/vertical-cloud-lab/byu-vcl/pull/255"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd))[:600] + "\n" + r.stderr[-2500:])
    return r


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)


def tts(text):
    path = f"{TMP}/tts_{hashlib.sha1((VOICE + text).encode()).hexdigest()[:12]}.mp3"
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        run(["edge-tts", "--voice", VOICE, "--text", text, "--write-media", path])
    return path, duration(path)


def ts(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def timeline(name, approx=False):
    """(meta, rows, end): each caption's start and end (s, on frame boundaries), and the video's length. approx=True
    falls back to the committed 15 fps timing (../viz3d/out/<name>.json, within a frame or two) if there is no render."""
    path = f"{CLEAN}/{name}.json"
    if approx and not os.path.exists(path):
        print(f"{name}: no clean render yet, using the 15 fps timing", flush=True)
        path = f"{ROOT}/viz3d/out/{name}.json"
    meta = json.load(open(path))
    fps = meta["fps"]
    start = {s["label"]: s["start_frame"] / fps for s in meta["substeps"]}
    lines = CLIPS[name]["lines"]
    t = [0.0] + [round((start[lab] + off) * fps) / fps for lab, off, _, _ in lines[1:]]
    end = meta["n_frames"] / fps + END_HOLD
    rows = [dict(label=lab, caption=cap, narration=nar, start=t[k], end=t[k + 1] if k + 1 < len(t) else end)
            for k, (lab, off, cap, nar) in enumerate(lines)]
    for r in rows:
        r["mp3"], r["speech"] = tts(r["narration"])
    return meta, rows, end


def check(name, rows):
    errs = []
    for k, r in enumerate(rows, 1):
        words, dwell = len(r["caption"].split()), r["end"] - r["start"]
        if words > MAX_WORDS:
            errs.append(f"{name} #{k} '{r['caption']}': {words} words (max {MAX_WORDS})")
        if dwell < MIN_DWELL - 1e-6:
            errs.append(f"{name} #{k} '{r['caption']}': up {dwell:.2f} s (min {MIN_DWELL})")
        if LEAD + r["speech"] > dwell - SPARE:
            errs.append(f"{name} #{k}: the line takes {r['speech']:.2f} s, the caption is up {dwell:.2f} s")
    return errs


def caption_png(text, path, W, H):
    """One caption: white bold text on a navy pill, centred near the bottom of a transparent full frame."""
    s = H / 1080
    f = ImageFont.truetype(FONTB, int(round(60 * s)))
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tw = d.textlength(text, font=f)
    padx, pady = 40 * s, 18 * s
    bw, bh = tw + 2 * padx, asc + desc + 2 * pady
    x0, y0 = (W - bw) / 2, H - 60 * s - bh
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=20 * s, fill=NAVY + (238,), outline=(255, 255, 255, 235),
                        width=max(1, round(3 * s)))      # the outline keeps it apart from the blue frame
    d.text((x0 + padx, y0 + pady), text, font=f, fill=(255, 255, 255), anchor="la")
    img.save(path)


def build(name):
    meta, rows, end = timeline(name)
    errs = check(name, rows)
    if errs:
        raise SystemExit("\n".join(errs))
    W, H = meta["size"]; fps = meta["fps"]
    src, out = f"{CLEAN}/{name}.mp4", f"{OUT}/{name}.mp4"
    half = 0.5 / fps                       # switch captions between frames, never on one
    inputs, fc = ["-i", src], [f"[0:v]tpad=stop_mode=clone:stop_duration={END_HOLD}[v0]"]
    for k, r in enumerate(rows):
        png = f"{TMP}/{name}_cap{k}.png"
        caption_png(r["caption"], png, W, H)
        inputs += ["-i", png]
        fc.append(f"[v{k}][{k + 1}:v]overlay=0:0:enable='gte(t,{r['start'] - half:.4f})*lt(t,{r['end'] - half:.4f})'"
                  f"[v{k + 1}]")
    fc.append(f"[v{len(rows)}]format=yuv420p[vout]")
    for k, r in enumerate(rows):
        inputs += ["-i", r["mp3"]]
        ms = int(round((r["start"] + LEAD) * 1000))
        fc.append(f"[{len(rows) + 1 + k}:a]adelay={ms}|{ms}[a{k}]")
    fc.append("".join(f"[a{k}]" for k in range(len(rows))) + f"amix=inputs={len(rows)}:normalize=0,apad,{AUDIO}[aout]")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
         "-t", f"{end:.4f}", "-r", str(fps), "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", "-movflags", "+faststart",
         out])
    sheet(name, rows, out)
    print(f"{name}: {duration(out):.2f} s, {os.path.getsize(out) / 1e6:.1f} MB -> {out}", flush=True)
    return rows, end


def sheet(name, rows, mp4, cols=4, tw=480):
    """A frame from each caption (1.5 s in, or just before it ends), labelled with its time."""
    th = tw * 9 // 16
    tiles = []
    for k, r in enumerate(rows):
        t = min(r["start"] + 1.5, r["end"] - 0.2)
        png = f"{TMP}/{name}_tile{k}.png"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-vf", f"scale={tw}:{th}",
             png])
        im = Image.open(png).convert("RGB")
        d = ImageDraw.Draw(im)
        lab = f"{k + 1} · {ts(r['start'])}–{ts(r['end'])}"
        f = ImageFont.truetype(FONT, 15)
        d.rectangle((0, 0, d.textlength(lab, font=f) + 12, 22), fill=(255, 255, 255))
        d.text((6, 3), lab, font=f, fill=(20, 20, 24))
        tiles.append(im)
    rows_n = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * tw + (cols - 1) * 4, rows_n * th + (rows_n - 1) * 4), (255, 255, 255))
    for i, im in enumerate(tiles):
        out.paste(im, ((i % cols) * (tw + 4), (i // cols) * (th + 4)))
    out.save(f"{HERE}/{name}_sheet.jpg", quality=85, optimize=True)


def script_md(done):
    """script.md: every caption, when it is up, its line and how long that takes."""
    md = ["# Slide clips: captions, narration and timing", "",
          f"Generated by `build_ppt.py` from [`captions.py`](captions.py). Rules: at most {MAX_WORDS} words a caption, "
          f"each up at least {MIN_DWELL:g} s; each line starts {LEAD:g} s after its caption and ends at least "
          f"{SPARE:g} s before the next. Times are in the video, m:ss.s; the animation runs at its own speed, and the "
          f"last frame is held {END_HOLD:g} s.", ""]
    for name, (rows, end) in done.items():
        c = CLIPS[name]
        dw = [r["end"] - r["start"] for r in rows]
        md += [f"## {c['title']}", "", f"`{name}`, {ts(end)} long. {len(rows)} captions, up {min(dw):.1f}–{max(dw):.1f} s "
               f"each; at most {max(len(r['caption'].split()) for r in rows)} words.", "",
               "| # | Caption (words) | Up | For | Narration | Spoken | Spare |", "|---|---|---|---|---|---|---|"]
        for k, r in enumerate(rows, 1):
            a = r["start"] + LEAD
            md.append(f"| {k} | {r['caption']} ({len(r['caption'].split())}) | {ts(r['start'])}–{ts(r['end'])} | "
                      f"{r['end'] - r['start']:.1f} s | {r['narration']} | {ts(a)}–{ts(a + r['speech'])} | "
                      f"{r['end'] - a - r['speech']:.1f} s |")
        md += ["", f"![{name}]({name}_sheet.jpg)", ""]
    open(f"{HERE}/script.md", "w").write("\n".join(md))


def describe(name, ref, rows):
    c = CLIPS[name]
    tut = json.load(open(f"{ROOT}/tutorials/uploads.json"))["draft 4"]["01-before"]["url"]
    blob = f"https://github.com/vertical-cloud-lab/byu-vcl/blob/{ref}/atomizer-training"
    lines = [c["summary"], "",
             f"For slides: one short caption at a time (at most {MAX_WORDS} words, each up at least {MIN_DWELL:g} s), a "
             "short spoken line for each, and the animation at its own speed. Draft for review.", ""]
    lines += [f"{int(r['start'] // 60)}:{int(r['start'] % 60):02d} {r['caption']}" for r in rows]
    lines += ["", "3D model in CadQuery, rendered with PyVista, built from the training videos and AMAZEMET's "
              "documents; parts move along their real assembly paths. Narration: Microsoft Edge TTS " + VOICE +
              " at 1x.", "",
              f"The whole step, with Bartosz Kalicki (AMAZEMET) explaining it: Atomizer tutorial 1, before a run: {tut}",
              "", f"Script and timing: {blob}/ppt/script.md", f"Captions: {blob}/ppt/captions.py",
              f"SOP: {blob}/sop.md", f"Pull request: {PR}"]
    desc = "\n".join(lines)
    assert "<" not in desc and ">" not in desc and len(desc) <= 5000 and len(c["title"]) <= 100, name
    return desc


def upload(ref, names):
    sys.path.append(REPO)
    sys.path.insert(1, f"{ROOT}/playlist")
    from youtube.yt_service import upload_video
    from catalog import TAGS
    log = json.load(open(LOG)) if os.path.exists(LOG) else {}
    for name in names:
        if name in log:
            print(name, "already uploaded:", log[name]["url"]); continue
        path = f"{OUT}/{name}.mp4"
        _, rows, _ = timeline(name)
        title = CLIPS[name]["title"]
        print("uploading", name, title, flush=True)
        vid = upload_video(path, title, describe(name, ref, rows), privacy="unlisted", tags=TAGS + ["slides", "animation"])
        log[name] = {"video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                     "uploaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "privacy": "unlisted",
                     "size_bytes": os.path.getsize(path), "links_ref": ref}
        json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
        print(name, "->", log[name]["url"], flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="animations (default: all in captions.py), or 'upload'")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--ref", help="for upload: the pushed commit the description's links point at")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    if args.names[:1] == ["upload"]:
        if not args.ref:
            raise SystemExit("upload needs --ref <pushed commit>")
        return upload(args.ref, args.names[1:] or list(CLIPS))
    names = args.names or list(CLIPS)
    if args.check:
        bad = []
        for name in names:
            _, rows, end = timeline(name, approx=True)
            bad += check(name, rows)
            for k, r in enumerate(rows, 1):
                print(f"{name} {k:2d} {ts(r['start'])}-{ts(r['end'])} up {r['end'] - r['start']:4.1f}s "
                      f"speech {r['speech']:4.2f}s spare {r['end'] - r['start'] - LEAD - r['speech']:4.2f}s "
                      f"{len(r['caption'].split())}w  {r['caption']}")
        print("\n".join(bad) or "all rules met")
        return
    done = {name: build(name) for name in names}
    if set(done) == set(CLIPS):
        script_md(done)


if __name__ == "__main__":
    main()

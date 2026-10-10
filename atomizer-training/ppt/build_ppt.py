"""Build the slide versions of the 3D step animations: one short caption at a time and a short spoken line for each.
The single-step clips run the animation at its own speed (the same as in the tutorials' GIFs and videos); the summary is
one condensed take through the furnace, the stack, the melt and the pour (../viz3d/steps.py anim_summary).

Input: ../viz3d/out/clean/<name>.mp4 and .json, the animation rendered with no text at all, at 1920 x 1080 and 30 fps:

    cd ../viz3d && VIZ3D_CLEAN=1 VIZ3D_SIZE=1920x1080 VIZ3D_FPS=30 \\
        xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py 03_furnace_load 02_stack summary

Captions and narration: captions.py, which also holds the rules this checks before building. Voice: Microsoft Edge TTS,
the tutorials' VOICE (../tutorials/scripts.py), at 1x. Output: videos/<name>.mp4 (1920 x 1080, 30 fps, h264 + aac;
committed, so they can go straight into a slide), script.md (every caption with its times, and how long its line takes)
and <name>_sheet.jpg (one frame per caption, for checking).

    python build_ppt.py                         # all of them
    python build_ppt.py summary                 # one (script.md keeps the others' sections as they are)
    python build_ppt.py --check                 # rules and timing only: needs the .json and the TTS, not the MP4
    python build_ppt.py upload --ref <sha>      # upload videos/*.mp4 unlisted (upload-only token), ids into uploads.json
    python build_ppt.py animations [names]      # the ten step animations as they are, into videos/animations/ (below)

`animations` takes the 1080p30 renders that ../viz3d writes with VIZ3D_HD=1 (out/hd/<name>.mp4 with the GIF's text,
out/clean/<name>.mp4 without), checks each pair against its timing, and copies them to videos/animations/<name>.mp4 and
<name>_no_text.mp4, with animations_sheet.jpg showing a frame of each. No captions or narration are added.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time
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


def end_hold(name):
    return CLIPS[name].get("end_hold", END_HOLD)


def timeline(name, approx=False):
    """(meta, rows, end): each caption's start and end (s, on frame boundaries), and the video's length. approx=True
    falls back to the committed 15 fps timing (../viz3d/out/<name>.json, within a frame or two) if there is no render."""
    path = f"{CLEAN}/{name}.json"
    if approx and not os.path.exists(path):
        print(f"{name}: no clean render yet, using the 15 fps timing", flush=True)
        path = f"{ROOT}/viz3d/out/{name}.json"
    if not os.path.exists(path):
        raise SystemExit(f"{name}: no timing in {path}; render it first (see the docstring)")
    meta = json.load(open(path))
    fps = meta["fps"]
    start = {s["label"]: s["start_frame"] / fps for s in meta["substeps"]}
    lines = CLIPS[name]["lines"]
    t = [0.0] + [round((start[lab] + off) * fps) / fps for lab, off, _, _ in lines[1:]]
    end = meta["n_frames"] / fps + end_hold(name)
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
    inputs, fc = ["-i", src], [f"[0:v]tpad=stop_mode=clone:stop_duration={end_hold(name)}[v0]"]
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
    split(name, meta, end)
    return rows, end


PART_HOLD = 0.5          # s each part but the last ends on (the last has the clip's own end hold)


def parts(name, meta, end):
    """[(file, start, end)]: the clip cut where the sub-steps in CLIPS[name]["parts"] start (each one a caption's start,
    so no line is cut), one step per slide."""
    ps = CLIPS[name].get("parts", [])
    fps = meta["fps"]
    start = {s["label"]: s["start_frame"] / fps for s in meta["substeps"]}
    t = [0.0] + [start[lab] for _, lab in ps[1:]] + [end]
    return [(f"{name}_{suffix}.mp4", t[k], t[k + 1]) for k, (suffix, _) in enumerate(ps)]


def split(name, meta, end):
    fps = meta["fps"]
    for k, (fn, a, b) in enumerate(parts(name, meta, end)):
        hold = 0.0 if b >= end - 1e-6 else PART_HOLD
        vf = f"trim=start_frame={round(a * fps)}:end_frame={round(b * fps)},setpts=PTS-STARTPTS"
        af = f"atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS"
        if hold:
            vf += f",tpad=stop_mode=clone:stop_duration={hold}"
            af += f",apad=pad_dur={hold}"
        out = f"{OUT}/{fn}"
        run(["ffmpeg", "-y", "-v", "error", "-i", f"{OUT}/{name}.mp4", "-vf", vf, "-af", af, "-r", str(fps),
             "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", "-movflags", "+faststart", out])
        print(f"  part {fn}: {ts(a)}-{ts(b)} of the clip, {duration(out):.2f} s, {os.path.getsize(out) / 1e6:.1f} MB",
              flush=True)


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
    """script.md: every caption, when it is up, its line and how long that takes. Clips not built this time keep their
    section from the existing script.md."""
    old = {}
    if os.path.exists(f"{HERE}/script.md"):
        for sec in open(f"{HERE}/script.md").read().split("\n## ")[1:]:
            m = re.search(r"^`([^`]+)`, ", sec, re.M)
            if m:
                old[m.group(1)] = "## " + sec.rstrip("\n")
    md = ["# Slide clips: captions, narration and timing", "",
          f"Generated by `build_ppt.py` from [`captions.py`](captions.py). Rules: at most {MAX_WORDS} words a caption, "
          f"each up at least {MIN_DWELL:g} s; each line starts {LEAD:g} s after its caption and ends at least "
          f"{SPARE:g} s before the next. Times are in the video, m:ss.s. The single-step clips run the animation at its "
          f"own speed; the summary is condensed. The last frame is held at the end ({END_HOLD:g} s unless stated).", ""]
    for name in CLIPS:
        if name not in done:
            if name in old:
                md += [old[name], ""]
            continue
        rows, end = done[name]
        c = CLIPS[name]
        dw = [r["end"] - r["start"] for r in rows]
        md += [f"## {c['title']}", "", f"`{name}`, {ts(end)} long. {len(rows)} captions, up {min(dw):.1f}–{max(dw):.1f} s "
               f"each; at most {max(len(r['caption'].split()) for r in rows)} words."
               + (f" The last frame is held {end_hold(name):g} s." if end_hold(name) != END_HOLD else ""), ""]
        if c.get("note"):
            md += [c["note"], ""]
        md += ["| # | Caption (words) | Up | For | Narration | Spoken | Spare |", "|---|---|---|---|---|---|---|"]
        for k, r in enumerate(rows, 1):
            a = r["start"] + LEAD
            md.append(f"| {k} | {r['caption']} ({len(r['caption'].split())}) | {ts(r['start'])}–{ts(r['end'])} | "
                      f"{r['end'] - r['start']:.1f} s | {r['narration']} | {ts(a)}–{ts(a + r['speech'])} | "
                      f"{r['end'] - a - r['speech']:.1f} s |")
        if c.get("parts"):
            meta = json.load(open(f"{CLEAN}/{name}.json"))
            ps = parts(name, meta, end)
            md += ["", "Also cut into one part per step, for a slide each (each ends on a "
                   f"{PART_HOLD:g} s hold; the last keeps the clip's own):", ""]
            md += [f"- [`videos/{fn}`](videos/{fn}): {ts(a)}–{ts(b)} of the clip" for fn, a, b in ps]
        md += ["", f"![{name}]({name}_sheet.jpg)", ""]
    open(f"{HERE}/script.md", "w").write("\n".join(md))


TUTORIAL_NAMES = {"01-before": "Atomizer tutorial 1, before a run", "02-during": "Atomizer tutorial 2, during a run"}


def describe(name, ref, rows):
    c = CLIPS[name]
    drafts = json.load(open(f"{ROOT}/tutorials/uploads.json"))
    tuts = drafts[max(drafts, key=lambda d: int(d.split()[-1]))]     # the latest draft of the tutorials
    blob = f"https://github.com/vertical-cloud-lab/byu-vcl/blob/{ref}/atomizer-training"
    speed = c.get("note") or "The animation runs at its own speed."
    lines = [c["summary"], "",
             f"For slides: one short caption at a time (at most {MAX_WORDS} words, each up at least {MIN_DWELL:g} s) "
             f"and a short spoken line for each. {speed} Draft for review.", ""]
    lines += [f"{int(r['start'] // 60)}:{int(r['start'] % 60):02d} {r['caption']}" for r in rows]
    lines += ["", "3D model in CadQuery, rendered with PyVista, built from the training videos and AMAZEMET's "
              "documents; parts move along their real assembly paths. Narration: Microsoft Edge TTS " + VOICE +
              " at 1x.", ""]
    keys = c.get("tutorials", ("01-before",))
    lines.append("The whole step, with Bartosz Kalicki (AMAZEMET) explaining it:" if len(keys) == 1 else
                 "The whole steps, with Bartosz Kalicki (AMAZEMET) explaining them:")
    lines += [f"{TUTORIAL_NAMES[k]}: {tuts[k]['url']}" for k in keys]
    lines += ["", f"Script and timing: {blob}/ppt/script.md", f"Captions: {blob}/ppt/captions.py",
              f"SOP: {blob}/sop.md", f"Pull request: {PR}"]
    desc = "\n".join(lines)
    assert "<" not in desc and ">" not in desc and len(desc) <= 5000 and len(c["title"]) <= 100, name
    return desc


def script_rows(name):
    """The captions' start times as the last build wrote them to script.md, for describing an upload on a machine without
    the clean render (it is not committed): [{"caption", "start"}]."""
    sec = open(f"{HERE}/script.md").read().split(f"`{name}`, ", 1)[1].split("\n## ", 1)[0]
    rows = [dict(caption=m.group(1), start=int(m.group(2)) * 60 + float(m.group(3)))
            for m in re.finditer(r"^\| \d+ \| (.+?) \(\d+\) \| (\d+):(\d+\.\d)–", sec, re.M)]
    if len(rows) != len(CLIPS[name]["lines"]):
        raise SystemExit(f"{name}: script.md has {len(rows)} captions, captions.py {len(CLIPS[name]['lines'])}")
    return rows


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
        rows = timeline(name)[1] if os.path.exists(f"{CLEAN}/{name}.json") else script_rows(name)
        title = CLIPS[name]["title"]
        print("uploading", name, title, flush=True)
        vid = upload_video(path, title, describe(name, ref, rows), privacy="unlisted", tags=TAGS + ["slides", "animation"])
        log[name] = {"video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                     "uploaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "privacy": "unlisted",
                     "size_bytes": os.path.getsize(path), "links_ref": ref}
        json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
        print(name, "->", log[name]["url"], flush=True)


ANIMATIONS = {         # the step animations in the order of a run, as in ../viz3d/README.md
    "00_machine": "0 · Tour of the machine",
    "01_utilities": "1 · Utilities on",
    "03_furnace_load": "2a · Furnace prep and loading",
    "03b_chamber": "2b · Chamber: splash disc, container, catch bowl",
    "02_stack": "2c · Ultrasonic stack and the door",
    "04_gas_wash": "3 · Gas wash",
    "05_melt": "4 · Melt",
    "06_pour": "5 · Pour and atomize",
    "06b_oct6": "What goes wrong: the upper sonotrode under the stream (Oct 6); rendered with VIZ3D_STACK=oct6",
    "07_end_cooldown": "6–8 · End of pour, cool down, collect",
    "08_clean": "9 · Clean and reset",
}


def probe(path):
    """(width, height, frame rate, frames, has audio) of an MP4."""
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,nb_frames",
             "-of", "json", path])
    st = json.loads(r.stdout)["streams"]
    v = next(x for x in st if x["codec_type"] == "video")
    return (int(v["width"]), int(v["height"]), v["r_frame_rate"], int(v["nb_frames"]),
            any(x["codec_type"] == "audio" for x in st))


def animations(names=(), cols=2, tw=640):
    """videos/animations/: each step animation with the GIF's text and with none (all, or `names`), and a sheet with a
    frame of each one there."""
    dst = f"{OUT}/animations"
    os.makedirs(dst, exist_ok=True)
    for name in names or ANIMATIONS:
        meta = json.load(open(f"{CLEAN}/{name}.json"))
        want = (*meta["size"], f"{meta['fps']}/1", meta["n_frames"], False)
        for src, out in ((f"{ROOT}/viz3d/out/hd/{name}.mp4", f"{dst}/{name}.mp4"),
                         (f"{CLEAN}/{name}.mp4", f"{dst}/{name}_no_text.mp4")):
            got = probe(src)
            if got != want:
                raise SystemExit(f"{src}: {got}, expected {want} from {CLEAN}/{name}.json; render it again")
            shutil.copyfile(src, out)
        print(f"{name}: {ts(meta['n_frames'] / meta['fps'])}, {os.path.getsize(f'{dst}/{name}.mp4') / 1e6:.1f} MB with "
              f"text, {os.path.getsize(f'{dst}/{name}_no_text.mp4') / 1e6:.1f} MB without", flush=True)
    tiles = []
    for name in ANIMATIONS:
        if not os.path.exists(f"{dst}/{name}.mp4"):
            continue
        meta = json.load(open(f"{CLEAN}/{name}.json"))
        secs = meta["n_frames"] / meta["fps"]
        th = tw * meta["size"][1] // meta["size"][0]
        png = f"{TMP}/anim_{name}.png"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{secs * 0.55:.3f}", "-i", f"{dst}/{name}.mp4", "-frames:v", "1",
             "-vf", f"scale={tw}:{th}", png])
        im = Image.open(png).convert("RGB")
        lab = f"{name}.mp4 · {ts(secs)}"
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(FONT, 16)
        d.rectangle((0, th - 26, d.textlength(lab, font=f) + 14, th), fill=(255, 255, 255))
        d.text((7, th - 23), lab, font=f, fill=(20, 20, 24))
        tiles.append(im)
    th = tiles[0].height
    rows_n = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols - 1) * 4, rows_n * th + (rows_n - 1) * 4), (255, 255, 255))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * (tw + 4), (i // cols) * (th + 4)))
    sheet.save(f"{HERE}/animations_sheet.jpg", quality=85, optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="animations (default: all in captions.py), or 'upload', or 'animations'")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--ref", help="for upload: the pushed commit the description's links point at")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    if args.names[:1] == ["animations"]:
        return animations(args.names[1:])
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
    script_md(done)


if __name__ == "__main__":
    main()

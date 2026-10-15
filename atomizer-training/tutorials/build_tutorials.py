"""Assemble the narrated tutorial videos from the 3D step animations, the draw.io outlines and clips of the training videos.

Segment kinds (see scripts.py):
  title    — opening card over the 3D render of the machine, one short line of narration
  outline  — a draw.io diagram (diagrams/<name>.png): the tutorial's steps, or one of them highlighted as a section divider
  build    — a draw.io outline built up PowerPoint-style (diagrams/<name>_build<k>.png): the step boxes under the first
             sentence, then each step's details appear, as a hard cut, the moment the sentence naming that step starts
  anim     — a 3D step animation (../viz3d/out/mp4/<name>.mp4). Narration given as a list is timed sentence by sentence
             against the animation's sub-steps (../viz3d/out/<name>.json); the sub-step stretches if the voice needs longer
  clip     — the trainer's own words, cut from a training video: snapped to sentence boundaries with word-timed Whisper
             (clip_words.py), cut frame-exact from the 720p window of the video that covers it, stabilised (vidstab, two
             passes, zoomed in just enough to hide the moving edges, capped), subtitled from the same words,
             loudness-matched
  real     — the action itself, from the recordings (real-footage.md): cut at the pick's in and out points (its middle
             REAL_MAX seconds if longer, never through a word), stabilised like a clip, with its own sound and subtitles,
             under a bar naming what it shows
  card     — a text card with narration

Synthetic narration is Microsoft Edge TTS (VOICE in scripts.py) at 1x. Segments are joined with short crossfades (FADE),
except that a build segment is cut into and out of, like the slide changes it imitates.
Output: ./out/<tutorial>.mp4, 1280x720 h264 + aac.

    python build_tutorials.py             # all
    python build_tutorials.py 02-during   # one
Set ATOMIZER_DL to the folder holding <id>.m4a (or excerpts <id>_a<start>.m4a with a .json giving their t0) and
<id>.v360.mp4 (default /tmp/work/dl), and ATOMIZER_HLS to the folder
holding the 720p windows <id>_<start>.ts with their <id>_<start>.json (t0 = video time of the first frame; default
/tmp/work/hls). A clip that no window covers falls back to the 360p copy, with a warning. ATOMIZER_THREADS=2 caps the
threads of every ffmpeg call, for a shared machine.
"""
import glob, hashlib, json, math, os, re, shutil, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scripts import FIXES, TUTORIALS, VOICE
import clip_words

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl")
HLS = os.environ.get("ATOMIZER_HLS", "/tmp/work/hls")
THREADS = os.environ.get("ATOMIZER_THREADS", "")
if THREADS:
    os.environ.setdefault("OMP_NUM_THREADS", THREADS)          # libvidstab's own OpenMP threads
OUT = f"{HERE}/out"; TMP = f"{HERE}/tmp"; DIAG = f"{HERE}/diagrams"; V3D = f"{ROOT}/viz3d/out"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VIDEOS = {v["id"]: v for v in json.load(open(f"{ROOT}/videos.json"))}
W, H, FPS = 1280, 720, 30
FADE = 0.4
AUDIO = "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100"
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2"]
SHORT = {"wRc8p2_FnJo": "Training video 1", "naePD8o9_Gk": "Training video 2", "txH397FGTAU": "Training video 3",
         "1F9_4ccwhss": "Training video 4", "58wJ_Khwgyk": "Training video 5", "tfb4fsVNIFI": "Training video 6",
         "FDRTt68Vfvo": "Training video 7", "HTlUrAr5HVU": "Training video 8", "9kn-HhXCr1o": "Training video 9",
         "u-KjR5TENN4": "Expert cleaning, POV", "f8KL31PN8bA": "Cartridge cleaning", "2wMgeI-E7zw": "Commissioning, Sep 28",
         "qYyT39D5Yzo": "First run, Oct 2, part 1", "of5-LhkX_VQ": "First run, Oct 2, part 2", "07QOPRHIEvw": "Placing the atomizer",
         "Kv9DT3Vo0GE": "Construction update", "z6rwmQW_3Vg": "Turning Al crucibles", "Pk0K5sBz-sQ": "Training, Sep 29",
         "TFpU4uqVF9c": "Atomizing AlSi10Mg-Al6063", "VFycaxIq0Tc": "Oct 6 run, video 1", "dnPs56DPt6I": "Oct 6 run, video 2",
         "DWH1CEygsTI": "Oct 6 run, video 3", "LSQmxwmlTkQ": "Drilling a nozzle, Sep 30"}


def run(cmd):
    if THREADS and cmd[0] == "ffmpeg":       # every decoder (before each -i), the encoder (before the output) and filters
        cmd = [cmd[0], "-filter_threads", THREADS, "-filter_complex_threads", THREADS] + \
              [x for k, a in enumerate(cmd[1:], 1) for x in ((["-threads", THREADS] if a == "-i" or k == len(cmd) - 1 else [])
                                                             + [a])]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd))[:600] + "\n" + r.stderr[-2500:])
    return r


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


def probe_wh(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
               path]).stdout.strip().split(",")
    return int(out[0]), int(out[1])


def tts(text, path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        run(["edge-tts", "--voice", VOICE, "--text", text, "--write-media", path])
    return duration(path)


def font(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size)


INK = "#1F2937"
CARD_VERSION = "5"            # bump when card_png or still_with_audio change, so cached cards are rebuilt
ACCENT = {"00": "#1E3A8A", "01": "#00897B", "02": "#C2410C", "03": "#6D28D9"}   # navy, then the diagrams' tutorial colours


def wrap_px(d, text, f, width):
    """Greedy word wrap to a pixel width."""
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if cur and d.textlength(t, font=f) > width:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + ([cur] if cur else [])


def card_png(title, sub, path, accent=ACCENT["00"], kicker="BYU Vertical Cloud Lab · AMAZEMET rePowder"):
    """A light card in the diagrams' style: text on the left, the 3D machine on the right, a bar in the tutorial's colour."""
    im = Image.new("RGB", (W, H), "white")
    art = f"{V3D}/machine_clean.png"
    if os.path.exists(art):
        m = Image.open(art).convert("RGB").resize((W, H), Image.LANCZOS)
        im.paste(m, (110, 0))
        x0, x1 = 600, 760                                     # white up to x0, fading to the bare render by x1
        ramp = Image.linear_gradient("L").rotate(90, expand=True).resize((x1 - x0, H))
        if ramp.getpixel((0, 0)) < ramp.getpixel((x1 - x0 - 1, 0)):
            ramp = ramp.transpose(Image.FLIP_LEFT_RIGHT)
        mask = Image.new("L", (W, H), 0); mask.paste(Image.new("L", (x0, H), 255), (0, 0)); mask.paste(ramp, (x0, 0))
        im = Image.composite(Image.new("RGB", (W, H), "white"), im, mask)
    d = ImageDraw.Draw(im)
    d.rectangle([0, H - 14, W, H], fill=accent)
    d.text((80, 150), kicker.upper(), font=font(20, True), fill=accent)
    y = 196
    for line in wrap_px(d, title, font(52, True), 560):
        d.text((80, y), line, font=font(52, True), fill=INK); y += 64
    y += 22
    items = [x.strip() for x in re.split(r" · | → ", sub)] if (sub.count(" · ") + sub.count(" → ")) >= 2 else None
    if items:                                   # a list of points: one bullet each, smaller type
        for item in items:
            item = item[:1].upper() + item[1:]
            for k, line in enumerate(wrap_px(d, item, font(25), 520)):
                if k == 0:
                    d.ellipse([84, y + 12, 94, y + 22], fill=accent)
                d.text((108, y), line, font=font(25), fill="#374151"); y += 34
            y += 8
    else:
        for line in wrap_px(d, sub, font(28), 560):
            d.text((80, y), line, font=font(28), fill="#4B5563"); y += 40
    im.save(path)


def still_with_audio(png, mp3, out, dur, fade_in=False, zoom=False):
    """A still under narration; `zoom` adds a slow push-in (2.5 % over the segment) so long diagrams are not static."""
    n = max(1, int(dur * FPS))
    vf = (f"scale={2 * W}:{2 * H},zoompan=z='1+0.025*on/{n}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
          f"format=yuv420p") if zoom else f"scale={W}:{H},format=yuv420p"
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", png, "-i", mp3, "-t", f"{dur:.2f}",
         "-vf", vf + (",fade=t=in:st=0:d=0.6" if fade_in else ""),
         "-af", f"adelay=250|250,apad,{AUDIO}", *ENC, out])
    return out


def accent_for(text):
    m = re.search(r"[Tt]utorial (\d)", text)
    return ACCENT.get(f"0{m.group(1)}", ACCENT["00"]) if m else ACCENT["00"]


def seg_title(i, title, sub, narration):
    png = f"{TMP}/title_{i}.png"; mp3 = f"{TMP}/title_{i}.mp3"; out = f"{TMP}/seg_{i}.mp4"
    card_png(title, sub, png, accent=accent_for(sub))
    return still_with_audio(png, mp3, out, tts(narration, mp3) + 1.4, fade_in=True)


def seg_card(i, title, sub, narration):
    png = f"{TMP}/card_{i}.png"; mp3 = f"{TMP}/card_{i}.mp3"; out = f"{TMP}/seg_{i}.mp4"
    card_png(title, sub, png, accent=accent_for(title + " " + sub))
    return still_with_audio(png, mp3, out, tts(narration, mp3) + 1.0)


def seg_outline(i, name, narration):
    png = f"{DIAG}/{name}.png"; mp3 = f"{TMP}/outline_{i}.mp3"; out = f"{TMP}/seg_{i}.mp4"
    if not os.path.exists(png):
        raise FileNotFoundError(png)
    d = tts(narration, mp3)
    return still_with_audio(png, mp3, out, d + 1.0, zoom=d > 6)


BUILD_LEAD, BUILD_GAP, BUILD_TAIL = 0.25, 0.2, 1.0    # s: before the first sentence, between sentences, after the last


def build_pngs(name):
    """diagrams/<name>_build0.png, _build1.png, ... (from diagrams/make_diagrams.py), in order."""
    pngs = []
    while os.path.exists(f"{DIAG}/{name}_build{len(pngs)}.png"):
        pngs.append(f"{DIAG}/{name}_build{len(pngs)}.png")
    return pngs


def seg_build(i, name, sentences):
    """An outline built up like a PowerPoint slide. Sentence 0 is spoken over the step boxes alone (<name>_build0.png);
    build k (the details of steps 1..k) appears at the start of sentence k, a hard cut with no fade, and stays until the
    next. Each sentence is its own TTS clip, so the cuts land on its measured start."""
    pngs = build_pngs(name); out = f"{TMP}/seg_{i}.mp4"
    if len(pngs) != len(sentences):
        raise ValueError(f"build {name}: {len(sentences)} sentences for {len(pngs)} images ({name}_build0.png ...): "
                         "give one sentence for the step boxes, then one per step")
    mp3s = [f"{TMP}/build_{i}_{k}.mp3" for k in range(len(sentences))]
    starts, t = [], BUILD_LEAD
    for text, mp3 in zip(sentences, mp3s):
        starts.append(t); t += tts(text, mp3) + BUILD_GAP
    cuts = [0] + [round(s * FPS) for s in starts[1:]] + [round((t - BUILD_GAP + BUILD_TAIL) * FPS)]   # frame numbers
    n, inputs, fv, fa = len(pngs), [], [], []
    for k, png in enumerate(pngs):
        frames = cuts[k + 1] - cuts[k]
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{(frames + 1) / FPS:.4f}", "-i", png]
        fv.append(f"[{k}:v]scale={W}:{H},setsar=1,format=yuv420p,trim=end_frame={frames}[v{k}]")
    for k, (mp3, s) in enumerate(zip(mp3s, starts)):
        inputs += ["-i", mp3]
        fa.append(f"[{n + k}:a]adelay={int(s * 1000)}|{int(s * 1000)}[a{k}]")
    fc = ";".join(fv + fa) + ";" + "".join(f"[v{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=0[vout];" \
         + "".join(f"[a{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0,apad,{AUDIO}[aout]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
         "-t", f"{cuts[-1] / FPS:.4f}", *ENC, out])
    print(f"    build {name}: " + ", ".join(f"{k} at {c / FPS:.2f}s" for k, c in enumerate(cuts[:-1])), flush=True)
    return out


def anim_mp4(name):
    """The step animation's MP4: ../viz3d/out/mp4/<name>.mp4 from a fresh render, else the committed 1080p copy with the
    same text and timing in ../ppt/videos/animations/."""
    p = f"{V3D}/mp4/{name}.mp4"
    return p if os.path.exists(p) else f"{ROOT}/ppt/videos/animations/{name}.mp4"


def wait_ready(path, timeout=1800):
    """The 3D renders may still be (re)writing an MP4: wait until it probes cleanly and has stopped changing."""
    import time
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            m = os.path.getmtime(path); duration(path)
            if time.time() - m > 20:
                return
        except (OSError, RuntimeError, ValueError):
            pass
        time.sleep(10)
    raise TimeoutError(path)


def seg_anim(i, name, narration, substeps=None):
    """A 3D animation under narration. With a list of sentences and the sub-step JSON, each sentence starts with its
    sub-step and the sub-step is slowed (up to 1.6x) and then held on its last frame until the sentence is done.
    `substeps` = (first, last) plays only those sub-steps (inclusive), so one animation can serve several sections."""
    mp4 = anim_mp4(name); meta = f"{V3D}/{name}.json"; out = f"{TMP}/seg_{i}.mp4"
    wait_ready(mp4)
    sentences = narration if isinstance(narration, list) else [narration]
    steps = json.load(open(meta))["substeps"] if os.path.exists(meta) else None
    fps = json.load(open(meta)).get("fps", 15) if os.path.exists(meta) else 15
    if steps is not None and substeps is not None:
        steps = steps[substeps[0]:substeps[1] + 1]
    if steps is None or len(sentences) != len(steps):
        if steps is not None:
            print(f"  {name}: {len(sentences)} sentences for {len(steps)} sub-steps, timing the whole thing", flush=True)
            span = {"start_frame": steps[0]["start_frame"], "end_frame": steps[-1]["end_frame"]}
        else:
            span = {"start_frame": 0, "end_frame": None}
        sentences = [" ".join(sentences)]
        steps = [span]
    parts, auds = [], []
    for k, (st, text) in enumerate(zip(steps, sentences)):
        mp3 = f"{TMP}/anim_{i}_{k}.mp3"
        d_tts = tts(text, mp3) + 0.5 if text.strip() else 0.0
        s0 = st["start_frame"] / fps
        e0 = (st["end_frame"] / fps) if st.get("end_frame") is not None else duration(mp4)
        d_vid = e0 - s0
        slow = min(1.6, max(1.0, d_tts / d_vid)) if d_vid > 0 else 1.0
        hold = max(0.0, d_tts - d_vid * slow)
        part = f"{TMP}/anim_{i}_{k}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s0:.3f}", "-t", f"{d_vid:.3f}", "-i", mp4, "-an",
             "-vf", f"setpts={slow:.4f}*PTS,fps={FPS},scale={W}:{H},tpad=stop_mode=clone:stop_duration={hold:.2f},format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", part])
        parts.append(part); auds.append((mp3 if text.strip() else None, duration(part)))
    vlist = f"{TMP}/anim_{i}.txt"; open(vlist, "w").write("".join(f"file '{p}'\n" for p in parts))
    # narration track: each sentence placed at the start of its sub-step
    inputs, filt, t = [], [], 0.0
    for k, (mp3, d) in enumerate(auds):
        if mp3:
            inputs += ["-i", mp3]
            filt.append(f"[{len(inputs) // 2}:a]adelay={int((t + 0.2) * 1000)}|{int((t + 0.2) * 1000)}[a{k}]")
        t += d
    labels = "".join(f"[a{k}]" for k, (mp3, _) in enumerate(auds) if mp3)
    n = labels.count("[")
    fc = ";".join(filt) + f";{labels}amix=inputs={n}:normalize=0,apad,{AUDIO}[aout]"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", vlist, *inputs, "-filter_complex", fc,
         "-map", "0:v", "-map", "[aout]", "-t", f"{t:.2f}", *ENC, out])
    return out


CLIP_VERSION = "2"       # bump when seg_clip changes, so cached clips are rebuilt
# Stabilisation crops rather than showing moving edges: vidstab zooms in by the static amount (optzoom=1) that the clip's
# corrections need, plus a fixed amount for the largest rotation. The corrections are capped, so the zoom never passes
# STAB_MAX_ZOOM; a jolt bigger than the cap is left partly in rather than cropped further.
STAB_MAX_ZOOM = 10.0     # %: 10 % zoom crops 9 % of each dimension (4.5 % a side)
STAB_ANGLE = 0.01        # rad: the largest rotation corrected (0.57 deg)
STAB_SMOOTH = 15         # frames either side in the camera-path low-pass (31 frames, about 1 s)


def clip_source(vid, s, e):
    """(path, t0) of the downloaded high-resolution window that covers [s, e], tallest first: HLS segments in
    {HLS}/<id>_<start>.ts with a .json whose t0 is the video time of the file's first frame. None if no window covers it.
    (t0 was checked against the 360p copy: the frame at t0 + x in the window is the 360p copy's frame at the same time.
    The .ts timestamps run one frame later, so the file's own start_time is not used.)"""
    best = None
    for p in glob.glob(f"{HLS}/{glob.escape(vid)}_*.json"):
        m = json.load(open(p))
        ts = os.path.join(HLS, m.get("file", os.path.basename(p)[:-5] + ".ts"))
        if m.get("video_id") == vid and m["t0"] <= s and e <= m["t1"] and os.path.exists(ts):
            if best is None or m.get("height", 0) > best[2]:
                best = (ts, float(m["t0"]), m.get("height", 0))
    return best[:2] if best else None


def audio_source(vid, s, e):
    """(path, t0) of the sound for [s, e]: the full-length track {DL}/<id>.m4a (t0 = 0), else an excerpt
    {DL}/<id>_a<start>.m4a whose .json gives t0, the video time of its first sample. Excerpts are cut on the Pi, decoded
    from t0 and re-encoded, so that a rebuild over a slow link moves minutes of audio rather than hours."""
    a = f"{DL}/{vid}.m4a"
    if os.path.exists(a):
        return a, 0.0
    for p in glob.glob(f"{DL}/{glob.escape(vid)}_a*.json"):
        m = json.load(open(p))
        if m.get("video_id") == vid and m["t0"] <= s and e <= m["t1"] and os.path.exists(f"{DL}/{m['file']}"):
            return f"{DL}/{m['file']}", float(m["t0"])
    raise FileNotFoundError(f"{vid}: need {a}, or an excerpt that covers {s:.1f}-{e:.1f}")


def seg_clip(i, vid, start, dur, speaker, section=""):
    """The trainer's own words: sentence-snapped, cut from the 720p window, stabilised, subtitled, labelled,
    loudness-matched."""
    out = f"{TMP}/seg_{i}.mp4"
    s, e, words = clip_words.snap(vid, start, dur)
    a, a0 = audio_source(vid, s, e)
    d = e - s
    srt = f"{TMP}/clip_{i}.srt"
    with open(srt, "w") as f:
        for k, (c0, c1, text) in enumerate(clip_words.srt_lines(words, s), 1):
            ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}".replace(".", ",")
            f.write(f"{k}\n{ts(c0)} --> {ts(min(c1, d))}\n{clip_words.fix(text, FIXES)}\n\n")
    # pass 0: the cut. Video from the high-resolution window, decoded from the window's start (seeking inside an MPEG-TS
    # can land between keyframes) and trimmed by timestamp at the frame nearest s; audio from the full-length track at s.
    trf = f"{TMP}/clip_{i}.trf"; cut = f"{TMP}/clip_{i}_cut.mp4"
    src = clip_source(vid, s, e)
    if src:
        x = round((s - src[1]) * FPS) / FPS                     # seconds into the window, on its frame grid
        vin, vtrim = ["-i", src[0]], f"trim=start={max(0.0, x - 0.5 / FPS):.4f},setpts=PTS-STARTPTS,"
    else:
        v = f"{DL}/{vid}.v360.mp4"
        if not os.path.exists(v):
            raise FileNotFoundError(f"{vid}: no window in {HLS} covers {s:.1f}-{e:.1f}, and no {v}")
        print(f"  ! clip {vid} {s:.1f}-{e:.1f}: no window in {HLS} covers it; using the 360p copy", flush=True)
        vin, vtrim = ["-ss", f"{s:.3f}", "-i", v], ""
    run(["ffmpeg", "-y", "-v", "error", *vin, "-ss", f"{s - a0:.3f}", "-t", f"{d:.3f}", "-i", a,
         "-filter_complex", f"[0:v]{vtrim}fps={FPS}[v]", "-map", "[v]", "-map", "1:a:0", "-t", f"{d:.3f}",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", cut])
    # pass 1: motion analysis of the cut, at source resolution
    run(["ffmpeg", "-y", "-v", "error", "-i", cut, "-vf", f"vidstabdetect=shakiness=8:accuracy=9:result={trf}",
         "-f", "null", "-"])
    w, h = probe_wh(cut)
    mm = f"{int(start) // 60:02d}:{int(start) % 60:02d}" if start < 3600 else f"{int(start) // 3600}:{int(start) % 3600 // 60:02d}:{int(start) % 60:02d}"
    label = f"{speaker}  ·  {SHORT.get(vid, VIDEOS.get(vid, {}).get('title', vid))}  ·  {mm}"
    esc = lambda x: x.replace("\\", "").replace(":", "\\:").replace("'", "’").replace(",", "\\,")
    label, section = esc(label), esc(section)
    # pass 2, first in the chain so the label and subtitles drawn afterwards are never cropped
    rot = 100 * max(w, h) / min(w, h) * math.sin(STAB_ANGLE) + 0.5    # % zoom that hides the largest rotation, + margin
    shift = int((STAB_MAX_ZOOM - rot) / 200 * min(w, h))             # px: optzoom=1 adds at most 2*shift/min(w,h)
    stab = (f"vidstabtransform=input={trf}:smoothing={STAB_SMOOTH}:optzoom=1:zoom={rot:.2f}:maxshift={shift}:"
            f"maxangle={STAB_ANGLE}:crop=keep:interpol=bilinear,unsharp=5:5:0.6:3:3:0.3")
    if h > w:   # portrait phone video: blurred fill behind the frame instead of black bars
        fg = f"[0:v]{stab},scale=-2:{H}:flags=lanczos,split[fg][bgsrc];" \
             f"[bgsrc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.12[bg];" \
             f"[bg][fg]overlay=(W-w)/2:0"
    else:
        fg = f"[0:v]{stab},scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black"
    style = "FontName=DejaVu Sans,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H99000000," \
            "BorderStyle=4,Outline=0,Shadow=0,MarginV=22"
    vf = (f"{fg},drawbox=x=0:y=0:w=iw:h=46:color=black@0.45:t=fill,"
          + (f"drawtext=fontfile={FONTB}:text='{section}':x=w-tw-20:y=13:fontsize=21:fontcolor=0x9fd3ff," if section else "")
          + f"drawtext=fontfile={FONT}:text='{label}':x=20:y=13:fontsize=21:fontcolor=white,"
          f"subtitles={srt}:force_style='{style}',fade=t=in:st=0:d=0.25,fade=t=out:st={max(0, d - 0.3):.2f}:d=0.3[vout]")
    r = run(["ffmpeg", "-y", "-v", "info", "-nostats", "-i", cut, "-filter_complex", vf, "-map", "[vout]", "-map", "0:a:0",
             "-af", f"highpass=f=90,afftdn=nf=-25,{AUDIO},afade=t=in:st=0:d=0.15,afade=t=out:st={max(0, d - 0.3):.2f}:d=0.3",
             *ENC, out])
    for p in (cut, trf):
        os.remove(p)
    zoom = re.findall(r"Final zoom: ([-\d.]+)", r.stderr)
    print(f"    clip {vid} {start}+{dur} -> {s:.1f}-{e:.1f} from {os.path.basename(src[0]) if src else 'the 360p copy'}"
          f" ({w}x{h}), stabilised with {float(zoom[-1]) if zoom else float('nan'):.1f} % zoom:"
          f" {''.join(x['w'] for x in words).strip()[:150]}", flush=True)
    return out


REAL_VERSION = "2"        # bump when seg_real changes, so cached picks are rebuilt
REAL_MAX, REAL_SLACK = 14.0, 3.0   # s: a pick up to REAL_MAX + REAL_SLACK plays whole; a longer one plays its middle REAL_MAX
REAL_LIGHT_ZOOM = 5.0     # %: zoom cap for picks marked "light" in real-footage.md (the camera rests on one view)
TAG = {"real": ("IN THE LAB", "#00897B"), "wrong": ("WHAT GOES WRONG", "#C2410C")}


_TRANSCRIPTS = {}


def transcript_words(vid, s, e):
    """Words of the full word-timed transcript (../transcripts/whisper/<id>.json) that overlap [s, e], as clip_words
    gives them: [{"w", "s", "e"}]."""
    if vid not in _TRANSCRIPTS:
        p = f"{ROOT}/transcripts/whisper/{vid}.json"
        _TRANSCRIPTS[vid] = [{"w": w[2], "s": w[0], "e": w[1]} for seg in (json.load(open(p))["segments"] if os.path.exists(p)
                             else []) for w in seg.get("words") or []]
    return [w for w in _TRANSCRIPTS[vid] if w["e"] > s and w["s"] < e]


def real_window(vid, t_in, t_out, exact=False, at="middle"):
    """(start, end, words) of a pick: all of it, or REAL_MAX seconds of it if it is longer than REAL_MAX + REAL_SLACK: the
    middle, or with at="end" the last (where the words that matter come at the end of the pick).
    An end that falls inside a word moves out to the word's edge, and a sentence that finishes within 1.5 s is let finish,
    so the sound never stops mid-word. `exact` keeps the given points (picks timed to the frame by hand)."""
    s, e = float(t_in), float(t_out)
    if not exact and e - s > REAL_MAX + REAL_SLACK:
        mid = e - REAL_MAX / 2 if at == "end" else (s + e) / 2
        s, e = mid - REAL_MAX / 2, mid + REAL_MAX / 2
    words = transcript_words(vid, s - 4, e + 4)
    if not exact and words:
        inside = [w for w in words if w["s"] < s < w["e"] and w["e"] - w["s"] < 1.2]   # longer: Whisper's padding
        if inside:                            # start on the word's first sound, not halfway through it
            before = [w["e"] for w in words if w["e"] <= inside[0]["s"]]
            s = max(inside[0]["s"] - 0.1, before[-1] if before else 0.0)
        inside = [w for w in words if w["s"] < e < w["e"] and w["e"] - w["s"] < 1.2]
        e0 = e = inside[0]["e"] if inside else e
        prev = None
        for w in [w for w in words if w["s"] >= e - 0.01]:   # let a sentence in progress finish, if it does so soon
            if w["e"] - e0 > 1.5 or (prev and w["s"] - prev["e"] > 0.7):
                break
            if w["w"].strip().endswith((".", "?", "!")):
                e = w["e"]
                break
            prev = w
        after = [w["s"] for w in words if w["s"] >= e - 0.01]
        e = min(e + 0.15, after[0] - 0.02) if after and after[0] > e else e + 0.15
    return max(0.0, s), e, [w for w in words if w["s"] >= s - 0.05 and w["e"] <= e + 0.05]


def real_bar(caption, source, section, kind, path):
    """The top bar of a real-footage pick, drawn with Pillow: a coloured tag, what the pick shows, where it is from, and
    the step at the right."""
    im = Image.new("RGBA", (W, 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 50], fill=(0, 0, 0, 125))
    tag, colour = TAG[kind]
    ft, fc, fs = font(15, True), font(22, True), font(18)
    tw = d.textlength(tag, font=ft)
    d.rounded_rectangle([16, 12, 16 + tw + 20, 38], radius=5, fill=colour)
    d.text((26, 16), tag, font=ft, fill="white")
    x = 16 + tw + 20 + 14
    d.text((x, 12), caption, font=fc, fill="white"); x += d.textlength(caption, font=fc) + 14
    fsec = font(19, True)
    right = W - 20 - (d.textlength(section, font=fsec) + 24 if section else 0)
    while source and x + d.textlength(source, font=fs) > right:      # never run into the step label
        source = source[:-2].rstrip() + "…"
    d.text((x, 15), source, font=fs, fill="#D1D5DB")
    if section:
        d.text((W - 20 - d.textlength(section, font=fsec), 14), section, font=fsec, fill="#9fd3ff")
    im.save(path)


def seg_real(i, vid, t_in, t_out, caption, opts=None, section=""):
    """A real-footage pick: cut from the 720p window, stabilised (less zoom for a camera at rest), with the recording's own
    sound (or silence where real-footage.md says to mute the chatter), subtitled from the word-timed transcript, under a
    bar naming what it shows."""
    opts = opts or {}
    out = f"{TMP}/seg_{i}.mp4"
    s, e, words = real_window(vid, t_in, t_out, opts.get("exact", False), opts.get("at", "middle"))
    d = e - s
    mute = opts.get("mute", False)
    a, a0 = (None, 0.0) if mute else audio_source(vid, s, e)
    srt = f"{TMP}/real_{i}.srt"
    cues = [] if mute else clip_words.srt_lines(words, s)
    with open(srt, "w") as f:
        for k, (c0, c1, text) in enumerate(cues, 1):
            ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}".replace(".", ",")
            f.write(f"{k}\n{ts(c0)} --> {ts(min(c1, d))}\n{clip_words.fix(text, FIXES)}\n\n")
    src = clip_source(vid, s, e)
    if not src:
        raise FileNotFoundError(f"real {vid} {s:.1f}-{e:.1f}: no window in {HLS} covers it")
    trf = f"{TMP}/real_{i}.trf"; cut = f"{TMP}/real_{i}_cut.mp4"
    x = round((s - src[1]) * FPS) / FPS
    ain = ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=44100:cl=stereo"] if mute else ["-ss", f"{s - a0:.3f}", "-t", f"{d:.3f}", "-i", a]
    run(["ffmpeg", "-y", "-v", "error", "-i", src[0], *ain,
         "-filter_complex", f"[0:v]trim=start={max(0.0, x - 0.5 / FPS):.4f},setpts=PTS-STARTPTS,fps={FPS},"
         # no bigger than the frame it ends up in (1080p and portrait sources), so the two vidstab passes stay quick
         f"scale='min({W},iw)':'min({H},ih)':force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos[v]",
         "-map", "[v]", "-map", "1:a:0", "-t", f"{d:.3f}",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", cut])
    run(["ffmpeg", "-y", "-v", "error", "-i", cut, "-vf", f"vidstabdetect=shakiness=8:accuracy=9:result={trf}",
         "-f", "null", "-"])
    w, h = probe_wh(cut)
    cap = REAL_LIGHT_ZOOM if opts.get("light") else STAB_MAX_ZOOM
    rot = 100 * max(w, h) / min(w, h) * math.sin(STAB_ANGLE) + 0.5
    shift = max(4, int((cap - rot) / 200 * min(w, h)))
    stab = (f"vidstabtransform=input={trf}:smoothing={STAB_SMOOTH}:optzoom=1:zoom={rot:.2f}:maxshift={shift}:"
            f"maxangle={STAB_ANGLE}:crop=keep:interpol=bilinear,unsharp=5:5:0.6:3:3:0.3")
    if h > w:
        fg = f"[0:v]{stab},scale=-2:{H}:flags=lanczos,split[fg][bgsrc];" \
             f"[bgsrc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=24:2,eq=brightness=-0.12[bg];" \
             f"[bg][fg]overlay=(W-w)/2:0"
    else:
        fg = f"[0:v]{stab},scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black"
    mm = f"{int(t_in) // 60:02d}:{int(t_in) % 60:02d}" if t_in < 3600 else f"{int(t_in) // 3600}:{int(t_in) % 3600 // 60:02d}:{int(t_in) % 60:02d}"
    bar = f"{TMP}/real_{i}_bar.png"
    real_bar(caption, f"{SHORT.get(vid, VIDEOS.get(vid, {}).get('title', vid))} · {mm}", opts.get("section", section),
             "wrong" if opts.get("wrong") else "real", bar)
    style = "FontName=DejaVu Sans,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H99000000," \
            "BorderStyle=4,Outline=0,Shadow=0,MarginV=22"
    vf = (f"{fg}[base];[base][1:v]overlay=0:0," + (f"subtitles={srt}:force_style='{style}'," if cues else "")
          + f"fade=t=in:st=0:d=0.25,fade=t=out:st={max(0, d - 0.3):.2f}:d=0.3[vout]")
    af = "anull" if mute else f"highpass=f=90,afftdn=nf=-25,{AUDIO}"
    r = run(["ffmpeg", "-y", "-v", "info", "-nostats", "-i", cut, "-i", bar, "-filter_complex", vf, "-map", "[vout]",
             "-map", "0:a:0", "-af", f"{af},afade=t=in:st=0:d=0.15,afade=t=out:st={max(0, d - 0.3):.2f}:d=0.3", *ENC, out])
    for p in (cut, trf):
        os.remove(p)
    zoom = re.findall(r"Final zoom: ([-\d.]+)", r.stderr)
    print(f"    real {vid} {t_in}-{t_out} -> {s:.1f}-{e:.1f} ({d:.1f}s) from {os.path.basename(src[0])} ({w}x{h}),"
          f" {float(zoom[-1]) if zoom else float('nan'):.1f} % zoom{', muted' if mute else ''}: {caption}", flush=True)
    return out


def concat_xfade(segs, out, fade=FADE, cuts=()):
    """Join the segments with a crossfade of `fade` seconds (video xfade, audio acrossfade), or with a hard cut at the
    joins in `cuts` (join k is the one into segs[k]). Each segment's video and audio are first held or padded to the same
    whole number of frames, so neither kind of join can shift the sound against the picture."""
    durs = [round(duration(s) * FPS) / FPS for s in segs]
    inputs = sum((["-i", s] for s in segs), [])
    norm = [f"[{k}:v]fps={FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=1,"
            f"trim=duration={d:.4f},settb=AVTB[n{k}];"      # concat outputs AVTB, and xfade needs both inputs alike
            f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad,atrim=duration={d:.4f}[m{k}]"
            for k, d in enumerate(durs)]
    fv, fa = [], []
    vprev, aprev, end = "n0", "m0", durs[0]
    for k in range(1, len(segs)):
        if k in cuts:
            fv.append(f"[{vprev}][n{k}]concat=n=2:v=1:a=0[v{k}]")
            fa.append(f"[{aprev}][m{k}]concat=n=2:v=0:a=1[a{k}]")
            end += durs[k]
        else:
            fv.append(f"[{vprev}][n{k}]xfade=transition=fade:duration={fade}:offset={end - fade:.3f}[v{k}]")
            fa.append(f"[{aprev}][m{k}]acrossfade=d={fade}:c1=tri:c2=tri[a{k}]")
            end += durs[k] - fade
        vprev, aprev = f"v{k}", f"a{k}"
    n = len(segs) - 1
    fc = ";".join(norm + fv + fa)
    fc += f";[v{n}]fade=t=out:st={end - 0.8:.2f}:d=0.8[vend];[a{n}]afade=t=out:st={end - 0.8:.2f}:d=0.8[aend]"
    script = f"{TMP}/{os.path.basename(out)}.filter"
    open(script, "w").write(fc)
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex_script", script, "-map", "[vend]", "-map", "[aend]",
         *ENC, "-movflags", "+faststart", out])
    return out


NUM = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}


def section_label(narration):
    """'Step two: the ultrasonic stack.' -> 'Step 2 · the ultrasonic stack' for the clips' top bar."""
    m = re.match(r"Step (\w+): (.*?)[.,]", narration)
    if not m:
        return ""
    desc = re.sub(r"^(the|a|an) ", "", m.group(2))
    return f"Step {NUM.get(m.group(1).lower(), m.group(1))} · {desc[:1].upper()}{desc[1:]}"


def seg_key(seg):
    """Segments are cached in tmp/ under a hash of everything that goes into them, so a rebuild redoes only what changed."""
    kind, args = seg[0], seg[1:]
    deps = [VOICE, json.dumps(args, ensure_ascii=False)]
    if kind == "clip":
        src = clip_source(args[0], *clip_words.snap(args[0], args[1], args[2])[:2])
        deps += [json.dumps(FIXES, sort_keys=True), CLIP_VERSION, f"{STAB_MAX_ZOOM}/{STAB_ANGLE}/{STAB_SMOOTH}",
                 f"{src[0]}@{os.path.getmtime(src[0])}" if src else "360p"]
    if kind == "real":
        o = args[4] if len(args) > 4 and args[4] else {}
        w0, w1 = real_window(args[0], args[1], args[2], o.get("exact", False), o.get("at", "middle"))[:2]
        src = clip_source(args[0], w0, w1)
        deps += [json.dumps(FIXES, sort_keys=True), REAL_VERSION, f"{STAB_MAX_ZOOM}/{REAL_LIGHT_ZOOM}/{STAB_ANGLE}/{STAB_SMOOTH}",
                 f"{REAL_MAX}/{REAL_SLACK}", f"{src[0]}@{os.path.getmtime(src[0])}" if src else "none"]
    if kind == "build":
        deps += [CARD_VERSION, f"{BUILD_LEAD}/{BUILD_GAP}/{BUILD_TAIL}"] + \
                [f"{os.path.basename(p)}@{os.path.getmtime(p)}" for p in build_pngs(args[0])]
    if kind == "anim":
        wait_ready(anim_mp4(args[0]))
        deps += [str(os.path.getmtime(p)) for p in (anim_mp4(args[0]), f"{V3D}/{args[0]}.json") if os.path.exists(p)]
    if kind == "outline" and os.path.exists(f"{DIAG}/{args[0]}.png"):
        deps.append(str(os.path.getmtime(f"{DIAG}/{args[0]}.png")))
    if kind in ("title", "card", "outline"):
        deps.append(CARD_VERSION)
    if kind in ("title", "card") and os.path.exists(f"{V3D}/machine_clean.png"):
        deps.append(str(os.path.getmtime(f"{V3D}/machine_clean.png")))
    return f"{kind}_" + hashlib.sha1("|".join(deps).encode()).hexdigest()[:12]


def make_seg(seg):
    kind, args = seg[0], seg[1:]
    sid = seg_key(seg)
    if os.path.exists(f"{TMP}/seg_{sid}.mp4"):
        try:
            duration(f"{TMP}/seg_{sid}.mp4")
            return f"{TMP}/seg_{sid}.mp4"
        except (RuntimeError, ValueError):       # half-written by an interrupted build: make it again
            os.remove(f"{TMP}/seg_{sid}.mp4")
    fn = {"title": seg_title, "card": seg_card, "outline": seg_outline, "build": seg_build, "anim": seg_anim,
          "clip": seg_clip, "real": seg_real}[kind]
    return fn(sid, *args)


def hard_cuts(segments):
    """The joins (index k = the join into segment k) that are hard cuts: into and out of a build, like slide changes."""
    return {k for k in range(1, len(segments)) if "build" in (segments[k - 1][0], segments[k][0])}


def plan(key):
    """The tutorial's segments, with each clip tagged by the step whose divider precedes it."""
    out, section = [], ""
    for seg in TUTORIALS[key]["segments"]:
        if seg[0] in ("outline", "build"):
            section = section_label(seg[2]) if seg[0] == "outline" and "_step" in seg[1] else ""
        if seg[0] == "clip" and section:
            seg = (*seg[:6], section)
        if seg[0] == "real":
            seg = (*seg[:6], section)
        out.append(seg)
    return out


def build(key):
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    segs, segments = [], plan(key)
    for i, seg in enumerate(segments):
        kind, args = seg[0], seg[1:]
        segs.append(make_seg(seg))
        print(key, i, kind, args[0] if kind not in ("clip", "real") else f"{args[0]}@{args[1]}", f"{duration(segs[-1]):.1f}s",
              flush=True)
    out = f"{OUT}/{key}.mp4"
    concat_xfade(segs, out, cuts=hard_cuts(segments))
    print(key, "->", out, f"{duration(out) / 60:.2f} min", flush=True)
    return out


def timeline(key):
    """When each segment starts in out/<key>.mp4, joined as concat_xfade joins them, from the cached segments (nothing is
    built): [(seconds, kind, name)]. For chapter times in ../playlist/catalog.py."""
    segments, out, end = plan(key), [], 0.0
    cuts = hard_cuts(segments)
    for k, seg in enumerate(segments):
        d = round(duration(f"{TMP}/seg_{seg_key(seg)}.mp4") * FPS) / FPS
        start = 0.0 if k == 0 else end if k in cuts else end - FADE
        out.append((round(start, 2), seg[0], f"{seg[1]}@{seg[2]}" if seg[0] in ("clip", "real") else seg[1]))
        end = start + d
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["--clips"]:     # pre-build only the clips and real picks (they need neither the renders nor the diagrams)
        os.makedirs(TMP, exist_ok=True)
        for k in (sys.argv[2:] or list(TUTORIALS)):
            for seg in plan(k):
                if seg[0] in ("clip", "real"):
                    print(k, seg[0], seg[1], seg[2], f"{duration(make_seg(seg)):.1f}s", flush=True)
    elif sys.argv[1:2] == ["--timeline"]:     # segment start times of built tutorials, for chapters
        for k in (sys.argv[2:] or list(TUTORIALS)):
            for t, kind, name in timeline(k):
                print(f"{k}  {int(t) // 60}:{int(t) % 60:02d}  {t:7.2f}  {kind:8s} {name}", flush=True)
    else:
        for k in (sys.argv[1:] or list(TUTORIALS)):
            build(k)

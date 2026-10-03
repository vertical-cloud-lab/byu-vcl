"""Assemble the narrated tutorial videos from the 3D step animations, the draw.io outlines and clips of the training videos.

Segment kinds (see scripts.py):
  title    — opening card over the 3D render of the machine, one short line of narration
  outline  — a draw.io diagram (diagrams/<name>.png): the tutorial's steps, or one of them highlighted as a section divider
  anim     — a 3D step animation (../viz3d/out/mp4/<name>.mp4). Narration given as a list is timed sentence by sentence
             against the animation's sub-steps (../viz3d/out/<name>.json); the sub-step stretches if the voice needs longer
  clip     — the trainer's own words, cut from a training video: snapped to sentence boundaries with word-timed Whisper
             (clip_words.py), stabilised (vidstab, two passes), subtitled from the same words, loudness-matched
  card     — a text card with narration

Synthetic narration is Microsoft Edge TTS (VOICE in scripts.py) at 1x. Segments are joined with short crossfades (FADE).
Output: ./out/<tutorial>.mp4, 1280x720 h264 + aac.

    python build_tutorials.py             # all
    python build_tutorials.py 02-during   # one
Set ATOMIZER_DL to the folder holding <id>.v360.mp4 and <id>.m4a (default /tmp/work/dl).
"""
import hashlib, json, math, os, re, shutil, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scripts import FIXES, TUTORIALS, VOICE
import clip_words

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl")
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
         "u-KjR5TENN4": "Expert cleaning, POV", "f8KL31PN8bA": "Cartridge cleaning", "2wMgeI-E7zw": "Training (Sterling's phone)",
         "qYyT39D5Yzo": "First run, Oct 2, part 1", "of5-LhkX_VQ": "First run, Oct 2, part 2", "07QOPRHIEvw": "Placing the atomizer",
         "Kv9DT3Vo0GE": "Construction update", "z6rwmQW_3Vg": "Turning Al crucibles", "Pk0K5sBz-sQ": "Training, Sep 29",
         "TFpU4uqVF9c": "Atomizing AlSi10Mg-Al6063"}


def run(cmd):
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
    mp4 = f"{V3D}/mp4/{name}.mp4"; meta = f"{V3D}/{name}.json"; out = f"{TMP}/seg_{i}.mp4"
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


def seg_clip(i, vid, start, dur, speaker, section=""):
    """The trainer's own words: sentence-snapped, stabilised, subtitled, labelled, loudness-matched."""
    out = f"{TMP}/seg_{i}.mp4"
    v = f"{DL}/{vid}.v360.mp4"; a = f"{DL}/{vid}.m4a"
    if not (os.path.exists(v) and os.path.exists(a)):
        raise FileNotFoundError(f"{vid}: need {v} and {a}")
    s, e, words = clip_words.snap(vid, start, dur)
    d = e - s
    srt = f"{TMP}/clip_{i}.srt"
    with open(srt, "w") as f:
        for k, (c0, c1, text) in enumerate(clip_words.srt_lines(words, s), 1):
            ts = lambda x: f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}".replace(".", ",")
            f.write(f"{k}\n{ts(c0)} --> {ts(min(c1, d))}\n{clip_words.fix(text, FIXES)}\n\n")
    # pass 1: motion analysis of the cut, at source resolution
    trf = f"{TMP}/clip_{i}.trf"; cut = f"{TMP}/clip_{i}_cut.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s:.2f}", "-t", f"{d:.2f}", "-i", v, "-ss", f"{s:.2f}", "-t", f"{d:.2f}",
         "-i", a, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac",
         "-b:a", "192k", cut])
    run(["ffmpeg", "-y", "-v", "error", "-i", cut, "-vf", f"vidstabdetect=shakiness=8:accuracy=15:result={trf}",
         "-f", "null", "-"])
    w, h = probe_wh(cut)
    mm = f"{int(start) // 60:02d}:{int(start) % 60:02d}" if start < 3600 else f"{int(start) // 3600}:{int(start) % 3600 // 60:02d}:{int(start) % 60:02d}"
    label = f"{speaker}  ·  {SHORT.get(vid, VIDEOS.get(vid, {}).get('title', vid))}  ·  {mm}"
    esc = lambda x: x.replace("\\", "").replace(":", "\\:").replace("'", "’").replace(",", "\\,")
    label, section = esc(label), esc(section)
    stab = f"vidstabtransform=input={trf}:smoothing=24:zoom=4:optzoom=0:interpol=bicubic,unsharp=5:5:0.6:3:3:0.3"
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
    run(["ffmpeg", "-y", "-v", "error", "-i", cut, "-filter_complex", vf, "-map", "[vout]", "-map", "0:a:0",
         "-af", f"highpass=f=90,afftdn=nf=-25,{AUDIO},afade=t=in:st=0:d=0.15,afade=t=out:st={max(0, d - 0.3):.2f}:d=0.3",
         *ENC, out])
    for p in (cut, trf):
        os.remove(p)
    print(f"    clip {vid} {start}+{dur} -> {s:.1f}-{e:.1f}: {''.join(x['w'] for x in words).strip()[:150]}", flush=True)
    return out


def concat_xfade(segs, out, fade=FADE):
    """Join the segments with a crossfade of `fade` seconds (video xfade, audio acrossfade)."""
    durs = [duration(s) for s in segs]
    inputs = sum((["-i", s] for s in segs), [])
    norm = [f"[{k}:v]settb=AVTB,fps={FPS},format=yuv420p,setsar=1[n{k}];"
            f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo[m{k}]" for k in range(len(segs))]
    fv, fa = [], []
    vprev, aprev, off = "n0", "m0", 0.0
    for k in range(1, len(segs)):
        off += durs[k - 1] - fade
        fv.append(f"[{vprev}][n{k}]xfade=transition=fade:duration={fade}:offset={off:.3f}[v{k}]")
        fa.append(f"[{aprev}][m{k}]acrossfade=d={fade}:c1=tri:c2=tri[a{k}]")
        vprev, aprev = f"v{k}", f"a{k}"
    n = len(segs) - 1
    fc = ";".join(norm + fv + fa)
    fc += f";[v{n}]fade=t=out:st={sum(durs) - fade * n - 0.8:.2f}:d=0.8[vend];[a{n}]afade=t=out:st={sum(durs) - fade * n - 0.8:.2f}:d=0.8[aend]"
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
        deps.append(json.dumps(FIXES, sort_keys=True))
    if kind == "anim":
        wait_ready(f"{V3D}/mp4/{args[0]}.mp4")
        deps += [str(os.path.getmtime(p)) for p in (f"{V3D}/mp4/{args[0]}.mp4", f"{V3D}/{args[0]}.json") if os.path.exists(p)]
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
        return f"{TMP}/seg_{sid}.mp4"
    fn = {"title": seg_title, "card": seg_card, "outline": seg_outline, "anim": seg_anim, "clip": seg_clip}[kind]
    return fn(sid, *args)


def plan(key):
    """The tutorial's segments, with each clip tagged by the step whose divider precedes it."""
    out, section = [], ""
    for seg in TUTORIALS[key]["segments"]:
        if seg[0] == "outline":
            section = section_label(seg[2]) if "_step" in seg[1] else ""
        if seg[0] == "clip" and section:
            seg = (*seg[:6], section)
        out.append(seg)
    return out


def build(key):
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    segs = []
    for i, seg in enumerate(plan(key)):
        kind, args = seg[0], seg[1:]
        segs.append(make_seg(seg))
        print(key, i, kind, args[0] if kind != "clip" else f"{args[0]}@{args[1]}", f"{duration(segs[-1]):.1f}s", flush=True)
    out = f"{OUT}/{key}.mp4"
    concat_xfade(segs, out)
    print(key, "->", out, f"{duration(out) / 60:.2f} min", flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["--clips"]:     # pre-build only the clip segments (they need neither the 3D renders nor the diagrams)
        os.makedirs(TMP, exist_ok=True)
        for k in (sys.argv[2:] or list(TUTORIALS)):
            for seg in plan(k):
                if seg[0] == "clip":
                    print(k, seg[1], seg[2], f"{duration(make_seg(seg)):.1f}s", flush=True)
    else:
        for k in (sys.argv[1:] or list(TUTORIALS)):
            build(k)

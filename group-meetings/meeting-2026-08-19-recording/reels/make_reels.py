#!/usr/bin/env python3
"""Render the AI-in-the-lab reels set: vertical 1080x1920 quote-driven cuts of the
2026-08-19 meeting and the breakout pair discussions, with filler words and dead air
removed by micro-cuts and the quote text revealed on screen word-by-word in sync with
the audio (the "Frieren next-episode preview" look: dark frame, voices, text).

v2 (2026-08-26), after review feedback on the first set:
  * black canvas instead of navy, no timestamp/source bug in the corner;
  * the on-screen quote is PRE-WRAPPED at a fixed set of line breaks, so words never
    reflow to a different line as the reveal advances (each word lands in its final
    position the moment it appears) -- see wrap_phrase();
  * bigger type: the quote auto-fits from 104 px down, instead of a fixed 76 px;
  * the speaker is a single grayed-out "Name:" label, not a role caption;
  * every source is background-noise reduced before the cut (see AUDIO_DENOISE).

v3 (2026-08-27): meeting items can carry "visual": "footage" with a "crop" (source
coordinates) so the screen share Sterling ran for 16:12-1:15:22 of the recording -- the
three questions, the GitHub thread where @claude reports the sensor test -- and the room
camera actually appear, instead of every meeting bite being text on black. Items may also
carry "redact": timed black boxes in source coordinates, for screen content that must not
be published (unused since 2026-08-29; see the EDL).

v4 (2026-08-29), implementing the findings of ../best-practices/:
  * the reel OPENS ON THE QUOTE. The branded title card is no longer a silent piece in
    front of the cut; its kicker and title fade in over the first bite instead, so the
    first voice is audible in frame 1 (finding 2);
  * SAFE AREAS: the quote measure stops at x=846, clear of the right-hand action-button
    column, and a full block bottoms out at y=1387 -- above the caption/handle strip on
    Shorts (~1600), Reels (~1490) and TikTok (~1440). Three lines instead of four,
    shorter phrases, so the type stays large inside the smaller measure (finding 5);
  * TEXT OVER FOOTAGE is presented as static 1-3 line blocks, not word-by-word: reading
    the screen share, reading a growing quote and listening at once is the split-attention
    case the redundancy principle actually warns about. Word-by-word survives where it is
    safe -- text on black, no competing visual (finding 7);
  * the sidecar .vtt files are real caption tracks: cues never overlap, lines are wrapped
    to <=42 characters, every cue carries a <v Speaker> tag, and cue ends are extended
    into the following silence to bring the reading rate down (findings 3 and 4).

Reads reels-edl.json. Every item carries its final keep-intervals ("segments", seconds
on the source timeline, already word-aligned and filler-cut) and the kept words with
their source-time onsets ("words", [start, end, text]) used for the burned text reveal
and the sidecar captions. Nothing is inferred at render time -- the EDL is the edit.

Usage:
    python3 make_reels.py --source /path/to/meeting.mp4 \
        --clips-dir /path/to/clips --workdir /tmp/reels-build [--only reel-id]

The meeting MP4 is re-fetched with `yt-dlp -f source "<share link>"` (../README.md);
the breakout clips live on the stream-cam Pi under ~/vcl-ai-clips/ (see
../highlights/README.md for the YouTube download recipe). Items whose source is
unavailable can instead be supplied pre-cut via --recovered (a manifest of
{"<reel-id>__<item-id>": {"audio": wav, "video": mp4, "dur": s}}), which is how this
pass was rendered when the runner had neither tailnet nor YouTube access.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).resolve().parent
INTER = Path("/usr/share/fonts/opentype/inter")
FONT_QUOTE = INTER / "Inter-SemiBold.otf"
FONT_LABEL = INTER / "Inter-Medium.otf"
FONT_BODY = INTER / "Inter-Regular.otf"
FONT_TITLE = INTER / "InterDisplay-Bold.otf"

W, H, FPS = 1080, 1920, 30
AR = 48000
BG = "black"

# ---- fixed layout. Every item uses the same geometry, so a cut between two items
# ---- moves the words and nothing else -- which is most of what made v1 feel choppy.
#
# v4 keeps the whole composition inside the phone-safe rectangle. Vertically the platforms
# put their own chrome over roughly the top 10 % and the bottom 20-25 % of the frame; the
# lowest published overlay edge of the three targets is TikTok's at about y=1440, so the
# quote block is sized to bottom out above that. Horizontally the like/comment/share column
# starts around x=860-900 on Reels and TikTok, so the text measure stops at x=846 -- the
# waveform and footage may run wider, since a clipped waveform edge costs nothing.
SAFE_L = 78
SAFE_R = 234
TEXT_W = W - SAFE_L - SAFE_R     # 768 px of usable measure (x = 78 .. 846)
VIS_Y, VIS_H, VIS_W = 326, 512, W   # "visual zone": footage, or the waveform on text items
SPEAKER_Y = 866                  # grayed-out "Name:" label
QUOTE_Y = 940                    # top of the quote block (never moves)
QUOTE_BOTTOM = 1440              # lowest published platform-overlay edge of the three
QUOTE_SIZES = (118, 110, 102, 94, 86, 79, 72, 66)
LINE_H = 1.19                    # multiple of the font size
MAX_LINES = 4
QUOTE_MAX_H = QUOTE_BOTTOM - QUOTE_Y   # a 4-line phrase auto-fits to 102 px; a 3-line
                                       # phrase keeps the full 118 px
TITLE_KICKER_Y, TITLE_MAIN_Y = 176, 214   # the opening overlay, over the first bite
TITLE_HOLD = 3.3                 # seconds the opening title stays up
WAVE_W, WAVE_H = 924, 300
PHRASE_HOLD = 1.15               # seconds a finished phrase lingers before clearing
PHRASE_TARGET, PHRASE_HARD = 38, 50   # on-screen phrase length, in characters
FIT_SLACK = 0.985                # libass vs. PIL metric safety margin
CAPTION_LINE = 42                # sidecar .vtt line limit (Netflix 42, BBC 37)
CAPTION_HOLD = 1.6               # max seconds a cue may run past its last word
CAPTION_GAP = 0.08               # minimum silence between consecutive cues
CAPTION_LEAD = 0.35              # a cue may come up slightly before its first word

LOUDNORM = "loudnorm=I=-14:TP=-1.2:LRA=11"  # reels/Shorts level (highlights use -16)

# Background-noise reduction, applied to the *continuous* source before the micro-cuts
# so the denoisers never have to re-adapt at a splice. RNNoise (arnndn) does the heavy
# lifting on room tone / HVAC / laptop fans; afftdn cleans up the residual hiss; the
# presence bell and the low/high cuts are for intelligibility on phone speakers.
# Measured on this recording: between-word level -29.7 -> -40.9 dBFS in the room and
# -25.6 -> -40.5 dBFS on the Teams call side, with the ASR transcript unchanged.
RNNOISE_MODEL = Path("/tmp/rnnoise-sh.rnnn")
RNNOISE_URL = ("https://raw.githubusercontent.com/GregorR/rnnoise-models/master/"
               "somnolent-hogwash-2018-09-01/sh.rnnn")


def denoise_chain(mode="full"):
    """mode="gentle" skips RNNoise; mode="none" is a no-op, for media recovered from an
    already-denoised render (running the chain twice thins the voice). RNNoise buys ~11 dB of background suppression and
    leaves normal speech untouched (measured: identical ASR word counts and avg_logprob
    across three sample spans), but it can swallow a near-whispered aside it does not
    classify as speech -- so an item can opt out with "denoise": "gentle" in the EDL."""
    if mode == "none":
        return "anull"
    parts = ["highpass=f=85"]
    if mode != "gentle" and RNNOISE_MODEL.exists():
        parts.append(f"arnndn=m={RNNOISE_MODEL}")
        parts.append("afftdn=nr=10:nf=-30:tn=1")
    else:                                    # ungated fallback: FFT denoise only
        parts.append("afftdn=nr=8:nf=-32:tn=1")
    parts += ["equalizer=f=3000:t=q:w=1.3:g=3", "lowpass=f=12000",
              "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=200"]
    return ",".join(parts)


def run(cmd, **kw):
    proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        sys.exit(f"FAILED ({proc.returncode}): {' '.join(str(c) for c in cmd)}\n"
                 f"{proc.stderr[-3000:]}")
    return proc


def snap(t):
    return round(t * FPS) / FPS


def frames_of(p):
    pr = run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames",
              "-show_entries", "stream=nb_read_frames", "-of", "default=nw=1:nk=1", p])
    return int(pr.stdout.strip())


def fmt_vtt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


# ------------------------------------------------------- text measurement & wrapping
_FONT_CACHE = {}


def _font(path, size):
    key = (str(path), size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(str(path), size)
    return _FONT_CACHE[key]


def text_w(s, path, size):
    return _font(path, size).getlength(s)


def _greedy_lines(words, size, width):
    """Greedy wrap of `words` (list of str) at `size`; returns list of index-lists."""
    lines, cur = [], []
    for i, w in enumerate(words):
        trial = " ".join(words[j] for j in cur + [i])
        if cur and text_w(trial, FONT_QUOTE, size) > width:
            lines.append(cur)
            cur = [i]
        else:
            cur.append(i)
    if cur:
        lines.append(cur)
    return lines


def wrap_phrase(words, force=None):
    """Pick the largest quote size at which `words` fits in <=MAX_LINES lines within the
    measure and the height budget, and return (size, lines) where `lines` are the FIXED
    line breaks used for every reveal step of this phrase. Fixing the breaks up front is
    the whole point: with them, a word that appears never moves again."""
    budget = TEXT_W * FIT_SLACK
    if force is not None:
        return force, _greedy_lines(words, force, budget)
    for size in QUOTE_SIZES:
        lines = _greedy_lines(words, size, budget)
        if len(lines) <= MAX_LINES and len(lines) * size * LINE_H <= QUOTE_MAX_H:
            if all(text_w(" ".join(words[j] for j in ln), FONT_QUOTE, size) <= budget
                   for ln in lines):
                return size, lines
    size = QUOTE_SIZES[-1]
    return size, _greedy_lines(words, size, budget)


# ---------------------------------------------------------------- audio per item
def _loudnorm_measured(path):
    meas = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", str(path), "-af", f"{LOUDNORM}:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]+\}\s*$", meas.stderr)
    if not m:
        return LOUDNORM
    j = json.loads(m.group(0))
    return (LOUDNORM + f":measured_I={j['input_i']}:measured_TP={j['input_tp']}"
            f":measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}"
            f":offset={j['target_offset']}:linear=true")


def _finish_audio(raw, work, iid):
    wav = work / f"{iid}.wav"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-i", raw,
         "-af", f"{_loudnorm_measured(raw)},aresample={AR},"
                f"aformat=channel_layouts=mono", wav])
    return wav


def render_item_audio(src, segs, work, iid, mode="full"):
    """Denoise the continuous source once, then a sample-exact concat of the
    keep-intervals with 15 ms anti-click fades at every micro-cut junction, then
    two-pass loudnorm. One seeked input; the 2 s pre-roll lets the denoisers settle."""
    base = max(0.0, min(s for s, _ in segs) - 2.0)
    raw = work / f"{iid}.raw.wav"
    n = len(segs)
    graph = [f"[0:a]aresample={AR},aformat=channel_layouts=mono,{denoise_chain(mode)},"
             f"asplit={n}" + "".join(f"[d{k}]" for k in range(n))]
    for k, (s, e) in enumerate(segs):
        d = e - s
        graph.append(
            f"[d{k}]atrim=start={s - base:.4f}:end={e - base:.4f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.015,afade=t=out:st={max(0.0, d - 0.015):.4f}:d=0.015[a{k}]")
    graph.append("".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1[a]")
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-ss", f"{base:.3f}",
         "-i", src, "-filter_complex", ";".join(graph), "-map", "[a]", raw])
    return _finish_audio(raw, work, iid)


def render_recovered_audio(pre_cut, work, iid, mode="full"):
    """Pre-cut item audio (the keep-intervals are already applied): denoise + loudnorm."""
    raw = work / f"{iid}.raw.wav"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-i", pre_cut,
         "-af", f"aresample={AR},aformat=channel_layouts=mono,{denoise_chain(mode)}", raw])
    return _finish_audio(raw, work, iid)


# ---------------------------------------------------------------- video per item
def _fit_visual():
    """scale/pad expression placing any source inside the visual zone, centered."""
    return (f"scale={VIS_W}:{VIS_H}:force_original_aspect_ratio=decrease:"
            f"force_divisible_by=2,fps={FPS}")


def _crop_of(crop, k):
    """crop: [w,h,x,y] for every segment, or a per-segment list of those (null = none).
    Source coordinates, applied before the fit into the visual zone -- this is how a
    1920x1080 screen share becomes legible on a 1080-wide phone frame: crop to the part
    of the screen being talked about, then scale that up instead of the whole desktop."""
    if not crop:
        return None
    if isinstance(crop[0], (list, type(None))):
        crop = crop[k] if k < len(crop) else None
    return f"crop={crop[0]}:{crop[1]}:{crop[2]}:{crop[3]}" if crop else None


def _redactions_of(redact, s, e):
    """Timed black boxes in source coordinates, applied before the crop. Used where the
    screen share exposes something that must not be published (see the EDL's `why`)."""
    out = []
    for r in redact or []:
        a, b = r["t"]
        if b <= s or a >= e:
            continue
        w, h, x, y = r["rect"]
        lo, hi = max(0.0, a - s), min(e - s, b - s)
        en = f":enable='between(t,{lo:.3f},{hi:.3f})'"
        out.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black:t=fill{en}")
        if r.get("label"):
            out.append(f"drawtext=fontfile={FONT_LABEL}:text='{r['label']}':"
                       f"x={x}+({w}-text_w)/2:y={y}+({h}-text_h)/2:fontsize=34:"
                       f"fontcolor=white@0.34{en}")
    return out


def render_item_video(src, segs, work, iid, fade_in=0.0, crop=None, redact=None):
    """Footage item: the source, fitted into the visual zone on black."""
    cmd = ["ffmpeg", "-y", "-nostdin", "-loglevel", "error"]
    graph, durs = [], []
    for k, (s, e) in enumerate(segs):
        d = snap(e) - snap(s)
        durs.append(d)
        cmd += ["-ss", f"{snap(s):.4f}", "-to", f"{snap(e) + 0.25:.4f}", "-i", src]
        pre = _redactions_of(redact, snap(s), snap(e))
        cs = _crop_of(crop, k)
        if cs:
            pre.append(cs)
        pre = ",".join(pre) + "," if pre else ""
        graph.append(f"[{k}:v]{pre}{_fit_visual()},setpts=PTS-STARTPTS,"
                     f"tpad=stop_mode=clone:stop_duration=0.3,trim=end={d:.6f}[v{k}]")
    total = sum(durs)
    graph.append("".join(f"[v{k}]" for k in range(len(segs))) +
                 f"concat=n={len(segs)}:v=1:a=0[vc]")
    cmd += ["-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={total:.4f}"]
    post = [f"fade=t=in:d={fade_in}"] if fade_in else []
    post += ["setsar=1", "format=yuv420p"]
    graph.append(f"[{len(segs)}:v][vc]overlay=(main_w-overlay_w)/2:"
                 f"{VIS_Y}+({VIS_H}-overlay_h)/2:eof_action=pass,"
                 f"{','.join(post)}[v]")
    out = work / f"{iid}.video.mp4"
    run(cmd + ["-filter_complex", ";".join(graph), "-map", "[v]", "-t", f"{total:.6f}",
               "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])
    return out


def render_recovered_video(pre_cut, dur, work, iid, fade_in=0.0):
    post = [f"fade=t=in:d={fade_in}"] if fade_in else []
    post += ["setsar=1", "format=yuv420p"]
    graph = (f"[1:v]{_fit_visual()},setpts=PTS-STARTPTS[fg];"
             f"[0:v][fg]overlay=(main_w-overlay_w)/2:{VIS_Y}+({VIS_H}-overlay_h)/2:"
             f"eof_action=pass,{','.join(post)}[v]")
    out = work / f"{iid}.video.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={dur:.4f}",
         "-i", pre_cut, "-filter_complex", graph, "-map", "[v]", "-t", f"{dur:.4f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])
    return out


def render_card_item_video(wav, dur, work, iid, fade_in=0.0):
    """Text-only item: black frame with a live waveform of the (already cut) audio
    sitting in the visual zone, so audio-only bites keep the same composition as
    footage bites. The words themselves come from the ASS track."""
    post = [f"fade=t=in:d={fade_in}"] if fade_in else []
    post += ["setsar=1", "format=yuv420p"]
    wy = VIS_Y + (VIS_H - WAVE_H) // 2
    graph = (f"[1:a]aformat=channel_layouts=mono,"
             f"showwaves=s={WAVE_W}x{WAVE_H}:mode=cline:rate={FPS}:"
             f"colors=0xFFFFFF@0.46[wv];"
             f"[0:v][wv]overlay={SAFE_L}:{wy}:eof_action=pass,{','.join(post)}[v]")
    out = work / f"{iid}.video.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={dur:.4f}",
         "-i", wav, "-filter_complex", graph, "-map", "[v]", "-t", f"{dur:.4f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])
    return out


def mux_item(video, wav, work, iid):
    nf = frames_of(video)
    out = work / f"{iid}.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-i", video, "-i", wav,
         "-map", "0:v", "-map", "1:a",
         "-af", f"apad,atrim=end={nf / FPS:.6f},asetpts=PTS-STARTPTS",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", str(AR), "-ac", "1", out])
    return out, nf / FPS


# ---------------------------------------------------------------- title / end cards
def drawtext(font, textfile, y, size, color="white", x=SAFE_L):
    return (f"drawtext=fontfile={font}:textfile={textfile}:x={x}:y={y}:"
            f"fontsize={size}:fontcolor={color}:line_spacing=16")


def render_card(work, iid, card, kind):
    d = snap(card["dur"])

    def tf(tag, text):
        p = work / f"{iid}_{tag}.txt"
        p.write_text(text)
        return p

    vf = []
    if kind == "title":
        vf += [drawtext(FONT_LABEL, tf("k", card["kicker"]), 660, 32, "white@0.55"),
               drawtext(FONT_TITLE, tf("t", card["title"]), 740, 126),
               f"drawbox=x={SAFE_L}:y={card.get('rule_y', 1010)}:w=150:h=5:"
               f"color=white@0.5:t=fill",
               drawtext(FONT_BODY, tf("s", card["sub"]), card.get("sub_y", 1058), 44,
                        "white@0.8")]
    else:  # end card
        lines = card["lines"]
        y = 860 - 30 * len(lines)
        for i, line in enumerate(lines):
            if line:
                bold = i in card.get("bold", (0,))
                vf.append(drawtext(FONT_QUOTE if bold else FONT_BODY, tf(f"l{i}", line),
                                   y + 70 * i, 48 if bold else 36,
                                   "white" if bold else "white@0.72"))
    fade_out = 0.8 if kind == "end" else 0.35
    vf += ["fade=t=in:d=0.3", f"fade=t=out:st={d - fade_out:.2f}:d={fade_out}",
           "setsar=1", "format=yuv420p"]
    out = work / f"{iid}.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={BG}:s={W}x{H}:r={FPS}:d={d}",
         "-f", "lavfi", "-t", str(d), "-i", f"anullsrc=r={AR}:cl=mono",
         "-vf", ",".join(vf), "-shortest",
         "-c:v", "libx264", "-preset", "fast", "-crf", "17",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(AR), "-ac", "1", out])
    return out, d


# ---------------------------------------------------------------- text reveal (ASS)
# WrapStyle 2 = never auto-wrap: only the \N breaks this script computes are used, so
# libass cannot reflow a line as words are added. Alignment 7/4 keep the block
# left-aligned and top-anchored at a fixed MarginV, so a partially revealed line does
# not re-centre itself.
ASS_HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Speaker,Inter Medium,46,&H00A6A6A6,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,7,{SAFE_L},{SAFE_R},{SPEAKER_Y},1
Style: Part,Inter Medium,34,&H00787878,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,7,{SAFE_L},{SAFE_L},{VIS_Y - 74},1
Style: Quote,Inter SemiBold,118,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,{SAFE_L},{SAFE_R},{QUOTE_Y},1
Style: TitleKicker,Inter Medium,30,&H008C8C8C,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,0,7,{SAFE_L},{SAFE_L},{TITLE_KICKER_Y},1
Style: TitleMain,Inter Display SemiBold,58,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,{SAFE_L},{SAFE_L},{TITLE_MAIN_Y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Text
"""


def ass_time(t):
    cs = max(0, round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def esc(text):
    return text.replace("{", "(").replace("}", ")").replace("\n", "\\N")


def item_phrases(it):
    """The on-screen phrases of one laid-out item. Footage items get shorter phrases:
    they are shown as one static block rather than revealed word-by-word, and a short
    block is what keeps the split-attention cost down when there is also something to
    look at. Both the burned text and the sidecar captions come from this one function,
    so the .vtt can never drift from what the viewer sees."""
    static = is_static(it)
    return chunk_phrases(it.get("words") or [],
                         *((30, 40) if static else (PHRASE_TARGET, PHRASE_HARD)))


def is_static(it):
    """True where the frame already carries information -- footage, a screen share -- so
    the quote is presented as a finished block instead of growing word by word."""
    return it.get("visual", "card") != "card"


def chunk_phrases(words, target=None, hard=None):
    """Split kept words into on-screen phrases: break at sentence enders, em-dashes,
    or ~PHRASE_TARGET chars at a natural gap. words: [[out_t0, out_t1, text], ...].
    v4 shortens the target from 54/72 to 38/50 characters: the safe-area measure is
    768 px rather than 924 and the block is three lines rather than four, so a shorter
    phrase is what keeps the auto-fit near the top of QUOTE_SIZES instead of shrinking
    the type. It also lands most sidecar cues inside the 42-character caption limit."""
    target = PHRASE_TARGET if target is None else target
    hard = PHRASE_HARD if hard is None else hard
    phrases, cur, cur_len = [], [], 0
    for i, w in enumerate(words):
        cur.append(w)
        cur_len += len(w[2]) + 1
        gap = (words[i + 1][0] - w[1]) if i + 1 < len(words) else 99
        ender = w[2].rstrip('"”').endswith((".", "?", "!", "—", ":"))
        if ender or (cur_len >= target and gap >= 0.22) or cur_len >= hard:
            phrases.append(cur)
            cur, cur_len = [], 0
    if cur:
        phrases.append(cur)
    return phrases


def reveal_text(words, lines, upto):
    """Words 0..upto laid out on the phrase's FIXED line breaks."""
    parts = []
    for ln in lines:
        seg = [words[j] for j in ln if j <= upto]
        if not seg:
            break
        parts.append(" ".join(seg))
    return "\\N".join(parts)


def build_ass(layout, path, title=None):
    """layout: [{offset, dur, speakers, part, visual, words:[[t0,t1,text] item-local]}].
    `title` (kicker + title) fades in over the FIRST item instead of being a silent card
    in front of the cut, so the reel opens on a voice and a quote."""
    ev = []
    for n, it in enumerate(layout):
        off, dur = it["offset"], it["dur"]
        for a, b, lab in it.get("speakers") or []:
            ev.append(("Speaker", off + a + (0.10 if a == 0 else 0.0),
                       off + min(b, dur) - 0.04, esc(lab), ""))
        # the opening title occupies the part label's slot on item 0
        if it.get("part") and not (n == 0 and title):
            ev.append(("Part", off + 0.10, off + min(3.4, dur),
                       esc(it["part"].upper()), "{\\fad(260,420)}"))
        phrases = item_phrases(it)
        fitted = [wrap_phrase([w[2] for w in ph]) for ph in phrases]
        # one type size for the whole item: the smallest any of its phrases needs, so
        # the quote never changes size on screen inside a bite
        item_size = min((f[0] for f in fitted), default=QUOTE_SIZES[0])
        static = is_static(it)
        for phrase in phrases:
            texts = [w[2] for w in phrase]
            _, lines = wrap_phrase(texts, item_size)
            tag = f"{{\\fs{item_size}}}"
            last_end = phrase[-1][1]
            nxt = next((w[0] for w in it["words"] if w[0] > last_end + 1e-6), None)
            close = min(dur, last_end + PHRASE_HOLD, nxt if nxt is not None else 9e9)
            if static:
                # whole block at once: over footage the viewer is already reading the
                # frame, and a growing line of text is the split-attention case
                st, en = off + phrase[0][0], off + close
                ev.append(("Quote", st, max(en, st + 0.02),
                           esc(reveal_text(texts, lines, len(texts) - 1)),
                           tag + "{\\fad(180,240)}"))
                continue
            for i, w in enumerate(phrase):
                st = off + w[0]
                en = off + (phrase[i + 1][0] if i + 1 < len(phrase) else close)
                if en - st < 0.01:
                    en = st + 0.01
                pre = tag
                if i == 0:
                    pre += "{\\fad(130,0)}"
                if i == len(phrase) - 1:
                    pre += "{\\fad(0,240)}"
                ev.append(("Quote", st, en, esc(reveal_text(texts, lines, i)), pre))
    if title:
        ev.append(("TitleKicker", 0.12, TITLE_HOLD,
                   esc(title["kicker"]), "{\\fad(300,520)}"))
        ev.append(("TitleMain", 0.20, TITLE_HOLD + 0.15,
                   esc(title["title"].replace("\n", " ")), "{\\fad(300,520)}"))
    out = [ASS_HEAD]
    for style, st, en, text, pre in ev:
        out.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},{style},,0,0,0,{pre}{text}")
    Path(path).write_text("\n".join(out) + "\n")


# ------------------------------------------------------------------ sidecar captions
def wrap_caption(text, limit=CAPTION_LINE):
    """Balanced wrap of one cue to at most two lines of <= `limit` characters."""
    if len(text) <= limit:
        return [text]
    words, best = text.split(), None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if len(a) > limit or len(b) > limit:
            continue
        score = abs(len(a) - len(b))
        if best is None or score < best[0]:
            best = (score, [a, b])
    if best:
        return best[1]
    lines, cur = [], ""                      # fall back to a greedy fill
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def speaker_at(it, t):
    for a, b, lab in it.get("speakers") or []:
        if a - 0.01 <= t < b:
            return lab.rstrip(":").strip()
    return None


def build_vtt(layout, path):
    """A real caption track, not a transcript dump. Cues are the same phrases that are
    burned into the picture; each one is clamped so it ends before the next begins
    (WebVTT leaves overlapping cues undefined and YouTube's ingest handles them
    inconsistently), extended into any following silence to bring the reading rate
    down, wrapped to <= CAPTION_LINE characters over at most two lines, and tagged with
    the speaker -- WCAG 1.2.2 requires captions to identify who is talking, and the
    burned render already knows."""
    cues = []
    for it in layout:
        for phrase in item_phrases(it):
            cues.append({"s": it["offset"] + phrase[0][0],
                         "e": it["offset"] + phrase[-1][1],
                         "text": " ".join(w[2] for w in phrase),
                         "spk": speaker_at(it, phrase[0][0])})
    cues.sort(key=lambda c: c["s"])
    end_of_reel = layout[-1]["offset"] + layout[-1]["dur"] if layout else 0.0
    for i, c in enumerate(cues):                     # a caption may lead its audio a
        prev = cues[i - 1]["e"] if i else 0.0        # little; it may never lag it
        c["s"] = max(c["s"] - CAPTION_LEAD, prev + CAPTION_GAP, 0.0)
    for i, c in enumerate(cues):
        nxt = cues[i + 1]["s"] if i + 1 < len(cues) else end_of_reel
        c["e"] = max(c["s"] + 0.4, min(c["e"] + CAPTION_HOLD, nxt - CAPTION_GAP))
    out = ["WEBVTT", ""]
    for c in cues:
        body = "\n".join(wrap_caption(c["text"]))
        if c["spk"]:
            body = f"<v {c['spk']}>{body}"
        out += [f"{fmt_vtt(c['s'])} --> {fmt_vtt(c['e'])}", body, ""]
    Path(path).write_text("\n".join(out))
    return cues


# ---------------------------------------------------------------- final join
def join_reel(pieces, ass_path, out_path):
    durs = [frames_of(p) / FPS for p in pieces]
    graph = []
    for i, d in enumerate(durs):
        graph.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}];"
                     f"[{i}:a]aresample={AR},apad,atrim=end={d:.6f},"
                     f"asetpts=PTS-STARTPTS[a{i}]")
    graph.append("".join(f"[v{i}][a{i}]" for i in range(len(durs))) +
                 f"concat=n={len(durs)}:v=1:a=1[vc][aout]")
    graph.append(f"[vc]ass={ass_path}:fontsdir={INTER}[vout]")
    gf = Path(ass_path).with_suffix(".graph.txt")
    gf.write_text(";\n".join(graph))
    cmd = ["ffmpeg", "-y", "-nostdin", "-loglevel", "error"]
    for p in pieces:
        cmd += ["-i", p]
    cmd += ["-filter_complex_script", gf, "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out_path]
    run(cmd)
    return durs


# ---------------------------------------------------------------- main
def item_words_local(item):
    """Map source-time words to item-local output time through the keep-intervals."""
    segs = [(snap(s), snap(e)) for s, e in item["segments"]]
    out, acc = [], 0.0
    for s, e in segs:
        for t0, t1, txt in item["words"]:
            if t0 >= s - 0.02 and t0 < e:
                lt0 = acc + max(0.0, t0 - s)
                lt1 = acc + min(e - s, max(0.0, t1 - s))
                out.append([round(lt0, 3), round(max(lt1, lt0 + 0.05), 3), txt])
        acc += e - s
    return out, acc


def item_speakers_local(item, dur):
    """Map the item's diarized speaker turns onto item-local time through the same
    keep-intervals, so the grayed-out label follows whoever is actually talking. Falls
    back to a single label covering the item when the EDL has no turns for it."""
    spans = item.get("speaker_spans")
    if not spans:
        return [[0.0, dur, item["speaker"]]] if item.get("speaker") else []
    segs = [(snap(s), snap(e)) for s, e in item["segments"]]
    out, acc = [], 0.0
    for s, e in segs:
        for t0, t1, lab in spans:
            a, b = max(t0, s), min(t1, e)
            if b - a <= 0.05:
                continue
            out.append([round(acc + a - s, 3), round(acc + b - s, 3), lab])
        acc += e - s
    out.sort()
    merged = []
    for a, b, lab in out:                       # stitch turns split by a micro-cut
        if merged and merged[-1][2] == lab and a - merged[-1][1] < 0.6:
            merged[-1][1] = b
        else:
            merged.append([a, b, lab])
    if merged:
        merged[0][0] = 0.0                      # label is up from the first frame
        for i in range(len(merged) - 1):        # no gaps: a name stays until the next
            merged[i][1] = merged[i + 1][0]
        merged[-1][1] = dur
    return [m for m in merged if m[1] - m[0] > 0.35]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="original meeting MP4 (75:34)")
    ap.add_argument("--clips-dir", default=None, help="breakout clips (<id>.mp4)")
    ap.add_argument("--recovered", default=None,
                    help="manifest of pre-cut item media for unreachable sources")
    ap.add_argument("--workdir", default="/tmp/reels-build")
    ap.add_argument("--outdir", default=None, help="default: workdir")
    ap.add_argument("--only", default=None, help="render just this reel id")
    args = ap.parse_args()

    edl = json.load(open(HERE / "reels-edl.json"))
    recovered = json.load(open(args.recovered)) if args.recovered else {}
    outdir = Path(args.outdir or args.workdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if not RNNOISE_MODEL.exists():
        print(f"note: {RNNOISE_MODEL} absent -- falling back to afftdn-only denoise "
              f"(fetch it from {RNNOISE_URL})", flush=True)

    for reel in edl["reels"]:
        if args.only and reel["id"] != args.only:
            continue
        work = Path(args.workdir) / reel["id"]
        work.mkdir(parents=True, exist_ok=True)
        pieces, layout, cursor = [], [], 0.0
        chapters = []

        def add(path, dur, lay=None):
            nonlocal cursor
            pieces.append(path)
            if lay:
                lay.update(offset=cursor, dur=dur)
                layout.append(lay)
            cursor += dur

        # v4: no silent branded card in front of the cut -- the title fades in over
        # the first bite instead (see build_ass), so frame 1 already has a voice on it.
        title = reel.get("title_card")
        if title and title.get("dur"):
            p, d = render_card(work, "card_title", title, "title")
            add(p, d)
            title = None
        for n, item in enumerate(reel["items"]):
            iid = f"i{n:02d}_{item['id']}"
            key = f"{reel['id']}__{item['id']}"
            fade_in = 0.25 if n == 0 else 0.0
            words, planned = item_words_local(item)
            if key in recovered:
                rec = recovered[key]
                wav = render_recovered_audio(
                    rec["audio"], work, iid,
                    rec.get("denoise", item.get("denoise", "full")))
                if rec.get("video"):
                    video = render_recovered_video(rec["video"], rec["dur"], work, iid,
                                                   fade_in)
                else:
                    video = render_card_item_video(wav, rec["dur"], work, iid, fade_in)
            else:
                src = (args.source if item["src"] == "meeting"
                       else str(Path(args.clips_dir) / f"{item['src']}.mp4"))
                segs = [(snap(s), snap(e)) for s, e in item["segments"]]
                wav = render_item_audio(src, segs, work, iid,
                                        item.get("denoise", "full"))
                if item.get("visual", "card") == "card":
                    video = render_card_item_video(wav, planned, work, iid, fade_in)
                else:
                    video = render_item_video(src, segs, work, iid, fade_in,
                                              item.get("crop"), item.get("redact"))
            piece, dur = mux_item(video, wav, work, iid)
            if item.get("chapter"):
                chapters.append((cursor, item["chapter"]))
            add(piece, dur, {"speakers": item_speakers_local(item, dur),
                             "part": item.get("part"), "words": words,
                             "visual": item.get("visual", "card")})
            print(f"  {reel['id']} {iid}: {dur:.2f}s ({len(words)} words)", flush=True)
        p, d = render_card(work, "card_end", reel["end_card"], "end")
        add(p, d)

        ass_path = work / f"{reel['id']}.ass"
        build_ass(layout, ass_path, title)
        final = outdir / f"{reel['output_basename']}.mp4"
        join_reel(pieces, ass_path, final)

        # sidecar captions (phrase-level) on the reel timeline
        build_vtt(layout, outdir / f"{reel['output_basename']}.vtt")
        if chapters and reel.get("chapters_sidecar"):
            if chapters[0][0] <= snap(reel["title_card"].get("dur", 0.0)) + 0.5:
                chapters[0] = (0.0, chapters[0][1])   # first bite owns 0:00
            else:
                chapters.insert(0, (0.0, reel.get("chapter0", "Cold open")))
            ch = [f"{int(t // 60)}:{int(t % 60):02d} {name}" for t, name in chapters]
            (outdir / f"{reel['output_basename']}.chapters.txt").write_text(
                "\n".join(ch) + "\n")
        pr = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                  "-of", "default=nw=1:nk=1", final])
        print(f"{reel['id']}: {final}  {float(pr.stdout.strip()):.2f}s "
              f"(planned {cursor:.2f}s)", flush=True)


if __name__ == "__main__":
    main()

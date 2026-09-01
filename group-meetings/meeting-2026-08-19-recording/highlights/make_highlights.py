#!/usr/bin/env python3
"""Render the AI-in-the-lab highlights compilation from the 2026-08-19 meeting recording
plus the seven break-off pair-discussion clips from the channel.

Reads edl.json (meeting-clip boundaries on the original 75:34 timeline; breakout-clip
boundaries on each clip's own timeline) plus the Teams transcript (../transcript.vtt for
caption text, ../transcript.json for speaker IDs) and per-clip whisper captions
(sources/<id>.vtt), then uses ffmpeg to cut each piece frame-accurately with burned
captions, a source bug (meeting timecode or youtu.be link), and two-pass loudness
normalization; normalizes breakout footage to the 1920x1080 canvas (portrait phone
clips pillarboxed on the card navy); generates title cards; concatenates everything;
and emits sidecar captions/chapters on the output timeline.

Usage:
    python3 make_highlights.py --source /path/to/original.mp4 \
        --clips-dir /path/to/clips --workdir /tmp/build

2026-08-29 (implementing ../best-practices/ finding 1): the delivered audio was
16 kHz mono at 96 kbps and undenoised -- an 8 kHz bandwidth ceiling, telephone-grade,
on the artifact most likely to be watched by someone outside the lab. Degraded audio is
the single most costly thing in the whole evidence review: it lowers judged credibility
and measurably impairs memory for the facts being stated, and listeners attribute the
fault to the speaker rather than the microphone. Delivery is now 48 kHz at 160 kbps and
the reels' noise-reduction chain runs ahead of the loudness normalization, with a
DENOISE_PREROLL of source audio in front of every cut so the denoisers are settled
before the first frame. The sidecar captions are also a real caption track now: cues
never overlap, lines wrap at 42 characters, and speakers are tagged (findings 3 and 4).

The meeting MP4 is not in git — re-fetch it with `yt-dlp -f source "<share link>"`
(see ../README.md). The breakout clips are the YouTube uploads listed in
edl.json["sources"], one <id>.mp4 per clip in --clips-dir (download recipe in
README.md here; they also live on the stream-cam Pi under ~/vcl-ai-clips/).
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
NAVY = "0x002E5D"  # BYU royal blue

SUB_STYLE = ("FontName=DejaVu Sans,FontSize=13,PrimaryColour=&H00FFFFFF,"
             "OutlineColour=&H88000000,BorderStyle=1,Outline=1.2,Shadow=0.6,MarginV=24")
MIN_CAPTION_S = 0.7  # drop caption fragments shorter than this after clamping
CAPTION_LINE = 42    # sidecar .vtt line limit (Netflix 42, BBC 37)
CAPTION_GAP = 0.08   # minimum silence between consecutive sidecar cues
CAPTION_HOLD = 1.2   # max seconds a sidecar cue may run past its transcript end

# Background-noise reduction, ported from the reels renderer (../reels/make_reels.py):
# 85 Hz high-pass -> RNNoise -> residual FFT denoise -> presence bell -> 12 kHz low-pass
# -> gentle compression. Applied to a window of continuous source audio that starts
# DENOISE_PREROLL seconds before the cut, so the adaptive stages are settled by the time
# the piece begins; the pre-roll is trimmed off before loudness normalization.
RNNOISE_MODEL = Path("/tmp/rnnoise-sh.rnnn")
RNNOISE_URL = ("https://raw.githubusercontent.com/GregorR/rnnoise-models/master/"
               "somnolent-hogwash-2018-09-01/sh.rnnn")
DENOISE_PREROLL = 2.0


def denoise_chain():
    parts = ["highpass=f=85"]
    if RNNOISE_MODEL.exists():
        parts += [f"arnndn=m={RNNOISE_MODEL}", "afftdn=nr=10:nf=-30:tn=1"]
    else:                                    # ungated fallback: FFT denoise only
        parts.append("afftdn=nr=8:nf=-32:tn=1")
    parts += ["equalizer=f=3000:t=q:w=1.3:g=3", "lowpass=f=12000",
              "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=200"]
    return ",".join(parts)


def audio_source_args(source, s, e):
    """Input args for a second, audio-only read of `source` carrying the pre-roll."""
    return ["-ss", f"{max(0.0, s - DENOISE_PREROLL):.3f}", "-to", f"{e:.3f}",
            "-i", str(source)]


def denoise_prefix(s):
    """Filter prefix that denoises the pre-rolled window and trims back to the cut."""
    lead = s - max(0.0, s - DENOISE_PREROLL)
    return f"{denoise_chain()},atrim=start={lead:.3f},asetpts=PTS-STARTPTS"


SIDECARS_ONLY = False   # set by --sidecars-only: reuse the pieces already rendered
                        # into the workdir and only re-emit the .vtt / chapters


def encode(out, cmd):
    """Run an encode unless we are only re-emitting the text sidecars."""
    if SIDECARS_ONLY and Path(out).exists():
        return
    run(cmd)


def run(cmd, **kw):
    proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        sys.exit(f"FAILED ({proc.returncode}): {' '.join(str(c) for c in cmd)}\n{proc.stderr[-3000:]}")
    return proc


def parse_ts(ts):
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def load_cues(vtt_path, json_path, fixes):
    """VTT display cues (nicely chunked) tagged with speakers from the JSON entries."""
    entries = []
    for e in json.load(open(json_path))["entries"]:
        entries.append((parse_ts(e["startOffset"]), parse_ts(e["endOffset"]), e["speakerDisplayName"]))
    cues = []
    for block in re.split(r"\n\n+", open(vtt_path).read()):
        m = re.search(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)", block)
        if not m:
            continue
        st, en = parse_ts(m.group(1)), parse_ts(m.group(2))
        text = re.sub(r"</?v[^>]*>", "", block[m.end():]).replace("\n", " ").strip()
        for old, new in fixes:
            text = text.replace(old, new)
        spk = next((s for (a, b, s) in entries if a - 0.25 <= st and en <= b + 0.25), None)
        cues.append({"s": st, "e": en, "spk": spk, "text": text})
    return sorted(cues, key=lambda c: c["s"])


def load_simple_cues(vtt_path, fixes):
    """Display cues from a plain WEBVTT (the whisper-generated breakout captions)."""
    cues = []
    for block in re.split(r"\n\n+", Path(vtt_path).read_text()):
        m = re.search(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)", block)
        if not m:
            continue
        text = block[m.end():].replace("\n", " ").strip()
        for old, new in fixes:
            text = text.replace(old, new)
        cues.append({"s": parse_ts(m.group(1)), "e": parse_ts(m.group(2)),
                     "spk": None, "text": text})
    return sorted(cues, key=lambda c: c["s"])


def fmt_srt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def fmt_vtt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


def piece_captions(cues, piece, edl, in_breakout, default_spk=None):
    """Caption cues for one piece, clamped to it and shifted to piece-local time."""
    s, e = piece["s"], piece["e"]
    out, last_spk = [], None
    kept = [c for c in cues if c["e"] > s + 0.05 and c["s"] < e - 0.05]
    if in_breakout:
        kept = [c for c in kept if c["spk"] != "@3" and len(c["text"].split()) > 2]
    for c in kept:
        cs, ce = max(c["s"], s), min(c["e"], e)
        if ce - cs < MIN_CAPTION_S:
            continue
        text = c["text"]
        name = edl["speaker_names"].get(c["spk"] or "")
        if in_breakout and name and c["spk"] != last_spk:
            text = f"{name}: {text}"
        last_spk = c["spk"]
        out.append({"s": cs - s, "e": ce - s, "text": text,
                    "spk": name or default_spk})
    if out and piece.get("cap_last_text"):
        out[-1]["text"] = piece["cap_last_text"]
    # Teams cue spans overlap each other by up to 0.33 s. Burned in, that makes libass
    # push the colliding cue off its line; in the sidecar it is undefined WebVTT. Clamp
    # each cue to end before the next one starts, and drop anything left degenerate.
    for a, b in zip(out, out[1:]):
        a["e"] = min(a["e"], b["s"] - CAPTION_GAP)
    return [c for c in out if c["e"] - c["s"] >= 0.25]


def wrap_caption(text, limit=CAPTION_LINE):
    """Balanced wrap of one cue to at most two lines of <= `limit` characters."""
    if len(text) <= limit:
        return [text]
    words, best = text.split(), None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if len(a) <= limit and len(b) <= limit:
            score = abs(len(a) - len(b))
            if best is None or score < best[0]:
                best = (score, [a, b])
    if best:
        return best[1]
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def loudnorm_measure(source, s, e):
    """Measured on the DENOISED signal -- measuring the raw cut and then denoising it
    would leave the correction pass working from the wrong numbers."""
    proc = subprocess.run(
        ["ffmpeg", "-nostdin", *audio_source_args(source, s, e), "-vn",
         "-af", f"{denoise_prefix(s)},loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"\{[^{}]+\}\s*$", proc.stderr)
    return json.loads(m.group(0)) if m else None


def snap(t, fps=16):
    """Snap a time to the frame grid so video/audio piece durations match exactly."""
    return round(t * fps) / fps


def render_piece(source, work, idx, piece, item, edl, cues):
    s, e = snap(piece["s"]), snap(piece["e"])
    piece = dict(piece, s=s, e=e)
    d = e - s
    in_breakout = not item.get("src") and any(a <= s <= b for a, b in edl["breakout_ranges"])
    caps = piece_captions(cues, piece, edl, in_breakout,
                          default_spk=item.get("names"))
    srt = work / f"cap_{idx:02d}.srt"
    srt.write_text("".join(f"{i + 1}\n{fmt_srt(c['s'])} --> {fmt_srt(c['e'])}\n{c['text']}\n\n"
                           for i, c in enumerate(caps)) or "1\n00:00:00,000 --> 00:00:00,100\n\n\n")

    vf = []
    if item.get("src"):  # breakout clip: normalize to canvas (portrait -> navy pillarbox)
        w, h = edl["video"]["width"], edl["video"]["height"]
        vf += [f"scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2",
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={NAVY}"]
    vf += [f"fps={edl['video']['fps']}", f"subtitles=filename={srt}:force_style='{SUB_STYLE}'"]
    if piece.get("label"):  # pair + topic attribution, top left, first seconds only
        lab = work / f"lab_{idx:02d}.txt"
        lab.write_text(piece["label"])
        vf.append(f"drawtext=fontfile={FONT}:textfile={lab}:x=44:y=40:fontsize=30:"
                  f"fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=10:enable='lte(t,4.0)'")
    if piece.get("bug"):  # source timecode / clip link, top right, first seconds only
        bug = work / f"bug_{idx:02d}.txt"
        bug.write_text(piece["bug"])
        vf.append(f"drawtext=fontfile={FONT}:textfile={bug}:x=w-tw-44:y=40:fontsize=30:"
                  f"fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=10:enable='lte(t,3.2)'")
    if piece.get("video_fade_in"):
        vf.append(f"fade=t=in:d={piece['video_fade_in']}")
    if piece.get("video_fade_out"):
        fo = piece["video_fade_out"]
        vf.append(f"fade=t=out:st={d - fo:.3f}:d={fo}")
    vf += ["setsar=1", "format=yuv420p"]  # uniform SAR: scaled pieces must match at concat

    ln = "loudnorm=I=-16:TP=-1.5:LRA=11"
    meas = loudnorm_measure(source, s, e)
    if meas:
        ln += (f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
               f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
               f":offset={meas['target_offset']}:linear=true")
    afade_out = max(piece.get("video_fade_out") or 0.12, 0.12)
    graph = (f"[0:v]{','.join(vf)}[vout];"
             f"[1:a]{denoise_prefix(s)},{ln},aresample={edl['audio']['rate']},"
             f"afade=t=in:d=0.10,afade=t=out:st={d - afade_out:.3f}:d={afade_out}[aout]")

    out = work / f"piece_{idx:02d}.mp4"
    encode(out, ["ffmpeg", "-y", "-nostdin", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", source,
         *audio_source_args(source, s, e),
         "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]", "-t", f"{d:.6f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
         "-video_track_timescale", "16000",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(edl["audio"]["rate"]), "-ac", "1", out])
    return out, caps, d


def drawtext(font, textfile, y, size, color="white", x="160"):
    return (f"drawtext=fontfile={font}:textfile={textfile}:x={x}:y={y}:"
            f"fontsize={size}:fontcolor={color}")


def render_audio_piece(source, work, idx, piece, item, edl, cues):
    """Audio-only breakout bite: navy card with pair names, topic, live waveform,
    and burned captions. Most in-person pairs set the phone face-up while recording,
    so their clips are audio with ceiling video -- this presents them honestly."""
    s, e = snap(piece["s"]), snap(piece["e"])
    piece = dict(piece, s=s, e=e)
    d = e - s
    caps = piece_captions(cues, piece, edl, False,
                          default_spk=item.get("names"))
    srt = work / f"cap_{idx:02d}.srt"
    srt.write_text("".join(f"{i + 1}\n{fmt_srt(c['s'])} --> {fmt_srt(c['e'])}\n{c['text']}\n\n"
                           for i, c in enumerate(caps)) or "1\n00:00:00,000 --> 00:00:00,100\n\n\n")

    def tf(tag, text):
        p = work / f"audio_{idx:02d}_{tag}.txt"
        p.write_text(text)
        return p

    w, h, fps = edl["video"]["width"], edl["video"]["height"], edl["video"]["fps"]
    vf = [drawtext(FONT, tf("k", item.get("kicker", "THE BREAKOUTS · AUDIO RECORDING")),
                   356, 26, "white@0.62"),
          drawtext(FONT_BOLD, tf("n", item["names"]), 408, 76),
          "drawbox=x=164:y=540:w=130:h=3:color=white@0.5:t=fill",
          drawtext(FONT, tf("t", item.get("topic", "")), 576, 34, "white@0.85"),
          f"subtitles=filename={srt}:force_style='{SUB_STYLE}'"]
    if piece.get("bug"):
        bug = work / f"bug_{idx:02d}.txt"
        bug.write_text(piece["bug"])
        vf.append(f"drawtext=fontfile={FONT}:textfile={bug}:x=w-tw-44:y=40:fontsize=30:"
                  f"fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=10:enable='lte(t,3.2)'")
    vf += ["setsar=1", "format=yuv420p"]

    ln = "loudnorm=I=-16:TP=-1.5:LRA=11"
    meas = loudnorm_measure(source, s, e)
    if meas:
        ln += (f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
               f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
               f":offset={meas['target_offset']}:linear=true")
    afade_out = 0.12
    graph = (
        f"[0:a]{denoise_prefix(s)},aresample={edl['audio']['rate']},asplit=2[aw][ao];"
        f"[aw]showwaves=s={w}x200:mode=cline:rate={fps}:colors=0xFFFFFF@0.40[wv];"
        f"[1:v][wv]overlay=0:660:eof_action=pass[v0];"
        f"[v0]{','.join(vf)}[vout];"
        f"[ao]{ln},aresample={edl['audio']['rate']},"
        f"afade=t=in:d=0.10,afade=t=out:st={d - afade_out:.3f}:d={afade_out}[aout]")

    out = work / f"piece_{idx:02d}.mp4"
    encode(out, ["ffmpeg", "-y", "-nostdin", *audio_source_args(source, s, e),
         "-f", "lavfi", "-i", f"color=c={NAVY}:s={w}x{h}:r={fps}:d={d:.4f}",
         "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]", "-t", f"{d:.6f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
         "-video_track_timescale", "16000",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(edl["audio"]["rate"]), "-ac", "1", out])
    return out, caps, d


def render_card(work, idx, item, edl):
    d = snap(item["dur"])
    fps, w, h = edl["video"]["fps"], edl["video"]["width"], edl["video"]["height"]

    def tf(tag, text):
        p = work / f"card_{idx:02d}_{tag}.txt"
        p.write_text(text)
        return p

    vf = []
    if item["kind"] == "title":
        vf += [drawtext(FONT, tf("k", item["kicker"]), 388, 26, "white@0.62"),
               drawtext(FONT_BOLD, tf("t", item["title"]), 452, 116),
               "drawbox=x=164:y=622:w=150:h=4:color=white@0.55:t=fill",
               drawtext(FONT, tf("s", item["sub"]), 664, 38, "white@0.85")]
    elif item["kind"] == "section":
        vf += [drawtext(FONT, tf("k", f"PART {item['num']}"), 438, 28, "white@0.6"),
               drawtext(FONT_BOLD, tf("t", item["title"]), 496, 58),
               "drawbox=x=164:y=600:w=110:h=3:color=white@0.5:t=fill"]
    else:  # end card
        lines = item["lines"]
        y = 540 - 30 * len(lines)
        for i, line in enumerate(lines):
            if line:
                bold = i in (1,)
                vf.append(drawtext(FONT_BOLD if bold else FONT, tf(f"l{i}", line),
                                   y + 62 * i, 40 if bold else 32,
                                   "white" if bold else "white@0.8"))
    fade_out = 0.45 if item["kind"] != "end" else 0.8
    vf += [f"fade=t=in:d=0.35", f"fade=t=out:st={d - fade_out:.2f}:d={fade_out}",
           "setsar=1", "format=yuv420p"]

    out = work / f"piece_{idx:02d}.mp4"
    encode(out, ["ffmpeg", "-y", "-nostdin",
         "-f", "lavfi", "-i", f"color=c={NAVY}:s={w}x{h}:r={fps}:d={d}",
         "-f", "lavfi", "-t", str(d), "-i",
         f"anullsrc=r={edl['audio']['rate']}:cl=mono",
         "-vf", ",".join(vf), "-shortest",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
         "-video_track_timescale", "16000",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(edl["audio"]["rate"]), "-ac", "1", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="original meeting MP4 (75:34)")
    ap.add_argument("--clips-dir", help="directory with the breakout clips (<id>.mp4)")
    ap.add_argument("--workdir", default="/tmp/meeting/build")
    ap.add_argument("--sidecars-only", action="store_true",
                    help="do not encode anything: reuse the pieces already in --workdir "
                         "and only re-emit the .vtt / chapters sidecars")
    args = ap.parse_args()
    global SIDECARS_ONLY
    SIDECARS_ONLY = args.sidecars_only

    edl = json.load(open(HERE / "edl.json"))
    work = Path(args.workdir)
    work.mkdir(parents=True, exist_ok=True)
    cues = load_cues(HERE.parent / "transcript.vtt", HERE.parent / "transcript.json",
                     edl["caption_text_fixes"])
    clip_cues = {key: load_simple_cues(HERE / "sources" / f"{key}.vtt",
                                       edl["caption_text_fixes"])
                 for key in (edl.get("sources") or {})}

    # pass 1: render every piece; remember captions/chapter anchors per piece index
    pieces, chapters_at, piece_caps = [], [], {}
    idx = 0
    for item in edl["items"]:
        if item["type"] == "card":
            title = item.get("title") or "End card"
            chapters_at.append((idx, title if item["kind"] != "end" else "Where to watch more"))
            pieces.append(render_card(work, idx, item, edl))
            idx += 1
        else:
            if item["id"] == "cold-open":
                chapters_at.append((idx, "Cold open: anyone can use AI (Carl)"))
            src_key = item.get("src")
            if src_key and not args.clips_dir:
                sys.exit(f"item {item['id']} needs --clips-dir (breakout clip {src_key})")
            item_source = (Path(args.clips_dir) / f"{src_key}.mp4") if src_key else args.source
            item_cues = clip_cues[src_key] if src_key else cues
            for j, piece in enumerate(item["pieces"]):
                piece = dict(piece, bug=item.get("bug") if j == 0 else None,
                             label=item.get("label") if j == 0 else None,
                             video_fade_in=item.get("video_fade_in") if j == 0 else None,
                             video_fade_out=item.get("video_fade_out") if j == len(item["pieces"]) - 1 else None)
                renderer = (render_audio_piece if item.get("visual") == "audio-card"
                            else render_piece)
                p, caps, d = renderer(item_source, work, idx, piece, item, edl, item_cues)
                pieces.append(p)
                piece_caps[idx] = caps
                idx += 1
                print(f"  piece {idx:02d} [{item.get('id')}] {d:.2f}s", flush=True)

    # actual video duration of each rendered piece (frame-exact at 16 fps)
    durs = []
    for p in pieces:
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v",
                             "-count_frames", "-show_entries", "stream=nb_read_frames",
                             "-of", "default=nw=1:nk=1", p], capture_output=True, text=True)
        durs.append(int(pr.stdout.strip()) / edl["video"]["fps"])

    # pass 2: join with the concat FILTER, padding/trimming each segment's audio to
    # exactly its video duration -- stream-copy concat of independently encoded MP4s
    # accumulates AAC-frame padding into audible A/V drift (~240 ms mid-video here).
    graph, labels = [], []
    for i, d in enumerate(durs):
        graph.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}];"
                     f"[{i}:a]aresample={edl['audio']['rate']},apad,atrim=end={d:.6f},"
                     f"asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    graph.append(f"{''.join(labels)}concat=n={len(durs)}:v=1:a=1[vout][aout]")
    graph_file = work / "concat_filter.txt"
    graph_file.write_text(";\n".join(graph))
    final = work / f"{edl['output_basename']}.mp4"
    cmd = ["ffmpeg", "-y", "-nostdin"]
    for p in pieces:
        cmd += ["-i", p]
    cmd += ["-filter_complex_script", graph_file, "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "160k", "-ar", str(edl["audio"]["rate"]), "-ac", "1",
            "-movflags", "+faststart", final]
    encode(final, cmd)

    # timeline offsets from actual durations
    offsets, t = [], 0.0
    for d in durs:
        offsets.append(t)
        t += d
    timeline = t
    out_caps = [{"s": offsets[i] + c["s"], "e": offsets[i] + c["e"], "text": c["text"],
                 "spk": c.get("spk")}
                for i, caps in sorted(piece_caps.items()) for c in caps]
    chapters = [(offsets[i], name) for i, name in chapters_at]

    # sidecar captions + chapters on the compilation timeline. The cues are a real
    # caption track, not a transcript dump: no cue may overlap the next (WebVTT leaves
    # that undefined and YouTube's ingest handles it inconsistently), lines wrap at
    # CAPTION_LINE characters over at most two lines, and the speaker is tagged, which
    # WCAG 1.2.2 requires and the burned-in render already knows.
    vtt = ["WEBVTT", ""]
    for i, c in enumerate(out_caps):
        end = c["e"] + CAPTION_HOLD           # buy reading time out of the silence that
        if i + 1 < len(out_caps):             # follows, never out of the next cue
            end = min(end, out_caps[i + 1]["s"] - CAPTION_GAP)
        end = max(min(end, c["e"] + CAPTION_HOLD), c["s"] + 0.05)
        if end <= c["s"] + 0.15:
            continue
        text = c["text"]
        if c.get("spk") and text.startswith(f"{c['spk']}: "):
            text = text[len(c["spk"]) + 2:]
        body = "\n".join(wrap_caption(text))
        if c.get("spk"):
            body = f"<v {c['spk']}>{body}"
        vtt += [f"{fmt_vtt(c['s'])} --> {fmt_vtt(end)}", body, ""]
    (work / f"{edl['output_basename']}.vtt").write_text("\n".join(vtt))
    ch_lines = [f"{int(t // 60):d}:{int(t % 60):02d} {name}" for t, name in chapters]
    (work / "highlights-chapters.txt").write_text("\n".join(ch_lines) + "\n")

    print(f"\nfinal: {final}  ({timeline:.2f}s planned)")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "default=nw=1:nk=1", final], capture_output=True, text=True)
    print(f"probed duration: {probe.stdout.strip()}s")
    print("\n".join(ch_lines))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render the AI-in-the-lab highlights compilation from the 2026-08-19 meeting recording.

Reads edl.json (clip boundaries on the original 75:34 timeline) plus the Teams
transcript (../transcript.vtt for caption text, ../transcript.json for speaker IDs),
then uses ffmpeg to cut each piece frame-accurately with burned captions, a source
timecode bug, and two-pass loudness normalization; generates title cards; concatenates
everything; and emits sidecar captions/chapters on the output timeline plus a 4x4
contact-sheet preview.

Usage:
    python3 make_highlights.py --source /path/to/original.mp4 --workdir /tmp/build

The source MP4 is not in git — re-fetch it with `yt-dlp -f source "<share link>"`
(see ../README.md).
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


def fmt_srt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def fmt_vtt(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}.{ms % 1000:03d}"


def piece_captions(cues, piece, edl, in_breakout):
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
        out.append({"s": cs - s, "e": ce - s, "text": text})
    if out and piece.get("cap_last_text"):
        out[-1]["text"] = piece["cap_last_text"]
    return out


def loudnorm_measure(source, s, e):
    proc = subprocess.run(
        ["ffmpeg", "-nostdin", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", source, "-vn",
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
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
    in_breakout = any(a <= s <= b for a, b in edl["breakout_ranges"])
    caps = piece_captions(cues, piece, edl, in_breakout)
    srt = work / f"cap_{idx:02d}.srt"
    srt.write_text("".join(f"{i + 1}\n{fmt_srt(c['s'])} --> {fmt_srt(c['e'])}\n{c['text']}\n\n"
                           for i, c in enumerate(caps)) or "1\n00:00:00,000 --> 00:00:00,100\n\n\n")

    vf = [f"fps={edl['video']['fps']}", f"subtitles=filename={srt}:force_style='{SUB_STYLE}'"]
    if piece.get("bug"):  # source timecode, top right, first seconds only
        bug = work / f"bug_{idx:02d}.txt"
        bug.write_text(piece["bug"])
        vf.append(f"drawtext=fontfile={FONT}:textfile={bug}:x=w-tw-44:y=40:fontsize=30:"
                  f"fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=10:enable='lte(t,3.2)'")
    if piece.get("video_fade_in"):
        vf.append(f"fade=t=in:d={piece['video_fade_in']}")
    if piece.get("video_fade_out"):
        fo = piece["video_fade_out"]
        vf.append(f"fade=t=out:st={d - fo:.3f}:d={fo}")
    vf.append("format=yuv420p")

    ln = "loudnorm=I=-16:TP=-1.5:LRA=11"
    meas = loudnorm_measure(source, s, e)
    if meas:
        ln += (f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
               f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
               f":offset={meas['target_offset']}:linear=true")
    afade_out = max(piece.get("video_fade_out") or 0.12, 0.12)
    af = (f"{ln},aresample={edl['audio']['rate']},"
          f"afade=t=in:d=0.10,afade=t=out:st={d - afade_out:.3f}:d={afade_out}")

    out = work / f"piece_{idx:02d}.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", source,
         "-vf", ",".join(vf), "-af", af,
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
         "-video_track_timescale", "16000",
         "-c:a", "aac", "-b:a", "96k", "-ar", str(edl["audio"]["rate"]), "-ac", "1", out])
    return out, caps, d


def drawtext(font, textfile, y, size, color="white", x="160"):
    return (f"drawtext=fontfile={font}:textfile={textfile}:x={x}:y={y}:"
            f"fontsize={size}:fontcolor={color}")


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
    vf += [f"fade=t=in:d=0.35", f"fade=t=out:st={d - fade_out:.2f}:d={fade_out}", "format=yuv420p"]

    out = work / f"piece_{idx:02d}.mp4"
    run(["ffmpeg", "-y", "-nostdin",
         "-f", "lavfi", "-i", f"color=c={NAVY}:s={w}x{h}:r={fps}:d={d}",
         "-f", "lavfi", "-t", str(d), "-i",
         f"anullsrc=r={edl['audio']['rate']}:cl=mono",
         "-vf", ",".join(vf), "-shortest",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
         "-video_track_timescale", "16000",
         "-c:a", "aac", "-b:a", "96k", "-ar", str(edl["audio"]["rate"]), "-ac", "1", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="original meeting MP4 (75:34)")
    ap.add_argument("--workdir", default="/tmp/meeting/build")
    args = ap.parse_args()

    edl = json.load(open(HERE / "edl.json"))
    work = Path(args.workdir)
    work.mkdir(parents=True, exist_ok=True)
    cues = load_cues(HERE.parent / "transcript.vtt", HERE.parent / "transcript.json",
                     edl["caption_text_fixes"])

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
            for j, piece in enumerate(item["pieces"]):
                piece = dict(piece, bug=item.get("bug") if j == 0 else None,
                             video_fade_in=item.get("video_fade_in") if j == 0 else None,
                             video_fade_out=item.get("video_fade_out") if j == len(item["pieces"]) - 1 else None)
                p, caps, d = render_piece(args.source, work, idx, piece, item, edl, cues)
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
            "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", final]
    run(cmd)

    # timeline offsets from actual durations
    offsets, t = [], 0.0
    for d in durs:
        offsets.append(t)
        t += d
    timeline = t
    out_caps = [{"s": offsets[i] + c["s"], "e": offsets[i] + c["e"], "text": c["text"]}
                for i, caps in sorted(piece_caps.items()) for c in caps]
    chapters = [(offsets[i], name) for i, name in chapters_at]

    # sidecar captions + chapters on the compilation timeline
    vtt = ["WEBVTT", ""]
    for c in out_caps:
        vtt += [f"{fmt_vtt(c['s'])} --> {fmt_vtt(c['e'])}", c["text"], ""]
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

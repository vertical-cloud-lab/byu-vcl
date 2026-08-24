#!/usr/bin/env python3
"""Render the AI-in-the-lab reels set: vertical 1080x1920 quote-driven cuts of the
2026-08-19 meeting and the breakout pair discussions, with filler words and dead air
removed by micro-cuts and the quote text revealed on screen word-by-word in sync with
the audio (the "Frieren next-episode preview" look: dark card, voices, text).

Reads reels-edl.json. Every item carries its final keep-intervals ("segments", seconds
on the source timeline, already word-aligned and filler-cut) and the kept words with
their source-time onsets ("words", [start, end, text]) used for the burned text reveal
and the sidecar captions. Nothing is inferred at render time — the EDL is the edit.

Usage:
    python3 make_reels.py --source /path/to/meeting.mp4 \
        --clips-dir /path/to/clips --workdir /tmp/reels-build [--only reel-id]

The meeting MP4 is re-fetched with `yt-dlp -f source "<share link>"` (../README.md);
the breakout clips live on the stream-cam Pi under ~/vcl-ai-clips/ (see
../highlights/README.md for the YouTube download recipe).
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
NAVY = "0x002E5D"  # BYU royal blue, as in ../highlights
W, H, FPS = 1080, 1920, 30
AR = 48000
LOUDNORM = "loudnorm=I=-14:TP=-1.2:LRA=11"  # reels/Shorts loudness (highlights uses -16)
STRIP_Y = 430          # y of a 1080x608 landscape strip inset
WAVE_Y, WAVE_H = 1520, 240
PHRASE_HOLD = 1.1      # seconds a finished phrase lingers before clearing


def run(cmd, **kw):
    proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        sys.exit(f"FAILED ({proc.returncode}): {' '.join(str(c) for c in cmd)}\n{proc.stderr[-3000:]}")
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


# ---------------------------------------------------------------- audio per item
def render_item_audio(src, segs, work, iid):
    """Sample-exact concat of the keep-intervals with 15 ms anti-click fades at every
    micro-cut junction, then two-pass loudnorm. One seeked input; atrim per segment."""
    base = max(0.0, min(s for s, _ in segs) - 2.0)
    raw = work / f"{iid}.raw.wav"
    graph = []
    for k, (s, e) in enumerate(segs):
        d = e - s
        graph.append(
            f"[0:a]atrim=start={s - base:.4f}:end={e - base:.4f},asetpts=PTS-STARTPTS,"
            f"aresample={AR},aformat=channel_layouts=mono,"
            f"afade=t=in:d=0.015,afade=t=out:st={max(0.0, d - 0.015):.4f}:d=0.015[a{k}]")
    graph.append("".join(f"[a{k}]" for k in range(len(segs))) +
                 f"concat=n={len(segs)}:v=0:a=1[a]")
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-ss", f"{base:.3f}",
         "-i", src, "-filter_complex", ";".join(graph), "-map", "[a]", raw])
    meas = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", raw, "-af", f"{LOUDNORM}:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True)
    import re as _re
    m = _re.search(r"\{[^{}]+\}\s*$", meas.stderr)
    ln = LOUDNORM
    if m:
        j = json.loads(m.group(0))
        ln += (f":measured_I={j['input_i']}:measured_TP={j['input_tp']}"
               f":measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}"
               f":offset={j['target_offset']}:linear=true")
    wav = work / f"{iid}.wav"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error", "-i", raw,
         "-af", f"{ln},aresample={AR},aformat=channel_layouts=mono", wav])
    return wav


# ---------------------------------------------------------------- video per item
def seg_filters(style):
    if style == "footage":  # 9:16 sources fill the frame exactly (no crop surprises)
        return (f"scale={W}:{H}:force_original_aspect_ratio=increase:force_divisible_by=2,"
                f"crop={W}:{H},fps={FPS}")
    if style == "strip":    # 16:9 source as a centered strip on navy
        return f"scale={W}:-2,fps={FPS}"
    raise ValueError(style)


def render_item_video(src, segs, work, iid, style, fade_in=0.0):
    cmd = ["ffmpeg", "-y", "-nostdin", "-loglevel", "error"]
    graph = []
    durs = []
    for k, (s, e) in enumerate(segs):
        d = snap(e) - snap(s)
        durs.append(d)
        cmd += ["-ss", f"{snap(s):.4f}", "-to", f"{snap(e) + 0.25:.4f}", "-i", src]
        graph.append(f"[{k}:v]{seg_filters(style)},setpts=PTS-STARTPTS,"
                     f"tpad=stop_mode=clone:stop_duration=0.3,trim=end={d:.6f}[v{k}]")
    total = sum(durs)
    graph.append("".join(f"[v{k}]" for k in range(len(segs))) +
                 f"concat=n={len(segs)}:v=1:a=0[vc]")
    post = []
    if style == "strip":
        cmd += ["-f", "lavfi", "-i", f"color=c={NAVY}:s={W}x{H}:r={FPS}:d={total:.4f}"]
        graph.append(f"[{len(segs)}:v][vc]overlay=(main_w-overlay_w)/2:{STRIP_Y}:"
                     f"eof_action=pass[vs]")
        cur = "[vs]"
    else:
        cur = "[vc]"
    if fade_in:
        post.append(f"fade=t=in:d={fade_in}")
    post += ["setsar=1", "format=yuv420p"]
    graph.append(f"{cur}{','.join(post)}[v]")
    out = work / f"{iid}.video.mp4"
    run(cmd + ["-filter_complex", ";".join(graph), "-map", "[v]", "-t", f"{total:.6f}",
               "-c:v", "libx264", "-preset", "fast", "-crf", "17", out])
    return out


def render_card_item_video(wav, dur, work, iid, fade_in=0.0):
    """Navy quote card: live waveform of the (already cut) audio; text comes from ASS."""
    post = [f"fade=t=in:d={fade_in}"] if fade_in else []
    post += ["setsar=1", "format=yuv420p"]
    graph = (f"[1:a]aformat=channel_layouts=mono,"
             f"showwaves=s={W}x{WAVE_H}:mode=cline:rate={FPS}:colors=0xFFFFFF@0.35[wv];"
             f"[0:v][wv]overlay=0:{WAVE_Y}:eof_action=pass,{','.join(post)}[v]")
    out = work / f"{iid}.video.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={NAVY}:s={W}x{H}:r={FPS}:d={dur:.4f}",
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


# ---------------------------------------------------------------- cards
def drawtext(font, textfile, y, size, color="white", x="90"):
    return (f"drawtext=fontfile={font}:textfile={textfile}:x={x}:y={y}:"
            f"fontsize={size}:fontcolor={color}:line_spacing=14")


def render_card(work, iid, card, kind):
    d = snap(card["dur"])

    def tf(tag, text):
        p = work / f"{iid}_{tag}.txt"
        p.write_text(text)
        return p

    vf = []
    if kind == "title":
        vf += [drawtext(FONT, tf("k", card["kicker"]), 620, 30, "white@0.62"),
               drawtext(FONT_BOLD, tf("t", card["title"]), 700, 112),
               f"drawbox=x=90:y={card.get('rule_y', 960)}:w=150:h=4:color=white@0.55:t=fill",
               drawtext(FONT, tf("s", card["sub"]), card.get("sub_y", 1000), 40, "white@0.85")]
    elif kind == "section":
        vf += [drawtext(FONT, tf("k", card.get("kicker", "")), 840, 30, "white@0.6"),
               drawtext(FONT_BOLD, tf("t", card["title"]), 900, 64),
               "drawbox=x=90:y=1020:w=110:h=3:color=white@0.5:t=fill"]
    else:  # end card
        lines = card["lines"]
        y = 860 - 28 * len(lines)
        for i, line in enumerate(lines):
            if line:
                bold = i in card.get("bold", (0,))
                vf.append(drawtext(FONT_BOLD if bold else FONT, tf(f"l{i}", line),
                                   y + 66 * i, 44 if bold else 34,
                                   "white" if bold else "white@0.8"))
    fade_out = 0.30 if kind != "end" else 0.8
    vf += ["fade=t=in:d=0.28", f"fade=t=out:st={d - fade_out:.2f}:d={fade_out}",
           "setsar=1", "format=yuv420p"]
    out = work / f"{iid}.mp4"
    run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error",
         "-f", "lavfi", "-i", f"color=c={NAVY}:s={W}x{H}:r={FPS}:d={d}",
         "-f", "lavfi", "-t", str(d), "-i", f"anullsrc=r={AR}:cl=mono",
         "-vf", ",".join(vf), "-shortest",
         "-c:v", "libx264", "-preset", "fast", "-crf", "17",
         "-c:a", "aac", "-b:a", "160k", "-ar", str(AR), "-ac", "1", out])
    return out, d


# ---------------------------------------------------------------- text reveal (ASS)
ASS_HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Header,DejaVu Sans,37,&H38FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,3,0,1,0,0,8,90,90,318,1
Style: Bug,DejaVu Sans,27,&H55FFFFFF,&H000000FF,&H88000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,9,90,44,44,1
Style: QuoteCard,DejaVu Sans,76,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,100,100,760,1
Style: QuoteStrip,DejaVu Sans,64,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,100,100,1150,1
Style: QuoteFoot,DejaVu Sans,58,&H00FFFFFF,&H000000FF,&H96000000,&H78000000,-1,0,0,0,100,100,0,0,1,3,1,1,96,96,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Text
"""


def ass_time(t):
    cs = max(0, round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def esc(text):
    return text.replace("{", "(").replace("}", ")").replace("\n", "\\N")


def chunk_phrases(words):
    """Split kept words into on-screen phrases: break at sentence enders, em-dashes,
    or ~44 chars at a natural gap. words: [[out_t0, out_t1, text], ...]."""
    phrases, cur, cur_len = [], [], 0
    for i, w in enumerate(words):
        cur.append(w)
        cur_len += len(w[2]) + 1
        gap = (words[i + 1][0] - w[1]) if i + 1 < len(words) else 99
        ender = w[2].rstrip('"”').endswith((".", "?", "!", "—", ":"))
        if ender or (cur_len >= 44 and gap >= 0.28) or cur_len >= 60:
            phrases.append(cur)
            cur, cur_len = [], 0
    if cur:
        phrases.append(cur)
    return phrases


def build_ass(layout, path):
    """layout: [{offset, dur, style, header, bug, words:[[t0,t1,text] item-local]}]"""
    ev = []
    for it in layout:
        off, dur = it["offset"], it["dur"]
        if it.get("header"):
            ev.append(("Header", off + 0.10, off + dur - 0.04, esc(it["header"])))
        if it.get("bug"):
            ev.append(("Bug", off, off + min(2.6, dur), esc(it["bug"])))
        style = {"card": "QuoteCard", "strip": "QuoteStrip",
                 "footage": "QuoteFoot"}[it["style"]]
        for pi, phrase in enumerate(chunk_phrases(it.get("words") or [])):
            nxt_start = None
            rest = list(it["words"])
            # find start of next phrase in output time
            last_end = phrase[-1][1]
            for w in rest:
                if w[0] > last_end + 1e-6:
                    nxt_start = w[0]
                    break
            phrase_close = min(dur, last_end + PHRASE_HOLD,
                               nxt_start if nxt_start is not None else 9e9)
            for i, w in enumerate(phrase):
                st = off + w[0]
                en = off + (phrase[i + 1][0] if i + 1 < len(phrase) else phrase_close)
                if en - st < 0.01:
                    en = st + 0.01
                text = esc(" ".join(x[2] for x in phrase[:i + 1]))
                ev.append((style, st, en, text))
    lines = [ASS_HEAD]
    for style, st, en, text in ev:
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},{style},,0,0,0,{text}")
    Path(path).write_text("\n".join(lines) + "\n")


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
    graph.append(f"[vc]ass={ass_path}[vout]")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="original meeting MP4 (75:34)")
    ap.add_argument("--clips-dir", required=True, help="breakout clips (<id>.mp4)")
    ap.add_argument("--workdir", default="/tmp/reels-build")
    ap.add_argument("--outdir", default=None, help="default: workdir")
    ap.add_argument("--only", default=None, help="render just this reel id")
    args = ap.parse_args()

    edl = json.load(open(HERE / "reels-edl.json"))
    outdir = Path(args.outdir or args.workdir)
    outdir.mkdir(parents=True, exist_ok=True)

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

        p, d = render_card(work, "card_title", reel["title_card"], "title")
        add(p, d)
        for n, item in enumerate(reel["items"]):
            iid = f"i{n:02d}_{item['id']}"
            if item.get("card"):  # section micro-card
                p, d = render_card(work, iid, item["card"], "section")
                chapters.append((cursor, item["card"]["title"]))
                add(p, d)
                continue
            src = (args.source if item["src"] == "meeting"
                   else str(Path(args.clips_dir) / f"{item['src']}.mp4"))
            segs = [(snap(s), snap(e)) for s, e in item["segments"]]
            wav = render_item_audio(src, segs, work, iid)
            words, planned = item_words_local(item)
            style = item.get("visual", "card")
            fade_in = 0.25 if n == 0 else 0.0
            if style == "card":
                video = render_card_item_video(wav, planned, work, iid, fade_in)
            else:
                video = render_item_video(src, segs, work, iid, style, fade_in)
            piece, dur = mux_item(video, wav, work, iid)
            if item.get("chapter"):
                chapters.append((cursor, item["chapter"]))
            add(piece, dur, {"style": style, "header": item.get("header"),
                             "bug": item.get("bug"), "words": words})
            print(f"  {reel['id']} {iid}: {dur:.2f}s ({len(words)} words)", flush=True)
        p, d = render_card(work, "card_end", reel["end_card"], "end")
        add(p, d)

        ass_path = work / f"{reel['id']}.ass"
        build_ass(layout, ass_path)
        final = outdir / f"{reel['output_basename']}.mp4"
        join_reel(pieces, ass_path, final)

        # sidecar captions (phrase-level) on the reel timeline
        vtt = ["WEBVTT", ""]
        for it in layout:
            for phrase in chunk_phrases(it.get("words") or []):
                s = it["offset"] + phrase[0][0]
                e = min(it["offset"] + it["dur"], it["offset"] + phrase[-1][1] + 0.3)
                vtt += [f"{fmt_vtt(s)} --> {fmt_vtt(e)}",
                        " ".join(w[2] for w in phrase), ""]
        (outdir / f"{reel['output_basename']}.vtt").write_text("\n".join(vtt))
        if chapters and reel.get("chapters_sidecar"):
            if chapters[0][0] > 0.01:
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

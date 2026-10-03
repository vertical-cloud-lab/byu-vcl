"""Build timestamps.md: every row of every per-video timestamp log in notes/*.md, with non-autoplay YouTube links.

Link convention: the mm:ss cell links to https://www.youtube.com/embed/<id>?start=<s>, which opens the player paused at
that second (embeds do not autoplay unless autoplay=1 is passed). The ▶ cell is the ordinary watch link
(https://www.youtube.com/watch?v=<id>&t=<s>s), which YouTube autoplays."""
import json, re, sys, os, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
videos = json.load(open(f"{ROOT}/videos.json"))
meta = {v["id"]: v for v in videos}
def secs(mmss):
    p = [int(x) for x in mmss.split(":")]
    return p[0]*60 + p[1] if len(p) == 2 else p[0]*3600 + p[1]*60 + p[2]
def iso_dur(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d); h, mi, s = (int(x) if x else 0 for x in m.groups())
    return f"{h}:{mi:02d}:{s:02d}" if h else f"{mi}:{s:02d}"
logs = {}  # id -> list of (mmss, phase, text)
for path in sorted(glob.glob(f"{ROOT}/notes/*.md")):
    vid = None; in_log = False
    for line in open(path, encoding="utf-8"):
        h = re.match(r"^## ([A-Za-z0-9_-]{11}) ", line)
        if h: vid = h.group(1); in_log = False; continue
        if line.startswith("### Timestamp log"): in_log = True; continue
        if line.startswith("### "): in_log = False; continue
        if in_log and vid and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", cells[0]):
                logs.setdefault(vid, []).append((cells[0], cells[1], cells[2]))
order = [l.strip() for l in open(f"{HERE}/video_ids.txt") if l.strip()]
out = ["# Atomizer videos: timestamp log", "",
       "Every substantive moment in the BYU VCL atomizer videos (install, AMAZEMET rePowder training Sep 29–30 2026, and the team's own runs), "
       "indexed from the transcripts in [`transcripts/`](transcripts/). Reading agents extracted the rows from the YouTube auto-captions and "
       "then re-checked them line by line against the Whisper transcripts; the six videos without captions were indexed from Whisper alone, "
       "and the ones with no speech from frames of the footage. The `mm:ss` is the caption start time (or the Whisper segment start), so a "
       "link lands at most a few seconds before the moment.", "",
       "**Links do not autoplay.** The `mm:ss` link opens YouTube's embed player paused at that second "
       "(`youtube.com/embed/<id>?start=<s>`; embeds only autoplay when `autoplay=1` is passed). The ▶ link is the normal watch page at the same "
       "time, which does autoplay. Unlisted videos open with either link; private ones need the channel login.", "",
       "Phases: *before* (utilities, stack, furnace prep, loading), *during* (pump-down/gas wash, heating, atomizing), *after* (shutdown, cooldown, "
       "venting, powder collection), *cleaning/maintenance*, *theory*, *troubleshooting*, *installation*, *chatter*.", "",
       "Transcript source per video is listed in the heading: **auto + whisper** = rows from YouTube auto-captions (caption start times), "
       "re-checked line by line against the faster-whisper large-v3-turbo transcript, with disagreements noted in the row; **whisper** = no "
       "YouTube captions, rows from Whisper alone; **keyframes** = no usable speech (Whisper returns only hallucinated filler), rows read from "
       "frames of the footage (see [`keyframes/`](keyframes/README.md)) and marked (keyframe); **auto** = auto-captions only, not yet re-checked.", ""]
total = 0
for vid in order:
    v = meta[vid]; rows = logs.get(vid, [])
    has_auto = os.path.exists(f"{ROOT}/transcripts/autosubs/{vid}.txt")
    has_whisper = os.path.exists(f"{ROOT}/transcripts/whisper/{vid}.txt")
    if rows and all(text.startswith("(keyframe)") for _, _, text in rows):
        src = "keyframes"
    else:
        src = "auto + whisper" if has_auto and has_whisper else "whisper" if has_whisper else "auto" if has_auto else "none"
    out.append(f"## {v['title']}")
    out.append(f"`{vid}` · {v['published'][:10]} · {iso_dur(v['duration'])} · {v['privacy']} · transcript: {src} · "
               f"[open paused](https://www.youtube.com/embed/{vid}?start=0) · [▶ watch](https://www.youtube.com/watch?v={vid})")
    out.append("")
    if not rows:
        out.append("_No rows yet: no transcript of this video has been indexed._"); out.append(""); continue
    out.append("| mm:ss | ▶ | phase | what happens / what is said |"); out.append("| --- | --- | --- | --- |")
    for mmss, phase, text in rows:
        s = secs(mmss); total += 1
        out.append(f"| [{mmss}](https://www.youtube.com/embed/{vid}?start={s}) | [▶](https://www.youtube.com/watch?v={vid}&t={s}s) | {phase} | {text} |")
    out.append("")
out.insert(2, f"_{total} timestamped rows across {sum(1 for v in order if logs.get(v))} of {len(order)} videos._\n")
open(f"{ROOT}/timestamps.md", "w", encoding="utf-8").write("\n".join(out))
print("rows:", total)

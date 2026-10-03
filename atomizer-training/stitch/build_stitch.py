#!/usr/bin/env python3
"""One video of every logged moment in the 26 atomizer videos, in the order of a run.

The raw material is the timestamp log (notes/*.md, the same rows as timestamps.md): one row per substantive moment. Each
row becomes a window of the source video that starts just before the row and ends at the next row, or after CAP seconds,
whichever is first; rows marked chatter end the previous window but are not shown. Every row is assigned to one chapter of
the procedure (ASSIGN: per video, from which second on which chapter applies; the chapters follow the SOP's outline, from
installation through power-up, stack, charge, furnace, chamber, gas wash, pour, after, cleaning). Consecutive rows of the
same chapter whose windows touch merge into one clip, so a continuous piece of work stays continuous, and the cut points are
snapped to sentence boundaries with the word-timed Whisper transcripts where they exist. Clips are then ordered by chapter,
then by recording order of the videos, then by time; a chapter card precedes each chapter.

Every clip carries its source and the running source time in the top bar, the chapter on the right, the log's own note
for that moment as a lower third (yellow, top), and Whisper subtitles (bottom). Nothing is stabilised, cross-faded or
narrated: this is the complete footage reorganised, the starting point the tutorials can be cut from.

    python build_stitch.py plan      # clip count and minutes per chapter
    python build_stitch.py jobs      # hls_sections.py job list for the windows that no fetched window covers yet
    python build_stitch.py edl       # edl.md (every clip, with links) and chapters.json
    python build_stitch.py build [VIDEO_ID ...]   # the clip segments (all, or only these videos'), then the stitch
    python build_stitch.py concat    # just the final join, from the cached segments
    python build_stitch.py upload    # unlisted, with the chapter list in the description

Set ATOMIZER_DL to the folder with <id>.m4a (and <id>.v360.mp4 as a fallback), ATOMIZER_HLS to the folder of fetched
720p windows (<name>.ts + <name>.json with t0/t1, from ../tools/hls_sections.py)."""
import glob, hashlib, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(ROOT)
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl"); HLS = os.environ.get("ATOMIZER_HLS", "/tmp/work/hls")
TX = f"{ROOT}/transcripts/whisper"
OUT = f"{HERE}/out"; TMP = os.environ.get("ATOMIZER_STITCH_TMP", "/tmp/work/stitch")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H, FPS = 1280, 720, 30
LEAD = 1.5            # s before a row's time that its window starts (caption times already run a second or two early)
CAP = 60.0            # s: longest window an action row gets when the next row is further away than this
CAP_CONV = 45.0       # s: the same for a row that is conversation (theory, parts, lessons, admin ...), see CONV
CAP_KEYFRAME = 30.0   # s: the same for rows read from frames of a video with no speech
CONV = {"theory", "parts", "part", "parameter", "lesson", "cost", "idea", "future", "admin", "context", "design", "material",
        "result", "status", "record", "unclear", "housekeeping", "tools", "safety", "maintenance", "panel", "plumbing", "check",
        "check / lesson", "procedure", "prep / lesson", "cleaning / lesson", "loading / lesson"}
MIN_CLIP = 6.0        # s: a lone row shorter than this is extended
MERGE_GAP = 0.75      # s: windows of the same chapter closer than this merge into one clip
NOTE_MAX = 40.0       # s: a note stays on screen until the next one, or this long
SLACK = 6.0           # s fetched either side of a clip, so the cut can move onto a sentence boundary
CLIP_VERSION = "1"
THREADS = os.environ.get("ATOMIZER_THREADS", "")
ENC = ["-c:v", "libx264", "-preset", "superfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", str(FPS * 2),
       "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2"]
AUDIO = "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100"
VIDEOS = {v["id"]: v for v in json.load(open(f"{ROOT}/videos.json"))}

# key, label in the top bar, card title, card note
CHAPTERS = [
    ("install", "Installation", "Installation and commissioning", "September 2026: the room, placing the machine, the vacuum test, the dehumidifier."),
    ("tour", "The machine", "The machine: a tour of the module", "Bartosz Kalicki walks through the inside of the unit: gas, air, water, filters, pump, generator, PLC."),
    ("hmi", "HMI and pressure logic", "The HMI: pages, scan, program and pressure logic", "Accounts and settings, the ultrasonic scan, the atomization program, gas wash, melting and pouring pressure, turbo."),
    ("theory", "Theory", "Materials, boosters and particle size", "What sets the particle size, which metals work, and what the first powders looked like."),
    ("safety", "Safety", "Safety and PPE", "Respirators, hearing protection, lab coats, the room oxygen sensor, venting before opening."),
    ("utilities", "Power-up and utilities", "Before a run: power-up and utilities", "Breakers, heat exchanger and facility water, compressed air, argon; the daily checks."),
    ("stack", "The ultrasonic stack", "Before a run: the ultrasonic stack", "Transducer, booster, sonotrodes, plate: torques, mounting in the housing, scan and wet test, plate position."),
    ("charge", "Charge preparation", "Charge preparation: cups, rods and dosing", "Turning the aluminium cups, dosing powder into them, the rods."),
    ("furnace", "Furnace and loading", "Before a run: furnace, nozzle, crucible and loading", "Thermocouple, sealing rod, insulation, nozzle and holder, crucible and graphite nut, loading, closing the lid."),
    ("chamber", "Chamber and container", "Before a run: chamber, plate guard, bowl and container", "Protective plate, the catch bowl, wiping the plate, mounting the container, closing the door."),
    ("gaswash", "Gas wash and heating", "During a run: gas wash and heating", "Furnace and chamber purges, 250 and 500 C, melting pressure, pressure control, oxygen, melting the charge."),
    ("pour", "The pour", "During a run: the pour", "Scan, vibration on, sealing rod up, pouring pressure, turbo, amplitude and plate position; the end-of-pour sequence."),
    ("after", "After a run", "After a run: shutdown, cooldown, venting, powder out", "Heating off, cooling to 400 C, venting, opening, brushing the powder down, closing and removing the container."),
    ("cleaning", "Cleaning", "Cleaning between runs", "Chamber, cone and view port, seals, crucible and sealing rod, the plate; the expert's own clean, start to finish."),
    ("consumables", "Tools and consumables", "Tools, consumables and spares", "Wrenches and torque wrench, the consumables tour, the dry box, brushes."),
    ("wrapup", "Lessons and planning", "Lessons, planning and support", "What to practise, what to log, what to order, how to reach AMAZEMET."),
]
CHAP = {c[0]: c for c in CHAPTERS}
ACCENT = {"install": "#1E3A8A", "tour": "#1E3A8A", "hmi": "#1E3A8A", "theory": "#1E3A8A", "safety": "#B91C1C",
          "utilities": "#00897B", "stack": "#00897B", "charge": "#00897B", "furnace": "#00897B", "chamber": "#00897B",
          "gaswash": "#C2410C", "pour": "#C2410C", "after": "#6D28D9", "cleaning": "#6D28D9", "consumables": "#374151",
          "wrapup": "#374151"}

# recording order (upload times are batch uploads; the order comes from what is said in the videos, see README)
VIDEO_ORDER = ["Kv9DT3Vo0GE", "07QOPRHIEvw", "cKwQbKdE22Q", "z6rwmQW_3Vg", "2wMgeI-E7zw", "wRc8p2_FnJo", "1F9_4ccwhss",
               "58wJ_Khwgyk", "tfb4fsVNIFI", "Pk0K5sBz-sQ", "naePD8o9_Gk", "txH397FGTAU", "w02MRlZhpNk", "prj_xgeuQtM",
               "u-KjR5TENN4", "LSQmxwmlTkQ", "f8KL31PN8bA", "TFpU4uqVF9c", "FDRTt68Vfvo", "HTlUrAr5HVU", "9kn-HhXCr1o",
               "BxA7Z9Fliss", "QXSj0j1OqL8", "dXRB7c6GeDw", "qYyT39D5Yzo", "of5-LhkX_VQ"]
SHORT = {"wRc8p2_FnJo": "Training video 1", "naePD8o9_Gk": "Training video 2", "txH397FGTAU": "Training video 3",
         "1F9_4ccwhss": "Training video 4", "58wJ_Khwgyk": "Training video 5", "tfb4fsVNIFI": "Training video 6",
         "FDRTt68Vfvo": "Training video 7", "HTlUrAr5HVU": "Training video 8", "9kn-HhXCr1o": "Training video 9",
         "Pk0K5sBz-sQ": "Training, Sep 29 (short clip)", "u-KjR5TENN4": "Expert cleaning, POV",
         "f8KL31PN8bA": "Cartridge cleaning", "2wMgeI-E7zw": "Training (Sterling's phone)",
         "TFpU4uqVF9c": "Atomizing AlSi10Mg-Al6063", "prj_xgeuQtM": "Dosing session, AlSi10Mg-Al6063",
         "QXSj0j1OqL8": "Dosing Al 4047", "qYyT39D5Yzo": "First run, Oct 2, part 1", "of5-LhkX_VQ": "First run, Oct 2, part 2",
         "BxA7Z9Fliss": "Claude ping for dosing", "dXRB7c6GeDw": "Dosing troubleshooting", "LSQmxwmlTkQ": "Drill press, graphite nozzle",
         "z6rwmQW_3Vg": "Turning Al crucibles", "07QOPRHIEvw": "Placing the atomizer", "Kv9DT3Vo0GE": "Construction update",
         "cKwQbKdE22Q": "Vacuum test", "w02MRlZhpNk": "Dehumidifier troubleshooting"}
DAY = {"Kv9DT3Vo0GE": "Sep 1", "07QOPRHIEvw": "Sep 3", "cKwQbKdE22Q": "Sep 8", "z6rwmQW_3Vg": "Sep 26", "2wMgeI-E7zw": "Sep 28",
       "wRc8p2_FnJo": "Sep 29", "1F9_4ccwhss": "Sep 29", "58wJ_Khwgyk": "Sep 29", "tfb4fsVNIFI": "Sep 29", "Pk0K5sBz-sQ": "Sep 29",
       "naePD8o9_Gk": "Sep 29", "txH397FGTAU": "Sep 29", "w02MRlZhpNk": "Sep 29", "prj_xgeuQtM": "Sep 29", "u-KjR5TENN4": "Sep 30",
       "LSQmxwmlTkQ": "Sep 30", "f8KL31PN8bA": "Sep 30", "TFpU4uqVF9c": "Sep 30", "FDRTt68Vfvo": "Sep 30", "HTlUrAr5HVU": "Sep 30",
       "9kn-HhXCr1o": "Sep 30", "BxA7Z9Fliss": "Sep 30", "QXSj0j1OqL8": "Sep 30", "dXRB7c6GeDw": "Sep 30", "qYyT39D5Yzo": "Oct 2",
       "of5-LhkX_VQ": "Oct 2"}
KEYFRAME_ONLY = {"u-KjR5TENN4", "QXSj0j1OqL8", "prj_xgeuQtM"}

# Which chapter a row belongs to: per video, (from this second on, chapter). Rows whose phase is chatter are never shown.
ASSIGN = {
    "Kv9DT3Vo0GE": [(0, "install")], "07QOPRHIEvw": [(0, "install")], "cKwQbKdE22Q": [(0, "install")],
    "w02MRlZhpNk": [(0, "install")], "z6rwmQW_3Vg": [(0, "charge")],
    "2wMgeI-E7zw": [(0, "utilities"), (207, "tour"), (269, "wrapup"), (362, "theory"), (417, "utilities"), (449, "stack"),
                    (634, "furnace"), (697, "cleaning"), (745, "consumables"), (782, "safety"), (828, "charge"), (893, "wrapup")],
    "wRc8p2_FnJo": [(0, "utilities"), (54, "tour"), (953, "utilities"), (1091, "hmi"), (2099, "furnace")],
    "1F9_4ccwhss": [(0, "furnace"), (341, "chamber"), (570, "safety"), (592, "chamber")],
    "58wJ_Khwgyk": [(0, "chamber"), (400, "stack"), (1852, "gaswash"), (3442, "pour"), (3862, "after"), (4040, "cleaning"),
                    (4106, "after"), (4131, "cleaning"), (4428, "safety"), (4576, "after"), (4668, "cleaning")],
    "tfb4fsVNIFI": [(0, "after")], "Pk0K5sBz-sQ": [(0, "after")],
    "naePD8o9_Gk": [(0, "gaswash"), (160, "charge"), (203, "gaswash"), (881, "pour"), (1489, "after"), (1815, "pour"), (1946, "after")],
    "txH397FGTAU": [(0, "cleaning"), (301, "consumables"), (554, "cleaning"), (559, "consumables"), (580, "cleaning"), (611, "stack"),
                    (873, "theory"), (972, "gaswash"), (1114, "theory"), (1218, "gaswash"), (2318, "pour"), (2765, "after")],
    "FDRTt68Vfvo": [(0, "cleaning"), (19, "stack"), (59, "cleaning"), (428, "wrapup"), (630, "consumables"), (860, "stack"),
                    (3102, "chamber"), (3115, "stack"), (3143, "cleaning")],
    "HTlUrAr5HVU": [(0, "furnace")],
    "9kn-HhXCr1o": [(0, "gaswash"), (1025, "pour"), (1710, "after"), (1953, "consumables"), (2627, "wrapup"), (2771, "after"),
                    (2793, "consumables"), (2827, "utilities"), (2880, "wrapup")],
    "u-KjR5TENN4": [(0, "cleaning")],
    "f8KL31PN8bA": [(0, "cleaning"), (779, "stack"), (927, "cleaning"), (957, "charge")],
    "TFpU4uqVF9c": [(0, "gaswash"), (1154, "pour")],
    "prj_xgeuQtM": [(0, "charge")], "QXSj0j1OqL8": [(0, "charge")], "BxA7Z9Fliss": [(0, "charge")], "dXRB7c6GeDw": [(0, "charge")],
    "LSQmxwmlTkQ": [(0, "furnace")],
    "qYyT39D5Yzo": [(0, "utilities"), (106, "stack"), (352, "consumables"), (381, "cleaning"), (444, "utilities"), (458, "stack"),
                    (476, "consumables"), (589, "chamber"), (608, "furnace"), (654, "utilities"), (882, "stack"), (1041, "chamber"),
                    (1049, "gaswash"), (1124, "furnace"), (1200, "stack")],
    "of5-LhkX_VQ": [(0, "utilities"), (85, "chamber"), (145, "gaswash"), (180, "furnace"), (243, "gaswash"), (1335, "charge"),
                    (1397, "pour"), (1417, "gaswash"), (1467, "pour"), (1679, "after")],
}


def run(cmd, check=True):
    if THREADS and cmd[0] == "ffmpeg":
        cmd = [cmd[0], "-threads", THREADS, "-filter_threads", THREADS] + cmd[1:]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd))[:800] + "\n" + r.stderr[-3000:])
    return r


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


def iso_dur(d):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d); h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def hms(t, ms=False):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    if ms:
        return f"{h}:{m:02d}:{s:05.2f}"
    return f"{h}:{m:02d}:{int(s):02d}" if h else f"{m}:{int(s):02d}"


# ----------------------------------------------------------------------------------------------------------- the log
def rows():
    """[{vid, t, phase, text}] from notes/*.md, in file order (make_timestamps.py reads the same tables)."""
    def secs(mmss):
        p = [int(x) for x in mmss.split(":")]
        return p[0] * 60 + p[1] if len(p) == 2 else p[0] * 3600 + p[1] * 60 + p[2]
    out = []
    for path in sorted(glob.glob(f"{ROOT}/notes/*.md")):
        vid = None; in_log = False
        for line in open(path, encoding="utf-8"):
            h = re.match(r"^## ([A-Za-z0-9_-]{11}) ", line)
            if h:
                vid = h.group(1); in_log = False; continue
            if line.startswith("### Timestamp log"):
                in_log = True; continue
            if line.startswith("### "):
                in_log = False; continue
            if in_log and vid and line.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 3 and re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", cells[0]):
                    out.append({"vid": vid, "t": secs(cells[0]), "phase": cells[1], "text": cells[2]})
    return out


def chapter_of(vid, t, phase):
    if phase.strip().lower() == "chatter":
        return None
    chap = None
    for t0, c in ASSIGN[vid]:
        if t >= t0:
            chap = c
    return chap


# ------------------------------------------------------------------------------------------------------- transcripts
_words = {}


def words_for(vid):
    """[(start, end, word)] from the word-timed Whisper JSON, or None if that video has none yet."""
    if vid not in _words:
        p = f"{TX}/{vid}.json"
        ws = None
        if os.path.exists(p):
            segs = json.load(open(p))["segments"]
            if segs and "words" in segs[0]:
                ws = [(w[0], w[1], w[2]) for s in segs for w in s.get("words", [])]
        if ws is None:
            return None                      # not cached: the transcript may still be on its way
        _words[vid] = ws
    return _words[vid]


def segments_for(vid):
    """[(start, end, text)] coarse segments, from the JSON or the SRT, for videos without word times."""
    p = f"{TX}/{vid}.json"
    if os.path.exists(p):
        return [(s["start"], s["end"], s["text"]) for s in json.load(open(p))["segments"]]
    p = f"{TX}/{vid}.srt"
    out = []
    if os.path.exists(p):
        blocks = open(p, encoding="utf-8").read().strip().split("\n\n")
        for b in blocks:
            ls = b.split("\n")
            if len(ls) >= 3 and "-->" in ls[1]:
                a, z = ls[1].split("-->")
                conv = lambda x: sum(float(v) * m for v, m in zip(x.strip().replace(",", ".").split(":"), (3600, 60, 1)))
                out.append((conv(a), conv(z), " ".join(ls[2:])))
    return out


def _ends(w):
    return w.strip().endswith((".", "?", "!"))


def snap(vid, start, end, last_note):
    """Move the cut onto sentence boundaries (or pauses > 0.7 s) near the requested times, when word times exist."""
    ws = words_for(vid)
    if not ws:
        return start, end
    starts = [ws[i][0] for i in range(len(ws)) if i == 0 or _ends(ws[i - 1][2]) or ws[i][0] - ws[i - 1][1] > 0.7]
    ends = [ws[i][1] for i in range(len(ws)) if _ends(ws[i][2]) or i == len(ws) - 1 or ws[i + 1][0] - ws[i][1] > 0.7]
    c = [s for s in starts if start - 3.0 <= s <= start + 2.5]
    if c:
        # prefer a boundary before the requested time, so the words the row describes are not lost
        start = min(c, key=lambda s: abs(s - start) + (0 if s <= start else 1.5)) - 0.3
    c = [e for e in ends if end - 4.0 <= e <= end + 3.0 and e >= last_note + 3.0]
    if c:
        end = min(c, key=lambda e: abs(e - end)) + 0.35
    # inside a sentence that runs past the cut: do not cut a word
    inside = [w for w in ws if w[0] < end < w[1]]
    if inside:
        end = inside[0][1] + 0.2
    return max(0.0, start), end


# ------------------------------------------------------------------------------------------------------------- plan
def plan():
    """The clips, ordered: [{vid, start, end, chapter, notes: [(t, text)], key}]."""
    by_vid = {}
    for r in rows():
        by_vid.setdefault(r["vid"], []).append(r)
    clips = []
    for vid, rs in by_vid.items():
        rs = sorted(rs, key=lambda r: r["t"])          # stable: same-time rows keep file order
        vdur = iso_dur(VIDEOS[vid]["duration"])
        times = sorted({r["t"] for r in rs})
        cur = None
        for r in rs:
            chap = chapter_of(vid, r["t"], r["phase"])
            cap = CAP_KEYFRAME if vid in KEYFRAME_ONLY else CAP_CONV if r["phase"].strip().lower() in CONV else CAP
            nxt = [t for t in times if t > r["t"]]
            w0 = max(0.0, r["t"] - LEAD)
            w1 = min(nxt[0] if nxt else vdur, r["t"] + cap, vdur)
            if chap is None:
                cur = None
                continue
            if cur and cur["chapter"] == chap and w0 <= cur["end"] + MERGE_GAP:
                cur["end"] = max(cur["end"], w1)
                if cur["notes"] and cur["notes"][-1][0] == r["t"]:
                    cur["notes"][-1] = (r["t"], cur["notes"][-1][1] + "  ·  " + r["text"])
                else:
                    cur["notes"].append((r["t"], r["text"]))
            else:
                cur = {"vid": vid, "start": w0, "end": w1, "chapter": chap, "notes": [(r["t"], r["text"])]}
                clips.append(cur)
    for c in clips:
        vdur = iso_dur(VIDEOS[c["vid"]]["duration"])
        if c["vid"] not in KEYFRAME_ONLY:
            c["start"], c["end"] = snap(c["vid"], c["start"], c["end"], c["notes"][-1][0])
        if c["end"] - c["start"] < MIN_CLIP:
            c["end"] = c["start"] + MIN_CLIP
        c["end"] = min(c["end"], vdur)
        c["start"] = round(c["start"], 2); c["end"] = round(c["end"], 2)
        c["key"] = f"{c['vid']}_{int(c['start'])}"
    order = {k: i for i, k in enumerate(VIDEO_ORDER)}; corder = {c[0]: i for i, c in enumerate(CHAPTERS)}
    clips.sort(key=lambda c: (corder[c["chapter"]], order[c["vid"]], c["start"]))
    return clips


def covering_window(vid, start, end):
    """(path, t0, height) of a fetched window that covers [start, end], tallest first; None if none does."""
    best = None
    for p in glob.glob(f"{HLS}/{glob.escape(vid)}_*.json"):
        m = json.load(open(p))
        ts = os.path.join(HLS, m.get("file", os.path.basename(p)[:-5] + ".ts"))
        if m.get("video_id") == vid and m["t0"] <= start + 0.05 and end <= m["t1"] + 1.5 and os.path.exists(ts):
            if best is None or m.get("height", 0) > best[2]:
                best = (ts, float(m["t0"]), m.get("height", 0))
    return best


def cmd_plan(clips):
    tot = 0
    print(f"{len(clips)} clips")
    for key, label, title, _ in CHAPTERS:
        cs = [c for c in clips if c["chapter"] == key]
        d = sum(c["end"] - c["start"] for c in cs); tot += d
        vids = sorted({c["vid"] for c in cs}, key=VIDEO_ORDER.index)
        print(f"  {key:12s} {len(cs):4d} clips {d / 60:6.1f} min   {', '.join(SHORT[v] for v in vids)}")
    print(f"total {tot / 60:.1f} min; {sum(1 for c in clips if covering_window(c['vid'], c['start'], c['end']))} clips covered by fetched windows")


def cmd_jobs(clips, chapters=None):
    jobs = []
    for c in clips:
        if chapters and c["chapter"] not in chapters:
            continue
        if covering_window(c["vid"], c["start"], c["end"]):
            continue
        vdur = iso_dur(VIDEOS[c["vid"]]["duration"])
        jobs.append({"video_id": c["vid"], "start": max(0.0, c["start"] - SLACK), "end": min(vdur, c["end"] + SLACK),
                     "name": f"{c['vid']}_s{int(c['start'])}"})
    json.dump(jobs, sys.stdout, indent=0)
    print(f"\n{len(jobs)} windows, {sum(j['end'] - j['start'] for j in jobs) / 60:.1f} min of video", file=sys.stderr)


# -------------------------------------------------------------------------------------------------------------- edl
def emb(vid, t):
    return f"https://www.youtube.com/embed/{vid}?start={int(t)}"


def cmd_edl(clips, timeline=None):
    """edl.md: every clip, in stitch order, with links; chapters.json for the description."""
    lines = ["# Start-to-finish stitch: edit decision list", "",
             "Every clip of [the stitch](README.md), in the order it plays. `source` links open the source video paused at the "
             "clip's start; `in stitch` is where the clip starts in the stitched video (when it has been built). The notes are the "
             "timestamp log's own rows for the moments inside the clip ([`../timestamps.md`](../timestamps.md)).", ""]
    pos = 0.0; n = 0
    for key, label, title, note in CHAPTERS:
        cs = [c for c in clips if c["chapter"] == key]
        if not cs:
            continue
        d = sum(c["end"] - c["start"] for c in cs)
        part = next((q for q in PARTS if key in q[2]), None)
        tl = timeline.get(part[0]) if (timeline and part) else None
        at = tl["chapters"].get(key) if tl else None
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"_{len(cs)} clips, {d / 60:.1f} min" + (f", at {hms(at)} in {part[1].split(':')[0].lower()}" if at is not None else "") + f"._ {note}")
        lines.append("")
        lines.append("| # | source | in stitch | length | notes |")
        lines.append("| --- | --- | --- | --- | --- |")
        for c in cs:
            n += 1
            src = f"[{SHORT[c['vid']]} ({DAY[c['vid']]}) {hms(c['start'])}–{hms(c['end'])}]({emb(c['vid'], c['start'])})"
            at = tl["clips"].get(c["key"]) if tl else None
            notes = "<br>".join(f"[{hms(t)}]({emb(c['vid'], t)}) {txt}" for t, txt in c["notes"])
            lines.append(f"| {n} | {src} | {hms(at) if at is not None else ''} | {c['end'] - c['start']:.0f} s | {notes} |")
        lines.append("")
    open(f"{HERE}/edl.md", "w", encoding="utf-8").write("\n".join(lines))
    print("edl.md:", n, "clips")


# ------------------------------------------------------------------------------------------------------------ build
def ass_escape(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)              # markdown links -> text
    s = s.replace("`", "").replace("**", "").replace("{", "(").replace("}", ")").replace("\\", "/")
    return re.sub(r"\s+", " ", s).strip()


def cues_from_words(ws, start, end, max_words=9, max_len=3.4):
    """Subtitle cues (s, e, text), clip-relative, from word times inside [start, end]."""
    sel = [w for w in ws if w[1] > start + 0.05 and w[0] < end - 0.05]
    cues, cur = [], []
    for i, w in enumerate(sel):
        cur.append(w)
        nxt = sel[i + 1] if i + 1 < len(sel) else None
        brk = (nxt is None or _ends(w[2]) or (w[2].strip().endswith(",") and len(cur) >= 4) or len(cur) >= max_words
               or (nxt and nxt[0] - w[1] > 0.6) or cur[-1][1] - cur[0][0] > max_len)
        if brk:
            cues.append((max(0.0, cur[0][0] - start), min(end - start, cur[-1][1] - start + 0.2), "".join(x[2] for x in cur).strip()))
            cur = []
    return cues


def cues_from_segments(segs, start, end):
    out = []
    for s0, s1, text in segs:
        if s1 > start and s0 < end:
            out.append((max(0.0, s0 - start), min(end - start, s1 - start), text.strip()))
    return out


def write_ass(path, clip, cues):
    def ts(t):
        t = max(0.0, t); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    d = clip["end"] - clip["start"]
    ev = []
    for k, (t, text) in enumerate(clip["notes"]):
        a = max(0.0, t - clip["start"])
        b = clip["notes"][k + 1][0] - clip["start"] if k + 1 < len(clip["notes"]) else d
        b = min(b, a + NOTE_MAX, d)
        if b - a > 0.3:
            ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Note,,0,0,0,,{ass_escape(text)}")
    for a, b, text in cues:
        if b - a > 0.15 and text:
            ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Speech,,0,0,0,,{ass_escape(text)}")
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
           "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
           "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding\n"
           "Style: Speech,DejaVu Sans,29,&H00FFFFFF,&H000000FF,&H00000000,&H70000000,0,0,0,0,100,100,0,0,3,0,0,2,60,60,26,1\n"
           "Style: Note,DejaVu Sans,23,&H0080E6FF,&H000000FF,&H00000000,&H58000000,0,0,0,0,100,100,0,0,3,0,0,7,22,22,58,1\n\n"
           "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    open(path, "w", encoding="utf-8").write(hdr + "\n".join(ev) + "\n")


def esc_dt(x):
    """Text for drawtext inside single quotes: colons and commas escaped, no quotes or percent signs."""
    return x.replace("\\", "").replace("%", "").replace(":", "\\:").replace("'", "’").replace(",", "\\,")


def seg_key(clip):
    src = covering_window(clip["vid"], clip["start"], clip["end"])
    deps = [CLIP_VERSION, clip["vid"], f"{clip['start']}-{clip['end']}", clip["chapter"], json.dumps(clip["notes"], ensure_ascii=False),
            "words" if words_for(clip["vid"]) else "segments", f"{src[0]}@{os.path.getmtime(src[0])}" if src else "360p"]
    return "clip_" + hashlib.sha1("|".join(deps).encode()).hexdigest()[:12]


def build_clip(clip):
    out = f"{TMP}/{seg_key(clip)}.mp4"
    if os.path.exists(out):
        try:
            duration(out); return out
        except (RuntimeError, ValueError):
            os.remove(out)
    vid, s, e = clip["vid"], clip["start"], clip["end"]; d = e - s
    a = f"{DL}/{vid}.m4a"
    if not os.path.exists(a):
        raise FileNotFoundError(a)
    ws = words_for(vid)
    cues = cues_from_words(ws, s, e) if ws else cues_from_segments(segments_for(vid), s, e)
    ass = f"{TMP}/{seg_key(clip)}.ass"; write_ass(ass, clip, cues)
    src = covering_window(vid, s, e)
    while not src and not os.path.exists(f"{HLS}/.fetch_done"):      # the Pi is still fetching: wait for this window
        time.sleep(20); src = covering_window(vid, s, e)
    if src:
        x = max(0.0, round((s - src[1]) * FPS) / FPS - 0.5 / FPS)
        vin, vtrim = ["-i", src[0]], f"trim=start={x:.4f},setpts=PTS-STARTPTS,"
        low = False
    else:
        v = f"{DL}/{vid}.v360.mp4"
        if not os.path.exists(v):
            raise FileNotFoundError(f"{vid}: no window in {HLS} covers {s:.1f}-{e:.1f}, and no {v}")
        print(f"  ! {vid} {s:.1f}-{e:.1f}: no 720p window, using the 360p copy", flush=True)
        vin, vtrim = ["-ss", f"{s:.3f}", "-i", v], ""
        low = True
    # the picture: fit 1280x720; portrait phone video over a blurred copy of itself instead of black bars
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", vin[-1]])
    w0, h0 = (int(x) for x in r.stdout.strip().splitlines()[0].split(",")[:2])   # MPEG-TS lists the stream twice
    if h0 > w0:
        fit = (f"split[fg][bgsrc];[fg]scale=-2:{H}[fgs];"      # the blur is done small, then scaled up: cheap
               f"[bgsrc]scale=320:180:force_original_aspect_ratio=increase,crop=320:180,boxblur=5:1,scale={W}:{H},"
               f"eq=brightness=-0.15[bg];[bg][fgs]overlay=(W-w)/2:0")
    else:
        fit = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black"
    label = f"{SHORT[vid]}  ·  {DAY[vid]}  ·  "
    chap = CHAP[clip["chapter"]][1]
    bar = (f"drawbox=x=0:y=0:w=iw:h=46:color=black@0.5:t=fill,"
           f"drawtext=fontfile={FONT}:text='{esc_dt(label)}%{{pts\\:gmtime\\:{int(s)}\\:%H\\\\\\:%M\\\\\\:%S}}':x=20:y=13:fontsize=21:fontcolor=white,"
           f"drawtext=fontfile={FONTB}:text='{esc_dt(chap)}':x=w-tw-20:y=13:fontsize=21:fontcolor=0x9fd3ff")
    if low:
        bar += f",drawtext=fontfile={FONT}:text='360p copy':x=w-tw-20:y=h-30:fontsize=16:fontcolor=white@0.7"
    vf = f"[0:v]{vtrim}fps={FPS},{fit},{bar},ass={ass},format=yuv420p[v]"
    run(["ffmpeg", "-y", "-v", "error", *vin, "-ss", f"{s:.3f}", "-t", f"{d:.3f}", "-i", a,
         "-filter_complex", vf, "-map", "[v]", "-map", "1:a:0", "-t", f"{d:.3f}", "-shortest", "-af", AUDIO, *ENC,
         "-movflags", "+faststart", out])
    return out


def card_png(path, kicker, title, sub, accent, footer=""):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    f = lambda size, bold=False: ImageFont.truetype(FONTB if bold else FONT, size)

    def wrap(text, fnt, width):
        lines, cur = [], ""
        for w in text.split():
            t = f"{cur} {w}".strip()
            if cur and d.textlength(t, font=fnt) > width:
                lines.append(cur); cur = w
            else:
                cur = t
        return lines + ([cur] if cur else [])
    d.rectangle([0, 0, 18, H], fill=accent)
    d.rectangle([0, H - 14, W, H], fill=accent)
    d.text((80, 130), kicker.upper(), font=f(22, True), fill=accent)
    y = 176
    for line in wrap(title, f(54, True), 1100):
        d.text((80, y), line, font=f(54, True), fill="#1F2937"); y += 66
    y += 18
    for line in wrap(sub, f(27), 1100):
        d.text((80, y), line, font=f(27), fill="#4B5563"); y += 38
    if footer:
        y = H - 60
        for line in reversed(wrap(footer, f(21), 1100)):
            y -= 30
            d.text((80, y), line, font=f(21), fill="#6B7280")
    im.save(path)


def card_seg(name, kicker, title, sub, accent, footer="", dur=5.0):
    key = "card_" + hashlib.sha1(f"{CLIP_VERSION}|{kicker}|{title}|{sub}|{accent}|{footer}|{dur}".encode()).hexdigest()[:12]
    out = f"{TMP}/{key}.mp4"
    if os.path.exists(out):
        return out
    png = f"{TMP}/{key}.png"; card_png(png, kicker, title, sub, accent, footer)
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", png, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", f"{dur:.2f}", "-vf", f"scale={W}:{H},format=yuv420p,fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.4:.2f}:d=0.4",
         "-shortest", *ENC, "-movflags", "+faststart", out])
    return out


PARTS = [("part1", "Part 1: the machine, and before a run",
          ["install", "tour", "hmi", "theory", "safety", "utilities", "stack", "charge", "furnace", "chamber"]),
         ("part2", "Part 2: during and after a run", ["gaswash", "pour", "after", "cleaning", "consumables", "wrapup"])]


def timeline_of(clips, part=None):
    """[(kind, item, make)] for one part of the stitch, in order: title card, then per chapter a card and its clips.
    With part=None, everything in one timeline (no part title cards)."""
    tl = []
    keys = part[2] if part else [c[0] for c in CHAPTERS]
    cs_all = [c for c in clips if c["chapter"] in keys]
    tot = sum(c["end"] - c["start"] for c in cs_all)
    if part:
        tl.append(("title", None, lambda part=part, tot=tot, n=len(cs_all): card_seg(
            part[0], "BYU Vertical Cloud Lab · AMAZEMET rePowder", f"The atomizer, start to finish: every recorded step. {part[1]}",
            f"A raw cut of the {len(VIDEOS)} atomizer videos (Sep 1 – Oct 2 2026), reorganised into the order of a run: this part has "
            f"{n} clips, {tot / 3600:.1f} hours. Top bar: source video, day, running source time; right: the chapter. "
            "Yellow text: the timestamp log's note for the moment. Bottom: Whisper subtitles. Nothing is narrated or stabilised.",
            "#1E3A8A", "Chapters are in the video description. The clip list, with a link to every source moment: "
            "github.com/vertical-cloud-lab/byu-vcl, atomizer-training/stitch/edl.md", dur=9.0)))
    for n, (key, label, title, note) in enumerate(CHAPTERS, 1):
        if key not in keys:
            continue
        cs = [c for c in clips if c["chapter"] == key]
        if not cs:
            continue
        d = sum(c["end"] - c["start"] for c in cs)
        vids = sorted({c["vid"] for c in cs}, key=VIDEO_ORDER.index)
        srcs = ", ".join(f"{SHORT[v]} ({DAY[v]})" for v in vids)
        tl.append(("card", key, lambda key=key, n=n, title=title, note=note, d=d, srcs=srcs, cs=cs: card_seg(
            key, f"Chapter {n} of {len(CHAPTERS)}", title, note, ACCENT[key],
            f"{len(cs)} clips, {d / 60:.0f} min, from: {srcs}", dur=5.0)))
        for c in cs:
            tl.append(("clip", c, lambda c=c: build_clip(c)))
    return tl


def cmd_build(clips, only=None):
    """Encode the clip segments: whichever pending clip has its window (and, for videos named in ATOMIZER_WAIT_WORDS, its
    word-timed transcript) first, in timeline order; waits while the fetch is still running, and falls back to the 360p
    copies for whatever never arrived once {HLS}/.fetch_done exists."""
    os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    wait_words = {v for v in os.environ.get("ATOMIZER_WAIT_WORDS", "").split(",") if v}
    t0 = time.time(); n = 0
    pending = [c for c in clips if not only or c["vid"] in only]
    worker, nworkers = (int(x) for x in os.environ.get("ATOMIZER_WORKER", "0/1").split("/"))   # "k/n": every n-th clip
    pending = [c for i, c in enumerate(pending) if i % nworkers == worker]
    for kind, item, make in timeline_of(clips):
        if kind == "card" and not only and worker == 0:
            make()
    while pending:
        fetched = os.path.exists(f"{HLS}/.fetch_done")
        ready = [c for c in pending if (fetched or covering_window(c["vid"], c["start"], c["end"]))
                 and (c["vid"] not in wait_words or words_for(c["vid"]))]
        if not ready:
            time.sleep(15); continue
        c = ready[0]; pending.remove(c)
        p = build_clip(c); n += 1
        print(f"{time.strftime('%H:%M:%S')} {c['chapter']:11s} {c['vid']} {hms(c['start'])}-{hms(c['end'])} "
              f"{duration(p):6.1f}s  {os.path.basename(p)}  ({len(pending)} left)", flush=True)
    print(f"{n} clips in {(time.time() - t0) / 60:.1f} min", flush=True)


def load_timeline():
    p = f"{HERE}/chapters.json"
    return json.load(open(p)) if os.path.exists(p) else {}


def cmd_concat(clips, parts=None):
    """Join each part from the cached segments (no re-encode); record where every chapter and clip starts."""
    os.makedirs(OUT, exist_ok=True)
    timeline = load_timeline()
    for part in PARTS:
        if parts and part[0] not in parts:
            continue
        paths, tl, pos = [], {"chapters": {}, "clips": {}}, 0.0
        for kind, item, make in timeline_of(clips, part):
            p = make(); d = duration(p)
            if kind == "card":
                tl["chapters"][item] = round(pos, 2)
            elif kind == "clip":
                tl["clips"][item["key"]] = round(pos, 2)
            paths.append(p); pos += d
        lst = f"{TMP}/concat_{part[0]}.txt"
        open(lst, "w").write("".join(f"file '{p}'\n" for p in paths))
        out = f"{OUT}/atomizer_start_to_finish_{part[0]}.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out])
        tl["total"] = round(pos, 2); tl["file"] = os.path.basename(out); tl["title"] = part[1]
        timeline[part[0]] = tl
        json.dump(timeline, open(f"{HERE}/chapters.json", "w"), indent=1)
        print(out, f"{duration(out) / 3600:.2f} h, {os.path.getsize(out) / 1e9:.2f} GB", flush=True)
    cmd_edl(clips, timeline)


def description(clips, timeline, part):
    tl = timeline[part[0]]
    other = [q for q in PARTS if q[0] != part[0]][0]
    log = json.load(open(f"{HERE}/uploads.json")) if os.path.exists(f"{HERE}/uploads.json") else {}
    lines = [f"{part[1]}. Raw cut, draft 1, for review. Every logged moment of the 26 atomizer videos on this channel (installation, "
             "the AMAZEMET rePowder training with Bartosz Kalicki on Sep 29–30 2026, the dosing sessions and the team's first run on "
             "Oct 2), reorganised into the order of a run and joined end to end: nothing narrated, stabilised or faded. The top bar "
             "names the source video, its day and the running source time; the yellow text is the timestamp log's note for the "
             "moment; subtitles are Whisper. Pauses with nothing logged are skipped, which is why the clips cut.", "", "Chapters:"]
    for n, (key, label, title, note) in enumerate(CHAPTERS, 1):
        if key in tl["chapters"]:
            lines.append(f"{hms(tl['chapters'][key])} {n}. {title}")
    lines.append("")
    if other[0] in log.get("draft 1", {}):
        lines.append(f"{other[1]}: {log['draft 1'][other[0]]['url']}")
    lines += ["The clip list, with a link to every source moment, and the procedure written out: "
              "https://github.com/vertical-cloud-lab/byu-vcl/pull/255 (atomizer-training/stitch/edl.md). Issue #124."]
    return "\n".join(lines)


def cmd_upload(clips, parts=None):
    sys.path.insert(0, REPO)
    from youtube.yt_service import upload_video
    timeline = load_timeline()
    log_p = f"{HERE}/uploads.json"
    log = json.load(open(log_p)) if os.path.exists(log_p) else {}
    done = log.setdefault("draft 1", {})
    for part in PARTS:
        if parts and part[0] not in parts:
            continue
        if part[0] in done:
            print(part[0], "already uploaded:", done[part[0]]["url"]); continue
        path = f"{OUT}/atomizer_start_to_finish_{part[0]}.mp4"
        if part[0] not in timeline or not os.path.exists(path):
            print(part[0], "not built yet"); continue
        title = f"rePowder atomizer, every recorded step: {part[1].replace(': ', ', ')} (raw cut, draft 1)"   # YouTube: 100 chars max
        assert len(title) <= 100, title
        vid = upload_video(path, title, description(clips, timeline, part), privacy="unlisted",
                           tags=["atomizer", "rePowder", "AMAZEMET", "BYU VCL", "training"])
        done[part[0]] = {"video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "title": title,
                         "uploaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "privacy": "unlisted",
                         "size_bytes": os.path.getsize(path), "duration_s": timeline[part[0]]["total"],
                         "clips": len(timeline[part[0]]["clips"])}
        json.dump(log, open(log_p, "w"), indent=1)
        print(part[0], "->", done[part[0]]["url"], flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    clips = plan()
    if cmd == "plan":
        cmd_plan(clips)
    elif cmd == "jobs":
        cmd_jobs(clips, set(sys.argv[2:]) or None)
    elif cmd == "edl":
        cmd_edl(clips, load_timeline() or None)
    elif cmd == "build":
        cmd_build(clips, set(sys.argv[2:]) or None)
    elif cmd == "concat":
        cmd_concat(clips, set(sys.argv[2:]) or None)
    elif cmd == "upload":
        cmd_upload(clips, set(sys.argv[2:]) or None)
    else:
        raise SystemExit(__doc__)

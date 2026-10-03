"""Word-timed Whisper for the windows the tutorials cut from the training videos.

The clip times in scripts.py come from caption start times (±2 s), which is how the first drafts began clips mid-sentence.
For every clip this transcribes a window around it with word timestamps, and `snap()` moves the cut to the nearest sentence
start before it and the nearest sentence end after it. The same words become the burned-in subtitles. Results are cached in
clip_words/<id>_<start>.json (committed), so a rebuild only needs Whisper for clips that are new or moved.

    python clip_words.py            # every clip in scripts.py without a cache file
"""
import json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl")
CACHE = f"{HERE}/clip_words"
PAD = 12.0          # seconds of audio transcribed either side of the requested window
_model = None


def cache_path(vid, start):
    return f"{CACHE}/{vid}_{int(start)}.json"


def transcribe_window(vid, start, dur):
    global _model
    from faster_whisper import WhisperModel
    if _model is None:
        _model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=4)
    w0 = max(0.0, start - PAD); wd = dur + 2 * PAD
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{w0:.2f}", "-t", f"{wd:.2f}", "-i", f"{DL}/{vid}.m4a",
                          "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.float32)
    segs, _ = _model.transcribe(audio, language="en", word_timestamps=True, vad_filter=False,
                                condition_on_previous_text=False, beam_size=5)
    words = [{"w": x.word, "s": round(w0 + x.start, 2), "e": round(w0 + x.end, 2)} for s in segs for x in (s.words or [])]
    return {"video_id": vid, "start": start, "dur": dur, "window": [round(w0, 2), round(w0 + wd, 2)],
            "model": "faster-whisper large-v3-turbo int8, word timestamps", "words": words}


def words_for(vid, start, dur):
    """Cached words of any window that covers [start - 2, start + dur + 2], else a fresh transcription."""
    import glob
    for p in sorted(glob.glob(f"{CACHE}/{vid}_*.json")):
        d = json.load(open(p))
        if d["window"][0] <= max(0.0, start - 2) and d["window"][1] >= start + dur + 2:
            return d["words"]
    p = cache_path(vid, start)
    os.makedirs(CACHE, exist_ok=True)
    d = transcribe_window(vid, start, dur)
    json.dump(d, open(p, "w"), indent=0)
    return d["words"]


def _ends(w):
    return w["w"].strip().endswith((".", "?", "!"))


def snap(vid, start, dur, early=4.0, late=3.0, end_early=5.0, end_late=4.0):
    """(start, end, words) with the cut moved to sentence (or long-pause) boundaries near the requested window."""
    words = words_for(vid, start, dur)
    if not words:
        return start, start + dur, []
    # a time given to within 0.3 s of a word boundary is taken as exact (scripts.py sets most clips from the word list)
    exact0 = [i for i, w in enumerate(words) if abs(w["s"] - start) <= 0.3]
    starts = [i for i, w in enumerate(words) if i == 0 or _ends(words[i - 1]) or w["s"] - words[i - 1]["e"] > 0.7]
    cands = [i for i in starts if start - early <= words[i]["s"] <= start + late]
    if exact0:
        i0 = min(exact0, key=lambda i: abs(words[i]["s"] - start))
    elif cands:
        i0 = min(cands, key=lambda i: (abs(words[i]["s"] - start) + (0 if words[i]["s"] <= start else 1.5)))
    else:
        i0 = min(range(len(words)), key=lambda i: abs(words[i]["s"] - start))
    target = start + dur
    exact1 = [i for i, w in enumerate(words) if i >= i0 and abs(w["e"] - target) <= 0.4]
    ends = [i for i, w in enumerate(words) if i >= i0 and (_ends(w) or i == len(words) - 1 or words[i + 1]["s"] - w["e"] > 0.7)]
    ecands = [i for i in ends if target - end_early <= words[i]["e"] <= target + end_late]
    if exact1:
        i1 = min(exact1, key=lambda i: abs(words[i]["e"] - target))
    elif ecands:
        i1 = min(ecands, key=lambda i: abs(words[i]["e"] - target))
    else:
        i1 = max([i for i in range(i0, len(words)) if words[i]["e"] <= target + end_late] or [len(words) - 1])
    return max(0.0, words[i0]["s"] - 0.25), words[i1]["e"] + 0.4, words[i0:i1 + 1]


def fix(text, fixes):
    for a, b in fixes.items():
        text = text.replace(a, b)
    return text


def srt_lines(words, t0, max_words=9, max_len=3.2):
    """Subtitle cues (start, end, text) relative to t0, broken at punctuation, pauses, or every few words."""
    cues, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = (nxt is None or _ends(w) or w["w"].strip().endswith(",") and len(cur) >= 4 or len(cur) >= max_words
               or (nxt and nxt["s"] - w["e"] > 0.6) or cur[-1]["e"] - cur[0]["s"] > max_len)
        if brk:
            cues.append((max(0.0, cur[0]["s"] - t0), max(0.0, cur[-1]["e"] - t0 + 0.15), "".join(x["w"] for x in cur).strip()))
            cur = []
    return cues


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    from scripts import TUTORIALS
    for key, t in TUTORIALS.items():
        for seg in t["segments"]:
            if seg[0] == "clip":
                vid, start, dur = seg[1], seg[2], seg[3]
                if not os.path.exists(cache_path(vid, start)) and not os.path.exists(f"{DL}/{vid}.m4a"):
                    print(f"{key} {vid} {start}: no audio in {DL} yet", flush=True); continue
                s, e, ws = snap(vid, start, dur)
                print(f"{key} {vid} {start:>5}+{dur:<3} -> {s:7.2f}-{e:7.2f} ({e - s:4.1f}s): {''.join(w['w'] for w in ws).strip()}",
                      flush=True)

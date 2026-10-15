"""Whisper transcripts of the atomizer videos: faster-whisper large-v3-turbo, int8, on CPU.

    python transcribe.py                  # every video in PRIORITY without a word-timed transcript yet
    python transcribe.py prj_xgeuQtM ...  # just these

Batched for speed, with word timestamps so that the segments can be re-cut at sentence ends (or every ~12 s of speech),
and the words themselves kept in the JSON (`words`: [start, end, word, probability]) for cutting clips on them:
the batched pipeline on its own returns 30-45 s segments, too coarse for a timestamp link. Videos in NO_VAD are machine
noise with speech underneath, which the voice-activity filter drops whole, so they run without it, in fixed
30 s windows.
Audio comes from DL (<id>.m4a); missing files are pulled from the stream-cam Pi, rate-capped, as tools/dl.sh left them.
"""
import json, os, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel, BatchedInferencePipeline

PRIORITY = ["u-KjR5TENN4", "f8KL31PN8bA", "LSQmxwmlTkQ", "naePD8o9_Gk", "9kn-HhXCr1o", "58wJ_Khwgyk", "txH397FGTAU",
            "FDRTt68Vfvo", "1F9_4ccwhss", "HTlUrAr5HVU", "Pk0K5sBz-sQ", "tfb4fsVNIFI", "TFpU4uqVF9c", "of5-LhkX_VQ",
            "qYyT39D5Yzo", "2wMgeI-E7zw", "QXSj0j1OqL8", "z6rwmQW_3Vg", "07QOPRHIEvw", "Kv9DT3Vo0GE", "cKwQbKdE22Q",
            "w02MRlZhpNk", "prj_xgeuQtM", "BxA7Z9Fliss", "dXRB7c6GeDw", "wRc8p2_FnJo"]
NO_VAD = {"u-KjR5TENN4", "QXSj0j1OqL8"}
MODEL = "large-v3-turbo"
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl"); OUT = os.environ.get("ATOMIZER_TX", "/tmp/work/transcripts")
MAX_SEG = 12.0


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def fmt(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def piece(words):
    """One output segment, keeping its words as [start, end, word, probability]."""
    return {"start": round(words[0].start, 2), "end": round(words[-1].end, 2),
            "text": "".join(x.word for x in words).strip(),
            "words": [[round(x.start, 2), round(x.end, 2), x.word, round(x.probability, 3)] for x in words]}


def recut(segments):
    """Split Whisper's segments at sentence ends, or when a piece passes MAX_SEG seconds, using the word times."""
    out = []
    for s in segments:
        words = s.words or []
        if not words:
            out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(), "words": []}); continue
        cur = []
        for w in words:
            cur.append(w)
            ends_sentence = w.word.strip().endswith((".", "?", "!"))
            if ends_sentence or (cur[-1].end - cur[0].start) > MAX_SEG:
                out.append(piece(cur)); cur = []
        if cur:
            out.append(piece(cur))
    return [o for o in out if o["text"]]


def fetch(vid):
    remote = os.environ["RPI_STREAM_CAM_USERNAME"] + "@" + os.environ["RPI_STREAM_CAM_HOSTNAME"] + ":atomizer-dl/"
    subprocess.run(["rsync", "-aq", "--bwlimit=3000", remote + vid + ".m4a", DL + "/"], capture_output=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    pending = sys.argv[1:] or [v for v in PRIORITY if not os.path.exists(f"{OUT}/{v}.json")
                               or "words" not in (json.load(open(f"{OUT}/{v}.json"))["segments"] or [{}])[0]]
    model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    pipe = BatchedInferencePipeline(model=model)
    for attempt in range(3):
        still = []
        for vid in pending:
            m4a = f"{DL}/{vid}.m4a"
            if not os.path.exists(m4a):
                fetch(vid)
            if not os.path.exists(m4a):
                still.append(vid); print(time.strftime("%H:%M:%S"), vid, "audio not available yet", flush=True); continue
            t = time.time(); audio = load(m4a)
            dur = len(audio) / 16000
            clips = [{"start": s, "end": min(s + 30.0, dur)} for s in range(0, int(dur), 30)] if vid in NO_VAD else None
            segs, info = pipe.transcribe(audio, language="en", batch_size=8, vad_filter=vid not in NO_VAD,
                                         clip_timestamps=clips, word_timestamps=True)
            out = recut(list(segs))
            with open(f"{OUT}/{vid}.srt", "w") as srt, open(f"{OUT}/{vid}.txt", "w") as txt:
                for i, s in enumerate(out, 1):
                    srt.write(f"{i}\n{fmt(s['start'])} --> {fmt(s['end'])}\n{s['text']}\n\n")
                    txt.write(f"[{int(s['start'] // 60):02d}:{int(s['start'] % 60):02d}] {s['text']}\n")
            json.dump({"video_id": vid, "model": f"faster-whisper {MODEL} int8 (batched, word timestamps, "
                       + ("no vad" if vid in NO_VAD else "vad") + ")", "duration": info.duration, "segments": out},
                      open(f"{OUT}/{vid}.json", "w"), indent=0)
            print(time.strftime("%H:%M:%S"), vid, f"done {info.duration / 60:.1f} min audio in {(time.time() - t) / 60:.1f} min,",
                  len(out), "segments", flush=True)
        pending = still
        if not pending:
            break
        time.sleep(60)
    print("TRANSCRIPTION LOOP FINISHED", flush=True)


if __name__ == "__main__":
    main()

"""Word-level Whisper re-runs of short disputed clips, plus a speech check of the videos Whisper found silent.

    python recheck_clips.py      # writes ../transcripts/whisper/recheck-clips.json

The Whisper transcripts of the first 16 videos came from the batched pipeline, whose 30 s-4 min segments sometimes drop
or merge a short line. Where the auto-captions and that transcript disagreed on a number, a name or a label, the clip
around the line is decoded again on its own: faster-whisper large-v3-turbo, int8, not batched, no VAD, word timestamps,
beam 5, and beam 1 as a second opinion where the first left doubt. Every window that was decoded is listed, including the
ones that came out less clear; the notes cite them as "clip re-run". The VAD check runs Silero at the default threshold
and at a sensitive one on the three videos with (almost) no speech, to show that their Whisper text is hallucination.
Audio comes from DL (<id>.m4a), fetched from the stream-cam Pi with transcribe.py's rate-capped rsync if missing.
"""
import json, os, subprocess, time
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DL = os.environ.get("ATOMIZER_DL", "/tmp/work/dl")
OUT = f"{ROOT}/transcripts/whisper/recheck-clips.json"
# (video, start s, end s, beams, what the clip is checked for)
CLIPS = [
    ("1F9_4ccwhss", 120, 160, (5,), "Video 4 02:18 sealing block vs sealing rod"),
    ("1F9_4ccwhss", 130, 150, (5, 1), "Video 4 02:18 sealing block vs sealing rod"),
    ("1F9_4ccwhss", 210, 232, (5,), "Video 4 03:35 the 1300 phrase"),
    ("1F9_4ccwhss", 212, 232, (5, 1), "Video 4 03:35 the 1300 phrase"),
    ("1F9_4ccwhss", 200, 250, (5, 1), "Video 4 03:35 the 1300 phrase"),
    ("1F9_4ccwhss", 560, 596, (5,), "Video 4 09:30 oxygen sensor"),
    ("HTlUrAr5HVU", 30, 80, (5,), "Video 8 00:37 nozzle drill size"),
    ("HTlUrAr5HVU", 165, 180, (5,), "Video 8 02:52 hole or holder"),
    ("HTlUrAr5HVU", 445, 475, (5,), "Video 8 07:30 100 %"),
    ("2wMgeI-E7zw", 145, 180, (5,), "Sterling's phone 02:29 coolant flow"),
    ("2wMgeI-E7zw", 485, 505, (5,), "Sterling's phone 08:03 ultrasonic run time"),
    ("TFpU4uqVF9c", 575, 615, (5,), "RUN1 09:48 '10. Final one'"),
    ("TFpU4uqVF9c", 1145, 1175, (5,), "RUN1 19:14 pour-pressure label"),
    ("TFpU4uqVF9c", 1220, 1245, (5,), "RUN1 20:36 end-of-pour sequence"),
    ("qYyT39D5Yzo", 865, 900, (5,), "OCT2a 14:42 torque setting"),
    ("qYyT39D5Yzo", 1100, 1150, (5,), "OCT2a 18:44 0.5 mm"),
    ("of5-LhkX_VQ", 980, 1025, (5,), "OCT2b 16:31 pressure control on or off"),
    ("of5-LhkX_VQ", 1330, 1425, (5,), "OCT2b 22:15-23:37 plug length and pour pressure"),
    ("of5-LhkX_VQ", 1395, 1415, (5, 1), "OCT2b 23:17 pour pressure"),
    ("of5-LhkX_VQ", 1540, 1595, (5,), "OCT2b 25:53 plate"),
    ("of5-LhkX_VQ", 1550, 1575, (5, 1), "OCT2b 25:53 plate"),
    ("of5-LhkX_VQ", 1595, 1640, (5,), "OCT2b 26:45 pour"),
    ("w02MRlZhpNk", 100, 125, (5,), "dehumidifier 01:43 breaker"),
    ("Kv9DT3Vo0GE", 100, 110, (5,), "construction 01:44 who drills the sink holes"),
    ("prj_xgeuQtM", 0, 25, (5,), "the only detected speech in the nzyjn0 dosing video"),
    ("u-KjR5TENN4", 0, 6, (5,), "the only VAD blip in the expert cleaning POV"),
]
VAD_CHECK = ["u-KjR5TENN4", "QXSj0j1OqL8", "prj_xgeuQtM"]


def audio(vid):
    path = f"{DL}/{vid}.m4a"
    if not os.path.exists(path):
        remote = os.environ["RPI_STREAM_CAM_USERNAME"] + "@" + os.environ["RPI_STREAM_CAM_HOSTNAME"] + ":atomizer-dl/"
        subprocess.run(["rsync", "-aq", "--bwlimit=3000", remote + vid + ".m4a", DL + "/"], capture_output=True)
    return path


def load(path, start=None, end=None):
    cut = ["-ss", str(start), "-t", str(end - start)] if start is not None else []
    raw = subprocess.run(["ffmpeg", "-v", "error", *cut, "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    clips = []
    for vid, start, end, beams, why in CLIPS:
        pcm = load(audio(vid), start, end)
        for beam in beams:
            segs, _ = model.transcribe(pcm, language="en", beam_size=beam, word_timestamps=True, vad_filter=False,
                                       condition_on_previous_text=False)
            segs = [{"start": round(start + s.start, 2), "end": round(start + s.end, 2), "text": s.text.strip(),
                     "avg_logprob": round(s.avg_logprob, 2)} for s in segs]
            clips.append({"video_id": vid, "clip": [start, end], "beam": beam, "checks": why, "segments": segs})
            print(time.strftime("%H:%M:%S"), vid, start, end, f"beam {beam}:", " | ".join(s["text"] for s in segs), flush=True)
    vad = []
    for vid in VAD_CHECK:
        pcm = load(audio(vid))
        for th in (0.5, 0.2):
            ts = get_speech_timestamps(pcm, VadOptions(threshold=th, min_speech_duration_ms=250, min_silence_duration_ms=1000,
                                                       speech_pad_ms=200))
            vad.append({"video_id": vid, "threshold": th, "duration_s": round(len(pcm) / 16000, 1),
                        "speech_s": round(sum(t["end"] - t["start"] for t in ts) / 16000, 1),
                        "regions": [[round(t["start"] / 16000, 2), round(t["end"] / 16000, 2)] for t in ts]})
            print(vid, th, vad[-1]["speech_s"], "s of speech", flush=True)
    json.dump({"model": "faster-whisper large-v3-turbo int8 (not batched, no vad, word timestamps)", "clips": clips,
               "vad_check": vad}, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()

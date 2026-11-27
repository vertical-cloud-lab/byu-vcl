"""The floor-space segment's narration: Kokoro v1.0, voice af_heart at 0.96 speed, as the campaign video
(twin/video/narration.py's phonemes, respellings and model files), from twin/video/narration_floorspace.json.

    cd vertical-lab
    python -m twin.video.floorspace_voice tts       # speak the lines whose text changed -> out/floorspace/narration/
    python -m twin.video.floorspace_voice check     # heard back by faster-whisper (small.en): check.json

Each line's FLAC (24 kHz, 16-bit) and lines.json (text, spoken form, phonemes, seconds, sha256) are committed, so the
segment rebuilds without the speech model. A line is spoken again only when its text changes.
"""
from __future__ import annotations

import hashlib
import math
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

from . import narration as N

HERE = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).with_name("narration_floorspace.json")
NDIR = HERE / "out" / "floorspace" / "narration"


def script() -> dict:
    return json.loads(SCRIPT.read_text())


def spoken(text: str, say: dict) -> str:
    """The line with this segment's respellings (numbers with thousands separators: the phonemizer reads '4,280' as
    'four, two hundred eighty'), then narration.SAY's."""
    for a in sorted(say, key=len, reverse=True):
        text = re.sub(r"(?<![\w.,])" + re.escape(a) + r"(?![\w,]|\.\d)", say[a], text)
    return text


def tts(force: bool = False) -> dict:
    import soundfile as sf
    sc = script()
    say = sc.get("say", {})
    NDIR.mkdir(parents=True, exist_ok=True)
    recp = NDIR / "lines.json"
    rec = json.loads(recp.read_text()) if recp.exists() else {"lines": {}}
    k = None
    keep = {}
    for ln in sc["lines"]:
        path = NDIR / f"{ln['id']}.flac"
        sp = spoken(ln["text"], say)
        have = rec["lines"].get(ln["id"])
        if not force and have and have.get("text") == ln["text"] and have.get("spoken") == sp and path.exists():
            keep[ln["id"]] = have
            continue
        ph = N.phonemes(sp)
        if k is None:
            from kokoro_onnx import Kokoro
            k = Kokoro(*N.KOKORO)
        y, sr = k.create(ph, voice=N.VOICE, speed=N.SPEED, lang="en-us", is_phonemes=True)
        assert sr == N.SR, sr
        sf.write(str(path), np.asarray(y, np.float32), N.SR, format="FLAC", subtype="PCM_16")
        y, _ = sf.read(str(path), dtype="float32")
        keep[ln["id"]] = dict(text=ln["text"], spoken=sp, phonemes=ph, seconds=round(len(y) / N.SR, 2),
                              sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        print(f"{ln['id']}: {keep[ln['id']]['seconds']:.2f} s", flush=True)
    for f in NDIR.glob("*.flac"):
        if f.stem not in keep:
            f.unlink()
    out = dict(voice=f"Kokoro v1.0 {N.VOICE} (kokoro-onnx, open weights), speed {N.SPEED}", voice_id=N.VOICE,
               speed=N.SPEED, rate=N.SR, model_sha256={
                   "kokoro-v1.0.onnx": "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
                   "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"},
               lines=keep)
    recp.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    return out


def durations() -> dict:
    rec = json.loads((NDIR / "lines.json").read_text())
    return {k: v["seconds"] for k, v in rec["lines"].items()}


def _norm(t: str) -> list:
    t = t.lower().replace("-", " ")
    t = re.sub(r"[^a-z0-9. ]", " ", t)
    return [w.strip(".") for w in t.split() if w.strip(".")]


def _audio16k(path) -> np.ndarray:
    """A file as 16 kHz mono float32, decoded here (this runner's PyAV is newer than faster-whisper's decoder)."""
    import soundfile as sf
    from scipy.signal import resample_poly
    y, sr = sf.read(str(path), dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    g = math.gcd(int(sr), 16000)
    return resample_poly(y, 16000 // g, int(sr) // g).astype(np.float32)


def check(model="small.en") -> dict:
    """Every line transcribed by faster-whisper and compared word by word with its spoken form (numbers in words)."""
    import jiwer
    from faster_whisper import WhisperModel
    from num2words import num2words
    wm = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=int(os.environ.get("WHISPER_THREADS", "1")))
    sc = script()
    say = sc.get("say", {})
    res, ref_all, hyp_all = {}, [], []

    def words(t):
        t = spoken(t, say)
        t = N.spoken(t)
        t = re.sub(r"(\d+)\.(\d+)", lambda m: f"{m.group(1)} point {' '.join(m.group(2))}", t)
        t = re.sub(r"\d+", lambda m: num2words(int(m.group(0))), t)
        return " ".join(_norm(t))
    for ln in sc["lines"]:
        segs, _ = wm.transcribe(_audio16k(NDIR / f"{ln['id']}.flac"), language="en", beam_size=5)
        hyp = " ".join(s.text for s in segs).strip()
        r, h = words(ln["text"]), words(hyp)
        res[ln["id"]] = dict(text=ln["text"], heard=hyp, wer=round(jiwer.wer(r, h), 4))
        ref_all.append(r)
        hyp_all.append(h)
        print(ln["id"], res[ln["id"]]["wer"], "|", hyp, flush=True)
    out = dict(model=model, wer=round(jiwer.wer(" ".join(ref_all), " ".join(hyp_all)), 4), lines=res)
    (NDIR / "check.json").write_text(json.dumps(out, indent=1) + "\n")
    print("overall WER", out["wer"])
    return out


def check_encoded(mp4: Path, model="small.en") -> dict:
    """The encoded file's own audio, transcribed whole and compared word by word with the whole script."""
    import subprocess
    import tempfile
    import jiwer
    from faster_whisper import WhisperModel
    from num2words import num2words
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vn", "-ac", "1", "-ar", "16000", str(wav)],
                       check=True)
        y = _audio16k(wav)
    wm = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=int(os.environ.get("WHISPER_THREADS", "2")))
    segs, _ = wm.transcribe(y, language="en", beam_size=5)
    hyp = " ".join(sg.text for sg in segs).strip()
    sc = script()
    say = sc.get("say", {})

    def words(t):
        t = N.spoken(spoken(t, say))
        t = re.sub(r"(\d+)\.(\d+)", lambda m: f"{m.group(1)} point {' '.join(m.group(2))}", t)
        t = re.sub(r"\d+", lambda m: num2words(int(m.group(0))), t.replace(",", ""))
        return " ".join(_norm(t))
    ref = " ".join(words(ln["text"]) for ln in sc["lines"])
    out = dict(model=model, file=Path(mp4).name, wer=round(jiwer.wer(ref, words(hyp)), 4), heard=hyp)
    (NDIR / "encoded_check.json").write_text(json.dumps(out, indent=1) + "\n")
    print("encoded file's audio WER", out["wer"])
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if sys.argv[1:] else "tts"
    if cmd == "tts":
        tts(force="--force" in sys.argv)
        print(json.dumps(durations()))
    elif cmd == "check":
        check(sys.argv[2] if sys.argv[2:] else "small.en")
    elif cmd == "check_encoded":
        check_encoded(Path(sys.argv[2]))
    else:
        raise SystemExit(__doc__)

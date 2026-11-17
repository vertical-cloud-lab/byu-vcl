"""Transcribe an audio file with Whisper large-v3 (via faster-whisper, on CPU).

Writes three files next to each other in OUT_DIR:

- transcript.txt   plain text, one segment per line
- transcript.md    the same with [mm:ss] timestamps
- transcript.json  segments plus model, settings and timing, for provenance

Usage:
    pip install faster-whisper
    python scripts/transcribe_whisper.py AUDIO OUT_DIR [--model large-v3] [--language en]

On a 4-core GitHub runner, large-v3 in int8 transcribed a 5.5 min memo in 3-5.5 min
(docs/talks/2026-11-17-research-lunch-and-learn). The default conditioning on previous
text looped ("Yeah." x10) there; --no-condition-on-previous-text did not.

Audio is decoded here with PyAV (bundled FFmpeg), so no system ffmpeg is needed.
We do not use faster-whisper's own decode_audio(): faster-whisper 1.2.1 passes
av.open(..., metadata_errors=...), which PyAV 19 (the version pip picks for
Python 3.14) no longer accepts, so it fails with a TypeError before transcribing.
"""

import argparse
import json
import time
from pathlib import Path

import av
import numpy as np
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000  # what Whisper expects


def decode_audio(path: str) -> np.ndarray:
    """Any audio/video file -> mono float32 at 16 kHz in [-1, 1]."""
    chunks = []
    resampler = av.AudioResampler(format="s16", layout="mono", rate=SAMPLE_RATE)
    with av.open(path) as container:
        for frame in container.decode(audio=0):
            chunks += [f.to_ndarray().reshape(-1) for f in resampler.resample(frame)]
    chunks += [f.to_ndarray().reshape(-1) for f in resampler.resample(None)]  # flush
    return np.concatenate(chunks).astype(np.float32) / 32768.0


def mmss(seconds: float) -> str:
    m, s = divmod(int(round(seconds)), 60)
    return f"{m:02d}:{s:02d}"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("audio")
    p.add_argument("out_dir")
    p.add_argument("--model", default="large-v3")
    p.add_argument("--language", default="en", help="'auto' to detect")
    p.add_argument("--compute-type", default="int8")
    p.add_argument("--beam-size", type=int, default=5)
    p.add_argument(
        "--no-vad",
        action="store_true",
        help="keep long silences (VAD trimming reduces hallucinated text in pauses)",
    )
    p.add_argument(
        "--no-condition-on-previous-text",
        action="store_true",
        help="decode each 30 s window independently; breaks the repetition loops "
        "(e.g. 'Yeah.' x10) and lost punctuation large-v3 can fall into",
    )
    args = p.parse_args()
    condition = not args.no_condition_on_previous_text

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    model = WhisperModel(args.model, device="cpu", compute_type=args.compute_type)
    t_load = time.time() - t0

    segments, info = model.transcribe(
        decode_audio(args.audio),
        language=None if args.language == "auto" else args.language,
        beam_size=args.beam_size,
        vad_filter=not args.no_vad,
        condition_on_previous_text=condition,
    )
    segs = []
    for s in segments:  # generator: transcription happens here
        segs.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        print(f"[{mmss(s.start)}] {s.text.strip()}", flush=True)
    t_total = time.time() - t0

    (out / "transcript.txt").write_text("\n".join(s["text"] for s in segs) + "\n")
    (out / "transcript.md").write_text(
        "\n\n".join(f"**[{mmss(s['start'])}]** {s['text']}" for s in segs) + "\n"
    )
    (out / "transcript.json").write_text(
        json.dumps(
            {
                "audio": Path(args.audio).name,
                "duration_s": round(info.duration, 2),
                "language": info.language,
                "language_probability": round(info.language_probability, 3),
                "model": f"faster-whisper {args.model}",
                "compute_type": args.compute_type,
                "beam_size": args.beam_size,
                "vad_filter": not args.no_vad,
                "condition_on_previous_text": condition,
                "model_load_s": round(t_load, 1),
                "wall_clock_s": round(t_total, 1),
                "segments": segs,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()

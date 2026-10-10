#!/usr/bin/env python3
"""Word-level ASR over padded windows of a source file.

Usage: python3 asr_dump.py spans.json out.json
spans.json: {"source": "/path.mp4", "windows": [[s, e, "tag"], ...]}
Emits {"tag": {"window": [s,e], "words": [[abs_start, abs_end, prob, "text"], ...]}}
Times are absolute seconds on the source timeline.
"""
import json
import subprocess
import sys
import tempfile

from faster_whisper import WhisperModel

spans = json.load(open(sys.argv[1]))
model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8",
                     cpu_threads=4)
out = {}
for s, e, tag in spans["windows"]:
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-loglevel", "error",
                        "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", spans["source"],
                        "-vn", "-ac", "1", "-ar", "16000", f.name], check=True)
        segs, _ = model.transcribe(f.name, language="en", word_timestamps=True,
                                   beam_size=5,
                                   hotwords="Claude BoTorch Bayesian CAD Jarvis")
        words = []
        for seg in segs:
            for w in seg.words or []:
                words.append([round(s + w.start, 3), round(s + w.end, 3),
                              round(w.probability, 2), w.word.strip()])
    out[tag] = {"window": [s, e], "words": words}
    print(f"{tag}: {len(words)} words", flush=True)

json.dump(out, open(sys.argv[2], "w"), indent=0)
print("ASR_DUMP_DONE")

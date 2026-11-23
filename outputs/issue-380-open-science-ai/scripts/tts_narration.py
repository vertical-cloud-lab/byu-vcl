#!/usr/bin/env python3
"""Synthesize narration per scene with Kokoro-82M (Apache-2.0), offline on CPU.
Writes video/audio/<scene>.wav (24 kHz) and video/durations.json. Run with the TTS venv."""
import json, sys, os, numpy as np, soundfile as sf
from kokoro import KPipeline
NARR = os.environ.get("NARR", "video/narration.json"); DURF = os.environ.get("DURF", "video/durations.json")
N = json.load(open(NARR))
only = set(sys.argv[1:])
pipe = KPipeline(lang_code="a")
dur = json.load(open(DURF)) if os.path.exists(DURF) else {}
for s in N:
    if only and s["scene"] not in only:
        continue
    chunks = [a for _, _, a in pipe(s["text"], voice="af_heart", speed=1.0, split_pattern=r"\n+")]
    gap = np.zeros(int(0.25 * 24000), dtype=np.float32)
    audio = np.concatenate([np.concatenate([c.numpy() if hasattr(c, "numpy") else c, gap]) for c in chunks])
    sf.write(f"video/audio/{s['scene']}.wav", audio, 24000)
    dur[s["scene"]] = round(len(audio) / 24000, 2)
    print(s["scene"], dur[s["scene"]], flush=True)
    json.dump(dur, open(DURF, "w"), indent=1)
print("total", round(sum(dur.values()), 1))

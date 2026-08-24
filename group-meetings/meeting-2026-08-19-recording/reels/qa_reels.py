#!/usr/bin/env python3
"""QA: re-transcribe every rendered reel and check the cut junctions.

For each reel MP4: transcribe with faster-whisper (word timestamps), then verify each
item's expected first and last display words are heard near their planned output
offsets, and print the full re-heard text for eyeball review. Also reports integrated
loudness and that video and audio durations match.

Usage: python3 qa_reels.py --outdir /path/to/rendered [reel-id ...]
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
FPS = 30


def snap(t):
    return round(t * FPS) / FPS


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("reels", nargs="*")
    args = ap.parse_args()
    edl = json.load(open(HERE / "reels-edl.json"))
    out = Path(args.outdir)
    model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
    fails = 0
    for reel in edl["reels"]:
        if args.reels and reel["id"] not in args.reels:
            continue
        mp4 = out / f"{reel['output_basename']}.mp4"
        pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "stream=codec_type,duration", "-of", "json", mp4],
                            capture_output=True, text=True)
        sd = {s["codec_type"]: float(s["duration"])
              for s in json.loads(pr.stdout)["streams"]}
        ln = subprocess.run(["ffmpeg", "-nostdin", "-i", mp4, "-af",
                             "loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json",
                             "-f", "null", "-"], capture_output=True, text=True)
        m = re.search(r"\{[^{}]+\}\s*$", ln.stderr)
        lint = json.loads(m.group(0))["input_i"] if m else "?"
        segs, _ = model.transcribe(str(mp4), language="en", word_timestamps=True,
                                   beam_size=5)
        heard = [(w.start, w.word.strip()) for s in segs for w in (s.words or [])]
        cursor = snap(reel["title_card"]["dur"])
        print(f"\n===== {reel['id']}  v={sd.get('video'):.2f}s "
              f"a={sd.get('audio'):.2f}s loudness={lint} LUFS")
        for item in reel["items"]:
            if item.get("card"):
                cursor += snap(item["card"]["dur"])
                continue
            dur = sum(snap(e) - snap(s) for s, e in item["segments"])
            words = item["words"]
            exp_first = [norm(w[2]) for w in words[:2]]
            exp_last = [norm(w[2]) for w in words[-2:]]
            head = [norm(w) for t, w in heard if cursor - 1.2 <= t <= cursor + 2.5]
            tail = [norm(w) for t, w in heard
                    if cursor + dur - 2.5 <= t <= cursor + dur + 1.2]
            ok = (any(e in head for e in exp_first if e),
                  any(e in tail for e in exp_last if e))
            if not all(ok):
                fails += 1
            print(f"  [{'OK' if ok[0] else 'HEAD?'} {'OK' if ok[1] else 'TAIL?'}] "
                  f"{item['id']:16s} @{cursor:7.2f}s+{dur:5.2f}")
            cursor += dur
        print("  FULL: " + " ".join(w for _, w in heard))
    print(f"\nQA {'PASS' if fails == 0 else f'{fails} CHECK(S) FLAGGED'}")


if __name__ == "__main__":
    main()

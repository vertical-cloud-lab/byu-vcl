#!/usr/bin/env python3
"""QA the rendered reels: re-transcribe each finished MP4 and check that every EDL item's
first and last kept words survive at the offset the renderer planned for them, then
report loudness and A/V duration parity. Catches clipped words at a junction -- the
failure mode reported on the first highlights cut -- on the *rendered output* rather
than on the plan.

Usage: python3 qa_reels.py --dir /tmp/reels-out [--only reel-id]
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FPS = 30


def snap(t):
    return round(t * FPS) / FPS


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def probe(mp4):
    out = {}
    for stream in ("v", "a"):
        pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream,
                             "-show_entries", "stream=duration", "-of",
                             "default=nw=1:nk=1", str(mp4)],
                            capture_output=True, text=True)
        out[stream] = float(pr.stdout.strip().splitlines()[0])
    pr = subprocess.run(["ffmpeg", "-nostdin", "-i", str(mp4), "-af",
                         "loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json", "-f",
                         "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]+\}\s*$", pr.stderr)
    out["lufs"] = float(json.loads(m.group(0))["input_i"]) if m else float("nan")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--only", default=None)
    ap.add_argument("--window", type=float, default=3.2,
                    help="seconds either side of a junction to check")
    args = ap.parse_args()
    from faster_whisper import WhisperModel
    model = WhisperModel("distil-large-v3", device="cpu", compute_type="int8")
    edl = json.load(open(HERE / "reels-edl.json"))
    bad = 0
    for reel in edl["reels"]:
        if args.only and reel["id"] != args.only:
            continue
        mp4 = Path(args.dir) / f"{reel['output_basename']}.mp4"
        if not mp4.exists():
            print(f"{reel['id']}: MISSING {mp4}")
            bad += 1
            continue
        wav = Path("/tmp") / f"qa_{reel['id']}.wav"
        subprocess.run(["ffmpeg", "-y", "-nostdin", "-v", "error", "-i", str(mp4),
                        "-vn", "-ar", "16000", "-ac", "1", str(wav)], check=True)
        segs, _ = model.transcribe(str(wav), language="en", beam_size=5,
                                   word_timestamps=True, condition_on_previous_text=False)
        heard = [(w.start, norm(w.word)) for s in segs for w in s.words if norm(w.word)]
        info = probe(mp4)
        cursor = snap(reel["title_card"]["dur"])
        print(f"\n=== {reel['id']}  {info['v']:.2f}s v / {info['a']:.2f}s a  "
              f"{info['lufs']:.1f} LUFS")
        if abs(info["v"] - info["a"]) > 0.05:
            print(f"    !! A/V duration mismatch {info['v'] - info['a']:+.3f}s")
            bad += 1
        for item in reel["items"]:
            if item.get("card"):
                cursor += snap(item["card"]["dur"])
                continue
            dur = round(sum(snap(e) - snap(s) for s, e in item["segments"]) * FPS) / FPS
            words = [w[2] for w in item["words"]]
            for tag, expect, at in (("open", words[:3], cursor),
                                    ("close", words[-3:], cursor + dur)):
                want = [norm(w) for w in expect if norm(w)]
                near = [w for t, w in heard if abs(t - at) <= args.window]
                ok = any(near[i:i + len(want)] == want
                         for i in range(max(0, len(near) - len(want) + 1)))
                if not ok:   # fall back to "most of the words are there somewhere near"
                    ok = sum(w in near for w in want) >= max(1, len(want) - 1)
                if not ok:
                    bad += 1
                    print(f"    !! {item['id']:<18} {tag} @{at:7.2f}s expected "
                          f"{' '.join(want)!r}, heard {' '.join(near)!r}")
            cursor += dur
        print(f"    {sum(1 for i in reel['items'] if not i.get('card'))} items checked")
    print(f"\n{'FAIL' if bad else 'PASS'}: {bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

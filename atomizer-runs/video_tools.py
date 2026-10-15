#!/usr/bin/env python3
"""Look at atomizer run videos: contact sheets, picked frames and crops, transcripts.

The videos are first-person phone recordings, so the camera moves all the time and
fixed-ROI measurements don't work. This is for finding moments and reading them:
a contact sheet to find where things happen, then full-resolution frames or crops
of those moments, and a Whisper transcript of the narration.

    python video_tools.py sheet VIDEO OUT.jpg --start 0 --end 754 --step 26 --cols 6 --width 320
    python video_tools.py frames VIDEO OUT.jpg --cols 2 --width 800 3 99 "111@380,0,830,600"
    python video_tools.py transcribe AUDIO [AUDIO ...] --out-dir DIR --model small.en

A frame spec is a time in seconds, optionally with a crop in source pixels:
``t@x0,y0,x1,y1``. Every tile is labelled with its own m:ss.s.

Needs opencv-python-headless and numpy; ``transcribe`` also needs faster-whisper and
imageio-ffmpeg. Audio is decoded with imageio-ffmpeg's static ffmpeg and handed to
Whisper as an array, because faster-whisper 1.2's own decoder calls PyAV with an
argument older PyAV builds reject.
"""

import argparse
import json
import os
import subprocess

import cv2
import numpy as np


def _label(im, t):
    lab = "%d:%04.1f" % (t // 60, t % 60)
    scale = 0.5 if im.shape[1] <= 400 else 0.6
    cv2.rectangle(im, (0, 0), (len(lab) * int(22 * scale) + 8, int(40 * scale)), (0, 0, 0), -1)
    cv2.putText(im, lab, (4, int(30 * scale)), cv2.FONT_HERSHEY_SIMPLEX, scale,
                (255, 255, 255), 1, cv2.LINE_AA)
    return im


def _read(cap, t, crop=None):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, fr = cap.read()
    if not ok:
        return None
    if crop:
        x0, y0, x1, y1 = crop
        fr = fr[y0:y1, x0:x1]
    return fr


def _tile(fr, width):
    h = int(round(width * fr.shape[0] / fr.shape[1]))
    interp = cv2.INTER_AREA if fr.shape[1] > width else cv2.INTER_CUBIC
    return cv2.resize(fr, (width, h), interpolation=interp)


def _assemble(tiles, cols, out, quality):
    th = max(t.shape[0] for t in tiles)
    tw = tiles[0].shape[1]
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.zeros((rows * th, cols * tw, 3), np.uint8)
    for i, im in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r * th:r * th + im.shape[0], c * tw:(c + 1) * tw] = im
    cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, quality])
    print(out, "%d tiles" % len(tiles), "%dx%d" % (sheet.shape[1], sheet.shape[0]))


def sheet(a):
    cap = cv2.VideoCapture(a.video)
    tiles, t = [], a.start
    while t <= a.end + 1e-6:
        fr = _read(cap, t)
        if fr is None:
            break
        tiles.append(_label(_tile(fr, a.width), t))
        t += a.step
    _assemble(tiles, a.cols, a.out, a.quality)


def frames(a):
    cap = cv2.VideoCapture(a.video)
    tiles = []
    for spec in a.specs:
        t, _, crop = spec.partition("@")
        fr = _read(cap, float(t), tuple(map(int, crop.split(","))) if crop else None)
        if fr is not None:
            tiles.append(_label(_tile(fr, a.width), float(t)))
    _assemble(tiles, a.cols, a.out, a.quality)


def transcribe(a):
    import imageio_ffmpeg
    from faster_whisper import WhisperModel

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    os.makedirs(a.out_dir, exist_ok=True)
    for path in a.audio:
        raw = subprocess.run([ff, "-v", "error", "-i", path, "-ac", "1", "-ar", "16000",
                              "-f", "s16le", "-"], capture_output=True, check=True).stdout
        audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
        segs, _ = model.transcribe(audio, language="en", vad_filter=True, beam_size=5)
        out = [{"start": round(s.start, 1), "end": round(s.end, 1), "text": s.text.strip()}
               for s in segs]
        name = os.path.basename(path).split(".")[0]
        dest = os.path.join(a.out_dir, "transcript_%s.json" % name)
        json.dump(out, open(dest, "w"), indent=1)
        print(dest, "%d segments" % len(out))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet", help="one frame every STEP seconds, tiled")
    s.add_argument("video")
    s.add_argument("out")
    s.add_argument("--start", type=float, default=0)
    s.add_argument("--end", type=float, required=True)
    s.add_argument("--step", type=float, required=True)
    s.add_argument("--cols", type=int, default=6)
    s.add_argument("--width", type=int, default=320)
    s.add_argument("--quality", type=int, default=82)
    s.set_defaults(func=sheet)
    f = sub.add_parser("frames", help="picked frames or crops, tiled")
    f.add_argument("video")
    f.add_argument("out")
    f.add_argument("specs", nargs="+", help="t or t@x0,y0,x1,y1 (seconds, source px)")
    f.add_argument("--cols", type=int, default=2)
    f.add_argument("--width", type=int, default=800)
    f.add_argument("--quality", type=int, default=85)
    f.set_defaults(func=frames)
    w = sub.add_parser("transcribe", help="Whisper transcript per audio file, as JSON")
    w.add_argument("audio", nargs="+")
    w.add_argument("--out-dir", default=".")
    w.add_argument("--model", default="small.en")
    w.set_defaults(func=transcribe)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()

"""Round 16 (PR #371's check: "out/setup_lab.gif is round 14's render, not round 15's"): a render in HD mode
(VIZ3D_HD=1, render_r16.py) writes only its MP4 under out/r16/ and its sub-steps under out/clean/, never the GIF or the
still that the README and notes link, so those go stale whenever a clip is re-rendered for the long-form. This makes
both from the round-16 MP4: the GIF as scene.write_gif makes it (800 x 450, 10 fps, one palette, gifsicle, under
4.9 MB), and the still from the frame scene.py would have kept (the clip's JSON "still" frame when it has one, else
85 % of the way through).

    python3 r16_gifs.py setup_lab vlm_workflow ...     # out/r16/<clip>.mp4 -> out/<clip>.gif, out/<clip>_still.png
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
GIF_FPS = 10


def frames(mp4: Path, fps: float, size=(800, 450)):
    tmp = Path(tempfile.mkdtemp(prefix="r16gif_"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-i", str(mp4), "-vf",
                    f"fps={fps},scale={size[0]}:{size[1]}:flags=lanczos", str(tmp / "f%05d.png")], check=True)
    return [Image.open(p).convert("RGB") for p in sorted(tmp.glob("f*.png"))]


def main(names):
    from scene import write_gif
    for name in names:
        mp4 = OUT / "r16" / f"{name}.mp4"
        if not mp4.exists():
            print(f"{name}: no out/r16/{name}.mp4", flush=True)
            continue
        fr = frames(mp4, GIF_FPS)
        gif = OUT / f"{name}.gif"
        gif.parent.mkdir(parents=True, exist_ok=True)
        write_gif(fr, gif)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(mp4)], capture_output=True, text=True).stdout)
        meta = OUT / "clean" / f"{name}.json"
        t = 0.85 * dur
        if meta.exists():
            m = json.loads(meta.read_text())
            st = [s for s in m.get("substeps", []) if s.get("still")]
            if st:
                t = min(dur - 0.05, st[-1]["start_frame"] / float(m.get("fps", 30)) + 0.5)
        still = OUT / f"{name}_still.png"
        still.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                        str(still)], check=True)
        print(f"{name}: {len(fr)} GIF frames -> {gif.relative_to(HERE)} ({gif.stat().st_size / 1e6:.2f} MB), still at "
              f"{t:.1f} s -> {still.relative_to(HERE)}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])

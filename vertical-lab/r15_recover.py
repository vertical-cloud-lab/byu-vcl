"""Round 16 (#303, PR #318): round 15's clips back from its YouTube copy, so the long-form can be rebuilt without drawing
all 89 minutes again.

Round 15 rendered into out/r15/, which is git-ignored, so its renders went with its runner. Its long-form is on YouTube
(https://www.youtube.com/watch?v=79FL6mTFSsI), and round 15's own out/longform.json (at commit R15_COMMIT) says where
every part starts and how long it is, to the frame. So each clip is cut back out of the video:

    ssh -D 127.0.0.1:1080 -N -f <user>@<pi>                   # any lab Pi: YouTube refuses player requests from runners
    python3 r15_recover.py fetch --proxy socks5h://127.0.0.1:1080   # the 720p HLS stream (itag 232), 1001 segments,
                                                                    # each capped at 750 kB/s -> $R15_YT/r15.ts (438 MB)
    python3 r15_recover.py cut [CLIP ...]     # every mp4 part (or those named) -> out/r15/<rel>, out/r15/recovered.json

Frame n of the stream is at its start time plus n/30 s: checked at the set-up clip's first frame, where the stream's
frames 892-893 are the card and 894-895 the clip (round 15's longform.json: the clip starts at 29.80 s, 29.80 x 30 =
894). Each clip is decoded from 8 s before its start (a coarse seek), trimmed on those timestamps with a half-frame
margin and written at CRF 12, then its frames are counted against round 15's (all 53 matched).

longform.py takes a clip from out/r16/ first, then out/r15/, then out/mp4/, and speaks a narration line over a recovered
clip where round 15 spoke it (longform.r15_offsets). The cost is one more generation of YouTube's compression.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R15_URL = "https://www.youtube.com/watch?v=79FL6mTFSsI"
R15_COMMIT = "4f9ec11e"            # round 15's long-form build: its out/longform.json
ITAG = "232"                       # 720p30 H.264 HLS, the highest rate YouTube serves for it
YT = Path(os.environ.get("R15_YT", "/tmp/r15yt"))


def fetch(proxy: str, rate: str = "750K", workers: int = 2) -> Path:
    """The whole stream, segment by segment, through `proxy` (rate-capped per segment for the Pi's Wi-Fi)."""
    seg = YT / "seg"
    seg.mkdir(parents=True, exist_ok=True)
    info = YT / "info.json"
    if not info.exists():
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--proxy", proxy, "--js-runtimes", "node", "-J", R15_URL],
                           capture_output=True, check=True)
        info.write_bytes(r.stdout)
    fmt = next(f for f in json.loads(info.read_text())["formats"] if f["format_id"] == ITAG)
    playlist = YT / f"itag{ITAG}.m3u8"
    if not playlist.exists():
        subprocess.run(["curl", "-sf", "--max-time", "60", "--proxy", proxy, "-o", str(playlist), fmt["url"]],
                       check=True)
    urls = [ln.strip() for ln in playlist.read_text().splitlines() if ln.strip() and not ln.startswith("#")]

    def get(i):
        p = seg / f"{i:05d}.ts"
        if p.exists() and p.stat().st_size > 1000:
            return True
        tmp = p.with_suffix(".part")
        for _ in range(4):
            r = subprocess.run(["curl", "-sf", "--retry", "3", "--max-time", "300", "--proxy", proxy, "--limit-rate", rate,
                                "-o", str(tmp), urls[i]])
            if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 1000:
                tmp.rename(p)
                return True
        return False
    with cf.ThreadPoolExecutor(workers) as ex:
        bad = [i for i, ok in zip(range(len(urls)), ex.map(get, range(len(urls)))) if not ok]
    if bad:
        raise SystemExit(f"{len(bad)} segments failed: {bad[:10]}")
    lst = YT / "segs.txt"
    lst.write_text("".join(f"file '{seg / f'{i:05d}.ts'}'\n" for i in range(len(urls))))
    out = YT / "r15.ts"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-map",
                    "0:v", str(out)], check=True)
    print(f"{len(urls)} segments -> {out} ({out.stat().st_size / 1e6:.0f} MB)", flush=True)
    return out


def cut(only=()) -> list[dict]:
    ts = YT / "r15.ts"
    t0 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=start_time", "-of", "csv=p=0", str(ts)],
                              capture_output=True, text=True).stdout)
    meta = json.loads(subprocess.run(["git", "show", f"{R15_COMMIT}:./out/longform.json"], capture_output=True, text=True,
                                     cwd=HERE, check=True).stdout)
    done = []
    for r in meta["parts"]:
        if r["kind"] != "mp4":
            continue
        src = r["src"]
        rel = src.split("out/r15/", 1)[1] if "out/r15/" in src else src.split("out/mp4/", 1)[1]
        if only and rel not in only and Path(rel).stem not in only:
            continue
        n0, n1 = round(r["start_s"] * 30), round((r["start_s"] + r["seconds"]) * 30)
        dst = HERE / "out" / "r15" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        a, b = t0 + (n0 - 0.5) / 30, t0 + (n1 - 0.5) / 30
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-threads", "2", "-ss", f"{max(0.0, r['start_s'] - 8.0):.3f}",
                        "-copyts", "-i", str(ts), "-vf", f"trim=start={a:.5f}:end={b:.5f},setpts=PTS-STARTPTS", "-an",
                        "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-pix_fmt", "yuv420p",
                        "-threads", "2", "-movflags", "+faststart", str(dst)], check=True)
        got = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                              "stream=nb_read_frames", "-of", "csv=p=0", str(dst)], capture_output=True,
                             text=True).stdout.strip()
        done.append(dict(rel=rel, start_s=r["start_s"], frames=n1 - n0, got=got, ok=str(n1 - n0) == got))
        print(f"{'OK ' if done[-1]['ok'] else 'BAD'} {rel}: frames {n0}-{n1} ({n1 - n0}), got {got}", flush=True)
    (HERE / "out" / "r15" / "recovered.json").write_text(json.dumps(dict(
        source=f"{R15_URL}, itag {ITAG} (720p30 H.264), fetched through a lab Pi", start_time=t0, clips=done),
        indent=1) + "\n")
    return done


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "fetch":
        opt = dict(zip(args[1::2], args[2::2]))
        fetch(opt.get("--proxy", "socks5h://127.0.0.1:1080"))
    elif args and args[0] == "cut":
        cut(args[1:])
    else:
        print(__doc__)

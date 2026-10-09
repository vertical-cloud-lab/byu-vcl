# Atomizer runs

Analysis of runs on the Amazemet rePowder ultrasonic atomizer, one folder per run date.
This is the run-by-run record behind the repeatability study in
[#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261).

| Run | Write-up | In short |
| --- | --- | --- |
| 2026-10-08 | [`2026-10-08/`](2026-10-08/README.md) | The melt dripped onto a frozen lump on the plate's tip, or past it, and hardly atomized. O2 took at least three gas washes at 500 °C to reach the mid 20s ppm. |

Run 1 (2026-10-06) has no video, only the notes and photo in #261.

## Getting the videos

Run videos are phone recordings uploaded unlisted to the BYU Vertical Cloud Lab channel.
YouTube refuses player extraction from GitHub Actions runners (*"Sign in to confirm you're
not a bot"*), so download them on a Pi and copy them back. The OT-2 Pi that holds
`~/ytframes/grab.py` (see [`CLAUDE.md`](../CLAUDE.md)) was offline on 2026-10-09, so the
CubXL Pi was used:

```bash
PI="$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME"
ssh "$PI" 'mkdir -p ~/ytframes/atomizer && cd ~/ytframes/atomizer &&
  ~/.venvs/ytframes/bin/yt-dlp --limit-rate 2500K \
    -f "136/bv*[height<=720][ext=mp4],140/ba[ext=m4a]" \
    -o "%(id)s.f%(format_id)s.%(ext)s" --write-info-json --no-progress \
    https://youtu.be/<id> ...'
mkdir -p /tmp/atomizer-videos
scp -q -l 24000 "$PI:ytframes/atomizer/*" /tmp/atomizer-videos/
```

- That Pi has no JavaScript runtime. yt-dlp warns about it, but the 720p video (136) and
  the m4a audio (140) still came through on 2026-10-09.
- It has no ffmpeg either, so video and audio arrive as separate files. Nothing needs them
  merged: frames come from the video file and transcripts from the audio file.
- The three 2026-10-08 videos (426 MB) took about 3 min to download at the 2.5 MB/s cap
  and about 6 min to copy back.

**What was changed on the CubXL Pi (2026-10-09):** a venv at `~/.venvs/ytframes` with
`yt-dlp[default]` 2026.08.19, which includes `yt-dlp-ejs`. The downloads are kept in
`~/ytframes/atomizer/`. No sudo, nothing system-wide, no services.

## Reading them

[`video_tools.py`](video_tools.py) does three things:

```bash
pip install opencv-python-headless numpy faster-whisper imageio-ffmpeg
V=/tmp/atomizer-videos

# Find moments: one frame every 26 s, six across
python video_tools.py sheet $V/bWkP5YcsJTc.f136.mp4 sheet.jpg --end 754 --step 26

# Look at them: chosen frames or crops (t@x0,y0,x1,y1 in source pixels)
python video_tools.py frames $V/dTyuZmqYxHA.f136.mp4 view.jpg 3 99 "111@380,0,830,600"

# What was said: a Whisper transcript per audio file
python video_tools.py transcribe $V/*.f140.m4a --out-dir .
```

The phone moves the whole time, so fixed-region measurements and OCR of the panel don't
work. Tesseract on raw frames returned fragments such as `CHAMBER PRESSURE * 151 {mbar}`
and missed most readings. Panel values in the write-ups were read by eye from crops made
with `frames`, and each one gives its video time. The narration is the richest source:
operators say what they press and what the panel shows.

The commands that made every figure in a run folder are in that folder's
[`make_figures.sh`](2026-10-08/make_figures.sh).

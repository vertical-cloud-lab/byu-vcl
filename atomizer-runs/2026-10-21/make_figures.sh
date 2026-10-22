#!/usr/bin/env bash
# Rebuild the frame figures in this folder from the downloaded video (see README.md, Reproducing).
# Usage: V=/tmp/oct21 bash make_figures.sh   (needs ../video_tools.py from PR #268)
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
T="python3 -P $D/../video_tools.py"
V=${V:-/tmp/oct21}
V1=$V/p6Itg-ngMZA.f136.mp4

# Generator (Indutherm GU 500 AMA): 499 °C before the 1000 °C setpoint; 811 °C before the pour;
# 736 °C and 0.0 after it; the keypad, with the button labelled "Graining Pressure"
$T frames "$V1" "$D/gu500.jpg" --cols 2 --width 640 "1360@760,180,1020,380" "1650@520,0,760,160" \
  "1916@150,0,420,130" "1606@400,380,680,560"
# HMI: chamber pressure, furnace temperature and O2 during the 500 °C washes
$T frames "$V1" "$D/hmi_o2.jpg" --cols 1 --width 900 "1080@640,0,1130,140" "1186@640,120,1060,320" "1320@600,0,1130,120"
# The pour: what the collar phone saw (the floor mat and the stack's transducer end, not the plate)
$T frames "$V1" "$D/pour.jpg" --cols 4 --width 480 1705 1714 1728 1776
# After the run: through the front viewport, and the cylinder behind the "116 PSI" remark
$T frames "$V1" "$D/after.jpg" --cols 2 --width 640 1192 2380
python3 -P "$D/timeline.py"

# Review sheets: phone frame with the stream frame of the same instant inset. Needs stream_sync.py
# (atomizer-training/tools on PR #276) and a RUN.json naming the joined stream file (offset 0 =
# 13:03:23) and the video's file and stream_offset_s from alignment.json.
# S=stream_sync.py; R=run.json
# python3 -P $S sheet $R p6Itg-ngMZA 40 0 1160 "$D/review/v1_a.jpg"
# python3 -P $S sheet $R p6Itg-ngMZA 40 1200 2360 "$D/review/v1_b.jpg"
# The pour on the stream, every 4 s from 14:02:21 (offset 3537 s):
# ffmpeg -ss 3537 -t 264 -i stream.ts -vf "fps=1/4,crop=176:144:80:0,scale=264:216:flags=neighbor,tile=11x6" \
#   -frames:v 1 "$D/review/stream_pour_4s.jpg"

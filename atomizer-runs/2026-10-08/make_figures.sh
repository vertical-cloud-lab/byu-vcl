#!/usr/bin/env bash
# Rebuild every figure in this folder from the downloaded videos (see ../README.md).
# Usage: V=/tmp/atomizer-videos bash make_figures.sh
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
T="python3 -P $D/../video_tools.py"
V=${V:-/tmp/atomizer-videos}
P1=$V/bWkP5YcsJTc.f136.mp4   # pt1, start-up
P2=$V/dTyuZmqYxHA.f136.mp4   # pt2, the pour
S=$V/KTJzug0D0mA.f136.mp4    # results short

$T sheet "$P1" "$D/pt1_sheet_0000-1234.jpg" --start 0 --end 754 --step 26 --cols 6 --width 320
$T sheet "$P1" "$D/pt1_sheet_1300-2600.jpg" --start 780 --end 1567 --step 26 --cols 6 --width 320
$T sheet "$P2" "$D/pt2_sheet.jpg" --start 0 --end 269 --step 9 --cols 6 --width 320
$T sheet "$S" "$D/results_sheet.jpg" --start 0 --end 27.5 --step 1 --cols 7 --width 180

$T frames "$P2" "$D/pt2_viewport.jpg" --cols 2 --width 800 3 99 111 123.5 129 135
$T frames "$P2" "$D/pt2_stream_0150.jpg" --cols 6 --width 300 \
  $(for t in 110.0 110.2 110.4 110.6 110.8 111.0 111.2 111.4 111.6 111.8 112.0 112.2; do printf "%s@380,0,830,600 " $t; done)
$T frames "$P2" "$D/pt2_stream_0208.jpg" --cols 6 --width 300 \
  $(for t in 128.0 128.2 128.4 128.6 128.8 129.0 129.2 129.4 129.6 129.8 130.0 130.2; do printf "%s@430,0,880,600 " $t; done)
$T frames "$P2" "$D/pt2_ultrasonic_panel.jpg" --cols 3 --width 600 \
  "45@380,0,1280,400" "63@150,150,900,450" "76@380,0,1280,400" "79@380,0,1280,400" "81@380,0,1280,400" "86@380,0,1280,400"
$T frames "$S" "$D/results_frames.jpg" --cols 3 --width 400 5 8 10.5 16 19 24.5
$T frames "$P1" "$D/pt1_hmi_oxygen.jpg" --cols 2 --width 640 "780@380,0,1000,130" "806@300,0,760,175"
$T frames "$P1" "$D/pt1_checklist.jpg" --cols 2 --width 800 520 572
$T frames "$P2" "$D/pt2_checklist.jpg" --cols 1 --width 700 "262@0,170,470,720"

# transcript.md was built from: $T transcribe $V/*.f140.m4a --out-dir <dir> --model small.en

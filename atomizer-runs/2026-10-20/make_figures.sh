#!/usr/bin/env bash
# Rebuild the frame figures in this folder from the downloaded videos (see README.md, Reproducing).
# Usage: V=/tmp/oct20-videos bash make_figures.sh   (needs ../video_tools.py from PR #268)
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd)
T="python3 -P $D/../video_tools.py"
V=${V:-/tmp/oct20-videos}
V1=$V/7c8iHQInI_A.f136.mp4; V2=$V/vPhZTvfIu7s.f136.mp4; V3=$V/OFS_PLxoV94.f136.mp4; V4=$V/Ev9WMscAetw.f136.mp4

$T frames "$V1" "$D/v1_argon.jpg" --cols 4 --width 480 84 168 273 318
$T frames "$V3" "$D/v3_cylinders.jpg" --cols 2 --width 640 1272 1384
$T frames "$V1" "$D/v1_furnace.jpg" --cols 4 --width 480 400 425 462 714
$T frames "$V1" /tmp/o1.jpg --cols 2 --width 640 1428 1470
$T frames "$V2" /tmp/o2.jpg --cols 2 --width 640 558 630
python3 -c "import cv2, numpy as np; a=cv2.imread('/tmp/o1.jpg'); b=cv2.imread('/tmp/o2.jpg'); cv2.imwrite('$D/oring.jpg', np.vstack([a, b]), [cv2.IMWRITE_JPEG_QUALITY, 85])"
$T frames "$V3" "$D/v3_scan.jpg" --cols 1 --width 1100 "736@380,0,1280,400"
$T frames "$V4" "$D/v4_hmi.jpg" --cols 2 --width 960 156 175 182 214 227 234
python3 -P "$D/timeline.py"

# Review sheets: phone frame with the stream frame of the same instant inset. Needs stream_sync.py
# (atomizer-training/tools on PR #276) and a RUN.json naming the joined stream file (offset 0 =
# 13:24:47) and each video's file and stream_offset_s from alignment.json.
# S=stream_sync.py; R=run.json
# python3 -P $S sheet $R 7c8iHQInI_A 60 0 1440 "$D/review/v1.jpg"
# python3 -P $S sheet $R vPhZTvfIu7s 45 0 810 "$D/review/v2.jpg"
# python3 -P $S sheet $R OFS_PLxoV94 60 0 1500 "$D/review/v3.jpg"
# python3 -P $S sheet $R Ev9WMscAetw 15 0 255 "$D/review/v4.jpg"

#!/usr/bin/env bash
# Builds the talk's showreel of five agent-made system animations, plus
# slide-ready MP4s of the ones that exist only as GIFs.
#
# Every source is fetched from its own repo, pinned to the commit the
# README cites, into a scratch directory. Nothing in the sources is run.
#
#   bash make_showreel.sh [OUT_DIR]     (default: this script's directory)
#
# Needs ffmpeg with libx264 and the DejaVu fonts (apt: ffmpeg fonts-dejavu-core).
set -euo pipefail

OUT=${1:-$(cd "$(dirname "$0")" && pwd)}
SRC=$(mktemp -d /tmp/showreel-src.XXXXXX)
WORK=$(mktemp -d /tmp/showreel-work.XXXXXX)
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
BOLD=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
W=1280; H=720; BAND=64; FPS=30

RA=1b7acd55da8be50c393b5cdb7a56f99e75d3ab50     # robot-arms PR 10, wrist camera mount
SWAP=26789139fbe9f7a6972af7788d23f7a29dd67abd   # robot-arms PR 44, auger swap
OT2=49677cfff31a67765d9182c01765bfa994a7545d    # byu-vcl PR 234, OT-2 lid camera
DAL=01e8ad3827c254b4eaaee208c72bc079387d41ab    # digital-alloy-lab PR 264, CubXL copper screen
VLM=b8b74f5c514eef09ea33aa28268128bc67b7932c    # byu-vcl PR 329, vertical lab

fetch() {  # repo sha path dest
  curl -fsSL "https://raw.githubusercontent.com/vertical-cloud-lab/$1/$2/$3" -o "$SRC/$4"
}
fetch robot-arms "$RA" piper-camera-mount/renders/assembly_steps.gif cam.gif
fetch robot-arms "$SWAP" end-effectors/auger-swap/renders/s1.gif swap_s1.gif
fetch robot-arms "$SWAP" end-effectors/auger-swap/renders/alt_a_cf.gif swap_alt_a_cf.gif
fetch byu-vcl "$OT2" ot2-overhead-camera/lid-mount/renders/setup_steps.mp4 ot2.mp4
fetch byu-vcl "$OT2" ot2-overhead-camera/lid-mount/renders/lid_camera_plate.jpg ot2_real.jpg
fetch digital-alloy-lab "$DAL" alloy-corrosion/copper/cubxl-cu-spot.mp4 cubxl.mp4
fetch digital-alloy-lab "$DAL" alloy-corrosion/copper/media/cubxl-empty-ben-2026-06-26.jpg cubxl_real.jpg
fetch byu-vcl "$VLM" vertical-lab/out/mp4/org_vertical_lab_readme_1280.mp4 vlm.mp4

esc() { printf '%s' "$1" | sed -e 's/:/\\:/g' -e 's/%/\\%/g'; }  # titles must not contain quotes

# Dark title band over the clip: "n/5  Title" on the left, the source on the right.
band() {  # n title source
  local t s
  t=$(esc "$1/5   $2"); s=$(esc "$3")
  printf "pad=%d:%d:0:%d:color=0x1f2933,drawtext=fontfile=%s:text='%s':x=24:y=(%d-th)/2:fontsize=30:fontcolor=white,drawtext=fontfile=%s:text='%s':x=w-tw-24:y=(%d-th)/2:fontsize=20:fontcolor=0xc8d1da" \
    "$W" "$H" "$BAND" "$BOLD" "$t" "$BAND" "$FONT" "$s" "$BAND"
}
fit() {  # scale into the area under the band, letterboxed on white
  printf "scale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1" \
    "$W" "$((H - BAND))" "$W" "$((H - BAND))"
}
enc=(-c:v libx264 -preset slow -crf 22 -pix_fmt yuv420p -r "$FPS" -an)

# segment: n title source input start src_seconds out_seconds
segment() {
  local n=$1 title=$2 source=$3 in=$4 ss=$5 len=$6 out=$7
  local speed
  speed=$(awk -v a="$len" -v b="$out" 'BEGIN{printf "%.4f", a/b}')
  ffmpeg -v error -y -ss "$ss" -t "$len" -i "$SRC/$in" \
    -vf "setpts=PTS/$speed,fps=$FPS,$(fit),$(band "$n" "$title" "$source")" \
    -t "$out" "${enc[@]}" "$WORK/seg$n.mp4"
}
# still: n title source image seconds caption
still() {
  local n=$1 title=$2 source=$3 img=$4 secs=$5 cap
  cap=$(esc "$6")
  ffmpeg -v error -y -loop 1 -t "$secs" -i "$SRC/$img" \
    -vf "fps=$FPS,$(fit),drawtext=fontfile=$BOLD:text='$cap':x=(w-tw)/2:y=h-th-28:fontsize=28:fontcolor=white:box=1:boxcolor=0x1f2933@0.85:boxborderw=12,$(band "$n" "$title" "$source")" \
    "${enc[@]}" "$WORK/seg${n}b.mp4"
}

segment 1 "A wrist camera mount for the robot arm" "robot-arms PR 10" cam.gif 0 51.6 12
segment 2 "An overhead camera for the OT-2" "byu-vcl PR 234" ot2.mp4 0 94 12
still   2 "An overhead camera for the OT-2" "byu-vcl PR 234" ot2_real.jpg 3 "The real camera, looking down at the deck"
segment 3 "The robot arm swaps an auger in the powder doser" "robot-arms PR 44" swap_s1.gif 0 25.9 12
segment 4 "A copper corrosion screen on the CubXL" "digital-alloy-lab PR 264" cubxl.mp4 62 62 14
still   4 "A copper corrosion screen on the CubXL" "digital-alloy-lab PR 264" cubxl_real.jpg 3 "The real CubXL, before the modules"
segment 5 "A vertical lab: the equipment comes to the arm" "byu-vcl PR 329" vlm.mp4 0 100.8 18

: > "$WORK/list.txt"
for s in seg1 seg2 seg2b seg3 seg4 seg4b seg5; do echo "file '$WORK/$s.mp4'" >> "$WORK/list.txt"; done
ffmpeg -v error -y -f concat -safe 0 -i "$WORK/list.txt" -c copy -movflags +faststart "$OUT/showreel.mp4"

# A small GIF of the same reel, for GitHub pages and comments.
ffmpeg -v error -y -i "$OUT/showreel.mp4" \
  -vf "fps=8,scale=560:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" \
  -loop 0 "$OUT/showreel.gif"

# One still per system, for a static slide or a handout.
ffmpeg -v error -y \
  -ss 30 -i "$SRC/cam.gif" -ss 40 -i "$SRC/ot2.mp4" -ss 12 -i "$SRC/swap_s1.gif" \
  -ss 70 -i "$SRC/cubxl.mp4" -ss 20 -i "$SRC/vlm.mp4" -i "$SRC/ot2_real.jpg" \
  -filter_complex "\
[0]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:white,setsar=1[a];\
[1]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:white,setsar=1[b];\
[2]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:white,setsar=1[c];\
[3]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:white,setsar=1[d];\
[4]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:white,setsar=1[e];\
[5]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2:white,setsar=1[f];\
[a][b][c]hstack=3[top];[d][e][f]hstack=3[bot];[top][bot]vstack=2" \
  -frames:v 1 "$OUT/systems_sheet.png"

# Slide-ready MP4s of the clips that exist only as GIFs.
for g in cam swap_s1 swap_alt_a_cf; do
  ffmpeg -v error -y -i "$SRC/$g.gif" \
    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=$FPS" -movflags +faststart \
    -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -an "$OUT/$g.mp4"
done
mv "$OUT/cam.mp4" "$OUT/wrist_camera_mount_assembly.mp4"
mv "$OUT/swap_s1.mp4" "$OUT/auger_swap_strategy1.mp4"
mv "$OUT/swap_alt_a_cf.mp4" "$OUT/auger_swap_custom_fingers.mp4"

rm -rf "$SRC" "$WORK"
ls -la "$OUT"

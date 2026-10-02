#!/bin/bash
# cap.sh <tag>: one still from each ribbon camera, sequentially, nothing else.
# Camera 0 = CAM/DISP 0 (csi0), camera 1 = CAM/DISP 1 (csi1). If camera 0 is
# busy because someone has the deckcam live view open (deckcam uses camera 0),
# fall back to deckcam's own /snapshot.jpg rather than interrupting the viewer.
tag="$1"; out=/tmp/jog_20261002; mkdir -p "$out"
for idx in 0 1; do
  f="$out/${tag}__cam${idx}_csi${idx}.jpg"
  t0=$(date -u +%H:%M:%S)
  if LIBCAMERA_LOG_LEVELS="*:ERROR" timeout 30 rpicam-still --camera $idx -n -t 3000 \
       --width 2304 --height 1296 --metadata "${f%.jpg}.json" -o "$f" >/dev/null 2>"$out/err.txt"; then
    echo "$tag cam$idx ok ${t0}Z $(stat -c %s "$f") bytes"
  else
    echo "$tag cam$idx rpicam-still FAILED ${t0}Z: $(tail -2 "$out/err.txt" | tr '\n' ' ')"
    if [ $idx = 0 ] && curl -sf -m 20 -o "$f" http://127.0.0.1:8743/snapshot.jpg; then
      echo "$tag cam0 via deckcam snapshot $(stat -c %s "$f") bytes"
    fi
  fi
done

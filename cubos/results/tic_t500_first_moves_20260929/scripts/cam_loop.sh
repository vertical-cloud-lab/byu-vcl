#!/bin/bash
# Stills from cam0 for N seconds, each file named by lab-local time.
cd "$2" || exit 1
end=$(( $(date +%s) + ${1:-40} ))
while [ "$(date +%s)" -lt "$end" ]; do
  timeout 15 rpicam-still --camera 0 --width 1536 --height 864 --nopreview --immediate \
    -o "cam0_$(date +%H%M%S).jpg" >/dev/null 2>&1
done

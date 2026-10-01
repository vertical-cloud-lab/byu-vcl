#!/bin/bash
# Run as root (sudo). Camera stills while the Tic steps the motor itself.
set -u
TAG=$1; SECS=$2
U=${SUDO_USER}; OUT=/tmp/tic_run/$TAG
sudo -u "$U" mkdir -p "$OUT"; chmod 777 "$OUT"
sudo -u "$U" bash /tmp/tic_run/cam_loop.sh "$SECS" "$OUT" < /dev/null &
P2=$!
sleep 1.5
python3 /tmp/tic_run/tic_usb_moves.py "$OUT" < /dev/null
wait $P2
chmod 644 "$OUT"/*; chmod 755 "$OUT"
echo "=== frames"; ls "$OUT" | grep jpg | tr '\n' ' '; echo

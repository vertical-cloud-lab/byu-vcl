#!/bin/bash
# Run as root (sudo): polls the Tic and takes stills while the Arduino steps.
# Usage: sudo bash run_moves.sh TAG SECONDS move [move ...]   (move = code,dir,steps,rate)
set -u
TAG=$1; SECS=$2; shift 2
OUT=/tmp/tic_run/$TAG; sudo -u "$SUDO_USER" mkdir -p "$OUT"
U=${SUDO_USER}
bash /tmp/tic_run/tic_poll.sh "$SECS" > "$OUT/tic_poll.log" 2>&1 < /dev/null &
P1=$!
sudo -u "$U" bash /tmp/tic_run/cam_loop.sh "$SECS" "$OUT" < /dev/null &
P2=$!
sleep 1.5
sudo -u "$U" env PYTHONDONTWRITEBYTECODE=1 /home/$U/CubOS/.venv/bin/python \
  /tmp/tic_run/arduino_moves.py "$@" < /dev/null 2>&1 | tee "$OUT/arduino_moves.log"
wait $P1 $P2
chmod 644 "$OUT"/*
echo "=== tic poll"; cat "$OUT/tic_poll.log"
echo "=== frames"; ls "$OUT" | grep jpg | tr '\n' ' '; echo

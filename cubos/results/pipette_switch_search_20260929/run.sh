#!/bin/bash
# Run as root (sudo): poll the Tic while switch_search.py drives the plunger.
set -u
OUT=/tmp/switch_search; U=${SUDO_USER}
TIC=/home/$U/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd
rm -f "$OUT/.stop"
$TIC --status --full > "$OUT/tic_status_before_${SCRIPT:-switch_search}.txt" 2>&1
bash "$OUT/tic_poll.sh" "$OUT" > "$OUT/tic_poll_${SCRIPT:-switch_search}.log" 2>&1 < /dev/null &
P=$!
sudo -u "$U" env PYTHONDONTWRITEBYTECODE=1 /home/$U/CubOS/.venv/bin/python \
  "$OUT/${SCRIPT:-switch_search}.py" "$@" < /dev/null 2>&1 | tee "$OUT/${SCRIPT:-switch_search}.log"
touch "$OUT/.stop"; wait $P
$TIC --status --full > "$OUT/tic_status_after_${SCRIPT:-switch_search}.txt" 2>&1
chmod 644 "$OUT"/*.log "$OUT"/*.txt

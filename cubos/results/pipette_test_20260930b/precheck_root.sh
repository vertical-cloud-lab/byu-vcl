#!/bin/bash
# Run as root (sudo). Tic: is it energized, and do BOTH coils draw current?
# Compares VIN energized vs de-energized (the 12 V brick is soft, so the sag is
# a proxy for coil current). No step pulses are sent; the motor does not move.
set -u
U=${SUDO_USER}; H=/home/$U; OUT=/tmp/run_20260930b
TIC=$H/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd
ts(){ date -u +%H:%M:%S.%3NZ; }
row(){ s=$($TIC --status 2>&1); printf '%s  energized=%-3s VIN=%s  stopping=%s\n' "$(ts)" \
  "$(grep -m1 'Energized' <<<"$s" | awk '{print $2}')" \
  "$(grep -m1 'VIN voltage' <<<"$s" | awk '{print $3}')" \
  "$(grep -m1 -A1 'Errors currently stopping' <<<"$s" | head -1 | cut -d: -f2 | xargs)"; }
$TIC --status --full > $OUT/tic_status_before_run.txt 2>&1
echo "-- as found (energized)"; for i in 1 2 3 4 5; do row; sleep 0.4; done
$TIC --deenergize; sleep 1.5
echo "-- de-energized";        for i in 1 2 3 4 5; do row; sleep 0.4; done
$TIC --energize; sleep 1.5
echo "-- re-energized";        for i in 1 2 3 4 5; do row; sleep 0.4; done
$TIC --status --full > $OUT/tic_status_energized.txt 2>&1
chmod 644 $OUT/*.txt

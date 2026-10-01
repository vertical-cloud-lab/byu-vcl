#!/bin/bash
# Run as root. No motion: releases and restores the Tic's holding current while
# sampling VIN, to see whether the driver is really loading the 12 V supply.
TIC=${TIC:-/home/${SUDO_USER}/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd}
sample() { for i in 1 2 3 4 5 6; do
  s=$($TIC --status); printf '%s  %-14s VIN=%s  energized=%s  errors_now=%s\n' "$(date +%H:%M:%S.%3N)" "$1" \
   "$(grep -m1 'VIN voltage' <<<"$s" | awk '{print $3}')" "$(grep -m1 Energized <<<"$s" | awk '{print $2}')" \
   "$(grep -m1 -A1 'Errors currently stopping' <<<"$s" | tail -1 | xargs)"; sleep 0.5; done; }
sample energized
$TIC --deenergize && echo "$(date +%H:%M:%S.%3N)  --deenergize sent"; sleep 1
sample de-energized
$TIC --current 343 && $TIC --energize && echo "$(date +%H:%M:%S.%3N)  --current 343 + --energize sent"; sleep 1
sample 343mA
$TIC --current 990 && echo "$(date +%H:%M:%S.%3N)  --current 990 sent"; sleep 1
sample 990mA

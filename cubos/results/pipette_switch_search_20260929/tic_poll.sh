#!/bin/bash
# Run as root. Poll the Tic's live state until $1/.stop exists.
TIC=/home/${SUDO_USER}/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd
while [ ! -f "$1/.stop" ]; do
  s=$($TIC --status 2>&1)
  printf '%s  VIN=%s  energized=%s  state=%s  errors_now=%s\n' "$(date +%H:%M:%S.%3N)" \
    "$(grep -m1 'VIN voltage' <<<"$s" | awk '{print $3}')" \
    "$(grep -m1 'Energized' <<<"$s" | awk '{print $2}')" \
    "$(grep -m1 'Operation state' <<<"$s" | cut -d: -f2 | xargs)" \
    "$(grep -m1 -A1 'Errors currently stopping' <<<"$s" | tail -1 | xargs)"
  sleep 0.4
done

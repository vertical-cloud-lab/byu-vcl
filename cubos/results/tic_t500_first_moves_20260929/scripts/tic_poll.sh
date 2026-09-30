#!/bin/bash
# Poll the Tic's live state while something else drives STEP/DIR. Run as root.
TIC=${TIC:-/home/${SUDO_USER:-$USER}/.local/opt/pololu-tic-1.8.1-linux-rpi/ticcmd}
end=$(( $(date +%s) + ${1:-40} ))
while [ "$(date +%s)" -lt "$end" ]; do
  s=$($TIC --status 2>&1)
  printf '%s  VIN=%s  energized=%s  state=%s  errors_now=%s\n' "$(date +%H:%M:%S.%3N)" \
    "$(grep -m1 'VIN voltage' <<<"$s" | awk '{print $3}')" \
    "$(grep -m1 'Energized' <<<"$s" | awk '{print $2}')" \
    "$(grep -m1 'Operation state' <<<"$s" | cut -d: -f2 | xargs)" \
    "$(grep -m1 -A3 'Errors currently stopping' <<<"$s" | head -1 | cut -d: -f2 | xargs)"
  sleep 0.4
done

#!/bin/bash
# Run as the Pi user. Firmware verify (read-only), plunger HOME, GRBL snapshot.
set -u
OUT=/tmp/run_20260930b; PY=~/CubOS/.venv/bin/python
PORT=/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
verify() {
  if "$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D -q -q -U "flash:v:$2:i" >/tmp/v.out 2>&1; then
    echo "  $1 : MATCH  $(grep -o '[0-9]* bytes of flash verified' /tmp/v.out)"
  else
    echo "  $1 : no     $(grep -oE 'verification (error|mismatch)[^;]*' /tmp/v.out | head -1)"
  fi
}
echo "== which image is on the board (avrdude -U flash:v:, read-only) $(date -u +%TZ)"
verify panda_vcl_p20gen2_tic796_20260930 $OUT/panda_vcl_p20gen2_tic796_20260930.hex
verify panda_vcl_p20gen2_20260917        $OUT/panda_vcl_p20gen2_20260917.hex
sleep 2
echo; echo "== plunger (PawduinoLink, as CubOS talks to it)"
cd ~/CubOS && PYTHONDONTWRITEBYTECODE=1 $PY $OUT/precheck_arduino.py < /dev/null 2>&1
echo; echo "== GRBL, read-only $(date -u +%TZ)"
PYTHONDONTWRITEBYTECODE=1 $PY $OUT/grbl_read.py < /dev/null 2>&1

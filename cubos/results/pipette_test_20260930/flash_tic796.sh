#!/bin/bash
# Flash the STEPS_PER_MM 796 image (Tic T500, 1/8 step), verify before and after.
set -u
PORT=/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
FW=~/byu-vcl/cubos/firmware
NEW=/tmp/panda_vcl_p20gen2_tic796.hex
verify() {  # $1 label, $2 hex
  if "$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D -q -q -U "flash:v:$2:i" >/tmp/v.out 2>&1; then
    echo "  $1 : MATCH  $(grep -o '[0-9]* bytes of flash verified' /tmp/v.out)"
  else
    echo "  $1 : no     $(grep -oE 'verification (error|mismatch)[^;]*' /tmp/v.out | head -1)"
  fi
}
echo "Firmware: flashing panda_vcl_p20gen2_tic796_20260930.hex -- $(date -u +%FT%TZ)"
echo; echo "sha256:"; sha256sum "$NEW" "$FW/panda_vcl_p20gen2_20260917.hex"
echo; echo "=== which image is on the board BEFORE (avrdude -U flash:v:, read-only) ==="
verify panda_vcl_p20gen2_20260917 "$FW/panda_vcl_p20gen2_20260917.hex"
verify panda_vcl_p20gen2_tic796   "$NEW"
echo; echo "=== FLASH ==="
"$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D -U "flash:w:$NEW:i" 2>&1 | grep -E 'Writing|Reading|verified|error|mismatch|done'
echo; echo "=== which image is on the board AFTER ==="
verify panda_vcl_p20gen2_tic796   "$NEW"
verify panda_vcl_p20gen2_20260917 "$FW/panda_vcl_p20gen2_20260917.hex"

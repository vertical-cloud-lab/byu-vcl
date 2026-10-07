#!/bin/bash
# Flash fix B (spreadCycle), backing up and verifying before and after.
# Same avrdude call as ../pipette_test_20260930/flash_tic796.sh.
set -u
PORT=/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
OLD=$1   # panda_vcl_p20gen2_tic796_fastmove_20261001.hex
NEW=$2   # the fix B image
verify() {  # $1 label, $2 hex
  if "$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D -q -q -U "flash:v:$2:i" >/tmp/v.out 2>&1; then
    echo "  $1 : MATCH"
  else
    echo "  $1 : no     $(grep -oE 'verification (error|mismatch)[^;]*' /tmp/v.out | head -1)"
  fi
}
echo "Firmware: flashing fix B (spreadCycle) -- $(date -u +%FT%TZ)"
echo; echo "sha256:"; sha256sum "$OLD" "$NEW"
echo; echo "=== backup of the flash as it is (avrdude -U flash:r) ==="
"$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D -q -q -U "flash:r:flash_before_20261007.hex:i" && sha256sum flash_before_20261007.hex
echo; echo "=== which image is on the board BEFORE ==="
verify fastmove_20261001 "$OLD"
verify spreadcycle       "$NEW"
echo; echo "=== FLASH ==="
"$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D -U "flash:w:$NEW:i" 2>&1 | grep -E 'Writing|Reading|verified|error|mismatch|done'
echo; echo "=== which image is on the board AFTER ==="
verify spreadcycle       "$NEW"
verify fastmove_20261001 "$OLD"

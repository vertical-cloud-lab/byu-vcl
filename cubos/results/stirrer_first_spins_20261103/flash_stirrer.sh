#!/bin/bash
# Flash the stirrer image onto the CubXL's Uno, 2026-11-03.
# Same avrdude calls as ../tmc2209_spreadcycle_20261007/flash_spreadcycle.sh and BUILD.md stage 7:
# back up the flash, confirm the board is on the 10-07 image, and only then write.
set -u
PORT=/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
FW=~/byu-vcl-pipette/cubos/firmware
OLD=$FW/panda_vcl_p20gen2_tic796_fastmove_spread_20261007.hex
NEW=$FW/panda_vcl_p20gen2_tic796_fastmove_spread_stir_20261019.hex
AVR=("$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P "$PORT" -b 115200 -D)
verify() {  # $1 label, $2 hex; returns 0 on a match
  if "${AVR[@]}" -q -q -U "flash:v:$2:i" >/tmp/v.out 2>&1; then
    echo "  $1 : MATCH"; return 0
  else
    echo "  $1 : no     $(grep -oE 'verification (error|mismatch)[^;]*|first mismatch[^;]*' /tmp/v.out | head -1)"; return 1
  fi
}
echo "Stirrer firmware flash -- $(date -u +%FT%TZ)"
echo; echo "port -> $(readlink -f "$PORT")"
echo; echo "nothing holding the port:"; fuser -v "$(readlink -f "$PORT")" 2>&1 || echo "  (none)"
echo; echo "sha256:"; sha256sum "$OLD" "$NEW"
echo; echo "=== backup of the flash as it is (avrdude -U flash:r) ==="
"${AVR[@]}" -q -q -U "flash:r:flash_before_stirrer_20261103.hex:i" || { echo "BACKUP FAILED: nothing written"; exit 1; }
sha256sum flash_before_stirrer_20261103.hex
echo; echo "=== which image is on the board BEFORE ==="
verify spread_20261007 "$OLD"; ON_OLD=$?
verify stir_20261019   "$NEW"
if [ "$ON_OLD" -ne 0 ]; then echo; echo "NOT on the 10-07 image: nothing written"; exit 2; fi
echo; echo "=== FLASH $(date -u +%FT%TZ) ==="
"${AVR[@]}" -U "flash:w:$NEW:i" 2>&1 | grep -E 'Writing|Reading|verified|error|mismatch|done|bytes'
echo; echo "=== which image is on the board AFTER $(date -u +%FT%TZ) ==="
verify stir_20261019   "$NEW"
verify spread_20261007 "$OLD"
echo; echo "done $(date -u +%FT%TZ)"

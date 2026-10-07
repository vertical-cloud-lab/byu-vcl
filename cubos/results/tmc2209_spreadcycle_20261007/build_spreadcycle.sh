#!/bin/bash
# Build fix B: the 10-01 image with spreadCycle instead of StealthChop.
# Copies ~/panda_fw_vcl_tic796_fast, proves a clean rebuild of the copy still
# gives the flashed 10-01 image, then changes the one line and rebuilds.
set -eu
SRC=~/panda_fw_vcl_tic796_fast
DST=~/panda_fw_vcl_tic796_fast_spread
PIO=~/.venvs/pio/bin/pio
WANT=6d2dc97741a4e5ee0f05b8c7d7ba7254c1e04b6e1f77438eb714d2af7223437f  # panda_vcl_p20gen2_tic796_fastmove_20261001.hex
HEX=.pio/build/uno/firmware.hex
echo "build: $(date -u +%FT%TZ)"
test ! -e "$DST"
cp -a "$SRC" "$DST"
cd "$DST"
"$PIO" run -e uno -t clean >/dev/null
"$PIO" run -e uno 2>&1 | grep -E '^(RAM|Flash):|SUCCESS|ERROR|error'
echo "unchanged rebuild: $(sha256sum $HEX | cut -c1-64)"
[ "$(sha256sum $HEX | cut -c1-64)" = "$WANT" ] && echo "  = the 10-01 image" || { echo "  differs from the 10-01 image, stopping"; exit 1; }
sed -i 's|^    stepperDriver.enableStealthChop();$|    stepperDriver.disableStealthChop(); // [VCL] spreadCycle: initialize() turns pwm_autoscale off, and StealthChop without it does not regulate current to IRUN/IHOLD|' src/Pipette.cpp
diff -u "$SRC/src/Pipette.cpp" src/Pipette.cpp || true
"$PIO" run -e uno 2>&1 | grep -E '^(RAM|Flash):|SUCCESS|ERROR|error'
echo "fix B: $(sha256sum $HEX | cut -c1-64)"

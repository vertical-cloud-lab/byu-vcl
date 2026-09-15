# PANDA Arduino firmware — the VCL build

The Arduino Uno on `/dev/ttyACM0` runs **one** firmware that serves the
capper, the line-break sensor, the lights *and* the pipette plunger. Anything
flashed here affects the capper too, so nothing in this directory should be
applied casually.

Upstream: [`BU-KABlab/PANDA_Arduino`](https://github.com/BU-KABlab/PANDA_Arduino)
@ `228615b` ("fixed mixing function for pipette", 2025-08-27).

## What is on the board (2026-09-15)

| file | what it is |
| --- | --- |
| `flash_20260915T220346Z.hex` | **Backup of the flash as it was before this change.** Read with `avrdude -U flash:r:...:i` at 2026-09-15 22:03 UTC. Restores the board exactly. |
| `panda-arduino-p20-and-driver-status.patch` | The VCL delta against upstream `228615b`. Four files, +112/-7. |
| `panda_vcl_p20_20260915.hex` | The image actually flashed, built on the Pi from that patch. |

**The backup proved the provenance.** Parsed and compared byte-for-byte, the
16 308 program bytes read off the board were **identical** to a local build of
upstream `228615b` — so the board really was running stock upstream, and the
VCL image is a provably minimal delta from it.

`panda_vcl_p20_20260915.hex` is the exact 17 370-byte image that was written and
verified by avrdude. A rebuild reproduced it bit-for-bit in one environment, but
**the build is not reproducible in general**: `platformio.ini` pins its library
dependencies with `^` ranges, so a clone that resolves a different minor version
builds a slightly different image (17 364 bytes in one such case). Flash the
committed hex if you want exactly what was on the board; rebuild from the patch
if you want the source of truth.

## Upstream `main` does not compile

`228615b` gives a default argument for `dwell_ms` in **both** the declaration
in `include/Pipette.h` and the definition in `src/Pipette.cpp`, which is a hard
C++ error:

```
src/Pipette.cpp:355:86: error: default argument given for parameter 4 of
  'bool mixInPlace(int, float, float, float)'
```

The patch drops the duplicate from the definition; the header keeps it, so the
default is unchanged. Worth sending upstream — as it stands nobody can build
`main`.

## What changed, and why

### Pipette constants — it was configured as a P300

The pipette on the head is a **P20 GEN2** (legible on the body in
`../results/pi5_des4_provision_20260914/pipette_label_p20_gen2.jpg`).

| constant | was | now | why |
| --- | --- | --- | --- |
| `MAX_VOLUME` | 300.0 | **20.0** | P300 value. `STATUS` reported `max_vol: 300.00` for months. |
| `MIN_VOLUME` | 5.0 | **1.0** | P300 value. This clamp is why `ASPIRATE 0.5` always landed at 35.45: 0.5 clamped up to 5. |
| `UL_TO_MM` | 0.1098 | **1.8** | 0.1098 is the P300 calibration. 1.8 = `PRIME_POSITION` 36.0 / 20 µL, so a full-scale 20 µL aspirate lands the plunger at 0.0. **A starting estimate, not a calibration** — it needs a gravimetric check. |
| `RUN_CURRENT_PERCENT` | 50 | **17** | ~1.25 A peak against a motor science-jubilee specs at **500 mA peak** for a Gen2 OT-2 pipette (`M906 V500`) — about 2.5× its rating. |
| `HOLD_CURRENT_PERCENT` | 30 | **10** | Not asked for, but forced: the TMC2209 library maps hold 0-100 → IHOLD 0-31 **independently** of run current, so leaving 30 against a run of 17 would draw more current standing still than moving. 10 keeps the original 0.6 hold/run ratio. |

`PRIME_POSITION` 36.0, `BLOWOUT_POSITION` 44.0 and `DROP_TIP_POSITION` 55.0 are
**unchanged** — they are mechanical plunger positions, and `UL_TO_MM` 1.8 is
derived from `PRIME_POSITION`, so moving one means re-deriving the other.
They may still be P300 figures; a P20's usable travel is shorter, and
`DROP_TIP_POSITION` 55.0 in particular is worth checking against the real
plunger before anything relies on the ejector.

### New: `CMD_PIPETTE_DRIVER_STATUS = 29`

Ben bridged `RX_PIN` (A0) to `TX_PIN` (A1) with 10 kΩ on 2026-09-15, which is
what makes a TMC2209 read possible — PDN_UART is half duplex, so the driver
answers on the wire it was addressed on, and without the bridge the Arduino
could only ever talk.

Before this, `setupMotor()` wrote six registers and checked none of them, and
no command exposed driver state. A driver sitting at minimum current with its
output stage off was indistinguishable, at the serial port, from a healthy one.

```
OK:{"msg":"Driver status","v":[<comm>,<flags>,<current_scaling>]}
```

* `comm` — `0` no reply at all · `1` communicating but not set up (driver power
  was lost after `setup()`, so defaults reloaded) · `2` set up and communicating
* `flags` — bitmask, `DRVSTATUS_*` in `include/Pipette.h`: over-temperature
  warning/shutdown, short-to-ground A/B, low-side short A/B, **open-load A/B**,
  the 120/143/150/157 °C flags, stealthChop, standstill, hardware-disabled
* `current_scaling` — the driver's actual CS value, 0-31, or `-1` if unread

`open_load_a`/`open_load_b` answer the coil-continuity question without a
meter. Read it with CubOS's own link:

```python
from cubos.instruments.controllers.pawduino import PawduinoLink
link = PawduinoLink.acquire("/dev/ttyACM0", 115200); link.connect()
print(link.send_command(29, timeout=15))
```

## Rebuild / reflash / restore

PlatformIO lives in a user venv on the Pi (`~/.venvs/pio`), toolchain under
`~/.platformio` — no sudo, nothing system-wide.

```bash
git clone https://github.com/BU-KABlab/PANDA_Arduino.git ~/panda_fw_vcl
cd ~/panda_fw_vcl && git checkout 228615b
git apply ~/byu-vcl/cubos/firmware/panda-arduino-p20-and-driver-status.patch
~/.venvs/pio/bin/pio run -e uno -t upload --upload-port /dev/ttyACM0
```

To put the board back exactly as it was:

```bash
AVRDUDE=~/.platformio/packages/tool-avrdude/avrdude
CONF=$(find ~/.platformio -name avrdude.conf | head -1)
"$AVRDUDE" -C "$CONF" -c arduino -p atmega328p -P /dev/ttyACM0 -b 115200 -D \
    -U flash:w:~/byu-vcl/cubos/firmware/flash_20260915T220346Z.hex:i
```

Close every serial handle first — CubOS holds `/dev/ttyACM0` for the whole of a
run, and opening the port resets the board.

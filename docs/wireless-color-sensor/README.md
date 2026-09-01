# Wireless color sensor — diagnosing "it isn't reading color"

Fault-localizing diagnostic for the AS7341 sensor package
([issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33)),
built against the reference firmware at
[AccelerationConsortium/wireless-color-sensor](https://github.com/AccelerationConsortium/wireless-color-sensor).

## Run it

Copy `as7341_diagnose.py` onto the Pico W and run it **on the board** (Thonny, or
the MicroPico "run" button in VS Code — not your laptop's Python):

```python
>>> import as7341_diagnose
```

It needs no credentials, no network, and nothing from `lib/`. It talks raw I²C to
the AS7341 on purpose, so a missing or half-copied `as7341*.py` shows up as a
finding rather than hiding the real state of the hardware.

`ImportError: no module named 'machine'` means you are in desktop Python — the
board is disconnected and the editor fell back to the local interpreter.

## What each stage answers

| Stage | Question | A failure here means |
| --- | --- | --- |
| 0 | Which MicroPython build is flashed? | Non-W `.uf2` → no `network`, no `ssl` |
| 1 | Is anything at 0x39, and on which pins? | Cable, power, or wrong bus |
| 2 | Is it really an AS7341? | Bus noise, or a different chip |
| 3 | Can it complete a conversion? | Chip powered but not integrating |
| 4 | Does it respond to light? | The decisive one — see below |
| 5 | Does it discriminate *hue*, not just brightness? | Manual check |

Stage 4 is the one that separates "broken" from "working but in the dark." It
reads with the LED off, then at 4 mA and 10 mA, and compares. A sensor whose
counts jump with the LED is fine; the problem is upstream in whatever was
supposed to illuminate the sample.

## Traps that look like a dead sensor

1. **Nothing turns the light on.** In the reference `sensor_file/main.py`,
   `read_sensor_data()` has `# sensor.LED = True` commented out and
   `run_color_experiment()` has `# set_color(R, Y, B)` commented out. Sealed in
   the 3D-printed housing there is no light to measure, and every channel reads
   near zero — correctly.
2. **`Sensor()` defaults to the wrong pins.** The signature is
   `def __init__(self, atime=200, astep=999, gain=128, i2c=I2C(1, scl=Pin(27), sda=Pin(26)))`.
   The Proto Under Plate's STEMMA QT connector is wired to **GP4/GP5**, so a bare
   `Sensor()` raises `ExternalDeviceNotFound`. Always pass
   `Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)))`. That default is also evaluated at
   *import* time, so importing the module claims GP26/GP27 either way.
3. **`sensor.LED` raises before it is set.** `Sensor.__init__` never assigns
   `self._led_state`, so *reading* the property before writing it raises
   `AttributeError`.
4. **Missing `lib/` files.** `as7341.py` does `from as7341_smux_select import *`.
   All three of `as7341.py`, `as7341_sensor.py`, `as7341_smux_select.py` must be
   in `/lib` on the board.
5. **Wrong firmware.** A REPL banner reading `Raspberry Pi Pico with RP2040` —
   without the **W** — is the non-W build: no WiFi, no `ssl`, no `ussl`.
   Reflash from <https://micropython.org/download/RPI_PICO_W/>. If the `RPI-RP2`
   drive never mounts, try a different USB cable first; charge-only micro-USB
   cables are common.

## Testing

The diagnostic was exercised against a register-level AS7341 simulator across six
scenarios — healthy, non-W firmware, sensor on GP26/GP27, nothing on the bus, LED
with no effect, and saturation — and each failure branch reports the correct
cause. The simulator is a test fixture, not hardware validation: stages 0–5 have
not yet been run against the physical sensor.

# Pico W firmware change: gain and integration time per reading

The colour sensor's board runs upstream
[`AccelerationConsortium/wireless-color-sensor`](https://github.com/AccelerationConsortium/wireless-color-sensor)
`sensor_file/`. Its `main.py` reads the AS7341 at fixed settings and ignores
everything in a read command but `experiment_id`, so gain and integration time
cannot be changed over MQTT. This directory changes that, without changing any
reading that doesn't ask for it.

| file | what |
| --- | --- |
| [`sensor_settings.py`](sensor_settings.py) | new module for the board: parses, applies and reports per-reading settings |
| [`main.py.patch`](main.py.patch) | three small edits to upstream `sensor_file/main.py` at `07efedd` |
| [`test_sensor_settings.py`](test_sensor_settings.py) | 29 checks: the module against a fake AS7341, then upstream `main.py` fetched, patched and its message handler driven with fake MQTT messages |

After flashing, a command may carry `settings`; any key left out keeps its default:

```json
{"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": "...",
 "settings": {"gain": 512, "atime": 200, "astep": 999}}
```

- **gain** 0.5, 1, 2, 4, … 512 · **atime** 0–255 · **astep** 0–65534. Integration per
  half-reading is (atime + 1) × (astep + 1) × 2.78 µs; a reading is two halves.
- The defaults are put back straight after that one reading, so commands without
  `settings` read exactly as before.
- Every reply gains `sensor_settings`: what was used, the gain code the chip itself
  latched with the counts (ASTATUS), and whether either half saturated.
- Bad settings get an `error` reply and no reading.
- Host side: `sensor_read.SensorLink.read(settings={...})`. It refuses a reply without
  `sensor_settings`, so a board still on the old firmware can't silently read at the
  default while the data says otherwise.

**The default gain is 256x, not 128x, on purpose.** Upstream `Sensor()` passes its gain
*factor* (128) to `as7341.set_again()`, which wants a *code* (0–10) and ignores anything
out of range, so the chip has always stayed at its power-on code 9 = 256x (DS000504,
CFG1 0xAA). The patch sets 256x explicitly, so new readings stay comparable with every
old one.

## Flashing it (one USB visit)

1. **Plug the Pico W's USB into the Pi that holds the robot link**
   (`RPI_STREAM_CAM_HOSTNAME`). This may mean opening the enclosure.
2. Address the board **by its USB serial only** — an Arduino can own `/dev/ttyACM0`
   on that Pi, and bare `mpremote` grabs the first ACM device:

   ```bash
   M="$HOME/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438"
   $M fs ls
   ```
3. **Back up what is on the board first** (it may not be exactly upstream; a
   2026-09-03 backup in `~/pico-backups/` had an older `lib/as7341_sensor.py`):

   ```bash
   B=~/pico-backups/$(date +%Y%m%d_%H%M%S); mkdir -p "$B/lib"
   $M fs cp :main.py "$B/" + fs cp :lib/as7341_sensor.py "$B/lib/" + fs cp :lib/as7341.py "$B/lib/"
   ```
4. Patch the board's own `main.py`, not a fresh copy, so local edits (Wi-Fi country,
   I²C pins) survive. With this branch checked out in `~/byu-vcl` on the Pi (if
   `patch` refuses, port the three hunks by hand):

   ```bash
   mkdir -p /tmp/fw/sensor_file && tr -d '\r' < "$B/main.py" > /tmp/fw/sensor_file/main.py
   (cd /tmp/fw && patch -p1 < ~/byu-vcl/wireless-color-sensor/pico/main.py.patch)
   $M fs cp ~/byu-vcl/wireless-color-sensor/pico/sensor_settings.py :sensor_settings.py
   $M fs cp /tmp/fw/sensor_file/main.py :main.py + reset
   ```
5. Unplug it and put it back in its base. **Don't judge it while it's on the Pi's USB**
   (its prints block once the serial buffer fills; see `CLAUDE.md`).
6. Check over MQTT: `read(settings={"gain": 256})` should come back with
   `sensor_settings.halves[*].again_code == 9`, and a plain `read()` should give the
   same counts as before the change.

To undo: copy the backed-up `main.py` back, and delete `:sensor_settings.py`.

## First sweep once it's flashed

On white, black and one colour, at the standing read height, one landing each:
gain 64, 128, 256, 512 at atime 200, then atime 100 and 255 at the best gain. Re-read
the white and black at every setting: the datasheet's gain ratios are not exact powers
of two (512x is 7.25–8.25× the 64x response).

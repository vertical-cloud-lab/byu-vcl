# Pico W firmware: per-reading gain (installed 2026-10-09)

The colour sensor's Pico W (USB serial `e6647c15673a2438`) runs the board's own copy of
[`AccelerationConsortium/wireless-color-sensor`](https://github.com/AccelerationConsortium/wireless-color-sensor)
`sensor_file/`. On 2026-10-09 one change went in: **a read command can now ask for a gain.**
Nothing else changed. Integration time, Wi-Fi, MQTT and every other file are as they were.

| file | what |
| --- | --- |
| [`main.py`](main.py) | what is on the board now: the old `main.py` plus the gain change |
| [`main.py.gain.patch`](main.py.gain.patch) | the change on its own (two hunks) |
| [`board-2026-10-09/`](board-2026-10-09/) | every non-secret file as it was on the board before the change; [`MANIFEST.md`](board-2026-10-09/MANIFEST.md) lists all 32 with their on-board hashes |
| [`test_gain.py`](test_gain.py) | 40 checks without the board: the patch, the gain parsing, and both `main.py` files driven with fake MQTT messages |
| [`gain-test-2026-10-09.json`](gain-test-2026-10-09.json) | every reading taken on the board while testing, plus the chip's registers before and after |

## What is on the board

Read off the board on 2026-10-09 at 16:56 MDT, before anything changed.

| part | version |
| --- | --- |
| MicroPython | `v1.29.0 on 2026-08-24 (GNU 16.1.0 MinSizeRel)`, build `RPI_PICO_W`. Byte-identical to the official [`RPI_PICO_W-20260824-v1.29.0.uf2`](https://micropython.org/resources/firmware/RPI_PICO_W-20260824-v1.29.0.uf2): all 3,538 of its blocks match the board's flash. 1.29.0 is the version `CLAUDE.md` requires (I²C bug in 1.26–1.28) |
| Wi-Fi chip firmware | built into the MicroPython image above, so covered by the same file |
| `main.py` | 6,432 bytes, `469a5a6d…`. Upstream `07efedd` plus a `SoftI2C` import and a comment that MicroPython 1.29 is required. Both 09-03 backups call `Sensor()` with its defaults too |
| `lib/as7341_sensor.py` | 4,577 bytes, `d9b673c5…`, unchanged since at least the 09-03 backup. **Older than upstream:** `Sensor(atime=100, astep=999, gain=8)` |
| `lib/as7341.py`, `lib/mqtt_as.py`, other libraries | see [`MANIFEST.md`](board-2026-10-09/MANIFEST.md); all identical to the 09-03 backup |
| AS7341 sensor chip | no firmware. ID register `0x24` (AS7341), revision 0 |

**The sensor reads at 128x gain, 2 × 281 ms per reading.** That's what the board's
`Sensor()` sets (gain code 8, ATIME 100, ASTEP 999), and the chip's own registers said so
when read live: CFG1 = 8, ATIME = 100, ASTEP = 999. This corrects 10-01, when I read
upstream's newer `as7341_sensor.py` instead of the board's, and concluded the chip ran at
256x and 2 × 559 ms. Since the file hasn't changed since at least 09-03, **every reading
on record was taken at 128x, 2 × 281 ms.**

## Backups

On the robot Pi (`RPI_STREAM_CAM_HOSTNAME`), in `~/pico-backups/20261009_165748_before-gain/`
(mode 700, as it holds the Wi-Fi and MQTT credentials):

| file | what | checked |
| --- | --- | --- |
| `files/` | all 32 files, including `my_secrets.py` | each sha256 matched the one computed on the board |
| `flash-full-2MB.bin` | the whole 2 MB flash: MicroPython, Wi-Fi firmware and every file | sha256 `c9944136…135c`, matched the board's own |
| `flash-full-2MB-restore.uf2` | that image as a UF2, for drag-and-drop | converts back to the image exactly |
| `RPI_PICO_W-20260824-v1.29.0.uf2` | the official MicroPython download | identical to the board's firmware |
| `inventory.out` | the version and file report above | |

The board also keeps its old `main.py` as `main.py.before-gain`.

## Rolling back

Always address the board by its USB serial, never by `/dev/ttyACM*`:

```bash
M="$HOME/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438"
B=~/pico-backups/20261009_165748_before-gain
```

1. **Undo the gain change only** (the usual case):
   ```bash
   $M fs cp $B/files/main.py :main.py + reset
   ```
2. **Put back every file** exactly as on 10-09:
   ```bash
   cd $B/files && for f in $(find . -type f | sed 's|^\./||'); do $M fs cp "$f" ":$f"; done; $M reset
   ```
3. **Put back the whole flash** (MicroPython and all files), if the board won't boot or
   `mpremote` can't reach it: hold **BOOTSEL** while plugging the USB in (or run
   `$M bootloader`), and copy `flash-full-2MB-restore.uf2` onto the `RPI-RP2` drive that
   appears. Easiest from a laptop; on the Pi the drive has to be mounted by hand, which needs
   `sudo`. To reinstall MicroPython alone and keep the files, copy the official
   `RPI_PICO_W-20260824-v1.29.0.uf2` instead: it ends at `0x100DD200`, well before the
   filesystem.

## Using the gain

From the runner or the Pi:

```python
with sensor_read.SensorLink() as link:
    r = link.read(settings={"gain": 512})      # one reading at 512x
    r = link.read()                            # 128x, exactly as before
```

On the wire, a read command may carry `settings`; **gain is the only key accepted**:

```json
{"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": "...", "settings": {"gain": 512}}
```

- **gain:** 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256 or 512. Leaving `settings` out reads at 128x.
- **The gain applies to that one reading.** 128x is put back straight afterwards, even if
  the reading fails.
- **Every reply now says what gain it used:**
  `"sensor_settings": {"gain": 512, "again_code": 10, "analog_saturated": false}`. The code
  and the saturation flag come from the chip's ASTATUS register, read straight after the
  counts.
- **Anything else** (another key, a gain not in the list) gets an `error` reply and no reading.
- `SensorLink.read()` refuses a reply that doesn't confirm the gain it asked for.

**Gain ratios aren't exact powers of two.** On the board, 512x read 3.84× the 128x counts,
not 4×; the datasheet allows 7.25–8.25× between 64x and 512x. So re-read the white and
black wells at every gain you use; never scale one gain's readings to another.

## How it was tested

1. `python3 test_gain.py` (40 checks, no board). Among them: the patch turns the board's own
   `main.py` into [`main.py`](main.py) byte for byte; a plain read gives exactly the old
   `main.py`'s counts; integration time is never written.
2. **On the board, from RAM first** (`mpremote run`, nothing written to flash), then
   **installed and after a hard reset**, over MQTT from the runner. Totals of all 8 channels,
   with the sensor wherever it sat while plugged into the Pi:

   | gain | 32x | 64x | 128x (plain) | 256x | 512x |
   | --- | --- | --- | --- | --- | --- |
   | total | 601 | 1,185 | 2,382–2,385 | 4,696 | 9,146–9,157 |
   | reported code | 6 | 7 | 8 | 9 | 10 |

   Plain reads before, between and after the other gains agreed to within 3 counts, and gains
   300 and 1000 and an `atime` key were refused.
3. After the install, the chip's registers read CFG1 8, ATIME 100, ASTEP 999, as before, and
   the only file differences on the board were `main.py` and the added `main.py.before-gain`.

**One thing found while testing:** the ASTATUS byte that `lib/as7341.py` keeps from its own
bulk read showed code 8 at every gain, even though the counts scaled. Reading ASTATUS again
straight afterwards gave the right code, with the same counts. So `main.py` reads it
directly.

**And one observation:** after the hard reset the board answered over MQTT normally while
still plugged into the Pi's USB, with no program reading its serial port (every check from
17:09 to 17:13 MDT). `CLAUDE.md` warns that `main.py` can stall in that state. Probably
because nothing had opened the port since the reset: as I read MicroPython's USB code, it
drops output when no program has the port open, and only waits when one has it open but
isn't reading. Not tested further.

## The 10-01 version, withdrawn

[`3a74e00`](https://github.com/vertical-cloud-lab/byu-vcl/commit/3a74e00) made gain *and*
integration time settable. It was written against upstream's `main.py` and
`as7341_sensor.py`, not the board's, so its default (256x, 2 × 559 ms) would have changed
every plain reading 4×. It was never installed, and its files were removed from this folder
on 10-09.

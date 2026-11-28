---
name: ot2-color-sensor
description: The OT-2 liquid handler and the Pico W AS7341 color sensor - reaching the OT-2 HTTP API, the departed lid-camera Pi, driving the Pico with mpremote by USB serial, sensor firmware facts (R/Y/B are dispense volumes, AS7341 LED, SMUX timing), the MicroPython 1.29 I2C requirement, the USB print-buffer stall, prior accuracy work. Use for any OT-2, Pico W, color sensor or color-mixing hardware task.
---

# OT-2 and the Pico W color sensor

The rules in the root `CLAUDE.md` apply throughout: never print a credential, hostname or IP, and treat every Pi as a live production device.

**The OT-2 lid camera Pi left on 2026-11-10.** The Pi 5 + HQ Camera behind
`RPI_STREAM_CAM_HOSTNAME` (also the OT-2's network link, the CubOS Pi and the `~/ytframes`
host) now belongs to the Borys lab at the University of Utah and is on their tailnet. It
streams to their channel, not ours. Its VCL files were archived to Sterling's OneDrive
(*VCL Pi archives*) and removed from the Pi. `RPI_STREAM_CAM_HOSTNAME`, `_USERNAME` and
`_PASSWORD` therefore point at nothing until a replacement Pi is set up and they are
updated. Until then **the OT-2 has no network link and no overhead camera.** The rebuild
(parts, steps, and the Pi-only scripts salvaged from it) is tracked in
[vertical-cloud-lab/digital-wetlab](https://github.com/vertical-cloud-lab/digital-wetlab).

**Reaching the OT-2.** The robot is not on the tailnet. It was wired directly to the Pi
behind `RPI_STREAM_CAM_HOSTNAME` (not `OT2_STREAM_CAM_HOSTNAME`, which is the atomizer-room
Zero 2 W) and answered only on the link-local address
`http://169.254.51.252:31950`, so every OT-2 HTTP API call has to be made *from that Pi* —
you cannot reach the robot from a runner or a laptop. `~/ot2ctl.py` on that Pi is a thin
wrapper over the maintenance-run API and is the quickest way to see the call pattern. Send
`Opentrons-Version: 3` on every request. `GET /health` is read-only and safe; anything under
`/maintenance_runs` moves real hardware.

**Reaching the Pico W.** The sensor board plugged into the OT-2 lid camera Pi (gone since 2026-11-10; see
"Reaching the OT-2") over USB and is
driven with `mpremote`, installed there as a venv at `~/.venvs/mpremote/bin/mpremote`
(1.29.0 + pyserial). It went in as a venv rather than apt so it needs no sudo and touches
nothing system-wide; that Pi also runs CubOS gantry work, so keep changes to it contained.

**Always address the board by USB serial, never by device path:**

```bash
~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 fs ls
```

An Arduino (`2341:0043`) already owns `/dev/ttyACM0` on that Pi, so the Pico comes up as
`ttyACM1` — and `mpremote`'s bare auto-connect grabs the *first* ACM device. Targeting a
path, or letting it auto-detect, opens a REPL against the Arduino instead, which may be
driving real gantry hardware. Match on `2e8a` / the serial and nothing else.

Two more gotchas. Connecting with `mpremote` interrupts whatever `main.py` is running and
its buffered `log.txt` is lost, so an empty log after a reset means "I interrupted it", not
"it never ran" — to watch a boot, `mpremote ... run <local copy of main.py>` and read the
stream instead. And the reference `main.py` calls `connectWiFi(..., country="CA")`; for US
operation that should be `"US"`, since the country code governs the usable 2.4 GHz channels.

**The sensor firmware's own facts, read from source** (upstream
[`wireless-color-sensor`](https://github.com/AccelerationConsortium/wireless-color-sensor),
`sensor_file/`, which is what our Pico W runs). Three of these were guessed wrong on #197
before anyone read the code:

- **`R`/`Y`/`B` in the MQTT command payload are paint dispense volumes in microlitres, not
  LED colours.** `OT2mqtt.py` aspirates them from vials `B1`/`B2`/`B3` with `R+Y+B <= 300`
  because the pipette is a P300. The sensor board never reads them. So `sensor_read.read(
  rgb=...)` controls nothing and never did.
- **There is a controllable white LED on the AS7341** — `lib/as7341.py` `set_led_current()`,
  4-20 mA, wrapped as a `Sensor.LED` property. It is off because `main.py`'s
  `read_sensor_data()` has `# sensor.LED = True` / `# sensor.LED = False` commented out.
  Do not "fix" this without reading
  [ac-dev-lab#87](https://github.com/AccelerationConsortium/ac-dev-lab/issues/87) first: it
  was tried upstream and rejected for saturating the enclosure walls and making similar
  colours *less* distinguishable.
- **One reading is two SMUX integrations**, `F1F4CN` then `F5F8CN`, and `Clear` is sampled
  in both and discarded in both. At the shipped `Sensor(atime=200, astep=999, gain=128)`
  that is 558.8 ms per cycle, 1.118 s per reading — about 80% of the measured ~1.42 s MQTT
  round trip. Gain 128x against a 512x maximum, and the largest channel ever recorded here
  is 3216 of 65535 full scale, so there is real headroom.

**Prior art: this has worked before, upstream, twice.** See
`wireless-color-sensor/ot2/accuracy-provenance.md` for the sourced ledger — the quantified
success is a per-well white reference taking repeatability from 6-7% RSD to 1.2-2.3%
([ac-dev-lab#152](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152)), and
the second is a light panel under the plate plus per-well blank normalisation
([ac-dev-lab#552](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552)). Check
that file before re-deriving an accuracy fix from scratch; #197 re-derived the per-position
blank independently over several sessions.

**MicroPython 1.29.0 or newer is required.** On 1.26–1.28 the RP2040 hardware I2C driver has
a regression: `i2c.scan()` ACKs the AS7341 at `0x39`, but every register read or write
returns `OSError: [Errno 5] EIO`, at any bus speed, with or without a repeated START. It
cost real time to find because it looks exactly like a wiring or power fault, and because it
reproduces on *every* board — two different Pico Ws, two different sensors and two different
base boards all failed identically. That cross-board consistency is the tell: a shared
firmware bug, not a shared hardware fault. Bit-banged `SoftI2C` works on the same pins on the
affected versions and is the fallback if an older build is ever unavoidable. See
[micropython#19087](https://github.com/micropython/micropython/issues/19087) and
[micropython#18257](https://github.com/micropython/micropython/issues/18257).

**Do not judge the sensor from a board plugged into the Pi.** `main.py` prints continuously
(`waiting for connection...`, `Elapsed: Ns`, `RAM free ...`). With USB enumerated but nothing
reading the serial port, the RP2040 CDC TX buffer fills and `print()` blocks, so `main.py`
starts and then wedges before it ever reaches the broker. Under `mpremote run` a host is
draining the buffer, so the same code runs fine — which makes this look like an intermittent
network problem. On mains or battery power with no USB host, MicroPython discards stdout and
it behaves normally. Verify the MQTT path with the board on its own power, not on the Pi.

Board backups (including the pre-existing `my_secrets.py`) are on the Pi under
`~/pico-backups/<timestamp>/`, and the board keeps its own `my_secrets.py.bak`.

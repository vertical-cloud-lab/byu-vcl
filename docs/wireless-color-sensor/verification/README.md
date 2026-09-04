# Verification run — 2026-09-04, after the ground rework

Everything below was measured this session against the physical board
(`e6647c15673a2438`), reached over Tailscale → stream-cam Pi → USB, and over the
broker from CI.

## Result

The board is fully functional. The whole pipeline runs:

    Pico W ──wifi/TLS──▶ HiveMQ ──▶ CI ──▶ MongoDB

| Check | Result |
| --- | --- |
| AS7341 at `0x39`, I2C0 SDA=GP4 SCL=GP5 | present |
| firmware | 1.29.0, `RPI_PICO_W` |
| sensor response to its own LED (gain 4) | **51 → 31239 counts, 600×**, 0/8 saturated |
| baseline after the LED goes off | returns to 51 — no drift |
| readings published over the board's own radio | 4/4 delivered |
| `main.py` answering MQTT commands after a reset | 3/3, ~1.5 s |
| readings collected through the normal command path | 10/10, 1.39–1.49 s |
| documents written to `digital-wetlab.sensor-data` | 14 |

## What the board was doing when it looked dead

It was silent on MQTT at the start of the session while sitting on the Pi's USB
port, and a **`reset` was enough to bring it back** — after which `main.py`
joined wifi and answered every command. So the silence was a wedged process, not
a fault: consistent with the USB CDC trap, where `main.py` prints continuously,
the buffer fills with no host draining it, and `print()` blocks forever.

## The ground rework is NOT validated by this run

USB was supplying power throughout:

    VBUS present (USB supplying power): True
    ADC(Pin(29))   raw=   32629  ->  4.929 V     # VSYS, USB rail

`ADC(3)` returns 0.037 V on this build and is wrong; use `ADC(Pin(29))`.

Battery operation is therefore untested. To test it: unplug USB, short-press the
LiPo SHIM button, then run `python board_triage.py`.

## Firmware faults — still unfixed, and visible in the numbers

The contrast between the two paths isolates fault #1 exactly. Same sensor, same
gain, minutes apart:

| path | LED | total counts |
| --- | --- | ---: |
| `board_read_colors.py` (LED driven explicitly) | on | **31239** |
| `main.py` via an MQTT command | commented out | **810** |

1. `sensor.LED = True` is commented out in `read_sensor_data()` — readings are of
   ambient light only.
2. `set_color` is undefined and no NeoPixel is wired, so the R/Y/B values in a
   command are ignored. Ten readings across five commanded colours returned
   totals of 809–812, i.e. within noise of each other.
3. The driver default `gain=8` saturates when lit; `gain=4` does not (measured
   0/8 saturated at 31239 counts).

## Scripts

Each runs on the board via `mpremote ... run <file>`, addressed by USB serial:

    ~/.venvs/mpremote/bin/mpremote connect id:e6647c15673a2438 run board_read_colors.py

- `board_read_colors.py` — dark / LED-on / dark, one I2C init. Re-muxing I2C0
  latches the bus so `scan()` keeps ACKing while every register read returns
  `OSError(5)`, hence the single init.
- `board_publish_wireless.py` — reads and publishes over the board's own radio,
  so the reading travels wifi → TLS → broker rather than back down the cable.
- `board_power_state.py` — VBUS presence and VSYS, to tell USB power from battery.

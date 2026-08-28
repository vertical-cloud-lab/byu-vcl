# Reading the wireless color sensor (intensity + flicker frequency)

Tooling to take an actual measurement from the AS7341 in the sensor package —
per-wavelength counts, a broadband intensity channel, and the flicker
frequency — and get it off the Pico W as JSON/CSV.

## What the AS7341 can actually report

"Light intensity and frequency" maps onto three different things on this part,
so it is worth being precise about which number is which:

| quantity | what you get | notes |
|---|---|---|
| **Spectral intensity** | 8 channels: 410, 440, 470, 510, 550, 583, 620, 670 nm | 16-bit counts per channel. This is the "frequency content" of the light in the optical sense — the sensor's whole point. |
| **Broadband intensity** | `clear` (unfiltered) and `nir` | `clear` is the closest thing to a single "how bright is it" number. It is **counts, not lux** — the AS7341 is not a calibrated photometer, so treat it as relative unless you calibrate against a reference. |
| **Flicker frequency** | `flicker_hz` = **100, 120, or 0** | A dedicated mains-flicker detector, *not* a general frequency counter. 120 Hz = 60 Hz mains (what BYU lab lighting should read), 100 Hz = 50 Hz mains, 0 = no flicker detected (daylight, DC-driven LED, high-frequency driver, or too dim to call). |

Every reading also carries `basic_counts` (raw counts ÷ (gain × integration
time)) and a `saturated` flag. Compare `basic_counts` — not raw counts —
whenever gain, `atime`, or `astep` differ between readings.

## Path 1 — USB serial (works today, returns everything)

Plug the Pico W into any computer with a USB cable. No WiFi, no broker, no
credentials.

```bash
pip install pyserial
# copy pico_read_intensity_flicker.py onto the Pico first (Thonny, or mpremote:
#   mpremote cp pico_read_intensity_flicker.py :
# — or skip that, the collector uploads it into RAM automatically)
python collect_over_serial.py --n 10 --period 1.0 --out reading.json --csv reading.csv
```

Options: `--led-ma 8` turns the onboard LED on for the reading (even values
4–20 mA; 0 = ambient), `--port` overrides autodetection.

Output looks like:

```
idx    clear    nir      flicker   spectral counts
0      5231     812      120 Hz       99   294   470   756  1172  1507  1548   775
channel order: 410, 440, 470, 510, 550, 583, 620, 670 (nm)
```

The collector sends Ctrl-C first, which stops the demo `main.py` running on the
Pico. Nothing is written to the Pico's filesystem; power-cycling restores normal
MQTT operation.

**Plugging the Pico into the RPi-5** (`rpi-5-stream-cam-2wp0`, already on the
tailnet next to the OT-2) makes this remotely triggerable — including by
`@claude` from a GitHub comment, the same way the OT-2 pickup tests are driven.
That is the lowest-effort way to get readings without someone standing at a
laptop.

## Path 2 — wireless over HiveMQ (needs credentials, and a firmware change)

`request_over_mqtt.py` speaks the topic contract already implemented in the
upstream demo firmware (`sensor_file/main.py`):

- publish `command/picow/{PICO_ID}/as7341/read` with
  `{"command": {"R":0,"Y":0,"B":0}, "experiment_id": "..."}`
- reply arrives on `color-mixing/picow/{PICO_ID}/as7341` with `sensor_data`
  added

```bash
pip install paho-mqtt
cp my_secrets.example.py my_secrets.py   # fill in HIVEMQ_* and PICO_ID
python request_over_mqtt.py --out reading.json
```

Two limitations, both real:

1. **Credentials.** These are *not* only on the Pico: host, username **and
   password** are committed in the upstream demo's Colab notebook
   ([`sensor_file/test_sensor.ipynb`](https://github.com/AccelerationConsortium/wireless-color-sensor/blob/main/sensor_file/test_sensor.ipynb)),
   which is how the 2026-08-10 readings were taken. That also means anyone can
   publish to this device's command topic, so they are worth rotating and
   moving into Actions secrets (`HIVEMQ_PASSWORD`) rather than relied on as
   published. `PICO_ID` is `test`.
2. **The firmware returns less than the sensor can.** `main.py` calls the
   `Sensor` wrapper's `all_channels`, which returns only the 8 spectral
   channels — it discards `clear`/`nir` and never touches flicker detection.
   For a wireless intensity + flicker reading, `main.py`'s `read_sensor_data()`
   needs replacing with a call into this directory's `measure()`:

   ```python
   from pico_read_intensity_flicker import measure

   def read_sensor_data():
       return measure(quiet=True)
   ```

   That keeps the MQTT contract identical while widening `sensor_data`.

## Path 3 — read *and store* (`read_and_upload.py`)

Paths 1 and 2 get a reading onto your screen. This one carries it the rest of
the way to the VCL MongoDB, and — more usefully — tells you *which* system
broke when it doesn't:

```bash
pip install paho-mqtt pymongo
export HIVEMQ_PASSWORD=...   # broker
export MONGODB_URI=...       # database
python read_and_upload.py --n 3 --label "red dye, well A1" --upload
```

Nine numbered stages (S1 network → S9 verified upsert), each with its own exit
code; readings are written to disk *before* any upload is attempted, so a
database outage only costs a backfill. Full stage table, reproduced failure
signatures and remedies: [`READ_AND_UPLOAD_RUNBOOK.md`](READ_AND_UPLOAD_RUNBOOK.md).

## Files

| file | runs on | purpose |
|---|---|---|
| `pico_read_intensity_flicker.py` | Pico W (MicroPython) | Drives `lib/as7341.py` directly for 8 channels + clear + NIR + flicker; prints `#WCS# {...}` JSON |
| `collect_over_serial.py` | host (RPi-5 / laptop) | Raw-REPL client over USB; parses readings, writes JSON/CSV |
| `request_over_mqtt.py` | host | HiveMQ request/response using the upstream topic contract |
| `read_and_upload.py` | host | **Read → validate → derive colour → MongoDB**, split into numbered stages so a failure names the system that broke. See [`READ_AND_UPLOAD_RUNBOOK.md`](READ_AND_UPLOAD_RUNBOOK.md) |
| `my_secrets.example.py` | host | Template for the MQTT credentials (`my_secrets.py` is git-ignored) |

`pico_read_intensity_flicker.py` needs the upstream `lib/` folder
(`as7341.py`, `as7341_smux_select.py`) already present on the Pico — it is, on
the demo board.

## Status

As of **2026-08-28**, tested end-to-end from a GitHub Actions runner:

- **Broker path works** — DNS, TLS and MQTT auth all pass, and the reply topic
  subscribes cleanly (S1–S3).
- **The Pico W does not answer** (S4) — every read command is PUBACKed by the
  broker and nothing comes back; a 45 s listen on `#` and `$SYS/#` saw zero
  messages. The sensor has been offline since the 2026-08-10 session; a flat
  LiPo is the leading hypothesis.
- **The storage half is proven** (S5–S9) against a real MongoDB 7.0.40 server,
  replaying the genuine 2026-08-10 readings, including idempotent re-upload
  and read-back verification.

The USB path (`collect_over_serial.py`) remains the way to test the AS7341
itself without WiFi, and is still un-run against hardware.

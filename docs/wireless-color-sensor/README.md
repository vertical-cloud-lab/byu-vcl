# Wireless color sensor: end-to-end test procedure

How to test the AS7341 wireless color sensor from "does it read a color?" all the
way to "did the reading land in the database?", structured so that a failure tells
you **which link broke** instead of just that something broke.

Companion to [issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33).
Reference build: <https://accelerationconsortium.github.io/wireless-color-sensor/>

## The pipeline (and the part that surprises people)

```
  Pico W + AS7341            HiveMQ Cloud              Bridge service            MongoDB
 ┌──────────────────┐      ┌──────────────┐        ┌──────────────────┐      ┌───────────┐
 │ read 8 channels  │─────▶│  MQTT broker │───────▶│ subscribes, then │─────▶│ documents │
 │ publish JSON     │ TLS  │  (port 8883) │  TLS   │ writes to Mongo  │      │           │
 └──────────────────┘      └──────────────┘        └──────────────────┘      └───────────┘
      stages 1-8                stages B-F              stage F                stages G-H
   (pico_selftest.py)                    (host_selftest.py)
```

**The sensor never talks to the database.** It only publishes MQTT. Something else
has to subscribe and write to MongoDB. In the AC reference deployment that
"something else" is the Hugging Face Space
([`OT-2-LCM/app.py`](https://huggingface.co/spaces/AccelerationConsortium/OT-2-LCM/blob/main/app.py)),
which subscribes to the sensor topic and calls `save_result()` in `DB_utils.py`.

Two consequences that are easy to lose an afternoon to:

1. If you are watching MongoDB for rows and see nothing, the sensor may be working
   perfectly. The missing piece is the subscriber.
2. In the reference Space, `save_result()` is only called at the end of a **full
   OT-2 experiment flow** — a bare sensor reading published on its own is held in
   memory (`sensor_results[exp_id]`) and never persisted. So "publish a reading and
   expect a database row" does not work even with a correctly configured Space.

Topics (from the reference [`main.py`](https://github.com/AccelerationConsortium/wireless-color-sensor/blob/main/sensor_file/main.py)):

| Direction | Topic |
| --- | --- |
| command in | `command/picow/{PICO_ID}/as7341/read` |
| data out | `color-mixing/picow/{PICO_ID}/as7341` |

Payload published by the sensor:

```json
{
  "experiment_id": "...",
  "command": {"R": 0, "Y": 0, "B": 0},
  "sensor_data": {"ch410": 112, "ch440": 205, "ch470": 338, "ch510": 410,
                  "ch550": 502, "ch583": 466, "ch620": 389, "ch670": 271}
}
```

The eight channels are the AS7341's spectral bands in nanometres. A reading is
"a color" in the sense that the *ratio* between channels encodes hue — ch410/ch440
rise under blue light, ch620/ch670 under red.

## Running the test

### Part 1 — on the Pico W: `pico_selftest.py`

Copy to the board and run it in Thonny (or `mpremote run pico_selftest.py`).
Set `STOP_AFTER = 3` at the top to check only the sensor, with no credentials and
no network involved. That is the right first move whenever behaviour is
uncertain — it separates "the sensor is broken" from "the network is broken".

| Stage | Checks | Needs |
| --- | --- | --- |
| 1 | I2C scan finds the AS7341 at `0x39` | sensor plugged in |
| 2 | All 8 spectral channels read back | `as7341_sensor.py` in `/lib` |
| 3 | Counts track LED color (red→ch620/670, blue→ch410/440) | NeoPixel |
| 4 | `my_secrets.py` has all 6 values | credentials on device |
| 5 | WiFi associates | 2.4 GHz WPA2-PSK network |
| 6 | NTP sets the clock | outbound NTP allowed |
| 7 | `ssl`/`ussl` importable, CA cert present | correct firmware |
| 8 | MQTT connect over TLS, publish a real reading | broker credentials |

Stage 3 is the actual "reads for some colors" test: it takes a reading with the
LED off, then under red, green, and blue, and confirms the channels move in the
expected spectral direction. Brightness alone is not enough — a sensor that
responds to *any* light but not *differentially* is reported as a distinct failure.

### Part 2 — off the Pico: `host_selftest.py`

Runs on any machine with CPython. Verifies the upload half.

```bash
pip install paho-mqtt pymongo

export HIVEMQ_HOST=abc123.s1.eu.hivemq.cloud   # bare hostname, no https://
export HIVEMQ_USERNAME=... HIVEMQ_PASSWORD=...
export PICO_ID=...
export MONGODB_CONNECTION_STRING=...           # optional; G-H skip without it

python host_selftest.py              # listen for whatever the sensor publishes
python host_selftest.py --command    # actively ask the sensor for a reading
python host_selftest.py --anonymous  # against a local broker, to rule out HiveMQ auth
```

| Stage | Checks |
| --- | --- |
| A | Required credentials are present in the environment |
| B | Broker hostname resolves |
| C | TCP + TLS handshake on 8883 succeeds |
| D | Broker accepts the credentials (CONNACK rc) |
| E | Subscribe to the data topic is acknowledged |
| F | A reading actually arrives, with all 8 channels |
| G | MongoDB responds to `ping` |
| H | A document round-trips: insert then read back |

Exit code is 0 only if every attempted stage passed, so it works in CI.

## Where errors occur: fault localization

Read this top to bottom and stop at your first failure. Later stages depend on
earlier ones, so downstream failures are usually noise.

| Symptom | Almost always means |
| --- | --- |
| `ImportError: no module named 'machine'` | The script ran in desktop Python, not on the Pico. This is the failure reported earlier in issue #33 — the board showed as disconnected, so Thonny fell back to the local interpreter. |
| `ImportError: no module named 'ssl'` (and `ussl` also missing) | The firmware is not a stock Pico W build. Reflash the official `RPI_PICO_W` `.uf2`: hold BOOTSEL, plug in USB, drag the file onto the `RPI-RP2` drive. If `RPI-RP2` never appears, try a different **cable** (charge-only micro-USB cables are common) and a different port before suspecting the board. |
| Stage 1 I2C scan returns `[]` | No power or a dead STEMMA QT cable. Reseat both ends. |
| Stage 1 finds devices but not `0x39` | Something else is on the bus; the AS7341 is not connected. |
| Stage 2 all channels read `0` | Sensor answers on I2C but returns no counts — usually total darkness or unset gain. Retry under room light. |
| Stage 3 no change LED off vs. on | The NeoPixel pin is wrong, or the LED is not illuminating the sensor. Watch it by eye while the test runs. |
| Stage 5 WiFi never associates | MicroPython supports **WPA2-PSK on 2.4 GHz only**. It cannot join eduroam or any WPA2-Enterprise SSID, and cannot see 5 GHz-only networks. Use a dedicated IoT SSID or a phone hotspot forced to 2.4 GHz. |
| Stage 8 fails with a certificate error | Check stage 6 first. A wrong clock invalidates every certificate and surfaces as a confusing TLS error. |
| Stage D `rc=4` | Wrong username or password. |
| Stage D `rc=5` | Credential exists but is not authorized. |
| Stage E no SUBACK | The credential lacks **subscribe** permission on the topic. HiveMQ requires publish and subscribe to be granted explicitly per topic pattern — this is the single most common silent failure in this stack. |
| Stage C times out | Port 8883 blocked by a firewall. Confirm with a phone hotspot. |
| **Stages C–E pass but F times out** | The broker path is healthy, so the sensor is not publishing. Check that the Pico is powered and *running* `main.py` rather than sitting at the REPL, that it joined WiFi, and that `PICO_ID` matches the device exactly. Run `pico_selftest.py` to find out which. |
| Stage G fails on DNS/timeout | Atlas network access list does not include the client IP. CI runners and HF Spaces have dynamic IPs, so this needs `0.0.0.0/0`. |
| Stage H insert fails after G passes | The DB user has connect but not `readWrite` on that database. |

## Status as of 2026-08-28

An automated attempt to run this test end-to-end from GitHub Actions could not
reach any hardware. Findings, in the order they block progress:

1. **`claude.yml` no longer joins the tailnet.** `CLAUDE.md` states the workflow
   pre-connects via the Tailscale GitHub Action, but the current workflow has only
   three steps — checkout, model-selector, and the Claude action — and `tailscale`
   is not installed on the runner. Connecting is still possible because
   `TS_OAUTH_CLIENT_ID` / `TS_OAUTH_SECRET` are in the env block, but it has to be
   done manually each run. Either restore the action step or update `CLAUDE.md`.
2. **No Pico W is attached to any reachable machine on the tailnet.** Four Pis were
   online; three were reachable over Tailscale SSH and were inspected
   (`rpi-5-stream-cam`, `rpi-2w-stream-cam`, `rpi-zero2w-stream-cam`). The fourth,
   `rpi-zero2w-powder-doser`, refused the credentials available here and was not
   checked. Of the three inspected, `rpi-5-stream-cam` has an Arduino Uno R3 and a
   CH340 adapter on USB; the other two have no USB serial devices at all. No device
   with the Raspberry Pi USB vendor ID (`2e8a`) appeared on any of them. None had
   AS7341, `my_secrets.py`, `mqtt_as`, or `netman` code, and none had `paho-mqtt` or
   `pymongo` installed.
3. **No broker or database credentials exist in this repository.** The `env:` block
   of `claude.yml` contains no `HIVEMQ_*`, `MQTT_*`, `MONGODB_*`, or `PICO_ID`
   entries. This matches the still-open checklist in
   [this comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/33#issuecomment-5273486295):
   the MongoDB cluster and HiveMQ broker have not been created for BYU VCL yet.
4. **No subscriber/bridge exists for BYU VCL.** Even with a broker and a database,
   nothing currently subscribes to the sensor topic and writes to MongoDB. The AC
   reference deployment does this inside its Hugging Face Space, and that Space has
   not been duplicated under a BYU VCL account.

So the sensor→database chain has three of its four links missing on the BYU VCL
side. `host_selftest.py` was validated against a live public TLS broker with a
simulated sensor — stages A–F pass, and G/H were confirmed to fail cleanly with a
bad connection string — so the harness itself is known-good and ready to point at
real infrastructure.

## To unblock

1. Bring the Pico W to a machine and run `pico_selftest.py` with `STOP_AFTER = 3`.
   This needs no accounts and no credentials, and settles whether the assembled
   hardware reads color at all. **Do this first** — it is independent of everything
   below.
2. Create the HiveMQ Cloud cluster and a credential with explicit publish *and*
   subscribe permission on `color-mixing/#` and `command/#`.
3. Create the MongoDB Atlas cluster, a `readWrite` user, and set network access to
   `0.0.0.0/0`.
4. Write `my_secrets.py` onto the Pico, then run the full `pico_selftest.py`.
5. Add `HIVEMQ_HOST`, `HIVEMQ_USERNAME`, `HIVEMQ_PASSWORD`, `PICO_ID`, and
   `MONGODB_CONNECTION_STRING` as repository secrets **and** to the `env:` block of
   `.github/workflows/claude.yml`. The workflow edit must be made by a human — the
   GitHub App cannot modify files under `.github/workflows/`.
6. Stand up the subscriber that writes to MongoDB, either by duplicating the AC
   Space or by running a small bridge on one of the Pis.

Steps 2–6 are the infrastructure work already scoped in issue #33; step 1 is
independent and worth doing immediately.

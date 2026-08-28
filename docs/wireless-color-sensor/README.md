# Wireless color sensor: end-to-end test procedure

How to test the AS7341 wireless color sensor from "does it read a color?" all the
way to "did the reading land in the database?", structured so that a failure tells
you **which link broke** instead of just that something broke.

Companion to [issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33).
Reference build: <https://accelerationconsortium.github.io/wireless-color-sensor/>

| File | What it is |
| --- | --- |
| [`pico_selftest.py`](pico_selftest.py) | 8 on-device stages, sensor through MQTT publish. `STOP_AFTER = 3` needs no credentials. |
| [`host_selftest.py`](host_selftest.py) | 8 host-side stages, broker through MongoDB round-trip. |
| [`mqtt_to_mongodb.py`](mqtt_to_mongodb.py) | The bridge: subscribes to the sensor topic, writes each reading to MongoDB. |
| [`simulate_sensor.py`](simulate_sensor.py) | Publishes realistic AS7341 readings, to test the upload path without hardware. |
| [`local_e2e_demo.sh`](local_e2e_demo.sh) | Runs the whole upload pipeline locally with no cloud accounts. |

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
For BYU VCL that piece is [`mqtt_to_mongodb.py`](mqtt_to_mongodb.py) in this
directory — it stores every reading as it arrives, with no experiment
orchestration in between.

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

### Part 3 — the bridge: `mqtt_to_mongodb.py`

The piece that actually answers "did it upload to our database?". Subscribes to
the sensor topic and inserts one document per reading.

```bash
export HIVEMQ_HOST=... HIVEMQ_USERNAME=... HIVEMQ_PASSWORD=... PICO_ID=...
export MONGODB_CONNECTION_STRING=...

python mqtt_to_mongodb.py --loopback              # run until interrupted
python mqtt_to_mongodb.py --loopback --expect 3   # exit 0 after 3 readings stored
python mqtt_to_mongodb.py --dry-run               # parse and print, never write
```

**Always pass `--loopback`.** See the next section for why — without it, the two
most common failures are indistinguishable.

Each reading is stored as:

```json
{
  "received_at":    "2026-08-28T17:34:21.452Z",
  "topic":          "color-mixing/picow/{PICO_ID}/as7341",
  "device_id":      "{PICO_ID}",
  "experiment_id":  "33ed97e0-...",
  "command":        {"R": 255, "Y": 0, "B": 0},
  "sensor_data":    {"ch410": 31, "...": "...", "ch670": 874},
  "raw":            "<the payload exactly as published>",
  "malformed":      false
}
```

`raw` is kept deliberately: a payload that fails to parse is still stored, flagged
`malformed`, rather than dropped. A reading silently discarded at 2am is much
harder to diagnose than one sitting in the collection with a flag on it.

To exercise the upload path without hardware, [`simulate_sensor.py`](simulate_sensor.py)
publishes the same payload shape the firmware does:

```bash
python simulate_sensor.py --colors off red green blue white
```

That is also the cleanest way to split a failure in half: if the simulator's
readings reach MongoDB, then the broker, bridge, and database are all fine and the
problem is on the device.

### Part 4 — prove the whole thing offline: `local_e2e_demo.sh`

```bash
./local_e2e_demo.sh
```

Stands up a local mosquitto broker configured like HiveMQ Cloud (TLS on 8883,
username/password auth) and a MongoDB container, then runs simulated readings
through the bridge into the database and reports what landed. No cloud accounts,
no hardware, about a minute.

Its value is as a control: if this passes on your machine but the real pipeline
fails, the difference is in the credentials or the cloud services, not the code.
Requires docker, mosquitto, and openssl. Set `MQTT_PORT` / `MONGO_PORT` if you
already have something on 8883 or 27017.

## The trap: a successful subscription that delivers nothing

This is worth its own section because it cost time on this issue and it is
genuinely counter-intuitive.

A broker can accept your subscription — returning `SUBACK: Granted QoS 1`, the
same acknowledgement a working subscription gets — and then deliver **zero**
messages, because the credential lacks *read* permission on the topic. This was
reproduced deliberately against a local broker with a publish-only ACL:

```
SUBACK: ['Granted QoS 1']
published (client has write permission)
RESULT: messages delivered back to subscriber = 0
```

From the subscriber's side, that is indistinguishable from a sensor that simply
is not publishing. Both look like "connected, subscribed, nothing arrives", and
it is easy to spend an afternoon debugging a Pico that was never at fault.

`--loopback` resolves it. The bridge publishes a probe to its own subscribe topic
and waits for the echo:

- **probe comes back** → the delivery path is proven good, so silence really is
  the sensor's fault.
- **probe does not come back** → broker permissions, not the sensor.

```
loopback  FAIL -- the broker acknowledged the subscription but did not deliver
                  our own probe back to us.
-> this is a BROKER PERMISSION problem, not a sensor problem
-> in HiveMQ, grant this credential both publish AND subscribe on the topic
   pattern (they are separate permissions)
```

Probe messages are recognised by a per-run nonce and are never written to MongoDB.

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
| Stage E no SUBACK | The credential lacks **subscribe** permission on the topic. HiveMQ requires publish and subscribe to be granted explicitly per topic pattern. |
| Subscribe is acknowledged but no data ever arrives | Ambiguous by design — either the sensor is silent or the credential lacks *read* access. Re-run the bridge with `--loopback` to tell them apart. See the section above. |
| Bridge: `CONNECT REFUSED rc=4` or `rc=134` | Wrong username or password. (3.1.1 brokers say 4, MQTT 5 brokers say 134.) |
| Bridge: `CONNECT REFUSED rc=5` or `rc=135` | Credential exists but is not authorized for this topic. |
| Bridge: `loopback FAIL` | Broker permissions. The credential needs subscribe as well as publish. |
| Bridge: `INSERT FAILED` after Mongo connects | The DB user can connect but lacks `readWrite` on that database. |
| Bridge: documents stored with `malformed: true` | The device published something that is not the expected JSON. Inspect the `raw` field of those documents — the payload is preserved. |
| Stage C times out | Port 8883 blocked by a firewall. Confirm with a phone hotspot. |
| **Stages C–E pass but F times out** | The broker path is healthy, so the sensor is not publishing. Check that the Pico is powered and *running* `main.py` rather than sitting at the REPL, that it joined WiFi, and that `PICO_ID` matches the device exactly. Run `pico_selftest.py` to find out which. |
| Stage G fails on DNS/timeout | Atlas network access list does not include the client IP. CI runners and HF Spaces have dynamic IPs, so this needs `0.0.0.0/0`. |
| Stage H insert fails after G passes | The DB user has connect but not `readWrite` on that database. |

## Status as of 2026-08-28

Two automated attempts have now been made to run this test end-to-end from GitHub
Actions. Neither could reach hardware. The second attempt re-verified every
finding independently rather than inheriting it, and additionally built and
validated the missing bridge.

### What was verified this run

1. **`claude.yml` no longer joins the tailnet.** `CLAUDE.md` states the workflow
   pre-connects via the Tailscale GitHub Action, but the workflow has only three
   steps — checkout, model-selector, and the Claude action — and `tailscale` is not
   installed on the runner. Connecting manually works because `TS_OAUTH_CLIENT_ID`
   / `TS_OAUTH_SECRET` are in the env block. Either restore the action step or
   correct `CLAUDE.md`.
2. **No Pico W is attached to any reachable machine on the tailnet.** Five machines
   were online; three accepted the credentials available here and were inspected.
   One has an Arduino Uno R3 and a CH340 adapter on USB; the other two have no USB
   serial devices at all. No device with the Raspberry Pi USB vendor ID (`2e8a`)
   appeared on any of them, and none had AS7341, `my_secrets.py`, `mqtt_as`, or
   `netman` code, or `paho-mqtt` / `pymongo` installed. Two machines refused the
   available credentials and could not be checked.
3. **No broker or database credentials exist in this repository.** The `env:` block
   of `claude.yml` contains no `HIVEMQ_*`, `MQTT_*`, `MONGODB_*`, or `PICO_ID`
   entries. This matches the still-open checklist in
   [this comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/33#issuecomment-5273486295):
   the MongoDB cluster and HiveMQ broker have not been created for BYU VCL yet.
4. **The bridge did not exist.** Nothing subscribed to the sensor topic and wrote
   to MongoDB. That is now [`mqtt_to_mongodb.py`](mqtt_to_mongodb.py).

### What was proven to work

The upload half of the pipeline was run for real on the CI runner, against a
mosquitto broker configured to mimic HiveMQ Cloud (TLS on 8883, username/password
auth, per-topic ACLs) and a genuine MongoDB 7 instance:

```
17:34:15  connected
17:34:15  subscribed to color-mixing/picow/{PICO_ID}/as7341
17:34:15  loopback  probe published, waiting for it to come back...
17:34:15  loopback  PASS -- the broker delivers on this topic
17:34:20  stored _id=6a91c69c...  looks  dark  (B=15  G=21  R=16)
17:34:21  stored _id=6a91c69d...  looks   red  (B=38  G=134 R=898)
17:34:22  stored _id=6a91c69e...  looks green  (B=117 G=750 R=119)
17:34:23  stored _id=6a91c69f...  looks  blue  (B=768 G=155 R=34)
17:34:23  stored _id=6a91c69f...  looks white  (B=568 G=643 R=564)
17:34:24  done -- 5 message(s) received, 5 stored
```

Verified directly in the database afterwards: 5 documents, 0 malformed, 0 loopback
probes leaked. Every failure mode was also deliberately induced and confirmed to
report the correct cause: wrong password, unresolvable host, unreachable database,
silent sensor, and a publish-only credential.

**The only untested link is the physical sensor.** Everything downstream of it now
has a known-good, exercised implementation.

## To unblock

1. Bring the Pico W to a machine and run `pico_selftest.py` with `STOP_AFTER = 3`.
   This needs no accounts and no credentials, and settles whether the assembled
   hardware reads color at all. **Do this first** — it is independent of everything
   below.
2. Create the HiveMQ Cloud cluster and a credential with explicit publish *and*
   subscribe permission on `color-mixing/#` and `command/#`. Grant both; see the
   trap section above for what happens when subscribe is missing.
3. Create the MongoDB Atlas cluster, a `readWrite` user, and set network access to
   `0.0.0.0/0` (CI runners and HF Spaces have dynamic IPs).
4. Write `my_secrets.py` onto the Pico, then run the full `pico_selftest.py`.
5. Add `HIVEMQ_HOST`, `HIVEMQ_USERNAME`, `HIVEMQ_PASSWORD`, `PICO_ID`, and
   `MONGODB_CONNECTION_STRING` as repository secrets **and** to the `env:` block of
   `.github/workflows/claude.yml`. The workflow edit must be made by a human — the
   GitHub App cannot modify files under `.github/workflows/`.
6. Run `python mqtt_to_mongodb.py --loopback --expect 1` while the sensor takes a
   reading. That is the whole test.

Steps 2–5 are the infrastructure work already scoped in issue #33; step 1 is
independent and worth doing immediately.

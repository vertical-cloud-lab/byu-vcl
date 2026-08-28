# Runbook: colour-sensor read → database upload

Requested by @timothy-commins in [PR #60](https://github.com/vertical-cloud-lab/byu-vcl/pull/60):
*"run a simple test where the color sensor reads for some colors and to see if
it can upload that data to our database ... document the whole process so that
we can tell where errors occur if they show up"*.

The path from the AS7341 to the database crosses **six independent systems**:

```
 AS7341 ──I2C──> Pico W ──WiFi──> HiveMQ Cloud ──TLS──> host ──TLS──> MongoDB Atlas
   (1)             (2)      (3)        (4)                (5)              (6)
```

Any one of them can be the reason "it didn't work", and they fail in ways that
look identical from the outside — a dead sensor, a flat battery, a rotated
password and a blocked firewall all produce the same silence. So
[`read_and_upload.py`](read_and_upload.py) splits the run into numbered stages,
each printing `PASS`/`FAIL`/`WARN` and exiting with a **distinct code**. When
something breaks, the stage number tells you which of the six systems to go
look at, without guessing.

## The stages

| stage | checks | exit | a failure means |
|---|---|---|---|
| **S1** | DNS + TCP to the broker | 10 | *your host* has no route/DNS to HiveMQ (firewall, proxy, offline) |
| **S2** | TLS handshake + MQTT auth | 20 | credentials wrong/rotated, or the HiveMQ cluster is suspended |
| **S3** | subscribe to the reply topic | 30 | login accepted but the credential's ACL forbids the topic |
| **S4** | the Pico answers a read command | 40 | **the sensor side is down** — Pico off, off WiFi, or `main.py` stopped |
| **S5** | the reply is a *usable reading* | 50 | the Pico replied but the AS7341 didn't (zeros, missing channels, saturation) |
| **S6** | derive colour from the 8 channels | 60 | pure maths; only a code bug gets here |
| **S7** | write the readings to disk | 70 | disk/permissions — this is the stage that stops data being lost |
| **S8** | connect to MongoDB | 80 | `MONGODB_URI` unset/wrong, or this host's IP isn't on the Atlas access list |
| **S9** | upsert **and read back** | 90 | wrote but couldn't confirm — usually the DB user lacks `readWrite` |

Two design rules worth knowing:

1. **S7 runs before S8/S9, always.** If you pass `--upload` without `--out`,
   the script picks a filename for you. A database outage therefore costs you
   nothing but a backfill — re-run later with `--replay` and the readings land
   in Mongo unchanged.
2. **S9 verifies by reading back.** A write that reports success but can't be
   queried is not an upload. Every document carries a `reading_uid`
   (SHA-1 of `experiment_id` + counts) and is **upserted** on it, so
   re-running a backfill updates instead of duplicating — the same idempotency
   rule as `powder-doser`'s `dose_run_capture.py`.

## Running it

```bash
pip install paho-mqtt pymongo
export HIVEMQ_PASSWORD=...          # or fill in my_secrets.py
export MONGODB_URI=...              # only needed for --upload

# three readings of whatever the sensor is pointed at, stored in Mongo
python read_and_upload.py --n 3 --label "red dye, well A1" --upload

# storage half only, from readings captured earlier (backfill after an outage)
python read_and_upload.py --replay 'readings/*.json' --upload

# prove S5-S9 with no sensor and no database credentials
python read_and_upload.py --self-test
```

## Test results, 2026-08-28

Run from a GitHub Actions runner. Reproduce with the commands above.

### Acquisition half: S1–S3 pass, **S4 fails**

```
[   0.21s] S1  PASS 248cc294c37642359297f75b7b023374.s2.eu.hivemq.cloud -> 20.79.70.109, tcp/8883 open
[   0.92s] S2  PASS CONNACK=Success as user 'sgbaird'
[   1.12s] S3  PASS subscribed color-mixing/picow/test/as7341 (Granted QoS 1)
[   1.25s] S4  .... read 1/2 sent (R/Y/B=0/0/0, experiment_id=cb4ae910)
[  26.26s] S4  FAIL no reply on the data topic within 25 s
[  28.40s] S4  .... read 2/2 sent (R/Y/B=50/50/50, experiment_id=453a692b)
[  53.41s] S4  FAIL no reply on the data topic within 25 s
[  53.42s] S4  FAIL 2/2 reads timed out -- the broker accepted every command, so the Pico W never answered
EXIT=40
```

Corroborating check: subscribing to `#` **and** `$SYS/#` for 45 s returned
**0 messages** and no retained state — nothing at all is publishing to this
broker. Combined with S2/S3 passing, that isolates the fault to the device:
the credentials, broker, topics and this host's network are all fine.

**The Pico W is offline.** The last successful reading was
[2026-08-10](../camera/pickup-test-2026-08-10-full-cycle-sensor-read/), 18 days
earlier, on a 500 mAh LiPo — a flat battery is the leading hypothesis.

### Storage half: S5–S9 all pass

Verified end-to-end against a **real MongoDB 7.0.40 server**, replaying the
four genuine 2026-08-10 readings:

```
S5  PASS reading 1: 8/8 channels, none saturated
S6  PASS reading 1: #FFF985, dominant 620 nm
S7  PASS wrote 4 document(s)
S8  PASS connected to MongoDB 7.0.40
S9  PASS inserted wireless_color_sensor.sensor_readings reading_uid=cef45f71 (read-back verified)
```

Re-running the same input reports `updated` rather than `inserted` — the
idempotency rule holds.

![pipeline results](https://github.com/vertical-cloud-lab/byu-vcl/blob/5dd8776/wireless-color-sensor/sensor/renders/read_and_upload_pipeline.png?raw=true)

**The pipeline does separate colours.** Seated in its base the module reads
green (peak 550 nm, `#9FFF2D`, CCT ≈ 5400 K); lifted into the lab lighting it
reads warm yellow (peak 620 nm, `#FFF985`, CCT ≈ 3550 K). Those are two
genuinely different chromaticities recovered from real counts, which is the
cheapest available proof that the colour maths is wired up correctly.

Caveat carried in every document: eight samples is a coarse basis for a
390–830 nm integral, and the AS7341 reports **counts, not radiance**. The
colour is a *relative* estimate — good for "is this well redder than that
one" and for tracking change, not for an absolute colorimetric claim.

## Failure signatures, reproduced

Each of these was triggered deliberately, so the table above is observed
behaviour rather than a guess:

| what was broken | stage | what you see |
|---|---|---|
| `MONGODB_URI` not set | S8 | `S8 FAIL MONGODB_URI is not set` → readings still on disk from S7 |
| unreachable Mongo host | S8 | `S8 FAIL could not reach MongoDB: ServerSelectionTimeoutError` (after 15 s) |
| every channel 0 | S5 | `WARN every channel reads 0 -- the AS7341 is almost certainly not answering on I2C` |
| channels absent | S5 | `WARN missing channels: ch470, ch510, ...` |
| all channels 65535 | S5 | `WARN saturated channels (clipped, value unusable)` |
| reply with no `sensor_data` | S5 | `FAIL reply has no sensor_data object`, exit 50 |
| Pico not answering | S4 | `FAIL no reply on the data topic`, exit 40 |

The three `WARN` cases are stored with `quality.ok = false` rather than
discarded — a bad reading is itself a datum, and dropping it silently would
hide exactly the intermittent faults this instrumentation exists to catch.

## Bringing the sensor back (S4)

In order of likelihood:

1. **Charge/replace the LiPo.** Power-cycle and watch the onboard LED — it
   blinks once `main.py` is running. Dark LED = no power.
2. **Check WiFi.** `main.py` calls `connectWiFi(SSID, PASSWORD, country="CA")`
   and has *no retry* around the MQTT loop failing later — if the AP changed
   or the Pico booted out of range, it sits there doing nothing. Serial
   console shows where it stopped.
3. **Test the sensor without WiFi at all** — plug the Pico into USB and run
   [`collect_over_serial.py`](collect_over_serial.py). That bypasses stages
   1–4 entirely and tells you whether the AS7341 itself is alive. Plugging it
   into the RPi-5 (already on the tailnet next to the OT-2) makes this
   remotely triggerable.

## Known gaps

- **`MONGODB_URI` is not available to this repo's Actions workflow.** The VCL
  Atlas cluster is wired into `powder-doser`'s workflow (`MONGODB_URI`,
  `MONGODB_USERNAME`, `MONGODB_PASSWORD`, `PI_MONGODB_URI`) but `byu-vcl`'s
  `claude.yml` doesn't pass any of them, so a CI run can reach S7 but never
  S8. Adding `MONGODB_URI` (and `HIVEMQ_PASSWORD`) to this repo's secrets
  closes the loop. Atlas also denies unknown IPs — an Actions runner needs
  `0.0.0.0/0` on the access list or a fixed egress.
- **The HiveMQ credentials are published in a public repo.** Host, username
  *and password* are committed in
  `sensor_file/test_sensor.ipynb` upstream, so anyone can publish to the
  command topic and drive this device. Worth rotating and moving to secrets.
- **The firmware returns only the 8 spectral channels** — no `clear`, `nir`,
  flicker, gain or integration time. Documents record this under
  `fields_not_reported` so a consumer never mistakes "absent" for "zero".
  Widening it is a one-function change in `main.py` (see [README](README.md)).
- **Pose dominates the raw counts** (the 550 nm ↔ 620 nm split above is
  *entirely* pose, not chemistry). Any real colorimetric protocol has to read
  at a fixed height with fixed illumination, or the sample's contribution is
  swamped.

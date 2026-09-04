# Wireless color sensor — verified state

Results of a live hardware session on 2026-09-04, run from GitHub Actions against the
physical board (`PICO_ID` `e6647c15673a2438`) over Tailscale → the stream-cam Pi → USB.
Everything below was executed, not inferred.

## The chain works

| Link | Result |
| --- | --- |
| AS7341 on I2C0 GP4/GP5 | answers at `0x39`, part number register `0x92` reads `0x24` |
| Reads light | dark total **416** counts → LED-lit total **436,935**, a **1000×** response |
| Returns to baseline | LED off again → **414**, so the response is the light, not drift |
| WiFi (WPA2, 2.4 GHz) | associates, DHCP lease obtained |
| NTP | clock set from `time.google.com` |
| TLS + broker | connects to the BYU VCL HiveMQ cluster, cert validates |
| Publish + round trip | reading published to `color-mixing/picow/<PICO_ID>/as7341` and delivered back |

The sensor package is not broken. Nothing in the hardware or the network path needs fixing.

## Why it looks like it "isn't reading color"

`main.py` boots, connects to the broker, and reports this for a reading:

```
{ch410: 6, ch440: 4, ch470: 9, ch510: 164, ch550: 169, ch583: 35, ch620: 16, ch670: 12}
```

Near zero on every channel — because **nothing turns a light on**. In `read_sensor_data()`
both `sensor.LED = True` and `sensor.LED = False` are commented out, and in
`run_color_experiment()` so is `set_color(R, Y, B)`. Sealed inside the enclosure, a healthy
AS7341 correctly reports that it is dark in there.

Three separate faults sit behind that single symptom:

1. **The sensor LED is commented out.** Uncommenting `sensor.LED = True` in
   `read_sensor_data()` takes the same board from 416 counts to 436,935.
2. **`set_color` is never defined.** `NeoPixel` is imported at the top of `main.py` and then
   never instantiated, and no `set_color` function exists anywhere on the board. The call is
   commented out at the one site that uses it — which is the only reason the R/Y/B command
   does not raise `NameError`. The colors in an incoming command are currently ignored.
3. **The stock gain saturates.** `Sensor()` defaults to `gain=128`. Lit, every channel pins
   at 65535, so consecutive readings are identical no matter what is in front of the sensor:

   ```
   gain    415    445    480    515    555    590    630    680
      2    121    798   1003   1024   1207   1174   1290    972
      4    468   3112   3904   3990   4699   4579   5021   3791
      8   7371  48744  61155  62646  65535  65535  65535  59593   SATURATED
    128   7375  48752  61164  62648  65535  65535  65535  59593   SATURATED
   ```

   **Use `gain=4`.** Counts scale cleanly between gain 2 and 4, so the sensor is linear in
   that range; 8 and above are unusable with the LED on.

## Do not judge the board while it is plugged into the Pi

Reset with USB enumerated and nothing draining the serial port, then check 45 s later:

```
WLAN active   : False
WLAN connected: False
```

`main.py` never even reaches `connectWiFi`. It prints continuously, the RP2040 CDC TX buffer
fills, and `print()` blocks forever. Under `mpremote run` a host is draining that buffer and
the identical code runs fine — which makes this look like an intermittent network fault. On
battery or a plain USB charger, MicroPython discards stdout and it behaves normally.

**Consequence: while the board sits on the Pi's USB port, it is not on the broker at all.**
Subscribing and seeing nothing does not mean the sensor is broken.

## The Colab notebook's defaults no longer match this board

`AccelerationConsortium/wireless-color-sensor/sensor_file/test_sensor.ipynb` defaults to the
Acceleration Consortium's broker with `PICO_ID = "test"`. This board is provisioned for the
**BYU VCL** broker with `PICO_ID = e6647c15673a2438` and `COURSE_ID = byu-vcl`. Subscribing
to `#` on the AC broker for four minutes returns nothing from it — right question, wrong
address. Set both fields in the notebook, or it will look dead while working fine.

That notebook also carries a working HiveMQ username and password in plain text in a public
repository. Worth rotating.

## Running the checks

Address the board by USB serial, never by `/dev/ttyACM*` — a second Pico and, at times, an
Arduino share that Pi, and `mpremote`'s auto-connect grabs the first one it finds.

```bash
MP=~/.venvs/mpremote/bin/mpremote
$MP connect id:e6647c15673a2438 reset
$MP connect id:e6647c15673a2438 run board_diagnose.py    # no credentials, no network
$MP connect id:e6647c15673a2438 run board_e2e_mqtt.py    # uses the board's own credentials
```

Reset before `board_diagnose.py`. Register access works from a clean boot, but re-muxing
I2C0 onto other pins latches the bus: `scan()` keeps ACKing `0x39` while every register read
returns `OSError(5)`, at any bus speed. That is indistinguishable from a dead sensor and cost
time in this session. `SoftI2C` still works in that state and clears it; so does a reset.

## What is still missing

- **Nothing subscribes on the cloud side.** The sensor publishes MQTT and stops there. No
  MQTT→MongoDB bridge is running, so a reading reaching the broker still lands in no database.
- **PR #194 is not merged.** `issue_comment` runs use the workflow from the default branch,
  so until it lands on `main` no agent session gets `MQTT_*` or `MONGODB_*` — the broker can
  only be reached from the board's side, as `board_e2e_mqtt.py` does.

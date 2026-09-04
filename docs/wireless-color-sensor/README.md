# Wireless color sensor — reaching the board

The Pico W (`PICO_ID = e6647c15673a2438`) is no longer plugged into a USB host.
It runs from a charger, so the old `mpremote`-over-USB route is gone and there
are exactly two ways to reach it:

| route | needs | status |
| --- | --- | --- |
| IP layer (ping) | nothing but same-subnet access | **works today** |
| MQTT broker | BYU VCL HiveMQ credentials | blocked — see below |
| USB / `mpremote` | board plugged into a tailnet machine | gone by design |

The board runs no listening services (no SSH, no web server), so the IP layer
tells you only whether it is alive. Everything else goes through the broker.

## Checking the board is alive — no credentials needed

Run from a machine on the same lab subnet (`10.60.0.0/17`), e.g. a stream-cam Pi:

```bash
./board_network_probe.sh            # defaults to 10.60.98.128
```

This distinguishes the two situations that otherwise look identical: *the board
is dead* versus *the board is fine but we cannot hear it*. Identification relies
on a TTL of 255 (MicroPython's lwIP stack; Linux answers 64) plus the absence of
any open port, which is what separates the Pico W from the several Raspberry Pi
Linux machines sharing the same `88:a2:9e` OUI on this network.

Verified against the live board and two negative controls (a Linux Pi, and an
unused IP); both controls are correctly rejected.

## Measured 2026-09-04

```
=== probing 10.60.98.128 ===
  PASS  reachable, 0% packet loss     (90/90 packets, rtt avg 7.2 ms)
  PASS  ttl=255 -- microcontroller (lwIP) stack, not Linux
  PASS  no listening ports, as expected for the Pico W
  PASS  MAC 88:a2:9e:16:48:b6 is a Raspberry Pi OUI
```

Moving the board off the Pi and onto a charger **fixed** the fault recorded on
2026-09-04 earlier, where the board reported `WLAN active: False` and never
reached `connectWiFi`. That was a full USB CDC buffer: with a USB host attached
but nothing draining the serial port, `print()` inside `main.py` blocks forever.
A charger supplies power without enumerating a CDC endpoint, so nothing blocks.

**Test the wireless path on a charger or battery, never plugged into the Pi.**

## Why readings still cannot be collected from CI

The board publishes to the **BYU VCL** HiveMQ broker. Subscribing requires
`MQTT_BROKER` / `MQTT_USERNAME` / `MQTT_PASSWORD` / `PICO_ID`, which are added to
the workflow's `env:` block by PR #194 — still open. `issue_comment` runs always
use the workflow from `main`, so no agent session can subscribe until it merges.

Confirmed the board is *not* on the Acceleration Consortium broker: subscribing
there to `#` for 120 s with the board powered and on Wi-Fi returned only our own
messages. A loopback probe passed in the same run, so the silence was the
board's absence from that broker, not a subscription permission problem.

Topics (from PR #194):

```
command/picow/<PICO_ID>/as7341/read     <- send a read command here
color-mixing/picow/<PICO_ID>/as7341     <- readings come back here
```

## Known firmware faults, still unfixed

Reaching the board is separate from it producing useful numbers. On the board:

1. `sensor.LED = True` is commented out in `read_sensor_data()`, so readings are
   ambient light only.
2. `set_color` is never defined and no NeoPixel is wired — the R/Y/B values in a
   command are ignored.
3. The driver default `gain=8` saturates every channel when lit; use `gain=4`.

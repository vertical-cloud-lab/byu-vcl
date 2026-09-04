# Wireless color sensor — MQTT to MongoDB

Verified working on 2026-09-04 from a GitHub Actions runner, after the credentials
in PR #194 reached `main`. The whole chain runs unattended:

```
CI runner --TLS--> HiveMQ Cloud --WiFi--> Pico W (AS7341) --> HiveMQ --> CI runner --> MongoDB
```

The board answers in **~1.4 s**, every time, with all eight spectral channels.
Nothing is plugged into it but a charger.

## Running it

```bash
pip install paho-mqtt pymongo
python sensor_collect.py --colors dark,red,yellow,blue,white
python sensor_collect.py --repeat 10 --no-store     # bench check, no database
```

Needs `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `PICO_ID`,
and `MONGODB_URI` / `MONGODB_DATABASE` unless `--no-store`.

## Battery power: 2026-09-04 19:00 UTC — the board went silent

After the LiPo SHIM was soldered on and the board moved from a charger to battery
alone, it stopped answering. The broker is not implicated; the board is simply not
running. Evidence, each layer with its own positive control:

| Layer | Result | Control that rules out a false negative |
| --- | --- | --- |
| Broker connect / subscribe | `CONNACK Success`, `Granted QoS 1` | — |
| Broker delivery to us | **PASS** | our own probe echoes back off `.../_probe` |
| Read commands | **0 replies from 14 commands** over ~11 min | our own commands echo back on `#` throughout |
| Any traffic on `#` | **0 messages** in 90 s | — |
| Board at its last IP `10.60.98.128` | **0/13 packets** | the gateway answers 3/3 from the same host |
| Board MAC `88:a2:9e:16:48:b6` | **absent** from a full `10.60.0.0/17` sweep | the sweep found two other `88:a2:9e` Pis `REACHABLE` |
| Pico on USB anywhere | none on either stream-cam Pi | — |

The comparison that localises it — same broker, same credentials, same firmware,
**one variable changed**:

| Time (UTC) | Power source | Result |
| --- | --- | --- |
| 16:28 | charger, no data host | 17/17 replies, ~1.4 s each, 7 documents in `sensor-data` |
| 19:00–19:11 | battery via LiPo SHIM | 0/14 replies, absent from the wifi |

So the failure arrived with the power change, not with the network or the code.

### Where to look first

The board never joins wifi, which puts the fault before `connectWiFi` — i.e. in
power, not configuration:

1. **The SHIM's power button.** The Pimoroni LiPo SHIM comes up *off* when a battery
   is connected; a short press switches it on and a long press switches it off. A
   board that was never switched on behaves exactly like this.
2. **Charge state.** The SHIM only charges the cell over the Pico's own micro-USB, so
   a battery that has never been plugged in sits at shipping charge. The Adafruit 1317
   is **150 mAh**, and a Pico W holding a wifi association draws roughly 50–70 mA, so a
   full cell is worth only about two hours and a partial one considerably less.
3. **Brownout on the radio.** The Pico W's current spikes when the transmitter keys up.
   A small or depleted cell sags under that load, resetting the board *at the moment it
   tries to associate* — which produces this exact signature: never on the network,
   never on the broker, no matter how long you wait.
4. **The SHIM joints.** All pads need continuity, `VSYS` and `GND` especially. An
   earlier SHIM in this thread was soldered a couple of millimetres out of position.

Distinguishing 1–3 from 4 is a two-minute test: plug the Pico into a USB charger and
leave it an hour, then re-run `board_triage.py`. If it answers, the assembly is sound
and the cell was flat; if it stays silent on the charger, suspect the joints.

## Triage

`board_triage.py` reports which link is broken rather than that something is:

```bash
python board_triage.py                 # broker + board
python board_triage.py --lan-check     # add the wifi check; run from the lab LAN
```

It separates the three causes that look identical from a distance — broker refusing
to deliver, board off the network, board on the network but not publishing — and each
verdict names the next thing to check. Exercised against the live silent board on
2026-09-04; the LAN branch was run from the stream-cam Pi with the gateway as a
positive control.

## Data hygiene note

Four of the seven documents in `sensor-data` were written by an ad-hoc script and
carry `total_counts: None`. Readings written by `sensor_collect.py` populate it.
Worth normalising before anyone aggregates that collection.

## The command payload shape matters

The firmware indexes the incoming JSON like this:

```python
command = incoming_dict["command"]
experiment_id = incoming_dict["experiment_id"]
R = command["R"]; Y = command["Y"]; B = command["B"]
```

so a command must be nested:

```json
{"command": {"R": 255, "Y": 0, "B": 0}, "experiment_id": "anything"}
```

A flatter payload such as `{"R": 0, "Y": 0, "B": 0}` raises `KeyError` **inside the
board's handler**, where a bare `except` swallows it. The board prints a traceback to
a serial port nobody is reading and publishes nothing — indistinguishable, from the
subscriber's side, from a board that is switched off. This cost a session.

## `--loopback` is not optional

A broker can answer `SUBACK: Granted QoS 1` and then deliver nothing, when the
credential has publish but not subscribe permission. That also looks exactly like a
silent sensor. `sensor_collect.py` always echoes a probe off its own topic first, so
a broker permission problem reports itself as one instead of sending you to the bench.

## Measured: the commanded colour does nothing

Ten readings, alternating `R=Y=B=0` and `R=Y=B=255`, five each:

| chan | OFF mean | MAX mean | diff | within-group sd |
| --- | ---: | ---: | ---: | ---: |
| ch410 | 91.8 | 92.0 | +0.2 | 0.40 |
| ch440 | 293.0 | 293.0 | 0.0 | 0.00 |
| ch470 | 342.0 | 342.0 | 0.0 | 0.00 |
| ch510 | 747.4 | 747.4 | 0.0 | 0.49 |
| ch550 | 1092.0 | 1092.0 | 0.0 | 0.00 |
| ch583 | 1290.0 | 1289.8 | −0.2 | 0.40 |
| ch620 | 1365.4 | 1365.4 | 0.0 | 0.49 |
| ch670 | 858.6 | 858.2 | −0.4 | 0.49 |

Both groups produce the same three total values — `{6079, 6080, 6081}`. Every
difference is smaller than the noise within a single group, so the commanded colour
has no measurable effect at all.

That ±1 count jitter is itself a useful control: it means each reply is a **fresh
conversion**, not a cached or retained value being replayed. The sensor is genuinely
sampling; it is measuring ambient room light and ignoring the command.

## Why — three firmware faults, none of them hardware

1. **`sensor.LED = True` is commented out** in `read_sensor_data()`, so every reading
   is ambient light. With that line restored, earlier bench measurements over USB went
   from 416 to 436,935 total counts.
2. **`set_color` is never defined and no NeoPixel is wired.** `NeoPixel` is imported at
   the top of `main.py` and never instantiated. Driving all 24 usable GPIO pins produced
   no response from the sensor, so the R/Y/B fields have no hardware behind them on this
   build. Fixing the firmware alone will not make commanded colour work.
3. **The driver default `gain=8` saturates** once anything is lit — several channels pin
   at 65535 and different samples return identical numbers. Use `gain=4`; counts scale
   linearly from gain 1 through 4.

Fault 1 is a one-line firmware change. Fault 3 is a one-argument change. Fault 2 needs
an illumination source physically added, or the RGB command dropped from the interface.

## Keep the board off USB

Plugged into a Pi with nothing draining the serial port, `main.py` fills the RP2040 CDC
TX buffer and `print()` blocks forever — the board wedges before it ever reaches
`connectWiFi`, and looks like a network fault. On a charger it behaves correctly, which
is how it is deployed now. Verify the MQTT path on its own power, never on the Pi.

## What is not yet proven

The sensor measures eight bands reproducibly and reports them over the wireless path.
It has **not** been shown to distinguish two different coloured samples — that needs
someone to physically place samples in front of it, and cannot be done from CI.

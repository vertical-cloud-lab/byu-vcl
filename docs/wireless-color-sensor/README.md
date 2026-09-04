# Wireless color sensor — battery operation verified

Live results from CI, 2026-09-04 22:18 UTC, with the Pico W running from the LiPo
SHIM and battery alone — no USB, no wired power.

## Result

The full chain works with nothing physically attached to the board:

```
CI runner ──TLS──▶ HiveMQ Cloud ──▶ Pico W (battery) ──▶ AS7341 read
                        ◀── reading ──┘        └──▶ MongoDB (digital-wetlab.sensor-data)
```

| Check | Result |
| --- | --- |
| Broker CONNACK / SUBACK | Success / Granted QoS 1 |
| Loopback probe (positive control) | PASS |
| Colour sweep | **5 / 5** replies, 1.35–1.45 s |
| Stability burst, 45 s continuous | **10 / 10** replies, 0 missed |
| Latency across all 15 | min 1.35 s, median 1.35 s, max 1.45 s |
| Reading spread over the burst | 789–791 counts, **0.25 %** |
| MongoDB | 5 documents written and read back |

## Power source is what changed

Nothing else did — same broker, same credentials, same firmware, same board.

| Time (UTC) | Power | Replies |
| --- | --- | --- |
| 16:28 | USB charger | 17 / 17 |
| 19:00–19:11 | battery, freshly soldered SHIM | **0 / 14** |
| 22:18 | battery | **15 / 15** |

The 19:00 silence was a power state, not a soldering fault. The SHIM joints are good.

## Still outstanding: the reading does not respond to the commanded colour

Every reply in the colour sweep came back at the same total (790 ± 1) whether the
command asked for dark, red, green, blue or white. Three firmware faults sit behind
this, all measured earlier on 2026-09-04 and all still unfixed:

| # | Fault | Effect |
| --- | --- | --- |
| 1 | `sensor.LED = True` is commented out in `read_sensor_data()` | The AS7341 reads ambient light only. Restoring the line took totals from 416 to 436 935. |
| 2 | `set_color` is never defined and no NeoPixel is wired | The R/Y/B values in a command are silently ignored. A pin sweep of all 24 usable GPIOs produced no sensor response. |
| 3 | Driver default `gain=8` saturates when lit | Channels pin at 65535, so different samples return identical numbers. Use `gain=4`. |

Fault 2 needs hardware, not a code change.

## Payload format — the trap

The firmware indexes a **nested** payload. A flat one raises `KeyError` inside the
handler, where a bare `except` swallows it; the board then publishes nothing and
looks identical to a board that is switched off.

```python
{"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": "..."}   # correct
{"R": 0, "Y": 0, "B": 0}                                        # silently ignored
```

## Keep the board off USB

Plugged into a Pi with nothing draining the serial port, `main.py` fills the USB CDC
buffer and `print()` blocks before it ever reaches `connectWiFi`. The board looks dead
while being perfectly healthy. On battery or a plain charger, MicroPython discards
stdout and it runs normally.

## Running the test

```bash
pip install paho-mqtt pymongo
python sensor_quick_test.py     # needs MQTT_BROKER/PORT/USERNAME/PASSWORD and PICO_ID
```

It always runs the loopback probe first, so a broker permission problem names itself
instead of being mistaken for a silent board.

# Wireless color sensor — what the readings mean

Correction to earlier notes on this branch's predecessors, plus the measurements
behind it. All figures were taken on 2026-09-04 with the Pico W running from the
LiPo SHIM and battery alone.

## Identical readings across a colour sweep are correct, not a fault

Earlier write-ups listed "the reading does not respond to the commanded colour"
as an outstanding fault. That was the wrong reading of the design. **In this
deployment the `R`, `Y`, `B` values in a command are metadata, not instructions
to the sensor.**

Three things in the upstream firmware say so directly:

| Evidence in [`sensor_file/main.py`](https://github.com/AccelerationConsortium/wireless-color-sensor/blob/main/sensor_file/main.py) | |
| --- | --- |
| `# Dummy function for running a color experiment` | the comment on `run_color_experiment` itself |
| `# set_color(R, Y, B)` and `# clear_color()` | both commented out; neither function is defined anywhere on the board |
| topic `command/picow/{PICO_ID}/as7341/read` | the command is named *read* |

And the values are echoed straight back beside the reading:

```python
payload_data = incoming_dict.copy()
payload_data.update({"sensor_data": sensor_data})
```

That is what you do with a label. `R`/`Y`/`B` are red, yellow and blue — the
*subtractive* primaries of dye mixing, describing what the OT-2 dispensed into
the well, not an additive R/G/B colour for an emitter. A stationary sensor over
an unchanged well returns the same numbers, and should.

## The control that proves the sensor is not simply stuck

Both explanations — "the sensor is stuck" and "nothing in front of it changed" —
predict identical numbers, so a colour sweep cannot tell them apart. Changing
the light while the sensor stays still can. The AS7341's own LED is driven over
I²C, so this needs no motion at all:

| reading | 410 | 440 | 470 | 510 | 550 | 583 | 620 | 670 | total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LED off | 1 | 2 | 2 | 13 | 15 | 7 | 7 | 5 | **52** |
| LED on | 498 | 3331 | 4179 | 4197 | 4920 | 4815 | 5287 | 4001 | **31228** |
| LED off | 1 | 2 | 2 | 13 | 15 | 7 | 7 | 5 | **52** |
| LED on | 497 | 3330 | 4177 | 4194 | 4915 | 4810 | 5281 | 3997 | **31201** |

600×, and the dark baseline returns bit-identical both times (`gain=4`, stored in
`digital-wetlab.sensor-data` as `usb-wireless-*`). The sensor registers a change
with a completely static scene, so identical numbers across a colour sweep mean
the *illumination and the sample* did not change — which is the expected result.

## What is still worth fixing: the readings are of ambient room light

This survives the argument above, because it is about the baseline rather than
about motion. `sensor.LED = True` is commented out in `read_sensor_data()`, so
every reading over MQTT measures whatever the room is doing.

Two timescales, both with the board untouched on battery:

| | total counts |
| --- | --- |
| within one burst, over seconds | **770 ± 1** (0.12 % spread, 8/8 replies) |
| 22:12 → 22:18 → 22:35 UTC | **810 → 790 → 770** |

The drift between bursts is roughly 40× the noise floor within one. Nothing was
moved and no command differed; the room changed. Read well A at 22:12 and well B
at 22:35 and you would attribute a 5 % baseline shift to the sample.

Turning the sensor LED on removes the room from the measurement — a lit reading
is ~600× ambient, so ambient contributes about 0.2 %.

| change | effect |
| --- | --- |
| uncomment `sensor.LED = True` (and the matching `= False`) in `read_sensor_data()` | the measurement becomes self-illuminated instead of tracking the room |
| pass `gain=4` | `gain=8` pins channels at 65535 once lit, making every sample read identically |

That second one only matters once the LED is on. Unlit at `gain=4` the sensor is
nowhere near saturation (max channel 224 of 65535).

Both are edits to `main.py` on the board, which needs a USB host briefly — and
the board should go straight back onto battery afterwards, since plugged into a
Pi with nothing draining the serial port `main.py` fills the USB CDC buffer and
`print()` blocks before it ever reaches `connectWiFi`.

## Illumination is a design decision, not a missing part

`set_color` having no NeoPixel behind it is not a defect of this build. The
device is a passive reader; the light has to come from somewhere else. Two paths
are open, and they are not equivalent:

- **Reflectance** — the AS7341's own LED, already on the board, already proven
  above. Nothing to buy.
- **Transmission** — illuminate the well plate from below, which is the
  screen-mount idea in [this
  comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/33#issuecomment-3915224309).
  Better suited to reading liquid colour, and needs hardware.

## Payload format — the trap

The firmware indexes a **nested** payload. A flat one raises `KeyError` inside
the handler, where a bare `except` swallows it; the board then publishes nothing
and looks exactly like it is switched off.

```python
{"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": "..."}   # correct
{"R": 0, "Y": 0, "B": 0}                                        # silently ignored
```

## Scripts

```bash
pip install paho-mqtt pymongo

# characterise the noise floor and compare against earlier bursts
python static_scene_check.py --repeat 8 --history

# command the board and store readings in MongoDB
python sensor_collect.py --colors dark,red,yellow,blue,white
```

Both publish a probe to their own topic first. A broker can grant a subscription
and then deliver nothing when the credential lacks read permission, which is
indistinguishable from a silent board; the probe tells those apart.

Needs `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `PICO_ID`,
and for storage `MONGODB_URI` / `MONGODB_DATABASE`.

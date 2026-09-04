# Wireless color sensor — MQTT to MongoDB

Verified working on 2026-09-04 from a GitHub Actions runner, after the credentials
in PR #194 reached `main`. The whole chain runs unattended:

```
CI runner --TLS--> HiveMQ Cloud --WiFi--> Pico W (AS7341) --> HiveMQ --> CI runner --> MongoDB
```

The board answers in **~1.4 s**, every time, with all eight spectral channels.
Nothing is plugged into it but a charger.

> **Current status (2026-09-04 21:40 UTC): broken at the sensor.** `GP5`, the I²C
> clock line, is shorted to ground, so the AS7341 cannot be reached and `main.py`
> aborts before it starts the radio. See the root-cause section below; the pipeline
> itself is unchanged and works the moment the board reads again.

## Running it

```bash
pip install paho-mqtt pymongo
python sensor_collect.py --colors dark,red,yellow,blue,white
python sensor_collect.py --repeat 10 --no-store     # bench check, no database
```

When the board answers nothing at all, start on the board itself instead — this
needs no credentials and no network, and it separates a wiring fault from a
software one:

```bash
mpremote connect id:e6647c15673a2438 run board_pin_short_scan.py
```

Needs `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`, `PICO_ID`,
and `MONGODB_URI` / `MONGODB_DATABASE` unless `--no-store`.

## 2026-09-04 21:40 UTC — root cause found: `GP5` (SCL) is shorted to ground

The board was plugged into the RPi 5 stream-cam Pi and reached over USB. It is
healthy in every respect except one: **physical pin 7 — `GP5`, the I²C clock line
to the STEMMA QT connector — is held at ground.** With SCL clamped low the master
can never clock, so the AS7341 cannot be reached at all.

This supersedes the battery-power explanation below. It is a single root cause for
both symptoms, and every link was measured rather than inferred.

### The scan

`board_pin_short_scan.py`, run on the board. Every one of the 26 header GPIOs was
tested by fighting it with the RP2040's internal pull-up and pull-down in turn:

```
GPIO   phys pin  verdict                  adj GND pin   role
GP4    pin 6     EXTERNAL PULL-UP                       I2C0 SDA -> STEMMA QT
GP5    pin 7     *** SHORTED TO GND ***   8             I2C0 SCL -> STEMMA QT
...    (all 24 others: floating (open))
```

Two readings matter, and they point in opposite directions:

| Pin | Reading | What it proves |
| --- | --- | --- |
| `GP4` / SDA | external pull-up wins against the internal pull-down | the AS7341 breakout **is powered** and the STEMMA QT cable **is intact** — that pull-up is its own 10 kΩ to 3V3 |
| `GP5` / SCL | reads 0 even with the internal pull-up on | something a few kΩ or less is tying it to ground |

`GP5` is physical pin 7; physical pin 8 is `GND`, immediately adjacent, on the same
header row that was just soldered. A bridge between those two pads produces exactly
this reading. **Confirm with a multimeter, power off: pin 7 to pin 8 should be open,
not a few ohms.** Reflow the joint and clean the flux.

### Confirmations

| Check | Result | Runs |
| --- | --- | --- |
| `GP5` shorted, `GP4` pulled up | identical every time, including after a hard `machine.reset()` | 4 |
| `i2c.scan()` on `I2C(0)` GP4/GP5 | empty | 6+ |
| Sweep of all 12 hardware I²C pin pairs + `SoftI2C` | nothing on any bus | 1 full sweep |
| Every register access | `OSError: [Errno 110] ETIMEDOUT` | every attempt |

The sweep matters: it rules out "the sensor moved to different pins" rather than
assuming the wiring is what the code says.

### Why the board also vanished from the network

`main.py` builds the sensor at import time, on line 65, *before* it touches wifi:

```python
sensor = Sensor(i2c=I2C(0, scl=Pin(5), sda=Pin(4)))   # line 65
...
connectWiFi(SSID, PASSWORD, country="CA")             # line ~93 — never reached
```

Running the board's own `main.py` under `mpremote` confirms it dies there:

```
Failed to contact AS7341 at I2C address 0x39
Traceback (most recent call last):
  File "<stdin>", line 65, in <module>
  File "/lib/as7341_sensor.py", line 60, in __init__
ExternalDeviceNotFound: Failed to contact AS7341, terminating
```

So **a dead I²C line looks exactly like a dead radio.** The board never joins wifi,
never reaches the broker, and answers no commands — with nothing wrong with the
radio, the credentials, the network or the power.

And the radio is provably fine. Skipping the sensor entirely and calling
`connectWiFi` directly, on the same board, minutes later:

```
MAC address: 88:a2:9e:16:48:b6
connected
ip = 10.60.98.128
ifconfig : ('10.60.98.128', '255.255.128.0', '10.60.0.1', '10.8.0.8')
```

Same MAC, same address it has always held. Note the ordering trap this creates:
the LAN sweeps recorded below correctly found no board on the network, and that was
read as a power failure. It was the sensor stopping the program before the radio
ever started.

### Timeline

| Time (UTC) | Event | Sensor |
| --- | --- | --- |
| 16:26–16:28 | 17/17 MQTT replies, 7 documents written to `sensor-data` | reading |
| ~18:51 | LiPo SHIM soldered onto the Pico W | — |
| 19:00–19:40 | 0 replies from 26 commands; board absent from the LAN | not reading |
| 21:40 | reached over USB: `GP5` shorted, `main.py` aborts at line 65 | not reading |

The last known-good readings are still in the database and were re-queried this
session, so the "worked at 16:28" end of the comparison is independently recorded
rather than remembered.

### What this does not say

The wifi test above was run on USB power. It shows the radio and credentials are
sound and that the silence needs no power explanation — it does **not** independently
re-test the battery path. Fix the short first; if the board then answers on a charger
but not on the cell, the battery reasoning below becomes relevant again.

---

## Battery power: 2026-09-04 — the board went silent (superseded)

> **Superseded by the section above.** The board is silent because `main.py`
> aborts at the sensor before it reaches `connectWiFi`, on any power source.
> The observations here are accurate and the controls are worth keeping; the
> conclusion drawn from them — that power was the fault — was wrong.


After the LiPo SHIM was soldered on and the board moved from a charger to battery
alone, it stopped answering, and it has stayed silent across two sessions. The broker
is not implicated; the board is simply not on the network.

The comparison that localises it — same broker, same credentials, same firmware,
**one variable changed**:

| Time (UTC) | Power source | Result |
| --- | --- | --- |
| 16:28 | USB charger, no data host | 17/17 replies, ~1.4 s each, 7 documents in `sensor-data` |
| 19:00–19:11 | battery via LiPo SHIM | 0 replies from 14 commands |
| 19:22–19:40 | battery, SHIM confirmed switched on | 0 replies from 12 commands |

Evidence, each layer with its own positive control:

| Layer | Result | Control that rules out a false negative |
| --- | --- | --- |
| Broker connect / subscribe | `CONNACK Success`, `Granted QoS 1` | — |
| Broker delivery to us | **PASS**, every attempt | our own probe echoes back off `.../_probe` |
| Read commands | **0 replies from 26** across two sessions | our own commands echo back throughout |
| Board at its last IP `10.60.98.128` | **0/8 packets** | the gateway answers 3/3 from the same host |
| Board MAC `88:a2:9e:16:48:b6` | **absent** from a full `10.60.0.0/17` sweep | the sweep found two other `88:a2:9e` Pis `REACHABLE` |
| Any lwIP (TTL 255) host on the subnet | one, MAC `1c:90:ff:…` — **not** a Raspberry Pi OUI | the sweep does detect TTL-255 hosts, so it would have found the board |
| Pico on USB anywhere | none on either stream-cam Pi | — |
| Newest document in `sensor-data` | 3.2 h old at 19:40 | database reachable, `ping → {'ok': 1}` |

So the failure arrived with the power change, not with the network or the code.

### What the two LEDs do and do not tell you

Both indicators being lit is what makes this confusing, so it is worth being precise
about what each one actually reports. Per
[Pimoroni](https://shop.pimoroni.com/products/pico-lipo-shim), the SHIM has
"a white one that shows when the shim is providing power and a red one to tell you
when the battery is being charged."

| Indicator | Proves | Does **not** prove |
| --- | --- | --- |
| SHIM **white** LED | the SHIM is switched on and delivering power | that the RP2040 is executing anything |
| AS7341 **green** LED | the Pico's 3V3 rail is up | that the RP2040 is executing anything |
| SHIM **red** LED | the cell is charging (USB present) | — |
| Pico's own onboard LED | RP2040 running **and** the CYW43 wifi chip initialised | — |

The white LED does settle one thing: the SHIM's power button is on, so "never switched
on" is ruled out. (The button is a plain toggle on a quick press-and-release, and it
retains its last state — there is no separate long-press to switch off.)

But neither the white nor the green LED says anything about code. The Pico's 3V3
regulator is a **buck-boost** part specified from 1.8 V input, so it holds 3V3 — and
therefore both LEDs — steady on a cell discharged well below the point where the wifi
radio can be supported. **A nearly flat battery looks exactly like a healthy one from
the outside.** Worse, a buck-boost converter draws *more* input current as its input
voltage falls, so a weak cell is loaded hardest precisely when the transmitter keys up.

The one indicator that would distinguish "running" from "powered" is the Pico's own
onboard LED, and on a Pico W that LED hangs off the CYW43 wifi chip — so it cannot
light at all until the radio initialises.

### Ranked causes, and the test that separates them

The board never joins wifi, which puts the fault before `connectWiFi` — in power or
in execution, not in configuration:

1. **The cell is flat.** The SHIM charges only over the Pico's own micro-USB, through
   an MCP73831 at 215 mA. A battery that has not been plugged in since assembly sits at
   whatever charge it had after months on a shelf. The Adafruit 1317 is **150 mAh** and
   a Pico W holding an association draws roughly 45–70 mA, spiking higher, so a full
   cell is worth only about two hours and a depleted one nothing useful.
2. **Brownout as the radio keys up.** A sagging cell resets the board *at the moment it
   tries to associate*, which reproduces this signature exactly: never on the network,
   never on the broker, however long you wait — and, because the reset cycle is
   milliseconds, both LEDs look continuously lit throughout.
3. **A SHIM joint that is fine at idle and marginal under load.** Tens of milliamps of
   LED current prove far less about a joint than a 150 mA radio burst does. `VSYS` and
   `GND` especially.
4. **The board is not running MicroPython** — sitting in the ROM bootloader, which the
   SHIM button can reach when double-pressed with `BOOTSEL` held.

**One test separates 1–3 from 4, and grades the battery at the same time:** connect the
Pico's micro-USB to a plain wall charger with the battery still attached, and watch the
red LED.

| Observation | Reading |
| --- | --- |
| Red LED lights and stays on for tens of minutes | the cell really was flat — cause 1 |
| Red LED off, or out within a minute or two | the cell was already full — look at 3 and 4 |
| Board answers on the broker while on USB | the assembly is sound; this is the configuration that worked at 16:28 |
| Board still silent **on USB** | not a battery problem — the soldering changed something |

Use a wall charger rather than a stream-cam Pi for that test, for the CDC reason below —
unless the intent is also to push firmware, in which case the Pi is the right choice and
charges the cell over the same cable.

## Wireless charging is not the same as a wired charger

> Kept for reference. This was written while power was still the leading
> hypothesis; the fault turned out to be the shorted SCL line. The pin-by-pin
> account of the SHIM below is accurate and worth having.

Raised on 2026-09-04: *"currently the wireless color sensor is being charged wirelessly
so it would be the equivalent as if it were plugged into a power source as done
previously."* Half of that is right, and the half that is wrong is worth being precise
about, because it changes which test is meaningful.

**Right:** a Qi receiver is a dumb power source with no USB data lines, so it does *not*
reproduce the CDC-buffer wedge described below. On that axis it behaves like a wall
charger, not like a Pi.

**Wrong:** charging and running are different functions on different pins, and the
wireless link is the least reliable way to deliver either.

### The power path, pin by pin

The [assembly instructions](https://accelerationconsortium.github.io/wireless-color-sensor/)
wire the Qi receiver to **VBUS (pin 40)** and **GND (pin 38)**. Pimoroni's own
[account of which pins the SHIM uses](https://forums.pimoroni.com/t/pico-lipo-shim-used-pins/21995)
says what each one is for:

| Pin | Name | Pimoroni's description |
| --- | --- | --- |
| 40 | `VBUS` | "used to charge the battery" |
| 39 | `VSYS` | "used to power the PICO" |
| 38 | `GND` | ground |
| 37 | `3V3_EN` | "turns the PICO on off via the button on the shim" |
| 36 | `3V3_OUT` | "for the shim power led only" |
| 35 / 34 | `ADC_VREF` / `GP28` | "used for battery state" |

So the Qi receiver lands on the **charge** input, not the **run** input. Wireless power
tops up the cell through the SHIM's MCP73831 at 215 mA; the RP2040 itself is fed from
`VSYS`, which the SHIM drives, gated by the button on `3V3_EN`. Pimoroni are explicit
that this gate applies with external power present — `3V3_EN` is needed "for the power
button to work **while USB is plugged in**." A Pico with 5 V on `VBUS` and the SHIM
switched off does not run.

### The link is binary, so "it is on the dock" is not evidence

The receiver is an [Adafruit 1901](https://www.adafruit.com/product/1901), a TI
BQ51013B that "manages the coil so that you'll always get 5V and 500mA" — but only
within the transmitter's 2–8 mm range and with the coil facing the pad. Adafruit are
blunt about the failure mode: if the coil is too far or turned the wrong way "it wont
work at all." There is no partial delivery to misread as slow charging. Either the
link is up at 5 V or there is nothing.

The assembly instructions give the confirmation signal: when wireless charging is
actually happening, **the transmitter's blue LED and the SHIM's red LED are both lit.**

### The fork this creates

This is the whole diagnosis in one observation, and it takes five seconds:

| Transmitter blue + SHIM red | What it means | Where the fault is |
| --- | --- | --- |
| **Not both lit** | no power is being delivered; the board is still running off whatever charge the cell holds | back to the flat-cell / brownout causes above — retest on a **wired** charger, which cannot silently fail this way |
| **Both lit** | `VBUS` is at a regulated 5 V | power is no longer the explanation — the fault is the assembly or the RP2040 is not executing `main.py` |

Only in the second case does "wireless charging is equivalent to plugging it in"
actually hold. Until both LEDs are confirmed, a silent board on the dock is the
expected result of a flat cell, not new information.

### Firmware is not implicated

Also raised, and correct: this does not need a firmware change. The board was answering
17/17 commands at 16:28 UTC on the firmware it still has, so nothing about the code
changed between working and silent. The three firmware faults documented above affect
what the numbers *mean*; they cannot stop the board joining wifi. The earlier suggestion
in this thread to reflash MicroPython was withdrawn on 2026-09-04 after the board was
confirmed to be running the correct `RPI_PICO_W` build, version 1.29.0.

### The measurement that ends the guessing

Everything above still leaves two live candidates — a marginal joint, and an RP2040 that
is powered but not executing. Both are settled by plugging the Pico's micro-USB into a
stream-cam Pi for two minutes and looking at how it enumerates:

| USB enumeration | Conclusion |
| --- | --- |
| nothing appears | no power reaching the RP2040 — a `VSYS`/`GND` joint, or `3V3_EN` held low |
| appears as `RPI-RP2` mass storage | sitting in the ROM bootloader, not running MicroPython — a double-press of the SHIM button with `BOOTSEL` held reaches this state |
| appears as a MicroPython serial device | the RP2040 is healthy; read `GP28` for the cell voltage and the remaining question is whether the cell can carry the radio |

The CDC-buffer caveat below does not apply to this test, because the board is being
driven directly rather than left to run `main.py` unattended.

`board_power_check.py` performs the last two rows: it reports the firmware build and
then reads the cell voltage through the SHIM's own battery-state divider on `GP28`,
so "is the battery flat?" becomes a number instead of an inference.

## Triage

`board_triage.py` reports which link is broken rather than that something is:

```bash
python board_triage.py                 # broker + board
python board_triage.py --lan-check     # add the wifi check; run from the lab LAN
```

`board_power_check.py` runs on the board instead of against it, for when triage has
already established that the board is simply not on the network:

```bash
mpremote connect id:e6647c15673a2438 run board_power_check.py
```

Five stages: firmware build, supply rail at idle, cell charge, whether external 5 V is
actually present on `VBUS`, and — the one that matters — whether the rail holds while
the radio keys up. It judges that last stage on the absolute floor as well as the sag,
because a board that is *already* browned out when the baseline is taken shows a sag of
zero, which sag alone would read as a clean bill of health. Exercised against a stubbed
board across eight scenarios; each names the right cause.

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

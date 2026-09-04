# OT-2 colour X-scan: pick up from slot 10, read three X positions over slot 8

The test @timothy-commins asked for in
[issue #33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33):

> make the color sensor pick up the enclosure from well 10, and then place it
> into 3 different places in the x direction on well 8. the test will then
> test the color at each of the 3 places in well 8

```
seated baseline read
  -> pick up the enclosure from slot 10        (proven descent/entry/press recipe)
  -> grip check                                (the sensor's own counts confirm the lift)
  -> carry to slot 8, x = centre - 30 mm       descend to the read height, read 3x
  -> carry to slot 8, x = centre               descend to the read height, read 3x
  -> carry to slot 8, x = centre + 30 mm       descend to the read height, read 3x
  -> carry back to slot 10, reseat, home
  -> reseat-confirm read
```

Every reading goes to `digital-wetlab.sensor-data` in MongoDB and to a local
JSON file.

## Run it

The script has to run on **the machine with the USB-Ethernet cable to the
OT-2**. The robot answers only on the link-local address
`169.254.51.252:31950`, and the same machine needs internet for HiveMQ and
MongoDB — so it must be one host, not two.

Neither Pi currently has `paho-mqtt` or `pymongo`, and their Python 3.13 is
externally managed, so use a venv:

```bash
python3 -m venv ~/.venvs/xscan
~/.venvs/xscan/bin/pip install paho-mqtt pymongo requests

export MQTT_BROKER=... MQTT_PORT=8883 MQTT_USERNAME=... MQTT_PASSWORD=...
export PICO_ID=... MONGODB_URI=... MONGODB_DATABASE=digital-wetlab
```

Then, in order:

```bash
# 1. confirm the pickup coordinate. Homes, hovers the BARE nozzle 30 mm above
#    the computed pickup point, and stops. Slide the base under it.
~/.venvs/xscan/bin/python run_xscan_test.py --align

# 2. sensor + database only -- the robot never moves
~/.venvs/xscan/bin/python run_xscan_test.py --dry-run

# 3. the real test
~/.venvs/xscan/bin/python run_xscan_test.py
```

Run `--align` **every time the base is moved**. The slot-10 pickup coordinate
below is the proven slot-8 coordinate translated by the OT-2 slot pitch, not a
measured one — `--align` turns that assumption into a 30-second visual check
before anything presses down on the enclosure.

## Deck layout

| | |
|---|---|
| Enclosure base | slot **10**, socket at (36.55, 315.5) |
| Read positions | slot **8**, x = 166.38 / 196.38 / 226.38, all at y = 225.0, z = 120.0 |
| Pipette | `p300_single_gen2`, left mount |

The pickup offset within the slot is (36.55, 44.0) — the same offset the
[PR #60 sessions](../camera/) used for the base in slot 8, so slot 10 gives
(0, 271.5) + (36.55, 44.0). The read Y uses the same within-slot 44.0 mm, which
lands on y = 225.0 in slot 8 — the exact Y those camera-verified sessions ran at.

**Only X changes between the three reads.** The 2026-08-10 session measured
that raw counts are dominated by pose — the same sensor read ~15× higher lifted
than seated — so a scan that also varied Y or Z would be measuring the pose
rather than the sample. Y, Z, settle time and command values are identical at
all three positions.

At z = 120 the nozzle is 29.5 mm above its press depth, so the enclosure's
aperture sits about **29.5 mm above the deck**. If you put a plate or a
backlight in slot 8, raise or lower with `--read-z`; the aperture height is
always `read_z - 90.5`.

## Motion recipe

Unchanged from the recipe that completed **9 of 9** pick-and-reseat cycles in
July/August 2026 ([`../camera/pickup-test-2026-08-10-pick-and-reseat/`](../camera/pickup-test-2026-08-10-pick-and-reseat/)).
Only the start slot and the read positions are new.

| stage | value |
|---|---|
| Descent ladder | z 170 → 150 → 120 → 105 → 101 → 99 |
| Straight entry | z = 95 @ 5 mm/s |
| Press | z = 90.5 @ 5 mm/s (≥ 7 mm engagement, so eject works later) |
| Lift test | z = 110 + 4 s dwell |
| High lift | z 130 → 150 → 170 @ 15 mm/s |
| Carry | 8.5 mm segments @ 10 mm/s |
| Read | descend to z = 120 @ 10 mm/s, settle 1.5 s, read ×3 |
| Drop-off | pickup x − 6 mm (anti-tilt), staged descent 130 → 110 → 108 → 101 → 95.5 |
| Eject | `dropTipInPlace`, clear to z = 128, home |

The staged climbs and segmented carries are not decoration: on 2026-07-31 the
module came off the nozzle during a single long Z move.

## Safety behaviour

**Grip check.** After the lift test the script takes two readings and compares
them with the seated baseline. Lifting the enclosure off its base uncovers the
aperture, which raised the counts ~15× in the 2026-08-10 session. If the counts
do not rise by at least 2× (`--grip-ratio`), the nozzle came up empty and the
script aborts before the carry rather than flying an empty nozzle to slot 8 and
then "reseating" it next to a still-seated enclosure. `--skip-grip-check`
disables it.

**Reseat on failure.** Any exception during the carry or the reads triggers the
reseat leg and a home before the script exits, so the enclosure is not left
hanging. If that also fails, the message points at
[`../cad/recover_reseat.py`](../cad/recover_reseat.py), which recovers a
stranded grip — but look inside the robot first.

**Preflight.** Before the robot is touched: the broker connection is proved by
publishing a probe to our own topic and waiting for the echo (a broker can grant
a subscription and then deliver nothing), the sensor is proved by taking the
seated baseline, and every coordinate is bounds-checked against its slot.

## Files

| file | what it is |
|---|---|
| `run_xscan_test.py` | the test |
| `sensor_read.py` | one MQTT connection held open for the run; `read()` returns the 8 channels |
| `deck.py` | OT-2 slot origins and slot/offset maths, with no `opentrons` dependency |
| `check_reachability.py` | pushes every planned coordinate through the Opentrons simulator |

## Options

```
--home-slot 10 --scan-slot 8      which slots to use
--base-dx / --base-dy             where the socket sits within the home slot
--scan-dx -30,0,30                X offsets from the scan slot's centre (any number of them)
--scan-dy 44.0                    within-slot Y for the reads
--read-z 120 --carry-z 170        heights
--reads 3                         readings per position
--rgb 0,0,0                       R,Y,B sent with each read command
--align / --dry-run / --simulate  the three rehearsal modes
--no-mongo --out results.json     where the data goes
```

`--simulate` prints the whole motion plan with no robot and no sensor — useful
for checking a changed layout before taking it anywhere near hardware.

## What has been verified, and what has not

Verified on 2026-09-04 from CI:

- `sensor_read.py` against the live board — 8 channels back in 1.5 s.
- `--dry-run` end to end — baseline reads, MongoDB write into
  `digital-wetlab.sensor-data`, JSON output.
- `check_reachability.py` — all 28 planned coordinates in bounds for a
  left-mount P300; `deck.py`'s slot origins match the packaged Opentrons deck
  definition. Negative controls confirm the checker has teeth: `--scan-dx
  -100,0,100` is rejected as off-slot and `--read-z 250` is rejected as above
  the 218 mm Z limit.
- `--simulate` — 72 moves planned, segmentation and staging as intended.

Not verified: **the motion itself.** The OT-2 did not answer on
`169.254.51.252` from either stream-cam Pi during this session, and neither Pi
has a USB-Ethernet adapter attached, so the robot half could not be exercised.
Reconnect the OT-2's USB-Ethernet cable to the Pi (or run from whichever machine
holds that link) and start with `--align`.

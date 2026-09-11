# OT-2 colour X-scan: pick up from slot 10, read three X positions over the scan slot

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

As of 2026-09-09 that machine is the Pi behind **`RPI_STREAM_CAM_HOSTNAME`**,
not the one behind `OT2_STREAM_CAM_HOSTNAME`. The adapter is a Realtek RTL8153
on `eth1` holding `169.254.210.205/16`. The `OT2_STREAM_CAM_HOSTNAME` Pi has no
ethernet interface and no USB devices at all, so `169.254.51.252` times out from
there — which is what "the OT-2 is not answering" looked like in the previous
session. Check with `ip -4 -br addr` before concluding the robot is down.

The venv is already set up on that Pi at `~/.venvs/xscan` (`paho-mqtt`,
`pymongo`, `requests`; the system Python 3.13 is externally managed, hence the
venv). To rebuild it elsewhere:

```bash
python3 -m venv ~/.venvs/xscan
~/.venvs/xscan/bin/pip install paho-mqtt pymongo requests

export MQTT_BROKER=... MQTT_PORT=8883 MQTT_USERNAME=... MQTT_PASSWORD=...
export PICO_ID=... MONGODB_URI=... MONGODB_DATABASE=digital-wetlab
```

Then, in order:

```bash
# 0. is the enclosure actually on the deck? One HTTP call, no motion.
~/.venvs/xscan/bin/python deck_photo.py -o deck.jpg

# 1. confirm the pickup coordinate. Homes, hovers the BARE nozzle 30 mm above
#    the computed pickup point, and stops. Slide the base under it.
~/.venvs/xscan/bin/python run_xscan_test.py --align

# 2. sensor + database only -- the robot never moves
~/.venvs/xscan/bin/python run_xscan_test.py --dry-run

# 3. the real test
~/.venvs/xscan/bin/python run_xscan_test.py
```

**Step 0 is not optional when nobody is standing at the robot.** The grip check
catches an empty pickup, but only after the nozzle has already descended and
pressed at slot 10. A photograph costs one HTTP call and answers the same
question before anything moves — on 2026-09-09 it found the deck completely
bare, with nothing in slot 10 or slot 8.

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
| `stream_index.py` | every reading → its UTC instant → a timestamped livestream link |
| `frames_from_stream.py` | pulls one frame per measurement and OCR-verifies it against the clock burned into the stream |
| `plot_spectra.py` | 300 px spectra in the light-mixing `basic_plotting.py` style |
| `build_gallery.py` | stitches frame + spectrum + link into `measurement-gallery.md` |
| `stream_grab_pi.py` | the Pi-side half of the frame grab (lives there as `~/ytframes/grab.py`) |
| `led_probe.py` | zero-motion check of whether the module's LEDs respond (they do not) |
| `deck_photo.py` | one HTTP call to the OT-2's own overhead camera |

## Lining a reading up against the livestream

`python3 stream_index.py` writes `measurement-stream-index.{json,md}`: all 114
readings of the 2026-09-09 session with a UTC instant and a `?t=` link into the
archived stream. `frames_from_stream.py` then pulls the frame at each instant.

Two things to know before trusting a link:

* **The archive timeline is not wall clock.** For `bQDrYpT3vaE` it runs 67 s
  behind `release_timestamp` from the third hour onward — a step, not a drift.
  That is more than one scan position, so `--offset-shift` is not cosmetic.
* **The stream burns a `%Y-%m-%d_%H-%M-%S` clock (lab local, UTC−6) into every
  frame**, which is how the offset is verified rather than assumed. Every
  committed frame records its OCR'd clock in `frames/frames.json`.

YouTube refuses player extraction from a GitHub Actions runner; the fetching
half runs over SSH on the stream-cam Pi (`~/ytframes/grab.py` there).

## Options

```
--home-slot 10 --scan-slot 8      which slots to use
--base-dx / --base-dy             where the socket sits within the home slot
--scan-dx -30,0,30                X offsets from the scan slot's centre (any number of them)
--scan-dy 44.0                    within-slot Y for the reads
--read-z 120 --carry-z 170        heights
--press-z 90.5                    pickup press depth; lower = deeper = tighter fit
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

Not verified on 2026-09-04: **the motion itself.** The OT-2 did not answer on
`169.254.51.252`, which was read at the time as a disconnected USB-Ethernet
adapter.

### 2026-09-09 — the robot answers; the deck is empty

That reading was half right. The adapter was never missing, it is on the *other*
Pi (see [Run it](#run-it)). From `RPI_STREAM_CAM_HOSTNAME` the robot answers
immediately:

```
GET /health -> 200  {"name": "OT2CEP20210722R13", "robot_model": "OT-2 Standard",
                     "api_version": "8.8.1", "system_version": "v1.19.6"}
GET /instruments    -> p300_single_gen2, left mount, ok=true
GET /calibration/status -> deckCalibration OK (2026-01-27)
```

Also verified this session, from the Pi that would drive the run:

- Sensor over MQTT — 8 channels, total 770 ± 1 across five reads, ~1.4 s each.
- `--dry-run` — broker delivery PASS, baseline reads, 2 documents written to
  `digital-wetlab.sensor-data`, JSON out.
- `--simulate` — 72 moves.
- `check_reachability.py` — 28/28 coordinates in bounds, slot origins match the
  packaged deck definition.
- **The maintenance-run command path, on the real robot.** Create run →
  `loadPipette` → `home` → `savePosition` → delete, all succeeded: pipette
  loaded in 2.4 s, home in 12.5 s, nozzle parked at (384.05, 349.93, 199.60).
  This is the path every move in the test goes through, and it had never been
  exercised before. Home was safe to run precisely because the deck was
  photographed empty first.

**The motion still did not run, for a different reason: the deck is bare.**
`deck_photo.py` shows all eleven slots empty — no enclosure, no base in slot 10,
nothing in slot 8. Running the test in that state would have descended on an
empty slot, come up with nothing, and aborted at the grip check without
measuring anything.

So the remaining blocker is now purely physical: stand the enclosure on its base
in slot 10, then run step 0, `--align`, and the test.

### 2026-09-09 — slot 7 at two heights; the LEDs were off the whole time

Two more complete cycles, both with slot 7 empty: the run asked for on #197
(`--scan-slot 7 --read-z 125`) and a control at the previous height
(`--scan-slot 7 --read-z 120`). The control exists because the requested run
changes both the slot and the height at once, so alone it cannot attribute the
difference to either. Grip check 5.1× and 5.3×; reseat confirmed on both.

Full write-up and data: [`results-slot7-2026-09-09.md`](results-slot7-2026-09-09.md).

Two things came out of it that change how the test should be run:

- **`--rgb` defaults to `0,0,0`, so every scan measures ambient light only.**
  The module's own illumination is never switched on. *Superseded in part later
  the same day:* `--rgb` turns out to be **inert** — the board acknowledges every
  level and colour but nothing lights (`led-probe-2026-09-09.json`), so "set
  `--rgb`" is not an available fix. Controlled illumination needs a working light
  source in the enclosure. This still reframes the "46% swing" finding: it is a
  symptom of reading with no illumination, not an inherent property of the deck.
- **Raising the aperture makes everything worse.** 5 mm higher cost 9–42% of the
  signal and made read-to-read repeatability 30–300× worse (0.03–0.07% at
  z 120 against 1–11% at z 125), and reversed the sign of the positional
  gradient. Slot 7 at z 120 gives ~7000 counts, a −5.5% gradient over 60 mm and
  reads that agree to within 2–5 counts; it beats both slot 8 and the raised
  pose on every measure. Default to it.

### 2026-09-09 — read z 129 with a 0.5 mm deeper press

Requested on #197 after the module worked loose and came off its base at the end
of the previous session: read 1 mm higher, press 0.5 mm deeper for a tighter fit.
`--press-z` was added for it, and it shifts the release height by the same delta
so the module is set down from the height the proven recipe used rather than
dropped from 0.5 mm up.

    run_xscan_test.py --scan-slot 7 --read-z 129 --press-z 90.0

Cycle completed, grip 4.6×, reseat confirmed at 436 against a seated 445. Full
write-up: [`results-z129-press90-2026-09-09.md`](results-z129-press90-2026-09-09.md).

Three things worth carrying forward:

- **A deeper press also raises the read height.** Seating the nozzle further into
  the socket makes the module ride higher on it, so `--read-z 129 --press-z 90.0`
  puts the aperture 39.0 mm off the deck — 1.5 mm above the previous run, not the
  1.0 mm the `--read-z` number alone suggests. `aperture_height_mm` in the run
  JSON is the number to compare across runs, not `--read-z`.
- **One clean cycle does not validate a grip fix.** The previous session's
  three-position cycle also completed cleanly; the module was lost during the
  longer second cycle that followed. And the grip *ratio* is a light reading at
  the lift height, not a measure of fit — a deeper press moves the aperture, so
  the ratio shifts for reasons unrelated to how tightly the module is held.
- **Bare deck is not spectrally flat, and differs by position.** At x = 93.88 the
  620 nm share is 28.6% against 20.9% at the slot centre, in the empty run and
  both paint runs alike. A per-position empty reference is the only valid
  baseline; "looks reddish" is not evidence of a red sample.

## 2026-09-09, late — why only yellow ever registers (no motion)

Re-analysis of every scan on record, prompted by the question on #197: if the
aperture clears the deck and passes over a vial at each stop, why does only one
colour show? Full write-up:
[`results-why-only-yellow-2026-09-09.md`](results-why-only-yellow-2026-09-09.md);
regenerate the figure with `python3 plot_why_only_yellow.py`.

- **Read height decides whether this instrument works.** Spread of the spectral
  shape across the three stops of an **empty** slot 7, worst channel, in points of
  share: **0.14 at z 120 · 1.52 at z 125 · 7.69 at z 128.** Fifty-five times worse
  for an 8 mm rise, with nothing on the deck. The colour effects reported earlier
  in the day are ~1.3 points, i.e. smaller than the artefact at the height they
  were measured at.
- **The height needed to clear a tall vial is the height at which measuring
  stops working.** Prefer flat opaque targets at z 120 over vials at z 128.
- **Occlusion and yellow paint have the same spectrum.** The room light carries 4×
  more flux in 583–670 than in 410–470, and 440/470 sit on a white LED's blue pump
  peak while 410 sits below it. So losing sight of the cool component reads as
  "440/470 down, 410 flat, red up" — indistinguishable from a yellow absorber
  without an illuminant of your own. Blue samples have no flux to reflect; red
  samples darken an already-red background, which is the artefact's own signature.
- **Check a claimed detection in absolute counts.** The "yellow" at x = 33.88 came
  with the total up 17% and 410 nm up 12% while 440 nm fell 25%. An absorber does
  not raise the total, and yellow's absorption edge is monotone below ~480 nm, so
  it must cut 410 at least as hard as 440. That was the room light changing between
  two runs six minutes apart, not a sample.
- **To settle it: move the sample, re-scan.** If the feature follows the vial it is
  real; if it stays at the same X it is the machine.

---

## Opentrons App protocols — `protocols/`

Two protocols to run from the Opentrons App, replacing hand-tuned deck
coordinates with labware the app can calibrate. See
[`protocols/README.md`](protocols/README.md).

- [`protocols/01_pickup_both_sides.py`](protocols/01_pickup_both_sides.py) —
  can the P300 use **both** sockets of the charging base? Hover over each, pick
  up in place, or shuttle the enclosure A1 → A2 → A1.
- [`protocols/02_read_height_over_well.py`](protocols/02_read_height_over_well.py) —
  carry the enclosure to one well of a 96-well plate and step through read
  heights, expressed relative to the **well rim** rather than as an absolute
  deck Z.

Three constraints found by simulating against `opentrons==8.8.1`, the robot's
own software version:

- **`pick_up_tip` from the 2-well dock fails at `apiLevel` 2.14 and above** —
  `InvalidStoredData: ... less dense than an SBS 96 standard`. The newer
  tip-tracking code assumes a rack at least 12 wells wide and 8 tall. Both
  protocols are pinned to **2.13**, which uses the older core. The cost is no
  runtime parameters; Labware Position Check still works.
- **Labware Position Check cannot separate A1 from A2** — one offset per
  labware, so it slides both sockets together. A per-socket error has to be
  fixed by editing `wells.A2.x` / `.y` in the definition.
- **A bare P300 GEN2 on the left mount bottoms out at deck z 29.45 mm**, about
  +15 mm over a 96-well plate rim. Dry runs can only rehearse the top of a
  height ladder; the rest needs the 84 mm enclosure attached.

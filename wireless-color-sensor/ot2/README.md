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
| `blank_correction.py` | divides a sample run by a blank run per position, offset removed |
| `led_probe.py` | zero-motion check of whether the module's LEDs respond (they do not) |
| `analyse_person_effect.py` | whether somebody at the machine moves the readings; `--gate` screens a run for a background that shifted mid-position |
| `deck_photo.py` | one HTTP call to the OT-2's own overhead camera; turns the frame 180° upright, `--fix FILE` corrects a saved one |
| `robot_lights.py` | read or set the deck rail lights; one HTTP call, no motion |
| `analyse_rail_lights.py` | what the rail lights buy: precision, uniformity, colour self-consistency |
| `reseat_module.py` | recovery when a release fires and the module stays on the nozzle; `--check` moves nothing |
| `background_baseline.py` | seated background of the closed enclosure; says whether the offset has moved |
| `test_measurement_timestamps.py` | tries to break PR #201's timestamp work; `--live` adds MQTT + Atlas, never the robot |
| `plot_timestamp_lag.py` | how late the pre-fix MongoDB `timestamp` field was, per reading |

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

## The background (blank) measurement

A background — or blank — is **a reading of the empty well, taken at the same
pose, under the same light, immediately before the sample goes in.** It is not a
dark reading and it is not a calibration constant: it is the *same measurement
with the sample removed*, so that dividing the sample by it cancels everything
that is not the sample.

The sensor never measures colour. It measures how many photons land in each of
its eight bands, which is the product of four things:

```
counts(λ)  =  source(λ)  ×  path(λ)  ×  sample(λ)  ×  responsivity(λ)
```

Only `sample(λ)` is wanted. The blank contains the other three at that exact
spot, so `sample / blank` leaves the sample's own spectrum — the room light's
warm cast, the deck's colour, the enclosure's geometry and the AS7341's uneven
per-channel sensitivity all divide out. Without one, a raw count is a statement
about the room, not the liquid; every run before 2026-09-09 demonstrated that.

**One blank per well, not one per plate.** The blank has to be taken where the
sample will be, because this rig's background is strongly position-dependent.
An *empty* slot 7 at read z 128 already disagrees with itself between its three
stops — 620 nm is 23.1 % / 20.9 % / 28.6 % of the total with nothing on the deck
at all. Borrowing a neighbour's blank injects a **37–92 %** error, against a
largest-ever colour signal of about ±30 %.

**Subtract before dividing.** About 439 counts of every reading are a fixed
green glow inside the closed enclosure (`ch410` was exactly 6 on all 26 seated
reads across seven runs and eight hours). Because it is *additive*, it must be
removed from both numbers before the ratio:

```
             sample(λ) − offset(λ)
ratio(λ)  =  ─────────────────────
             blank(λ)  − offset(λ)
```

Dividing without subtracting drags ch510/ch550 toward 1.0 by up to 6 %, and at
read z 128 that offset is 36–47 % of ch510 — against 18 % at z 120, which is
another reason the lower read height is the better one.

**Dry blank or solvent blank.** Both are useful and they answer different
questions. A *dry* empty well is the background for everything that is not the
liquid. A well holding the same volume of plain water is the stricter blank: it
also cancels the meniscus, the refraction at the water surface and water's own
weak absorption, leaving pigment alone. Take the dry one first — it is free —
and the water one when comparing dilutions against each other.

**Freshness matters more than it looks.** The blank and the sample must be
minutes apart with nobody near the machine. The archived-stream frames showed a
person in shot during 11 of the 27 readings on 2026-09-09, including the whole
of the "empty-slot baseline at z 128" that the paint run was normalised
against — so that pair was never a valid blank/sample pair.

### Doing it with what is already here

No new flag is needed. Run the *same* command twice, changing only the well's
contents and the output file:

```bash
# 1. blank: the well is empty. Stand clear of the machine.
python3 run_xscan_test.py --scan-slot 7 --read-z 120 --out blank.json

# 2. add the sample, move nothing else, stand clear again.
python3 run_xscan_test.py --scan-slot 7 --read-z 120 --out sample.json

# 3. the ratio, with the additive offset removed and a per-position cross-check
python3 blank_correction.py --blank blank.json --sample sample.json --cross-check
```

Positions are matched by the labels `run_xscan_test.py` writes (`pos1-dx-30` and
so on), so both runs must use the same `--scan-dx`.

**What a blank does not fix.** It cancels a *stable* background, so it cannot
rescue a background that changed between the two reads — someone leaning over
the deck, a light switched, the module reseated at a slightly different depth.
It also cannot create signal that was never there: under warm ambient light a
blue vial reflects in a band that barely exists, and blue's spectral signature
is a −0.954 match for the sensor's own two-cycle readout artefact. A blank is
necessary for this measurement to mean anything; it is not sufficient on its
own, and a controlled light source still is the larger fix.

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

## 2026-09-09, later — three instrument artefacts, none of them ambient light

Asked on #197 whether ambient light is the whole story, given that our sample is a
19 mm vial top rather than `ac-dev-lab#552`'s thin transparent columns. It is not.
Full write-up:
[`results-instrument-artefacts-2026-09-09.md`](results-instrument-artefacts-2026-09-09.md);
regenerate with `python3 analyse_instrument_artefacts.py`. No hardware needed —
it reads only the committed `xscan-*.json` files.

- **A green LED is on inside the enclosure.** 26 seated reads across 7 runs and ~8 h
  give 439 counts, `ch410` exactly 6 every time, peaked at 510/550 nm. That is an
  indicator LED (Pico W or breakout), not room light and not darkness. It is a fixed
  *additive* term nobody subtracts, and it is **36–47% of ch510 at read z 128** against
  18% at z 120 — so its share moves with signal level, bending the normalised spectrum
  position to position with an empty slot. **Subtract the seated vector before
  normalising.**
- **One reading is two measurements.** The AS7341 has 11 photodiodes and 6 ADCs, so
  F1–F4 and F5–F8 are separate integrations. The repeat-read correlation matrix breaks
  *exactly* there: **+0.970 within F1–F4, +0.978 within F5–F8, +0.649 across**, and a
  scan over all seven possible split points peaks sharply at 510\|550 (+0.325 vs +0.157
  next best). 410 and 510 are 100 nm apart and correlate at 0.97; 510 and 550 are 40 nm
  apart and correlate at 0.61 — spectral adjacency does not predict that, ADC scheduling
  does. Per-read half-to-half mismatch reaches 12.4%.
- **That artefact is spectrally degenerate with yellow — and with blue inverted.**
  Cosine similarity against the artefact: **blue −0.954**, yellow +0.761, red +0.566.
  The x = 33.88 "yellow" feature matches real yellow pigment at +0.808 and a pure
  readout half-step at +0.804. Indistinguishable. This is why yellow is the only colour
  that has ever appeared, and it would still be true in a blacked-out room.
- **A 19 mm vial fills 49% of the spot at z 128** (~±20° FOV, no lens; 79% at z 120),
  and a clear vial over the deck is a double-pass filter, not a reflector, so contrast
  is `f·(1−T²)` ≈ 18% best case against a 7.69-point empty-slot artefact.
- **The sensor runs at 5% of full scale** — largest count on record 3404 of 65535.
- **The payload returns 8 numbers and nothing else.** No gain, no integration time, so
  two runs cannot be checked for comparability — and the AS7341 samples `Clear` in
  *both* SMUX cycles, which is exactly the factor needed to stitch the halves together.
  The firmware measures it and throws it away.
- **Untried and free: the OT-2's own rail lights.** `POST /robot/lights {"on": true}`,
  one HTTP call, no motion — a controllable source already on the machine. `#552` found
  them too bright, which with 20× of ADC headroom is the good failure mode.


## 2026-09-10 — testing PR #201's timestamp work (no motion)

`test_measurement_timestamps.py`, **39 of 40 checks pass**. Full write-up in
[`results-fix-verification-2026-09-10.md`](results-fix-verification-2026-09-10.md).

| leg | how it was tested | result |
| --- | --- | --- |
| reading → timestamp | fake broker driving the real `SensorLink` | id, ISO strings and epoch fields agree to the ms and bracket an independent measurement |
| reading → MongoDB | real driver, real Atlas cluster, scratch collection, cleaned up after | 0.0 ms drift through BSON; two readings 163 s apart stay 163 s apart; `stored_at` separate and later |
| reading → livestream link | regenerate the committed index; cross-check all 27 frames | byte-identical, 114/114 linked, worst OCR-clock error 0.8 s |
| **sensor → reading** | **not tested** | the board did not answer; it is on battery, not on the Pi's USB |

The pre-fix documents still in `sensor-data` quantify what the fix removes:
median **103 s** late, worst **258 s**, always late and never early.
## 2026-09-10 — the reads police themselves; gate a blank before trusting it (no motion)

Prompted by the push-back on #197 that the overhead camera is not the sensor.
That is right, and the 2026-09-09 write-up was sloppy to say "a person in shot"
as though the livestream did something — the frame is only evidence that
somebody was at an open machine. Full write-up:
[`results-person-effect-2026-09-10.md`](results-person-effect-2026-09-10.md);
reproduce with `python3 analyse_person_effect.py`.

- **The enclosure is sealed only while it is on its base.** Closed, it reads
  **439.2 counts, sd 2.39** over 26 reads and ~8 h with people coming and going,
  `ch410` exactly 6 every time. Lifted over a slot it reads 2134–7263, so
  **79–94 % of every measurement is light that entered from outside.** During a
  measurement it is a funnel pointed at a room-lit deck, not a dark box.
- **A person at the machine moves the reading, and the sensor says so itself.**
  The three reads at a position are 1.4 s apart with the gantry parked, so only
  the light can change between them. Quiet: `7084, 7083, 7086` — 0.04 %, every
  channel within one count. With somebody there, at the same aperture height:
  `3431, 3298, 4345` — **+31.7 % in 1.4 s**, warm-weighted (583 nm +47 %, 410 nm
  +8 %), which is light *added* by a large close skin-coloured reflector, not a
  shadow. Across all 27 positions: spread over 1 % for 9 of 10 with somebody
  there against 3 of 17 without, Fisher exact **p = 0.00075**; height-stratified
  permutation **p = 0.0033**.
- **Gate a run instead of watching the video.** A quiet position repeats to
  0.03–0.13 %, so `analyse_person_effect.py --gate FILE` flags any position whose
  reads disagree by more than **0.5 %**. It catches three positions the frames
  called clear, because somebody just out of frame is invisible to the camera and
  obvious to the sensor. **A blank whose own background moved cannot cancel the
  sample's** — gate the blank before pipetting.
- Caveats worth carrying: the 39.0 mm stratum contradicts the trend on n=1;
  person and object-being-placed are entangled at the position level (the 1.4 s
  step is not); and one frame per ~4.2 s position understates the effect.

## 2026-09-10, post-move — rail lights on by default; the background moved

The lab setup was moved and re-assembled. Full write-up:
[`results-postmove-2026-09-10.md`](results-postmove-2026-09-10.md).

- **The OT-2 has no network link.** Its USB-ethernet adapter is still on the
  stream-cam Pi and the driver still loads, but `/sys/class/net/eth1/carrier`
  is `0` — `NO-CARRIER` since boot, so nothing is plugged into it. Not a
  wrong-Pi mix-up (the other Pi has no ethernet interface at all), not moved
  onto Wi-Fi (port 31950 closed across the Pi's whole `/24`, no mDNS). **Check
  `carrier` before assuming an address is stale**: with no carrier, no address
  on that interface can work.
- **The rail lights are now on by default.** `run_xscan_test.py --lights
  {on,off,leave}`, default `on`, set *before* the seated baseline so the
  baseline and the scan it references share one illuminant. If the robot cannot
  be reached the run stops rather than producing a reading that is not
  comparable with a lit one; `--lights leave` is the explicit opt-out. The
  state is recorded as `run.lights` in the JSON and in every MongoDB document,
  so two runs can finally be checked for comparability. `robot_lights.py` is
  the standalone one-call version. **Untested against hardware** — the robot
  was unreachable when this was written.
- **The closed-enclosure background moved −5.9 %** (439.19 → 413.27 counts,
  **10.9 sd** of the old spread; `background_baseline.py`, 30 seated reads).
  Not a uniform dimming: the 510/550 nm core held (−2 to −3.5 %) while the
  wings fell 8–32 %, so the indicator LED is steady and what has gone is
  broadband room light that used to leak into the closed box. The new baseline
  is *steadier* — total sd 1.34 against 2.39 — which fits. **Every offset
  vector and blank from 2026-09-09 is stale.** `blank_correction.py` already
  defaults to taking its offset from the blank and sample runs themselves, so a
  fresh pair is self-consistent; do not reuse an old blank against a new sample.
- **Run `background_baseline.py` after anything is unplugged, re-seated,
  re-sited or re-batteried.** It needs no robot and no tailnet — MQTT only —
  and it says outright whether the offset has moved beyond noise.
- **`test_measurement_timestamps.py --live` is 44/44.** The sensor → reading
  leg, untested on 2026-09-10 03:02 because the board was silent, now passes;
  the fixed code has written its first real documents. Section 10's *"the fix
  has never run for real"* marker was spent and is replaced by a check that no
  post-fix document collapses its reading time onto its write time.
- **A live frame can be pulled from the OT-2 stream when the camera is busy.**
  The streamer holds the camera exclusively, so `rpicam-still` is not an
  option on that Pi; `yt-dlp -g` on the channel's `/live` URL returns a URL
  that is already a *media* playlist (segments, not variants), so fetch its
  last segment and hand ffmpeg the local file.

## 2026-09-10, 19:50 — the background with the rail lights on

Full write-up: [`results-background-lights-2026-09-10.md`](results-background-lights-2026-09-10.md).
Two cycles at slot 7 / read z 129 / press z 90.0 with the vials off the deck,
differing only in the rail lights.

- **Rail lights on is now the standing default**, at the user's request on #197.
  `--lights on` is already `run_xscan_test.py`'s default; `--lights leave` opts
  out. Measured against an unlit control minutes apart: **5.6× more signal**
  (15224 vs 2724 counts), worst read-to-read spread **0.31 % vs 2.71 %**, zero
  positions over the 0.5 % stability gate against one, and the fixed internal
  green offset down from 14.9 % of the reading to **3.1 %** (on ch510, 38.3 %
  to 8.3 %). Still 4.9 % of full scale, so the gain and integration-time
  registers are untouched headroom.
- **The cost, stated plainly: the rails are not uniform over the deck.** They
  add a 6.7 % gradient across 60 mm of X where the unlit deck had 2.2 %, and
  the between-stop colour disagreement is 0.30 points lit against 0.11 unlit.
  Both are fixed lamp geometry, which is what a per-position blank divides out;
  the unlit run's 2.71 % was the room stepping mid-run, which a blank cannot
  rescue.
- **A blank is only valid for the same pose *and* the same lights state.** The
  rails leak into the closed enclosure too — seated 467 lit against 406 unlit.
- **The OT-2 camera is mounted inverted; frames need 180°, not 90°.** And the
  old correction was a silent no-op whenever Pillow was missing, which it was
  on the Pi — so every frame before today was raw. Fixed, loudly: `rotate()`
  raises and `deck_photo.py` exits 3 rather than shipping an unrotated frame.
  The 14 committed robot-camera frames have been turned upright in place, and
  one earlier conclusion changes with them: the 19:41 frame showed the vials
  **off** the deck, not on it.
- **A release can fail to let go.** `dropTipInPlace` fired and the module
  stayed on the nozzle (reseat-confirm 1010 vs seated 406). That is recoverable
  — `reseat_module.py` retried it, 1016 → 419 — because the module's position
  is known. A module lying on the *deck* is not; tell them apart with a photo.
  This is the other edge of the 0.5 mm deeper press.

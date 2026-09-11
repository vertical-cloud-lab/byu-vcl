# Has anyone ever got accurate colour results from this rig?

Asked on [#197](https://github.com/vertical-cloud-lab/byu-vcl/issues/197) on
2026-09-11. This file is the answer and the evidence, so that the next session
does not have to re-derive it.

**Yes — twice, upstream at the Acceleration Consortium. Never yet in this
repository.** One of the two upstream successes is quantified; the other is
qualitative but ran a whole university course on it.

Everything below is sourced. Where a number is quoted, the link goes to the
comment it came from.

---

## 1. The two successes

### 1a. Yanghuang Lin (@Neil-YL), February 2025 — the quantified one

Winter 2025 MSE403H1 practical, `ac-dev-lab` (then `ac-training-lab`)
[#152](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152).

The decisive step was a **per-well white reference**:

> "I have measured a white color to have a full-reflection value for each wells
> location and use it as the denominator for other color measure value. The
> relative standard deviation (RSD) can be reduced from **6-7% to 1.2-2.3%**."
> — [2025-02-12](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152#issuecomment-2654927124)

Units: RSD is the standard deviation of a channel's normalised value across
repeat measurements, as a percentage of that channel's own mean. It is the only
repeatability number in the whole project's history from before 2026-09.

Three things travelled with it:

- **OT-2 rail lights on, room light off.** Policy set by @sgbaird on
  [2025-01-23](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152#issuecomment-2611256310):
  *"Let's keep ot-2 light on always."*
- **The A row of the plate was discarded**, not corrected — its well-to-well
  variation was too large, so all A-row wells were marked `used` in MongoDB and
  the Hugging Face Space skipped them.
- **Dilute acrylic paint**, ~10:1 water:paint, after food colouring and Crayola
  washable were both tried and rejected.

Confirmed a year later by @sgbaird, asked directly whether the course had worked:
*"Yes, I believe so — with the acrylic paint."*
([2026-03-20](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4100689540))

### 1b. Kelvin Chow (@kelvinchow23), March 2026 — the recovery

Winter 2026 practical,
[#552](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552). It
started by failing in exactly the way #197 failed:

> "It seems the sensor is much more responsive to the lighting conditions then
> the colour in the well. I put a box over it and there's almost zero signal. I
> turn on the Opentrons lights and its too high. I partially blocked the light
> or used my phone flashlight, and there were no distinct peaks when the sensor
> was reading pure red, blue, and yellow colours. Channel intensities seemed to
> moved together."
> — [2026-03-08](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4019810830)

Fixed over about two weeks, in this order:

1. **A light panel underneath the well plate** (borrowed from SDL4), dimmed with
   sheets of paper because its lowest setting was still too bright —
   [2026-03-13](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4052400355).
   This is the single most important structural difference from #197: it turns a
   double-pass reflectance measurement off an uncontrolled deck into
   single-pass transmission through the sample.
2. **Curtains around the machine** to cut room light —
   [2026-03-19](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4093879580).
3. **A blank-well survey**: 5 measurements in each of the 96 wells, empty,
   giving a per-well intensity map and a per-well coefficient of variation —
   [2026-03-19](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4087471195).
4. **Normalising every measurement against that well's own blank** —
   [2026-03-21](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4101574167):

   > "i ran it again but normalized the data to account for the varying lighting
   > conditions of the blank wells. It's better. […] These are the closest
   > colors to the target. **This is much better than anything i've seen
   > previously**"

   The Bayesian optimisation campaign then started proposing blue ≈ 0, which was
   correct: the target mixture had blue close to 0.

**Stated honestly, it was still noisy.** @sgbaird, 2026-03-23: *"The 'model fit
is poor' warning is a bit concerning. Basically measurements are too noisy for
it to make a reliable model."* So 1b is "the optimiser now finds the target",
not "the spectrum is trustworthy".

---

## 2. Things that were tried and did *not* work

Worth knowing before repeating any of them.

| tried | outcome | source |
| --- | --- | --- |
| Food colouring in water | Transparent, thin column, poor signal; superseded by acrylic | #152 |
| Crayola washable paint | Too viscous even at 1:15–1:20; visible layering, sticky bubbles after blow-out | #152 |
| Food dye + milk | "data looks better than anything else i've seen, but is still noisy"; also has to be washed out or it smells | #552, 2026-03-24 |
| **AS7341 onboard LED, black-printed enclosure** | "made some channels less distinguishable of some similar colors"; "not improving the data quality" | #87, #152 |
| Cardboard box over the machine | "almost zero signal" | #552, 2026-03-08 |
| Phone flashlight | "no distinct peaks" — and a phone torch is PWM'd | #552, 2026-03-08 |
| OT-2 rail lights alone, 2026 run | "too high" at that point — before the light panel and the blank normalisation | #552, 2026-03-08 |
| Cycling through all pipette tips | Made dispensed volumes *worse*; reverted to reusing 3 tips | #552, 2026-03-19 |

**Note the fourth row.** The AS7341's own white LED is not an unexplored win —
it was tried upstream and rejected, on the grounds that it saturates the
enclosure walls and *reduces* the contrast between similar colours.

---

## 3. Firmware facts, read from source rather than inferred

All from
[`AccelerationConsortium/wireless-color-sensor`](https://github.com/AccelerationConsortium/wireless-color-sensor),
`sensor_file/`, which is the code our Pico W runs.

### 3a. `R` / `Y` / `B` are paint volumes in microlitres, not LED colours

`OT2mqtt.py` consumes them as `p300.aspirate(color_volume[pos], reservoir[pos])`
from vials `B1`/`B2`/`B3`, with `R + Y + B <= 300` because the pipette is a P300.
The sensor board never reads them.

This corrects two earlier conclusions on #197: the advice to "set `--rgb` before
the paint test" (2026-09-09 01:22) was not actionable, and the follow-up finding
that "the LEDs are inert" (2026-09-09 01:47) was right about the observation and
wrong about the cause. Nothing lights because `--rgb` was never a light command.

### 3b. There *is* a controllable white LED, disabled by two commented-out lines

- `lib/as7341.py:541` implements `set_led_current(current)`, 4–20 mA.
- `lib/as7341_sensor.py:126-138` wraps it as a `Sensor.LED` property.
- `main.py`'s `read_sensor_data()` has `# sensor.LED = True` and
  `# sensor.LED = False` commented out.

So enabling it is a two-line firmware change on the board — but see §2, it was
deliberately turned off upstream.

### 3c. One reading really is two integrations

```python
def all_channels(self):
    self.sensor.start_measure("F1F4CN")
    f1, f2, f3, f4, clr, nir = self.sensor.get_spectral_data()
    self.sensor.start_measure("F5F8CN")
    f5, f6, f7, f8, clr, nir = self.sensor.get_spectral_data()
    clr, nir          # discarded
    return [f1, f2, f3, f4, f5, f6, f7, f8]
```

The 2026-09-09 23:42 session inferred this seam from the correlation structure
of 72 repeat reads (within-half correlation +0.970 / +0.978, across the seam
+0.649). It is now confirmed from the code. `Clear` is sampled in *both* cycles
and thrown away in both — it is exactly the factor needed to stitch the halves.

### 3d. Gain and integration time, and the headroom

`Sensor(atime=200, astep=999, gain=128)`, all defaults, never overridden.

- Integration time = `(atime+1) * (astep+1) * 2.78 us` = **558.8 ms per cycle**,
  so **1.118 s for a full 8-channel reading**. Measured MQTT round trip on
  2026-09-10 was 1.40–1.46 s, i.e. integration is ~80% of it. Independent
  corroboration of §3c.
- Gain is **128x**; the AS7341 supports up to **512x**, so there is 4x of
  unused gain.
- Largest single channel ever recorded here with the rail lights on: **3216
  counts of 65535 full scale = 4.9%**.

---

## 4. The accuracy steps taken on #197, with what each was worth

Units, because they were mixed up earlier in the issue:

- **counts** — one channel's raw ADC output, 0..65535.
- **share** — one channel's counts divided by *that same reading's* total counts
  across all 8 channels, x100.
- **share point** — one percentage point of share. The unit an error and a
  colour signal are compared in.
- **resolution floor** — 2x the standard deviation of a channel's share across
  the repeat reads at one position, worst channel, in share points. A sample
  that moves a channel's share by less than this is indistinguishable from
  doing nothing.

For scale: the largest colour signal this rig has ever produced is **2.61 share
points**.

| # | step | what it was worth | when |
| --- | --- | --- | --- |
| 1 | **OT-2 rail lights on** | resolution floor 0.017 -> 0.417 share points off vs on (recomputed 2026-09-11 from the committed JSON; the 2026-09-10 write-up reported 0.018 / 0.338 using a slightly different estimator). 5.6x the signal: mean total 15224 counts lit vs 2724 unlit | 2026-09-10 |
| 2 | **Per-position blank, not one blank per plate** | using a neighbouring stop's blank injects 0.295 share points | 2026-09-10 |
| 3 | **Subtract the sealed offset before dividing** | the ~440-count green glow is 8.3% of ch510 counts lit, 38.3% unlit; subtracting it is arithmetically identical to removing the lamp, residual 0.00 share points | 2026-09-10 |
| 4 | **Nobody at the machine during a reading** | 1.40 share points; a forearm over an open deck raised the total 31.7% in 1.4 s with the gantry parked | 2026-09-10 |
| 5 | **Match the blank's read height to the sample's** | 3.12-9.67 share points if mismatched -- larger than the whole signal | 2026-09-10 |
| 6 | **Match the blank's lights state to the sample's** | 2.55-2.80 share points if mismatched -- also larger than the whole signal | 2026-09-10 |
| 7 | **Read at z 120 rather than 128** | empty-slot between-stop colour disagreement 0.8% of share at z 120 vs 55.7% at z 128 | 2026-09-09 |
| 8 | **Timestamp every reading** | the MongoDB `timestamp` was the batch write time: median 103 s late, worst 258 s, across 122 pre-fix documents | 2026-09-10 |
| 9 | **A stability gate on the repeat reads** | flags any position whose 3 reads disagree by more than 0.5% of that position's own total counts; catches a changed background without needing the video | 2026-09-10 |

**None of these produced a colour measurement.** Every run on #197 to date has
been an empty slot, a bare deck, or vials sitting outside the sensor's field of
view. The steps above are the instrument being characterised, not the experiment
being done.

---

## 5. What upstream did that #197 has not

In descending order of how much it appears to have mattered:

1. **A light panel under the plate.** §1b step 1. Neither AC success relied on
   ambient light; the 2025 run used the rail lights in a darkened room, the 2026
   run used a transmission panel. #197 has the rail lights (step 1 above) and
   nothing under the sample.
2. **A 96-well plate instead of vials.** Liquid sits *down in* a well, so the
   aperture can be brought to the surface with `plate[well].top(z=-1.3)` --
   1.3 mm below the rim -- instead of being blocked by a 36 mm vial standing on
   the deck. This is what made #197's whole height series necessary, and it is
   the thing that removes it.
3. **A blank of the same well.** Both AC successes normalise per well. #197
   derived the same requirement independently (steps 2, 5, 6) but has never run
   a genuine blank/sample pair.
4. **Room light excluded** -- curtains, or a darkened room.
5. **Labware definitions instead of hardcoded deck coordinates**, so a
   calibration done once in the Opentrons App applies everywhere. See the
   README section on that.

---

## Sources

- [ac-dev-lab#152](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152) -- Winter 2025 practical; the white-reference result
- [ac-dev-lab#552](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552) -- Winter 2026 practical; the light panel and blank normalisation
- [ac-dev-lab#87](https://github.com/AccelerationConsortium/ac-dev-lab/issues/87) -- AS7341 in the housing; the LED experiments
- [ac-dev-lab#64](https://github.com/AccelerationConsortium/ac-dev-lab/issues/64) -- the fake-tip housing wearing out; 2.5 mm design survived ~7000 pickups
- [wireless-color-sensor](https://github.com/AccelerationConsortium/wireless-color-sensor) -- firmware, CAD, assembly docs
- [byu-vcl#33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33), [#103](https://github.com/vertical-cloud-lab/byu-vcl/issues/103), [#115](https://github.com/vertical-cloud-lab/byu-vcl/issues/115), [#166](https://github.com/vertical-cloud-lab/byu-vcl/issues/166) -- this repo's OT-2 and blackout work

# 2026-10-20: set-up only, run deferred to Oct 21

Gage spent the afternoon setting the atomizer up and ran out of time before a run. By
15:51 MDT it was loaded and ready for Oct 21
([#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261)).
The videos were still uploading to YouTube at the time. None of them were public on the
lab channel at 23:30 UTC, so this record is built from the written note alone. Add the
video links to the table below once they are up, and the analysis can be done from them
the same way as for [Oct 8](../2026-10-08/README.md) (on PR #268).

| Video | Length | What it covers |
| --- | --- | --- |
| *(not yet linked)* | | |

## What went into the set-up

In order, from the note:

1. **The argon tank was empty** when checked, so it was swapped before anything else.
2. **The ultrasonic stack was rebuilt for a small Mo plate and the 1.5:1 booster.** This
   is the configuration the repeatability plan calls for (1.5:1 booster, fixed amplitude,
   Mo or CF plates; [plan](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6216453097)).
   Oct 8 used CF with the 1.5:1 booster and only dripped. Ronnie's Oct 9 note says the slow,
   steady drip seen on Oct 8 would probably have atomized on a Mo plate. Oct 21 is the
   first test of that.
3. **The furnace was inspected and cleaned again.**
4. **On start-up something was not sealing, and air was leaking in.** The note does not
   say which seal, or how it was found and fixed.

Result: loaded and ready, but no run. Set-up took the whole afternoon.

## Why this matters for the repeatability study

- **Set-up variation is run-to-run variation.** Each of the four steps above can change
  the next run: a fresh tank, a rebuilt stack (torque, plate clocking, landing point), a
  freshly cleaned furnace and a reseated seal. If Oct 21 is run 1 of the baseline, write
  down the state of each, or the spread across runs will be partly a spread in set-up.
- **The leak goes straight into O2.** O2 has been the slowest thing to bring down (Oct 6
  went from 19 to 140 ppm during the run; Oct 8 needed three gas washes at 500 °C to reach
  25–26 ppm). If the leaking seal was the cause of either, Oct 21's O2 curve should be
  visibly better. Record the O2 after each wash, and at the start and end of the pour.
- **The stack was rebuilt, so the landing point has to be checked again.** Three runs in a
  row (Oct 2, 6, 8) failed where the melt meets the plate. Before heating, check where the
  stream will land, high on the plate's face and clear of the upper sonotrode (Ø0.785 in ×
  2.23 in). The trainer suggested a laser pointer for this. The plate comes off at 45° and
  is 4.71 × 0.82 in, with no overhang behind the sonotrodes.
- **Set-up is eating the run days.** If set-up keeps taking a full afternoon, the 5–8
  baseline runs take weeks. Timing each step once would show where the time goes (waiting
  on gas, cleaning, leak hunting).

## For the Oct 21 run

Settings to hold, from the plan and the Oct 8 notes:

| Setting | Value |
| --- | --- |
| Alloy | Al 6063 |
| Plate | small Mo |
| Booster | 1.5:1 |
| Amplitude | 90 (set it; on Oct 6 it was left at 50) |
| Charge | 250–350 g, weighed |
| Graining pressure | 0.19 bar, as on Oct 8, to see if the slow drip repeats |
| Melt temperature, melt time | as on Oct 6 (840 °C, 2 min) unless changed on purpose |

Before the pour:

- [ ] Check the nozzle exit for frozen globs (Ronnie found some on Oct 9 and picked them
      out with tweezers).
- [ ] Check the stream's landing point on the plate.
- [ ] Start the ultrasonic system **before** opening the sealing pin (missed on Oct 6).
- [ ] Note which seal leaked on Oct 20 and how it was fixed.

During and after:

- [ ] O2 after each wash, and at pour start and end.
- [ ] Film the ultrasonic panel during the pour. On Oct 8 it read POWER 0 W throughout,
      and nobody knows yet whether it reads above 0 W while atomizing.
- [ ] Weigh the powder, any lump on the plate and anything in the cup, to get yield.
- [ ] Then PSD (sieves, #262), SEM sphericity and composition per the plan.

## Open questions for Gage

- Which seal leaked, and how was it found?
- Was the tank empty because of a leak or just use? If a leak, that is the same question.
- How was the chamber left overnight: under argon, or open to air with the charge in?
- How long did each step take?

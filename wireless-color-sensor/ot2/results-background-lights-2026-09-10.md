# The empty-deck background, with and without the rail lights — 2026-09-10

Asked on #197, with the coloured vials taken off the deck, for a reading of the
background the vials sit against; for the OT-2's rail lights to be on for tests
from here on; and for the deck photos to come back the right way up.

All three done. Two full pick-scan-reseat cycles ran at **slot 7, read z 129,
press z 90.0** — the exact pose the last paint run used — differing only in the
rail lights. Nobody was near the machine for either.

## What the rail lights buy

| | lights **ON** | lights off | |
| --- | --- | --- | --- |
| Mean total over the 3 stops | **15224** | 2724 | **5.6× more signal** |
| Worst read-to-read spread | **0.31 %** | 2.71 % | 8.7× better |
| Positions over the 0.5 % stability gate | **0 of 3** | 1 of 3 | |
| Internal offset as a share of the reading | **3.1 %** | 14.9 % | 4.8× less |
| … on ch510 specifically | **8.3 %** | 38.3 % | 4.6× less |
| Total swing across the 3 stops | 6.7 % | **2.2 %** | *lights are worse* |
| Colour disagreement between stops | 0.30 pts | **0.11 pts** | *lights are worse* |

The first four rows are the case for leaving them on. The last two are the
honest cost, and they are the same effect seen twice: **the rails are not
uniform over the deck**, so they add a gradient of their own along X.

That trade is worth taking, because the two kinds of error are not equally
harmful:

* The unlit run's 2.71 % is a **step** — position 2's third read drops to 2685
  and positions read afterwards stay at that lower level. The room changed
  mid-run and stayed changed. No blank can cancel a background that moved
  between the blank and the sample.
* The lit run's 6.7 % X gradient is **fixed geometry**. A lamp bolted to the
  machine illuminates x = 93.88 more brightly than x = 33.88 today, tomorrow
  and next week. That is exactly what a per-position blank divides out.

Controlled illumination converts a random error into a systematic one, and
`blank_correction.py` removes systematic ones.

## The background, lit — the reference for the paint run

Empty deck, slot 7, read z 129, press z 90.0, rail lights on. Mean of 3 reads.

| x (mm) | 410 | 440 | 470 | 510 | 550 | 583 | 620 | 670 | **total** | spread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33.88 | 235 | 1102 | 1047 | 1924 | 2681 | 3020 | 2978 | 1769 | **14756** | 0.01 % |
| 63.88 | 243 | 1147 | 1082 | 1971 | 2744 | 3086 | 3046 | 1817 | **15136** | 0.31 % |
| 93.88 | 254 | 1226 | 1136 | 2060 | 2866 | 3216 | 3153 | 1869 | **15779** | 0.02 % |
| — | 6 | 5 | 12 | 165 | 177 | 45 | 30 | 27 | *467 seated* | |

**This is only a blank for a sample read at this exact pose and with the lights
on.** Two things make an old blank useless: a different `--read-z`, and a
different lights state. The lights change the *seated* offset too — 467 lit
against 406 unlit, so the closed enclosure leaks ~15 % of its own background in
from the rails.

## The internal offset is the quieter win

`analyse_instrument_artefacts.py` found a fixed additive term inside the closed
enclosure — a green indicator LED, ~440 counts, peaked at 510/550 nm, that
`blank_correction.py` must subtract from both sample and blank *before*
dividing. Being additive, it hurts in proportion to how little signal there is:

| | ch510 offset share |
| --- | --- |
| 2026-09-09, read z 128, unlit | 36–47 % |
| 2026-09-10, read z 129, unlit | 38.3 % |
| **2026-09-10, read z 129, lit** | **8.3 %** |

Turning the lights on did more for this than any of the height changes tried on
2026-09-09, and it did it without moving the sensor nearer the sample.

## Headroom is still there

Largest single channel across the lit run: **3216 of 65535, 4.9 % of full
scale.** The 5.6× gain did not cost dynamic range — there is still ~20× of it
unused, so the gain and integration-time registers remain the cheapest
untried improvement, and brighter is not yet a risk.

## The module did not release at the end of the second cycle

The lights-off cycle finished with a reseat-confirmation read of **1010 counts
against a seated 406**. `dropTipInPlace` fired and the module stayed on the
nozzle; the gantry homed still carrying it. The deck photo shows it in the air
over the back-right of the deck, held on the pipette, base empty.

This is a **different failure from 2026-09-09**, when the module came off
entirely and lay on the deck. The distinction decides whether it can be fixed
without hands:

* on the deck → position and orientation unknown, so pressing the nozzle on it
  is blind. Needs a person.
* on the nozzle → position exactly known, and the identical release had
  succeeded four minutes earlier at the same press depth. Ordinary recovery.

`reseat_module.py` does that recovery and was used here: **1016 → 419 counts**,
confirmed by photo. It reads the sensor first and refuses to move if the module
is already seated, and `--check` reports without any motion at all.

**This is the other edge of the 0.5 mm deeper press** added on 2026-09-09 to
stop the module falling off mid-carry. A fit tight enough not to shed the
module in transit is also a fit that sometimes will not let go of it. The
failure mode has moved from "module on the floor" to "module still aboard",
which is the better of the two, but the press depth is now bracketed on both
sides and worth revisiting with a person watching.

Also worth noting: the **grip check was 3.2× on the cycle that failed to
release**, against 4.6–5.3× on every cycle that released cleanly. That is the
lowest on record. It is a light reading rather than a force measurement, so it
cannot be read as "grip strength" — but as a *flag* it fired on the one cycle
that went wrong, and it is free.

## The deck photos were upside down, and the correction was a no-op

`deck_photo.py` rotated the frame by a quarter turn, and the OT-2's camera is
mounted **inverted**, so the correct turn is a half turn. That was one bug. The
other was worse: `rotate()` returned the frame *untouched* when Pillow was
missing, and **Pillow was not installed on the stream-cam Pi**, which is the
only machine that can reach the robot. So the correction never ran once, and
never said so.

Both are fixed. `rotate()` now raises rather than silently passing the frame
through, `deck_photo.py` exits non-zero and prints `BUT IT IS UPSIDE DOWN` if
it cannot rotate, and `--fix FILE` corrects an already-saved frame elsewhere.
Pillow is now in `~/.venvs/xscan` on the Pi. The 14 robot-camera frames
committed on 2026-09-09 and 2026-09-10 have been turned upright in place.

**One conclusion changes.** The 19:41 session read its upside-down frame as
"the three vials are on the deck now rather than off on the ledge". Turned the
right way up, the same frame shows them **off** the deck, on the bench to the
right — where they still are. Upright, slot 1 is front-left and the trash in
slot 12 is back-right.

## Files

| file | what |
| --- | --- |
| `background-lightson-2026-09-10.json` | 15 readings, the lit background |
| `background-lightsoff-2026-09-10.json` | 15 readings, the unlit control |
| `analyse_rail_lights.py` | the comparison and the figure |
| `rail-lights-2026-09-10.png` | the figure |
| `reseat_module.py` | recovery when a release fails to let go |
| `deck-background-{before,after,reseated}-2026-09-10.jpg` | deck, upright |

All 30 readings are also in `digital-wetlab.sensor-data`, with `run.lights`
recorded on every document.

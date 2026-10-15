# 2026-10-02 — what the blackout did: less stray light, steadier readings, no measurable colour gain

Asked on [PR #202](https://github.com/vertical-cloud-lab/byu-vcl/pull/202) by
@timothy-commins: now that the OT-2 is temporarily blacked out, how did that affect
the accuracy? No hardware moved. [`analyse_blackout.py`](analyse_blackout.py) works
from runs already on file and writes [`blackout-2026-10-02.json`](blackout-2026-10-02.json)
and the chart.

The OT-2 went dark in two steps:

| stage | when | runs on file |
| --- | --- | --- |
| no blackout | 2026-09-30 morning | 09:53, 10:22, 10:46, 11:18 |
| sides covered | between the 11:18 and 13:19 runs of 09-30 (noted by Tim at 13:47) | 13:19, 15:36, 16:13, 19:14 |
| sides + cardboard and wood | 2026-10-01, ~13:30 | 13:43 |

![light at three fixed spots by stage; colour error at matched heights before and after the cardboard](blackout-2026-10-02.png)

## 1. How much light it removed

Every run on file from 09-30 10:22 on, except 19:14, picks the enclosure up from socket
A2 (92.8, 316.5) and reads at the same three spots on the way out. No paint or plate is involved there, so
those readings change only with the light. Board lamp (406.5 counts, the sealed
reading of 09-10) subtracted:

| spot | no blackout | sides covered | + cardboard | sides removed | cardboard removed, of what was left |
| --- | --- | --- | --- | --- | --- |
| z 93, just lifted | 628 | 485 | 411 | 23% | 15% |
| z 110, above the socket | 5,348 | 4,050 | 3,629 | 24% | 10% |
| z 190, carry height | 12,349 | 9,550 | 8,914 | 23% | 7% |

Within a stage the runs agree to ≤ 1.1% (z 110 and 190) and ≤ 3% (z 93), hours apart,
so the two steps are the blackout, not drift. Together they removed 28–35% of the light
at these spots.

The light the cardboard took out was **warmer than the rail lights'**: 440 nm ÷ 620 nm is
0.21–0.24 for the removed light against 0.42–0.44 for what is left. So the light inside
is now slightly bluer, and all of it is rail light: on 10-01, with the rail lights off,
the enclosure on the white well read `[4.5, 2.0, 8.0, 162.2, 169.0, 33.7, 13.2, 8.3]`,
the board's own lamp and nothing else.

## 2. Steadier readings, though not all of it is the blackout

Two readings in a row at one spot, ~1.5 s apart, nothing moving:

| run | stage | pairs | median | largest | over 0.5% |
| --- | --- | --- | --- | --- | --- |
| 09-30 09:53, 10:31, 10:54 | none | 100 | 0.01–0.02% | 0.10% | 0 |
| 09-30 11:26 (Tim watching) | none | 49 | 0.015% | 1.75% | 3 |
| 09-30 13:19 | sides | 52 | 0.13% | 2.30% | 10 |
| 09-30 15:36, 16:13 | sides | 106 | 0.02–0.03% | 1.88% | 2 |
| 09-30 19:14 | sides | 87 | 0.065% | **5.35%** | 15 |
| **10-01 13:49** | **cardboard** | **151** | **0.022%** | **0.24%** | **0** |

The jumps came and went with the run, not with the stage: the quiet 09-30 morning runs,
with no blackout at all, were as steady as 10-01. And at contact, 19:14's red wandered
by 3% and 8% on its two landings while the yellow, read in between, held to 0.1%. That
looks more like the enclosure settling on the plate (or the wet paint) than like light.
What the blackout does guarantee is that someone moving in the lab can no longer change
the light the sensor gets: there is none left from outside.

They mattered. The largest (red, 6,040 → 5,725) moved its white/black-calibrated colour
by 0.06–0.20 per channel, as much as the whole colour error. Within one landing at
contact, a calibrated colour scattered by SD 0.022–0.024 on 09-30's red and ≤ 0.002
on every well on 10-01.

## 3. Colour accuracy: no measurable gain from the cardboard

The 09-30 19:14 run (sides covered) and 10-01 (cardboard) read the same five wells at
the same heights. Both scored like [`analyse_height_series.py`](analyse_height_series.py):
white/black-calibrated at each height, mean miss against the published pigment ranges,
440–670 nm. 10-01 at z ≤ 90 uses the re-scored values (white from the second H12
landing, [`landing_shift.py`](landing_shift.py)).

| nozzle z | 125 | 90 | 89 | 88 | 87 | 86.5 |
| --- | --- | --- | --- | --- | --- | --- |
| sides covered (09-30 19:14) | 0.24 | 0.18 | 0.10 | 0.16 | 0.12 | 0.13 |
| … with red's 2nd landing | 0.24 | 0.20 | 0.16 | 0.21 | 0.18 | 0.16 |
| + cardboard (10-01) | **0.15** | 0.27 | 0.34 | 0.43 | 0.44 | **0.44** |

**Better 37 mm up, worse resting on the plate.** Neither change can be pinned on the
cardboard, because between the two runs the plate moved from slot 1 to slot 7, the paint
aged ~19 h, and the enclosure hung from the other socket.

- **At z 125** the 09-30 colours were squeezed 52× (barely told apart), 10-01's 2.4×.
  09-30's row was also unevenly lit there: blue (H10) read 7% brighter than yellow (H2),
  the reverse of the paints (on 10-01 yellow read 4.5% brighter), so the light was
  stronger towards the row's right-hand end. Uneven light is the one kind of room light a white/black correction can't remove,
  so the cardboard may have helped here. The slot move could do the same.
- **In contact** the paint and the plate are the likelier causes. The light that reaches
  a well through the clear plate made the empty well read brighter than the white both
  before the cardboard (09-30 15:47: 1.09–1.21× per channel) and after it (10-01:
  1.02–1.29×), so that path was there before.

**Why the blackout can't fix the rest.** A steady, even room light is already cancelled
by the white/black correction; only its changes and its unevenness hurt. The error left
on 10-01 comes from the rail lights themselves: light reaching the sensor up through the
clear plate and from the empty wells and deck in view (§1 of
[`results-height-series-2026-10-01.md`](results-height-series-2026-10-01.md)).

## What to do with it

- **Keep the blackout.** A 1% change is now a real change.
- **The black paper won't take out more room light; there is none left.** It may change
  how much rail light the walls bounce back (cardboard is brown), so re-read the white
  and black wells after it goes up.
- **To measure the blackout on its own:** one run reading the same wells with the
  cardboard on, then off, same plate and pick-up. Needs someone to take the cardboard off.
- **The levers for the colour error are geometric:** read higher (z 95–100) and black
  paper *under* the plate.

## Files

| file | what |
| --- | --- |
| [`analyse_blackout.py`](analyse_blackout.py) | all three comparisons and the chart |
| [`blackout-2026-10-02.json`](blackout-2026-10-02.json) | per-run fixed-spot readings, every pair's difference summary, matched-height scores, scatter |
| [`blackout-2026-10-02.png`](blackout-2026-10-02.png) | the chart |

# Every colour measurement, timestamped and linked to the livestream

Asked on #197 for timestamped livestream links, a frame of the deck at each
measurement instant, and a small spectrum plot per test in the style of
[`scripts/basic_plotting.py`](https://huggingface.co/spaces/AccelerationConsortium/light-mixing/blob/main/scripts/basic_plotting.py)
from the light-mixing Space.

All three exist now, for all 114 readings of the 2026-09-09 session:

| artefact | what |
| --- | --- |
| `measurement-stream-index.md` / `.json` | 114 readings, each with its UTC instant and a `?t=` link |
| `measurement-gallery.md` | the 27 scan positions as frame + spectrum + link |
| `frames/` | 27 livestream frames, each verified against the burned-in clock |
| `spectra/` | 27 × 300 px spectra, `basic_plotting.py` style |

Regenerate with `stream_index.py` → `frames_from_stream.py` → `plot_spectra.py`
→ `build_gallery.py`.

## The readings were not properly timestamped. They are now.

The question in the request was well aimed: **there was no timestamp on a
reading.** `sensor_read.SensorLink.read` returned channels, a total and a
latency, and nothing else. The only recoverable instant was an accident of
naming — the epoch-ms that `experiment_id` happens to embed:

```python
experiment_id = f"{label or 'read'}-{int(time.time() * 1000)}"
```

Worse, the field that *looked* like a timestamp was the wrong one.
`store_in_mongodb` stamped every document with `utcnow()` at insert time, and
insert happens once, after the whole run:

```python
docs.append({"timestamp": utcnow(), ...})   # every doc in the batch, identical
```

So all fifteen documents of a run carried one time, up to **three minutes after**
the reading each of them describes. Anyone lining `digital-wetlab.sensor-data`
up against a clock — the livestream, a lab notebook, a photograph — would have
been misled, and silently.

Fixed in two places:

* `sensor_read.py` now returns `t_request_utc`, `t_response_utc` and their epoch
  forms. The measurement is *bracketed* by those two rather than given a single
  false-precision instant: the board integrates somewhere between the command
  going out and the answer coming back, nearer the latter. One clock read now
  feeds both `experiment_id` and the explicit field, so they cannot disagree.
* `run_xscan_test.py` writes the reading's own response time as `timestamp`, and
  keeps the batch write time separately as `stored_at`.

`stream_index.py` prefers the explicit fields when they are there and falls back
to the `experiment_id` reconstruction for everything already recorded, so the
2026-09-09 data is fully recoverable.

## The archive timeline is not wall clock, and it is not a drift

The session sits inside one segment of the rolling OT-2 stream:
[`bQDrYpT3vaE`](https://www.youtube.com/watch?v=bQDrYpT3vaE), *OT-2 stream
picam-ot2, 2026-09-08 UTC 19:00*, 7 h 57 m, `release_timestamp`
2026-09-08T19:01:16Z.

Computing `t - release_timestamp` and calling it the video offset is wrong here:

| video offset asked for | clock burned into the returned frame | `release + offset` | error |
| --- | --- | --- | --- |
| 5 s | `2026-09-08_13-01-15` | 19:01:21Z | **−6 s** |
| 11 000 s | `2026-09-08_16-05-43` | 22:04:36Z | **+67 s** |
| 22 161 s | `2026-09-08_19-11-44` | 01:10:37Z | **+67 s** |
| 26 900 s | `2026-09-08_20-30-43` | 02:29:36Z | **+67 s** |

A constant 67 s from the third hour onward, and *not* a drift — a step, which is
what an archive that concatenates across a stall looks like. At 17–20 s per scan
position, 67 s is more than one read position: naive links would have pointed at
the wrong measurement, plausibly enough that nobody would have noticed.

The fix is that the stream burns `%Y-%m-%d_%H-%M-%S` (lab local, UTC−6) into
every frame, so `frames_from_stream.py` closes the loop — grab at the estimated
offset, OCR the overlay, and if it disagrees, shift by exactly the error and
grab again. **All 27 frames landed within 1 s of their intended instant on the
first pass**, and each one's OCR'd clock is recorded next to it in
`frames/frames.json`. The links are verified, not asserted.

Practical note for anyone reproducing this: YouTube refuses player extraction
from a GitHub Actions runner ("Sign in to confirm you're not a bot"), so the
fetching runs over SSH on the stream-cam Pi. The channel listing works from
anywhere; only the player does not.

## What the frames show: eleven of the 27 measurements had a person in shot

This is the part worth the effort, and it is not visible anywhere in the data.

| run | positions | what the frames show |
| --- | --- | --- |
| 1 — slot 8, z 120 | 01:13 | **hand holding a yellow vial** beside the module at pos 1 and 2, head in shot |
| 2 — slot 7, z 125 | 01:28–01:29 | **hand placing a red vial** at pos 1 and 2; the vial is standing on the deck at pos 3 |
| 3 — slot 7, z 120 | 01:32–01:33 | clear and genuinely empty at all three |
| 4 — slot 7, z 128 | 01:43 | **the vials are being placed during the run** — a person fills half the frame at pos 1, an arm crosses the deck at pos 2, all three vials are down by pos 3 |
| 5 — paint, 3 positions | 01:52–01:53 | vials in place; a hand and a dark object at the right edge at pos 2 |
| 6 — **9-position sweep** | 01:58–02:00 | **all nine clear**, vials in place, nobody in shot |
| 7 — slot 7, z 129 | 02:22 | **hand in shot** at pos 1 and 2 |

Two consequences follow directly, and they undercut conclusions drawn earlier in
the session.

**The "empty-slot baseline at z 128" was never an empty slot.** Run 4 is the
reference the paint run was normalised against, and the source of the claim that
the instrument disagrees with itself about the colour of an empty slot by 7.69
points at that height. The frames show the vials being carried in and set down
*during* those very readings, with a person between the room lights and the
aperture. Every ratio computed against it — including the "yellow" signature at
x = 33.88 — is measuring that, not the paint.

**The height series compared one clean run against two contaminated ones.** The
monotone "every millimetre up makes it worse" ran z 120 → z 125 → z 128. Of
those, only z 120 is clear in the frames; z 125 has a hand and a red vial in shot
at two of three positions and z 128 is the run above. The ranking may still be
right — the geometry argument for it is independent — but this data cannot
support it, and the effect sizes attributed to 5 mm and 8 mm of height are not
separable from a person leaning over the deck.

These are ambient-light readings — the module's own LEDs are inert, established
[earlier in this session](results-paint-2026-09-09.md) — so a body between the
lights and a non-light-tight enclosure is not a hypothetical confound.

**What survives.** The **9-position sweep** is the one run with the vials in
place and nobody in shot for all nine positions, and it was already the run whose
conclusion rested on a within-run comparison. Run 3 (slot 7, z 120) is the one
genuinely clean empty-slot reference on record — but it is at a different height
than the paint runs, so it cannot serve as their denominator. **There is no
uncontaminated empty-slot reference at z 128.** Getting one is a five-minute run
with nobody near the machine.

## Prior art: `AccelerationConsortium/ac-dev-lab#552`

The same demo, run for the Winter 2026 MSE403H1 practical, hit exactly this wall
and the thread is worth reading before the next attempt:

* "It seems the sensor is much more responsive to the lighting conditions than
  the colour in the well... Channel intensities seemed to move together, probably
  due to changes in lighting conditions" — the identical failure mode, found
  independently ([comment](https://github.com/AccelerationConsortium/ac-dev-lab/issues/552#issuecomment-4019810830)).
* Their fixes, in order of how much they helped: a **light panel underneath the
  plate** for even, controlled illumination; **blackout curtains** round the
  machine; and **normalising every well against a blank reading of that same
  well**, which is the same per-position reference this session kept arriving at.
* Blank-well data showed real well-to-well variation and a usable coefficient of
  variation *within* a well — i.e. normalisation worked, but only against a blank
  taken at the same place.
* Acrylic paint is the material that worked for them; food dye and milk were
  tried and were worse. See also
  [ac-dev-lab#87](https://github.com/AccelerationConsortium/ac-dev-lab/issues/87)
  on how much the printed housing itself changes the results.
* Mechanically: the housing's fake-tip region wears out and the sensor starts
  being dropped — which is what happened here on 2026-09-09. Their fix was to
  reprint it; the 2.5 mm design survived ~7000 pickups.

The one thing they had that this setup does not is a light source. Until the
module lights its own sample, every number here is a measurement of the room —
which is why a person walking up to the machine shows up in the data at all.

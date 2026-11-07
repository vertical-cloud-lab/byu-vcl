# Maintenance in the workflow: the clip (`upkeep_clip.py`)

Sterling, on PR #318 (2026-11-07): "Something that's been on my mind is maintenance over long-term and how that gets
handled in workflows." `notes/upkeep.md` answers that in words and numbers. This clip shows three of the answers
happening, in the lab as the set-up movie leaves it.

```bash
PREVIEW=1 xvfb-run -a python3 upkeep_clip.py       # the last frame of each sub-step -> /tmp/preview_upkeep_clip.png
ARM_AUDIT=1 xvfb-run -a python3 upkeep_clip.py     # every frame collision-checked -> out/collisions/
VIZ3D_FPS=6 xvfb-run -a python3 upkeep_clip.py     # -> out/mp4/upkeep_clip.mp4, out/upkeep_clip.gif, .json, still
```

`VLAB_ONLY_TRAYS=BE` is the default: only trays B and E, the two the clip presents, are populated. The Shuttles are
clad, so the empty trays aren't seen.

## The render

- **[MP4](../out/mp4/upkeep_clip.mp4):** 701 frames at 6 fps, 1280 × 720, 116.8 s, 6.0 MB.
  - Part 1, the week: frames 0-78.
  - Part 2, the check: frames 79-399.
  - Part 3, the tip change: frames 401-700.
- **[GIF](../out/upkeep_clip.gif):** 512 px at 3 fps, 2.5 MB. **[Still](../out/upkeep_clip_still.png).**
- **The control chart, both versions:** [today's check](../out/upkeep_clip_chart.png) and
  [the what-if](../out/upkeep_clip_chart_whatif.png).
- **[Arm audit](../out/collisions/upkeep_clip.json):** 534 frames checked, **0 in collision**.
  - FCL mesh-mesh on the drawn meshes, every frame after its update.
  - The world was what the arm can reach from Shuttle 1's dock (493 of 1,268 actors).
  - The forearm and wrist rose to 1,585 mm at most.
- **Cost:** 13.5 min in one slot (22:57-23:11 UTC), `VLAB_ONLY_TRAYS=BE`. The audit took 2.5 min, the preview 2.5 min
  once the cache was built.
- **Fixed after the preview (round 10's continuation):**
  - **The reading's camera.** It had the weight behind the doser's vertical extrusion. It now looks along the
    close-up's clear line of sight, nearer, with the weight a third of the way across, clear of the chart.
  - **The tip change's camera.** It sat behind the person's shoulder. It now looks along the extraction view's line,
    closer, with the person to the left of the iMicro.
  - **The captions.** They no longer say the HR-202i calibrates itself, and they say the check weighs ten times.
  - **The fused-silica check** is the arm's next job on tray E. The clip had claimed it ran while the tray went back
    up.

## What it shows

### 1/3 The week

`out/upkeep_week.png`, full frame: one steady-state week of the model with every station's bookings. Process steps
are grey; upkeep is coloured by who does it:
- the arm's checks at night;
- the person's tasks on the weekday shift, round the crucible hours;
- vendors;
- faults waiting for the next shift.

### 2/3 A check between jobs

`upkeep.py` task `bal_weights`: daily, the arm, 0.2 h, at night.
- **The weight.** The A&D HR-202i under the multi-doser's dose point is checked with a 100 g OIML class E2 weight.
  The weight lives in tray J's store and rides on the MiR's deck in a low seat of its own (ours).
- **Into the balance.** The arm takes the weight by its body, as weight tongs would, and stands it on our vessel
  shuttle's fork outside the doser. The shuttle carries it through the balance's side door onto the pedestal on the
  pan and backs out, as round 9's 8:37 clip sets a vial.
- **The reading.** It settles to 100.0001 g. The shuttle lifts the weight off and back ten times, for USP <41>'s
  repeatability (one is shown). The mean goes on a control chart against the lab's limits.
- **The what-if.** A reading outside the limits is repeated once. Still out, the doser is flagged, no doses are booked
  on it, and a person's task is booked for the next shift.
- **Back.** The weight goes back to its seat on the deck and tray B goes back up.

**No internal mass.** A&D's [HR-i manual](https://www.aandd.jp/products/manual/balances/hr-i.pdf) calibrates the
HR-202i "using a weight that you have". So this weight is its daily check and, once a month, its calibration
(`bal_cal`). The first version of the clip said the balance calibrated itself with a built-in mass, which is wrong for
the HR-i series.

### 3/3 A person's task, with the tray pulled out

`upkeep.py` task `nano_tip`: every 600 indentation runs, a person, the tray pulled out, 2 h.
1. Tray E comes to Shuttle 1's opening.
2. The MiR250 + UR10e drives off to Shuttle 2, which carries on working. Only Shuttle 1's opening is taken.
3. A person rolls an extraction table to the opening and docks it against the cover's lip.
4. The tray comes out onto the table's rails. Kardex's Shuttle XP brochure, p. 6: "With the full tray extraction
   device, a tray is placed in front of the access opening" (notes/maintenance.md). Off its dock the tray has no
   power, so the iMicro is shut down first.
5. The iMicro's hood lifts. The person, in gloves and safety glasses, unscrews the Berkovich tip and fits the new one.
6. The hood comes down, the tray rolls back onto its dock and the table goes away.
7. The MiR docks at Shuttle 1 again. The new tip's area function on fused silica is the arm's next job on tray E
   (`nano_fs`), before any sample, and the run count starts from zero.

At 304 alloys a year the tip falls due about every two years. So the model's first year has no planned extraction,
only one repair: a broken tip, with a 72 h wait for the part.

## What it assumes

| What | Value | Basis |
|---|---|---|
| Check weight | 100 g OIML E2, Ø24 mm, 37.5 mm tall, knob form | OIML R 111-1's shape, sized from the mass at 8.0 g/cm³ (estimated); E2's ±0.16 mg tolerance from its Table 1 |
| Limits | action ±0.3 mg, warning ±0.2 mg | ours: the HR-202i's ±0.2 mg linearity plus the E2 tolerance |
| Readings on the chart | 30 working days | illustrative, seeded |
| The weight's seat on the deck | 64 mm block, 3 mm pocket | ours |
| Extraction table | 2,360 × 900 mm, rails at the opening's 854 mm | assumed: Kardex publishes no size for its extraction device or its cart (notes/maintenance.md has the questions to ask) |
| The person | 1.75 m: lab coat, nitrile gloves, safety glasses | drawn here (`Person`): no figure existed in the codebase. The finale (`timelapse.py`) uses the same figure |
| The tip change | 2 h, every 600 runs | assumed (`upkeep.py nano_tip`) |

The person's arms are a two-link solve to each hand target, and their walk is a simple gait. Neither is checked for
contact with the tray or the table, so their hands are illustrative. `ARM_AUDIT` checks only the UR10e.

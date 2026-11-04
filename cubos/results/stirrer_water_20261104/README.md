# Stir test with water and the stir bar (2026-11-04): the fan didn't turn, and the Hall sensor saw nothing

Asked for by Ben on [PR #269](https://github.com/vertical-cloud-lab/byu-vcl/pull/269)
(23:12 UTC): he had put a vial filled with water, with the stir bar in it, on the compact
stirrer, and asked for a stir, filmed if the cameras could see it. An hour earlier, with the
holder on and no vial, the same stirrer spun and counted every turn
([`stirrer_spin_20261104`](../stirrer_spin_20261104/README.md)). **With the vial and bar in,
the fan did not start at any speed from 300 to 2000 rpm. The Hall sensor gave no pulses, the
firmware stopped each step after 12 s with `stalled` set, and nothing in camera 1's view of
the vial moved.** All times UTC (the lab is on MST, UTC−7). `~/cubxl_runs/HOLD` was set from
23:14:15.

## What the cameras see

The CubXL Pi has two cameras. Camera 0 (`deckcam.py`'s, overhead) sees the vial's black cap
from above and the bench around it. **Camera 1 sees the vial from the side**, above the
stirrer's cup, next to the second compact stirrer, which is empty
([full frame](frames/231423Z_camera1_full.jpg)). Through the glass there is a white block
that looks like the bar, but it is one of the cup's fingers: the empty cup shows the same
block in the same place relative to its screws ([side by side](frames/231423Z_camera1_cups_compared.jpg)).
The bar itself lies on the vial's floor, down inside the cup, and can't be made out. So
camera 1 can show the water moving, but not the bar.

<img src="frames/231423Z_camera1_cups_compared.jpg" width="640">

*Camera 1, 23:14:23, full resolution. Left: the vial in its cup. Right: the empty stirrer's
cup, with the same white block.*

## The run (23:19:13–23:23:01)

[`stir_video.py`](stir_video.py) ran on the Pi, started by [`watch_run.py`](watch_run.py) on
the runner, which also read the thread every 15 s for a request to stop. It filmed camera 1,
cropped to the vial (`--roi 0,0.716,0.375,0.284`, 864 × 368, 30 fps MJPEG, 20 ms shutter,
focus fixed at 1.16 dioptres), from 4 s before the first command to 8 s after the last. On
one connection to the Uno it then sent each step as `30,<rpm>,<seconds + 15>` and read `31`
every second ([log](water_1104.log), [data](water_1104.jsonl)).

| UTC | Asked | What `31` said |
|---|---|---|
| 23:19:21 | 300 rpm, 60 s | `rpm` 0.0 throughout; duty 0.300 → 0.315 as the stall kicks repeated; at 12.1 s `target` 0 and `stalled` 1 |
| 23:20:21 | 600 rpm, 30 s | the same, stalled at 12.1 s |
| 23:20:51 | 900 rpm, 30 s | the same |
| 23:21:22 | 1200 rpm, 30 s | the same |
| 23:21:52 | 1500 rpm, 30 s | the same |
| 23:22:22 | 2000 rpm, 30 s | the same |
| 23:22:53 | stop (`30,0`) | `rpm` 0.0 |

Each step is one full-power kick of 0.5 s, then five more after 0.75 s pauses as the
firmware found no pulses, so the fan got 36 kicks at 100 % duty in all. The speed asked for
makes no difference to that: the setpoint only ramps once pulses arrive. The Uno answered
every command, the Pi logged no USB event or over-current, and `get_throttled` stayed 0x0
with 5.11 V in.

## Did anything move?

<img src="stir_water_300rpm.gif" width="600">

*The first step, 23:19:18–23:19:34.5, with the Uno's replies burned in
([MP4](stir_water_300rpm.mp4), made by [`make_clip.py`](make_clip.py)). The kick starts at
23:19:21.1; the firmware gives up at 23:19:33.*

[`motion.py`](motion.py) measures how much each frame differs from the one before, over all
of the vial camera 1 sees, and over a patch of bare deck for the camera's own noise
([output](motion_output.txt), [per frame](water_1104_motion.csv)).

![frame-to-frame change over the vial and over bare deck, through all six steps](motion.png)

- **The vial changes less from frame to frame than bare deck does:** median 1.05 grey
  levels (99th percentile 1.17) against 1.37 (1.50). Water swirling, or a bar turning
  through the water, would change it far more than that.
- **No spike at the kicks.** The only local change is a highlight on the glass flickering at
  18 s and 23 s into the recording, during the first step's kicks: a few dozen pixels, which
  may be the water trembling. The larger bumps are in the deck patch too, so they are the
  light or the exposure, not the vial.

With no Hall pulses through 36 kicks and nothing moving in the vial, **the fan most likely
didn't turn at all.** Turning with the bar left behind, it would still have toggled the
sensor. Turning with the bar following, it would have moved the water.

## Why

Without the vial, the fan started on the first kick an hour earlier. With the vial and bar
on, it doesn't start, so the bar is what stops it. `BUILD.md` stage 8 expected the coupling
might be too strong (README [risk 1](../../../hardware/vial-stirrer-cubxl/README.md#risks-and-open-questions)):
the magnets are 2.4 mm from the vial, against about 7 mm on the Pioreactor. Two ways that
stops a 40 mm fan at 5 V:

1. **Breakaway.** The magnets pull the bar down onto the vial's floor. To start, the fan
   has to drag the bar round against that friction, and a fan at 5 V has little starting
   torque.
2. **The rotor is pulled up.** The bar also pulls the magnets, and the fan's rotor with
   them, up toward the vial. The carrier's top is 1.10 mm below the holder's ceiling
   ([MuJoCo check](../../../hardware/vial-stirrer-cubxl/README.md#interference-check-in-mujoco-2026-11-04)).
   If the fan's sleeve bearing lets the rotor rise that far, the carrier rubs the ceiling.
   Nobody has measured the rotor's end play.

The camera can't tell these apart, but one test with Ben at the bench can: start the fan
with the vial out, then lower the vial in while it runs. If it keeps turning, it was
breakaway. If it stops as the vial seats, the pull stops it outright. Either way, the fix
`BUILD.md` names is a spacer disc under the vial (1, 2 or 3 mm; none has been printed yet),
which weakens both.

## On the Pi

`~/stir_20261104b/` has `stir_video.py`, the logs, the full recording (`water_1104.mjpeg`,
236 MB, 6809 frames, not committed) and its frame times. `HOLD` was set at 23:14:15. Nothing
else on the Pi changed; `deckcam.py` was left as it was.

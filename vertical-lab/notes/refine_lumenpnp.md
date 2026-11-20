# The LumenPnP, rebuilt from Opulo's CAD and checked against Opulo's videos (#303, PR #318)

The old model was a guess: "Opulo publishes no overall size", so it took 680 × 680 × 450 mm from the 600 mm
extrusions and a photo (±15 %). Opulo does publish the whole machine, though, as CAD. The model is now built
from that CAD's numbers, and the video frames are used only to check it and to size the feeders, which the CAD
leaves out.

## Sources

**Opulo's repository**, [`opulo-inc/lumenpnp`](https://github.com/opulo-inc/lumenpnp) at
[`64cf68d`](https://github.com/opulo-inc/lumenpnp/tree/64cf68d5b7980f095ef11913065e7f45a1e3e447) (2026-10-14).
Nothing from it is committed here; it is cited only.
- [`src/assembly.FCStd`](https://github.com/opulo-inc/lumenpnp/blob/64cf68d5b7980f095ef11913065e7f45a1e3e447/src/assembly.FCStd)
  is the whole machine as a FreeCAD 1.0 assembly. Its 501 parts are stored as BREP, all in one frame. Reading the
  BREP bounding boxes and side profiles with OCP (cadquery's OpenCascade) gave every position in the model:
  - the seven 600 mm 20 × 20 extrusions: upper side rails at z 90–110, lower side rails at z 20–40, front and back
    rails at z 0–20 (y −20…0 and 430…450), and the X gantry at z 134.8–154.8;
  - the MGN12H rails: two 550 mm for Y, one 525 mm for X;
  - the leg and leg-extension side profiles, read as polygons. The front extensions are 30 mm wide where the legs
    are 40;
  - the Y gantries, the X motor and idler mounts, the yellow tension arms, and the head: front plate, carriage,
    the Z NEMA 17 turned 45° (the "diamond"), the two NEMA 11 Z gantries with the red and blue back plates, the
    nozzle holders 47.4 mm apart, and the down-looking camera 63 mm behind them in its white diffuser;
  - the feeder blades: 25 slots from x 102.6 to 497.6, a 15.8 mm pitch;
  - the bottom-vision parts, the control box under the left side, and both drag chains with their bends.
- [`src/CSM/staging-plate-offcenter.FCStd`](https://github.com/opulo-inc/lumenpnp/blob/64cf68d5b7980f095ef11913065e7f45a1e3e447/src/CSM/staging-plate-offcenter.FCStd)
  is 600 × 120 × 3.4 mm. [`build-plate.FCStd`](https://github.com/opulo-inc/lumenpnp/blob/64cf68d5b7980f095ef11913065e7f45a1e3e447/src/CSM/build-plate.FCStd)
  is 600 × 75 × 3 mm, and there are two of them. The FDM files `bottom-light-mount`, `bottom-vision-cover`,
  `discard-bin` and `cal-fid-mount` gave the sizes of the parts on and under the staging plate.
- [`bom.json`](https://github.com/opulo-inc/lumenpnp/blob/64cf68d5b7980f095ef11913065e7f45a1e3e447/bom.json)
  gives the quantities: seven extrusions, two NEMA 11s, four NEMA 17s, and leg extensions as standard. Its notes
  say the Z back plates are printed in red and blue PLA and the light mounts in white (they are diffusers).
- [`DESIGN_DECISIONS.md`](https://github.com/opulo-inc/lumenpnp/blob/64cf68d5b7980f095ef11913065e7f45a1e3e447/DESIGN_DECISIONS.md)
  explains the counterweighted Z: one NEMA 17 drives both Z gantries, so one nozzle goes up as the other goes
  down. It also gives boards up to 225 × 400 mm.

**Opulo's videos**, used for registration (the frames are fetched again through the Pi, not committed):

| View | Frame | What it shows |
|---|---|---|
| `v42_front_right` | [LumenPnP v4.2: Easy In-House SMT Assembly, 0:19](https://youtu.be/awn-P1sYTt0?t=19) | A v4.2 on a bench, low from the front right, no feeders |
| `v4_front` | [Introducing LumenPnP v4, 0:10](https://youtu.be/bvGPbwndZMQ?t=10) | A v4.0 in the studio from the front, full feeder rows |
| `v4_front_check` (held out) | [LumenPnP v4 - What's New, 0:04](https://youtu.be/FzCwtPgJDBg?t=4) | The same shoot from a little further left |

Other frames I looked at: the top views ([bvGPbwndZMQ 0:46](https://youtu.be/bvGPbwndZMQ?t=46) and
[awn-P1sYTt0 0:29](https://youtu.be/awn-P1sYTt0?t=29)) and the feeder close-ups
([bvGPbwndZMQ 0:58](https://youtu.be/bvGPbwndZMQ?t=58) and [1:31](https://youtu.be/bvGPbwndZMQ?t=91)). For the
motion I used the storyboards of the pick, the bottom-camera check and the placement
(awn-P1sYTt0 1:09–1:17, bvGPbwndZMQ 1:15–1:22). The [v4 video](https://youtu.be/FzCwtPgJDBg?t=21) also gives the
work area: 360 × 270 mm.

## What changed

**Size.** The model is now **707 × 673 × 342 mm** (the nozzle tubes loop to about 364), where it was 680 × 680 ×
450. The real machine is about 25 % lower. Most of the old error was in height: the plates sit 144 mm above the
bench, the Y rails' tops at 219, and the head's top at 342.

**Frame.** It is now built as it really is:
- The plates rest on the lower side rails. The feeder rails run front and back, 20 mm lower still. The Y rails
  run on top of the upper side rails, with their MGN12 steel.
- The legs have their real side profiles, triangular cut-outs and extensions.
- The Y-belt tension arms (yellow) sit on the front of the front legs, a striker post and a yellow thumb screw on
  the front left, and the Y motors in the back legs.

The old model's details were wrong in several places:
- yellow "corner" blocks on top of all four legs;
- the plates over the rails;
- three 120 mm plates;
- a box-shaped head with the camera in front.

**Plates.** Following Opulo's v4.2 CAD:
- the 120 mm staging plate has the up-looking camera off-centre at x 120;
- the up-looking camera's white ring light shows through a 56 mm hole;
- the bottom-vision cover hangs under the plate;
- the discard bin, the calibration fiducial mount and the nozzle rack sit on top;
- two 75 mm build plates sit behind it;
- all are black with a 25 mm hole grid.

The v4.0 promo frames have PCB plates in another layout, so no plate edge is picked in them.

**Head.** It is built from Opulo's parts:
- the front plate and carriage;
- the Z motor as a diamond on top;
- the two NEMA 11s, with rotary unions, nozzle holders and camera masks;
- the red and blue Z back plates;
- the down-looking camera behind the nozzles in its white diffuser;
- the cable splay, and the red and blue tubes.

**Drag chains.** The Y chain runs along the left side, outside the frame. The X chain lies on its support behind the
gantry and loops up to the head at the right. In each chain the bend moves half as far as the carriage, and the
runs stretch to suit: `Joint("follow")` with a linear jacobian (`_stretch`).

**Feeders.** These are Opulo's powered feeders, a separate design that is not in this repository. Ten stand on the
front rail and five on the back, mirrored. Each one is a black body with a top arm reaching in towards the plate,
a front drop with the yellow drive gear and tab, and tape over the pick window. Their top and bottom were fitted
to the v4.0 front frames (`FREE`): `feed_top` went from 52 to 54.9 and `feed_low` from −40 to −37.3. `feed_in` (74)
is not constrained by any view.

**Motion.** These were checked against the videos and DESIGN_DECISIONS.md:
- The travel is the real one. The X extrusion moves y −25…422, between the legs. The head moves x 81…519,
  between its motor and idler mounts. In the CAD's frame, nozzle 1 reaches the front feeders' pick windows
  (y ≈ 65), the back ones (y ≈ 365) and the camera (x 120, y 140).
- **The two nozzles are counterweighted:** when nozzle 1 goes down to pick or place, nozzle 2 goes up the same
  distance. The old model moved one nozzle on its own.
- The sequence now follows OpenPnP's job:
  1. The top camera visits the board's two fiducials.
  2. For each part, nozzle 1 goes to a feeder (front slots 2 and 5, then back slot 3) and drops about 22 mm to the tape.
  3. Over the up-looking camera it drops 9 mm, with the ring light on, and turns the part 90° (the pin-1 dot shows
     it).
  4. It goes down 31 mm onto the board.

## The fit

`python3 register.py solve lumenpnp` keeps every dimension that comes from the CAD fixed and fits only the feeders.
The joint values in each frame were found by a grid search over the camera fit. Each frame has its own camera.

| View | Picks | rms (px) | Focal length (px) | Pose (gantry, head) |
|---|---|---|---|---|
| `v42_front_right` | 13 points, 3 rail points | 6.05 | 1024 | 0.94, 0.46 |
| `v4_front` | 17 points | 7.44 | 904 | 1.00, 0.50 |
| `v4_front_check` (held out) | 12 points | 5.58 | 964 | 1.00, 0.50 |

With the frame points alone (the legs and arms), `v42_front_right` came to 3.1 px before the gantry picks were
added. That is CAD dimensions with no fitting. In `v4_front`, the worst picks are the feeders, at 11–13 px: their
shape is not in the CAD, and that machine has 25 feeders where the model has 10. Next worst are the foot corners,
at 7–12 px: the extension's inner face is hard to tell from its front at that angle.

## Still uncertain

- **The feeders' shape** is a sketch from the videos. The pick window, the tape path and the reels are not modelled
  from drawings. Opulo's feeder repository would settle it.
- **The machine's version.** The model follows v4.2: steel plates, and the camera at x 120. The v4.0 promo frames
  show PCB plates and a centred camera. The frame, gantry and head are the same in both.
- **The pose in each frame** is a grid-search estimate. Gantry and head are good to about ±0.02, but there are few
  head picks.
- **The floor.** The legs' extensions end at z −100 in the CAD. The rubber feet (bom.json: 10 mm, adhesive) are taken as 1 mm.
- **Close-ups.** `fab_tour.py`'s `tour_one` ignores `Instrument.zoom`, unlike `tour.py`. So the close-up of the
  first pick (`inst.zoom = {3: …, 12: "out"}`) does not show yet, and the 9–31 mm nozzle strokes are small in the
  whole-machine view.

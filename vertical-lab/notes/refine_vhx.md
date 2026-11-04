# The Keyence VHX-7000 + EA-300, refined against Keyence's video (#303, PR #318)

The model was a beige box stand with a rectangular head, and a plain blue monitor on a box. Keyence's own
[Versatile User-Friendly Digital Microscope | VHX-7000N Series](https://www.youtube.com/watch?v=C4IBBj20OpE) shows
the real system twice:

- [0:19](https://youtu.be/C4IBBj20OpE?t=19): front view of the monitor-controller and console beside the stand
  (real footage on a table). This stand has the plain head, not the EA-300.
- [1:25](https://youtu.be/C4IBBj20OpE?t=85): the EA-300 configuration from the front right. It is a product shot
  with a reflective floor, probably composited.

I also looked through the contact sheets of [e2CA0tNNYpI](https://www.youtube.com/watch?v=e2CA0tNNYpI) (0:00–0:09 is
the same EA-300 shot) and [mlHiTNpCwjM](https://www.youtube.com/watch?v=mlHiTNpCwjM) (dark, stylised CG, no whole
views). I fetched frames 0:05 and 1:02 of C4IBBj20OpE but didn't pick from them.

## What it showed, and what changed

- **Dark grey and black with silver, not white.** There are three new materials: `char_vhx_dark`, `char_vhx_grey` and
  `char_vhx_silver`.
- **Base:** a pedestal whose silver skirt flares out at the floor. Its centre front is dark between the silver
  flanks, its top is dark, and it has the VHX badge with a blue light and the focus knob on the right.
- **Stage:** a dark stage column carries the motorized XY stage at mid-height, with its 171 × 168 mm top and 100 mm
  disk.
- **Column:** it rises at the back, and a silver arch runs forward from it over the head. The arch now belongs to
  the column, so it stays put while the head tilts under it.
- **EA-300:** a dark box under the arch, with a grey right-side panel. The VH-ZST zoom lens (silver tube, dark grip
  and nose) hangs down its front right, and the EA-300's own objective is under its centre. In the footage the face
  with KEYENCE and the blue light (the front) is the narrow one. So the box is drawn 210 mm across and 280 mm deep,
  against Keyence's "280 W × 210 D". That is an inference, flagged in `VHX_LOOK`.
- **Controller:** a monitor. A black bezel frames the 596.7 × 335.7 mm screen. Under it is a full-width silver "VHX"
  bar with a rounded underside, standing on a narrower silver foot (430 mm). The console sits in front: a silver
  body with dark keys, a jog dial on the left and a joystick on the right.
- **Joints and actions:** the head tilt, the focus sweep, the laser, the plasma and the spectrum panel are unchanged.
  The last caption now gives the height computed from the model: 656 mm with the arch, under Kardex's 727.5 mm.

## The fit

`register.py` (refs/vhx/, fit.json). Each frame's monitor and stand are separate views, because the monitor stands
somewhere different in every shot.

- **Views from the same real frame share a lens.** At 0:19 the monitor and stand share `C4IBBj20OpE@19`.
- **The 1:25 product shot gets two cameras.** Its monitor and stand are probably composited, so each has its own.
- **Scale:** the published 625 × 460 mm controller and 596.7 × 335.7 mm screen, and the 171 mm stage top.

| view | picks | RMS, camera only → fitted | |
|---|---|---|---|
| front_0019_monitor | screen corners, bezel top corners | 3.4 → 3.3 px | fitted |
| front_0019_stand | plate front edge, stage bottom corners, knob, base front bottom | 3.7 → 3.3 px | fitted |
| ea300_0085_monitor | screen and bezel corners | 4.6 → 4.6 px | fitted |
| ea300_0085_stand | base badge, knob, two EA-300 top corners | 33.6 px | holdout (check) |

- **Fitted** (`FREE`): base width 290.7, badge height 73.7, stage 213.4 wide × 53.4 tall, stage top at 225.0 mm (the
  plate's top at 231 mm), screen 12.2 mm below the bezel's top, bezel bottom at 84.9 mm.
- **Not fitted, because no view sees them:** the depths (base 435, stage 200 mm), the column, the arch, and the
  EA-300's height and place. The EA-300's 345–595 mm span is estimated by hand from 1:25, scaled against the stage.
- **The VHX badge on the base is left out of the 0:19 picks.** It sits 10 px right of the stage's centre, which the
  stage's ±20 mm X travel can explain. With it in, the fit turned the camera through about 30° of yaw.

## Still uncertain

- **The 1:25 check fails at the knob, by 66 px.** Seen from there, the knob sits much closer to the badge than a
  base this wide predicts. Either the shot is a composite, or the knob or base is placed wrong. The EA-300's two top
  corners do match (2.4 px and 1.1 px).
- **At 0:19 the model shows more of its left side than the photo does.** The model's base (435 mm) and EA-300 (280
  mm) are deeper than the plain stand seen there, so the base depth is a guess. Keyence publishes no outer size for
  the VHX-S750E.
- **The EA-300's orientation** (narrow face forward), and where the VH-ZST hangs relative to the laser's axis.
- **The console's place** changes from shot to shot. It is drawn in front of the monitor's centre.

# Refining the SEM model against footage of the TM4000Plus / TM4000PlusII (#303)

`sem()` in `instruments.py` is Hitachi's TM4000PlusII tabletop SEM. Its envelope stays Hitachi's published
330 W x 614 D x 547 H mm, which sets the scale. The proportions in between are now fitted with `register.py` to four
frames from two sources: Hitachi's own product shot and the Canadian Centre for Electron Microscopy's (CCEM)
TM4000Plus videos. The Plus and the PlusII share a body; the II is a badge on the front panel.

## Sources

| view (`refs/sem/`) | frame | what it shows |
| --- | --- | --- |
| `hitachi_front_left` | [Hitachi, "The new TM4000II / TM4000PlusII Tabletop Microscope", 0:01](https://youtu.be/cg1S2WZVWr8?t=1) | Product shot from the front left, 960 x 720: the top, the left side and the front |
| `ccem_front_right` | [CCEM, "Loading the specimen", 1:05](https://youtu.be/IqZkvBX-7cU?t=65) | The whole machine from the front right, closed, 640 x 360 |
| `ccem_front_right_2` | [CCEM, "Loading the specimen", 0:23](https://youtu.be/IqZkvBX-7cU?t=23) | The same machine, further round to the right |
| `ccem_front_left` | [CCEM, "Stopping Observation and Unloading the Sample", 0:40](https://youtu.be/jI-MMJVOH94?t=40) | The same machine from the front left, a hand on the door |

These were used for the motion, not registered:

- **The door coming out.** [CCEM "Loading", 0:22-0:27](https://youtu.be/IqZkvBX-7cU?t=22) and
  [CCEM "Unloading", 0:29-0:41](https://youtu.be/jI-MMJVOH94?t=29).
- **The holder in the stage's socket.** It is lifted out at
  [CCEM "Unloading", 0:31](https://youtu.be/jI-MMJVOH94?t=31), and put in at
  [Microscopy Australia, "SEM: Hitachi TM4000Plus Benchtop SEM Workflow", 0:48](https://youtu.be/1_TpZkI3LWo?t=48)
  ("load the sample holder onto microscope stage"). The same video shows the height gauge at 0:24-0:44.

The frames were fetched through the stream-cam Pi with `frames.py`: four storyboards and 13 frames. Frames from these
videos are not committed (`refs/.gitignore`). `register.py` fetches them again from each view's `video` and `t`.

## What changed, and why

**The body.** It was a box under a separate off-white hood that overhung it, with a ridge on top.

- **Top front edge.** The top front edge now rolls over in an 80 mm radius, as it does in every view.
- **Top cover.** Its seam sweeps down each side from the back of the top to the front. It shows on the left side
  in the Hitachi shot and as a curved line on the right side at CCEM 1:05.
- **Wedge.** A wedge sits on the front of the top: 151 wide, 31 mm tall at its face, tapering back into the top. In
  the Hitachi shot its left face is a dark triangle and its front face a light quad. At CCEM 1:05 it is the step at
  the top left.
- **Colours.** The cover is white and the sides a shade greyer, as in the Hitachi shot.
- **Vents and feet.** Two vent grilles are on the left side (Hitachi shot, CCEM 0:40). The feet are small grey
  discs, 12 mm, where they were 25 mm chrome cylinders.

**The front.** The panel was a bright blue (`inst_blue`). It is now `inst_navy`: the real one samples at about
(0.15, 0.20, 0.34) in the lit Hitachi shot.

- **Panel.** It sits 20 mm deep in a white frame 35 mm wide. Along its top is the lit strip between "EVAC" and
  "AIR". Below that are the TM4000Plus name, the II badge, an icon badge and HITACHI.
- **EVAC/AIR button.** At the right, 277 mm up. It was 320 mm up.
- **Fitted heights.** The panel runs from 236 to 417 mm, and the door from 30 to 236 mm.
- **Door.** A navy block 201 mm wide, narrower than the recess, with a dark surround on either side.
- **Handle.** A black bar 149 mm wide on two posts, about 24 mm below the door's top. It was a flat slab 70 mm down.

**The stage and the sample.**

- **Stage.** An X-Y stage now rides on the door's inside face: a carrier, two slides, lead screws and a socket in
  the middle, as in the CCEM close-ups. It was a round stage on a column.
- **Sample.** The sample is the lab's 1.25 in maroon Bakelite mount (`MOUNT_D`, `mount_red`, as on the polisher). It
  sits on a cylindrical holder: a pin, a post and a knurled collar.
- **EBSD port.** It moved in line with the socket, so the 70 degree pre-tilted holder's face looks at it.

**The motion.** The door still slides straight out with the stage on its inside face, which is what the videos show.
Three things changed:

- **Holder.** It now starts off to the right of the machine. Before, it floated in front of the panel.
- **Insertion.** The holder drops straight down into the socket.
- **Tour camera.** It moved round to the front left and up: `inst.cam` is (-1.5, -1.2, 1.2), where it was (-0.9,
  -2.0, 0.85). It now also zooms in for the insertion (`inst.zoom`). From the old angle the open door hid the
  stage: the door is 236 mm tall and stands 93 mm in front of the socket.

## The fit

`python3 register.py solve sem` fits 17 parameters (`FREE["sem"]`) and the four cameras. The two CCEM front-right
views share one focal length. The values written into `SEM` are within 2 mm of the last fit, which is inside the noise of the 360p picks. `refs/sem/fit.json` has the residual of every pick.

| view | size | picks | rms, px |
| --- | --- | --- | --- |
| `hitachi_front_left` | 960 x 720 | 25 | 4.63 (camera alone 4.85) |
| `ccem_front_left` | 640 x 360 | 9 | 5.01 (camera alone 5.15) |
| `ccem_front_right` | 640 x 360 | 17 | 4.02 (camera alone 4.06) |
| `ccem_front_right_2` | 640 x 360 | 8 | 2.11 (camera alone 2.15) |

At 360p a pixel is 2-2.5 mm at the machine. The overlays are in `out/register/sem/`.

## Still uncertain

- **How far the door stands proud, and how deep the panel sits.** The door's side face shows from either side,
  which makes its edges ambiguous. So the door's right corners were dropped from the right-hand views. `proud` is
  constrained by no pick and stays at 6 mm.
- **The wedge's length and the seam's curve.** The wedge's front face is picked, but its length (`hump_len`, 200 mm)
  and how it meets the top at the back are not. The cover seam's curve is drawn from the photos, not fitted.
- **One outlier.** In `ccem_front_right` (1:05) the back corner of the top looks about 29 px higher than the model
  puts it. Two views agree with the model to 1-4 px: the Hitachi shot and CCEM 0:23, which is the same machine. So
  the pick was dropped. The phone may have zoomed between the two moments, though views from one video share a
  focal length here.
- **The II badge.** In the CCEM views it lands 5-9 px from the panel's centre line, and the model keeps it on the
  centre line.
- **Door travel.** It stays at 170 mm, from ac-dev-lab #132's model. CCEM's close-ups suggest closer to 200 mm,
  but that was not measured.
- **The vents.** Their positions are approximate, not picked.
- **The EDS analyser, EBSD detector and pump beside the machine.** None of the videos shows the lab's own
  configuration. They are as before, a proposal.

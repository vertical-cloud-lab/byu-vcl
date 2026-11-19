# The melt-chamber and melt-stream cameras and their displays (PR #353, #303)

Clip `atom_cameras` (`atom_cameras.py`). Models and API: `atom_cams.py`. Bill of materials:
`out/atom/cameras_bom.json`. Camera poses as rendered: `out/atom/cameras_poses.json`.

Sterling asked (PR #318, 19 Nov): "you should add in the camera / screen setups described in DAL along with the
atomizer. The melt chamber and meltstream cameras and displays." That design is digital-alloy-lab PR 189
(`atomizer-viewport-cameras/`, issue byu-vcl #198): three Raspberry Pi 5 units, one per viewing window, each with its
own display beside the operator, streaming as well. Nothing in it has been printed or bench-tested with cameras yet
(DAL README, "Not done yet"). The one bench test is the front unit's 5 in HDMI panel, on 13 Nov (DAL #258).

## What is drawn, and where it comes from

Every unit part is DAL's own geometry: the Onshape Part Studio "rePowder viewport cameras (byu-vcl #198)" as DAL
exported it (`exports/onshape_partstudio.step`, read with its part names the way DAL's `cad/check.py` reads it). That
STEP has the printed parts, the bought parts as DAL drew them (Pi 5 and Active Cooler, HQ Camera with M12 and C lenses,
Camera Module 3 Wide, the three displays, the 2020 extrusion, the post, the magnetic base) and the machine parts round
the windows (port nut and glass, AMAZEMET's LED cover and cable pod, the sight-glass ring, the lid window and plate).
`python3 atom_cams.py --extract` tessellates it once into `out/atom/cams_dal189_parts.npz` (110 kB), so the clip
does not need the DAL clone.

| Unit | Window (this model) | Cameras | Display | Pi wiring (DAL) | Mount (DAL) |
|---|---|---|---|---|---|
| Front | round view port, front face, axis 21.6 deg up, 8.5 deg left (`M.VIEWPORT_N`) | HQ Camera M12 + 16 mm M12 (CIL160), lens 15 mm left of the axis; Camera Module 3 Wide 18.5 mm right | Elecrow 5 in HDMI, 800 x 480, facing out along the axis, ~20 deg up | HQ on CSI0, CM3 Wide on CSI1, display on micro-HDMI (both MIPI ports carry cameras) | 12-sided socket slides 15 mm over AMAZEMET's LED cover, keyed by the cable pod at 6 o'clock, M6 ball plunger |
| Left | door sight glass, y -45, z 1060 (the CadQuery model's, as `repowder/model.py` has it) | Camera Module 3 Wide on the sight glass's axis | Raspberry Pi Touch Display 2, 5 in (DSI) | CM3 Wide on CSI0, display on DSI | split collar on the sight-glass ring, one M4; rides on the door |
| Top | lid window, front facet (DAL's; added here, see below) | HQ Camera C/CS + 16 mm C lens, hot mirror, variable ND, on the line 66.4 deg below level, lens 245 mm from the glass | Waveshare 2.8 in DSI, 480 x 640, tilted 30 deg down at the arm's tip | HQ on CSI0, display on DSI | switchable magnetic base and 5/8 in post on the blue frame's top, printed hub on a detent collar ("working", "parked", 90 deg apart), ~470 mm 2020 arm |

How each unit was put on this model (`atom_cams.py`; the same moves as DAL's `cad/units.py`):
- **Front:** rigid, from the Onshape port (x -15, z 1035 where the axis leaves the face, 20 deg up, not turned) to this
  model's axis, about where each axis leaves the face (a 8.5 deg turn and a 1.6 deg tilt). The model's own 12-sided
  flange and glass are hidden in this clip; DAL's nut, glass, LED cover and pod are drawn in their place, as DAL's
  renders did. DAL drew the nut solid; it is bored here to the glass's 63 mm so the cameras can see in.
- **Left:** moved (-10, -65, +45) mm (units.py: Onshape sight glass y +20, z 1015, ring 30 proud, to the CadQuery
  model's y -45, z 1060, ring 22 proud) and parented to the door. This model's door has no hole behind its sight glass
  (the glass is a disc on the plate), so a 44 mm hole is cut in the door's mesh in this scene only.
- **Top:** not moved. The Onshape arm aims at (0, 0, 1240): the crucible datum (`M.Z_CR` 1219.2) plus ~20 mm of melt,
  DAL's aim, which holds on this model too.

## The lid window: DAL is right, the model's slot is not (and the model's lid is turned 90 deg)

This model has a 26 x 84 mm slot on the lid's LEFT facet (#327, from T4 5:16). DAL measured a 60 x 64 mm glass-ceramic
window in a polished plate with 8 screws on the lid's FRONT facet, ~50 deg from level, centre about (y -94, z 1455)
(`measure/measurements.md` section 3; frames DWH1CEygsTI 25:40, 58wJ_Khwgyk 58:06, of5-LhkX_VQ 24:18). I checked the
frames DAL used:
- **DWH1CEygsTI 25:40** (DAL's annotated frame): the window face on, and behind it, on the right, the GU 500 AMA
  keypad on the blue cabinet, also face on. The cabinet is behind the machine (+y), so the camera looks along +y and
  the window faces -y: the front facet. The knob is to the window's right.
- **2wMgeI-E7zw 10:00** (the whole machine from the front left): the lid stands open on the furnace's left, its inside
  facing right; the latch is seen edge-on on the body's right side.
- **1F9_4ccwhss (T4) 5:05 and 5:16**: these fit a camera on the machine's right looking left (the latch's bolt runs to
  the right, into the cabinet, i.e. back). The narrow "slot" at the top left of 5:16 is the front window seen edge-on.

So DAL's reading (hinge on the left, knob on the right, window on the front facet) fits all four frames. The model's
lid (#327: hinge at the back, knob on the front, window on the left) is the same lid turned 90 deg about the furnace
axis. A second check points the same way: **opened about its back hinge, the model's lid runs into the blue cabinet.**
The hinge axis (y 154) is 11 mm in front of the cabinet's face (y 165): the hinge leaf's top reaches the face at about
5 deg, the lid's shell at about 30 deg, and at the full 105 deg the shell's top is about 185 mm inside the cabinet
(geometry; the audit's movers check on a ghost copy of the lid reported the same, more than 50 mm deep). A left hinge
has room.

What I did, without editing `repowder/model.py`: DAL's plate and pane (STEP parts) go on the model's FRONT facet as a
part of `atom_cams.py` riding the lid (`cams:lid_window`), centred where the camera's line crosses this facet,
(0, -95.6, 1458.9), turned from DAL's 50 deg facet to this model's 53 deg; the lid's mesh in this scene is rebuilt with
the model's own calls (`M._prism`) with that 60 x 64 opening cut and without the left slot; `hood_window` is hidden.
Side effect: the knob, which the model puts at the front facet's foot, sits under the window here; on the machine it
is to the window's right. **For the model's owner:** the lid (and the latch with it) should be turned 90 deg, hinge on
the left (DAL: x about -160, pin along y), or measured first (DAL's guide, sheet 7). Every clip that opens the lid
inherits this.

## What each camera sees (rendered, and in numbers)

Each feed is rendered from the camera's own pose (`unit_poses()`) and lens: HQ + 16 mm, 22.2 x 16.8 deg (IMX477
6.287 x 4.712 mm at f 16); Camera Module 3 Wide, 102 x 67 deg (Raspberry Pi). The renders are 320 x 240 (16:9 ones
320 x 180), every 2nd frame, in a strip under the frame that the clip does not show, then put on each display as a
texture and in the panels. The glass panes are left out of the feeds (the cameras see through them). The front
cameras get a head light (AMAZEMET's LED ring), the left and top a dimmer one; the melt is drawn self-lit.

| Camera | Landing point of the stream (`M.IMPACT`, on the plate) | Nozzle exit | Field (half angles) | What the feed shows |
|---|---|---|---|---|
| Front HQ | 24.4 deg below its axis, 243 mm away | 40.5 deg above | 11.1 x 8.4 deg | the stream in mid-air and the upper sonotrode's end, not the landing point: **DAL found the same on 5 Nov (24 deg, 238 mm)**; it needs the +10 to -30 deg tilt DAL describes |
| Front CM3 Wide | 23.5 deg below, 257 mm | 37.4 deg above | 51 x 33.5 deg | the landing point, the plate, the stream; the port's bore takes a large part of the picture on its outer side (DAL estimated a quarter; it depends on how deep the glass sits) |
| Left CM3 Wide | **48.9 deg below, 15.6 deg aside, 249 mm** | 16.6 deg above | 51 x 33.5 deg, and the 44 mm bore through the door limits it to about 25.5 deg | the nozzle and the top of the stream. **The landing point and the plate are out of its view** |
| Top HQ | (the melt, through the lid window) | | 11.1 x 8.4 deg | the window plate, and through the window the crucible's top, the sealing rod and the melt, ~190 mm across at the melt |

The left camera is a finding: DAL put it there for the side view of nozzle and plate, the view that would have shown
the 6 Oct failure (the melt on the upper sonotrode). On this model's sight glass (from the CadQuery model) the plate is
49 deg under its axis; on DAL's Onshape numbers (z 1015) it would be about 39 deg. Either way it is outside the
camera's 33.5 deg half field and the bore's ~25 deg. If the sight glass measures as either model has it, the left unit
needs a downward tilt with the camera close to the glass, or the side view has to come from elsewhere. Measure the
sight glass first (DAL guide, sheet 5; its y is the number the two models disagree on most).

## The procedure in the clip, step by step

| Step | What happens | Who/what | Source |
|---|---|---|---|
| 1/6 | the three units on the machine | (installed by a person, DAL "Assembly, briefly") | DAL README |
| 2/6 | lines of sight: the top camera's line through the window to the melt (66.4 deg below level); the front pair along the port axis; the left on the sight-glass axis | | DAL README "Design"; placement.json |
| 3/6 | MiR250 1 drives to (100, -620) (model frame, ours: the first spot from which every pose is reachable and no link touches anything); the UR10e closes the 2F-85 on the extrusion 300 mm out from the post (top and bottom faces, closed to 20.6 mm), swings the arm +90 deg about the post until the plunger clicks into "parked", lets go and backs off 60 mm; later grips again and swings it back to "working" | arm 1 | park +90 deg: DAL `viewport_mounts.fs` (`park`, default 90); detent: DAL README "The arm" |
| 3/6 | why it parks: in "working" the arm, pod and display box hang 1.68-1.84 m up over the front of the furnace, where the loading arm's wrist and tong come in (chapter 2's tong is held 185 mm above the cup, `TONG_GRASP`) | | DAL: "Swing the arm clear to load the crucible" |
| 3/6 | MiR250 1 drives to its waiting spot (250, -1250) | MiR 1 | ours |
| 4/6 | the displays, which Pi drives which; the atomizer's own HMI (Weintek cMT2166X) is separate | | DAL README "Displays"; DAL #258 |
| 5/6 | the charge (the model's four 17 x 100 mm slugs, ours) heats and slumps into a pool about 29 mm over the crucible datum; the top feed shows it on the 2.8 in display and in a panel | the machine | chapter 2 (`alloy_atomize`) for the coil glow; DAL for the hot mirror and ND |
| 6/6 | the pour: sealing rod up, the stream onto the plate, the spray; front and left feeds on their displays and in panels | the machine | chapter 2's stream, film and particles |

Why the robot parks the arm rather than the lid needing it: in this model, if the lid could swing 105 deg back (it
cannot, see above), it would pass 130 mm under the arm in its working dimple (at 79 deg, knob to hub); DAL gives
118 mm for its left-hinged lid. So in neither case does the lid itself hit the arm. The arm is parked for the loading
reach, as DAL parks it for loading by hand. I did not open the lid in this clip: in this model that motion goes
through the blue cabinet.

Forces, ours/assumed: the M6 ball plunger's spring is not published for the HARFINGTON pick; JW Winco's GN 615-M6-K
is 11-18 N (DAL shopping list). On a 45 deg dimple at ~20 mm from the post that is ~0.4 N m, ~1.2 N at the 300 mm grip:
nothing for the UR10e. The swinging arm is about 0.6 kg (DAL's printed masses plus the Pi, display, camera and lens;
estimate). The 2F-85 needs only a light grip (its range is 20-235 N, Robotiq). Timing (ours): 4 s per swing, ~25 s
for the whole park-and-return including the approach.

## Checks

- **ARM_AUDIT=1 on the final script: 0 of 1178 frames with an arm, gripper or held-part collision, 0 mover contacts
  (round 11 strict rules).** Getting there: the first version followed the arc with `follow()`, whose chords put the
  hub 0.3 mm into its post for 40 frames; the swing now solves the tool's pose on the exact arc each frame. The nearest
  IK branch put the upper arm through the front unit at every spot tried; the spot search now tries every branch and
  drives the clear one (`joint_to(q1=...)`). MiR 1's first waiting spot overlapped MiR 2 (parked at the right, out of
the views; it has no part here); moved. Chapter 2's
  stream was cutting the vibrating plate by 3 mm; the vibration is not shown and the stream stops 4 mm short.
- **Clearances (FCL, this model):**
  - front unit: 29.9 mm from the upper swing bolt (`clamp0`) closed, 25.6 mm open, but **0.09 mm** when the bolt's
    knob passes over the socket at 60 % of its swing (0.1-0.8 mm from 50 to 60 %, sampled every 2 %): in effect it
    scrapes the socket every time the door is opened. Not shown in the clip (the bolts don't move in it). 20.3 mm from
    the furnace body above.
    The model's `clamp0` already overlaps the model's own LED-cover flange (FCL distance 0); it overlaps DAL's cover
    the same way. DAL's measurements put the bolt ~50 mm left of the cover: the model's bolt (pin at x -90) should move.
  - left unit: 3.1 mm from `clamp0` with the door shut; through the door's swing (clamps open) at least 37 mm, from
    the coil leads at full open; more than 55 mm from the stack (DAL: 61.5 mm).
  - top unit: the magnetic base sits on the frame's top; the lens 229 mm from the lid's knob; parked, 76 mm from the
    cabinet; working, 130 mm from where the lid's swing would pass.
- The feeds were checked by casting each camera's axis: before the bores, the front pair saw DAL's solid nut 10 mm
  away and the left camera the door's plate.

## Not done

- No motion of the lid (model problem above), no tilt for the front HQ or the left camera (DAL's own open item for the
  HQ), no cable runs, no streaming.
- The upper swing bolt's knob scrapes the front socket when it is swung open (0.09 mm at the closest sample), with
  the bolt where the model has it.
- The left unit's view of the plate (above) needs the sight glass measured.
- The charge is the model's four slugs, not a real charge; the melt's look through the hot mirror and ND is drawn,
  not computed.

## Open questions for the lab

1. Which way does the furnace lid hinge, left (DAL) or back (#327)? Every lid motion in this PR depends on it.
2. Where exactly is the door's sight glass, and can a camera behind it see the plate at all?
3. Should the front HQ get DAL's adjustable tilt (+10 to -30 deg) now that both models put the landing point 24 deg
   under the axis?
4. Where is the upper swing bolt relative to the LED cover (DAL: ~50 mm to its left)?

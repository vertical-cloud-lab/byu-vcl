# The Form 4, refined against Formlabs' videos (#303, PR #318)

The Form 4 model (`form4()` in [`fab_resin.py`](../fab_resin.py)) was a grey block with an orange box on top: a
225 mm base, a small blue screen in the middle of its front, a cover over the front two-thirds only, a separate grey
rear housing with the cartridge on it, and a cover hinged on its top rear edge that swung out over the front. Frames of
the real printer from four angles, closed and open, show most of that is wrong. The model is now registered to those
frames the way the polisher was ([`refine_polisher.md`](refine_polisher.md)).

## Sources

| Video | What it shows |
|---|---|
| Formlabs Support, [Step-by-Step Guide For Unboxing Formlabs Form 4](https://www.youtube.com/watch?v=sMc4ezYyhDg) (2:17) | Product shots: front left ([0:03](https://youtu.be/sMc4ezYyhDg?t=3)) and front ([0:08](https://youtu.be/sMc4ezYyhDg?t=8)), the parts on the platform, the screen's home page |
| MLC CAD Systems, [Formlabs Form 4 Setup Guide](https://www.youtube.com/watch?v=NXrAn3QfKYw) (5:08) | The same camera before and after the cover opens: shut ([0:48](https://youtu.be/NXrAn3QfKYw?t=48)), open ([0:53](https://youtu.be/NXrAn3QfKYw?t=53)); the black deck and its blue latch before the tank goes in; the screen's "Slide a clean build platform onto the build platform mount. Close the latch to lock it." ([3:10](https://youtu.be/NXrAn3QfKYw?t=190)); the cartridge going in from above at the back (3:54–4:14) |
| Formlabs Support, [Getting Started with Form 4 & Form 4L](https://www.youtube.com/watch?v=U29JzSdHs9c) (5:03) | A Form 4 shut, front left, from just above, the cartridge's cap a small knob at the back of the top ([4:41](https://youtu.be/U29JzSdHs9c?t=281)). Its 2:16–3:39 and 4:19 frames are a **Form 4L**, whose cartridges go in at the side: not this printer |
| ShortCircuit, [We gotta go FAST! - Formlabs Form 4](https://www.youtube.com/watch?v=Q9CMfm-lkds) (5:18) | The cover open from the front: the Z tower is two aluminium columns either side of the lead screw, nearly as tall as the cover, the cover's side panels hanging high on either side ([1:08](https://youtu.be/Q9CMfm-lkds?t=68)); shut, front on ([0:19](https://youtu.be/Q9CMfm-lkds?t=19)) |

Formlabs' support article [Replacing the Form 4 cover hinges](https://formlabs.com/support/Replacing-the-Form-4-cover-hinges/)
places the hinges "at the rear of the printer under the back panel", says they "slide into the slots on the Z-tower",
and has you "rotate the cover as if you were opening it and slide it away from the back of the printer" to take it off.
The published envelope (398 × 367 × 554 mm, 844 mm tall with the cover open) is Formlabs' tech-spec page, as before.
All frames came through the stream-cam Pi (14 of them, from four storyboards); they are not committed.

## What changed, and the frame that showed it

- **The base** is satin silver, 170 mm to the top of a lighter 18 mm lip that the cover sits on (it was 225 mm and
  grey). "formlabs" is small at its lower left. All four closed views.
- **The touchscreen** sits in a black bezel that takes the whole right half of the base's front, from x = 5 mm to the
  right-hand corner and round it, and from 12 mm off the bench up into the lip. The display is about 148 × 95 mm, with
  its lower edge 37 mm up. It was a 116 × 76 mm screen in the middle of the front. The model now shows the home screen's
  green printer drawing and three rows (0:03, 0:08).
- **The cover** is one orange shell over the whole footprint, with rounded vertical and top edges. It was a box over
  the front 300 mm, with a grey rear housing behind it. Its top fits at **537 mm, not 554**. The published 554 is taken
  to be to the cartridge's cap, a knob just proud of the top at the back (4:41, and the 0:03 top). A full-height cover
  could not reach both the left and the right edges of either product shot: it missed the right by about 20 px.
- **Inside:** a black deck round the LCD with a blue latch at its front left (0:53, before the tank goes in); the
  resin tank's frame is light grey, not dark (0:08, 0:03); the Z tower is two aluminium columns with the black rail
  and lead screw between them, nearly as tall as the cover (0:53, ShortCircuit 1:08); the cartridge stands behind it.
- **The cover's motion.** The old hinge on the top rear edge of a 300 mm cover, at 73°, swung the cover's open side out
  over the front, its side panels hanging almost vertically in front of the printer. The real cover pivots on the
  Z tower's top. Its front rises, its open side turns towards you, and it ends up above the machine: the rear edges of
  its side panels become its lower edges, nearly level and just over the columns (0:53, ShortCircuit 1:08). The hinge
  is fitted to the 0:53 frame: y = 162 mm (21 mm in from the back), z = 496 mm. The angle is then set so that the
  front top edge reaches the published 844 mm: 83°.
- **The platform's motion** stays as it was, and the frames agree. At the end of the print the carrier is at the top,
  and the platform slides off its mount towards you by its handle. A fresh one slides on, and the latch locks it
  (the printer's own screen, 3:10). Only the captions changed.
- **The camera** pulls back (framing 1.32, 0.69). The base and the screen were cut off at the bottom of the frame, and
  the open cover needs the room above.

## The fit

[`register.py`](../register.py) fits the four views below. The published W × D × H sets the scale, with the cover's
top free under it. Eleven proportions are free: the lip's height and thickness, the bezel's left edge and top, the
display's four edges, the cover's top, and the hinge's y and z. The open view is posed with the cover open
(`pose: {"cover": 1}`).

**Each product shot has its own camera.** The two are cuts of a promo with different lenses (fitted 2672 and
1873 px), so they carry `"camera"` labels. Forcing them to share one lens, which `register.py` does by default for
frames of one video, cost 3–6 px on both. The two MLC CAD frames come from one camera on a tripod and do share a lens.

| View | Picks | RMS | Focal length |
|---|---|---|---|
| [Front left, 0:03](https://youtu.be/sMc4ezYyhDg?t=3) | 20 | 2.2 px | 2672 px |
| [Front, 0:08](https://youtu.be/sMc4ezYyhDg?t=8) | 20 | 2.4 px | 1873 px |
| [Shut, from above, 0:48](https://youtu.be/NXrAn3QfKYw?t=48) | 12 | 1.6 px | 1062 px (shared) |
| [Open, 0:53](https://youtu.be/NXrAn3QfKYw?t=53) | 8 | 2.4 px | 1062 px (shared) |
| **Check, held out:** [Getting Started, 4:41](https://youtu.be/U29JzSdHs9c?t=281), another video and camera | 11 | 4.6 px | 1010 px |

The worst residuals are on the cover's top front edge in the front shot (7 px) and in the check (8 px), where the
12 mm rounding of the top edge blurs into the glare. Four picks were dropped:
- the lowest point on the back-left edge in 0:03, where the lip's own rounded corner makes the silhouette (35 px);
- the same low point in 0:48 (14 px);
- the bezel's top-left corner in 0:48, which sits inside the lip in that view;
- a point I had taken for the cover's back top edge in 0:03, which was the top's right-hand edge.

In 0:03 the camera is just above the cover's top; without picks on the back edge the fit had put it below.

| | Before | Fitted |
|---|---|---|
| Base, to the top of the lip | 225 | 170 |
| Cover's top | 554 | 537 (cartridge cap to 554) |
| Screen, W × H; its bottom edge | 116 × 76; 102 | 148 × 95; 37 |
| Cover's hinge (y, z) | (118, 554), on the cover's top rear edge | (162, 496), on the Z tower |
| Cover open: angle, top, depth | 73°, 844, about 460 | 83°, 844, 408 |

**The overlays were drawn with every mesh opaque.** `register.py draw` builds its silhouette from the depth buffer,
and VTK writes no depth under translucent surfaces. The tinted cover, drawn at opacity 0.6, therefore left no outline
at all. The overlays in `out/register/form4/` come from a small driver that wraps `register.draw` with
`add_mesh(opacity=1)`. A fix in `register.py` itself, such as an opaque pass for the mask, would make that driver
unnecessary.

## Still uncertain

- **The cover's top, 537 mm.** It is fitted, not published; the 17 mm up to 554 is put down to the cartridge's cap.
  The frames show the cap as a small dark knob, but none shows its height.
- **The open depth.** The fitted cover opens to 408 mm deep, against Formlabs' 478 mm "minimum access" depth. The
  published figure may include room behind for the cable and the cartridge; nothing in the frames shows the open
  cover reaching that far.
- **The hinge.** Only one open frame constrains it: y = 162 mm moves about 3 mm from one solve to the next, z much
  less. The open angle follows from the published 844 mm, not from a measurement.
- **The joint fit has more than one minimum at the 1–2 px level.** Restarted from its own result, it settled with
  the MLC lens at 1141 px and 2.7 / 4.0 px on that pair, the cover's top 1 mm higher. The committed fit is the better
  one, reached from the values one solve earlier, and `FORM4` holds exactly its parameters.
- **Inside the cover.** The tower's columns (112 and 92 mm wide), the tank (310 × 220 × 46 mm), the carrier and the
  cartridge are read off the frames by eye. They are not fitted, because the orange cover blurs their edges.
- **Not modelled:** the mixer in the tank, the tank's lid, the build platform's latch, the LED light strip, and the
  power and Ethernet sockets at the back.

# XRD: the Rigaku MiniFlex, refined against footage of the machine (#303)

The model is the **6th-generation MiniFlex ("MiniFlex 6G")**, which Rigaku has sold since 2023. A lab buying a MiniFlex
now gets this one. The envelope was already the 6G's, from Rigaku's 6G sheet and brochure: 620 W x 456 D x 722 H mm,
80 kg. The title still said "MiniFlex 600", though, and the look came from the brochure's outline drawing. The model
is now titled "Rigaku MiniFlex (6th generation)". Its front is fitted with `register.py` to frames of Rigaku's own 6G
video. The published W and H stay fixed as the scale.

## Sources

The 6G footage is registered: `refs/xrd/*.json`, with overlays in `out/register/xrd/`.

- Rigaku Corporation, "New 6th generation MiniFlex benchtop X-ray diffractometer from Rigaku" (`8tI9uFKevr0`).
  YouTube only offered 640x360 for this video.
  - [1:02](https://youtu.be/8tI9uFKevr0?t=62): the product shot, square to the front on white (`6g_product_front`).
    It is a studio photo, not the video's camera, so it is given its own lens (`"camera"` in its JSON).
  - [0:20](https://youtu.be/8tI9uFKevr0?t=20): in a lab, from the front right, door shut (`6g_lab_front_right`).
  - [0:28](https://youtu.be/8tI9uFKevr0?t=28): the same lab, door open while a sample is loaded by hand
    (`6g_lab_door_open`).
  - [2:21](https://youtu.be/8tI9uFKevr0?t=141): inside, close up.

The MiniFlex 600 footage was used only for the parts the 6G kept, as noted below. It is not registered.

- AZoNetwork, "Rigaku - Miniflex 600 ... Pittcon 2013" (`uaN16cv-vCk`):
  - [0:33](https://youtu.be/uaN16cv-vCk?t=33): Rigaku's product photo of the 600, from the front left.
  - [0:19](https://youtu.be/uaN16cv-vCk?t=19): the door open at the booth.
  - [2:12](https://youtu.be/uaN16cv-vCk?t=132): the button strip, close up.
- Yale CBIC, "Rigaku MiniFlex 600 Powder Diffractometer" (`uuqsQ7pZCs0`):
  - [1:30](https://youtu.be/uuqsQ7pZCs0?t=90): the right side.
  - [0:50](https://youtu.be/uuqsQ7pZCs0?t=50): the door open.
- FMDL, "XRD (MiniFlex 600) 사용법" (`Zx1N5B6_GEc`):
  - [0:53](https://youtu.be/Zx1N5B6_GEc?t=53): front, door shut; the subtitle says to close the door and press
    DOOR LOCK.
  - [4:36](https://youtu.be/Zx1N5B6_GEc?t=276): the strip from the left.
- AMSEC WWU, "MSCI 410: Lab 1 XRD Demo" ([1:53](https://youtu.be/1FZ_D_RvDlU?t=113)): the door opened by its
  left-hand handle. That machine has the 8-position changer; its generation can't be told from the frames.

Rejected:

- The MiniFlex XpC (`grWcAvM83ls`) is a different housing, with a horizontal goniometer and a robot loader.
- Americanlaboratory's `qXiP6V2QMRE` was not needed.

## What changed, and the evidence

The front is three navy parts, and none of them is the old light-grey control panel or off-white logo band:

- **The "Rigaku" band** is fixed at the top. It stays put when the door opens (0:28).
- **The door** has the vertical handle at its left and "MiniFlex" centred low on it (1:02).
- **The button strip** is the bottom of the navy front, with rounded lower corners. From left to right: the radiation
  label, the yellow DOOR LOCK, a lamp, the HV key, power off (white) and on (green), and the red e-stop.

The body seam runs through the door's bottom edge. The colour is a new `rigaku_navy` material.

Other changes:

- **The top is flat.** There is no raised cover on top: the old model had a 30 mm one, but neither 6G view shows it,
  even the product shot taken from slightly above. Without it, the 722 mm height and the 620 mm width agree with the
  product shot. There the body is 214 px from its bottom edge (on 23 mm feet) to its top edge, and 188 px wide across
  the bulges: 614 mm at that scale. With a 30 mm cover counted in the 722 mm, the same frame gives about 590 mm.
- **The orange X-ray lamp** is at the top of the front, centred over the Rigaku band (1:02, 0:20). It used to be at
  the top right. It now lights while the X-rays are on: a new `glow` piece fades in and out with the scan.
- **The side bulges** stay, but are now fitted: about 30 mm proud, from z = 354 to 555 mm, with rounded ends (1:02).
  The MiniFlex 600 has flat sides (Yale 1:30, Pittcon 0:33). This is where the generations differ.
- **The body** has rounded vertical edges. Its feet are black, at the corners and 60 mm in. It has vent slots low on
  both sides, which the 600 has on both sides (Pittcon 0:33, Yale 1:30) and the 6G at least on the right (0:20).
- **The door's inside is light grey**, and the opening has a light-grey frame (0:28 for the 6G, Pittcon 0:19 for the
  600). The door is now 30 mm thick.
- **Inside**, the tube is a white housing with a green lamp and a warning label on the left (0:28, 2:21; the 600 at
  Pittcon 0:19). The D/teX detector on the 2θ arm is navy, as Rigaku's is (2:21; Pittcon 0:19). The goniometer, its
  height (450 mm, in the middle of the door) and the θ-2θ motion are as before. The inside is not registered.
- **The motion.** The door hinges on its right and opens to 100°. The open frame fixes that angle: in it, the handle
  lands 1.6 px from its picks at 100°, and 15 to 18 px off at 95° or 105°. The sample goes in by hand (0:28). The
  captions now name the DOOR LOCK button and the lamp. The e-stop is a mushroom 28 mm proud, in a yellow collar.

The front's proportions are now parameters: `panel_x`, `panel_top`, `door_top`, `seam_z`, `strip_z0`, the bulges,
the e-stop and the handle. `xrd_anchors` publishes them. `ANCHORS`/`FREE`/`CHECKS["xrd"]` follow `xrd()`.

## The fit

Thirteen parameters are free. `W` = 620, `H` = 722 and `D` = 456 are fixed. The fitted values are written into `XRD`;
they are exactly the `params` of `refs/xrd/fit.json`:

| parameter | start (old model or by eye) | fitted |
|---|---|---|
| body_w | 566 (old) / 576 | 560.2 |
| panel_x (half-width of the navy front) | 199 (old) / 206 | 199.6 |
| panel_top (top of the navy front) | 680 (old logo band) / 709 | 707.6 |
| door_top (bottom of the Rigaku band) | 611 (old) / 624 | 628.2 |
| seam_z (door bottom, body seam) | 297 (old base_top) / 304 | 305.3 |
| strip_z0 (bottom of the strip) | 199 (old) / 206 | 210.4 |
| bulge z | 309-543 (old) | 353.5-554.7 |
| e-stop (x, z) | (160, 245) (old) | (153.0, 254.8) |
| handle (x; z) | (-172; 353-461) (old) | (-179.4; 368.4-467.4) |

The rms is the residual over each view's point picks:

| view | picks | rms (camera only -> joint fit) |
|---|---|---|
| 6g_product_front (1:02) | 22 | 2.07 -> 2.09 px |
| 6g_lab_front_right (0:20) | 11 | 1.22 -> 1.09 px |
| 6g_lab_door_open (0:28) | 11 | 1.19 -> 1.18 px |

At these frames' scale, 1 px is about 3.3 mm in the product shot and 2.8 mm in the lab frames. The worst picks are the
product shot's bottom-left corner (5 px) and its feet (3-4 px). That corner is rounded and in shadow.

## Still uncertain

- **Depth.** No 6G frame shows the back or a whole side, so `body_d` (395) and the 456 mm overall depth are not
  fitted. The same goes for the bulges' front-to-back extent, which is kept from the old model at 92 to 216 mm behind
  the front. The bulges might be lifting handles: they read as a raised panel, but this could not be confirmed.
- **Low resolution.** Only the 640x360 stream was offered for Rigaku's 6G video, so the picks are good to a pixel or
  two.
- **The product shot's lens.** It is a studio photo with an unknown focal length. The prior pulls it towards a wide
  lens, and it fits at about 1.0 x the frame width.
- **The inside is approximate.** The tube housing's size, the detector and the goniometer's depth are read off
  close-ups, not fitted. The sample holder still waits in mid-air off to the left before it is loaded, as before.
- **Shared files.** `README.md` (the instruments table, line 43, and the sources list, lines 81-82) still says
  "Rigaku MiniFlex 600" and "the outline drawings in Rigaku's MiniFlex brochure". `services.py` line 112 labels the
  XRD's power figure "Rigaku MiniFlex 600"; the 6G's tube is also 600 W. These are left for whoever merges.

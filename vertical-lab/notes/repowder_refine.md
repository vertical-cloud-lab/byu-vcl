# Refining the rePowder model against the lab's footage (#303, PR "refine the rePowder model")

Sterling, 2026-11-05: "refining the model based on training and atomizer run videos so that it's a highly faithful
reproduction of the actual system (e.g., hinges, clamps, etc.)". This is the first pass. It concentrates on the
furnace's lid, hinge, draw latch and pneumatic bolt, which T4 shows well, and registers the model to four frames.
Code: [`repowder/model.py`](../repowder/model.py) (`hood_parts`, `joints`, `joint_matrix`),
[`instruments_repowder.py`](../instruments_repowder.py) (the `register.py` instrument),
[`refs/repowder/`](../refs/repowder/) (frames, picks, `fit.json`), [`out/repowder_refine/`](../out/repowder_refine/).

## Sources

All from the lab's training video T4, *Atomizer training video 4 (Sep 29): loading the furnace, cleaning the chamber*,
[`1F9_4ccwhss`](https://youtu.be/1F9_4ccwhss) (10:08), fetched as single 720p frames through the stream-cam Pi
(`frames.py`; storyboards for 0:00-7:50 only, the Pi's frame cache was left to `frames.py` and holds no video).

| Frame | What it shows | Used for |
| --- | --- | --- |
| [1:53](https://youtu.be/1F9_4ccwhss?t=113) | lid open, standing up behind the furnace, inside to the camera; latch lever up, bolt through its edge | hinge side and swing; held-out view |
| [2:28](https://youtu.be/1F9_4ccwhss?t=148) (storyboard) | same, wider | hinge side |
| [3:08](https://youtu.be/1F9_4ccwhss?t=188) (storyboard) | lid open, crucible stack visible, deck outline | housing flat on the right |
| [5:08](https://youtu.be/1F9_4ccwhss?t=308) | lid open, lever, keeper-free, bolt rod from the cabinet | fitted view "open lid" |
| [5:41](https://youtu.be/1F9_4ccwhss?t=341) | lid shut, front: keeper plate with two screws, latch, foot bolt, bolt rod, black ball knob, sloping facets, slot | fitted view "front closed" |
| [6:05](https://youtu.be/1F9_4ccwhss?t=365) | from the chamber's left: lid, hinge block with three pins at the back, door open, viewport ring | fitted view "from left" |
| [5:16-5:31](https://youtu.be/1F9_4ccwhss?t=316) (storyboard) | closing the lid, the latch worked by hand | latch kinematics |

The earlier notes cite 5:08-5:23 (`alloy_atomize.md`); the frames are re-fetched here because
`refs/repowder_lid/` named there is not in the repository.

## What the frames show, and what changed

Measured from the frames (pixel picks against the model, see below):
1. **The lid hinges at the back.** Open (1:53, 5:08) it stands about vertical, leaning back, behind the furnace, and
   the hinge block (three knuckles on a plate) is on the back of the lid in 6:05. The model had a *left* hinge on a
   y axis (a guess carried from #124). Now: axis along x at (0, 154, 1351), positive opening, 105 deg, `joint "lid"`.
2. **The lid is a cast faceted shell, not a hexagon:** a short vertical lower band, then sloping facets up to a narrow
   flat top, round at the front left, square over the housing's flat on the right (it nearly touches the blue
   cabinet). Fitted dimensions: radius 140, top radius 45, extent to x = 190, lower band 53 -> 55, facets 126, wall 5
   (assumed). The slot (viewing window) is on the *left* facet, not the front; the black ball knob is on a stalk at
   the front facet's foot, left of centre; the yellow hot-surface label stays on the front facet (assumed there).
3. **The housing is round at the front left and flat on the side facing the cabinet** (`furnace_ext`); the latch, the
   lever post and the bolt are on that flat.
4. **The draw latch is a tall stainless over-centre latch**: a foot bracket with a nut bolted to the housing low down,
   a channel lever on a pin through the foot, a wire loop on the lever's upper pivot that hooks over a keeper plate
   (two screws, a lip) on the lid. Now separate parts: `latch_foot` (fixed), `latch_lever` + `latch_loop`
   (`joint "latch"`, 95 deg about a horizontal x axis at the foot, positive swings out to -y), `latch_keeper` (rides
   the lid).
5. **The bolt is a ~6 mm rod out of the blue cabinet that passes through a lug on the lever's right edge**, at about
   55 % of the lever's height. `latch_bolt` (`joint "bolt"`, slides +70 mm back into the cabinet), `bolt_housing`.

Part names that existed still do: `hood`, `hood_window`, `hood_hot_label`, `hood_knob`, `hood_hinge`. New: `hood_hinge_leaf`
(lid), `furnace_ext`, `latch_foot`, `latch_lever`, `latch_loop`, `latch_keeper`, `latch_bolt`, `bolt_housing`.
Constants: `HINGE` is now a point on the x-axis hinge; new `LID` (parameter dict), `LID_PARTS`, `LID_OPEN_DEG`,
`LATCH_OPEN_DEG`, `BOLT_TRAVEL`, `joints()`, `joint_matrix(name, 0..1)`, `knob_centre()`, `latch_geom()`.

### What chapter 2 (`alloy_atomize.py`) must change when this merges
It is not touched here (the atomize stream owns it). Needed:
- `hood(sc, deg)` (line ~550): `R((0, 1, 0), -deg, M.HINGE)` becomes `R((-1, 0, 0), deg, M.HINGE)` (or
  `M.joint_matrix("lid", deg / M.LID_OPEN_DEG)`). The lid now opens backwards, so the arm's grasp path of the knob
  (line ~1492, hard-coded `(90 + 131) / 2, -20, 1470`) must use `M.knob_centre()` and rotate it by the same matrix;
  it will have to lift the lid by the knob towards +y/up, not swing it left.
- `latch_meshes`, `LATCH_AZ`, the `keeper` parent (lines ~1000-1061) duplicate the latch now in the model; drop them
  and drive `joint "latch"` (lever, loop) and `joint "bolt"`, with `latch_keeper` riding the lid. The lever now pivots
  at the foot, not at the keeper side.
- `FURNACE_CUT` names are unchanged; `hood` is still the cut group.

## Registration (`python3 register.py solve|draw repowder`)

Camera per view (pinhole, one radial term, lens shared per video), picks on identifiable points (latch foot nut, lever
top, lug, bolt end, keeper top, lid corners, knob ball, hinge block, door-opening corners, viewport ring). Free:
`r1, ext, h1, h2, latch_x, latch_len, cabinet_x` (+-40 % of start). Residuals in pixels of 1280 x 720 frames:

| View | role | RMS before fit of the dimensions | RMS after |
| --- | --- | --- | --- |
| 5:41 front, lid shut | fitted | 29.9 | 20 |
| 5:08 lid open | fitted | 33.7 | 15 |
| 6:05 from the left | fitted | 38.3 | 27 (viewport ring alone 59 px) |
| 1:53 lid open, wide | **held out** | 21.7 | **9.1** |

Overlays (footage with the model's outline) are in `out/register/repowder/`, copied to
[`out/repowder_refine/`](../out/repowder_refine/); `before_after.jpg` there puts the old model (main at `9a5dc71`) and
the refined one on the same footage, both with the cameras fitted to the refined model, which favours the new one a
little. The old model's lid did not have the right outline in any view (wrong hinge side, the hexagon too low).

## Measured vs assumed

Measured (pixel picks, fit): lid plan radius/extent, facet heights, top radius, hinge side, latch foot position and
lever length, the bolt's height and its end at the cabinet. Assumed: lid wall (5 mm), the loop's geometry, the
hinge's barrel diameter (16) and the knuckle block width (150), the opening angles (lid 105 deg is "stands up and
leans back" from two frames, not a stop), 70 mm of bolt travel, the keeper's lip, bolt diameter (6 mm from its look
against the lever, not measured), the O-ring and deck outline on the flat (the existing circular O-ring is kept).
Scale: the model's body radius, deck height and door sizes are fixed from the vendor numbers; every other dimension
here is relative to them, through a focal length the fit also finds (448-645 px, a wide phone lens).

## Still uncertain

- Lid height: 5:41 and 6:05 suggest the lid is taller than the envelope arithmetic allows (the fit stops at the lower
  band's bound, 45 mm); a vertical measurement of the lid and the O&MM's 1600 mm total height would settle it.
- The picks are by eye on a 40 px grid, so a pick is good to about 5-10 px; the 15-27 px fitted RMS is mostly the
  model's missing detail (rounded corners, the sloping facets are planar here, the real front facet is two facets).
- **The chamber door seems to be hinged at the back**, not at the front as the model (and T5 25:00, T7 45:00 per the
  README) say: in 6:05 the open leaf and its two hinges are on the back side, the star knobs on the front. Not
  changed (chapter 2's stack motion depends on it); one frame is not enough.
- **The viewport** is 59 px off in 6:05: the ring there faces the camera (the left), near the front corner, rather than
  straight out of the front face. Not changed.
- Latch motion: modelled as a rigid lever + loop; the real loop pivots on the lever and its hook leaves the keeper
  first.

## Questions for the lab

1. Total height of the furnace body and the lid's height from the seam (a tape measure would settle the lid).
2. Which edge is the chamber door hinged on, and which side are the swing bolts?
3. How far does the pneumatic bolt travel, and does it go through a hole in the lever or past its edge?
4. Is the viewport on the front face or on the front-left corner, and at what angle?
5. Any atomizer run video from the back or the right (we only have the left and front); the run video named
   2brsz-90seg in `alloy_atomize.md` has no usable YouTube id in the repository, so no run frame was used.

Not done in this pass: gas and vacuum fittings, the control panel (the "GU 500 A" panel and keypad are in the model;
T4 5:41 shows its layout, which was not checked against the model), clamps on the chamber flange, the HMI arm.

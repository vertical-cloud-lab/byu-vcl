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

Not done in the first pass: gas and vacuum fittings, the control panel, clamps, the HMI arm (the second pass, below, did the panel, the door clamps and the viewport).


---

# Second pass (round 10): door, clamps, viewport, panel, more footage

More frames, fetched one at a time through the Pi (`frames.py`). Video ids: T1 `wRc8p2_FnJo`, T2 (the lab's 6 Oct run, DAL #189's `FDRTt68Vfvo`),
T4 `1F9_4ccwhss`, T5 `58wJ_Khwgyk`. The atomizer run videos in DAL #159 (`dTyuZmqYxHA`, `bMLbosPXffw`, `bWkP5YcsJTc`, `IGZ0saVgkzw`) show the
melt and SEM screens, not the machine, so no frame from them was usable; the run-day footage that does show the machine is in `FDRTt68Vfvo`
(51:00). Independent dimensions come from DAL PR #189's `atomizer-viewport-cameras/measure/measurements.md` (frame pixel spans, body diameter 270 +-10 %
as the scale, so each figure carries its +-); where it agrees with a frame here that is said.

| Frame | Used for | Role |
| --- | --- | --- |
| [T1 30:13](https://youtu.be/wRc8p2_FnJo?t=1813) | closed lid from the front with the GU 500 AMA panel, latch, bolt, keeper | fitted, 19.0 px RMS (f 1146 px) |
| [T5 27:16](https://youtu.be/58wJ_Khwgyk?t=1636) | door open, two swing bolts, viewport hood, from the front-left | held out, 25.7 px (camera-only, planar picks) |
| [T2 51:00](https://youtu.be/FDRTt68Vfvo?t=3060) | the chamber's front face: hood, upper and lower swing bolts, slots | held out, **11.4 px** |
| [T5 24:46](https://youtu.be/58wJ_Khwgyk?t=1486), [T4 7:49](https://youtu.be/1F9_4ccwhss?t=469) | door open from the left: leaf stands out of the opening's back edge, hinge straps there | qualitative (edge-on, no camera solve) |

Earlier views, refitted with the same free dimensions: T4 5:08 15.3, 5:41 19.9, 6:05 26.2 (fitted); T4 1:53 **9.2** (held out). Fitted values
now r1 41.9, ext 185.5, h1 52.0, h2 125.9, latch_x 73.7, latch_len 156.9, cabinet_x 188.3 (first pass 41.6 / 185 / 50 / 125.8 / 71.4 / 155.1 / 189): the new frame moved
nothing by more than 3 mm.

## What changed

| Part | Was | Now | Source |
| --- | --- | --- | --- |
| Chamber door | hinged at the **front** edge (guess, #261) | hinged at the **back** edge (+y), `joint "door"`, axis z at (-135, 128), 100 deg (assumed) swings the front edge out to -x; parts `door`, `door_glass`, `door_kf_clamp` (the stack rides the door as before) | T5 24:46, 27:16, T4 7:49: leaf stands out of the opening's back edge; DAL #189 lists four frames for the same. Opening angle is "stands out", not a stop. |
| Door clamps | three swing bolts at the back edge, vertical pins | **two** swing bolts with black T knobs on brackets on the **front** face near its left edge, pin along y, `joint "clamp0"`, `"clamp1"`, 180 deg, over the top; closed = rod points left through an ear on the door's front edge (new, 8 x 22 mm, assumed), open = points right along the face towards the hood | T2 51:00 (11.4 px held out), T5 27:16; heights z 1035 and 840 from DAL (mid-hood; 110 mm under the hood); pin x -90 and reach 62 fitted by eye to those frames (+-15 mm, pin 25 px off in both) |
| Third bolt | | **not placed**: a black knob hangs at the door's bottom edge in T5 24:46 and T2 51:00 (pointing down, bracket on the chamber's sloping underside); its bracket is not resolved | |
| Viewport | on the front face at x 5, 180 mm hood | x -15 (centre 100 mm in from the left edge), z 1035, 168 mm across corners, 75 mm opening, glass 63 mm, 12-gon, tilted ~20 deg | DAL #189 (+-25 mm on the position; 168 +-25 across corners). The T4 6:05 "front-left corner" guess was wrong: T2 51:00 and T5 27:16 show it on the front face, flush with the left edge (hood left/right/top picks 4-8 px held out at T2). |
| Door KF clamp | none | ring with a black wing screw on the door's stack housing | T5 24:46, 27:56 (wing nut visible), size assumed |
| GU 500 AMA panel | 5 x 3 square keys | five soft keys under the LCD, then a pad of 2 x 5 round keys | T1 30:13, T4 5:41 |

The panel's label position, the red 22 mm button (red here, not the model's yellow-plated rotary switch at 1100 mm) and the blue bezel recess are as in T1 30:13 but not
re-measured; the frame view fits with the panel LCD centre at 0-15 px.

## Lid height, settled

The first pass said the fit stopped at the lower band's bound. With T1 30:13 added nothing is at a bound (h1 52 of >= 20, h2 126 of >= 40), and
the lid is 178 mm above its seam, inside DAL's 150 +-30 (from T1 35:10 and T4 5:16). The earlier mismatch was the model's rounded body, not the lid.

## Still assumed / open

- door opening angle (100 deg), door ears, the clamps' pin x and reach, the KF clamp's size, the wing screw's position, lid wall (5 mm).
- Third swing bolt at the door's bottom; the door's own hinge straps are two plates here, the real ones are welded L brackets (T5 24:46).
- Gas and vacuum fittings: only the door's KF clamp was added. The T5 frames show a KF-flanged sight-glass stub (T5 28:45, 29:05) and hoses on the left face,
  none measured. The wall-mounted brass gas pipes (T5 27:16 top left) are not in the model.
- The latch lever is a rigid lever + loop (the loop's own pivot is not modelled).
- The clamp held-out camera (T5 27:16) is a near-planar solve (f 1619 px, far from the lens of the other T5 frames): its 25.7 px is a weak check; T2 51:00 (11.4 px) is the real one.
- Frame picks are by eye on an 80 px grid, +-5-10 px.

## What chapter 2 has to change to adopt this model

Read from `alloy_atomize.py` on the main tree (round 9, not touched here). The lid now hinges at the **back** and opens backwards, towards the blue
cabinet, not to the left; its knob moves up and back, not up and left.

| `alloy_atomize.py` | Now | Change |
| --- | --- | --- |
| `hood(sc, deg)` (l. 559) | `R((0, 1, 0), -deg, M.HINGE)`, hinge on the left | `M.joint_matrix("lid", deg / M.LID_OPEN_DEG)` (or `R((-1, 0, 0), deg, M.HINGE)`); `HOOD_OPEN` = 105 = `M.LID_OPEN_DEG` |
| `hinge_w = W(M.HINGE)` (l. 1598), `GRIP_KNOB` (l. 1601), `LID_KNOB_N` (l. 1253, "281 mm from the hinge") | knob grasp hard-coded at the front-right | grasp at `M.knob_centre()` carried by the same matrix; the lever arm to the new hinge (y = +154) is about 280 mm, so `LID_KNOB_N` barely changes, recompute it |
| Latch: `latch_meshes`, `LATCH_AZ`, `add_latch`, `latch(sc, deg)`, `sc.parent[g("keeper")] = g("hood")` (l. 989-1094) | a local copy of the latch (round 6) | drop it; use model parts `latch_foot` (fixed), `latch_lever` + `latch_loop` (`joint "latch"`, 95 deg about +x at the foot, positive swings out to -y), `latch_keeper` (rides `hood`), `latch_bolt` (`joint "bolt"`, +70 mm in x), `bolt_housing` |
| Round 9's two arms (l. 1526-1640) | arm 2 presses the lid's top at `PRESS_AT` while arm 1 pulls the lever; arm 1 then swings the lid to the left, towards MiR 2 | same order, but the lid no longer goes to MiR 2: after the latch, **arm 2 holds the lid by its top, arm 1 works the lever and bolt, then one arm lifts the lid by the knob and swings it back and up to ~105 deg against the cabinet**. The comment at l. 1587 ("meets arm 2's forearm from 95 deg up") and CAM_TWO / CAM_LATCH2 framing need re-checking with `ARM_AUDIT=1`; arm 2 can probably stay at the front while the lid goes backwards. The press point on the lid's top changes with the new top (radius 42 flat, round 9's `PRESS_AT` (-25, -15) is on it) |
| Chamber (not used by ch. 2 today) | `CHAMBER_CUT` lists `door`; the door never moves | `door` hinges at the back now: `M.joint_matrix("door", v)`; children `stack`, `cover` (l. 300) keep following it. Clamps `clamp0`, `clamp1` (`joint`) must be opened before the door, in a story that opens it (swing 180 deg over the top). Add `clamp0`, `clamp1`, `door_kf_clamp` to `CHAMBER_CUT` if they should be cut away with the chamber |

Joint names the model exports through `M.joints()`: `lid`, `latch`, `bolt`, `door`, `clamp0`, `clamp1`; values 0..1 of `deg` or `vec`
(`LID_OPEN_DEG` 105, `LATCH_OPEN_DEG` 95, `BOLT_TRAVEL` 70 mm, `DOOR_OPEN_DEG` 100, `CLAMP_OPEN_DEG` 180). Parts by joint: `lid` -> `M.LID_PARTS`; `latch` -> `latch_lever`, `latch_loop`;
`bolt` -> `latch_bolt`; `door` -> `M.DOOR_PARTS`; `clampK` -> `clampK`. Constants that moved: `DOOR_HINGE` (y now +128), `CLAMP_PTS`/`CLAMP_AXES` (two, on the front face),
`VIEWPORT` (-15, -128, 1035). `M.CLAMP_SWING`, `M.CLAMP_Z` for the door clamps no longer exist (`CLAMP_Z` still names the flange clamp's height).

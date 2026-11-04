# Round 7 foundation: a taller opening, the MiR's storage, a wrist camera, tag cubes

byu-vcl #303, PR #318. Four changes that every scene picks up, from Sterling's review on 2026-11-04.

## 1. A 996 mm opening

Sterling: "Change the VLM to assume that 996 mm or whatever the bay height was for that other used module."

- **The opening is now 996 mm tall** over the 833 mm access table. `vlm.Z_OPEN_TOP = Z_SILL + OPEN_H` = 1829 mm.
  - Source: a used Shuttle XP 500 (2005/2006, 3050 × 864 mm), listed with "Bedienöffnung frontseitig auf 833 mm,
    Höhe 996 mm" ([lagersysteme-paternoster.de, Pos. 89](https://www.lagersysteme-paternoster.de/gebrauchte-lagertechnik/kardex-shuttle-xp500-3050x864-pos-89/)).
- **Product height is about 856.5 mm. This is an estimate.** `vlm.MAX_GOODS_H = POF_GOODS_H + (OPEN_H - POF_OPEN_H)`.
  - Kardex's published figure is 727.5 mm (the POF order sheet). It stays as `vlm.POF_GOODS_H`.
  - The 867 mm header height of the standard opening (`vlm.POF_OPEN_H`) comes from Kardex's renders, not a datasheet.
  - The estimate keeps the header as far above the goods as on the standard unit (115.5 mm).
- `GOODS_CLEAR` stays 20 mm. At the opening the goods top out at 1713.5 mm, 1733.5 mm with the clearance.
- **Code that now follows the new figure:** `tour.FIT`, `maintenance.py`'s label, and everything that already read
  `vlm.MAX_GOODS_H` (`services.py`, `setup_lab.py`, `maintenance.LOST`).
- `kardex_tall.py` compares against Kardex's 727.5 mm and asserts its own `H_996` equals `vlm.MAX_GOODS_H`.

## 2. The MiR's storage: a low block with real pockets

Sterling: "There's no insertion gap for the intermediary storage on the MiR250. They would just fall off. Also, it's
positioned rather high ... Should probably be much lower / flush with the base."

- **No post now.** The storage is a block standing on the cabinet top, beside the arm's mounting plate.
  - Its top is 30 mm over the cabinet top, 10 mm over the mounting plate.
- **The pockets are bored** (`props.pocket_block`, CadQuery):
  - 1 mm radial clearance;
  - a 3 mm, 45° lead-in at the mouth;
  - 26 mm deep. That is 43 % of the 61 mm vial and 41 % of the 63.5 mm charge cup.
- `props.buffer_holder()`: one vial, a 64 × 64 mm block. The seat is 4 mm up from the cabinet top.
- `charge.carrier()`: four cups in a row along y, 85 mm apart. The block is 39 × 294 mm.
  - The row is 30 mm outboard of `BUFFER_LOCAL` (it sits at x = −330 mm in the MiR's frame).
  - At 85 mm, the 2F-85's open fingertips (73.7 mm out) clear the next cup at any finger angle.
- Both keep their returns, `(mesh, seats)`. `animate.BUFFER_LOCAL` is unchanged, (−300, −150).
- **The UR10e reaches every seat on a collision-free IK branch.** Checked with `collide.ik_all` and the collision
  checker, with the MiR, the block, the cups and the wrist camera drawn:
  - the vial, gripped 50 mm up, and 170 mm above it: 4 of 8 IK branches clear;
  - each cup from straight above (`alloy_atomize.py`'s grip, 8 mm under the top) at the chapter's finger angles: 4 of
    8 branches clear. With the fingers fully open it is clear at every finger angle, in 15° steps;
  - each cup set down level (as `alloy_charge.py` does, with the cups before it in place): clear from the outboard
    side, headings 60-150°.
- The fingertips stay about 5 mm above the block, gripping the vial 50 mm up.

**Other MiR-mounted holders, not changed:**
- `alloy_models.mir_fixtures`: the plate carrier on a 120 mm post and the bar holder on a 230 mm post
  (`alloy_workflow.py`);
- `alloy_print.holder_mesh`: the container and jar cups on 140 mm posts;
- `alloy_atomize.py`: the powder container's cradle on a 150 mm post.

## 3. A camera on the gripper

Sterling: "The gripper of the arm should have a camera on it."

- **An Intel RealSense D405**: 42 × 42 × 23 mm, 7-50 cm range, 87° × 58° depth field of view
  ([Intel](https://www.intelrealsense.com/depth-camera-d405/)).
- It sits on a clamp-and-plate bracket round the 2F-85's coupling, on the side away from the fingers' closing axis.
  It looks along the tool axis. A USB-C cable stub runs back past the wrist. The bracket is a layout choice.
- The grasp point is about 120 mm in front of the lens, inside the D405's range.
- **It does not move the TCP.** It is a gripper part, `"camera"`, fixed to the flange (`ur_arm.camera_meshes`,
  `gripper_fk`). So `robot.py` draws it and `collide.py` checks it.
- It never touches wrist 1, 2 or 3 in 2000 random poses, so the cached self-collision pairs still hold.
- **The park pose turns it away from the machines.** With wrist 3 at 0°, the camera stuck out 71 mm past the MiR's
  side and caught the opening's post as the MiR docked. `animate.PARK_DEG` now has wrist 3 at 180°.
- `ur_arm._cached` now keys the vendor meshes on what they are built from, not on the whole file. It no longer deletes
  old pickles, since checkouts share `.cache/`.

## 4. Tag cubes

Sterling: "why are the AprilTags ... only facing up? Wouldn't it make more sense to make this a cube with the
repeating AprilTag pattern on each face or something?"

- `warehouse.tag(size=120, ident)` is now a 120 mm cube on its post.
- The top and all four sides each carry a different tag. So a camera sees one from any side as well as from above.
- Each face is laid out like an AprilTag 36h11: a white ring, a black ring, and 6 × 6 data cells.
- The bits are seeded at random (`warehouse.tag_bits`). They are not real tag IDs.

## Collision audits (`ARM_AUDIT=1`)

| Clip | Before (committed) | After |
|---|---|---|
| `animate.py workflow` | 0 of 1140 frames | 0 of 1140 |
| `warehouse.py`, arms | 0 of 1120 | 0 of 1120 |
| `warehouse.py`, MiR bodies | 0 of 1120 | 0 of 1120 |

Before the park pose changed, `warehouse.py` had 4 of 1120 frames: the camera against the opening's post.

## For the other scenes

- **Storage slots F1 and F2 need moving.** The front column's supports now start at 1949 mm, over the taller opening.
  F1, at 1900 mm, is under them. `vlm.SLOTS` was left alone.
- **Narration still quotes 727.5 mm as the limit** in `fab_trays.py`, `fab_resin.py`, `fab_metal.py`, `line.py`,
  `instruments.py`, `instruments_lab.py` (`HIP`), `instruments_char.py`, `services.py` and `setup_lab.py`'s docstring.
  It is right as Kardex's published figure but not as this model's limit.
- **The wrist camera rides 46-88 mm off the tool axis**, 120-143 mm behind the grasp point. In a level grip from
  `props.tcp_frame(..., spin=0)` it is on top. In `warehouse.upright()` grips it is underneath.
- `alloy_charge.py`'s closing shot now frames the middle of the carrier's row.

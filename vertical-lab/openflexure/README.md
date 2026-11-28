# OpenFlexure microscopes in reflection, from OpenFlexure's own OpenSCAD

How the OpenFlexure Microscope v7 and the OpenFlexure Delta Stage in [`../openflexure.py`](../openflexure.py) were
made. Both are set up for reflection (epi-) illumination: a beamsplitter optics module, the filter cube and the
reflection illuminator, with the LED beside the optics module under the stage.

| | Source | Licence |
|---|---|---|
| Microscope v7 | [openflexure-microscope](https://gitlab.com/openflexure/openflexure-microscope), tag `v7.0.0-beta5`, commit `4828ffa5c4a1`. There is no final v7.0.0 tag yet | CERN-OHL-S-2.0 |
| Delta Stage | [openflexure-delta-stage](https://gitlab.com/openflexure/openflexure-delta-stage), tag `v1.2.3`, commit `d882d18b2c12`; its microscope submodule is pinned at `f57655b65f28` (v6.1.5 era) | CERN-OHL-1.2 |

The meshes, about 60 MB of STL, are not committed, the same as the other vendor CAD in this folder. They go in
`../.cache/openflexure/{v7,delta}/`. [`manifest.json`](manifest.json) lists every part with:
- its source module and commit;
- its triangle count and bounding box;
- a colour from OpenFlexure's `render_settings.scad`;
- which stage axes it moves with;
- for the delta stage, the 4×4 transform that places it.

## Pipeline

1. **Clone** both repositories at the tags above.
2. **Use OpenSCAD's nightly build** (2026.11.01 here) with `--backend=manifold`. Every part then renders in about a
   second. Ubuntu's apt package is 2021.01 and CGAL-only, which is far too slow for the main bodies.
3. **Prepare the v7 working copy.** Fix a stray comma at `mount_illumination.scad:68`, which the newer parser rejects.
   Unzip `rendering/librender/hardware.zip` in place: the actuators, motors, clips and hardware import its screws and
   nuts, and export without them, with only a warning, if it is missing. Export the main body once, in place:
   `openscad --backend=manifold -o rendered_main_body.stl rendered_main_body.scad` in `rendering/librender/`, because
   `render_body()` imports that STL.
4. **Copy the wrappers in.** Each `use`/`include` is relative to where the wrapper sits:

   | Wrapper | Goes in |
   |---|---|
   | `assemble_v7_reflection.scad`, `delta_helpers.scad` | the v7 repo's `rendering/` |
   | `delta_stage_parts.scad`, `feet_assembled.scad` | the delta repo's `openscad/` |
   | `illum_parts.scad`, `clip_part.scad` | the delta's `openflexure-microscope/openscad/` |

5. **Export one part per call**, with `run_part.sh` / `run_native.sh` and the part lists in `v7_partlist.txt`,
   `delta_jobs.txt` and `helper_jobs.txt`. They record the exact `-D` options, for example
   `-D transmission_illumination=true -D reflection_illumination=true -D stage_connectors=true` for the delta stage,
   as its `build.sh` sets them. The paths are as they were on the runner (`/tmp/openflexure/...`).
6. **Run `assemble_outputs.py`.** It applies the delta stage's transforms, writes the per-part STLs and the manifest,
   and decimates any part above 300k triangles (none was). `../openflexure.py` decimates further, to 25k triangles
   per part, for the animations.

## What was placed by hand

Neither repository renders the reflection set-up assembled, so these come from the .scad sources:

- **Filter cube:** `translate([0, 8, fl_cube_bottom]) rotate_x(90)`, with `fl_cube_bottom` = -9.4 mm for v7 and -9.5
  mm for the delta.
- **Illuminator holder:** flipped with `rotate_x(180)`. That is the only way its screw holes, beam height and the
  main body's cut-out all line up.
- **LED and condenser:** along the slip plate's slot. The slot allows -45 to -23 mm; the position used is a choice.
- **v7 stage:** the stage is part of the one-piece main body, so `xy_stage` is the body intersected with the stage's
  outline above z = 60 mm (grown 0.1 mm, to take the edge of the top flexure ring). The four legs that carry it are
  cut out the same way, each with a region around it in its `leg_frame()`: `leg_x` and `leg_y` are the two
  `actuator_leg()`s, leg and lever arm together, and `leg_back_left` and `leg_back_right` are the plain `leg()`s. Each
  region takes the strip of the top flexure ring between the leg and the stage, and leaves the bottom flexures with the
  body. `actuator_column_x` and `actuator_column_y` are the columns, cut at the flexure that joins each to its arm and
  kept inside the housing's void. `main_body` is the rest. `reference/main_body_one_piece.stl` is the body as printed.
- **Delta stage:** the repository has no assembly scripts. `legs()` is exported a part at a time: `leg0`-`leg2`,
  `lever0`-`lever2` (each lever with the `lever_flexures` that hinge it to the casing) and `column0`-`column2`, with
  `i` at `rotate(120 * i)` as in `each_lever()`. (`PART="legs_and_levers"` still gives all of `legs()` in one.)
  - The body sits 79 mm up on the electronics base, rotated 120°, so the illuminator exits through the base's window.
  - The optics are rotated a further 60°, to match the objective mount.
  - The objective, tube lens, camera, motors and gears are v7's models at the delta's heights.
  - The Pi and Sangaboard sit at the base's `raspi_center`.

## How the legs and levers move

`../openflexure.py` moves each leg, lever and column as a linkage driven by the stage's displacement `d`, to first
order (`Joint("follow")` in `../instruments.py`), from the .scad parameters. Its `mechanism()` checks that every
flexure stays within the design's `flex_a` and that each leg's top flexure lands where the stage does.

- **v7** (`microscope_parameters.scad`): the bottom flexures are at z = `lower_xy_flex_z` + 0.5 + `flex_t`/2 = 0.875
  and the top ones 60 mm higher (`upper_xy_flex_z` = `leg_height` - `leg_block_t` = 65 - 5), both at radius `leg_r` -
  `flex_l`/2 = 29.25. Each leg leans on its bottom flexure by (`d` . radial)/60 and shears as a parallelogram by
  (`d` . tangent)/60. The X and Y legs turn with their arms, so each column drops by (`actuating_nut_r` +
  `flex_l`/2)/60 = 35.0/60 of the stage's travel along its leg. The tour's (6, 4) mm leans the X leg by 0.118 rad
  (`flex_a` = 0.15) and drops its column 4.1 mm (travel 5.1 mm).
- **Delta Stage** (`parameters.scad`): each lever pivots on its `lever_flexures` at radius `stage_r` + `zflex[1]`/2 =
  25.75 and z = `dz` + `zflex[2]`/2 = 0.875; its leg stands on it at `lever_l` = 35 and meets the stage at z =
  `flex_z2` + 0.875 = 70.875, back at radius 25.75, so the leg leans in 35 mm over 70. The lever turns by
  (`d`<sub>z</sub> - `d`<sub>radial</sub>/2)/35, which keeps the leg's length; its column rises by `nut_y` -
  `zflex[1]`/2 = 46.25 mm per radian. The leg turns about its foot by -`d`<sub>radial</sub>/70 and shears by
  `d`<sub>tangent</sub>/70. With `flex_a` = 0.1 that leaves little focus travel at the corners of an x/y scan, so the
  tour moves the stage (5, -4, 1.2) mm and the array rasters +-4 x +-3 mm with up to 1 mm of focus.

Not moved: the brass nut in each actuator column and the band on its hooks are part of the actuator assembly, which
stays put, so at full travel the v7 X column overlaps its nut by up to 0.8 mm, inside the closed housing.

Left out: transmission illumination, wiring, clip screws and petri-dish holders. The LED and the slide are
placeholders; the animations replace the slide with a slide carrying a polished coupon.

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
3. **Fix one line in the v7 working copy:** a stray comma at `mount_illumination.scad:68`, which the newer parser rejects.
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
  outline above z = 60 mm, and `main_body` is the rest. `reference/main_body_one_piece.stl` is the body as printed.
- **Delta stage:** the repository has no assembly scripts.
  - The body sits 79 mm up on the electronics base, rotated 120°, so the illuminator exits through the base's window.
  - The optics are rotated a further 60°, to match the objective mount.
  - The objective, tube lens, camera, motors and gears are v7's models at the delta's heights.
  - The Pi and Sangaboard sit at the base's `raspi_center`.

Left out: transmission illumination, wiring, clip screws and petri-dish holders. The LED and the slide are
placeholders; the animations replace the slide with a slide carrying a polished coupon.

# Issue #354: previews of the plate sent to the H2D on 2026-11-19

All images are generated from the exact 3MF that was sent
(`bambu/evidence/2026-11-19/issue-354-cubxl-studio/sent/…3mf` on branch
`claude/issue-354-20261119-1837`), or from the STLs in
`modules/electromagnetic-capper/v2/stl/` on that branch.

- `studio_*_preview.png`: Bambu Studio's own thumbnails embedded in the 3MF
  (green is Studio's default filament colour; the AMS mapped it to black PLA at Send).
- `gcode_*.png`: the plate's G-code (`Metadata/plate_1.gcode`) parsed and drawn,
  so they show what the printer actually runs. `scripts/gcode_render.py` parses,
  `scripts/plot_gcode.py` plots.
- `cad_*.png`: shaded renders of the source STLs in their as-used orientation
  (`scripts/stl_render.py`).

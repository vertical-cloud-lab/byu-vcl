# figures/: one script per figure

- `figN_slug.py` makes figure N (`figS1_slug.py` for the SI). Lower-case slug,
  words joined by underscores: `fig3_tensile_strength.py`.
- It reads only from `data/`, through `vs.read_csv("file.csv")` (or
  `vs.data_path("file.json")` for other formats), and writes only to
  `figures/out/`, through `vs.save(fig)` and `vs.caption(...)`.
- It draws at the printed size: `vs.figure("single")` is 85 mm wide,
  `vs.figure("double")` 175 mm. `vs.save` refuses titles, text under 7 pt,
  lines under 0.6 pt and any other width.
- `vs.caption(what=..., n=..., error_bars=..., data=...)` writes the caption
  stub `figures/out/figN_slug.caption.tex`, used in the manuscript as
  `\figcaption{figN_slug}`. Compute `n` from the data frame, never type it;
  say what the error bars are ("mean ± one standard deviation of three
  specimens"), or why there are none ("none: each point is a single dose").
- Any randomness (jitter, bootstrap) uses a fixed seed, so the figure rebuilds
  byte for byte and `make rebuild-check` can tell a real change from noise.

`make figures` runs every script, with `VCL_STRICT_DATA=1` so a script that
opens a data file outside `data/` fails. The two examples here,
[`fig1_time_vs_error.py`](fig1_time_vs_error.py) and
[`fig2_group_spread.py`](fig2_group_spread.py), plot the powder-doser salt
campaign: delete them, their outputs and `data/salt_doses.*` when you start a
paper.

# Colour-blind check

Some readers, mostly men, have a colour-vision deficiency,
mostly red-green. The `paper` preset uses the Okabe-Ito palette, which was
designed for this, but a palette alone does not make a figure readable.
Two series in orange and vermillion, or meaning carried by colour alone,
still fail.

Run it at **G2 (results freeze)** for every figure, and again before **G4**
if any figure changed.

```bash
make figures
make colorblind      # sheets in figures/out/cvd/, and LOOK lines in the output
```

Each sheet shows the figure as drawn, then simulated for deuteranopia,
protanopia and tritanopia (Machado, Oliveira and Fernandes 2009, severity 1),
then in greyscale. The script also names any two series colours that are
distinct as drawn but nearly the same (CIELAB difference under 10) under a
simulation.

## For each figure

- [ ] In every simulated panel, each series can be told from every other,
      and matched to its label without reading colour names.
- [ ] Every LOOK line is resolved: the pair now differs by a second cue (marker
      shape, filled against open, line style, a direct label), or the series
      were merged.
- [ ] No meaning rests on red against green (good/bad, pass/fail, up/down).
- [ ] Continuous colour scales are perceptually uniform (`viridis`, `cividis`;
      diverging: `RdBu`, `PuOr`, centred on a meaningful zero), never `jet`
      or `rainbow`, and the colour bar has a label in "Quantity (unit)" form.
- [ ] Text on a coloured background is readable in greyscale.
- [ ] Photographs or micrographs with false colour state the mapping in the
      caption.
- [ ] If the journal prints in black and white, or a reader might, the
      greyscale panel works on its own.

## Record

In the tracker's G2 or G4 update: `make colorblind` output's last line, the
commit it ran on, and which LOOK lines were fixed and how.

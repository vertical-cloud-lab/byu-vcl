# Figure list

These are candidates for the atomizer part of the article. A collection article will
probably take two or three of them into the main text, and the rest go to the SI. Each
entry lists the runs and measurements it needs, and anything it waits on (see the
[can't-wait table](README.md#cant-wait-no-me-orders-this-year)).

## Main-text candidates

### 1. From custom charge to LPBF powder

- **a.** The cup, plug and powder charge: a cutaway render from the `atomizer-charge/` CAD in PR #232.
- **b.** The machine in section, with the stack, the plate and the landing point: the
  `atomizer-training/viz3d/` model from PR #255, with the stack as rebuilt there.
- **c.** A good pour, as a viewport frame from a valid Block A run.
- **d.** SEM of the 15–45 µm powder at low magnification.
- **e.** The PSD with the LPBF window shaded.

**Needs:** a and b exist. c needs a valid Block A run filmed through the viewport. d
needs SEM, and e needs the sieves and SEM sizing.

### 2. Repeatability at fixed settings

- **a.** Cumulative PSDs of every valid Block A run, both halves of each, with the
  commercial AlSi10Mg reference dashed.
- **b.** D10, D50 and D90 for each run, plotted against run order, with plate changes
  marked.
- **c.** Mass balance per run, as stacked bars: in range, out of range, splats, puddle,
  skull, unaccounted. Invalid runs are drawn hatched.
- **d.** Circularity distribution for each run.
- **e.** CV of each metric against its bar, next to the published spreads: Hinrichs 2021
  (d90 11 %, O 6 %), Yankin 2025 (D50 ±2 %, D10 ±7 %), and NIST gas atomization (D50 CV
  0.6–4 % within a heat).

**Needs:** A1–A5 (up to A8), the sieves, SEM, powder O (2027) for the O entry in e. This
is the figure that makes claim C2.

### 3. Composition set by the charge

- **a.** Measured Si (EDS mean over ≥ 30 particles, and ICP-OES where available) against
  charge Si. Show the 1:1 line, and the spec-limit range of each charge as a horizontal
  bar.
- **b.** Per-particle Si distributions at the top, middle and bottom of the jar for each
  spread point (violin or strip plot).
- **c.** EDS map of a polished particle cross-section at the 30 wt% point, to show
  homogeneity within a particle.
- **d.** Mg recovery (ICP-OES Mg ÷ charge Mg) against Si.

**Needs:** Block B, Block A as the 0 wt% point, and u23y78 as a pilot point (marked as a
pilot). d waits for ICP-OES in 2027. Makes claim C3.

### 4. Powder quality across the spread

D50, in-range yield, circularity and doser V_g against Si, with Block A's ±1σ as a band
at 0 wt%. Does Si change how the plate atomizes?

**Needs:** Block B, plus the doser and sieves. Could be the SI if Si changes nothing.

### 5. The print

- **a.** The MIDI build, or the 55 mm build-reduction coupons.
- **b.** Relative density against commercial AlSi10Mg printed on the same machine.
- **c.** Microstructure in cross-section (optical and SEM).
- **d.** Hardness, or tensile results if there's enough powder.

**Needs:** Block C and Utah time (2027). Makes claim C4.

## SI candidates

| # | Figure | Needs |
| --- | --- | --- |
| S1 | **Where the melt met the plate.** Oct 2 (shot past), Oct 6 (upper sonotrode), Oct 8 (frozen lump at the tip), against a valid run. Video stills next to the viz3d landing-point render. This is the reason for the gate. | Exists: the PR #268 frames and the PR #255 renders. Needs one valid run for comparison. |
| S2 | Process logs for each run: O₂ through the washes, temperature, pour pressure, pour start and end | HMI camera or export |
| S3 | Mass balance for every run, valid or not, with closure | Scale only |
| S4 | Variance components: split-to-split against run-to-run, for each metric | Two halves per run |
| S5 | Cross-sections: internal porosity per block, and Mo or W picked up from the plate and sonotrode | Polishing, EDS |
| S6 | Plate wear: photos before and after, metrics against how many runs the plate had done | Plate log |
| S7 | Flowability: V_g, I_stop and Hausner ratio against commercial AlSi10Mg | Doser, sieves |
| S8 | Powder O against chamber O₂ at the pour, and against storage time | Inert-gas fusion (2027) |

## Tables

| # | Table |
| --- | --- |
| T1 | Fixed settings and their tolerances (from the README) |
| T2 | Repeatability: mean, SD, CV and the 95 % CI on σ for each metric, against the bar and the literature |
| T3 | The spread: charge composition (weighed masses and spec range) against measured EDS and ICP-OES |

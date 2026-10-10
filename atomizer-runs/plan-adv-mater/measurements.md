# What to measure every run

Each run gets a filled-in [`run-record-template.yaml`](run-record-template.yaml), kept in
its run folder (`byu-vcl/atomizer-runs/<date>/`). The bag ID is the run's ID: the
six-character label from [#249](https://github.com/vertical-cloud-lab/byu-vcl/issues/249).
"Every run" here includes runs that fail the gate. Their mass balance and process record
are what the completion rate is built from.

## During the run

| What | When | How |
| --- | --- | --- |
| Settings (the [fixed settings](README.md#fixed-settings-for-blocks-ac)) | Before heating, and when the sealing rod goes up | Read off the HMI and say them out loud on the video. Use the HMI's "amplitude real", not the knob. |
| Landing point | Before heating, with the door open | Laser down the nozzle, or check by eye. Photo with a ruler in frame. Record the distance from the plate's tip and the mark on the stack's slide. |
| Chamber O₂ | After each wash (with its temperature), when the sealing rod goes up, at the end of the pour | HMI. Record the number of washes too. |
| Temperatures, pressures | Melt setpoint and reading, hold time, chamber, pour and turbo pressures | HMI. Count the turbo pulses and note when each one was. |
| Pour start and end | Sealing rod up, stream stops | HMI clock or video time |
| Video | From before the sealing rod goes up until the stream stops | Phone clamped at the front port, plus the panel. Upload unlisted to the Atomizer Runs playlist. |
| POWER reading | During the pour | Film it. That shows whether 0 W means anything (open since Oct 8). |
| Room humidity and temperature | Before the run | Hygrometer, if the lab has one |

## Mass balance (yield)

Weigh each part separately to 0.01 g, in a tared, grounded container. Bag the non-powder
parts too, as the SOP's *"collect, bag, and mark metal splashes"* step says.

1. Charge in, by part: rods, each cup, plugs and powder.
2. Powder in the collection jar.
3. Powder swept from the cone and collection port.
4. Splats and lumps on the plate, the upper sonotrode and the connector. Take them off
   without reshaping the parts.
5. The puddle in the cup or bowl.
6. The skull left in the crucible, and any nozzle globs.

From these:

- **Powder yield** = (2 + 3) ÷ 1
- **In-range yield** = the in-range sieve fraction scaled to all of (2 + 3), ÷ 1
- **Atomized fraction** = (2 + 3) ÷ (1 − 6). This separates how well the plate atomized
  from how much metal reached it.
- **Closure** = (2 + 3 + 4 + 5 + 6) ÷ 1. It should be ≥ 95 %. The rest is lost to filters
  and walls.

## Splitting and keeping samples back

1. Combine (2) and (3). Split them into halves A and B by cone and quarter on a grounded
   tray (a riffler can wait until 2027).
2. **Keep 5 g back** from half A before sieving. Seal it in a labelled vial under argon
   (glovebox) or with desiccant, and log the date it was sealed. It goes for powder O and
   ICP-OES in 2027. Fine Al picks up oxygen in air, so record how many days each sample
   was stored before it was measured.
3. Sieve each half separately. Every measurement below is made on both halves, so that
   measurement noise can be separated from run-to-run noise.

## PSD

- **Sieves:** No. 60 (250 µm), No. 230 (63 µm), No. 325 (45 µm) and the pan. Sieve by hand,
  10–20 g at a time, because the bed depth is the limit on a 3 in sieve. Ground the stack
  and the operator, and wear a P100 or better (sieve doc, PR #262). Weigh each fraction to
  0.01 g.
- **SEM sizing:** before sieving, quarter each half down to about 0.5 g and size ≥ 1000
  particles from it, using equivalent circle diameter, weighted by volume. This gives D10,
  D50 and D90, and the fraction under 15 µm. Dry sieving is unreliable below about 45 µm,
  so the 15 µm end of the window has to come from SEM. Check D50 against the cumulative
  sieve masses.
- If a laser-diffraction instrument can be used without an ME Order, run one half on it
  as a cross-check.

## Oxygen

- Chamber O₂ is recorded every run (above). It's the run's process oxygen.
- Powder O is measured by inert-gas fusion on the retained samples, for every Block A
  run, the Block B endpoints and the commercial AlSi10Mg reference. Send them as one
  batch in 2027, so that they share a calibration.

## Morphology

- **SEM SE images** at 100×, 500× and 2000× on the fraction that passes the 45 µm
  sieve. Keep the magnifications, voltage and working distance the same every run.
- **Shape** on the same images: circularity (4πA/P²) and aspect ratio on ≥ 400 particles
  per half, and the share of particles with satellites, ligaments or splat shapes.
- **Cross-sections** for one run per block and per spread point: mount, polish with the
  [polishing SOP (PR #258)](https://github.com/vertical-cloud-lab/byu-vcl/pull/258), then
  measure internal porosity (area %) and take EDS maps.

## Composition

- **EDS** at 5 kV: 30 or more particles from each of the top, middle and bottom of the
  jar, at least 3×10⁴ counts per spectrum, with the beam within ±0.3 R of each particle's
  apex ([caliber#13](https://github.com/vertical-cloud-lab/caliber/pull/13#issuecomment-6032146879)).
  Report Si for every run. Flag any Mo, W, Ni or Fe, which would be pick-up from the plate
  or the W–Ni–Fe upper sonotrode.
- **ICP-OES** in 2027, on the retained samples: every Block B run, two Block A runs, a
  slice from each 6063 lot and the 4047 powder lot. It gives bulk Si, Mg (and so Mg
  recovery) and Fe. EDS can't resolve Mg below 1 wt%.

## Flowability

- **Doser:** V_g and I_stop, following
  [powder-doser `docs/flowability/`](https://github.com/vertical-cloud-lab/powder-doser/blob/0030e0d/docs/flowability/README.md),
  on the sieved, dried 15–45 µm fraction. Run the commercial AlSi10Mg reference in the
  same session.
- **Hausner ratio:** tapped density ÷ bulk density, in a graduated cylinder.

## The plate

Record the plate's ID, how many runs it has done, before and after photos, and any
cracks or dark spots at the edge. Retire it when the metal no longer lifts off. Over
Block A this gives plate age as a covariate.

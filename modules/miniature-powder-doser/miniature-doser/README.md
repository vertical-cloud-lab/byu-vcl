# Miniature powder doser: the lab's doser folded into an 80 × 85 × 61 mm module

This is the smallest version of the lab's powder doser drawn so far. It is built from
[powder-doser PR 176](https://github.com/vertical-cloud-lab/powder-doser/pull/176)'s own parts (branch
`claude/issue-172-20261003-2216`, commit `509a0bf`, `cad/text-to-cad/STEP/assembly_servos_above.step`), folded up, with
a screw-on capillary on the auger's outlet. It was first drawn to fit beside the melt stream inside the rePowder's
chamber (2026-10-06 and 07), where the doser as built (190 × 261 × 103 mm) has no room. The same module is a candidate
for the smaller powder-dosing module mentioned for the CubXL (byu-vcl issues 213 and 150): one powder, dispensed in
varying amounts to a precise spot, with powder changes done by hand.

This note is the self-contained version of the design. **Everything here is a concept from CAD and estimates. Nothing
has been built or tested.**

![](module_views.png)

![](module_turntable.gif)

## What changed from the doser as built

[`doser_cad.py`](../ods-lpbf-gifs/doser_cad.py)'s `compact_meshes(nose=True)` builds the module from PR 176's STEP. Every kept part is
PR 176's own part, moved along the auger axis. The only new parts are a cradle, the capillary and a vibration motor.

- **Kept:**
  - the auger tube (25 mm OD, 21 mm bore, PR 176's internal flight and v4 outlet), its moulded 44T gear and its screw
    cap;
  - the NEMA 11 with its 20T pinion and its upright;
  - both split-clamp brackets and their screws.
- **Cut:** the tube goes from 250 mm to 85 mm, outlet face to cap end (`COMPACT_TUBE` keeps four pieces of it). The
  gear's front face sits 20 mm from the outlet, and the stepper stays behind the gear, now reaching back beside the
  cap. As drawn, the flight keeps the 25 mm between the outlet face and the gear's centre, about 2.4 of PR 176's 8
  turns, and the open store keeps 58 mm of the 21 mm bore, about 20 cm³ (about 12 g of 1.2 g/cm³ granules half
  full). A real build could run the flight further back into the store.
- **Dropped:**
  - the two MG996R tilt servos, the baseplate and the hinged mounting plate: the tilt is fixed;
  - the tap collar and its solenoid: the vibration motor takes over. The solenoid can come back on the side if the
    bench shows the tap is still needed.
- **Added:**
  - a machined cradle under the brackets and the stepper's upright;
  - the capillary on the outlet (below);
  - a vibration motor on the front bracket's foot.
- **Size:** 80 × 85 × 61 mm for the body in its own frame, 123 mm long with the collar and capillary (as built, with
  its PCB holder: 215 × 273 × 129 mm).
- **Tilt:** fixed at 35°. PR 176's DEM gives the full dose per turn anywhere from 22.5° to 45° of tilt.
- `compact_meshes(mirror=True)` builds the mirror image, with the stepper on the other side of the tube.

## The outlet: no funnel, no spout, no taper

Earlier versions added a separate funnel and spout, then a tapered nose. Both were dropped (Sterling's notes,
2026-10-07): powder can sit in an intermediate tube with nothing to move it, and a taper is where it is likely to clog.
What is left keeps PR 176's tested inside and follows the storage augers' rule, keep the bore and drop the flight:

| Along the axis | Inside | What it does |
| --- | --- | --- |
| Behind the outlet face | 21 mm bore, PR 176's flight (10.4 mm pitch, 0.5 mm thick, on an 8 mm core) | As tested: one pulse per turn |
| The last 12 mm behind the face | PR 176's v4 outlet: a short funnel to a 3 mm annular exit round the core's tip | As tested. The only narrowing, and the lab already runs it |
| 0 to 3 mm in front of the face | A collar, 25 mm OD, threaded onto the outlet end | Capillaries swap without reprinting the auger |
| 3 to 38 mm in front of the face | A capillary: 3 mm bore (v4's exit), 5 mm OD, smooth | Places the powder within a few mm of the target. Vibrated and kept full, it sets the rate between the flight's pulses |

The capillary turns with the tube (`NOSE_OUT`, `NOSE_IN` in `doser_cad.py`). The vibration motor shakes the tube and,
with it, the capillary. [`nose_insets.png`](../ods-lpbf-gifs/out/nose_insets.png) is a cutaway of the outlet and a sketch of what the full
capillary does to the pulses.

![](../ods-lpbf-gifs/out/nose_insets.png)

**Why not a full-bore smooth end?** A 21 mm mouth spills powder off its lowest point, so it can't place powder on a
spot a few mm across. The 3 mm bore is 20 to 60 diameters of a 50 to 150 µm granule, so free-flowing granules shouldn't
arch in it. Cohesive powder might: in PR 176's DEM, cohesive powder bridged in the v4 funnel until a tap freed it. So
the bench tests try 2 and 4 mm bores too.

## Pulses, and how to make the rate steadier

- **The flight delivers one pulse per turn.** PR 176's DEM gives about 0.3 cm³ of bulk powder per turn, about 380 mg
  of 1.2 g/cm³ granules. At 10 mg/s that is one pulse every 38 s.
- **The capillary holds about 250 mm³, about 300 mg,** close to one pulse. Two ways to run it, to compare on the bench:
  - **Screw-metered:** the auger's speed sets the rate, and the vibration only keeps powder moving.
  - **Vibration-metered:** the auger keeps the capillary topped up, and the vibration amplitude sets the rate. A full
    capillary discharges at a rate set by its bore, slope and vibration, more or less independent of the powder above
    it. With the vibration off, it acts as a valve if the bore is narrow enough for the granules to arch.
- **Smaller pulses without a taper:** a two- or three-start flight in the same 21 mm bore. Three starts give three
  pulses of about 127 mg per turn instead of one of 380 mg. That is a bench variant and is not drawn.
- **What vibrating capillaries have shown** ([Edison 02](../doser-atomizer/edison/results/02-steady-low-rate-auger-feeding.md), a literature
  review run through Edison Scientific): about 0.2 mg/s continuously with about 10 µm powder, and 1 mg/s
  at 150 Hz (Matsusaka 1996). Flow starts at about 2.5 m/s² of tube acceleration (1.1 to 3.9), and the maximum rate
  scales roughly as the bore to the power 2 to 2.5. In a larger bore, free-flowing powder kept running after the
  vibration stopped. One pharmaceutical vibrating capillary is reported at 1 to 10 mg/s with under 3 % variation, but
  how that was averaged is unverified.
- **The same review's advice:** don't change the taper, the pitch and the capillary all at once, because each can pack
  powder into a new blockage.
- **Vibration sources:** a coin eccentric-mass motor, a voice coil or piezo shaker, or the stepper itself dithering a
  few microsteps at tens of Hz, which needs no extra part. The render shows a separate motor so the function is
  visible.
- **Blown powder isn't obviously steadier at these rates.** DED powder feeders run at grams per minute. The
  pneumatically assisted microfeeders that reach mg/s meter the powder mechanically first and only then carry it in
  gas.

## Bench tests, before anything else is built

1. **Define steady first.** Log the balance at 10 Hz or faster. Report the delivered mass and its RSD over 0.1, 1, 5
   and 30 s windows, the fraction of time with no flow, the pulse spectrum, and the tail after a stop. A one-minute RSD
   can hide exactly the pulses that matter.
2. **One change at a time,** with a granule surrogate (spray-dried alumina or silica, 50 to 150 µm), at 22.5°, 35° and
   45°:
   - PR 176's tube as is, as the control;
   - two- and three-start flights in the same 21 mm bore, with no capillary;
   - a stationary, separately vibrated short capillary under PR 176's outlet, with adjustable bore and holdup;
   - the capillary on the outlet, turning with the tube: 2, 3 and 4 mm bores, 20 to 40 mm long, vibration on and off,
     watching for holdup and the tail after a stop.
3. **Compare vibration sources:** the existing solenoid tap, a coin eccentric-mass motor, and stepper dithering.
4. **Then a cohesive powder,** to find where the capillary bridges.
5. **Check the shortened flight:** whether 2 to 4 turns meter as well as PR 176's 8.

## Calibration and dose checks

- **The doser closes its loop on a balance under the cup**, as on the bench. Wherever there is room for a balance or
  load cell under the target, that stays the primary measurement: mg per turn and per vibration setting, measured in
  the conditions the dose will see.
- **Weigh the auger cartridge** (tube and cap) before and after a run on a 0.1 mg balance. That gives the total
  delivered, independent of everything else.
- **Video can count the powder in flight**, calibrated against the balance runs. Camera-based powder-flow sensing is
  established in blown-powder DED: an optical sensor converted to mass flow at 125 Hz ran a closed loop
  ([Breese 2021](https://doi.org/10.1007/s00170-021-07438-z)), and a 2025 review counts 34 camera-based methods
  against 4 weight-based ones ([Madeira Araujo 2025](https://doi.org/10.3390/pr13092995)).

## Where it was first drawn: inside the atomizer chamber

[`ods_c_gravity.gif`](../ods-lpbf-gifs/out/ods_c_gravity.gif) (5 fps; [`ods_c_gravity.mp4`](../ods-lpbf-gifs/out/mp4/ods_c_gravity.mp4) has every frame, and
[`ods_c_gravity.json`](../ods-lpbf-gifs/out/ods_c_gravity.json) gives each step's caption and frame range; unlisted on YouTube at
https://youtu.be/ZlRDlSrZXf4) shows the problem it was built for:

- **C.1 and C.2:** the doser as built doesn't fit beside the stream on either side.
- **C.3:** the module, on a slide on the chamber door, upslope of the stream, with its capillary 2.6 mm from the
  stream's surface.
- **C.4 to C.9:** its electronics, loading, calibration in place, feeding, the entry-height knob and an in-run
  on/off control.

![](../ods-lpbf-gifs/out/ods_c_gravity_still.png)

That version is built for the chamber: a 316L auger printed by laser powder bed fusion, PEEK pinions, a vacuum-rated
stepper, vented stainless fasteners, and the POWDER_DOSER_V2 board kept outside the chamber, with only the stepper,
the vibration motor and a thermocouple inside, wired through a multipin feedthrough. **On a bench or a deck in air,
none of that is needed:** PR 176's printed parts, its normal NEMA 11 and its board apply as they are.

## Not checked

- Nothing has been built. The module is PR 176's parts rearranged in CAD.
- Whether the shortened flight meters as well as PR 176's 8 turns, and whether the 3 mm capillary meters steadily.
  The mg figures are estimates from PR 176's DEM volume per turn and an assumed 1.2 g/cm³ granule bulk density. The DEM
  was not re-run for the new parts.
- The store and flight figures above are computed here from the drawn tube pieces and PR 176's `auger.py`. The
  2026-10-06 note had about 14 cm³ and about 4 turns.
- The cradle is a placeholder box, not a designed part. There is no mounting interface for any deck yet.
- The render shows PR 176's tube from outside. The flight and v4 outlet appear only in the cutaway.

## Rendering

[`module_views.py`](module_views.py) draws `module_views.png` and `module_turntable.gif`. Its docstring has the
checkout and install commands. It needs the doser's STEP from the powder-doser repo, cadquery-ocp 7.9 (8.0 moved
`TDF_LabelSequence`) and pyvista 0.49. [`doser_cad.py`](../ods-lpbf-gifs/doser_cad.py) reads the STEP once (about 10 s) and caches the
meshes in `.cache/`. [`nose_insets.py`](../ods-lpbf-gifs/nose_insets.py) draws the cutaway; it takes its fonts from the atomizer GIFs' helper module, so to
run it on its own, swap `gifkit.font` for PIL's `ImageFont.truetype`. The chamber GIF's scene code (`ods_gifs.py`) is
not included: it builds on byu-vcl's rePowder viz3d model and also holds the other atomizer concept animations.

# Mixing in the CubXL's vials: how far the P20 goes, and stirring instead

@benwhitney5463 asked on [#169](https://github.com/vertical-cloud-lab/byu-vcl/issues/169)
(2026-10-09) after `pipette_test_mix` ran 12/12
([`pipette_test_mix_20261009b`](../results/pipette_test_mix_20261009b/README.md)).
Vial_2 held water-based acrylic paint, and the mix "really only mixed in a very
small area". How much harder can the pipette mix, and would magnetic stirring be
better?

**Short answer.** The P20 can mix somewhat harder, but no setting gets it to mixing a
20 mL vial. The limit is the stroke: 20 µL is a fraction of a percent of what is in
the vial. Changing *where* it aspirates and dispenses is the one P20 change worth
trying, and it needs no code. For vial-scale mixing, put a stir bar in each vial and
a stirrer under each vial position. The P300 would help a lot (15× per stroke) but
would still be short of a few mL, and it costs the 1–20 µL range.

Nothing here has been tried on hardware. It is analysis of the 10-09 run record,
CubOS at the Pi's commit `496819c`, and Opentrons' published pipette definitions.

## What the 10-09 `mix` did

- **All six strokes were within 1 mm of one spot.** CubOS's
  [`PipetteInstrument.mix`](https://github.com/Ursa-Laboratories/CubOS/blob/496819c/packages/core/src/cubos/instruments/pipette/interface.py#L88-L120)
  aspirates at the engage height, rises `lift_mm`, dispenses and aspirates, drops
  back, and dispenses. `lift_mm` is fixed at 1.0 mm; the YAML `mix` command has no
  way to change it. The engage height was −35, the tip end 35 mm below the rim.
- **`speed` in the YAML does nothing on this pipette.** The Opentrons driver always
  sends 0
  ([`opentrons.py`](https://github.com/Ursa-Laboratories/CubOS/blob/496819c/packages/core/src/cubos/instruments/pipette/vendors/opentrons.py#L37-L42)),
  so the firmware runs at its own rate: the 100 µs step floor, ~8,700 steps/s, which
  is 10.9 mm/s of plunger or ~8 µL/s
  ([firmware README](../firmware/README.md)). That is about Opentrons' default P20
  flow rate (7.56 µL/s).
- **Each stroke moved 20–23 µL**, 2.86 s each way. One 3-cycle `mix` passed about
  0.13 mL through the tip in ~40 s, which is ~0.24 mL per minute.

## Why only a small region mixed

1. **The stroke is tiny next to the liquid.** The vials are 28 mm outside diameter
   (deck file), so about 25 mm inside: every 1 mm of depth holds ~0.49 mL. If they
   are the capper BOM's 20 mL VOA vials (typically 28 × 57 mm), a tip end 35 mm below
   the rim sits ~20 mm above the bottom, and only reaches liquid when the vial holds
   ~10 mL or more. At 10 mL a 20 µL stroke is 0.2% of the liquid, and a whole `mix`
   is 1.3%. In a 2025 survey of 96-well protocols, the few that give the mix
   volume as a share of the well use values such as 50% and 80%
   ([King 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12776400/)). By that rule
   the P20 suits about 25–40 µL, a few hundred times less than the vial holds.
2. **The jet is small and slow.** 20 µL is a sphere 1.7 mm in radius. At ~8 µL/s
   through a ~0.5 mm orifice (my estimate for a 20 µL tip, not measured) it leaves
   at ~4 cm/s, a Reynolds number around 20 in water. That jet is laminar and loses
   its speed close to the tip. Paint is far more viscous than water, so in paint it
   travels even less.
3. **In and out at the same spot mostly undoes itself.** At low Reynolds number,
   drawing a volume in and pushing it back out from the same place returns most of
   the liquid to roughly where it came from. A 1 mm lift between strokes changes
   little. Viscous paint is the worst case for this.

The King survey (wells, not vials) also found three cycles often too few for a
gentle, small jet, and suggests 5–10 strokes for hard mixes. It found tip placement
and angle second-order *in a well*. In a vial whose depth is many times the jet's
reach, where the tip draws from and where it returns to matters much more.

## How far each P20 setting can go

| setting | now | how far it can go | what it buys |
|---|---|---|---|
| cycles | 3 (6 strokes), ~11.6 s each | 10–20. YAML only | Proportionally more liquid through the tip. 20 cycles ≈ 4 min and ~0.9 mL, still under 10% of a 10 mL fill |
| where it draws and returns | within 1 mm of one spot | Draw near the bottom, return near the top (or the reverse) with `transfer`; see below. YAML only | Breaks the in-and-out reversibility and lifts settled paint. The most useful P20 change for a layered sample |
| plunger speed | 10.9 mm/s, ~8 µL/s: the firmware's step floor | Opentrons' P20 GEN2 maximum is 24 µL/s, ~32 mm/s or ~25,600 steps/s at 796 steps/mm. Needs firmware work: faster step timing plus an acceleration ramp, then the post-run `HOME` check for lost steps | ~3× the jet speed and ~0.7 mL/min through the tip instead of 0.24. Still 20 µL per stroke |
| stroke volume | 20 µL | None. A 20 µL tip holds 20 µL; drawing more pulls liquid into the pipette | — |

Even with every setting at its limit, the P20 passes under 1 mL a minute through
its tip, and passing liquid through the tip is not the same as mixing it.

### Draw low, return high, with `transfer` (not run)

The YAML can't send a bare `dispense`: CubOS keeps it off the protocol commands
([`pipette.py`](https://github.com/Ursa-Laboratories/CubOS/blob/496819c/packages/core/src/cubos/protocol_engine/commands/pipette.py#L316-L327)).
But `transfer` takes separate `source_height` and `destination_height`, and splits
a volume over the model's 20 µL into equal strokes of up to 20 µL
([`pipette.py`](https://github.com/Ursa-Laboratories/CubOS/blob/496819c/packages/core/src/cubos/protocol_engine/commands/pipette.py#L496-L506)).
A transfer from a vial into the same vial is therefore a vertical mix:

```yaml
  # Untested sketch. 10 strokes: draw 20 uL low, return it high.
  - transfer:
      source: vial_2
      destination: vial_2
      volume_ul: 200.0
      source_height: -45.0       # PLACEHOLDER: set from the measured inside depth
      destination_height: -30.0  # PLACEHOLDER: just under the liquid surface
```

Before running it:

- **Measure the vial's inside depth from the rim.** The deck file says `height: 83`,
  but a 20 mL VOA vial is about 57 mm tall. A `source_height` past the bottom drives
  the tip into the glass, and `validate_setup` checks reachability, not whether the
  vial is that deep.
- Check in the validate and mock gates, before anything moves, that `transfer`
  accepts the same vial as source and destination, that it plans ten 20 µL strokes,
  and what path the gantry takes between the two heights.
- On this firmware the first `ASPIRATE` after a tip pick-up pushes ~21 µL of air
  out through the tip on its way down to prime, so the first stroke bubbles. With
  paint, that can foam. After that, each stroke draws ~23 µL rather than 20,
  because it starts from the blowout plane.

## The P300 for comparison

From Opentrons' own definitions
([`pipetteNameSpecs.json`](https://github.com/Opentrons/opentrons/blob/558eca0/shared-data/pipette/definitions/1/pipetteNameSpecs.json),
[`pipetteModelSpecs.json`](https://github.com/Opentrons/opentrons/blob/7032da6/shared-data/pipette/definitions/1/pipetteModelSpecs.json)):

| | P20 GEN2 | P300 GEN2 |
|---|---:|---:|
| max per stroke | 20 µL | 300 µL |
| µL per mm of plunger (`ulPerMm`, top row) | 0.746 | 9.16 |
| default flow rate (API ≥ 2.6) | 7.56 µL/s | 92.86 µL/s |
| max flow rate | 24 µL/s | 275 µL/s |
| at our firmware's 10.9 mm/s | ~8 µL/s | ~100 µL/s |
| one 3-cycle `mix` | ~0.13 mL | ~1.8 mL |
| one stroke, as a share of 5 / 10 mL | 0.4% / 0.2% | 6% / 3% |
| min volume | 1 µL | 20 µL |

So the P300 does make a big difference: 15× per stroke and ~12× per second at the
same plunger speed, with a much stronger jet. It uses the same 10-pin header, and
Ursa's stack was built around one (the PANDA firmware it runs shipped with P300
constants; [wiring doc §7](opentrons-pipette-wiring.md#7-consequences-that-outlive-the-wiring-fix)).
But 300 µL is still only 3–6% of a few-mL fill, its minimum is 20 µL, and it needs
its own firmware constants, 300 µL tips, a tip rack and new Z heights.

## Stirring instead

Most of these put a PTFE-coated stir bar in each vial and turn it with a rotating
magnetic field from outside. **The current rack holds the 28 mm vials at a 33 mm
pitch** (vial_1 at Y 45, vial_2 at Y 78), so there is only ~5 mm between vials.
Anything that has to go *around* a vial needs a new rack. Anything *under* a vial
fits the present one.

| option | how | for | against |
|---|---|---|---|
| **A. Stir plate under each vial** (rotating magnets) | A small 12 V brushless fan (30–40 mm) or N20 gear motor with two N52 disc magnets on the hub, one north-up and one south-up, spaced to the ends of the stir bar. Speed by PWM through a logic-level MOSFET (the capper BOM's IRLZ44s): a knob at first, later a spare pin on the PAW Arduino, which needs a new firmware command | Cheap (roughly $10–15 a position), the classic DIY stir plate, strongest coupling for the money | Needs ~10–20 mm under the vial, so the rack goes up and the vial Z heights get re-taught. Moving parts |
| **B. Rotating field from fixed coils** (no moving parts) | Four small coils under the vial at 90°. Each opposite pair, wound or wired in opposition, is one phase of a bipolar stepper driver. The stir bar is then the rotor: one bar revolution per 4 full steps, so 600 rpm is 40 full steps/s. The Tic T500, now off the plunger, can drive it straight from the Pi over USB (`ticcmd --velocity`), and its current limit sets the field strength | Thin, quiet, no wear. One driver can run several vials with their coils in series. No Arduino firmware | Less torque than NdFeB magnets at the same gap. The coils warm the vial a little. Commercial "induction stirrers" work this way (e.g. [Heathrow Scientific's](https://heathrowscientific.com/magnetic-induction-1), 50–2,000 rpm), and [fablab RUC's open build](https://fablab.ruc.dk/magnetic-stirrer/) uses 3 coils, an Arduino and an L298N |
| **C. Magnets on either side** (Ben's idea) | Magnets on opposite sides of the vial, one with north facing in and one with south, turning around the vial's axis | Works: the field across the vial is horizontal, so it turns a horizontal bar | The magnets have to orbit the vial, so they need a ring bearing and clearance all round, which the 33 mm pitch doesn't leave. As fixed coils at the sides, it becomes B with the same clearance problem |
| D. Vortex or orbital shaking | A vibration motor or a small orbital shaker under the rack, with the vial capped first (the capper can) | Nothing goes into the vial | Shakes the vial positions that the capper and pipette rely on. Vial_1's decap has already been marginal |
| E. Stir with the tip | Small XY circles with the tip submerged (GRBL `G2`/`G3`) | No new hardware | Needs a new CubOS command and collision checks. The neck limits the circle (the press-fit caps are `VialCap16mm`), and a P20 tip is a weak paddle that paint could pull off |
| F. Overhead stirrer tool | A small DC motor with a paddle on the head | High torque, handles paint | Wash or swap the paddle between vials. Another tool on the head |

**My suggestion:** start with A under one vial position. It is the cheapest and
strongest, and it answers the paint question quickly. Move to B if the height or the
moving parts become a problem. Stirring is routine in electrochemistry anyway: stir
to homogenise, then a quiet period before the measurement. So the same hardware
serves the potentiostat plans.

```
 A. Side view, one vial                    B. Top view, four coils under the vial

        | |  <- tip, >= 8-10 mm                       (1) phase A, north up
     |  | |  |    off the bottom
     |  \ /  |                                   (4)    ======    (2)
     |~~~~~~~|  <- liquid                    phase B   stir bar  phase B
     | [===] |  <- stir bar                  south up             north up
     +-------+  <- glass bottom, ~1.5-2 mm
  ===============  rack floor: thin or open           (3) phase A, south up
      N     S    <- two disc magnets
    [ fan hub ]                                Bipolar stepper driver (the Tic):
    [ 12 V fan ]  speed by PWM via a MOSFET      phase A = coils 1 + 3 in series
                                                 phase B = coils 2 + 4 in series
                                                 the bar turns once per 4 full steps
```

Practical points for either one:

- **Keep the gap small.** The coupling falls off steeply with distance, and the
  magnet-to-bar distance is the variable DIY builders find matters most. Aim for
  ≤ ~5 mm from magnet top to the inside bottom of the vial: a thin or open rack
  floor, plus the ~1.5–2 mm of glass.
- **Stir bar:** PTFE-coated, about 12–15 mm long for a ~25 mm bore. Ramp the speed up
  rather than stepping it, or the bar decouples and rattles. Viscous liquids want
  lower speed and a stronger bar.
- **Keep the tip clear of the bar**, about 8–10 mm off the bottom, and stop stirring
  while pipetting. The vortex lowers the surface at the centre.

## A quick way to compare options

Put a known volume of water in a vial (say 5 mL), let the pipette put 20 µL of food
dye on the bottom, then photograph from the side at fixed times: after today's `mix`,
after the `transfer` sketch, and after 30 s on a stirrer. The deck cameras look down
at the vials, so a phone on a stand gives a better side view.

## What would sharpen this

- How much liquid vial_2 held, and how much paint went in.
- The vials' inside depth from the rim.
- What the real experiments will mix: aqueous solutions for the potentiostat behave
  much more like water than paint does, and their volumes decide between the P20
  plus a stirrer and the P300.

## Sources

- M. R. King, "Pipette, mix, repeat: A reduced-order fluid model and protocol survey
  to evaluate 96-well mixing protocols", bioRxiv preprint, 2025
  ([PMC12776400](https://pmc.ncbi.nlm.nih.gov/articles/PMC12776400/)). Not yet peer
  reviewed.
- Opentrons pipette definitions, `shared-data/pipette/definitions/1/` (linked above).
- CubOS at `496819c`, the commit on the CubXL Pi (linked above).
- DIY stir plates: [KJ Magnetics, *Stirring with magnetic bars*](https://www.kjmagnetics.com/blog/stirring-with-magnetic-bars),
  [Make: homebrew stir plate](https://makezine.com/projects/homebrew-stir-plate),
  [thepulsar.be DIY magnetic stirrer](https://thepulsar.be/article/diy-magnetic-stirrer).
- Rotating-field stirrers: [fablab RUC magnetic stirrer](https://fablab.ruc.dk/magnetic-stirrer/),
  [US4199265A](https://patents.google.com/patent/US4199265) (motorless magnetically
  coupled stirrer).

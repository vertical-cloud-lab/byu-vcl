# A vacuum press for the charge cups

[`vacuum_press.py`](../vacuum_press.py), byu-vcl #303, for DAL #140 ("Vacuum Hydraulic Powder Press to Avoid
Explosions") and DAL #156. Sterling: the plug should go in all the way and compress the powder to a set tonnage, and
a vacuum press would be better. This note covers the press chosen, what it looks like, how it is run, the numbers,
and what a robot needs to run it. The model is drop-in for the plug press in `charge.press_parts()`, so
`alloy_charge.py` can use it. That swap has not been made yet.

```
xvfb-run -a python3 vacuum_press.py          # the clip -> out/vacuum_press.gif, out/mp4/vacuum_press.mp4, still, .json
python3 vacuum_press.py numbers              # the numbers only -> out/vacuum_press.json
```

## The press: Specac Atlas Autotouch 15T

**Off the shelf:** the Specac Atlas Autotouch 15T (part no. GS2581X, 230 V; there are 110 V versions), a two-stage
rotary-vane pump, isolation valve V1, vent valve V2 with a needle valve, and a Pirani gauge.

**Ours:** the evacuable die round F1, the punch, the ejector pin, the shuttle with its rails and stand, the ejector
under the shuttle's out position, and the dry Ar line on V2.

Why the Autotouch:

- **It is automatic.** A program has up to 10 steps ("pump up to", "maintain for", "release to"), and one Start
  press runs the whole program. "Maintain Load" tops the load back up as the powder settles. Release can be fast,
  medium or slow.
- **Its numbers are published,** and Specac's own videos show its whole cycle (below).
- **It takes evacuable dies.** Specac makes them (13 mm GS03000, and 32/40 mm Atlas dies with an evacuation port,
  GS26101/GS26102). Its KBr video gives the vacuum procedure.
- **The 15T's range fits.** It presses 2-15 t in 0.2 t steps. That covers the 3.2 t needed here, with room for Cu
  cups. The 8T (1-8 t) and the 25T share its frame.
- **Specac has used it to cold-compact metal-matrix-composite powders:** application note AN21-11, and a video,
  `FBPlvkuo6mU`, which is no longer available.

The others considered:

| Press | For | Against |
| --- | --- | --- |
| Carver AutoPellet RP | 25/40 t; touchscreen recipe (clamp force, dwell, decompression rate, *ejection force*); "provision for vacuum line connection to the pellet die"; glovebox-friendly | No dimension sheet found (375 lb on a Spectra datasheet); 25 t minimum frame for a 3 t job; no video of the vacuum use found |
| SPEX 3636 X-Press | 35 t automatic; 20 x 13 x 22.5 in; final pressure, dwell 0-10 min, release 0-10 min; door interlock; video `edVBi2R-hQQ` | Its pages say "standard die sets"; only its predecessor (3635) is stated to take SPEX evacuable dies; minimum 10 t, far over 3 t |

The Carver is the fallback if an integrated ejection stroke matters more than size and price. Its "ejection force"
setting suggests the press can push the pellet out itself.

## Sources

- Specac Autotouch product page,
  <https://specac.com/product/autotouch-press-high-throughput-xrf-press/> (read 2026-11-04). Gives:
  - 425 x 405 x 640 mm (W x D x H), 95 kg (8T/15T/25T);
  - ram stroke 24 mm, piston Ø82, leadscrew nose Ø32;
  - 40-155 mm between the pressing faces;
  - working area Ø220 x 155 mm;
  - load ranges, 6 programs x 10 steps, hold 0-99 min, 3 release rates;
  - part numbers.
- Specac, "How to use an automatic hydraulic press",
  <https://specac.com/theory-articles/how-to-use-an-automatic-hydraulic-press-spectroscopy-guides/>. It gives the
  sequence: raise the guard, centre the die, wind the leadscrew down onto it, lower the guard. The screen shows
  "Close Guard" and nothing runs until the guard is down. Then Start: "Load Rising", "Maintaining Load", Stop, then
  "Fast Release".
- Videos, read as storyboards and frames through the lab's Pi (`frames.py`; frames are not committed):
  - [`BH___JpLYeE`](https://www.youtube.com/watch?v=BH___JpLYeE), *How to make an XRF pellet with Specac's
    Autotouch hydraulic press* (Specac, 2:45). Product shot 0:17, used for the overall proportions. Die assembly
    0:33-1:03. Die in the press, leadscrew down, guard raised then closed 1:04-1:19: the guard slides down by a
    handle on its bottom rail. Programming 1:20-1:53. A two-stage program runs 1:55-2:13 ("pump up to 3.0 t,
    maintain 0.3 min, pump up to 4.0 t, maintain 0.3 min, medium release"). Die out 2:15-2:28.
  - [`b2jWgsfSmMQ`](https://www.youtube.com/watch?v=b2jWgsfSmMQ), *Using Specac's Autotouch press for XRF sample
    prep* (Specac, 2:51). Die assembly 0:13-0:35. Die in, leadscrew down 0:37-0:47. Guard closed, front view of the
    working area and tower 0:51. Pressing and hold 0:51-1:08. Die out and pellet ejected 1:10-1:32. The whole press
    from the front-left 1:34-2:15.
  - [`ehN10mMm-T8`](https://www.youtube.com/watch?v=ehN10mMm-T8), *How to Make a Good KBr Pellet* (Specac, 1:54),
    for the evacuable-die procedure. 1:02-1:20: "The leadscrew is brought down into contact with the plunger. A
    vacuum pump is attached to the evacuation port on the die and pumped for 1-5 minutes. The press is then pumped
    up to 5 tons … and wait 1-3 minutes." 1:21-1:28: release, take the base off, invert the die on its extractor
    ring, and press the pellet out.
- #222 (branch `claude/issue-222-20260925-0343`, `atomizer-charge/README.md`) gives:
  - E4: 9.9 g AlSi10Mg filling the bore, plug pressed flush, about 75 % dense, at about 100 MPa (1.3 t);
  - press fit 1.3-1.6 t at µ 1.05-1.35 (µ 0.4 sliding), at 30.7 MPa contact for .0008 in interference;
  - "Reserve 2 t";
  - tapped densities: AlSi10Mg 1.60, Si 1.10 g/cm³;
  - "push the cup out through F1 with a 5/8 in drift";
  - Edison's warning that compacting a near-sealed capsule hydraulically removes the volume the gas needs.
- Pump: no datasheet was checked. It is drawn as a small two-stage rotary-vane pump, about 300 x 140 x 190 mm.
  Resellers list an Edwards RV3 at about 2 x 10⁻³ mbar ultimate.

## What it looks like (the model)

The model is in mm. In the press frame the origin is on the bench at the centre of the 425 x 405 footprint, z is up
and front is -y.

**From the press itself:**
- The press column is on the left, 292 mm wide: a grey plinth (115 mm, rounded front), a blue drum round the
  cylinder (Ø250 x 120), grey side plates, and a crosshead under a grey top housing up to 640 mm.
- The blue control tower is on the right, 133 mm wide and 500 mm tall. It carries the touchscreen (centre about 420
  mm up), and the Start and Stop buttons under it.
- The piston face is at z = 245 with the ram down. It rises 24 mm.
- The leadscrew nose hangs from the crosshead. The crosshead's underside is 155 mm above the piston face.
- The guard is clear PETG, curved, in a grey frame. It slides up 165 mm to open.

**Measured or assumed:**
- Scaled from the product shot: the column and tower widths and the heights.
- Assumed: the press axis 66 mm left of and 56 mm in front of the footprint's centre, and the depths of the column
  and tower.

**Ours:**
- **The die** is a Ø80 steel body with F1 in a Ø31.80 bore, standing on a 15 mm floor.
  - The cup's base is on the bore floor, on a Ø15.9 (5/8 in) ejector pin. The pin is flush with the floor and backed
    by the piston, so it is #222's drift built in.
  - The bore runs 22 mm above F1, to guide the punch.
  - The vacuum port (KF16) opens into the bore 4 mm above F1. It needs a sintered filter disc against the powder.
- **The punch** is Ø31.70 hardened steel, 30 mm long, with a Ø50 x 12 flange for the gripper. Its Viton O-ring is
  10 mm above its face, so it seals before the plug moves and never passes the port.
- **The shuttle** is a 110 x 110 x 15 mm plate on two rails, 230 mm of travel, out to a stand in front of the press.
  It sits on the rails, and the piston lifts it off them.

## The cycle, as a robot runs it

| # | Step | Who | Needs |
| --- | --- | --- | --- |
| 1 | Guard up | guard actuator (or the arm, by its handle) | a guard actuator; the interlock stays in circuit |
| 2 | Shuttle out (230 mm) | shuttle drive | rails, a drive, end sensors |
| 3 | Ejector pin up 90.5 mm, the cup's base 4.5 mm over the body | ejector | an actuator under the out position |
| 4 | Dosed cup onto the pin; pin down lowers it into F1 (line-to-line fit) | arm, ejector | as `alloy_charge.py` already does with the nest's ejector |
| 5 | Plug set in the mouth on its lead-in, 8.0 mm proud | arm, from above | as now |
| 6 | Punch into the bore; O-ring seals; it rests on the plug | arm (punch weighs about 0.3 kg) | a rack spot for the punch |
| 7 | Shuttle in; guard down | shuttle, guard | the hose and rails pass under the guard's bottom rail |
| 8 | V1 opens through the needle valve, then fully; hold 2 min under 1 mbar | PLC | V1 (solenoid), needle valve, Pirani gauge readout |
| 9 | Start: program P1 (pump up to 3.2 t, maintain 1.0 min, slow release to 0 t) | the arm presses Start, or a remote input | the Start button within the arm's reach |
| 10 | The ram closes the 2 mm gap to the leadscrew, pushes the plug 8.03 mm to flush, then F1 takes the rest | press | |
| 11 | V1 shuts; V2 lets in dry Ar to 1013 mbar | PLC | V2, Ar regulator |
| 12 | Release to 0 t; ram down | press (end of P1) | |
| 13 | Guard up; shuttle out; arm lifts the punch | | vent first: under vacuum, about 80 N holds the punch down |
| 14 | Ejector pushes the cup up out of F1; the arm takes it | ejector, arm | the push-out force (below) |

The leadscrew is wound down by hand once, to 2 mm over the punch's top. That leaves 145.5 mm between the faces. The
cycle uses 10.0 of the 24 mm stroke.

## The numbers (`out/vacuum_press.json`)

The bore is Ø12.70. The plug is set 1.49 mm into the mouth and travels **8.03 mm** to flush. The powder is tapped up
to the set plug's bottom, so the plug starts on it.

| | Set (before) | Flush (after) |
| --- | --- | --- |
| Powder column above the bore floor | 46.13 mm | 38.10 mm |
| Volume, with the drill point | 6.005 cm³ | 4.987 cm³ |
| 9.61 g AlSi10Mg (2.67 g/cm³ solid) | 1.60 g/cm³, 59.9 % | 1.93 g/cm³, **72.2 %** |

The cavity volume here is the bore's own. `charge.volumes()` gives 4.903 cm³, because it draws the powder 0.05 mm
inside the wall.

Ram force over the plug's travel:

| x, mm | rel. density | powder, MPa | powder, kN | fit sliding, kN | fit breakaway, kN | total sliding, kN | total breakaway, kN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.599 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1.6 | 0.620 | 12 | 1.5 | 0.7 | 2.5 | 2.3 | 4.0 |
| 3.2 | 0.643 | 26 | 3.3 | 1.7 | 5.8 | 5.0 | 9.1 |
| 4.8 | 0.667 | 42 | 5.3 | 2.7 | 9.1 | 8.0 | 14.4 |
| 6.4 | 0.693 | 60 | 7.6 | 3.7 | 12.4 | 11.3 | 20.0 |
| 8.03 (flush) | 0.722 | 82 | 10.3 | 4.7 | 15.7 | 15.0 | 26.1 |

How the force is built up:

- **Powder.** A Heckel line, ln(1/(1−D)) = K·P + A, through the tapped density at 0 MPa and #222's E4 point (9.9 g
  flush: 74.3 % at 100 MPa). That gives K = 0.00446 /MPa (a yield pressure of 224 MPa). The E4 point is #222's
  estimate, not a measurement.
- **Fit.** #222's press fit (30.7 MPa over the plug's length: 1.25-1.61 t breakaway at µ 1.05-1.35, 0.48 t sliding
  at µ 0.4). It is scaled by how much of the plug's straight land has entered the bore's straight part, from 0 at
  0.41 mm of travel to all of it at flush.

The set point follows:

- **At flush:** 1.05 t on the powder, plus 0.48 t of sliding fit = 1.53 t if the plug keeps moving. If it sticks
  near the end it needs up to 2.66 t to start again.
- **Set point: 3.2 t (31.4 kN).** That is 1.05 t on the powder plus #222's 2 t reserve for the fit, rounded up to
  the 15T's 0.2 t step. The excess over what it takes to reach flush goes into F1, which is as long as the cup: 32 MPa
  on its annulus at 3.2 t.
- **The density is set by the geometry.** F1 stops the plug at flush, so the dose sets the final density. Raising
  the set point only loads F1. To compress to a chosen pressure, choose the dose: m = ρ_solid · V_flush · D(P). The
  catch is that the dose then has to fit under the set plug. E4's 9.9 g (100 MPa, set point 3.4 t) stands 1.5 mm
  above the set plug's bottom, so the arm couldn't seat the plug on it. 9.61 g (82 MPa) is the most that fits at
  1.60 g/cm³ tapped.

**Gas in the pores.** If none escapes through the vent while the plug goes in, this is the upper bound:

| | Before pressing | At flush | Sealed, at 700 °C |
| --- | --- | --- | --- |
| Air, no vacuum | 1013 mbar, about 100 µmol | 1755 mbar | 5.8 bar |
| Pumped to 1 mbar | about 0.1 µmol | 1.7 mbar | 5.8 mbar |

That thousandfold drop in the gas is what the vacuum buys. It answers Edison's warning on E4.

**The current runs don't compact anything.** `charge.RUNS` doses for composition, not fill:
- **Al-10Si:** 3.92 g Si stands 18.4 mm below the set plug.
- **Cu-10Ni:** 12.97 g Ni stands 25.5 mm below.
- **In both,** the plug goes in flush without reaching the powder.

Filling to the set line would take 6.61 g Si (15.8 wt% Si in a 5N Al cup) or 29.4 g Ni (20.1 wt%). To keep 10 wt%
and still compact, fill the rest with powder of the cup's own metal (premixed, as #222's E3 does) or use a shorter
bore.

## API (for `alloy_charge.py`)

- `press_parts()` returns `{group: {name: (mesh, colour)}}` in the press frame unless noted:
  - **`fixed`:** plinth, drum, column, dome, leadscrew, rails, stand, tower.
  - **`screen`:** bezel, screen, label, badge, buttons, switch.
  - **`guard`:** frame, handle, panel. Draw the panel at `PETG_ALPHA`. Shown closed; open is +`VP["guard_open"]`
    (165) in z.
  - **`ram`:** the piston, face at `VP["piston_down"]` (245). It moves +z by 0-24.
  - **`shuttle`:** plate, body, f1, port. The frame's origin is the plate's underside on the die axis. Place it at
    `(AXX, y, 245 + ram)`, with y from `VP["shuttle_out_y"]` (-286) to `VP["shuttle_in_y"]` (-56).
  - **`pin`:** child of the shuttle. Its top is at `VP["cup_base_local"]` (30) + e, with e from 0 to `VP["eject"]`
    (90.5).
  - **`ejector`:** the push rod in the stand, top at 0. Place it at `(AXX, -286, 245 + e)`.
  - **`punch`:** face at 0. It sits in the shuttle frame at `VP["punch_set_local"]` (101.53) minus the plug's travel.
  - **`vacuum`:** pump, fan, handle, block, valves, knob, gauge, display, line, ar_line.
- `hose(p_port)`: the flexible hose from the die's port (world) to the valve block. Rebuild it each frame.
- `die_parts(cut=True)`: half sections of the body, F1, punch, O-ring and pin, as `charge.lathe`.
- `channel_strip()`: DAL #156's channel across the plug's top.
- `press()`: the press assembled, for static scenes.
- `compaction(powder, mass_g)`, `runs_vs_set_line()`, `report()`: the numbers.
- **Key points** (press frame, z up from the bench):

  | Point | (x, y, z) |
  | --- | --- |
  | Cup base, in the press, ram down | (-66, -56, 275) |
  | Cup base, out, pin down | (-66, -286, 275) |
  | Cup base where the arm sets and picks the cup (pin up) | (-66, -286, 365.5) |
  | F1 top, out | (-66, -286, 338.5) |
  | Die body top, out | (-66, -286, 360.5) |
  | Leadscrew nose | (-66, -56, 390.5) |

  The plug is set 1.49 mm into the mouth, its top 8.03 mm above F1's top. The punch's flange top is 143.5 mm above
  the plate's underside.
- **Footprint:** the press is 425 x 405 x 640 mm. With the shuttle's stand in front (to y = -361) and the pump on the
  left (to x = -560), it is 773 x 766 mm.
- **The arm works only at the out position:** cup and plug from the front and above, as now, and the punch by its
  flange from above.

## Open questions for the lab

1. **The guard.** The press won't start with the guard open, and the guard's bottom rail closes onto the drum. The
   shuttle's rails and the die's hose have to pass under it: a 12 mm slot, or a guard that stops 12 mm higher.
   - Specac would have to agree that it still guards.
   - The guard also needs an actuator, or the arm can lift it by its handle.
   - Ask Specac too whether the Autotouch has a remote-start input. Otherwise the arm presses Start.
2. **Ejection force.** After pressing, the cup is tight in F1: the bore yields at about 73 MPa (#222), and the
   powder reaches 82 MPa. Measure the push-out force on the first cup before choosing the ejector. Pneumatics give
   about 0.2 t at Ø63 and 6 bar; if it needs more, use an electric ejector or a second press stroke on an
   extractor ring, as Specac's KBr method does.
3. **The plug's channel.** The punch rests on the plug during pump-down, so the plug's vent breathes only through a
   channel across its top (DAL #156). Without one, the gas under the plug is pumped only around the unseated lead-in.
4. **Pump-down rate.** Edison warns that the Ø1/16 in vent can draw powder out during pump-down. Soft-pump through
   the needle valve; the right rate and hold (Specac's KBr procedure says 1-5 min) are to be found on the first cups.
   Put the filter in the port either way.
5. **Vent gas.** The plug is vented, so whatever the die is vented with fills the compact's pores. Use dry Ar (the
   furnace is pumped and Ar-filled anyway), not room air. Sealing under vacuum (crimping or welding the vent) is
   the other option, and a much bigger change.
6. **Doses.** The current 10 wt% doses don't reach the plug (above). Decide between filling to the set line, a
   premix with the cup's metal, or a different cup.
7. **Calibration.** The Heckel line rests on one estimated point. Press E4-style cups at two or three doses and
   weigh, gauge and section them. The Autotouch shows load but not ram position, so travel must come from the plug's
   final height. The cup's OD after pressing is #222's check anyway.
8. **Cu cups.** No numbers here for the Cu plug's fit or Ni's compaction. Cu's higher yield likely means a higher
   breakaway; the 15T has room.

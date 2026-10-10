# Open-source magnetic stirrers: what the stirrer design draws on

This is the background for [`README.md`](README.md): what the Pioreactor actually
does, the other published fan-and-magnet stirrers, and what recurs across them.
Gathered on 2026-10-10 from the Pioreactor's repositories, docs, forum and shop, two
Edison literature queries, and a search of GitHub and the open-hardware literature.

## The Pioreactor's stirring, in detail

Pinned sources:

- software: [`Pioreactor/pioreactor@0ae14c0`](https://github.com/Pioreactor/pioreactor/tree/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c)
- hardware: [`Pioreactor/hardware@ca40a91`](https://github.com/Pioreactor/hardware/tree/ca40a91e728801b139b1086853f7cf74ce76def9) (CC BY-SA 4.0)
- docs: [`Pioreactor/docs.pioreactor@6e07789`](https://github.com/Pioreactor/docs.pioreactor/tree/6e0778995487c8e9aec60bfac6ea168bef312be4)

The v1.5 parts list is on [Printables 1471620](https://www.printables.com/model/1471620).
Its mechanical parts are published as meshes only (no STEP), under the Open Community
License v1. The v1.1 files ([Printables 863347](https://www.printables.com/model/863347-pioreactor-20ml-v11-printable-parts))
are CC-BY-SA. The magnet carrier here is re-modelled from dimensions measured off the
v1.5 mesh, not copied.

| | Pioreactor v1.5 (20 mL) | Source |
|---|---|---|
| Fan | Orion **OD4010-12HSS**: 40 × 40 × 10.5 mm, 12 V, 0.07 A, 2-wire (no tach), sleeve bearing, holes Ø3.5 on 32 mm | v1.5 BOM; [forum 628](https://forum.pioreactor.com/t/ordering-information-for-cables-schematic-for-pioreactor-hat/628/2) |
| Why 2-wire | "slightly cheaper… fits into the design of the existing PWM outputs… The hall sensor setup we use is basically what a 3-or 4-pin fan does, too." | [forum 288](https://forum.pioreactor.com/t/why-did-you-choose-to-use-a-2-pin-fan-instead-of-a-3-or-4-pin-fan/288/2) |
| Magnets | 2 × neodymium, 0.250 × 0.060 in, "two magnets of opposite orientation" | v1.5 BOM; [dev log 8](https://pioreactor.com/blogs/pioreactor/pioreactor-development-log-8) |
| Magnet holder | Printed, Ø24.0 × 3.23 mm, 1.55 mm floor, pockets Ø6.66 × 1.675 mm open to the vial, **9.8 mm** centre to centre (measured from the mesh) | `magnet_holder.3mf`, Printables 1471620 |
| Stir bars | 20 mL: PTFE 3 × 12 mm. 40 mL: 15 × 6 mm with pivot ring. "maximum length of a stir bar is 20mm" | [shop 2003](https://pioreactor.com/products/3-mm-ptfe-stir-bar), [shop 2046](https://pioreactor.com/products/15x6mm-ptfe-stir-bar), [FAQ](https://github.com/Pioreactor/docs.pioreactor/blob/6e0778995487c8e9aec60bfac6ea168bef312be4/user-guide/99-common-questions.mdx#L145-L171) |
| Vial | 20 mL borosilicate, 27.5 mm OD, 57.4 mm tall, 24-400 thread | [shop](https://pioreactor.com/products/20ml-glass-vial) |
| Drive | PWM channel 1 = GPIO17, software PWM, `pwm_hz=200`, from the Pi's 5 V | [pwm.py](https://github.com/Pioreactor/pioreactor/blob/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c/core/pioreactor/utils/pwm.py#L96-L114), [config](https://github.com/Pioreactor/pioreactor/blob/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c/packaging/shared-assets/pioreactor/config.example.ini#L26-L37), [external power](https://github.com/Pioreactor/docs.pioreactor/blob/6e0778995487c8e9aec60bfac6ea168bef312be4/user-guide/03-Extending%20your%20Pioreactor/09-external-power.md#L9-L37) |
| Driver circuit | HAT schematic not published. Its STEP shows BSS316N-footprint N-MOSFETs with a diode beside each 2-pin output, so a low-side switch plus flyback (inferred) | [HAT v1.2.step](https://github.com/Pioreactor/hardware/blob/ca40a91e728801b139b1086853f7cf74ce76def9/CAD/HAT/HAT%20v1.2.step) |
| Speed sensing | Not the fan's tach. A TI **DRV5021A3** Hall switch on the heater board, under the vial, 5.3 mm off centre, over the magnets' path. Open drain to GPIO21, falling edges, **1 pulse per turn** (checked by filming the bar) | [heater BOM](https://github.com/Pioreactor/hardware/blob/ca40a91e728801b139b1086853f7cf74ce76def9/heater_20ml/Heater_Jan_0824_Public/Assembly/Bill%20of%20Materials-Heater%28DEV%29.xlsx), [stirring.py L57-76](https://github.com/Pioreactor/pioreactor/blob/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c/core/pioreactor/background_jobs/stirring.py#L57-L76), [issue 432](https://github.com/Pioreactor/pioreactor/issues/432) |
| Control | Target 500 rpm by default, start at 30 % duty, Kp 0.005 (Ki = Kd = 0). The PID output is *added* to the duty each update, clamped to ±7.5 points, every 23 s. Range 0–2000 rpm; ~125 rpm practical floor | [config L110-113](https://github.com/Pioreactor/pioreactor/blob/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c/packaging/shared-assets/pioreactor/config.example.ini#L110-L113), [stirring.py L286-298](https://github.com/Pioreactor/pioreactor/blob/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c/core/pioreactor/background_jobs/stirring.py#L286-L298) |
| Start and stall | 100 % for 0.5 s at start. At 0 rpm: 0 % for 0.75 s, 100 % for 0.75 s, then min(1.01 × estimate, 60 %) "to avoid the death spiral" | [stirring.py L448-523](https://github.com/Pioreactor/pioreactor/blob/0ae14c035c8a7ae1e52f273872a46ed3fd036b1c/core/pioreactor/background_jobs/stirring.py#L448-L523) |
| Stack | Plastic floor 1.055 mm under the heater board; magnet faces ~1.1 mm below the holder, ~3.9 mm below the Hall, ~6.8 mm plus thermal pad below the vial (estimated from the meshes) | Printables meshes |

Reported problems ([stirring troubleshooting](https://github.com/Pioreactor/docs.pioreactor/blob/6e0778995487c8e9aec60bfac6ea168bef312be4/user-guide/50-Troubleshooting/Stirring%20troubleshooting.md#L10-L75)
and the forum), with what this design does about each:

| Problem | Design response |
|---|---|
| Grinding: the magnets catch on the M3 screws above them | Screw heads ~12 mm outside the magnets' path; stainless screws |
| Random stops at 200–250 rpm; staff suspect magnets too close to the heater board ([789](https://forum.pioreactor.com/t/stirring-randomly-stops/789/4)) | No board or steel over the magnets; spacer discs if needed |
| The magnets pulled the fan base up once spacers were removed ([781](https://forum.pioreactor.com/t/self-test-failure-the-fan-stirring-is-spinning-but-no-rpms-were-measured/781/4)) | Fan screwed to posts |
| RPM reads 0 with the fan spinning: magnets too far from the sensor | Latch beside the carrier, estimated ±19 mT at it against ≤ 9.5 mT to trip |
| A 20 mm bar stalled below 500 rpm, and the PID overreacted to big setpoint drops ([245](https://forum.pioreactor.com/t/stirring-speed-with-different-stir-bar-lost-stirring/245)) | Setpoint ramp in the firmware |
| A bar that wouldn't speed up until the vial was lifted ~6 mm ([262](https://forum.pioreactor.com/t/stirring-calibration-intercept/262)) | Spacer discs under the vial to tune the gap |
| Magnets coming loose ("are the two magnets still present on the fan?") | Pockets plus CA glue |

## Other published fan-and-magnet stirrers

From the Edison survey
([answer](../../outputs/issue-169-magnetic-stirrer/literature_survey_answer.md),
[references](../../outputs/issue-169-magnetic-stirrer/literature_survey_references.md)).
Most papers give few stirrer details; "NR" means not reported.

| Design | Vessel | Drive | Speed and sensing | Notes |
|---|---|---|---|---|
| eVOLVER (Wong 2018, *Nat. Biotechnol.*) | 20–40 mL vials | PC fan + magnets | 0–1500 rpm, software set; no tach reported | Stirring stopped before OD reads |
| Chi.Bio (Steel 2020, *PLOS Biol.*) | 30 mL tube, 12–25 mL | Off-the-shelf fan under a heat plate | Adjustable; rpm NR | ~US$300 per reactor |
| EVE (Gopalakrishnan 2022, *eLife*) | ~12 mL in small vials | Fan + magnets, custom PCB, Pi | ~225 rpm | Printed-holder variation shifted the optics |
| Liu–Yang morbidostat (2016) | Culture vials | Fan, magnet glued to the shaft, PWM at 5 V | PWM | Shaft-to-vial alignment and vial–magnet spacing called critical |
| OptoPACE (Crane 2026) | Turbidostat and lagoon vessels | Two CD-player DC motors + magnets | Arduino PWM through a MOSFET, 5 V rail | Same low-side MOSFET pattern |
| Markovitch 2020 (UPLC vial stirrer) | UPLC vials | DC motor, magnet plate (25 × 8 × 1 mm magnets) | 200–1200 rpm, **closed loop on a magnetic sensor**, 1–2 % of setpoint; error if > 10 % off for 60 s | Field weaker off-centre |
| Lab-in-Syringe (Horstkotte 2020 review) | Syringes | Stacked NdFeB discs on a motor; brushless PC-fan motors preferred for speed stability | Up to 3000 rpm in an opposing-magnet design | Bar tumbling (use short bars or crosses); the bar holding the drive magnets at start-up (accelerate slowly) |
| BrickSDLab (Böser 2025) | 50 mL beaker, 15 mm bar | LEGO NXT motor + LEGO magnet | ≤ 700 rpm, LEGO tacho | No printing at all |
| OpenTCC (Sanchez 2020) | — | Hard-drive BLDC spindles | Arduino | Stirrer details NR |

The coupling query
([answer](../../outputs/issue-169-magnetic-stirrer/literature_coupling_answer.md))
found **no published decoupling speed or torque for a 10–15 mm bar in a 25 mm vial**.
Two of its points shaped the firmware and the risk list:

- A drive-side rpm (tach or Hall on the magnets) does not see the bar slip.
- Ramping avoids the extra torque of sudden acceleration, but it cannot fix a speed the
  coupling can't hold.

Its order-of-magnitude heat check: 1 W fully into 20 mL of water is at most
~0.7 °C/min.

## Lessons that recur

1. **Two magnets, opposite poles up, about one bar length apart** (Pioreactor 9.8 mm for
   12–15 mm bars). The field that turns the bar is horizontal between them.
2. **Keep the gap small, but not tiny:** DIY builds treat the magnet-to-bar distance as
   the main variable, while the Pioreactor forum shows that very close magnets cause
   start-up and stall trouble. Hence the spacer discs.
3. **Measure the drive, then confirm the bar.** Closed loop on the drive (Pioreactor,
   Markovitch) gives repeatable speed. Only watching the bar shows it is coupled.
4. **Start hard, change gently:** a full-power kick to break static friction, then
   ramps (Pioreactor; Lab-in-Syringe's "accelerate slowly").
5. **Centre the drive under the bar.** A misaligned drive makes the bar walk
   (Liu–Yang; De Bruyker in the coupling answer).
6. **Low-side MOSFET PWM from a microcontroller** is the common driver (Pioreactor,
   OptoPACE).

## GitHub and accelerated-discovery.org

*(Pending: a broader search of GitHub projects, accelerated-discovery.org and the
Acceleration Consortium's repositories is still running and will be added here.)*

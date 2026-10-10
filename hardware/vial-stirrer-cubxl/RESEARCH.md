# Open-source magnetic stirrers: what the stirrer design draws on

This is the background for [`README.md`](README.md): what the Pioreactor actually
does, the other published fan-and-magnet stirrers, and what recurs across them.
Gathered on 2026-10-10 from the Pioreactor's repositories, docs, forum and shop, two
Edison literature queries, accelerated-discovery.org, the Acceleration Consortium's
repositories, and a search of GitHub and the open-hardware literature.

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

## accelerated-discovery.org and the Acceleration Consortium

[accelerated-discovery.org](https://accelerated-discovery.org) is a Discourse forum, "a
community for all self-driving lab enthusiasts supported by the Acceleration
Consortium". It is not a hardware catalogue. A search of it for stir, stirrer, magnetic,
mixing, vial, fan, rpm and Pioreactor turned up:

- [t/510](https://accelerated-discovery.org/t/electrode-lifecycle-enhancement-through-computational-testing-and-research-automation/510),
  post 4: a "redesigned … stir plate module (which was developed with assistance from SDL5
  at the AC) to hold six vials". It is probably AC-SDL4's module below (inferred).
- [t/563](https://accelerated-discovery.org/t/engagement-with-industry-vendors/563), post 5:
  "20 mL vials are fairly standard at the Acceleration Consortium", linking the
  Pioreactor's 20 mL vial with a 12 mm bar.

The AC's own stirrers, all fan-and-magnet:

| Repo | What | Drive and control | Notes |
|---|---|---|---|
| [AC-SDL4/Stirring-Module](https://github.com/AC-SDL4/Stirring-Module/blob/5b3d5cd4babe28addfcda56175587d295a80628a/README.md) (no licence) | 6 × 28 mm vials on a 127.5 × 85 mm plate footprint | Six Sunon 25 mm 5 V 2-wire fans in parallel on **one IRLZ44N** with a 1N4001 flyback; Pico, 1 kHz PWM, 60 ms kick; open loop | Fans turn at different speeds; all start only above 45 %; shakes above 92 %; 50 % PEG not possible. Measured from its STL: ~4 mm PLA floor + ~2 mm air (inferred), which may explain the weak coupling. Fusion 360 + STL |
| [opentrons_labware "MatterLab 6 Well Stirrer 20mL"](https://github.com/AccelerationConsortium/opentrons_labware/blob/6c004322715547e7dd6aa92b2138b7137776b218/README.md) (MIT) | 2 × 3 × 20 mL at 35 × 40.5 mm | Mini fans with magnets, on/off; stirrer firmware not published | STL only |
| [photo-reactor "LEDbyXample"](https://github.com/AccelerationConsortium/photo-reactor/blob/460cc342ca0e9b85737ab1c46291fc89a8cf2f1d/README.md) (no licence) | 8 mL vial | 20 mm 5 V tach fan, 2 × 6 × 2 mm magnets on the hub; **closed loop** through an EMC2101 fan controller on a Pico WH, ±1 % duty every 0.2 s | "the fan may not initialize if the stir bar is too close or too far away from the magnets". ~US$83 |
| [lumastir](https://github.com/AccelerationConsortium/lumastir/blob/b6adc4e1a778d681dd7d778fbf65b9ea417258af/README.md) (MIT) | 3 or 6 vials for an Opentrons deck | 30 mm Pi case fans, PCA9685 PWM at 500 Hz, Pi Zero 2W on a battery; open loop | Claim/heartbeat API that auto-stops; "Do not infer successful mixing from an HTTP response" |

None of these closes the loop on a single 20 mL vial, so the Pioreactor stays the closest
match.

## Other open designs worth knowing

| Design | Drive | Speed and sensing | Notes |
|---|---|---|---|
| [eVOLVER hardware](https://github.com/FYNCH-BIO/hardware) ([paper](https://doi.org/10.1038/nbt.4151)) | 40 mm 12 V fan, 2 NdFeB magnets, 28 mm vials | Open loop, ms bursts at 12 V; ~500–1400 rpm by video | Magnets came unglued at constant 12 V and needed a bracer; a jumping bar was fixed by "increasing the space" |
| Chi.Bio ([paper](https://doi.org/10.1371/journal.pbio.3000794)) | PC fan, 2 × N35 Ø9.53 × 3.18 mm, opposite poles up | Open loop, 1.5 s kick | "Non magnetic … spacers … are required" |
| [Markovitch 2020](https://doi.org/10.1038/s42004-020-00427-5) ([files](https://zenodo.org/record/4118046), CC BY 4.0) | DC motor turning one magnet plate under 48 UPLC vials | 200–1200 rpm, magnetic-sensor closed loop, 0.98–0.99 of setpoint by video | Outer positions get a weaker field |
| [rio-controller heating-stirring](https://github.com/wenzel-lab/rio-controller/blob/69cba2a/hardware-modules/heating-stirring/README.md) (CERN-OHL-W-2.0) | 40 mm 3-wire fan, 2 × Ø6 × 2 mm magnets, opposite poles | Tach PI loop on a PIC | Magnets raised 3–4 mm off the hub so the fan still runs |
| [SimonLane/MagStir](https://github.com/SimonLane/MagStir) (MIT / CC BY 4.0) | 30 mm 5 V PWM + tach fan, USB powered | Arduino PID on the tach | Balance the carrier, "otherwise vibration will be a problem" |
| [KopfLab micrologger](https://github.com/KopfLab/micrologger_device) (non-commercial) | Brushless motor | 100-pulse/rev encoder, 50–5000 rpm, ramps 500 rpm/s up | Stops stirring before each read |
| [micworg/stir](https://github.com/micworg/stir) | 80–140 mm 4-wire fans, N52 magnets | Tach loop at 25 kHz; "CATCH" stops and restarts to recapture a thrown bar | Parametric OpenSCAD magnet mount |
| [Ludnie/StirDuino](https://github.com/Ludnie/StirDuino) (GPL-3.0 / CC BY-SA 4.0) | Brushed DC motor, encoder, PID | ≤ 1500 rpm | "Detecting a slipping stir bar" is still on its to-do list |
| [Hoffmann 2017 turbidostat](https://doi.org/10.1371/journal.pone.0181923) | 80 mm fan | Hall sensor (TLE4905L) closed loop | |
| [Dutreuil & Pinheiro 2026, HardwareX](https://doi.org/10.1016/j.ohx.2026.e00816) | 80 mm fan | Open loop | The one dedicated stirrer in HardwareX's 828 titles |

Further papers: [Cook 2022, *Lab Chip*](https://doi.org/10.1039/d1lc01081f) ("when the
distance … was equal to the length of the stirrer, the impeller rotation was stable");
[Omari 2021, *Chemistry–Methods*](https://doi.org/10.1002/cmtd.202000066) (fixed vial
placement roughly halves variability); [Cherepanova 2025, *JACS Au*](https://doi.org/10.1021/jacsau.5c00412)
(off-centre bars tilt, rub the wall and crack vials); [Baldwin 2018, *PRL*](https://doi.org/10.1103/PhysRevLett.121.064502)
(why bars jump). No Digital Discovery paper describes a stirrer, and
[Science Jubilee](https://doi.org/10.1039/D3DD00033H) has no stirrer tool.

**Coil drives are patented in one form.** Four coils per vial with diagonal pairs in
series, each pair one phase of a stepper driver, is GE's
[US8398297](https://patents.google.com/patent/US8398297B2/en), which Google Patents lists
as active until 2031-07-12. That is option B in
[`vial-mixing.md`](../../cubos/docs/vial-mixing.md). Its claim 1 also needs steel pole
pieces and adjacent coil groups. Check before building it beyond research; this is not
legal advice.

## More lessons from the wider survey

- **The gap is a window, not just "as small as possible".** Pioreactor moved its magnets
  closer for stronger agitation, then fixed a stall by backing off ~1 mm. eVOLVER fixed a
  jumping bar by adding space. LEDbyXample's fan won't start if the bar is too close or
  too far. No source gives an optimum in mm, so this design makes the gap adjustable.
- **The magnet spacing should be about the bar length** (Cook 2022; gharris012's
  StirPlate parameter "stirBarLength" is literally the magnet spacing). The 9.8 mm here
  suits the 12 mm bar best; for the 15 mm bar, `MAG_CC = 12` is worth a try.
- **Every DIY sensor sees the drive, not the bar.** Only a coil drive's Hall sensors see
  the bar itself. Watch the bar when commissioning.
- **Have a stop that doesn't depend on the software.** Lumastir's docs warn that a
  software timer is no guarantee. Here the gate pull-down turns the fan off whenever the
  XIAO resets or loses USB power, and the firmware runs a watchdog.
- **Stop before measuring.** Chi.Bio settles for 5–10 s, eVOLVER ~20 s, and KopfLab stops
  before each read.

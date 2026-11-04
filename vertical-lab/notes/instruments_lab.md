## Lab equipment, round 4: corrosion on the CubXL, DED, packaging, and a HIP

Four more models in [`instruments_lab.py`](../instruments_lab.py), each an `Instrument` that `tour.py` loads and plays.

| Model | What the animation shows | GIF, MP4 | Size W × D × H (mm), published | Where |
|---|---|---|---|---|
| CubXL set up for corrosion spots, with a NuVant EZstat Pro | The P20 takes a tip and fills well S1 with 150 µL of 0.6 M NaCl; the capper carries the electrode cap from its park cup to S1; the potentiostat runs OCP, then a cyclic polarization, drawn as an overlay (illustrative); the cap is rinsed and parked; the well's liquid goes to a tube for ICP; on to S2 | [GIF](../out/instruments/cubxl_corrosion.gif), [MP4](../out/mp4/instruments/cubxl_corrosion.mp4) | CubXL 740 × 605 × 488 (#199's model); EZstat Pro 255 × 245 × 102 | tray A |
| DED, powder-fed laser: InssTek MX-Lab | The door swings open; a substrate goes from the shelf to the worktable; argon purge (O2 readout); the head builds a six-spoke "wagon wheel", each spoke a different blend, bead segments rising as the nozzle passes; the door opens | [GIF](../out/instruments/ded.gif), [MP4](../out/mp4/instruments/ded.mp4) | 680 × 684 × 835 (machine); base cabinet estimated | on the floor, beside the VLM |
| Packaging station: Primera AP380 + LX500c, Zebra ZD621t, Uline H-190 | A jar into the nest; the LX500c prints its label; the AP380 wraps it on; the jar is bagged and the H-190 seals the bag; into the foam insert; lid on; the ZD621t's 4 × 6 in label onto the lid. Insets show the jar label and what the box must carry | [GIF](../out/instruments/packaging.gif), [MP4](../out/mp4/instruments/packaging.mp4) | each piece published (below); about 1990 × 650 × 229 as laid out here | a tray (fits) |
| HIP against a tray: Kobelco O2-Dr.HIP | The tray and its 727.5 mm product height; the HIP lowered onto it; the parts that don't fit, in red; see-through to the vessel; the verdict | [GIF](../out/instruments/hip.gif), [MP4](../out/mp4/instruments/hip.mp4), [still](../out/instruments/hip.png) | 1315 × 1100 × 1300, 1100 kg | does not fit a tray |

Clip lengths at 1280 × 720, 15 fps: the CubXL 34.6 s (MP4 2.3 MB, GIF 3.6 MB), DED 24.2 s (1.3 MB, 1.5 MB),
packaging 28.1 s (1.4 MB, 2.0 MB), HIP 17.9 s (0.7 MB, 0.9 MB). Each has a hero still,
`out/instruments/<key>.png`, and `out/instruments/<key>.json` with the frame range of every step.

### The CubXL, set up for corrosion spots

- **The plan is DAL's, not built.** The deck, the electrode cap and the head follow DAL PR #180
  (`alloy-corrosion/cubxl-setup.md`, branch `claude/issue-213-20261013-2132`), in the CubOS deck frame of Ben's
  2026-10-02 calibration. DAL says every coordinate is "a proposal to be re-jogged, not a measurement", and nothing
  has been printed, wired or run.
- **What is on the deck.**
  - A coupon tray at the back with four stations, S1-S4, 25 mm apart. Each polished piece sits face up on a pogo pin
    that touches its bare back, the working-electrode contact. A lid presses an FKM O-ring (AS568-006) onto its face:
    a 3 mm well, 0.071 cm², with an 8 mm bore above it for about 150 µL.
  - NaCl stocks of 0.6, 0.06 and 0.006 M and DI water, in capped 20 mL vials; a rinse cup and a park cup; a 2 × 8
    rack of open 0.5 mL tubes for ICP; two 30-tip racks; a tip waste.
- **The electrode cap.** 20 mm across, 16 mm tall. A leak-free 2 mm Ag/AgCl reference runs down the middle inside
  five turns of 0.25 mm Pt wire, the counter. A steel disc on top takes the capper's 50 N magnet. Two pogo pins at
  ±11 mm land on reference and counter pads beside each station.
  - The capper moves it as it moves vial caps, so the head is free during a measurement. Only one reference and one
    counter are needed.
- **The head.** Capper at (0, 0), P20 at (+55, +11), camera at (−40, +10). Travel at carriage height 122 mm; setting
  the cap at 58.
  - #199's CubXL model has the pipette 105 mm to the left of the capper. Here the head is rebuilt to DAL's offsets.
  - Frame, gantry and carriage are #199's parts, split the way `animate.py` splits them.
- **One spot**, from DAL's `protocol.md`:
  - fill 150 µL;
  - OCP for 30 min;
  - LPR, ±10 mV about OCP at 0.167 mV/s;
  - rest 5 min;
  - cyclic polarization from 50 mV below OCP, at 0.167 mV/s (ASTM G61's 0.6 V/h) or 1 mV/s for screening,
    reversing at 1 mA/cm²;
  - collect the liquid and one 150 µL rinse into a tube for ICP.

  That is 44 min a spot at 1 mV/s and 107 min at the G61 rate. Eight spots make a tray load.
- **The potentiostat is the one the lab has now**: NuVant's EZstat Pro, lent by Dr. Porter (byu-vcl #231, DAL #221).
  - 10 × 9.625 × 4 in (255 × 245 × 102 mm), 2.8 kg, ±1 A, ±25 V compliance, a 5-lead cell cable (nuvant.com).
  - It runs from NuVant's EZware on a Windows 7 PC that is cabled to the CubXL's Pi. The PC is not drawn.
  - DAL's plan sized the bus for an EmStat Pico in a small box behind the deck. The EZstat is 255 mm wide, so here
    it stands beside the frame, with its cable over the back cross member to the tray's back edge.
  - The box is plain grey at the published size. Its front panel isn't modelled.
- **The curve is illustrative, and labelled so on screen.** No corrosion spot has been run yet. The EZstat passed
  its first dummy-cell check, C1, on 2026-10-26 (byu-vcl #291, via DAL #221).
  - E_corr −0.81 V vs SCE and i_corr 3.39 × 10⁻⁷ A/cm² are the published values DAL's README quotes for as-built LPBF
    AlSi10Mg in aerated 3.5 wt% NaCl (Wu et al. 2022, doi:10.3390/ma15248786).
  - The passive current (1.5 µA/cm²), E_pit (−0.705 V), E_rp (−0.775 V) and the Tafel slopes are made up for the
    drawing.
  - The forward scan reverses at 1 mA/cm², as DAL's protocol says.
- **The powder doser has no part in it** (DAL #222; `cubxl-setup.md` §8). The corrosion tests use polished metal
  and liquid electrolyte.

### DED: why the InssTek MX-Lab

DAL's own plan buys DED time in two steps (PR #117, the ONR FY27 YIP proposal: "single-stream, blown-powder laser DED
is not available at BYU"):
- **first the MX-Lab** in Prof. Zak Fang's lab at the University of Utah, about 0.5 kg of powder a deposit;
- **then the FormAlloy X2** at Mines, with at least 2 kg a powder.

PR #220's 630 bronze plan sieves into the X2's cuts, 45-105 and 100-200 µm. DAL infers that Utah's machine is an
MX-Lab from its six hoppers; that is to be confirmed with Prof. Fang.

| | InssTek MX-Lab | FormAlloy X2 (Mines) | FormAlloy L2 (L221 was the first L-series) |
|---|---|---|---|
| Size | 680 × 684 × 835 mm without accessories (Technical Data Rev.3, 2020) | not published | not published |
| Mass | 250 kg | not published | not published |
| Build | 150 × 150 × 150 mm stroke; 175 × 175 mm table | 250 × 250 × 300 mm (Mines ADAPT) | 250 × 250 × 300 mm (JHU) |
| Laser | Yb fibre, 300 W (2020) to 500 W (2024 brochure) | 1 kW (Mines); Cornell's unit, 500 W | 1 kW IR (JHU); the L221 in HT-READ, 150 W blue |
| Feeders | up to 6 hoppers of about 0.42 L, fed together to mix in the melt pool | 4 feeders (Mines); Cornell's unit, 2 | two hoppers plus the 16-vial Alloy Development Feeder |
| Small batches | 0.03-2 g/min; batch size not published | at least 2 kg a powder (Mines, by e-mail in PR #117) | grams per ADF vial not published |
| Atmosphere | option: Ar > 99.999 %, O2 ≤ 50 ppm | not stated | < 100 ppm O2 and moisture (JHU) |

- **The MX-Lab is the only one of the three with a published size and mass.** It is also the small-batch,
  multi-hopper machine, and the first step in DAL's plan. So that is what is modelled.
- **The HT-READ feeder doesn't blend.** Vecchio et al.'s Alloy Development Feeder holds 16 vials of pre-mixed powder
  and feeds one at a time. It switches compositions; it does not mix them in the melt pool.
- **The model.**
  - Matte black, from InssTek's and Chalmers' photos.
  - The door hinges on the left and has a dark laser-filter window and an orange gasket.
  - The touchscreen, E-stop and buttons are above a seam a little over half height.
  - The worktable is perforated, and six orange powder lines run to a coaxial nozzle.
- **The base cabinet is an estimate.** Its size isn't published: about 900 mm wide and 1000 mm tall, scaled from the
  Chalmers photo against the published 680 mm width.
- **Illustrative parts.**
  - The six spokes' colours, copper to a pale alloy grey, stand for blends and are not compositions.
  - The O2 readout runs from 20.9 % to 50 ppm on a log scale; how long the purge takes is not published.
  - Which axes move the head or the table isn't published. Here the head moves.
- **The MX-Lab stands on the floor.** At 680 × 684 × 835 mm and 250 kg without its base it would fit a strong tray's
  load, but not the 727.5 mm height, and it needs argon. Like the wire EDM, it goes beside the VLM (`floor=True`).

### The packaging station

- **Every piece is a real benchtop product at its published size.**

  | Piece | Size W × D × H (mm), mass | Source |
  |---|---|---|
  | Primera AP380 wrap-around label applicator; takes containers 15-170 mm across | 340 × 508 × 226, 9.07 kg | primera.com |
  | Primera LX500c colour label printer; print width 19-108 mm | 264 × 389 × 180 closed, 3.2 kg | primera.com |
  | Zebra ZD621t, 4 in thermal transfer; 104 mm print width at 203 dpi | 202 × 267 × 192, 2.5 kg | Zebra spec sheet, via a distributor; Zebra's own site refused the runner |
  | Uline H-190 12 in impulse sealer; seals up to 8 mil poly | 452 × 84 × 188, 4.2 kg | uline.com |
  | Nalgene 2104-0008 250 mL wide-mouth HDPE jar | 61 across × 131 tall | thermofisher.com |
  | Uline S-23611 pick-and-pack foam shipper, charcoal foam | 324 × 311 × 108 | uline.com |
  | Uline S-6802 4 × 6 in labels | 102 × 152 | uline.com |

  The jar nest and the bag stand are fixtures drawn here; their sizes are layout choices.
- **It fits a tray.** Laid out in a line, with the foot switch and the bag stand in front, it is about 1990 × 650 mm
  and 229 mm tall. The LX500c's lid stands 442 mm open.
- **Print and apply are two steps, not one.** The AP380 takes labels die-cut with the waste removed, on a roll.
  Primera sells no print-and-apply bundle, and labels die-cut digitally on the LX610 are not compatible. So the
  LX500c prints a batch's labels, the roll is rewound, and the AP380 applies them one per jar.
- **The label insets are examples.**
  - The jar label's fields (sample ID, alloy, mass, date, lab) follow DAL's powder SOP (PR #187): "Label container
    with mixture composition and date".
  - The QR code is real and holds the label's text, one line each (the `qrcode` package, version 5, error
    correction L, 37 × 37 modules; 3 px a module at 720p). zbar and OpenCV both read it back from the rendered
    MP4's frames, and zbar from the GIF's too. Until round 5 it was a placeholder pattern.
  - The shipping label's addresses are placeholders.
- **Dangerous goods: a test decides, not the alloy's name** (49 CFR 172.101; 173.124-125).

  | Powder | Entry | Class |
  |---|---|---|
  | Aluminium powder, coated | UN1309 | 4.1 |
  | Aluminium powder, uncoated | UN1396 | 4.3 |
  | Aluminium silicon powder, uncoated | UN1398 | 4.3 |
  | Magnesium powder or magnesium alloys powder | UN1418 | 4.3 |
  | Copper, bronze, iron, stainless steel | no named entry | regulated only if a UN test puts them in a class |

  - A powder is out of Division 4.1 if UN test N.1 shows it doesn't burn along its length within 10 minutes. It is
    out of Division 4.3 if test N.5 shows it gives off no more than 1 L of gas per kg per hour.
  - Supplier SDSs for AlSi10Mg disagree. Renishaw's (20-63 µm) says "Not dangerous goods according to ADR, IATA and
    IMDG". The Heeger SDS in byu-vcl's root carries H228 and H261, yet says "UN Number Not applicable".
  - The lab's one shipment so far: DAL's `alloy-workflow-review.md` says the 2026-02-18 package to Amazemet (Poland)
    went via the BYU Post Office, and "Materials were confirmed non-hazardous per IATA by MSE Supplies". The file
    doesn't say what that rested on, or whether it covered the silicon powder and aluminium wire in the mixtures.
- **What the box carries.**
  - **Not dangerous goods:** no DG marks or labels, and "Not Restricted" on the air waybill (IATA DGR 8.2.6).
  - **Regulated, e.g. untested Al powder, coated:** "UN1309, Aluminium powder, coated", the Class 4.1 FLAMMABLE SOLID
    label, and the shipper's and consignee's addresses (172.301).
  - Limited quantities by ground (up to 1 kg inner packagings for 4.1 PG II) take the limited-quantity mark instead.
  - USPS takes no flammable solid abroad (Publication 52, 344.2). A regulated powder can't go to Poland through the
    BYU Post Office.
  - Not checked: the IATA DGR text itself (paywalled), UN packaging marks and the Shipper's Declaration.

### Could a HIP fit on the VLM? No.

- **The smallest 200 MPa lab HIP with a published size is Kobelco's O2-Dr.HIP.** 1315 × 1100 × 1300 mm, 1100 kg,
  200 MPa, up to 2000 °C with a graphite heater, hot zone up to 75 × 100 mm (kobelco.co.jp, Dr. HIP page).

  | | O2-Dr.HIP | Tray limit | Result |
  |---|---|---|---|
  | Height | 1300 mm | 727.5 mm through the opening | 572.5 mm over, 1.79 times |
  | Depth | 1100 mm | 864 mm tray, about 840 inside the rim | 236 mm deeper than the tray |
  | Mass | 1100 kg | 228 / 360 / 490 kg | 4.8 / 3.1 / 2.2 times |
  | Services | argon, cooling water, compressed air | power, in a slot and at the opening only | |

  Its 1100 mm depth is 260 mm more than the tray's inside, 840 mm; turned 90°, its 1315 mm side is 475 mm more. At
  the opening it is 456 mm taller than the 844 mm under the header.
- **The others are bigger, or publish nothing.**
  - AIP6-30H (30,000 psi; hot zone 75 × 125 mm): no size or mass published.
  - EPSI's and Hiperbaric's smallest units: no size or mass published.
  - Quintus' smallest current compact unit, the QIH 15L: 4.2 × 3.0 × 3.4 m and 8 t. A "QIH 3" was not found.
  - MTI's CM-HIP-2: 1200 × 630 × 1425 mm and 250 kg, but a 20 MPa furnace, a tenth of HIP pressure. It is still
    698 mm too tall.
- **Safety.**
  - **Stored energy.** Ideal-gas argon at 200 MPa, expanding isentropically (NIST NCNR's stored-energy method, k = 5/3),
    holds about 0.29 MJ per litre. The 75 × 100 mm hot zone alone, 0.44 L, is about 0.13 MJ. That is a lower bound:
    the vessel's free volume isn't published, and argon is far from ideal at 200 MPa.
  - **Vessel codes.** ASME VIII Div. 2/3 or PED vessels; wire-wound vessels are designed to leak before they burst.
  - **The room.** Oxygen sensors for the argon, cooling water, a gas exhaust and pressurized air, all on the floor.
  - **Cooling.** Hiperbaric runs its cooling on an independent supply so it never stops. A tray loses power in transit.
  - **Moving platforms.** Nothing published covers a HIP on one.
- **So a HIP stands beside the VLM, like the wire EDM,** with its gas, water and compressor, and the arm brings it
  work.
- **In the model.** The vessel and its frame inside are drawn schematically from Kobelco's cutaway, since their sizes
  aren't published. The HIP is set 130 mm back on the tray rather than centred: centred, its front would stand
  through the opening's header, which is only 20-80 mm in front of the tray. So the whole 236 mm it is deeper than
  the tray overhangs the back, and the red box there shows it. The tray, its 727.5 mm envelope and the opening's posts and header are drawn to Kardex's figures
  (#53, the order sheet).

### How these four are animated

`instruments.Joint` moves a piece between two values per action. These clips need more than that, so the module adds
two things and keeps them local:

- **A shared timeline.**
  - `Track` and `Turn` are joints whose translation or angle follows knots on one timeline.
  - The CubXL's gantry, carriage and head, the electrode cap, the tips and the liquid levels all share one timeline.
    So does the packaging jar's position, tilt and spin, and the DED head with its 72 bead segments.
  - One action can then carry the head through several waypoints and pick up or set down what it carries on the way.
- **The camera moves, the per-view labels and the plots go through `tour.tour_one` (round 5's fixes).** Each
  instrument sets `Instrument.cams` (a view per action), `Instrument.step_labels` (that view's leader labels, from
  its action on) and `Instrument.overlay` (the live plot or inset, drawn over every frame through `Scene.overlays`).
  Until round 5 this module wrapped `scene.Scene.step` and `.overlay` on import, keyed on the scene's name. The four
  clips render pixel-identical either way.
- **Render on a display number of your own.** Two renders here failed with "bad X server connection" on a display
  number that had just been released. `xvfb-run --server-num=152` worked.

```bash
LP_NUM_THREADS=2 xvfb-run --server-num=152 -s "-screen 0 1280x720x24" python3 tour.py cubxl_corrosion ded packaging hip
```

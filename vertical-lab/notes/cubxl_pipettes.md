# The CubXL's pipettes, water and sulfide lost from the well, and a sturdier reference electrode

Asked for on [PR #318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318#issuecomment-7046840630) (Sterling,
2026-11-20), handed off as [#365](https://github.com/vertical-cloud-lab/byu-vcl/issues/365):

> "For the CubXL, would it make sense to put both a P20 and a P300 onboard? It seems like there are a lot of small
> transfers to fill things up, and I worry a bit about evaporation (you could run some basic calculations related to
> that?). Maybe it's fine though. Or maybe an Opentrons Flex pipette (5-1000 uL)."
>
> "We should also probably use something more robust than the Ag/AgCl reference electrode (and there are probably
> some that require far less maintenance)"

The CubXL on tray A runs DAL's copper corrosion screen
([digital-alloy-lab PR #180](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/180), its branch at
[`633995b`](https://github.com/vertical-cloud-lab/digital-alloy-lab/tree/633995b/alloy-corrosion)), drawn in
[`cubxl_corrosion.md`](cubxl_corrosion.md). Code for this note: [`cubxl_evap.py`](../cubxl_evap.py) →
[`out/cubxl_evap.json`](../out/cubxl_evap.json), [`out/cubxl_evap.png`](../out/cubxl_evap.png).

SECTION_SUMMARY

## 1. The pipettes: add a P300 beside the P20; not a Flex, not yet

### What the P20 moves now

DAL's plan ([`protocol.md` §3-4](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/633995b/alloy-corrosion/copper/protocol.md)),
for a main spot at 1 mg/L S, with the CubXL's P20 single GEN2 (1-20 µL) only:

| Per spot | Volume | P20 transfers |
|---|---|---|
| ASW into the well, dispensed from above the meniscus | 135 µL | 7 × 19.3 µL |
| The 10 mg/L sulfide stock, last, same tip | 15 µL | 1 |
| The well's liquid to its 0.5 mL tube (a new tip) | 150 µL | 8 × 18.75 µL |
| DI water into the emptied well, for the rinse (a third tip: the collection tip has touched well liquid, so DAL's tip rule keeps it out of the DI vial) | 150 µL | 8 × 18.75 µL |
| The rinse to the tube | 150 µL | 8 × 18.75 µL |
| 1 M HNO₃ into the tube (the night's one acid tip) | 20 µL | 1 |
| **Total** | | **33** |

DAL counts 25 (8 + 16 + 1); how the rinse water gets into the well isn't written down (noted in
[`cubxl_corrosion.md`](cubxl_corrosion.md)), and drawing it with a clean tip adds 8.

### The three options

Accuracy is Opentrons' published systematic error (± %) and CV at each volume, interpolated on log volume between
its points ([GEN2 white paper](https://insights.opentrons.com/hubfs/Products/Pipettes/GEN2%20Pipette%20White%20Paper.pdf),
Table 1; Flex: [Pipette Accuracy data sheet](https://insights.opentrons.com/hubfs/Products/Pipettes/Tech%20Data%20Sheet_Pipette%20Accuracy.pdf),
May 2026). A series of n equal transfers keeps the systematic % and divides the CV by √n. Head time is
[`cubxl_evap.py`](../cubxl_evap.py)'s plan of moves, timed with the CubXL's own measured steps (§2, "How it is
computed").

| | **P20 only (now)** | **P20 + P300** (two OT-2 GEN2 singles) | **One Flex 1-Channel 1000 µL** |
|---|---|---|---|
| Range | 1-20 µL | 1-20 and 20-300 µL | 5-1000 µL, on 50, 200 or 1000 µL tips |
| 135 µL of ASW | 7 × 19.3: ±1.5 %, CV 0.3 % | P300, 1 × 135: ±1.2 %, CV 0.5 % | 200 µL tip: not specified below 200 µL (±0.5 %, 0.15 % at 200); 50 µL tip, 3 × 45: ±0.7 %, 0.2 % |
| 15 µL of sulfide stock | ±1.7 %, CV 0.9 % | the P20: the same | 50 µL tip: ±2.9 %, CV 1.5 % |
| 150 µL to the tube | 8 × 18.75: ±1.6 %, CV 0.3 % | P300: ±1.0 %, CV 0.4 % | not specified (200 µL tip) |
| 20 µL of acid | ±1.5 %, CV 0.8 % | the P20: the same (the P300 at its 20 µL floor: ±4 %, 2.5 %) | 50 µL tip: ±2.3 %, CV 1.2 % |
| Transfers a spot | 33 | 6 | 6 |
| Head time a spot | **22.5 min**: fill 6.0, collect and rinse 15.2, acid 1.3 | **7.5 min**: 3.1, 3.2, 1.3 | 7.2 min |
| The well open before the cap goes on | 9 min | 6 min | 6 min |
| Mixes the 150 µL well after the sulfide? | barely: 20 µL strokes stir the top | yes, with the P300 | yes |
| New tips a spot | 3 | 4 (2 if the ASW and DI tips, which only ever touch their own stock, are kept for the night as DAL keeps the acid tip) | 3 |
| Size | 44.5 × 32.3 mm, 330.5 mm long | a second body the same size, 311.5 mm long | 64 × 50 mm, 374.5 mm long, 2.5 kg (Opentrons' sheet; may include packing) |
| On the head | as now, on Ben's PAW-V2 mount at (+55, +11) from the capper | a second bracket beside the P20 (34 mm apart, as an OT-2's two mounts are) and **20 mm higher**: its tip then hangs 51.1 mm below the nozzle against the P20's 30.95 (tips 59.3 and 39.2 mm long, 8.2 and 8.25 mm on the nozzle), so both tip ends sit at the same height on the CubXL's one Z axis | an adapter plate for its two captive 2.5 mm screws and the contact pins on its back (the connector isn't published); 200 µL tips hang 48.6 mm |
| Driven by CubOS? | yes: the PANDA Arduino and a TMC2209 drive the pipette's bare stepper and limit switch over its 10-pin ribbon ([`opentrons-pipette-wiring.md`](../../cubos/docs/opentrons-pipette-wiring.md)) | **yes, the same way.** The PANDA firmware's stock constants *are* a P300 GEN2's (300 µL, `UL_TO_MM` 0.1098, the one constant upstream calibrated: [`cubos/firmware/README.md`](../../cubos/firmware/README.md)), and CubOS already has a `p300_single_gen2` model. Simplest: a second Uno + TMC2209 on its own `/dev/serial/by-id` port with Opentrons' P300 planes (bottom −14.5, blowout −19, drop-tip −37 mm; 9.18 µL/mm; 1.25 A to drop a tip) | **no, not without a project.** It is a smart device: STM32 with its own driver, pressure, capacitive and tip-presence sensors, on CAN FD at 500 kbit/s and 36 V. Opentrons' firmware and host code are open (Apache-2.0, `ot3-firmware`, `opentrons-hardware`), but no one has published running a Flex pipette off a Flex |
| Cost | owned | **$2,950** (999-00003) + about $40 (Uno, driver board) | $3,600 (999-00187) + a CAN FD adapter and a 36 V supply + the development |
| Tips | $8.50 a rack of 96 (20 µL) | 300 µL tips $8.50 a rack, in a rack of their own on the deck | $16 a rack (Flex tips) |

Prices from opentrons.com, read 2026-11-20. The $1,250 in [`docs/pipette-selection-cubxl.md`](../../docs/pipette-selection-cubxl.md)
is the 2023 price; the 2024 list had $2,250.

### What the P300 buys, and what it doesn't

- **Head time, 22.5 → 7.5 min a spot.** DAL's night is set by the measurement (52 min a spot), and the head already
  collects spot k−1 while spot k is measured, so most of the saving is slack. What comes off the night is the fill
  (6.0 → 3.1 min a spot, about 25 min over 8 spots). It also takes 27 transfers a spot, about 200 a night, off the
  P20's plunger and the gantry.
- **Accuracy: a wash.** Every option is within ±1-3 % at these volumes. The P20 is the right tool for the 15 µL of
  sulfide and the 20 µL of acid; the P300's single 135 µL is a little better than seven P20 draws in systematic
  error and a little worse in scatter.
- **Evaporation: not a reason** (§2: 0.3-0.5 µL a spot, against 2-3.5 µL lost under the cap).
- **Mixing: the reason that matters.** §2 shows the sulfide added last needs mixing, and a P20 can't mix 150 µL.
- **One caution for every option: dispensing from above the meniscus.** Opentrons' figures are for dispensing into a
  vessel. A drop leaves a tip only when it outweighs the surface tension holding it (Tate's law): about 12 µL on a 20
  µL tip's 0.9 mm end, so a 19.3 µL dispense from above can leave part of a drop on the tip, and the blow-out may or
  may not shake it off. Touching off on the bore's wall above the meniscus settles it; a gravimetric check of the
  CubXL's own dispense move (into a weighed well) should come first, with any pipette.

**Recommendation: keep the P20 and add an OT-2 GEN2 P300 single beside it.** The P300 takes the ASW, the collection,
the rinse and the mixing; the P20 keeps the sulfide and the acid. It is the same pipette family, tips, wiring and
firmware the CubXL already runs, so the risk is mechanical: the bracket, and checking every move for the second
tool's shadow, as DAL's deck check does for the capper.

**Not the Flex 1-Channel 1000, for now.** It costs only $650 more than a P300 and its pressure and tip-presence
sensing would be welcome on an unattended night, but nobody has driven one off a Flex, it is 2.5 kg and 374.5 mm
long on a head built for a P20, and at 15 µL it is less accurate than the P20 it would replace. Revisit it if the
CubXL ever needs millilitre transfers, or once someone publishes a Flex pipette on a third-party gantry.

## 2. Evaporation, and what really moves the sulfide

![Water and sulfide lost from the well](../out/cubxl_evap.png)

### How it is computed

[`cubxl_evap.py`](../cubxl_evap.py) extends DAL's own cap check
([`copper/cad/cad_check.py`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/633995b/alloy-corrosion/copper/cad/cad_check.py),
which gives the 1.6 µL/h under the cap and 6.1 µL/h with no cap that the protocol quotes). The model and its inputs:

- **Water vapour diffuses** from the liquid surface up the still air in the well's bore, then out: through the open
  mouth (an end correction of 0.8 r into still air), through the clearance cap's 0.12 mm skirt gap over its 3.2 mm
  land, or through the O-ring cap's 0.3 mm vent (DAL's fallback `electrode_cap_oring`; the vent's length, 6 mm, is
  assumed). Geometry from DAL's `cad_parts.json`: an 8 mm bore to 10 mm above the metal, 150 µL standing 4.4 mm.
- **Seawater** evaporates 1.9 % slower than pure water (water activity 0.981). Saturated vapour 19.4 g/m³ at 22 °C,
  D = 0.25 cm²/s (Massman 1998), as DAL uses.
- **The VLM's airflow.** [`services.md`](services.md) sizes the VLM's ventilation at 1100-2200 m³/h for a 5-10 K rise;
  over the enclosure's 2.83 × 3.12 m plan that is **0.035-0.069 m/s** on average. Moving air thins the boundary layer
  over a mouth (laminar flat plate, 0.664 Re^½ Sc^⅓, blended with still-air diffusion). 0.3 m/s stands for a spot near
  an inlet. The air in the bore below the mouth is taken as still; the bound with the bore swept clean is in the JSON
  (`open_well_bore_flushed_bound`) and is 2.8-6 times higher.
- **Conditions.** The room at 22 °C and 40 % RH (DAL's), a dry Provo winter at 20 % RH, 60 % RH, and the inside of
  the ventilated VLM: 5 K over the room (its design rise), so room air at 40 % RH is 30 % in there.
- **The fill's timing** comes from the head-time model of §1: step times measured on the CubXL itself
  ([`pipette_test_20261007`](../../cubos/results/pipette_test_20261007/SUMMARY.md): aspirate 12.8 s, dispense 7.2 s,
  a 33 mm move 5.0 s at F3000, decap 7.3 s, cap 7.0 s, tip pickup 8.4 s, drop 12.8 s).

### The well: 1-3 % of its water per spot

| Water lost from the 150 µL well in one spot | 22 °C, 40 % RH, still | 22 °C, 20 % RH | VLM: 27 °C, 30 % RH, 0.07 m/s |
|---|---|---|---|
| Fill, P20 (8 transfers, 6.0 min) | 0.44 µL | 0.59 µL | 0.78 µL |
| Fill, P300 or Flex (2 transfers, 2.7-3.1 min) | 0.14 µL | 0.19 µL | 0.26 µL |
| Leak check and cap going on (3 min open) | 0.29 µL | 0.39 µL | 0.53 µL |
| 52 min of electrochemistry under the clearance cap | 1.34 µL | 1.81 µL | 2.15 µL |
| **Whole spot, P20 only** | **2.07 µL (1.4 %)** | **2.79 µL (1.9 %)** | **3.46 µL (2.3 %)** |
| Whole spot, P20 + P300 | 1.78 µL (1.2 %) | 2.39 µL (1.6 %) | 2.94 µL (2.0 %) |
| Whole spot, P20 only, O-ring cap with its 0.3 mm vent | 0.74 µL (0.5 %) | 0.99 µL (0.7 %) | 1.32 µL (0.9 %) |

- **Chloride rises by the same fraction:** 0.55 M becomes 0.557-0.563 M by the end of a spot. That is within the
  batch-to-batch spread of a made-up ASW and small against what the protocol varies.
- **The many small transfers cost 0.3-0.5 µL** (0.2-0.35 % of the well) against one big transfer: the well is open
  for a few minutes either way, and 65 % of the loss happens under the cap during the measurement. **Evaporation is
  not a reason to change the pipette.**
- **Under the cap the airflow hardly matters** (1.55 → 2.48 µL/h in the VLM case, mostly from the 5 K warmer air):
  the 0.12 mm gap is the bottleneck. With no cap at all the VLM's air would matter more: 5.8 → 10.5 µL/h at 0.07 m/s
  and 27 °C, and up to 39 µL/h if the moving air swept the bore (an upper bound).
- **The tip** carries 19.3 µL for about 8 s with a 0.6 mm opening: a few nanolitres. Its known effect is inside the
  tip: at low RH the first aspiration of a fresh tip under-delivers until the air cushion is saturated, which ISO
  8655 handles by pre-wetting. Seven transfers with one tip pre-wet themselves after the first.

### The open ICP-MS tubes: the biggest water loss on the deck

Each spot's 320 µL waits in an open 0.5 mL polypropylene tube until a person caps the rack in the morning (DAL,
`cubxl-setup.md` §5). The meniscus is 13 mm below the rim (`instruments_lab.tube_level`): **2.1 µL/h** at 22 °C and
40 % RH, **3.6 µL/h** inside the VLM. Over an 8-spot night, with the tubes capped 3 h after the last spot, the tubes
lose **2-7 %** of their liquid at 40 % RH and **3-12 %** inside the VLM (figure, panel b). Every element in a tube
reads high by that much if its concentration is multiplied by the nominal 320 µL.

DAL already weighs each tube in the morning (`protocol.md` §4, step 11: "recovered mass within *choose* % of what was
dispensed"). **Use the morning mass, not 320 µL, to turn ICP-MS concentrations into micrograms, and expect that check
to read low by the evaporation, not by a pipetting loss.** Cheaper still: a loose printed lid over the tube rack, as
the electrode cap does for the well, cuts it about fourfold.

### Stock vials and cups

| | 22 °C, 40 % RH | VLM case |
|---|---|---|
| A 20 mL stock vial with its cap off | 10 µL/h | 19 µL/h |
| ASW, open about 5 min a spot (P20), 8 spots | 7 µL a night, 0.04 % of 18 mL | 13 µL, 0.07 % |
| A capped stock, PDMS cap sealing (water through 2 mm of PDMS, assumed 36,000 Barrer) | 2.9 µL/day: 0.3 % in 3 weeks | 4.6 µL/day: 0.5 % |
| A capped stock, if the cap leaves a 50 µm gap round the rim | 28 µL/day: **3.3 % in 3 weeks** | 45 µL/day: **5.3 %** |
| A 4 mL rinse cup, open all night | 6.9 µL/h: 0.08 mL a night | 12.5 µL/h |

- **Opening a stock for transfers costs nothing that matters.** What matters is whether the capper's printed caps
  seal when they sit on the vial. Ben's caps are press-fit PLA filled with PDMS (`modules/electromagnetic-capper`);
  DAL's cap check describes them as "resting almost free". A stock is meant to last weeks (`cubxl-setup.md` §5), so a
  leaky cap would walk the ASW's chloride up by 3-5 % over its life. **Weigh each stock vial when it is filled and
  each week**; refill at a 1 % loss.
- **The sulfide stocks lose sulfide, not water, each time they open.** The headspace's H₂S goes and the surface loses
  more while the cap is off: **0.47 % of the stock's sulfide per single draw**, 1.5 % for the eight P20 draws of a
  well made of stock alone (the 0.1 and 10 mg/L targets) against 0.46 % for one P300 draw. Over a night of sulfide
  spots that is a few percent, consistent with DAL's plan to make the sulfide stocks fresh each night and to measure
  them at the start and end.

### Sulfide in the well: H₂S escapes far faster than water

This is the number that matters, and it does not depend on the pipette. At pH 8.2 in seawater only 2.3 % of the
dissolved sulfide is H₂S (pK₁* 6.57 at 22 °C, Millero, Plese & Fernandez 1988), but H₂S is volatile (air/water
partition 0.38, Sander 2015). The same paths that let water vapour out let H₂S out, with the sulfide in the well
diffusing up to the surface to replace it (D = 1.6 × 10⁻⁹ m²/s; the well is 3.0 mm deep, 93 min of diffusion time).
[`cubxl_evap.py`](../cubxl_evap.py) solves that in one dimension for the 1 mg/L well (135 µL of ASW, then 15 µL of the
10 mg/L stock), from the moment the sulfide lands to the end of the measurement:

| 1 mg/L well, 22 °C, 40 % RH | Left in the well when the cap goes on | Left at the end (55 min) | At the metal, mean over the measurement |
|---|---|---|---|
| A. As planned: sulfide last, not mixed (a 0.3 mm layer on top), leak check and cap-on open (3 min), clearance cap | 25 % | 6 % | **11 %** of nominal |
| B. As A, mixed at once after the sulfide | 81 % | 26 % | **66 %** |
| C. Mixed, and the leak check done before the sulfide (30 s open), clearance cap | 92 % | 28 % | **70 %** |
| D. As C, with the O-ring cap (sealed but for its 0.3 mm vent) | 92 % | 89 % | **93 %** |
| E. Bound: the whole well stirred (below), 3 min open, clearance cap | 38 % | 0.4 % | 8 % |

- **The clearance cap holds water but not H₂S.** It cuts the gas path's conductance about fourfold, which takes water
  loss from 6 to 1.6 µL/h. For sulfide that only takes the escape velocity at the surface from 16 to 4.3 µm/s, and
  both are far above what diffusion in the liquid can deliver (D/depth ≈ 0.5 µm/s). So the loss is set by diffusion
  in the well either way: the sulfide halves in about 30 min, cap or no cap. Only a cap that seals (D: 0.03 µm/s)
  keeps it.
- **Mixing matters as much as the cap.** Dispensed from above onto 135 µL of ASW and left, the sulfide spends its
  first minutes in a thin layer at the surface, where it escapes, and needs an hour and a half to diffuse down to the
  metal (A). The drop's own impact mixes some of it, so the truth for the plan as written is between A and B. A few
  aspirate-dispense cycles in the well with the sulfide tip, which goes to the waste anyway so DAL's tip rules allow
  it, move it to B.
- **E, the other bound.** Evaporation cools the surface: 79 W/m² open, 21 W/m² under the clearance cap, so the surface
  sits 0.4 K and 0.1 K below the metal, which gives a Marangoni number of 1300 and 340 against an onset near 80 for
  a layer cooled from above. A clean ASW surface may well turn over, and then the loss runs at the gas side's rate: τ =
  depth / 4.3 µm/s = 12 min under the clearance cap. With the O-ring cap evaporation stops, so does the stirring
  (Marangoni number 3), and D stands.
- **The copper takes sulfide too.** Over 63 min at DAL's fresh-surface 1-11 µA/cm² on the 0.10-0.13 cm² wetted, the
  metal releases 4-54 nmol of Cu(I), enough to bind 2-27 nmol of sulfide as Cu₂S, against 4.7 nmol in a 1 mg/L well.
  That sink is the experiment's own and is not modelled; it comes on top of the H₂S.
- **The wells made of stock alone** (0.1 and 10 mg/L: 150 µL of a stock) lose sulfide during the fill, and here the
  pipette does matter: 8 P20 transfers over 6 min leave **42 %** of the sulfide in the well when the cap goes on and 14
  % at the end; one big transfer leaves 83 % and 27 %.

**So DAL's sulfide axis is not what the stocks say** with the clearance cap: the metal sees somewhere between a tenth
and two thirds of the nominal dose, averaged over the measurement, depending on mixing that nobody controls. That is a
larger and less certain error than anything in the pipetting. DAL already flagged the still well's oxygen limit as
compressing the sulfide response (`protocol.md` §3); this is a second, independent compression.

### Fixes, ranked by what they buy

1. **Seal the well for sulfide spots**: DAL's own fallback O-ring cap (`electrode_cap_oring`, with its 0.3 mm vent),
   or a clearance cap with a much longer, narrower gap. It keeps 89 % of the sulfide (D) and stops 98 % of the
   water loss under the cap. Its catch is DAL's: 2.3-85 N to pull it off against the electromagnet's ~23 N. Sulfide
   spots are the place to solve that (a lever, or a cap the gantry pushes off sideways), since only they need it.
2. **Mix after the sulfide**, with the tip that added it (3-5 aspirate-dispense cycles, about 45 s on the CubXL). A
   P300 mixes a 150 µL well properly; a P20's 20 µL strokes stir the top of it.
3. **Do the leak check before the sulfide**, on the ASW alone, then add the sulfide, mix and cap within 30 s (C).
4. **Measure it.** A witness well on S4 (the PTFE blank) filled at the same dose, collected after the same 63 min into
   a zinc-acetate trap and read by methylene blue, tells the real dose. The tubes are acidified at once, which drives
   off H₂S, so the main tubes can't tell it.
5. **Make the 0.1 and 10 mg/L wells in one transfer** (a P300), or from a premixed vial, not 8 P20 draws of stock.
6. **For water**: weigh the tubes and the stocks, as above; a lid over the tube rack. Lowering the room's dryness or
   humidifying the VLM is not needed for the well: 1-3 % per spot is fine.

SECTION_REFERENCE

SECTION_MODEL

SECTION_OPEN

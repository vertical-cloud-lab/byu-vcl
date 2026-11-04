# The CubXL on tray A: DAL's copper corrosion screen, and the powder the doser makes for it

Asked for on [PR #318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318) (2026-11-04):

> "The amount of liquid removed from the CubXL vials doesn't correspond to the actual 20, 200, or 1000 uL pipettes
> that would be typical of OT-2 pipettes. ... Also, the CubXL isn't in the same configuration and isn't showing the
> same workflow as [DAL PR #180](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/180#issuecomment-6464147350)."
>
> "Why are you dosing salt? You should be showing the dosing of several alloy precursors into a charge cup for the
> atomizer workflows and dosing of an atomized powders for use in the CubXL."

Code: [`instruments_lab.py`](../instruments_lab.py) (`cubxl_corrosion`, `powder_test`), [`cubxl_rig.py`](../cubxl_rig.py),
[`animate.py`](../animate.py) (`workflow`). Clips: [`cubxl_corrosion.mp4`](../out/mp4/instruments/cubxl_corrosion.mp4),
[`vlm_workflow.mp4`](../out/mp4/vlm_workflow.mp4).

## What DAL's copper screen is

Everything is from digital-alloy-lab PR #180's branch `claude/issue-213-20261013-2132` at
[`aeda51a`](https://github.com/vertical-cloud-lab/digital-alloy-lab/tree/aeda51a/alloy-corrosion), the commit of the
comment Sterling linked:

| File | What it fixes here |
|---|---|
| [`copper/deck_cu.py`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/copper/deck_cu.py), [`plot_deck_layout.py`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/plot_deck_layout.py) | every deck position and the head's offsets |
| [`copper/protocol.md`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/copper/protocol.md) §2-4, §6 | the cell, the electrolyte mixing table, the 13-step sequence, ICP-MS |
| [`copper/render_cubxl_cu.py`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/copper/render_cubxl_cu.py) | DAL's own animation: its story (10 steps), cameras, how it places Ben's STEP files, the well-level function |
| [`copper/copper_numbers.json`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/copper/copper_numbers.json) | P20 transfer counts, timing (67 min a spot), the 320 µL tube, EIS and Randles numbers, hold charge |
| [`cubxl-setup.md`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/cubxl-setup.md) §3, §5, §8 | the head (a P20 single Gen2), transfer counts, and the doser's role |

**The deck** (CubOS deck frame of Ben's 2026-10-02 calibration, mm; a proposal, nothing built). Now drawn exactly so:

| Item | Where |
|---|---|
| Coupon tray, S1 C71500 Cu-Ni, S2 C95800 NAB, S3 a DED pad, S4 a PTFE blank | x 185/210/235/260, y 240; face z 20, lid 26 |
| Well | AS568-006 in a 7.30 × 1.40 mm counterbore, a 2.9 mm throat 1.6 mm deep, an 8 mm bore: 150 µL |
| Ben's 9-position 20 mL holder ([STEP](../../modules/electromagnetic-capper/cad/9VialHolder20mL_TightFit.step)), x 318, y 35 + 33k | spare (FeSO₄ nights), 1 M HNO₃, ASW (D1141, no heavy metals), ASW + 10 mg/L S, ASW + 0.1 mg/L S, DI water; y 233 and 266 empty |
| Cups (4 mL) | rinse 2 ASW (30, 245), rinse 1 DI (60, 245), park cup (90, 245) |
| Tube rack, 2 × 8 open 0.5 mL PP tubes | x 176 + 12k, y 28 / 46 |
| Tip racks, 2 × 15 at 8.5 mm | rack 1 (Ben's) A1 (291.3, 89); rack 2 A1 (108, 89) |
| Tip waste | (385, 150), Ø 30 |
| Head | capper (Ben's PAW-V2 mount [STEP](../../modules/electromagnetic-capper/cad/PAW-V2-ElectromagnetMount.step), magnet face 16 below the carriage), P20 (+55, +11), camera (−40, +10) |
| Electrode cap | leak-free Ag/AgCl reference, tip 3 mm above the metal, in a Pt coil; two pogo pins at ±11 mm |

Before this, the clip drew the **aluminium** plan of [`cubxl-setup.md`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/cubxl-setup.md)
(0.6/0.06/0.006 M NaCl stocks, one rinse cup, coupons of one alloy, OCP then cyclic polarization on every spot), with
the stocks and rack 2 moved, and the P20 drawing 150 µL in one go.

**The spot, in the clip's order** (protocol §4; DAL's story in `render_cubxl_cu.py`):

1. A 20 µL tip from Ben's rack.
2. The capper lifts the ASW cap; **7 transfers of 19.3 µL** (135 µL), each dispensed from above the meniscus.
3. Sulfide last: **one 15 µL transfer** of the 10 mg/L S stock with the same tip → 150 µL at 1 mg/L S; the tip to the waste.
4. Leak check, head camera, 2 min.
5. The electrode cap from the park cup onto S1's boss, tipless.
6. OCP 20 min → **EIS at OCP 10 min** (10 mV rms, 100 kHz → 10 mHz) → LPR ±10 mV → rest 5 min → **+50 mV hold 10 min**
   → OCP 5 min. EIS needs the requested potentiostat: the EZstat Pro beside the frame has none, so until it arrives
   DAL skips it and runs OCP 30 min (said on screen).
7. The cap off, dipped in DI water, then seawater, parked.
8. A new tip: **8 transfers of 18.75 µL** from S1 to tube 1, then the 150 µL DI rinse the same way (**16 transfers**).
9. Acidify at once: the acid cap off, the night's one acid tip from rack 2, **one 20 µL transfer** of 1 M HNO₃ from
   above the rim → **320 µL** at 62 mM HNO₃; the acid tip back to rack 2, the cap back.
10. The camera images the spot; next, S2.
11. A card: cyclic polarization **only on selected spots, and last on each** (fill to EIS, the scan, its own tube):
    on a main spot its ~3.4 mC would swamp the tube's copper against the hold's 0.2–2.8 mC.

**Volumes and pipettes.** The pipette is the CubXL's own **P20 single-channel Gen2** (1–20 µL, `cubxl-setup.md` §3),
with 20 µL tips; no move is over 20 µL. A panel on screen counts the µL in the tip, in S1, in tube 1, and in the stock
vials, and which transfer it is. The first transfer of each series is shown at full speed, the rest sped up (labelled).

**Levels to scale** (`well_level`, `tube_level`, `tip_level` in `instruments_lab.py`):

| | Volume | Level |
|---|---|---|
| Well S1 (DAL's `well_level`) | 150 µL | 4.4 mm above the metal (4.5 with the cap's capillary in) |
| Tube 1, 0.5 mL PP | 150 / 300 / 320 µL | 12.6 / 17.5 / 18.2 mm above its outside bottom |
| A 20 µL tip | 15 / 19.3 / 20 µL | 10.0 / 11.2 / 11.4 mm up from its end |
| A 20 mL stock vial (18 mL, Ø 25.2 mm inside) | −135 µL of ASW | 0.27 mm lower: the panel shows 18.000 → 17.865 mL |

**The measurement overlay is illustrative**, as before: E − E_corr against time with each phase at the protocol's
settings (±10 mV, +50 mV) but a made-up drift; the Nyquist arc is the Randles circuit DAL's video draws (R_u 60 Ω,
R_p 48.8 kΩ from its C71500 well simulation, an assumed 30 µF/cm² on 0.0661 cm²).

**For DAL, from building it in 3-D** (not changed in the drawing):
- DAL's deck check is in plan, with the capper as a 10 mm-radius disc. Ben's PAW-V2 mount, placed as
  `render_cubxl_cu.py` places it, spans x −25.2 to +15.7 and y −16.7 to +14.5 mm about the capper's axis in its
  lowest 16 mm. With one well at each station's centre (DAL's render, and this clip) it clears rack 2 by 0.3 mm while
  the P20 is in S1. With the **two wells per station** of the deck check (y 235.5 / 244.5), the front well puts the
  mount 9 × 4 mm over rack 2's back right corner, 8–15 mm below the rack's top. Drawing from a stock, it comes 1.6 mm
  into the side of Ben's rack 1, 1 mm below its top, if that rack is DAL's tips ± 5.75 mm.
- The DI rinse: protocol §4 step 11 moves "150 µL plus one 150 µL DI rinse" into the tube, and §3's tip rule says a
  tip that has touched well liquid never goes back into a stock, while 17 tips a night is two a well plus the acid
  tip. Where the rinse's DI water is drawn from, with which tip, isn't written down. The clip shows it as a sped-up
  "the same way", without drawing a tip into the DI vial.

## Why the doser doses atomized powder now, not salt

DAL rules salt out in so many words (`cubxl-setup.md` §8): "Making electrolyte from solid NaCl on the deck is possible
but pointless here ... three 20 mL stocks cover 0.006 to 0.6 M for weeks ... Dosing salt would add a balance, a
dissolution step and a stirrer for no gain." Every electrolyte in the clips is a stock the P20 draws from.

Where salt was dosed as a powder:
- **Round 2's workflow** (`animate.py workflow`, `vlm_workflow.mp4` before this): "dose 0.5 g of a powder" (0.512 g)
  into a vial, then "add liquid to it in the CubXL". **Re-scripted here.**
- **PR #320's multi-doser cutaway** (`instruments_round2.py` at `5a39245`, in the long-form's chapter 4): "Salt leaves
  the outlet at 105 mg a turn ... The vial holds 0.525 g of salt", the rig's test powder (powder-doser TEST-PLAN T6c,
  T8). Its `cubxl_lh` clip then pipettes onto "the vial dosed by the multi-doser" and mixes. Not changed here
  (#320's file); the long-form now uses this note's clips for tray A instead.
- Chapter 1 ([`alloy_charge.py`](../alloy_charge.py), another session's) is where the doser doses alloy precursors
  (Si, AlSi10Mg, Ni, Cu) into the atomizer's charge cups.

**What the doser does for the CubXL instead.** DAL names one place the doser matters to corrosion (`cubxl-setup.md`
§8, "Where it could matter"): a **powder reactivity test**, "Dose a weighed 10–50 mg of each run's powder into a tube,
add 0.6 M NaCl ..., hold for a fixed time, and send the liquid to ICP with the corrosion tubes. Dissolved Al and Mg
per gram of powder would track the oxide and surface condition the atomizer program is trying to control." DAL puts
it after the corrosion baseline, outside the BOM, and says the powder itself can't be a working electrode. That is the
closest documented use, so the workflow shows it:

1. Tray B: the doser's module 6 holds atomized AlSi10Mg from a rePowder run, its 20–63 µm cut. The auger turns in
   short steps until the load cell reads **25 mg**: a heap 6 mm across and 2 mm tall at a 34° angle of repose and an
   assumed poured 1.4 g/cm³, drawn to scale. mg resolution on the doser's 100 g cell is a requirement (powder-doser
   PR #270 §5), not a demonstrated figure.
2. The arm brings the vial to tray A and stands it in the **spare seat** of Ben's holder (318, 35), which DAL keeps for
   a FeSO₄ vial on non-sulfide nights only.
3. The CubXL's P20 takes a tip, the capper lifts the seawater cap, and **10 transfers of 20 µL** put **200 µL** on the
   powder, 0.39 mm deep in the vial (to scale). The copper deck's chloride stock is ASW; DAL's §8 names 0.6 M NaCl (the
   aluminium plan's top stock). The hold and the ICP-MS tube are told in the caption, not drawn.

What is assumed: the powder (AlSi10Mg: the alloy route's), its bulk density, the 25 mg and 200 µL (DAL gives 10–50 mg
and no volume), the vial (the doser's own 20 mL; DAL says "a tube"), and the seat.

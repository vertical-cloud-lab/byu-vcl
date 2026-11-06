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

Both clips were rendered at 10 fps (`VIZ3D_FPS=10`) to finish in the session; `xvfb-run --server-num=80 python3
tour.py cubxl_corrosion` and `xvfb-run --server-num=81 python3 animate.py workflow` give 15 fps. Round 2's workflow
was arm-audited after the opening went to 996 mm (`ARM_AUDIT=1`): **0 of 1191 frames** in collision
([`out/collisions/vlm_workflow.json`](../out/collisions/vlm_workflow.json)).

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

One difference, kept on purpose: DAL's render draws a small potentiostat box behind the deck (x 0–80, y 290–330, its
EmStat Pico plan). The clip keeps the potentiostat the lab has, NuVant's EZstat Pro, beside the frame with its cell
cable to the tray's bus, as before ([#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231)).

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
  `render_cubxl_cu.py` places it, is 41 × 31 mm in its lowest 16 mm (x −25.2 to +15.7, y −16.7 to +14.5 about the
  capper's axis). Every waypoint of the spot and of the powder test was checked against the deck with CadQuery
  booleans. The one hit: drawing from the ASW and the 10 mg/L S stocks (carriage at 70), the mount's lower edge is
  1.6 mm into Ben's rack 1 over 12 mm, 1 mm below the rack's top, if that rack is DAL's tips ± 5.75 mm wide and 55 mm
  tall (as `render_cubxl_cu.py` draws it). Measuring the real rack settles it.
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
   assumed poured 1.4 g/cm³, drawn to scale. mg resolution on the doser's 100 g cell is a requirement ([byu-vcl
   PR #270](https://github.com/vertical-cloud-lab/byu-vcl/pull/270) §5, which DAL cites), not a demonstrated figure.
2. The arm brings the vial to tray A and stands it in the **spare seat** of Ben's holder (318, 35), which DAL keeps for
   a FeSO₄ vial on non-sulfide nights only.
3. The CubXL's P20 takes a tip, the capper lifts the seawater cap, and **10 transfers of 20 µL** put **200 µL** on the
   powder, 0.39 mm deep in the vial (to scale). The copper deck's chloride stock is ASW; DAL's §8 names 0.6 M NaCl (the
   aluminium plan's top stock). The hold and the ICP-MS tube are told in the caption, not drawn.

What is assumed: the powder (AlSi10Mg: the alloy route's), its bulk density, the 25 mg and 200 µL (DAL gives 10–50 mg
and no volume), the vial (the doser's own 20 mL; DAL says "a tube"), and the seat.

## Round 9: where does the second cap go? (PR #318, Sterling 2026-11-05 22:56)

> "The CubXL magnet can only hold one cap at a time. Where is that other cap? Does it get placed in an intermediate spot?
> (probably the best option, but you'll need to check for interference or simply have an empty vial that's sole purpose is
> as a temporary parking spot for a cap when two caps need to be off at the same time."

Code: [`r9_cubxl.py`](../r9_cubxl.py) (a copy of `instruments_lab.cubxl_corrosion` and its timeline, registered under the same
`REGISTRY` key, so `tour.load` and [`cubxl_rig.py`](../cubxl_rig.py) use it everywhere; `instruments_lab.py` is untouched),
clip [`cubxl_corrosion.mp4`](../out/mp4/instruments/cubxl_corrosion.mp4).

**What DAL already decided** ([PR #180](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/180) at
[`aeda51a`](https://github.com/vertical-cloud-lab/digital-alloy-lab/tree/aeda51a/alloy-corrosion)): nothing about vial caps
other than the primitive. `cubxl-setup.md` §3 says "CubOS's `decap a` / `cap b` pair already moves one cap from one vial to
another, which is the whole primitive needed", and DAL's own answer for the electrode cap is a **vial as the parking
place**: the 4 mL park cup, "the cap parks in the reference's storage solution between nights". So a vial that holds a cap
is already the convention; protocol.md §4 only requires that cap moves are tipless (the electrode cap's).

**Where two caps are off at once.** DAL's 13 steps, as the clip ordered them in round 8, never had two vial caps off: each
stock was opened, used and re-capped in turn, the cap riding the magnet (so the magnet was occupied, but nobody needed it).
That is only true while every transfer is a separate open-draw-close. Any order that keeps one stock open while another
is opened needs a second place. The clip now shows exactly that case: **ASW is kept open through the sulfide addition**
(the same tip goes from the 7 ASW transfers to the 15 µL sulfide draw with no re-cap in between, and a top-up from ASW
stays possible if the leak check or the volume says S1 is short). That is two caps off at once: the ASW cap is parked, the
sulfide cap rides the magnet, then each goes home in turn (sulfide first, ASW fetched from its parking spot after). The
electrode cap is a third cap, but it is never off at the same time as a stock cap: it is picked and set between the
sulfide step and the acid step with every stock capped. (The ordering is this round's choice, not DAL's; DAL's strictly
serial order needs no parking vial, and the clip's step 3 can go back to it by deleting two moves.)

**Options weighed.**

| Option | Cost on the deck | Capper reach | Verdict |
|---|---|---|---|
| A post or cup on the deck | new part, new footprint; the deck is full (holder, cups, rack, tray all drawn from DAL's coordinates) | any, but every free spot near x 318 is the holder's own | needs hardware DAL doesn't list |
| **An empty 20 mL vial in Ben's holder, seat 6 (y 233)** | none: DAL's holder has two empty seats (6 and 7, "positions 6 and 7 stay empty"); one vial, no liquid | on the stocks' own x line, 33 mm from the sulfide stock, so no new travel at height; the cap goes on exactly as on a stock vial (same seat, same magnet height, same CubOS `cap`/`decap`) | chosen: Sterling's suggestion |
| An intermediate spot on the cups block | the cups (x 30-90, y 245) are 4 mL vials with the electrode cap parked in one; a 16 mm vial cap doesn't sit on a 15 mm cup | far from the stocks: +230 mm | no |

The vial rather than a cup: a vial cap has the same boss and the same lid geometry as the stock it came from, and a cap that
sits on a clean, dry, empty vial doesn't pick up anything from a stock's rim. Keep it dry and dedicated: it holds only
caps, never a liquid. A second parking vial (seat 7) costs nothing if a third cap is ever parked.

**Interference** ([`interference.py`](../interference.py), MuJoCo + FCL, every frame of the 1125 of the clip):
8 faults and the same 8 as round 8's clip, all pre-existing and unchanged (tips seating in their racks, the gantry
guides, the O-rings: "as modelled" or "guide" by `interference.py`'s own classification), no new fault from the
parking vial, the parked cap or the extra capper moves. The new contacts are minor (under `TOUCH_MM` of seating): the ASW cap
on the parking vial (1.61 mm, the same seating as a cap on any of its own vial: `built in` 1.61 mm on the stocks). Round 7's
finding stands, unchanged: Ben's capper mount brushes tip rack 1 by 1.06 mm over 13 mm3 (1.6 mm in round 7's CadQuery
check) on the way to the stocks; the moves to the parking vial add none. The head at the parking vial puts the camera at
x 278, y 243 over the coupon tray's far end with its underside about 95 mm above the deck, roughly 70 mm over the lids (an estimate from the model).

For the 8:37 clip (`animate.workflow`, the doser stream's): that clip shows the powder test (`powder_test`), whose only
stock is the ASW for the 200 µL addition, so it needs no second cap. If it ever opens two stocks, call
`r9_cubxl.corr_offsets` (via `cubxl_rig.CubRig.pose`, which now does) with `pcap="asw"` in the state, and `vcap=...` for the
cap on the magnet.

Not yet verified by anyone: that the magnet can seat and lift a cap from a vial of the same make held 33 mm away (no
bench test; the lift force is DAL's open bench test 1 for the electrode cap).

**Open (camera).** In the committed clip the close-up camera for steps 2 and 3 (`_C_HOLD` in `r9_cubxl.py`, eye (140, 40, 340),
CubOS mm) is too tight: the parked ASW cap on the parking vial is hard to see behind the head. A pulled-back eye of about
(15, -60, 545) looking at (318, 170, 50) was queued as a second render but was stopped for slot time and never viewed; it is
unverified. The GIF in `out/instruments/` is the committed 598-frame GIF thinned to every second frame at 0.8 scale (3.8 MB).

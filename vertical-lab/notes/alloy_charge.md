# The alloy route, chapter 1: the atomizer charge, made up in the VLM

[`alloy_charge.py`](../alloy_charge.py) over [`charge.py`](../charge.py), byu-vcl #303. It replaces round 2's vial
(`animate.py workflow`: a 20 mL vial dosed, then liquid added in the CubXL). It also fills a gap in
[`dal_workflow.md`](dal_workflow.md): a station that fills and presses the atomizer's cups.

Reworked after [PR #318's review](https://github.com/vertical-cloud-lab/byu-vcl/pull/318):
- **four cups a run**, not two;
- **an A&D HR-202i balance**, not the multi-doser's 100 g load cell;
- **one funnel per powder**, not the doser's shared catch funnel.

| Step | What happens | Shown |
| --- | --- | --- |
| 1 | Tray B comes down to the opening. It carries the multi-doser, the HR-202i, an eight-cup charge rack, a plug press and a funnel stand | wide, then labelled |
| 2 | The arm sets the Si funnel in the doser's fork. Its stem stops 4 mm over a cup's rim | the station |
| 3 | The first 5N Al cup goes from the rack into the doser's cradle, under the funnel. The carousel indexes the Si module, docks, tilts and doses 3.92 g by auger turns. Then the cup goes into the HR-202i, which reads it | cup, funnel in half section; the balance |
| 4 | Onto the press's ejector, down into the F1 sleeve; its own plug from above; the nest slides in and the ram presses the plug flush; onto the MiR250's carrier | press in half section |
| 5 | The other three Al cups, faster | wide |
| 6 | The Si funnel goes back to the stand; the Ni funnel takes the fork | the station |
| 7 | The four OFE Cu cups with Ni, faster; they go back on the rack. The Ni funnel goes back to the stand | wide |
| 8 | Tray B goes back into storage. Four Al-10Si cups are on the MiR for the rePowder | the carrier |

## The charge

**The geometry is #222's own.** The cup, plug and sleeve profiles are copied dimension for dimension from
`atomizer-charge/cad/charge_cad.py` (branch `claude/issue-222-20260925-0343`, commit `2a608d6`), the parametric CAD
behind the lab's STEP files, shop drawing and process sheets:
- **cup (P2):** 3/4 × 2.5 in, with a 1/2 in bore 1.875 in deep and a 118° drill point;
- **plug (P3):** 1/2 × 3/8 in, with a 15° lead-in and a 1/16 in vent;
- **F1:** 1018 steel, 1.25 in round, bored to the cup's OD + .0005 in, as long as the cup.

From the profiles (Pappus):
- cup 11.887 cm³;
- plug 1.173 cm³;
- cavity under a flush plug 4.903 cm³, including the drill point.

**Four cups a run.** The lab loads four charges into the crucible (Sterling, PR #318). The Oct 27 630 bronze run went
in as four rod pieces, 1,080 g (DAL #219, #230). #222 already has four places round the sealing rod. Two runs are made
up ([`out/alloy_recipe.json`](../out/alloy_recipe.json)):

| Run | Cups | Powder in each | Fill | Charge | Designed |
| --- | --- | --- | --- | --- | --- |
| this one | 4 × 5N Al (2.699 g/cm³): cup 32.08 g, plug 3.17 g | Si 3.92 g, tapped 1.10 g/cm³ (#222) | 27.7 mm, 10.4 mm headspace | 156.7 g | Al-10Si |
| next | 4 × OFE Cu, C10100 (8.94 g/cm³): cup 106.27 g, plug 10.48 g | Ni 12.97 g, tapped 4.9 g/cm³ (assumed) | 20.6 mm, 17.5 mm headspace | 518.9 g | Cu-10Ni |

- **Al-10Si** has the Si of the AlSi10Mg that the line prints (chapter 4). It has no Mg: 5N cups bring none, unlike
  the 6063 trial cups.
- **156.7 g of Al cups is a normal Al run.** The lab's Al runs so far melted 169–180 g (DAL #159: 180 g of 6063 on
  Oct 6, 169 g of 4047 on Oct 21 and 22). Chapter 2 works out what it makes.
- **Cu-10Ni** is the 90/10 cupronickel of the Navy's seawater piping. C70600 adds 1–1.8 % Fe. This is DAL's Cu
  work: #162 (high-purity Cu rod "similar to the aluminum rods") and #219 (the NAB run).
- **"Designed"** means every gram dissolves, as #222 uses the word. ICP/EDS on the powder measures recovery.
- **Weigh, don't trust volumes** (#222). The tapped densities set only the fill heights drawn.

**The 5N rod is Ø20 mm** (DAL #152), not 3/4 in. The cups here keep #222's 3/4 in profile, so they are the same
part in another metal. A 5N cup turned from Ø20 bar would be 0.95 mm larger across.

## Weighing: an A&D HR-202i, not a load cell

**The multi-doser's 100 g load cell is gone.** The chain carousel in powder-doser PR #185 dosed onto a TAL221 bar load
cell. The lab's own doser doses onto an analytical balance, the A&D HR-100A (102 g × 0.1 mg), read over RS-232
(powder-doser #99; PR #97 replaced the HX711 load cell with the HR-100A in the doser's paper and BOM). A Cu cup with its plug and Ni
is 129.7 g, over the HR-100A's 102 g. So the station here weighs on its larger sibling, the **A&D HR-202i**:
- **220 g × 0.1 mg**, with a 51 g × 0.01 mg fine range. It is one of the balances powder-doser's
  `design/brainstorming.md` weighs (FZ-523, HR-202i, HR-300i, HR-100A);
- the Al cup with its Si is 36.0 g and the Cu cup with its Ni is 119.2 g before the plug, all inside one range.

**The model** ([`lab_models/labware.py`](../lab_models/labware.py), `balance_hr202i`, `hr202i_parts`) is drawn from
A&D's HR-i manual, section 15.1 "External Dimensions" (p. 60):
- 217 × 442 × 316 mm overall; the body 200 wide, 428 deep, 310 tall;
- pan Ø90, its centre 163 mm behind the front;
- weighing chamber 183 × 164.5 mm inside and 250 mm over the pan, the pan 86.5 mm behind the chamber's front glass;
- side doors 148.5 × 251 mm, top door 164 × 148.5 mm, all sliding back;
- the pan's height (50 mm) and the display's slope are read off the drawing, not dimensioned.

**The balance can't go under the doser's outlet as the rig is built.** The chain carousel's docking actuator (the
P16 and its clevis on the station's cross rail) stands 6 mm behind the auger's outlet, from the rig's base up to the
carriage. The old vial (28 mm across) fitted in front of it; a 90 mm pan, let alone a 183 mm weighing chamber, does
not. So, in this chapter:
- the rig's load cell, vial cup, vial post and catch funnel come out;
- a new 2020 post on the same base rail carries a cradle for the cup (a C open to the front, so the arm slides the cup
  in level) and, above it, a fork for the powder's funnel;
- the doser doses by auger turns, from its own calibration;
- the arm takes the cup to the HR-202i, which reads it. Inside the tolerance (±1 % of the dose, assumed), the cup goes
  on; a short cup would go back to the doser for a top-up, as the trickler does on the HR-100A.

Dosing straight onto the balance, in closed loop, needs the station redesigned so that the outlet sits over the
balance's top door: the actuator moved behind or above, and the rig raised or the balance lowered. That is
powder-doser's call. The arm can't slide the HR-202i's doors: here they open on their own, which assumes a door drive
or a balance with automatic doors.

## One funnel per powder

**The doser has no funnel of its own.** When the lab charged cups by hand, it used paper funnels, and a funnel only
ever saw one powder, to avoid cross-contamination (Sterling, PR #318). Here:
- **each powder has its own funnel**, labelled by a coloured band (Si yellow, Ni green). It is only used for that
  powder. Printed PP is drawn; it could as well be stainless steel, or a paper funnel thrown away after each run;
- **it lives on a stand** on tray B, by its flange, in a fork open to the front, so the arm takes it level;
- **at the doser it sits in a fork over the cup.** Its stem, 9 mm across, points into the 12.7 mm bore and stops 4 mm
  over the rim. It never touches a cup, so it carries nothing from one cup to the next, and the cup slides in and out
  under it;
- **the swap** is the cross-contamination step: the Si funnel comes out after the four Al cups and goes back to its
  place, and the Ni funnel takes the fork for the Cu cups. One funnel serves all the cups of one powder in a run;
- **the dose's path** is the auger, the powder's funnel and the cup, nothing shared. Each module's auger already
  carries only its own powder.

Keeping funnels apart, in practice:
- dedicated and labelled, one per powder, cleaned between runs (the sieve-cleaning question in DAL #234 applies);
- or paper, used once and thrown away, as the lab did by hand. A robot would need a dispenser for those.

Funnel geometry (`charge.FUNNEL`, our design): cone 40 mm across and 22 mm tall over a 2 mm flange 28 mm across,
a stem 9 mm across (6 mm bore) and 12 mm long, and a 42 mm band to grip by. The stream from the auger lands on the cone
15 mm off its axis, about 66 mm below the outlet.

## What the chapter showed

- **The weighing station and the dosing station are two places.** The rig as built has no room under its outlet for
  a balance (above). Each cup makes one extra trip, doser to balance.
- **A cup is always held level.** It is picked, placed and carried with the fingers closing sideways, so its axis
  never tilts. That is why the rack has the cups in its front row, the cradle is open to the front, and the balance's
  cup holder is open to its door. The balance is turned so that a side door faces the arm.
- **The plugs are taken from above.** The 2F-85's pads are 38 mm long and a plug is 9.5 mm tall. The fingertips meet
  the plug's top 7.5 mm, 2 mm above the cup's rim.
- **The press has to open above the nest.** The arm sets the plug from above, and the gripper and wrist need about
  270 mm over it. So the nest slides out from under the ram for loading, and back in for pressing. A press-fit
  station's shuttle table is the usual answer.
- **The ram bottoms out on F1.** F1 is as long as the cup, so the plug ends flush with the rim (#222). The plug
  travels 8.0 mm after its lead-in seats it 1.5 mm into the mouth.
- **F1 makes a gripper problem.** With the plug flush, the cup is entirely inside the sleeve. The nest's ejector
  lifts it 36 mm so the gripper can take it.
- **Eight cups and two funnels fill tray B's left half.** The rack is 336 mm long, the HR-202i 442 mm. The press now
  stands behind the rack, and the arm reaches over the rack's cups to its nest.

Replaced since round 4: "a Cu cup is over the doser's load cell" (there is no load cell), and "the doser's funnel
is wrong for a cup" (there is no shared funnel; each powder's funnel is sized for the bore).

## Assumed

- **The press:** a benchtop electric press with a shuttle nest and an ejector. It is 260 × 325 × 510 mm (frame and
  motor), with a 100 mm stroke above F1. No press-fit force is given, since #222 gives no interference for the plug.
  The lab's own press-fit station is a 1 t arbor press (#222 E4), worked by hand.
- **The rack, the station's post, cradle and fork, the funnels and their stand, the balance's cup holder and the
  MiR's carrier** are this model's designs. The carrier stands where round 2's one-vial holder stood.
- **The balance's doors open on their own** (a door drive; the HR-i's are manual).
- **Dosing by auger turns** lands within ±1 % of the dose (the readings shown are made up to be inside it).
- **Tapped densities of Ni, Fe and Cu powder**: 55 % of the solid. The Si and Al values are #222's.
- **The two powder modules**, Si in module 6 and Ni in module 3, are a choice. The multi-doser has 13.
- **The vent's puff** while the plug goes in is drawn only to show where the air leaves. Nothing was computed.

## Open questions

- Should the doser dose straight onto the balance? Then the chain carousel's station needs a new layout (above).
- Does the plug press-fit need F1 at all with 5N Al? 5N is much softer than 6063-T52, which also makes the cup's wall
  easier to bulge.
- How tight is the plug in a Cu cup? A Cu plug in a Cu bore needs the same interference as Al, or a new one.
- Should each cup be weighed again after pressing, as #222 asks ("weigh it")? The HR-202i is on the tray, so it would
  cost one more trip per cup.
- How are the funnels cleaned between runs, or are they paper and single-use? DAL #234 asks the same of the sieves.

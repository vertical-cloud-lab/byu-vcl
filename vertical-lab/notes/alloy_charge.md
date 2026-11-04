# The alloy route, chapter 1: the atomizer charge, made up in the VLM

[`alloy_charge.py`](../alloy_charge.py) over [`charge.py`](../charge.py), byu-vcl #303. It replaces round 2's vial
(`animate.py workflow`: a 20 mL vial dosed, then liquid added in the CubXL). It also fills a gap in
[`dal_workflow.md`](dal_workflow.md): a station that fills and presses the atomizer's cups.

| Step | What happens | Shown |
| --- | --- | --- |
| 1 | Tray B comes down to the opening. It carries the multi-doser, a charge rack and a plug press | wide, then the labelled tray |
| 2 | The UR10e takes an empty 5N Al cup from the rack, gripper level, and stands it under the doser's funnel on its load cell | arm |
| 3 | The carousel indexes the Si module, docks, tilts and doses 3.92 g. The bore fills from the drill point | close-up, cup in half section |
| 4 | The cup goes onto the press's ejector, which draws it down into the F1 sleeve. The arm sets the cup's own plug from above | arm, press |
| 5 | The nest slides in, and the ram presses the plug flush. Air leaves through the vent | close-up, half section |
| 6 | The charged cup goes onto the MiR250's carrier | arm |
| 7 | The same again, faster: the second Al cup (Si), then two OFE Cu cups (Ni), which go back on the rack | arm |
| 8 | Tray B goes back into storage. Two Al-10Si cups are on the MiR for the rePowder | the carrier |

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

**Two metals, two runs** ([`out/alloy_recipe.json`](../out/alloy_recipe.json)):

| Run | Cups | Powder in each | Fill | Charge | Designed |
| --- | --- | --- | --- | --- | --- |
| this one | 2 × 5N Al (2.699 g/cm³): cup 32.08 g, plug 3.17 g | Si 3.92 g, tapped 1.10 g/cm³ (#222) | 27.7 mm, 10.4 mm headspace | 78.3 g | Al-10Si |
| next | 2 × OFE Cu, C10100 (8.94 g/cm³): cup 106.27 g, plug 10.48 g | Ni 12.97 g, tapped 4.9 g/cm³ (assumed) | 20.6 mm, 17.5 mm headspace | 259.5 g | Cu-10Ni |

- **Al-10Si** has the Si of the AlSi10Mg that the line prints (chapter 4). It has no Mg: 5N cups bring none, unlike
  the 6063 trial cups.
- **Two cups a run** is #222's default. 80-100 g is the basis of #161's 100 g/run purchase model.
- **Cu-10Ni** is the 90/10 cupronickel of the Navy's seawater piping. C70600 adds 1-1.8 % Fe. This is DAL's Cu
  work: #162 (high-purity Cu rod "similar to the aluminum rods") and #219 (the NAB run).
- **"Designed"** means every gram dissolves, as #222 uses the word. ICP/EDS on the powder measures recovery.
- **Weigh, don't trust volumes** (#222). The tapped densities set only the fill heights drawn.

**The 5N rod is Ø20 mm** (DAL #152), not 3/4 in. The cups here keep #222's 3/4 in profile, so they are the same
part in another metal. A 5N cup turned from Ø20 bar would be 0.95 mm larger across.

## What the chapter showed

- **A Cu cup is over the doser's load cell.** The cup alone is 106 g, and with its Ni 119 g. The rig's TAL221 is
  rated 100 g (powder-doser PR #185 `params.py`). Cu cups need a larger cell, about 300 g. The Al cup with its Si is
  36 g. The clip says so on screen while it doses a Cu cup.
- **The doser's catch funnel is wrong for a cup.** Its 18 mm spout is wider than the cup's 12.7 mm bore. To stand the
  cup with its rim at the spout, the vial cup on the load cell would have to be about 8 mm deeper. Here the cup is
  drawn there regardless (`alloy_charge.doser_seat_rig`). A cup station needs a spout under about 11 mm and a deeper
  holder.
- **The cup is captured between its holder and the funnel**, exactly as round 2 found for the vial. The arm slides it
  in level and 6 mm high, which the real funnel would not allow.
- **A cup is always held level.** It is picked, placed and carried with the fingers closing sideways, so its axis
  never tilts. That is why the rack has the cups in its front row: a level gripper reaches them from the front with
  its palm clear of the block.
- **The plugs are taken from above.** The 2F-85's pads are 38 mm long and a plug is 9.5 mm tall. The fingertips meet
  the plug's top 7.5 mm, 2 mm above the cup's rim.
- **The press has to open above the nest.** The arm sets the plug from above, and the gripper and wrist need about
  270 mm over it. So the nest slides out from under the ram for loading, and back in for pressing. A press-fit
  station's shuttle table is the usual answer.
- **The ram bottoms out on F1.** F1 is as long as the cup, so the plug ends flush with the rim (#222). The plug
  travels 8.0 mm after its lead-in seats it 1.5 mm into the mouth.
- **F1 makes a gripper problem.** With the plug flush, the cup is entirely inside the sleeve. The nest's ejector
  lifts it 36 mm so the gripper can take it.

## Assumed

- **The press:** a benchtop electric press with a shuttle nest and an ejector. It is 260 × 325 × 510 mm (frame and
  motor), with a 100 mm stroke above F1. No press-fit force is given, since #222 gives no interference for the plug.
  The lab's own press-fit station is a 1 t arbor press (#222 E4), worked by hand.
- **The rack**, the doser's cup holder and the MiR's carrier are printed blocks of this design. The carrier stands
  where round 2's one-vial holder stood.
- **Tapped densities of Ni, Fe and Cu powder**: 55 % of the solid. The Si and Al values are #222's.
- **The two powder modules**, Si in module 6 and Ni in module 3, are a choice. The multi-doser has 13.
- **The vent's puff** while the plug goes in is drawn only to show where the air leaves. Nothing was computed.

## Open questions

- Does the plug press-fit need F1 at all with 5N Al? 5N is much softer than 6063-T52, which also makes the cup's wall
  easier to bulge.
- How tight is the plug in a Cu cup? A Cu plug in a Cu bore needs the same interference as Al, or a new one.
- Should the cups be weighed on a separate balance after pressing, as #222 asks ("weigh it"), rather than on the
  doser's cell before the plug goes in? With a Cu cup, the doser's cell can't do it anyway.

## Revised on review (PR #318, 2026-11-04): the plug pressed home, in a vacuum press

Sterling: "the plug is supposed to be pushed in all the way such that the powder gets compressed to a certain
tonnage. Also, it would be better if it were a vacuum press". Both are now in the chapter
([`alloy_press.py`](../alloy_press.py), [`vacuum_press.md`](vacuum_press.md)):

- **The doses above compacted nothing.** They stood 18 mm (Si) and 25 mm (Ni) under the set plug. The bore is now
  tapped full to the set plug: the alloying powder, then a top-up of the cup's own metal. For Al-10Si that is 3.92 g
  Si and 3.91 g AlSi10Mg (itself 10 % Si). For Cu-10Ni it is 14.62 g Ni and 14.81 g Cu. See
  [`out/alloy_recipe_pressed.json`](../out/alloy_recipe_pressed.json).
- **The press is a Specac Atlas Autotouch 15T** with our evacuable die round F1. It replaces the assumed electric
  press with its shuttle nest:
  - the die is pumped below 1 mbar;
  - the plug goes 8.0 mm to flush on a 3.2 t program;
  - the powder goes from 52 to 63 % dense (Al) or 55 to 66 % (Cu);
  - the die is vented with dry Ar.
- **The plug goes in at the rack.** A gripper pointing down at the press's working height puts the wrist into the
  VLM's opening, and it couldn't follow the plug into the die's 31.8 mm bore anyway. The cup rides to the press with
  its plug in the mouth.
- **The press's own notes** answer "the press has to open above the nest" and "the ram bottoms out on F1" above.
  The shuttle carries the die out of the press to the arm, and the ejector pin raises the cup out of F1.
- **Collision-checked** (`collide.py`): 0 of 2752 frames.

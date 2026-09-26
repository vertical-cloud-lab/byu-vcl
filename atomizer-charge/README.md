# rePowder first-run charges: CAD, experiments, and parts for the prototyping lab

Issue [#222](https://github.com/vertical-cloud-lab/byu-vcl/issues/222). This folder has the Al cups, plugs, and slugs
for the first atomizer runs (#161), all turned from the 3/4" 6063-T52 bar that arrived on 2026-09-24
(McMaster [1640T16](https://www.mcmaster.com/1640T16/), 2 ft). The CAD is parametric
([build123d](https://github.com/gumyr/build123d), OpenCascade B-rep): change a dimension in
[`cad/charge_cad.py`](cad/charge_cad.py) and the STEP files, renders, masses, compositions, and shop drawing all
regenerate from it. The furnace, crucible, and sealing-rod specs it draws on, restated from AMAZEMET's and
Indutherm's manuals, are in [`repowder-reference/`](repowder-reference/README.md).

![Crucible cutaway with four standard cups](cad/renders/crucible_cutaway.png)

## How the parts get made

Three clips, generated from the same CAD by [`cad/machining.py`](cad/machining.py). Drilling is shown cut in half so
the hole is visible; the tool positions are the real ones, and each frame re-revolves the profile with the cut taken
so far.

| Turn the cup | Turn the lid | Load it and pump down |
| --- | --- | --- |
| ![Machining the cup](cad/anim/machining_cup.gif) | ![Machining the lid](cad/anim/machining_plug.gif) | ![Filling the cup and venting it](cad/anim/fill_and_vent.gif) |

The vent, in one line: **the chamber is pumped down before melting, so air shut under a solid lid has to leave through
the powder.** A Ø1/16" hole through the lid gives it somewhere else to go (#104).

**Before anyone makes cups, cut one P1 slug and try it in the crucible with the sealing rod fitted**
([why](#getting-a-slug-past-the-rods-adapter)), **and measure the crucible** ([what to measure](#measure-before-machining)).
The crucible dimensions below are scaled from a drawing, not measured.

## The crucible: documented vs. scaled

No vendor document dimensions the crucible. Indutherm's section of the same furnace (GU500 manual Fig. 61) is a CAD
drawing, though, so its proportions can be measured and scaled by one known length
([working](repowder-reference/crucible_proportions.py), [figure](repowder-reference/figures/crucible-proportions.png)).
Scaled to the quoted 225 cm³, it lands on all three numbers Bartosz gave on 9/17, so that is what the model uses.

| Quantity | Value in the model | Status | Source |
| --- | --- | --- | --- |
| Crucible | graphite, **225 cm³**. The 400 cm³ one is a separate upgrade that wasn't quoted | documented | AMAZEMET's quote ([reference §2](repowder-reference/README.md#2-answers-for-byu-vcl222)) |
| Melt delivery | pour hole in the floor, sealed by the sealing rod; melt is pushed out by a pressure differential | documented | AMAZEMET, [induction melting](https://www.amazemet.com/induction-melting-principle/); [9/17 call](../docs/meetings/2026-09-17-repowder-install/transcript.md) (20:12, 17:40) |
| Loading order | rod fitted and seated **first**, then the metal is weighed and filled around it. Never run without the rod | documented | GU500 pp. 15, 47–51 ([reference §4.2](repowder-reference/README.md#42-assembly-and-loading-order)) |
| Bore | **Ø57 mm** (was Ø52, inferred assuming a flat floor) | scaled | GU500 Fig. 61 at 225 cm³ |
| Sealing rod | **Ø12.6 mm**, ball tip seated round the pour hole (was Ø12) | scaled | same |
| Rod-to-wall gap | 22 mm | scaled; Bartosz said "around 20 mm" | same; 9/17 call, 20:12 |
| Floor | **a ~36° cone** down to a ~Ø7 pour hole, not flat | scaled | same |
| Depth | 81 mm of straight bore, 102 mm rim to the floor's apex. A charge may stand ~19 mm up into the filling cone on the rim, ~120 mm above the apex | scaled; Bartosz said "10–11 cm" and "12 cm" | same; 9/17 call, 21:21 |
| Rod adapter and arm | adapter ≈Ø22 over the axis, its bottom ≈18 mm above the rim; arm ≈47 mm above the rim | scaled, and the **least certain** number: the drawing shows the adapter's width along the arm only | same ([reference §4.3](repowder-reference/README.md#43-loading-clearance)) |
| Nozzle | **Not known for our unit.** The consumable pack lists "nozzles" with no size. Published rePowder work used a Ø0.7 mm hBN orifice; Indutherm's micro plates are 0.3, 0.5, and 1 mm, and 2 mm is its water-granulation hole | open | Ge et al. 2025; GU500 pp. 41, 48, 55 |
| Melt push | **200 mbar Ar over-pressure**, after 3 evacuation/Ar cycles to <50 ppm O₂; system pumps to 4×10⁻¹ mbar. The furnace allows −1 to +0.5 bar, and the pour pressure is programmed as a begin → end ramp | published; range documented | Ge et al. 2025; Ukabhai et al. 2025; GU500 pp. 18, 36 |
| Temperature | Type N thermocouple in a hole in the crucible wall, to 1300 °C. The furnace controls on the wall, so **the metal lags the reading** on heat-up | documented | GU500 pp. 18, 36 |
| Crucible coating | **BN spray on the graphite** is published rePowder practice. The vendor documents don't mention it | published | Ge et al. 2025 |
| Most Al it holds | ≈0.5 kg: the model gives 499 g to the rim, and the price list's 0.9 kg for 400 cm³ pro-rates to the same | derived | PL-2024 ([reference §2](repowder-reference/README.md#2-answers-for-byu-vcl222)) |
| Published charge sizes | 100 g Al/Cu pellets; 400–500 g discs + arc-melted bars | documented, published | Ukabhai et al. 2025; Ge et al. 2025 |
| Coil | 10 kW, 7 kHz; drawn schematically | power documented | GU500 p. 18 |

**Why Ø57 and not Ø52.** Ø52 came from putting 225 ml in a flat-floored cylinder 105 mm deep. The drawing's floor is a
cone, which holds less than a cylinder of the same depth, so the bore has to be wider to hold the same 225 cm³. Scaled
instead so the gap is exactly 20 mm, the drawing holds only 163 cm³.

## Getting a slug past the rod's adapter

The rod is seated before any metal goes in, and its adapter hangs over the middle of the crucible down to about the top
of the filling cone. Everything has to get past it, and that, not the rod-to-wall gap, is what limits the slug
diameter.

![Plan view: four cups fit around the rod, but the rod's adapter is in the way](cad/renders/crucible_top.png)

| Part | Straight down | Tipped in |
| --- | ---: | ---: |
| P1 / P2, 3/4" × 2.5" | −1.35 mm | **−0.09 mm** (−2.1 to +0.5) |
| the same, bar at its +.014" tolerance | −1.71 | −0.44 |
| P4, 3/4" × 1.25" | −1.35 | +1.08 (−1.2 to +1.8) |
| 5/8" × 2.5", for comparison | +1.83 | +3.10 |
| 1/2" × 2.5" | +5.00 | +6.28 |
| 5N Ø20 mm rod, 2.5" long | −2.30 | −1.04 |

*Room to spare; negative means it doesn't fit. From `loading_margin()` in [`charge_cad.py`](cad/charge_cad.py), the
same model as the reference's. Ranges in brackets span its three scalings of the drawing (20 mm gap, 225 cm³,
245 cm³).*

- **Straight down, no 3/4" part fits.** The band between the adapter and the wall is ≈17.7 mm, and the bar is 19.05.
- **Tipped in, it's too close to call.** With its foot against the rod and its top leaning away from the adapter, the
  tight moment is when the slug is ~45 mm into the bore. It misses by 0.09 mm, far inside the error of a scaled drawing.
- **So try one.** Cut a P1 first; E2 needs two anyway. With the furnace cold, the bell open, and the rod fitted and
  closed, hold the slug by its top and tip it in from the side away from the arm and the wall thermocouple. Once it is
  ~45 mm in and its top is below the adapter, it is past the tight spot; lift it back out the same way. Gloves (#126).
- **If it won't go in:** ask AMAZEMET whether the rod can stand in the pour hole on its own, with the adapter pinned on
  after loading, or be pulled and re-seated after loading. Either clears the mouth, but both are outside the documented
  order. Failing that, 5/8" bar goes straight in with 0–2.3 mm to spare, but the cups would need resizing.
- **AMAZEMET's 4047 benchmark rods** are their own answer to what fits: note their diameter, and how they load them.

The documented sequence, for the first run (GU500 pp. 34, 42, 47–51): crucible, filling cone, wall thermocouple, then
the rod fitted and seated; metal in around it; close the bell; evacuate and backfill (Indutherm says one cycle for
usual alloys, the published rePowder work did three); heat under argon. Open the bell only below 500 °C.

## Rods around the piston, or one ring over it?

- **Four 3/4" slugs fit around the rod, with room to spare.** They sit 3.3–7.9 mm apart depending on which way they
  lean, and still ≥3.2 mm apart at 600 °C: Al grows ~1.4 % by then, graphite ~0.3 %. Five fit too, 3.3 mm apart
  pushed out to the wall, though they can't all touch the rod at once; six overlap even cold. (In the old Ø52 model,
  five didn't fit.) The floor cone rises towards the wall, so each slug stands on the outer edge of its base and leans
  a degree or so onto the rod.
- **You don't need a full crucible.** AMAZEMET's [FAQ](https://www.amazemet.com/faq/) puts the input at "a few to a
  few hundred grams". What limits the charge is the minimum melt for a steady pour, not crucible volume. Two slugs make
  80–100 g, which is the 100 g/run basis of the #161 purchase model. Four slugs make ~175 g. The crucible would hold
  ~500 g of liquid Al.
- **The ring over the rod** ([render](cad/renders/ring_concept.png)) is now ruled out by the documented procedure, not
  just by cost. The rod is seated before the metal goes in, the ring's Ø16 hole can't pass the ≈Ø22 adapter, and the
  furnace must never run without the rod. It would need AMAZEMET to allow fitting the rod after loading. It also doesn't
  add capacity. Powder capacity comes from wall thickness, not from ring vs. rods: the ring holds 37 cm³ of powder,
  while four 3/4" × 100 mm thin-wall cups would hold 73 cm³. On top of that, the ring needs a 2" bar (a 5N Ø50 bar
  costs far more than Ø20), a trepanning cut, and a rotary stage to dose into. Identical slugs stand in a rack and dose
  like vials.
- **So: repeat slugs.** Separate slugs also cover Bartosz's caveat. If a powder cup doesn't fully melt, rerun it as one
  cup plus one solid slug, so that part of the charge is already molten when the powder is released. Indutherm's own
  charge is short cut pieces dropped in around the seated rod ([photo](repowder-reference/README.md#43-loading-clearance)).

## Experiments

Two slugs per run by default. The insets share one scale, so a smaller picture is a smaller part. Powder masses assume
tapped densities (AlSi10Mg 1.60, Si 1.10, re-atomized 6063 1.65 g/cm³). **Weigh; don't trust volumes.**
"Designed" composition is what you get if every gram dissolves, so ICP/EDS on the powder against it measures recovery.

| | Run | Tier | Per run | Fill per cup (weigh it) | Charge / run | Powder | Designed | What it tells you |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| <img src="cad/renders/insets/E1_alsi10mg_cup.png" width="80"> | **E1** AlSi10Mg in a cup, plug on top | first | 2 × P2 + P3 | 8.0 g AlSi10Mg, tapped to the plug line | 86 g | 18.5 % | Al-2.2Si-0.6Mg | Does powder inside Al melt fully? |
| <img src="cad/renders/insets/E2_solid_slug.png" width="80"> | **E2** Solid 6063 (control) | first | 2 × P1 | — | 97 g | 0 % | 6063 (Al-0.4Si-0.7Mg) | Baseline yield / PSD. **Run before E6**, which uses its powder |
| <img src="cad/renders/insets/E3_mix_cup.png" width="80"> | **E3** AlSi10Mg + Si, plug on top | first | 2 × P2 + P3 | 3.75 g Si + 2.52 g AlSi10Mg, **premixed** | 83 g | 15.1 % | **Al-10Si-0.6Mg**: AlSi10Mg's Si | Si recovery. Compare with commercial AlSi10Mg and the arc-melted batch (#223) |
| <img src="cad/renders/insets/E4_pressed_in_sleeve.png" width="80"> | **E4** AlSi10Mg, plug pressed hydraulically | handy | 2 × P2 + P3, pressed in F1 | 9.9 g AlSi10Mg filling the whole bore, then plug pressed flush (≈75 % dense) | 90 g | 22 % | Al-2.5Si-0.6Mg | Does compaction help (#104)? |
| <img src="cad/renders/insets/E5_si_cup.png" width="80"> | **E5** Si only | handy | 2 × P2 + P3 | 4.64 g Si (leaves ~6 mm headspace) | 80 g | 11.6 % | **Al-12Si**, same as the Al 4047 benchmark rods | Si dissolution, compared directly with AMAZEMET's 4047 |
| <img src="cad/renders/insets/E6_al_powder_cup.png" width="80"> | **E6** Re-atomize our 6063 powder | handy | 2 × P2 + P3 | 8.2 g of E2's powder | 87 g | 19 % | 6063 | Powder melting with no composition change. Also O pickup per pass |
| <img src="cad/renders/insets/E7_thin_cup.png" width="80"> | **E7** Small batch, thin-wall cup | later | 1–2 × P4 + P5 | 7.5 g AlSi10Mg | 19 g per cup | 39.5 % | Al-4.2Si-0.55Mg | How small a charge still pours. Thin wall = less oxide skin ([#161 Edison note](https://github.com/vertical-cloud-lab/byu-vcl/issues/161#issuecomment-5593664416)) |

Cups stand **plug up**, so the powder drops into metal that is already liquid and the vent points up. E1, E3, E5, and
E6 use the plug to close the cup, not to compact it: the powder is tapped to the plug line first. E4 is the compaction
test.

**The pour runs on the argon over-pressure, not on the melt's weight.** The melt fills the floor cone first, so two
slugs stand 28–31 mm over the pour hole (`melt_depth_mm` in [`experiments.json`](cad/experiments.json)). That is only
~7 mbar of head. Pushing liquid Al into a 0.7 mm hole it doesn't wet takes ~50 mbar (2γ/r, ignoring the oxide skin,
which only adds to it; 35 mbar at 1 mm, 70 at 0.5). Even a full ~0.5 kg charge gives only 23 mbar, so with any
sub-millimetre nozzle the charge size doesn't change this, and the published 200 mbar does the work. The same 2γ/r
reproduces Indutherm's own start pressures for bronze (reference [§4.5](repowder-reference/README.md#45-nozzle-and-flow)).
The cone helps small charges: E7's 38 g still stands 21 mm over the hole.

## Parts for the prototyping lab

Dimensioned drawing: [`cad/drawings/charge_parts.pdf`](cad/drawings/charge_parts.pdf) (1:1 on Letter at 100 %,
plugs 3:1), with a [PNG preview](cad/drawings/charge_parts.png). STEP: [`cad/step/`](cad/step). GitHub renders the
[STL files](cad/stl) in a 3D viewer, including a
[cutaway of the crucible with four cups](cad/stl/crucible_cutaway_4x_std_cup.stl).

| | Part | Key dimensions, inches [mm] | E1–E3 (bar on hand) | E4–E7 | Mass |
| --- | --- | --- | ---: | ---: | ---: |
| <img src="cad/renders/insets/P_solid_slug.png" width="72"> | **P1** Solid slug | Ø.750 as received × 2.500 [63.5], .02 × 45° ends | 2 | — | 48.7 g |
| <img src="cad/renders/insets/P_std_cup.png" width="72"> | **P2** Standard cup | Ø.750 × 2.500; Ø.500 bore 1.875 [47.6] deep to full Ø (118° point OK); drill 31/64, then bore or ream; 1/8" wall | 4 + 1 spare | 6 | 32.0 g |
| <img src="cad/renders/insets/P_std_plug.png" width="72"> | **P3** Plug for P2 (shown ~3×) | Ø = **that cup's measured bore + .0005–.0008**; .375 [9.5] long; Ø1/16" vent through; 15° lead-in on the nose; .015 break on the top, deburr only | 4 + 1 spare | 6 | 3.1 g |
| <img src="cad/renders/insets/P_thin_cup.png" width="72"> | **P4** Thin-wall cup | Ø.750 × 1.250 [31.75]; Ø.625 flat-bottom bore 1.125 deep; 1/16" wall, 1/8" floor | — | 2 | 9.1 g |
| <img src="cad/renders/insets/P_thin_plug.png" width="72"> | **P5** Plug for P4 (shown ~3×) | Ø = measured P4 bore + .0005; .1875 [4.76] long; vent; lead-in | — | 2 | 2.5 g |
| <img src="cad/renders/insets/F_support_sleeve.png" width="72"> | **F1** Press support sleeve (1018 cold-finished, ASTM A108) | Ø1.250 × 2.500; bore = **measured P2 OD + .0005 max**, line-to-line is better | — | 1 | 252 g |

**Bar budget.** Each piece uses its length plus ~3 mm for kerf and facing, and ~25 mm is left as a chucking
remnant. E1–E3 plus a spare cup set take 528 of the 585 usable mm of the bar on hand. E4–E7 need 559 mm, so order
**one more 1640T16**: 2 ft ($21.65) just covers it, and 4 ft ($36.08) leaves room for re-dos (prices as of 9/17). At one
slug per run, all seven runs fit in the bar on hand (504 mm).

**Machining rules that matter** (also on the drawing):

1. **Cup first, then plug.** Measure each cup's bore and turn its own plug to **+.0005–.0008"** over it, never
   more. `fit_check()` in [`charge_cad.py`](cad/charge_cad.py) works this out from Lamé rather than asserting it,
   and lands in `parts.json`. At .0008" the contact pressure is 30.7 MPa and P2's 1/8" wall sees 79.7 MPa hoop at
   the bore, **98.7 MPa von Mises — 0.90 of 6063-T52's 110 MPa minimum yield**. The elastic ceiling is **.00089"**.
   *The old .001" limit was wrong*: hoop alone understates the bore by 24 %, and at .001" von Mises is 123 MPa,
   1.12× yield. Press force at .0008" is **1.3–1.6 t** (µ 1.05–1.35 static for dry Al on Al — 0.4 is the sliding
   value and it is breakaway that sizes the press). Reserve 2 t. The thin cup P4 is elastic to .0011".
2. **Every plug is vented** (Ø1/16" through the axis). Gas sealed in with the powder has nowhere to go until the cup
   melts, which is the melt-ejection risk flagged in #104 and PR #134. The chamber is also pumped down before melting.
3. **Slug OD ≤ measured rod-to-wall gap − 0.7 mm**, because Al outgrows graphite on heating, **and it has to get past
   the rod's adapter**, which is the tighter limit ([above](#getting-a-slug-past-the-rods-adapter)). The gap now
   looks like ~22 mm, which the 3/4" bar clears, and so would the 5N Ø20.0 rods. The adapter is what may force
   either to be turned down.
4. No marker ink, scribing, or stamping on the parts. Degrease in IPA, dry, weigh each part to 0.01 g, and label the
   bag.

## Every size is a stock size

Checked on 2026-09-25, because a drawing that calls out a size nobody stocks turns a two-day job into a two-week
one. Three dimensions were not standard and were changed; the rest were already right.

| Dimension | Standard? | Governing standard |
| --- | --- | --- |
| Ø3/4" 6063 bar | ✅ stock, on hand | ASTM B221 extruded bar |
| Ø.500 bore, Ø.625 bore | ✅ both standard chucking-reamer sizes | ASME B94.2 |
| 31/64 pilot drill before the Ø.500 bore | ✅ fractional; leaves .0156" total stock, which is Machinery's Handbook practice for a 1/2" reamer | ASME B94.11M |
| 118° drill point left in the cup bottom | ✅ general-purpose point | ASME B94.11M |
| Lengths 2.500 / 1.875 / 1.250 / .375 / .1875 | ✅ all on the inch scale | — |
| 15° press-fit lead-in | ✅ 10–15° is the recommended lead-in | ANSI B4.2 |
| .0005–.001" interference on a Ø.500 bore | ✅ top of **FN1**, the class ANSI B4.1 designates for *"thin sections or long fits"* — which is exactly a 1/8" wall | ANSI B4.1 |
| ~~Ø1 mm vent~~ → **Ø1/16"** | ⚠️ changed. A metric bit isn't in a US fractional/number index, and at .375" deep a 1 mm bit is 9.5×D where 1/16" is 6×D. #60 (.040") is the alternate if 1/16" looks too big | ASME B94.11M |
| ~~0.5 / 0.3 mm chamfers~~ → **.020 / .015"** | ⚠️ changed. The sheet was mixing mm and inch callouts, which is how a part gets made wrong | — |
| ~~Ø2.000" F1 sleeve, bore +.001–.002"~~ → **Ø1.250", bore +.0005" max** | ⚠️ changed, see below | 1018 CRS stock size |

**Why F1 shrank, and why its bore got tighter.** The cup's OD grows only **.00059"** before its bore reaches
yield (same Lamé calculation, in `fit_check()`, with the von Mises check; hoop stress alone gives .00074"). A
.001–.002" slip fit therefore never touches the sleeve until after the cup has already started to yield — the sleeve
was decorative. Bored to +.0005" it actually takes load, just.
And it doesn't need to be 2": .25" of 1018 over a .750" bore sees ~30 MPa hoop at 100 MPa bore pressure, nowhere
near its ~370 MPa yield. Ø1.250" is a stock size, weighs 252 g instead of 870 g, and is less boring.

**One thing to watch, not a change.** A 1/2" chucking reamer's flute is 2.000" (ASME B94.2) and the bore is
1.875" deep, so a standard reamer only just reaches, with no room for chips. Single-point boring has no such limit
and gives a measured bore, which is what the plug is matched to anyway. The drawing now says *bore or ream*.

## Independent review (Edison, 2026-09-25)

Two FutureHouse/Edison crows were run against this folder — a literature crow on the metallurgy and an analysis
crow on the arithmetic. Raw answers and task ids are in
[`outputs/issue-222-edison-doublecheck/`](../outputs/issue-222-edison-doublecheck). What they changed:

**Confirmed, unchanged:** the Lamé contact pressure and hoop stress; the 0.00074" hoop-only OD growth; every
standard size above; the 2.000" reamer flute; four slugs fit and five do not (five need a 16.205 mm pitch radius
cold and 16.432 mm hot, against 16.420 mm available — 0.012 mm interference even pushed outward) — in the Ø52 model
it was given, since superseded by the Ø57 scaling above; Al ≈1.4 % and graphite ≈0.3 % linear growth to 600 °C; BN
wash on graphite is published rePowder practice.

**Corrected, and now in the files:**

| Was | Now | Why |
| --- | --- | --- |
| .001" interference ceiling | **.0008"** | Yield is von Mises, not hoop alone. At .001" the bore is (−38.3, 99.7, 0) MPa → **123.4 MPa von Mises, 1.12× yield**. Elastic ceiling .00089" |
| µ 0.4–1.2, press 0.6–1.8 t | **µ 1.05–1.35, 1.3–1.6 t** | 0.4 is *sliding* Al-on-Al; breakaway is what sizes the press. Reserve 2 t |
| F1 keeps the cup elastic | **It doesn't, and can't** | Even line-to-line, at E4's ~100 MPa bore pressure the Al bore is at 152 MPa von Mises; it first yields at ~73 MPa. The steel is fine (147 MPa von Mises against ~345 MPa). **F1's job is to bound the OD, not prevent set** — so gauge each cup's OD after pressing and before it goes near the crucible |
| "mild steel" | **1018 cold-finished, ASTM A108** | Round bar isn't cold *rolled* |

**Not changed — our numbers are right.** Edison's masses (cup 32.46 g, lid 3.20 g, slug 48.69 g) are higher than
ours (31.98 / 3.15 / 48.65) because it worked from nominal dimensions and said so: it ignored the .020 edge
breaks and the 118° drill point that the CAD actually cuts. The CAD volumes stand.

### Metallurgy flags — these are for #161, not for the machinist

Ranked by how much they would change the plan:

1. **Elemental Si may not dissolve in time (E3, E5).** Si melts at 1414 °C, so at 700–850 °C it *dissolves*,
   mass-transfer limited. Measured: Si cylinders at 738 °C were only **29–44 % dissolved after 2–3.5 min**.
   Raising superheat 40→80 °C bought ~30 % on the mass-transfer coefficient; stirring bought more. Edison's
   recommendation is **AlSi50 master alloy** instead, or coarse clean granules added below the surface with a
   validated hold. Undissolved Si in front of a **Ø0.7 mm nozzle** is the failure mode. The furnace maker's own rule,
   written for water granulation but the nearest thing to vendor guidance: at least 50–80 °C of superheat, and a hold
   of ≥5 min once fully molten, **10 min when alloying in the furnace** (GU500 pp. 42–45). The reading is the
   crucible wall's, so while it heats the metal is cooler than the display says.
2. **Powder inside a cup melts, but not necessarily clean (E1, E4, E6, E7).** Every particle carries an alumina
   skin that does not dissolve in the melt; opposed skins make Campbell bifilms. Gas-atomised powder also holds Ar
   and adsorbed moisture, and liquid Al dissolves ~15× the hydrogen that solid Al does. Standard practice is
   vacuum degassing at 350–450 °C before consolidation — which the sealed cup has no path for. Remelting
   high-surface-area Al (chips) recovers only 60–83 % without flux, ~90 % with good Ar practice; powder is worse.
3. **The vent is a compromise, and Edison flags both sides of it.** Sealed, the capsule can pressurise; open, the
   Ø1/16" hole can aspirate powder during pump-down and can wick liquid Al under the 200 mbar Ar over-pressure.
   It specifically contraindicates **E4** — hydraulic compaction of a near-sealed capsule removes the interparticle
   volume the gas needs. A sintered or labyrinth plug above the metal line is the proper fix if we keep going.
4. **The cup is most of the charge.** At ~35 g of 6063 around 8–10 g of powder the cup is ~80 % of the slug, so it
   sets Si, Mg, Fe and Cu. Already in the mass balance here, but Mg also *leaves*: it oxidises and evaporates
   above ~700 °C (−7.8 % over ten LPBF cycles for AlSi7Mg, and worse in a small melt). Treat the designed Mg as an
   upper bound. The furnace melts under argon above 500 °C (it starts flushing the crucible with protective gas there
   by default), which keeps that loss slow; a melt held hot under vacuum would lose its Mg far faster.
5. **Don't pre-specify a re-atomisation pass count (E6).** No Al-specific per-pass oxygen number exists. Proxies:
   AlSi10Mg LPBF reuse adds ~0.005 pp O per build against a 0.2 wt % limit; ultrasonic atomisation of Ti chips
   added ~220 ppm. Full remelt makes fresh droplet surface, so expect more. Measure O by inert-gas fusion each pass.
6. **Sequencing.** Run AMAZEMET's own solid **Al 4047 benchmark rods first**, then the solid control (E2), then
   one powder cup with full post-run chemistry — before E3–E7 add variables. Watching the 4047 rods go in past the
   rod's adapter answers the loading question as well.
7. **E7's 1.6 mm wall** may melt through or collapse before its powder has melted. Unverified.
8. **Crucible geometry is still unverified.** Edison searched and found **no** published rePowder crucible bore,
   sealing-rod diameter, or 4047 rod dimensions, and the vendor documents don't dimension it either. The model now
   uses Indutherm's drawing scaled to 225 cm³ (Ø57 / Ø12.6, a ~22 mm gap). That answers Edison's other point, that a
   Ø19.05 cup in a 20 mm gap leaves almost nothing for expansion and gas flow, but puts the rod's adapter in the way
   ([above](#getting-a-slug-past-the-rods-adapter)).

## Filling a cup

1. Dry the powders at 80 °C for ≥10 h (#161). Fill in the clean powder area with the usual PPE (#126).
2. Weigh the cup + plug pair. For E3, premix the Si and AlSi10Mg in a vial first.
3. Weigh the powder into the cup, tapping as you go. Stop at the target mass or the plug line, whichever comes first,
   and record the actual mass.
4. Press the plug flush in the soft-jaw vise or arbor press. For E4, stand the cup in F1 on a flat plate and use the
   hydraulic press, ~3–4 t (≈1.3 t to compact the powder plus ≈1.3–1.6 t of press fit). F1 is the cup's length, so
   the platen bottoms out at flush. Push the cup out through F1 with a 5/8" drift. Don't clear the vent with
   compressed air (#126).
5. Weigh the loaded cup: that mass balance gives the true powder fraction. Store sealed with desiccant (#30, #230).

## Measure before machining

The crucible is reachable now: Bartosz: "if you move the foam out you can see the crucible" (9/17 call, 20:12). Wear
gloves (#126).

1. **Try a P1 slug past the rod's adapter** ([how](#getting-a-slug-past-the-rods-adapter)). If it goes in, the rest
   of this list refines the model. If it doesn't, stop before making cups.
2. **With the rod fitted and closed:** the adapter's width both ways, the heights of its bottom and of the arm's
   underside above the filling cone, and where the arm and the wall thermocouple sit around the mouth.
3. **Crucible bore** at the rim and just above the floor cone (graphite crucibles are often tapered).
4. **Sealing-rod OD**, and its tip: a ball, or a cone, and how it seats in the pour hole.
5. **Depth** from the rim down to the floor cone beside the rod; the filling cone's thickness; and the height from its
   top to the closed bell. Is ~120 mm above the floor really available?
6. **Which nozzle shipped**, and what is in the "Induction 225 cm³ consumable pack": how many crucibles and rods, and
   the nozzle sizes. AMAZEMET's quote settles 225 vs. 400 ml; the packing list confirms it.
7. **The Al 4047 benchmark rods** AMAZEMET shipped: diameter, length, how many make a run, and how they are meant to go
   in past the adapter. That is AMAZEMET's own answer to "what fits" and "what's the minimum charge".
8. **For AMAZEMET or Bartosz:** the minimum charge for a steady pour; whether the rod can be seated with the adapter
   pinned on after loading, or pulled and re-seated (a 3/4" fallback and the ring concept both depend on it); whether
   a BN wash on the graphite is standard for Al (#161 Edison note); and the superheat they use for Al. The reference
   lists the documents to ask for at the same time ([§13](repowder-reference/README.md#13-documents-to-request)).

Change `CRUCIBLE_ID`, `SEALING_ROD_D`, `BORE_STRAIGHT`, `FLOOR_CONE_H`, `ROD_ADAPTER_D`, `ROD_ADAPTER_ABOVE_RIM`, or
`STOCK_D` in `charge_cad.py` and re-run to update everything.

## Regenerating

```bash
pip install build123d pyvista matplotlib   # tested: build123d 0.13.0, pyvista 0.49.0, VTK 9.7.0
cd atomizer-charge/cad
python charge_cad.py          # step/, stl/, parts.json, experiments.json (masses, compositions, bar budget)
xvfb-run -a python render.py  # renders/ (VTK needs a display; xvfb-run on a headless machine)
python drawings.py            # drawings/charge_parts.pdf + .png
xvfb-run -a python machining.py  # anim/*.gif (also needs pillow)
```

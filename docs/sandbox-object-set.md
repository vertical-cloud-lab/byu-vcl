# Sandbox object set for the PiPER arm

Working notes for [issue #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199),
answering "use Edison, web search, and intuition to define a list of common objects we'd
put in the sandbox". The sandbox is the one sgbaird sketched
[on #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199): the PiPER plus
relevant samples and holders, namely SEM stubs, filled and empty vials, well plates, and
aluminium crucibles and lids for the press-fit and atomizer-transfer steps. There is also
an A1 mini nearby. It now has a home: a quarter-dome enclosure on a second table at spot D
in CB154 ([#229](https://github.com/vertical-cloud-lab/byu-vcl/issues/229)).

Sources, in the order they were used:

- **The org's own threads.** Every issue, PR, and comment across the 13 repos in
  `vertical-cloud-lab`, plus `borysgroup/aurora-cloud-infra`, read for objects that are
  actually handled here.
- **A census of 38 published arm-based lab systems**, recording what their arms pick up.
- **Vendor and standards sheets** for dimensions.
- **Edison Q5** ([`edison-6dof/q5-sandbox-object-set/`](edison-6dof/q5-sandbox-object-set/)).

Where the list is judgement rather than citation, it says so.

## Why a list matters more than it sounds

Q4 said *no published physical laboratory-object manipulation benchmark exists*
([Q4 §3.3](edison-6dof/q4-closed-loop-design-protocol/answer.md)). That is now too strong.
Real-robot laboratory benchmarks appeared in 2026:

- [**LabDex**](https://arxiv.org/abs/2608.18618) (19 Aug 2026) unifies real and simulated
  chemistry-lab manipulation, on a Franka with a dexterous hand.
- [**WetRobo**](https://arxiv.org/abs/2609.18435) (16 Sep 2026) is a reproducible kit built
  on **one AgileX PiPER** with a string-driven Dynamixel gripper, according to its
  [README](https://github.com/tsudalab/WetRobo). Its three tasks are lifting a Petri-dish
  lid, lifting a bottle cap, and opening an incubator door.

What still does not exist is **a buyable labware object set** with per-object part numbers,
masses, meshes, and protocols — a "YCB for labware". LabDex describes its objects only in
words, and WetRobo has three objects and no parts list. The laboratory benchmarks that do
ship assets are all simulation-only: AutoBio, LabUtopia, Labimus, Chemistry3D, and MATTERIX.

So this list is the sandbox's shopping list, and it is also the first draft of that missing
set. It is written like one, so another lab could buy the same things. It is also what
every protocol in the arc needs:

- the reliability campaign (Q2)
- the compliance-vs-precision map and the generative-gripper loop (Q3)
- the finger-vs-arm attribution design (Q4)

## What the stock gripper rules in and out

The object list is shaped by the PiPER's gripper more than by the arm. The figures below
come from the [user manual](https://static.generation-robots.com/media/agilex-piper-user-manual.pdf),
as tabulated on [the enclosure branch for #229](https://github.com/vertical-cloud-lab/byu-vcl/blob/fc1bc5a/robot-arm/enclosure/README.md).

| | Value | What it means for the object list |
|---|---|---|
| Jaw opening | **0–70 mm** (a 100 mm variant exists; the SDK has a 70/100 mm setting) | An SBS plate's footprint is 127.76 × 85.48 mm, and even its top is ~83 mm wide, so **the stock fingers cannot grip one across any side.** Every vial, stub, cup, and coupon fits. |
| Grip force | 40 N rated, 50 N max | Ample for glass vials. Enough to crush an aluminium DSC pan, a weighing dish, or a PS weigh boat, so those need force-limited or compliant fingers. |
| Gripper repeatability | ±0.5 mm | Five times the arm's claimed ±0.1 mm. At the fingertip, the gripper dominates. |
| Gripper mass | 0.5 kg | If the 1.5 kg rating is at the flange, about 1 kg is left for fingers and object. No Tier 1 object exceeds ~0.25 kg (the steel press sleeve), so payload is not a constraint. |
| J6 range | **±100°** | 200° of wrist roll in total. A 24-400 cap needs about a full turn to come off, so **uncapping needs at least two regrasp cycles** and a fixture that resists the torque. |
| Fingertip offset | ~140 mm past the flange | Sets the approach clearance for deep holders and the balance draft shield. |

**The well plate is the forcing function for custom fingers**, and it makes a crisp first
design problem for the generative-gripper loop (Q3 rank 1): *one finger pair, on a 0–70 mm
parallel gripper, that holds a 12 mm vial and an 85.48 mm plate.* Stepped fingers do it.
The fingertip faces sit inward of the jaw by *a* and handle small objects over a 0–70 mm
range. A recessed zone behind them sits outward by *b* and spans 2(*a*+*b*) to
2(*a*+*b*) + 70 mm. With *a* + *b* = 10 mm, the recessed zone covers 20–90 mm, which is the
plate's short side with room to spare. The catch is that the fingertips then hang below the
plate. So the plate has to sit on a raised nest narrower than its footprint, which is how
commercial plate hotels solve the same problem. The alternative is simply buying the 100 mm
gripper. Zwirnmann et al.
([IROS 2023](https://arxiv.org/abs/2302.03644)) show how tight this is even on a bigger
gripper. The Franka Hand's travel is 83 mm, and they grasp a 96-well plate across its
**83 mm top width**, above the wider skirt. That only works because their fingers are
built to touch exactly when closed, so no travel is lost to finger thickness. The PiPER's
70 mm falls 13 mm short even of that. Their monolithic dual-extrusion PLA/TPU fingers cover
containers from 6 mm microtubes to well plates, sorted by a mass → width → lid-type
taxonomy. They are the closest published precedent for one finger set across a labware
range.

## How objects were chosen

YCB's authors picked objects that span shape, size, texture, weight, and rigidity, and
that are cheap, widely available, durable, and portable
([Calli et al. 2015](https://arxiv.org/abs/1502.03143)). The same logic, adapted to a
materials lab, gives five tests. An object earns a Tier 1 slot if it passes the first and
at least two of the others:

1. **It rehearses a real transfer step here.** Atomizer feedstock, powder dosing, SEM,
   OT-2 liquid handling, printed coupons. An object nobody here touches does not belong in
   the core, however common it is elsewhere.
2. **Published SDL arms handle it**, so a success rate on it is comparable to someone
   else's (census below).
3. **It exercises a property axis** that breaks grasps or placements: transparent,
   specular, small, thin, crushable, wide, fill-dependent, two-part, or seat-into-fixture.
   Every axis should be hit by **at least two** objects, so no conclusion rests on one
   part.
4. **It is buyable by part number**, cheap, and either durable or cheap to replace. For
   consumables that deform in use (a pressed plug, a crimped pan), the list states the
   per-trial cost.
5. **It is safe to run unattended.** Filled objects use sealed caps, and open powder and
   open liquid stay out of the arm cell until the unattended-operation safety question is
   settled. That question went to Edison as `8ac9a19f` from the sibling
   `claude/issue-199-20260915-0844` branch and has not been fetched yet.

## Tier 1 — the core set (15 objects, buy or make now)

Almost everything here already exists in the lab, or costs little. Specs marked *(typical)*
are catalogue norms rather than measured values. Weigh and caliper five of each on arrival
(see [the object record](#what-each-object-record-should-carry)).

| # | Object | Spec | Why it's in | Exercises |
|---|---|---|---|---|
| 1 | **Atomizer charge cup** (P2) — empty, and charged with surrogate powder + plug | 3/4" (19.05 mm) 6063-T52 bar ([McMaster 1640T16](https://www.mcmaster.com/1640T16/)), 63.5 mm long, Ø12.7 × 47.6 mm bore. **32.0 g** empty, ~40–45 g charged (4.6–9.9 g of powder + the 3.1 g plug) | Going by [#104](https://github.com/vertical-cloud-lab/byu-vcl/issues/104) and #222, this is #199's "aluminium crucible and lid". It is atomizer feedstock, not labware: it melts with the powder, so it is consumed every real run ([#222](https://github.com/vertical-cloud-lab/byu-vcl/issues/222#issuecomment-5822478482), [PR #232](https://github.com/vertical-cloud-lab/byu-vcl/blob/323adba/atomizer-charge/README.md)). "Identical slugs stand in a rack and dose like vials." | specular · fill-dependent · **tipped insertion** past the sealing-rod adapter. The model gives **−0.09 mm** of margin, too close to call |
| 2 | **Vented press-fit plug** (P3) | 6063, Ø12.7 mm + interference, 9.5 mm long, **3.1 g**, Ø1/16" vent | The press-fit step. The fit takes **1.3–1.6 t** on an arbor press or vise, so the arm *starts* the plug and loads the press; it cannot press ([PR #232](https://github.com/vertical-cloud-lab/byu-vcl/blob/323adba/atomizer-charge/README.md)) | small · specular · two-part |
| 3 | **Solid slug** (P1) | Ø19.05 × 63.5 mm, **48.7 g** | The same outline as #1 with no bore and no fill, so object variability drops to the bar tolerance. It is the **reference object** for separating arm and finger error from object error (Q4) | specular · reference |
| 4 | **Press sleeve** (F1) | 1018 steel, Ø31.75 × 63.5 mm, **252 g** | The cup goes into it before pressing. It is the heaviest real object in the chain | heavy · specular · seat |
| 5 | **100 mL Griffin beaker** | glass, ~50 × 70 mm *(typical)*. Must be ≤3" tall to clear the HR-100A breeze break | The doser's current receiving vessel. **Emptying it is the only step the doser's optimization loop blocks on** ([powder-doser#164](https://github.com/vertical-cloud-lab/powder-doser/issues/164#issuecomment-5782367692), [#116](https://github.com/vertical-cloud-lab/powder-doser/issues/116#issuecomment-5347262222)) | transparent · breakable · open-top spill · reach under a draft shield |
| 6 | **Auger module** | PLA tube Ø25 × 250 mm with a 48-tooth Ø50 gear; **56.7 g** empty, ~0.2 kg full. 16 full-size and 9 short already printed | Auger exchange is the pick-and-place job [powder-doser#128](https://github.com/vertical-cloud-lab/powder-doser/issues/128#issuecomment-5145184675) wanted a gripper for ([#131](https://github.com/vertical-cloud-lab/powder-doser/pull/131#issuecomment-5124314682), [#134](https://github.com/vertical-cloud-lab/powder-doser/issues/134#issuecomment-5183033746)) | long · heavy · fill-dependent · keyed seat (gear mesh) |
| 7 | **SEM pin stub** | Al, Ø12.7 mm head, Ø3.2 × 8 mm pin, ~1 g. [Ted Pella 16111](https://www.tedpella.com/SEM_html/SEMpinmount.aspx), $27.50/50; 100 on order | #199's list and [#49](https://github.com/vertical-cloud-lab/byu-vcl/issues/49). The polished face must never be touched ([caliber#6](https://github.com/vertical-cloud-lab/caliber/pull/6#issuecomment-5623520309)), so fingers grip the rim or pin | small · specular · 3.2 mm pin-in-hole |
| 8 | **20 mL glass vial, 24-400** — empty, powder-filled, water-filled (sealed) | 28 mm OD, ~57.5 mm body *(typical)*. **Use 24-400, not 22-400.** The CubXL's 28.2 mm magnetic caps need it ([#147](https://github.com/vertical-cloud-lab/byu-vcl/issues/147#issuecomment-4918503560), [#151](https://github.com/vertical-cloud-lab/byu-vcl/issues/151#issuecomment-5185560271)), and the two caps don't interchange | Vials are the **#2 object class** in the census (12 of 38 systems). The 20 mL size matches the YuMi PXRD workflow of Lunt et al. | transparent · fill-dependent · slosh · cap (uncap needs regrasps: J6 is only ±100°) |
| 9 | **2 mL autosampler vial** | 12 × 32 mm (Agilent 5182-0714) or 11.6 × 32 mm ND9 (Macherey-Nagel), ≤3 g | The size Ada and the Hein lab handle, so success rates are directly comparable | small · transparent |
| 10 | **15 mL conical tube** | PP, ~17 mm OD × ~120 mm (Falcon 352096). Caps are wider than the body: 22.3 mm on Eppendorf's | The OT-2's stock-solution tubes in the AC 6-tube rack ([#64](https://github.com/vertical-cloud-lab/byu-vcl/issues/64#issuecomment-4007871843)). Tubes are census class #7 | translucent · long · cap wider than body |
| 11 | **96-well plate** — empty, and sealed with water | NEST 200 µL flat (`nest_96_wellplate_200ul_flat`), 127.56 × 85.36 × 14.3 mm | The OT-2 plate in use ([digital-wetlab#8](https://github.com/vertical-cloud-lab/digital-wetlab/pull/8)). **Wider than the 70 mm gripper**, so it is the first custom-finger problem | wide · slosh · seat into a 128.0 × 86.0 mm OT-2 slot, snug rather than clearance |
| 12 | **OT-2 20 µL tip rack** | 127.76 × 85.48 × 64.69 mm | The P20 rack in slot 2 ([PR #118](https://github.com/vertical-cloud-lab/byu-vcl/pull/118)). A second SBS object, tall with a high centre of gravity | wide · tall · seat |
| 13 | **Tensile coupons**: a PETG replica of the lab's LPBF dog-bone, and an ASTM D638 Type V | Dog-bone 100 × 10 × 6 mm with a 32 × 6 mm gauge ([#77](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4314505474)). Type V ≥63.5 × 9.53 mm, 3.18 mm neck, ≤4 mm thick | Coupon-into-grip is Q1's tightest tolerance (±0.3 mm). The A1 mini prints fresh ones for free, and the mini tester's geometry is still open ([#215](https://github.com/vertical-cloud-lab/byu-vcl/issues/215#issuecomment-5676406588)) | thin · keyed orientation · seat into grips |
| 14 | **Anti-static weigh boat** | PS, 41 × 41 × 8 mm, 0.3 mm wall *(typical)* | In daily use for manual weighing ([#15](https://github.com/vertical-cloud-lab/byu-vcl/issues/15#issuecomment-3999005476)). Insulating where #1 conducts, which bears on the open static question ([powder-doser#84](https://github.com/vertical-cloud-lab/powder-doser/issues/84)). Boats stick together, so picking one off a stack is its own primitive (Q5) | thin · crushable at 40 N · pour · singulate |
| 15 | **Spoonula / micro-spatula** | stainless, ~150–210 mm *(typical)* | The one tool-use object. Scooping is how Radulov et al. 2026 handle powder (a Franka with a Robotiq gripper holding the scoop), and it is Q3's open-powder-scoop project | tool use · long · specular |

**Fill states count as separate objects in the log.** Objects #1, #8, and #11 each come in
more than one fill state. Q4's model has fill state as a fixed effect, and a filled vial and
an empty one fail differently: an empty one is purely refractive, while a filled one adds a
meniscus and a centre-of-gravity shift.

## Tier 2 — extension (add once Tier 1 runs)

These broaden coverage toward other SDLs, so numbers are comparable, and toward the lab's
next workflows.

| Object | Spec | Why |
|---|---|---|
| **WetRobo's three tasks**: a culture-media bottle cap, a Petri-dish lid, a hinged door | per [WetRobo](https://github.com/tsudalab/WetRobo) | The only published lab kit on **the same arm**. Matching its tasks gives a same-arm comparison for free. Note that WetRobo replaced the stock gripper |
| **10 mL crimp-top headspace vial** | ~22.5 × 46 mm, 20 mm crimp *(typical)* | The vial of Burger et al. 2020 and ARChemist, the most-cited arm SDL lineage |
| **Alumina crucible** | e.g. [AdValue AL-2010A](https://www.advaluetech.com/Pdf_files/Alumina_Crucibles.pdf), 10 mL, Ø25 × 25 mm, $9.59 | A-Lab is the only published lineage whose arms handle crucibles. Its crucible size isn't in the paper; its control code moves 10 mL of slurry per crucible |
| **TA Tzero Al DSC pan + lid** | ~5.4–6.7 mm OD (sources disagree), **49.7 mg** for the pair, 20 µL (901683.901 + 901671.901) | What Q3 and Q4 took "crucible and lid" to mean. Now the extreme small, crushable object. Needs tweezer fingertips or vacuum. No robotic DSC press-fit has been published (Q3) |
| **Aluminium weighing dish** | 57 × 14.5 mm, ~2.2 g ([US Plastic 72452](https://www.usplastic.com/catalog/item.aspx?itemid=38615), $9.43/100) | Crushable *and* specular. Also the dispense target powder-doser#84 wants grounded |
| **Mini LPBF build plate** | 26 × 25 × 1 mm ([#61](https://github.com/vertical-cloud-lab/byu-vcl/issues/61#issuecomment-4185372469)) | A thin near-planar metal part under ~2 mm, a class the [sibling branch's perception scan](https://github.com/vertical-cloud-lab/byu-vcl/blob/3a72755/docs/6dof-q3-sandbox-plan.md) called "essentially unstudied" |
| **Induction-furnace sample stack** | graphite cup Ø20.30 × 6.5 mm + stepped lid, alumina discs Ø14, sapphire window Ø9.5 × 0.5 ([SI](https://github.com/vertical-cloud-lab/custom-induction-furnace/blob/main/paper/SI.tex)) | Fine assembly with a real use |
| **Cuvette** | PS, 12.5 × 12.5 × 45 mm (BRAND 759075D) | Q1's ±0.5 mm spectrometer seat. The square section makes it keyed |
| **XRF cup / zero-background Si plate** | Chemplex 1330 Ø30.7 × 22.9 mm; MTI Ø32 × 2.0 mm ($215) | Characterization formats that aren't settled in-house yet. **Use a printed dummy of the Si plate first**, since a drop costs $215 |
| **Mounted metallography puck** | Bakelite, 1¼" (31.75 mm) *(typical; in-house size unmeasured)* | SEM/EBSD samples ([#110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issuecomment-5736363939)) |
| **Wireless colour sensor** | AS7341 + Pico W, ~40 × 60 × 84 mm, ~50 g | It falls off the P20 because the press fit holds only ~52 g ([#197](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5594748767)). Re-docking it is a real recovery task |
| **Tensegrity T3 prism** | ≤81 × 79 × 104 mm, 18–23 g, PLA struts + TPU tendons; ~50 printed | Loading the drop tower is the most repetitive manual step in the org. Grip it by a strut. Deferred only because the tower's location relative to the arm is undecided |
| **CR2032 coin cell** (a dead cell or an empty case) | Ø20 × 3.2 mm, ~3 g, IEC 60086 | If the set is ever released, this is the most reproducible thin specular disc anyone can buy. Keep jaw pads non-conductive, because the can and the cap are opposite terminals |
| **Warped printed 384-well plate** | the Formlabs V2 copy that "needs force to seat" ([#5](https://github.com/vertical-cloud-lab/byu-vcl/issues/5#issuecomment-3842025907)) | A deliberately imperfect object. Real labware is out of tolerance more often than benchmarks admit |

## Tier 3 — defer or leave out

- **Open metal powder in the arm cell.** Al, AlSi10Mg, and Si are combustible dusts, and
  the lab's own rules are no compressed air, ESD protection, and grounded vessels
  ([#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126#issuecomment-4710583414),
  [powder-doser#31](https://github.com/vertical-cloud-lab/powder-doser/pull/31#issuecomment-4423553706)).
  Real powder goes in **sealed** containers only (#1, #8) until the safety question is
  answered and there is an interlock. Open-container work uses a surrogate (see below).
- **Open liquids**: reservoirs and unsealed plates. A spill lands on a CAN-bus arm with no
  obstacle sensing, rated only IP22.
- **The real crucible inside the rePOWDER.** Rehearse on a replica. The bell may only open
  below 500 °C, and how hot parts come out after a run is not documented.
- **Petri dishes (beyond WetRobo's lid), coin cells, NMR tubes, Charpy bars, deep-well
  plates, microtubes.** They are common elsewhere but not in this lab's workflows. The
  census puts coin cells and Petri dishes in battery and bio SDLs, and deep-well plate
  heights vary by 3 mm between vendors (41 vs 44.1 mm).
- **The Ø170 mm LPBF build plate and A1 mini print removal.** Both are "AM in the loop"
  work for later, and both need a dedicated fixture.

## Coverage: every failure axis is hit at least twice

Rows are the properties that break grasps and placements. Cells are Tier 1 object numbers.

| Axis | Tier 1 objects | Why it matters |
|---|---|---|
| Transparent / refractive | 5, 8, 9 (translucent: 10, 14) | RGB-D depth error on transparent labware still reaches 38 mm (Q1) |
| Specular metal | 1, 2, 3, 4, 7, 15 | On metallic parts, BundleTrack's error goes from 6.6 mm top-down to 32 mm at a 45° view ([sibling-branch perception scan](https://github.com/vertical-cloud-lab/byu-vcl/blob/3a72755/docs/6dof-q3-sandbox-plan.md)) |
| Small (≤13 mm across the grasp) | 2, 7, 9, 13 | The ±0.5 mm gripper repeatability becomes a large share of the object |
| Wider than the 70 mm stroke | 11, 12 | Forces custom fingers or the 100 mm gripper |
| Thin or near-planar | 13, 14 | Almost no silhouette or depth contrast |
| Crushable or breakable | 5, 8, 9, 14 | 40 N rated grip; a cracked vial ends a campaign |
| Heavy or long (≥0.2 kg, or ≥200 mm) | 4, 6, 15 | Slip under acceleration; torque at the fingertip |
| Mass or CG changes with fill | 1, 6, 8, 11 | The same grasp on a different object |
| Slosh or spill | 5, 8 (water), 11 (sealed) | Motion limits; containment |
| Two-part (plug, cap) | 1 + 2, 8, 10 | Contact-rich; uncapping needs regrasps at J6 ±100° |
| Seat into a fixture (peg-in-hole) | 1, 4, 7, 8, 11, 12, 13 | The primitive Q3 says compliance should buy |
| Keyed or orientation-dependent | 6, 11, 12, 13 | Yaw has to be right, not just position |
| Tool use | 14, 15 | The grasp has to resist a moment, not just hold |

**Redundant candidates dropped from Tier 1:**

- a 4 mL and an 8 mL vial (they sit between #8 and #9 on every axis)
- the Al weighing dish (it overlaps #14 except for being specular, so it went to Tier 2)
- a 50 mL conical tube (it overlaps #10)
- a deep-well plate (it overlaps #11 and #12, and vendors disagree on its height)

## What published SDL arms actually pick up

The census covered 38 arm-based lab systems. It found the ranking below, by the number of
systems whose arm handles each class:

| Class | Systems | Sandbox objects |
|---|---|---|
| Racks, trays, holders, carriers | 14 | every fixture below |
| Vials, 2–40 mL | 12 | 8, 9 (+ 10 mL crimp in Tier 2) |
| Open glassware and bottles | 9 | 5 |
| Pipettes, tips, droppers | 9 | 12 |
| Caps and lids | 7 | 2, 8, 10 (+ WetRobo cap and lid) |
| Instrument doors, lids, buttons | 5 (4 more motorized the door instead) | balance breeze break (+ WetRobo door) |
| Tubes | 5 | 10 |
| Flat substrates and slides | 5 | 13 (+ mini build plate) |
| Powder tools and media | 4 | 1, 14, 15 |
| XRD holders | 3 | Tier 2 |
| SBS plates and reservoirs | 2 (first in bio automation) | 11, 12 |
| Crucibles | 2 (both A-Lab lineage) | 1 (+ alumina and DSC in Tier 2) |

Three things stand out.

- **Racks and vials dominate.** The core should look like a vial lab even though this is a
  metals lab. It does: the atomizer cup behaves like a vial in a rack.
- **SBS plates are rare for arms in chemistry and materials.** They are common in biology.
  The plate is in Tier 1 because the OT-2 is here, not because it is typical.
- **Low-cost arms in the literature handle light objects.** Examples are myCobot,
  MG400, SO-101, and PiPER handling vials, tubes, lids, and coin-cell parts. Nothing in
  Tier 1 exceeds ~0.25 kg, so results transfer down to those arms as well as up.

## What Edison Q5 added, and where it is wrong

Q5 (`c1c66197`, verbatim in
[`edison-6dof/q5-sandbox-object-set/answer.md`](edison-6dof/q5-sandbox-object-set/answer.md))
proposed an 18-item Tier 1. Most of it agrees with the table above. Its most useful
contributions are reliability numbers the object list should be designed against:

- **Vendor variation is real.** At Liverpool, certified vials varied enough to jam in
  their fixtures. After the wells were widened, 100 consecutive vials fit, and tapered
  edges plus compliance gave **464/464** rack placements (Burger 2023, pp. 62–69 and
  108–112, as cited by Q5). This is the ≥1 mm clearance rule, measured.
- **Printed fingers break under repetition.** The YuMi PXRD workflow cut SmartGripper force
  from **20 N to 10 N because the fingers snapped** under repetitive use (Lunt et al.). The
  PiPER's 40 N rated grip on a PETG finger deserves the same caution, and it is another
  reason Q4's fatigue protocol matters.
- **Transparency costs about half the success rate.** Visual-only vial insertion succeeded
  **48.78%** of the time, and multimodal feedback raised it to **89.55%** (Butterworth et al.
  2023). End-to-end robotic capping reached **88%**, and rack insertion **92%** (Fakhruldeen
  et al. 2025). None of these used a sub-$5k arm.
- **Stacked consumables fail at singulation.** Weigh boats stick together, so "pick one off
  the stack" is its own primitive and needs a dispenser.
- **Stock consumables at 2× the planned trial count.** Record the lot for every item. No
  published benchmark handles single-use or deforming objects.

Where it is wrong, checked against the lab's threads and vendor pages:

- **The atomizer parts are invented.** Q5 gives a "Ø20 × 80 mm" cup at "≈30 g empty /
  ≈80 g filled", a "Ø20 × 5 mm press-fit disc", and a separate "Ø20 × 25 mm aluminium
  dosing crucible". The real parts are:
  - a 19.05 × 63.5 mm cup at 32.0 g
  - a 12.7 × 9.5 mm vented plug at 3.1 g
  - 4.6–9.9 g of powder per cup

  The doser's crucible has no defined geometry yet (PR #232, #222).
- **Masses are high.** The SEM stub is ~1 g, not ≈3 g
  ([caliber#6](https://github.com/vertical-cloud-lab/caliber/pull/6#issuecomment-5840573985)).
  A printed D638 Type V is ~2 g by volume, not ≈5 g.
- **SEM mounts.** JEOL and Hitachi cylinder stubs are Ø9.5–15 mm (Ted Pella 16221/16231/16322),
  not "Ø25 or Ø32 mm".
- **The benchmark claim is out of date.** Q5 repeats Q4's "no published physical
  laboratory-object manipulation benchmark". LabDex and WetRobo postdate its corpus.
- **Where we disagree on tiers,** the lab's workflows decided it:
  - Charpy coupons go to Tier 3, because there is no impact tester here.
  - The XRD cup goes to Tier 2, because XRD is "available but unused".
  - The reservoir comes out, because open liquid stays out of the cell.
  - The coin cell goes to Tier 2, where its IEC 60086 standardization makes it the most
    reproducible thin disc anyone can buy, but it is not a workflow object here.

## Fill surrogates

Real metal powder stays sealed (Tier 3), so open-container work needs stand-ins. Neither
Q5 nor the web search found an SDL that matched a surrogate to a metal powder by
flowability. **That is an open gap, and a cheap one to close here**, since the doser team
already stocks a shelf of candidate powders
([list](https://github.com/vertical-cloud-lab/powder-doser/blob/main/docs/candidate-powders-shopping-list.md)).

| Stand-in for | Surrogate | Basis |
|---|---|---|
| AlSi10Mg, 15–45 µm, spherical, Hausner ratio ~1.10–1.20 | **fine NaCl** (HR ~1.15–1.25) or **glass microspheres** (HR ~1.05–1.15) | Q5. It flags the HR values as extrapolated from pharmaceutical flow data, not tested robotically |
| Si, <45 µm, angular, cohesive, HR ~1.30–1.45 | **fine lactose** (HR ~1.30–1.40), or wheat flour (HR ~1.35–1.45) | Q5, same caveat. Prefer lactose: flour is a combustible dust too, just a milder one |
| Liquids | **dyed water** at 25 / 50 / 75 % fill, sealed | Q5's suggested fill convention. Dye makes the meniscus and any spill visible to the wrist camera |
| Viscous reagents (later) | 50 wt % glycerol–water, ~6 mPa·s | Q5 |

Radulov et al. 2026, the SDL scooping study that Q1 and Q5 both lean on, spanned flow
behaviour with seven powders: SiO₂, sugar, NaCl, semolina, NaHCO₃, pectin, and wheat
flour. Borrowing two of them (NaCl, and silica if a very cohesive case is wanted) makes our
scoop numbers comparable to theirs.

**Measure the Hausner ratio of each surrogate next to the real AlSi10Mg and Si.** It takes
a graduated cylinder and a balance, and in-house tapped density was already recommended in
[powder-doser#163](https://github.com/vertical-cloud-lab/powder-doser/issues/163#issuecomment-5736135714).
Doing it turns "we used salt" into a matched surrogate. Use grounded conductive trays under
powder stations and absorbent liners under liquid ones (Q5).

## Stations the objects move between

The sandbox needs stand-ins for the places objects actually go. Each is a printed or
borrowed replica at spot D until the arm is co-located with the real thing.

- **HR-100A balance.** Use the real one, or a same-footprint dummy with the breeze break
  and drop hole. Vessels must be ≤3" tall and ≤102 g gross, so reaching under the break is
  its own approach constraint. Arm motion near a 0.1 mg balance is a new disturbance, so log
  the balance alongside the arm.
- **Crucible replica.** Ø57 mm bore, Ø12.6 mm sealing rod, and the ≈Ø22 mm adapter
  overhang ~18 mm above the rim, all from
  [PR #232's model](https://github.com/vertical-cloud-lab/byu-vcl/blob/323adba/atomizer-charge/README.md).
  **Measure the real crucible first.** The model is scaled from a drawing, and tipped
  insertion of a 3/4" part misses by 0.09 mm in it.
- **Press.** An arbor press or soft-jaw vise with the F1 sleeve (#4). The arm loads and
  unloads it, and the press supplies the 1.3–1.6 t.
- **OT-2 slot replica.** A 128.0 × 86.0 mm pocket, raised so stepped fingers can reach
  below the plate's top edge.
- **Racks.** SBS-footprint racks for #1, #3, and #8, plus the AC 6-tube rack for #10,
  which already exists at 127.76 × 85.48 × 61 mm with Ø20 × 58 mm wells.
- **Stub tray.** The caliber insert (19 seats, 15 mm pitch,
  [caliber#17](https://github.com/vertical-cloud-lab/caliber/pull/17)). Its thread already
  suggests an SBS-footprint version, which the arm would also prefer.
- **Coupon grips.** A printed mock of the mini tester's grips
  ([#215](https://github.com/vertical-cloud-lab/byu-vcl/issues/215)).
- **A1 mini.** It prints every fixture above, plus replacement coupons (#13).

## Fixtures and holders to print

Tag the fixture, not the part (Q3). Every holder below is a PETG print from the A1 mini
with a 20 mm AprilTag on matte label stock on a **sidewall**, in a non-coplanar pair where
the fixture is large enough. Rules carried over from Q3, applied to every receiving
feature:

- **1–2 mm lead-in chamfer at 15–30°**, and **≥1 mm diametral clearance** unless the step
  *is* the press-fit. At ±0.5 mm of gripper repeatability, a 0.5 mm clearance needs active
  compliance, while 1.5 mm succeeds >95% of the time under position control alone.
- **V-groove seats for cylinders** (vials, the atomizer cup), so diameter variation
  between vendors shifts height rather than lateral position.
- **Stub holders with tapered pin bores** and replaceable press-fit bushings (Q5), so a
  3.2 mm pin that arrives 0.5 mm off-axis still self-seats. Don't use magnets, even though
  the sibling branch's plan suggests them: the stubs are aluminium.
- **Raised plate nests narrower than the SBS footprint**, so stepped fingers can reach
  under the plate's top edge. Match the OT-2 deck slot, so a plate placed in the sandbox
  is a rehearsal for a plate placed on the robot.
- **Print one reference fixture five times** before trusting any of them. Q4 puts FDM
  error at 0.18 ± 0.07 mm, which is already a third of the clearance budget.

## What each object record should carry

Q4's protocol table and YCB's release format agree on the minimum, and it costs little to
collect at purchase time:

- supplier, part number, lot, and purchase date
- measured dimensions (calipers, n = 5 specimens) against the nominal, and mass empty and
  filled
- material and surface finish
- fill recipe (surrogate, fill fraction, cap torque)
- canonical pose in its fixture, as a tag ID plus a fixed offset
- a mesh (vendor STEP if one exists, otherwise a CadQuery model from the measured
  dimensions, which CADSmith can generate)
- for consumables, the per-trial replacement rule

That record is what turns a shelf of labware into a benchmark someone else can rebuild.

## Where to start

This part is judgement, ordered by value per unit of effort.

1. **Service the doser's collection vessel (#5).** Lift the beaker from under the breeze
   break, empty it, and re-seat it under the drop hole. It is the one step that currently
   stops a closed loop in this org, so automating it turns an existing optimization
   campaign into an overnight one. Pitch it as a lab-level transfer arm, not a doser part.
   [powder-doser#36](https://github.com/vertical-cloud-lab/powder-doser/issues/36) already
   rejected "a 6-axis arm" *as part of the doser*.
2. **Charge cup into the crucible replica (#1 and #3).** This is the riskiest real step: a
   tipped insertion past an overhang with no measured margin. It gets rehearsed hundreds of
   times on the slug and a replica before anyone tries it on the real crucible.
3. **Vials and cups in and out of SBS racks (#1, #8, #9).** This is the baseline for the
   reliability campaign. It is directly comparable to Liverpool and Lunt et al., and it is
   what the first 119 zero-failure operations should be (Q2).
4. **Stubs from tray to tray (#7).** The first small specular part, and the
   3.2 mm pin-in-hole.
5. **Plate on and off an OT-2 slot replica (#11 and #12).** This is where the first custom
   fingers get designed. It makes a well-posed target for the CADSmith loop: *one finger
   pair, 0–70 mm stroke, 12 mm vial to 85.48 mm plate.*

## Open questions for the team

- **Measure the rePOWDER crucible.** Bore, rod OD, adapter width, and the adapter's height
  above the rim. The replica, and whether a 3/4" cup can be tipped in at all, both depend
  on it.
- **The doser's aluminium crucible is still undefined**
  ([powder-doser#84](https://github.com/vertical-cloud-lab/powder-doser/issues/84)). One
  option is to make it the charge cup itself. The cup is 63.5 mm tall, under the 3"
  limit, and at ~45 g charged it stays well under the 102 g balance. That would let one
  object carry powder from doser to atomizer. The risk is that a 12.7 mm bore is a small
  target under the auger outlet, so it may need a printed funnel.
- **70 mm or 100 mm gripper?** The 100 mm variant exists and the SDK already has the
  setting. Buying it removes the plate problem. Keeping the 70 mm one keeps the plate as a
  clean design target for the generative loop. The second is the more interesting paper,
  and the first is the faster sandbox.
- **Which 20 mL vials?** #151 cites a Fisher part for the CubXL but deferred the purchase.
  Buying one 24-400 SKU for both the CubXL and the sandbox avoids two vial populations.
- **Which SEM holder does BYU's microscopy facility use?** The stub tray should match its
  pitch, so a loaded tray can go straight to the microscope.
- **Where are the doser, atomizer, OT-2, and CubXL relative to spot D?** Until the arm can
  reach a real station, every Tier 1 task runs against a replica. That is fine for the
  reliability data, but it is not yet automation.

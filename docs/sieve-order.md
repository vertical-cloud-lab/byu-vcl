# Sieves for atomized powder (#222)

The atomized Al 4047 has chunks in it (splats, beads, a few millimetres across), and an LPBF print wants it cut to
the usual laser powder bed fusion range, **20–63 µm**. The order below is a stack of 3 in all-stainless Gilson test
sieves. It was checked on 2026-10-07 against the experimental sections of the LPBF and ultrasonic-atomization
literature (two Edison reviews, [`outputs/pr-262-edison-sieve/`](../outputs/pr-262-edison-sieve/)), against
sieve-maker guidance, and against the combustible-dust rules for aluminium. Three things changed:

- **Hold the 20 µm sieve.** Ultrasonically atomized Al has almost nothing under 20 µm (D10 of 36–45 µm in every
  paper found), and a 20 µm woven-wire sieve blinds when shaken by hand: dry sieving is "deficient" below about
  45 µm. Nobody in the LPBF literature makes a lower cut by dry sieving; suppliers do it by air classification, and
  labs only scalp the top end. Order the No. 60 and No. 230 now, measure the first batch's size distribution, and buy
  the No. 635 (or a No. 325) only if the fines turn out to matter.
- **Grounding is not optional.** NFPA 484 (combustible metals) and NFPA 77 want every piece of equipment in the
  process bonded and grounded, movable things clipped to a flexible lead during transfer, the person grounded, and
  powder never poured over an insulator. So: a bonding lead on the stack and on the tray, the ESD coat and wrist strap
  that came with the atomizer, and a stainless tray instead of the sheet of paper Bartosz uses.
- **A dust mask is not enough.** NIOSH's 2025 evaluation of an AM powder facility recommends a powered air-purifying
  respirator for sieving; the floor is a half-face respirator with P100 filters. Bartosz cleans the atomizer in a
  full-face respirator.

BYU Chem Stores has no online catalog. Ask them first (801-422-2678, chemstores@chem.byu.edu); if they have nothing,
order these. Prices read from globalgilson.com on 2026-10-07.

| Sieve | Opening | What it does | Model | Price |
|---|---:|---|---|---:|
| Cover | — | Keeps fine Al dust in while the stack is shaken | [V3SFXCV](https://www.globalgilson.com/3-inch-sieve-cover-stainless) | $23.70 |
| No. 60 | 250 µm | Takes out the chunks the hand missed, and protects the fine mesh below | [V3SF #60](https://www.globalgilson.com/3-inch-sieve-all-stainless-full-height-number-60) | $58.50 |
| No. 230 | 63 µm | Top of the LPBF range. What passes is the print fraction | [V3SF #230](https://www.globalgilson.com/3-inch-sieve-all-stainless-full-height-number-230) | $71.20 |
| Pan | — | Catches the print fraction | [V3SFXPN](https://www.globalgilson.com/3-inch-sieve-pan-stainless-full-height) | $45.80 |
| | | | **Order now** | **$199.20** |
| No. 635 | 20 µm | Bottom of the LPBF range. **Deferred**: buy after the first batch's PSD shows fines are a problem, and only with a shaker | [V3SF #635](https://www.globalgilson.com/3-inch-sieve-all-stainless-full-height-number-635) | $176.90 |
| No. 325 | 45 µm | Optional, if Utah asks for the tighter 20–45 µm cut some machines use | [V3SF #325](https://www.globalgilson.com/3-inch-sieve-all-stainless-full-height-number-325) | $74.50 |
| Shaker | — | Gilson SS-3 3 in vibratory shaker: seven full-height 3 in sieves, 3,600 vpm, 0–100 % amplitude, solenoid tap 60/min, timer. The literature's answer to hand tapping, and the first automation step | [SS-3](https://www.globalgilson.com/gilson-performer-iii-3-inch-sieve-shaker) | $1,601.40 |

Also needed, from wherever is quickest: a stainless tray with a lip (about 280 × 220 mm), a stainless lab scoop, a
stainless powder funnel that sits in a 3 in sieve, bonding leads with clips (two) and a ground point, 100 mL glass
jars (the "smaller jars" of 2026-09-29), a half-face respirator with P100 filters, and a soft natural-fibre brush.
Gilson's 20 µm and 45 µm sieves do **not** include backing cloth; order it with them if they are ever bought, since
a fine mesh without it stretches.

![The procedure, from the CAD model](../sieving/viz3d/out/sieving.gif)

*The whole procedure at real dimensions: [`sieving/viz3d/`](../sieving/viz3d/README.md). The No. 635 is drawn
because it is in the stack as first proposed; the split of the 50 g batch is an example, not a measurement.*

## Why these cuts

**63 µm upper cut: standard.** SLM Solutions specifies AlSi10Mg as 20–63 µm and Renishaw asks for 20–63 µm; EOS
specifies 25–70 µm and recycles through a 90 µm sieve. The LPBF papers that sieve Al powder use 60, 63, 70, 75, 80, 90
and 100 µm meshes, always as a single scalping cut to remove spatter and agglomerates. Yankin et al. (2025),
atomizing AlSi12 ultrasonically at 35 kHz, sieved through 63 µm and called everything finer usable for a Renishaw
AM400; about 75 % of their powder passed.

**20 µm lower cut: not done this way.** No experimental section found makes a lower cut by dry sieving. Commercial
powder gets its lower end from the supplier's air classifier. And the ultrasonically atomized Al reported so far is
narrow and sits above 20 µm:

| Paper | Machine, alloy | D10 / D50 / D90 (µm) | Sieve used |
|---|---|---:|---|
| Yankin et al. 2025, *Sci. Rep.* | ATO Lab+ US35 (35 kHz), AlSi12 | 38.7–44.7 / 52.3–54.7 / 66.4–72.7 | 63 µm; ~75 % passed |
| Ukabhai et al. 2025, *MATEC* | AMAZEMET rePowder, induction, Al–10Cu | 36 / 65 / 78 | none reported; target 15–75 µm |
| Bałasz et al. 2023 | ultrasonic, Ti6Al4V | 45 / 55 / 62 (volume) | 63 ± 20 µm class, Multiserw LPzE-3e shaker, 50 Hz |
| Jedynak et al. 2024 | rePowder, induction, AlSiMg–SiC composite | mean 88–120 | 200 µm scalp |

With D10 near 40 µm the sub-20 µm fraction is a few per cent at most. The cost of taking it out by hand is the
blinding described below; the cost of leaving it in is nothing measurable until a laser-diffraction PSD says
otherwise. Expect a D50 of 50–65 µm from the rePowder on Al, and 50–75 % of what atomizes to pass 63 µm, so a 10–100 g
charge gives 5–50 g of print fraction. The Oct 6 run (#261) was mostly splats; the first jars will tell.

**Why a 20 µm woven sieve blinds.** Near-mesh particles wedge in the apertures and fine Al charges triboelectrically
and sticks to the wires and to larger particles. Neikov & Yefimov (*Handbook of Non-Ferrous Metal Powders*, 2019)
put the limit of ordinary dry sieving at about 45 µm (325 mesh); below that the methods are air-jet sieving
(Alpine type, to about 10 µm) or air classification. Hand tapping is not even the analysis method: ASTM B214 and
ISO 4497 specify a shaker with rotary and tapping action, and side-to-side shaking alone promotes blinding. If a
20 µm sieve is ever used here it belongs on the SS-3, in 5–10 g charges, with backing cloth, and the mesh inspected
under a microscope after use.

## 3 in, the container, and the rest of the workflow

**3 in is right for tens of grams.** Sieve analysis uses 75 mm or 200 mm rings; the 100–300 g charges in the
standards are for 200 mm sieves, which have seven times the area. On a 3 in mesh (74 mm clear, 43 cm²) a 50 g batch
of Al at 1.6 g/cm³ tapped is a **7.7 mm bed**, and one layer of 50 µm particles is only **3–4 g**. Gilson's own rule
is that no more than one or two particle layers should remain on a mesh at the end. So feed the top sieve in parts
of 10–20 g, not the whole batch at once; it is the bed depth, not the frame diameter, that sets the rate.

**The atomizer's powder container is wider than the sieve.** In #255's model it is Ø130 × 202 mm with a Ø108 top
tube; the position was observed on video, the size is assumed, and nobody has put a rule on it yet. Whatever the
exact number, its mouth is wider than a 3 in sieve, so the powder cannot be poured straight in: it goes onto the
tray (where the pieces are picked out) and from there by scoop into a funnel sitting in the top sieve. That is
Bartosz's practice (pour onto paper, remove the larger pieces by hand or through a mesh, T2 50:51 and 55:12) with the
paper replaced by a grounded tray.

**The other end is the doser.** The powder doser's cartridge is a Ø25.0 mm auger tube
([powder-doser PR #170](https://github.com/vertical-cloud-lab/powder-doser/pull/170)), and on Sep 30 the pieces in
the unsieved Al 4047 clogged its outlet ("those bigger chunks really gummed up the nozzle", DOSE2 27:21). The sieved
20–63 µm jar is what gets loaded into it; the 63–250 µm jar goes back into a cup for re-atomization (E6 in #222).
The whole loop is: container → tray → pieces to the dish → No. 60 / No. 230 / pan → weigh each fraction → jar with a
6-character ID (#249) → doser cartridge → cup → atomizer.

## Grounding, atmosphere, PPE

Aluminium powder from 2 to 63 µm is among the most ignitable metal dusts: a minimum ignition energy of 3–13 mJ and a
minimum explosible concentration of 45–170 g/m³ (Benson 2012; Taveau et al. 2018). A person carries 25–30 mJ of
static. So:

- **Bond and ground** the stack, the tray, the funnel, the jars' tray and the scoop: a clip and flexible lead to a
  ground point, per NFPA 484 and NFPA 77. All-stainless sieves are conductive, which is one reason to prefer them
  to brass frames (the other is Cu and Zn pickup into an Al alloy). Wear the ESD coat and wrist strap AMAZEMET
  supplied (9/17 call). Never pour or slide powder over paper, plastic or acrylic. Use conductive, non-sparking
  scoops and natural-fibre brushes; synthetic bristles and plastic scoops accumulate charge (Aluminum Association,
  *Safe Handling of Aluminum Fine Particles*).
- **Atmosphere.** The industry sieves Al and Ti under argon: SLM Solutions' PSM100, Farleygreene's Sievgen and the
  Russell AMPro Lab all purge with inert gas. The safety literature calls an oxygen-free glovebox the preferred
  arrangement and, where that is not practical, local extraction that keeps the air below the MEC, with a documented
  dust-hazard analysis (NFPA 652/660). For tens of grams, a fume hood with the sash down and the stack covered is the
  minimum; the glovebox from the 9/17 call is the right home for this step when it exists.
- **PPE.** Half-face respirator with P100 filters at minimum (NIOSH recommends a PAPR for sieving), nitrile gloves,
  safety glasses, the ESD coat. Sieve with the cover on; let the dust settle before lifting it.
- **Housekeeping.** No compressed air, no shop vacuum: a Class II / Group E certified vacuum or a damp wipe. Keep the
  area below 55 % RH (the atomizer room's dehumidifier) and let a cold jar warm to room temperature before opening.

## Is this how LPBF labs do it?

Yes, at this scale. Research atomizer labs classify with standard test sieves on a mechanical shaker (Bałasz et al.
2023: a Multiserw LPzE-3e at 50 Hz to DIN 66165-1; Yankin et al. 2025: a 63 µm mesh; NIST's AM lab hand-sieved
through an EOS 80 µm sieve). Production LPBF uses closed vibratory stations with ultrasonic deblinding under argon
(PSM100, Russell AMPro, Sievgen), which are built for kilograms per batch: the Russell AMPro Lab, the smallest, takes
1–4 L batches and does half a litre in under 30 minutes, and would hold up more powder in its own corners than one
of our runs makes.

## Tutorials and instructions

- Hand sieving, the motion and the endpoint: Haver & Boecker, [What is hand sieving?](https://blog-oh.haverboecker.com/particle-analysis/hand-sieving):
  coarsest on top; rotate the stack with one hand and tap the frame with the other, about 3 minutes for a stack,
  1–4 minutes per single sieve; then run each sieve on its own and add what passes to the one below; be consistent
  in tapping and rotation speed. Video: [Hand Sieving Method for Materials Sieve Analysis](https://www.youtube.com/watch?v=Jf_p934fSpA)
  and [What Is Hand Sieving?](https://www.youtube.com/watch?v=INPkoA3dnCY). These are aggregate practice; for Al
  add the cover, the grounding and the respirator.
- Choosing sieves: Gilson, [Selecting the right test sieve for non-conventional use](https://www.globalgilson.com/blog/selecting-the-right-test-sieve-for-non-conventional-use):
  stainless over brass; backing cloth for stainless mesh finer than No. 70; no more than one or two layers of
  material on the mesh at the end; the SS-3 and the GilSonic AutoSiever as the two 3 in machines.
- Metal powder in AM: Russell Finex, [Sieving and screening fine metal powders](https://www.russellfinex.com/en/demonstration-videos/sieving-fine-metal-powder/)
  (titanium through a vibrating sieve) and the [AMPro Sieve Station](https://www.youtube.com/watch?v=izu1iPD0giw);
  Elcan, [Sieving additive manufacturing powders](https://elcanindustries.com/blog_posts/sieving-additive-manufacturing-powders/)
  (standard screeners blind at these sizes; SLM powders are cut between 15 and 44 µm).
- Safety: Aluminum Association, [Safe Handling of Aluminum Fine Particles](https://www.aluminum.org/sites/default/files/2021-11/Safe_Handling-Aluminum_Fine_Particles.pdf)
  (420 µm / 40 mesh and finer is explosible; ground everything; NFPA 484 and 77; conductive scoops, natural-fibre
  brushes, no ordinary vacuum cleaners); Newson Gale's powder-processing case of a flash fire between a vibrating
  sieve and an ungrounded drum on nylon wheels.

## Procedure

1. Gloves, ESD coat and wrist strap, respirator. Clip the bonding leads to the tray and to the pan of the stack.
2. With the dust settled, tip the powder container out onto the tray. Pick the pieces out by hand into the dish:
   they go back into the next charge.
3. Stack: pan, No. 230, No. 60. Put the funnel in the No. 60 and scoop the powder in, 10–20 g at a time. Cover on.
4. Rotate the stack in a flat circle and tap the frame, about 3 minutes. Lift the cover, brush the underside of the
   No. 230 gently with the natural-fibre brush if it is blinding, and give it another minute. (On the SS-3: 3–5
   minutes with the tap on, then check that the retained mass has stopped changing.)
5. Unstack into tared jars through the funnel: No. 60 → the dish; No. 230 (63–250 µm) → "coarse" jar; pan
   (< 63 µm) → the print jar on the balance. Weigh every fraction. The yield says how many runs a print needs.
6. Lid on, 6-character ID (#249), alloy, run, date and sieve sizes in the log, jar into the desiccant box. Back-fill
   with argon if the jar will sit for weeks.
7. Clean: brush the sieves out, ultrasonic bath in IPA for the meshes, dry, inspect the No. 230 against the light.
   One alloy per set of sieves if at all possible; at least a full clean between alloys.
8. Before the first print: a laser-diffraction PSD of the print jar (D10/D50/D90 and span). That is also what
   decides whether the No. 635 ever gets bought.

## Automating this step

**The worry about a thick bed is right.** Sieving is a probability game played at the mesh: a particle has to reach
an aperture, and on a 3 in screen a single layer of 50 µm Al is 3–4 g. Tapping and vibration move the bed and
re-present particles; they do not push a 7 mm bed through 63 µm wires, and a cohesive, charged Al powder bridges and
blinds long before that. Overloading is the main failure mode the powder handbooks name. So a sieve *inside* the
doser, with a whole dose sitting on it, is the wrong architecture, however versatile the doser has turned out to be.

**The right architecture is the doser as the feeder.** Keep the screen separate and let the auger meter powder onto
it slowly: for a 76 mm, 63 µm screen, about **1–5 g/min** keeps the bed in the one-layer regime (a 30 g batch in
about 15 minutes, which is a normal sieve-analysis time). The screen is excited two ways, as the SLM Solutions
PSM100 does: low-frequency vibration to transport the powder, and **ultrasonic deblinding at 35–36 kHz** on the
mesh wires, pulsed so that light powder can settle between bursts. The sieved powder falls into the cup or a jar;
oversize stays on the screen and is tipped off between batches. The Pi/Pico that already runs the auger, tap
solenoid and balance can run the ultrasound and the vibration too, and a mass balance (fed minus passed) detects a
blinding screen. No published device combines dosing and sieving in one step; the nearest things are pharmaceutical
vibratory sieve-chute micro-dosers (0.06–24 g/min) and the AM powder-recovery stations.

**The cheap intermediate is a shaker with a tapper**, which is the "automated tapping" the doser has, on the right
object: the SS-3 (above) vibrates at 3,600 vpm with a 60/min solenoid tap and a timer, takes seven full-height 3 in
sieves, and does 10–30 g per 10–20 min cycle. Loading, unstacking and weighing stay manual. The GilSonic AutoSiever
(about $8,600) is the same idea with 3,600 sonic pulses a minute through the stack and goes to 5 µm on 3 in sieves,
10 g at a time below 38 µm: the off-the-shelf answer if a fines cut is ever needed.

**What an automated sieve for Al must respect.** A PLA/PETG enclosure is out: insulating, so it charges, and
combustible. ESD filament fixes the first problem only. The enclosure is metal, bonded; the solenoid, vibration motor
and ultrasonic generator are ignition sources and sit outside the dust space or are rated for it; dust-tight
connections; argon purge or extraction; a dust-hazard analysis before it runs unattended. Budget: a shaker is
$1.6k–10k, an engineered ultrasonic screen with generator, transducer, enclosure and controls $10k–30k, an AM
sieving station tens of thousands and far too big.

**Suggested order of work.** Hand sieve the first batches with the stack above and weigh the fractions; buy the
SS-3 when the rhythm is known; then design the fed screen with the doser as feeder, starting at 0.5–1 g/min and
measuring hold-up, carry-over and recovery before trusting it.

## What was checked, and what was not

- Edison, `job-futurehouse-paperqa3-high`, two tasks with the questions in
  [`queries.md`](../outputs/pr-262-edison-sieve/queries.md): the sieve plan against experimental sections
  ([answer](../outputs/pr-262-edison-sieve/sieve_plan_answer.md), [references](../outputs/pr-262-edison-sieve/sieve_plan_references.md))
  and sieving automation and bed-depth limits
  ([answer](../outputs/pr-262-edison-sieve/automation_answer.md), [references](../outputs/pr-262-edison-sieve/automation_references.md)).
  Key sources: Neikov & Yefimov 2019; Yankin et al. 2025; Ukabhai et al. 2025; Bałasz et al. 2023; Weiss et al. 2021;
  Cordova et al. 2020; Smolina et al. 2022; Moylan et al. 2013; Benson 2012; Taveau et al. 2018; O'Connell 2002
  (ultrasonic deblinding); Stefaniak et al. 2025 (NIOSH HHE); Gibbons et al. 2024.
- Sieve and shaker sizes and prices from globalgilson.com; the Haver & Boecker, Gilson, Elcan, Russell Finex and
  Aluminum Association pages above.
- The powder container's size is still the assumption in #255's model. A tape measure on its mouth and body would
  settle it and the model's constants.
- One source, Jedynak et al. 2024 (MRS Forum), sits behind a Cloudflare challenge that neither the runner nor the
  stream-cam Pi's headless Chromium gets past; that Pi has no display tooling for mouse automation and carries a
  live stream, so it was not installed for one marginal paper. Edison had the paper.

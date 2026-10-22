# Polishing SOP Steps 1-6, checked against PACE

Written for Ronnie's 2026-10-06 request on [#258](https://github.com/vertical-cloud-lab/byu-vcl/pull/258):
compare Steps 1-6 of [`SOP/sem-eds-polishing-sop.md`](../SOP/sem-eds-polishing-sop.md) with the PACE
Technologies guides, the way Steps 7-11 were checked against PACE's lapping-film guide. Where PACE says
nothing, the row says which other source it uses. PACE pages and store prices were read on 2026-10-06.

**Steps 1-6 have not been edited.** They are still Ronnie's Google Doc, word for word. Each "Proposed
change" below is for Ronnie to accept or reject.

## Short version

The SOP is a sound general metallography procedure. Most of the differences come from PACE treating
aluminum as a special case. For us the reason to follow PACE there is the one that ruled out colloidal
silica: anything that leaves Si on the face biases the Si result.

1. **Step 4 grinds on five SiC papers, and SiC embeds in aluminum.** PACE's aluminum method replaces
   the 320, 400 and 600 SiC with one P1200 *alumina* paper and keeps only the 800 and 1200 SiC, about
   1 minute each. 12″ plain-back P1200 alumina paper is $145 per 100 (`ALO-2112-P1200`).
2. **Step 4's settings need labels.** PACE runs aluminum at 5-10 lb (22-45 N), with head and table both
   at 100 rpm and turning the same way. If 35 / 30 / 150 means 35 N, head 30 rpm and table 150 rpm, the
   force is in range but the speeds are far apart.
3. **Add an ultrasonic clean between the 1200 paper and the alumina pad.** PACE: "Clean the sample
   ultrasonically between every step." The pad is reused, so one SiC grain carried onto it can scratch
   every sample polished on it afterwards.
4. **Step 5 should stop when the 1200 scratches are gone, not when no scratches are visible.** That
   settles its "(verify this piece of info)". The 0.1 µm film in Step 7 removes the alumina's own
   scratches, and long runs on a napped pad leave the Si network standing in relief.
5. **End each alumina run with 10-15 s of DI water on the turning pad.** Then, if a haze is left, wipe it
   off with a cotton swab and anhydrous alcohol rather than repeating the ultrasonic clean.
6. **PACE agrees with the ASTM E1078 note about compressed air:** "shop air carries oil and moisture that
   will recontaminate the specimen". Use filtered, oil-free gas. That answers open question 4 in the SOP.
7. **Clean the cut piece before mounting (Step 2), and write the press settings into the SOP.** PACE
   gives 150-180 °C, 3000-4000 psi and 5-8 minutes for phenolic, cooled under pressure.

The rest are smaller fixes or optional purchases.

## Step 1: sectioning on the diamond saw

| SOP | PACE | Proposed change |
|---|---|---|
| The PSC's diamond blade, as issued | "Ductile materials (metals, plastics) cut better with high concentration: more cutting points spreading the load." ([sectioning](https://www.metallographic.com/guides/sectioning)) | Ask the PSC whether the blade is high concentration (HC) or low (LC). LC is meant for brittle materials. |
| No blade dressing | "Dress the blade with a ceramic dressing stick before cutting." "Dress before each cutting session, and again any time cut rate begins to fall." Load "less than 200 grams", speed "less than 300 RPM", and "Always use a dressing fixture." ([sectioning](https://www.metallographic.com/guides/sectioning)) | Dress the blade before each session. A PACE stick (`DRES-0010`) is $15; the PSC may have one. |
| ~1400 rpm free, kept at 1000-1100 rpm while cutting | "Do not force the cut. If it slows down, reduce force or check the blade rather than pushing harder". "Start the cut with reduced force to establish the kerf". For aluminum: "use a low cutting speed to minimize heat generation and deformation" ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Holding the drop to 1000-1100 rpm is a sensible feed limit. PACE would go lighter still: start and finish each cut with less force, and dress the blade if it keeps bogging down rather than pushing harder. |
| Tap water as coolant | "A good cutting fluid removes and suspends swarf, lubricates the blade-sample interface, and inhibits corrosion of the sample, blade, and machine." ([sectioning](https://www.metallographic.com/guides/sectioning)) | Optional. Water works if the piece is cleaned before mounting (Step 2). |
| No PPE listed | "Wear appropriate PPE: safety glasses, hearing protection on abrasive cutters, gloves when handling sharp samples" ([sectioning](https://www.metallographic.com/guides/sectioning)) | Add safety glasses. |
| Ends with taking the saw apart | "Clean cutting fluid and swarf from the sample" ([sectioning](https://www.metallographic.com/guides/sectioning)) | Add: rinse the piece, rinse it with ethanol, and let it dry. |
| ~1 cm piece, to fit an SEM stub | "Aim for the specimen to occupy roughly 50–70% of the mount diameter. Too small a specimen wastes resin and floats during pouring" ([mounting](https://www.metallographic.com/guides/mounting)) | Keep 1 cm, since the stub sets the size. It is about 30% of a 1¼″ mount, which is why small pieces tip, as on [09-23](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issuecomment-5802068338). PACE's answer is to "use mounting clips". |

## Step 2: compression mounting

| SOP | PACE | Proposed change |
|---|---|---|
| Sample goes into the press as cut | "Clean the specimen of cutting fluid, oxide, and handling residue. Oil contamination prevents polymerization at the specimen surface." For gaps between resin and specimen: "Clean specimen surface before mounting" ([mounting](https://www.metallographic.com/guides/mounting); [polishing](https://www.metallographic.com/guides/polishing-methods)) | Add a first bullet: the piece must be clean and dry before it goes in. This matters more now that Step 7 is on film: alumina or SiC trapped in a gap around the metal can wash out onto the 0.1 µm film. |
| "Configure settings according to the laminated sheet" | For phenolic on aluminum: "Apply pressure: 3000-4000 psi for phenolic", "Heat to 150-180°C and hold for 5-8 minutes", "Cool under pressure to room temperature" ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Copy the sheet's numbers into the SOP and check them against these. Then the SOP works without the sheet. |
| Black Bakelite (phenolic) | Phenolic is listed under "Lower edge retention", and shrinks 0.006 in/in against 0.001–0.003 for glass-filled epoxy or DAP. Graphite- or copper-filled phenolic "is electrically conductive end-to-end through the mount", and "A conductive mount drains the charge to the SEM stage." For aluminum: "The sample must be conductive for SEM; either use a conductive mounting resin or sputter-coat" ([mounting](https://www.metallographic.com/guides/mounting); [aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Optional: graphite-filled conductive phenolic, PACE [`CONDUCTO`](https://shop.metallographic.com/products/conducto), $44 per lb. It adds only C. If the SEM takes 1¼″ mounts (SOP open question 2), the puck is grounded through the mount itself, with no carbon-tape bridge. Avoid the copper-filled version, since Cu is one of AlSi10Mg's specified elements. |
| (heat) | "A 150°C mount cycle is effectively a small further age and can shift the precipitate distribution being analyzed." PACE recommends castable epoxy for "A356-T6, and similar age-hardened alloys". ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | No change for EDS: a few minutes at 150-180 °C doesn't change composition. It would matter for hardness or microstructure work on as-built AlSi10Mg. |

## Step 3: belt sander

| SOP | PACE | Proposed change |
|---|---|---|
| Belt-sand until all Bakelite is off the face | PACE's aluminum method has no belt step. It starts on P1200 alumina paper, "grind until the sample is plane". PACE calls its belt grinder "the right tool for coarse planarization of hard ferrous specimens". "It is possible to create more damage in grinding than in sectioning. Starting with too coarse an abrasive drives deformation deeper into the specimen than the original cut." The damage under each grit "runs roughly 3 to 5 times the abrasive particle diameter". ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation); [grinding](https://www.metallographic.com/guides/grinding-techniques)) | Write the belt's grit into the SOP. Stop as soon as metal shows over the whole face, using light pressure, because Step 4 has to grind out everything the belt damaged. If the belt is coarse (60-120 grit), consider skipping it and taking the Bakelite skin off on the first paper of Step 4 instead. |
| "moving it side to side across the belt" | "Push the sample in smooth, unidirectional strokes against the SiC roll, covering the full belt width so the paper wears evenly." "Whatever the motion, keep contact uniform across the specimen face." ([grinding](https://www.metallographic.com/guides/grinding-techniques)) | Add: hold the puck flat. Rocking it grinds facets into the face. |

## Step 4: grinding

| SOP | PACE | Proposed change |
|---|---|---|
| SiC 320, 400, 600, 800, 1200 "(verify these values, they could be off)" | For aluminum: "600 grit (P1200) ALO paper: Water lubricant, light force (5-10 lb / 22-45 N), 100/100 rpm head/base, grind until the sample is plane", then 800 (P2400) SiC, then "1200 grit (P4000) SiC paper: Water lubricant, 5-10 lb, 100/100 rpm, 1 minute." "ALO does not embed into aluminum the way SiC does". Also: "one P500 or P1200 alumina paper can replace the full SiC sequence of 240, 320, 400, and 600 grit", though "The alumina shortcut does not apply when you need very heavy stock removal (still requires coarse SiC)". ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation); [grinding](https://www.metallographic.com/guides/grinding-techniques)) | The numbers are right: they are standard US (ANSI) grits and the usual SiC sequence. For aluminum, PACE replaces the 320, 400 and 600 SiC with one P1200 alumina paper, [`ALO-2112-P1200`](https://shop.metallographic.com/products/alo-2112-p1200) (12″ plain back, $145 per 100). Start on P500 alumina ([`ALO-2112-P500`](https://shop.metallographic.com/products/alo-2112-p500), $145) instead if the belt leaves deep scratches. Keep the 800 and 1200 SiC, briefly. Measure the disc against the ring before ordering, as with the SiC papers on 09-23. |
| (why it matters) | Buehler ground Al-7%, -12% and -20% Si alloys through 120-600 SiC: "SiC particles can become embedded in aluminum alloys. In general, this problem varies with alloy composition and usually arises with the finer grit size papers." PACE's aluminum troubleshooting says embedded grains are "likely SiC pressed in from the fine-grind steps". ([Buehler Tech-Notes 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf); [aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Every embedded SiC grain reads as Si in EDS. Fewer SiC papers, each run for a short time, means fewer grains for Steps 5 and 7 to remove. |
| "There is a 1200 plain and 1200 fine" | PACE's aluminum method uses one 1200 (P4000) SiC paper, for 1 minute. | The plain 1200 is enough, as the person helping you said. Drop the 1200 fine. |
| "Gentle settings (from top down) are 35, 30, 150", no labels | "light force (5-10 lb / 22-45 N), 100/100 rpm head/base". "Match base and head speeds, same direction, for damage-sensitive materials (the 100/100 rule)." Matched rotation "cancels the velocity differential at the specimen, which preserves inclusions and brittle phases, produces a uniform finish, and gives a flat surface across the specimen." ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation); [polishing](https://www.metallographic.com/guides/polishing-methods); [grinding](https://www.metallographic.com/guides/grinding-techniques)) | Write the label and unit next to each number. If 35 is newtons, it is inside PACE's range (35 N is about 8 lb); if it is pounds, it is 3.5 times PACE's maximum. Set the head and table to the same speed, turning the same way, 100/100 if the machine allows. Step 7 already asks for this. |
| No time per paper; "continuously checking" | "Most grinding steps fall in the 1-2 minute range". "If you're still grinding after 2-3 minutes and not seeing progress, the paper is glazed; replace it." On embedded SiC: "the SiC paper was glazed or over-loaded; replace it next time." ([grinding](https://www.metallographic.com/guides/grinding-techniques); [aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Add: about 1 minute per paper. If a paper stops cutting, put on a fresh one rather than grinding longer. |
| Water rinses between papers | "Ultrasonic cleaning for 30-60 seconds is the gold standard when available". Before polishing: "Clean the sample ultrasonically between every step. The single most common cause of 'mystery scratches' is carry-over of a coarser abrasive." ([grinding](https://www.metallographic.com/guides/grinding-techniques); [polishing](https://www.metallographic.com/guides/polishing-methods)) | Keep the water rinses between papers. Add 30-60 s in the ultrasonic after the 1200 paper, before the alumina pad, in the lidded glass container as in Step 6. |
| "Wear gloves" | (Not PACE. Ronnie's [ASTM E1078 notes](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4400486364): "Use powder-free gloves".) | Say powder-free nitrile. |

## Step 5: 1 µm alumina on the Imperial pad

| SOP | PACE | Proposed change |
|---|---|---|
| "Set time to 3 minutes"; repeat "until there are no more visible scratches (verify this piece of info)" | "Stop a step when the previous scratch pattern is gone, not when a timer reaches a number. Over-polishing is the most common operator error: it rounds edges, pulls inclusions, and produces relief between phases of different hardness." PACE's 1 µm step on aluminum runs 2 minutes. ([polishing](https://www.metallographic.com/guides/polishing-methods); [aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | New stop rule: stop when the 1200 scratches are gone under the optical microscope. Fine alumina scratches are expected, and Step 7 removes them. Use 1-2 minute runs instead of 3. |
| Machine settings not stated | PACE uses the same "light force (5-10 lb / 22-45 N), 100/100 rpm head/base" for its 1 µm step on aluminum. ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Say which settings to use. The same as Step 4 is fine. |
| (if the 1200 scratches won't clear) | For cast Al-Si alloys, PACE adds "an intermediate 3 µm DIAMAT diamond on ATLANTIS pad step" before 1 µm, because "These harder alloys leave residual SiC scratches that 1 µm diamond alone won't fully clear". ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Nothing to add yet. If Step 5 regularly needs more than a few runs, a 3 µm step is PACE's fix. |
| 1 µm alumina on the Imperial (napped, flocked) pad | PACE's aluminum method uses 1 µm diamond on its low-nap ATLANTIS pad, but also says alumina slurries are "common for soft-metal rough polishing". On napped, flocked pads: "Keep times short; high nap rounds edges." For multi-phase materials: "Use harder, lower-nap pads to keep all phases in the same plane." ([aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation); [polishing](https://www.metallographic.com/guides/polishing-methods)) | Keep the alumina and pad you have, with short runs. If the SEM shows relief around the Si network, try a low-nap pad next, such as PACE [`ATL-3012`](https://shop.metallographic.com/products/atl-3012) (12″ adhesive back, $95 for 5). |
| "Don't use water on the polishing pad" | "Rinse the polishing pad and specimen with distilled or deionized water for the last 10-15 seconds of polishing to clean both surfaces." ([cleaning](https://www.metallographic.com/metallographic-consumables/cleaning)) | Keep the machine's water off. Add: for the last 10-15 s of each run, squirt DI water from the bottle onto the turning pad. It lifts the alumina off before it can dry on the face. |
| 6-7 circles of alumina before lowering the puck, then more as needed | "Wet the pad with the suspension before applying the specimen." "Drip or spray suspension continuously. A dry pad polishes nothing and damages the specimen." ([polishing](https://www.metallographic.com/guides/polishing-methods)) | No change. |
| Pad reused for one alloy; replace it if it rips | "Dedicate each pad to one abrasive size." "Replace pads when they glaze, embed contaminants, or no longer wet uniformly." ([polishing](https://www.metallographic.com/guides/polishing-methods)) | Add PACE's other signs: replace the pad when it is glazed or no longer wets evenly. |
| Dry with "compressed air from the fume hood" | "Dry the surface with filtered, oil-free compressed gas (shop air carries oil and moisture that will recontaminate the specimen)". For aluminum: "Compressed air only, no heated drying". ([cleaning](https://www.metallographic.com/metallographic-consumables/cleaning); [aluminum](https://www.metallographic.com/guides/aluminum-sample-preparation)) | Use a filtered, oil-free source: bottled nitrogen, a can of non-flammable gas (PACE [`AIR-1000`](https://shop.metallographic.com/products/air-1000), $14), or an oil-removing filter on the hood line. This applies in Steps 5-8. |
| Names the Allied alumina; the bottle on the shelf is OnPoint Alumabrasive | "Use polycrystalline alumina (not calcined gamma alumina) for the final step. Gamma alumina aggregates and scratches soft metals." ([polishing](https://www.metallographic.com/guides/polishing-methods)) | OnPoint's page doesn't say which kind Alumabrasive is. With the film now doing the final polish, this matters less. Update the name. |

## Step 6: cleaning

| SOP | PACE | Proposed change |
|---|---|---|
| Ultrasonic "for however long is needed" | "Use an appropriate surfactant solution and clean for 1-3 minutes, followed by a water rinse." ([cleaning](https://www.metallographic.com/metallographic-consumables/cleaning)) | Write 1-3 minutes. |
| Haze: "repeat ultrasonication until haze is no longer present" | Polycrystalline alumina particles "electrostatically coat the specimen surface and look like a matte film after rinsing. The polish underneath is fine. Wipe gently with a cotton ball and a cleaning solution (PACE ULTRACLEAN 2, or soapy water)". For a matte film: "Lightly remove particles with a cotton swab and anhydrous alcohol; if the film persists, briefly return to final polish with an on-platen water rinse". ([polishing](https://www.metallographic.com/guides/polishing-methods); [cleaning](https://www.metallographic.com/metallographic-consumables/cleaning)) | Replace repeated ultrasonics with a gentle wipe using a cotton swab wet with anhydrous ethanol or IPA. Keep the rule against paper towels. The DI rinse in Step 5 should make the haze rarer. |
| "Spray with ethanol" | "rinse or dip the specimen in anhydrous alcohol to displace residual water". "Diluted alcohol such as 70% IPA still carries enough water to leave spots." ([cleaning](https://www.metallographic.com/metallographic-consumables/cleaning)) | Say 200-proof (anhydrous) ethanol. |
| Methanol in the lidded glass container | PACE's alcohol is "anhydrous (≥99%) isopropyl alcohol or ethanol". It doesn't mention methanol. ([cleaning](https://www.metallographic.com/metallographic-consumables/cleaning)) | Optional: use ethanol or IPA instead. Methanol is the most toxic of the three, and Step 8 already allows IPA. |
| "fill with 1/4-1/2 inch of deionized water" | (Not PACE. A typical ultrasonic cleaner manual: "The cleaning bath must not be operated with liquid levels below the minimum level line", or "serious damage may be caused to the generator and transducers." [RS manual](https://docs.rs-online.com/25c8/0900766b800caea5.pdf)) | Fill to the line marked in our unit's tank. A quarter inch is probably below it, and the water has to reach well up the glass container for the ultrasound to get into it. |

## Already in line with PACE

- **Rinsing between papers:** the puck, holder, rings and table, with the water washing away from the sample.
- **Moving on only when the old scratches are gone:** "Visual inspection of the scratch pattern is always the better indicator."
- **One pad per alloy, labeled and bagged with its backing back on.**
- **Single-use papers.** This is stricter than PACE, which plans on "5 to 8 per fine paper", and there is no reason to relax it.
- **Never wiping the face with a paper towel, and never setting it face down.**
- **DI water for rinsing the polished face:** "Always use distilled or deionized water for final cleaning."
- **No heat when drying:** "Compressed air only, no heated drying".
- **Solvent only in the lidded glass container, never in the tank.**
- **No 90° turn between papers on the polisher:** "On a rotating platen, scratches are multidirectional, so rotation matters less".

## If all of it is adopted

| What | PACE part | Price |
|---|---|---:|
| P1200 alumina paper, 12″ plain back, 100 | [`ALO-2112-P1200`](https://shop.metallographic.com/products/alo-2112-p1200) | $145 |
| P500 alumina paper, only if P1200 can't clear the belt scratches | [`ALO-2112-P500`](https://shop.metallographic.com/products/alo-2112-p500) | $145 |
| Blade dressing stick | [`DRES-0010`](https://shop.metallographic.com/products/dres-0010) | $15 |
| Non-flammable compressed gas, 10 oz | [`AIR-1000`](https://shop.metallographic.com/products/air-1000) | $14 |
| Optional: graphite conductive phenolic, 1 lb | [`CONDUCTO`](https://shop.metallographic.com/products/conducto) | $44 |
| Optional: ATLANTIS low-nap pad, 12″, 5 | [`ATL-3012`](https://shop.metallographic.com/products/atl-3012) | $95 |

List prices from the PACE store on 2026-10-06, before shipping and tax.

## Questions this adds

1. What grit is the belt in Step 3?
2. Is the PSC's blade high or low concentration, and does the PSC have a dressing stick?
3. What does the press's laminated sheet say (temperature, pressure, heat and cool times)?
4. What are 35, 30 and 150, with units? (Already open question 1 in the SOP.)

## Sources

- PACE Technologies guides: [Aluminum Sample Preparation](https://www.metallographic.com/guides/aluminum-sample-preparation),
  [Sectioning](https://www.metallographic.com/guides/sectioning), [Mounting](https://www.metallographic.com/guides/mounting),
  [Grinding Techniques](https://www.metallographic.com/guides/grinding-techniques),
  [Polishing Methods](https://www.metallographic.com/guides/polishing-methods) and
  [Cleaning & Drying](https://www.metallographic.com/metallographic-consumables/cleaning). The aluminum guide
  says its recipes "come directly from" Zipperian's *Metallographic Handbook*, Section 11.1.1.
- Buehler, [*Tech-Notes* 3(2)](https://www.buehler.com/assets/solutions/technotes/vol3_issue2.pdf), on preparing
  Al-7.15%, 11.82% and 19.85% Si alloys.
- RS Components, [ultrasonic cleaning tank instructions](https://docs.rs-online.com/25c8/0900766b800caea5.pdf)
  (RS 196-6591 / 196-6608), for the minimum water level.
- Ronnie's ASTM E1078 notes, [#77](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4400486364).

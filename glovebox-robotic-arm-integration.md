# Glovebox Options for Robotic Arm Integration

Follow-up research to [`glovebox-options.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8979061/glovebox-options.md) (added in [PR #78](https://github.com/vertical-cloud-lab/byu-vcl/pull/78)), narrowed to one question: **which gloveboxes can house a robotic arm without a custom build?**

The earlier document optimized for a human working through glove ports, with the powder doser as the largest thing inside. This one assumes a robot arm is a first-class occupant of the box. That changes which specifications actually bind, and it changes the shortlist.

Prices below were gathered on **2026-09-15**. See [How pricing was gathered](#how-pricing-was-gathered) for provenance and caveats.

## Why this is a different specification

| Constraint | Human-operated box | Robot-integrated box |
|---|---|---|
| **Getting equipment in** | Antechamber is enough — samples and small tools | A 6-axis arm does not fit through a Ø150–390 mm antechamber. You need a **removable panel or a large equipment door**, or you accept a full purge-down every time the arm comes out |
| **Feedthroughs** | A few banana plugs for battery cycling | **Multiple KF-40 (or larger) flanges** for motor power, Ethernet/EtherCAT, E-stop, and optionally pneumatics — the controller stays outside the box |
| **Floor** | A work surface | A **mounting surface**: flat, rigid, bolt-down, and load-rated. A moving arm applies reaction torques, not just static weight |
| **Internal height** | Comfortable reach | Arm reach envelope **plus** the tallest tool, plus clearance so the elbow does not strike the window |
| **Thermal** | Negligible | The arm dumps heat into a sealed box with no convective path out. A-Lab GPSS runs **air conditioning holding 24 °C ± 1 °C** — that is a designed-in subsystem, not an afterthought |
| **Atmosphere load** | Operator and samples | Continuous **outgassing** from cable jackets, connector plastics, and gearbox greases, loading the purifier around the clock |
| **Particulates** | Metal powder | Metal powder **plus** gearbox, belt, and cable-carrier wear |
| **Maintenance** | Open the box | The arm must be serviceable **through glove ports**, or every service call costs a purge cycle |

The last row is the one most often underestimated, and it has a published design rule attached — see below.

## Prior art: this has been done, and the lessons are documented

**[A-Lab GPSS, UC Berkeley](https://arxiv.org/abs/2604.11957)** (A-Lab for Glovebox Powder Solid-state Synthesis) is the closest published analogue to what the VCL wants — automated powder dispensing, mixing, heating, grinding, and XRD prep, all air-free.

- Enclosure: a **customized double-glovebox**, five workstations inside
- Robots: **two Universal Robots UR5e arms mounted on the glovebox floor**, bridged by a **linear rail** so samples hand off without the arms having to reach each other
- Atmosphere achieved: **< 0.1 ppm O₂, < 10 ppm H₂O**
- Thermal: **air conditioning at 24 °C ± 1 °C**
- Layout rule, quoted in substance from the paper: equipment that needs **low maintenance** (e.g. furnaces) goes **along the centerline** where manual access is poor; equipment that **needs servicing** goes **along the sidewalls**, reachable through the glove ports. Space is packed densely with a **vertical stacking strategy** while preserving clearance for robot motion.

That layout rule should be treated as a hard constraint on any box we buy: **the robot's serviceable parts have to fall inside glove reach.**

Other relevant precedent:

- **[Etelux](https://www.etelux-glovebox.com/robotic-arm-inside-a-glove-box/)** sells robotic-arm-in-glovebox as a catalogue solution
- **[Allum Corp](https://www.allumcorp.com/products/robot-integrated-glovebox/)** offers a robot-integrated glovebox with a 3-axis arm for dividing, mixing, and weighing — very close to our powder-dosing use case
- Nuclear glovebox robotics is a mature field worth borrowing from: the [Sellafield robotic arm retrofit](https://www.world-nuclear-news.org/articles/robotic-arm-improves-glovebox-safety-at-sellafield), AtkinsRéalis' **ARGO** drop-in arm for *existing* gloveboxes, and a Los Alamos-partnered UR5 integration. The retrofit path — buy a good box, add the arm later — is a proven pattern, not a compromise

## How pricing was gathered

Vendor and reseller pages routinely block GitHub Actions runners. Fetching the same URLs from the lab's Raspberry Pi over Tailscale (a university-network IP, not a datacenter IP) gets through:

| URL | From CI runner | From the Pi |
|---|---|---|
| `terrauniversal.com/glove-boxes-isolators.php` | **HTTP 403** | **HTTP 200** |
| `msesupplies.com/...` | HTTP 200 | HTTP 200 |
| `robotshop.com/...` | — | HTTP 403 (Cloudflare — blocked from both) |

Several vendors also show "Price: RFQ" in the page body while carrying a real number in the structured product data. Those are reported below as store-data prices and flagged as such — treat them as indicative, not as a quote.

**Everything below is a list/asking price, not a quote.** Academic discounts, freight, and installation are not included.

## Tier A — Used, purifier-equipped, already feedthrough-rich

This is the tier that actually solves the robot problem, because these boxes were built for OEM integration and **already have the flanges**. Current [UsedGlovebox.com](https://usedglovebox.com/gloveboxes) inventory (read 2026-09-15):

| Item | System | Why it matters for a robot |
|---|---|---|
| **25-319** | Vacuum Technology Inc. **Universal 1800/750/900, 6-port**, gas purifier, mfg 2021 | **20 × KF-40 feedthroughs.** 1800 mm (71") wide. This is the single most robot-ready listing found — 20 flanges is more than any integration needs |
| **25-320** | VTI **Universal 1800/750/900, 7-port**, purifier, mfg 2020 | **10 × KF-40 feedthroughs**, same 1800 mm envelope |
| **25-322** | VTI **Universal 2440/750/900, 4-port**, purifier, mfg 2022 | 2440 mm (96") wide — room for an arm *and* the doser *and* a linear rail |
| — | **Vigor Sci-Lab SG4800/750TS, 8-port**, purifier, 150 °C heated antechamber, mfg 2021 | 4800 mm (189"). Almost certainly larger than CB154 can take; listed for completeness |
| — | **VAC NEXGEN, 14-port**, three self-contained sections joined by "T" antechambers, purifiers, O₂/H₂O analyzers, 600 °C vacuum oven, freezer, built 2020 | The multi-section architecture is exactly the A-Lab GPSS pattern — transfer between zones without air exposure |
| **25-325** | **MBraun Labmaster Pro SP, 4-port** + MB 200B purifier, LMF inline solvent absorber | Vacuum pump and gloves **not** included |
| **26-331** | **MBraun Labmaster, 3-port** + MB 20G purifier, inline solvent trap, integrated G3P spin coater | Two vacuum pumps required, not included; gloves not included; spin coater works but is outside warranty |

VTI's Universal series states attainable purity of **< 1 ppm O₂ and < 1 ppm H₂O** and ships with a PLC touchscreen controller, O₂/H₂O sensors, large and small antechambers, foot switch, and an Edwards RV-10 pump. Several listings carry a **90-day warranty**, which is unusual on used purifier boxes.

> **Honest limitation:** every one of these is listed **"Call for Pricing"** or **"Make Offer"** — no public numbers, and no amount of fetching from any IP changes that. The nearest comparable data points are the asking prices already in [`glovebox-options.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8979061/glovebox-options.md): MBraun MB200MOD at **$12,349.99**, Vigor SG1200-750TS at **$14,000**, and an [Innovative Technology PurgeLab 1250 at **$40,000**](https://www.labx.com/item/innovative-technology-purgelab-1250-glove-box/DIS-101429-1098696) (EquipNet, via LabX) as a ceiling for 1250 mm purifier systems. Expect the 1800 mm VTI units to land between those. **Getting real numbers on items 25-319 and 25-322 is the highest-value next action in this document.**

## Tier B — New, published price, and big enough

| Product | Price (2026-09-15) | Chamber | Access for a robot | Purifier? |
|---|---|---|---|---|
| **[MSE PRO GBV-3, 798 L](https://www.msesupplies.com/products/mse-pro-gbv-3-798l-stainless-steel-vacuum-glove-box)** | **$10,502.95** | 1200 × 700 × 950 mm (47" × 27.6" × 37.4") | Transition chamber Ø350 × 400 mm **and a 450 × 600 mm left door** — the door is what makes arm installation practical | ❌ **No.** MSE state plainly it is "a basic vacuum/inert gas glove box, **not** a fully automated purification glove box system" |
| [MSE PRO GBV-3 frame](https://www.msesupplies.com/products/frame-for-mse-pro-gbv-3-stainless-steel-vacuum-glove-box) | $769.95 | — | — | — |
| [MSE PRO GBV-3 vacuum pump](https://www.msesupplies.com/products/vacuum-pump-for-mse-pro-gbv-3-stainless-steel-vacuum-glove-box) | $1,895.95 | — | — | — |
| [MSE PRO GBV-2, 338 L](https://www.msesupplies.com/products/mse-pro-gbv-2-338l-stainless-steel-vacuum-glove-box) | $6,983.95 | — | Smaller — marginal for a 664–700 mm arm | ❌ |
| MSE PRO GBV-1, 150 L | $5,734.95 | — | Too small for an arm | ❌ |
| **[MSE PRO Single-Station Glove Box for Battery Research](https://www.msesupplies.com/products/mse-pro-single-station-glove-box-for-battery-research)** | **$40,912.95** | — | — | ✅ Purification system included |
| MSE PRO Double-Station Glove Box for Battery Research | **$43,762.95** | — | — | ✅ |
| [MSE PRO stainless compact + antechamber](https://www.msesupplies.com/products/mse-pro-economy-compact-laboratory-stainless-steel-glove-box-with-antechamber) | $5,930.95 (**$6,540.95** with support stand) | 600 × 400 × 500 mm | Too small for an arm | ❌ |
| [Cleatech 2-port acrylic vacuum + airlock](https://www.cleatech.com/product/vacuum-glovebox-with-airlock/) | $5,580.00 | 26" × 18" × 20" | Acrylic — not groundable, see safety note | ❌ |
| [MTI VGB-1](https://www.mtixtl.com/products/vgb1) | **$4,698.00** in store data, page displays "Price: RFQ" | 22" × 17" × 16" | Too small for an arm | ❌ |

**The GBV-3 is the interesting entry in this tier.** At **$13,168.85** for box + frame + pump it is the cheapest new stainless enclosure found that a 664–700 mm arm plausibly fits inside, and the **450 × 600 mm side door** means you can install and service the arm without dismantling anything. The catch is equally clear: no purifier, so it is a purge/vacuum box in the hundreds-of-ppm class until one is added — the same trade-off as the $2,999 Alabama Labconco in the existing document, but stainless (groundable) and with a door an arm fits through.

**The two battery-research boxes at ~$41K–$44K are the honest comparison against a new LC-100 (~$34K).** They include purification; the GBV series does not.

## Tier C — New automation platforms (RFQ only)

| Vendor | Platform | Robot-relevant capability |
|---|---|---|
| **[LC Technologies](https://lctechinc.com/)** | LC-100 / LC-180 / LC-200 | **Already quoting us** (~$34K–$54K with the 25% academic discount) and recommended by Drs. Porter and Rappleye. No published robot-integration offering — but a US manufacturer mid-quote is the cheapest possible place to ask for extra KF flanges and a removable panel. **Ask before comparing anything else** |
| **[Inert Corp](https://www.inertcorp.com/gloveboxes/purelab/)** | PureLab HE (2GB/3GB/4GB) | Explicitly "fully automated platform allowing for easy integration of OEM equipment"; modular; Siemens SIMATIC S7-1200 PLC + HMI. Internal dims: **2GB 1250 × 780 × 900 mm**, **3GB 1500 × 780 × 900 mm** |
| **[MBraun](https://www.mbraun.com/products/glovebox-workstations/unilab-pro-glovebox/)** | UNIlab Pro / LABmaster Pro | Modular, 2/3/4 gloves, single or double sided, housings combinable; markets integration with third-party devices and fully automated processing lines |
| **[Etelux](https://www.etelux-glovebox.com/robotic-arm-inside-a-glove-box/)** | Standard / Lab2000 series | The only vendor found that advertises **robotic arm integration as a product**. Lab2000 comes in 1200/1500/1800/2400 mm. Chinese-made, typically quotes well under MBraun — useful as a negotiating lever |
| **[Allum Corp](https://www.allumcorp.com/products/robot-integrated-glovebox/)** | Robot-integrated glovebox | 3-axis arm that divides, mixes, and weighs — closest catalogue match to powder dosing. Storefront carries no price (structured data shows `0`); RFQ only |

## Robot arms: real prices and glovebox suitability

| Arm | Price | Payload | Reach | Glovebox-relevant notes |
|---|---|---|---|---|
| **[igus ReBeL 6-DOF](https://rbtx.com/en-US/components/robots/rebel-cobot-6-degrees-of-freedom-reach-664-mm)** | **$7,499** | 2 kg (0.5 kg at rated 7 picks/min) | 664 mm | **Dry-running, self-lubricating polymer strain-wave gears — no grease at all.** That is the single best outgassing and contamination profile of this group for a sealed box. `igumid ESD` conductive material is offered, which matters for Al/Mg powder. Trade-off: lowest rigidity and accuracy; polymer construction needs the ESD variant to be groundable |
| **[UFACTORY xArm 6](https://www.ufactory.us/product/ufactory-xarm-6)** | **$9,500** list (street ~$8,849) | 5 kg | 700 mm | 12.2 kg, IP40, harmonic drives, aluminium/carbon-fibre. Best payload-per-dollar. **Listed out of stock at ufactory.us on 2026-09-15** |
| **Mecademic Meca500** | ~**€17,960** ex-VAT; used from **$16,425** | 0.5 kg | 330 mm | Embedded controller (no separate cabinet), 0.005 mm repeatability, smallest footprint of any 6-axis arm. Good if the box is tight; payload likely too low for crucibles |
| **[Dobot CR5](https://www.robotlab.com/store/dobot-cr5/)** | **$22,980** | 5 kg | 900 mm | Longer reach; RaaS leasing offered |
| **Universal Robots UR5e** | **$35,000–$48,000** | 5 kg | 850 mm | **What A-Lab GPSS runs.** Discontinued, superseded by the UR7e — which makes the used market worth watching. The safest choice if we want to copy a working published system |

**None of these are sold as inert-atmosphere-rated.** Every vendor above would need to confirm, in writing, behaviour in dry argon: grease compatibility, outgassing rate, and whether operating without convective cooling voids the warranty. The ReBeL's grease-free design sidesteps most of that question, which is why it leads the table despite being the weakest arm.

## Integration engineering notes

1. **Heat is the constraint people miss.** A sealed box has no convective path to room air. A-Lab GPSS conditions to 24 °C ± 1 °C; budget for either a glovebox chiller/AC option or a cold-plate on the arm base. Also note a second-order effect: **gas purifier performance and O₂/H₂O sensor calibration both drift with temperature**, so thermal control protects the data, not just the hardware.
2. **Put the controller outside.** Every arm here has a separate control box except the Meca500. Outside means less heat, less outgassing, and service without a purge — and it is exactly what the KF-40 feedthroughs on the VTI units are for.
3. **Outgassing loads the purifier continuously.** Cable jackets, connector bodies, and greases release volatiles into a closed loop. Ask any used-box seller what purifier media age is, and assume a robot shortens regeneration intervals.
4. **Particulates cut both ways.** Al/Mg powder is the hazard we already track; gearbox and cable-carrier wear is a *new* contaminant that lands in the powder. Sealed/dry-running gearboxes and cable carriers rated for cleanroom use are worth the premium.
5. **Grounding still governs, and now it includes the robot.** Per [NFPA 484 and the safety notes already in `glovebox-options.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8979061/glovebox-options.md#safety-considerations), static discharge is a primary ignition source for Al/Mg powder. A stainless box is groundable; **a polymer-bodied arm inside a grounded box is not**, unless specified in a conductive/ESD material. This alone rules out acrylic enclosures for a robot-plus-powder cell.
6. **Design for service through the glove ports.** Follow the A-Lab rule: the arm's serviceable side faces a glove port, and long-lived equipment goes down the centerline.
7. **Measure the door, not just the chamber.** An arm that fits the chamber but not the transfer port means every maintenance event is a full purge-down. The GBV-3's 450 × 600 mm side door is the specific feature that makes it viable at its price.

## Cost scenarios

Enclosure + arm only. Freight, installation, tooling, and grippers excluded.

| | Scenario 1 — Staged | Scenario 2 — Used, purifier-equipped | Scenario 3 — New, turnkey |
|---|---|---|---|
| Box | MSE PRO GBV-3 + frame + pump | VTI Universal 1800/750/900 (item 25-319, 20 × KF-40) | LC Technologies LC-100/LC-180, robot options added |
| Box cost | **$13,168.85** (verified list) | **RFQ** — estimate $15K–$25K by comparison to MB200MOD ($12.3K) and PurgeLab 1250 ($40K) | **~$34K–$54K** (existing quotes, 25% academic discount) |
| Arm | igus ReBeL — **$7,499** | UFACTORY xArm 6 — **$9,500** | UR5e-class — **$35K–$48K** |
| Subtotal | **~$20.7K** | **~$25K–$35K** (est.) | **~$70K–$100K** (est.) |
| Atmosphere | Purge only, 100s of ppm until a purifier is added | **< 1 ppm O₂ / < 1 ppm H₂O** | **< 1 ppm O₂ / H₂O** |
| Feedthroughs | Would need to be added | **Already present (20 × KF-40)** | Spec them into the quote |
| Warranty | New | 90 days on several listings | 2 yr + free install/training |
| Main risk | No purifier; ppm-level work needs a later upgrade | Condition unknown until inspected; price unknown until RFQ | Cost |

## Recommendation

1. **Ask LC Technologies first, this week.** We are mid-quote with a US manufacturer that BYU faculty already recommend. Adding **extra KF-40 feedthroughs and a removable side panel** to an LC-100/LC-180 quote is a cheap question with a potentially decisive answer — a robot-ready new box with a 2-year warranty and free installation would collapse most of the trade-offs in this document. Nothing else should be decided before that answer arrives.
2. **In parallel, RFQ UsedGlovebox.com items 25-319 and 25-322.** The 1800 mm VTI with **20 × KF-40 feedthroughs** is the best-matched hardware found anywhere in this search, purifier included and < 1 ppm rated. Its only unknown is price. Item 25-322 (2440 mm) is the one that comfortably fits an arm, the doser, and a linear rail in the A-Lab pattern.
3. **Treat the MSE PRO GBV-3 at $13,168.85 as the fallback, not the target.** It is the cheapest credible *stainless* enclosure with a door an arm fits through, and it is groundable — a real advantage over the fiberglass-lined Labconco path for Al/Mg work. But it ships without a purifier, so it buys a robot cell at purge-level atmosphere, and the ppm-grade upgrade is a separate later purchase.
4. **Start with the igus ReBeL at $7,499 for arm-side de-risking.** Grease-free polymer gearing is the lowest-contamination option available, an ESD variant exists for the powder hazard, and at 10–20% of a UR5e the cost of learning that a sealed argon box needs more thermal management than expected is small. Move up to an xArm 6 or UR-class arm once the enclosure and thermal design are proven. If we instead want to replicate A-Lab GPSS directly, the UR5e is the arm to match — and its discontinuation means used units should be tracked.
5. **Do not put a robot in an acrylic box.** The Cleatech and MSE acrylic options remain fine for human powder storage; they are groundable by no one, and a moving arm generating static next to Al/Mg powder is the specific scenario NFPA 484 exists for.

## Questions to put to vendors

**To LC Technologies (highest priority — we are already in their quote pipeline):**
- Can an LC-100/LC-180 be supplied with additional KF-40 (or larger) feedthroughs, and how many?
- Is a removable side or rear panel available, sized to pass a ~700 mm-reach arm (~12–20 kg)?
- What is the floor load rating, and can it take bolt-down mounting?
- Is a chiller or air-conditioning option offered for continuous internal heat load?
- Have you supplied a box with a customer-installed robot before, and what did it need?

**To used-box sellers (items 25-319, 25-320, 25-322):**
- Price, and what is included (pump, gloves, sensors, purifier media age)
- Exact internal dimensions and **floor-to-window clearance**
- Feedthrough count, size, and current occupancy — how many KF-40s are actually free
- Leak-rate test results (ISO 10648-2) and last purifier regeneration
- Electrical supply required (208/230 V single or three phase) — route past Physical Facilities early
- Crated dimensions and weight, to reuse the freight/rigging analysis already done in [PR #78](https://github.com/vertical-cloud-lab/byu-vcl/pull/78)

**To robot vendors (igus, UFACTORY, Universal Robots):**
- Rated or tested behaviour in dry argon at < 1 ppm O₂/H₂O
- Outgassing data for cable jackets, connector bodies, and any lubricant
- Heat dissipation at typical duty cycle, and whether still-air operation voids warranty
- Availability of an ESD-safe / conductive variant, and how to bond it to a grounded box
- Whether the control box can sit outside with the umbilical passing through a KF-40 flange, and the maximum cable length

## Next steps

- [ ] Ask LC Technologies about feedthroughs, removable panels, floor load rating, and thermal options on the LC-100/LC-180 quotes already in flight
- [ ] RFQ UsedGlovebox.com items **25-319** (1800 mm, 20 × KF-40) and **25-322** (2440 mm) — the only real unknown on these is price
- [ ] Measure CB154: door width, ceiling height, and available floor footprint, against an 1800 mm and a 2440 mm box ([cb154-annotated.pdf](https://github.com/vertical-cloud-lab/byu-vcl/blob/e127103/cb154-annotated.pdf) is in this repo)
- [ ] Measure the powder doser (footprint, height with hopper clearance) and decide the arm's required reach envelope from that, not from the catalogue
- [ ] Get written answers on inert-atmosphere operation from igus and UFACTORY before committing to an arm
- [ ] Decide whether the goal is a **robot cell** (buy for the arm now) or a **robot-ready box** (buy the best box now, retrofit the arm later, as Sellafield and ARGO do) — this choice sets the budget more than any product on this page
- [ ] Reconcile with the tiering already agreed in [`glovebox-options.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/8979061/glovebox-options.md): none of the options here replace the LC Technologies systems for battery-grade work

## Sources

Glovebox and automation: [A-Lab GPSS (arXiv 2604.11957)](https://arxiv.org/abs/2604.11957) · [Etelux robotic arm in a glovebox](https://www.etelux-glovebox.com/robotic-arm-inside-a-glove-box/) · [Allum Corp robot-integrated glovebox](https://www.allumcorp.com/products/robot-integrated-glovebox/) · [Inert PureLab HE](https://www.inertcorp.com/gloveboxes/purelab/) · [MBraun UNIlab Pro](https://www.mbraun.com/products/glovebox-workstations/unilab-pro-glovebox/) · [LC Technologies](https://lctechinc.com/) · [Sellafield robotic arm retrofit](https://www.world-nuclear-news.org/articles/robotic-arm-improves-glovebox-safety-at-sellafield)

Pricing: [UsedGlovebox.com inventory](https://usedglovebox.com/gloveboxes) · [MSE PRO GBV-3](https://www.msesupplies.com/products/mse-pro-gbv-3-798l-stainless-steel-vacuum-glove-box) · [MSE PRO glove boxes](https://www.msesupplies.com/collections/mse-pro-glove-boxes) · [Cleatech vacuum glovebox](https://www.cleatech.com/product/vacuum-glovebox-with-airlock/) · [MTI VGB-1](https://www.mtixtl.com/products/vgb1) · [LabX PurgeLab 1250](https://www.labx.com/item/innovative-technology-purgelab-1250-glove-box/DIS-101429-1098696)

Robot arms: [igus ReBeL on RBTX](https://rbtx.com/en-US/components/robots/rebel-cobot-6-degrees-of-freedom-reach-664-mm) · [igus ReBeL product page](https://www.igus.com/automation/rebel-cobot) · [UFACTORY xArm 6](https://www.ufactory.us/product/ufactory-xarm-6) · [Dobot CR5 (RobotLab)](https://www.robotlab.com/store/dobot-cr5/) · [Mecademic Meca500](https://mecademic.com/products/meca500-industrial-robot-arm/) · [UR5e pricing survey](https://robotsourced.com/robots/cobots/ur5e/)

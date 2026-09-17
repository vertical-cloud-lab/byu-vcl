# Electronics inside a metal-powder enclosure: what's actually disqualifying

Follow-up research for [#219](https://github.com/vertical-cloud-lab/byu-vcl/issues/219). The
original sourcing note recommended *against* mounting an AirGradient particulate monitor inside the
powder enclosure, citing NFPA 484 and NEC Class II. This document checks that claim properly,
answers the same question for a Raspberry Pi, and enumerates the other equipment and practices that
carry the same hidden problem.

Scope: an AMAZEMET rePowder ultrasonic atomizer producing Al / AlSi10Mg / Al–Si powder at
15–45 µm ([#124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124)), elemental feedstock
across Al, Si, Mg, Ti, Zr, Mn, Cr, Cu, Fe, Ni, Ce, Sc, Li, Er, Zn, Sn
([#161](https://github.com/vertical-cloud-lab/byu-vcl/issues/161)), a CubXL powder doser
([#150](https://github.com/vertical-cloud-lab/byu-vcl/issues/150)), and an interim fume-hood
arrangement in the Dillon lab ([#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195)).

**This is engineering research, not a compliance determination.** Whether your specific setup is a
classified location is a decision for BYU EHS and the authority having jurisdiction (AHJ),
informed by a dust hazard analysis. Everything below is intended to make that conversation
shorter and better-informed.

---

## 1. The short version

The earlier "don't put it inside" conclusion holds, but the strongest reasons are not the ones
originally given.

| Original reason | Status |
|---|---|
| NFPA 484 → NEC Art. 500 Class II, wants dusttight enclosures | Direction right, detail incomplete. Dusttight is the **Division 2** allowance. The *interior* of the enclosure during operation is Division 1 by default, where dusttight alone is not the standard — but the **room** outside it is very likely unclassified if housekeeping is decent (§2). That distinction is the whole design lever. |
| The PM sensor's laser diode is an ignition source | Weakest of the arguments. IEC 60079-28 treats sub-15 mW / Class 1 optical sources as the benign case; the PMS5003T laser is a few mW inside a sealed optical chamber. |
| ASA weatherproof ≠ dusttight in the NEC sense | Correct, and NEC 110.28 says so directly: *"IP ratings are not a substitute for Enclosure Type."* |
| "It's an unrated board with a fan" | This is the real argument, and it's stronger than stated — see below. |

The three reasons that actually carry the weight:

1. **Ignition energy.** Reported MIE for AlSi10Mg is **11–14 mJ**, and 4 mJ for pure Al
   ([Ignition and explosibility of aluminium alloys used in Additive Layer Manufacturing](https://www.sciencedirect.com/science/article/abs/pii/S0950423017303765),
   *J. Loss Prev. Process Ind.*). A static discharge from a person is
   [10–30 mJ](https://stonehousesafety.com/static-electricity-and-combustible-dusts-are-all-electrostatic-discharges-hazardous/),
   with ~90 mJ quoted elsewhere. Your powder's ignition energy sits **below** what a human body
   routinely delivers. Dusts with MIE < 30 mJ are classed as very sensitive to electrostatic
   ignition. This is the number that should drive every decision here.
2. **Aluminum dust is electrically conductive.** Group E is
   [the only NEC dust group treated as conductive](https://ldpi-inc.com/resources/classification-codes/class-2-locations/).
   Conductive dust on an unprotected board bridges traces and connectors, producing exactly the
   arc the MIE number says you cannot afford. A Raspberry Pi's 40-pin header, USB shells and
   microSD contacts are open conductors at ~1 mm pitch.
3. **A fan in a dust-bearing volume is a dust-cloud generator.** Layered dust is a fire; suspended
   dust is a deflagration. Deliberately drawing dust-laden air through a device is the wrong side
   of that line.

Note what is *not* the problem: **hot surfaces and radios**. A Raspberry Pi SoC runs 60–85 °C and a
switch-mode supply somewhat less. Aluminum's dust-cloud MIT is ~690 °C
([Minimum ignition temperatures and explosion characteristics of micron-sized aluminium powder](https://www.sciencedirect.com/science/article/abs/pii/S0950423019309386));
even the worst case found — Al–Mg *stacked layer* self-ignition at
[310–320 °C](https://www.sciencedirect.com/science/article/abs/pii/S0950423023002395) — is 4× the
Pi's surface temperature. Similarly, IEC 60079-0 sets an RF threshold power of
[6 W](https://cdn.standards.iteh.ai/samples/22385/309820fd38c44d1ba9327256b5439cb5/IEC-60079-0-2017.pdf)
for hazardous areas; ESP32 and Pi Wi-Fi run ~0.1 W. Don't spend attention on thermal management or
"is Wi-Fi safe" — spend it on bonding, grounding and keeping conductors out of the dust.

---

## 2. What the standards actually say

### NFPA 484 is now NFPA 660 Chapter 22

NFPA 660, *Standard for Combustible Dusts and Particulate Solids*, was published December 2024 and
consolidates NFPA 61, 484, 652, 654, 655 and 664; metal dusts land in
[Chapter 22](https://www.donaldson.com/en/resources/technical-articles/nfpa-660/). The
[dust hazard analysis](https://ei1.com/understanding-dust-hazard-analysis-preparing-for-nfpa-660-compliance/)
requirement carries over from NFPA 652 with a five-year revalidation cycle. For metal dust the DHA
has to use metal-specific explosibility data and address extinguishing-agent incompatibility.

### Is our powder in scope? Almost certainly yes

- NFPA 484 A.3.3.6.1: *"Any particle that has a minimum dimension of less than 500 microns could
  behave as a combustible dust if suspended in air"* (quoted in Sandia
  [SAND2014-19158PE](https://www.osti.gov/servlets/purl/1242062)).
- NFPA 484 4.1.3: getting *out* from under the standard requires documented non-combustibility
  **proven by testing**, acceptable to the AHJ. There is no published gram- or kilogram-scale
  de minimis exemption. Scale changes the *consequence*, not the applicability.
- The Aluminum Association's
  [F-1 guidance](https://www.aluminum.org/sites/default/files/2021-11/Safe_Handling-Aluminum_Fine_Particles.pdf):
  material at 420 µm (40 mesh) or finer "has the potential for explosion."

15–45 µm feedstock is an order of magnitude below that line, and the atomizer's fines/condensate
tail is below *that*.

### The quantitative criteria: it's dust-layer thickness, not inventory

Classification turns on accumulation and frequency, not on how many kilograms you own. The
practitioner-standard reading of NFPA 499/654 (Rodgers 2011, *Practical issues with electrical area
classification*):

| Layer thickness | Accumulation | Result |
|---|---|---|
| ≥ 1/8 in (3.2 mm) | continuous / frequent | **Class II, Division 1** |
| ≥ 1/8 in | infrequent | **Class II, Division 2** |
| 1/32–1/8 in (0.8–3.2 mm) | continuous / frequent | **Division 2**, if housekeeping holds the average below 1/16 in |
| 1/32–1/8 in | infrequent, cleaned up same shift | **Unclassified** — dusttight enclosures still recommended |
| < 1/32 in (0.8 mm) | — | Generally **unclassified** |

Plus the housekeeping trigger already noted: a 0.4 mm layer over ≥ 5% of the floor area demands
immediate cleaning and can move the classification.

Two consequences worth internalising:

- **Housekeeping is a design control, not just hygiene.** It is literally the variable that decides
  whether your room is a classified location — and therefore whether an ordinary Raspberry Pi in
  the room is legal.
- **Scale does not exempt you.** There is no documented de minimis or small-quantity exemption in
  NFPA 484, 652, 654 or 660. Gram-scale R&D goes through the same DHA; what small scale changes is
  the *consequence*, and often the *extent* of any classified area, not the applicability.

### The Division question, and why Group E is different

NEC 500.5(C)(1) defines Class II Division 1, and subpart (c) is the one that matters:

> *"In which Group E combustible dusts may be present in quantities sufficient to be hazardous"*

Group E is
[combustible metal dust — aluminum, magnesium and their commercial alloys](https://blog.exair.com/2019/01/24/explanation-of-hazardous-locations-class-ii-div-1-groups-e-f-and-g/).
Unlike the organic groups, there is no "abnormal operation only" softening: if Group E dust can be
present in hazardous quantity, you are in Division 1. Practitioners debate the edges of this
([Mike Holt forum](https://forums.mikeholt.com/threads/must-group-e-be-always-division-1-there-is-not-ciidii-group-e.2577591)),
but the drafting intent is clear, and it's why conductive metal dust gets its own clause.

Consequences:

- **Division 2 relief does not apply.** NEC 502.10(B) permits
  [dusttight enclosures in Division 2](https://www.ecmweb.com/national-electrical-code/article/20897735/nec-article-502-class-ii-hazardous-locations);
  Division 1 requires enclosures *identified for the location*.
- **An IP rating is not an Enclosure Type.** NEC 110.28 states
  [IP ratings are not a substitute](https://industrialmonitordirect.com/blogs/knowledgebase/nec-class-ii-div-2-dust-tight-enclosure-requirements-for-industrial-facilities);
  NEMA 12 is dusttight but explicitly not a hazardous-location rating.
- **Surface temperature marking** per NEC 500.8(D)(2) must be below the dust's ignition temperature
  ([165 °C cap for organic dusts that dehydrate or carbonize](https://up.codes/s/class-ii-temperature));
  for aluminum this constraint is generous and, per §1, not the binding one.
- NFPA 499 notes the NEC **zone** system is not to be used for metal dusts, and that combustible
  metal dust is **Group IIIC** regardless of particle size
  ([NFPA 484 TIA](https://docinfofiles.nfpa.org/files/AboutTheCodes/484/TIA_484_22_1.pdf)).
  NFPA 484 likewise treats metal dust as Class II Group E *regardless of particle size*, because the
  NEC's generic combustible-dust definition carries size limits that don't match the metal hazard.
- **The enclosure interior is Division 1 by default.** Where metal dust is normally present during
  operation — atomising, sieving, transferring — the inside of the enclosure classifies as Class II
  Division 1 Group E. The significant exception: if the volume is **inerted below the limiting
  oxygen concentration**, a DHA may support a different conclusion. That is AHJ-dependent, and it
  is the single most valuable thing the rePowder's argon atmosphere buys you.

### The IEC/ATEX framing is more intuitive for an enclosure

Zone 20 is where a dust cloud is present continuously or frequently — explicitly *the inside of
process equipment*. Zone 21 is occasional during normal operation (a charging point, an inspection
port). Zone 22 is fault-only and short-lived (a leaking lid, a duct joint). See
[ATEX zone classification](https://www.powderprocess.net/Safety/ATEX_Zones_Classification.html).

So: **inside the enclosure is Zone 20/21; just outside the seams is Zone 22.** Placing the monitor
at the boundary rather than in the middle isn't a compromise — it's the correct location both for
safety and for the measurement, since containment is a property of the boundary.

### The real-world data point

OSHA cited Powderpart Inc. (Woburn, MA) after a November 2013 titanium-powder explosion during
vacuuming that burned an employee over 65–70% of body surface — one willful and nine serious
violations, $64,400 proposed. The citation list includes, verbatim:

> *Equipment and conductors did not meet electrical standards* · *Equipment and wiring not
> intrinsically safe (Class II, Division 1 electrical panels, light switches, J-boxes, etc.. not
> present)* · *Electrical boxes not closed* · *Ignition sources present: (no ESD grounding straps
> & matts)*

(OSHA Citation #947859, reproduced in Sandia
[SAND2014-19158PE](https://www.osti.gov/servlets/purl/1242062).) This is a metal-AM operation being
cited for ordinary, unrated electrical equipment in a powder area — the exact question at hand.
A more recent case: a
[September 2023 dust explosion in Shanghai](https://www.sciencedirect.com/science/article/abs/pii/S0950423024001979)
during replacement of a 3D printer's dust-collector filter killed two and injured two.

### And the industry's own rule of thumb

The Aluminum Association's
[TR-2](https://www.aluminum.org/sites/default/files/2021-11/Safe_Storage.pdf) (*Recommendations for
Storage and Handling of Aluminum Powders and Paste*) puts it in one sentence:

> *"Keep as much electrical equipment as possible outside processing areas. Only lighting and
> control circuits should be in operating rooms. All electrical equipment must meet the National
> Electric Codes for hazardous installations. This includes flashlights, hazardous portable power
> tools and other devices."*

If a **flashlight** is called out by name, a Raspberry Pi is not a borderline case.

---

## 3. The numbers

| Property | Value | Source |
|---|---|---|
| MIE, pure Al (AM grade) | **4 mJ** | [Ignition and explosibility of Al alloys in ALM](https://www.sciencedirect.com/science/article/abs/pii/S0950423017303765) |
| MIE, AlSi10Mg | **11 mJ and 14 mJ** (two batches) | same |
| MIE, Al alloys generally | 13–23 mJ | same |
| MIE, high-purity Al powder | 40–45 mJ | [Micron-sized Al MIT/explosion characteristics](https://www.sciencedirect.com/science/article/abs/pii/S0950423019309386) |
| MIE, Al nanopowder (40 nm) | < 5 mJ | [IJAME 15(2)](https://ijame.umpsa.edu.my/images/Vol%2015%20Issue%202%20June%202018/10%200407.pdf) |
| MIT, dust cloud, micron Al | ~690 °C | [as above](https://www.sciencedirect.com/science/article/abs/pii/S0950423019309386) |
| Self-ignition, Al–Mg powder **layer** | 310–320 °C | [Moisture/accumulated-dust ignition study](https://www.sciencedirect.com/science/article/abs/pii/S0950423023002395) |
| MIE, Al at 40 µm (i.e. our coarse end) | 59.7 mJ; MEC 35 g/m³, K<sub>St</sub> 77 (St 1), P<sub>max</sub> 5.9 bar | Wu et al. 2010, via Edison |
| MIE, Al nanopowder 35–100 nm | **< 1 mJ**; K<sub>St</sub> 296–673, P<sub>max</sub> 7.3–12.5 bar | Wu et al. 2010 / Bouillard et al. 2010, via Edison |
| MIE, Al **flake** | as low as ~0.1 mJ in sensitive reports | Benson 2012 / Reding 2018, via Edison |
| MIT, dust cloud, 6 µm Al | **420 °C** — far below the 650–690 °C coarse value | Benson 2012, via Edison |
| LIT, Al flake **layer** | 320–326 °C | Cadwallader 2003 / Reding 2018, via Edison |
| K<sub>St</sub>, Al 5–15 µm fines | 220 (St 2), vs. 77 for the same material at 40 µm | Benson 2012, via Edison |
| MEC, aluminum | 0.040 oz/ft³ ≈ **40 g/m³** (USBM RI-6516); literature range 35–170 g/m³ | [Aluminum Association F-1](https://www.aluminum.org/sites/default/files/2021-11/Safe_Handling-Aluminum_Fine_Particles.pdf) |
| K<sub>St</sub> class, aluminum | **St 3 (strong)**, K<sub>St</sub> > 300 bar·m/s | [SAND2014-19158PE](https://www.osti.gov/servlets/purl/1242062) |
| P<sub>max</sub> / (dP/dt)<sub>max</sub>, Al | 7–8 bar / 1170 bar·s⁻¹ | [ALM alloys paper](https://www.sciencedirect.com/science/article/abs/pii/S0950423017303765) |
| P<sub>max</sub> / (dP/dt)<sub>max</sub>, Al alloys | 5–7 bar / 250–360 bar·s⁻¹ | same |

Against those, the candidate ignition sources:

| Source | Energy / temperature | Verdict |
|---|---|---|
| Human-body static discharge | 10–30 mJ (to ~90 mJ) | **Exceeds MIE.** The dominant risk. |
| Charged plastic surface, propagating brush discharge | Can ignite heavy dust clouds outright ([IEC 60079-32-1](https://cdn.standards.iteh.ai/samples/21691/2f3b16ec221b4b2e8d50a9503af65759/IEC-TS-60079-32-1-2013-AMD1-2017.pdf)) | **Exceeds MIE.** |
| Arc from conductive dust bridging a PCB / connector | Unbounded — it's mains- or supply-limited | **Exceeds MIE.** |
| Motor commutator, relay contact, switch | Spark-producing by design; TR-2 names commutators explicitly | **Exceeds MIE.** |
| Raspberry Pi SoC hot surface | 60–85 °C | Far below 310 °C. Not the issue. |
| PMS5003T laser diode | few mW, sealed chamber; IEC 60079-28 benign threshold 15 mW / Class 1 | Not the issue. |
| ESP32 / Pi Wi-Fi | ~0.1 W vs. IEC 60079-0 threshold 6 W | Not the issue. |

**A caveat on the AlSi10Mg row.** The 11–14 mJ figures come from one peer-reviewed study of ALM
aluminium alloys. An independent deep-literature search found *no reliably transferable published
MIE/MIT/MEC/K<sub>St</sub> dataset for AlSi10Mg* and recommended treating generic aluminium bounds
as the conservative stand-in until the actual lot is tested. Take 11–14 mJ as an order-of-magnitude
anchor, not a design value.

Note also how strongly the numbers track the **fines tail** rather than the nominal cut: the same
aluminium goes from K<sub>St</sub> 77 (St 1) at 40 µm to 220 (St 2) at 5–15 µm, and cloud MIT drops
from ~650 °C to 420 °C at 6 µm. Your 15–45 µm product is the benign part; the atomiser's condensate
and fines are the hazard, and they are also the fraction the AirGradient can actually see.

A caution that applies to every row above, from ASTM via Sandia: *"The values obtained are specific
to the sample tested, the method used and the test equipment used. The values are not to be
considered intrinsic material constants."* Published MIE for aluminum spans an order of magnitude
because it depends on particle size distribution, oxide state and moisture. **Your atomizer
produces a new powder every run.** Treat the literature as an order-of-magnitude guide and test
your own fines if this becomes load-bearing.

---

## 4. "Would a Raspberry Pi be recommended against? Or fine if it has a good case?"

Same answer as the AirGradient, more strongly — a Pi has more exposed conductors, more cable
entries, and (on a Pi 5) usually a fan.

A "good case" is a real risk reduction but it is not a compliance path, and it fails in specific,
checkable ways:

- **Vents and fans defeat dusttightness.** Any active-cooled case is out. Passive, fully sealed
  only — which for a Pi 5 means thermal throttling under load, so size the workload accordingly.
- **Cable entries are the leak path.** USB, Ethernet, HDMI and power need glands or bulkhead
  connectors, not slots.
- **Servicing breaks the seal**, in a room where dust has settled. Every microSD swap is an event.
- **A plastic case tribocharges.** IEC 60079-32-1 restricts insulating surface area precisely
  because charged non-conductive surfaces produce incendive discharges in dust atmospheres. A bare
  ABS/ASA/PC box in a flowing metal-dust stream is the failure mode, not the mitigation.
- **Conductive dust is a when, not an if.** Once Al dust is inside a non-sealed case, it doesn't
  need an ignition source to ruin your day — it shorts things, and *then* provides one.

Decision table:

| Situation | Is a Pi OK? | What "good" means |
|---|---|---|
| **Outside** the dust-bearing volume, in the room | Yes | An ordinary case. This is the answer ~95% of the time and costs nothing. |
| Inside the enclosure, and the DHA concludes the enclosure is **not** a classified location | Defensible with care | Fully sealed IP6X/NEMA 12+, **no fan, no vents**, glanded entries, conformal-coated board, surface temp ≪ 310 °C, exterior conductive or static-dissipative and **bonded to the enclosure ground**, on a GFCI/fused supply, inspected and cleaned on a schedule. This is risk reduction, not compliance. |
| Inside, and it **is** a classified Class II Div 1 / Zone 20–21 location | No — a case is not enough | Listed Class II Div 1 equipment, or IEC Ex tb IIIC (IEC 60079-31), or a purged/pressurized enclosure per NFPA 496 ([Type Z / Ex pzc reduces the interior to unclassified](https://www.pepperl-fuchs.com/en/products/hazardous-area-products-and-solutions/purge-and-pressurization-systems/ex-pzc-purge-and-pressurization-systems-gp32722)). Pressurization is the standard answer for computers too large for flameproof and too power-hungry for intrinsic safety. Expect 10–100× the cost of the Pi, plus a continuous clean-air or inert supply. |

**Costs, roughly.** A small NEMA 12 / IP66 enclosure suitable for an SBC is $100–500 bare, before
certified glands and breathers. An NFPA 496 purged/pressurised enclosure starts around $500–2000+
plus a continuous clean-gas supply and purge controller. Intrinsically safe barriers run $50–200
per channel. Against a $40 Pi, the arithmetic argues for itself.

**The one control that beats all of them: inert the volume.** If the enclosure atmosphere is held
below the limiting oxygen concentration (~5% O₂ is the figure usually quoted for aluminium, but
test yours), there is no deflagration to initiate, and the DHA may reach a different classification
altogether. The rePowder already works under argon. Extending that logic to the downstream powder
enclosure — with O₂ monitoring, alarms and interlocks, and the monitoring recorded, since an
unmonitored inerting system is exactly what OSHA cited Powderpart for — is a far better investment
than hardening a Pi. Caveats: inerting de-passivates powder, and magnesium burns in N₂ and CO₂, so
argon is the only safe choice across your element list.

**The design move that makes all of this go away:** split the volumes. Compute, power supplies,
drivers and radios live outside; only the minimum passive sensing element goes inside, on a glanded
cable. A stepper motor inside and its driver outside is a different risk profile from a Pi inside.
This is what LPBF OEMs and powder-handling vendors do — ATEX-rated vacuums and sieve stations,
gloveboxes, and the electronics kept out of the powder-wetted volume
([Russell AMPro](https://www.russellfinex.com/en/separation-equipment/screening-machines/am-powder-sieving/),
[Volkmann PowTReX](https://www.volkmannusa.com/powtrex/)).

**If you genuinely need in-enclosure particulate data**, the certified product category is
electrostatic-induction dust monitors rather than optical ones: the
[Sintrol DUMO EXG A](https://dustsafetyscience.com/continuous-dust-monitoring/) is UL/CSA certified
for **Class II Division 1, Groups E, F and G**, measures 0.01 mg/m³ to 6 g/m³, and outputs
4–20 mA / Modbus. The sensing element is a single solid metal probe with the electronics in an
Ex-rated housing — exactly the "minimum element inside" pattern. The alternative is extractive
sampling: probe inside, instrument outside, conductive grounded sample line (ordinary plastic
tubing here would be its own ignition source).

There is also a cheap third option specific to the PMS5003T: put it in the **exhaust stream
downstream of filtration**, where dust concentration is negligible by design. You lose the
in-enclosure number and gain a filter-breakthrough alarm, which is arguably the more actionable
signal anyway.

---

## 5. "Are there other things like this?"

Yes — and several are more dangerous than the monitor. Ranked roughly by how likely they are to
bite this project.

| Thing | Why it's a problem | What to do instead |
|---|---|---|
| **Extension cords, power strips, wall warts** | Not dusttight; unplugging arcs; internal contacts. Mundane and therefore invisible. Powderpart was cited for open electrical boxes. | Hardwired or dusttight fittings, or keep them outside the classified zone entirely. |
| **Ordinary shop vac / lab vacuum** | The single most-documented ignition source in metal AM. A dust cloud forms *inside* the vacuum, static builds from particle motion, and the filter is a fuel bed. This is what injured the Powderpart employee. | Immersion-separator wet vacuum or a vacuum certified for Group E dusts; conductive hose and tools; everything bonded and grounded; maintained and liquid-level-checked (Powderpart's *was* explosion-proof but poorly maintained). |
| **Compressed-air blow-down** | Turns a layer into a cloud. Prohibited by NFPA 484 practice. | Don't. Ever. |
| **Synthetic brushes, plastic scoops** | TR-2/F-1 are explicit: they *"accumulate strong static charges."* | Natural-fiber bristle brushes; conductive, non-sparking, grounded scoops. No plastic, no ferrous metal (impact sparks). |
| **Unbonded containers during transfer** | Pouring is a tribocharging operation. In a documented Italian incident, compressed air into an ungrounded transfer hose produced a ~150 mJ discharge that ignited aluminium dust with an MIE of ~50 mJ — a 3× margin over the ignition threshold from an operation that looks routine. | *"Both containers should be bonded together and provided with a grounding strap"* (TR-2). Applies to the atomizer's airlock containers too. |
| **Water, and sprinklers overhead** | Al + H₂O → H₂ + heat. A water stream also raises a dust cloud. Damp powder is *more* hazardous, not less. Powderpart was cited for failing to assess "water sprinklers & metal powders." | Class D agent or dry sand, applied gently, aimed *above* the fire so it settles by gravity. No water, no halon/halogenated agents, no CO₂. Confirm what suppression is over the bench with EHS. |
| **Reactive metal pairs / thermites** | Your element list is a thermite catalogue: Al+Ni, Al+Ti, Ti+B, Zr+B, Si–Zr, Ce–Si, Ni–Si, Mn–Si, Si–Ti are all named in the Sandia deck. These need **no oxygen** and generally react to completion. Li is an alkali metal — a separate regime again. | Segregate storage. Never co-mix or co-collect swarf/fines from different elements. Think hard before a mixed-powder doser. |
| **Atomizer fines and condensate** | The sub-10 µm fraction has the lowest MIE and is what escapes containment. Processing under inert gas can **de-passivate** powder, which can then auto-ignite on air exposure (Sandia). | Controlled passivation / slow air bleed before opening; treat the collector as the most hazardous vessel in the system. |
| **Dust collection** | Ordinary baghouses and especially electrostatic precipitators are ignition sources; F-1 says precipitators *"should not be used."* The Shanghai fatality happened during filter replacement. | Wet/immersion or explosion-vented collector, located outside the building, ≥4500 fpm transport velocity, grounded and interlocked, non-sparking fan with bearing temperature sensing (the Sandia TSRL design). |
| **The fume hood itself** | A hood is a ventilation control, not a dust-control enclosure: it draws the cloud *toward* a fan and a shared duct, and its sash is not a dust barrier. The interim arrangement in [#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195) is a shared facility. | Confirm with EHS and the Dillon lab before any powder work in it. Don't let "interim" become the permanent plan without a DHA. |
| **Housekeeping** | 1/32″ of accumulated dust over 5% of a room's surface area is the recognised hazard threshold. A primary explosion lofts settled dust and the secondary one is what kills. | Scheduled wet-wipe / certified-vacuum cleaning, logged. This is the highest-value, lowest-cost control on the list. |
| **Motors, fans, belts, bearings** | Commutators arc; stalled or failed bearings become hot surfaces; belts tribocharge. | Brushless, sealed, bonded; drivers outside; bearing temperature monitoring on anything in the dust stream. |
| **Cameras, LED ring lights, laptops, phones, flashlights** | Unrated electronics with batteries and switches. TR-2 names flashlights explicitly. | Camera outside a window looking in. Phones/laptops stay out of the powder area. |
| **Li-ion batteries and UPSes in the enclosure** | A stored-energy source with a plausible thermal event, inside the one volume you least want one. (This is a second reason to skip the battery-equipped AirGradient Open Air Max.) | Keep batteries out of the dust-bearing volume. |
| **Hybrid mixtures** | Metal dust plus organic dust or solvent vapour is more sensitive than either alone. | Don't run solvent work and powder work in the same enclosure or on the same exhaust. |
| **3D-printed fixtures and plastic tubing** | PLA/ABS/PETG parts and PTFE lines are insulators in a charging flow — the propagating-brush-discharge case in IEC 60079-32-1. Also: PTFE and aluminium powder will burn together (Sandia). | Conductive or static-dissipative materials, bonded; metal where practical. Relevant directly to the CubXL doser design. |

---

## 6. Recommendations for this project

1. **Keep the AirGradient placement as recommended** — enclosure exhaust, a seam/door gap, or the
   operator breathing zone just outside. Updated reasoning: it is Zone 22 rather than Zone 20/21,
   it's where containment is actually measured, and the monitor's own fan isn't stirring the
   dirty side.
2. **Split the CubXL/doser design into two volumes now, while it's cheap.** Powder-wetted volume
   inside; Pi, drivers, PSUs and radios outside; glanded cables between. Retrofitting this later
   costs far more than designing it in.
3. **Ground and bond everything**, including the atomizer's transfer containers, per NFPA 77.
   Add an ESD mat and wrist strap at the powder bench — Powderpart was cited for the absence of
   exactly this.
4. **Buy the housekeeping kit before the powder arrives**: a combustible-metal-rated vacuum,
   natural-fibre brush, conductive non-sparking scoops, Class D extinguisher and dry sand.
5. **Get a DHA started with EHS**, referencing NFPA 660 Ch. 22. Ask specifically about: the fume
   hood, overhead suppression, and whether the enclosure interior will be treated as a classified
   location. That answer determines whether anything electrical may go inside at all.
6. **Ask about inerting the powder enclosure, not just the atomiser.** Argon below the LOC, with
   O₂ monitoring, alarms and interlocks, plus a logged record that the monitoring works. This is
   the control with the best ratio of risk reduction to cost, and it is what every commercial LPBF
   OEM does. Argon specifically — Mg burns in N₂ and CO₂.
7. **Treat the fines and condensate as a separate, more hazardous material** from the screened
   15–45 µm product: passivate under inert gas before air exposure, store sealed, grounded and
   isolated, and test them separately.
8. **Consider testing your own powder.** ASTM E1226 (explosibility), E1515 (MEC), E2019 (MIE),
   E1491 (cloud MIT), E2021 (layer hot-surface ignition), E2931 (LOC). Since the atomizer is
   itself the variable under study, the fines fraction differs run to run, and a measured MIE for
   *your* powder converts most of the argument above from literature to fact. Test three things:
   virgin powder, reused powder, and the collected fines/condensate.
9. **If in-enclosure monitoring is genuinely required**, price a Sintrol DUMO EXG A, an extractive
   setup, or a post-filter position in the exhaust — rather than trying to harden a consumer device.
10. **Run the AirGradient for a week before any powder work** to establish the quiet baseline.

For scale: the CSB recorded 281 combustible-dust incidents in the US between 1980 and 2005 —
119 deaths, 718 injuries — with metal dust accounting for about 20%. The recurring causes are
inadequate housekeeping, uncontrolled ignition sources, improper grounding and non-rated equipment.
That is a short list, and every item on it is cheap to fix before the powder arrives.

---

## Sources

- [NFPA 484 / NFPA 660 TIA](https://docinfofiles.nfpa.org/files/AboutTheCodes/484/TIA_484_22_1.pdf) — electrical area classification for metal dusts, Group IIIC
- [Donaldson: NFPA 660 consolidation](https://www.donaldson.com/en/resources/technical-articles/nfpa-660/) and [EI Group: DHA requirements](https://ei1.com/understanding-dust-hazard-analysis-preparing-for-nfpa-660-compliance/)
- Sandia National Laboratories, A. Hall, *Powder Safety Awareness for Additive Manufacturing*, [SAND2014-19158PE](https://www.osti.gov/servlets/purl/1242062) — including the OSHA Powderpart citation #947859
- The Aluminum Association, [TR-2 *Storage and Handling of Aluminum Powders and Paste*](https://www.aluminum.org/sites/default/files/2021-11/Safe_Storage.pdf) and [F-1 *Handling Aluminum Fines*](https://www.aluminum.org/sites/default/files/2021-11/Safe_Handling-Aluminum_Fine_Particles.pdf)
- [*Ignition and explosibility of aluminium alloys used in Additive Layer Manufacturing*](https://www.sciencedirect.com/science/article/abs/pii/S0950423017303765), *J. Loss Prev. Process Ind.*
- [*Minimum ignition temperatures and explosion characteristics of micron-sized aluminium powder*](https://www.sciencedirect.com/science/article/abs/pii/S0950423019309386)
- [*Explosion characteristics and suppression analysis of AlSi12 powder used in additive manufacturing*](https://www.sciencedirect.com/science/article/abs/pii/S0950423024001979)
- [IEC TS 60079-32-1 (electrostatic hazards)](https://cdn.standards.iteh.ai/samples/21691/2f3b16ec221b4b2e8d50a9503af65759/IEC-TS-60079-32-1-2013-AMD1-2017.pdf) and [IEC 60079-0 (RF thresholds)](https://cdn.standards.iteh.ai/samples/22385/309820fd38c44d1ba9327256b5439cb5/IEC-60079-0-2017.pdf)
- [EC&M: NEC Article 502, Class II Hazardous Locations](https://www.ecmweb.com/national-electrical-code/article/20897735/nec-article-502-class-ii-hazardous-locations)
- [Stonehouse: are all electrostatic discharges hazardous?](https://stonehousesafety.com/static-electricity-and-combustible-dusts-are-all-electrostatic-discharges-hazardous/)
- [ATEX zone classification for dusts](https://www.powderprocess.net/Safety/ATEX_Zones_Classification.html)
- [Dust Safety Science: continuous dust monitoring / Sintrol DUMO EXG A](https://dustsafetyscience.com/continuous-dust-monitoring/)
- [Pepperl+Fuchs Ex pzc purge and pressurization](https://www.pepperl-fuchs.com/en/products/hazardous-area-products-and-solutions/purge-and-pressurization-systems/ex-pzc-purge-and-pressurization-systems-gp32722)
- [Metal AM: safety management in metal additive manufacturing](https://www.metal-am.com/articles/safety-management-in-metal-3d-printing/)
- ISO/ASTM 52931 (AM environmental/health/safety principles) and ISO/ASTM 52928 (powder life-cycle management)

An Edison Scientific deep-literature search (`LITERATURE_HIGH`, task `31a6b617-43eb-4af2-a605-9cc4a8ccea65`)
was run against the same questions; its full answer, reference list and artifacts are committed
under [`outputs/issue-219-ignition-sources/`](../outputs/issue-219-ignition-sources/). Where this
document cites "via Edison", the underlying primary references are listed in
[`edison_references.md`](../outputs/issue-219-ignition-sources/edison_references.md).

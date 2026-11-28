# Could the lab design and build its own vertical lift module?

Sterling, issue #53, 2026-10-27, never answered: "Wondering if we might be able to design and build our own, including making
sure it meets ASHRAE requirements, etc. Granted, that might be a huge undertaking with a lot of safety risks, too."

**Short answer: not the lift. Buy the lift (new, or used with a service check) and build everything on and around it:
the trays, the docks, the cameras, the robot interface.** The reasons, the standards, an estimate of the work, and the
numbers are below. Facts are cited; **estimates are the author's engineering judgement and are marked "(estimate)"**.
Checked 2026-11-07 UTC; the standards were identified by web search and by the notes, **not read in full**, so every
standard below needs a check of the current edition by BYU EHS or a compliance engineer before it is relied on.

## 1. What a VLM is, and why it is hard

Two columns of trays hang on chains inside a steel shaft, with an extractor that fetches a tray and pushes it to an
opening. For our lab the model has 2450 × 864 mm trays rated 500 kg, 15 trays in two units, a unit 3950 mm tall, a shutter
at the opening and, in the quotes, an operator or robot at the opening (`notes/kardex_opening.md`).

The hazards that make it a machine for specialists:
- **Suspended load.** About 7 tonnes of trays and instruments hang from chains above a person or a robot (15 trays × up to 500 kg).
  A chain or brake failure drops a tray down the shaft.
- **An extractor and a shutter** that move under power near an operator.
- **A pinch and crush zone** at the opening, and entry into the shaft for maintenance.
- **Instruments with heat, N2, water and powder** on the trays (the lab adds these hazards; a standard VLM carries goods).

## 2. The standards a VLM has to meet

| Area | Standard | What it asks | Who checks |
|---|---|---|---|
| Machine safety, VLM-specific, US | **ANSI MH24.2** (Material Handling Industry; "power-operated vertical carousels and vertical lift modules": hazards in installation, start-up, operation, maintenance, testing) | design, guarding, controls, training, maintenance of VLMs | the maker, OSHA inspectors rely on it as a consensus standard (search result, edition **[to confirm]**) |
| Machine safety, VLM-specific, EU | **EN 15095** "storage lifts" (the standard named in Kardex and Modula literature **[to confirm title and scope]**); EU Machinery Directive 2006/42/EC | CE marking: risk assessment, safety-related controls | notified body or the maker's declaration |
| Safety of control systems | **ISO 13849-1** (performance level), **ISO 13855** (safe distances), **ISO 12100** (risk assessment), **IEC 62061** | safety PLC, light curtains, interlocks, E-stop at a defined performance level (typically PL d) | the machine builder |
| Electrical, US | **NFPA 79** (electrical standard for industrial machinery), **NFPA 70 (NEC) Article 670** (industrial machinery), **UL 508A** (industrial control panels) | wiring, protection, disconnects, labelling, short-circuit rating | **an NRTL** (UL, Intertek, TUV) field evaluation or a listed panel; the AHJ |
| Worker protection | **OSHA 29 CFR 1910.212** (machine guarding), **1910.147** (lockout/tagout), **1910.303-399** (electrical), 1910.178 where it overlaps | guards, LOTO, electrical safety | OSHA, BYU EHS |
| Fire | **NFPA 13** (sprinklers; storage rules, and its parking-lift/shaft provisions as analogues), local fire code; **NFPA 484** for combustible metal powders (Al fines); **NFPA 855** for any lithium-ion UPS bank | sprinkler coverage inside an enclosed shaft; dust control | fire marshal, AHJ |
| Seismic, Utah | **IBC and ASCE 7** (nonstructural components and nonbuilding structures; Provo is typically seismic design category D, some Wasatch Front sites E, from a low-authority blog; **verify with the USGS tool and BYU Facilities**); **MH16.1** for racks | anchorage of a 3.95 m tall, 7 t machine; tray retention in an earthquake | a structural engineer, building official |
| Heat and ventilation | **ASHRAE 62.1** (ventilation), **ASHRAE 55** (comfort), **ASHRAE 90.1** (energy), **ASHRAE thermal guidelines for electronics** (for the equipment's temperature class), **ASHRAE 110** (hood containment) | the room and the enclosure must carry away the heat; hoods must contain | the mechanical engineer; ASHRAE standards are design criteria for the room and are not a certification of a VLM |
| Floor and building | the building code's floor-load and slab design | point loads under the unit's feet | structural engineer |

**ASHRAE, specifically.** No ASHRAE standard certifies a VLM. ASHRAE enters through the room: the model's enclosure is
2.83 × 3.12 × 3.95 m with 56 m² of walls and roof, and the instruments inside put up to about **7 kW** into it (`notes/services.md`).
A heat balance (air, 1.2 kg/m³, 1005 J/kg-K) gives the airflow for a temperature rise ΔT: 7,000 W at ΔT = 5 K needs about
**4,200 m³/h**; at ΔT = 30 K about **700 m³/h**, the model's range. Whoever supplies the machine must also give an **operating
temperature limit** for the chains, drives and trays; that figure is exactly what the Kardex and Modula questions in
`infrastructure.md` ask.

## 3. What building one would take (estimates)

| Work package | What it is | Effort (estimate) |
|---|---|---|
| Concept and risk assessment | ISO 12100 hazard analysis; define trays, shaft, extractor, shutter, safety functions | 2-3 months, one engineer, plus a safety consultant |
| Structure | 3.95 m frame, tray guides, seismic anchors, structural calculations stamped by a PE | 3-4 months, a structural engineer |
| Drives | chain or belt hoists with a brake and a **safety gear or chain-break detection**, an extractor with a tray-pull mechanism, positioning to about 1 mm | 4-6 months, two engineers, test stand |
| Controls | safety PLC, light curtains, E-stop, shutter interlock, fieldbus to our scheduler | 3-4 months |
| Electrical | UL 508A panel, NFPA 79 wiring | 1-2 months, plus an NRTL field evaluation |
| Validation | overload and drop tests at 125-150 percent of rated load, cycle life, seismic review | 2-3 months |
| Documentation | manuals, LOTO procedures, training, a technical file | 1-2 months |
| Total | | **about 2-3 engineer-years elapsed 12-18 months (estimate)** and a **lab-owned liability** for a machine that holds 7 t above people |

Cost (estimate): parts for a unit of this size about **$40-80k** (steel, chains, motors, safety components, trays); engineering time
that a university lab pays for in student and staff effort; **NRTL field evaluation $10-30k**; a **third-party risk assessment** and a
structural PE review **$10-30k**; insurance and BYU Risk Management sign-off are **[to confirm]**. The buyer of a commercial unit gets
those certifications bundled.

What a builder does **not** get: a CE or NRTL mark that the maker already holds, a service network in Utah, a software stack, spare parts, or a
manufacturer's liability. If a student is hurt, the university, not a vendor, is the manufacturer.

## 4. Build versus new versus used

| | Build | New (Kardex, Modula) | Used (Europe) | Used (US) |
|---|---|---|---|---|
| Price found | parts $40-80k plus certification $20-60k plus staff time (estimates) | **Kardex $97k and Modula $118k**, April 2026 quotes for the lab's specification (issue #53 comment 4179678435; the quotes themselves are private; Modula's is priced with Bay S) | **EUR 14,500-26,950** asking for a Shuttle XP 500, **plus** dismantling, freight, rigging, reassembly (Europe) | **$110,000-120,000** for two large units from Outsource Equipment (#53 comment 4165070381), "far too large" |
| Conformity | the lab carries it | CE/UL by the maker; ANSI MH24.2 | CE (400 V); US needs an NRTL **field evaluation** and a 208 V conversion (estimate $10-30k) | as sold |
| Service | none | maker's service in the US | none unless Kardex US agrees to cover it | dealer |
| Warranty | none | yes | none | limited |
| Fits our 996 mm opening and 856 mm products | by design | **open question** (Kardex, Modula Bay M/XL) | one listing shows a 996 mm opening (used XP 500) | no |
| Lead time | 12-18 months (estimate) | Kardex QuickShip 4-6 weeks for standard sizes (a search result), custom longer | weeks, plus shipping | now |
| Delivered to Provo (estimate) | $100-150k plus staff time | the quote plus freight and installation, **[to confirm]** | EUR 20-35k unit + $30-60k freight, rigging, conversion and service (estimate) | the quote |

## 5. What is worth building ourselves

Everything on the tray side of the lift is ours already, and none of it is a suspended-load hazard:
- the **trays' content**: instruments, racks, posts, the camera units, the glovebox shell;
- the **docks and plates** (a CombiTac assembly with our valves, section 7 of `infrastructure.md`);
- the **tray UPS and cabling**, the **robot interface** and the **scheduler**;
- the **riser and manifold** for air, N2 and water, the dock windows (with the maker's approval).

A middle path: **a static shelving or rack cell** served by the MiR and UR (no hung loads, no extractor), which gives up the
footprint advantage of a VLM (the model's 15 trays of 2450 × 864 mm in about 9 m² of floor) but needs only the robots' own
safety cases. It is not costed here.

## 6. Recommendation

1. **Do not build the lift.** The standards are not the obstacle; the liability and the elapsed time are. A tray fall, a chain failure or a shaft
   entry accident carries a university-level risk, and the schedule (12-18 months, estimate) is longer than waiting for a new unit.
2. **Buy new** if the budget stands ($97k Kardex or $118k Modula in April 2026, per #53, before the extras we need), **or buy a used European XP 500
   only with** (a) a Kardex US service engineer's written agreement to commission and service it, (b) an NRTL field evaluation priced in,
   (c) a 996 mm opening if possible. The asking prices look cheap and are not once freight, conversion and certification are added.
3. **Ask each maker for the missing numbers first**: product height through the opening, full extraction, point loads, temperature limit,
   a robot interface, and a docking tray. These are the questions in sections 1-2 of `infrastructure.md`. Their answers decide whether an
   off-the-shelf VLM can host the lab at all.
4. **Put what we can build on the tray side** and keep the lift stock, so its safety certification stays the maker's.
5. **Involve BYU EHS, the fire marshal and a structural engineer now**: sprinklers in the shaft, the seismic anchorage and the floor load do not
   depend on who built the machine.

## Sources (2026-11-07 UTC; web search results, not read in full unless noted)
- ANSI MH24.2 listing: [ANSI webstore, MHI](https://webstore.ansi.org/sdo/mhi) (search result).
- NFPA 13 and parking-lift sprinkler guidance as an analogue: [LA Dept of Building and Safety NFPA 13 2022 mechanical parking lifts](https://dbs.lacity.gov/sites/default/files/efs/forms/pc17/NFPA-13-2022--Mechanical-Parking-Lifts.pdf), [Portland Fire](https://www.portland.gov/fire/permits-inspections/documents/design-guidelines-sprinkler-coverage-car-stacking-lift-systems/download).
- Utah seismic: [Provo design criteria](https://www.provo.gov/800/Design-Criteria), a [2026 summary blog](https://www.meltplan.com/blogs/structural-design-in-utah-seismic-snow-load-and-foundation-code-requirements) (low authority).
- Prices: issue #53 comments [4179678435](https://github.com/vertical-cloud-lab/byu-vcl/issues/53#issuecomment-4179678435) and [4165070381](https://github.com/vertical-cloud-lab/byu-vcl/issues/53#issuecomment-4165070381); used listings in `infrastructure.md` section 3; Kardex QuickShip from [Kardex's info page](https://info.kardex.com/us-en/ppc/general/shuttle/kr/noam-01) (search result).
- The model's numbers: `vertical-lab/notes/services.md`, `notes/kardex_opening.md`.

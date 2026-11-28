# Facility locations: what the repos already say

Gathered on 2026-11-12 from `vertical-cloud-lab/byu-vcl` and `vertical-cloud-lab/digital-alloy-lab` (DAL), as a
starting point for a byu-vcl PR on where a facility like the vertical cloud lab could be built. It goes with
`transcript.md`, the facility part of Sterling and Gage's conversation that day. Links into PR branches are pinned to
the commit current on 2026-11-12.

## What the conversation asked for

- **The task:** a byu-vcl issue that lists the warehouses and other locations where a facility could go, framed as
  "if we were to build a facility like this", pointing to the `vertical-lab/` visualizations
  ([#303](https://github.com/vertical-cloud-lab/byu-vcl/issues/303),
  [PR #318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318)).
- **Height:** about 50 ft, as in the 50 ft array below.
- **Floor area:** 20,000 ft² is a number that has come up. For comparison, Radical AI (New York) was said to have just
  moved into about 40,000 ft², and may have a California site too. Both figures need checking.
- **Where:** Lehi, Utah came up as probably a good area.
- **What kind of site:** places that already handle gas lines and hazardous materials. Bringing in utilities is easier
  there, and the site shows a precedent, legally too, for this kind of use. Sterling expects the facility to be the
  toughest part.
- **Renovate or build:** short term, a warehouse with the utilities put in, which is much cheaper. Later, perhaps a
  building made exactly how we want it.

## The facility the visualizations describe

| What | Figures | Where |
|---|---|---|
| The VLM | Kardex Shuttle XP 500. 2450 × 864 mm trays and a 2780 × 3074 mm module footprint. 3950 mm tall in the lab version (under 13 ft). 208 V three-phase. Trays are powered in their slot and at the opening, not while moving. Quotes for one unit are in #53 | [#53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53), [`vlm.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/9ca1a9c/vertical-lab/vlm.py) |
| The 50 ft array | Kardex builds the Shuttle up to 30 m tall, in 100 mm steps. The animation uses 15.15 m, just under 50 ft. It has eight units in two rows of four across an 1100 mm aisle, with one UR10e on a floor rail: 352 powered trays and 1056 instruments. The array alone covers about 12 × 7.5 m (under 1,000 ft²), so it asks for clear height far more than floor area | [`scale.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/03801d8/vertical-lab/scale.py), [still](https://github.com/vertical-cloud-lab/byu-vcl/blob/03801d8/vertical-lab/out/vlm_scale_still.png), [GIF](https://github.com/vertical-cloud-lab/byu-vcl/blob/03801d8/vertical-lab/out/vlm_scale.gif), [video](https://www.youtube.com/watch?v=9A9XuBT0BYk) |
| The lab floor | Two Shuttles, with the large machines on the floor beside them: the atomizer, LPBF (Aconity MIDI), wire EDM, tensile frames, furnace, glovebox and fume hood. MiR250 + UR10e mobile manipulators serve them | [PR #318 README](https://github.com/vertical-cloud-lab/byu-vcl/blob/9ca1a9c/vertical-lab/README.md), [`out/tray_plan_floor.png`](https://github.com/vertical-cloud-lab/byu-vcl/blob/9ca1a9c/vertical-lab/out/tray_plan_floor.png) |
| The warehouse version | The VLM and floor machines on an open warehouse floor, served by mobile manipulators instead of a rail | [`warehouse.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/9ca1a9c/vertical-lab/warehouse.py), [video](https://www.youtube.com/watch?v=3IrSB9-meN8) |
| Throughput, which sets how many floor machines there are | About one fully tested alloy a day as modeled. Ten a day needs 3 rePowders, 4 Aconity MIDIs and crucible cover round the clock, among other things | [PR #332 `notes/bottleneck.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/notes/bottleneck.md) |
| Services and heat | Docking couplings carry mains, Ethernet, air, N₂ and chilled water to each tray. With everything on, about 7 kW goes into one VLM, which needs forced ventilation. The wire EDM is the largest single electrical load, and the line needs its own three-phase panel | [`notes/services.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/9ca1a9c/vertical-lab/notes/services.md) |

## Site and utility requirements already written down

- [PR #331](https://github.com/vertical-cloud-lab/byu-vcl/pull/331)'s
  [`lab_answers.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/685216e/vertical-lab/procurement/lab_answers.md#site-and-utilities)
  has a "Site and utilities" table. The site must provide:
  - **Building:** at least 4.0 m ceiling for one 3.95 m Shuttle. A concrete slab, with the load rating still to
    confirm (a loaded Shuttle and the wire EDM are the heaviest items). Delivery access: dock, doors, freight
    elevator. Wasatch Front seismic.
  - **Power and gases:** 120 V and 208 V three-phase (the atomizer's 400 V needs a transformer), house air, an N₂
    generator, argon (cylinders or bulk) and chilled water.
  - **Exhaust and ventilation:** ducted exhaust, plus about 700-4,200 m³/h of ventilation per VLM.
  - **Network and safety:** wired network, and an EHS (environmental health and safety) review.
  - **Hazards on site:** reactive aluminium fines, argon, IPA and fine metal powders.

  Most rows are still marked **[to confirm]**, because they depend on the room.
- [`build_our_own_vlm.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/685216e/vertical-lab/procurement/build_our_own_vlm.md)
  lists the standards a VLM installation answers to: ANSI MH24.2, EN 15095, ISO 13849, NFPA 79 / UL 508A, NFPA 13 and
  484, IBC / ASCE 7 seismic and ASHRAE for the room. NFPA 484 (combustible metals) and the fire code's hazardous
  occupancy rules will matter as much as square footage when screening a building.
- [`infrastructure.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/685216e/vertical-lab/procurement/infrastructure.md)
  has vendors and specs for the VLMs (Kardex, Modula, used dealers), the N₂ generator, chiller, gas supply, UPSs and
  fume hoods.

## What fitting out the current lab (CB 154) took

These are the line items a new site would need again, at a larger scale.

- [byu-vcl#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31) Lab layout planning.
  - Floor plans: [`cb154.pdf`](https://github.com/vertical-cloud-lab/byu-vcl/blob/226ccc6/cb154.pdf) and
    [`cb154-annotated.pdf`](https://github.com/vertical-cloud-lab/byu-vcl/blob/226ccc6/cb154-annotated.pdf). The room
    is about 700 ft².
  - Gage's outlet map and equipment sizes. The VLM was planned at about 10 × 10 ft, with its own direct exhaust.
  - The 24 April facilities meeting's work order:
    - a counter with sink and eye rinse;
    - a 14 × 10 × 9 ft hard-wall clean room;
    - the atomizer's exhaust, argon, chilled water, compressed air and power;
    - power and argon for a glovebox, and power for a Mastrex MX 120;
    - Ethernet, an O₂ detector, a dehumidifier and HEPA air.
- [byu-vcl#7](https://github.com/vertical-cloud-lab/byu-vcl/issues/7): CB 154 is the old projects lab. The adjoining
  carpeted room is another group's, and has asbestos tiles under the carpet.
- [byu-vcl#29](https://github.com/vertical-cloud-lab/byu-vcl/issues/29) Fume hood. On campus, exhaust is the
  bottleneck: one building had run out of chemical exhaust.
- [byu-vcl#18](https://github.com/vertical-cloud-lab/byu-vcl/issues/18) drench hose,
  [byu-vcl#41](https://github.com/vertical-cloud-lab/byu-vcl/issues/41) N₂ and argon supply,
  [byu-vcl#305](https://github.com/vertical-cloud-lab/byu-vcl/issues/305) particle concentration alert.
- DAL: [#142](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/142) atomizer installation and lab
  renovations, [#126](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/126) Class D fire extinguisher,
  [#127](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/127) HEPA filtration,
  [#131](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/131) dehumidifiers,
  [#130](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/130) gloveboxes,
  [#251](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/251) atomizer SOP.

## Leads already in the repos

- **Lehi:** Texas Instruments' LFAB is there, with 620,000+ ft² of clean room and 15 miles of automated wafer track
  ([byu-vcl#319](https://github.com/vertical-cloud-lab/byu-vcl/issues/319)). Gage has asked BYU's recruiting office to
  set up a tour. That would also be a look at a site that already runs gas lines and hazardous materials.
- **Warehouses that already run VLMs:** in [byu-vcl#53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53), a
  dealer mentioned a contract the Church has used for VLMs in its distribution warehouses. Sterling asked for a
  contact there. The VLM dealers in #53 (Kardex through Hoj Engineering, Modula through Outsource Equipment) can also
  say what clear height and floor loading a tall Shuttle needs.

## Open questions for the PR

1. What clear height, floor loading and fire-code occupancy does a 15 m Shuttle array need? A 50 ft clear height is
   rare in ordinary warehouses. Is there a pit, a high-bay or a shorter-unit fallback?
2. What sites exist within commuting distance of BYU, starting with Lehi and Utah County? For each: clear height,
   area, power, gas and exhaust, zoning, lease or sale status, and a public contact.
3. Which local sites already handle gases and hazardous materials (fabs, labs, battery, chemical or pharma
   buildings) and are vacant or for lease?
4. Renovate or build: costs per ft² and lead times for a leased warehouse fitted with utilities, against a
   purpose-built building.
5. What do comparable self-driving-lab facilities occupy? Radical AI's reported ~40,000 ft² is one, to be checked.

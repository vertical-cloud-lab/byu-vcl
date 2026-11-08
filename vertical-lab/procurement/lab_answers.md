# The lab's answers to the questions every vendor asks

Every sales team asks the same questions before it will give a budgetary quote: who is buying, where it goes, what
it has to do, how many and how fast, what utilities are there, when and how it will be bought, and who services it.
This page answers them once for the whole vertical cloud lab, so each vendor file (`infrastructure.md`,
`characterization.md`, `production.md`) only has to answer what is specific to that product.

Facts come from the model on PR #318 (`vertical-lab/README.md`, `notes/`). **[to confirm]** marks anything only the lab can
answer (a room, a date, a budget, an account). Those need filling in before an email goes out. Nothing here is a
commitment to buy.

## Who

| Question | Answer |
|---|---|
| Organisation | Brigham Young University (BYU), Provo, Utah, USA: Department of Mechanical Engineering |
| Group | BYU Vertical Cloud Lab ([github.com/vertical-cloud-lab](https://github.com/vertical-cloud-lab)) |
| Principal investigator | Sterling G. Baird, BYU Mechanical Engineering (also Acceleration Consortium, University of Toronto) |
| Contact for the quote | **[to confirm: name, email, phone]** |
| End users | Graduate and undergraduate researchers. The robots load most instruments; people load the atomizer's crucible and do the maintenance |
| Purchasing | BYU Purchasing, by purchase order **[to confirm: buyer, quote address, W-9 / tax-exemption certificate on request]** |

## What it is for

A self-driving laboratory for metal alloy development: the "digital alloy lab". New compositions are melted and
atomized into powder, sieved, printed by laser powder bed fusion, cut, heat treated, tensile tested, sectioned,
mounted and polished, then characterized. The loop runs largely unattended.

- **Instruments sit on the trays of two vertical lift modules** (Kardex Shuttle XP 500, 2450 × 864 mm trays), 15
  trays in all.
- **The VLM brings a tray to its opening.** A mobile manipulator (a UR10e on a MiR250, with a Robotiq 2F-85 gripper
  and a RealSense D405 wrist camera) then loads or unloads the instrument on it.
- **Large machines stand on the floor:** the atomizer, LPBF printer, wire EDM, tensile frame, depowdering, sieving
  cell and fume hood.
- **Materials:** Al alloys (Al-Si, AlSi10Mg, Al 4047, Al 6063), Cu alloys (Cu-Ni) and nickel-aluminium bronze.
  - **Powders:** atomized in the lab, 20-63 µm for LPBF and 45-105 µm for DED. Al fines are treated as combustible
    metal dust (NFPA 484).
  - **Solids:** printed coupons, E8 subsize and miniature tensile bars, 1.5 in metallographic mounts.
- **No HF anywhere** in the workflow. ICP-MS goes to the BYU Spectroscopic Facility.

## How many and how fast

The year-1 figures come from the lab's own schedule model (`out/timelapse_model.json`, round 8). They are planning
numbers, not commitments; the round-10 maintenance model (`out/upkeep_model.json`) revises them.

| Per year (model) | |
|---|---|
| Atomizer runs | about 700 (three a weekday, staffed) |
| Alloys atomized / printed and fully tested | about 378 / 324 |
| Tensile tests | about 1,420 (room temperature and up to 200 °C) |
| SEM images | about 7,000 |
| XRD, XRF and laser-diffraction measurements | about 380 each |
| Powder made | about 170 kg |

Most instruments are wanted as **one unit**. The VLMs, mobile manipulators and grippers are wanted as **two**. The
UPSs and tray couplings are wanted as **15**, one per tray. Quantities are in each vendor's section.

## Automation: what we need from an instrument

Ranked from must to nice. Each vendor section asks which apply.

1. **Remote start and stop, and a status read-back,** over Ethernet or RS-232 (an API, SDK, OPC UA, Modbus or a
   documented command set), or at least digital I/O. A workflow scheduler drives everything.
2. **A sample position a robot can reach:** from the front or top, with a gripper 85 mm wide and fingers
   127-138 mm across the knuckles.
3. **Doors and lids that open on command,** or that a robot can open. Otherwise we add our own actuators, and we need
   to know whether that voids the warranty.
4. **Data export** in an open format, with timestamps.
5. **Unattended operation:** interlocks that fail safe, error states the software can read, and no pop-up dialogs
   needing a click.

## Site and utilities

| Question | Answer |
|---|---|
| Building, room, floor | **[to confirm]**, BYU campus, Provo, UT 84602 |
| Ceiling height | At least 4.0 m needed. The VLM is planned at 3950 mm, under the 13 ft (3962 mm) in issue #53 **[to confirm the room]** |
| Floor | Concrete slab **[to confirm load rating; a loaded Shuttle XP 500 and a wire EDM are the heaviest items]** |
| Access for delivery | **[to confirm door widths, loading dock, freight elevator]** |
| Seismic | Utah, Wasatch Front **[to confirm the seismic design category with BYU Facilities]** |
| Electrical | 120 V single-phase and 208 V three-phase. The VLM, wire EDM and atomizer need three-phase; the atomizer's 400 V needs a transformer (`notes/services.md`) **[to confirm panel capacity]** |
| Compressed air | House air **[to confirm pressure and dew point]** |
| Nitrogen | An N₂ generator beside the VLM, piped to each tray's coupling |
| Argon | Cylinders or a bulk supply for the atomizer and LPBF printer **[to confirm]** |
| Chilled water | A recirculating chiller beside the VLM (Thermo ThermoFlex 900 class) |
| Exhaust | A ducted fume hood and a downdraft enclosure for sieving **[to confirm duct routing and capacity]** |
| Heat | About 7 kW into the VLM with everything on, so it needs forced ventilation of roughly 700-4,200 m³/h (`notes/services.md`) |
| Network | Wired Ethernet to every tray through its coupling; the BYU network **[to confirm VLAN and remote-access policy]** |
| Safety review | BYU Engineering's lab safety plan and EHS sign-off before install |

## Money, timing, buying

| Question | Answer |
|---|---|
| Budgetary or firm? | **Budgetary**, for planning and proposals. List price and academic price, please, valid at least 90 days |
| Budget | **[to confirm]** |
| When | **[to confirm]**. Purchase depends on funding; the lab is planning now |
| Funding | Research proposals in preparation **[to confirm which to name]** |
| Academic or education pricing | Yes, please quote it |
| Shipping | Delivered to Provo, UT 84602. Rigging and installation itemised **[to confirm the receiving address]** |
| Trade-ins or used units | Welcome for VLMs and large machines |
| Tax-exempt status | BYU is a private university; sales-tax exemption and the exemption certificate to give a vendor **[to confirm with BYU Purchasing]**. Do not assume Utah's exemption applies |
| Who places the order | A BYU purchase order through BYU Purchasing; vendors invoice BYU, not a person **[to confirm with BYU Purchasing]** |
| W-9, vendor registration, payment terms | BYU Purchasing's vendor-setup forms and payment terms **[to confirm with BYU Purchasing]**. Ask the vendor for its W-9 and remit-to details |
| Incoterms and imports | For EU and Asian makers, ask for a delivered-duty-paid price to Provo, UT; customs broker and import duty on the vendor **[to confirm with BYU Purchasing]** |
| Export and end-use | Academic research use only, no re-export, no military end use. EU powder and laser equipment may ask for an end-user statement, which BYU's export-control office would sign **[to confirm]** |
| Dock, lift gate, crane | Whether the receiving dock takes a truck with a lift gate, pallet jack and forklift access, and the route to the lab room **[to confirm with BYU facilities]** |
| Hazardous materials | Reactive aluminium fines (NFPA 484-type), argon, IPA and fine metal powders are on site; vendor service staff get an EHS briefing first **[to confirm]** |
| Insurance, references | A certificate of insurance for installers and two university references per large item are welcome |

## Service, training, upkeep

The lab is planning the instruments' upkeep over years (`notes/upkeep.md`), so every quote should include:

- **Warranty:** length and what it covers.
- **Installation and training:** on site or remote, and how many people.
- **Preventive maintenance:** the schedule, the tasks we can do ourselves, those that need a service engineer, and
  downtime per visit.
- **Consumables and wear parts:** a list with prices and expected life.
- **Calibration and verification:** intervals and standards, e.g. ASTM E4 or ISO 7500-1 for load frames.
- **Service contract:** the price per year, and response times in Utah.
- **Remote diagnostics:** if offered, and what network access they need.
- **The nearest service engineer.**

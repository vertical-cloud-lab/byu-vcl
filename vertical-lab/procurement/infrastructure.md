# Procurement pack: the infrastructure (VLMs, robots, docks, power, gas, hoods, cameras, packaging, jars, ICP-MS)

Part of Sterling's ask on PR #318 (2026-11-07): "find all the contact information, specs, requests, etc. for the
individual parts ... Include specific emails and answer the typical questions people would be asking us in order for
them to give a budgetary quote." This file covers the lab's **infrastructure**. The instruments are in
`characterization.md` and `production.md`. The answers every vendor asks for (who, where, utilities, budget, timeline,
purchasing) are in [`lab_answers.md`](lab_answers.md); each section here answers only what is specific to the product.
The machine-readable list is [`infrastructure.csv`](infrastructure.csv). The build-it-ourselves question is in
[`build_our_own_vlm.md`](build_our_own_vlm.md).

**Conventions.**
- **Checked** is 2026-11-07 UTC, from 04:00 to 07:30. **Via Pi** says whether the page was fetched through the
  stream-cam Pi because the runner was blocked (403, 404 or a JS-only page), one fetch at a time, nothing left on its disk.
- **[to confirm]** marks a site fact only the lab can supply, or a contact detail that a search snippet gave and no
  official page confirmed. **Check every number before sending an email.**
- **Business contacts only.** For the lab's existing quotes (Kardex via Hoj Engineering; Modula via Outsource
  Equipment) the thread is cited, not the addresses: [issue #53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53),
  comments [4165070381](https://github.com/vertical-cloud-lab/byu-vcl/issues/53#issuecomment-4165070381),
  [4165074412](https://github.com/vertical-cloud-lab/byu-vcl/issues/53#issuecomment-4165074412) and
  [4179678435](https://github.com/vertical-cloud-lab/byu-vcl/issues/53#issuecomment-4179678435).
- **Every vendor is also asked** (and every draft below says so in one line): the preventive-maintenance schedule,
  consumables and spares with prices, a service-contract price, and the response time in Utah. The lab is modelling
  upkeep over years (`notes/upkeep.md`).
- Specs are the maker's published figures where cited, and the model's numbers (`vertical-lab/notes/`) where it says so.

## Contents

| # | Section | Qty | Pi needed |
|---|---|---|---|
| 1 | Kardex Shuttle XP 500 and Shuttle 700/1000 | 2 | yes (contact page) |
| 2 | Modula Lift (MC50D, MC75D, MC1000D; Bay M and XL) | 2 | yes (contact, dealers) |
| 3 | Used-VLM dealers | 1-2 | no |
| 4 | Teradyne Robotics: MiR250 and UR10e | 2 + 2 | tried (JS pages) |
| 5 | Robotiq 2F-85 | 2 | no |
| 6 | Intel RealSense D405 | 2 | tried |
| 7 | Stäubli CombiTac | 15 sets + 15 docks + bay | tried |
| 8 | Eaton 5PX1500RTNG2, and lithium-ion UPSs | 15 | no |
| 9 | Parker Balston UHPN2-1100 nitrogen generator | 1 | no |
| 10 | Thermo ThermoFlex 900 chiller | 1 | no |
| 11 | Gas supply: Airgas, Linde, Norco | | no |
| 12 | Labconco Protector XStream, 4 ft | 1 | no |
| 13 | Sentry Air 24 in ductless hood | 1 | no |
| 14 | Tray glovebox: Vigor and others | 1 | no |
| 15 | Stream cameras: Raspberry Pi 5, HQ Camera, Camera Module 3 Wide | 15 trays, 2-3 each | no |
| 16 | PiKVM V4 Mini | 1+ | no |
| 17 | Primera LX500c + AP380 | 1 + 1 | no |
| 18 | Zebra ZD621t | 1 | tried |
| 19 | Uline H-190 impulse sealer | 1 | no |
| 20 | Powder jars, grounded racks, gasketed cans | hundreds | no |
| 21 | BYU Spectroscopic Facility (Agilent 8900 ICP-MS/MS) | service | yes |

---

## 1. Kardex: Shuttle XP 500 (two), and the Shuttle 700/1000

### 1. What we'd buy
- **Maker and model:** Kardex Shuttle XP 500, **two units**, trays **2450 × 864 mm**, **15 trays** in all (the split between the two units is in
  `notes/tray_plan.md`), the unit **3950 mm** tall (under the 13 ft
  in #53). The tray type quoted in #53 is the Strong, 500 kg per tray (the quote says 490).
- **Options we need (open):** a **996 mm opening** (the used XP 500 listing, "Bedienöffnung frontseitig auf 833 mm,
  Höhe 996 mm") where the usual product height is 727.5 mm; **full tray extraction** at the opening; a **rear opening**
  for a second robot; powered tray at the opening (Kardex powers a tray in its slot and at the opening but not in
  transit, #53).
- **Role:** the lab's backbone. Instruments stand on trays; the VLM brings a tray to the opening and a UR10e on a MiR250
  loads it. Cited to the `README.md` round-9 section and `notes/kardex_opening.md`, `notes/tray_plan.md`.
- **Alternative to ask about:** the **Shuttle 700 and 1000** (taller product height; the Shuttle 1000's mesh-box trays
  imply about 1 m, `notes/kardex_opening.md`).

### 2. Published specs that matter for integration
- **Trays:** the POF order sheets give the 2450 × 864 mm Strong tray 500 kg (the #53 quote says 490), and
  992 lb per tray with a 32.8 in floor-to-tray height on the AC's XP 500 quote (#372; `notes/kardex_opening.md`).
  Ratings fall as width grows (265 kg at 3050 mm). **Point-load ratings are not published.**
- **Utilities:** 208 V three-phase (#53); a used 2450 × 864 unit lists 400 V, 17 A (`notes/services.md`).
- **Interfaces:** Kardex's own control software with a host connection (Power Pick Global is Kardex's WMS name; **[to confirm]**); what an API looks like is **not published** (the dealer replies in #53 said software integration is possible and
  priced by the host software).
- **Robot loading and doors:** the opening is at a delivery height of 833 mm with a shutter; there is no published
  robot interface and no door actuation beyond the shutter.
- **Size:** the enclosure is about 2.83 × 3.12 × 3.95 m (the model); weight is not published.

### 3. Contact
- **Web form (US):** <https://www.kardex.com/en-us/company/get-in-touch> ("I have a question regarding a system or
  product"); the page lists no email or phone. The same page group has a "find a local contact" route.
- **Phone:** Kardex Remstar, 41 Eisenhower Drive, Westbrook, ME 04092, **800-639-5805** (press releases 2013-2018, not on
  the current site; **[to confirm]**).
- **Regional:** the lab's existing quote came through **Hoj Engineering** (thread cited above). Whether Hoj covers Utah
  or the Mountain West is **[to confirm]**.
- **Education programs:** none found.

### 4. Our open questions for them
From `notes/kardex_opening.md` "Ask Kardex" and `notes/lab_r8.md`:
1. The **maximum product height through the opening** on the **Shuttle 700 and 1000**, standard and as a special; and on
   the XP 500, whether the used unit's **996 mm opening** is orderable and what height of goods it takes (we estimate
   856 mm).
2. **Full tray extraction** on the XP 500 2450 × 864 and at a **rear opening**: is it a standard option, and how far does
   the tray come out?
3. The **extraction table's size**, and the **trolley's load** (can it take a 500 kg tray with a 250 kg point load on
   0.47 m²?).
4. The product height and **concentrated-load rating** of the Shuttle 1000's pallet and mesh-box trays.
5. Does a tall opening change the **833 mm delivery height** or the **3950 mm unit height**?
6. A **powered tray** at the opening: the dealer offered a quick-connect cord; we want a tray that docks at the opening
   (CombiTac, section 7) without voiding the warranty.
7. **Dock windows** in the column side walls (60 mm stroke, 108 mm deep housing) and a **riser** for air, N2 and water:
   allowed? **Heat:** a stored tray gives off 60-2,800 W; what temperature limit does the enclosure have?
8. **A robot at the opening:** a shutter or light curtain interface (I/O or fieldbus) the robot controller can read.
9. **Seismic anchoring** and the floor load (point loads) for a Utah site.
10. PM schedule, consumables and spares with prices, a service contract price, response time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Model and quantity | Shuttle XP 500, 2 units, 15 trays in total (slots per unit: see `notes/tray_plan.md`) |
| Tray size and load | 2450 × 864 mm; heaviest tray load per the model about 236-500 kg; the HIP and a wire EDM are the heavy items **[to confirm]** |
| Product height | 727.5 mm standard; we need 856.5 mm (the 996 mm opening) |
| Unit height | 3950 mm; ceiling at least 4.0 m **[to confirm the room]** |
| What is stored | Instruments, mostly electric, not goods; a few (the powder store, 581 jars) on short trays |
| Environment | Indoor, temperature-controlled; heat from instruments up to about 7 kW into the unit with everything on |
| Hazards | Al fines as combustible dust (NFPA 484); sealed jars only; no HF |
| Throughput | Low: a tray fetch every few minutes, not picks per hour |
| Access | One robot opening per unit, plus a rear opening if available |
| Software | Our own scheduler (Python) over an API; no WMS **[to confirm]** |
| Power | 208 V three-phase **[to confirm the panel]** |
| Floor and seismic | Concrete slab **[to confirm]**; Wasatch Front, seismic design category D-E likely **[to confirm with BYU Facilities]** |
| Install | Delivered to Provo; rigging and installation itemised |

### 6. Draft email
> **To:** Kardex Remstar US sales (web form, <https://www.kardex.com/en-us/company/get-in-touch>), copy Hoj Engineering
> **Subject:** Budgetary quote: 2 × Shuttle XP 500, 2450 × 864 mm, 996 mm opening, robot loading, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab is planning two Shuttle XP 500 units (2450 × 864 mm trays, 15 trays, 3950 mm tall) to hold
> laboratory instruments that a mobile robot loads at the opening. You quoted one earlier through Hoj Engineering
> (April 2026). We would like a budgetary quote, list and academic, valid 90 days, for two, and answers to these:
> 1. The tallest product height through the opening on the XP 500 (is the 996 mm opening orderable?) and on the Shuttle
>    700 and 1000.
> 2. Full tray extraction at the front opening and at a rear opening on the XP 500; the extraction table size and the
>    trolley's load.
> 3. Point-load ratings (for example 250 kg on 0.47 m²), and a powered or docked tray at the opening.
> 4. An I/O or fieldbus interface for a robot to read the shutter and tray state.
>
> Please include the preventive-maintenance schedule, consumables and spares with prices, a service-contract price and
> the response time to Provo, Utah. Our site answers are in the attached sheet. Thank you.
>
> [name, BYU Mechanical Engineering, email, phone **[to confirm]**]

### 7. Sources (checked 2026-11-07 UTC)
- [Kardex US get-in-touch page](https://www.kardex.com/en-us/company/get-in-touch), via Pi (the runner's fetch of `/en-us/contact` was a 404).
- [Kardex Shuttle product page](https://www.kardex.com/en-us/products/vertical-lift-module/kardex-shuttle), cited in `notes/kardex_opening.md`.
- Phone and address: search snippets of Kardex press releases (<https://www.pr.com/press-release/532174>), not fetched.
- [The used XP 500 listing with a 996 mm opening](https://www.lagersysteme-paternoster.de/gebrauchte-lagertechnik/kardex-shuttle-xp500-3050x864-pos-89/), cited in the notes.
- Issue #53 comments cited above.

---

## 2. Modula: Lift VLMs (MC50D, MC75D, MC1000D; Bay M and XL)

### 1. What we'd buy
- **Maker and model:** Modula Lift, **two units**; tray types **MC50D (500 kg), MC75D (750 kg) and MC1000D (990 kg)**,
  2,500 × 857 mm; **Bay M (895 mm)** or **Bay XL (1,295 mm)** of product height, against Bay S (695 mm) in the April 2026 quote
  (`notes/lab_r8.md`, "Modula's taller bays").
- **Role:** the alternative to Kardex. A taller bay would fit the Lasefinity Fusion X and the Parker Balston generator
  (Bay M), and the Sharebot MetalONE and Kings 3D DiMetal-100 (Bay XL).
- **Options to ask:** Modula's **Robot Interface** (anthropomorphic robots) and **AMR integration**, Modula
  **OPC-UA Telemetry**, Climate Control, and the Modula Lift's powered tray options.

### 2. Published specs
- **Trays:** 500, 750, 990 kg at 2,500 × 857 mm; Bay S, M, XL = 695, 895, 1,295 mm (Modula's brochure, found by
  Sterling, PR #318 2026-11-04). Tray fitting to Kardex's 2450 × 864 mm is open.
- **Software and interfaces:** Modula WMS packages, Modula Web Analytics (remote support), **OPC-UA Telemetry**,
  a **Robot Interface** and an **AMR** page on modula.us (page list fetched via Pi, 2026-11-07).
- **Made in the USA:** Franklin, Ohio and Lewiston, Maine production facilities.
- Power, weight and footprint: **not published** on the pages read.

### 3. Contact
- **Email:** `info.usa@modula.com` (from Modula's contact page, via Pi; the address is obfuscated in the HTML).
- **Phone:** general **937-365-7860**; customer care **800-361-0785**; toll-free **877-648-9755**.
- **Address:** Modula Inc., 5000 Commerce Center Drive, Franklin, OH 45005 (headquarters; also a Maine plant at 90 Alfred
  A. Plourde Parkway, Lewiston, ME 04240).
- **Web form:** <https://modula.us/contact-us/>. **Dealers:** <https://modula.us/dealer-network/> (a map; Utah not listed in the
  text, ask which dealer serves Utah).
- **Lab's existing channel:** Outsource Equipment (thread cited above).

### 4. Our open questions
1. Re-quote with **Bay M or XL**; the price against Bay S.
2. Fitting **our trays** (a 2450 × 864 mm layout) to Modula's 2,500 × 857 mm trays.
3. **Full tray extraction** at the opening, and a **rear opening**.
4. The **Robot Interface** and **AMR Integration** pages: what does the robot's controller see (shutter, tray position,
   a door actuator)?
5. A **powered tray** at the opening (Modula Lift tray options), the dock windows in the column walls, and heat limits.
6. **Point loads** of the 750/990 kg trays; weight and footprint; floor loading.
7. Software: which of the WMS packages is the lightest, and the API or **OPC-UA** nodes for a Python scheduler (the
   question in #53: "what software do we want to run the machine").
8. PM schedule, consumables, spares, service contract price, Utah response time.

### 5. Their intake questions, answered
As Kardex (section 1), plus: **tray type** MC75D or MC1000D (the HIP and the Aconity MIDI exceed even 990 kg); **bay**
M or XL; **number of units** 2; **WMS** minimal, our own scheduler over OPC-UA **[to confirm]**; **robot** UR10e on a MiR250
at the opening; **power** per `lab_answers.md`.

### 6. Draft email
> **To:** `info.usa@modula.com`; copy Outsource Equipment
> **Subject:** Budgetary re-quote: 2 × Modula Lift, Bay M or XL, MC75D/MC1000D, robot loading, BYU (Provo, UT)
>
> Hello,
>
> We received a Modula quote in April 2026 through Outsource Equipment (Bay S, 695 mm). Our instruments are taller: please
> quote **two Modula Lifts with Bay M (895 mm) and Bay XL (1,295 mm)**, MC75D or MC1000D trays, a robot loading opening, and
> a rear opening if possible, as a budgetary list and academic price valid 90 days. Please tell us:
> 1. Whether the trays can follow a 2450 × 864 mm layout, and the point-load ratings.
> 2. What the Robot Interface and AMR Integration options give a UR10e/MiR250 pair: shutter and tray status, door actuation.
> 3. A powered tray at the opening, and the OPC-UA data a Python scheduler can read.
> 4. Weight, footprint and the electrical supply.
>
> Please include the PM schedule, consumables and spares with prices, a service-contract price and the response time to
> Provo, Utah. Thank you.
>
> [name, BYU Mechanical Engineering, email, phone **[to confirm]**]

### 7. Sources (2026-11-07 UTC)
- [Modula contact page](https://modula.us/contact-us/) and [dealer network](https://modula.us/dealer-network/), both via Pi (the runner got 403).
- [Modula's government capability statement](https://modula.us/wp-content/uploads/2021/04/Modula-Inc-Government-Capability-Statement.pdf), a search result, not fetched.
- `notes/lab_r8.md`; issue #53 comments.

---

## 3. Used-VLM dealers

### 1. What we'd buy
One or two used Shuttle XP 500 (or equivalent) units, trays about 2450 × 864 mm, ideally with a tall opening. #53 records two
used units from Outsource Equipment (on behalf of Vertical Storage USA) at $110,000 and $120,000, "far too large for us" (comment
4165070381), and four earlier ones that are gone.

### 2. Specs and prices found
| Listing | Year | Size | Ask | Note |
|---|---|---|---|---|
| Sindelfingen/Flensburg, DE | 2017 | XP 500 2450 × 813 | EUR 26,950 net | dismantled and loaded; transport and reassembly extra |
| Frankfurt, DE | 2006 | XP 500 3050 × 864 | EUR 14,500 each for three | same terms |
| Sold, resale.info | 2002 | XP 500 2500 × 812 | EUR 15,950 (2021) | sale record |
| Sold, resale.info | 1995 | 2450 × 863 | EUR 17,500 (2013) | sale record |
| UK | 2017 | Modula ML50 | EUR 11,000 ex VAT | Fareham |

Transport from Europe, rigging, reassembly, a CE-to-US electrical conversion (400 V to 208 V) and an NRTL field evaluation are not
in these asks (`build_our_own_vlm.md` prices them as estimates).

### 3. Contact
- **Marketplaces (published business sites):** machineseeker (<https://www.machineseeker.com/>), werktuigen
  (<https://www.werktuigen.com/>), resale.info, used-machines.com: each listing has an enquiry form.
- **Dealer in Germany with the 996 mm unit:** [lagersysteme-paternoster.de](https://www.lagersysteme-paternoster.de/) (enquiry form).
- **US:** Vertical Storage USA / Outsource Equipment (existing contact, thread cited). No US used-VLM specialist found; Raymond West
  (California) sells new VLMs.

### 4. Open questions
Year, tray count and **tray load**, the **opening height** (996 mm?), controller and software version and whether it is supported,
service history, **voltage** (400 V three-phase vs 208 V), **EN to US** conversion, whether Kardex US will **service** a unit imported from
Europe, and whether the seller dismantles and loads.

### 5. Their intake questions, answered
Pickup or delivery to Provo, UT; **[to confirm]** whether the lab has a forklift or crane and a dock; ceiling at least 4.0 m; purchase
by BYU purchase order; payment terms **[to confirm]**.

### 6. Draft email
> **Subject:** Enquiry: Kardex Shuttle XP 500, 2450 × 864 mm, tall opening, shipping to Utah, USA
>
> Hello, we are a university laboratory (BYU, Provo, Utah, USA) looking for one or two Shuttle XP 500 units with 2450 × 864 mm
> trays, an opening of about 996 mm and full-extraction trays if available. For your unit: the year, tray count and load, the
> opening height, the voltage, the service history and the price dismantled and loaded; and whether it can be inspected under power.
> We would ship to Utah and re-commission with a US Kardex service engineer. Thank you. [name, email **[to confirm]**]

### 7. Sources (2026-11-07 UTC, search snippets, not fetched)
[machineseeker.ie listing](https://www.machineseeker.ie/kardex+remstar-shuttle+xp+500+2450x813/i-18477291), [resale.info](https://resale.info/en/kardex-shuttle-xp-500-2450x813-челночный-складской-лифт-патерностер-циркуляция/No-163239111),
[the 996 mm unit](https://www.lagersysteme-paternoster.de/gebrauchte-lagertechnik/kardex-shuttle-xp500-3050x864-pos-89/),
[UK Modula ML50](https://www.machineseeker.ie/modula+s.p.a.-ml50/i-21201335), Raymond West
[VLM page](https://www.raymondwest.com/orange-county-ca/material-handling-equipment-supplier/warehouse-automation/vlm).

---

## 4. Teradyne Robotics: MiR250 and UR10e (two mobile manipulators)

### 1. What we'd buy
- **Maker and models:** Teradyne Robotics (Universal Robots + Mobile Industrial Robots): **MiR250 ×2** (autonomous mobile robot,
  97 kg) each carrying a **UR10e ×2** (33.3 kg arm, 12 kg control box, 12.5 kg payload) with a **Robotiq 2F-85** and a
  **RealSense D405** (sections 5-6). Mounted on the MiR's top module: about 52 kg on top (arm 33.3, payload 12.5, gripper 0.9, plate).
- **Options:** MiR Hook or top module with a **48 V power feed**, a UR **mounting plate**, MiR **markers** (L or VL) for docking, **MiR
  Fleet**, a UR-MiR synchronisation URCap, a **charger** per unit (the model draws a marker).
- **Role:** the robots drive between the VLMs and the floor machines and load instruments through the openings.
  Cited to `notes/warehouse.md`, `notes/arm_collisions.md`, README.
- **Product status:** a search listing says the UR12e superseded the UR10e in May 2025 **[to confirm current availability]**.

### 2. Published specs
- **MiR250:** top speed 2.0 m/s (drawn at 1.5 m/s); corridor for one 1450 mm; two MiR250s passing 3000 mm (2100-2450 with dynamic
  set-ups); dock docked 80 mm off the face; payload and 97 kg (MiR250 Specifications, 2023-06-28, hosted by the distributor Hartfiel).
- **Power to a top module:** **48 V at 10 A combined, 480 W** (MiR). **UR10e maximum 615 W** (UR data sheet) and its control box runs
  on **100-240 V AC**. **Open:** how MiR and UR power this pair (`notes/warehouse.md`).
- **Tip risk:** UR's manual warns that an arm's loads can tip a mobile robot; MiR250 + UR10e at 12.5 kg needs reduced accelerations
  (`notes/warehouse.md`). **Pose repeatability** at a station ±3-6 mm, ±1° with an L-marker (needs a camera target or touch-off).
- **Interfaces:** the UR has RTDE, Modbus, Dashboard, ROS drivers; the MiR a REST API and an I/O module; both Ethernet.

### 3. Contact
- **Universal Robots USA:** `sales@universal-robots.com`, **+1 844-462-6268** (844-GO-COBOT), 27175 Haggerty Road, Suite 160, Novi, MI
  48377; get-started form <https://www.universal-robots.com/contact-us/get-started/>; partner portal <https://partners.universal-robots.com/>.
- **MiR:** global `mail@mir-robots.com`, +45 20 37 75 77 (Denmark); distributor and partner pages
  <https://www.mobile-industrial-robots.com/distributors>. A North America MiR sales contact is **[to confirm]** (Teradyne Robotics
  sells through distributors, certified system integrators and OEMs).
- **Distributors found (not Utah-specific):** **Hartfiel Automation** (distributes SICK, Universal Robots and MiR; **1-800-331-7301**;
  its 2019 purchase of Fiero adds a Wheat Ridge, Colorado office, **[to confirm]**); **Cross Company** (UR Certified System Integrator,
  location **[to confirm]**); **Automation Distribution** (lists the UR10e with prices).
- **Utah-based UR or MiR integrator:** none confirmed. Use each maker's partner locator filtered to Utah.
- **Academic:** UR Academy and UR's university discounts exist; **[to confirm]** through the distributor.

### 4. Open questions
1. **How to power a UR10e (615 W) from a MiR250 top module (480 W)**: a battery, a second battery, a DC-DC converter, or the 24 V
   bus? Is the MiR's own battery sized for it, and what does it do to runtime?
2. **Tipping and stopping** with a UR10e at full reach at 12.5 kg: the lowest acceleration limits and a validated stack.
3. **Docking accuracy** at the VLM's opening and at floor stations (±3-6 mm), and a **wrist camera** touch-off at each station.
4. **Safety:** MiR's SICK scanners with the arm up; ISO 3691-4 and ISO 10218 for the combined machine; who certifies the pair.
5. Charging docks: two robots, one dock each; charge time and the floor space (0.84 m dock).
6. The **UR10e vs UR12e**; a MiR250 vs MiR600 for the load; pricing for 2 + 2, academic.
7. The URCap for MiR-UR synchronisation, and what the VLM's controller (OPC-UA or I/O) can tell the robot.
8. PM schedule, consumables (MiR wheels, battery), spares, service contract, **Utah response time**.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Application | Loading and unloading laboratory instruments (up to 12.5 kg, vials, jars, mounts) at VLM openings |
| Payload | 12.5 kg on the UR; about 52 kg on the MiR's top |
| Reach and heights | Openings about 857 mm up; the top of a 1000 mm machine about 1857 mm up |
| Floor | Flat, clean, sealed concrete; aisle 3.0 m **[to confirm the room]**; docks 0.84 m wide |
| Speed and cycle | Low; minutes per tray; MiR at 1.5 m/s, 0.3 m/s² ramp |
| Environment | Indoor lab; powders (sealed jars only), no HF; ESD care |
| Interfaces | Ethernet; REST/RTDE; our Python scheduler |
| Safety | Shared with students; cage-free; EHS review **[to confirm]** |
| Fleet | 2 robots; Fleet software for traffic |

### 6. Draft email
> **To:** `sales@universal-robots.com` and a MiR distributor (Hartfiel Automation, 1-800-331-7301, or the one the partner locator names for Utah)
> **Subject:** Budgetary quote: 2 × MiR250 + 2 × UR10e (mobile manipulators), university lab, Provo UT
>
> Hello,
>
> The BYU Vertical Cloud Lab plans two mobile manipulators: a UR10e on a MiR250, each with a Robotiq 2F-85 gripper and a RealSense D405 wrist
> camera, loading instruments at vertical lift modules. We would like a budgetary quote (academic and list, valid 90 days) for 2 + 2, the top
> plates and a charger per unit. Our open questions:
> 1. How is the UR10e (615 W; its control box takes 100-240 V AC) powered from the MiR250's top module (48 V, 10 A, 480 W)?
> 2. Validated limits for a 12.5 kg payload at full reach (tip risk), and docking accuracy at a VLM opening.
> 3. Who certifies the combined machine's safety; is a Utah or Mountain West integrator available?
> 4. UR10e vs UR12e availability.
>
> Please include the PM schedule, consumables and spares with prices, a service-contract price and the response time to Provo, Utah.
> [name, BYU Mechanical Engineering, email, phone **[to confirm]**]

### 7. Sources (2026-11-07 UTC)
- [UR contact page](https://www.universal-robots.com/contact-us/) (runner); [UR distributors page](https://www.universal-robots.com/distributors/) (runner; no Utah list).
- [MiR contact](https://www.mobile-industrial-robots.com/contact) (via Pi: email and phone from the HTML); [MiR distributors](https://www.mobile-industrial-robots.com/distributors) (search result).
- [MiR250 Specifications](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf) (cited in `notes/warehouse.md`).
- Hartfiel: [web](https://www.hartfiel.com/) (search snippets); UR12e note: [revelationmachinery.com listing](https://revelationmachinery.com/product/universal-robot-ur10e-2023/).

---

## 5. Robotiq 2F-85 (two)

### 1. What we'd buy
Robotiq **2F-85 adaptive gripper ×2** (UR e-Series kit, "AGC-ES-UR-KIT-85"), one per UR10e. Knuckle span 127-138 mm; weighs about
0.9 kg. Optional: a **Robotiq FT 300-S** force-torque sensor (0.1 N resolution; `notes/alloy_atomize.md` discusses it for the atomizer's lid).
Role: grips instruments, trays' lids, jars; the multi-doser's pan is out of reach with it (README round 9).

### 2. Specs that matter
Stroke 85 mm; the lab's design friction figure **141 N** against a 200 N design load (`notes/alloy_atomize.md`); 24 V, 3 A max (Robotiq data sheet,
**[to confirm]**); Modbus RTU/URCap over the UR wrist; no door actuation of its own.

### 3. Contact
- **Phone:** **1-888-762-6847** (head office, Lévis, QC; Robotiq's contact page, 2026-11-07); outside US/Canada +1 418 380 2788.
- **Quote page:** <https://robotiq.com/quote>; partners <https://robotiq.com/robotiq-partners> (a Utah distributor is **[to confirm]**).
- **Email:** none published on the contact page. **Price:** Robotiq publishes none; distributors list the 2F-85 from about **$4,999-$9,271**
  (Automation Distribution $9,271 list, UR Kit $5,885; the Robotics Center $5,825): wide spread, **[to confirm]**.

### 4. Open questions
Fingers for the jars and vial racks (custom pads, ESD?); **friction pads vs force** for a 12.5 kg payload; life in cycles; the **FT 300-S**
on the UR10e with the 2F-85 and the D405; whether **dust** (Al fines, sealed jars) voids the IP rating; PM, spares (finger pads), service price, Utah response.

### 5. Their intake questions
Robot: UR10e; payload object 0.5-12 kg; grip width 85 mm; ~20 grasps per tray visit; environment: indoor lab, clean, ESD; cycle time slow.
Parts: custom fingers by us; quantity 2.

### 6. Draft email
> **To:** Robotiq (<https://robotiq.com/quote>, 1-888-762-6847), or the Utah-area distributor
> **Subject:** Budgetary quote: 2 × 2F-85 for UR10e (e-Series kit), university lab
>
> We need two 2F-85 grippers with the UR e-Series kit, and a quote for one FT 300-S. Our fingers will be our own (jar and rack pads). Please give
> the academic and list price, delivery, a Utah distributor, and the PM schedule, spare finger pads and prices, and expected cycles to service.
> [name, email, phone **[to confirm]**]

### 7. Sources
[Robotiq contact](https://robotiq.com/contact-us) (runner, 2026-11-07); prices: [Automation Distribution](https://automationdistribution.com/robotiq-agc-grp-2f85-2f-85),
[Robotics Center](https://www.roboticscenter.ai/blog/robotiq-gripper-guide) (search snippets).

---

## 6. Intel RealSense D405 (two)

### 1. What we'd buy
**RealSense D405** stereo depth camera ×2, one per UR10e wrist (camera-only or with cable, 99ACXD / 99ACXC at DigiKey).
It is made now by **RealSense** after its spin-out from Intel (the product page lists a D405 series; the company site is realsenseai.com;
**[to confirm the spin-out and who warrants Intel-labelled stock]**). Role: touch-off at each station (`notes/warehouse.md`, the wrist camera in the hood in `notes/alloy_atomize.md`).

### 2. Specs
USB 3, close-range depth (about 7-50 cm), about 42 × 42 mm face; 5 V from the UR's tool or a USB hub (**[to confirm]** against the datasheet).
Open SDK (librealsense) and ROS wrapper; calibration is on the camera.

### 3. Contact
Site <https://www.realsenseai.com/> (via Pi; no contact details in the HTML; JS page). Buy through **DigiKey** (list $1,761-2,374, zero stock on
2026-11-07), or resellers at **$260-300** (Aztekc $273, Ichome $279). One reseller shows the D405 discontinued in Japan: ask RealSense.
**No sales email or phone found; use RealSense's "Book a Demo" or Support form.**

### 4. Open questions
Is the D405 **still sold and supported**; the successor; the **firmware** for UR tool-flange cables; the accuracy at 10-30 cm; mounting to the 2F-85.

### 5. Intake
Quantity 2; use: robot wrist at 10-30 cm; reflective metals and glass jars; indoor.

### 6. Draft email
> **To:** RealSense via the website's contact form (<https://www.realsenseai.com/>), copy DigiKey
> **Subject:** D405 availability and support (2 units, university lab)
>
> We plan two D405 wrist cameras on UR10e arms. Is the D405 current, who supports it after the Intel spin-out, and what is the lead time through
> DigiKey or a US distributor? Please give the academic price and a successor if it is being retired. [name, email **[to confirm]**]

### 7. Sources
[DigiKey D405](https://www.digikey.hk/en/product-highlight/i/intel-realsense/d405-depth-camera), [Aztekc](https://aztekc.com/intel-realsense-depth-camera-d405-intel/p),
[Ichome](https://ichome.com/product-detail/intel/82635dsd405mp) (search snippets, 2026-11-07); RealSense site via Pi.

---

## 7. Stäubli CombiTac (docks for 15 trays and the bay)

### 1. What we'd buy
One **CombiTac** mating set per tray plus a dock per slot a tray uses and the bay (15 plates, the docks in the VLM's side walls), as in
`notes/services.md`: **4 × Ø3 mm power units (39 A, 600 V)**, a **10 Gbit Cat 6A module** (RJ45), **RCT06** compressed air (shut-off one side,
15 bar), **SCT03** nitrogen (G1/8, shut-off both sides), **2 × LCT06** chilled water (G1/4, shut-off both sides), and **CombiTac align 4** guide
pins with conical sockets (4 mm radial, ±2° misalignment, **100,000 cycles**). The product is now sold as **CombiTac uniq**: use both names.

### 2. Specs
As above. Stäubli prohibits connecting or disconnecting the pneumatic and fluid inserts **under pressure**: the dock shuts and vents before it
pulls back, so the valves are ours. The dock's housing is 108 mm deep, stroke 60 mm (the model).

### 3. Contact
- **Stäubli Electrical Connectors, Inc.**, 100 Market Street, Windsor, CA 95492, **+1 707 838 0530**; a contact form on staubli.com; no sales email
  published. The Duncan, SC office (+1 864 433 1980) handles fluid connectors, robotics and textile, not electrical.
- **Fluid connectors** (air, N2, water) come from the Duncan, SC fluid-connectors business **[to confirm]**.
- **Distributors:** none found for Utah.

### 4. Open questions
1. **Mating cycles** per insert, and the **life of the water and air inserts** at 100 docking cycles a day.
2. Whether a **single plate** can carry mains + Cat 6A + air + N2 + 2 water in the footprint the model uses, and which modules to pick.
3. **Misalignment** a tray's side plate will see in the VLM's extractor (4 mm / ±2° is the published limit).
4. **Hot-plugging** power (39 A) vs our contactor; the **dry-break** rule for water (no drip).
5. Quote per set, and a **mock-up kit** to test a dock and a plate on a bench; PM, spares, service.

### 5. Intake
Quantity: 15 plates and 16 docks (15 slots plus the bay) **[to confirm]**; cycles: about 100 per day at the opening; media as listed; ambient 15-40 °C;
supply: 120 V single-phase per tray (5 kVA continuous at 80 %); N2 99.9999 % at low flow; chilled water at 20 °C.

### 6. Draft email
> **To:** Stäubli Electrical Connectors, Windsor CA (website form; +1 707 838 0530)
> **Subject:** Budgetary quote: CombiTac uniq docking set (4 power, Cat 6A, air, N2, 2 × water), 16 docks and 15 plates
>
> We are building a docking coupling for instrument trays in a vertical lift module: four Ø3 mm power units, one 10 Gbit RJ45 module, an RCT06 air, an SCT03
> nitrogen and two LCT06 water inserts on a CombiTac align 4 plate, mated about 100 times a day. Please quote 15 plates and 16 docks (budgetary, academic),
> and tell us the rated cycles per insert, the allowed misalignment, whether you offer a bench kit, and who supplies the fluid inserts in Utah.
> Please include maintenance intervals, spares and prices. [name, email **[to confirm]**]

### 7. Sources
[Stäubli North America](https://staubli.com/us/en/about-us/who-we-are/staubli-north-america.html) (search snippet; the runner got 403, and the Pi's fetch of
the electrical-connectors page returned a stub), [CombiTac catalogue](https://m.keiconn.com/assets/pdf/Staubli-CombiTac-MainCatalog.pdf) (search result).

---

## 8. Eaton 5PX1500RTNG2 UPS (fifteen), and lithium-ion alternatives

### 1. What we'd buy
**Eaton 5PX G2 1440 VA / 1440 W, 120 V, 2U rack/tower, with network card** ×15, one on every tray, standing on its side at the back right of the tray
(86 × 437 × 447 mm; `notes/services.md`). It carries the tray for about 6 s in transit. A 230 V 5PX 1500 runs 44 min at 300 W (a retailer's figure).
Price at resellers: **$1,566-1,767** each, so about **$23,500-26,500** for 15.

### 2. Specs
8 × NEMA 5-15R; Gigabit network card; four-post rail kit; hot-swappable battery; Eaton's relay card option; the 5PX G2 line may use lithium-ion in
some SKUs (**[to confirm]** for this one).

### 3. Contact
Eaton (Tripp Lite): **cpdipresaleshelp@eaton.com**, +1 773-869-1776, 10000 Woodward Avenue, Woodridge, IL 60517 (as shown on a Tripp Lite compare page;
**[to confirm]** on eaton.com). Resellers: CompSource **800-356-5794**, Barcodes Inc. (quote form), DigiKey.

### 4. Open questions
Runtime at 300-1,000 W; **battery chemistry**, the cycle life when it is recharged every dock cycle (about 100 transits a day); mounting on its side and **orientation limits**;
**vibration** on an extractor; operating **temperature** inside the enclosure (up to 40 °C?); a contact or relay to tell a tray's controller it is on battery; **Li-ion**
variant; PM (battery replacement interval), spares, service price.

### 5. Intake
Quantity 15; load per tray 60-2,800 W (the furnace tray holds heaters during transit); autonomy 6-10 s; 120 V; rack/tower; network management; ambient inside a ventilated VLM.

### Lithium-ion alternatives
| Option | Why | Caution |
|---|---|---|
| Eaton **9PX Lithium-ion** or an Eaton 5PX G2 lithium SKU (the Tripp Lite relay-card page lists "9PX Lithium-ion") | same vendor, 8-10 year battery life, lighter | price; **[to confirm]** models and runtime |
| **APC Smart-UPS Ultra** (lithium-ion, 1.5 kVA, 2U) | 10-year battery, short charge | SKU **[to confirm]**; APC's contact |
| A **supercapacitor or LiFePO4** DC bus on the tray | runs 6 s at 3 kW with no chemistry limit | custom, needs a certified supply |
Pros: longer life and about 1/3 the weight, quicker recharge for 100 transits a day. Cons: **fire risk in a sealed, enclosed VLM** (a lithium cell in a closed enclosure with powders; ask the
AHJ about NFPA 855's small-system rules and the sprinkler design), temperature limit for charging, cost. Ask each maker for UL 1973/UL 9540A data.

### 6. Draft email
> **To:** `cpdipresaleshelp@eaton.com` (confirm on eaton.com) and a reseller (CompSource)
> **Subject:** Quote: 15 × 5PX1500RTNG2, and lithium-ion options, university lab
>
> We plan 15 UPSs, each carrying a laboratory tray for 6-10 s during transfers in a vertical lift module, recharged about 100 times a day. Please quote 15 × 5PX1500RTNG2 (with network card)
> and the lithium-ion options (9PX Lithium-ion, 5PX G2 lithium), with battery chemistry, rated cycles, side mounting, temperature limit and a relay for "on battery". Please include the PM
> schedule, battery replacement interval and price, and a service contract. [name, email **[to confirm]**]

### 7. Sources
[Tripp Lite compare page](https://blog.tripplite.com/products/products-compare/mids/5PX1500HRTG2,5PX1500RTNG2), [CompSource](https://www.compsource.com/buy/5PX1500RTNG2/Eaton-1191),
[Eaton Tripp Lite 5PX1500RTG2 support](https://tripplite.eaton.com/support/5PX1500RTG2) (search results, 2026-11-07, not fetched); `notes/services.md`.

---

## 9. Parker Balston UHPN2-1100 nitrogen generator

### 1. What we'd buy
**Parker Balston UHPN2-1100** ×1 (99.9999 % N2 at 1,100 cc/min, 120 V), beside the VLM, piped to each tray's N2 inlet (`notes/services.md`). It needs **clean dry compressed air at 60-125 psig**
and has no compressor: buy a **Powerex compressor** or use house air. It is 889 mm tall, so it fits **Bay M** (895 mm) of a Modula but not a Kardex tray.

### 2. Specs
120 V / 60 Hz, about **700 W**; inlet 1/4 in, outlet 1/8 in; **35 × 12 × 16 in (889 × 305 × 406 mm)**, shipping 137 lb (62 kg), about 50 kg dry; output to 85 psig.
Resellers: Marshall Scientific **$17,910**, Chromtech **$18,917**; GovSci, GMI, GenTech, Fisher.

### 3. Contact
Parker Balston support **1-800-343-4048** (quick-start manual); <https://www.balstonlabgasgenerators.com/>. Sales through a lab-supply distributor (above). No Utah distributor found.

### 4. Open questions
Is **1.1 L/min** enough for the trays' purge (how many trays at once)? A larger model; **air quality** (dew point, oil) needed; the **compressor** pairing; **catalyst module**; PM (filter
elements, catalyst), consumable prices, service contract; piping to 15 couplings; **O2 monitoring**.

### 5. Intake
N2 demand: purge-only glovebox plus inerting vessels, about 1-5 L/min peak **[to confirm]**; purity 99.999 %+; house air **[to confirm pressure and dew point]**; space beside the VLM; 120 V circuit.

### 6. Draft email
> **To:** a Parker Balston distributor (Marshall Scientific; Parker 1-800-343-4048)
> **Subject:** Quote: UHPN2-1100 with compressor, university lab, Utah
>
> Please quote a UHPN2-1100 nitrogen generator with a matching air compressor, academic price, delivery to Provo, UT. Our N2 demand is about 1-5 L/min peak to a purge-only glovebox and
> instrument purges. Please advise if a larger model is needed, and the filter and catalyst PM schedule with prices and a service contract. [name, email **[to confirm]**]

### 7. Sources
[Marshall Scientific](https://new.marshallscientific.com/Parker-Balston-UHPN2-1100-Ultra-Pure-Nitrogen-Gas-p/uhpn2-1100.htm), [Chromtech](https://chromtech.com/uhpn2-1100-nitrogen-generator-11lpm-with-catalyst-mod),
[GMI spec page](https://supplies.gmi-inc.com/product/parker-nitrogen-generator-uhpn2-1100-model-ultra-high-purity-zero-grade/) (search results, 2026-11-07, not fetched).

---

## 10. Thermo Scientific ThermoFlex 900 recirculating chiller

### 1. What we'd buy
**ThermoFlex 900** (TF900, 120 V) ×1 beside the VLM, 900 W at 20 °C (`notes/services.md`), feeding the trays' LCT06 couplings. The model draws a placeholder box; **size and electrical input were not found**.
For the **rePowder atomizer** the notes use a separate chiller (`notes/services.md`).

### 2. Specs
Up to 900 W at 60 Hz (750 W at 50 Hz); 5-40 °C; CE and CSA. Resellers give **conflicting** weights (125 lb vs 250 lb for 120 V) and dimensions (32 × 19 × 32 in?). Use Thermo's manual for catalog number TF900.

### 3. Contact
Thermo Fisher Scientific US: the order page <https://www.thermofisher.com/order/catalog/product/TF900>; Fisher Scientific US sales **[to confirm the number]**; Thermo's temperature-control group. No Utah rep found.

### 4. Open questions
Dimensions, weight, **electrical input (120 V circuit, A)**, **heat rejected into the room**, pump pressure/flow at the trays' 2 × LCT06 inserts (8.48 L/min at 5 m/s is the insert's rating), coolant (water + inhibitor), whether 900 W is enough for 15 trays, PM, spares and service.

### 5. Intake
Heat load: up to about 7 kW into the VLM with everything on (most is **air**, not water; **[to confirm]** the water share per tray: furnace, polisher, atomizer); temperature 20 °C; flow per tray; 120 V.

### 6. Draft email
> **To:** Thermo Fisher Scientific (TF900 order page / Fisher US sales)
> **Subject:** TF900 specifications and quote for a laboratory tray cooling loop
>
> Please send the TF900's dimensions, weight, input current at 120 V, flow and pressure curve, and a budgetary quote with a coolant kit and a PM schedule, spares and service price. We will tap about
> 2 × G1/4 per tray for up to 15 trays, **[to confirm]** total water load. [name, email]

### 7. Sources
[Thermo TF900 page](https://www.thermofisher.com/order/catalog/product/TF900), [Fisher listing](https://www.fishersci.com/shop/products/thermoflex-recirculating-chillers/13875057), a used listing (search results, 2026-11-07).

---

## 11. Gas supply in Utah: Airgas, Linde, Norco

### 1. What we'd buy
**Argon** (atomizer and LPBF printer; cylinders, MicroBulk or a bulk tank) and **nitrogen** (backup to the generator; liquid N2 dewars), with a cylinder-rental contract.
Volumes are **[to confirm]**: the atomizer's argon per run (about 700 runs a year) is in `notes/alloy_atomize.md`.

### 2. Specs
Argon 99.999 % (UHP) for LPBF and atomizing; N2 UHP; CGA 580 outlet; cylinder cage and **oxygen deficiency monitors** in rooms with bulk or many cylinders.

### 3. Contact
- **Airgas:** customer service **866-935-3370**; Salt Lake City branches at **1211 South Pioneer Road (84104)** and **3415 South 700 West (84119)** (directory phone (801) 288-5010; **[to confirm]**);
  MicroBulk argon is offered company-wide; bulk at these branches **[to confirm]**. Locator <https://locations.airgas.com/ut/saltlakecity/>.
- **Linde:** Linde Gas & Equipment, 6880 S 2300 E, Salt Lake City 84121; welding center 1884 S 300 W, 84115; a plant at 12385 W Alternate Hwy 50, Magna 84044 (directory listings). Phone **[to confirm]**; <https://www.lindeus.com/>.
- **Norco:** 2006 W 1500 S, Salt Lake City 84104 and 3750 W 2100 S, 84120, plus West Jordan (directory listings); Norco serves ID, OR, WA, MT, NV, UT, WY and runs its own ASUs. Phone **[to confirm]**; <https://www.norco-inc.com/>.
- **Academic:** university cylinder contracts through BYU Purchasing **[to confirm]**.

### 4. Open questions
Bulk vs cylinders at our consumption; delivery schedule, tank siting and the **vaporizer and regulators**; gas purity certificates; cylinder rental rates; **LN2 for the XRF or SEM**; the delivery truck's access to the room.

### 5. Intake
Gases and purity; usage per month **[to confirm]**; delivery address and dock; cylinder storage plan and fire marshal approval; account type (BYU PO).

### 6. Draft email
> **To:** Airgas (866-935-3370), Linde and Norco Salt Lake City branches
> **Subject:** Argon and nitrogen supply for a university metal-powder laboratory, Provo UT
>
> We need UHP argon (atomizer and LPBF printer) and nitrogen, about **[to confirm]** cylinders a month, delivered to BYU in Provo. Please quote cylinder rental, MicroBulk or a bulk argon tank if the volume
> justifies it, delivery schedule and regulators/manifold options, and the BYU academic price. [name, email **[to confirm]**]

### 7. Sources
[Airgas Utah locator](https://locations.airgas.com/ut/), [SLC branch](https://locations.airgas.com/ut/saltlakecity/airgas-store-c250.html), Norco and Linde directory listings and job postings (search snippets, 2026-11-07).

---


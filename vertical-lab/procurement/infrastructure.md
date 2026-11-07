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
- **Second pass (2026-11-07, about 22:15-23:00 UTC):** every contact below is marked `(verified: <url>, 2026-11-07)`, `(partial: ...)` or `(unverified: <reason>)`; the CSV has `contact_status` and `contact_status_note` columns. Contact status is about the vendor's own page only; nothing was sent or submitted.
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
- **Address:** Kardex Remstar Support & Service Center, 41 Eisenhower Dr, Westbrook, ME 04092 (verified: <https://www.kardex.com/en/company/kardex-locations>, 2026-11-07; the page gives no phone or email for it).
- **Phone:** **800-639-5805** appeared only in press releases of 2013-2018; no current Kardex US page lists a phone (unverified: the get-in-touch, service, imprint and locations pages show none, 2026-11-07).
- **Regional:** Kardex's own locations page lists US distributor points in MA, MI, CT, NY, CA (Concord) and OH and **none in Utah or the Mountain West**; each links back to the get-in-touch form (verified: <https://www.kardex.com/en/company/kardex-locations>, 2026-11-07).
  The lab's earlier quote came through **Hoj Engineering** (thread cited above). **Hoj Innovations (Hoj Engineering & Sales Co.)**, 862 West Fine Drive, Salt Lake City, UT 84119, is a Utah firm that
  lists Kardex miniload and AS/RS systems; Utah material-handling sales **801-266-8881**, main **(385) 437-6275**, `info@hoj.net`, `inquiry@hoj.net`, Mon-Fri 9-5 MST
  (verified: <https://hoj.net/pages/utah-locations>, <https://hoj.net/pages/contact-us>, <https://hoj.net/pages/automated-storage-retrieval-systems>, 2026-11-07).
  Whether Hoj is an authorized Kardex dealer for the Shuttle VLM, and for Utah, is **unverified**: its pages show the miniload and AS/RS lines but no Shuttle VLM page, and Kardex names no Utah dealer. Ask both.
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
- Address: [Kardex locations page](https://www.kardex.com/en/company/kardex-locations) (runner, 2026-11-07); the 800-639-5805 phone is from old press releases (<https://www.pr.com/press-release/532174>) and is unverified. Hoj: [hoj.net Utah locations](https://hoj.net/pages/utah-locations) (runner, 2026-11-07).
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
- **Email:** `info.usa@modula.com` (the first pass read it on Modula's contact page via the Pi; on 2026-11-07 the page returned a Cloudflare challenge to the runner and to the Pi's curl and headless Chromium, so it could not be re-read: unverified this pass).
- **Phone:** general **937-365-7860**; customer care **800-361-0785**; toll-free **877-648-9755** (unverified: same block, 2026-11-07).
- **Address:** Modula Inc., 5000 Commerce Center Drive, Franklin, OH 45005 (headquarters; also a Maine plant at 90 Alfred
  A. Plourde Parkway, Lewiston, ME 04240) (unverified: same block).
- **Web form:** <https://modula.us/contact-us/>. **Dealers:** <https://modula.us/dealer-network/> (a map; unreadable behind the same Cloudflare block, so no Utah dealer is confirmed; ask Modula which dealer serves Utah).
- **West-coast and Mountain West dealer candidates** (their own pages, 2026-11-07): **Pacific Integrated** says it is "an authorized distributor for Modula Vertical Lift Modules"; **(888) 550-5888**, `sales@pacificintegrated.com`; offices in Tacoma WA, Addison TX, Hayward CA and a sales office in Surprise AZ; no Utah office listed
  (verified: <https://www.pacificintegrated.com/?p=1662>, 2026-11-07). **Associated** (Raymond; "Platinum Level Modula Sales & Service Center"), 6450 Muirfield Dr, Hanover Park, IL 60133, **800-755-7201**, no service area stated
  (verified: <https://prod-cms-associated-solutions.raymondcorp.com/modula>, 2026-11-07). **Hoj Innovations** (Salt Lake City) is Kardex-oriented; no Modula listing found.
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
- [Modula's government capability statement](https://modula.us/wp-content/uploads/2021/04/Modula-Inc-Government-Capability-Statement.pdf), downloaded 2026-11-07 (200) but the PDF text could not be extracted here, so nothing in it is relied on.
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
- **Marketplaces (published business sites; enquiry forms not re-fetched this pass: unverified):** machineseeker (<https://www.machineseeker.com/>), werktuigen
  (<https://www.werktuigen.com/>), resale.info, used-machines.com: each listing has an enquiry form.
- **Dealer in Germany with the 996 mm unit:** [lagersysteme-paternoster.de](https://www.lagersysteme-paternoster.de/) (enquiry form).
- **US:** Vertical Storage USA / Outsource Equipment (existing contact, thread cited). No US used-VLM specialist found; Raymond West
  (California) sells new VLMs (unverified: not fetched). For a used Kardex unit in Utah, **Hoj Innovations** (Salt Lake City, 801-266-8881, `inquiry@hoj.net`; verified: <https://hoj.net/pages/contact-us>, 2026-11-07) services Kardex systems and may know of units; ask.

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
  48377; get-started form <https://www.universal-robots.com/contact-us/get-started/>; partner portal <https://partners.universal-robots.com/>
  (verified: <https://www.universal-robots.com/contact-us/>, 2026-11-07; the partner portal itself was not opened).
- **MiR:** global `mail@mir-robots.com` (verified: <https://www.mobile-industrial-robots.com/distributors>, 2026-11-07); the +45 20 37 75 77 Denmark number is not on that page (unverified: first pass read it on the contact page, which now returns 404).
  The distributors page is a locator; no North America MiR sales email or phone is published there (unverified: none found; go through a distributor).
- **Distributors found:** **Hartfiel Automation** (distributes SICK, Universal Robots and MiR) **1-800-331-7301**; its MiR page lists **Utah, Colorado, Wyoming and Nevada** among the states where the MiR line is available
  (verified: <https://www.hartfiel.com/mir-robots/>, via the Pi's headless Chromium, 2026-11-07; the list sits under the MiR page, not specifically the MiR250). Hartfiel's Wheat Ridge, Colorado office is unverified (the runner got 403 and the pages carry no address). **Cross Company** (UR Certified System Integrator): location unverified, site blocks both runner and Pi (403).
  **Automation Distribution** (lists the UR10e with prices; not re-fetched, unverified).
- **Utah-based UR or MiR integrator:** none found (unverified: the UR partner locator is a script-driven page; two web searches named none). **Hoj Innovations** (Salt Lake City; <https://hoj.net/pages/autonomous-mobile-robots>) sells autonomous mobile robots but names no brand on the page, so ask whether it carries MiR.
- **Academic:** UR Academy and UR's university discounts exist (unverified: ask the distributor).

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
- [MiR contact](https://www.mobile-industrial-robots.com/contact) (first pass via Pi; now 404); [MiR distributors](https://www.mobile-industrial-robots.com/distributors) (runner, 2026-11-07); [UR contact](https://www.universal-robots.com/contact-us/) (runner, 2026-11-07); [Hartfiel MiR page](https://www.hartfiel.com/mir-robots/) (Pi Chromium, 2026-11-07).
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
- **Phone:** **1-888-762-6847** (head office, Lévis, QC); outside US/Canada +1 418 380 2788 (verified: <https://robotiq.com/contact-us>, 2026-11-07).
- **Quote page:** <https://robotiq.com/quote>; partners <https://robotiq.com/robotiq-partners> (the partners page lists no Utah distributor; a web search found none either; unverified: ask Robotiq, whose support page offers "Contact Your Local Distributor").
- **Email:** none published on the contact page. **Price:** Robotiq publishes none; distributors list the 2F-85 from about **$4,999-$9,271**
  (Automation Distribution $9,271 list, UR Kit $5,885; the Robotics Center $5,825): wide spread (unverified: reseller listings, not re-fetched).

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
Site <https://www.realsenseai.com/>; sales through the form at <https://www.realsenseai.com/contact/> ("Talk with Sales", with a phone field but no published email or number) and the maker's own store <https://store.realsenseai.com/> (which lists the D405) (verified: both, runner, 2026-11-07). Buy through **DigiKey** (list $1,761-2,374, zero stock on
2026-11-07), or resellers at **$260-300** (Aztekc $273, Ichome $279). One reseller shows the D405 discontinued in Japan: ask RealSense.
**No sales email or phone is published; use the Contact page's "Talk with Sales" form.** The D405 series page is <https://www.realsenseai.com/products/d405-series/> (verified, 2026-11-07). Reseller prices are unverified (search snippets).

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
  published (unverified: staubli.com returned 403 to the runner and to the Pi's curl and Chromium on 2026-11-07; the Windsor address and number agree across several industry directories, which are not the vendor's page; one directory shows an `ec.us@staubli.com` address and another 855-583-1201, neither used). The Duncan, SC office (+1 864 433 1980) handles fluid connectors, robotics and textile, not electrical.
- **Fluid connectors** (air, N2, water) come from the Duncan, SC fluid-connectors business (unverified: staubli.com blocked, 2026-11-07).
- **Distributors:** none found for Utah (unverified: same block).

### 4. Open questions
1. **Mating cycles** per insert, and the **life of the water and air inserts** at 100 docking cycles a day.
2. Whether a **single plate** can carry mains + Cat 6A + air + N2 + 2 water in the footprint the model uses, and which modules to pick.
3. **Misalignment** a tray's side plate will see in the VLM's extractor (4 mm / ±2° is the published limit).
4. **Hot-plugging** power (39 A) vs our contactor; the **dry-break** rule for water (no drip).
5. Quote per set, and a **mock-up kit** to test a dock and a plate on a bench; PM, spares, service.

### 5. Intake
Quantity: 15 plates and 16 docks (15 slots plus the bay) **[to confirm]**; cycles: an assumed 100 a day at the openings **[to confirm]**; media as listed; ambient 15-40 °C;
supply: 120 V single-phase per tray (5 kVA continuous at 80 %); N2 99.9999 % at low flow; chilled water at 20 °C.

### 6. Draft email
> **To:** Stäubli Electrical Connectors, Windsor CA (website form; +1 707 838 0530)
> **Subject:** Budgetary quote: CombiTac uniq docking set (4 power, Cat 6A, air, N2, 2 × water), 16 docks and 15 plates
>
> We are building a docking coupling for instrument trays in a vertical lift module: four Ø3 mm power units, one 10 Gbit RJ45 module, an RCT06 air, an SCT03
> nitrogen and two LCT06 water inserts on a CombiTac align 4 plate, mated an assumed 100 times a day. Please quote 15 plates and 16 docks (budgetary, academic),
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
(unverified: `tripplite.eaton.com` redirects the runner and the Pi to the Eaton site's pages, which list no presales address or phone, 2026-11-07; a web search of the Eaton-hosted 5PX G2 product page returned the same address, phone, +1 773-869-1329 and `cpdipresaleshelp@eaton.com`, so it is plausible but not re-read). No Utah Eaton rep found.
Resellers: CompSource **800-356-5794** (seller listing; compsource.com returned 403, unverified), Provantage 800-336-1166 (search result, unverified), Barcodes Inc. (quote form), DigiKey.

### 4. Open questions
Runtime at 300-1,000 W; **battery chemistry**, the cycle life when it is recharged every dock cycle (an assumed 100 transits a day, **[to confirm against `out/upkeep_model.json`]**); mounting on its side and **orientation limits**;
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
> We plan 15 UPSs, each carrying a laboratory tray for 6-10 s during transfers in a vertical lift module, recharged an assumed 100 times a day. Please quote 15 × 5PX1500RTNG2 (with network card)
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
Parker Balston technical services **1-800-343-4048**, 8 AM-5 PM Eastern, `balstontechsupport@parker.com` (North America), Industrial Gas Filtration and Generation Division, 242 Neck Road, Haverhill, MA 01835, <https://www.parker.com/labgas> (partial: a web search reports these from Parker's own UHPN2 upgrade-instructions PDF, <https://www.parker.com/content/dam/Parker-com/Literature/IGFG/PDF-Files/TI-UHPN2-UPG_RevA.pdf>, but parker.com returned 403 to the runner, the Pi and WebFetch, and balstonlabgasgenerators.com did not connect, 2026-11-07).
Sales through a lab-supply distributor (above). No Utah distributor found (unverified).

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
Thermo Fisher Scientific US: the order page <https://www.thermofisher.com/order/catalog/product/TF900>; Fisher Scientific customer service **1-800-766-7000** (partial: shown as the number to call in Fisher's own page text, <https://www.fishersci.com/us/en/contact-us.html>, via the Pi's Chromium, 2026-11-07; the page lists no sales-specific line). thermofisher.com's contact page lists no number in its page text (the TF900 order page loaded but gave no phone). No Utah rep found (unverified).

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
- **Airgas:** customer service **866-935-3370**; Salt Lake City: the **Airgas Store at 3415 South 700 West (84119), (801) 288-5010**, and an **Airgas Dry Ice site at 1211 South Pioneer Road (84104), (801) 977-9215** (the first pass wrongly listed the Pioneer Road site as a gas branch)
  (verified: <https://locations.airgas.com/ut/saltlakecity/>, 2026-11-07; 866-935-3370 is on that page too). Airgas's general contact form is <https://www.airgas.com/contact-us> (verified). MicroBulk argon is offered company-wide; bulk at these branches is unverified (ask).
- **Linde:** Linde Gas & Equipment cylinders and welding supplies: product orders **1-800-225-8247**, customer service and technical support **1-877-772-9247**; general **1-844-44LINDE (1-844-445-4633)**, `contactus@linde.com`
  (verified: <https://www.lindeus.com/contact-us>, 2026-11-07). Salt Lake City sites 6880 S 2300 E (84121), welding center 1884 S 300 W (84115) and a Magna plant at 12385 W Alternate Hwy 50 (84044) come from directory listings; Linde's page names no Utah branch phone (unverified: use the national lines to be routed).
- **Norco:** 2006 W 1500 S, Salt Lake City 84104 and 3750 W 2100 S, 84120, plus West Jordan (directory listings); Norco serves ID, OR, WA, MT, NV, UT, WY and runs its own ASUs (unverified: <https://www.norco-inc.com/> loads but its branch finder is script-driven and gave no branch address or phone to the runner or the Pi's Chromium on 2026-11-07; a phone-less "Contact Us" and "Branch Finder" are the only routes found).
- **Academic:** university cylinder contracts through BYU Purchasing (unverified). BYU Financial Services' tax pages say a vendor needs the University's Utah charitable exemption certificate (purchases of $1,000 or more) or a TC-73 seller contract (under $1,000); see <https://finserve.byu.edu/sales-tax-faqs> (search result, 2026-11-07); BYU tax-exempt status is for BYU Purchasing to confirm.

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
[Airgas Utah locator](https://locations.airgas.com/ut/), [SLC branch](https://locations.airgas.com/ut/saltlakecity/airgas-store-c250.html), [Airgas locator](https://locations.airgas.com/ut/saltlakecity/) and [Linde contact page](https://www.lindeus.com/contact-us) (runner, 2026-11-07); Norco and Linde Utah addresses from directory listings and job postings (search snippets).

---


## 12. Labconco Protector XStream, 4 ft ducted hood

### 1. What we'd buy
**Labconco Protector XStream laboratory hood, 4 ft (1219 mm)**, on a base cabinet (1219 × 958 × 2581 mm, about 260 kg, on the floor), 18 in (457 mm) sash stop, ducted to the building exhaust (`notes/instruments_r7.md`).
Role: wet work (etching without HF, solvents, the sieve's IPA bath). Round 8 removed HF: Keller's reagent goes to the BYU facility, not this hood (`notes/lab_r8.md`).

### 2. Specs
Labconco's page (`labconco.com/p/protector-xstream-laboratory-hoods`); the spec PDF was blocked. Ducted: airflow per the sash stop and face velocity (typically 100 fpm); **a blower and duct routing are separate**
(Labconco sells blowers and the Protector hood's Optional Basecabinet). Electrical 115 V, **[to confirm]**.

### 3. Contact
- **Labconco:** sales **(816) 333-8811**, toll-free **(800) 821-5525**, fax (816) 363-0130, 8811 Prospect Ave, Kansas City, MO 64132-2696; form <https://www.labconco.com/contact> ("Request a Quote") (verified: <https://www.labconco.com/contact>, 2026-11-07).
- **Utah representative:** **Jackson Corning**, Sales Representative (Northern California, Nevada, Utah), <https://www.labconco.com/sales/us-and-canada-sales/jackson-corning>; no email or direct phone listed (use the main line) (verified: <https://www.labconco.com/sales/us-and-canada-sales>, 2026-11-07). Distributors: <https://www.labconco.com/distributors>.
- **Academic:** state contract / GSA pricing via distributors (unverified: ask).

### 4. Open questions
Exact **exhaust CFM** and static pressure for a 4 ft with the 18 in sash stop; a **VAV controller** and its BMS (BACnet) interface for a hood that a robot may feed; **can a robot reach through the sash** (a motorised sash?);
service after install: certification (ASHRAE 110 test) and PM; consumables (filters not used), spares, service price.

### 5. Intake
Hood use: acids, solvents, IPA; **no HF**, no perchloric; ducted exhaust **[to confirm routing and capacity]**; floor load; ceiling height 2581 mm hood fits; compliance with ANSI/AIHA Z9.5 **[to confirm]**.

### 6. Draft email
> **To:** Jackson Corning, Labconco (via 800-821-5525 or the contact form), and the Utah distributor
> **Subject:** Budgetary quote: Protector XStream 4 ft with base cabinet and blower, BYU Provo
>
> Please quote a 4 ft Protector XStream with the 18 in sash stop, a base cabinet (acid or flammable), a sash-position sensor and a motorised sash if available, and a blower. Please give the exhaust flow and static pressure,
> the BMS interface, and the ASHRAE 110 certification, PM schedule, spares and a service contract in Utah. [name, email **[to confirm]**]

### 7. Sources
[Labconco contact page](https://www.labconco.com/contact) and [US & Canada sales](https://www.labconco.com/sales/us-and-canada-sales) (runner, 2026-11-07); [product page](https://www.labconco.com/p/protector-xstream-laboratory-hoods) as cited in `notes/instruments_r7.md`.

---

## 13. Sentry Air Systems ductless hood, 24 in (on a tray)

### 1. What we'd buy
**Sentry Air 24 in ductless hood** with its blower, 1030 × 610 × 715 mm, about 41 kg, on a VLM tray (`notes/instruments_r7.md`): the only ductless hood found under 856.5 mm (Air Science's Purair Basic is 889 mm tall; Erlab's Captair is taller).
Candidate catalogue numbers seen: SAS-224-DCH (24 in, 80 cfm, acrylic), SAS-324-HEMS. **[to confirm the model]** with Sentry.

### 2. Specs
24 D × 26 W × 25 H in outside (610 × 660 × 635 mm); carbon filters (solvent vapours, **not HF**); the air returns to the room, i.e. into the VLM. Mains 115 V.

### 3. Contact
**sales@sentryair.com**, **1.800.799.4609**, Sentry Air Systems, 21221 FM 529 Rd, Cypress, TX 77433 (verified: <https://www.sentryair.com/>, 800-799-4609 and `sales@sentryair.com` shown on the page, also 877-780-7452 and 713-690-2153 international; via the Pi's Chromium, 2026-11-07, since the runner got 406; the Cypress, TX address is from the product sheet, unverified). Dealers: Cal-Pac Lab (calpaclab.com), SPER Direct (not re-fetched, unverified).

### 4. Open questions
Filter **life and the vapour list** (IPA, ethanol, etchants); **air return into the VLM** (is it acceptable, and the flow); a **robot-actuated sash** or access door; blower noise and heat; **PM** (filter swap hours, price), spares, service.

### 5. Intake
Chemicals and volumes (IPA, ethanol; no HF); duty cycle; on a tray with 15 mm clearance from instruments; location in the VLM enclosure; 115 V.

### 6. Draft email
> **To:** `sales@sentryair.com`
> **Subject:** Quote: 24 in ductless hood (low profile) for a laboratory tray, BYU
>
> We want a 24 in ductless hood that fits under 856 mm total height (your standard is 635 mm outside). Please quote it with the blower and carbon filter set, state the filter life for IPA and ethanol, whether a motorised sash is possible,
> the PM schedule, filter and spare prices and a service contract. [name, email **[to confirm]**]

### 7. Sources
[Sentry Air page](https://www.sentryair.com/dfhapp.htm) as cited in `notes/instruments_r7.md`; contact details from a [Cal-Pac listing](https://calpaclab.com/24-ductless-fume-hood-acrylic-80-cfm/sas-224-dch) and a search snippet quoting the product sheet (2026-11-07).

---

## 14. Tray glovebox: Vigor and others

### 1. What we'd buy
A **custom N2 glovebox, purge-only, with a mini antechamber at the front**, 1390 × 830 × 810 mm, about 140 kg (estimate), on a VLM tray (`notes/instruments_r7.md`); for Mg, Li master alloys and fines under about 63 µm (`notes/lab_r8.md`).
Vigor's standard box is 1200 × 750 × 900 mm, **too tall** for a tray at 856.5 mm: we need a **custom height** (810 mm).

### 2. Specs (Vigor)
Lengths 1200, 1500, 1800, 2400 mm; width 750; height 900. Antechambers: large (370 mm ID × 600 mm) and **small (150 mm ID × 300 mm, manual only)**; 220 mm aluminium glove ports; "each glovebox is custom made". N2 purge is not mentioned, so ask.

### 3. Contact
- **Vigor Tech USA:** 5718 Westheimer Rd, Suite 1000, Houston, TX 77057; **no email or phone published**, product enquiry form on <https://www.pharmaceutical-tech.com/products/vigor-tech-usa/standard-gloveboxes> (the distributor's page) (unverified: vigortechusa.com gave no readable contact to the runner or the Pi's Chromium, 2026-11-07; the address is from the first pass).
- **Plas-Labs** (Lansing, MI): US sales **(800) 866-7527**, also (517) 372-7177 and (517) 372-2857 (verified: <https://www.plas-labs.com/contact>, 2026-11-07); it lists "Custom Glove Boxes" as a product line.
- **Others to ask:** MBraun (<https://www.mbraunusa.com/>; unverified: its contact page was not readable, 2026-11-07), Terra Universal (unverified: Cloudflare challenge, 2026-11-07), Inert Technology (PureLab) (unverified: contact page 404).

### 4. Open questions
**Custom height of 810 mm** and the 1390 mm length; **robot loading** through an antechamber door or a glove-free port; **O2/H2O sensor** (purge-only: target ppm); N2 consumption (L/min) against the 1.1 L/min generator; **door actuators**
for the antechamber; a **catalyst/regeneration** option; PM, spares, a leak-test schedule, service.

### 5. Intake
Application: handling Mg, Li master alloys and fines in sealed cans; atmosphere N2 with O2 under **[to confirm]** ppm; interior size; weight limit on a tray (about 140 kg); glove ports; robot access; gas supply (the N2 coupling); power 120 V.

### 6. Draft email
> **To:** Vigor Tech USA (website form), MBraun and Plas-Labs
> **Subject:** Custom purge-only glovebox, 810 mm tall, for a laboratory tray: budgetary quote
>
> We need a glovebox no taller than 810 mm, 1390 mm long, 830 mm deep, with a mini antechamber at the front that a robot (not a person) loads, and N2 purge only. Please quote it with an O2 sensor and a door actuator,
> state the N2 consumption, glove-port options, and the PM and leak-test schedule, spares and service price. [name, email **[to confirm]**]

### 7. Sources
[Vigor Tech USA standard gloveboxes](https://www.pharmaceutical-tech.com/products/vigor-tech-usa/standard-gloveboxes) (runner, 2026-11-07); `notes/instruments_r7.md`.

---

## 15. Stream cameras: Raspberry Pi 5, HQ Camera, Camera Module 3 Wide

### 1. What we'd buy
Per tray, 2-3 camera units: **Raspberry Pi 5** (16 GB or 8 GB), **Raspberry Pi HQ Camera** with a **16 mm C-mount lens** (22.2 × 16.8° view) and **Camera Module 3 Wide** (102 × 67°; 120° diagonal), a PoE or USB-C supply, a case and 2020 posts (`notes/services.md`).
The lab already runs Pi streams (picam-ot2 at 144p; `CLAUDE.md`).

### 2. Specs
Raspberry Pi's figures (`notes/services.md`). **Price shock:** the 16 GB Pi 5 rose to **$385** on 2 Nov 2026 (reported), from $305; the 8 GB model's price **[to confirm]**. Consider the **8 GB** Pi 5 or a Pi 4 for stream-only duty.

### 3. Contact
No sales email: buy from **Raspberry Pi Approved Resellers** (<https://www.raspberrypi.com/resellers/>; unverified: raspberrypi.com returned 403 to the runner and a bot page to the Pi, 2026-11-07). US: **PiShop.us**, **Adafruit**, **SparkFun**, **CanaKit**, **Digi-Key**.
**PiShop.us:** contact form at <https://www.pishop.us/contact-us/>, `support@pishop.us`, **844-774-4338** (it is an online-only store) (verified: <https://www.pishop.us/contact-us/>, 2026-11-07). **Adafruit:** <https://www.adafruit.com/contact> loads (verified) but lists a support forum and no sales email or number that we could extract; ask for a quote through its site (unverified).
`compliance@raspberrypi.com` is for compliance questions only (first pass; unverified now). Education: Raspberry Pi has an education programme (unverified).

### 4. Open questions
Stock and lead time for **30-45 Pis**, the price if bought in bulk (Raspberry Pi's "industrial" sales team for 100+), the **HQ Camera**'s availability, lens options, the **Pi 5's power draw** inside the enclosure's heat (60 W per tray idle), and an industrial Pi (Compute Module 5) alternative.

### 5. Intake
Quantity: 15 trays × 2-3 units = 30-45 sets, plus spares; use: streaming and QA to YouTube and a scheduler over Ethernet; environment up to 40 °C inside a VLM.

### 6. Draft email
> **To:** PiShop.us and Adafruit sales (their quote forms)
> **Subject:** Quote: 40 × Raspberry Pi 5, 20 × HQ Camera with 16 mm lens, 25 × Camera Module 3 Wide, PoE HATs
>
> Please quote these with academic pricing and tell us the stock, the lead time and whether a volume discount applies. [name, email **[to confirm]**]

### 7. Sources
[Raspberry Pi 5 product page](https://www.raspberrypi.com/products/raspberry-pi-5/) (runner), price news [techenclave](https://techenclave.com/news/items/raspberry-pi-raises-the-16gb-pi-5-price-by-80-to-385) (search snippet), 2026-11-07.

---

## 16. PiKVM V4 Mini

### 1. What we'd buy
**PiKVM V4 Mini** ×1+ (120 × 68 × 24 mm, 0.35 kg; HDMI capture to 1920 × 1200; USB keyboard and mouse emulation; ATX control board in the kit): remote screen and keyboard for the VHX-7000's controller PC (`notes/instruments_r7.md`).

### 2. Specs
PiKVM V4 Mini datasheet (<https://docs.pikvm.org/v4/v4mini_datasheet.pdf>): no USB-C display input (the **V4 Plus** is the model with KVM switching). Ethernet; power by USB-C or PoE **[to confirm]**.

### 3. Contact
No support or sales email is published. PiKVM's own buy page lists its resellers: **HiPi** (shop.hipi.io), **CloudFree** (cloudfree.shop), **Pimoroni** and others, and its support page points to a Discord (<https://discord.gg/bpmXfz5>), Reddit (r/pikvm) and GitHub
(verified: <https://pikvm.org/buy/> and <https://pikvm.org/support/>, 2026-11-07). PiShop.us and Newegg ($589.88) stock it too (reseller listings, unverified as authorised). Contact CloudFree or HiPi for a quote; neither store's contact page was read.

### 4. Open questions
Does the VHX-7000's PC accept a USB HID emulation and a capture of its HDMI at its resolution; **Remote Desktop** as an alternative; stock and a 2-3 unit price.

### 5. Intake
Quantity 1-3; target: Windows PCs of instruments (VHX-7000, EZware PC); network: tray Ethernet.

### 6. Draft email
> **To:** PiShop.us (quote form)
> **Subject:** Quote: PiKVM V4 Mini, 3 units, academic
>
> Please give the price, stock and lead time, and whether the V4 Mini is supported for Windows 7 and Windows 10 targets over HDMI. [name, email **[to confirm]**]

### 7. Sources
[Pimoroni](https://shop.pimoroni.com/products/pikvm-v4-mini), [PiShop.us](https://www.pishop.us/product/pikvm-v4-mini/), [Newegg](https://www.newegg.com/p/3D0-0001-000K4) (search results, 2026-11-07, not fetched).

---

## 17. Primera LX500c + AP380 (packaging station)

### 1. What we'd buy
**Primera LX500c** colour label printer (print width 19-108 mm; 264 × 389 × 180 mm closed, 3.2 kg) **×1** and **AP380** wrap-around label applicator (containers 15-170 mm across; 340 × 508 × 226 mm, 9.07 kg) **×1**, at the packaging station (`notes/instruments_lab.md`).
Primera sells **no print-and-apply bundle**, and labels die-cut on the LX610 are not compatible (the notes).

### 2. Specs
Interfaces: USB; the AP380 has a foot pedal or a start signal **[to confirm]**; the LX500c has a Windows driver and a Mac driver (no Linux driver **[to confirm]**). Labels and ribbons are consumables.

### 3. Contact
**sales@primera.com**, **+1-763-475-6676**, toll-free **800-797-2772**, fax +1-763-475-6677, Primera Technology, Two Carlson Parkway North, Plymouth, MN 55447; live chat (Mon-Fri 7:00-22:00 CDT, Sat 11:00-20:00). No sales form (verified: <https://www.primera.com/contact-us>, `sales@primera.com`, +1 763 475-6676 and +1 800 797-2772 on the page, 2026-11-07). No Utah distributor found.

### 4. Open questions
A **robot start signal** (a dry contact) for the AP380; a **Linux or API** way to print from the scheduler (SDK, CUPS); **label stock** for glass jars and the AP380's wrap on 30-500 mL jars; ink cost per label; PM, **printheads and ink as consumables with prices**, service.

### 5. Intake
Items: jars 30-500 mL (15-170 mm diameter), about 1,000-2,000 a year **[to confirm]**; label size; environment: indoor; workflow: robot places the jar in a nest.

### 6. Draft email
> **To:** `sales@primera.com`
> **Subject:** LX500c + AP380 for robot-loaded jar labelling: budgetary quote and integration questions
>
> We want one LX500c and one AP380 at a robot cell. Please quote them, and tell us how a controller starts the applicator (a contact closure), whether there is a Linux/API interface for the LX500c, which label stock suits glass jars of 30-500 mL, and the consumable cost per label,
> the PM schedule and spares. Academic price, please. [name, email **[to confirm]**]

### 7. Sources
[Primera contact page](https://www.primera.com/contact-us) (runner, 2026-11-07); product sizes from `notes/instruments_lab.md` (primera.com).

---

## 18. Zebra ZD621t

### 1. What we'd buy
**Zebra ZD621t**, 4 in thermal transfer, 203 dpi (104 mm print width; 202 × 267 × 192 mm, 2.5 kg) ×1, printing the 4 × 6 in label for the lid (`notes/instruments_lab.md`; Uline S-6802 labels).

### 2. Specs
USB, Ethernet and serial; **ZPL** over TCP 9100 (printable from a Python scheduler); Zebra's own site refused the runner earlier (the notes).

### 3. Contact
Zebra's own contact page (<https://www.zebra.com/us/en/about-zebra/contact-zebra.html>) offers a "Contact Sales" pre-sales form and lists no phone or email; its partner page offers "Buying From an Authorized Zebra Reseller" and "Find a Partner" (<https://www.zebra.com/us/en/partners/find-a-partner.html>)
(verified: both, via the Pi, 2026-11-07, since the runner got 406). Buy from a **Zebra Authorized Partner**. Zebra's US sales phone is not published on that page (unverified).

### 4. Open questions
Ribbon type for glass-jar lids; **auto-peel** and a presenter for robot pick-up; ZPL printing from Python; PM (printhead life), consumable and service prices.

### 5. Intake
Label 4 × 6 in; volumes **[to confirm]**; ribbon wax/resin; network Ethernet.

### 6. Draft email
> **To:** a Zebra Authorized Partner (via the locator)
> **Subject:** Quote: ZD621t with peeler and ribbon, university lab
>
> One ZD621t (203 dpi, Ethernet) with a label peeler/presenter, 12 rolls of 4 × 6 in thermal-transfer labels and ribbons, academic price; please give printhead life and the PM schedule and service price. [name, email **[to confirm]**]

### 7. Sources
Zebra pages attempted via the runner (HTTP 406) and the Pi (no content, 2026-11-07); size and print width from `notes/instruments_lab.md`.

---

## 19. Uline H-190 impulse sealer

### 1. What we'd buy
**Uline H-190 12 in impulse sealer** ×1 (452 × 84 × 188 mm, 4.2 kg; seals up to 8 mil poly) plus the pick-and-pack foam shipper **S-23611** (324 × 311 × 108 mm), labels **S-6802** (`notes/instruments_lab.md`).

### 2. Specs
Uline's catalogue; mains 120 V; a foot-pedal or timer; **no robot interface**.

### 3. Contact
Uline sales **1-800-295-5510**, `customer.service@uline.com`; <https://www.uline.com/> (verified: <https://www.uline.com/>, 2026-11-07). Uline's locations page (<https://www.uline.com/Corporate/About_Locations>) lists no Utah or Salt Lake City site; the nearest listed are Ontario, CA (Los Angeles) at 4810 South Hellman Avenue and Dallas, TX (verified, 2026-11-07), so expect shipping from there, not a Utah pickup.

### 4. Open questions
Whether the sealer can run from a **relay** (timer) for a robot; sealing thickness; **spares**: replacement heating element and Teflon tape, with prices; warranty.

### 5. Intake
Bag 8 mil max; volumes **[to confirm]**; BYU purchase account.

### 6. Draft email
Order through the website or call 1-800-295-5510 with the part numbers above (no quote needed); ask for the element and Teflon-tape spares.

### 7. Sources
[Uline poly bags page](https://www.uline.com/Cls_01/Impulse-Sealers) (runner, 2026-11-07; only the phone number was usable); sizes from `notes/instruments_lab.md`.

---

## 20. Powder jars, grounded racks, gasketed metal cans

### 1. What we'd buy
**Clear glass wide-mouth jars with PTFE-lined caps, 30-500 mL, hundreds: 581 in the model** (trays N and O, the sample store on tray J and the packaging station; `notes/lab_r8.md`), in **grounded racks** (conductive, ESD, with a bond wire to the tray)
and **gasketed metal cans** for fines under about 63 µm, Mg and the Al-Li master alloy (`notes/lab_r8.md`: "sealed gasketed metal cans, or glovebox only").
The model's jar sizes are "typical wide-mouth straight-sided jars, not a supplier's drawing (estimates)".

### 2. Specs to fix
Material: borosilicate or soda-lime glass; **PTFE-lined phenolic or PP caps**; mouth 38-70 mm; label 20-60 mm; **cans:** steel or tinplate, **gasket** (silicone or Viton), a **UN-rated** can if shipped; static-dissipative racks (surface resistance 10⁶-10⁹ Ω).

### 3. Contact (candidate suppliers, none fetched)
- **Uline**, **1-800-295-5510**, glass jars and steel cans (<https://www.uline.com/>).
- **Qorpak** (clear glass jars with PTFE-lined caps; part of Berlin Packaging): `Qorpak@BerlinPackaging.com`, **800-922-7558** (verified: <https://www.qorpak.com/contact>, 2026-11-07). **Berlin Packaging**: **800-363-9822**, contact form (verified: <https://www.berlinpackaging.com/contact>, 2026-11-07).
  **Fisher Scientific**: customer service **1-800-766-7000** (partial: in Fisher's own page text, <https://www.fishersci.com/us/en/contact-us.html>, 2026-11-07); VWR not checked (unverified).
- Racks: a **custom ESD rack** (laser-cut or 3D-printed in conductive material) by us; an ESD supplier is not yet named (open gap).

### 4. Open questions
Lot-controlled **glass with certificates**; cap liners that do not shed PTFE; **jars for ICP** (acid-washed); static buildup in glass versus HDPE (combustible metal dust): **grounding practice for NFPA 484**; can-style gaskets; pricing at 500-1,000 quantity; **breakage** by a robot gripper (use of 85 mm 2F-85 pads).

### 5. Intake
Quantity: 581 jars at the start, then growth **[to confirm]**; size mix **[to confirm]**; contents: Al, Cu alloys, Mg and Li master alloys; labels by our Primera printer.

### 6. Draft email
> **To:** Uline (1-800-295-5510), Qorpak (`Qorpak@BerlinPackaging.com`, 800-922-7558) and Berlin Packaging
> **Subject:** Quote: 600 glass jars, PTFE-lined caps (30, 60, 125, 250, 500 mL), 100 steel gasketed cans
>
> We store metal powders in sealed glass jars (clear, wide-mouth, PTFE-lined caps) and in gasketed metal cans for fines. Please quote 600 jars in these sizes and 100 cans with silicone or Viton gaskets, and tell us whether you have static-dissipative options, lot certificates and the lead time. [name, email **[to confirm]**]

### 7. Sources
`notes/lab_r8.md` (jars, 2026-11-05 and 2026-11-07); Uline phone number from the runner fetch, 2026-11-07.

---

## 21. BYU Spectroscopic Facility: Agilent 8900 ICP-MS/MS (a service, not a purchase)

### 1. What we'd use
The **Agilent 8900 ICP-MS Triple Quadrupole** at the BYU Spectroscopic Facility, as an **internal service** (the facility does its own sample digestion, so nothing in the lab uses HF; `notes/lab_r8.md`).
About 112 15 mL ICP-MS tubes in the model, plus the CubXL's 0.5 mL tubes (`notes/instruments_r7.md`).

### 2. Published
**$35/hour for internal BYU users and $70/hour for external users** (the facility's atomic-analysis page, 2026-11-07).

### 3. Contact
**Faculty advisor: Jason J. Sorensen**, `jason.sorensen@byu.edu`, C203 BNSN, **(801) 422-7083** (verified: the facility's own contact page, <https://labs.chem.byu.edu/byu-spectroscopic-facility/contact>, via the Pi, 2026-11-07). Facility page: <https://labs.chem.byu.edu/byu-spectroscopic-facility/atomic-analysis>.

### 4. Open questions
Sample **turnaround**; **acceptable matrices** and digestion for Al, Cu, Ni alloys (no HF: Si, Al-Li master alloy, Ti?); **batch size** (hundreds of tubes), **the hourly rate per sample**; whether the facility can **accept robot-delivered racks** or needs people; data format and an
**API/LIMS**; the **Training** pathway; the publication policy.

### 5. Intake
Elements and ranges (Al, Si, Cu, Ni, Fe, Mg, Li, Ce) **[to confirm]**; volume (hundreds a year); digest method; the lab's own sample prep (1.5 in mounts to a rinse; 150 µL rinses).

### 6. Draft email
> **To:** `jason.sorensen@byu.edu`
> **Subject:** ICP-MS service for the BYU Vertical Cloud Lab: sample preparation, turnaround and batch rates
>
> Hello Dr. Sorensen, the Vertical Cloud Lab (Mechanical Engineering) would like to send alloy digests (Al, Cu, Ni, Mg, Li) to the Agilent 8900 as an internal user ($35/h). Could you tell us which digestion you run (we avoid HF), the number of samples per hour,
> the turnaround, the minimum batch, the data format and who loads samples? [name, email **[to confirm]**]

### 7. Sources
[Atomic analysis page](https://labs.chem.byu.edu/byu-spectroscopic-facility/atomic-analysis) and [contact page](https://labs.chem.byu.edu/byu-spectroscopic-facility/contact), both via Pi (the runner got 403), 2026-11-07.

---

## Gaps (contacts, second pass, 2026-11-07)

**Confirmed from the vendor's own page:** Kardex (Westbrook ME address and the form; no Utah dealer), Hoj Innovations (Salt Lake City), Pacific Integrated and Associated (Modula dealers), Universal Robots USA, MiR global email, Hartfiel (MiR in Utah), Robotiq phone, RealSense contact form and store, Airgas (Salt Lake City, corrected), Linde national lines, Labconco (Utah rep), Sentry Air, Plas-Labs, PiShop.us, PiKVM buy and support pages, Primera, Zebra forms, Uline (phone; no Utah site), Qorpak, Berlin Packaging, BYU Spectroscopic Facility.

**Still open (unverified), most important first:**
1. **Modula** email, phones, and the Utah dealer: modula.us and modula.com sit behind a Cloudflare challenge for both the runner and the Pi. Use Pacific Integrated (Arizona and California offices) or ask Modula's form.
2. **Kardex phone** (800-639-5805 is from 2013-2018 press releases) and whether **Hoj** is a Kardex dealer for the Shuttle VLM: ask both; Kardex names no Utah dealer.
3. **Stäubli** (403 everywhere): the Windsor, CA number comes from directories only; no Mountain West distributor found.
4. **Eaton** presales address and phone: eaton.com pages list none; the figures are from a search result of the Eaton-hosted product page.
5. **Parker Balston** (403 everywhere): the 800-343-4048 and `balstontechsupport@parker.com` come from a search report of Parker's own PDF; no Utah distributor.
6. **Norco** and **Linde** Utah branch phones; Utah-based **UR** and **MiR** integrators (partner locators are script-driven); Cross Company and Hartfiel Colorado addresses.
7. **MBraun**, **Terra Universal**, **Inert Technology**, **Vigor Tech USA**: no contact page was readable.
8. **Robotiq Utah distributor** and **Raspberry Pi** reseller page (403); Adafruit sales route; **VWR**; an **ESD rack supplier** is not yet named.
9. BYU's tax-exempt status for these purchases: BYU Financial Services describes a Utah charitable exemption certificate and a TC-73 seller contract (<https://finserve.byu.edu/sales-tax-faqs>); BYU Purchasing is to confirm.

**Added this pass:** Hoj Innovations (Utah Kardex-line integrator), Pacific Integrated and Associated (Modula), Plas-Labs and Qorpak/Berlin (named contacts), PiKVM's official resellers, Airgas dry-ice site correction, Uline's nearest warehouses.

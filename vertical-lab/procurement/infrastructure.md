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
- **Maker and model:** Kardex Shuttle XP 500, **two units**, trays **2450 × 864 mm**, **15 trays** in all (the model fills
  six slots in Shuttle 1 and the rest in Shuttle 2; `notes/tray_plan.md`), the unit **3950 mm** tall (under the 13 ft
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
- **Trays:** the POF order sheets give the 2450 × 864 mm Strong tray 500 kg, 236 kg-class lighter trays, and
  992 lb per tray with a 32.8 in floor-to-tray height on the AC's XP 500 quote (#372; `notes/kardex_opening.md`).
  Ratings fall as width grows (265 kg at 3050 mm). **Point-load ratings are not published.**
- **Utilities:** 208 V three-phase (#53); a used 2450 × 864 unit lists 400 V, 17 A (`notes/services.md`).
- **Interfaces:** Kardex's own software, Power Pick Global or the Shuttle's PLC interface, host connection over
  Ethernet; what an API looks like is **not published** (the Hoj reply in #53 said software integration is possible and
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
  (California) sells new VLMs. **Kardex and Modula** both ask to be the route for refurbished units.

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

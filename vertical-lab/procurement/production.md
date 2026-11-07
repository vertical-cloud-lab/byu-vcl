# Production workflow: vendors, contacts, specs and draft RFQ emails (vendors-c)

Part of the procurement pack for the vertical cloud lab (#303, PR #318). This file covers the atomizing, pressing, sieving, depowdering, printing, cutting, sample-prep, machining, DED, fabrication and feedstock items. The machine-readable index is [`production.csv`](production.csv); the lab's own answers (institution, site, utilities, timeline, budget, purchasing) are in [`lab_answers.md`](lab_answers.md). Only published business contact details are listed. Items marked **[to confirm]** are site or vendor facts we could not check. All pages were checked on 2026-11-07 UTC.

**No quotes have been requested yet; none of the emails below has been sent.** Every vendor is also asked for the preventive-maintenance schedule, consumables and spares with prices, and a service-contract price, because the lab models long-term maintenance (`vertical-lab/maintenance.py`).

## Common answers

Typical intake questions, answered once (vendor sections add specifics):

| Question | Answer |
|---|---|
| Application | An automated lab that atomizes, presses, sieves, prints, cuts, polishes and tests small alloy samples; a Kardex shuttle store with two MiR250 + UR10e units and tray instruments (`vertical-lab/README.md`). |
| Alloys and materials | Al-Si (AlSi10Mg, Al 4047), Cu-Ni (Cu-10Ni, Cu-30Ni), NAB bronze (C63000), 5N Al and OFE Cu (C10100) cups with Si and Ni powders. Reactive Al fines: NFPA 484 combustible-metal-dust practice. |
| Batch size | 4 charge cups a run, about 157-300 g of Al a run (about 0.3-1.1 kg a run with Cu); LPBF 55 mm kit builds of about 30 g, full 170 mm cylinder about 440 g (`notes/alloy_atomize.md`, `notes/timelapse.md`). |
| Throughput (year 1) | About 700 atomizer runs and 324 alloys fully tested (`out/timelapse_model.json`). |
| Automation | UR10e arms on MiR250 bases; PLC/I-O for door, start and status signals wanted on every machine. |
| Software | Python/PLC control; vendor software on a lab PC; remote API or contact closure preferred. |
| Utilities | Argon, N2, compressed air, chilled water, DI water, exhaust, 208 V 3-phase for the largest loads (FANUC 13 kVA). Site feeds: **[to confirm; see lab_answers.md]**. |
| Site, budget, timeline, purchasing | See [`lab_answers.md`](lab_answers.md) **[to confirm]**. |

## Index

| # | Item | Maker | Owned |
|---|---|---|---|
| 1 | AMAZEMET rePowder (atomizer) - OWNED: spares, 400 cm3 crucible, service | AMAZEMET | yes |
| 2 | Charge press: Specac Atlas Autotouch 15T + evacuable dies (Carver AutoPellet as fallback) | Specac |  |
| 3 | Sieving: Retsch AS 200 control + 8 in sieves (OWNED shaker/sieves: spares, extra sieves, service) | Retsch | yes |
| 4 | Sieve cleaning: ultrasonic bath for IPA (Elma, Branson and others) | Elma / Branson |  |
| 5 | Sieve cleaning: air knife and blower (EXAIR air knife; blower to be chosen) | EXAIR |  |
| 6 | Depowdering: Solukon SFM-AT200 | Solukon |  |
| 7 | LPBF: Aconity3D AconityMIDI / MIDI+ and the 55 mm build kit | Aconity3D |  |
| 8 | LPBF scale-up: EOS M 400-4 | EOS |  |
| 9 | Cutting: FANUC ROBOCUT wire EDM (alpha-C400iC) | FANUC (via Methods Machine Tools) |  |
| 10 | Sample prep: LECO PX500 polisher + MX400 mounting press | LECO |  |
| 11 | Sample prep (comparison): QATM QPOL 250 Bot automated polishing cell | QATM (Verder Scientific) |  |
| 12 | Sample prep: Buehler VibroMet 2 | Buehler (ITW) |  |
| 13 | Machining: Makera Carvera CNC | Makera |  |
| 14 | DED and repair: Meltio M450 and its robot cell | Meltio |  |
| 15 | DED: InssTek MX-Lab | InssTek |  |
| 16 | Fabrication: SnowX SnowPod (pre-release desktop LPBF) | SnowX |  |
| 17 | Fabrication: Formlabs Form 4, Form Wash, Form Cure | Formlabs |  |
| 18 | Fabrication: Opulo LumenPnP | Opulo |  |
| 19 | Fabrication: DDM Novastar SPR-45VA stencil printer | DDM Novastar |  |
| 20 | Fabrication: Bambu Lab H2D, A1 mini and A2L - OWNED (H2D, A1 mini): spares and consumables | Bambu Lab | yes |
| 21 | Feedstock: 5N Al and OFE Cu (C10100) bar, Si and Ni powders, AlSi10Mg powder | Goodfellow |  |

## 1. AMAZEMET rePowder (atomizer) - OWNED: spares, 400 cm3 crucible, service

### 1. What we would buy
**Maker / model:** AMAZEMET (Warsaw, Poland) rePowder ultrasonic-atomization induction module, which the lab already owns (built on an Indutherm induction furnace, per the lab's O&MM and facility guide; `lab_models/equipment.py` `REPOWDER`). **To buy:** (1) the 400 cm3 crucible upgrade (225 cm3 today; DAL #219 says the proposal counts on three runs per 2 kg lot in the 225 cm3 crucible, two in the 400 cm3); (2) spare crucible sets (graphite, BN-coated, with holder nut and lower seal), nozzle plates (0.3, 0.5, 1 mm and blank plates), sealing rods (BN) and adapters, thermocouples, seals; (3) a service contract; (4) the PLC/remote-control option for the SEALING ROD button and the lid latch if it exists (DAL #151). **Qty:** 1 machine owned; 2-3 spare crucible sets, 2 sealing rods and adapters, 2 nozzle plates of each size; 1 crucible 400 cm3 (or 2). **Role and place:** chapter 2 of the alloy route, a floor machine beside the Kardex VLM, loaded by two MiR250 + UR10e units (`notes/alloy_atomize.md`, `notes/crucible_automation.md`).

- **Model check (2026-11-07):** **current**. AMAZEMET still sells the rePowder, and in November 2025 added an AI model that runs the atomizer from a melt-pool camera feed, which bears on the remote-control question (DAL #151). AMAZEMET's TUM case study shows interchangeable 225 and 400 ml crucibles. No notice ends spares or service for owned machines, but no page lists parts or service terms and the rePowder page did not load on the runner, so ask directly. (https://www.metal-am.com/amazemet-adds-ai-automation-to-repowder-atomisation/)

### 2. Published specs that matter for integration
Envelope about 1000 x 800 x 1600 mm (`REPOWDER`, from the O&MM p. 42 and facility guide p. 7). Power: 400 V 3-phase and 230 V on 32 A plugs, the optimizer up to about 60 A (the install call; `notes/services.md`). Argon at about 0.1-0.2 bar melt/graining pressures with a turbo stage (DAL #219: 0.1 bar melt, 0.19 bar graining, 1.5 bar turbo); a chiller on its own 230 V plug. Interfaces: the SEALING ROD button lifts the rod (PLC signal only if AMAZEMET allows), a lid latch and a lid with a knob, a thermocouple port, thread-and-nut crucible holder (`notes/crucible_automation.md`). No published remote-start/API on the pages we saw; ask.

### 3. Contact

- **Email:** sales@amazemet.com; office@amazemet.com (verified: https://amazemet.com/contact/, 2026-11-07)
- **Phone:** +48 573 481 303 (verified: https://amazemet.com/contact/, 2026-11-07)
- **Web / form:** https://amazemet.com/contact/ (form goes to the sales and application team)
- **Regional rep / distributor:** None published for the US. The contact page links https://www.amazemet.com/agents-and-distributors/ (fetched 2026-11-07); it names no agent or distributor, says to use the contact form to join the network, and gives registered partners a login portal. AXT (Australia) is not on that page. Ask sales@amazemet.com whether a US agent exists (unverified: none published)
- **Contact status (2026-11-07):** verified: email, phone, form, agents page (no US agent published).
- **Office / hours:** Mon-Fri 08:00-16:00 Warsaw time; registered office al. Jana Pawla II 27, 00-867 Warszawa; R&D centre Trasa Lubelska 46, 05-462 Majdan
- **Academic / owner note:** Since the machine is owned, send under the existing order/installation reference **[to confirm: order no., serial]**.
- **Status:** owned by the lab; the contact is for spares, consumables and service.

### 4. Our open questions for them

- Price and lead time of the 400 cm3 crucible, and whether the same holder, nut, sealing rod and nozzle plate fit (DAL #219).
- Thread specification of the crucible-to-holder and nut-to-shank joints, snug and breaking torque, and whether a keyed crucible or captive nut is possible (`notes/crucible_automation.md` item 5).
- Price of a crucible, nozzle plate, sealing rod, brass adapter and thermocouple; recommended spare set.
- Does the SEALING ROD button accept a PLC signal? Is there a remote start/stop, status or data interface (DAL #151)? Can the lid latch be sensed or actuated?
- Can the adapter be pinned on after loading the cups (`notes/alloy_atomize.md`)?
- Which routine maintenance (graphite parts, insulation, seals, vacuum/argon lines, ultrasonic converter and sonotrode wear) and at what interval; sonotrode lifetime and price.
- Service contract and remote support terms for a customer in the US; spare-part stocking in the US.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al 5N cups with Si/Ni/Cu additions, Al-Si (AlSi10Mg, Al 4047), Cu-10Ni, Cu-30Ni, NAB (C63000) bronze; reactive Al fines under 63 um (NFPA 484-type hazard; DAL sieve note). Batch: 4 charged cups a run, about 157-300 g of Al a run (`notes/alloy_atomize.md`); the first Cu run melted 1,080 g of 630 bronze, about 97% became powder, about 0.7 kg usable (DAL #219). Throughput: about 700 atomizer runs a year at up to three weekday runs, crucible changed by a person on a day shift (`out/timelapse_model.json`). Automation: two MiR250 + UR10e units open the lid, load cups and take the container. Utilities: argon, 400 V 3-phase **[to confirm site feed]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** sales@amazemet.com  
**Cc:** office@amazemet.com
**Subject:** rePowder (owned): 400 cm3 crucible quote, spare parts list and service contract

> Hello,
>
> We own an AMAZEMET rePowder and want a budgetary quote for the 400 cm3 crucible upgrade, a spare set of wear parts, and an annual service contract. We are automating the machine with two UR10e arms on mobile bases.
>
> Facts:
> - Machine: rePowder, 225 cm3 crucible today **[to confirm: serial no., order ref.]**.
> - Use: Al-Si and Cu-Ni/NAB powders, 4 cups a run, up to 3 runs a weekday, about 700 runs a year.
> - Site: Brigham Young University, Utah **[to confirm building, 400 V 3-phase feed, argon supply]**.
>
> Questions:
> 1. Price and lead time of the 400 cm3 crucible, and whether the same holder, nut, sealing rod and nozzle plate fit (DAL #219).
> 2. Thread specification of the crucible-to-holder and nut-to-shank joints, snug and breaking torque, and whether a keyed crucible or captive nut is possible.
> 3. Price of a crucible, nozzle plate, sealing rod, brass adapter and thermocouple; recommended spare set.
> 4. Does the SEALING ROD button accept a PLC signal? Is there a remote start/stop, status or data interface (DAL #151)? Can the lid latch be sensed or actuated?
> 5. Can the adapter be pinned on after loading the cups?
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://amazemet.com/contact/ (WebFetch/WebSearch from the runner)
- https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-303-vendors-rfq/vertical-lab/notes (WebFetch/WebSearch from the runner)
- https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219 (WebFetch/WebSearch from the runner)
- https://www.metal-am.com/amazemet-adds-ai-automation-to-repowder-atomisation/ (2026-11-07, search snippet)
- https://www.amazemet.com/repowder/ (2026-11-07, search snippet)
- https://www.amazemet.com/technical-university-of-munich-amazemet-case-study/ (2026-11-07, search snippet)

## 2. Charge press: Specac Atlas Autotouch 15T + evacuable dies (Carver AutoPellet as fallback)

### 1. What we would buy
**Maker / model:** Specac Atlas Autotouch 15T, part GS2581X (230 V; 110 V versions exist), with a two-stage rotary-vane pump, isolation valve V1, vent valve V2 with needle valve, Pirani gauge; Atlas evacuable dies (13 mm GS03000; 32/40 mm with evacuation port, GS26101/GS26102) **[confirm which die suits the 1-1/4 in F1 cup]**. Lab-made: F1 die, catch ring, punch, ejector pin, shuttle (`notes/vacuum_press.md`). **Qty:** 1 press, 1 pump set, 2 evacuable dies. **Fallback:** Carver AutoPellet RP (25/40 t, touchscreen recipes incl. ejection force, vacuum port on the die), qty 1. **Role and place:** chapter 1 of the alloy route, tray B beside the OT-2/doser, pressing 4 charge cups to about 3.2 t (DAL #140, #156).

- **Model check (2026-11-07):** **current**. Specac's product page still lists the Atlas Autotouch 15T as GS2581X (a 110 V 60 Hz US version; 425 x 405 x 640 mm, 95 kg; up to 6 stored programs, no remote interface listed) and the evacuable dies GS03000, GS26101 and GS26102. Carver's site promotes the redesigned AutoPellet RP series (3887.RP.L 25 t and 4387.RP.L 40 t, 5 in platen, a vacuum connection to the die); its product page did not load on the runner. (https://specac.com/product/autotouch-press-high-throughput-xrf-press/)

### 2. Published specs that matter for integration
Specac: 2-15 t in 0.2 t steps, up to 10 programme steps ('pump up to', 'maintain', 'release'), one Start press runs a programme; sample space up to 220 mm diameter x 155 mm; ram stroke 24 mm; about 95 kg (Avantor listing for SPCCGS25810, 230 V); full outline not found. Mains 230 V (or 110 V version); a dry-argon line goes to V2 (ours). Interfaces: front-panel Start; remote-start input not published. Carver AutoPellet: 25/40 t, about 375 lb (a Spectra datasheet), touchscreen recipe (clamp force, dwell, decompression rate, ejection force), vacuum-line provision, no dimension sheet found.

### 3. Contact

- **Email:** uscs@specac.com (US customer service) and sales@specac.co.uk (UK sales) (verified: https://specac.com/contact-us/, 2026-11-07). The first pass listed sales@specac.com; it is NOT on Specac's contact or distributors pages (unverified: removed, do not use); customer.services@specac.co.uk is the global address
- **Phone:** +1 914-747-7202 (USA); +44 (0) 1689 873 134 (UK) (verified: https://specac.com/contact-us/, 2026-11-07); UK sales line on the distributors page +44 (0) 1689 892902
- **Web / form:** https://specac.com/contact-us/ (Get a Quote); 15-minute applications call https://specac.com/book-application-appointment/ (booking link not re-fetched, unverified); distributors https://specac.com/our-distributors/
- **Regional rep / distributor:** Specac lists no Utah or Mountain West distributor (verified: https://specac.com/our-distributors/, 2026-11-07). US distributors listed there (no email or phone on the page): REFLEX Analytical (NJ, https://www.reflexusa.com/), Premier Lab Supply (FL, https://www.premierlabsupply.com/contact/), Unitech USA (FL, https://www.unitechusa.com/), Firebird Optics (NY, https://www.firebirdoptics.com/); Specac says to order direct if none is local. Carver (Wabash IN, https://www.carverpress.com/contact, 2026-11-07): main +1 260-563-7577 (1 parts, 2 equipment presses), carverpress@acscorporate.com, regional sales manager Donovan Sparks +1 260-233-6881 dsparks@acscorporate.com, sales support Kendra Shepler +1 260-233-6914 kshepler@acscorporate.com, technical service +1 260-233-6900 (Tom Huston +1 260-233-6890 thuston@acscorporate.com), wabashservice@acscorporate.com (all verified)
- **Contact status (2026-11-07):** partial: uscs@, phone, distributors and Carver verified; sales@specac.com removed as unverified.
- **Office / hours:** Specac US office: 333 N Bedford Rd, Suite 129, Mt Kisco NY 10549
- **Academic / owner note:** Applications consultation is free; ask for an academic quote.

### 4. Our open questions for them

- Does the Autotouch accept a remote-start or contact-closure input so a robot or PLC can start a programme, or must the arm press Start (`notes/vacuum_press.md`)?
- Force needed to push a pressed cup out of the F1 die: is there an ejection stroke or must the ejector be lab-made, and what stroke does the ram have for it?
- Can a programme hold a vacuum (pump-down, hold, vent with argon) through V1/V2 under the press's own control or is the pump separate?
- Dimensions and mass of the 15T as shipped, and of the 110 V version; is a bench-mounted stand required?
- Is the 15T rated for repeated 3.2 t cycles for hundreds of cups a year; duty cycle, oil change interval, seal kit prices?
- Carver: can the AutoPellet run unattended with an external eject, and does its vacuum die take a 1-1/4 in cup form?
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: 5N Al and OFE Cu (C10100) cup stock, plus Si and Ni powders pressed into a bore in the cup, plug pressed on top; powder is reactive, so vacuum or argon die (DAL #140: press chosen to avoid explosions). Batch: 4 cups a run, about 8.7 g of powder a cup for Al-Si, 12.97 g Ni for the Cu-10Ni set, plug press fit about 1.3-1.6 t (DAL #222). Target 3.2 t. Throughput: about 700 runs a year x 4 cups, so about 2,800 pressings a year. Automation: the arm loads the shuttle, the press runs a stored programme. Utilities: 230 V single phase, argon (dry) to V2, a vacuum pump exhaust.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** uscs@specac.com (US customer service; sales@specac.com is unverified), cc sales@specac.co.uk  
**Cc:** uscs@specac.com
**Subject:** Budgetary quote: Atlas Autotouch 15T (GS2581X) with evacuable dies, and robot-start question

> Hello,
>
> We want a budgetary quote for one Atlas Autotouch 15T with a rotary-vane pump and two evacuable dies, and two answers before we order: does it take a remote start, and what force does it take to push a pressed cup out of the die?
>
> Facts:
> - Use: cold-compacting Ni/Si powder into a 1-1/4 in Al or Cu cup under vacuum, about 3.2 t, 4 cups per cycle, about 2,800 cups a year.
> - A UR10e arm will load the press; ideally a contact-closure Start.
> - Site: Brigham Young University, Utah **[to confirm]**; 230 V or 110 V **[to confirm]**.
>
> Questions:
> 1. Does the Autotouch accept a remote-start or contact-closure input so a robot or PLC can start a programme, or must the arm press Start?
> 2. Force needed to push a pressed cup out of the F1 die: is there an ejection stroke or must the ejector be lab-made, and what stroke does the ram have for it?
> 3. Can a programme hold a vacuum (pump-down, hold, vent with argon) through V1/V2 under the press's own control or is the pump separate?
> 4. Dimensions and mass of the 15T as shipped, and of the 110 V version; is a bench-mounted stand required?
> 5. Is the 15T rated for repeated 3.2 t cycles for hundreds of cups a year; duty cycle, oil change interval, seal kit prices?
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://specac.com/contact-us/ (WebFetch/WebSearch from the runner)
- https://specac.com/our-distributors/ (WebFetch/WebSearch from the runner)
- https://specac.com/locations/ (fetched via the stream-cam Pi)
- https://www.carverpress.com/contact (fetched via the stream-cam Pi)
- https://specac.com/product/autotouch-press-high-throughput-xrf-press/ (WebFetch/WebSearch from the runner)
- https://specac.com/product/autotouch-press-high-throughput-xrf-press/ (2026-11-07, runner)
- https://carverpress.com/presses-accessories/bench-top-auto-presses/pellet/ (2026-11-07, search snippet)
- https://www.labcompare.com/5207-Laboratory-Press/25497138-AutoPellet-RP-Bench-Top-Lab-Presses/ (2026-11-07, search snippet)

## 3. Sieving: Retsch AS 200 control + 8 in sieves (OWNED shaker/sieves: spares, extra sieves, service)

### 1. What we would buy
**Maker / model:** Retsch AS 200 control vibratory sieve shaker (electromagnetic drive), with the clamping lid for 8 in sieves; 8 in stainless sieves No. 60 (250 um), No. 100, 140, 230 (63 um), 325 (45 um) and pan (No. 60, No. 230 and pan bought; No. 100, 140, 325 on order, DAL PR #175 `docs/sieve-order.md`). **To buy:** a second shaker or spares (clamping device, timer/amplitude board, springs), spare sieve set so a stack can wash while another runs, IQ/OQ documentation. **Qty:** 1 shaker owned; 1 spare stack; 1 spare clamping lid. **Role and place:** chapter 3, the sieve bench, stack 567 mm tall on the shaker's 212 mm base, under Kardex's 727.5 mm limit (`notes/instruments_char.md`).

- **Model check (2026-11-07):** **current**. Retsch still sells the AS 200 control (100-240 V; 417 x 212 x 384 mm, about 35 kg; USB and EasySieve) and offers technical support and IQ/OQ documents for it, so service is still offered for the owned shaker. Its 2026 data sheet still lists clamping lids, clamping devices and wear parts (clamping nuts 32.142.0001, quick-clamping elements, their O-ring, the sieve-plate rubber disc), so spares are still offered too. (https://www.retsch.com/products/sieving/sieve-shakers/as-200-control/)

### 2. Published specs that matter for integration
AS 200 control: 417 W x 384 D x 212 H mm (`instruments_char.sieve()`); sieves 100 mm to 8 in (203 mm); measuring range 20 um to 25 mm; 3 kg load; amplitude 0-3 mm digital; interval and timer; amplitude held constant by a controller; dry and wet sieving; IQ/OQ available. Mains 100-240 V **[to confirm model voltage]**. Interfaces: front panel; Retsch's EasySieve software option needs a PC link **[to confirm]**; no remote-start for a robot published. Clamping lid has two knobs (the arm turns them, `notes/instruments_char.md`).

### 3. Contact

- **Email:** info-us@verder-scientific.com (verified: https://www.verder-scientific.com/us, 2026-11-07)
- **Phone:** +1 866-473-8724 (Verder Scientific Inc., Newtown PA) (verified: https://www.verder-scientific.com/us, 2026-11-07)
- **Web / form:** https://www.retsch.com/contact-services/ (form; US offices via https://www.verder-scientific.com/contact-services); US request page https://www.verder-scientific.com/us (Consultation, Service Inquiry)
- **Regional rep / distributor:** Verder Scientific Inc. is the US entity; its page names Kyle James, Team Leader Retsch USA (verified: https://www.verder-scientific.com/us, 2026-11-07). US distributors list the AS 200 control: Fisher Scientific (15582515), Thomas Scientific (8324A62), Avantor/VWR (unverified: catalogue numbers from the first pass); no Utah rep found. Sieves: Fisher 8 in No. 60 stainless $369 (DAL #146 comment); Gilson (globalgilson.com)
- **Contact status (2026-11-07):** verified: info-us@ and phone now confirmed on the Verder US page (no longer from a search result).
- **Office / hours:** Verder Scientific Inc., 11 Penns Trail, Newtown PA 18940
- **Academic / owner note:** Retsch and QATM are Verder Scientific brands, so one US office handles both; ask for the application lab for Al powder sieving.
- **Status:** owned by the lab; the contact is for spares, consumables and service.

### 4. Our open questions for them

- Is there a remote-start or external-trigger option (contact closure, Modbus, EasySieve over USB/Ethernet) so the robot cell can start and read a run?
- Is the AS 200 control rated for combustible metal dust (Al under 63 um)? ATEX/Class II Div 2 options, grounding kit, a sealed stack option, inert-gas sieving (argon) with a lid seal?
- Which sieve-cleaning method does Retsch recommend between alloys (ultrasonic IPA, DAL #234), and the mesh life/pricing of the 325 cloth?
- Replacement parts and typical wear intervals (springs, drive, clamping device), and annual service price.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: atomized Al-Si, Cu-Ni and NAB powders, reactive Al fines. Cuts: No. 60 scalp, No. 100/140/230/325 and pan; 20-63 um for LPBF, 45-105 and 100-200 um for DED (DAL PR #220). Batch: whole run's container, about 0.3-1.1 kg a run. Throughput: about 700 runs a year, so about 700 sieve stacks. Automation: arm turns the lid knobs, a pneumatic tipper turns each sieve over a funnel. Utilities: 100-240 V, a ground bar and downdraft extraction ours.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** info-us@verder-scientific.com
**Subject:** Budgetary quote: Retsch AS 200 control spare/second shaker, 8 in sieves, and a robot-start question

> Hello,
>
> We use an AS 200 control with 8 in sieves for reactive Al and Cu-alloy powders and want a budgetary quote for a second unit or spares, a spare sieve set, and an annual service plan.
>
> Facts:
> - Powder: Al-Si, Cu-Ni, NAB; Al fines under 63 um are combustible, so we ground the stack and extract.
> - A UR10e arm loads and unloads the stack, about 700 stacks a year.
> - Question: any contact-closure start or serial/Ethernet control on the AS 200 control?
>
> Questions:
> 1. Is there a remote-start or external-trigger option (contact closure, Modbus, EasySieve over USB/Ethernet) so the robot cell can start and read a run?
> 2. Is the AS 200 control rated for combustible metal dust (Al under 63 um)? ATEX/Class II Div 2 options, grounding kit, a sealed stack option, inert-gas sieving (argon) with a lid seal?
> 3. Which sieve-cleaning method does Retsch recommend between alloys (ultrasonic IPA, DAL #234), and the mesh life/pricing of the 325 cloth?
> 4. Replacement parts and typical wear intervals (springs, drive, clamping device), and annual service price.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.verder-scientific.com/contact-services (fetched via the stream-cam Pi)
- https://www.retsch.com/contact-services/ (fetched via the stream-cam Pi)
- https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/146 (WebFetch/WebSearch from the runner)
- https://www.retsch.com/products/sieving/sieve-shakers/as-200-control/ (2026-11-07, runner)
- https://www.retsch.com/files/452772/product-data-sheet-as-200-control.pdf (2026-11-07, search snippet)

## 4. Sieve cleaning: ultrasonic bath for IPA (Elma, Branson and others)

### 1. What we would buy
**Maker / model:** an ultrasonic bath with a water jacket, sonicating a closed vessel of IPA indirectly (so IPA is not heated or ignited in the tank). Candidates: Elma (Elmasonic P/S series, Elma Schmidbauer GmbH) and Branson (Emerson Bransonic CPX series, e.g. CPX2800/CPX1800H); also Crest, Cole-Parmer. **[to confirm size]**: a tank that takes a 8 in x 2 in (203 x 50 mm) sieve in a closed jar. **Qty:** 1 (+1 spare vessel). **Role and place:** the sieve wash module on a 450 mm bench extension left of the tipper (`notes/instruments_char.md`); an Advantech manual asks at most 150 W, room temperature, short runs, sieve suspended off the tank floor.

- **Model check (2026-11-07):** **current**. Elma's page lists the Elmasonic P in seven sizes; the P 120H (inside 275 x 215 x 195 mm), P 180H and P 300H are wide enough for a 203 mm sieve, at 220-240 V on that page, so ask for 115 V. Branson's lab page still lists the Bransonic CPX and CPXH baths and the 120 V CPX2800H is still sold, but distributors mark the 230 V "-E" versions and some CPX/CPXH 5800 and 8800 part numbers discontinued, with replacement links. (https://www.elma-ultrasonic.com/en/elmasonic-p)

### 2. Published specs that matter for integration
Elma: GmbH in Singen, Germany, tanks of 1-1000 L, 37/80 kHz, heating and sweep options. Branson CPX: 1.5-40 L tanks, 40 kHz, digital timer and heater, 120/230 V. Utilities: mains, drain, DI water for the jacket; explosion hazard from IPA vapour, so closed vessel only. Interface: front panel; relay or external start varies by model **[to confirm]**.

### 3. Contact

- **Email:** sales@elma-ultrasonic.com (listed for Chemistry & Process Consulting, Elmaclean) (verified: https://www.elma-ultrasonic.com/en/contact, 2026-11-07); Branson: info@bransonultrasonics.com appears in a manual only (unverified)
- **Phone:** Elma: none published on its contact page (verified: https://www.elma-ultrasonic.com/en/contact, 2026-11-07). Branson: +1 203-796-0400 is a directory number, not on Branson's own site, and a 2026 report says Branson moved its HQ from Brookfield CT to Farmington Hills MI (unverified: use https://www.branson.emerson.com/en , whose Contact Us link and Emerson's +1 888 889 9170 on https://www.emerson.com/en-us/contact-us are the only own-site routes)
- **Web / form:** https://www.elma-ultrasonic.com/en/contact ; retailer list https://www.elma-ultrasonic.com/en/haendler ; Branson: https://www.branson.emerson.com/en/laboratory-equipment-tabletop-cleaners (the old emerson.com/en-us/automation/branson URL redirects here; verified 2026-11-07)
- **Regional rep / distributor:** Elma lists no US distributor on its contact page; its retailer page https://www.elma-ultrasonic.com/en/haendler loads a country picker we could not read (unverified). Branson CPX through distributors, e.g. Fiber Optic Center sales@focenter.com +1 800-473-4237 (unverified: focenter.com returned 403 to the runner and the Pi)
- **Contact status (2026-11-07):** partial: Elma email verified; Branson phone, Fiber Optic Center and US/Utah distributor unverified.
- **Academic / owner note:** Ask for lab pricing.

### 4. Our open questions for them

- Can the tank run indirectly (a sealed vessel of IPA in a water jacket) without the vessel resonating or the IPA heating; the recommended power density?
- Is there an external start/stop or a relay for a robot cell? Can it be fitted under a hood with an exhaust duct?
- Is a vessel holder and jacket-water level control available as a standard accessory?
- Transducer lifetime, degassing, and the PM schedule; service contract price.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: stainless 8 in sieves with loaded fine powders (No. 325 cloth), IPA as the fluid. Batch: one sieve at a time; between alloys. Throughput: about 700 cleans a year. Automation: a lift lowers the basket ring into the bath. Utilities: mains, DI water **[to confirm]**, exhaust.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** sales@elma-ultrasonic.com
**Subject:** Quote: ultrasonic bath for indirect IPA cleaning of 8 in sieves

> Hello,
>
> We need a budgetary quote for one ultrasonic bath that sonicates a closed IPA vessel indirectly through a water jacket, holding an 8 in (203 mm) sieve.
>
> Facts:
> - Duty: about 700 cleans a year, one sieve at a time.
> - Hazard: IPA, so no direct sonication and no heating of IPA.
> - Needed: external start/stop for a robot cell; US 120 V **[to confirm]**; US distributor.
>
> Questions:
> 1. Can the tank run indirectly (a sealed vessel of IPA in a water jacket) without the vessel resonating or the IPA heating; the recommended power density?
> 2. Is there an external start/stop or a relay for a robot cell? Can it be fitted under a hood with an exhaust duct?
> 3. Is a vessel holder and jacket-water level control available as a standard accessory?
> 4. Transducer lifetime, degassing, and the PM schedule; service contract price.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.elma-ultrasonic.com/en/contact (fetched via the stream-cam Pi)
- https://www.emerson.com/en-us/automation/branson (fetched via the stream-cam Pi)
- https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/234 (WebFetch/WebSearch from the runner)
- https://www.elma-ultrasonic.com/en/elmasonic-p (2026-11-07, runner)
- https://www.branson.emerson.com/en/laboratory-equipment-tabletop-cleaners (2026-11-07, search snippet)
- https://www.itm.com/product/branson-cpx-952-238r-cpxh-2800-ultrasonic-bath-digital-timer-with-heat-0-7-gal-2-8-l (2026-11-07, search snippet)
- https://www.globaltestsupply.com/product/branson-cpx-952-837r-ultrasonic-bath-m8800h-e (2026-11-07, search snippet)

## 5. Sieve cleaning: air knife and blower (EXAIR air knife; blower to be chosen)

### 1. What we would buy
**Maker / model:** EXAIR Super Air Knife (aluminium, 6-12 in) on the lab's compressed air, for blowing powder off the cloth after the bath; a blower alternative (regenerative or centrifugal, **[to confirm maker]**) if house air is unavailable. **Qty:** 1 knife, 1 regulator/shut-off valve. **Role and place:** sieve wash module, inside the downdraft hood (`notes/instruments_char.md`).

- **Model check (2026-11-07):** **current**. EXAIR still lists the aluminium Super Air Knife in 6 in and 12 in lengths (models 110006 and 110012; kit 110212). The blower maker is not chosen, so there is no model to check for it. (https://www.exair.com/110006.html)

### 2. Published specs that matter for integration
Air knife: compressed air at about 80 psig, 1/4-1/2 in NPT, amplification about 40:1, a 6 in knife uses roughly 15 SCFM at 80 psi **[to confirm from the data sheet]**. Needs oil-free filtered air; a solenoid valve for PLC control.

### 3. Contact

- **Email:** techelp@exair.com (technical help); orders@exair.com (US and Canada orders) (verified: https://www.exair.com/contact-us/, 2026-11-07); application engineers (named on the page): Jason Kirby jasonkirby@exair.com, Jordan Shouse jordanshouse@exair.com, Brian Farno brianfarno@exair.com, Russ Bowman russbowman@exair.com
- **Phone:** +1 800-903-9247 (US and Canada); +1 513-671-3322 (verified: https://www.exair.com/contact-us/, 2026-11-07); the page warns of phone-system trouble and asks for email or chat
- **Web / form:** https://www.exair.com/contact-us/ (no 'Product Specialist' is named on the page: use Consult an Engineer / the application engineers)
- **Regional rep / distributor:** EXAIR sells direct; no distributor or Utah rep is listed on its contact page, and https://www.exair.com/storelocator is international (verified 2026-11-07); no Utah rep (unverified)
- **Contact status (2026-11-07):** verified: email, phone, application engineers; no Utah rep published. Blower alternative (no vendor yet): Gast Manufacturing (Benton Harbor MI) +1 269-926-6171, tel link on https://www.gastmfg.com/contact-us (partial: phone only; its regenerative-blower line not confirmed).
- **Office / hours:** 11510 Goldcoast Drive, Cincinnati OH 45249

### 4. Our open questions for them

- Right knife length and air pressure for blowing sub-45 um powder out of a 325 mesh cloth without damaging it; is a shim thinner than standard available?
- Compressed-air consumption and a recommended filter/regulator/solenoid kit for PLC control.
- PM and spare parts; any service plan.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: fine metal powder residues on stainless cloth. Batch: one sieve per cycle. Throughput: about 700 a year. Automation: valve on a PLC. Utilities: filtered air 80 psig **[to confirm site supply]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** techelp@exair.com
**Subject:** Air knife selection for blowing fine metal powder off 8 in test sieves

> Hello,
>
> We want to select and quote a Super Air Knife for blowing powder off 8 in test sieves (325 mesh stainless cloth) inside a downdraft hood.
>
> Facts:
> - Sieve: 203 mm diameter, 45 um cloth.
> - Control: solenoid valve on a PLC.
> - Air: house air **[to confirm pressure and flow]**.
>
> Questions:
> 1. Right knife length and air pressure for blowing sub-45 um powder out of a 325 mesh cloth without damaging it; is a shim thinner than standard available?
> 2. Compressed-air consumption and a recommended filter/regulator/solenoid kit for PLC control.
> 3. PM and spare parts; any service plan.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://exair.com/about-us.html (WebFetch/WebSearch from the runner)
- https://www.exair.com/110006.html (2026-11-07, search snippet)
- https://exair.com/catalog/category/view/id/471 (2026-11-07, search snippet)

## 6. Depowdering: Solukon SFM-AT200

### 1. What we would buy
**Maker / model:** Solukon Maschinenbau GmbH SFM-AT200 (automatic unpacking and depowdering station, programmable rotation about one axis, variable-frequency vibration, inert gas). **Qty:** 1, with the inert-gas option (argon) and the ultrasonic option if offered **[to confirm]**. **Role and place:** the depowdering box between the printer and the 68FM-100 on the floor line; the arm sets a build plate in it (`notes/alloy_workflow.md`).

- **Model check (2026-11-07):** **current**. Solukon's page still offers the SFM-AT200 (parts up to 300 x 300 x 230 mm; machine 1,160 x 985 x 1,139 mm, 150 kg; 400 V, 16 A, 0.4 kW; inert-gas infusion option); the new SFM-AT850 shown at Formnext 2026 is a large-part machine, not a replacement. The page gives both 60 kg and 100 kg as the part-weight limit; ask which holds. (https://www.solukon.de/en/sfm-at200)

### 2. Published specs that matter for integration
Parts up to 300 x 300 x 230 mm and 60 kg (TCT Magazine); no outer size published (the real unit may need about a metre more); inert gas nitrogen or argon; mains and compressed air **[to confirm from data sheet]**; programmable amplitudes. Interfaces: touchscreen; door sliding up; remote start and clamp form unknown; ask.

### 3. Contact

- **Email:** kontakt@solukon.de (verified: https://www.solukon.de/en/contact/, 2026-11-07)
- **Phone:** +49 821 44098-0 (verified: https://www.solukon.de/en/contact/, 2026-11-07)
- **Web / form:** https://www.solukon.de/en/contact/ (inquiry, quote and service forms); product https://www.solukon.de/en/products/sfm-at200/
- **Regional rep / distributor:** Utah is in NB Additive LLC's territory (verified: https://www.solukon.de/en/distribution-partners/, 2026-11-07) (listed there: Colorado, Idaho, Illinois, Iowa, Kansas, Louisiana, Montana, Missouri, Minnesota, Nebraska, New Mexico, North Dakota, Oklahoma, South Dakota, Texas, Utah, Wyoming). NB Additive: Info@nbadditive.com, +1 314-202-0521, 7336 Hidden Oaks Drive, North Richland Hills TX 76182 (verified: https://www.nbadditive.com/, 2026-11-07) (its page lists no states and does not mention Solukon). Other US partners on the Solukon page: DMARK Corporation (AZ, CA, NV, OR, WA), Phillips Corp (eastern states)
- **Contact status (2026-11-07):** verified: Solukon email/phone, NB Additive for Utah, NB email/phone.
- **Office / hours:** Solukon Maschinenbau GmbH, Aulzhausener Str. 14, 86165 Augsburg

### 4. Our open questions for them

- How does the SFM-AT200 clamp a build plate (what plate interface, size and thickness, and can the arm load it through the door), and can the clamp be keyed for a 170 mm round Aconity plate?
- Remote start, door actuation and status over PLC (digital I/O, fieldbus)?
- Cycle time for a 170 mm x 100 mm bar plate with Al-Si powder; powder recovery into a sealed container and an Al-safe (NFPA 484) specification.
- Outer dimensions, weight, mains, air and inert gas flow; the foundation requirement.
- Is a smaller or custom variant available for 55 mm kit plates?
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si, Cu-Ni, NAB bars printed on 170 mm plates (or 55 mm kit); reactive Al. Batch: one plate per build, about 440 g full cylinder, about 30 g in the 55 mm kit (DAL #138). Throughput: about 324 alloys a year; plates for builds only a fraction. Automation: a UR10e loads the plate. Utilities: argon, mains, compressed air **[to confirm]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** Info@nbadditive.com (Solukon's Utah partner), cc kontakt@solukon.de  
**Cc:** kontakt@solukon.de
**Subject:** Quote: Solukon SFM-AT200 for Al-Si and Cu alloy plates, robot loading

> Hello,
>
> We want a budgetary quote for one SFM-AT200 with inert gas, and three answers: how it clamps a plate, whether a robot can load it, and its remote start.
>
> Facts:
> - Parts: bars on 170 mm round plates, and a 55 mm reduction kit; Al-Si, Cu-Ni, NAB.
> - Automation: a UR10e sets the plate in the door.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. How does the SFM-AT200 clamp a build plate (what plate interface, size and thickness, and can the arm load it through the door), and can the clamp be keyed for a 170 mm round Aconity plate?
> 2. Remote start, door actuation and status over PLC (digital I/O, fieldbus)?
> 3. Cycle time for a 170 mm x 100 mm bar plate with Al-Si powder; powder recovery into a sealed container and an Al-safe (NFPA 484) specification.
> 4. Outer dimensions, weight, mains, air and inert gas flow; the foundation requirement.
> 5. Is a smaller or custom variant available for 55 mm kit plates?
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.solukon.de/contact/ (WebFetch/WebSearch from the runner)
- https://www.solukon.de/en/distribution-partners/ (WebFetch/WebSearch from the runner)
- https://www.nbadditive.com/ (fetched via the stream-cam Pi)
- https://www.solukon.de/en/products/sfm-at200/ (WebFetch/WebSearch from the runner)
- https://www.solukon.de/en/sfm-at200 (2026-11-07, runner)

## 7. LPBF: Aconity3D AconityMIDI / MIDI+ and the 55 mm build kit

### 1. What we would buy
**Maker / model:** Aconity3D GmbH AconityMIDI (or MIDI+), 170 mm diameter x 200 mm build space, with the optional diameter-55 mm build-reduction kit (about 20 cm3, about 30 g powder; AMAZEMET prints its atomized powders on one), inert glovebox for powder handling. **Qty:** 1 machine, 1 kit. **Role and place:** chapter 4 print, a floor machine at x = 3250 beside the VLM; the arm passes a jar through a 280 mm high door to the supply cylinder (`notes/alloy_print.md`).

- **Model check (2026-11-07):** **current**. Aconity3D's site still lists both the AconityMIDI and the AconityMIDI+; the MIDI+ is the newer, larger sibling (up to four lasers in the QUATTRO setup and a larger build plate), not a replacement. The product pages' specs did not come through on the runner, so whether the 55 mm kit fits both is still to confirm. (https://aconity3d.com/products/aconity-midi-plus/)

### 2. Published specs that matter for integration
Footprint about 2450 x 1500 x 2320 mm (model), older design 2170 x 1590 x 2340; 1450 kg; build 170 x 200 mm; the MIDI's door lifts to about 165 degrees; the chamber opening is about 280 mm tall and the supply cylinder 540 mm behind it. Argon; power not published (`notes/services.md`: 'Aconity MIDI, Inert glovebox: not found'). Interfaces: AconityStudio software; door, plate and cylinder actuation for a robot unknown; ask.

### 3. Contact

- **Email:** info@aconity3d.com (verified: https://www.aconity3d.com/, 2026-11-07); support: https://support.aconity3d.com (not re-fetched, unverified)
- **Phone:** +49 2406 92749-0 (fax -99) (verified: https://aconity3d.com/, 2026-11-07)
- **Web / form:** https://aconity3d.com/products/aconity-midi
- **Regional rep / distributor:** AconityUS, Inc. (US arm, announced 2018 at UTEP in El Paso): no US contact on Aconity's own site (https://aconity3d.com/ lists only info@ and the German phone; /contact is 404) (unverified: no US contact). Ask info@aconity3d.com for the North America sales rep. Utah and Amazemet already run MIDIs
- **Contact status (2026-11-07):** partial: info@ and phone verified; US rep unverified (none published).
- **Office / hours:** Aconity3D GmbH, An den Glaswerken 2, 52134 Herzogenrath, Germany
- **Academic / owner note:** Utah's MIDI is a collaborator's (DAL PR #169); confirm whether to use it instead of buying.

### 4. Our open questions for them

- How does the MIDI's door open (hinge, lift, powered or manual) and can a robot or an actuator open and close it? Door clearance for a 2F-85 gripper, and does it release an interlock when the arm is inside?
- Is the supply cylinder fill reachable from a jar-pour (440 g full cylinder), and how does a 55 mm kit change the supply (30 g)?
- Remote start, job loading, status and data export (OPC UA, REST) for automation; the build plate unload route and who clamps it for the Solukon.
- Power, argon flow and exhaust; the inert glovebox's power and size.
- Price of MIDI vs MIDI+, the 55 mm kit, and the PM schedule (filter, optics, recoater blades), service contract.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si (AlSi10Mg, Al 4047), Cu-Ni, NAB; reactive Al under 63 um (20-63 um LPBF cut). Batch: 55 mm kit builds of about 30 g; full cylinder about 440 g. Throughput: about 324 alloys a year through the full route; kit builds about 5 h each (`notes/timelapse.md`). Automation: UR10e pours a jar into the supply, a plate goes to the Solukon. Utilities: argon, mains **[to confirm]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** info@aconity3d.com
**Subject:** Budgetary quote: AconityMIDI+ with 55 mm kit, door automation, US sales contact

> Hello,
>
> We want a budgetary quote for one AconityMIDI (or MIDI+) with the 55 mm build kit and inert glovebox, and answers on door actuation and remote start for a robot cell. Please also forward to AconityUS or your North America representative.
>
> Facts:
> - Alloys: Al-Si, Cu-Ni, NAB; 55 mm kit builds of about 30 g, about 324 alloys a year.
> - Automation: a UR10e opens the door and pours powder into the supply cylinder.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. How does the MIDI's door open (hinge, lift, powered or manual) and can a robot or an actuator open and close it? Door clearance for a 2F-85 gripper, and does it release an interlock when the arm is inside?
> 2. Is the supply cylinder fill reachable from a jar-pour (440 g full cylinder), and how does a 55 mm kit change the supply (30 g)?
> 3. Remote start, job loading, status and data export (OPC UA, REST) for automation; the build plate unload route and who clamps it for the Solukon.
> 4. Power, argon flow and exhaust; the inert glovebox's power and size.
> 5. Price of MIDI vs MIDI+, the 55 mm kit, and the PM schedule (filter, optics, recoater blades), service contract.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://aconity3d.com/ (WebFetch/WebSearch from the runner)
- https://aconity3d.com/products/aconity-midi (fetched via the stream-cam Pi)
- https://www.amazemet.com/aconity-midi-lpbf-system-in-amazemets-rd-facility (WebFetch/WebSearch from the runner)
- https://aconity3d.com/products/aconity-midi-plus/ (2026-11-07, runner)
- https://www.3dnatives.com/3d-materials/en/3d-printers/aconity-midi-plus/ (2026-11-07, search snippet)

## 8. LPBF scale-up: EOS M 400-4

### 1. What we would buy
**Maker / model:** EOS GmbH EOS M 400-4 (four 400 W lasers, 400 x 400 x 400 mm), with its powder-handling stations. **Qty:** 1, scale-up (not part of the screening line). **Role and place:** chapter 8 scale-up on the floor (`notes/scaleup.md`).

- **Model check (2026-11-07):** **current**. EOS still calls the M 400-4 its flagship four-laser machine; the US address now redirects to the global page, which gives 5,140 x 2,490 x 2,625 mm, about 4,900 kg and at least 7,500 x 6,000 x 3,300 mm of installation space, so plan on those larger figures. Power (3 x 50 A, 45 kW max, 22 kW typical) and air (7 bar, 20 m3/h) are unchanged. (https://www.eos.info/Equipment/Metal-Platforms/EOS-M-400-4)

### 2. Published specs that matter for integration
Build 400 x 400 x 400 mm incl. plate; 4 x 400 W Yb fibre; up to 7.0 m/s; focus about 90 um; 3 x 50 A, 45 kW max, 22 kW typical; compressed air 7 bar, 20 m3/h. Size 4181 x 1613 x 2355 mm and about 4835 kg, install at least 6500 x 6000 x 3300 mm (EOS global page), while the EOS US page says 5140 x 2490 x 2625 mm, about 4900 kg, 7500 x 6000 x 3300 mm; ask which. Argon or nitrogen supply **[to confirm]**.

### 3. Contact

- **Email:** No sales email for the US; use the form https://www.eos.info/help-contact/contact-us (verified: https://www.eos.info/about-us/locations-worldwide, 2026-11-07); global info@eos.info is listed on the worldwide locations page
- **Phone:** +1 877 388 7916 (EOS North America: Pflugerville TX, Novi MI) (verified: https://www.eos.info/about-us/locations-worldwide, 2026-11-07)
- **Web / form:** https://www.eos.info/help-contact/contact-us (the earlier https://www.eos.info/en-us/contact is 404)
- **Regional rep / distributor:** EOS North America Pflugerville Technical Center, 3813 Helios Way #298, Pflugerville TX 78660; Novi Technical Center, 28970 Cabot Drive #700, Novi MI 48377; Advanced Laser Materials (ALM) Temple TX +1 254 773 3080; US sales partners listed: AdvancedTek (St. Paul MN, +1 651-489-6990), Phillips Corporation (Hanover MD, +1 864-395-7243), Phillips Federal (+1 301-997-6097) (verified: https://www.eos.info/about-us/locations-worldwide, 2026-11-07). No Mountain West rep listed (unverified: none published)
- **Contact status (2026-11-07):** verified: phone, offices, partners; no Utah rep or sales email published.

### 4. Our open questions for them

- Which size is correct (4181 x 1613 x 2355 vs 5140 x 2490 x 2625 mm), and is the M 400-4 a 2026 quote item or end-of-sale?
- Material and process parameter sets for Al-Si, Cu-Ni, NAB.
- Argon/nitrogen consumption, floor load, exhaust and a foundation.
- Automation interface for a robot to load plates and unload; service plan.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si, Cu-Ni, NAB; reactive Al. Batch: a full 400 mm bed for scale-up of down-selected alloys; not part of the 55 mm screening. Throughput: tens of builds a year. Utilities: 3 x 50 A, 7 bar air, argon.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** (EOS web form, https://www.eos.info/help-contact/contact-us; EOS North America +1 877 388 7916)
**Subject:** Budgetary quote: EOS M 400-4 for Al-Si and Cu alloys scale-up

> Hello,
>
> We want a budgetary quote for one EOS M 400-4 with powder handling, for scale-up of alloys screened on a small-format system.
>
> Facts:
> - Alloys: AlSi10Mg and Al 4047, Cu-Ni, NAB.
> - Need the correct footprint and mass, and utilities (power, argon, air).
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Which size is correct (4181 x 1613 x 2355 vs 5140 x 2490 x 2625 mm), and is the M 400-4 a 2026 quote item or end-of-sale?
> 2. Material and process parameter sets for Al-Si, Cu-Ni, NAB.
> 3. Argon/nitrogen consumption, floor load, exhaust and a foundation.
> 4. Automation interface for a robot to load plates and unload; service plan.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://eos.info/en-us/metal-solutions/metal-printers/data-sheets/sds-eos-m-400-4 (WebFetch/WebSearch from the runner)
- https://www.eos.info/en-us (fetched via the stream-cam Pi)
- https://www.eos.info/Equipment/Metal-Platforms/EOS-M-400-4 (2026-11-07, runner)

## 9. Cutting: FANUC ROBOCUT wire EDM (alpha-C400iC)

### 1. What we would buy
**Maker / model:** FANUC ROBOCUT alpha-C400iC (smallest of the alpha-C400iC / C600iC / C800iC set), with the automatic front door and a CCR rotary table **[to confirm]**; sold, integrated and serviced in North America by Methods Machine Tools. **Qty:** 1. **Role and place:** a floor machine beside the VLM; coupons 14 x 10 x 6 mm and 10 x 10 x 6 mm slices (`notes/alloy_workflow.md`, `notes/services.md`).

- **Model check (2026-11-07):** **current**. FANUC America still offers the ROBOCUT alpha-C400iC with a quote button (XY 400 x 300 mm, Z 255 mm, work up to 500 kg, machine about 2,200 kg). No "iD" generation was found: FANUC's own ROBOCUT pages still list the alpha-CiC series as the C400iC, C600iC and C800iC (added in 2024), with a June 2026 catalogue and 2026 software additions only. (https://www.fanucamerica.com/products/robocut/robocut-a-c400ic)

### 2. Published specs that matter for integration
Max workpiece weight 60 kg (page); automatic wire threading 10 s; unattended wire 60 h, 30 kg spool option up to 140 h; automatic front door, work-pan partial drain, automatic fill; up to 7 axes; thin wire 0.05 mm. 200 V 3-phase, 13 kVA (snippet), 36 A per phase at 208 V; the biggest single load on the line. DI water for the tank and chiller **[to confirm]**. Interfaces: FANUC CNC (door, programme start via I/O or FOCAS **[to confirm]**).

### 3. Contact

- **Email:** Contact form: https://www.fanucamerica.com/contact (no email on the page) (verified: https://www.fanucamerica.com/contact, 2026-11-07)
- **Phone:** 888-FANUC-US = 888-326-8287 ("Need immediate help?"; the first pass had 888-326-8723, wrong) (verified: https://www.fanucamerica.com/contact, 2026-11-07); Methods Machine Tools +1 877-668-4262 (verified: https://www.methodsmachine.com/contact/, 2026-11-07)
- **Web / form:** https://www.fanucamerica.com/products/robocut (the page links this; the first pass URL /products/robocut-wire-edm is unverified); form options include ROBOMACHINE Quote and Service & Parts
- **Regional rep / distributor:** Methods Machine Tools (Sudbury MA, 65 Union Ave, +1 978-443-5388): its contact page lists a Rocky Mountains line +1 602-848-1221 (also Southwest) (verified: https://www.methodsmachine.com/contact/, 2026-11-07); Phoenix office 615 West 24th St, Tempe AZ 85282, +1 602-437-2220 (verified: https://www.methodsmachine.com/locations/, 2026-11-07); the locations page lists no Utah office. Exclusive North American ROBOCUT importer: unverified (first-pass claim). Ask the Rocky Mountains line whether it covers Utah
- **Contact status (2026-11-07):** partial: FANUC phone corrected; Methods lines verified; Utah coverage and ROBOCUT exclusivity unverified.
- **Office / hours:** FANUC America HQ, 3900 West Hamlin Road, Rochester Hills MI 48309

### 4. Our open questions for them

- Which model fits a Kardex-adjacent floor slot and 14 x 10 x 6 mm coupons cut from a 6 mm plate; the footprint, mass, tank depth, and the door drop.
- Automation interface: can a UR10e load a workpiece through the automatic front door, and is there a door-open and start signal over I/O; recommended fixture and plate-clamp for coupons.
- Dielectric: DI water consumption, filter and resin schedule; wire cost per coupon; cutting rate (FANUC publishes no rate).
- Utilities: confirm 200 V 3-phase 13 kVA, chiller, and compressed air.
- PM schedule, consumables list and prices, service contract with a Utah engineer.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si, Cu-Ni, NAB; conductive. Batch: coupons 14 x 10 x 6 mm and 10 x 10 x 6 mm slices from printed bars; about 324 alloys, several coupons each. Automation: a UR10e through the door. Utilities: 200 V 3-phase, DI water **[to confirm]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** (FANUC America web form, https://www.fanucamerica.com/contact), cc Methods Machine Tools, 877-668-4262
**Subject:** Budgetary quote: ROBOCUT alpha-C400iC wire EDM with robot loading

> Hello,
>
> We want a budgetary quote for one ROBOCUT alpha-C400iC with the automatic front door, for cutting small coupons from printed Al-Si and Cu-alloy bars, loaded by a UR10e arm.
>
> Facts:
> - Coupons about 14 x 10 x 6 mm; about 324 alloys a year.
> - Need door, start and status signals for a robot cell.
> - Site: Utah **[to confirm]**; 208 V 3-phase **[to confirm]**.
>
> Questions:
> 1. Which model fits a Kardex-adjacent floor slot and 14 x 10 x 6 mm coupons cut from a 6 mm plate; the footprint, mass, tank depth, and the door drop.
> 2. Automation interface: can a UR10e load a workpiece through the automatic front door, and is there a door-open and start signal over I/O; recommended fixture and plate-clamp for coupons.
> 3. Dielectric: DI water consumption, filter and resin schedule; wire cost per coupon; cutting rate (FANUC publishes no rate).
> 4. Utilities: confirm 200 V 3-phase 13 kVA, chiller, and compressed air.
> 5. PM schedule, consumables list and prices, service contract with a Utah engineer.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.fanucamerica.com/products/robocut-wire-edm (WebFetch/WebSearch from the runner)
- https://www.methodsmachine.com/ (fetched via the stream-cam Pi)
- https://www.fanucamerica.com/products/robocut/robocut-a-c400ic (2026-11-07, runner)
- https://fanuc.eu/uk/en/who-we-are/news/eu-rc-a-c800ic-release-03-2024 (2026-11-07, search snippet)
- https://www.fanuc.co.jp/en/product/robocut/ (2026-11-07, search snippet)
- https://www.fanuc.co.jp/en/product/new_product/2024/202406_robocut_alphac800ic.html (2026-11-07, search snippet)

## 10. Sample prep: LECO PX500 polisher + MX400 mounting press

### 1. What we would buy
**Maker / model:** LECO Corporation PX500 grinder/polisher (touch screen, 6-position holder, fluid dispensing) and MX400 mounting press (1.5 in / 38.1 mm hot mounts in carbon-filled phenolic, 20 mm tall). **Qty:** 1 + 1; consumables: SiC papers 320-1200, alumina, diamond suspensions, mounting resin, polishing cloths. **Role and place:** chapter 6, the mount press and polisher at a tray or floor spot **[to confirm which]**; the arm loads mounts into the holder (`notes/refine_polisher.md`).

- **Model check (2026-11-07):** **current**. LECO's mounting-press page lists the MX400 with the MX500 (205 x 535 x 610 mm; an optional closed-loop MX Water Recirculator removes the need for facility water and a drain). LECO's PX-series page still lists the PX500 (10 and 12 in or 250 and 300 mm wheels, up to five fluid dispensers, 7 in touchscreen), though it did not load on the runner. (https://www.leco.com/instrument/mounting-presses/)

### 2. Published specs that matter for integration
PX500 about 533 W x 711 D x 635 H mm (a reseller's figure for the PX400/PX500; LECO publishes no dimensions); power rating not published (the model uses the EcoMet 30's 740 W as an estimate); water, drain and compressed air **[to confirm]**. MX400: depth 460 mm, height 480 mm to the deck (`eu.leco.com/product/mx400-500`). Interfaces: touch screen programmes; no remote start published.

### 3. Contact

- **Email:** info@leco.com (unverified: LECO's US contact page obscures the address; use the Contact Us form at https://www.leco.com/contacts/usa)
- **Phone:** +1 800-292-6141; +1 269-985-5496; Metallography or Elemental Analysis Instruments +1 269-985-5497 (verified: https://www.leco.com/contacts/usa, 2026-11-07)
- **Web / form:** https://www.leco.com/contacts/usa
- **Regional rep / distributor:** LECO instrument service, Western United States: +1 702-263-8547 / 8548 (verified: https://www.leco.com/contacts/usa, 2026-11-07); the page names no sales rep or distributor for Utah or the West (unverified: none published)
- **Contact status (2026-11-07):** partial: phones verified; email unverified (obfuscated); Utah rep none published.
- **Office / hours:** LECO Corporation, 3000 Lakeview Avenue, St. Joseph MI 49085

### 4. Our open questions for them

- How does a mount stay in the PX500's holder when it is lifted (spring, ball plunger, vacuum, mechanical pin), and can a robot gripper drop a 38.1 mm mount in and pull it out?
- Remote start of a programme, door and lid actuation, and status over contact closure or Ethernet; can the head be started by a PLC?
- Does the PX500 ship with a coolant tank, waste filtration, and what water/drain connections; electrical rating (not published).
- MX400: can its cycle be started remotely, and a robot-loadable mould; cycle time and cooling for a 1.5 in conductive mount; consumable resin price per mount.
- PM schedule, wearing parts (platen, seals, pump) and a service contract with a Utah or Las Vegas technician.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si, Cu-Ni, NAB coupons (conductive hot mounts for SEM/EDS and micro-Vickers). Batch: one coupon per mount, 6-position holder. Throughput: about 324 alloys, several coupons each, so over a thousand mounts a year. Automation: UR10e. Utilities: water, drain, air **[to confirm]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** LECO Contact Us form, https://www.leco.com/contacts/usa (info@leco.com is unverified)
**Subject:** Budgetary quote: PX500 polisher and MX400 mounting press, robot loading question

> Hello,
>
> We want a budgetary quote for one PX500 and one MX400 for metallographic prep of small Al-Si and Cu-alloy coupons, loaded by a UR10e. First question: how a mount is retained in the PX500's holder when it is lifted.
>
> Facts:
> - Mounts: 1.5 in (38.1 mm) conductive phenolic, about 1,000+ a year.
> - Need remote start and status for the PX500 and MX400.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. How does a mount stay in the PX500's holder when it is lifted (spring, ball plunger, vacuum, mechanical pin), and can a robot gripper drop a 38.1 mm mount in and pull it out?
> 2. Remote start of a programme, door and lid actuation, and status over contact closure or Ethernet; can the head be started by a PLC?
> 3. Does the PX500 ship with a coolant tank, waste filtration, and what water/drain connections; electrical rating (not published).
> 4. MX400: can its cycle be started remotely, and a robot-loadable mould; cycle time and cooling for a 1.5 in conductive mount; consumable resin price per mount.
> 5. PM schedule, wearing parts (platen, seals, pump) and a service contract with a Utah or Las Vegas technician.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.leco.com/contacts/usa (fetched via the stream-cam Pi)
- https://www.leco.com/instrument/px-series-grinder-polishers/ (fetched via the stream-cam Pi)
- https://eu.leco.com/product/mx400-500 (WebFetch/WebSearch from the runner)
- https://www.leco.com/instrument/mounting-presses/ (2026-11-07, runner)
- https://www.leco.com/instrument/px-series-grinder-polishers/ (2026-11-07, search snippet)
- https://eu.leco.com/product/px400-px500-grinder-polisher-series (2026-11-07, search snippet)

## 11. Sample prep (comparison): QATM QPOL 250 Bot automated polishing cell

### 1. What we would buy
**Maker / model:** QATM (a Verder Scientific brand, ATM Qness GmbH) QPOL 250 BOT, a robot grinding/polishing cell with a magazine of 16 pre-loaded 250 mm discs, six fluid reservoirs, a dosing unit, ultrasonic clean; used as a comparison to the PX500 route. **Qty:** quote only (1). **Role and place:** comparison for a robotic polishing cell (BAM's RASI cell uses one; `notes/refine_polisher.md`).

- **Model check (2026-11-07):** **current**. QATM's page still offers the Qpol 250 BOT (1,320 x 1,500 x 800 mm; up to 16 discs; six-fold dosing; fresh water R1/2 at up to 6 bar, DN50 drain, 6 bar air; touchscreen, no network port listed). (https://www.qatm.com/products/grinding-polishing-etching/fully-automatic-grinder-polisher/qpol-250-bot/)

### 2. Published specs that matter for integration
250 mm wheels, 160 mm sample holder, 1.1 kW drive, about 310 kg (DKSH Australia spec snippet; **[confirm]**); room for 16 grinding/polishing media; integrated ultrasonic cleaning; compressed air and water **[to confirm]**. Robot-ready by design.

### 3. Contact

- **Email:** Form: https://www.qatm.com/contact/contact-form/ (loads; has a US state field) (verified: https://www.qatm.com/contact-services/, 2026-11-07); US: info-us@verder-scientific.com (verified: https://www.verder-scientific.com/us, 2026-11-07)
- **Phone:** +1 866-473-8724 (Verder Scientific Inc., Newtown PA) (verified: https://www.verder-scientific.com/us, 2026-11-07)
- **Web / form:** https://www.qatm.com/contact-services/
- **Regional rep / distributor:** QATM sells through Verder Scientific Inc. in the US; Jason Starr, Team Leader QATM USA (verified: https://www.verder-scientific.com/us, 2026-11-07); no separate Utah rep (the QATM form has a US state list including Utah, and routes the request)
- **Contact status (2026-11-07):** verified: email, phone, QATM USA team leader; no Utah rep published.
- **Office / hours:** 11 Penns Trail, Newtown PA 18940

### 4. Our open questions for them

- Is the BOT supplied with its own gripper and magazine of 16 discs, and how does it hold a 38.1 mm mount; can it be loaded by a UR10e?
- Mounts per hour and consumable cost per mount for Al-Si and Cu alloys.
- Utilities, footprint, and software interface; PM and service price.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si, Cu-Ni, NAB mounts. Batch: 16 discs a magazine. Throughput: over a thousand mounts a year. Utilities: air, water, 230 V **[to confirm]**.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** info-us@verder-scientific.com
**Subject:** Budgetary quote: QATM QPOL 250 BOT for small Al-Si and Cu coupons

> Hello,
>
> We are comparing automated polishing options and want a budgetary quote for a QPOL 250 BOT for small coupons in 38.1 mm mounts.
>
> Facts:
> - About 1,000+ mounts a year.
> - Robot cell integration with a UR10e **[to confirm]**.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Is the BOT supplied with its own gripper and magazine of 16 discs, and how does it hold a 38.1 mm mount; can it be loaded by a UR10e?
> 2. Mounts per hour and consumable cost per mount for Al-Si and Cu alloys.
> 3. Utilities, footprint, and software interface; PM and service price.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.qatm.com/ (fetched via the stream-cam Pi)
- https://www.atm-m.com/products/grinding-polishing-etching/fully-automatic-grinder-polisher/qpol-250-bot/ (WebFetch/WebSearch from the runner)
- https://www.verder-scientific.com/contact-services (fetched via the stream-cam Pi)
- https://www.qatm.com/products/grinding-polishing-etching/fully-automatic-grinder-polisher/qpol-250-bot/ (2026-11-07, runner)

## 12. Sample prep: Buehler VibroMet 2

### 1. What we would buy
**Maker / model:** Buehler (ITW) VibroMet 2 vibratory polisher (model 67-1635-250 in listings **[to confirm]**) with holders and weights, 0.1 um diamond/colloidal silica. **Qty:** 1. **Role and place:** the SOP's final step, 0.1 um diamond for 1-2 h, checked every 30 min; not modelled, a caption (`notes/refine_polisher.md`).

- **Model check (2026-11-07):** **superseded by VibroMet 3**. Buehler's VibroMet 2 page says "The VibroMet 2 has been discontinued and replaced by our updated VibroMet 3." The VibroMet 3 is one part number, 67-2105, for 100-240 V single phase (no separate 115 V and 230 V units), keeps the 12 in (305 mm) cloth with a 285 mm usable area, takes holders for 25, 30, 40 and 50 mm mounts, stores up to 6 methods and has ON, OFF or PULSE end-of-cycle options; its page gives no size, weight or remote interface. (https://www.buehler.com/products/grinding-and-polishing/vibratory-polishers/vibromet-2-vibratory-polisher/)

### 2. Published specs that matter for integration
Horizontal-oscillating vibratory bowl; bowl size, weight and 115/230 V figures not read **[to confirm from the brochure]**; mains only; no remote interface.

### 3. Contact

- **Email:** info@buehler.com; support@buehler.com (verified: https://www.buehler.com/contact, 2026-11-07)
- **Phone:** +1 800-283-4537; +1 847-295-6500 (verified: https://www.buehler.com/contact, 2026-11-07)
- **Web / form:** https://www.buehler.com/contact (US state selector)
- **Regional rep / distributor:** https://www.buehler.com/contact has a US state selector (Utah included) that shows the contact only after a selection (unverified: the Utah rep could not be read); service locations https://www.buehler.com/service/service-locations/ (verified 2026-11-07, no Utah entry read)
- **Contact status (2026-11-07):** partial: email and phone verified; Utah rep unverified.
- **Office / hours:** Buehler, 41 Waukegan Road, Lake Bluff IL 60044

### 4. Our open questions for them

- Can a mount holder be loaded and removed by a robot; holder sizes for 38.1 mm mounts and weights.
- Power, footprint and an on/off contact for a robot cell.
- Consumables (cloth, suspension) and PM schedule; service contract.
- The VibroMet 2 is discontinued: the VibroMet 3 (67-2105) price, size, weight, and whether it has a start/stop or status contact for a robot cell.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: Al-Si, Cu-Ni, NAB polished mounts for EBSD/nanoindentation. Batch: 6 mounts per holder. Throughput: hundreds a year. Utilities: mains.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** info@buehler.com  
**Cc:** support@buehler.com
**Subject:** Budgetary quote: VibroMet 2 with holders and consumables

> Hello,
>
> We want a budgetary quote for one VibroMet 2 with holders for 38.1 mm mounts, loaded by a robot arm, for final polishing of Al and Cu alloy coupons.
>
> Facts:
> - Batch: up to 6 mounts, 1-2 h cycles.
> - Need a start contact or timer interface.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Can a mount holder be loaded and removed by a robot; holder sizes for 38.1 mm mounts and weights.
> 2. Power, footprint and an on/off contact for a robot cell.
> 3. Consumables (cloth, suspension) and PM schedule; service contract.
>
> Your site says the VibroMet 2 has been replaced by the VibroMet 3: please quote the current model and say what changed in size, weight, utilities and remote control.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.buehler.com/ (fetched via the stream-cam Pi)
- https://www.buehler.com/contact/ (fetched via the stream-cam Pi)
- https://www.buehler.com/products/grinding-and-polishing/vibratory-polishers/vibromet-2-vibratory-polisher/ (2026-11-07, runner)
- https://www.buehler.com/products/grinding-and-polishing/vibratory-polishers/vibromet-3-vibratory-polisher/ (2026-11-07, runner)
- https://www.jhtechnologies.com/products/buehler/buehler-vibromet™-2 (2026-11-07, search snippet)
- https://manuals.online/buehler/laboratory-equipment/vibromet-2/user-manual/1p3yd (2026-11-07, search snippet)

## 13. Machining: Makera Carvera CNC

### 1. What we would buy
**Maker / model:** Makera Carvera (desktop 4-axis CNC, 200 W spindle with ER11 collet, automatic tool changer; the Carvera Air is the smaller sibling) **[to confirm which]**. **Qty:** 1 + collets/end mills. **Role and place:** faces 1.5 in 416-stainless pucks flush (0.4 mm off) for nanoindentation and PIP, tray M at Shuttle 2 (`notes/instruments_r7.md`).

- **Model check (2026-11-07):** **current**. Makera showed the Carvera, the Carvera Air and the new entry-level Z1 at CES 2026, its own Carvera page still sells the Carvera, and no Carvera 2 was found. Makera has teased a new desktop CNC for Formnext (17-20 November 2026), so check again after that; makera.com returned 429 to the runner. (https://themachinemaker.com/news/makera-to-present-next-generation-desktop-cnc-solutions-at-ces-2026/)

### 2. Published specs that matter for integration
200 W spindle, ER11, auto tool change, enclosed; mains 110/220 V **[to confirm]**; USB/Wi-Fi control, G-code; door automation not supported **[to confirm]**.

### 3. Contact

- **Email:** support@makera.com; orders@makera.com; info@makera.com; cam@makera.com (verified: https://www.makera.com/, 2026-11-07)
- **Phone:** +1 (888) 456-5472 (verified: https://www.makera.com/, 2026-11-07)
- **Web / form:** https://www.makera.com/
- **Regional rep / distributor:** Direct web store; no reseller list read (unverified: the contact-us page returned 404 or HTTP 429)
- **Contact status (2026-11-07):** verified: emails and phone on the Makera homepage; resellers unverified.

### 4. Our open questions for them

- Can a robot load work through the door, does the Carvera accept a remote start (Wi-Fi/serial G-code), and is a probe/auto-zero available for a fixture?
- Spindle and tool life when facing 416 stainless and Cu pucks, and the PM schedule.
- Business or education price and service terms.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: stainless pucks with Al/Cu coupons; facing 0.4 mm. Batch: one puck a run. Throughput: hundreds a year. Utilities: mains, vacuum for chips.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** support@makera.com  
**Cc:** orders@makera.com
**Subject:** Education quote: Carvera for facing small stainless pucks in an automated lab

> Hello,
>
> We want a quote for one Carvera, with a spare tool set, used to face 1.5 in stainless pucks, and a question on remote start and door automation.
>
> Facts:
> - Cuts: facing 0.4 mm on 416 stainless.
> - Control: a UR10e loads work.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Can a robot load work through the door, does the Carvera accept a remote start (Wi-Fi/serial G-code), and is a probe/auto-zero available for a fixture?
> 2. Spindle and tool life when facing 416 stainless and Cu pucks, and the PM schedule.
> 3. Business or education price and service terms.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.makera.com/pages/contact-us (fetched via the stream-cam Pi)
- https://www.makera.com/ (fetched via the stream-cam Pi)
- https://themachinemaker.com/news/makera-to-present-next-generation-desktop-cnc-solutions-at-ces-2026/ (2026-11-07, search snippet)
- https://overclock3d.net/?p=316261 (2026-11-07, search snippet)
- https://www.makera.com/products/carvera (2026-11-07, search snippet)

## 14. DED and repair: Meltio M450 and its robot cell

### 1. What we would buy
**Maker / model:** Meltio M450 (wire-laser DED) and the Meltio Robot Cell with the Blue Laser Engine **[to confirm]**. **Qty:** 1 (cell for scale-up). **Role and place:** M450 is 1400 mm tall, floor-standing (`notes/scaleup.md`, `fab_metal.py`); the cell repairs a part with a programme (`r8_scale.py`).

- **Model check (2026-11-07):** **superseded by Meltio M600**. The M450 address on Meltio's site now shows the M600, Meltio's products page lists only the M600, the Robot Cell and the Engine Robot and Engine CNC kits, a reseller shows the M450 as unavailable, and Meltio's CEO calls the M600 the M450's second generation; no formal end-of-life notice was found. The M600 is much bigger than the 1400 mm tall M450: 300 x 400 x 600 mm build, 1,050 x 1,050 x 1,950 mm, 800-1,000 kg, 3-phase 400 V (4-6 kW average, 10.6 kW peak), water chiller included, blue laser. (https://meltio3d.com/products/meltio-m450/)

### 2. Published specs that matter for integration
M450 1400 mm tall; the substrate plate enters via a front door; argon shield gas; wire spools; mains **[to confirm]**. Robot cell: a six-axis robot and a Meltio head; software on request.

### 3. Contact

- **Email:** web form: https://meltio3d.com/contact/
- **Phone:** +1 915-282-3437 (USA & LATAM, Gabriel Ortiz) (verified: https://meltio3d.com/contact/, 2026-11-07)
- **Web / form:** https://meltio3d.com/contact/
- **Regional rep / distributor:** The contact page's "Select a Partner" dropdown lists AECAM Solutions and ExBuild among others, without country or role (verified: https://meltio3d.com/contact/, 2026-11-07); so ExBuild is still listed. US sales partner Automation Engineering Company (AEC), 9 Shelter Drive, Greer SC 29650 (announced 2026-02-23; teamaec.com) (unverified: not on the contact page)
- **Contact status (2026-11-07):** partial: phone and web form verified; AEC and ExBuild territory unverified; no email published.

### 4. Our open questions for them

- Which Meltio parts and wires for Al-Si, Cu-Ni and NAB; is the 630 bronze wire available?
- Door, plate loading and a start signal for a UR10e; the cell's price and software.
- Argon use, power, PM schedule, consumables, service plan.
- The M450 address on your site now shows the M600: is the M450 still sold? If not, the M600's price, size (1,050 x 1,050 x 1,950 mm), weight (800-1,000 kg), 400 V 3-phase supply, chiller, and start/status interface for a robot.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: NAB, Cu-Ni, Al-Si wires. Batch: repair and bead tests. Throughput: low, scale-up. Utilities: argon, mains.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** (Meltio web form, https://meltio3d.com/contact/) and AEC
**Subject:** Budgetary quote: Meltio M450 and a robot cell for alloy scale-up and repair

> Hello,
>
> We want a budgetary quote for one M450 and for a Meltio Robot Cell, for NAB, Cu-Ni and Al-Si wire builds and repair.
>
> Facts:
> - Wire alloys: C63000, Cu-30Ni, Al-Si.
> - Need door and start signals for a UR10e.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Which Meltio parts and wires for Al-Si, Cu-Ni and NAB; is the 630 bronze wire available?
> 2. Door, plate loading and a start signal for a UR10e; the cell's price and software.
> 3. Argon use, power, PM schedule, consumables, service plan.
>
> Your site now shows the M600 where the M450 was: if the M450 is no longer sold, please quote the current model and say what changed in size, weight, utilities and remote control.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://meltio3d.com/contact/ (fetched via the stream-cam Pi)
- https://www.metal-am.com/?p=114955 (WebFetch/WebSearch from the runner)
- https://meltio3d.com/products/meltio-m450/ (2026-11-07, runner)
- https://meltio3d.com/products/ (2026-11-07, runner)
- https://3dprint.com/307901/on-ground-in-spain-for-meltio-m600-2 (2026-11-07, search snippet)
- https://matterhackers.com/store/l/meltio-m450-wire-laser-metal-3d-printer (2026-11-07, search snippet)

## 15. DED: InssTek MX-Lab

### 1. What we would buy
**Maker / model:** InssTek MX-Lab (3-axis laser-powder DED, argon with a 50 ppm O2 option). **Qty:** 1 or use the University of Utah's (the DAL #219 notes name 'Utah (InssTek MX-Lab)'). **Role and place:** floor machine (`notes/scaleup.md`).

- **Model check (2026-11-07):** **current**. InssTek's site still lists the MX-Lab beside the MX-Fab, MX-Med and MX-Custom, and one was installed at Chalmers in April 2025. One Russian reseller marks it discontinued, which the maker's page contradicts. (https://www.insstek.com/)

### 2. Published specs that matter for integration
680 x 684 x 835 mm without accessories (the base cabinet is not published); 250 kg (the model's figure); argon (50 ppm O2 option), powder carrier gas, 220 V 15(20) A, exhaust.

### 3. Contact

- **Email:** sales@insstek.com (verified: https://www.insstek.com/, 2026-11-07)
- **Phone:** +82-42-935-9646 (fax -9649) (verified: https://www.insstek.com/, 2026-11-07)
- **Web / form:** http://www.insstek.com/
- **Regional rep / distributor:** US: Phillips Corporation (Hanover MD): +1 410-564-2929 or 800-878-4242, sales pcsales@phillipscorp.com, and it lists InssTek and EOS under Solutions by Brand (verified: https://www.phillipscorp.com/contact-us/, 2026-11-07); Phillips names no Western rep. Whole Metals (Chicago) showroom (unverified)
- **Contact status (2026-11-07):** verified: InssTek email and phone; Phillips verified; Whole Metals unverified.
- **Office / hours:** 154 Sinseong-ro, Yuseong-gu, Daejeon

### 4. Our open questions for them

- What the base cabinet holds and its height; footprint with accessories.
- Door actuation and start for automation; powder and Ar consumption.
- Price, PM and service contract in the US via Phillips.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: 45-105 and 100-200 um DED powder cuts. Batch: about 0.5 kg lots for Utah's blown-powder tracks. Utilities: argon, 220 V.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** sales@insstek.com
**Subject:** Budgetary quote: MX-Lab via Phillips, for alloy blown-powder tracks

> Hello,
>
> We want a budgetary quote for one MX-Lab with the low-O2 option, and the US contact at Phillips.
>
> Facts:
> - Powder: 45-105 um Al-Si and Cu alloys, about 0.5 kg lots.
> - Site: Utah **[to confirm]**.
> - Utilities: argon, 220 V.
>
> Questions:
> 1. What the base cabinet holds and its height; footprint with accessories.
> 2. Door actuation and start for automation; powder and Ar consumption.
> 3. Price, PM and service contract in the US via Phillips.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- http://www.insstek.com/ (fetched via the stream-cam Pi)
- https://www.phillipscorp.com/insstek/ (fetched via the stream-cam Pi)
- https://www.insstek.com/ (2026-11-07, runner)
- https://www.metal-am.com/insstek-installs-mx-lab-ded-additive-manufacturing-machine-at-chalmers-university/ (2026-11-07, search snippet)

## 16. Fabrication: SnowX SnowPod (pre-release desktop LPBF)

### 1. What we would buy
**Maker / model:** SnowX SnowPod (desktop LPBF, 316L at launch, with the NitroPod nitrogen separator). **Qty:** 2 (tray I, two units). **Role and place:** the only powder-bed machine that passes the 727.5 mm opening (`fab_metal.py`).

- **Model check (2026-11-07):** **unconfirmed** (not yet released). Early-bird reservations are open on Kickstarter, the launch is expected in Q4 2026 and no ship date is given. Known so far: 80 x 80 x 100 mm build, 316L in sealed cartridges, a SnowPod and NitroPod kit; size, weight, power and network control are not published. (https://www.3dnatives.com/en/desktop-metal-3d-printer-snowpod-22102026/)

### 2. Published specs that matter for integration
360 x 360 x 660 mm, 40 kg, 80 x 80 x 100 mm build, 200 W fibre, 40 um spot; N2 from NitroPod about 99.9 % at 3 L/min; a Kickstarter kit, launch planned Q4 2026, not shipping yet. Planned price $5,299 (kit); $5,899 with the NitroPod (a news report).

### 3. Contact

- **Email:** contact@snowx.com (verified: https://snowx.com/, 2026-11-07)
- **Phone:** +86 512 6672 8020 (verified: https://snowx.com/, 2026-11-07)
- **Web / form:** https://snowx.com/
- **Regional rep / distributor:** None (Suzhou)
- **Contact status (2026-11-07):** verified: email and phone on the SnowX homepage.
- **Office / hours:** SnowX Technology Co., Ltd.

### 4. Our open questions for them

- Ship date, US warranty and service, and whether Al-Si and Cu alloys are validated.
- Interface for remote start and door actuation.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: 316L at launch only; Al-Si and Cu alloys unsupported. Batch: 80 x 80 x 100 mm. Utilities: N2 from the NitroPod.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** contact@snowx.com
**Subject:** Pre-order enquiry: two SnowPod units for a research lab

> Hello,
>
> We would like pricing for two SnowPod units with NitroPod, and your plan for Al-Si and Cu alloys.
>
> Facts:
> - Use: alloy screening at small scale.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Ship date, US warranty and service, and whether Al-Si and Cu alloys are validated.
> 2. Interface for remote start and door actuation.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://snowx.com/ (fetched via the stream-cam Pi)
- https://www.3dnatives.com/en/desktop-metal-3d-printer-snowpod-22102026/ (WebFetch/WebSearch from the runner)
- https://www.3dnatives.com/en/desktop-metal-3d-printer-snowpod-22102026/ (2026-11-07, runner)
- https://3dprintingindustry.com/news/snowx-opens-kickstarter-pre-launch-page-for-snowpod-compact-metal-3d-printer-255152/ (2026-11-07, search snippet)

## 17. Fabrication: Formlabs Form 4, Form Wash, Form Cure

### 1. What we would buy
**Maker / model:** Formlabs Form 4 (resin SLA), Form Wash and Form Cure (2nd gen). **Qty:** 1 + 1 + 1 **[to confirm what the lab owns]**. **Role and place:** tray G (`fab_resin.py`, `notes/refine_form4.md`).

- **Model check (2026-11-07):** **current**. Formlabs still sells the Form 4 and the second-generation Form Wash V2 and Form Cure V2, which its pages list as compatible with the Form 4; the Form 4L is a larger sibling, not a replacement, and no Form 5 was found. The new Form Studio 1 (ships from 16 November 2026) is a separate low-cost line. (https://formlabs.com/3d-printers/form-4/)

### 2. Published specs that matter for integration
Form 4 cover open 407 x 478 x 844 mm, 18.3 kg; Form Wash 315 x 293 x 405 mm; Form Cure 337 x 356 x 404 mm, 12.1 kg; 405 nm turntable; power and resin/IPA EHS questions open.

### 3. Contact

- **Email:** Form: https://formlabs.com/company/contact/sales/
- **Phone:** +1 833-489-0545 (US/Canada; shown as +1 833 489 0545) (verified: https://formlabs.com/company/contact/sales/, 2026-11-07); the 9-6 ET hours were not re-checked (unverified)
- **Web / form:** https://formlabs.com/company/contact/sales/
- **Regional rep / distributor:** Reseller in Utah: GoEngineer, 739 Fort Union Blvd, Midvale UT 84047, +1 800 688 3234 (verified: https://formlabs.com/company/partners/, 2026-11-07); no email on the page
- **Contact status (2026-11-07):** verified: sales form, phone, Utah reseller GoEngineer.
- **Academic / owner note:** Education discounts via sales.

### 4. Our open questions for them

- Remote start by API (PreForm Dashboard), cover opening by a robot, and cartridge exchange.
- Resin and IPA handling; PM schedule for the Form 4's tank/LF; service plans.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: standard resins for fixtures, mounts, test rigs. Batch: small. Utilities: mains, ventilation.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** (Formlabs sales form)
**Subject:** Quote: Form 4, Form Wash, Form Cure with service plan

> Hello,
>
> We want a quote for a Form 4 with Wash and Cure for an automated lab and a service plan.
>
> Facts:
> - Robot loads/unloads the build platform.
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Remote start by API (PreForm Dashboard), cover opening by a robot, and cartridge exchange.
> 2. Resin and IPA handling; PM schedule for the Form 4's tank/LF; service plans.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://formlabs.com/company/contact/sales/ (fetched via the stream-cam Pi)
- https://formlabs.com/3d-printers/form-4/ (2026-11-07, runner)
- https://3dprinting.com/news/formlabs-launches-form-studio-1/ (2026-11-07, search snippet)
- https://formlabs.com/products/form-wash/ (2026-11-07, search snippet)
- https://formlabs.com/products/form-cure/ (2026-11-07, search snippet)

## 18. Fabrication: Opulo LumenPnP

### 1. What we would buy
**Maker / model:** Opulo LumenPnP pick-and-place. **Qty:** 1. **Role and place:** tray H for PCB assembly (`fab_pcb.py`).

- **Model check (2026-11-07):** **current**. Opulo's product page lists LumenPnP v4.1.0 as what ships (the v4 line launched in September 2024), and no newer hardware revision was found; quote and configure for v4.1, which has its own OpenPnP config files. opulo.io returned 429 to the runner. (https://www.opulo.io/products/lumenpnp)

### 2. Published specs that matter for integration
Open hardware (opulo-inc/lumenpnp); mains; USB control; 600 x 120 mm build plate in the model; needs air/vacuum **[to confirm]**.

### 3. Contact

- **Email:** Form: https://www.opulo.io/pages/contact-sales (no email published; privacy@opulo.io is for data requests)
- **Phone:** not published (verified: https://www.opulo.io/pages/contact-sales shows a form, no phone or email, 2026-11-07)
- **Web / form:** https://www.opulo.io/pages/contact-sales
- **Regional rep / distributor:** Direct
- **Contact status (2026-11-07):** partial: form URL verified; no email or phone published.

### 4. Our open questions for them

- Lead time for a LumenPnP, the feeder set, and spare nozzles/vacuum parts.
- Service and PM for feeders.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: PCBs for sensors. Batch: small. Utilities: mains.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** (Opulo sales form)
**Subject:** Quote: LumenPnP with feeders

> Hello,
>
> We want a quote for one LumenPnP with feeders and spares.
>
> Facts:
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Lead time for a LumenPnP, the feeder set, and spare nozzles/vacuum parts.
> 2. Service and PM for feeders.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.opulo.io/ (fetched via the stream-cam Pi)
- https://www.opulo.io/pages/contact-us (fetched via the stream-cam Pi)
- https://www.opulo.io/products/lumenpnp (2026-11-07, search snippet)
- https://docs.opulo.io/openpnp (2026-11-07, search snippet)

## 19. Fabrication: DDM Novastar SPR-45VA stencil printer

### 1. What we would buy
**Maker / model:** DDM Novastar SPR-45VA semi-automatic stencil printer. **Qty:** 1. **Role and place:** tray H (`fab_pcb.py`).

- **Model check (2026-11-07):** **current**. DDM Novastar's stencil-printer page still lists the SPR-45VA (semi-automatic, SMTrue Vision Assist) beside the SPR-45, SPR-25 and SPR-20. A machinetools.com directory marks the Novastar brand "no longer made", which the maker's own page contradicts. (https://www.ddmnovastar.com/stencil-printers)

### 2. Published specs that matter for integration
762 x 889 x 406 mm, about 73 kg; frames up to 584 x 584 mm; dual squeegees; power frame lift; vacuum nest; compressed air **[to confirm]**.

### 3. Contact

- **Email:** sales@ddmnovastar.com; service@ddmnovastar.com (verified: https://www.ddmnovastar.com/contact-us, 2026-11-07)
- **Phone:** +1 215-485-5663 x208 (sales); x230 (service/support) (verified: https://www.ddmnovastar.com/contact-us, 2026-11-07)
- **Web / form:** https://www.ddmnovastar.com/contact-us
- **Regional rep / distributor:** The contact page has a "Find a DDM Representative" selector by world area, country or state, and a map; the Utah result was not readable from the static page (unverified)
- **Contact status (2026-11-07):** verified: emails, phone, extensions; Utah rep unverified.
- **Office / hours:** 212 Railroad Drive, Ivyland PA 18974

### 4. Our open questions for them

- Remote start and frame lift trigger; service interval; squeegee parts and prices.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: solder paste on PCBs. Batch: small. Utilities: air, mains.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** sales@ddmnovastar.com
**Subject:** Quote: SPR-45VA

> Hello,
>
> We want a quote for one SPR-45VA with spare squeegees and a service plan.
>
> Facts:
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Remote start and frame lift trigger; service interval; squeegee parts and prices.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.ddmnovastar.com/contact-us (fetched via the stream-cam Pi)
- https://www.ddmnovastar.com/stencil-printers (2026-11-07, runner)
- https://www.machinetools.com/en/brands/novastar (2026-11-07, search snippet)

## 20. Fabrication: Bambu Lab H2D, A1 mini and A2L - OWNED (H2D, A1 mini): spares and consumables

### 1. What we would buy
**Maker / model:** Bambu Lab H2D and A1 mini (owned), A2L **[model and ownership to confirm; no specs in the notes]**. **To buy:** nozzles (0.2 or 0.4 mm only, lab rule), hotends, build plates, AMS, belts, filament. **Role and place:** H2D tray C; A1 mini (`lab_models/equipment.py`).

- **Model check (2026-11-07):** **current** (H2D, A1 mini, A2L). Bambu's US store lists the H2D and the A1 mini for sale beside the H3C (launching), X2D, P2S, H2C, P1S, A1 and H2S, and promotes the A2L as all-new, grouping it with the H2 series as the printers with 300 mm+ build volumes; Bambu's spec page gives the A2L (launched 1 June 2026) as open-frame, 330 x 320 x 325 mm build, 544 x 529 x 505 mm, about 12.8 kg, 80 C bed, 0.2 to 0.8 mm nozzles, 2.4 GHz Wi-Fi only (no Ethernet) and 1000 W in a 100-120 V version. For the owned printers, the store still sells H2D spare parts, and when Bambu ended the X1 and P1P in 2026 it kept an end-of-life service period; an "A1 Mini 2" and an H2S replacing the H2D appeared on one aggregator only and are rejected, since the store sells both the H2D and the H2S. (https://us.store.bambulab.com/collections/3d-printer)

### 2. Published specs that matter for integration
H2D envelope 492 x 514 x 626 mm, bed 350 x 320 mm, 1,050 W average, 1,320 W max at 110 V (snippet); A1 mini 347 x 315 x 365 mm. LAN mode needs a Pi; starts need the Bambu cloud login (CLAUDE.md).

### 3. Contact

- **Email:** contact@bambulab.com (feedback); bd@bambulab.com (business); support via https://bambulab.com/en-us/contact-us (all unverified: bambulab.com returned 403 / a Cloudflare challenge to the runner, the Pi and headless Chromium, 2026-11-07)
- **Phone:** not published
- **Web / form:** https://bambulab.com/en-us/contact-us
- **Regional rep / distributor:** Dealer list https://bambulab.com/en-us/dealer (unverified: blocked)
- **Contact status (2026-11-07):** unverified: site blocked on 2026-11-07; contacts carried over from the first pass.
- **Status:** owned by the lab; the contact is for spares, consumables and service.

### 4. Our open questions for them

- Is a business or education account available that does not require the shared lab login for LAN start?
- Spare parts availability and warranty for the H2D hotends.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: PLA/PETG fixtures. Batch: small. Utilities: mains.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** contact@bambulab.com (unverified: bambulab.com blocked the checks)
**Subject:** Education/business purchase: H2D spares and print-start accounts

> Hello,
>
> We own an H2D and an A1 mini and need spares and a business account for automated starts.
>
> Facts:
> - Site: Utah **[to confirm]**.
>
> Questions:
> 1. Is a business or education account available that does not require the shared lab login for LAN start?
> 2. Spare parts availability and warranty for the H2D hotends.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://bambulab.com/en-us/contact-us (fetched via the stream-cam Pi)
- https://bambulab.com/en-us/dealer (fetched via the stream-cam Pi)
- https://us.store.bambulab.com/collections/3d-printer (2026-11-07, maker's page, headed Chromium on the stream-cam Pi)
- https://bambulab.com/en/a2l/specs (2026-11-07, search snippet)
- https://blog.bambulab.com/bambu-lab-a2l-creative-playground-extra-large (2026-11-07, search snippet)
- https://us.store.bambulab.com/products/a1-mini (2026-11-07, search snippet)
- https://bambulab.com/en/support/buying-guide?id=904389439320043520&page=2 (2026-11-07, search snippet)
- https://3dprintingindustry.com/news/new-bambu-lab-a2l-3d-printer-technical-specifications-and-pricing-252057/ (2026-11-07, search snippet)
- https://uk.store.bambulab.com/en/collections/spare-parts-for-h2d (2026-11-07, search snippet)
- https://all3dp.com/4/bambu-lab-ceases-production-of-the-p1p-outlines-5-year-end-of-life-service/ (2026-11-07, search snippet)
- https://3dprintingindustry.com/news/bambu-lab-discontinues-the-x1-series-after-four-years-on-the-market-250791/ (2026-11-07, search snippet)

## 21. Feedstock: 5N Al and OFE Cu (C10100) bar, Si and Ni powders, AlSi10Mg powder

### 1. What we would buy
**What:** 5N Al rod 20 mm x 100 mm + 12 mm x 100 mm (DAL #152: 20 mm OD cup stock, press-fit plug; the pair costs $1,920 at 100 mm, $1,590 at 50 mm); OFE Cu C10100 rods of the same sizes (DAL #162, #222); Si powder (coarse 45-106 um), Ni powder; AlSi10Mg powder as a benchmark. **Qty:** 48 cups and 48 plugs of each metal (`notes/alloy_charge.md`); **[to confirm]** powder kg. Suppliers found: Goodfellow, ESPI Metals, American Elements, Heeger Materials, MSE Supplies, McMaster, Valimet.

- **Model check (2026-11-07):** **current**. These are standard grades, not models (5N is a purity, C10100 the UNS number for OFE copper, AlSi10Mg is covered by ASTM F3318), so nothing is superseded; check stock and certificates when quoting. (https://en.wikipedia.org/wiki/AlSi10Mg)

### 2. Published specs that matter for integration
Al 5N: Goodfellow 20 mm x 50/100/300/1000 mm at $860/$1,070/$1,750/$3,540 (DAL #152). Cu: McMaster has 630 NAB (8203K41). McMaster ground 6061 20 mm 6940T22 (+/-0.013 mm) is the stand-in. OFE C10100 price not found. Si powder: Heeger spherical 45-106 um.

### 3. Contact

- **Email:** Goodfellow: inq@goodfellow.com (verified: https://www.goodfellow.com/usa/contact-us, 2026-11-07); Heeger: sales@heegermaterials.com (verified: https://www.heegermaterials.com/, 2026-11-07); ESPI Metals: sales@espimetals.com (verified: https://www.espimetals.com/index.php/contact-us, 2026-11-07); MSE Supplies: sales@msesupplies.com (verified: https://www.msesupplies.com/, 2026-11-07); Valimet: sales@valimet.com (verified: https://www.valimet.com/contact, 2026-11-07); McMaster: chi.sales@mcmaster.com (unverified: the contact page shows only the phone and an Email Us link)
- **Phone:** Goodfellow +1 800-821-2870 (verified: https://www.goodfellow.com/usa/contact-us, 2026-11-07); Heeger +1 833-222-8587 (verified: https://www.heegermaterials.com/, 2026-11-07); McMaster +1 630-833-0300 (verified: https://www.mcmaster.com/help/contact-us/, 2026-11-07); ESPI +1 541-488-8311 / 800-638-2581 (verified: https://www.espimetals.com/index.php/contact-us, 2026-11-07); MSE Supplies +1 520-789-6673 (verified: https://www.msesupplies.com/, 2026-11-07); Valimet +1 209-444-1600 (verified: https://www.valimet.com/contact, 2026-11-07); American Elements +1 310-208-0551 (unverified: americanelements.com returns 403)
- **Web / form:** https://www.goodfellow.com/usa/aluminium-rod-group
- **Regional rep / distributor:** ESPI Metals (Ashland OR, 1050 Benson Way) quotes same day, no public prices (verified: its contact page); MSE Supplies (Tucson AZ) reachable from its homepage; Online Metals unverified (403 to the runner and the Pi); Valimet, 431 Sperry Road, Stockton CA 95206, phone now verified on its own page
- **Contact status (2026-11-07):** partial: Goodfellow, Heeger, ESPI, MSE, Valimet, McMaster phone verified; McMaster email, American Elements, Online Metals unverified.
- **Office / hours:** Goodfellow, 301 Grant Street, Suite 270, Pittsburgh PA 15219

### 4. Our open questions for them

- 5N rod tolerance on a 20 mm OD; lot certificates (GDMS) and an oxygen figure; tighter-tolerance ground stock.
- OFE C10100 20 mm and 12 mm rod, ASTM B187/B301, as-drawn tolerance, and price at 100 mm lengths.
- Ni and Si powder cuts for pressing; Si 45-106 um; combustible-dust shipping.
- (standard) Preventive-maintenance schedule (intervals, hours, who does it) and what a visit costs.
- (standard) Consumables and spares we should hold, with part numbers and prices.
- (standard) Price of a service contract (annual), what it covers, and the response time to Utah **[to confirm site]**.
- (standard) Lead time, installation and training scope, warranty, and academic or government pricing.

### 5. Their intake questions, answered
Materials: reactive Al fines; Si/Ni powders go in a cup; NFPA 484 handling. Batch: 4 cups a run, about 700 runs, so about 2,800 cups a year.

Standard answers shared by every vendor are in the [common answers](#common-answers); site facts are in [`lab_answers.md`](lab_answers.md).

### 6. Draft email
**To:** inq@goodfellow.com
**Subject:** Quote: 5N Al rod 20 mm and 12 mm x 100 mm, and OFE copper C10100

> Hello,
>
> We want a quote for 5N Al rod (20 mm and 12 mm OD x 100 mm) and OFE copper C10100 in the same sizes, for charge cups.
>
> Facts:
> - Qty: 48 cups' worth of each, about 2,800 a year at full rate **[to confirm first order]**.
> - Please send GDMS certificates.
> - Ship to Utah **[to confirm]**.
>
> Questions:
> 1. 5N rod tolerance on a 20 mm OD; lot certificates (GDMS) and an oxygen figure; tighter-tolerance ground stock.
> 2. OFE C10100 20 mm and 12 mm rod, ASTM B187/B301, as-drawn tolerance, and price at 100 mm lengths.
> 3. Ni and Si powder cuts for pressing; Si 45-106 um; combustible-dust shipping.
>
> Please also send: the preventive-maintenance schedule; consumables and spares with part numbers and prices; the annual service-contract price and response time; lead time, installation and training, warranty and academic pricing.
>
> The BYU Vertical Cloud Lab (institution, ship-to address, utilities and timeline: see the lab's answers sheet) **[sender name, title, phone to confirm]**.
>
> Thank you.

### 7. Sources (checked 2026-11-07 UTC)
- https://www.goodfellow.com/usa/contact-us (fetched via the stream-cam Pi)
- https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152 (WebFetch/WebSearch from the runner)
- https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/162 (WebFetch/WebSearch from the runner)
- https://en.wikipedia.org/wiki/AlSi10Mg (2026-11-07, search snippet)

## Superseded or discontinued (model check, 2026-11-07)

| Item | Modelled | Status | Successor | Source |
| --- | --- | --- | --- | --- |
| 4. Sieve cleaning | Branson CPX baths: 230 V "-E" versions and some CPX/CPXH 5800 and 8800 part numbers | discontinued per distributors (Branson still lists the CPX line) | 120 V CPX2800H still sold; other replacements are linked by distributors, not named | https://www.itm.com/product/branson-cpx-952-238r-cpxh-2800-ultrasonic-bath-digital-timer-with-heat-0-7-gal-2-8-l |
| 12. Sample prep | Buehler VibroMet 2 (67-1635-160 / -250) | discontinued (Buehler's own page) | Buehler VibroMet 3, 67-2105, 100-240 V; size and weight not published | https://www.buehler.com/products/grinding-and-polishing/vibratory-polishers/vibromet-2-vibratory-polisher/ |
| 14. DED and repair | Meltio M450 | superseded (no formal end-of-life notice found) | Meltio M600: 300 x 400 x 600 mm build, 1,050 x 1,050 x 1,950 mm, 800-1,000 kg, 3-phase 400 V, chiller | https://meltio3d.com/products/meltio-m450/ |
| 16. SnowX | SnowPod | unconfirmed: not yet released (Kickstarter early-bird, launch Q4 2026, no ship date) | none | https://www.3dnatives.com/en/desktop-metal-3d-printer-snowpod-22102026/ |

Everything else in this file is current as of 2026-11-07; see each section's Model check bullet.

## Gaps

Second pass (2026-11-07): each contact was re-read on the vendor's own page, from the runner first and from the stream-cam Pi where the runner was blocked; the "Contact status" line under each Section 3 and the `contact_status` columns of `production.csv` record the result.

- Corrections: FANUC America phone is 888-326-8287 (the first pass had 888-326-8723). Specac's sales@specac.com is not on its pages (use uscs@specac.com or sales@specac.co.uk). The Retsch/QATM email info-us@verder-scientific.com is now confirmed on the Verder US page. Valimet's phone and email are now confirmed on its own page.
- No verified sales email: EOS, Opulo, Meltio, FANUC (web forms only); Aconity US (AconityUS has no contact on Aconity's own site); Bambu Lab has no phone.
- Still unverified (site blocked or content not readable): Bambu Lab (403 / Cloudflare challenge on the runner, the Pi and headless Chromium), Online Metals and American Elements (403), Fiber Optic Center (403), the Branson phone and HQ move, McMaster chi.sales@, LECO info@ (obscured).
- US regional reps for Utah remain unconfirmed because the vendor pages publish none or load them only after a selection: LECO, Buehler (state selector), DDM (representative finder), QATM/Retsch (Verder routes by form), EOS, Aconity, FANUC (ask Methods' Rocky Mountains line +1 602-848-1221 whether it covers Utah). Confirmed Utah-relevant: NB Additive (Solukon), GoEngineer Midvale UT (Formlabs).
- Blower vendor for the sieve air-knife alternative still not chosen (Gast Manufacturing, +1 269-926-6171, is a lead only).
- Specs not found: PX500 power, Aconity MIDI power, VibroMet 2 size, OFE copper price, Bambu A2L.

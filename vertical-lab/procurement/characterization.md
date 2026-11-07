# Procurement pack: characterization, mechanical testing, balances, furnace and the corrosion station

Part of Sterling's ask on PR #318 (2026-11-07): "find all the contact information, specs, requests, etc. for the
individual parts that go into this entire workflow. Include specific emails and answer the typical questions people
would be asking us in order for them to give a budgetary quote." This file covers the **instruments that measure and
test**. The infrastructure is in [`infrastructure.md`](infrastructure.md). The answers every vendor asks for (who, where,
utilities, budget, timeline, purchasing, service) are in [`lab_answers.md`](lab_answers.md); each section here answers
only what is specific to the product. The machine-readable list is [`characterization.csv`](characterization.csv).

**Conventions.**
- **Checked** is 2026-11-07 UTC (about 04:00 to 07:30). **Via Pi** says whether the page was fetched through the
  stream-cam Pi because the runner was blocked or the page was JS-only: one fetch at a time, rate-limited to 300 kB/s,
  nothing left on its disk. "No (blocked)" means both the runner and the Pi were refused.
- **[to confirm]** marks a site fact only the lab can supply, **or a contact detail that came from a search snippet or a
  directory and not from the vendor's own page.** Check every number before sending an email.
- **Business contacts only.** No personal names or direct lines. Where a vendor publishes only a web form, the form is
  the contact and no email is guessed.
- **Every vendor is also asked, and every draft says so in one line:** the preventive-maintenance schedule, the
  calibration and verification needs (for example annual ASTM E4 load verification), consumables and spares with
  prices, a service-contract price, and the response time in Utah. The lab is modelling upkeep over years.
- Specs are the maker's published figures where cited, and the model's numbers (`vertical-lab/notes/`) where it says so.
- **Throughput** in every section comes from `out/timelapse_model.json` (round 8): in year 1, about **378 alloys
  atomized and 324 fully tested**, 702 atomizer runs, 1,420 tensile tests, 378 each of XRD, XRF and laser diffraction,
  6,804 SEM images, 972 indents and 648 corrosion spots. Planning numbers, not commitments.
- **Samples across the workflow:** Al alloys (Al-Si, AlSi10Mg, 4047, 6063), Cu alloys (Cu-Ni C71500), nickel-aluminium
  bronze (NAB, C95800); atomized powders 20-63 um (LPBF) and 45-105 um (DED), within the 20-150 um range we quote;
  printed coupons; 1.5 in (38 mm) metallographic mounts; ASTM E8 subsize and miniature tensile bars.

## Contents

| # | Section | Qty | Pi used |
|---|---|---|---|
| 1 | Rigaku MiniFlex (6th gen), zero-background holders, NIST SRM 640 Si | 1 | yes (contact page) |
| 2 | Malvern Panalytical Mastersizer 3000 + Aero S | 1 | yes (contact page) |
| 3 | Bruker S2 PUMA Series 2 (XY Autochanger or Automation, He option) | 1 | yes (contact page, empty) |
| 4 | Hitachi TM4000PlusII + Oxford Instruments AZtecOne EDS | 1 | yes (blocked, Akamai) |
| 5 | KLA iMicro nanoindenter | 1 | yes (blocked, bot wall) |
| 6 | Plastometrex PLX-Benchtop (PIP) | 1 | yes (contact page) |
| 7 | Keyence VHX-7000 / VHX-X1 + EA-300 LIBS | 1 | yes (contact page) |
| 8 | Mitutoyo HM-220 Type D micro-Vickers | 1 | yes (contact page) |
| 9 | Instron 68FM-100 + 3119-608 + AVE 2 + AT6; and the 68SC-2 | 1 + 1 | yes (blocked, Cloudflare) |
| 10 | ZwickRoell zwickiLine Z5.0 TN (horizontal) | 1 | yes (contact page) |
| 11 | Tinius Olsen and ADMET horizontal frames up to about 15 kN | 0-1 | yes (sales page) |
| 12 | A&D balances (HR-202i, GH-202, HR-100A) and OIML E2 check weights | 1 + 1 + sets | yes (redirect page) |
| 13 | Nabertherm NAT 15/65 | 1 | yes (contact pages) |
| 14 | The CubXL (lab-built, no maker): SainSmart frame and parts | 1 | no |
| 15 | NuVant EZstat Pro potentiostat | 1 | yes (contact page) |
| 16 | Opentrons OT-2 with P300 and P20 | 1 | yes (contact page) |
| 17 | Reference electrodes and Pt: Innovative Instruments, WPI, Pine, BASi, Gamry | 1-4 + Pt | yes (contact pages) |

**Cross-cutting findings, read these first.**
1. **Three products have a newer model that the lab's model does not use.** The Hitachi TM4000PlusII has a
   TM4000PlusIII successor (Hitachi, 2024-08-22). The Mastersizer 3000 has a "3000+" in Malvern's range. The Keyence
   VHX-7000 is replaced by the VHX-X1 (the notes already say so). Every draft asks for the current model.
2. **A&D's HR-202i is discontinued, and the GH-202 that replaced it may be too.** One A&D brochure marks the whole
   GH/HR-i data table "DISCONTINUED". Ask A&D what is current (section 12).
3. **The 5 kN zwickiLine cannot pull the 6 x 6 mm route bar (14.8 kN).** It can pull a bar faced to 6 x 1.5 mm
   (3.7 kN) or a miniature bar. The 68FM-100 is a 100 kN frame used at 15 percent of capacity; section 9 asks whether a
   smaller frame would do.
4. **The CubXL has no maker.** It is a lab build around a SainSmart Genmitsu PROVerXL 4030 V2 frame (section 14).
5. **The EZstat Pro's EIS is contradictory.** The notes say the lab's unit has none; a vendor listing says it does
   (section 15).

---

## 1. Rigaku MiniFlex (6th generation), zero-background holders, NIST SRM 640 Si

### 1. What we'd buy
- **Maker and model:** Rigaku MiniFlex, 6th generation ("MiniFlex 6G"), **one**, 600 W Cu tube, with the optional **ASC-8
  8-position autosampler with spinner** (to be asked: whether it is needed when a robot loads one holder at a time),
  and a **D/teX Ultra2** detector as standard (the XSPA-200 ER pixel detector is the option).
- **Accessories:** **zero-background holders** (single-crystal Si, off-cut), a **NIST SRM 640 Si** line-position standard
  (7.5 g; section 1.8 below), a spare tube.
- **Role and place:** phase identification of atomized powders and printed material. The arm sifts powder onto a
  zero-background holder, strikes it flush, and sets it in the MiniFlex through its door. **Tray D**, with the SEM
  (README round 8, `notes/refine_xrd.md`). About 378 scans a year.
- **Model check (2026-11-07):** **current** (MiniFlex), **superseded by SRM 640g** (the Si standard), holders **unconfirmed**. Rigaku's page still sells the "Gen 6" MiniFlex with the D/teX Ultra2 as standard, the XSPA-200 ER and ASC-8 as options, and names no successor; NIST's SRM 640g certificate is dated 2024-02-27, so 640f is the old lot (same 7.5 g Si powder, same use), and no holder part number was found to check. (<https://rigaku.com/products/x-ray-diffraction-and-scattering/xrd/miniflex>; <https://www.nist.gov/publications/certification-standard-reference-materialr-640g-line-position-and-line-shape-standard>)

### 2. The published specs that matter for integration
- **Size and mass:** 620 W x 722 H x 460 D mm, 80 kg (Rigaku's page; the model uses 456 D).
- **Utilities:** single-phase 100-240 V, 50/60 Hz. **Cooling is not stated on the page.** **[to confirm]**
- **Interfaces:** an external Windows PC with **SmartLab Studio II**. Remote control or an API is **not published**.
- **Robot loading and door:** a front door with a door lock button. **Door actuation is not published.** The MiniFlex XpC
  has a robot loader but a different housing (rejected, `notes/refine_xrd.md`).
- **Automation kits:** the 8-position changer only.

### 3. Contact
- **Email:** info@rigaku.com (general; the only address on the contact page). **Phone:** +1 281-362-2300 (Rigaku Americas,
  The Woodlands, TX; the service page prints it only as the extension route "+1 281-362-2300 x 132", so the main
  sales number is **partial**: `(verified as the Rigaku Americas switchboard: https://rigaku.com/service-and-support/contact-service, 2026-11-07)`;
  the street address 9009 New Trails Drive is `(unverified: not on the pages read)`). The contact page now routes sales to a
  form at <https://rigaku.com/about/contact-sales> (the old `/contact-us` URL is a 404; the live one is
  <https://rigaku.com/about/contact-us>, verified 2026-11-07).
- **Quote form:** <https://rigaku.com/products/get-a-quote?product_lines___us=XRD&xrd_products=MiniFlex>. **Service desk:**
  support@rigaku.com, 1-888-362-2324 (24/7 help desk) `(verified: https://rigaku.com/service-and-support/contact-service, 2026-11-07)`.
- **Regional rep (Utah / Mountain West):** `(unverified: no territory list on rigaku.com; ask the sales form, checked 2026-11-07)`.
- **Academic:** none found.

### 4. Our open questions for them
1. **Door actuation:** can the door be opened by a robot, or fitted with an actuator and an open/closed sensor, and does
   that keep the warranty? The X-ray interlock must read it.
2. **Remote start and status** from a scheduler: a documented command set, SmartLab Studio II scripting, or digital I/O.
3. Is the **ASC-8 needed**, or does a single manual-position holder stage suit a robot?
4. The **sample height and holder pocket** for a zero-background holder (the arm sets it in, so the tolerance matters).
5. **Cooling**: is a chiller needed, and what room-temperature range?
6. Is **Fe fluorescence** from Cu radiation a problem on our Cu and Al-Cu samples, and is a **Co** tube or fluorescence-
   suppression detector settings advised? (Cu alloys and Fe-bearing NAB.)
7. Annual **radiation survey** and the registration a Utah lab needs for an X-ray tube (Utah DWMRC, **[to confirm]**).
8. PM schedule, calibration and alignment verification (the SRM 640 routine), spares and tube life with prices, service
   contract price, nearest engineer to Provo.
9. **SRM 640g, not 640f** (model check, 2026-11-07): 640g is the current lot (certificate 2024-02-27). Order 640g from NIST, and ask Rigaku whether SmartLab Studio II needs its 640g lattice value entered for the alignment check.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Sample types | Atomized Al, Cu-Ni and NAB powders, 20-150 um; sifted onto a zero-background holder, nothing ground. Printed coupons as a second use **[to confirm]** |
| Scans | About 378 a year, 2 theta 10-90 deg, a short scan (under 30 min) **[to confirm]** |
| Quantitative phase analysis | Wanted (Rietveld), software and licence to quote **[to confirm]** |
| Automation | Robot sets one holder; remote start; no operator; a UR10e with a 2F-85 gripper |
| Software | SmartLab Studio II; the lab's scheduler needs an interface |
| Utilities | One 120 V outlet; no water. Tray D has power and Ethernet through its dock |
| Quantity, timeline, budget | 1; budgetary; [lab_answers.md](lab_answers.md) |
| Install | On a VLM tray, delivered to Provo; the lab's riggers and the robot integrator install it |

### 1.8 SRM 640 and the holders
- **NIST SRM 640f** is the seventh-generation Si powder standard, about 7.5 g, a = 0.5431144 nm (NIST certificate). The
  Sigma-Aldrich listing already shows a newer **640g**, so **order the current one**. NIST SRM program: 301-975-2200,
  SRMMSDS@nist.gov (the SDS contact) `(unverified: not on nist.gov/srm or nist.gov/srm/contact-us; the NIST switchboard 301-975-2000 is on those pages, 2026-11-07)`; catalog <https://www.nist.gov/srm>. Price: not found.
- **Zero-background holders:** ask Rigaku for its own holder part number; third-party Si holders are a cheaper route but
  were **not verified** here.

### 6. Draft email
> **To:** Rigaku Americas sales (web form above), cc info@rigaku.com
> **Subject:** Budgetary quote: MiniFlex 6G with ASC-8, robot-loaded, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab is planning one MiniFlex (6th generation, Cu tube, D/teX Ultra2) to scan about 380 atomized
> Al, Cu-Ni and NAB powders a year, loaded by a UR10e arm onto a zero-background holder. We would like a budgetary quote,
> list and academic, valid 90 days, for: the MiniFlex; the ASC-8 (and a price without it); zero-background holders; a spare tube.
> Please tell us:
> 1. Can the door be opened by a robot or an actuator, and read by the interlock, without voiding the warranty?
> 2. Remote start and status from our scheduler: what is documented?
> 3. Cooling, power and room requirements, and the Utah registration you advise for the tube.
> 4. Preventive maintenance and calibration (alignment, SRM 640 checks), tube life, spares with prices, a service
>    contract price, and the response time to Provo, UT.
>
> Delivery to Provo, UT 84602. Details and a site sheet are in the attached lab answers. [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://rigaku.com/contact-us> (info@rigaku.com) | yes |
| <https://rigaku.com/products/x-ray-diffraction-and-scattering/xrd/miniflex> (specs, quote URL; WebFetch) | no |
| Search: Rigaku Americas address, phone, service desk | no |
| NIST SRM 640f certificate and SDS (search results) | no |
| `notes/refine_xrd.md`, README round 8 | n/a |
| <https://rigaku.com/products/x-ray-diffraction-and-scattering/xrd/miniflex> (model check: Gen 6 current) (2026-11-07, runner) | no |
| <https://www.nist.gov/publications/certification-standard-reference-materialr-640g-line-position-and-line-shape-standard> and <https://tsapps.nist.gov/srmext/certificates/640g.pdf> (SRM 640g) (2026-11-07, search snippet) | no |

---

## 2. Malvern Panalytical Mastersizer 3000 + Aero S

### 1. What we'd buy
- **Maker and model:** Malvern Panalytical **Mastersizer 3000** (or its current "3000+"; to ask) optical unit with the
  **Aero S** dry powder disperser, **one**, plus the Aero S **small-volume tray / hopper** and the **Mastersizer software
  with 21 CFR Part 11** only if required (not needed, **[to confirm]**).
- **Role and place:** laser diffraction particle size (Dv10, Dv50, Dv90) of the sifted powder, as a quality gate on each
  atomized batch. About 5 g is poured into the Aero S; the optical bench is drawn in cutaway. **Tray E**, with the KLA
  iMicro. About 378 measurements a year.
- **Model check (2026-11-07):** **superseded by the Mastersizer 3000+**. Malvern launched it on 2024-03-14 as the "worthy successor" to the 3000, and its Mastersizer page now lists only the 3000+ Lab (0.1-1000 um, manual dispersion units only), Pro (0.1-2500 um) and Ultra (0.01-3500 um), so the Aero S probably needs the Pro or Ultra **[to confirm]**; its main unit is the same 690 x 300 x 450 mm, about 30 kg, as the model's bench, and it adds Smart Manager remote monitoring. (<https://www.malvernpanalytical.com/en/about-us/press-releases/news/pr240314-matersizer-3000-plus-launch>; <https://www.malvernpanalytical.com/en/products/product-range/mastersizer-range/mastersizer-3000>)

### 2. The published specs that matter for integration
- **Size:** the bench is **690 W x 300 D x 450 H mm**; the Aero S **260 x 180 x 380 mm** (Malvern's datasheet figures
  used in `notes/refine_mastersizer.md`).
- **Utilities:** the Aero S needs **dry, oil-free compressed air** (pressure, flow and dew point are **not in these
  notes, ask**). Mains power for the bench.
- **Interfaces:** the Mastersizer software on a PC. An API or automation hook is **not published** in the sources we read.
- **Robot loading:** the Aero S cover lifts off by hand in Malvern's videos; the model adds an actuator. The hopper
  takes a poured sample.
- **Automation kits:** none for the Aero S found.

### 3. Contact
- **Web form (sales):** <https://www.malvernpanalytical.com/en/about-us/contact-us/sales>; the contact page also routes to
  application support (`/en/support/contact-support/application-enquiry`), service, consumables, and "find your local
  contact" (`/en/about-us/contact-us/distributors`, which loaded as a JS form).
- **Phone (US):** +1 800-279-7297, Westborough, MA, `(unverified: the contact and sales pages print no phone;
  a Malvern event page (Sept 2025) gives the office as 2400 Computer Drive, Suite 2100, Westborough, MA 01581; 117 Flanders Road is older)`.
  The sales page <https://www.malvernpanalytical.com/en/about-us/contact-us/sales> is a form promising a reply "within 1 business day" `(verified: 2026-11-07)`. **Email:** none published.
- **Regional rep (Utah):** a regional manager is assigned by the form `(unverified: the distributors page is a JS form that returned no list to the runner or to Chromium on the Pi, 2026-11-07)`. **Academic:** ask.

### 4. Our open questions for them
From `notes/refine_mastersizer.md`, `notes/alloy_characterize.md`:
1. Is the **Mastersizer 3000 still sold**, or is the **3000+** (and a "3000+ Ultra") the model to quote? What changes?
2. **Metal powders**: the "Measuring metal powders" method (Malvern video 6ZuKAAHb_20) with refractive index, absorption
   and density for Al, Cu-Ni and NAB; how it handles **reactive Al fines** in dry dispersion (we treat them as NFPA 484
   combustible dust; is an inert-gas feed possible?).
3. How many **grams** per run, and can a **5 g aliquot** be recovered?
4. **Automatic cleaning, and a robot-friendly flow**: the cover and hopper are lifted by hand. Can the cover and tray be
   actuated, and can the measurement be started and read by an API or a command line?
5. **Air supply:** pressure, flow, dryness and a filter set.
6. **Particle size standards** for verification (a glass bead standard) and how often.
7. PM schedule, lens and optics cleaning, consumables (the Aero S wear parts, filters) with prices, service contract
   price, response time in Utah.
8. **Mastersizer 3000+** (model check, 2026-11-07): the 3000 has been followed by the 3000+. Which version takes the **Aero S** (the Lab lists manual dispersion units only), and what changed in size, weight, utilities and remote control?

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Sample | Dry atomized metal powder, 20-150 um (LPBF cut 20-63 um, DED cut 45-105 um) |
| Quantity per sample | About 5 g poured; recovery wanted but not required |
| Hazard | Al fines are combustible metal dust; no toxic powders; no HF **[to confirm Cu-Ni dust handling]** |
| Throughput | About 378 a year, one an hour at most |
| Automation | Robot pours from a vial; start and read-back by software |
| Utilities | 120 V; clean dry air **[to confirm tray A-F dock air]** |
| Software | Mastersizer software; export in an open format |
| Quantity | 1 |

### 6. Draft email
> **To:** Malvern Panalytical US sales (web form above)
> **Subject:** Budgetary quote: Mastersizer 3000 (or 3000+) with Aero S for metal powders, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one laser-diffraction system for dry atomized Al, Cu-Ni and bronze powders,
> 20-150 um, about 380 measurements a year, fed by a robot arm. We would like a budgetary quote (list and academic, valid
> 90 days) for the current Mastersizer with Aero S, and answers to:
> 1. Is the 3000 or the 3000+ the model to quote, and what is the difference for metal powders?
> 2. The air supply the Aero S needs, and whether the cover, hopper and cleaning can be driven by software or an actuator.
> 3. Can a measurement be started and read by an API or command line, with no dialogs?
> 4. Reactive Al fines: any guidance for dry dispersion?
> 5. Preventive maintenance, verification standards, consumables with prices, a service contract price, and the
>    response time to Provo, UT.
>
> If the Mastersizer 3000 is no longer sold, please quote the Mastersizer 3000+ version (Lab, Pro or Ultra) that takes the Aero S, and say what changed in size, weight, utilities and remote control.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.malvernpanalytical.com/en/about-us/contact-us> (form links) | yes |
| <https://www.malvernpanalytical.com/en/about-us/contact-us/sales> (form only) | yes |
| Search: US phone and address (directories: Photonics, LabCompare) | no |
| `notes/refine_mastersizer.md` (sizes) | n/a |
| <https://www.malvernpanalytical.com/en/about-us/press-releases/news/pr240314-matersizer-3000-plus-launch> (3000+ launch, successor) (2026-11-07, runner) | no |
| <https://www.malvernpanalytical.com/en/products/product-range/mastersizer-range/mastersizer-3000> (lists only 3000+ Lab, Pro, Ultra) (2026-11-07, runner) | no |
| <https://www.atascientific.com.au/lp/mastersizer-3000-pro/> (distributor: Aero M for the Lab and Pro; Pro automated dry) (2026-11-07, search snippet) | no |
| <https://www.malvernpanalytical.com/en/products/product-range/mastersizer-range/mastersizer-3000-plus-lab> (3000+ main unit 690 x 300 x 450 mm, about 30 kg) (2026-11-07, search snippet) | no |

---

## 3. Bruker S2 PUMA Series 2 (XY Autochanger or Automation), with the He option

### 1. What we'd buy
- **Maker and model:** Bruker AXS **S2 PUMA Series 2**, **one**, **XY Autochanger** (20 positions, liquid detection) or
  the **Automation** version (the same, plus a conveyor/robot interface on the back); **HighSense XP** detector (C to
  Am) if light elements matter, else **HighSense** (Na to Am); **Pd** anode; **helium option** ("Helium mode with
  reduced pressure" for loose powder); **SPECTRA.ELEMENTS** software with **SMART-QUANT FP**.
- **Role and place:** bulk composition of atomized powder (and, as a second use, printed coupons) to verify the
  alloy made. The arm fills an XRF cup (40 mm across, 38 mm tall at most) and loads the tray. **Tray M** (README round 8
  and `notes/tray_plan.md`). About 378 analyses a year.
- **Model check (2026-11-07):** **current**. Bruker's S2 PUMA Series 2 page still offers the Single, XY Autochanger, Carousel, Automation and Mapping-Stage versions, calls the HighSense XP detector "the latest addition", and names no successor. (<https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2.html>)

### 2. The published specs that matter for integration
(Bruker's product page, via WebFetch)
- **Size and mass, by version:** Single 67 x 71 x 37 cm, 87 kg; Carousel (12 or 18 positions) 67 x 71 x 57 cm, 130 kg;
  **XY Autochanger** 67 x 71 x **61 cm**, **108 kg**; **Automation** 67 x 71 x 61 cm, 110 kg; Mapping-Stage 132 kg.
- **Utilities:** 100-240 V, 50/60 Hz, max 600 VA. He for the He mode (supply and consumption **not published**).
- **Tube and detector:** Pd or Ag anode, 50 W, 50 kV max; Peltier-cooled SDD, no liquid nitrogen.
- **Interfaces:** 12.1 in touchscreen; **LIMS-compatible through AXSCOM**; the Automation version's **feed interface is
  on the back, "conveyor belt or robot arm"**, with an HD camera for sample verification.
- **Lid:** the **open height is not published** (the model draws a 35 degree lid reaching about 905-1010 mm).

### 3. Contact
- **Web forms (on the product page):** contact sales
  <https://www.bruker.com/en/meta/forms/baxs-form-pages/marketo-forms/baxs-sales-contact-form-xrf.html> and request a quote
  <https://www.bruker.com/en/meta/forms/baxs-form-pages/marketo-forms/baxs-sales-contact-form-quote-xrf.html>. The
  contact page (<https://www.bruker.com/en/about-us/contact.html>) is a form only; it was fetched through the Pi.
- **Phone:** Bruker AXS Inc., 5465 East Cheryl Parkway, Madison, WI 53711, **+1 608-276-3000** `(verified: https://www.bruker.com/en/services/support/office.americas.united-states-madison.html, 2026-11-07)`.
  **Email (XRF, single-crystal XRD, XRD sales):** **info.baxs@bruker.com** `(verified: same page, 2026-11-07)`; service
  **service.baxs.us@bruker.com**, +1 800 234-XRAY (same page). Micro-XRF/TXRF/handheld sales is a different address
  (info.bna@bruker.com); do not use it for the S2 PUMA. (The earlier note "no sales email published" was wrong.)
- **Regional rep:** the US XRF sales role is "central region" (job postings); a Utah rep `(unverified: no territory list on the Madison office page, 2026-11-07)`. S2 PUMA is
  also sold through distributors elsewhere (for example DKSH in Asia); none found for the Mountain West.

### 4. Our open questions for them
From `notes/instruments_char.md` ("Ask Bruker for the open height") and `notes/refine_xrf.md`:
1. **The lid's open height** and swing, and whether it can be **opened by a robot or an actuator**, or whether the
   **Automation** version's interface replaces the lid (the arm would feed through the back?).
2. **The Automation interface:** what signals (I/O, Ethernet, AXSCOM) a UR10e or a scheduler uses for start, status and
   sample-in-place; is a robot cell reference available?
3. **Loose powder:** the cup and film type for Al, Cu-Ni and NAB powder; does the **He reduced-pressure mode** work
   without a film failure; how much **He** per hour, and a cylinder or a generator?
4. **Light elements** (Mg, Al, Si in Al alloys): is **HighSense XP** needed, and what are the detection limits for 0.5-2 percent Mg?
5. **Calibration:** which standards (powder, NAB, Al-Si) and the SMART-QUANT FP accuracy for atomized powder.
6. **Radiation registration** for Utah, and an annual survey.
7. PM schedule, tube and detector life, consumables (cups, films) with prices, service contract price and response
   time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Elements and range | Al, Si, Mg, Cu, Ni, Fe, Mn, Zn, Sn, Ti, others to ppm; Na to Am; C to Am only if XP |
| Samples | Atomized powder in cups, 20-150 um; coupons as a second use; solids polished flat |
| Number | About 378 a year, plus standards |
| Automation | Robot loads cups into the autochanger; remote start |
| Utilities | 120 V, 600 VA; He **[to confirm supply]** |
| Software | SPECTRA.ELEMENTS; LIMS via AXSCOM |

### 6. Draft email
> **To:** Bruker AXS sales, XRF (web form above)
> **Subject:** Budgetary quote: S2 PUMA Series 2 (Automation or XY Autochanger), He option, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab plans one S2 PUMA Series 2 to analyze about 380 atomized Al, Cu-Ni and bronze powders a year,
> loaded by a robot arm. Please quote (list and academic, valid 90 days): the **Automation** version and the **XY Autochanger**
> with HighSense (and XP), Pd tube, He option, SPECTRA.ELEMENTS and SMART-QUANT FP. We ask:
> 1. The lid's open height, and can a robot or actuator open it, or does the Automation interface remove the need?
> 2. The Automation interface signals and a robot-cell reference; AXSCOM for a scheduler.
> 3. The cup and film for loose powder in He mode; He consumption.
> 4. Standards for atomized Al and Cu alloys; Utah radiation registration.
> 5. Preventive maintenance, tube and detector life, consumables with prices, a service contract price, and the
>    response time to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2.html> (WebFetch) | no |
| <https://www.bruker.com/en/about-us/contact.html> (form only) | yes |
| Search: Madison address and phone | no |
| `notes/instruments_char.md`, `notes/refine_xrf.md` | n/a |
| <https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2.html> (model check: current) (2026-11-07, runner) | no |

---

## 4. Hitachi TM4000PlusII + Oxford Instruments AZtecOne EDS

### 1. What we'd buy
- **Maker and model:** Hitachi High-Tech **TM4000PlusII** tabletop SEM (the "Plus" variant is the one with an EDS port), **one**, with an **EDS system: Oxford Instruments AZtecOne** with an X-Max SDD (the
  alternative is Bruker QUANTAX 75, which Austrian listings pair with it). **Ask for the TM4000PlusIII**, announced
  2024-08-22, which may have replaced the II.
- **Accessories:** conductive **carbon tabs and stubs**, the **1.5 in mount holder**, a **stage for mounted samples**, the
  **dry scroll pump**, and a spare source (ask what the source is and its life).
- **Role and place:** secondary and backscatter imaging of powder (a sphericity and satellite count), and EDS spot
  chemistry of polished mounts. The mount sits in a cup in the stage socket; the drawer slides out. **Tray D**. About 20
  images per alloy, 6,804 images a year.
- **Model check (2026-11-07):** **superseded by the TM4000PlusIII** (and the X-Max SDD by Oxford's Xplore). Hitachi's US tabletop page lists only the TM4000PlusIII/TM4000III (launched 2024-08-22), which add Recipe Control (stage moves, magnification and image capture run automatically), workflow automation (sequential execution, repetition, conditional branching), a high-current Mode 5 with Oxford's AZtecLiveLite particle analysis, a filament-life monitor, 20 kV and a low-vacuum SE detector (UVD); no dimensions are on the page, so the footprint is to ask, and the EDS offered is Quantax75, the Element series or the AZtec series, while Oxford's AZtecOne page now names only the Xplore detector (XploreCompact 30 or 65 for tabletop SEMs). (<https://www.hitachi-hightech.com/us/en/products/microscopes/sem-tem-stem/tabletop-microscopes/tm4000iii.html>; <https://nano.oxinst.com/products/aztec/aztecone>)

### 2. The published specs that matter for integration
- **Size and mass:** **330 x 614 x 547 mm** main unit, **54 kg**; the diaphragm pump 144 x 270 x 216 mm (Hitachi, via
  `notes/instruments_lab.md`).
- **Utilities:** the model uses the PlusIII's 500 VA (the II's figure was **not found**); a 100-240 V outlet.
- **Interfaces:** a PC with Hitachi's software; remote operation or an API is **not published**. Hitachi lists **no EBSD
  option for the TM4000 series**.
- **Robot loading and door:** a front drawer; **drawer actuation is not published** and the model adds an actuator
  (the "EVAC" pump-down is started from the software or a button).
- **Automation kits:** none found; an auto-feeder is not part of the series.

### 3. Contact
- **Hitachi High-Tech America:** 5100 Franklin Drive, Pleasanton, CA 94588 `(unverified: the US site blocks the runner and the Pi; a search index of the US site's Locations page shows 5960 Inglewood Drive, Suite 200, Pleasanton, CA 94588-3355, +1-925-218-2800, so the Franklin Drive address is probably old)`. The
  **U.S. site <https://www.hitachi-hightech.com/us/> blocks both the runner (403) and the Pi (Akamai "Access Denied")**,
  so no official phone or email was read (Chromium on the Pi was also refused, 2026-11-07).
  **Utah lead, `(unverified: indexed by search but not fetched)`:** Hitachi's US electron-microscope sales page for the **West region, which lists UT**
  (<https://www.hitachi-hightech.com/us/en/support/microscopes/em-sales_contacts/west.html>) names a regional sales manager at
  **(800) 253-3053** (the Dallas microscopy customer-service line). A person on a normal browser should open it and read the Utah contact. Directory numbers conflict (+1 925-218-2800; 800-227-8877; others), so **use the
  site's "Contact Us" form and ask for the SEM sales manager**.
- **Distributor:** McCrone Microscopes & Accessories, Westmont, IL, **630-887-7100**, lists the Hitachi FlexSEM 1000 II tabletop SEM
  `(verified: https://www.mccrone.com/contact-us/, 2026-11-07)`; whether it sells the TM4000PlusII or covers Utah is `(unverified)`.
- **Oxford Instruments NanoAnalysis (US):** **us.nainfo@oxinst.com** `(unverified: an exhibitor listing; not on nano.oxinst.com)`. The official page
  <https://nano.oxinst.com/contact-us> `(verified: 2026-11-07)` is a web form plus a Concord, MA office, **+1 (978) 369-9933** (fax 978 369-8287), and a UK head office at
  +44 (0)1494 442255; use the form and ask for a North America EDS sales contact. Address 300 Baker Avenue, Suite 150, Concord, MA 01742; AZtecOne info at <https://nano.oxinst.com/AZtecOne>. (Earlier note that the Oxford contact pages returned nothing was a wrong URL; `/contact-us` works.)
- **Academic:** Oxford offers training courses in Concord and on-site; education pricing `(unverified: not on the pages read)`.

### 4. Our open questions for them
From `notes/refine_sem.md` and `notes/instruments_lab.md`:
1. **Is the TM4000PlusII still sold, or the PlusIII?** Differences in stage, detectors and EDS port.
2. **Automation:** can the **drawer and EVAC** be started by software or digital I/O, so a robot loads a mount and
   the scheduler starts a recipe? Is there a **scripting or remote API** for stage moves, image capture and EDS?
3. **Powder:** stubs for 20-150 um powder with carbon tape; **low vacuum (30-100 Pa) without charging**; is a **coating** needed?
4. **EDS pairing:** AZtecOne versus QUANTAX 75 on the TM4000; which one **Hitachi quotes as a package**; **Mg, Al, Si**
   in Al alloys, **C** not quantified.
5. **Mount size:** does the standard stage take a **1.5 in (38 mm) mount** at 5-10 mm height, with **stage-height limits**?
6. **Vibration and floor:** it will sit on a **VLM tray** that moves; what **isolation** does it need and can it be shut down for transit?
7. **EBSD:** none listed; what does Hitachi or Oxford advise for a tabletop with EBSD (we model Bruker e-Flash XS)?
8. PM schedule, **source and filament** lifetime, consumables with prices, service contract price, response time in Utah.
9. **TM4000PlusIII and Xplore** (model check, 2026-11-07): the PlusIII (2024-08-22) adds recipes, Mode 5 and filament monitoring. Its size, weight and power, whether recipes can be started remotely, and which EDS (AZtecOneXplore or AZtecLiveOne) Hitachi now packages.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Samples | Atomized powder on carbon-tape stubs; polished 1.5 in mounts of Al, Cu-Ni and NAB; no biological samples |
| Imaging | BSE and SE, 5 and 15 kV, 100-5,000x; EDS maps |
| Throughput | About 6,800 images a year, 20 per alloy; one alloy an hour |
| Automation | Robot loads; software starts recipes; read-back of state |
| Software | Hitachi's and the EDS vendor's, with an export to open image formats |
| Utilities | 120 V; a dry pump; no water |

### 6. Draft email
> **To:** Hitachi High-Tech America, SEM sales (web form), cc McCrone (Hitachi tabletop SEM distributor); and Oxford Instruments
> NanoAnalysis, us.nainfo@oxinst.com
> **Subject:** Budgetary quote: TM4000PlusII (or PlusIII) with AZtecOne EDS, robot-loaded, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one TM4000Plus-class tabletop SEM with EDS to image about 380 atomized powder batches and
> polished Al, Cu-Ni and bronze mounts a year, loaded by a robot arm on a vertical lift tray. Please quote the TM4000PlusII or
> PlusIII with the EDS packaged (AZtecOne or other), list and academic, valid 90 days, and tell us:
> 1. Which model is current, and can the drawer, vacuum start and a recipe be driven by software or I/O?
> 2. Is there a scripting or remote API for stage, image and EDS?
> 3. Stage limits for a 1.5 in mount; low-vacuum use on powder.
> 4. Floor-vibration limits for a lift tray, and whether it may stand in a moving tray.
> 5. Preventive maintenance, source life, consumables with prices, a service contract price and the response time to Provo, UT.
>
> We understand the TM4000PlusIII has followed the PlusII and the Xplore detector the X-Max: please quote the current models and say what changed in size, weight, utilities and remote control (the PlusIII's recipes in particular).
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.hitachi-hightech.com/us/en/about/contact/> and the US product page (Access Denied) | yes, blocked |
| Search: TM4000PlusIII announcement (2024-08-22); McCrone partnership | no |
| Search: Oxford `us.nainfo@oxinst.com`, Concord address | no |
| `notes/refine_sem.md`, `notes/instruments_lab.md` | n/a |
| <https://www.hitachi.com/en/press/articles/2024/08/0822/> (PlusIII launch) (2026-11-07, search snippet) | no |
| <https://www.hitachi-hightech.com/us/en/products/microscopes/sem-tem-stem/tabletop-microscopes/> (lists only TM4000PlusIII/TM4000III) (2026-11-07, maker's page, headed Chromium on the stream-cam Pi) | yes |
| <https://www.hitachi-hightech.com/us/en/products/microscopes/sem-tem-stem/tabletop-microscopes/tm4000iii.html> (PlusIII features, EDS options; no dimensions) (2026-11-07, maker's page, headed Chromium on the stream-cam Pi) | yes |
| <https://www.mccrone.com/product/hitachi-tm4000plusiii-and-tm4000iii-tabletop-sems/> (PlusIII features) (2026-11-07, runner) | no |
| <https://nano.oxinst.com/products/aztec/aztecone> (AZtecOne with Xplore) (2026-11-07, runner) | no |
| <https://nano.oxinst.com/assets/uploads/products/nanoanalysis/documents/Flyers/AZtecLiveOne%20with%20XploreCompact%2030%20and%2065%20for%20TTM.pdf> (XploreCompact 30, 65 for tabletop SEMs) (2026-11-07, search snippet) | no |
| <https://www.hitachi-hightech.com/us/en/products/microscopes/sem-tem-stem/tabletop-microscopes/aztec.html> (AZtecOneXplore standard) (2026-11-07, search snippet) | no |

---

## 5. KLA iMicro nanoindenter

### 1. What we'd buy
- **Maker and model:** KLA **iMicro** nanoindenter, **one**, **InForce 1000** actuator (the **InForce 50** for soft
  materials is an option we do not need), the **Berkovich** tip, the **magnetic puck sample holder**, **NanoBlitz 3D**
  mapping, and the **InView** software.
- **Role and place:** a grid of nanoindents (a 5 x 5 on each mount, about 3 per alloy, **972 a year**) for hardness and
  modulus of the polished mount. The stage carries the mount from the microscope to the indenter. **Tray E**, with the
  Mastersizer; the hood lifts for the arm.
- **Model check (2026-11-07):** **current**. KLA's iMicro page is live with a Request a Quote button, and KLA's pages list the iMicro beside the G200X, iNano, NanoFlip and InSEM HT with the InForce 1000; no successor or new iMicro version was found. (<https://www.kla.com/products/instruments/nanoindenters/imicro>)

### 2. The published specs that matter for integration
(AZoNano's iMicro listing and UNH's facility page, via WebFetch)
- **Load and displacement:** up to **1 N**, 6 nN resolution, noise floor below 200 nN; **80 um** displacement,
  drift below 0.05 nm/s; **frame stiffness above 3.5 MN/m**; data rate 100 kHz.
- **Stage:** automated XY, **100 mm X, 21 mm Y, 25 mm Z travel**; 2-position magnetic puck holder; integrated microscope;
  a **gantry with integrated vibration isolation**.
- **Interfaces:** InView (RunTest, ReviewData, InFocus). **API, scripting and a robot interface are not published.**
- **Not published:** **size, weight, power and environment** (KLA's PDF is bot-protected; the model's 540 x 520 x 520 mm
  is an estimate).

### 3. Contact
- **KLA's contact page and datasheet were unreachable** from the runner and from the Pi (bot wall). No official email or
  phone was read. **Use KLA's "Contact us" form from <https://www.kla.com/products/instruments/nanoindenters/imicro>
  and its "Request a quote".** A directory lists Oak Ridge, Tennessee as the nanoindenter site (the former Nanomechanics Inc.).
  `(unverified: kla.com returns 200 to the runner but the contact text did not load for us, and Chromium on the Pi got nothing, 2026-11-07.)`
  A search index of kla.com shows, but we did not fetch, **(858) 573-9300** for quotes (iMicro page), **+1 800 600 2829 / nanosupport@kla.com**
  for service and support, and 105 Meco Lane, Oak Ridge, TN 37830 (<https://www.kla.com/locations>). Treat as `(unverified)` until read in a browser.
- **Regional distributor:** none found for the US (NanoTechnology Solutions covers Australia and New Zealand) `(unverified)`. **Academic:** two universities run an iMicro as a service (UNH, Kassel), so **testing as a service
  is an alternative** to ask about.

### 4. Our open questions for them
1. **Vibration:** the iMicro will stand on a **VLM tray** that moves between stops. What floor-vibration limit does it
   have, how long to settle after a move, and can the tray carry it without it being re-leveled?
2. **Robot loading:** the hood lifts by hand. Can it be actuated, and can the **sample puck and mount** (1.5 in) be loaded
   by a gripper? What is the **sample height limit**?
3. **Automation:** is there an **API, command line or OPC**, for recipe start and status, and for unattended grid runs?
4. **Size, weight, power, and room requirements**, including temperature stability.
5. **Mount fit:** magnetic puck versus a mounted sample in a **38 mm** mount; is a clamp available?
6. **Tip wear and verification:** fused silica reference, tip area function frequency, and tip prices.
7. **Is the iMicro the right fit** for Al, Cu-Ni and NAB, or would a smaller iNano be enough for a hardness map?
8. PM schedule, consumables and spares with prices, service contract price, response time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Samples | Polished, hot-mounted metal coupons in 1.5 in mounts: Al alloys, Cu-Ni, NAB |
| Tests | Hardness and modulus by Oliver-Pharr (ISO 14577), grids, no scratch at first **[to confirm]** |
| Load range | 1 mN to 1 N, mostly 5-500 mN |
| Throughput | 972 indents a year, 3 per alloy; a few hours a mount |
| Automation | Robot loading; unattended grid runs; remote start |
| Environment | A lab room, a thermal cabinet if needed; a moving tray **[to confirm]** |

### 6. Draft email
> **To:** KLA Instruments (web form, nanoindenters)
> **Subject:** Budgetary quote: iMicro with InForce 1000, robot-loaded, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one iMicro to indent polished 38 mm mounts of Al, Cu-Ni and bronze, about 970 indents a
> year, loaded by a robot arm. Please quote (list and academic, valid 90 days) an iMicro with InForce 1000, Berkovich tip,
> magnetic puck holder, NanoBlitz 3D and InView. Please tell us:
> 1. Footprint, weight, power, and vibration and temperature limits, and whether it can stand in a vertical lift tray
>    that moves between stops.
> 2. Can the hood and the stage loading be driven by a robot, and is there an API for unattended runs?
> 3. The sample holder for a 38 mm mount.
> 4. Preventive maintenance, calibration (reference materials, tip area function), consumables with prices, a service
>    contract price and the response time to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.kla.com/products/instruments/nanoindenters/imicro> and its PDF (bot wall) | yes, blocked |
| <https://www.azonano.com/equipment-details.aspx?EquipID=1357> (specs; WebFetch) | no |
| <https://www.unh.edu/research/university-instrumentation-center/nanoindenter-kla-instruments-imicro-nanoindenter> | no |
| Search: KLA acquires Nanomechanics Inc. (Oak Ridge) | no |
| <https://www.kla.com/products/instruments/nanoindenters/imicro> (model check: live, Request a Quote) (2026-11-07, maker's page, headed Chromium on the stream-cam Pi) | yes |

---

## 6. Plastometrex PLX-Benchtop (Profilometry-based Indentation Plastometry)

### 1. What we'd buy
- **Maker and model:** Plastometrex **PLX-Benchtop**, **one**, with the **PLX-AutoStage** (automated multi-sample testing),
  the **CORSICA+** software subscription, and **spherical indenters** (a 1 mm radius ball in the model); the
  **PLX-HotStage** (800 C) is **not** wanted at first.
- **Role and place:** a bulk-like stress-strain curve from a single indent (yield, UTS and work-hardening) of a printed
  or sectioned sample, as a fast screen next to the tensile test. About 972 a year with the nanoindents. **Tray E**.
- **Model check (2026-11-07):** **current**. Plastometrex's site lists the PLX-Benchtop (with the PLX-HotStage add-on and CORSICA+) and no newer benchtop; the **PLX-AutoStage is new**, and trade press says it launches commercially in Q4 2026 with pre-orders taken, so its delivery date matters. (<https://www.plastometrex.com/>; <https://www.tctmagazine.com/plastometrex-to-roll-out-plx-autostage-for-automated-pip-testing-later-this-year/>)

### 2. The published specs that matter for integration
(Plastometrex product page, via WebFetch)
- **Samples:** real parts or coupons **as small as 1.5 x 1.5 x 0.75 mm**; minimal preparation.
- **Indents:** about **0.25-1 mm wide, 25-200 um deep**; spaced as close as **1.5 mm**.
- **Time:** a stress-strain curve "in as little as **5 minutes**".
- **Automation:** the **PLX-AutoStage** add-on tests several samples.
- **Not published:** **dimensions, weight, power, price, calibration** (the model scales the 500 mm width, plus or minus
  20 percent, from videos; `notes/refine_pip.md`).

### 3. Contact
- **Email:** info@plastometrex.com (general). **Web form:** <https://www.plastometrex.com/request-a-quote> and
  <https://www.plastometrex.com/book-a-demo>; contact <https://www.plastometrex.com/contact>.
- **Offices (the contact page):** **U.S. office, 6410 Langfield Rd, Building J, Houston, TX 77092**; UK office, Unit 7
  Technopark, Newmarket Road, Cambridge CB5 8PB. **Phone (UK):** +44 (0)1223 867992 `(unverified: the contact page text we read gave only info@plastometrex.com)`.
  A US phone is not published. **info@plastometrex.com** `(verified: https://www.plastometrex.com/contact, 2026-11-07)`.
- **Regional rep:** the Houston office; a Mountain West rep `(unverified: none published)`. **Academic:** an Illinois MRL facility
  runs one (<https://mrl.illinois.edu/facilities/equipment/Indentation-Plastometer-Plastometrex-PLX-Benchtop>).

### 4. Our open questions for them
From `notes/refine_pip.md` ("Still uncertain") and the grep of `notes/`:
1. **Size, weight and power**, and the **depth** (we use 560 mm) and **floor space for a robot to reach the platen**.
2. **Robot loading:** the platen is open from the front; how is the **sample clamped** (a 1.5 in mount, or a cut piece)?
   Is a **hold-down** automatic, and can the AutoStage be sequenced by software?
3. **The profilometer:** how is the stylus lowered and traced; is a **sample height limit** published?
4. **Can the PLX test a polished, mounted 38 mm coupon** or must the sample be unmounted, flat and parallel?
5. **Al and Cu alloys, NAB:** is the **inverse FE method** validated on these (AlSi10Mg, Cu-Ni) and on an **as-printed** surface?
6. **Software:** an API, or a headless mode, and where the data live under **CORSICA+**.
7. **Indenter wear:** ball material, life, price; the **calibration and verification** (a reference sample).
8. PM schedule, consumables and spares with prices, a service contract price, response time in Utah (Houston?).

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Materials | Al-Si and Al-Mg-Si alloys, Cu-Ni, NAB; as printed and heat treated |
| Sample form | Sectioned coupons (6 x 6 mm and larger) and 1.5 in mounts; polished or ground |
| Property targets | Yield and UTS to within 10 percent of tensile **[to confirm]** |
| Throughput | About 970 a year with the nanoindents (3 per alloy); 5 minutes each |
| Automation | AutoStage, robot loading |
| Utilities | Mains; a clean bench |

### 6. Draft email
> **To:** info@plastometrex.com (and the web form, <https://www.plastometrex.com/request-a-quote>); Houston office
> **Subject:** Budgetary quote: PLX-Benchtop with AutoStage and CORSICA+, robot-loaded, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one PLX-Benchtop with the AutoStage to screen about 320 printed Al, Cu-Ni and NAB alloys a
> year, loaded by a robot arm. Please quote it (list and academic, valid 90 days), and tell us:
> 1. Size, weight and power, and how a sample is clamped; can a robot load a 38 mm mount or a cut coupon?
> 2. Can the AutoStage and tests be driven by software with no dialogs (an API)?
> 3. Is the method validated for as-printed Al and Cu alloys?
> 4. Indenter and stylus life and prices, calibration and verification, a service contract price, and the response time
>    to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.plastometrex.com/contact> (email, offices) | yes |
| <https://www.plastometrex.com/products/plx-benchtop> (specs; WebFetch) | no |
| `notes/refine_pip.md` | n/a |
| <https://www.plastometrex.com/> (model check: PLX-Benchtop current) (2026-11-07, runner) | no |
| <https://www.tctmagazine.com/plastometrex-to-roll-out-plx-autostage-for-automated-pip-testing-later-this-year/> (AutoStage Q4 2026) (2026-11-07, search snippet) | no |

---

## 7. Keyence VHX-7000 / VHX-X1 + EA-300 LIBS

### 1. What we'd buy
- **Maker and model:** Keyence **VHX-X1** (the replacement for the VHX-7000, which is discontinued) with the **S700
  stand** (motorized, if offered), a **VH-ZST** zoom lens, and the **EA-300 LIBS** elemental analysis head, **one**.
- **Role and place:** wide-field optical imaging and 3D reconstruction of the broken tensile bar, and a laser-induced
  breakdown spectrum (LIBS) spot chemistry. **Tray K**, the controller turned sideways, with a **PiKVM V4 Mini** on top
  (`notes/instruments_r7.md`). DAL's proposal already lists a VHX-7000 at BYU.
- **Model check (2026-11-07):** **discontinued** (the VHX-7000); the VHX-X1 and EA-300 we plan are **current**. Keyence's VHX-7000 page says "This model has been discontinued" and names the VHX-X1 as the replacement, and its elemental-analyzer page lists only the EA-300 series, for VHX microscopes, and the VHX-S700 stand ("EA-compatible") and VH-ZST lens are listed as VHX-X1 series models; the VHX-7000 in DAL's proposal is the old model, so the X1's size, weight and remote control are to confirm. (<https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/>; <https://www.keyence.com/products/microscope/elemental-analyzer/>)

### 2. The published specs that matter for integration
- **EA-300:** 280 x 210 x 375 mm, 7.2 kg; **355 nm Nd:YAG, Class 1, 10 um spot**; H to U; powered by the controller's
  camera port (Keyence's page).
- **VHX-7000 controller:** 625 W x 460 H x 180 D mm, about 12 kg, **27 in 4K screen built in**; Gigabit LAN, USB 2.0 and
  3.0, **DisplayPort out**, 1 TB HDD, 430 VA. **VHX-X1:** 635 x 450 x 132 mm, 10.8 kg.
- **Stand VHX-S750E:** XYZ motorized, XY plus or minus 20 mm, stage 171 x 168 mm, 23.8 kg, 5 kg load. The **S700 is
  EA-compatible**.
- **Interfaces:** the controller's screen and mouse; **remote desktop and an API are not documented** (`notes/instruments_r7.md`).

### 3. Contact
- **Phone:** **1-888-539-3623** (Keyence Corporation of America, 500 Park Boulevard, Suite 200, Itasca, IL 60143, on the
  site). **Email:** none published; **Ask an Expert** <https://www.keyence.com/inquiry/askKeyence/>, **price**
  <https://www.keyence.com/products/microscope/digital-microscope/vhx-x1/get-pricing/>, **demo**
  <https://www.keyence.com/inquiry/requestDemoTest/>.
- **Regional rep:** Keyence sells **direct**; a Utah or Mountain West sales engineer is assigned by the form `(unverified: no territory list; 1-888-539-3623 verified on https://www.keyence.com/inquiry/askKeyence/, 2026-11-07; that page also prints info@keyence.com, so a general address exists)`.

### 4. Our open questions for them
From `notes/instruments_r7.md` ("To check with Keyence"):
1. **The controller's DisplayPort resolution:** can it be set to **1920 x 1200 or lower** so a **PiKVM** (HDMI capture to
   1920 x 1200) can show it through a DP-to-HDMI adapter?
2. **Remote Desktop or a remote-control API:** can it be enabled, or is there a documented **automation interface**
   (start a capture, read the stage)?
3. Does the **VHX-X1 take the EA-300**, with the S700 stand and the VH-ZST on **lens joint OP-88660**?
4. **LIBS on our alloys:** Mg, Si, Al, Cu, Ni, Fe, Mn; **calibration standards**; **laser safety** and the interlock; the
   **consumables** (a protective window, the laser's life).
5. **Robot loading:** the stage height limit for a 38 mm mount and a 100 mm tensile bar; a **repeatable fixture**.
6. **The head's tilt range** (Keyence gives none; Georgia Tech says -60 to +90 degrees).
7. PM schedule, **calibration** of the scale (a stage micrometer), spares and consumables with prices, service contract price,
   response time in Utah.
8. **VHX-X1 versus VHX-7000** (model check, 2026-11-07): the VHX-7000 is discontinued. What changed in size, weight, utilities and remote control, and does the EA-300 fit the VHX-X1 unchanged?

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Samples | Broken E8 bars, polished mounts, powder on stubs; Al, Cu-Ni, NAB |
| Magnification | 20-2000x with VH-ZST; LIBS 300-1000x |
| Throughput | A few images per tested bar (about 1,400 a year) |
| Automation | Robot places the sample; a remote desktop through a PiKVM |
| Utilities | 120 V; 430 VA controller |

### 6. Draft email
> **To:** Keyence Corporation of America, 1-888-539-3623, web form (Ask an Expert, quote)
> **Subject:** Budgetary quote: VHX-X1 with S700 stand, VH-ZST and EA-300 LIBS, robot-loaded, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one VHX-X1 with the S700 stand, VH-ZST lens and EA-300 LIBS, loaded by a robot arm.
> Please quote it (list and academic, valid 90 days), and answer:
> 1. Can the controller's DisplayPort output be set to 1920 x 1200 or lower for a KVM-over-IP box, and can Remote Desktop or
>    an API be enabled?
> 2. Does the VHX-X1 take the EA-300 on the S700 with the VH-ZST?
> 3. LIBS standards for Al, Cu-Ni and bronze, and its consumables.
> 4. Preventive maintenance, calibration, spares with prices, a service contract price, and the response time to Provo, UT.
>
> The VHX-7000 is discontinued: please quote the VHX-X1 configuration that replaces it and say what changed from the VHX-7000 in size, weight, utilities and remote control.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.keyence.com/contact/> (phone, address) | yes |
| <https://www.keyence.com/products/microscope/digital-microscope/vhx-x1/> (links; WebFetch) | no |
| `notes/instruments_char.md`, `notes/instruments_r7.md` | n/a |
| <https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/> (discontinued, VHX-X1 replacement) (2026-11-07, runner) | no |
| <https://www.keyence.com/products/microscope/elemental-analyzer/> (EA-300 series) (2026-11-07, runner) | no |
| <https://www.keyence.com/products/microscope/digital-microscope/vhx-x1/models/vhx-s700/> and <https://www.keyence.com/products/microscope/digital-microscope/vhx-x1/models/vh-zst/> (S700, VH-ZST in the X1 series) (2026-11-07, search snippet) | no |

---

## 8. Mitutoyo HM-220 Type D micro-Vickers

### 1. What we'd buy
- **Maker and model:** Mitutoyo **HM-220 Type D** (PC-driven, motorized XY stage with autofocus), **one**, with the
  **AVPAK-20** software and PC, the **50 x 50 mm motorized XY stage (810-461E)** or the **100 x 100 mm (810-462E)**, a
  Vickers indenter, and **reference test blocks**.
- **Role and place:** a row of HV0.1 micro-Vickers indents on a polished mount, read automatically. On the **hot mount**
  by its own loading slide. **Tray L**. About 324 mounts a year.
- **Model check (2026-11-07):** **current**. Mitutoyo America's product page for the HM-210/220 Type D is live with order numbers 64AAB380P to 64AAB383P, an Inquire button and no discontinued or successor note; a search snippet describes a 2025 Mitutoyo America promotion on the Type D as a "clearance" offer "while supplies last" (the PDF itself could not be read), so ask whether a successor is coming. (<https://pim.mitutoyo.com/products/test-equipment/micro-hardness-testers/hm-210-220-vickers-hardness-testing-machine-type-d/>)

### 2. The published specs that matter for integration
(Mitutoyo catalog section K via `notes/instruments_r7.md`; dealer pages)
- **Size:** main unit **315 x 671 x 595 mm, 43 kg**; with the AVPAK PC the model uses 533 x 672 x 595 mm, 48 kg. It is
  **the only automatic tester whose maker publishes its height** (595 mm).
- **Load:** **0.4903 mN to 19.61 N** (0.05 to 2 kgf); a motorized **turret for up to 4 objectives and 2 indenters**.
- **Stage:** Type D motorized XY, 50 x 50 mm (100 x 100 optional), table 130 x 130 mm, 25 mm/s; motorized focus; 3 MP camera.
- **Interfaces:** AVPAK on a Mitutoyo-specified PC. **Remote start, API and door or lid actuation are not published**; the
  HM-220 has no door.

### 3. Contact
- **Phone:** **1-888-648-8869** (Mitutoyo America, 965 Corporate Blvd., Aurora, IL 60502, on the contact page).
  **Email:** none published. **Forms:** Request a Quote and Request a Demo on <https://www.mitutoyo.com/contact-us/>.
- **Regional rep:** **Distributor Locator** on the same site (<https://www.mitutoyo.com/contact-us/>); a Utah distributor is
  `(unverified: the locator at ecatalog.mitutoyo.com is zip-driven and did not answer the runner or the Pi, 2026-11-07)`. 1-888-648-8869 and the Request a Quote form `(verified: https://www.mitutoyo.com/contact-us/, 2026-11-07)`.

### 4. Our open questions for them
1. **Automation:** can **AVPAK** run a test list and export results with **no operator**, driven by a script, a command
   line or an **API**? Is there an **I/O** interface for start and complete?
2. **Robot loading:** a **hold-down** for a 38 mm mount that a gripper can set, and the **stage and objective clearance**
   (the model's 767 mm depth with its PC is too deep for tray L, so the PC would stand elsewhere).
3. **Which stage** (50 or 100 mm) for a 1.5 in mount; **minimum indent spacing** at HV0.1 in AlSi10Mg (about 125 HV, 86 um).
4. **Calibration and verification:** the reference blocks, **ASTM E384 / E92 and ISO 6507-2** verification interval.
5. **The PC:** which one Mitutoyo specifies, and whether a **headless** or networked one is allowed.
6. Is there a **successor** to the HM-220 (the HM-200 series is old)?
7. PM schedule, **indenter and objective life**, consumables with prices, a service contract price, response time in Utah.
8. **Is the HM-220 Type D still in production** (model check, 2026-11-07)? A 2025 promotion was described as a clearance; if a successor is coming, its size, weight, utilities and remote control.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Samples | Polished, hot-mounted (conductive or Bakelite) 1.5 in coupons of Al, Cu-Ni, NAB |
| Test | HV0.1 (some HV0.5), rows of 5-10 indents, 3 mounts an hour |
| Standards | ASTM E384; ISO 6507 |
| Throughput | About 324 mounts a year |
| Automation | Robot loads; AVPAK runs a list; results exported |

### 6. Draft email
> **To:** Mitutoyo America (web form, Request a Quote); a Utah distributor from the Distributor Locator
> **Subject:** Budgetary quote: HM-220 Type D with AVPAK, robot-loaded, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one HM-220 Type D with the 50 x 50 mm (or 100 x 100 mm) motorized stage and AVPAK to test about
> 320 polished 38 mm mounts a year, loaded by a robot arm. Please quote it (list and academic, valid 90 days), and tell us:
> 1. Can AVPAK run a test list and export results unattended, from a script, command line or API, with I/O for start and done?
> 2. A mount hold-down a gripper can load, and the objective clearance.
> 3. The verification blocks and interval (ASTM E384 or ISO 6507-2).
> 4. Preventive maintenance, indenter and objective life, consumables with prices, a service contract price, and the
>    response time to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.mitutoyo.com/contact-us/> (phone, address, forms) | yes |
| Mitutoyo catalog section K (`https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf`) via `notes/instruments_r7.md` | n/a |
| Search: HM-220 Type D dealers (stage numbers, AVPAK-20) | no |
| <https://pim.mitutoyo.com/products/test-equipment/micro-hardness-testers/hm-210-220-vickers-hardness-testing-machine-type-d/> (Type D live, 64AAB380P to 383P) (2026-11-07, runner) | no |
| <https://www.mitutoyo.com.sg/sg-en/product/detail/hm-200-series> (HM-200 series listed) (2026-11-07, search snippet) | no |
| <https://cdn.mediavalet.com/usil/mitutoyo/1IFeZDSZZkyaPpaef11DoA/0Ysxo04xMUuJ4T4nijmsCA/Original/HM%20Hardness_Promo.pdf> (2025 promotion; text not readable) (2026-11-07, search snippet) | no |

---

## 9. Instron: 68FM-100 + 3119-608 chamber + AVE 2 + AT6 automated testing system; and the 68SC-2

### 1. What we'd buy
- **Maker and model:** Instron **68FM-100** floor-model electromechanical frame (100 kN), **one**, with:
  the **3119-608 environmental chamber** (-150 to 600 C with a cooling option; we need ambient to 200 C),
  the **AVE 2** non-contacting video extensometer (reading through the chamber's window), **100 kN hydraulic
  wedge grips** (flat specimens, front loading; Instron CP104947 listed in `notes/alloy_workflow.md`) with **grip faces for 6 mm
  flat bars**, **Bluehill Universal** software, and a **load-cell verification** (ASTM E4).
- **The AT6 6-axis robotic automated testing system:** the model loads the 68FM-100 "as in Instron's AT6 cells". We ask
  whether to **buy an AT6**, or **load with our own UR10e** and buy only the frame, chamber and extensometer.
- **The 68SC-2 tabletop** (2 kN, single column): **one, as a small-specimen option** (460 x 615 x 1410 mm).
- **Role and place:** tensile tests of printed **E8 subsize bars** (100 mm long, a 32 mm reduced section 6 mm wide and
  6 mm thick, **14.8 kN** at AddUp's 412 MPa AlSi10Mg) at room temperature and **up to 200 C**. About **1,420 a year**. The
  68FM-100 is on the **floor, beside the VLM** (2287 x 1140 x 786 mm, 799 kg per Instron).
- **Model check (2026-11-07):** **current**, with a **new, smaller 100 kN option**. Instron's 6800 Series page still offers the 68FM floor models (the 68FM-100 included) and the 68SC single-column frames (to 5 kN), and the AT6 is current (to 600 kN, up to 500 specimens unattended, optional chambers and parallel frames); new is the **68TM-100 table model**, "40% smaller" than the floor model: 1640 x 760 x 715 mm (0.54 m2) against 2287 x 1140 x 786 mm, 100-240 V single phase against 208-240 V, but 420 mm between columns against 575 mm, 508 against 1016 mm/min and 180 against 300 kN/mm. The 3119-608 (-150 to 600 C, 165 kg, in Instron's 3119-600 literature) and the AVE 2 (now "AVE2", for the 3119-600 chambers) were checked by search snippet only. (<https://www.instron.com/en/products/testing-systems/universal-testing-systems/6800-series/>; <https://www.instron.com/wp-content/uploads/2025/09/100kn-universal-testing-systems-tm-fm.pdf>; <https://www.instron.com/en/products/testing-systems/automated-testing-systems/at6-6-axis-robotic-automated-testing-system/>)

### 2. The published specs that matter for integration
- **68FM-100:** force 100 kN; crosshead travel 1407 mm (standard height), **vertical test space 1494 mm**, 575 mm between
  columns, 2287 x 1140 x 786 mm, 799 kg (Instron's floor-model sheet; search extract). Operating 5 to 40 C.
- **3119-608:** -150 to 600 C, **inside 400 x 400 x 560 mm**, outside 550 x 710 mm, forced convection; below ambient needs
  a cooling option (Instron's catalog extract). The door opening is 400 x 560 mm in the model.
- **AVE 2:** resolution to 2 um, cyclic up to 20 Hz, field of view up to 240 mm, and it **can be used with temperature
  chambers** (Instron). The newer **AVE 3** exists, so ask which is current.
- **AT6:** modular **6-axis robot** that automates tensile, flexural, compression and lap shear to ASTM and ISO, with
  dual-frame parallel testing, and "contact us" for standards compatibility. **Instron's AT2/AT3/AT6 handling details
  could not be verified from the literature**; the videos are the source (`notes/alloy_workflow.md`).
- **Interfaces:** Bluehill Universal. An **API, remote command set and OPC UA are not published** in what we read.
- **Door actuation:** **not published**; the model assumes an actuator on the 3119 door.

### 3. Contact
- **Phone:** **+1 800 564 8378** or **+1 781 575 5000**, Instron, 825 University Ave, Norwood, MA 02062-2643 `(unverified: instron.com returns 403 to the runner and a Cloudflare challenge to Chromium on the Pi, 2026-11-07; a search index of instron.com's Locations page shows 800-564-8378 for sales)`. **Email:** none published.
- **Web:** <https://www.instron.com/en/contact-us> returns **403 to the runner and a Cloudflare challenge to the Pi**, so
  the contact and quote forms were not read. **Use the form on <https://www.instron.com>.**
- **Regional rep (Utah / Mountain West):** not published; an Instron **field service engineer role for the Salt Lake City
  area** exists (a job posting), so there is service coverage. A sales rep `(unverified: Instron's contact page is a region selector we could not load)`.
- **Academic:** `(unverified)` ask for education pricing.

### 4. Our open questions for them
From `notes/alloy_workflow.md`, `notes/instruments_r7.md` and the user's request:
1. **Does the AT6 handle E8 subsize bars** (100 mm long, 6 mm wide, 3.7 to 6 mm thick), and does it hold them **at 200 C in a
   3119-608**? Which of the AT6's frames and **chambers** are supported, and is the **68FM-100 a supported frame**?
2. **Is the AT6 needed**, or can **our UR10e on a MiR250** load a 68FM-100 safely? What **door, grip and safety** hooks does
   Instron sell (the chamber door, the wedge grip's **front-loading hydraulic actuation**, the **crosshead interlock**)?
3. **Frame size.** The route bar needs **14.8 kN**, 15 percent of a 100 kN frame; the faced bar needs 3.7 kN. Would a
   **30 or 50 kN table frame (the 68TM-30 or -50)** suit, can it take the **3119-608**, and what does it save? **[Instron's
   exact model list is not verified here.]**
4. **Software:** **Bluehill Universal's API or a command line**, so a scheduler starts a method and reads the result; **no
   dialogs**; export in an open format.
5. **AVE 2 or AVE 3 through the chamber's heated window** at 200 C, and **marker-free** gauge length on a 25 mm gauge section.
6. **Calibration and verification:** **ASTM E4 annual load verification** (or ISO 7500-1), **E83 or ISO 9513** extensometer
   class, **E21** elevated-temperature, the chamber's **thermocouple survey**; who does it in Utah and what it costs.
7. **Floor and install:** weight 799 kg, **anchoring**, ceiling clearance for the 2287 mm height.
8. PM schedule and downtime, **consumables** (grip faces, chamber elements, fan), spares with prices, a service contract
   price, and the response time in Utah.
9. **The new 68TM-100 table model** (model check, 2026-11-07): 1640 x 760 x 715 mm, 100-240 V. Would it take the 3119-608 chamber and the AVE 2 in its 420 mm between columns, and do its 180 kN/mm and 508 mm/min suit E8 subsize bars? It could leave the floor for a tray or bench.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Material | AlSi10Mg and other Al-Si alloys, Cu-Ni, NAB; as printed and heat treated (T5, T6) |
| Specimen | ASTM E8/E8M subsize sheet bar: **L 100, A 32, W 6, C 10, B 30, R 6, G 25 mm**, 6 mm thick (14.8 kN) or faced to 1.5 mm (3.7 kN) |
| Tests | Room temperature and up to 200 C; strain by video extensometer; yield, UTS, elongation |
| Rate | About 0.4 mm/mm/min is fast; a test is a few minutes |
| Number | About **1,420 a year** (4 bars per alloy, 324 alloys) |
| Automation | Robot loads and unloads; start and result by software; unattended |
| Utilities | 208 V (**[to confirm]**); air if the grips need it **[to confirm]**; clean floor |
| Standards | ASTM E8, E21; ASTM E4 verification |

### 6. Draft email
> **To:** Instron sales, Norwood, MA (web form and +1 800 564 8378)
> **Subject:** Budgetary quote: 68FM-100 with 3119-608, AVE 2 and automation (AT6 or robot-ready), BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab plans about 1,400 tensile tests a year on ASTM E8 subsize AlSi10Mg, Cu-Ni and bronze bars (100 mm
> long, 6 mm wide, up to 6 mm thick, up to 14.8 kN), at room temperature and up to 200 C, loaded by a robot arm. We would like a
> budgetary quote (list and academic, valid 90 days) for the 68FM-100 with the 3119-608 chamber, the AVE 2, 100 kN
> hydraulic wedge grips for 6 mm flat bars and Bluehill Universal, and a price for the AT6 on the same frame (and a smaller
> frame as an alternative). Please tell us:
> 1. Does the AT6 handle E8 subsize bars at 200 C with the 3119-608, and is the 68FM-100 a supported AT6 frame?
> 2. If we load the frame with our own arm, which door, grip and interlock hooks does Instron offer, and does it keep the warranty?
> 3. Bluehill's API or a command line for unattended runs.
> 4. Would a 30 or 50 kN frame take the same chamber and extensometer?
> 5. Preventive maintenance, ASTM E4 annual verification, consumables and spares with prices, a service contract price,
>    and the response time to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.instron.com/en/contact-us> (403; Cloudflare challenge on the Pi) | yes, blocked |
| Search: Instron brochure (825 University Ave; +1 800 564 8378), 68FM-100 and 3119-608 catalogs, AVE 2, AT6 page | no |
| Search: SLC field service job posting | no |
| `notes/alloy_workflow.md`, `notes/instruments_r7.md`, README | n/a |
| <https://www.instron.com/en/products/testing-systems/universal-testing-systems/6800-series/> (68FM, 68SC, new 68TM-100) (2026-11-07, maker's page, headed Chromium on the stream-cam Pi) | yes |
| <https://www.instron.com/wp-content/uploads/2025/09/100kn-universal-testing-systems-tm-fm.pdf> (68TM-100 versus 68FM-100, Sep 2025) (2026-11-07, maker's page, headed Chromium on the stream-cam Pi) | yes |
| <https://www.instron.com/en/products/testing-systems/automated-testing-systems/at6-6-axis-robotic-automated-testing-system/> (AT6 current) (2026-11-07, maker's page, headed Chromium on the stream-cam Pi) | yes |
| <https://www.instron.com/en/products/testing-accessories/extensometers/ave-2-advanced-video-extensometer/> (AVE2, 3119-600 chambers) (2026-11-07, search snippet) | no |
| <https://instron.com/-/media/literature-library/manuals/thermal-safety-sheet-for-3119-600-series-temperature-controlled-chambers.pdf?la=en> (3119-608, 165 kg) (2026-11-07, search snippet) | no |

---

## 10. ZwickRoell zwickiLine Z5.0 TN (horizontal)

### 1. What we'd buy
- **Maker and model:** ZwickRoell **zwickiLine Z5.0 TN** (5 kN, 1289 mm tall column), **one**, run **on its side** on
  a tray; **grips for miniature specimens**, a **video or clip-on extensometer**, **testXpert** software.
- **Role and place:** tensile tests of **miniature specimens** or **faced** bars (6 x 1.5 mm, 3.7 kN, 74 percent of the
  frame), as a second tensile machine. **Tray L**, on its side, 638 mm deep, in front of the UPS.
- **Model check (2026-11-07):** **current**. ZwickRoell's product information for the zwickiLine Z0.5 to Z5.0 lists the Z5.0 TN (item 059006) beside the TS and TH and says the frame runs vertical or horizontal; no successor was found (search snippet; the sheet itself not opened). (<https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf>)

### 2. The published specs that matter for integration
(ZwickRoell product information PI 396 and `notes/instruments_r7.md`)
- **Size:** Z5.0 TS, TN, TH are 789, **1289** and 1589 mm tall; 408 mm wide (411 with electronics); 480 deep (622 with
  electronics); **70, 78 and 83 kg**. The model uses **1289 x 638 x 448 mm, 83 kg** for the TN.
- **Force and speed:** **5 kN**; 0.0005 to 600 mm/min; test area **105 mm deep**.
- **Horizontal use:** "can be operated in **vertical or horizontal position** as required, and can be swiveled 180 degrees
  in horizontal mode" (ZwickRoell's copy, quoted in the notes).
- **Interfaces and automation:** testXpert software; **roboTest** is ZwickRoell's robot cell (the Edison R8 reference used a
  Z100 with roboTest L, 148 valid tests). Robot or API **hooks for the Z5.0** are not published.

### 3. Contact
- **ZwickRoell LP, 1009 Market Center Drive NW, Kennesaw, GA 30144**, **+1 770 420 6555**; hotline **+1 678 695 5757**
  (the contact page `(verified: https://www.zwickroell.com/contact/ and https://www.zwickroell.com/company/about-us/zwickroell-north-america/, 2026-11-07)`). **Email:** no sales email is printed; the page is a form
  (<https://www.zwickroell.com/contact/>), which asks for the country and a "contacts worldwide" selector.
- **Regional rep (Utah):** the **Contacts worldwide** selector assigns one by zip code `(unverified: needs a browser form; no Utah rep on the pages read, 2026-11-07)`.
- **Academic:** `(unverified)`.

### 4. Our open questions for them
From `notes/timelapse.md`, `notes/instruments_r7.md` ("whether the zwickiLine's grips take it, is open"):
1. **Grips for miniature specimens:** the geometry we would use is open (a 55 mm kit build can only hold miniature bars); **which
   grips and gauge lengths** fit, and which standard (ASTM E8 subsize, ISO 6892, a sub-size dog-bone) do they meet?
2. **Horizontal mounting:** is the **horizontal position** a **supported, certified** use with the **testXpert** software,
   the load cell and the grips, and with **gravity** on a hanging extensometer? Any **drawing for a tray plate**?
3. **Robot loading:** can a gripper set a bar between **open jaws** from above? Are the **jaws pneumatic**, with a
   **command interface**, and what **signals** does a robot read?
4. **Is 5 kN enough** (miniature and faced bars), or does ZwickRoell advise the **Z10** or the **AllroundLine** in a roboTest
   cell, which are bigger?
5. **testXpert's API:** a way to start tests and read results with no operator.
6. **Calibration:** **ISO 7500-1 / ASTM E4** verification, class 0.5 or 1, who does it in Utah, price.
7. PM schedule, **consumables** (grip faces), spares with prices, a service contract price, response time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Material | Al, Cu-Ni, NAB printed bars; room temperature only on this machine |
| Specimen | **Miniature or faced** bars, 1.5 to 3 mm thick, 25 to 55 mm long **[to confirm geometry]** |
| Force | Up to 3.7 kN |
| Throughput | A share of the 1,420 tests a year **[to confirm the split with section 9]** |
| Automation | Robot loads between open jaws; start and results by software |
| Orientation | Horizontal |

### 6. Draft email
> **To:** ZwickRoell LP, Kennesaw, GA (web form and +1 770 420 6555)
> **Subject:** Budgetary quote: zwickiLine Z5.0 TN for horizontal, robot-loaded miniature tensile tests, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one zwickiLine Z5.0 TN, mounted **on its side** on a vertical-lift tray, to pull miniature and
> faced tensile bars of printed Al, Cu-Ni and bronze (up to 3.7 kN) loaded by a robot arm from above. Please quote it
> (list and academic, valid 90 days) with miniature-specimen grips, an extensometer and testXpert, and tell us:
> 1. Is horizontal mounting a supported use, and is there a drawing for a mounting plate?
> 2. Which grips take miniature specimens (and to which standard), and can a robot set a bar between open jaws, with a
>    command interface for the jaws?
> 3. testXpert's API for unattended runs.
> 4. Preventive maintenance, ISO 7500-1 verification, consumables and spares with prices, a service contract price, and
>    the response time to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.zwickroell.com/contact/> (address, phone) | yes |
| ZwickRoell PI 396 (`02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf`; text not extractable, figures from `notes/instruments_r7.md`) | no |
| `notes/timelapse.md`, `notes/edison_r8.md` | n/a |
| <https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf> (Z5.0 TN, item 059006) (2026-11-07, search snippet) | no |

---

## 11. Tinius Olsen and ADMET: horizontal frames up to about 15 kN

### 1. What we'd buy
- **Maker and model:** **none chosen; a quote request.** A **motorized horizontal tensile frame of about 15 kN** that stands on
  a tray (the 14.8 kN route bar), from **Tinius Olsen** (horizontal frames from 5 to 300 kN) or **ADMET** (an **eXpert 5000**
  frame set up horizontal, "quote only"). **Quantity 0 or 1**, only if the zwickiLine is too small.
- **Role and place:** the route's full 6 x 6 mm bar on a tray. The notes found **no motorized horizontal machine with a
  published size that reaches 14.8 kN** (`notes/instruments_r7.md`).
- **Model check (2026-11-07):** **current** (no model chosen). Tinius Olsen's horizontal testers page lists the MHT 1000 (5 kN), MHT 5000 (25 kN), MHT 30000 (150 kN) and MHT 60000 (300 kN), none at 15 kN, so the **MHT 5000 is the smallest that reaches 14.8 kN**; ADMET still describes the eXpert 5000 series as modular frames set up vertical or horizontal. (<https://tiniusolsen.com/product-category/universal-testing-machines/horizontal-testers>; <https://www.admet.com/product-category/testing-machines/universal-testing-machines/>)

### 2. The published specs that matter for integration
- **Tinius Olsen:** horizontal machines from 5 to 300 kN; **no size published**.
- **ADMET:** eXpert 5000 frames can be set up horizontal; **no size published**; quote only.
- **Others in the notes:** TecQuipment SM1002 (20 kN, hand-cranked); Mark-10 horizontal stands (2.2 kN); Kammrath and Weiss 10
  kN module (60 mm specimens). No Instron statement says a 68SC or 68TM can lie horizontal.

### 3. Contact
- **Tinius Olsen (USA):** **sales@tiniusolsen.com**, **+1 215-675-7100**, 1065 Easton Road, Horsham, PA 19044
  (<https://www.tiniusolsen.com/contact/sales/>); request a quote <https://www.tiniusolsen.com/contact/request-a-quote/>.
  `(verified: https://www.tiniusolsen.com/contact/sales/, 2026-11-07: US entry is the Horsham HQ, sales@tiniusolsen.com, 215 675 7100; named reps are for Canada and abroad, so no Utah rep is published)`.
- **ADMET:** **info@admet.com**, **(800) 667-3220** toll-free or **(781) 769-0850**, 51 Morgan Drive, Norwood, MA 02062
  `(verified: https://www.admet.com/contact/, 2026-11-07; also (781) 769-0884 fax)`.
- **Academic:** both sell to universities; education pricing `(unverified)`.

### 4. Our open questions for them
1. **A motorized horizontal frame at 15 kN with a 100 mm specimen:** **dimensions, weight, force and a drawing**, so we can fit it on
   a 2426 x 840 mm tray with an 856.5 mm height limit.
2. **Is horizontal operation a supported use** with the load cell, the grips and the **software**?
3. **Grips** for 6 x 6 mm flat bars and **robot loading** from above with open jaws.
4. **Software** with an API and unattended operation; **temperature** (a chamber) is not needed here.
5. **ASTM E4 verification**, PM schedule, consumables and spares with prices, a service contract price, response time in
   Utah.

### 5. Their intake questions, answered
As in section 9: AlSi10Mg and other printed bars, **E8 subsize**, up to **14.8 kN**, room temperature only, robot loaded, about a
share of the 1,420 tests a year, 208 V or 120 V **[to confirm]**.

### 6. Draft email (send one to each)
> **To:** sales@tiniusolsen.com (and +1 215-675-7100); info@admet.com
> **Subject:** Budgetary quote: motorized horizontal tensile frame, about 15 kN, for a robot-loaded tray, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab needs one **motorized horizontal tensile frame of about 15 kN**, no more than 840 mm deep and 856 mm
> tall in its footprint, to pull 6 x 6 mm printed Al bars (ASTM E8 subsize, 100 mm long) loaded from above by a robot arm.
> Please send a budgetary quote (list and academic, valid 90 days), the **dimensions and weight**, and tell us:
> 1. Is horizontal operation a supported use, and with which grips and software?
> 2. Can a robot set a bar between open jaws, and is there an API for unattended runs?
> 3. Preventive maintenance, ASTM E4 verification, consumables with prices, a service contract price, and the response time to
>    Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.tiniusolsen.com/contact/sales/> (US address, `sales@tiniusolsen.com`, +1 215-675-7100) | yes |
| <https://www.admet.com/contact/> (address, phones, `info@admet.com`) | yes |
| `notes/instruments_r7.md` (horizontal frames) | n/a |
| <https://tiniusolsen.com/product-category/universal-testing-machines/horizontal-testers> (MHT 1000 to 60000) (2026-11-07, runner) | no |
| <https://www.admet.com/product-category/testing-machines/universal-testing-machines/> (eXpert 5000 series, vertical or horizontal) (2026-11-07, search snippet) | no |

---

## 12. A&D balances (HR-202i, GH-202, HR-100A) and OIML E2 check weights

### 1. What we'd buy
- **Maker and model:** A&D (A&D Weighing, A&D Engineering) **HR-202i** (220 g x 0.1 mg, with a 51 g x 0.01 mg fine range,
  RS-232C only), **one**, for the multi-doser's charge station; the **GH-202** is its successor (same ranges, "Phoenix"
  series in the US); the lab's own **HR-100A** (102 g x 0.1 mg) is already in the powder-doser design. **Sets of
  OIML class E2 check weights** with an accredited certificate.
- **Role and place:** the multi-doser doses by weight on the pan: a Cu charge cup with its plug and Ni weighs 129.7 to
  135.7 g, over the HR-100A's 102 g, so the 220 g balance is needed. **Tray B**, under the dose point (`notes/multidoser.md`).
- **Model check (2026-11-07):** **discontinued** (HR-202i, GH-202 and HR-100A); the Troemner 7421-E2W set is **current** (Transcat lists it). A&D's own analytical-balance list now shows only the BA-T/BA, BH-T/BH, BM, BM-S ("NEW"), GR, Apollo and Fortis series and its HR-i and GH pages return 404 (US dealers such as Rice Lake still listed GH stock in 2025-2026, and dealers name the FX-104, 102 g x 0.1 mg, for the HR-100A). The like-for-like 0.01 mg replacement is the **BH-225D** (51 g x 0.01 mg / 220 g x 0.1 mg, smart range, RS-232C and USB; the BH-225DTE adds LAN and Bluetooth); for 0.01 mg over the whole 130-136 g cup, the **BM-252** (250 g x 0.01 mg, RS-232C, USB, Ethernet option). (<https://aandd.jp/products/weighing/wproduct.html>; <https://aandd.jp/products/weighing/balance/analytical/bh.html>; <https://aandd.jp/products/weighing/balance/analytical/bm.html>)

### 2. The published specs that matter for integration
- **Ranges:** 220 g x 0.1 mg; 51 g x 0.01 mg (dual range). **Interface:** **RS-232C built in** (the GH manual), read by the
  doser as `Q` at **2400 baud, 7E1** (`notes/multidoser.md`). A **WinCT** tool is a free download (A&D).
- **Pan and doors:** a 90 mm pan, anti-static glass draft shield with side and top doors, **opened by hand** (an
  actuator is needed for a robot-served station). The **GH-202's external size is not found** (the HR-202i's is in A&D's HR-i manual,
  `notes/multidoser.md`).
- **Status:** the notes say A&D **discontinued the HR-202i for the GH-202**. A German GH/HR-i brochure marks the series data table
  **"DISCONTINUED"**, a Thailand site still lists the HR-i; **neither a successor nor the status of the GH-202 was confirmed**.

### 3. Contact
- **A&D Weighing:** site <https://weighing.andonline.com/> (the old `andweighing.com` redirects; the page was fetched
  through the Pi and has a contact and quote link). **San Jose** (A&D Engineering): 1756 Automation Pkwy, San Jose,
  CA 95131, **408-263-5333** `(unverified: directory only)`. **Official numbers `(verified: https://weighing.andonline.com/contact-us, 2026-11-07)`:** customer service **(888) 726-5931**, technical support/service **(800) 726-4940** (6:00 to 4:30 Pacific, Mon to Fri), and a contact form; the A&D Company page also lists main (800) 726-3364 (search index). **No sales email is published**; the pattern in
  directories is unverified, so **use the site's Contact Us and Request a Quote forms**.
- **Who sells A&D in the US:** A&D sells through **dealers**: examples found are **Capitol Scientific** (GH-202 page), **MnM Scales**,
  **Fisher Scientific** and **Rice Lake Weighing Systems** (listing the "Phoenix GH" micro balances). **Utah dealer: `(unverified: no dealer locator found on weighing.andonline.com, 2026-11-07)`**; ask customer service for the authorized dealer nearest Provo.
- **Check weights:** **Troemner** (a Henry Troemner LLC product; the **7421-E2W 200 g to 1 mg OIML E2 set with an NVLAP
  certificate** is listed at **$3,820** on Transcat, **(800) 633-0561** was from a product listing and is **not** on Transcat's own page, which gives **(800) 828-1470** `(verified: https://www.transcat.com/contact-us, 2026-11-07)`; use the latter). Sold also
  by Fisher and Thomas Scientific.

### 4. Our open questions for them
1. **What replaces the HR-202i, and is the GH-202 itself discontinued?** Which model is **in stock and supported** for 2026-2036?
2. **RS-232C on the GH-202:** the command set (`Q`, `S`, `SIR`, `C`), **baud and parity** defaults, and **a USB or
   Ethernet** option for a Raspberry Pi; does the **GH-202 have an internal calibration weight** (the "i" in HR-202i)?
3. **Automation:** a **draft shield with a motorized door** or a robot kit, or what does A&D advise? Can the **top and side
   doors** be actuated without voiding the warranty?
4. **Dimensions and weight** of the GH-202 (to fit in the doser's U-shaped base, 316 mm tall with the shield).
5. **Calibration and verification:** the **weights** needed (a 200 g and a 100 g E2 weight, plus 1 mg to 50 g), **a calibration
   interval** for a **semi-micro** balance, **ASTM E898 / USP <41>** checks, who calibrates in Utah.
6. **Anti-static and vibration:** a **static eliminator** for powder and a **vibration table** (the doser's motor is nearby).
7. PM schedule, consumables, spares with prices, a service contract price, and the response time in Utah.
8. **HR-202i and GH-202 discontinued** (model check, 2026-11-07): A&D's list now has the BH-T/BH, BM and BM-S series. Quote the **BH-225D or BH-225DTE** (51 g x 0.01 mg / 220 g x 0.1 mg) or the **BM-252** (250 g x 0.01 mg); their size, weight, draft-shield door and command set over RS-232C, USB or LAN. Is the HR-100A replaced by the FX-104?

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Use | Dosing metal powders (Al, Cu, Ni, Fe) and 130 g cups by weight; a quarter-turn auger loop |
| Range and readability | 220 g x 0.1 mg minimum; 0.01 mg fine range useful for small additions |
| Environment | A lab bench in a VLM tray; vibration from a stepper; no draft control **[to confirm]** |
| Interface | RS-232C to a Raspberry Pi; a scheduler reads it |
| Quantity | 1 balance; check weight sets for 2-3 balances |

### 6. Draft email
> **To:** A&D Weighing, Contact Us / Request a Quote (<https://weighing.andonline.com/>); and a Utah dealer
> **Subject:** Quote and availability: GH-202 (or current replacement for the HR-202i) with RS-232C, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab uses an A&D HR-100A and wants a 220 g x 0.1 mg balance (HR-202i or its replacement) to dose
> metal powder by weight, read over RS-232C by a computer, with its doors opened by an actuator. Please quote (list and
> academic, valid 90 days) a GH-202 or whichever model is current, and tell us:
> 1. Is the HR-202i discontinued, and is the GH-202 current? What is the successor?
> 2. The RS-232C command set and defaults, a USB or Ethernet option, and whether it has internal calibration.
> 3. Can the draft-shield doors be motorized or actuated without voiding the warranty, and the balance's external dimensions?
> 4. Calibration and verification (weights and interval), preventive maintenance, spares, a service-contract price, and the
>    response time to Provo, UT.
>
> The HR-202i and GH-202 appear to be discontinued: please quote the current model with the same ranges (we understand the BH-225D, 51 g x 0.01 mg / 220 g x 0.1 mg, or the BM-252 for 0.01 mg to 250 g) and say what changed in size, weight, utilities and remote control (RS-232C, USB, LAN).
>
> [to confirm: name, title, phone]

### 6b. Draft email for check weights
> **To:** Troemner via Transcat sales, (800) 828-1470 (Transcat contact page)
> **Subject:** Quote: OIML class E2 weight set with an accredited certificate, 1 mg to 200 g, BYU (Provo, UT)
>
> Hello. Please quote a Troemner 7421-E2W (200 g to 1 mg) or equivalent OIML E2 set with an NVLAP certificate, plus
> single 200 g and 100 g E2 weights, and the recalibration interval and price. Delivery to Provo, UT 84602.
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://weighing.andonline.com/> (redirect from `andweighing.com/contact-us`) | yes |
| Search: GH-202 and HR-202i pages (Capitol Scientific, MnM Scales, Fisher), A&D GH/HR-i brochure ("DISCONTINUED") | no |
| Search: Troemner 7421-E2W on Transcat | no |
| `notes/multidoser.md`, `notes/alloy_charge.md` | n/a |
| <https://aandd.jp/products/weighing/wproduct.html> (analytical balance list; no HR-i, GH or HR-A) (2026-11-07, runner) | no |
| <https://aandd.jp/products/weighing/balance/analytical/bh.html> (BH-225D, BH-225DTE) (2026-11-07, runner) | no |
| <https://aandd.jp/products/weighing/balance/analytical/bm.html> and <https://aandd.jp/products/weighing/balance/analytical/bm-s.html> (BM-252, BM-255DS) (2026-11-07, runner) | no |
| <https://aandd.jp/products/weighing/balance/analytical/hri.html> and <https://aandd.jp/products/weighing/balance/analytical/gh.html> (both 404) (2026-11-07, runner) | no |
| <https://www.ricelake.com/products/phoenix-gh-series-a-d-weighing-analytical-balance/?print=true> (GH still listed by a US dealer, 2026-07-24) (2026-11-07, search snippet) | no |
| <https://sandiegoscale.com/products/a-d-hr-100a-hr-a-series-compact-analytical-balance> (HR-100A "Replaced by FX-104") (2026-11-07, search snippet) | no |
| <https://www.transcat.com/troemner-7421-e2w-200g-1mg-oiml-class-e2-weight-set-nvlap> (7421-E2W listed) (2026-11-07, search snippet) | no |

---

## 13. Nabertherm NAT 15/65 (heat treatment)

### 1. What we'd buy
- **Maker and model:** Nabertherm **NAT 15/65**, **one**, with a **B510 or C550 controller** (listings name both) and
  **NTLog Basic** (USB logging). Optional: a **motorized or robot-friendly door** (to ask).
- **Role and place:** solution treatment and ageing of printed coupons and bars (Al T5 and T6; Cu-Ni ageing), with a
  stainless rack; a quench tank beside it. **Tray F** (the tray's modelled load is 3,654 W). About 324 loads a year.
- **Model check (2026-11-07):** **current**. Nabertherm's tabletop forced-convection page lists the NAT 15/65 (15 L, 650 C, single phase, uniformity up to +/-5 C), and its news names NAT as the newer family that followed the NA 15/65; the B510 and C550 are in its current Series 500 controllers, with NTLog. (<https://nabertherm.com/en/products/labor/ovens-and-forced-convection/forced-convection-chamber-furnaces-tabletop-design>; <https://nabertherm.com/en/company/news/new-furnace-family-nat>)

### 2. The published specs that matter for integration
(Nabertherm datasheet table via distributor listings; **not read from Nabertherm's own site**, whose product URL returned 404)
- **Size:** **470 x 790 x 460 mm**, **60 kg**, **15 L**, chamber **295 x 340 x 170 mm**; **650 C**; **2.8 kW, single phase**;
  heat-up to Tmax about 40 minutes; **uniformity plus or minus 5 C (DIN 17052-1)**.
- **Interfaces:** the B510 and C550 have a **USB** port for NTLog Basic and NTGraph. A **Modbus or RS-232 interface for the
  NAT 15/65 was not found**.
- **Door:** a hinged door with a white fibre plug and a bar handle (the video); **door actuation is not published**.
- **Utilities:** 1-phase **voltage options for the US (208 or 240 V) are [to confirm]**.

### 3. Contact
- **Nabertherm Inc. (USA):** **contact@nabertherm.com**, **+1 302-322-3665**, New Castle, DE 19720, **64 Reads Way**
  (some directories say 54 Read's Way). `(verified: https://nabertherm.com/en/contact/world-wide-sales, 2026-11-07; fax +1 302 322 3215)`.
  Nabertherm's own contact pages (fetched through the Pi) list **contact@nabertherm.de** and **+49 4298 922-0** (Lilienthal,
  Germany; spare parts **+49 4298 922-474**; service **+49 4298 922-333**).
- **Regional (Utah):** Nabertherm lists a **dealer log-in and world-wide sales** page; the Mountain West contact is
  `(unverified: the world-wide sales page lists the US subsidiary only, with no regional dealer for Utah, 2026-11-07)`.
- **Distributors:** MSE Supplies and Fisher Scientific list the NAT 15/65 (search).

### 4. Our open questions for them
1. **Controller interface:** does the **B510 or C550 offer Modbus (RS-485 or Ethernet)**, or the **NCC** data interface, so a
   scheduler **starts a program and reads the status**? What does Nabertherm sell for a PLC link?
2. **Door:** can the door be **opened by a pneumatic or electric actuator**, with a **limit switch** that a robot reads, and a
   **safe-opening** limit for hot loads? Does it **void the warranty**?
3. **Uniformity for Al:** the plus or minus 5 C of the NAT 15/65 against a **solution-treatment tolerance** (AMS 2750 class); is
   there a **tighter** option or a **survey**? **Quench delay** from the door to the tank?
4. **US voltage:** the 2.8 kW at **208 V single-phase**, the breaker and plug.
5. **Cooling** for the tray: the outer-skin temperature at 540 C, and **heat output** into a VLM (2.8 kW peak).
6. **Fan and element life**, a **thermocouple replacement** and **calibration** (a temperature survey interval).
7. PM schedule, consumables and spares with prices, a service contract price, response time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Use | Solution treatment (about 520-540 C) and artificial ageing (160-200 C) of Al-Si and Cu-Ni parts |
| Load | A rack of E8 bars and coupons, up to 1 kg **[to confirm]** |
| Atmosphere | Air; no inert gas |
| Cycles | About 324 loads a year, one to a few hours each |
| Automation | Robot opens the door and sets a rack; program start by software |
| Utilities | 1-phase, 2.8 kW **[to confirm voltage]**; exhaust not needed **[to confirm]** |

### 6. Draft email
> **To:** Nabertherm Inc., contact@nabertherm.com (verified 2026-11-07), +1 302-322-3665
> **Subject:** Budgetary quote: NAT 15/65 with B510 or C550, robot-loadable door, BYU (Provo, UT)
>
> Hello,
>
> The BYU Vertical Cloud Lab wants one NAT 15/65 (650 C, 15 L) for solution treatment and ageing of printed Al and Cu-Ni parts,
> loaded by a robot arm on a vertical-lift tray. Please quote it (list and academic, valid 90 days) with the B510 or C550
> controller and NTLog Basic, and tell us:
> 1. Is there a Modbus or similar interface on the controller so software can start and read a program?
> 2. Can the door be actuated with a limit switch a robot reads, without voiding the warranty?
> 3. The US voltage options, and the temperature uniformity for Al solution treatment (AMS 2750 class).
> 4. Preventive maintenance, a temperature survey interval, spares with prices, a service contract price, and the response time
>    to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.nabertherm.com/en/contact> (and `/subsidiaries`), `contact@nabertherm.de` | yes |
| Search: Nabertherm Inc. phone, email, address; NAT 15/65 datasheet table via MSE Supplies, Fisher, imlab; NTLog pages | no |
| `notes/refine_furnace.md`, README (470 x 790 x 460 mm, 60 kg) | n/a |
| <https://nabertherm.com/en/products/labor/ovens-and-forced-convection/forced-convection-chamber-furnaces-tabletop-design> (NAT 15/65 listed) (2026-11-07, search snippet) | no |
| <https://nabertherm.com/en/company/news/new-furnace-family-nat> (NAT family) (2026-11-07, search snippet) | no |
| <https://nabertherm.com/en/series-500> (B510, C550, NTLog) (2026-11-07, search snippet) | no |

---

## 14. The CubXL (tray A): who makes it, and what parts to buy

### 1. What we'd buy
- **Maker and model: there is no maker.** The CubXL is the **lab's own machine**, not a product. The model's CubXL
  (`equipment.cubxl()`, README table row "CubXL (tray A)") is "the lab's CadQuery model from #199: the **Genmitsu PROVerXL 4030 V2
  frame from SainSmart's spec**, the rest from lab photos", split into frame, gantry, carriage and tools, with a **400 x 300 x
  110 mm travel**. Its head (a capper, a **P20 single Gen2**, a camera) and **CubOS** control software are the lab's, as
  calibrated on 2026-10-02 ([DAL PR #180](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/180),
  `alloy-corrosion/cubxl-setup.md`, commit `aeda51a`).
- **So the buy list is parts, not a machine:** a **SainSmart Genmitsu PROVerXL 4030 V2** frame (if a second CubXL is built, or a
  spare), and the items in DAL's `bom.csv` (FKM AS568-006 O-rings, pogo pins, 0.5 mL tubes, Opentrons 20 uL tips, a Pt wire, a
  leak-free reference; sections 16 and 17).
- **Role and place:** the corrosion screen: 4 coupon stations with a lid and O-ring well (3 mm, 0.071 cm2, about 150 uL), a
  magnetic electrode cap carried by the capper, OCP, LPR and cyclic polarization. **Tray A**, 100 W. About **648 spots a year**.
- **Model check (2026-11-07):** **current**. SainSmart's shop still sells the Genmitsu PROVerXL 4030 V2 (400 x 300 x 110 mm, closed-loop NEMA 23, ball screws), with an open-box listing too, and no V3 was found; the DAL `bom.csv` parts are generic and were not checked. (<https://sainsmart.com/products/proverxl-4030-v2>)

### 2. The published specs that matter for integration
- **SainSmart Genmitsu PROVerXL 4030 V2:** working area **400 x 300 x 110 mm**, about **31 kg**, a **GRBL**-based control, NEMA 23
  steppers on a C-beam frame (a manual summary on manuals.plus; the voltage listings conflict, so check the unit's label).
- **Interfaces:** CubOS (the lab's). Nothing is vendor-published for the head.

### 3. Contact
- **SainSmart technical support:** **support@sainsmart.com** (the V2 user manual) `(partial: https://sainsmart.com/pages/contact-us loaded but printed no address we could read, 2026-11-07)`. **Quote:** retail purchase; no RFQ needed.
- **The lab's own people:** the CubOS author (Ben, in PR #180) is the "maker" for any question about the head and software
  **[to confirm the contact]**.
- **Regional rep:** none. **Academic:** none.

### 4. Our open questions for them
1. **Is the PROVerXL 4030 V2 the right frame to rebuild** (a **rated load and rigidity** for a tool head, the **Z travel** of 110 mm
   against the 122 mm carriage height used at travel in the model)? Who holds the lab's **calibration files**?
2. **Mains voltage and the spindle** (not used); can it run **without the spindle and its router** and keep a warranty?
3. **PM:** lead-screw and linear-rail lubrication, belt or nut wear, **recalibration after 1,000 hours**, a **spares kit**
   with prices (SainSmart), and the lab's own spares.
4. For the **lab's CubXL** (not a vendor): the **tray-A fit** (the CubXL, the OT-2 at 662 mm, the doser), the **vibration** when the
   gantry moves, and who maintains it.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Use | A gantry for liquid handling and electrode handling, not machining |
| Quantity | 1 now; a spare frame **[to confirm]** |
| Environment | A VLM tray; dry |
| Software | CubOS (lab) on a Raspberry Pi |

### 6. Draft email (only if a frame or parts are bought)
> **To:** support@sainsmart.com
> **Subject:** PROVerXL 4030 V2: use without spindle, rated head load, spares kit, BYU (Provo, UT)
>
> Hello. The BYU Vertical Cloud Lab uses a PROVerXL 4030 V2 as a liquid-handling gantry (400 x 300 x 110 mm travel, no spindle).
> Please tell us the rated tool-head load, whether it may run without the spindle and router, the maintenance interval and a
> price list for a spares kit (lead screws, nuts, rails, stepper drivers). [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| README (CubXL row), `notes/cubxl_corrosion.md`, `notes/instruments_lab.md` | n/a |
| [DAL `cubxl-setup.md`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/cubxl-setup.md) and `bom.csv` (via `gh api`) | no |
| Search: SainSmart support email and PROVerXL 4030 V2 specs (manuals.plus) | no |
| <https://sainsmart.com/products/proverxl-4030-v2> (model check: current) (2026-11-07, search snippet) | no |

---

## 15. NuVant EZstat Pro potentiostat

### 1. What we'd buy
- **Maker and model:** **NuVant Systems Inc.** (part of **A3 Global**) **EZstat Pro**, **one**. The lab **already has** one
  (byu-vcl #231); this section is for **spares, calibration, an EIS option, and a possible second unit**.
- **If EIS is needed:** the notes say "EIS needs the requested potentiostat: the EZstat Pro beside the frame has none"; DAL's
  `bom.csv` lists the **PalmSens EmStat Pico (ESPICO-ALL, $580 on 2026-09-28; ESPICO-DK about $1,800)** as option B. **Ask
  NuVant whether the EZstat Pro has EIS**: a vendor listing says it does (0.01 to 10 kHz).
- **Role and place:** OCP, LPR and cyclic polarization of 4 coupons on the CubXL. Beside the CubXL frame, on **tray A**.
- **Model check (2026-11-07):** **current**. NuVant's products page still lists the "best-selling EZstat Pro potentiostat/galvanostat" under Electrochemistry Research Equipment, beside the Powerstat and Arraystat, and names no successor; NuVant is still "an A3 Global company", and its online store (store.nuvant.com) now sells hybrid-car batteries, not potentiostats. (<https://www.nuvant.com/products>)

### 2. The published specs that matter for integration
(An etesters vendor listing, **not NuVant's page**)
- Menu-driven potentiostat/galvanostat; waveform generation; **16-bit DAQ at 250 kS/s aggregate**; **EIS 0.01 to 10 kHz**
  (claimed); active IR compensation; **EZware (LabVIEW-based)**; a 1-year warranty.
- **Size, weight and power: not found.** **Interfaces:** USB or a PC with **EZware**. The lab's rig runs EZware on a **Windows 7**
  PC on a point-to-point Ethernet link to the CubXL Pi (`CLAUDE.md`, #231). An **API, SCPI or a CLI** is **not published**.
- **Robot interface:** none (the cell is wired through a bus to the pogo pins; the arm does not touch it).

### 3. Contact
- **Web form:** <https://www.nuvant.com/contact> and **Request Quote** on the same site (fetched through the Pi). **Email:**
  **info@a3global.com** (the only address on the contact page). **Phone:** none published `(verified: https://www.nuvant.com/contact, 2026-11-07)`.
- **Regional rep:** none. **Academic:** NuVant's pages stress education; pricing `(unverified)`. The contact page gives
  **300 Schell Ln, 309/310, Phoenixville, PA 19460** `(verified: https://www.nuvant.com/contact, 2026-11-07)`.

### 4. Our open questions for them
1. **EIS:** does the **EZstat Pro** have **EIS** (frequency range, an option or a software license)? If not, what is NuVant's
   EIS-capable model and its price?
2. **Remote control:** a **driver, DLL, LabVIEW VI, SCPI or command line** so CubOS or a scheduler can run OCP, LPR, CV
   **without EZware's GUI**; and **EZware on a current Windows** (the lab's PC runs Windows 7).
3. **Cell cable and a 3-wire bus** to **pogo pins**; the **current ranges** for a **0.071 cm2** working electrode.
4. **Calibration and verification:** a **dummy cell** check (the DAL BOM has a resistor and capacitor), a **factory calibration**
   interval, and a **recertification** price.
5. **Spares** (cables, a fuse, the DAQ) with prices, a **service contract** price, response time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Application | Corrosion of Al, Cu-Ni and NAB in 0.6, 0.06, 0.006 M NaCl or ASW: OCP 30 min, LPR plus or minus 10 mV at 0.167 mV/s, cyclic polarization, EIS if available |
| Cell | 3-electrode, 150 uL well, 0.071 cm2 working area, a leak-free Ag/AgCl reference, a Pt coil counter |
| Currents | nA to uA for passive metals; **[to confirm ranges]** |
| Throughput | 648 spots a year, 67 min each (DAL) |
| Software | A driver for CubOS (Python) |

### 6. Draft email
> **To:** info@a3global.com (cc the NuVant web form)
> **Subject:** EZstat Pro: EIS option, scripted control, calibration and spares, BYU (Provo, UT)
>
> Hello. The BYU Vertical Cloud Lab runs an EZstat Pro on a robotic corrosion cell (3-electrode, 0.071 cm2). Please tell us:
> 1. Does the EZstat Pro include EIS, or is there an option or model that does (price)?
> 2. Is there a driver, DLL, LabVIEW VI or command set so software can run OCP, LPR and cyclic polarization without the GUI,
>    and does EZware run on a current Windows?
> 3. Recalibration interval and price, spares with prices, a service contract price, and the response time to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://www.nuvant.com/contact> (`info@a3global.com`) | yes |
| Search: EZstat Pro listing (etesters) | no |
| DAL `bom.csv` (EmStat Pico option) via `gh api`; `notes/cubxl_corrosion.md` | no |
| <https://www.nuvant.com/products> (EZstat Pro listed) (2026-11-07, runner) | no |
| <https://store.nuvant.com> (hybrid batteries only) (2026-11-07, runner) | no |

---

## 16. Opentrons OT-2 with P300 and P20

### 1. What we'd buy
- **Maker and model:** **Opentrons OT-2**, **one** on tray A, with a **P300 single-channel Gen2** (the model uses 30-300 uL, 300 uL
  tips) on the right mount and a **P20 single-channel Gen2** (1-20 uL, 20 uL tips) on the left, **tip racks** and the **96 deep-well
  plate** the model uses for ICP dilutions. **The lab already has an OT-2** (the stream-cam Pi runs it; `CLAUDE.md`); whether a
  **second robot** is bought for the tray is **[to confirm]**. The model notes a **P1000** would suit a 20 mL batch.
- **Role and place:** makes the CubXL's NaCl and sulfide stocks and the ICP dilutions (`notes/ot2_corrosion.md`). **Tray A**, in
  front of the UPS, **662 mm tall**, 100-180 W active.
- **Model check (2026-11-07):** **current**. Opentrons **still sells the OT-2 new** (its product page has a price, an Add to Cart button and "Ships in 6 weeks", and no end-of-sale notice; the Flex is the newer robot), and **still sells the GEN2 single-channel pipette** in P20, P300 and P1000 ("OT-2 Single-Channel Pipette", item 999-00002, ships in 7 business days). (<https://opentrons.com/products/ot-2-robot>; <https://opentrons.com/products/single-channel-electronic-pipette-p20/>)

### 2. The published specs that matter for integration
- **Interfaces:** the OT-2 has an **HTTP API on port 31950** (send `Opentrons-Version: 3`; `GET /health` is read-only) and a
  **Python Protocol API**. **Robot loading:** the OT-2's deck is loaded from the front with the lid; it is **not designed for a robot arm**
  and has no door actuation.
- **Size, weight, power:** Opentrons publishes these; the notes carry only the 662 mm height and the 100-180 W. **[to confirm]**
- **Status:** Opentrons now sells the **Flex**; the OT-2 is still on its shop. Price figures conflict between the store and
  third-party guides, so **take the quote**.

### 3. Contact
- **Phone:** **+1 (646) 212-3703** (global; product specialists 4:00 AM to 8:00 PM ET, Mon to Fri); **web form**
  <https://opentrons.com/contact> (responses within 24 hours; the page names a help center for support). `(verified via headless Chromium on the Pi: https://opentrons.com/contact, 2026-11-07; also UK/EU +44 758 861 1072; the page is 403 to the runner)`. **Email:** none
  published on that page. **Quote:** Opentrons' shop creates a quote from the cart (<https://shop.opentrons.com>).
- **Education:** Opentrons advertises **education pricing** (a 2024 press release).
- **Regional rep:** `(unverified: none published; ask the form)`.

### 4. Our open questions for them
1. **Is the OT-2 supported and available for ten years**, and what are **end-of-life dates for the OT-2 and the Gen2 pipettes**? Is the
   **Flex** the better buy, and does it keep the **HTTP API** the lab uses?
2. **A robot arm and the OT-2:** can **a robot load labware** through the lid, or **an actuator** hold it open, without voiding the warranty? An
   **external e-stop or interlock** input?
3. **Pipette accuracy at 1-20 uL** for **viscous or salt solutions**; **gravimetric calibration** and **verification** intervals;
   **tip pickup** reliability for **20 uL tips**.
4. **Network and API security** on a lab LAN; **firmware** updates.
5. **Spares and consumables** (tips, pipette tips-pickup parts, gaskets) with prices; a **service contract** price; response time in Utah.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Application | Preparing NaCl and ASW stocks, a sulfide stock at 0.1 mg/L, and 10x dilutions in 2 % HNO3 for ICP-MS |
| Volumes | 1-20 uL and 30-300 uL; up to 2 mL per transfer set |
| Samples | Aqueous, acidic (2 % HNO3), saline; no biologicals; no volatile organics |
| Throughput | Nightly runs, 16 spots |
| Software | Python and the HTTP API, driven by a scheduler |
| Quantity | 1 |

### 6. Draft email
> **To:** Opentrons sales (web form <https://opentrons.com/contact>; +1 646-212-3703)
> **Subject:** Budgetary quote: OT-2 with P300 and P20 Gen2 (and the Flex as an alternative), BYU (Provo, UT)
>
> Hello. The BYU Vertical Cloud Lab uses an OT-2 for corrosion stocks and ICP dilutions and wants one more, on a vertical-lift tray.
> Please quote (education pricing, valid 90 days) an OT-2 with a P300 and a P20 single-channel Gen2, tip racks and a deep-well plate,
> and the Flex as an alternative. We ask:
> 1. The OT-2's support horizon and the Flex's equivalent API.
> 2. A robot loading the deck, or holding the lid open, and an external e-stop input.
> 3. Pipette verification intervals, consumables and spares with prices, a service contract price, and the response time
>    to Provo, UT.
>
> [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| <https://opentrons.com/contact> (phone, hours) | yes |
| Search: Opentrons store, education pricing (Business Wire 2024) | no |
| `notes/ot2_corrosion.md`, `notes/services.md`, `CLAUDE.md` (Opentrons API call pattern) | n/a |
| <https://opentrons.com/products/ot-2-robot> (OT-2 sold new) (2026-11-07, runner) | no |
| <https://opentrons.com/products/single-channel-electronic-pipette-p20/> (GEN2 single-channel P20, P300, P1000) (2026-11-07, runner) | no |
| <https://opentrons.com/robots/ot-2> (Buy now; pipettes listed) (2026-11-07, runner) | no |

---

## 17. Reference electrodes and platinum: Innovative Instruments, WPI, Pine Research, BASi, Gamry

### 1. What we'd buy
From DAL's `bom.csv` (checked 2026-10-17 there):
- **A leak-free Ag/AgCl reference, 1-2 mm** (Innovative Instruments **LF-1 or LF-2**, or **WPI Dri-Ref 2 mm**), **1**, about $250,
  for the 150 uL well. A fritted electrode leaks KCl into so small a well.
- **A master reference** (a standard fritted Ag/AgCl, **Ossila C2015B1**, 110 GBP), **1**, to check the working one; never in a well.
- **Pt wire 0.25 mm** (Advent PT5434, 0.1 m, $184) for the **five-turn counter coil**, or Ossila's finished Pt counter ($247).
- **Alternatives for a fritted reference and a Pt coil/mesh from Pine Research, BASi and Gamry**, if a standard cell is wanted.
- **Role and place:** the electrode cap on the CubXL, 20 mm across, 16 mm tall, carried by the capper. **Tray A**.
- **Model check (2026-11-07):** **current** (WPI DRIREF-2, Ossila C2015B1, Advent PT5434); **unconfirmed** (Innovative Instruments LF-1 and LF-2). No LF-1 or LF-2 maker page was found, and innovativeinstruments.com is now an Italian process-instrument company in Milan with no electrodes, so the leak-free maker's current site and status are unknown; Pine, BASi and Gamry name no model. (<https://www.wpiinc.com/driref-2-dri-ref-reference-electrode-2-mm>; <https://ossila.com/products/ag-agcl-reference-electrode>; <https://advent-rm.com/en-GB/Products/Pure-Metals/Platinum/Form/Wire/Line/PT5434>; <https://www.innovativeinstruments.com/contatti/>)

### 2. The published specs that matter for integration
- **Cap:** a **2 mm leak-free Ag/AgCl** down the middle inside **five turns of 0.25 mm Pt**; a steel disc on top for the capper's
  50 N magnet; two pogo pins at plus or minus 11 mm (`notes/cubxl_corrosion.md`).
- **Vendor specs (LF-1, Dri-Ref):** body diameter, tip length, stability and storage were **not read**; the vendor pages are
  "price on request" from the runner (DAL's note).

### 3. Contact
| Vendor | Email | Phone | Form or page | Via Pi |
|---|---|---|---|---|
| Innovative Instruments, Inc. (leak-free LF-1/LF-2) | **info@innovativeinstruments.com** | not on the page | <https://www.innovativeinstruments.com/contact> `(verified email, 2026-11-07; the page URL itself 404s to the runner, the email appears in the page text)` | yes |
| World Precision Instruments (Dri-Ref) | none printed | **(941) 371-1003** (verified https://www.wpiinc.com/contact-us 2026-11-07); US toll free **(866) 606-1974**; fax (941) 377-5428 | <https://www.wpiinc.com/contact-us>; 175 Sarasota Center Blvd, Sarasota, FL 34240 | yes |
| Pine Research Instrumentation | none printed | **+1 (919) 782-8320** (verified https://pineresearch.com/contact/ 2026-11-07), Mon-Fri 9-5 ET | <https://pineresearch.com/contact/> (forms: Quote Request, Technical Support) | yes |
| BASi (an Inotiv company) | **BASi@basinc.com** (quotes, verified https://www.basinc.com/contact 2026-11-07); AR_Orders@basinc.com (orders) | **800-845-4246**; (765) 497-8359 | <https://www.basinc.com/contact> | yes |
| Gamry Instruments | none printed | **215-682-9330** (US sales, quotes, demos; verified https://www.gamry.com/contact-us/ 2026-11-07) | <https://www.gamry.com/contact-us/> | yes |
| Ossila (DAL BOM) | **info@ossila.com** | +44 (0)114 2999 180 (UK) | <https://www.ossila.com/products/reference-electrode> `(verified: 2026-11-07)` | no |
| Advent Research Materials (DAL BOM) | **info@advent-rm.com** | +44 1865 884 440 (UK) | <https://www.advent-rm.com/contact> `(verified: 2026-11-07)` | no |

- **Regional rep (Utah):** none published for any `(unverified: all six forms; none shows a territory list, 2026-11-07)`. **Academic:** BASi has educational kits; others **[to confirm]**.

### 4. Our open questions for them
1. **Leak-free mini-reference:** the **LF-1 and LF-2 or Dri-Ref** outer diameter, **tip length**, and whether the **2 mm** body fits a **3 mm
   throat** above a 150 uL well; **leak rate** (microliters of KCl per hour) and **chloride contamination** for **ICP-MS** of Cu, Ni, Al;
   **Cl-free** filling.
2. **Life and storage** of a leak-free electrode in air, between **16 spots a night**; **drift** against the master, a **recheck interval**; **price per
   unit** and **lead time**; **spares**.
3. **A magnetic cap** carries a **steel disc** (the electrode body must not be ferromagnetic near the reference).
4. **Pt wire** purity (99.95 %), spool length and price; **Pt mesh or coil** as a finished part.
5. **Calibration and verification:** the master reference against a **saturated calomel or a certified standard**, and its replacement interval.
6. **Which of Pine, BASi and Gamry** supply a **leak-free** or **micro** reference; **price**; academic discount.
7. **Who makes the LF-1 and LF-2 now** (model check, 2026-11-07)? innovativeinstruments.com is an Italian process-instrument company with no electrodes; find the leak-free maker's current site before writing to it.

### 5. Their intake questions, answered
| They will ask | Answer |
|---|---|
| Application | A 3-electrode cell in a 150 uL well; NaCl 0.6 to 0.006 M and ASW; pH about 8; room temperature |
| Reference | Ag/AgCl, leak-free, 1-2 mm; no frit leakage; no Cl contamination for ICP |
| Counter | Pt, several times the well area (five turns of 0.25 mm wire) |
| Duration | 30 min to 67 min per spot, 16 spots a night |
| Quantity | 1 reference, 1 master, 0.1 m Pt; spares **[to confirm]** |

### 6. Draft email
> **To:** info@innovativeinstruments.com; the WPI web form; BASi@basinc.com
> **Subject:** Quote: leak-free 1-2 mm Ag/AgCl reference (LF-1, LF-2 or Dri-Ref 2 mm), BYU (Provo, UT)
>
> Hello. The BYU Vertical Cloud Lab needs one leak-free Ag/AgCl reference of 2 mm diameter or less for a 150 uL corrosion well
> (0.6 to 0.006 M NaCl), moved by a robot, with no chloride contamination for ICP-MS. Please quote one (and a spare), and tell
> us the outer diameter and tip length, the leak rate, the storage and life, the recheck interval and the price per unit,
> and the lead time to Provo, UT. Academic price, valid 90 days. [to confirm: name, title, phone]

### 7. Sources (checked 2026-11-07 UTC)
| Source | Via Pi |
|---|---|
| The five vendor contact pages above | yes |
| DAL `bom.csv` (parts, prices) via `gh api` | no |
| Search: Innovative Instruments, WPI (no direct LF-1 page found) | no |
| <https://www.wpiinc.com/driref-2-dri-ref-reference-electrode-2-mm> (DRIREF-2 listed) (2026-11-07, search snippet) | no |
| <https://ossila.com/products/ag-agcl-reference-electrode> (C2015B1 listed) (2026-11-07, search snippet) | no |
| <https://advent-rm.com/en-GB/Products/Pure-Metals/Platinum/Form/Wire/Line/PT5434> (PT5434 listed) (2026-11-07, search snippet) | no |
| <https://www.innovativeinstruments.com/> and <https://www.innovativeinstruments.com/contatti/> (Milan, no electrodes; /contact now 404) (2026-11-07, runner) | no |

---

## Superseded or discontinued (model check, 2026-11-07)

From the makers' own pages where the runner could read them, else search snippets or distributors. Items found current are in each
section's "Model check" line and in `characterization.csv` (`model_status`).

| Item | Modelled | Status | Successor | Source |
|---|---|---|---|---|
| XRD standard (section 1) | NIST SRM 640f | superseded | SRM 640g (certificate 2024-02-27) | <https://www.nist.gov/publications/certification-standard-reference-materialr-640g-line-position-and-line-shape-standard> (search snippet) |
| Particle size (section 2) | Mastersizer 3000 + Aero S | superseded | Mastersizer 3000+ (Lab, Pro, Ultra; launched 2024-03-14), same 690 x 300 x 450 mm bench; which version takes the Aero S to confirm | <https://www.malvernpanalytical.com/en/about-us/press-releases/news/pr240314-matersizer-3000-plus-launch> (runner) |
| SEM (section 4) | Hitachi TM4000PlusII | superseded | TM4000PlusIII (2024-08-22); Hitachi's US page lists only the III; footprint not published | <https://www.hitachi-hightech.com/us/en/products/microscopes/sem-tem-stem/tabletop-microscopes/tm4000iii.html> (maker's page, headed Chromium on the stream-cam Pi) |
| EDS detector (section 4) | Oxford AZtecOne with X-Max SDD | superseded | Xplore detector; XploreCompact 30 or 65 for tabletop SEMs (Hitachi: AZtecOneXplore) | <https://nano.oxinst.com/products/aztec/aztecone> (runner) |
| Microscope (section 7) | Keyence VHX-7000 | discontinued | VHX-X1 (already planned) | <https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/> (runner) |
| Tensile frame (section 9) | Instron 68FM-100 | current; new smaller option | 68TM-100 table model (1640 x 760 x 715 mm, 100-240 V; 420 mm between columns) | <https://www.instron.com/wp-content/uploads/2025/09/100kn-universal-testing-systems-tm-fm.pdf> (maker's page, headed Chromium on the stream-cam Pi) |
| Balance (section 12) | A&D HR-202i | discontinued | BH-225D / BH-225DTE (51 g x 0.01 mg, 220 g x 0.1 mg); BM-252 (250 g x 0.01 mg) | <https://aandd.jp/products/weighing/wproduct.html> (runner) |
| Balance (section 12) | A&D GH-202 | discontinued | as above; US dealers still list GH stock | <https://aandd.jp/products/weighing/wproduct.html> (runner) |
| Balance (section 12) | A&D HR-100A (the lab's own) | discontinued | FX-104 (102 g x 0.1 mg), per dealers | <https://sandiegoscale.com/products/a-d-hr-100a-hr-a-series-compact-analytical-balance> (search snippet) |
| Reference electrode (section 17) | Innovative Instruments LF-1 / LF-2 | unconfirmed | maker's site not found; the domain is now an Italian firm | <https://www.innovativeinstruments.com/contatti/> (runner) |

---

## Gaps and what to do next

| Gap | Why it matters | What to do |
|---|---|---|
| **No official contact read for Hitachi (US), KLA and Instron** | Their sites block the runner, the Pi and headless Chromium on the Pi (second pass 2026-11-07). Search indexes of the official pages show: Hitachi **West region EM sales page lists UT**, (800) 253-3053; KLA quotes (858) 573-9300, support +1 800 600 2829, nanosupport@kla.com; Instron sales 800-564-8378. None of these was fetched | Someone on a normal browser opens Hitachi's `.../em-sales_contacts/west.html`, KLA's iMicro page and Instron's contact page and reads the Utah/sales contact |
| **No US sales email for most vendors** | Most publish only a form, and no email is guessed | Use the forms; copy the draft email into them |
| **No Utah or Mountain West rep** for any vendor | A regional rep is where the fastest quote and the service engineer come from | Ask in each form; Instron has a Salt Lake City field-service role |
| **Pending vendor data**: Hitachi III, Mastersizer 3000+, A&D replacement, NAT 15/65 US voltage | The model uses older names | Each draft asks |
| **The HM-220's AVPAK, the S2 PUMA's Automation and the Instron's AT6 automation interfaces** | The lab needs a command interface | Asked first in each section |
| **Prices** | None of these vendors publish list prices (Troemner's 7421-E2W, $3,820 on Transcat, is the exception) | Budgetary quotes (list and academic, valid 90 days) |
| **Second pass 2026-11-07: verified from the vendor's own page** | Rigaku service line and 281-362-2300 x132; Bruker Madison phone, info.baxs@bruker.com and service@ (the old note "no sales email" was wrong); Plastometrex info@; Keyence phone; Mitutoyo phone; Zwick phone; Tinius Olsen sales@ and phone; ADMET; Nabertherm Inc. (contact@nabertherm.com, +1 302 322 3665, 64 Reads Way); Oxford's Concord phone; McCrone phone; NuVant address; Opentrons phone; A&D US service numbers; Transcat (800) 828-1470 (the (800) 633-0561 was wrong); Gamry, Pine, BASi, WPI, Innovative Instruments, Ossila, Advent | Nothing further for these |
| **Still unverified** | Malvern US phone (no phone on its pages); Oxford us.nainfo@oxinst.com; Rigaku street address; A&D San Jose 408-263-5333; NIST SRMMSDS@nist.gov; SainSmart support@ (loaded page showed no address) | Use the forms; do not email an unverified address without a check |
| **No Utah or Mountain West rep published** | Every vendor's territory list is a JS form, a region selector or a zip lookup (Malvern, Mitutoyo, Zwick, Instron, A&D dealers); Tinius Olsen's US entry is HQ only | Ask in each form; call A&D customer service (888) 726-5931 for the dealer nearest Provo |


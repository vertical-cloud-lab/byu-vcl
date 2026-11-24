# Unit costs and gas-atomizer sizes: the research behind plan.py and gas_atomizer.py


Web research, compiled 2026-11-24. No vendor contact, no sign-ups.

## How to read this

- **Public procurement records are the backbone.**
  - US federal awards come from the public USAspending API (`api.usaspending.gov`).
  - EU and UK awards come from the TED search API (`api.ted.europa.eu`).
  - Each record links to the human-readable award page.
- **What an award amount covers.** It is the obligated total of one order. It often includes installation, training, freight and accessories, and sometimes more than one unit. The description says what was bought, and is quoted where it matters.
- **Currency conversions are rough planning rates, not dated rates.** 1 EUR ≈ 1.10 USD, 1 GBP ≈ 1.30 USD, 1 USD ≈ 7.1 CNY, 1 USD ≈ 17–18 ZAR. They are marked "≈".
- **Confidence labels:**
  - **Procurement record**: an award or contract value.
  - **List/retail**: a distributor's web price.
  - **Vendor guidance**: the maker's own published cost rule of thumb.
  - **Auction/used**: an asking price.
  - **Aggregator/estimate**: an unsourced third-party figure.
  - **UNCONFIRMED**: could not be verified against a primary source.

---

## Part A: prices

| Item | Price or range | Year / currency | Source URL | Confidence |
|---|---|---|---|---|
| **VLM: Kardex Shuttle (any)**: cost per height | $6,000–8,000 per vertical foot "as a starting point"; FAQ gives ~$95,000 baseline for a standard VLM; a taller unit is cheaper per ft³ | 2025 (article dated 12/11/25), USD | https://www.kardex.com/en-us/blog/how-much-does-a-vertical-lift-module-cost | Vendor guidance |
| VLM: dealer rule of thumb | $6,500–8,500 per linear foot of height | ~2025, USD | https://www.southwestsolutions.com/automated-storage/vertical-lift-module/ | Dealer guidance (from search excerpt, page not re-fetched) |
| **Kardex Shuttle XP 500, 2450 × 864 mm trays, 4,850 mm tall** (P/N XP500-2450-864-4850) | $108,000 (1 unit) | 2019, USD | https://www.usaspending.gov/award/CONT_AWD_FA301619PA255_9700_-NONE-_-NONE- | Procurement record (USAF, JBSA Lackland) |
| Kardex Shuttle XP HD500, 2450 × 864 × 5,850 mm | $103,098 per order. Three identical orders were placed in 2018. | 2018, USD | https://www.usaspending.gov/award/CONT_AWD_SPE8E318F863T_9700_SPE8EG14D0010_9700 | Procurement record (DLA) |
| Kardex Shuttle XP HD500, 1850 × 864 × 4,950 mm | $86,474 | 2019, USD | https://www.usaspending.gov/award/CONT_AWD_FA302019PA045_9700_-NONE-_-NONE- | Procurement record (USAF) |
| Kardex XP500 VLM (size not given) | $234,645 | 2024, USD | https://www.usaspending.gov/award/CONT_AWD_SPE8E324FB9SC_9700_SPE8E324D0002_9700 | Procurement record (DLA). Size and quantity not stated. |
| "Kardex Shuttle 500 VLM 96.46 in × 34 in" (2450 × 864 mm trays) | $888,701 per order | 2025, USD | https://www.usaspending.gov/award/CONT_AWD_SPE8E325FB52Q_9700_SPE8E324D0024_9700 | Procurement record (DLA). Quantity not stated, probably several units. |
| Shuttle XP VLM via GSA (MSC Industrial) | $446,712 and $408,339 (two 2024 orders) | 2024, USD | https://www.usaspending.gov/award/CONT_AWD_47QSCC24F5ZJR_4732_47QSCC21A0004_4732 | Procurement record. Quantity not stated. |
| Kardex Shuttle **XLD** 500, 2450 × 864 mm trays (96.46 in × 34 in), 22 ft 1.75 in (6.75 m) tall, 138 trays, 1,102 lb (500 kg) per tray | $213,291 sale price ($350,469 "list"). Freight and installation are extra. | ~2026, USD | https://storemorestore.com/shelving-and-racks/industrial-shelving/kardex-shuttle-xld-500-vertical-lift-module-96-x-34-heavy-duty-storage-trays | List/retail. The XLD is a heavy-duty sibling of the XP. |
| Kardex Shuttle XP 500 (aggregator) | $120,000 "MSRP" (16 m height listed) | listing updated 4/2026, USD | https://robotomated.com/explore/warehouse/kardex-shuttle-xp-500 | Aggregator. UNCONFIRMED and probably too low for 16 m. |
| Used Kardex Shuttle XP 500, 2450 × 813 mm, 7.65 m, 2016 | EUR 30,800 ex works, excluding shipping and installation | ~2025, EUR | https://www.relevatorgroup.com/vertical-storage-systems/vertical-lift-modules/kardex-shuttle-xp-500-2450x813-vertical-lift-module-2 | Auction/used |
| Shuttle 250/500 spec envelope (for modelling) | Max height 30,050 mm. Tray width up to 4,050 mm. Unit width 1,580–4,380 mm, depth 2,312–3,074 mm. Up to 560 kg per tray. | current | https://www.kardex.com/en-us/products/shuttle-vertical-lift-modules | Vendor spec |
| **AMAZEMET rePowder** (Basic system, focused plasma melting, 40 kHz, suction casting, O2 sensor, 1 yr maintenance) | $286,720 | 2023, USD | https://www.usaspending.gov/award/CONT_AWD_80MSFC24PA004_8000_-NONE-_-NONE- (notice: https://www.highergov.com/contract-opportunity/notice-of-award-of-sole-source-ultrasonic-atomizer-23-80-msfc-p-8c2de/) | Procurement record (NASA MSFC, sole source via A3DM Technologies) |
| AMAZEMET (via A3DM): "Atomizer for NIST" | $321,595 | 2024, USD | https://www.usaspending.gov/award/CONT_AWD_1333ND24PNB640536_1341_-NONE-_-NONE- | Procurement record. Model not stated; A3DM is AMAZEMET's US channel. |
| AMAZEMET ultrasonic atomizer, Hochschule Aalen | EUR 407,700 (≈ $450k) | 2025, EUR | https://ted.europa.eu/en/notice/-/detail/320960-2025 | Procurement record (TED award, winner AMAZEMET Sp. z o.o.) |
| "Modulare Verdüsungsanlage", Universität der Bundeswehr München (direct award) | EUR 196,350 | 2025, EUR | https://ted.europa.eu/en/notice/-/detail/607581-2025 | Procurement record. Vendor not shown, likely AMAZEMET or Blue Power AUS. UNCONFIRMED. |
| **Gas atomizer, VIGA** (Blue Power), Hochschule Trier / Umwelt-Campus Birkenfeld: design, build, deliver, install, commission | EUR 533,605 (≈ $590k) | 2025, EUR | https://ted.europa.eu/en/notice/-/detail/572943-2025 (tender: .../472463-2025) | Procurement record (TED award, winner BluePower Casting Systems GmbH). Model not stated, probably AUG 1000 or 3000 class. |
| ALD **VIGA 35** (35 L furnace, dual-pour tundish, hot gas, gas recirculation), built 2022 | $3,500,000 "new price" | 2022 unit, 2024 auction, USD | https://industrialnewswire.com/press-release/tauber-arons-inc-and-aaron-industrial-solutions-announce-timed-online-auction-of-assets-of-a-premier-metal-3d-printing-company-and-powder-producer-in-northern-california-302031703/ ; https://3dprint.com/306429/is-uniformity-labs-out-of-business-metal-3d-printing-equipment-up-for-auction/ | Auctioneer's stated new cost (Uniformity Labs bankruptcy). Production scale, not lab. |
| R&D VIGA atomizer (4–12 L melt, about 30–90 kg steel), Swerim + Kanthal | SEK 20 M (≈ EUR 2 M) | 2021, SEK | https://www.swerim.se/nyheter/swerim-och-kanthal-investerar-i-en-ultramodern-atomiseringsenhet ; https://www.swerim.se/en/metal-powder-gas-atomization | News. The investment figure may include installation. |
| 250 kg batch VIGA (Atomising Systems + Consarc), Liberty Powder Metals, Teesside | About £10 M initial project, £9.83 M scheme cost, £4.6 M grant. Includes facility, not equipment only. | 2020–22, GBP | https://www.metal-am.com/liberty-powder-metals-secures-4-6-million-for-metal-powder-atomisation/ ; https://www.metal-am.com/atomising-systems-supplies-atomiser-to-liberty-powder-metals-in-partnership-with-consarc/ | News (project cost) |
| Chinese domestic lab VIGA (imports excluded), Xi'an Univ. of Technology | CNY 1.30 M budget cap (≈ $0.18M) | 2020, CNY | https://www.xaut.edu.cn/info/1240/11553.htm | Procurement (tender budget). Lower bound only, not a US price. |
| Chinese 250 kg vacuum atomizer, IMR CAS | CNY 3.7 M budget (≈ $0.52M) | 2024, CNY | http://www.imr.cas.cn/xwzx/tzgg/202404/t20240415_7102843.html | Procurement (tender budget, from search excerpt) |
| Lab-scale gas atomizer, NRC Canada (Mississauga), lowest-price RFP | Value not published | 2026, CAD | https://canadabuys.canada.ca/en/tender-opportunities/tender-notice/cb-921-51743946 | Tender only, no price |
| Arcast / PSI HERMIGA / Topcast / ALD VIGA-1B/2B / Retech | No published price found | — | — | Gap |
| **Aconity MIDI**, Universität Innsbruck (notice text names "Aconity MIDI") | EUR 456,074 | 2019, EUR | https://ted.europa.eu/en/notice/-/detail/159646-2019 | Procurement record (TED, direct award) |
| **AconityMIDI+**, Neue Materialien Bayreuth | EUR 350,000 | 2022, EUR | https://ted.europa.eu/en/notice/-/detail/174213-2022 | Procurement record (TED award; notice text names AconityMIDI+) |
| Aconity (Univ. of Turku; its equipment page lists an Aconity MIDI) | EUR 398,790 | 2021, EUR | https://ted.europa.eu/en/notice/-/detail/509009-2021 ; https://www.utu.fi/en/susfab/equipment/open_source_multi_material_metal_ceramic_3d_printer_aconity_midi | Procurement record. Model inferred. |
| Aconity multi-laser LPBF with in-situ monitoring (2 × 400 W + 1 kW MIDI+), Univ. of Nottingham | £893,150 excl. VAT (estimate had been £416,000) | 2021, GBP | https://www.find-tender.service.gov.uk/Notice/031918-2021 ; https://d3tenders.com/contract/ocds-h6vhtk-02bfc7.md ; https://www.nottingham.ac.uk/research/groups/cfam/research/processes/laser-powder-bed-fusion-lpbf.aspx | Procurement record (heavily configured research system) |
| Aconity LPBF (notice names Aconity MIDI), Forschungszentrum Jülich | EUR 675,390 | 2026, EUR | https://ted.europa.eu/en/notice/-/detail/689139-2026 | Procurement record (winner Aconity3D GmbH) |
| Other awards whose notice text mentions Aconity (winner and model not confirmed) | Sheffield £576,000 (2017); Bochum EUR 515,294 (2019); BTU Cottbus EUR 502,537 (2018); hereon EUR 758,700 (2022); Twente EUR 869,280 (2023) | 2017–23 | TED notices 384995-2017, 556977-2019, 252839-2018, 639368-2022, 44071-2023 (https://ted.europa.eu/en/notice/-/detail/<number>) | Procurement record. Vendor and model not confirmed. |
| AconityMINI (small LPBF), NASA | $196,350 | 2026, USD | https://www.usaspending.gov/award/CONT_AWD_80NSSC27P0033_8000_-NONE-_-NONE- | Procurement record |
| **EOS M 400-4**: "quad laser, accessories, installation, training and consumables, qty 1 lot" | $2,364,744 | 2023, USD | https://www.usaspending.gov/award/CONT_AWD_N6893623F0317_9700_GS03F080CA_4732 | Procurement record (US Navy NAWC, via Phillips Corp. on GSA) |
| EOS M 400-4, 52-week lease | $985,664 per year | 2025, USD | https://www.usaspending.gov/award/CONT_AWD_W519TC25PA096_9700_-NONE-_-NONE- | Procurement record (Army, Rock Island) |
| EOS M 400-4 (third-party estimates) | $1.5–2.5 M, "est. fully configured" | 2026, USD | https://machinetoolindex.com/machines/eos-m-400-4 | Aggregator/estimate |
| **MiR250** standard | $64,790 | 2026, USD | https://www.rg-group.com/store/product/100016-standard/mir250-autonomous-mobile-robot | List/retail (US distributor) |
| MiR250 | $59,440 | 2026, USD | https://shop.gibsonengineering.com/products/MiR250 (via https://robotpriceindex.com/robots/mir-250) | List/retail (page 403 to fetch, figure from index) |
| MiR250 Shelf Carrier ESD package, 2024 | EUR 42,500 excl. VAT | 2025, EUR | https://www.machineseeker.nz/mir-mir250+shelf+carrier+esd+und+zubeh%C3%B6r/i-21127667 | Used/ex-demo |
| **UR10e** arm (1300 mm reach) | $50,630 (2023), $47,085 (2022); pair of UR10e $84,744 (2019) | 2019–23, USD | https://www.usaspending.gov/award/CONT_AWD_80NSSC23PA487_8000_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_80NSSC22PC034_8000_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_80NSSC20P0030_8000_-NONE-_-NONE- | Procurement record (NASA) |
| **UR12e** | $44,636 (Vention list); EUR 42,525 incl. VAT (Funduino) | 2026, USD/EUR | https://vention.io/parts/universal-robots-ur12e-collaborative-robot-arm-3443 ; https://funduinoshop.com/en/robotics/universal-robots/ur12e/universal-robots-ur12e | List/retail (from search excerpts) |
| UR12e, DLA order | $89,690 (scope not stated; probably a kit with accessories) | 2026, USD | https://www.usaspending.gov/award/CONT_AWD_SPE8EL26F18QW_9700_SPE8EJ21D0020_9700 | Procurement record (scope unclear) |
| **Robotiq 2F-85** gripper | ~$5,000–6,000 (reseller; SVRC $5,825); RS Italy 2F-85 kit with Wrist Connect EUR 4,906 excl. VAT | 2026, USD/EUR | https://www.roboticscenter.ai/blog/robotiq-gripper-guide ; https://it.rs-online.com/web/p/pinze-robotiche/0136163 | List/retail (from search excerpts) |
| **Wire EDM**: Sodick ALN600G | $271,315 (Navy 2026); $301,673 (USAF 2025) | 2025–26, USD | https://www.usaspending.gov/award/CONT_AWD_N0016726F1083_9700_N0016725A1003_9700 ; https://www.usaspending.gov/award/CONT_AWD_FA860125P0073_9700_-NONE-_-NONE- | Procurement record |
| Wire EDM: FANUC Robocut C600iC-ADV | $220,362 | 2026, USD | https://www.usaspending.gov/award/CONT_AWD_80NSSC27P0128_8000_-NONE-_-NONE- | Procurement record (NASA) |
| Wire EDM: Mitsubishi MV2400R / GF CUT P 550 / Makino UX6 | $221,600 (2020) / $222,085 (2021) / $201,524 (2026) | 2020–26, USD | https://www.usaspending.gov/award/CONT_AWD_SPE8E320F8977_9700_SPE8E315D0033_9700 ; https://www.usaspending.gov/award/CONT_AWD_80NSSC21P2777_8000_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_SPE8E326FB6HY_9700_SPE8E325D0022_9700 | Procurement record |
| **Instron 68FM-100** (100 kN floor frame) | $145,607 (USAF 2022, standard height, short base); $161,830 (NASA 2023); $207,865 (Navy 2024, "system") | 2022–24, USD | https://www.usaspending.gov/award/CONT_AWD_FA812623P0016_9700_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_80NSSC23PA554_8000_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_N6893624F0191_9700_N6893620D0015_9700 | Procurement record |
| (Instron 68FM-300, for reference) | $247,279–322,760 | 2026, USD | https://www.usaspending.gov/award/CONT_AWD_N0016426PG025_9700_-NONE-_-NONE- | Procurement record |
| **HIP**, American Isostatic Presses (lab/small) | $154,500 (NPS 2019); $340,000 (NASA MSFC 2018, 3 bids); $875,000 (Naval Research Lab 2024) | 2018–24, USD | https://www.usaspending.gov/award/CONT_AWD_N6227119P5013_9700_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_80MSFC18P0063_8000_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_N0017324P2030_9700_-NONE-_-NONE- | Procurement record (models not stated) |
| HIP (AIP) at UK universities | £155,000 (Huddersfield 2021); £210,000 (Swansea 2016); £225,000 (Manchester 2020); £333,000 (Sheffield 2017) | 2016–21, GBP | TED 358106-2021, 415056-2016, 124928-2020, 382548-2017 | Procurement record (notice text names AIP) |
| HIP awards where the notice names Quintus Technologies (model not stated) | EUR 678,000 (Politecnico di Torino 2019); EUR 1,495,623 (BTU Cottbus 2020); EUR 1.70 M (CV Řež 2023); EUR 5,086,655 (BTU Cottbus 2022, large) | 2019–23, EUR | TED 164727-2019, 135624-2020, 781736-2023, 568881-2022 | Procurement record. QIH 15L price itself UNCONFIRMED. |
| Quintus HIP, 300 mm × 850 mm hot zone (CSIR tender docs: QIH 32-2070-1400 MURC) | About R50 M (≈ $2.8–3.0 M) funding, plus building R10.85 M | 2022, ZAR | https://castingssa.com/?p=7626 ; https://www.csir.co.za/sites/default/files/Documents/Appendix%204%20-%20Scope%20of%20Supply%20-%20QIH%2032-2070-1400%20MURC%2C%20Ref%2061064%2C%20Rev%200.pdf | News/funding figure |
| **Benchtop SEM, Hitachi TM4000PlusII** | $98,900 with accessories, set-up, training, freight (USDA-ARS 2021); $199,548 (DLA 2022, probably with EDS) | 2021–22, USD | https://www.usaspending.gov/award/CONT_AWD_12905B21P0255_12H2_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_SPE8EL22F15QD_9700_SPE8EJ21D0020_9700 | Procurement record |
| (Tabletop SEM, other brand) | $125,280 | 2022, USD | https://www.usaspending.gov/award/CONT_AWD_N0016722P0111_9700_-NONE-_-NONE- | Procurement record |
| **Benchtop XRD, Rigaku MiniFlex 6G** | $99,465 (NASA 2023); $99,444 (USDA-ARS 2024); $107,591 (NASA 2021); $119,968 (EPA 2020) | 2020–24, USD | https://www.usaspending.gov/award/CONT_AWD_80NSSC23PB731_8000_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_12405B24P0336_12H2_-NONE-_-NONE- | Procurement record |
| **Construction: Virginia state cost database** (actual comps, Richmond, rates as of 1/1/2026, incl. utilities and site work) | New dry lab, physics/engineering: $484 / $501 / $503 per sf (L/M/H). New wet lab H: $769/sf. Research labs (BSL-3 class): $1,362/sf. Maintenance buildings: $362/sf. Lab equipment: $53/sf. | 2026, USD | https://dgs.virginia.gov/site-assets/deb/Miscellaneous/R_2%20PUBLISHED%20Virginia%20Building%20Construction%20Cost%20Database%20-%202026.pdf | Public cost database |
| Construction: Texas THECB standard, new "Laboratory, General" (FY2019–25, inflation- and location-adjusted) | $854/GSF (average + 1 SD) | 2025, USD | https://reportcenter.highered.texas.gov/reports/data/average-construction-costs-fy-2019-2025/ | Public cost standard |
| Construction: lab benchmarks | CBRE: $675–1,200/sf ground-up lab in Boston, SF and San Diego. JLL: $350–1,325/sf by region. | 2024, USD | https://www.cbre.com/insights/reports/life-sciences-construction-benchmarks-and-trends-2024 ; https://www.us.jll.com/en/views/lab-construction-costs-and-the-unique-variables-at-play | Consultant benchmark (from search excerpts) |
| Construction: industrial shell | RLB Q3 2026 industrial warehouse hard cost $75–370/sf (18 US cities). RSMeans 1-story factory $116–129/sf (2019 data, outdated). | 2026 / 2019, USD | https://reliamag.com/topics/guides/cost-to-build-a-factory-us ; https://www.rsmeans.com/model-pages/factory-1-story | Consultant benchmark (secondary) |
| Real project: **ASU ISTB12** (robotics/manufacturing, high-bay collaborative space), Mesa AZ | $185 M building (≈ $250 M with equipment) for 173,000 GSF, about $1,070/GSF | opened 10/2025, USD | https://news.asu.edu/20231205-arizona-impact-istb12-be-major-economic-boost-mesa-region ; https://news.asu.edu/20251024-science-and-technology-istb-12-one-stop-shop-robotics-manufacturing | Project actual (news) |
| Real project: **UMaine GEM / Factory of the Future** (two large manufacturing bays) | $82 M for 50,000 GSF, about $1,640/GSF (total project cost) | completion 2026, USD | https://umaine.edu/capital-projects/?p=392 ; https://mainebiz.biz/article/umaine-breaks-ground-on-82m-factory-of-the-future/ | Project budget (news) |
| Real project: **Purdue HARF** (hypersonic tunnel high-bay building) | $41 M for 65,000 sf, about $630/sf | opened 2023, USD | https://www.purdue.edu/newsroom/2023/Q2/purdue-applied-research-institute-opens-41m-hypersonics-and-applied-research-facility/ | Project actual (news) |
| Real project: **LSU Construction & Advanced Manufacturing Bldg** (high-bay strong-floor lab) | $107 M for about 147,000 sf, about $730/sf | groundbreaking 2027, USD | https://www.wafb.com/2024/10/18/lsu-announces-new-construction-advanced-manufacturing-building-elevate-states-economy/ ; https://lsu.edu/fs/project-updates/construction-management-advanced-manufacturing.php | Project budget (news) |
| Real project: **ORNL Translational Research Capability** (heavy-equipment and inert-environment labs) | $95 M TPC for about 100,000 sf, about $950/sf | 2019 start, USD | https://ornl.gov/news/new-research-facility-will-serve-ornls-growing-mission-computing-materials-rd | Project estimate (DOE) |
| **Bulk LN2/LAr: tanks and installation** | Bulk LN2 tank replacement $247,962 (Navy 2024, 3 bids). 1,500-gal LN2 tank $78,770 (Navy 2024). Argon tank, gas drops and installation $126,577 (Army 2019). New argon tank or cross-connect (construction) $210,750 (CDC 2019). | 2019–24, USD | https://www.usaspending.gov/award/CONT_AWD_N0025324P0034_9700_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_N0017424P0225_9700_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_W911QX19P0065_9700_-NONE-_-NONE- ; https://www.usaspending.gov/award/CONT_AWD_75D30119C06578_7523_-NONE-_-NONE- | Procurement record |
| Bulk argon, supplier-leased model | Microbulk Ar $3.79/CCF; 1,500 L tank rental $300/month (EPA 2019) | 2019, USD | https://www.usaspending.gov/award/CONT_AWD_68HE0419P0021_6800_-NONE-_-NONE- | Procurement record |
| Used 6,000-gal vacuum-jacketed cryogenic tank (Cosmodyne, 50 psig, skid) | $35,500 | ~2026, USD | https://surplusrecord.com/listing/6000-gal-cosmodyne-horizontal-vacuum-jacketed-cryogenic-tank-50-psig-skid-mounted-1186863/ | Used listing (search excerpt). A new 6,000–11,000 gal tank price was not found (UNCONFIRMED). |

### Suggested planning unit costs (my synthesis, not quotes; 2026 USD, delivered and installed)

| Item | Planning value | Basis |
|---|---|---|
| Kardex Shuttle XP 500, ~10.7 m (35 ft), 2450 × 864 mm trays | **$250k** (range $210–300k) | Kardex $6–8k/ft × 35 ft. Matches federal $103–108k for 4.9–5.9 m units in 2018–19 and the $213k retail price for a 6.75 m XLD. |
| AMAZEMET rePowder | **$400k** ($290–460k) | NASA $287k, NIST $322k, Aalen EUR 408k |
| Lab/pilot VIGA gas atomizer, 5–25 kg (HERMIGA 100/10 or AUG 3000 class) | **$1.0–1.5M** (small AUG-class from ~$0.6M) | Trier/Blue Power EUR 534k (small); Swerim about EUR 2M (4–12 L); VIGA 35 $3.5M (production). The pilot-class figure is an estimate. |
| AconityMIDI / MIDI+ | **$600–800k** | EUR 350–456k for base MIDI/MIDI+ (2019–22); EUR 675k (2026); £893k for a heavily optioned unit |
| EOS M 400-4 | **$2.2–2.5M** | Navy $2.36M including installation, training and consumables |
| MiR250 + UR12e + 2F-85 mobile manipulator (hardware only) | **~$120k** + integration (often 1.5–2× hardware) | $60–65k + $45–50k + $5–6k |
| Wire EDM | **$275k** | $200–302k awards, 2020–26 |
| Instron 68FM-100 with grips/extensometer | **$200k** | $146–208k |
| HIP: lab (AIP-class) / QIH 15L-class / QIH 32–48 class | **$0.4M / $1.2M / $3M** | Awards above. The QIH 15L-class value is UNCONFIRMED. |
| Benchtop SEM with EDS / MiniFlex XRD | **$150k / $110k** | Awards above |
| High-bay advanced-manufacturing R&D building (total project) | **$700–1,100/sf** | Projects at $630–1,640/sf; VA/TX public lab standards $500–850/sf; industrial shell $75–370/sf |
| Bulk Ar or N2 station (pad, piping, vaporizer, tank lease set-up) | **$150–250k each**, plus site distribution piping | Federal tank and installation awards above |

---

## Part B: geometry of a representative close-coupled VIGA gas atomizer

**Recommended model: PSI HERMIGA 100/10 VI** (Phoenix Scientific Industries, UK). It is the only lab/pilot close-coupled VIGA found with a full published data sheet and a dimensioned plan and elevation drawing. Its siblings (HERMIGA 100/25 V2I, 120/25 CC) share the same 6.0 × 5.1 × 5.7 m envelope.

- Data sheet: https://www.psiltd.co.uk/wp-content/uploads/2024/07/C1-HERMIGA-100-10-VI-Rev-2.pdf
- The same dimensioned drawing (plan 5950 × 5050, front elevation 5950 wide × 5700 high) appears in https://www.psiltd.co.uk/wp-content/uploads/2024/07/D2-HERMIGA-120-50-V3I-Rev-3.pdf
- Range page: https://www.psiltd.co.uk/technology/hermiga-vacuum-inert-gas-atomisation-systems/the-hermiga-pilot/

### HERMIGA 100/10 VI: published data

| Parameter | Value |
|---|---|
| System size (L × D × H) | **6.0 m × 5.1 m × 5.7 m** (drawing: 5,950 × 5,050 × 5,700 mm) |
| Weight | 5 t |
| Crucible | Induction-heated, **1.5 L (about 10 kg steel)** |
| Atomizing die | Supersonic close-coupled ("invariable" die) |
| Atomization rate | 2–4 kg/min steel, so a 10 kg melt pours in about 3–5 min |
| Powder d50 | 10–100 µm |
| Melt chamber | Side-opening, water-cooled, 304L stainless steel |
| Atomization chamber | Water-cooled, 304L stainless steel |
| Powder handling | High-efficiency cyclone, partial and HEPA filters |
| Power | 100 kVA, 3-phase |
| Cooling water | About 70 L/min at 5 bar |
| Gas | Ar, N2 or He. Up to 6 kg/min. **Minimum supply pressure 20 bar.** |
| Options | O2 monitoring, pyrometry, booster pump, melt charging and sampling, gas superheat, extra transfer hoppers |
| Output per run | The 100-series is marketed as **10–25 kg of powder per run** (100/25 version: 4 L, 25 kg). The usable LPBF cut is a fraction of that; size distribution data were not found (UNCONFIRMED). |

### Dimensions scaled from the dimensioned drawing (±10%, my measurement)

Scale: 5,700 mm = 579 px, about 9.85 mm/px.

| Feature | Approximate value |
|---|---|
| Upper (melt) deck height | ≈ **3.5–3.6 m** |
| Intermediate deck | ≈ 2.2 m |
| Low walkway / stair landing | ≈ 1.05–1.1 m |
| Melt chamber | Horizontal-axis cylinder with dished ends, about **1.3–1.4 m** across and about 1.3 m tall, top at about 5.3–5.4 m. A side door swings on a 680 mm radius (shown on the plan). Small fittings and valves reach the 5.7 m overall height. |
| Atomization chamber ("tower") | Vertical water-jacketed cylinder about **1.1 m OD**. The cylindrical section runs about 1.75 m, from about 4.0 m down to about 2.3 m, with a conical bottom of about 0.8–0.9 m below it. The axis is directly under the melt chamber. |
| Cyclone and collection | Two cones hang below the 2.2 m deck: one under the atomization chamber, one under the cyclone. Each discharges through a valve into a **powder can** (roughly 0.4–0.5 m diameter, about 0.5 m tall) sitting just above the floor. A vertical filter or exhaust module stands at the right. A boxed filter (about 0.8 m) is at about 2.3–3.3 m on the right. |
| Control console/cabinet | About **1.45 m wide × 1.3 m tall**, standing on the upper deck to the right of the melt chamber (top at about 4.9 m) |
| Induction power/heat station | About 0.5 m × 1.0 m box beside the melt chamber on the upper deck (left) |
| Stairs | From the floor to the low walkway and up to the upper deck |
| Plan | Steel deck grid of about 5.95 × 5.05 m. Melt chamber near the centre. Two 1,200 × 500 mm units on the rear edge, probably the transfer hoppers listed as an option (UNCONFIRMED). One more 1,200 mm unit at the rear right. |

**Photo description** (data-sheet photo): a two-level steel structure with handrails. The melt chamber sits on the top deck, and the atomization column passes down through the deck. The cone, cyclone and powder cans are at ground level. Stairs run up the front right.

### Comparison candidates

| Model | Capacity | Size (L × D × H) | Notes | Source |
|---|---|---|---|---|
| **PSI HERMIGA 75/5 VI** (compact R&D) | 0.7 L (about 5 kg steel); the 75/3 is 0.4 L (about 3 kg) | **3.2 × 2.1 × 2.4 m**, 4 t | Top-opening melt chamber on a single low platform (about 1.3–1.5 m, from the photo). Atomization cylinder and cone below, discharging into a powder can on a castor trolley. Small side cyclone. Control panel on the frame. Separate induction power cabinet on the floor. 200 kVA. Gas max 6 kg/min. PSI says the Mini was designed to fit a 4 m floor-to-floor height. | https://www.psiltd.co.uk/wp-content/uploads/2024/07/B4-HERMIGA-75-5-Rev-1.pdf ; https://www.psiltd.co.uk/solutions/vacuum-inert-gas-atomisation-systems/atomiser-development/ |
| PSI HERMIGA 120/50 V3I (production reference) | 50 kg steel, tilt-pour furnace plus heated tundish, 3–6 kg/min | **10.0 × 6.5 × 7.5 m**, about 25 t | Dual-section water-cooled chamber. Gas supply at 30 bar minimum. | https://www.psiltd.co.uk/wp-content/uploads/2024/07/D2-HERMIGA-120-50-V3I-Rev-3.pdf |
| **Blue Power AUG 3000** | 3.4–3.9 L crucible, 22 kg steel (HTC version) or bronze, up to 2,000–2,100 °C, 3–4 h cycle, 30 kW generator. The AUG 1000 is 1.5–1.7 L, 8 kg steel, 1.5–2 h, 20 kW. | **Not published** (UNCONFIRMED) | Close-coupled or free-fall nozzles. Melt chamber and nozzle plate lift and swing aside. Water-cooled spray tower and cyclone. Gas preheat up to 450 °C. Differential-pressure control. | https://bluepower-casting.com/en/AUG-3000/AUG3000 ; https://images.nuernbergmesse.de/files/2e3b6b49-8ba5-8ede-3e2a-82bec7773122.pdf |
| **ALD VIGA-2B** (LU Hannover, combined with EIGA 70-500) | 2 L crucible, 1,700 °C, 40 kW VIM, 60–90 min cycle | Not published | Ar from a 20–32 bar high-pressure tank with gas preheating. VIGA gas flow 15–25 m³/min. | https://www.iw.uni-hannover.de/en/facilities/inert-gas-powder-atomization-unit-eiga-viga |
| ALD VIGA-1B (TU Freiberg) | 1 L crucible, 5.5–7.0 kg charge, 800–1,650 °C | Not published | Atomizing gas up to 26 bar, preheat to 100 °C. Chamber 0.05 mbar to 1 bar. | https://tu-freiberg.de/en/fakult5/iest/iest-equipment/metallurgy/inert-gas-atomisation-vigaeiga |
| DTU refurbished lab VIGA | 1.5 L graphite crucible, up to 10 kg ferrous, about 90 min per 316L run | Not published | Induction furnace at the top. Close-coupled die. Cyclone between the atomization chamber and a sealed powder container (opened in a glovebox). N2 at up to 2.5 bar absolute. | https://backend.orbit.dtu.dk/ws/portalfiles/portal/288451513/del_Rio_2022_IOP_Conf._Ser._Mater._Sci._Eng._1249_012034.pdf |
| Arcast ATM GP 10 / GP 100 | 5–10 kg / 50–100 kg, ceramic crucible, close-coupled | Not published | Arc 200/500: 50–1,000 g, cold crucible | https://www.arcastinc.com/Arcast%20Atomizers.pdf |
| Generic Chinese VIGA (Hunan APD, 5–1,000 kg) | — | Atomization tank **≥ 1.2 m diameter, inner height > 2.5 m** | 2–6 MPa gas, 900–1,500 m³/h | https://www.hnapd.com/product/details_505.html |

### Notes for the 3-D model

- **Building height.** A HERMIGA 100-class unit needs about 6 m of clear height. Plan about 7 m, which leaves room to lift the melt-chamber lid and for a crane hook. A 50 kg production unit needs about 7.5 m plus clearance.
- **Gas.** Plan a high-pressure gas supply of at least 20–30 bar, using cylinder bundles or a bulk liquid tank with a high-pressure pump and vaporizer. Peak draw is about 6 kg/min Ar (about 3.4 Nm³/min). ALD's VIGA-2B is quoted at 15–25 m³/min.
- **Water.** Plan for about 70 L/min.
- **Power.** Plan for 100–200 kVA per unit.

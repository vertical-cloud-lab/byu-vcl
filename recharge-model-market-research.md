# Market research for the VCL recharge center: AMAZEMET rePowder comparables, vendor outreach list, and the first BYU approval document

> **Status: exploratory research, not policy, not a price list.** Compiled 6 October 2026 in
> response to [PR #107](https://github.com/vertical-cloud-lab/byu-vcl/pull/107) (the atomizer
> is now installed; MS&T26 is under way in Pittsburgh). Every figure below is quoted from a
> public page fetched on that date and linked in §10. Prices and rates change; re-verify
> before quoting anyone.

## 0. How this was gathered (and what could not be)

- Web discovery ran on the GitHub Actions runner. Page fetches that the runner's datacenter
  IP could not make (BYU Financial Services, Mining Weekly, several trade sites) were made
  from the CubXL Raspberry Pi over Tailscale SSH with rate-capped `curl`, read-only, and
  parsed back on the runner.
- Two sites could not be read from **either** machine: `matscitech.org` (the MS&T26
  exhibitor list) and `engineering.jhu.edu` (JHU's facility pages) both serve a Cloudflare
  JavaScript challenge ("Just a moment…") to any non-browser client, regardless of IP. The
  JHU fee table below comes from a Wayback Machine snapshot dated 13 January 2026; the
  MS&T26 expo list comes from the co-located Advanced Materials Show USA, which shares Hall A
  and the same two exhibit days.
- The MS&T26 final program PDF (14k lines) contains no exhibitor list, only session rooms.
- **Not found:** the UK web page with published AMAZEMET rates that was remembered on the
  PR. Searches across `royce.ac.uk` and all `ac.uk` domains surface only the Royce/Sheffield
  Arcast gas atomiser (no rate card) and Royce's subsidised Equipment Access Schemes. If
  the page exists, it is not indexed under "rePOWDER", "AMAZEMET" or "ultrasonic atomiser".

## 1. The first official BYU document, and who receives it

The first formal document is a **proposal to establish a recharge center**, and it goes to
the **Department Chair**. From the *Recharge Center Policy & Procedures* (June 2005), §2
"Establishing a Recharge Center", p. 1, verbatim:

> "The prospective Recharge Center must submit a proposal to establish a recharge center
> to the Chair of the cognizant Department for approval. The Chair will forward the
> approved Recharge Center proposal to the Dean's Office for its approval. The Dean's
> Office will forward the proposal to the Director of Regulatory Accounting, currently
> (June 2005) John N. Gardner, who will establish the appropriate account and budget
> number(s) for the Recharge Center."

Three details that matter for the send-out:

1. **It travels with a rate proposal.** Rate proposals are due "when they are initially
   established" (p. 2), and "The Chair or Dean is responsible to review and approve
   recharge center rates prior to submission to Regulatory Accounting" (p. 2). So the
   packet the Chair signs is the establishment proposal **plus** the initial rate proposal
   (and, to include depreciation in rates, the equipment/depreciation schedule request,
   since "An equipment reserve account is required to include equipment depreciation in
   recharge rates", p. 2).
2. **The VP's office is in the loop.** The responsibilities table (p. 9) says center
   management must "Request the establishment of a recharge center or cost center from the
   Chair, Dean's and VP's office." The narrative on p. 1 names only Chair → Dean →
   Regulatory Accounting; the VP step is the one the SEM-lab conversation (issue #106)
   pointed at with Larry Howell. Treat it as a real signature line.
3. **The current Director of Regulatory Accounting is not the 2005 name.** BYU Financial
   Services' Accounting page (read live today) lists **Rebecca Harrison, Director,
   Regulatory Accounting and Reporting, 107 ECCB, rebecca_harrison@byu.edu, 801-422-6639.**
   Regulatory Accounting is the office that "Approve[s] the establishment of recharge
   centers" and "Review[s] and approve[s] rates" (p. 9).

The policy prescribes no form: a memo-style proposal is what the text describes. The draft
in this repo, [`drafts/recharge-center-establishment-proposal.md`](drafts/recharge-center-establishment-proposal.md),
is written to that routing, with the rate proposal and the equipment/depreciation package
as its attachments. One practical step before the Chair signs: a two-line email to
Regulatory Accounting asking whether a current template or checklist has replaced the 2005
memo format (question 1 in the kickoff agenda). That email is informal; the Chair's packet
is the official start.

## 2. The AMAZEMET rePowder, induction module specifically

**What the induction module is.** Facility pages at JHU and Georgia Tech describe it the
same way: an induction heating module with a **graphite crucible** that melts alloys up to
**1300 °C**, with interchangeable **225 ml and 400 ml** crucibles (JHU). The vendor page
says induction is "usually used to process alloys with melting points up to 1300 °C" and
shows silver, bronze and aluminum as demonstrated materials; the arc/plasma module covers
the 1300–3500 °C range and the laser source is "in development". Ultrasonic frequency sets
the size: 20 kHz gives d50 80–100 µm, 40 kHz 45–60 µm, 60 kHz 35–45 µm; argon use is
"~10 L/min"; batch range "from a few grams to several kg per day". AMAZEMET reports "over
80 devices sold worldwide" in 18 countries, "28 available modules and options", and 12
distributors.

**Posted purchase prices: none.** AMAZEMET and its distributors publish no list price. The
one hard public number is a US federal purchase order:

| Evidence | Configuration | Price | Date |
| --- | --- | --- | --- |
| NASA Marshall Space Flight Center sole-source PO 80MSFC24PA004 to A3DM Technologies LLC (AMAZEMET's US distributor) | Basic rePowder **with Focused Plasma Melting System** (plasma module, not induction), multifrequency generator 17–70 kHz, sonotrode starter pack, exhaust-gas recirculation, vacuum feedthrough, ultrasonic suction casting, 40 kHz system, hygrometer, O₂ sensor upgrade, maintenance kit and workbench, delivery, commissioning, one year of maintenance | **$286,720** | 21 Nov 2023 |

That is a plasma-configured system with most options. An induction-module system is
generally the lower-temperature, lower-cost melting path, so the $250k planning figure used
throughout the dossier is consistent with the only public comparable. The Mintek (South
Africa), Chemnitz and TUM write-ups give no purchase figures.

**AMAZEMET's own atomization service (a price floor for "custom powder development").**
The service accepts **50 g** minimum feedstock, quotes "a budget starting point of
€1,000", includes in-house arc-melting and homogenization of custom compositions, shares
full process parameters, and processes multiple materials in one order at no extra charge.
Contact sales@amazemet.com, +48 573 481 303. This is the closest thing to a published
market price for what the VCL would sell: roughly **€1,000 for a tens-of-grams research
batch**, before shipping and before any alloy-development labor.

**The induction-based competitor.** Blue Power / Indutherm's **AUS 500** is an
induction-melting ultrasonic atomizer developed "in cooperation with Amazemet": crucible
sizes 0.25–0.7 L, batches "around 100 g or less" up to "several kg (bronze) per hour".
No public price either.

## 3. Published facility rates on the same instrument

Three US university facilities run a rePowder and publish rates. Normalized to the six-hour
run the PI described, they bracket the dossier's draft numbers rather than contradicting
them.

| Facility (configuration) | Published rate | Six-hour run equivalent | Source date |
| --- | --- | --- | --- |
| **Northwestern, CHiMaD Metals Processing Facility (CMPF)** — plasma torch, 40 kHz, ~200 g input rod, "~100 g powder a day" | **Per run:** $1,075 NU / $1,720 external academic / $2,150 commercial; powder not included; arc melter $100/$100/$200 | $1,075 / $1,720 / $2,150 | live, 6 Oct 2026 |
| **Johns Hopkins, Materials Characterization & Processing (MCP)** — induction module (graphite crucible ≤1300 °C, 225/400 ml) **and** arc/plasma module, 40 + 60 kHz, gas recirculation | **Per hour, independent (self-operated):** $25 internal academic / $25 external academic / $41 external non-academic / $30 startup. **Assisted:** $93 / $93 / $152.52 / $111.60 | independent: $150 / $150 / $246; assisted: $558 / $558 / $915 | Wayback snapshot, 13 Jan 2026 |
| **Georgia Tech, Advanced Manufacturing Pilot Facility (AMPF)** — induction (≤1300 °C) and arc/plasma | **Per hour, "Advanced Manufacturing" tier:** $80 internal / $275 external | $480 / $1,650 | live, 6 Oct 2026 |
| Dossier draft (5-yr depreciation, 2.0 FTE basis) | Per run: $918 internal / $1,391 federal external / $1,650 non-federal | same | — |

Reading the table:

- The two hourly facilities price the **machine** and leave operator labor as a separate,
  optional "assisted" line (JHU) or as the user's own trained time (both). A remote-access
  cloud lab cannot offer self-operation, so the comparable rows are JHU **assisted**
  ($558–$915 per six-hour run) and Georgia Tech external ($1,650), not the $150 independent
  rows.
- Northwestern's per-run model is the only one that bundles labor and consumables the way
  the dossier does, and its internal rate ($1,075) sits above the draft's $918. The draft's
  non-federal rate ($1,650) equals Georgia Tech's external rate exactly and sits just under
  Northwestern's external-academic rate ($1,720).
- JHU and Northwestern both run two tiers for externals (academic vs. non-academic or
  commercial) with a ~1.6× spread (JHU) to 2× (Northwestern) over internal. BYU's policy
  produces the same shape from a different rule (cost + overhead for federal externals,
  plus a discretionary surcharge for non-federal ones).
- None of the three posts a separate induction-module rate; JHU and Georgia Tech charge
  one instrument rate regardless of melting module.

Other facilities checked: Ames National Laboratory's Powder Synthesis & Development
Capability (close-coupled gas atomization, 2–5 kg experimental and 10–25 kg pilot) posts no
rates and works through DOE Strategic Partnership Project cost estimates, restricted to
powders "which cannot be obtained in the specified quality or quantity from commercial
suppliers" (PSD@ameslab.gov). Royce/University of Sheffield (Arcast EIGA, Tekna
spheroidiser) posts no rate card; access via royce@sheffield.ac.uk with subsidised access
schemes. Colorado School of Mines and UMass IALS publish core rates but list no atomizer.

## 4. Belmont Metals

"Belmont materials" is **Belmont Metals, Inc.**, Brooklyn, NY (330 Belmont Avenue, 11207),
a non-ferrous alloy maker since 1896. What its site says that is relevant to a quote:

- It offers a **Research Atomizer** and "work with a metallurgy team to create the perfect
  alloy in small-batch form" for 3D-printing powder development; the full chain is material
  selection, melting/mixing, atomization, and sizing/sieving.
- **Minimum sample sizes:** aluminum-based alloys **4 lb**; bismuth-, copper-, lead-, tin-
  and zinc-based alloys **5 lb**. Alloy systems named in its powder article: zinc, nickel,
  aluminum. Pricing is described only as "Low Flat Rate Pricing".
- **Quote route:** phone 1 (833) 4-ALLOYS or +1 718 342-4900, or the contact form at
  belmontmetals.com/contact-us. No pricing, lead time, or powder-size data is published.

Belmont is a **feedstock and master-alloy** house as much as a powder producer: its own
article argues that powder quality "starts with the feedstock". That makes it a candidate
for two different quotes: custom alloy *powder* (their atomizer), and custom alloy
*ingot/shot feedstock* for the VCL's induction crucible.

## 5. MS&T26 and the Advanced Materials Show USA: who to talk to on the floor

MS&T26 runs 4–7 October 2026 at the David L. Lawrence Convention Center; the exhibition is
in **Hall A on 6–7 October**, co-located with The Advanced Materials Show USA ("120+
exhibitors" per the MS&T brochure). The public exhibitor list is the Advanced Materials
Show's (about 100 names with booths). AMAZEMET is **not** on it (its listed shows are TMS
2026 in March and Formnext in November). Booths worth a visit for custom-powder quotes and
for the recharge center's supply chain:

| Booth | Exhibitor | Why |
| --- | --- | --- |
| **725** | **Goodfellow Corporation** | Sells **custom metal alloy powders made "using patented ultrasonic technology"** in batches "as small as 100 g", including high-entropy and custom compositions; stock powders ship in 48 h. The most direct like-for-like competitor/collaborator on the floor. Ask who atomizes for them and what a 100–500 g custom aluminum alloy costs. +1-800-821-2870. |
| **818** | **Kennametal, Inc.** | Pittsburgh-headquartered; gas-atomized Co/Ni/Fe AM powders (Stellite 21 AM), R&D pilot centre in Latrobe. Ask about development lots and whether they take outside alloy requests. |
| **911** | **Stanford Advanced Materials** | Specialty powder and custom-alloy supplier (trading house); useful for a benchmark quote on small custom lots. |
| **622** | **Metalor Technologies USA** | Precious-metal powders and flakes; relevant only if Au/Ag/Pt alloys enter the service menu. |
| **616** | **Powder Processing and Technology** | Toll powder-processing house (milling, classification, thermal processing). Not an atomizer, but a candidate for downstream sieving/classification if the VCL does not want to do it. Verify scope at the booth. |
| **1029** | **Powdertech International** | Specialty magnetic powders; a possible customer-side contact for soft-magnetic alloy powders, not a supplier. |
| **923 / 722** | **Thermo-Calc Software / Sente Software (JMatPro)** | Alloy-design tools the custom-alloy service would use to pre-screen compositions before an atomization run. |
| 719 / 917 / 733 / 825 / 1013 / 1017 | Malvern Panalytical / Anton Paar / HORIBA / Microtrac–Retsch (Verder) / Fritsch / LECO | Particle-size, flow, density and O/N/H analysis: the QA instruments a powder recharge center will need to quote and later buy from the equipment reserve. |
| 830 / 625 / 1023 / 836 / 933 / 937 | Zircar Zirconia / Centorr Vacuum / Materials Research Furnaces / Oxy-Gon / Thermcraft / Nabertherm | Crucibles, inert-atmosphere furnaces, heat-treatment: consumables and the next equipment on the reserve list. |
| 909 / 718 | Element Materials Technology / Westmoreland Mechanical Testing | Accredited external test labs for powder/part certification if customers ask for it. |
| 1036 / 1037 / 1011 / 1133 / 736 | Texas A&M MSE / Case Western / Alfred / FAMU-FSU / Clarkson CAMP | Academic booths: potential external-academic users and peer facilities to ask about their own rate structures. |

Two Pittsburgh-area powder makers are **not** on the list but are a short drive from the
venue and fit the outreach list (§6): ATI Powder Metals (Oakdale) and 6K Additive
(Burgettstown).

## 6. Outreach list: industry (custom / small-batch powder development)

Ordered roughly by fit for research-quantity custom alloys. Minimums and contacts are as
published on each company's site; "Al?" flags whether aluminum alloys are explicitly
offered.

| Company | Location | Method / scale | Published minimum | Al? | Contact |
| --- | --- | --- | --- | --- | --- |
| **AMAZEMET** (atomization service) | Majdan / Warsaw, Poland | Ultrasonic (rePowder), arc-melt pre-alloying | **50 g**; "budget starting point €1,000" | yes (induction) | sales@amazemet.com, +48 573 481 303 |
| **Goodfellow** | Pittsburgh, PA (US HQ, 301 Grant St) / UK | Ultrasonic ("patented ultrasonic technology") | **100 g** | yes | +1-800-821-2870; booth 725 at MS&T26 |
| **Belmont Metals** | Brooklyn, NY | Research Atomizer + metallurgy team | **4 lb** Al-based, 5 lb others; "low flat rate" | yes | 1 (833) 4-ALLOYS; belmontmetals.com/contact-us |
| **Rosswag Engineering** | Pfinztal (Karlsruhe), Germany | BluePower gas atomizer + in-house LPBF qualification | **5–50 kg**, "within 2 weeks" | yes (portfolio) | rosswag-engineering.de |
| **Ultra Fine Specialty Products** | Woonsocket, RI | Pilot gas atomizer (Ar/N₂) | small batches "up to 500 lbs" | steels, Ni, Co, Cu, magnetic (Al not listed) | (401) 488-4990; ultrafinepowder.com |
| **Arcast Inc. / Arcast Materials** | Oxford, Maine | Atomizer maker; contract powder production for "challenging" and reactive alloys (VersaMelt ≈3 kg/cycle) | per quote | reactive/Ti focus | arcastinc.com, arcastmaterials.com |
| **Atomising Systems Ltd** | Sheffield, UK | Operates gas, water **and ultrasonic** atomisers for niche markets | per quote | per quote | atomising.co.uk / metal-powder.co.uk |
| **Valimet** | Stockton, CA | Toll atomization of aluminum alloys, ≤2500 °F melts, 2–200 µm | **100 lb** to 100 t | **yes, Al specialist** | sales@valimet.com, +1 209 444 1600 |
| **Equispheres** | Ottawa, Canada | Proprietary atomization; Al 2xxx–7xxx + custom alloys | per quote | **yes** | equispheres.com |
| **Elementum 3D** | Erie, CO | Custom Al/Cu/Ni/steel alloy development (RAM), application development | per quote | **yes** | elementum3d.com |
| **6K Additive** | Burgettstown, PA (near Pittsburgh) | UniMelt microwave plasma; custom-engineered alloys incl. HEAs, Ti, refractory | per quote | not listed | sales@6kadditive.com, (724) 215-7049 |
| **ATI Powder Metals** | Oakdale, PA (near Pittsburgh) | Gas atomization; Ni superalloy, Ti, specialty steel | production scale | no | (412) 923-2670 |
| **Kennametal Additive** | Pittsburgh / Latrobe, PA | Gas atomization; Co/Ni/Fe, Stellite, WC | production scale | no | booth 818 at MS&T26 |
| **Continuum Powders** (Custom Foundry Runtime) | Houston, TX / Cloverdale, CA | Plasma-gas atomization sold as machine runtime | **40–50 kg** | not stated | 707-234-5565, continuumpowders.com/contact |
| **Nanoval** | Berlin, Germany | Laval-nozzle gas atomization | **2 kg** to 5,000 kg; "small amounts for first testing" | per quote | nanoval.de |
| **Additive Plus** (US distributor of 3D Lab's ATO ultrasonic atomizers, Poland) | California, USA | Ultrasonic (ATO); "custom alloy batch runs in 3–4 weeks" | per quote | per quote | additiveplus.com |
| **Blue Power / Indutherm** | Walzbachtal, Germany | AUS 500 induction ultrasonic atomizer maker | equipment, not service | — | bluepowerinduction.com |

How to use this list: the top three rows are the same price band the VCL would compete in
(tens of grams to a few pounds, ultrasonic or research atomizer, €1,000-ish entry price).
Rows from Rosswag down are gas-atomization houses whose minimums (5–50 kg and up) are the
reason a university ultrasonic atomizer has a market at all. Quotes from both bands give
the recharge proposal a documented market range, which Regulatory Accounting will not
require but the non-federal surcharge discussion will benefit from.

## 7. Outreach list: academic and national-lab facilities

| Facility | Instrument | Public rates? | Contact |
| --- | --- | --- | --- |
| **Northwestern CMPF (CHiMaD)** | rePowder, plasma torch | yes, per run (§3) | cmpf@northwestern.edu, 847-467-6283; 1801 Maple Ave, Evanston |
| **Johns Hopkins MCP** | rePowder, **induction + plasma** | yes, hourly (§3) | MCPadmin@jhu.edu, 410-516-2203; Stieff Building, Baltimore |
| **Georgia Tech AMPF** | rePowder, **induction + plasma** | yes, hourly (§3) | ampf.research.gatech.edu |
| **Ames National Laboratory PSDC** | Close-coupled gas atomizers, 2–5 kg and 10–25 kg | no; DOE SPP cost estimates | PSD@ameslab.gov |
| **Royce / University of Sheffield** | Arcast EIGA (induction + gas), Tekna spheroidiser | no; access schemes | royce@sheffield.ac.uk |
| **Empa** (Switzerland) | rePowder (AMAZEMET shipment announcement) | no | via AMAZEMET partner list |
| **Technical University of Munich** | rePowder (commissioned Feb 2024; Al alloys, chip recycling) | no | AMAZEMET case study |
| **Chemnitz University of Technology** | rePowder (2024; high-Mn Fe alloys for coatings) | no | AMAZEMET case study |
| **TU Darmstadt** | rePowder (magnetocaloric Gd powders) | no | AMAZEMET references |
| **Mintek** (South Africa) | rePowder (Sept 2023) | no | Mining Weekly |
| ORNL MDF, LLNL, NASA MSFC | rePowder systems (AMAZEMET partner list; NASA PO above) | user-program / not fee-for-service | — |

Northeastern University is named in a search summary as a rePowder user but no facility
page could be found; treat as unverified. The three US universities with public rates are
the natural first calls: they are the peer group Regulatory Accounting would recognise, and
JHU's and Georgia Tech's induction modules are the exact hardware configuration.

## 8. A one-paragraph quote request that works for both lists

> We operate a research ultrasonic atomizer (AMAZEMET rePowder, induction module, ≤1300 °C)
> and are benchmarking custom alloy powder development. Please quote (a) a single custom
> aluminum alloy composition we specify, 500 g and 2 kg of spherical powder, 20–63 µm, with
> certificate of analysis and PSD; (b) your minimum order and lead time; (c) whether you
> can pre-alloy from elemental feedstock or require master alloy; (d) any NRE or
> alloy-development fee separate from per-kg price. Please also state whether you offer
> academic or research pricing.

Keep the alloy generic in the first round; the point is a comparable number, not a
disclosure of what the lab is developing.

## 9. What this changes in the dossier, and what it does not

- **Nothing in the rate design changes.** The three published US rates bracket the draft
  numbers (§3). The draft's $918 internal rate is below Northwestern's $1,075 and above the
  hourly facilities' machine-only rows; the draft's $1,650 non-federal rate matches Georgia
  Tech's external rate.
- **The $250k planning cost is consistent with the only public purchase price** (NASA's
  $286,720 for a plasma-configured system). The capitalized-cost worksheet still needs the
  actual invoice, tariff, freight and installation figures.
- **AMAZEMET's €1,000 / 50 g service and Goodfellow's 100 g custom powders set the market
  floor** for the smallest jobs. A per-job minimum fee in that range is defensible as
  "setup and expendables" under policy p. 4 and is in line with what research customers
  already pay.
- **The first official document is unchanged**: the establishment proposal, to the
  Department Chair, with the rate proposal attached, forwarded Chair → Dean (→ VP office) →
  Director of Regulatory Accounting (Rebecca Harrison).

## 10. Sources (all fetched 6 October 2026)

**BYU**
- BYU Financial Services, Accounting (Regulatory Accounting and Reporting contact): https://finserve.byu.edu/accounting
- BYU Recharge Center Policy & Procedures (June 2005), pp. 1–2, 9: [`byu-recharge-center-policy-and-procedures.pdf`](byu-recharge-center-policy-and-procedures.pdf)

**AMAZEMET / rePowder**
- rePOWDER product page: https://www.amazemet.com/repowder/
- AMAZEMET in numbers: https://www.amazemet.com/amazemet-in-numbers/
- Atomization service: https://www.amazemet.com/amazemet-new-business-line-atomization-service/ and https://3dprintingindustry.com/news/amazemet-launches-custom-atomization-service-for-rd-alloy-development-242187/
- References / partners: https://www.amazemet.com/references/
- AXT distributor page (modules): https://www.axt.com.au/products/ultrasonic-powder-atomiser-and-alloy-prototyping-platform/
- NASA MSFC sole-source award, $286,720: https://www.federalcompass.com/award-contract-detail/80MSFC24PA004 and https://www.highergov.com/contract-opportunity/notice-of-award-of-sole-source-ultrasonic-atomizer-23-80-msfc-p-8c2de/
- A3DM Technologies (US distributor): https://www.crunchbase.com/organization/a3dm-technologies
- Blue Power AUS 500: https://bluepowerinduction.com/our-machines/plants-for-metal-powder-production/ultrasonic-atomizer-aus-500 and https://www.metal-am.com/blue-power-and-amazemet-develop-compact-ultrasonic-atomiser/
- Mintek: https://www.miningweekly.com/article/mintek-shows-off-its-new-amazemet-ultrasonic-atomiser-2023-09-11
- TUM / Chemnitz case studies: https://www.amazemet.com/technical-university-of-munich-amazemet-case-study/ ; https://www.amazemet.com/chemnitz-university-of-technology-partnership-and-persistence-in-securing-funding-case-study/
- Empa shipment: https://www.amazemet.com/amazemet-ships-repowder-ultrasonic-atomization-platform-to-empa/

**Facility rates**
- Northwestern CMPF pricing: https://cmpf.northwestern.edu/fees/ ; instrument page: https://cmpf.northwestern.edu/equipment/amazemet-repowder-ultrasonic-atomizer-2/
- JHU MCP fee structure (Wayback, 13 Jan 2026): https://web.archive.org/web/20260113092112/https://engineering.jhu.edu/MCP/fee-structure/ ; instrument page: https://engineering.jhu.edu/MCP/equipment/amazemet-repowder-ultrasonic-powder-atomizer-and-alloy-prototyping-platform/ ; iLab listing: https://johnshopkins.ilab.agilent.com/service_center/show_external/3809
- Georgia Tech AMPF rates: https://manufacturing.gatech.edu/facilities/equipment-usage-rates ; instrument page: https://ampf.research.gatech.edu/amazemet-repowder
- Ames Lab PSDC: https://www.ameslab.gov/dmse/powder-synthesis-and-development-capability and https://www.ameslab.gov/dmse/powder-synthesis-and-development-capability/faq-about-psd
- Royce / Sheffield: https://www.royce.ac.uk/equipment-and-facilities/powder-atomising/ and https://sheffield.ac.uk/royce-institute/capabilities/materials-processing/powder-production
- Mines SIF user fees: https://sif.mines.edu/user-fees ; UMass IALS rates: https://www.umass.edu/ials/core-facility-rates

**Belmont Metals**
- Custom alloys: https://www.belmontmetals.com/custom-alloys/ ; powder development article: https://www.belmontmetals.com/how-to-develop-alloy-powders-for-3d-printing/ ; feedstock article: https://www.belmontmetals.com/the-secret-to-perfect-powder-it-starts-with-the-feedstock/ ; directory listing: https://www.azom.com/suppliers.aspx?SupplierID=4182

**MS&T26 / Advanced Materials Show USA**
- MS&T26 advance brochure: https://archive.tms.org/matscitech/mst26/MST26-Advance-Brochure.pdf ; final program: https://archive.tms.org/matscitech/mst26/MST26-Final-Program.pdf
- Advanced Materials Show USA 2026 exhibitor list: https://advancedmaterialsshowusa.com/exhibitor-list/ ; partnership page: https://advancedmaterialsshowusa.com/the-advanced-materials-show-usa-partners-with-mst/
- Goodfellow custom alloy powders: https://www.goodfellow.com/usa/services/custom-metal-alloy-powders ; show page: https://www.goodfellow.com/usa/resources/events-advanced-materials-show-2026-pittsburgh/

**Industry**
- Rosswag: https://www.rosswag-engineering.de/en/news/metal-powder-portfolio-at-rosswag/
- Ultra Fine Specialty Products: https://www.metal-am.com/ultra-fine-specialty-products-announces-line-of-metal-powders-specifically-for-additive-manufacturing/
- Arcast: https://www.metal-am.com/articles/arcast-melting-and-atomisation-expertise-for-a-new-generation-of-metal-powders/ ; http://www.arcastmaterials.com/powder.htm
- Atomising Systems Ltd: https://www.atomising.co.uk/news ; https://www.metal-powder.co.uk/
- Valimet: https://valimet.com/custom-aluminum-alloys/
- Equispheres: https://equispheres.com/product-lines/
- Elementum 3D: https://www.elementum3d.com/aluminum/
- 6K Additive: https://www.6kinc.com/news/press-release/6k-demonstrates-custom-engineered-metal-alloy-powders-for-additive-manufacturing-at-formnext/
- ATI Powder Metals: https://www.metal-am.com/ati-to-expand-nickel-based-superalloy-powder-capabilities-for-additive-manufacturing-sector/
- Kennametal: https://www.metal-am.com/kennametal-launches-stellite-powder-for-additive-manufacturing/
- Continuum Powders CFR: https://www.continuumpowders.com/continuum-launches-custom-foundry-runtime-to-accelerate-specialty-and-small-batch-alloys/
- Nanoval: https://www.metal-am.com/nanoval-offers-extensive-range-of-alloys-to-metal-additive-manufacturing-market/
- Additive Plus / ATO: https://additiveplus.com/product-category/atomizers/

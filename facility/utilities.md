# Utilities: what a facility like this needs, what we could hook into, and what we'd build

*If we were to build a facility like this* (the vertical cloud lab in the
[#303](https://github.com/vertical-cloud-lab/byu-vcl/issues/303) visualizations,
[PR #318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318)), which utilities would it need? Which could we hook
into, and which would we have to build ourselves? In particular, are there R&D zones with argon ready to hook up to?
Gage asked this on [#343](https://github.com/vertical-cloud-lab/byu-vcl/issues/343). The answer builds on the
requirements in [`README.md`](README.md#1-what-the-facility-needs).

Everything was read from public pages on 2026-11-12. **Nobody was contacted.** "(snippet)" marks a fact seen only in a
search result, not on a page that was opened. Sizes marked *estimate* are worked out here from the repo's own numbers,
not quoted by anyone.

## Short answer

- **Only five utilities come from outside:** electricity, natural gas, water, sewer and telecom. In an industrial park
  each normally reaches the lot line already, from a city, a utility or a carrier. Buildings differ in **how much** has
  been brought in, above all the electrical service.
- **We'd build everything the process uses**, inside whatever building we lease: argon, nitrogen, chilled water,
  compressed air, vacuum, exhaust and make-up air, dust collection, gas and oxygen monitoring, standby power and DI
  water. A new warehouse shell has lights, ESFR sprinklers, restrooms, docks and some power, and little else.
- **Argon: no R&D zone here has it on tap, and that would be unusual anywhere.**
  - No argon or nitrogen pipeline network turned up in Utah, and no Utah lab building advertises house gases.
  - In the US, argon goes by pipe only from an air separation plant built on or beside the user's own site, for a steel
    mill or a fab. Everyone else gets liquid argon by truck, into a tank on their own site that the gas supplier fills
    and rents to them ([§3](#3-argon-and-nitrogen-a-tank-on-our-own-pad)).
  - So "argon ready to hook up" in practice means a building where an earlier tenant left a gas pad, a vaporizer and
    piping. That saves the pad and the piping, not the supply contract, which we would sign wherever we went.
- **No district chilled water or steam** was found for private buildings in Utah County or the south valley either
  ([§2](#2-who-supplies-the-outside-utilities-by-city)).
- **So what to pay for in a building** is what is slow or costly to add:
  - **power already in**, 2,000-4,000 A at 480 V: a generator, a transformer or switchgear can take 30-65 weeks
    ([§4](#4-rough-costs-and-lead-times-for-what-wed-build)), while a gas tank takes weeks;
  - **roof strength, or ground space**, for exhaust fans and make-up air units;
  - **process utilities an earlier tenant left:** a gas pad, compressed-air lines, a generator, clean rooms. The
    BlendTec building in Orem has the last three ([README](README.md#places-that-already-run-gases-or-hazardous-materials));
  - **a precedent:** an earlier tenant at the address that held gas, hazardous-materials or wastewater permits.

## 1. Each utility: what uses it, how much, and hook up or build

*The #318 floor* is the lab as PR #318 lays it out. *Ten a day* is
[PR #332](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/notes/bottleneck.md)'s ten-alloys-a-day
line, with 3 rePowder atomizers, 4 Aconity MIDIs, the EOS M 400-4 and the Meltio cell, among others.

| Utility | What uses it | How much | Hook up or build |
|---|---|---|---|
| **Electricity** | Everything. The Kardex Shuttles are 208 V three-phase ([#53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53)). The rePowder takes 400 V and 230 V on 32 A plugs ([install call](../rePowder-BYU-Installation-Details.txt)). The EOS is 3 × 50 A, the wire EDM 13 kVA, a tray up to 3.5 kW | About 2,000-3,000 A at 480Y/277 V for ten a day ([README](README.md#everything-else-a-building-has-to-provide), *estimate*) | **Hook up** to the city or utility. **Build** the transformers to 400 V (for the European machines) and to 208Y/120 V, the panels, and the UPSs on the trays |
| **Standby power** | The ventilation of a hazardous (Group H) room, which the code requires on standby power ([README](README.md#codes-that-decide-the-building)); gas and oxygen alarms; controls and network; robots parking safely | Tens to a few hundred kW (*estimate*) | **Build**: a generator and UPSs |
| **Natural gas** | Space heating, and above all heating the make-up air that replaces what the hoods and dust collectors exhaust, through Utah winters | Set by the exhaust airflow | **Hook up**. The process heat (melting, printing, furnaces) is electric |
| **Water** | Sinks, eyewashes and safety showers, the polisher, top-up for the wire EDM's deionised water, and the sprinklers | Small for the process | **Hook up** to the city main. **Build** backflow preventers, a tempered-water mix for the showers and eyewashes, and a small RO/DI unit. Ask for the fire flow at the address: sprinklers in the array or racks may need a fire pump |
| **Sewer** | Sinks, the polisher, cleaning | Small | **Hook up**, under the sewer district's rules for non-domestic wastewater ([§2](#2-who-supplies-the-outside-utilities-by-city)). **Build** a settling tank or filter for polishing slurry. No powder goes down a drain: fine Al in water makes hydrogen, so the sieves are washed in IPA, which is collected as waste ([vertical-lab README](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/README.md)) |
| **Telecom** | Remote control, the stream cameras, data | 1 Gbit/s or more, from two carriers (*estimate*) | **Hook up** to the carriers. **Build** the network inside. A cloud lab goes offline when its line does, so two carriers on different routes are worth asking for |
| **Argon** | The rePowders (5N, up to 8 bar, about 10 L/min each while atomizing), the printers, furnaces and gloveboxes | Three rePowders atomizing round the clock use about 43 m³ a day: four or five high-pressure cylinders a day, or a 230 L liquid cylinder every four days (*estimate*). The printers come on top; their draw needs the vendors' figures | **Build**: a microbulk or bulk tank on our own pad, filled and rented by the gas supplier, with a vaporizer and piping ([§3](#3-argon-and-nitrogen-a-tank-on-our-own-pad)) |
| **Nitrogen** | Every tray's coupling ([`services.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/9ca1a9c/vertical-lab/notes/services.md)), glovebox purges, inerting, perhaps the array's fire protection | One glovebox's first purge takes about 2.4 m³ ([`instruments_r7.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/cc31ddc/vertical-lab/instruments_r7.py)). The 1.1 L/min generator PR #331 picked would take 36 h for that | **Build**: a larger PSA generator off the house air, or a liquid-nitrogen tank, or both ([§3](#3-argon-and-nitrogen-a-tank-on-our-own-pad)) |
| **Helium, forming gas** | The XRF's helium mode for loose powder (Bruker S2 PUMA); forming gas only if a glovebox purifier is added | Small | **Build**: cylinders |
| **Chilled water** | The rePowder's heat exchanger, the printers' lasers, the EOS, the trays' couplings | The sum of the machines' heat to water: ask each vendor | **Build**: one loop with an outdoor chiller or dry cooler, or the packaged chillers that come with each machine, whose heat then goes into the room |
| **Compressed air** | The EOS (7 bar, 20 m³/h), the N₂ generator (60-125 psig), the polisher, the Mastersizer (0-4 bar), the rePowder's optimizer | A few tens of m³/h (*estimate*) | **Build**: compressor, dryer, receiver, piping |
| **Vacuum** | The SEM, glovebox antechambers, vacuum furnaces | Point of use | **Build**: a pump at each instrument |
| **Exhaust and make-up air** | Fume hoods, the downdraft sieving enclosure, local exhaust at the atomizers and the printers' powder stations, and about 7 kW of heat in each VLM (700-4,200 m³/h of ventilation per VLM, #331) | Likely the largest fit-out item | **Build**: fans, ducts and heated make-up air units. Warehouse roofs often can't carry them, so they may have to stand on the ground ([README](README.md#everything-else-a-building-has-to-provide)) |
| **Dust collection** | Sieving, powder handling, depowdering the printers | | **Build**: a listed wet-type collector indoors, or a collector outside the building (IFC chapter 22, [README](README.md#codes-that-decide-the-building)) |
| **Humidity control, HEPA** | The powder room, as in CB 154 (DAL [#131](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/131), [#127](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/127)) | | **Build** |
| **Gas and oxygen monitoring** | Wherever argon or nitrogen can collect: the powder room, gloveboxes, any pit under the array | | **Build**. CB 154 needed an O₂ detector ([#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31)) |
| **Fire protection** | The building, the array, the powder | | **Hook up** to the building's sprinklers and alarm. **Build** the changes for lab rooms, Class D extinguishers, and the array's own nitrogen system, since NFPA 13 limits ceiling-only ESFR heads to 45 ft ceilings ([README](README.md#codes-that-decide-the-building)) |

## 2. Who supplies the outside utilities, by city

**The same everywhere:**
- **Natural gas:** Enbridge Gas Utah. Enbridge bought Dominion Energy's Utah gas business (formerly Questar Gas) in
  2024 ([KUTV](https://kutv.com/news/eye-on-your-money/dominion-energy-is-now-enbridge-gas-in-utah), snippet).
  Not checked city by city.
- **Culinary water:** the city, in each city below (not checked address by address). Draper has two providers, Draper
  City and WaterPro ([Draper](https://www.draperutah.gov/living-in-draper-city/utilities/water-and-storm-water/), snippet).

**By city**, for the cities in the [candidate list](README.md#2-candidate-sites):

| City | Candidate sites | Electricity | Sewer district, and its rules for non-domestic wastewater | Fibre |
|---|---|---|---|---|
| **Lehi** | Holbrook Bldgs 5 and 2, Thanksgiving Way, Millplace, Lewis Landing, 1657 N State St | **Lehi City Power**, the city's own ([Lehi](https://www.lehi-ut.gov/departments/power/power-sources/)), a [UAMPS](https://uamps.com/members) member | **TSSD** ([pretreatment](https://timpssd.gov/pretreatment)): new buildings and remodels "must meet the requirements of the Pretreatment program on paper, before the buildings are built or remodeled"; a pretreatment survey comes with the business licence | **Lehi Fiber**: city-owned, open access, run by Strata Networks, with five ISPs that quote business service ([Lehi](https://www.lehi-ut.gov/living-in-lehi/lehi-fiber)) |
| American Fork | AF Industrial Bldg 1, Catalyst Ph. 3, Price AF, Fluke Industrial (sale) | Rocky Mountain Power | TSSD | a city fibre project restarted as a public-private partnership in April 2025, status unclear ([AF Citizen](https://afcitizen.com/2025/04/15/new-partnership-reboots-long-delayed-af-fiber-project), snippet) |
| Lindon | 310 N Geneva Rd | Rocky Mountain Power | Orem's plant, under an interlocal agreement ([agreement](https://www.utah.gov/pmn/files/1105887.pdf), snippet) | UTOPIA ([UTOPIA](https://www.utopiafiber.com/faqs), snippet) |
| Orem | BlendTec | Rocky Mountain Power | Orem's plant; the city issues industrial permits ([Orem](https://orem.gov/pretreatment), snippet) | UTOPIA ([Orem](https://orem.org/utopia), snippet) |
| **Provo** | Provo Manufacturing Facility, Vista Heights | **Provo Power**, the city's own, a UMPA member ([UMPA](https://www.utah.gov/pmn/files/1318719.pdf), snippet) | Provo's plant; city code provides for individual wastewater discharge permits ([§10.04.180](https://provo.municipal.codes/Code/10.04.180), snippet) | Google Fiber, with small-business service since 2015 ([Google](https://fiber.google.com/cities/provo), [Lightwave](https://lightwaveonline.com/fttx/ftth-b/article/16651068/google-fiber-launches-business-services-in-provo), snippet) |
| **Springville** | Hamilton Commerce Center, Center Street Industrial | **Springville City Power**, the city's own, a UAMPS member | Springville's plant; city code provides for individual discharge permits ([Title 4 Ch. 14](https://codepublishing.com/UT/Springville/html/Springville04/Springville0414.html), snippet) | Google Fiber, approved in 2021 ([Daily Herald](https://www.heraldextra.com/news/local/2021/oct/20/google-fiber-is-coming-to-springville-after-city-council-approval/), snippet) |
| **Spanish Fork** | Global Logistics HQ, El Tenedor | **Spanish Fork City Power**, the city's own, a UMPA member ([UMPA](https://www.utah.gov/pmn/files/1318719.pdf), snippet) | Spanish Fork's plant; a questionnaire with the business licence, and an industrial discharge application ([Spanish Fork](https://www.spanishfork.gov/living-in-our-community/water-and-sewer/sewer-info/pretreatment/), snippet) | SFCN, the city's own network, with a business service ([SFCN](https://www.sfcn.org/press/business_network.php), snippet) |
| Saratoga Springs | Pioneer Crossing, Northshore, Spring Heights | Rocky Mountain Power | TSSD | no city network found |
| Bluffdale | Mountain Point Bldg 3 | Rocky Mountain Power | **JBID**, which "issues industrial wastewater discharge permits" ([JBID](https://jbidut.gov/?p=164)) | All West Communications ([All West](https://www.allwest.com/blog/all-west-communications-kicks-off-fiber-internet-construction-in-bluffdale-utah/), snippet) |
| Herriman | Axia | Rocky Mountain Power | JBID ([service area](https://jbidut.gov/collection-system/service-area/)) | All West ([Herriman](https://herriman.gov/fiber-internet), snippet) |
| Draper | Lone Peak "Fuji", Lone Peak Innovation Center Bldg 17, 12162 Business Park Dr | Rocky Mountain Power | JBID for the Salt Lake County part, TSSD for the Utah County part ([service area](https://jbidut.gov/collection-system/service-area/)) | not verified |
| Eagle Mountain | the land beside the 200 MW substation, Tract Pole Canyon | Rocky Mountain Power, since the city sold it its electric system in 2014-15 ([KUER](https://www.kuer.org/energy-environment/2014-11-06/rocky-mountain-power-to-take-over-eagle-mountains-electric-system), snippet) | the city's own plant ([Eagle Mountain](https://eaglemountain.gov/government/public-utilities/), snippet); TSSD also lists Eagle Mountain | Direct Communications ([Directcom](https://directcomfiber.com), snippet) |

- **Four candidate cities run their own power: Lehi, Provo, Springville and Spanish Fork.** So do Payson and Salem.
  Rocky Mountain Power is the state's only rate-regulated electric utility
  ([Utah Office of Consumer Services](https://commerce.utah.gov/ocs/learn-about-your-service-provider/electric-utilities)).
  None of the other cities above is on the state's list of municipal utilities, so they are taken to be on Rocky
  Mountain Power; confirm by address. A city utility sets its own fees and timelines: Lehi's impact fees are in
  [README §3](README.md#3-renovate-or-build).
- **Every sewer district here regulates non-domestic wastewater.** For a lab that means at least a survey with the
  business licence, possibly a permit, and in TSSD's area a plan review before the fit-out. What we'd send down the
  drain is mostly sink and polishing water; whether that needs a permit is the district's call (draft 8).
- **District energy:** none is offered to private buildings in the area. At The Point in Draper a geothermal "thermal
  grid" is only proposed ([feasibility study, Sept 2025](https://energy.utah.gov/wp-content/uploads/The-Point-Geothermal-Feasibility-September-2025-Rev1.0-LowRes-2-1-1.pdf),
  snippet), and the University of Utah sells chilled water from its own plants to its own buildings
  ([U of U](https://facilities.utah.edu/se/resources/chilled-water-rates/index.php), snippet).
- **Fire flow:** nothing public for these parks. Ask the city for the fire flow at an address before counting on
  sprinklers in a tall array.

## 3. Argon and nitrogen: a tank on our own pad

### Why nothing is on tap

- **No industrial-gas pipeline network turned up in Utah.** The only Utah gas pipelines found were inside one plant:
  the oxygen lines within Geneva Steel's works in Vineyard, in a 1997 contract
  ([Law Insider](https://lawinsider.com/contracts/6svf50nOCrD)).
- **In the US, argon goes by pipe only from an air separation plant on the user's site.** UIG says argon is delivered
  "through pipeline systems when integrated with on-site ASU installations", and otherwise by bulk liquid or cylinders
  ([UIG](https://uigi.com/industrial-gas-services/on-site-gas-production/on-site-argon-production/)). Nippon Sanso
  Matheson pipes only oxygen and nitrogen, and sells argon as bulk liquid by truck
  ([NSMG](https://us.nipponsanso.com/?p=869)). On-site plants are for steel mills and fabs, on contracts of 7-15 years
  ([UIG](https://uigi.com/services-overview/), snippet).
- **No Utah lab or R&D building advertises house gases, bulk nitrogen or argon.** The lab listings found give size and
  lab suitability only. 860 W LeVoy Dr in Taylorsville, zoned R&D, offers venting shafts and emergency power, and mentions
  no gases ([CityFeet](https://www.cityfeet.com/cont/listing/860-w-levoy-dr-taylorsville-ut-84123/cs30624186), snippet).
- **Texas Instruments' LFAB in Lehi:** nothing public on its gas supply, nor on any supply to neighbours.
- **Where the liquid comes from** is not settled. In 1997 Air Liquide ran an air separation plant at Geneva Works in
  Vineyard that made liquid argon ([Law Insider](https://lawinsider.com/contracts/6svf50nOCrD)); whether it still
  exists was not found. Linde runs an air separation plant at Garfield, in Magna (job postings, snippet). Praxair's 2015
  Salt Lake City liquefier was for nitrogen and oxygen
  ([Hydrocarbon Processing](https://hydrocarbonprocessing.com/news/2015/10/praxair-adds-new-utah-liquefier-to-serve-refiners/)).
  No Utah plant was confirmed to make argon. Ask each supplier which plant fills Utah County (draft 6).

### How a supplier tank works

- **The supplier puts a cryogenic tank on our site, fills it by tanker, and watches its level by telemetry**
  ([NSMG](https://us.nipponsanso.com/?p=869)). We pay a monthly rental and the gas. One public price sheet, a Maine
  state contract from 2022, lists $466.67 a month for the tank, $50 for telemetry and argon at $5.85 per 100 ft³
  ([Maine](https://www.maine.gov/dafs/bbm/procurementservices/sites/maine.gov.dafs.bbm.procurementservices/files/inline-files/2022%20MA%20221121-076%20Prices.pdf),
  snippet). At that price, three rePowders atomizing round the clock would use about $90 of argon a day (*estimate*).
- **Sizes and when to switch** (all snippet): Airgas microbulk is 230-1,500 L, for more than 20 cylinders a month
  ([Airgas](https://www.airgas.com/solutions/gas-supply-modes/microbulk)). Air Products suggests microbulk above 10
  cylinders a month ([Air Products](https://microsites.airproducts.com/ae/expert/Ask_the_experts/Supply_options.htm)).
  Bulk tanks run 6,000-60,000 L ([Air Liquide's Vietnam page](https://vn.airliquide.com/bulk-supply)). Rocky Mountain Air suggests bulk
  above about one liquid cylinder a week ([README](README.md#3-renovate-or-build)). At four or five cylinders a day for
  the atomizers alone, ten a day is past all of these.
- **What we'd provide:** the concrete pad (7 × 7 ft and 12 in thick for a 1,500 L microbulk tank, 10 × 10 ft for
  2,000 L, per Air Products' install guide,
  [PDF](https://www.airproducts.ca/-/media/files/en/237/237-11-002-us-cryoease-microbulk-solutions-standard-outdoor-installation.pdf),
  snippet); the setbacks, a screen and truck access ([README](README.md#codes-that-decide-the-building)); the permit;
  the piping to each machine and its regulators; and oxygen monitoring.
- **Time:** weeks, not months. Air Products says microbulk can go in about four weeks once designed
  ([README](README.md#3-renovate-or-build), snippet).

### Nitrogen: make it or have it delivered

- **A PSA generator** off the house air suits a steady, modest flow such as the tray couplings. Purity costs output:
  one Berg unit gives 59 Nm³/h at 99.99 % but 32.2 Nm³/h at 99.999 %
  ([DirectIndustry](https://www.directindustry.com/prod/berg-kompressoren-gmbh/product-4603099-2860151.html), snippet).
- **A liquid-nitrogen tank** suits big, short draws: a glovebox's first purge, or inerting a vessel. The array's
  nitrogen fire protection is a separate cylinder bank sold with it.
- **Both** is a common pattern: the generator for the base load, a microbulk tank for peaks and as a backup.

### Where an earlier tenant might have left a pad

Ask brokers for buildings whose earlier tenants used bulk gas (draft 9): metal fabrication and laser-cutting shops
(nitrogen assist gas, argon mixes for welding), food and beverage plants (nitrogen, CO₂), medical-device makers,
electronics plants and labs. A pad, a vaporizer and stainless piping in place save some weeks and some cost, and they
show the city has permitted bulk cryogenic gas at that address before.

## 4. Rough costs and lead times for what we'd build

Order-of-magnitude figures, mostly from vendors and cost guides. Most are for the equipment alone; installation is
extra unless stated.

| What we'd build | Rough cost | Lead time | Source |
|---|---|---|---|
| Argon or nitrogen microbulk tank (the supplier's) | about $470 a month plus $50 for telemetry, and the gas; the pad is ours | weeks | [Maine contract, 2022](https://www.maine.gov/dafs/bbm/procurementservices/sites/maine.gov.dafs.bbm.procurementservices/files/inline-files/2022%20MA%20221121-076%20Prices.pdf) (snippet) |
| Gas piping in the building | not found; needs a contractor's quote | | |
| PSA nitrogen generator | not found reliably | | |
| Process chiller | $550-1,700 per ton of cooling, equipment | 16-30 weeks for packaged air-cooled units under 300 tons | [Terrapin, Nov 2026](https://terrapincg.com/news/data-center-chiller-cost-lead-times-2026) |
| Compressed air: a 50 hp rotary screw with dryer | about $26,000-32,000, equipment | 18-21 weeks (one listing) | [Portland Compressor](https://portlandcompressor.com/store/chicago-pneumatic-50hp-gear-drive-rotary-screw-air-compressor-with-integrated-air-dryer-215cfm-125psi-230-460v-cpcm-50-d), [Ferguson](https://www.fergusonhome.com/quincy-compressor-4152016908/s2095847) (both snippets) |
| Standby generator, 500 kW | about $180,000-220,000 new; $260,000-435,000 with transfer switch and installation (snippets, weak sources) | 32-48 weeks for 500-1,000 kW; 12-30 weeks for 500 kW from one distributor | [Terrapin](https://terrapincg.com/news/switchgear-transformer-generator-lead-times-2026), [Global Power, May 2026](https://globalpwr.com/blog/generator-lead-times-in-2026) |
| Dust collector for combustible metal, with explosion protection | $25,000-75,000 at 3,000-8,000 CFM; $75,000-200,000 at 10,000-25,000 CFM; one 8,000-10,000 CFM project cost $376,000 installed | 10-14 weeks | [Industrial Clean Air Products, 2026](https://industrialcleanairproducts.com/combustible-dust-collectors/) (a vendor) |
| Fume hood, 6 ft | $8,000-57,000 each, plus ducts and make-up air | | [OnePointe, 2020](https://www.onepointesolutions.com/blog/how-much-does-a-fume-hood-cost/) |
| Oxygen-depletion monitoring | about $1,500 a sensor point in a 3-point system | | [Process Insights](https://www.process-insights.com/products-3/products-industrial/oxygen-analyzers/series-1000-oxygen-deficiency-monitor/) |
| Pad-mount transformer, 2,500 kVA | from about $80,000 (snippet); often the utility's to supply, so ask it first | 12-26 weeks from stock, 40+ custom; 40-65 weeks for pad-mount units up to 5 MVA | [Giga Energy, 2025](https://www.gigaenergy.com/blog/transformer-lead-times), [Terrapin](https://terrapincg.com/news/switchgear-transformer-generator-lead-times-2026) |
| 480 V switchboard, 2,000-4,000 A | not found | switchgear averaged 44 weeks in 2025 | [README](README.md#3-renovate-or-build) |

**The slow items are electrical:** the generator, the transformer and the switchboard (30-65 weeks), then the chiller
and the compressor (16-30 weeks). A gas tank takes weeks. That is the same conclusion as the README's: a building
with the power already in is worth paying for.

## 5. What to look for on a tour

Each of these already in place is something we don't have to build.

1. **The electrical service:** amps, voltage, the transformer's size, and room on site for a bigger one.
2. **Process utilities an earlier tenant left:** a gas pad or tank, gas piping, compressed-air lines, a generator,
   chilled water or a cooling tower, clean rooms, exhaust fans and their roof curbs.
3. **The roof:** whether it can carry exhaust fans and make-up air units, or whether there is ground space for them.
4. **Room outside for a gas tank:** 1 ft from the building, 5 ft from lot lines, 10 ft from air intakes and exits, and
   truck access ([README](README.md#codes-that-decide-the-building)). Lehi wants outdoor equipment behind a 6 ft screen.
5. **The sprinklers and the water main:** ESFR or not, the fire flow at the site, any fire pump.
6. **The sewer:** which district, and whether an earlier tenant held a wastewater permit there.
7. **Telecom:** which carriers already serve the building.
8. **The building itself:** the slab, the roof structure, the sprinkler placard, whether the space is an end unit,
   and who the neighbours are ([`zoning-and-safety.md`](zoning-and-safety.md#4-what-else-to-look-for-in-a-building)).

## 6. Who to ask

None of these has been contacted. Drafts 5 and 6 in [`drafts.md`](drafts.md) are for the power utility and the gas
suppliers. Drafts 8 and 9 are new: one for the sewer district, one asking brokers for buildings with process
utilities already in.

| Who | For | Public page | Draft |
|---|---|---|---|
| **Sewer districts:** TSSD (Lehi, American Fork, Saratoga Springs, part of Eagle Mountain and Draper); Orem (Orem, Lindon); Provo; Springville; Spanish Fork; JBID (Bluffdale, Herriman, Draper) | whether a lab's wastewater needs a survey or permit, and when | [TSSD](https://timpssd.gov/pretreatment), [Orem](https://orem.gov/pretreatment), [Provo](https://provo.municipal.codes/Code/10.04.180), [Springville](https://codepublishing.com/UT/Springville/html/Springville04/Springville0414.html), [Spanish Fork](https://www.spanishfork.gov/living-in-our-community/water-and-sewer/sewer-info/pretreatment/), [JBID](https://jbidut.gov/?p=164) | 8 |
| **Power:** Lehi City Power, Provo Power, Springville and Spanish Fork city power, Rocky Mountain Power | capacity and timeline at an address | [Lehi](https://www.lehi-ut.gov/departments/power/power-sources/), [state list](https://commerce.utah.gov/ocs/learn-about-your-service-provider/electric-utilities) | 5 |
| **Gas suppliers:** Rocky Mountain Air (Orem), Humphries (American Fork, Spanish Fork), Linde (Provo), Airgas, Air Liquide (Lindon), DJB Gas Services, Norco, Matheson | microbulk or bulk, which plant fills Utah County, pad and lead time | [README contacts](README.md#contacts) | 6 |
| **Brokers and EDCUtah** | buildings with process utilities already in | [README contacts](README.md#contacts) | 9 |
| Enbridge Gas Utah | a gas service big enough to heat the make-up air | [Enbridge update](https://dominionenergy.com/utah/enbridge-update) | none |
| Fibre: Lehi Fiber, UTOPIA, Google Fiber, SFCN, All West, Direct Communications | business service at an address | linked in [§2](#2-who-supplies-the-outside-utilities-by-city) | none |

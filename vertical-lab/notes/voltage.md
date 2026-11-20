# Voltage: what each machine needs, against the tray dock

Sterling (PR #318, 2026-11-20): "Are all modules within the VLM currently 120 V? Do some have higher power
requirements?"

## Short answer

**Not all of them.** Two machines on the trays need more than 120 V, and four more draw 12 A or more at 120 V.
Everything else on the twelve powered trays runs from 120 V or has a universal 100-240 V input.

- **208/230 V, both on tray F:**
  - the Nabertherm NAT 15/65 furnace: 2.8 kW would be 23 A at 120 V, so it has to be built for 208 V and go
    across L1-L2 (13.5 A);
  - the LECO PX500 polisher: LECO sells it only as the 230 V PX500A2.
- **12 A or more at 120 V,** each needing a branch circuit of its own:
  - tray D's UPS, the GXT5LI-3000: 24 A on a NEMA L5-30P, a whole 30 A leg;
  - the Form Cure (2nd Gen): 15 A;
  - the T-962A reflow oven: 13.6 A;
  - the H2D: 12 A.
- **Nothing on a tray needs three-phase.** No single machine needs more than one 30 A leg.
- **Two trays don't fit the dock as specified,** counting every machine at its rating at once:
  - **tray D** puts all its current on one leg, at or over the 24 A continuous limit, and nothing on the other:
    24 A at the UPS's input rating, 28 A at the backed machines' ratings;
  - **tray F** reaches 27 A on one leg if the furnace, the PX500 and the MX400 run together.

  Both fit with the changes in [What this means for the dock](#what-this-means-for-the-dock). The other ten trays
  stay within 24 A a leg; the highest is tray G's 15 A.
- **On the floor, the big machines are three-phase:**
  - at 208 V: the two Kardex units, the FANUC wire EDM, the Instron 68FM-100 and the Meltio cell;
  - at 400 V: the Aconity MIDI+ and the rePowder;
  - the EOS M 400-4 at 3 x 50 A, voltage unpublished.

  The InssTek MX-Lab is 220 V single phase.

Every published figure below links to its source. The machine-by-machine data is in
[`out/voltage.json`](../out/voltage.json), built from `ups.TRAY_LOADS`'s tray contents ([`ups.md`](ups.md)), so the
trays are the ones the UPS sizing uses. Of the 53 machines on the trays (not counting cameras and switches):

| Figures | Machines |
|---|---|
| read from the maker's or a distributor's document | 34 |
| from a search snippet or third-party article | 3 |
| not found | 7 |
| PCs not chosen yet | 5 |
| our own designs | 4 |

## The dock, and the rules it works under

Each dock brings **208Y/120 V on four contacts: L1, L2, N and PE**, from a two-pole 30 A breaker (CombiTac 3 mm
contacts, 39 A; [`services.md`](services.md)). That gives a tray:

- **120 V on either leg** (L1-N or L2-N), for anything with a 120 V or universal 100-240 V input;
- **208 V single phase across L1-L2**, for a machine built for 208/230/240 V.

It does not give three-phase: there is no L3.

Four limits follow, from the breaker and the US electrical code (NEC, NFPA 70):

1. **A leg may carry 24 A continuously.** A load that runs three hours or more counts as continuous, and a
   branch circuit may carry only 80 % of its breaker's rating continuously. The furnace holding temperature, the
   SEM's pumps and the UPSs are continuous loads.
2. **One plug-in machine may use at most 80 % of its circuit:** 12 A on a 15 A circuit, 16 A on 20 A, 24 A on
   30 A ([EC&M](https://www.ecmweb.com/qampa/code-qa-cord-and-plug-connected-equipment)).
3. **A 30 A circuit may feed only 30 A receptacles** when it feeds more than one (NEC Table 210.21(B)(3);
   [EC&M](https://www.ecmag.com/section/codes-standards/code-focus-article-210-branch-circuits),
   [Cal/OSHA's copy of the table](https://dir.ca.gov/title8/2360_4.html)). Ordinary 5-15R and 5-20R outlets can't
   hang straight off the dock's breaker. So the tray's distribution box has to have **its own branch breakers**.
4. **The neutral carries real current.** On two legs and a neutral taken from a wye, the neutral carries about
   as much as a loaded leg, not the difference between the legs
   ([EC&M on the code's rule](https://www.ecmag.com/magazine/articles/article-detail/your-business-bad-harmony-what-estimators-need-know-nec)).
   It carries more again with switch-mode supplies that lack power-factor correction, as their third harmonics
   add in it. The 39 A N contact covers 30 A legs, but the N conductor on the tray must be full size.

## How the numbers are made

- **Each machine's current** is taken at the voltage it runs at, in this order of preference:
  1. the maker's published current;
  2. its published VA;
  3. its watts over the voltage, at power factor 1 (so a lower bound);
  4. failing all of these, `ups.TRAY_LOADS`'s rated watts.
- **The backed rows** (ups.py's branch through the tray's UPS) reach the dock as one load, the UPS. It draws the
  backed machines' summed ratings (published VA where there is one), divided by the UPS's efficiency at that load
  (ENERGY STAR, as in ups.py). The UPS's own input rating is given beside it.
- **Legs:**
  - the UPS and each unbacked 120 V machine go on the lighter leg, biggest first;
  - a 208 V machine loads both legs.
- **Sums are arithmetic, with everything at its nameplate at once.** That is an upper bound no schedule reaches;
  it is what the breaker has to allow if nothing on the tray is interlocked.
- **Each tray's camera Pis and switch** are one row. ups.py counts each Pi on its own 27 W supply as well as the
  switch's 60 W; fed by PoE+, they would add nothing beyond the switch.

## Tray by tray

In each table:

- **"Branch"** is ups.py's: backed rows reach the dock through the UPS row.
- **"A at the dock"** is the current used in the leg sums.
- **The source link's text** says how the figure was found:
  - *published*: read in the maker's or a distributor's document;
  - *snippet*: from a search snippet or third-party article;
  - *not_found*;
  - *estimate*: a PC not chosen yet;
  - *ours*: our own design.

### Tray A (R2)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| Opentrons OT-2 | backed | 100-240 V AC, 50/60 Hz (external Mean Well GST220A, 36 V DC to the robot) | about 100-180 W operating (Opentrons); a 220 W supply (1.8 A at 120 V) | external supply (IEC C14 inlet, snippet) | [published](https://docs.opentrons.com/ot-2/installation/requirements/) | 120 V |
| CubXL gantry (Genmitsu PROVerXL 4030 frame, our controller) | backed | switchable 115/230 V AC (Genmitsu's control box): set to 115 | not published; 100 W counted (0.8 A at 120 V) | - | [snippet](https://m.media-amazon.com/images/I/A1Sj30cosNL.pdf) | set the supply's switch to 115 before plugging in |
| NuVant EZstat Pro potentiostat | backed | not found (external supply) | not published; 30 W counted (0.2 A at 120 V) | - | [not_found](https://www.nuvant.com/products/ezstat-pro) | not found |
| Windows PC for EZware | backed | an ordinary desktop PC (100-240 V) | not published; 150 W counted (1.2 A at 120 V) | NEMA 5-15P | estimate | estimate |
| the CubXL's Raspberry Pi 5 | backed | 100-240 V AC (27 W USB-C supply) | 27 W supply (0.2 A at 120 V) | NEMA 1-15P (US supply) | [published](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf) | 120 V |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert GXT5LI-1500LVRT2UXL (1500 VA / 1350 W)** | carries the backed rows | 120 V typical, 60-150 V (online) | input rating 12.0 A (5.8 A at the backed rows' 641 VA/W) | NEMA 5-15P | [published](https://prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf) | 12 A: its own 15 or 20 A branch |

Legs, everything at its rating at once: **L1 5.8 A** (UPS 5.8); **L2 0.0 A** (nothing). N about 5.8 A. With the UPS at its own input rating: L1 12.0 A, L2 0.0 A. **Within 24 A a leg**.

Everything is 120 V or universal. Set the CubXL's Genmitsu supply to 115 before it is plugged in. The EZstat Pro's supply rating wasn't found (read its label).

### Tray B (R3)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| multi-doser chain carousel v5 (Mean Well LRS-350-24 + Pi) | backed | 90-132 V or 180-264 V AC, chosen by a switch (LRS-350-24): set to 115 | 6.8 A typ. at 115 V AC (3.4 A at 230 V); 350 W out; about 400 W in (6.8 A at 120 V) | none: screw terminals (we fit the cord or inlet) | [published](https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF) | switch-selected input: 208 V on the 115 V setting destroys it |
| A&D HR-202i analytical balance | backed | AC adapter for the local voltage (US adapter) | approx. 11 VA (0.1 A at 120 V) | AC adapter (US blades) | [published](https://www.aandd.jp/products/manual/balances/hr-i.pdf) | 120 V |
| Specac Atlas Autotouch 15T press | unbacked | one model per region: 110 V 60 Hz for the USA (GS25811); 230 V 50 Hz UK/EU (GS25810) | not published; 400 W counted (3.3 A at 120 V) | - | [published](https://specac.com/product/autotouch-press-high-throughput-xrf-press/) | 120 V |
| Edwards RV3 rotary-vane pump (A652-01-906, set to 115 V) | unbacked | dual-voltage motor, switched: 110-120 V or 220-240 V, 50/60 Hz | 6.9 A full load at 115-120 V 60 Hz (3.0 A at 230-240 V); 550 W at 60 Hz (6.9 A at 120 V) | IEC inlet on the motor; cord bought separately (Edwards lists a NEMA 6-15P set for 200-230 V) | [published](https://www.vacuumpumpsupply.com/content/1-Manual-Edwards-RotaryVane-RV3-RV5-RV8-RV12.pdf) | 120 V |
| 1 camera Pi 5 and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.7 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert PSI5-800SRT2ULIN (800 VA / 720 W)** | carries the backed rows | 120 V nominal, 75-146 V (line-interactive) | input rating 6.7 A (4.2 A at the backed rows' 493 VA/W) | NEMA 5-15P | [snippet](https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups/psi5-800srt2ulin/) | 120 V |

Legs, everything at its rating at once: **L1 6.9 A** (RV3 6.9); **L2 7.5 A** (UPS 4.2, Autotouch 3.3). N about 7.2 A. With the UPS at its own input rating: L1 6.9 A, L2 10.0 A. **Within 24 A a leg**.

All 120 V. Two inputs are switch-selected rather than universal: the doser's LRS-350 (keep it on 115) and the RV3 (A652-01-906 ships on 115 V). The Autotouch is sold as a 110 V 60 Hz model for the USA (GS25811); its power isn't published.

### Tray C (F1)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| Bambu Lab H2D (100-120 V version) | unbacked | 100-120 V AC (US) / 200-240 V AC (a separate model), 50/60 Hz | max 1320 W at 110 V (2200 W at 220 V); average 1050 W (12.0 A at 120 V) | - | [published](https://bambulab.com/en-us/h2d/tech-specs) | >= 12 A at 120 V: its own 20 A branch |
| Bambu Lab A1 mini | unbacked | 100-240 V AC, 50/60 Hz | 150 W max (1.2 A at 120 V) | - | [published](https://bambulab.com/en-us/a1-mini/tech-specs) | 120 V |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert PSI5-800SRT2ULIN (800 VA / 720 W)** | carries the backed rows | 120 V nominal, 75-146 V (line-interactive) | input rating 6.7 A (1.0 A at the backed rows' 114 VA/W) | NEMA 5-15P | [snippet](https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups/psi5-800srt2ulin/) | 120 V |

Legs, everything at its rating at once: **L1 12.0 A** (H2D 12.0); **L2 2.2 A** (A1 mini 1.2, UPS 1.0). N about 11.1 A. With the UPS at its own input rating: L1 12.0 A, L2 7.9 A. **Within 24 A a leg**.

All 120 V. The H2D's US model is rated 1320 W at 110 V, 12 A: that is 80 % of a 15 A circuit, so it wants a 20 A branch of its own. Don't buy its 200-240 V model by mistake (a separate SKU).

### Tray D (R1)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| Hitachi TM4000PlusII SEM, main unit | backed | single phase 100-240 V AC (90-250 V), 50/60 Hz | 500 VA (4.2 A at 120 V) | - | [published](https://hte.hitachi-hightech.com/hubfs/Product%20Page%20-%20TM4000/Hitachi_TM4000_Series_III_Brochure.pdf?hsLang=en) | 120 V |
| the SEM's PC and monitor (Hitachi-supplied) | backed | not published (a desktop PC: 100-240 V) | not published; 200 W counted (1.7 A at 120 V) | NEMA 5-15P | [not_found](https://hte.hitachi-hightech.com/hubfs/Product%20Page%20-%20TM4000/Hitachi_TM4000_Series_III_Brochure.pdf?hsLang=en) | not found |
| Oxford Instruments AZtecOne EDS (analyser unit) | backed | single phase 100-240 V AC, 50/60 Hz | 400 VA (3.3 A at 120 V) | - | [published](https://matcl.umd.edu/files/2022/06/TM400PlusII-2.pdf) | 120 V |
| Rigaku MiniFlex 600-C (600 W tube, internal chiller) | backed | single phase 100-240 V AC +-10 %, 50/60 Hz | 1.1 kVA (MiniFlex 600 with external chiller: 1.0 kVA) (9.2 A at 120 V) | IEC C14-type inlet (a C13 cord); no cord supplied outside Japan | [published](https://resources.rigaku.com/hubfs/2024%20Rigaku%20Global%20Site/Resource%20Hub/Knowledge%20Library/Brochures/BR_23_MiniFlex_Rev0723_226325528_SinglePgs_low-res.pdf?hsLang=en) | 120 V |
| the MiniFlex's PC | backed | single phase 100-240 V AC (Rigaku's site requirement) | 0.7 kVA (Rigaku's budget for the PC) (5.8 A at 120 V) | - | [published](https://resources.rigaku.com/hubfs/2024%20Rigaku%20Global%20Site/Resource%20Hub/Knowledge%20Library/Brochures/BR_23_MiniFlex_Rev0723_226325528_SinglePgs_low-res.pdf?hsLang=en) | 120 V |
| 3 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (1.2 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert GXT5LI-3000LVRT2UXL (3000 VA / 2700 W)** | carries the backed rows | 120 V typical, 60-150 V (online) | input rating 24.0 A (27.7 A at the backed rows' 3041 VA/W) | NEMA L5-30P (120 V, 30 A, locking) | [published](https://prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf) | L5-30P: a 30 A, 120 V circuit of its own: one whole leg; 24 A is exactly the 30 A leg's continuous limit; backed branch 3041 VA/W at its ratings: over the unit's 2700 W |

Legs, everything at its rating at once: **L1 27.7 A** (UPS 27.7); **L2 0.0 A** (nothing). N about 27.7 A. With the UPS at its own input rating: L1 24.0 A, L2 0.0 A. **Over 24 A continuous on a leg, inside the 30 A breaker** (with the UPS at its own rating: at 24 A on a leg, the continuous limit).

Every machine is universal 100-240 V, so all of it could run at 120 V or at 208 V.

The problem is the UPS: the GXT5LI-3000LVRT2UXL is a 120 V unit with a 30 A L5-30P plug, rated 24 A in. The whole tray hangs on one leg at the continuous limit while the other leg carries nothing. At Rigaku's 0.7 kVA budget for the MiniFlex's PC the backed rows add to 3.0 kVA, more than the unit's 2700 W; with ups.py's 200 W for that PC they add to 2.5 kVA (23 A in).

### Tray E (R4)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| Plastometrex PLX-Benchtop with its PC | backed | not found | not published; 200 W counted (1.7 A at 120 V) | - | [not_found](https://www.plastometrex.com/products/plx-benchtop) | not found |
| KLA iMicro nanoindenter (InQuest controller) with its PC | backed | not found | not published; 300 W counted (2.5 A at 120 V) | - | [not_found](https://www.kla.com/wp-content/uploads/iMicro.pdf) | not found |
| Malvern Mastersizer 3000 optical bench with the Aero S | backed | 100/240 V, 50/60 Hz | not published; 200 W counted (1.7 A at 120 V) | - | [published](https://www.malvernpanalytical.com/br/assets/MRK1872-07-EN_MS3000_Broch_BrandUpdate_LR_web_tcm55-17232.pdf) | 120 V |
| the Mastersizer's PC | backed | an ordinary desktop PC (100-240 V) | not published; 150 W counted (1.2 A at 120 V) | NEMA 5-15P | estimate | estimate |
| the Aero S vacuum extractor (Malvern's 'vacuum unit') | unbacked | not found | not published; 1200 W counted (10.0 A at 120 V) | - | [not_found](https://ougfc.montana.edu/eal-lres/documents/Mastersizer-3000-user-manual-English-MAN0474-2-1.pdf) | not found |
| 3 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (1.2 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert GXT5LI-1500LVRT2UXL (1500 VA / 1350 W)** | carries the backed rows | 120 V typical, 60-150 V (online) | input rating 12.0 A (9.0 A at the backed rows' 991 VA/W) | NEMA 5-15P | [published](https://prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf) | 12 A: its own 15 or 20 A branch |

Legs, everything at its rating at once: **L1 10.0 A** (extractor 10.0); **L2 9.0 A** (UPS 9.0). N about 9.5 A. With the UPS at its own input rating: L1 12.0 A, L2 10.0 A. **Within 24 A a leg**.

All 120 V or universal where published. Three figures weren't found: the PLX-Benchtop, the iMicro and Malvern's vacuum extractor. The extractor is the big one: 1200 W (ups.py's estimate) is 10 A at 120 V.

### Tray F (F2)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| LECO PX500 grinder/polisher (PX500A2) | unbacked | 230 V only: there is no 115 V PX500 (the 115 V models are the PX400A1/S1, 8-10 in wheels) | not published by LECO; 740 W in a search snippet (ups.py) (3.6 A at 208 V) | - | [published](https://www.leco.com/wp-content/uploads/documents/brochures/209-254-PX-series.pdf) | needs 208/230 V: across L1-L2; ask LECO whether 208 V is inside the 230 V unit's tolerance |
| Nabertherm NAT 15/65 forced-convection furnace | unbacked | 230 V 1/N/PE as standard; Nabertherm: every 1-phase furnace can be built for 110-240 V, 50/60 Hz; the US listing found is 240 V single phase | 2.8 kW (current page; 3.3 kW in an older catalogue and the US listing) (13.5 A at 208 V) | - | [published](https://nabertherm.com/en/products/industrie/thermprozesstechnik/prozesse-unter-luft/forced-convection-furnaces/forced) | needs 208/240 V: across L1-L2 (23 A at 120 V would take a whole leg); order it wound for 208 V: a 240 V furnace on 208 V gives 75 % of its power |
| LECO MX400 mounting press, 1.5 in mold (MX400381, 115 V) | unbacked | AC 115 V or 230 V (separate part numbers), 50/60 Hz, single phase | 115 V / 10 A (1.25 in, 1.5 in, 30 mm); 115 V / 12 A (40, 50 mm); 230 V / 5-6 A; heater 900 W (1200 W for 40/50 mm) (10.0 A at 120 V) | - | [published](https://www.leco.com/wp-content/uploads/documents/brochures/209-277-001-MX400.pdf) | 10 A at 120 V: its own 15 or 20 A branch |
| quench tank lift (ours: a stepper on a 24 V supply) | unbacked | 120 V to a 24 V supply (ours) | not published; 60 W counted (0.5 A at 120 V) | - | ours | ours |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert PSI5-800SRT2ULIN (800 VA / 720 W)** | carries the backed rows | 120 V nominal, 75-146 V (line-interactive) | input rating 6.7 A (1.0 A at the backed rows' 114 VA/W) | NEMA 5-15P | [snippet](https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups/psi5-800srt2ulin/) | 120 V |

Legs, everything at its rating at once: **L1 27.0 A** (MX400 10.0); **L2 18.5 A** (UPS 1.0, quench lift 0.5); across L1-L2 at 208 V: PX500 3.6, NAT 15/65 13.5. N about 9.3 A. With the UPS at its own input rating: L1 27.0 A, L2 24.2 A. **Over 24 A continuous on a leg, inside the 30 A breaker**.

Two machines need 208/230 V. LECO sells the PX500 only as the 230 V PX500A2. The NAT 15/65's 2.8 kW would be 23 A at 120 V, so it has to be built for 208 V (Nabertherm builds its 1-phase furnaces for 110-240 V) and go across L1-L2: 13.5 A on each leg (15.9 A at the older 3.3 kW rating).

With the furnace, the PX500 and the 120 V MX400 all on, one leg reaches 27 A: inside the breaker, over 24 A continuous. Either the furnace and the MX400 take turns (ups.md's rule already), or the MX400 is its 230 V model (MX400382, 5 A) across L1-L2 too: then both legs are about 23 A with everything on (at 2.8 kW; 25 A at 3.3 kW). Ask LECO whether its 230 V machines accept 208 V.

### Tray K (2R1)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| glovebox controller: 24 V DC PLC, HMI and supply (ours) | backed | 120 V to a 24 V DC supply (ours) | not published; 30 W counted (0.2 A at 120 V) | - | ours | ours |
| Teledyne 3000TA-XL trace O2 analyser | backed | universal AC input 85-230 V, 50/60 Hz | 20 VA max (0.2 A at 120 V) | - | [published](https://www.chromservis.eu/media/0/05_pdf/Catalogues/Teledyne_3000TAXL_UK.pdf) | 120 V |
| Michell Easidew TX dew-point transmitter | backed | 2-wire 4-20 mA loop, powered from the controller's 24 V DC | not published; 0.5 W counted (0.0 A at 120 V) | none (loop powered) | [snippet](https://www.processsensing.com/docs/datasheet/Michell_Instruments_Easidew_TX_I.S._Datasheet.pdf) | no outlet: loop powered |
| glovebox solenoid valves, 4-6 x 24 V DC (ours) | backed | 24 V DC from the controller's supply | not published; 40 W counted (0.3 A at 120 V) | none | ours | ours |
| antechamber vacuum pump (an Edwards RV3 at 115 V, if the same as the press's) | unbacked | dual-voltage, switched: 110-120 V or 220-240 V | 6.9 A full load at 115-120 V 60 Hz; 550 W (6.9 A at 120 V) | - | [published](https://www.vacuumpumpsupply.com/content/1-Manual-Edwards-RotaryVane-RV3-RV5-RV8-RV12.pdf) | 120 V |
| analytical balance in the glovebox (HR-202i class) | backed | AC adapter for the local voltage | approx. 11 VA (HR-202i) (0.1 A at 120 V) | AC adapter | [published](https://www.aandd.jp/products/manual/balances/hr-i.pdf) | 120 V |
| capper gantry and tipping cradle (ours) | backed | 120 V to a 24 V supply (ours) | not published; 60 W counted (0.5 A at 120 V) | - | ours | ours |
| Keyence VHX-7000 controller (27 in 4K monitor with it) | backed | 100-240 V AC +-10 %, 50/60 Hz | 430 VA (3.6 A at 120 V) | - | [published](https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-7000/) | 120 V |
| Keyence VHX-S750E motorised stand | backed | 100-240 V AC +-10 %, 50/60 Hz | 130 VA (1.1 A at 120 V) | - | [published](https://www.keyence.com/products/microscope/digital-microscope/vhx-7000/models/vhx-s750e/) | 120 V |
| Keyence EA-300 LIBS head | backed | no mains input: powered from the VHX controller's camera port | not published; 0 W counted (0.0 A at 120 V) | none | [published](https://www.keyence.com/products/microscope/elemental-analyzer/ea-300/models/ea-300) | no outlet: powered by the VHX controller |
| PiKVM V4 Mini | backed | 5 V USB-C (its adapter: 100-240 V) | 12 W (ups.py) (0.1 A at 120 V) | USB-C adapter | [published](https://docs.pikvm.org/v4/v4mini_datasheet.pdf) | 120 V |
| 1 camera Pi 5 and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.7 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert GXT5LI-1500LVRT2UXL (1500 VA / 1350 W)** | carries the backed rows | 120 V typical, 60-150 V (online) | input rating 12.0 A (7.5 A at the backed rows' 820 VA/W) | NEMA 5-15P | [published](https://prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf) | 12 A: its own 15 or 20 A branch |

Legs, everything at its rating at once: **L1 7.5 A** (UPS 7.5); **L2 6.9 A** (antechamber pump 6.9). N about 7.2 A. With the UPS at its own input rating: L1 12.0 A, L2 6.9 A. **Within 24 A a leg**.

All 120 V or universal. The antechamber pump isn't chosen; counted as an RV3 at 115 V (6.9 A).

### Tray L (2R2)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| ZwickRoell zwickiLine Z5.0 TN (testControl II) | backed | 100-240 V, 1Ph/N/PE, +-10 %, 50/60 Hz | approx. 500 VA at full load (4.2 A at 120 V) | - | [published](https://www.zwickroell.com/fileadmin/content/Files/SharePoint/user_upload/PI_EN/02_396_zwickiLine_Z0_5_up_to_Z5_0_Materials_Testing_Machine_PI_EN.pdf) | 120 V |
| the testXpert PC | backed | an ordinary desktop PC (100-240 V) | not published; 150 W counted (1.2 A at 120 V) | NEMA 5-15P | estimate | estimate |
| Mitutoyo HM-220 Type D micro-Vickers | backed | 100-125 / 220-240 V AC, 50/60 Hz (US: 100-125 V) | 39 VA (main unit); 90 W counted (ups.py, unsourced) (0.8 A at 120 V) | AC cord set, UL/CSA (02ZAA010) | [published](https://www.mitutoyo.com/webfoo/wp-content/uploads/K_section.pdf) | 120 V |
| the AVPAK PC (Mitutoyo-specified) | backed | an ordinary desktop PC (100-240 V) | not published; 150 W counted (1.2 A at 120 V) | NEMA 5-15P | estimate | estimate |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert GXT5LI-1500LVRT2UXL (1500 VA / 1350 W)** | carries the backed rows | 120 V typical, 60-150 V (online) | input rating 12.0 A (9.1 A at the backed rows' 1004 VA/W) | NEMA 5-15P | [published](https://prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf) | 12 A: its own 15 or 20 A branch |

Legs, everything at its rating at once: **L1 9.1 A** (UPS 9.1); **L2 0.0 A** (nothing). N about 9.1 A. With the UPS at its own input rating: L1 12.0 A, L2 0.0 A. **Within 24 A a leg**.

All universal. ZwickRoell gives 500 VA (ups.py counts 500 W). Mitutoyo gives 39 VA for the HM-220's main unit; the Type D's motorised stage and autofocus have no published rating, so ups.py's 90 W stays.

### Tray M (2R3)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| Bruker S2 PUMA Series 2, XY Autochanger | backed | 100-240 V, 50/60 Hz | max. 600 VA (5.0 A at 120 V) | - | [published](https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2.html) | 120 V |
| the S2 PUMA's optional vacuum pump | unbacked | not found | not published; 300 W counted (2.5 A at 120 V) | - | [not_found](https://www.bruker.com/en/products-and-solutions/elemental-analyzers/xrf-spectrometers/s2-puma-series2.html) | not found |
| Sentry Air SS-224-DCH ductless hood, 24 in | backed | 115 V, 1 phase, 60 Hz (a 220 V / 50 Hz version too) | 0.3 A at 115 V (0.3 A at 120 V) | NEMA 5-15P, 8 ft cord | [published](https://completelabsystems.com/wp-content/uploads/2022/02/ss-224-dch.pdf) | 120 V |
| Makera Carvera (200 W spindle) | unbacked | 100-120 V / 200-240 V AC, 50/60 Hz | 3.6 A at 115 V, 2 A at 230 V (community wiki); 400 W max (Makera) (3.6 A at 120 V) | - | [published](https://www.makera.com/pages/product-compare) | check any 115/230 V selector before first power-up |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert GXT5LI-1500LVRT2UXL (1500 VA / 1350 W)** | carries the backed rows | 120 V typical, 60-150 V (online) | input rating 12.0 A (6.8 A at the backed rows' 749 VA/W) | NEMA 5-15P | [published](https://prep.vertiv.com/491871/globalassets/products/critical-power/uninterruptible-power-supplies-ups/liebert--gxt5-lithium-ion-1000-3000va-rack-tower-guide-specifications.pdf) | 12 A: its own 15 or 20 A branch |

Legs, everything at its rating at once: **L1 6.8 A** (UPS 6.8); **L2 6.1 A** (Carvera 3.6, S2 PUMA pump 2.5). N about 6.5 A. With the UPS at its own input rating: L1 12.0 A, L2 6.1 A. **Within 24 A a leg**.

All 120 V or universal. The S2 PUMA's vacuum pump has no published make or rating (300 W, ups.py's estimate). The Carvera takes 100-120 or 200-240 V: check for a selector before first power-up.

### Tray H (2R4)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| DDM Novastar SPR-45VA stencil printer | unbacked | 120 V AC, 50/60 Hz (220-240 V available) | 2 A (2.0 A at 120 V) | - | [published](https://pentalogix.com/pdf/SPR_45VA_Stencil_Printers.pdf) | 120 V |
| Opulo LumenPnP v4 (24 V 6 A supply) | backed | 100-240 V AC, 50/60 Hz | 2.5 A max; 144 W out (2.5 A at 120 V) | IEC C14 inlet on the supply | [published](https://cdn.shopify.com/s/files/1/0570/4256/7355/files/Opulo_Power_Supply_Datasheet-24V_6A.pdf?v=1723229996) | 120 V |
| the OpenPnP host (a mini PC) | backed | its adapter, 100-240 V | not published; 100 W counted (0.8 A at 120 V) | - | estimate | estimate |
| Puhui T-962A reflow oven (110 V build) | unbacked | separate 110 V and 220 V builds, 50/60 Hz | 1500 W (13.6 A at 120 V) | - | [published](https://taianpuhui.en.made-in-china.com/product/GXLmWKoTvtUI/China-Desktop-Reflow-Oven-Puhui-T962A.html) | >= 12 A at 120 V: its own 20 A branch; or the 220 V build across L1-L2 (about 6.4 A, 1.3 kW) |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert PSI5-800SRT2ULIN (800 VA / 720 W)** | carries the backed rows | 120 V nominal, 75-146 V (line-interactive) | input rating 6.7 A (4.3 A at the backed rows' 514 VA/W) | NEMA 5-15P | [snippet](https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups/psi5-800srt2ulin/) | 120 V |

Legs, everything at its rating at once: **L1 13.6 A** (T-962A 13.6); **L2 6.3 A** (UPS 4.3, SPR-45VA 2.0). N about 11.8 A. With the UPS at its own input rating: L1 13.6 A, L2 8.7 A. **Within 24 A a leg**.

All 120 V, but the T-962A's 110 V build at 1500 W is 13.6 A: over 80 % of a 15 A circuit, so it needs a 20 A branch (or its 220 V build across L1-L2, about 6.4 A and 1.3 kW at 208 V).

### Tray G (2F1)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| Formlabs Form 4, x2 | unbacked | 100-240 V AC, 50/60 Hz | 4.8 A max; 480 W (9.6 A at 120 V) | - | [published](https://media.formlabs.com/m/3e4df0e3abd6c913/original/-ENUS-Form-4-Manual.pdf) | 120 V |
| Formlabs Form Wash (2nd Gen) | unbacked | 90-240 V, 50/60 Hz | 2.0 A; 50 W (2.0 A at 120 V) | - | [published](https://formlabs.com/global/products/form-wash/) | 120 V |
| Formlabs Form Cure (2nd Gen), North American unit | unbacked | 100-120 V AC, 50-60 Hz (NA); 220-240 V, 8 A (EU unit) | 15 A (NA); no total; two 450 W heaters + 150 W of UV LEDs (about 1.05 kW) (15.0 A at 120 V) | - | [published](https://media.formlabs.com/m/c401ff26124914/original/-ENUS-Form-Cure-2nd-Generation-Manual.pdf) | 15 A at 120 V: its own 20 A branch (over 80 % of a 15 A one) |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert PSI5-800SRT2ULIN (800 VA / 720 W)** | carries the backed rows | 120 V nominal, 75-146 V (line-interactive) | input rating 6.7 A (1.0 A at the backed rows' 114 VA/W) | NEMA 5-15P | [snippet](https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups/psi5-800srt2ulin/) | 120 V |

Legs, everything at its rating at once: **L1 15.0 A** (Form Cure 15.0); **L2 12.6 A** (Form 4 4.8, Form 4 4.8, Form Wash 2.0, UPS 1.0). N about 13.9 A. With the UPS at its own input rating: L1 17.0 A, L2 16.3 A. **Within 24 A a leg**.

All 120 V or universal, but the Form Cure (2nd Gen) North American unit is rated 15 A: a 20 A branch of its own (Formlabs asks for a dedicated outlet that can deliver 12 A).

### Tray I (2F2)

| Machine | Branch | Supply as published | Current / power as published (A at the dock) | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| SnowX SnowPod desktop LPBF (pre-release), x2 | unbacked | 100-240 V AC | 700 W (11.7 A at 120 V) | - | [snippet](https://makers101.com/snowpod-desktop-metal-3d-printer/) | 120 V |
| SnowX NitroPod N2 generator (pre-release) | unbacked | not found | not published; 500 W counted (4.2 A at 120 V) | - | [not_found](https://makers101.com/snowpod-desktop-metal-3d-printer/) | not found |
| 2 camera Pi 5s and the PoE+ switch | backed | 100-240 V supplies ([Pi](https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf); the switch's adapter: 100-240 V in snippets) | 27 W each, 60 W (0.9 A at 120 V) | US adapters | [published](https://techspecs.ui.com/unifi/switching/usw-lite-8-poe) | 120 V |
| **UPS: Vertiv Liebert PSI5-800SRT2ULIN (800 VA / 720 W)** | carries the backed rows | 120 V nominal, 75-146 V (line-interactive) | input rating 6.7 A (1.0 A at the backed rows' 114 VA/W) | NEMA 5-15P | [snippet](https://www.vertiv.com/en-us/products-catalog/critical-power/uninterruptible-power-supplies-ups/psi5-800srt2ulin/) | 120 V |

Legs, everything at its rating at once: **L1 10.0 A** (SnowPod 5.8, NitroPod 4.2); **L2 6.8 A** (SnowPod 5.8, UPS 1.0). N about 8.9 A. With the UPS at its own input rating: L1 10.8 A, L2 11.7 A. **Within 24 A a leg**.

The SnowPod is quoted at 700 W and 100-240 V by a third-party article (pre-release; ups.py counts 1000 W each); the NitroPod's rating wasn't found. Either way the tray is well inside the dock.

## On the floor

These are fed from the building, not through a dock. They come from `setup_lab.FLOOR_PLAN`, `r8_scale`,
`services.py`'s utilities and chargers, and the atomizer area.

| Station | Machine | Supply as published | Current / power | Plug | Source | Flag |
|---|---|---|---|---|---|---|
| vlm, vlm2 | Kardex Shuttle XP 500 vertical lift module, x2 | 208 V 3-phase 60 Hz (also 240, 480 or 600 V) | FLA 32.7 A at 208 V (35 A fuse); 28.3 A at 240 V; 14.2 A at 480 V; 8.6 kVA installed | hard-wired | [published](https://info.kardex-remstar.com/knowledge/vlm-and-vcm-power-requirements) | 208 V 3-phase: a 35 A circuit for each unit |
| repowder | AMAZEMET rePowder atomizer, its optimizer and chiller | 400 V 3-phase and 230 V; each unit comes with a 32 A plug | the optimizer up to about 60 A (AMAZEMET, install call) | 32 A plugs (or hard-wired) | [published](https://github.com/vertical-cloud-lab/byu-vcl/blob/7b333e9/rePowder-BYU-Installation-Details.txt) | 400 V 3-phase and 230 V: the install call has BYU providing both |
| glovebox | Inert PureLab HE glovebox, 2 gloves, with purifier | 110-120 V or 200-240 V, 50/60 Hz (built for the region ordered) | main breaker 15 A at 110 V (vacuum pump 10 A, blower 5 A, light 5 A) | cord and plug: needs two outlets | [published](https://www.nist.gov/document/innovative-technology-inert-purelab-glove-boxmanual) | 120 V: two outlets |
| sieve_cell | Retsch AS 200 control sieve shaker | 100-240 V, 50/60 Hz, 1-phase | not published on Retsch's page | - | [published](https://www.retsch.com/products/sieving/sieve-shakers/as-200-control/) | 120 V |
| aconity | Aconity3D AconityMIDI+ LPBF printer | 400 V 3-phase + N + PE, 50 Hz | 32 A; about 22 kVA at 32 A (computed) | - | [snippet](https://www.3dnatives.com/3d-materials/en/3d-printers/aconity-midi-plus/) | 400 V 3-phase: a transformer from 208 V (or 480 to 400 V) |
| instron_floor | Instron 68FM-100 (100 kN floor frame) | 1-phase 208-240 V (-5/+10 %, reduced load and speed ratings) or 3-phase 208, 240 or 400 V +-10 %, 47-63 Hz; 3-phase preferred | 3000 VA (1-phase, from Instron's Italian page) | - | [snippet](https://www.instron.com/wp-content/uploads/2024/06/6800-Series-Floor-Model-Universal-Testing-Machines.pdf) | 208 V 3-phase (Instron's preferred) or 208 V 1-phase at reduced ratings |
| instron_floor | Instron 3119-608 environmental chamber (to 600 C) | not found (single phase, per Instron's series page) | not published | - | [not_found](https://www.instron.com/en/products/testing-accessories/environmental-chambers-furnaces/environmental-chambers/) | not found |
| instron_small | Instron 68SC-2 (table frame) | 100, 120, 220 or 240 V +-10 %, 1-phase, 47-63 Hz | not confirmed (1400 VA appears for the family) | - | [snippet](https://www.instron.com/ko/resources/literature/6800-series-table-model-universal-testing-machines/) | 120 V |
| fumehood | Labconco Protector XStream 4 ft ducted hood | 100-115 V, 50/60 Hz (model without services); 208-230 V, 5 A (a model with services) | 10 A (a 115 V listing, not tied to this model) | cord | [snippet](https://new.marshallscientific.com/Labconco-110410000-4-Protector-XStream-Laboratory-p/110410000.htm) | 120 V |
| ded | InssTek MX-Lab DED | 1-phase 220 V, 50-60 Hz | 15 (20) A; about 3.3-4.4 kVA (computed) | - | [snippet](https://dipaul.ru/upload/iblock/c19/74xw2oocyxtfsb060f664hnz00l0ya8i.pdf) | 208/240 V 1-phase on a 20 A two-pole circuit; 208 V is 5.5 % under 220 V: ask InssTek |
| wire_edm | FANUC ROBOCUT alpha-C400iC wire EDM | 200 V +-10 % 3-phase, 50/60 Hz; 220 V +-10 % 60 Hz option | about 36 A at 208 V (computed); 13 kVA | hard-wired | [published](https://www.fanucamerica.com/uploads/files/data-sheets/ROBOCUT-C400iC-Wire-EDM.pdf) | 208 V 3-phase, directly (inside 200 V +-10 %) |
| eos_m400 | EOS M 400-4 | not stated (3-phase; 400 V likely) | 3 x 50 A; 45 kW max, 22 kW typical | hard-wired | [published](https://www.eos.info/en-us/metal-solutions/metal-printers/data-sheets/sds-eos-m-400-4) | 3-phase; voltage to confirm with EOS (a transformer if 400 V) |
| meltio_cell | Meltio Robot Cell (US build) | USA: two inputs, 230 V and 208 V 3-phase; Europe 380-415 V 3W+N+PE, 50/60 Hz | 20 kW peak, 7 kW average | one 3-phase connector | [published](https://meltio3d.com/wp-content/uploads/2026/08/Technical-datasheet_-Meltio_Robot_Cell_USA_Europe_26_08.pdf) | 208/230 V 3-phase (US build) |
| utilities | Parker Balston UHPN2-1100 N2 generator | 120 V, 60 Hz | about 5.8 A (computed); 700 W | 120 V outlet | [published](https://supplies.gmi-inc.com/product/parker-nitrogen-generator-uhpn2-1100-model-ultra-high-purity-zero-grade/) | 120 V |
| utilities | Thermo Scientific ThermoFlex 900 chiller | 115 V 60 Hz 1-phase (a 208-230 V model too) | 15 A branch circuit | NEMA 5-15P (6-15P for the 208-230 V model) | [published](https://www.nanofab.utah.edu/wp-content/uploads/2022/10/ThermoFlex-Manual.pdf) | 120 V on its own 15 A circuit |
| chargers | MiR Charge 48V, x2 | 100-240 V, 50-60 Hz | 14 A max input; 48 V out: 40 A max at 240 V, 20 A max at 120 V | standard outlet | [snippet](https://www.konicaminolta.com.au/products/robotics/mir-charge-48v) | 120 V halves the charge rate; 208/240 V for the full 40 A |
| robot | Universal Robots e-Series control box (UR10e) | AC 100-240 V (90-264 V), 47-440 Hz; DC variant 24-48 V (19-72 V) | external fuse 15-16 A at 90-200 V; 615 W max (UR10e system; snippet) | - | [published](https://www.universal-robots.com/manuals/EN/HTML/SW10_14/Content/prod_oem_polyx/oempsx_cb_all_specs_root.htm) | 120 V, or 48 V DC from the MiR's battery (the DC box) |
| repowder (area) | Nilfisk CFM 118EXP explosion-proof vacuum | 120 V, 60 Hz, 1-phase (US) | 10 A max; 1000 W (1200 W in another Nilfisk document) | - | [snippet](https://manualmachine.com/nilfisk/118/10136940-brochure/) | 120 V on its own 15 A circuit |
| packaging | Packaging station: Uline H-190 impulse sealer, Primera LX500c and AP380, Zebra ZD621t | H-190: 120 V; LX500c and ZD621t: 100-240 V, 50/60 Hz; AP380: not found (its siblings AP360/AP362: 100-240 V) | H-190: 580 W impulse (an older Uline table says 380 W); LX500c: 60 W | - | [snippet](https://www.uline.com/product/detail/H-190) | 120 V |

## What this means for the dock

1. **The dock can stay as it is.** 208Y/120 V on L1, L2, N and PE at 30 A carries every tray once trays D and F
   are changed as in items 3 and 4. No tray needs three-phase or more than 30 A a leg, so an L3 contact or a bigger
   contact set would buy nothing.
2. **Each tray's distribution box needs its own branch breakers,** not a power strip. It is fed by a two-pole 30 A
   breaker, and a 30 A circuit may only feed 30 A receptacles. In practice that means a small load centre on each
   tray with four to six branches:
   - a two-pole 20 A branch with a NEMA 6-20R for each 208 V machine;
   - a 20 A branch for each machine drawing 12 A or more at 120 V;
   - 15 or 20 A branches for the UPS and the rest, split between L1 and L2 as in the tables above.
3. **Tray D: replace the single 120 V GXT5LI-3000.** Its L5-30P takes a whole leg at 24 A, the continuous limit,
   and leaves the other leg empty. Two ways round it:
   - **Two 120 V units on opposite legs.** A GXT5LI-2000LVRT2UXL (2000 VA / 1800 W, 16 A in; Vertiv's guide
     specification) for the MiniFlex and its PC, and a GXT5LI-1500 (12 A) for the SEM, its PC, the EDS, the cameras
     and the switch. That gives about 12-16 A on one leg and 11 A on the other. It keeps every tray on Vertiv's
     family and its one network card. The GXT5LI-2000's input plug wasn't confirmed (its outlets include an
     L5-20R).
   - **One 208 V unit across L1-L2,** such as Eaton's 9PX3000GRT-L (3 kVA / 2.7 kW, LiFePO4, L6-20P in, 8 C13 and
     2 C19 out; [Eaton](https://www.eaton.com/us/en-us/skuPage.9PX3000GRT-L.html), search snippet). That gives
     about 13-16 A on each leg. Every machine on tray D takes 100-240 V, so all of them can run from its 208 V
     outlets. It is 605 mm deep, against the GXT5LI-3000's 546 mm.

   Either needs a fit check on the tray (`setup_lab.py fit`).
4. **Tray F:**
   - **Order the furnace wound for 208 V,** and ask LECO whether the PX500A2 runs on 208 V. A 240 V furnace run on
     208 V gives only 75 % of its power. Each goes on a two-pole 20 A branch.
   - **Then either** keep ups.md's rule that the furnace and the MX400 don't heat at the same time (18 A a leg), or
     buy the MX400's 230 V model (MX400382, 5 A) so all three heavy machines sit across L1-L2. With everything on,
     that is about 23 A a leg at the furnace's 2.8 kW, and 25 A at the 3.3 kW of the older catalogue.
5. **Trays C, G and H:**
   - a 20 A branch each for the H2D, the Form Cure and the T-962A;
   - on tray G, the Form Cure goes on the other leg from the two Form 4s;
   - on tray H, the alternative is the T-962A's 220 V build across L1-L2 (about 6.4 A).
6. **Set switch-selected inputs to 115 V before first power-up,** since 208 V on a 115 V setting destroys a supply:
   - the CubXL's Genmitsu supply;
   - the doser's LRS-350;
   - both RV3 pumps (or buy the A652-01-906, which ships set to 115 V);
   - check the Carvera for a selector.
7. **The neutral.** With both legs loaded, N carries about as much as a leg. As tray D is specified, all of its 24-28 A
   comes back on N. The tray's N conductor has to be full size; the 39 A contact is enough.
8. **The floor needs its own supplies:**
   - a three-phase 208Y/120 V panel for the two Kardex units (35 A each), the wire EDM (13 kVA, about 36 A), the
     Instron 68FM-100 and the Meltio cell;
   - 400 V for the Aconity: a 208-to-400 V step-up transformer, or 480-to-400 V if the building has 480 V. The
     rePowder's install call has BYU providing 400 V and 230 V for it already;
   - EOS has to give the M 400-4's voltage: 3 x 50 A at 400 V is only 35 kVA against its 45 kW maximum;
   - the MX-Lab on a two-pole 208 or 240 V circuit sized for its 15 (20) A, once InssTek confirms 208 V (5.5 %
     under its 220 V);
   - a 208 or 240 V outlet for each MiR charger if they should charge at full rate. At 120 V a charger gives 20 A
     out, against 40 A at 240 V.

## Not found, and what to ask for

Read these off the nameplates when the machines arrive, or ask the makers:

- **NuVant EZstat Pro:** its external supply's rating. nuvant.com gives only the supply's size.
- **Plastometrex PLX-Benchtop and KLA iMicro:** no electrical data at all on their pages. KLA's PDF wouldn't load.
- **Malvern:**
  - the Mastersizer 3000's draw: only "100/240 V, 50/60 Hz" is published;
  - the Aero S vacuum extractor's model and rating: 1200 W in ups.py is an estimate, and with 10 A it is the
    largest unknown on tray E.
- **Power figures not published:**
  - the Specac Autotouch's (the US model is 110 V, 60 Hz);
  - the LECO PX500's (740 W is a snippet).
- **Bruker:** the S2 PUMA's optional vacuum pump.
- **SnowX:** the NitroPod, and the SnowPod beyond a third-party "700 W, 100-240 V".
- **Hitachi:** the TM4000's PC ("another power source for PC is required").
- **Instron:** the 3119-608 chamber's supply, the 68FM-100's current, and the 68SC-2's VA (Instron's
  preinstallation manuals have them).
- **AMAZEMET and Aconity3D:** published supply data, beyond the install call and a third-party listing.
- **Primera:** the AP380 label applicator's supply.

## Where this differs from ups.TRAY_LOADS

ups.py is unchanged; these are for its next pass:

- **Rigaku:**
  - the MiniFlex is 1.1 kVA as the 600-C, with its chiller inside, and that matches ups.py;
  - Rigaku budgets **0.7 kVA** for its PC, against ups.py's 200 W. At 0.7 kVA tray D's backed rows reach 3.0 kVA,
    the GXT5LI-3000's whole rating.
- **Formlabs:** the Form Cure (2nd Gen) is rated **15 A** in North America. The 7 A in ups.md belongs to another
  product, the Form Studio Wash+Cure. ups.py's 1800 W (15 A x 120 V) stands; its heaters and LEDs add to about
  1.05 kW.
- **Ratings in VA, not W:** Teledyne gives 20 VA, ZwickRoell 500 VA.
- **Smaller than ups.py counts:**
  - Mitutoyo gives **39 VA** for the HM-220's main unit (ups.py: 90 W, no source found);
  - Makera gives **400 W** for the Carvera (ups.py: 430 W);
  - the SnowPod is quoted at **700 W** (ups.py: 1000 W each).

# Twin round 6: the used-equipment market

Issue [#424](https://github.com/vertical-cloud-lab/byu-vcl/issues/424). Round 5's twin
(`vertical-lab/twin/round5.py` at `4bb91b1`, PR 405) buys a station used when `USED_OK` names it, with one set of
stand-ins for every such station (`USED`: it ships 2 weeks after BYU's purchase order, costs 45 % of new, 1 in 4
arrives faulty or needs refurbishment, which takes 6 weeks and 15 % of the new price, and commissioning takes a week
longer). This folder replaces those stand-ins with what was actually for sale on 27 November 2026, for every station
and instrument either lab buys in the twin (`twin/econ.py`'s `_vertical()` and `_conventional()`), not only the ones in
`USED_OK`.

**Round 6 reads [`summary.csv`](summary.csv)** (one row per twin key, plus one per component where a station is
several machines), or the same through `twin/market6.py`:

```python
from twin import market6
m = market6.load()            # key -> dict: used_ok, lead_w, lead_sigma, price_frac, p_fault, refurb_w,
                              #             refurb_sigma, refurb_frac, extra_com_w, market, n_listings, ...
```

`python3 -m twin.market6` rebuilds `summary.csv` and `summary.json` from `listings.csv` and `new.csv`.

<!-- tables:start -->
## Results by station

Round 5's stand-ins, for comparison: `price_frac` 0.45, `lead_w` 2, `p_fault` 0.25, `refurb_w` 6, `refurb_frac` 0.15, `extra_com_w` 1. **Market**: *yes* = at least 5 listings that fit, 2 of them in North America, one priced; *thin* = fewer; *none* = nothing found. Prices are asking prices in USD; *like-for-like* is the median over the twin's own model and its maker's line only. `price_frac` is the median used price plus freight and rigging, over the twin's new price.

| Key | Lab | In `USED_OK` | Market | Listings (N. America) | Priced | Median used, all | Priced on | Discount vs new | `price_frac` | `lead_w` | `p_fault` (best) | `extra_com_w` | Order to working, used / new (weeks) |
| --- | --- | :-: | --- | --: | --: | --: | --- | --: | --: | --: | --: | --: | --: |
| `sem` | vertical | yes | yes | 17 (8) | 8 | $16k | like-for-like (4 priced): $15k | 85 % | 0.20 | 3.0 | 0.14 (0.05) | 1.5 | 9.4 / 12.0 |
| `eds` | vertical |  | thin | 1 (1) | 1 | $1,007 | all that fit (1 priced): $1,007 | 98 % | 0.05 | 2.5 | 0.30 (0.30) | 1.5 | 8.8 / 11.0 |
| `ebsd` | vertical |  | thin | 2 (1) | 1 | $2,804 | all that fit (1 priced): $2,804 | 98 % | 0.04 | 5.0 | 0.30 (0.30) | 1.5 | 13.3 / 19.0 |
| `xrd` | vertical | yes | yes | 5 (4) | 1 | $24k | all that fit (1 priced): $24k | 78 % | 0.24 | 2.5 | 0.35 (0.30) | 1.5 | 10.1 / 12.0 |
| `xrf` | vertical | yes | yes | 14 (5) | 9 | $16k | North America (3 priced): $12k | 90 % | 0.12 | 2.5 | 0.34 (0.30) | 1.5 | 13.0 / 17.0 |
| `mastersizer` | vertical | yes | yes | 66 (24) | 15 | $15k | like-for-like (7 priced): $17k | 84 % | 0.21 | 2.5 | 0.25 (0.10) | 1.5 | 9.5 / 12.0 |
| `hardness` | vertical | yes | yes | 28 (13) | 14 | $6,113 | North America (8 priced): $11k | 85 % | 0.16 | 2.0 | 0.27 (0.10) | 0.5 | 6.3 / 9.0 |
| `nanoindenter` | vertical | yes | thin | 3 (3) | 2 | $23k | all that fit (2 priced): $23k | 91 % | 0.10 | 2.5 | 0.30 (0.30) | 1.5 | 10.8 / 19.0 |
| `pip` | vertical |  | none | 0 (0) | 0 |  |  |  |  |  |  | 0.5 | – / 13.0 |
| `vhx` | vertical | yes | yes (microscope) | 21 (6) | 12 |  | components (below) | 30 % | 0.70 | 2.0 | 0.33 | 0.5 | 6.5 / 7.0 |
| `polish` | vertical | yes | yes (polisher, saw) | 32 (10) | 18 |  | components (below) | 49 % | 0.51 | 2.0 | 0.42 | 0.5 | 7.2 / 10.0 |
| `furnaces` | vertical | yes | yes | 69 (24) | 21 | $3,950 | North America (9 priced): $2,500 | 88 % | 0.17 | 2.0 | 0.30 (0.10) | 0.5 | 6.4 / 9.0 |
| `sieve_cell` | vertical |  | yes (shaker) | 37 (17) | 18 |  | components (below) | 4 % | 0.96 | 2.0 | 0.28 | 0.5 | 8.4 / 15.0 |
| `doser` | vertical |  | yes (press, pump) | 63 (19) | 37 |  | components (below) | 67 % | 0.33 | 2.0 | 0.46 | 0.5 | 9.4 / 20.0 |
| `glovebox` | vertical |  | yes | 15 (4) | 9 | $21k | North America (3 priced): $21k | 62 % | 0.44 | 2.5 | 0.28 (0.30) | 1.0 | 8.6 / 14.0 |
| `hoods` | vertical |  | yes (hood) | 13 (9) | 7 |  | components (below) | 25 % | 0.75 | 2.5 | 0.32 | 1.0 | 7.8 / 11.0 |
| `icpms` | vertical | yes | yes (instrument) | 96 (42) | 34 |  | components (below) | 41 % | 0.59 | 2.5 | 0.28 | 2.0 | 12.7 / 18.0 |
| `instron` | vertical | yes | yes | 65 (28) | 35 | $12k | like-for-like in North America (4 priced): $12k | 93 % | 0.10 | 3.0 | 0.30 (0.20) | 1.5 | 12.3 / 20.0 |
| `chamber` | vertical | yes | thin | 2 (1) | 1 | $9,650 | all that fit (1 priced): $9,650 | 81 % | 0.21 | 2.5 | 0.20 (0.10) | 0.5 | 6.6 / 17.0 |
| `zwick` | vertical | yes | yes | 32 (2) | 17 | $29k | like-for-like (15 priced): $29k | 17 % | 0.90 | 2.0 | 0.30 (0.30) | 0.5 | 7.4 / 12.0 |
| `edm` | vertical | yes | yes | 118 (51) | 35 | $27k | like-for-like (16 priced): $24k | 89 % | 0.20 | 3.0 | 0.31 (0.20) | 2.0 | 13.8 / 23.0 |
| `machining` | vertical |  | yes (lathe, bar_feeder) | 113 (41) | 36 |  | components (below) | 6 % | 0.94 | 3.0 | 0.54 | 2.0 | 15.1 / 28.0 |
| `carvera` | vertical |  | none | 0 (0) | 0 |  |  |  |  |  |  | 0.5 | – / 3.0 |
| `units` | vertical |  | yes (mir) | 54 (18) | 29 |  | components (below) | 18 % | 0.82 | 2.0 | 0.30 | 1.0 | 11.2 / 19.0 |
| `floor_unit` | vertical |  | yes (mir) | 56 (20) | 30 |  | components (below) | 16 % | 0.83 | 2.0 | 0.30 | 1.0 | 9.2 / 17.0 |
| `shuttle` | vertical |  | thin | 26 (1) | 11 | $14k | like-for-like (11 priced): $14k | 93 % | 0.40 | 9.0 | 0.25 (0.10) | 2.0 | 18.5 / 18.0 |
| `couplings` | vertical |  | none | 0 (0) | 0 |  |  |  |  |  |  | 0.0 | – / 10.0 |
| `midi` | vertical |  | thin | 44 (0) | 15 | $67k | all that fit (15 priced): $67k | 90 % | 0.13 | 8.0 | 0.23 (0.10) | 6.0 | 25.4 / 26.0 |
| `mxlab` | vertical |  | none | 0 (0) | 0 |  |  |  |  |  |  | 6.0 | – / 34.0 |
| `repowder` | both |  | none | 0 (0) | 0 |  |  |  |  |  |  | 2.0 |  |
| `ups` | vertical |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 0.0 | – / 6.0 |
| `cameras` | vertical |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 0.0 | – / 4.0 |
| `services` | vertical |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 1.0 | – / 18.0 |
| `sieve` | conventional |  | yes | 37 (17) | 18 | $2,812 | like-for-like in North America (4 priced): $4,175 | 48 % | 0.57 | 2.0 | 0.28 (0.05) | 0.5 | 5.4 /  |
| `doser_conv` | conventional |  | thin | 36 (10) | 19 |  |  |  |  |  |  |  |  |
| `furnace` | conventional |  | yes | 69 (24) | 21 | $3,950 | North America (9 priced): $2,500 | 92 % | 0.11 | 2.0 | 0.30 (0.10) | 0.5 | 5.4 /  |
| `density` | conventional |  | yes | 17 (4) | 15 | $2,000 | North America (3 priced): $2,395 | 80 % | 0.24 | 3.0 | 0.20 (0.10) | 0.5 | 6.1 /  |
| `glovebox_conv` | conventional |  | yes | 15 (4) | 9 | $21k | North America (3 priced): $21k | 62 % | 0.44 | 2.5 | 0.28 (0.30) | 1.0 | 6.6 /  |
| `hood` | conventional |  | yes (hood) | 13 (9) | 7 |  | components (below) | 25 % | 0.75 | 2.5 | 0.32 | 1.0 | 6.8 /  |
| `cubxl` | conventional |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 0.5 |  |

### Stations that are several machines

| Key | Component | New (each) | Market | Listings (N. America) | Priced | Median used | `price_frac` |
| --- | --- | --: | --- | --: | --: | --: | --: |
| `vhx` | libs | $95k | none | 0 (0) | 0 |  |  |  |
| `vhx` | microscope | $95k | yes | 21 (6) | 12 | like-for-like (9 priced): $36k | 0.40 | 2.0 |
| `polish` | polisher | $23k | yes | 12 (4) | 5 | all that fit (5 priced): $2,638 | 0.14 | 2.0 |
| `polish` | press | $19k | thin | 8 (0) | 6 | all that fit (6 priced): $2,694 | 0.24 | 7.0 |
| `polish` | saw | $13k | yes | 12 (6) | 7 | North America (4 priced): $5,250 | 0.45 | 2.0 |
| `sieve_cell` | rest | $53k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `sieve_cell` | shaker | $6,700 | yes | 37 (17) | 18 | like-for-like in North America (4 priced): $4,175 | 0.69 | 2.0 |
| `doser` | balance | $3,500 | thin | 17 (1) | 11 | all that fit (11 priced): $1,500 | 0.57 | 2.0 |
| `doser` | carousel | $2,362 | n/a (new only) | 0 (0) | 0 |  |  |  |
| `doser` | press | $41k | yes | 19 (9) | 8 | like-for-like (3 priced): $6,561 | 0.22 | 2.0 |
| `doser` | pump | $3,000 | yes | 27 (9) | 18 | like-for-like in North America (6 priced): $1,225 | 0.57 | 2.0 |
| `hoods` | hood | $14k | yes | 13 (9) | 7 | like-for-like (3 priced): $3,500 | 0.37 | 2.5 |
| `hoods` | install | $21k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `icpms` | autosampler | $12k | yes | 13 (5) | 5 | like-for-like (4 priced): $91k | 7.46 | 3.0 |
| `icpms` | instrument | $190k | yes | 83 (37) | 29 | like-for-like in North America (8 priced): $78k | 0.43 | 2.5 |
| `icpms` | rest | $58k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `machining` | bar_feeder | $16k | yes | 5 (5) | 1 | all that fit (1 priced): $6,500 | 0.47 | 2.0 |
| `machining` | lathe | $65k | yes | 65 (21) | 11 | like-for-like (8 priced): $35k | 0.87 | 3.0 |
| `machining` | rest | $142k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `machining` | robot_arm | $52k | yes | 43 (15) | 24 | like-for-like in North America (7 priced): $51k | 1.00 | 2.0 |
| `units` | arm | $45k | yes | 43 (15) | 24 | like-for-like in North America (7 priced): $51k | 1.15 | 2.0 |
| `units` | gripper | $5,500 | thin | 2 (0) | 0 |  |  | 7.0 |
| `units` | mir | $62k | yes | 9 (3) | 5 | like-for-like (4 priced): $33k | 0.59 | 2.0 |
| `units` | rest | $28k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `floor_unit` | arm | $45k | yes | 43 (15) | 24 | like-for-like in North America (7 priced): $51k | 1.15 | 2.0 |
| `floor_unit` | gripper | $5,500 | thin | 2 (0) | 0 |  |  | 7.0 |
| `floor_unit` | mir | $62k | yes | 9 (3) | 5 | like-for-like (4 priced): $33k | 0.59 | 2.0 |
| `floor_unit` | rest | $30k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `floor_unit` | vacuum | $12k | thin | 2 (2) | 1 | all that fit (1 priced): $8,045 | 0.74 | 2.5 |
| `doser_conv` | balance | $4,000 | thin | 17 (1) | 11 | all that fit (11 priced): $1,500 | 0.50 | 2.0 |
| `doser_conv` | doser | $5,000 | n/a (new only) | 0 (0) | 0 |  |  |  |
| `doser_conv` | press | $9,000 | yes | 19 (9) | 8 | like-for-like (3 priced): $6,561 | 1.01 | 2.0 |
| `hood` | hood | $14k | yes | 13 (9) | 7 | like-for-like (3 priced): $3,500 | 0.37 | 2.5 |
| `hood` | install | $21k | n/a (new only) | 0 (0) | 0 |  |  |  |

## New price and the vendor's stated lead time

Most instrument makers quote lead times only on request; the leads below are the ones a vendor or distributor publishes. The twin's lead (round 4's `BUILD`, including BYU's 2-week purchase order) is assumed for every item but the room.

| Key | Item | New, each | Vendor's stated lead | Twin's lead (weeks) |
| --- | --- | --: | --- | --: |
| `sem` | Hitachi TM4000PlusII benchtop SEM | $100k | quote only (no lead published) | 10 |
| `furnaces` | Nabertherm NAT 15/65 forced-convection furnace | $20k | quote only (Fisher UK's last estimated ship date is in 2024) ([source](https://www.fishersci.co.uk/shop/products/forced-convection-chamber-furnace-na-15-65-5/p-7236198)) | 8 |
| `sieve_cell` | Retsch AS 200 sieve shaker with sieves | $6,700 | estimated shipment 4 to 6 weeks (Certified MTP, US) ([source](https://certifiedmtp.com/retsch-as-200-basic-sieve-shaker)) | 12 |
| `hoods` | Labconco Protector XStream 6 ft ducted hood | $14k | an 8 ft Protector XStream ships in 7-14 days (Calpac); 6 ft 'call for lead time' (GovSci) ([source](https://www.calpaclab.com/8-protector-xstream-laboratory-hood-100-115v-50-60hz-custom-options-available/lc-110810000)) | 10 |
| `edm` | FANUC ROBOCUT wire EDM | $230k | quote only ('contact a ROBOCUT application expert') ([source](https://www.fanucamerica.com/products/robocut)) | 18 |
| `machining` | Haas ST-10 turning centre | $65k | 16 available; 1 week, built to order (haascnc.com ST-10 page, read 2026-11-27) ([source](https://www.haascnc.com/machines/lathes/st/models/standard/st-10.html)) | 22 |
| `machining` | UR10e / UR12e on a pedestal | $52k | about 7 days (Funduinoshop, EU); non-stock e-Series 'usually ships in 4 weeks' (Motion World, US) ([source](https://funduinoshop.com/en/robotics/universal-robots/ur12e/universal-robots-ur12e)) | 22 |
| `carvera` | Makera Carvera desktop CNC | $5,799 | in stock in the US warehouse, ships within 7 business days (makera.com, read 2026-11-27) ([source](https://www.makera.com/products/carvera)) | 3 |
| `units` | UR12e cobot arm | $45k | about 7 days (Funduinoshop, EU); non-stock 4 weeks (Motion World, US) ([source](https://vention.io/parts/universal-robots-ur12e-collaborative-robot-arm-3443)) | 14 |
| `floor_unit` | UR12e cobot arm | $45k | as the units' | 14 |
| `shuttle` | Kardex Shuttle XP 500, 9.15 m, 2450 x 864 mm trays | $210k | Kardex QuickShip 4-6 weeks for standard sizes, custom longer (PR 331) ([source](https://www.kardex.com/en-us/blog/how-much-does-a-vertical-lift-module-cost)) | 14 |
| `midi` | Aconity3D AconityMIDI+ LPBF | $700k | quote only (lead not found) | 18 |
| `mxlab` | InssTek MX-Lab blown-powder DED | $300k | quote only (lead not found) | 26 |
| `sieve` | Retsch AS 200 sieve shaker and a set of sieves | $8,000 | estimated shipment 4 to 6 weeks (Certified MTP, US) ([source](https://certifiedmtp.com/retsch-as-200-basic-sieve-shaker)) |  |

## Sources

| Source | Kind | Access | Pages read | Listings kept |
| --- | --- | --- | --: | --: |
| [eBay](https://www.ebay.com/) | marketplace (active and sold) | blocked | 2 |  |
| [BidSpotter](https://www.bidspotter.com/) | auction aggregator | challenged | 1 |  |
| [EquipNet](https://www.equipnet.com/) | auction and dealer | challenged | 2 |  |
| [Surplus Record](https://www.surplusrecord.com/) | machinery listings | challenged | 1 |  |
| [LabX](https://www.labx.com/) | lab-equipment marketplace (dealers) | ok | 110 | 234 |
| [Machinio](https://www.machinio.com/) | machinery and equipment aggregator (dealers) | ok | 88 | 390 |
| [GovDeals](https://www.govdeals.com/) | government and university surplus auctions | ok | 54 | 11 |
| [AllSurplus](https://www.allsurplus.com/) | commercial surplus auctions (same platform as GovDeals) | ok | 69 | 40 |
| [Public Surplus](https://www.publicsurplus.com/) | government and university surplus auctions | ok | 42 | 2 |
| [Federal Equipment Company](https://www.fedequip.com/) | used-equipment dealer | ok | 8 |  |
| [BioSurplus](https://www.biosurplus.com/) | used lab-equipment dealer | ok | 3 |  |
| [Machineseeker](https://www.machineseeker.com/) | machinery marketplace (dealers and auctions, mostly Europe) | ok | 116 | 195 |
| [Exapro](https://www.exapro.com/) | used-machinery broker (Europe) | ok | 74 | 88 |
| [DOTmed](https://www.dotmed.com/) | medical and lab equipment marketplace | ok | 34 | 15 |
| [Marshall Scientific](https://www.marshallscientific.com/) | used lab-equipment dealer and refurbisher | ok | 36 | 5 |
| [Conquer Scientific](https://conquerscientific.com/) | used and refurbished analytical instruments dealer | ok | 15 | 5 |
| [GMI (re-certified equipment)](https://www.gmi-inc.com/) | refurbisher of analytical instruments | ok | 7 |  |
| [Robots Done Right](https://robotsdoneright.com/) | used industrial robot dealer | ok | 8 |  |
| [SEMTech Solutions](https://www.semtechsolutions.com/) | SEM refurbisher | ok | 9 | 12 |
| [Haas Automation](https://www.haascnc.com/) | maker (new price and stated lead) | ok | 1 |  |
| [Makera](https://www.makera.com/) | maker (new price and stated lead) | ok | 1 |  |
| [GSA Advantage](https://www.gsaadvantage.gov/) | federal catalogue (looked for stated delivery days) | ok | 3 |  |

<!-- tables:end -->

## Files

| File | What it is |
| --- | --- |
| [`listings.csv`](listings.csv) | One row per listing seen that fits a station's role: station key, component, how close a match (`exact` model, same maker's `family`, or a `sub`stitute that does the same job), title, source, URL, price as listed and in USD, price kind (asking, starting bid, current bid, on request), condition (as-is, used, tested, refurbished, warranty, new surplus), the words the condition was read from, location and region, distance where the site gives one, seller type and name, stated availability, delivery terms, weight, a freight and rigging estimate, date seen. Rows with `keep = 0` are kept for the record (duplicates of a unit listed twice, new equipment advertised on LabX, rows dropped on review) with the reason. |
| [`summary.csv`](summary.csv) | Per station key, in the twin's units: listings found (and how many in North America, priced, exact, family, substitute), the median used price and its quartiles, the like-for-like median (exact and family only), the discount against new, freight and rigging, `price_frac` (median delivered used price over the twin's new price), `lead_w` and `lead_sigma`, `p_fault`, `refurb_w`, `refurb_frac`, `extra_com_w`, the condition mix, whether a real used market exists, and `used_ok`. |
| [`summary.json`](summary.json) | The same, with every assumption the summary used and its source. |
| [`new.csv`](new.csv) | Each item's new price (the twin's, with its source) and the vendor's stated lead time where one is published, with the page it came from. |
| [`sources.csv`](sources.csv) | Every source tried, whether it could be read, and how many pages and listings it gave. |
| [`visits.csv`](visits.csv) | Every page the browsers opened: time, URL, HTTP status, and whether it was a challenge or block page. |
| [`shots/`](shots/) | Screenshots of representative listings. |
| [`tools/`](tools/) | The scripts: the browser rig and pacing (`browse.py`, `chrome.sh`, `chrome_n.sh`), the search plans and crawler (`plan1.json`, `plan2.json`, `crawl.py`), the matching rules (`stations.py`), the card and page parsers (`parse.py`, `detail.py`, `build_listings.py`) and the report (`report.py`). |

## How the pages were read

**Through the lab Pi, in a headed browser.** Google Chrome 158, headed, on virtual displays (Xvfb) on the CI runner,
with all of its traffic sent out through the CubXL Pi over an SSH SOCKS tunnel, so that sites saw the lab's network
(AS6510, Brigham Young University, Utah) rather than a datacenter. This is the rig CLAUDE.md describes for Onshape
(`rig.sh` at byu-vcl `49677cf`). Chrome was not run on the Pi itself: that Pi has 1 GB of RAM and runs a live camera
service. Nothing was installed or written on the Pi; it only relayed traffic.

**At a person's pace.** Every page was preceded by a pause of 4-9 s (6-12 s for listing pages), then read with mouse
moves along eased, slightly curved paths with jitter, and uneven wheel scrolls, before its contents were read. Each
group of sites had a browser of its own, and each site was only ever open in one browser at a time, so no site saw
more than one page every 20 s or so. (Chrome throttles hidden tabs so hard that a second tab stalls, which is why the
groups were given separate browsers on separate virtual displays rather than tabs.)

**Public pages only.** No log-in, bid, purchase, quote request or message. Prices behind "request a price" were left
unrequested. Every page was checked for a challenge or block page (Cloudflare, CAPTCHA, "confirm you are human", an
HTTP 403 block page). A site that challenged or blocked the browser was recorded and left alone: not solved, not
retried from another address, not reached another way.

**Searches.** 181 queries over 10 sites (`tools/plan1.json`, `tools/plan2.json`): model names (the twin's own model
and its maker's other generations) and the generic name of the instrument, on the sites where each kind of equipment
is sold. Every listing card on every results page was kept (`search.jsonl`, not committed: it holds page text), and
matched against each station's rules (`tools/stations.py`): the twin's own model (`exact`), the same maker's line
(`family`), or another maker's instrument that does the station's job (`sub`), with parts, accessories, consumables and
things that only share a word left out. Then each listing that matched was opened, up to 30 per station and
component, for its condition, location, seller, price, availability, delivery terms and weight.

**Tray stations take benchtop instruments only.** The automated lab's SEM, XRD and XRF ride on trays, so a floor-standing
SEM, diffractometer or WDXRF can't stand in for them. Those listings are kept as `sem_floor`, `xrd_floor` and
`xrf_floor` (a conventional lab could use one) and left out of the tray stations' statistics.

**Prices.** Asking prices as listed, converted at the ECB's euro reference rates of 17 November 2026 (USD 1.0989, GBP
0.83305, CHF 0.9233 per euro, and so on; `tools/build_listings.py`). A current bid on a running auction is recorded
but left out of the price statistics, because it is not what the unit will sell for. eBay's sold listings, the usual
source of transaction prices, could not be read (eBay blocked the browser), so these are asking prices, which run
above what units sell for.

## From listings to the twin's numbers

`twin/market6.py` turns `listings.csv` and `new.csv` into `summary.csv`. What is measured and what is assumed:

* **Measured:** the number of listings that fit, where they are, the asking prices, the like-for-like prices, the mix
  of conditions, stated availability and delivery terms, and whether a real market exists (at least 5 listings that
  fit, at least 2 of them in North America, at least one priced).
* **Assumed** (each constant is in `market6.py` with its source, and in `summary.json`):
  * freight and rigging by shipping class and region (`FREIGHT`), anchored on LTL rates and machine-moving guides;
  * the lead from purchase order to the unit on site (`LEAD`): the seller's handling (a week for a dealer, two for a
    refurbisher or an auction's close and removal window), transit (a week across the US, six from overseas) and
    booking riggers;
  * extra commissioning for a used unit (`EXTRA_COM`): half a week for a bench tool, 1.5-2 weeks for vacuum and X-ray
    instruments and machines, 6 weeks for an LPBF or DED machine's recommissioning and requalification by its maker;
  * the chance a unit arrives faulty or needs refurbishment, by condition (`P_FAULT`: 1 in 20 refurbished with a
    warranty, 1 in 10 refurbished or warranted, 1 in 5 tested, 3 in 10 "used" with nothing said, 1 in 2 as-is). The
    mix of conditions is measured; these rates are not: no failure-rate data for used lab equipment was found. `p_fault`
    is the market's mix; `p_fault_best` is the lowest-risk listing in North America at no more than 1.5 times the
    median price, what a lab that shops for condition could get;
  * refurbishment time and cost if it is faulty (`REFURB`), by class, replaced by the listings' own difference
    between refurbished and as-is or used prices where both have at least two priced listings.

A station that is several machines (the machining cell, the robot units, prep and polishing, the doser, the ICP-MS
station, the VHX with its LIBS head, the hoods) is summarized per component, and then as a station: components with a
real used market are bought used at their delivered median, the rest new. Its lead and risks are those of its used
components, and a component bought new can still set the station's lead.

## Caveats

* **Asking prices, not sale prices.** eBay's sold listings were not readable; Public Surplus and GovDeals show only
  running auctions. Dealers' asking prices are an upper bound on what a unit sells for.
* **Many prices are on request.** Machine-tool and instrument dealers often don't publish a price. Those listings
  count towards whether a market exists and towards the condition mix, not towards the price.
* **Europe is over-represented for machines.** Machineseeker and Exapro list far more used wire EDMs, LPBF machines,
  Kardex Shuttles and UR cobots than the US sites read here. A European machine needs export crating, ocean freight
  and customs (in `FREIGHT` and `LEAD`), and may need a 400 V/50 Hz to 480 V/60 Hz transformer and UL or NFPA 79
  re-certification, which isn't priced here.
* **Condition is what the seller says.** "Tested" and "fully functional" are the seller's words; government and
  university surplus auctions sell as-is, where-is.
* **Matching is by rules, then by eye.** `stations.py` decides what fits a station; every station's list was then read
  through and rows that slipped through were dropped with a reason. Some judgment calls remain (how old a wire EDM may
  be, whether an older generation of benchtop SEM does the job).
* **A used unit must also be the right size.** A Kardex Shuttle has to fit the room's height and the twin's tray size;
  a used one usually needs its frame cut down or extended by Kardex. That is priced as relocation, not as a rebuild.
* **One day's snapshot.** Listings come and go; a thin market can be empty next month.

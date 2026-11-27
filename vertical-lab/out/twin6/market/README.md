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
m = market6.load()                    # key -> the station's row of summary.csv (used_ok, lead_w, price_frac, ...)
p = market6.used_params("edm", m)     # round 5's USED for one station: lead_w, lead_sigma, price_frac, p_fault,
                                      # refurb_w, refurb_sigma, refurb_frac, extra_com_w; ok = buy used at all;
                                      # fallback = the values the market didn't give (round 5's stand-in kept)
```

So round 6 can replace `USED_OK` with the keys whose `used_ok` is true and `USED` with `used_params(key)` per
station; `used_rule` then decides, as in round 5, whether buying used saves enough days. `python3 -m twin.market6`
rebuilds `summary.csv` and `summary.json` from `listings.csv` and `new.csv`.

## In short

<!-- inshort:start -->
* **Most instruments and lab tools have a real used market in North America, at a fraction of the twin's new
  prices.** Benchtop SEMs, XRF, laser diffraction, micro-Vickers, the Keyence microscope, prep machines, furnaces, sieve
  shakers, gloveboxes, fume hoods, ICP-MS, tensile frames and wire EDMs all had several listings that fit, most of them
  priced. Delivered (asking price plus freight and rigging), the median `price_frac` across the stations with a real
  market is 0.31 (round 5 assumed 0.45 for every station), from 0.12 to 0.95. The twin's own models are dearer than
  that median: an Agilent 7800 or 7850 ICP-MS is $67-100k refurbished with a warranty against about $190k new, a 2014
  Haas ST-10 $24,900 against $64,995 new, a 2021-2024 FANUC ROBOCUT α-C400iC about €89,000 in Europe against $230k.
* **The automation and the printers are a different story.** No used Plastometrex PIP, AMAZEMET rePowder, InssTek
  MX-Lab or Aconity MIDI was listed anywhere. Used LPBF machines are common (EOS M 270/280/290, SLM 125/280, Concept
  Laser M2 and Mlab, TruPrint 1000; 82 listings, 11 in North America), but none is the twin's open research
  machine, and each needs its maker's recommissioning and a licence transfer, so `midi` is priced on like-for-like
  listings only and stays new. Kardex Shuttle XP 500s are plentiful in Europe, almost absent in the US, and their prices
  are on request; `shuttle` stays new too. UR cobot arms and MiR AMRs do have a market (35 UR arms and 9 MiRs
  listed), which makes the robot units part-used.
* **Used saves little time where new is quick.** The Haas ST-10 is in stock new (16 available, one week), the Carvera
  ships in seven business days and UR cobots in one to four weeks. Where the twin's new leads are long (8-16 weeks for
  instruments, 18 for the EDM), a domestic used unit is on site about 2.5 weeks after the purchase order, and working
  4.3 weeks sooner than new (median over the stations with a real market; `order_to_working_used_w` against
  `order_to_working_new_w`, before the facility window).
* **The fault risk is about round 5's.** With the listings' mix of conditions, `p_fault` has a median of 0.28 (round 5:
  0.25): lower where refurbished units with a warranty are common (SEM, ICP-MS), higher at government and university
  auctions (sold as-is) and for stations bought as several used machines (prep, the doser, the robot units), any one of
  which can arrive faulty. A lab that buys the best-condition unit near the median price gets 0.10 (`p_fault_best`).
* **`USED_OK` changes.** The market doesn't support `chamber`, `nanoindenter` (round 5 bought them used). It does support `couplings`, `density`, `doser`, `doser_conv`, `floor_unit`, `furnace`, `glovebox`, `glovebox_conv`, `hood`, `hoods`, `machining`, `sieve`, `sieve_cell`, `units`, which round 5 bought new.
* **Where the market can't say:** eBay (blocked) and closed auctions would have given sale prices; these are asking
  prices. Several stations have only a handful of priced listings (`n_priced` in `summary.csv`), and the fault rates per
  condition are assumptions.
<!-- inshort:end -->

<!-- tables:start -->
## What changes from round 5

* **Stations with a real used market at a saving** (`used_ok`, 26): `couplings`, `density`, `doser`, `doser_conv`, `edm`, `floor_unit`, `furnace`, `furnaces`, `glovebox`, `glovebox_conv`, `hardness`, `hood`, `hoods`, `icpms`, `instron`, `machining`, `mastersizer`, `polish`, `sem`, `sieve`, `sieve_cell`, `units`, `vhx`, `xrd`, `xrf`, `zwick`.
* **In round 5's `USED_OK` but not supported by the market** (2): `chamber`, `nanoindenter`.
* **Not in `USED_OK` but with a real used market** (14): `couplings`, `density`, `doser`, `doser_conv`, `floor_unit`, `furnace`, `glovebox`, `glovebox_conv`, `hood`, `hoods`, `machining`, `sieve`, `sieve_cell`, `units`.
* Across the `used_ok` stations, the median `price_frac` is 0.31 (round 5: 0.45), the median `lead_w` 2.5 weeks (round 5: 2) and the median `p_fault` 0.28 (round 5: 0.25).

## Results by station

Round 5's stand-ins, for comparison: `price_frac` 0.45, `lead_w` 2, `p_fault` 0.25, `refurb_w` 6, `refurb_frac` 0.15, `extra_com_w` 1. **Market**: *yes* = at least 5 listings that fit, 2 of them in North America, one priced; *thin* = fewer; *none* = nothing found. Prices are asking prices in USD; *like-for-like* is the median over the twin's own model and its maker's line only. `price_frac` is the median used price plus freight and rigging, over the twin's new price.

| Key | Lab | In `USED_OK` | Market | Listings (N. America) | Priced | Median used, all | Priced on | Discount vs new | `price_frac` | `lead_w` | `p_fault` (best) | `extra_com_w` | Order to working, used / new (weeks) |
| --- | --- | :-: | --- | --: | --: | --: | --- | --: | --: | --: | --: | --: | --: |
| `sem` | vertical | yes | yes | 18 (9) | 5 | $16k | North America (4 priced): $16k | 84 % | 0.20 | 3.5 | 0.12 (0.05) | 1.5 | 9.7 / 12.0 |
| `eds` | vertical |  | thin | 1 (1) | 0 |  |  |  |  | 2.5 | 0.30 (0.30) | 1.5 | 8.8 / 11.0 |
| `ebsd` | vertical |  | thin | 2 (1) | 1 | $2,804 | all that fit (1 priced): $2,804 | 98 % | 0.04 | 5.0 | 0.30 (0.30) | 1.5 | 13.3 / 19.0 |
| `xrd` | vertical | yes | yes | 8 (6) | 1 | $24k | all that fit (1 priced): $24k | 78 % | 0.24 | 2.5 | 0.30 (0.10) | 1.5 | 9.8 / 12.0 |
| `xrf` | vertical | yes | yes | 18 (6) | 9 | $16k | North America (3 priced): $12k | 90 % | 0.12 | 2.5 | 0.28 (0.10) | 1.5 | 12.7 / 17.0 |
| `mastersizer` | vertical | yes | yes | 68 (36) | 14 | $16k | like-for-like (7 priced): $17k | 84 % | 0.18 | 2.5 | 0.23 (0.05) | 1.5 | 9.4 / 12.0 |
| `hardness` | vertical | yes | yes | 26 (14) | 13 | $5,277 | North America (9 priced): $7,999 | 89 % | 0.12 | 2.0 | 0.23 (0.10) | 0.5 | 6.2 / 9.0 |
| `nanoindenter` | vertical | yes | thin | 3 (3) | 2 | $23k | all that fit (2 priced): $23k | 91 % | 0.10 | 2.5 | 0.37 (0.30) | 1.5 | 11.2 / 19.0 |
| `pip` | vertical |  | none | 0 (0) | 0 |  |  |  |  |  |  | 0.5 | – / 13.0 |
| `vhx` | vertical | yes | yes (microscope) | 21 (8) | 12 |  | components (below) | 31 % | 0.69 | 2.0 | 0.33 | 0.5 | 6.5 / 7.0 |
| `polish` | vertical | yes | yes (polisher, press, saw) | 33 (19) | 17 |  | components (below) | 78 % | 0.22 | 2.0 | 0.53 | 0.5 | 7.3 / 10.0 |
| `furnaces` | vertical | yes | yes | 65 (29) | 23 | $4,396 | North America (10 priced): $3,225 | 84 % | 0.21 | 2.0 | 0.28 (0.05) | 0.5 | 6.3 / 9.0 |
| `sieve_cell` | vertical |  | yes (shaker) | 42 (28) | 17 |  | components (below) | 5 % | 0.95 | 2.0 | 0.25 | 0.5 | 8.3 / 15.0 |
| `doser` | vertical |  | yes (press, balance, pump) | 62 (41) | 36 |  | components (below) | 85 % | 0.15 | 2.0 | 0.59 | 0.5 | 9.4 / 20.0 |
| `glovebox` | vertical |  | yes | 14 (8) | 7 | $12k | North America (4 priced): $16k | 72 % | 0.31 | 2.5 | 0.28 (0.30) | 1.0 | 8.6 / 14.0 |
| `hoods` | vertical |  | yes (hood) | 13 (10) | 8 |  | components (below) | 25 % | 0.75 | 2.5 | 0.34 | 1.0 | 7.9 / 11.0 |
| `icpms` | vertical | yes | yes (instrument) | 94 (60) | 35 |  | components (below) | 39 % | 0.61 | 3.5 | 0.21 | 2.0 | 13.2 / 18.0 |
| `instron` | vertical | yes | yes | 59 (25) | 29 | $12k | like-for-like in North America (3 priced): $15k | 91 % | 0.12 | 3.0 | 0.30 (0.20) | 1.5 | 12.3 / 20.0 |
| `chamber` | vertical | yes | thin | 4 (2) | 3 | $3,694 | like-for-like (3 priced): $3,694 | 93 % | 0.09 | 2.5 | 0.17 (0.30) | 0.5 | 6.5 / 17.0 |
| `zwick` | vertical | yes | yes | 32 (11) | 18 | $19k | North America (6 priced): $13k | 63 % | 0.38 | 3.0 | 0.17 (0.05) | 0.5 | 8.0 / 12.0 |
| `edm` | vertical | yes | yes | 117 (50) | 24 | $37k | North America (10 priced): $38k | 84 % | 0.20 | 3.0 | 0.31 (0.20) | 2.0 | 13.8 / 23.0 |
| `machining` | vertical |  | yes (lathe, bar_feeder, robot_arm) | 105 (32) | 21 |  | components (below) | 16 % | 0.84 | 3.0 | 0.61 | 2.0 | 14.9 / 28.0 |
| `carvera` | vertical |  | none | 0 (0) | 0 |  |  |  |  |  |  | 0.5 | – / 3.0 |
| `units` | vertical |  | yes (mir, arm) | 46 (9) | 18 |  | components (below) | 37 % | 0.63 | 2.0 | 0.37 | 1.0 | 10.9 / 19.0 |
| `floor_unit` | vertical |  | yes (mir, arm, vacuum) | 53 (16) | 19 |  | components (below) | 35 % | 0.65 | 2.0 | 0.56 | 1.0 | 8.9 / 17.0 |
| `shuttle` | vertical |  | thin | 35 (2) | 1 | $42k |  |  |  | 4.0 | 0.30 (0.30) | 2.0 | 13.8 / 18.0 |
| `couplings` | vertical |  | yes | 6 (4) | 4 | $568 | like-for-like in North America (4 priced): $568 | 86 % | 0.18 | 2.0 | 0.25 (0.10) | 0.0 | 6.5 / 10.0 |
| `midi` | vertical |  | none | 82 (11) | 22 | $71k |  |  |  | 3.0 | 0.32 (0.20) | 6.0 | 20.9 / 26.0 |
| `mxlab` | vertical |  | none | 4 (4) | 1 | $10k |  |  |  | 3.0 | 0.30 (0.30) | 6.0 | 20.8 / 34.0 |
| `repowder` | both |  | none | 2 (0) | 0 |  |  |  |  | 8.0 | 0.10 (0.10) | 2.0 | 12.6 /  |
| `ups` | vertical |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 0.0 | – / 6.0 |
| `cameras` | vertical |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 0.0 | – / 4.0 |
| `services` | vertical |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 1.0 | – / 18.0 |
| `sieve` | conventional |  | yes | 44 (28) | 17 | $2,625 | like-for-like in North America (7 priced): $3,000 | 62 % | 0.44 | 2.0 | 0.25 (0.05) | 0.5 | 5.3 /  |
| `doser_conv` | conventional |  | yes (press, balance) | 36 (18) | 19 |  | components (below) | 52 % | 0.48 | 2.0 | 0.49 | 0.5 | 5.4 /  |
| `furnace` | conventional |  | yes | 65 (29) | 23 | $4,524 | North America (10 priced): $3,225 | 89 % | 0.14 | 2.0 | 0.28 (0.05) | 0.5 | 5.3 /  |
| `density` | conventional |  | yes | 16 (9) | 13 | $2,237 | North America (8 priced): $2,198 | 82 % | 0.23 | 2.0 | 0.26 (0.10) | 0.5 | 5.3 /  |
| `glovebox_conv` | conventional |  | yes | 14 (8) | 7 | $12k | North America (4 priced): $16k | 72 % | 0.31 | 2.5 | 0.28 (0.30) | 1.0 | 6.6 /  |
| `hood` | conventional |  | yes (hood) | 13 (10) | 8 |  | components (below) | 25 % | 0.75 | 2.5 | 0.34 | 1.0 | 6.9 /  |
| `cubxl` | conventional |  | n/a (new only) | 0 (0) | 0 |  |  |  |  |  |  | 0.5 |  |

### Stations that are several machines

| Key | Component | New (each) | Market | Listings (N. America) | Priced | Median used | `price_frac` |
| --- | --- | --: | --- | --: | --: | --: | --: |
| `vhx` | libs | $95k | none | 0 (0) | 0 |  |  |  |
| `vhx` | microscope | $95k | yes | 21 (8) | 12 | like-for-like (9 priced): $36k | 0.38 | 2.0 |
| `polish` | polisher | $23k | yes | 12 (6) | 5 | North America (3 priced): $2,500 | 0.13 | 2.0 |
| `polish` | press | $19k | yes | 9 (6) | 6 | North America (5 priced): $2,750 | 0.17 | 2.0 |
| `polish` | saw | $13k | yes | 12 (7) | 6 | North America (5 priced): $5,550 | 0.47 | 2.0 |
| `sieve_cell` | rest | $53k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `sieve_cell` | shaker | $6,700 | yes | 42 (28) | 17 | like-for-like in North America (7 priced): $3,000 | 0.52 | 2.0 |
| `doser` | balance | $3,500 | yes | 17 (7) | 11 | North America (6 priced): $822 | 0.38 | 2.0 |
| `doser` | carousel | $2,362 | n/a (new only) | 0 (0) | 0 |  |  |  |
| `doser` | press | $41k | yes | 19 (11) | 8 | North America (4 priced): $2,000 | 0.06 | 2.0 |
| `doser` | pump | $3,000 | yes | 26 (23) | 17 | like-for-like in North America (14 priced): $1,025 | 0.55 | 2.0 |
| `hoods` | hood | $14k | yes | 13 (10) | 8 | like-for-like in North America (3 priced): $3,500 | 0.37 | 2.5 |
| `hoods` | install | $21k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `icpms` | autosampler | $12k | none | 0 (0) | 0 |  |  |  |
| `icpms` | instrument | $190k | yes | 94 (60) | 35 | like-for-like in North America (18 priced): $82k | 0.46 | 3.5 |
| `icpms` | rest | $58k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `machining` | bar_feeder | $16k | yes | 5 (5) | 1 | all that fit (1 priced): $6,500 | 0.47 | 2.0 |
| `machining` | lathe | $65k | yes | 65 (21) | 6 | like-for-like (3 priced): $55k | 0.94 | 3.0 |
| `machining` | rest | $142k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `machining` | robot_arm | $52k | yes | 35 (6) | 14 | like-for-like (14 priced): $20k | 0.41 | 2.0 |
| `units` | arm | $45k | yes | 35 (6) | 14 | like-for-like (14 priced): $20k | 0.47 | 2.0 |
| `units` | gripper | $5,500 | thin | 2 (0) | 0 |  |  | 7.0 |
| `units` | mir | $62k | yes | 9 (3) | 4 | like-for-like (3 priced): $33k | 0.55 | 2.0 |
| `units` | rest | $28k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `floor_unit` | arm | $45k | yes | 35 (6) | 14 | like-for-like (14 priced): $20k | 0.47 | 2.0 |
| `floor_unit` | gripper | $5,500 | thin | 2 (0) | 0 |  |  | 7.0 |
| `floor_unit` | mir | $62k | yes | 9 (3) | 4 | like-for-like (3 priced): $33k | 0.55 | 2.0 |
| `floor_unit` | rest | $30k | n/a (new only) | 0 (0) | 0 |  |  |  |
| `floor_unit` | vacuum | $12k | yes | 7 (7) | 1 | all that fit (1 priced): $8,045 | 0.74 | 2.0 |
| `doser_conv` | balance | $4,000 | yes | 17 (7) | 11 | North America (6 priced): $822 | 0.33 | 2.0 |
| `doser_conv` | doser | $5,000 | n/a (new only) | 0 (0) | 0 |  |  |  |
| `doser_conv` | press | $9,000 | yes | 19 (11) | 8 | North America (4 priced): $2,000 | 0.26 | 2.0 |
| `hood` | hood | $14k | yes | 13 (10) | 8 | like-for-like in North America (3 priced): $3,500 | 0.37 | 2.5 |
| `hood` | install | $21k | n/a (new only) | 0 (0) | 0 |  |  |  |

## Examples by station

Up to three priced listings per key that count in the statistics, the twin's own model and North America first (all of them are in `listings.csv`).

* `sem`: [2014 Hitachi TM3030 desktop Scanning Electron Microscope](https://www.machinio.com/listings/112379422-2014-hitachi-tm3030-desktop-scanning-electron-microscope-in-tokyo-japan) (family; $30k; 2014, as is tested; Tokyo, Japan; machinio); [Hitachi High Tech TM1000 Tabletop Miscroscope](https://www.labx.com/item/hitachi-high-tech-tm1000-tabletop-miscroscope/ESS-218916-135581066025) (sub; $8,000; warranty; California, US; labx); [Hitachi TM1000 Tabletop SEM](https://www.labx.com/item/hitachi-tm1000-tabletop-sem/222484-4958062) (sub; $16k; refurbished; New Jersey, US; labx).
* `ebsd`: [HKL Technology Nordlys XL 30 EBSD Detector Module Working Surplus](https://www.machinio.com/listings/114624892-hkl-technology-nordlys-xl-30-ebsd-detector-module-working-surplus-in-albuquerque-nm) (family; $2,804; used; Albuquerque, NM, USA; machinio).
* `xrd`: [2012 Rigaku Miniflex 600 X-ray powder diffractometer](https://www.machinio.com/listings/112090360-2012-rigaku-miniflex-600-x-ray-powder-diffractometer-in-san-jose-ca) (exact; $24k; used; San Jose, CA, USA; machinio).
* `xrf`: [Panalytical Epsilon5 X-Ray Fluorescence Spectrometer XRF Analyzer](https://www.machinio.com/listings/122193340-panalytical-epsilon5-x-ray-fluorescence-spectrometer-xrf-analyzer-in-baroda-mi) (sub; $8,820; used; Baroda, MI, USA; machinio); [PANalytical Epsilon 5 XRF analysis system mining ore material sampling](https://www.machinio.com/listings/51921213-panalytical-epsilon-5-xrf-analysis-system-mining-ore-material-sampling-in-santa-clarita-ca) (sub; $12k; tested; Santa Clarita, CA, USA; machinio); [THERMO QUANX SPECTROMETER XRF Analyzer EDXRF ANALYZER](https://www.machinio.com/listings/100969216-thermo-quanx-spectrometer-xrf-analyzer-edxrf-analyzer-in-milton-freewater-or) (sub; $12k; as is; Milton-Freewater, OR, USA; machinio).
* `mastersizer`: [Malvern Mastersizer 3000 Particle Analyzer](https://www.labx.com/item/malvern-mastersizer-3000-particle-analyzer/scp-54817-5782150) (exact; $35k; used; Washington, US; labx); [LAB SYSTEMS Malvern Mastersizer 3000E Particle Size Analyzer For Sale](https://www.dotmed.com/listing/lab-general/lab-systems/malvern-mastersizer-3000e/particle-size-analyzer/5106676) (exact; $17k; as is tested; Poland; dotmed); [Malvern Mastersizer 3000](https://www.machinio.com/listings/111884414-malvern-mastersizer-3000-in-burladingen-germany) (exact; $18k; refurbished; Burladingen, Baden-Württemberg, Germany; machinio).
* `hardness`: [Wilson Tukon Microhardness Tester Model 300 BM/DF](https://www.machinio.com/listings/116316344-wilson-tukon-microhardness-tester-model-300-bm-df-in-milton-freewater-or) (sub; $3,000; used; Milton-Freewater, OR, USA; machinio); [Leitz Miniload micro hardness tester, Vickers diamond, 100 and 400 pow](https://www.machinio.com/listings/16217154-leitz-miniload-micro-hardness-tester-vickers-diamond-100-and-400-power-in-salem-ma) (sub; $5,250; used; Salem, MA, USA; machinio); [Leitz Miniload micro hardness tester, Vickers diamond, 100 and 400 pow](https://www.labx.com/item/leitz-miniload-micro-hardness-tester-vickers-diamond-100/DIS-57385-LBQ055LeitzMiniloadm) (sub; $5,250; refurbished; Massachusetts, US; labx).
* `nanoindenter`: [Hysitron TRIBOINDENTER TS150 W/CONTROL](https://www.machinio.com/listings/100970167-hysitron-triboindenter-ts150-w-control-in-milton-freewater-or) (sub; $6,500; used; Milton-Freewater, OR, USA; machinio); [Hysitron TI 900 #9566-P](https://www.machinio.com/listings/88254579-hysitron-ti-900-9566-p-in-baltimore-md) (sub; $40k; as is; Baltimore, MD, USA; machinio).
* `vhx`: [Keyence VHX-7000 4K Digital Microscope System](https://www.labx.com/item/keyence-vhx-7000-4k-digital-microscope-system/scp-162061-5915428) (exact; $42k; used; Rhode Island, US; labx); [KEYENCE VHX-7000 Digital Microscope KEYENCEVHX-7000](https://www.machineseeker.com/keyence-vhx-7000/i-22910831) (exact; $22k; 2021, tested; Robotnícka 5441, 036 01 Martin, Slovensk; machineseeker); [Measuring system KeyenceKeyence VHX-7000 Series](https://www.machineseeker.com/keyence-keyence+vhx-7000+series/i-22014618) (exact; $36k; 2024, warranty; Schlieren, Switzerland; machineseeker).
* `polish`: [LECO Spectrum 2000 Speed Polisher Grinder](https://www.machinio.com/listings/86948002-leco-spectrum-2000-speed-polisher-grinder-in-santa-barbara-ca) (family; $4,995; tested; Santa Barbara, CA, USA; machinio); [Buehler Simplimet 2 Specimen Mounting Press €1,000.00 Euro](https://www.labx.com/item/buehler-simplimet-2-specimen-mounting-press/DIS-50372-A220220) (sub; $1,099; used; Rhode Island, US; labx); [Buehler SimpliMet 1000 Mounting Press €1,500.00 Euro](https://www.labx.com/item/buehler-simplimet-1000-mounting-press/DIS-50372-A220229) (sub; $1,648; used; Rhode Island, US; labx).
* `furnaces`: [Nabertherm NA 120/65/B500 €8,890.00 Euro](https://www.labx.com/item/nabertherm-na-120-65-b500/DIS-96958-45025) (family; $9,769; refurbished; Baden-Württemberg, DE; labx); [Lindberg/Blue M Box Furnace](https://www.labx.com/item/lindberg-blue-m-box-furnace/DIS-50372-A198660) (sub; $1,000; used; Rhode Island, US; labx); [Thermo Scientific BF51848A-1 Lindberg/Blue M Moldatherm Box Furnaces](https://www.machinio.com/listings/119730744-thermo-scientific-bf51848a-1-lindberg-blue-m-moldatherm-box-furnaces-in-rancho-cordova-ca) (sub; $1,454; warranty; Rancho Cordova, CA; machinio).
* `sieve_cell`: [Retsch AS 200 control Vibratory Sieve Shaker Digital](https://www.labx.com/item/retsch-as-200-control-vibratory-sieve-shaker-digital/DIS-50372-A222980) (exact; $2,000; used; Rhode Island, US; labx); [Retsch AS 200 Control B Sieve Shaker](https://www.labx.com/item/retsch-as-200-control-b-sieve-shaker/DIS-50372-416689) (exact; $3,000; used; Rhode Island, US; labx); [Retsch AS 200 Jet Air Jet Sieving Machine](https://www.labx.com/item/retsch-as-200-jet-air-jet-sieving-machine/63231-34637) (exact; $3,850; refurbished warranty; Connecticut, US; labx).
* `doser`: [Specac Atlas Autotouch Press Model - GS25810 Benchtop Laboratory Press](https://www.machinio.com/listings/116047016-specac-atlas-autotouch-press-model-gs25810-benchtop-laboratory-press-in-scotland-uk) (exact; $6,561; tested; Scotland, United Kingdom; machinio); [Specac Atlas Autotouch Press Model - GS25810 Benchtop Laboratory Press](https://www.labx.com/item/specac-atlas-autotouch-press-model-gs25810-benchtop/DIS-225824-ITEM-58293) (exact; $6,596; used; Wales, GB; labx); [Edwards RV3 Rotary Vane Vacuum Pump](https://www.machinio.com/listings/117115637-edwards-rv3-rotary-vane-vacuum-pump-in-suwanee-ga) (family; $175; used; Suwanee, GA, USA; machinio).
* `glovebox`: [LINEMASTER OMNI-LAB Inert-Atmosphere Glovebox Chamber](https://www.labx.com/item/linemaster-omni-lab-inert-atmosphere-glovebox-chamber/DIS-50372-A222294) (family; $5,000; used; Rhode Island, US; labx); [MBRAUN UNIlab M Braun Gas Purifier GLOVEBOX SYSTEM MB-BL-1](https://www.machinio.com/listings/122494444-mbraun-unilab-m-braun-gas-purifier-glovebox-system-mb-bl-1-in-milton-freewater-or) (sub; $10k; used; Milton-Freewater, OR, USA; machinio); [Mbraun Labmaster 130 64941](https://www.machinio.com/listings/103823847-mbraun-labmaster-130-64941-in-freehold-township-nj) (sub; $21k; used; Freehold, NJ, USA; machinio).
* `hoods`: [BMC 8' Fume Hood](https://www.machinio.com/listings/74113618-bmc-8-fume-hood-in-san-diego-ca) (family; $3,500; used; San Diego, CA, USA; machinio); [Hanson 4' Fume Hood](https://www.machinio.com/listings/79199588-hanson-4-fume-hood-in-san-diego-ca) (family; $3,500; used; San Diego, CA, USA; machinio); [(2021) Mott SafeGuard Model 7471040 5 foot chemical fume hood (pre-own](https://www.labx.com/item/2021-mott-safeguard-model-7471040-5-foot-chemical-fume-hood/DIS-83192-dd116633b983c5d109f48b36137f802a) (family; $5,500; used; Ohio, US; labx).
* `icpms`: [Agilent 7800 ICPMS](https://www.labx.com/item/agilent-7800-icpms/13496024) (exact; $67k; warranty; Missouri, US; labx); [AGILENT 7850 ICP-MS Mass Spectrometer For Sale](https://www.dotmed.com/listing/mass-spectrometer/agilent/7850-icp-ms/5845264) (exact; $75k; as is tested; NH, USA; dotmed); [Agilent 7800 ICP-MS | Inductively Coupled Plasma Mass Spectrometer | F](https://www.labx.com/item/agilent-7800-icp-ms-inductively-coupled-plasma-mass/scp-250383-5772109) (exact; $80k; used; Alberta, CA; labx).
* `instron`: [INSTRON 1125 5500R UNIVERSAL TENSILE COMPRESSION MATERIAL TESTING MACH](https://www.machinio.com/listings/121833293-instron-1125-5500r-universal-tensile-compression-material-testing-machine-in-woodruff-sc) (family; $10k; used; Woodruff, SC, USA; machinio); [Instron 1123 Tensile Tester 4400R](https://www.machinio.com/listings/100969083-instron-1123-tensile-tester-4400r-in-milton-freewater-or) (family; $15k; used; Milton-Freewater, OR, USA; machinio); [Instron fatigue test frame 1127 tension compression 5800R CAP 56,000LB](https://www.machinio.com/listings/100968907-instron-fatigue-test-frame-1127-tension-compression-5800r-cap-56-000lbs-in-milton-freewater-or) (family; $35k; used; Milton-Freewater, OR, USA; machinio).
* `chamber`: [Instron 3119-403 temperature chamber for single column testing machine](https://www.labx.com/item/instron-3119-403-temperature-chamber-for-single-column/DIS-86979-4244) (family; $9,650; refurbished warranty; California, US; labx); [Instron SFL SP 1711 Furnace & Controller Lab £2,400.00 Pound](https://www.labx.com/item/instron-sfl-sp-1711-furnace-controller-lab/DIS-225824-ITEM-55068) (family; $3,166; used; Wales, GB; labx); [Instron SFL 2000K Furnace & Controller Lab £2,800.00 Pound](https://www.labx.com/item/instron-sfl-2000k-furnace-controller-lab/DIS-225824-ITEM-55067) (family; $3,694; used; Wales, GB; labx).
* `zwick`: [Zwick/Roell Z0.5TN Testing machine for tensile and compression with 50](https://www.labx.com/item/zwick-roell-z0-5tn-testing-machine-for-tensile-and/DIS-86979-5033) (family; $28k; refurbished warranty; California, US; labx); [2020 Zwick Roell ProLine Z010 Materials Tensile Tester – 10 kN](https://www.labx.com/item/2020-zwick-roell-proline-z010-materials-tensile-tester-10/DIS-86979-5193) (family; $38k; refurbished warranty; California, US; labx); [Universal testing machine ZwickRoellZwicki Z2,5](https://www.machineseeker.com/zwickroell-zwicki+z2%2C5/i-21245962) (family; $6,484; tested; Giebel 30, 42327 Wuppertal, Deutschland; machineseeker).
* `edm`: [Wire eroding machine FanucROBOCUT α-C400iC](https://www.machineseeker.com/fanuc-robocut+%CE%B1-c400ic/i-23271802) (exact; $98k; 2024, refurbished; Priemyselný Areál Východ 4944, 058 01 Po; machineseeker); [FANUC ROBOCUT Alpha-0iB A04B-0313-B011#U5 Wire EDM](https://www.machinio.com/listings/119066730-fanuc-robocut-alpha-0ib-a04b-0313-b011-u5-wire-edm-used-in-detroit-mi) (family; $20k; 2002, used; Detroit, MI; machinio); [FANUC 1IE-SAWF WIRE [WE-010181]](https://www.machinio.com/listings/118922911-fanuc-1ie-sawf-wire-we-010181-in-united-states) (family; $50k; used; United States; machinio).
* `machining`: [2014 Haas ST-10](https://www.machinio.com/listings/122513622-2014-haas-st-10-in-chicago-il) (exact; $25k; 2014, used; Chicago, IL, USA; machinio); [Machining center HAASST-10](https://www.machineseeker.com/haas-st-10/i-21433077) (exact; $38k; 2019, tested; Maleva 2c, 11711 Tallinn, EE; machineseeker); [CNC lathe HAASST-10](https://www.machineseeker.com/haas-st-10/i-20963087) (exact; $55k; 2022, tested; Unit 4 Bretfield Ct, Bretton St 5, WF12 ; machineseeker).
* `units`: [Industrial robot MiRMiR250 Shelf Carrier ESD und Zubehör](https://www.machineseeker.com/mir-mir250+shelf+carrier+esd+und+zubeh%C3%B6r/i-21127667) (exact; $33k; 2024, tested; Leiderer Straße 12, 63811 Stockstadt a. ; machineseeker); [MIR 100 Mobile industrial robot (2018) with 110v MiRCharge](https://www.machinio.com/listings/106668342-mir-100-mobile-industrial-robot-2018-with-110v-mircharge-in-san-jose-ca) (family; $19k; 2018, used; San Jose, CA, USA; machinio); [Universal Robotics UR10 Robot, , 2018](https://www.machinio.com/listings/115117801-universal-robotics-ur10-robot-used-2018-in-imlay-city-mi) (family; $20k; 2018, tested; Imlay City, MI, USA; machinio).
* `floor_unit`: [Nilfisk VHS210N1 LC C2D2 AU Single Phase Combustible Dust Vacuum](https://www.machinio.com/listings/118024317-nilfisk-vhs210n1-lc-c2d2-au-single-phase-combustible-dust-vacuum-in-ixonia-wi) (family; $8,045; new surplus; Ixonia, WI, USA; machinio).
* `shuttle`: [2010 SYSTEM LOGISTICS Modula-MX50-7300](https://www.machinio.com/listings/112425623-2010-system-logistics-modula-mx50-7300-in-british-columbia-canada) (sub; $42k; used; British Columbia, Canada; machinio).
* `couplings`: [Stäubli 34.11024 Combitac Male Aluminum Air Supply Connection Housing](https://www.machinio.com/listings/122555075-staubli-34-11024-combitac-male-aluminum-air-supply-connection-housing-assembly-in-baroda-mi) (exact; $372; used; Baroda, MI, USA; machinio); [Stäubli 34.11024 Combitac Male Aluminum Air Supply Connection Housing](https://www.machinio.com/listings/122555076-staubli-34-11024-combitac-male-aluminum-air-supply-connection-housing-assembly-in-baroda-mi) (exact; $392; used; Baroda, MI, USA; machinio); [CT-K/MODUL86591/84480,31008124 | Staubli CT-K/MODUL86591/84480 CombiTa](https://www.machinio.com/listings/106730567-ct-k-modul86591-84480-31008124-staubli-ct-k-modul86591-84480-combitac-connector-assembly-31008124-new-in-baroda-mi) (exact; $745; used; Baroda, MI, USA; machinio).
* `midi`: [Concept Laser Machines Mlab cusing 200R Steel Metal 3D Printer](https://www.machinio.com/listings/104975803-concept-laser-machines-mlab-cusing-200r-steel-metal-3d-printer-in-baltimore-md) (sub; $44k; tested; Baltimore, MD; machinio); [3d printer SLMSLM 280 HL](https://www.machineseeker.com/slm-slm+280+hl/i-23334206) (sub; $38k; 2013, tested; Liberec, Czech Republic; machineseeker); [Metal 3d printer Concept LaserMlab 100R](https://www.machineseeker.com/concept+laser-mlab+100r/i-23020031) (sub; $44k; 2021, tested; Lysá nad Labem, Czech Republic; machineseeker).
* `mxlab`: [OPTOMEC 750 LENS MACHINE](https://www.machinio.com/listings/100969301-optomec-750-lens-machine-in-milton-freewater-or) (sub; $10k; used; Milton-Freewater, OR; machinio).
* `density`: [AmScope Stereo Microscope](https://www.labx.com/item/amscope-stereo-microscope/DIS-50372-A217988) (sub; $750; used; Rhode Island, US; labx); [Leeds Stereo Microscope Extendable Eyepoint Adjuster for Olympus SZX](https://www.labx.com/item/leeds-stereo-microscope-extendable-eyepoint-adjuster-for/DIS-88306-e072eb72da43b302c7d541629a6e457b) (sub; $995; used; North Carolina, US; labx); [Carton SPZV-50 Stereo Microscope Specifications](https://marshallscientific.com/products/carton-spzv-50-stereo-microscope) (sub; $1,095; warranty; Cambridge, MA, US (Marshall Scientific); marshall).

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
| [eBay](https://www.ebay.com/) | marketplace (active and sold) | blocked | 3 |  |
| [BidSpotter](https://www.bidspotter.com/) | auction aggregator | challenged | 1 |  |
| [EquipNet](https://www.equipnet.com/) | auction and dealer | challenged | 2 |  |
| [Surplus Record](https://www.surplusrecord.com/) | machinery listings | challenged | 1 |  |
| [LabX](https://www.labx.com/) | lab-equipment marketplace (dealers) | ok | 340 | 252 |
| [Machinio](https://www.machinio.com/) | machinery and equipment aggregator (dealers) | ok | 342 | 440 |
| [GovDeals](https://www.govdeals.com/) | government and university surplus auctions | ok | 81 | 13 |
| [AllSurplus](https://www.allsurplus.com/) | commercial surplus auctions (same platform as GovDeals) | ok | 99 | 40 |
| [Public Surplus](https://www.publicsurplus.com/) | government and university surplus auctions | ok | 43 | 2 |
| [Federal Equipment Company](https://www.fedequip.com/) | used-equipment dealer | ok | 8 |  |
| [BioSurplus](https://www.biosurplus.com/) | used lab-equipment dealer | ok | 3 |  |
| [Machineseeker](https://www.machineseeker.com/) | machinery marketplace (dealers and auctions, mostly Europe) | ok | 237 | 195 |
| [Exapro](https://www.exapro.com/) | used-machinery broker (Europe) | ok | 106 | 87 |
| [DOTmed](https://www.dotmed.com/) | medical and lab equipment marketplace | ok | 35 | 15 |
| [Marshall Scientific](https://www.marshallscientific.com/) | used lab-equipment dealer and refurbisher | ok | 38 | 5 |
| [Conquer Scientific](https://conquerscientific.com/) | used and refurbished analytical instruments dealer | ok | 16 | 5 |
| [GMI (re-certified equipment)](https://www.gmi-inc.com/) | refurbisher of analytical instruments | ok | 7 |  |
| [Robots Done Right](https://robotsdoneright.com/) | used industrial robot dealer | ok | 8 |  |
| [SEMTech Solutions](https://www.semtechsolutions.com/) | SEM refurbisher | ok | 18 | 11 |
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

## `summary.csv`, column by column

| Column | Meaning |
| --- | --- |
| `lab`, `station`, `component`, `item`, `qty` | The twin's key (`econ.py`), and the component for a station that is several machines; `(station)` is the station's combined row, which is the one round 6 reads. |
| `new_usd_each`, `new_lead_w_vendor`, `new_lead_text`, `twin_lead_w` | The twin's new price; the vendor's stated lead where published; round 4's assumed lead (with the purchase order). |
| `market`, `market_like_for_like`, `used_ok` | Whether a real used market exists (*yes*, *thin*, *none*), over all listings that fit and over like-for-like ones; `used_ok` = a real market and `price_frac` under 1. |
| `n_listings`, `n_north_america`, `n_priced`, `n_current_bids`, `n_exact`, `n_family`, `n_substitute` | Counts of listings that fit (duplicates and parts left out). |
| `median_used_usd`, `p25_used_usd`, `p75_used_usd`, `min_used_usd`, `max_used_usd`, `median_exact_family_usd` | Asking prices of every priced listing that fits, and of like-for-like ones. |
| `price_basis`, `median_basis_usd`, `discount_vs_new`, `discount_vs_new_all` | The group the price is taken from (see below), its median, and the discount against new (over that group, and over all). |
| `freight_rigging_usd`, `median_delivered_usd`, `price_frac` | Freight and rigging where the lab would buy; the median plus that; over the twin's new price (round 5's `price_frac`). |
| `bought_from`, `lead_w`, `lead_sigma`, `ship_w`, `rigging_w` | Where the lab would buy; weeks from the purchase order to the unit on site (round 5's `lead_w`), its log-normal spread, and its parts. |
| `new_parts_lead_w`, `lead_w_with_new_parts` | For a station bought partly used: the lead of the parts still bought new, and the station's lead with them. |
| `p_fault`, `p_fault_best`, `share_*` | The chance it arrives faulty or needs refurbishment, from the condition mix (round 5's `p_fault`); for the best-condition unit near the median price; the mix itself. |
| `refurb_w`, `refurb_sigma`, `refurb_frac`, `refurb_source`, `refurb_expected_w` | If faulty: weeks and cost (fraction of new) to put right, where they come from, and `p_fault` times the weeks. |
| `extra_com_w`, `checkout_w` | Commissioning a used unit needs beyond a new one (round 5's `extra_com_w`). |
| `order_to_working_used_w`, `order_to_working_new_w` | Weeks from the purchase order to working: used (order, lead, expected refurbishment, installation, commissioning, checkout) against new (round 4's lead, installation, commissioning), before the facility window. |

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

**Searches.** 195 queries over 14 sites (`tools/plan1.json`, `tools/plan2.json`, `tools/plan3.json`): model names (the twin's own model
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
* **Where the lab would buy.** If at least two listings that fit are in North America, the lead and the fault risk are
  those of the North American listings (a lab doesn't import what it can truck); otherwise of all of them. Freight and
  rigging are for the same place. The price is the median asking price of the first group with at least three priced
  listings, in an order that depends on the station (`price_basis` says which group was used):
  * measuring instruments (SEM, EDS, EBSD, XRD, XRF, laser diffraction, micro-Vickers, nanoindenter, ICP-MS, the VHX):
    like-for-like in North America, like-for-like anywhere, then any that fit in North America;
  * generic tools (furnaces, hoods, gloveboxes, prep, frames and chambers, sieve shakers, the doser's parts, the EDM,
    the lathe): like-for-like in North America, any that fit in North America, then like-for-like anywhere;
  * stations whose integration depends on the model (`LFL_REQUIRED`: the Kardex Shuttles, the LPBF and DED machines,
    the atomizer, the PIP, the couplings, and the MiR, UR arm and gripper of the robot units and the machining cell):
    like-for-like only, and the market is judged on like-for-like listings too.

  Like-for-like means the twin's own model or its maker's line of the same generation (a TM3000-TM4000 tabletop SEM,
  a Mastersizer 2000 or 3000, any FANUC ROBOCUT, a MiR or a UR arm): an older or manual instrument can measure, but
  not always as the automated lab needs.
* **Plausible prices only.** A price under 2 % or over 150 % of the twin's new price (a part, a placeholder, a bundle or
  a new unit at list) stays in `listings.csv` but out of the statistics (`in_price_stats`), as does a running
  auction's current bid.
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

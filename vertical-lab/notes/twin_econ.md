# The twin's economics: what an experiment costs, how full the lab is, and how much faster it gets there

The digital twin ([`twin.md`](twin.md), [`../twin/README.md`](../twin/README.md)) runs FLAIME (Al, LPBF) and the ONR
YIP (Cu, DED) at the same time, either on the proposals' partner facilities (`facility="proposed"`, called the
*conventional lab* here) or in PR 318's automated lab (`facility="vertical_lab"`). Its own ledger only counts what the
proposals' non-personnel budgets pay: feedstock, consumables and station fees. This layer adds what that ledger leaves
out, so the two labs can be compared on what they actually cost:

* the **capital and running costs** of each lab ([`../twin/econ.py`](../twin/econ.py)): every machine with its price
  and source, service life, service contract, power and floor area; people;
* the **utilization** of each instrument and the **outside work** its idle hours could take as a cloud user facility,
  with the slowdown that work would cause the campaigns ([`../twin/cloud.py`](../twin/cloud.py));
* the **acceleration factor** and **enhancement factor** of the self-driving-lab literature, with time to target and
  cost to target together ([`../twin/accel.py`](../twin/accel.py)).

```bash
cd vertical-lab
python3 -m pytest -q twin/tests/test_econ.py          # 18 checks, under a second
python3 -m twin.econ tables                           # capex and annual cost of each lab
python3 -m twin.cloud validate 4                      # outside jobs booked into the twin, 4 seeds a level (2 workers)
python3 -m twin.econ all                              # figures, out/twin2/econ/econ_summary.json, and this file's results
```

`twin.econ all` reads the round-2 runs in `out/twin2/runs/*.jsonl` when they hold both facilities (otherwise round 1's
`out/twin/runs/facility.jsonl` and `main.jsonl`), the event logs in `out/twin2/events/` and `out/twin2/econ/events/`,
and the state of the art from `out/twin2/oracle.json`.

## Method

### Costs

**Equipment.** Each item has a price (each, delivered; installed where the source says so), a service life, an annual
service contract as a share of the price, an average power draw and a duty (the share of the year it draws that much),
and a floor area (tray instruments ride in the Shuttles and take none). Prices come first from procurement records
(USAspending awards, EU TED awards), then list prices, then the lab's own notes; what has no published price is marked
`estimate` or `assumed`. Most were collected for the $200M facility budget (`facility/costs_and_sizes.md` at commit
aa41d0d) and checked or extended for this layer. A year of an item costs:

* **depreciation**, straight-line over its life (or a capital-recovery annuity with `discount`). BYU capitalizes
  equipment over 3-10 years and buildings over 40 ([BYU asset capitalization](https://finserve.byu.edu/asset-capitalization-procedures));
  Dartmouth uses 7 years for scientific equipment
  ([schedule](http://www.dartmouth.edu/finance/purchasing/ppe/useful_life_schedule.php)). Instruments get 10 years
  here, the robots 7, cameras 5, the Shuttles 15, hoods and the fit-out 20 (assumed within those ranges);
* **service**: 8-15 % of the purchase price a year for full service on analytical instruments
  ([Lab Manager](https://www.labmanager.com/optimize-instrument-service-contracts-based-on-risk-costs-and-criticality-35207)),
  about 10 % for electron microscopes (Univ. of Florida, on the
  [MIT labnetwork list](https://mtl.mit.edu/pipermail/labnetwork/attachments/20240208/bb294d65/attachment.html)); two
  federal one-year Mastersizer 3000 agreements cost 4-13 % of the instrument. 10 % is used for the SEM, EDS, EBSD,
  XRD, XRF, ICP-MS, nanoindenter, MIDI and MX-Lab, 5-8 % for the atomizer, frames, EDM and PIP, 2-5 % for simple
  equipment and the robots (assumed);
* **utilities and space**: electricity at Utah's commercial price, 10.40 c/kWh (EIA
  [Electric Power Monthly table 5.6.B](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_b),
  Jan-Sep 2026), at each item's draw and assumed duty; floor space at $20/ft²/yr to operate (assumed, from EAB's
  research-lab cost of ownership, [$2.3M per 1,000 ft² over 50 years](https://eab.com/wp-content/uploads/2025/09/PDF-EAB-Research-True-Costs-of-Space-IG.pdf));
  the building itself is depreciated with the capex, at the $200M plan's $825/ft² over 40 years. The vertical lab's
  floor is its machines' footprints plus its 305 m² of open floor (`notes/floor_cleaning.md`); the conventional lab's
  is its machines plus 40 m² (assumed).

**People.** The vertical lab has one technician on the weekday day shift (the atomizer's crucible and upkeep:
`upkeep.py` books 31 h a week of tasks after the ramp, 13 of them the crucible) and a quarter of a research engineer
for the robots' programs, recoveries and repairs (assumed). The conventional lab's work is done by graduate students,
by the hour: `econ.HANDS_ON` gives the hands-on hours of each booking (a fixed part per job plus a share of the
station hours; e.g. the atomizer is attended throughout plus an hour of loading and cleaning, a Utah MIDI build is
3 h of travel, set-up and depowdering, a Mines session 2 h of preparation and shipping; all assumed). Rates: a BYU
PhD student costs the $31,500 stipend ([BYU Chemistry](https://gradprogram.chem.byu.edu/graduate-program/frequently-asked-questions))
plus two semesters of tuition at $4,468 ([BYU catalog](https://catalog.byu.edu/policy/tuition-and-fees)) over 1,500
research hours (assumed), $27/h; BYU charges no fringe on student wages (its Sponsored Programs Handbook). The
technician and engineer are BLS May 2025 means for Provo-Orem-Lehi (engineering technologists $64,040; mechanical
engineers $105,770; series in the table below) plus 35 % fringe (assumed: BYU's negotiated rate agreement is a scanned
PDF with no text). Design and analysis time is the same in both labs and left out of both.

**The ledger.** The twin's own spending is split into consumables and feedstock (orders; and in the vertical lab its
in-house station fees, which are plates, argon, wire and cones) and outside fees (in the conventional lab every station
fee: BYU's core facilities, Utah, the Provo EDM service, NSL; in the vertical lab what stays outside: Mines, NSL, gas
atomization, HPC).

**Allocation** (`econ.allocate`). Each item's annual fixed cost (depreciation, service, utilities and space) is
assigned to the twin station(s) it serves; infrastructure (Shuttles, units, the floor unit, glovebox, hoods, UPSs,
couplings, cameras, the fit-out, the open floor) and the fixed staff are overhead. A station's fixed cost F is
recovered over its busy hours, like a core facility's recharge rate: a user pays F x b / max(B, u x A), where b is its
hours, B everyone's, A the station's available hours on its calendar (24/7, or 45 h a week on the day shift; the
atomizer by its start slots, 16 runs a week) and u an assumed utilization the outside users bring it to. A station no
campaign uses sells u x A of its hours outside and its idle cost joins the overhead, which is shared in proportion to
the direct cost each user absorbed. So with the campaigns alone (`utilization=None`) they absorb the whole lab, and as
outside work fills it their share falls (smoothly, as `test_outside_users_lower_the_campaigns_share_smoothly` checks).
That is the sense in which "higher utilization lowers the capex per experiment".

**Per experiment and to a target.** `cost_per_experiment(run, ...)` divides a run's costs by the alloys it
demonstrated (the twin's unit of discovery: an alloy through tensile tests for FLAIME, through tensile and 30-day
immersion for the ONR); `campaign_cost(run, campaign, target)` gives the days and money to the first alloy at or above
the target, with fixed costs accrued pro rata to time and labour to the bookings made. Three bases: **cash** (the twin's
ledger, the proposals' view), **operating** (cash plus labour, service, utilities and space) and **full** (operating plus
depreciation).

### Utilization, outside work and slowdown

`cloud.utilization(events)` reads an event log and gives each in-house station's busy hours by campaign over its
available hours. `cloud.CATALOGUE` lists the outside jobs a cloud user facility would sell, each with its station hours
and the rates published user facilities charge academic and industry users (sources in the table below; where none was
found the price is the twin's own assumption and says so). `cloud.fill(util, cap)` puts jobs into each station's idle
hours up to the cap; with `demand_h_week` it also stops at that much outside demand per instrument; the two units'
hours limit the total (9 minutes of a unit a job, ICP-MS samples in racks, assumed); each job costs a technician's
quarter hour and 10 % of its price in consumables (assumed).

Slowdown, two ways:

1. **Kingman's approximation** (J. F. C. Kingman, "The single server queue in heavy traffic", *Proc. Camb. Phil. Soc.*
   57(4), 902-904, 1961, doi:10.1017/S0305004100036094): the mean wait in queue W = rho/(1-rho) x (ca² + cs²)/2 x ts,
   in its multi-server form rho^(sqrt(2(m+1))-1) / (m(1-rho)) for m units (Hopp and Spearman's *Factory Physics*,
   after Sakasegawa). For each station the campaign visits: its own arrivals' and services' variability from the event
   log, the outside jobs as Poisson arrivals with the catalogue's durations, waits in calendar time. The campaign's
   cycle (a design's first booking to its demonstration, the median over the log) grows by the visits per
   demonstrated alloy times the added wait.
2. **The twin itself**: `cloud.external_callable` books Poisson outside jobs at every station with catalogue jobs, up to
   each level, into the facility before the campaigns run (`Twin(..., external=callable)`), and the campaigns are re-run
   with the same seeds. Outside jobs booked first behave like reserved sessions: the campaigns work around them.

### Acceleration and enhancement

Rohr et al. define the **acceleration factor** as the ratio of the number of experiments random selection and a
sequential learner need to reach the same performance, and the **enhancement factor** as the ratio of their performance
at the same budget (B. Rohr et al., "Benchmarking the acceleration of materials discovery by sequential learning",
*Chem. Sci.* 11, 2696-2706, 2020, [doi:10.1039/C9SC05999G](https://pmc.ncbi.nlm.nih.gov/articles/PMC8157525/)); their
"good" is any catalyst from the top 1 percentile, and they find AFs and EFs "up to approximately 20x" against random,
"but not yet at the orders-of-magnitude level anticipated for AI-guided discovery", and warn that "the acceleration
factors for the entire experiment workflow will be even smaller". Liang et al. use the same pair on five experimental
datasets (top-5 % fraction; EF and AF up to 8x on the crossed-barrel set, 2-4x elsewhere; GP with anisotropic kernels
and random forests comparable): Q. Liang et al., *npj Comput. Mater.* 7, 188 (2021),
[doi:10.1038/s41524-021-00656-9](https://www.nature.com/articles/s41524-021-00656-9) (its Eq. 4 prints the ratio
upside down). Adesiji, Wang, Kuo and Brown survey the field: AF(y) = n_ref / n_AL to first reach y, EF(n) =
y*_AL(n) / y*_ref(n) on best-so-far values; across 42 studies and 63 benchmarks the reported AF runs from 1.3 to 100
with a median of 6, and EF peaks at 10-20 experiments per dimension ("Benchmarking self-driving labs", *Digital
Discovery* 5(1), 14-27, 2026, [doi:10.1039/D5DD00337G](https://arxiv.org/abs/2508.06642); numbers from the arXiv
v1 full text). Volk and Abolhasani's metrics for self-driving labs (degree of autonomy, operational lifetime,
throughput, precision, material usage, accessible parameter space, optimization efficiency) do not define AF or EF, and
they found that 65 % of 17 surveyed studies made no algorithm comparison at all (*Nat. Commun.* 15, 1378, 2024,
[doi:10.1038/s41467-024-45569-5](https://www.nature.com/articles/s41467-024-45569-5)). Canty et al. ask for exactly
this kind of techno-economic comparison, and describe the centralized facility that time-shares instruments among
outside users (*Nat. Commun.* 16, 3856, 2025, [doi:10.1038/s41467-025-59231-1](https://www.nature.com/articles/s41467-025-59231-1)).

Here (`accel.py`), following Adesiji et al.: x is experiments (demonstrated alloys), days or dollars; each seed is one
twin-year; AF is the ratio of the medians over seeds of x to first reach the target. A seed that never reaches it is
censored at what it used (the horizon, its year's spend, its count), and the medians are **Kaplan-Meier medians**; if
fewer than half of an arm's seeds reach the target its median is unbounded and AF is reported as a bound (at least the
largest x the reference used over the new arm's median). CIs are percentile bootstraps over seeds, resampled within
each arm; a resample whose reference falls short gives an unbounded AF (or a zero cost ratio), which is why some lower
cost-ratio CIs read 0 %. EF is the ratio of mean best-so-far true utility at the same x. The headline compares time to
target and cost to target (operating and full; and full with outside users at the cap sharing the lab), at the state
of the art's true utility from `out/twin2/oracle.json` (AlSi10Mg for FLAIME, C95800 NAB for the ONR): "matching or
beating the state of the art".

## Results

These are a model's numbers: a synthetic truth, assumed hands-on hours and demand, prices with the sources given. They
say how the money and the time move between the two labs in this model, not what either lab will cost.

<!-- econ:begin -->
*Generated 2026-11-25 05:45 UTC from out/twin/runs/facility.jsonl, out/twin/runs/main.jsonl (proposed|random|historical|: 30; proposed|cost_aware|historical|: 30; vertical_lab|random|historical|: 10; vertical_lab|cost_aware|historical|: 10; proposed|tiered|historical|: 20), 14 event logs, and the slowdown validation in out/twin2/econ/validate.json. Targets: out/twin2/oracle.json sota_utility (flaime_al: AlSi10Mg, onr_cu: C95800 NAB).*

### Key numbers

- **Capital.** The vertical lab's equipment and fit-out: $5.40M; the conventional lab's own tools: $0.54M. A year of fixed cost (depreciation, service, utilities and space, fixed staff): $1.18M against $0.12M.
- **Utilization.** The two campaigns use 4.4% of the vertical lab's available hours (capex-weighted); the atomizer, the busiest, 37% of its start slots.
- **Cost per demonstrated alloy** (both campaigns): conventional $9.6k without capex, $11.7k with; vertical lab used by the campaigns alone $16.8k / $30.7k; vertical lab 60% utilized by outside users $4.6k / $5.9k.
- **Outside work.** At 20 h a week of outside demand per instrument (assumed), 26,983 jobs a year bring $3.08M at academic user-facility rates, $2.44M net of handling and consumables: 4.1x the lab's depreciation and 2.1x all its fixed costs. Filling every station to 60% instead (capacity, no demand limit): 106,854 jobs, $13.17M.
- **Slowdown, FLAIME.** With outside work bringing each station to 25%, 50%, 70%, 85%: cycle time x0.97/1.06/1.40/2.22 in the twin (Kingman x1.01/1.08/1.27/1.73); days to the target x1.00/1.02/1.25/1.45.
- **Slowdown, ONR.** With outside work bringing each station to 25%, 50%, 70%, 85%: cycle time x1.09/1.02/1.11/1.55 in the twin (Kingman x1.00/1.04/1.14/1.37); days to the target x0.93/0.96/1.06/1.17.
- **Headline.** FLAIME: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.4232) 1.9x faster (95% CI 1.2-unbounded) (reached in 100% of 10 seeds against 65% of 20); at 169% of the operating cost (95% CI 53%-257%); at 233% of the full cost (95% CI 0%-359%); at 50% of the full at 60% utilization cost (95% CI 0%-78%); reference: the conventional lab (tiered).
- **Headline.** ONR: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.5559) 1.3x faster (95% CI 0.91-unbounded) (reached in 90% of 10 seeds against 55% of 20); at 262% of the operating cost (95% CI 0%-334%); at 385% of the full cost (95% CI 0%-498%); at 79% of the full at 60% utilization cost (95% CI 0%-97%); reference: the conventional lab (tiered).

### The two labs

| | capex | floor | depreciation a year | service | utilities and space | fixed staff | fixed cost a year |
|---|---|---|---|---|---|---|---|
| vertical lab | $5.40M | 356 m² | $599.9k | $358.8k | $103.2k | $122.2k | $1,184.0k |
| conventional lab (its own tools) | $0.54M | 50 m² | $63.8k | $33.9k | $15.2k | $8.6k | $121.5k |

**Vertical lab: equipment** (each item's price, life, service share, kW at an assumed duty, floor; source)

| item | n | each | life | service | kW | m² | kind | source |
|---|---|---|---|---|---|---|---|---|
| Kardex Shuttle XP 500, 9.15 m (30 ft), 2450 x 864 mm trays | 2 | $210,000 | 15 y | 3% | 6.8 | 17 | list | https://www.kardex.com/en-us/blog/how-much-does-a-vertical-lift-module-cost ($6-8k per vertical foot); federal orders for 4.85-5.85 m XP 500s $103-108k (2018-19) in facility/costs_and_sizes.md (aa41d0d) |
| MiR250 + UR12e + Robotiq 2F-85 mobile manipulator, with cabinet, cameras, Class D unit, integration | 2 | $140,000 | 7 y | 5% | 0.35 | 2.4 | list | MiR250 $59-65k (US distributors, 2026), UR12e about $45k (Vention list), 2F-85 $5-6k, plus ours: facility/costs_and_sizes.md (aa41d0d) and the $200M plan's $120-160k |
| Third MiR250 unit for the floor, with a Nilfisk CFM 118EXP explosion-proof vacuum (notes/floor_cleaning.md) | 1 | $155,000 | 7 y | 5% | 0.6 | 1.2 | estimate | estimate: a unit as above plus an explosion-proof vacuum and hose reel |
| Inert PureLab HE glovebox with purifier, O2 and dew-point sensors | 1 | $55,000 | 10 y | 4% | 1.2 | 2 | procurement | National Archives, Inert PureLab HE 1250 with extension, stand, installation and training, $54,848 (2023) https://www.usaspending.gov/award/CONT_AWD_88310323P00054_8800_-NONE-_-NONE- |
| Ducted 6 ft fume hoods, installed | 2 | $35,000 | 20 y | 2% | 0.3 | 3 | estimate | estimate: $8-57k for a 6 ft hood before installation (https://www.onepointesolutions.com/blog/how-much-does-a-fume-hood-cost/) |
| UPSs on the powered trays (six PSI5-800, five GXT5LI-1500, one GXT5LI-3000; notes/ups.md) | 1 | $22,000 | 8 y | 2% | 0.25 | 0 | estimate | GXT5LI-1500 $2,707 at CDW (notes/ups.md); the rest estimated |
| CombiTac docks and tray plates on 12 powered trays and 2 bays (notes/coupling.md) | 14 | $4,000 | 10 y | 2% | 0 | 0 | estimate | estimate |
| Tray, bay and security cameras with their Pi 5s and switches (notes/security_cameras.md, notes/base_cameras.md) | 1 | $18,900 | 5 y | 0% | 0.6 | 0 | list | notes/security_cameras.md ($17,300 NDAA-compliant) + notes/base_cameras.md (two bases, $1,600) |
| Fit-out: argon and N2 lines, a Parker Balston N2 generator, chillers, power distribution, dust collection and explosion protection, network and data store | 1 | $450,000 | 20 y | 2% | 4 | 0 | estimate | estimate (the $200M plan prices the same services at $8-14M for 34 Shuttles, facility/costs_and_sizes.md (aa41d0d)) |
| AMAZEMET rePowder ultrasonic atomizer, with its optimizer and chiller | 1 | $350,000 | 10 y | 8% | 12 | 2.5 | procurement | NASA MSFC $286,720 (2023) https://www.usaspending.gov/award/CONT_AWD_80MSFC24PA004_8000_-NONE-_-NONE- ; NIST $321,595 (2024); Hochschule Aalen EUR 407,700 (2025) (facility/costs_and_sizes.md (aa41d0d)) |
| Aconity3D AconityMIDI+ laser powder-bed fusion | 1 | $700,000 | 10 y | 10% | 10 | 3 | procurement | EU awards EUR 350-456k (2019-22), Forschungszentrum Juelich EUR 675,390 (2026) https://ted.europa.eu/en/notice/-/detail/689139-2026 (facility/costs_and_sizes.md (aa41d0d)) |
| InssTek MX-Lab blown-powder DED | 1 | $300,000 | 10 y | 10% | 4.4 | 2.5 | procurement | InssTek awards: CNRS EUR 200,000 (2024) https://ted.europa.eu/en/notice/-/detail/137843-2024 , Wuppertal 'Mini-DED' EUR 241,550 (2025) https://ted.europa.eu/en/notice/-/detail/76406-2025 , Chalmers SEK 3.6M (2024) https://ted.europa.eu/en/notice/-/detail/564443-2024 ; plus shipping and installation (estimate) |
| FANUC ROBOCUT wire EDM | 1 | $230,000 | 10 y | 5% | 7.5 | 5 | procurement | NASA FANUC C600iC-ADV $220,362 (2026) https://www.usaspending.gov/award/CONT_AWD_80NSSC27P0128_8000_-NONE-_-NONE- ; $200-302k awards 2020-26 (facility/costs_and_sizes.md (aa41d0d)) |
| Instron 68FM-100 floor frame with grips and extensometer | 1 | $175,000 | 10 y | 6% | 3 | 1.5 | procurement | USAF $145,607 (2022), NASA $161,830 (2023), Navy $207,865 (2024) https://www.usaspending.gov/award/CONT_AWD_80NSSC23PA554_8000_-NONE-_-NONE- (facility/costs_and_sizes.md (aa41d0d)) |
| Instron 3119-608 environmental chamber (to 600 C) | 1 | $50,000 | 10 y | 5% | 3 | 0 | estimate | estimate: $40-60k in the $200M plan |
| ZwickRoell zwickiLine Z5.0 TN with testControl II | 1 | $35,000 | 10 y | 5% | 0.5 | 0 | assumed | assumed: no public price or award found (quote only) |
| Machining cell (PR 373): lathe, pedestal UR10e, wash and accumulator (notes/machining.md) | 1 | $275,000 | 10 y | 5% | 5 | 6 | estimate | notes/machining.md: capital about $230-320k |
| Agilent 7850 ICP-MS with SPS 4, chiller, trace-metals hood, hot block and dilutor (notes/icpms.md) | 1 | $260,000 | 10 y | 10% | 4.5 | 3 | list | 7850 $160-220k (LabX 2026 buyer's guide, notes/icpms.md); SPS 4 $12,305 list (Agilent quote in a 2017 West Virginia bid file); hood, dilutor and hot block estimated at $50k |
| Sieve cell: Retsch AS 200, tipper, wash module, downdraft enclosure | 1 | $60,000 | 10 y | 4% | 1 | 2 | estimate | AS 200 about $6.7k each with sieves (USAF, three for $19,968, 2022) https://www.usaspending.gov/award/CONT_AWD_FA860122P0079_9700_-NONE-_-NONE- ; the rest estimated ($40-80k in the $200M plan) |
| Nabertherm NAT 15/65 forced-convection furnaces (tray F) | 2 | $20,000 | 10 y | 3% | 2.8 | 0 | estimate | estimate; a Carbolite chamber furnace cost NASA $23,521 (2022) https://www.usaspending.gov/award/CONT_AWD_80NSSC22PB945_8000_-NONE-_-NONE- |
| Hitachi TM4000PlusII benchtop SEM | 1 | $100,000 | 10 y | 10% | 0.7 | 0 | procurement | USDA-ARS $98,900 with set-up and training (2021) https://www.usaspending.gov/award/CONT_AWD_12905B21P0255_12H2_-NONE-_-NONE- (facility/costs_and_sizes.md (aa41d0d)) |
| Oxford Instruments AZtecOne EDS for the TM4000 | 1 | $55,000 | 10 y | 10% | 0.4 | 0 | procurement | Oxford EDS detector: USGS $49,995 (2025) https://www.usaspending.gov/award/CONT_AWD_140G0325P0065_1434_-NONE-_-NONE- ; USAF $57,990 (2021) |
| EBSD detector on the SEM (assumed in the lab's plan) | 1 | $120,000 | 10 y | 10% | 0.2 | 0 | procurement | Oxford Symmetry S2: Army $87,430 (2021) https://www.usaspending.gov/award/CONT_AWD_W31P4Q21P0012_9700_-NONE-_-NONE- ; an Oxford EBSD added to AZtec $156,400 (2021) |
| Rigaku MiniFlex 600-C benchtop XRD with prep station | 1 | $105,000 | 10 y | 10% | 1.8 | 0 | procurement | NASA $99,465 (2023), USDA-ARS $99,444 (2024), EPA $119,968 (2020) https://www.usaspending.gov/award/CONT_AWD_80NSSC23PB731_8000_-NONE-_-NONE- (facility/costs_and_sizes.md (aa41d0d)) |
| Bruker S2 PUMA Series 2 EDXRF with XY autochanger | 1 | $120,000 | 10 y | 10% | 0.9 | 0 | procurement | Univ. Copenhagen S2 PUMA EUR 115,000 (2019) https://ted.europa.eu/en/notice/-/detail/308367-2019 ; benchtop EDXRF: Rigaku NEX CG $93,565 (2020), Malvern Epsilon 4 $144,163 (2022) |
| Malvern Mastersizer 3000 with Aero S | 1 | $110,000 | 10 y | 8% | 1.55 | 0 | procurement | Mastersizer 3000 awards $68-140k (2021-26), e.g. DLA $107,798 (2023) https://www.usaspending.gov/award/CONT_AWD_SPE8EL23F16XT_9700_SPE8EJ21D0020_9700 ; none names the Aero S |
| Mitutoyo HM-220 micro-Vickers with AVPAK | 1 | $70,000 | 10 y | 5% | 0.24 | 0 | list | HM-220 Type B $58,385 list, PC not included (https://penntoolco.com/mitutoyo-pc-driven-micro-vickers-hardness-tester-hm-220-type-b-64aab325p); Type D's automation and the PC estimated |
| KLA iMicro nanoindenter | 1 | $250,000 | 10 y | 10% | 0.3 | 0 | procurement | Navy, iMicro with iQwave2, $248,751 (2025) https://www.usaspending.gov/award/CONT_AWD_N0017325P0430_9700_-NONE-_-NONE- |
| Plastometrex PLX-Benchtop (indentation plastometry) | 1 | $130,000 | 10 y | 8% | 0.2 | 0 | procurement | NASA $127,500 (2025) https://www.usaspending.gov/award/CONT_AWD_80NSSC25PB546_8000_-NONE-_-NONE- ; Navy $160,187 (2025) |
| Keyence VHX-7000 with VHX-S750E stand and EA-300 LIBS head | 1 | $190,000 | 10 y | 5% | 0.56 | 0 | procurement | VHX-7000 $67-118k (federal awards 2020-23, e.g. USDA $118,385 https://www.usaspending.gov/award/CONT_AWD_12405B23F0240_12H2_GS07F5934R_4730 ); an EA-300-class LIBS head added to a VHX-7000 at Warsaw, PLN 385,012 (about $95k, 2025) https://ted.europa.eu/en/notice/-/detail/68926-2025 |
| LECO PX500 grinder/polisher, MX400 mounting press, sectioning saw | 1 | $55,000 | 10 y | 5% | 1.9 | 0 | procurement | PX500A2 $22,904 (Navy 2021) https://www.usaspending.gov/award/CONT_AWD_N0016421PJ124_9700_-NONE-_-NONE- ; a mounting press $15.9-22.6k (Buehler SimpliMet 4000, DLA 2024; Struers, Army 2025); the saw estimated |
| Makera Carvera desktop CNC (tray M) | 1 | $5,799 | 10 y | 3% | 0.4 | 0 | list | list $5,799 (https://www.makera.com/products/carvera.json) |
| CubXL gantry, NuVant EZstat Pro potentiostat, Opentrons OT-2 with P20 and P300, vials | 1 | $35,000 | 10 y | 3% | 0.6 | 0 | estimate | estimate: OT-2 GEN2 P300 $2,950 (opentrons.com, notes/cubxl_pipettes.md); a Gamry Interface 1010E cost the Navy $29,505 (2021); the EZstat Pro is quote only |
| Multi-doser carousel, A&D HR-202i balance, Specac Atlas Autotouch 15T with vacuum dies and an Edwards RV3 pump | 1 | $50,000 | 10 y | 3% | 1 | 0 | estimate | notes/multidoser.md (BoM $2,362); the Autotouch about EUR 37,660 at VWR (search snippet); pump and balance estimated |

**Conventional lab: equipment** (each item's price, life, service share, kW at an assumed duty, floor; source)

| item | n | each | life | service | kW | m² | kind | source |
|---|---|---|---|---|---|---|---|---|
| AMAZEMET rePowder ultrasonic atomizer, with its optimizer and chiller (the lab's own) | 1 | $350,000 | 10 y | 8% | 12 | 2.5 | procurement | NASA MSFC $286,720 (2023) https://www.usaspending.gov/award/CONT_AWD_80MSFC24PA004_8000_-NONE-_-NONE- ; NIST $321,595 (2024); Hochschule Aalen EUR 407,700 (2025) (facility/costs_and_sizes.md (aa41d0d)) |
| Retsch AS 200 sieve shaker and a set of sieves | 1 | $8,000 | 10 y | 3% | 0.1 | 0.5 | procurement | USAF, three AS 200 with sieves for $19,968 (2022) https://www.usaspending.gov/award/CONT_AWD_FA860122P0079_9700_-NONE-_-NONE- |
| Powder doser, balance and a manual hydraulic press with vacuum die | 1 | $18,000 | 10 y | 3% | 0.5 | 1 | estimate | estimate |
| Box furnace (about 1,200 C) and a forced-convection ageing oven | 1 | $30,000 | 10 y | 3% | 3 | 1 | estimate | estimate; a Carbolite chamber furnace cost NASA $23,521 (2022) |
| CubXL gantry, EZstat Pro potentiostat, OT-2 and immersion vials (DAL's own) | 1 | $35,000 | 10 y | 3% | 0.6 | 1.5 | estimate | estimate (as the vertical lab's) |
| Density balance kit and a stereo microscope | 1 | $12,000 | 10 y | 2% | 0.1 | 0.5 | estimate | estimate |
| Glovebox with purifier | 1 | $55,000 | 10 y | 4% | 1.2 | 2 | procurement | as the vertical lab's (Inert PureLab HE, $54,848) |
| Ducted fume hood | 1 | $35,000 | 20 y | 2% | 0.3 | 1.5 | estimate | estimate |

**People** (fully loaded; hourly = a year's cost over productive hours)

| role | a year | hours | per hour | source |
|---|---|---|---|---|
| grad student | $40,436 | 1,500 | $26.96 | BYU Chemistry PhD stipend 2026-27 $31,500 (https://gradprogram.chem.byu.edu/graduate-program/frequently-asked-questions) plus two semesters of graduate tuition, $4,468 each for Latter-day Saint students (https://catalog.byu.edu/policy/tuition-and-fees); BYU charges no fringe on student wages (Sponsored Programs Handbook); 1,500 research hours a year assumed |
| technician | $86,454 | 1,800 | $48.03 | BLS OEWS May 2025, engineering technologists (17-3029), Provo-Orem-Lehi, mean $64,040 (series OEUM003934000000017302904), plus 35 % fringe (assumed) |
| research engineer | $142,790 | 1,800 | $79.33 | BLS OEWS May 2025, mechanical engineers (17-2141), Provo-Orem-Lehi, mean $105,770 (series OEUM003934000000017214104), plus 35 % fringe (assumed) |
| staff scientist | $135,176 | 1,800 | $75.10 | BLS OEWS May 2025, materials engineers (17-2131), Utah, mean $100,130 (series OEUS490000000000017213104), plus 35 % fringe (assumed) |

| rate | value | source |
|---|---|---|
| kwh_usd | 0.104 | EIA Electric Power Monthly table 5.6.B, Utah commercial, Jan-Sep 2026: 10.40 c/kWh (https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_b) |
| space_om_usd_m2_yr | 215 | assumed $20/ft2/yr: EAB (Gordian 2025 data) puts a research lab's 50-year cost of ownership at $2.3M per 1,000 ft2, $46/ft2/yr, of which the building's own depreciation (below) is about $21 (https://eab.com/wp-content/uploads/2025/09/PDF-EAB-Research-True-Costs-of-Space-IG.pdf) |
| space_capex_usd_m2_yr | 222 | the $200M plan's high-bay building at $700-1,100/ft2 (published comps in facility/costs_and_sizes.md (aa41d0d)), $825/ft2 over BYU's 40-year building life (https://finserve.byu.edu/asset-capitalization-procedures) |

### Cost per experiment

An experiment is an alloy demonstrated through the whole chain (tensile for FLAIME; tensile and 30-day immersion for the ONR). Conventional: `proposed|cost_aware|historical|`; vertical: `vertical_lab|cost_aware|historical|`. Ratio of sums over the seeds.

| case | alloys | capex | service | utilities, space | labour | consumables, feedstock | outside fees | **total** |
|---|---|---|---|---|---|---|---|---|
| both: conventional, no capex | 933 | $0.0k | $1.1k | $0.5k | $2.8k | $3.3k | $1.9k | **$9.6k** |
| both: conventional, with capex | 933 | $2.1k | $1.1k | $0.5k | $2.8k | $3.3k | $1.9k | **$11.7k** |
| both: vertical lab, campaigns only, no capex | 433 | $0.0k | $8.3k | $2.4k | $2.8k | $3.2k | $0.1k | **$16.8k** |
| both: vertical lab, campaigns only, with capex | 433 | $13.9k | $8.3k | $2.4k | $2.8k | $3.2k | $0.1k | **$30.7k** |
| both: vertical lab, 60% utilized, no capex | 433 | $0.0k | $0.8k | $0.2k | $0.3k | $3.2k | $0.1k | **$4.6k** |
| both: vertical lab, 60% utilized, with capex | 433 | $1.3k | $0.8k | $0.2k | $0.3k | $3.2k | $0.1k | **$5.9k** |
| FLAIME: conventional, no capex | 830 | $0.0k | $1.1k | $0.5k | $2.7k | $2.1k | $1.8k | **$8.1k** |
| FLAIME: conventional, with capex | 830 | $1.9k | $1.1k | $0.5k | $2.7k | $2.1k | $1.8k | **$10.0k** |
| FLAIME: vertical lab, campaigns only, no capex | 391 | $0.0k | $6.5k | $1.9k | $2.3k | $2.2k | $0.0k | **$12.8k** |
| FLAIME: vertical lab, campaigns only, with capex | 391 | $11.2k | $6.5k | $1.9k | $2.3k | $2.2k | $0.0k | **$24.1k** |
| FLAIME: vertical lab, 60% utilized, no capex | 391 | $0.0k | $0.8k | $0.2k | $0.3k | $2.2k | $0.0k | **$3.4k** |
| FLAIME: vertical lab, 60% utilized, with capex | 391 | $1.3k | $0.8k | $0.2k | $0.3k | $2.2k | $0.0k | **$4.7k** |
| ONR: conventional, no capex | 103 | $0.0k | $1.4k | $0.7k | $3.4k | $13.2k | $3.1k | **$21.8k** |
| ONR: conventional, with capex | 103 | $3.2k | $1.4k | $0.7k | $3.4k | $13.2k | $3.1k | **$25.0k** |
| ONR: vertical lab, campaigns only, no capex | 42 | $0.0k | $25.1k | $6.5k | $8.1k | $12.9k | $1.1k | **$53.8k** |
| ONR: vertical lab, campaigns only, with capex | 42 | $38.3k | $25.1k | $6.5k | $8.1k | $12.9k | $1.1k | **$92.0k** |
| ONR: vertical lab, 60% utilized, no capex | 42 | $0.0k | $0.9k | $0.3k | $0.4k | $12.9k | $1.1k | **$15.5k** |
| ONR: vertical lab, 60% utilized, with capex | 42 | $1.5k | $0.9k | $0.3k | $0.4k | $12.9k | $1.1k | **$17.0k** |

### Utilization and outside work

From 4 event logs of the vertical lab (capex-weighted mean utilization by the two campaigns: 4.4%). Outside jobs fill each station's idle hours up to 60% of its available hours (capacity), or up to 20 h a week of outside demand per instrument (demand-limited; assumed: 20 h a week of outside bookings per instrument, a busy core-facility instrument).

| station | calendar | available h | campaigns' h | utilization | outside jobs a year (capacity) | revenue (capacity) | outside jobs (demand-limited) | revenue (demand-limited) | jobs |
|---|---|---|---|---|---|---|---|---|---|
| atomizer | day6, 1x | 2,086 | 777 | 37.3% | 86 | $129.3k | 86 | $129.3k | Ultrasonic atomization of a user's feedstock (a run and a full clean) |
| immersion | 24/7, 24x | 210,240 | 8,111 | 3.9% | - | - | - | - | - |
| doser | 24/7, 1x | 8,760 | 290 | 3.3% | - | - | - | - | - |
| shop | 24/7, 2x | 17,520 | 480 | 2.7% | - | - | - | - | - |
| utah_midi | 24/7, 1x | 8,760 | 201 | 2.3% | 632 | $758.2k | 130 | $156.4k | LPBF build on the MIDI (user powder) |
| byu_sem | 24/7, 1x | 8,760 | 164 | 1.9% | 3,394 | $426.4k | 695 | $87.3k | SEM/EDS session, EBSD map |
| utah_mxlab | 24/7, 1x | 8,760 | 165 | 1.9% | 1,273 | $651.6k | 261 | $133.5k | DED session (half a day) |
| sieve | 24/7, 1x | 8,760 | 100 | 1.1% | - | - | - | - | - |
| furnace | 24/7, 2x | 17,520 | 74 | 0.4% | 2,609 | $76.2k | 261 | $7.6k | Heat treatment (a furnace run) |
| psd | 24/7, 1x | 8,760 | 33 | 0.4% | 10,446 | $255.9k | 2,086 | $51.1k | Laser-diffraction PSD (dry) |
| byu_icpms | day, 1x | 2,346 | 6 | 0.2% | 14,022 | $1,261.9k | 10,429 | $938.6k | ICP-MS sample |
| density | 24/7, 1x | 8,760 | 20 | 0.2% | - | - | - | - | - |
| edm | 24/7, 1x | 8,760 | 19 | 0.2% | 5,237 | $785.6k | 1,043 | $156.4k | Wire-EDM cutting (a plate of specimens) |
| cubxl | 24/7, 1x | 8,760 | 14 | 0.2% | 4,368 | $262.1k | 869 | $52.1k | Corrosion screen (OCP, LPR, EIS, CP) |
| tensile | 24/7, 2x | 17,520 | 22 | 0.1% | 17,483 | $3,356.8k | 1,738 | $333.7k | Tensile test, 3 sub-size bars |
| hardness | 24/7, 1x | 8,760 | 0 | 0.0% | 10,512 | $149.3k | 2,086 | $29.6k | Micro-Vickers hardness map |
| nanoindent | 24/7, 1x | 8,760 | 0 | 0.0% | 5,256 | $404.7k | 1,043 | $80.3k | Nanoindentation map |
| pip | 24/7, 1x | 8,760 | 0 | 0.0% | 10,512 | $2,628.0k | 2,086 | $521.4k | PIP test (stress-strain curve by indentation) |
| prep | 24/7, 1x | 8,760 | 0 | 0.0% | - | - | - | - | - |
| tensile_hot | 24/7, 1x | 8,760 | 0 | 0.0% | 3,504 | $1,345.5k | 695 | $267.0k | Elevated-temperature tensile test |
| xrd | 24/7, 1x | 8,760 | 0 | 0.0% | 7,008 | $341.6k | 1,390 | $67.8k | Powder XRD scan |
| xrf | 24/7, 1x | 8,760 | 0 | 0.0% | 10,512 | $331.9k | 2,086 | $65.8k | XRF sample |

| | outside jobs a year | revenue | net of handling and consumables | x depreciation | x all fixed costs |
|---|---|---|---|---|---|
| capacity (60% cap) | 106,854 | $13.17M | $10.56M | 17.6 | 8.9 |
| demand-limited (20 h a week), academic rates | 26,983 | $3.08M | $2.44M | 4.1 | 2.1 |
| demand-limited, industry rates | 26,983 | $5.52M | $4.64M | 7.7 | 3.9 |
| demand 5 h a week, academic | 6,759 | $0.79M | $0.63M | 1.0 | 0.5 |
| demand 10 h a week, academic | 13,519 | $1.58M | $1.26M | 2.1 | 1.1 |
| demand 20 h a week, academic | 26,983 | $3.08M | $2.44M | 4.1 | 2.1 |
| demand 40 h a week, academic | 47,045 | $5.41M | $4.30M | 7.2 | 3.6 |

**Value per capex dollar.** The campaigns demonstrate 43.3 alloys a year in the vertical lab; at the conventional lab's full cost of $11.7k an alloy that is 0.09 dollars of experiments a year per dollar of capex. With demand-limited outside work it is 0.55, and 2.05 if the capacity sells.

### Slowdown

Outside jobs booked into the twin's facility before the campaigns run (`Twin(..., external=...)`, hook: twin), 4 seeds a level, 20 twin-years in all, against Kingman's estimate on the same baseline.

| campaign | outside work up to | twin: cycle time | twin: days to target (KM) | Kingman | alloys demonstrated | best |
|---|---|---|---|---|---|---|
| flaime_al | 0% | 1.00x | 1.00x | 1.00x | 42.8 | 0.698 |
| flaime_al | 25% | 0.97x | 1.00x | 1.01x | 41.0 | 0.691 |
| flaime_al | 50% | 1.06x | 1.02x | 1.08x | 38.5 | 0.708 |
| flaime_al | 70% | 1.40x | 1.25x | 1.27x | 32.2 | 0.675 |
| flaime_al | 85% | 2.22x | 1.45x | 1.73x | 26.2 | 0.677 |
| onr_cu | 0% | 1.00x | 1.00x | 1.00x | 6.0 | 0.673 |
| onr_cu | 25% | 1.09x | 0.93x | 1.00x | 5.5 | 0.673 |
| onr_cu | 50% | 1.02x | 0.96x | 1.04x | 5.5 | 0.634 |
| onr_cu | 70% | 1.11x | 1.06x | 1.14x | 6.0 | 0.633 |
| onr_cu | 85% | 1.55x | 1.17x | 1.37x | 4.5 | 0.601 |

### Acceleration and cost to target

| comparison | campaign | target | AF in days (95% CI) | AF in experiments | reached (new / ref) | operating cost ratio | full cost ratio | full, outside users at the cap |
|---|---|---|---|---|---|---|---|---|
| tiered on the partners -> cost_aware in the vertical lab | flaime_al | 0.423 | 1.90 (1.16-unbounded) | 0.59 (0.22-8.29) | 100% / 65% | 169% | 233% | 50% |
| tiered on the partners -> cost_aware in the vertical lab | onr_cu | 0.556 | 1.28 (0.91-unbounded) | 1.50 (0.50-unbounded) | 90% / 55% | 262% | 385% | 79% |
| random on the partners -> cost_aware in the vertical lab | flaime_al | 0.423 | >= 3.9 | >= 6.1 | 100% / 13% | <= 55% | <= 83% | <= 18% |
| random on the partners -> cost_aware in the vertical lab | onr_cu | 0.556 | >= 1.5 | >= 2.0 | 90% / 23% | <= 209% | <= 307% | <= 63% |
| cost_aware on the partners -> cost_aware in the vertical lab | flaime_al | 0.423 | 1.15 (0.77-1.45) | 0.71 (0.35-2.40) | 100% / 93% | 175% | 267% | 58% |
| cost_aware on the partners -> cost_aware in the vertical lab | onr_cu | 0.556 | 1.24 (0.96-unbounded) | 1.50 (0.67-2.00) | 90% / 63% | 271% | 395% | 82% |

Headlines:

- FLAIME: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.4232) 1.9x faster (95% CI 1.2-unbounded) (reached in 100% of 10 seeds against 65% of 20); at 169% of the operating cost (95% CI 53%-257%); at 233% of the full cost (95% CI 0%-359%); at 50% of the full at 60% utilization cost (95% CI 0%-78%); reference: the conventional lab (tiered).
- ONR: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.5559) 1.3x faster (95% CI 0.91-unbounded) (reached in 90% of 10 seeds against 55% of 20); at 262% of the operating cost (95% CI 0%-334%); at 385% of the full cost (95% CI 0%-498%); at 79% of the full at 60% utilization cost (95% CI 0%-97%); reference: the conventional lab (tiered).
- FLAIME: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.4232) at least 3.9x faster: the conventional lab (random) reached it in fewer than half its seeds within the horizon (reached in 100% of 10 seeds against 13% of 30); at most 55% of the operating cost; at most 83% of the full cost; at most 18% of the full at 60% utilization cost; reference: the conventional lab (random).
- ONR: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.5559) at least 1.5x faster: the conventional lab (random) reached it in fewer than half its seeds within the horizon (reached in 90% of 10 seeds against 23% of 30); at most 209% of the operating cost; at most 307% of the full cost; at most 63% of the full at 60% utilization cost; reference: the conventional lab (random).
- FLAIME: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.4232) 1.1x faster (95% CI 0.77-1.5) (reached in 100% of 10 seeds against 93% of 30); at 175% of the operating cost (95% CI 144%-259%); at 267% of the full cost (95% CI 220%-397%); at 58% of the full at 60% utilization cost (95% CI 46%-84%); reference: the conventional lab (cost_aware).
- ONR: in this simulated benchmark, the vertical lab (cost_aware) reached the target (0.5559) 1.2x faster (95% CI 0.96-unbounded) (reached in 90% of 10 seeds against 63% of 30); at 271% of the operating cost (95% CI 0%-338%); at 395% of the full cost (95% CI 0%-492%); at 82% of the full at 60% utilization cost (95% CI 0%-99%); reference: the conventional lab (cost_aware).

<!-- econ:end -->

## What the numbers say

The block above is regenerated with every `python3 -m twin.econ all`; this is how to read it.

1. **Alone, the vertical lab is the expensive way to run two campaigns.** Its equipment costs ten times the
   conventional lab's own tools, and with service, power, space and its fixed staff it costs about ten times as much a
   year; the two campaigns, held to their budgets and work-in-progress caps, use a few percent of its hours (the
   atomizer, held to its start slots and the day shift's crucible, is the exception). So a demonstrated alloy costs
   more in the vertical lab when the campaigns carry it alone, even though no student's hands are on the work.
2. **The same lab, filled, is the cheaper one.** Charged the way a core facility charges, depreciation and service per
   alloy fall as 1/utilization once outside work passes the campaigns' own use; at the cap the vertical lab's full cost
   per alloy falls below the conventional lab's. What is left is mostly feedstock and consumables, the same in both.
3. **Outside work could pay for the lab, if the demand exists.** At published academic user-facility rates even a
   modest assumed demand covers the depreciation several times over; the rates are high per instrument-hour against a
   benchtop instrument's depreciation, which is how core facilities fund their staff. The demand is the unknown.
4. **The slowdown is mild until about 70 % and steep above it.** Kingman's estimate follows the twin to 70 % and
   underestimates it at 85 %, where outside jobs booked first act like reserved sessions and take the atomizer's slots.
   Days to target grow less than cycle time: the campaigns keep many experiments in flight.
5. **Acceleration is mostly the policy against weak baselines, and the lab's own share is modest.** Against the
   conventional lab running the same policy the vertical lab is a little faster; against random or the screening
   funnel it reaches the state of the art in seeds where they never do within the horizon, so only bounds can be given.

## Limits

* **Demand is not modelled.** The capacity figures assume outside users take every idle hour up to the cap; the
  demand-limited figures assume 20 h a week per instrument (and the sensitivity table 5-40). Neither is a market study.
* **The conventional lab's free stations.** The twin leaves BYU's Instron frames, hardness testers and metallography
  free to the conventional lab; they carry no charge here either. BYU's internal core-facility rates are subsidised
  (BYU's EM facility puts its operating cost at about $300/h against $30-105/h charged), so outside fees understate the
  full cost of the conventional route.
* **Hands-on hours are assumed**, per booking, from the twin's step times; nobody has timed the conventional workflow.
  They are priced at a BYU student's cost ($27/h), which is low: a research assistant at a university charging full
  tuition and fringe costs two to three times as much, which would raise the conventional lab's labour line by as much.
* **The building** is charged at the $200M plan's high-bay cost per square foot whether or not the pilot cell sits in
  an existing BYU building; dropping it lowers the vertical lab's annual cost by about 7 %.
* **Unpriced items**: the zwickiLine Z5.0 (no award or list price found), the MX-Lab's installation, the fit-out, the
  couplings, the hoods, the CubXL bundle and the EBSD detector's fit to a benchtop SEM are estimates or assumptions.
* **Service contracts** are a share of price, not quotes; no vendor has quoted the lab.
* **Robots as a resource**: the twin does not schedule the two units; their hours only cap the outside work here.
* **Round 1 inputs**: until the lead's round-2 runs land, the cost and acceleration numbers use round 1's `facility`
  and `main` experiments (no BOFN; the cost-aware policy stands in), while the utilization and slowdown come from
  round-2 engine event logs. `python3 -m twin.econ all` picks up round 2 automatically.

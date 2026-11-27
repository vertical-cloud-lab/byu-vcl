# Digital twin, round 6: money tracked, the used market, crucibles, the HPC at scale (the engine and the grid)

Sterling, on PR 405 (2026-11-27 17:46 UTC): "Twin round 6. Branch from this PR's head … This job builds and validates
the engine and the grid. Don't run the full grid here." Six changes: money isn't limited for either lab, it's tracked;
used equipment from the real market (issue 424); pre-coated crucibles modelled explicitly; far more HPC candidates
than 4×; BOFN and pKGFN rows that reproduce on any CPU; copper's optimizers without the cap on blend screens. Every
sensitivity is run with BOFN and pKGFN as well as the cheap policies. Everything else is round 5's
([`twin_round5.md`](twin_round5.md)).

This round's job built the engine and the grid and checked them. **It made no row of the grid.** The grid runs in
compute slices afterwards (section 8). Everything here is simulated: synthetic truths, simulated instruments,
assumed prices, capacities, lead times and schedules.

**In short.**

<!-- SUMMARY -->

## 1. Money tracked, not limited

Every rule that stopped spending is gone, in both labs and for every policy (`twin/round6.py` `GATES_REMOVED`, each
with where it lived):

| Rule removed | Where it was |
|---|---|
| the budget: an action dearer than the money left was refused | `Campaign.submit3` |
| the spending plan (round 5 had already set it to the whole budget) | `Campaign.submit3`, `Campaign.plan` |
| round 4's reserve for the coming week's standing partner slots | `Campaign4.reserve` |
| round 5's money kept for the work in progress: a new composition waited until the lots already made could be paid through their next steps | `Campaign5.wip_reserve` |
| the stock heuristic's three money rules (no item stocked beyond the days the money lasts; never the money kept for work in progress; stock at most 20 % of the money left) | `Campaign5._reorder` |
| the run loop: a campaign with no money was not asked, and after a refusal the rest of a decision's actions were held back | `Twin5.run_async` |
| the policies' check that money is left for a new design ($1,500 aluminium, $3,000 copper) | `policies2.Base2.can_start_new` |
| BOFN's and pKGFN's cap on copper's blend screens (a quarter of the money spent plus $2,500) | `net3.Net3._screen_share_ok` |

What still limits work is what limits it in a lab (`GATES_KEPT`): stations, robots, people and their hours, a
crucible for each atomizer run, stock and its lead times, decision windows and sign-offs (round 5), and round 4's
WIP limit before the first fabrication step (it counts lots against two weeks of that step's capacity, not dollars).

**Tracked instead.** Every dollar a campaign spends is booked with a category as it is spent (`Campaign6.charge`,
`_route`): stock ordered into the stores, consumables (the lab's own stations' fees and each action's supplies),
partners and services (partners' sessions, BYU core facilities, outside services), and the scale-up stages after
discovery (a line of their own, as in rounds 4-5). The lab's own money is booked on a cash basis
(`Twin6._spend_events`): capital bought new, capital bought used (with any refurbishment), the facility (the space's
fit-out, then each item's service contract, utilities and floor space from the day it is online) and labour (the fixed
staff from day 0, and hands-on hours at the student rate). A test checks that the categories add up to the ledger,
dollar for dollar. Each row reports:

* cumulative spend by week for each campaign and for the lab, by category (`r6.spend`);
* spend to each target, campaign money alone and with the lab's fixed costs shared 2 : 1 between the campaigns as
  round 5's budgets were (`campaigns.<k>.spend_to_target`);
* per new alloy tested, without and with fixed costs (`campaigns.<k>.per_alloy`).

Round 5's budgets stay in the rows as a reference line (`reference_usd`), not a limit. All the money is still there at
t = 0, the facility is ready between day 60 and day 100 (drawn per seed), and equipment is ordered on day 0 and
installed once the space is ready.

## 2. Used equipment from the market

The engine reads the per-station summary of issue 424's survey, `out/twin6/market/summary.csv`, written by that
branch's `twin/market6.py` (`round6.load_market`, `used_params`, `build_schedule6`). For each station the survey
lists, its own numbers replace round 5's stand-ins field by field: whether a used market exists and is cheaper than
new (`used_ok`, replacing round 5's `USED_OK`), the delivered price as a fraction of new (`price_frac`), the lead from
BYU's purchase order to the unit on site and its spread (`lead_w`, `lead_sigma`), the chance a unit arrives faulty or
needs refurbishment (`p_fault`), the refurbishment's time, spread and cost (`refurb_w`, `refurb_sigma`,
`refurb_frac`), and the extra commissioning a used unit needs (`extra_com_w`). A field the survey leaves empty keeps
round 5's number. The survey writes a row for each station and, for a station that is several machines (the
machining cell, the prep line), one for each machine too; only the station's own row is read, since it already
combines its machines. Round 5's rule then decides: buy used when that saves at least 14 expected days against the
space's readiness, with the fault risk priced in. Every row records where its numbers came from
(`r6.used.source`) and the summary's sha256 (`r6.used.file_sha256`), so rows made before and after the file lands
can't be mixed by accident.

**The survey landed (PR 429, merged here on 2026-11-27) and is wired in.** Its per-station summary,
[`out/twin6/market/summary.csv`](../out/twin6/market/summary.csv), comes from 1,181 listings on LabX, Machinio,
Machineseeker, Exapro, GovDeals, AllSurplus, Public Surplus, DOTmed, Federal Equipment and Marshall Scientific
([its README](../out/twin6/market/README.md)). eBay, BidSpotter, EquipNet and Surplus Record blocked or challenged
the survey's browser, so they're not in it. Every row of the grid records the file's sha256 (`51ba653a…`).

**One fix was needed to read it.** A station bought partly used is on site when its last part is. The survey gives
that lead as `lead_w_with_new_parts`: the later of the used parts' lead (`lead_w`) and the new parts' lead. The
engine read `lead_w` alone. That would have had the doser on site in 2 weeks while its carousel, bought new, takes
14, and the machining cell in 3 while its baths, dryer and integration take 20. The same applied to the floor unit,
the mobile units, the ICP-MS, the sieve cell and the VHX. The engine now reads `lead_w_with_new_parts` where the survey
gives it, as the survey's own `market6.used_params` does. A test checks that the two readers agree on all eight
numbers and `used_ok` for every station the lab builds
(`test_engine_reads_the_committed_survey_as_market6_does`).

**What it changes** ([`out/twin6/checks/used_market.md`](../out/twin6/checks/used_market.md), the 16 seeds' build-out
both ways, made by `checks/used_market.py`):

* **Two stations are bought used: the EDM and the Instron frame**, in every seed. A used unit saves 32 and 21.5
  expected days, at 20 % and 12 % of the new price delivered, against round 5's stand-in of 45 %. Each arrives
  faulty in some seeds (the EDM in 5 of 16, the Instron in 2), at 31 % and 29 % odds from the listings' mix of
  conditions.
* **The environmental chamber and the nanoindenter are now bought new.** Round 5's stand-ins bought both used. The
  survey found 4 and 3 listings, too few to count on (`thin`), so they arrive after their 16-week leads.
* **Every other station with a real market saves fewer than 14 expected days**, round 5's threshold, so it's bought
  new. Most of these have leads of 8-12 weeks that the space's readiness (day 60-100) hides. The rest are partly
  used and wait for their new parts anyway.
* **The cell is integrated on the same day in all 16 seeds** (median day 201), and the last station is online on
  the same day (median 247). Capital is $4.68M rather than $4.66M (medians).

**Stations the lab buys with no used market it would buy from** (`round6.no_used_market()`; every row records each
station's verdict in `r6.used.stations`):

| Station | Survey's verdict | Listings |
|---|---|---|
| Plastometrex PLX-Benchtop (PIP) | none: made since 2019, no used unit found | 0 |
| KLA iMicro nanoindenter | thin | 3 |
| Instron 3119-608 environmental chamber | thin | 4 |
| Makera Carvera desktop CNC | none | 0 |
| Aconity3D AconityMIDI+ LPBF | none like for like (82 other LPBF machines listed) | 82 |
| InssTek MX-Lab DED | none like for like | 4 |
| Kardex Shuttle XP 500 | thin: common in Europe, prices on request, almost none in the US | 35 |
| EBSD detector | thin | 2 |
| AZtecOne EDS for the TM4000 | thin | 1 |
| Cameras, UPSs | not surveyed: commodity, bought new | 0 |

The fit-out (`services`) is building work, and the conventional lab buys nothing: it works with the equipment it
has. Its stations are in the survey for the economics only.

## 3. Pre-coated crucibles

Round 5 derived the automated atomizer's cycle (about 2.2 h per aluminium composition) assuming spare pre-coated
crucibles: each is out of service about 14-16 h for its clean, BN respray and overnight dry, so a 2-3 h cycle needs
6-8 per alloy family in rotation, and with one per family the lab manages about one run a day. Round 6 models them
(`CRUCIBLES`, `CruciblePool`, `ResourceAtom6`):

* **How many.** The automated lab: as many as keep the atomizer at its cycle, (run + 15 h) / run rounded up: 8 for
  aluminium (2.2 h) and 6 for copper (3.4 h). The conventional lab: 3 a family (two attended starts a day and a
  spare). Both start with one a family, what the lab has now.
* **Bought at t = 0**, after BYU's two-week purchase order, at a lead drawn per seed and family (a 21-day median, a
  geometric spread of 1.8), paid on delivery as a stores order.
* **Price and lead** (stand-ins until a vendor quotes for the rePOWDER's own geometry; `CRUCIBLE_SOURCE`): no vendor
  sells a factory BN-coated graphite crucible of this size, and AMAZEMET's spares have no public price or lead time.
  A stock graphite bottom-pour crucible of about 200 mL with its sealing rod is $198 (MTI EQ-GR6083-LD), plain
  220-250 mL crucibles $90-170; coated in house with ZYP BN aerosol ($45 a can, about $1 a coat). Stock items ship in
  1-5 working days; graphite machined to print takes 7-12 days at one shop and 6-8 weeks at others. **$200 each, 21
  days.** Whether a third-party crucible fits the rePOWDER is unverified.
* **Turnaround and life.** After each run a crucible is out of service 15 h (cleaned, resprayed, dried), whoever does
  it. Each melt wears 1/12 of an aluminium crucible and 1/6 of a copper one (the twin's rates since round 1), drawn
  from the stores, which reorder them like any other item.
* **The atomizer's rate.** A run needs a crucible of its family. Until the pool arrives there is one a family, about
  one run a day; after it arrives, and once the cell is integrated, the automated atomizer runs at the derived cycle.
  Before the cell, people run it, at most 8 a week, as in round 5.

**The day the derived cycle starts**, per seed (`r6.crucibles.families.<k>.derived_cycle_start_d`; computed here from
each seed's build-out and crucible draws, the same as the runs will record):

| Seed | Space ready | Cell integrated | Aluminium's pool in | Copper's pool in | Derived cycle starts | With the pool 240 days late (Al / Cu) |
|---|---|---|---|---|---|---|
| 0 | 67 | 212 | 43 | 22 | 212 (the cell) | 283 / 262 |
| 1 | 67 | 161 | 32 | 50 | 161 (the cell) | 272 / 290 |
| 2 | 90 | 206 | 43 | 31 | 206 (the cell) | 283 / 271 |
| 3 | 77 | 171 | 63 | 32 | 171 (the cell) | 303 / 272 |
| 4 | 77 | 201 | 62 | 76 | 201 (the cell) | 302 / 316 |
| 5 | 88 | 248 | 51 | 43 | 248 (the cell) | 291 / 283 |
| 6 | 65 | 194 | 35 | 64 | 194 (the cell) | 275 / 304 |
| 7 | 89 | 246 | 49 | 20 | 246 (the cell) | 289 / 260 |
| 8 | 61 | 200 | 60 | 55 | 200 (the cell) | 300 / 295 |
| 9 | 64 | 233 | 25 | 27 | 233 (the cell) | 265 / 267 |
| 10 | 100 | 191 | 34 | 28 | 191 (the cell) | 274 / 268 |
| 11 | 84 | 194 | 140 | 40 | 194 (the cell) | 380 / 280 |
| 12 | 91 | 208 | 75 | 36 | 208 (the cell) | 315 / 276 |
| 13 | 78 | 191 | 41 | 33 | 191 (the cell) | 281 / 273 |
| 14 | 100 | 212 | 32 | 41 | 212 (the cell) | 272 / 281 |
| 15 | 90 | 185 | 34 | 31 | 185 (the cell) | 274 / 271 |

Days from t = 0. At the nominal lead the pools are in on day 20-140, months before the cell (day 161-248), so **the cell, not the crucibles, sets the day the derived cycle starts in every seed**. The crucibles bind only when they are late: in the grid's `crucibles_late` arms the pool arrives 240 days after its lead time, on day 260-380, and the automated atomizer runs at one crucible a family, about one run a day each, from the cell until then.

## 4. The HPC stream at scale

Round 5's stream (Sterling's note 4): a stand-in allocation of 256 cores at 0.05 core-hours a candidate evaluates
about 123,000 candidates a day for each campaign (89.7 million over the two years), outside the money and outside
the acquisition's cost. The policies saw 64 new ones a day, as open-CALPHAD results, with the newest 128 unexplored
kept visible; round 5's `hpc_more` showed 4× as many changed no target with the cheap policies.

**Round 6 scales what the policies see** (`hpc.scale`: 64 × scale new candidates a day, the newest 128 × scale
kept), without keeping every candidate ever simulated in memory (`Twin6._stream_tick`): a candidate that has left the
visible pool with nothing started on it is dropped a day later and can be rebuilt from its batch's seed if a policy
still asks for it; one a policy starts stays visible with its simulation. At large pools, BOFN and pKGFN value at
most 384 free candidates a decision: the 288 best by the funnel's own screen and proxy (what round 3's networks
already use as their prior before they have data) and 96 drawn at random from the rest (`opt/net6.py`).

**What uses the stream.** The heuristic on aluminium doesn't: it starts from the reference alloys and then mutates
the best alloy measured, so the stream's scale reaches it only through the stations it shares with copper. The funnel
on copper ranks every visible candidate by its proxy whenever it rebuilds its shortlist. BOFN and pKGFN draw every new
design from the visible pool.

**What a candidate costs the simulation.** About 0.25 ms each to sample, simulate and index (profiled at 16×, 60
days: `Space.sample` 87 µs, the open-CALPHAD Scheil model 65-125 µs, `design_id` 30 µs), plus what the policies spend
looking at a larger pool. At the allocation's full capacity, about 123,000 a day for each campaign, the stream alone
would take about 60 s per simulated day: some 12 hours per two-year run, for 1,392 runs. **The full capacity can't be
simulated with this stream.** What would make it possible: a vectorized sampler and Scheil model for the stream
(both are per-candidate Python today), or a library of candidates simulated once and shared by every run, with each
day's visible pool drawn as the top of a random draw of the day's size (a sketch, not built).

**The pilot** ([`out/twin6/checks/hpc_pilot.md`](../out/twin6/checks/hpc_pilot.md), `hpc_pilot.jsonl`, made by
`out/twin6/checks/hpc_pilot.py`): the stocked arm of each lab, the same seeds at each scale, 365 days for the
heuristic and the funnel and 300 days for BOFN in the automated lab. A few seeds can show only large changes: a run's
path parts from the same seed's at another scale as soon as one decision differs.

<!-- PILOT_TABLE -->

**What it shows.**

* **The heuristic on aluminium doesn't change with scale** beyond the seed-to-seed spread, as expected: it never
  looks at the stream.
* **The conventional lab's copper does.** With the funnel it reached copper's first target within the year in 0 of 4
  seeds at 1× and 4×, 1 of 4 at 16× and 2 of 2 at 64×, and its best new copper alloy rose from 0.38 to 0.67 (medians).
  That lab tests about two copper alloys a year (Utah's monthly MX-Lab session), so which two it picks matters most,
  and a larger pool gives its proxy better ones to pick. The automated lab tests about 20 a year, and its copper
  outcomes don't move with scale in four seeds.
* **So outcomes have not stopped changing at 64×**, and the effect is larger in the conventional lab than in the
  automated one: a comparison at a smaller scale would favour the automated lab.
* **The stream's cost is linear in scale:** about 0.035 s of runtime per simulated day per unit of scale with the
  heuristic and the funnel, and about 0.05 with BOFN (`smoke.json` `stream_cost`, the median over the pilot's pairs
  of runs that differ only in scale). Over two years that is about +80 s at 4×, +400 s at 16×, +1,650 s at 64× and
  +6,500 s at 256× with the cheap policies; +580, +2,300 and +9,300 s at 16×, 64× and 256× with BOFN or pKGFN.

**The main arms run at 64×** (`bench6.HPC_SCALE`): 4,096 new candidates a day for each campaign, the newest 8,192
visible. It is the largest scale at which a two-year run stays workable: about 30 minutes with the heuristic and the
funnel and 1-1.5 hours with BOFN or pKGFN in the automated lab. At 256× the stream alone takes about two hours a
run, and the grid would take about three times as long. The grid's `hpc` experiment runs the stocked arms at 1×, 4×
and 16× (tier 2), and `hpc256` at 256× (tier 5, last), each with all three policies and 16 seeds, so where outcomes
stop changing is measured on the grid's own seeds. A one-line change (`HPC_SCALE = 16`) gives a grid about a third
cheaper, at the cost of the conventional lab's copper.

## 5. BOFN and pKGFN rows that reproduce on any CPU

Round 5 found that its BOFN and pKGFN rows, made under `TWIN_PIN=avx2`, reran bit for bit between the EPYC 9V45 and
9V74 and not on an EPYC 7763 or a Xeon 6975P-C; the heuristic's and the funnel's rows reran everywhere. Three
libraries still chose their arithmetic by the CPU (details and numbers in
[`out/twin6/checks/pin_search/`](../out/twin6/checks/pin_search/README.md)):

1. **numpy's own float64 kernels.** numpy dispatches `exp`, `log`, `power`, `expm1` and `log1p` to AVX-512 code on a
   CPU that has it, and to AVX2 code otherwise. The two disagree in the last bit for 4.6 % of `exp`'s results and
   5.3 % of `power`'s. The network policies compute their utilities with these; the heuristic, the funnel, the truth
   and the instruments use Python's `math`, which is why only BOFN's and pKGFN's rows differed. The EPYC 7763 has no
   AVX-512.
2. **MKL inside torch** takes a different code branch on a non-Intel CPU whatever `MKL_ENABLE_INSTRUCTIONS` says,
   and the two branches differ in matrix products, Cholesky factors, triangular solves and the vector math behind
   `torch.exp`, `erf` and `tanh`. The Xeon is the Intel CPU.
3. **OpenBLAS's blocking** (numpy's and scipy's). `OPENBLAS_CORETYPE=Haswell` fixes the kernels, not how a product is
   blocked, which OpenBLAS sets from the L2 cache it finds. At exactly 1,024 KB, the EPYC 9V45's and 9V74's, it blocks
   differently from every other size tried, so products and factorizations of size 300 or so differ. Under the Haswell
   kernels that blocking also crashes numpy on a 64 × 384 by 384 × 64 product. This one was found in this job.

**`TWIN_PIN=portable`** (`twin/repro.py`) is round 5's `avx2` (OpenBLAS's Haswell kernels, torch's AVX2 kernels,
MKL capped at AVX2, one thread everywhere, `PYTHONHASHSEED=0`) plus `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,
AVX512_SPR` (numpy's AVX2 kernels on every CPU), `MKL_CBWR=COMPATIBLE` with `MKL_DYNAMIC` and `OMP_DYNAMIC` off
(MKL's conditional numerical reproducibility, the one branch Intel documents for all Intel and compatible CPUs),
`OPENBLAS_L2_SIZE=256` (Haswell's own L2) and oneDNN capped at AVX2 (a precaution). `bench6` and `gpcheck6` set it
themselves and refuse to make kept rows under any other. Each row records what is in force, as the libraries
themselves report it: numpy's enabled kernels, MKL's branch, CNR state and threads, OpenBLAS's kernels and threads,
torch's capability and threads (`env`); `repro.problems6` lists anything that isn't.

**The GP determinism check** (`python -m twin.gpcheck6`, `twin/gpcheck6.py`; the reference is
[`out/twin6/checks/gpcheck.json`](../out/twin6/checks/gpcheck.json), made on this job's EPYC 9V74 from `330d5aa` with a
clean `twin/`). Each part runs in a fresh interpreter under the pin, with every variable that could steer the
libraries removed first:

* **a kernel probe**: fixed inputs through every numerical building block the network policies use, hashed in seven
  groups: numpy's math, its reductions and BLAS, scipy (its own OpenBLAS, L-BFGS-B, special functions), torch's math
  (MKL's vector math and ATen) and BLAS and LAPACK (at the sizes a GP fit uses), and whole GP fits (BoTorch's
  `SingleTaskGP`, marginal likelihood, gradient, fitted hyperparameters, posterior). A group that differs names the
  library that still follows the CPU;
* **three short runs on the grid's engine**: BOFN and pKGFN in the conventional lab (220 days), and BOFN in the
  automated lab (200 days), at a pool of 4× round 5's candidates, so that BOFN's cut of a large pool runs too. Each
  is hashed three ways: the row (apart from timing and provenance), the event log, and **the GP state**, every node's
  fitted hyperparameters and scaling and the policy's last posterior means as exact floats. The GP state is the
  sensitive part. In a 150-day run a last-bit difference in a fit changes the GP state at once and no decision yet,
  so a check of the row and log alone would pass on a machine whose two-year rows then differ.

It takes about 2 minutes with four workers (`TWIN_WORKERS=4`), 5 with one. Exit 0: every probe group and every run's
row, log and GP state match. Exit 1: something differs (it prints what). Exit 2: the pin isn't in force. Each slice
runs it first and commits its record (`out/twin6/slices/gpcheck-slice-<k>.json`), so the slices' mix of CPUs is the
test.

**What was shown here, and what wasn't.** This runner is an AMD EPYC 9V74. For Intel CPUs, Intel's Software
Development Emulator (SDE 9.58) runs the same binaries while presenting another CPU's identity and instruction set:
`-hsw` (Haswell, AVX2 only, 256 KB of L2) and `-gnr` (Granite Rapids, the Xeon 6975P-C's family).

* **Before the OpenBLAS fix** (the first attempt's measurements, [`pin_search/`](../out/twin6/checks/pin_search/README.md)):
  150-day automated-lab BOFN runs had the same rows and event logs under every setting (no decision had changed
  yet), but their GP states told them apart. Under `avx2` the native EPYC, emulated Haswell and emulated Granite
  Rapids gave three different GP states; with numpy's kernels and MKL's branch pinned, all three gave the same. The
  kernel probe still differed in numpy's BLAS and in scipy between the native EPYC and both emulated CPUs, which
  agreed with each other: that was OpenBLAS's blocking.
* **With the full pin, on this runner**: the probe matches the emulated Haswell's and Granite Rapids' in all seven
  groups.
* **The whole check under emulated Granite Rapids** (`TWIN_GPCHECK_WRAP="sde64 -gnr --" python -m twin.gpcheck6`):
  **it matches the reference in every part**, the seven probe groups and all three runs' rows, event logs and GP
  states ([`gpcheck_sde_gnr.json`](../out/twin6/checks/gpcheck_sde_gnr.json)). Under the emulator it took 29 minutes.

The emulator presents another CPU's identity, instruction set and cache sizes to the libraries, not another chip's
silicon. A real Intel runner and a real EPYC 7763 are the test that counts, and the slices will be it. If a slice's
check fails, its record names the group that differs.

**Rows made under `portable` are round 6's own**: not round 5's, not round 3's. Round 5's rows were made under
`avx2` and still reproduce under `avx2` on the CPUs they did.

## 6. Copper's optimizers without the cap on blend screens

Round 5 named the optimizers' cap on copper's blend screens (a quarter of the money spent so far plus $2,500;
`net3.Net3._screen_share_ok`) as the likely cause of copper's stretches with free capacity and nothing started, and
didn't confirm it. Round 6 removes the cap with the other money rules (section 1).

**The check** ([`out/twin6/checks/copper_idle.md`](../out/twin6/checks/copper_idle.md), made by
`out/twin6/checks/copper_idle.py`): the arms and seeds in which round 5 flagged a copper stretch, rerun on round 6's
engine for the days that cover them, each twice: with round 6's policy (no cap), and with the cap put back and
nothing else changed (`bofn3cap`, `pkgfn3cap` in `twin/opt/net6.py`, check-only variants that the grid never runs).
Round 6 also changed the rule that flags a stretch. Round 5 called the first fabrication step free when it was busy
less than half of every hour of the stretch, which counts the weeks between a partner's monthly sessions as free
capacity; round 6 counts the sessions offered and not used (`round6._could_start`). So both rules are applied to the
same stretches, to keep a change of rule from passing as a change of policy. The check ran at 16× round 5's
candidates (the main scale when it started), for 260 days in the conventional lab and 170 in the automated one.

Flagged stretches at copper's first fabrication step (round 6's rule / round 5's rule):

| Lab | Policy | Stock | Seed | Days | Round 5 flagged | Flagged, cap (r6 rule / r5 rule) | Flagged, no cap (r6 rule / r5 rule) | Blend screens, cap / no cap | Lots, cap / no cap |
|---|---|---|---|---|---|---|---|---|---|
| conventional | bofn3 | lean | 0 | 260 | 2 | 1 / 1 | 0 / 0 | 6 / 6 | 5 / 5 |
| conventional | bofn3 | lean | 4 | 260 | 2 | 1 / 2 | 0 / 0 | 7 / 7 | 5 / 5 |
| conventional | bofn3 | reorder | 0 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| conventional | bofn3 | reorder | 2 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| conventional | pkgfn3 | reorder | 0 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| conventional | pkgfn3 | reorder | 2 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| vertical | bofn3 | reorder | 0 | 170 | 3 | 0 / 0 | 0 / 0 | 5 / 5 | 4 / 4 |
| vertical | bofn3 | reorder | 1 | 170 | 2 | 0 / 0 | 0 / 0 | 4 / 4 | 7 / 7 |
| vertical | pkgfn3 | reorder | 0 | 170 | 3 | 0 / 0 | 0 / 0 | 5 / 5 | 4 / 4 |
| vertical | pkgfn3 | reorder | 1 | 170 | 2 | 0 / 0 | 0 / 0 | 4 / 4 | 7 / 7 |

**What it shows.**

* **Without the cap no stretch is flagged in any case, by either rule** (0 of 10 runs).
* **The cap was the cause where copper spends slowly**: in the conventional lab ordering metal as it goes, putting the
  cap back brings round 5's stretches back (days 0-53 and 0-57 for seed 0, 0-81 and 0-43 for seed 4, against round 5's
  0-53 and 0-22/23-64, 0-81 and 0-43/44-78). With the cap, BOFN asked for a new copper design 255 and 334 times in
  260 days and was turned away by its own cap nearly every time; without it, 38 and 24 times. The count shows as
  `new_low_ei` in those rows: net3 returns before it counts the eligible candidates (the check-only variants now
  count it as `new_capped`).
* **Elsewhere the cap never bound in round 6.** In the conventional lab with stock and in the automated lab, the run
  with the cap put back is the same as the run without it, call for call and dollar for dollar: buying stock and
  running the lab raise the money spent, and the cap rises with it. Round 5's stretches there came from its other
  money rules (the money kept for work in progress, the stock heuristic's money rules, the budget), which round 6 has
  also removed.
* Where the cap bound, it delayed copper's work rather than stopping it: by day 260 the same blend screens and lots
  were made with and without it, but with it copper had spent less ($37,900 against $45,900 for seed 0; the same
  $25,800 for seed 4) and its first weeks were idle.

## 7. Speed

Without money gates the automated lab works for the full two years, so BOFN's and pKGFN's runs do more than round
5's (which idled after day 371-434). A profile of the first attempt's automated-lab BOFN run (300 days, stocked,
seed 0: 778 s under the profiler) put **92 % of its time in proposing, 86 % in valuing new designs**
(`net3._cands_new`) and **66 % in the atomize node's search over 64 settings for each candidate**
(`policies2.atomizer_settings`, 120,000 calls): each trial's features rebuilt from the whole design (7.8 million
`atom_x` calls, 8.1 million `Space.encode` calls, 32 million `np.clip` calls) and one GP prediction per candidate
(130,000 `posterior` calls). Round 6 (`opt/net6.py`, the network policies only) builds a composition's features once
and encodes only the three settings that change, which gives the same numbers as `Space.encode`, and predicts the 64
trials of 16 candidates in one call, with the same random draws in the same order. A test checks that the faster
search makes the same choices from the same draws and leaves the generator in the same state
(`test_faster_atomizer_search_is_the_same_search`). A batched prediction can differ from 64 single ones in the last
bit, which is why round 6's BOFN rows are not round 5's even apart from the engine.

**Measured** ([`out/twin6/checks/speed/`](../out/twin6/checks/speed/README.md), runs side by side on this runner):
the faster search made the same automated-lab BOFN run (200 days) 6 % faster, 219 s against 234 s, with identical
results run for run. It is a modest gain: early in a run the atomize node has little data and the search is a
smaller share. MKL's reproducible mode (`MKL_CBWR=COMPATIBLE`, section 5) costs about as much the other way: a
conventional-lab BOFN run over 220 days took 90.5 s with it and 85.5 s without, with the same results; MKL's
GP-sized factorizations alone take 2-4 times as long under it, but they are a small part of a run.

<!-- SPEED_NUMBERS -->

## 8. The grid, and how to run it

`twin/bench6.py`. The arms are round 5's: `vertical` (the automated lab, built from day 0 while experiments run on
every route) and `conventional` (existing equipment, core facilities and partners, run by people), each `reorder`
(the reorder-point heuristic) or `lean` (each charge's metal ordered when needed). `fast` runs the heuristic on
aluminium and the funnel on copper; `bofn3` and `pkgfn3` run time-aware BOFN or pKGFN on both campaigns. Every
experiment runs all three, 16 seeds an arm (12 is the floor a comparison is reported from).

| Experiment | What | Arms | Runs |
|---|---|---|---|
| `arms` | like with like four ways (both labs, both stock rules) | 12 | 192 |
| `plans` | round 4's other two plans for the automated lab: waiting for the cell, external routes only (parallel is `arms`), stocked | 6 | 96 |
| `dec_none`, `dec_slow` | decision windows: no delay, slow (nominal is `arms`), the four arms | 24 | 384 |
| `atom` | the automated atomizer's cycle at 3 h and slow, 5.5 h (derived is `arms`), the automated lab both ways | 12 | 192 |
| `crucibles_late` | the crucible pool 240 days late, the automated lab both ways | 6 | 96 |
| `noused` | every station bought new, the automated lab stocked | 3 | 48 |
| `hpc` | the HPC stream at the other scales, both labs stocked | 24 | 384 |
| all | | 87 | 1,392 |

<!-- GRID_HOURS -->

**The order of work** (`TIERS`): tier 1 is `arms`; tier 2 what it rests on (`plans`, `hpc`); tier 3 `noused` and
`crucibles_late`; tier 4 the decision windows and the atomizer's cycle. Within a tier the first 12 seeds of every arm
come before the last four.

**Rows.** One JSON line per run: the configuration; for each campaign the best new alloy over time, the day and money
to each target (campaign money alone and with the lab's fixed costs), per new alloy, counters, the policy's own
counts; round 4's record (`r4`) and round 6's (`r6`: money by category and week, used purchases and their source,
the atomizer's runs, crucibles and the day the derived cycle starts, decisions, stock, shared stations, idle
stretches with causes, the HPC stream); the sha256 of the event log; and the provenance: the CPU, kernels, versions
and pin (`env`), and the commit with the tree hash of `twin/` at the start and the end of the run and whether `twin/`
differed from it at either point (`code`). Event logs are kept for `arms` and for seeds 0-1 of everything else.

**A compute slice** (out/twin6/README.md has the whole procedure):

```bash
cd vertical-lab
export PIP_TIMEOUT=600 PIP_RETRIES=2
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 && pip install -r out/twin6/requirements.txt
K=1
python -m twin.gpcheck6 --out out/twin6/slices/gpcheck-slice-$K.json            # exit 0 before any row is made
python -m twin.bench6 ids out/twin6/slices/slice-$K.txt --slice $K --workers 4
```

`python -m twin.bench6 slices 0` writes the lists (`out/twin6/slices/slice-<k>.txt`), as many as keep each at or
under 16 core-hours, the longest runs first; `fold` brings the slices' rows in; `status` writes
[`out/twin6/left.md`](../out/twin6/left.md).

## 9. What this job did not do

* **The grid itself**, as asked: no row of it was made. `python -m twin.bench6 status` lists every run as left.
* **The HPC at its full capacity** (about 123,000 candidates a day for each campaign, 1,920× round 5's) can't be
  simulated with this stream: about 12 hours of stream per two-year run (section 4). The grid goes to 256×.
* **Real Intel and EPYC 7763 runners.** The pin was shown on this AMD EPYC 9V74 and under an emulated Granite Rapids
  and Haswell, not on those CPUs themselves; the slices' GP checks will be the test (section 5).
* **pKGFN in the HPC pilot**, and BOFN in the conventional lab's pilot beyond the stream's cost: BOFN in the automated
  lab stood for the network policies. The grid's `hpc` and `hpc256` experiments run all three policies in both labs.
* **The copper check at the main scale.** It ran at 16× (and two cases at 1×), not 64×.
* **The analysis module** for round 6's rows (round 5's `like5.py` reads round 5's record, `r5`; round 6's rows carry
  `r6`, with money by category instead of a budget, and the crucible item renamed `crucible_coated`). It belongs with
  the grid's results.
* **Fixed costs.** Round 5's economics charged the automated lab's fixed costs in full from day 0. Round 6's spend
  tracking books each item's service, utilities and space from the day it is online, and the space's own from the day
  it is ready, so that limit is gone from the rows; the analysis still has to use it.

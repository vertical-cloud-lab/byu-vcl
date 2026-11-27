# Digital twin, round 5: two years from the day the money arrives

Sterling, on PR 400 (2026-11-27): "Twin round 5: two years from the day the money arrives, with enough runs to trust
every comparison." All money at t = 0; the facility ready between day 60 and day 100; used equipment by a rule;
real experiments from day 0; stock bought early by a heuristic, then a look back at what should have been bought;
shared equipment modelled as it's really used; decisions made by people take time. Compare like with like (four
ways), round 4's three plans and round 3's economics, on at least 12 seeds per arm. Four notes he added while it ran
are in section 0.

Round 4 is [`twin_round4.md`](twin_round4.md), round 3b [`twin_round3b.md`](twin_round3b.md). Everything here is
simulated: synthetic truths, simulated instruments, assumed prices, capacities, lead times and schedules. It shows
how the labs, plans and policies interact in the model, not what the real lab will find. **No vendor has given a
lead time, and no used-equipment price or risk has been quoted, so every build-out date, used purchase and stock
lead rests on stand-ins.**

<!-- RESULTS-SUMMARY -->

## 0. Sterling's notes while round 5 ran

He asked for notes starting `Round 5 note:` to be applied as they came. Four came, all from sgbaird, all applied to
every row (each row lists them in `r5.notes`). Note 4 arrived while the first batch ran, so that batch was stopped
and its 40 rows discarded; every row in `out/twin5/runs/` includes notes 1-4.

| Note | Time (UTC) | What it asked | What changed |
|---|---|---|---|
| 1 | 05:37 | "For the conventional lab, assume at most 8 atomizations per week." | The conventional lab's atomizer has two attended starts a day (08:00, 13:00), aluminium Mon-Wed and copper Friday, Thursday free as DAL #256's flex day: 8 a week. The automated lab's atomizer runs the same way until its cell is integrated (people run it then). |
| 2 | 05:41 | The automated lab's atomizer runs 24/7; derive the cycle for a unique composition from the lab's record, step by step, as a design target, with a sensitivity (derived, 3 h, slower). | Section 2. Derived: about 2.2 h a composition for aluminium (about 76 a week), 3.4 h for copper, from the cell's integration, both campaigns as they need it. Sensitivity: derived, 3 h, slow. |
| 3 | 05:51 | Round 3's automated lab sat idle for long stretches: give it its own 24/7 atomizer used by both campaigns as needed; check nothing but the spending plan causes the stall; idle time per station and campaign with a cause for each stretch; unambiguous counters. | The atomizer as in note 2; all money at t = 0; a daily log per campaign and the idle stretches with their causes (section 7); counters (designed, lots made, alloys made, alloys printed, alloys tested). |
| 4 | 06:11 | "Designed" at full computational capacity, outside the cost-aware choice: model the HPC available; keep it running both years; the simulation nodes not part of pKGFN's p or BOFN's cost; report HPC use, candidates evaluated, and whether more compute would have changed anything. | Section 6: an open-CALPHAD stream on a stand-in allocation of 256 cores (122,880 candidates a day), free to the campaigns; the policies see the newest 128 unexplored candidates, 64 new a day. |

## What changed from round 4, and why

| Round 4 | Round 5 | Why |
|---|---|---|
| Round 3's spending plan: 15 % of the money at day 0, all of it by 75 % of the horizon | All of each campaign's two-year money from day 0, in both labs | The request |
| The room fitted out in about four months (the atomizer room's 16 weeks); installation waited for it | The facility is ready between day 60 and day 100, drawn per seed (a stand-in); equipment is ordered on day 0 and may arrive earlier, but installation starts only once the space is ready | The request |
| Every station bought new | Used equipment where a used market exists, chosen by a rule (section 1) | The request |
| A standing stock bought at day 0 ("stocked") or each charge's metal ordered when needed ("lean") | "Stocked" is a reorder-point heuristic with safety stock from each item's lead and use, updated as the campaign runs, under three money rules (section 3); "lean" as before | The request; the money rules from the first runs |
| Copper's route skipped steps the real process needs, so sharing showed up as little more than the atomizer and the SEM | Copper's deposits are cut by wire EDM, heat treated, sectioned, polished, hardness-mapped and PIP-tested; coupons are prepared; aluminium's builds are sectioned for the crack check (section 4) | The request |
| Decisions were instantaneous | A person's decision waits for the next review or weekly meeting; the automated lab's own decisions stay hourly, with a sign-off for expensive steps (section 5) | The request |
| The atomizer: 3 attended starts a weekday and 1 on Saturday, aluminium Mon-Thu, copper Fri-Sat (16 a week), in every plan | The conventional lab: 8 a week. The automated lab: the same until its cell is integrated, then 24/7 at a derived cycle, either campaign at any time | Notes 1-3 |
| Simulations bought by the policies, $1-25 each, as a small pool | A continuous stream on the HPC allocation, free to the campaigns; open-CALPHAD only (Thermo-Calc is licence-limited) | Note 4 |
| The conventional lab was round 3's facility, ordered as it went (round 3b) | The conventional lab is round 4's external-only plan run by people: BYU's existing equipment and core facilities and the same partners, with the same money from day 0 | Like with like: the same outside world for both labs |
| Two engine rules for every policy (a WIP limit before the first fabrication step; money kept for the coming week's standing slots) | A third: money kept for the work in progress (section 3) | The first runs: without a spending plan, copper spent its money on powders it couldn't test |

Round 4's code is unchanged but for a hook (`Facility4.schedule`), so its results still reproduce. Round 5 is
[`twin/round5.py`](../twin/round5.py) (round 4's classes, subclassed), its runner
[`twin/bench5.py`](../twin/bench5.py), its comparisons [`twin/like5.py`](../twin/like5.py), its figures
[`twin/figures5.py`](../twin/figures5.py), and its tests [`twin/tests/test_round5.py`](../twin/tests/test_round5.py).

**Reproducibility.** Every row is made under round 3b's pin ([`twin/repro.py`](../twin/repro.py)) with
`TWIN_PIN=avx2`: one BLAS thread, the AVX2 kernels, `PYTHONHASHSEED=0`, the global generators seeded per run. This
runner has AVX-512 (an AMD EPYC 9V45), but round 5's rows are all new, and a follow-up may land on an AVX2-only
runner (the three cancelled runs had EPYC 7763s), so one pin keeps every table on one set of kernels. Every row
records the CPU, the kernels, the package versions (numpy 2.5.5, scipy 1.18.1, torch 2.15.0 CPU, botorch 0.18.1,
gpytorch 1.15.2, linear_operator 0.6.1, as round 3b's), the commit it was made from and the notes it includes.
`twin/tests/test_round5.py` reruns a short run and checks the row is identical.

## 1. The facility window and used equipment

* **The space is ready at day U(60, 100)**, drawn per seed (`ROOM_DAYS`). Every item of PR 318's lab is ordered on
  day 0 with round 4's lead draws for the same seed; each is installed when it and the space are there, then
  commissioned (round 4's install and commissioning weeks), then ramps up on round 4's learning curve.
* **Used equipment** is allowed for the stations with a real used market (`USED_OK`): wire EDM, the tensile frames
  and chamber, ICP-MS, SEM, XRD, XRF, Mastersizer, micro-Vickers, nanoindenter, polishers, furnaces, digital
  microscope. Not the Aconity MIDI or InssTek MX-Lab (rare, and the vendors' installation and qualification are tied
  to new machines), the robots, Kardex or docks, the custom cells, the Plastometrex benchtop, or the CubXL (owned).
* **Stand-ins** (`USED`): a used unit ships 2 weeks after BYU's purchase order (itself 2 weeks, DAL PR 266) and costs
  45 % of new; 1 in 4 arrives faulty or needs refurbishment (6 weeks, 15 % of the new price); a week more
  commissioning (a service engineer's check and calibration).
* **The rule** (`used_rule`): buy used when the expected days saved, against the expected date the space is ready
  (day 80) and with the fault risk priced in, are at least 14. An item that arrives new before the space is ready
  saves nothing used, so the rule picks only the items whose new lead runs past the space.

<!-- RESULTS-USED -->

## 2. The automated lab's atomizer (note 2)

The cycle per unique composition, from the lab's own records. `runs.csv` (DAL PR 286, `8320f13`) has no step
timings; the run records' lab-time timelines do (DAL `atomizer-runs/2026-10-08`, `-10-21`, `-10-28`, `-11-13`
READMEs), with the SOP (DAL PR 253), #219 and #256's schedule (which says "Nothing in the chain has been timed end to
end").

| Step | Observed or stated | Efficient and automated (what limits it) | Overlaps the next run? |
|---|---|---|---|
| Loading, set-up, close | 18.5 min (Oct 28, skull removal and nozzle check included); about 34 min (Nov 13) | 15-25 min; labour | the charge is made ahead |
| Pump-down, purge, washes | 19 min (Oct 21); 20 min (Oct 28, one extra wash); at least 21 min (Oct 8, three 500 °C washes); about 1.7 h (Nov 13, a sensor fault) | 15-20 min; the machine | no |
| Heat, melt, 2-min hold | about 6 min for 169 g of Al (Oct 21); about 8.5 min for 858 g of bronze (Oct 28) | 6-10 min; physics | no |
| Atomize | about 3 min (Oct 21); 3.5-3.7 min (Oct 27-28); about 6 min (Nov 13) | 3-5 min; physics | no |
| Cool to 400 °C, vent, until the furnace can be touched | "~1 h" (#256); "full cooldown about 30 min" (training); clean-up began about 37 min after the pour (Oct 21) | vent at 15-30 min, crucible out at about 60 min; physics | the powder is collected meanwhile |
| Powder collection | not timed on its own | about 35 min of arm work (`atom_timeline.py`, an estimate) | yes, inside the cool-down |
| Clean and rebuild, same family | about 50 min (Nov 7: full teardown, new nozzle, pin and plate, BN respray, #219); 1-2 h (#256); BN "sprayed the night before, dry" (SOP) | about 30 min on the critical path with a pre-coated spare crucible; the overnight dry is physics | only with spare crucibles |
| Copper to aluminium | "full clean (about 1 h)" (SOP); separate copper crucible, nozzle and rod; booster swap by a person | 1-2 h a switch | no |

* **Derived: about 2.2 h a composition for aluminium** (2.0-2.5 h): from the end of a pour to ready for the next
  charge about 1.6 h (about an hour of cooling with the powder collected meanwhile, then the crucible swap, lid and
  leak check), plus about 0.6 h for the next run (charge, 20 min of washes, 8 min of melting, 4 min of pouring).
  **About 76 a week at 24/7.** Bronze melts, pours and cools longer and needs a new nozzle and plate every run: about
  2.5-3 h, and the twin's yield model gives 3.4 h. These are the twin's own per-run hours
  (`atomize_yield.charge_plan`: 2.21 h Al, 3.36 h Cu at 225 cm3), so the derived case books them. A switch between
  an aluminium and a copper melt costs 1.5 h.
* **Next to the 3 h figure and the record:** 3 h is 56 a week; the lab's record is 10 runs in 43 days, 1.6-1.7 a
  week. The manual best times (a 35-minute run, a 50-minute turnaround) are already close to the derived cycle:
  automation gains hours of operation and overlap, not faster steps.
* **It is a design target, not a demonstrated rate, and it assumes pre-coated spare crucibles.** Each crucible is out
  of service about 14-16 h for its overnight BN dry, so a cycle of 2-3 h needs 6-8 coated crucibles per alloy family
  in rotation; the lab has one per family now, which allows at most 1 run a day (7 a week at 24/7), the record's best
  pace. Copper needs a new nozzle and plate every run and an empty cure for each fresh coat. Faults cost hours (Nov 13,
  1.5 h of purging; Oct 20, an afternoon). Charge preparation (1-1.5 h to dose and pack, 2-3.5 h with machined cups)
  is off the atomizer's critical path but adds up to 56-84 h a week at 56 runs.
* **The slow case:** #256's untimed step estimates one after another (a 2.5-3.5 h run, 1 h to cool, 1-2 h to clean),
  4.5-6.5 h: 5.5 h for aluminium, 6.5 h for copper, 2 h a switch.
* **When it applies:** from the day the cell is integrated (the robots tend the runs). Until then people run the
  atomizer as the conventional lab does, at most 8 a week (note 1). In the external-only plan it never changes.

<!-- RESULTS-ATOM -->

## 3. Money and stock

* **All money at t = 0.** Each campaign has round 3's money a year for two years from day 0: aluminium $240k, copper
  $120k, in both labs. No spending plan. Round 4's reserve for the coming week's standing slots stays.
* **Money kept for the work in progress** (a third engine rule, for every policy in both labs): a new composition
  starts only if the money left after it still pays for the next steps of the lots made (or in the making) in the
  last 60 days whose alloy has no tested result yet: aluminium a build and a test each; copper a small deposit each
  and, for half of them, a large deposit, its tensile, screen and immersion. In the first test runs, with no spending
  plan and a 24/7 atomizer, copper spent its two-year money on powders by about day 330, 56 of its 72 charges waiting
  months for plates and nozzles, and could not pay to deposit or test them. Copper's atomizer consumables cost about
  $470 a run (a plate and a nozzle).
* **The stock heuristic** ("stocked", `REORDER`): for each item, a reorder point `s = dL + z sqrt(L sd(d)^2 + d^2
  sd(L)^2)` and an order-up-to level `s + 30 days of use`, with z = 1.65 (a 95 % cycle service level), sd(d) = d
  (lumpy demand, a charge at a time), sd(L) = L ln(gsd) from the item's own lead spread, and L its median lead plus the
  office's 3 days (Silver, Pyke & Thomas 2017, ch. 6). The daily use d starts from round 2's standing stock (about a
  month's use at the vertical lab's pace; 0.7 of it for the conventional lab's 8 runs a week) and is updated from the
  campaign's own use: the last 60 days blended with the prior, or the last 30 days if higher (the cell's atomizer is a
  surge). It is checked at every charge and once a day; orders go through the market model of rounds 1-4 (its prices,
  lead spreads, backorders and failing channels).
* **Three money rules on the stock**, each found in the first runs: no item is stocked beyond the days the money left
  lasts at the last 30 days' rate of spending, or beyond the campaign's end ($110k of aluminium stock was left unused
  without it); stock never spends the money kept for the work in progress; and the stock on hand and on order is
  worth at most 20 % of the money left (without the last two, copper's stocked arm spent its money on plates and
  nozzles by day 231 and reached its targets in fewer seeds than its lean arm).
* **"Lean"** is round 3b's: what is on hand at day 0 (DAL's own stock by November 2026), and each charge's metal and
  consumables ordered when it needs them (1.5 times the shortfall, at least the minimum order).

<!-- RESULTS-STOCK -->

## 4. Shared equipment as the real process uses it

Every step of both campaigns against the real process (the proposals' networks, DAL's SOPs and #256's schedule).
Added (stand-in hours; `CU_STEPS`, `AL_STEPS`); "side" steps are booked and charged after the result and not waited
for:

| Campaign, action | Steps added | Why |
|---|---|---|
| Copper small DED, pre-placed and blend deposits | section, mount and polish (prep 1-1.5 h) before the SEM; micro-Vickers (0.25-0.5 h, side) | density, cracks, dilution, beta' and grain size are read off a polished cross-section |
| Copper large DED (1 kg in house, 2 kg at Mines) | wire EDM (1.5 h), heat treatment (3 h), prep (1.5 h) before the SEM; hardness, a PIP map on the section and ICP-MS of the deposit (side) | the block must be cut off its thick substrate and into bar blanks, coupons and a section; a temper anneal before testing, as for NAB-type alloys; PIP and hardness give strength on the section; ICP-MS the deposit's composition |
| Copper corrosion screen and immersion | the coupon face ground and polished (prep 0.5 h) before the CubXL or the vials; after 30 days the coupon sectioned (prep 1 h) for the selective-attack depth | electrochemistry and immersion need a prepared face; selective attack is read on a section |
| Aluminium builds | a cube sectioned and polished (prep 1 h) for the crack check | the crack check reads a polished section |
| Unchanged | copper tensile (machining 1 h, frames 0.6 h; blanks already cut by EDM); copper and aluminium powder (cups, doser, atomizer, sieve, PSD, SEM/EDS, ICP-MS on request); aluminium test, promote, PIP and section | already as the real process |

In the conventional lab the EDM is the Provo service (7 days, $150), PIP the Plastometrex service, prep, hardness
and the furnaces BYU's own on day shifts; in the automated lab, the in-house stations once online.

<!-- RESULTS-SHARED -->

## 5. Decisions made by people take time

Sterling, on PR 400: "Someone has to look at the results, think, maybe discuss them at a weekly meeting, and then
act." His earlier comments on the human element: DAL #283 (2026-11-26), the goal is new alloys "in a tenth of the
normal wall time ... compared with traditional research (manual experiments, human decision making)"; DAL #277
(2026-11-24), "Weekly 30 minute meetings, 10 minutes of which we spend on our computers, triggering prompts and
recording"; DAL #276, compare "the 'conventional lab' it's compared against, against how this lab actually works
today"; DAL #54, "building hours, ... automated vs. manual steps, the morning and evening shift schedules, 6 days a
week". The schedule he moved to DAL #256 (2026-11-24) is the nearest thing to a decision cadence: "Friday optimizer
update: refit on the data through Thursday and pick next week's batch", "The 30-min meeting on Friday, so it doubles
as the decision meeting", powder handled within 48 h. DAL PR 297's clocked benchmark decided its conventional rounds
"at Monday 09:00 meetings once the previous round's bars are back". None of these gives a number for the delay itself,
so the windows below are stand-ins built on those cadences (`DECISIONS`). Day 0 is a Monday; no decisions at weekends.

| Kind of decision | Conventional lab (all decisions are people's) | Automated lab |
|---|---|---|
| Routine next steps on a lot, part or deposit, and stopping a test | the next working-day review at 13:00, once 2 results wait or the oldest has waited 40 h ("powder handled within 48 h") | the lab's own, hourly |
| Choosing new compositions and promoting an alloy (the results that score an alloy: tensile, copper's screen, tensile and immersion) | the Friday 13:00 meeting (#256) | the heuristic: the Friday meeting (a person's rule of thumb in either lab); the optimizers and the funnel: their own, hourly |
| A gas-atomized lot, the validation network's verdict, the full-part test | the day after a meeting | a sign-off: the next working day |
| Any action over $2k (a Mines session, a partner's E8 plate) | (at the meeting or review that chose it) | a sign-off at the next working-day 10:00, at least 2 h after it is first proposed |

* **Slow:** reviews twice a week (Tue, Thu) once 4 results wait or the oldest has waited 100 h; meetings every other
  Monday at 09:00 (PR 297's rounds); sign-offs two working days later. **No delay:** everything as it comes (rounds 1-4).
* **How it works in the engine** (`Twin5.run_async`): a result a person must look at is held until its decision point
  and only then shown to the policy; when the result is an alloy's score, the alloy counts as demonstrated at the time
  the result came back, not when someone looked at it, so the window slows the next decision, not the measurement.

<!-- RESULTS-DECISIONS -->

## 6. The HPC stream (note 4)

* **Compute.** The open-CALPHAD node (pycalphad, what the policies' candidate pools use) at 0.05 core-hours a
  candidate (rounds 1-4), on a stand-in allocation of 256 cores of BYU's Office of Research Computing (FLAIME App. 2
  counts about 28,000 cores on the cluster): 122,880 candidates a day, every day of the two years, counted.
  Thermo-Calc's nodes are limited by licence seats, not cores, and stay as before.
* **Outside the money and the acquisitions.** The stream costs the campaigns nothing, and the policies' own
  open-CALPHAD calls are free too. In BOFN and pKGFN (`twin/opt/net3.py`) the acquisition already chose among physical
  actions only: the simulation node kept a pool of 48-64 simulated candidates topped up. The stream replaces that.
* **What the policies see.** No policy can use 122,880 candidates a day. The twin keeps the newest 128 unexplored
  candidates visible to them, 64 new a day spread over the day; every candidate a policy makes, builds or tests stays
  visible. `hpc_more` runs four times that (512 kept, 256 a day).

<!-- RESULTS-HPC -->

<!-- RESULTS-BODY -->

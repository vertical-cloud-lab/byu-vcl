# Digital twin, round 4: building the lab while running real experiments, every route at once

Sterling, on PR 394 (2026-11-26): "Twin round 4: building the lab while running real experiments, with every route at
its maximum throughput. ... Wall time to discovery, counted from the day the funding arrives, is what matters most.
So model the lab as in-house *and* external at once, scheduled together at maximum throughput with data-driven
decisions. It shouldn't be either/or, and the campaign shouldn't wait for the cell to be finished. ... Compare three
plans: wait until the cell is built, then start; ramp up in parallel, as above; external routes only."

Round 1 is [`twin.md`](twin.md), round 2 [`twin_round2.md`](twin_round2.md), round 3
[`twin_round3.md`](twin_round3.md). Everything here is simulated: synthetic truths, simulated instruments, assumed
prices, capacities, lead times and schedules. It shows how the plans, routes and policies interact in the model, not
what the real lab will find. **No vendor has given a lead time for any station yet, so every build-out date below
rests on stand-ins** (section 1).

<!-- RESULTS -->

## What changed from round 3, and why

| Round 3 | Round 4 | Why |
|---|---|---|
| The clock starts with the vertical lab built, stocked and running | The clock starts the day the funding arrives. Each in-house station is ordered then and comes online after its lead time, installation (once the room is fitted out) and commissioning; the robots run stations round the clock only once the cell is integrated | Wall time to discovery is counted from the funding |
| Every station at full rate from day 0 | A learning curve on every new station, fitted to the lab's own ten logged atomizer runs: more failed jobs (redone), slower jobs and more equipment faults at first | The atomizer's first six weeks: 2 good runs of 10, 1.6 runs a week against the 5 planned, 2 equipment faults |
| One facility per run: the vertical lab or the conventional lab | Every route at once: a router sends each step to whichever station of its kind returns the result first (in house once online; BYU's own equipment and core facilities and every partner from day 0), counting the redos a ramping station would need | In-house and external at once, scheduled together |
| Partners booked when an action was bought, with a random booking lead | Standing slots at the partners (Utah's MIDI 2 builds a week, MX-Lab monthly, Mines 7 sessions a year, Valimet monthly), each filled at the last moment before shipping, with the coming week's slots' money kept for them | Book standing slots and decide what goes in them as late as possible |
| No difference between sites | Each fabrication route has its own process offset (the same nominal laser power delivers a different effective power) and each testing route a measurement offset; the lab records the nominal settings unless someone recorded the process on site | Each route has its own bias; provenance |
| An alloy's story ended at its tensile (and immersion) test | Alloys at the second target move on through a gas-atomized lot, a validation network across the sites, and a full-part application test | Stages a promising alloy moves through |
| Three plans did not exist | `wait` (round 3's vertical lab, from the day the cell is complete), `parallel` and `external` | The request |

Round 3's code is unchanged (round 4 subclasses its `Facility`, `Campaign` and `Twin` in
[`twin/round4.py`](../twin/round4.py)), so round 3's results still reproduce. Round 4 is not seed-for-seed comparable
with round 3: the horizon is two years from funding, the facility differs, and the random streams are drawn in a
different order.

## 1. Build-out

Every station of PR 318's lab (the items and prices of [`twin/econ.py`](../twin/econ.py)) is ordered on day 0. A
station is online when its items have arrived, been installed in the new room and been commissioned. Installation
waits for the room's fit-out. The existing BYU atomizer and DAL's CubXL are on hand from day 0.

* **Lead times are stand-ins.** No vendor has given a lead or installation time for any of these stations. PR 331's
  quote drafts ask for them, and "nothing has been sent to any vendor"; PR 318: "There are no costs (#331 is where
  quotes go)". The few anchors:
  * comparable LPBF machines ship in 12-16 weeks (Xact Metal 12, DAL #133; AO Metal A30 12-16, DAL PR 245);
  * Kardex QuickShip is 4-6 weeks for standard sizes, "custom longer" (PR 331);
  * a BYU purchase order takes "ten days to two weeks PLUS shipping" (DAL PR 266);
  * BYU's WDXRF took 3-4 weeks to set up (VCL PR 95);
  * the atomizer's own room took 16 weeks: delivered Jun 11 2026, installed Sep 28, held up by the room's renovation
    (DAL #142, #159).
  
  Each seed draws every lead around its median (lognormal, σ 0.25). The medians are in
  `twin/round4.py` (`BUILD`).
* **Payments:** 30 % on order for items of $100k or more, the rest on delivery. Capital is $5.0M: PR 318's lab less
  the atomizer the lab already owns and DAL's CubXL.
* **The cell:** until the two MiR250 + UR12e units, the Kardex and the docks are commissioned and integrated (8
  weeks of programming the stations' transfers, assumed), in-house stations are run by people on the day shift (the
  hands-on hours of round 3's conventional lab). After that the robots load them round the clock.

<!-- BUILD -->

## 2. Ramp-up: a learning curve from the lab's own atomizer

DAL PR 286's `atomizer-runs/runs.csv` (at `8320f13`) lists every run the lab made on its own, Oct 2 to Nov 13 2026,
after AMAZEMET's training runs. Two of ten made usable powder (Oct 27, about 91 %; Nov 10, about 75 %). Oct 22 made
"more powder than Oct 21, still below target", which counts as half here. Two runs ended in an equipment fault: the
generator tripped on Nov 5, and on Nov 13 the shot burned the cup's seals and cracked its glass. Ten runs in 43 days
is 1.6 a week, against DAL #256's plan of 5.

* **Failures.** With a mature run failing 10 % of the time (bofn-clocked's figure, DAL PR 297), the chance of a
  learning failure on a station's (n+1)-th job is P0·exp(−n/N_L). The maximum-likelihood fit is P0 = 1.0 and
  N_L = 12.9 jobs. The profile likelihood is flat from about 5 to beyond 50 jobs, so ten runs pin the shape only
  loosely (`round4.fit_learning`).
* **Speed.** A job takes F0 = 3 times as long at first, from 1.6 runs a week against 5, falling on the same curve.
* **Faults.** A fifth of first jobs end in an equipment fault (2 of 10), with a few days' repair (median 72 h,
  assumed).
* **The existing atomizer starts at n = 10**, its ten logged runs: about a 46 % chance of a learning failure on its
  next run.
* **Every new process station** (MIDI, MX-Lab, EDM, machining cell, doser, sieve cell) starts on this curve.
  Instruments with the vendor's validated methods (SEM, XRD, ICP-MS, frames, ...) start at a third of the failure and
  fault chance and a third of the slowdown. That split is assumed: the atomizer is the only station with a logged
  history.
* **What a failure costs.** A failed job is redone on the same station, so it costs that station's time and the
  money again. A failed atomizer run is the run's own failure: the policy sees no powder, as in rounds 1-3.

## 3. Routes

Each step of an action names a kind of station (round 3's keys: an LPBF build, a wire-EDM job, a tensile test).
Round 4 books it on whichever station of that kind returns the result first (`Facility4.pick`). Every station of the
kind that the plan has counts, and so do the redos a ramping station would need. Policies still choose what to do,
on round 3's terms; the router chooses where.

| Route | Kind | From | Capacity and calendar | Lead and turnaround | Fee | Offset (σ) | Source |
|---|---|---|---|---|---|---|---|
| BYU atomizer (AMAZEMET rePOWDER) | powder | day 0, n = 10 on the learning curve | 3 starts a weekday + 1 Saturday; Al Mon-Thu, Cu Fri-Sat | 2.5 h a run | consumables | none | FLAIME App. 2; DAL #256 |
| Utah Aconity MIDI (core facility) | LPBF | day 0 | standing reservation, 2 builds a week (Tue, Wed) | ship 1 day; parts 4 days after the start | $800 | laser power 5 % | ONR budget ($800, unconfirmed); "$120/hr" (FLAIME genesis proposal); DAL #138 (parts 4 days after the start); Edison: about 8 builds a month |
| 3D Powder Tech (**hypothetical service**) | LPBF | day 0 | 1 build a week | ship 3 days; 5 days | $1,500 | 10 % | DAL #133: a printer vendor ($40k base) that printed samples only toward a sale, poor trial prints; the service is assumed |
| Utah InssTek MX-Lab (Fang group) | DED, small and blends | day 0 | one half-day session every 30 days (Tuesdays) | ship 1 day; 1 day | $300 (assumed) | 5 % | ONR YIP proposal ("about twelve half-day sessions a year"); DAL #256 |
| Mines FormAlloy X2 | DED, 2 kg | day 0 | 7 sessions a year | ship 5 days; 10 days (assumed) | $1,204 | 10 % | DAL PR 117 (3-7 sessions a year); ONR YIP field 10 ($155/machine h, $165/labour h, $1,204 with F&A) |
| Valimet (gas atomization) | ≥ 50 kg lot | day 0 | monthly slot | ship 14 days; 21 days | $8,000 + melt stock | none | FLAIME DAG; Edison: 6-12 weeks, $3-8k |
| BYU core facilities and shop | SEM, ICP-MS, XRD, XRF, metallography, Vickers, frames, furnaces | day 0 | day shifts | as round 3 | as round 3 | frames 2 % | round 2-3 `facility.py` |
| Provo EDM, Plastometrex PIP service, NSL | services | day 0 | as round 3 | 7, 7 and 10 days | $150, $250, $150 | none | round 2-3 |
| Outside tensile laboratory (**hypothetical**) | tensile | day 0 | 4 at a time, day shifts | 2 + 8 days | $600 (3 bars) | 4 % | no outside lab is named in DAL or byu-vcl; $200 a bar as DAL PR 297 (bofn-clocked) |
| In-house stations (PR 318) | all of the above | their build-out dates | round the clock with the robots; day shift before | round 3's | round 3's | the reference (0) | PR 318; `twin/facility.py` VERTICAL |

The offsets follow DAL PR 297's bofn-clocked benchmark (DAL #283) where they overlap. There, a partner printer moves
the laser-process ridge by −0.05, another lab's ridge by ±0.08, and its tensile frames read +0.04. Here each seed
draws its own offset for each site.

* **Standing slots, filled late.** A partner's session is reserved ahead, so taking it needs only the shipping lead.
  What goes into it is decided at most a day before the material must leave: an action is admitted to a slot only
  once the slot starts within its shipping time plus a day. The policy therefore has every result back that it could
  have.
* **Money for the slots.** Each campaign keeps the money for the coming week's unfilled slots. Without that reserve,
  the first runs left Utah's slots empty for months: cheap new powders spent the money while the next slot was still
  outside its window.
* **Money.** Each campaign keeps round 3's money per year (aluminium $120k, copper $60k), two years' worth over the
  two-year horizon, on round 3's spending plan (15 % at day 0, all of it by 75 % of the horizon). The plan is the same
  in every plan of the three. The wait plan carries its unspent money to its start.

## 4. The stages after discovery

An alloy whose measured utility reaches the second target (T2) moves on, one at a time per campaign, under the same
rule in every plan and for every policy. The stages have their own scale-up money (FLAIME's DAG budgets six
gas-atomization runs), so discovery's money is the same in every plan.

1. **Production-representative powder.** A gas-atomized lot: Valimet for aluminium (≥ 50 kg), Ames for copper
   (25 kg, as rounds 1-3). The next two stages need kilograms. The ultrasonic atomizer makes a few hundred grams a
   run, and not as a production atomizer would.
2. **A distributed validation network.** The gas lot is made into parts and tested at every fabrication site the plan
   has, at the same time:
   * aluminium: the in-house MIDI, Utah's MIDI and 3D Powder Tech;
   * copper: the in-house MX-Lab, Utah's MX-Lab and Mines.

   Each site builds with its own process offset. The alloy passes if the sites' mean true utility is at or above the
   state of the art (T1).
3. **A full part in an application-specific performance test** at an outside laboratory (assumed):
   * aluminium: a printed heat-exchanger or bracket in thermal-mechanical cycling, 6 weeks, $15k;
   * copper: a DED repair on a seawater pump or valve part, 60 days in flowing seawater, $20k.

"Validated T2" in the tables is the first alloy at T2 (its true utility) that has passed all three.

<!-- STAGES -->

## Sources

1. Round 4's tables: [`out/twin4/fig/tables.md`](../out/twin4/fig/tables.md) and
   [`out/twin4/fig/numbers.json`](../out/twin4/fig/numbers.json) (`twin/figures4.py`); the per-run logs in
   [`out/twin4/runs/`](../out/twin4/runs/).
2. The engine and runner: [`twin/round4.py`](../twin/round4.py), [`twin/bench4.py`](../twin/bench4.py); tests in
   [`twin/tests/test_round4.py`](../twin/tests/test_round4.py).
3. The atomizer's runs: DAL PR 286, `atomizer-runs/runs.csv` and `README.md` at `8320f13`; DAL #159, #219.
4. Lead times and prices: VCL PR 318, PR 331 (`procurement/`), PR 95; DAL #133, #142, PR 245, PR 266; `twin/econ.py`.
5. Partners: DAL #133 (3D Powder Tech), #138 (Utah's MIDI), PR 117 (Mines, MX-Lab), the ONR YIP proposal and its
   field 10 facilities page (Mines' rates, MX-Lab sessions), the FLAIME genesis proposal (Utah's rate), DAL #256
   (calendars), DAL PR 297 (bofn-clocked: offsets, outside bar price, failure rates).

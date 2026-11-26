# Digital twin, round 3: physical capacity, asynchronous acquisition, interim readings, pKGFN, time to discovery

Sterling, on PR 393 (2026-11-26): "Round 3 of the twin: remove the scheduling constraints that aren't physical, then
rerun. ... Round 2 explains copper's result as 'copper data is slow and scarce' (§ 5.3). But the twin caps work in
flight at 8 actions for copper and 24 for aluminium, and a 30-day immersion holds one of those slots for its whole
month. The policies also choose one action at a time. A real lab isn't limited to sequential evaluation, or to
synchronous batches either. ... Replace the in-flight cap with physical capacity ... Asynchronous acquisition ...
Interim observations and early stopping ... pKGFN proper ... Optimize for wall time to discovery, not just cost ...
Fairness ... Report mean ± SE with paired differences, and say plainly where BOFN or pKGFN still doesn't win."

Round 1 is [`twin.md`](twin.md), round 2 [`twin_round2.md`](twin_round2.md). Everything here is simulated: synthetic
truths, simulated instruments, assumed prices, capacities and schedules. It shows how policies, capacity and
schedules interact in the model, not what the real lab will find.

## What changed from round 2, and why

| Round 2 | Round 3 | Why |
|---|---|---|
| A cap on each campaign's actions in flight (24 aluminium, 8 copper), whatever they held: a 30-day immersion took one of copper's eight for its month | No cap. Stations keep their units, calendars, start slots, session caps and breakdowns; every step also books its robot or person; passive steps hold a fixture slot (24 immersion positions, furnace positions) and the sample, nothing else | The cap was not a physical limit, and it made copper look slow because the cap was |
| A policy was asked for `wip − inflight` actions when one of its results came back | Every simulated hour, a campaign whose results came back or whose lab had a booking end is asked for a ranked list of actions across every node of every part; each starts if its gating station can take it within 2 h (later steps may queue) | A lab chooses a station's next job when the station frees up, from everything it could do then |
| Money limited only by the budget (the cap throttled spending) | One spending plan for every policy: a stocked lab's day-0 inventory, then 15 % of the rest, rising to all of it at 75 % of the horizon; money goes in the policy's own ranking (once the top-ranked action has to wait for the plan, nothing ranked below it that costs more than $50 starts that hour) | Without the cap, something has to pace money; a plan is what a grant has |
| Pending work was handled by the cap and a distance rule within one batch | Kriging believer: GP-BO adds each design in flight to its GP at the posterior mean; BOFN and pKGFN count parts whose final result is in flight at their posterior mean in the incumbent, and keep new designs 0.03 away (composition features) from anything started | Asynchronous BO needs a model of what is already running |
| The 30-day immersion was one result at day 30 | Interim readings at days 1, 3, 7 and 14 (mass change of the uncleaned coupon, from the coupon's own film-growth trajectory; selective attack only at day 30), a network node from interim reading to 30-day rate, and a stop action | A long test says something along the way; a coupon that can't pay should give its position back |
| BOFN "in the spirit of pKGFN": EI per dollar for new designs and the dear steps, the cheap nodes always | BOFN (EI per cost of the remaining path to a demonstrated alloy) and pKGFN (the knowledge gradient of the next node or bundle, per its cost) on every node of every part, each with a per-dollar or a time-aware denominator | The request: pKGFN proper, and acquisitions that target days |
| The funnel screened its 256 designs a few at a time under the cap, made its 24 best, then rebuilt the same shortlist and made those designs again | The funnel screens its 256 at once, makes its best 24, then the next 24 down its own ranking, and screens 256 more when those run out | The same freedom to fill capacity for every policy |
| A copper alloy was scored when its tensile came back if its immersion had started (`Campaign._cu_check` tested only that both keys existed) | Both results must be back | A bug, found here; see below |

**A round-2 bug, and what it did.** `Campaign._cu_check` scored a copper alloy once the deposit had a `tensile` and an
`immersion` entry, and an immersion that had only started was the string `"pending"`. So an alloy whose immersion
started before its tensile came back was scored when the tensile came back, up to 30 days before its immersion
finished. In round 2's seed-0 event logs, **126 of 271 copper alloys were scored early**: random 13-20 a run, the
funnel 13-22, the cost-aware model 12, plain BOFN 3-4, GP-BO 1-2, BOFN with blend screening 0 (its immersions waited
for a slot under the cap). The scored utility was the truth's, so best-of-year values barely move, but round 2's copper
day counts (5.2-5.4) favour the funnel and the baselines by up to 30 days. Round 3 fixes it; round 2's code keeps the
old check behind a flag (`Campaign.legacy_cu_check`, set by `twin/bench2.py`), so its committed results still
reproduce, and `TWIN_FIX_CU_CHECK=1` reruns round 2 with the fix.

Round 3 is not seed-for-seed comparable with round 2: the engine differs and the interim readings draw from the same
random streams. Comparisons below are within round 3, or policy by policy across rounds.

## 1. Physical capacity

Each step of an action books its station (`Facility.run_step_joint`) together with whoever has to be there when it
starts: the earliest time all of them are free. An action is admitted only if its gating station would take it within
2 h of when the part gets there (`Campaign.gate_ok`; the atomizer for powder, the MIDI for a print, the MX-Lab or the
Mines session for DED, the EDM for bars, metallography for sections and PIP, the CubXL for a screen, an immersion
position for a coupon); the steps after the gate may queue (first come, first served). The two campaigns share the
atomizer; each hour, the one further below its share of the money in the atomizer's recent hours decides first.

| Resource | Vertical lab | Conventional lab | Source |
|---|---|---|---|
| Atomizer (AMAZEMET rePOWDER) | 1; starts at 08:00, 10:30, 13:00 Mon-Fri and 09:00 Sat; 2.5 h a run (225 cm³), 3 h to change between Al and Cu | the same | FLAIME App. 2 ("up to 3 compositions/day M-F and 1 on Saturday"); `timelapse.py`; AMAZEMET's 2-4 h changeover (`bottleneck.py`) |
| Robots | 2 MiR250 + UR12e, round the clock, 0.1 h a step | none | PR 318; the transfer time from `setup_lab.TwoLab` and `warehouse.Amr` timings (assumed 6 min) |
| People | 1 technician, Mon-Sat 08-17: each atomizer run's attended hour, packing outside work | 3 operators, Mon-Sat 08-17: each station's hands-on hours (`econ.HANDS_ON`: a fixed part per booking plus a share of the hours, capped at a day) | `econ.STAFF` (one person on the day shift); DAL #256 (`al-campaign-schedule/README.md` L21-L25 @ 6ff7717: "One run takes about 10–15 person-hours from charge to SEM" and the plan needs "a third trained operator") |
| LPBF | Aconity MIDI in house, round the clock, 5 h a build | Utah core facility: at most 3 builds a week, booking lead about 7 days, results 2 days after | PR 318; ONR budget and FLAIME App. 2 (round 1) |
| DED | InssTek MX-Lab in house, round the clock: blend screen 3 h, small deposit 4 h, 1 kg plate 8 h | Utah MX-Lab half-day sessions, one per 21 days; Mines FormAlloy X2 for 2 kg, one session per 35 days, 21-day lead, 10-day turnaround | PR 318 `bottleneck.py`; DAL PR 117 |
| Heat treatment | 2 furnaces × 4 coupon positions, a 3 h cycle starting every 3 h, robots load | 2 × 4 positions, cycles at 08:00, 11:00 and 14:00 on weekdays, a person loads | assumed (positions per furnace) |
| Immersion | 24 vial positions on the gantry deck | 24 | round 1's assumption |
| CubXL screen | 1, round the clock | 1, attended 0.25 h | DAL PR 117 Task 2 |
| SEM, XRD, XRF, metallography, Vickers, PIP, EDM, tensile | in house (PR 318 chapters 4-7), round the clock | core facilities and services on day shifts with their rates and turnaround (PIP and EDM outside) | round 2 (`facility.py`) |

The robots and the technician are not a constraint in these runs (robots well under 10 % busy); in the conventional
lab, the three operators are (section 3.4).

## 2. The policies

All on the same engine, capacity and money (`twin/opt/policies3.py`, `twin/opt/net3.py`):

* **Random, Sobol, the heuristic**: round 1 and 2's decisions unchanged, behind an adapter that offers every downstream
  step at once and up to four new designs a decision, and offers again whatever a busy station or the plan turned away.
* **Tiered screening** (and its mis-specified and ablated variants): section "What changed".
* **GP-BO**: round 2's (one GP from the design to the measured utility, EI per dollar), with the kriging believer.
* **BOFN** (`bofn3`, time-aware; `bofn3_usd`, per dollar): round 2's network (the same nodes and data), with every
  candidate (a new design; a print from powder already made, or another print at new settings when a lot's parts came
  out unsound; PIP and section; bars; for copper a blend screen, PIP and screen, atomizing a screened blend or going
  large from a small deposit, a 1 kg deposit, tensile, immersion, and stopping a coupon) scored by the expected
  improvement of the part's utility over the incumbent, per cost of the remaining path to a demonstrated alloy.
* **pKGFN** (`pkgfn3`, time-aware): the knowledge gradient of the next node or bundle (powder and its first print,
  PIP and section, PIP and screen, the whole chain of a 1 kg deposit, tensile, the 30-day result), per its own cost
  (Buathong et al. 2024; DAL's port, `benchmarks/partial_kgfn`, and its `bofn-cu-ded` policy, whose bundles,
  incumbent-anchored inner max and EI-per-cost fallback this follows). Six Monte Carlo fantasies of the node's outputs,
  each carried through the rest of the network with 24 common draws; the value is E[max(μ(y), c)] − max(μ, c) with c
  the best alternative's posterior mean or the incumbent. KG for the four candidates of each stage with the most EI per
  cost to completion (DAL scores 16). Two simplifications: the fantasy's effect on *other* parts' posteriors (through the
  node GP's covariance) is left out, an independent-alternatives inner max; and when every KG is flat, EI per cost to
  completion decides (DAL's fallback).
* **Denominators.** Per dollar: the action's money. Time-aware: bottleneck-hours, the station-hours of the step or path
  weighted by each station's load (the share of its next 72 h booked, at least 0.05; the next 720 h for immersion
  positions), plus 0.001 h per dollar so money still breaks ties. Money is the plan's constraint in both.

**What BOFN and pKGFN needed before they worked on this engine** (each found in a test year, fixed for both, and part
of the policies as run):

1. *Powder that won't atomize.* The network's utility starts at the print or DED node, so a design that atomizes to
   nothing looked as good as one that doesn't (87 of 98 aluminium lots in one test year had no usable powder). New
   designs are now weighted by the atomize node's chance of an in-cut yield above 3 %, and need an expected improvement
   of at least 1e-4 to start.
2. *Powder already made is printed* (round 2's rule): only a reprint at new settings is valued.
3. *Copper's blend screens against screened blends.* An unscreened design valued at the atomized fidelity beat every
   screened blend valued from its own (inhomogeneous, so worse) readings, and the year's copper money went to screens.
   Both are now valued at the blend fidelity, and before copper's tensile and immersion nodes have data, the proxies
   for them carry their spread (PIP to yield, 12 %; uniform to total elongation, a factor of 1.4; the 1-hour screen to
   the 30-day rate, a factor of 1.6; a blend's inhomogeneity, a fifth lower ± 35 %).
4. *Screens can't take the whole budget.* Blend screens (with their PIP and screen) are capped at 25 % of copper's money
   so far plus $2,500. Round 2's BOFN with blend screening spent 18 % on them (12 seeds, 17-20 %).
5. *KG of finishing is 0 before the first demonstration.* With an incumbent of 0 and a utility that is never negative,
   the KG of a coupon's 30-day result is exactly 0 (its posterior mean is a martingale), and pKGFN stopped every coupon
   on day 1 (four discarded runs). Stop decisions use EI of finishing, for both, once an alloy has been demonstrated.

These are design choices, stated so the comparison can be judged; the baselines needed none.

RESULTS_PLACEHOLDER

# The campaign trace (`campaign_trace.json`)

One JSON file per traced twin run: every booking the run made, with the sample it served, its step in DAL's workflow
network and how it ended; every sample and what came of it; every measurement; and, at every iteration, what the
optimizer proposed, the acquisition value it gave each proposal, and the best so far. Built by `twin/trace.py`
(`python -m twin.trace check <file>` checks a file against this schema). A traced run is an ordinary run that also
records: a traced and an untraced run give the same results.

- **`campaign_trace.json`** is BOFN's traced year on DAL's own lab as DAL #256 schedules it
  (`dal256_bofn_s0_stock-lean_seeding-dal275.json`), seeded with DAL #275's common seed set. It is a copy, kept under
  this name so it can be found.
- The other files here are the seed-0 traces of the `seeded` experiment (the vertical lab) and the `seeded_dal256`
  experiment (DAL #256's schedule), for BOFN, standard BO (GP-BO) and random:
  `<facility>_<policy>_s0[_stock-lean]_seeding-dal275.json`.

**Everything in a trace is simulated.** The truth is round 2's synthetic truth (`twin/truth_al.py`, `twin/truth_cu.py`),
not a measurement. Where it differs from DAL's synthetic benchmarks is set out in `notes/twin_round2.md`, section 6.

## Time

`t_*_h` are hours from the start, where t = 0 is a Monday at 00:00; `day = t / 24`. The horizon is 365 days.

## Top level

| key | what it holds |
|---|---|
| `meta` | `schema` ("vertical-lab campaign trace v1"), `run_id`, `generated_utc`, `cfg` (the run's config: policy, seed, facility, stock, seeding, ...), `time`, `horizon_h`, `outcomes` (the outcome codes below, defined), `campaigns` (per campaign: `budget_usd`, `wip` (actions in flight at once), `spent_usd`, `elements`, `process` (the process variables), `base`) |
| `stations` | `[[key, {name, units, hours, external}], ...]`: the facility's stations and calendars (`24/7`, `day` = Mon-Fri 08-17, `day6` = Mon-Sat) |
| `seeds` | per campaign, DAL #275's seed set as run: `label`, `asked_wt_pct` (the composition #275 asks for), `run_wt_pct` (after projecting onto the campaign's design box), `process` (the default process settings it ran at), `design` (its design id in this run) |
| `samples` | `{sample_id: {...}}`, every physical thing made (below) |
| `events` | every booking, breakdown, refused proposal, literature step and end-of-run decision, in time order (below) |
| `iterations` | every time the policy was asked for actions (below) |
| `results` | every measurement returned to the policy, plus the hidden score of each tested alloy (below) |
| `weekly` | `atomizer_runs` per campaign per week, `atomizer_runs_total`, `weeks_below_3` (weeks with fewer than DAL #256's three runs), `rule` |
| `curves` | per campaign, `[[day, money spent, best new alloy's true utility so far], ...]` at each new tested alloy (references excluded) |
| `literature` | the campaign's literature steps, each answered by an Edison result already posted in DAL (below) |

## `samples`

Ids: `L<n>` a powder lot, `B<n>` an LPBF build, `D<n>` a DED deposit, `E8-L<n>` the E8 tensile plate of lot n.

| key | what it holds |
|---|---|
| `type` | `lot`, `build` or `deposit` |
| `campaign`, `design` | which campaign and design |
| `parent` | the lot a build or deposit was made from |
| `created_h` | when it was made (its last booking ended) |
| `status`, `detail` | how it ended, as an outcome code (below) with the reason |
| lots | `runs`, `failed_runs`, `crucible_cm3`, `cut_g` (grams in the printing cut) |
| builds | `cubes`, `bars_cube`, `sound_cubes` (dense ≥ 0.98 and crack density < 0.3 /mm²) |
| deposits | `mode` (`blend`, `preplaced`, `blown_small`, `blown_large`), `blocks` |

## `events`

One record per event, in time order:

| key | what it holds |
|---|---|
| `id` | its index |
| `t_start_h`, `t_end_h`, `duration_h`, `day` | when (simulated time) |
| `station` | the station key (`stations`), `literature` for a literature step, or null for a decision |
| `campaign`, `sample`, `design` | what it served |
| `step` | the step in plain words |
| `dal211` | the step's node in DAL #211's workflow network, or null where #211 has no such step (below) |
| `twin_node`, `what` | the twin's own node and booking kind |
| `run` | for atomizer runs, the run's index within its lot |
| `outcome`, `detail` | how it ended (below), and why |

**Outcome codes** (DAL #274's node-level ledger, Ax's trial statuses per node):

| code | meaning |
|---|---|
| `COMPLETED` | ran and measured, whatever the value |
| `FAILED` | did not produce its output for a reason outside the inputs (equipment, chance); may be retried; the node gets no data point. An atomizer run that drips at the base rate (6 % at good settings) |
| `ABANDONED` | did not produce a usable output because of its inputs: a run that drips because the melt was too cold or flooded (a drip probability more than twice the base rate), a build or deposit with no dense, crack-free cube; a viability label 0 at that node's inputs |
| `EARLY_STOPPED` | a usable part the policy chose not to take further (partial evaluation); upstream data kept |
| `STALE` | proposed but never run (refused for money, or still queued at the horizon), or made but not measured by the horizon |
| `NOT_AS_PLANNED` | ran, but what was made differs from the design (more than 15 % relative and 0.2 wt% in an element, e.g. Mg boiled off); the policy sees the executed composition in the EDS, XRF and ICP-MS numbers |
| `DOWN` | a station breakdown and its repair; bookings wait, none fail |

DAL #274's `RUNNING` (in flight) and `INCOMPLETE` (one output missing) do not occur at the end of a finished year.

## `iterations`

| key | what it holds |
|---|---|
| `campaign`, `it`, `t_h`, `day` | which campaign, the iteration's number and when |
| `n_free` | actions in flight the policy could still start |
| `spent_usd` | the campaign's money spent so far |
| `best_obs` | the policy's incumbent: the best utility it has *measured* (null before its first) |
| `best_true_new`, `best_true_all` | the hidden best so far: the best true utility of a new alloy tested, and of any alloy (references included). The policy never sees these |
| `proposals` | what it proposed: `kind` (`powder`, `blend_ded`, `print`, `section`, `pip`, `test`, a DED mode, a simulation, ...), `accepted` (false: refused for money), `design` and `x` (the design: composition and process settings) for new designs, the sample or lot for next steps, `acq` (the acquisition value), `acq_kind` (what that value is: e.g. "EI per $ (one GP, design to measured utility)", "network EI per $", "next Sobol design", "mutation of the best alloy"), and for model-based policies `ei`, `mu`, `sd` and `cost` behind it |

## `results`

`t_h`, `campaign`, `type` (`lot`, `build`, `deposit`, `tensile`, `screen`, `immersion`, a simulation kind, or
`scored (hidden)`), `sample`, `design`, and `measured` (what the lab's analysis returned: d50, cut, oxygen, EDS
composition; densities and crack density; yield, UTS and elongation; corrosion rates). `scored (hidden)` rows carry
the truth's `u_true`, `discovery` and `feasible`, which no policy sees, and `reference` (a re-test of a known alloy).

## `literature`

`t_h`, `campaign`, `decision` (the decision it informs), `question`, `edison` (where the answer is posted in DAL),
`dal211`, `reused` (always true: no new query is sent). Each also appears in `events` with station `literature`.

## DAL #211's network

The nodes are those of ONR YIP Fig. 1 ("the full workflow network"), the TikZ in
[`onr-yip-technical-proposal-cu-ded.tex` L206-L275 at DAL b4d5a89](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/b4d5a89/near-term-submissions/onr-yip/onr-yip-technical-proposal-cu-ded.tex#L206-L275)
(DAL PR 215): `p1` CALPHAD and heat flow, `p2` Charge, `p3` Atomize, `p4` Small DED (Utah), `p5` Large DED (Mines),
`p6` Microscopy, `t1` Tensile, `t2` Seawater screen, `t3` Immersion, `t4` Repair coupon. The figure draws the
copper/DED workflow only, so aluminium bookings get the same node where the step is the same one (charge, atomize,
microscopy, tensile) and null where it has none (LPBF builds, Archimedes density, PIP, heat treatment, hot tensile,
XRD, XRF, ICP-MS, the blend doser). The in-house 1 kg MX-Lab deposit takes `p5`'s place as the large deposit.
`twin/trace.py` `STEPS` is the whole map.

## DAL #256's schedule (`facility = dal256`)

The `dal256` facility is DAL's own lab on DAL #256's plan ([`al-campaign-schedule/` at DAL
6ff7717](https://github.com/vertical-cloud-lab/digital-alloy-lab/tree/6ff7717/al-campaign-schedule) and the plan in
[#256's comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/256#issuecomment-7123300072)).
Every #256 time is an estimate: "Nothing in the chain has been timed end to end". `twin/facility.py` `DAL256`.

| step | station | #256 | in the twin |
|---|---|---|---|
| Cups and plugs | shop | "ahead, in bulk", 2-3.5 h a run | off the critical path (not booked) |
| Dose, pack, press the plug, IPA clean | doser | 1-1.5 h, the day before | 1.0 h a run + 0.25 h |
| BN-coat the crucible | | 15 min + overnight dry, the evening before | not booked: fits the one-run-a-day cadence |
| Atomizer run | atomizer | 2.5-3.5 h (start-up, loading, three washes, melt, pour); Mon-Thu, one a day | the twin's run (about 2.2 h for an aluminium charge in the 225 cm³ crucible) + 3.0 h, starting 08:00 Mon-Thu |
| Cool to 400 °C and vent; collect, weigh, clean, rebuild | atomizer | ~1 h; 1-2 h | inside the + 3.0 h |
| Copper runs | atomizer | Fridays, each followed by a ~1 h full clean | Fridays only: the run (about 3.4 h) + 4.0 h |
| Sieve two splits | sieve | 1-1.5 h within 48 h | 1.25 h, day shift |
| Flowability, Hausner ratio | psd | 0.5-1 h within a week | 0.75 h |
| Powder SEM and EDS | SEM | one Thursday session for the week's powders, 4-5 h; 2-3 h a run with stubs | 1.25 h a lot, Thursdays only |
| Polishing | prep | one batch a week (Wednesday, PX500) | Wednesdays only, the twin's times |
| Hardness and density | hardness, density | Wednesday, on everything printed that week | Wednesdays only |
| Tensile, corrosion | tensile, cubxl | Thursday, daytime; corrosion daytime only | Thursdays only, day shift |
| LPBF at Utah | MIDI | 2-day sessions (Tue-Wed) on alternate weeks; each composition its own build | Tue-Wed, at most 3 builds in 14 days |
| Part removal, heat treatment, prep | | about a week after each session | the MIDI's results back 7 days after a build |
| DED at Utah | MX-Lab | 1-day sessions | Tuesdays, at most 1 in 21 days |

**Assumed where #256 gives no time:** XRD (0.75 h), XRF (0.5 h), PIP (an outside service: 0.5 h, booked 5 days
ahead, results 7 days later, after 3 h of heat treatment for aluminium), wire EDM (0.75 h,
outside, 7-day turnaround), furnace hours, machining (1 h a set of bars), a build's hours within a session (5 h), and
ICP-MS (0.1-0.4 h; 10-day turnaround at BYU's core facility). These keep the twin's own values (`twin/facility.py`,
`twin/campaign.py`). Two differences remain: #256 picks the optimizer's batch on Fridays, while the twin's policies
propose whenever a slot frees; and a booking that switches the atomizer between aluminium and copper also pays the
twin's changeover, so a few copper Fridays run past 17:00.

**At least three atomizer runs a week.** `weekly.weeks_below_3` lists the weeks that fell short. On DAL's lab these
are weeks waiting on materials ordered as they are needed (the stock is `lean`), as in #256's own plan, which has
weeks of 0-2 runs.

# A digital twin of the manufacturing network, for synthetic benchmarks

Two alloy campaigns run at the same time and are kept apart:

* **FLAIME** (DAL, Genesis Mission proposal on `consolidation-2`): aluminium alloys for laser powder bed fusion.
  Al plus 15 elements, mineral burden as an objective, CALPHAD → ultrasonic atomization → LPBF → tensile.
* **ONR YIP** (DAL PR 117, the copper-DED version): copper alloys designed as powders for blown-powder DED. Eight
  elements, nickel as an objective, CALPHAD and heat flow → atomization → small DED at Utah → 2 kg DED at Mines →
  tensile, a one-hour corrosion screen and 30-day immersion.

Each has its own search space, function network, ground truth, objectives, budget, feedstock stores, observation log
and policy. They share what a real lab would make them share: one atomizer (switching it between an Al and a Cu melt
costs a changeover), the SEM, the outside facilities, the market and the calendar. It is the "synthetic function" of
DAL's preliminary benchmark (`benchmarks/bofn-prelim`) grown into the whole network, with the limits that benchmark
listed ("no measurement noise, one objective, no corrosion branch, no process physics, and one experiment at a time")
removed. The write-up, sources and results are in [`../notes/twin.md`](../notes/twin.md).

## Run it

```bash
python3 -m venv /tmp/twinenv && /tmp/twinenv/bin/pip install numpy scipy scikit-learn matplotlib pycalphad scheil pytest
cd vertical-lab
/tmp/twinenv/bin/python -m pytest -q twin/tests                 # 17 checks, ~7 s
/tmp/twinenv/bin/python -m twin.bench one                       # one twin-year, both campaigns, printed
TWIN_WORKERS=4 /tmp/twinenv/bin/python -m twin.bench run    # every experiment, 370 twin-years, ~20 min on 4 cores
/tmp/twinenv/bin/python -m twin.figures                         # out/twin/*.png and bench_summary.json
```

Rebuilding the physics data (optional; the results are committed in `data/`):

```bash
/tmp/twinenv/bin/python -m twin.usgs extract          # USGS MCS 2026 subset (downloads 3.2 MB, sha256-checked)
/tmp/twinenv/bin/python -m twin.calphad al-dilute     # m, k at the Al corner from mc_al and COST 507
/tmp/twinenv/bin/python -m twin.calphad al-scheil     # Scheil on 7 reference Al alloys
/tmp/twinenv/bin/python -m twin.calphad cu-design 480 # equilibrium over 483 Cu compositions (~5 min, 3 cores)
```

## Use it from an optimizer

A policy is anything with `propose(view, n_free) -> [action, ...]`. The twin calls it whenever one of the campaign's
results comes back (and once a day while nothing is in flight), with `n_free` slots under the campaign's work-in-
progress cap. `view` is what the lab would know: designs, simulation outputs, lots with measured size, oxygen and EDS
(ICP-MS when bought), builds or deposits with measured density, cracks, beta', tensile and corrosion results, money
left, and `estimate(action)` for an action's rough cost. It never contains the truth.

```python
from twin import campaign as C, policies as P
specs = {"flaime_al": C.Spec("flaime_al", 120_000, wip=24, seed=0),
         "onr_cu":    C.Spec("onr_cu",     60_000, wip=8,  seed=0)}
pols  = {"flaime_al": MyPolicy("flaime_al"), "onr_cu": P.CostAware("onr_cu")}    # mix freely
twin  = C.Twin(specs, pols, scenario="tariffs", facility="vertical_lab", seed=0, horizon_days=365)
out   = twin.run()        # per campaign: best-so-far curve (days, $, utility), spend by kind, orders, ...
```

Actions are dicts. FLAIME: `sim_open | sim_tc | sim_am` (`design`), `powder` (`design`, `runs`, `icp`), `print`
(`lot`, up to 9 `params`, `bars_at`), `test` (`build`, `hot`), `promote` (`lot`, `params`), `gas_atomize` (`design`:
Valimet, 50 kg). ONR: `sim_open | sim_tc | sim_heat`, `powder` (`into` tops up an earlier lot), `nsl`, `preplaced |
small_ded` (`lot`, up to 4 `params`), `large_ded` (`lot`, `params`), `tensile | screen | immersion` (`deposit`),
`gas_atomize` (`design`: Ames). A design is a composition in wt% plus the
process settings of `spaces.AL` / `spaces.CU`; `space.encode`/`decode` map it to and from [0, 1]^d.

DAL's BOFN and pKGFN (`benchmarks/bofn-prelim/bofn_alloy.py`) plug in as a policy: their stages map onto these actions
(CALPHAD → `sim_*`, atomize → `powder`, print → `print`/`small_ded`/`large_ded`, test → `test`/`tensile`/
`immersion`), and their GP nodes read the measured outputs from `view`.

## Round 2 (2026-11-25): every instrument simulated, real optimizers, economics, a video

Round 1 (above, `notes/twin.md`) built the network, the market and the facility with plain noise on each measured
number. Round 2 replaces that noise with the instruments themselves and adds what is needed to say how much faster and
cheaper the vertical lab finds alloys. The write-up and results are in [`../notes/twin_round2.md`](../notes/twin_round2.md).

| Piece | Code | Notes |
|---|---|---|
| Instrument simulators: raw data (micrographs, spectra, patterns, curves) and the lab's own analysis, with calibrated fast modes | `instruments/` (`sem eds ebsd xrd xrf icpms micro` and `psd atomize_yield reuse density tensile pip hardness corrosion mech`) | `notes/twin_instruments_micro.md`, `notes/twin_instruments_mech.md` |
| The vertical lab's instruments as partial evaluations (section with SEM/EBSD/XRD/Vickers, PIP, the CubXL screen), powder reuse, the 225 or 400 cm³ crucible, in-house DED blocks for bars, a stocked inventory, blended-powder DED screening for copper, the event log | `campaign.py`, `facility.py`, `truth_cu.py` | `notes/twin_round2.md` |
| Policies on BoTorch: Sobol, a metallurgist's heuristic, GP-BO, SAASBO (NUTS and MAP), BOFN with partial evaluations (atomize, print, EBSD section, PIP and tensile nodes; DED, PIP, screen, tensile and immersion for copper), BOFN with blend screening | `opt/` | `notes/twin_round2.md` |
| The truth without a lab: state-of-the-art targets, the landscape, how well the screens rank | `oracle.py` | |
| The benchmark, its summary and figures | `bench2.py`, `figures2.py` | |
| Capex, cost per alloy with and without capital, utilization, outside (cloud user facility) work, acceleration factors | `econ.py`, `cloud.py`, `accel.py` | `notes/twin_econ.md` |
| The campaign trace: every booking with its sample, its node in DAL #211's network and its outcome (DAL #274's ledger), every sample, the optimizer's state at each iteration, the literature steps (DAL's own Edison answers); DAL #275's common seed set | `trace.py`, `seeding.py` | `../out/twin2/trace/README.md` |
| DAL's own lab on DAL #256's schedule (facility `dal256`) | `facility.py` (`DAL256`) | `../out/twin2/trace/README.md` |
| The campaign video | `video/` | `notes/twin_video.md` |

```bash
cd vertical-lab
/tmp/venv/bin/pip install numpy scipy scikit-learn scikit-image matplotlib pillow pycalphad scheil pytest "botorch[fully_bayesian]"
/tmp/venv/bin/python -m pytest -q twin/tests                      # round 1 + instruments + economics
/tmp/venv/bin/python -m twin.oracle                               # out/twin2/oracle.json (targets)
TWIN_WORKERS=3 /tmp/venv/bin/python -m twin.bench2 run main cu_hidden cu_proxy conventional stock crucible reuse
TWIN_WORKERS=3 /tmp/venv/bin/python -m twin.bench2 run seeded seeded_dal256 saas cu_money   # traces: out/twin2/trace/
/tmp/venv/bin/python -m twin.figures2                             # out/twin2/fig/
/tmp/venv/bin/python -m twin.econ all                             # out/twin2/econ/
/tmp/venv/bin/python -m twin.instruments.gallery_micro; /tmp/venv/bin/python -m twin.instruments.gallery_mech
```

`TWIN_INSTRUMENTS=stub` swaps every simulator for round 1's plain noise (for development).

## What is real, what is ours

| Layer | Source |
|---|---|
| Search spaces and rules | the proposals, verbatim (`spaces.py`) |
| Prices, import reliance, critical flags | USGS MCS 2026 data release, live download (`usgs.py`) |
| Al solidification | pycalphad on MatCalc mc_al and COST 507 (open node); assessed binary diagrams (truth); `thermo.py` |
| Cu thermodynamics | pycalphad on MatCalc mc_ni over 483 compositions, emulated (`calphad.py`, `thermo.py`) |
| Lab-lot prices and lead times | DAL's 2026 procurement threads, aggregated (`supply.py`) |
| Stations, rates, turnaround | the proposals' budgets and DAL's experience; PR 318's `timelapse.py` for the vertical lab (`facility.py`) |
| Process physics | Lang (atomizer), Rosenthal, King et al. (keyhole), Tang et al. (lack of fusion) (`physics.py`) |
| Strength, ductility, corrosion | textbook forms with coefficients calibrated on 7 reference alloys; ours (`truth_al.py`, `truth_cu.py`) |
| Thermo-Calc (TC-Python, TCAL/TCCU, AM Module) | interface only (`calphad.ThermoCalcBackend`); its nodes are the truth plus a small error until it runs on BYU's HPC |
| Private quotes and rates | not committed: put them in `data/private/prices.json` (git-ignored) and `supply.load_private()` uses them |

## Round 3 (2026-11-26): physical capacity, asynchronous acquisition, interim readings, pKGFN, time to discovery

Round 2 capped each campaign's work in flight (24 aluminium actions, 8 copper) and asked a policy for that many actions
only when results came back, so a 30-day immersion held one of copper's eight slots for a month. Round 3 removes the
cap; what limits work is what limits it in a lab. The write-up and results are in
[`../notes/twin_round3.md`](../notes/twin_round3.md).

| Piece | Code |
|---|---|
| The asynchronous engine, opt-in (`Twin(..., mode="async")`): hourly decisions whenever a station, robot, person or fixture frees up or results come back; an action starts if its gating station can take it within 2 h and the spending plan allows it (spent in the policy's own ranking); campaigns take the shared atomizer by deficit | `campaign.py` (`run_async`, `submit3`, `gate_ok`, `plan`) |
| Physical capacity: PR 318's two robots and the technician (vertical lab), three operators doing each station's hands-on hours (conventional lab), immersion and furnace positions; joint booking of a step with its helpers; early release of a fixture | `facility.py` (`PHYSICAL`, `run_step_joint`, `Resource.find/commit/release_early`) |
| Interim immersion readings (days 1, 3, 7, 14) from the coupon's own film-growth trajectory, a stop action | `campaign.py` (`_interim`, `_do_immersion3`, `_do_stop`) |
| Every policy on the engine: an adapter for random, Sobol and the heuristic; the funnel; GP-BO with a kriging believer; BOFN and pKGFN on every node of every part, per-dollar or time-aware | `opt/policies3.py`, `opt/net3.py`, `opt/tinygp.py` |
| The benchmark, figures, economics | `bench3.py`, `figures3.py`, `econ3.py` |

```bash
cd vertical-lab
/tmp/venv/bin/python -m pytest -q twin/tests/test_round3.py
TWIN_WORKERS=4 /tmp/venv/bin/python -m twin.bench3 run main cu_hidden cu_proxy cu_ablation cu_money conventional main_more
/tmp/venv/bin/python -m twin.figures3 && /tmp/venv/bin/python -m twin.econ3 pkgfn3
```

Round 2's engine is unchanged in `mode="wip"`, except one fix behind a flag: `Campaign._cu_check` scored a copper alloy
when its tensile came back if its immersion had only started. `twin/bench2.py` keeps the old check
(`legacy_cu_check`), so round 2's committed results reproduce; `TWIN_FIX_CU_CHECK=1` runs round 2 with the fix.

**Round 3's video** is built by `twin/video/` with `TWIN_VIDEO_ROUND=3` (the cards in `video/figs3.py`, their numbers
in `video/numbers3.py`, the script in `video/narration3.json`): see
[`../notes/twin_video.md`](../notes/twin_video.md#round-3s-video). `python -m pytest -q twin/tests/test_video_round3.py`
checks every spoken number against the committed summaries.

## Round 3b (2026-11-26): round 3 reproduces, and the lab comparison like with like

Round 3's BOFN and pKGFN rows depend on the floating-point kernels the BLAS libraries pick for the CPU (AVX-512 on
round 3's runner), and, in the last bit now and then, on Python's per-process string hashing. Round 3b pins both, and
reruns round 3's committed rows to check. It also runs the missing arms of the lab comparison: the vertical lab
ordering metal as it goes, and the conventional lab stocked. Every seed now has an event log. The write-up is
[`../notes/twin_round3b.md`](../notes/twin_round3b.md).

| Piece | Code |
|---|---|
| The pin (one BLAS thread, the AVX-512 kernels, `PYTHONHASHSEED=0`, global generators seeded per run, the set-up recorded in every row), applied when `twin` is imported; `check` reruns BOFN seed 0 for 30 days against the committed log, `row` reruns a whole committed row | `repro.py`, `__init__.py` |
| `Twin.stop_h`: end a run early without changing its horizon (the spending plan still sees the full year) | `campaign.py` |
| The runs: the missing arms (`v_lean`, `c_stocked`, `c_lean_net`) and round 3's runs again for their event logs (`re_main`, `re_main_more`, `re_conventional`), xz-compressed logs in `out/twin3b/events/` (`bench3b.read_events`) | `bench3b.py`, `bench3.py` (`simulate`) |
| The comparison four ways, the median seeds for a replay, the figure | `like3b.py`, `figures3b.py` |

```bash
cd vertical-lab
/tmp/venv/bin/python -m twin.repro check
/tmp/venv/bin/python -m pytest -q twin/tests/test_round3b.py
TWIN_WORKERS=4 /tmp/venv/bin/python -m twin.bench3b run v_lean c_stocked c_lean_net re_main re_main_more re_conventional
/tmp/venv/bin/python -m twin.like3b && /tmp/venv/bin/python -m twin.figures3b
```

**Round 3b's video** is round 3's cut again with these results (`TWIN_VIDEO_ROUND=3b`: the cards in `video/figs3b.py`,
their numbers in `video/numbers3b.py`, the script in `video/narration3b.json`). It leads the lab comparison with like
for like, shows the stock as its own effect, and replays the replay arm's two median seeds. See
[`../notes/twin_video.md`](../notes/twin_video.md#round-3bs-re-cut). `python -m pytest -q
twin/tests/test_video_round3b.py` checks every spoken number against `like3b.json` and the cells against `tables.md`.

## Round 4 (2026-11-26): building the lab while running real experiments, every route at once

Round 3 started with the vertical lab built. Round 4 counts from the day the funding arrives. The in-house stations are
ordered then and come online after their lead times, installation and commissioning, and ramp up on a learning curve
fitted to the lab's own atomizer runs. Meanwhile the campaigns run on the existing atomizer, BYU's own equipment and
every partner route, and a router sends each step to whichever route returns its result first. The write-up and
results are in [`../notes/twin_round4.md`](../notes/twin_round4.md).

| Piece | Code |
|---|---|
| Build-out: the stations' lead times (stand-ins), installation once the room is fitted out, commissioning, the cell's integration, capital payments | `round4.py` (`BUILD`, `build_schedule`) |
| Ramp-up: the learning curve fitted to DAL PR 286's ten atomizer runs (redone jobs, slower jobs, equipment faults) | `round4.py` (`LEARN`, `fit_learning`, `Resource4`, `Facility4.job_done`) |
| Routes: in house, BYU, Utah's MIDI and MX-Lab, 3D Powder Tech, Mines, Valimet, outside testing; standing slots filled as late as possible; site offsets and provenance visits | `round4.py` (`STANDING`, `EXTRA`, `OFFSETS`, `PROVENANCE`, `Facility4.pick`, `Campaign4`) |
| Two admission rules for every policy: money kept for the coming week's standing slots, and a WIP limit before the first fabrication step | `round4.py` (`Campaign4.reserve`, `Campaign4.submit3`) |
| The stages after discovery: a gas lot, a validation network across the sites, a full-part test | `round4.py` (`STAGES`, `Twin4._stage_tick`) |
| The three plans (wait for the cell, ramp up in parallel, external routes only), the benchmark, tables and figures | `bench4.py`, `figures4.py` |

```bash
cd vertical-lab
python -m pytest -q twin/tests/test_round4.py
TWIN_WORKERS=4 python -m twin.bench4 run plans plans_best plans_3x provenance routes nolearn
python -m twin.figures4
```

Round 3's code is unchanged: round 4 subclasses `Facility`, `Campaign` and `Twin`.

## Round 5 (2026-11-27): two years from the day the money arrives, the automated lab against a conventional lab

All money at t = 0; the facility ready between day 60 and day 100; used equipment by a rule; a reorder-point stock
heuristic (and a look back at what should have been bought); copper's route with the steps the real process needs;
decision windows for people; Sterling's four notes while it ran (8 atomizations a week in the conventional lab; the
automated atomizer 24/7 at a cycle derived from the lab's record; idle stretches with causes; a continuous HPC stream
of simulated candidates). The write-up and results are in [`../notes/twin_round5.md`](../notes/twin_round5.md).

| Piece | Code |
|---|---|
| The facility window, used equipment (stand-ins and the rule) | `round5.py` (`ROOM_DAYS`, `USED_OK`, `USED`, `used_rule`, `build_schedule5`) |
| The atomizer: 8 a week by people, 24/7 at the derived cycle once the cell is integrated | `round5.py` (`ATOM_MANUAL`, `ATOM_CYCLE`, `ResourceAtom`) |
| Decision windows (review, meeting, sign-off), per lab and per kind of decision | `round5.py` (`DECISIONS`, `Decide`, `Twin5.run_async`) |
| Copper's and aluminium's added steps on the shared stations | `round5.py` (`CU_STEPS`, `AL_STEPS`, `Campaign5`) |
| Money at t = 0, money kept for the work in progress, the stock heuristic and its money rules | `round5.py` (`Campaign5.plan`, `wip_reserve`, `REORDER`, `_reorder`) |
| The HPC stream (note 4) | `round5.py` (`HPC`, `Twin5._stream_tick`) |
| Reports: shared stations by campaign, idle stretches with causes, counters, stock | `round5.py` (`shared_use`, `idle_report`, `counters`, `Campaign5.stock_report`) |
| The runs (every row under `TWIN_PIN=avx2`, with its commit, CPU, kernels and notes), comparisons, figures | `bench5.py`, `like5.py`, `figures5.py` |

```bash
cd vertical-lab
python -m pytest -q twin/tests/test_round5.py
TWIN_WORKERS=4 python -m twin.bench5 run arms plans dec_none dec_slow atom noused hpc_more net net_more plans_net
python -m twin.bench5 pack && python -m twin.like5 && python -m twin.figures5
```

Every planned run is committed (488 rows; `python -m twin.bench5 status` says 0 left), so `run` has nothing to do. The
last 69 (the automated lab's BOFN and pKGFN seeds and the plans with BOFN) were made in six compute slices and
folded in: their drivers, their checks and the fold's check are in `../out/twin5/slices/`. A BOFN or pKGFN row
reproduces bit for bit only on some CPU models (the notes' "Reproducibility").

Round 4's code is unchanged but for a hook (`Facility4.schedule`): round 5 subclasses `Facility4`, `Campaign4` and
`Twin4`.

# Digital twin, round 2: every instrument simulated, real optimizers, what it costs, and a video

Sterling, on PR 318 (2026-11-25): "open a new PR in relation to [the digital twin] ... that also contains the
results from that session. This time, consider that there is lots of equipment available. You should be making
synthetic functions and/or using simulations, etc. for everything from desktop SEM + EDS + EBSD (simulated
micrographs, spectra, and patterns), to particle size analysis (PSD), yield, powder XRD, PIP, and other various
characterization, synthesis, and processing modules. ... The synthetic functions should not be dumbed down. Also,
the Cu benchmark may need some further investigation given that tiered BO was on par with BOFN. ... SAASBO ... consider
both the optimization efficiency in terms of budget (esp. compared to random and some DoE method like Sobol or
something simple and heuristic), as well as the throughput increase and the overall reduction in cost per experiment
... Make sure you're also considering powder reuse and allowing for the option of a 400 cm^3 crucible ... percent
utilization across core instruments, from a cloud user facility perspective."

Round 1 is [`twin.md`](twin.md) (the network, the market, the facility, the first 370 twin-years). This file is
round 2: what changed, how it is checked, the results, the copper investigation, and what is assumed. The
instruments have their own notes ([microscopy and diffraction](twin_instruments_micro.md),
[powder, mechanics and corrosion](twin_instruments_mech.md)), as do the [economics](twin_econ.md) and the
[video](twin_video.md).

## 1. The instruments: raw data, then the lab's own analysis

Round 1 measured every quantity as the truth plus a Gaussian. Round 2 makes each instrument's raw data from the
artifact's hidden state, then runs the analysis the lab would run on it. The errors, biases, detection limits and the
correlations between instruments come out of that chain, because every instrument looks at the same hidden part.

| Instrument | Raw data it makes | What the analysis returns | What emerges (not imposed) |
|---|---|---|---|
| SEM, powder (TM4000) | secondary-electron image of particles: lognormal sizes from the lot's runs, satellites, ligaments from cold melts, edge brightness, shot noise | sphericity, satellite share, image d50 | projection bias of image sizing; satellites hide in clusters |
| SEM, section | backscattered image of a polished section: phases by mean Z, lack-of-fusion, keyhole and gas pores, hot cracks along columnar boundaries, scratches | porosity, largest pore, lack-of-fusion share, crack length per area | a single section misses sparse large pores; resolution floor for small ones |
| EDS (desktop SDD) | 0-20 keV spectrum: bremsstrahlung, K/L/M lines, Fano-limited resolution, escape and sum peaks, dead time, counting noise | composition with 3σ detection limits | real overlaps (Er M/Al K, Mn Kβ/Fe Kα, Ni Kβ/Cu Kα, Cu Kβ/Zn Kα, Ti Kβ/Ce Lα); Li invisible; light elements worse on powder |
| EBSD | orientation map (columnar <100> fibre or equiaxed grains), indexing that fails at strain, pores and martensite; Kikuchi patterns in full mode | grain size, equiaxed share, texture strength, indexed share, KAM, β′ share | β′ under-counted against XRD because martensite indexes poorly |
| XRD (MiniFlex) | Bragg-Brentano pattern: structure factors, Lorentz-polarization, Kα1/Kα2, Scherrer and strain broadening, preferred orientation, displacement, counting noise | phases by whole-pattern fit, FCC lattice parameter, solute estimate, crystallite size, β′ | detection limits of 1-3 wt% (Mg₂Si at 0.2 wt% is not seen) |
| XRF (S2 PUMA) and ICP-MS | element-dependent precision; the ICP-MS digest is HF-free | composition | ICP-MS loses Si above ~1 wt% (no HF in this lab), so silicon comes from XRF |
| Laser diffraction (Mastersizer) | the lot's volume distribution through the instrument's optical model and dispersion | d10/d50/d90, span, in-cut and fines shares | agglomerates and satellites shift the coarse tail |
| Yield (balances, sieves) | the run-by-run mass balance | charge, collected, in-cut grams | sieving loses about 15 % of the ideal cut for coarse Al lots |
| Archimedes density | weighings in air and liquid | relative density against the designed composition | open, surface-connected porosity reads as solid; Mg boil-off reads high |
| Tensile (3 sub-size bars) | full curves: compliance, Voce plasticity, necking, fracture at each bar's worst defect (weakest link) | 0.2 % yield, UTS, elongation | scatter grows with defects; cracked bars break before yield |
| PIP (Plastometrex) | indent profile from the Voce law, profilometer noise | yield, UTS, uniform elongation by inverse fit | samples ~1 mm³ of sound metal, so it over-reads porous or cracked parts (+18 % on average) |
| Vickers, nanoindentation | indent diagonals; Oliver-Pharr load-displacement | HV; H and E | size effect; pores under indents |
| CubXL corrosion screen | OCP drift, LPR, EIS, cyclic polarization | Rp, icorr, early rate, Rct, Eb, Erp | the Tafel fit reads 1.5-1.75x the true early rate |
| 30-day immersion | mass loss; SEM of selective attack; ICP-MS of the solution | 30-day rate, attack depth, Cu and Ni release | |

Every simulator has three fidelities: `full` (publication-size raw data and the analysis), `lite` (small raw data and
the same analysis, under ~30 ms) and `fast` (under 1 ms, errors sampled from distributions fitted to many lite runs,
state-dependent, checked against lite by the tests). The benchmark runs in `fast`. The galleries in
`out/twin2/instruments/` show each instrument's raw data and what its analysis extracted.

**Found by the simulators, then fixed in how the lab checks a part.** With Archimedes alone, a part's density read
0.3 % high on average with a 0.9 % spread, because lack-of-fusion pores open to the surface fill with water; 17 % of
cubes read as dense (≥ 99.5 %) when they were not. The print and DED routes already book an hour of SEM, so every
made part is now checked by Archimedes and by its polished section imaged in the SEM, and the lower density is the one
reported (`Campaign._soundness`). That removes the bias (−0.02 %); what is left (0.6 % spread, about 12 % of cubes on
the wrong side of the 99.5 % gate each way) is the real difficulty of telling 99.4 % from 99.6 %.

## 2. The campaign engine

* **Partial evaluations the vertical lab can buy** besides round 1's: `section` (cut, mount, polish; SEM, EBSD and a
  Vickers row; XRD for copper), `pip` (aluminium coupons are heat-treated first, like the bars) and, for copper,
  `blend_ded` (below).
* **The crucible**: the rePowder's standard 225 cm³ crucible or the 400 cm³ upgrade (DAL #219). The charge per run,
  the run time, the consumables and the added drip risk come from `atomize_yield.charge_plan`; a policy picks it per
  run.
* **Powder reuse**: the unfused powder of every LPBF build (about 18 of the 30 g a 55 mm kit spreads, 370 of the 440 g
  of an E8 plate) and the overspray of every DED deposit is sieved and returned to its lot, with more oxygen and
  satellites (`reuse.after_build` / `after_ded`), blended by mass. Every later part made from the lot carries it.
* **In-house DED blocks for bars** (vertical lab): 1 kg on the MX-Lab, no NSL certificate and no Mines queue.
* **A stocked inventory** (vertical lab): consumables and every feedstock but Sc and Er bought at day 0 at the day's
  prices and charged to the campaign, reordered four times over. Ordering each charge's metal as it is needed (round
  1, and DAL today) left the atomizer 89 % idle in a development run while work in flight waited on orders; at 12
  seeds it delays the state of the art 1.5-2.9× (section 5.6).
* **Booking tags and an event log**: every booking records the design and the network node it served
  (`Twin.event_log`), which is what the video and the utilization study read.
* **External load**: `Twin(..., external=callable)` lets outside users' jobs take slots before the campaigns run.
* **DAL's own lab on DAL #256's schedule** (facility `dal256`, `twin/facility.py` `DAL256`): the conventional lab's
  stations on #256's calendar and step times: one atomizer run a day Mon-Thu with copper on Fridays, a run plus about
  3 h to cool, clean and rebuild, a Thursday SEM session and a Wednesday polishing batch, tensile and corrosion on
  Thursdays, two-day Utah LPBF sessions on alternate weeks with parts back a week later. The times #256 doesn't give
  keep the twin's own; `out/twin2/trace/README.md` lists both.
* **The campaign trace** (`twin/trace.py`, schema in `out/twin2/trace/README.md`): every booking with its sample, its
  node in DAL #211's network and its outcome in DAL #274's ledger (`COMPLETED`, `FAILED`, `ABANDONED`,
  `EARLY_STOPPED`, `STALE`, `NOT_AS_PLANNED`, `DOWN`), every sample, every measurement, the optimizer's state at every
  iteration (what it proposed, the acquisition value, its incumbent and the hidden best so far), and the literature
  steps a campaign would run, each pointing at an Edison answer already in DAL (no new queries). A traced run gives
  the same results as an untraced one.
* **A common seed set** (`twin/seeding.py`, DAL #275): the seeded runs start every policy from the same seven
  aluminium seeds (D1 and D2 baselines, the B30 and B15 dosing checks, the S1 and S2 literature picks, the S3 IMSE
  pick) and five copper seeds built the same way (#275 plans aluminium only), so that no policy's lead is a warm
  start.

## 3. The policies

All are `propose(view, n_free)` on the twin (`twin/opt/policies2.py`, BoTorch 0.18):

* **Random** (round 1: every design through the whole chain) and **Sobol** (a scrambled Sobol design, made in order).
* **Heuristic**: start from the reference alloys (AlSi10Mg, Al-Mn-Cr-Zr, Al-Zr; 90-10, 70-30, NAB), keep the best
  measured alloy, try one or two elements up or down from it with the process settings that worked.
* **Tiered** (round 1): screen 256 designs with the open CALPHAD node, make the 24 the proxy likes best, in order.
* **Round-1 cost-aware GP**: a GP on the final utility with CALPHAD features, the proxy before four results.
* **GP-BO**: a GP (BoTorch's `SingleTaskGP`) from the whole design (d = 23 for FLAIME, 14 for copper) to the measured
  utility, expected improvement per dollar over a pool of Sobol points and local moves, the reference alloys as its
  first designs. **SAASBO**: the same with the sparse axis-aligned subspace prior, fully Bayesian (NUTS, 128 warm-up,
  128 samples thinned to 16) and at its MAP point. A NUTS fit took 25-170 s at 30-140 points on the runner, so a fresh
  chain at every new result would have cost about 33 CPU-hours for 12 seeds: SAASBO runs a fresh chain each time its
  data have grown by 4 points and by half (at 3, 7, 11, 17, 26, 39, 59, 89, 134, ... points), and in between rebuilds
  the model on the new data with the last chain's hyperparameter samples, as the MAP GPs reuse theirs.
* **BOFN**: a GP per node of the function network, each node's inputs its parents' measured outputs plus the design
  variables acting on it; the utility computed through MC samples of the network; expected improvement per dollar for
  new designs and for every next step of a part already made. FLAIME: atomize → print → EBSD section → PIP → tensile.
  Copper: atomize → DED → PIP and CubXL screen → tensile and 30-day immersion of a 1 kg deposit. Partial evaluation
  (in the spirit of pKGFN): a sound part gets the cheap nodes (PIP, section, screen) at once, and the dear step
  (bars, a 1 kg deposit) only when its posterior expected improvement per dollar beats starting something new. The
  atomize node picks the atomizer settings; the print and DED nodes pick the process settings. Same reference start as
  GP-BO.
* **BOFN + blend screen** (copper): every new composition is first deposited from blended elemental powders on the
  MX-Lab (no atomizer run, about $250 with PIP and the screen), and atomized only when the network, which carries a
  blend/atomized flag on its DED, PIP, screen, tensile and immersion nodes, says it is worth it.

## 4. Targets: the state of the art, from the truth itself

`twin/oracle.py` scores the reference alloys and 1,500 random designs on the truth, each at the best of 12 process
settings (24 for the references and the best 40 designs), then hill-climbs on the truth for an upper reference. It
also ranks the same 1,500 designs with the tiered funnel's screen and proxy (`out/twin2/oracle.json`):

| | best reference (the state of the art) | random designs above it | best the oracle found | proxy vs utility (Spearman, feasible designs) | the funnel's top 24: mean utility; above the state of the art |
|---|---|---|---|---|---|
| FLAIME | AlSi10Mg, 0.42 (Scalmalloy fails the mineral gate) | 8.2 % | 0.86 (Al-0.6Mn-0.5Zr-0.2Mg-0.4Fe-2Li) | 0.46 | 0.28; 42 % |
| ONR | NAB, 0.56 (70-30 has 30 % Ni) | 8.2 % | 0.76 (Cu-7.0Ni-8.0Al-1.6Fe-0.1Ti) | 0.40 | 0.46; 33 % |

(An earlier version of this table, from a run before the oracle tuned each design's process, gave 7.2 % and 0.5 %
above the state of the art and Spearman 0.51 and 0.007; `oracle.json` as committed is the version above.)

**T1**: a new alloy (not a re-test of a reference) at or above the state of the art. **T2**: halfway from the state of
the art to the oracle's best (0.64 for FLAIME, 0.66 for copper). Curves and targets count new alloys only.

## 5. Results

*Checked against `out/twin2/fig/tables.md`, `bench2_summary.json` and the per-run logs (`out/twin2/runs/`). Standard
errors are the sample standard deviation (n − 1) over seeds divided by √n. Everything here is simulated, not
measured.*

**What this shows.** Before any equipment is bought, the digital twin simulates the whole alloy-discovery workflow,
with real prices, lead times and machine schedules. Search strategies and lab designs compete for a simulated year
against the same hidden, synthetic "true" alloy landscape, so each is scored on what it actually found and what it
cost.

**The setup.** Two campaigns share one lab: aluminum alloys for laser powder-bed printing (named FLAIME after its
proposal; $120k a year for materials and services) and copper alloys for directed energy deposition, a blown-powder
printing process (DED; from an Office of Naval Research proposal; $60k a year). Each has a hidden property map
(textbook formulas calibrated on 7 known alloys) that the strategies never see, plus open CALPHAD thermodynamics,
USGS metal prices with supply shocks, and lead times from the lab's own purchasing [1]. **The score** (0 to 1)
combines strength, ductility and either mineral-supply burden (aluminum) or seawater corrosion and nickel (copper). It
is zero unless the part is dense and crack-free, and it is computed on the hidden truth for the best alloy actually
made and tested [1]. On this truth the best existing alloy scores 0.42 for aluminum (AlSi10Mg) and 0.56 for copper
(nickel-aluminum bronze); a direct search of the truth found 0.86 and 0.76 [2].

### 5.1 Round 1 (Nov 24): simple strategies, plain measurement noise

370 simulated years, with simple strategies: random recipes, a "tiered" screen that ranks recipes by a cheap
thermodynamic calculation, and a cost-aware model that weighs each test's expected gain against its price. The full
optimizer was not yet plugged in [1, 7].

- **Strategy matters.** Aluminum, 20 simulated years each: cost-aware model 0.63 ± 0.03, random recipes 0.15 ± 0.06.
- **Parallel work makes a year enough.** With one experiment in flight at a time, almost nothing good got through in a
  year (aluminum 0.07, copper 0.08); with 24 and 8 in flight, 0.64 and 0.56.
- **Vertical lab against the partner facilities named in the proposals** (own instruments around the clock, against
  booking lead times, turnaround and session caps; cost-aware model, 10 simulated years each): aluminum 0.70 ± 0.02
  against 0.64 ± 0.03; a score of 0.6 reached in 90% against 50% of runs, at a median $31k and 94 days against $43k
  and 114 days; 4.7 against 2.3 "discoveries" a year (alloys passing the proposal's strength and ductility bar).
  Copper: 0.65 ± 0.02 against 0.56 ± 0.07 [1].

(Round 1's standard errors are as `notes/twin.md` reports them.)

### 5.2 Round 2 (Nov 25): every instrument simulated, real optimizers

Each instrument (SEM, EDS, EBSD, XRD, XRF, ICP-MS, particle sizing, Archimedes density, tensile, small-sample
indentation testing called PIP, hardness, corrosion) now makes raw data from the part's hidden state, and the lab's own
analysis runs on it, so errors and biases emerge instead of being assumed [3]. Setup: the vertical lab design, one
year, both campaigns, the same budgets, 8 strategies × 12 random seeds (96 simulated years) [3, 5]. The strategies
[3, 8]:

- **Random**, and **Sobol** (recipes spread evenly over the design space). Neither learns.
- **Heuristic**: a metallurgist without a model. Start from known alloys, nudge one or two elements.
- **Tiered screening**: rank 256 recipes by a cheap CALPHAD calculation, make the top 24.
- **GP-BO** (standard Bayesian optimization): one model from recipe to final score; it picks the next test by expected
  gain per dollar.
- **BOFN** (Bayesian optimization of function networks): one model per workflow step (powder, print, polished section,
  PIP, tensile), so cheap intermediate results teach it, and a part goes on to the costly step only when that is the
  best use of the money. **+ blend screen** (copper only): each new recipe is first deposited from mixed elemental
  powders (about $250) and atomized only if promising.

"Best new alloy": true score of the best new alloy made in the year (re-tests of known alloys don't count), mean ±
standard error over 12 runs. "Halfway": halfway from the best existing alloy to the best found on the truth (0.64
aluminum, 0.66 copper) [2, 4, 5].

| Strategy | Al: best new alloy | Al: runs reaching halfway | Al: runs beating today's best; median days | Cu: best new alloy | Cu: runs reaching halfway |
|---|---|---|---|---|---|
| BOFN, set A (Cu also plain BOFN) | 0.65 ± 0.03 | 67% | 92%; 123 | 0.33 ± 0.09 | 8% |
| BOFN, set B (Cu with blend screen) | 0.69 ± 0.01 | 83% | 100%; 116 | 0.67 ± 0.01 | 58% |
| Heuristic | 0.60 ± 0.02 | 25% | 100%; 37 | 0.58 ± 0.02 | 17% |
| Round-1 cost-aware model | 0.55 ± 0.08 | 50% | 83%; 48 | 0.63 ± 0.02 | 42% |
| GP-BO | 0.46 ± 0.07 | 17% | 83%; 185 | 0.53 ± 0.06 | 17% |
| Tiered screening | 0.34 ± 0.09 | 17% | 58%; 60 | 0.69 ± 0.02 | 75% |
| Sobol | 0.10 ± 0.05 | 0% | 8% (1 run) | 0.45 ± 0.05 | 8% |
| Random | 0.10 ± 0.06 | 8% | 8% (1 run) | 0.35 ± 0.08 | 17% |

![Round 2 best new alloy against days, by strategy](../out/twin2/fig/twin2_best_vs_days.png)
*Round 2, simulated: best new alloy so far against days, mean ± standard error over 12 runs per strategy; aluminum
left, copper right. Dotted line: the best existing alloy on this synthetic truth [9].*

- **Aluminum: BOFN finishes highest and most reliably** (0.65 to 0.69; halfway in 67% to 83% of runs, against 25% for
  the heuristic). The heuristic beats today's best fastest (median 37 days against about 120), then stalls: BOFN's
  edge is a better final alloy, not a faster first one. Standard GP-BO trails the heuristic on both campaigns [4, 5].
- **The two BOFN sets run the same aluminum strategy**; only the copper strategy sharing the lab (and its atomizer)
  differs, so 0.65 against 0.69 is run-to-run spread [8].
- **Copper: no clear winner, and plain BOFN fails.** Tiered screening (0.69 ± 0.02) edges BOFN with the blend screen
  (0.67 ± 0.01) and beats today's best sooner (median 88 against 225 days). Plain BOFN scores 0.33, no better than
  random (0.35); 5 of its 12 runs ended the year with no new alloy scoring above zero. Copper results are slow and
  costly, so a model has little to learn from; the cheap blend screen supplies more data [1, 4, 5]. The copper test is
  also too kind to tiered screening: its screen uses the truth's own strengthening coefficients. Section 5.3 reruns it
  with an effect the screen cannot see.
- **Fidelity check.** With slower, fuller instrument simulators, BOFN scored 0.665 against 0.690 on aluminum and 0.36
  against 0.36 on copper (the same 3 seeds) [4].

### 5.3 The copper tie, tested four ways: none favors BOFN

In the main benchmark, tiered screening edged BOFN with the blend screen on copper (0.69 against 0.67) and plain BOFN
failed (0.33). Round 2's first reading was that the copper truth was too kind to the funnel: nothing in it was hidden
from the CALPHAD screen, and the funnel's proxy reads the truth's own strengthening coefficients (14 MPa per wt% Al,
2.6 Ni, 6 Mn; `truth_cu.CuTruth.strength`). Four tests, 12 seeds each, same seeds as the main benchmark:

**A hidden effect: γ₂ (`cu_hidden`, 7 policies × 12 seeds).** Above Al = 8.2 + Ni/2 wt%, nickel-aluminium bronze keeps
γ₂ (Cu₉Al₄), which corrodes selectively in seawater and embrittles it (the Weill-Couly/Meigh rule). The CALPHAD nodes
don't report it. In the truth (`truth_cu.CuTruth`, `gamma2`), with g₂ the wt% of Al above the line, elongation falls by
a factor e^(−1.2 g₂), the 30-day corrosion rate rises by a factor 1 + 2.5 g₂ and the selective-attack depth by 25 µm per
g₂, and the 1-hour screen's early rate by only 1 + 1.5 g₂. The targets don't move: NAB (Al 9.2, Ni 4.5) and the
oracle's best (Al 8.0, Ni 7.0) are both below the line.

| Copper, best new alloy | as run | with γ₂ | paired difference |
|---|---|---|---|
| Tiered screening | 0.69 ± 0.02 | 0.69 ± 0.02 | 0.00 (identical, seed for seed) |
| BOFN + blend screen | 0.67 ± 0.01 | 0.55 ± 0.08 | −0.12 ± 0.08 |
| Round-1 cost-aware model | 0.63 ± 0.02 | 0.63 ± 0.02 | 0.00 (identical) |
| Heuristic | 0.58 ± 0.02 | 0.58 ± 0.02 | 0.00 (identical) |
| GP-BO | 0.53 ± 0.06 | 0.53 ± 0.06 | 0.00 (identical) |
| Random | 0.35 ± 0.08 | 0.35 ± 0.08 | 0.00 (identical) |
| Plain BOFN | 0.33 ± 0.09 | 0.29 ± 0.09 | −0.04 ± 0.04 |

- **Only the two BOFN variants changed.** Every other policy's results were identical with and without the effect,
  seed for seed: none of their best alloys sat in the γ₂ corner, and no learning policy's choices changed, so none of
  them measured an alloy there.
- **The screen keeps the funnel out of the corner anyway.** The corner is 2.2 % of the copper space, and the funnel's
  screen (liquidus, freezing range under 110 K, β at 900 °C under 0.3) passes 13 % of it, against 62 % of the space as
  a whole (4,096 Sobol designs). β at 900 °C rises in the same high-Al, low-Ni bronzes where γ₂ forms, so the effect is
  not hidden from the screen in practice.
- **BOFN with the blend screen explored the corner** (strong, cheap, low-nickel bronzes, which score well on the plain
  truth) and lost 0.12 there, with 2 of its 12 runs ending at zero. Its 1-hour corrosion screen sees only part of the
  effect (the early rate), while the selective attack shows only in the 30-day immersion, the copper analogue of DAL
  #205's η knob.

**A mis-specified proxy (`tiered_mis`, 12 seeds, plain truth and with γ₂).** The same funnel, the same 256 screened
designs per seed, with each strengthening coefficient of its proxy off by its own lognormal factor (σ = 0.4, a factor
of 1.5 at one sigma), as a rule of thumb from the literature would be. Copper: 0.71 ± 0.01, a paired +0.02 ± 0.02 over
the plain funnel (9 seeds better, 3 worse), and +0.03 ± 0.02 over BOFN with the blend screen. With γ₂ on, the results
are identical again. Aluminium: 0.30 ± 0.09 (−0.04 ± 0.04 paired).

**The funnel taken apart (`cu_ablation`, 12 seeds each).** Its screen with the passing designs made in a random
order scored 0.58 ± 0.04 on copper (−0.11 ± 0.03 paired against the funnel), and its proxy's top 24 with no screen
0.60 ± 0.04 (−0.08 ± 0.05), against 0.69 for both. On aluminium the proxy without the screen failed outright (all 12
years at zero: without the screen's cracking and mineral gates every pick fails), and the screen with a random order
did as well as the funnel (0.35 against 0.34).

**Three times the copper money (`cu_money`, $180k a year, 12 seeds).** The funnel used it: it spent $87k, tested 18
copper alloys instead of 11, and finished at 0.70 ± 0.01 (+0.01 ± 0.01 paired). BOFN with the blend screen didn't: it
spent $65k, tested 13 instead of 10, and finished at 0.63 ± 0.03 (−0.05 ± 0.03), 0.07 ± 0.04 behind the funnel (2 seeds
ahead, 10 behind). Copper is limited by time and work in flight (eight actions at once, deposits that take weeks), not
by money, and BOFN's per-dollar acquisition doesn't turn spare money into more results.

**What this says.** The funnel's copper lead comes from its screen and a sensible ranking together, and the ranking
doesn't need the truth's coefficients: off by a factor of 1.5 each, it did as well (0.71). On this truth the freezing
range (hot cracking) and β at 900 °C (retained β′) are the main ways a copper alloy fails, and the open CALPHAD node
sees both. Among what passes, a rule of thumb about which elements strengthen picks well. The γ₂ effect doesn't reach
the funnel either. BOFN has to learn the same failure modes from slow and costly copper results (about 10-14 alloys
tested a year), so it doesn't catch up within a year. A copper truth with a failure mode the screen cannot see *and*
that sits where the funnel looks would test the funnel properly. That is not done here.

![Copper with and without the γ₂ effect](../out/twin2/fig/twin2_cu_hidden.png)

### 5.4 The vertical lab against a conventional lab (`conventional`, 6 policies × 12 seeds)

The conventional lab is the proposals' own (`facility = "proposed"`): the rePOWDER on FLAIME's three starts a
weekday and one on Saturdays, BYU's core facilities at their rates, Utah's MIDI and MX-Lab and Mines' X2 with their
booking lead times, turnaround and session caps, metal ordered as each charge needs it, day shifts. It runs three years
at three years' money, so its slower clock has room to show where it gets to. Same seeds, same truths.

**Best new alloy, mean ± SE over 12 seeds:**

| Policy | FLAIME, conventional, year 1 | year 3 | FLAIME, vertical lab, year 1 | ONR, conventional, year 1 | year 3 | ONR, vertical lab, year 1 |
|---|---|---|---|---|---|---|
| BOFN | 0.64 ± 0.04 | 0.74 ± 0.01 | 0.65 ± 0.03 (0.69 ± 0.01 in set B) | 0.05 ± 0.05 | 0.55 ± 0.03 | 0.33 ± 0.09 (blend screen: 0.67 ± 0.01) |
| Heuristic | 0.58 ± 0.02 | 0.68 ± 0.01 | 0.60 ± 0.02 | 0.36 ± 0.07 | 0.64 ± 0.01 | 0.58 ± 0.02 |
| GP-BO | 0.33 ± 0.08 | 0.52 ± 0.08 | 0.46 ± 0.07 | 0.24 ± 0.08 | 0.64 ± 0.02 | 0.53 ± 0.06 |
| Tiered screening | 0.30 ± 0.09 | 0.34 ± 0.09 | 0.34 ± 0.09 | 0.61 ± 0.04 | 0.71 ± 0.01 | 0.69 ± 0.02 |
| Random | 0.20 ± 0.09 | 0.39 ± 0.08 | 0.10 ± 0.06 | 0.22 ± 0.07 | 0.62 ± 0.03 | 0.35 ± 0.08 |
| Sobol | 0.10 ± 0.05 | 0.27 ± 0.07 | 0.10 ± 0.05 | 0.21 ± 0.08 | 0.57 ± 0.02 | 0.45 ± 0.05 |

**Time to the state of the art** (a new alloy at or above the best reference alloy: 0.42 aluminium, 0.56 copper).
Acceleration factor = the conventional lab's median days ÷ the vertical lab's, Kaplan-Meier medians where seeds don't
get there, 95 % bootstrap intervals over seeds (`twin/accel.py`; `out/twin2/econ/econ_summary.json`):

| Vertical lab running | against the conventional lab running | FLAIME | ONR |
|---|---|---|---|
| BOFN (blend screen for copper) | BOFN (plain: blend screening needs the in-house MX-Lab) | **1.9× faster** (1.1-3.4): 116 against 220 days | **3.7× faster** (2.0 to unbounded): 225 against 840 days; the conventional lab got there in 6 of 12 seeds |
| BOFN (blend screen for copper) | a metallurgist's heuristic | **1.1×** (0.7-2.2): 116 against 123 days | **2.2×** (1.7-2.6): 225 against 490 days |
| BOFN (blend screen for copper) | a Sobol design | at least 9.4× (the conventional lab got there in 3 of 12 seeds) | 3.5× (1.7 to unbounded) |
| the heuristic | the same heuristic | 3.3× (1.1-11.9): 37 against 123 days | 3.4×, but the vertical lab's heuristic got there in only 7 of 12 seeds |

- **The lab's own share is about 2-3× in time.** Running the same policy, the vertical lab reaches the state of the art
  1.9× sooner with BOFN on aluminium and 3.3-3.4× sooner with the heuristic (copper's 3.7× also has the blend screen
  in it, which only the vertical lab runs). It tests 1.5× as many aluminium alloys a year
  (BOFN: 34.5 against 23.2) and twice as many copper alloys (12.8 against 6.2) on the same yearly money, and makes
  1.5× as many measurements (763 against 507 a year).
- **On aluminium, the vertical lab with BOFN is no faster to the state of the art than a conventional lab running the
  heuristic** (1.1×, the interval includes 1). This doesn't favor BOFN: the heuristic starts from the reference alloys
  and nudges them, which reaches 0.42 quickly anywhere. BOFN's lead is further up: halfway to the oracle's best (0.64),
  the same comparison is 4.5× (1.5-8.8; 153 against 691 days median; 83 % of the vertical lab's seeds got there in the
  year, 75 % of the conventional lab's in three).
- **On copper, both effects add up.** The conventional lab's copper results take months (Mines sessions, outside
  turnaround), so every policy there gets to the state of the art late (median day 334 for the tiered funnel, 490-840
  for the others); the vertical lab with blend screening gets there 1.5× sooner than the conventional tiered funnel
  (1.2-2.1; same method, `accel.acceleration_factor`) and 2.2-3.7× sooner than the conventional lab with any other
  policy.
- **Three years of the conventional lab beat one year of the vertical lab on the final score** (aluminium BOFN 0.74
  against 0.69; copper tiered 0.71 against 0.69), as three years at three times the money should. The comparison that
  matters is time to a target, above.

![Vertical lab (one year) against the conventional lab (three years)](../out/twin2/fig/twin2_vertical_vs_conventional.png)
![Days to the state of the art, each seed a dot](../out/twin2/fig/twin2_time_to_target.png)

### 5.5 SAAS priors don't help here (`saas`, 3 policies × 12 seeds, the main benchmark's seeds)

| | FLAIME best new | paired against the default GP | ONR best new | paired against the default GP |
|---|---|---|---|---|
| GP-BO, default GP (main benchmark) | 0.46 ± 0.07 | | 0.53 ± 0.06 | |
| SAASBO: SAAS prior, fully Bayesian (NUTS) | 0.38 ± 0.07 | −0.08 ± 0.04 (3 seeds better, 7 worse) | 0.44 ± 0.07 | −0.09 ± 0.05 (2 better, 5 worse) |
| GP-BO with the SAAS prior at its MAP point | 0.50 ± 0.05 | +0.05 ± 0.06 | 0.55 ± 0.06 | +0.02 ± 0.05 |
| BOFN, default GP nodes (main benchmark) | 0.65 ± 0.03 | | 0.33 ± 0.09 | |
| BOFN with SAAS (MAP) nodes | 0.65 ± 0.04 | 0.00 ± 0.06 | 0.36 ± 0.07 | +0.04 ± 0.06 |

- **The fully Bayesian SAASBO did worse than the default GP**, on both campaigns. It also tested fewer aluminium alloys
  (24 a year against GP-BO's 44). The MAP SAAS prior and BOFN's SAAS nodes changed nothing clearly.
- **Likely reasons, not tested separately:** the spaces are 23- and 14-dimensional with 25-45 tested alloys a year, but BoTorch's
  default GP already uses dimension-scaled lengthscale priors (Hvarfner et al. 2024), which do well in high dimensions.
  The utility also depends on many of the elements at once (strengthening, mineral burden, freezing range), so a prior
  that expects few active dimensions has little to gain.
- **SAASBO ran lighter than BoTorch's recommended settings:** 128 warm-up steps, 128 samples thinned to 16, and a fresh
  chain only when the data grew by 4 points and by half (about six chains a simulated year, both campaigns), with the
  last chain's samples reused in between (section 3). A chain at every result would have cost about 33 CPU-hours. Part
  of its shortfall may be that.

![Default GP surrogates against SAAS priors](../out/twin2/fig/twin2_saas.png)

### 5.6 The crucible, powder reuse and stocking (`crucible`, `reuse`, `stock`; 12 seeds each, paired with the main benchmark's seeds)

| Change (vertical lab) | Policy | FLAIME best new | paired change | days to the state of the art (median) | ONR best new | paired change | days to the state of the art |
|---|---|---|---|---|---|---|---|
| 400 cm³ crucible (DAL #219) instead of 225 | BOFN + blend screen | 0.67 ± 0.02 | −0.02 ± 0.03 | 83 (116) | 0.63 ± 0.03 | −0.04 ± 0.03 | 205 (225) |
| | plain BOFN | 0.67 ± 0.02 | +0.02 ± 0.04 | 102 (123) | 0.54 ± 0.07 | **+0.21 ± 0.10** | 167, 8 of 12 seeds (141, 3 of 12) |
| | heuristic | 0.61 ± 0.02 | 0.00 ± 0.02 | **12 (37)** | 0.59 ± 0.03 | 0.00 ± 0.01 | 85 (127) |
| no powder reuse | plain BOFN | 0.71 ± 0.02 | +0.06 ± 0.05 | 103 (123) | 0.40 ± 0.09 | +0.07 ± 0.13 | 171 (141) |
| | heuristic | 0.62 ± 0.02 | +0.01 ± 0.01 | 37 (37) | 0.57 ± 0.03 | −0.01 ± 0.03 | 121 (127) |
| ordering metal as it goes (DAL today) | plain BOFN | 0.62 ± 0.03 | −0.03 ± 0.05 | **189 (123)** | 0.43 ± 0.07 | +0.11 ± 0.07 | 278 (141) |
| | heuristic | 0.58 ± 0.02 | −0.03 ± 0.01 | **107 (37)** | 0.58 ± 0.03 | −0.01 ± 0.03 | 261 (127) |

In brackets: the main benchmark's median, the same policy and seeds. Mean ± SE over 12 seeds; paired change = the
mean over seeds of (this run − the main run with the same seed).

- **The 400 cm³ crucible mostly saves time.** One run makes enough powder for more parts, so the heuristic reaches the
  state of the art in 12 days instead of 37, and plain BOFN gets copper's 1 kg deposits made: +0.21 ± 0.10 on copper,
  the largest change in this table. BOFN with the blend screen already atomizes only what it promotes, and gains
  nothing (−0.04 ± 0.03 on copper, within two errors of zero).
- **Powder reuse doesn't pay here.** Turning it off changed nothing clearly: plain BOFN did a little better without it
  (+0.06 ± 0.05 on aluminium), because reused powder carries more oxygen and satellites into every part made from the
  lot (`twin/instruments/reuse.py`). The model's reuse saves powder, but powder is not what limits these campaigns.
  This doesn't favor reuse, and it rests on the model's degradation rates.
- **Stocking the feedstock matters most for time.** Ordering each charge's metal as it is needed, as DAL buys today,
  delays the state of the art 2.9× with the heuristic (107 against 37 days) and 1.5× with BOFN (189 against 123),
  with the year's best alloy barely changed.

![What the crucible, powder reuse and stocking change](../out/twin2/fig/twin2_options.png)

### 5.7 From DAL #275's common seeds, on two schedules, and the campaign trace (`seeded`, `seeded_dal256`)

BOFN, standard BO (GP-BO) and random, 12 seeds each, every policy starting from the same seven aluminium seeds (#275's
D1, D2, B30, B15, S1, S2, S3) and five copper seeds (section 2), on the vertical lab (stocked) and on DAL's own lab as
DAL #256 schedules it (ordering as it goes; section 2 and `out/twin2/trace/README.md`):

| | Vertical lab: FLAIME | ONR | DAL's lab on #256's schedule: FLAIME | ONR |
|---|---|---|---|---|
| BOFN | **0.69 ± 0.02**; halfway in 10 of 12, median day 123 | **0.64 ± 0.02**; state of the art in 12 of 12, day 86 | **0.66 ± 0.02**; halfway in 9 of 12, day 129 | 0.30 ± 0.09; 6 of 12 end at zero |
| GP-BO | 0.60 ± 0.06; halfway in 5 of 12 | 0.62 ± 0.02 | 0.47 ± 0.08 | **0.51 ± 0.07** |
| Random | 0.60 ± 0.02; halfway in 3 of 12 | 0.59 ± 0.02 | 0.55 ± 0.05 | 0.27 ± 0.09 |
| New alloys tested a year (BOFN) | 39 | 14 | 20 | 3 |

- **Some seeds already beat the state of the art on aluminium.** On this truth some of #275's seed alloys score
  above AlSi10Mg (in seed 0, the B30 dosing check, Al-3.9Si-0.5Mg, at 0.56), so every policy gets there with its first
  tests: a median of day 2 in the vertical lab, and day 52-73 on DAL's schedule, where the first seeds come back from
  Utah. Halfway to the oracle's best (0.64) is what separates the policies.
- **BOFN finishes highest on aluminium on both labs** (0.69 and 0.66, against 0.60 and 0.47-0.55). On DAL's schedule
  it reaches the halfway target about as soon as in the vertical lab (median day 129 against 123, 9 and 10 of 12
  seeds), because aluminium on #256's plan is limited by Utah's sessions, not the atomizer.
- **Copper is what DAL's schedule can't do in a year.** Copper runs only on Fridays, and its deposits go through
  Utah's sessions, the Thursday SEM and a 30-day immersion, so the first copper result comes back around day 210 and
  BOFN tests 3 copper alloys a year against 14 in the vertical lab. There **GP-BO ends ahead of BOFN (0.51 ± 0.07
  against 0.30 ± 0.09)**: with three results no model learns anything, and that doesn't favor BOFN.
- **The seeds rescue plain BOFN on copper** in the vertical lab: 0.64 ± 0.02 against 0.33 ± 0.09 from its own start
  (the main benchmark), as #275 argued a common, informed seed set would.

![Best new alloy so far against simulated days, every policy from DAL #275's seeds](../out/twin2/fig/twin2_seeded_best_vs_days.png)

**The campaign trace.** [`out/twin2/trace/campaign_trace.json`](../out/twin2/trace/campaign_trace.json) is BOFN's
traced year on DAL's lab on #256's schedule (seed 0; schema in [`out/twin2/trace/README.md`](../out/twin2/trace/README.md)):
1,207 events, 974 of them on a node of DAL #211's network; 98 powder lots, 39 builds and 16 deposits, each with how it
ended in DAL #274's ledger (64 completed, 28 abandoned for their inputs, 23 not as planned, 7 early-stopped, 31 stale
at the horizon); 310 iterations with 340 proposals, 114 of them with an acquisition value; 17 literature steps, each
an Edison answer already in DAL; and 189 atomizer runs, at least three a week in 41 of the 53 weeks (the short weeks
are weeks 3-7, waiting on the first orders, and seven later weeks). The same is there for GP-BO and
random on both labs, and for BOFN on the vertical lab (2,511 events, 398 atomizer runs).

![Atomizer runs a week in BOFN's traced year](../out/twin2/fig/twin2_trace_weekly.png)

### 5.8 What it costs: cost per experiment, utilization, outside users (`twin/econ.py`, `notes/twin_econ.md`)

Every price says where it comes from in `twin/econ.py` (procurement records and list prices, or marked assumed).

- **Capital and fixed costs.** The vertical lab: $5.40M of equipment and fit-out, $1.18M a year fixed (depreciation,
  service contracts, utilities and space, one person on the day shift and a quarter of an engineer). The conventional
  lab owns $0.54M and rents the rest by the hour: $0.12M a year fixed.
- **Cost per demonstrated alloy** (an alloy made, printed or deposited, and tested; both campaigns, BOFN in each lab):

  | | no capex | with capex |
  |---|---|---|
  | Conventional lab | $9.4k | $11.6k |
  | Vertical lab, the two campaigns alone | $15.7k | $28.6k |
  | Vertical lab, 60 % utilized (outside users take the idle hours) | $4.5k | $5.9k |

  By campaign, with capex: aluminium $10.3k conventional, $25.1k vertical alone, $5.2k vertical at 60 %; copper
  $16.4k, $40.9k and $8.2k.
- **The cost of getting to the state of the art**, the vertical lab (BOFN, blend screen for copper) as a fraction of
  the conventional lab's (95 % intervals in `econ_summary.json`):

  | Against the conventional lab running | | the campaigns' own spending | operating, alone | full, alone | operating, shared | full, shared |
  |---|---|---|---|---|---|---|
  | the same BOFN | FLAIME | 0.63 | 1.36 | 2.00 | **0.84** | 1.14 |
  | | ONR | 0.41 | 0.84 | 1.15 | **0.42** | **0.48** |
  | the heuristic | FLAIME | 1.23 | 2.65 | 3.81 | 1.63 | 2.16 |
  | | ONR | 0.78 | 1.55 | 2.16 | **0.77** | **0.90** |

  "Alone": the vertical lab's fixed costs carried by the two campaigns only. "Shared": outside users take each
  in-house station's idle hours, up to 10 h a week of demand per instrument (assumed) and 60 % utilization, and pay
  their share. Operating cost leaves capex out; full cost includes it. The conventional lab is charged alone in both
  cases (its rented facilities' rates already include their sharing).
- **This doesn't favor the vertical lab on its own.** Carrying its fixed costs alone, it costs more per alloy than
  the conventional lab and more to reach the state of the art, by 1.4-3.8× on aluminium. Alone, it is cheaper only in
  copper's operating cost against the same BOFN (0.84). Shared with outside users, it is cheaper on copper against
  both references and in aluminium's operating cost against the same BOFN.
- **Utilization.** With only the two campaigns, the capex-weighted utilization of the vertical lab's instruments is
  5.8 %. The atomizer is the busiest station (46 % of the hours its start slots allow: three a weekday and one on
  Saturday); the doser, the MIDI, the SEM, the shop and the MX-Lab are at 3-5 %, everything else under 2 %. The
  atomizer's person, not a machine, sets the pace, as `bottleneck.py` found for ten alloys a day.
- **Outside work (a cloud user facility).** At an assumed 10 h a week of outside demand per instrument, capped at
  60 % utilization: about 13,500 outside jobs a year (ICP-MS samples, SEM and EBSD sessions, corrosion screens, EDM
  cuts, atomizer runs of a user's feedstock), $1.55M of revenue and $1.23M net a year, 2.1× the lab's depreciation and
  1.0× its fixed costs. Every capex dollar then returns $0.33 a year of value instead of $0.10. Without that demand
  figure (which is assumed, `twin/cloud.py`), the capacity is there (about 106,000 jobs a year at 60 %) but not the
  customers.

![Cost per experiment](../out/twin2/econ/econ_cost_per_experiment.png)
![Utilization, and what outside users could fill](../out/twin2/econ/econ_utilization.png)

### 5.9 Where BOFN doesn't win, plainly

- **Copper, the main benchmark:** tiered CALPHAD screening finished ahead of BOFN with the blend screen (0.69 ± 0.02
  against 0.67 ± 0.01) and got to the state of the art sooner (median 88 against 225 days). Plain BOFN did no better
  than random (0.33 against 0.35), with 5 of its 12 years ending with no new alloy above zero.
- **Copper with a hidden effect (γ₂):** BOFN with the blend screen lost 0.12 ± 0.08 and tiered screening lost
  nothing (5.3).
- **Copper with a mis-specified proxy:** tiered screening still finished ahead of BOFN with the blend screen, by
  0.03 ± 0.02 (5.3).
- **Copper with three times the money:** the funnel used it and BOFN didn't; BOFN finished 0.07 ± 0.04 behind (5.3).
- **Aluminium, time to the state of the art:** in the vertical lab the heuristic gets there first (37 against about
  120 days); BOFN's lead is the final alloy (0.65-0.69 against 0.60) and the harder target.
- **Aluminium, against a conventional lab:** the vertical lab with BOFN is 1.1× (0.7-2.2) as fast as a conventional lab
  running the heuristic to the state of the art (5.4).
- **SAAS priors:** the fully Bayesian SAASBO did worse than default GP-BO on both campaigns (−0.08 ± 0.04 and
  −0.09 ± 0.05, paired), and BOFN's SAAS nodes changed nothing (5.5).
- **Copper on DAL's own lab, as #256 schedules it:** from the common seeds, GP-BO ended ahead of BOFN (0.51 ± 0.07
  against 0.30 ± 0.09), with only about three copper alloys tested a year (5.7).
- **Cost:** carrying its own fixed costs, the vertical lab costs more per alloy than the conventional lab ($28.6k
  against $11.6k with capex) and 1.4-3.8× as much to reach the state of the art on aluminium (5.8).

### Limits

All simulated (synthetic truths, simulated instruments, assumed budgets, prices and schedules): this shows how
strategies, instruments, schedules and facilities interact in the model, not what the real lab will find [1, 3].

- **Spread.** With 12 seeds and standard errors of 0.01 to 0.10, gaps under about 0.05 mean little: the two BOFN sets
  run the same aluminium policy and differ by 0.04.
- **The rounds aren't directly comparable.** Round 2 counts new alloys only and measures more harshly; the round-1
  cost-aware model fell from 0.70 to 0.55.
- **The targets.** The 0.86 and 0.76 come from a local search on the truth, not a proven optimum.
- **The implementation.** The twin's BOFN is a new BoTorch implementation, not DAL's benchmark code
  (`benchmarks/bofn-prelim`). SAASBO's NUTS chains run on a refit schedule (section 3).
- **Assumed inputs.**
  - The conventional lab's rates for outside partners (Mines, Utah's MX-Lab, Valimet, Ames) and every breakdown rate are assumed.
  - DAL #256's times are estimates: nothing in its chain has been timed end to end.
  - The outside demand behind the cloud-facility numbers is assumed.
- **Mechanisms the model invents.** The γ₂ effect and the mis-specified proxy are tests of the copper result, not
  findings about copper. Powder reuse's degradation rates come from the model, so "reuse doesn't pay" rests on them.

## 6. Where round 2's truths differ from DAL's synthetic benchmarks

The campaign trace and every result above use round 2's synthetic truths (`twin/truth_al.py`, `twin/truth_cu.py`).
DAL has three synthetic benchmarks of its own; none is on DAL's `main`.

| | DAL #121 (aluminium LPBF, "bofn-prelim") | DAL #205 (copper DED, "bofn-cu-ded") | DAL #265 (EIFN test function) | Round 2 here |
|---|---|---|---|---|
| Design space | 7-D, all scaled to [0, 1]: Zn+Mg, Cu, Zr, Sc, an atomizer setting, laser power, scan speed; no units | 7-D, scaled: Ni 0-30, Al 0-9.5, Fe 0-4.5, Mn 0-4 wt%, atomizer setting, power (Utah capped), speed | 20 inputs, x1-x10 in [0, 1], the rest in [-5, 5] | the proposals' own spaces in physical units: FLAIME Al + 15 elements and 8 process variables (d = 23), the ONR's Cu + 8 elements and 6 process variables (d = 14), with their rules (`twin/spaces.py`) |
| Node functions | hand-written closed forms (solute strengthening, a Scheil-type crack criterion, nucleant crack suppression, a P - v process ridge) | closed forms over 8 priced stages and 11 nodes; also a physics variant (pycalphad `mc_ni` grid, a seawater film model fitted to 30 published rates) | analytic test functions chained: Styblinski-Tang, DTLZ2, Rastrigin, ZDT4 | CALPHAD (pycalphad on MatCalc `mc_al` and COST 507 as the open node, assessed binaries in the truth), process physics (Lang, Rosenthal, King et al., Tang et al.), textbook strength, ductility and corrosion calibrated on 7 reference alloys, USGS mineral data |
| What the lab measures | the node's true value | the node's true value | the node's true value | raw data from simulated instruments, then the lab's analysis: errors, biases and detection limits emerge (section 1) |
| Noise | none | none | none | from the instruments, plus run-to-run process scatter |
| The screen's blind spot | a knob, κ: how much a nucleant suppresses hot cracking, which the CALPHAD screen can't see | κ, and η: the 1-hour screen is blind to β′ selective attack | none | emerges from the open databases' own errors (`mc_al` puts Zr and Sc on the wrong side of k = 1, no primary Al₃Zr); copper's γ₂ effect is an option (`cu_hidden`, section 5.3) |
| Objective | J = strength − 0.3 × mineral burden; optimum known (J* = 0.694 at κ = 1) | J = strength × immersion pass − 0.3 × burden; J* = 0.492 at (κ, η) = (1, 1) | two objectives, known Pareto front | a 0-1 utility: strength, ductility and mineral burden (FLAIME) or corrosion and nickel (ONR), zero unless dense and crack-free; no known optimum (a local search on the truth found 0.86 and 0.76) |
| Money and time | $100k of new spend, stage prices; no clock | $100k, stage prices; no clock | unit node costs | the campaigns' yearly budgets ($120k, $60k), USGS prices with supply shocks, lead times, and a shared lab with calendars, so days matter as well as dollars |
| Start | sunk seed data for every policy: CALPHAD on 32 compositions + 5 random full chains | the same | none | each policy's own start in the main benchmark; DAL #275's common seed set in the seeded runs (5.6) |
| Score | true J of the best design printed and tested, as % of J* | the same, carried through tensile and immersion | not run | true utility of the best new alloy made and tested (references excluded) |

**What the difference changes.** On #205's copper network the spec tiered screen fails outright (0 of its 80
immersions pass; −8 % of J*), because the 1-hour screen can't see β′ attack (η = 1) and the shortlist is Al bronzes
with 2-6 wt% Ni. On round 2's copper truth, tiered screening did best (0.69) because nothing in the truth was hidden
from its screen and its proxy used the truth's own strengthening coefficients. Section 5.3 adds a hidden effect to
test that. #121's aluminium result (BOFN with powder reuse ahead of tiered screening by about 3.8× in spend, but only
when κ = 1) has the same shape as round 2's aluminium result, where the open databases' blind spot plays κ's part.
DAL's sources: [#121](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/121) (`benchmarks/bofn-prelim/`
at d1ca727, PR 117), [#205](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/205) (`benchmarks/bofn-cu-ded/`
at b1ba843, PR 206), [#265](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/265)
(`benchmarks/eifn_synthetic/` at 6c7b0ef).


## Sources for section 5

1. Round 1 write-up, [`notes/twin.md`](twin.md) (L31-43, L173-313 at [a7b0090](https://github.com/vertical-cloud-lab/byu-vcl/blob/a7b0090/vertical-lab/notes/twin.md?plain=1#L173-L313)).
2. Targets: [`out/twin2/oracle.json`](../out/twin2/oracle.json) (`twin/oracle.py`).
3. This write-up, sections 1-4.
4. Round 2 result tables: [`out/twin2/fig/tables.md`](../out/twin2/fig/tables.md) and [`out/twin2/bench2_summary.json`](../out/twin2/bench2_summary.json), with n − 1 standard errors.
5. The runner, [`twin/bench2.py`](../twin/bench2.py) (`EXPERIMENTS`), and the per-run logs, [`out/twin2/runs/`](../out/twin2/runs/).
6. Round 2 progress report on PR 318 (the copper tie; unfinished runs), Nov 25: https://github.com/vertical-cloud-lab/byu-vcl/pull/318#issuecomment-7153171668
7. Round 1 report on PR 318, Nov 24: https://github.com/vertical-cloud-lab/byu-vcl/pull/318#issuecomment-7122957665
8. Strategy code: [`twin/opt/policies2.py`](../twin/opt/policies2.py) and [`twin/policies.py`](../twin/policies.py).
9. Figures: [`out/twin2/fig/`](../out/twin2/fig/).

The results draft this section grew from was staged for this PR on Nov 25 (written from this branch at e3667f8). Every
number in it was checked against the tables and run logs above. One was wrong: plain BOFN on copper ended the year
with no new alloy above zero in 5 of its 12 runs, not 6. The standard errors are now the sample standard deviation
(n − 1), which raises five of them by 0.01.

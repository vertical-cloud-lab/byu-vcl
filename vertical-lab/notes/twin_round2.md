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
  1, and DAL today) left the atomizer 89 % idle while work in flight waited on orders.
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

`twin/oracle.py` scores the reference alloys and 3,000 random designs on the truth at tuned process settings, then
hill-climbs on the truth for an upper reference:

| | best reference (the state of the art) | random designs above it | best the oracle found | proxy vs utility (Spearman, feasible designs) |
|---|---|---|---|---|
| FLAIME | AlSi10Mg, 0.42 (Scalmalloy fails the mineral gate) | 7.2 % | 0.86 (Al-0.6Mn-0.5Zr-0.2Mg-0.4Fe-2Li) | 0.51 |
| ONR | NAB, 0.56 (70-30 has 30 % Ni) | 0.5 % | 0.76 (Cu-8.4Ni-6.1Al-1.5Fe-1.9Mn-0.3Ti) | 0.007 |

**T1**: a new alloy (not a re-test of a reference) at or above the state of the art. **T2**: halfway from the state of
the art to the oracle's best (0.64 for FLAIME, 0.66 for copper). Curves and targets count new alloys only.

RESULTS_PLACEHOLDER

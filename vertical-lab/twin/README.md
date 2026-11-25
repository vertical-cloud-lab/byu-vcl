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
| The campaign video | `video/` | `notes/twin_video.md` |

```bash
cd vertical-lab
/tmp/venv/bin/pip install numpy scipy scikit-learn matplotlib pillow pycalphad scheil pytest "botorch[fully_bayesian]"
/tmp/venv/bin/python -m pytest -q twin/tests                      # round 1 + instruments + economics
/tmp/venv/bin/python -m twin.oracle                               # out/twin2/oracle.json (targets)
TWIN_WORKERS=3 /tmp/venv/bin/python -m twin.bench2 run main conventional saas stock crucible reuse cu
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

# Atomization repeatability: literature check and number of repeats (#261)

Requested in [#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261): what published
run-to-run spread exists for ultrasonic (and gas) atomization in PSD, yield and sphericity, and how
many repeat runs the 6063 baseline needs. Run on 2026-10-07.

## Bottom line

No one has published a fixed-setting repeatability study of ultrasonic atomization for Al, and only
one exists for any alloy. Gas atomization has no heat-to-heat study at fixed settings either, and no
standard (ASTM F3049, NASA MSFC-STD-3716) sets a minimum number of heats or lots. Our baseline would
be new data.

Plan on **5 runs at truly fixed settings, extending to 8** if the spread turns out comparable to the
effects we care about.

## What exists

| Source | What | Spread |
| --- | --- | --- |
| [Hinrichs 2021](https://doi.org/10.3390/met11111723) | The only ultrasonic replicate study. Mo-20Si-52.8Ti, ATO Lab+, 35 kHz, 60 %, 160 A, three 40-50 g rods kept separate "to assess process stability and reproducibility" | d90 (count) 63 / 72 / 78 µm, CV ≈ 11 %. O 1450 / 1330 / 1280 ppm, CV ≈ 6 %, against ±10-30 ppm per measurement. Yield 45-50 wt% <100 µm, pooled |
| [Priyadarshi 2024](https://doi.org/10.1016/j.addma.2024.104033) | Closest to our setup. Pure Al, induction melt at 800 °C, nozzle onto a carbon-fibre plate, 60 kHz, 250 g per run | Yield "consistently exceeded 80 %". Dv50 flat from 60 to 75 % amplitude (within measurement error), +29 % from 75 to 100 % |
| [Yankin 2025](https://doi.org/10.1038/s41598-025-06086-7) | AlSi12, ATO Lab, 7 single runs with current, amplitude and torch angle varied on purpose | D50 52.3-54.7 µm (±2 %), D10 ±7 %, span 0.40-0.64. An upper bound for D50 at fixed settings, not for the tails |
| [Bałasz 2024](https://doi.org/10.3390/ma17225642) | 316L, ATO Lab, Taguchi L16 | Powder/feed efficiency 32.5-80.6 %. 5 of 16 runs aborted as melt built up on the sonotrode |
| [Slotwinski 2014](https://doi.org/10.6028/jres.119.018) (NIST) | Gas atomized, containers from one heat lot | D50 CV 0.55 % (17-4, n = 4) and 4.2 % (CoCr, n = 15). Within a heat, not heat to heat |
| [Grubbs 2022](https://doi.org/10.3390/met12040603) | Al 5056, 19 samples from a handling and storage study, not separate heats | D50 CV 1.4 %, D90 4.5 %, span 5.9 % |
| NASA IN718 survey (Smith & Sudbrack 2017) | 19 lots from 13+ suppliers | D50 12.8-25.4 µm, O 109-331 ppm. Supplier spread, not atomizer noise |

The pattern is consistent: D50 is robust, and the tails (D10, D90, span), yield and oxygen carry the
noise.

## How many repeats

The baseline answers "what is σ_run?". The 95 % confidence interval on σ from n runs, as a multiple
of the sample SD s:

| n | σ lies within |
| --- | --- |
| 3 | 0.52-6.3 × s |
| 5 | 0.60-2.9 × s |
| 6 | 0.62-2.4 × s |
| 8 | 0.66-2.0 × s |
| 10 | 0.69-1.8 × s |

Three runs say almost nothing, and the returns flatten past about 8. Once σ is known, comparing two
settings at α = 0.05 and 80 % power takes about 4 runs per setting for a 3σ difference, 6 for 2σ and
17 for 1σ, which is also how far a single optimization run can be trusted.

## Practical notes for the runs

- Run 1 (1:1 booster, amplitude 50, sonotrode in the nozzle's path) is a shakedown, not part of the
  set. Count aborted runs as a stability rate, and keep them out of σ.
- Hold the plate material (carbon fibre *or* Mo), charge mass, booster and amplitude fixed. Log the
  run order so drift (sonotrode or plate wear, O₂) can be told apart from noise.
- Measure each batch twice so measurement noise separates from run noise: two riffled splits for
  sieving (spinning riffler CV ≈ 0.1 % against ≈ 5 % for scoop sampling, NPL guide), and ≥ 400
  particles per sample for SEM circularity (±0.01 at 95 % if the per-particle SD is about 0.1).
- EDS on 6063 is at its limit. Mg and Si are both below 1 wt%, where even standards-based EDS on
  polished samples is about ±25 % relative ([Newbury 2015](https://doi.org/10.1007/s10853-014-8685-2)).
  Top, middle and bottom EDS will mostly measure EDS noise. ICP-OES on one or two batches is a better
  check. EDS does better on the 4047 composition spread once Si reaches several wt%, where the
  same guidance is ±10 % relative (1-10 wt%) or ±5 % (above 10 wt%).

## Files

| File | Contents |
| --- | --- |
| `q1_ultrasonic_repeatability_*` | Edison high-effort literature review, ultrasonic atomization |
| `q2_gas_atomization_repeatability_*` | Edison high-effort literature review, gas atomization |
| `q3_measurement_repeatability_*` | Edison literature query, sieving, laser diffraction, SEM shape, EDS and sampling precision |
| `q4_ultrasonic_precedent_*` | Edison precedent check ("has anyone run replicates?") |
| `*_answer.md`, `*_trajectory.json`, `*_task_id.json` | Answer, full verbose task payload, and query/task ID for each |
| `google_scholar_via_pi.csv` | 13 Google Scholar queries run from the CubXL Pi, 102 unique hits |

The Edison answers are long and cite page-level contexts. Treat them as leads: the Hinrichs numbers
above were checked against the paper itself.

Google Scholar returns HTTP 429 even from the Pi's IP to a bare request. It works when the session
first loads the Scholar home page to pick up cookies, then waits 10-18 s between queries.

# Round 3 tables (simulated)

Targets: T1 = the state of the art (aluminium 0.4232, copper 0.5559); T2 = halfway from it to the oracle's best (aluminium 0.6393, copper 0.6565). New alloys only. Standard errors: sample SD (n - 1) / sqrt(n).

## Main benchmark (vertical lab, one year)

**Aluminium (FLAIME, LPBF)** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the seeds got there; paired against Tiered screening on the same seeds)

| Policy | n | best new alloy | paired vs Tiered screening (ahead/behind) | T1 reached | T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |
|---|---|---|---|---|---|---|---|---|---|---|
| BOFN, time-aware | 12 | 0.73 ± 0.02 | +0.43 ± 0.08 (11/1) | 12/12 | 83 | 11/12 | 96 | 105.0 | 20.5 | 0.0 |
| pKGFN, time-aware | 12 | 0.71 ± 0.03 | +0.41 ± 0.09 (11/1) | 12/12 | 67 | 10/12 | 83 | 108.0 | 30.4 | 0.0 |
| BOFN, per dollar | 12 | 0.66 ± 0.03 | +0.36 ± 0.09 (11/1) | 12/12 | 80 | 7/12 | 119 | 105.8 | 19.6 | 0.0 |
| Tiered screening | 12 | 0.30 ± 0.08 |  | 6/12 | 146 | 1/12 | >365 | 118.9 | 17.9 | 0.0 |
| Heuristic | 12 | 0.55 ± 0.03 | +0.25 ± 0.08 (10/2) | 11/12 | 24 | 1/12 | >365 | 119.9 | 77.5 | 0.0 |
| GP-BO | 12 | 0.37 ± 0.07 | +0.07 ± 0.06 (5/4) | 9/12 | 226 | 1/12 | >365 | 116.5 | 34.5 | 0.0 |
| Sobol | 12 | 0.34 ± 0.07 | +0.04 ± 0.08 (6/4) | 6/12 | 309 | 2/12 | >365 | 119.2 | 13.1 | 0.0 |
| Random | 12 | 0.25 ± 0.08 | -0.05 ± 0.13 (5/5) | 5/12 | >365 | 2/12 | >365 | 119.4 | 59.6 | 0.0 |

**Copper (ONR, DED)** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the seeds got there; paired against Tiered screening on the same seeds)

| Policy | n | best new alloy | paired vs Tiered screening (ahead/behind) | T1 reached | T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |
|---|---|---|---|---|---|---|---|---|---|---|
| BOFN, time-aware | 12 | 0.58 ± 0.04 | -0.11 ± 0.04 (2/10) | 8/12 | 221 | 5/12 | >365 | 60.6 | 7.6 | 3.3 |
| pKGFN, time-aware | 12 | 0.61 ± 0.03 | -0.08 ± 0.03 (3/9) | 9/12 | 295 | 4/12 | >365 | 60.5 | 6.4 | 2.8 |
| BOFN, per dollar | 12 | 0.60 ± 0.03 | -0.09 ± 0.03 (2/10) | 10/12 | 255 | 5/12 | >365 | 60.3 | 7.4 | 3.0 |
| Tiered screening | 12 | 0.69 ± 0.02 |  | 11/12 | 142 | 10/12 | 148 | 60.5 | 11.3 | 0.0 |
| Heuristic | 12 | 0.57 ± 0.03 | -0.12 ± 0.04 (1/11) | 7/12 | 234 | 1/12 | >365 | 61.1 | 9.5 | 0.0 |
| GP-BO | 12 | 0.54 ± 0.06 | -0.15 ± 0.06 (2/10) | 7/12 | 255 | 3/12 | >365 | 61.3 | 8.3 | 0.0 |
| Sobol | 12 | 0.47 ± 0.06 | -0.22 ± 0.06 (2/10) | 5/12 | >365 | 1/12 | >365 | 60.6 | 9.9 | 0.0 |
| Random | 12 | 0.52 ± 0.03 | -0.17 ± 0.03 (1/11) | 6/12 | 285 | 1/12 | >365 | 60.6 | 13.4 | 0.0 |

## Where the money went (main benchmark, mean over seeds, $k; 'order' is metal and consumables, the stocked lab's day-0 inventory and its reorders)

**Aluminium (FLAIME, LPBF)**

| Policy | total | order | print | test | section | sim_open | pip | powder | metal's share |
|---|---|---|---|---|---|---|---|---|---|
| BOFN, time-aware | 105.0 | 85.3 | 14.7 | 3.2 | 0.9 | 0.4 | 0.5 | 0.0 | 82% |
| pKGFN, time-aware | 108.0 | 84.7 | 16.0 | 4.7 | 1.4 | 0.4 | 0.8 | 0.0 | 79% |
| BOFN, per dollar | 105.8 | 87.0 | 14.0 | 3.0 | 0.9 | 0.4 | 0.5 | 0.0 | 82% |
| Tiered screening | 118.9 | 106.0 | 9.6 | 2.6 | 0.0 | 0.6 | 0.0 | 0.0 | 89% |
| Heuristic | 119.9 | 79.6 | 21.2 | 19.1 | 0.0 | 0.0 | 0.0 | 0.0 | 66% |
| GP-BO | 116.5 | 99.0 | 12.3 | 5.2 | 0.0 | 0.0 | 0.0 | 0.0 | 85% |
| Sobol | 119.2 | 107.5 | 9.8 | 1.9 | 0.0 | 0.0 | 0.0 | 0.0 | 90% |
| Random | 119.4 | 101.2 | 9.6 | 8.7 | 0.0 | 0.0 | 0.0 | 0.0 | 85% |

**Copper (ONR, DED)**

| Policy | total | order | blend_ded | blown_large | immersion | tensile | blown_small | pip | corrosion | metal's share |
|---|---|---|---|---|---|---|---|---|---|---|
| BOFN, time-aware | 60.6 | 48.2 | 6.5 | 1.8 | 1.4 | 1.4 | 0.2 | 0.6 | 0.4 | 80% |
| pKGFN, time-aware | 60.5 | 47.8 | 6.7 | 1.7 | 1.2 | 1.3 | 0.2 | 0.9 | 0.6 | 79% |
| BOFN, per dollar | 60.3 | 47.9 | 6.6 | 1.7 | 1.4 | 1.4 | 0.2 | 0.6 | 0.4 | 79% |
| Tiered screening | 60.5 | 52.7 | 0.0 | 1.6 | 1.7 | 1.4 | 2.0 | 0.0 | 0.2 | 87% |
| Heuristic | 61.1 | 53.2 | 0.0 | 1.9 | 2.2 | 1.7 | 2.1 | 0.0 | 0.0 | 87% |
| GP-BO | 61.3 | 54.9 | 0.0 | 1.5 | 1.6 | 1.3 | 2.1 | 0.0 | 0.0 | 90% |
| Sobol | 60.6 | 54.4 | 0.0 | 1.4 | 1.5 | 1.2 | 2.0 | 0.0 | 0.0 | 90% |
| Random | 60.6 | 53.1 | 0.0 | 1.7 | 2.0 | 1.6 | 2.0 | 0.0 | 0.2 | 88% |


## Paired comparisons within the main benchmark (same seeds)

| Campaign | A | B | seeds | best: A − B (A ahead/behind) | T1: A first / B first / tie | T1 median days A; B | T2: A first / B first / tie | T2 median days A; B | spent A − B ($k) |
|---|---|---|---|---|---|---|---|---|---|
| Aluminium | BOFN, time-aware | BOFN, per dollar | 12 | +0.07 ± 0.03 (8/2) | 3 / 3 / 6 | 83; 80 | 5 / 2 / 5 | 96; 119 | -0.8 |
| Aluminium | pKGFN, time-aware | BOFN, per dollar | 12 | +0.05 ± 0.04 (9/2) | 8 / 1 / 3 | 67; 80 | 7 / 3 / 2 | 83; 119 | +2.1 |
| Aluminium | pKGFN, time-aware | BOFN, time-aware | 12 | -0.02 ± 0.04 (7/4) | 5 / 4 / 3 | 67; 83 | 5 / 5 / 2 | 83; 96 | +2.9 |
| Aluminium | BOFN, time-aware | Tiered screening | 12 | +0.43 ± 0.08 (11/1) | 8 / 4 / 0 | 83; 146 | 10 / 1 / 1 | 96; >365 | -13.8 |
| Aluminium | pKGFN, time-aware | Tiered screening | 12 | +0.41 ± 0.09 (11/1) | 8 / 4 / 0 | 67; 146 | 9 / 1 / 2 | 83; >365 | -10.9 |
| Aluminium | BOFN, time-aware | Heuristic | 12 | +0.17 ± 0.03 (12/0) | 2 / 10 / 0 | 83; 24 | 10 / 1 / 1 | 96; >365 | -14.9 |
| Aluminium | pKGFN, time-aware | Heuristic | 12 | +0.16 ± 0.05 (10/2) | 5 / 7 / 0 | 67; 24 | 10 / 1 / 1 | 83; >365 | -12.0 |
| Aluminium | BOFN, time-aware | GP-BO | 12 | +0.36 ± 0.06 (12/0) | 8 / 4 / 0 | 83; 226 | 10 / 1 / 1 | 96; >365 | -11.4 |
| Aluminium | pKGFN, time-aware | GP-BO | 12 | +0.35 ± 0.08 (12/0) | 9 / 3 / 0 | 67; 226 | 9 / 1 / 2 | 83; >365 | -8.5 |
| Copper | BOFN, time-aware | BOFN, per dollar | 12 | -0.02 ± 0.03 (5/5) | 8 / 2 / 2 | 221; 255 | 4 / 2 / 6 | >365; >365 | +0.3 |
| Copper | pKGFN, time-aware | BOFN, per dollar | 12 | +0.01 ± 0.03 (7/5) | 6 / 5 / 1 | 295; 255 | 1 / 4 / 7 | >365; >365 | +0.2 |
| Copper | pKGFN, time-aware | BOFN, time-aware | 12 | +0.03 ± 0.03 (8/4) | 4 / 6 / 2 | 295; 221 | 1 / 4 / 7 | >365; >365 | -0.0 |
| Copper | BOFN, time-aware | Tiered screening | 12 | -0.11 ± 0.04 (2/10) | 1 / 10 / 1 | 221; 142 | 1 / 9 / 2 | >365; 148 | +0.1 |
| Copper | pKGFN, time-aware | Tiered screening | 12 | -0.08 ± 0.03 (3/9) | 2 / 10 / 0 | 295; 142 | 1 / 9 / 2 | >365; 148 | +0.0 |
| Copper | BOFN, time-aware | Heuristic | 12 | +0.01 ± 0.05 (7/5) | 4 / 6 / 2 | 221; 234 | 4 / 1 / 7 | >365; >365 | -0.5 |
| Copper | pKGFN, time-aware | Heuristic | 12 | +0.04 ± 0.04 (7/5) | 5 / 6 / 1 | 295; 234 | 3 / 1 / 8 | >365; >365 | -0.6 |
| Copper | BOFN, time-aware | GP-BO | 12 | +0.04 ± 0.07 (8/4) | 5 / 6 / 1 | 221; 255 | 5 / 2 / 5 | >365; >365 | -0.8 |
| Copper | pKGFN, time-aware | GP-BO | 12 | +0.07 ± 0.06 (9/3) | 6 / 5 / 1 | 295; 255 | 4 / 3 / 5 | >365; >365 | -0.8 |

## cu_proxy (plain truth, B = main)

**Aluminium (FLAIME, LPBF)** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the seeds got there; paired against Tiered screening on the same seeds)

| Policy | n | best new alloy | paired vs Tiered screening (ahead/behind) | T1 reached | T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |
|---|---|---|---|---|---|---|---|---|---|---|
| Tiered, mis-specified proxy | 12 | 0.41 ± 0.08 |  | 8/12 | 25 | 2/12 | >365 | 119.5 | 18.1 | 0.0 |

**Copper (ONR, DED)** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the seeds got there; paired against Tiered screening on the same seeds)

| Policy | n | best new alloy | paired vs Tiered screening (ahead/behind) | T1 reached | T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |
|---|---|---|---|---|---|---|---|---|---|---|
| Tiered, mis-specified proxy | 12 | 0.70 ± 0.01 |  | 12/12 | 104 | 10/12 | 115 | 60.6 | 12.2 | 0.0 |


| Campaign | A | B | seeds | best: A − B (A ahead/behind) | T1: A first / B first / tie | T1 median days A; B | T2: A first / B first / tie | T2 median days A; B | spent A − B ($k) |
|---|---|---|---|---|---|---|---|---|---|
| Aluminium | Tiered, mis-specified proxy | Tiered screening | 12 | +0.11 ± 0.07 (5/3) | 4 / 3 / 5 | 25; 146 | 1 / 0 / 11 | >365; >365 | +0.7 |
| Copper | Tiered, mis-specified proxy | Tiered screening | 12 | +0.01 ± 0.02 (6/6) | 8 / 4 / 0 | 104; 142 | 7 / 5 / 0 | 115; 148 | +0.1 |

## cu_ablation

**Aluminium (FLAIME, LPBF)** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the seeds got there; paired against Tiered screening on the same seeds)

| Policy | n | best new alloy | paired vs Tiered screening (ahead/behind) | T1 reached | T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |
|---|---|---|---|---|---|---|---|---|---|---|
| Tiered, proxy only (no screen) | 12 | 0.18 ± 0.08 |  | 4/12 | >365 | 1/12 | >365 | 118.4 | 14.2 | 0.0 |
| Tiered, screen only (random order) | 12 | 0.30 ± 0.08 |  | 6/12 | 213 | 1/12 | >365 | 119.7 | 18.1 | 0.0 |

**Copper (ONR, DED)** (mean ± SE over seeds; days are Kaplan-Meier medians, '>' = fewer than half the seeds got there; paired against Tiered screening on the same seeds)

| Policy | n | best new alloy | paired vs Tiered screening (ahead/behind) | T1 reached | T1 median days | T2 reached | T2 median days | spent ($k) | new alloys tested a year | stops a year |
|---|---|---|---|---|---|---|---|---|---|---|
| Tiered, proxy only (no screen) | 12 | 0.61 ± 0.03 |  | 8/12 | 220 | 5/12 | >365 | 61.0 | 8.4 | 0.0 |
| Tiered, screen only (random order) | 12 | 0.44 ± 0.07 |  | 6/12 | 324 | 3/12 | >365 | 60.7 | 11.4 | 0.0 |

### cu_ablation against the main benchmark (B = main, same seeds)

| Campaign | A | B | seeds | best: A − B (A ahead/behind) | T1: A first / B first / tie | T1 median days A; B | T2: A first / B first / tie | T2 median days A; B | spent A − B ($k) |
|---|---|---|---|---|---|---|---|---|---|
| Aluminium | Tiered, screen only (random order) | Tiered screening | 12 | -0.01 ± 0.07 (6/2) | 4 / 3 / 5 | 213; 146 | 1 / 0 / 11 | >365; >365 | +0.9 |
| Aluminium | Tiered, proxy only (no screen) | Tiered screening | 12 | -0.12 ± 0.09 (2/6) | 1 / 6 / 5 | >365; 146 | 0 / 1 / 11 | >365; >365 | -0.5 |
| Copper | Tiered, screen only (random order) | Tiered screening | 12 | -0.25 ± 0.07 (0/12) | 3 / 8 / 1 | 324; 142 | 3 / 7 / 2 | >365; 148 | +0.2 |
| Copper | Tiered, proxy only (no screen) | Tiered screening | 12 | -0.08 ± 0.03 (6/6) | 2 / 9 / 1 | 220; 142 | 1 / 9 / 2 | >365; 148 | +0.5 |

## Alloys and evaluations a year, round 2 -> round 3 (main benchmark, seed means)
| Policy (round 2 -> round 3) | Al lots | Al prints | Al PIP | Al bar tests | Al alloys demonstrated | Cu lots | Cu blend screens | Cu 1 kg deposits | Cu 30-day immersions finished | Cu coupons stopped early | Cu alloys demonstrated |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Random -> Random | 153 -> 235 | 43 -> 61 | 0 -> 0 | 42 -> 60 | 42 -> 60 | 20 -> 19 | - -> 0 | - -> 14 | - -> 13 | - -> 0 | 14 -> 13 |
| Sobol -> Sobol | 152 -> 232 | 40 -> 63 | 0 -> 0 | 10 -> 13 | 10 -> 13 | 21 -> 21 | - -> 0 | - -> 12 | - -> 10 | - -> 0 | 10 -> 10 |
| Heuristic -> Heuristic | 146 -> 206 | 106 -> 140 | 0 -> 0 | 103 -> 131 | 103 -> 131 | 21 -> 20 | - -> 0 | - -> 16 | - -> 14 | - -> 0 | 14 -> 14 |
| Tiered screening -> Tiered screening | 158 -> 236 | 38 -> 62 | 0 -> 0 | 15 -> 18 | 15 -> 18 | 22 -> 20 | - -> 0 | - -> 13 | - -> 11 | - -> 0 | 11 -> 11 |
| GP-BO -> GP-BO | 149 -> 233 | 70 -> 79 | 0 -> 0 | 45 -> 36 | 45 -> 36 | 22 -> 21 | - -> 0 | - -> 12 | - -> 11 | - -> 0 | 12 -> 11 |
| BOFN (round 2) -> BOFN, time-aware | 144 -> 207 | 64 -> 95 | 34 -> 24 | 34 -> 22 | 34 -> 22 | 20 -> 17 | - -> 44 | - -> 14 | - -> 8 | - -> 3 | 13 -> 8 |
| BOFN + blend screen (round 2) -> BOFN, time-aware | 147 -> 207 | 67 -> 95 | 36 -> 24 | 36 -> 22 | 36 -> 22 | 14 -> 17 | - -> 44 | - -> 14 | - -> 8 | - -> 3 | 10 -> 8 |
| BOFN (round 2) -> pKGFN, time-aware | 144 -> 202 | 64 -> 103 | 34 -> 35 | 34 -> 32 | 34 -> 32 | 20 -> 17 | - -> 46 | - -> 14 | - -> 8 | - -> 3 | 13 -> 7 |

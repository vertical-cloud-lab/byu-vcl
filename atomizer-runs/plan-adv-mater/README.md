# Atomizer runs plan for the Advanced Materials collection article

The atomization results are going into a large Advanced Materials collection article, due
early 2028, rather than a standalone first paper in *Powder Technology*
([#218](https://github.com/vertical-cloud-lab/byu-vcl/issues/218)). The article will be
drafted in `vertical-cloud-lab/digital-alloy-lab-private`. This folder turns the runs so far
and the 4047-in-6063 spread into a plan for the atomizer part of that article. It covers
what each upcoming run is meant to show, the bar the repeats have to clear, what to log
every run, the figures, and what can't wait while ME Orders are closed.

It is self-contained, so it can be copied as-is. Links back to `byu-vcl` are absolute and
pinned to commits. Drafted 2026-10-10 from
[#264](https://github.com/vertical-cloud-lab/byu-vcl/issues/264),
[#249](https://github.com/vertical-cloud-lab/byu-vcl/issues/249),
[#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261),
[PR #268](https://github.com/vertical-cloud-lab/byu-vcl/pull/268) and
[PR #232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232). The thresholds and
defaults below are proposals for Gage, Ronnie and Sterling to settle before run A1.

| File | What it is |
| --- | --- |
| this README | The plan: claims, fixed settings, runs, the repeatability bar, what can't wait, timeline |
| [`runs-so-far.md`](runs-so-far.md) | The Oct 2, 6 and 8 runs, what each gives the article and what its record is missing |
| [`run-plan.csv`](run-plan.csv) | One row per planned run: what it varies, what it is meant to show, what it depends on |
| [`measurements.md`](measurements.md) | What to measure every run, how, and what to keep for later |
| [`run-record-template.yaml`](run-record-template.yaml) | The per-run record to fill in, one copy per run |
| [`figures.md`](figures.md) | Figure list, with the runs and measurements each figure needs |
| [`plan_numbers.py`](plan_numbers.py) → [`plan_numbers.json`](plan_numbers.json) | Reproduces every number quoted here: repeat counts, spread masses, MIDI batch count |

## In short

- **The runs fall into blocks.** Before the end of 2026: a no-melt gate (G0), 5–8 baseline
  repeats on 6063 (Block A), and a 7-run composition spread (Block B). In 2027: powder for one
  MIDI print (Block C), then benchmark alloys once feedstock can be bought (Block D).
- **The Oct 2, 6 and 8 runs are pilots, not repeats.** All three went wrong where the melt
  meets the plate, so a run only counts if its landing point was checked before heating.
- **The repeatability bar** is n ≥ 5 valid runs with D50 CV ≤ 10 %, D10 and D90 CV ≤ 15 %,
  in-range yield SD ≤ 5 points, circularity SD ≤ 0.02 and powder O CV ≤ 15 %. At least 4 of
  the first 5 attempts have to be valid. Each run is also measured twice, so that measurement
  noise can be told apart from run-to-run noise.
- **Every run logs** a full mass balance (yield), sieve fractions plus SEM sizing (PSD),
  chamber O₂ at fixed points with a sealed sample kept back for powder O, and SEM shape
  (morphology). Every run also gets EDS and the doser flowability test.
- **Five things can't wait:** sieves, enough Mo plates, enough 6063 from one lot, a count
  of the run consumables, and asking Utah about MIDI time. Each one either blocks Block A or
  sets how big Block C is. Everything else (cameras, shaker, data taps, outside O and ICP
  analysis) can wait until 2027, using the workarounds below.

## What the atomizer part has to show

The claims, and the meeting whiteboard's wants that each one answers:

| Claim | Whiteboard wants | Runs |
| --- | --- | --- |
| **C1 Capability.** A 250 g charge becomes LPBF-range powder in an academic-lab ultrasonic atomizer. | 15–45 µm, sphericity, flowability, low oxide, yield | A |
| **C2 Repeatability.** The run-to-run spread at fixed settings. As of the October 2026 search, only one replicate study of ultrasonic atomization had been published, for any alloy, and none for Al ([lit check](https://github.com/vertical-cloud-lab/byu-vcl/blob/7a18b9c/outputs/issue-261-repeatability/README.md)), so this would be new. | All of C1's, run after run: #264's "consistent powder" for the print | A |
| **C3 Composition set by the charge.** Measured Si follows the Si in the charge across the spread, and the powder is homogeneous within each particle and across the batch. | Target composition, homogeneity within a particle and a batch | B, with A as the 0 wt% point |
| **C4 Printability.** One print on the Aconity MIDI from in-house powder, compared with commercial AlSi10Mg. | Everything above, end to end | C |

The rest of the article, including the FLAIME scope in `digital-alloy-lab-private#111`,
isn't covered here. This session couldn't read that repository.

## Fixed settings for Blocks A–C

Hold all of these fixed, and record the actual value every run. Block B varies only how
much 4047 powder is in the charge.

| Setting | Proposed | Why |
| --- | --- | --- |
| Charge | **250 ± 2 g in total**: 6063 from one bar lot, plus the 4047 powder in Block B. Weigh every part. | Start-up and end losses are fixed amounts, so yield as a percentage depends on charge mass. Holding it at 250 g in every block lets Block A serve as Block B's 0 wt% point. 250 g is the low end of #264's 250–350 g, which leaves cups enough room to reach 30 wt% (see the [spread](#composition-spread-block-b)). |
| Plate | **Mo**, labelled, used only for the 6063 family. Log how many runs each plate has done. | Bartosz says CF doesn't atomize with the 1.5:1 booster ([Oct 8](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6088484430)). Oct 2 (u23y78), on Mo, is the only run that made a useful amount of powder. A metal plate lasts about 4–6 runs with the reverse booster and a low-melting alloy, 1–3 otherwise, with no guarantee either way ([SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/88eeace/atomizer-training/sop.md#cleaning-and-maintenance)). Expect plate changes, and log them as a covariate. |
| Booster, amplitude | **1.5:1, amplitude set to 90 %**. Record the HMI's "amplitude real". | [#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6032139581), aimed at 15–45 µm |
| Nozzle | One bore for the whole study (0.5 mm on Oct 2). Inspect it and clear globs before every run. | Ronnie found [globs at the exit](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6089539052) after Oct 8 |
| Temperature | One schedule, picked before A1. The trainer's default is 850 °C to drop the charge and 780–800 °C at the pour. | Oct 2 used 830 °C as a guess ([SOP lessons](https://github.com/vertical-cloud-lab/byu-vcl/blob/88eeace/atomizer-training/sop.md#lessons-from-the-first-unsupervised-run-oct-2)) |
| Hold before the pour | **One hold for Blocks A and B, picked before A1.** If mixing is the question, 5 min is the safer choice. | Every run so far held 2 min. Indutherm's manual says 5 min once molten, and 10 min when alloying in the furnace ([PR #232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232)), which is what Block B does. A longer hold loses some Mg, but slowly while the melt is under argon rather than vacuum (PR #232). Changing the hold between blocks would mix it up with composition. |
| Pour pressure | Start at **0.19 bar**, and at G0 confirm with Bartosz what the HMI number means | 0.19 bar gave the slow drip on Oct 8, but that nozzle may have been partly blocked: globs were found at its exit afterwards. 0.17 bar was "too high" on Oct 2, which only makes sense if the number is a differential (an [open question](https://github.com/vertical-cloud-lab/byu-vcl/blob/88eeace/atomizer-training/sop.md#open-questions)). |
| O₂ at the pour | **≤ 30 ppm when the sealing rod goes up**, otherwise wash again | The trainer said never to work above 100 ppm, and that 40–50 is best ([T1 25:03](https://www.youtube.com/embed/wRc8p2_FnJo?start=1503)). The team has been reaching the low 20s: one wash at 500 °C did it on Oct 2, Oct 8 needed three. What matters most for the repeats is that it's the same every run. |
| Landing point | **On the plate's face, at a fixed distance from the tip**, set at G0. Check it before heating and mark the stack's slide position. | Three runs in a row went wrong here ([runs so far](runs-so-far.md)) |
| Sequence | Transducer cooling, then scan, amplitude, **ULTRASONIC START**, pour pressure, sealing rod up | Oct 6: the vibration was started late |
| Room humidity | Logged, not controlled | It's on the whiteboard, and Al fines pick up moisture |

## Runs and what each is meant to show

Row by row in [`run-plan.csv`](run-plan.csv). Only those trained on the machine (Gage,
Ronnie, Sterling) handle the machine and the transducer
([#265](https://github.com/vertical-cloud-lab/byu-vcl/issues/265)). Machining, cleaning,
sieving, SEM, polishing and the doser are open to everyone.

| Run | Charge | Meant to show | Decision after |
| --- | --- | --- | --- |
| **G0** (no melt) | none | That the stream will land where we want, before anything is heated. Settle the landing point (laser down the nozzle, or door open), mark the stack position, and get a camera on the HMI. Run the measurements on the u23y78, 4yghtr and kj0461 powder to shake down sieving, SEM and the doser. | A1 can start once the landing point is fixed and recorded |
| **A1** | 6063, 250 g | That the gate works: the stream lands on the face and the plate atomizes. It's also the first run measured end to end. | If it fails the gate, find the cause and run again. A failed run doesn't count toward n but does count against completion. |
| **A2–A5** | 6063, 250 g | The run-to-run SD of every bar metric, any drift with run order, and the effect of a plate change if one happens | Check against the [bar](#the-repeatability-bar) at n = 5 |
| **A6–A8** (only if needed) | 6063, 250 g | A tighter estimate of the SD. The 95 % CI narrows from 0.60–2.87× to 0.66–2.04× the measured SD. | Final call on the bar |
| **B1–B7** | 4047 powder in 6063 cups, made up to 250 g | Whether measured Si follows the charge, and whether the powder mixes within particles and across the jar. Also whether Si changes yield, PSD or shape. B4 is a 0 wt% repeat, to catch drift since Block A. | Pick the composition for the MIDI print |
| **C1–Cn** (2027) | The chosen composition, 250 g | Enough powder for one MIDI print. Each batch is checked against the bar before it's blended, so the bar doubles as the batch acceptance test. | Print at Utah |
| **D** (2027) | Benchmarks: in-house AlSi10Mg, Scalmalloy and others against the purchased powder ([#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6032139581)) | That in-house powder of a known-good alloy matches purchased powder | Planned separately, once feedstock can be ordered |

### Composition spread (Block B)

The points are those of [PR #232](https://github.com/vertical-cloud-lab/byu-vcl/blob/e639fbd/atomizer-charge/README.md#composition-spread-4047-powder-in-6063-cups-264),
rescaled to a fixed 250 g charge, with plain 6063 rod making up the mass. The composition then
comes from the weighed masses via `charge_composition()` in that PR. The ranges are the alloy
spec limits taken at both ends. From [`plan_numbers.py`](plan_numbers.py):

| 4047 powder, wt% | 4047 powder per run | Cups | Si, wt% | Mg, wt% | Runs |
| --- | --- | --- | --- | --- | --- |
| 0 | — | plain rod | 0.20–0.60 | 0.45–0.90 | Block A and B4 |
| 7.5 | 18.8 g | 3 as-made, 71 % full | 1.01–1.53 | 0.42–0.84 | B2, B7 |
| 15 | 37.5 g | 3 thin, 78 % full | 1.82–2.46 | 0.38–0.78 | B5 |
| 22.5 | 56.2 g | 4 thin, 88 % full | 2.63–3.39 | 0.35–0.72 | B1 |
| 30 | 75.0 g | 5 thin, 94 % full (only fits if pushed out to the wall) | 3.44–4.32 | 0.32–0.66 | B3, B6 |

- **This is a Si spread.** Neighbouring points are about 0.9 wt% Si apart. Single-particle EDS
  at 5 kV resolves 1 wt% with about 3×10⁴ counts
  ([caliber#13](https://github.com/vertical-cloud-lab/caliber/pull/13#issuecomment-6032146879)),
  so the mean of 30 or more particles separates neighbouring points easily. The Mg steps
  (~0.05 wt%) are below what EDS can see, so Mg needs ICP-OES.
- **The run order** (22.5, 7.5, 30, 0, 15, 30, 7.5) keeps composition from rising steadily
  with time, so plate or nozzle wear can't pass for a composition effect.
- **Before B3, check that five thin cups fit.** Try them in the cold crucible with the sealing
  rod in place. If they don't, the top point drops to 25 wt%: four full thin cups hold 63.8 g.
- **Block B needs 188 g of sieved 4047 powder,** or 281 g with the endpoints repeated. The
  thin cups (5/8 in drill, 0.060 in wall, 1/4 in plug) have to be machined before B1.

## The repeatability bar

Agree on it before A1 and don't move it afterwards.

**A run is valid** if the landing point was checked before heating, the vibration was on
before the sealing rod went up, O₂ was ≤ 30 ppm at the pour, every fixed setting was within
tolerance, and the pour finished. Invalid runs are still recorded, and count toward the
completion rate.

| Metric | Measured by | Pass, over ≥ 5 valid runs | Why this number |
| --- | --- | --- | --- |
| Completion | valid runs ÷ attempted runs | ≥ 4 of the first 5 | Bałasz 2024 aborted 5 of 16 runs to build-up on the sonotrode. Our last 3 of 3 failed at the plate. |
| D50 (by volume) | SEM sizing, checked against the sieve fractions | CV ≤ 10 % | At 10 %, the 29 % D50 shift from amplitude 75 → 100 % (Priyadarshi 2024) is 3σ, which 4 runs per setting detect. Hinrichs 2021 measured a d90 CV of 11 %. |
| D10, D90 | same | CV ≤ 15 % | The tails are noisier in every study (Yankin 2025: D10 ±7 %) |
| In-range yield | sieved mass under 45 µm, less SEM's share under 15 µm, ÷ charge mass | SD ≤ 5 points | Sets how many runs a print needs. At a 25 % mean, ±5 points means 6–9 runs for a full build cylinder. |
| Powder yield | all powder ÷ charge mass | SD ≤ 10 points | Yield is the noisiest metric in the literature |
| Circularity | SEM, ≥ 400 particles per split | SD of the run means ≤ 0.02 | One sample is good to ±0.01 at 400 particles, if the per-particle SD is about 0.1 |
| Powder O | inert-gas fusion on the retained samples (in 2027) | CV ≤ 15 % | Hinrichs: 6 % at fixed settings. Al fines carry more oxide. |
| Measurement check | two splits per run | split-to-split SD ≤ half the run-to-run SD | Otherwise we'd be measuring the measurement |
| Mass balance | sum of everything weighed out ÷ charge | ≥ 95 % every run | A quality check on the record, not a process metric |

**After n = 5:** powder O won't be measured until 2027, so this decision uses the other
metrics, and O is checked against the bar afterwards.

- **Everything passes with room to spare** (no metric within 20 % of its limit): the process
  counts as repeatable. Go on to Block B with one run per point, and repeat the 7.5 and
  30 wt% points.
- **A metric is close to its limit, or a run was invalid:** run A6–A8, then decide at n = 8.
- **A metric still fails at n = 8:** report the SD as measured. It's still the first such
  number for Al. Block B then needs more repeats per point: 4 runs per setting for a 3σ
  effect, 6 for 2σ, 17 for 1σ. That won't fit in 2026, so the spread drops to its two ends
  (0 and 30 wt%).

Report each metric as mean ± SD, CV, the 95 % CI on σ (0.60–2.87× the measured SD at n = 5),
and the slope against run order.

## Measured every run

Details in [`measurements.md`](measurements.md). The record is
[`run-record-template.yaml`](run-record-template.yaml).

- **Yield:** weigh the charge in, and everything out in separate parts: the jar, the cone
  sweep, splats on the plate and sonotrode, the puddle in the cup, the crucible skull and
  nozzle globs. From these come powder yield, in-range yield and how well the mass balance
  closes.
- **PSD:** two splits per run, each sieved at 250 / 63 / 45 µm. SEM sizing (≥ 1000 particles)
  gives D10, D50, D90 and the fraction under 15 µm, since dry sieving is unreliable below about
  45 µm.
- **Oxygen:** chamber O₂ after each wash, when the sealing rod goes up, and at the end of the
  pour, with the number of washes. A 5 g split is sealed under argon for inert-gas fusion in
  2027.
- **Morphology:** SEM at 100×, 500× and 2000×. Circularity and aspect ratio on ≥ 400
  particles per split, plus the share with satellites. Cross-sections on one run per block
  and per composition.
- **Also:** EDS at 5 kV (top, middle and bottom of the jar, ≥ 30 particles each; look for Mo
  and W picked up from the plate and sonotrode), the doser's V_g and I_stop against
  same-session AlSi10Mg, and the Hausner ratio.

## Figures

The full list, with the runs and measurements each one needs, is in
[`figures.md`](figures.md). The main-text candidates:

1. **From charge to powder.** The cup, the machine, a good pour and the powder.
2. **Repeatability.** Block A's PSDs overlaid, per-run metrics against run order, and the CVs
   alongside the literature.
3. **Composition set by the charge.** Measured Si against charge Si, per-particle
   distributions, and EDS maps.
4. **Powder quality across the spread.** D50, yield, circularity and flowability against Si.
5. **The print.** The build, its density and microstructure, against commercial AlSi10Mg.

## Can't wait (no ME Orders this year)

The equipment line stays unspent in 2026. This plan assumes nothing new is bought through ME
Orders before January 2027. If the line reopens at a different date, the "can wait" rows just
move.

| Item | Needed for | Without an order | Verdict |
| --- | --- | --- | --- |
| **Sieves**: No. 60, No. 230, pan and cover, $199.20 ([PR #262](https://github.com/vertical-cloud-lab/byu-vcl/blob/d301844/docs/sieve-order.md)). **Add the No. 325 (45 µm, $74.50)**, because the article's window is 15–45 µm and the planned stack stops at 63. | PSD, in-range yield, sieving before the doser (unsieved 4047 clogged it), the MIDI powder | Borrow: ask Chem Stores (801-422-2678) and nearby labs. Without sieves, Block A loses in-range yield (the metric that sizes Block C), the doser test (unsieved powder clogs it), and the check of SEM D50 against the sieve masses. | **Can't wait**, unless it can be borrowed or has already been ordered |
| **Mo plates** | Blocks A and B: 12–15 runs at 4–6 runs per plate means 2–4 plates, more if any crack | Count the labelled, uncracked Mo plates now. The fallback is CF with the amplifying 1:1.5, which made coarse powder on Sep 29, so the article would lose its 15–45 µm claim. | **Can't wait if fewer than 3** (an AMAZEMET consumable, with lead time) |
| **6063 bar, one lot** | 4.6 kg ([`plan_numbers.py`](plan_numbers.py)): 2.0 kg for 8 Block A runs, 1.5 kg for Block B, 0.66 kg of chips from boring 23 cups, and 0.5 kg for two failed runs | Weigh what's on hand and find its lot or heat number. If a second lot can't be avoided, keep a slice of each and tag each run with its lot. The 6063 spec allows Si 0.2–0.6 and Mg 0.45–0.9, which is wider than the spread's Mg steps. | **Can't wait if under ~5 kg** |
| **Run consumables**: graphite nozzles, sealing rods, crucible, BN spray, filters, pump oil, argon | Every run, about 15 in Oct–Dec | Count them against 15 runs. Argon: the booth may hold at most two Ar/N₂ cylinders, not manifolded (Bryant Brown, 2026-10-08, [#126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126)). | **Can't wait** for anything that won't last 15 runs |
| **MIDI time at Utah** | Block C | Not an order, but ask now ([#77](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-6032142676)): the cost, whether Utah has the 55 mm build-reduction kit, and the PSD Utah wants. The kit needs about 30 g, which is 1 run. The full cylinder needs about 440 g, which is 8 runs at 25 % in-range yield. | **Ask now** |
| Landing-point laser fixture | G0, before A1 | No order needed: print a fixture on the lab's printers and use a laser pointer from the lab, or check with the door open | Not an order, but **do it first** |
| 4047 powder | Block B: 188–281 g sieved. Block C at 30 wt%: 75 g a run, about 600 g for a full cylinder. | Weigh what's on hand from the Sep 29 runs. If there isn't enough, atomize 4047 rod (1–2 runs, no order). For Block C, plan to atomize more 4047 in 2027 or buy rod. | Can wait, as long as Block B is covered |
| Powder O and ICP-OES (outside services) | The O metric in the bar, Mg recovery in Block B, the bulk check on EDS | Keep a 5 g split from every run, sealed under Ar (glovebox) or with desiccant, and log the day it was sealed. Composition doesn't change in storage, but O creeps up. | Can wait until 2027 |
| HMI data export ([#221](https://github.com/vertical-cloud-lab/byu-vcl/issues/221#issuecomment-6032140520)) | Settings and the O₂ and temperature log | Not an order: VNC monitor mode and the EasyWeb export need AMAZEMET's History-level password. Until then, use a camera on the panel and say the values out loud. | Can wait |
| Viewport cameras, $1,217.61 ([#198](https://github.com/vertical-cloud-lab/byu-vcl/issues/198#issuecomment-6032141634)) | Video of the landing point | A clamped phone at the front port, from before the sealing rod goes up until the stream stops | Can wait |
| Tap on the generator's power output (DB15 breakout and isolated ADC) | Whether the POWER reading means anything | Film the POWER reading during the pour | Can wait |
| Sieve shaker ($1,601.40), riffler | Faster, more even sieving and splits | Sieve by hand, 10–20 g at a time. Split by cone and quarter on a grounded tray. | Can wait |
| Larger crucible | Fewer Block C runs | Use more runs | Can wait |
| Aluminium vise jaws, metric tool set ([#265](https://github.com/vertical-cloud-lab/byu-vcl/issues/265)) | Torquing the stack | The current soft jaws and borrowed tools. The handling rule is unchanged. | Can wait |
| Benchmark feedstock (Thermo Fisher quote expired, ME Order 13300, [#161](https://github.com/vertical-cloud-lab/byu-vcl/issues/161)) | Block D | — | Can wait. Block D moves to 2027. |

## Timeline

| When | What |
| --- | --- |
| Oct 2026 | Inventory (plates, 6063, 4047 powder, consumables, sieves), G0, A1. Start machining thin cups. Ask Utah. |
| Nov 2026 | A2–A5, about two runs a week as on Oct 6 and 8. The n = 5 decision, then A6–A8 if needed. |
| Late Nov – mid Dec 2026 | Block B (7 runs). If Block A runs late, cut Block B to the 30 wt% point (B3, B6) and the drift check (B4). |
| Dec 2026 – Jan 2027 | Catch up on characterization. Send the retained samples for O and ICP-OES once ordering reopens. |
| Jan – Apr 2027 | Orders that waited. Block C, and the MIDI print. Block D once feedstock arrives. |
| May – Oct 2027 | Characterize the print, make the figures, draft in `digital-alloy-lab-private` |
| Early 2028 | Submit |

## Copying into `digital-alloy-lab-private`

Copy the folder as-is. Every link out of it is absolute and pinned to a commit, and
`plan_numbers.py` needs only numpy and scipy. The run records themselves stay in
`byu-vcl/atomizer-runs/<date>/`, as in [PR #268](https://github.com/vertical-cloud-lab/byu-vcl/pull/268),
with one filled-in `run-record-template.yaml` per run.

## Sources

- Runs: [#249](https://github.com/vertical-cloud-lab/byu-vcl/issues/249),
  [#261](https://github.com/vertical-cloud-lab/byu-vcl/issues/261), the
  [Oct 8 video record](https://github.com/vertical-cloud-lab/byu-vcl/blob/f74c654/atomizer-runs/2026-10-08/README.md)
  (PR #268), and the [training SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/88eeace/atomizer-training/sop.md)
  with its [Oct 6 notes](https://github.com/vertical-cloud-lab/byu-vcl/blob/88eeace/atomizer-training/runs/2026-10-06.md)
  (PR #255)
- Repeatability literature and repeat counts:
  [`outputs/issue-261-repeatability/`](https://github.com/vertical-cloud-lab/byu-vcl/blob/7a18b9c/outputs/issue-261-repeatability/README.md)
  (Hinrichs 2021, Priyadarshi 2024, Yankin 2025, Bałasz 2024, NIST)
- Spread and cup dimensions:
  [`atomizer-charge/composition_spread.json`](https://github.com/vertical-cloud-lab/byu-vcl/blob/e639fbd/atomizer-charge/composition_spread.json)
  (PR #232)
- Sieves and grounding: [`docs/sieve-order.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/d301844/docs/sieve-order.md) (PR #262)
- Flowability proxies: [powder-doser `docs/flowability/`](https://github.com/vertical-cloud-lab/powder-doser/blob/0030e0d/docs/flowability/README.md)
- EDS counts and beam position: [caliber#13](https://github.com/vertical-cloud-lab/caliber/pull/13#issuecomment-6032146879)

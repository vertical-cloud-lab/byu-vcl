# 6-DOF arm + eye-in-hand vision in self-driving labs — findings

Working notes for [issue #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199).
Paraphrases the verbatim Edison answers in [`docs/edison-6dof/`](edison-6dof/); go there
for the citations and the raw text.

## The hardware we are planning around

AgileX **PiPER**: 6-DOF, 4.2 kg mass, **1.5 kg payload**, **626 mm reach**, vendor-claimed
**0.1 mm repeatability**, CAN bus + Python API, `piper_ros` on ROS 2 Humble/Iron, roughly
$2.5k–$4k. Plus a camera of our own on the wrist.

## What Q1 established

**Every deployed arm-based SDL uses an expensive industrial arm.** KUKA KMR-iiwa
(Liverpool mobile robotic chemist, *Nature* 2024), ABB YuMi (Liverpool PXRD workflow),
Franka Research 3 (vision-guided powder scooping, *Digital Discovery* 2026), Denso-Wave
COBOTTA (NIMS intermetallic synthesis). **No published SDL runs on a sub-$5k arm.** That
absence is the opportunity, not a warning.

**The arm is a logistics layer, not the chemistry.** In every system above, the arm moves
vials, crucibles, coupons, and racks between stations; purpose-built hardware (Chemspeed,
Opentrons, custom fixtures) does the dispensing, heating, and sealing. Planning the PiPER
as a *transfer* layer that feeds our existing gantry/furnace/printer/tester stack matches
what actually works.

**Reliability, not capability, is the binding constraint.** Ada (UBC/AC) reports ~1
run-ending failure per 40 samples — 97.5% per-sample success. Over a 50-sample overnight
campaign that is a **28.2% chance of finishing uninterrupted**; ~99.8% per-sample would be
needed for 90%. Liverpool needed >1 year of debugging for stable multi-platform operation.

**And nobody reports it.** No deployed SDL paper gives a mean-time-between-intervention
for the arm specifically. Failure rates are unreported, campaign-level, or mixed in with
instrument and software errors.

**Vision numbers worth holding onto.** TransGraspNet, eye-in-hand RealSense D435i on an
AUBO i5: 91.0% grasp success over 100 trials on transparent labware (96% simple, 86%
cluttered), 3.8° angular and 8.5 mm positional grasp error. Vision-guided powder scooping:
89.2% successful-scoop classification, 96% unsuccessful-scoop, 1.93 ± 2.04 mg mean weighing
error, robust across 40–700 lux. RGB-D depth error on transparent labware still reaches
38 mm — the reason fiducials remain load-bearing.

**Scripted primitives still beat learned policies here.** VLA models land at 30–60%
out-of-box success on unseen tasks, against the >99% per-operation reliability unattended
SDL operation needs. Fiducial-corrected scripted motion is the pragmatic 2026 choice.

**Task tolerances vs. what a cheap arm delivers** (Edison flags the PiPER figure as
extrapolation — no published characterization of this arm exists, which is itself Gap 1):

| Task | Tolerance needed |
|---|---|
| Powder scoop transfer | ±2–5 mm |
| Vial rack insertion | ±1–2 mm lateral, ±3° |
| Crucible into furnace | ±1 mm, under thermal drift |
| Cuvette into spectrometer | ±0.5 mm |
| Tensile coupon into grip | ±0.3 mm |

Sub-$5k arms are estimated at ±0.5–2 mm at best in practice, versus ±0.03–0.1 mm at the
flange for a UR5e or Franka — and that degrades at extension, under payload, and with
thermal drift. So: **arm for transfer and coarse positioning, fixtures for the precision
seat, vision to close the gap.**

## Ranked opportunities (Edison's ordering, Tier 1 first)

1. **Gap 3 — first published MTBI for an arm-based SDL**, with an open failure taxonomy
   over >500 cycles. Lowest competition, highest community need.
2. **Gap 1 — first metrological characterization of a sub-$5k arm**: repeatability,
   thermal drift, payload-at-extension, backlash, cycle count. Fast, and it is the
   baseline every later claim rests on. Scoopable — move first.
3. **Gap 2 — vision-corrected primitives**: eye-in-hand ArUco/AprilTag servoing to <0.5 mm
   on a $2.5k arm, across 6+ SDL tasks, open-loop vs. corrected.
4. **Gap 5 — ROS 2 + Bayesian-optimization orchestration package** with telemetry and
   cloud queuing. Directly leverages honegumi/Ax work already in this lab.
5. **Gap 9 — cloud-operated frugal SDL**, remote users, multi-day campaign, reported
   uptime and intervention rate. This is the Vertical Cloud Lab thesis, stated as a paper.
6. **Gap 10 — vision-guided powder handling** on a wrist camera instead of an external
   one, on AM-relevant metal powders. Ties straight into `powder-doser` and LPBF.

Then: transparent/metallic monocular pose estimation (Gap 4), uncertainty-aware policy
switching (6), digital-twin pre-flight collision checking (8), VLA data-efficiency (7),
fiducial-vs-learned benchmarking (11), LLM-verified plans against furnace and containment
interlocks (12).

**Called out as already crowded** — general VLA architecture work, BO algorithms for SDLs,
LLM-as-scientist for experiment design, and generic transparent-object grasping. Only the
SDL-specific angle on the last one is viable.

## Where this lands against our existing repos

- **`tensegrity-optimization`** already closes a BO loop through print → drop test, but
  specimen handling on and off the Lansmont M23 is manual. That is a concrete,
  well-instrumented home for Gaps 3 and 9.
- **`powder-doser`** is the natural target for Gap 10 — wrist-camera fill estimation on
  metal powders, benchmarked against the 1.93 mg result.
- **`caliber`** and the OT-2/`digital-wetlab` stack give a second workflow to measure
  MTBI on, with different failure modes.

## What Q2 established (metrology and reliability methods)

**Verifying the PiPER's claimed 0.1 mm repeatability needs a reference 3–5× better — so
≤0.02–0.03 mm expanded uncertainty (k=2).** Very little cheap equipment clears that bar, and
Q2 is blunt about which does:

| Method | Cost | Expanded uncertainty (k≈2) | Verdict for a 0.1 mm claim |
|---|---|---|---|
| Three-probe LVDT / comparator kinematic nest | $1.5–8k | 0.003–0.02 mm per channel; 0.01–0.05 mm reconstructed | **primary instrument** — directly measures return-to-point scatter |
| Laser tracker, rented | $1–3k/day | 0.006–0.03 mm | gold standard; 2–3 days covers a near-complete ISO 9283 campaign |
| Dial indicator in a ballbar-style fixture | $0.3–3k | 0.005–0.03 mm per axis | good for repeatability/backlash, not full 6-D pose |
| Photogrammetry, coded targets | $1–10k | 0.03–0.15 mm | secondary, for workspace maps |
| OptiTrack/Vicon | $8–50k | 0.05–0.3 mm static | marginal — cannot certify 0.1 mm alone |
| 3D-printed task board | $50–500 | 0.2–1 mm as printed | task success only; **0.1 mm insertion clearance is not 0.1 mm uncertainty** |
| RealSense/ZED/Kinect | $0.25–2.5k | 1–5 mm commodity depth | inadequate for the claim |

Recommended combination: an LVDT nest as the primary instrument plus 1–2 laser-tracker
rental days for absolute accuracy across the workspace, everything validated against
traceable gauge blocks.

**The reliability sample sizes are the number to plan around.** With zero observed failures,
a 95% one-sided lower bound needs n ≥ log(0.05)/log(p):

- **118 operations** to support p ≥ 0.975 (Ada's level)
- **1,497 operations** to support p ≥ 0.998 (the level an overnight campaign actually needs)

Any observed failure pushes both up, so a publishable claim means **500–1,500 operations**.
Report cause-specific MTBI via competing-risks survival analysis (Kaplan–Meier /
Nelson–Aalen with right censoring), and use Weibull β to separate infant mortality (β < 1)
from wear-out (β > 1).

**Minimum credible paper, per Q2:** ISO 9283-aligned characterization at 5 poses and 2
payloads with a documented thermal warm-up protocol and a real uncertainty budget, plus a
≥500-cycle reliability campaign with structured failure logging. ~2–3 weeks of lab time and
$5–10k of measurement equipment. It would be the first paper with both metrology and real
MTBI for a low-cost arm in an SDL.

## What Q3 established (end effectors + generative CAD)

**The one sentence that matters:** *no published system autonomously closes the loop from
laboratory-object requirements through editable, manufacturable gripper CAD, FDM
fabrication, and measured manipulation performance on a real SDL arm.* Every existing
system closes a subset:

- **Fit2Form** (Ha, Agrawal & Song 2020) — object shape → generated parallel-jaw fingers →
  printed → physically tested on a WSG50 (5 N grasp, 15 cm lift, X/Y shake, ~30 N poke).
  Closest prior art, but it emits geometry rather than editable parametric CAD, has no
  controller or material co-optimization, does not feed results back into redesign, and
  never touches laboratory objects.
- **Yi et al. 2025** — block-wise finger stiffness co-optimized with grasp pose through a
  differentiable neural surrogate, printed and tested. Real co-design, but over a
  predefined flexure family.
- **IterCAD, Text2CAD-Bench, CADIR, CME-CAD, CAD-Recode, DeepCAD** — all optimize digital
  similarity. IterCAD reaches 0.64% invalid / median Chamfer 0.10 on Text2CAD; **none
  report a functional fabrication test.**
- **Omaisan 2026** — robot-aware computational design of object-specific *passive* grippers
  with contact zones, insertion sweeps, FEA and topology optimization. Four designs passed
  the digital gates; coupon calibration and the proposed 100-cycle physical tests were
  **explicitly still pending**.
- **MATTERIX** — simulates workflows (75% real pick-and-place, 90% pouring) but generates
  no grippers, and its position-based-dynamics powder is explicitly unvalidated for cohesive
  AlSi10Mg or Si.

### Absences Q3 states outright

- No published SDL reports MTBI for the arm or the end effector.
- **No study quantifies how much compliant capture envelope compensates for a given arm
  repeatability error** on a lab peg-in-hole task. RCC devices, standard in industrial
  assembly, have *no* published laboratory-automation application.
- **No lightweight tool changer exists for a sub-1.5 kg payload arm.** Commercial changers
  (ATI, Stäubli) weigh 0.5–1.5 kg and target 5–50 kg arms — a 0.5 kg changer would eat a
  third of the PiPER's payload. Precision kinematic couplings reach 0.3–1.4 µm (3σ) and
  ±5 µm for split-groove vs. ±50 µm for dowel pins, but steel-on-steel fretting degrades
  that to ~10 µm after several hundred cycles.
- **No robotic DSC crucible press-fit lid system** has been published with insertion force,
  compliance, or success-rate data.
- **No open-source SDL powder scoop reports cross-contamination, cleaning efficacy, or
  triboelectric charging.**
- **No published work uses a Raspberry Pi HQ fixed-focus camera for manipulation.** Q3's
  own estimate — f/1.6, 6 mm lens, 100 mm working distance → roughly ±5 mm depth of field —
  is flagged as extrapolation, and it is tight enough to need a stopping-down or refocus
  strategy.

### Numbers worth keeping

- Compliant lab fingers (Zwirnmann 2023): microtube top-grasp wrest force **5.0(5) → 14.9(22) N**
  moving from rigid to dual-material construction; pinch 20 N, power grasp 100 N conditions.
- InstaGrasp TPU tendons survived **>86,000 stress cycles**; Tough PLA fatigue data reaches
  **42,000 cycles** — but never in a gripper geometry at operational strain, which Q3 flags
  as the extrapolation.
- GelSight Mini: three-axis force to ~**4% MAE up to 15 N** when calibrated. DIGIT is
  **$15–50**. A real F/T sensor (BOTA SensONE / ATI Nano17) is **$1,500–5,000** and
  50–100 g — characterization-only at a 1.5 kg payload. Motor-current force estimation on
  this arm class is **unpublished**.
- Low-cost eye-in-hand grasping reports **85–93%** success; one monocular 5-DOF system hit
  90% with ±3 mm residual, failures concentrated at field-of-view edges where error
  exceeded 5 mm. Typical working distance 15–20 cm.

### Q3's ranked projects, in our terms

1. **Closed-loop generative end-effector design** — specification → CadQuery → FDM → robot
   test → redesign, beating expert-designed universal *and* object-specific fingers across
   vials, SEM stubs, well plates, and coupons. Needs ≥1,000 cycles per finalist and
   ablations of kernel checks, VLM judging, and physical feedback. **Strongly de-risked by
   CADSmith.** *Additive Manufacturing* / RA-L / *Digital Discovery*, 9–18 months.
2. **Compliance-versus-precision map** — impose lateral/axial/angular error deliberately and
   map success probability vs. clearance for rigid chamfer, TPU pad, flexure, Fin-Ray, RCC.
   RA-L / RCIM / JMR, 6–12 months.
3. **End-effector reliability benchmark** — thousands of pick/place/seat operations with
   MTBI, recovery rate, and a failure taxonomy. *HardwareX* + dataset, 6–12 months.
4. **Printed kinematic tool changer for a 1.5 kg arm** — mass, 6-DOF redocking repeatability
   over ≥1,000 cycles, wear and powder-debris sensitivity. Geometry strongly de-risked by
   CADSmith; tribology is new. *HardwareX* / *Precision Engineering*, 6–10 months.
5. **Robotic DSC crucible + press-fit lid station.** 6. **Fixed-focus wrist vision for
   last-centimeter servoing.** 7. **Open powder scoop with quantified decontamination.**

**Crowded, stay out:** general text-to-CAD benchmarking, dexterous multi-finger hand design,
GelSight/DIGIT tactile hardware, general grasp synthesis.

## What Q4 established (the protocol for the generative-gripper loop)

Q4 was asked for a protocol, not a survey, and it mostly delivered one. Verbatim answer in
[`edison-6dof/q4-closed-loop-design-protocol/answer.md`](edison-6dof/q4-closed-loop-design-protocol/answer.md).

**Four endpoints, split by what each can attribute.** Off the arm: **retention force**
(pull-to-slip on a rigidly fixtured finger set, keeping the full force–displacement curve)
and **capture envelope** (success against deliberately imposed lateral, axial, and angular
offsets, reported per axis as ED50/ED90 from a logistic mixed model). On the arm: **binary
grasp success** (lift ≥50 mm within 3 s and hold 3 s, the Cross-Embodiment Gripper
Benchmark definition) and **seating success**. Never claim a finger-only improvement from
on-arm data alone. Cycle time is dominated by the arm, so it is a systems metric only.

**Power at a high baseline is the expensive part.** Detecting 90% → 95% at 80% power
(two-sided α = 0.05) takes **~435–475 trials per group**. I re-derived that: 435 from the
plain two-proportion test, 474 with continuity correction. Q4's other figure is
overstated, though: it says 95% → 98% needs ">1,000 per group", but the same calculation
gives **~590–650** at 80% power and ~790–850 at 90%. Q4 is also inconsistent with itself
on the total. Its §1.3 budgets 900 trials per design (5,400 total), while the offset grid
in its own deliverable table works out to **14,040**. It flags this and says to resolve it
before pre-registering.

**Fatigue has no data to design against.** There are no S–N curves for FDM TPU-85A, PETG,
or PA-CF at flexure strains, and no ASTM/ISO method for FDM compliant-mechanism fatigue
(ASTM D7791 can be adapted). The closest study is Juwita 2019: PLA–TPU 95A at ~2 Hz,
8–80% of yield, where several interface designs failed before reaching 100k cycles. The
proposed protocol:

- displacement-controlled cycling at ≤1 Hz
- failure = fracture, ≥20% loss of closure force, ≥20% permanent set, or delamination
- 100k-cycle run-out, ≥5 specimens per finalist
- checkpoints at 1k, 10k, 50k, and 100k cycles

Q4 also finds no direct precedent in the compliant-gripper literature for our rigid + TPU
mechanical-interlock joints. That literature relies on adhesion.

**One print is not a design.** FDM dimensional error is 0.18 ± 0.07 mm across 42 PLA parts
(Li 2026). Plan on ≥3 independent prints per design, and first run a variance-components
pilot of five prints of one reference finger per printer.

**What to feed back to the generator.** VLMgineer (Gao 2026) is the only direct evidence.
There, scalar task reward beat image feedback, and adding execution images *reduced*
reward by 5.4%. Q4's ranking:

1. structured scalar reward plus a failure label from a pre-registered taxonomy
2. force–displacement features
3. failure labels alone
4. a VLM reading of failure video, which should go to human review, not the loop

Using a balance as a *design-loop* reward is unpublished.

**Ablations and the control arm.** Five matched ablations: no physical feedback, no VLM
judge, no kernel checks, no parametric priors, and no simulation pre-screen. The
human-expert control gets the identical frozen specification, matched person-hours and
pilot prints, and anonymous design codes. Its CAD is frozen before confirmatory testing.
Si et al. (43 experts, >100 h of execution each, blinded review) is the precedent to cite.
Budget 30–60 printed-and-tested designs, target 50, at roughly 45 min of printing plus
30 min of testing each. That is ~60 h of printer and robot time.

**The absence that matters most here** is Q4's claim that *no published lab-object
manipulation benchmark exists.* That is slightly out of date. Real-robot lab benchmarks
appeared in August and September 2026: [LabDex](https://arxiv.org/abs/2608.18618), and
[WetRobo](https://arxiv.org/abs/2609.18435), a reproducible kit built on an AgileX PiPER.
The narrower claim still holds. Neither ships a buyable labware object set with part
numbers, masses, and meshes. Every protocol above needs one, and nobody has published it.
That is the reason for [`sandbox-object-set.md`](sandbox-object-set.md), which Edison Q5
fed into.

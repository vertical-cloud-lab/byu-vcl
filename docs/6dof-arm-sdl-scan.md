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

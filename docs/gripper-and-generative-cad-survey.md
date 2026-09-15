# Custom grippers, end effectors, and generative CAD — org survey

Working notes for [issue #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199),
answering the "look into custom gripper and end-effector design … noting generative CAD and
generative systems design as potential project paths, in addition to extensively looking at
powder-doser repo issues and PRs" request.

This file is the **repo-survey half**. The literature half is the Edison scan in
[`docs/edison-6dof/`](edison-6dof/), and the arm-level findings are in
[`docs/6dof-arm-sdl-scan.md`](6dof-arm-sdl-scan.md).

Method: `gh api repos/vertical-cloud-lab/powder-doser/issues` over all 157 issues and PRs
(open and closed), then full comment threads pulled for the 37 that touch generative CAD,
mechanism design, or end effectors. Org-wide `gh search issues` for gripper / end-effector /
arm / AprilTag / LeRobot terms. Comment bodies, not just issue bodies — most of the content
in this org lives in the comments.

## 1. The org is already running a generative-CAD bake-off, and nobody has written it up

This is the most important finding of the survey, and it was not visible from the issue
titles alone.

`powder-doser` has a **controlled, four-way comparison of CAD-authoring methods on one
identical engineering specification** already in flight:

| Arm of the comparison | Issue / PR | State |
|---|---|---|
| The shared spec prompt itself (`powder-doser-assembly-prompt.md`) | [#104](https://github.com/vertical-cloud-lab/powder-doser/issues/104) / [#105](https://github.com/vertical-cloud-lab/powder-doser/pull/105) | written, "one perfect prompt", standalone by construction |
| GitHub Copilot (Opus 4.8), agentic loop | [#106](https://github.com/vertical-cloud-lab/powder-doser/issues/106) / [#107](https://github.com/vertical-cloud-lab/powder-doser/pull/107) | ran |
| Zoo.dev ML-ephant API | [#108](https://github.com/vertical-cloud-lab/powder-doser/issues/108) / [#110](https://github.com/vertical-cloud-lab/powder-doser/pull/110) | ran (first Copilot attempt blocked by a ruleset) |
| Zoo Design Studio (human-in-the-loop GUI) | [#109](https://github.com/vertical-cloud-lab/powder-doser/issues/109) | manual entry, results reported in-thread |
| CADSmith | [#111](https://github.com/vertical-cloud-lab/powder-doser/issues/111) / [#112](https://github.com/vertical-cloud-lab/powder-doser/pull/112) | ran |
| Human expert in Fusion 360, screen-recorded and narrated | [#120](https://github.com/vertical-cloud-lab/powder-doser/issues/120) | in progress, parts divvied between two students, uploaded to the lab YouTube channel |

Plus a paired simple-part / complex-part ladder run on both Zoo and CADSmith with the same
brief each time: [#52](https://github.com/vertical-cloud-lab/powder-doser/issues/52)/[#53](https://github.com/vertical-cloud-lab/powder-doser/pull/53) and
[#54](https://github.com/vertical-cloud-lab/powder-doser/issues/54)/[#55](https://github.com/vertical-cloud-lab/powder-doser/pull/55) (simple: an auger shaft-collar
bracket), [#56](https://github.com/vertical-cloud-lab/powder-doser/issues/56)/[#57](https://github.com/vertical-cloud-lab/powder-doser/pull/57) and
[#58](https://github.com/vertical-cloud-lab/powder-doser/issues/58)/[#59](https://github.com/vertical-cloud-lab/powder-doser/pull/59) (complex: hinged mounting
plate + baseplate with a linear-actuator tilt).

**What makes this publishable rather than merely internal:** a matched human-expert control
arm, a real engineering spec with interference constraints rather than a synthetic
benchmark prompt, and parts that get **printed and assembled** — so the outcome measure can
be "did it fit and function", not Chamfer distance against a reference mesh. Every published
text-to-CAD benchmark the org's own literature notes cite (DeepCAD, Fusion 360 Gallery, ABC,
SketchGraphs, Text2CAD, GenCAD-Code, Omni-CAD) evaluates against reference geometry, not
against whether the part works in an assembly that was independently specified.

The missing pieces are a pre-registered rubric and a scoring protocol. That is days of work,
not months.

## 2. Hard numbers already measured in-house

Pulled out of comment threads, because they are the kind of thing that gets lost:

- **Zoo.dev ML-ephant text-to-CAD**: ~14–16 min per fresh job, **$6.89** per call in
  [#7](https://github.com/vertical-cloud-lab/powder-doser/pull/7); returns STEP (real
  B-rep, not mesh) + KCL source + glTF. The `/ml/text-to-cad/iteration` endpoint is
  **~5.5 min vs ~14 min fresh** and **preserves named parameters across edits**, which is
  the property that makes it usable in a loop at all.
- **One-shot fails in a specific, repeatable way.** The full-system prompt made ML-ephant
  (a) slice the auger open to "show" internals — a rendering-style cheat, not geometry —
  and (b) bolt on a hopper nobody asked for, because the prompt said "powder dosing".
  Narrow per-part prompts (≤6 sentences, explicit dimensions, explicit *negative*
  constraints) fixed both. That is a reproducible failure taxonomy with a stated mitigation.
- **The Judge loop was already ported here.** `cad/meta-tools/render_step.py` does
  CadQuery `importStep` → `toVtkPolyData(tol=0.03)` → VTK offscreen → PNG under
  `xvfb-run`, explicitly as the CADSmith-style VLM-Judge render step. Grading is
  bbox / solid-count / manifold against a **hand-authored CadQuery ground truth**.
- **Literature baselines already collected** in
  [#29](https://github.com/vertical-cloud-lab/powder-doser/pull/29) (`paper/background/03`–`06`):
  CADSmith ~38× Chamfer reduction, CADCrafter 3.6% invalid rate, GenCAD-Self-Repairing
  65.84% repair rate, CADReview's **GPT-4o detecting only 41.5%** of human-made errors in
  OpenSCAD programs, and Sadik & Bujny 2025's **zero Hausdorff distance for code-level
  human edits** vs. image-only correction. The last two together are the argument for why
  a deterministic verifier plus a code-level human review beat model self-correction.
- **Onshape REST works headlessly** with classroom-scoped keys — STEP in via
  `POST /blobelements/...?translate=true`, STL/STEP back out via `/translations` — so an
  "LLM emits code → kernel regenerates → REST exports STEP" loop has a validated transport.

## 3. There is already a live custom-gripper problem in this org

[`powder-doser` #128 (multi-doser)](https://github.com/vertical-cloud-lab/powder-doser/issues/128)
is a carousel of auger modules, and the stated approach is a **solenoid-driven single-link
arm with a gripper on the end that grabs augers and holds them in place, replacing the
brackets**. The thread already worked out the two things that decide whether such a gripper
is easy or impossible:

- **Key the interface, don't make the gripper smart.** A D-flat, hex boss, or two-pin
  bayonet bolted to the chain attachment link makes yaw deterministic, "and stays
  deterministic through pick/place if the gripper indexes on the same key." This is the
  same conclusion the arm-side scan reached from the other direction — fixtures provide the
  precision seat, the arm provides transfer.
- **Don't index off motor steps.** Chordal action on a roller chain pulses speed ~5% at 10
  teeth, ~2% at 15; use ≥19 teeth and index off a per-module datum the gripper pulls into
  (or the RFID tag from [#133](https://github.com/vertical-cloud-lab/powder-doser/issues/133)).

[#92](https://github.com/vertical-cloud-lab/powder-doser/issues/92) already contains a
**Zoo Design Studio "Gripper File" + transcript** from a hands-on session, so there is a
generated-gripper artifact in the org to use as a baseline.

**The obvious move:** that single-link solenoid arm is a 1-DOF special case of the job a
PiPER would do. Designing the auger-exchange end effector once, for both, turns a
one-off mechanism into the first end-effector study.

## 4. Compliant-mechanism tooling exists here and is shelved

[`powder-doser` #5](https://github.com/vertical-cloud-lab/powder-doser/pull/5) built a
**bistable snap-through compliant trough** with a real analysis stack:
`scripts/bimodal_compliance.py` (energy landscape → peak snap force **2.358 N**, barrier
**2.91 mJ**, wells **±1.901 mm**), a robustness sweep (`--samples 256`, P(bistable) = 1.000,
pre-compression dominating variance at S₁ ≈ 0.84), a parametric OpenSCAD source whose
variables mirror the `FlexureParams` dataclass, and pytest regression tests asserting
bimodality. Print guidance from the same thread: **PETG, not PLA** (PLA too brittle at ~3%
snap-through strain), base flat on the bed so **layer lines run along the flexure length**
or it delaminates after a few snaps, ≤0.2 mm layers so a 0.6 mm flexure has 4 layers across
the bending direction, ~45 min / ~6 g per copy.

sgbaird closed the topic with "probably not going to do anything else with the bimodal
compliant mechanism design" — but the *tooling* is the reusable asset. A compliant /
underactuated gripper finger is the same analysis: energy landscape, snap force, print
orientation, fatigue. The 100-cycle fatigue protocol sketched there is the seed of the
cycle-life measurement the arm-side scan says nobody reports.

## 5. Digital twin: already scanned, don't re-ask

[`powder-doser` #158](https://github.com/vertical-cloud-lab/powder-doser/issues/158) already
ran a high-effort Edison query on digital-twin / physics simulation for design iteration
(task `674609d3`, answer committed as
`docs/edison/literature-high-digital-twin-simulation.md`). Its conclusions constrain what
"generative systems design" can honestly claim here:

- **MATTERIX** (Isaac Sim/Isaac Lab, PhysX PBD particles, semantics engine; sim-to-real 75%
  pick-and-place, 90% pouring) is the right template for the **workflow/motion** layer of a
  twin and explicitly *not* calibrated for powder micromechanics — no JKR/EEPA cohesion, no
  triboelectrics — so it cannot rank doser geometries on milligram-scale dose CV.
- Calibrated cohesive DEM (LIGGGHTS / MercuryDPM / Yade, or EDEM/Rocky) is the quantitative
  tier: screw/auger thrust within 5–20% of experiment, angle of repose within 2–3%, ~10%
  sim-to-real on bucket filling. A DEM + surrogate + NSGA-II screw-conveyor optimization
  was **hardware-validated** (+15.8% mass flow, −26.2% energy) — published precedent for
  sim-in-the-loop geometry optimization.
- Calibration is the crux: ~144 simulations for 4 parameters via CMA-ES, with parameter
  non-uniqueness the trap (same repose angle, different dynamics).
- **Nobody simulates the measurement chain** — no published work puts a balance in the loop
  (settling time, tapper vibration, stable-reading logic). Cheap gap, ours to take.

## 6. What the arm changes about all of this

The PiPER is not a new subject; it is the missing actuator for problems this org has already
framed:

- `tensegrity-optimization` closes a BO loop through print → drop test with **manual
  specimen handling**. An arm that seats a coupon in the fixture is the difference between a
  demo and an overnight campaign.
- `powder-doser` #128's auger exchange is a pick-and-place task in disguise.
- `caliber` + the OT-2 + `digital-wetlab` give a second workflow with different failure
  modes, which is what a reliability study needs to avoid being single-system anecdote.
- CADSmith gives a *generator* for end-effector geometry, and the printed-and-tested
  grasp-success rate gives it an outcome measure that no text-to-CAD benchmark currently
  has.

## 7. Where the survey says to be careful

- **Generative CAD landscape is already well covered in-house** (`paper/background/03`–`06`,
  five Edison queries plus artifacts). Another landscape query would be waste; the open
  question is specifically *generative design of end effectors with fabricate-and-test
  outcomes*, which is what Q3 of the 6DOF scan asks.
- **Commercial generative-design suites were already triaged and rejected** on the
  editability/scriptability filter — nTop, Creo Generative, Siemens NX TO, ANSYS Discovery,
  Altair Inspire all "skip on the proposal budget"; Onshape Education and Zoo.dev Plus
  ($20/mo) were the two "try" verdicts. Re-litigating that is a waste of a session.
- **Static charge is an open in-house question** ([#84](https://github.com/vertical-cloud-lab/powder-doser/issues/84):
  ground the auger, or is grounding the aluminium crucible enough?) and it is unmodelled in
  every simulation engine the #158 scan surveyed. Anything an end effector does with dry
  metal powder inherits this.

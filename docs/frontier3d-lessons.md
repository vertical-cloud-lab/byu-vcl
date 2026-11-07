# What Frontier3D can teach our generative-CAD and systems-design work

Written for [#330](https://github.com/vertical-cloud-lab/byu-vcl/issues/330) on 2026-11-07. I read Frontier3D at commit
[`2ad47eb`](https://github.com/Einsia/Frontier3D/tree/2ad47eb), together with its paper (dated 2026-11-06), and read our own repos at their heads that day. Section 3 inventories about 160 of our attempts across 11 vertical-cloud-lab repos. Work that moved between repos (byu-vcl → robot-arms, byu-vcl ↔ digital-alloy-lab) is counted once, under the repo where most of the thread lives.

## TL;DR

1. **Frontier3D is a benchmark, not a CAD tool.** Coding agents write Blender (L1/L2) or Unreal (L3) code. The harness rebuilds that code in a sealed container and scores it. It won't model our parts for us; how it evaluates them is the part we can borrow.
2. **Its L1 Text2Code tasks are the kind of part we design:** a two-axis camera bracket, a lead-screw slide stage, a sealed electronics enclosure, a pillow-block bearing. Frontier agents score 76–84/100 on them while generating **blind**: no render, no measurement, and only execution errors fed back.
   - Those task specs are AI drafts not yet calibrated by a human (`"annotation_review": "ai_draft_pending_human_calibration"`), and Text2Code is not human-validated.
   - The checks that matter most to us (assembly clearance, mating, coaxiality) are mostly `missing` or left to the vision model.
   - So their high Text2Code scores say almost nothing about whether a part would fit.
3. **Our agents mostly checked a model against itself, then the part failed against the real one.** The self-checks were interference of 0 mm³ against their own proxies, FEA, manifold checks, slicing, or a pass from the vision judge. The failures came from guessed vendor dimensions, unmodelled cables and set screws, the wrong lens, a missing PCB thickness, or printer tolerance. Nearly every correction came from a person's eye, a caliper or a failed print.
4. **What carries over is the structure of their evaluation, aimed at what they don't measure and we keep failing.**
   - The structure: a frozen map from each requirement to a check, with honest coverage status; semantic labels, so geometry can be measured directly; a blind judge that lists issues and fails closed; a gate that rebuilds from source; the worst case over variants; and edits scored on both the change and what was preserved.
   - The target: fit against **measured mating geometry** and **printer-calibrated tolerances**.
5. **We already have most of the checking code, but it is scattered.** It sits on about 15 unmerged branches across five repos (§3.9), and none of it runs as a standing gate. Merging it is the cheapest large improvement.
6. **[#325](https://github.com/vertical-cloud-lab/byu-vcl/issues/325#issuecomment-6666720744)** (the AI-for-Science credit application) already promises "a benchmark of 30 real lab parts against hand-designed baselines".
   - Frontier3D's task-package layout (a public `instruction.md`, a private `harness/`, a `solution/`) is a ready template for it.
   - Our solved cases are unusually good ground truth: the part that physically worked, plus the human corrections that got it there.

---

## 1. What Frontier3D actually is

[Einsia/Frontier3D](https://github.com/Einsia/Frontier3D/tree/2ad47eb) ("Frontier3DBench"; [paper](https://lab.einsia.ai/frontier3dbench/Frontier3DBench.pdf), [project page](https://lab.einsia.ai/frontier3dbench)) has 145 tasks. Agents run through Claude Code, Codex or a vendor CLI. They submit Blender Python or an Unreal project, which is executed and scored.

| Level | Tasks | What the agent builds | Closest lab analogue |
| --- | ---: | --- | --- |
| L1 Text2Code | 15 | Mechanical assemblies from text: bolted flange, pillow-block bearing, lead-screw slide stage, machine vise, pulley clevis, six-hole indexing turntable, sliding latch, sealed electronics enclosure, filter housing, telescoping lock pin, two-axis camera bracket, four-roller guide fixture | Mounts, enclosures, stages, fixtures |
| L1 Image2Code / SingleView | 25 / 25 | An object from multi-view or single reference images (an opening cabinet hinge with telescoping struts, a bench drill, a turbofan, …) | Copying a part from a photo or a vendor drawing |
| L2 Brief2Scene / Reference2Scene / RealPhoto | 20 / 10 / 25 | A whole scene from a brief or from reference images | Cell, bench or deck layout |
| L2 SceneEdit | 10 | A change to an existing scene: the requested edit made **and nothing else changed** | Revising an existing part or layout |
| L3 Text/Image2Environment | 5 / 10 | Interactive Unreal environments | Little direct analogue |

### Scoring

From [`docs/en/scoring.md`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/docs/en/scoring.md) and [`metrics.md`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/docs/en/reference/metrics.md):

- **Text2Code:** `0.60 vlm + 0.30 data + 0.10 detail`.
  - `data` is the mean of frozen native checks measured in Blender: part inventory, closed, connected, solid validity, hole probes, part count and hierarchy.
- **Image tasks:** `0.50 main_image + 0.20 localization + 0.20 vlm + 0.10 detail`.
- **SceneEdit:** `0.20 numeric + 0.30 target + 0.20 preservation + 0.20 vlm + 0.10 detail`.
- **Detail:** a frozen checklist of local-shape "atoms", each scored `coverage × (1 − deviation)`.
  - It takes the **minimum over 8 variants**: the primary run plus three seeds, each as a native scene and as a GLB export.
  - So a model that is right once, but not reproducibly, gets its worst variant's score.
- **VLM rubric:** integer grades 0–4 per frozen criterion.
  - Fidelity answers must name the achieved features, the largest discrepancy and its severity. The maximum grade for each severity is: `none` 4, `minor` 3, `major` 2, `wrong_or_absent` 0, `not_demonstrated` 0.
  - Inconsistent answers are rejected.

### How generation works

The released route ([`orchestrator/generator.py`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/orchestrator/generator.py), [`orchestrator/feedback.py`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/orchestrator/feedback.py)) works like this:

- **What the agent can do:**
  - It returns one JSON bundle of source files and is told "it may not have Python or Blender installed".
  - Claude Code runs with `--tools Read,Glob,Grep[,Bash]`. The generator image has no Blender in it.
- **Attempts:** up to 6, using the policy `'feedback': 'previous_response_and_public_execution_errors'`, `'selection': 'first_executable_submission'`, `'score_feedback': False`.
- **What a repair sees:** "Only public execution/delivery errors are provided. No score or private reference is available."
- **The legacy L2 route did show the agent its renders.** It had a `preview.py` broker that rendered the draft "in the actual isolated Blender environment". The paper's runs don't use it.

### Results

Paper Table 3, matching the project page:

| Model (harness, effort) | Total | Text2Code | Image2Code | SingleView | L1 | L2 | L3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6.1-sol (Codex, max) | **66.02** | 82.10 | **69.61** | **66.26** | **71.21** | **70.35** | 58.89 |
| GPT-6-astra (Codex, max) | 63.85 | 79.54 | 68.44 | 62.28 | 68.63 | 62.51 | **61.28** |
| Claude Opus 5.5 (Claude Code, max) | 62.29 | **84.05** | 66.73 | 58.00 | 67.37 | 62.61 | 58.23 |
| DeepSeek-v4.1-Flash (DSH, max) | 57.45 | 83.17 | 57.49 | 56.92 | 63.20 | 62.00 | 49.72 |
| Kimi-K3.1-Pro (Kimi CLI, max) | 55.96 | 83.34 | 56.25 | 53.23 | 61.34 | 59.42 | 49.34 |
| Qwen3.8-Max (Claude Code, xhigh) | 46.03 | 81.98 | 43.97 | 37.34 | 50.19 | 50.64 | 39.44 |

Findings relevant to us:

- **Text beats images, everywhere.**
  - Text2Code ranges from 75.93 to 84.05, but the best multi-view and single-view reconstruction scores are only 69.61 and 66.26. Every configuration scores lower on reconstruction than on text, at both L1 and L2.
  - For us, a part specified as dimensioned text (a vendor drawing transcribed into numbers) is an easier problem than "copy this from a photo".
- **Structure is easier than fidelity.**
  - Averaged across models: L1 structure 72.77, visual quality 57.28, task fulfilment 52.15.
  - Claude Opus 5.5 has both the highest Text2Code score (84.05) and the highest L1 structural score (83.27). That is the model and harness we already use, and Text2Code is the category closest to our work.
- **Mechanisms work in isolation, not in sequence.** On L3, local mechanisms average 83.08, but motion clearance averages 20.82 and stateful workflows 30.26.
- **Cost doesn't track score.** Estimated cost per task is Sol $1.01, DeepSeek $0.45, Opus $21.17: "Higher estimated spending does not consistently yield higher scores."
- **Human agreement was measured only for the reference-image families:** Kendall τb 0.727 against human rankings, versus 0.679 between human raters. The judge, GPT-6-astra, is from the same family as the top two models.

### Evaluation rules worth copying

Paraphrased from `scoring.md`, `metrics.md` and the code:

1. **Delivery is a gate, separate from quality.** An unloadable scene, a missing export or a forbidden dependency sets `S_core = 0`. "A passed system gate does not establish semantic task quality."
2. **The generator never sees the grading.** Grading notes stay in organizer-only `harness/` and `solution/` directories, and no task root or evaluator is mounted into the candidate's container.
3. **Freeze the source, then measure it.** The accepted source is bound to a hash and rebuilt in a container with `--network none --read-only`.
   - A re-render from the saved file is authoritative. The agent's own submitted PNG is kept only as a diagnostic.
4. **A missing measurement is not a zero and not a pass.**
   - API, render or infrastructure failures stay `null` and block the final score. They are never filled with zero or weighted away.
   - A measured candidate defect zeroes only the check it affects.
5. **No judge shopping.** Judge retries repair transport or schema failures only, and "accept the first valid judgment regardless of score".
   - Judges never see other candidates or earlier scores.
   - Their L2 audit judge is told "DO NOT output scores". It lists issues, and code converts them to deductions at fixed severities. "Unobservable" withholds credit instead of granting it, and the prompt reminds the judge that "AABBs do not prove holes or contacts."
6. **Shortcuts are checked for.**
   - Material nodes, packed-image hashes and UV coverage are traced: "A full reference on a simple plane violates the modeling contract."
   - Text tasks ban bitmaps outright.
   - Instructions name the shortcut in advance, e.g. "a box with sail triangles is insufficient".
7. **Robustness means the minimum, not the mean.** Detail takes the worst result across seeds and export formats.
8. **Measure geometry directly; use the VLM only where that is impossible.**
   - Parts are matched to required roles "by measured geometry, never by object names… one candidate object cannot satisfy two roles".
   - Holes are probed with radial ray-casts on several z-layers, plus an axial through-test.
   - Motion (the Image2Code_008 cabinet hinge) is checked over frame-keyed poses with invariants: distance to the axis, monotonic opening, return to closed, rigidity, attachment. The VLM is not involved.
9. **Coverage is reported honestly.** Each requirement maps to `check_ids` with an `implementation` status of `complete`, `partial` or `missing`, and weights are labelled `pilot_not_calibrated` when they are guesses.

---

## 2. How a task is specified so it can be checked (two worked examples)

### 2a. L1 Text2Code_011: two-axis camera bracket

- **What the candidate sees** ([`instruction.md`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/data/3dbench/tasks/L1/Text2Code/task_L1_Text2Code_011/instruction.md), 21 lines). One dense paragraph carries every number:
  - "Build a 19-part camera mount… The base is 90 × 90 × 8, bottom Z=0, central bore 16.4"
  - "Leave the 1 mm lateral gap between platform and each upright"
  - holes of diameter 6.4 at (±35, ±35), with bolt-and-washer pairs
  - "All parts must be closed, individually connected and separately editable. Preserve real holes and specified clearances, with dimensional and placement errors no greater than 0.3 mm. Do not add threads, fillets or hidden machinery"
  - "Export in metres. Save the assembled state at frame 1 and a readable exploded state at frame 61"

  It gives a frozen run command and an exact output tree. **It specifies no pan or tilt range.**
- **What only the organizer sees** (`harness/eval_spec.json`, `alignment.json`):
  - Tolerances of 0.3 mm on dimensions and 0.15 mm on bore radius; seeds `[0,1,2]`.
  - Critical constraints: part count, closed, connected, valid solid, export, materials, and quality on every seed.
  - Checks: a bounding box per part role; ray-cast probes of the base holes, base bore and fork bore; `part_count == 19`; and `all_parented`.
  - Each of the 23 requirements is mapped to its checks with an honest status. `assembly_clearance` is `"implementation": "missing"`.
  - Across all 15 Text2Code tasks (307 requirements), checks are 15 % complete, 74 % partial and 12 % missing. Assembly clearance is missing in 12 of the 15 tasks.
- **Detail atoms (9, equal weight, judged by the VLM from the two renders).** Base, pan sleeve, spindle, fork base, uprights, bushings, platform, tilt pins, fasteners. Each atom carries its numbers, e.g. "bushings OD 14 / bore 8.4 / L 6 at (±28,0,69)".
  - Coverage rule: "simple placeholders and repeated primitives count toward coverage only for truly matching structure."
  - Deviation rule: rates only what was built; exact values are "measured separately by native clauses."
- **What is measured and what is not.**
  - Measured in Blender: inventory, part count, closed, connected, valid solid, a few hole radii and through-holes, parenting, the bitmap ban, GLB loading, seeds.
  - Left to the VLM: positions, coaxiality, mating and contact, **the 1 mm gap**, and fastener seating.

The 1 mm gap and the fastener seating are exactly the things that failed on our camera mounts (§3), and they are exactly what Frontier3D does not measure.

### 2b. L2 Brief2Scene_001: a harbour, structured like a lab-layout brief

**The candidate's [`instruction.md`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/data/3dbench/tasks/L2/Brief2Scene/task_L2_Brief2Scene_001/instruction.md):**

- **Measurable clauses:**
  - "a continuous walking route at least 1.2 m wide from the shore to the docking end"
  - "hull must sit partly below the water while its accessible deck is above it"
  - "at least five barrels and five crates… without blocking the pier connection"
- **Shortcuts named in advance.**
- **Units and frame:** "metres and Z up".
- **A clean-room run command:** `blender --background --factory-startup --python output/solution.py -- …`.
- **A semantic label on every entity** (`bench_role`), from a fixed vocabulary. This one line is what lets the evaluator *measure* the scene rather than ask a VLM about it.

**The organizer-only [`harness/methods.json`](https://github.com/Einsia/Frontier3D/blob/2ad47eb/data/3dbench/tasks/L2/Brief2Scene/task_L2_Brief2Scene_001/harness/methods.json)** (translated from Chinese):

| Row | What is checked | How |
| --- | --- | --- |
| Execution validity | Files present, entry point runs, native re-render, missing dependencies | A clean workspace with only the empty `input/` and the brief mounted. The checker never reads `solution/` |
| Requirement coverage | Every verifiable clause in the brief | "Split each verifiable requirement into an evaluator-side checklist; count semantic instances, not objects; unrequested decoration is not penalized" |
| Geometry & layout | Support, connection, gaps, occlusion, explicit scale | World-coordinate measurements. Stated minimums get a 1 % tolerance and "approximately" gets ±10 %. "Hard thresholds only for relations mentioned in the brief" |
| Spatial plausibility | Interpenetration volume, floating distance, route connectivity | BVH collision sampling, with intended contacts excluded by role. A planar occupancy map, with obstacles inflated by the required clear width, is tested for connectivity |
| Physics | Static support | `static-support-v1`: gravity along −Z, 0.02 m contact tolerance |
| Reproducibility | Two runs with the same seed | Geometry and material digests compared |
| Efficiency | Time, tokens, tool calls, failures | Recorded, but "quality and cost reported separately" |

`hidden_dimensions_or_object_names_as_requirements: false` means nothing is graded that the brief didn't ask for.

Point that table at a robot cell or an instrument deck and it becomes a systems-design acceptance test: a clear route for the arm, no interpenetration, everything supported, counts and spacings as stated, and a layout that rebuilds from source.

---

## 3. What we have tried

**Legend:**
- Outcome: ✅ worked · 🟡 partial · ❌ failed · ⏸ abandoned or superseded · ❔ unknown or never tested.
- `I#n` / `P#n` are issues and PRs in the repo of that subsection.
- † marks rows read from a title or diffstat only, not the thread.

### 3.1 byu-vcl

| Link | What | Approach | Outcome → lesson |
| --- | --- | --- | --- |
| [I#5](https://github.com/vertical-cloud-lab/byu-vcl/issues/5), [I#39](https://github.com/vertical-cloud-lab/byu-vcl/issues/39) | 384-well plate | Human Fusion 360 model from the Greiner datasheet; resin print; Labware JSON | ✅ Print orientation and supports changed the fit more than the CAD did |
| [I#33](https://github.com/vertical-cloud-lab/byu-vcl/issues/33), [I#100](https://github.com/vertical-cloud-lab/byu-vcl/issues/100) | Colour-sensor enclosure | Reprinted upstream STEP/3MF | ⏸ Upstream files were wrong, old or empty |
| [P#60](https://github.com/vertical-cloud-lab/byu-vcl/pull/60), [P#116](https://github.com/vertical-cloud-lab/byu-vcl/pull/116) | P20 press-fit fake tip; sensor dock | build123d plus FEA, bore-sweep prints, OT-2 pick videos | 🟡 Web-sourced dimensions fit the wrong feature ("attaching to the tip ejector mechanism"). The bore error carried into P#116. Superseded by buying a P300 |
| [I#27](https://github.com/vertical-cloud-lab/byu-vcl/issues/27), [P#90](https://github.com/vertical-cloud-lab/byu-vcl/pull/90), [P#98](https://github.com/vertical-cloud-lab/byu-vcl/pull/98) | Echem cell | Upstream SLA design printed outside the lab | 🟡 Check build volume and resin first |
| [I#64](https://github.com/vertical-cloud-lab/byu-vcl/issues/64), [I#167](https://github.com/vertical-cloud-lab/byu-vcl/issues/167), [I#147](https://github.com/vertical-cloud-lab/byu-vcl/issues/147)/[P#174](https://github.com/vertical-cloud-lab/byu-vcl/pull/174) | Vial rack, Zero 2W camera mount, electromagnetic capper | Reused proven open designs | ✅ Reuse is cheapest |
| [I#111](https://github.com/vertical-cloud-lab/byu-vcl/issues/111), [P#295](https://github.com/vertical-cloud-lab/byu-vcl/pull/295) | Vacuum chamber, POV mounts | Buy-vs-build studies | ⏸ Buying won |
| [I#31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31), [P#96](https://github.com/vertical-cloud-lab/byu-vcl/pull/96), [P#109](https://github.com/vertical-cloud-lab/byu-vcl/pull/109) | Lab layout | Annotated floor plan plus docs | 🟡 No layout model; vendors lack dimensions |
| [I#34](https://github.com/vertical-cloud-lab/byu-vcl/issues/34), [P#84](https://github.com/vertical-cloud-lab/byu-vcl/pull/84) | OT-2 overhead camera | Field-of-view doc with estimates | ⏸ Wrong machine dimensions ("much more than 7 inches") |
| [I#187](https://github.com/vertical-cloud-lab/byu-vcl/issues/187) | CAD platform | Fusion 360 → Onshape | ✅ Code-CAD gives provenance; record GUI modelling with narration |
| [I#169](https://github.com/vertical-cloud-lab/byu-vcl/issues/169) | P20 dummy pipette | OpenSCAD with "measure-me" estimates | ❌ "best to ditch Claude's efforts, at least on this task" |
| [I#151](https://github.com/vertical-cloud-lab/byu-vcl/issues/151#issuecomment-5148536761) | Tip-rack edit | trimesh/manifold3d boolean on the vendor STL | ❔ Its symmetric difference with the stock part was 0 outside the plate: a preservation check, done by hand |
| [I#165](https://github.com/vertical-cloud-lab/byu-vcl/issues/165#issuecomment-6044748800) | Cubware camera mount, STL → STEP | OCP primitive fitting | ✅ on the third try. A faceted STEP is useless |
| [P#171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171), [P#228](https://github.com/vertical-cloud-lab/byu-vcl/pull/228) | CubOS offsets and safe-z | `validate_setup`, `--mock`, `passive_shadow.py` | ✅ after real collisions. The stock gates checked only the commanded tool |
| [P#269](https://github.com/vertical-cloud-lab/byu-vcl/pull/269) | Magnetic vial stirrer | Onshape FeatureScript, then CadQuery; magpylib, MuJoCo, G-code fit, Hall-sensor rpm | ✅ after many rounds. The fit (0.05 mm) and the magnet gap could only be tuned on prints |
| [I#266](https://github.com/vertical-cloud-lab/byu-vcl/issues/266), [P#272](https://github.com/vertical-cloud-lab/byu-vcl/pull/272) | Arm ↔ CubXL dock and fingers | CadQuery from vendor STEP, FK/IK margins, headless slice | ❔ Strong pipeline, never printed |
| Branch [`issue-213`](https://github.com/vertical-cloud-lab/byu-vcl/tree/41c02d6/modules/openraman-cubxl) † | OpenRAMAN on the CubXL | Official STEP, search over 7,420 poses | ❔ Rests on an unpinned CubOS ↔ PandaDeck coordinate assumption |
| [P#274](https://github.com/vertical-cloud-lab/byu-vcl/pull/274), [P#297](https://github.com/vertical-cloud-lab/byu-vcl/pull/297) | Doser module, auger-cartridge stack | build123d + pyvista, tilt sweep | ❔ "Nothing has been built or tested"; the CubXL was modelled as boxes until a person measured it |
| [I#307](https://github.com/vertical-cloud-lab/byu-vcl/issues/307), [P#308](https://github.com/vertical-cloud-lab/byu-vcl/pull/308) | CubXL schematic | matplotlib from calibration YAMLs | 🟡 "frame members sized by eye"; there is no CubXL CAD |
| [P#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234) | OT-2 lid camera mount | CadQuery (12 interference pairs), Onshape REST + UI, Bambu CLI slice, G-code `fit_sim`, FEA, MP4 | ✅ installed and in focus. Fit errors only showed up on prints ("both rings were too small"; "forgot… the pcb of the cam is 2mm thick") |
| [P#241](https://github.com/vertical-cloud-lab/byu-vcl/pull/241) | Pi 5 dual-camera bracket | CadQuery vs vendor STEP (73 pairs), Onshape replay | 🟡 Interference checks miss load paths ("will probably need some extra support") |
| [P#245](https://github.com/vertical-cloud-lab/byu-vcl/pull/245) | PiPER wrist camera mount (v1) | CadQuery in the gripper's STEP frame, voxel FEA from G-code | 🟡 FEA on the as-sliced part reversed a README instruction. Continued in robot-arms |
| [P#257](https://github.com/vertical-cloud-lab/byu-vcl/pull/257) | Atomizer cable holder | Human Onshape design; agent rebuilt and diffed it (0.1 mm³), clip FEA | ✅ The agent once exported a stale version |
| [P#296](https://github.com/vertical-cloud-lab/byu-vcl/pull/296) | Viewport camera units | 957-line FeatureScript, 57 sourced guesses as named variables, measuring guide | ❔ Turning guesses into named variables is the right pattern. Moved to DAL |
| [P#255](https://github.com/vertical-cloud-lab/byu-vcl/pull/255), [P#327](https://github.com/vertical-cloud-lab/byu-vcl/pull/327) | rePowder model and animations; registration | CadQuery from video frames, per-frame `collide.py`; `register.py` pinhole fit (held-out view 9.1 px RMS) | 🟡 Unchecked renders were physically wrong ("Elastigirl / Mr. Fantastic powers"). Fitting to reference frames caught a guessed hinge axis |
| [P#232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232), [P#277](https://github.com/vertical-cloud-lab/byu-vcl/pull/277) | Al charge cup and press-fit plug | build123d with von Mises `fit_check`, drawings, lathe | ✅/🟡 The analysis corrected the interference; the student machinists couldn't hold it ("just barely too small for a press fit") |
| [P#240](https://github.com/vertical-cloud-lab/byu-vcl/pull/240), [P#254](https://github.com/vertical-cloud-lab/byu-vcl/pull/254) | Generative-CAD survey, `lab-models/`, pick shelf | Survey; 57 objects from specs; reach map | 🟡 The survey: "The missing pieces are a pre-registered rubric and a scoring protocol." |
| [I#303](https://github.com/vertical-cloud-lab/byu-vcl/issues/303), [P#318](https://github.com/vertical-cloud-lab/byu-vcl/pull/318), [P#320](https://github.com/vertical-cloud-lab/byu-vcl/pull/320), [P#321](https://github.com/vertical-cloud-lab/byu-vcl/pull/321), [P#328](https://github.com/vertical-cloud-lab/byu-vcl/pull/328), [P#329](https://github.com/vertical-cloud-lab/byu-vcl/pull/329) | Vertical-lab animations (about 40 instruments) | CadQuery → PyVista, FCL, MuJoCo + CoACD, reach | 🟡 Each plausibility error came back until it became an automated check ("Passed through the MiR250"; "oriented 90 degrees the wrong way") |
| Print pipeline: [I#82](https://github.com/vertical-cloud-lab/byu-vcl/issues/82), [P#145](https://github.com/vertical-cloud-lab/byu-vcl/pull/145), [P#280](https://github.com/vertical-cloud-lab/byu-vcl/pull/280), [P#316](https://github.com/vertical-cloud-lab/byu-vcl/pull/316), … | `@claude-print` | Approval gate, plate self-check, nozzle check | ✅ Every rule followed an incident. End to end on 11-02 ([P#95 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-6589992268)) |

### 3.2 powder-doser

About 50 attempts. GitHub calls this repo "G-code" because of two identical 16 MB PrusaSlicer files committed during the auger work. Nothing in the repo generates G-code.

| Link | What | Approach | Outcome → lesson |
| --- | --- | --- | --- |
| [P#2](https://github.com/vertical-cloud-lab/powder-doser/pull/2), [P#5](https://github.com/vertical-cloud-lab/powder-doser/pull/5)/[P#14](https://github.com/vertical-cloud-lab/powder-doser/pull/14) | Scoop "excavator"; bistable trough | CadQuery + `cad/dfm.py` (28 checks); OpenSCAD + CalculiX + Edison | ⏸ Renders showed the agent had misread the mechanism ("It doesn't touch anything, it just drops"). The physics check killed the trough early |
| [I#6](https://github.com/vertical-cloud-lab/powder-doser/issues/6)/[P#7](https://github.com/vertical-cloud-lab/powder-doser/pull/7) | Tool survey | Rhino/Compute, nTop, Fusion generative design, Onshape, zoo, Leo, Adam, CADScribe | 🟡 "You have a full dev environment. You should try to install each of these" |
| [P#13](https://github.com/vertical-cloud-lab/powder-doser/pull/13) | Dosing concepts A–H | OpenSCAD cutaways, 2-D animations | ❌ Spatially inconsistent; "use something more physical (e.g., CAD software" |
| [P#16](https://github.com/vertical-cloud-lab/powder-doser/pull/16) | 25 mm Archimedes auger | OpenSCAD, slicers, prints, salt test | ✅ "We did end up using this". The slicer's floating-cantilever warning predicted the failed print |
| [I#34](https://github.com/vertical-cloud-lab/powder-doser/issues/34)/[P#35](https://github.com/vertical-cloud-lab/powder-doser/pull/35) | Whole module from text | CadQuery, 2 rounds of Edison VLM judging | ❌ "3 bodies in what should be a single-body part. You consistently have trouble with that kind of reasoning." Led to working part by part |
| [P#47](https://github.com/vertical-cloud-lab/powder-doser/pull/47), [P#49](https://github.com/vertical-cloud-lab/powder-doser/pull/49), [P#51](https://github.com/vertical-cloud-lab/powder-doser/pull/51) | Auger bracket; geared auger + NEMA 11 pinion; tap collar + mount plate | CadQuery / OpenSCAD / zoo KCL from human drawings | ✅ after rounds. Edits broke function ("The archimedes screw is gone"; "you did it backwards"). The hole pattern was fixed only by the vendor PDF. P#51 is still the only AI-made part on the rig |
| [P#53](https://github.com/vertical-cloud-lab/powder-doser/pull/53), [P#55](https://github.com/vertical-cloud-lab/powder-doser/pull/55), [P#57](https://github.com/vertical-cloud-lab/powder-doser/pull/57), [P#59](https://github.com/vertical-cloud-lab/powder-doser/pull/59) | Bracket and hinged-plate bake-off | zoo, "CADSmith-style" (really hand-written), CADSmith | 🟡 Invented features ("pyramidical-looking base"); tool misattribution; "placement of the motor was nonsensical… if you had pulled the models from #48" |
| [P#66](https://github.com/vertical-cloud-lab/powder-doser/pull/66) | Dual-servo tilt hinge | CadQuery involute gears, 0–90° collision sweep | 🟡 Gears stripped; the servo mount was sawn off. Vendor servo dimensions were missing |
| [I#72](https://github.com/vertical-cloud-lab/powder-doser/issues/72), [I#120](https://github.com/vertical-cloud-lab/powder-doser/issues/120) | Record of prints; official redraw | Humans in Fusion 360 | AI parts redrawn "to match original design intent, not the ai-generated parts" |
| [P#81](https://github.com/vertical-cloud-lab/powder-doser/pull/81) | Auger capacity | Analytic model, deliberately no CAD | ✅ Within 1 % of the STL meshes |
| [I#92](https://github.com/vertical-cloud-lab/powder-doser/issues/92) | Chain rack, gripper | Zoo Design Studio, used by humans | 🟡 Best spatial reasoning of the tools tried, but ~1 h per iteration |
| [P#105](https://github.com/vertical-cloud-lab/powder-doser/pull/105), [P#107](https://github.com/vertical-cloud-lab/powder-doser/pull/107), [P#110](https://github.com/vertical-cloud-lab/powder-doser/pull/110), [I#109](https://github.com/vertical-cloud-lab/powder-doser/issues/109) †, [P#112](https://github.com/vertical-cloud-lab/powder-doser/pull/112) | 10-part bake-off from one sourced spec ([SPEC.md](https://github.com/vertical-cloud-lab/powder-doser/blob/5b3b53c/cad/powder-doser-assembly/SPEC.md)) | Copilot CadQuery, zoo API, Zoo Studio, "CADSmith" | ❔ Never scored; the Zoo Studio arm was never reported. Internal thread hit zoo's 420 s limit; a tool was substituted without saying so |
| [P#25](https://github.com/vertical-cloud-lab/powder-doser/pull/25), [P#61](https://github.com/vertical-cloud-lab/powder-doser/pull/61), [P#76](https://github.com/vertical-cloud-lab/powder-doser/pull/76), [I#94](https://github.com/vertical-cloud-lab/powder-doser/issues/94)/[I#95](https://github.com/vertical-cloud-lab/powder-doser/issues/95), [P#100](https://github.com/vertical-cloud-lab/powder-doser/pull/100) | Electronics: BOM, KiCad, PCB, scale loop | Copilot/Claude KiCad, DeepPCB, Quilter | 🟡 → ✅ Footprints invented ("8 pins while the schematic shows it having 9"); "the auger will be rotating, so it can't have any wiring directly attached" |
| [I#128](https://github.com/vertical-cloud-lab/powder-doser/issues/128), [P#185](https://github.com/vertical-cloud-lab/powder-doser/pull/185), [P#188](https://github.com/vertical-cloud-lab/powder-doser/pull/188) | Multi-doser chain carousel v1–v5 | Code-CAD + Onshape REST; 28 McMaster STEPs; 576-instance interference sweeps; FEA | ❔ design only. The checks found 5 real part errors. Humans found violations of the system's purpose ("We can't use a funnel"; "is this not actually using a scale?") |
| [P#170](https://github.com/vertical-cloud-lab/powder-doser/pull/170), [P#178](https://github.com/vertical-cloud-lab/powder-doser/pull/178), [P#176](https://github.com/vertical-cloud-lab/powder-doser/pull/176) | Full-assembly figure; native FeatureScript; whole-doser re-creation | Regression render; fsgen (IoU 1.000000); text-to-cad/cadgen + `dfam-check`, 15 check scripts | 🟡 The checks found a cap thread half a pitch off; a human found an assembly-order swap. The render was stale against the rig; Onshape quota hit (HTTP 402) |
| [P#23](https://github.com/vertical-cloud-lab/powder-doser/pull/23), [P#181](https://github.com/vertical-cloud-lab/powder-doser/pull/181), [I#193](https://github.com/vertical-cloud-lab/powder-doser/issues/193), [P#200](https://github.com/vertical-cloud-lab/powder-doser/pull/200) | Slice-and-send; parts for 25 dosers | Bambu CLI, `print_fit.py`, `@claude-print` | ❌ mostly. "Ghost prints"; bodies "printed as seperate parts instead of printing attatched"; "All printing will be done manually until further notice." The guards did block bad sends |

### 3.3 robot-arms

All the CAD is in unmerged PRs. Several threads started in byu-vcl (P#245, P#240, P#254).

| Link | What | Approach | Outcome → lesson |
| --- | --- | --- | --- |
| [I#4](https://github.com/vertical-cloud-lab/robot-arms/issues/4), [P#10](https://github.com/vertical-cloud-lab/robot-arms/pull/10) | Wrist mount: Pi 5, HQ cam + 6 mm lens, CM3 Wide | CadQuery in AgileX's STEP (sha256-pinned); 66-pair interference at 0 mm³, AprilTag views, CalculiX (solid and as-sliced); Onshape copy | 🟡 **Passed every digital check, then failed physical fit three times:** the HQ housing ("did not have enough clearance for… shoulders of the HQ mount"), the CM3 hole ("too small"), the lens set screw. Fixed by remodelling from RP-008200's vector drawing. Rule: "reliable only source (our estimate based on image as a very last resort)" |
| [I#2](https://github.com/vertical-cloud-lab/robot-arms/issues/2), [P#9](https://github.com/vertical-cloud-lab/robot-arms/pull/9) | Enclosure dome, hutch, shelf, camera cradles | trimesh/pyvista/openseespy; reach from URDF; FEA | 🟡 Humans built a simpler $120 PVC cube. The "any orientation" cradle failed in use; "the unreachable area is 90 degrees off" |
| [I#42](https://github.com/vertical-cloud-lab/robot-arms/issues/42), [P#44](https://github.com/vertical-cloud-lab/robot-arms/pull/44) | Powder-doser auger-swap tooling | CadQuery; IK-posed PiPER; `fit_check.py`; Onshape | 🟡 Humans supplied the design intent each round: "unnecessarily tall"; "counter sinks need to be flat… twice as deep"; "compliant clip… NOT be locked with screw and nut" |
| [P#25](https://github.com/vertical-cloud-lab/robot-arms/pull/25) | J1 rest seat | URDF meshes + manifold3d | ⏸ The human sketch already had the key insight |
| [I#24](https://github.com/vertical-cloud-lab/robot-arms/issues/24), [P#40](https://github.com/vertical-cloud-lab/robot-arms/pull/40) | Fixed camera layout | `piper_twin.py` (matches the SDK to 0.1 mm); 5,151 camera pairs scored | 🟡 Cameras installed; the sim-vs-real comparison was never run |
| [I#54](https://github.com/vertical-cloud-lab/robot-arms/issues/54) | Motion with the mount fitted | Scripted runs | ✅ on run 4, after a J6 jam and "the camera screws scratched the J2 housing". The mount's checks never covered cables or self-collision through motion |
| [I#19](https://github.com/vertical-cloud-lab/robot-arms/issues/19)/[P#20](https://github.com/vertical-cloud-lab/robot-arms/pull/20), [I#59](https://github.com/vertical-cloud-lab/robot-arms/issues/59)/[P#60](https://github.com/vertical-cloud-lab/robot-arms/pull/60), [P#41](https://github.com/vertical-cloud-lab/robot-arms/pull/41) | Pick-and-place; relay power; wrist power | Staged scripts; a fake arm (23/23 tests); datasheets | ✅ Simulate, then run gated on hardware. The agent caught a human's part-number mix-up |
| [P#8](https://github.com/vertical-cloud-lab/robot-arms/pull/8) | `lab-models/`: ~60 labware STEPs plus equipment | CadQuery with four provenance tiers and per-dimension `sources/*.json` | ❔ The provenance tiers are the right idea; never reviewed |
| [I#21](https://github.com/vertical-cloud-lab/robot-arms/issues/21), [P#23](https://github.com/vertical-cloud-lab/robot-arms/pull/23), [I#5](https://github.com/vertical-cloud-lab/robot-arms/issues/5) | Reliability protocol; SOP; MoveIt primer | Docs | Docs only. MoveIt/MuJoCo never adopted, so collision checking is ad hoc per script |

### 3.4 digital-alloy-lab (DAL)

There is no CAD on `main`; about 12 PRs are open.

| Link | What | Approach | Outcome → lesson |
| --- | --- | --- | --- |
| [I#158](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/158), [P#200](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/200), [P#174](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/174) | Transducer cable holder; SEM stub holder | Human Onshape design; the agent exported, rebuilt (within 0.002 mm), sliced and printed | ✅ "No sliding at all". Human designs, agent fabricates |
| [I#152](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152), [P#172](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/172), [P#179](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/179) | Atomizer charge cup and plug | build123d, von Mises `fit_check`, Edison review, lathe | ✅ used in runs. Humans fixed the jargon and the animation physics ("unphysical intersection in the lid gif") |
| [I#231](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/231), [P#232](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/232) | Containment parts | CadQuery | ❌ Wrong printer target. The correction ("I meant the bambu A1 mini") arrived mid-run, where the running session couldn't see it |
| [P#173](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/173), [I#147](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/147), [P#189](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/189) | rePowder model; viewport camera mounts | CadQuery from video frames + `collide.py`; parametric Onshape with a "measure these" variable tab | 🟡 Three rePowder models disagree (sight glass off by 65 mm). "please be much better at describing what you want me to measure and even label them on an image" |
| [I#236](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/236) | Dummy P20 pipette (from byu-vcl I#169) | OpenSCAD from estimates | ❌ A human's measured Onshape model is the one in use |
| [I#222](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/222), [P#240](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/240), [P#241](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/241), [P#216](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/216) | Mini doser, 50-cup filler, figure | CadQuery on vendor STEPs | ❔ "Nothing has been built or tested"; three CubXL dimensions are guesses |
| [I#164](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/164) | Ultrasonic plate position | Tolerance analysis vs a human jig | ✅ The simple physical jig won |

### 3.5 tensegrity-optimization

This is the most mature loop: OpenSCAD → STL → Bambu CLI `.3mf` → GUI fix-ups → H2D print → weigh, photograph, drop test → BO. It took about 3 months and roughly 180 comments on one PR to get there.

| Link | What | Approach | Outcome → lesson |
| --- | --- | --- | --- |
| [P#35](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/35) | T3 prism: struts, TPU cables, vertex shells, plates | OpenSCAD + `render_print.sh`; admesh, iso PNGs, slice stats | ✅ eventually. Errors appeared only at import or print: single-material `.3mf`; "holes on a lot of the vertices. I.e., you violated the following" |
| P#35 (accelerometer pocket) | 6×6×5.94 mm sensor seat | Agent-sized variants A0–A3 | ✅ after a human edit to 6.2 × 6.2 × 6.8. The agent's slack let the sensor fall out, and 6.000 mm "was too tight" |
| [P#22](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/22), [P#39](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/39) | Reference structures; joint designs | Python generators, form-finding; OpenSCAD with iso views + cuts in 3 planes | 🟡 Iso renders hid non-physical geometry and the cross-sections exposed it ("B dovetail and the D eyelet"). The "simplified" generators had quietly stopped being tensegrities |
| [P#52](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/52), [P#64](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/64), [P#66](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/66) | DOE plate; multi-material slicing; baked-in supports | OpenSCAD; Bambu CLI; trimesh ray-cast pillars + FEA | ❌/🟡 "there's no 3rd nozzle in the H2D"; "why are you using PrusaSlicer"; "supports weren't touching… so the print failed". Production still uses hand-painted supports |
| [I#95](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/95) | Parametric B-rep | Onshape FeatureScript via API; build123d → STEP | 🟡 Not adopted: "I thought it would have an actual feature tree… sketches, extrudes"; a paper-thin roof |
| [P#102](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/102), [I#98](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/98) | BO rounds 2–6 | OpenSCAD plates; as-printed mass model; slicer settings read back from `.3mf` | ✅ Constant solid mass is not constant printed mass (18.5–22.3 g) |
| [P#33](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/33) | Drop simulation, six engines | MuJoCo, PyBullet, … | 🟡 Early runs were non-physical ("goes beneath the 'floor'"). Render every simulation |

### 3.6 custom-induction-furnace and caliber

| Link | What | Approach | Outcome → lesson |
| --- | --- | --- | --- |
| [furnace P#3](https://github.com/vertical-cloud-lab/custom-induction-furnace/pull/3), [P#12](https://github.com/vertical-cloud-lab/custom-induction-furnace/pull/12) | System schematic, BOM, crucible figures for a paper | Scripted native PPTX; matplotlib from the operator's annotated photos | 🟡 About 8 correction rounds on physical layout ("no support stand… It is all connected by KF40 flanges"; "the coolant is ethylene glycol"); an invented BOM total. The fix was a dated facts ledger, [AGENTS.md "Physical-configuration facts"](https://github.com/vertical-cloud-lab/custom-induction-furnace/blob/8a2ea31/AGENTS.md#L328) |
| [caliber P#17](https://github.com/vertical-cloud-lab/caliber/pull/17), [P#6](https://github.com/vertical-cloud-lab/caliber/pull/6#issuecomment-5721157704) | SEM stub tray | CadQuery → STL/STEP/PNG | ⏸ Built before the need was confirmed: "Do we even need to have them stuck into a base?" |
| [caliber P#24](https://github.com/vertical-cloud-lab/caliber/pull/24) | EDS design space | Ax Sobol + BO | 🟡 Bounds must come from instrument limits |

### 3.7 CADSmith, PCBSchemaGen and LaMAGIC forks; digital-wetlab

- **[CADSmith](https://github.com/vertical-cloud-lab/CADSmith)** (the upstream README cites [arXiv 2603.26512](https://arxiv.org/abs/2603.26512)) is our closest Frontier3D-like loop.
  - Pipeline: planner → CadQuery coder → OCCT executor → validator + vision-model judge → refiner.
  - **Only two checks can fail a part:** it must be a valid watertight solid, and the judge must pass it.
  - Volume, bounding box and face counts are given to the judge as information only.
  - It **fails open**: if the judge call throws, the check is marked passed ([`validator.py`](https://github.com/vertical-cloud-lab/CADSmith/blob/d9620aa/autofab/validator.py)).
- **Our CADSmith runs:**
  - [P#2](https://github.com/vertical-cloud-lab/CADSmith/pull/2): the powder-doser chassis passed the judge. An Edison review then found 6 P0 bugs: an auger-coupler gap, heat-set holes that "drill into air", a pocket rotated 90°, and others. The helical auger failed after 6 iterations.
  - [P#6](https://github.com/vertical-cloud-lab/CADSmith/pull/6): 12/12 valid solids and 11/12 judge passes, at 70 calls and 363k/95k tokens. The spec demanded 0 mm³ interference at 0/45/90°, but the runner contains no intersection code.
  - Our runs used the same model for coder and judge, unlike upstream's Sonnet-coder/Opus-judge split.
  - [P#4](https://github.com/vertical-cloud-lab/CADSmith/pull/4): a hinge hole 20 mm off was "invisible in a rendered three-view thumbnail". The agent's own write-up calls automated kernel checks of named features "the single biggest leverage point".
- **[PCBSchemaGen P#4](https://github.com/vertical-cloud-lab/PCBSchemaGen/pull/4):** ERC-clean, but part numbers and URLs were invented until checked against vendor files. The prompt already held the net list, so this tested transcription, not design.
- **[LaMAGIC P#2](https://github.com/vertical-cloud-lab/LaMAGIC/pull/2):** "Skip gracefully is another way of saying you were too lazy to figure it out". Selection by simulation helped, but the simulations ran at the repo's default operating point, not ours.
- **digital-wetlab:**
  - [P#8](https://github.com/vertical-cloud-lab/digital-wetlab/pull/8): the protocol's digital deck drifted from the physical deck.
  - [P#84](https://github.com/vertical-cloud-lab/digital-wetlab/pull/84): a vial holder with "Nobody has calipered the vials yet". `opentrons_simulate` served as a deck-conflict check.
- **No CAD content:** vclv, structural-alloy-sdl-workshop, streamingLambda and `.github`. `.github` has no org-wide agent instructions.

### 3.8 Cross-repo pattern

- **Where parts succeeded:**
  - Someone designed or measured the geometry: a human in Onshape or Fusion, a vendor STEP or vector drawing, or a proven open design.
  - The agent did the fabrication engineering: rebuilding and diffing, FEA on the as-sliced part, slicing, printing, keeping evidence.
  - Or it iterated against physical prints judged by a person.
- **Where parts failed:**
  - The agent supplied geometry it hadn't measured (proxies, estimates from photos or the web), and checked the model only against itself.
  - It reasoned about assemblies spatially and got them wrong: disconnected bodies, orientations 90° off, nothing touching.
  - It added or dropped requirements over a long thread.

### 3.9 Check code we already have (mostly unmerged)

| Check | Where |
| --- | --- |
| Pairwise interference, often across poses | robot-arms [`piper_mount.py`](https://github.com/vertical-cloud-lab/robot-arms/blob/1b7acd5/piper-camera-mount/cad/piper_mount.py) (exits non-zero), [`fit_check.py`](https://github.com/vertical-cloud-lab/robot-arms/blob/097006f/end-effectors/auger-swap/fit_check.py); powder-doser [`check_interference.py`](https://github.com/vertical-cloud-lab/powder-doser/blob/353dae7/cad/chain-carousel-v2/check_interference.py), [`digital_twin.py`](https://github.com/vertical-cloud-lab/powder-doser/blob/97521d2/cad/mounting-plate-assembly/digital_twin.py); byu-vcl [`interference.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/fbc6614/vertical-lab/interference.py) |
| Collision through animation and motion | byu-vcl [`collide.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/fbc6614/vertical-lab/collide.py), [`passive_shadow.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/ddd7853/cubos/tools/passive_shadow.py) (on main) |
| Registration to reference images | byu-vcl [`register.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/fbc6614/vertical-lab/register.py) |
| Fit on the as-sliced toolpath | byu-vcl [`fit_sim.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/49677cf/ot2-overhead-camera/lid-mount/slice/fit_sim.py), [`key_fit.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/4d5446c/hardware/vial-stirrer-cubxl/analysis/key_fit.py); robot-arms [`sliced_fea.py`](https://github.com/vertical-cloud-lab/robot-arms/blob/1b7acd5/piper-camera-mount/sim/sliced_fea.py) |
| Cross-tool equivalence (volume, IoU, symmetric difference) | DAL/byu-vcl [`compare_to_onshape.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/bc25668/atomizer-cable-holder/rebuild/compare_to_onshape.py); powder-doser [`compare_step.py`](https://github.com/vertical-cloud-lab/powder-doser/blob/68f71a2/cad/fsgen/compare_step.py); byu-vcl [`features.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/c7aa2ca/pi5-dual-camera-mount/onshape/features.py) |
| DFM and printability | powder-doser [`cad/dfm.py`](https://github.com/vertical-cloud-lab/powder-doser/blob/a22cf5f/cad/dfm.py) (on main), [text-to-cad check suite](https://github.com/vertical-cloud-lab/powder-doser/blob/61717c7/cad/text-to-cad/checks/README.md), [`check_stl.py`](https://github.com/vertical-cloud-lab/powder-doser/blob/57c30d0/docs/prints/2026-11-03-baseplate-h2d/check_stl.py) (bed fit) |
| Fastener matching against vendor STEPs | powder-doser [`fastener_check.py`](https://github.com/vertical-cloud-lab/powder-doser/blob/7f5b3b7/cad/full-assembly/fastener_check.py) |
| Dimension provenance | robot-arms [`lab-models/`](https://github.com/vertical-cloud-lab/robot-arms/blob/bdb25d3/lab-models/README.md) (four tiers, verbatim source quotes); DAL [`HOW-TO-MEASURE.md`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/c4827e9/atomizer-viewport-cameras/measure/guide/HOW-TO-MEASURE.md); byu-vcl P#296's Variable Studio |
| Reference-based scoring (Chamfer, F1, IoU) | CADSmith `metrics.py` |

---

## 4. Failure modes → what Frontier3D does → what we could do

| # | What keeps going wrong (examples) | Frontier3D's mechanism | Suggested practice for us |
| --- | --- | --- | --- |
| 1 | **Mating geometry guessed.** robot-arms P#10 (HQ housing, CM3 hole, set screw); byu-vcl P#60, P#84, I#169; DAL I#236; powder-doser P#57/P#66; tensegrity pocket | Ground truth is held by the organizer. Roles are matched "by measured geometry, never by object names". Unchecked clauses are listed (`unverified_requirements`, `pending_numeric_requirements`) | Every mating dimension is a named variable with a provenance tier: vendor STEP or vector drawing > caliper > datasheet > photo estimate. Anything still at "estimate" is a pending requirement: the part is not print-ready, and at most a fit coupon goes out |
| 2 | **Checks pass, part fails.** robot-arms P#10; CADSmith P#2 (6 P0s after a judge pass); powder-doser P#35 (after 2 judge rounds); tensegrity P#35 | A map from each requirement to its checks with `complete / partial / missing` status; "a passed system gate does not establish semantic task quality" | Keep a requirements file per design. Every PR reports coverage, e.g. "17/23 clauses machine-checked, 4 visual-only, 2 unchecked", so "all checks pass" can't be read as "meets spec" |
| 3 | **Physically impossible geometry or motion.** byu-vcl P#255, P#318; powder-doser P#2, P#35; tensegrity P#39, P#33 | Closed, connected, valid solid, no self-intersection; BVH interpenetration with intended contacts excluded by role; floating distance; static support; route connectivity | One shared check library, run on every CAD PR: one solid per printed part, a pairwise interference matrix with an allow-list of intended contacts, minimum clearance, support and contact |
| 4 | **Only one pose checked; cables, set screws and adjustable parts ignored.** robot-arms I#54, P#10; byu-vcl P#269 | Image2Code_008: poses keyed to frames, checked against invariants (axis distance, monotonic opening, return to closed, rigidity, attachment). L3 scores interaction separately | State motion ranges in the spec (their 011 omits them) and check clearance across the whole range. Model cables and adjustable parts as swept envelopes |
| 5 | **Weak self-review.** Same model as coder and judge (CADSmith P#2/P#6); fixed three-view renders miss misalignment (CADSmith P#4); the judge fails open | Blind judge with a frozen checklist; author and previous scores withheld; it lists features, the largest discrepancy and severity; code turns issues into scores; first valid judgment kept; technical failures block the score | Use a judge from a different model family. It lists issues by severity against the frozen checklist, sees exploded and section views (011 requires an exploded state), and fails closed. No re-asking until it passes |
| 6 | **Revisions break other features.** powder-doser P#49 ("The archimedes screw is gone", threads backwards); robot-arms P#10 ("Don't change anything else") | SceneEdit scores the requested change and the preservation of everything else | Every revision reports a geometric diff: volume or symmetric difference outside the edited region should be about 0, as byu-vcl I#151 already did by hand |
| 7 | **Requirements drift or get invented in long threads.** P20 vs P300; "Why in the world does the doser have a load cell?"; "80mm above the cup rim is a made up design requirement"; a funnel that defeats the no-cross-contamination goal | A frozen, hash-bound instruction; "hard thresholds only for relations mentioned in the brief" | Keep the spec in the repo and add each human correction as a dated clause, like the furnace facts ledger. Requirements the agent adds are marked as proposals |
| 8 | **Delivery breaks.** Single-material `.3mf`; faceted STEP; a stale export; a share link with export disabled; STEP bodies printed as separate parts; work never pushed; three disagreeing rePowder models | An exact output tree; a clean-room rebuild from source; seeds; native and GLB variants; a failed delivery gate scores 0 | A CAD delivery contract: source, spec, checks and outputs (STEP, STL, 3MF, views). CI rebuilds from source and diffs the outputs; checks STEP is analytic B-rep and one solid; checks 3MF body and material counts and bed fit. Validated designs merge to `main` as the source of truth |
| 9 | **Wrong assumptions about the environment.** PrusaSlicer for an H2D; a third nozzle; a 0.4 mm slice on a 0.6 mm nozzle; 16 mm vs 6 mm lens | Every task states the runtime, units, axes, render settings and allowed materials | One lab environment file that agents read first: printers, nozzles, materials, slicer quirks, fasteners and inserts in stock, measured tolerances |
| 10 | **Fits guessed, no calibrated tolerances.** byu-vcl P#234 rings; P#269 ("0.05mm is the best fit"); tensegrity 6.000 mm "too tight"; byu-vcl P#277 press fit | Worst case over variants (minimum of 8) | A tolerance library built from fit ladders, per printer, nozzle and material. Evaluate fits at the corners of the tolerance band and keep the worst |
| 11 | **Claimed runs that didn't happen; silent tool swaps.** powder-doser P#55/P#57/P#112; a model substitution in CADSmith P#6; "skip gracefully" | Every run is bound to its provenance; a missing measurement is neither zero nor a pass | Record tool, model, version and log for every attempt. Report "not run" as not run |
| 12 | **Cost and latency invisible.** CADSmith P#6: 70 calls; zoo 14–16 min and $6.89 a call; `@claude-print` mostly waiting | Efficiency is recorded, but kept separate from quality | Log tokens, minutes and dollars per design attempt alongside its check results |

---

## 5. Where Frontier3D does not help

- **No engineering geometry.** It uses meshes, not B-rep. Text2Code_011 even says "Do not add threads, fillets or hidden machinery". It has nothing on tolerances, printability, load, cables or fit against a real part. Our hardest failures (rows 1, 4 and 10 above) are outside its scope, so we have to build those checks ourselves.
- **Its numbers measure blind generation.** Candidates never see a render or a measurement. An agent with previews and kernel measurements, which is what we run, isn't measured by it at all.
- **Its specs are AI drafts and its text tasks are unvalidated.** The specs carry `ai_draft_pending_human_calibration`, and human agreement was measured only on the image families. The judge also comes from the same family as the two top-scoring models.
- **It forbids retrieval; we should prefer it.** Frontier3D bans downloading matching geometry because it measures capability. In our records, reused vendor or open geometry (the capper, the vial rack, OpenRAMAN, switching to a P300, the gripper STEP) is the most reliable path. Reuse with provenance should be the default.
- **It has no physical oracle.** Printing and measuring are our ground truth. A fit coupon or a caliper reading is worth more than any rubric score.

---

## 6. Suggested next steps

These are suggestions for discussion; none of them is implemented here.

1. **Merge one shared CAD check library and gate on it.** Gather the scripts in §3.9 into one package, with a CI job on PRs that touch CAD:
   - rebuild from source;
   - one valid solid per printed part;
   - interference matrix with an allow-list;
   - clearance across motion ranges;
   - bed fit and 3MF body count;
   - a preservation diff against the previous revision.

   It should report coverage, not just pass/fail.
2. **Give each design a requirements file.** Clauses, a source tier for every mating dimension, `pending` for anything unmeasured, and a dated corrections ledger. This also fixes context loss across `@claude` sessions.
3. **Use a blind judge from another model family.** It sees standard, exploded and section views plus a photo of the real mating part when one exists. It lists issues by severity against the frozen checklist and fails closed.
4. **Build a tolerance library from fit ladders,** per printer (H2D, A1 mini), nozzle (0.2/0.4 mm) and material. Evaluate designs at the worst corner of the tolerance band.
5. **Start a small benchmark, about 10 tasks, toward #325's 30.** Use Frontier3D's layout: a public brief, a private harness, and the physically validated solution. The human corrections become the test atoms. Candidate tasks:
   - OT-2 lid camera mount (byu-vcl P#234)
   - vial stirrer (P#269)
   - atomizer cable holder (P#257 / DAL I#158)
   - charge cup press fit (P#232)
   - tap collar and mount plate (powder-doser P#51)
   - geared auger (P#49)
   - PiPER wrist mount (robot-arms P#10, whose three misfits become three atoms)
   - tensegrity accelerometer pocket (P#35)
   - 384-well plate (byu-vcl I#5)
   - one assembly-level task from powder-doser `SPEC.md` or CADSmith P#6
   - one layout task: the robot-arms camera placement or the CubXL doser module

   Then score Claude Code + checks, CADSmith, zoo and text-to-cad on it. That supplies the rubric the powder-doser bake-off never had.
6. **Add a short CAD section to each repo's CLAUDE.md, or to an org-wide file.** Only powder-doser has any CAD rule today (a one-liner), and `.github` has no org-wide agent instructions. Contents: the source hierarchy, "measure, don't guess", one solid per printed part, the delivery contract, default clearances from the tolerance library, and "never claim a run that didn't happen".

---

## Method

- Frontier3D was cloned read-only and none of its code was run. I read its docs, task packages, harness code and paper.
- Our repos were covered by six parallel readers, one per repo group, plus one for Frontier3D's code. They used `gh` listings, full comment threads and shallow clones, and inspected unmerged branches where those looked relevant. They spot-checked the quotes; I re-checked a sample of quotes and Frontier3D code claims myself before writing this.
- Rows marked † were read from a title or diffstat only.
- Counts such as "about 160 attempts" are counts of inventory rows. Rows group related issues and PRs, so they are approximate.

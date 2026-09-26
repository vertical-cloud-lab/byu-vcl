
# Experimental Protocol for a Physically Closed Generative End-Effector Design Loop

## 1. The Measurement, Done Properly

### 1.1 Dependent Variables

The central challenge is that "this finger is better" conflates finger geometry with arm pose error, perception, control, and print variability. Published gripper benchmarking uses several dependent variables, each with different attribution properties.

The Cross-Embodiment Gripper Benchmark (CEGB) operationalizes **binary grasp success** as: object lifted ≥50 mm within 3 s and held for 3 s without slip; per-object success is the mean across canonical poses; dataset-level performance uses both micro- and macro-averages with Wilson score confidence intervals (pqac-00000004). The Bekiroglu et al. benchmarking protocol for grasp planning adds a **robustness test** after lifting: a rotational perturbation followed by a 10-second sinusoidal shake, with failure modes explicitly catalogued (pqac-00000047). **Retention force** (pull-to-slip) is measured in NIST-derived protocols by increasing a tangential load on a rigidly fixtured gripper until first sustained slip; the result is F_ideal = max(F_pull), with slip resistance computed as μ_eff = F_slip/ΣN_i (pqac-00000000, pqac-00000006). **Grasp pullout strength** under static or quasistatic loading is recognized as a hand-level benchmark (pqac-00000001). **Volumetric grasping capacity** — the range of cylinder diameters stably grasped — serves as a proxy for capture envelope (pqac-00000001). **Cycle time** is recorded from commanded approach to fully open, but is dominated by arm speed and controller settings rather than finger geometry (pqac-00000000).

The following table ranks these metrics by their vulnerability to arm confounding and their suitability for this protocol:

| Metric | Operational Definition | Published Use (citations) | Confounded by Arm Pose? | Recommended for This Protocol |
|---|---|---|---|---|
| Binary grasp success | Success if the object is lifted ≥50 mm within 3 s and held for 3 s without slip or drop; report successes/attempts, with macro- and micro-averages and Wilson confidence intervals. | CEGB/YCB-style benchmark (pqac-00000004); related YCB protocol lifts 150 mm and holds for 3 s (pqac-00000005) | **High.** Approach collision, pose error, reachability, trajectory tracking, and finger geometry all affect the result. | **Primary integrated endpoint**, but only under paired designs, identical trajectories, randomized order, and explicit pose perturbations. Do not call this a finger-only measurement. |
| Retention force (pull-to-slip) | With the arm locked or gripper mounted to a rigid fixture, increase a calibrated tangential load at a preregistered rate until first sustained slip or release; record peak force, force at first slip, and failure mode. | Cross-embodiment/NIST-derived gripper benchmark defines ideal retention as the maximum applied tangential force before slip or the safety limit (pqac-00000000) | **Low off-arm; medium on-arm.** Arm compliance and controller reactions confound an on-arm pull. | **Primary finger-level endpoint.** Test axially and laterally, use ≥3 physical prints per design, and retain the full force–displacement curve. |
| Slip resistance, μeff | Measure total finger normal force ΣNi and tangential force at incipient slip Fslip; compute μeff = Fslip/ΣNi. For torque loading, report a holding-quality factor such as FslipL/Ta. | NIST-derived grasp-strength and slip-resistance procedures (pqac-00000006) | **Low in a rigid fixture.** Sensitive instead to contact material, surface state, normal-force calibration, and object geometry. | **Secondary mechanistic endpoint** when normal force can be measured credibly; otherwise report Fslip without claiming a friction coefficient. |
| Capture envelope | Estimate success probability over imposed lateral, axial, and angular offsets while holding trajectory and object fixture constant; summarize the 3-D success surface and ED50/ED90 offset thresholds from a logistic mixed model. | YCB gripper assessment uses controlled object offsets with fixed gripper position (pqac-00000043); hand benchmarks also use maximum/minimum stable cylinder diameter as volumetric capacity (pqac-00000001) | **Deliberately includes pose error.** It measures the finger’s tolerance to arm/object misregistration rather than nominal precision. | **Co-primary robustness endpoint.** Use symmetric offsets, randomized trials, and report axis-specific ED50/ED90 with bootstrap confidence intervals. |
| Grasp resilience (shake test) | After acquisition and lift, apply a fixed rotational perturbation followed by a preregistered 10 s sinusoidal shake; failure is slip beyond threshold, release, or drop. | Bekiroglu et al. include rotation and 10 s sinusoidal shaking after lifting (pqac-00000047); resilience under rapid disturbance is recognized as a hand benchmark (pqac-00000001) | **Medium.** Arm acceleration and trajectory tracking determine the applied disturbance. | **Secondary integrated endpoint.** Verify wrist acceleration with an IMU and use the identical measured disturbance trace for every design. |
| Pullout strength | Under static or quasistatic loading, pull an object from a closed grasp in a defined direction and record peak load, work to release, displacement at release, and failure mode. | Recognized hand benchmark for maintenance of grasp under increasing external load (pqac-00000001) | **Low off-arm; medium on-arm.** On-arm tests add structural compliance and controller behavior. | **Primary finger-level endpoint**, especially for vials, SEM stubs, coupons, and crucibles; distinguish axial extraction from tangential slip. |
| Cycle time | Time from commanded approach/start through acquisition, task completion, release, and return to fully open; separately report time-to-lift and time-to-release. | NIST-derived protocols define cycle time from commanded approach until fully open and report median and bootstrap intervals (pqac-00000000); CEGB records time-to-lift and release (pqac-00000004) | **Very high.** Dominated by arm speed limits, planner, communication, and controller settings. | **Secondary systems metric only.** Keep motion profiles identical; never use it alone to claim a better finger. |
| Seating success | Success if the grasped object reaches the preregistered final pose or insertion depth, remains there after release, and violates neither force nor damage limits; report depth/pose error and peak force in addition to pass/fail. | YCB block placement and peg insertion reveal sensitivity to grasp-pose uncertainty and 5–10 mm perturbations (pqac-00000026, pqac-00000030) | **Very high.** Arm accuracy, compliance, grasped-object pose, fixture tolerance, and finger geometry are inseparable without auxiliary measurements. | **Primary task endpoint for DSC lids, SBS plates, and vial placement**, but model it as a system-level outcome and instrument insertion force or final pose. |
| Cycle life | Repeatedly close/open between specified displacement or strain limits under controlled temperature/humidity until fracture, permanent set, stiffness/force loss beyond a preregistered threshold, or run-out; report cycles to each criterion and censored run-outs. | PLA/Tough-PLA–TPU 95A mechanisms were tested at 8–80% of yield stress, approximately 2 Hz, toward 100,000 cycles; several interfaces failed before run-out (pqac-00000007, pqac-00000009) | **Low off-arm; medium on-arm.** On-arm cycling adds variable stroke, alignment, heating, and control effects. | **Mandatory durability endpoint.** Use fixture-based strain-controlled tests, ≥5 specimens for screening and ≥10 finalist specimens, 100,000-cycle run-out, plus retained-force/stiffness checks at logarithmic intervals. |


*Table: Ranks operational gripper-performance endpoints by attribution strength and protocol value. It separates finger-level fixture measurements from integrated outcomes that remain confounded by arm pose and control.*

**Recommendation.** Use two co-primary finger-level endpoints measured off-arm (retention force, capture envelope via controlled perturbations) and two co-primary system-level endpoints measured on-arm (binary grasp success, seating/placement success). Never claim a finger-only improvement using only on-arm data.

### 1.2 Separating Finger from Arm Contribution

Published practice does not include a standardized protocol for isolating gripper geometry from arm effects. The Shilati et al. dexterity benchmarking review recommends supplementing system-level results with component-level and hand-level benchmarks, arguing that system-level outcomes "cannot automatically be attributed to the fingers" because many non-hand factors affect performance (pqac-00000041). Bekiroglu et al. control confounding by standardizing object placement, providing known object models and poses, and prescribing workspace geometry, but they do not impose a common controller or hand (pqac-00000045, pqac-00000046). The YCB gripper assessment uses fixed gripper position with controlled object offsets of 0 and 1 cm to test robustness (pqac-00000043).

**Concrete designs for this protocol:**

1. **Fixed-fixture retention testing.** Mount the finger set in a rigid off-arm fixture bolted to the bench. Apply calibrated tangential loads via a hanging mass or force-gauge pull at a preregistered rate. This eliminates arm compliance, controller reaction, and thermal drift entirely.

2. **Deliberately perturbed poses.** On-arm, test at nominal and at five preregistered offsets (±lateral, axial, ±angular). Fit a logistic model to success vs. offset to extract ED50/ED90 thresholds — the capture envelope. This *deliberately includes* arm pose error as a realistic nuisance, but the comparison is paired: every design sees the identical trajectory and offset grid.

3. **Paired designs on identical trajectories.** Lock the trajectory (waypoints, speeds, gripper timing) and swap only the finger set. Randomize the order of designs within each session and block on day to absorb thermal drift.

4. **Blocking on time-of-day.** The PiPER's thermal behavior is undocumented. Run a morning and afternoon block each day, randomize design assignment within each block, and include block as a random effect in the statistical model.

**What standard practice misses:** No published protocol performs arm-swap paired testing, time-of-day blocking, or variance decomposition between finger and arm contributions. These are novel contributions you would be making.

### 1.3 Statistical Design

**Power analysis for binary success at high baselines.** At a 90% baseline success rate, detecting a 5 percentage point improvement (to 95%) with 80% power and α = 0.05 (two-sided) requires approximately 435–475 trials per group using a two-proportion z-test or Fisher's exact test. At 95% baseline detecting a 3 pp improvement, the requirement exceeds 1,000 per group. The Q2 result — 118 operations for a one-sided 95% reliability claim at p ≥ 0.975 with zero failures — applies to single-design reliability demonstration, not between-design comparison.

**Paired/blocked structure.** With k = 5 AI designs + 1 human control, n = 6 object classes, and m = 3 physical prints per design, the experimental unit is the print-on-object combination. Use a logistic mixed-effects model: fixed effects for design, object, offset, fill state, printer, trial index, and interactions; random intercepts for physical print and object specimen. Report estimated marginal probabilities with simultaneous confidence intervals.

**Multiplicity correction.** Apply Holm correction to the family of k = 5 planned contrasts (each AI design vs. human control), separately for each primary endpoint. Across objects, use a preregistered primary analysis on the macro-average and secondary per-object analyses with an explicit second-level correction.

**Capture envelope reporting.** Fit a logistic mixed model with offset magnitude and axis as predictors. Report ED50 (offset at which success drops to 50%) and ED90 (offset at which success drops to 90% of nominal) per axis, with bootstrap 95% CIs. The CEGB reports Wilson score intervals for binomial proportions (pqac-00000004); extend this to the logistic model.

**Practical sample sizes.** For 5 designs vs. 1 control on 6 objects with 3 prints each: 30 nominal + 20 perturbed trials per print-object cell yields ~50 × 18 cells per design = 900 trials per design, 5,400 total for confirmatory testing. This gives adequate power for a 5 pp difference at a 90% baseline on the pooled-object macro-average.

### 1.4 Fatigue and Cycle Life for Printed Compliant Fingers

Published fatigue data for FDM flexures are sparse. The most relevant study (Juwita, 2019) tested dual-extrusion PLA–TPU 95A and Tough PLA–TPU 95A bi-material compliant mechanisms using an Instron ElectroPuls E10000 at approximately 2 Hz, with maximum stress at 80% of measured yield and minimum at 8% (pqac-00000007, pqac-00000008). The target was 100,000 cycles. PLA–TPU 95A mechanisms were more durable than Tough PLA–TPU 95A, but cylindrical and tapered interface designs fractured before reaching the 100,000-cycle target (pqac-00000009, pqac-00000010). The authors note that the selected test frequency may have been too high for viscoelastic materials, recommending a lower frequency to allow stress relaxation (pqac-00000009). Li et al. (2026) reported that PLA buttons survived 20,000 press cycles without functional failure (pqac-00000022).

**What is absent from the literature:** No published S-N curves exist for FDM-printed TPU-85A, PETG, or PA-CF at flexure-relevant strain amplitudes. No ASTM or ISO standard specifically addresses fatigue testing of FDM-printed compliant mechanisms. ASTM D7791 (tension-tension fatigue of plastics) and ISO 13003 (fiber-reinforced composites) can be adapted but do not account for layer-adhesion anisotropy or multi-material interfaces.

**Protocol for this study:** Use displacement-controlled cycling at a frequency ≤ 1 Hz to avoid viscoelastic heating. Define failure as fracture, ≥20% loss of closure force, ≥20% permanent set, or visible delamination. Define run-out at 100,000 cycles. Test ≥ 5 specimens per finalist design. Measure retained stiffness, closure force, retention force, and permanent set at logarithmic intervals (1k, 10k, 50k, 100k). This is necessarily a *new benchmark contribution*, as there is no existing data to design against for mechanical-interlock rigid+TPU joints.

### 1.5 Print-to-Print and Printer-to-Printer Variability

Published FDM dimensional accuracy data consistently report tolerances of approximately ±0.1–0.2 mm for PLA. Li et al. (2026) found mean dimensional error of 0.18 ± 0.07 mm across 42 PLA parts, all within ±0.5 mm, and recommend 0.1–0.2 mm clearance for mating interfaces (pqac-00000022). Alsoufi (2018) demonstrated that ±0.1 mm absolute tolerance is achievable with 0.1 mm layer height (pqac-00000024). No comprehensive print-to-print variance study with n ≥ 30 replicates of a single design was identified.

**Protocol:** Before the confirmatory study, run a variance-components pilot: print 5 copies of one reference finger on each printer (A1 mini, A1 mini with H2D), randomized across plate position and day. Measure critical dimensions (finger width, gap, flexure thickness), mass, closure force, stiffness, and retention force. Partition variance among printer, day, print, and measurement repeat. Use the result to determine the minimum replicate count; the expected result is n ≥ 3 prints per design.

---

## 2. The Generative Loop

### 2.1 Feedback Signal to the Generator

VLMgineer (Gao et al., 2026) provides the most relevant empirical data on feedback modality for VLM-driven tool design. In their evolutionary pipeline, candidates are evaluated via task-specific fitness functions returning scalar rewards. They explicitly tested adding execution images as feedback to the next evolutionary query, but this *reduced* average reward by 5.4%; they attribute this to VLMs' difficulty in accurately grounding raw visual observations (pqac-00000015). Video and object-centric feedback signals also performed worse than scalar task reward (pqac-00000014, pqac-00000040).

**Ranking of feedback signals for this protocol, by information content and practicality:**

1. **Structured scalar reward** (grasp success rate + normalized retention force + normalized capture-envelope area): highest practicality, empirically best in VLMgineer. Pair with a structured failure-mode label from a preregistered taxonomy.
2. **Force–displacement curves** from fixture testing: high information content (reveals partial contact, premature slip, compliance mismatch), but requires parsing into scalar features for LLM consumption. Recommend extracting: peak force, stiffness, energy-to-slip, and failure mode, then returning these as a structured dictionary.
3. **Failure-mode labels** (no contact, partial contact, premature slip, object damage, deformation failure): categorical, low-dimensional, interpretable by the LLM.
4. **VLM reading of failure video**: tempting but empirically counterproductive per VLMgineer's finding. Reserve for human review but do not feed into the automated loop.
5. **Human code-level edits**: Sadik & Bujny (2025) found that code-level human edits achieve zero Hausdorff distance vs. image-only correction for *geometric* similarity. No analogous result exists for *functional* feedback — this is a gap. In this protocol, human code-level edits would be a separate ablation condition (human-in-the-loop vs. autonomous).
6. **Balance/force feedback as the reward signal**: No published use of balance/weighing as a reward signal in a design optimization loop was identified; balance feedback appears only in control loops. Your HR-100A balance with closed-loop logging would be novel as a design-loop reward signal, measuring mass-transfer accuracy as a continuous outcome.

### 2.2 Physical Iteration Budget

Standard Bayesian optimization performs well for low-dimensional problems (< 15–20 parameters) and degrades above that (pqac-00000023). For a budget of 30–60 physical evaluations:

- **Phase 1 (Exploration, ~10 designs):** Use CADSmith to generate a diverse initial population spanning the design space. Evaluate each on 1–2 primary objects with abbreviated grasp trials (10 per object).
- **Phase 2 (Exploitation, ~20–30 designs):** Use multi-fidelity BO with simulation (CadQuery + FEA for interference/stress checks) as the cheap tier and physical testing as the expensive tier. Batch-parallel evaluation of 3–5 candidates per iteration. GP with anisotropic kernels or Random Forest surrogates are recommended (Liang et al., 2021).
- **Phase 3 (Confirmation, ~5–10 designs):** Freeze the top 5 candidates and the human control. Full confirmatory testing with 3 prints per design and the complete trial protocol.

The total of ~50 printed-and-tested designs is achievable at ~45 min print time + ~30 min test time per design, implying ~60 hours of robot+printer time for the optimization campaign.

### 2.3 Required Ablations

A referee will demand evidence that the headline claim ("an LLM designed a better gripper") is not attributable to a single component. Five ablations are required:

1. **No physical feedback (simulation only):** Run the full CADSmith pipeline with simulation evaluation only, no fabrication or physical testing during optimization.
2. **No VLM judge:** Remove the three-view VLM judge from CADSmith; rely only on kernel validation.
3. **No kernel/manifold checks:** Remove OpenCASCADE exact validation; allow the LLM to generate any geometry.
4. **No parametric priors:** Remove any object-specific dimensional hints from the prompt.
5. **No simulation pre-screen:** Send every generated design directly to fabrication without FEA or interference checks.

Each ablation receives the same generation calls, candidate budget, fabrication allowance, and stopping rule. The minimum set supporting the headline claim is: the full pipeline must outperform every ablation on the primary endpoint.

### 2.4 The Human-Expert Control Arm

Si et al. (2026) provide the strongest methodological precedent for human-vs-AI design comparisons. They recruited 43 qualified expert researchers, randomly assigned ideas from human and AI conditions, required >100 hours of execution per participant, and evaluated outcomes through blinded expert review with FDR-corrected statistical tests (pqac-00000034, pqac-00000035). A central finding was that AI-generated ideas declined significantly more than human ideas from ideation to execution, underscoring the importance of execution-based evaluation over ideation-stage judgment (pqac-00000036).

**Fair control design when the expert is a student in the same lab:**
- Give the expert the **identical frozen specification**: object dimensions/CAD, material constraints, actuator interface geometry, safety limits, print-time budget, and the same number of pilot prints as the AI pipeline receives physical evaluations.
- Allow ordinary CAD tools, simulation, and online resources. Record all design rationale, time logs, and rejected concepts.
- **Time budget:** Match total person-hours to the AI pipeline's wall-clock time, or if the AI runs overnight, match to the researcher's available working hours during the same period.
- **Blinding:** Assign anonymous design codes. Test operators and data analysts should not know which design is AI-generated and which is human-designed.
- Freeze the submitted CAD before any confirmatory testing begins.

### 2.5 Pre-Registration and Reporting

No established precedent exists for pre-registering a hardware-design comparison. However:
- **OSF or AsPredicted** can host the pre-registration. Register: hypotheses, endpoints, exclusion criteria, stopping rules, offset grid, randomization schedule, model formula, planned contrasts, multiplicity family, missing-data handling, and success/failure thresholds.
- **CONSORT-adapted checklist:** Adapt CONSORT items (randomization, blinding, sample size justification, primary/secondary outcomes, complete case analysis) for hardware. The RB2 benchmark demonstrates cross-lab protocol pooling as a model (pqac-00000029).
- **HardwareX requirements** (bill of materials, build instructions, validation data) apply to the reporting, not the pre-registration.
- **ASME/RA-L expectations:** Repeated trials with statistical analysis, clear failure-mode documentation, and reproducible hardware descriptions.

Archive CadQuery source, STEP/STL files, slicer projects, G-code hashes, LLM prompts, model API call logs, raw balance and force logs, videos, failure labels, and analysis code.

---

## 3. Reusing What You Have

### 3.1 Mechanical Interlock Joints in Compliant Grippers

The compliant-gripper literature overwhelmingly relies on **interfacial adhesion** between rigid and flexible phases in multi-material FDM prints, not mechanical interlock. Juwita (2019) tested PLA–TPU 95A and Tough PLA–TPU 95A with cylindrical and tapered interfaces, but these are adhesion-dependent geometries, not captive mechanical interlocks (pqac-00000009, pqac-00000011). De Dominicis (2023) studied PLA–TPU interface strength for prosthetic applications but again used interfacial adhesion. Your printed-in-place rigid + TPU-85A mechanical-interlock joints (pull-through ratio 1.71× anchor-bulb, 2.5× captive core) appear to have **no direct precedent** in the compliant-gripper literature. This is a novel contribution that should be explicitly tested and reported.

### 3.2 Balance/Force Feedback as Reward Signal

No published use of a balance or weighing instrument as the **reward signal in a design optimization loop** was identified. Balance feedback appears in robotic control loops (e.g., force-controlled grasping) but not in closed-loop design generation. Using the HR-100A balance with closed-loop logging to measure mass-transfer accuracy (e.g., did the gripper successfully transfer the correct mass of powder?) as a continuous design reward would be novel. This is worth pursuing as a differentiated contribution.

### 3.3 Benchmark Object Sets

The **YCB Object and Model Set** (Calli et al., 2015) is the most widely used benchmark, with 77 consumer objects, high-resolution RGBD scans, and geometric models. Its documented limitations include: cost (~$350), portability constraints (airline suitcase), exclusion of fragile/perishable items, and — critically — absence of laboratory-specific objects such as SEM stubs, vials, well plates, or crucibles (pqac-00000031, pqac-00000033). The set also requires task-specific protocols for meaningful comparison; objects alone are insufficient (pqac-00000033).

**Peg-in-hole benchmarks** are extremely sensitive to positioning error: YCB peg-insertion success dropped from 10/10 at nominal to 4/10 with 5 mm perturbation and 0/10 with 10 mm perturbation (pqac-00000026, pqac-00000030). Peg-in-Bench offers reconfigurability but remains limited to predefined insertion geometries (pqac-00000029).

**No published lab-object benchmark exists.** Labimus (Wu et al., 2026) simulates chemical laboratory manipulation tasks but is simulation-only. Your lab-object set (SEM stubs, vials, well plates, DSC crucibles, tensile coupons, powder scoops) would be the first physical laboratory-manipulation object set — another contribution.

---

## 4. Deliverable: The Protocol

The following table specifies the complete pre-registerable experimental design:

| Component | Specification | Rationale/Source |
|---|---|---|
| Objects tested | Six laboratory-object classes: SEM stubs; empty and filled vials; SBS well plates; aluminium DSC crucibles and press-fit lids; printed tensile coupons; and standardized powder-scoop tasks using cohesive AlSi10Mg and Si powders. Record dimensions, mass, fill state, surface condition, lot, and canonical pose for every specimen. | YCB demonstrates the value of fixed objects and poses but is dominated by consumer objects and requires task-specific protocols; laboratory-object coverage is absent (pqac-00000031, pqac-00000033). |
| Compared designs | Five frozen AI-generated finalist designs plus one human-expert control. Select finalists using a preregistered algorithm before confirmatory testing; prohibit outcome-informed substitution. | Multiple retained candidates reduce dependence on a lucky generation seed. Evolutionary design literature supports population-based selection using task reward (pqac-00000014, pqac-00000017). |
| Replicate prints | Three independently printed finger sets per design for confirmatory manipulation and retention tests. Randomize build-plate position and printing order, and distribute each design across both printer models where manufacturable. Record print, printer, material lot, and build date. | FDM accuracy depends on nozzle, layer height, and process settings; published PLA work uses approximately 0.1–0.2 mm mating allowances, so one print cannot represent a design (pqac-00000022, pqac-00000024, pqac-00000025). |
| Grasp trials | Per print–object combination: 30 nominal-pose attempts plus 20 attempts at each of five preregistered offset conditions. Suggested conditions are positive lateral, negative lateral, axial, positive angular, and negative angular offsets. Fix magnitudes after pilot calibration but before freezing the confirmatory protocol. | Published benchmarks use repeated prescribed object poses and controlled offsets. Binary success should require a defined lift and hold rather than subjective judgment (pqac-00000004, pqac-00000043, pqac-00000046). |
| Fixture retention test | Mount each finger set in a rigid off-arm fixture. For each of three prints, perform five pulls per object and direction at a fixed displacement rate; measure first sustained slip, peak force, work to release, and failure mode. Randomize pull direction and specimen order. | NIST-derived testing increases tangential load until slip and defines retention using maximum pull force; fixture testing minimizes arm and controller confounding (pqac-00000000, pqac-00000006). |
| Cycle-life test | Test five independently printed specimens per finalist and control using displacement- or strain-controlled cycling to a 100,000-cycle run-out. Measure retained stiffness, closure force, permanent set, visible damage, and retention performance at baseline, 1,000, 10,000, 50,000, and 100,000 cycles. | Published PLA/Tough-PLA–TPU mechanisms used 8–80% of yield stress, approximately 2 Hz, and a 100,000-cycle target, but several interfaces failed before run-out; exact gripper-relevant fatigue data remain sparse (pqac-00000007, pqac-00000009, pqac-00000011). |
| Statistical model | Fit a logistic mixed-effects model for grasp success with fixed effects for design, object, offset axis and magnitude, fill state, printer, trial index, and relevant interactions; include random intercepts for physical print and object specimen. Report estimated marginal probabilities and simultaneous 95% intervals. Apply Holm correction to planned AI-versus-control contrasts across designs and objects. | Binary benchmark outcomes are conventionally reported as success proportions with Wilson intervals, but repeated trials on the same prints require hierarchical rather than independent-binomial analysis (pqac-00000004, pqac-00000047). |
| Capture-envelope analysis | Model signed lateral, axial, and angular offsets directly, including preregistered nonlinear terms or splines. Report axis-specific ED50 and ED90 thresholds, bootstrap 95% confidence intervals, and integrated success volume over the tested offset domain. | Controlled perturbations expose robustness that nominal success misses; peg-insertion results show that 5 mm errors can sharply reduce success and 10 mm errors can eliminate it (pqac-00000026, pqac-00000030). |
| Primary success criterion | The prespecified selected AI design must exceed the human control’s object-macro-averaged grasp-success probability by more than 5 percentage points, with the multiplicity-adjusted lower 95% confidence bound above zero. It must also be non-inferior in median retention force using a preregistered 10% margin and have no catastrophic failure before 100,000 cycles in at least four of five fatigue specimens. | Requiring statistical superiority plus retention and durability guards prevents a fragile design from winning through nominal grasp success alone. |
| Required ablations | Five matched ablations: no physical feedback; no VLM judge; no exact-kernel or manifold checks; no parametric priors; and no simulation prescreen. Give each the same generation calls, candidate budget, fabrication allowance, and stopping rule as the full pipeline. | Scalar task reward is the strongest documented feedback in VLM-guided tool evolution; adding final images reduced average reward by 5.4%, making feedback modality an essential ablation (pqac-00000015, pqac-00000020). |
| Human-expert control | Give the expert the identical specification, object CAD or scans, materials, printer constraints, actuator interface, safety limits, and total person-hours. Permit ordinary CAD, simulation, pilot prints, and test data within the same fabrication budget. Freeze submitted CAD before confirmatory testing; assign anonymous design codes and blind operators and analysts where feasible. | A credible human–AI comparison uses qualified participants, controlled assignment, substantial execution effort, and blinded outcome review. Si et al. used 43 experts, approximately 100 hours per execution, and four to five expert reviews per project (pqac-00000034, pqac-00000035, pqac-00000036). |
| Total budget | Optimization campaign: 30–60 fabricated-and-tested candidate designs, with 50 as the target. The stated full confirmatory design equals 14,040 grasp attempts, not approximately 4,500. A 4,500-trial cap requires a preregistered incomplete-block subset, such as 25 nominal plus 25 perturbed trials per design–print–object cell for five primary object classes, with the sixth reserved for external validation. | Resolve the arithmetic before preregistration; otherwise the workload and power claims are inconsistent. Batch Bayesian optimization is appropriate for expensive, low-dimensional physical evaluation (pqac-00000023). |
| Preregistration and reporting | Register hypotheses, endpoints, exclusions, stopping rules, offset grid, randomization schedule, model formula, contrasts, multiplicity family, missing-data handling, and success thresholds on OSF or AsPredicted before confirmatory printing. Archive CadQuery source, STEP and STL files, slicer projects, G-code hashes, prompts, model settings, raw balance and force logs, videos, failure labels, and analysis code. | Hardware research lacks a widely adopted CONSORT-equivalent preregistration standard; a frozen and auditable protocol is therefore necessary to distinguish confirmatory evidence from iterative engineering. |


*Table: This table specifies the objects, controls, replication, endpoints, statistical analysis, ablations, durability testing, and reporting needed for a defensible AI-versus-human gripper comparison. It also identifies and resolves the inconsistency between the proposed full factorial design and a 4,500-trial budget.*

### Success and Failure Criteria

**Success:** The prespecified AI finalist exceeds the human control's object-macro-averaged grasp success by >5 pp (lower 95% CI > 0), is non-inferior in median retention force (within 10% margin), and survives ≥100,000 cycles in ≥4/5 fatigue specimens with <20% functional loss.

**Failure:** Any of: (a) no AI design exceeds the human control on the primary endpoint; (b) the winning AI design fails fatigue testing; (c) the winning AI design's advantage disappears when tested off-arm in the fixture; (d) print-to-print variance exceeds the design-to-design effect.

### Three Most Likely Referee Rejections

| Rejection Ground | Why It Is Likely | What to Measure Now |
|---|---|---|
| **Arm confounding: “You measured the arm, not the finger.”** | Integrated binary grasp success combines finger geometry with approach error, trajectory tracking, calibration, reachability, perception, and control. Published benchmarking guidance therefore distinguishes hand/component tests from system-level tests and uses known poses or controlled perturbations to reduce confounding (pqac-00000041, pqac-00000043, pqac-00000045, pqac-00000046). | Run rigid-fixture retention and axial/lateral pullout tests with force–displacement logging. Separately estimate capture envelopes using randomized, deliberately imposed lateral, axial, and angular pose errors while keeping the trajectory fixed. Show that the winning design improves both off-arm finger metrics and paired on-arm performance. |
| **Print variability: “One print is not a design.”** | FDM dimensions depend on nozzle, layer height, orientation, printer, material lot, and thermal history. Published practice allows roughly 0.1–0.2 mm extra clearance at mating interfaces, making a single artifact an inadequate experimental unit (pqac-00000022, pqac-00000024, pqac-00000025). | Print **at least three independent replicates per design** for the confirmatory comparison. First run a variance-components pilot with **five prints of one reference finger on each printer**, randomized across plate position and day; measure critical dimensions, mass, closure force, stiffness, and retention force, then partition variance among printer, day, print, and measurement repeat. |
| **Strawman human baseline: “The expert didn’t try.”** | An unmatched expert may receive less time, fewer pilot prints, poorer tools, or less feedback than the AI pipeline. Credible human–AI studies use qualified participants, substantial and documented execution effort, matched conditions, and blinded outcome review (pqac-00000034, pqac-00000035, pqac-00000036). | Give the expert the identical frozen specification, objects and CAD data, manufacturability constraints, safety limits, optimization time, simulation access, physical-test information, and print budget. Record person-hours, tool use, rejected concepts, design rationale, code/CAD history, and pilot outcomes; freeze the final design before anonymous confirmatory testing. |
| **Missing fatigue data: “How do you know it survives?”** | Published gripper-relevant fatigue evidence is sparse. PLA/Tough-PLA–TPU 95A mechanisms have been tested toward a 100,000-cycle target under 8–80% of measured yield stress, but several interfaces failed before run-out and detailed strain–life curves are absent (pqac-00000007, pqac-00000009, pqac-00000011, pqac-00000012). | Run a pilot on the mechanically interlocked rigid–TPU joint at a maximum load initially corresponding to **80% of measured specimen yield** and a minimum of 8%, targeting **100,000 cycles**. Because stress-controlled axial results do not automatically transfer to bending flexures, also measure local flexure strain, temperature, permanent set, stiffness, closure force, and retention at baseline, 1k, 10k, 50k, and 100k cycles; define fracture or ≥20% functional loss as failure and 100k as censored run-out. |


*Table: The principal threats to a defensible AI-designed-gripper claim are arm confounding, unmodeled print variability, an unfair human control, and unsupported durability. The table specifies measurements that should begin before the confirmatory study is frozen.*

### What Is Simply Absent from the Literature

1. **No S-N fatigue curves** for FDM TPU-85A, PETG, or PA-CF at flexure-relevant bending strains. You must generate your own data.
2. **No published lab-object manipulation benchmark.** The YCB set does not include laboratory consumables. You are creating a new benchmark.
3. **No precedent for balance-as-reward** in a design optimization loop. This is novel territory.
4. **No published physical closed-loop** from LLM → editable parametric CAD → FDM → physical test → LLM. VLMgineer closes simulation → URDF → print → real test but does not use editable parametric CAD or iterate on physical feedback (pqac-00000015). Fit2Form closes geometry → print → test but without editable parametric CAD. You would be the first to close this complete loop.
5. **No standardized arm-vs-finger attribution protocol.** Paired fixture testing with thermal-drift blocking would be a methodological contribution.
6. **No functional-feedback analog to Sadik & Bujny's code-edit result.** Whether code-level edits conditioned on physical test outcomes (not geometric similarity) achieve analogous convergence is an open question.

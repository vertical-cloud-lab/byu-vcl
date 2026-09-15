# Methods-Focused Guide to Publishable Robot-Arm Metrology and Reliability Characterization for Self-Driving Laboratories

## 1. Measuring Robot-Arm Accuracy and Repeatability: Standards and Practical Execution

### 1.1 What the Standards Specify

**ISO 9283:1998 (Manipulating industrial robots — Performance criteria and related test methods)** is the foundational standard. It defines the following key metrics, all evaluated at the tool center point (TCP):

- **Pose accuracy (AP):** The distance between the mean attained TCP position (over n ≥ 30 cycles) and the commanded position. Formally, the robot is commanded to the same pose from the same direction n times; AP is the Euclidean norm of the vector from the command point to the centroid of the cluster of attained points (pqac-00000008, pqac-00000034).

- **Pose repeatability (RP):** The radius of the sphere centered on the mean attained position that contains all (or a specified fraction, typically mean + 3σ) of the attained positions. RP characterizes dispersion and is always measured unidirectionally unless stated otherwise (pqac-00000008, pqac-00000034).

- **Multi-directional pose accuracy variation (vAP):** The maximum distance between the means of positions attained from three mutually orthogonal approach directions. This captures backlash and hysteresis-dependent errors.

- **Distance accuracy (AD):** The difference between the mean measured distance between two commanded poses and the nominal (computed) distance. A segment-mapping study on a UR3 cobot reported AD of ±0.078 mm and distance repeatability of ±0.102 mm (pqac-00000009).

- **Pose accuracy drift (dAP):** The systematic shift in the mean attained position over an extended operating period (typically 8 hours continuous or intermittent duty), capturing thermal and mechanical creep effects.

**Test procedure essentials from ISO 9283:**
- **Pose set:** A minimum of 5 poses distributed across the workspace, selected on a diagonal measurement plane for 6-axis robots. The standard specifies that poses should cover ≥80% of the rated workspace diagonal (pqac-00000009).
- **Cycles per pose:** n ≥ 30 approach cycles per pose, per direction.
- **Speed:** Tests at 100% and 50% of rated speed.
- **Load:** Tests at 0% (no payload) and 100% of rated payload.
- **Warm-up:** The standard requires that the robot perform a warm-up cycle before measurement begins—typically running representative motions until thermal equilibrium is approached. ISO 9283 does not prescribe a specific warm-up duration but requires that the warm-up procedure be documented.
- **Ambient conditions:** Temperature 20 ± 2 °C; temperature must be logged throughout.

**ISO/TS 15066** addresses collaborative robot operation and focuses on force/pressure limits and speed/separation monitoring rather than metrological characterization. It does not replace ISO 9283 for accuracy testing but is relevant for safety documentation when testing cobots.

**ASME B89.4.22 and ISO 10360** address articulated-arm coordinate measuring machines (AACMMs), not robot manipulators, but their volumetric performance evaluation methods (length-measurement error, single-point articulation test) provide useful methodological templates for budget-constrained labs. The key transferable concept is testing with calibrated length artifacts (gauge blocks, ball bars, step gauges) at multiple positions and orientations.

**VDI/VDE 2617-9** extends CMM testing guidance to articulated arms and similarly emphasizes traceable artifact-based verification, providing a framework adaptable to robot TCP verification.

### 1.2 What a University Lab Can Realistically Execute Without a Laser Tracker

The central challenge is that ISO 9283 assumes an external measurement system with uncertainty at least 3–5× better than the robot's claimed performance. For a robot claiming ±0.1 mm repeatability, the external reference must demonstrate ≤0.02–0.03 mm expanded uncertainty (k=2). The following table summarizes low-cost options:

| Method | Approximate cost, USD | Achievable expanded uncertainty, approximately k = 2 | Suitable uses | Principal limitations and controls |
|---|---:|---:|---|---|
| Multi-camera photogrammetry with coded targets and bundle adjustment | 1,000–10,000 | **0.03–0.15 mm** over a carefully calibrated 0.5–1 m volume; **0.2–1 mm** for less controlled setups | Multi-pose position and orientation, path mapping, workspace error maps, and thermal drift | Target localization, traceable scale, camera geometry, lens stability, and lighting dominate. Validate throughout the volume with traceable artifacts; reprojection residual alone is not measurement uncertainty. Ranges are engineering estimates. |
| ChArUco-board stereo or multi-view bundle adjustment | 300–3,000 | **0.05–0.30 mm** in a tightly controlled 0.3–0.8 m volume; commonly **0.2–1 mm** without metrology-grade board characterization | Relative pose repeatability, workspace maps, and drift exceeding roughly 0.2–0.5 mm | Printed-board pitch, flatness, humidity distortion, rolling shutter, calibration bias, and the board-to-TCP transform can dominate. Use a dimensionally inspected board on glass or aluminium and validate against independent gauge lengths. |
| Dial indicators or digital comparators in a ballbar-style fixture | 300–3,000 | **0.005–0.03 mm per axis**; approximately **0.02–0.08 mm** for an assembled multidirectional result | Local repeatability, reversal and backlash, unidirectional drift, and radial-distance variation | Normally measures only scalar components. Contact force, cosine error, probe hysteresis, fixture compliance, and TCP seating must be quantified. Strong for testing repeatability, but insufficient alone for full absolute 6-D pose accuracy. |
| Three-probe LVDT or electronic-comparator kinematic nest | 1,500–8,000 | **0.003–0.02 mm per channel**; approximately **0.01–0.05 mm** for reconstructed local displacement | High-resolution local repeatability, warm-up drift, approach-direction effects, and intervention thresholds | Small measurement range and local coverage. Requires a precision sphere, stiff nest, calibrated probe vectors, synchronized acquisition, and contact-force checks. Orientation requires more probes or spatially separated targets. |
| 3-D-printed kinematic artifact or task board | 50–500 plus dimensional inspection | **0.05–0.30 mm** when CMM-inspected with correction data; typically **0.2–1 mm** when used as printed | Task success, insertion testing, relative repeatability, and reproducible fixture construction | Shrinkage, anisotropy, warpage, wear, and printer variation prevent its use as primary sub-0.1-mm ground truth. Embed steel balls, dowels, or gauge bushings and publish inspected coordinates. Nominal 0.1-mm insertion clearance does not imply 0.1-mm metrological uncertainty (pqac-00000026, pqac-00000030). |
| Used bridge CMM, portable CMM, or institutional CMM access | 5,000–30,000 used; commonly 100–300 per service hour | **0.003–0.02 mm** for a maintained bridge CMM; approximately **0.03–0.10 mm** for many portable articulated arms | Calibration of TCP targets, fixtures, boards, gauge lengths, and accessible static poses | Requires current calibration, probe qualification, controlled temperature, an appropriate probing strategy, and a task-specific uncertainty statement. Conventional CMMs cannot generally follow dynamic motion and may have restricted robot access. |
| Laser interferometer with retroreflector | 8,000–40,000 | **0.001–0.01 mm** along one measurement line after environmental compensation | Traceable distance accuracy, linear path error, drift, and ballbar-like radial tests | Measures displacement along the beam rather than full 6-D pose. Abbe and cosine errors, refractive-index compensation, reflector alignment, and fixture stability dominate. Multiple beam directions are required for 3-D reconstruction. |
| OptiTrack- or Vicon-class optical motion capture | 8,000–50,000 | **0.05–0.30 mm** for static rigid-body position in a carefully calibrated small volume; commonly **0.2–1 mm** in larger or occluded volumes | Full-volume repeatability, path behavior, orientation, and screening of many poses | Vendor calibration residuals are not uncertainty. Marker geometry, centroid bias, occlusion, rigid-body fitting, and spatially varying calibration error require validation using traceable gauge lengths. Usually not sufficient by itself to certify 0.1-mm repeatability. |
| Laser tracker with spherical mounted retroreflector, bought used or rented | 25,000–80,000 used; commonly 1,000–3,000 per rental day | **0.006–0.03 mm** position uncertainty over typical laboratory distances | Reference-grade workspace AP, RP, AD, path, and drift measurements | A single reflector measures position but not orientation. Requires line of sight, tracker warm-up, atmospheric compensation, calibrated reflector offsets, and frame registration. A Leica AT901-based study reported approximately 6 µm tracker point accuracy (pqac-00000031, pqac-00000032). |
| Low-cost stereo or active-depth cameras such as ZED, RealSense, or Azure Kinect | 250–2,500 | **0.2–1 mm** at short range for custom global-shutter stereo with high-quality targets; generally **1–5 mm** for commodity active-depth output | Coarse path maps, failure detection, vision correction, and drift exceeding approximately 1 mm | Bias varies with range, surface, temperature, texture, exposure, multipath, and calibration. Raw active depth is inadequate for a 0.1-mm claim; custom stereo still requires traceable volumetric validation. |
| Calibrated telecentric camera or microscope observing one plane | 1,000–8,000 | **0.002–0.02 mm in-plane** over a small field of view | Local planar repeatability, endpoint marks, thermal drift, and contact-task studies | Restricted field and dimensionality; weak out-of-plane sensitivity. Alignment, pixel-scale calibration, target extraction, vibration, and focus stability matter. ISO-inspired studies have used repeated physical marks, but such adaptations are not complete ISO 9283 tests (pqac-00000008, pqac-00000034). |


*Table: Comparison of affordable external-reference methods for robot-arm characterization. The uncertainty ranges are credible targets only with traceable calibration and a complete uncertainty budget; otherwise they remain engineering estimates.*

**Critical assessment for certifying "0.1 mm repeatability":** To credibly verify or refute a 0.1 mm RP claim, the measurement system must achieve ≤0.02–0.03 mm expanded uncertainty. From the table above, the realistic options are:

1. **Dial-indicator/LVDT kinematic nest** (~$1.5–8k): Best value for pure repeatability testing. A three-probe LVDT nest with a precision tooling ball on the TCP can achieve 0.01–0.05 mm uncertainty and directly measures the quantity of interest (return-to-point scatter). This is the recommended primary instrument for a budget-constrained lab.

2. **Laser tracker rental** (~$1–3k/day): For 2–3 rental days, a lab can execute a near-complete ISO 9283 campaign across multiple workspace poses. A Leica AT901 provides ~6 µm point accuracy (pqac-00000032). This is the gold standard and is recommended for at least a subset of validation poses.

3. **Photogrammetry with coded targets** (~$1–10k): Can achieve 0.03–0.15 mm with careful calibration but requires significant expertise and traceable scale validation. Best used as a secondary method for workspace mapping.

4. **OptiTrack/Vicon motion capture** (~$8–50k): Typically achieves 0.05–0.3 mm static accuracy, marginal for certifying 0.1 mm claims without independent traceable validation.

**Recommendation:** Combine a LVDT/dial-indicator nest (primary, for high-resolution repeatability at selected poses) with 1–2 days of laser tracker rental (for absolute accuracy across the workspace). Validate all instruments against traceable gauge blocks or calibrated ball bars.

## 2. Thermal Drift and Duty-Cycle Effects

### 2.1 Magnitudes and Time Constants

Thermal drift is a dominant error source for robot arms, particularly during warm-up. Heat generated by motors and gearboxes (including harmonic drives, cycloidal drives, and planetary reducers) is conducted through the robot structure, causing dimensional changes in aluminum links and compliance changes in drive components.

Key findings from the literature:

- **Warm-up duration:** Industrial robots typically require approximately **2 hours** of continuous representative motion to reach thermal steady state, with some precision applications requiring up to **5 hours** (pqac-00000010).

- **Drift magnitude:** For a KUKA KR-15/2, cold-start repeatability was approximately **±140 µm** versus a catalog specification of ±100 µm, while steady-state repeatability improved to approximately **±20 µm**—an 80% improvement over the manufacturer's stated value (pqac-00000010, pqac-00000011). A rough estimate suggests that a 5°C temperature rise in a typical aluminum robot link produces approximately **40 µm** of linear thermal expansion (pqac-00000011).

- **Simplified system time constants:** In a two-link experimental system, thermal steady state was reached at approximately **200 seconds** with total longitudinal deformation of approximately **120 µm** (pqac-00000013). Full robot arms have longer time constants (30–120 minutes) due to larger thermal masses.

- **Low-cost arms with integrated modular actuators:** No published thermal characterization was found specifically for sub-$5k arms (AgileX PiPER class) with brushless motors and planetary/harmonic reducers. This is a genuine gap. These actuators likely exhibit faster thermal transients (lower thermal mass) but potentially larger percentage drift relative to their shorter link lengths. **This is flagged as extrapolation—characterizing this is exactly the novel contribution.**

### 2.2 Warm-Up Protocol Design for Reproducibility

Based on the literature and ISO 9283 requirements:

1. **Standardized warm-up trajectory:** Define a representative joint-space trajectory that exercises all joints through ≥80% of their range at ≥50% rated speed.
2. **Duration:** Run for a minimum of 60 minutes (low-cost arms) or until TCP drift rate falls below 5 µm/min for 10 consecutive minutes.
3. **Temperature logging:** Attach K-type thermocouples or digital sensors (e.g., DS18B20, ±0.5°C) to each joint housing. Log at ≥1 Hz. Record ambient temperature with a calibrated sensor (±0.1°C resolution).
4. **Drift measurement:** Record TCP position at a reference pose every 5 minutes throughout warm-up using the LVDT nest or equivalent.
5. **Report:** Plot TCP drift vs. time and vs. joint temperatures. Fit exponential decay models to extract time constants per axis. Report ambient temperature range during all tests (pqac-00000010, pqac-00000014, pqac-00000015, pqac-00000017).

## 3. Reliability Engineering for Autonomous Laboratories

### 3.1 Existing Metrics and Frameworks

The SDL community currently lacks standardized reliability metrics. No deployed SDL paper reports MTBI specifically for the robot arm. However, several frameworks are emerging:

**Autonomy level scales for SDLs:**
- Lo et al. (2024) proposed a multi-dimensional autonomy classification where autonomy is reported separately for synthesis, characterization, sample transfer, and experiment planning. They suggested incorporating **failure rate/tolerance** and **number of uninterrupted iterations** as dimensions of autonomy classification (pqac-00000018).
- Cheng et al. (2026) proposed a **five-level autonomy framework** where Levels 4–5 represent genuine laboratory autonomy requiring failure recovery, verifiability, safety constraints, audit trails, and sustained closed-loop operation (pqac-00000019).
- Le Houx (2025) proposed a **six-level taxonomy (L0–L5)** with a key "Inference Barrier" at Level 3, along with the **Entropy-Scaled Measurement Efficiency (ESME)** metric and Operational Design Domain (ODD) concepts borrowed from autonomous vehicles (pqac-00000020, pqac-00000022, pqac-00000023).
- The **ADePT framework** defines four dimensions: Adaptability, Dexterity, Perception, and Task complexity for assessing laboratory robotics capability.

**Failure taxonomies:**
- **LabRobFail** (Wang et al., 2026) is the first dedicated failure taxonomy and benchmark for chemical SDLs. It defines **5 major failure categories** and **11 fine-grained failure types**: Perception Failure (target positioning deviation, operation position error), Grasping Failure (gripper control failure, object slippage), Motion Failure (pose control error, incomplete trajectory), Logic Failure (sequence reversal, step omission), and Safety Failure (protocol violation, improper handling). The benchmark includes >20,000 trajectories across >70 task scenarios with severity assessment on a 4-level scale (L1–L4) (pqac-00000000, pqac-00000001, pqac-00000002, pqac-00000004).
- Cheng et al. (2026) proposed a complementary three-layer taxonomy: execution failures, sample state/identity failures, and measurement/data failures (pqac-00000005, pqac-00000006).

**Adjacent field practices:**
- **Semiconductor fab:** Uses Overall Equipment Effectiveness (OEE = Availability × Performance × Quality), MTBF, MTTR, and detailed equipment event logging per SEMI E10/E58 standards.
- **Industrial robotics:** ISO 9283 for performance; IEC 61508/62443 for functional safety; Weibull analysis for component life.
- **Spacecraft autonomy:** Uses autonomy level scales analogous to SAE J3016 for vehicles; fault-detection-isolation-recovery (FDIR) architectures; mission success probability models.
- **Warehouse automation:** Uses picks-per-hour, grasp success rate, MTBF, and intervention rate (interventions per 1000 picks).

### 3.2 Statistical Framework for MTBI Claims

**Per-operation reliability model (binomial):** If each operation succeeds independently with probability p, then after n operations the number of failures follows Binomial(n, 1−p). To distinguish p = 0.975 from p = 0.998 with 95% confidence requires:

- Using a one-sided exact binomial test, observing 0 failures in n trials gives a 95% lower confidence bound on p of p_lower = 1 − (0.05)^(1/n).
- For p_lower ≥ 0.975: n ≥ log(0.05)/log(0.975) ≈ **118 trials** (0 failures).
- For p_lower ≥ 0.998: n ≥ log(0.05)/log(0.998) ≈ **1,497 trials** (0 failures).
- With some failures observed, larger samples are needed. A reasonable minimum for a publishable claim is **500–1,500 operations** depending on the target reliability level.

**Time-to-failure model (Weibull):** For wear-out or infant-mortality analysis, the two-parameter Weibull distribution f(t) = (β/η)(t/η)^(β−1) exp(−(t/η)^β) is standard. β < 1 indicates infant mortality (decreasing failure rate); β > 1 indicates wear-out. Maximum likelihood estimation with right-censored data (runs that ended without failure) is straightforward and should be used when campaigns are terminated before all units fail.

**Renewal process:** For ongoing SDL operation with repair/recovery, a renewal-process model is appropriate. The mean time between interventions is estimated as total operating time divided by number of interventions, with confidence intervals from parametric bootstrap or from the renewal-theory relationship to the underlying failure-time distribution.

**Censored and mixed failure modes:** Use competing-risks survival analysis. Each failure mode (e.g., grasp failure, collision, software error) has its own cause-specific hazard. Kaplan-Meier or Nelson-Aalen estimators handle right-censored data. Report cause-specific MTBI alongside overall MTBI.

## 4. Existing Benchmarks and Datasets

### 4.1 Robot Manipulation Benchmarks

- **NIST Assembly Task Board:** A collection of insertion and fastening operations representing industrial assembly. Supports precision insertion and assembly evaluation but does not support tolerance variation or task reconfiguration (pqac-00000028).
- **YCB Object and Model Set:** Standardized object set for grasping and manipulation research; widely adopted but not specifically designed for precision insertion tasks (pqac-00000030).
- **Peg-in-Bench** (Delgado et al., 2026): A modular, 3D-printable benchmark for high-precision peg-in-hole insertion. Features 5 peg geometries, 3 clearance tolerances (0.1, 1, 3 mm), reconfigurable bases, and a scenario-generation tool with machine-readable JSON specifications. Available at github.com/aistairc/peg-in-bench (pqac-00000026, pqac-00000027, pqac-00000029).
- **FMB (Functional Manipulation Benchmark), FurnitureBench, RLBench, OCRTOC, ManipulationNet:** Various manipulation benchmarks focused on policy learning rather than metrological characterization (pqac-00000030).
- **RoboCup@Work:** Industrial-relevant mobile manipulation tasks with standardized scoring.

### 4.2 Lab-Automation-Specific Benchmarks

**No standardized labware task board currently exists.** This is a significant gap. A credible labware task board for the SDL community would need to contain:

1. **SBS/ANSI-format microplate slots** (96-well and 384-well) with defined clearances
2. **Vial racks** (2 mL, 20 mL scintillation vials) with pick-and-place targets
3. **Pipette tip rack interface** for tip pickup testing
4. **Lid-handling stations** for petri dishes and microplates
5. **Weighing station access** mimicking analytical balance placement
6. **Calibrated gauge features** (precision dowel holes, kinematic references) for metrological ground truth
7. **Machine-readable fiducials** for vision-system evaluation

Endorsement from SLAS (Society for Laboratory Automation and Screening), ANSI/SBS standards committees, and key SDL groups (Aspuru-Guzik, Abolhasani, Sparks) would be needed for community adoption.

## 5. Publication and Venue Strategy

### 5.1 Target Venues

| Venue | Scope fit | Open data/hardware requirements | Typical review cycle | Notes |
|---|---|---|---|---|
| **HardwareX** (Elsevier) | Excellent for open hardware characterization | Requires complete design files, BOM, build instructions, validation data | 3–6 months | Specifically designed for hardware papers; lower impact factor but high citation utility for reference implementations |
| **Digital Discovery** (RSC) | SDL community home journal | Encourages open data; RSC open-access options | 3–5 months | Published Lo et al. "Frugal Twin" review and similar SDL infrastructure papers (pqac-00000018) |
| **SLAS Technology** | Laboratory automation focus | Standard data availability statements | 3–6 months | Directly relevant audience; formerly JALA |
| **Measurement** (Elsevier) | Metrology and measurement methods | Standard data sharing | 3–5 months | Strong fit for ISO 9283-style characterization papers |
| **Precision Engineering** (Elsevier) | Machine and robot metrology | Standard | 3–6 months | Highest prestige for metrology work; more demanding reviewers |
| **IEEE RA-L** | Robotics, manipulation, calibration | Multimedia/code encouraged | 3–5 months (single review cycle) | High visibility; requires robotics novelty beyond pure characterization |
| **IEEE T-ASE** | Automation, manufacturing systems | Standard | 6–12 months | Good for reliability/OEE framework papers |
| **JOSS** (Journal of Open Source Software) | Software packages only | Requires open-source code repository | 1–3 months | For the analysis software/toolkit, not the experimental paper |

### 5.2 Recommended Strategy

**Primary submission:** HardwareX or Digital Discovery for the combined metrology + reliability paper. Both value open hardware contributions and serve the SDL community.

**Secondary/companion:** Measurement or Precision Engineering for a deeper metrology-only treatment with ISO 9283 compliance analysis. SLAS Technology for a reliability-focused companion emphasizing MTBI and failure taxonomy.

**Software companion:** JOSS for the open-source data-analysis toolkit.

## 6. The Minimum Credible Paper

### 6.1 Experimental Campaign Specification

**Robot under test:** Sub-$5k 6-DOF arm (e.g., AgileX PiPER or equivalent), fully documented with firmware version, serial number, and joint-level specifications.

**Pose set:** 5 poses distributed across the workspace diagonal plane per ISO 9283 guidelines, covering ≥80% of the rated workspace. Include at least one near-center pose, one near maximum reach, and one at a high joint-4/5/6 rotation (pqac-00000009).

**Cycle counts per pose:**
- **Repeatability (RP):** 30 cycles × 5 poses × 3 approach directions = **450 individual measurements** minimum
- **Accuracy (AP):** Same 30 cycles, with absolute position referenced to external measurement
- **Distance accuracy (AD):** 30 cycles between each of 5 pose pairs = **150 measurements**
- **Drift (dAP):** 1 reference pose measured every 5 minutes over 4 hours = **48 drift measurements**

**Payload conditions:** Test at 0% and 100% of rated payload (typically 0 g and 250–500 g for PiPER-class arms).

**Speed conditions:** Test at 50% and 100% of rated TCP speed.

**Thermal protocol:**
1. Cold start: Log joint and ambient temperatures. Begin drift measurement immediately.
2. Warm-up trajectory: Run standardized joint-space trajectory for 60 minutes.
3. Document time to thermal equilibrium (drift rate < 5 µm/min for 10 min).
4. All RP/AP/AD measurements taken after warm-up completion.
5. Log temperatures continuously throughout at ≥0.1 Hz.
6. Ambient temperature: maintain 20 ± 2°C or document excursions.

**Measurement instruments:**
- **Primary (repeatability):** Three-probe LVDT kinematic nest with precision tooling ball on TCP. Budget: ~$2–4k. Calibrate probes against gauge blocks; document probe geometry and uncertainty budget.
- **Validation (accuracy):** 1–2 days of laser tracker rental OR calibrated photogrammetry system validated against traceable scale bars. Budget: ~$2–5k.
- **Temperature:** K-type thermocouples on each joint + calibrated ambient sensor. Budget: ~$200.

**Statistical analysis plan:**
- Report AP, RP (mean + 3σ sphere radius), vAP, AD, and dAP per ISO 9283 definitions.
- Report per-axis components (x, y, z) as well as 3D Euclidean values.
- Fit exponential thermal-drift model: d(t) = d_∞(1 − exp(−t/τ)) + d_0.
- Compute 95% confidence intervals on all metrics via bootstrap (n=10,000 resamples).
- Test for workspace-position dependence via ANOVA across 5 poses.
- Test for payload dependence via paired comparison.

**Reliability campaign (for MTBI):**
- Define a standardized SDL operation cycle: home → pick vial from rack → transfer to station → place → return. Duration ~30–60 seconds.
- Run ≥500 consecutive cycles with automated logging (video + telemetry).
- Log every intervention with timestamp, cause category (LabRobFail taxonomy: PF/GF/MF/LF/SF), and recovery action (pqac-00000000, pqac-00000001).
- Report per-operation success rate with exact binomial 95% CI.
- Report MTBI = total operating time / number of interventions, with bootstrap CI.
- If sufficient failures observed, fit Weibull model to time-between-failure data.

**Data/code artifacts to release:**
1. Raw measurement data (CSV/HDF5) with metadata (timestamps, temperatures, poses, payloads)
2. Robot URDF and calibration parameters
3. Analysis code (Python, open-source, with requirements.txt)
4. CAD files for LVDT nest fixture and any 3D-printed artifacts (STL + STEP)
5. Video of measurement setup and representative test cycles
6. Uncertainty budget spreadsheet

### 6.2 Anticipated Reviewer Critiques and Preemptive Responses

1. **"Your measurement system uncertainty is not traceable."** Preempt by: calibrating LVDTs against gauge blocks; documenting complete uncertainty budget per GUM (Guide to the Expression of Uncertainty in Measurement); validating against a second independent method (laser tracker or CMM-inspected artifact).

2. **"N=30 cycles is too few / you only tested 5 poses."** Preempt by: following ISO 9283 minimum requirements explicitly; computing and reporting statistical power; showing that confidence intervals are sufficiently narrow for the claims made.

3. **"Thermal state was not controlled."** Preempt by: documenting warm-up protocol with drift data; reporting all temperatures; showing measurements were taken in steady state (pqac-00000010, pqac-00000011).

4. **"Results may not generalize to other specimens of the same arm."** Acknowledge this limitation; recommend multi-unit testing as future work; report serial number and firmware version for reproducibility.

5. **"MTBI sample size is insufficient."** Preempt by: running ≥500 cycles; reporting exact binomial confidence intervals; being explicit about what reliability level the data can and cannot distinguish.

6. **"No comparison to established robots."** If budget allows, include comparison data from a UR3e or similar cobot with known specifications. Otherwise, compare to manufacturer datasheets and published UR3 characterization data (pqac-00000009).

7. **"The failure taxonomy is ad hoc."** Preempt by: adopting the LabRobFail taxonomy (pqac-00000000, pqac-00000002) or explicitly mapping to it; documenting inter-rater agreement on failure classification.

### 6.3 Summary: Minimum Viable Scope

The smallest defensible paper combines: (a) ISO 9283-aligned characterization of a sub-$5k arm at 5 poses, 2 payloads, with documented thermal protocol and traceable measurement uncertainty; (b) ≥500-cycle reliability campaign with structured failure logging. This would be the first paper to provide both quantitative metrological characterization and real MTBI data for a low-cost arm in an SDL context, filling a clear gap identified by the SDL community. The complete campaign is achievable in approximately 2–3 weeks of dedicated lab time with ~$5–10k in measurement equipment (LVDT nest + laser tracker rental + temperature sensors), making it realistic for a small academic lab.

---

*Note: ISO 9283, ISO/TS 15066, ASME B89.4.22, ISO 10360, and VDI/VDE 2617-9 are proprietary standards documents. The specific clause numbers and procedural details described above are synthesized from secondary sources that reference these standards and from established metrology practice. Researchers should obtain the current editions of these standards for full compliance. The thermal drift magnitudes, measurement system uncertainties, and cost estimates represent best available evidence and engineering judgment; values flagged as extrapolation (particularly for sub-$5k arms) require experimental validation.*
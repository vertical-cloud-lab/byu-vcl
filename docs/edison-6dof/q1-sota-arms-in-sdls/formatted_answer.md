Question: # Question

What is the current state of the art (2023-2026) for using low-cost 6-DOF robotic
manipulator arms, with wrist-mounted ("eye-in-hand") cameras, as the sample-transfer and
manipulation layer of self-driving laboratories (SDLs) for materials science and
chemistry? I want a critical, citation-dense survey plus an explicit gap analysis that
identifies which unsolved problems are both high-impact and timely for a small
university lab to attack in the next 12-18 months.

# Context for the answer

We are a university self-driving-lab group (Vertical Cloud Lab, BYU Mechanical
Engineering) working on remotely accessible, cloud-controlled autonomous laboratories for
structural/aerospace alloys and electrochemistry. Our existing automation is
gantry-and-fixture based: vertical lift modules, a powder dosing/excavation unit,
ultrasonic atomizers, laser powder-bed-fusion metal 3D printers, tensile/drop testers,
custom induction furnaces, Opentrons OT-2 liquid handlers, and 3D-printed electrochemical
cells. We are about to acquire an AgileX PiPER 6-DOF arm (a ~1.5 kg payload, ~$2.5k
research arm with CAN-bus control and a ROS 2 driver) and will attach our own camera to
its wrist. We care about frugal, reproducible, open-hardware approaches ("frugal twins")
and about remote/cloud operation by users who are not physically present.

# Specifically, please address

1. **What arms actually do in deployed SDLs.** Survey concrete deployed systems where a
   6-DOF arm (not a gantry, not a Cartesian liquid handler, not an AGV/mobile base alone)
   performs the manipulation: e.g. the mobile robotic chemist work from Cooper's group at
   Liverpool, the A-Lab at LBNL, Ada/Acceleration Consortium self-driving labs, ARES/
   autonomous synthesis platforms, Emerald/Strateos-style cloud labs, Chemspeed +
   arm hybrids, and any 2025-2026 entrants. For each: what arm, what payload, what
   end-effector, what tasks, what fraction of the workflow the arm covers, what the
   reported throughput and failure/intervention rate are, and whether the integration
   code is open.

2. **Arm vs. gantry vs. fixed automation — the honest trade study.** Under what
   conditions does a 6-DOF arm actually beat a cheaper gantry or a purpose-built fixture
   in an SDL? Quantify where you can: positional repeatability required for common lab
   tasks (vial capping/decapping, crucible transfer, sample coupon loading into a tensile
   grip, cuvette into a spectrometer, powder scoop transfer, electrode swapping), and
   compare to the repeatability actually delivered by sub-$5k arms. Where do low-cost
   arms fail — payload at extension, thermal drift, backlash, gravity sag, lack of
   force sensing?

3. **Vision in the loop.** What is the current best practice for eye-in-hand vision on a
   research arm? Cover: hand-eye calibration methods and their achievable accuracy;
   fiducial-based (AprilTag/ArUco/ChArUco) vs. learned 6-DoF pose estimation
   (FoundationPose, MegaPose, SAM-6D and successors); when RGB-D or stereo is needed
   versus monocular; and the practical accuracy ceiling of each in cluttered, specular,
   transparent-labware scenes. Transparent and reflective objects (glass vials, quartz
   crucibles, metal powder) are a known hard case — what actually works there in 2025-2026?

4. **Vision-language-action (VLA) and foundation models for manipulation.** How usable
   are open VLA models (OpenVLA, Octo, RT-2-class, pi-0 / pi-0.5, GR00T N1, SmolVLA and
   whatever is current) for laboratory manipulation specifically? What data volumes,
   fine-tuning cost, and success rates are actually reported on lab-like tasks? Is the
   honest 2026 answer still "scripted motion primitives plus fiducials beat learned
   policies for repetitive lab tasks," and if so, where exactly is the crossover?

5. **Reliability, error recovery, and remote operation.** SDL papers rarely report
   mean-time-between-intervention. What is known about failure modes of arm-based lab
   automation, and what architectures (behavior trees, state machines, LLM planners with
   verifiers, digital twins for pre-flight collision checking, teleoperation fallback)
   are being used to keep an arm running unattended or under remote supervision? What
   safety interlocks are standard for a collaborative arm near hot furnaces, powders, or
   solvents?

6. **Gap analysis — the actual deliverable.** Given all of the above, list 8-15 specific,
   concrete research or engineering contributions that (a) are not yet solved or not yet
   published, (b) are tractable for a small academic lab with one low-cost 6-DOF arm, a
   custom wrist camera, existing gantry/furnace/printer/tester hardware, and strong
   Bayesian-optimization and cloud-infrastructure expertise, and (c) would be timely and
   citable in 2026-2027. For each, state the specific claim a paper would make, the
   minimum experiment needed to support it, the most likely venue, and what would make it
   fail or be scooped. Rank them. Be blunt about which ideas are already crowded.

Please prioritize peer-reviewed and arXiv sources from 2024-2026, cite specific numbers
(repeatability in mm, success rates, throughput, cost) wherever the literature reports
them, and clearly flag where you are extrapolating rather than citing.


# Low-Cost 6-DOF Robotic Arms with Eye-in-Hand Cameras for Self-Driving Laboratories: State of the Art and Gap Analysis (2023–2026)

## 1. What Arms Actually Do in Deployed SDLs

The dominant role of 6-DOF (or 7-DOF) arms in current SDLs is **inter-station sample transfer**—moving vials, crucibles, coupons, or racks between synthesis, characterization, and storage modules—rather than performing the core chemistry or physics themselves. Process-intensive steps (liquid dispensing, heating, sealing, powder mixing) are almost universally delegated to purpose-built stations (Chemspeed, Opentrons, custom fixtures), while the arm acts as a flexible "logistics layer."

The following table summarizes the major deployed systems identified in the literature:

| System | Institution | Arm model | DOF | Payload | End-effector | Arm’s primary tasks / workflow coverage | Reported throughput | Reported reliability | Integration code | Key reference |
|---|---|---:|---:|---:|---|---|---|---|---|---|
| Mobile robotic chemist | University of Liverpool, Cooper group | KUKA KMR-iiwa mobile manipulator | 7 | 14 kg | Custom HGPLE-14 Festo gripper with vial/rack fingers | Transports prepared MS/NMR samples among Chemspeed iSynth, UPLC–MS, and benchtop NMR; accesses stations and operates doors. Chemspeed—not the arm—performs liquid handling, heating, sealing, and aliquoting. | Dai et al. report autonomous campaigns lasting 2–3 days but no normalized rate. The often-quoted 688 experiments in 8 days (~86/day) belongs to the group’s earlier 2020 photocatalyst campaign and should not be attributed directly to the 2024 workflow. | No MTBI or operation-level success rate; authors report that stable multi-platform operation required >1 year of development/debugging. | Workflow scripts are described, but a complete reproducible integration stack is not reported as open. | Dai et al., *Nature* (2024) (dai2024autonomousmobilerobots pages 6-7, dai2024autonomousmobilerobots pages 2-3, dai2024autonomousmobilerobots pages 7-8, dai2024autonomousmobilerobots pages 9-10, liu2023transformingorganicchemistry pages 8-10, lunt2024aroboticworkflow pages 49-57) |
| Robotic PXRD workflow | University of Liverpool | ABB YuMi IRB 14000 dual-arm robot; KUKA KMR-iiwa supplies mobile transport | 7 axes per YuMi arm | Not reported in source | Modified ABB SmartGrippers; KUKA uses custom Festo gripper | YuMi transfers vials, grinds/mixes/inverts samples, and loads powder into custom PXRD plates; KUKA moves racks, opens diffractometer doors, and loads plates. Together they cover transfer and PXRD preparation, while Chemspeed performs crystallization. | Not reported | No MTBI or aggregate success rate reported; mobile-base positioning is ±10 mm and orientation <±2.5°, with six-point calibration used for station registration. | ARChemist/ROS architecture is described; availability of a complete deployable hardware-integration repository is only partial or unclear. | Lunt (2024) (lunt2024aroboticworkflow pages 49-57, lunt2024aroboticworkflow pages 42-49, lunt2024aroboticworkflow pages 103-110, lunt2024aroboticworkflow pages 125-129) |
| Vision-guided powder scooping | University of Liverpool, Cooper/Pizzuto groups | Franka Research 3 | 7 | Not reported in source | Robotiq 85F gripper holding a spatula/scoop | Iterative powder acquisition and dispensing: an external RealSense D405 evaluates scoop fill, detects empty or failed scoops, and triggers trajectory adjustment; a precision balance closes the mass loop. | Cycle throughput not reported; mean absolute weighing error was 1.93 ± 2.04 mg across seven powders. | Successful-scoop classification 89.21%; unsuccessful-scoop classification 96% across 40–700 lux. No long-duration intervention rate reported. | Publication does not establish release of the complete robot-integration stack. | Radulov et al., *Digital Discovery* (2026) (radulov2026visionguidedadaptivescooping pages 4-6, radulov2026visionguidedadaptivescooping pages 6-7, radulov2026visionguidedadaptivescooping pages 3-4, radulov2026visionguidedadaptivescooping pages 1-2, radulov2026visionguidedadaptivescooping pages 2-3) |
| Automated bulk-intermetallic synthesis | NIMS / Takano group | Denso-Wave COBOTTA on a one-axis slider | 6 | Not reported in source | Custom 3D-printed gripper | Retrieves dosing heads and copper carriers; moves materials to/from the balance and delivery station; returns products to storage. Sliders—not the arm—perform final insertion into the arc-melting chamber. | Not reported | No MTBI, per-transfer success, or intervention rate reported. | ROS 2 modular orchestration is described through `main`, `weighing`, `cobotta`, `slider`, `plc`, and `record` nodes; the paper supports an open architecture, but does not establish that every driver/source file is publicly released. | Wang, Terashima & Takano (2025/26) (wang2509orchestrationofheterogeneous pages 1-3, wang2509orchestrationofheterogeneous pages 6-9, wang2509orchestrationofheterogeneous pages 3-6, wang2509orchestrationofheterogeneous pages 9-12) |
| Ada spray-coating SDL | University of British Columbia / Acceleration Consortium | Custom single-arm module; commercial model not specified | Not reported | Not reported | Rotatable gripper and pipetting/dispensing tooling; spray-coating hardware | Transfers substrates and consumables and links mixing, coating, heating, and characterization modules; purpose-built stations perform most process physics. | Up to four parallel experiments and ~100 experiments/day; an earlier Ada configuration produced one synthesized/characterized sample every ~20 min and required replenishment after seven samples. | Approximately one run-ending failure per 40 samples (97.5% per-sample success). For a 50-sample overnight campaign this implies only 28.2% completion probability; ~99.8% per-sample reliability would be needed for 90% campaign completion. | Partially documented; a complete turnkey open integration stack is not established. | Rupnow (2024), with prior Ada description (lunt2024aroboticworkflow pages 11-16, rupnow2024aselfdrivinglaboratory pages 101-107, rupnow2024aselfdrivinglaboratory pages 21-26) |
| A-Lab | Lawrence Berkeley National Laboratory | Arm manufacturer/model and number of arms not established by the retrieved source | Not reported | Not reported | Custom solid-handling fixtures; details not established by the retrieved source | Automated inorganic solid-state workflow is widely described as including powder dosing/mixing, crucible handling, furnace processing, and characterization, but the retrieved evidence does not resolve which steps are performed by a 6-DOF arm rather than dedicated automation. | Attempted 58 target materials in just over two weeks; the retrieved excerpt does not support a normalized arm throughput. | No arm-operation success, MTBI, or intervention rate reported in the retrieved source. Failed syntheses were used to propose revised procedures. | Not fully open; no complete arm-control/integration repository established. | Adam, *PNAS* (2024), summarizing A-Lab (adam2024theautomatedlab pages 1-3) |


*Table: Deployed and research-stage SDLs using articulated manipulators, with reported workflow coverage, throughput, reliability, and code availability. The table distinguishes arm-performed operations from work delegated to fixed automation and flags metrics that the literature does not report.*

**Key observations.** Cooper's Liverpool mobile robotic chemist (Dai et al., *Nature* 2024) is the most visible 6-DOF-arm SDL. Two KUKA KMR-iiwa mobile manipulators (7-DOF, 14 kg payload) transport reaction vessels between a Chemspeed iSynth synthesizer, a UPLC–MS, and a benchtop NMR, enabling instruments to be shared with human researchers rather than monopolized (dai2024autonomousmobilerobots pages 6-7, dai2024autonomousmobilerobots pages 2-3, dai2024autonomousmobilerobots pages 1-2). The authors emphasize that achieving stable multi-platform operation required more than a year of development and debugging, and that low per-module failure rates are "practically important" (dai2024autonomousmobilerobots pages 7-8). In a separate Liverpool workflow for PXRD screening, an ABB YuMi dual-arm robot performs crystal sample preparation while KUKA handles inter-station transport; the KUKA mobile base achieves ±10 mm positioning precision and <±2.5° orientation, improved via six-point calibration with force feedback (lunt2024aroboticworkflow pages 49-57, lunt2024aroboticworkflow pages 42-49).

For materials-science SDLs specifically, Wang et al. describe a Denso-Wave Cobotta 6-axis cobot integrated via ROS 2 for automated bulk intermetallic synthesis, where the arm retrieves dosing heads from storage, transports them to an electronic balance, and delivers loaded sample carriers to an arc-melting chamber (wang2509orchestrationofheterogeneous pages 1-3, wang2509orchestrationofheterogeneous pages 6-9, wang2509orchestrationofheterogeneous pages 3-6). The ROS 2 architecture uses six principal nodes (main, weighing, cobotta, slider, plc, record) with asynchronous execution (wang2509orchestrationofheterogeneous pages 6-9, wang2509orchestrationofheterogeneous pages 9-12).

Ada (University of British Columbia / Acceleration Consortium) achieves up to ~100 experiments/day with a single-arm module linking mixing, spray-coating, heating, and characterization, but reports approximately one run-ending failure per 40 samples (97.5% per-sample success). For a 50-sample overnight campaign, this yields only a 28.2% probability of uninterrupted completion; the authors calculate that 99.8% per-sample reliability would be needed for 90% campaign success (rupnow2024aselfdrivinglaboratory pages 101-107, rupnow2024aselfdrivinglaboratory pages 21-26). This reliability gap is arguably the single most important quantitative finding in the SDL reliability literature.

The A-Lab at LBNL is widely cited for attempting 58 target materials autonomously in roughly two weeks, but the retrieved literature does not resolve which specific tasks are performed by articulated arms versus dedicated automation (adam2024theautomatedlab pages 1-3).

**A critical absence:** No deployed SDL paper reports a formal mean-time-between-intervention (MTBI) metric for the robotic arm specifically. Failure rates are either unreported, reported at the whole-campaign level, or conflated with instrument and software errors.

---

## 2. Arm vs. Gantry vs. Fixed Automation: The Honest Trade Study

**When a 6-DOF arm wins.** Arms are justified when the workflow requires (a) reaching multiple spatially distributed stations that cannot be arranged linearly, (b) operating existing human-designed equipment (doors, lids, instrument loading bays), or (c) flexibility to reconfigure for new experiments without hardware redesign (dai2024autonomousmobilerobots pages 1-2, wang2509orchestrationofheterogeneous pages 3-6). Cooper's system explicitly uses mobile robots so that instruments can be shared with human researchers without monopolizing them (dai2024autonomousmobilerobots pages 1-2).

**When a gantry or fixture wins.** For repetitive, geometrically constrained tasks—liquid dispensing, plate handling, well-plate transfer—gantry systems (Opentrons OT-2 at ~$5k, Jubilee at ~$2k) offer superior positional repeatability at lower cost (lo2023reviewoflowcost pages 2-5, lo2023reviewoflowcost pages 14-16, lo2023reviewoflowcost pages 12-14). The frugal-twin review notes that liquid-handling frugal twins are currently more practical than solid-handling ones because pumps and tubing are inexpensive and robust, whereas powder handling remains difficult and costly (lo2023reviewoflowcost pages 26-28). The Jubilee multi-tool motion platform, with interchangeable tools and ~$2,000 total cost, supports fabrication, liquid handling, and integration with plate spectrometers (lo2023reviewoflowcost pages 12-14).

**Quantitative repeatability comparison** (*note: partially extrapolated*). The KUKA KMR-iiwa mobile base achieves ±10 mm positioning before calibration (lunt2024aroboticworkflow pages 49-57). Industrial cobots (UR5e, Franka) typically specify ±0.03–0.1 mm repeatability at the flange, but this degrades substantially at extension, under payload, and with thermal drift. Sub-$5k arms like the AgileX PiPER are expected to have repeatability in the ±0.5–2 mm range at best (*extrapolation: no published characterization of the PiPER exists*). Common lab tasks span a wide range of tolerance requirements:

- **Vial rack insertion:** ±1–2 mm lateral, ±3° angular (achievable with low-cost arms + vision correction)
- **Cuvette into spectrometer slot:** ±0.5 mm (marginal for low-cost arms without visual servoing)
- **Tensile coupon into grip:** ±0.3 mm (likely requires fixture-based alignment, not free-space arm placement)
- **Powder scoop transfer:** ±2–5 mm (achievable; vision feedback is more critical than arm repeatability, as shown by Radulov et al.)
- **Crucible into furnace:** ±1 mm but under thermal drift conditions (challenging)

**Where low-cost arms fail.** Payload at extension (the PiPER's 1.5 kg drops rapidly at full reach), gravity sag, backlash in harmonic/cycloidal drives, and absence of torque sensing are the primary limitations. The frugal-twin literature recommends accepting lower precision and compensating with repeated measurements when throughput is high (lo2023reviewoflowcost pages 5-7, lo2023reviewoflowcost pages 12-14).

**The honest recommendation for BYU's setup:** Use the PiPER arm for inter-station transfer and coarse positioning, but retain gantry/fixture-based alignment for precision-critical operations (tensile grip loading, electrode cell assembly). Vision-in-the-loop correction is essential to close the repeatability gap.

---

## 3. Vision in the Loop

### 3.1 Eye-in-Hand Best Practice

Current SDL vision systems predominantly use Intel RealSense RGB-D cameras. Radulov et al. use an external RealSense D405 for powder-fill assessment, achieving 89.2% accuracy for successful-scoop classification and 96% for unsuccessful-scoop classification across 40–700 lux illumination, with a stopping tolerance of 1 mg and average weighing error of 1.93 ± 2.04 mg (radulov2026visionguidedadaptivescooping pages 4-6, radulov2026visionguidedadaptivescooping pages 6-7, radulov2026visionguidedadaptivescooping pages 3-4, radulov2026visionguidedadaptivescooping pages 1-2). TransGraspNet uses an eye-in-hand RealSense D435i on an AUBO i5, achieving 91.0% overall grasp success across 100 trials on transparent labware (96% simple, 86% cluttered), with 3.8° angular error and 8.5 mm positional offset for grasp alignment (hu2026transgraspnetphysicallyand pages 6-7).

### 3.2 Fiducial vs. Learned Pose Estimation

**Fiducial-based methods** (AprilTag, ArUco, ChArUco) remain the workhorse for SDL station registration. Their accuracy ceiling is typically ±1–2 mm in translation and ±1° in rotation at working distances of 0.3–0.5 m with a calibrated camera (*extrapolation from robotics literature; no SDL-specific characterization was found*). They are deterministic, require no training data, and fail gracefully (detection either succeeds or doesn't). The Liverpool KUKA system uses a six-point calibration procedure with calibration cubes and force feedback for station registration (lunt2024aroboticworkflow pages 49-57).

**Learned 6-DoF pose estimators** (FoundationPose, MegaPose, SAM-6D) are model-free methods that generalize to unseen objects given only a CAD model or reference images. MegaPose uses a two-stage render-and-compare pipeline trained on >20,000 synthetic objects, with a coarse estimation runtime of 1.68 s/detection (vaggelis20256dobjectpose pages 34-38). FoundationPose and SAM-6D show correct predictions on standard benchmarks, though SAM-6D is slower due to multi-stage filtering and point-cloud validation (vaggelis20256dobjectpose pages 52-54). Neither method has been specifically validated on transparent laboratory glassware in the retrieved literature.

### 3.3 Transparent and Reflective Objects

This remains a recognized hard problem. TransGraspNet addresses it through physics-aware and geometry-consistent depth completion, achieving RMSE 0.043 m and δ<1.25 accuracy of 91.5% on ClearGrasp, with zero spillage during 0.5 m/s liquid transport (hu2026transgraspnetphysicallyand pages 6-7). A separate edge-aware perception pipeline for transparent labware achieves a Boundary F-score of 97.80 on a 21-category LabGlass-IS dataset (3,485 images, 6,099 instances), running at 140.85 FPS, with 93.3% collision-avoidance success in real-robot trials but a mean 3D centroid error of 38.0 mm (max 60.5 mm), primarily along the depth axis (ding2608fromtransparentlabware pages 1-2, ding2608fromtransparentlabware pages 5-7, ding2608fromtransparentlabware pages 7-8). The 38 mm depth error is acceptable for collision avoidance but far too large for precision grasping—this is an open gap.

---

## 4. Vision-Language-Action (VLA) and Foundation Models for Manipulation

### 4.1 Current Performance

The following table summarizes VLA benchmark performance:

| Model | Parameters | SimplerEnv Google Robot (VM/VA %) | SimplerEnv WidowX (%) | LIBERO-10 (%) | VLA-Arena robustness | Fine-tuning data | Key limitation |
|---|---:|---:|---:|---:|---|---|---|
| OpenVLA | 7B | 32.7 / 40.0 | 1.0 | 53.7 | OpenVLA-OFT fell to 0% with L1 static distractors; vanilla OpenVLA lost most L0 performance (liang2026pixelvlaadvancingpixellevel pages 6-8, gu2026safemultitaskfailure pages 17-19, zhang2025vlaarenaanopensource pages 6-7) | Bridge v2 + Fractal | Slow inference and weak out-of-distribution robustness |
| π0 (Pi-Zero) | 3B | 54.5 / 54.8 | 27.1 | 85.2 | Retained 70% success with L1 dynamic distractors and generally led evaluated architectures (liang2026pixelvlaadvancingpixellevel pages 6-8, gu2026safemultitaskfailure pages 17-19, zhang2025vlaarenaanopensource pages 6-7) | Proprietary large-scale corpus | Expensive training/inference; reproducibility is constrained by proprietary data |
| Octo-Base | 0.1B | 14.6 / 1.6 | 16.0 | 75.1 | Not reported | Open X-Embodiment subset | Lightweight, but markedly lower physical-robot benchmark accuracy (liang2026pixelvlaadvancingpixellevel pages 6-8, liang2026pixelvlaadvancingpixellevel pages 8-10) |
| SmolVLA | 2B | Not reported | Not reported | Not reported | Fell to 0% with L1 static distractors (zheng2026xvlasoftpromptedtransformer pages 9-10, zhang2025vlaarenaanopensource pages 6-7) | Not reported | Fragile under distribution shift |
| RT-1-X | Not reported | 49.4 / 36.9 | 1.1 | Not reported | Not reported | RT-X dataset | Not open-weight; performance transfers poorly to WidowX (liang2026pixelvlaadvancingpixellevel pages 6-8) |
| PixelVLA | ~7B | 61.4 / 50.1 | 55.1 grasp score; 16.7 task-success score | 86.7 | Not reported | Pixel-160K: 160,000 demonstrations | Requires pixel-level supervision and extensive post-training (liang2026pixelvlaadvancingpixellevel pages 8-10) |


*Table: Comparison of major VLA models on manipulation benchmarks reported in 2025–2026. The results expose substantial embodiment-transfer and distribution-shift weaknesses despite strong simulated benchmark scores.*

State-of-the-art VLAs achieve only 30–60% success when deployed out-of-the-box on real robots with unseen instructions (gu2026safemultitaskfailure pages 1-2, gu2026safemultitaskfailure pages 2-4). π0 leads at 85.2% on LIBERO-10 and 54.5% on the Google Robot benchmark, while OpenVLA achieves 32.7–53.7% depending on setting (liang2026pixelvlaadvancingpixellevel pages 6-8, gu2026safemultitaskfailure pages 17-19). Crucially, VLA-Arena robustness evaluations show that SmolVLA and OpenVLA-OFT drop to 0% success with static distractors at difficulty level L1, while π0 retains ~70% with dynamic distractors (zhang2025vlaarenaanopensource pages 6-7).

Fine-tuning requirements remain substantial: PixelVLA uses 160,000 demonstrations and trains for 200K+ steps on multiple A100 GPUs (liang2026pixelvlaadvancingpixellevel pages 8-10). X-VLA-0.9B was trained on 290K episodes from seven data sources (zheng2026xvlasoftpromptedtransformer pages 9-10). VLA-Arena fine-tuning uses 50 trajectories per task at the "Large" scale (zhang2025vlaarenaanopensource pages 1-2, zhang2025vlaarenaanopensource pages 6-7).

### 4.2 The Honest 2026 Answer

**Yes, scripted motion primitives plus fiducials still beat learned policies for repetitive lab tasks in 2026.** The evidence supports this conclusion clearly:

- VLA out-of-box success on unseen tasks is 30–60% (gu2026safemultitaskfailure pages 1-2), far below the >99% per-operation reliability needed for overnight SDL campaigns (rupnow2024aselfdrivinglaboratory pages 101-107).
- Fine-tuning on lab-specific data requires hundreds to thousands of demonstrations and multi-GPU training.
- SAFE-CHEM demonstrates that even with ensemble-based uncertainty-aware switching, insertion success reaches only 68% with learned policies (jones2608safechemuncertaintyawarepolicy pages 7-8), while scripted rule-based backup controllers provide the safety net.
- No VLA has been deployed in a real SDL for production chemistry.

**The crossover will occur** when VLAs can be fine-tuned with ~50 demonstrations per task on a single GPU (as VLA-Arena's protocol suggests is becoming possible) and when failure detection + recovery (SAFE, SAFE-CHEM) matures sufficiently to provide >99% composite task reliability. This crossover is plausibly 2–3 years away for simple pick-and-place, longer for dexterous manipulation.

### 4.3 Failure Detection for VLAs

SAFE monitors internal VLA latent features and achieves 86.76% ROC-AUC (seen tasks) and 64.16–88.42% (unseen tasks) for failure detection on real robots, with <1 ms overhead (gu2026safemultitaskfailure pages 9-11, gu2026safemultitaskfailure pages 6-7). SAFE-CHEM uses ensemble variance from BC-RNN policies with kernel density estimation thresholds, improving lift success from 75.7% (single policy) to 99.3% (ensemble + switching) and pick-and-place from 67.7% to 98.3%, though insertion remains at 68% (jones2608safechemuncertaintyawarepolicy pages 7-8, jones2608safechemuncertaintyawarepolicy pages 5-6).

---

## 5. Reliability, Error Recovery, and Remote Operation

### 5.1 Failure Modes

The literature identifies failure modes at three levels (cheng2026towardshumanledagentdriven pages 11-13):
- **Execution:** clogged tips, under-delivered reagents, incomplete door closures, crooked plate placement, instrument malfunctions, dropped or tilted glassware, gripper slip
- **State/Identity:** contamination, carryover, reagent degradation, sample swaps, barcode errors
- **Measurement/Data:** readout drift, batch effects, missing metadata, "silent failures" where an apparently successful run yields invalid results

Ada's failure analysis found the mixing station most unreliable (29.8% of issues), with leading causes being instrument failure (23.2%), software error (17.2%), and slide handling (15.2%) (rupnow2024aselfdrivinglaboratory pages 101-107).

### 5.2 Recovery Architectures

**Uncertainty-aware policy switching (SAFE-CHEM):** Ensemble variance triggers transfer from learned to rule-based backup controllers, achieving up to 99.3% task success while reducing safety violations. Validated via zero-shot sim-to-real transfer on a Franka Production 3 (jones2608safechemuncertaintyawarepolicy pages 7-8, jones2608safechemuncertaintyawarepolicy pages 2-4, jones2608safechemuncertaintyawarepolicy pages 1-2).

**Verification-first autonomy (Cheng et al. 2026):** Proposes layered enforcement—pre-execution screening, execution-time sandboxing with hard bounds on physical parameters, real-time telemetry, and automatic pauses/aborts when deviations exceed validated thresholds. Post-execution provenance and QC artifacts complete the framework (cheng2026towardshumanledagentdriven pages 8-11, cheng2026towardshumanledagentdriven pages 11-13, cheng2026towardshumanledagentdriven pages 7-8, cheng2026towardshumanledagentdriven pages 15-16).

**LLM-assisted planning with formal verification (MaCoPlanner):** Compiles equipment manuals into typed intermediate representations, generates plans via VLM, then verifies with LTL + Safety FSM before execution. Achieves 97.3% safety-clause compliance and 2.7% violation rate, with iterative repair when violations are detected (xin2026macoplannerllmassistedmanualcompiled pages 1-2, xin2026macoplannerllmassistedmanualcompiled pages 11-12).

**ROS 2 orchestration (Wang et al.):** Modular, distributed control framework with asynchronous operations. PLC handles safety-critical functions (pumping, venting, interlocking) via ladder logic, while ROS 2 coordinates higher-level workflow (wang2509orchestrationofheterogeneous pages 6-9, wang2509orchestrationofheterogeneous pages 9-12).

### 5.3 Safety Interlocks

The KUKA KMR-iiwa arm uses collision detection that stops motion at 30 N detected force (lunt2024aroboticworkflow pages 49-57). For environments with hot furnaces or hazardous powders, the literature recommends PLC-managed interlocks for safety-critical operations (valves, vacuum, power supply) with ROS 2 handling only higher-level orchestration (wang2509orchestrationofheterogeneous pages 6-9, wang2509orchestrationofheterogeneous pages 9-12). Cooper's 2026 work with GPT-5.1 shows that LLM reasoning is ~35× faster and ~1,900× cheaper than human expert reasoning, but produces "some costly silent errors, logical inconsistencies, and apparent memory limitations," supporting the need for formal verification layers rather than trusting LLM planners alone (dai2024autonomousmobilerobots pages 6-7).

---

## 6. Gap Analysis: Ranked Research Opportunities for a Small University Lab

Based on the evidence above, the following 12 research contributions are identified as both unsolved and tractable for BYU's setup (one PiPER arm, wrist camera, existing gantry/furnace/printer/tester infrastructure, Bayesian optimization expertise, cloud infrastructure).

### Tier 1: High-Impact, Low Competition, Directly Tractable

**Gap 1. Quantitative reliability characterization of a sub-$5k arm for SDL tasks.**
- *Claim:* First published positional repeatability, thermal drift, payload-at-extension, and backlash characterization of the AgileX PiPER (or comparable ~$2.5k arm) under laboratory conditions relevant to SDLs.
- *Experiment:* Systematic measurement of end-effector pose error vs. payload, reach, temperature, and cycle count using a laser tracker or dial indicator; benchmark against fiducial-corrected vs. open-loop performance.
- *Venue:* HardwareX or Digital Discovery.
- *Failure mode:* Trivial to execute but could be scooped if AgileX or another group publishes first. Move fast.

**Gap 2. Vision-corrected manipulation primitives for a low-cost arm: closing the repeatability gap.**
- *Claim:* Eye-in-hand fiducial-based visual servoing (ArUco/AprilTag) on a sub-$5k arm achieves <0.5 mm positioning accuracy sufficient for vial insertion, crucible transfer, and electrode cell loading.
- *Experiment:* Attach camera to PiPER wrist, implement look-then-move and visual servoing loops, measure accuracy across 6+ SDL-relevant tasks, compare open-loop vs. corrected.
- *Venue:* IEEE Robotics and Automation Letters (RA-L) or Digital Discovery.
- *Risk:* Many robotics groups could do this; the SDL-specific task set and frugal hardware angle provide differentiation.

**Gap 3. First published MTBI for an arm-based SDL with transparent failure logging.**
- *Claim:* Systematic measurement and open publication of mean-time-between-intervention, failure taxonomy, and recovery statistics for a low-cost arm operating in a materials-science SDL over >500 operation cycles.
- *Experiment:* Instrument your PiPER + furnace/printer/tester workflow with structured telemetry (per Cheng et al.'s framework), run extended campaigns, classify and publish all failures.
- *Venue:* Digital Discovery or Nature Communications (if coupled with a materials discovery result).
- *Risk:* Low competition—no SDL paper reports MTBI for the arm specifically (rupnow2024aselfdrivinglaboratory pages 101-107, dai2024autonomousmobilerobots pages 7-8). This is a gap the community explicitly needs filled.

### Tier 2: High-Impact, Moderately Competitive

**Gap 4. Transparent and metallic object pose estimation for SDL labware with a monocular wrist camera.**
- *Claim:* A fine-tuned depth-completion or learned pose estimation pipeline (building on TransGraspNet/FoundationPose) achieves <5 mm 3D centroid error on quartz crucibles, metal powder containers, and glass vials using only a monocular RGB camera—eliminating the need for RGB-D depth that fails on transparent/specular surfaces.
- *Experiment:* Collect a small dataset of SDL-specific labware, fine-tune existing models, benchmark against RealSense D435i baseline.
- *Venue:* ICRA or CoRL 2027.
- *Risk:* TransGraspNet (hu2026transgraspnetphysicallyand pages 6-7) and the LabGlass-IS pipeline (ding2608fromtransparentlabware pages 1-2) are active competitors; differentiation via metals/powders and monocular-only constraint is key.

**Gap 5. ROS 2 + Bayesian optimization integration package for heterogeneous SDL orchestration.**
- *Claim:* An open-source ROS 2 package that orchestrates heterogeneous SDL hardware (arm, furnace, printer, tester) with integrated Bayesian optimization, structured telemetry, and cloud-accessible experiment queuing.
- *Experiment:* Demonstrate closed-loop optimization of a materials property (e.g., alloy composition → tensile strength) using the PiPER arm as the transfer layer, with remote users submitting experiments via web interface.
- *Venue:* Journal of Open Source Software (JOSS) + a materials venue for the application.
- *Risk:* Wang et al.'s ROS 2 framework (wang2509orchestrationofheterogeneous pages 1-3, wang2509orchestrationofheterogeneous pages 6-9) is a direct precedent but lacks BO integration and cloud access.

**Gap 6. Uncertainty-aware policy switching for SDL manipulation on a low-cost arm.**
- *Claim:* SAFE-CHEM-style ensemble switching (jones2608safechemuncertaintyawarepolicy pages 7-8) works on a sub-$5k arm with <50 demonstration trajectories per task, achieving >95% success on SDL-specific pick-place-insert tasks.
- *Experiment:* Collect demonstrations via teleoperation on PiPER, train BC-RNN ensemble, benchmark switching vs. single policy vs. scripted primitives.
- *Venue:* CoRL or RSS workshop → full paper.
- *Risk:* The Liverpool/Pizzuto group is the obvious competitor; your angle is the frugal hardware and materials-science tasks.

### Tier 3: High-Impact but More Competitive or Longer-Term

**Gap 7. VLA fine-tuning for SDL tasks: how many demonstrations are actually needed?**
- *Claim:* Fine-tuning OpenVLA or SmolVLA on <100 SDL-specific demonstrations (vial transfer, crucible loading, powder scooping) on a single consumer GPU achieves >80% task success, characterizing the data-efficiency frontier for lab manipulation.
- *Experiment:* Collect 10/30/50/100 demonstrations per task, fine-tune with LoRA, benchmark against scripted primitives.
- *Venue:* NeurIPS or ICML workshop → Digital Discovery.
- *Risk:* VLA fine-tuning is extremely crowded (liang2026pixelvlaadvancingpixellevel pages 6-8, liang2026pixelvlaadvancingpixellevel pages 8-10, zheng2026xvlasoftpromptedtransformer pages 9-10, zhang2025vlaarenaanopensource pages 1-2); the SDL-specific task domain is the differentiator.

**Gap 8. Digital twin pre-flight collision checking for remote SDL operation.**
- *Claim:* A URDF-based digital twin of the SDL workcell, synchronized with the physical arm via ROS 2, catches >95% of collision trajectories before execution, enabling safe remote operation by non-expert users.
- *Experiment:* Build digital twin in MoveIt2/Isaac Sim, implement pre-flight trajectory validation, measure collision detection rate and false-positive rate across diverse experiment plans.
- *Venue:* IEEE CASE or Journal of Laboratory Automation.
- *Risk:* Digital twins for manufacturing are common; the SDL-specific safety and remote-operation angle is novel.

**Gap 9. Cloud-operated frugal SDL with the PiPER arm as the manipulation layer.**
- *Claim:* First demonstration of a remotely accessible, cloud-controlled SDL where a sub-$3k arm performs all sample transfers for a closed-loop materials optimization campaign, operated by users who are not physically present.
- *Experiment:* Build web interface, run multi-day campaign with remote users (e.g., collaborators at another institution), report uptime, intervention rate, and optimization convergence.
- *Venue:* Matter or Digital Discovery.
- *Risk:* Emerald Cloud Labs and Strateos exist commercially; your differentiator is the open-hardware, frugal, academic angle and the structural materials domain.

**Gap 10. Powder handling with vision feedback on a low-cost arm.**
- *Claim:* Radulov et al.'s vision-guided adaptive scooping (radulov2026visionguidedadaptivescooping pages 4-6, radulov2026visionguidedadaptivescooping pages 6-7) can be replicated on a sub-$5k arm with a wrist-mounted camera (instead of external camera), achieving comparable weighing accuracy (<3 mg error) for metal powders relevant to additive manufacturing.
- *Experiment:* Adapt the color-matching fill-estimation approach to wrist-mounted view, test on 5+ metal powders, benchmark against Radulov's 1.93 mg result.
- *Venue:* Digital Discovery.
- *Risk:* Direct comparison with the Cooper/Pizzuto group's system; your angle is frugal hardware + AM-relevant metal powders.

**Gap 11. Benchmarking fiducial vs. learned pose estimation for SDL labware.**
- *Claim:* Systematic comparison of AprilTag/ArUco fiducials, FoundationPose, and MegaPose for localizing common SDL objects (vials, crucibles, well plates, electrode cells) using an eye-in-hand camera, reporting accuracy, latency, robustness to occlusion, and setup time.
- *Experiment:* Standard accuracy evaluation on a set of 10+ SDL labware items, measured with ground-truth poses from a calibration board.
- *Venue:* ICRA or RA-L.
- *Risk:* Pose estimation benchmarking is competitive; the SDL-specific labware angle (especially transparent + metallic) is the differentiator.

**Gap 12. LLM-verified experiment plans for SDL safety.**
- *Claim:* Adapting MaCoPlanner-style LTL + FSM verification (xin2026macoplannerllmassistedmanualcompiled pages 1-2, xin2026macoplannerllmassistedmanualcompiled pages 11-12) to SDL experiment plans—checking that proposed arm trajectories respect furnace temperature interlocks, powder containment constraints, and chemical compatibility rules before execution.
- *Experiment:* Encode your SDL's safety rules as LTL specifications, implement verification layer in ROS 2, measure violation rate across 100+ generated experiment plans.
- *Venue:* Lab on a Chip or CASE.
- *Risk:* Requires formal methods expertise; MaCoPlanner only demonstrated in simulation on industrial panels.

### Priority Ranking for BYU

1. **Gap 3** (MTBI characterization) — lowest competition, highest community need, directly publishable
2. **Gap 1** (arm characterization) — fast to execute, establishes baseline for all subsequent work
3. **Gap 2** (vision-corrected primitives) — essential enabling technology for everything else
4. **Gap 5** (ROS 2 + BO package) — leverages existing expertise, high reuse value
5. **Gap 9** (cloud-operated frugal SDL) — leverages Vertical Cloud Lab branding and cloud infrastructure
6. **Gap 10** (powder handling) — directly relevant to LPBF/AM workflow
7. **Gap 4** (transparent/metallic pose estimation) — robotics venue publication
8. **Gap 6** (uncertainty-aware switching) — bridges to learned policies
9. **Gap 8** (digital twin pre-flight) — enables safe remote operation
10. **Gap 7** (VLA fine-tuning for SDL) — high visibility but crowded
11. **Gap 11** (fiducial vs. learned benchmark) — useful but potentially scooped
12. **Gap 12** (LLM-verified plans) — highest technical bar, longest timeline

### What Is Already Crowded (Avoid as Primary Focus)

- General VLA architecture improvements (massive competition from Physical Intelligence, Google DeepMind, etc.)
- Bayesian optimization algorithms for SDL (well-covered by Aspuru-Guzik, Cooper, and others)
- LLM-as-scientist for experiment design (Cooper's 2026 GPT-5.1 benchmark sets a very high bar)
- General transparent object grasping (active CV competition; only the SDL-specific angle is viable)

### Summary

The state of the art in 2026 is that 6-DOF arms in SDLs serve primarily as flexible inter-station transfer agents, with all deployed systems using expensive industrial arms (KUKA, ABB, Franka) rather than sub-$5k research arms. Eye-in-hand vision with RGB-D cameras achieves 86–96% grasp success on transparent labware, but depth errors of 38 mm remain problematic for precision tasks. VLA models achieve 30–60% out-of-box success on unseen tasks, far below the >99% per-operation reliability required for unattended SDL operation; scripted primitives with fiducial correction remain the pragmatic choice. The most impactful and least crowded contributions for a small university lab center on transparent reliability reporting (MTBI), low-cost arm characterization, vision-corrected manipulation primitives, and open ROS 2 orchestration packages—work that provides the infrastructure the SDL community needs but that flagship groups have little incentive to publish.

References

1. (dai2024autonomousmobilerobots pages 6-7): Tianwei Dai, Sriram Vijayakrishnan, Filip T. Szczypiński, Jean-François Ayme, Ehsan Simaei, Thomas Fellowes, Rob Clowes, Lyubomir Kotopanov, Caitlin E. Shields, Zhengxue Zhou, John W. Ward, and Andrew I. Cooper. Autonomous mobile robots for exploratory synthetic chemistry. Nature, 635(8040):890-897, Nov 2024. URL: https://doi.org/10.1038/s41586-024-08173-7, doi:10.1038/s41586-024-08173-7. This article has 336 citations and is from a highest quality peer-reviewed journal.

2. (dai2024autonomousmobilerobots pages 2-3): Tianwei Dai, Sriram Vijayakrishnan, Filip T. Szczypiński, Jean-François Ayme, Ehsan Simaei, Thomas Fellowes, Rob Clowes, Lyubomir Kotopanov, Caitlin E. Shields, Zhengxue Zhou, John W. Ward, and Andrew I. Cooper. Autonomous mobile robots for exploratory synthetic chemistry. Nature, 635(8040):890-897, Nov 2024. URL: https://doi.org/10.1038/s41586-024-08173-7, doi:10.1038/s41586-024-08173-7. This article has 336 citations and is from a highest quality peer-reviewed journal.

3. (dai2024autonomousmobilerobots pages 7-8): Tianwei Dai, Sriram Vijayakrishnan, Filip T. Szczypiński, Jean-François Ayme, Ehsan Simaei, Thomas Fellowes, Rob Clowes, Lyubomir Kotopanov, Caitlin E. Shields, Zhengxue Zhou, John W. Ward, and Andrew I. Cooper. Autonomous mobile robots for exploratory synthetic chemistry. Nature, 635(8040):890-897, Nov 2024. URL: https://doi.org/10.1038/s41586-024-08173-7, doi:10.1038/s41586-024-08173-7. This article has 336 citations and is from a highest quality peer-reviewed journal.

4. (dai2024autonomousmobilerobots pages 9-10): Tianwei Dai, Sriram Vijayakrishnan, Filip T. Szczypiński, Jean-François Ayme, Ehsan Simaei, Thomas Fellowes, Rob Clowes, Lyubomir Kotopanov, Caitlin E. Shields, Zhengxue Zhou, John W. Ward, and Andrew I. Cooper. Autonomous mobile robots for exploratory synthetic chemistry. Nature, 635(8040):890-897, Nov 2024. URL: https://doi.org/10.1038/s41586-024-08173-7, doi:10.1038/s41586-024-08173-7. This article has 336 citations and is from a highest quality peer-reviewed journal.

5. (liu2023transformingorganicchemistry pages 8-10): Chengchun Liu, Yuntian Chen, and Fanyang Mo. Transforming organic chemistry research paradigms: moving from manual efforts to the intersection of automation and artificial intelligence. Nov 2023. URL: https://doi.org/10.1360/nso/20230037, doi:10.1360/nso/20230037. This article has 14 citations.

6. (lunt2024aroboticworkflow pages 49-57): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

7. (lunt2024aroboticworkflow pages 42-49): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

8. (lunt2024aroboticworkflow pages 103-110): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

9. (lunt2024aroboticworkflow pages 125-129): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

10. (radulov2026visionguidedadaptivescooping pages 4-6): Nikola Radulov, Thomas Little, Andrew I. Cooper, and Gabriella Pizzuto. Vision-guided adaptive scooping for powder weighing in autonomous chemistry laboratories. Digital Discovery, 5(5):2120-2127, Jan 2026. URL: https://doi.org/10.1039/d5dd00569h, doi:10.1039/d5dd00569h. This article has 0 citations and is from a peer-reviewed journal.

11. (radulov2026visionguidedadaptivescooping pages 6-7): Nikola Radulov, Thomas Little, Andrew I. Cooper, and Gabriella Pizzuto. Vision-guided adaptive scooping for powder weighing in autonomous chemistry laboratories. Digital Discovery, 5(5):2120-2127, Jan 2026. URL: https://doi.org/10.1039/d5dd00569h, doi:10.1039/d5dd00569h. This article has 0 citations and is from a peer-reviewed journal.

12. (radulov2026visionguidedadaptivescooping pages 3-4): Nikola Radulov, Thomas Little, Andrew I. Cooper, and Gabriella Pizzuto. Vision-guided adaptive scooping for powder weighing in autonomous chemistry laboratories. Digital Discovery, 5(5):2120-2127, Jan 2026. URL: https://doi.org/10.1039/d5dd00569h, doi:10.1039/d5dd00569h. This article has 0 citations and is from a peer-reviewed journal.

13. (radulov2026visionguidedadaptivescooping pages 1-2): Nikola Radulov, Thomas Little, Andrew I. Cooper, and Gabriella Pizzuto. Vision-guided adaptive scooping for powder weighing in autonomous chemistry laboratories. Digital Discovery, 5(5):2120-2127, Jan 2026. URL: https://doi.org/10.1039/d5dd00569h, doi:10.1039/d5dd00569h. This article has 0 citations and is from a peer-reviewed journal.

14. (radulov2026visionguidedadaptivescooping pages 2-3): Nikola Radulov, Thomas Little, Andrew I. Cooper, and Gabriella Pizzuto. Vision-guided adaptive scooping for powder weighing in autonomous chemistry laboratories. Digital Discovery, 5(5):2120-2127, Jan 2026. URL: https://doi.org/10.1039/d5dd00569h, doi:10.1039/d5dd00569h. This article has 0 citations and is from a peer-reviewed journal.

15. (wang2509orchestrationofheterogeneous pages 1-3): Wei-Sheng Wang, Kensei Terashima, and Yoshihiko Takano. Orchestration of heterogeneous experimental machines via ros2 for automated bulk intermetallic synthesis. Science and Technology of Advanced Materials: Methods, Feb 2509. URL: https://doi.org/10.1080/27660400.2025.2611510, doi:10.1080/27660400.2025.2611510. This article has 2 citations.

16. (wang2509orchestrationofheterogeneous pages 6-9): Wei-Sheng Wang, Kensei Terashima, and Yoshihiko Takano. Orchestration of heterogeneous experimental machines via ros2 for automated bulk intermetallic synthesis. Science and Technology of Advanced Materials: Methods, Feb 2509. URL: https://doi.org/10.1080/27660400.2025.2611510, doi:10.1080/27660400.2025.2611510. This article has 2 citations.

17. (wang2509orchestrationofheterogeneous pages 3-6): Wei-Sheng Wang, Kensei Terashima, and Yoshihiko Takano. Orchestration of heterogeneous experimental machines via ros2 for automated bulk intermetallic synthesis. Science and Technology of Advanced Materials: Methods, Feb 2509. URL: https://doi.org/10.1080/27660400.2025.2611510, doi:10.1080/27660400.2025.2611510. This article has 2 citations.

18. (wang2509orchestrationofheterogeneous pages 9-12): Wei-Sheng Wang, Kensei Terashima, and Yoshihiko Takano. Orchestration of heterogeneous experimental machines via ros2 for automated bulk intermetallic synthesis. Science and Technology of Advanced Materials: Methods, Feb 2509. URL: https://doi.org/10.1080/27660400.2025.2611510, doi:10.1080/27660400.2025.2611510. This article has 2 citations.

19. (lunt2024aroboticworkflow pages 11-16): Amy Lunt. A robotic workflow to screen crystal forms using powder x-ray diffraction. Text, Jan 2024. URL: https://doi.org/10.17638/03178518, doi:10.17638/03178518. This article has 0 citations and is from a peer-reviewed journal.

20. (rupnow2024aselfdrivinglaboratory pages 101-107): Connor Rupnow. A self-driving laboratory designed to optimize scalable spray coating of metal solutions. Text, Jan 2024. URL: https://doi.org/10.14288/1.0434661, doi:10.14288/1.0434661. This article has 1 citations and is from a peer-reviewed journal.

21. (rupnow2024aselfdrivinglaboratory pages 21-26): Connor Rupnow. A self-driving laboratory designed to optimize scalable spray coating of metal solutions. Text, Jan 2024. URL: https://doi.org/10.14288/1.0434661, doi:10.14288/1.0434661. This article has 1 citations and is from a peer-reviewed journal.

22. (adam2024theautomatedlab pages 1-3): David Adam. The automated lab of tomorrow. Proceedings of the National Academy of Sciences of the United States of America, Apr 2024. URL: https://doi.org/10.1073/pnas.2406320121, doi:10.1073/pnas.2406320121. This article has 17 citations and is from a highest quality peer-reviewed journal.

23. (dai2024autonomousmobilerobots pages 1-2): Tianwei Dai, Sriram Vijayakrishnan, Filip T. Szczypiński, Jean-François Ayme, Ehsan Simaei, Thomas Fellowes, Rob Clowes, Lyubomir Kotopanov, Caitlin E. Shields, Zhengxue Zhou, John W. Ward, and Andrew I. Cooper. Autonomous mobile robots for exploratory synthetic chemistry. Nature, 635(8040):890-897, Nov 2024. URL: https://doi.org/10.1038/s41586-024-08173-7, doi:10.1038/s41586-024-08173-7. This article has 336 citations and is from a highest quality peer-reviewed journal.

24. (lo2023reviewoflowcost pages 2-5): Stanley Lo, Sterling Baird, Joshua Schrier, Ben Blaiszik, Sergei Kalinin, Helen Tran, Taylor Sparks, and Alán Aspuru-Guzik. Review of low-cost self-driving laboratories: the "frugal twin" concept. Sep 2023. URL: https://doi.org/10.26434/chemrxiv-2023-6z9mq, doi:10.26434/chemrxiv-2023-6z9mq. This article has 4 citations.

25. (lo2023reviewoflowcost pages 14-16): Stanley Lo, Sterling Baird, Joshua Schrier, Ben Blaiszik, Sergei Kalinin, Helen Tran, Taylor Sparks, and Alán Aspuru-Guzik. Review of low-cost self-driving laboratories: the "frugal twin" concept. Sep 2023. URL: https://doi.org/10.26434/chemrxiv-2023-6z9mq, doi:10.26434/chemrxiv-2023-6z9mq. This article has 4 citations.

26. (lo2023reviewoflowcost pages 12-14): Stanley Lo, Sterling Baird, Joshua Schrier, Ben Blaiszik, Sergei Kalinin, Helen Tran, Taylor Sparks, and Alán Aspuru-Guzik. Review of low-cost self-driving laboratories: the "frugal twin" concept. Sep 2023. URL: https://doi.org/10.26434/chemrxiv-2023-6z9mq, doi:10.26434/chemrxiv-2023-6z9mq. This article has 4 citations.

27. (lo2023reviewoflowcost pages 26-28): Stanley Lo, Sterling Baird, Joshua Schrier, Ben Blaiszik, Sergei Kalinin, Helen Tran, Taylor Sparks, and Alán Aspuru-Guzik. Review of low-cost self-driving laboratories: the "frugal twin" concept. Sep 2023. URL: https://doi.org/10.26434/chemrxiv-2023-6z9mq, doi:10.26434/chemrxiv-2023-6z9mq. This article has 4 citations.

28. (lo2023reviewoflowcost pages 5-7): Stanley Lo, Sterling Baird, Joshua Schrier, Ben Blaiszik, Sergei Kalinin, Helen Tran, Taylor Sparks, and Alán Aspuru-Guzik. Review of low-cost self-driving laboratories: the "frugal twin" concept. Sep 2023. URL: https://doi.org/10.26434/chemrxiv-2023-6z9mq, doi:10.26434/chemrxiv-2023-6z9mq. This article has 4 citations.

29. (hu2026transgraspnetphysicallyand pages 6-7): Hai-Ling Hu, Mingyi Zhu, Yiquan An, Yifei Tian, Tianyou Zuo, and Lifeng Zhou. Transgraspnet: physically and geometrically consistent manipulation of transparent labware. ArXiv, Jul 2026. URL: https://doi.org/10.48550/arxiv.2607.29567, doi:10.48550/arxiv.2607.29567. This article has 0 citations.

30. (vaggelis20256dobjectpose pages 34-38): O Vaggelis. 6d object pose estimation: literature review and model-free mask generation pipeline. Unknown journal, 2025.

31. (vaggelis20256dobjectpose pages 52-54): O Vaggelis. 6d object pose estimation: literature review and model-free mask generation pipeline. Unknown journal, 2025.

32. (ding2608fromtransparentlabware pages 1-2): From Transparent Labware Segmentation to Collision Avoidance: A Real-Time Edge-Aware Perception Pipeline This article has 0 citations.

33. (ding2608fromtransparentlabware pages 5-7): From Transparent Labware Segmentation to Collision Avoidance: A Real-Time Edge-Aware Perception Pipeline This article has 0 citations.

34. (ding2608fromtransparentlabware pages 7-8): From Transparent Labware Segmentation to Collision Avoidance: A Real-Time Edge-Aware Perception Pipeline This article has 0 citations.

35. (liang2026pixelvlaadvancingpixellevel pages 6-8): Wenqi Liang, Gan Sun, Yao He, Jiahua Dong, Suyan Dai, Ivan Laptev, Salman Khan, and Yang Cong. Pixelvla: advancing pixel-level understanding in vision-language-action model. ArXiv, Nov 2026. URL: https://doi.org/10.48550/arxiv.2511.01571, doi:10.48550/arxiv.2511.01571. This article has 20 citations.

36. (gu2026safemultitaskfailure pages 17-19): Qiao Gu, Yuanliang Ju, Shengxiang Sun, Igor Gilitschenski, Haruki Nishimura, Masha Itkina, and Florian Shkurti. Safe: multitask failure detection for vision-language-action models. ArXiv, Jun 2026. URL: https://doi.org/10.48550/arxiv.2506.09937, doi:10.48550/arxiv.2506.09937. This article has 82 citations.

37. (zhang2025vlaarenaanopensource pages 6-7): Borong Zhang, Jiahao Li, Jiacheng Shen, Yishuai Cai, Yuhao Zhang, Yuanpei Chen, Juntao Dai, Jiaming Ji, and Yaodong Yang. Vla-arena: an open-source framework for benchmarking vision-language-action models. ArXiv, Dec 2025. URL: https://doi.org/10.48550/arxiv.2512.22539, doi:10.48550/arxiv.2512.22539. This article has 29 citations.

38. (liang2026pixelvlaadvancingpixellevel pages 8-10): Wenqi Liang, Gan Sun, Yao He, Jiahua Dong, Suyan Dai, Ivan Laptev, Salman Khan, and Yang Cong. Pixelvla: advancing pixel-level understanding in vision-language-action model. ArXiv, Nov 2026. URL: https://doi.org/10.48550/arxiv.2511.01571, doi:10.48550/arxiv.2511.01571. This article has 20 citations.

39. (zheng2026xvlasoftpromptedtransformer pages 9-10): Jinliang Zheng, Jianxiong Li, Zhihao Wang, Dongxiu Liu, Xirui Kang, Yuchun Feng, Yinan Zheng, Jiayi Zou, Yilun Chen, Jia Zeng, Ya-Qin Zhang, Jiang-Miao Pang, Jingjing Liu, Tai Wang, and Xianyuan Zhan. X-vla: soft-prompted transformer as scalable cross-embodiment vision-language-action model. ArXiv, Oct 2026. URL: https://doi.org/10.48550/arxiv.2510.10274, doi:10.48550/arxiv.2510.10274. This article has 260 citations.

40. (gu2026safemultitaskfailure pages 1-2): Qiao Gu, Yuanliang Ju, Shengxiang Sun, Igor Gilitschenski, Haruki Nishimura, Masha Itkina, and Florian Shkurti. Safe: multitask failure detection for vision-language-action models. ArXiv, Jun 2026. URL: https://doi.org/10.48550/arxiv.2506.09937, doi:10.48550/arxiv.2506.09937. This article has 82 citations.

41. (gu2026safemultitaskfailure pages 2-4): Qiao Gu, Yuanliang Ju, Shengxiang Sun, Igor Gilitschenski, Haruki Nishimura, Masha Itkina, and Florian Shkurti. Safe: multitask failure detection for vision-language-action models. ArXiv, Jun 2026. URL: https://doi.org/10.48550/arxiv.2506.09937, doi:10.48550/arxiv.2506.09937. This article has 82 citations.

42. (zhang2025vlaarenaanopensource pages 1-2): Borong Zhang, Jiahao Li, Jiacheng Shen, Yishuai Cai, Yuhao Zhang, Yuanpei Chen, Juntao Dai, Jiaming Ji, and Yaodong Yang. Vla-arena: an open-source framework for benchmarking vision-language-action models. ArXiv, Dec 2025. URL: https://doi.org/10.48550/arxiv.2512.22539, doi:10.48550/arxiv.2512.22539. This article has 29 citations.

43. (jones2608safechemuncertaintyawarepolicy pages 7-8): L Jones, S Shahzad, A Sana, and G Pizzuto. Safe-chem: uncertainty-aware policy switching for robust robotic chemistry. ArXiv, 2608. URL: https://doi.org/10.48550/arxiv.2608.09303, doi:10.48550/arxiv.2608.09303.

44. (gu2026safemultitaskfailure pages 9-11): Qiao Gu, Yuanliang Ju, Shengxiang Sun, Igor Gilitschenski, Haruki Nishimura, Masha Itkina, and Florian Shkurti. Safe: multitask failure detection for vision-language-action models. ArXiv, Jun 2026. URL: https://doi.org/10.48550/arxiv.2506.09937, doi:10.48550/arxiv.2506.09937. This article has 82 citations.

45. (gu2026safemultitaskfailure pages 6-7): Qiao Gu, Yuanliang Ju, Shengxiang Sun, Igor Gilitschenski, Haruki Nishimura, Masha Itkina, and Florian Shkurti. Safe: multitask failure detection for vision-language-action models. ArXiv, Jun 2026. URL: https://doi.org/10.48550/arxiv.2506.09937, doi:10.48550/arxiv.2506.09937. This article has 82 citations.

46. (jones2608safechemuncertaintyawarepolicy pages 5-6): L Jones, S Shahzad, A Sana, and G Pizzuto. Safe-chem: uncertainty-aware policy switching for robust robotic chemistry. ArXiv, 2608. URL: https://doi.org/10.48550/arxiv.2608.09303, doi:10.48550/arxiv.2608.09303.

47. (cheng2026towardshumanledagentdriven pages 11-13): Wenduo Cheng, Mingqian Ma, Shuaike Shen, Anna Hupalowska, Jennifer E. Rood, Yang Zhang, Gaurav Agrawal, Christine Bakan, Michelle A. Lee, Aviv Regev, and Jian Ma. Towards human-led, agent-driven autonomous laboratories for the life sciences. Unknown journal, Aug 2026. URL: https://doi.org/10.20944/preprints202608.0273.v1, doi:10.20944/preprints202608.0273.v1.

48. (jones2608safechemuncertaintyawarepolicy pages 2-4): L Jones, S Shahzad, A Sana, and G Pizzuto. Safe-chem: uncertainty-aware policy switching for robust robotic chemistry. ArXiv, 2608. URL: https://doi.org/10.48550/arxiv.2608.09303, doi:10.48550/arxiv.2608.09303.

49. (jones2608safechemuncertaintyawarepolicy pages 1-2): L Jones, S Shahzad, A Sana, and G Pizzuto. Safe-chem: uncertainty-aware policy switching for robust robotic chemistry. ArXiv, 2608. URL: https://doi.org/10.48550/arxiv.2608.09303, doi:10.48550/arxiv.2608.09303.

50. (cheng2026towardshumanledagentdriven pages 8-11): Wenduo Cheng, Mingqian Ma, Shuaike Shen, Anna Hupalowska, Jennifer E. Rood, Yang Zhang, Gaurav Agrawal, Christine Bakan, Michelle A. Lee, Aviv Regev, and Jian Ma. Towards human-led, agent-driven autonomous laboratories for the life sciences. Unknown journal, Aug 2026. URL: https://doi.org/10.20944/preprints202608.0273.v1, doi:10.20944/preprints202608.0273.v1.

51. (cheng2026towardshumanledagentdriven pages 7-8): Wenduo Cheng, Mingqian Ma, Shuaike Shen, Anna Hupalowska, Jennifer E. Rood, Yang Zhang, Gaurav Agrawal, Christine Bakan, Michelle A. Lee, Aviv Regev, and Jian Ma. Towards human-led, agent-driven autonomous laboratories for the life sciences. Unknown journal, Aug 2026. URL: https://doi.org/10.20944/preprints202608.0273.v1, doi:10.20944/preprints202608.0273.v1.

52. (cheng2026towardshumanledagentdriven pages 15-16): Wenduo Cheng, Mingqian Ma, Shuaike Shen, Anna Hupalowska, Jennifer E. Rood, Yang Zhang, Gaurav Agrawal, Christine Bakan, Michelle A. Lee, Aviv Regev, and Jian Ma. Towards human-led, agent-driven autonomous laboratories for the life sciences. Unknown journal, Aug 2026. URL: https://doi.org/10.20944/preprints202608.0273.v1, doi:10.20944/preprints202608.0273.v1.

53. (xin2026macoplannerllmassistedmanualcompiled pages 1-2): MaCoPlanner: LLM-Assisted Manual-Compiled Task Planning with Proactive Safety Verification for Robotic Industrial Panel Operation This article has 0 citations.

54. (xin2026macoplannerllmassistedmanualcompiled pages 11-12): MaCoPlanner: LLM-Assisted Manual-Compiled Task Planning with Proactive Safety Verification for Robotic Industrial Panel Operation This article has 0 citations.
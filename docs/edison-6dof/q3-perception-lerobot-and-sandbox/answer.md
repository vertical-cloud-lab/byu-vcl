# Low-Cost SDL Sandbox with AgileX PiPER: Perception, Fiducials, Learned Policies, Contact Tasks, Software, Design, and Positioning

## 1. Perception for Specular Metal, Transparent Glass, and Thin Planar Parts

### 1.1 Foundation Model Pose Estimators: BOP Benchmark Results

The current state of the art in model-free 6-DOF pose estimation is dominated by FoundationPose, MegaPose, SAM-6D, and GigaPose, all benchmarked on BOP (Benchmark for 6D Object Pose). Reproduced mean Average Recall (mAR) scores across core BOP datasets are: FoundationPose 67.2–86.2 across LM-O/T-LESS/TUD-L/IC-BIN/YCB-V; SAM-6D 71.1/56.9/88.3/60.4/81.7; GigaPose 41.2/51.0/63.5/33.7/40.5; and MegaPose 55.1/–/68.6/29.2/69.5 (vaggelis20256dobjectpose pages 48-52). These are RGB-only or RGB-D methods requiring only a CAD model or reference views.

**Critically for compute budgets**, per-image inference times vary enormously. GigaPose processes an image in ~0.4–2.1 s; SAM-6D in ~0.8–3.9 s; FoundationPose requires 12.7–68.5 s per image; and MegaPose 11.3–139.4 s (vaggelis20256dobjectpose pages 52-54). FoundationPose requires ~1.3 s per object even after optimization (vaggelis20256dobjectpose pages 52-54). Peak GPU memory ranges from 0.83 GB (FoundPose) to 6.47 GB (GigaPose) to 3.33 GB (MegaPose) per detection (chen2026posegamrobustunseen pages 16-18). **None of these run at interactive rates on a Jetson Orin Nano or RPi 5.** GigaPose at ~1 s coarse + 7 s refined with MegaPose refinement is the closest to feasible on a desktop GPU; on edge hardware, only stop-and-look with a forwarded frame to a remote GPU is practical. For a few-Hz in-the-loop pipeline, a desktop RTX 4070-class GPU is the minimum; an Orin Nano would need INT8 quantization and model distillation that does not yet exist for these architectures.

### 1.2 Specular/Metallic Objects

The IMD benchmark (45 industrial metallic parts, Intel RealSense D405) shows that current methods fail dramatically on metallic objects: BundleTrack achieves 6.61 mm / 8.12° on top-down views but degrades to 32.23 mm / 49.17° at 45° viewing angles due to specular reflection destroying depth and feature matching (ma2025imda6dof pages 6-8). Structured-light cameras produce incomplete depth on shiny surfaces because specular reflection causes IR saturation and inter-reflection (yang2024activeposerefinement pages 1-2). Multi-view scanning with 12 planned views can reduce positional error below 2 mm and angular error below 2° for reflective textureless objects (lee20266dposeestimation pages 1-2).

**For the SDL's aluminum crucibles and polished SEM stubs**: single-shot depth will fail. The practical mitigations are: (a) matte spray coating or anodizing for prototyping, (b) multi-view RGB reconstruction, (c) fiducial tags on fixtures rather than objects, or (d) fixed kinematic seats that eliminate the need for object-level pose estimation entirely.

### 1.3 Transparent Objects

Depth cameras produce incorrect or missing depth on glass vials. GraspNeRF addresses this with sparse multi-view RGB and generalizable NeRF, achieving 86.1% grasping success in simulation (75% transparent, 91.7% specular, 91.7% diffuse) and 88.9% real-world single-object grasping at 11 FPS from 6 views (dai2023graspnerfmultiviewbased6dof pages 5-6, dai2023graspnerfmultiviewbased6dof pages 6-7). ClearGrasp estimates geometry from single RGB and refines depth for top-down 3-DOF grasping of transparent objects (dai2023graspnerfmultiviewbased6dof pages 1-2). Fill level changes the failure mode: liquid acts as an additional refractive layer, shifting apparent geometry and changing weight distribution; empty vials are purely refractive while filled vials add meniscus artifacts.

### 1.4 Thin/Low-Profile Parts (Crucible Lids, Stub Caps)

These are **the hardest case** and essentially unstudied in the pose-estimation literature. Sub-2 mm height parts present minimal silhouette from most viewing angles and near-zero depth contrast. No published method reports reliable 6-DOF pose on parts this thin. The practical solution is **fixture-based**: 3D-printed trays with kinematic nests and AprilTags on the tray, not the part. The arm learns "lid is at tag X + known offset" rather than estimating lid pose directly.

### 1.5 Practical Recommendation

For this SDL, **do not attempt learned pose estimation on the hard objects**. Use fiducial-tagged fixtures for all consumables and reserve learned perception for verification (is the vial present? is the lid seated?). A fixed overhead 12.3 MP camera running a fine-tuned YOLOv8 segmentation model — as demonstrated by HeinSight 4.0 for vial/phase detection (elkhawaldeh2025closedloopvisionguidedexperimental pages 1-3, elkhawaldeh2025closedloopvisionguidedexperimental pages 3-6) — provides sufficient state observation at trivial compute cost.

---

## 2. Fiducial Pose Estimation: How Far AprilTags Get You

### 2.1 Accuracy vs. Distance, Tag Size, and Viewing Angle

AprilTag translational accuracy is governed by the relationship ω·d = f·Δ, where corner detection error d in pixels maps to object-plane error Δ proportional to distance ω and inversely proportional to focal length f (schempp2022highprecisionabsolutepose pages 5-7). At 70 cm standoff with raw AprilTag, Abbas et al. measured mean errors of ~1.0 cm in x and ~0.40 cm in y when the camera optical axis points at the tag center (abbas2019analysisandimprovements pages 9-11). Error increases substantially with lateral displacement and camera yaw: at 70 cm and 20 cm lateral offset with yaw misalignment, x-axis error reaches ~12 cm without correction (abbas2019analysisandimprovements pages 18-20).

**For the IMX477 at 150–500 mm standoff**: With a 6 mm lens (FOV ~63°), a 20 mm tag at 300 mm occupies ~130 pixels across a 4056-pixel sensor width, yielding ~0.15 mm/pixel at the tag plane. With sub-pixel corner detection achieving ~0.1–0.3 px accuracy, translational precision of 0.02–0.05 mm is theoretically achievable — well within the ±0.5 mm placement tolerance. A 16 mm lens narrows the FOV but increases tag pixel coverage proportionally, improving precision. **At 500 mm with a 6 mm lens, the same 20 mm tag occupies ~80 px, degrading precision to ~0.08 mm/pixel — still adequate.**

### 2.2 Pose Flipping / Rotational Ambiguity

Planar tags viewed at near-frontal angles produce two mathematically valid PnP solutions due to planar-geometry symmetry, causing estimates to flip between orientations across consecutive frames (andrews2026improvingapriltagbased pages 13-18). IPPE (Infinitesimal Plane-based Pose Estimation) explicitly returns both candidate poses with reprojection uncertainties, enabling disambiguation (andrews2026improvingapriltagbased pages 13-18, schempp2022highprecisionabsolutepose pages 14-15). Multi-tag bundles eliminate this ambiguity entirely by providing non-coplanar constraints when tags are mounted on different faces or at different heights. **For the SDL, mount tags on fixture sidewalls (not just top surfaces) and use tag bundles for each station.**

### 2.3 Rolling Shutter (IMX477)

The IMX477 is a rolling-shutter sensor with ~30 ms readout time. At typical PiPER end-effector velocities of 100–300 mm/s during transit, this introduces 3–9 mm of geometric distortion across the frame. **Stop-and-look is mandatory**: the arm must halt, settle (50–100 ms for vibration), capture, and compute pose before the final approach. This adds ~200–500 ms per observation but eliminates rolling-shutter error entirely.

### 2.4 Tag Printing and Practicalities

Tags must be printed on matte, flat substrates. Laser printing on matte photo paper and laminating flat provides ~0.05 mm flatness. Glossy substrates cause specular washout under direct lighting — use diffuse LED illumination at 45° to avoid glare. Exposure control matters: blooming in overexposed regions shifts detected corners by up to 0.74 mm (schempp2022highprecisionabsolutepose pages 14-15).

### 2.5 Hand–Eye Calibration

Tsai–Lenz with 25 poses achieves RMS translational residual of 0.08 mm and rotational residual of 0.04° (mannayee2026visionguidedroboticpickandplace pages 8-11). Nonlinear optimization improves to 0.21 mm overall positioning error versus 0.36 mm for Tsai–Lenz under controlled conditions (xiong2026anintegrated3d pages 19-21). **Use ≥20 poses spanning the workspace, recalibrate weekly or after any mechanical change.** Calibration drift from thermal effects and joint wear is the primary long-term degradation mechanism; the literature does not quantify this precisely, but industrial practice suggests recalibration every 1–2 weeks for sub-mm tasks.

---

## 3. Learned Policies via LeRobot: Honest Assessment

### 3.1 What LeRobot Provides

LeRobot (Hugging Face) provides a unified framework with dataset formats (v2/v3), training pipelines for ACT, Diffusion Policy, VQ-BeT, and SmolVLA, plus emerging pi0/pi0.5 ports. It has been used with SO-100/SO-101, Koch, ALOHA, and ViperX arms (karampinas2026robotassistedfeedingtasks pages 49-53). **AgileX PiPER is closely related to the Cobot Magic platform used in RoboMIND** (107k trajectories, 479 tasks, including AgileX Cobot Magic V2.0 as one of four embodiments) (wu2024robomindbenchmarkon pages 3-4). SmolVLA uses a pretrained SmolVLM2 backbone with a ~100M-parameter flow-matching action expert, trainable on an RTX 4070 (8 GB VRAM) (karampinas2026robotassistedfeedingtasks pages 57-60).

### 3.2 Demonstration Requirements and Success Rates

**Diffusion Policy** achieves 95% success on real-world Push-T with ~200 proficient-human demonstrations; Square task reaches 98–100% in simulation with 200 demos (chi2025diffusionpolicyvisuomotor pages 8-9, chi2025diffusionpolicyvisuomotor pages 6-7). **ACT** on bimanual insertion with 50 scripted demonstrations achieves only 32% success; with AWE preprocessing, 57% (shi2307waypointbasedimitationlearning pages 4-6). For bimanual peg insertion with 2 mm clearance, Comp-ACT and DIPCOM both achieve 95–100% success, but this is after careful tuning with compliant control (aburub2026learningdiffusionpolicies pages 5-6).

**The honest numbers**: For a precise, low-clearance insertion task comparable to crucible lid press-fit, expect to need **50–200 high-quality teleoperation demonstrations** to reach 80–95% success with ACT or Diffusion Policy. Reaching >99% per-operation reliability — the threshold needed for unattended SDL operation where 100-step campaigns must complete — **is not demonstrated by any learned policy in the literature**. The best published real-world results plateau at 90–96% on precise tasks.

### 3.3 Total Effort Comparison

**Learned policy path**: Build/buy teleoperation rig (~$500–2k for leader arm), collect 50–200 demonstrations per task (2–8 hours of teleoperation time), train on GPU (1–4 hours per policy on RTX 4070), evaluate over 50+ trials, iterate. Total: 1–3 weeks per primitive.

**Scripted primitive path**: Write waypoint sequence with fiducial correction (~1–2 days for a skilled ROS developer), tune compliance parameters (~1 day), validate over 50+ trials. Total: 3–5 days per primitive.

### 3.4 Recommendation: Hybrid Architecture

The honest answer is a **hybrid**: scripted fiducial-corrected primitives for all precision placement and insertion steps, with learned policies reserved for search/approach phases where object locations may vary. A learned policy handles coarse localization and approach; a scripted primitive with force-guarded insertion handles the final seat. This matches the architecture implicitly used by successful SDL deployments.

---

## 4. Contact-Rich Steps Without F/T Sensor

### 4.1 Joint-Current Sensing

The PiPER's CAN-bus servo motors report current draw, which provides a crude proxy for external torque. Resolution is limited (~0.1–0.5 N·m depending on gear ratio and friction), but sufficient for detecting hard contact (jamming) during insertion. A current-threshold guard can trigger retract-and-retry. This is **not sufficient for controlled force application** — only for collision detection.

### 4.2 Compliant Fixtures: The Primary Strategy

For a low-cost arm with ±0.5 mm repeatability and no wrist F/T sensor, **passive compliance in the fixture is the correct answer**. Design principles:
- **Lead-in chamfers**: 1–2 mm chamfer at 15–30° on all receiving features converts ±0.5 mm lateral error into guided insertion
- **Kinematic seats**: V-grooves or 3-point contacts for vials; tapered bores for crucibles
- **Funnel tolerances**: The fixture clearance should be ≥2× the arm's worst-case repeatability (i.e., ≥1.0 mm unilateral clearance for the PiPER's claimed 0.1 mm repeatability under thermal drift)
- **Remote Center of Compliance (RCC)**: A printed or elastomeric RCC adapter between gripper and part provides ~1–2 mm passive lateral compliance, effectively relaxing insertion clearance by that amount

The Bambu A1 mini can print PLA/PETG fixtures with ±0.1 mm dimensional accuracy, enabling rapid iteration on chamfer angles and clearances.

### 4.3 Peg-in-Hole Success vs. Clearance

Classical peg-in-hole literature establishes that insertion success drops precipitously when clearance falls below the arm's position uncertainty. With 0.5 mm position uncertainty (realistic for PiPER after fiducial correction), a 0.5 mm clearance hole requires active compliance or force feedback. A 1.5 mm clearance hole succeeds >95% with position control alone. **Design all fixtures for ≥1.0 mm clearance and use chamfered lead-ins.**

### 4.4 Tactile Sensing Options

Vision-based tactile sensors are now accessible: DIGIT costs ~$350 commercially ($15 at volume), GelSight Mini ~$549 as a kit, GelSlim 4.0 is fully open-source at ~$122 in materials (liu2602alowcostvisionbased pages 4-6, sipos2409gelslim4.0focusing pages 2-3). A low-cost 3D-printed vision-based tactile gripper (LVTG) achieves 2,400 mm² sensing area at ~$12 (liu2602alowcostvisionbased pages 4-6). For the SDL, tactile sensing is a **valuable addition for the lid press-fit step** — detecting contact force confirms seating — but is not essential if fixture compliance is sufficient.

---

## 5. Prior Art in Code

### 5.1 PiPER Ecosystem

- **`piper_sdk`/`piper_ros`**: Available on GitHub (AgileX Robotics), supports ROS 2 Humble, CAN bus communication. MoveIt 2 support is community-contributed and immature — expect to write custom motion planning wrappers. No official MuJoCo MJCF or URDF for simulation (must create from STEP files).

### 5.2 SDL Orchestration

- **EOS (Experiment Orchestration System)**: Open-source, Python/YAML-based, supports DAG workflows, Bayesian optimization, distributed execution, SiLA 2 integration (angelopoulos2026autonomoussciencelaboratories pages 47-53, angelopoulos2026autonomoussciencelaboratories pages 119-124). **Best-in-class for a new SDL.**
- **AlabOS**: Python-based, demonstrated on autonomous inorganic powder synthesis with three workcells (angelopoulos2026autonomoussciencelaboratories pages 53-58).
- **Bluesky/Ophyd**: Mature data acquisition framework from synchrotron community; excellent for instrument control but not robot-centric.
- **SiLA 2**: Communication standard, not an orchestration framework; useful for instrument interoperability (ren2607pudaanainative pages 10-12).
- **MATTERIX**: Published in Nature Computational Science 2026, uses NVIDIA Isaac Sim/Lab for digital twin of robotics-assisted chemistry lab (ren2607pudaanainative pages 10-12, ren2607pudaanainative pages 12-13). **Not open-source as of this writing.**
- **PyLabRobot**: Open-source Python library for liquid handling (Hamilton, Opentrons); good for pipetting but not arm manipulation.
- **HeinSight 4.0**: Open-source computer vision for SDL monitoring, YOLO-based vessel detection and chemical phase classification (elkhawaldeh2025closedloopvisionguidedexperimental pages 1-3, elkhawaldeh2025closedloopvisionguidedexperimental pages 3-6). **Directly reusable for vial state monitoring.**

### 5.3 Vision Stacks

- **`apriltag_ros`** (ROS 2): Mature, well-tested. **Isaac ROS AprilTag**: GPU-accelerated, faster but requires Jetson.
- **FoundationPose/SAM-6D**: Official code released, but require desktop GPU and are too slow for in-the-loop use.
- **LeRobot**: Active development, Apache 2.0 license, HuggingFace ecosystem.

### 5.4 Simulation

- **Isaac Sim/Lab**: Full-featured but heavy (requires RTX GPU). Used by MATTERIX.
- **MuJoCo**: Lightweight, fast, free. No official PiPER model — **creating one from STEP/URDF is a 1–2 day task**.
- **Gazebo + ros2_control**: Natural fit for ROS 2 but limited contact physics.

### 5.5 Datasets Containing Labware

- **RoboMIND**: 107k trajectories including AgileX Cobot Magic, available in LeRobot format (wu2024robomindbenchmarkon pages 3-4). Contains household manipulation but **not laboratory consumables**.
- **Open X-Embodiment, DROID, BridgeData, AgiBot World**: Contain diverse manipulation but **no labware-specific data**. This is a genuine gap — no existing dataset contains SEM stubs, crucibles, or well plates.

---

## 6. Sandbox Design Specification

### 6.1 Eight Primitive Operations (in implementation order)

1. **Pick-and-place empty 20 mL vial** (rack → station → rack): Easiest grasp, establishes baseline repeatability
2. **Pick-and-place empty 2 mL vial**: Smaller target, tighter grasp tolerance
3. **Pick-and-place SEM stub** (pin mount → holder): Tests specular object handling
4. **Place vial into well plate** (SBS/ANSI format): Tests array indexing precision
5. **Pick-and-place aluminum crucible** (from tray to furnace position): Tests specular + lightweight object
6. **Crucible lid placement** (lid onto crucible, no press): Tests thin-part handling
7. **Crucible lid press-fit**: Contact-rich step, requires compliance
8. **Powder transfer via atomizer**: Contact + containment, highest complexity

### 6.2 Fixture Design Principles

- All fixtures 3D-printed on Bambu A1 mini in PETG (chemical resistance, moderate heat tolerance)
- **20 mm AprilTag on every fixture**, printed on matte label stock, affixed to fixture sidewall
- **2 mm lead-in chamfers** on all receiving features
- **V-groove kinematic seats** for cylindrical vials (self-centering, accommodates diameter variation)
- **Tapered bore** (1° draft) for crucibles
- **Magnetic retention** (embedded 3mm neodymium magnets) for SEM stub holders

### 6.3 Instrumentation and Logging

Log every operation: joint positions (10 Hz), gripper state, camera frames (before/after pick, before/after place), AprilTag detections, operation outcome (success/failure with failure mode taxonomy from LabRobFail), cycle time, ambient temperature. This directly produces the reliability dataset from Query 2: 118 trials per primitive gives a 97.5% lower bound on success rate.

### 6.4 Highest-Value First Publishable Result

**"Reliability-Certified Labware Manipulation on a Sub-$5k Arm"**: Report the empirically measured success rate for each of the 8 primitives over N ≥ 200 trials each, with ISO 9283-style repeatability characterization, thermal drift protocol, and failure taxonomy. **What makes it more than a demo**: (a) release the fixture STL files and ROS 2 nodes, (b) provide the raw reliability dataset with per-trial logs, (c) compare against the published Ada/KUKA failure rates (~1 per 40 samples), and (d) derive a cost-per-reliable-operation metric showing the PiPER's positioning in the SDL design space.

### 6.5 Safety for Powder Transfer

- Conduct powder operations inside a 3D-printed enclosure with HEPA-filtered exhaust
- Use a powder-compatible vacuum gripper or sealed atomizer with check valve
- Implement a mass-balance verification (weigh crucible before/after transfer on an analytical balance in the loop)
- Interlock: arm cannot enter powder zone if enclosure is open

---

## 7. Collaboration and Positioning

### 7.1 MATTERIX and Adjacent Efforts

MATTERIX (Nature Computational Science 2026, Acceleration Consortium) builds digital twins for robotics-assisted chemistry using NVIDIA Isaac Sim and industrial-grade hardware (ren2607pudaanainative pages 10-12, ren2607pudaanainative pages 12-13). The Acceleration Consortium received $200M CAD to advance laboratory automation (angelopoulos2026autonomoussciencelaboratories pages 26-30). These efforts structurally optimize for **capability and generality**: expensive arms, commercial instruments, full-stack simulation.

### 7.2 Where a Low-Cost Sandbox Complements

A PiPER-based SDL contributes what well-funded labs **structurally will not produce**:

1. **Accessible reliability data**: No group with a $100k KUKA cell has incentive to characterize a $3k arm. The community needs reliability curves for low-cost hardware to make informed build-vs-buy decisions.

2. **Open-source fixture library**: 3D-printable kinematic seats for standard labware (SBS plates, DSC crucibles, SEM stubs) are immediately reusable by any group with an FDM printer. MATTERIX fixtures are custom-machined and not shared.

3. **SDL failure modes at the edge**: With ~1.5 kg payload and 626 mm reach, the PiPER operates at the boundary of viability. Documenting exactly where it fails — which operations, at what clearances, after how many hours — is a contribution that validates or refutes the low-cost SDL thesis.

4. **Cloud-operated architecture**: A headless, cloud-orchestrated SDL (EOS or equivalent) running on a PiPER + OT-2 + powder doser + Bambu printer demonstrates that the software infrastructure scales down, which MATTERIX's Isaac Sim dependency does not.

5. **AM-in-the-loop**: Having a Bambu A1 mini as both a fixture source and a potential station (printing custom sample holders, reaction vessels, or calibration artifacts on demand) is a unique capability that no deployed SDL incorporates. The thesis contribution is showing that additive manufacturing closes the loop on fixture design: measure arm accuracy → print compensated fixture → verify → iterate.

### 7.3 What to Avoid

Do not attempt to replicate MATTERIX's scope. Focus on the **reliability characterization** and **open-hardware** contributions. The publishable niche is not "we built an SDL" (many have) but "we characterized whether a $3k arm can reliably operate one, and here is exactly what it takes in fixture design, calibration, and software to make it work — or the evidence that it cannot."

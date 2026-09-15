# Question

Third in a sequential series of high-effort literature queries for a university group
standing up a low-cost, cloud-operated self-driving laboratory (SDL) around an **AgileX
PiPER** class 6-DOF arm (~$2.5–4k, 1.5 kg payload, 626 mm reach, vendor-claimed 0.1 mm
repeatability, CAN bus + `piper_ros` on ROS 2) with a **camera we mount ourselves** —
most likely a Raspberry Pi HQ camera (Sony IMX477, 12.3 MP, C/CS-mount, fixed manual-focus
lens chosen specifically because the lens will not shift like an autofocus module).

Query 1 established that every deployed arm-based SDL uses an expensive industrial arm
(KUKA KMR-iiwa, ABB YuMi, Franka Research 3, Denso COBOTTA); the arm is a *logistics*
layer; reliability, not capability, is the binding constraint (Ada reports ~1 run-ending
failure per 40 samples); and that fiducial-corrected scripted primitives beat VLA policies
(30–60% out-of-box on unseen tasks) for unattended operation. Query 2 covered ISO 9283
metrology on a budget, thermal drift protocols, reliability statistics (118 trials for a
97.5% lower bound, ~1,497 for 99.8%), the LabRobFail failure taxonomy, Peg-in-Bench, and
venue strategy.

The group is about to build a **physical sandbox**: the arm on a bench with real lab
consumables — **SEM stubs (pin mounts), 2 mL and 20 mL vials both empty and filled,
SBS/ANSI well plates, aluminum DSC/TGA crucibles and their lids (including the press-fit
lid step and a powder-atomizer transfer step)** — plus a Bambu Lab A1 mini printer nearby
as a fixture/jig source and possibly as a station in the loop. Cameras may be wrist-
mounted *or* fixed in the cell, and AprilTags/ArUco are assumed available but the group
explicitly wants to go beyond fiducial-only perception.

# Specifically, please address

1. **Perception for the actual objects, not generic benchmarks.** What is the
   state of the art (2022–2026) for 6-DOF pose estimation and grasping of the specific
   hard cases here: **specular/mirror-finish metal** (aluminum crucibles and lids,
   polished SEM stubs), **transparent glass** (vials, empty vs. liquid-filled — does
   fill level change the failure mode?), and **thin, low-profile, nearly-planar parts**
   (crucible lids, stub caps)? Cover monocular/RGB-only methods (FoundationPose, MegaPose,
   SAM-6D, GigaPose, FreeZe, Any6D and successors), transparent-object depth completion
   (ClearGrasp, TransCG, Dex-NeRF/Evo-NeRF, TRansPose, ASGrasp), polarization imaging,
   structured light and laser-line profilometry, and event cameras. Give measured
   accuracy numbers (ADD/ADD-S, AR on BOP), and state which are usable in-the-loop at a
   few Hz on a Raspberry Pi 5 / Jetson Orin Nano class compute budget versus which need a
   desktop GPU.

2. **How far fiducials actually get you, and where they break.** Quantify AprilTag/ArUco
   pose uncertainty as a function of tag size, camera resolution, focal length, distance
   and viewing angle — including the well-known **rotational ambiguity / pose flipping**
   at near-frontal views and how AprilTag 3, `apriltag_ros`, IPPE, and multi-tag bundles
   mitigate it. What in-plane and out-of-plane accuracy is achievable with a **12.3 MP
   IMX477 and a fixed 6 mm / 8 mm / 16 mm C-mount lens** at 150–500 mm standoff, and what
   does that imply for closing a ±0.5 mm placement tolerance? Cover the practicalities:
   tag printing and substrate flatness, tag-to-feature transform calibration, lighting and
   specular washout on glossy tags, motion blur, and rolling shutter — the IMX477 is a
   rolling-shutter sensor, so quantify the error that introduces during arm motion and
   whether stop-and-look is mandatory. Also: hand–eye calibration (Tsai–Lenz, Park–Martin,
   Daniilidis, and modern optimization-based methods) — achievable residuals, how many
   poses, and how the calibration degrades over days/weeks of operation.

3. **Learned policies via LeRobot — is this the right time?** Hugging Face **LeRobot** was
   raised by a collaborator. Assess it concretely for this setting: what does the
   framework actually provide (`lerobot` datasets v2/v3, ACT, Diffusion Policy, VQ-BeT,
   SmolVLA, pi0/pi0.5 ports), which arms are supported out of the box (SO-100/SO-101,
   Koch, ALOHA, ViperX, and whether AgileX PiPER is supported — AgileX also makes the
   LeRobot-affiliated **AgileX PiPER/Cobot Magic** and **RoboTwin** platforms), and what
   teleoperation hardware is needed to collect demonstrations. **How many demonstrations
   per task** do ACT / Diffusion Policy / SmolVLA actually need for a >90% success rate on
   a precise, low-clearance task, and what success rates are reported on tasks comparable
   to insertion and lid press-fit? Contrast the total effort (teleop rig, data collection
   hours, GPU training, evaluation) against writing a fiducial-corrected scripted
   primitive that does the same job. Be blunt about whether a learned policy can reach
   the >99% per-operation reliability an unattended SDL needs, and identify where a
   hybrid — learned for search/approach, scripted plus force control for the final seat —
   is the honest answer.

4. **Contact-rich steps without a force/torque sensor.** The press-fit lid step and the
   peg-in-hole-like seats (vial into rack, stub into holder, crucible into a furnace
   position) are contact tasks. What can be achieved with **joint-current/torque sensing
   on a low-cost arm** (no wrist F/T sensor), with **compliant or remote-center-of-
   compliance fixtures**, with **admittance/impedance control** on an arm with limited
   bandwidth, and with **tactile or vision-based tactile sensing** (GelSight/DIGIT/
   TacTip class, and low-cost printable variants)? Quantify insertion success versus
   clearance, and state what clearance a passively compliant fixture buys you relative to
   free-space placement accuracy.

5. **Prior art in code, not just papers — GitHub and Hugging Face.** Survey what is
   actually released and usable: `piper_ros` / `piper_sdk` maturity, MoveIt 2 support,
   ROS 2 Jazzy/Humble status; SDL orchestration stacks (**MATTERIX** from the Acceleration
   Consortium — note Kourosh Darvish as an author — **ChemOS/ChemOS 2.0**, Bluesky/Ophyd,
   **PyLabRobot**, **Opentrons** HTTP API, SiLA 2, LabOP/Autoprotocol, AlabOS, ORCA/
   ODTP); vision stacks (`apriltag_ros`, `aruco_ros`, Isaac ROS AprilTag, FoundationPose
   and SAM-6D releases, `lerobot`); simulation and digital twins (Isaac Sim/Lab,
   MuJoCo MJCF for the PiPER, Genesis, RoboTwin, ManiSkill, `ros2_control` + Gazebo).
   For each: license, activity, whether a PiPER-class arm is actually supported, and
   whether adopting it is faster than writing our own. Identify **Hugging Face datasets
   and models** relevant to lab manipulation specifically (LeRobot dataset hub, RoboTwin,
   Open X-Embodiment, DROID, BridgeData, AgiBot World) and say which contain anything
   resembling labware.

6. **What the sandbox should contain, and what to measure in it first.** Given the object
   list above and a Bambu A1 mini for fixtures, specify a concrete first sandbox: which
   5–8 primitive operations to implement, in what order, the fixture design principles
   (kinematic seats, lead-in chamfers, funnel tolerances, tag placement), what to
   instrument, and what to log so the campaign doubles as the reliability dataset from
   Query 2. Which of these operations is the **highest-value first publishable result**,
   and what would make it more than a demo? Include safety and containment notes for the
   powder-atomizer transfer step.

7. **Collaboration and positioning.** Given MATTERIX (Nature Computational Science 2026,
   Acceleration Consortium) and adjacent efforts, where does a low-cost-arm sandbox
   complement rather than duplicate that work? What would a group with a PiPER, an OT-2, a
   powder doser, a gantry, an LPBF-adjacent AM workflow, and a cloud-access thesis
   contribute that the well-funded labs structurally will not?

Prioritize 2023–2026 sources. Give measured numbers with the hardware and conditions they
were measured under. Clearly flag extrapolation, and explicitly say when something is
unknown rather than interpolating.

# Q3 — perception, LeRobot, and what to actually build in the sandbox

Third Edison query for [issue #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199),
task `29bb1dbe`. Verbatim answer in
[`edison-6dof/q3-perception-lerobot-and-sandbox/answer.md`](edison-6dof/q3-perception-lerobot-and-sandbox/answer.md).
Verification of its claims is in [`6dof-verification-and-ecosystem.md`](6dof-verification-and-ecosystem.md);
**read the corrections in §"Where Q3 is wrong" before acting on §5 of the raw answer.**

## The load-bearing conclusion

**Do not attempt learned pose estimation on the hard objects.** The three object classes in
the proposed sandbox are, in order of difficulty, exactly the three the pose-estimation
literature handles worst:

- **Specular aluminium** (crucibles, lids, polished SEM stubs). On the IMD benchmark of 45
  industrial metallic parts, BundleTrack gets 6.61 mm / 8.12° top-down but degrades to
  **32.23 mm / 49.17° at a 45° viewing angle** — specular reflection destroys both depth and
  feature matching. Structured light saturates on shiny surfaces.
- **Transparent glass** (vials). GraspNeRF reaches 88.9% real-world single-object grasping
  at 11 FPS from 6 views, but needs multi-view. **Fill level changes the failure mode**:
  an empty vial is purely refractive, a filled one adds a meniscus artifact.
- **Thin, near-planar parts** (crucible lids, stub caps). Edison's assessment is that these
  are *"essentially unstudied"* — no published method reports reliable 6-DOF pose on parts
  under ~2 mm tall, because they present almost no silhouette and near-zero depth contrast.

The consequence is a design rule, not a research problem: **tag the fixture, not the part.**
The arm should know "lid is at tag X plus a known offset", never "estimate the lid's pose".

This is also why the foundation-model pose estimators are a distraction here. FoundationPose
needs 12.7–68.5 s per image, MegaPose 11.3–139.4 s, SAM-6D 0.8–3.9 s, GigaPose 0.4–2.1 s,
at 0.83–6.47 GB of GPU memory. **None run at interactive rates on a Pi 5 or an Orin Nano.**

## Fiducials: the theory is generous, the measurements are not

Edison's optics calculation for our exact hardware: a 20 mm tag at 300 mm on the IMX477 with
a 6 mm lens spans ~130 px of the 4056 px width → ~0.15 mm/px, and at 0.1–0.3 px corner
accuracy that is **0.02–0.05 mm** — twenty times better than the ±0.5 mm we need. At 500 mm
it degrades to ~0.08 mm/px, still adequate.

Treat that as an upper bound on what is possible, not a prediction. In the same answer, the
measured result it cites (Abbas et al.) is **~1.0 cm error in x at 70 cm standoff**, rising
to ~12 cm with 20 cm lateral offset and yaw misalignment. Two orders of magnitude between
the theory and the measurement is the whole engineering problem, and it is where the
vision-corrected-primitives contribution (Q1 gap 3) actually lives.

Three practical constraints that shape the cell design:

- **Stop-and-look is mandatory.** The IMX477 is rolling-shutter with ~30 ms readout; at
  100–300 mm/s that is **3–9 mm of geometric distortion across the frame**. The arm must
  halt, settle 50–100 ms, capture, then commit — roughly 200–500 ms per observation.
- **Mount tags on fixture sidewalls, not just top faces, and use bundles.** Near-frontal
  planar views give two valid PnP solutions and the estimate flips between frames. IPPE
  returns both with reprojection uncertainties; non-coplanar multi-tag bundles remove the
  ambiguity outright.
- **Matte substrate, diffuse 45° lighting.** Blooming in overexposed regions shifts detected
  corners by up to **0.74 mm** — larger than the tolerance we are trying to hold.

Hand–eye: Tsai–Lenz with 25 poses gives 0.08 mm RMS translational residual; nonlinear
optimization reaches 0.21 mm overall positioning error vs. 0.36 mm for Tsai–Lenz. Use ≥20
poses, recalibrate weekly. Long-term calibration drift is not quantified in the literature —
which, like the MTBI gap, means measuring it is a contribution.

## LeRobot: the honest numbers

For a low-clearance insertion comparable to the lid press-fit, expect **50–200 good
teleoperation demonstrations** for 80–95% success. The anchors:

| Result | Number |
|---|---|
| Diffusion Policy, real-world Push-T, ~200 demos | 95% |
| ACT, bimanual insertion, 50 scripted demos | **32%** (57% with AWE preprocessing) |
| Comp-ACT / DIPCOM, bimanual peg insertion at 2 mm clearance | 95–100%, but only after tuning with compliant control |

And the conclusion that matters: **>99% per-operation reliability is not demonstrated by any
learned policy in the literature.** The best real-world results plateau at 90–96% on precise
tasks. Against a 50-step campaign, 96% per operation is a 13% chance of finishing.

Effort, per primitive: learned ≈ 1–3 weeks (rig, 2–8 h teleop, 1–4 h training, 50+ eval
trials, iterate); scripted-with-fiducial-correction ≈ 3–5 days. The recommendation is a
**hybrid** — learned or vision-driven search and approach where location varies, scripted and
force-guarded for the final seat.

So the answer to @jss265's LeRobot suggestion is "yes, but not for the insertion". It earns
its place on the approach phase and as the data-collection substrate, and — see the
ecosystem doc — the teleop rig is an off-the-shelf purchase (`lerobot-teleoperator-pipermate`
driving the PiPER from a PiperMate leader arm), not a build.

## Contact-rich steps without an F/T sensor

Joint-current sensing over CAN resolves roughly 0.1–0.5 N·m — **enough to detect a jam and
trigger retract-and-retry, not enough to control force.** The primary strategy is passive
compliance in the fixture:

- **1–2 mm lead-in chamfers at 15–30°** on every receiving feature — this is what converts
  ±0.5 mm of lateral error into a guided insertion
- **V-groove kinematic seats** for vials (self-centering, tolerates diameter variation);
  **1° tapered bore** for crucibles; embedded 3 mm neodymium magnets for SEM stub holders
- **Design every fixture for ≥1.0 mm clearance.** At 0.5 mm position uncertainty, a 0.5 mm
  clearance hole needs active compliance; a **1.5 mm clearance hole succeeds >95% under
  position control alone**
- A printed or elastomeric **RCC adapter** buys ~1–2 mm of passive lateral compliance

If tactile sensing is wanted later for the press-fit specifically, it is cheap now: GelSlim
4.0 is fully open-source at ~$122 in materials, DIGIT ~$350, GelSight Mini ~$549.

## The sandbox, in implementation order

Edison's eight primitives, which escalate cleanly in difficulty:

1. Empty 20 mL vial, rack → station → rack *(baseline repeatability)*
2. Empty 2 mL vial *(tighter grasp tolerance)*
3. SEM stub, pin mount → holder *(first specular object)*
4. Vial into SBS/ANSI well plate *(array indexing)*
5. Aluminium crucible, tray → furnace position *(specular and light)*
6. Crucible lid placed, not pressed *(thin part)*
7. **Crucible lid press-fit** *(contact-rich; needs compliance)*
8. Powder transfer via atomizer *(contact plus containment)*

Fixtures in PETG on the A1 mini, 20 mm AprilTag on matte label stock on every fixture
sidewall. Log per operation: joint positions at 10 Hz, gripper state, camera frames before
and after each pick and place, tag detections, outcome tagged with the **LabRobFail category
and subtype**, cycle time, ambient temperature. That log *is* the Q2 reliability dataset —
the sandbox and the reliability paper are the same campaign, not two.

Note the cycle-count correction from the verification doc: Edison repeats "118 trials per
primitive" here, which should be **119** for a zero-failure 97.5% lower bound, and if the
goal is to *compare* two conditions rather than certify one, ~310 per arm is the right budget.

**Highest-value first result**: measured success rate for each of the 8 primitives over
N ≥ 200 trials, with ISO 9283-style repeatability, the thermal protocol, and the failure
taxonomy. What lifts it above a demo: release the fixture STLs and ROS 2 nodes, publish the
raw per-trial logs, compare against the Ada ~1-in-40 figure, and derive a
**cost-per-reliable-operation** metric that places the PiPER in the SDL design space.

Powder step safety: printed enclosure with HEPA-filtered exhaust, sealed atomizer with check
valve, in-loop mass-balance verification (weigh before/after), and an interlock so the arm
cannot enter the powder zone with the enclosure open.

## Positioning against MATTERIX

Edison's read is that the well-funded labs structurally optimize for **capability and
generality** — expensive arms, commercial instruments, full-stack simulation — and therefore
will not produce:

1. **Reliability data for cheap hardware.** Nobody with a $100k KUKA cell has an incentive to
   characterize a $3k arm, and the community needs those curves to make build-vs-buy calls.
2. **An open 3D-printable fixture library** for standard labware — immediately reusable by
   any group with an FDM printer.
3. **Documented failure boundaries.** At 1.5 kg payload and 626 mm reach the PiPER sits at
   the edge of viability; saying exactly which operations fail, at what clearance, after how
   many hours, either validates or refutes the low-cost SDL thesis. Both outcomes publish.
4. **A cloud-operated, headless architecture** that scales *down* — which an Isaac Sim
   dependency does not.
5. **AM in the loop.** A printer as both fixture source and station is, per Edison, something
   no deployed SDL incorporates: measure arm accuracy → print a compensated fixture → verify
   → iterate. This is the one that ties `powder-doser`, `tensegrity-optimization` and the
   arm into a single story.

The framing to keep: the contribution is not "we built an SDL" — many have — but "we
characterized whether a $3k arm can reliably run one, and here is exactly what it takes in
fixtures, calibration and software, or the evidence that it cannot."

## Where Q3 is wrong

Checked against the repositories themselves. Two of these would have cost real time.

**"MATTERIX … Not open-source as of this writing."** False.
[`AccelerationConsortium/Matterix`](https://github.com/AccelerationConsortium/Matterix) is
public and **BSD-3-Clause**, created 10 Sep 2025, last pushed 10 Sep 2026, 55 stars, with
Docker, `pyproject.toml`, and a `source/` tree. It is available to read and to build on
today — which changes the collaboration question from "can we get access" to "where do we
plug in", and makes reaching out to Kourosh Darvish a conversation about an existing
codebase. Edison also sourced its MATTERIX statements to `ren2607pudaanainative`, a
different paper, so the claim was never grounded in MATTERIX's own materials.

**"No official MuJoCo MJCF or URDF for simulation (must create from STEP files)"**, costed at
"a 1–2 day task". False. [`piper_ros`](https://github.com/agilexrobotics/piper_ros) ships
`src/piper_description/mujoco_model/piper_description.xml` and
`piper_no_gripper_description.xml` — official MJCF — alongside `piper_description.urdf`,
`.xacro`, no-gripper and `with_teach` variants, and Gazebo assets. The work is already done.

**"MoveIt 2 support is community-contributed and immature."** The `humble` branch of the
official repo contains `src/piper_moveit/piper_no_gripper_moveit/`. Maturity is a fair open
question; provenance is not — it is AgileX's own.

**A real gotcha Edison did not flag**: `piper_ros`'s **default branch is `noetic`** — ROS 1.
A plain `git clone` gets ROS 1. The branches are `noetic`, `foxy`, `humble_beta1`, `humble`;
check out `humble` explicitly.

**LeRobot's supported-robot list is stale.** Edison lists "SO-100/SO-101, Koch, ALOHA, and
ViperX". The current `src/lerobot/robots/` tree has `so_follower`, `koch_follower`,
`openarm_follower`, `reachy2`, `rebot_b601_follower`, `omx_follower`, `lekiwi`, `hope_jr`,
`unitree_g1` and bimanual variants — no ALOHA or ViperX package. The policy set is also much
larger than the "ACT, Diffusion Policy, VQ-BeT, SmolVLA, pi0/pi0.5" given: `groot`, `eo1`,
`evo1`, `xvla`, `wall_x`, `molmoact2`, `vla_jepa`, `rtc`, `fastwam` and others ship today.

**"No existing dataset contains SEM stubs, crucibles, or well plates."** True as stated for
the big embodiment corpora (RoboMIND, Open X-Embodiment, DROID, BridgeData, AgiBot World),
and it is right that RoboMIND's 107k trajectories include AgileX Cobot Magic V2.0 as one of
four embodiments. But the Hugging Face survey found lab-specific collections it missed —
**`autobio-bench`** (MIT, LeRobot format, nine tasks including centrifuge insertion and
thermal-cycler door operation) and **`lerobotForScienceEdu`** (real staged lab-workflow
demonstrations). See the ecosystem doc. Neither closes the gap, but "start from nothing" is
the wrong starting assumption.

## What Q4 should ask

Q3's answer makes the next question narrower than the arc originally sketched. The two live
uncertainties are now (a) the **cloud-operated control plane** — Edison recommends EOS over
AlabOS/Bluesky/ChemOS for a new SDL, which deserves scrutiny against our existing
MQTT + MongoDB + HF Space stack rather than a greenfield assumption — and (b) **unattended
operation and safety** around the furnace and the powder step, which is what turns a sandbox
into something that can run overnight. Safety is the harder gate and the one that blocks the
reliability campaign, so it should go first.

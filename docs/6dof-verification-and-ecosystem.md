# Verifying the Edison 6-DOF answers, and what the code ecosystem actually looks like

Companion to [`6dof-arm-sdl-scan.md`](6dof-arm-sdl-scan.md), for
[issue #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199). Two jobs:

1. **Check Edison's load-bearing numbers against the full text of the sources**, rather
   than against its own summary of them.
2. **Survey what is released as code and data** — GitHub and Hugging Face — since a
   literature agent sees papers, not repositories, and several of the most useful things
   here have no paper attached.

Articles were fetched from the OT-2 stream-cam Pi's residential IP (`~/vcl-6dof-verify/`)
because publisher sites and some hosts refuse GitHub Actions runners. Every "confirmed"
below means the number was grepped out of the article text, not inferred.

## 1. Verification results

### Confirmed verbatim

**AgileX PiPER specifications.** [global.agilex.ai/products/piper](https://global.agilex.ai/products/piper)
states **1.5 kg payload, 626 mm reach, 0.1 mm repeatability**, 4.2 kg arm mass, 6-DOF.
Every figure the planning rests on is the vendor's own, exactly as quoted. Note what this
does *not* establish: the 0.1 mm is an unqualified vendor claim with no stated payload,
speed, pose set, cycle count, or thermal state — which is precisely why Q1 ranked
independent characterization as opportunity No. 2.

**Peg-in-Bench.** [`aistairc/peg-in-bench`](https://github.com/aistairc/peg-in-bench)
exists and is as described: a scenario generator with STL files, **5 shapes** and **three
tolerance levels — 0.1 mm (tight), 1 mm (medium), 3 mm (loose)**. Directly reusable; the
0.1 mm tier is almost certainly beyond a PiPER in free space, which makes it a good
honest-difficulty ladder rather than a demo.

**LabRobFail's headline counts.** arXiv [2607.23704](https://arxiv.org/abs/2607.23704) —
"over 20,000 trajectories across 70+ task scenarios, five failure categories, and 11
fine-grained failure types". The five categories (Perception, Grasping, Motion, Logic,
Safety) and all 11 subtypes are confirmed in the text.

### Confirmed but materially incomplete

**LabRobFail's trajectories are simulated, not observed.** The paper's own description:
*"LabRobFail-Sim **injects controllable failures** at the control, physics, and semantic
levels, enabling the construction of LabRobFail-Data."* Edison presented this as "the
first dedicated failure taxonomy and benchmark for chemical SDLs" without saying the
20,000 trajectories are synthetic injections in simulation.

This matters more than any other correction here. It means:

- The **taxonomy is adoptable** — it is a reasonable, published set of category labels to
  log our interventions against, and using it makes our data comparable.
- It is **not a source of failure-rate priors**. Injected failure distributions tell you
  nothing about how often a real PiPER drops a real vial.
- Therefore it **does not scoop the MTBI gap** — it reinforces it. Real measured
  intervention rates on real hardware remain unpublished. Q1's No. 1 opportunity survives
  contact with the source.

Two further details: severity is **four named levels — Minor, Recoverable, Critical,
Catastrophic**, not "L1–L4" (the paper's L1/L2/L3 are the benchmark's *cognitive* tiers,
a different axis Edison merged with severity); and the code lands at
[`Su-ISE-2001/SciRobo`](https://github.com/Su-ISE-2001/SciRobo), with the appendix still
calling the data "SciRobo-Data" — worth knowing before searching for "LabRobFail" and
finding nothing.

**Le Houx is a beamline taxonomy, and ESME is not his.** arXiv
[2601.06978](https://arxiv.org/abs/2601.06978) confirms the 6-level L0–L5 scale and the
Inference Barrier at Level 3. But it is named the **BASE scale** (Benchmarking Autonomy in
Scientific Experiments) — Edison never used the name — and it is explicitly built for
**Large-Scale User Facilities**, whose constraints the abstract says are *"incompatible"*
with the owner-operator model that SDL taxonomies assume. Edison offered it as an SDL
autonomy scale without that caveat. ESME appears in the text as a **citation to reference
[11]**, not as Le Houx's contribution; Edison credited him with proposing it.

The scope mismatch is interesting rather than disqualifying. The BASE scale's premise —
*"zero-shot deployment where agents must operate immediately without extensive training
periods"*, because the operator is not the owner — is a closer fit to a **cloud lab with
remote users** than the owner-operator SDL literature is. If the Vertical Cloud Lab thesis
gets written up (Q1's opportunity No. 5), BASE is the more honest framework to position
against, and that is an argument *for* citing it, just not for the reason given.

### Arithmetic

Edison's sample-size claims recompute correctly but with two caveats:

| Claim | Recomputed | Note |
|---|---|---|
| n ≥ 118 for a 97.5% lower bound, 0 failures | log(0.05)/log(0.975) = **118.33** | rounds **up to 119**; 118 misses the bound |
| n ≥ 1497 for a 99.8% lower bound, 0 failures | log(0.05)/log(0.998) = **1496.37** → 1497 | correct |
| 97.5%/sample → 28.2% over 50 samples | 0.975^50 = **0.2820** | correct |
| ~99.8% needed for 90% over 50 | 0.90^(1/50) = **0.99790** | correct |

The larger point: Q2 asked *how many cycles to distinguish 97.5% from 99.8%*, and Edison
answered *how many zero-failure trials certify each bound separately*. Those differ. A
two-proportion comparison at α=0.05 one-sided and 80% power needs roughly **310 operations
per arm** — a materially cheaper experiment than 1,497, and the one that matches the
question. Both belong in a methods section; only one of them was asked for.

## 2. What is actually released — GitHub

| Project | License | Last push | Read |
|---|---|---|---|
| [`agilexrobotics/piper_sdk`](https://github.com/agilexrobotics/piper_sdk) | MIT | 2026-09-07 | **Actively maintained.** The real integration surface. |
| [`agilexrobotics/piper_ros`](https://github.com/agilexrobotics/piper_ros) | MIT | 2026-03-04 | Six months stale. Usable, but the SDK is where the work is going. |
| [`AgRoboticsResearch/lerobot_robot_piper`](https://github.com/AgRoboticsResearch/lerobot_robot_piper) | Apache-2.0 | 2026-05-13 | LeRobot plugin. Cleanly licensed. |
| [`WeGo-Robotics/lerobot_robot_piper`](https://github.com/WeGo-Robotics/lerobot_robot_piper) | **none** | 2026-09-04 | More features (multi-arm teleop, safety limits, GUI) and more active — but **no license file, so not safely reusable**. Worth an issue asking them to add one. |
| [`AccelerationConsortium/Matterix`](https://github.com/AccelerationConsortium/Matterix) | BSD-3 | 2026-09-10 | "Digital Twin for Robotics-Assisted Chemistry Lab Automation". Active. The Kourosh Darvish contact @sgbaird raised. |

**PiPER is not a first-class LeRobot robot.** It does not appear in
`src/lerobot/robots/`; it appears in `docs/source/third_party_robots.mdx`. That is less bad
than it sounds — LeRobot auto-discovers any installed package named `lerobot_robot_*`,
`lerobot_teleoperator_*`, or `lerobot_camera_*`, so adding the PiPER is a `pip install`
rather than a fork. But it does mean nobody upstream tests PiPER on release.

**There is an off-the-shelf teleop path.** `lerobot-teleoperator-pipermate` on PyPI drives
the PiPER from a **PiperMate** leader arm built on FashionStar UART servos. If we go the
demonstration-learning route, the rig is a purchase, not a build. That was the practical
blocker and it is already solved by someone else.

## 3. What is actually released — Hugging Face

Edison Q2 concluded **"no standardized labware task board currently exists."** As a
statement about *physical, endorsed, published* task boards that holds. As a statement
about what exists to build on, it is wrong, and the gap is on Hugging Face rather than in
the literature — exactly the blind spot of a literature-only agent.

**[`autobio-bench`](https://huggingface.co/autobio-bench)** — the closest thing to a
labware benchmark that exists. **MIT-licensed**, LeRobot v2.0 format, `robot_type: ur5e`,
100 episodes per task, both MuJoCo and Blender renders of each:

| Task | Why it matters here |
|---|---|
| `insert`, `insert_centrifuge_5430` | the vial/holder seat, with a named real instrument |
| `pickup` | the transfer primitive |
| `pipette` | maps onto the OT-2 / `digital-wetlab` side |
| `screw_loose`, `screw_tighten` | closest released analogue to the **crucible lid press-fit** |
| `thermal_cycler_open`, `thermal_cycler_close` | instrument-door manipulation |
| `thermal_mixer` | instrument interaction |

It is simulation, and on a UR5e rather than a low-cost arm — so it does not close any of
the Q1 gaps. What it does is give a **task vocabulary that already has downloads behind
it**, and a concrete answer to "what should the sandbox contain": seven of its nine tasks
have a physical counterpart in the object list @sgbaird proposed.

**[`lerobotForScienceEdu`](https://huggingface.co/lerobotForScienceEdu)** — real LeRobot
demonstration datasets for staged lab workflows, collected Nov–Dec 2025. The `AgarBadge_v1`
series is split by workflow stage — `1st_Liquid-Handling` (100 eps), `2nd_Agar-Adding` (90),
`3rd_Heating-And-Stirring` (70), `4th_Thermal-Safety-Logic` (42/91), `5th_Aliquot` (81),
plus full-episode runs — alongside `Pipette_Squeeze` at 20 and 40 episodes. The episode
counts are in the dataset names, which makes this an unusually direct read on **how much
demonstration data people actually collect per lab task**: tens, not thousands.

**Real PiPER LeRobot data exists.** `KeWangRobotics/piper_test`, `kelo234/piper_real_test_*`,
`shilong123/lerobot_piper`, and `cpxu/RoboTwin_piper_12_tasks_data` are all PiPER-specific.
None are labware, but they establish that the PiPER→LeRobot recording path works for other
people before we spend money proving it.

Also present: `BIT-MJY/test_tube_pick` / `_place` / `_traj`, `maolinlei/chemistry_robot`,
`cyberorigin/pipette`, and `nimarez/lerobot-lab-operations-1..5`.

## 4. Repository survey — what the issue asked for and the last pass missed

The previous session reported `borysgroup/aurora-cloud-infra` as a stub from its README
alone. @sgbaird's correction was right: **the repository is a stub, the issue tracker is
not.** The relevant threads:

- **[#5 Design of picamera2 mount for AgileX end effector](https://github.com/borysgroup/aurora-cloud-infra/issues/5)**
  — the PiPER wrist camera is already an open work item, with AgileX STEP/CAD links
  gathered and a Pi 5 dual-camera requirement written up. Two prior Claude branches carry
  the design docs. It also contains the most important operational fact in this issue:
  @kinstonwithoutg noted they are **"running out of space in the glovebox"** and is unsure
  the mount is still for Aurora. If the PiPER is not going into Aurora's glovebox, the
  BYU-side sandbox @sgbaird described is not a parallel effort — it is the destination.
- **[#16 HQ streaming cam with Pi 5](https://github.com/borysgroup/aurora-cloud-infra/issues/16)**
  — the dual-HQ-camera-on-one-Pi-5 hardware is **ordered and arriving**, with a camera pod
  mount (CadQuery source + STEP + STL) landed 15 Sept. Two CSI ports, one per camera, and
  the stated intent is one livestream channel plus one command-based point-and-shoot
  channel. That second channel is the machine-vision channel; the eye-in-hand work does not
  need new hardware procurement.
- **[#13 Outline of workflow architecture](https://github.com/borysgroup/aurora-cloud-infra/issues/13)**
  — MonArk runs semi-central orchestration on a single computer, with per-station local
  compute and an Epson arm whose stopping logic is driven by sensors on other equipment.
  Useful as the "what not to do" baseline for a cloud-native control plane.

On our side, `powder-doser`
[#158](https://github.com/vertical-cloud-lab/powder-doser/issues/158) (digital twins for
generative system design) is the direct xref @sgbaird gave, and #156 (spread patterns),
#140 (state-space representation) and #130 (data for optimization) are where an arm-fed
powder workflow would plug in. `tensegrity-optimization` #98/#36/#49 are the print → drop
→ test loop whose specimen handling is still manual — the readiest home for a transfer
primitive that earns its keep.

## 5. What changes as a result

1. **The MTBI gap is confirmed open, and better-defined than before.** LabRobFail gives us
   a citable taxonomy to log against and simultaneously proves nobody has published real
   rates. Adopt the five categories and eleven subtypes verbatim; do not adopt its numbers.
2. **The sandbox task list should mirror `autobio-bench`.** Seven of its nine tasks have a
   physical counterpart in the proposed object set. Matching the vocabulary makes our real
   data the sim-to-real counterpart of an existing MIT-licensed benchmark, which is a much
   stronger position than inventing a task list.
3. **Budget ~310 cycles per condition, not 1,497**, if the goal is to *compare* conditions
   (open-loop vs. vision-corrected, cold vs. warm). Reserve four-digit cycle counts for
   certifying an absolute reliability floor.
4. **The teleop question is answered before it is asked.** PiperMate + a LeRobot plugin is
   a purchase. The open question is not *can we collect demonstrations* but *should we* —
   which is Q3.
5. **Ask WeGo-Robotics to add a license.** Their plugin is the better one and is currently
   unusable for anything we would publish.

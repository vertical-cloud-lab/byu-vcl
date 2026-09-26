# Edison Scientific raw responses — 6DOF robotics / SDL scan (issue #199)

Verbatim answers from the [Edison Scientific](https://edisonscientific.com/) tasks
submitted for [issue #199](https://github.com/vertical-cloud-lab/byu-vcl/issues/199),
archived here for provenance so future readers can see exactly what the model said before
any of it was paraphrased. Same convention as
[`powder-doser/docs/edison/`](https://github.com/vertical-cloud-lab/powder-doser/tree/main/docs/edison).

All traffic goes through `https://api.platform.edisonscientific.com` (the
`api.platform.futurehouse.org` endpoint is a different cluster and will cancel the task).

| Directory | Edison `task_id` | `job_name` | Status |
|---|---|---|---|
| `q1-sota-arms-in-sdls/` | `85b13938-c944-4f68-8dc8-f452a9a073a2` | `job-futurehouse-paperqa3-high` | **success** (34 min) |
| `q2-metrology-and-reliability-methods/` | `cbb5a078-5411-4391-a29b-902196894bc5` | `job-futurehouse-paperqa3-high` | **success**, fetched 2026-09-15 |
| `q3-grippers-and-end-effectors/` | `bccdc402-47d0-44c0-955c-85bca64f182d` | `job-futurehouse-paperqa3-high` | **success** (22 min) |
| `q4-closed-loop-design-protocol/` | `80856303-053c-4b8c-b450-ccc0808273a7` | `job-futurehouse-paperqa3-high` | **success**, fetched 2026-09-26 |
| `q5-sandbox-object-set/` | `c1c66197-fee2-4c28-bde1-2bb4f2ad1433` | `job-futurehouse-paperqa3-high` | **success** (31 min) |

The queries are deliberately **sequential**: each follow-up is written against the
previous answer, so Q2 is not composed until Q1 returns.

## Planned query arc

1. **Q1 — SOTA + gap analysis.** Low-cost 6-DOF arms with eye-in-hand cameras as the
   manipulation layer of SDLs: what is deployed, arm-vs-gantry trade study, vision
   pipelines (fiducial vs. learned pose, transparent/specular labware), VLA foundation
   models for lab manipulation, reliability/remote operation, and a ranked list of
   timely contributions for a small lab. **(returned — see `q1-sota-arms-in-sdls/answer.md`)**
2. **Q2 — metrology and reliability methods.** How to execute Q1's two top-ranked gaps
   rigorously: ISO 9283 / ASME B89.4.22 pose-accuracy testing without a laser tracker,
   thermal drift protocols, reliability statistics and failure taxonomies for autonomous
   labs, existing manipulation benchmarks, venue strategy, and the minimum credible
   paper. **(returned — see `q2-metrology-and-reliability-methods/answer.md`)**
3. **Q3 — custom gripper and end-effector design, plus generative CAD / generative systems
   design.** SOTA end effectors in lab automation (custom 3D-printed grippers, labware-specific
   jaws, compliant/underactuated fingers, suction/magnetic, tool changers at a 1.5 kg payload
   budget, powder-specific tooling, force/tactile sensing on low-cost hardware, wrist-camera
   placement), then a careful read on topology optimization / DfAM / LLM-driven CAD /
   generative grasp synthesis / morphology co-design / layout synthesis — grounded against
   `CADSmith` and against `powder-doser`'s in-house generative-CAD work. **(returned — see
   `q3-grippers-and-end-effectors/answer.md`)**
4. **Q4 — the protocol for Q3's rank-1 project.** Not another survey: the experimental design
   that would make "a generative loop designed a better gripper" defensible — dependent
   variables and how to separate the finger's contribution from the arm's, statistical power
   for high-baseline binary success, fatigue protocols for FDM flexures, what feedback signal
   to return to the generator, ablations a referee will demand, how to run a fair human-expert
   control, and pre-registration/reporting standards. **(returned — see
   `q4-closed-loop-design-protocol/answer.md`)**
5. **Q5 — the sandbox object set.** Q4 found that no physical laboratory-object manipulation
   benchmark exists, so Q5 asks for one: a census of what published SDL arms actually handle,
   per-object specifications and governing standards, a property-axis coverage matrix, how
   YCB-style sets were chosen, fill surrogates, fixtures, and a tiered buy list. **(returned —
   see `q5-sandbox-object-set/answer.md`, and
   [`../sandbox-object-set.md`](../sandbox-object-set.md) for the list checked against the
   lab's own parts, where Q5 invented the atomizer-charge geometry)**
6. **Q6 — remaining axes**, to be narrowed further: (a) transparent/specular labware pose estimation and
   grasping for glass vials, quartz crucibles, and metal powder; (b) hand-eye calibration
   and closed-loop visual servoing accuracy achievable on a sub-$5k arm with a custom
   wrist camera; (c) an arm as the sample-exchange layer closing the loop on an existing
   drop-tower / tensile / LPBF workflow; (d) safety and autonomy architecture for an arm
   operating unattended near furnaces and reactive powders under remote supervision.

## Reproducing / resuming

[`scripts/edison_6dof.py`](../../scripts/edison_6dof.py) has three subcommands. Never run
`wait` in the background — the GitHub Actions runner is destroyed the moment the final
comment is posted, which kills backgrounded processes.

```bash
python scripts/edison_6dof.py submit <slug> <prompt-file>   # LITERATURE_HIGH
python scripts/edison_6dof.py wait   <slug> [interval] [budget]
python scripts/edison_6dof.py fetch  <slug>                 # answer + artifacts
```

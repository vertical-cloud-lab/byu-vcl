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
| `q1-sota-arms-in-sdls/` | `85b13938-c944-4f68-8dc8-f452a9a073a2` | `LITERATURE_HIGH` | submitted 2026-09-08 16:40 UTC, polling |

The queries are deliberately **sequential**: each follow-up is written against the
previous answer, so Q2 is not composed until Q1 returns.

## Planned query arc

1. **Q1 — SOTA + gap analysis.** Low-cost 6-DOF arms with eye-in-hand cameras as the
   manipulation layer of SDLs: what is deployed, arm-vs-gantry trade study, vision
   pipelines (fiducial vs. learned pose, transparent/specular labware), VLA foundation
   models for lab manipulation, reliability/remote operation, and a ranked list of
   timely contributions for a small lab. *(submitted)*
2. **Q2–Q5 — chosen from Q1's gap analysis.** Candidate axes, to be narrowed by what Q1
   actually says is unsolved: (a) transparent/specular labware pose estimation and
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

# The CubXL corrosion plan for copper: follow-up Edison queries

Written 2026-10-18 for [PR #278](https://github.com/vertical-cloud-lab/byu-vcl/pull/278). Sterling
asked for "a follow-up set of Edison scientific queries in the context of doing this for copper,
focused on naval applications, leveraging directed energy deposition, single stream
powder-based", cross-referencing
[digital-alloy-lab PR #117](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/117).

**Status: written, not run.** Edison's login refused this repo's `EDISON_PLATFORM_API_KEY` with
`403 {"detail":"Forbidden"}`, four times between 00:48 and 00:51 UTC on 2026-10-18. The API itself answered
(an unauthenticated request got its normal `401 Missing auth header`), so this is the key, not
the network. The same secret name worked in digital-alloy-lab on 2026-10-17, up to 19:07 UTC. So
either byu-vcl's copy of the secret differs from that one, or the key has since been revoked or
run out of credit. No task was created.

| File | What it is |
| --- | --- |
| [`queries.py`](queries.py) | The ten questions, with the shared context, "already established" and output blocks |
| [`edison_corrosion_cu.py`](edison_corrosion_cu.py) | Submit, wait, fetch and status, laid out like PR #117's `edison_cu_ded.py` |

## What these ask, and why

PR #117's 53 queries (`edison-trajectories/cu-ded-2026-10/`) already cover the alloys, powder
making, DED process windows, film mechanisms, short against long tests, and corrosion metrology in
general. They don't cover the test this folder's parent plans: a 3–4 mm O-ring well holding about
150 µL on a polished cross-section, a low-cost potentiostat, and ICP of the used liquid. These
questions ask what that test becomes for Cu–Ni and NAB in naval service. Each one carries over a
named part of [the aluminum plan](../README.md).

The shared context fixes the target as single-stream blown-powder laser DED, meaning one
pre-alloyed powder feed, not in-situ blending, which is how PR #117 used the term. A block of
"already established" findings from PR #117 (films take months to mature, Tafel and assumed-B
pitfalls, natural seawater reversing rankings, DeCost 2022 being simulated, MAP-E) tells Edison
not to re-derive them.

| Name | Job | What it asks | Carries over |
| --- | --- | --- | --- |
| `c1-01-small-cell-artifacts-cu` | LITERATURE_HIGH | What goes wrong for copper alloys in an open 10–200 µL well: dissolved Cu redepositing, oxygen supply, evaporation, pH at the counter, crevice attack under the O-ring, area effects | §4 "Things that will bite". Copper's cathodic reaction is oxygen-diffusion-limited, and its dissolved metal plates back out, so the small well matters more than it does for Al |
| `c1-02-dc-sequence-for-cu` | LITERATURE | What replaces the G61-style cyclic polarization for alloys that corrode actively. Holds at cathodic-protection and galvanic-couple potentials. Current and potential ranges, to size the potentiostat | The protocol's sequence and §5's potentiostat spec. PR #117's b5-06 asked about measurement pitfalls and a one-hour protocol in general, not cyclic polarization, holds or current ranges |
| `c1-03-element-resolved-dissolution-cu` | LITERATURE_HIGH | AESEC, flow-cell ICP-MS and offline ICP of Cu–Ni and NAB: congruent or selective dissolution, faradaic balance, sodium matrix effects. Copper release rates, antifouling, and limits on copper discharge | §1.3, the chemistry link. For a naval copper alloy, its copper release rate is a property in its own right |
| `c1-04-zone-resolved-repair-electrochem` | LITERATURE | Deposit, fusion zone, HAZ and substrate compared by microcapillary cell, SDC, SVET, SECM and SKPFM; galvanic coupling; where to put wells on a repair cross-section | The repair coupons, and PR #117's open item 5 (masked zones plus a ZRA test) |
| `c1-05-specimen-prep-surface-state-cu` | LITERATURE | Final polish, delay and cleaning; as-deposited, machined or polished faces; build-plane orientation; pores acting as crevices | The polishing SOP (#258) and the XY/XZ comparison |
| `c1-06-electrolyte-series-naval` | LITERATURE | Which series mixed from stocks (chloride, sulfide, oxygen, pH, ammonia, ferrous dosing, temperature) gives each alloy a slope, and how to keep it stable in an open well | The 0.006–0.6 M chloride series |
| `c1-07-mini-jet-flow-cell-cu` | LITERATURE | Can a syringe- or peristaltic-fed micro-jet on a 3–4 mm spot screen erosion-corrosion, and what wall shear does it take to match 3–4 m/s pipe limits | New. Flow-driven attack is a well-known failure mode of Cu–Ni seawater piping, and the plan has no flow |
| `c1-08-precedent-automated-cu-corrosion` | PRECEDENT | Has anyone automated corrosion tests of copper alloys, especially printed or weld-repaired ones, or paired them with ICP of the electrolyte? | The novelty check of §2 and §7 |
| `c1-09-rapid-solidification-proxies-cu` | LITERATURE | Do laser-surface-melted, single-track, splat or arc-melted forms predict the corrosion of a multi-layer DED deposit? | §1.2, leftovers against the print, and the atomizer's splats and skull |
| `c1-10-coulometric-oxide-reduction-cu` | LITERATURE | Can cathodic reduction on the same potentiostat measure the oxide films on Cu–Ni and NAB, and the oxide on copper powder, compared with inert-gas fusion? | PR #117's "measure oxygen per lot by inert-gas fusion" (b3-10). It would be a second use of the potentiostat |

## To run

Once the key works, from the repo root (needs `pip install edison-client`):

```bash
python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py submit 1
# one foreground call; PR #117 found every job, standard or high, takes about 30 min
python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py wait 1 45
python alloy-corrosion/copper-ded-edison/edison_corrosion_cu.py fetch
```

`submit` writes `_task_ids.json` as each task is created, so commit it straight away. `fetch` writes
`batch1/<name>.md` (the question, then Edison's answer) and `raw/<name>.json.gz` (the full verbose
trajectory). Commit both.

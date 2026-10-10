# salt_doses.csv

One row per dose of the powder-doser salt campaign `salt-20260929T014732Z`:
0.5 g of table salt per dose, dosed by the Zero into a cup on a balance. This
is the kit's worked example; a paper replaces it with its own snapshots.

- **Units:**
  - `trial_index`: dose number in the campaign, from 0 (no unit)
  - `label`: the campaign's name for the dose (`baseline-00`, `corner-03`, `bo-005`, ...)
  - `group`: `hand-tuned` (the four `baseline`/`rebaseline` doses), `screening`
    (`corner` and `center`), `recentring` (`recenter`), `optimizer` (`bo`)
  - `status`: `ok`, `overshoot` (more than the tolerance over 0.5 g), or
    `cycle-budget` (stopped at the time limit)
  - `t_total_s`: time for the whole dose (s)
  - `error_mg`: settled mass minus 0.5 g (mg); negative is under
  - `abs_error_mg`: `|error_mg|` (mg)
- **n:** 42 doses, one per row, all from one campaign, one powder, one
  target mass and one machine: 4 hand-tuned, 20 screening, 4 recentring and
  14 optimizer doses. No dose was repeated with the same settings, so
  there are no technical replicates; a group's spread is spread across
  settings, not repeatability.
- **Provenance:** derived on 2026-10-10 from
  `data/opt/salt-20260929T014732Z/campaign_records.jsonl` in
  [vertical-cloud-lab/powder-doser](https://github.com/vertical-cloud-lab/powder-doser)
  at commit `ff074df` (branch `claude/opt-results-slides-20261005`; the
  campaign itself is from PR #166). SHA-256 of that file:
  `d82f4318d087b628ca3e085c008e5930d5ab0ff476907bfbf0246601ab3cfea5`.
  Each row is that file's `trial_index` and `label`, and its `summary`'s
  `status`, `t_total_s`, `error_mg` and `abs_error_mg`, unchanged; `group`
  follows `group()` in that branch's `docs/optimization/slides/campaign_data.py`
  with the four groups renamed.

# Copper's idle stretches with and without the cap on blend screens (round 6's engine)

Made by `python out/twin6/checks/copper_idle.py table` from `copper_idle.jsonl`. A stretch is flagged when copper's first fabrication step (or the atomizer) started nothing for two weeks or more while the policy was waiting and the campaign could have started a job (twin/round6.py `idle_report6`). Everything is simulated.

Round 5's rule (the station busy under half of every hour of the stretch) is applied to the same stretches beside round 6's (a partner's session offered and not used, or an in-house station free half its open hours), so that a change of rule is not mistaken for a change of policy. Counts are of copper's first fabrication step, where round 5 found its stretches.

| Lab | Policy | Stock | Seed | Days | Round 5 flagged | Flagged, cap (r6 rule / r5 rule) | Flagged, no cap (r6 rule / r5 rule) | Blend screens, cap / no cap | Lots, cap / no cap |
|---|---|---|---|---|---|---|---|---|---|
| conventional | bofn3 | lean | 0 | 260 | 2 | 1 / 1 | 0 / 0 | 6 / 6 | 5 / 5 |
| conventional | bofn3 | lean | 4 | 260 | 2 | 1 / 2 | 0 / 0 | 7 / 7 | 5 / 5 |
| conventional | bofn3 | reorder | 0 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| conventional | bofn3 | reorder | 2 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| conventional | pkgfn3 | reorder | 0 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| conventional | pkgfn3 | reorder | 2 | 260 | 1 | 0 / 0 | 0 / 0 | 6 / 6 | 6 / 6 |
| vertical | bofn3 | reorder | 0 | 170 | 3 | 0 / 0 | 0 / 0 | 5 / 5 | 4 / 4 |
| vertical | bofn3 | reorder | 1 | 170 | 2 | 0 / 0 | 0 / 0 | 4 / 4 | 7 / 7 |
| vertical | pkgfn3 | reorder | 0 | 170 | 3 | 0 / 0 | 0 / 0 | 5 / 5 | 4 / 4 |
| vertical | pkgfn3 | reorder | 1 | 170 | 2 | 0 / 0 | 0 / 0 | 4 / 4 | 7 / 7 |

Copper's first fabrication step, flagged stretches in all: with the cap put back 2 by round 6's rule and 3 by round 5's; without it 0 and 0.

# Storing powders in the warm, dry enclosure (2026-09-30)

Follow-up to [#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42). On its first night the
dehumidified enclosure in CB 154 held 39–42% RH at 24.1–24.4 °C (dew point 9.4–10.3 °C). The room
would read about 54% at 21.8 °C (dew point about 12 °C). The question: does the extra ~2.5 °C
undo the benefit of drier air for the powders stored there?

| Edison query (both `success`) | Job | Answer | Full trajectory |
| --- | --- | --- | --- |
| Temperature vs humidity: water uptake and oxidation | LITERATURE_HIGH | [answer](q1-temperature-vs-humidity-water-uptake-and-oxidation-answer.md) | [json](q1-temperature-vs-humidity-water-uptake-and-oxidation.json) |
| AM powder storage studies and recommendations | LITERATURE | [answer](q2-am-powder-storage-studies-and-recommendations-answer.md) | [json](q2-am-powder-storage-studies-and-recommendations.json) |

Queries and task IDs are in [`_task_ids.json`](_task_ids.json).

## Answer: warmer but drier is better, not worse

- **Water uptake follows RH at the powder's own temperature.** Absolute humidity is not the
  controlling variable. On alumina, 55% RH gives about 3 adsorbed water layers and 35–40% about 2
  (Deng et al. 2008, [10.1021/jp800944r](https://doi.org/10.1021/jp800944r)). At fixed RH a
  warmer surface holds slightly *less* water.
- **The temperature penalty is small.** For +2.4 °C, a thermally activated rate rises about
  1.26× if E<sub>a</sub> = 71 kJ/mol and 1.64× if 150 kJ/mol. Those activation energies are from
  high-temperature oxidation (Trunov et al. 2005), so these are upper bounds. Room-temperature oxide
  growth on Al is field-driven and self-limiting.
- **Both rooms are below the ~70% RH onset of atmospheric corrosion of clean Al** (Graedel 1989,
  [10.1149/1.2096869](https://doi.org/10.1149/1.2096869)). The enclosure has more margin.
  Mg-, Zn- and Li-rich phases can react below 70%.
- **The one direct test agrees.** Peres et al. 2024
  ([10.1590/1980-5373-mr-2023-0490](https://doi.org/10.1590/1980-5373-mr-2023-0490)) held AlSi10Mg
  powder for 5 days at 50 °C/17%, 23 °C/29% (silica gel), 50 °C/60% and 23 °C/90% RH. Only
  50 °C/17% kept the as-opened Carney flow. The authors conclude that humidity matters more than
  temperature. That test used a 27 °C rise; ours is 2.4 °C.

## Read with care

- **The oxygen numbers are not storage rates.** Edison cites AlSi10Mg oxygen rising from 0.067 to
  0.257 wt% (Fedina et al. 2022). That powder was aged 96 h in an open furnace at **400 °C**, per
  the extracted text, not stored at room temperature.
- **A key storage study is missing.** Riener et al. 2021 is the most directly relevant one
  ([10.1016/j.addma.2021.101896](https://doi.org/10.1016/j.addma.2021.101896), storage conditions
  and reconditioning of AlSi10Mg vs LPBF part quality). It turned up only in a reference list, so
  its results are not in either answer.
- **The "15–25 °C, below 55% RH" guidance is second-hand.** Edison attributes it to ISO/ASTM
  52907/52928 via a thesis. It has not been checked against the standards.
- **Li-bearing alloys need more than a dry room.** Store them sealed under argon with desiccant,
  even inside the enclosure. No room-temperature storage rates were found for Al–Li, Al–Ce or
  Al–Er powders.
- **Stainless steel and silicon:** a few degrees make no difference, but humidity still matters
  for flow. 316L stopped flowing after 24 h at 70% RH (Kim et al. 2025,
  [10.2497/jjspm.16p-t6-09](https://doi.org/10.2497/jjspm.16p-t6-09)).

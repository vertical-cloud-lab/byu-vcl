# Cold atomizer surfaces, fresh powder, and storage at 27 °C (2026-10-03)

Follow-up to [#42](https://github.com/vertical-cloud-lab/byu-vcl/issues/42) and
[PR #247](https://github.com/vertical-cloud-lab/byu-vcl/pull/247). Since Sep 30 the enclosure has held
27.2 °C at 25–26% RH (dew point 4–10 °C). The room is about 21.8 °C and 40% RH. The rePowder's
water-cooled chamber runs off building chilled water. On Sep 28, with no heat load, that water pulled
the loop below the 10 °C "water too cold" alarm, and condensate dripped from the hoses. The questions:
what does a cold chamber mean for fresh powder when the chamber is opened to air, and what does the
5.4 °C warmer enclosure mean for stored powder? The dew point analysis is in
[`scripts/airgradient/condensation_risk.py`](../../scripts/airgradient/condensation_risk.py).

| Edison query (both `success`) | Job | Answer | Full trajectory |
| --- | --- | --- | --- |
| Cold chamber, fresh powder, cooling water vs dew point | LITERATURE_HIGH | [answer](q3-cold-atomizer-chamber-fresh-powder-condensation-answer.md) | [json](q3-cold-atomizer-chamber-fresh-powder-condensation.json) |
| Storage at 27 vs 22 °C, Riener et al. 2021, silica gel | LITERATURE | [answer](q4-storage-at-27c-vs-22c-riener-2021-silica-gel-answer.md) | [json](q4-storage-at-27c-vs-22c-riener-2021-silica-gel.json) |

Queries and task IDs are in [`_task_ids.json`](_task_ids.json). Numbering continues from
[`../edison-powder-storage-temperature-2026-09-30/`](../edison-powder-storage-temperature-2026-09-30/README.md).

## Answer

- **What matters is the RH at the powder's own temperature.** That RH is the air's vapor pressure over
  saturation at the powder's temperature. Powder lying on a cold wall sees far more than the room
  reading. At or below the dew point, adsorption becomes condensation in the gaps between particles.
- **Moist aluminum powder clumps, and drying only partly undoes it.**
  - At 80% RH, AlSi10Mg forms agglomerates that shaking does not break up (Weiss et al. 2022,
    [10.1016/j.procir.2022.08.102](https://doi.org/10.1016/j.procir.2022.08.102)).
  - Drying below about 175 °C removes only physisorbed water. Trihydroxides need about 300 °C for 1 h,
    and even then they become oxide, not metal.
  - Per Fedina et al.'s account of Riener et al. 2021, drying removed the adsorbed water, but the extra
    oxygen stayed.
- **Fresh powder is the most sensitive.** Gas-atomized Al grows a ~5 nm oxide within hours of first
  exposure, and exposure to humid air releases more H₂O and H₂ on heating than exposure to dry air
  (Yamasaki et al.). Commercial inert-gas atomizers often bleed 1–2 vol% O₂ to passivate the powder
  (Anderson & Foley 2001, [10.1002/sia.1087](https://doi.org/10.1002/sia.1087)). Protocols are
  proprietary.
- **Cooling water vs dew point.** No standard was found. The one documented case is a cold-crucible
  induction melter (Gombert & Richardson 2004, INEEL). There, both the manufacturer and the
  collaborators said to keep the water "well above the dew point", because condensation near energized
  parts invites arcing. Edison's rule of thumb is 3–5 °C above the dew point. It is uncited, so treat it
  as engineering practice.
- **Storage at 27 °C.** No study has varied temperature at fixed RH near ambient for these powders, so no
  measured multiplier exists. Riener et al. 2021 was again inaccessible. Silica gel holds slightly less
  water at the same RH when warmer (Legrand et al. 2022,
  [10.1016/j.cej.2021.134058](https://doi.org/10.1016/j.cej.2021.134058)), but the numbers are in an
  unavailable supplement. Breathing from a 1–3 °C daily swing moves 0.3–1% of a container's headspace
  per cycle. That is about 20–60 mg of water over 90 days for 10 L of headspace, if the seal is poor.

## Read with care

- **Fedina et al. 2022's "aged 96 h" oxygen rise (0.067 → 0.257 wt%) is from 400 °C ageing**, as the
  Sep 30 README notes. q3's table lists it without the temperature. It is not a storage rate.
- **Edison's inference that the rePowder has no passivation step is not from AMAZEMET.** Ask Bartosz.
- **Edison's own minimum water temperatures depend on the enclosure being sealed.** It gives 11–13 °C
  for the enclosure, 15–17 °C if room air gets in, and 18–20 °C in summer with the enclosure open. The
  AirGradient data supports a 15 °C floor in the enclosure; see the PR comment.
- **The Riener et al. hydrogen range (143–908 ppm) is quoted second-hand** through Schulze et al. 2025.
  It mixes new, aged and dried powder.

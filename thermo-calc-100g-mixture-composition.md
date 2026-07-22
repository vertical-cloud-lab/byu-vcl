# Thermo-Calc input for the 100 g ultrasonic atomization mixture

This note converts the recorded **100 g mixture** in [issue #16 comment 4012488827](https://github.com/vertical-cloud-lab/byu-vcl/issues/16#issuecomment-4012488827) into a Thermo-Calc-friendly elemental composition in **wt.%**.

## Source masses

| Component | Measured mass (g) |
| --- | ---: |
| 1100 Al wire | 38.1640 |
| Si powder | 20.3042 |
| AlSi10Mg powder | 41.5472 |
| Total | 100.0154 |

## Composition assumptions

1. **1100 Al wire**  
   Treat as Al for the recommended Thermo-Calc input. AA1100 is **99.0 wt.% Al minimum**, but the supplied repo docs do not resolve the remaining trace-element breakdown tightly enough to support a better explicit element-by-element entry.

2. **Si powder**  
   The SDS in this repo (`silicon-powder-mcmaster-carr-sds-2014400 SDS SI101 011020.pdf`) lists **Si = 98.0-99.5 wt.%**. For a single nominal Thermo-Calc input, use **99.0 wt.% Si**.

3. **AlSi10Mg powder**  
   The [MSE Supplies product page](https://www.msesupplies.com/products/mse-pro-alsi10mg-aluminum-based-metal-powder-for-additive-manufacturing-3d-printing?variant=32224600490042) for the 15-45 um powder lists:
   - **Si = 9.0-11.0 wt.%**
   - **Mg = 0.2-0.45 wt.%**
   - **Al = balance**
   - trace limits: Fe <= 0.55, Mn <= 0.45, Cu <= 0.1, Ti <= 0.15, Zn <= 0.1, Sn <= 0.05, Pb <= 0.05 wt.%

For the nominal Thermo-Calc input below, use the midpoint values **Si = 10.0 wt.%** and **Mg = 0.325 wt.%**, so **Al = 89.675 wt.%** for the AlSi10Mg fraction.

## Recommended Thermo-Calc input (nominal)

Using the assumptions above and renormalizing to 100 wt.% gives:

| Element | wt.% |
| --- | ---: |
| Al | 75.56 |
| Si | 24.30 |
| Mg | 0.14 |

If Thermo-Calc needs a single composition, this is the cleanest input to start with.

## How that nominal composition was obtained

### Nominal element masses before renormalization

| Source | Al (g) | Si (g) | Mg (g) |
| --- | ---: | ---: | ---: |
| 1100 Al wire (treated as Al) | 38.1640 | 0.0000 | 0.0000 |
| Si powder (99.0 wt.% Si) | 0.0000 | 20.1012 | 0.0000 |
| AlSi10Mg powder (Al 89.675 / Si 10.0 / Mg 0.325 wt.%) | 37.2575 | 4.1547 | 0.1350 |
| Total modeled mass | 75.4215 | 24.2559 | 0.1350 |

These modeled masses sum to **99.8124 g**, so they were renormalized to 100 wt.% for the Thermo-Calc entry.

## Sensitivity window from supplier/datasheet ranges

If you want to bracket the uncertainty from the Si powder purity and the AlSi10Mg composition ranges, the modeled blend is approximately:

| Element | Low wt.% | High wt.% |
| --- | ---: | ---: |
| Al | 74.94 | 75.88 |
| Si | 23.63 | 24.77 |
| Mg | 0.08 | 0.19 |

## Practical recommendation

For the first Thermo-Calc AM Module run, use:

- **Al 75.56 wt.%**
- **Si 24.30 wt.%**
- **Mg 0.14 wt.%**

This is an **alloy blend chemistry**, not a molecular stoichiometric formula. If the Thermo-Calc team wants trace impurities (Fe, Cu, Mn, Zn, Ti, etc.) modeled explicitly, the next step should be to obtain a supplier certificate of analysis for the exact AA1100 wire and AlSi10Mg powder lots.

## Sources

- [Issue #16 comment with the 100 g measured masses](https://github.com/vertical-cloud-lab/byu-vcl/issues/16#issuecomment-4012488827)
- `silicon-powder-mcmaster-carr-sds-2014400 SDS SI101 011020.pdf`
- `aluminum-1100-wire-sds-0217200 SDS Alum 041116.pdf`
- [MSE Supplies AlSi10Mg 15-45 um product page](https://www.msesupplies.com/products/mse-pro-alsi10mg-aluminum-based-metal-powder-for-additive-manufacturing-3d-printing?variant=32224600490042)

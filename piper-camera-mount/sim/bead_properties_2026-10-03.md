# Bead-level ("lamina") properties for G-code-based FE: PLA Basic and PAHT-CF

Compiled 2026-10-03. Values are in MPa unless stated. Axes: **1** = along the bead, **2** = across beads in the layer plane, **3** = build direction (Z).
Machine-readable copy: [`bead_properties.json`](bead_properties.json).

How to read the tags:
- **[TDS]** is a Bambu datasheet value.
- **[lit]** is a literature or vendor value.
- **[cal]** was back-calculated from the TDS with the coupon model in §1.
- **[assum.]** has no direct source. The reason is given next to it.

## 1. How Bambu prints its TDS specimens, and the coupon model used

**From the datasheets:**
- The newest PAHT-CF datasheet is **V3.0** ([wiki PDF](https://wiki.bambulab.com/filament-acc/asacf-pahtcf/65f1b18a6d6142d794a1a6a00f1496ef.pdf)). It downloaded straight to the runner (HTTP 200, no Pi needed).
- PAHT-CF specimens: 290 °C nozzle, 100 °C bed, 100 mm/s, **100 % infill**, then annealed and dried at 80 °C for 12 h. Tensile is ISO 527 and flexural is ISO 178.
- The tensile drawing is an **ISO 527-2 type 1A** bar: 150 mm long, with a 10 × 4 mm gauge. The **Z bar is printed standing upright**, so the Z test loads purely across the layers.
- PLA Basic V3.0 ([PDF](https://store.bblcdn.com/s1/default/58b85d0f3db94878854a28fdb8a0006e/Bambu_PLA_Basic_Technical_Data_Sheet.pdf)): 220 °C nozzle, 35 °C bed, 200 mm/s, 100 % infill, annealed and dried at 55 °C for 8 h.
- **Neither sheet states the walls, raster angle, layer height or nozzle.**

**Assumed slicer settings** (taken from the Bambu Studio defaults, which I read in the source: [`fdm_process_common.json`](https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/process/fdm_process_common.json), [`0.20mm Standard @BBL X1C.json`](https://github.com/bambulab/BambuStudio/blob/master/resources/profiles/BBL/process/0.20mm%20Standard%20%40BBL%20X1C.json)):
- `wall_loops` = 2
- outer / inner wall widths 0.42 / 0.45 mm
- solid infill width 0.42 mm
- `infill_direction` = 45°
- 0.2 mm layers

So the X-Y coupon is modelled as 2 walls on each side plus a ±45° core. The walls take 2·(0.42+0.45)/10 = **17.4 %** of the gauge width with a 0.4 mm nozzle, or about **25 %** with a 0.6 mm nozzle.

**Coupon model:**
- Stiffness: E_XY = f_w·E1 + (1−f_w)·E_x(±45 laminate, by classical laminate theory, CLT).
- Strength: a plastic rule of mixtures, f_w·Xt + (1−f_w)·σ_±45. The ±45 core fails by Hashin's matrix criterion, (σ2/Yt)² + (τ12/S12)² = 1.
- The Z coupon is a series stack of layers, so **E3 = E_Z** and **Zt = σ_Z** directly.

**Check:** the recommended PLA set gives E_XY = 2549–2573 (TDS 2580) and σ_XY = 35.7 (TDS 35). The PAHT-CF set gives E_XY = 3752–4106 for walls at 17–25 % (TDS 3860 ± 230) and σ_XY = 88 (TDS 92 ± 7).

**Second scenario (PAHT-CF only):**
- If Bambu's X-Y bars were 0/90 rather than ±45, the same TDS modulus would give **E1 ≈ 4640** (CLT).
- That figure is the low end of the E1 range.

## 2. Bambu TDS anchors

| Quantity | PLA Basic V3.0 | PAHT-CF V3.0 (dry) | PAHT-CF V2.0 (dry) |
|---|---|---|---|
| Density, g/cm³ | 1.24 | 1.06 | 1.06 |
| Tensile modulus X-Y / Z | 2580±220 / 2060±170 | 3860±230 / 2180±130 | 3860 / 2180 |
| Tensile strength X-Y / Z | 35±4 / 31±3 | **92±7 / 47±5** | 88 / 64 |
| Elongation at break X-Y / Z | 12.2 / 7.5 % | 8.4 / 4.1 % | – |
| Flexural modulus X-Y / Z | 2750 / 2370 | 4230 / 1820 | 4120 / 1680 |
| Flexural strength X-Y / Z | 76 / 59 | 125 / 61 | 140 / 68 |
| Source | [TDS](https://store.bblcdn.com/s1/default/58b85d0f3db94878854a28fdb8a0006e/Bambu_PLA_Basic_Technical_Data_Sheet.pdf) | [TDS V3.0](https://wiki.bambulab.com/filament-acc/asacf-pahtcf/65f1b18a6d6142d794a1a6a00f1496ef.pdf) | [TDS V2.0, retailer copy](https://www.machines-3d.com/images/Image/File/Fiches%20techniques/CONSOMMABLES/FILAMENTS%20BAMBU%20LAB/Bambu_PAHT-CF_Technical_Data_Sheet.pdf) |

Notes on PAHT-CF:
- **V3.0 still gives dry values only.** Its Z tensile strength fell from 64 (V2.0) to 47 MPa.
- The composition is "PA 12 and other long-chain PA, carbon fiber", with a melting point of 225 °C and Tg of 70 °C. That melting point is well above neat PA12's ≈178 °C, so the matrix is a blend.
- At density 1.06, the CF content is about 10 wt % if the matrix is neat PA12 (my inference).

**Wet PAHT-CF values from Bambu.** These come only from the product page ([store page](https://us.store.bambulab.com/products/paht-cf), read via its [Shopify JSON](https://bambulab-us.myshopify.com/products/paht-cf.js)). Saturated water uptake is 0.88 % at 25 °C / 55 % RH. Bambu states a 12–18 % decline, against 40–45 % for "normal PA-CF". The page does not give its conditioning protocol.

| Flexural | Dry | Wet | Wet / dry |
|---|---|---|---|
| Modulus X-Y | 4230 | 3640 | **0.86** |
| Modulus Z | 1820 | 1480 | **0.81** |
| Strength X-Y | 125 | 115 | **0.92** |
| Strength Z | 61 | 49 | **0.80** |

## 3. Literature and analogue data used

**PLA**

| Source | Configuration | Values |
|---|---|---|
| [Ferreira et al. 2017, *Compos. B* 124:88](https://doi.org/10.1016/j.compositesb.2017.05.013), read from the [preprint](https://www.nakka-rocketry.net/Articles/0paperPLAcf_R3_RG.pdf) Tables 3–5 | Unidirectional 0°, 90° and ±45° coupons, 100 % infill, 0.4 mm nozzle. ASTM D638 / D3518. | **PLA:** E1 3376, E2 3125, G12 1092, ν12 0.331. S1 (Xt) 54.7, S2 (Yt) 37.1, S12 (D3518) 18.0. **PLA + 15 wt % short CF:** E1 7541, E2 3920 (**E1/E2 = 1.92**, against 1.08 for neat PLA), G12 1268, ν12 0.400. Xt 53.4, Yt 35.4, S12 18.9. |
| [Song et al. 2017, *Mater. Des.* 123:154](https://doi.org/10.1016/j.matdes.2017.03.051) ([accepted manuscript](https://spiral.imperial.ac.uk/bitstreams/c34d2e00-a3ba-486b-8d40-77599a169575/download), Table 4) | Unidirectional blocks, machined. 0.2 mm layers, 220 °C, 0.4 mm nozzle, strain rate 2.5e-4 /s. | **Tension:** E 3.98 / 4.04 GPa (0° / 90°). σmax 54.9 (0°), 61.4 (45° off-axis), 46.2 (90°). **Compression:** σmax 98.4 (0°), 98.1 (90°). Ratios: **Xc/Xt = 1.79, Yc/Yt = 2.12**. |
| [Gonabadi, Yadav & Bull 2020, *IJAMT* 111:695](https://doi.org/10.1007/s00170-020-06138-4) ([open access](https://eprints.ncl.ac.uk/269330)) | 0.15 mm layers, 0.4 mm nozzle, 220 °C. ASTM D638, and Iosipescu shear (D5379). | **Tension:** E1 3.5 GPa, Xt 55, ν12 ≈ 0.35. Upright: E ≈ 2 GPa, ν31 ≈ 0.2. **Shear:** in-plane (flat 0°) G 1.27 GPa, S 35. On-edge 0° (τ13): 1.21 GPa, 27. Upright (interlayer): 0.95 GPa, 18. Their upright strength was only ≈ 5 MPa, i.e. poorly bonded. |
| [Li, Xu & Fang 2024, *Thin-Walled Struct.* 199](https://www.sciencedirect.com/science/article/pii/S026382312400243X) (search snippet only, unverified) | 0° / 90° / Z, Hill48 | E 2697 (0°), 2575 (90°), ≈ 2250 (Z), giving E2/E1 ≈ 0.95 and E3/E1 ≈ 0.83. |
| [Casavola et al. 2016, *Mater. Des.* 90:453](https://doi.org/10.1016/j.matdes.2015.11.009) | Same method (0°, 90°, ±45° plus CLT) | No numbers retrieved. |

**PA12-CF and CF-nylon analogues** (no PA12-CF lamina paper found)

| Source | Configuration | Values |
|---|---|---|
| [Dynamism PA12-CF TDS](https://dynamism.com/media/catalog/product/pdf/Dynamism_PA12-CF_TDS.pdf) | 2 shells, 100 % infill, ISO 527 / 178. Dry: annealed 80 °C 24 h. Wet: 3 days immersed. | **Dry:** E 3304 / 1801 (X-Y / Z), σ 71.6 / 43.3. **Wet:** E 3054 / 1520, σ 73.4 / 42.0. Wet/dry: **E_XY 0.92, E_Z 0.84, σ ≈ 1.0, flexural strength 0.92**. |
| [Polymaker Fiberon PA12-CF10](https://fiberon.polymaker.com/product/pa12-cf10/) (snippet; page returned 403) | X-Y / Z | E 3311 / 1807, σ 77.4 / 52.2. Probably the same base as Dynamism. |
| [BASF Ultrafuse PAHT CF15 TDS](https://forward-am.com/wp-content/uploads/2024/10/Ultrafuse_PAHT_CF15_TDS_EN_v3.5-1.pdf) | XY / XZ (on edge) / ZX (upright). Dry vs 23 °C / 50 % RH for 72 h. High-temperature PA matrix, not PA12. | **Dry:** E 8386 / – / 3532, σ 103 / – / 18.2. Flexural modulus XZ / ZX 7669 / 2715 (**≈ E1/E3 = 2.8**). ν = 0.44. **Conditioned:** E_XY ×0.60, E_Z ×0.70, Xt ×0.61. This PA6-type matrix is much more moisture-sensitive than PA12. |
| [Belei & Amancio-Filho 2024, *3DP&AM* 11:1921](https://doi.org/10.1089/3dp.2023.0173) ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11669830/)) | Ultrafuse PAHT CF15. 0.6 mm nozzle, 0.4 mm layers. ISO 527. | **UTS:** 0/90 111.3; ±45 **93.7** (D3518-style τ12 ≈ 47); ±30 106.4; ±60 95.2. |
| [Prusament PA11 CF TDS](https://prusament.com/wp-content/uploads/2022/08/TDS_PA11CFB.pdf) | 2 perimeters, 100 % rectilinear infill, as printed | Horizontal (±45 plus walls) vs on-edge. Tensile modulus 2.5 / 3.3 GPa. **Flexural modulus 3.0 / 6.2 GPa**; the on-edge bar's bending faces are perimeters, so it reads close to E1. |
| [CNC Kitchen, PA6-CF vs PA12-CF](https://www.cnckitchen.com/blog/carbon-fiber-nylon-in-3d-printing-pa6-vs-pa12-tested) | X-Y; PA12 at about 0.7 % water | **PA12-CF:** dry about 120 MPa, conditioned −15 %, stiffness unchanged within scatter. **PA6-CF:** 56 % of strength, about 1/3 of stiffness. |
| [Chabaud et al. 2019, *Addit. Manuf.* 26:94](https://www.sciencedirect.com/science/article/abs/pii/S2214860418309102) (abstract) | Continuous CF in a PA (Markforged) matrix, 98 % RH | Stiffness / strength fell 25 / 18 % longitudinally and 45 / 70 % transversely. |

No interlaminar shear data (short-beam or ILSS) was found for short-CF nylon FFF, so S13 and S23 are inferred.

## 4. Recommended sets (dry, as printed and annealed like the TDS bars)

| | **PLA Basic** | low–high | basis | **PAHT-CF** | low–high | basis |
|---|---|---|---|---|---|---|
| E1 | **2800** | 2500–3400 | [cal] E2/E1 = 0.93 and G12/E1 = 0.32 from Ferreira; reproduces the TDS X-Y 2580 | **7600** | 4600–9500 | [cal] reproduces TDS 3860 for walls at 17–25 %. The low end is the 0/90 scenario; the high end follows Prusament and BASF (on-edge flexural modulus 6.2–7.7 GPa) |
| E2 | **2600** | 2300–3100 | [lit] Ferreira 0.93·E1; Li 2024 0.95 | **2700** | 2300–3400 | [assum.] matrix-dominated, ≥ E3. Uses the PLA ratio E2/E3 = 1.24. E1/E2 = 2.8, against 1.9 for Ferreira's PLA-CF and 2.8 for BASF's flexural E1/E3 |
| E3 | **2060** | 1900–2400 | [TDS] Z modulus | **2180** | 1900–2400 | [TDS] Z modulus |
| G12 | **900** | 800–1100 | [lit] 0.32·E1 (Ferreira 1092 / 3376); Gonabadi 1.27 / 3.5 GPa | **950** | 800–1150 | [assum.] ≈ 0.35·E2 (Ferreira PLA-CF G12/E2 = 0.32). This value controls the calibrated E1 |
| G13 | **810** | 700–930 | 0.9·G12. Gonabadi: on-edge/flat 0.95, upright/flat 0.75 | **850** | 700–1000 | [assum.] 0.9·G12 |
| G23 | **760** | 650–900 | [assum.] E3 / (2(1+ν23)) | **770** | 650–900 | [assum.] E3 / (2(1+ν23)) |
| ν12 | **0.35** | 0.32–0.38 | [lit] Gonabadi 0.35 / 0.32; Ferreira 0.331 | **0.38** | 0.33–0.44 | [lit] Ferreira PLA-CF 0.40; BASF 0.44 |
| ν13 | **0.35** | 0.30–0.38 | [lit] Gonabadi upright ν31 ≈ 0.2 at E3/E1 = 0.57 gives ν13 ≈ 0.35 | **0.38** | 0.33–0.44 | [assum.] = ν12 |
| ν23 | **0.35** | 0.30–0.40 | [assum.] | **0.42** | 0.35–0.48 | [assum.] matrix-dominated |
| Xt | **48** | 38–55 | [cal] ±45/0° strength ratio 0.66 (Ferreira PLA) applied to TDS 35. Literature 0° values are 54.7–55 | **120** | 100–140 | [cal] ratio 0.71 (Ferreira PLA-CF) applied to TDS 92. CNC Kitchen PA12-CF ≈ 120; BASF 103 |
| Xc | **80** | 60–90 | [lit] Song Xc/Xt = 1.79 × 48 = 86, rounded down for this toughened grade | **100** | 75–130 | [assum.] Xc/Xt ≈ 0.85, usual for short fibre (fibre micro-buckling). The bending estimate 3σtσc/(σt+σc) = 125 gives a coupon σc ≥ 76 |
| Yt | **33** | 28–40 | [lit] Ferreira Yt/Xt = 0.68; ≥ Zt | **50** | 42–65 | [assum.] 1.06·Zt (the PLA ratio). Matrix/interface-dominated, so not scaled with Xt |
| Yc | **70** | 55–85 | [lit] Song Yc/Yt = 2.12 | **80** | 60–100 | [assum.] matrix compressive yield |
| Zt | **31** | 25–34 | [TDS] Z strength | **47** | 40–64 | [TDS] V3.0 (V2.0: 64; Polymaker 52; Dynamism 43) |
| Zc | **65** | 50–80 | [assum.] ≈ Yc, since interfaces close in compression | **75** | 60–100 | [assum.] ≈ Yc |
| S12 | **19** | 15–30 | [cal] Hashin ±45 core reproduces TDS 35. Ferreira D3518 18.0; Iosipescu pure shear (Gonabadi) up to 35. Use 16 with max-stress | **47** | 40–52 | [cal + lit] Hashin calibration 50; Belei ±45 gives τ12 ≈ 47; max-stress gives 43 |
| S13 | **18** | 14–27 | Zt/√3 = 17.9. Gonabadi upright 18, on-edge 27 | **33** | 25–44 | [assum.] between Zt/√3 = 27 and S12·Zt/Yt = 44 |
| S23 | **18** | 14–25 | as S13 | **30** | 22–40 | [assum.] ≤ S13, since no fibre crosses either plane |

All sets give a positive-definite compliance matrix, both dry and wet.

**PAHT-CF wet knock-down** (multiply the dry values; Bambu's numbers are used wherever they exist):

| Quantity | Factor | Range | Basis |
|---|---|---|---|
| E1 | 0.86 | 0.80–0.94 | Bambu flexural X-Y; Dynamism E_XY 0.92 |
| E2 | 0.83 | 0.80–0.92 | [assum.] between Bambu's X-Y and Z |
| E3 | 0.81 | 0.80–0.90 | Bambu flexural Z; Dynamism E_Z 0.84 |
| G12, G13, G23 | 0.81 | 0.75–0.90 | [assum.] matrix-dominated, like Z |
| ν | 1.0 | 1.0–1.15 | [assum.] |
| Xt | 0.92 | 0.85–1.0 | Bambu flexural X-Y strength; CNC Kitchen 0.85; Dynamism 1.0 |
| Xc | 0.85 | 0.80–0.92 | [assum.] matrix-yield-controlled |
| Yt, Yc | 0.85 | 0.80–1.0 | [assum.] |
| Zt, Zc | 0.80 | 0.80–0.97 | Bambu flexural Z strength; Dynamism σ_Z 0.97 |
| S12, S13, S23 | 0.82 | 0.78–0.95 | [assum.] |

**Caveats:**
- Bambu's wet state is "saturated at 25 °C / 55 % RH" by inference only. Do not use BASF's PA6-type factors (×0.60) for PAHT-CF.
- No moisture knock-down is given for PLA (water uptake 0.43 %).
- All values are room temperature and short-term. PLA creeps markedly at 40–50 °C (see [`materials_2026-09-27.md`](materials_2026-09-27.md)).
- E1 for PAHT-CF is the least certain number. A single 0° coupon plus one ±45° coupon printed on the H2D, with the same profile as the mount, would pin E1 and G12.

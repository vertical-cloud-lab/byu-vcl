# Build plate for printing ULTEM (PEI), issue #352

Question (sgbaird, 2026-11-17): what should a build plate be made of to print ULTEM?

## Answer

No single plate material makes ULTEM stick. What works is a **flat, heat-stable plate with a
renewable layer on top**, run at the **hottest bed the printer allows**.

1. **Best supported: borosilicate glass plus a high-temperature adhesive.** The adhesive can be
   Vision Miner Nano Polymer Adhesive, Magigoo HT, or PVP/PVA glue, at a 150-200 °C bed.
   - Thompson et al. 2026 (HardwareX) printed ULTEM 1010 on glass with at least 4 coats of Nano
     Polymer Adhesive, at a 200 °C bed and ~80 °C chamber. A brim was still needed.
   - Vakharia et al. 2023 (NASA Glenn) printed ULTEM 9085 on PVA-coated glass at a 200 °C bed.
   - Intamsys's FUNMAT HT guide prescribes the frosted side of glass with at least 4 layers of
     PVP glue, for both ULTEM 9085 (140 °C bed) and ULTEM 1010 (160 °C bed).
2. **Runner-up: polyimide (Kapton) film or tape on glass.** Shuttleworth 2020 used PI tape plus
   PVP at 150 °C. The film itself survives these temperatures; the tape's silicone adhesive is
   the weak point (about 260 °C).
3. **If the plate can't be glass: G-11/FR-5 glass-epoxy, not G-10/FR-4.**
   - G-10/FR-4 is rated about 130 °C and G-11/FR-5 about 155 °C (NEMA temperature index).
     The two are often sold interchangeably as "Garolite".
   - Essentium's 9085 sheet specifies "G-11 or MIC-6 Aluminum" with Magigoo HT or VM Nano, at a
     120-140 °C bed.
   - For a custom bed, use cast and stress-relieved MIC-6 tooling plate. A thin aluminium bed
     buckled about 1.5 mm at 150 °C (Shuttleworth 2020).

**Avoid:**

- **A bare PEI ("Ultem") sheet as the contact surface.** The part and the sheet are the same
  polymer, so welding is physically plausible. Edison found no study that measured it. Every
  documented success on a PEI sheet used an adhesive layer.
- **Bare glass.** It lost adhesion after a few prints.
- **Bare thin aluminium.** It buckles.
- **Dimafix.** It degrades above about 125 °C.
- **Plain G-10/FR-4 above about 130 °C.**

Stratasys's own route is different: a disposable "high temperature build sheet" with a raft of
support material printed first, so the part never touches the sheet. Stratasys does not publish
what the sheet is made of.

**Bed temperature matters more than the plate.** Fabrizio 2020 printed ULTEM on a PEI sheet with
Magigoo HT at three bed temperatures:

| Bed | Result |
| --- | --- |
| 120 °C | Significant warping, even with a 10 mm brim |
| 150 °C | Slight edge warp, after removal only |
| 180 °C | No significant warp |

### On the lab's Bambu Lab H2D

Bambu's spec maximums are a 350 °C nozzle, a 120 °C bed and a 65 °C chamber. That is the very
bottom of ULTEM 9085's window and below ULTEM 1010's 370 °C+ nozzle range, so on the H2D the
thermal limits matter more than the plate. Only small 9085 parts are realistic.

The one vendor recipe that reaches down to 120 °C is Essentium's: G-11 (or MIC-6) with Magigoo HT
or VM Nano.

## Vendor guidance (text read from the primary documents)

| Source | Grade | Surface | Bed °C | Chamber °C | Nozzle °C |
| --- | --- | --- | --- | --- | --- |
| [Intamsys FUNMAT HT guide](https://cdn.shopify.com/s/files/1/2327/6017/files/FUNMAT_HT_Printing_Process_Guide.pdf) | 9085 / 1010 | Frosted glass + ≥4 layers PVP glue. "Removing a print after it is cooled may cause the glass plate to break." | 140 / 160 | 90 | 360 / 370 |
| [Essentium 9085 TDS](https://nexa3d.com/wp-content/uploads/2024/08/TDS-Essentium-9085.pdf) | 9085 | "G-11 or MIC-6 Aluminum"; "Magigoo® HT or VM Nano" | 120-140 (150-185 HSE) | - | 360-390 |
| [BASF Ultrafuse PEI 9085 TDS](https://cdn.shopify.com/s/files/1/1339/4265/files/BASF_Ultrafuse_PEI_9085_TDS_EN_v1.1.pdf) | 9085 | Glass | 160-190 | 160-180 | 340-360 |
| [3D4Makers PEI 9085 TDS](https://cdn.shopify.com/s/files/1/0658/6459/7724/files/TDS_PEI_ULTEM_9085.pdf) | 9085 | PEI sheet | 120-160 | - | 350-380 |
| [Prusa, PEI (Ultem), HT90](https://help.prusa3d.com/article/pei-ultem_725809) | - | "2-3 layers of Magigoo HT and use a brim" | 150-155 | 85-90 | 370-420 |
| [3DXTech 9085 blog](https://www.3dxtech.com/blogs/featured/ultem%E2%84%A2-9085-pei-filament-aerospace-grade-3d-printing-filament-for-high-temperature-applications) | 9085 | not stated | 140-160 | ~190 for best properties | 350-380 |
| [Bambu H2D spec](https://bambulab.com/es/h2d/tech-specs) | - | - | max 120 | max 65 | max 350 |

## Edison outputs in this folder

| Query | Job | Files |
| --- | --- | --- |
| comparison: rank bed surfaces for ULTEM 9085/1010 | `paperqa3-high` | `comparison_task_id.json`, `literature_comparison_{task.json,answer.md,references.md,artifact-00.md,artifact-01.md}` |
| adhesion: quantitative adhesion data, and PEI-on-PEI welding | `paperqa3` | `adhesion_task_id.json`, `literature_adhesion_{task.json,answer.md,references.md}` |

Caveats on Edison's answers:

- **PVA glue.** The comparison answer says ordinary PVA glue "should not be used". Its own
  adhesion answer cites PVA-coated glass at a 200 °C bed (Vakharia 2023), and Intamsys uses PVP
  glue. Glue on glass is documented, so treat that line as unsupported.
- **Its 120 °C ranking is extrapolated.** Edison ranks glass + PI + Magigoo HT first for a
  120 °C-bed printer, and calls that ranking an "engineering extrapolation" itself.
- **Its 190-220 °C "ideal bed" is extrapolated too.** It comes from a PLA/ABS study (Spoerk 2018).
- **No ULTEM adhesion forces.** Neither query found a measured peel, shear or pull-off force for
  ULTEM on any build surface.

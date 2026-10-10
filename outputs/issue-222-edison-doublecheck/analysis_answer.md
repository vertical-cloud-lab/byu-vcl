## CONFIRMED

- **Interference-fit Lamé results:** for a 0.0254 mm diametral interference,
  \[
  p=\frac{E(\Delta d/d)(b^2-a^2)}{2b^2}=38.33\ \text{MPa},
  \]
  and the hub-bore hoop stress is
  \[
  \sigma_\theta(a)=p\frac{b^2+a^2}{b^2-a^2}=99.67\ \text{MPa}=0.906\,S_y.
  \]
  The elastic Lamé numbers **38.3 MPa and 99.7 MPa are confirmed**.
- **Press force:** the interface normal load is 14.568 kN, giving 5.827 kN at \(\mu=0.4\) and 17.481 kN at \(\mu=1.2\). Thus **0.594 and 1.783 metric tonne-force are confirmed**. In US press short tons, however, these are **0.655 and 1.965 ton-force**.
- **Free cup OD growth:** when the unsupported bore hoop stress first equals 110 MPa, \(p_i=42.31\) MPa and the open-ended Lamé OD growth is **0.000736 in**, confirming **0.00074 in** under that specific maximum-principal-stress calculation.
- **Common shop sizes:** 3/4-in 6063-T52 extruded round, 31/64-in drill, 1/2-in chucking reamer, 5/8-in cutting tools, 1/16-in and #60 drills, and 1-1/4-in and 2-in 1018 cold-finished rounds are all commonly stocked US sizes. Relevant specifications are ASTM B221 for the extruded aluminium product, ASTM A108 for cold-finished 1018 bar, ASME B94.11M for twist-drill dimensions, and ASME B94.2 for reamers. Examples of actual stock listings confirm [3/4-in 6063-T52](https://alcobrametals.com/product/3-4-6063-t52-extruded-round/), [1-1/4-in ASTM A108 1018](https://continentalsteel.com/item/cold-finished-bars/cold-finished-round-bar-type-1018/1018-1250), and [2-in 1018](https://www.speedymetals.com/p-706-2-rd-cold-finished-1018.aspx).
- **Reamer reach:** an ANSI/ASME-pattern 1/2-in straight-shank chucking reamer commonly has a **2.000-in flute length**, so it nominally reaches a 1.875-in-deep bore, with only 0.125 in spare. Confirm the selected tool and allow for its lead chamfer and blind-hole chip space; it will not itself create a sharp flat bottom. [ASME B94.2 scope and a dimensional listing](https://garvintools.com/product-detail/chucking-reamers-st-shank/).
- **Vent drills:** all three are standard:
  - 1/16 in = **0.06250 in = 1.5875 mm**;
  - 1 mm = **0.03937 in**;
  - #60 = **0.04000 in = 1.016 mm**.

  Standard jobber flute lengths are about 7/8 in for 1/16 and 11/16 in for #60, both exceeding the 0.375-in lid length. The 1 mm and #60 options are essentially equivalent, but neither is the nearest equivalent to 1/16 in. [ASME-based drill-size table](https://engineersedge.com/drill_sizes.htm) and [jobber-length dimensions](https://www.autodrill.com/resources/charts/jobber-length-drill-dimensions).
- **Thermal expansion magnitudes:** 1.4% for aluminium from room temperature to 600 °C is reasonable; 6063 data give ~23.4–25.6 µm/(m·K), corresponding to roughly 1.36–1.48%. Graphite at 0.3% is plausible but grade- and direction-dependent. [6063 thermal data](https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6063T6).

## ERRORS / CORRECTIONS

### 1. Fit yielding and friction

Although the quoted hoop stress is correct, comparing hoop stress alone with yield is unsafe. At the hub bore,

\[
(\sigma_r,\sigma_\theta,\sigma_z)=(-38.33,99.67,0)\ \text{MPa},
\]

so the von Mises stress is **123.38 MPa**, or **1.12 times** the 110 MPa minimum yield. The purely elastic solution therefore predicts local first yield. The corresponding elastic von-Mises limit is about **0.000892-in diametral interference**, not 0.001 in. Real edge effects and galling add uncertainty.

The range \(\mu=0.4\)–1.2 is **not a clean-dry static-friction range**. A commonly tabulated aluminium/aluminium pair gives **1.05–1.35 static** and about **0.4 sliding**; galling makes a single Coulomb coefficient especially unreliable. That static range predicts **1.56–2.01 metric tonne-force** (1.72–2.21 US short tons). The 0.4 value is more representative of established sliding than breakaway. [Friction table](https://www.engineeringtoolbox.com/friction-coefficients-d_778.html).

### 2. ANSI B4.1 fit class

For the ANSI B4.1 nominal range **over 0.40 through 0.56 in**, containing 0.500 in, the deviations from basic size are:

| Class | Hole limits, thou | Shaft limits, thou | Interference, thou | Actual dimensions at 0.500 in |
|---|---:|---:|---:|---|
| FN1 | +0.0 to +0.4 | +0.5 to +0.8 | **0.1 to 0.8** | hole 0.5000–0.5004; shaft 0.5005–0.5008 |
| FN2 | +0.0 to +0.7 | +1.2 to +1.6 | **0.5 to 1.6** | hole 0.5000–0.5007; shaft 0.5012–0.5016 |

Therefore **0.0005–0.0010 in is not wholly FN1**: 0.0005–0.0008 lies within FN1, but 0.0009–0.0010 does not. The complete proposed range is within FN2. Source: [ANSI B4.1 Table 9 reproduction](https://faculty.ksu.edu.sa/sites/default/files/fits_us_tables_ansi_b4.1-1967_r1987.pdf).

ANSI calls FN1 a **light drive fit** and says it is *suitable for thin sections or long fits*; it does not define FN1 exclusively as “the thin-section fit.” [Fit-class descriptions](https://amesweb.info/fits-tolerances/ansi-preferred-tolerances-fits-charts.aspx).

### 3. Sleeve

The 0.000736-in growth is only the point where bore **hoop stress** reaches 110 MPa. Yield criteria give earlier limits:

- open-ended, von Mises: \(p_i=34.18\) MPa and OD growth **0.000594 in**;
- ideal closed-ended region, using \(\nu_{Al}=0.33\): \(p_i=35.28\) MPa and OD growth **0.000512 in**.

Thus the practical “about 0.0005 in” clearance warning is reasonable when closed-end axial stress and von Mises yielding are included, but it does **not** follow from the quoted 0.00074-in hoop-only result. A guaranteed elastic design needs essentially line-to-line contact or intentional preload after accounting for tolerances, ovality and surface finish.

For a line-to-line 0.750-in-ID × 1.250-in-OD steel sleeve, taking \(E_s=200\) GPa, \(\nu_s=0.29\), and no initial clearance, coupled Lamé compatibility at 100 MPa gives:

- aluminium/steel contact pressure: **51.56 MPa**;
- steel hoop stress: **109.57 MPa at the ID**, **58.01 MPa at the OD**;
- maximum steel von Mises stress: **142.52 MPa at the ID**.

A closed-end aluminium correction changes these slightly to contact **53.24 MPa**, steel-ID hoop **113.14 MPa**, and steel-ID von Mises **147.18 MPa**. These are below typical cold-drawn 1018 yield values (~345–380 MPa in this size range), so **the steel sleeve itself is strong enough**. A published size-dependent sheet gives at least 50–55 ksi yield around 1.25–2 in diameter ([1018 cold-drawn data](https://nessteel.com/wp-content/uploads/2025/01/1018-Data-.pdf)). ASTM A108 by itself should not be treated as a universal guaranteed mechanical-property value; certify the purchased condition.

However, the sleeve does **not keep the 110 MPa-yield aluminium fully elastic** at 100 MPa internal pressure. At the aluminium bore the line-to-line solution gives

\[
(\sigma_r,\sigma_\theta) = (-100,74.38)\ \text{MPa},
\]

and von Mises stress **151.56 MPa**. First aluminium yield occurs at only ~**72.6 MPa internal pressure** in this linear coupled model. Thus the corrected verdict is: **steel safe, aluminium not elastically safe**. Intentional sleeve interference/prestress, a thicker aluminium wall, or a higher-strength insert is required if permanent set is unacceptable.

For reference, assuming the steel alone received the entire 100 MPa directly would give **212.5 MPa steel-ID hoop stress**, but that is not the compatible two-cylinder load split.

### 4. Sizes and machining details

| Item | Verdict / correction |
|---|---|
| 31/64 drill → 1/2 reamer | Diametral stock is **0.015625 in**, arithmetic confirmed. It is slightly above Hannibal’s stated 0.010–0.015-in finish-reaming range for a 0.500-in tool, although 31/64 is the nearest common fractional recommendation and drill oversize normally reduces actual stock. Prefer a measured prehole around **0.485–0.490 in**, chosen for the specific reamer and process. [Manufacturer guide](https://www.hannibalcarbide.com/wp-content/uploads/2024/02/cost-effective-reaming-guide.pdf). |
| 5/8 flat-bottom bore | **5/8 in is standard**, but “flat bottom” requires a counterbore, end mill, boring tool, or purpose-made flat-bottom drill—not an ordinary twist drill. It is a feature specification, not a unique standard drill operation. |
| 15° press-fit lead-in | **Valid and common design choice, but not a standardized mandatory value.** ASME Y14.5 governs how the chamfer is dimensioned, not a preferred 15° value. No nearest replacement is needed. |
| 0.015-in edge break | **Valid conventional drawing callout, but not a standardized preferred magnitude.** Specify its tolerance and whether it is a chamfer or merely a maximum edge break. No nearest replacement is needed. |
| “1018 CRS round” | Common shop language, but **1018 cold-finished/cold-drawn round per ASTM A108** is the more precise purchase description; round bar is not literally made by sheet-style cold rolling in many supply chains. |

### 5. Cold and hot packing

At the stated 16.000 mm pitch radius, with 19.05 mm aluminium cylinders, a 52 mm graphite bore and a 12 mm graphite rod:

| Clearance | Cold | At 600 °C, using Al ×1.014 and graphite ×1.003 |
|---|---:|---:|
| Cylinder to outer bore | **0.475 mm** | **0.372 mm** |
| Cylinder to central rod | **0.475 mm** | **0.372 mm** |
| Adjacent gap, four cylinders at 90° | **3.577 mm** | **3.379 mm** |
| Adjacent gap, five cylinders at 72° | **−0.241 mm** | **−0.451 mm** |

I allowed the graphite-defined 16 mm pitch radius to expand by 0.3%; if the centre locations remain fixed at exactly 16.000 mm hot, the hot inner and outer clearances instead become **0.324 and 0.420 mm**.

Therefore **four fit, but five do not fit on a 16.0 mm pitch radius**. Cold, five could be rearranged outward because they require at least **16.205 mm** pitch radius and the outer-bore maximum is **16.475 mm**. At 600 °C they require **16.432 mm**, but only **16.420 mm** is available, a **0.012 mm interference** even after outward rearrangement.

At 600 °C, 6063 is also close to its ~615 °C solidus; its T52 temper and room-temperature yield strength are not usable structural properties there. These are geometry-only hot-clearance results.

### 6. Masses

Using the dimensions exactly as stated and density 2.69 g/cm³:

| Part | Correct volume | Correct mass | Submitted value |
|---|---:|---:|---:|
| Cup | **12.0666 cm³** | **32.459 g** | 11.89 cm³, 31.98 g |
| Lid less 1.588 mm vent | **1.18773 cm³** | **3.195 g** | 1.173 cm³, 3.15 g |
| Solid 19.05 × 63.5 mm slug | **18.09896 cm³** | **48.686 g** | 18.08 cm³, 48.65 g |

The slug values are close but not exact; the cup and lid numbers are low. I treated all dimensions as nominal and ignored chamfers, tool-tip radii and surface finishes.

- **Discretionary analytical decisions:**
  - I used plane-stress Lamé theory for the primary press-fit and sleeve calculations, then separately showed the closed-end axial-stress correction.
  - I used von Mises stress, rather than maximum hoop stress alone, to assess yielding of these ductile metals.
  - I modeled the sleeve and cup as concentric, perfectly elastic cylinders with zero initial clearance; real tolerance and post-yield contact require nonlinear finite-element analysis or proof testing.
  - I interpreted “t” as metric tonne-force while also reporting US short tons because US hydraulic presses are commonly rated in short tons.
  - For the hot packing calculation, I assumed the bore, rod and pitch-location structure are graphite and the four outer cylinders are aluminium.

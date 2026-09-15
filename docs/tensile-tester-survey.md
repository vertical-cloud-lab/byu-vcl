# Mini tensile tester evaluation — AFRL/BYU capstone stage vs. alternatives

Context: [byu-vcl#215](https://github.com/vertical-cloud-lab/byu-vcl/issues/215). Compiled
2026-09-15. The literature half of this document came from an Edison
`LITERATURE_HIGH` run (task `80aba941-6bf1-4146-b3fb-9c961b0ecacb`); raw artifacts are in
[`outputs/tensile-tester-survey/`](../outputs/tensile-tester-survey/).

## 1. What the capstone machine actually is

From the poster: **BYU Capstone team SIGMA, 2022–2023, sponsored by the Air Force Research
Laboratory**, coached by Oliver Johnson. Members: Ethan Gardner, Jared Yates, Maren
Johnston, Tyler Schultz, Reid Ward, Adam Oldham.

The important framing detail is that **this was not a from-scratch build**. The stated
objective was to *"modify an existing tensile testing stage provided by the Air Force
Research Laboratory to eliminate bending in the test sample, support in-situ testing, and be
compatible for use with an optical microscope."* So the deliverable was a fix to an AFRL
stage, not a design the lab owns outright.

Architecture, from Fig. 1: a horizontal **dual opposed lead screw** stage with two carriages
driven symmetrically from a single gearmotor, so the gauge section stays centered while both
grips retract. That is the standard architecture for in-situ work — it keeps the region of
interest inside the objective's field of view for the whole test.

### Reported key success measures (Fig. 6)

| Measure | Initial | Ideal (target) | Actual (achieved) |
|---|---:|---:|---:|
| Percent bending of sample | 180 % | 5 % | **28 %** |
| Max load without yielding | 5 kN | 5 kN | **5 kN** |
| Min working distance (sample top → lens bottom) | 9 mm | < 9 mm | **7.8 mm** |
| Min distance between carriages | 0 mm | 10 mm | **12.6 mm** |

Three candidate root causes for the bending were tested: (1) sample not in the plane of
force, (2) excess clearance on the lead screws, (3) sample not contacting the whole grip.
Two prototypes followed — a *realignment* prototype that drops the sample plane inline with
the screw plane to kill the moment arm, and a *reduced clearance* prototype that tightens
the fit between load screws and threaded bushings so the carriages cannot tilt under load.
The final result (28 %) came from the reduced-clearance prototype plus shims.

### The honest read on those numbers

Two of the four measures **missed target**, and they are the two that matter:

- **Percent bending 28 % vs. a 5 % target.** The team picked 5 % because that is the
  conventional bending-strain limit for a well-aligned load train (ASTM E1012 quantifies
  alignment as the ratio of bending strain to axial strain; ≤5 % is the usual acceptance
  bar for E8/ISO 6892-1 work). 180 % → 28 % is a genuine 6.4× improvement and real
  engineering, but 28 % is still ~5.6× over the bar.
- **Minimum distance between carriages 12.6 mm vs. a 10 mm target**, and it got *worse*
  than the 0 mm starting point. This sets the shortest specimen the stage can grip.

Working distance (7.8 mm) and load capacity (5 kN) both met target.

What 28 % bending means in practice: **ultimate tensile strength will be roughly fine,
modulus and yield will not be.** Koko et al. (NPL, 2024) deliberately misaligned a Deben
stage by 2° and found UTS moved only from 46.8 to 46.6 MPa while the fracture mode flipped
from tensile to shear — i.e. *UTS agreement cannot be used to validate alignment.* Anything
depending on the elastic portion of the curve is compromised at 28 %.

## 2. Load capacity vs. what the VCL actually wants to test

This is the decisive calculation. [ac-dev-lab#451](https://github.com/AccelerationConsortium/ac-dev-lab/issues/451)
is about atomizing an in-house alloy and printing tensile/fatigue coupons — that is the
workload this stage would serve. A 5 kN ceiling sets the largest specimen cross-section:

| Alloy | Typical AM UTS | Max cross-section at 5 kN | Equivalent round specimen |
|---|---:|---:|---:|
| AlSi10Mg (as-built) | ~400–460 MPa | ~11–12.5 mm² | ~3.8–4.0 mm dia |
| SS316L (LPBF) | ~640 MPa | ~7.8 mm² | ~3.2 mm dia |
| 17-4PH (H900) | ~1100–1300 MPa | ~3.8–4.5 mm² | ~2.2–2.4 mm dia |
| 18Ni300 maraging | ~1100–2000 MPa | ~2.5–4.5 mm² | ~1.8–2.4 mm dia |

So 5 kN lands **exactly at the boundary** for the aluminum alloys the lab is already handling
(the AlSi10Mg and Al-1100 SDSs are in this repo): a 4 mm-diameter sub-size ASTM E8 round bar
of AlSi10Mg needs ~5.0 kN to fail. It works, with no margin. For the steels that
Additive Plus recommended in #451 for safety reasons (SS316L, 17-4PH, 18Ni300) you are pushed
to ~2–3 mm specimens, which is below standard sub-size E8 and into miniature-specimen
territory — where the size effect itself becomes a research variable rather than a nuisance.

Relevant standards context: the smallest geometry in ASTM E8/E8M is the 6 mm-wide sub-size
at 25 mm gauge length. ASTM F42.01 work item **WK75901** is actively developing a *miniature*
tension specimen at 10–15 mm gauge length specifically for AM metals, and AFRL's own
[AFRL-RX-WP-TR-2023-0057](https://apps.dtic.mil/sti/trecms/pdf/AD1202451.pdf) assessed
subscale specimen test methods. Sub-sized specimens consistently read *lower* yield and
tensile strength than full-size ones due to size effects.

## 3. What the Acceleration Consortium has been doing

| Issue | What it is | Status |
|---|---|---|
| [ac-dev-lab#140](https://github.com/AccelerationConsortium/ac-dev-lab/issues/140) | Umbrella: build a low-cost, open-source tensile or compression tester, WiFi-enabled | Open since 2025-01-07 |
| [ac-dev-lab#352](https://github.com/AccelerationConsortium/ac-dev-lab/issues/352) | The actual build — paired Actuonix T16 track actuators, crush plate setup | Open, active through 2025-08 |
| [ac-dev-lab#151](https://github.com/AccelerationConsortium/ac-dev-lab/issues/151) | Driving application — BO of 3D-printed resin lattice compressive strength | Open since 2025-01-16 |
| [ac-dev-lab#451](https://github.com/AccelerationConsortium/ac-dev-lab/issues/451) | Atomize an in-house alloy, print coupons, mechanically test them | Open since 2025-09-04 |

Design as it stands in #352: two Actuonix T16 track actuators at 64:1 gearing (chosen over
256:1 for safety), rigidly coupled, **~200 N working max**, aluminum-extrusion frame after an
all-3D-printed first draft, 3D-printed compression platens and tensile grips, Raspberry Pi
Zero 2 W + Actuonix LAC control. Fusion 360 [design](https://a360.co/3HFtYbx) and a
[BOM](https://docs.google.com/document/d/1Wp7zpH_Hkz3KkFWVvlrlRCnG6Pnzgpu30aDLOMM2tjU/edit)
exist.

Three conclusions from those threads are worth importing directly:

1. **Current draw was abandoned as a force proxy.** The original idea was to skip the load
   cell and infer force from actuator current. Kelvin Chow's [objection](https://github.com/AccelerationConsortium/ac-dev-lab/issues/352#issuecomment-3128374776)
   settled it — the LAC board cannot report current anyway, so an external sensor was needed
   regardless, and if you're adding a sensor it should be a load cell.
2. **Plastic actuator carriages take a moment under off-axis load.** Kelvin's diagram flagged
   that a force applied away from the actuator axis bends the carriage, and that the distance
   between the two actuators should be minimized. *This is the same failure mode the capstone
   poster spent a year on* — different hardware, identical physics.
3. **It has already bitten them.** In #151, Chance's first lattice compression run produced
   [unusable data](https://github.com/AccelerationConsortium/ac-dev-lab/issues/151#issuecomment-2607873157)
   because "the plate tilted during compression." That run peaked at ~701 N — already 3.5×
   over the T16 pair's ~200 N budget, incidentally.

## 4. Recent designs the January-2025 search missed

Issue #140 listed four references (Instructables UTM v2, FreeLoader, Liu's UofT thesis,
Open Pull). The Edison run surfaced these, all post-dating that list:

| Design | Year | Capacity | Cost | Notes |
|---|---:|---:|---:|---|
| [**MT-02**](https://doi.org/10.34726/hss.2024.113842) (Demmel, TU Wien) | 2024 | 3.5 kN rated (5 kN cell) | not stated | Closest open-source analogue to the capstone stage. 2× NEMA 17 + twin SFU1605 ball screws, aluminum profile frame, Arduino + touchscreen, FreeCAD/KiCad. **Validated against a ZwickRoell RetroLine** |
| [**DIY-EMTT**](https://doi.org/10.1016/j.ohx.2024.e00546) (Wiranata et al., *HardwareX*) | 2024 | 98 N | **US$173** | CC BY-SA 4.0, full CAD + LabVIEW GUI released. Adds a resistance meter for electromechanical testing. Soft/stretchable materials |
| [**Camelot**](https://doi.org/10.1186/s12915-025-02216-9) (Trozzi et al., *BMC Biology*) | 2025 | 0.1 N – tens of N | ~£60 in actuator + cell | Interchangeable beam load cells (~10 µN resolution on the 10 g cell), **camera-based optical tracking at ~5 µm**, open-source MorphoRobotX. The extensometry approach is the transferable part |
| [**MicroStretch**](https://www.hardware-x.com/article/S2468-0672(25)00115-4/fulltext) (*HardwareX*) | Jan 2026 | low (soft samples) | **< US$100** | Bipolar stepper + lead screw + Arduino, 3D-printed PLA, designed to sit on a microscope stage for live imaging |
| [**Koko, Fry & Mingard**](https://doi.org/10.47120/npl.mat128) (NPL report) | 2024 | — | — | **Not a machine — the single most useful reference here.** Quantified uncertainty of in-situ micromechanical testing of AM materials against an Instron 5969 |
| [**APEX**](https://doi.org/10.2172/2584738) (LLNL + Cornell) | 2025 | — | — | Closest thing to the end goal: DED → automated grind/polish → microscopy → hardness → **compression test**, 48 samples/day, ML-guided. Extensible target 2027 |
| [**CrackPy / cobot-DIC**](https://doi.org/10.21203/rs.3.rs-3128435/v1) (Strohmann et al., DLR) | 2023 | 4.5–15 kN | — | KUKA LBR iiwa carrying a microscope to CNN-identified crack tips on a servo-hydraulic rig. Open-source Python |
| [**Random combinatorial libraries**](https://doi.org/10.1557/s43577-026-01078-y) (Chawla et al.) | 2026 | — | — | Hundreds of compositions in one epoxy mount, SEM-EDS mapped, ~45 s/indent nanoindentation with BO-guided site selection |

Also new since the #140 list: [Simonovski et al. 2025](https://doi.org/10.3389/fmats.2025.1609564)
on small punch testing of AM 316L, and [Cannon et al. 2026](https://doi.org/10.1007/s11665-026-14603-6)
on small punch repeatability. **EN 10371** small punch uses an 8 mm × 0.5 mm disc — far less
material than any tensile coupon, with published correlations reaching R² > 0.95 at ±10 %.

For reference, the **FreeLoader** from #140's original list is 5 kN, ±1.8 N, 2–30 mm/min,
under US$4,000 — the same load class as the capstone stage, at known cost, with published
validation, but *not* an in-situ stage.

## 5. Accuracy pitfalls, quantified

From the NPL report and the MT-02 validation — these are the numbers to design against:

| Error source | Magnitude |
|---|---|
| Crosshead-derived modulus | MT-02 **underestimated Young's modulus by 48 %** vs. video extensometry |
| Machine/fixture compliance | 2.5 µm/N (one benchtop frame); ~0.8 µm/N (Deben, pin-mounted) |
| 2° specimen misalignment | Fracture mode tensile → shear; UTS moved only 46.8 → 46.6 MPa |
| Specimen diameter variation of 70 µm | **14 % uncertainty in stress** |
| Load cell zero offset | ~2.1 ± 1.3 N phantom force |
| Commanded vs. actual displacement, 5 kN single-leadscrew rig | R² = 0.79, i.e. **>20 % inconsistency** |
| Linear compliance correction validity | Only to ~0.5 % strain (AlMg3), ~1 % (PA6) |

The compliance correction is `ΔL = ΔX − C_total·P`, and it must be re-measured after any
change of grips, load cell, fixture or specimen geometry.

## 6. Recommendation

**Take the stage if AFRL will part with it, but scope it as an in-situ microscopy
accessory, not as the lab's tensile tester.**

It is strong where it is unusual: dual opposed lead screws keeping the gauge section
stationary, 7.8 mm working distance under an objective, 5 kN in a stage that fits on a
microscope. No open-source design found does all three — the closest, MT-02 at 3.5 kN, is a
benchtop frame with no microscope compatibility. Commercially the nearest equivalents are
Deben's dual-leadscrew stages and Kammrath & Weiss's symmetric designs, in the
$15k–50k+ band. Getting one for free is worth real effort.

It is weak exactly where a general-purpose tester needs to be strong: 28 % bending rules out
trustworthy modulus and yield; 5 kN caps AlSi10Mg at ~4 mm round sub-size specimens with no
margin, and pushes the steels of #451 to ~2–3 mm; 12.6 mm minimum carriage separation
constrains specimen length; and the poster documents no load-cell calibration, no
extensometry, and no automation interface.

Before committing, get answers to:

1. **Is it actually available, and on what terms?** It is AFRL property that a BYU team
   modified. Ask Oliver Johnson, who coached the team.
2. **What is the load cell and is it calibrated?** The poster says "5 kN max load without
   yielding" — a *structural* claim about the frame, not a measurement spec. Capacity,
   resolution, and calibration traceability are all unreported.
3. **What drives it, and can it be scripted?** No controller, software, or data interface
   appears anywhere on the poster. For SDL integration this is the long pole.
4. **Did the 28 % ever come down?** The poster is the 2022–23 endpoint; there may be later
   work.

If it lands, the sequence should be: re-measure bending per ASTM E1012 with a strain-gauged
alignment specimen (the capstone's percent-bending measurement was their own, not a
standardized one) → characterize `C_total` with a stiff reference specimen → add DIC or
video extensometry through the microscope, which the stage's own geometry makes unusually
easy → only then trust a stress-strain curve.

Independently of that decision, **the AC's ~200 N T16 build is not a path to metal tensile
testing** — it is 25× short of this stage and ~7× short of the 701 N that #151's resin
lattices already needed. It should stay pointed at polymer/lattice compression. For metals,
the tiered structure the literature converges on is: nanoindentation or hardness for
screening → small punch (EN 10371, 8 mm × 0.5 mm discs) as the intermediate tier → sub-size
E8 tensile with real extensometry for validation. A 5 kN in-situ stage is a reasonable
validation-tier instrument for aluminum; it is not a screening tool.

## References

Full Edison output, including the complete reference list with DOIs, is in
[`outputs/tensile-tester-survey/`](../outputs/tensile-tester-survey/) —
`answer.md`, `formatted_answer.md`, `references.md`, and the two comparison-table artifacts.

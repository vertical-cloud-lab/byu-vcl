# Aconity MIDI 3D Printing Setup — University of Utah (Speer Collab)

Related to issues [#46](https://github.com/vertical-cloud-lab/byu-vcl/issues/46), [#45](https://github.com/vertical-cloud-lab/byu-vcl/issues/45), and [#47](https://github.com/vertical-cloud-lab/byu-vcl/issues/47).

---

## 1. System Overview

| Parameter | Details |
|---|---|
| **Machine** | Aconity MIDI |
| **Location** | University of Utah |
| **Collaboration** | Speer Lab (contact: Alik) |
| **Process** | Laser Powder Bed Fusion (LPBF) |

---

## 2. Powder — AlSi10Mg

| Parameter | Value |
|---|---|
| **Material** | AlSi10Mg |
| **Supplier SDS** | `AlSi10Mg-sds-from-heegermaterials [not MSE supplies].pdf` (in repo) |
| **Max tap density** | 1.7 g/cm³ |
| **Hopper fill requirement** | 3× the intended print height |
| **Powder supply hopper diameter** | 170 mm |
| **Build platform diameter** | 170 mm |

### 2.1 Powder Quantity Calculation (First Print)

- Intended print height: **6 mm**
- Required hopper fill height: 3 × 6 mm = **18 mm**
- Hopper volume (cylinder, r = 85 mm, h = 18 mm): π × 85² × 18 ≈ 408,407 mm³ ≈ 408 cm³
- Required powder mass: 408 cm³ × 1.7 g/cm³ ≈ **695 g**
- Powder currently on hand: **~800 g** ✓ (sufficient)

> Note: Carl Robison needed ~25–40 g (18 mL) for a separate shipment, leaving ~760–775 g on hand — still sufficient for the ~695 g required.

---

## 3. Part Geometry — Dog-Bone Tensile Specimen

Dimensions taken from the drawing provided in issue #47:

| Dimension | Value |
|---|---|
| **Overall length** | 100 mm |
| **End width** | 10 mm |
| **Gauge length** | 32 mm |
| **Gauge width** | 6 mm |
| **Part thickness (print height)** | 6 mm |

![Dogbone tensile specimen drawing](https://github.com/user-attachments/assets/c19534f9-a41c-408f-b0f0-01bc5ea9bb1b)

---

## 4. Build Plate

| Parameter | Details |
|---|---|
| **Material** | Aluminum 6061 (6000-series) |
| **Fabricated by** | Alik (U of Utah) |
| **Bonding note** | AlSi10Mg expected to bond well to 6000-series aluminum per Alik |

---

## 5. Print Setup

| Parameter | Details |
|---|---|
| **Post-processing** | As-built (no heat treatment) |
| **Powder drop-off** | Ronnie Guymon delivers powder to Alik |
| **Expected start** | Friday at the earliest (after Thursday drop-off) |

---

## 6. Contacts

| Role | Name | Notes |
|---|---|---|
| **U of Utah operator** | Alik | Aconity MIDI operator; fabricated Al 6061 build plate |
| **U of Utah coordinator** | Ashley | Point of contact at Speer Lab |
| **BYU VCL — powder** | Ronnie Guymon | Delivering AlSi10Mg powder |
| **BYU VCL — PI** | Sterling Baird (@sgbaird) | Project oversight |
| **BYU VCL — reference** | Carl Robison | Used Al 6061 for build plates on related issue #61 (Luis/3D Powder Tech) |

---

## 7. Next Steps

- [ ] Confirm print date with Alik after powder drop-off
- [ ] Receive as-built tensile specimens from U of Utah
- [ ] Characterize printed parts (density, microstructure, tensile properties)
- [ ] Evaluate AlSi10Mg bonding to Al 6061 build plate
- [ ] Order additional AlSi10Mg powder if needed for future prints (current stock ~800 g; one print requires ~695 g)

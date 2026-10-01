# Plate Reader Options for BYU VCL

Research into microplate (plate) reader options that can be controlled with Python, including new, used, and refurbished availability. Top-loading is preferred, but side-loading is also acceptable.

> **Reference model:** [Byonoy Absorbance 96](https://byonoy.com/absorbance-96/) (~$5,500 new)

## Summary Comparison

| Model | Detection Modes | Loading | Python Control | New Price | Used/Refurb Price | Plate Formats |
|---|---|---|---|---|---|---|
| [Byonoy Absorbance 96](#byonoy-absorbance-96) | Absorbance | Top | ✅ Native (pyserial, PyLabRobot) | ~$5,500 | N/A | 96-well |
| [Opentrons Flex Absorbance Plate Reader](#opentrons-flex-absorbance-plate-reader-module) | Absorbance | Top (robotic) | ✅ Native (Opentrons Python API) | $14,850 | N/A | 96-well |
| [BMG CLARIOstar / CLARIOstar Plus](#bmg-labtech-clariostar--clariostar-plus) | Abs, FL, Lum, TRF, FP | Side (drawer) | ✅ Native (PyLabRobot) | ~$60K–$90K | $16K–$31K | 6–1536-well |
| [BMG SPECTROstar Nano](#bmg-labtech-spectrostar-nano) | Absorbance | Side (drawer) | ⚠️ ActiveX/DDE (pywin32) | ~$20K–$30K | ~$9K | 96/384-well + cuvette |
| [BioTek Epoch 2](#biotek-agilent-epoch-2) | Absorbance | Side (drawer) | ⚠️ Gen5 scripting + CSV export | $11.5K–$21K | $5K–$10K | 6–384-well + cuvette |
| [BioTek Synergy H1](#biotek-agilent-synergy-h1) | Abs, FL, Lum | Top | ⚠️ Gen5 scripting + CSV export | ~$29K | $15K–$19K | 6–384-well |
| [BioTek Synergy HTX](#biotek-agilent-synergy-htx) | Abs, FL, Lum | Top | ⚠️ Gen5 scripting + CSV export | ~$15K–$20K | $2.5K–$7K | 6–384-well |
| [Molecular Devices SpectraMax Mini](#molecular-devices-spectramax-mini) | Abs, FL, Lum | Side (drawer) | ⚠️ SoftMax Pro export | Quote req. | N/A (too new) | 6–384-well |
| [Molecular Devices SpectraMax M2/M2e](#molecular-devices-spectramax-m2m2e) | Abs, FL, Lum | Side (drawer) | ⚠️ SoftMax Pro export | Discontinued | $5K–$7K | 6–384-well |
| [Open-Source Plate Reader (OSP)](#open-source-plate-reader-osp) | Abs, FL | Top | ✅ Native (Python/Raspberry Pi) | ~$3,500 (DIY) | N/A | 96-well |

**Legend:** ✅ = direct Python instrument control available; ⚠️ = indirect control via proprietary software scripting, COM/ActiveX, or data export

---

## Detailed Options

### Byonoy Absorbance 96

The reference model from the original issue. Ultra-compact, USB-powered absorbance reader.

| Spec | Value |
|---|---|
| **Detection** | Absorbance (endpoint, kinetic) |
| **Wavelengths** | 4 LEDs (up to 6 on Automate model), 400–1000 nm |
| **Detectors** | 96 photodiodes (one per well) |
| **OD Range** | 0–4.0 OD |
| **Resolution** | 0.001 OD |
| **Read Time** | ~3 seconds (single wavelength, full plate) |
| **Plate Format** | 96-well |
| **Loading** | **Top-loading** (open design, no moving parts) |
| **Size / Weight** | 9.6 × 15.4 × 5.5 cm / <1 kg |
| **Power** | USB (5V, 2.5W) |
| **Price (new)** | ~$5,500 |
| **Price (used/refurb)** | N/A (relatively new product) |

**Python Control:**
- Community Python library: [`kasper64/absorbance96`](https://github.com/kasper64/absorbance96) (pyserial-based)
- [PyLabRobot integration](https://docs.pylabrobot.org/user_guide/02_analytical/plate-reading/byonoy/absorbance.html) for the Automate model
- CSV/PDF export from bundled Windows/macOS app

**Pros:**
- Extremely compact and portable
- Direct Python control
- Very fast reads
- Top-loading
- Low cost

**Cons:**
- Absorbance only (no fluorescence or luminescence)
- 96-well only
- Fixed wavelength LEDs (not a monochromator)

**Links:** [Product page](https://byonoy.com/absorbance-96/) · [Datasheet (PDF)](https://lablogic.com/data/file/b/8/Byonoy-Absorbance-96-Datasheet-EU-Version-1.2.1640166501.pdf) · [Enzo listing](https://www.enzo.com/product/absorbance-96-plate-reader/)

---

### Opentrons Flex Absorbance Plate Reader Module

Designed for the Opentrons Flex liquid-handling platform; requires a Flex robot for full automation.

| Spec | Value |
|---|---|
| **Detection** | Absorbance (endpoint, kinetic) |
| **Wavelengths** | 400–1000 nm (standard filters: 450, 562, 600, 650 nm; custom available) |
| **Detectors** | 96 photodiodes |
| **OD Range** | 0–4.0 OD |
| **Resolution** | 0.001 OD |
| **Plate Format** | 96-well (flat bottom) |
| **Loading** | **Top-loading** (automated via Flex Gripper) |
| **Size / Weight** | 9.6 × 15.5 × 5.7 cm / ~790 g |
| **Power** | USB (5V, 2.5W) |
| **Price (new)** | $14,850 (module only; Flex robot sold separately) |
| **Price (used/refurb)** | N/A (new product) |

**Python Control:**
- Full [Opentrons Python API](https://docs.opentrons.com/python-api/modules/absorbance-plate-reader/) support
- Open/close lid, initialize wavelengths, read plates, export results
- Designed for fully automated walkaway workflows

**Pros:**
- Native, well-documented Python API
- Seamless integration with Opentrons Flex ecosystem
- Top-loading with robotic plate handling

**Cons:**
- Requires Opentrons Flex robot ($25K+) for full functionality
- Absorbance only
- Not available in Europe (patent restrictions)
- 96-well only

**Links:** [Product page](https://opentrons.com/products/opentrons-flex-absorbance-plate-reader-module-gen1) · [Python API docs](https://docs.opentrons.com/python-api/modules/absorbance-plate-reader/) · [Brochure (PDF)](https://insights.opentrons.com/hubfs/Products/Flex/Opentrons%20Flex_Absorbance%20Plate%20Reader%20Brochure.pdf)

---

### BMG LABTECH CLARIOstar / CLARIOstar Plus

High-end multimode reader with native Python support via PyLabRobot. Best-in-class sensitivity.

| Spec | Value |
|---|---|
| **Detection** | Absorbance, Fluorescence (incl. FRET), Fluorescence Polarization, Luminescence (incl. BRET), TRF, AlphaScreen/AlphaLISA |
| **Wavelengths** | 220–1000 nm (UV/Vis abs); ~240–740 nm (fluorescence) |
| **Optical System** | Dual Linear Variable Filter Monochromators + high-sensitivity filters |
| **Plate Formats** | 6–1536-well |
| **Loading** | **Side-loading** (motorized plate drawer) |
| **Temperature** | Ambient +3°C to 65°C |
| **Price (new)** | ~$60,000–$90,000 |
| **Price (used/refurb)** | ~$16,000–$31,000 |

**Python Control:**
- ✅ Native support via [PyLabRobot](https://docs.pylabrobot.org/user_guide/02_analytical/plate-reading/bmg-clariostar.html)
- Serial-over-USB communication
- Supports plate loading tray operation, absorbance/fluorescence/luminescence reads
- Active development for additional features

**Pros:**
- Best Python integration among full-featured readers (PyLabRobot)
- Multimode detection with excellent sensitivity
- Supports up to 1536-well plates
- Robotic automation compatible

**Cons:**
- Expensive even used ($16K+)
- Side-loading (drawer-based)
- Large benchtop footprint

**Links:** [LabX listings](https://www.labx.com/product/bmg-labtech-clariostar) · [PyLabRobot docs](https://docs.pylabrobot.org/user_guide/02_analytical/plate-reading/bmg-clariostar.html) · [ALT listing](https://americanlaboratorytrading.com/lab-equipment-products/bmg-labtech-clariostar-plus-plate-reader-21426/)

---

### BMG LABTECH SPECTROstar Nano

Absorbance-focused reader with cuvette port. Older model with wide used availability.

| Spec | Value |
|---|---|
| **Detection** | Absorbance (UV/Vis) |
| **Wavelengths** | 220–1000 nm (monochromator-based) |
| **Plate Formats** | 96/384-well + cuvette holder |
| **Loading** | **Side-loading** (plate drawer) |
| **Read Speed** | ~1 second per 96-well plate |
| **Price (new)** | ~$20,000–$30,000 |
| **Price (used/refurb)** | ~$9,000 |

**Python Control:**
- ActiveX/DDE interface controllable via Python (`pywin32`)
- ASCII data output for automated parsing
- No dedicated Python API; custom scripting required

**Pros:**
- Full UV/Vis spectrum via monochromator
- Cuvette port for single-sample work
- Affordable refurbished units

**Cons:**
- Absorbance only
- Requires Windows and custom scripting for Python control
- Side-loading

**Links:** [BMG product page](https://www.bmglabtech.com/en/spectrostar-nano/) · [LabX listings](https://www.labx.com/product/bmg-labtech-spectrostar-nano)

---

### BioTek (Agilent) Epoch 2

Widely used absorbance spectrophotometer. Monochromator-based for full UV/Vis range.

| Spec | Value |
|---|---|
| **Detection** | Absorbance |
| **Wavelengths** | 200–999 nm (1 nm increments, monochromator) |
| **Light Source** | Xenon flash lamp |
| **Plate Formats** | 6–384-well; optional Take3 micro-volume plate; optional cuvette port |
| **Loading** | **Side-loading** (plate drawer) |
| **Read Speed** | ~8 sec / 96-well; ~14 sec / 384-well |
| **Temperature** | 4-zone incubation up to 65°C |
| **Shaking** | Linear, orbital, double orbital |
| **Price (new)** | ~$11,500–$21,000 (config dependent) |
| **Price (used/refurb)** | ~$5,000–$10,000 |

**Python Control:**
- Controlled via Gen5/Gen6 software (no direct Python API)
- Data export to CSV/Excel for Python analysis
- Compatible with BioStack plate stacker for automation

**Pros:**
- Full UV/Vis spectrum
- Wide plate format support
- Good used/refurbished availability and pricing
- Incubation and shaking built in
- Spectral scanning capability

**Cons:**
- No direct Python instrument control
- Side-loading
- Absorbance only

**Links:** [Fisher Scientific](https://www.fishersci.com/shop/products/epoch-2-microplate-spectrophotometer-10/BTEPOCH2NS) · [LabX listings](https://www.labx.com/product/biotek-microplate-reader) · [BioSPX specs](https://www.biospx.com/product/epoch-2/)

---

### BioTek (Agilent) Synergy H1

Multimode reader with monochromator and filter-based optics. Top-loading design.

| Spec | Value |
|---|---|
| **Detection** | Absorbance, Fluorescence (top/bottom), Luminescence |
| **Wavelengths** | 200–999 nm (abs); filter cubes for FL |
| **Plate Formats** | 6–384-well |
| **Loading** | **Top-loading** |
| **Temperature** | Incubation up to 65°C |
| **Shaking** | Linear, orbital, double orbital |
| **Price (new)** | ~$29,000 |
| **Price (used/refurb)** | ~$15,000–$19,000 |

**Python Control:**
- Gen5 software with automation scripting
- Data export to CSV/Excel for Python analysis
- No direct Python API

**Pros:**
- Top-loading ✓
- Multimode detection
- Full UV/Vis monochromator
- Incubation and shaking

**Cons:**
- Expensive, even used
- No direct Python instrument control

**Links:** [AmpTech listing](https://www.amptechfl.com/products/biotek-synergy-h1-multimode-microplate-reader-w-gen-5-software) · [LabX listings](https://www.labx.com/product/biotek-microplate-reader)

---

### BioTek (Agilent) Synergy HTX

Budget multimode reader. Top-loading. Good availability on used market.

| Spec | Value |
|---|---|
| **Detection** | Absorbance, Fluorescence, Luminescence |
| **Wavelengths** | Filter-based |
| **Plate Formats** | 6–384-well |
| **Loading** | **Top-loading** |
| **Temperature** | Incubation to 50°C |
| **Shaking** | Linear, orbital |
| **Price (new)** | ~$15,000–$20,000 |
| **Price (used/refurb)** | ~$2,500–$7,000 |

**Python Control:**
- Gen5 software with data export
- No direct Python API

**Pros:**
- Top-loading ✓
- Very affordable used ($2.5K–$7K)
- Multimode detection
- Widely available on secondary market

**Cons:**
- Filter-based (not monochromator)
- No direct Python instrument control

**Links:** [LabX listings](https://www.labx.com/product/biotek-microplate-reader) · [Bimedis listings](https://bimedis.com/biotek-synergy-ht-m468157/refurbished) · [ALT listings](https://americanlaboratorytrading.com/lab-equipment-manufacturers/biotek_1342/)

---

### Molecular Devices SpectraMax Mini

Newer compact multimode reader. Upgradeable detection modes.

| Spec | Value |
|---|---|
| **Detection** | UV/Vis Absorbance, Fluorescence, Luminescence (user-upgradeable from 2 to 3 modes) |
| **Wavelengths** | 200–1000 nm (xenon flash) |
| **Plate Formats** | 6–384-well |
| **Loading** | **Side-loading** (ejectable plate drawer) |
| **Size / Weight** | ~40 × 32 × 35 cm / ≤18 kg |
| **Price (new)** | Quote required (est. <$10,000 for base config) |
| **Price (used/refurb)** | N/A (too new for secondary market) |

**Python Control:**
- SoftMax Pro software; data export to Excel/XML/PDF
- No public Python API/SDK
- Robotic-compatible for automation workflows

**Pros:**
- Compact, modular, upgradeable
- UV range (200 nm) capability
- Potentially affordable for a multimode reader

**Cons:**
- No direct Python instrument control
- Side-loading
- Limited used availability

**Links:** [Product page](https://www.moleculardevices.com/products/microplate-readers/multi-mode-readers/spectramax-mini-reader) · [Brochure (PDF)](https://www.moleculardevices.com/sites/default/files/en/assets/brochures/br/spectramax-mini-microplate-reader.pdf)

---

### Molecular Devices SpectraMax M2/M2e

Discontinued but widely available used multimode reader.

| Spec | Value |
|---|---|
| **Detection** | Absorbance, Fluorescence, Luminescence |
| **Wavelengths** | 200–1000 nm (dual monochromators) |
| **Plate Formats** | 6–384-well |
| **Loading** | **Side-loading** (plate drawer) |
| **Price (new)** | Discontinued |
| **Price (used/refurb)** | ~$5,000–$7,000 |

**Python Control:**
- SoftMax Pro software
- Data export for Python analysis
- SoftMax Pro SDK available (separate license; ~$760/yr academic)

**Pros:**
- Affordable used
- Full UV/Vis monochromator
- Multimode detection
- Widely available on secondary market

**Cons:**
- Discontinued (limited manufacturer support)
- Side-loading
- SDK requires paid license

**Links:** [LabX listings](https://www.labx.com/product/molecular-devices-spectramax) · [Certified refurbished program](https://www.moleculardevices.com/products/additional-products/certified-refurbished-instruments)

---

### Open-Source Plate Reader (OSP)

DIY, fully Python-controlled plate reader from the University of Pennsylvania Chow Lab.

| Spec | Value |
|---|---|
| **Detection** | Full-spectrum absorbance and fluorescence |
| **Sensitivity** | ~10 nM fluorescent dyes |
| **Control** | Python + Raspberry Pi (touchscreen GUI) |
| **Plate Format** | 96-well |
| **Loading** | **Top-loading** |
| **Build Cost** | <$3,500 |

**Python Control:**
- ✅ Fully Python-controlled from the ground up
- Custom Python API on Raspberry Pi
- Open-source hardware and software

**Pros:**
- Lowest cost option
- Complete Python control
- Top-loading
- Both absorbance and fluorescence
- Fully open-source and customizable
- Optogenetic stimulation capability

**Cons:**
- Requires assembly (DIY build)
- Not commercially validated/supported
- May lack precision of commercial instruments
- No manufacturer warranty or service

**Links:** [GitHub (brianchowlab/OSP)](https://github.com/brianchowlab/OSP) · [Publication](https://par.nsf.gov/servlets/purl/10087608) · [C&EN article](https://cen.acs.org/analytical-chemistry/diagnostics/Building-DIY-plate-reader/97/web/2019/01)

---

## Python Integration Summary

Readers with **native** Python instrument control (can send commands directly to hardware):

| Reader | Python Library | Notes |
|---|---|---|
| Byonoy Absorbance 96 | [`kasper64/absorbance96`](https://github.com/kasper64/absorbance96), [PyLabRobot](https://docs.pylabrobot.org/) | pyserial-based; Automate model via PyLabRobot |
| Opentrons Flex Module | [Opentrons Python API](https://docs.opentrons.com/python-api/modules/absorbance-plate-reader/) | Requires Opentrons Flex robot |
| BMG CLARIOstar | [PyLabRobot](https://docs.pylabrobot.org/user_guide/02_analytical/plate-reading/bmg-clariostar.html) | Serial-over-USB; actively developed |
| Open-Source Plate Reader | [GitHub (brianchowlab/OSP)](https://github.com/brianchowlab/OSP) | Custom Python API on Raspberry Pi |

Readers with **indirect** Python integration (data export / COM automation):

| Reader | Integration Method |
|---|---|
| BMG SPECTROstar Nano | ActiveX/DDE via `pywin32` (Windows only) |
| BioTek Epoch 2 | Gen5 scripting + CSV export |
| BioTek Synergy H1/HTX | Gen5 scripting + CSV export |
| SpectraMax Mini | SoftMax Pro export |
| SpectraMax M2/M2e | SoftMax Pro export; SDK available (paid) |

---

## Recommendations

### Best overall value with Python control
**Byonoy Absorbance 96** (~$5,500 new) — The reference model is actually an excellent choice if absorbance-only is sufficient. Top-loading, compact, direct Python control, and affordable.

### Best for automation integration
**Opentrons Flex Absorbance Module** ($14,850) — If the lab already has or plans to acquire an Opentrons Flex, this provides seamless Python-driven automation. Top-loading via robotic gripper.

### Best multimode with Python control
**BMG CLARIOstar** ($16K–$31K used/refurb) — The only full-featured multimode reader with native PyLabRobot support. Excellent sensitivity across all detection modes. Side-loading is a trade-off.

### Best budget multimode (used)
**BioTek Synergy HTX** ($2.5K–$7K used) — Top-loading multimode reader at very low used prices. No direct Python control, but data export to CSV is straightforward for analysis workflows.

### Best DIY/educational option
**Open-Source Plate Reader (OSP)** (<$3,500 build cost) — Full Python control, both absorbance and fluorescence, top-loading. Ideal if the lab has the capacity to build and maintain custom equipment.

---

## Vendor Checklist (Questions to Ask)

When requesting quotes, consider asking:

- [ ] What wavelengths are available / included?
- [ ] What software is included and what are ongoing licensing costs?
- [ ] Is there a Python SDK/API, or what automation interfaces are supported?
- [ ] What plate formats are supported (96, 384, 1536)?
- [ ] Is temperature control / incubation included?
- [ ] Is shaking included?
- [ ] What is the loading mechanism (top vs. side/drawer)?
- [ ] For used/refurbished: what is the warranty period and what has been serviced?
- [ ] What are annual service contract costs?
- [ ] Is the unit compatible with robotic plate stackers or liquid handlers?

## Where to Find Used/Refurbished Units

- [LabX](https://www.labx.com/categories/microplate-readers)
- [New Life Scientific](https://newlifescientific.com/collections/microplate-readers)
- [American Laboratory Trading (ALT)](https://americanlaboratorytrading.com/)
- [Bimedis](https://bimedis.com/)
- [Machinio](https://www.machinio.com/)
- [DOTmed](https://www.dotmed.com/)
- [eBay](https://www.ebay.com/sch/i.html?_nkw=microplate+reader)
- [Cambridge Scientific](https://www.cambridgescientific.com/product-category/microplate-readers)
- [Molecular Devices Certified Refurbished](https://www.moleculardevices.com/products/additional-products/certified-refurbished-instruments)

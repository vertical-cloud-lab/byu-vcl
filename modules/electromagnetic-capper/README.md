# Electromagnetic Vial Capper/Decapper Module

Magnet-based (rotation-free) vial capping/decapping module for automated liquid handling,
replicated from the **PANDA-film** self-driving lab developed by Keith A. Brown's group
(KABlab) at Boston University.

- **Paper:** Quinn, H.; Robben, G. A.; Zheng, Z.; Yan, J.; Li, Y.; Yang, Z.; Politi, M.;
  Peek, N.; Pozzo, L.; Werner, J. G.; Brown, K. A. *PANDA-film: an automated system for
  electrodeposition of polymer thin films and their wetting analysis.*
  [arXiv:2601.07043](https://arxiv.org/abs/2601.07043) (2026). CC BY 4.0.
  A copy is committed in [`paper/`](paper/) together with its license.
- **Source hardware/software repo:** [BU-KABlab/PANDA-BEAR](https://github.com/BU-KABlab/PANDA-BEAR) (GPL-2.0)
- **Arduino firmware:** [BU-KABlab/PANDA_Arduino](https://github.com/BU-KABlab/PANDA_Arduino)
- **Community discussion:** [Electromagnetic capper thread on accelerated-discovery.org](https://accelerated-discovery.org/t/electromagnetic-capper/579)
- **Tracking issue:** vertical-cloud-lab/byu-vcl#147

## How it works

Commercial capper/decappers grip and rotate caps. This design avoids rotary motion
entirely: a small **5 V, 50 N electromagnet** mounted on the gantry head picks up
custom **press-fit caps that carry a steel disc**, and an **IR break-beam sensor**
confirms successful cap pickup and replacement (paper Figure 2A–B).

Custom caps are fabricated by:

1. 3D printing the cap body in **PLA** (the authors used a Bambu A1; any well-tuned FDM
   printer works) — [`cad/VialCap16mm.step`](cad/VialCap16mm.step)
2. Filling the cap interior with **PDMS (Sylgard 184, 10:1 base:crosslinker)** for
   chemical resistance and sealing
3. Affixing a **steel disc with 3M adhesive** into the recessed region on top of the cap

The electromagnet sits in a 3D-printed holder
([`cad/PAW-V2-ElectromagnetMount.step`](cad/PAW-V2-ElectromagnetMount.step)) alongside
the IR break-beam sensor. It is switched by an Arduino Uno through an IRLZ44 logic-level
MOSFET with a 1N5819 flyback diode across the coil.

**Validated performance (paper §3.1, Figure 2C):** 100% capping/decapping success with
tolerance to **~3 mm of vertical approach-height misalignment**, tested across five
independently fabricated caps × 10 decap/recap cycles per height step (0.2 mm steps).

## Contents

| Path | Description |
|------|-------------|
| [`BOM.md`](BOM.md) | Bill of materials for the ME order (procure + print + fabricate) |
| [`paper/panda-film-2601.07043.pdf`](paper/panda-film-2601.07043.pdf) | The paper (arXiv:2601.07043, CC BY 4.0) |
| [`paper/LICENSE-CC-BY-4.0.txt`](paper/LICENSE-CC-BY-4.0.txt) | Paper license |
| [`cad/VialCap16mm.step`](cad/VialCap16mm.step) | Custom vial cap (print one per stock vial) |
| [`cad/PAW-V2-ElectromagnetMount.step`](cad/PAW-V2-ElectromagnetMount.step) | Electromagnet + sensor mount for the gantry head |
| [`cad/9VialHolder20mL_TightFit.step`](cad/9VialHolder20mL_TightFit.step) | 9-position 20 mL vial rack for the deck |
| [`cad/LICENSE-GPL-2.0.txt`](cad/LICENSE-GPL-2.0.txt), [`cad/NOTICE.txt`](cad/NOTICE.txt) | License/notice for the CAD files (from PANDA-BEAR) |

Note on sources: the paper was submitted to arXiv as PDF only — no LaTeX source is
available from the e-print endpoint (it returns the identical PDF), so only the PDF is
committed here.

## Build references

- [PANDA-BEAR Construction Guide](https://github.com/BU-KABlab/PANDA-BEAR/blob/main/documentation/Construction.md) — PAW assembly, parts checklist
- [PANDA-BEAR Arduino Wiring](https://github.com/BU-KABlab/PANDA-BEAR/blob/main/documentation/Arduino-Wiring.md) — circuit diagrams (electromagnet MOSFET driver, IR sensor)
- [PANDA-BEAR full BOM](https://github.com/BU-KABlab/PANDA-BEAR/blob/main/documentation/documents/bom.md) — complete PANDA-film parts list (superset of this module)
- [3D print files (all)](https://github.com/BU-KABlab/PANDA-BEAR/tree/main/documentation/3D-prints)

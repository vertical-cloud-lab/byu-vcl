# Pipette selection for the CubXL

Research notes toward choosing a single-channel pipette / dispensing head for the CubXL
automated liquid-handling workcell.

## Requirements

- **Budget:** strictly < $2,000; ideally **$100–$300**.
- **Specs:** similar to an Opentrons **OT-2 GEN2** pipette (air-displacement, disposable tips).
- **Volume class:** 20 µL **or** 300 µL — **lean 300 µL**, since we already run a 20 µL pipette on the OT-2.
- **Priority:** open-source designs, and **especially any that are open-source AND commercially sold**.

## Baseline: OT-2 P300 GEN2 (the spec target)

The Opentrons P300 GEN2 single-channel pipette covers **20–300 µL** with:

| Volume | Accuracy | Precision (CV) |
|-------:|:--------:|:--------------:|
| 20 µL  | ±4%      | ±2.5%          |
| 150 µL | ±1%      | ±0.4%          |
| 300 µL | ±0.6%    | ±0.3%          |

It is itself **open-source hardware that is commercially sold** — the cleanest example of the
"open-source AND commercial" category. The catch is **price and control coupling**: the standalone
single-channel pipette lists at roughly **$1,250 (2024 price list) up to ~$2,950 (current product
page)**, and it expects the OT-2's CAN-bus control electronics. Mounting one on a non-Opentrons
motion system is possible (see Science Jubilee below) but is not a $100–300 solution.
It fits the < $2k ceiling but **not** the preferred $100–300 target.

## Options surveyed

### 1. Acceleration Consortium "Digital Pipette" (recommended budget option)
- **Repo:** `ac-rad/digital-pipette` (also mirrored under AccelerationConsortium tooling).
- **Design:** 3D-printed body driving a Luer syringe (e.g. NORM-JECT 10 mL) with an **Actuonix
  L16-100-63-6-R** linear actuator (74 g, 100 N max), controlled by Arduino / Raspberry Pi Pico W.
- **Cost:** ~**$150–$200** BOM (actuator ~$100, MCU ~$25, syringe/hardware ~$15–30) — squarely in
  the target range.
- **License:** open source (CC-BY-4.0 hardware / MIT firmware).
- **Volume:** set by the syringe geometry rather than fixed to 20/300 µL; a ~300 µL working range is
  achievable by choosing syringe bore + actuator stroke.
- **v2 (2026):** *Digital pipette: open hardware for liquid transfer in self-driving laboratories*
  (Digital Discovery, DOI [10.1039/D5DD00336A](https://doi.org/10.1039/D5DD00336A)) reports a
  redesign that supports **robotic disposable-tip exchange** and liquid-handling accuracy **within
  ISO 8655-2 tolerances** — much closer to OT-2-class behavior than v1.
- **Jubilee integration:** a **Science Jubilee adapter** exists (AC forum thread #255) — relevant
  because the CubXL is a Jubilee/OT-2-style gantry.
- **Commercial availability:** no turnkey commercial product; it is build-it-yourself.

### 2. Pipettin-bot / OLA (Open Lab Automata)
- **Repo/docs:** `gitlab.com/pipettin-bot`, docs at `docs.openlabautomata.xyz`.
- **Volume:** **2–1000 µL** using OLA's own micropipettes; adapters exist for commercial pipettes
  (e.g. Gilson Pipetman).
- **License:** hardware **CERN-OHL-S v2**, software **AGPL-3.0**.
- **Cost:** positioned as low-cost vs. $10k+ commercial robots; no published single-tool BOM.
- **Commercial availability:** documentation/DIY-focused; no assembled kit sales advertised.

### 3. Science Jubilee "pipette tool" (mounts an OT-2 pipette)
- **Docs:** science-jubilee pipette tool — mounts an **Opentrons OT-2 pipette** (20/300/1000 µL) as
  a Jubilee tool-changer head with disposable tips.
- **Why it matters:** gives genuine OT-2 P300 accuracy on a Jubilee-class motion system, but inherits
  the OT-2 pipette's cost. Open-source adapter + commercial pipette hybrid.

### 4. Other open-source liquid handlers (context, not drop-in heads)
- **Sidekick** — low-cost 3D-printed dispensing robot (open source).
- **Open-source personal pipetting robots** (Nature Communications, 2022) and various modular
  frameworks — useful reference designs but whole-robot rather than a single mountable head.

## Preliminary recommendation

For a **~300 µL, < $300, open-source** head closest to OT-2 P300 GEN2 behavior:

1. **Build the AC Digital Pipette v2** (ISO 8655-2-compliant, tip-exchange capable, ~$150–200,
   existing Jubilee adapter). Best fit for the stated budget and specs.
2. If **true OT-2 P300 accuracy** is required and budget can stretch toward the < $2k ceiling, mount
   an **Opentrons P300 GEN2** via the **Science Jubilee pipette tool** — the strongest
   "open-source AND commercially sold" answer, at ~$1,250+.
3. **Pipettin-bot / OLA** is the fallback if we want a fully documented open ecosystem spanning
   2–1000 µL, accepting more integration work and no assembled-kit purchase path.

## Sources
- Digital Pipette (v1): Digital Discovery, DOI 10.1039/D3DD00115F
- Digital Pipette (v2, 2026): Digital Discovery, DOI 10.1039/D5DD00336A
- AC forum: improvements to the digital pipette (#236), Science Jubilee adapter (#255),
  Pipettin-bot follow-up (#345), equipment validation & automation (#517)
- `ac-rad/digital-pipette`; AccelerationConsortium/ac-dev-lab issues #143, #146
- Pipettin-bot / OLA: gitlab.com/pipettin-bot, docs.openlabautomata.xyz
- Science Jubilee pipette tool docs; Opentrons P300 GEN2 white paper & product page

## Edison Scientific cross-check (peer-reviewed literature)

A high-effort Edison Scientific (FutureHouse PaperQA) literature query was run in parallel
(task `becbd72a-0746-40ac-ba46-b8835b91b577`, `job-futurehouse-paperqa3-high`). Its answer is
grounded in ~10 peer-reviewed sources and both **confirms** and **corrects** the survey above.

### Key correction: the Digital Pipette is a *milliliter-scale* device, not 300 µL

The most important finding. Edison's read of the primary papers is that **both Digital Pipette
versions operate an order of magnitude above the 300 µL target**:

- **v1** (Yoshikawa 2023, [10.1039/d3dd00115f](https://doi.org/10.1039/d3dd00115f)) — validated
  around a **10 mL** syringe (~0.2% random error at 10 mL); syringe/Luer tips, **no disposable
  200–300 µL tip support**.
- **v2** (Yoshikawa 2026, [10.1039/d5dd00336a](https://doi.org/10.1039/d5dd00336a)) — ~**$270**
  air-displacement redesign with robotic tip exchange, but its **validated range is 0.2–10 mL**,
  using **BRAND 1–10 mL** tips. Gravimetric ISO 8655-6 testing was done at **1, 5, and 10 mL**
  (systematic error −0.49% to −0.10%, CV 0.10–0.58%).

So the earlier write-up's implication that the Digital Pipette v2 is a drop-in ~300 µL, OT-2-P300
replacement is **not supported**: hitting 300 µL would require a smaller-syringe redesign and fresh
validation, not an off-the-shelf build. It remains the **most Jubilee-ready** open design (a
sub-$100 Jubilee mount is demonstrated in Pelkie 2025), just not at the target volume as published.

### New option surfaced: FINDUS (best open-source volume-range match)

Edison surfaced **FINDUS** (Barthels 2020, SLAS Technology,
[10.1177/2472630319877374](https://doi.org/10.1177/2472630319877374)) — an open-source 3D-printable
liquid handler (<$400 full system, ~50 h build) that drives **standard P200 (20–200 µL) / P1000
(200–1000 µL)** pipettes with a NEMA 11 stepper, ESP8266 control, **<0.3% error, ISO 8655
compliant**, and **standard disposable tips**. Its **P200 module is the closest volume-range match
to the OT-2 P300 class** of any open-source design found, and the stepper drive is naturally
Duet3D/RepRapFirmware-compatible. Catch: it's built into its own Cartesian gantry, so you'd extract
and adapt the pipette subassembly for a Jubilee tool-changer (custom mechanical work).

Other designs Edison flagged: **OTTO** (Florian 2020, ~$1,500, ~2.5% error — within budget but less
accurate), **Sidekick** (Keesey 2022, ~$710, **dispense-only, no aspiration, no tips** — not a
general pipette replacement), and **Pipettin-bot/OLA** (no validated pipette-head specs in the
peer-reviewed literature).

### Edison's ranked recommendation (300 µL, <$300, open-source, OT-2-like)

1. **FINDUS pipette subassembly (P200 module)** — best volume match (20–200 µL), best documented
   accuracy (<0.3%, ISO 8655), standard tips, stepper-based → Jubilee-friendly. Needs mechanical
   adaptation off its native gantry.
2. **AC Digital Pipette v2, redesigned downward** — best-documented low-cost open build with a
   demonstrated Jubilee adapter, but 300 µL sits at the extreme bottom of its 0.2–10 mL validated
   range (redesign + revalidation required).
3. **Science Jubilee OT-2 P300 adapter** — closest to *true* OT-2 P300 behavior (~0.7% accuracy,
   ~0.15% CV, standard Opentrons tips) via a demonstrated 3D-printed adapter (Pelkie 2025), but the
   pipette itself is proprietary and hard to source standalone; effective cost likely above $300.
4. **AC Digital Pipette v1** — cheapest (<$200), simplest, but Luer-syringe / no disposable tips and
   a worse fit for 300 µL semantics than v2.

### On "open-source AND commercially sold"

Edison reaches the **same conclusion** as the survey but states it more starkly: **no design was
found that is simultaneously (a) open-source hardware, (b) sold assembled or as a kit, (c) in the
20–300 µL range, and (d) built to integrate with a custom motion platform.** The nearest
"open + commercial" embodiment is still **Opentrons** — practically, an **OT-2 P300 mounted via the
Science Jubilee adapter** — but the pipette remains proprietary. Edison explicitly calls this an
**open-hardware gap / opportunity**.

### Where Edison agrees with the survey

- OT-2 P300 GEN2 is the accuracy/precision baseline (Edison cites ~0.7% accuracy, ~0.15% CV).
- The Science Jubilee adapter is the cleanest OT-2-class-on-Jubilee route (Pelkie 2025 — note
  S. Baird is a co-author).
- The AC Digital Pipette is the most reproduced / Jubilee-ready open design.
- No turnkey commercial version of the sub-$300 open designs exists.

### Net effect on the recommendation

- If you want the **closest published open-source match to OT-2 P300 volumes/specs at <$300**, the
  strongest lead is now **adapting the FINDUS P200 pipette drive**, not the Digital Pipette.
- If you want the **easiest Jubilee integration** and can tolerate a volume redesign, the
  **Digital Pipette v2** is still attractive (existing Jubilee mount, active development).
- If you want **guaranteed OT-2 accuracy** and can spend toward the ceiling, the **Science Jubilee +
  OT-2 P300** hybrid remains the safest, at the cost of true openness and a higher price.

### Additional peer-reviewed sources (from Edison)

- FINDUS — Barthels et al., SLAS Technology 2020, [10.1177/2472630319877374](https://doi.org/10.1177/2472630319877374)
- OTTO — Florian et al., Scientific Reports 2020, [10.1038/s41598-020-70465-5](https://doi.org/10.1038/s41598-020-70465-5)
- Sidekick — Keesey et al., HardwareX 2022, [10.1016/j.ohx.2022.e00319](https://doi.org/10.1016/j.ohx.2022.e00319)
- Digital Pipette v1 — Yoshikawa et al., Digital Discovery 2023, [10.1039/d3dd00115f](https://doi.org/10.1039/d3dd00115f)
- Digital Pipette v2 — Yoshikawa et al., Digital Discovery 2026, [10.1039/d5dd00336a](https://doi.org/10.1039/d5dd00336a)
- Science Jubilee / democratizing SDLs — Pelkie et al., ChemRxiv 2025, [10.26434/chemrxiv-2025-zhkrf](https://doi.org/10.26434/chemrxiv-2025-zhkrf)
- Flexible pipette-based tool changes — Nazeri et al., HardwareX 2025, [10.1016/j.ohx.2025.e00653](https://doi.org/10.1016/j.ohx.2025.e00653)
- Low-cost 3D printing for lab automation (review) — Doloi et al., Digital Discovery 2025, [10.1039/d4dd00411f](https://doi.org/10.1039/d4dd00411f)
- Adapting a low-cost pipetting robot (nanoliter) — Councill et al., SLAS Technology 2021, [10.1177/2472630320973591](https://doi.org/10.1177/2472630320973591)
- Robotic liquid-handling in genomics (commercial context) — Tegally et al., BMC Genomics 2020, [10.1186/s12864-020-07137-1](https://doi.org/10.1186/s12864-020-07137-1)
- Open hardware review — Wenzel, PLOS Biology 2023, [10.1371/journal.pbio.3001931](https://doi.org/10.1371/journal.pbio.3001931)

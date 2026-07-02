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

> An Edison Scientific literature query was submitted in parallel to expand and cross-check this
> survey; its findings are appended below once available.

# pH meter options for the Cub XL

Research for [issue #148](https://github.com/vertical-cloud-lab/byu-vcl/issues/148): find a set of recommended pH meters/probes for the Cub XL, ideally something that (a) does not need to be stored in water, (b) is small enough to fit in a standard 20 mL scintillation vial, and (c) — stretch goal — combines ionic conductivity + pH + temperature in one probe.

## Constraints and context

**Vial geometry.** A standard 20 mL scintillation vial is 28 mm OD × 61 mm tall with a 22-400 neck finish, which gives a mouth opening of roughly 15 mm ID ([Sigma-Aldrich V7005](https://www.sigmaaldrich.com/US/en/product/sigma/v7005)). So any probe ≤ 12 mm OD passes through the neck with a little clearance; a ≤ 8 mm probe is comfortable.

**Prior art in ac-dev-lab.** Three related issues were reviewed:

- [ac-dev-lab#447](https://github.com/AccelerationConsortium/ac-dev-lab/issues/447) (parent): pH probe testing. Key takeaway from the thread: *"Atlas Scientific needs to be continually immersed during storage it seems, and the InLab 710 doesn't have pH it seems."*
- [ac-dev-lab#448](https://github.com/AccelerationConsortium/ac-dev-lab/issues/448): Atlas Scientific [pH kit](https://atlas-scientific.com/kits/ph-kit/) testing. Interfacing was worked out (UART↔USB adapter, or I2C via the [I2C toggler](https://atlas-scientific.com/ezo-accessories/i2c-toggler/); Python support via [`atlas_i2c`](https://github.com/timboring/atlas_i2c)). The blocker was wet storage, not electronics.
- [ac-dev-lab#446](https://github.com/AccelerationConsortium/ac-dev-lab/issues/446): Mettler Toledo InLab 710 — turned out to be conductivity-only (no pH).

**The two ways to satisfy "no wet storage":**

1. Buy a sensor technology that genuinely tolerates dry storage — in practice that means **ISFET (solid-state) pH sensors** (or optical patches). Glass-membrane electrodes, including "Tris-compatible flat" variants, all want wet storage.
2. Keep a conventional glass probe and **automate the wet storage** — park the probe in a 20 mL vial of storage solution and use the Cub XL's capper/decapper to cap that vial around the probe (or a press-fit cap) whenever the system is idle. This is the idea proposed in issue #148 and is by far the cheapest robust option.

## Recommended options

### Tier 1 — pragmatic default: Atlas Scientific Mini pH + automated storage vial

| Spec | Value |
|---|---|
| Probe | [Mini Lab Grade pH Probe (ENV-20-pH)](https://atlas-scientific.com/probes/mini-ph-probe/) ([datasheet](https://files.atlas-scientific.com/l-mini_pH_probe.pdf)) |
| Dimensions | **12 mm OD × 62.4 mm** — fits through a 22-400 vial neck |
| Range / accuracy | pH 0–14, ±0.002, 95% response in 1 s |
| Interface | SMA → [EZO-pH circuit](https://atlas-scientific.com/circuits/ezo-ph-circuit/) (I2C or UART; Python: [`atlas_i2c`](https://github.com/timboring/atlas_i2c)); works with Pico W / Pi |
| Storage | **Wet** (ships with a 10 mL pH ~3.8 soaker bottle) |
| Price | ~$90 (≈ €89.95 at [Sensors & Probes](https://sensorsandprobes.com/products/mini-ph-probe)) |
| Life | ~2 yr working, ~1 yr recalibration interval |

This is the same electronics ecosystem already de-risked in ac-dev-lab#448, in a package 88 mm shorter than the standard [Lab Grade probe (ENV-40-pH)](https://files.atlas-scientific.com/pH_probe.pdf) (12 mm × 150.6 mm, which also fits the vial neck but is long). An even thinner [Micro pH Probe](https://atlas-scientific.com/probes/micro-ph-probe/) exists for very tight spaces.

**Storage automation (the issue-#148 idea):** dedicate one parked 20 mL vial containing pH-4/KCl storage solution as the probe's "home" position. When idle, the robot dips the probe into that vial; the capper/decapper (or a slotted press-fit cap on the probe shaft) closes the vial to limit evaporation. Top up/replace the solution on a schedule. This converts a wet-storage probe into a hands-off component — the main failure mode is evaporation, which a capped vial makes slow.

### Tier 2 — genuinely dry-storable: ISFET (non-glass) pH sensors

ISFETs can be stored dry and used without preparation — this was verified experimentally for three commercial ISFETs in [Ziebart et al., *ChemistryOpen* 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12680566/) (Winsense had the highest slope, 59.7 mV/pH; Microsens the best precision, ±0.01–0.03 pH; Sentron the best stability; Microsens/Sentron modules cost €120–180 and Winsense ~€15 per sensor).

**Turnkey: Sentron (now a Millar company) wireless probes** — [product family](https://millar.com/our-expertise/off-the-shelf-products/probes):

- **MicroFET** — **3 mm tip diameter**, 110 mm barrel; pH 0–14; NTC temperature sensor; trivially fits a 20 mL vial (needs only 7–8 mm liquid depth per the [Sysmatec listing](https://sysmatec.ch/en/product/isfet-micro-ph-probe-sentron-microfet/)).
- ConeFET / LanceFET / CupFET — larger-tip variants, same electronics.
- Pricing: ~€920 per wireless probe (MicroFET +€115) at [ESTEDE Scientific](https://en.estede-scientific.com/Sentron-ISFET-wireless-pH-Meters); all include temperature.
- Caveats: current generation is **Bluetooth LE + phone/tablet app** (up to 6 probes). There is no documented Python API, so SDL integration means either BLE reverse-engineering (e.g. with `bleak`) or exporting via the app. The older cabled SI400/SI600 meter line is discontinued.

**DIY / OEM module: Winsense WIPS ISFET** ([winsense.co.th](http://www.winsense.co.th/products.html), [sensor datasheet](https://tmec.nectec.or.th/public/uploaded/products/isfet/ISFET2016/ISFET%20pH%20Sensor.pdf)) — ~€15 per sensor, dry storage, but you build the readout (TI's [LMP91200](https://www.ti.com/product/LMP91200) pH AFE is designed for exactly this) plus a reference electrode. Cheap enough to treat sensors as consumables; best fit if a Pico-W-based "IoLT" node is attractive. Microsens' MSFET 3330 (€120–180) is the higher-precision OEM alternative per the ChemistryOpen paper.

**Process-grade: Endress+Hauser Memosens CPS47E** ([product page](https://www.endress.com/en/field-instruments-overview/liquid-analysis-product-overview/digital-pH-sensor-Memosens-CPS47E)) — 12 mm ISFET in PEEK, pH 0–14, digital inductive Memosens coupling. Very robust, but it uses a liquid KCl reference (shouldn't be allowed to dry out completely), needs a Memosens transmitter, and sensor + transmitter lands well north of $1k. Overkill for the Cub XL unless long unattended campaigns in aggressive media are planned.

**Note on a common near-miss:** the Vernier [Go Direct Tris-Compatible *Flat* pH](https://www.vernier.com/product/go-direct-tris-compatible-flat-ph/) ($179) is sometimes suggested for small samples, but it is still a **glass** electrode and requires wet (pH-4/KCl) storage — it does not solve the storage problem.

### Tier 3 — the conductivity + pH + temperature question

A true single-body pH/EC/T probe that fits a 20 mL vial doesn't really exist at hobby/lab prices:

- **Hanna HI98129 "Combo"** ([product page](https://hannainst.com/hi98129-ph-ec-tds-tester.html), $224.99) measures pH + EC (0–3999 µS/cm) + TDS + temperature in one pocket tester, and its pH cartridge is replaceable — but it's a handheld (163 × 40 × 26 mm) meant to be dunked in a beaker, has no digital interface for automation, and the pH cell still needs wet storage. Fine as a manual cross-check instrument, not as the Cub XL's sensor.
- **Sentron multiparameter probes** (above) get pH + temperature (+ EC on some LanceFET variants) in one dry-storable tip — the closest thing to the stretch goal, at ~€1k.
- **Recommended modular path:** stay in the Atlas EZO ecosystem and stack the parameters on one I2C bus:
  - pH: Mini pH probe + EZO-pH (Tier 1)
  - Conductivity: [Mini Conductivity Probe K 1.0 (ENV-20-EC-K1.0)](https://atlas-scientific.com/probes/mini-e-c-probe-k-1-0/) ([datasheet](https://files.atlas-scientific.com/Mini_EC_K_1.0_probe.pdf)) — **12 mm OD × 84 mm**, 5–200,000 µS/cm, ±2%, graphite electrodes, **stores dry**, ~10-year recalibration interval — + EZO-EC circuit
  - Temperature: PT-1000 probe + EZO-RTD circuit (also enables temperature compensation for both pH and EC)

  All three EZO circuits speak I2C from a single Pico W / Pi, matching the interfacing already explored in ac-dev-lab#448. Conductivity probes have no wet-storage problem, so only the pH probe needs the parking-vial treatment.

## Comparison summary

| Option | Fits 20 mL vial? | Dry storage? | pH acc. | EC/Temp? | Automation interface | Approx. cost |
|---|---|---|---|---|---|---|
| Atlas Mini pH + EZO-pH | ✅ 12 mm | ❌ (parking vial fixes) | ±0.002 | via EZO-EC/RTD | I2C/UART, Python | ~$90 + $65 circuit |
| Atlas Lab Grade pH Kit (ac-dev-lab#448) | ✅ 12 mm (150 mm long) | ❌ | ±0.002 | via EZO | I2C/UART, Python | ~$165 kit |
| Sentron MicroFET (wireless) | ✅✅ 3 mm | ✅ ISFET | ~±0.01–0.1 | Temp ✅ | BLE app (no official API) | ~€1035 |
| Winsense WIPS ISFET module | ✅ (bare die/probe) | ✅ ISFET | slope 59.7 mV/pH | build your own | custom AFE (LMP91200) | ~€15/sensor + electronics |
| E+H Memosens CPS47E | ✅ 12 mm | ⚠️ (liquid KCl ref.) | high | Temp ✅ | Memosens transmitter | >$1k |
| Hanna HI98129 Combo | ❌ handheld | ❌ | ±0.05 | EC+TDS+Temp ✅ | none (manual) | $225 |
| Vernier GDX-FPH flat pH | ~ (flat tip) | ❌ glass | ±0.2 typ. | Temp via GDX | BT/USB (godirect-py) | $179 |

## Bottom line

1. **Cheapest robust path (recommended start):** Atlas Scientific **Mini pH probe + EZO-pH** on I2C, with the probe parked in a capped 20 mL storage-solution vial handled by the capper/decapper when idle. Add **Mini EC K1.0 + EZO-EC** and **EZO-RTD** for the conductivity + temperature wishes — the EC probe stores dry, so only pH needs the parking vial.
2. **If dry storage is a hard requirement:** Sentron **MicroFET** (3 mm ISFET, pH+T, ~€1k, BLE integration effort) or a **Winsense/Microsens ISFET module** with a custom LMP91200 readout (~€15–180/sensor, real electronics project). The [ChemistryOpen 2025 comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC12680566/) is the best independent data on these.
3. A single small probe doing **EC + pH + T** at reasonable cost doesn't exist off the shelf; the modular Atlas stack is the practical substitute.

## Edison Scientific literature query

An Edison (`LITERATURE` job) query was run asking for compact pH sensors for SDLs that fit a 20 mL vial, dry-storage options, combined pH/EC/T probes, and published probe-storage automation approaches. The full cited response is in [`edison-ph-meter-query.md`](edison-ph-meter-query.md). Headline findings:

- **ISFET is the recommended dry-storable class**, and the literature confirms the Sentron-style probe geometry (~8 mm OD, vs ~12 mm for glass) fits a 20 mL vial well ([Oelssner 2005](https://doi.org/10.1016/j.snb.2004.05.009); [Demuth 2016](https://doi.org/10.1007/s00253-016-7412-0)). ISFET encapsulation resistance drops over months of wet immersion but **recovers during dry storage** — i.e., dry storage is actively good for these sensors, not just tolerated ([Oelssner 2005](https://doi.org/10.1016/j.snb.2004.05.009)).
- **The real ISFET tradeoff is drift → more frequent calibration.** Compensated systems reach ~0.003 pH/h drift and ~0.02 pH accuracy at 23 °C, but drift grows with pH and temperature and varies device-to-device ([Chen 2008](https://doi.org/10.1109/jsen.2008.2006471); [Vilouras 2021](https://doi.org/10.5525/gla.thesis.82122)). Budget for an automated recalibration step in the Cub XL workflow regardless of which ISFET is chosen.
- **No off-the-shelf single-shaft pH + EC + T probe under 12 mm exists** — this confirms the modular Atlas stack (or the Sentron pH+T probe plus a separate EC cell) is the right substitute. The only integrated pH+redox+conductivity devices found are research builds (e.g. [Daoudi 2017](https://doi.org/10.3390/s17061372), antimony pH + GEIS conductivity, validated over 16 months but custom).
- **Contactless alternatives worth knowing:** optical pH sensor spots (PreSens-style, <0.01 pH/day drift, attached to the vessel wall — no probe to store) and passive RFID pH/EC/T tags for single-use vessels ([Demuth 2016](https://doi.org/10.1007/s00253-016-7412-0)). Both need vessel redesign but eliminate probe maintenance entirely.
- **Published SDL probe-maintenance strategies** map directly onto the issue-#148 plan: permanent probe insertion through a screw-cap ([Frachon 2006](https://doi.org/10.1128/aem.00239-06)); robotic dip-and-measure on a carousel with a parked probe (pHBot/[Jose 2024](https://doi.org/10.26434/chemrxiv-2024-990q0)); automated rinse/sparge cleaning ([Electrolab, Oh 2023](https://doi.org/10.1016/j.device.2023.100103)); avoiding electrodes via indicator-dye colorimetry ([BrickSDLab, Böser 2025](https://doi.org/10.26434/chemrxiv-2025-lb8jt)); and platform-level automated capping of storage vials (Chemspeed). Edison notes that a **purpose-built automated wetting/storage station for pH electrodes is a genuine gap in the published literature** — so the capper/decapper storage-vial idea in #148 is novel enough to be worth documenting.

## Link validation

All links above were checked on 2026-07-02:

| Link | Status |
|---|---|
| Atlas datasheets (`files.atlas-scientific.com`: [mini pH](https://files.atlas-scientific.com/l-mini_pH_probe.pdf), [lab pH](https://files.atlas-scientific.com/pH_probe.pdf), [mini EC](https://files.atlas-scientific.com/Mini_EC_K_1.0_probe.pdf)) | ✅ HTTP 200, PDFs parsed; specs above come from these |
| `atlas-scientific.com` product pages | ⚠️ Return HTTP 403 to non-browser clients (bot protection); products confirmed via the 200-OK datasheets and the [Sensors & Probes retailer listing](https://sensorsandprobes.com/products/mini-ph-probe) (✅ live, €89.95, 6 in stock) |
| [Millar/Sentron probe family](https://millar.com/our-expertise/off-the-shelf-products/probes), [lab-testing page](https://millar.com/industrial-applications/laboratory-testing) | ✅ live (note: `sentron.nl` deep links now 301-redirect to millar.com and some old paths 404 — link millar.com, not sentron.nl) |
| [Sysmatec MicroFET listing](https://sysmatec.ch/en/product/isfet-micro-ph-probe-sentron-microfet/) | ✅ live, confirms 3 mm tip, 7–8 mm min. liquid depth |
| [ESTEDE Sentron wireless pricing](https://en.estede-scientific.com/Sentron-ISFET-wireless-pH-Meters) | ✅ live, €920 (+€115 MicroFET) |
| [Ziebart 2025, ChemistryOpen (PMC12680566)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12680566/) | ✅ live, full text |
| [Hanna HI98129](https://hannainst.com/hi98129-ph-ec-tds-tester.html) | ✅ live, $224.99 |
| [E+H Memosens CPS47E](https://www.endress.com/en/field-instruments-overview/liquid-analysis-product-overview/digital-pH-sensor-Memosens-CPS47E) | ✅ live, 12 mm ISFET confirmed |
| [Vernier GDX-FPH](https://www.vernier.com/product/go-direct-tris-compatible-flat-ph/) | ✅ live, $179, glass + wet storage confirmed |
| [Sigma-Aldrich 20 mL vial V7005](https://www.sigmaaldrich.com/US/en/product/sigma/v7005) | ✅ live, 28 × 61 mm confirmed |
| Winsense ([site](http://www.winsense.co.th/products.html)) | ⚠️ site has a self-signed TLS certificate; product and ~€15 pricing corroborated by the ChemistryOpen paper and [NECTEC datasheet](https://tmec.nectec.or.th/public/uploaded/products/isfet/ISFET2016/ISFET%20pH%20Sensor.pdf) |
| Campbell Scientific CS526 ISFET | ❌ excluded — [product retired](https://www.campbellsci.com/cs526) |

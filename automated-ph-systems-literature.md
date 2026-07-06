# Automated systems using pH meters — storage, integration, and cleaning

Survey of published/commercial automated systems that measure pH, focused on the
three questions relevant to the Cub XL:

1. **How is the probe stored** (wet vs. dry, parking vials, storage solution)?
2. **How is it integrated** onto an automated platform (gripper vs. fixed, flow cell, wash station)?
3. **How is it cleaned between experiments**?

Emphasis is on systems with **constraints like ours**: small volumes, vials, robotic
handling, walk-away autonomy. All links below were checked (see validation notes at the end).

---

## Most relevant: research self-driving / automated systems

### 1. pHbot — self-driving pH-adjustment robot (Chitre et al., 2024)
*Chitre, A. et al. "pHbot: Self-Driven Robot for pH Adjustment of Viscous Formulations
via Physics-informed-ML." Chemistry–Methods (Wiley), 2024.*
- Paper (Wiley): https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/cmtd.202300043
- Open-access preprint (ChemRxiv): https://chemrxiv.org/engage/chemrxiv/article-details/64d7af964a3f7d0c0d0eebd6
- Open-access PDF (NTU): https://dr.ntu.edu.sg/handle/10356/175755
- Code + assembly guide (GitHub): https://github.com/sustainable-processes/pHbot

**Why it matters for us — this is the closest match.** Lab-scale small-batch titration
(**~10 mL, 12 samples**), reaching target pH in 2–5 iterations across 250 formulations,
**~15 min/sample including cleaning**.
- **Integration:** the probe sits over a dedicated **washing station** served by **two pumps
  (inlet / outlet)** — i.e., a fixed probe with pumped rinse fluid rather than a moving probe.
- **Cleaning:** an explicit automated cleaning protocol was developed specifically to handle
  **high-viscosity, non-Newtonian analytes (up to ~5000 cP)**, which are the hardest case for
  probe fouling. Detailed wash/positioning specs are in the repo's `pHBotAssemblyGuide.pdf`.
- **Takeaway:** demonstrates that a pumped wash station beats a simple dip-rinse when samples
  are sticky, and that ~15 min/sample is a realistic cycle time budget when cleaning is included.

### 2. Fully automated 96-well pH measurement with a semiconductor pH-FET sensor
*"A fully automated pH measurement system for 96-well microplates using a semiconductor-based
pH sensor." Sensors and Actuators B: Chemical, 2009.*
- https://www.sciencedirect.com/science/article/abs/pii/S0925400509007485

**Why it matters — smallest-volume example, and dry-storable sensor type.**
- Uses a **flow-through differential pH-FET (ISFET-class) probe** — solid-state, so it does
  **not require wet storage** the way a glass bulb does (directly relevant to the "don't want to
  store in water" goal in this issue).
- **Sample volume: 26 µL.** Per-well cycle: **60 s wash / 20 s movement / 3 s suction / 52 s
  measurement.** The dominant time cost is the wash step — a useful calibration point for us.
- **Cleaning = flow-through rinse**; contamination is removed by pumped wash fluid, not wiping.

### 3. Self-driving lab for OER electrocatalysts (Rooney et al., 2023) — electrode-handling lessons
*"A Critical Evaluation of a Self-Driving Laboratory for the Optimization of Electrodeposited
Earth-Abundant Mixed-Metal Oxide Catalysts for the OER."* arXiv:2305.12541
- https://arxiv.org/abs/2305.12541

Doesn't measure pH, but its **electrode-in-automation** findings transfer directly:
- Handles **4 mL vials** with robotic grippers, syringe pumps, and pipette tips.
- Uses **separate cells for deposition vs. measurement to prevent cross-contamination** — the
  automation analogue of "clean between experiments."
- Explicitly notes that **a human can gently wipe an electrode mid-experiment but current
  automated systems cannot**, forcing electrochemical-cell redesign. This is the core design
  constraint behind our capper/decapper parking-vial idea.

### 4. SDL review — the electrode-maintenance gap
*Tom, G. et al. "Autonomous Chemical Experiments: Challenges and Perspectives on Establishing a
Self-Driving Lab." Accounts of Chemical Research, 2022.* (open access)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9454899/

Frames electrode conditioning/cleaning as a recognized **unsolved challenge** in SDLs —
supports the earlier finding that a purpose-built automated wetting/storage station is a real
gap worth contributing to.

---

## Commercial automated pH systems (documented cleaning + storage workflows)

### 5. Hudson Robotics Rapid_pH
- https://hudsonlabautomation.com/products/ph-meters/
- Application note: https://hudsonlabautomation.com/automated-ph-testing-prioritizing-accuracy-and-efficiency-in-the-lab/

Robotic pH meter for **microplates, tubes, and vials**. Workflow: **read → rinse with DI water →
air-dry the probe → repeat.** For **viscous samples**, the wash station uses a **power-wash spray
of DI water** to remove carryover (same lesson as pHbot). Range 0–14, ±0.05 pH.

### 6. Mettler Toledo InMotion autosamplers (+ InLab electrodes)
- https://www.mt.com/us/en/home/products/Laboratory_Analytics_Browse/Product_Family_Browse_titrators_main/automated-titration-systems/InMotion-autosamplers.html

Handles up to **~300 samples** with automated measurement, calibration, **conditioning, and
cleaning**. Uses a **PowerShower™** rinse plus conditioning sequences and includes explicit
**sensor maintenance and storage** steps between runs — the most complete commercial example of
automated *storage* (not just rinsing). Small-format **Micro / InLab Micro** electrodes exist for
low volumes.

### 7. Zinsser Analytic automated pH measurement toolbox
- https://www.zinsser-analytic.com/en/products/automation-toolbox/automated-ph-measurement/

Modular robotic pH add-on: gripper moves the probe, with a machine that cleans and dries the probe
between measurements.

---

## Cleaning-mechanism references (patents)

Useful if we design our own wash/parking station:
- **Self-cleaning probe with flow cell + agitated cleaning beads** — US 6,992,488:
  https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6992488
- **Portable pH meter with self-cleaning electrode chamber** — US 4,285,792:
  https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4285792
- **Automated cleaning + calibration maintenance device for a probe** — US (retractable
  maintenance station): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4852385

---

## Patterns that answer the three questions

**Storage.**
- Glass-bulb probes: automated systems **park them in a storage-solution vial** between runs
  (Mettler InMotion sensor-storage step) — the automated version of our capped-parking-vial idea.
- Solid-state **pH-FET/ISFET** probes (paper #2) sidestep wet storage entirely, at the cost of drift
  (consistent with the ISFET tradeoff already noted in the earlier issue research).

**Integration.** Two dominant architectures:
1. **Fixed probe + pumped wash station**, sample brought to the probe (pHbot #1, 96-well #2,
   Hudson #5) — best for small volumes and viscous/sticky samples.
2. **Moving probe on a gripper/arm**, dipped into sample then into wash/storage (Zinsser #7,
   Mettler #6) — best when samples stay in place and there are many of them.

**Cleaning between experiments.**
- **Pumped/sprayed DI-water rinse** is universal; a **power-wash spray** is the documented upgrade
  for viscous carryover (pHbot #1, Hudson #5, Mettler PowerShower #6).
- **Flow-through cells** rinse without moving the probe (#2, patent US 6,992,488).
- **No system wipes the probe** — automation can't replicate the human wipe (OER SDL #3), so all
  rely on fluid flow, which is why wash time dominates the cycle.

**Constraint match.** The closest analogues to the Cub XL (small volume, vials, walk-away): pHbot
(~10 mL, 12 vials, viscous-capable) and the 26 µL pH-FET microplate system. Both use a fixed probe
with a pumped wash rather than a moving probe.

---

## Link validation

| Source | Status |
|---|---|
| pHbot — Wiley DOI | Live (publisher page 403s to bots; open-access copies below confirm content) |
| pHbot — ChemRxiv / NTU / GitHub | Live, open access |
| 96-well pH-FET — ScienceDirect | Live (abstract 403s to bots; metadata + specs confirmed via search index) |
| OER SDL — arXiv:2305.12541 | Live, PDF fetched |
| SDL review — PMC9454899 | Live, open access |
| Hudson Rapid_pH product + app note | Live, content parsed |
| Mettler InMotion | Live, content parsed |
| Zinsser Analytic | Live |
| USPTO patent PDFs (6992488, 4285792, 4852385) | Live |
